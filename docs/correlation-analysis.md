# **Correlation Analysis & Churn Prediction — PRD**

## **1. Overview**

Build a correlation analysis workflow for churn prediction.

The goal is to identify meaningful relationships between features and churn while avoiding incorrect causal conclusions.

For example, if `support_tickets` has a correlation of `r = 0.8` with churn, this does not prove that support tickets cause churn. An underlying factor such as customer pain may cause both.

---

## **2. Objectives**

- Calculate Pearson correlations.
- Calculate Spearman correlations.
- Compare correlation methods.
- Visualize correlations using a heatmap.
- Identify strongly correlated feature pairs.
- Interpret correlations without assuming causation.
- Remove redundant features for model preparation.

---

## **3. Task 1 — Pearson & Spearman Correlation**

Calculate both Pearson and Spearman correlation matrices:

```python
pearson_corr = df.corr(method="pearson")
spearman_corr = df.corr(method="spearman")

comparison = pd.DataFrame({
    "pearson": pearson_corr["churn"],
    "spearman": spearman_corr["churn"]
})

print(comparison)

Compare which feature correlations differ between Pearson and Spearman.

4. Task 2 — Correlation Heatmap

Create and save a Pearson correlation heatmap:

import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 10))

sns.heatmap(
    pearson_corr,
    annot=True,
    cmap="coolwarm",
    center=0,
    ax=ax
)

ax.set_title("Feature Correlation Matrix")

plt.tight_layout()
plt.savefig("output/correlation_heatmap.png")
5. Task 3 — Identify Strong Correlations

Find feature pairs with absolute correlation greater than 0.7:

corr_flat = pearson_corr.unstack()

strong = (
    corr_flat[corr_flat.abs() > 0.7]
    .sort_values(ascending=False)
)

strong_pairs = strong[strong != 1.0].head(10)

print(strong_pairs)

Identify the strongest relationships and avoid duplicate/self-correlations.

6. Task 4 — Business Interpretation

Interpret strong correlations without assuming causation.

Example:

analysis = {
    "support_tickets <-> churn": {
        "correlation": 0.8,
        "possible_directions": [
            "support_tickets -> churn",
            "churn -> support_tickets",
            "customer_pain -> both"
        ],
        "interpretation": (
            "Customer pain may influence both support tickets "
            "and churn; correlation alone cannot establish causation."
        ),
        "action": "Investigate underlying customer pain and support issues."
    }
}

print(json.dumps(analysis, indent=2))

Document alternative explanations for strong correlations.

7. Task 5 — Feature Selection

Identify redundant features using correlation.

Example:

df_features = df[
    [
        "engagement",
        "transactions_per_month",
        "support_tickets",
        "churn"
    ]
]

# engagement and transactions_per_month have r = 0.92

df_features = df_features.drop(
    "engagement",
    axis=1
)

print(df_features.corr())

Keep the more interpretable feature when two features provide highly redundant information.