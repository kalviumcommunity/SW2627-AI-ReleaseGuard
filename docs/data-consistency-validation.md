````md
# Data Consistency & Validation Rules

## Overview

This project implements systematic validation rules to detect invalid, incomplete, malformed, and logically inconsistent records before they are used for analysis.

The validation pipeline checks multiple data quality conditions, isolates failed records, and generates a structured validation report.

## Problem

The raw dataset may contain:

- Birth dates in the future
- Negative prices
- Missing customer IDs
- Missing emails
- Invalid email formats
- Invalid phone numbers
- Campaign end dates before start dates

Using such records directly can lead to incorrect analysis and unreliable business decisions.

## Validation Rules

The pipeline implements the following validation categories.

### 1. Range Checks

Age must be between 0 and 150.

```python
df["valid_age"] = (df["age"] >= 0) & (df["age"] <= 150)
````

Price must not be negative.

```python
df["valid_price"] = df["price"] >= 0
```

Birth dates must be between 1920-01-01 and the current date.

```python
df["valid_date"] = (
    (df["birth_date"] >= "1920-01-01") &
    (df["birth_date"] <= pd.Timestamp.now())
)
```

### 2. Null Constraints

Critical fields must not be missing.

```python
df["valid_customer_id"] = df["customer_id"].notna()
df["valid_email"] = df["email"].notna()
```

### 3. Format Validation

Email addresses must contain `@`.

```python
df["valid_email_format"] = df["email"].str.contains("@", na=False)
```

Phone numbers must contain exactly 10 digits.

```python
df["valid_phone"] = df["phone"].str.match(r"^\d{10}$", na=False)
```

### 4. Business Rule Validation

The campaign end date must not be before the start date.

```python
df["valid_date_order"] = df["end_date"] >= df["start_date"]
```

### 5. Combined Validation

All validation rules are combined to determine whether each record passes validation.

```python
validation_cols = [
    "valid_age",
    "valid_price",
    "valid_customer_id",
    "valid_email_format",
    "valid_date_order"
]

df["passes_all_checks"] = df[validation_cols].all(axis=1)
```

## Failure Isolation

Records that fail one or more validation rules are isolated into a separate dataset.

```python
failures = df[~df["passes_all_checks"]]

failures.to_csv(
    "output/validation_failures.csv",
    index=False
)
```

This keeps invalid records traceable without allowing them to proceed into analysis.

## Validation Report

The validation process reports:

* Total records
* Number of passed records
* Number of failed records
* Failure counts for individual validation rules

Example:

```python
print(f"Records: {len(df)}")
print(f"Passed: {df['passes_all_checks'].sum()}")
print(f"Failed: {(~df['passes_all_checks']).sum()}")
```

A structured report is stored in:

```text
output/validation_report.json
```

## Clean Dataset

Only records that pass all required validation checks are allowed to proceed to analysis.

```python
df_clean = df[df["passes_all_checks"]]
```

The validated dataset is stored in:

```text
data/processed/validated_data.csv
```

## Workflow

```text
Raw Dataset
     ↓
Range Checks
     ↓
Null Constraints
     ↓
Format Validation
     ↓
Business Rule Validation
     ↓
Combine Validation Results
     ↓
Isolate Failed Records
     ↓
Generate Validation Report
     ↓
Validated Dataset
     ↓
Analysis
```

## Output Files

```text
output/validation_failures.csv
output/validation_report.json
data/processed/validated_data.csv
```

### `validation_failures.csv`

Contains records that failed one or more validation rules.

### `validation_report.json`

Contains structured validation results and pass/fail counts.

### `validated_data.csv`

Contains records that passed all required validation checks.

## Key Benefits

* Detects invalid data before analysis
* Prevents corrupted records from reaching downstream analysis
* Provides multiple validation rule categories
* Isolates failed records for investigation
* Produces a traceable validation report
* Makes validation systematic and repeatable

## Conclusion

The Data Consistency & Validation pipeline provides a systematic way to identify and isolate invalid records before analysis. Range checks, null constraints, format validation, and business rules work together to improve data reliability and maintain a clear validation audit trail.

```
```
