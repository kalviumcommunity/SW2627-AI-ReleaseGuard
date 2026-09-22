````md
# Duplicate Detection & Deduplication

## Overview

The Duplicate Detection & Deduplication module identifies and removes duplicate records from datasets.

It detects exact duplicates, near-duplicates based on key columns, and removes duplicate records using configurable keep strategies.

The process also maintains an audit trail and records before-and-after metrics.

---

## Problem

Duplicate records can cause:

- Inflated customer counts
- Incorrect transaction totals
- Duplicated revenue
- Inaccurate analysis
- Unreliable business decisions

Duplicates may occur when data is imported multiple times, combined from different sources, or loaded repeatedly.

---

## Solution

The deduplication workflow follows these steps:

```text
Raw Dataset
     |
     v
Detect Exact Duplicates
     |
     v
Detect Near-Duplicates
     |
     v
Remove Duplicates
     |
     v
Log Removed Records
     |
     v
Compare Before / After
     |
     v
Deduplicated Dataset
````

---

## Exact Duplicate Detection

Exact duplicates are rows where all column values are identical.

The module uses Pandas:

```python
df.duplicated()
```

It reports:

* Number of exact duplicates
* Total duplicate rows including originals
* Sample duplicate records

---

## Near-Duplicate Detection

Near-duplicates are identified using key columns that define record uniqueness.

Example:

```python
key_columns = ['customer_id', 'transaction_date']
```

Records with the same key values but different other fields are treated as near-duplicates.

The module reports:

* Records with duplicate keys
* Unique key combinations containing duplicates
* Sample duplicate groups

---

## Duplicate Removal Strategies

### Keep First

Keeps the first occurrence and removes later duplicates.

```python
df.drop_duplicates(keep='first')
```

### Keep Last

Keeps the last occurrence.

```python
df.drop_duplicates(keep='last')
```

### Most Complete

For near-duplicates, the record with the fewest missing values is retained.

This helps preserve the most complete version of a record.

---

## Audit Logging

All removed duplicate records are saved for auditing and recovery.

```text
output/removed_duplicates_audit.csv
```

An audit summary is also generated:

```text
output/dedup_audit_summary.json
```

The summary records:

* Removal timestamp
* Number of records removed
* Reason for removal
* Audit file location
* Audit note

---

## Before and After Validation

The process compares the dataset before and after deduplication.

Metrics include:

* Rows before
* Rows after
* Rows removed
* Removal percentage
* Number of columns
* Nulls before
* Nulls after
* Timestamp

Example:

```text
DEDUPLICATION FINAL SUMMARY

Rows before:  5,000
Rows after:   4,950
Removed:      50 (1.00%)

Nulls before: 120
Nulls after:  100
```

The results are stored in:

```text
output/dedup_summary.json
```

---

## Main Workflow

```text
1. Load raw dataset
2. Detect exact duplicates
3. Detect near-duplicates using key columns
4. Remove exact duplicates
5. Remove near-duplicates
6. Log removed records
7. Compare before/after metrics
8. Save deduplicated dataset
```

---

## Output

The final deduplicated dataset is saved to:

```text
data/processed/deduplicated_data.csv
```

Audit files:

```text
output/
├── removed_duplicates_audit.csv
├── dedup_audit_summary.json
└── dedup_summary.json
```

---

## Key Benefits

* Detects exact duplicate records.
* Identifies near-duplicates using key columns.
* Supports first, last, and most-complete keep strategies.
* Preserves removed records for auditing.
* Documents the impact of deduplication.
* Prevents duplicate records from distorting analysis.

---

## Conclusion

Duplicate records must be detected and handled before analysis.

By identifying exact and near-duplicates, selecting an appropriate record to retain, logging removed records, and comparing before-and-after metrics, the dataset becomes more reliable, traceable, and suitable for downstream processing.

```
```
