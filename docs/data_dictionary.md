# SalesCompass data dictionary

## `data/raw/leads.csv`

- `lead_id` — unique simulated identifier; one record per lead.
- `created_at` — timestamp of initial lead creation (naive fixed scenario local time).
- `source` — acquisition source: inbound demo, paid/organic search, partner referral, webinar, outbound.
- `segment` — SMB, Mid-market, Enterprise.
- `campaign`, `company`, `owner` — source campaign, fictional company name and sales owner.
- `status` — New, Contacted, Qualified, Converted, Disqualified.
- `first_contact_at`, `qualified_at`, `converted_at` — lifecycle event timestamp, blank if missing/not reached.

## `data/raw/activities.csv`

`activity_id`, `lead_id`, `owner`, `activity_type`, `activity_at`, `outcome`. Multiple activity rows per lead.

## `data/raw/stage_history.csv`

`lead_id`, `stage`, `entered_at`. Event-history table rather than current status snapshot. The stage path is New -> Contacted -> Qualified -> Converted for converted leads, with optional Disqualified terminal state.

## `data/raw/opportunities.csv`

`opportunity_id`, `lead_id`, `created_at`, `owner`, `amount`, `status`, `stage`, `close_date`. One opportunity per converted lead in this simplified model. Amount is USD modeled opportunity face value.

**Synthetic constraints:** lead ID foreign keys must exist, conversion requires a recorded opportunity, and first contact must follow creation. The dataset generator uses a fixed pseudorandom seed and October 31, 2026 scenario clock.
