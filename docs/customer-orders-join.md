# **Customer & Orders Data Join — PRD**

## **1. Overview**

Merge a customer table containing **1,000 rows** with an orders table containing **5,000 rows**.

The pipeline should:

- Perform an explicit customer-to-orders join.
- Validate row counts before and after merging.
- Detect unmatched customer and order keys.
- Compare different join types.
- Check for unexpected duplication.
- Document the final join decision and business reasoning.

---

## **2. Objectives**

- Correctly merge customers and orders using `customer_id`.
- Preserve required customer records.
- Identify customers without orders.
- Identify orders without matching customers.
- Validate the merge result.
- Document why the selected join type is appropriate.

---

## **3. Explicit Join & Row Count Validation**

Use `customer_id` as the join key.

```python
print(f"Left: {len(df_customers)}")
print(f"Right: {len(df_orders)}")

df_merged = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="left"
)

print(f"Merged: {len(df_merged)}")
print(
    f"Change: {len(df_merged) - len(df_customers)}"
)

Validate:

Customer row count.
Orders row count.
Merged row count.
Change in row count.
4. Detect Unmatched Keys

Find customers who have no orders:

unmatched_customers = df_customers[
    ~df_customers["customer_id"].isin(
        df_orders["customer_id"]
    )
]

Find orders without a matching customer:

unmatched_orders = df_orders[
    ~df_orders["customer_id"].isin(
        df_customers["customer_id"]
    )
]

Save the results:

unmatched_customers.to_csv(
    "output/unmatched_customers.csv",
    index=False
)

unmatched_orders.to_csv(
    "output/unmatched_orders.csv",
    index=False
)

Report:

Customers without orders.
Orphaned orders.
5. Compare Join Types

Compare:

Inner join
Left join
Outer join
inner = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="inner"
)

left = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="left"
)

outer = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="outer"
)

print(f"Inner: {len(inner)}")
print(f"Left: {len(left)}")
print(f"Outer: {len(outer)}")

Document what records are preserved by each join type.

6. Validate Duplication

Check the merged columns:

print(df_merged.columns)

Check how many records exist per customer:

key_counts = df_merged["customer_id"].value_counts()

print(
    f"Max orders per customer: {key_counts.max()}"
)

Validate that multiple rows for a customer are expected because a customer can have multiple orders.

7. Document Join Decision

Create a join report:

join_report = {
    "join_type": "left",
    "left_table": "customers",
    "right_table": "orders",
    "join_key": "customer_id",
    "left_rows": len(df_customers),
    "right_rows": len(df_orders),
    "result_rows": len(df_merged),
    "unmatched_left": len(unmatched_customers),
    "unmatched_right": len(unmatched_orders),
    "reasoning": (
        "Left join preserves all customers, "
        "including customers with no orders."
    )
}

Document why the selected join type fits the business requirement.