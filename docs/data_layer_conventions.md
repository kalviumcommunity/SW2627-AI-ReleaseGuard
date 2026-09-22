# Clean Data Layer Naming Conventions & Architecture

This document establishes the architecture, naming conventions, and data governance rules for the centralized SQL database layer (`data/release_risk.db`) in **Release Risk Analyzer (`ReleaseGuard`)**.

---

## 1. Overview & Architecture

The clean data layer provides a single source of truth for all operational dashboards, statistical reporting, and risk prediction workflows.

```text
Raw Datasets (CSV)
  │ (Ingestion, Cleaning, Temporal Join & Feature Engineering)
  ▼
Processed Tables (`deployment_outcomes`, `incidents`, `pipeline_logs`, `rollbacks`)
  │
  ├──────► SQL Views (`vw_active_deployments`, `vw_risk_by_environment`, `vw_incident_resolution_metrics`)
  │
  └──────► Pre-Aggregated Summary Tables (`agg_daily_release_risk`)
            │
            ▼
   Streamlit Dashboard & Analytical Reports
```

---

## 2. Naming Conventions

### 2.1 Views (`vw_`)
- **Prefix**: `vw_`
- **Pattern**: `vw_[subject/domain]_[metric_or_scope]`
- **Purpose**: Virtual tables encapsulating complex joins, conditional logic, risk classifications, or metric aggregations without duplicating raw storage.

**Registered Views**:
1. `vw_active_deployments` — Operational deployments enriched with risk severity levels (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
2. `vw_risk_by_environment` — Aggregated stability, rollback, alert rates, and MTTR per service/environment.
3. `vw_incident_resolution_metrics` — Resolution MTTR, reassignments, and reopens by priority bucket and assignment group.

### 2.2 Pre-Aggregated Summary Tables (`agg_`)
- **Prefix**: `agg_`
- **Pattern**: `agg_[grain]_[subject]`
- **Purpose**: Physical summary tables pre-computed on schedule or data pipeline execution to ensure instantaneous UI rendering for high-volume time-series queries.

**Registered Aggregations**:
1. `agg_daily_release_risk` — Daily release risk statistics aggregated by date, service, and environment.

---

## 3. Required Metadata Fields for Aggregated Tables

All `agg_*` tables must include the following audit metadata columns:
- `aggregation_date` (TEXT ISO 8601 YYYY-MM-DD): The date grain of the aggregation.
- `row_count` (INTEGER): Number of contributing operational records.
- `updated_at` (TEXT ISO 8601): Timestamp when the aggregation was generated.

---

## 4. SQL Filtering Standards

When querying the data layer, follow the standardized filtering pattern:
```sql
SELECT 
    dimensions, 
    aggregate_metrics
FROM table_or_view
WHERE row_level_filters       -- Filter raw rows before grouping
GROUP BY dimensions           -- Aggregate by target attributes
HAVING aggregate_filters      -- Filter groups based on metrics (e.g. instability_rate_pct > 20.0)
ORDER BY ranking_metrics DESC -- Rank results
LIMIT N;
```
