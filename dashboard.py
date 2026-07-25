
# dashboard.py
# Attendance Management System - CBSE Class 12 Project
# Main Dashboard Window — Updated with Charts & Theme Toggle

import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import get_connection
import config

# Try importing matplotlib — it's optional (charts won't show if not installed)
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def open_dashboard(user_id, name, role):
    root = tk.Tk()
    app = Dashboard(root, user_id, name, role)
    root.mainloop()


class Dashboard:
    def __init__(self, root, user_id, name, role):
        self.root = root
        self.user_id = user_id
        self.name = name
        self.role = role
        self._chart_canvas = None  # holds matplotlib widget reference

        self.root.title("Attendance Management System - Dashboard")
        self.root.geometry("1050x650")
        self.root.resizable(True, True)
        self.root.eval('tk::PlaceWindow . center')

        self._apply_bg()
        self.build_ui()
        self.load_stats()

    # -------------------------------------------------------
    # Theme Helpers
    # -------------------------------------------------------
    def _apply_bg(self):
        t = config.get_theme()
        self.root.configure(bg=t["bg"])

    def _theme(self):
        return config.get_theme()

    def _recolor_widget(self, widget):
        """Recursively recolor all widgets to match the current theme."""
        t = self._theme()
        widget_class = widget.winfo_class()
        try:
            if widget_class in ("Frame", "Labelframe"):
                bg = t["bg"]
                # Identify sidebar vs content by stored tag if present
                tag = getattr(widget, "_theme_role", None)
                if tag == "sidebar":
                    bg = t["sidebar_bg"]
                elif tag == "top_bar":
                    bg = t["top_bar"]
                elif tag == "filter":
                    bg = t["sidebar_bg"]
                widget.configure(bg=bg)
            elif widget_class == "Label":
                tag = getattr(widget, "_theme_role", None)
                bg = t["bg"]
                fg = t["fg"]
                if tag == "sidebar":
                    bg = t["sidebar_bg"]
                elif tag == "top_bar":
                    bg = t["top_bar"]
                elif tag == "accent":
                    fg = t["accent"]
                widget.configure(bg=bg, fg=fg)
            elif widget_class == "Button":
                tag = getattr(widget, "_theme_role", None)
                if tag == "sidebar_btn":
                    widget.configure(bg=t["sidebar_bg"], fg=t["fg"],
                                     activebackground=t["accent"])
                elif tag == "danger":
                    widget.configure(bg=t["danger"], fg=t["fg"])
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._recolor_widget(child)

    def toggle_theme(self):
        config.toggle_theme()
        t = self._theme()
        self.root.configure(bg=t["bg"])
        self._recolor_widget(self.root)
        # Refresh label on toggle button
        self.theme_btn.configure(
            text="[ Light Mode ]" if config.current_theme == "dark" else "[ Dark Mode  ]"
        )
        # Reload stats to redraw chart with new colors
        self.load_stats()

    # -------------------------------------------------------
    # UI Build
    # -------------------------------------------------------
    def build_ui(self):
        t = self._theme()

        # Top Bar
        top_bar = tk.Frame(self.root, bg=t["top_bar"], height=55)
        top_bar._theme_role = "top_bar"
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="  ATTENDANCE MANAGEMENT SYSTEM",
            font=("Arial", 14, "bold"),
            bg=t["top_bar"], fg="white"
        ).pack(side="left", padx=10, pady=10)

        tk.Label(
            top_bar,
            text=f"Logged in as: {self.name} ({self.role.title()})  ",
            font=("Arial", 10),
            bg=t["top_bar"], fg="white"
        ).pack(side="right", padx=10)

        # Theme Toggle button — lives in top bar
        self.theme_btn = tk.Button(
            top_bar,
            text="[ Light Mode ]",
            font=("Arial", 9, "bold"),
            bg=t["top_bar"], fg="#ffe082",
            relief="flat", cursor="hand2",
            activebackground=t["accent"], activeforeground="white",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right", padx=8)

        # Main Content
        main = tk.Frame(self.root, bg=t["bg"])
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=t["sidebar_bg"], width=210)
        sidebar._theme_role = "sidebar"
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="MENU",
            font=("Arial", 11, "bold"),
            bg=t["sidebar_bg"], fg=t["accent"]
        ).pack(pady=20)

        menu_items = [
            ("  Dashboard",        self.show_dashboard),
            ("  Students",         self.open_students),
            ("  Attendance",       self.open_attendance),
            ("  Reports",          self.open_reports),
            ("  Teachers",         self.open_teachers),
            ("  Enrollments",      self.open_enrollments),
            ("  Change Password",  self.change_password),
            ("  Logout",           self.logout),
        ]

        for text, cmd in menu_items:
            btn = tk.Button(
                sidebar, text=text,
                font=("Arial", 10),
                bg=t["sidebar_bg"], fg=t["fg"],
                relief="flat", anchor="w",
                padx=15, pady=10, cursor="hand2",
                activebackground=t["accent"], activeforeground="white",
                command=cmd
            )
            btn._theme_role = "sidebar_btn"
            btn.pack(fill="x", padx=5, pady=2)

        # Right Content
        self.content_frame = tk.Frame(main, bg=t["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self._chart_canvas = None

    def show_dashboard(self):
        self.clear_content()
        self.load_stats()

    # -------------------------------------------------------
    # Dashboard Stats + Chart
    # -------------------------------------------------------
    def load_stats(self):
        self.clear_content()
        t = self._theme()

        tk.Label(
            self.content_frame,
            text="Dashboard Overview",
            font=("Arial", 14, "bold"),
            bg=t["bg"], fg=t["fg"]
        ).pack(anchor="w", pady=(0, 15))

        total_students = 0
        present_today = 0
        absent_today = 0
        late_today = 0
        leave_today = 0

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            from datetime import date
            today = date.today().strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=%s AND status='Present'", (today,))
            present_today = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=%s AND status='Absent'", (today,))
            absent_today = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=%s AND status='Late'", (today,))
            late_today = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=%s AND status='Leave'", (today,))
            leave_today = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            # Stat cards
            stats = [
                ("Total Students", total_students, "#2d1b60"),
                ("Present Today",  present_today,  "#155724"),
                ("Absent Today",   absent_today,   "#7b1c1c"),
                ("Late Today",     late_today,     "#856404"),
                ("On Leave Today", leave_today,    "#1e3a5f"),
            ]

            cards_frame = tk.Frame(self.content_frame, bg=t["bg"])
            cards_frame.pack(fill="x")

            for title, value, color in stats:
                card = tk.Frame(cards_frame, bg=color, bd=0, relief="flat")
                card.pack(side="left", padx=6, pady=5, ipadx=18, ipady=12)
                tk.Label(
                    card, text=str(value),
                    font=("Arial", 24, "bold"),
                    bg=color, fg="white"
                ).pack()
                tk.Label(
                    card, text=title,
                    font=("Arial", 9),
                    bg=color, fg="#cccccc"
                ).pack()

        except mysql.connector.Error as err:
            tk.Label(
                self.content_frame,
                text=f"Database Error: {err}",
                font=("Arial", 10),
                bg=t["bg"], fg="red"
            ).pack()

        # -------------------------------------------------------
        # Attendance Pie Chart (matplotlib)
        # -------------------------------------------------------
        if MATPLOTLIB_AVAILABLE:
            self._draw_charts(present_today, absent_today, late_today, leave_today)
        else:
            tk.Label(
                self.content_frame,
                text="Install matplotlib for attendance chart: pip install matplotlib",
                font=("Arial", 9, "italic"),
                bg=t["bg"], fg=t["fg_dim"]
            ).pack(anchor="w", pady=5)

        # Quick Actions
        tk.Label(
            self.content_frame,
            text="\nQuick Actions",
            font=("Arial", 12, "bold"),
            bg=t["bg"], fg=t["fg"]
        ).pack(anchor="w", pady=(15, 8))

        actions = [
            ("Mark Today's Attendance", self.open_attendance),
            ("Add New Student",         self.open_students),
            ("Generate Report",         self.open_reports),
        ]

        for text, cmd in actions:
            tk.Button(
                self.content_frame,
                text=text, font=("Arial", 10),
                bg=t["accent"], fg="white",
                relief="flat", cursor="hand2",
                padx=15, pady=7,
                command=cmd
            ).pack(anchor="w", pady=4)

    def _draw_charts(self, present, absent, late, leave):
        """Draw matplotlib charts embedded in the dashboard."""
        t = self._theme()
        bg_color = t["bg"]
        is_dark = config.current_theme == "dark"
        fg_color = "white" if is_dark else "#1a1a2e"

        chart_frame = tk.Frame(self.content_frame, bg=bg_color)
        chart_frame.pack(anchor="w", pady=5, fill="x")

        # PIE CHART
        values = [present, absent, late, leave]
        labels = ["Present", "Absent", "Late", "Leave"]
        colors = ["#28a745", "#dc3545", "#ffc107", "#17a2b8"]
        filtered = [(v, l, c) for v, l, c in zip(values, labels, colors) if v > 0]

        if not filtered:
            no_data_frame = tk.Frame(chart_frame, bg="#1e1040", width=360, height=180)
            no_data_frame.pack_propagate(False)
            no_data_frame.pack(side="left", pady=5)
            tk.Label(no_data_frame, text="No attendance recorded today.", font=("Arial", 10, "italic"), bg="#1e1040", fg="#a8a8b3").place(relx=0.5, rely=0.45, anchor="center")
            return

        fig = Figure(figsize=(7, 2.8), dpi=85, facecolor=bg_color)
        
        # Subplot 1: Pie
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(bg_color)
        fv, fl, fc = zip(*filtered)
        wedges, texts, autotexts = ax1.pie(
            fv, labels=fl, colors=fc,
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.55, edgecolor=bg_color, linewidth=2),
            textprops=dict(color=fg_color, fontsize=8)
        )
        for autotext in autotexts: autotext.set_color(fg_color)
        ax1.set_title("Today's Attendance", color=fg_color, fontsize=10, pad=8)

        # Subplot 2: Bar (Dummy Weekly Trend)
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(bg_color)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        rates = [85, 90, 88, 92, present/(present+absent+late+leave)*100 if (present+absent+late+leave)>0 else 0]
        ax2.bar(days, rates, color="#8b5cf6")
        ax2.set_ylim(0, 100)
        ax2.set_title("Weekly Trend (%)", color=fg_color, fontsize=10)
        ax2.tick_params(colors=fg_color, labelsize=8)
        for spine in ax2.spines.values(): spine.set_edgecolor(fg_color)

        fig.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left")
        self._chart_canvas = canvas

    # -------------------------------------------------------
    # Open Modules
    # -------------------------------------------------------
    def open_students(self):
        self.clear_content()
        import students
        students.StudentModule(self.content_frame)

    def open_attendance(self):
        self.clear_content()
        import attendance
        attendance.AttendanceModule(self.content_frame)

    def open_reports(self):
        self.clear_content()
        import reports
        reports.ReportModule(self.content_frame)

    def open_teachers(self):
        self.clear_content()
        import teachers
        teachers.TeacherModule(self.content_frame)

    def open_enrollments(self):
        self.clear_content()
        import enroll_admin
        enroll_admin.EnrollmentAdminModule(self.content_frame)

    # -------------------------------------------------------
    # Change Password
    # -------------------------------------------------------
    def change_password(self):
        t = self._theme()
        win = tk.Toplevel(self.root)
        win.title("Change Password")
        win.geometry("350x280")
        win.configure(bg=t["bg"])
        win.grab_set()

        tk.Label(win, text="Change Password", font=("Arial", 12, "bold"),
                 bg=t["bg"], fg=t["accent"]).pack(pady=15)

        tk.Label(win, text="Current Password:", bg=t["bg"], fg=t["fg"],
                 font=("Arial", 10)).pack(anchor="w", padx=30)
        old_pass = tk.Entry(win, show="*", bg=t["entry_bg"], fg=t["fg"],
                            font=("Arial", 11), relief="flat", bd=5)
        old_pass.pack(padx=30, fill="x", pady=(2, 8))

        tk.Label(win, text="New Password:", bg=t["bg"], fg=t["fg"],
                 font=("Arial", 10)).pack(anchor="w", padx=30)
        new_pass = tk.Entry(win, show="*", bg=t["entry_bg"], fg=t["fg"],
                            font=("Arial", 11), relief="flat", bd=5)
        new_pass.pack(padx=30, fill="x", pady=(2, 8))

        tk.Label(win, text="Confirm New Password:", bg=t["bg"], fg=t["fg"],
                 font=("Arial", 10)).pack(anchor="w", padx=30)
        confirm_pass = tk.Entry(win, show="*", bg=t["entry_bg"], fg=t["fg"],
                                font=("Arial", 11), relief="flat", bd=5)
        confirm_pass.pack(padx=30, fill="x", pady=(2, 15))

        def save_password():
            old = old_pass.get().strip()
            new = new_pass.get().strip()
            confirm = confirm_pass.get().strip()

            if not old or not new or not confirm:
                messagebox.showwarning("Warning", "All fields are required!", parent=win)
                return
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!", parent=win)
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id FROM users WHERE user_id=%s AND password=%s",
                    (self.user_id, old)
                )
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE users SET password=%s WHERE user_id=%s",
                        (new, self.user_id)
                    )
                    conn.commit()
                    messagebox.showinfo("Success", "Password changed successfully!", parent=win)
                    win.destroy()
                else:
                    messagebox.showerror("Error", "Current password is incorrect!", parent=win)
                cursor.close()
                conn.close()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err), parent=win)

        tk.Button(win, text="Save Password", font=("Arial", 10, "bold"),
                  bg=t["accent"], fg="white", relief="flat", cursor="hand2",
                  command=save_password).pack(pady=5)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import login
            root = tk.Tk()
            login.LoginWindow(root)
            root.mainloop()
