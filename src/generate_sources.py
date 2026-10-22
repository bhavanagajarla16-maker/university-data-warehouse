"""
generate_sources.py
Generates realistic heterogeneous source datasets for University Data Warehouse Consolidation.
Sources:
  1. Student Information System (CSV) -> data/sources/sis_students.csv
  2. Learning Management System Logs (JSON) -> data/sources/lms_engagement.json
  3. Legacy ERP Examination & Fee Records (SQLite DB) -> data/sources/legacy_erp.db
"""

import os
import random
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
os.makedirs(SOURCES_DIR, exist_ok=True)

random.seed(42)

# Master definitions
DEPARTMENTS = [
    {"dept_code": "ME", "dept_name": "Mechanical Engineering", "college": "College of Engineering"},
    {"dept_code": "CSE", "dept_name": "Computer Science & Engineering", "college": "College of Engineering"},
    {"dept_code": "ECE", "dept_name": "Electronics & Communication Engineering", "college": "College of Engineering"},
    {"dept_code": "EEE", "dept_name": "Electrical & Electronics Engineering", "college": "College of Engineering"},
]

COURSES = [
    {"course_code": "DMW-401", "course_name": "Data Mining & Warehousing", "dept_code": "CSE", "credits": 4},
    {"course_code": "THM-402", "course_name": "Applied Thermodynamics", "dept_code": "ME", "credits": 4},
    {"course_code": "CAD-403", "course_name": "Computer Aided Design & Manufacturing", "dept_code": "ME", "credits": 3},
    {"course_code": "DSP-404", "course_name": "Digital Signal Processing", "dept_code": "ECE", "credits": 4},
    {"course_code": "PS-405", "course_name": "Power Systems Analysis", "dept_code": "EEE", "credits": 3},
    {"course_code": "AI-406", "course_name": "Artificial Intelligence & ML", "dept_code": "CSE", "credits": 4},
]

FACULTY = [
    {"faculty_code": "FAC101", "faculty_name": "Mr. K. Naresh Babu", "designation": "Associate Professor", "dept_code": "CSE"},
    {"faculty_code": "FAC102", "faculty_name": "Dr. V. Ramanjaneyulu", "designation": "Professor & HOD", "dept_code": "ME"},
    {"faculty_code": "FAC103", "faculty_name": "Dr. S. K. Lakshmi", "designation": "Assistant Professor", "dept_code": "ECE"},
    {"faculty_code": "FAC104", "faculty_name": "Mr. P. Srinivas Rao", "designation": "Senior Lecturer", "dept_code": "EEE"},
]

FIRST_NAMES = ["Bhavani", "Karthik", "Sneha", "Rahul", "Pooja", "Vikram", "Ananya", "Rohan", "Divya", "Suresh", "Sai", "Manish", "Deepa", "Harish", "Pravallika"]
LAST_NAMES = ["Prasad", "Reddy", "Sharma", "Varma", "Chowdary", "Rao", "Naidu", "Patel", "Kumar", "Iyer"]

def generate_heterogeneous_sources():
    print("[*] Generating Heterogeneous Source Datasets...")

    # 1. Student Information System (CSV)
    students = []
    # Guarantee user's student ID
    students.append({
        "student_id": 1001,
        "roll_no": "23ME1A5449",
        "first_name": "Bhavani Prasad",
        "last_name": "K.",
        "gender": "Male",
        "dob": "2003-05-14",
        "department_code": "ME",
        "admission_year": 2023,
        "current_semester": 5,
        "category": "General",
        "status": "Active"
    })

    # Generate additional 59 students across departments
    for i in range(2, 61):
        dept = random.choice(DEPARTMENTS)["dept_code"]
        roll = f"23{dept}1A{5400 + i}"
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        gender = random.choice(["Male", "Female"])
        birth_year = random.randint(2002, 2004)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        students.append({
            "student_id": 1000 + i,
            "roll_no": roll,
            "first_name": fname,
            "last_name": lname,
            "gender": gender,
            "dob": dob,
            "department_code": dept,
            "admission_year": 2023,
            "current_semester": random.choice([4, 5, 6]),
            "category": random.choice(["General", "OBC", "SC/ST", "EWS"]),
            "status": "Active"
        })

    csv_path = os.path.join(SOURCES_DIR, "sis_students.csv")
    df_students = pd.DataFrame(students)
    df_students.to_csv(csv_path, index=False)
    print(f"  [+] Created Source 1 (CSV): {csv_path} ({len(df_students)} records)")

    # 2. Learning Management System Logs (JSON)
    lms_logs = []
    log_id = 50001
    for s in students:
        roll = s["roll_no"]
        # enroll in 3 to 4 courses
        assigned_courses = random.sample(COURSES, k=random.randint(3, 4))
        for c in assigned_courses:
            log_id += 1
            login_count = random.randint(15, 95)
            video_hours = round(random.uniform(5.5, 48.0), 2)
            assignment_score = round(random.uniform(55.0, 98.0), 1)
            # Give good score for 23ME1A5449
            if roll == "23ME1A5449":
                assignment_score = round(random.uniform(85.0, 99.0), 1)
                login_count = random.randint(70, 110)
            
            lms_logs.append({
                "log_id": log_id,
                "student_roll_no": roll,
                "course_code": c["course_code"],
                "total_access_count": login_count,
                "watch_time_hours": video_hours,
                "assignment_percentage": assignment_score,
                "last_active_timestamp": (datetime(2026, 9, 1) + timedelta(days=random.randint(1, 45))).isoformat()
            })

    json_path = os.path.join(SOURCES_DIR, "lms_engagement.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(lms_logs, f, indent=2)
    print(f"  [+] Created Source 2 (JSON): {json_path} ({len(lms_logs)} records)")

    # 3. Legacy ERP Examination & Fee Records (SQLite Database)
    db_path = os.path.join(SOURCES_DIR, "legacy_erp.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables in legacy source
    cursor.execute("""
    CREATE TABLE legacy_faculty (
        faculty_code TEXT PRIMARY KEY,
        faculty_name TEXT,
        designation TEXT,
        dept_code TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE legacy_exam_marks (
        exam_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_roll_no TEXT,
        course_code TEXT,
        semester INTEGER,
        academic_year TEXT,
        internal_marks REAL,
        external_marks REAL,
        attendance_percentage REAL,
        faculty_code TEXT,
        exam_date TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE legacy_fee_payments (
        transaction_id TEXT PRIMARY KEY,
        student_roll_no TEXT,
        academic_year TEXT,
        semester INTEGER,
        tuition_fee REAL,
        scholarship_waiver REAL,
        amount_paid REAL,
        payment_date TEXT,
        payment_mode TEXT
    );
    """)

    # Insert faculty
    for fac in FACULTY:
        cursor.execute("INSERT INTO legacy_faculty VALUES (?, ?, ?, ?)",
                       (fac["faculty_code"], fac["faculty_name"], fac["designation"], fac["dept_code"]))

    # Insert exam marks matching courses
    exam_dates = ["2026-05-15", "2026-05-18", "2026-05-22", "2026-05-25"]
    for s in students:
        roll = s["roll_no"]
        dept = s["department_code"]
        sem = s["current_semester"]
        
        # Determine courses for student
        dept_courses = [c for c in COURSES if c["dept_code"] == dept]
        if not dept_courses:
            dept_courses = COURSES[:2]
        
        # Add DMW-401 for everyone or CSE/ME
        if COURSES[0] not in dept_courses:
            dept_courses.append(COURSES[0])

        for c in dept_courses:
            int_marks = random.randint(22, 30) if roll == "23ME1A5449" else random.randint(14, 30)
            ext_marks = random.randint(50, 70) if roll == "23ME1A5449" else random.randint(28, 70)
            att_pct = round(random.uniform(75.0, 96.0), 1) if roll == "23ME1A5449" else round(random.uniform(62.0, 95.0), 1)
            fac = random.choice(FACULTY)["faculty_code"]
            ex_date = random.choice(exam_dates)
            
            cursor.execute("""
            INSERT INTO legacy_exam_marks 
            (student_roll_no, course_code, semester, academic_year, internal_marks, external_marks, attendance_percentage, faculty_code, exam_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (roll, c["course_code"], sem, "2025-26", int_marks, ext_marks, att_pct, fac, ex_date))

        # Insert Fee record
        tuition = 65000.0
        waiver = 25000.0 if s["category"] in ["SC/ST", "EWS"] else (10000.0 if roll == "23ME1A5449" else 0.0)
        paid = tuition - waiver
        tx_id = f"TXN-{roll}-{sem}"
        cursor.execute("""
        INSERT INTO legacy_fee_payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx_id, roll, "2025-26", sem, tuition, waiver, paid, "2026-01-10", "Online NetBanking"))

    conn.commit()
    conn.close()
    print(f"  [+] Created Source 3 (Legacy SQLite DB): {db_path}")
    print("[SUCCESS] Heterogeneous Sources Generated Successfully!\n")

if __name__ == "__main__":
    generate_heterogeneous_sources()
