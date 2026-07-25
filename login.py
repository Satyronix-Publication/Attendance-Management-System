
# login.py
# Attendance Management System - CBSE Class 12 Project
# Login Window

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import get_connection, create_database


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System - Login")
        self.root.geometry("450x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0a1e")

        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')

        self.build_ui()

    def build_ui(self):
        # -------------------------------------------------------
        # Title
        # -------------------------------------------------------
        tk.Label(
            self.root,
            text="ATTENDANCE MANAGEMENT SYSTEM",
            font=("Arial", 13, "bold"),
            bg="#0f0a1e", fg="#8b5cf6"
        ).pack(pady=(30, 5))

        tk.Label(
            self.root,
            text="Class 11 & 12 | CBSE",
            font=("Arial", 10),
            bg="#0f0a1e", fg="#a8a8b3"
        ).pack(pady=(0, 20))

        # -------------------------------------------------------
        # Login Frame
        # -------------------------------------------------------
        frame = tk.Frame(self.root, bg="#1e1040", bd=2, relief="groove")
        frame.pack(padx=40, pady=10, fill="both", expand=True)

        tk.Label(
            frame, text="LOGIN", font=("Arial", 12, "bold"),
            bg="#1e1040", fg="#8b5cf6"
        ).pack(pady=10)

        # Login Type Selection
        self.login_type = tk.StringVar(value="Staff")
        type_frame = tk.Frame(frame, bg="#1e1040")
        type_frame.pack(pady=5)
        
        tk.Radiobutton(type_frame, text="Staff (Admin/Teacher)", variable=self.login_type, value="Staff",
                       bg="#1e1040", fg="white", selectcolor="#2d1b60", activebackground="#1e1040", activeforeground="white").pack(side="left", padx=10)
        tk.Radiobutton(type_frame, text="Student", variable=self.login_type, value="Student",
                       bg="#1e1040", fg="white", selectcolor="#2d1b60", activebackground="#1e1040", activeforeground="white").pack(side="left", padx=10)

        # Username / Roll No
        tk.Label(
            frame, text="Username / Roll No:", font=("Arial", 10),
            bg="#1e1040", fg="white", anchor="w"
        ).pack(padx=30, fill="x")

        self.username_entry = tk.Entry(
            frame, font=("Arial", 11),
            bg="#2d1b60", fg="white", insertbackground="white",
            relief="flat", bd=5
        )
        self.username_entry.pack(padx=30, pady=(2, 10), fill="x")

        # Password
        tk.Label(
            frame, text="Password:", font=("Arial", 10),
            bg="#1e1040", fg="white", anchor="w"
        ).pack(padx=30, fill="x")

        self.password_entry = tk.Entry(
            frame, font=("Arial", 11), show="*",
            bg="#2d1b60", fg="white", insertbackground="white",
            relief="flat", bd=5
        )
        self.password_entry.pack(padx=30, pady=(2, 15), fill="x")

        # Login Button
        tk.Button(
            frame, text="LOGIN",
            font=("Arial", 11, "bold"),
            bg="#8b5cf6", fg="white",
            relief="flat", cursor="hand2",
            width=20, pady=6,
            command=self.login
        ).pack(pady=(5, 10))

        # New Enrollment Button
        tk.Button(
            frame, text="New Student Enrollment",
            font=("Arial", 9, "underline"),
            bg="#1e1040", fg="#a8a8b3",
            relief="flat", cursor="hand2",
            activebackground="#1e1040", activeforeground="white",
            command=self.open_enrollment
        ).pack(pady=(0, 10))

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.login())

        # Default credentials hint
        tk.Label(
            self.root,
            text="Staff: admin/admin123 | Student: roll_no/password",
            font=("Arial", 8),
            bg="#0f0a1e", fg="#555577"
        ).pack(pady=5)

    def open_enrollment(self):
        import enrollment
        enrollment.open_enrollment_window(self.root)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter username and password!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.login_type.get() == "Staff":
                cursor.execute(
                    "SELECT user_id, name, role FROM users WHERE username=%s AND password=%s",
                    (username, password)
                )
                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if user:
                    user_id, name, role = user
                    messagebox.showinfo("Success", f"Welcome, {name}!")
                    self.root.destroy()
                    import dashboard
                    dashboard.open_dashboard(user_id, name, role)
                else:
                    messagebox.showerror("Error", "Invalid username or password!")
                    self.password_entry.delete(0, tk.END)

            else:
                # Student Login
                cursor.execute(
                    "SELECT student_id, full_name, roll_number FROM students WHERE roll_number=%s AND student_password=%s",
                    (username, password)
                )
                student = cursor.fetchone()
                cursor.close()
                conn.close()

                if student:
                    student_id, name, roll_number = student
                    messagebox.showinfo("Success", f"Welcome, {name}!")
                    self.root.destroy()
                    try:
                        import student_portal
                        student_portal.open_student_portal(student_id, name, roll_number)
                    except Exception as e:
                        import traceback
                        # If the portal crashes, show a native message box with the error
                        import tkinter as tk
                        err_root = tk.Tk()
                        err_root.withdraw()
                        messagebox.showerror("Portal Crash", f"An error occurred while opening the portal:\n\n{str(e)}\n\n{traceback.format_exc()}")
                        err_root.destroy()
                else:
                    messagebox.showerror("Error", "Invalid roll number or password!")
                    self.password_entry.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Cannot connect to database.\n{err}")


# -------------------------------------------------------
# Main
# -------------------------------------------------------
if __name__ == "__main__":
    create_database()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
