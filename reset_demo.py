"""
reset_demo.py
=============
Run this file ONCE to:
  1. Clear Python's __pycache__ (forces fresh reload of all modules)
  2. Insert 10 demo students directly into the database
  3. Insert today's sample attendance data

Usage:
    python reset_demo.py

Then restart the main app:
    python main.py
"""

import os
import shutil
import sys

# -----------------------------------------------------------
# Step 1: Clear __pycache__
# -----------------------------------------------------------
print("=" * 50)
print("STEP 1: Clearing Python cache (__pycache__)...")
pycache_path = os.path.join(os.path.dirname(__file__), "__pycache__")
if os.path.exists(pycache_path):
    shutil.rmtree(pycache_path)
    print("  [OK] __pycache__ deleted.")
else:
    print("  [OK] No cache found, skipping.")

# -----------------------------------------------------------
# Step 2: Connect to database and insert demo data
# -----------------------------------------------------------
print("\nSTEP 2: Inserting demo data into database...")

try:
    import mysql.connector

    # Read DB config from database.py
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'SatyAi',
        'database': 'attendance_system'
    }

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # -------------------------------------------------------
    # 10 Demo Students
    # -------------------------------------------------------
    demo_students = [
        ("1101", "Aarav Sharma",    "11", "A", "Male",   "2008-03-15", "9876543210", "Rajesh Sharma",    "9876543200", "parent.aarav@gmail.com",    "12 MG Road, Delhi"),
        ("1102", "Priya Singh",     "11", "A", "Female", "2008-07-22", "9876543211", "Suresh Singh",     "9876543201", "parent.priya@gmail.com",    "45 Connaught Place, Delhi"),
        ("1103", "Rohan Verma",     "11", "A", "Male",   "2008-01-10", "9876543212", "Anil Verma",       "9876543202", "parent.rohan@gmail.com",    "8 Lajpat Nagar, Delhi"),
        ("1104", "Sneha Gupta",     "11", "A", "Female", "2008-11-05", "9876543213", "Vikram Gupta",     "9876543203", "parent.sneha@gmail.com",    "22 Saket, Delhi"),
        ("1105", "Karan Mehta",     "11", "A", "Male",   "2008-06-18", "9876543214", "Deepak Mehta",     "9876543204", "parent.karan@gmail.com",    "5 Vasant Kunj, Delhi"),
        ("1201", "Ananya Patel",    "12", "A", "Female", "2007-04-25", "9876543215", "Mahesh Patel",     "9876543205", "parent.ananya@gmail.com",   "33 South Extension, Delhi"),
        ("1202", "Vivek Rao",       "12", "A", "Male",   "2007-09-12", "9876543216", "Sanjay Rao",       "9876543206", "parent.vivek@gmail.com",    "17 Karol Bagh, Delhi"),
        ("1203", "Meera Joshi",     "12", "A", "Female", "2007-02-28", "9876543217", "Prakash Joshi",    "9876543207", "parent.meera@gmail.com",    "9 Dwarka Sector 6, Delhi"),
        ("1204", "Arjun Nair",      "12", "A", "Male",   "2007-08-14", "9876543218", "Ramesh Nair",      "9876543208", "parent.arjun@gmail.com",    "60 Greater Kailash, Delhi"),
        ("1205", "Pooja Chaudhary", "12", "A", "Female", "2007-12-01", "9876543219", "Naresh Chaudhary", "9876543209", "parent.pooja@gmail.com",    "3 Rohini Sector 10, Delhi"),
    ]

    inserted = 0
    skipped = 0
    for s in demo_students:
        roll = s[0]
        name = s[1]
        cursor.execute("SELECT student_id FROM students WHERE roll_number=%s", (roll,))
        if cursor.fetchone():
            print(f"  [SKIP] {name} (Roll {roll}) already exists.")
            skipped += 1
        else:
            cursor.execute("""
                INSERT INTO students
                    (roll_number, full_name, class, section, gender, dob,
                     phone, parent_name, parent_contact, email, address, student_password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (*s, roll))
            print(f"  [ADD]  {name} (Roll {roll}) - Class {s[2]}-{s[3]}")
            inserted += 1

    print(f"\n  Students: {inserted} added, {skipped} already existed.")

    # -------------------------------------------------------
    # Demo Teachers
    # -------------------------------------------------------
    demo_teachers = [
        ("Mr. Sharma", "Mathematics", "9876543001", "sharma.math@example.com"),
        ("Mrs. Verma", "Physics", "9876543002", "verma.phy@example.com"),
        ("Miss Gupta", "English", "9876543003", "gupta.eng@example.com"),
        ("Mr. Singh", "Computer Science", "9876543004", "singh.cs@example.com"),
        ("Mr. Patel", "Chemistry", "9876543005", "patel.chem@example.com"),
    ]
    t_inserted = 0
    for t in demo_teachers:
        cursor.execute("SELECT teacher_id FROM teachers WHERE name=%s", (t[0],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO teachers (name, subject, phone, email) VALUES (%s, %s, %s, %s)", t)
            t_inserted += 1
    print(f"  Teachers: {t_inserted} added.")

    # -------------------------------------------------------
    # Demo Enrollment Requests
    # -------------------------------------------------------
    demo_requests = [
        ("Rahul Dev", "11", "B", "Male", "2008-05-12", "9988776655", "Suresh Dev", "9988776600", "rahul.dev@gmail.com", "15 Nehru Place, Delhi", "Pending"),
        ("Neha Khatri", "11", "B", "Female", "2008-09-20", "9988776656", "Raj Khatri", "9988776601", "neha.k@gmail.com", "42 Hauz Khas, Delhi", "Pending"),
        ("Siddharth Roy", "12", "B", "Male", "2007-01-15", "9988776657", "Amit Roy", "9988776602", "sid.roy@gmail.com", "18 Janakpuri, Delhi", "Pending"),
    ]
    req_inserted = 0
    cursor.execute("SELECT count(*) FROM enrollment_requests")
    if cursor.fetchone()[0] == 0:
        for r in demo_requests:
            cursor.execute("""
                INSERT INTO enrollment_requests (full_name, class, section, gender, dob, phone, parent_name, parent_contact, email, address, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
            req_inserted += 1
    print(f"  Enrollment Requests: {req_inserted} added.")

    # -------------------------------------------------------
    # Historical Attendance Demo (Past 5 days + Today)
    # -------------------------------------------------------
    from datetime import date, timedelta
    import random
    
    today = date.today()
    att_inserted = 0
    
    cursor.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    subjects = ["English", "Mathematics", "Physics", "Chemistry", "Computer Science"]
    
    for i in range(5):
        d = today - timedelta(days=i)
        if d.weekday() >= 5: continue # skip weekends
        d_str = d.strftime("%Y-%m-%d")
        
        for sid in student_ids:
            # Generate random but realistic attendance
            rand = random.random()
            if rand < 0.85: status = "Present"
            elif rand < 0.92: status = "Absent"
            elif rand < 0.97: status = "Late"
            else: status = "Leave"
            
            # Use English as a default subject for demo
            try:
                cursor.execute("""
                    INSERT INTO attendance (student_id, date, subject, status, remarks)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status=VALUES(status), remarks=VALUES(remarks)
                """, (sid, d_str, "English", status, "Demo historical data"))
                att_inserted += 1
            except Exception:
                pass

    conn.commit()
    cursor.close()
    conn.close()

    print(f"  Attendance: {att_inserted} records inserted across last 5 days.")

    # -------------------------------------------------------
    # Step 3: Verify
    # -------------------------------------------------------
    print("\nSTEP 3: Verifying...")
    conn2 = mysql.connector.connect(**DB_CONFIG)
    cur2 = conn2.cursor()
    cur2.execute("SELECT COUNT(*) FROM students")
    total = cur2.fetchone()[0]
    cur2.execute("SELECT COUNT(*) FROM attendance WHERE date=%s", (today.strftime("%Y-%m-%d"),))
    att_count = cur2.fetchone()[0]
    cur2.execute("SELECT COUNT(*) FROM enrollment_requests")
    req_count = cur2.fetchone()[0]
    cur2.execute("SELECT COUNT(*) FROM teachers")
    tch_count = cur2.fetchone()[0]
    cur2.close()
    conn2.close()

    print(f"  Total Students in DB : {total}")
    print(f"  Attendance records today: {att_count}")
    print(f"  Enrollment Requests pending: {req_count}")
    print(f"  Teachers in DB: {tch_count}")

    print("\n" + "=" * 50)
    print("SUCCESS! Demo data is ready.")
    print("=" * 50)
    print("\nNow run:  python main.py")
    print("You should see:")
    print(f"  - Total Students: {total}")
    print(f"  - Enrollment requests in sidebar")
    print(f"  - Populated Analytics Charts")
    print("  - Students module with CSV Import + ID Card buttons")

except mysql.connector.Error as e:
    print(f"\n[ERROR] Database error: {e}")
    print("\nCheck that MySQL is running and the password in DB_CONFIG is correct.")
    print("Current config:")
    print("  host: localhost")
    print("  user: root")
    print("  password: SatyAi")
    print("  database: attendance_system")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
