"""
End-to-End Release Risk Analyzer Pipeline Orchestrator
Executes Steps 1 to 6 sequentially with audit checkpoints.
"""

import os
import sys
import logging
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("ReleaseRiskPipeline")

def main():
    start_time = datetime.now()
    logger.info("Starting Release Risk Analyzer Data Engineering Pipeline...")

    try:
        # Step 1: Real Data Ingestion
        logger.info(">>> Step 1: Real Data Ingestion & Schema Validation")
        from scripts.data_ingestion import run_ingestion
        run_ingestion()

        # Step 2: Deployment Derivation & Synthetic Rollback Generation
        logger.info(">>> Step 2: Derive Deployments & Model Synthetic Rollbacks")
        from scripts.derive_deployments import run_derive_deployments
        run_derive_deployments()

        # Step 3: Cleaning & Deduplication
        logger.info(">>> Step 3: Timestamp Standardization, Null Handling & Deduplication")
        from scripts.cleaning import run_cleaning
        run_cleaning()

        # Step 4: Join Validation & Outcome Labeling
        logger.info(">>> Step 4: Heuristic 2-Hour Temporal & Service Join Validation")
        from scripts.join_validation import run_join_validation
        run_join_validation()

        # Step 5: Feature Engineering
        logger.info(">>> Step 5: Temporal & Severity Risk Feature Engineering")
        from scripts.feature_engineering import run_feature_engineering
        run_feature_engineering()

        # Step 6: SQLite Ingestion & Analytical KPI Queries
        logger.info(">>> Step 6: SQLite Loading & Analytical KPI Execution")
        from scripts.database_kpis import run_database_pipeline
        run_database_pipeline()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Pipeline finished successfully in {elapsed:.2f} seconds!")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
