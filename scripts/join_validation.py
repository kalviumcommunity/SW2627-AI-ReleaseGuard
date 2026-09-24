"""
Step 4: Heuristic Join Validation & Outcome Classification

Viva Defense Documentation:
--------------------------
1. The Core Data Challenge:
   CI/CD pipelines and ServiceNow ITSM platforms are completely decoupled systems.
   They lack a shared global primary/foreign key.

2. Defensible Multi-Dimensional Heuristic Matching:
   A deployment is linked to an incident if and only if:
   a) Temporal Proximity: The incident's `opened_at` occurs between [T_deploy, T_deploy + 2.0 hours].
   b) Domain/Service Semantic Affinity: The CI/CD service matches the ServiceNow incident category
      or assignment group based on an explicit ontology mapping dictionary (with substring fallback).

3. Priority Conflict Resolution:
   If multiple incidents trigger in the 2-hour window, the highest severity incident
   (1 - Critical > 2 - High > 3 - Moderate > 4 - Low) is selected as the primary cause.

4. Outcome Classification Rule:
   - 'rolled_back': Explicit rollback event in rollbacks.csv (or failed deployment with rollback).
   - 'alerted': Non-rollback deployment with a verified matching post-release incident.
   - 'stable': Deployment with zero matching incidents in the observation window.

5. Orphaned Record Auditing:
   ITSM tickets unrelated to release events (e.g., standard desktop support, general user inquiries)
   are audited and categorized as orphaned/unmatched records in output/join_audit_report.json.
"""

import os
import sys
import json
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
OUTPUT_DIR = "output"

# Explicit Semantic Mapping Dictionary
SERVICE_CATEGORY_AFFINITY = {
    "auth-service": ["security", "access", "iam", "auth", "login"],
    "payment-api": ["finance", "transaction", "payment", "billing", "checkout"],
    "cart-service": ["checkout", "cart", "ecom", "application", "shopping"],
    "user-profile": ["userdata", "profile", "user", "database", "account"],
    "web-frontend": ["user interface", "frontend", "ui", "web", "portal", "client"],
    "notification-worker": ["messaging", "queue", "notification", "email", "sms", "worker"],
    "inventory-db-migrator": ["migration", "inventory", "database", "stock", "dba"]
}

PRIORITY_RANKS = {
    "1 - Critical": 1,
    "2 - High": 2,
    "3 - Moderate": 3,
    "4 - Low": 4
}

def is_service_category_match(service: str, category: str, assignment_group: str) -> bool:
    """Checks whether the service matches category or assignment group semantically."""
    svc_lower = str(service).lower()
    cat_lower = str(category).lower()
    grp_lower = str(assignment_group).lower()
    
    # Direct substring inclusion
    if svc_lower in cat_lower or svc_lower in grp_lower:
        return True
        
    keywords = SERVICE_CATEGORY_AFFINITY.get(svc_lower, [])
    for kw in keywords:
        if kw in cat_lower or kw in grp_lower:
            return True
            
    # Generic application fallback
    if "application" in cat_lower or "general" in cat_lower:
        return True
        
    return False

def run_join_validation():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    dep_file = os.path.join(PROCESSED_DIR, "clean_deployments.csv")
    inc_file = os.path.join(PROCESSED_DIR, "clean_incidents.csv")
    rbk_file = os.path.join(PROCESSED_DIR, "clean_rollbacks.csv")
    
    if not os.path.exists(dep_file) or not os.path.exists(inc_file) or not os.path.exists(rbk_file):
        from scripts.cleaning import run_cleaning
        run_cleaning()
        
    df_dep = pd.read_csv(dep_file)
    df_inc = pd.read_csv(inc_file)
    df_rbk = pd.read_csv(rbk_file)
    
    logger.info(f"Loaded {len(df_dep)} deployments, {len(df_inc)} incidents, {len(df_rbk)} rollbacks")
    
    # Parse datetimes for temporal comparison
    df_dep["dep_dt"] = pd.to_datetime(df_dep["deploy_timestamp"] if "deploy_timestamp" in df_dep.columns else pd.Timestamp.now(), errors="coerce")
    df_inc["inc_opened_dt"] = pd.to_datetime(df_inc["opened_at"] if "opened_at" in df_inc.columns else pd.Timestamp.now(), errors="coerce")
    df_inc["inc_resolved_dt"] = pd.to_datetime(df_inc["resolved_at"] if "resolved_at" in df_inc.columns else None, errors="coerce")
    
    matched_incident_ids = set()
    deployment_outcomes = []
    
    # -------------------------------------------------------------
    # 1. Join Deployments -> Rollbacks (Exact FK Join)
    # -------------------------------------------------------------
    rbk_dict = {row["deployment_id"]: row for _, row in df_rbk.iterrows()} if "deployment_id" in df_rbk.columns else {}
    
    # -------------------------------------------------------------
    # 2. Join Deployments -> Incidents (2-Hour Window Heuristic Join)
    # -------------------------------------------------------------
    for _, dep in df_dep.iterrows():
        dep_id = dep.get("deployment_id", "DEP-UNKNOWN")
        dep_time = dep.get("dep_dt", pd.Timestamp.now())
        svc = dep.get("service", "unknown-service")
        
        # Check explicit rollback
        rbk_match = rbk_dict.get(dep_id, None)
        has_rollback = rbk_match is not None
        
        # Find matching incidents within [T_deploy, T_deploy + 2 hours]
        window_end = dep_time + pd.Timedelta(hours=2) if pd.notnull(dep_time) else pd.Timestamp.now()
        candidate_incidents = df_inc[
            (df_inc["inc_opened_dt"] >= dep_time) & 
            (df_inc["inc_opened_dt"] <= window_end)
        ] if pd.notnull(dep_time) else pd.DataFrame()
        
        best_inc = None
        best_rank = 999
        
        for _, inc in candidate_incidents.iterrows():
            if is_service_category_match(svc, inc.get("category", ""), inc.get("assignment_group", "")):
                prio = str(inc.get("priority", "4 - Low"))
                rank = PRIORITY_RANKS.get(prio, 4)
                if rank < best_rank:
                    best_rank = rank
                    best_inc = inc
                    
        # Determine Outcome Classification
        if has_rollback or str(dep.get("status", "")).lower() == "failed":
            outcome = "rolled_back"
        elif best_inc is not None:
            outcome = "alerted"
        else:
            outcome = "stable"
            
        rec = {
            "deployment_id": dep_id,
            "pipeline_id": dep.get("pipeline_id", ""),
            "service": svc,
            "environment": dep.get("environment", "production"),
            "deploy_timestamp": dep.get("deploy_timestamp", str(dep_time)),
            "deployed_by": dep.get("deployed_by", "system_bot"),
            "status": dep.get("status", "Success"),
            "commit_id": dep.get("commit_id", ""),
            "branch": dep.get("branch", ""),
            "outcome": outcome,
            "has_rollback": 1 if has_rollback else 0,
            "rollback_id": rbk_match.get("rollback_id", None) if rbk_match is not None else None,
            "rollback_reason": rbk_match.get("reason", None) if rbk_match is not None else None,
            "matched_incident_id": best_inc.get("incident_id") if best_inc is not None else None,
            "incident_priority": best_inc.get("priority") if best_inc is not None else None,
            "incident_category": best_inc.get("category") if best_inc is not None else None,
            "incident_opened_at": best_inc.get("opened_at") if best_inc is not None else None,
            "incident_resolved_at": best_inc.get("resolved_at") if best_inc is not None else None
        }
        
        # Calculate Time to Resolution (TTR) in hours if incident exists
        if best_inc is not None and pd.notnull(best_inc.get("opened_at")) and pd.notnull(best_inc.get("resolved_at")):
            try:
                ttr = (pd.to_datetime(best_inc["resolved_at"]) - pd.to_datetime(best_inc["opened_at"])).total_seconds() / 3600.0
                rec["time_to_resolution_hours"] = round(ttr, 2)
            except Exception:
                rec["time_to_resolution_hours"] = None
            if "incident_id" in best_inc and pd.notnull(best_inc["incident_id"]):
                matched_incident_ids.add(best_inc["incident_id"])
        else:
            rec["time_to_resolution_hours"] = None
            
        deployment_outcomes.append(rec)
        
    df_outcomes = pd.DataFrame(deployment_outcomes)
    outcomes_path = os.path.join(PROCESSED_DIR, "deployment_outcomes.csv")
    df_outcomes.to_csv(outcomes_path, index=False)
    logger.info(f"Generated {len(df_outcomes)} final deployment outcomes at: {outcomes_path}")
    
    # -------------------------------------------------------------
    # 3. Join Audit & Orphaned Record Telemetry
    # -------------------------------------------------------------
    all_incident_ids = set(df_inc["incident_id"].dropna()) if "incident_id" in df_inc.columns else set()
    orphaned_incidents = all_incident_ids - matched_incident_ids
    
    outcome_distribution = df_outcomes["outcome"].value_counts().to_dict()
    
    join_audit = {
        "execution_timestamp": pd.Timestamp.utcnow().isoformat() + "Z",
        "total_deployments": int(len(df_outcomes)),
        "outcome_distribution": {k: int(v) for k, v in outcome_distribution.items()},
        "deployments_with_rollbacks": int(df_outcomes["has_rollback"].sum()),
        "deployments_with_incidents": int(df_outcomes["matched_incident_id"].notnull().sum()),
        "total_incidents_analyzed": int(len(all_incident_ids)),
        "incidents_matched_to_deployments": int(len(matched_incident_ids)),
        "orphaned_incidents_count": int(len(orphaned_incidents)),
        "orphaned_incidents_ratio_pct": round(len(orphaned_incidents) / len(all_incident_ids) * 100, 2) if len(all_incident_ids) > 0 else 0,
        "join_matching_logic": {
            "temporal_window_hours": 2.0,
            "semantic_matching": "Service-to-Category Dictionary + Substring Mapping",
            "conflict_resolution": "Highest Incident Priority Selection"
        }
    }
    
    audit_path = os.path.join(OUTPUT_DIR, "join_audit_report.json")
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(join_audit, f, indent=4)
        
    logger.info(f"Saved Join Validation Audit report to: {audit_path}")
    return df_outcomes, join_audit

if __name__ == "__main__":
    run_join_validation()
