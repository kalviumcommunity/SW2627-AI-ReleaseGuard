"""
Step 6: SQLite Storage & Analytical KPI Engine with Clean Data Layer

Loads clean datasets into SQLite (data/release_risk.db), constructs SQL views and
pre-aggregated summary tables, validates database schemas, and executes analytical KPI queries.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("DatabaseKPIs")

DB_PATH = os.path.join(PROJECT_ROOT, "data", "release_risk.db")
PROCESSED_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "deployment_outcomes.csv")
INCIDENTS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "clean_incidents.csv")
PIPELINE_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "clean_deployments.csv")
ROLLBACKS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "clean_rollbacks.csv")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
VIEWS_DIR = os.path.join(PROJECT_ROOT, "database", "views")
AGG_DIR = os.path.join(PROJECT_ROOT, "database", "aggregations")

def load_tables_to_sqlite(db_path: str = DB_PATH):
    """Loads processed CSV datasets into SQLite database tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # 1. Main deployment outcomes table
    if os.path.exists(PROCESSED_FILE):
        df_outcomes = pd.read_csv(PROCESSED_FILE)
        df_outcomes.to_sql("deployment_outcomes", conn, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_outcomes)} rows into 'deployment_outcomes' table")
    else:
        raise FileNotFoundError(f"Processed file missing: {PROCESSED_FILE}")

    # 2. Supporting clean operational tables
    if os.path.exists(INCIDENTS_FILE):
        df_incidents = pd.read_csv(INCIDENTS_FILE)
        df_incidents.to_sql("incidents", conn, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_incidents)} rows into 'incidents' table")

    if os.path.exists(PIPELINE_FILE):
        df_pipeline = pd.read_csv(PIPELINE_FILE)
        df_pipeline.to_sql("pipeline_logs", conn, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_pipeline)} rows into 'pipeline_logs' table")

    if os.path.exists(ROLLBACKS_FILE):
        df_rollbacks = pd.read_csv(ROLLBACKS_FILE)
        df_rollbacks.to_sql("rollbacks", conn, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_rollbacks)} rows into 'rollbacks' table")

    conn.commit()
    return conn

def setup_clean_data_layer(conn: sqlite3.Connection):
    """Creates SQL views and populates pre-aggregated summary tables."""
    cursor = conn.cursor()

    # Drop existing views first to allow schema updates
    cursor.execute("DROP VIEW IF EXISTS vw_active_deployments;")
    cursor.execute("DROP VIEW IF EXISTS vw_risk_by_environment;")
    cursor.execute("DROP VIEW IF EXISTS vw_incident_resolution_metrics;")

    # 1. Execute SQL view files from database/views/
    view_files = [
        "vw_active_deployments.sql",
        "vw_risk_by_environment.sql",
        "vw_incident_resolution_metrics.sql"
    ]
    for view_file in view_files:
        view_path = os.path.join(VIEWS_DIR, view_file)
        if os.path.exists(view_path):
            with open(view_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
                cursor.executescript(sql_content)
                logger.info(f"Executed view SQL script: {view_file}")

    # 2. Execute pre-aggregated table definition from database/aggregations/
    agg_file = os.path.join(AGG_DIR, "agg_daily_release_risk.sql")
    if os.path.exists(agg_file):
        with open(agg_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
            cursor.executescript(sql_content)
            logger.info(f"Executed table aggregation script: agg_daily_release_risk.sql")

    # 3. Populate pre-aggregated summary table agg_daily_release_risk
    populate_agg_query = """
    INSERT OR REPLACE INTO agg_daily_release_risk
    SELECT 
        SUBSTR(deploy_timestamp, 1, 10) AS aggregation_date,
        service,
        environment,
        COUNT(*) AS total_deployments,
        SUM(CASE WHEN outcome = 'stable' THEN 1 ELSE 0 END) AS stable_count,
        SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) AS alert_count,
        SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) AS rollback_count,
        ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct,
        ROUND(AVG(time_to_resolution_hours), 2) AS mean_mttr_hours,
        COUNT(*) AS row_count,
        DATETIME('now') AS updated_at
    FROM deployment_outcomes
    GROUP BY SUBSTR(deploy_timestamp, 1, 10), service, environment;
    """
    cursor.execute(populate_agg_query)
    conn.commit()
    logger.info("Populated pre-aggregated summary table 'agg_daily_release_risk'")

def validate_database_schema(conn: sqlite3.Connection):
    """Validates tables, views, and column schema compliance."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cursor = conn.cursor()

    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view');")
    db_objects = cursor.fetchall()

    schema_audit = {"tables": {}, "views": {}}
    for obj_name, obj_type in db_objects:
        cursor.execute(f"PRAGMA table_info({obj_name});")
        cols = [{"id": row[0], "name": row[1], "type": row[2], "notnull": row[3]} for row in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM {obj_name};")
        count = cursor.fetchone()[0]
        
        target_dict = schema_audit["tables"] if obj_type == "table" else schema_audit["views"]
        target_dict[obj_name] = {
            "row_count": count,
            "column_count": len(cols),
            "columns": cols
        }

    audit_file = os.path.join(OUTPUT_DIR, "database_schema_audit.json")
    with open(audit_file, "w", encoding="utf-8") as f:
        json.dump(schema_audit, f, indent=4)
        
    logger.info(f"Database schema audit saved to: {audit_file}")
    return schema_audit

def run_kpi_queries(conn: sqlite3.Connection):
    """Executes SQL analytical queries using WHERE, GROUP BY, HAVING, ORDER BY."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Query 1: Temporal Instability from vw_active_deployments
    q1 = """
    SELECT 
        day_of_week,
        deploy_hour,
        COUNT(*) AS total_deployments,
        SUM(has_rollback) AS rollback_count,
        SUM(has_alert) AS alert_count,
        ROUND(100.0 * SUM(has_rollback) / COUNT(*), 2) AS rollback_rate_pct,
        ROUND(100.0 * SUM(has_alert) / COUNT(*), 2) AS alert_rate_pct,
        ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct
    FROM vw_active_deployments
    GROUP BY day_of_week, deploy_hour
    HAVING total_deployments >= 2
    ORDER BY instability_rate_pct DESC, total_deployments DESC;
    """
    df_temporal_kpi = pd.read_sql_query(q1, conn)
    
    # Query 2: Environment Risk from vw_risk_by_environment
    q2 = """
    SELECT 
        service,
        environment,
        total_deployments,
        instability_rate_pct,
        rollback_rate_pct,
        mean_mttr_hours
    FROM vw_risk_by_environment
    WHERE total_deployments > 0
    ORDER BY instability_rate_pct DESC;
    """
    df_env_kpi = pd.read_sql_query(q2, conn)
    
    # Query 3: Incident MTTR from vw_incident_resolution_metrics
    q3 = """
    SELECT 
        priority_bucket,
        incident_category,
        incident_count,
        avg_ttr_hours,
        avg_risk_weight
    FROM vw_incident_resolution_metrics
    ORDER BY avg_ttr_hours DESC;
    """
    df_mttr_kpi = pd.read_sql_query(q3, conn)
    
    # Query 4: Daily pre-aggregated metrics from agg_daily_release_risk
    q4 = """
    SELECT 
        aggregation_date,
        service,
        environment,
        total_deployments,
        instability_rate_pct,
        mean_mttr_hours,
        updated_at
    FROM agg_daily_release_risk
    ORDER BY aggregation_date DESC, instability_rate_pct DESC
    LIMIT 10;
    """
    df_daily_agg = pd.read_sql_query(q4, conn)
    
    print("\n" + "="*80)
    print("KPI 1: Temporal Instability Rate (Day & Deploy Hour)")
    print("="*80)
    print(df_temporal_kpi.head(5).to_string(index=False))
    
    print("\n" + "="*80)
    print("KPI 2: Environment Health & Vulnerability Metrics")
    print("="*80)
    print(df_env_kpi.to_string(index=False))
    
    print("\n" + "="*80)
    print("KPI 3: Incident Resolution MTTR by Priority & Group")
    print("="*80)
    print(df_mttr_kpi.to_string(index=False))
    
    print("\n" + "="*80)
    print("KPI 4: Pre-Aggregated Daily Release Risk Summary")
    print("="*80)
    print(df_daily_agg.to_string(index=False))
    print("="*80 + "\n")
    
    kpi_results = {
        "temporal_kpi_sample": df_temporal_kpi.head(10).to_dict(orient="records"),
        "environment_kpi": df_env_kpi.to_dict(orient="records"),
        "mttr_by_priority": df_mttr_kpi.to_dict(orient="records"),
        "daily_pre_aggregated_sample": df_daily_agg.to_dict(orient="records")
    }
    
    kpi_file = os.path.join(OUTPUT_DIR, "kpi_summary.json")
    with open(kpi_file, "w", encoding="utf-8") as f:
        json.dump(kpi_results, f, indent=4)
        
    logger.info(f"Saved analytical KPI summary to: {kpi_file}")
    return df_temporal_kpi, df_env_kpi, df_mttr_kpi, df_daily_agg

def run_database_pipeline():
    conn = load_tables_to_sqlite()
    setup_clean_data_layer(conn)
    validate_database_schema(conn)
    run_kpi_queries(conn)
    conn.close()

if __name__ == "__main__":
    run_database_pipeline()
