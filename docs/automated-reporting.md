## Overview

Extend the analytics dashboard with automated reporting so stakeholders receive key insights without manually opening the dashboard.

The workflow should be:

```text
Analysis Output
      ↓
Report Generator
      ↓
Structured Insight Report
      ↓
Email Delivery
      ↓
Stakeholder
Task 1: Generate a Structured Report

Create report_generator.py with a reusable generate_report() function.

The report must dynamically calculate values from the current DataFrame.

Required Content
Report title and date
KPI summary
Key finding
Recommended action

Example:

def generate_report(df, report_date):
    revenue = df["revenue"].sum()
    customers = df["customer_id"].nunique()
    avg_order = df["revenue"].mean()

    top_segment = (
        df.groupby("segment")["revenue"]
        .sum()
        .idxmax()
    )

    lines = [
        "WEEKLY ANALYTICS REPORT",
        f"Date: {report_date}",
        "",
        "== KPI SUMMARY ==",
        f"Total Revenue: ${revenue:,.0f}",
        f"Active Customers: {customers:,}",
        f"Average Order: ${avg_order:,.0f}",
        "",
        "== KEY FINDING ==",
        f"Top segment: {top_segment}",
        "",
        "== RECOMMENDED ACTION ==",
        "Allocate resources to high-growth segments."
    ]

    return "\n".join(lines)
Acceptance
Function runs without errors.
Values are calculated dynamically.
No hardcoded KPI values.
Report contains all three required sections.
Task 2: Implement Email Delivery

Create email_sender.py using Python smtplib.

Requirements
Read credentials from environment variables.
Use SMTP with TLS.
Send the generated report to a specified recipient.
Return a success/failure result.
import os
import smtplib
from email.mime.text import MIMEText

def send_report(report_text, recipient):
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    server_host = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    server_port = int(os.environ.get("SMTP_PORT", "587"))

    if not sender or not password:
        print("Email not configured. Skipping.")
        return False

    msg = MIMEText(report_text)
    msg["Subject"] = "Weekly Analytics Report"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP(server_host, server_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return True

    except Exception as e:
        print(f"Send failed: {e}")
        return False
Acceptance
Email function is implemented.
SMTP credentials are read from environment variables.
Successful delivery returns True.
Failed delivery returns False.
Task 3: Validate Report Sections

The generated report must contain:

KPI Summary

Real calculated metrics such as:

Revenue
Active Customers
Average Order Value
Key Finding

A dynamically calculated insight, such as the highest-revenue segment.

Recommended Action

A clear business action based on the analysis.

Acceptance

The generated report contains all three sections with real computed values.

Task 4: Non-Blocking Error Handling

Email failures must not terminate the dashboard or reporting pipeline.

Requirements
Catch SMTP/connection/authentication errors.
Log or display a useful error message.
Return a failure status.
Allow the application to continue running.

Example:

try:
    success = send_report(report, recipient)

    if not success:
        print("Report delivery failed.")

except Exception as e:
    print(f"Reporting error: {e}")
Acceptance

Invalid SMTP credentials result in an error message rather than an application crash.

Task 5: Secure Credential Management

Create .env.example documenting the required variables.

SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
Requirements
Never hardcode credentials.
Never commit real passwords or app passwords.
Add .env to .gitignore.
Use environment variables for SMTP configuration.
.env.example contains only placeholder values.

Example .gitignore entry:

.env
File Structure
assignment-30/
├── report_generator.py
├── email_sender.py
├── .env.example
└── .gitignore
Acceptance Criteria
 Structured report is generated dynamically.
 Report contains KPI summary.
 Report contains a key finding.
 Report contains a recommended action.
 Email delivery uses smtplib.
 SMTP credentials come from environment variables.
 Email failures do not crash the application.
 .env.example documents required variables.
 Real credentials are not committed.