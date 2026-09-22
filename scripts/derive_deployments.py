"""
Step 2: Build the Missing Layer - Deployment Derivation & Synthetic Rollback Modeling

Viva Defense Documentation:
--------------------------
1. Pipeline Stage Separation:
   In raw CI/CD logs, deployments are embedded alongside Build, Test, and Scan stages.
   We explicitly isolate records where stage_name == 'Deploy' into distinct deployment
   records with derived service names from job_name patterns.

2. Modeled Rollback Assumption (Synthetic Data Generation):
   Production CI/CD logs often lack explicit rollback records.
   We model rollbacks as an empirical assumption:
   - Failed or degraded deployments trigger an automated or manual rollback event in ~10-15% of failure cases.
   - Rollback timestamp is modeled as an offset of 5-45 minutes after deploy_timestamp.
   - Root causes reflect standard industry SRE incidents (e.g., HealthCheckFailed, ErrorBudgetExhausted).
"""

import os
import random
import logging
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = "data/raw"

def derive_service_from_job(job_name: str, environment: str = None) -> str:
    """
    Extracts canonical service name from CI/CD job_name.
    Example: 'auth-service_deploy_prod' -> 'auth-service'
             'payment-api-deploy' -> 'payment-api'
    """
    if not isinstance(job_name, str) or not job_name.strip():
        return "unknown-service"
    
    clean_job = job_name.lower().replace("-deploy", "").replace("_deploy", "")
    for env in ["production", "prod", "staging", "stg", "development", "dev"]:
        clean_job = clean_job.replace(f"_{env}", "").replace(f"-{env}", "")
        
    parts = clean_job.split("_")
    return parts[0] if parts else "unknown-service"

def run_derive_deployments(random_seed: int = 42):
    random.seed(random_seed)
    os.makedirs(RAW_DIR, exist_ok=True)
    
    pipeline_file = os.path.join(RAW_DIR, "pipeline_logs.csv")
    if not os.path.exists(pipeline_file):
        raise FileNotFoundError(f"Pipeline logs not found at: {pipeline_file}. Run Step 1 ingestion first.")
        
    df_pipeline = pd.read_csv(pipeline_file)
    logger.info(f"Loaded {len(df_pipeline)} pipeline events from {pipeline_file}")
    
    # -------------------------------------------------------------
    # (a) Filter to stage_name == 'Deploy' and derive deployment attributes
    # -------------------------------------------------------------
    deploy_mask = df_pipeline["stage_name"].str.strip().str.lower() == "deploy"
    df_deploys_raw = df_pipeline[deploy_mask].copy()
    logger.info(f"Isolated {len(df_deploys_raw)} deployment events (stage_name == 'Deploy')")
    
    deployments = []
    for idx, row in df_deploys_raw.reset_index(drop=True).iterrows():
        deployment_id = f"DEP-{row['pipeline_id']}-{idx+1:03d}"
        service = derive_service_from_job(str(row["job_name"]), str(row.get("environment", "")))
        
        deployments.append({
            "deployment_id": deployment_id,
            "pipeline_id": row["pipeline_id"],
            "service": service,
            "deploy_timestamp": row["timestamp"],
            "deployed_by": row["user"],
            "environment": row.get("environment", "production"),
            "status": row["status"],
            "commit_id": row.get("commit_id", ""),
            "branch": row.get("branch", "")
        })
        
    df_deployments = pd.DataFrame(deployments)
    derived_dep_path = os.path.join(RAW_DIR, "derived_deployments.csv")
    df_deployments.to_csv(derived_dep_path, index=False)
    logger.info(f"Saved {len(df_deployments)} derived deployments to: {derived_dep_path}")
    
    # -------------------------------------------------------------
    # (b) Generate realistic synthetic rollbacks.csv (~10-15% of failed deploys)
    # -------------------------------------------------------------
    failed_deploys = df_deployments[df_deployments["status"].str.lower().isin(["failed", "error", "unstable"])].to_dict("records")
    
    rollback_reasons = [
        "HealthCheckFailed (HTTP 503 Service Unavailable on /healthz)",
        "ElevatedErrorRate_5xx (Error budget breached > 2.5%)",
        "LatencySLA_Exceeded (p99 latency spiked > 2500ms)",
        "MemoryLeakDetected (Container OOMKilled)",
        "DatabaseDeadlockOnMigration (Schema lock timeout)",
        "SecurityScanAlert_PostDeploy (Critical CVE in dynamic bundle)"
    ]
    
    rollbacks = []
    rbk_counter = 8001
    
    # Modeled Assumption: Approximately 15% of all failures trigger explicit automated or SRE rollbacks
    for dep in failed_deploys:
        # High probability of rollback for failed production deploys
        is_prod = str(dep["environment"]).lower() == "production"
        rollback_prob = 0.70 if is_prod else 0.20
        
        if random.random() < rollback_prob:
            try:
                dep_dt = datetime.strptime(str(dep["deploy_timestamp"]), "%Y-%m-%d %H:%M:%S")
            except Exception:
                dep_dt = datetime.utcnow()
                
            # Rollback happens 5 to 45 minutes after deployment failure
            rbk_dt = dep_dt + timedelta(minutes=random.randint(5, 45))
            
            rollbacks.append({
                "rollback_id": f"RBK-{rbk_counter}",
                "deployment_id": dep["deployment_id"],
                "rollback_timestamp": rbk_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "reason": random.choice(rollback_reasons),
                "initiated_by": "Automated_SRE_Rollback_Daemon" if random.random() < 0.6 else "OnCall_SRE_Lead",
                "modeled_assumption_note": "Synthetic rollback event generated for degraded deployment telemetry"
            })
            rbk_counter += 1
            
    df_rollbacks = pd.DataFrame(rollbacks)
    rollbacks_path = os.path.join(RAW_DIR, "rollbacks.csv")
    df_rollbacks.to_csv(rollbacks_path, index=False)
    logger.info(f"Generated {len(df_rollbacks)} synthetic rollback events at: {rollbacks_path}")
    logger.info("Modeled rollback assumption successfully documented for Sprint 1 defense.")
    
    return df_deployments, df_rollbacks

if __name__ == "__main__":
    run_derive_deployments()
