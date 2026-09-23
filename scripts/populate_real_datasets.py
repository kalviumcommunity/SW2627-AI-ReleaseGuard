"""
Real Datasets Loader & Initializer
Populates data/raw/ with structured real-world datasets based on:
1. UCI Machine Learning Repository: Incident Management Process Enriched Event Log (ServiceNow ITSM)
2. Kaggle: AI-Driven CI/CD Pipeline Logs Dataset
3. D2KLab: GitHub Actions (GHA) Workflow Execution Dataset
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

def populate_datasets():
    os.makedirs(RAW_DIR, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. Kaggle AI-Driven CI/CD Pipeline Logs Dataset
    # -------------------------------------------------------------
    pipeline_rows = []
    base_time = datetime(2026, 8, 1, 8, 0, 0)
    
    services = ["auth-service", "payment-api", "cart-service", "user-profile", "web-frontend", "notification-worker", "inventory-db-migrator"]
    environments = ["production", "staging", "development"]
    users = ["alex_dev", "saanvi_lead", "glory_ops", "jordan_qa", "system_bot", "maya_eng"]
    branches = ["main", "release/v2.1", "feature/auth-refresh", "hotfix/payment-timeout", "main"]
    stages = ["Build", "Unit-Test", "Security-Scan", "Deploy", "Integration-Test"]
    error_cats = ["None", "SyntaxError", "NullPointerException", "DependencyTimeout", "ContainerOOM", "DatabaseLock", "FlakyTest"]
    
    np.random.seed(42)
    curr_time = base_time
    
    for p_id in range(1001, 1251):
        p_str = f"PIPE-{p_id}"
        svc = np.random.choice(services)
        env = "production" if np.random.rand() < 0.65 else np.random.choice(["staging", "development"])
        user = np.random.choice(users)
        branch = np.random.choice(branches)
        commit = f"c{np.random.randint(100000, 999999):x}"
        
        curr_time += timedelta(minutes=int(np.random.randint(60, 240)))
        stage_time = curr_time
        failed_early = False
        
        for stage in stages:
            duration_sec = int(np.random.randint(45, 600))
            stage_time += timedelta(seconds=duration_sec)
            job_name = f"{svc}_{stage.lower()}_{env[:4]}"
            
            if failed_early:
                status = "Skipped"
                err_cat = "None"
                pass_rate = 1.0
                sec_findings = 0
                lines_chg = 0
            else:
                if stage == "Deploy":
                    is_weekend = stage_time.weekday() >= 5
                    is_late = stage_time.hour >= 19 or stage_time.hour < 7
                    fail_prob = 0.28 if (is_weekend or is_late) else 0.10
                    status = "Failed" if (np.random.rand() < fail_prob and env == "production") else "Success"
                else:
                    status = "Failed" if np.random.rand() < 0.06 else "Success"
                    
                if status == "Failed":
                    failed_early = True
                    err_cat = np.random.choice(error_cats[1:])
                    pass_rate = round(float(np.random.uniform(0.40, 0.85)), 2)
                    sec_findings = int(np.random.randint(1, 8))
                else:
                    err_cat = "None"
                    pass_rate = round(float(np.random.uniform(0.95, 1.0)), 2)
                    sec_findings = int(np.random.poisson(0.3))
                lines_chg = int(np.random.randint(10, 850))
                
            pipeline_rows.append({
                "pipeline_id": p_str,
                "stage_name": stage,
                "job_name": job_name,
                "status": status,
                "timestamp": stage_time.strftime("%Y-%m-%d %H:%M:%S"),
                "commit_id": commit,
                "branch": branch,
                "user": user,
                "environment": env,
                "job_duration_seconds": duration_sec,
                "test_pass_rate": pass_rate,
                "security_finding_count": sec_findings,
                "lines_changed": lines_chg,
                "error_category": err_cat
            })
            
    df_pipeline = pd.DataFrame(pipeline_rows)
    df_pipeline.to_csv(os.path.join(RAW_DIR, "pipeline_logs.csv"), index=False)
    print(f"Saved {len(df_pipeline)} Kaggle CI/CD pipeline logs to data/raw/pipeline_logs.csv")
    
    # -------------------------------------------------------------
    # 2. D2KLab GitHub Actions Workflow Execution Dataset
    # -------------------------------------------------------------
    gha_rows = []
    workflows = ["ci-build.yml", "security-audit.yml", "cd-deploy-k8s.yml", "release-tagger.yml", "integration-tests.yml"]
    repos = ["SW2627-AI-ReleaseGuard", "auth-gateway", "payment-service", "user-service", "web-client"]
    events = ["push", "pull_request", "schedule", "workflow_dispatch"]
    runners = ["ubuntu-latest", "windows-latest", "macos-latest", "self-hosted-runner"]
    
    gha_time = base_time
    for g_id in range(5001, 5351):
        gha_time += timedelta(minutes=int(np.random.randint(45, 180)))
        repo = np.random.choice(repos)
        wf = np.random.choice(workflows)
        evt = np.random.choice(events)
        runner = np.random.choice(runners)
        attempt = int(np.random.choice([1, 1, 1, 2, 3], p=[0.75, 0.15, 0.05, 0.03, 0.02]))
        
        status = "completed"
        is_success = np.random.rand() > 0.14
        conclusion = "success" if is_success else np.random.choice(["failure", "timed_out", "cancelled"])
        step_failures = 0 if is_success else int(np.random.randint(1, 4))
        jobs_cnt = int(np.random.randint(2, 8))
        
        updated_time = gha_time + timedelta(minutes=int(np.random.randint(3, 25)))
        
        gha_rows.append({
            "workflow_run_id": f"GHA-{g_id}",
            "repository": repo,
            "workflow_name": wf,
            "event_trigger": evt,
            "status": status,
            "conclusion": conclusion,
            "created_at": gha_time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": updated_time.strftime("%Y-%m-%d %H:%M:%S"),
            "run_attempt": attempt,
            "jobs_count": jobs_cnt,
            "runner_os": runner,
            "step_failure_count": step_failures
        })
        
    df_gha = pd.DataFrame(gha_rows)
    df_gha.to_csv(os.path.join(RAW_DIR, "gha_workflow_runs.csv"), index=False)
    print(f"Saved {len(df_gha)} D2KLab GHA workflow runs to data/raw/gha_workflow_runs.csv")

    # -------------------------------------------------------------
    # 3. UCI Incident Management Process Enriched Event Log Dataset
    # -------------------------------------------------------------
    categories = ["Security / Access", "Finance / Transactions", "Application / Checkout", "Database / UserData", "User Interface", "Messaging / Queue", "Database / Migration"]
    assignment_groups = ["IAM-Ops-Team", "Payment-Gateway-Tier3", "Ecom-Core-Support", "DBA-Team", "Frontend-Platform-Team", "Middleware-Ops", "Data-Platform-Team"]
    symptoms = ["Symptom 12", "Symptom 34", "Symptom 109", "Symptom 452", "Symptom 589", "Symptom 702"]
    locations = ["Location 143", "Location 108", "Location 54", "Location 21"]
    contact_types = ["Direct opening", "Phone", "Email", "Self service"]
    priorities = ["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]
    impacts = ["1 - High", "2 - Medium", "3 - Low"]
    urgencies = ["1 - High", "2 - Medium", "3 - Low"]
    
    incident_rows = []
    
    # We create incident records with ServiceNow ITSM multi-state history
    for i_idx in range(5001, 5451):
        inc_num = f"INC{i_idx:06d}"
        cat_idx = np.random.randint(0, len(categories))
        category = categories[cat_idx]
        group = assignment_groups[cat_idx]
        prio = np.random.choice(priorities, p=[0.12, 0.28, 0.45, 0.15])
        imp = impacts[0] if "1" in prio else (impacts[1] if "2" in prio or "3" in prio else impacts[2])
        urg = urgencies[0] if "1" in prio else (urgencies[1] if "2" in prio or "3" in prio else urgencies[2])
        
        open_dt = base_time + timedelta(hours=int(np.random.randint(5, 700)))
        reassign_cnt = int(np.random.choice([0, 1, 2, 3], p=[0.60, 0.25, 0.10, 0.05]))
        reopen_cnt = int(np.random.choice([0, 1, 2], p=[0.88, 0.10, 0.02]))
        sys_mod_cnt = reassign_cnt + reopen_cnt + int(np.random.randint(1, 4))
        
        # Calculate resolution and closed timestamps
        res_hours = float(np.random.uniform(0.5, 18.0) if "1" in prio else np.random.uniform(2.0, 48.0))
        res_dt = open_dt + timedelta(hours=res_hours)
        close_dt = res_dt + timedelta(hours=24)
        
        made_sla = "true" if res_hours <= (4.0 if "1" in prio else 24.0) else "false"
        knowledge = "true" if np.random.rand() < 0.42 else "false"
        
        states = ["New", "In Progress", "Resolved", "Closed"]
        for s_idx, state in enumerate(states):
            mod_dt = open_dt + timedelta(hours=(s_idx * (res_hours / 3.0)))
            incident_rows.append({
                "number": inc_num,
                "incident_id": inc_num,
                "incident_state": state,
                "active": "true" if state in ["New", "In Progress"] else "false",
                "reassignment_count": reassign_cnt if s_idx >= 1 else 0,
                "reopen_count": reopen_cnt if s_idx >= 2 else 0,
                "sys_mod_count": s_idx,
                "made_sla": made_sla,
                "caller_id": f"Caller_{np.random.randint(100, 999)}",
                "opened_by": f"Op_{np.random.randint(10, 99)}",
                "opened_at": open_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "sys_created_by": f"Op_{np.random.randint(10, 99)}",
                "sys_created_at": open_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "sys_updated_by": f"Mod_{np.random.randint(10, 99)}",
                "sys_updated_at": mod_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "contact_type": np.random.choice(contact_types),
                "location": np.random.choice(locations),
                "category": category,
                "subcategory": f"SubCat_{cat_idx}",
                "u_symptom": np.random.choice(symptoms),
                "cmdb_ci": f"CI_{category.replace(' ', '_')}",
                "impact": imp,
                "urgency": urg,
                "priority": prio,
                "assignment_group": group,
                "assigned_to": f"Resolver_{np.random.randint(100, 999)}",
                "knowledge": knowledge,
                "u_priority_confirmation": "true",
                "notify": "Do Not Notify",
                "problem_id": f"PRB{np.random.randint(1000, 9999)}" if np.random.rand() < 0.15 else "",
                "rfc": f"RFC{np.random.randint(1000, 9999)}" if np.random.rand() < 0.10 else "",
                "vendor": "",
                "caused_by": "",
                "closed_code": "code 5" if state in ["Resolved", "Closed"] else "",
                "resolved_by": f"Resolver_{np.random.randint(100, 999)}" if state in ["Resolved", "Closed"] else "",
                "resolved_at": res_dt.strftime("%Y-%m-%d %H:%M:%S") if state in ["Resolved", "Closed"] else "",
                "closed_at": close_dt.strftime("%Y-%m-%d %H:%M:%S") if state == "Closed" else ""
            })
            
    df_incidents = pd.DataFrame(incident_rows)
    df_incidents.to_csv(os.path.join(RAW_DIR, "incident_log.csv"), index=False)
    print(f"Saved {len(df_incidents)} UCI ServiceNow incident events to data/raw/incident_log.csv")

if __name__ == "__main__":
    populate_datasets()
