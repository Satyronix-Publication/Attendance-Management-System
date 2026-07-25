# student_portal.py
# Attendance Management System - CBSE Class 12 Project
# Student Portal Window

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database import get_connection

class StudentPortal:
    def __init__(self, root, student_id, name, roll_number):
        self.root = root
        self.student_id = student_id
        self.name = name
        self.roll_number = roll_number
        
        self.root.title(f"Student Portal - {self.name} ({self.roll_number})")
        self.root.geometry("800x600")
        self.root.configure(bg="#0f0a1e")
        self.root.resizable(False, False)
        
        self.build_ui()
        self.load_attendance()

    def build_ui(self):
        # Top Bar
        top_bar = tk.Frame(self.root, bg="#1e1040", height=50)
        top_bar.pack(fill="x")
        
        tk.Label(
            top_bar, text="👨‍🎓 STUDENT PORTAL", font=("Arial", 14, "bold"),
            bg="#1e1040", fg="#8b5cf6"
        ).pack(side="left", padx=15, pady=10)
        
        tk.Button(
            top_bar, text="Logout", font=("Arial", 9),
            bg="#7b1c1c", fg="white", relief="flat", cursor="hand2",
            command=self.logout
        ).pack(side="right", padx=15)

        # Tab Control
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#0f0a1e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e1040", foreground="white", font=("Arial", 10), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#8b5cf6")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Tabs
        self.tab_attendance = tk.Frame(self.notebook, bg="#0f0a1e")
        self.tab_profile = tk.Frame(self.notebook, bg="#0f0a1e")
        self.tab_id = tk.Frame(self.notebook, bg="#0f0a1e")
        
        self.notebook.add(self.tab_attendance, text="My Attendance")
        self.notebook.add(self.tab_profile, text="My Profile")
        self.notebook.add(self.tab_id, text="Virtual ID Card")

        self.build_attendance_tab()
        self.build_profile_tab()
        self.build_id_tab()

    def build_attendance_tab(self):
        # Summary Frame
        self.summary_frame = tk.Frame(self.tab_attendance, bg="#0f0a1e")
        self.summary_frame.pack(fill="x", pady=10)
        
        # Table
        cols = ("Date", "Subject", "Status", "Remarks")
        self.tree = ttk.Treeview(self.tab_attendance, columns=cols, show="headings", height=15)
        
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Subject", width=200)
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Remarks", width=250)

        style = ttk.Style()
        style.configure("Treeview", background="#1e1040", foreground="white", rowheight=25, fieldbackground="#1e1040")
        style.configure("Treeview.Heading", background="#2d1b60", foreground="white", font=("Arial", 9, "bold"))

        self.tree.pack(fill="both", expand=True)

    def load_attendance(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Fetch Attendance
            cursor.execute("""
                SELECT date, subject, status, remarks 
                FROM attendance 
                WHERE student_id = %s 
                ORDER BY date DESC
            """, (self.student_id,))
            rows = cursor.fetchall()
            
            present = absent = late = leave = 0
            for row in rows:
                self.tree.insert("", tk.END, values=row)
                status = row[2]
                if status == "Present": present += 1
                elif status == "Absent": absent += 1
                elif status == "Late": late += 1
                elif status == "Leave": leave += 1
            
            total = len(rows)
            pct = round((present / total * 100), 2) if total > 0 else 0
            
            for w in self.summary_frame.winfo_children():
                w.destroy()

            stats = [
                (f"Total: {total}", "#2d1b60"),
                (f"Present: {present}", "#155724"),
                (f"Absent: {absent}", "#7b1c1c"),
                (f"Attendance: {pct}%", "#856404" if pct < 75 else "#155724")
            ]
            
            for text, color in stats:
                tk.Label(self.summary_frame, text=text, font=("Arial", 10, "bold"),
                         bg=color, fg="white", padx=15, pady=5).pack(side="left", padx=5)
            
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def build_profile_tab(self):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (self.student_id,))
            self.student_data = cursor.fetchone()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))
            self.student_data = {}

        if not self.student_data: return

        frame = tk.Frame(self.tab_profile, bg="#1e1040", bd=2, relief="groove")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        info = [
            ("Roll Number:", self.student_data.get('roll_number')),
            ("Full Name:", self.student_data.get('full_name')),
            ("Class/Section:", f"{self.student_data.get('class')} - {self.student_data.get('section')}"),
            ("Gender:", self.student_data.get('gender')),
            ("Date of Birth:", self.student_data.get('dob')),
            ("Phone:", self.student_data.get('phone')),
            ("Email:", self.student_data.get('email')),
            ("Parent Name:", self.student_data.get('parent_name')),
            ("Parent Contact:", self.student_data.get('parent_contact')),
        ]
        
        for i, (label, val) in enumerate(info):
            tk.Label(frame, text=label, bg="#1e1040", fg="#a8a8b3", font=("Arial", 10, "bold")).grid(row=i, column=0, padx=20, pady=10, sticky="e")
            tk.Label(frame, text=val, bg="#1e1040", fg="white", font=("Arial", 10)).grid(row=i, column=1, padx=10, pady=10, sticky="w")
            
        # Change Password Button
        tk.Button(frame, text="Change Password", bg="#8b5cf6", fg="white", relief="flat", cursor="hand2", command=self.change_password).grid(row=len(info), column=0, columnspan=2, pady=20)

    def change_password(self):
        win = tk.Toplevel(self.root)
        win.title("Change Password")
        win.geometry("300x200")
        win.configure(bg="#0f0a1e")
        win.resizable(False, False)
        
        tk.Label(win, text="New Password:", bg="#0f0a1e", fg="white", font=("Arial", 10)).pack(pady=10)
        pwd_entry = tk.Entry(win, show="*", font=("Arial", 10), bg="#2d1b60", fg="white", insertbackground="white")
        pwd_entry.pack(pady=5)
        
        def save():
            new_pwd = pwd_entry.get().strip()
            if not new_pwd: return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET student_password=%s WHERE student_id=%s", (new_pwd, self.student_id))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", "Password updated successfully!")
                win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))
                
        tk.Button(win, text="Save", bg="#28a745", fg="white", font=("Arial", 10, "bold"), relief="flat", command=save).pack(pady=15)

    def build_id_tab(self):
        tk.Label(self.tab_id, text="Your Virtual ID Card", bg="#0f0a1e", fg="white", font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(self.tab_id, text="Save this ID card to your phone for quick attendance marking.", bg="#0f0a1e", fg="#a8a8b3", font=("Arial", 10)).pack(pady=5)
        
        tk.Button(self.tab_id, text="Generate & Save ID Card", bg="#8b5cf6", fg="white", font=("Arial", 11, "bold"), padx=20, pady=10, cursor="hand2", relief="flat", command=self.download_id).pack(pady=30)
        
    def download_id(self):
        import id_card
        info = {
            "name": self.student_data.get('full_name'),
            "roll": self.student_data.get('roll_number'),
            "class": self.student_data.get('class'),
            "section": self.student_data.get('section'),
            "dob": self.student_data.get('dob'),
            "phone": self.student_data.get('phone'),
            "parent_contact": self.student_data.get('parent_contact')
        }
        
        img = id_card.generate_virtual_id(info)
        import os
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"ID_Card_{info['roll']}.png",
            title="Save ID Card",
            filetypes=[("PNG files", "*.png")]
        )
        if filepath:
            try:
                img.save(filepath)
                messagebox.showinfo("Success", f"ID Card saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")

    def logout(self):
        self.root.destroy()
        
        # Start fresh login window
        import login
        root = tk.Tk()
        app = login.LoginWindow(root)
        root.mainloop()

def open_student_portal(student_id, name, roll_number):
    root = tk.Tk()
    app = StudentPortal(root, student_id, name, roll_number)
    root.mainloop()
