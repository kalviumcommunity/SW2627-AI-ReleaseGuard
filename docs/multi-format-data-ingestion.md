# **Multi-Format Data Ingestion**

## **Objective**

Build a Python ingestion script that loads data from different formats into analysis-ready Pandas DataFrames.

The script should support:

- CSV files with different delimiters and encodings
- JSON files, including nested structures
- Basic ingestion validation and documentation
- Saving processed datasets for further analysis

---

## **Getting Started**

Create a working branch:

```bash
git checkout -b feature/multi-format-data-ingestion

All work should be committed to this branch and submitted through a Pull Request to main.

Tasks
Task 1 — Load CSV Files

Create:

scripts/ingest_data.py

Implement a CSV ingestion function using explicit parameters:

import pandas as pd

def ingest_csv(filepath, delimiter=",", encoding="utf-8", dtype_dict=None):
    """Load a CSV file with explicit delimiter, encoding, and data types."""
    try:
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )

        print(f"CSV loaded: {filepath}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        return df

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        raise

    except UnicodeDecodeError:
        print(f"Encoding error with: {encoding}")
        raise

Test the function using a comma-separated CSV file.

Document why the selected delimiter, encoding, and data types are appropriate.

Task 2 — Load JSON Files

Create a JSON ingestion function that can handle nested data.

def ingest_json(filepath, is_nested=False):
    """Load JSON and optionally flatten nested structures."""
    try:
        df = pd.read_json(filepath)

        if is_nested:
            df = pd.json_normalize(df)

        print(f"JSON loaded: {filepath}")
        print(f"Shape: {df.shape}")

        return df

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        raise

The function should support:

Flat JSON
Nested JSON
Conversion into tabular DataFrames

For example:

{
    "customer": {
        "name": "Alice"
    }
}

can be represented as:

customer.name
-------------
Alice
Task 3 — Encoding Fallback

Implement a fallback strategy for CSV files.

Try multiple encodings such as:

def ingest_csv_with_fallback(
    filepath,
    delimiters=[","],
    fallback_encodings=None
):
    """Try multiple delimiters and encodings."""
    
    if fallback_encodings is None:
        fallback_encodings = [
            "utf-8",
            "latin-1",
            "iso-8859-1",
            "cp1252"
        ]

    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(
                    filepath,
                    delimiter=delimiter,
                    encoding=encoding
                )

                print(
                    f"Loaded using delimiter='{delimiter}', "
                    f"encoding='{encoding}'"
                )

                return df

            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

    raise ValueError(
        f"Could not load {filepath} with the provided options"
    )

This allows the ingestion process to handle files that use different encodings or delimiters.

Task 4 — Document Ingestion Results

Create a function that summarizes the loaded data.

def document_ingestion(df, source_file):
    """Print a basic ingestion report."""

    print("\n" + "=" * 50)
    print(f"INGESTION REPORT: {source_file}")
    print("=" * 50)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nData Types:")
    print(df.dtypes)

    print("\nNull Values:")
    print(df.isnull().sum())

    print("\nSample Data:")
    print(df.head(3))

    print("=" * 50)

    return df

The report should provide enough information to understand what was successfully loaded.

Task 5 — Main Ingestion Script

Use a main execution block to combine the ingestion functions.

if __name__ == "__main__":

    print("Starting multi-format ingestion...\n")

    csv_df = ingest_csv(
        "data/raw/customers.csv",
        delimiter=",",
        encoding="utf-8"
    )

    document_ingestion(csv_df, "customers.csv")

    json_df = ingest_json(
        "data/raw/transactions.json",
        is_nested=True
    )

    document_ingestion(json_df, "transactions.json")

    csv_df.to_csv(
        "data/processed/customers_ingested.csv",
        index=False
    )

    json_df.to_csv(
        "data/processed/transactions_ingested.csv",
        index=False
    )

    print("All data ingested successfully.")
Task 6 — Create Sample Data

Create:

data/raw/customers.csv
customer_id,name,email,signup_date
1,Alice,alice@example.com,2025-01-15
2,Bob,bob@example.com,2025-02-20
3,Carol,carol@example.com,2025-03-10

Create:

data/raw/transactions.json
[
  {
    "id": 1,
    "customer_id": 1,
    "amount": 100,
    "status": "completed"
  },
  {
    "id": 2,
    "customer_id": 2,
    "amount": 250,
    "status": "pending"
  },
  {
    "id": 3,
    "customer_id": 1,
    "amount": 150,
    "status": "completed"
  }
]