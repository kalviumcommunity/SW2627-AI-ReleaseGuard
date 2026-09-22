-- ======================================================================
-- Release Risk Analyzer - Core Analytical KPI Queries
-- ======================================================================

-- 1. Rollback & Alert Rate by Day of Week and Deploy Hour
-- Evaluates temporal vulnerability windows for deployments
SELECT 
    day_of_week,
    deploy_hour,
    COUNT(*) AS total_deployments,
    SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) AS rollback_count,
    SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) AS alert_count,
    ROUND(100.0 * SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) / COUNT(*), 2) AS rollback_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) / COUNT(*), 2) AS alert_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN outcome != 'stable' THEN 1 ELSE 0 END) / COUNT(*), 2) AS instability_rate_pct
FROM deployment_outcomes
GROUP BY day_of_week, deploy_hour
ORDER BY instability_rate_pct DESC, total_deployments DESC;


-- 2. Mean Time-to-Resolution (MTTR) by Incident Priority
-- Measures operational incident duration across severity tiers
SELECT 
    priority_bucket,
    COUNT(matched_incident_id) AS incident_count,
    ROUND(AVG(time_to_resolution_hours), 2) AS mean_ttr_hours,
    ROUND(MIN(time_to_resolution_hours), 2) AS min_ttr_hours,
    ROUND(MAX(time_to_resolution_hours), 2) AS max_ttr_hours
FROM deployment_outcomes
WHERE priority_bucket != 'None / Stable' AND time_to_resolution_hours IS NOT NULL
GROUP BY priority_bucket
ORDER BY mean_ttr_hours DESC;


-- 3. Top Risk Conditions Ranked by Instability Rate
-- Identifies top 5 riskiest combinations of service, environment, day, and time window
SELECT 
    service,
    environment,
    day_of_week,
    time_bucket,
    COUNT(*) AS total_deployments,
    SUM(is_instability) AS unstable_deployments,
    ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct,
    SUM(has_rollback) AS total_rollbacks
FROM deployment_outcomes
GROUP BY service, environment, day_of_week, time_bucket
ORDER BY instability_rate_pct DESC, total_rollbacks DESC, total_deployments DESC
LIMIT 5;
