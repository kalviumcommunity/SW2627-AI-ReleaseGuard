# **SQL Filtering, Aggregation & HAVING — PRD**

## **1. Overview**

Build a set of SQL queries demonstrating the correct use of `WHERE`, `GROUP BY`, `HAVING`, and `ORDER BY`.

The key distinction is:

- `WHERE` filters individual rows **before** grouping.
- `GROUP BY` creates aggregated groups.
- `HAVING` filters groups **after** aggregation.
- `ORDER BY` sorts the final result.

For example, "Enterprise customers with >$10k annual spending" requires `HAVING` when the `$10k` condition is based on `SUM(amount)`.

---

## **2. Objectives**

- Demonstrate row-level filtering with `WHERE`.
- Aggregate data using `GROUP BY`.
- Filter aggregated groups using `HAVING`.
- Combine `WHERE` and `HAVING`.
- Rank and sort aggregated results.
- Document the correct filtering pattern for the team.

---

## **3. Task 1 — WHERE Filtering**

Use `WHERE` to remove invalid or unwanted rows before aggregation:

```sql
SELECT
    customer_id,
    SUM(amount) AS annual_revenue,
    COUNT(*) AS transaction_count
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
  AND amount > 0
  AND transaction_status = 'completed'
GROUP BY customer_id
ORDER BY annual_revenue DESC;

Document each condition:

Condition	Purpose
transaction_date	Restrict analysis period
amount > 0	Exclude refunds/invalid amounts
transaction_status	Include completed transactions only
4. Task 2 — GROUP BY & Aggregation

Group transactions by multiple dimensions:

SELECT
    c.customer_type,
    DATE_TRUNC(
        'month',
        t.transaction_date
    )::DATE AS month,
    COUNT(DISTINCT t.customer_id) AS unique_customers,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS monthly_revenue,
    AVG(t.amount) AS avg_transaction
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'
GROUP BY
    c.customer_type,
    DATE_TRUNC(
        'month',
        t.transaction_date
    )
ORDER BY month DESC;

Requirements:

Group by at least two dimensions.
Use at least three aggregate functions.
Demonstrate that WHERE filters rows before grouping.
5. Task 3 — HAVING Filtering

Use HAVING when the condition depends on an aggregate:

SELECT
    customer_id,
    COUNT(*) AS transaction_count,
    SUM(amount) AS annual_revenue
FROM transactions
WHERE transaction_date >= DATE '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 10000
   AND COUNT(*) >= 5
ORDER BY annual_revenue DESC;
WHERE vs HAVING
WHERE
  ↓
Filters individual rows
  ↓
GROUP BY
  ↓
Creates aggregated groups
  ↓
HAVING
  ↓
Filters aggregated groups

Use:

WHERE amount > 0

when filtering individual transactions.

Use:

HAVING SUM(amount) > 10000

when filtering customers based on their total spending.

6. Task 4 — WHERE + HAVING

Combine row-level data-quality filters with group-level business thresholds:

SELECT
    c.customer_type,
    COUNT(DISTINCT t.customer_id) AS segment_customers,
    SUM(t.amount) AS segment_revenue,
    ROUND(AVG(t.amount), 2) AS avg_order_value
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'
  AND t.transaction_status = 'completed'
  AND t.amount > 0
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 100
   AND SUM(t.amount) > 100000
ORDER BY segment_revenue DESC;

Document the logic:

WHERE:
- Removes invalid transactions.
- Restricts the analysis period.
- Keeps completed transactions.

GROUP BY:
- Creates customer-type groups.

HAVING:
- Keeps sufficiently large segments.
- Applies revenue thresholds to aggregated groups.
7. Task 5 — ORDER BY & Ranking

Rank and return the top-performing segments:

SELECT
    c.customer_type,
    c.industry,
    COUNT(DISTINCT t.customer_id) AS customers,
    SUM(t.amount) AS total_revenue,
    ROUND(AVG(t.amount), 2) AS avg_order,
    RANK() OVER (
        ORDER BY SUM(t.amount) DESC
    ) AS revenue_rank
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE '2024-01-01'
GROUP BY
    c.customer_type,
    c.industry
HAVING COUNT(DISTINCT t.customer_id) >= 10
ORDER BY total_revenue DESC
LIMIT 20;

Requirements:

Sort by revenue.
Use RANK().
Apply a minimum group size.
Return the top 20 segments.
8. Task 6 — Enterprise Customers Above $10K

Demonstrate the core business question:

Which Enterprise customers have more than $10,000 in annual spending?

SELECT
    c.customer_id,
    c.customer_type,
    SUM(t.amount) AS annual_spending,
    COUNT(*) AS transaction_count
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_type = 'Enterprise'
  AND t.transaction_date >= DATE '2024-01-01'
  AND t.transaction_status = 'completed'
  AND t.amount > 0
GROUP BY
    c.customer_id,
    c.customer_type
HAVING SUM(t.amount) > 10000
ORDER BY annual_spending DESC;

Here:

WHERE filters Enterprise customers and valid transactions.
GROUP BY calculates spending per customer.
HAVING filters customers whose aggregated spending exceeds $10,000.
9. SQL Filtering Pattern

Use this pattern across the team:

SELECT
    dimensions,
    aggregate_functions
FROM table
JOIN ...
WHERE row_level_conditions
GROUP BY dimensions
HAVING aggregate_conditions
ORDER BY result_columns
LIMIT N;
Quick Reference
Requirement	SQL Clause
Filter individual rows	WHERE
Create groups	GROUP BY
Filter aggregate results	HAVING
Sort results	ORDER BY
Return only top N	LIMIT
Calculate ranking	RANK()
Rule of Thumb
"Should this individual row be included?"
        ↓
      WHERE

"Should this aggregated group be included?"
        ↓
      HAVING