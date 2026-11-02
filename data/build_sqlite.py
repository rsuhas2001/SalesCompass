"""Materialize synthetic CRM CSVs in SQLite and publish reusable sales ops views."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'runtime/salescompass.sqlite3'

DDL='''
CREATE INDEX IF NOT EXISTS idx_lead_segment ON leads(segment);
CREATE INDEX IF NOT EXISTS idx_lead_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_activity_lead ON activities(lead_id);
CREATE INDEX IF NOT EXISTS idx_opp_lead ON opportunities(lead_id);
CREATE VIEW IF NOT EXISTS v_source_funnel AS
SELECT l.source,
       COUNT(DISTINCT l.lead_id) AS leads,
       COUNT(DISTINCT o.lead_id) AS converted,
       ROUND(100.0 * COUNT(DISTINCT o.lead_id) / NULLIF(COUNT(DISTINCT l.lead_id),0),1) AS conversion_pct,
       ROUND(COALESCE(SUM(o.amount),0),2) AS pipeline_value
FROM leads l LEFT JOIN opportunities o ON l.lead_id=o.lead_id
GROUP BY l.source;
CREATE VIEW IF NOT EXISTS v_owner_activity AS
SELECT l.owner,
       COUNT(DISTINCT l.lead_id) AS assigned_leads,
       COUNT(DISTINCT a.activity_id) AS recorded_touches,
       COUNT(DISTINCT o.lead_id) AS created_opportunities
FROM leads l LEFT JOIN activities a ON a.lead_id=l.lead_id
LEFT JOIN opportunities o ON o.lead_id=l.lead_id
GROUP BY l.owner;
'''

def build(target=TARGET):
    target=Path(target);target.parent.mkdir(exist_ok=True,parents=True)
    with sqlite3.connect(target) as c:
        for name in ['leads','activities','opportunities','stage_history']:
            df=pd.read_csv(ROOT/'data/raw'/f'{name}.csv',keep_default_na=False)
            df.to_sql(name,c,if_exists='replace',index=False)
        c.executescript(DDL)
    return target

if __name__=='__main__':
    print(f'Created {build()}')
