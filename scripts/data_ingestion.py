"""
Step 1: Real Multi-Dataset Ingestion & Dynamic Validation
Loads and validates operational datasets from data/raw/ or dynamic uploader:
- UCI ServiceNow Incident Management Process Enriched Event Log (incident_log.csv)
- Kaggle AI-Driven CI/CD Pipeline Logs (pipeline_logs.csv)
- D2KLab GitHub Actions Workflow Dataset (gha_workflow_runs.csv)

Features:
- Character encoding fallback (utf-8, utf-8-sig, latin1, iso-8859-1, cp1252)
- Flexible schema validation & null inspection
- Comprehensive audit reporting to output/ingestion_audit_report.json
"""

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

EXPECTED_SCHEMAS = {
    "incident_log.csv": [
        "number", "incident_state", "opened_at", "resolved_at", "closed_at",
        "priority", "category", "reassignment_count", "reopen_count", "assignment_group"
    ],
    "pipeline_logs.csv": [
        "pipeline_id", "stage_name", "job_name", "status", "timestamp",
        "commit_id", "branch", "user", "environment"
    ],
    "gha_workflow_runs.csv": [
        "workflow_run_id", "repository", "workflow_name", "event_trigger",
        "status", "conclusion", "created_at", "updated_at", "runner_os"
    ]
}

ENCODING_CANDIDATES = ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252"]

def load_with_encoding_fallback(filepath: str) -> tuple[pd.DataFrame, str]:
    """Attempts to load a CSV file using a prioritized sequence of character encodings."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found at: {filepath}")
    
    last_error = None
    for enc in ENCODING_CANDIDATES:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            logger.info(f"Successfully loaded '{os.path.basename(filepath)}' using encoding: {enc}")
            return df, enc
        except (UnicodeDecodeError, Exception) as e:
            last_error = e
            continue
            
    raise ValueError(f"Failed to read '{filepath}' with any candidate encodings. Error: {last_error}")

def validate_schema(df: pd.DataFrame, dataset_name: str) -> dict:
    """Validates schema columns and inspects dataset health."""
    expected_cols = EXPECTED_SCHEMAS.get(os.path.basename(dataset_name), [])
    present_cols = list(df.columns)
    missing_cols = [col for col in expected_cols if col not in present_cols]
    extra_cols = [col for col in present_cols if col not in expected_cols]
    
    null_counts = df.isnull().sum().to_dict()
    is_valid = len(missing_cols) == 0
    
    return {
        "is_valid": is_valid,
        "expected_columns": expected_cols,
        "present_columns": present_cols,
        "missing_columns": missing_cols,
        "extra_columns": extra_cols,
        "null_counts": {k: int(v) for k, v in null_counts.items()},
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns))
    }

def run_ingestion():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # Check if raw files exist, else populate real datasets
    incident_file = os.path.join(RAW_DIR, "incident_log.csv")
    pipeline_file = os.path.join(RAW_DIR, "pipeline_logs.csv")
    gha_file = os.path.join(RAW_DIR, "gha_workflow_runs.csv")
    
    if not os.path.exists(incident_file) or not os.path.exists(pipeline_file) or not os.path.exists(gha_file):
        logger.info("Operational datasets missing in data/raw/. Initializing real dataset loader...")
        from scripts.populate_real_datasets import populate_datasets
        populate_datasets()

    audit_report = {
        "execution_timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "SUCCESS",
        "datasets": {}
    }
    
    datasets_to_ingest = ["incident_log.csv", "pipeline_logs.csv", "gha_workflow_runs.csv"]
    
    for filename in datasets_to_ingest:
        filepath = os.path.join(RAW_DIR, filename)
        if not os.path.exists(filepath):
            continue
        try:
            df, detected_encoding = load_with_encoding_fallback(filepath)
            validation_result = validate_schema(df, filename)
            file_size_bytes = os.path.getsize(filepath)
            
            audit_report["datasets"][filename] = {
                "file_path": filepath,
                "file_size_bytes": file_size_bytes,
                "encoding_used": detected_encoding,
                "schema_validation": validation_result
            }
            
            if not validation_result["is_valid"]:
                audit_report["status"] = "WARNING_SCHEMA_MISMATCH"
                logger.warning(f"Schema warning in {filename}: Missing columns {validation_result['missing_columns']}")
            else:
                logger.info(f"Schema validation PASSED for {filename} ({validation_result['total_rows']} rows)")
                
        except Exception as e:
            logger.error(f"Error ingesting {filename}: {str(e)}")
            audit_report["status"] = "FAILED"
            audit_report["datasets"][filename] = {"error": str(e)}
            
    report_path = os.path.join(OUTPUT_DIR, "ingestion_audit_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=4)
        
    logger.info(f"Ingestion audit report saved to: {report_path}")
    return audit_report

if __name__ == "__main__":
    run_ingestion()

