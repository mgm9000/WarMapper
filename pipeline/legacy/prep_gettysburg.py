"""Gettysburg, the first morning: write this battle's battle file (battle.json).

The record comes from the data pilot workbook (v7: Positions, Units, Assignments, Events, Sources), the fit of the 1876 sheet
(pipeline/georef) and the OpenStreetMap extract (data/osm/gettysburg.txt). What is set here is only what the playback adds:
which rows make up each symbol's track, and how the two maps are cut. If the map scan is present
(maps/gettysburg/map_full.png) the two base pictures are cut again as well.
"""
import sys, os, math
W=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(W,"pipeline")); sys.path.insert(0,os.path.join(W,"pipeline","georef"))
import gettysburg_georef as g, gettysburg_picks as picks
import battlefile as bf
import openpyxl
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
HERE=os.path.join(W,'playbacks','gettysburg')
DAY='1863-07-01'
# The mapped area of the 1876 sheet, in scan pixels, shown at SC of scan resolution;
# and the ground of the first morning (DET), shown at full SC on top of the whole sheet at SCW.
X0,Y0,X1,Y1=650,1178,7300,8120; SC=0.8
DET=(650,1380,5160,4100); SCW=0.4
def px(x,y):
    """a scan pixel of the 1876 sheet -> [longitude, latitude]"""
    la,lo=g.px2ll(x,y); return bf.ll(la,lo)

wb=openpyxl.load_workbook(W+"/data/Military Map Explorer data pilot v7.xlsx",data_only=True,read_only=True)
def table(n):
    it=wb[n].iter_rows(values_only=True); h=next(it)
    return [dict(zip(h,r)) for r in it if r and r[0]]
CAMPAIGN='ACW-GETT'
pos={r['pos_id']:r for r in table('Positions') if r['campaign_id']==CAMPAIGN}
units={r['unit_id']:r for r in table('Units') if str(r['side_id']).startswith('ACW-')}
assign={}
for a in table('Assignments'): assign.setdefault(a['unit_id'],[]).append(a)
catalogue={r['source_id']:{'title':r['title'],'citation':r['citation'],'type':r['type'],'url':r['url']} for r in table('Sources')}

# ---- the playback window and when each row is shown ----
T_START,T_END=435,630     # 7:15 to 10:30, in minutes from midnight
def minutes(s):
    """a workbook time -> minutes from midnight on 1 July; a date before the day counts as midnight"""
    s=bf.iso(s)
    if s is None: return None
    if len(s)==10 or s[:10]<DAY: return 0
    return int(s[11:13])*60+int(s[14:16])
def shown(r):
    """Shown from the latest start the row gives (the end of the window if it has none) to its latest end."""
    t0=minutes(r['start_latest'])
    if t0 is None: t0=T_END
    t1=minutes(r['end_latest'])
    if t1 is None: t1=t0
    return [bf.at_minute(DAY,t0),bf.at_minute(DAY,t1)]
def geom(r,pid):
    if r['lat'] in (None,''): return None
    if pid=='P08':   # Devin's skirmish line is three points read from the sheet
        a,b=picks.LN['DEVSK1']; c=picks.LN['DEVSK2'][1]; return [px(*a),px(*b),px(*c)]
    pts=[bf.ll(r['lat'],r['lon'])]
    if r['line_end_lat'] not in (None,''): pts.append(bf.ll(r['line_end_lat'],r['line_end_lon']))
    return pts

# ---- tracks: one per symbol. id, unit, rows, what the playback adds ----
T=[
 ('US-8IL-pk','US-8IL',['P02'],{'label':'8 IL Cav picket','echelon':'company','hold_until':bf.at_minute(DAY,480),'hide_after':True}),
 ('US-B1','US-B1',['P01','P04','P05'],{}),
 ('US-B1-sk','US-B1',['P03'],{'label':'Gamble skirmishers','echelon':'squadrons','hide_after':True,'loose':True}),
 ('US-3IN','US-3IN',['P28'],{'parent':'US-B1','hide_after':True}),('US-12IL','US-12IL',['P29'],{'parent':'US-B1','hide_after':True}),
 ('US-8IL','US-8IL',['P30'],{'parent':'US-B1','hide_after':True}),('US-8NY','US-8NY',['P31'],{'parent':'US-B1','hide_after':True}),
 ('US-B2','US-B2',['P06'],{}),
 ('US-6NY','US-6NY',['P07'],{'label':'6 NY Cav sqn','echelon':'squadrons','loose':True}),
 ('US-B2-sk','US-B2',['P08'],{'label':'Devin skirmishers','echelon':'squadrons','loose':True}),
 ('US-A2','US-A2',['P09'],{'hide_after':True}),
 ('US-A2-R','US-A2-R',['P10'],{'nudge':[-20,-14]}),('US-A2-N','US-A2-N',['P11'],{'nudge':[20,14]}),('US-A2-P','US-A2-P',['P12'],{}),
 ('CS-ARCH','CS-ARCH',['P14','P16','P17','P18'],{}),
 ('CS-7TN','CS-7TN',['P32'],{'parent':'CS-ARCH','hide_after':True}),('CS-14TN','CS-14TN',['P33'],{'parent':'CS-ARCH','hide_after':True}),
 ('CS-5ALB','CS-5ALB',['P34'],{'parent':'CS-ARCH','hide_after':True}),('CS-13AL','CS-13AL',['P35'],{'parent':'CS-ARCH','hide_after':True}),
 ('CS-1TN','CS-1TN',['P36'],{'parent':'CS-ARCH','hide_after':True}),
 ('CS-DAV','CS-DAV',['P19','P20','P24','P37','P38'],{}),
 ('CS-42MS','CS-42MS',['P21'],{'parent':'CS-DAV','hide_after':True}),('CS-2MS','CS-2MS',['P22'],{'parent':'CS-DAV','hide_after':True}),('CS-55NC','CS-55NC',['P23'],{'parent':'CS-DAV','hide_after':True}),
 ('CS-MARYE','CS-MARYE',['P15'],{'nudge':[0,-26]}),
 ('CS-PETT','CS-PETT',['P26'],{}),('CS-BROCK','CS-BROCK',['P27'],{}),
 ('CS-11MS','CS-11MS',['P25'],{'off_map':'With the division wagon train near Cashtown, about 8 miles west of Gettysburg.'}),
]
tracks=[]; used=set()
for tid,uid,rows,o in T:
    steps=[]
    for pid in rows:
        r=pos[pid]; used.add(pid)
        steps.append({'id':pid,'start':[bf.iso(r['start_earliest']),bf.iso(r['start_latest'])],'end':[bf.iso(r['end_earliest']),bf.iso(r['end_latest'])],'show':shown(r),
          'at':None if o.get('off_map') else geom(r,pid),'activity':r['activity'],'place':r['place_description'],'quote':r['source_wording'],
          'method':r['position_method'],'confidence':r['overall_confidence'],'time_basis':r['time_basis'],
          'location':{'source':r['coord_source'],'basis':r['coordinate_basis'],'confidence':r['coordinate_confidence'],'precision_m':int(r['coord_precision_m']) if r['coord_precision_m'] else None},
          'sources':bf.ids(r['source_ids']),'notes':r['notes'],'review':r['review_status'],'battle':r['battle_id']})
    tracks.append(dict({'id':tid,'unit':uid,'steps':steps},**o))
print('rows not on a track:',sorted(set(pos)-used))

ECH={'Division':'division','Brigade':'brigade','Regiment':'regiment','Regiment (part)':'regiment','Battalion':'battalion','Battery':'battery','Section':'section'}
BR={'Cavalry':'cavalry','Infantry':'infantry','Artillery':'artillery','Horse artillery':'artillery'}
ulist=[]
for uid,u in units.items():
    ulist.append({'id':uid,'name':u['unit_name'],'label':u['map_label'],'side':u['side_id'],'nation':u['nation'],'branch':BR[u['branch']],'echelon':ECH[u['echelon']],
      'sources':bf.ids(u['source_ids']),'notes':u['notes'],
      'assignments':[{'from':bf.iso(a['valid_from']),'to':bf.iso(a['valid_to']),'parent':a['parent_unit_id'],'commander':a['commander'],'strength':a['strength / equipment'],'sources':bf.ids(a['source_ids'])} for a in assign.get(uid,[])]})

# ---- events: from the workbook; the playback marks each at its latest time ----
EXTRA={'GE04':" The spreadsheet says 9:30; Bachelder's map says 9 a.m."}
events=[]
for e in table('Events'):
    if e['campaign_id']!=CAMPAIGN: continue
    events.append({'id':e['event_id'],'start':bf.iso(e['time_earliest']),'end':bf.iso(e['time_latest']),'at':bf.iso(e['time_latest']),'name':e['name'],
      'text':e['summary']+EXTRA.get(e['event_id'],''),'steps':[s for s in bf.ids(e['pos_ids']) if s in used],'sources':bf.ids(e['source_ids']),'battle':e['battle_id']})

# ---- labels ----
# landmarks named on both maps, and two the current map names for itself, so they are shown on the 1876 map only
labels=[{'text':n,'at':px(x,y),'kind':'landmark','show':show} for n,(x,y,show) in {'Herr Tavern':(2484,2545,'both'),'Lutheran Seminary':(3745,3433,'both'),'Willoughby Run':(2893,2960,'period'),
        'Chambersburg Pike':(1900,2215,'period'),'McPherson farm':(3165,3040,'both'),'Pennsylvania College':(4444,3168,'both')}.items()]

# ---- current map: today's roads, streams, woods and names from the OpenStreetMap extract, cut to the sheet.
#      The cutting is done in the sheet's own pixels (at SC), then every point goes back to longitude and latitude. ----
CW,CH=round((X1-X0)*SC),round((Y1-Y0)*SC); MG=40
def back(p): return px(p[0]/SC+X0,p[1]/SC+Y0)
def osm_rows():
    for ln in open(W+'/data/osm/gettysburg.txt',encoding='utf-8'):
        code,name,body=ln.rstrip('\n').split('|',2); la=lo=0; pts=[]
        for i,pr in enumerate(body.split(';')):
            a,b=pr.split(','); la,lo=(int(a),int(b)) if i==0 else (la+int(a),lo+int(b))
            x,y=g.ll2px(la/1e5,lo/1e5); pts.append(((float(x)-X0)*SC,(float(y)-Y0)*SC))
        yield code,name,pts
def inside(p): return -MG<=p[0]<=CW+MG and -MG<=p[1]<=CH+MG
def pieces(pts):
    """Cut a line into the runs that lie on the sheet (each run keeps one point beyond the edge so it reaches it)."""
    out=[];cur=[]
    for i,p in enumerate(pts):
        if inside(p):
            if not cur and i>0: cur.append(pts[i-1])
            cur.append(p)
        elif cur:
            cur.append(p); out.append(cur); cur=[]
    if len(cur)>1: out.append(cur)
    return [c for c in out if len(c)>1]
def enc(pts): return bf.pack([back(p) for p in pts])
ROAD={'Hm':'m','Hp':'p','Hs':'s','Ht':'t','Hu':'u','Hr':'r','Hv':'v'}
lines=[]; areas=[]; named={}; spots=[]
for code,name,pts in osm_rows():
    if code[0]=='P':
        if inside(pts[0]): spots.append((code,name,pts[0]))
        continue
    if code in('Fw','Fl'):
        if any(inside(p) for p in pts): areas.append(['wood' if code=='Fw' else 'water',name,enc(pts)])
        if name and any(inside(p) for p in pts): spots.append((code,name,(sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))))
        continue
    for run in pieces(pts):
        if code in ROAD: lines.append(['road',ROAD[code],name,enc(run)])
        elif code=='Rr': lines.append(['rail','',name,enc(run)])
        elif code=='Ra': continue
        else: lines.append(['water','river' if code=='Wr' else 'stream',name,enc(run)])
        if name and code in('Hm','Hp','Hs','Ht','Hu','Wr','Ws'): named.setdefault((name,code[0]),[]).append((code,run))
# one or two labels per named road or stream, laid along it
OLD={'Chambersburg Road':'Chambersburg Pike','Fairfield Road':'Hagerstown Road','York Road':'York Pike'}
LVL0={'Chambersburg Road','Fairfield Road','Mummasburg Road','Biglerville Road','Old Harrisburg Road','Herrs Ridge Road','Knoxlyn Road','Willoughby Run','Marsh Creek','Rock Creek','York Road','Baltimore Pike','Emmitsburg Road','Taneytown Road','Hanover Road','Old Mill Road','Table Rock Road','Plum Run'}
ROT=math.degrees(math.atan2(g.b,g.a))   # the sheet sits this many degrees off north, so a direction read on the sheet is turned by it
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
        labels.append({'text':name,'alt':OLD.get(name),'at':back(m),'angle':round(ang+ROT),'level':0 if name in LVL0 else 1,'kind':'water' if kind=='W' else 'road'})
AREAS={'Herr Ridge':0,'McPherson Ridge':0,'Oak Hill':0,'Oak Ridge':0,'Gettysburg':0,'Seminary Ridge':0,'Cemetery Ridge':0,'Cemetery Hill':0,'Culps Hill':0,'Little Round Top':0,'Big Round Top':0,
       'Railroad Cut':1,"Herbst's Woods":1,'McMillan Woods':1,'Barlow Knoll':1,'Benner Hill':1,'The Peach Orchard':1,"Devil's Den":1,'The Wheat Field':1,'Warfield Ridge':1,'Powers Hill':1,"Wolf's Hill":1,"Spangler's Spring":1,'Pitzer Woods':1,'Rose Woods':1}
seen=set()
for code,name,p in spots:
    if name in AREAS and name not in seen and 0<=p[0]<=CW and 0<=p[1]<=CH:
        seen.add(name); labels.append({'text':name,'at':back(p),'level':AREAS[name],'kind':'town' if code=='Ptow' else 'area'})

# ---- the 1876 sheet: the whole of it, and the first morning's ground at twice the detail ----
def quad(x0,y0,x1,y1): return [px(x0,y0),px(x1,y0),px(x1,y1),px(x0,y1)]
sheet=quad(X0,Y0,X1,Y1)
maps=[{'id':'bachelder-1876','title':"Bachelder, Map of the battle field of Gettysburg: first day's battle (1876)",'credit':'Bachelder, 1876 · Boston Public Library','source':'S18',
       'fit':{'method':'similarity (scale, turn and shift) on four landmarks','metres_per_pixel':round(math.hypot(g.a,g.b),4),'turn_degrees':round(ROT,2)},
       'images':[{'file':'map_wide.jpg','corners':sheet},{'file':'map.jpg','corners':quad(*DET),'detail':True}]}]
SCAN=W+'/maps/gettysburg/map_full.png'
if os.path.exists(SCAN):
    full=Image.open(SCAN).convert('RGB')
    im=full.crop(DET).resize((round((DET[2]-DET[0])*SC),round((DET[3]-DET[1])*SC)),Image.LANCZOS); im.save(HERE+'/map.jpg',quality=80,optimize=True,progressive=True)
    im=full.crop((X0,Y0,X1,Y1)).resize((round((X1-X0)*SCW),round((Y1-Y0)*SCW)),Image.LANCZOS); im.save(HERE+'/map_wide.jpg',quality=78,optimize=True,progressive=True)
else: print('map scan not found: base pictures not rebuilt')

# ---- how this battle is played back: the settings the shared player reads (docs/battle-file.md, "playback") ----
playback={'page_title':'Gettysburg Day 1 Playback','style':'tactical','scale_bar':'yards','rate':3,'bounds':'bachelder-1876',
 'follow':{'min':[1390,925],'margin':140},
 'bases':[{'id':'old','label':'1876 map','short':'1876','title':"Bachelder's 1876 map of the first day (M switches maps)",'map':'bachelder-1876','backdrop':'paper','fade':True},
          {'id':'mod','label':'Current map','short':'Today','title':'The same ground today, from OpenStreetMap (M switches maps)','current':True,'clip':'bachelder-1876'}],
 # zoom levels, in screen pixels per metre, at which things appear or change
 'zoom':{'max':1.95,'min_factor':0.96,'follow_max':1.04,'fold':0.215,'labels':0.273,'towns_until':0.487,'landmarks_from':0.195,'minor_roads_from':0.156,'force_names_from':0.195},
 'fold':{'label':'Regiments'},'rules':{'blend':4},
 'texts':{'stated':'A report, tablet or the 1876 map puts the unit here.','inferred':'Worked out from the sequence of events, not stated by a source.',
          'moving':'No source records this stretch. The unit is drawn on a straight line between two recorded positions.'},
 'found':{'map_read':'read from the 1876 map','estimate':'estimated from the description'},
 'about':[l for l in open(HERE+'/about.txt',encoding='utf-8').read().split('\n') if l]}
battle={'id':'gettysburg-day1-morning','title':'Gettysburg, the first morning','subtitle':"Buford's cavalry against Heth's division on the Chambersburg Pike",'playback':playback,
 'record':{'workbook':'Military Map Explorer data pilot v7','campaign':CAMPAIGN,'battles':['GETT-D1-AM','GETT-D1','GETT']},
 # Gettysburg is fought on three numbered days, 1 to 3 July 1863
 'time':{'unit':'minute','zero':DAY+'T00:00','start':bf.at_minute(DAY,T_START),'end':bf.at_minute(DAY,T_END),'focus':[bf.at_minute(DAY,450),bf.at_minute(DAY,615)],
         'calendar':{'first':DAY,'numbered':True,'days':3}},
 'view':{'origin':bf.ll(g.LAT0,g.LON0),'extent':[min(c[0] for c in sheet),min(c[1] for c in sheet),max(c[0] for c in sheet),max(c[1] for c in sheet)]},
 'opening':{'label':'Before 7:30','text':"Before the first shot. Gamble's brigade is in camp at the seminary and Calef's battery is on the pike."},
 'sides':[{'id':'ACW-US','code':'US','name':'United States (Union)','short':'Union','colour':'blue'},{'id':'ACW-CS','code':'CS','name':'Confederate States','short':'Confederate','colour':'red'}],
 'units':ulist,'tracks':tracks,'events':events,'labels':labels,'maps':maps,
 'base':{'credit':'© OpenStreetMap contributors','source':'S39','lines':lines,'areas':areas}}
battle['sources']=bf.used_sources(battle,catalogue,['S39'])
bf.write(battle,HERE+'/battle.json')
