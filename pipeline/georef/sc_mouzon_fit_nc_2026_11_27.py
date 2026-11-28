"""Mouzon 1775 fitted to the ground in North Carolina too, without moving South Carolina (SC storyline Session 2, 27 Nov 2026).

  NE_DIR=natural-earth python3 -I pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py      rewrites pairs and PC in pipeline/georef/sc_mouzon_fit.json

NE_DIR holds the GeoJSON files of github.com/nvkelso/natural-earth-vector (geojson/): rivers_north_america, rivers_lake_centerlines,
coastline, admin_1_states_provinces_lines (all ne_10m_), public domain (S136).

Why. The regional map for the chapter's battles and campaign (Cowpens to Guilford Courthouse) needs Mouzon's North Carolina, which is on
the same four mounted sections of the scan as South Carolina's upper half. The fit of 26 Nov 2026 holds South Carolina; this extends it.

How, so that nothing Morgan has reviewed moves:
  - every pair of the 26 Nov fit is kept (pairs_refit_2026_11_26 holds them, so this can be run again);
  - ANCHORS: every vertex of every reviewed South Carolina line (pipeline/recon/sc_1775_traced.json) is added as a pair, at the ground
    point the 26 Nov fit gives it, held to 0.25 km. The splines may then bend north of the old crop but not inside it;
  - nine North Carolina towns as point controls, read on the scan where Mouzon draws them and placed on today's ground by a cited site
    (TOWNS, 1.5-2 km), and one seam tie on the Pee Dee (TIES). Brunswick was tried and left out: held, it folded the ground at New Inlet, and left out it is found again 21 km
    from its site (Mouzon draws the lower Cape Fear out of true with itself);
  - the traced North Carolina rivers, coast and Virginia line matched to the same lines in Natural Earth, seven times over (as
    sc_mouzon_fit.py did), pairs held to 10 km so that none folds the ground. Pairs on 20th-century reservoirs are dropped (RES); so are
    those inside ZONES, where the fold of the 26 Nov fit is mended (below).
Result (printed when run): outside the fold zones every South Carolina vertex moves at most 20 m (median 0). Inside them (Morgan asked
for the fold to be fixed, 27 Nov 2026) the South Carolina lines move onto today's ground: the Catawba up to 18.6 km (its stretch from the
1772 line to below the Catawba Nation had been matched to the river north of the state line), the road from the Catawba Nation to Charlotte
up to 18.6 km, the Cherokee path's east end 11 km, the east end of the 1772 line 10.8 km, the 1764 line's middle vertex 12.3 km, the
Broad above the Pacolet 6.9 km and the Pacolet's mouth 1 km. One grid point still folds, at crop (2600, 475) where the Pacolet meets the
Broad, a small fold the 26 Nov fit already had. The North Carolina towns are held within 0.2 km; left out in turn, each is found again
0.3-6.6 km from its site. The rivers lie a median 0.1-0.75 km from today's courses (90% within 1-2 km). No North Carolina line folds.
"""
import json, math, os, sys, time
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIT=json.load(open(f'{ROOT}/pipeline/georef/sc_mouzon_fit.json'))
SC=json.load(open(f'{ROOT}/pipeline/recon/sc_1775_traced.json'))
NC=json.load(open(f'{ROOT}/pipeline/recon/nc_1775_traced.json'))
KX,KY=92.83,110.9
SY,SX=FIT['seam']['y'],FIT['seam']['x']
def panel(x,y): return ('U' if y<SY else 'L')+('L' if x<SX else 'R')
def xy(ll): return ((ll[0]+81.0)*KX,(ll[1]-33.5)*KY)
def ll(p): return (p[0]/KX-81.0,p[1]/KY+33.5)
def models(P,smooth):
    M={}
    for pn in ['UL','UR','LL','LR']:
        X,Y,W=[],[],[]
        for m,g,sd in P:
            p2=panel(*m)
            if p2==pn or (abs(m[1]-SY)<160 and p2[1]==pn[1]) or (abs(m[0]-SX)<160 and p2[0]==pn[0]): X.append(m);Y.append(g);W.append(sd)
        M[pn]=RBFInterpolator(np.array(X,float),np.array(Y,float),kernel='thin_plate_spline',smoothing=np.array(W)**2*smooth.get(pn,8.0),degree=1)
    return M
def apply(M,pts):
    pts=np.asarray(pts,float); out=np.zeros_like(pts)
    pn=np.array([panel(x,y) for x,y in pts])
    for k,f in M.items():
        s=pn==k
        if s.any(): out[s]=f(pts[s])
    return out
BASE0=FIT.get('pairs_refit_2026_11_26',FIT['pairs'])
# The fold (Morgan, 27 Nov 2026, evening: "fix it"). The 26 Nov fit turns the ground over where the Broad and the Catawba cross the 1772 line
# (crop x 2675-3200, y 0-185; and two small patches): with the Lake Wylie pairs dropped nothing held the Catawba there, and it put Mouzon's
# Catawba at the line 8.7 km north-west of today's. Inside ZONES the South Carolina vertices are not held, the 26 Nov pairs are dropped, and
# FIXES (where today's Broad and Catawba cross the state line, which follows the 1772 line there) and the rivers matched to today's hold the map.
ZONES=[(2300,-80,2650,330),(2650,-80,3200,440),(3425,455,3550,525)]
def inzone(m,pad=0): return any(a-pad<=m[0]<=b+pad and c-pad<=m[1]<=d+pad for a,c,b,d in ZONES)
BASE=[p for p in BASE0 if not inzone(p[0])]
OLD=models(BASE0,FIT['smoothing'])
# anchors: every 4th point of every reviewed South Carolina line, mapped by the 26 Nov fit
scpts=[tuple(p) for v in SC.values() for p in v['line']]
scpts=list(dict.fromkeys(scpts))
anch_g=apply(OLD,scpts)
ANCH=[[list(map(float,m)),[round(float(a),4),round(float(b),4)],0.25] for m,(a,b) in zip(scpts,anch_g) if not inzone(m,40)]
TOWNS=[ # name, M, (lon, lat), sd_km, source
 ('Charlotte (the court house crossroads)',(3112,-79),(-80.84333,35.22694),1.5,'workbook Labels (cowpens: Charlotte)'),
 ('Salisbury (the court house)',(3483,-588),(-80.46885,35.66848),1.5,'Rowan County Courthouse marker, HMdb 34278'),
 ('Salem',(3743,-1068),(-80.2419,36.0854),1.5,'Salem Tavern, Old Salem Historic District (NRHP)'),
 ('Bethabara',(3717,-1135),(-80.2986,36.1544),1.5,'Bethabara Historic District (NRHP 78001948)'),
 ('New Garden Meeting House',(4127,-1062),(-79.889164,36.090444),2.0,'workbook Labels (guilford-courthouse)'),
 ('Hillsborough',(4772,-1057),(-79.0956,36.0736),1.5,'Hillsborough Historic District (NRHP 73001363)'),
 ('Halifax (the court house)',(6094,-1235),(-77.58956,36.32875),1.5,'Halifax Court House (NRHP 79001719)'),
 ('Cross Creek (the old state house site, Market House, Fayetteville)',(4940,70),(-78.878306,35.052556),1.5,'Market House, Fayetteville (NRHP 70000451)'),
 ('Wilmington',(5738,1300),(-77.9508,34.235),1.5,'Wilmington Historic District (NRHP 74001364)'),
]
# Seam tie (as the refit of 26 Nov tied the Pee Dee across the horizontal gap): Mouzon's two upper sections do not meet on the Pee Dee, so
# its last point above the vertical gap (crop x 4232) is tied to where the reviewed South Carolina Pee Dee begins below it, on the ground as
# sc-1775 had it before this extension; the North Carolina side takes up the difference (its last 13 km are left out of the matching).
FIXES=[('Catawba at the 1772 line',(2905,92),(-81.0384,35.1304),2.0,'Natural Earth (S136): the Catawba where the state line (the line of 1772) reaches it'),
      ]   # the Broad's crossing was tried as a control too and left out: held with the Broad matched to today's, it folded the ground beside it
TIES=[('Pee Dee at the vertical seam (tie)',(4216,282),(-79.919936,34.973568),2.5,'the start of the South Carolina Pee Dee (SC75-RIV-PEEDEE), as built on 26 Nov 2026')]
TP=[[list(map(float,m)),[round(xy(g)[0],4),round(xy(g)[1],4)],sd] for _,m,g,sd,_ in TOWNS+TIES+FIXES]
# Natural Earth targets
NE=os.environ.get('NE_DIR','natural-earth')+'/'
def lines(f,filt=None):
    out={}
    for ft in json.load(open(NE+f+'.geojson'))['features']:
        g=ft['geometry']
        if not g: continue
        L=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
        nm=ft['properties'].get('name') or ''
        if filt and not filt(ft['properties']): continue
        for l in L:
            if any(-84.5<c[0]<-75 and 32<c[1]<37.5 for c in l): out.setdefault(nm,[]).append([tuple(c[:2]) for c in l])
    return out
R={}
for f in ['ne_10m_rivers_north_america','ne_10m_rivers_lake_centerlines']:
    for k,v in lines(f).items(): R.setdefault(k,[]).extend(v)
COAST=[l for v in lines('ne_10m_coastline').values() for l in v]
VANC=[l for v in lines('ne_10m_admin_1_states_provinces_lines',lambda p:'Virginia' in ' '.join(str(x) for x in p.values() if isinstance(x,str)) and 'North Carolina' in ' '.join(str(x) for x in p.values() if isinstance(x,str))).values() for l in v]
MATCH={'riv-catawba-1':['Catawba'],'riv-broad-1':['Broad'],'riv-catawba-nc':['Catawba'],'riv-broad-nc':['Broad'],'riv-yadkin':['Yadkin','Great Pee Dee'],'riv-peedee-nc':['Great Pee Dee','Yadkin'],'riv-haw':['Haw'],'riv-deep':['Deep'],
       'riv-capefear':['Cape Fear'],'riv-dan':['Dan'],'riv-roanoke':['Roanoke'],'shore-nc':'COAST','bnd-va':'VANC'}
RES={'James':(-82.0,-81.8,35.7,35.8),'Rhodhiss-Hickory-Lookout':(-81.6,-81.0,35.7,35.85),'Norman':(-81.0,-80.85,35.4,35.65),'Mountain Island':(-81.0,-80.92,35.3,35.42),
     'High Rock':(-80.4,-80.15,35.55,35.75),'Tuckertown-Badin-Tillery':(-80.15,-79.98,35.25,35.6),'W Kerr Scott':(-81.3,-81.15,36.1,36.15),'Blewett Falls':(-79.95,-79.85,35.0,35.15),
     'Jordan':(-79.12,-78.95,35.62,35.85),'Kerr':(-78.8,-78.2,36.45,36.72),'Gaston':(-78.2,-77.75,36.45,36.62),'Roanoke Rapids':(-77.75,-77.6,36.45,36.52),'Lure':(-82.25,-82.15,35.4,35.46),'Wylie':(-81.15,-80.95,35.0,35.25),'Fishing Creek':(-80.95,-80.85,34.55,34.70)}
def inres(g):
    lo,la=ll(g); return any(a<=lo<=b and c<=la<=d for a,b,c,d in RES.values())
def tgt(fid):
    v=MATCH[fid]
    if v=='COAST': return COAST
    if v=='VANC': return VANC
    return [l for n in v for l in R.get(n,[])]
def seg_tree(L):
    P=[];A=[];B=[]
    for l in L:
        q=[xy(c) for c in l]
        for a,b in zip(q,q[1:]): A.append(a);B.append(b)
    A=np.array(A);B=np.array(B); return A,B,cKDTree((A+B)/2)
def nearest(p,T):
    A,B,tr=T; idx=tr.query(p,k=min(40,len(A)))[1]; best=(1e9,None)
    for i in np.atleast_1d(idx):
        a,b=A[i],B[i]; d=b-a; t=max(0,min(1,np.dot(np.array(p)-a,d)/(np.dot(d,d)+1e-12))); q=a+t*d; dd=np.hypot(*(np.array(p)-q))
        if dd<best[0]: best=(dd,q)
    return best
TREES={k:seg_tree(tgt(k)) for k in MATCH}
def samples(step=12):
    out=[]
    for fid in MATCH:
        pts=(NC.get(fid) or SC[fid])['line']; acc=0
        if fid in SC: pts=[q for q in pts if inzone(q)]
        for a,b in zip(pts,pts[1:]):
            L=math.hypot(b[0]-a[0],b[1]-a[1]); n=max(1,int(L/step))
            for j in range(1,n+1):
                q=(a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n); acc+=L/n
                if acc>=step: acc=0; out.append((fid,q))
    return out
NCSD=10.0   # km: stiff enough that no North Carolina line folds the ground (4 and 6 left folds at Halifax and New Inlet)
SM={'UL':40.0,'LL':40.0,'UR':200.0,'LR':200.0}
def run(verbose=True):
    base=BASE+ANCH+TP
    M=models(base,SM); S=samples(); pairs=None
    for it,lim in enumerate([25,18,12,9,7,6,5]):
        t=time.time(); P=apply(M,[s[1] for s in S]); new=[]; used=0
        for (fid,m),p in zip(S,P):
            d,q=nearest(p,TREES[fid])
            if fid in ('riv-catawba-nc','riv-broad-nc') and m[1]>-150: continue
            if fid=='riv-peedee-nc' and m[1]>150: continue   # held by the seam tie   # let the North Carolina reach leave the reviewed South Carolina end smoothly
            if d<lim and not inres(q): new.append([list(map(float,m)),[round(float(q[0]),4),round(float(q[1]),4)],NCSD]); used+=1
        M=models(base+new,SM); pairs=new
        r=[math.hypot(*(apply(M,[m])[0]-np.array(g))) for m,g,sd in TP]
        if verbose: print('iter',it,'lim',lim,'pairs',used,'towns med %.2f max %.2f km'%(np.median(r),max(r)),'%.0fs'%(time.time()-t),flush=True)
    return M,base,pairs
if __name__=='__main__':
    M,base,pairs=run()
    allsc=[tuple(p) for v in SC.values() for p in v['line']]
    a=apply(OLD,allsc); b=apply(M,allsc); d=np.hypot(*(a-b).T)
    z=np.array([inzone(q,40) for q in allsc])
    print('South Carolina vertices outside the fold zones',int((~z).sum()),'moved: median %.0f m, max %.0f m'%(np.median(d[~z])*1000,d[~z].max()*1000))
    print('inside the fold zones',int(z.sum()),'moved: median %.1f km, max %.1f km'%(np.median(d[z]),d[z].max()))
    for k,v in SC.items():
        q=[tuple(p) for p in v['line']]; dd=np.hypot(*(apply(OLD,q)-apply(M,q)).T)
        if dd.max()>0.5: print('   %-28s moves up to %.1f km (median %.1f)'%(k,dd.max(),np.median(dd)))
    nf=0
    for y in range(-50,900,25):
        for x in range(2200,3600,25):
            pq=np.array([x,y],float); a3=apply(M,[pq,pq+[2,0],pq+[0,2]])
            if np.linalg.det(np.array([a3[1]-a3[0],a3[2]-a3[0]]).T)>=0: nf+=1
    print('folded grid points (crop x 2200-3600, y -50 to 900):',nf)
    full=base+pairs; loo={}
    for (nm,m,g,sd,src) in TOWNS:
        e=math.hypot(*(apply(M,[m])[0]-np.array(xy(g))))
        M2=models([p for p in full if p[0]!=list(map(float,m))],SM); l=math.hypot(*(apply(M2,[m])[0]-np.array(xy(g)))); loo[nm]=round(l*1000)
        print('%-62s held within %.2f km, left out %.1f km'%(nm,e,l))
    F=json.load(open(f'{ROOT}/pipeline/georef/sc_mouzon_fit.json'))
    F.setdefault('pairs_refit_2026_11_26',F['pairs']); F.setdefault('PC_refit_2026_11_26',F['PC'])
    F['PC']=F['PC_refit_2026_11_26']+[{'name':n,'m':list(m),'lonlat':list(g),'sd_km':sd,'source':src,'added':'2026-11-27','loo_m':loo[n]} for n,m,g,sd,src in TOWNS]+[{'name':n,'m':list(m),'lonlat':list(g),'sd_km':sd,'source':src,'added':'2026-11-27'} for n,m,g,sd,src in TIES+FIXES]
    F['pairs']=full
    F['extend_nc']={'date':'2026-11-27','anchors':len(ANCH),'towns':len(TP),'pairs_nc':len(pairs),'sd_nc_km':NCSD,'reservoirs':sorted(RES),
                    'sc_moved_m_outside_zones':{'median':round(float(np.median(d[~z]))*1000),'max':round(float(d[~z].max())*1000)},'zones':ZONES,
                    'why':'North Carolina for the regional map; see pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py'}
    json.dump(F,open(f'{ROOT}/pipeline/georef/sc_mouzon_fit.json','w'))
    print('pairs',len(F['pairs_refit_2026_11_26']),'->',len(full))
