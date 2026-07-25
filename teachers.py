
# teachers.py
# Attendance Management System - CBSE Class 12 Project
# Teacher Management Module

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from database import get_connection


class TeacherModule:
    def __init__(self, parent):
        self.parent = parent
        self.selected_id = None
        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.parent, text="Teacher Management",
            font=("Arial", 14, "bold"),
            bg="#0f0a1e", fg="white"
        ).pack(anchor="w", pady=(0, 10))

        # -------------------------------------------------------
        # Buttons Row
        # -------------------------------------------------------
        top = tk.Frame(self.parent, bg="#0f0a1e")
        top.pack(fill="x", pady=5)

        buttons = [
            ("Add Teacher",    self.add_teacher_form, "#28a745"),
            ("Edit Teacher",   self.edit_teacher_form, "#2d1b60"),
            ("Delete Teacher", self.delete_teacher,    "#dc3545"),
            ("Refresh",        self.load_teachers,     "#6c757d"),
        ]
        for text, cmd, color in buttons:
            tk.Button(top, text=text, font=("Arial", 10),
                      bg=color, fg="white", relief="flat",
                      cursor="hand2", padx=10, pady=5,
                      command=cmd).pack(side="left", padx=5)

        # Also add teacher as a login user
        tk.Button(top, text="Add Teacher Login Account",
                  font=("Arial", 9),
                  bg="#856404", fg="white", relief="flat",
                  cursor="hand2", padx=10, pady=5,
                  command=self.add_teacher_login).pack(side="left", padx=5)

        # -------------------------------------------------------
        # Teacher Table
        # -------------------------------------------------------
        table_frame = tk.Frame(self.parent, bg="#0f0a1e")
        table_frame.pack(fill="both", expand=True, pady=10)

        cols = ("ID", "Name", "Subject", "Phone", "Email")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        col_widths = [60, 180, 150, 120, 200]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview", background="#1e1040", foreground="white",
                         rowheight=28, fieldbackground="#1e1040", font=("Arial", 10))
        style.configure("Treeview.Heading", background="#2d1b60", foreground="white",
                         font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#8b5cf6")])

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.load_teachers()

    def load_teachers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers ORDER BY name")
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = self.tree.item(selected[0])['values'][0]

    def add_teacher_form(self):
        self._open_form("Add New Teacher", None)

    def edit_teacher_form(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a teacher to edit!")
            return
        self._open_form("Edit Teacher", self.selected_id)

    def _open_form(self, title, teacher_id):
        win = tk.Toplevel()
        win.title(title)
        win.geometry("400x320")
        win.configure(bg="#0f0a1e")
        win.grab_set()

        tk.Label(win, text=title, font=("Arial", 12, "bold"),
                 bg="#0f0a1e", fg="#8b5cf6").pack(pady=15)

        frame = tk.Frame(win, bg="#1e1040")
        frame.pack(padx=20, fill="both", expand=True)

        fields = [
            ("Name*",       "name"),
            ("Subject*",    "subject"),
            ("Phone",       "phone"),
            ("Email",       "email"),
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label, bg="#1e1040", fg="white",
                     font=("Arial", 10), anchor="w").grid(
                row=i, column=0, padx=15, pady=6, sticky="w")
            entry = tk.Entry(frame, font=("Arial", 11), bg="#2d1b60", fg="white",
                             insertbackground="white", relief="flat", bd=4, width=25)
            entry.grid(row=i, column=1, padx=10, pady=6)
            entries[key] = entry

        if teacher_id:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM teachers WHERE teacher_id=%s", (teacher_id,))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    for (label, key), val in zip(fields, row[1:]):
                        entries[key].insert(0, str(val) if val else "")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err), parent=win)

        def save():
            data = {k: e.get().strip() for k, e in entries.items()}
            if not data['name'] or not data['subject']:
                messagebox.showwarning("Warning", "Name and Subject are required!", parent=win)
                return
            if data['phone'] and not data['phone'].isdigit():
                messagebox.showerror("Error", "Phone must contain digits only!", parent=win)
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                if teacher_id:
                    cursor.execute("""
                        UPDATE teachers SET name=%s, subject=%s, phone=%s, email=%s
                        WHERE teacher_id=%s
                    """, (data['name'], data['subject'], data['phone'],
                          data['email'], teacher_id))
                    msg = "Teacher updated successfully!"
                else:
                    cursor.execute("""
                        INSERT INTO teachers (name, subject, phone, email)
                        VALUES (%s, %s, %s, %s)
                    """, (data['name'], data['subject'], data['phone'], data['email']))
                    msg = "Teacher added successfully!"
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self.load_teachers()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err), parent=win)

        tk.Button(frame, text="Save", font=("Arial", 11, "bold"),
                  bg="#8b5cf6", fg="white", relief="flat", cursor="hand2",
                  width=20, pady=6, command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=15)

    def delete_teacher(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a teacher to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this teacher?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teachers WHERE teacher_id=%s", (self.selected_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", "Teacher deleted successfully!")
                self.selected_id = None
                self.load_teachers()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))

    def add_teacher_login(self):
        """Create a login account for a teacher so they can log into the system."""
        win = tk.Toplevel()
        win.title("Create Teacher Login Account")
        win.geometry("380x300")
        win.configure(bg="#0f0a1e")
        win.grab_set()

        tk.Label(win, text="Create Teacher Login",
                 font=("Arial", 12, "bold"), bg="#0f0a1e", fg="#8b5cf6").pack(pady=15)

        frame = tk.Frame(win, bg="#1e1040")
        frame.pack(padx=20, fill="both", expand=True)

        labels_keys = [
            ("Full Name*",  "name"),
            ("Username*",   "username"),
            ("Password*",   "password"),
        ]
        entries = {}
        for i, (label, key) in enumerate(labels_keys):
            tk.Label(frame, text=label, bg="#1e1040", fg="white",
                     font=("Arial", 10), anchor="w").grid(
                row=i, column=0, padx=15, pady=8, sticky="w")
            show = "*" if key == "password" else ""
            entry = tk.Entry(frame, font=("Arial", 11), bg="#2d1b60", fg="white",
                             insertbackground="white", relief="flat", bd=4,
                             width=22, show=show)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry

        def create():
            data = {k: e.get().strip() for k, e in entries.items()}
            if not data['name'] or not data['username'] or not data['password']:
                messagebox.showwarning("Warning", "All fields required!", parent=win)
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role, name) VALUES (%s,%s,%s,%s)",
                    (data['username'], data['password'], 'teacher', data['name'])
                )
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success",
                    f"Login account created!\nUsername: {data['username']}\nPassword: {data['password']}",
                    parent=win)
                win.destroy()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists!", parent=win)
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err), parent=win)

        tk.Button(frame, text="Create Account", font=("Arial", 11, "bold"),
                  bg="#28a745", fg="white", relief="flat", cursor="hand2",
                  width=20, pady=6, command=create).grid(
            row=len(labels_keys), column=0, columnspan=2, pady=15)
