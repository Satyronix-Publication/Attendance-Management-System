# enroll_admin.py
# Attendance Management System - CBSE Class 12 Project
# Admin Module for Managing Enrollments

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database import get_connection

class EnrollmentAdminModule:
    def __init__(self, parent):
        self.parent = parent
        self.build_ui()
        self.load_data()

    def build_ui(self):
        tk.Label(self.parent, text="Enrollment Requests", font=("Arial", 14, "bold"),
                 bg="#0f0a1e", fg="white").pack(anchor="w", pady=(0, 10))

        # Controls
        controls = tk.Frame(self.parent, bg="#1e1040", pady=10, padx=10)
        controls.pack(fill="x")

        tk.Button(controls, text="Refresh", font=("Arial", 9, "bold"),
                  bg="#2d1b60", fg="white", relief="flat", cursor="hand2", padx=10,
                  command=self.load_data).pack(side="left", padx=5)

        tk.Button(controls, text="Approve Selected", font=("Arial", 9, "bold"),
                  bg="#28a745", fg="white", relief="flat", cursor="hand2", padx=10,
                  command=self.approve).pack(side="left", padx=5)

        tk.Button(controls, text="Reject Selected", font=("Arial", 9, "bold"),
                  bg="#dc3545", fg="white", relief="flat", cursor="hand2", padx=10,
                  command=self.reject).pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(self.parent, bg="#0f0a1e")
        table_frame.pack(fill="both", expand=True, pady=10)

        cols = ("ID", "Name", "Class", "Section", "Gender", "Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.column("Name", width=150)
        self.tree.column("Date", width=150)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background="#1e1040", foreground="white", rowheight=25, fieldbackground="#1e1040")
        style.configure("Treeview.Heading", background="#2d1b60", foreground="white", font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", "#8b5cf6")])

        self.tree.pack(fill="both", expand=True)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT request_id, full_name, class, section, gender, request_date, status FROM enrollment_requests ORDER BY request_date DESC")
            
            for row in cursor.fetchall():
                tag = row[6].lower() # 'pending', 'approved', 'rejected'
                self.tree.insert("", tk.END, values=row, tags=(tag,))
                
            self.tree.tag_configure("pending", foreground="#ffc107")
            self.tree.tag_configure("approved", foreground="#28a745")
            self.tree.tag_configure("rejected", foreground="#dc3545")
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def approve(self):
        sel = self.tree.selection()
        if not sel: return
        
        req_id = self.tree.item(sel[0])['values'][0]
        status = self.tree.item(sel[0])['values'][6]
        
        if status != "Pending":
            messagebox.showinfo("Info", "Can only approve pending requests.")
            return
            
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM enrollment_requests WHERE request_id=%s", (req_id,))
            req = cursor.fetchone()
            
            if req:
                # Generate a roll number (e.g. Class + ID)
                cursor.execute("SELECT MAX(student_id) as m FROM students")
                res = cursor.fetchone()
                next_id = (res['m'] or 0) + 1
                roll_no = f"{req['class']}{next_id:03d}"
                
                # Generate a unique random password (8 chars)
                import string
                import random
                alphabet = string.ascii_letters + string.digits
                unique_password = ''.join(random.choice(alphabet) for i in range(8))
                
                # Insert into students
                cursor.execute("""
                    INSERT INTO students (roll_number, full_name, class, section, gender, dob, phone, parent_name, parent_contact, email, address, student_password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (roll_no, req['full_name'], req['class'], req['section'], req['gender'], req['dob'], req['phone'], req['parent_name'], req['parent_contact'], req['email'], req['address'], unique_password))
                
                # Update request status
                cursor.execute("UPDATE enrollment_requests SET status='Approved' WHERE request_id=%s", (req_id,))
                
                conn.commit()
                messagebox.showinfo("Approval Successful", 
                                    f"Application Approved!\n\n"
                                    f"🎓 Student: {req['full_name']}\n"
                                    f"👤 Username (Roll No): {roll_no}\n"
                                    f"🔑 Unique Password: {unique_password}\n\n"
                                    f"Please securely share these credentials with the student.")
                
            cursor.close()
            conn.close()
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def reject(self):
        sel = self.tree.selection()
        if not sel: return
        
        req_id = self.tree.item(sel[0])['values'][0]
        status = self.tree.item(sel[0])['values'][6]
        
        if status != "Pending":
            messagebox.showinfo("Info", "Can only reject pending requests.")
            return
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE enrollment_requests SET status='Rejected' WHERE request_id=%s", (req_id,))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))
