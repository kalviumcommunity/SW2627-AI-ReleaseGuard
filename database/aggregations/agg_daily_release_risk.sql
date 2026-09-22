-- Table: agg_daily_release_risk
-- Purpose: Pre-aggregated daily release risk summary table for high-performance dashboard queries.
-- Grain: One row per aggregation_date, service, and environment.

CREATE TABLE IF NOT EXISTS agg_daily_release_risk (
    aggregation_date TEXT NOT NULL,
    service TEXT NOT NULL,
    environment TEXT NOT NULL,
    total_deployments INTEGER NOT NULL,
    stable_count INTEGER NOT NULL,
    alert_count INTEGER NOT NULL,
    rollback_count INTEGER NOT NULL,
    instability_rate_pct REAL NOT NULL,
    mean_mttr_hours REAL,
    row_count INTEGER NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (aggregation_date, service, environment)
);

-- Aggregation Refresh Query:
-- INSERT OR REPLACE INTO agg_daily_release_risk
-- SELECT 
--     SUBSTR(deploy_timestamp, 1, 10) AS aggregation_date,
--     service,
--     environment,
--     COUNT(*) AS total_deployments,
--     SUM(CASE WHEN outcome = 'stable' THEN 1 ELSE 0 END) AS stable_count,
--     SUM(CASE WHEN outcome = 'alerted' THEN 1 ELSE 0 END) AS alert_count,
--     SUM(CASE WHEN outcome = 'rolled_back' THEN 1 ELSE 0 END) AS rollback_count,
--     ROUND(100.0 * SUM(is_instability) / COUNT(*), 2) AS instability_rate_pct,
--     ROUND(AVG(time_to_resolution_hours), 2) AS mean_mttr_hours,
--     COUNT(*) AS row_count,
--     DATETIME('now') AS updated_at
-- FROM deployment_outcomes
-- GROUP BY SUBSTR(deploy_timestamp, 1, 10), service, environment;
