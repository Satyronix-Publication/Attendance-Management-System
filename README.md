# ATTENDANCE MANAGEMENT SYSTEM
### CBSE Class 12 Python Project

---

## Technologies Used
| Technology | Purpose |
|-----------|---------|
| Python 3.x | Programming Language |
| Tkinter | GUI Library (built-in) |
| MySQL | Database |
| mysql-connector-python | Database Connectivity |

---

## Files Description

| File | Purpose |
|------|---------|
| `main.py` | Entry point — Run this file |
| `database.py` | Database connection, table creation |
| `login.py` | Login window |
| `dashboard.py` | Main dashboard with sidebar |
| `students.py` | Student management (Add/Edit/Delete/Search) |
| `attendance.py` | Mark and save attendance |
| `reports.py` | Generate reports, export CSV, low attendance alerts |
| `teachers.py` | Teacher management |

---

## Database Configuration (in database.py)
```
Host     : localhost
User     : user
Password : root
Database : attendance_system
```

---

## How to Run

### Step 1 — Install MySQL Connector
```
pip install mysql-connector-python
```
or with Anaconda:
```
conda install -c conda-forge mysql-connector-python
```

### Step 2 — Make sure MySQL is running
- Start MySQL Server (XAMPP / MySQL Workbench / Command Line)
- The database and tables will be created automatically on first run

### Step 3 — Run the Application
```
python main.py
```

---

## Default Login Credentials
```
Username : admin
Password : admin123
Role     : Admin
```

---

## Features Implemented

1. **User Authentication** — Admin and Teacher login with password change
2. **Student Management** — Add, Edit, Delete, Search students (Class 11 & 12)
3. **Teacher Management** — Add, Edit, Delete teachers + create login accounts
4. **Attendance Marking** — Mark Present / Absent / Late / Leave per subject
5. **Attendance Reports** — Daily, Weekly, Monthly reports
6. **Low Attendance Alert** — Highlights students below 75%
7. **Attendance Percentage** — Auto-calculated per student
8. **Export to CSV** — Export reports to Desktop as CSV file
9. **Data Validation** — Duplicate roll number check, empty field check
10. **SQL Injection Prevention** — Parameterized queries used throughout

---

## Database Tables

| Table | Fields |
|-------|--------|
| users | user_id, username, password, role, name |
| students | student_id, roll_number, full_name, class, section, gender, dob, phone, parent_name, parent_contact, email, address |
| teachers | teacher_id, name, subject, phone, email |
| subjects | subject_id, subject_name |
| attendance | attendance_id, student_id, date, subject, status, remarks |

---

## Subjects Available (Class 11 & 12 CBSE)
- English, Mathematics, Physics, Chemistry, Biology
- Computer Science, Accountancy, Business Studies
- Economics, Physical Education

---

*Made as a CBSE Class 12 Computer Science Project*
