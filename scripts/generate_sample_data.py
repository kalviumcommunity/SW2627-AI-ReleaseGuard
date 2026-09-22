"""
Sample Dataset Generator for Release Risk Analyzer.
Generates authentic raw datasets in data/raw/:
1. incident_log.csv: Modeled on UCI ServiceNow Incident Management Process Enriched Event Log
2. pipeline_logs.csv: Modeled on AI-driven CI/CD Pipeline execution logs
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_datasets(output_dir="data/raw", num_pipelines=120, num_incidents=250, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    # Base timeline: 30 days of release activity
    base_time = datetime(2026, 8, 1, 8, 0, 0)
    
    # -------------------------------------------------------------
    # 1. Pipeline Logs Generation
    # -------------------------------------------------------------
    services = ["auth-service", "payment-api", "cart-service", "user-profile", "web-frontend", "notification-worker", "inventory-db-migrator"]
    environments = ["production", "staging", "development"]
    users = ["alex_dev", "saanvi_lead", "glory_ops", "jordan_qa", "system_bot", "maya_eng"]
    branches = ["main", "release/v2.1", "feature/auth-refresh", "hotfix/payment-timeout", "main"]
    stages = ["Build", "Unit-Test", "Security-Scan", "Deploy", "Integration-Test"]
    
    pipeline_rows = []
    
    current_time = base_time
    for p_id in range(1001, 1001 + num_pipelines):
        p_str = f"PIPE-{p_id}"
        svc = random.choice(services)
        env = "production" if random.random() < 0.65 else random.choice(["staging", "development"])
        user = random.choice(users)
        branch = random.choice(branches)
        commit = f"c{random.randint(100000, 999999):x}"
        
        # Advance time by random interval (2 to 8 hours)
        current_time += timedelta(minutes=random.randint(120, 480))
        stage_time = current_time
        
        # Pipeline status progression
        failed_early = False
        for stage in stages:
            stage_time += timedelta(minutes=random.randint(2, 15))
            job_name = f"{svc}_{stage.lower()}_{env[:4]}"
            
            if failed_early:
                status = "Skipped"
            else:
                if stage == "Deploy":
                    # ~18% deploy failure or partial degradation in production, higher on Fridays/weekends
                    is_weekend = stage_time.weekday() >= 5
                    is_late = stage_time.hour >= 19 or stage_time.hour < 7
                    fail_prob = 0.30 if (is_weekend or is_late) else 0.12
                    status = "Failed" if (random.random() < fail_prob and env == "production") else "Success"
                else:
                    status = "Failed" if random.random() < 0.05 else "Success"
                
                if status == "Failed":
                    failed_early = True
            
            pipeline_rows.append({
                "pipeline_id": p_str,
                "stage_name": stage,
                "job_name": job_name,
                "status": status,
                "timestamp": stage_time.strftime("%Y-%m-%d %H:%M:%S"),
                "commit_id": commit,
                "branch": branch,
                "user": user,
                "environment": env
            })
            
    df_pipelines = pd.DataFrame(pipeline_rows)
    pipeline_path = os.path.join(output_dir, "pipeline_logs.csv")
    df_pipelines.to_csv(pipeline_path, index=False, encoding="utf-8")
    print(f"Generated {len(df_pipelines)} pipeline log events at: {pipeline_path}")

    # -------------------------------------------------------------
    # 2. ServiceNow Incident Log Generation (UCI Enriched Schema)
    # -------------------------------------------------------------
    # Mapping service domains to ServiceNow Categories & Assignment Groups
    service_to_category = {
        "auth-service": ("Security / Access", "IAM-Ops-Team"),
        "payment-api": ("Finance / Transactions", "Payment-Gateway-Tier3"),
        "cart-service": ("Application / Checkout", "Ecom-Core-Support"),
        "user-profile": ("Database / UserData", "DBA-Team"),
        "web-frontend": ("User Interface", "Frontend-Platform-Team"),
        "notification-worker": ("Messaging / Queue", "Middleware-Ops"),
        "inventory-db-migrator": ("Database / Migration", "Data-Platform-Team")
    }
    
    incident_rows = []
    
    # We will generate some incidents tied close to production deployments (within 2h window)
    deploy_events = df_pipelines[(df_pipelines["stage_name"] == "Deploy") & (df_pipelines["environment"] == "production")].to_dict("records")
    
    inc_counter = 5001
    for dep in deploy_events:
        dep_time = datetime.strptime(dep["timestamp"], "%Y-%m-%d %H:%M:%S")
        svc = dep["job_name"].split("_")[0]
        cat, group = service_to_category.get(svc, ("Application / General", "Global-Service-Desk"))
        
        # High likelihood of incident if deploy failed or on risky hours
        dep_failed = (dep["status"] == "Failed")
        prob_incident = 0.85 if dep_failed else (0.28 if (dep_time.weekday() >= 4 or dep_time.hour >= 18) else 0.08)
        
        if random.random() < prob_incident:
            opened_at = dep_time + timedelta(minutes=random.randint(5, 110))
            duration_hours = random.uniform(0.5, 6.0) if not dep_failed else random.uniform(2.0, 14.0)
            resolved_at = opened_at + timedelta(hours=duration_hours)
            closed_at = resolved_at + timedelta(days=1)
            
            priority = "1 - Critical" if dep_failed else random.choice(["2 - High", "3 - Moderate", "4 - Low"])
            
            # ServiceNow enriched logs frequently contain multiple lifecycle snapshots for same incident_id
            num_snapshots = random.randint(1, 3)
            for s_idx in range(num_snapshots):
                snapshot_time = opened_at + timedelta(minutes=s_idx * 20)
                incident_rows.append({
                    "incident_id": f"INC00{inc_counter}",
                    "opened_at": opened_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "closed_at": closed_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "priority": priority,
                    "category": cat,
                    "reassignment_count": s_idx,
                    "reopen_count": 1 if (random.random() < 0.1 and s_idx > 0) else 0,
                    "assignment_group": group,
                    "sys_updated_at": snapshot_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            inc_counter += 1

    # Also generate independent / background ITSM incidents (unrelated to deployments)
    for _ in range(num_incidents - len(incident_rows)):
        rand_offset = timedelta(days=random.uniform(0, 30), hours=random.uniform(0, 24))
        opened_at = base_time + rand_offset
        resolved_at = opened_at + timedelta(hours=random.uniform(1.0, 8.0))
        closed_at = resolved_at + timedelta(days=2)
        
        svc = random.choice(services)
        cat, group = service_to_category[svc]
        priority = random.choice(["2 - High", "3 - Moderate", "4 - Low", "4 - Low"])
        
        incident_rows.append({
            "incident_id": f"INC00{inc_counter}",
            "opened_at": opened_at.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved_at.strftime("%Y-%m-%d %H:%M:%S"),
            "closed_at": closed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "priority": priority,
            "category": cat,
            "reassignment_count": random.choice([0, 1, 2]),
            "reopen_count": 0,
            "assignment_group": group,
            "sys_updated_at": opened_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        inc_counter += 1

    df_incidents = pd.DataFrame(incident_rows)
    incident_path = os.path.join(output_dir, "incident_log.csv")
    df_incidents.to_csv(incident_path, index=False, encoding="utf-8")
    print(f"Generated {len(df_incidents)} incident event records at: {incident_path}")

if __name__ == "__main__":
    generate_datasets()
