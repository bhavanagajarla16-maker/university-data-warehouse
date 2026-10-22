"""
run_all.py
Master execution script for University Data Warehouse Consolidation.
Runs:
  1. Heterogeneous Data Generation
  2. Warehouse Initialization & ETL Pipeline
  3. OLAP Analytics & Star vs. Snowflake Performance Benchmarking
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import generate_sources
from etl_pipeline import UniversityETLPipeline
import olap_analytics

def main():
    print("=" * 80)
    print(" PROJECT TITLE:")
    print(" ETL/ELT Pipeline Optimization for Heterogeneous Sources via Star/Snowflake")
    print(" Schema Design with Dimensional Modeling, Applied to University DW Consolidation")
    print(" Student Roll No : 23ME1A5449")
    print(" Faculty Guide   : Mr. K. Naresh Babu")
    print(" Subject         : Data Mining & Warehousing")
    print("=" * 80)

    # Step 1: Generate Heterogeneous Sources
    print("\n>>> STEP 1: Generating Raw Heterogeneous Data Sources (CSV, JSON, RDBMS)...")
    generate_sources.generate_heterogeneous_sources()

    # Step 2: Run ETL Pipeline
    print("\n>>> STEP 2: Executing ETL Pipeline (Extraction, Cleansing, SCD-2, Star/Snowflake Load)...")
    pipeline = UniversityETLPipeline()
    pipeline.run()

    # Step 3: Run OLAP Analytics & Benchmark
    print("\n>>> STEP 3: Running OLAP Operations (Roll-up, Drill-down, Slice, Dice, Pivot, Benchmark)...")
    olap_analytics.run_olap_analytics()

    print("\n" + "#" * 80)
    print(" [COMPLETED] ALL PHASES EXECUTED SUCCESSFULLY!")
    print(f" Database Location: {os.path.join(BASE_DIR, 'data', 'warehouse', 'university_data_warehouse.db')}")
    print(f" Reports Location : {os.path.join(BASE_DIR, 'reports')}")
    print("#" * 80)

if __name__ == "__main__":
    main()
