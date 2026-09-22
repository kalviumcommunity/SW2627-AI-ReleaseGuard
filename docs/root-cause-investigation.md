# **Root Cause Investigation & Incident Analysis — PRD**

## **1. Overview**

Investigate a major revenue decline systematically instead of assuming the cause.

The analysis will identify when the incident occurred, which customers and transaction segments were affected, what errors correlated with the decline, and whether the evidence supports a specific root-cause hypothesis.

---

## **2. Objectives**

- Identify the exact time window of the revenue decline.
- Compare before, during, and after incident performance.
- Segment affected customers and transactions.
- Analyze categorical patterns and error logs.
- Develop an evidence-based root-cause hypothesis.
- Validate the hypothesis against external evidence.
- Document findings and recommended actions.

---

## **3. Task 1 — Isolate the Incident Window**

Calculate daily and hourly success rates:

```python
df["success_rate"] = (
    df["status"] == "success"
).astype(int)

daily_success = (
    df.groupby(df["timestamp"].dt.date)["success_rate"]
    .mean()
)

threshold = (
    daily_success.mean()
    - daily_success.std()
)

anomaly_dates = daily_success[
    daily_success < threshold
].index

print("Anomalies:", anomaly_dates.tolist())

Zoom into the identified problem date:

problem_day = anomaly_dates[0]

hourly_data = (
    df[df["timestamp"].dt.date == problem_day]
    .groupby(df["timestamp"].dt.hour)["success_rate"]
    .mean()
)

problem_hour = hourly_data.idxmin()

print(hourly_data)
print(
    f"Worst hour: {problem_hour}:00 "
    f"({hourly_data[problem_hour]:.1%})"
)

Requirements:

Identify the anomalous date.
Identify the affected hour.
Compare performance before, during, and after the incident.
Document the exact incident window.
4. Task 2 — Segment Analysis

Analyze the affected period across important dimensions:

problem_window = df[
    (df["timestamp"].dt.date == problem_day)
    & (df["timestamp"].dt.hour == problem_hour)
]

by_customer_type = (
    problem_window
    .groupby("customer_type")["success_rate"]
    .agg(["mean", "count"])
)

by_payment = (
    problem_window
    .groupby("payment_method")["success_rate"]
    .agg(["mean", "count"])
)

by_region = (
    problem_window
    .groupby("region")["success_rate"]
    .agg(["mean", "count"])
)

print(by_customer_type)
print(by_payment)
print(by_region)

Requirements:

Analyze customer type.
Analyze payment method.
Analyze region.
Include success/failure rate and transaction count.
Identify segments disproportionately affected.
Document the observed pattern.
5. Task 3 — Correlation & Error Analysis

Mark transactions occurring during the incident:

df["is_problem_period"] = (
    (df["timestamp"].dt.date == problem_day)
    & (df["timestamp"].dt.hour == problem_hour)
).astype(int)

Analyze categorical relationships:

for col in [
    "payment_method",
    "customer_type",
    "region",
    "device_type"
]:
    crosstab = pd.crosstab(
        df[col],
        df["is_problem_period"]
    )

    print(f"\n{col}:")
    print(crosstab)

Review errors during the incident:

error_correlation = (
    df[df["is_problem_period"] == 1]
    ["error_message"]
    .value_counts()
    .head(10)
)

print(error_correlation)

Requirements:

Analyze categorical patterns using crosstabs.
Review error messages during the incident.
Identify dominant errors.
Compare affected and unaffected segments.
Connect observed patterns to possible causes.
6. Task 4 — Document Investigation & Hypothesis

Create a structured investigation report:

investigation_report = f"""
ROOT CAUSE INVESTIGATION REPORT

OBSERVATION:
- Revenue decline: approximately 50%
- Incident date: {problem_day}
- Incident hour: {problem_hour}:00
- Affected segments: [document findings]

ANALYSIS:
- Customer type: [findings]
- Payment method: [findings]
- Region: [findings]
- Device type: [findings]
- Dominant error: [error]
- Error frequency: [percentage]

HYPOTHESIS:
[Describe the most evidence-supported explanation.]

CONFIDENCE:
[LOW / MEDIUM / HIGH]

EVIDENCE:
- [Evidence 1]
- [Evidence 2]
- [Evidence 3]

RECOMMENDED ACTIONS:
1. [Action]
2. [Action]
3. [Action]
"""

with open(
    "output/investigation_report.txt",
    "w"
) as f:
    f.write(investigation_report)

Requirements:

Document what happened.
Document when it happened.
Identify affected users/segments.
Explain observed patterns.
State a hypothesis and confidence level.
Provide evidence supporting the hypothesis.
Recommend actionable remediation.

Do not treat correlation as proof of causation; distinguish observed evidence from the hypothesis.

7. Task 5 — Validate the Hypothesis

Compare internal incident data with external evidence.

Example structure:

validation = """
HYPOTHESIS VALIDATION

Timeline Alignment:
- External event: [time]
- Internal failures: [time]
- Alignment: [MATCH / PARTIAL / NO MATCH]

Segment Alignment:
- External system affected: [segment]
- Internal affected segment: [segment]
- Alignment: [MATCH / PARTIAL / NO MATCH]

Error Alignment:
- External incident: [description]
- Internal error: [description]
- Alignment: [MATCH / PARTIAL / NO MATCH]

CONCLUSION:
[SUPPORTED / PARTIALLY SUPPORTED / REJECTED]

NEXT ACTION:
[Recommended action based on evidence]
"""

print(validation)

Requirements:

Validate the timeline.
Validate the affected segment.
Compare internal errors with external evidence.
Document supporting and conflicting evidence.
Clearly state whether the hypothesis is supported, partially supported, or rejected.
8. Investigation Framework

The analysis should follow this sequence:

Revenue Decline
      ↓
When did it happen?
      ↓
Which hour/window?
      ↓
Who was affected?
      ↓
Which payment/product/region/device?
      ↓
What errors occurred?
      ↓
What patterns correlate?
      ↓
What hypotheses explain the evidence?
      ↓
Can external evidence validate the hypothesis?
      ↓
Root Cause + Recommended Action
9. Acceptance Criteria
 Anomalous date is identified.
 Exact incident hour/window is identified.
 Before/during/after metrics are compared.
 Customer segments are analyzed.
 Payment methods are analyzed.
 Regions are analyzed.
 Device types are analyzed.
 Failure counts and rates are documented.
 Error logs are analyzed.
 Dominant error patterns are identified.
 A root-cause hypothesis is documented.
 Confidence level is provided.
 Evidence supporting the hypothesis is documented.
 Alternative explanations are considered.
 External evidence is used for validation.
 Timeline alignment is checked.
 Final conclusion is documented.
 Actionable remediation is recommended.