"""
Release Risk Analyzer - Modern Presentation UI (v5)

Features:
1. Custom Graphic Hero Illustration & Modern Executive Layout
2. Clean, Uncluttered Visualizations (Plotly chart optimizations)
3. Concise 1-2 Sentence Descriptions Directly Below Each Visual
4. Full Light Mode ☀️ & Dark Mode 🌙 Adaptive Styling
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
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    db_path = os.path.join(PROJECT_ROOT, "data", "release_risk.db")
    csv_path = os.path.join(PROJECT_ROOT, "data", "processed", "deployment_outcomes.csv")
    
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
    db_path = os.path.join(PROJECT_ROOT, "data", "release_risk.db")
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
    paths = {
        "ingestion": os.path.join(PROJECT_ROOT, "output", "ingestion_audit_report.json"),
        "join": os.path.join(PROJECT_ROOT, "output", "join_audit_report.json"),
        "kpi": os.path.join(PROJECT_ROOT, "output", "kpi_summary.json"),
        "schema": os.path.join(PROJECT_ROOT, "output", "database_schema_audit.json")
    }
    for name, path in paths.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                reports[name] = json.load(f)
    return reports

try:
    df_raw = load_data()
    db_views = load_clean_data_views()
    audit = load_audit_reports()
except Exception as e:
    st.error(f"Error loading data: {e}. Run `python scripts/run_pipeline.py` first.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR FILTERS & THEME SELECTOR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:left; padding:8px 0 16px'>
        <div style='font-size:1.4rem; font-weight:800; color:#6366f1; letter-spacing:-0.03em;'>RELEASEGUARD</div>
        <div style='font-size:0.75rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;'>Release Risk Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    theme_choice = st.selectbox("UI Theme", ["Dark Mode", "Light Mode", "Auto System"], index=0)

    st.markdown("---")
    st.markdown("**Filters**")

    all_services = sorted(df_raw["service"].unique())
    sel_services = st.multiselect("Services", all_services, default=all_services)

    all_envs = sorted(df_raw["environment"].unique())
    sel_envs = st.multiselect("Environments", all_envs, default=all_envs)

    all_outcomes = sorted(df_raw["outcome"].unique())
    sel_outcomes = st.multiselect("Outcomes", all_outcomes, default=all_outcomes)

    min_date = df_raw["deploy_dt"].min().date()
    max_date = df_raw["deploy_dt"].max().date()
    date_range = st.date_input("Date Window", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    if "composite_risk_score" in df_raw.columns:
        min_r_val = float(df_raw["composite_risk_score"].min())
        max_r_val = float(df_raw["composite_risk_score"].max())
        risk_range = st.slider("Risk Score Threshold", min_value=0.0, max_value=100.0, value=(min_r_val, max_r_val), step=1.0)
    else:
        risk_range = (0.0, 100.0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset Filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.caption(f"Records Evaluated: **{len(df_raw)}**")
    st.caption("Backend: SQLite `data/release_risk.db`")

# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC THEME INJECTION & STYLING
# ─────────────────────────────────────────────────────────────────────────────
is_light = (theme_choice == "Light Mode")

if is_light:
    css_vars = """
    :root {
        --bg-body: #f8fafc;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        --text-main: #0f172a;
        --text-sub: #475569;
        --text-muted: #64748b;
        --hero-bg: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        --hero-border: #cbd5e1;
        --desc-bg: #f8fafc;
        --desc-border: #6366f1;
        --desc-text: #334155;
    }
    """
    plotly_font_color = "#334155"
    plotly_grid_color = "#f1f5f9"
    plotly_bg = "rgba(0,0,0,0)"
else:
    css_vars = """
    :root {
        --bg-body: #0f172a;
        --card-bg: #1e293b;
        --card-border: #334155;
        --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        --text-main: #f8fafc;
        --text-sub: #94a3b8;
        --text-muted: #64748b;
        --hero-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        --hero-border: #334155;
        --desc-bg: #1e293b;
        --desc-border: #818cf8;
        --desc-text: #94a3b8;
    }
    """
    plotly_font_color = "#94a3b8"
    plotly_grid_color = "#334155"
    plotly_bg = "rgba(0,0,0,0)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

{css_vars}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* KPI Metric Cards */
.kpi-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 18px 16px;
    box-shadow: var(--card-shadow);
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.kpi-label {{
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-sub);
    margin-bottom: 4px;
}}
.kpi-value {{
    font-size: 2.0rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-sub {{
    font-size: 0.76rem;
    color: var(--text-muted);
    font-weight: 500;
}}

/* Hero Layout */
.hero-card {{
    background: var(--hero-bg);
    border: 1px solid var(--hero-border);
    border-radius: 16px;
    padding: 28px 32px;
    box-shadow: var(--card-shadow);
}}
.hero-badge {{
    display: inline-block;
    padding: 4px 10px;
    background: rgba(99, 102, 241, 0.15);
    color: #6366f1;
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 20px;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-main);
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}}
.hero-sub {{
    color: var(--text-sub);
    font-size: 1.0rem;
    margin: 0;
    line-height: 1.5;
}}

/* Concise Visual Description Subtitle Box */
.visual-desc {{
    background: var(--desc-bg);
    border-left: 3px solid var(--desc-border);
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0 20px 0;
    font-size: 0.84rem;
    color: var(--desc-text);
    line-height: 1.45;
}}
.visual-desc strong {{
    color: var(--text-main);
}}

/* Section Title */
.section-header {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 18px 0 10px 0;
    letter-spacing: -0.01em;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FILTER EXECUTION & EMPTY-STATE CHECK
# ─────────────────────────────────────────────────────────────────────────────
fdf = df_raw[
    df_raw["service"].isin(sel_services) &
    df_raw["environment"].isin(sel_envs) &
    df_raw["outcome"].isin(sel_outcomes)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    fdf = fdf[(fdf["deploy_dt"].dt.date >= date_range[0]) & (fdf["deploy_dt"].dt.date <= date_range[1])]

if "composite_risk_score" in fdf.columns:
    fdf = fdf[(fdf["composite_risk_score"] >= risk_range[0]) & (fdf["composite_risk_score"] <= risk_range[1])]

if fdf.empty:
    st.warning("No deployment records match the selected filter criteria. Please broaden your filter selection.")
    if st.button("Reset Filters to View Full Dataset"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# Key Metrics
n_total = len(fdf)
n_rb = (fdf["outcome"] == "rolled_back").sum()
n_alert = (fdf["outcome"] == "alerted").sum()
rb_rate = (n_rb / n_total * 100) if n_total else 0.0
alert_rate = (n_alert / n_total * 100) if n_total else 0.0
instab = ((n_rb + n_alert) / n_total * 100) if n_total else 0.0
valid_ttr = fdf[fdf["time_to_resolution_hours"].notnull()]["time_to_resolution_hours"]
mttr = valid_ttr.mean() if len(valid_ttr) else 0.0
avg_risk = fdf["composite_risk_score"].mean() if "composite_risk_score" in fdf.columns else 0.0
OUTCOME_COLORS = {"stable": "#10b981", "alerted": "#f59e0b", "rolled_back": "#ef4444"}

# ─────────────────────────────────────────────────────────────────────────────
# HERO HEADER WITH GRAPHIC ILLUSTRATION
# ─────────────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([1.6, 1])

with col_h1:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-badge">RELEASE RISK INTELLIGENCE PLATFORM</div>
        <h1 class="hero-title">Software Release Analyzer</h1>
        <p class="hero-sub">
            Automated production risk forecasting, ITSM incident correlation, and CI/CD quality gate enforcement powered by open operational datasets.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    hero_img_path = os.path.join(PROJECT_ROOT, "public", "hero_illustration.jpg")
    if os.path.exists(hero_img_path):
        st.image(hero_img_path, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_overview, tab_deep, tab_explainer, tab_raw, tab_intake = st.tabs([
    "Overview Dashboard",
    "Deep Risk Analysis",
    "Pipeline Explainer",
    "SQL Clean Data Layer",
    "Dataset Intake Pipeline"
])

# =============================================================================
# TAB 1 — OVERVIEW DASHBOARD
# =============================================================================
with tab_overview:
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Deployments</div>
            <div class="kpi-value" style="color:#6366f1">{n_total:,}</div>
            <div class="kpi-sub">Filtered release volume</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Rollback Rate</div>
            <div class="kpi-value" style="color:#ef4444">{rb_rate:.1f}%</div>
            <div class="kpi-sub">{n_rb} failed / reverted</div>
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
            <div class="kpi-value" style="color:#0ea5e9">{mttr:.1f}<span style="font-size:0.85rem"> hrs</span></div>
            <div class="kpi-sub">Incident resolution time</div>
        </div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-value" style="color:#8b5cf6">{avg_risk:.1f}</div>
            <div class="kpi-sub">Normalized 0-100 score</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.8])
    with c1:
        st.markdown('<div class="section-header">Outcome Distribution</div>', unsafe_allow_html=True)
        outcome_counts = fdf["outcome"].value_counts().reset_index()
        outcome_counts.columns = ["Outcome", "Count"]
        fig_donut = px.pie(
            outcome_counts, values="Count", names="Outcome",
            color="Outcome", color_discrete_map=OUTCOME_COLORS, hole=0.6
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), showlegend=False,
            height=280, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, font=dict(color=plotly_font_color)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
        st.markdown("""
        <div class="visual-desc">
            <strong>Description:</strong> Breakdown of release outcomes into Stable (zero incidents within 2h), Alerted (incident created), and Rolled Back.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Daily Deployment & Instability Trend</div>', unsafe_allow_html=True)
        daily = fdf.groupby(fdf["deploy_dt"].dt.date).agg(
            total=("deployment_id", "count"),
            unstable=("is_instability", "sum")
        ).reset_index()
        daily["instab_pct"] = (daily["unstable"] / daily["total"] * 100).round(1)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=daily["deploy_dt"], y=daily["total"], name="Total Releases", marker_color="#94a3b8" if is_light else "#475569", opacity=0.7
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily["deploy_dt"], y=daily["instab_pct"], name="Instability %", yaxis="y2",
            line=dict(color="#ef4444", width=3), mode="lines"
        ))
        fig_trend.update_layout(
            height=280,
            yaxis=dict(title="Deploy Volume", gridcolor=plotly_grid_color),
            yaxis2=dict(title="Instability Rate (%)", overlaying="y", side="right", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=20, b=20, l=30, r=30), paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg,
            font=dict(color=plotly_font_color)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("""
        <div class="visual-desc">
            <strong>Description:</strong> Overlays daily release volume against the percentage of degraded or failed deployments over time.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Service Risk Scorecards</div>', unsafe_allow_html=True)

    svc = fdf.groupby("service").agg(
        total=("deployment_id", "count"),
        rollbacks=("has_rollback", "sum"),
        alerts=("outcome", lambda x: (x == "alerted").sum()),
        stables=("outcome", lambda x: (x == "stable").sum())
    ).reset_index()
    svc["instab_pct"] = ((svc["rollbacks"] + svc["alerts"]) / svc["total"] * 100).round(1)

    fig_svc = px.bar(
        svc.sort_values(by="instab_pct", ascending=True),
        y="service", x=["stables", "alerts", "rollbacks"],
        orientation="h",
        color_discrete_map={"stables": "#10b981", "alerts": "#f59e0b", "rollbacks": "#ef4444"},
        labels={"value": "Deployment Count", "variable": "Outcome", "service": "Service Domain"}
    )
    fig_svc.update_layout(
        barmode="stack", height=320, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg,
        font=dict(color=plotly_font_color), margin=dict(t=20, b=20, l=40, r=40),
        xaxis=dict(gridcolor=plotly_grid_color), yaxis=dict(gridcolor=plotly_grid_color)
    )
    st.plotly_chart(fig_svc, use_container_width=True)

    st.markdown("""
    <div class="visual-desc">
        <strong>Description:</strong> Microservice deployment scorecard displaying stable vs degraded release proportions per service domain.
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 2 — DEEP RISK ANALYSIS
# =============================================================================
with tab_deep:
    st.markdown('<div class="section-header">1. Operational Telemetry Flow (CI/CD → Incident Match → Outcome)</div>', unsafe_allow_html=True)

    n_deploy = len(fdf)
    n_inc_m = fdf["matched_incident_id"].notnull().sum()
    n_no_inc = n_deploy - n_inc_m
    n_al = (fdf["outcome"] == "alerted").sum()
    n_rb2 = (fdf["outcome"] == "rolled_back").sum()

    labels = ["Total Deployments", "Matched Incident (2h)", "No Incident Matched", "Stable Outcome", "Alerted Outcome", "Rolled Back Outcome"]
    sources = [0, 0, 1, 1, 2]
    targets = [1, 2, 4, 5, 3]
    values = [n_inc_m, n_no_inc, n_al, n_rb2, n_no_inc]

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels,
                  color=["#6366f1", "#f59e0b", "#10b981", "#10b981", "#f59e0b", "#ef4444"]),
        link=dict(source=sources, target=targets, value=values,
                  color=["rgba(99,102,241,0.25)", "rgba(16,185,129,0.25)", "rgba(245,158,11,0.35)", "rgba(239,68,68,0.35)", "rgba(16,185,129,0.35)"])
    )])
    fig_sankey.update_layout(
        height=300, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor=plotly_bg, font=dict(color=plotly_font_color)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.markdown("""
    <div class="visual-desc">
        <strong>Description:</strong> Visualizes deployment execution flow through 2-hour temporal & semantic incident matching to final release classification.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="section-header">2. Composite Risk Score Distribution</div>', unsafe_allow_html=True)
        if "composite_risk_score" in fdf.columns:
            fig_risk_dist = px.histogram(
                fdf, x="composite_risk_score", color="outcome", nbins=20,
                color_discrete_map=OUTCOME_COLORS,
                labels={"composite_risk_score": "Composite Risk Score (0-100)", "count": "Frequency"}
            )
            fig_risk_dist.update_layout(
                height=280, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, font=dict(color=plotly_font_color),
                xaxis=dict(gridcolor=plotly_grid_color), yaxis=dict(gridcolor=plotly_grid_color)
            )
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        st.markdown("""
        <div class="visual-desc">
            <strong>Description:</strong> Frequency distribution of calculated risk scores, demonstrating elevated failure probability above 65.0 risk index.
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="section-header">3. Temporal Risk Matrix (Day vs Hour)</div>', unsafe_allow_html=True)
        heatmap_data = fdf.pivot_table(index="day_of_week", columns="deploy_hour", values="is_instability", aggfunc="mean").fillna(0) * 100
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = heatmap_data.reindex([d for d in days_order if d in heatmap_data.index])

        fig_heat = px.imshow(
            heatmap_data, labels=dict(x="Deploy Hour (UTC)", y="Day of Week", color="Instability %"),
            color_continuous_scale="Reds"
        )
        fig_heat.update_layout(
            height=280, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, font=dict(color=plotly_font_color),
            xaxis=dict(gridcolor=plotly_grid_color), yaxis=dict(gridcolor=plotly_grid_color)
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("""
        <div class="visual-desc">
            <strong>Description:</strong> Heatmap highlighting high-risk execution hours (e.g. Friday afternoons and off-hours) to guide change freeze policies.
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 3 — PIPELINE EXPLAINER
# =============================================================================
with tab_explainer:
    st.markdown('<div class="section-header">Data Engineering Pipeline Architecture</div>', unsafe_allow_html=True)
    
    steps = [
        ("1. Multi-Dataset Ingestion", "Ingests raw open operational datasets (UCI ServiceNow Incident Log, Kaggle CI/CD Logs, D2KLab GHA Runs) with automatic character encoding detection (utf-8, latin1, cp1252)."),
        ("2. Deployment Isolation & Service Derivation", "Filters pipeline execution stages where stage_name == 'Deploy' and derives canonical service names and environment targets."),
        ("3. Standardization & Deduplication", "Standardizes all timestamps to ISO 8601 UTC format, imputes missing priorities, and deduplicates state snapshots."),
        ("4. Heuristic 2-Hour Join Engine", "Matches deployment records to incident logs triggered within [T_deploy, T_deploy + 2.0h] with semantic category affinity."),
        ("5. Domain Feature Engineering", "Derives 16+ temporal, quality, ITSM, and composite release risk metrics (0-100 normalized index)."),
        ("6. SQLite Storage & Clean Data Layer", "Loads clean datasets into SQLite `data/release_risk.db`, creating SQL views and pre-aggregated summary tables.")
    ]

    for title, desc in steps:
        st.markdown(f"""
        <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:10px; padding:14px 18px; margin-bottom:10px;">
            <div style="font-weight:700; color:#6366f1; font-size:0.92rem;">{title}</div>
            <div style="font-size:0.85rem; color:var(--text-sub); margin-top:4px; line-height:1.45;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    if audit:
        st.markdown("---")
        st.markdown('<div class="section-header">Live Audit Reports</div>', unsafe_allow_html=True)
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("**Ingestion Audit Summary**")
            st.json(audit.get("ingestion", {}))
        with col_a2:
            st.markdown("**Heuristic Join Audit Summary**")
            st.json(audit.get("join", {}))

# =============================================================================
# TAB 4 — RAW DATA & SQL CLEAN DATA LAYER
# =============================================================================
with tab_raw:
    st.markdown('<div class="section-header">SQL Clean Data Layer Views & Aggregation Tables</div>', unsafe_allow_html=True)

    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "Active Deployments View",
        "Environment Risk View",
        "Incident MTTR View",
        "Daily Pre-Aggregated Table",
        "Processed Outcomes Table"
    ])

    with subtab1:
        if "vw_active_deployments" in db_views:
            st.dataframe(db_views["vw_active_deployments"], use_container_width=True)
            st.caption("SQLite View: `vw_active_deployments`")

    with subtab2:
        if "vw_risk_by_environment" in db_views:
            st.dataframe(db_views["vw_risk_by_environment"], use_container_width=True)
            st.caption("SQLite View: `vw_risk_by_environment`")

    with subtab3:
        if "vw_incident_resolution_metrics" in db_views:
            st.dataframe(db_views["vw_incident_resolution_metrics"], use_container_width=True)
            st.caption("SQLite View: `vw_incident_resolution_metrics`")

    with subtab4:
        if "agg_daily_release_risk" in db_views:
            st.dataframe(db_views["agg_daily_release_risk"], use_container_width=True)
            st.caption("Pre-Aggregated Summary Table: `agg_daily_release_risk`")

    with subtab5:
        st.dataframe(fdf, use_container_width=True)
        st.caption("Clean Processed Dataset: `data/processed/deployment_outcomes.csv`")

# =============================================================================
# TAB 5 — DATASET INTAKE & AUTOMATED INGESTION PIPELINE
# =============================================================================
with tab_intake:
    st.markdown('<div class="section-header">Dataset Intake & Ingestion Pipeline</div>', unsafe_allow_html=True)
    st.markdown("Upload raw operational datasets for 1-click end-to-end processing: schema validation, cleaning, feature engineering, and live database sync.")

    up_c1, up_c2 = st.columns([2, 1])
    with up_c1:
        uploaded_file = st.file_uploader("Select CSV Dataset File", type=["csv"])
    with up_c2:
        dataset_type = st.selectbox(
            "Target Dataset Type",
            [
                "ServiceNow Incident Event Log (UCI Schema)",
                "CI/CD Pipeline Logs (Kaggle Schema)",
                "GitHub Actions Workflow Runs (D2KLab Schema)",
                "Custom Deployment Telemetry Log"
            ]
        )

    if uploaded_file is not None:
        st.info(f"Selected File: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
        
        if st.button("Process & Ingest Dataset", type="primary", use_container_width=True):
            with st.spinner("Processing dataset..."):
                try:
                    target_filename = "incident_log.csv" if "Incident" in dataset_type else ("pipeline_logs.csv" if "CI/CD" in dataset_type else ("gha_workflow_runs.csv" if "GitHub" in dataset_type else uploaded_file.name))
                    save_path = os.path.join(PROJECT_ROOT, "data", "raw", target_filename)
                    
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"File saved to `data/raw/{target_filename}`")
                    
                    from scripts.data_ingestion import run_ingestion
                    run_ingestion()
                    from scripts.derive_deployments import run_derive_deployments
                    run_derive_deployments()
                    from scripts.cleaning import run_cleaning
                    run_cleaning()
                    from scripts.join_validation import run_join_validation
                    run_join_validation()
                    from scripts.feature_engineering import run_feature_engineering
                    run_feature_engineering()
                    from scripts.database_kpis import run_database_pipeline
                    run_database_pipeline()
                    
                    st.cache_data.clear()
                    st.balloons()
                    st.success("Automated Pipeline Completed Successfully! Dashboard updated.")
                    
                except Exception as ex:
                    st.error(f"Ingestion Pipeline Error: {str(ex)}")
