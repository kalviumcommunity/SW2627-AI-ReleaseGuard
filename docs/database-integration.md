# **Database Integration & Single Source of Truth — PRD**

## **1. Overview**

Move cleaned analytical data from notebooks and scattered CSV files into a centralized database.

The database will become the single source of truth for downstream analysis, allowing Python scripts and notebooks to query consistent, validated data.

---

## **2. Objectives**

- Set up a database using SQLAlchemy.
- Load cleaned DataFrames into database tables.
- Validate the database schema.
- Query database data from Python.
- Create reusable database-loading functionality.
- Validate row counts and data types.
- Establish the database as the central analytical data source.

---

## **3. Task 1 — Setup Database Connection**

Use SQLite for a zero-setup local database:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///analytics.db"
)

with engine.connect():
    print("Database connection successful")

For PostgreSQL, use an environment variable rather than hardcoded credentials:

import os
from sqlalchemy import create_engine

database_url = os.getenv("DATABASE_URL")

engine = create_engine(database_url)

Requirements:

Configure SQLite or PostgreSQL.
Create the SQLAlchemy engine.
Test the connection.
Document the connection configuration.
Never commit database credentials or passwords.
4. Task 2 — Load Cleaned Data

Load the cleaned DataFrame into a database table:

df_clean.to_sql(
    "customers_cleaned",
    engine,
    if_exists="replace",
    index=False
)

Validate the table and row count:

from sqlalchemy import inspect
import pandas as pd

inspector = inspect(engine)

print(
    inspector.get_table_names()
)

count = pd.read_sql(
    "SELECT COUNT(*) AS row_count "
    "FROM customers_cleaned",
    engine
)

print(
    f"Rows loaded: "
    f"{count.iloc[0]['row_count']}"
)

Requirements:

Create the customers_cleaned table.
Use if_exists="replace" for the initial load.
Verify the table exists.
Confirm database row count matches the source DataFrame.
5. Task 3 — Validate Database Schema

Inspect the table structure:

from sqlalchemy import inspect

inspector = inspect(engine)

columns = inspector.get_columns(
    "customers_cleaned"
)

for column in columns:
    print(
        column["name"],
        column["type"],
        column["nullable"]
    )

Validate expected columns and types:

expected_columns = {
    "customer_id": "INTEGER",
    "email": "VARCHAR",
    "signup_date": "DATE"
}

for column_name, expected_type in expected_columns.items():
    column = next(
        c for c in columns
        if c["name"] == column_name
    )

    actual_type = str(column["type"])

    status = (
        "PASS"
        if expected_type in actual_type
        else "FAIL"
    )

    print(
        f"{status}: "
        f"{column_name} -> {actual_type}"
    )

Requirements:

Inspect all columns.
Display column names and types.
Validate expected data types.
Check nullable constraints.
Document any schema mismatches.
6. Task 4 — Query Database from Python

Run a simple SELECT query:

query = """
SELECT *
FROM customers_cleaned
WHERE customer_type = 'Enterprise'
"""

results = pd.read_sql(
    query,
    engine
)

print(f"Retrieved {len(results)} rows")
print(results.head())

Run an aggregation query:

query_agg = """
SELECT
    customer_type,
    COUNT(*) AS customer_count,
    AVG(lifetime_value) AS avg_ltv
FROM customers_cleaned
GROUP BY customer_type
ORDER BY avg_ltv DESC
"""

summary = pd.read_sql(
    query_agg,
    engine
)

print(summary)

Requirements:

Execute SELECT queries from Python.
Return query results as DataFrames.
Test a filtered query.
Test an aggregation query.
Verify returned results are correct.
7. Task 5 — Create Repeatable Loading Function

Create a reusable function for database loading:

def load_cleaned_data_to_database(
    df,
    table_name,
    database_path="analytics.db"
):
    """
    Load a cleaned DataFrame into a SQLite database.

    Parameters
    ----------
    df : pandas.DataFrame
        Cleaned data to load.

    table_name : str
        Destination database table.

    database_path : str
        SQLite database file path.

    Returns
    -------
    sqlalchemy.Engine
        Database engine for subsequent queries.
    """

    engine = create_engine(
        f"sqlite:///{database_path}"
    )

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count "
        f"FROM {table_name}",
        engine
    )

    rows_loaded = count.iloc[0]["row_count"]

    if rows_loaded != len(df):
        raise ValueError(
            "Row count validation failed"
        )

    print(
        f"Loaded {rows_loaded} rows "
        f"into {table_name}"
    )

    return engine

Example usage:

engine = load_cleaned_data_to_database(
    df_clean,
    "customers_cleaned"
)

results = pd.read_sql(
    """
    SELECT *
    FROM customers_cleaned
    LIMIT 10
    """,
    engine
)

print(results)

Requirements:

Wrap database loading in a reusable function.
Document function parameters.
Validate loaded row count.
Return the database engine.
Make the loading process repeatable.
8. Data Flow

The final workflow should follow:

Raw Data
   ↓
Cleaning & Transformation
   ↓
df_clean
   ↓
SQLAlchemy
   ↓
analytics.db
   ↓
customers_cleaned
   ↓
Python / Notebooks / Analysis

The database should replace scattered CSV copies as the central source for downstream analysis.