# **Time Series Analysis & Trend Detection — PRD**

## **1. Overview**

Analyze daily revenue data to identify sustainable business trends hidden by daily fluctuations.

The workflow will aggregate data into different time periods, calculate rolling averages, measure period-over-period growth, track cumulative revenue, and determine whether the business is accelerating, declining, or stable.

---

## **2. Objectives**

- Resample daily data into weekly and monthly periods.
- Calculate 7-day and 30-day rolling averages.
- Compare raw revenue with smoothed trends.
- Calculate month-over-month revenue growth.
- Track cumulative revenue.
- Identify overall trend direction and magnitude.
- Document business implications and recommended actions.

---

## **3. Task 1 — Resample Data by Time Period**

Convert the date column to a datetime index and aggregate revenue/orders:

```python
df_ts = df.set_index("date")

weekly_revenue = df_ts["revenue"].resample("W").sum()
weekly_count = df_ts["orders"].resample("W").count()
weekly_avg = df_ts["revenue"].resample("W").mean()

monthly_revenue = df_ts["revenue"].resample("ME").sum()
monthly_count = df_ts["orders"].resample("ME").count()

print(weekly_revenue)
print(monthly_revenue)

Requirements:

Resample to at least weekly and monthly periods.
Use multiple aggregation functions such as sum, count, and mean.
Identify the period with the highest revenue.
4. Task 2 — Rolling Window Averages

Calculate 7-day and 30-day rolling revenue averages:

df["revenue_ma7"] = (
    df["revenue"].rolling(window=7).mean()
)

df["revenue_ma30"] = (
    df["revenue"].rolling(window=30).mean()
)

Visualize raw revenue alongside both rolling averages:

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["revenue"],
    label="Raw",
    alpha=0.3
)

plt.plot(
    df["date"],
    df["revenue_ma7"],
    label="7-day MA"
)

plt.plot(
    df["date"],
    df["revenue_ma30"],
    label="30-day MA"
)

plt.legend()
plt.tight_layout()
plt.savefig("output/rolling_avg.png")

Identify periods where the rolling averages reveal trends that are difficult to see in the raw daily data.

5. Task 3 — Month-over-Month Growth

Calculate monthly revenue changes:

monthly_revenue = (
    df_ts["revenue"]
    .resample("ME")
    .sum()
)

mom_change = monthly_revenue.pct_change() * 100

print(mom_change)

Separate growth and decline periods:

growth_months = mom_change[mom_change > 0]
decline_months = mom_change[mom_change < 0]

print("Growth months:")
print(growth_months)

print("Decline months:")
print(decline_months)

Determine whether the observed pattern indicates accelerating growth, declining momentum, or relative stability.

6. Task 4 — Cumulative Revenue

Calculate accumulated revenue:

df["cumulative_revenue"] = (
    df["revenue"].cumsum()
)

Visualize cumulative revenue:

plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["cumulative_revenue"]
)

plt.title("Cumulative Revenue Over Time")
plt.tight_layout()
plt.savefig("output/cumulative.png")

Report the total revenue accumulated by the end of the analysis period:

total_revenue = df["cumulative_revenue"].iloc[-1]

print(f"Total revenue: ${total_revenue:,.0f}")
7. Task 5 — Trend Analysis & Business Implications

Use the 30-day rolling average to determine the recent trend:

recent_ma30 = df["revenue_ma30"].dropna().iloc[-30:]

start_value = recent_ma30.iloc[0]
end_value = recent_ma30.iloc[-1]

change = end_value - start_value
trend_magnitude = (
    change / start_value
) * 100

if trend_magnitude > 1:
    trend_direction = "up"
elif trend_magnitude < -1:
    trend_direction = "down"
else:
    trend_direction = "flat"

print(f"Trend: {trend_direction.upper()}")
print(f"30-day change: {trend_magnitude:.1f}%")
print(f"Latest MoM growth: {mom_change.iloc[-1]:.1f}%")
print(f"Revenue volatility: ${df['revenue'].std():,.0f}")

Document:

Trend direction: up, down, or flat.
Magnitude of recent change.
Latest month-over-month growth.
Revenue volatility.
Whether the trend appears sustainable.
Possible business implications.
Recommended action based on the observed trend.

Example interpretation:

TREND ANALYSIS

Rolling Average Trend: UP
30-day Change: +X.X%
Latest MoM Growth: +X.X%
Revenue Volatility: $X,XXX

Business Implications:
- Revenue is showing sustained upward/downward/flat momentum.
- Rolling averages provide a clearer signal than daily fluctuations.
- Investigate the factors contributing to the observed trend.

Recommended Action:
- Monitor the rolling trend and MoM growth.
- Investigate significant changes in revenue.
- Use sustainable metrics rather than individual daily fluctuations
  when making business decisions.