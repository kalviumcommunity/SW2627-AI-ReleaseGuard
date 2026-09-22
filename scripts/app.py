"""
Step 7: Release Risk Analyzer - Interactive Streamlit Dashboard

Features:
- Premium modern dark glassmorphism UI & metric cards
- Top 5 Riskiest Release Conditions (ranked by instability rate)
- Interactive Plotly visualizations:
  * Instability Trend Over Time
  * Rollback vs Alert breakdown by Service & Environment
  * Mean Time to Resolution (MTTR) by Severity Tier
  * Heatmap of Risk by Day of Week & Hour
- Multi-dimensional sidebar filters (Service, Environment, Outcome, Date Range)
- Live SQLite database connection with CSV fallback
- Detailed deployment log inspector with CSV export
"""

import os
import sys
import sqlite3
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

# Page Configuration
st.set_page_config(
    page_title="Release Risk Analyzer | ReleaseGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Dark Mode Aesthetics
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
    }
    
    /* Header Banner */
    .header-container {
        padding: 24px;
        background: linear-gradient(90deg, #1e1b4b 0%, #0f172a 100%);
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .header-desc {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    
    /* Risk Badges */
    .badge-rolled_back {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-alerted {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #f59e0b;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-stable {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Data Loader with Caching
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
        
    # If no data exists, trigger pipeline
    from scripts.run_pipeline import main as run_p
    run_p()
    df = pd.read_csv(csv_path)
    df["deploy_dt"] = pd.to_datetime(df["deploy_timestamp"])
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}. Please run `python scripts/run_pipeline.py` first.")
    st.stop()

# -------------------------------------------------------------
# Sidebar Navigation & Filters
# -------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=64)
st.sidebar.title("ReleaseGuard")
st.sidebar.markdown("**AI-Assisted CI/CD Risk Intelligence**")
st.sidebar.markdown("---")

st.sidebar.subheader("🔍 Global Filters")

# Service Filter
all_services = sorted(df_raw["service"].unique())
selected_services = st.sidebar.multiselect("Select Services", options=all_services, default=all_services)

# Environment Filter
all_envs = sorted(df_raw["environment"].unique())
selected_envs = st.sidebar.multiselect("Select Environments", options=all_envs, default=all_envs)

# Outcome Filter
all_outcomes = sorted(df_raw["outcome"].unique())
selected_outcomes = st.sidebar.multiselect("Deployment Outcomes", options=all_outcomes, default=all_outcomes)

# Date Range Filter
min_date = df_raw["deploy_dt"].min().date()
max_date = df_raw["deploy_dt"].max().date()
date_range = st.sidebar.date_input("Deployment Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Apply Filters
filtered_df = df_raw[
    (df_raw["service"].isin(selected_services)) &
    (df_raw["environment"].isin(selected_envs)) &
    (df_raw["outcome"].isin(selected_outcomes))
]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df["deploy_dt"].dt.date >= start_d) &
        (filtered_df["deploy_dt"].dt.date <= end_d)
    ]

# -------------------------------------------------------------
# Header Section
# -------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🛡️ Release Risk Analyzer</h1>
    <p class="header-desc">
        Operational telemetry bridge connecting CI/CD deployment pipelines with ServiceNow ITSM incident logs & synthetic rollback tracking.
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Top KPI Metric Cards
# -------------------------------------------------------------
total_deployments = len(filtered_df)
rolled_back_count = (filtered_df["outcome"] == "rolled_back").sum()
alerted_count = (filtered_df["outcome"] == "alerted").sum()
stable_count = (filtered_df["outcome"] == "stable").sum()

rollback_rate = (rolled_back_count / total_deployments * 100) if total_deployments > 0 else 0
alert_rate = (alerted_count / total_deployments * 100) if total_deployments > 0 else 0
instability_rate = ((rolled_back_count + alerted_count) / total_deployments * 100) if total_deployments > 0 else 0

valid_ttr = filtered_df[filtered_df["time_to_resolution_hours"].notnull()]["time_to_resolution_hours"]
mean_mttr = valid_ttr.mean() if len(valid_ttr) > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Deployments</div>
        <div class="metric-value">{total_deployments:,}</div>
        <div class="metric-subtitle">Evaluated release events</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Rollback Rate</div>
        <div class="metric-value" style="color: #f87171;">{rollback_rate:.1f}%</div>
        <div class="metric-subtitle">{rolled_back_count} rollbacks recorded</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Post-Deploy Alerts</div>
        <div class="metric-value" style="color: #fbbf24;">{alert_rate:.1f}%</div>
        <div class="metric-subtitle">{alerted_count} 2-hr window incidents</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Instability Rate</div>
        <div class="metric-value" style="color: #c084fc;">{instability_rate:.1f}%</div>
        <div class="metric-subtitle">Rollbacks + Alerts combined</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Mean Incident TTR</div>
        <div class="metric-value" style="color: #38bdf8;">{mean_mttr:.1f}h</div>
        <div class="metric-subtitle">Avg resolution time</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Section 1: Top 5 Riskiest Release Conditions
# -------------------------------------------------------------
st.subheader("🚨 Top 5 Riskiest Release Conditions (Ranked by Instability)")

risk_groups = filtered_df.groupby(["service", "environment", "day_of_week", "time_bucket"]).agg(
    total_deploys=("deployment_id", "count"),
    unstable_deploys=("is_instability", "sum"),
    rollbacks=("has_rollback", "sum")
).reset_index()

risk_groups["instability_rate_pct"] = (risk_groups["unstable_deploys"] / risk_groups["total_deploys"] * 100).round(1)
top_5_risks = risk_groups.sort_values(by=["instability_rate_pct", "rollbacks", "total_deploys"], ascending=False).head(5)

col_tbl, col_chart = st.columns([3, 2])

with col_tbl:
    st.dataframe(
        top_5_risks.rename(columns={
            "service": "Service",
            "environment": "Environment",
            "day_of_week": "Day of Week",
            "time_bucket": "Time Window",
            "total_deploys": "Total Deploys",
            "unstable_deploys": "Unstable Deploys",
            "instability_rate_pct": "Instability Rate (%)",
            "rollbacks": "Rollbacks"
        }),
        use_container_width=True,
        hide_index=True
    )

with col_chart:
    if len(top_5_risks) > 0:
        top_5_risks["condition_label"] = top_5_risks["service"] + " (" + top_5_risks["day_of_week"] + " - " + top_5_risks["time_bucket"].str.split(" ").str[0] + ")"
        fig_risk = px.bar(
            top_5_risks,
            x="instability_rate_pct",
            y="condition_label",
            orientation="h",
            color="instability_rate_pct",
            color_continuous_scale="Reds",
            labels={"instability_rate_pct": "Instability Rate (%)", "condition_label": "Release Condition"},
            title="Top 5 Risk Profiles"
        )
        fig_risk.update_layout(template="plotly_dark", height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# Section 2: Interactive Charts (Trends & Risk Breakdown)
# -------------------------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📈 Instability Trend Over Time")
    trend_df = filtered_df.copy()
    trend_df["date"] = trend_df["deploy_dt"].dt.date
    daily_trend = trend_df.groupby("date").agg(
        total=("deployment_id", "count"),
        unstable=("is_instability", "sum"),
        rolled_back=("has_rollback", "sum")
    ).reset_index()
    daily_trend["instability_rate"] = (daily_trend["unstable"] / daily_trend["total"] * 100).round(1)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=daily_trend["date"],
        y=daily_trend["instability_rate"],
        mode="lines+markers",
        name="Instability Rate (%)",
        line=dict(color="#818cf8", width=3),
        marker=dict(size=8, color="#c084fc")
    ))
    fig_trend.add_trace(go.Bar(
        x=daily_trend["date"],
        y=daily_trend["total"],
        name="Total Deployments",
        marker_color="rgba(100, 116, 139, 0.3)",
        yaxis="y2"
    ))
    fig_trend.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Instability Rate (%)", range=[0, 105]),
        yaxis2=dict(title="Deploy Count", overlaying="y", side="right", showgrid=False)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with row2_col2:
    st.subheader("📊 Deployment Outcomes by Service")
    svc_outcomes = filtered_df.groupby(["service", "outcome"]).size().reset_index(name="count")
    fig_svc = px.bar(
        svc_outcomes,
        x="service",
        y="count",
        color="outcome",
        color_discrete_map={"stable": "#10b981", "alerted": "#f59e0b", "rolled_back": "#ef4444"},
        barmode="stack",
        title="Outcome Distribution Across Microservices"
    )
    fig_svc.update_layout(template="plotly_dark", height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_svc, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# Section 3: Heatmap & MTTR Breakdown
# -------------------------------------------------------------
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🗓️ Temporal Risk Matrix (Day of Week vs Hour)")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat_data = filtered_df.groupby(["day_of_week", "deploy_hour"])["is_instability"].mean().reset_index()
    heat_data["is_instability"] = (heat_data["is_instability"] * 100).round(1)
    
    pivot_heat = heat_data.pivot(index="day_of_week", columns="deploy_hour", values="is_instability").reindex(day_order).fillna(0)
    
    fig_heat = px.imshow(
        pivot_heat,
        labels=dict(x="Hour of Day (UTC)", y="Day of Week", color="Instability %"),
        x=pivot_heat.columns,
        y=pivot_heat.index,
        color_continuous_scale="Plasma",
        title="Release Instability Heatmap (%)"
    )
    fig_heat.update_layout(template="plotly_dark", height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

with row3_col2:
    st.subheader("⏱️ Mean Time to Resolution (MTTR) by Priority")
    mttr_df = filtered_df[filtered_df["time_to_resolution_hours"].notnull()].groupby("priority_bucket")["time_to_resolution_hours"].mean().reset_index()
    if len(mttr_df) > 0:
        fig_mttr = px.bar(
            mttr_df,
            x="priority_bucket",
            y="time_to_resolution_hours",
            color="priority_bucket",
            color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#3b82f6"],
            labels={"time_to_resolution_hours": "Mean TTR (Hours)", "priority_bucket": "Severity Bucket"},
            title="Operational MTTR Breakdown"
        )
        fig_mttr.update_layout(template="plotly_dark", height=350, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_mttr, use_container_width=True)
    else:
        st.info("No matching incident resolution data in current filter selection.")

st.markdown("---")

# -------------------------------------------------------------
# Section 4: Granular Deployment Log Explorer
# -------------------------------------------------------------
st.subheader("📋 Granular Deployment Audit Log")

display_cols = [
    "deployment_id", "service", "environment", "deploy_timestamp", 
    "deployed_by", "outcome", "rollback_reason", "matched_incident_id", 
    "incident_priority", "time_to_resolution_hours"
]
available_display_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[available_display_cols].sort_values(by="deploy_timestamp", ascending=False),
    use_container_width=True,
    hide_index=True
)

# Export Action
csv_export = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Filtered Deployment Telemetry (CSV)",
    data=csv_export,
    file_name=f"release_risk_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)
