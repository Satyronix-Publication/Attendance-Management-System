
# reports.py
# Attendance Management System - CBSE Class 12 Project
# Attendance Reports Module

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import csv
import os
from datetime import date, timedelta
from database import get_connection


class ReportModule:
    def __init__(self, parent):
        self.parent = parent
        self.build_ui()

    def build_ui(self):
        tk.Label(
            self.parent, text="Attendance Reports",
            font=("Arial", 14, "bold"),
            bg="#0f0a1e", fg="white"
        ).pack(anchor="w", pady=(0, 10))

        # -------------------------------------------------------
        # Report Filter Frame
        # -------------------------------------------------------
        filter_frame = tk.Frame(self.parent, bg="#1e1040", pady=10, padx=10)
        filter_frame.pack(fill="x")

        # Report Type
        tk.Label(filter_frame, text="Report Type:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.report_type = tk.StringVar(value="Daily")
        ttk.Combobox(filter_frame, textvariable=self.report_type,
                     values=["Daily", "Weekly", "Monthly", "Student-wise", "Class-wise"],
                     width=14, state="readonly").grid(row=0, column=1, padx=5)

        # Date
        tk.Label(filter_frame, text="Date (YYYY-MM-DD):", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        tk.Entry(filter_frame, textvariable=self.date_var, font=("Arial", 10),
                 bg="#2d1b60", fg="white", insertbackground="white",
                 relief="flat", bd=4, width=13).grid(row=0, column=3, padx=5)

        # Class
        tk.Label(filter_frame, text="Class:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=4, padx=5)
        self.class_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.class_var,
                     values=["All", "11", "12"],
                     width=6, state="readonly").grid(row=0, column=5, padx=5)

        # Subject
        tk.Label(filter_frame, text="Subject:", bg="#1e1040", fg="white",
                 font=("Arial", 10)).grid(row=0, column=6, padx=5)
        self.subject_var = tk.StringVar(value="All")
        subjects = ["All", "English", "Mathematics", "Physics", "Chemistry",
                    "Biology", "Computer Science", "Accountancy",
                    "Business Studies", "Economics", "Physical Education"]
        ttk.Combobox(filter_frame, textvariable=self.subject_var,
                     values=subjects, width=16, state="readonly"
                     ).grid(row=0, column=7, padx=5)

        tk.Button(filter_frame, text="Generate Report",
                  font=("Arial", 9, "bold"),
                  bg="#8b5cf6", fg="white", relief="flat",
                  cursor="hand2", padx=8, pady=4,
                  command=self.generate_report).grid(row=0, column=8, padx=10)

        tk.Button(filter_frame, text="Export to CSV",
                  font=("Arial", 9, "bold"),
                  bg="#28a745", fg="white", relief="flat",
                  cursor="hand2", padx=8, pady=4,
                  command=self.export_csv).grid(row=0, column=9, padx=5)

        # -------------------------------------------------------
        # Summary Stats
        # -------------------------------------------------------
        self.summary_frame = tk.Frame(self.parent, bg="#0f0a1e")
        self.summary_frame.pack(fill="x", pady=5)

        # -------------------------------------------------------
        # Report Table
        # -------------------------------------------------------
        table_frame = tk.Frame(self.parent, bg="#0f0a1e")
        table_frame.pack(fill="both", expand=True, pady=5)

        cols = ("Roll No", "Name", "Class", "Section", "Date", "Subject", "Status", "Remarks")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        col_widths = [80, 140, 55, 65, 100, 130, 80, 120]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        style = ttk.Style()
        style.configure("Treeview", background="#1e1040", foreground="white",
                         rowheight=25, fieldbackground="#1e1040", font=("Arial", 9))
        style.configure("Treeview.Heading", background="#2d1b60", foreground="white",
                         font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", "#8b5cf6")])

        # Low attendance section
        tk.Label(
            self.parent, text="⚠  Low Attendance Alerts (Below 75%)",
            font=("Arial", 11, "bold"),
            bg="#0f0a1e", fg="#ffc107"
        ).pack(anchor="w", pady=(10, 2))

        alert_frame = tk.Frame(self.parent, bg="#0f0a1e")
        alert_frame.pack(fill="x")

        tk.Button(alert_frame, text="Show Low Attendance Students",
                  font=("Arial", 9),
                  bg="#856404", fg="white", relief="flat",
                  cursor="hand2", padx=10, pady=5,
                  command=self.show_low_attendance).pack(side="left", padx=5)

        tk.Button(alert_frame, text="Show Attendance % (All Students)",
                  font=("Arial", 9),
                  bg="#2d1b60", fg="white", relief="flat",
                  cursor="hand2", padx=10, pady=5,
                  command=self.show_attendance_percentage).pack(side="left", padx=5)

        tk.Button(alert_frame, text="📊 Advanced Analytics",
                  font=("Arial", 9, "bold"),
                  bg="#8b5cf6", fg="white", relief="flat",
                  cursor="hand2", padx=10, pady=5,
                  command=self.show_analytics).pack(side="left", padx=15)

    def generate_report(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        report_type = self.report_type.get()
        date_str = self.date_var.get().strip()
        class_ = self.class_var.get()
        subject = self.subject_var.get()

        query = """
            SELECT s.roll_number, s.full_name, s.class, s.section,
                   a.date, a.subject, a.status, a.remarks
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE 1=1
        """
        params = []

        if report_type == "Daily":
            query += " AND a.date = %s"
            params.append(date_str)
        elif report_type == "Weekly":
            try:
                d = date.fromisoformat(date_str)
                start = d - timedelta(days=d.weekday())
                end = start + timedelta(days=6)
                query += " AND a.date BETWEEN %s AND %s"
                params.extend([start.isoformat(), end.isoformat()])
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
        elif report_type == "Monthly":
            try:
                d = date.fromisoformat(date_str)
                query += " AND MONTH(a.date)=%s AND YEAR(a.date)=%s"
                params.extend([d.month, d.year])
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return

        if class_ != "All":
            query += " AND s.class = %s"
            params.append(class_)
        if subject != "All":
            query += " AND a.subject = %s"
            params.append(subject)

        query += " ORDER BY a.date DESC, s.class, s.section, s.roll_number"

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.current_data = rows

            present = absent = late = leave = 0
            for row in rows:
                self.tree.insert("", tk.END, values=row)
                status = row[6]
                if status == "Present": present += 1
                elif status == "Absent": absent += 1
                elif status == "Late": late += 1
                elif status == "Leave": leave += 1

            # Update summary
            for w in self.summary_frame.winfo_children():
                w.destroy()

            total = len(rows)
            summary_items = [
                (f"Total Records: {total}", "#2d1b60"),
                (f"Present: {present}", "#155724"),
                (f"Absent: {absent}", "#7b1c1c"),
                (f"Late: {late}", "#856404"),
                (f"Leave: {leave}", "#2d1b60"),
            ]
            for text, color in summary_items:
                tk.Label(self.summary_frame, text=text, font=("Arial", 9, "bold"),
                         bg=color, fg="white", padx=10, pady=3
                         ).pack(side="left", padx=4)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def export_csv(self):
        if not hasattr(self, 'current_data') or not self.current_data:
            messagebox.showwarning("Warning", "Please generate a report first!")
            return

        filename = f"attendance_report_{date.today()}.csv"
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Roll No", "Name", "Class", "Section",
                                 "Date", "Subject", "Status", "Remarks"])
                writer.writerows(self.current_data)
            messagebox.showinfo("Success", f"Report exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    def show_low_attendance(self):
        win = tk.Toplevel()
        win.title("Low Attendance Alert (Below 75%)")
        win.geometry("650x400")
        win.configure(bg="#0f0a1e")

        tk.Label(win, text="Students with Attendance Below 75%",
                 font=("Arial", 12, "bold"), bg="#0f0a1e", fg="#ffc107").pack(pady=10)

        cols = ("Roll No", "Name", "Class", "Section", "Present", "Total", "Percentage")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=14)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=85, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.roll_number, s.full_name, s.class, s.section,
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_days,
                       COUNT(a.attendance_id) AS total_days,
                       ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.attendance_id), 2) AS percentage
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.student_id, s.roll_number, s.full_name, s.class, s.section
                HAVING total_days > 0 AND percentage < 75
                ORDER BY percentage ASC
            """)
            for row in cursor.fetchall():
                pct = row[-1]
                tag = "danger" if pct < 60 else "warning"
                tree.insert("", tk.END, values=row, tags=(tag,))

            tree.tag_configure("danger", background="#7b1c1c")
            tree.tag_configure("warning", background="#856404")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err), parent=win)

    def show_attendance_percentage(self):
        win = tk.Toplevel()
        win.title("Student-wise Attendance Percentage")
        win.geometry("680x420")
        win.configure(bg="#0f0a1e")

        tk.Label(win, text="Attendance Percentage - All Students",
                 font=("Arial", 12, "bold"), bg="#0f0a1e", fg="white").pack(pady=10)

        cols = ("Roll No", "Name", "Class", "Section", "Present", "Total", "Percentage")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.roll_number, s.full_name, s.class, s.section,
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_days,
                       COUNT(a.attendance_id) AS total_days,
                       IFNULL(ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.attendance_id),0), 2), 0) AS percentage
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.student_id, s.roll_number, s.full_name, s.class, s.section
                ORDER BY s.class, s.section, s.roll_number
            """)
            for row in cursor.fetchall():
                pct = row[-1] or 0
                if pct < 60:
                    tag = "danger"
                elif pct < 75:
                    tag = "warning"
                else:
                    tag = "ok"
                tree.insert("", tk.END, values=row, tags=(tag,))

            tree.tag_configure("danger", background="#7b1c1c")
            tree.tag_configure("warning", background="#856404")
            tree.tag_configure("ok", background="#155724")

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err), parent=win)

        tk.Label(win, text="🔴 Below 60%  |  🟡 60-74%  |  🟢 75%+",
                 font=("Arial", 9), bg="#0f0a1e", fg="#a8a8b3").pack(pady=5)

    def show_analytics(self):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showerror("Dependency Error", "Please install matplotlib first:\npip install matplotlib")
            return

        win = tk.Toplevel(self.parent)
        win.title("Advanced Analytics Dashboard")
        win.geometry("900x600")
        win.configure(bg="#0f0a1e")
        
        tk.Label(win, text="📊 Analytics Overview", font=("Arial", 16, "bold"), bg="#0f0a1e", fg="white").pack(pady=15)
        
        chart_frame = tk.Frame(win, bg="#0f0a1e")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fig = Figure(figsize=(9, 4.5), dpi=90, facecolor="#0f0a1e")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Chart 1: Subject-wise Attendance
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor("#1e1040")
            cursor.execute("""
                SELECT subject, 
                       SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                FROM attendance
                GROUP BY subject
            """)
            data1 = cursor.fetchall()
            if data1:
                subjs, pcts = zip(*data1)
                ax1.barh(subjs, pcts, color="#8b5cf6")
                ax1.set_title("Subject-wise Attendance %", color="white")
                ax1.set_xlim(0, 100)
                ax1.tick_params(colors="white", labelsize=8)
                for spine in ax1.spines.values(): spine.set_edgecolor("white")
            
            # Chart 2: Class-wise comparison
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("#1e1040")
            cursor.execute("""
                SELECT s.class, 
                       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.attendance_id)
                FROM students s
                JOIN attendance a ON s.student_id = a.student_id
                GROUP BY s.class
            """)
            data2 = cursor.fetchall()
            if data2:
                classes, pcts = zip(*data2)
                ax2.bar(classes, pcts, color=["#28a745", "#17a2b8", "#ffc107"])
                ax2.set_title("Class-wise Attendance %", color="white")
                ax2.set_ylim(0, 100)
                ax2.tick_params(colors="white", labelsize=9)
                for spine in ax2.spines.values(): spine.set_edgecolor("white")
                
            cursor.close()
            conn.close()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err), parent=win)
            
        fig.tight_layout(pad=3.0)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
