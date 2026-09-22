"""
Step 5: Feature Engineering on Deployment Outcomes

Viva Defense Documentation:
--------------------------
1. Temporal Risk Features:
   - day_of_week: Day of the deployment (e.g. 'Friday' deployments are statistically riskier).
   - deploy_hour: 24-hour hour index (helps evaluate off-hours vs core business hours).
   - is_weekend: Binary indicator for Saturday/Sunday releases.
   - is_after_hours: Binary flag for deployments executed before 09:00 or after 18:00 UTC.
   - time_bucket: Human-readable window (Morning, Afternoon, Evening, Night).

2. Severity & Risk Categorization:
   - priority_bucket: Standardized categorical bucketing for ServiceNow incident severities (Critical P1 to Low P4).
   - is_instability: Binary outcome flag (1 for 'alerted' or 'rolled_back', 0 for 'stable').
   - risk_score_weight: Weighted penalty score (Stable=0, Alerted=1, RolledBack=2).
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = "data/processed"

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

def get_time_bucket(hour: int) -> str:
    if 6 <= hour < 12:
        return "Morning (06:00-12:00)"
    elif 12 <= hour < 18:
        return "Afternoon (12:00-18:00)"
    elif 18 <= hour < 24:
        return "Evening (18:00-24:00)"
    else:
        return "Night (00:00-06:00)"

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
    df["day_of_week_num"] = dt_series.dt.dayofweek  # 0=Monday, 6=Sunday
    df["deploy_hour"] = dt_series.dt.hour
    df["is_weekend"] = df["day_of_week_num"].apply(lambda x: 1 if x >= 5 else 0)
    df["is_after_hours"] = df["deploy_hour"].apply(lambda h: 1 if (h < 9 or h >= 18) else 0)
    df["time_bucket"] = df["deploy_hour"].apply(get_time_bucket)
    
    # 3. Derive Severity & Risk Buckets
    df["priority_bucket"] = df["incident_priority"].apply(bucket_priority)
    df["is_instability"] = df["outcome"].apply(lambda o: 1 if str(o).lower() in ["alerted", "rolled_back"] else 0)
    
    risk_weights = {"stable": 0, "alerted": 1, "rolled_back": 2}
    df["risk_score_weight"] = df["outcome"].apply(lambda o: risk_weights.get(str(o).lower(), 0))
    
    # 4. Save Enriched Dataset
    df.to_csv(outcomes_path, index=False)
    logger.info(f"Successfully added 8 engineered features to: {outcomes_path}")
    logger.info(f"Summary: Instability Rate = {(df['is_instability'].mean() * 100):.2f}%")
    return df

if __name__ == "__main__":
    run_feature_engineering()
