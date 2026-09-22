-- View: vw_active_deployments
-- Purpose: Provide a clean, standardized active deployment view with risk indicators over the operational timeline.
-- Used by: Release Risk Dashboard, Deployment Monitoring, CI/CD Audit.

CREATE VIEW IF NOT EXISTS vw_active_deployments AS
SELECT 
    d.deployment_id,
    d.pipeline_id,
    d.service,
    d.environment,
    d.commit_id,
    d.branch,
    d.deployed_by,
    d.deploy_timestamp,
    d.day_of_week,
    d.deploy_hour,
    d.is_weekend,
    d.is_after_hours,
    d.time_bucket,
    d.outcome,
    d.has_rollback,
    CASE WHEN d.outcome = 'alerted' THEN 1 ELSE 0 END AS has_alert,
    d.is_instability,
    d.risk_score_weight,
    d.matched_incident_id,
    d.incident_priority,
    d.incident_category,
    d.priority_bucket,
    d.time_to_resolution_hours,
    CASE 
        WHEN d.is_instability = 1 AND d.has_rollback = 1 THEN 'CRITICAL'
        WHEN d.is_instability = 1 THEN 'HIGH'
        WHEN d.outcome = 'alerted' THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_severity
FROM deployment_outcomes d;
