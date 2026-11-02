"""SalesCompass dashboard; run: uvicorn src.app:app --reload"""
from pathlib import Path
import sqlite3
from data.build_sqlite import build
import pandas as pd
import plotly.express as px
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .analytics import load_data,filtered,metrics,funnel,source_performance,stage_velocity,outreach,priorities,AS_OF

ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='SalesCompass',version='1.0',description='Synthetic CRM funnel and sales operations analytics.')
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
tpl=Jinja2Templates(directory=ROOT/'templates')

def plot(fig):
    fig.update_layout(template='plotly_white',margin=dict(l=14,r=14,t=14,b=14),height=310,font=dict(family='Arial',size=12),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    return fig.to_html(full_html=False,include_plotlyjs=False,config={'displayModeBar':False,'responsive':True})

@app.get('/',response_class=HTMLResponse)
def dashboard(request:Request,segment:str='All',source:str='All'):
    d=load_data();valid_segments=['All']+sorted(d['leads'].segment.unique());valid_sources=['All']+sorted(d['leads'].source.unique())
    segment=segment if segment in valid_segments else 'All';source=source if source in valid_sources else 'All'
    d=filtered(d,segment,source);m=metrics(d);f=funnel(d);s=source_performance(d);v=stage_velocity(d);o=outreach(d)
    ffig=px.bar(f,x='stage',y='leads',text='leads',color='stage',category_orders={'stage':['New','Contacted','Qualified','Converted']})
    sfig=px.bar(s,x='conversion_rate',y='source',orientation='h',color='conversion_rate',color_continuous_scale='Blues',text='conversion_rate') if len(s) else px.bar()
    vfig=px.bar(v,x='stage',y='median_hours',text='median_hours',color='stage') if len(v) else px.bar()
    ofig=px.bar(o,x='touch_bucket',y='conversion',text='conversion',color='touch_bucket')
    srows=s.to_dict('records')
    raw=d['leads'].copy();raw['created_dt']=pd.to_datetime(raw.created_at);raw=raw.sort_values('created_dt',ascending=False).head(15)
    return tpl.TemplateResponse(request,'dashboard.html',dict(title='Revenue operations overview',metrics=m,segment=segment,source=source,segments=valid_segments,sources=valid_sources,charts=[plot(x) for x in [ffig,sfig,vfig,ofig]],sources_table=srows,recent=raw.to_dict('records'),actions=priorities(d),asof=AS_OF.strftime('%b %d, %Y'),n=len(d['leads'])))

@app.get('/api/metrics')
def api_metrics(segment:str='All',source:str='All'):
    return metrics(filtered(load_data(),segment,source))

@app.get('/export/{dataset}.csv')
def export(dataset:str,segment:str='All',source:str='All'):
    if dataset not in ('leads','activities','opportunities','stage_history','source_performance'):
        return JSONResponse({'error':'Unknown dataset'},status_code=404)
    d=filtered(load_data(),segment,source)
    out=source_performance(d) if dataset=='source_performance' else d[dataset]
    return Response(out.to_csv(index=False),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="salescompass_{dataset}.csv"'})

@app.get('/api/sql-report')
def sql_report():
    path=build()
    with sqlite3.connect(path) as conn:
        conn.row_factory=sqlite3.Row
        rows=[dict(x) for x in conn.execute('SELECT * FROM v_source_funnel ORDER BY conversion_pct DESC')]
    return {'source':'SQLite view','rows':rows}

@app.get('/health')
def health():return {'status':'ok','as_of':AS_OF.isoformat(),'synthetic':True,'rows':len(load_data()['leads'])}
