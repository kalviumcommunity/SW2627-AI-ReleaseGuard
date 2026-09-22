# **Outlier Detection & Treatment — PRD**

## **1. Overview**

Implement an outlier detection and treatment pipeline for customer revenue and age data.

The pipeline should:

- Detect extreme values using Z-score.
- Detect outliers using IQR.
- Cap extreme values where appropriate.
- Flag outliers without deleting records.
- Document all cleaning decisions in a cleaning log.

---

## **2. Objectives**

- Identify statistically unusual values.
- Handle extreme revenue values.
- Detect impossible age values.
- Preserve useful data where possible.
- Make outlier treatment transparent and reproducible.

---

## **3. Z-Score Detection**

Detect values more than **3 standard deviations** from the mean.

```python
from scipy import stats

df["revenue_zscore"] = np.abs(
    stats.zscore(df["revenue"])
)

z_outliers = df[
    df["revenue_zscore"] > 3
]

print(f"Z-score outliers: {len(z_outliers)}")
Requirements
Calculate Z-scores for revenue.
Identify values where Z > 3.
Report the number of detected outliers.
4. IQR Detection

Detect values outside 1.5 × IQR.

Q1 = df["revenue"].quantile(0.25)
Q3 = df["revenue"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df["is_outlier_iqr"] = (
    (df["revenue"] < lower) |
    (df["revenue"] > upper)
)
Requirements
Calculate Q1 and Q3.
Calculate IQR.
Calculate lower and upper boundaries.
Flag values outside the boundaries.
5. Cap Revenue Outliers

Use a capping strategy for revenue.

Replace values outside the IQR boundaries with the corresponding boundary value.

df["revenue_capped"] = df["revenue"].clip(
    lower=lower,
    upper=upper
)

Validate the results:

print(
    f"Before: min={df['revenue'].min()}, "
    f"max={df['revenue'].max()}"
)

print(
    f"After: min={df['revenue_capped'].min()}, "
    f"max={df['revenue_capped'].max()}"
)
Decision
Column: revenue
Strategy: Cap
Method: IQR
Reason: Preserve customer records while reducing the influence of extreme values.
6. Flag Outliers

Create a binary flag using both detection methods.

df["is_outlier"] = (
    df["is_outlier_iqr"] |
    (df["revenue_zscore"] > 3)
)

Separate normal records and anomalies:

normal = df[~df["is_outlier"]]
anomalies = df[df["is_outlier"]]

print(f"Normal records: {len(normal)}")
print(f"Anomalies: {len(anomalies)}")
Requirements
Combine Z-score and IQR detection.
Keep the original records.
Create an is_outlier flag.
Report normal and anomalous record counts.
7. Age Validation

Identify impossible age values such as ages above 150.

Example:

df["age_outlier"] = (
    (df["age"] < 0) |
    (df["age"] > 120)
)

Document the selected valid age range and handling strategy.

Possible strategies:

Flag invalid ages.
Replace with null.
Remove records if required.
Cap values only when justified.
8. Cleaning Log

Create a cleaning log documenting every outlier transformation.

cleaning_log = [{
    "column": "revenue",
    "method": "IQR",
    "action": "cap",
    "threshold_lower": lower,
    "threshold_upper": upper,
    "affected_rows": df["is_outlier_iqr"].sum(),
    "date": pd.Timestamp.now()
}]

log_df = pd.DataFrame(cleaning_log)

log_df.to_csv(
    "output/cleaning_log.csv",
    index=False
)

The log should record:

Column name
Detection method
Treatment/action
Lower threshold
Upper threshold
Number of affected rows
Processing date