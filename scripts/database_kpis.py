"""
Step 6: SQLite Storage & Analytical KPI Engine

Loads data/processed/deployment_outcomes.csv into SQLite (data/release_risk.db)
and executes the core KPI queries:
1. Rollback and alert rate by day_of_week and deploy_hour
2. Mean Time-to-Resolution (MTTR) by incident priority
3. Top 5 riskiest release conditions ranked by instability rate
"""

import os
import sys
import sqlite3
import json
import logging
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = "data/release_risk.db"
PROCESSED_FILE = "data/processed/deployment_outcomes.csv"
OUTPUT_DIR = "output"

def load_to_sqlite(db_path: str = DB_PATH, csv_path: str = PROCESSED_FILE):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Processed dataset not found at: {csv_path}. Run Step 5 first.")
        
    df = pd.read_csv(csv_path)
    
    conn = sqlite3.connect(db_path)
    # Write dataframe to SQLite table
    df.to_sql("deployment_outcomes", conn, if_exists="replace", index=False)
    conn.commit()
    logger.info(f"Loaded {len(df)} rows from {csv_path} into SQLite database: {db_path} (table: deployment_outcomes)")
    return conn

def run_kpi_queries(conn: sqlite3.Connection):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Rollback & Alert Rate by Day of Week & Hour
    q1 = """
    SELECT 
        day_of_week,
        deploy_hour,
        COUNT(*) AS total_deployments,
        SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) AS rollback_count,
        SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) AS alert_count,
        ROUND(100.0 * SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) / COUNT(*), 2) AS rollback_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) / COUNT(*), 2) AS alert_rate_pct,
        ROUND(100.0 * SUM(CASE WHEN outcome != 'stable' THEN 1 ELSE 0 END) / COUNT(*), 2) AS instability_rate_pct
    FROM deployment_outcomes
    GROUP BY day_of_week, deploy_hour
    ORDER BY instability_rate_pct DESC, total_deployments DESC;
    """
    df_temporal_kpi = pd.read_sql_query(q1, conn)
    
    # 2. MTTR by Incident Priority
    q2 = """
    SELECT 
        priority_bucket,
        COUNT(matched_incident_id) AS incident_count,
        ROUND(AVG(time_to_resolution_hours), 2) AS mean_ttr_hours,
        ROUND(MIN(time_to_resolution_hours), 2) AS min_ttr_hours,
        ROUND(MAX(time_to_resolution_hours), 2) AS max_ttr_hours
    FROM deployment_outcomes
    WHERE priority_bucket != 'None / Stable' AND time_to_resolution_hours IS NOT NULL
    GROUP BY priority_bucket
    ORDER BY mean_ttr_hours DESC;
    """
    df_mttr_kpi = pd.read_sql_query(q2, conn)
    
    # 3. Top 5 Riskiest Release Conditions
    q3 = """
    SELECT 
        service,
        environment,
        day_of_week,
        time_bucket,
        COUNT(*) AS total_deployments,
        SUM(is_instability) AS unstable_deployments,
        ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct,
        SUM(has_rollback) AS total_rollbacks
    FROM deployment_outcomes
    GROUP BY service, environment, day_of_week, time_bucket
    ORDER BY instability_rate_pct DESC, total_rollbacks DESC, total_deployments DESC
    LIMIT 5;
    """
    df_top_risks = pd.read_sql_query(q3, conn)
    
    print("\n" + "="*80)
    print("KPI 1: Rollback & Alert Rate by Day and Hour (Top 5 Vulnerable Slots)")
    print("="*80)
    print(df_temporal_kpi.head(5).to_string(index=False))
    
    print("\n" + "="*80)
    print("KPI 2: Mean Time-to-Resolution (MTTR) by Incident Priority")
    print("="*80)
    print(df_mttr_kpi.to_string(index=False))
    
    print("\n" + "="*80)
    print("KPI 3: Top 5 Riskiest Release Conditions Ranked by Instability Rate")
    print("="*80)
    print(df_top_risks.to_string(index=False))
    print("="*80 + "\n")
    
    kpi_results = {
        "temporal_kpi_sample": df_temporal_kpi.head(10).to_dict(orient="records"),
        "mttr_by_priority": df_mttr_kpi.to_dict(orient="records"),
        "top_5_risk_conditions": df_top_risks.to_dict(orient="records")
    }
    
    kpi_file = os.path.join(OUTPUT_DIR, "kpi_summary.json")
    with open(kpi_file, "w", encoding="utf-8") as f:
        json.dump(kpi_results, f, indent=4)
        
    logger.info(f"Saved analytical KPI summary to: {kpi_file}")
    return df_temporal_kpi, df_mttr_kpi, df_top_risks

def run_database_pipeline():
    conn = load_to_sqlite()
    run_kpi_queries(conn)
    conn.close()

if __name__ == "__main__":
    run_database_pipeline()
