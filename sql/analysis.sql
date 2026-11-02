-- SalesCompass | locally executable SQLite analysis
-- Create SQLite database first: python data/build_sqlite.py

-- 1. Conversion and pipeline by acquisition source.
SELECT * FROM v_source_funnel ORDER BY conversion_pct DESC;

-- 2. Owner workload and outreach intensity.
SELECT owner, assigned_leads, recorded_touches, created_opportunities,
       ROUND(1.0 * recorded_touches / NULLIF(assigned_leads, 0), 2) AS touches_per_lead
FROM v_owner_activity ORDER BY assigned_leads DESC;

-- 3. Lead stages reached (not a snapshot of current status).
SELECT stage, COUNT(DISTINCT lead_id) AS reached
FROM stage_history GROUP BY stage ORDER BY reached DESC;

-- 4. Uncontacted leads with 24-hour follow-up exposure as of the sample clock.
SELECT lead_id, created_at, owner, source, segment
FROM leads
WHERE status='New'
  AND (julianday('2026-10-31 18:00:00')-julianday(created_at))*24 > 24
ORDER BY created_at;
