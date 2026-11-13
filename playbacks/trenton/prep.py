"""Build data.json for the Trenton playback from the data module and the OpenStreetMap extract. If the sketch scan is present (maps/trenton/map_full.png) it also makes the sketch image."""
import sys, os, json, math
S=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(S,"pipeline")); sys.path.insert(0,os.path.join(S,"pipeline","georef"))
import trenton_data as TR, trenton_geo as geo
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
SKS=0.7   # sketch image scale
def M(lat,lon):
    x,y=geo.xy(lat,lon); return [round(x,1),round(-y,1)]
def mins(s,end=False):
    s=str(s)
    if s=='unknown': return None
    if len(s)==10: return -600 if s==TR.D25 else (0 if not end else 1440)
    d,h=s.split(' '); m=int(h[:2])*60+int(h[3:]); return m-1440 if d==TR.D25 else m
units={u[0]:u for u in TR.UNITS}
ECH={'Army':'army','Headquarters':'hq','Division':'division','Brigade':'brigade','Regiment':'regiment','Company':'company','Detachment':'detachment','Battery':'battery','Section':'section'}
BR={'Infantry':'inf','Cavalry':'cav','Artillery':'art'}
rows={}
for p in TR.P: rows.setdefault(p['unit_id'],[]).append(p)
route={(r[7],r[8]):r for r in TR.ROUTES}
def kf(p):
    a,b=mins(p['se']),mins(p['sl']); c,d=mins(p['ee'],True),mins(p['el'],True)
    t0=(a+b)/2 if a is not None and b is not None else (b if b is not None else a)
    t1=(c+d)/2 if c is not None and d is not None else (c if c is not None else d)
    if t1 is None or t1<t0: t1=t0
    g=p['geom']
    def rng(x,y):
        f=lambda v: 'unknown' if v=='unknown' else (v[11:] if len(v)>10 else ('25 Dec' if v==TR.D25 else '26 Dec'))
        return f(x) if x==y else f(x)+' to '+f(y)
    return {'id':p['pos_id'],'t0':t0,'t1':t1,'ts':rng(p['se'],p['sl']),'te':rng(p['ee'],p['el']),
            'g':[M(x[0],x[1]) for x in g] if g else None,'gs':[[round(x[5][0]*SKS,1),round(x[5][1]*SKS,1)] for x in g] if g and all(x[5] for x in g) else None,
            'act':p['activity'],'place':p['place'],'tb':p['time_basis'],'cb':(g[0][4] if g else 'No position on record'),'cs':(g[0][2] if g else 'none'),
            'prec':(max(x[3] for x in g) if g else None),'src':p['source_ids'],'say':p['say'],'method':p['method'],'oc':p['oc'],'notes':p['notes'],
            'lat':(g[0][0] if g else None),'lon':(g[0][1] if g else None)}
HIDE={'T-US-ARMY','T-US-ADVF','T-HE-PKPEN','T-HE-ALT','T-HE-PKRIV','T-HE-PKBRG','T-HE-PKMAI','T-HE-PKFER','T-HE-ARTR','T-GB-16LD','T-HE-JAG'}
NUDGE={'T-US-HAM':[-26,-16],'T-US-STIR':[-30,16],'T-US-FORR':[24,-18],'T-US-GREENE':[26,14],'T-US-MOUL':[0,22],'T-HE-ARTR':[-24,0],'T-US-ADVW':[24,-4],'T-HE-ARTK':[20,10],'T-US-FERM':[18,-14],'T-HE-LOSS':[0,0]}
tracks=[]
kfs={u:[kf(p) for p in ps] for u,ps in rows.items()}
t04=kfs['T-US-ARMY'][-1]
for u in ('T-US-GREENE','T-US-SULL'):
    k=dict(t04); k['shared']=True; kfs[u].insert(0,k)
def virt(src_unit,src_id,at):
    k=[x for x in kfs[src_unit] if x['id']==src_id][0]
    v={'id':src_id,'t0':at,'t1':at,'ts':k['ts'],'te':k['te'],'g':k['g'],'gs':k['gs'],'virtual':True,'act':'With '+units[src_unit][2]+"'s column",'place':k['place'],'tb':k['tb'],'cb':k['cb'],'cs':k['cs'],'prec':k['prec'],
       'src':k['src'],'say':k['say'],'method':'interpolated','oc':'low','notes':'Shown leaving its division\'s last recorded position. Where the unit itself was at this moment is not in the sources read.','lat':k['lat'],'lon':k['lon']}
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
        if r and a['g'] and b['g']: b['via']=[M(x,y) for x,y in r[9]]
        elif a.get('virtual') and a['id']=='T19' and b['g']: b['via']=(PENN[:3] if uid in SHORT else PENN)+[b['g'][0]]
        elif a.get('virtual') and a['id']=='T55' and b['g'] and uid=='T-US-GLOV': b['via']=RIV+[b['g'][0]]
        elif a.get('virtual') and a['id']=='T55' and b['g'] and uid in ('T-US-STARK','T-US-MOUL'): b['via']=RIV[:4]+[b['g'][0]]
    u=units[uid]
    tr={'id':uid,'name':u[1],'label':u[2],'side':'US' if u[3]=='ARW-US' else 'CR','nation':u[4],'ech':ECH[u[6]],'branch':BR[u[5]],'cmd':u[8],'str':u[9],'k':ks}
    if uid in HIDE: tr['hideAfter']=True
    if uid in NUDGE: tr['nudge']=NUDGE[uid]
    if all(k['g'] is None for k in ks): tr['noplace']=True
    tracks.append(tr)
order=[u[0] for u in TR.UNITS]; tracks.sort(key=lambda t:order.index(t['id']))
ways=[]
for w in geo.load():
    pts=[M(a,b) for a,b in w['pts']]
    ways.append([w['zone']+w['cls'],w['name'],'M'+'L'.join(f'{x:.0f} {y:.0f}' for x,y in pts)])
def L(name,lat,lon,ang=0,lvl=1,sub=''): return {'t':name,'p':M(lat,lon),'a':ang,'l':lvl,'s':sub}
labels=[L('Warren St',40.22400,-74.76527,-80,1,'King St'),L('Broad St',40.22390,-74.76445,-88,1,'Queen St'),L('State St',40.22022,-74.76505,5,1,'Second St'),L('E Hanover St',40.22118,-74.76290,-8,1,'Third St'),
        L('Front St',40.21912,-74.76510,5,1),L('Perry St',40.22345,-74.76180,-18,1),L('Pennington Ave',40.22760,-74.76680,43,1,'Pennington road'),L('Brunswick Ave',40.22740,-74.76225,-50,1,'road to Princeton'),
        L('Montgomery St',40.22450,-74.76277,-78,1),L('W State St',40.22150,-74.77150,-18,1,'River Road'),L('Assunpink Creek',40.21870,-74.76000,-25,1),
        L('Delaware River',40.2620,-74.8540,-48,0),L('Bear Tavern Rd',40.2800,-74.8330,45,0),L('Scotch Rd',40.2700,-74.7990,60,0),L('Sullivan Way',40.2480,-74.8125,50,0,'River Road'),L('Pennington Rd',40.2530,-74.7770,75,0),L('Delaware River',40.2080,-74.7700,20,1)]
lm=[{'t':"McKonkey's Ferry landing",'p':M(40.29672,-74.86753),'l':0},{'t':'Bear Tavern','p':M(40.30918,-74.84857),'l':0},{'t':'Jacobs Creek','p':M(40.29080,-74.84043),'l':0},{'t':'Birmingham','p':M(40.26605,-74.81902),'l':0},
    {'t':'Trenton','p':M(40.2203,-74.7650),'l':0,'only':0},{'t':'Battle Monument','p':M(40.22575,-74.76478),'l':1},{"t":"Rall's headquarters",'p':M(40.22248,-74.76587),'l':1},{'t':'Old Barracks','p':M(40.21948,-74.7685),'l':1},
    {'t':"Friends' Meeting House",'p':M(40.22124,-74.76206),'l':1},{'t':'The Hermitage','p':M(40.2277,-74.7834),'l':1}]
SCAN=S+'/maps/trenton/map_full.png'
if os.path.exists(SCAN):
    im=Image.open(SCAN).convert('RGB'); w,h=im.size
    im=im.resize((round(w*SKS),round(h*SKS)),Image.LANCZOS); im.save(S+'/playbacks/trenton/sketch.jpg',quality=82,optimize=True,progressive=True); SKSIZE=im.size
else:
    SKSIZE=(3118,2020); print('sketch scan not found: sketch image not rebuilt')
src={s[0]:{'title':s[1],'url':s[7]} for s in TR.SOURCES}
xs=[p for wy in geo.load() for p in wy['pts']]
bb=[M(max(a for a,b in xs),min(b for a,b in xs)),M(min(a for a,b in xs),max(b for a,b in xs))]
data={'tracks':tracks,'ways':ways,'labels':labels,'lm':lm,'sources':src,'sk':{'w':SKSIZE[0],'h':SKSIZE[1]},'bbox':[bb[0][0],bb[0][1],bb[1][0],bb[1][1]]}
json.dump(data,open(S+'/playbacks/trenton/data.json','w'),separators=(',',':'),ensure_ascii=False)
print(SKSIZE,'data',os.path.getsize(S+'/playbacks/trenton/data.json')/1e3,'KB; bbox',data['bbox'])
for t in tracks: print(t['id'],t['label'],[(k['id'],round(k['t0']),round(k['t1']),'g' if k['g'] else '-','s' if k['gs'] else '-','v' if k.get('virtual') else '','via' if k.get('via') else '') for k in t['k']])
