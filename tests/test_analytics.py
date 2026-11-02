from src.analytics import load_data,filtered,metrics,funnel,source_performance,stage_velocity,outreach,priorities
from src.app import app
from fastapi.testclient import TestClient

def test_data_integrity():
    d=load_data();l=d['leads'];o=d['opportunities'];h=d['stage_history']
    assert len(l)>=500 and l.lead_id.is_unique
    assert o.opportunity_id.is_unique
    assert set(o.lead_id).issubset(set(l.lead_id))
    assert set(h.lead_id)==set(l.lead_id)
    assert (o.amount>0).all()

def test_metrics_and_filters():
    d=load_data();all_m=metrics(d)
    assert all_m['leads']==len(d['leads'])
    assert 0<=all_m['conversion_rate']<=100
    assert 0<=all_m['sla_rate']<=100
    subset=filtered(d,segment='Enterprise')
    assert subset['leads'].segment.eq('Enterprise').all()
    assert len(subset['leads'])<len(d['leads'])
    assert metrics(subset)['leads']<=all_m['leads']

def test_funnel_and_scores():
    d=load_data();f=funnel(d)
    assert set(f.stage)=={'New','Contacted','Qualified','Converted'}
    assert f.loc[f.stage=='New','leads'].iloc[0]==len(d['leads'])
    assert source_performance(d).leads.sum()==len(d['leads'])
    assert all(stage_velocity(d).median_hours>=0)
    assert outreach(d).leads.sum()==len(d['leads'])
    assert priorities(d)

def test_app_routes():
    c=TestClient(app)
    assert c.get('/').status_code==200
    assert 'Sales pipeline performance' in c.get('/').text
    assert c.get('/api/metrics?segment=SMB').json()['leads']>0
    assert 'lead_id' in c.get('/export/leads.csv').text
    assert c.get('/export/invalid.csv').status_code==404
    assert c.get('/health').json()['synthetic'] is True
    report=c.get('/api/sql-report')
    assert report.status_code==200
    assert sum(x['leads'] for x in report.json()['rows'])==len(load_data()['leads'])
