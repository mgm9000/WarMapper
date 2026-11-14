"""Build data.json for the Gettysburg playback from the v2 workbook and the OpenStreetMap extract (data/osm/gettysburg.txt). If the map scan is present (maps/gettysburg/map_full.png) it also cuts the base image."""
import sys, os, json, math
W=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(W,"pipeline","georef"))
import gettysburg_georef as g, gettysburg_picks as picks
import openpyxl
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
X0,Y0,X1,Y1=560,1380,5160,4100; SC=0.8
wb=openpyxl.load_workbook(W+"/data/Gettysburg Day 1 data pilot v2.xlsx",data_only=True)
def table(n):
    ws=wb[n]; rows=list(ws.iter_rows(values_only=True)); h=rows[0]
    return [dict(zip(h,r)) for r in rows[1:] if r[0]]
pos={r['pos_id']:r for r in table('Positions')}
units={r['unit_id']:r for r in table('Units')}
srcs={r['source_id']:r for r in table('Sources')}
TS='time_start (1 Jul 1863)'
def mins(s,end=False):
    s=str(s or '').strip()
    if len(s)==5 and s[2]==':': return int(s[:2])*60+int(s[3:])
    if s.startswith('Jun'): return 0
    if s.startswith('after'): return 630
    return None
def P(x,y): return [round((x-X0)*SC,1),round((y-Y0)*SC,1)]
def geom(r,pid):
    if r['lat'] in (None,''): return None
    if pid=='P08':
        a,b=picks.LN['DEVSK1']; c=picks.LN['DEVSK2'][1]; return [P(*a),P(*b),P(*c)]
    pts=[g.ll2px(float(r['lat']),float(r['lon']))]
    if r['line_end_lat'] not in (None,''): pts.append(g.ll2px(float(r['line_end_lat']),float(r['line_end_lon'])))
    return [P(float(x),float(y)) for x,y in pts]
T=[ # id, unit, rows, opts
 ('US-8IL-pk','US-8IL',['P02'],{'label':'8 IL Cav picket','ech':'company','hold':480,'hideAfter':True}),
 ('US-B1','US-B1',['P01','P04','P05'],{}),
 ('US-B1-sk','US-B1',['P03'],{'label':'Gamble skirmishers','ech':'squadrons','hideAfter':True,'loose':True}),
 ('US-3IN','US-3IN',['P28'],{'parent':'US-B1','hideAfter':True}),('US-12IL','US-12IL',['P29'],{'parent':'US-B1','hideAfter':True}),
 ('US-8IL','US-8IL',['P30'],{'parent':'US-B1','hideAfter':True}),('US-8NY','US-8NY',['P31'],{'parent':'US-B1','hideAfter':True}),
 ('US-B2','US-B2',['P06'],{}),
 ('US-6NY','US-6NY',['P07'],{'label':'6 NY Cav sqn','ech':'squadrons','loose':True}),
 ('US-B2-sk','US-B2',['P08'],{'label':'Devin skirmishers','ech':'squadrons','loose':True}),
 ('US-A2','US-A2',['P09'],{'hideAfter':True}),
 ('US-A2-R','US-A2-R',['P10'],{'nudge':[-20,-14]}),('US-A2-N','US-A2-N',['P11'],{'nudge':[20,14]}),('US-A2-P','US-A2-P',['P12'],{}),
 ('CS-ARCH','CS-ARCH',['P14','P16','P17','P18'],{}),
 ('CS-7TN','CS-7TN',['P32'],{'parent':'CS-ARCH','hideAfter':True}),('CS-14TN','CS-14TN',['P33'],{'parent':'CS-ARCH','hideAfter':True}),
 ('CS-5ALB','CS-5ALB',['P34'],{'parent':'CS-ARCH','hideAfter':True}),('CS-13AL','CS-13AL',['P35'],{'parent':'CS-ARCH','hideAfter':True}),
 ('CS-1TN','CS-1TN',['P36'],{'parent':'CS-ARCH','hideAfter':True}),
 ('CS-DAV','CS-DAV',['P19','P20','P24','P37','P38'],{}),
 ('CS-42MS','CS-42MS',['P21'],{'parent':'CS-DAV','hideAfter':True}),('CS-2MS','CS-2MS',['P22'],{'parent':'CS-DAV','hideAfter':True}),('CS-55NC','CS-55NC',['P23'],{'parent':'CS-DAV','hideAfter':True}),
 ('CS-MARYE','CS-MARYE',['P15'],{'nudge':[0,-26]}),
 ('CS-PETT','CS-PETT',['P26'],{}),('CS-BROCK','CS-BROCK',['P27'],{}),
 ('CS-11MS','CS-11MS',['P25'],{'offmap':'With the division wagon train near Cashtown, about 8 miles west of Gettysburg.'}),
]
ECH={'Division':'division','Brigade':'brigade','Regiment':'regiment','Regiment (part)':'regiment','Battalion':'battalion','Battery':'battery','Section':'section'}
BR={'Cavalry':'cav','Infantry':'inf','Artillery':'art','Horse artillery':'art'}
tracks=[]; used=set()
for tid,uid,rows,o in T:
    u=units[uid]; ks=[]
    for pid in rows:
        r=pos[pid]; used.add(pid)
        t0=mins(r[TS]); t1=mins(r['time_end'])
        if t1 is None: t1=t0
        gm=None if o.get('offmap') else geom(r,pid)
        ks.append({'id':pid,'t0':t0,'t1':t1,'ts':str(r[TS]),'te':str(r['time_end'] or ''),'g':gm,'act':r['activity'],'place':r['place_description'],
          'tb':r['time_basis'],'cb':r['coordinate_basis'],'cc':r['coordinate_confidence'],'oc':r['overall_confidence'],'src':r['source_ids'],
          'say':r['source_wording'],'method':r['position_method'],'notes':r['notes'] or '','status':r['review_status'],
          'lat':r['lat'],'lon':r['lon']})
    tr={'id':tid,'unit':uid,'name':u['unit_name'],'label':o.get('label') or u['map_label'],'side':'US' if u['side']=='Union' else 'CS',
        'ech':o.get('ech') or ECH.get(u['echelon'],'regiment'),'branch':BR.get(u['branch'],'inf'),'cmd':u['commander'] or '','str':u['strength / equipment'] or '','k':ks}
    for k in ('parent','hideAfter','hold','nudge','offmap','loose'):
        if k in o: tr[k]=o[k]
    tracks.append(tr)
print('unused rows',sorted(set(pos)-used))
S={k:{'title':v['title'],'cite':v['citation'],'type':v['type'],'url':v['url'] or ''} for k,v in srcs.items()}
lm={'Herr Tavern':P(2484,2545),'Lutheran Seminary':P(3745,3433),'Willoughby Run':P(2893,2960),'Chambersburg Pike':P(1900,2215),'Unfinished railroad':P(3120,2640),'McPherson farm':P(3165,3040),'Pennsylvania College':P(4444,3168),'Mummasburg Road':P(3930,1960)}
# ---- current map: today's roads, streams, woods and names from the OpenStreetMap extract, in the same pixel frame as the 1876 crop ----
CW,CH=round((X1-X0)*SC),round((Y1-Y0)*SC); MG=40
def osm_rows():
    for ln in open(W+'/data/osm/gettysburg.txt',encoding='utf-8'):
        code,name,body=ln.rstrip('\n').split('|',2); la=lo=0; pts=[]
        for i,pr in enumerate(body.split(';')):
            a,b=pr.split(','); la,lo=(int(a),int(b)) if i==0 else (la+int(a),lo+int(b))
            x,y=g.ll2px(la/1e5,lo/1e5); pts.append(((float(x)-X0)*SC,(float(y)-Y0)*SC))
        yield code,name,pts
def inside(p): return -MG<=p[0]<=CW+MG and -MG<=p[1]<=CH+MG
def pieces(pts):
    """Cut a line into the runs that lie on the crop (each run keeps one point beyond the edge so it reaches it)."""
    out=[];cur=[]
    for i,p in enumerate(pts):
        if inside(p):
            if not cur and i>0: cur.append(pts[i-1])
            cur.append(p)
        elif cur:
            cur.append(p); out.append(cur); cur=[]
    if len(cur)>1: out.append(cur)
    return [c for c in out if len(c)>1]
def path(pts,close=False): return 'M'+'L'.join(f'{x:.0f} {y:.0f}' for x,y in pts)+('Z' if close else '')
CLS={'Hm':'m','Hp':'p','Hs':'s','Ht':'t','Hu':'u','Hr':'r','Hv':'v'}
base={'road':[],'rail':[],'water':[],'wood':[],'lake':[]}; named={}; spots=[]
for code,name,pts in osm_rows():
    if code[0]=='P':
        if inside(pts[0]): spots.append((code,name,pts[0]))
        continue
    if code in('Fw','Fl'):
        if any(inside(p) for p in pts): base['wood' if code=='Fw' else 'lake'].append(path(pts,True))
        if name and any(inside(p) for p in pts): spots.append((code,name,(sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))))
        continue
    for run in pieces(pts):
        d=path(run)
        if code in CLS: base['road'].append([CLS[code],d])
        elif code=='Rr': base['rail'].append(d)
        elif code=='Ra': continue
        else: base['water'].append(['r' if code=='Wr' else 's',d])
        if name and code in('Hm','Hp','Hs','Ht','Hu','Wr','Ws'): named.setdefault((name,code[0]),[]).append((code,run))
# one or two labels per named road or stream, laid along it
OLD={'Chambersburg Road':'Chambersburg Pike','Fairfield Road':'Hagerstown Road'}
LVL0={'Chambersburg Road','Fairfield Road','Mummasburg Road','Biglerville Road','Old Harrisburg Road','Herrs Ridge Road','Knoxlyn Road','Willoughby Run','Marsh Creek','Rock Creek','York Street','Baltimore Street','Old Mill Road','Table Rock Road'}
labels=[]
for (name,kind),runs in sorted(named.items()):
    P_=[p for _,r in runs for p in r if 0<=p[0]<=CW and 0<=p[1]<=CH]
    if len(P_)<2: continue
    ax=0 if max(p[0] for p in P_)-min(p[0] for p in P_)>=max(p[1] for p in P_)-min(p[1] for p in P_) else 1
    P_.sort(key=lambda p:p[ax]); span=math.hypot(P_[-1][0]-P_[0][0],P_[-1][1]-P_[0][1])
    if span<150: continue
    segs=[(r[i],r[i+1]) for _,r in runs for i in range(len(r)-1)]
    for f in ([0.2,0.5,0.8] if span>1700 else [0.5]):
        c=P_[0][ax]+(P_[-1][ax]-P_[0][ax])*f
        hit=[sg for sg in segs if min(sg[0][ax],sg[1][ax])<=c<=max(sg[0][ax],sg[1][ax]) and sg[0][ax]!=sg[1][ax]]
        if hit:
            a_,b_=max(hit,key=lambda sg:math.hypot(sg[1][0]-sg[0][0],sg[1][1]-sg[0][1])); u=(c-a_[ax])/(b_[ax]-a_[ax])
            m=(a_[0]+(b_[0]-a_[0])*u,a_[1]+(b_[1]-a_[1])*u)
        else:
            a_,b_=min(segs,key=lambda sg:abs((sg[0][ax]+sg[1][ax])/2-c)); m=((a_[0]+b_[0])/2,(a_[1]+b_[1])/2)
        if not(70<=m[0]<=CW-70 and 30<=m[1]<=CH-30): continue
        ang=math.degrees(math.atan2(b_[1]-a_[1],b_[0]-a_[0]))
        if ang>90: ang-=180
        if ang<-90: ang+=180
        L_={'t':name,'p':[round(m[0]),round(m[1])],'a':round(ang),'l':0 if name in LVL0 else 1,'k':'w' if kind=='W' else 'r'}
        if name in OLD: L_['s']=OLD[name]
        labels.append(L_)
AREAS={'Herr Ridge':0,'McPherson Ridge':0,'Oak Hill':0,'Oak Ridge':0,'Gettysburg':0,'Railroad Cut':1,"Herbst's Woods":1,'McMillan Woods':1,'Barlow Knoll':1}
seen=set(); areas=[]
for code,name,p in spots:
    if name in AREAS and name not in seen and 0<=p[0]<=CW and 0<=p[1]<=CH:
        seen.add(name); areas.append({'t':name,'p':[round(p[0]),round(p[1])],'l':AREAS[name],'k':'town' if code=='Ptow' else 'area'})
print('current map:',{k:len(v) for k,v in base.items()},len(labels),'line labels',len(areas),'area labels')
data={'w':CW,'h':CH,'mpp':1.2318/SC,'tracks':tracks,'sources':S,'landmarks':lm,'base':base,'labels':labels,'areas':areas}
json.dump(data,open(W+'/playbacks/gettysburg/data.json','w'),separators=(',',':'))
SCAN=W+'/maps/gettysburg/map_full.png'
if os.path.exists(SCAN):
    im=Image.open(SCAN).convert('RGB').crop((X0,Y0,X1,Y1))
    im=im.resize((data['w'],data['h']),Image.LANCZOS); im.save(W+'/playbacks/gettysburg/map.jpg',quality=80,optimize=True,progressive=True)
else: print('map scan not found: base image not rebuilt')
print(data['w'],data['h'], len(open(W+'/playbacks/gettysburg/data.json').read())/1e3,'KB')
for t in tracks: print(t['id'],t['label'],t['ech'],t['branch'],[(k['id'],k['t0'],k['t1'],k['g']) for k in t['k']])
