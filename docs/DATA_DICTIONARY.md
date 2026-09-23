# Data Dictionary & Business Mapping

## 1. Dataset Overview

The **Release Risk Analyzer (`ReleaseGuard`)** database consolidates raw operational logs across three real open datasets:
1. **UCI Machine Learning Repository**: ServiceNow Incident Management Process Enriched Event Log (`incident_log.csv`)
2. **Kaggle**: AI-Driven CI/CD Pipeline Execution Logs Dataset (`pipeline_logs.csv`)
3. **D2KLab**: GitHub Actions Workflow Execution Dataset (`gha_workflow_runs.csv`)

These sources are cleaned, validated, and linked into a single source of truth in SQLite (`data/release_risk.db`).

- **Primary Analytical Table**: `deployment_outcomes`
- **Database Engine**: SQLite 3 / SQLAlchemy
- **Data Refresh Frequency**: Automated Intake Pipeline / Interactive UI Drag-and-Drop
- **Maintained By**: Data Engineering & Reliability Team

---

## 2. Table Schemas & Column Definitions

### 2.1 Table: `deployment_outcomes`

| Column Name | Data Type | Business Meaning | Example Value | Related KPI | Null Policy |
|---|---|---|---|---|---|
| `deployment_id` | `VARCHAR(64)` | Unique release deployment identifier | `DEP-PIPE-1001-001` | Total Deployments | **NOT NULL** |
| `pipeline_id` | `VARCHAR(64)` | Pipeline execution run identifier | `PIPE-1001` | Pipeline Volume | **NOT NULL** |
| `service` | `VARCHAR(64)` | Microservice component deployed | `auth-service` | Service Risk Breakdown | **NOT NULL** |
| `environment` | `VARCHAR(32)` | Target environment (`production`, `staging`, `development`) | `production` | Environment Instability Rate | **NOT NULL** |
| `commit_id` | `VARCHAR(40)` | Source code commit SHA | `c482f1` | Commit Traceability | **NOT NULL** |
| `branch` | `VARCHAR(64)` | Git branch name (`hotfix/*`, `release/*`, `main`) | `hotfix/payment-timeout` | Branch Risk Profile | **NOT NULL** |
| `deployed_by` | `VARCHAR(64)` | Operator or bot initiating deployment | `maya_eng` | User Risk Analysis | **NOT NULL** |
| `deploy_timestamp` | `DATETIME (ISO 8601)` | UTC timestamp when release occurred | `2026-08-01 14:30:00` | Temporal Trend Analysis | **NOT NULL** |
| `day_of_week` | `VARCHAR(16)` | Day of week when deployed | `Monday` | Day-of-Week Risk Heatmap | **NOT NULL** |
| `deploy_hour` | `INTEGER` | Deploy hour in 24-hour UTC format (0–23) | `14` | Off-Hours Deployment Risk | **NOT NULL** |
| `is_weekend` | `INTEGER (0/1)` | Binary indicator (1 if Sat/Sun) | `0` | Weekend Deployment Rate | **NOT NULL** |
| `is_after_hours` | `INTEGER (0/1)` | Binary indicator (1 if outside 09:00–18:00 UTC) | `1` | After-Hours Instability | **NOT NULL** |
| `time_bucket` | `VARCHAR(32)` | Categorical time window | `Afternoon (12:00-18:00)` | Window Instability Rate | **NOT NULL** |
| `deploy_quarter` | `VARCHAR(8)` | Fiscal quarter (`Q1`, `Q2`, `Q3`, `Q4`) | `Q3` | Quarterly Risk Analysis | **NOT NULL** |
| `month_sin` / `month_cos` | `FLOAT` | Cyclical month sine/cosine values | `0.866` / `-0.500` | Machine Learning Time Vectors | **NOT NULL** |
| `outcome` | `VARCHAR(32)` | Health outcome (`stable`, `alerted`, `rolled_back`) | `rolled_back` | Rollback & Alert Rate | **NOT NULL** |
| `has_rollback` | `INTEGER (0/1)` | Binary indicator of automated rollback | `1` | Rollback Rate % | **NOT NULL** |
| `is_instability` | `INTEGER (0/1)` | Composite flag (1 if alerted or rolled_back) | `1` | Instability Rate % | **NOT NULL** |
| `composite_risk_score` | `FLOAT` | Normalized 0-100 release risk index | `42.50` | Composite Release Risk Score | **NOT NULL** |
| `matched_incident_id` | `VARCHAR(32)` | Linked ServiceNow incident ID within 2h window | `INC005001` | Incident Match Rate | Nullable |
| `priority_bucket` | `VARCHAR(32)` | ServiceNow incident priority rating | `Critical (P1)` | MTTR by Priority | Nullable (`None / Stable` if no incident) |
| `time_to_resolution_hours` | `FLOAT` | Incident resolution time in decimal hours | `2.50` | Mean Time-to-Resolution (MTTR) | Nullable |
| `sla_breach_flag` | `INTEGER (0/1)` | Binary indicator of SLA violation | `1` | SLA Compliance Rate | **NOT NULL** |
| `escalation_depth` | `INTEGER` | Number of team reassignments | `2` | Operational Escalation Index | **NOT NULL** |
| `reopen_risk_score` | `FLOAT` | Weighted reopen/reassignment penalty | `3.70` | Ticket Quality Score | **NOT NULL** |
| `job_duration_seconds` | `INTEGER` | Pipeline execution duration in seconds | `420` | CI/CD Execution Efficiency | **NOT NULL** |
| `test_pass_rate` | `FLOAT` | Unit/integration test suite pass ratio (0.0–1.0) | `0.96` | Test Quality Metric | **NOT NULL** |
| `security_finding_count` | `INTEGER` | Pre-deploy security vulnerabilities detected | `1` | Security Risk Factor | **NOT NULL** |
| `flaky_test_flag` | `INTEGER (0/1)` | Binary indicator of non-deterministic test suites | `0` | Flaky Test Indicator | **NOT NULL** |

---

## 3. Key Business KPI Formulas

| KPI Name | Formula | Related Columns | Business Purpose |
|---|---|---|---|
| **Instability Rate (%)** | `100.0 * SUM(is_instability) / COUNT(*)` | `is_instability`, `deployment_id` | Measures total percentage of degraded/failed releases |
| **Rollback Rate (%)** | `100.0 * SUM(has_rollback) / COUNT(*)` | `has_rollback`, `deployment_id` | Measures percentage of failed releases requiring code rollback |
| **Mean MTTR (Hours)** | `AVG(time_to_resolution_hours)` | `time_to_resolution_hours`, `matched_incident_id` | Measures engineering response speed for incidents |
| **Composite Risk Score (0-100)** | Weighted function of temporal timing, test pass rate, security findings, SLA breach history, and incident priority | `composite_risk_score` | Quantifies single actionable release risk index |
| **SLA Compliance Rate (%)** | `100.0 * (1 - SUM(sla_breach_flag) / COUNT(*))` | `sla_breach_flag` | Evaluates ITSM response contract performance |
