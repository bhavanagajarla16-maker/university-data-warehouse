-- ==============================================================================
-- File: star_schema.sql
-- Project: ETL/ELT Pipeline Optimization for Heterogeneous Sources via
--          Star/Snowflake Schema Design with Dimensional Modeling
-- Student: 23ME1A5449 | Guide: Mr. K. Naresh Babu
-- Description: DDL for Enterprise Data Warehouse in Star Schema (Denormalized)
-- ==============================================================================

-- 1. Dimension: Student (SCD Type 2 enabled)
DROP TABLE IF EXISTS Dim_Student;
CREATE TABLE Dim_Student (
    student_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    gender TEXT,
    dob TEXT,
    department_code TEXT,
    department_name TEXT,
    admission_year INTEGER,
    current_semester INTEGER,
    category TEXT,
    effective_date TEXT,
    expiry_date TEXT,
    is_current INTEGER DEFAULT 1
);

-- 2. Dimension: Course (Denormalized with Department & College attributes)
DROP TABLE IF EXISTS Dim_Course;
CREATE TABLE Dim_Course (
    course_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL UNIQUE,
    course_title TEXT NOT NULL,
    credits INTEGER,
    department_code TEXT,
    department_name TEXT,
    college_name TEXT
);

-- 3. Dimension: Faculty (Denormalized with Department attribute)
DROP TABLE IF EXISTS Dim_Faculty;
CREATE TABLE Dim_Faculty (
    faculty_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_code TEXT NOT NULL UNIQUE,
    faculty_name TEXT NOT NULL,
    designation TEXT,
    department_code TEXT,
    department_name TEXT
);

-- 4. Dimension: Academic Time (Conformed Time Dimension)
DROP TABLE IF EXISTS Dim_AcademicTime;
CREATE TABLE Dim_AcademicTime (
    time_sk INTEGER PRIMARY KEY, -- YYYYMMDD format
    full_date TEXT NOT NULL UNIQUE,
    calendar_year INTEGER,
    month_name TEXT,
    month_number INTEGER,
    quarter INTEGER,
    academic_year TEXT,
    semester INTEGER,
    semester_type TEXT -- 'Odd' or 'Even'
);

-- 5. Fact Table: Student Academic & LMS Performance (Accumulating / Periodic Snapshot Grain)
DROP TABLE IF EXISTS Fact_StudentPerformance;
CREATE TABLE Fact_StudentPerformance (
    performance_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Foreign Keys to Conformed Dimensions
    student_sk INTEGER NOT NULL,
    course_sk INTEGER NOT NULL,
    faculty_sk INTEGER NOT NULL,
    time_sk INTEGER NOT NULL,
    -- Additive & Semi-Additive Numerical Facts / Metrics
    internal_marks REAL,
    external_marks REAL,
    total_marks REAL,
    grade_points REAL,
    attendance_pct REAL,
    lms_watch_hours REAL,
    lms_assignment_score REAL,
    is_passed INTEGER,
    FOREIGN KEY (student_sk) REFERENCES Dim_Student(student_sk),
    FOREIGN KEY (course_sk) REFERENCES Dim_Course(course_sk),
    FOREIGN KEY (faculty_sk) REFERENCES Dim_Faculty(faculty_sk),
    FOREIGN KEY (time_sk) REFERENCES Dim_AcademicTime(time_sk)
);

-- 6. Fact Table: Student Fee Transactions
DROP TABLE IF EXISTS Fact_FeeTransactions;
CREATE TABLE Fact_FeeTransactions (
    fee_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_sk INTEGER NOT NULL,
    time_sk INTEGER NOT NULL,
    tuition_fee REAL,
    scholarship_waiver REAL,
    amount_paid REAL,
    FOREIGN KEY (student_sk) REFERENCES Dim_Student(student_sk),
    FOREIGN KEY (time_sk) REFERENCES Dim_AcademicTime(time_sk)
);

-- ==============================================================================
-- Optimization: B-Tree Indexes on Star Schema Foreign Keys
-- Significantly accelerates star-join operations and dimension slicing
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_fact_student ON Fact_StudentPerformance(student_sk);
CREATE INDEX IF NOT EXISTS idx_fact_course ON Fact_StudentPerformance(course_sk);
CREATE INDEX IF NOT EXISTS idx_fact_faculty ON Fact_StudentPerformance(faculty_sk);
CREATE INDEX IF NOT EXISTS idx_fact_time ON Fact_StudentPerformance(time_sk);
CREATE INDEX IF NOT EXISTS idx_dim_student_roll ON Dim_Student(roll_no, is_current);
