"""
Release Risk Analyzer -- Premium Dark UI (v6)
Fixes: transparent Plotly bg causing data to vanish; removed broken theme toggle;
upgraded charts; richer descriptions.
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

st.set_page_config(
    page_title="ReleaseGuard | Release Risk Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Data Loaders ─────────────────────────────────────────────────────────────
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
            for name in [
                "vw_active_deployments",
                "vw_risk_by_environment",
                "vw_incident_resolution_metrics",
                "agg_daily_release_risk",
            ]:
                try:
                    views[name] = pd.read_sql_query(f"SELECT * FROM {name}", conn)
                except Exception:
                    pass
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
        "schema": os.path.join(PROJECT_ROOT, "output", "database_schema_audit.json"),
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

# ─── Theme Selection & Design Tokens ─────────────────────────────────────────
if "app_theme" not in st.session_state:
    st.session_state["app_theme"] = "Dark"

with st.sidebar:
    st.markdown(
        """
        <div style="padding:6px 0 12px">
            <div style="font-size:1.45rem;font-weight:800;letter-spacing:-0.03em;">🛡️ RELEASEGUARD</div>
            <div style="font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;opacity:0.75;">Release Risk Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    theme_choice = st.radio(
        "Appearance",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state["app_theme"] == "Dark" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["app_theme"] = "Dark" if "Dark" in theme_choice else "Light"
    is_dark = st.session_state["app_theme"] == "Dark"

if is_dark:
    BG_COLOR = "#0f172a"
    SIDEBAR_BG = "#0b1120"
    CARD_BG = "#1e293b"
    CARD_BORDER = "#334155"
    TEXT_MAIN = "#f8fafc"
    TEXT_SUB = "#cbd5e1"
    TEXT_MUTED = "#94a3b8"
    ACCENT = "#818cf8"
    ACCENT2 = "#38bdf8"
    GRID_COLOR = "#2d3f55"
    FONT_COLOR = "#cbd5e1"
    HERO_GRADIENT = "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)"
    VISUAL_DESC_BG = "rgba(129, 140, 248, 0.08)"
    SHADOW = "0 6px 20px rgba(0, 0, 0, 0.35)"
    BAR_TOTAL_COLOR = "#334155"
    BAR_TOTAL_BORDER = "#475569"
else:
    BG_COLOR = "#f8fafc"
    SIDEBAR_BG = "#ffffff"
    CARD_BG = "#ffffff"
    CARD_BORDER = "#e2e8f0"
    TEXT_MAIN = "#0f172a"
    TEXT_SUB = "#334155"
    TEXT_MUTED = "#64748b"
    ACCENT = "#4f46e5"
    ACCENT2 = "#0284c7"
    GRID_COLOR = "#e2e8f0"
    FONT_COLOR = "#334155"
    HERO_GRADIENT = "linear-gradient(135deg, #eef2ff 0%, #ffffff 100%)"
    VISUAL_DESC_BG = "rgba(79, 70, 229, 0.05)"
    SHADOW = "0 4px 16px rgba(0, 0, 0, 0.06)"
    BAR_TOTAL_COLOR = "#cbd5e1"
    BAR_TOTAL_BORDER = "#94a3b8"

OUTCOME_COLORS = {
    "stable": "#10b981",
    "alerted": "#f59e0b",
    "rolled_back": "#ef4444",
}


def base_layout(**overrides):
    """Shared Plotly layout with solid backgrounds so charts are always readable in both modes."""
    d = dict(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif", size=12),
        margin=dict(t=28, b=28, l=36, r=36),
    )
    d.update(overrides)
    return d


XAXIS_STYLE = dict(gridcolor=GRID_COLOR, zeroline=False, linecolor=CARD_BORDER, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR))
YAXIS_STYLE = dict(gridcolor=GRID_COLOR, zeroline=False, linecolor=CARD_BORDER, tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR))

# ─── Sidebar Filters ──────────────────────────────────────────────────────────
with st.sidebar:
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
    date_range = st.date_input(
        "Date Window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if "composite_risk_score" in df_raw.columns:
        min_r = float(df_raw["composite_risk_score"].min())
        max_r = float(df_raw["composite_risk_score"].max())
        risk_range = st.slider("Risk Score", 0.0, 100.0, (min_r, max_r), step=1.0)
    else:
        risk_range = (0.0, 100.0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Reset Filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.caption(f"Records Loaded: **{len(df_raw)}**")
    st.caption("Backend: SQLite `data/release_risk.db`")

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap");
html, body, [class*="css"] {{ font-family: "Inter", sans-serif; }}

/* Canvas styling */
.stApp {{
    background-color: {BG_COLOR} !important;
    color: {TEXT_MAIN} !important;
}}
header[data-testid="stHeader"] {{
    background-color: {BG_COLOR} !important;
}}
[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid {CARD_BORDER} !important;
}}

.kpi-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
    padding: 20px 18px;
    box-shadow: {SHADOW};
    height: 126px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.kpi-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {TEXT_MUTED};
    margin-bottom: 5px;
}}
.kpi-value {{
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 5px;
}}
.kpi-sub {{
    font-size: 0.74rem;
    color: {TEXT_MUTED};
    font-weight: 500;
}}

.hero-card {{
    background: {HERO_GRADIENT};
    border: 1px solid {CARD_BORDER};
    border-radius: 18px;
    padding: 32px 36px;
    box-shadow: {SHADOW};
}}
.hero-badge {{
    display: inline-block;
    padding: 4px 12px;
    background: rgba(99, 102, 241, 0.14);
    color: {ACCENT};
    font-size: 0.70rem;
    font-weight: 700;
    border-radius: 20px;
    letter-spacing: 0.09em;
    margin-bottom: 14px;
    text-transform: uppercase;
}}
.hero-title {{
    font-size: 2.3rem;
    font-weight: 800;
    color: {TEXT_MAIN} !important;
    margin: 0 0 10px 0;
    letter-spacing: -0.025em;
    line-height: 1.15;
}}
.hero-sub {{
    color: {TEXT_SUB} !important;
    font-size: 0.98rem;
    margin: 0;
    line-height: 1.65;
}}

.visual-desc {{
    background: {VISUAL_DESC_BG};
    border-left: 3px solid {ACCENT};
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 4px 0 2px 0;
    font-size: 0.83rem;
    color: {TEXT_SUB};
    line-height: 1.6;
}}
.visual-desc .desc-title {{
    font-size: 0.78rem;
    font-weight: 700;
    color: {ACCENT};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}}
.visual-desc p {{
    margin: 0 0 6px 0;
    color: {TEXT_SUB} !important;
}}
.visual-desc strong {{
    color: {TEXT_MAIN} !important;
    font-weight: 600;
}}

.section-header {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {TEXT_MAIN} !important;
    margin: 6px 0 12px 0;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.section-header::before {{
    content: "";
    display: inline-block;
    width: 3px;
    height: 1.05rem;
    background: {ACCENT};
    border-radius: 2px;
}}

.step-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    box-shadow: {SHADOW};
}}
.step-card:hover {{
    border-color: {ACCENT};
}}
.step-title {{
    font-weight: 700;
    color: {ACCENT};
    font-size: 0.90rem;
    margin-bottom: 6px;
}}
.step-desc {{
    font-size: 0.83rem;
    color: {TEXT_SUB} !important;
    line-height: 1.55;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 8px 16px;
    color: {TEXT_SUB};
}}
.stTabs [aria-selected="true"] {{
    background-color: {CARD_BG} !important;
    color: {ACCENT} !important;
    font-weight: 700;
    border-bottom: 2px solid {ACCENT} !important;
}}
</style>
"""
,
    unsafe_allow_html=True,
)

# ─── Filter Data ──────────────────────────────────────────────────────────────
fdf = df_raw[
    df_raw["service"].isin(sel_services)
    & df_raw["environment"].isin(sel_envs)
    & df_raw["outcome"].isin(sel_outcomes)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    fdf = fdf[
        (fdf["deploy_dt"].dt.date >= date_range[0])
        & (fdf["deploy_dt"].dt.date <= date_range[1])
    ]

if "composite_risk_score" in fdf.columns:
    fdf = fdf[
        (fdf["composite_risk_score"] >= risk_range[0])
        & (fdf["composite_risk_score"] <= risk_range[1])
    ]

if fdf.empty:
    st.warning("No deployment records match the selected filter criteria. Please broaden your filter selection.")
    if st.button("Reset Filters to View Full Dataset"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ─── Metrics ──────────────────────────────────────────────────────────────────
n_total = len(fdf)
n_rb = (fdf["outcome"] == "rolled_back").sum()
n_alert = (fdf["outcome"] == "alerted").sum()
n_stable = (fdf["outcome"] == "stable").sum()
rb_rate = (n_rb / n_total * 100) if n_total else 0.0
alert_rate = (n_alert / n_total * 100) if n_total else 0.0
instab = ((n_rb + n_alert) / n_total * 100) if n_total else 0.0
valid_ttr = fdf[fdf["time_to_resolution_hours"].notnull()]["time_to_resolution_hours"]
mttr = valid_ttr.mean() if len(valid_ttr) else 0.0
avg_risk = fdf["composite_risk_score"].mean() if "composite_risk_score" in fdf.columns else 0.0
p90_risk = fdf["composite_risk_score"].quantile(0.9) if "composite_risk_score" in fdf.columns else 0.0

# ─── Hero ─────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([1.6, 1])
with col_h1:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-badge">Release Risk Intelligence Platform</div>
            <h1 class="hero-title">AI-Powered Release<br>Risk Analyzer</h1>
            <p class="hero-sub">
                Automated production risk forecasting, ITSM incident correlation, and
                CI/CD quality gate enforcement — powered by open operational datasets
                and a 2-hour temporal join engine.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_h2:
    hero_img_path = os.path.join(PROJECT_ROOT, "public", "hero_illustration.jpg")
    if os.path.exists(hero_img_path):
        st.image(hero_img_path, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Navigation Tabs ──────────────────────────────────────────────────────────
tab_overview, tab_deep, tab_explainer, tab_raw, tab_intake = st.tabs(
    [
        "📊  Overview Dashboard",
        "🔬  Deep Risk Analysis",
        "🔧  Pipeline Explainer",
        "🗄️  SQL Clean Data Layer",
        "📥  Dataset Intake Pipeline",
    ]
)

# =============================================================================
# TAB 1 — OVERVIEW DASHBOARD
# =============================================================================
with tab_overview:

    # KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Total Deployments</div>
            <div class="kpi-value" style="color:{ACCENT}">{n_total:,}</div>
            <div class="kpi-sub">Filtered release volume</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Rollback Rate</div>
            <div class="kpi-value" style="color:#ef4444">{rb_rate:.1f}%</div>
            <div class="kpi-sub">{n_rb:,} hard failures reverted</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Incident Alert Rate</div>
            <div class="kpi-value" style="color:#f59e0b">{alert_rate:.1f}%</div>
            <div class="kpi-sub">{n_alert:,} triggered incidents</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with k4:
        clr = "#ef4444" if instab > 20 else ("#f59e0b" if instab > 10 else "#10b981")
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Instability Rate</div>
            <div class="kpi-value" style="color:{clr}">{instab:.1f}%</div>
            <div class="kpi-sub">{n_rb + n_alert:,} non-stable releases</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Mean MTTR</div>
            <div class="kpi-value" style="color:{ACCENT2}">{mttr:.1f}<span style="font-size:0.85rem"> hrs</span></div>
            <div class="kpi-sub">Avg incident resolution time</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with k6:
        rclr = "#ef4444" if avg_risk > 65 else ("#f59e0b" if avg_risk > 40 else "#10b981")
        st.markdown(
            f"""<div class="kpi-card">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-value" style="color:{rclr}">{avg_risk:.1f}</div>
            <div class="kpi-sub">P90 threshold: {p90_risk:.0f}</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Donut + Daily Trend
    c1, c2 = st.columns([1, 1.9])

    with c1:
        st.markdown('<div class="section-header">Outcome Distribution</div>', unsafe_allow_html=True)
        oc = fdf["outcome"].value_counts().reset_index()
        oc.columns = ["Outcome", "Count"]
        fig_donut = px.pie(
            oc, values="Count", names="Outcome",
            color="Outcome", color_discrete_map=OUTCOME_COLORS, hole=0.62,
        )
        fig_donut.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=11,
            marker=dict(line=dict(color=CARD_BG, width=3)),
        )
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5,
                font=dict(color=FONT_COLOR, size=11),
            ),
            height=300,
            **base_layout(margin=dict(t=10, b=40, l=10, r=10)),
        )
        fig_donut.add_annotation(
            text=f"<b>{n_stable:,}</b><br>Stable",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=TEXT_MAIN),
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown(
            """
            <div class="visual-desc">
                <div class="desc-title">What this shows</div>
                <p>Every deployment in the filtered date window is classified into one of three outcome
                buckets. <strong>Stable</strong> means no incident was raised within 2 hours of the release.
                <strong>Alerted</strong> means an ITSM ticket was created inside that window.
                <strong>Rolled Back</strong> means the release was actively reverted.</p>
                <p>The number in the centre is the raw count of clean (stable) releases.
                If the red or amber segment exceeds 15–20% of the total, it is a direct signal
                that testing gates or deployment procedures need tightening for the selected services.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="section-header">Daily Deployment Volume &amp; Instability Trend</div>',
            unsafe_allow_html=True,
        )
        daily = (
            fdf.groupby(fdf["deploy_dt"].dt.date)
            .agg(total=("deployment_id", "count"), unstable=("is_instability", "sum"))
            .reset_index()
        )
        daily["instab_pct"] = (daily["unstable"] / daily["total"] * 100).round(1)

        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=daily["deploy_dt"], y=daily["total"],
                name="Total Releases",
                marker_color=BAR_TOTAL_COLOR,
                marker_line_color=BAR_TOTAL_BORDER,
                marker_line_width=1,
                opacity=0.85,
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=daily["deploy_dt"], y=daily["instab_pct"],
                name="Instability %", yaxis="y2",
                mode="lines+markers",
                line=dict(color="#ef4444", width=2.5, shape="spline"),
                marker=dict(size=5, color="#ef4444", line=dict(color=CARD_BG, width=1.5)),
                fill="tozeroy",
                fillcolor="rgba(239,68,68,0.08)",
            )
        )
        fig_trend.update_layout(
            yaxis=dict(title="Release Count", **YAXIS_STYLE),
            yaxis2=dict(
                title="Instability %", overlaying="y", side="right",
                range=[0, 100], gridcolor="rgba(0,0,0,0)", zeroline=False,
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color=FONT_COLOR, size=11),
            ),
            height=300,
            xaxis=XAXIS_STYLE,
            **base_layout(margin=dict(t=24, b=28, l=40, r=50)),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown(
            """
            <div class="visual-desc">
                <div class="desc-title">What this shows</div>
                <p>The <strong>grey bars</strong> show total deployments pushed each calendar day.
                The <strong>red filled line</strong> on the right axis tracks the daily instability rate —
                the percentage of those deployments that triggered alerts or rollbacks.</p>
                <p>Look for days where the red line spikes despite moderate bar height: those are days
                where release quality fell, not just volume. Conversely, tall grey bars with a flat red
                line confirm that your process scales safely under high throughput.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Service Scorecard
    st.markdown('<div class="section-header">Service Risk Scorecard</div>', unsafe_allow_html=True)
    svc = (
        fdf.groupby("service")
        .agg(
            total=("deployment_id", "count"),
            rollbacks=("has_rollback", "sum"),
            alerts=("outcome", lambda x: (x == "alerted").sum()),
            stables=("outcome", lambda x: (x == "stable").sum()),
        )
        .reset_index()
    )
    svc["instab_pct"] = ((svc["rollbacks"] + svc["alerts"]) / svc["total"] * 100).round(1)
    svc = svc.sort_values("instab_pct", ascending=False)

    fig_svc = go.Figure()
    fig_svc.add_trace(
        go.Bar(y=svc["service"], x=svc["stables"], name="Stable",
               orientation="h", marker_color="#10b981",
               marker_line_color=CARD_BG, marker_line_width=1.5)
    )
    fig_svc.add_trace(
        go.Bar(y=svc["service"], x=svc["alerts"], name="Alerted",
               orientation="h", marker_color="#f59e0b",
               marker_line_color=CARD_BG, marker_line_width=1.5)
    )
    fig_svc.add_trace(
        go.Bar(y=svc["service"], x=svc["rollbacks"], name="Rolled Back",
               orientation="h", marker_color="#ef4444",
               marker_line_color=CARD_BG, marker_line_width=1.5)
    )
    fig_svc.update_layout(
        barmode="stack",
        xaxis=dict(title="Deployment Count", **XAXIS_STYLE),
        yaxis=dict(title="", autorange="reversed", **YAXIS_STYLE),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
            font=dict(color=FONT_COLOR, size=11),
        ),
        height=max(280, len(svc) * 38),
        **base_layout(margin=dict(t=36, b=28, l=140, r=36)),
    )
    st.plotly_chart(fig_svc, use_container_width=True)
    st.markdown(
        """
        <div class="visual-desc">
            <div class="desc-title">What this shows</div>
            <p>Each row is a microservice domain. Bars are sorted <strong>top-to-bottom by highest
            instability rate</strong>, so the most troubled services are always at the top. The stacked
            green, amber, and red segments show the exact count of stable, alerted, and rolled-back
            deployments for each service.</p>
            <p>A service whose bar is dominated by red and amber has a systemic reliability issue
            and should be the first target for root-cause analysis, expanded staging coverage,
            or a temporary deployment freeze pending a quality review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# TAB 2 — DEEP RISK ANALYSIS
# =============================================================================
with tab_deep:

    # Sankey
    st.markdown(
        '<div class="section-header">1. Deployment Flow — CI/CD to Outcome (Sankey)</div>',
        unsafe_allow_html=True,
    )
    n_inc_m = fdf["matched_incident_id"].notnull().sum()
    n_no_inc = len(fdf) - n_inc_m
    n_al = (fdf["outcome"] == "alerted").sum()
    n_rb2 = (fdf["outcome"] == "rolled_back").sum()

    labels = ["All Deployments", "Incident Matched", "No Incident", "Stable", "Alerted", "Rolled Back"]
    sources = [0, 0, 1, 1, 2]
    targets = [1, 2, 4, 5, 3]
    values = [n_inc_m, n_no_inc, n_al, n_rb2, n_no_inc]
    node_colors = ["#818cf8", "#f59e0b", "#10b981", "#10b981", "#f59e0b", "#ef4444"]
    link_colors = [
        "rgba(129,140,248,0.30)",
        "rgba(16,185,129,0.25)",
        "rgba(245,158,11,0.35)",
        "rgba(239,68,68,0.40)",
        "rgba(16,185,129,0.30)",
    ]

    fig_sankey = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=20, thickness=22,
                    line=dict(color=CARD_BORDER, width=1),
                    label=labels,
                    color=node_colors,
                    hovertemplate="%{label}: %{value:,}<extra></extra>",
                ),
                link=dict(source=sources, target=targets, value=values, color=link_colors),
            )
        ]
    )
    fig_sankey.update_layout(height=320, **base_layout(margin=dict(t=14, b=14, l=14, r=14)))
    st.plotly_chart(fig_sankey, use_container_width=True)
    st.markdown(
        """
        <div class="visual-desc">
            <div class="desc-title">What this shows</div>
            <p>This Sankey diagram traces every deployment left-to-right through the pipeline's
            <strong>2-hour temporal incident matching</strong> step. Flows entering "Incident Matched"
            were paired with a ServiceNow ticket raised within 2 hours of the release. Flows entering
            "No Incident" had no correlated ticket in that window.</p>
            <p>Ribbon width is proportional to volume. A thick red ribbon from "Incident Matched" to
            "Rolled Back" means matched incidents frequently escalated to full reversions — a signal to
            improve incident response speed. A thick green flow from "No Incident" to "Stable" confirms
            your unmatched deploys are genuinely healthy and not merely unmonitored.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    cl, cr = st.columns(2)

    # Violin chart
    with cl:
        st.markdown(
            '<div class="section-header">2. Risk Score Distribution by Outcome</div>',
            unsafe_allow_html=True,
        )
        if "composite_risk_score" in fdf.columns:
            fig_v = go.Figure()
            for outcome, color in OUTCOME_COLORS.items():
                sub = fdf[fdf["outcome"] == outcome]["composite_risk_score"].dropna()
                if len(sub) == 0:
                    continue
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                fill = f"rgba({r},{g},{b},0.15)"
                fig_v.add_trace(
                    go.Violin(
                        y=sub,
                        name=outcome.replace("_", " ").title(),
                        box_visible=True,
                        meanline_visible=True,
                        line_color=color,
                        fillcolor=fill,
                        opacity=0.85,
                        points="outliers",
                        marker=dict(color=color, size=3, opacity=0.6),
                        hoveron="violins+points",
                    )
                )
            fig_v.update_layout(
                yaxis=dict(title="Composite Risk Score (0–100)", **YAXIS_STYLE),
                xaxis=dict(title="Outcome", **XAXIS_STYLE),
                violingap=0.08,
                violinmode="overlay",
                showlegend=False,
                height=320,
                **base_layout(margin=dict(t=24, b=28, l=50, r=20)),
            )
            st.plotly_chart(fig_v, use_container_width=True)
        st.markdown(
            """
            <div class="visual-desc">
                <div class="desc-title">What this shows</div>
                <p>Each violin shows the <strong>full probability distribution</strong> of composite risk
                scores for one outcome group. The inner box-plot shows the median, interquartile range,
                and whiskers. The wider shaded shape reveals where most scores are concentrated — a wide
                belly means many deployments landed at that score range.</p>
                <p>If the <strong>Rolled Back</strong> violin sits noticeably higher on the score axis
                than Stable, the risk model is successfully separating failures from successes.
                Heavy overlap between Stable and Rolled Back distributions suggests the model needs
                additional features or retraining to improve discriminative power.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Heatmap
    with cr:
        st.markdown(
            '<div class="section-header">3. Temporal Risk Matrix — Day × Deploy Hour</div>',
            unsafe_allow_html=True,
        )
        hm = (
            fdf.pivot_table(
                index="day_of_week",
                columns="deploy_hour",
                values="is_instability",
                aggfunc="mean",
            ).fillna(0)
            * 100
        )
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hm = hm.reindex([d for d in days_order if d in hm.index])

        fig_heat = px.imshow(
            hm,
            labels=dict(x="Deploy Hour (UTC)", y="Day of Week", color="Instability %"),
            color_continuous_scale="RdYlGn_r",
            zmin=0, zmax=100,
            text_auto=".0f",
        )
        fig_heat.update_traces(textfont=dict(size=10, color="white"))
        fig_heat.update_layout(
            coloraxis_colorbar=dict(
                title="Instab %",
                tickfont=dict(color=FONT_COLOR),
                title_font=dict(color=FONT_COLOR),
                thickness=12,
            ),
            xaxis=dict(
                title="Deploy Hour (UTC)",
                tickfont=dict(color=FONT_COLOR),
                title_font=dict(color=FONT_COLOR),
            ),
            yaxis=dict(title="", tickfont=dict(color=FONT_COLOR)),
            height=320,
            **base_layout(margin=dict(t=24, b=28, l=90, r=20)),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown(
            """
            <div class="visual-desc">
                <div class="desc-title">What this shows</div>
                <p>Each cell represents a specific <strong>weekday × hour-of-day combination</strong>
                (UTC clock). The value inside and the cell colour (green = safe, yellow = caution,
                red = danger) both encode the percentage of deployments at that slot that became
                unstable. Empty slots appear at the dataset minimum.</p>
                <p>Common risk patterns: Friday afternoon clusters (reviewer attention drops),
                late-night slots (on-call fatigue, no QA), Monday-morning deploys (post-weekend
                config drift). These findings directly inform <strong>change-freeze windows</strong>
                and help schedule high-risk releases during peak-coverage hours.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Environment comparison
    st.markdown(
        '<div class="section-header">4. Environment Risk Comparison</div>',
        unsafe_allow_html=True,
    )
    env_agg = (
        fdf.groupby("environment")
        .agg(total=("deployment_id", "count"), instab=("is_instability", "sum"))
        .reset_index()
    )
    env_agg["instab_pct"] = (env_agg["instab"] / env_agg["total"] * 100).round(1)

    fig_env = go.Figure()
    fig_env.add_trace(
        go.Bar(
            x=env_agg["environment"],
            y=env_agg["instab_pct"],
            marker=dict(
                color=env_agg["instab_pct"],
                colorscale=[[0, "#10b981"], [0.4, "#f59e0b"], [1.0, "#ef4444"]],
                cmin=0, cmax=50,
                line=dict(color=CARD_BG, width=1.5),
            ),
            text=env_agg["instab_pct"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
            textfont=dict(color=FONT_COLOR, size=11),
        )
    )
    max_val = env_agg["instab_pct"].max() if not env_agg.empty else 10
    fig_env.update_layout(
        xaxis=dict(title="Environment", **XAXIS_STYLE),
        yaxis=dict(title="Instability Rate (%)", range=[0, max_val * 1.3 + 1], **YAXIS_STYLE),
        showlegend=False,
        height=300,
        **base_layout(margin=dict(t=28, b=28, l=50, r=20)),
    )
    st.plotly_chart(fig_env, use_container_width=True)
    st.markdown(
        """
        <div class="visual-desc">
            <div class="desc-title">What this shows</div>
            <p>Each bar represents a deployment environment such as <strong>production, staging,
            or canary</strong>. Bar height and colour (green through red) both encode the instability
            rate — the percentage of releases in that environment that resulted in incidents or rollbacks.
            The exact percentage is labelled above each bar for precision.</p>
            <p>A production bar significantly taller than staging indicates that pre-production
            environments do not accurately replicate production load, configuration, or data volumes.
            This is a direct justification for investment in environment parity and progressive
            canary-release strategies before fully graduating a release.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# TAB 3 — PIPELINE EXPLAINER
# =============================================================================
with tab_explainer:
    st.markdown(
        '<div class="section-header">Data Engineering Pipeline Architecture</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{TEXT_SUB};font-size:0.88rem;margin-bottom:18px;'>"
        "Six sequential stages transform raw, heterogeneous operational datasets into a clean, "
        "feature-rich SQLite analytical layer ready for risk scoring and visualisation.</p>",
        unsafe_allow_html=True,
    )

    steps = [
        (
            "1. Multi-Dataset Ingestion",
            "Ingests raw open operational datasets — UCI ServiceNow Incident Log, Kaggle CI/CD Logs, "
            "and D2KLab GitHub Actions runs — with automatic character-encoding detection "
            "(UTF-8, Latin-1, CP1252 fallback). Each source is validated against a schema contract before proceeding.",
        ),
        (
            "2. Deployment Isolation and Service Derivation",
            "Filters CI/CD pipeline executions to rows where stage_name == Deploy. "
            "Canonical service names and target environment labels (production, staging, canary) "
            "are derived from raw pipeline metadata using regex heuristics.",
        ),
        (
            "3. Standardisation and Deduplication",
            "All timestamps are normalised to ISO 8601 UTC. Missing incident priorities are imputed "
            "via a median-per-category strategy. Duplicate state snapshots (same deployment re-reported "
            "multiple times) are collapsed to a single authoritative record.",
        ),
        (
            "4. Heuristic 2-Hour Join Engine",
            "Matches each deployment record to incident log entries triggered within [T_deploy, T_deploy + 2.0 h]. "
            "A secondary semantic-affinity filter ensures the incident category is plausibly related "
            "to the deployed service, reducing false positive matches significantly.",
        ),
        (
            "5. Domain Feature Engineering",
            "Derives 16+ features: deploy hour, day-of-week, has_rollback flag, matched_incident_id, "
            "time_to_resolution_hours, and the headline composite_risk_score (0–100 normalised index "
            "weighting recency, incident severity, service tier, and environment).",
        ),
        (
            "6. SQLite Storage and Clean Data Layer",
            "Writes the enriched dataset to SQLite data/release_risk.db. Creates SQL views "
            "(vw_active_deployments, vw_risk_by_environment, vw_incident_resolution_metrics) "
            "and a pre-aggregated daily summary table (agg_daily_release_risk) for fast dashboard queries.",
        ),
    ]

    for title, desc in steps:
        st.markdown(
            f"""<div class="step-card">
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>""",
            unsafe_allow_html=True,
        )

    if audit:
        st.markdown("---")
        st.markdown('<div class="section-header">Live Audit Reports</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            st.markdown(
                f"<p style='color:{TEXT_SUB};font-size:0.83rem;font-weight:600;'>Ingestion Audit Summary</p>",
                unsafe_allow_html=True,
            )
            st.json(audit.get("ingestion", {}))
        with ca2:
            st.markdown(
                f"<p style='color:{TEXT_SUB};font-size:0.83rem;font-weight:600;'>Heuristic Join Audit Summary</p>",
                unsafe_allow_html=True,
            )
            st.json(audit.get("join", {}))


# =============================================================================
# TAB 4 — SQL CLEAN DATA LAYER
# =============================================================================
with tab_raw:
    st.markdown(
        '<div class="section-header">SQL Clean Data Layer — Views and Aggregation Tables</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{TEXT_SUB};font-size:0.86rem;margin-bottom:14px;'>"
        "Browse the SQLite views and pre-aggregated tables that power this dashboard. "
        "These are the clean, validated outputs of the 6-stage pipeline.</p>",
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4, s5 = st.tabs(
        ["Active Deployments", "Environment Risk", "Incident MTTR", "Daily Aggregates", "Processed Outcomes"]
    )

    with s1:
        if "vw_active_deployments" in db_views:
            st.dataframe(db_views["vw_active_deployments"], use_container_width=True)
            st.caption("View: vw_active_deployments — deployments currently in an active or running state.")
    with s2:
        if "vw_risk_by_environment" in db_views:
            st.dataframe(db_views["vw_risk_by_environment"], use_container_width=True)
            st.caption("View: vw_risk_by_environment — aggregated risk and instability metrics grouped by environment.")
    with s3:
        if "vw_incident_resolution_metrics" in db_views:
            st.dataframe(db_views["vw_incident_resolution_metrics"], use_container_width=True)
            st.caption("View: vw_incident_resolution_metrics — MTTR and SLA metrics per service and priority tier.")
    with s4:
        if "agg_daily_release_risk" in db_views:
            st.dataframe(db_views["agg_daily_release_risk"], use_container_width=True)
            st.caption("Table: agg_daily_release_risk — daily rollup of deployment counts and composite risk scores.")
    with s5:
        st.dataframe(fdf, use_container_width=True)
        st.caption(
            "Clean Processed Dataset: data/processed/deployment_outcomes.csv — filtered by sidebar controls."
        )


# =============================================================================
# TAB 5 — DATASET INTAKE PIPELINE
# =============================================================================
with tab_intake:
    st.markdown(
        '<div class="section-header">Dataset Intake and Automated Ingestion Pipeline</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{TEXT_SUB};font-size:0.88rem;max-width:700px;margin-bottom:22px;line-height:1.65;'>"
        "Upload a raw operational CSV to trigger the full end-to-end pipeline: "
        "schema validation, cleaning, feature engineering, and SQLite sync. "
        "The dashboard refreshes automatically on completion.</p>",
        unsafe_allow_html=True,
    )

    uc1, uc2 = st.columns([2, 1])
    with uc1:
        uploaded_file = st.file_uploader("Select CSV Dataset File", type=["csv"])
    with uc2:
        dataset_type = st.selectbox(
            "Target Dataset Type",
            [
                "ServiceNow Incident Event Log (UCI Schema)",
                "CI/CD Pipeline Logs (Kaggle Schema)",
                "GitHub Actions Workflow Runs (D2KLab Schema)",
                "Custom Deployment Telemetry Log",
            ],
        )

    with st.expander("📋 View Expected Columns & Formats for Selected Dataset Type"):
        st.markdown(
            """
            - **ServiceNow Incident Log**: `number`, `incident_state`, `opened_at`, `resolved_at`, `closed_at`, `priority`, `category`, `assignment_group`
            - **CI/CD Pipeline Logs**: `pipeline_id`, `stage_name` (Deploy), `job_name`, `status`, `timestamp`, `commit_id`, `branch`, `environment`
            - **GitHub Actions Runs**: `workflow_run_id`, `repository`, `workflow_name`, `event_trigger`, `status`, `conclusion`, `created_at`
            *(Note: Column names are case-insensitive and common aliases like `created_at`, `timestamp`, `open_time`, etc. are automatically mapped).*
            """
        )

    if uploaded_file is not None:
        st.info(f"Selected: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
        if st.button("Process and Ingest Dataset", type="primary", use_container_width=True):
            with st.spinner("Running pipeline..."):
                try:
                    target_filename = (
                        "incident_log.csv"
                        if "Incident" in dataset_type
                        else "pipeline_logs.csv"
                        if "CI/CD" in dataset_type
                        else "gha_workflow_runs.csv"
                        if "GitHub" in dataset_type
                        else uploaded_file.name
                    )
                    save_path = os.path.join(PROJECT_ROOT, "data", "raw", target_filename)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"File saved to data/raw/{target_filename}")

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
                    st.success("Pipeline completed successfully — dashboard data refreshed.")
                except Exception as ex:
                    st.error(f"Ingestion Pipeline Error: {str(ex)}")
