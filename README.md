# University Enterprise Data Warehouse & ETL/ELT Pipeline

**Project Title:** ETL/ELT Pipeline Optimization for Heterogeneous Sources via Star/Snowflake Schema Design with Dimensional Modeling, Applied to University/Enterprise Data Warehouse Consolidation  
**Candidate Roll No:** `23ME1A5449`  
**Batch / S.No:** `110`  
**Course:** Data Mining & Warehousing  
**Faculty Project Guide:** Mr. K. Naresh Babu  

---

## 📁 Project Directory Structure

```
university_dw_project/
├── data/
│   ├── sources/                  # Heterogeneous Source Silos
│   │   ├── sis_students.csv      # Source 1: Student Information System (CSV)
│   │   ├── lms_engagement.json   # Source 2: Learning Management Logs (JSON)
│   │   └── legacy_erp.db         # Source 3: Legacy RDBMS Database (SQLite)
│   └── warehouse/
│       └── university_data_warehouse.db  # Central Enterprise Data Warehouse
├── sql/
│   ├── star_schema.sql           # DDL: Denormalized Star Schema
│   ├── snowflake_schema.sql      # DDL: Normalized Snowflake Schema
│   └── olap_queries.sql          # Analytical OLAP & Benchmarking Queries
├── src/
│   ├── generate_sources.py       # Mock Heterogeneous Data Generator
│   ├── etl_pipeline.py           # Core Extraction, Cleansing & Loading Engine
│   └── olap_analytics.py         # OLAP Analytical Queries & Benchmark Suite
├── reports/
│   ├── dashboard.html            # Interactive Visual Dashboard Console
│   ├── star_vs_snowflake_benchmark.csv # Benchmark Latency CSV
│   └── olap_summary_report.txt   # Complete Analytical Output Logs
├── run_all.py                    # Master 1-Click Execution Script
├── SYNOPSIS.md                   # Formal Project Synopsis for Guide Approval
└── README.md                     # Documentation & Execution Guide
```

---

## 🚀 How to Run the Project

### Option 1: One-Click Master Execution
Run the master pipeline script using Anaconda Python (or any Python 3.10+):

```powershell
C:\Users\bhava\anaconda3\python.exe run_all.py
```

This single command will:
1. Generate the raw heterogeneous datasets (CSV, JSON, SQLite).
2. Initialize both Star and Snowflake schemas in the warehouse.
3. Run the complete ETL pipeline (clean, transform, compute grade points & SCD Type 2 metadata, load facts & dimensions).
4. Run OLAP operations (Roll-up, Drill-down, Slice, Dice, Pivot).
5. Execute the performance benchmark (Star vs. Snowflake schema latency).

---

## 📊 Viewing the Interactive Dashboard

An interactive dashboard has been generated at:
`reports/dashboard.html`

To view it, double-click the file or open it in your browser:
```powershell
Start-Process "reports\dashboard.html"
```
It displays:
* Department-wise performance roll-up graphs.
* Query latency benchmark between Star Schema and Snowflake Schema.
* Candidate drill-down table for Roll No **23ME1A5449**.
* High performers matrix and key metrics.

---

## 🧠 Core Architectural Concepts Implemented

1. **Heterogeneous Silo Integration:**
   * Ingests from 3 distinct data formats: flat CSV, semi-structured JSON, and relational RDBMS tables.
2. **Kimball Dimensional Modeling:**
   * **Fact Table:** `Fact_StudentPerformance` containing granular metrics (Internal marks, External marks, Attendance %, LMS watch time, Grade points, Pass status).
   * **Conformed Dimensions:** `Dim_Student`, `Dim_Course`, `Dim_Faculty`, `Dim_AcademicTime`.
3. **Slowly Changing Dimensions (SCD Type 2):**
   * Student dimension tracks historical lifecycle via `effective_date`, `expiry_date`, and `is_current` flags.
4. **Star vs. Snowflake Performance Benchmarking:**
   * **Star Schema:** Denormalized structure requires only **1 JOIN**, yielding ~0.33 ms average query latency.
   * **Snowflake Schema:** Normalized hierarchy requires **3 JOINs**, yielding ~0.42 ms average query latency (~1.26x slower due to relational join overhead).

---

## 📝 Academic Submission Files
* Formal synopsis ready for submission: [`SYNOPSIS.md`](./SYNOPSIS.md)
* Summary text report: [`reports/olap_summary_report.txt`](./reports/olap_summary_report.txt)
* Benchmark CSV: [`reports/star_vs_snowflake_benchmark.csv`](./reports/star_vs_snowflake_benchmark.csv)
