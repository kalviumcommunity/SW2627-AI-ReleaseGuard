# **Customer Feature Engineering — PRD**

## **1. Overview**

Engineer meaningful customer features from raw transaction data to support better modeling and customer segment analysis.

The pipeline should create:

- Engagement metrics
- Spend tiers
- Spend quartiles
- RFM-based customer scores
- Feature validation checks

---

## **2. Objectives**

- Convert raw transaction data into useful analytical features.
- Calculate customer engagement and spending metrics.
- Group customers into meaningful tiers.
- Create a composite RFM score.
- Validate the generated features.

---

## **3. Task 1 — Compute Ratio Features**

Create the following features:

```python
df["transactions_per_month"] = (
    df["total_transactions"] /
    (df["days_as_customer"] / 30)
)

df["avg_spend_per_transaction"] = (
    df["total_spent"] /
    df["total_transactions"]
)

df["lifetime_value_per_month"] = (
    df["total_spent"] /
    (df["days_as_customer"] / 30)
)

Validate the results:

print(
    df[
        [
            "transactions_per_month",
            "avg_spend_per_transaction",
            "lifetime_value_per_month"
        ]
    ].describe()
)
4. Task 2 — Engagement Tier

Create equal-width engagement tiers:

df["engagement_tier"] = pd.cut(
    df["transactions_per_month"],
    bins=[0, 2, 10, float("inf")],
    labels=["low", "medium", "high"]
)

Validate:

print(df["engagement_tier"].value_counts())
Tiers
Range	Tier
0–2	Low
2–10	Medium
10+	High
5. Task 3 — Spend Quartiles

Divide customers into four groups based on total spending:

df["spend_quartile"] = pd.qcut(
    df["total_spent"],
    q=4,
    labels=["Q1", "Q2", "Q3", "Q4"]
)

Validate:

print(df["spend_quartile"].value_counts())
6. Task 4 — RFM Composite Score

Create Recency, Frequency, and Monetary scores.

df["recency_score"] = pd.qcut(
    df["days_since_last_purchase"],
    q=5,
    labels=[5, 4, 3, 2, 1]
)

df["frequency_score"] = pd.qcut(
    df["purchase_count"],
    q=5,
    labels=[1, 2, 3, 4, 5]
)

df["monetary_score"] = pd.qcut(
    df["total_spent"],
    q=5,
    labels=[1, 2, 3, 4, 5]
)

Calculate the composite score:

df["rfm_score"] = (
    df["recency_score"].astype(int) +
    df["frequency_score"].astype(int) +
    df["monetary_score"].astype(int)
)

The RFM score should range from 3 to 15.

7. Task 5 — Feature Validation

Check feature distributions:

print(
    df["engagement_tier"].value_counts()
)

print(
    f"RFM score range: "
    f"{df['rfm_score'].min()}-"
    f"{df['rfm_score'].max()}"
)

Check for missing values:

print(
    df[
        [
            "engagement_tier",
            "spend_quartile",
            "rfm_score"
        ]
    ].isna().sum()
)