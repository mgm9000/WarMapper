"""Fit Mouzon 1775 (half-res crop of LOC g3900.ar139404) to the ground: per-panel thin-plate splines from point controls and from
matching the traced rivers and coast to today's (Natural Earth) lines, iterated (ICP)."""
import json,math,os,sys
import numpy as np
from scipy.interpolate import RBFInterpolator
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(os.path.dirname(HERE),'recon'))
import sc_natural_earth as ne, sc_1775_picks as picks
SN={k:v['line'] for k,v in json.load(open(os.path.join(os.path.dirname(HERE),'recon','sc_1775_traced.json'))).items() if not v.get('straight')}
def _dens(p,step=10):
    out=[p[0]]
    for a,b in zip(p,p[1:]):
        n=max(1,int(math.hypot(b[0]-a[0],b[1]-a[1])/step))
        out+= [(a[0]+(b[0]-a[0])*k/n,a[1]+(b[1]-a[1])*k/n) for k in range(1,n+1)]
    return out
for _k in ('bnd-nc-1772','bnd-nc-old','bnd-nc-1764e'): SN[_k]=_dens(picks.F[_k]['pts'])
SEAM_Y=1222; SEAM_X=4232
def panel(x,y): return ('U' if y<SEAM_Y else 'L')+('L' if x<SEAM_X else 'R')
# point controls: name, M(x,y), (lon,lat), sd_km, source
PC=[('Ninety Six',(2212,1368),(-82.02444,34.14694),1.0,'workbook SCP05 (S116, S117)'),
    ('Fort Charlotte',(1762,1638),(-82.5399235,33.9527111),1.5,'workbook SCP04'),
    ("Monck's Corner",(3953,2476),(-80.00667,33.19667),1.0,'workbook SCC17'),
    ('Fort Johnson',(4080,3068),(-79.9331454,32.7303256),0.8,'workbook SCP02 (S120)'),
    ('Esseneca (Sennekaw)',(1200,905),(-82.845133,34.666883),2.5,'workbook SCP06'),
    ('Broad and Saluda meet (the Congaree)',(3125,1590),(-81.056,34.004),1.5,'Natural Earth'),
    ('Wateree and Congaree meet (the Santee)',(3478,1803),(-80.632,33.751),2.0,'Natural Earth'),
    ('Lynches Creek meets the Pee Dee',(4727,1627),(-79.354,33.837),2.5,'Natural Earth'),
    ('Little Pee Dee meets the Pee Dee',(4790,1700),(-79.189,33.703),2.5,'Natural Earth'),
    ('Edisto forks',(3344,2546),(-80.892,33.264),2.5,'Natural Earth'),
    ('Pee Dee at Winyah Bay',(4775,2225),(-79.19,33.437),2.0,'Natural Earth'),
    ('Savannah River mouth',(3279,3993),(-80.891,32.032),2.0,'Natural Earth'),
    ('NC line at the sea, Little River',(5283,1695),(-78.573,33.883),2.0,'Natural Earth (state line)'),
    ('Santee mouth',(4767,2517),(-79.339,33.155),2.5,'Natural Earth'),
   ]
MATCH={'riv-savannah':['Savannah'],'riv-broad':['Broad'],'riv-saluda':['Saluda'],'riv-congaree':['Congaree'],'riv-wateree':['Wateree','Catawba'],
       'riv-catawba':['Catawba'],'riv-santee':['Santee'],'riv-peedee':['Great Pee Dee'],'riv-littlepeedee':['Little Pee Dee'],'riv-lynches':['Lynches'],
       'riv-edisto-n':['North Fork Edisto'],'riv-edisto':['Edisto'],'riv-waccamaw':['Waccamaw'],'riv-cooper':['Cooper'],'shore':'COAST','bnd-nc':'NCSC'}
R=ne.rivers(); C=ne.coast(); NCSC=[l for nm,l in ne.borders() if 'North Carolina' in nm and 'South Carolina' in nm]
def target(fid):
    for k,v in MATCH.items():
        if fid.startswith(k): return C if v=='COAST' else NCSC if v=='NCSC' else [l for n in v for l in R.get(n,[])]
    return None
def samples(step=12):
    out=[]
    for fid,pts in SN.items():
        T=target(fid)
        if not T: continue
        acc=0
        for (a,b) in zip(pts,pts[1:]):
            d=math.hypot(b[0]-a[0],b[1]-a[1]); acc+=d
            if acc>=step: acc=0; out.append((fid,(b[0],b[1]),T))
    return out
class Fit:
    def __init__(s,models): s.m=models
    def __call__(s,P):
        P=np.asarray(P,float); out=np.zeros_like(P)
        for i,(x,y) in enumerate(P): out[i]=s.m[panel(x,y)](np.array([[x,y]]))[0]
        return out
def solve(pairs,smooth):
    models={}
    for pn in ['UL','UR','LL','LR']:
        X=[];Y=[];W=[]
        for (m,g,sd) in pairs:
            p2=panel(*m); near = p2==pn or (abs(m[1]-SEAM_Y)<160 and p2[1]==pn[1]) or (abs(m[0]-SEAM_X)<160 and p2[0]==pn[0])
            if near: X.append(m);Y.append(g);W.append(sd)
        if len(X)<12: X=[p[0] for p in pairs];Y=[p[1] for p in pairs];W=[p[2] for p in pairs]
        X=np.array(X,float);Y=np.array(Y,float)
        models[pn]=RBFInterpolator(X,Y,kernel='thin_plate_spline',smoothing=np.array(W)**2*smooth,degree=1)
    return Fit(models)
def run(iters=7,verbose=True):
    base=[(m,ne.xy(g),sd) for (_,m,g,sd,_) in PC]
    fit=solve(base,50.0)
    S=samples()
    for it,lim in enumerate([25,18,12,9,7,6,5][:iters]):
        P=fit([s[1] for s in S]); pairs=list(base); used=0
        for (fid,m,T),p in zip(S,P):
            d,q=ne.nearest(p,T)
            if d<lim: pairs.append((m,q,4.0)); used+=1
        fit=solve(pairs,8.0)
        if verbose:
            r=[math.hypot(*(fit([m])[0]-np.array(g))) for (m,g,sd) in base]
            print('iter',it,'pairs',used,'controls median %.2f km max %.2f'%(np.median(r),max(r)))
    return fit,pairs
if __name__=='__main__':
    fit,pairs=run()
    import pickle; pickle.dump(pairs,open('sc_mouzon_pairs.pkl','wb'))   # written to the current folder; pipeline/georef/sc_mouzon_fit.json holds the pairs used
    # leave-one-out on point controls
    base=[(m,ne.xy(g),sd) for (_,m,g,sd,_) in PC]
    for i,(nm,m,g,sd,src) in enumerate(PC):
        pr=[p for p in pairs if p[0]!=m]
        f2=solve(pr,8.0); e=math.hypot(*(f2([m])[0]-np.array(ne.xy(g))))
        print('LOO %-40s %.2f km'%(nm,e))
