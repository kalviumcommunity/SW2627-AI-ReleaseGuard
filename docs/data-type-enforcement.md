# **Data Type Enforcement & Standardization**

## **Objective**

Convert inconsistent data types into standardized formats:

- String dates → `datetime`
- Currency strings → `float`
- `0/1` values → `boolean`
- Log all type conversions
- Generate a before/after dtype report

---

## **Getting Started**

Create a working branch:

```bash
git checkout -b feature/data-type-enforcement

Commit all work to this branch and create a PR to main.

Tasks
Task 1 — Create Type Casting Function

Create:

scripts/enforce_types.py

Implement a function that:

Accepts a DataFrame and type mapping
Converts columns to specified dtypes
Logs original and new dtypes
Records successful and failed conversions
Warns if a column is missing

Example:

def cast_columns_to_types(df, type_mapping):
    df_typed = df.copy()
    conversion_log = {}

    for col, target_dtype in type_mapping.items():
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        original_dtype = df[col].dtype

        try:
            df_typed[col] = df_typed[col].astype(target_dtype)

            conversion_log[col] = {
                "from": str(original_dtype),
                "to": str(target_dtype),
                "status": "success"
            }

        except Exception as e:
            conversion_log[col] = {
                "from": str(original_dtype),
                "to": str(target_dtype),
                "status": "failed",
                "error": str(e)
            }
            raise

    return df_typed, conversion_log
Task 2 — Convert String Dates

Create a function to convert date columns to datetime.

Requirements:

Accept a list of date columns
Use an explicit date format
Handle conversion errors
Print conversion status

Example:

def convert_string_dates_to_datetime(df, date_columns, date_format=None):
    df_typed = df.copy()

    for col in date_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        try:
            df_typed[col] = pd.to_datetime(
                df_typed[col],
                format=date_format
            )
            print(f"✓ {col}: Converted to datetime")

        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            raise

    return df_typed

Use:

date_format="%Y-%m-%d"
Task 3 — Convert Currency to Float

Create a function that:

Removes currency symbols
Removes commas and whitespace
Converts values to numeric/float
Logs failed conversions

Example:

def convert_currency_to_float(df, currency_columns):
    df_typed = df.copy()

    for col in currency_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        df_typed[col] = (
            df_typed[col]
            .astype(str)
            .str.replace("[$,]", "", regex=True)
            .str.strip()
        )

        df_typed[col] = pd.to_numeric(
            df_typed[col],
            errors="coerce"
        )

        print(f"✓ {col}: Converted to float")

    return df_typed

Example:

"$150.50" → 150.50
"$1,250.00" → 1250.00
Task 4 — Convert Boolean Values

Convert 0/1, yes/no, or similar values into proper boolean types.

Example:

def convert_integers_to_boolean(df, boolean_columns):
    df_typed = df.copy()

    for col in boolean_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue

        if df[col].dtype == "object":
            mapping = {
                "yes": True,
                "no": False,
                "true": True,
                "false": False,
                "1": True,
                "0": False,
                1: True,
                0: False
            }

            df_typed[col] = df_typed[col].map(mapping)

        else:
            df_typed[col] = df_typed[col].astype(bool)

        print(f"✓ {col}: Converted to boolean")

    return df_typed
Task 5 — Compare Before and After Types

Create:

def compare_dtypes(df_original, df_typed):
    comparison = pd.DataFrame({
        "column": df_original.columns,
        "dtype_before": df_original.dtypes.values,
        "dtype_after": df_typed.dtypes.values,
        "changed": (
            df_original.dtypes != df_typed.dtypes
        ).values
    })

    print(comparison.to_string(index=False))

    comparison.to_csv(
        "output/dtype_conversion_report.csv",
        index=False
    )

    return comparison

The report should show:

Column	Before	After	Changed
transaction_date	object	datetime64	True
amount	object	float64	True
is_active	int64	bool	True
Task 6 — Main Execution

Load:

data/raw/untyped_data.csv

Apply the conversions:

df = pd.read_csv("data/raw/untyped_data.csv")

df_typed = convert_string_dates_to_datetime(
    df,
    ["transaction_date", "signup_date"],
    date_format="%Y-%m-%d"
)

df_typed = convert_currency_to_float(
    df_typed,
    ["amount", "revenue"]
)

df_typed = convert_integers_to_boolean(
    df_typed,
    ["is_active", "is_premium"]
)

compare_dtypes(df, df_typed)

df_typed.to_csv(
    "data/processed/typed_data.csv",
    index=False
)
Task 7 — Test the Pipeline

Create:

data/raw/untyped_data.csv

Example:

transaction_date,amount,is_active,signup_date
2025-01-15,$150.50,1,2024-01-01
2025-02-20,$200.00,0,2024-02-15
2025-03-10,$75.25,1,2024-03-01

Run:

python scripts/enforce_types.py

Verify that:

Dates are datetime
Currency values are numeric
Boolean values are True/False
Conversion report is generated
Typed data is saved