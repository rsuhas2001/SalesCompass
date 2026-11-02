# Project interview case study — SalesCompass — Sales Funnel & Revenue Operations Analytics

## 1. Business problem

Sales leaders need to know which lead sources generate opportunities, where funnel movement slows, and whether new leads receive timely follow-up.

## 2. Stakeholders

Sales/Revenue Operations leadership, Business Development teams, cross-functional marketing and operations managers, and analysts maintaining trusted reporting.

## 3. My technical approach

1. Filter the sales dashboard by customer segment and acquisition channel
2. Measure lead-to-opportunity conversion, median first response time, 24-hour contacted-lead SLA and overdue new leads
3. Visualize cumulative funnel stage reach, source conversion, stage transition durations and outreach-touch correlations
4. Generate an evidence-based manager action queue with concrete next-step recommendations
5. Export leads, activities, opportunities and acquisition scorecards to CSV
6. Create a SQLite reporting database with indexed tables, reusable views and a SQL-report API

## 4. Demonstration

Click the Enterprise segment filter; compare conversion and pipeline with the unfiltered view. Read the source scorecard and discuss why source conversion should not be confused with causal marketing effectiveness. Inspect response SLA breaches and export the complete lead list. Visit `/api/sql-report` to verify SQL-backed source metrics.

## 5. The outcome I can describe

The project implements an operational tool against original synthetic data. I can demonstrate working code, repeatable test results, usable reports and the decisions it would enable. **No ROI, adoption, employer usage, or real sales improvement is claimed.**

### Potential resume bullet AFTER verifying it runs locally

> Built a local sales operations analytics platform for 520 synthetic leads using Python, SQLite, SQL views, and Plotly, tracking funnel conversion, pipeline value, lead response SLAs, and stage velocity with interactive filters and exportable scorecards.

## 6. Important limitations

Synthetic SaaS-like data, no real HubSpot/Outreach access; no propensity adjustments or causal inference; incomplete stage durations are excluded (right-censored); opportunities represent face-value pipeline, not recognized revenue.

## 7. Questions a hiring manager may ask

- What is the source of truth for each field and how do you reconcile disagreement?
- Which numerical metrics are descriptive versus causal?
- Why are these particular data-quality rules / SLA thresholds defensible?
- How do you test behavior, handle missing data and audit exceptions?
- What would change when moving from static CSV inputs to authenticated production systems?
- What are the trade-offs among speed, interpretability, reliability and privacy?

## 8. Why it fits sales operations roles

Directly maps to lead funnel reporting, conversion trends, sales velocity, engagement metrics, and stakeholder-ready summaries.
