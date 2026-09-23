# Overview

Build a Streamlit KPI dashboard that communicates business health at a glance.

The dashboard must contain five KPI cards showing:

- Current value
- Previous-period comparison
- Percentage change
- Trend direction
- Status colour
- Validated data source

The KPI system must calculate values dynamically from the clean data layer rather than using hardcoded numbers.

---

# Task 1: Compute Five KPI Metrics

Calculate the following metrics for the current month and compare them with the previous month.

| KPI | Current Period | Prior Period | Business Purpose |
|---|---|---|---|
| Total Revenue | Current month revenue | Previous month | Measures financial performance |
| Active Users | Users active this month | Previous month | Measures user engagement |
| Average Order Value | Mean order amount | Previous month | Measures purchasing value |
| Churn Rate | Customers lost this month | Previous month | Measures customer retention |
| Customer Satisfaction | Average rating | Previous month | Measures customer experience |

## Revenue

```python
current_revenue = pd.read_sql(
    """
    SELECT SUM(amount) AS total
    FROM orders
    WHERE MONTH(order_date) = %s
      AND YEAR(order_date) = %s
    """,
    engine,
    params=[current_month, current_year]
).iloc[0, 0]

Calculate percentage change:

revenue_change = (
    ((current_revenue - prior_revenue) / prior_revenue) * 100
    if prior_revenue
    else 0
)

Repeat the same pattern for:

Active Users
AOV
Churn Rate
Customer Satisfaction
KPI DataFrame
kpis = pd.DataFrame({
    "Metric": [
        "Revenue",
        "Active Users",
        "AOV",
        "Churn Rate",
        "Satisfaction"
    ],
    "Current": [
        current_revenue,
        current_users,
        current_aov,
        current_churn,
        current_satisfaction
    ],
    "Prior": [
        prior_revenue,
        prior_users,
        prior_aov,
        prior_churn,
        prior_satisfaction
    ],
    "Change_Pct": [
        revenue_change,
        users_change,
        aov_change,
        churn_change,
        satisfaction_change
    ]
})
Validation
 All five KPIs are calculated dynamically.
 No KPI values are hardcoded.
 Current and prior periods are calculated automatically.
 Values come from the clean data layer.
 Percentage changes are mathematically correct.
Task 2: Add Trend Indicators

Create a reusable function that determines the direction and status of each KPI.

Important business rule:

For Revenue, Active Users, AOV, and Satisfaction, an increase is generally positive. For Churn Rate, a decrease is positive.

def get_trend_indicator(change_pct, metric_name):
    if metric_name == "Churn Rate":
        if change_pct < -2:
            return "↓", "#10b981"
        elif change_pct > 2:
            return "↑", "#ef4444"
        else:
            return "→", "#f59e0b"

    if change_pct > 2:
        return "↑", "#10b981"
    elif change_pct < -2:
        return "↓", "#ef4444"
    else:
        return "→", "#f59e0b"

Apply the function:

kpis[["Trend", "Color"]] = kpis.apply(
    lambda row: pd.Series(
        get_trend_indicator(
            row["Change_Pct"],
            row["Metric"]
        )
    ),
    axis=1
)
Status Rules
Condition	Status	Colour
Positive change > 2%	On Track	Green
Change between -2% and +2%	Stable	Yellow
Negative change < -2%	Needs Attention	Red
Churn decrease > 2%	On Track	Green
Churn increase > 2%	Needs Attention	Red
Validation
 Every KPI has a trend indicator.
 Trend direction is correct.
 Churn uses inverse status logic.
 Colours are consistent across all cards.
Task 3: Display Percentage Change

Create a formatted change value:

kpis["Change_Display"] = kpis["Change_Pct"].apply(
    lambda x: f"{x:+.1f}%" if x != 0 else "0%"
)

Example:

Revenue          +12.5%   ↑
Active Users      +5.2%   ↑
AOV               +2.1%   ↑
Churn Rate        -2.8%   ↓
Satisfaction      +0.3%   →

The displayed value must clearly communicate:

Direction
Magnitude
Status
Validation
 Percentage changes use one decimal place.
 Positive values include +.
 Negative values include -.
 Zero changes display as 0%.
Task 4: Design the KPI Dashboard

Create:

kpi_dashboard.py

Use Streamlit with a wide layout.

import streamlit as st

st.set_page_config(layout="wide")

st.title("Sales Performance Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

columns = [col1, col2, col3, col4, col5]

for col, (_, kpi) in zip(kpis.iterrows(), columns):
    with col:
        st.metric(
            label=kpi["Metric"],
            value=kpi["Current"],
            delta=kpi["Change_Display"]
        )

The dashboard should visually follow:

┌──────────────────────────────────────────────────────────────┐
│                SALES PERFORMANCE DASHBOARD                   │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Revenue  │  Active  │   AOV    │  Churn   │ Satisfaction    │
│  $5.2M   │  2,500   │   $145   │   4.8%   │    4.2 / 5     │
│  ↑12.5%  │  ↑5.2%   │  ↑2.1%   │  ↓2.8%   │    →0.3%       │
│  GREEN   │  GREEN   │  GREEN   │  GREEN   │    YELLOW       │
├──────────────────────────────────────────────────────────────┤
│                    DETAILED ANALYTICS                        │
│                                                              │
│                    Charts / Analysis                         │
└──────────────────────────────────────────────────────────────┘
Optional Custom Card Styling

If st.metric() does not provide enough visual status information, use custom HTML/CSS cards.

Each card should communicate:

Metric Name
Current Value
↑ +12.5%
Status: On Track
Validation
 Five KPI cards appear at the top.
 Current values are visible.
 Percentage changes are visible.
 Trend direction is visible.
 Status colour is visible.
 Dashboard remains readable on a wide screen.
Task 5: Validate KPI Data Sources

Create:

kpi_sources.md

Document the source and calculation logic for every KPI.

Example:

# KPI Computation Sources

## Revenue KPI

- **Source:** `vw_daily_revenue`
- **Calculation:** Sum of `order_amount` for the current month.
- **Comparison:** Previous month.
- **Validation:** Cross-checked against the source aggregation.

## Active Users KPI

- **Source:** `vw_active_users`
- **Calculation:** Count of users with activity during the current month.
- **Comparison:** Previous month.
- **Validation:** Cross-checked against the source view.

## Average Order Value KPI

- **Source:** `vw_order_metrics`
- **Calculation:** Average order amount for the current month.
- **Comparison:** Previous month.
- **Validation:** Compared against the underlying order aggregation.

## Churn Rate KPI

- **Source:** `vw_customer_retention`
- **Calculation:** Customers lost during the current month divided by the applicable customer base.
- **Comparison:** Previous month.
- **Validation:** Compared against the retention data layer.

## Customer Satisfaction KPI

- **Source:** `vw_customer_satisfaction`
- **Calculation:** Average customer rating for the current month.
- **Comparison:** Previous month.
- **Validation:** Compared against the underlying ratings aggregation.

## Data Lineage

All KPI values are sourced from validated SQL views or pre-aggregated tables.

No KPI value is hardcoded.

The current and previous periods are calculated dynamically from dates.

Dashboard → KPI Query → Clean Data Layer → Source Data
Validation
 Every KPI has a documented source.
 Calculation logic is documented.
 Current/prior period logic is documented.
 No hardcoded KPI values exist.
 Data lineage is clear.
Bonus: Automatic KPI Updates

The KPI system should be designed so that new data flows through automatically.

Recommended architecture:

New Dataset
     ↓
Data Validation / Cleaning
     ↓
SQL Views / Aggregations
     ↓
KPI Queries
     ↓
Streamlit Dashboard

Use:

SQL views for reusable metric definitions.
Parameterized date ranges.
Scheduled data refreshes.
Dynamic current/prior period calculations.
Dashboard queries against the clean data layer.

This means the dashboard code does not need to change when new monthly data arrives.

Recommended File Structure
assignment-25/
├── kpi_dashboard.py
├── kpi_sources.md
└── output/
    └── screenshots/
Acceptance Criteria
 Five KPIs are implemented.
 Revenue uses current vs prior month.
 Active Users uses current vs prior month.
 AOV uses current vs prior month.
 Churn Rate uses current vs prior month.
 Satisfaction uses current vs prior month.
 Percentage changes are calculated dynamically.
 Trend arrows are displayed.
 Status colours are consistent.
 Churn uses inverse good/bad logic.
 KPI cards appear at the top of the dashboard.
 KPI values are sourced from the clean data layer.
 No hardcoded KPI values are used.
 kpi_sources.md documents data lineage.
 Dashboard updates automatically when new data is available.