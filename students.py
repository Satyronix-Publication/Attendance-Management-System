
# students.py
# Attendance Management System - CBSE Class 12 Project
# Student Management Module — Updated with CSV Import & QR Code ID Card

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from database import get_connection
import csv
import io

# Optional: QR Code & Image support
try:
    import qrcode
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


class StudentModule:
    def __init__(self, parent):
        self.parent = parent
        self.selected_id = None
        self.build_ui()

    def build_ui(self):
        # -------------------------------------------------------
        # Title
        # -------------------------------------------------------
        tk.Label(
            self.parent, text="Student Management",
            font=("Arial", 14, "bold"),
            bg="#0f0a1e", fg="white"
        ).pack(anchor="w", pady=(0, 10))

        # -------------------------------------------------------
        # Top - Search & Buttons
        # -------------------------------------------------------
        top = tk.Frame(self.parent, bg="#0f0a1e")
        top.pack(fill="x", pady=5)

        tk.Label(top, text="Search:", bg="#0f0a1e", fg="white",
                 font=("Arial", 10)).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_students())
        tk.Entry(top, textvariable=self.search_var,
                 font=("Arial", 10), bg="#2d1b60", fg="white",
                 insertbackground="white", relief="flat", bd=5,
                 width=20).pack(side="left", padx=5)

        buttons = [
            ("➕ Add Student",      "#28a745", self.add_student_form),
            ("✏️ Edit Student",     "#2d1b60", self.edit_student_form),
            ("🗑️ Delete Student",  "#dc3545", self.delete_student),
            ("📂 Import CSV",       "#0d6efd", self.import_csv),
            ("🪪 ID Card / QR",    "#6f42c1", self.generate_id_card),
            ("🔄 Refresh",          "#6c757d", self.load_students),
        ]

        for (text, color, cmd) in buttons:
            tk.Button(top, text=text, font=("Arial", 9),
                      bg=color, fg="white", relief="flat",
                      cursor="hand2", padx=8, pady=4,
                      command=cmd).pack(side="left", padx=3)

        # -------------------------------------------------------
        # Student Table
        # -------------------------------------------------------
        table_frame = tk.Frame(self.parent, bg="#0f0a1e")
        table_frame.pack(fill="both", expand=True, pady=10)

        cols = ("ID", "Roll No", "Name", "Class", "Section", "Gender", "Phone", "Parent Name", "Email")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        col_widths = [45, 75, 145, 55, 65, 65, 95, 125, 140]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        style = ttk.Style()
        style.configure("Treeview", background="#1e1040", foreground="white",
                         rowheight=25, fieldbackground="#1e1040", font=("Arial", 9))
        style.configure("Treeview.Heading", background="#2d1b60", foreground="white",
                         font=("Arial", 9, "bold"))
        style.map("Treeview", background=[("selected", "#8b5cf6")])

        self.load_students()

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, roll_number, full_name, class, section,
                       gender, phone, parent_name, COALESCE(email,'')
                FROM students ORDER BY class, section, roll_number
            """)
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))

    def search_students(self):
        keyword = self.search_var.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            like = f"%{keyword}%"
            cursor.execute("""
                SELECT student_id, roll_number, full_name, class, section,
                       gender, phone, parent_name, COALESCE(email,'')
                FROM students
                WHERE full_name LIKE %s OR roll_number LIKE %s OR student_id LIKE %s
            """, (like, like, like))
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

    def add_student_form(self):
        self._open_form("Add New Student", None)

    def edit_student_form(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a student to edit!")
            return
        self._open_form("Edit Student", self.selected_id)

    def _open_form(self, title, student_id):
        win = tk.Toplevel()
        win.title(title)
        win.geometry("520x580")
        win.configure(bg="#0f0a1e")
        win.grab_set()

        tk.Label(win, text=title, font=("Arial", 13, "bold"),
                 bg="#0f0a1e", fg="#8b5cf6").pack(pady=10)

        frame = tk.Frame(win, bg="#1e1040")
        frame.pack(padx=20, fill="both", expand=True)

        fields = [
            ("Roll Number*",        "roll_number"),
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
                row=i, column=0, padx=15, pady=4, sticky="w")
            entry = tk.Entry(frame, font=("Arial", 10), bg="#2d1b60", fg="white",
                             insertbackground="white", relief="flat", bd=4, width=28)
            entry.grid(row=i, column=1, padx=10, pady=4)
            entries[key] = entry

        if student_id:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
                row = cursor.fetchone()
                cursor.close()
                conn.close()
                if row:
                    vals = list(row[1:])
                    keys = [f[1] for f in fields]
                    for k, v in zip(keys, vals):
                        entries[k].insert(0, str(v) if v else "")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err), parent=win)

        def save():
            data = {k: e.get().strip() for k, e in entries.items()}

            if not data['roll_number'] or not data['full_name'] or not data['class'] or not data['section'] or not data['gender']:
                messagebox.showwarning("Warning", "Please fill all required (*) fields!", parent=win)
                return
            if data['class'] not in ('11', '12'):
                messagebox.showerror("Error", "Class must be 11 or 12!", parent=win)
                return
            if data['gender'] not in ('Male', 'Female', 'Other'):
                messagebox.showerror("Error", "Gender must be Male, Female, or Other!", parent=win)
                return
            if data['phone'] and not data['phone'].isdigit():
                messagebox.showerror("Error", "Phone number must contain digits only!", parent=win)
                return

            dob = data['dob'] if data['dob'] else None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                if student_id:
                    cursor.execute("""
                        UPDATE students SET
                            roll_number=%s, full_name=%s, class=%s, section=%s,
                            gender=%s, dob=%s, phone=%s, parent_name=%s,
                            parent_contact=%s, email=%s, address=%s
                        WHERE student_id=%s
                    """, (data['roll_number'], data['full_name'], data['class'],
                          data['section'], data['gender'], dob, data['phone'],
                          data['parent_name'], data['parent_contact'],
                          data['email'], data['address'], student_id))
                    msg = "Student updated successfully!"
                else:
                    cursor.execute("SELECT student_id FROM students WHERE roll_number=%s",
                                   (data['roll_number'],))
                    if cursor.fetchone():
                        messagebox.showerror("Error", "Roll number already exists!", parent=win)
                        return
                    cursor.execute("""
                        INSERT INTO students
                            (roll_number, full_name, class, section, gender, dob,
                             phone, parent_name, parent_contact, email, address)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (data['roll_number'], data['full_name'], data['class'],
                          data['section'], data['gender'], dob, data['phone'],
                          data['parent_name'], data['parent_contact'],
                          data['email'], data['address']))
                    msg = "Student added successfully!"

                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
                self.load_students()

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", str(err), parent=win)

        tk.Button(frame, text="Save", font=("Arial", 11, "bold"),
                  bg="#8b5cf6", fg="white", relief="flat", cursor="hand2",
                  width=20, pady=6, command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=15)

    def delete_student(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a student to delete!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?\nThis will also delete all attendance records for this student."):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE student_id=%s", (self.selected_id,))
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.selected_id = None
                self.load_students()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", str(err))

    # -------------------------------------------------------
    # CSV Import Feature
    # -------------------------------------------------------
    def import_csv(self):
        """Import students from a CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        # Show a preview / info window
        win = tk.Toplevel()
        win.title("Import Students from CSV")
        win.geometry("650x420")
        win.configure(bg="#0f0a1e")
        win.grab_set()

        tk.Label(win, text="📂 Import Students from CSV",
                 font=("Arial", 13, "bold"), bg="#0f0a1e", fg="#8b5cf6").pack(pady=10)

        # Expected format info
        info_text = ("Expected CSV Columns (in order):\n"
                     "roll_number, full_name, class, section, gender, "
                     "dob, phone, parent_name, parent_contact, email, address\n\n"
                     "• class must be 11 or 12\n"
                     "• gender must be Male, Female, or Other\n"
                     "• dob format: YYYY-MM-DD (can be empty)\n"
                     "• First row can be a header row (will be auto-skipped)")

        tk.Label(win, text=info_text, font=("Arial", 9), bg="#1e1040",
                 fg="#a8a8b3", justify="left", padx=15, pady=10).pack(fill="x", padx=20)

        log_text = tk.Text(win, bg="#1e1040", fg="white", font=("Consolas", 9),
                           height=10, relief="flat")
        log_text.pack(fill="both", expand=True, padx=20, pady=10)

        def log(msg, color="white"):
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)

        def do_import():
            import_btn.configure(state="disabled")
            log(f"Opening: {file_path}\n")
            inserted = 0
            skipped = 0
            errors = 0

            try:
                with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
                    reader = csv.reader(csvfile)
                    conn = get_connection()
                    cursor = conn.cursor()

                    for i, row in enumerate(reader):
                        # Skip header row
                        if i == 0 and row and row[0].strip().lower() in ('roll_number', 'roll no', 'roll'):
                            log(f"  Skipping header row: {row}")
                            continue

                        # Pad missing columns
                        while len(row) < 11:
                            row.append("")

                        (roll, name, cls, section, gender, dob,
                         phone, parent_name, parent_contact, email, address) = [
                            str(c).strip() for c in row[:11]
                        ]

                        # Basic validation
                        if not roll or not name or cls not in ('11', '12') or gender not in ('Male', 'Female', 'Other'):
                            log(f"  ⚠️  Row {i+1} skipped (invalid data): {row[:5]}", "yellow")
                            skipped += 1
                            continue

                        # Check duplicate
                        cursor.execute("SELECT student_id FROM students WHERE roll_number=%s", (roll,))
                        if cursor.fetchone():
                            log(f"  ⚠️  Row {i+1} skipped (roll {roll} already exists)")
                            skipped += 1
                            continue

                        dob_val = dob if dob else None

                        try:
                            cursor.execute("""
                                INSERT INTO students
                                    (roll_number, full_name, class, section, gender, dob,
                                     phone, parent_name, parent_contact, email, address)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (roll, name, cls, section, gender, dob_val,
                                  phone, parent_name, parent_contact, email, address))
                            log(f"  ✅ Row {i+1}: {name} (Roll: {roll}) — Added")
                            inserted += 1
                        except mysql.connector.Error as row_err:
                            log(f"  ❌ Row {i+1} DB error: {row_err}")
                            errors += 1

                    conn.commit()
                    cursor.close()
                    conn.close()

                log(f"\n✅ Import Complete! Added: {inserted} | Skipped: {skipped} | Errors: {errors}")
                self.load_students()

            except FileNotFoundError:
                log("❌ File not found!")
            except Exception as e:
                log(f"❌ Error: {e}")

        import_btn = tk.Button(win, text="▶  Start Import", font=("Arial", 10, "bold"),
                               bg="#28a745", fg="white", relief="flat", cursor="hand2",
                               padx=15, pady=6, command=do_import)
        import_btn.pack(pady=5)

    # -------------------------------------------------------
    # QR Code / ID Card Generation
    # -------------------------------------------------------
    def generate_id_card(self):
        """Generate a QR Code + ID card image for the selected student."""
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select a student first!")
            return

        if not QR_AVAILABLE:
            messagebox.showwarning(
                "Missing Library",
                "The 'qrcode' and 'pillow' libraries are required.\n"
                "Please run: pip install qrcode pillow"
            )
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, roll_number, full_name, class, section,
                       gender, phone, parent_name, email
                FROM students WHERE student_id=%s
            """, (self.selected_id,))
            student = cursor.fetchone()
            cursor.close()
            conn.close()

            if not student:
                messagebox.showerror("Error", "Student not found!")
                return

            sid, roll, name, cls, section, gender, phone, parent, email = student
            
            info = {
                "name": name,
                "roll": roll,
                "class": cls,
                "section": section,
                "dob": "N/A", # We don't fetch dob here in the query right now, or we could add it
                "phone": phone,
                "parent_contact": parent
            }
            
            import id_card
            card = id_card.generate_virtual_id(info)

            # Show in Tkinter popup
            win = tk.Toplevel()
            win.title(f"ID Card — {name}")
            win.geometry("450x650")
            win.configure(bg="#0f0a1e")
            win.resizable(False, False)

            tk.Label(win, text=f"Student ID Card",
                     font=("Arial", 12, "bold"), bg="#0f0a1e", fg="#8b5cf6").pack(pady=8)

            tk_img = ImageTk.PhotoImage(card)
            img_label = tk.Label(win, image=tk_img, bg="#0f0a1e")
            img_label.image = tk_img  # Keep reference
            img_label.pack(pady=5)

            def save_card():
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    initialfile=f"ID_Card_{roll}_{name.replace(' ','_')}.png",
                    filetypes=[("PNG Image", "*.png")]
                )
                if save_path:
                    card.save(save_path)
                    messagebox.showinfo("Saved", f"ID Card saved to:\n{save_path}", parent=win)

            tk.Button(win, text="Save ID Card as PNG",
                      font=("Arial", 10), bg="#8b5cf6", fg="white",
                      relief="flat", cursor="hand2", padx=12, pady=5,
                      command=save_card).pack(pady=8)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate ID card:\n{e}")
