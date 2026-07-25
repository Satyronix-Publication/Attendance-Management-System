# enrollment.py
# Attendance Management System - CBSE Class 12 Project
# Student Enrollment Module

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import get_connection


def open_enrollment_window(parent=None):
    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("Student Enrollment Form")
    win.geometry("550x650")
    win.configure(bg="#0f0a1e")
    win.resizable(False, False)

    if parent:
        win.grab_set()
    else:
        win.eval('tk::PlaceWindow . center')

    tk.Label(win, text="📝 New Student Enrollment", font=("Arial", 14, "bold"),
             bg="#0f0a1e", fg="#8b5cf6").pack(pady=15)

    tk.Label(win, text="Submit your details. Admins will review your application.\nOnce approved, your Username & Password will be your Roll Number.",
             font=("Arial", 10), bg="#0f0a1e", fg="#a8a8b3", justify="center").pack(pady=(0, 15))

    frame = tk.Frame(win, bg="#1e1040", bd=2, relief="groove")
    frame.pack(padx=30, fill="both", expand=True, pady=10)

    # Form fields definition
    fields = [
        ("Full Name*",          "full_name"),
        ("Class* (11/12)",      "class"),
        ("Section*",            "section"),
        ("Gender* (Male/Female/Other)", "gender"),
        ("Date of Birth (YYYY-MM-DD)", "dob"),
        ("Phone Number",        "phone"),
        ("Parent/Guardian Name","parent_name"),
        ("Parent Contact",      "parent_contact"),
        ("Email",               "email"),
        ("Address",             "address"),
    ]

    entries = {}
    for i, (label, key) in enumerate(fields):
        tk.Label(frame, text=label, bg="#1e1040", fg="white",
                 font=("Arial", 9), anchor="w").grid(
            row=i, column=0, padx=15, pady=8, sticky="w")
        entry = tk.Entry(frame, font=("Arial", 10), bg="#2d1b60", fg="white",
                         insertbackground="white", relief="flat", bd=4, width=30)
        entry.grid(row=i, column=1, padx=10, pady=8)
        entries[key] = entry

    def submit():
        data = {k: e.get().strip() for k, e in entries.items()}

        if not data['full_name'] or not data['class'] or not data['section'] or not data['gender']:
            messagebox.showwarning("Warning", "Please fill all required (*) fields!", parent=win)
            return
        if data['class'] not in ('11', '12'):
            messagebox.showerror("Error", "Class must be 11 or 12!", parent=win)
            return
        if data['gender'] not in ('Male', 'Female', 'Other'):
            messagebox.showerror("Error", "Gender must be Male, Female, or Other!", parent=win)
            return

        dob = data['dob'] if data['dob'] else None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO enrollment_requests
                    (full_name, class, section, gender, dob,
                     phone, parent_name, parent_contact, email, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['full_name'], data['class'], data['section'], data['gender'], dob,
                  data['phone'], data['parent_name'], data['parent_contact'],
                  data['email'], data['address']))
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Application submitted successfully!\nPlease wait for admin approval.", parent=win)
            win.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err), parent=win)

    tk.Button(win, text="🚀 Submit Application", font=("Arial", 11, "bold"),
              bg="#8b5cf6", fg="white", relief="flat", cursor="hand2",
              width=25, pady=8, command=submit).pack(pady=15)

    if not parent:
        win.mainloop()

if __name__ == "__main__":
    open_enrollment_window()
