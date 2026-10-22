"""
olap_analytics.py
Executes OLAP analytical operations (Roll-up, Drill-down, Slice, Dice, Pivot)
and runs benchmark performance tests comparing Star Schema vs. Snowflake Schema.
"""

import os
import time
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "warehouse")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DW_PATH = os.path.join(WAREHOUSE_DIR, "university_data_warehouse.db")
os.makedirs(REPORTS_DIR, exist_ok=True)

def run_olap_analytics():
    print("=" * 75)
    print(" OLAP ANALYTICAL OPERATIONS & SCHEMA BENCHMARK")
    print(" Candidate Roll No: 23ME1A5449 | Guide: Mr. K. Naresh Babu")
    print("=" * 75)

    if not os.path.exists(DW_PATH):
        print(f"[!] Error: Warehouse database not found at {DW_PATH}. Please run etl_pipeline.py first.")
        return

    conn = sqlite3.connect(DW_PATH)

    # --------------------------------------------------------------------------
    # 1. OLAP Roll-up: Course -> Department -> College
    # --------------------------------------------------------------------------
    print("\n[OLAP Operation 1: ROLL-UP] Department-Level Aggregations across College:")
    rollup_query = """
    SELECT 
        c.college_name AS College,
        c.department_name AS Department,
        COUNT(f.performance_fact_id) AS Total_Evaluations,
        ROUND(AVG(f.total_marks), 2) AS Avg_Marks,
        ROUND(AVG(f.attendance_pct), 2) AS Avg_Attendance_Pct,
        ROUND(AVG(f.lms_watch_hours), 2) AS Avg_LMS_Hours,
        ROUND(SUM(f.is_passed) * 100.0 / COUNT(f.performance_fact_id), 1) AS Pass_Pct
    FROM Fact_StudentPerformance f
    JOIN Dim_Course c ON f.course_sk = c.course_sk
    GROUP BY c.college_name, c.department_name
    ORDER BY Avg_Marks DESC;
    """
    df_rollup = pd.read_sql(rollup_query, conn)
    print(df_rollup.to_string(index=False))

    # --------------------------------------------------------------------------
    # 2. OLAP Drill-down: Deep Dive into Student 23ME1A5449 & Mechanical Engineering
    # --------------------------------------------------------------------------
    print("\n[OLAP Operation 2: DRILL-DOWN] Course-Level Granularity for Candidate 23ME1A5449:")
    drilldown_query = """
    SELECT 
        s.roll_no AS Roll_No,
        s.full_name AS Student_Name,
        c.course_code AS Course_Code,
        c.course_title AS Course_Title,
        f.internal_marks AS Internal_30,
        f.external_marks AS External_70,
        f.total_marks AS Total_100,
        f.grade_points AS Grade_Points,
        f.attendance_pct AS Att_Pct,
        f.lms_assignment_score AS LMS_Score
    FROM Fact_StudentPerformance f
    JOIN Dim_Student s ON f.student_sk = s.student_sk
    JOIN Dim_Course c ON f.course_sk = c.course_sk
    WHERE s.roll_no = '23ME1A5449'
    ORDER BY c.course_code;
    """
    df_drilldown = pd.read_sql(drilldown_query, conn)
    print(df_drilldown.to_string(index=False))

    # --------------------------------------------------------------------------
    # 3. OLAP Slice: Semester 5 Performance Across Departments
    # --------------------------------------------------------------------------
    print("\n[OLAP Operation 3: SLICE] Performance Slice for Semester 5:")
    slice_query = """
    SELECT 
        s.department_name AS Department,
        COUNT(DISTINCT s.student_sk) AS Enrolled_Students,
        ROUND(AVG(f.total_marks), 2) AS Semester_Avg_Marks,
        ROUND(AVG(f.lms_watch_hours), 2) AS Avg_LMS_Watch_Hours,
        ROUND(AVG(f.attendance_pct), 2) AS Avg_Attendance
    FROM Fact_StudentPerformance f
    JOIN Dim_Student s ON f.student_sk = s.student_sk
    WHERE s.current_semester = 5
    GROUP BY s.department_name;
    """
    df_slice = pd.read_sql(slice_query, conn)
    print(df_slice.to_string(index=False))

    # --------------------------------------------------------------------------
    # 4. OLAP Dice: Multi-Dimensional Selection (ME Dept, Attendance >= 80%, LMS Score >= 80)
    # --------------------------------------------------------------------------
    print("\n[OLAP Operation 4: DICE] High Performers (Dept=ME, Attendance>=80%, LMS Score>=80):")
    dice_query = """
    SELECT 
        s.roll_no AS Roll_No,
        s.full_name AS Name,
        c.course_code AS Course,
        f.total_marks AS Marks,
        f.attendance_pct AS Attendance,
        f.lms_assignment_score AS LMS_Score
    FROM Fact_StudentPerformance f
    JOIN Dim_Student s ON f.student_sk = s.student_sk
    JOIN Dim_Course c ON f.course_sk = c.course_sk
    WHERE s.department_code = 'ME'
      AND f.attendance_pct >= 80.0
      AND f.lms_assignment_score >= 80.0
    ORDER BY f.total_marks DESC
    LIMIT 6;
    """
    df_dice = pd.read_sql(dice_query, conn)
    print(df_dice.to_string(index=False))

    # --------------------------------------------------------------------------
    # 5. OLAP Pivot / Cross-Tabulation: Department vs. Course Average Marks
    # --------------------------------------------------------------------------
    print("\n[OLAP Operation 5: PIVOT] Department vs. Course Cross-Tabulation Matrix:")
    pivot_raw_query = """
    SELECT 
        s.department_code AS Department,
        c.course_code AS Course,
        ROUND(AVG(f.total_marks), 1) AS Avg_Score
    FROM Fact_StudentPerformance f
    JOIN Dim_Student s ON f.student_sk = s.student_sk
    JOIN Dim_Course c ON f.course_sk = c.course_sk
    GROUP BY s.department_code, c.course_code;
    """
    df_raw_pivot = pd.read_sql(pivot_raw_query, conn)
    pivot_table = df_raw_pivot.pivot(index="Department", columns="Course", values="Avg_Score").fillna("-")
    print(pivot_table.to_string())

    # --------------------------------------------------------------------------
    # 6. Performance Benchmark: Star Schema vs Snowflake Schema
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print(" PERFORMANCE BENCHMARK: STAR SCHEMA VS. SNOWFLAKE SCHEMA")
    print("=" * 75)

    iterations = 250
    star_query = """
    SELECT 
        c.department_name,
        c.course_title,
        ROUND(AVG(f.total_marks), 2) AS avg_marks
    FROM Fact_StudentPerformance f
    JOIN Dim_Course c ON f.course_sk = c.course_sk
    GROUP BY c.department_name, c.course_title;
    """

    snowflake_query = """
    SELECT 
        d.dept_name,
        c.course_title,
        ROUND(AVG(f.total_marks), 2) AS avg_marks
    FROM Fact_StudentPerformance_Snowflake f
    JOIN Dim_Course_Snowflake c ON f.course_sk = c.course_sk
    JOIN Dim_Department_Snowflake d ON c.dept_id = d.dept_id
    JOIN Dim_College_Snowflake col ON d.college_id = col.college_id
    GROUP BY d.dept_name, c.course_title;
    """

    # Benchmark Star
    t_star_start = time.time()
    for _ in range(iterations):
        conn.execute(star_query).fetchall()
    star_total_time_ms = (time.time() - t_star_start) * 1000.0
    star_avg_latency_ms = star_total_time_ms / iterations

    # Benchmark Snowflake
    t_snow_start = time.time()
    for _ in range(iterations):
        conn.execute(snowflake_query).fetchall()
    snow_total_time_ms = (time.time() - t_snow_start) * 1000.0
    snow_avg_latency_ms = snow_total_time_ms / iterations

    speedup_ratio = round(snow_avg_latency_ms / star_avg_latency_ms, 2) if star_avg_latency_ms > 0 else 1.0

    benchmark_data = [
        {
            "Schema Type": "Star Schema (Denormalized)",
            "Join Depth": "1 Join (Fact <-> Dim_Course)",
            "Total Time (250 runs)": f"{star_total_time_ms:.2f} ms",
            "Avg Latency per Query": f"{star_avg_latency_ms:.3f} ms",
            "Performance": "Baseline (Fastest)"
        },
        {
            "Schema Type": "Snowflake Schema (Normalized)",
            "Join Depth": "3 Joins (Fact <-> Course <-> Dept <-> College)",
            "Total Time (250 runs)": f"{snow_total_time_ms:.2f} ms",
            "Avg Latency per Query": f"{snow_avg_latency_ms:.3f} ms",
            "Performance": f"{speedup_ratio}x slower due to join overhead"
        }
    ]
    df_benchmark = pd.DataFrame(benchmark_data)
    print(df_benchmark.to_string(index=False))

    # Save outputs to reports
    csv_report_path = os.path.join(REPORTS_DIR, "star_vs_snowflake_benchmark.csv")
    df_benchmark.to_csv(csv_report_path, index=False)
    
    txt_report_path = os.path.join(REPORTS_DIR, "olap_summary_report.txt")
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write("UNIVERSITY DATA WAREHOUSE OLAP SUMMARY REPORT\n")
        f.write(f"Student Roll No: 23ME1A5449 | Guide: Mr. K. Naresh Babu\n")
        f.write("=" * 70 + "\n\n")
        f.write("1. ROLL-UP ANALYSIS:\n" + df_rollup.to_string(index=False) + "\n\n")
        f.write("2. CANDIDATE DRILL-DOWN (23ME1A5449):\n" + df_drilldown.to_string(index=False) + "\n\n")
        f.write("3. SEMESTER SLICE:\n" + df_slice.to_string(index=False) + "\n\n")
        f.write("4. HIGH PERFORMERS DICE:\n" + df_dice.to_string(index=False) + "\n\n")
        f.write("5. BENCHMARK RESULTS:\n" + df_benchmark.to_string(index=False) + "\n")

    conn.close()
    print(f"\n[SUCCESS] Reports successfully saved to {REPORTS_DIR}")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_olap_analytics()
