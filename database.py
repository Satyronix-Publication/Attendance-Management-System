
# database.py
# Attendance Management System - CBSE Class 12 Project
# Database Connection and Table Creation

import mysql.connector

# -------------------------------------------------------
# Database Configuration
# -------------------------------------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'SatyAi'
}

DB_NAME = 'attendance_system'


def get_connection():
    """Returns a connection to the attendance_system database."""
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_NAME
    )
    return conn


def create_database():
    """Creates the database and all required tables."""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # -------------------------------------------------------
        # Users Table (Admin & Teacher login)
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role ENUM('admin', 'teacher') DEFAULT 'teacher',
                name VARCHAR(100) NOT NULL
            )
        """)

        # -------------------------------------------------------
        # Students Table
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                roll_number VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                class VARCHAR(10) NOT NULL,
                section VARCHAR(50) NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                dob DATE,
                phone VARCHAR(15),
                parent_name VARCHAR(100),
                parent_contact VARCHAR(15),
                email VARCHAR(100),
                address TEXT,
                student_password VARCHAR(100) DEFAULT 'password123'
            )
        """)

        # Add column if missing (for existing DBs)
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN student_password VARCHAR(100) DEFAULT 'password123'")
        except mysql.connector.Error:
            pass # Column likely exists

        # Fix existing table if section column is too small
        cursor.execute("""
            ALTER TABLE students MODIFY COLUMN section VARCHAR(50) NOT NULL
        """)

        # -------------------------------------------------------
        # Teachers Table
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                email VARCHAR(100)
            )
        """)

        # -------------------------------------------------------
        # Subjects Table
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INT AUTO_INCREMENT PRIMARY KEY,
                subject_name VARCHAR(100) UNIQUE NOT NULL
            )
        """)

        # -------------------------------------------------------
        # Attendance Table
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                date DATE NOT NULL,
                subject VARCHAR(100) NOT NULL,
                status ENUM('Present', 'Absent', 'Late', 'Leave') NOT NULL,
                remarks VARCHAR(200),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                UNIQUE KEY unique_attendance (student_id, date, subject)
            )
        """)

        # -------------------------------------------------------
        # Enrollment Requests Table
        # -------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollment_requests (
                request_id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                class VARCHAR(10) NOT NULL,
                section VARCHAR(50) NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                dob DATE,
                phone VARCHAR(15),
                parent_name VARCHAR(100),
                parent_contact VARCHAR(15),
                email VARCHAR(100),
                address TEXT,
                status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -------------------------------------------------------
        # Insert Default Admin Account (if not exists)
        # -------------------------------------------------------
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password, role, name)
                VALUES (%s, %s, %s, %s)
            """, ('admin', 'admin123', 'admin', 'Administrator'))

        cursor.execute("SELECT * FROM users WHERE username = 'shivam'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (username, password, role, name)
                VALUES (%s, %s, %s, %s)
            """, ('shivam', 'shivam', 'admin', 'Shivam'))

        # -------------------------------------------------------
        # Insert Default Subjects for Class 11 & 12 (if not exists)
        # -------------------------------------------------------
        subjects = [
            ('English',), ('Mathematics',), ('Physics',),
            ('Chemistry',), ('Biology',), ('Computer Science',),
            ('Accountancy',), ('Business Studies',), ('Economics',),
            ('Physical Education',)
        ]
        for subj in subjects:
            cursor.execute("""
                INSERT IGNORE INTO subjects (subject_name) VALUES (%s)
            """, subj)

        conn.commit()
        print("Database and tables created successfully.")
        print("Default Admin -> Username: admin | Password: admin123")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def insert_demo_data():
    """Insert 10 sample students + today's attendance demo data."""
    demo_students = [
        # roll, name, class, section, gender, dob, phone, parent, parent_contact, email, address
        ("1101", "Aarav Sharma",    "11", "A", "Male",   "2008-03-15", "9876543210", "Rajesh Sharma",   "9876543200", "parent.aarav@gmail.com",    "12 MG Road, Delhi"),
        ("1102", "Priya Singh",     "11", "A", "Female", "2008-07-22", "9876543211", "Suresh Singh",    "9876543201", "parent.priya@gmail.com",     "45 Connaught Place, Delhi"),
        ("1103", "Rohan Verma",     "11", "A", "Male",   "2008-01-10", "9876543212", "Anil Verma",      "9876543202", "parent.rohan@gmail.com",     "8 Lajpat Nagar, Delhi"),
        ("1104", "Sneha Gupta",     "11", "A", "Female", "2008-11-05", "9876543213", "Vikram Gupta",    "9876543203", "parent.sneha@gmail.com",     "22 Saket, Delhi"),
        ("1105", "Karan Mehta",     "11", "A", "Male",   "2008-06-18", "9876543214", "Deepak Mehta",    "9876543204", "parent.karan@gmail.com",     "5 Vasant Kunj, Delhi"),
        ("1201", "Ananya Patel",    "12", "A", "Female", "2007-04-25", "9876543215", "Mahesh Patel",    "9876543205", "parent.ananya@gmail.com",    "33 South Extension, Delhi"),
        ("1202", "Vivek Rao",       "12", "A", "Male",   "2007-09-12", "9876543216", "Sanjay Rao",      "9876543206", "parent.vivek@gmail.com",     "17 Karol Bagh, Delhi"),
        ("1203", "Meera Joshi",     "12", "A", "Female", "2007-02-28", "9876543217", "Prakash Joshi",   "9876543207", "parent.meera@gmail.com",     "9 Dwarka Sector 6, Delhi"),
        ("1204", "Arjun Nair",      "12", "A", "Male",   "2007-08-14", "9876543218", "Ramesh Nair",     "9876543208", "parent.arjun@gmail.com",     "60 Greater Kailash, Delhi"),
        ("1205", "Pooja Chaudhary", "12", "A", "Female", "2007-12-01", "9876543219", "Naresh Chaudhary","9876543209", "parent.pooja@gmail.com",     "3 Rohini Sector 10, Delhi"),
    ]

    demo_attendance = [
        # roll_number -> status for today's English class
        ("1101", "Present"),
        ("1102", "Present"),
        ("1103", "Absent"),
        ("1104", "Present"),
        ("1105", "Late"),
        ("1201", "Present"),
        ("1202", "Present"),
        ("1203", "Present"),
        ("1204", "Absent"),
        ("1205", "Present"),
    ]

    try:
        conn = get_connection()
        cursor = conn.cursor()

        inserted_students = 0
        for s in demo_students:
            cursor.execute("SELECT student_id FROM students WHERE roll_number=%s", (s[0],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO students
                        (roll_number, full_name, class, section, gender, dob,
                         phone, parent_name, parent_contact, email, address)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, s)
                inserted_students += 1

        # Insert today's attendance for demo
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")

        inserted_att = 0
        for roll, status in demo_attendance:
            cursor.execute("SELECT student_id FROM students WHERE roll_number=%s", (roll,))
            row = cursor.fetchone()
            if row:
                sid = row[0]
                cursor.execute("""
                    INSERT IGNORE INTO attendance (student_id, date, subject, status, remarks)
                    VALUES (%s, %s, %s, %s, %s)
                """, (sid, today, "English", status, "Demo data"))
                inserted_att += 1

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Demo data inserted: {inserted_students} students, {inserted_att} attendance records.")

    except mysql.connector.Error as err:
        print(f"Demo Data Error: {err}")


# Run setup when this file is executed directly
if __name__ == "__main__":
    create_database()
    insert_demo_data()
