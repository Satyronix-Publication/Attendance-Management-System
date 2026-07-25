 # %%


# main.py
# Attendance Management System - CBSE Class 12 Project
# Entry Point - Run this file to start the application

"""
====================================================
   ATTENDANCE MANAGEMENT SYSTEM
   CBSE Class 12 Python Project
====================================================
   Technologies Used:
   - Python 3.x
   - Tkinter (GUI)
   - MySQL (Database)
   - mysql-connector-python (Database Connectivity)

   Default Login Credentials:
   - Username : admin
   - Password : admin123

   Database:
   - Host     : localhost
   - User     : user
   - Password : root
====================================================
"""

import tkinter as tk
from database import create_database
from login import LoginWindow


def main():
    # Step 1: Create database and tables (first run setup)
    print("Setting up database...")
    create_database()

    # Step 2: Open Login Window
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
