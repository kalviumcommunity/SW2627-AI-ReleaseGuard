# Overview

Build a Streamlit business performance dashboard using the **four-level information hierarchy**:

1. **Status** — KPI summary
2. **Trends** — Time-based performance
3. **Segments** — Business/customer comparisons
4. **Detail** — Filterable data exploration

The dashboard should allow executives to quickly understand overall performance while giving marketing, sales, and analytics teams the ability to investigate details.

---

# Task 1: Design the Dashboard Layout

## Level 1 — Status: KPI Summary

Create **5 KPI cards** at the top of the dashboard.

| KPI | Example Value | Change | Business Question |
|---|---:|---:|---|
| Revenue | $5.2M | +12.5% | Are we generating enough revenue? |
| Active Customers | 2,500 | +5.2% | Is our customer base growing? |
| Avg Order Value | $145 | +3.1% | Are customers spending more per order? |
| Churn Rate | 4.8% | -1.2% | Are we retaining customers? |
| NPS Score | 72 | +4 | Are customers satisfied with the business? |

### Implementation

```python
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Revenue", "$5.2M", "+12.5%")

with col2:
    st.metric("Active Customers", "2,500", "+5.2%")

with col3:
    st.metric("Avg Order Value", "$145", "+3.1%")

with col4:
    st.metric("Churn Rate", "4.8%", "-1.2%", delta_color="inverse")

with col5:
    st.metric("NPS Score", "72", "+4")
Validation
Exactly 5 KPI cards are displayed.
Each card contains:
Metric name
Current value
Period-over-period change
Trend direction
Every KPI has a documented business purpose.
Task 2: Build the Trend Section
Level 2 — Trends

Create 2–3 charts showing how business performance changes over time.

Chart 1 — Monthly Revenue Trend

Create a line chart showing monthly revenue.

Requirements:

X-axis: Month
Y-axis: Revenue ($M)
Add target/reference line at $5M
Add chart title
Add axis labels
Save as:
output/revenue_trend.png

Example:

ax.plot(months, revenue, marker="o", linewidth=2)
ax.axhline(
    y=5.0,
    linestyle="--",
    linewidth=1.5,
    label="Target: $5M"
)
Chart 2 — Customer Metrics

Create a dual-line chart comparing:

Active customers
Churned customers

Both metrics should share the same time axis.

Purpose:

Identify whether customer growth is occurring alongside increasing or decreasing churn.

Chart 3 — Business Trend

Choose a relevant third metric, such as:

Monthly orders
Conversion rate
Customer acquisition
Marketing campaign performance
Average order value
Trend Chart Requirements

Every chart must include:

Descriptive title
Labelled axes
Units
At least one annotation or reference/target line
Consistent colour palette
Task 3: Build the Segment Section
Level 3 — Segment Comparison

Create at least one segment comparison chart.

Revenue by Customer Segment

Use a horizontal bar chart for:

Enterprise
Mid-Market
SMB
Starter

Example:

segments = ["Enterprise", "Mid-Market", "SMB", "Starter"]
segment_revenue = [2.1, 1.5, 1.0, 0.6]

ax.barh(segments, segment_revenue)

ax.set_xlabel("Revenue ($M)")
ax.set_title("Revenue by Customer Segment")

Add value labels to each bar.

Business Question

Which customer segments contribute the most revenue, and which segments may require additional attention?

Validation
Segment breakdown is displayed.
Bar chart is used for comparison.
Values are labelled.
Chart has complete titles and axis labels.
Task 4: Apply Progressive Disclosure
Level 4 — Detailed Data Explorer

Create a detailed section that users can access after reviewing the summary information.

Filters

Add sidebar filters for:

Customer segment
Date range
Additional relevant dimensions where available

Example:

st.sidebar.header("Filters")

selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    ["All", "Enterprise", "Mid-Market", "SMB", "Starter"]
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(start_date, end_date)
)
Dynamic Filtering
if selected_segment != "All":
    filtered_df = df[df["segment"] == selected_segment]
else:
    filtered_df = df

The displayed records must update whenever filters change.

Data Table

Display relevant detailed fields:

st.dataframe(
    filtered_df[
        [
            "customer_id",
            "segment",
            "revenue",
            "last_activity",
            "churn_risk"
        ]
    ]
)
Export

Provide a CSV download:

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)
Validation
Filters work dynamically.
Table updates based on filters.
Detailed records are visible.
CSV export contains the filtered data.
Task 5: Create Dashboard Design Documentation

Create:

dashboard_design.md

The document must contain:

# Dashboard Design Documentation

## Information Hierarchy Applied

### Level 1 — Status
Five KPI cards provide an immediate overview of business health.

### Level 2 — Trends
Trend charts show how revenue, customers, churn, and other key metrics change over time.

### Level 3 — Segments
Segment charts compare business performance across customer groups.

### Level 4 — Detail
Filters, detailed records, and CSV export allow users to investigate specific data.

## Design Principles

1. **Progressive Disclosure**
   - Summary information is visible immediately.
   - Detailed information is available through filters and drill-down.

2. **Spatial Organisation**
   - The most important information appears at the top.
   - Supporting analysis appears progressively lower on the page.

3. **Consistent Visual Language**
   - Use the same colours and visual conventions across charts.

4. **Context Over Numbers**
   - KPIs include period-over-period changes.
   - Charts include targets or reference lines where appropriate.

## Colour Palette

- Primary: `#1f77b4` — main metrics
- Secondary: `#ff7f0e` — comparisons
- Success: `#2ca02c` — positive indicators
- Danger: `#d62728` — negative indicators

## Target Audience

- **CEO:** Quickly reviews the KPI row to understand overall performance.
- **Marketing/Sales Leadership:** Uses trends and segment analysis to monitor performance.
- **Analysts:** Uses filters, detailed records, and exports for deeper investigation.

## Data Sources

- KPI values: `vw_monthly_revenue`, `vw_active_customers`
- Trend data: `agg_daily_revenue`
- Segment data: `vw_customer_segments`

## Dashboard Structure

Status → Trends → Segments → Detailed Data Explorer
Recommended Dashboard Structure
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS PERFORMANCE DASHBOARD                 │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Revenue  │ Customers│ AOV      │ Churn    │ NPS            │
│ $5.2M    │ 2,500    │ $145     │ 4.8%     │ 72             │
│ +12.5%   │ +5.2%    │ +3.1%    │ -1.2%    │ +4             │
├─────────────────────────────────────────────────────────────┤
│                    TREND ANALYSIS                           │
│                                                             │
│  Revenue Trend                 Customer / Churn Trend       │
│  ────────────────             ─────────────────────         │
│                                                             │
│  Additional Business Trend                                  │
├─────────────────────────────────────────────────────────────┤
│                    SEGMENT ANALYSIS                         │
│                                                             │
│  Revenue by Customer Segment                                │
│  Enterprise █████████████████                               │
│  Mid-Market ███████████                                     │
│  SMB        ███████                                         │
│  Starter    ████                                            │
├─────────────────────────────────────────────────────────────┤
│                  DETAILED DATA EXPLORER                     │
│                                                             │
│  Filters → Segment | Date Range                             │
│                                                             │
│  Customer ID | Segment | Revenue | Activity | Churn Risk    │
│                                                             │
│                    [Download CSV]                           │
└─────────────────────────────────────────────────────────────┘
Acceptance Criteria
 Streamlit dashboard uses a wide layout.
 Five KPI cards are displayed at the top.
 Every KPI has a value and period-over-period change.
 KPI metrics have documented business justification.
 2–3 trend charts are implemented.
 Trend charts contain titles, labelled axes, units, and reference/annotation elements.
 Charts use a consistent colour palette.
 At least one segment comparison chart is implemented.
 Segment chart contains readable data labels.
 Detailed data explorer supports filtering.
 Data table updates dynamically.
 CSV export works with filtered records.
 dashboard_design.md documents hierarchy, design principles, colours, audience, and data sources.
 Dashboard follows the hierarchy: Status → Trends → Segments → Detail.