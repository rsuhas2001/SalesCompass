# Metric definitions and analytical limitations

| KPI | Exact definition |
|---|---|
| Lead count | Count of unique lead IDs in selected source/segment. |
| Lead conversion % | Leads currently marked Converted / all leads in filter. Every Converted lead has an opportunity. |
| Pipeline created | Sum of opportunity amount; this is *face-value pipeline*, not earned revenue or bookings. |
| 24-hour contacted lead SLA | Number of contacted leads with `first_contact_at - created_at <= 24h` / all contacted leads. Leads never contacted are separately tracked as overdue (not quietly counted as SLA successes). |
| Median first response | Median response delay for leads with a first-contact timestamp. |
| Overdue new leads | New leads with no contact and >24h age at the fixed sample clock. |
| Cumulative funnel stage reach | Number of unique lead IDs with a stage event, regardless of current stage; all leads start at New. |
| Stage duration | Time from stage entry to next observed stage transition; uncompleted transitions are excluded. |
| Outreach touch cohort | Number of logged activities for a lead grouped in 0, 1–2, 3–4, 5+ bands. Conversion rate is descriptive, not causal. |

**Analysis caveats:** Comparisons across sources are not adjusted for lead age, account mix, channel spend or selection. Response SLA rate excludes untouched leads, so management must read the overdue count alongside it. Recovered conversion counts will vary only if the source CSV is regenerated with a different seed or altered.
