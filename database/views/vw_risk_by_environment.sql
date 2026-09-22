-- View: vw_risk_by_environment
-- Purpose: Centralize deployment health & risk KPIs aggregated by service and environment.
-- Used by: Executive Risk Dashboard, Operations Overview.

CREATE VIEW IF NOT EXISTS vw_risk_by_environment AS
SELECT 
    service,
    environment,
    COUNT(*) AS total_deployments,
    SUM(CASE WHEN outcome = 'stable' THEN 1 ELSE 0 END) AS stable_deployments,
    SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) AS alerted_deployments,
    SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) AS rollback_deployments,
    ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct,
    ROUND(100.0 * SUM(has_rollback) / COUNT(*), 2) AS rollback_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) / COUNT(*), 2) AS alert_rate_pct,
    ROUND(AVG(time_to_resolution_hours), 2) AS mean_mttr_hours
FROM deployment_outcomes
GROUP BY service, environment;
