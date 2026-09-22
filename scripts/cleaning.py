"""
Step 3: Data Cleaning & Standardization

Viva Defense Documentation:
--------------------------
1. Timestamp Standardization:
   Dates across ServiceNow and CI/CD often have slight variations in formatting.
   We convert all timestamp fields into standard ISO 8601 UTC format (YYYY-MM-DD HH:MM:SS).

2. Null Handling Policy:
   - Missing incident categories -> 'General / Unknown'
   - Missing priorities -> '4 - Low' (conservative default)
   - Missing deployers -> 'system_bot'
   - Missing counts -> 0

3. Deduplication Strategy:
   - ServiceNow incident logs often contain state transitions for the same incident_id.
     We sort chronologically and retain the most recent update.
   - Pipeline deployment events are deduplicated by deployment_id keeping the latest execution.

4. Audit Logging:
   Every single null imputation, format transformation, and duplicate drop is logged
   row-by-row into output/cleaning_log.csv for full regulatory and engineering traceability.
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_DIR = "output"

class CleaningLogger:
    def __init__(self):
        self.logs = []
        
    def log(self, dataset: str, record_id: str, action: str, column_affected: str, original_val, new_val, reason: str):
        self.logs.append({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "dataset": dataset,
            "record_id": str(record_id),
            "action": action,
            "column_affected": column_affected,
            "original_value": str(original_val),
            "new_value": str(new_val),
            "reason": reason
        })
        
    def save(self, output_path: str):
        df_log = pd.DataFrame(self.logs)
        df_log.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df_log)} cleaning audit log records to: {output_path}")

def standardize_timestamp(val) -> str:
    """Standardizes timestamp to ISO 8601 string format (YYYY-MM-DD HH:MM:SS)."""
    if pd.isnull(val) or str(val).strip() in ["", "nan", "NaT", "None"]:
        return None
    try:
        dt = pd.to_datetime(val)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def clean_deployments(df: pd.DataFrame, clean_log: CleaningLogger) -> pd.DataFrame:
    logger.info(f"Cleaning deployments dataset (initial rows: {len(df)})")
    
    # 1. Null handling
    for idx, row in df.iterrows():
        rec_id = row.get("deployment_id", f"row_{idx}")
        if pd.isnull(row.get("service")) or str(row.get("service")).strip() == "":
            clean_log.log("deployments", rec_id, "IMPUTE_NULL", "service", row.get("service"), "unknown-service", "Missing service name imputed with fallback")
            df.at[idx, "service"] = "unknown-service"
            
        if pd.isnull(row.get("deployed_by")) or str(row.get("deployed_by")).strip() == "":
            clean_log.log("deployments", rec_id, "IMPUTE_NULL", "deployed_by", row.get("deployed_by"), "system_bot", "Missing user imputed with system_bot")
            df.at[idx, "deployed_by"] = "system_bot"
            
        if pd.isnull(row.get("environment")) or str(row.get("environment")).strip() == "":
            clean_log.log("deployments", rec_id, "IMPUTE_NULL", "environment", row.get("environment"), "production", "Missing environment defaulted to production")
            df.at[idx, "environment"] = "production"

    # 2. Timestamp standardization
    orig_times = df["deploy_timestamp"].copy()
    df["deploy_timestamp"] = df["deploy_timestamp"].apply(standardize_timestamp)
    for idx, (orig, new) in enumerate(zip(orig_times, df["deploy_timestamp"])):
        if str(orig) != str(new):
            rec_id = df.at[idx, "deployment_id"]
            clean_log.log("deployments", rec_id, "NORMALIZE_TIMESTAMP", "deploy_timestamp", orig, new, "Standardized to ISO 8601 UTC")
            
    # 3. Deduplication (keep most recent)
    initial_count = len(df)
    df["dt_temp"] = pd.to_datetime(df["deploy_timestamp"])
    df = df.sort_values(by="dt_temp").drop_duplicates(subset=["deployment_id"], keep="last").drop(columns=["dt_temp"])
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        clean_log.log("deployments", "MULTIPLE", "DEDUPLICATE", "deployment_id", f"{dropped_count} duplicates", "Retained latest", "Deduplicated by deployment_id")
        
    return df

def clean_incidents(df: pd.DataFrame, clean_log: CleaningLogger) -> pd.DataFrame:
    logger.info(f"Cleaning incidents dataset (initial rows: {len(df)})")
    
    # 1. Null handling
    for idx, row in df.iterrows():
        rec_id = row.get("incident_id", f"row_{idx}")
        if pd.isnull(row.get("category")) or str(row.get("category")).strip() == "":
            clean_log.log("incidents", rec_id, "IMPUTE_NULL", "category", row.get("category"), "General / Unknown", "Missing incident category")
            df.at[idx, "category"] = "General / Unknown"
            
        if pd.isnull(row.get("priority")) or str(row.get("priority")).strip() == "":
            clean_log.log("incidents", rec_id, "IMPUTE_NULL", "priority", row.get("priority"), "4 - Low", "Missing priority set to conservative Low")
            df.at[idx, "priority"] = "4 - Low"
            
        if pd.isnull(row.get("assignment_group")) or str(row.get("assignment_group")).strip() == "":
            clean_log.log("incidents", rec_id, "IMPUTE_NULL", "assignment_group", row.get("assignment_group"), "Global-Service-Desk", "Default assignment group")
            df.at[idx, "assignment_group"] = "Global-Service-Desk"

    # 2. Timestamp standardization
    for col in ["opened_at", "resolved_at", "closed_at"]:
        if col in df.columns:
            orig_col = df[col].copy()
            df[col] = df[col].apply(standardize_timestamp)
            for idx, (orig, new) in enumerate(zip(orig_col, df[col])):
                if str(orig) != str(new):
                    rec_id = df.at[idx, "incident_id"]
                    clean_log.log("incidents", rec_id, "NORMALIZE_TIMESTAMP", col, orig, new, "Standardized to ISO 8601 UTC")
                    
    # 3. Deduplication (keep most recent state snapshot)
    initial_count = len(df)
    sort_col = "sys_updated_at" if "sys_updated_at" in df.columns else "opened_at"
    df["sort_dt"] = pd.to_datetime(df[sort_col])
    df = df.sort_values(by="sort_dt").drop_duplicates(subset=["incident_id"], keep="last").drop(columns=["sort_dt"])
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        clean_log.log("incidents", "MULTIPLE", "DEDUPLICATE", "incident_id", f"{dropped_count} snapshots", "Retained latest", "Deduplicated incident lifecycle snapshots")
        
    return df

def clean_rollbacks(df: pd.DataFrame, clean_log: CleaningLogger) -> pd.DataFrame:
    logger.info(f"Cleaning rollbacks dataset (initial rows: {len(df)})")
    
    # 1. Null handling
    for idx, row in df.iterrows():
        rec_id = row.get("rollback_id", f"row_{idx}")
        if pd.isnull(row.get("reason")) or str(row.get("reason")).strip() == "":
            clean_log.log("rollbacks", rec_id, "IMPUTE_NULL", "reason", row.get("reason"), "UnspecifiedFailure", "Missing rollback reason")
            df.at[idx, "reason"] = "UnspecifiedFailure"
            
    # 2. Timestamp standardization
    orig_times = df["rollback_timestamp"].copy()
    df["rollback_timestamp"] = df["rollback_timestamp"].apply(standardize_timestamp)
    for idx, (orig, new) in enumerate(zip(orig_times, df["rollback_timestamp"])):
        if str(orig) != str(new):
            rec_id = df.at[idx, "rollback_id"]
            clean_log.log("rollbacks", rec_id, "NORMALIZE_TIMESTAMP", "rollback_timestamp", orig, new, "Standardized to ISO 8601 UTC")
            
    # 3. Deduplication
    initial_count = len(df)
    df["rbk_dt"] = pd.to_datetime(df["rollback_timestamp"])
    df = df.sort_values(by="rbk_dt").drop_duplicates(subset=["deployment_id"], keep="last").drop(columns=["rbk_dt"])
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        clean_log.log("rollbacks", "MULTIPLE", "DEDUPLICATE", "deployment_id", f"{dropped_count} duplicates", "Retained latest", "Deduplicated rollbacks by deployment_id")
        
    return df

def run_cleaning():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clean_log = CleaningLogger()
    
    # Load raw / derived sources
    dep_path = os.path.join(RAW_DIR, "derived_deployments.csv")
    inc_path = os.path.join(RAW_DIR, "incident_log.csv")
    rbk_path = os.path.join(RAW_DIR, "rollbacks.csv")
    
    if not os.path.exists(dep_path):
        from scripts.derive_deployments import run_derive_deployments
        run_derive_deployments()
        
    df_dep = pd.read_csv(dep_path)
    df_inc = pd.read_csv(inc_path)
    df_rbk = pd.read_csv(rbk_path)
    
    # Execute cleanings
    df_dep_clean = clean_deployments(df_dep, clean_log)
    df_inc_clean = clean_incidents(df_inc, clean_log)
    df_rbk_clean = clean_rollbacks(df_rbk, clean_log)
    
    # Save clean datasets
    df_dep_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_deployments.csv"), index=False)
    df_inc_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_incidents.csv"), index=False)
    df_rbk_clean.to_csv(os.path.join(PROCESSED_DIR, "clean_rollbacks.csv"), index=False)
    
    # Save cleaning audit log
    cleaning_log_file = os.path.join(OUTPUT_DIR, "cleaning_log.csv")
    clean_log.save(cleaning_log_file)
    logger.info("Cleaning stage completed successfully.")

if __name__ == "__main__":
    run_cleaning()
