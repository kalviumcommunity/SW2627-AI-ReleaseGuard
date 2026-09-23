# Business Analytics — Five Data Visualizations

## Branch
`assignment-24-five-visualizations`

## Commit
`visualizations: create five chart types with consistent styling and annotations`

---

# Overview

Create five business-focused visualizations using appropriate chart types.

Each visualization must:

- Answer a specific business question.
- Use the correct chart type.
- Have complete labels and titles.
- Follow one consistent colour palette.
- Include at least one meaningful annotation.
- Be exported as a high-resolution PNG.
- Be documented in `CHARTS_README.md`.

---

# Task 1: Create Five Chart Types

## Chart 1 — Revenue by Product Line

### Type
Horizontal bar chart

### Business Question

> Which product lines generate the most revenue during the last 90 days?

Query:

```python
revenue_by_product = pd.read_sql(
    """
    SELECT
        product_line,
        SUM(order_amount) AS revenue
    FROM orders
    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
    GROUP BY product_line
    ORDER BY revenue DESC
    """,
    engine
)

Create a horizontal bar chart and save:

output/chart1_revenue_by_product.png

Requirements:

Product line on Y-axis.
Revenue on X-axis.
Revenue values displayed on bars.
Clear title and axis labels.
Chart 2 — Revenue Trend
Type

Multi-line chart

Business Question

How has revenue changed over the last 12 months for the top three products?

Requirements:

Monthly time axis.
One line per top product.
Legend identifying each product.
Mark important increases/decreases.
Save as:
output/chart2_revenue_trend.png
Chart 3 — Order Value Distribution
Type

Histogram

Business Question

What is the distribution and typical range of customer order values?

Requirements:

Use order amount.
Create meaningful bins.
Label X-axis as order value.
Label Y-axis as order count/frequency.
Highlight important peaks or ranges.
Save as:
output/chart3_order_value_distribution.png
Chart 4 — Revenue Composition
Type

Stacked bar chart

Business Question

How does the revenue contribution of each product line change across quarters?

Requirements:

X-axis: Quarter.
Y-axis: Revenue.
Each product line represented by a consistent colour.
Include legend.
Add data labels where readable.
Annotate an important composition change.
Save as:
output/chart4_revenue_composition.png
Chart 5 — Marketing Spend vs Revenue
Type

Scatter plot

Business Question

What relationship exists between marketing spend and generated revenue?

Requirements:

X-axis: Marketing Spend ($).
Y-axis: Revenue ($).
Plot individual observations.
Add a trend line where appropriate.
Highlight an important outlier.
Save as:
output/chart5_marketing_vs_revenue.png

Correlation should be described as an association, not automatically interpreted as causation.

Task 2: Label All Charts Completely

Every chart must include:

Clear descriptive title.
X-axis label.
Y-axis label.
Appropriate units.
Legend for multi-series charts.
Data labels where they improve readability.
Gridlines where useful.
Currency formatting for monetary values.

Example:

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    df["date"],
    df["revenue"],
    marker="o",
    linewidth=2,
    label="Revenue"
)

ax.set_title(
    "Monthly Revenue Trend — Last 12 Months",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Revenue ($)", fontsize=12)

ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
Validation

Document the labels used for each chart in CHARTS_README.md.

Task 3: Apply a Consistent Colour Palette

Define one company-wide palette and reuse it across all visualizations.

PALETTE = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "neutral": "#7f7f7f"
}

CHART_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd"
]
Usage
Blue: primary metric.
Orange: comparison metric.
Green: positive/target indicator.
Red: warning, decline, or outlier.
Gray: neutral/reference information.
Purple: additional category where required.

Use the same product/category colour throughout different charts so users can recognize the same category consistently.