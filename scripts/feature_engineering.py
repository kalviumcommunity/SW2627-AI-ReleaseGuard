"""
Step 5: Advanced Domain-Specific Feature Engineering & Risk Scoring

Viva Defense Documentation:
--------------------------
1. Temporal Risk Features:
   - day_of_week / day_of_week_num: Identifies peak change freeze vs release windows.
   - deploy_hour: 24-hour hour index.
   - is_weekend: Binary indicator for Saturday/Sunday releases.
   - is_after_hours: Binary flag for deployments executed before 09:00 or after 18:00 UTC.
   - time_bucket: Human-readable window (Morning, Afternoon, Evening, Night).
   - deploy_quarter: Fiscal quarter index (Q1-Q4).
   - month_sin / month_cos: Cyclical temporal sine/cosine representations.

2. Pipeline & Quality Telemetry Features:
   - job_duration_seconds: Duration of deployment execution.
   - test_pass_rate: Suite pass percentage from unit/integration testing.
   - security_finding_count: Critical/High vulnerabilities detected prior to release.
   - lines_changed: PR change volume size.
   - flaky_test_flag: Binary indicator of non-deterministic test failures.

3. ServiceNow ITSM & Incident Features:
   - priority_bucket / priority_numeric: Standardized P1-P4 incident severity ranks.
   - time_to_resolution_hours: Time elapsed between incident opening and resolution.
   - sla_breach_flag: Indicator whether SLA response/resolution target was violated.
   - escalation_depth: Number of reassignments across engineering tier teams.
   - reopen_risk_score: Penalty score for reopened incident tickets.

4. Composite Risk Index (0-100 Score):
   - Combines deployment timing risk (off-hours penalty), pipeline test quality,
     security posture, SLA breach history, and incident severity weights into a single
     actionable release risk score.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

def bucket_priority(prio_val) -> str:
    """Standardizes priority text into clean severity buckets."""
    if pd.isnull(prio_val) or str(prio_val).strip() in ["", "nan", "None"]:
        return "None / Stable"
    prio_str = str(prio_val).lower()
    if "1" in prio_str or "critical" in prio_str:
        return "Critical (P1)"
    elif "2" in prio_str or "high" in prio_str:
        return "High (P2)"
    elif "3" in prio_str or "moderate" in prio_str or "medium" in prio_str:
        return "Moderate (P3)"
    elif "4" in prio_str or "low" in prio_str:
        return "Low (P4)"
    return "Moderate (P3)"

def get_priority_numeric(prio_str: str) -> int:
    if "P1" in prio_str or "Critical" in prio_str:
        return 1
    elif "P2" in prio_str or "High" in prio_str:
        return 2
    elif "P3" in prio_str or "Moderate" in prio_str:
        return 3
    elif "P4" in prio_str or "Low" in prio_str:
        return 4
    return 5

def get_time_bucket(hour: int) -> str:
    if 6 <= hour < 12:
        return "Morning (06:00-12:00)"
    elif 12 <= hour < 18:
        return "Afternoon (12:00-18:00)"
    elif 18 <= hour < 24:
        return "Evening (18:00-24:00)"
    else:
        return "Night (00:00-06:00)"

def calculate_composite_risk(row) -> float:
    """Calculates a normalized 0-100 Composite Release Risk Score."""
    score = 15.0  # Base risk baseline
    
    # 1. Temporal penalties
    if row.get("is_after_hours", 0) == 1:
        score += 18.0
    if row.get("is_weekend", 0) == 1:
        score += 22.0
        
    # 2. Pipeline quality penalties
    pass_rate = float(row.get("test_pass_rate", 1.0) if pd.notnull(row.get("test_pass_rate")) else 1.0)
    if pass_rate < 0.95:
        score += (0.95 - pass_rate) * 80.0
        
    sec_findings = float(row.get("security_finding_count", 0) if pd.notnull(row.get("security_finding_count")) else 0)
    score += min(sec_findings * 6.0, 24.0)
    
    # 3. Outcome & Incident severity penalties
    outcome = str(row.get("outcome", "stable")).lower()
    if outcome == "rolled_back":
        score += 35.0
    elif outcome == "alerted":
        score += 20.0
        
    prio_num = row.get("priority_numeric", 5)
    if prio_num == 1:
        score += 25.0
    elif prio_num == 2:
        score += 15.0
    elif prio_num == 3:
        score += 8.0
        
    sla_breach = float(row.get("sla_breach_flag", 0))
    if sla_breach == 1:
        score += 12.0
        
    return round(float(np.clip(score, 0.0, 100.0)), 2)

def run_feature_engineering():
    outcomes_path = os.path.join(PROCESSED_DIR, "deployment_outcomes.csv")
    if not os.path.exists(outcomes_path):
        from scripts.join_validation import run_join_validation
        run_join_validation()
        
    df = pd.read_csv(outcomes_path)
    logger.info(f"Loaded {len(df)} deployment outcomes for feature engineering")
    
    # 1. Parse Datetime
    dt_series = pd.to_datetime(df["deploy_timestamp"])
    
    # 2. Derive Temporal Features
    df["day_of_week"] = dt_series.dt.day_name()
    df["day_of_week_num"] = dt_series.dt.dayofweek
    df["deploy_hour"] = dt_series.dt.hour
    df["is_weekend"] = df["day_of_week_num"].apply(lambda x: 1 if x >= 5 else 0)
    df["is_after_hours"] = df["deploy_hour"].apply(lambda h: 1 if (h < 9 or h >= 18) else 0)
    df["time_bucket"] = df["deploy_hour"].apply(get_time_bucket)
    df["deploy_quarter"] = dt_series.dt.quarter.apply(lambda q: f"Q{q}")
    
    # Cyclical Time Encoding
    df["month_sin"] = np.sin(2 * np.pi * dt_series.dt.month / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * dt_series.dt.month / 12.0)
    
    # 3. Derive Severity & ITSM Features
    df["priority_bucket"] = df["incident_priority"].apply(bucket_priority)
    df["priority_numeric"] = df["priority_bucket"].apply(get_priority_numeric)
    df["is_instability"] = df["outcome"].apply(lambda o: 1 if str(o).lower() in ["alerted", "rolled_back"] else 0)
    
    risk_weights = {"stable": 0, "alerted": 1, "rolled_back": 2}
    df["risk_score_weight"] = df["outcome"].apply(lambda o: risk_weights.get(str(o).lower(), 0))
    
    # Time to resolution & SLA features
    if "opened_at" in df.columns and "resolved_at" in df.columns:
        open_dt = pd.to_datetime(df["opened_at"])
        res_dt = pd.to_datetime(df["resolved_at"])
        df["time_to_resolution_hours"] = (res_dt - open_dt).dt.total_seconds() / 3600.0
        df["time_to_resolution_hours"] = df["time_to_resolution_hours"].fillna(0.0).round(2)
    else:
        df["time_to_resolution_hours"] = 0.0
        
    df["sla_breach_flag"] = df.apply(
        lambda r: 1 if (str(r.get("made_sla")).lower() == "false" or r.get("time_to_resolution_hours", 0) > 24.0) else 0,
        axis=1
    )
    
    df["escalation_depth"] = df.get("reassignment_count", pd.Series(0)).fillna(0).astype(int)
    df["reopen_risk_score"] = (df.get("reopen_count", pd.Series(0)).fillna(0) * 2.5 + df["escalation_depth"] * 1.2).round(2)
    
    # 4. Derive Pipeline Telemetry Features (merge if available from raw pipeline logs)
    pipe_path = os.path.join(PROJECT_ROOT, "data", "raw", "pipeline_logs.csv")
    if os.path.exists(pipe_path):
        try:
            df_pipe = pd.read_csv(pipe_path)
            # Group by pipeline_id
            pipe_metrics = df_pipe.groupby("pipeline_id").agg({
                "job_duration_seconds": "sum",
                "test_pass_rate": "mean",
                "security_finding_count": "sum",
                "lines_changed": "max"
            }).reset_index()
            
            df = df.merge(pipe_metrics, on="pipeline_id", how="left")
        except Exception as e:
            logger.warning(f"Could not merge extra pipeline logs metrics: {e}")
            
    # Impute defaults if columns missing
    if "job_duration_seconds" not in df.columns:
        df["job_duration_seconds"] = 300
    if "test_pass_rate" not in df.columns:
        df["test_pass_rate"] = 0.98
    if "security_finding_count" not in df.columns:
        df["security_finding_count"] = 0
    if "lines_changed" not in df.columns:
        df["lines_changed"] = 150
        
    df["flaky_test_flag"] = df["test_pass_rate"].apply(lambda r: 1 if r < 0.92 else 0)
    
    # 5. Derive Composite Release Risk Score
    df["composite_risk_score"] = df.apply(calculate_composite_risk, axis=1)
    
    # 6. Save Enriched Outcome Telemetry
    df.to_csv(outcomes_path, index=False)
    logger.info(f"Successfully added 16 engineered domain features to: {outcomes_path}")
    logger.info(f"Summary: Mean Composite Risk Score = {df['composite_risk_score'].mean():.2f} / 100")
    return df

if __name__ == "__main__":
    run_feature_engineering()
