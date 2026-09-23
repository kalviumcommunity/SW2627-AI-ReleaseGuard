## Overview

Build an operational Streamlit dashboard that connects the complete workflow:

```text
Upload Dataset
      ↓
Data Validation
      ↓
Filter Widgets
      ↓
Filtered DataFrame
      ↓
Reactive KPIs + Charts

All metrics and visualizations must update automatically when filters change or new data is uploaded.

Task 1: Display Five Reactive KPIs

Create at least five KPI metrics using filtered_df.

Required KPIs
Total Revenue
Average Order Value
Record Count
Unique Customers
Data Quality %

Example:

total_revenue = filtered_df["revenue"].sum()
avg_order = filtered_df["revenue"].mean()
row_count = len(filtered_df)
unique_customers = filtered_df["customer_id"].nunique()

null_pct = (
    filtered_df.isnull().sum().sum()
    / (filtered_df.shape[0] * filtered_df.shape[1])
    * 100
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Revenue", f"${total_revenue:,.0f}")
with col2:
    st.metric("Avg Order", f"${avg_order:,.0f}")
with col3:
    st.metric("Records", f"{row_count:,}")
with col4:
    st.metric("Customers", f"{unique_customers:,}")
with col5:
    st.metric("Quality", f"{100 - null_pct:.1f}%")
Acceptance
All five KPIs are calculated dynamically.
No hardcoded metric values.
Changing any filter updates the KPIs.
Task 2: Add Three Reactive Chart Types

Implement at least three different chart types using filtered_df.

1. Line Chart — Revenue Trend
trend = (
    filtered_df.groupby("date")["revenue"]
    .sum()
    .reset_index()
)

st.line_chart(trend.set_index("date"))
2. Bar Chart — Revenue by Segment
seg = (
    filtered_df.groupby("segment")["revenue"]
    .sum()
    .reset_index()
)

st.bar_chart(seg.set_index("segment"))
3. Histogram — Revenue Distribution
import plotly.express as px

fig = px.histogram(
    filtered_df,
    x="revenue",
    nbins=30
)

st.plotly_chart(fig, use_container_width=True)
Acceptance
Three different chart types render.
Charts use the filtered DataFrame.
Changing filters updates every chart.
Task 3: Cache Data Loading

Use @st.cache_data for uploaded data processing.

@st.cache_data
def load_data(file_bytes, file_name):
    if file_name.endswith(".csv"):
        return pd.read_csv(file_bytes)
    elif file_name.endswith(".json"):
        return pd.read_json(file_bytes)
Acceptance
Data loading is cached.
Repeated filter interactions do not reload the source unnecessarily.
Uploaded files correctly invalidate/recalculate cached data when the file changes.
Task 4: Handle Empty Results

Prevent empty filters from producing errors or broken charts.

if filtered_df.empty:
    st.warning(
        "No data matches the current filters. "
        "Broaden your selection."
    )
    st.stop()
Acceptance
Impossible filter combinations show a clear warning.
No Python errors occur.
Empty charts are not rendered.
Task 5: Support Uploaded Datasets

The dashboard must work end-to-end from file upload to KPI display.

Requirements
Support uploaded CSV/JSON data.
Do not use hardcoded file paths.
Do not hardcode KPI values.
Validate required columns if the dashboard expects a specific schema.
Display a useful validation message when required columns are missing.

Example:

required_columns = {
    "date",
    "revenue",
    "segment",
    "customer_id"
}

missing = required_columns - set(df.columns)

if missing:
    st.error(
        f"Missing required columns: {', '.join(sorted(missing))}"
    )
    st.stop()
Acceptance
Uploading a valid dataset produces KPIs and charts.
Uploading another compatible dataset updates the dashboard.
Invalid datasets produce a clear validation message.
No hardcoded dataset values or file paths.
End-to-End Architecture
File Upload
    ↓
Cached Data Loader
    ↓
Schema Validation
    ↓
Sidebar Filters
    ↓
Filtered DataFrame
    ↓
┌───────────────┬────────────────┐
│ 5 KPI Metrics │ 3+ Charts      │
└───────────────┴────────────────┘
File Structure
assignment-29/
├── app.py
└── requirements.txt
Acceptance Criteria
 Five reactive KPI metrics implemented.
 Three different reactive chart types implemented.
 KPIs update when filters change.
 Charts update when filters change.
 @st.cache_data is used for data loading.
 Empty filter results are handled safely.
 Dataset upload works end-to-end.
 Required columns are validated.
 No hardcoded metric values or file paths.
 A different compatible dataset can be uploaded successfully.