### `docs/dataset-intake-validation.md`

````md
# Dataset Intake & Source Validation

## Overview

The Dataset Intake & Source Validation module acts as a quality gate before data enters the processing pipeline.

It validates incoming datasets and identifies common problems such as missing files, unsupported formats, incorrect schemas, encoding issues, and unexpected dataset dimensions.

The goal is to detect data problems early and provide clear validation results before any transformation or analysis begins.

---

## Problem

Incoming datasets may fail because:

- The file does not exist.
- The file is empty.
- The file format is unsupported.
- Required columns are missing.
- Unexpected columns are present.
- The file uses an unexpected encoding.
- Dataset dimensions differ from expected values.

If these problems are discovered only during analysis, debugging becomes difficult and downstream processing may fail.

---

## Solution

A validation layer runs before the main data pipeline.

```text
Incoming Dataset
       |
       v
File Existence Check
       |
       v
Format Validation
       |
       v
Schema Validation
       |
       v
Encoding Detection
       |
       v
Dimension Capture
       |
       v
Validation Report
       |
       v
Safe for Processing
````

If a critical validation check fails, the pipeline stops and reports the problem.

---

## Validation Checks

### 1. File Existence

The system checks:

* Whether the file exists.
* Whether the file contains data.

Example errors:

```text
File not found: data/input.csv
File is empty
```

---

### 2. File Format

The system verifies that the incoming file uses a supported format.

Supported formats include:

* CSV
* JSON
* XLSX

Example:

```text
Format valid: csv
```

Unsupported formats produce a clear error:

```text
Unsupported: txt
```

---

### 3. Schema Validation

The system compares the incoming dataset columns with the expected schema.

It identifies:

* Missing columns
* Extra columns

Example:

```text
Missing: {'revenue'}
```

or:

```text
Extra: {'customer_name'}
```

This helps detect unexpected changes in upstream data.

---

### 4. Encoding Detection

The system checks the encoding of the incoming file.

This helps identify files that use encodings such as:

* UTF-8
* Latin-1
* CP1252

The detected encoding and confidence level are reported.

Example:

```text
Detected: latin-1 (95%)
```

---

### 5. Dimensions

The validation process captures basic dataset statistics:

* Number of rows
* Number of columns
* File size in MB

Example:

```text
Rows: 500000
Columns: 4
File Size: 12.5 MB
```

These values can be used as baseline metrics to identify unexpected changes in future datasets.

---

## Validation Report

The validation results are combined into a single report.

The report contains:

* Timestamp
* File path
* Validation check results
* Dataset statistics

Example structure:

```json
{
  "timestamp": "2026-09-22T10:00:00",
  "filepath": "data/input.csv",
  "checks": {
    "file_exists": "File exists and has content",
    "format": "Format valid: csv",
    "schema": "Schema valid",
    "encoding": "Detected: utf-8 (99%)"
  },
  "statistics": {
    "rows": 500000,
    "columns": 4,
    "file_size_mb": 12.5
  }
}
```

---

## Fail-Fast Validation

Validation follows a fail-fast approach.

A later validation check should not run when an earlier critical check has already failed.

For example:

```text
Missing File
     ↓
Validation Failed
     ↓
Stop Pipeline
```

There is no reason to perform schema or dimension checks when the input file does not exist.

This prevents invalid data from reaching downstream processing.

---

## Actionable Error Messages

Validation messages should explain what went wrong instead of using vague messages.

### Poor

```text
Validation failed
```

### Better

```text
Missing column: revenue
```

### Poor

```text
Encoding error
```

### Better

```text
Detected latin-1 but expected utf-8
```

Specific messages make troubleshooting faster.

---

## Expected Outcome

The Dataset Intake & Source Validation module provides a quality firewall between incoming data and downstream processing.

The pipeline should only continue when the incoming dataset passes the required validation checks.

```text
Dataset
   ↓
Validate
   ↓
Pass ─────────→ Process Dataset
   |
   └── Fail ──→ Report Problem & Stop
```

---

## Key Benefits

* Detects malformed input early.
* Prevents invalid data from entering the pipeline.
* Provides clear and actionable error messages.
* Captures useful dataset statistics.
* Makes data pipelines more reliable.
* Simplifies troubleshooting and debugging.

---
