"""
Step 7: Release Risk Analyzer - Interactive Streamlit Dashboard (v2)

Enhanced with:
- Multi-tab navigation: Overview, Deep Analysis, Pipeline Explainer, Raw Data
- Pipeline Explainer tab: visual step-by-step walkthrough of what each script does
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
def load_audit_reports():
    reports = {}
    for name, path in [
        ("ingestion", "output/ingestion_audit_report.json"),
        ("join",      "output/join_audit_report.json"),
        ("kpi",       "output/kpi_summary.json"),
    ]:
        if os.path.exists(path):
            with open(path) as f:
                reports[name] = json.load(f)
    return reports

try:
    df_raw = load_data()
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
    st.caption(f"🗄️ Source: `data/release_risk.db`")

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
        End-to-end CI/CD deployment intelligence: connecting pipeline telemetry,
        ServiceNow ITSM incidents & synthetic rollback events into one unified risk view.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview Dashboard",
    "🔬 Deep Analysis",
    "🗺️ Pipeline Explainer",
    "📋 Raw Data & Audit"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "Total Deployments", f"{n_total:,}", "Evaluated release events", "#f1f5f9"),
        (c2, "Rollback Rate",     f"{rb_rate:.1f}%",  f"{n_rb} rollbacks", "#f87171"),
        (c3, "Post-Deploy Alerts",f"{alert_rate:.1f}%",f"{n_alert} 2-hr window incidents","#fbbf24"),
        (c4, "Instability Rate",  f"{instab:.1f}%",   "Rollbacks + Alerts", "#c084fc"),
        (c5, "Mean MTTR",         f"{mttr:.1f}h",     "Avg incident resolution time","#38bdf8"),
    ]
    for col, label, val, sub, color in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Outcome Donut + Gauge row ──
    oa, ob, oc = st.columns([2, 2, 1.5])

    with oa:
        st.markdown('<div class="section-header">🎯 Deployment Outcome Distribution</div>', unsafe_allow_html=True)
        donut_df = fdf["outcome"].value_counts().reset_index()
        donut_df.columns = ["outcome", "count"]
        fig_donut = px.pie(
            donut_df, names="outcome", values="count",
            color="outcome", color_discrete_map=OUTCOME_COLORS,
            hole=0.55
        )
        fig_donut.update_traces(textposition='outside', textfont_size=13)
        fig_donut.update_layout(
            template="plotly_dark", height=300,
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(l=20, r=20, t=20, b=40),
            annotations=[dict(text=f"<b>{n_total}</b><br>Total", x=0.5, y=0.5,
                              font_size=16, showarrow=False, font_color="#f1f5f9")]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> Every deployment ends in one of three states:
            <strong>stable</strong> (no post-release incident), <strong>alerted</strong>
            (an incident was opened within 2 hours of deploy), or <strong>rolled_back</strong>
            (an explicit rollback event was triggered). This donut shows the proportion of each.
        </div>""", unsafe_allow_html=True)

    with ob:
        st.markdown('<div class="section-header">📈 Instability Trend Over Time</div>', unsafe_allow_html=True)
        trend = fdf.copy()
        trend["date"] = trend["deploy_dt"].dt.date
        dt = trend.groupby("date").agg(
            total=("deployment_id","count"),
            unstable=("is_instability","sum"),
        ).reset_index()
        dt["rate"] = (dt["unstable"] / dt["total"] * 100).round(1)

        fig_tr = go.Figure()
        fig_tr.add_trace(go.Scatter(
            x=dt["date"], y=dt["rate"],
            mode="lines+markers", name="Instability %",
            line=dict(color="#818cf8", width=2.5),
            fill="tozeroy", fillcolor="rgba(129,140,248,0.1)",
            marker=dict(size=7, color="#c084fc")
        ))
        fig_tr.add_trace(go.Bar(
            x=dt["date"], y=dt["total"], name="Deploy Count",
            marker_color="rgba(100,116,139,0.25)", yaxis="y2"
        ))
        fig_tr.update_layout(
            template="plotly_dark", height=300,
            margin=dict(l=10,r=10,t=10,b=10),
            yaxis=dict(title="Instability %", range=[0, 110]),
            yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Deployments"),
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig_tr, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> Daily deployment volume (grey bars, right axis)
            vs daily instability rate % (purple line, left axis).
            Spikes in the line mean risky release windows — great for spotting patterns.
        </div>""", unsafe_allow_html=True)

    with oc:
        st.markdown('<div class="section-header">⚡ Instability Gauge</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(instab, 1),
            delta={"reference": 15, "suffix": "%"},
            number={"suffix": "%", "font": {"size": 32, "color": "#f1f5f9"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#475569"},
                "bar": {"color": "#818cf8"},
                "bgcolor": "rgba(30,41,59,0.5)",
                "steps": [
                    {"range": [0, 15],  "color": "rgba(16,185,129,0.2)"},
                    {"range": [15, 35], "color": "rgba(245,158,11,0.2)"},
                    {"range": [35, 100],"color": "rgba(239,68,68,0.2)"},
                ],
                "threshold": {"line": {"color": "#ef4444", "width": 3}, "value": 35}
            },
        ))
        fig_gauge.update_layout(
            template="plotly_dark", height=300,
            margin=dict(l=20,r=20,t=30,b=10),
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("""<div class="explainer" style="font-size:0.8rem">
            <strong>Green</strong> &lt;15% · <strong>Amber</strong> 15–35% · <strong>Red</strong> &gt;35%
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Outcome by Service (grouped) + Heatmap ──
    ha, hb = st.columns(2)

    with ha:
        st.markdown('<div class="section-header">🧩 Outcome Breakdown by Service</div>', unsafe_allow_html=True)
        svc_df = fdf.groupby(["service","outcome"]).size().reset_index(name="count")
        fig_svc = px.bar(
            svc_df, x="service", y="count", color="outcome",
            color_discrete_map=OUTCOME_COLORS, barmode="stack",
            text="count"
        )
        fig_svc.update_traces(textposition="inside", textfont_size=11)
        fig_svc.update_layout(
            template="plotly_dark", height=360,
            margin=dict(l=10,r=10,t=10,b=60),
            xaxis_tickangle=-30, showlegend=True,
            legend=dict(orientation="h", y=1.08)
        )
        st.plotly_chart(fig_svc, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> Which microservices produce the most rollbacks or alerts?
            Tall red/amber stacks = highest-risk services for your viva defence.
        </div>""", unsafe_allow_html=True)

    with hb:
        st.markdown('<div class="section-header">🗓️ Risk Heatmap — Day × Hour</div>', unsafe_allow_html=True)
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        heat = fdf.groupby(["day_of_week","deploy_hour"])["is_instability"].mean().reset_index()
        heat["pct"] = (heat["is_instability"] * 100).round(1)
        pivot = heat.pivot(index="day_of_week", columns="deploy_hour", values="pct").reindex(day_order).fillna(0)

        fig_heat = px.imshow(
            pivot,
            labels=dict(x="Hour of Day (UTC)", y="", color="Instability %"),
            color_continuous_scale="RdYlGn_r",
            aspect="auto", zmin=0, zmax=100
        )
        fig_heat.update_layout(
            template="plotly_dark", height=360,
            margin=dict(l=10,r=10,t=10,b=20),
            coloraxis_colorbar=dict(title="Risk %")
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> A calendar view of release risk.
            Bright red cells = historically dangerous deployment windows.
            Use this to argue <em>when not to deploy</em> in your sprint viva.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Top 5 Riskiest Conditions ──
    st.markdown('<div class="section-header">🚨 Top 5 Riskiest Release Conditions</div>', unsafe_allow_html=True)
    risk_g = fdf.groupby(["service","environment","day_of_week","time_bucket"]).agg(
        total=("deployment_id","count"),
        unstable=("is_instability","sum"),
        rollbacks=("has_rollback","sum")
    ).reset_index()
    risk_g["instability_pct"] = (risk_g["unstable"] / risk_g["total"] * 100).round(1)
    top5 = risk_g.sort_values(["instability_pct","rollbacks","total"], ascending=False).head(5).reset_index(drop=True)

    r1, r2 = st.columns([3, 2])
    with r1:
        top5_disp = top5.rename(columns={
            "service":"Service","environment":"Environment",
            "day_of_week":"Day","time_bucket":"Time Window",
            "total":"Deploys","unstable":"Unstable","instability_pct":"Risk %","rollbacks":"Rollbacks"
        })
        st.dataframe(top5_disp, use_container_width=True, hide_index=True)

    with r2:
        if len(top5) > 0:
            top5["label"] = top5["service"] + "\n" + top5["day_of_week"].str[:3] + " " + top5["time_bucket"].str.split("(").str[0].str.strip()
            fig_top = px.bar(
                top5, x="instability_pct", y="label", orientation="h",
                color="instability_pct", color_continuous_scale="Reds",
                text=top5["instability_pct"].astype(str) + "%",
                labels={"instability_pct":"Risk %","label":"Condition"}
            )
            fig_top.update_traces(textposition="outside")
            fig_top.update_layout(
                template="plotly_dark", height=280,
                margin=dict(l=10,r=10,t=10,b=10),
                coloraxis_showscale=False, xaxis_range=[0,115]
            )
            st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("""<div class="explainer">
        <strong>How to read this:</strong> Each row is a unique combination of Service + Environment + Day + Time window.
        <strong>Risk %</strong> = percentage of deployments in that slot that caused an alert or rollback.
        Conditions at 100% mean <em>every single deploy</em> in that window ended badly — strongest viva talking point.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEEP ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Sankey: Deployments → Service → Outcome ──
    st.markdown('<div class="section-header">🔄 Deployment Flow: Service → Outcome (Sankey)</div>', unsafe_allow_html=True)
    st.markdown("""<div class="explainer">
        <strong>What is a Sankey?</strong> It shows how deployments flow from each service into their final
        outcome. Thick red bands = lots of rollbacks from that service. Follow the colour to trace risk.
    </div>""", unsafe_allow_html=True)

    # Build sankey nodes + links
    services = sorted(fdf["service"].unique())
    outcomes = ["stable","alerted","rolled_back"]
    nodes = services + outcomes
    node_idx = {n: i for i, n in enumerate(nodes)}
    node_colors = (
        ["rgba(129,140,248,0.8)"] * len(services) +
        ["#10b981", "#f59e0b", "#ef4444"]
    )

    links_src, links_tgt, links_val, links_col = [], [], [], []
    sankey_color_map = {"stable":"rgba(16,185,129,0.4)","alerted":"rgba(245,158,11,0.4)","rolled_back":"rgba(239,68,68,0.5)"}
    for svc in services:
        for oc in outcomes:
            cnt = int(((fdf["service"] == svc) & (fdf["outcome"] == oc)).sum())
            if cnt > 0:
                links_src.append(node_idx[svc])
                links_tgt.append(node_idx[oc])
                links_val.append(cnt)
                links_col.append(sankey_color_map[oc])

    fig_sankey = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20, thickness=22,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
            label=nodes, color=node_colors
        ),
        link=dict(source=links_src, target=links_tgt, value=links_val, color=links_col)
    ))
    fig_sankey.update_layout(
        template="plotly_dark", height=400,
        margin=dict(l=10,r=10,t=20,b=10),
        font=dict(size=12, color="#cbd5e1")
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.markdown("---")

    # ── Rollback Root Cause + MTTR ──
    da, db_ = st.columns(2)

    with da:
        st.markdown('<div class="section-header">🔴 Rollback Root Cause Breakdown</div>', unsafe_allow_html=True)
        rb_df = fdf[fdf["rollback_reason"].notnull()]["rollback_reason"].value_counts().reset_index()
        rb_df.columns = ["reason","count"]
        if len(rb_df) > 0:
            # Shorten long labels
            rb_df["short"] = rb_df["reason"].str.split("(").str[0].str.strip()
            fig_rb = px.bar(
                rb_df, x="count", y="short", orientation="h",
                color="count", color_continuous_scale="Reds",
                text="count",
                labels={"count":"# Rollbacks","short":"Root Cause"}
            )
            fig_rb.update_traces(textposition="outside")
            fig_rb.update_layout(
                template="plotly_dark", height=340,
                margin=dict(l=10,r=10,t=10,b=10),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_rb, use_container_width=True)
        else:
            st.info("No rollback reason data in the current filter.")
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> What specifically caused each rollback.
            Dominant root causes here are your operational SRE failure patterns.
        </div>""", unsafe_allow_html=True)

    with db_:
        st.markdown('<div class="section-header">⏱️ MTTR by Priority & Service</div>', unsafe_allow_html=True)
        mttr_df = fdf[fdf["time_to_resolution_hours"].notnull()].copy()
        if len(mttr_df) > 0:
            mttr_grp = mttr_df.groupby(["service","priority_bucket"])["time_to_resolution_hours"].mean().reset_index()
            fig_mttr = px.scatter(
                mttr_grp,
                x="service", y="time_to_resolution_hours",
                color="priority_bucket", size="time_to_resolution_hours",
                size_max=30,
                color_discrete_sequence=["#ef4444","#f97316","#eab308","#3b82f6","#64748b"],
                labels={"time_to_resolution_hours":"Avg TTR (Hours)","service":"Service","priority_bucket":"Priority"}
            )
            fig_mttr.update_layout(
                template="plotly_dark", height=340,
                margin=dict(l=10,r=10,t=10,b=50),
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_mttr, use_container_width=True)
        else:
            st.info("No incident resolution data in current selection.")
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> How long it takes to resolve incidents per service,
            sized by severity. Large red bubbles = critical incidents taking long to fix.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── After-hours vs Business hours ──
    ea, eb = st.columns(2)

    with ea:
        st.markdown('<div class="section-header">🌙 After-Hours vs Business-Hours Risk</div>', unsafe_allow_html=True)
        ah = fdf.groupby("is_after_hours")["is_instability"].agg(["mean","sum","count"]).reset_index()
        ah["label"] = ah["is_after_hours"].map({0:"Business Hours (09:00–18:00)", 1:"After Hours (18:00–09:00)"})
        ah["pct"] = (ah["mean"] * 100).round(1)
        fig_ah = px.bar(
            ah, x="label", y="pct",
            color="label",
            color_discrete_sequence=["#10b981","#ef4444"],
            text=ah["pct"].astype(str) + "%",
            labels={"pct":"Instability Rate (%)","label":""}
        )
        fig_ah.update_traces(textposition="outside")
        fig_ah.update_layout(
            template="plotly_dark", height=320,
            showlegend=False, margin=dict(l=10,r=10,t=10,b=10)
        )
        st.plotly_chart(fig_ah, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> Whether after-hours deployments are riskier.
            If the red bar is significantly taller, this is a strong sprint viva argument
            for enforcing change-freeze policies outside business hours.
        </div>""", unsafe_allow_html=True)

    with eb:
        st.markdown('<div class="section-header">👤 Top Deployers by Instability</div>', unsafe_allow_html=True)
        user_df = fdf.groupby("deployed_by").agg(
            total=("deployment_id","count"),
            unstable=("is_instability","sum")
        ).reset_index()
        user_df["risk_pct"] = (user_df["unstable"] / user_df["total"] * 100).round(1)
        user_df = user_df.sort_values("risk_pct", ascending=False)
        fig_user = px.scatter(
            user_df, x="total", y="risk_pct",
            size="unstable", color="risk_pct",
            color_continuous_scale="Reds", hover_name="deployed_by",
            text="deployed_by",
            labels={"total":"Total Deployments","risk_pct":"Instability Rate (%)"},
            size_max=40
        )
        fig_user.update_traces(textposition="top center", textfont_size=10)
        fig_user.update_layout(
            template="plotly_dark", height=320,
            margin=dict(l=10,r=10,t=10,b=10),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_user, use_container_width=True)
        st.markdown("""<div class="explainer">
            <strong>What does this show?</strong> Which deployers have the highest instability rates
            (size = number of unstable deploys, position = frequency vs risk %).
            Top-right red bubbles = frequent <em>and</em> risky deployers.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Branch risk ──
    st.markdown('<div class="section-header">🌿 Branch-Level Risk Profile</div>', unsafe_allow_html=True)
    br_df = fdf.groupby(["branch","outcome"]).size().reset_index(name="count")
    fig_br = px.bar(
        br_df, x="branch", y="count", color="outcome",
        color_discrete_map=OUTCOME_COLORS, barmode="group",
        text="count",
        labels={"count":"Deployments","branch":"Branch","outcome":"Outcome"}
    )
    fig_br.update_traces(textposition="outside")
    fig_br.update_layout(
        template="plotly_dark", height=340,
        margin=dict(l=10,r=10,t=10,b=60),
        xaxis_tickangle=-25, legend=dict(orientation="h", y=1.08)
    )
    st.plotly_chart(fig_br, use_container_width=True)
    st.markdown("""<div class="explainer">
        <strong>What does this show?</strong> How each branch performs when deployed.
        <code>hotfix/*</code> branches often have high rollback rates because fixes are rushed.
        <code>main</code> should ideally be the most stable.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PIPELINE EXPLAINER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="explainer" style="margin-bottom:20px; font-size:0.95rem; border-color:rgba(56,189,248,0.3)">
        <strong>📖 How the Release Risk Analyzer Pipeline Works</strong><br>
        This tab walks through every script in the data engineering pipeline — what it does,
        why it was built that way, and what output it produces. Use this for your Sprint 1 Viva defence.
    </div>
    """, unsafe_allow_html=True)

    steps = [
        {
            "num": "STEP 0", "emoji": "🏗️",
            "title": "Repository & Environment Setup",
            "script": None,
            "desc": (
                "The project is structured around a clear separation of concerns: "
                "<code>data/raw/</code> for inputs, <code>data/processed/</code> for cleaned outputs, "
                "<code>scripts/</code> for pipeline logic, <code>output/</code> for audit logs, and "
                "<code>.github/workflows/</code> for CI/CD quality gates. "
                "A Python virtual environment ensures reproducibility."
            ),
            "outputs": ["requirements.txt", ".gitignore", ".env.example", "README.md"]
        },
        {
            "num": "STEP 1", "emoji": "📥",
            "title": "Real Data Ingestion (data_ingestion.py)",
            "script": "scripts/data_ingestion.py",
            "desc": (
                "Loads <code>incident_log.csv</code> (UCI ServiceNow Incident Log) and "
                "<code>pipeline_logs.csv</code> (CI/CD telemetry) with a "
                "<strong>5-tier encoding fallback</strong> (utf-8 → utf-8-sig → latin1 → iso-8859-1 → cp1252) "
                "because real enterprise exports have inconsistent character encodings. "
                "Schema validation checks all expected columns are present before processing continues."
            ),
            "outputs": ["output/ingestion_audit_report.json"]
        },
        {
            "num": "STEP 2", "emoji": "🔧",
            "title": "Build the Missing Layer (derive_deployments.py)",
            "script": "scripts/derive_deployments.py",
            "desc": (
                "CI/CD pipeline logs mix Build, Test, Scan, and Deploy stages together. "
                "We <strong>filter to stage_name == 'Deploy'</strong> and assign each a unique "
                "<code>deployment_id</code>, deriving the <code>service</code> name from <code>job_name</code> patterns. "
                "<br><br>"
                "<strong>Synthetic Rollback Modeling (Documented Assumption):</strong> "
                "~70% of <em>failed production deployments</em> get a synthetic rollback event, "
                "with a timestamp 5–45 minutes after failure and realistic SRE root causes "
                "(HealthCheckFailed, ElevatedErrorRate, MemoryLeakDetected). "
                "This models real-world SRE automation behaviour absent from raw CI/CD logs."
            ),
            "outputs": ["data/raw/derived_deployments.csv", "data/raw/rollbacks.csv"]
        },
        {
            "num": "STEP 3", "emoji": "🧹",
            "title": "Data Cleaning (cleaning.py)",
            "script": "scripts/cleaning.py",
            "desc": (
                "Three sources (deployments, incidents, rollbacks) each get: "
                "<ol style='margin:6px 0 0 18px'>"
                "<li><strong>Null imputation</strong> — missing categories → 'General/Unknown', missing priority → '4-Low'</li>"
                "<li><strong>ISO 8601 UTC timestamp normalization</strong> — all datetime strings are parsed and reformatted uniformly</li>"
                "<li><strong>Deduplication</strong> — ServiceNow logs contain lifecycle snapshots for the same incident_id; "
                "we keep the most recent snapshot by sorting on <code>sys_updated_at</code></li>"
                "</ol>"
                "Every single decision is logged row-by-row to the cleaning audit CSV."
            ),
            "outputs": [
                "data/processed/clean_deployments.csv",
                "data/processed/clean_incidents.csv",
                "data/processed/clean_rollbacks.csv",
                "output/cleaning_log.csv"
            ]
        },
        {
            "num": "STEP 4", "emoji": "🔗",
            "title": "Heuristic Join Validation (join_validation.py)",
            "script": "scripts/join_validation.py",
            "desc": (
                "<strong>The Hardest Engineering Decision:</strong> CI/CD deployments and ServiceNow "
                "ITSM incidents originate in completely separate enterprise systems with no shared key. "
                "We link them with a <strong>2-dimensional heuristic</strong>:"
                "<ol style='margin:6px 0 0 18px'>"
                "<li><strong>Temporal window:</strong> Incident <code>opened_at</code> must fall in "
                "[T_deploy, T_deploy + 2 hours]</li>"
                "<li><strong>Semantic affinity:</strong> Service name maps to incident category/assignment group "
                "via an explicit dictionary (auth-service → Security/Access, payment-api → Finance/Transactions)</li>"
                "</ol>"
                "If multiple incidents match, the highest severity (Critical P1 first) wins. "
                "Non-matched incidents become <em>orphaned records</em> and are audited separately."
            ),
            "outputs": ["data/processed/deployment_outcomes.csv", "output/join_audit_report.json"]
        },
        {
            "num": "STEP 5", "emoji": "⚙️",
            "title": "Feature Engineering (feature_engineering.py)",
            "script": "scripts/feature_engineering.py",
            "desc": (
                "Eight risk features are derived on the joined dataset: "
                "<code>day_of_week</code>, <code>deploy_hour</code>, <code>is_weekend</code>, "
                "<code>is_after_hours</code>, <code>time_bucket</code>, "
                "<code>priority_bucket</code>, <code>is_instability</code> (binary 0/1), "
                "and <code>risk_score_weight</code> (stable=0, alerted=1, rolled_back=2). "
                "These features power the heatmaps, KPI queries, and dashboard visualizations."
            ),
            "outputs": ["data/processed/deployment_outcomes.csv (enriched with 8 features)"]
        },
        {
            "num": "STEP 6", "emoji": "🗄️",
            "title": "SQLite Storage & Analytical KPIs (database_kpis.py)",
            "script": "scripts/database_kpis.py",
            "desc": (
                "The curated <code>deployment_outcomes</code> dataframe is written to a local "
                "<strong>SQLite database</strong> (<code>data/release_risk.db</code>) — no server required. "
                "Three analytical SQL queries compute: "
                "(1) rollback/alert rate grouped by <code>day_of_week</code> and <code>deploy_hour</code>, "
                "(2) Mean Time-to-Resolution (MTTR) per priority tier, "
                "(3) Top 5 riskiest release conditions ranked by instability rate. "
                "Results are saved to <code>output/kpi_summary.json</code>."
            ),
            "outputs": ["data/release_risk.db", "output/kpi_summary.json"]
        },
        {
            "num": "STEP 7", "emoji": "📊",
            "title": "Streamlit Dashboard (app.py)",
            "script": "scripts/app.py",
            "desc": (
                "This dashboard. A <strong>multi-tab interactive analytics interface</strong> built with Streamlit "
                "and Plotly. Reads live from SQLite with a CSV fallback. Includes global filters "
                "(service, environment, outcome, date range), 12+ interactive charts, "
                "pipeline explainer documentation, and CSV export."
            ),
            "outputs": ["http://localhost:8501"]
        },
        {
            "num": "STEP 8", "emoji": "🚦",
            "title": "CI/CD Data Quality Gate (data_quality.yml + test_data_quality.py)",
            "script": "tests/test_data_quality.py",
            "desc": (
                "A GitHub Actions workflow triggers on every push to <code>main</code>. "
                "It runs the full pipeline then executes 6 pytest assertions: "
                "(1) file exists and is non-empty, (2) zero null outcomes, "
                "(3) zero duplicate deployment_ids, (4) valid outcome domain values only, "
                "(5) zero nulls in critical fields, (6) temporal features in valid ranges. "
                "<strong>The build fails</strong> if any assertion fails, enforcing data contract compliance."
            ),
            "outputs": ["GitHub Actions: PASS / FAIL badge on main branch"]
        },
    ]

    # Render live audit stats alongside relevant steps
    if "ingestion" in audit:
        ingestion_summary = audit["ingestion"].get("datasets", {})
    if "join" in audit:
        join_summary = audit["join"]

    for step in steps:
        with st.expander(f"{step['emoji']} {step['num']} — {step['title']}", expanded=False):
            st.markdown(f"""
            <div class="step-card">
                <div class="step-num">{step['num']}</div>
                <div class="step-title">{step['emoji']} {step['title']}</div>
                <div class="step-desc">{step['desc']}</div>
                <div class="step-output">📤 <strong>Outputs:</strong> {"  ·  ".join(f"<code>{o}</code>" for o in step['outputs'])}</div>
            </div>
            """, unsafe_allow_html=True)

            # Attach live stats where available
            if step["num"] == "STEP 1" and "ingestion" in audit:
                ds = audit["ingestion"].get("datasets", {})
                for fname, info in ds.items():
                    schema = info.get("schema_validation", {})
                    st.success(f"✅ **{fname}**: {schema.get('total_rows','?')} rows · "
                               f"Encoding: `{info.get('encoding_used','?')}` · "
                               f"Valid: {schema.get('is_valid','?')}")

            elif step["num"] == "STEP 4" and "join" in audit:
                j = audit["join"]
                col_j1, col_j2, col_j3 = st.columns(3)
                col_j1.metric("Total Deployments", j.get("total_deployments","?"))
                col_j2.metric("Incidents Matched", j.get("incidents_matched_to_deployments","?"))
                col_j3.metric("Orphaned Incidents", f"{j.get('orphaned_incidents_count','?')} ({j.get('orphaned_incidents_ratio_pct','?')}%)")
                oc_dist = j.get("outcome_distribution", {})
                for oc, cnt in oc_dist.items():
                    badge_cls = f"badge-{oc}"
                    st.markdown(f"<span class='{badge_cls}'>{oc}</span> &nbsp; **{cnt}** deployments", unsafe_allow_html=True)

            elif step["num"] == "STEP 6" and "kpi" in audit:
                kpi = audit["kpi"]
                top_risks_kpi = kpi.get("top_5_risk_conditions", [])
                if top_risks_kpi:
                    st.markdown("**Live KPI 3 — Top Risk Conditions from SQLite:**")
                    st.dataframe(pd.DataFrame(top_risks_kpi), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — RAW DATA & AUDIT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">📋 Deployment Outcomes — Full Audit Log</div>', unsafe_allow_html=True)
    st.markdown("""<div class="explainer">
        <strong>What is this table?</strong> The final output of the entire data pipeline —
        every deployment event annotated with its matched incident, rollback, engineered features,
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
        st.markdown('<div class="section-header">📊 KPI Summary</div>', unsafe_allow_html=True)
        if "kpi" in audit:
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
