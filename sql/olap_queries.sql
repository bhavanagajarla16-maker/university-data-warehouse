-- ==============================================================================
-- File: olap_queries.sql
-- Project: ETL/ELT Pipeline Optimization for Heterogeneous Sources via
--          Star/Snowflake Schema Design with Dimensional Modeling
-- Student: 23ME1A5449 | Guide: Mr. K. Naresh Babu
-- Description: Standard OLAP Analytical Operations & Star vs Snowflake Benchmark
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. OLAP ROLL-UP: Aggregate from Course -> Department -> College level
-- ------------------------------------------------------------------------------
SELECT 
    c.college_name,
    c.department_name,
    COUNT(f.performance_fact_id) AS total_evaluations,
    ROUND(AVG(f.total_marks), 2) AS avg_total_marks,
    ROUND(AVG(f.attendance_pct), 2) AS avg_attendance_pct,
    ROUND(AVG(f.lms_watch_hours), 2) AS avg_lms_hours,
    ROUND(SUM(f.is_passed) * 100.0 / COUNT(f.performance_fact_id), 2) AS pass_percentage
FROM Fact_StudentPerformance f
JOIN Dim_Course c ON f.course_sk = c.course_sk
GROUP BY c.college_name, c.department_name
ORDER BY avg_total_marks DESC;


-- ------------------------------------------------------------------------------
-- 2. OLAP DRILL-DOWN: Deep dive into Mechanical Engineering by Course & Student
-- ------------------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.full_name,
    c.course_code,
    c.course_title,
    f.internal_marks,
    f.external_marks,
    f.total_marks,
    f.grade_points,
    f.lms_assignment_score
FROM Fact_StudentPerformance f
JOIN Dim_Student s ON f.student_sk = s.student_sk
JOIN Dim_Course c ON f.course_sk = c.course_sk
WHERE s.department_code = 'ME'
ORDER BY s.roll_no, c.course_code;


-- ------------------------------------------------------------------------------
-- 3. OLAP SLICE: Slicing by Academic Semester (Semester 5 performance snapshot)
-- ------------------------------------------------------------------------------
SELECT 
    s.department_name,
    COUNT(DISTINCT s.student_sk) AS student_count,
    ROUND(AVG(f.total_marks), 2) AS semester_avg_marks,
    ROUND(AVG(f.lms_watch_hours), 2) AS avg_lms_hours
FROM Fact_StudentPerformance f
JOIN Dim_Student s ON f.student_sk = s.student_sk
WHERE s.current_semester = 5
GROUP BY s.department_name;


-- ------------------------------------------------------------------------------
-- 4. OLAP DICE: Multi-dimensional Subcube Selection
-- (Mechanical Engineering AND High Attendance >= 80% AND High LMS Hours >= 20)
-- ------------------------------------------------------------------------------
SELECT 
    s.roll_no,
    s.full_name,
    c.course_code,
    f.total_marks,
    f.attendance_pct,
    f.lms_watch_hours,
    f.lms_assignment_score
FROM Fact_StudentPerformance f
JOIN Dim_Student s ON f.student_sk = s.student_sk
JOIN Dim_Course c ON f.course_sk = c.course_sk
WHERE s.department_code = 'ME'
  AND f.attendance_pct >= 80.0
  AND f.lms_watch_hours >= 20.0
ORDER BY f.total_marks DESC;


-- ------------------------------------------------------------------------------
-- 5. BENCHMARK COMPARISON QUERY: Star Schema (Single Denormalized Join Level)
-- ------------------------------------------------------------------------------
SELECT 
    c.department_name,
    c.course_title,
    ROUND(AVG(f.total_marks), 2) AS avg_marks
FROM Fact_StudentPerformance f
JOIN Dim_Course c ON f.course_sk = c.course_sk
GROUP BY c.department_name, c.course_title;


-- ------------------------------------------------------------------------------
-- 6. BENCHMARK COMPARISON QUERY: Snowflake Schema (Multi-Hop Normalized Joins)
-- ------------------------------------------------------------------------------
SELECT 
    d.dept_name,
    c.course_title,
    ROUND(AVG(f.total_marks), 2) AS avg_marks
FROM Fact_StudentPerformance_Snowflake f
JOIN Dim_Course_Snowflake c ON f.course_sk = c.course_sk
JOIN Dim_Department_Snowflake d ON c.dept_id = d.dept_id
JOIN Dim_College_Snowflake col ON d.college_id = col.college_id
GROUP BY d.dept_name, c.course_title;
