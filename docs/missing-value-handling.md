````md
# Missing Value Detection & Imputation

## Overview

The Missing Value Detection & Imputation module identifies incomplete records and applies appropriate strategies to handle missing values.

The goal is to make null handling intentional, documented, and auditable while preserving data quality.

---

## Problem

Real-world datasets commonly contain missing values such as:

- Missing customer emails
- Null transaction amounts
- Missing categories or regions
- Blank timestamps
- Missing critical identifiers

Incorrect handling can distort analysis, remove useful records, or create artificial data.

---

## Solution

The workflow follows these steps:

```text
Raw Dataset
     |
     v
Analyze Missing Values
     |
     v
Choose Strategy
     |
     +--> Mean/Median → Numerical
     |
     +--> Mode → Categorical
     |
     +--> Forward Fill → Time-Series
     |
     +--> Drop Rows → Critical Columns
     |
     v
Document Decisions
     |
     v
Validate Before/After Metrics
     |
     v
Cleaned Dataset
````

---

## Missing Value Analysis

Before treatment, the dataset is analyzed for:

* Null count
* Null percentage
* Data type
* Meaning of the missing value
* Total rows
* Total cells
* Total missing cells

Example:

```text
BEFORE IMPUTATION
Column       Null Count    Null %
amount       45            0.90%
email        30            0.60%
category     12            0.24%
```

---

## Imputation Strategies

### 1. Mean / Median

Used for numerical columns.

**Median** is preferred when data contains outliers because it is more resistant to extreme values.

Example:

```python
df['amount'].fillna(df['amount'].median())
```

Mean can also be used when it appropriately represents the numerical distribution.

---

### 2. Mode

Used for categorical columns.

The mode is the most frequently occurring value.

Example:

```python
df['category'].fillna(df['category'].mode()[0])
```

This preserves the existing categorical distribution more appropriately than inventing a new category.

---

### 3. Forward Fill

Used for time-series data.

The previous known value is used to fill the missing value.

```python
df['last_updated'].fillna(method='ffill')
```

This assumes that the previous value remains valid until a new value appears.

---

### 4. Drop Rows

Rows can be removed when critical columns are missing.

Example:

```python
df.dropna(subset=['customer_id', 'email'])
```

Critical identifiers should not be artificially generated because they must uniquely identify real records.

---

## Over-Imputation Risk

Excessive imputation can create artificial data and distort:

* Statistics
* Correlations
* Distributions
* Model results
* Business decisions

The percentage of imputed values should therefore be tracked and documented.

---

## Decision Documentation

Every imputation decision should record:

* Column name
* Column type
* Null count before treatment
* Strategy used
* Value used, when applicable
* Business reasoning
* Risk assessment

Example:

```json
{
  "strategy": "median_imputation",
  "business_reasoning": "Median is representative of typical transactions and resistant to high-value outliers.",
  "risk_assessment": "Low"
}
```

The decisions are stored in:

```text
output/imputation_decisions.json
```

---

## Before and After Validation

The workflow compares the dataset before and after treatment.

Metrics include:

* Total rows before
* Total rows after
* Rows removed
* Total nulls before
* Total nulls after
* Null count by column
* Null percentage by column

This makes the impact of imputation visible and auditable.

---

## Workflow

```text
1. Load raw dataset
2. Analyze missing values
3. Drop rows with critical nulls
4. Apply numerical imputation
5. Apply categorical imputation
6. Apply forward fill for time-series data
7. Document decisions
8. Validate before/after metrics
9. Save cleaned dataset
```

---

## Output

The module produces:

```text
output/
└── imputation_decisions.json

data/
└── processed/
    └── cleaned_data.csv
```

---

## Key Benefits

* Detects missing values before treatment.
* Uses different strategies based on column type and context.
* Prevents blind imputation.
* Documents business reasoning.
* Tracks the impact of cleaning.
* Produces an auditable data-cleaning process.

---

## Conclusion

Missing values should never be handled blindly.

By analyzing nulls first, selecting an appropriate strategy, documenting the reasoning, and comparing before-and-after metrics, the data-cleaning process becomes intentional, transparent, and defensible.

```
```
