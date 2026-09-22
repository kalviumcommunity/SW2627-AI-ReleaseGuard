# **NumPy Vectorization & Performance Optimization — PRD**

## **1. Overview**

Replace slow Python loop-based calculations with NumPy vectorized operations to improve performance on large datasets.

The goal is to make normalization, scoring, ranking, and other numerical operations production-ready for million-row datasets.

---

## **2. Objectives**

- Replace Python loops with NumPy vectorization.
- Normalize revenue using Min-Max scaling.
- Calculate Z-score values.
- Rank customers by revenue.
- Compare loop and NumPy performance.
- Store vectorized results back in the DataFrame.

---

## **3. Task 1 — NumPy Vectorization**

Replace loop-based normalization:

```python
import numpy as np

revenue_array = df["revenue"].values

normalized_np = (
    (revenue_array - revenue_array.min()) /
    (revenue_array.max() - revenue_array.min())
)

df["revenue_normalized"] = normalized_np

Validate that the vectorized result matches the loop-based result.

4. Task 2 — Z-Score Normalization

Calculate Z-scores using NumPy:

revenue_array = df["revenue"].values

z_scores = (
    (revenue_array - revenue_array.mean()) /
    revenue_array.std()
)

df["revenue_zscore"] = z_scores
5. Task 3 — Revenue Ranking

Rank customers by revenue in descending order:

revenue_array = df["revenue"].values

rankings = np.argsort(-revenue_array)

df["revenue_rank"] = np.empty_like(rankings)

df["revenue_rank"][rankings] = (
    np.arange(1, len(rankings) + 1)
)

Verify that the highest-revenue customer receives rank 1.

6. Task 4 — Performance Comparison

Compare Python loops with NumPy vectorization.

import time

start = time.time()

result_loop = []

for val in df["revenue"]:
    result_loop.append(val * 1.1)

loop_time = time.time() - start

start = time.time()

result_np = df["revenue"].values * 1.1

np_time = time.time() - start

print(f"Loop: {loop_time:.4f}s")
print(f"NumPy: {np_time:.4f}s")
print(f"Speedup: {loop_time / np_time:.0f}x")

Document the performance difference.

7. Task 5 — Integrate Results

Store all NumPy-generated features in the DataFrame:

df["revenue_normalized"] = normalized_np
df["revenue_zscore"] = z_scores
df["revenue_rank"] = df["revenue_rank"]

Validate:

print(f"Shape: {df.shape}")
print(f"Dtypes:\n{df.dtypes}")