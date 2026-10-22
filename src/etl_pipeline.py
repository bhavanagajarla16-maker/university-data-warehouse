"""
etl_pipeline.py
Core ETL/ELT Pipeline Engine for University Data Warehouse Consolidation.
Extracts heterogeneous sources (CSV, JSON, RDBMS), applies data quality
transformations, surrogate key lookups, SCD logic, and loads into Star and Snowflake schemas.
"""

import os
import time
import json
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DW_PATH = os.path.join(WAREHOUSE_DIR, "university_data_warehouse.db")

DEPT_LOOKUP = {
    "ME": {"dept_name": "Mechanical Engineering", "college": "College of Engineering"},
    "CSE": {"dept_name": "Computer Science & Engineering", "college": "College of Engineering"},
    "ECE": {"dept_name": "Electronics & Communication Engineering", "college": "College of Engineering"},
    "EEE": {"dept_name": "Electrical & Electronics Engineering", "college": "College of Engineering"},
}

COURSE_CATALOG = {
    "DMW-401": {"title": "Data Mining & Warehousing", "dept_code": "CSE", "credits": 4},
    "THM-402": {"title": "Applied Thermodynamics", "dept_code": "ME", "credits": 4},
    "CAD-403": {"title": "Computer Aided Design & Manufacturing", "dept_code": "ME", "credits": 3},
    "DSP-404": {"title": "Digital Signal Processing", "dept_code": "ECE", "credits": 4},
    "PS-405": {"title": "Power Systems Analysis", "dept_code": "EEE", "credits": 3},
    "AI-406": {"title": "Artificial Intelligence & ML", "dept_code": "CSE", "credits": 4},
}

class UniversityETLPipeline:
    def __init__(self):
        self.metrics = {}
        self.conn = None

    def initialize_warehouse(self):
        print("\n[Stage 0] Initializing Enterprise Data Warehouse Schema...")
        if os.path.exists(DW_PATH):
            os.remove(DW_PATH)
        self.conn = sqlite3.connect(DW_PATH)
        cursor = self.conn.cursor()

        # Execute Star Schema DDL
        star_sql_path = os.path.join(SQL_DIR, "star_schema.sql")
        with open(star_sql_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

        # Execute Snowflake Schema DDL
        snowflake_sql_path = os.path.join(SQL_DIR, "snowflake_schema.sql")
        with open(snowflake_sql_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

        self.conn.commit()
        print("  [OK] Star Schema & Snowflake Schema tables initialized.")

    def extract(self):
        print("\n[Stage 1: EXTRACTION] Ingesting from Heterogeneous Sources...")
        t0 = time.time()

        # 1. Extract CSV (SIS Students)
        csv_path = os.path.join(SOURCES_DIR, "sis_students.csv")
        df_students_raw = pd.read_csv(csv_path)
        print(f"  [+] Extracted SIS Student Registry (CSV): {len(df_students_raw)} rows")

        # 2. Extract JSON (LMS Engagement)
        json_path = os.path.join(SOURCES_DIR, "lms_engagement.json")
        with open(json_path, "r", encoding="utf-8") as f:
            lms_raw = json.load(f)
        df_lms_raw = pd.DataFrame(lms_raw)
        print(f"  [+] Extracted LMS Activity Logs (JSON): {len(df_lms_raw)} rows")

        # 3. Extract Relational SQLite (Legacy ERP)
        legacy_db = os.path.join(SOURCES_DIR, "legacy_erp.db")
        legacy_conn = sqlite3.connect(legacy_db)
        df_exam_raw = pd.read_sql("SELECT * FROM legacy_exam_marks", legacy_conn)
        df_faculty_raw = pd.read_sql("SELECT * FROM legacy_faculty", legacy_conn)
        df_fee_raw = pd.read_sql("SELECT * FROM legacy_fee_payments", legacy_conn)
        legacy_conn.close()
        print(f"  [+] Extracted Legacy Exam Records (RDBMS): {len(df_exam_raw)} rows")
        print(f"  [+] Extracted Legacy Faculty Records (RDBMS): {len(df_faculty_raw)} rows")
        print(f"  [+] Extracted Legacy Fee Ledger (RDBMS): {len(df_fee_raw)} rows")

        self.metrics["extract_time_sec"] = round(time.time() - t0, 4)
        return {
            "students": df_students_raw,
            "lms": df_lms_raw,
            "exams": df_exam_raw,
            "faculty": df_faculty_raw,
            "fees": df_fee_raw
        }

    def transform(self, raw_data):
        print("\n[Stage 2: TRANSFORMATION] Cleaning, Standardizing & Dimensional Modeling...")
        t0 = time.time()

        # ----------------------------------------------------------------------
        # A. Dimension: Dim_Student (with SCD Type 2 tracking metadata)
        # ----------------------------------------------------------------------
        df_student_dim = raw_data["students"].copy()
        df_student_dim["first_name"] = df_student_dim["first_name"].str.strip().str.title()
        df_student_dim["last_name"] = df_student_dim["last_name"].str.strip().str.title()
        df_student_dim["full_name"] = df_student_dim["first_name"] + " " + df_student_dim["last_name"]
        df_student_dim["department_name"] = df_student_dim["department_code"].map(
            lambda x: DEPT_LOOKUP.get(x, {}).get("dept_name", "General")
        )
        df_student_dim["effective_date"] = "2023-08-01"
        df_student_dim["expiry_date"] = "9999-12-31"
        df_student_dim["is_current"] = 1

        # ----------------------------------------------------------------------
        # B. Dimension: Dim_Course
        # ----------------------------------------------------------------------
        course_records = []
        for code, info in COURSE_CATALOG.items():
            dept_info = DEPT_LOOKUP.get(info["dept_code"], {})
            course_records.append({
                "course_code": code,
                "course_title": info["title"],
                "credits": info["credits"],
                "department_code": info["dept_code"],
                "department_name": dept_info.get("dept_name", "General"),
                "college_name": dept_info.get("college", "College of Engineering")
            })
        df_course_dim = pd.DataFrame(course_records)

        # ----------------------------------------------------------------------
        # C. Dimension: Dim_Faculty
        # ----------------------------------------------------------------------
        df_faculty_dim = raw_data["faculty"].copy()
        df_faculty_dim["department_name"] = df_faculty_dim["dept_code"].map(
            lambda x: DEPT_LOOKUP.get(x, {}).get("dept_name", "General")
        )
        df_faculty_dim.rename(columns={"dept_code": "department_code"}, inplace=True)

        # ----------------------------------------------------------------------
        # D. Dimension: Dim_AcademicTime
        # ----------------------------------------------------------------------
        all_dates = set(raw_data["exams"]["exam_date"].dropna().unique())
        all_dates.update(raw_data["fees"]["payment_date"].dropna().unique())
        time_records = []
        for d_str in sorted(all_dates):
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            time_sk = int(dt.strftime("%Y%m%d"))
            month_num = dt.month
            quarter = (month_num - 1) // 3 + 1
            sem_type = "Even" if month_num in [1, 2, 3, 4, 5, 6] else "Odd"
            time_records.append({
                "time_sk": time_sk,
                "full_date": d_str,
                "calendar_year": dt.year,
                "month_name": dt.strftime("%B"),
                "month_number": month_num,
                "quarter": quarter,
                "academic_year": "2025-26",
                "semester": 4 if sem_type == "Even" else 5,
                "semester_type": sem_type
            })
        df_time_dim = pd.DataFrame(time_records)

        # ----------------------------------------------------------------------
        # E. Fact Transformation & Heterogeneous Integration: Fact_StudentPerformance
        # ----------------------------------------------------------------------
        # Merge Exam data (RDBMS) with LMS activity (JSON)
        df_exams = raw_data["exams"].copy()
        df_lms = raw_data["lms"].copy()

        df_fact_merged = pd.merge(
            df_exams,
            df_lms[["student_roll_no", "course_code", "watch_time_hours", "assignment_percentage"]],
            on=["student_roll_no", "course_code"],
            how="left"
        )
        # Impute missing LMS activity
        df_fact_merged["watch_time_hours"] = df_fact_merged["watch_time_hours"].fillna(12.0)
        df_fact_merged["assignment_percentage"] = df_fact_merged["assignment_percentage"].fillna(70.0)

        # Calculate Facts / Metrics
        df_fact_merged["total_marks"] = df_fact_merged["internal_marks"] + df_fact_merged["external_marks"]
        
        def calculate_grade_points(total):
            if total >= 90: return 10.0
            elif total >= 80: return 9.0
            elif total >= 70: return 8.0
            elif total >= 60: return 7.0
            elif total >= 50: return 6.0
            elif total >= 40: return 5.0
            else: return 0.0

        df_fact_merged["grade_points"] = df_fact_merged["total_marks"].apply(calculate_grade_points)
        df_fact_merged["is_passed"] = df_fact_merged.apply(
            lambda r: 1 if (r["total_marks"] >= 40 and r["external_marks"] >= 25) else 0, axis=1
        )

        self.metrics["transform_time_sec"] = round(time.time() - t0, 4)
        print("  [OK] Applied business metrics: Grade Points, Passing Thresholds, SCD-2 columns.")
        return {
            "dim_student": df_student_dim,
            "dim_course": df_course_dim,
            "dim_faculty": df_faculty_dim,
            "dim_time": df_time_dim,
            "fact_performance_raw": df_fact_merged,
            "fees_raw": raw_data["fees"]
        }

    def load_star_schema(self, transformed):
        print("\n[Stage 3A: LOAD STAR SCHEMA] Loading Dimensions & Star Facts...")
        t0 = time.time()
        cursor = self.conn.cursor()

        # 1. Load Dim_Student
        df_student = transformed["dim_student"]
        for _, row in df_student.iterrows():
            cursor.execute("""
            INSERT INTO Dim_Student 
            (roll_no, first_name, last_name, full_name, gender, dob, department_code, department_name, admission_year, current_semester, category, effective_date, expiry_date, is_current)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["roll_no"], row["first_name"], row["last_name"], row["full_name"],
                row["gender"], row["dob"], row["department_code"], row["department_name"],
                row["admission_year"], row["current_semester"], row["category"],
                row["effective_date"], row["expiry_date"], row["is_current"]
            ))

        # 2. Load Dim_Course
        df_course = transformed["dim_course"]
        for _, row in df_course.iterrows():
            cursor.execute("""
            INSERT INTO Dim_Course (course_code, course_title, credits, department_code, department_name, college_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (row["course_code"], row["course_title"], row["credits"], row["department_code"], row["department_name"], row["college_name"]))

        # 3. Load Dim_Faculty
        df_faculty = transformed["dim_faculty"]
        for _, row in df_faculty.iterrows():
            cursor.execute("""
            INSERT INTO Dim_Faculty (faculty_code, faculty_name, designation, department_code, department_name)
            VALUES (?, ?, ?, ?, ?)
            """, (row["faculty_code"], row["faculty_name"], row["designation"], row["department_code"], row["department_name"]))

        # 4. Load Dim_AcademicTime
        df_time = transformed["dim_time"]
        for _, row in df_time.iterrows():
            cursor.execute("""
            INSERT INTO Dim_AcademicTime 
            (time_sk, full_date, calendar_year, month_name, month_number, quarter, academic_year, semester, semester_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["time_sk"], row["full_date"], row["calendar_year"], row["month_name"],
                row["month_number"], row["quarter"], row["academic_year"], row["semester"], row["semester_type"]
            ))

        self.conn.commit()

        # Build surrogate key lookup mappings
        student_map = dict(cursor.execute("SELECT roll_no, student_sk FROM Dim_Student WHERE is_current = 1").fetchall())
        course_map = dict(cursor.execute("SELECT course_code, course_sk FROM Dim_Course").fetchall())
        faculty_map = dict(cursor.execute("SELECT faculty_code, faculty_sk FROM Dim_Faculty").fetchall())

        # 5. Load Fact_StudentPerformance
        df_fact = transformed["fact_performance_raw"]
        fact_rows = []
        for _, row in df_fact.iterrows():
            s_sk = student_map.get(row["student_roll_no"])
            c_sk = course_map.get(row["course_code"])
            f_sk = faculty_map.get(row["faculty_code"])
            t_sk = int(datetime.strptime(row["exam_date"], "%Y-%m-%d").strftime("%Y%m%d"))

            if s_sk and c_sk and f_sk:
                fact_rows.append((
                    s_sk, c_sk, f_sk, t_sk,
                    row["internal_marks"], row["external_marks"], row["total_marks"],
                    row["grade_points"], row["attendance_percentage"],
                    row["watch_time_hours"], row["assignment_percentage"],
                    row["is_passed"]
                ))

        cursor.executemany("""
        INSERT INTO Fact_StudentPerformance 
        (student_sk, course_sk, faculty_sk, time_sk, internal_marks, external_marks, total_marks, grade_points, attendance_pct, lms_watch_hours, lms_assignment_score, is_passed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fact_rows)

        # 6. Load Fact_FeeTransactions
        df_fee = transformed["fees_raw"]
        fee_rows = []
        for _, row in df_fee.iterrows():
            s_sk = student_map.get(row["student_roll_no"])
            t_sk = int(datetime.strptime(row["payment_date"], "%Y-%m-%d").strftime("%Y%m%d"))
            if s_sk:
                fee_rows.append((s_sk, t_sk, row["tuition_fee"], row["scholarship_waiver"], row["amount_paid"]))

        cursor.executemany("""
        INSERT INTO Fact_FeeTransactions (student_sk, time_sk, tuition_fee, scholarship_waiver, amount_paid)
        VALUES (?, ?, ?, ?, ?)
        """, fee_rows)

        self.conn.commit()
        self.metrics["star_load_time_sec"] = round(time.time() - t0, 4)
        self.metrics["star_fact_records"] = len(fact_rows)
        print(f"  [OK] Loaded Star Schema: {len(fact_rows)} student performance facts & {len(fee_rows)} fee transactions.")

    def load_snowflake_schema(self, transformed):
        print("\n[Stage 3B: LOAD SNOWFLAKE SCHEMA] Loading Normalized Hierarchies...")
        t0 = time.time()
        cursor = self.conn.cursor()

        # 1. College
        cursor.execute("INSERT OR IGNORE INTO Dim_College_Snowflake (college_name) VALUES ('College of Engineering')")
        college_id = cursor.execute("SELECT college_id FROM Dim_College_Snowflake WHERE college_name = 'College of Engineering'").fetchone()[0]

        # 2. Departments
        for code, info in DEPT_LOOKUP.items():
            cursor.execute("""
            INSERT OR IGNORE INTO Dim_Department_Snowflake (dept_code, dept_name, college_id)
            VALUES (?, ?, ?)
            """, (code, info["dept_name"], college_id))
        
        dept_map = dict(cursor.execute("SELECT dept_code, dept_id FROM Dim_Department_Snowflake").fetchall())

        # 3. Courses
        for code, info in COURSE_CATALOG.items():
            cursor.execute("""
            INSERT OR IGNORE INTO Dim_Course_Snowflake (course_code, course_title, credits, dept_id)
            VALUES (?, ?, ?, ?)
            """, (code, info["title"], info["credits"], dept_map[info["dept_code"]]))

        # 4. Faculty
        df_faculty = transformed["dim_faculty"]
        for _, row in df_faculty.iterrows():
            cursor.execute("""
            INSERT OR IGNORE INTO Dim_Faculty_Snowflake (faculty_code, faculty_name, designation, dept_id)
            VALUES (?, ?, ?, ?)
            """, (row["faculty_code"], row["faculty_name"], row["designation"], dept_map[row["department_code"]]))

        # 5. Students
        df_student = transformed["dim_student"]
        for _, row in df_student.iterrows():
            cursor.execute("""
            INSERT INTO Dim_Student_Snowflake 
            (roll_no, first_name, last_name, full_name, gender, dob, dept_id, admission_year, current_semester, category, is_current)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["roll_no"], row["first_name"], row["last_name"], row["full_name"],
                row["gender"], row["dob"], dept_map[row["department_code"]],
                row["admission_year"], row["current_semester"], row["category"], row["is_current"]
            ))

        # 6. Academic Time normalized
        cursor.execute("INSERT OR IGNORE INTO Dim_Time_Year_Snowflake (academic_year) VALUES ('2025-26')")
        year_id = cursor.execute("SELECT academic_year_id FROM Dim_Time_Year_Snowflake WHERE academic_year = '2025-26'").fetchone()[0]

        df_time = transformed["dim_time"]
        for _, row in df_time.iterrows():
            cursor.execute("""
            INSERT OR IGNORE INTO Dim_AcademicTime_Snowflake 
            (time_sk, full_date, month_name, month_number, quarter, semester, semester_type, academic_year_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["time_sk"], row["full_date"], row["month_name"], row["month_number"],
                row["quarter"], row["semester"], row["semester_type"], year_id
            ))

        self.conn.commit()

        # Surrogate mappings for Snowflake
        student_sf_map = dict(cursor.execute("SELECT roll_no, student_sk FROM Dim_Student_Snowflake").fetchall())
        course_sf_map = dict(cursor.execute("SELECT course_code, course_sk FROM Dim_Course_Snowflake").fetchall())
        faculty_sf_map = dict(cursor.execute("SELECT faculty_code, faculty_sk FROM Dim_Faculty_Snowflake").fetchall())

        # Load Fact_StudentPerformance_Snowflake
        df_fact = transformed["fact_performance_raw"]
        sf_fact_rows = []
        for _, row in df_fact.iterrows():
            s_sk = student_sf_map.get(row["student_roll_no"])
            c_sk = course_sf_map.get(row["course_code"])
            f_sk = faculty_sf_map.get(row["faculty_code"])
            t_sk = int(datetime.strptime(row["exam_date"], "%Y-%m-%d").strftime("%Y%m%d"))

            if s_sk and c_sk and f_sk:
                sf_fact_rows.append((
                    s_sk, c_sk, f_sk, t_sk,
                    row["internal_marks"], row["external_marks"], row["total_marks"],
                    row["grade_points"], row["attendance_percentage"],
                    row["watch_time_hours"], row["assignment_percentage"],
                    row["is_passed"]
                ))

        cursor.executemany("""
        INSERT INTO Fact_StudentPerformance_Snowflake 
        (student_sk, course_sk, faculty_sk, time_sk, internal_marks, external_marks, total_marks, grade_points, attendance_pct, lms_watch_hours, lms_assignment_score, is_passed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sf_fact_rows)

        self.conn.commit()
        self.metrics["snowflake_load_time_sec"] = round(time.time() - t0, 4)
        print(f"  [OK] Loaded Snowflake Schema: {len(sf_fact_rows)} facts into normalized structure.")

    def run(self):
        print("=" * 70)
        print(" ETL/ELT PIPELINE EXECUTION FOR UNIVERSITY DATA WAREHOUSE")
        print(" Roll No: 23ME1A5449 | Guide: Mr. K. Naresh Babu")
        print("=" * 70)
        total_start = time.time()
        
        self.initialize_warehouse()
        raw = self.extract()
        transformed = self.transform(raw)
        self.load_star_schema(transformed)
        self.load_snowflake_schema(transformed)
        
        self.conn.close()
        total_elapsed = round(time.time() - total_start, 4)
        print("\n" + "=" * 70)
        print(" [SUMMARY] PIPELINE METRICS & PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"  - Extraction Time        : {self.metrics.get('extract_time_sec')} seconds")
        print(f"  - Transformation Time    : {self.metrics.get('transform_time_sec')} seconds")
        print(f"  - Star Schema Load Time  : {self.metrics.get('star_load_time_sec')} seconds")
        print(f"  - Snowflake Load Time    : {self.metrics.get('snowflake_load_time_sec')} seconds")
        print(f"  - Total Pipeline Time    : {total_elapsed} seconds")
        print(f"  - Fact Records Ingested  : {self.metrics.get('star_fact_records')} rows")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    pipeline = UniversityETLPipeline()
    pipeline.run()
