# Data Dictionary & Business Mapping

## 1. Dataset Overview

The **Release Risk Analyzer (`ReleaseGuard`)** database consolidates raw CI/CD deployment event logs (`pipeline_logs.csv`), IT service management incident logs (`incident_log.csv`), and automated rollback events (`rollbacks.csv`) into a single source of truth in SQLite (`data/release_risk.db`).

- **Primary Analytical Table**: `deployment_outcomes` (120 rows, 28 columns)
- **Database Engine**: SQLite 3 / SQLAlchemy
- **Data Refresh Frequency**: On-demand / CI-CD Pipeline Trigger
- **Maintained By**: Data Engineering & Reliability Team

---

## 2. Table Schemas & Column Definitions

### 2.1 Table: `deployment_outcomes`

| Column Name | Data Type | Business Meaning | Example Value | Related KPI | Null Policy |
|---|---|---|---|---|---|
| `deployment_id` | `VARCHAR(64)` | Unique release deployment identifier | `DEP-2026-0001` | Total Deployments | **NOT NULL** |
| `service` | `VARCHAR(64)` | Microservice component deployed | `auth-service` | Service Risk Breakdown | **NOT NULL** |
| `environment` | `VARCHAR(32)` | Target environment (`production`, `staging`) | `production` | Environment Instability Rate | **NOT NULL** |
| `version` | `VARCHAR(32)` | Release version tag | `v1.2.0` | Release Velocity | **NOT NULL** |
| `commit_id` | `VARCHAR(40)` | Source code commit SHA | `a1b2c3d` | Commit Traceability | **NOT NULL** |
| `branch` | `VARCHAR(64)` | Git branch name (`hotfix/*`, `release/*`, `main`) | `hotfix/patch-01` | Branch Risk Profile | **NOT NULL** |
| `deployed_by` | `VARCHAR(64)` | Operator or bot initiating deployment | `ci-cd-bot` | User Risk Analysis | **NOT NULL** |
| `deploy_timestamp` | `DATETIME (ISO 8601)` | UTC timestamp when release occurred | `2026-03-01T14:30:00Z` | Temporal Trend Analysis | **NOT NULL** |
| `day_of_week` | `VARCHAR(16)` | Day of week when deployed | `Monday` | Day-of-Week Risk Heatmap | **NOT NULL** |
| `deploy_hour` | `INTEGER` | Deploy hour in 24-hour UTC format (0–23) | `14` | Off-Hours Deployment Risk | **NOT NULL** |
| `is_weekend` | `INTEGER (0/1)` | Binary indicator (1 if Sat/Sun) | `0` | Weekend Deployment Rate | **NOT NULL** |
| `is_after_hours` | `INTEGER (0/1)` | Binary indicator (1 if outside 08:00–18:00 UTC) | `1` | After-Hours Instability | **NOT NULL** |
| `time_bucket` | `VARCHAR(32)` | Categorical time window | `Off-Hours` | Window Instability Rate | **NOT NULL** |
| `outcome` | `VARCHAR(32)` | Health outcome (`stable`, `alerted`, `rolled_back`) | `rolled_back` | Rollback & Alert Rate | **NOT NULL** |
| `has_rollback` | `INTEGER (0/1)` | Binary indicator of automated rollback | `1` | Rollback Rate % | **NOT NULL** |
| `has_alert` | `INTEGER (0/1)` | Binary indicator of operational alert | `1` | Alert Rate % | **NOT NULL** |
| `is_instability` | `INTEGER (0/1)` | Composite flag (1 if alerted or rolled_back) | `1` | Instability Rate % | **NOT NULL** |
| `matched_incident_id` | `VARCHAR(32)` | Linked ServiceNow incident ID within 2h window | `INC0010001` | Incident Match Rate | Nullable |
| `priority_bucket` | `VARCHAR(32)` | ServiceNow incident priority rating | `High (P2)` | MTTR by Priority | Nullable (`None / Stable` if no incident) |
| `time_to_resolution_hours` | `FLOAT` | Incident resolution time in decimal hours | `2.50` | Mean Time-to-Resolution (MTTR) | Nullable |
| `reassignment_count` | `INTEGER` | Number of team reassignment events | `1` | Operational Friction | Nullable |
| `reopen_count` | `INTEGER` | Number of incident reopen events | `0` | Resolution Quality | Nullable |

---

## 3. Ambiguous Columns & Resolutions

### `has_rollback` vs `is_instability`
- **Ambiguity**: Does an incident alert count as a rollback?
- **Resolution**: `has_rollback` strictly measures physical code rollbacks (14 events). `is_instability` is a composite flag (`has_rollback | has_alert`) measuring any non-stable release outcome (31 events).
- **KPI Mapping**: `has_rollback` -> **Rollback Rate %** (11.67%), `is_instability` -> **Instability Rate %** (25.83%).

### `priority_bucket`
- **Ambiguity**: How are ServiceNow numeric priorities (`1 - Critical`, `2 - High`) mapped for releases without incidents?
- **Resolution**: Unmatched/stable deployments are mapped to `'None / Stable'`. Matched incidents map to `'Critical (P1)'`, `'High (P2)'`, `'Moderate (P3)'`, `'Low (P4)'`.

---

## 4. Key Business KPI Formulas

| KPI Name | Formula | Related Columns | Business Purpose |
|---|---|---|---|
| **Instability Rate (%)** | `100.0 * SUM(is_instability) / COUNT(*)` | `is_instability`, `deployment_id` | Measures total percentage of risky releases |
| **Rollback Rate (%)** | `100.0 * SUM(has_rollback) / COUNT(*)` | `has_rollback`, `deployment_id` | Measures percentage of failed releases requiring code rollback |
| **Mean MTTR (Hours)** | `AVG(time_to_resolution_hours)` | `time_to_resolution_hours`, `matched_incident_id` | Measures engineering response speed for incidents |
| **After-Hours Risk Ratio** | `Instability Rate (After-Hours) / Instability Rate (Business Hours)` | `is_after_hours`, `is_instability` | Quantifies risk penalty of off-hours deployments |
