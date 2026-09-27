"""
Tests for ReleaseGuard Predictive Risk Model & Simulator Engine
"""

import os
import sys
import pytest
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.predictive_model import train_and_evaluate, simulate_deployment, load_and_prep_data


@pytest.fixture(scope="module")
def trained_model_and_results():
    pipeline, results, X_test, y_test = train_and_evaluate()
    return pipeline, results, X_test, y_test


def test_data_loading_and_features():
    X, y, df = load_and_prep_data()
    assert len(df) > 0, "Dataset should not be empty"
    assert len(X) == len(y), "Features and target length must match"
    assert set(y.unique()).issubset({0, 1}), "Target must be binary 0 or 1"
    assert "service" in X.columns
    assert "environment" in X.columns
    assert "test_pass_rate" in X.columns
    assert "deploy_hour" in X.columns


def test_model_training_and_metrics(trained_model_and_results):
    pipeline, results, X_test, y_test = trained_model_and_results
    assert pipeline is not None
    assert "metrics" in results
    metrics = results["metrics"]
    assert metrics["accuracy"] >= 0.70, "Model accuracy should be at least 70%"
    assert metrics["roc_auc"] >= 0.75, "Model ROC-AUC should be at least 0.75"
    assert "grouped_importances" in results
    assert len(results["grouped_importances"]) > 0


def test_simulate_deployment_output_structure(trained_model_and_results):
    pipeline, _, _, _ = trained_model_and_results
    sim = simulate_deployment(
        pipeline,
        service="auth-service",
        environment="production",
        day_of_week="Saturday",
        deploy_hour=21,
        test_pass_rate=0.88,
        security_finding_count=3,
        lines_changed=800,
    )
    assert "risk_percentage" in sim
    assert 0.0 <= sim["risk_percentage"] <= 100.0, "Risk percentage must be between 0 and 100"
    assert sim["risk_level"] in ["Low Risk", "Elevated Risk", "Critical Risk"]
    assert "recommendation" in sim
    assert "top_contributing_factors" in sim
    assert len(sim["top_contributing_factors"]) == 3, "Must return exactly 3 top contributing factors"


def test_risk_threshold_mapping(trained_model_and_results):
    pipeline, _, _, _ = trained_model_and_results
    
    # Safe test case (Staging, Tuesday afternoon, 99% pass, 0 security findings, small PR)
    safe_sim = simulate_deployment(
        pipeline,
        service="auth-service",
        environment="staging",
        day_of_week="Tuesday",
        deploy_hour=14,
        test_pass_rate=0.99,
        security_finding_count=0,
        lines_changed=120,
    )
    assert safe_sim["risk_percentage"] < 50.0
    assert safe_sim["risk_level"] in ["Low Risk", "Elevated Risk"]

    # High risk test case (Production, Sunday night, low pass rate, multiple CVEs, massive PR)
    risky_sim = simulate_deployment(
        pipeline,
        service="payment-api",
        environment="production",
        day_of_week="Sunday",
        deploy_hour=23,
        test_pass_rate=0.82,
        security_finding_count=5,
        lines_changed=1500,
    )
    assert risky_sim["risk_percentage"] > safe_sim["risk_percentage"], "Risky scenario must have higher risk % than safe scenario"


def test_model_derived_attribution_validity(trained_model_and_results):
    pipeline, _, _, _ = trained_model_and_results
    sim = simulate_deployment(
        pipeline,
        service="cart-service",
        environment="production",
        day_of_week="Friday",
        deploy_hour=19,
        test_pass_rate=0.91,
        security_finding_count=2,
        lines_changed=600,
    )
    for label, delta, explanation in sim["top_contributing_factors"]:
        assert isinstance(label, str) and len(label) > 0
        assert isinstance(delta, (int, float))
        assert isinstance(explanation, str) and len(explanation) > 0
