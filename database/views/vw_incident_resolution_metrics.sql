-- View: vw_incident_resolution_metrics
-- Purpose: Summarize incident resolution statistics and MTTR by priority bucket and incident category.
-- Used by: Incident Response Dashboard, Service Management Analytics.

CREATE VIEW IF NOT EXISTS vw_incident_resolution_metrics AS
SELECT 
    priority_bucket,
    incident_category,
    COUNT(matched_incident_id) AS incident_count,
    ROUND(AVG(time_to_resolution_hours), 2) AS avg_ttr_hours,
    ROUND(MIN(time_to_resolution_hours), 2) AS min_ttr_hours,
    ROUND(MAX(time_to_resolution_hours), 2) AS max_ttr_hours,
    ROUND(AVG(risk_score_weight), 2) AS avg_risk_weight
FROM deployment_outcomes
WHERE matched_incident_id IS NOT NULL AND time_to_resolution_hours IS NOT NULL
GROUP BY priority_bucket, incident_category;
