# PROJECT SYNOPSIS

## Title of the Project
**ETL/ELT Pipeline Optimization for Heterogeneous Sources via Star/Snowflake Schema Design with Dimensional Modeling, Applied to University/Enterprise Data Warehouse Consolidation**

---

### **Academic Details**
* **Candidate Roll Number:** `23ME1A5449`
* **Batch / Serial No:** `110`
* **Subject / Domain:** Data Mining & Warehousing (DMW)
* **Faculty Project Guide:** Mr. K. Naresh Babu
* **Degree / Department:** Bachelor of Technology (B.Tech), Mechanical / Engineering

---

## 1. Introduction & Background
Higher education institutions and modern enterprises generate high volumes of multi-modal, distributed data across disparate systems:
1. **Student Information Systems (SIS)** hosted on relational SQL platforms storing demographic and registration profiles.
2. **Learning Management Systems (LMS)** capturing clickstream interactions, video engagement, and digital assignment scores in semi-structured JSON formats.
3. **Legacy ERP Examination & Finance Systems** managing semester grades, fee ledgers, and faculty allocations.

Operating on these fragmented silos prevents institutional leaders from acquiring a unified 360-degree view of student progression, retention risks, and operational throughput.

---

## 2. Problem Statement
Traditional querying directly against operational OLTP (Online Transaction Processing) systems suffers from:
* High query latency and table locking when executing cross-departmental analytical aggregations.
* Inconsistent metrics due to schema divergence, missing keys, and lack of historical versioning (Slowly Changing Dimensions).
* Absence of optimized dimensional modeling (Star vs. Snowflake) suited for OLAP analytical operations (Roll-up, Drill-down, Slice, Dice).

---

## 3. Project Objectives
1. **Heterogeneous Ingestion:** Implement automated extraction pipelines handling CSV files, semi-structured JSON payloads, and relational SQLite/SQL tables.
2. **Dimensional Modeling:** Architect both **Star Schema** (denormalized, optimized for read-heavy OLAP) and **Snowflake Schema** (normalized dimension hierarchies) following Kimball dimensional modeling principles.
3. **ETL Pipeline Optimization:** Implement surrogate key management, data quality validations, missing-value imputation, and **SCD Type 2** (Slowly Changing Dimensions) tracking.
4. **OLAP Analytics & Benchmarking:** Formulate standard OLAP analytical queries and systematically benchmark execution performance between Star and Snowflake schemas.

---

## 4. System Architecture

```
[ Heterogeneous Silos ]
 ├── SIS Student Registry  (CSV)
 ├── LMS Online Activity   (JSON)
 └── Legacy ERP Database   (SQLite/RDBMS)
            │
            ▼
[ Extraction & Staging Layer ] (Pandas & Ingestion Workers)
            │
            ▼
[ Transformation & Quality Engine ]
 ├── Data Standardization & Deduplication
 ├── Surrogate Key Generation (Integer SKs)
 ├── Derived Metric Calculations (Total Marks, Grade Points, Pass Status)
 └── Slowly Changing Dimension (SCD Type 2) Historical Tracking
            │
            ▼
[ Enterprise Data Warehouse (EDW) Storage ]
 ├── Star Schema: Fact_StudentPerformance + Conformed Dimensions
 └── Snowflake Schema: Normalized 3NF Hierarchies (College -> Dept -> Course)
            │
            ▼
[ Analytical OLAP & Reporting Layer ]
 ├── OLAP Roll-up, Drill-down, Slice, Dice, Pivot Operations
 └── Interactive HTML5 / Chart.js Executive Dashboard Console
```

---

## 5. Dimensional Schema Design

### **A. Star Schema Structure**
* **Fact Table:** `Fact_StudentPerformance`
  * *Grain:* One row per student per course per examination cycle.
  * *Foreign Keys:* `student_sk`, `course_sk`, `faculty_sk`, `time_sk`.
  * *Measures:* `internal_marks`, `external_marks`, `total_marks`, `grade_points`, `attendance_pct`, `lms_watch_hours`, `lms_assignment_score`, `is_passed`.
* **Conformed Dimensions:**
  * `Dim_Student`: Surrogate key, Roll No, demographic data, SCD Type 2 timestamps (`effective_date`, `expiry_date`, `is_current`).
  * `Dim_Course`: Course code, title, credits, department name, college name.
  * `Dim_Faculty`: Faculty code, faculty name, designation, department name.
  * `Dim_AcademicTime`: Date SK (YYYYMMDD), full date, month, quarter, academic year, semester type.

### **B. Snowflake Schema Structure**
* Normalizes dimension hierarchies to eliminate redundancy:
  * `Dim_College_Snowflake` (1) &rarr; `Dim_Department_Snowflake` (M) &rarr; `Dim_Course_Snowflake` (M).
  * Evaluated directly against the Star schema to measure relational join overhead.

---

## 6. Implementation Results & Benchmarks

| Metric / Dimension | Star Schema (Denormalized) | Snowflake Schema (Normalized) |
| :--- | :--- | :--- |
| **Join Depth** | **1 Join** (`Fact` &harr; `Dim_Course`) | **3 Joins** (`Fact` &harr; `Course` &harr; `Dept` &harr; `College`) |
| **Average Query Latency** | **0.335 ms** | **0.422 ms** |
| **Query Performance** | **Baseline (1.26x Faster)** | Slower due to multi-hop join latency |
| **ETL Ingestion Throughput**| 136 Fact Records Consolidated | 136 Fact Records Consolidated |
| **Data Loss Rate** | 0.0% (Reconciled) | 0.0% (Reconciled) |

---

## 7. Hardware & Software Requirements
* **Operating System:** Windows 10/11 / Linux
* **Programming Language:** Python 3.10+
* **Core Libraries:** `pandas`, `sqlite3`, `json`, `datetime`
* **Data Storage:** SQLite3 / PostgreSQL Enterprise Data Warehouse
* **Visualization:** Chart.js, HTML5 Responsive Dashboard Console

---

## 8. Viva Voce FAQ & Guide Reference
* **Q1: Why choose Star Schema over 3NF in Data Warehouses?**
  * *Ans:* Star schema minimizes table joins, enabling storage engines to execute high-speed star-join bitmaps and hash joins essential for multi-dimensional aggregation.
* **Q2: What is SCD Type 2?**
  * *Ans:* Slowly Changing Dimension Type 2 preserves historical changes by inserting a new record with effective/expiry date timestamps rather than overwriting existing values.
* **Q3: What role does LMS clickstream play in DW consolidation?**
  * *Ans:* Ingesting semi-structured JSON logs enables correlation between online engagement (watch hours, quiz completion) and summative academic performance.
