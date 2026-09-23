## Overview

Add interactive sidebar filters to the Streamlit dashboard so users can explore the dataset dynamically.

All widgets must be connected to the DataFrame, and every downstream chart, metric, and table must use the filtered data.

---

## Task 1: Add Interactive Widgets

Add at least three different widget types:

- Date range picker
- Multi-select for segments
- Revenue range slider
- Optional: radio button

Example:

```python
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["date"].min(), df["date"].max())
)

selected_segments = st.sidebar.multiselect(
    "Segments",
    options=df["segment"].unique().tolist(),
    default=df["segment"].unique().tolist()
)

min_rev, max_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=int(df["revenue"].min()),
    max_value=int(df["revenue"].max()),
    value=(int(df["revenue"].min()), int(df["revenue"].max()))
)
Acceptance
At least three widget types are visible.
Each widget accepts user input.
Widgets are clearly labeled.
Task 2: Filter the DataFrame

Combine all widget values into one filtering pipeline.

filtered_df = df[
    (df["date"] >= pd.Timestamp(date_range[0]))
    & (df["date"] <= pd.Timestamp(date_range[1]))
    & (df["segment"].isin(selected_segments))
    & (df["revenue"] >= min_rev)
    & (df["revenue"] <= max_rev)
]

st.write(
    f"Showing {len(filtered_df):,} of {len(df):,} records"
)

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)
Acceptance
Every widget affects the DataFrame.
Row count updates immediately.
All downstream charts and metrics use filtered_df.
No chart or KPI continues using the unfiltered df.
Task 3: Set Useful Defaults

Widgets must load with the complete dataset selected.

Defaults
Date range → minimum to maximum dataset date
Segments → all segments selected
Revenue slider → minimum to maximum revenue
Acceptance

On first load:

Full dataset is visible.
No filter produces an empty state.
Users narrow the dataset from a useful starting point.
Task 4: Handle Empty Results

Filtering must never crash the application.

if filtered_df.empty:
    st.warning(
        "No data matches the current filters. "
        "Try broadening your selection."
    )
    st.stop()
Acceptance

Test an impossible combination such as a future date range.

The app must:

Display a helpful warning.
Avoid errors.
Stop rendering dependent content safely.
Task 5: Add Reset Filters

Add a sidebar Reset Filters button.

if st.sidebar.button("Reset Filters"):
    st.rerun()

The reset must restore the default filter state and show the complete dataset.

Acceptance
Reset button is visible.
Clicking it restores default filters.
Full dataset appears again.
Recommended Filter Flow
Raw Data
   ↓
Sidebar Widgets
   ↓
Filter DataFrame
   ↓
Empty-State Check
   ↓
Filtered Metrics
   ↓
Filtered Charts
   ↓
Filtered Table
File Structure
assignment-28/
└── app.py
Acceptance Criteria
 At least three widget types implemented.
 Date filter works.
 Segment filter works.
 Revenue threshold filter works.
 All filters combine correctly.
 Downstream metrics/charts use filtered data.
 Defaults show the complete dataset.
 Empty results display a warning instead of crashing.
 Reset Filters restores the default state.
 Filtered row count is displayed.