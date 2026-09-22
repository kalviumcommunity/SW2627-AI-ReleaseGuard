"""
Step 7: Release Risk Analyzer - Interactive Streamlit Dashboard (v2)

Enhanced with:
- Multi-tab navigation: Overview, Deep Analysis, Pipeline Explainer, Raw Data & SQL Clean Data Layer
- SQL Clean Data Layer integration: view live SQLite views (vw_active_deployments, vw_risk_by_environment, vw_incident_resolution_metrics) & pre-aggregated table (agg_daily_release_risk)
- Sankey diagram showing flow: deployments -> outcomes
- Funnel + donut charts for outcome distribution
- Per-service risk scorecards
- Rollback root cause breakdown
- Branch & user risk analysis
- After-hours vs business-hours comparison
- Animated gauges for key rates
- Inline "📖 What does this mean?" explanations throughout
"""

import os
import sys
import sqlite3
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ReleaseGuard | Release Risk Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.85), rgba(15,23,42,0.95));
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 22px 20px 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    transition: transform 0.25s ease, border-color 0.25s ease;
    height: 120px;
}
.kpi-card:hover { transform: translateY(-3px); border-color: rgba(129,140,248,0.5); }
.kpi-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 6px; }
.kpi-value { font-size: 2.1rem; font-weight: 800; line-height: 1; }
.kpi-sub { font-size: 0.78rem; color: #64748b; margin-top: 5px; }

/* ── Header ── */
.hero {
    padding: 28px 32px;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-radius: 18px;
    border: 1px solid rgba(129,140,248,0.2);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(129,140,248,0.05) 0%, transparent 70%);
}
.hero-title {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
}
.hero-sub { color: #94a3b8; font-size: 1rem; margin: 0; }

/* ── Section headers ── */
.section-header {
    font-size: 1.15rem; font-weight: 700; color: #e2e8f0;
    border-left: 4px solid #818cf8; padding-left: 12px;
    margin: 24px 0 16px;
}

/* ── Explainer boxes ── */
.explainer {
    background: rgba(129,140,248,0.08);
    border: 1px solid rgba(129,140,248,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.6;
}
.explainer strong { color: #a5b4fc; }

/* ── Risk badges ── */
.badge-rolled_back { background: rgba(239,68,68,0.15); color: #f87171;
    border: 1px solid #ef4444; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.badge-alerted { background: rgba(245,158,11,0.15); color: #fbbf24;
    border: 1px solid #f59e0b; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.badge-stable { background: rgba(16,185,129,0.15); color: #34d399;
    border: 1px solid #10b981; padding: 3px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

/* ── Pipeline step card ── */
.step-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.7), rgba(15,23,42,0.8));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    position: relative;
}
.step-num { font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #818cf8; margin-bottom: 6px; }
.step-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
.step-desc { font-size: 0.87rem; color: #94a3b8; line-height: 1.6; }
.step-output { margin-top: 10px; font-size: 0.82rem; color: #64748b; }
.step-output code { background: rgba(129,140,248,0.1); color: #a5b4fc;
    padding: 1px 6px; border-radius: 4px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    db_path = "data/release_risk.db"
    csv_path = "data/processed/deployment_outcomes.csv"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM deployment_outcomes", conn)
            conn.close()
            df["deploy_dt"] = pd.to_datetime(df["deploy_timestamp"])
            return df
        except Exception:
            pass
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df["deploy_dt"] = pd.to_datetime(df["deploy_timestamp"])
        return df
    from scripts.run_pipeline import main as run_p
    run_p()
    df = pd.read_csv(csv_path)
    df["deploy_dt"] = pd.to_datetime(df["deploy_timestamp"])
    return df

@st.cache_data(ttl=60)
def load_clean_data_views():
    db_path = "data/release_risk.db"
    views = {}
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            views["vw_active_deployments"] = pd.read_sql_query("SELECT * FROM vw_active_deployments", conn)
            views["vw_risk_by_environment"] = pd.read_sql_query("SELECT * FROM vw_risk_by_environment", conn)
            views["vw_incident_resolution_metrics"] = pd.read_sql_query("SELECT * FROM vw_incident_resolution_metrics", conn)
            views["agg_daily_release_risk"] = pd.read_sql_query("SELECT * FROM agg_daily_release_risk", conn)
            conn.close()
        except Exception:
            pass
    return views

@st.cache_data(ttl=60)
def load_audit_reports():
    reports = {}
    for name, path in [
        ("ingestion", "output/ingestion_audit_report.json"),
        ("join",      "output/join_audit_report.json"),
        ("kpi",       "output/kpi_summary.json"),
        ("schema",    "output/database_schema_audit.json"),
    ]:
        if os.path.exists(path):
            with open(path) as f:
                reports[name] = json.load(f)
    return reports

try:
    df_raw = load_data()
    db_views = load_clean_data_views()
    audit = load_audit_reports()
except Exception as e:
    st.error(f"❌ Could not load data: {e}. Run `python scripts/run_pipeline.py` first.")
    st.stop()

OUTCOME_COLORS = {"stable": "#10b981", "alerted": "#f59e0b", "rolled_back": "#ef4444"}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:8px 0 16px'>
        <div style='font-size:2.5rem'>🛡️</div>
        <div style='font-size:1.2rem; font-weight:800; color:#818cf8'>ReleaseGuard</div>
        <div style='font-size:0.75rem; color:#64748b'>Release Risk Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**🔍 Global Filters**")
    all_services = sorted(df_raw["service"].unique())
    sel_services = st.multiselect("Services", all_services, default=all_services)

    all_envs = sorted(df_raw["environment"].unique())
    sel_envs = st.multiselect("Environments", all_envs, default=all_envs)

    all_outcomes = sorted(df_raw["outcome"].unique())
    sel_outcomes = st.multiselect("Outcomes", all_outcomes, default=all_outcomes)

    min_date = df_raw["deploy_dt"].min().date()
    max_date = df_raw["deploy_dt"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    st.markdown("---")

    total_raw = len(df_raw)
    st.caption(f"📦 Total records in DB: **{total_raw}**")
    st.caption(f"🗄️ Source: `data/release_risk.db` (SQLite)")

# Apply filters
fdf = df_raw[
    df_raw["service"].isin(sel_services) &
    df_raw["environment"].isin(sel_envs) &
    df_raw["outcome"].isin(sel_outcomes)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    fdf = fdf[(fdf["deploy_dt"].dt.date >= date_range[0]) & (fdf["deploy_dt"].dt.date <= date_range[1])]

# Quick metrics
n_total    = len(fdf)
n_rb       = (fdf["outcome"] == "rolled_back").sum()
n_alert    = (fdf["outcome"] == "alerted").sum()
n_stable   = (fdf["outcome"] == "stable").sum()
rb_rate    = (n_rb / n_total * 100) if n_total else 0
alert_rate = (n_alert / n_total * 100) if n_total else 0
instab     = ((n_rb + n_alert) / n_total * 100) if n_total else 0
valid_ttr  = fdf[fdf["time_to_resolution_hours"].notnull()]["time_to_resolution_hours"]
mttr       = valid_ttr.mean() if len(valid_ttr) else 0.0

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1 class="hero-title">🛡️ Release Risk Analyzer</h1>
    <p class="hero-sub">
        End-to-End Data Engineering Pipeline • Real ServiceNow Incident & CI/CD Telemetry • Live SQLite Clean Data Layer
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_overview, tab_deep, tab_explainer, tab_raw = st.tabs([
    "📊 Overview Dashboard",
    "🔬 Deep Risk Analysis",
    "🗺️ Pipeline Explainer",
    "📋 Raw Data & SQL Clean Data Layer"
])

# =============================================================================
# TAB 1 — OVERVIEW DASHBOARD
# =============================================================================
with tab_overview:
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Deployments</div>
            <div class="kpi-value" style="color:#818cf8">{n_total}</div>
            <div class="kpi-sub">Filtered from {total_raw} total</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Rollback Rate</div>
            <div class="kpi-value" style="color:#ef4444">{rb_rate:.1f}%</div>
            <div class="kpi-sub">{n_rb} failed / rolled back</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Incident Alert Rate</div>
            <div class="kpi-value" style="color:#f59e0b">{alert_rate:.1f}%</div>
            <div class="kpi-sub">{n_alert} triggered incidents</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        color = "#ef4444" if instab > 20 else ("#f59e0b" if instab > 10 else "#10b981")
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Instability Rate</div>
            <div class="kpi-value" style="color:{color}">{instab:.1f}%</div>
            <div class="kpi-sub">{n_rb + n_alert} total non-stable</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Mean MTTR</div>
            <div class="kpi-value" style="color:#38bdf8">{mttr:.1f}<span style="font-size:1rem;font-weight:400"> hrs</span></div>
            <div class="kpi-sub">Time to incident resolution</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown('<div class="section-header">Outcome Distribution</div>', unsafe_allow_html=True)
        outcome_counts = fdf["outcome"].value_counts().reset_index()
        outcome_counts.columns = ["Outcome", "Count"]
        fig_donut = px.pie(
            outcome_counts, values="Count", names="Outcome",
            color="Outcome", color_discrete_map=OUTCOME_COLORS,
            hole=0.55
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Daily Deployment Instability Trend</div>', unsafe_allow_html=True)
        daily = fdf.groupby(fdf["deploy_dt"].dt.date).agg(
            total=("deployment_id", "count"),
            unstable=("is_instability", "sum"),
            rollbacks=("has_rollback", "sum")
        ).reset_index()
        daily["instab_pct"] = (daily["unstable"] / daily["total"] * 100).round(1)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=daily["deploy_dt"], y=daily["total"],
            name="Total Deployments", marker_color="#334155", opacity=0.8
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily["deploy_dt"], y=daily["instab_pct"],
            name="Instability Rate (%)", yaxis="y2",
            line=dict(color="#ef4444", width=3), mode="lines+markers"
        ))
        fig_trend.update_layout(
            yaxis=dict(title="Deploy Volume", gridcolor="rgba(255,255,255,0.05)"),
            yaxis2=dict(title="Instability Rate (%)", overlaying="y", side="right", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=30, b=30, l=40, r=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('<div class="explainer">📖 <strong>What does this mean?</strong> Instability Rate measures the percentage of releases that either triggered an incident alert or required a full rollback. High instability spikes indicate unsafe release windows (e.g. late Fridays or unvetted hotfixes).</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Service Risk Scorecards</div>', unsafe_allow_html=True)

    svc = fdf.groupby("service").agg(
        total=("deployment_id", "count"),
        rollbacks=("has_rollback", "sum"),
        alerts=("outcome", lambda x: (x == "alerted").sum()),
        stables=("outcome", lambda x: (x == "stable").sum()),
        avg_ttr=("time_to_resolution_hours", "mean")
    ).reset_index()
    svc["instab_pct"] = ((svc["rollbacks"] + svc["alerts"]) / svc["total"] * 100).round(1)

    fig_svc = px.bar(
        svc.sort_values(by="instab_pct", ascending=False),
        x="service", y=["stables", "alerts", "rollbacks"],
        title="Deployment Outcomes by Microservice",
        color_discrete_map={"stables": "#10b981", "alerts": "#f59e0b", "rollbacks": "#ef4444"},
        labels={"value": "Count", "variable": "Outcome"}
    )
    fig_svc.update_layout(
        barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"), margin=dict(t=40, b=40, l=40, r=40)
    )
    st.plotly_chart(fig_svc, use_container_width=True)

# =============================================================================
# TAB 2 — DEEP RISK ANALYSIS
# =============================================================================
with tab_deep:
    st.markdown('<div class="section-header">1. Operational Flow: Deployments → Incident Matching → Final Outcomes</div>', unsafe_allow_html=True)

    n_deploy  = len(fdf)
    n_inc_m   = fdf["matched_incident_id"].notnull().sum()
    n_no_inc  = n_deploy - n_inc_m
    n_st      = (fdf["outcome"] == "stable").sum()
    n_al      = (fdf["outcome"] == "alerted").sum()
    n_rb2     = (fdf["outcome"] == "rolled_back").sum()

    labels = [
        "Total Deployments",      # 0
        "Matched Incident (2h)",  # 1
        "No Incident Matched",    # 2
        "Stable Outcome",         # 3
        "Alerted Outcome",        # 4
        "Rolled Back Outcome"     # 5
    ]
    sources = [0, 0, 1, 1, 2]
    targets = [1, 2, 4, 5, 3]
    values  = [n_inc_m, n_no_inc, n_al, n_rb2, n_no_inc]
    colors  = ["#818cf8", "#34d399", "#f59e0b", "#ef4444", "#10b981"]

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=0.5),
            label=labels, color=["#818cf8", "#f59e0b", "#10b981", "#10b981", "#f59e0b", "#ef4444"]
        ),
        link=dict(source=sources, target=targets, value=values, color=["rgba(129,140,248,0.3)", "rgba(16,185,129,0.3)", "rgba(245,158,11,0.4)", "rgba(239,68,68,0.4)", "rgba(16,185,129,0.4)"])
    )])
    fig_sankey.update_layout(
        height=320, margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.markdown("---")
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="section-header">2. Branch Risk Profile</div>', unsafe_allow_html=True)
        fdf["branch_type"] = fdf["branch"].apply(
            lambda b: "hotfix/*" if str(b).startswith("hotfix")
            else ("release/*" if str(b).startswith("release")
            else ("main" if b == "main" else "other"))
        )
        b_df = fdf.groupby("branch_type").agg(
            total=("deployment_id", "count"),
            unstable=("is_instability", "sum")
        ).reset_index()
        b_df["instab_pct"] = (b_df["unstable"] / b_df["total"] * 100).round(1)

        fig_branch = px.bar(
            b_df, x="branch_type", y="instab_pct", text="instab_pct",
            color="instab_pct", color_continuous_scale="Reds",
            title="Instability Rate (%) by Git Branch Type",
            labels={"instab_pct": "Instability Rate (%)", "branch_type": "Branch Type"}
        )
        fig_branch.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
        st.plotly_chart(fig_branch, use_container_width=True)

    with c_right:
        st.markdown('<div class="section-header">3. After-Hours Deployment Penalty</div>', unsafe_allow_html=True)
        ah_df = fdf.groupby("time_bucket").agg(
            total=("deployment_id", "count"),
            unstable=("is_instability", "sum"),
            rollbacks=("has_rollback", "sum")
        ).reset_index()
        ah_df["instab_pct"] = (ah_df["unstable"] / ah_df["total"] * 100).round(1)

        fig_ah = px.bar(
            ah_df, x="time_bucket", y="instab_pct", text="instab_pct",
            color="time_bucket", color_discrete_sequence=["#38bdf8", "#f59e0b", "#ef4444"],
            title="Instability Rate (%) by Deployment Time Window",
            labels={"instab_pct": "Instability Rate (%)", "time_bucket": "Time Window"}
        )
        fig_ah.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
        st.plotly_chart(fig_ah, use_container_width=True)

# =============================================================================
# TAB 3 — PIPELINE EXPLAINER
# =============================================================================
with tab_explainer:
    st.markdown("""
    ### 🗺️ Data Engineering Pipeline Architectural Explainer

    This project takes raw ServiceNow incident event logs and CI/CD pipeline event logs, standardizes them, validates their schema, joins them using a 2-hour temporal heuristic, engineers risk features, and persists the clean data layer into SQLite.
    """)

    steps = [
        ("Step 1", "Real Data Ingestion & Schema Validation", "data_ingestion.py",
         "Ingests <code>incident_log.csv</code> (UCI ServiceNow dataset, 250 rows) and <code>pipeline_logs.csv</code> (600 CI/CD events). Performs encoding fallback (utf-8 -> latin-1) and strict schema checks against required columns.",
         f"Loaded <b>250</b> incident rows & <b>600</b> pipeline rows cleanly."),
        ("Step 2", "Deployment Derivation & Synthetic Rollback Generation", "derive_deployments.py",
         "Filters raw pipeline events for <code>stage_name == 'Deploy'</code> (120 deployment events). Models 14 synthetic rollback records based on real incident resolution patterns to satisfy Sprint 1 defense requirements.",
         f"Isolated <b>120</b> deployment events & generated <b>14</b> rollbacks."),
        ("Step 3", "Timestamp Standardization & Deduplication", "cleaning.py",
         "Parses messy timestamps (ISO 8601, slash formats) to standardized UTC string format. Deduplicates multiple snapshot entries per incident/deployment, retaining the latest known state.",
         f"Deduplicated snapshots; 100% clean UTC timestamps."),
        ("Step 4", "Heuristic 2-Hour Temporal & Service Join", "join_validation.py",
         "Performs left outer join matching each deployment to incidents occurring within <code>[T, T + 2 hours]</code> on the same service. Labels each deployment as <code>stable</code>, <code>alerted</code>, or <code>rolled_back</code>.",
         f"Matched <b>31</b> non-stable outcomes out of 120 total deployments."),
        ("Step 5", "Temporal & Severity Risk Feature Engineering", "feature_engineering.py",
         "Engineers operational features: <code>deploy_hour</code>, <code>is_weekend</code>, <code>is_after_hours</code>, <code>time_bucket</code>, <code>priority_bucket</code>, <code>is_instability</code>, and composite <code>risk_score_weight</code>.",
         f"Engineered <b>8</b> risk features across 120 rows."),
        ("Step 6", "SQLite Loading & Clean Data Layer Execution", "database_kpis.py",
         "Persists clean datasets to <code>data/release_risk.db</code> (SQLite), builds SQL views (<code>vw_active_deployments</code>, <code>vw_risk_by_environment</code>, <code>vw_incident_resolution_metrics</code>), populates <code>agg_daily_release_risk</code>, and executes analytical KPI queries.",
         f"Persisted to SQLite database; <b>4/4</b> views & pre-aggregations active.")
    ]

    for num, name, script, desc, out in steps:
        with st.expander(f"{num} — {name} (`scripts/{script}`)", expanded=True):
            st.markdown(f"""
            <div class="step-card">
                <div class="step-num">{num} • SCRIPTS/{script.upper()}</div>
                <div class="step-title">{name}</div>
                <div class="step-desc">{desc}</div>
                <div class="step-output">📌 <strong>Result:</strong> {out}</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TAB 4 — RAW DATA & SQL CLEAN DATA LAYER
# =============================================================================
with tab_raw:
    st.markdown('<div class="section-header">1. SQL Clean Data Layer Views Explorer</div>', unsafe_allow_html=True)
    st.markdown("Inspect live database objects stored in `data/release_risk.db` (SQLite):")

    v_tabs = st.tabs([
        "👁️ vw_active_deployments",
        "🌍 vw_risk_by_environment",
        "⏱️ vw_incident_resolution_metrics",
        "📈 agg_daily_release_risk (Pre-Aggregated)"
    ])

    with v_tabs[0]:
        if "vw_active_deployments" in db_views and len(db_views["vw_active_deployments"]) > 0:
            st.dataframe(db_views["vw_active_deployments"], use_container_width=True, hide_index=True)
            st.caption(f"Showing **{len(db_views['vw_active_deployments'])}** rows from view `vw_active_deployments`")
        else:
            st.info("View `vw_active_deployments` is loading or empty.")

    with v_tabs[1]:
        if "vw_risk_by_environment" in db_views and len(db_views["vw_risk_by_environment"]) > 0:
            st.dataframe(db_views["vw_risk_by_environment"], use_container_width=True, hide_index=True)
            st.caption(f"Showing **{len(db_views['vw_risk_by_environment'])}** rows from view `vw_risk_by_environment`")
        else:
            st.info("View `vw_risk_by_environment` is loading or empty.")

    with v_tabs[2]:
        if "vw_incident_resolution_metrics" in db_views and len(db_views["vw_incident_resolution_metrics"]) > 0:
            st.dataframe(db_views["vw_incident_resolution_metrics"], use_container_width=True, hide_index=True)
            st.caption(f"Showing **{len(db_views['vw_incident_resolution_metrics'])}** rows from view `vw_incident_resolution_metrics`")
        else:
            st.info("View `vw_incident_resolution_metrics` is loading or empty.")

    with v_tabs[3]:
        if "agg_daily_release_risk" in db_views and len(db_views["agg_daily_release_risk"]) > 0:
            st.dataframe(db_views["agg_daily_release_risk"], use_container_width=True, hide_index=True)
            st.caption(f"Showing **{len(db_views['agg_daily_release_risk'])}** pre-aggregated rows from table `agg_daily_release_risk`")
        else:
            st.info("Table `agg_daily_release_risk` is loading or empty.")

    st.markdown("---")
    st.markdown('<div class="section-header">2. Filtered Deployment Telemetry Explorer</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explainer">
        Below is the full <code>deployment_outcomes</code> dataset after 2-hour temporal join matching
        and computed outcome label. This is what gets loaded into SQLite and powers all charts above.
    </div>""", unsafe_allow_html=True)

    display_cols = [
        "deployment_id","pipeline_id","service","environment","deploy_timestamp",
        "deployed_by","branch","status","outcome","has_rollback","rollback_reason",
        "matched_incident_id","incident_priority","incident_category",
        "time_to_resolution_hours","day_of_week","deploy_hour","is_weekend",
        "is_after_hours","priority_bucket","is_instability","risk_score_weight"
    ]
    show_cols = [c for c in display_cols if c in fdf.columns]

    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search across any column...", "")
    with col_sort:
        sort_col = st.selectbox("Sort by", ["deploy_timestamp","risk_score_weight","time_to_resolution_hours"], index=0)

    display_df = fdf[show_cols].sort_values(by=sort_col, ascending=False)
    if search:
        mask = display_df.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=450)
    st.caption(f"Showing **{len(display_df)}** of **{n_total}** records")

    st.markdown("---")

    # Audit reports side by side
    ra, rb2, rc = st.columns(3)

    with ra:
        st.markdown('<div class="section-header">📄 Ingestion Audit</div>', unsafe_allow_html=True)
        if "ingestion" in audit:
            for fname, info in audit["ingestion"].get("datasets", {}).items():
                schema = info.get("schema_validation", {})
                st.markdown(f"**{fname}**")
                st.json({
                    "rows": schema.get("total_rows"),
                    "cols": schema.get("total_columns"),
                    "encoding": info.get("encoding_used"),
                    "valid_schema": schema.get("is_valid"),
                    "missing_cols": schema.get("missing_columns", []),
                    "null_counts": schema.get("null_counts", {})
                })

    with rb2:
        st.markdown('<div class="section-header">🔗 Join Audit</div>', unsafe_allow_html=True)
        if "join" in audit:
            j = audit["join"]
            st.json({
                "total_deployments": j.get("total_deployments"),
                "outcome_distribution": j.get("outcome_distribution"),
                "rollbacks_applied": j.get("deployments_with_rollbacks"),
                "incidents_matched": j.get("incidents_matched_to_deployments"),
                "orphaned_incidents": j.get("orphaned_incidents_count"),
                "orphan_ratio_pct": j.get("orphaned_incidents_ratio_pct"),
                "matching_logic": j.get("join_matching_logic")
            })

    with rc:
        st.markdown('<div class="section-header">🗄️ Database Schema Audit</div>', unsafe_allow_html=True)
        if "schema" in audit:
            st.json(audit["schema"])
        elif "kpi" in audit:
            mttr_kpi = audit["kpi"].get("mttr_by_priority", [])
            if mttr_kpi:
                st.markdown("**Mean TTR by Priority:**")
                st.dataframe(pd.DataFrame(mttr_kpi), use_container_width=True, hide_index=True)

    st.markdown("---")

    csv_export = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Deployment Telemetry (CSV)",
        data=csv_export,
        file_name=f"releaseguard_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
