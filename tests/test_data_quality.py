"""
Step 8: Automated Data Quality Gate Suite (Pytest)

Validates critical integrity constraints on data/processed/deployment_outcomes.csv:
1. Zero null values in 'outcome' column
2. Zero duplicate 'deployment_id's
3. Valid domain outcome categories: {'stable', 'alerted', 'rolled_back'}
4. Zero null values in primary operational columns (service, deploy_timestamp, environment)
5. Timestamp temporal validity and ranges
6. Clean Data Layer SQL views (vw_active_deployments, vw_risk_by_environment) & agg_daily_release_risk
7. Machine-readable Data Dictionary completeness
"""

import os
import sqlite3
import pytest
import pandas as pd

PROCESSED_FILE = os.path.join("data", "processed", "deployment_outcomes.csv")
DB_PATH = os.path.join("data", "release_risk.db")
DATA_DICT_CSV = os.path.join("docs", "data_dictionary.csv")

@pytest.fixture(scope="module")
def df_outcomes():
    """Fixture to load deployment_outcomes.csv or run pipeline if not found."""
    if not os.path.exists(PROCESSED_FILE):
        # Auto-run pipeline to generate dataset during local test execution
        from scripts.run_pipeline import main as run_p
        run_p()
        
    assert os.path.exists(PROCESSED_FILE), f"Dataset file {PROCESSED_FILE} must exist"
    df = pd.read_csv(PROCESSED_FILE)
    assert len(df) > 0, "Dataset must not be empty"
    return df

def test_file_exists_and_non_empty(df_outcomes):
    """Asserts that the processed outcomes dataset exists and is populated."""
    assert len(df_outcomes) > 0, "deployment_outcomes.csv should contain rows"
    assert "deployment_id" in df_outcomes.columns
    assert "outcome" in df_outcomes.columns

def test_no_null_outcomes(df_outcomes):
    """
    CRITICAL CI CHECK:
    Fails the build if any outcome is null, NaN, or whitespace.
    """
    null_outcomes_count = df_outcomes["outcome"].isnull().sum()
    empty_str_count = (df_outcomes["outcome"].astype(str).str.strip() == "").sum()
    
    assert null_outcomes_count == 0, f"Found {null_outcomes_count} null values in 'outcome' column"
    assert empty_str_count == 0, f"Found {empty_str_count} empty string values in 'outcome' column"

def test_no_duplicate_deployment_ids(df_outcomes):
    """
    CRITICAL CI CHECK:
    Fails the build if deployment_ids are not strictly unique.
    """
    duplicate_count = df_outcomes["deployment_id"].duplicated().sum()
    duplicates = df_outcomes[df_outcomes["deployment_id"].duplicated()]["deployment_id"].tolist()
    
    assert duplicate_count == 0, f"Found {duplicate_count} duplicate deployment_id values: {duplicates}"

def test_valid_outcome_categories(df_outcomes):
    """Asserts that all outcomes belong to the strictly allowed domain enum."""
    allowed_outcomes = {"stable", "alerted", "rolled_back"}
    present_outcomes = set(df_outcomes["outcome"].unique())
    invalid_outcomes = present_outcomes - allowed_outcomes
    
    assert len(invalid_outcomes) == 0, f"Found invalid outcome categories: {invalid_outcomes}"

def test_no_null_critical_fields(df_outcomes):
    """Asserts that essential operational fields have zero nulls."""
    critical_fields = ["deployment_id", "service", "environment", "deploy_timestamp", "deployed_by"]
    for field in critical_fields:
        null_count = df_outcomes[field].isnull().sum()
        assert null_count == 0, f"Critical field '{field}' contains {null_count} null values"

def test_valid_temporal_features(df_outcomes):
    """Asserts that engineered temporal features adhere to valid domain bounds."""
    if "deploy_hour" in df_outcomes.columns:
        assert df_outcomes["deploy_hour"].between(0, 23).all(), "deploy_hour must be between 0 and 23"
    if "is_weekend" in df_outcomes.columns:
        assert set(df_outcomes["is_weekend"].unique()).issubset({0, 1}), "is_weekend must be binary (0 or 1)"

def test_sqlite_database_views_and_aggregations():
    """Validates that clean data layer views and pre-aggregated summary tables exist and are populated."""
    assert os.path.exists(DB_PATH), f"Database file {DB_PATH} must exist"
    conn = sqlite3.connect(DB_PATH)
    
    # Test vw_active_deployments view
    df_active = pd.read_sql_query("SELECT * FROM vw_active_deployments;", conn)
    assert len(df_active) > 0, "vw_active_deployments view must contain rows"
    assert "risk_severity" in df_active.columns
    
    # Test vw_risk_by_environment view
    df_env = pd.read_sql_query("SELECT * FROM vw_risk_by_environment;", conn)
    assert len(df_env) > 0, "vw_risk_by_environment view must contain rows"
    assert "instability_rate_pct" in df_env.columns

    # Test agg_daily_release_risk table
    df_agg = pd.read_sql_query("SELECT * FROM agg_daily_release_risk;", conn)
    assert len(df_agg) > 0, "agg_daily_release_risk pre-aggregated summary table must contain rows"
    assert "aggregation_date" in df_agg.columns
    assert "updated_at" in df_agg.columns
    
    conn.close()

def test_data_dictionary_completeness():
    """Asserts that docs/data_dictionary.csv exists and contains required metadata fields."""
    assert os.path.exists(DATA_DICT_CSV), f"Data dictionary file {DATA_DICT_CSV} must exist"
    df_dict = pd.read_csv(DATA_DICT_CSV)
    assert len(df_dict) >= 15, "Data dictionary must contain entries for all key fields"
    required_cols = {"table_name", "column_name", "data_type", "description", "business_meaning"}
    assert required_cols.issubset(set(df_dict.columns)), f"Data dictionary missing columns: {required_cols - set(df_dict.columns)}"
