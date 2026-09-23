## Overview

Convert the completed churn analysis into clear, leadership-ready communication. Create a one-page executive summary focused on business impact, risks, recommendations, decisions, and next steps, while keeping technical methodology in a separate appendix.

---

## Task 1: Executive Summary

Create `executive_summary.md` with **300–400 words**.

### Required Sections

- **Situation** — Explain the churn problem and financial impact.
- **Key Findings** — 3+ specific findings using measurable numbers.
- **Business Risks** — Explain revenue, customer, competitive, and operational risks.
- **Recommendations** — Give specific actions, costs, expected impact, and timelines.
- **Decision Needed** — Clearly state what leadership must approve.
- **Next Steps** — Identify owners, actions, and deadlines.

### Requirements

- One-page maximum
- Non-technical language
- Self-contained
- Quantify business impact using `$` and `%`
- No equations, models, or statistical jargon
- Every recommendation must connect to a specific finding

---

## Task 2: Business Risk Analysis

Create a **Risk Analysis** section covering at least 3 risks.

For each risk include:

```markdown
### Risk 1: Revenue Loss From Churn
- **What:** 7% churn causes $2M annual revenue loss
- **Why It Matters:** Largest preventable revenue leak
- **Action:** Improve support response time

Cover risks such as:

Revenue loss from churn
High-value customer vulnerability
Competitive disadvantage
Support-team workload/burnout

Quantify the impact wherever possible.

Task 3: Recommendation Justification

Create a mapping table:

Finding	Business Risk	Recommendation	Expected Impact
Slow support increases churn	Revenue loss	Hire 2 support engineers	Reduce response time
High-value customers are sensitive to delays	Customer revenue loss	Prioritize high-value customers	Protect key accounts
Response times are degrading	Operational risk	Add staffing and workload controls	Improve service capacity
Current response time is 6 hours	Missed retention opportunity	Implement <2-hour SLA	Improve accountability

The cause → risk → recommendation → impact chain must be clear.

Task 4: Separate Executive and Technical Documents

Create two distinct documents.

executive_summary.md

Contains:

Situation
Key findings
Business risks
Recommendations
Decision needed
Next steps

Must be readable without technical knowledge.

technical_analysis.md

Contains the detailed supporting analysis:

Data sources and validation
Correlation/cohort analysis
Methodology
Model validation and assumptions
Regression results
P-values and AUC scores
Supporting charts

The technical document is an optional appendix for readers who need methodological detail.

Task 5: Audience Adaptation

Answer how communication changes between leadership audiences.

CEO

Focus on:

ROI
Revenue at risk
Investment required
Strategic decisions

Example:

Support delays are contributing to customer loss and $2M in annual revenue impact. Leadership must decide whether to approve the $200K staffing investment.

VP of Engineering

Focus on:

Current response time: 6 hours
Target: <2 hours
Routing/prioritization logic
Monitoring dashboards
Staffing requirements
Implementation plan

Principle: Same evidence, different emphasis and level of technical detail.

Task 6: Audience Versions — Bonus

Create audience_versions_A_B_C.md.

Version A — Board of Directors
Maximum one paragraph
Strategic risk
Shareholder/business value
Financial metrics only
Version B — Operations Team
Maximum two paragraphs
Implementation details
Process changes
Staffing
Timeline and ownership
Version C — Support Team
Maximum two paragraphs
How staffing improves workload
Response-time expectations
Support they will receive
Expected improvement to customer experience
Quality Checklist

Before submission:

 Executive summary is 300–400 words
 One-page maximum
 Situation clearly explains the problem
 Findings contain specific numbers
 Risks are quantified where possible
 Recommendations are actionable
 Every recommendation connects to a finding
 Decision/approval is explicit
 Next steps identify actions and timing
 No technical jargon in executive summary
 Technical analysis is separated
 Audience versions use different levels of detail
 Summary reads naturally when spoken aloud
File Structure
assignment-26/
├── executive_summary.md
├── technical_analysis.md
└── audience_versions_A_B_C.md
Acceptance Criteria
executive_summary.md is a self-contained 300–400 word leadership summary.
Business risks and financial impact are clearly quantified.
Recommendations are directly linked to documented findings.
Decision required from leadership is unambiguous.
Technical methodology is separated into technical_analysis.md.
CEO, engineering, board, operations, and support audiences receive appropriately adapted messaging.