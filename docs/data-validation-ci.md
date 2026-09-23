## Overview

Add automated data validation to GitHub Actions so schema-breaking changes are detected immediately.

The workflow should:

```text
Code Push / Pull Request
        ↓
GitHub Actions
        ↓
Run validate_data.py
        ↓
Schema + Type + Quality Checks
        ↓
PASS → Workflow succeeds
FAIL → Workflow fails → Merge blocked
Task 1: Create GitHub Actions Workflow

Create:

.github/workflows/validate.yml

The workflow must run on:

Push to main
Push to develop
Pull requests targeting main

Example:

name: Data Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install pandas

      - run: python validate_data.py data/processed/cleaned_data.csv
Acceptance
Workflow exists under .github/workflows/.
Push events trigger validation.
Pull requests targeting main trigger validation.
Task 2: Create Validation Script

Create:

validate_data.py

The script must validate:

Required Columns
required = [
    "customer_id",
    "order_id",
    "amount",
    "date",
    "segment"
]
Data Types

Verify:

amount is numeric.
Other expected types are validated where applicable.
Minimum Row Count

Require at least 100 rows.

Fully Null Columns

Detect columns containing only null values.

Exit Codes
0 → All checks passed
1 → One or more checks failed

Example structure:

import pandas as pd
import sys

def validate(path):
    df = pd.read_csv(path)
    errors = []

    required = [
        "customer_id",
        "order_id",
        "amount",
        "date",
        "segment"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        errors.append(f"Missing columns: {missing}")
    else:
        print("PASS: Required columns present")

    if "amount" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["amount"]):
            errors.append("amount column is not numeric")
        else:
            print("PASS: amount is numeric")

    if len(df) < 100:
        errors.append(f"Row count {len(df)} below minimum 100")
    else:
        print(f"PASS: Row count {len(df)} meets minimum")

    null_cols = [
        c for c in df.columns
        if df[c].isnull().all()
    ]

    if null_cols:
        errors.append(f"Fully null columns: {null_cols}")
    else:
        print("PASS: No fully null columns")

    if errors:
        print("VALIDATION FAILED:")
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    validate(sys.argv[1])
Task 3: Block Invalid Merges

A failed validation must cause the GitHub Actions job to fail.

Expected Behavior
Invalid schema
     ↓
validate_data.py
     ↓
sys.exit(1)
     ↓
GitHub Actions FAILED
     ↓
Pull Request cannot pass required check
Test
Remove a required column.
Push the change.
Confirm the workflow fails.
Restore the column.
Push again.
Confirm the workflow passes.

To actually enforce merge blocking, configure the repository's branch protection/ruleset so the Data Validation check is required before merging.

Task 4: Clear Validation Logging

Every validation check should produce descriptive output.

Successful Example
PASS: Required columns present
PASS: amount is numeric
PASS: Row count 1250 meets minimum
PASS: No fully null columns
ALL CHECKS PASSED
Failed Example
VALIDATION FAILED:
ERROR: Missing columns: ['segment']
ERROR: Row count 42 below minimum 100
Acceptance

GitHub Actions logs clearly show which checks passed and which failed.

Task 5: Separate Validation Logic

Keep validation logic in Python rather than embedding it in the workflow.

Required Architecture
.github/
└── workflows/
    └── validate.yml

validate_data.py

The workflow should simply execute:

python validate_data.py data/processed/cleaned_data.csv

This allows the same validation script to be run locally and in CI.

Acceptance Criteria
 GitHub Actions workflow created.
 Workflow triggers on push.
 Workflow triggers on pull requests to main.
 Required columns are validated.
 Data types are validated.
 Minimum row count is validated.
 Fully null columns are detected.
 Validation failures return exit code 1.
 Successful validation returns exit code 0.
 Logs clearly show PASS/ERROR results.
 Validation logic is separate from YAML.
 Failed CI check prevents a required-check-protected merge.