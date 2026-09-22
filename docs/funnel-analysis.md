# **Signup Funnel Analysis & Conversion Optimization — PRD**

## **1. Overview**

Analyze the signup-to-purchase funnel to identify where users are dropping off and determine which stage has the greatest business impact.

The analysis will measure user volume, drop-off rates, conversion rates, revenue impact, and potential recovery from improving the highest-impact bottleneck.

---

## **2. Objectives**

- Define sequential funnel stages.
- Count users at every stage.
- Calculate stage-to-stage conversion and drop-off rates.
- Identify the largest bottleneck.
- Estimate the financial impact of each drop-off.
- Visualize the funnel.
- Recommend which stage to optimize first.
- Define measurable success criteria.

---

## **3. Task 1 — Define Funnel Stages**

Calculate users reaching each funnel stage:

```python
stages = {
    "Sign Up": len(df[df["signup_completed"] == 1]),
    "Email Entered": len(df[df["email_entered"] == 1]),
    "Password Created": len(df[df["password_created"] == 1]),
    "Email Verified": len(df[df["email_verified"] == 1]),
    "Payment Added": len(df[df["payment_added"] == 1]),
    "First Purchase": len(df[df["first_purchase"] == 1])
}

print(stages)

Requirements:

Define at least 5 sequential stages.
Count users reaching each stage.
Verify that the funnel progresses logically.
Calculate overall funnel conversion from first to final stage.
4. Task 2 — Calculate Drop-Off Rates

Calculate users lost and conversion between consecutive stages:

stage_list = list(stages.values())
stage_names = list(stages.keys())

drop_off = []

for i in range(len(stage_list) - 1):
    users_before = stage_list[i]
    users_after = stage_list[i + 1]

    users_lost = users_before - users_after
    completion_rate = (
        users_after / users_before
    ) * 100

    drop_rate = (
        users_lost / users_before
    ) * 100

    drop_off.append({
        "from_stage": stage_names[i],
        "to_stage": stage_names[i + 1],
        "users_lost": users_lost,
        "completion_rate": completion_rate,
        "drop_rate": drop_rate
    })

funnel_df = pd.DataFrame(drop_off)

print(funnel_df)

Identify:

Absolute users lost.
Percentage drop-off.
Stage completion rate.
Stage with the highest drop-off rate.
Stage with the largest absolute user loss.
5. Task 3 — Visualize Funnel

Create a bar chart showing users at each stage:

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(
    stages.keys(),
    stages.values()
)

ax.set_ylabel("Users")
ax.set_xlabel("Stage")
ax.set_title("Signup Funnel: Volume by Stage")

for stage, count in stages.items():
    ax.text(
        stage,
        count,
        str(count),
        ha="center",
        va="bottom"
    )

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    "output/funnel_chart.png",
    dpi=150
)

plt.show()