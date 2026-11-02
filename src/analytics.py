"""Testable, side-effect-free sales pipeline calculations."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AS_OF=pd.Timestamp('2026-10-31 18:00:00')
STAGES=['New','Contacted','Qualified','Converted']

def load_data(folder=None):
    folder=Path(folder or ROOT/'data/raw')
    return {stem:pd.read_csv(folder/(stem+'.csv'),keep_default_na=False) for stem in ('leads','activities','opportunities','stage_history')}

def filtered(data,segment='All',source='All'):
    leads=data['leads'].copy()
    if segment!='All':leads=leads[leads.segment==segment]
    if source!='All':leads=leads[leads.source==source]
    ids=set(leads.lead_id)
    return {**data,'leads':leads,'activities':data['activities'][data['activities'].lead_id.isin(ids)].copy(),'opportunities':data['opportunities'][data['opportunities'].lead_id.isin(ids)].copy(),'stage_history':data['stage_history'][data['stage_history'].lead_id.isin(ids)].copy()}

def metrics(data):
    l=data['leads']; a=data['activities']; o=data['opportunities']
    n=len(l)
    created=pd.to_datetime(l.created_at)
    first=pd.to_datetime(l.first_contact_at,errors='coerce')
    response=(first-created).dt.total_seconds()/3600
    contacted=response.notna()
    within_24=(contacted&(response<=24)).sum()
    open_new=(l.status=='New')
    age=(AS_OF-created).dt.total_seconds()/3600
    overdue=(open_new&(age>24)).sum()
    return {'leads':n,'contacted':int(contacted.sum()),'sla_rate':round(100*within_24/int(contacted.sum()),1) if contacted.sum() else 0.0,'conversion_rate':round(100*(l.status=='Converted').sum()/n,1) if n else 0.0,'pipeline_created':round(float(pd.to_numeric(o.amount).sum()),2),'median_response_hours':round(float(response.median()),1) if contacted.sum() else None,'overdue_leads':int(overdue),'activities':len(a),'opportunities':len(o)}

def funnel(data):
    history=data['stage_history']
    return pd.DataFrame([{'stage':stage,'leads':int(history[history.stage==stage].lead_id.nunique())} for stage in STAGES])

def source_performance(data):
    l=data['leads'].copy();o=data['opportunities'].copy()
    amounts=pd.to_numeric(o.amount) if len(o) else pd.Series(dtype=float)
    o=o.assign(amount=amounts)
    rows=[]
    for src,group in l.groupby('source'):
        lead_ids=set(group.lead_id)
        converted=int((group.status=='Converted').sum())
        revenue=float(o[o.lead_id.isin(lead_ids)].amount.sum())
        rows.append({'source':src,'leads':len(group),'converted':converted,'conversion_rate':round(100*converted/len(group),1),'pipeline':round(revenue,0)})
    return pd.DataFrame(rows).sort_values('leads',ascending=False) if rows else pd.DataFrame(columns=['source','leads','converted','conversion_rate','pipeline'])

def stage_velocity(data):
    h=data['stage_history'].copy()
    if h.empty:return pd.DataFrame(columns=['stage','median_hours'])
    h['entered_at']=pd.to_datetime(h.entered_at)
    h=h.sort_values(['lead_id','entered_at'])
    h['next_at']=h.groupby('lead_id').entered_at.shift(-1)
    h['hours']=(h.next_at-h.entered_at).dt.total_seconds()/3600
    h=h[(h.hours.notna()) & (h.stage.isin(['New','Contacted','Qualified']))]
    res=h.groupby('stage').hours.median().reset_index().rename(columns={'hours':'median_hours'})
    res['median_hours']=res.median_hours.round(1)
    return res

def outreach(data):
    l=data['leads'];a=data['activities']
    act=a.groupby('lead_id').size().rename('touches') if len(a) else pd.Series(name='touches',dtype=int)
    x=l[['lead_id','status']].merge(act,left_on='lead_id',right_index=True,how='left').fillna({'touches':0});x['converted']=(x.status=='Converted').astype(int)
    x['touch_bucket']=pd.cut(x.touches,bins=[-1,0,2,4,1000],labels=['0','1–2','3–4','5+'])
    ret=x.groupby('touch_bucket',observed=False).agg(leads=('lead_id','size'),conversion=('converted','mean')).reset_index()
    ret['conversion']=(ret.conversion*100).round(1)
    return ret

def priorities(data):
    m=metrics(data);s=source_performance(data)
    items=[]
    if m['overdue_leads']:items.append({'severity':'HIGH','title':f"{m['overdue_leads']} uncontacted leads older than 24h",'action':'Audit lead ownership and follow-up queues; set response alerts.'})
    if len(s):
        low=s[s.leads>=12].sort_values('conversion_rate').iloc[0]
        items.append({'severity':'REVIEW','title':f"{low['source']} has {low['conversion_rate']:.1f}% conversion",'action':'Review qualification, campaign mix, and follow-up timing before adjusting spend.'})
    v=stage_velocity(data)
    if len(v):
        slow=v.sort_values('median_hours',ascending=False).iloc[0]
        items.append({'severity':'REVIEW','title':f"{slow['stage']} has median stage duration {slow['median_hours']:.0f}h",'action':'Investigate segment-specific delays and bottlenecks; compare qualified cohorts.'})
    return items
