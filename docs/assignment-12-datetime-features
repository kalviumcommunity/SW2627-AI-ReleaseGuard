# Date & Time Feature Engineering

## Overview

This project implements a date and time transformation pipeline for transaction data. It converts datetime strings into usable datetime features and performs temporal analysis to identify purchasing patterns, customer inactivity, and peak activity periods.

## Problem

Raw transaction data often contains dates and times as strings, making temporal analysis difficult. The pipeline transforms these values into structured datetime features for analysis and machine learning.

## Solution

The pipeline performs the following steps:

1. Parse transaction dates
2. Extract date and time features
3. Analyze weekly transaction trends
4. Calculate customer purchase recency
5. Analyze activity by day and hour
6. Validate the generated temporal features

## 1. Datetime Parsing

The `transaction_date` column is converted from a string into a datetime object using the explicit format:

```python
%Y-%m-%d %H:%M:%S
```

The resulting column is verified to have a `datetime64` data type.

## 2. Date & Time Features

The pipeline extracts:

* `day_of_week` — name of the day
* `hour` — hour of the transaction
* `week_num` — ISO calendar week

Example:

```python
df["day_of_week"] = df["transaction_date"].dt.day_name()
df["hour"] = df["transaction_date"].dt.hour
df["week_num"] = df["transaction_date"].dt.isocalendar().week
```

The distribution of transactions by hour is also analyzed using a histogram.

## 3. Weekly Analysis

The transaction date is used as the datetime index to perform weekly aggregation.

The pipeline calculates:

* Weekly transaction sum
* Weekly transaction count
* Weekly transaction mean

Example:

```python
weekly = df.resample("W").agg({
    "amount": ["sum", "count", "mean"]
})
```

This helps identify weekly transaction trends.

## 4. Customer Recency

The number of days since each customer's last purchase is calculated using datetime arithmetic.

This helps identify:

* Recently active customers
* Customers with longer inactivity periods
* Distribution of customer recency
* Potential inactive customers

## 5. Day & Hour Activity Analysis

Transactions are grouped by:

* Day of the week
* Hour of the day

The pipeline calculates:

* Total transaction amount
* Transaction count
* Average transaction amount

A pivot table is created with:

* Rows → Hour
* Columns → Day of week

This helps identify peak transaction activity windows.

## 6. Validation & Testing

The pipeline validates the generated temporal features by checking:

* Minimum transaction date
* Maximum transaction date
* Total date span
* Minimum and maximum hour
* Number of weeks
* Minimum customer recency
* Maximum customer recency

These checks help ensure that the transformations were applied correctly.

## 7. Output

The pipeline generates:

```text
data/processed/datetime_features.csv
output/temporal_analysis.json
```

### `datetime_features.csv`

Contains the processed transaction data along with the engineered datetime features.

### `temporal_analysis.json`

Contains the generated temporal analysis and validation metrics.

## 8. Workflow

```text
Load Transaction Data
        ↓
Parse Datetime
        ↓
Extract Date & Time Features
        ↓
Weekly Aggregation
        ↓
Customer Recency Analysis
        ↓
Day & Hour Analysis
        ↓
Peak Activity Detection
        ↓
Validation
        ↓
Generate Outputs
```

## Key Benefits

* Converts raw datetime strings into usable features
* Enables weekly transaction trend analysis
* Measures customer purchase recency
* Identifies peak activity periods
* Provides structured temporal analysis
* Validates datetime transformations

## Conclusion

The Date & Time Feature Engineering pipeline transforms raw transaction timestamps into meaningful temporal features and provides insights into transaction trends, customer activity, and peak purchasing periods.
