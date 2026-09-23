## Overview

Build the foundation of a multi-section Streamlit analytics dashboard before adding real data, charts, or filters.

The application shell must provide:

- Sidebar navigation
- Three content sections
- Responsive column layouts
- Expandable details
- Consistent visual hierarchy
- Important content above the fold
- Clean-environment setup

---

## Task 1: Sidebar Navigation

Create `app.py` with Streamlit sidebar navigation.

### Sections

- Overview
- Trends
- Data Explorer

Use `st.sidebar.radio()` to control which section appears.

```python
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)
Acceptance
Sidebar is always visible.
Selecting a section changes the main content.
Only the selected section is displayed.
Navigation labels are clear.
Task 2: Three Content Sections

Implement all three pages using st.columns() and st.expander().

Overview

Create a five-column KPI row:

Revenue | Users | AOV | Churn | NPS

Use st.metric() for each KPI.

Add an About These Metrics expander containing brief metric descriptions.

Trends

Include:

Revenue Trends
Customer Metrics
Chart placeholders
At least one column layout
At least one expander for additional information
Data Explorer

Include:

Data summary placeholders
Column-based layout
Filter/data-table placeholders
An expander for optional details
Acceptance
All three sections use columns.
Optional information is hidden inside expanders.
Content appears side by side where appropriate.
Task 3: Visual Hierarchy

Use Streamlit's hierarchy consistently.

Required Elements
st.title() — once per page
st.header() — major sections
st.subheader() — subsections
st.divider() — between major sections

Example:

st.title("Trend Analysis")

st.header("Revenue Trends")
st.subheader("Monthly Revenue")
st.write("Chart placeholder")

st.divider()

st.header("Customer Metrics")
st.subheader("Active Customers")
st.write("Chart placeholder")
Acceptance
All three sections follow the same hierarchy.
Pages are easy to scan.
Dividers clearly separate major content areas.
Task 4: Clean Environment Setup

Create requirements.txt containing all dependencies.

streamlit==1.38.0
pandas==2.1.4

The application must run from a clean clone using:

pip install -r requirements.txt
streamlit run app.py
Acceptance
No missing imports.
No hardcoded local file paths.
No startup errors.
First launch works from a clean environment.
Task 5: Above-the-Fold Layout

The most important content must appear immediately when the dashboard loads.

Requirements
KPI cards at the top of Overview.
No unnecessary introductory content before KPIs.
No large blank spaces.
Primary information visible without scrolling.
Acceptance

On first load, users immediately see the dashboard navigation and key Overview metrics.

File Structure
assignment-27/
├── app.py
└── requirements.txt
Acceptance Criteria
 Sidebar navigation works.
 Overview, Trends, and Data Explorer sections are implemented.
 Columns are used for side-by-side content.
 Expanders contain optional details.
 Visual hierarchy is consistent.
 Requirements file contains all dependencies.
 App runs successfully from a clean environment.
 KPIs appear above the fold.
 No unnecessary blank space or technical errors.