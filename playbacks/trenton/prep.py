"""Trenton, 26 December 1776: write this battle's battle file (battle.json).

The record comes from the pilot data module (pipeline/trenton_data.py, which is also what the workbook's Trenton rows are made from)
and the OpenStreetMap extract. What is set here is only what the playback adds: when each row is shown, the marches along the roads,
and where a unit with no record of its own leaves its division. If the sketch scan is present (maps/trenton/map_full.png) the sketch
picture is made again as well.
"""
import sys, os, math
S=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(S,"pipeline")); sys.path.insert(0,os.path.join(S,"pipeline","georef"))
import trenton_data as TR, trenton_geo as geo
import battlefile as bf
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
HERE=os.path.join(S,'playbacks','trenton')
DAY=TR.D26; SKETCH='wiederhold-1776'
SKS=0.7   # sketch image scale
def M(lat,lon): return bf.ll(lat,lon)
def at(m): return bf.at_minute(DAY,m)
def mins(s,end=False):
    s=str(s)
    if s=='unknown': return None
    if len(s)==10: return -600 if s==TR.D25 else (0 if not end else 1440)
    d,h=s.split(' '); m=int(h[:2])*60+int(h[3:]); return m-1440 if d==TR.D25 else m
units={u[0]:u for u in TR.UNITS}
ECH={'Army':'army','Headquarters':'headquarters','Division':'division','Brigade':'brigade','Regiment':'regiment','Company':'company','Detachment':'detachment','Battery':'battery','Section':'section'}
BR={'Infantry':'infantry','Cavalry':'cavalry','Artillery':'artillery'}
rows={}
for p in TR.P: rows.setdefault(p['unit_id'],[]).append(p)
route={(r[7],r[8]):r for r in TR.ROUTES}
def kf(p):
    a,b=mins(p['se']),mins(p['sl']); c,d=mins(p['ee'],True),mins(p['el'],True)
    t0=(a+b)/2 if a is not None and b is not None else (b if b is not None else a)
    t1=(c+d)/2 if c is not None and d is not None else (c if c is not None else d)
    if t1 is None or t1<t0: t1=t0
    g=p['geom']
    # t0 and t1 (minutes from midnight on the 26th) are when the playback shows the row: the middle of each range the record gives
    return {'id':p['pos_id'],'t0':t0,'t1':t1,'start':[bf.iso(p['se']),bf.iso(p['sl'])],'end':[bf.iso(p['ee']),bf.iso(p['el'])],
            'at':[M(x[0],x[1]) for x in g] if g else None,
            'on':{SKETCH:[[round(x[5][0]*SKS,1),round(x[5][1]*SKS,1)] for x in g]} if g and all(x[5] for x in g) else None,
            'activity':p['activity'],'place':p['place'],'quote':p['say'],'method':p['method'],'confidence':p['oc'],'time_basis':p['time_basis'],
            'location':{'source':g[0][2],'basis':g[0][4],'precision_m':max(x[3] for x in g)} if g else None,
            'sources':bf.ids(p['source_ids']),'notes':p['notes'],'battle':p['battle_id']}
HIDE={'T-US-ARMY','T-US-ADVF','T-HE-PKPEN','T-HE-ALT','T-HE-PKRIV','T-HE-PKBRG','T-HE-PKMAI','T-HE-PKFER','T-HE-ARTR','T-GB-16LD','T-HE-JAG'}
NUDGE={'T-US-HAM':[-26,-16],'T-US-STIR':[-30,16],'T-US-FORR':[24,-18],'T-US-GREENE':[26,14],'T-US-MOUL':[0,22],'T-HE-ARTR':[-24,0],'T-US-ADVW':[24,-4],'T-HE-ARTK':[20,10],'T-US-FERM':[18,-14],'T-HE-LOSS':[0,0]}
tracks=[]
kfs={u:[kf(p) for p in ps] for u,ps in rows.items()}
t04=kfs['T-US-ARMY'][-1]
for u in ('T-US-GREENE','T-US-SULL'):
    k=dict(t04); k['shared']=True; kfs[u].insert(0,k)
def virt(src_unit,src_id,at):   # a stand-in first step: the unit starts from a row of its division's
    k=[x for x in kfs[src_unit] if x['id']==src_id][0]
    v=dict(k,t0=at,t1=at,virtual=True,activity='With '+units[src_unit][2]+"'s column",method='interpolated',confidence='low',
           notes='Shown leaving its division\'s last recorded position. Where the unit itself was at this moment is not in the sources read.')
    return v
k19=[x for x in kfs['T-US-GREENE'] if x['id']=='T19'][0]; k55=[x for x in kfs['T-US-SULL'] if x['id']=='T55'][0]
for u in ('T-US-STEPH','T-US-MERC','T-US-STIR','T-US-FERM','T-US-FORR','T-US-HAM','T-US-HQ','T-US-ADVW'):
    kfs[u].insert(0,virt('T-US-GREENE','T19',k19['t1']))
for u in ('T-US-STARK','T-US-MOUL','T-US-GLOV','T-US-STCL'):
    kfs[u].insert(0,virt('T-US-SULL','T55',k55['t0']))
PENN=[M(a,b) for a,b in TR.R_PENN_TOWN[:-1]]
RIV=[M(a,b) for a,b in TR.R_RIVER_TOWN]
SHORT={'T-US-HQ','T-US-STEPH','T-US-FERM'}
for k in kfs['T-US-GREENE']:
    if k['id']=='T05':
        k['t0']=450; k['notes']+=' The playback shows this halt from 7:30, the time the column could have arrived by the route drawn.'
for uid,ks in kfs.items():
    ks.sort(key=lambda k:(k['t0'],k['t1']))
    for a,b in zip(ks,ks[1:]):
        if b['t0']<a['t1']: a['t1']=b['t0']
        r=route.get((a['id'],b['id']))
        if r and a.get('at') and b.get('at'): b['via']=[M(x,y) for x,y in r[9]]
        elif a.get('virtual') and a['id']=='T19' and b.get('at'): b['via']=(PENN[:3] if uid in SHORT else PENN)+[b['at'][0]]
        elif a.get('virtual') and a['id']=='T55' and b.get('at') and uid=='T-US-GLOV': b['via']=RIV+[b['at'][0]]
        elif a.get('virtual') and a['id']=='T55' and b.get('at') and uid in ('T-US-STARK','T-US-MOUL'): b['via']=RIV[:4]+[b['at'][0]]
    for k in ks: k['show']=[at(k.pop('t0')),at(k.pop('t1'))]
    tr={'id':uid,'unit':uid,'steps':ks}
    if uid in HIDE: tr['hide_after']=True
    if uid in NUDGE: tr['nudge']=NUDGE[uid]
    tracks.append(tr)
order=[u[0] for u in TR.UNITS]; tracks.sort(key=lambda t:order.index(t['id']))
# ---- current map: streets, the river and the creek from the OpenStreetMap extract ----
lines=[]
for w in geo.load():
    kind='water' if w['zone']=='W' else 'road'
    lines.append([kind,('river' if w['name']=='Delaware River' else 'stream') if kind=='water' else w['cls'],w['name'],bf.pack([M(a,b) for a,b in w['pts']])])
def L(name,lat,lon,ang=0,lvl=1,sub=''): return {'text':name,'alt':sub,'at':M(lat,lon),'angle':ang,'level':lvl,'kind':'road'}
labels=[L('Warren St',40.22400,-74.76527,-80,1,'King St'),L('Broad St',40.22390,-74.76445,-88,1,'Queen St'),L('State St',40.22022,-74.76505,5,1,'Second St'),L('E Hanover St',40.22118,-74.76290,-8,1,'Third St'),
        L('Front St',40.21912,-74.76510,5,1),L('Perry St',40.22345,-74.76180,-18,1),L('Pennington Ave',40.22760,-74.76680,43,1,'Pennington road'),L('Brunswick Ave',40.22740,-74.76225,-50,1,'road to Princeton'),
        L('Montgomery St',40.22450,-74.76277,-78,1),L('W State St',40.22150,-74.77150,-18,1,'River Road'),L('Assunpink Creek',40.21870,-74.76000,-25,1),
        L('Delaware River',40.2620,-74.8540,-48,0),L('Bear Tavern Rd',40.2800,-74.8330,45,0),L('Scotch Rd',40.2700,-74.7990,60,0),L('Sullivan Way',40.2480,-74.8125,50,0,'River Road'),L('Pennington Rd',40.2530,-74.7770,75,0),L('Delaware River',40.2080,-74.7700,20,1)]
labels+=[{'text':"McKonkey's Ferry landing",'at':M(40.29672,-74.86753),'level':0,'kind':'landmark'},{'text':'Bear Tavern','at':M(40.30918,-74.84857),'level':0,'kind':'landmark'},{'text':'Jacobs Creek','at':M(40.29080,-74.84043),'level':0,'kind':'landmark'},{'text':'Birmingham','at':M(40.26605,-74.81902),'level':0,'kind':'landmark'},
    {'text':'Trenton','at':M(40.2203,-74.7650),'level':0,'kind':'landmark'},{'text':'Battle Monument','at':M(40.22575,-74.76478),'level':1,'kind':'landmark'},{'text':"Rall's headquarters",'at':M(40.22248,-74.76587),'level':1,'kind':'landmark'},{'text':'Old Barracks','at':M(40.21948,-74.7685),'level':1,'kind':'landmark'},
    {'text':"Friends' Meeting House",'at':M(40.22124,-74.76206),'level':1,'kind':'landmark'},{'text':'The Hermitage','at':M(40.2277,-74.7834),'level':1,'kind':'landmark'}]
SCAN=S+'/maps/trenton/map_full.png'
if os.path.exists(SCAN):
    im=Image.open(SCAN).convert('RGB'); w,h=im.size
    im=im.resize((round(w*SKS),round(h*SKS)),Image.LANCZOS); im.save(HERE+'/sketch.jpg',quality=82,optimize=True,progressive=True); SKSIZE=im.size
else:
    SKSIZE=(3118,2020); print('sketch scan not found: sketch picture not rebuilt')
maps=[{'id':SKETCH,'title':"Wiederhold, sketch of the engagement at Trenton (1776)",'credit':'Wiederhold, 1776 \u00b7 Library of Congress','source':'S36',
       # the sketch is not to scale outside the town, so it is not laid on the ground: units carry their own positions on it (a step's "on")
       'georeferenced':False,'size':list(SKSIZE),'images':[{'file':'sketch.jpg'}]}]

ulist=[]
for u in TR.UNITS:
    ulist.append({'id':u[0],'name':u[1],'label':u[2],'side':u[3],'nation':u[4],'branch':BR[u[5]],'echelon':ECH[u[6]],'sources':bf.ids(u[10]),'notes':u[11],
                  'assignments':[{'parent':u[7],'commander':u[8],'strength':u[9]}]})

# ---- events: the record's, each marked on the timeline at the moment the playback's rows reach it.
#      id: (minutes from midnight, short name for the timeline, loud on the timeline?, wording where the playback's differs) ----
EV={'TE04':(240,'March begins',1,"The column sets off from the landing for Trenton, about nine miles away."),'TE05':(405,'Army divides',1,None),
    'TE06':(465,'First shots',1,"Greene's advance drives in Lt. Wiederhold's picket on the Pennington road."),'TE07':(476,"Sullivan's attack",0,None),'TE08':(480,'Guns open',0,None),
    'TE10':(498,'Line of battle',1,"The three Hessian regiments form a line along the east edge of the village."),'TE09':(503,'Guns taken',0,None),
    'TE11':(518,'Rall shot',1,"Rall leads two regiments back into the town and is mortally wounded on Queen Street."),'TE12':(530,'Surrender',1,None),'TE13':(545,'Knyphausen surrenders',0,None)}
steps_used={k['id'] for t in tracks for k in t['steps']}
events=[]
for e in TR.EVENTS:
    if e[0] not in EV: continue    # the crossing and the return to Pennsylvania lie outside the playback's hours
    m,short,loud,text=EV[e[0]]
    events.append({'id':e[0],'start':bf.iso(e[3]),'end':bf.iso(e[4]),'at':at(m),'name':e[5],'label':short if short!=e[5] else None,'text':text or e[6],'quiet':(not loud) or None,
                   'steps':[x for x in bf.ids(e[7]) if x in steps_used],'sources':bf.ids(e[8]),'battle':e[2]})
events.sort(key=lambda e:e['at'])
catalogue={s[0]:{'title':s[1],'citation':s[5],'type':s[4],'url':s[7]} for s in TR.SOURCES}
def box(x0,y0,x1,y1):
    """a box given in metres east and south of the middle of Trenton -> [west, south, east, north]"""
    (n,w),(s_,e)=geo.ll(x0,-y0),geo.ll(x1,-y1); return [round(w,5),round(s_,5),round(e,5),round(n,5)]
battle={'id':'trenton-1776','title':'Trenton','subtitle':'26 December 1776',
 'record':{'workbook':'Military Map Explorer data pilot v7','campaign':'ARW-TP','battles':['TREN']},
 # one day's fighting after a night march: no day numbers. The march (3:00 to 7:30) comes before the fight ("focus")
 'time':{'unit':'minute','zero':DAY+'T00:00','start':at(180),'end':at(600),'focus':[at(450),at(600)],'calendar':{'first':DAY,'numbered':False,'days':1}},
 'view':{'origin':bf.ll(geo.LAT0,geo.LON0),'extent':box(-17000,-10600,4200,2400),'presets':{'march':box(-9000,-9000,600,600)}},
 'opening':{'label':'Before the march','text':"The army is on the New Jersey bank, forming for the march. The crossing ran about three hours late."},
 'sides':[{'id':'ARW-US','code':'US','name':'United States (Continental Army and militia)','short':'American','colour':'blue'},
          {'id':'ARW-CR','code':'CR','name':'British Crown forces (British and German troops)','short':'Hessian and British','colour':'red'}],
 'units':ulist,'tracks':tracks,'events':events,'labels':labels,'maps':maps,
 'base':{'credit':'\u00a9 OpenStreetMap contributors','source':'S39','lines':lines,'areas':[]}}
battle['sources']=bf.used_sources(battle,catalogue,['S39'] if 'S39' in catalogue else [])
bf.write(battle,HERE+'/battle.json')
