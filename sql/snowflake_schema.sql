-- ==============================================================================
-- File: snowflake_schema.sql
-- Project: ETL/ELT Pipeline Optimization for Heterogeneous Sources via
--          Star/Snowflake Schema Design with Dimensional Modeling
-- Student: 23ME1A5449 | Guide: Mr. K. Naresh Babu
-- Description: DDL for Enterprise Data Warehouse in Snowflake Schema (Normalized)
-- ==============================================================================

-- 1. Hierarchy Level 1: College
DROP TABLE IF EXISTS Dim_College_Snowflake;
CREATE TABLE Dim_College_Snowflake (
    college_id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_name TEXT NOT NULL UNIQUE
);

-- 2. Hierarchy Level 2: Department (Normalized with FK to College)
DROP TABLE IF EXISTS Dim_Department_Snowflake;
CREATE TABLE Dim_Department_Snowflake (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_code TEXT NOT NULL UNIQUE,
    dept_name TEXT NOT NULL,
    college_id INTEGER,
    FOREIGN KEY (college_id) REFERENCES Dim_College_Snowflake(college_id)
);

-- 3. Dimension: Course (Normalized with FK to Department)
DROP TABLE IF EXISTS Dim_Course_Snowflake;
CREATE TABLE Dim_Course_Snowflake (
    course_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL UNIQUE,
    course_title TEXT NOT NULL,
    credits INTEGER,
    dept_id INTEGER,
    FOREIGN KEY (dept_id) REFERENCES Dim_Department_Snowflake(dept_id)
);

-- 4. Dimension: Faculty (Normalized with FK to Department)
DROP TABLE IF EXISTS Dim_Faculty_Snowflake;
CREATE TABLE Dim_Faculty_Snowflake (
    faculty_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_code TEXT NOT NULL UNIQUE,
    faculty_name TEXT NOT NULL,
    designation TEXT,
    dept_id INTEGER,
    FOREIGN KEY (dept_id) REFERENCES Dim_Department_Snowflake(dept_id)
);

-- 5. Dimension: Student (Normalized with FK to Department)
DROP TABLE IF EXISTS Dim_Student_Snowflake;
CREATE TABLE Dim_Student_Snowflake (
    student_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    gender TEXT,
    dob TEXT,
    dept_id INTEGER,
    admission_year INTEGER,
    current_semester INTEGER,
    category TEXT,
    is_current INTEGER DEFAULT 1,
    FOREIGN KEY (dept_id) REFERENCES Dim_Department_Snowflake(dept_id)
);

-- 6. Dimension: Time (Snowflake normalized: Day -> Month -> Year)
DROP TABLE IF EXISTS Dim_Time_Year_Snowflake;
CREATE TABLE Dim_Time_Year_Snowflake (
    academic_year_id INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year TEXT NOT NULL UNIQUE
);

DROP TABLE IF EXISTS Dim_AcademicTime_Snowflake;
CREATE TABLE Dim_AcademicTime_Snowflake (
    time_sk INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    month_name TEXT,
    month_number INTEGER,
    quarter INTEGER,
    semester INTEGER,
    semester_type TEXT,
    academic_year_id INTEGER,
    FOREIGN KEY (academic_year_id) REFERENCES Dim_Time_Year_Snowflake(academic_year_id)
);

-- 7. Fact Table in Snowflake Schema
DROP TABLE IF EXISTS Fact_StudentPerformance_Snowflake;
CREATE TABLE Fact_StudentPerformance_Snowflake (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_sk INTEGER NOT NULL,
    course_sk INTEGER NOT NULL,
    faculty_sk INTEGER NOT NULL,
    time_sk INTEGER NOT NULL,
    internal_marks REAL,
    external_marks REAL,
    total_marks REAL,
    grade_points REAL,
    attendance_pct REAL,
    lms_watch_hours REAL,
    lms_assignment_score REAL,
    is_passed INTEGER,
    FOREIGN KEY (student_sk) REFERENCES Dim_Student_Snowflake(student_sk),
    FOREIGN KEY (course_sk) REFERENCES Dim_Course_Snowflake(course_sk),
    FOREIGN KEY (faculty_sk) REFERENCES Dim_Faculty_Snowflake(faculty_sk),
    FOREIGN KEY (time_sk) REFERENCES Dim_AcademicTime_Snowflake(time_sk)
);
