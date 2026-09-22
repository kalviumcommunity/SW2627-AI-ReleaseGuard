# Release Risk Analyzer (`ReleaseGuard`)

> **Repository:** `SW2627-AI-ReleaseGuard`  
> **Author:** Saanvi Garg  
> **Course / Cohort:** Kalvium Community — Data Engineering Sprint 1

---

## 📌 Project Description

**Release Risk Analyzer** is an end-to-end data engineering pipeline and operational dashboard designed to quantify and mitigate software deployment risk. 

Modern engineering organizations operate disparate systems:
1. **CI/CD Build & Deployment Pipelines** (e.g., GitHub Actions, GitLab CI, Jenkins).
2. **ITSM / Incident Management Systems** (e.g., ServiceNow Incident Management Process Logs).

Because CI/CD pipelines and incident platforms rarely share a unified transactional key, this project engineers the missing link between deployment events and downstream operational incidents. The pipeline ingests multi-source logs, isolates deployment stages, models realistic synthetic rollback telemetry, standardizes timestamps, executes temporal & semantic heuristic joins, performs feature engineering, persists curated outcomes to SQLite, and serves an interactive **Streamlit Risk Dashboard** protected by **automated CI/CD data quality gates**.

---

## 🚀 Quick Start (4-Command Onboarding)

Get up and running from zero to interactive dashboard in 4 simple commands:

```bash
# 1. Clone & enter repository
git clone https://github.com/kalviumcommunity/SW2627-AI-ReleaseGuard.git && cd SW2627-AI-ReleaseGuard

# 2. Set up virtual environment and install dependencies
python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt

# 3. Run end-to-end data pipeline (ingestion -> derivation -> cleaning -> joins -> SQLite KPIs)
python scripts/run_pipeline.py

# 4. Launch the Streamlit Release Risk Dashboard
streamlit run scripts/app.py
```
---

## 🗂 Project Structure

```text
SW2627-AI-ReleaseGuard/
│
├── .github/
│   └── workflows/
│       └── data_quality.yml         # CI workflow running automated pytest quality gates
│
├── data/
│   ├── raw/                         # Raw input sources & synthetic rollback fixtures
│   │   ├── incident_log.csv         # UCI ServiceNow Incident Management Process log
│   │   ├── pipeline_logs.csv        # CI/CD pipeline stage execution events
│   │   └── rollbacks.csv            # Synthetic modeled rollback telemetry
│   ├── processed/                   # Cleaned & curated data layer
│   │   └── deployment_outcomes.csv  # Final joined & feature-engineered dataset
│   └── release_risk.db              # SQLite relational analytical database
│
├── notebooks/                       # Exploratory Data Analysis & prototyping notebooks
│
├── output/                          # Audit reports and data logs
│   ├── ingestion_audit_report.json  # Schema verification & encoding audit report
│   ├── cleaning_log.csv             # Row-level cleaning, deduplication & null-handling log
│   └── join_audit_report.json       # Join match statistics, orphaned record metrics
│
├── scripts/                         # Modular pipeline scripts
│   ├── data_ingestion.py            # Step 1: Ingestion with encoding fallback & validation
│   ├── derive_deployments.py        # Step 2: Deployment isolation & rollback generator
│   ├── cleaning.py                  # Step 3: Deduplication, ISO 8601 normalization & nulls
│   ├── join_validation.py          # Step 4: 2-hour window heuristic join & outcome labeling
│   ├── feature_engineering.py       # Step 5: Day/hour/weekend/priority risk feature engineering
│   ├── database_kpis.py             # Step 6: SQLite table ingestion & SQL KPI analytical queries
│   ├── run_pipeline.py              # Orchestrator running steps 1-6 end-to-end
│   └── app.py                       # Step 7: Streamlit interactive risk intelligence dashboard
│
├── tests/                           # Automated validation test suite
│   └── test_data_quality.py         # Pytest assertions for schema, nulls, duplicates & domains
│
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore configuration
├── contribution.md                  # Project sprint contribution log
├── requirements.txt                 # Project dependencies
└── README.md                        # Documentation and Viva defense notes
```

---

## 🎓 Sprint 1 Viva Defense & Architectural Decisions

### 1. Incident-to-Deployment Matching Logic (The Heuristic Link)
Because raw CI/CD telemetry and ServiceNow incident logs originate in decoupled systems:
- **Temporal Proximity**: Incidents are mapped to a deployment if the incident's `opened_at` occurs within **$[T_{\text{deploy}}, T_{\text{deploy}} + \text{2 hours}]$**.
- **Service-Category Mapping**: We apply a deterministic dictionary mapping CI/CD services (e.g. `auth-service`, `payment-gateway`, `frontend-app`) to ServiceNow categories/assignment groups (e.g. `Security / Access`, `Finance / Transactions`, `User Interface`).
- **Classification Hierarchy**:
  1. `rolled_back`: Explicit rollback recorded or deployment failed with rollback trigger.
  2. `alerted`: Incident opened within the 2-hour post-deployment window.
  3. `stable`: Clean deployment with zero matching incidents in the observation window.

### 2. Modeled Rollback Telemetry Assumption
- Real-world CI/CD logs frequently lack explicit rollback flags. In Step 2, synthetic rollbacks (`rollbacks.csv`) are generated for **10–15% of failed/degraded deployments**.
- **Modeled Assumption**: Rollback timestamps occur between $5$ to $45$ minutes after deployment failure with documented operational root causes (`HealthCheckFailed`, `ElevatedErrorRate`, `MemoryLeakDetected`).

### 3. Timestamp Normalization & Deduplication
- Multi-source timestamps (`YYYY-MM-DD HH:MM:SS`, ISO 8601, mixed formats) are parsed and standardized to **UTC ISO 8601**.
- Multiple snapshot updates for the same `incident_id` or `deployment_id` are deduplicated by retaining the **latest known state**, logging every deduplication event to `output/cleaning_log.csv`.
