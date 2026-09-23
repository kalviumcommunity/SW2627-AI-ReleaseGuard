"""
Automated Data Validation Script for ReleaseGuard CI/CD Pipeline
Verifies required columns, numeric data types, minimum row counts, null columns, and integrity constraints.
Exits with 0 on PASS, 1 on FAIL.
"""

import sys
import os
import pandas as pd

def validate_dataset(filepath):
    print(f"Running ReleaseGuard Data Integrity Check on: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"ERROR: Target file '{filepath}' does not exist.")
        sys.exit(1)
        
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"ERROR: Failed to read CSV file: {e}")
        sys.exit(1)
        
    errors = []
    
    # 1. Required Columns Check
    required_columns = [
        "deployment_id",
        "service",
        "environment",
        "deploy_timestamp",
        "outcome",
        "composite_risk_score"
    ]
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    else:
        print("PASS: Required schema columns present")
        
    # 2. Data Types Validation
    if "composite_risk_score" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["composite_risk_score"]):
            errors.append("'composite_risk_score' column is not numeric")
        else:
            print("PASS: 'composite_risk_score' is numeric")
            
    # 3. Minimum Row Count
    min_rows = 100
    if len(df) < min_rows:
        errors.append(f"Row count {len(df)} is below required minimum of {min_rows}")
    else:
        print(f"PASS: Dataset row count {len(df):,} meets minimum requirement ({min_rows})")
        
    # 4. Fully Null Columns Detection
    null_cols = [c for c in df.columns if df[c].isnull().all()]
    if null_cols:
        errors.append(f"Found 100% fully null columns: {null_cols}")
    else:
        print("PASS: No fully null columns detected")
        
    # 5. Domain Enum Outcome Check
    if "outcome" in df.columns:
        allowed = {"stable", "alerted", "rolled_back"}
        invalid = set(df["outcome"].dropna().unique()) - allowed
        if invalid:
            errors.append(f"Found invalid outcome values: {invalid}")
        else:
            print("PASS: All outcomes conform to allowed domain enum ('stable', 'alerted', 'rolled_back')")
            
    # 6. Primary Key Uniqueness
    if "deployment_id" in df.columns:
        dups = df["deployment_id"].duplicated().sum()
        if dups > 0:
            errors.append(f"Found {dups} duplicate deployment_ids")
        else:
            print("PASS: All deployment_ids are strictly unique")
            
    if errors:
        print("\nVALIDATION FAILED:")
        for error in errors:
            print(f"   ERROR: {error}")
        sys.exit(1)
        
    print("\nALL CHECKS PASSED SUCCESSFULLY")
    sys.exit(0)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "processed", "deployment_outcomes.csv")
    validate_dataset(path)
