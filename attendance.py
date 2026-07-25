
# attendance.py
# Attendance Management System - CBSE Class 12 Project
# Attendance Marking Module — Updated with Parent Email Notifications

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector
from database import get_connection
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


class AttendanceModule:
    def __init__(self, parent):
        self.parent = parent
        self.status_vars = {}     # student_id -> StringVar (status)
        self.remarks_vars = {}    # student_id -> StringVar (remarks)
        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.parent, text="Mark Attendance",
            font=("Arial", 14, "bold"),
            bg="#0f0a1e", fg="white"
        ).pack(anchor="w", pady=(0, 10))

        # -------------------------------------------------------
        # Filter Row
        # -------------------------------------------------------
        filter_frame = tk.Frame(self.parent, bg="#1e1040", pady=8, padx=10)
        filter_frame.pack(fill="x")

        # Date
        tk.Label(filter_frame, text="Date:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        tk.Entry(filter_frame, textvariable=self.date_var,
                 font=("Arial", 10), bg="#2d1b60", fg="white",
                 insertbackground="white", relief="flat", bd=4, width=12
                 ).grid(row=0, column=1, padx=5)

        # Class
        tk.Label(filter_frame, text="Class:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.class_var = tk.StringVar(value="11")
        ttk.Combobox(filter_frame, textvariable=self.class_var,
                     values=["11", "12"], width=5,
                     state="readonly").grid(row=0, column=3, padx=5)

        # Section
        tk.Label(filter_frame, text="Section:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=4, padx=5)
        self.section_var = tk.StringVar(value="A")
        ttk.Combobox(filter_frame, textvariable=self.section_var,
                     values=["A", "B", "C", "D", "E"],
                     width=5, state="readonly").grid(row=0, column=5, padx=5)

        # Subject
        tk.Label(filter_frame, text="Subject:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=6, padx=5)
        self.subject_var = tk.StringVar(value="English")
        subject_list = [
            "English", "Mathematics", "Physics", "Chemistry",
            "Biology", "Computer Science", "Accountancy",
            "Business Studies", "Economics", "Physical Education"
        ]
        ttk.Combobox(filter_frame, textvariable=self.subject_var,
                     values=subject_list, width=16,
                     state="readonly").grid(row=0, column=7, padx=5)

        tk.Button(filter_frame, text="Load Students",
                  font=("Arial", 9, "bold"),
                  bg="#8b5cf6", fg="white", relief="flat",
                  cursor="hand2", padx=8, pady=4,
                  command=self.load_students).grid(row=0, column=8, padx=10)

        # -------------------------------------------------------
        # Quick Mark All Buttons
        # -------------------------------------------------------
        quick_frame = tk.Frame(self.parent, bg="#0f0a1e")
        quick_frame.pack(fill="x", pady=5)

        tk.Label(quick_frame, text="Mark All As:", bg="#0f0a1e", fg="white",
                 font=("Arial", 9)).pack(side="left", padx=5)

        for status, color in [("Present", "#155724"), ("Absent", "#7b1c1c"),
                               ("Late", "#856404"), ("Leave", "#2d1b60")]:
            tk.Button(quick_frame, text=status, font=("Arial", 9),
                      bg=color, fg="white", relief="flat", cursor="hand2",
                      padx=8, pady=3,
                      command=lambda s=status: self.mark_all(s)
                      ).pack(side="left", padx=3)

        # Email notification toggle
        self.email_notify_var = tk.BooleanVar(value=config.EMAIL_ENABLED)
        email_chk = tk.Checkbutton(
            quick_frame,
            text="📧 Email parents on Absent/Late",
            variable=self.email_notify_var,
            bg="#0f0a1e", fg="#8b5cf6",
            selectcolor="#2d1b60",
            activebackground="#0f0a1e", activeforeground="#8b5cf6",
            font=("Arial", 9), cursor="hand2"
        )
        email_chk.pack(side="right", padx=15)

        # -------------------------------------------------------
        # Attendance Table (Scrollable Canvas)
        # -------------------------------------------------------
        table_label_frame = tk.Frame(self.parent, bg="#2d1b60")
        table_label_frame.pack(fill="x")

        headers = ["Roll No", "Student Name", "Status", "Remarks"]
        widths = [80, 200, 180, 200]
        for h, w in zip(headers, widths):
            tk.Label(table_label_frame, text=h, font=("Arial", 9, "bold"),
                     bg="#2d1b60", fg="white", width=w//7, anchor="w"
                     ).pack(side="left", padx=5, pady=4)

        container = tk.Frame(self.parent, bg="#0f0a1e")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#1e1040", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="#1e1040")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # -------------------------------------------------------
        # Save Button + Email Status Label
        # -------------------------------------------------------
        btn_frame = tk.Frame(self.parent, bg="#0f0a1e")
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="💾 Save Attendance",
                  font=("Arial", 11, "bold"),
                  bg="#28a745", fg="white", relief="flat",
                  cursor="hand2", padx=20, pady=7,
                  command=self.save_attendance).pack(side="left", padx=5)

        tk.Button(btn_frame, text="👁️ View Saved Attendance",
                  font=("Arial", 10),
                  bg="#2d1b60", fg="white", relief="flat",
                  cursor="hand2", padx=15, pady=7,
                  command=self.view_saved).pack(side="left", padx=5)

        tk.Button(btn_frame, text="⚙️ Email Settings",
                  font=("Arial", 10),
                  bg="#6f42c1", fg="white", relief="flat",
                  cursor="hand2", padx=12, pady=7,
                  command=self.open_email_settings).pack(side="left", padx=5)

        self.info_label = tk.Label(btn_frame, text="",
                                   font=("Arial", 9), bg="#0f0a1e", fg="#a8a8b3")
        self.info_label.pack(side="left", padx=10)

    # -------------------------------------------------------
    # Load Students
    # -------------------------------------------------------
    def load_students(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.status_vars.clear()
        self.remarks_vars.clear()

        class_ = self.class_var.get()
        section = self.section_var.get()
        date_str = self.date_var.get().strip()
        subject = self.subject_var.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, roll_number, full_name
                FROM students
                WHERE class=%s AND section=%s
                ORDER BY roll_number
            """, (class_, section))
            students = cursor.fetchall()

            cursor.execute("""
                SELECT student_id, status, remarks
                FROM attendance
                WHERE date=%s AND subject=%s AND student_id IN (
                    SELECT student_id FROM students WHERE class=%s AND section=%s
                )
            """, (date_str, subject, class_, section))
            existing = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            if not students:
                tk.Label(self.scroll_frame,
                         text="No students found for selected class and section.",
                         bg="#1e1040", fg="#a8a8b3",
                         font=("Arial", 10)).pack(pady=20)
                return

            self.info_label.config(
                text=f"Loaded {len(students)} students | Class {class_}-{section} | {subject} | {date_str}"
            )

            status_options = ["Present", "Absent", "Late", "Leave"]

            for i, (sid, roll, name) in enumerate(students):
                row_bg = "#1e1040" if i % 2 == 0 else "#1a1f3c"
                row = tk.Frame(self.scroll_frame, bg=row_bg)
                row.pack(fill="x", padx=2, pady=1)

                tk.Label(row, text=roll, width=10, anchor="w",
                         bg=row_bg, fg="white", font=("Arial", 9)
                         ).pack(side="left", padx=5)
                tk.Label(row, text=name, width=22, anchor="w",
                         bg=row_bg, fg="white", font=("Arial", 9)
                         ).pack(side="left", padx=5)

                status_var = tk.StringVar(
                    value=existing.get(sid, ("Present", ""))[0]
                )
                self.status_vars[sid] = status_var

                status_frame = tk.Frame(row, bg=row_bg)
                status_frame.pack(side="left", padx=5)

                colors_map = {
                    "Present": "#28a745", "Absent": "#dc3545",
                    "Late": "#ffc107", "Leave": "#17a2b8"
                }
                for opt in status_options:
                    tk.Radiobutton(
                        status_frame, text=opt, variable=status_var,
                        value=opt, bg=row_bg, fg=colors_map[opt],
                        selectcolor=row_bg, activebackground=row_bg,
                        font=("Arial", 9)
                    ).pack(side="left", padx=3)

                rem_var = tk.StringVar(
                    value=existing.get(sid, ("", ""))[1] or ""
                )
                self.remarks_vars[sid] = rem_var
                tk.Entry(row, textvariable=rem_var, width=20,
                         bg="#2d1b60", fg="white", insertbackground="white",
                         relief="flat", bd=3, font=("Arial", 9)
                         ).pack(side="left", padx=5)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def mark_all(self, status):
        for var in self.status_vars.values():
            var.set(status)

    # -------------------------------------------------------
    # Save Attendance + Email Notifications
    # -------------------------------------------------------
    def save_attendance(self):
        if not self.status_vars:
            messagebox.showwarning("Warning", "Please load students first!")
            return

        date_str = self.date_var.get().strip()
        subject = self.subject_var.get()

        if not date_str:
            messagebox.showwarning("Warning", "Please enter a valid date!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            saved = 0
            # Collect absent/late students who have parent emails
            notify_list = []   # list of (name, roll, status, parent_email)

            for sid, status_var in self.status_vars.items():
                status = status_var.get()
                remarks = self.remarks_vars[sid].get().strip()

                cursor.execute("""
                    INSERT INTO attendance (student_id, date, subject, status, remarks)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status=VALUES(status), remarks=VALUES(remarks)
                """, (sid, date_str, subject, status, remarks))
                saved += 1

                # Collect email targets for Absent / Late students
                if status in ("Absent", "Late") and self.email_notify_var.get():
                    cursor.execute(
                        "SELECT full_name, roll_number, email FROM students WHERE student_id=%s",
                        (sid,)
                    )
                    row = cursor.fetchone()
                    if row:
                        s_name, s_roll, s_email = row
                        if s_email:
                            notify_list.append((s_name, s_roll, status, s_email, subject, date_str))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"✅ Attendance saved for {saved} students!")

            # Send emails in background thread
            if notify_list:
                if config.EMAIL_ENABLED:
                    self.info_label.config(
                        text=f"📧 Sending {len(notify_list)} email notification(s)...",
                        fg="#ffc107"
                    )
                    t = threading.Thread(
                        target=self._send_notifications,
                        args=(notify_list,),
                        daemon=True
                    )
                    t.start()
                else:
                    self.info_label.config(
                        text=f"ℹ️ {len(notify_list)} absent/late — Email disabled. Configure in ⚙️ Settings.",
                        fg="#a8a8b3"
                    )

        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def _send_notifications(self, notify_list):
        """Background thread: send emails to parents."""
        sent = 0
        failed = 0

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(config.EMAIL_SENDER, config.EMAIL_APP_PASSWORD)

            for (name, roll, status, email, subject, att_date) in notify_list:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = f"Attendance Alert: {name} marked {status}"
                    msg["From"] = config.EMAIL_SENDER
                    msg["To"] = email

                    status_color = "#dc3545" if status == "Absent" else "#ffc107"
                    html_body = f"""
                    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px">
                    <div style="max-width:500px;margin:auto;background:white;border-radius:10px;
                                padding:30px;border-top:5px solid {status_color}">
                        <h2 style="color:{status_color};">⚠️ Attendance Alert</h2>
                        <p>Dear Parent/Guardian,</p>
                        <p>This is to inform you that your ward <strong>{name}</strong>
                        (Roll No: <strong>{roll}</strong>) was marked
                        <strong style="color:{status_color}">{status}</strong>
                        for the following class:</p>
                        <table style="border-collapse:collapse;width:100%;margin:15px 0">
                            <tr style="background:#f9f9f9">
                                <td style="padding:8px;border:1px solid #ddd"><b>Date</b></td>
                                <td style="padding:8px;border:1px solid #ddd">{att_date}</td>
                            </tr>
                            <tr>
                                <td style="padding:8px;border:1px solid #ddd"><b>Subject</b></td>
                                <td style="padding:8px;border:1px solid #ddd">{subject}</td>
                            </tr>
                            <tr style="background:#f9f9f9">
                                <td style="padding:8px;border:1px solid #ddd"><b>Status</b></td>
                                <td style="padding:8px;border:1px solid #ddd;color:{status_color}">
                                    <b>{status}</b>
                                </td>
                            </tr>
                        </table>
                        <p>Please ensure regular attendance to avoid any academic issues.</p>
                        <p style="color:#888;font-size:12px">
                            — Attendance Management System<br>
                            CBSE Class 11 &amp; 12
                        </p>
                    </div>
                    </body></html>
                    """

                    plain_body = (
                        f"Attendance Alert\n\n"
                        f"Dear Parent/Guardian,\n"
                        f"{name} (Roll: {roll}) was marked {status}\n"
                        f"Date: {att_date} | Subject: {subject}\n"
                    )

                    msg.attach(MIMEText(plain_body, "plain"))
                    msg.attach(MIMEText(html_body, "html"))

                    server.sendmail(config.EMAIL_SENDER, email, msg.as_string())
                    sent += 1

                except Exception:
                    failed += 1

            server.quit()

        except smtplib.SMTPAuthenticationError:
            # Schedule UI update back on main thread
            self.parent.after(0, lambda: self.info_label.config(
                text="❌ Email Error: Authentication failed. Check config.py credentials.",
                fg="#dc3545"
            ))
            return
        except Exception as e:
            self.parent.after(0, lambda: self.info_label.config(
                text=f"❌ Email Error: {e}",
                fg="#dc3545"
            ))
            return

        # Schedule UI update back on main thread
        self.parent.after(0, lambda: self.info_label.config(
            text=f"📧 Emails sent: {sent} | Failed: {failed}",
            fg="#28a745" if failed == 0 else "#ffc107"
        ))

    # -------------------------------------------------------
    # Email Settings Dialog
    # -------------------------------------------------------
    def open_email_settings(self):
        """Let the user configure email credentials at runtime."""
        win = tk.Toplevel()
        win.title("Email Notification Settings")
        win.geometry("430x320")
        win.configure(bg="#0f0a1e")
        win.grab_set()

        tk.Label(win, text="📧 Email Notification Settings",
                 font=("Arial", 13, "bold"), bg="#0f0a1e", fg="#8b5cf6").pack(pady=12)

        info = ("Uses your Gmail account to send alerts to parents.\n"
                "You need a Gmail App Password (not your regular password).\n"
                "Get it from: Google Account → Security → App Passwords")
        tk.Label(win, text=info, font=("Arial", 8), bg="#1e1040", fg="#a8a8b3",
                 justify="left", padx=10, pady=8, wraplength=390).pack(fill="x", padx=15)

        form = tk.Frame(win, bg="#0f0a1e")
        form.pack(padx=20, fill="x", pady=10)

        tk.Label(form, text="Gmail Address:", bg="#0f0a1e", fg="white",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=6)
        email_entry = tk.Entry(form, font=("Arial", 10), bg="#2d1b60", fg="white",
                               insertbackground="white", relief="flat", bd=4, width=28)
        email_entry.insert(0, config.EMAIL_SENDER)
        email_entry.grid(row=0, column=1, padx=10, pady=6)

        tk.Label(form, text="App Password:", bg="#0f0a1e", fg="white",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=6)
        pwd_entry = tk.Entry(form, show="*", font=("Arial", 10), bg="#2d1b60", fg="white",
                             insertbackground="white", relief="flat", bd=4, width=28)
        pwd_entry.insert(0, config.EMAIL_APP_PASSWORD)
        pwd_entry.grid(row=1, column=1, padx=10, pady=6)

        enabled_var = tk.BooleanVar(value=config.EMAIL_ENABLED)
        tk.Checkbutton(form, text="Enable Email Notifications", variable=enabled_var,
                       bg="#0f0a1e", fg="#8b5cf6", selectcolor="#2d1b60",
                       activebackground="#0f0a1e", font=("Arial", 10)
                       ).grid(row=2, column=0, columnspan=2, pady=6, sticky="w")

        def save_settings():
            config.EMAIL_SENDER = email_entry.get().strip()
            config.EMAIL_APP_PASSWORD = pwd_entry.get().strip()
            config.EMAIL_ENABLED = enabled_var.get()
            self.email_notify_var.set(config.EMAIL_ENABLED)
            messagebox.showinfo("Saved", "Email settings saved for this session!\n"
                                         "(To make permanent, edit config.py)", parent=win)
            win.destroy()

        def send_test():
            test_email = email_entry.get().strip()
            if not test_email:
                messagebox.showwarning("Warning", "Enter an email address first!", parent=win)
                return
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email_entry.get().strip(), pwd_entry.get().strip())
                msg = MIMEText("This is a test email from your Attendance Management System.")
                msg["Subject"] = "✅ Test Email — Attendance System"
                msg["From"] = email_entry.get().strip()
                msg["To"] = email_entry.get().strip()
                server.sendmail(email_entry.get().strip(), email_entry.get().strip(), msg.as_string())
                server.quit()
                messagebox.showinfo("Success", "✅ Test email sent successfully!", parent=win)
            except smtplib.SMTPAuthenticationError:
                messagebox.showerror("Error",
                    "Authentication failed!\nMake sure you're using an App Password, not your regular Gmail password.",
                    parent=win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}", parent=win)

        btn_frame = tk.Frame(win, bg="#0f0a1e")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="💾 Save Settings", font=("Arial", 10),
                  bg="#8b5cf6", fg="white", relief="flat", cursor="hand2",
                  padx=10, pady=5, command=save_settings).pack(side="left", padx=5)

        tk.Button(btn_frame, text="📤 Send Test Email", font=("Arial", 10),
                  bg="#28a745", fg="white", relief="flat", cursor="hand2",
                  padx=10, pady=5, command=send_test).pack(side="left", padx=5)

    # -------------------------------------------------------
    # View Saved Attendance
    # -------------------------------------------------------
    def view_saved(self):
        date_str = self.date_var.get().strip()
        class_ = self.class_var.get()
        section = self.section_var.get()
        subject = self.subject_var.get()

        win = tk.Toplevel()
        win.title(f"Attendance - {class_}-{section} | {subject} | {date_str}")
        win.geometry("620x420")
        win.configure(bg="#0f0a1e")

        tk.Label(win, text=f"Attendance Record: {class_}-{section} | {subject} | {date_str}",
                 font=("Arial", 11, "bold"), bg="#0f0a1e", fg="white").pack(pady=10)

        cols = ("Roll No", "Name", "Status", "Remarks")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=16)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Color rows by status
        tree.tag_configure("Present", foreground="#28a745")
        tree.tag_configure("Absent",  foreground="#dc3545")
        tree.tag_configure("Late",    foreground="#ffc107")
        tree.tag_configure("Leave",   foreground="#17a2b8")

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.roll_number, s.full_name, a.status, a.remarks
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date=%s AND a.subject=%s AND s.class=%s AND s.section=%s
                ORDER BY s.roll_number
            """, (date_str, subject, class_, section))
            for row in cursor.fetchall():
                status_tag = row[2] if row[2] in ("Present", "Absent", "Late", "Leave") else ""
                tree.insert("", tk.END, values=row, tags=(status_tag,))
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err), parent=win)
