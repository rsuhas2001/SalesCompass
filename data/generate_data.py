"""Reproducible synthetic SaaS CRM lifecycle dataset. Zero external services."""
from pathlib import Path
from datetime import datetime, timedelta
import random
import csv

OUT=Path(__file__).parent/'raw'
AS_OF=datetime(2026,10,31,18,0)
r=random.Random(2001)
SOURCES=['Inbound demo','Paid search','Organic search','Partner referral','Webinar','Outbound']
SEGMENTS=['SMB','Mid-market','Enterprise']
OWNERS=['Amira Chen','Noah Brooks','Priya Shah','Mateo Garcia','Leah Patel','Ethan Wright','Sofia Rivera','Jonah Kim']
CAMPAIGNS=['Q1 Launch','Industry Roundtable','Benchmark Report','Product Webinar','Fall Outreach','Always-on']

def write(name,rows,fields):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def iso(dt):return dt.strftime('%Y-%m-%dT%H:%M:%S')

def generate(n=520):
    OUT.mkdir(exist_ok=True,parents=True)
    leads=[];activities=[];history=[];opps=[]
    for i in range(1,n+1):
        lid=f'L{i:05d}'; created=AS_OF-timedelta(days=r.randint(1,258),hours=r.randint(0,20))
        source=r.choices(SOURCES,weights=[22,19,17,12,11,19])[0]
        segment=r.choices(SEGMENTS,weights=[48,37,15])[0]
        owner=OWNERS[(i*5+r.randrange(7))%len(OWNERS)]
        campaign=r.choice(CAMPAIGNS)
        p={'Inbound demo':.53,'Paid search':.30,'Organic search':.40,'Partner referral':.56,'Webinar':.34,'Outbound':.22}[source]
        stage=r.choices(['New','Contacted','Qualified','Converted','Disqualified'],weights=[15,22,22,round(p*70),17])[0]
        age=(AS_OF-created).total_seconds()/3600
        if age<36:stage='New'
        if age<96 and stage in ('Converted','Disqualified'):stage='Contacted'
        history.append(dict(lead_id=lid,stage='New',entered_at=iso(created)))
        contact=None; qualified=None; converted=None
        if stage!='New':
            response_hours=r.choices([r.uniform(.3,4),r.uniform(4,26),r.uniform(26,100)],weights=[45,35,20])[0]
            contact=created+timedelta(hours=response_hours)
            if contact>=AS_OF:stage='New';contact=None
            else:history.append(dict(lead_id=lid,stage='Contacted',entered_at=iso(contact)))
        if stage in ('Qualified','Converted','Disqualified') and contact:
            qualified=contact+timedelta(hours=r.randint(9,130))
            if qualified>=AS_OF: stage='Contacted';qualified=None
            elif stage!='Disqualified':history.append(dict(lead_id=lid,stage='Qualified',entered_at=iso(qualified)))
        if stage=='Converted' and qualified:
            converted=qualified+timedelta(hours=r.randint(14,220))
            if converted>=AS_OF:stage='Qualified';converted=None
            else: history.append(dict(lead_id=lid,stage='Converted',entered_at=iso(converted)))
        if stage=='Disqualified' and contact:
            stop=contact+timedelta(hours=r.randint(4,80))
            if stop>=AS_OF:stage='Contacted'
            else:history.append(dict(lead_id=lid,stage='Disqualified',entered_at=iso(stop)))
        leads.append(dict(lead_id=lid,created_at=iso(created),source=source,segment=segment,campaign=campaign,owner=owner,company=f'Acme Account {i:04d}',status=stage,first_contact_at=iso(contact) if contact else '',qualified_at=iso(qualified) if qualified else '',converted_at=iso(converted) if converted else ''))
        if contact:
            last=contact
            types=['Call','Email','Meeting']
            for j in range(r.randint(1,7)):
                t=contact+timedelta(hours=8*j+r.randint(0,16))
                if t>=AS_OF:break
                typ=r.choices(types,weights=[.35,.5,.15])[0]
                result=r.choice(['Connected','No answer','Reply','Booked meeting']) if typ!='Email' else r.choice(['Opened','Replied','No response'])
                activities.append(dict(activity_id=f'A{i:05d}{j:02d}',lead_id=lid,owner=owner,activity_type=typ,activity_at=iso(t),outcome=result))
                last=t
        if converted:
            value=round(r.uniform(4500,24000)*{'SMB':1,'Mid-market':2.7,'Enterprise':6.5}[segment],2)
            state=r.choices(['Open','Won','Lost'],weights=[.55,.27,.18])[0]
            opps.append(dict(opportunity_id=f'O{i:05d}',lead_id=lid,created_at=iso(converted),owner=owner,amount=value,status=state,stage=r.choice(['Discovery','Evaluation','Negotiation']) if state=='Open' else state,close_date=iso(converted+timedelta(days=r.randint(15,85)))[:10]))
    write('leads.csv',leads,['lead_id','created_at','source','segment','campaign','owner','company','status','first_contact_at','qualified_at','converted_at'])
    write('activities.csv',activities,['activity_id','lead_id','owner','activity_type','activity_at','outcome'])
    write('stage_history.csv',history,['lead_id','stage','entered_at'])
    write('opportunities.csv',opps,['opportunity_id','lead_id','created_at','owner','amount','status','stage','close_date'])
    print(f'Wrote {len(leads)} leads, {len(activities)} activities, {len(opps)} opportunities')

if __name__=='__main__':generate()
