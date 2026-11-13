import math, json, numpy as np
import os
W=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'data','osm','')
LAT0,LON0=40.2203,-74.7650
K=111320*math.cos(math.radians(LAT0)); M=111040
def xy(lat,lon): return ((lon-LON0)*K,(lat-LAT0)*M)
def ll(x,y): return (LAT0+y/M, LON0+x/K)
def load():
    ways=[]
    for line in open(W+'trenton.txt',encoding='utf-8').read().strip().split('\n'):
        code,name,g=line.split('|'); la=lo=0; pts=[]
        for p in g.split(';'):
            a,b=p.split(','); la+=int(a); lo+=int(b); pts.append((la/1e5,lo/1e5))
        ways.append({'zone':code[0],'cls':code[1],'name':name,'pts':pts})
    return ways
def seg_inter(p1,p2,p3,p4):
    x1,y1=xy(*p1);x2,y2=xy(*p2);x3,y3=xy(*p3);x4,y4=xy(*p4)
    d=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(d)<1e-9: return None
    t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/d; u=-((x1-x2)*(y1-y3)-(y1-y2)*(x1-x3))/d
    if -0.05<=t<=1.05 and -0.05<=u<=1.05: return ll(x1+t*(x2-x1),y1+t*(y2-y1))
def cross(ways,a,b):
    out=[]
    for wa in ways:
        if wa['name']!=a: continue
        for wb in ways:
            if wb['name']!=b: continue
            for i in range(len(wa['pts'])-1):
                for j in range(len(wb['pts'])-1):
                    r=seg_inter(wa['pts'][i],wa['pts'][i+1],wb['pts'][j],wb['pts'][j+1])
                    if r: out.append((round(r[0],5),round(r[1],5)))
    return out
# sketch (full-res px) <-> modern control points in the consistent part of the town
CP=[('Queen & Second (Broad & State)',2290,1125,40.22015,-74.76421),('King & Second (Warren & State)',2095,1125,40.22030,-74.76589),
    ('Queen & Third (Broad & Hanover)',2290,990,40.22096,-74.76425),('King & Third (Warren & Hanover)',2095,990,40.22104,-74.76577),
    ('English Church (St. Michael\'s)',2190,850,40.22220,-74.76535),('Queen Street bridge',2265,1490,None,None)]
def fit(cp):
    A=[];B=[]
    for n,x,y,la,lo in cp:
        E,N=xy(la,lo); A.append([x,-y,1,0]);B.append(E);A.append([-y,-x,0,1]);B.append(N)
    a,b,tx,ty=np.linalg.lstsq(np.array(A,float),np.array(B,float),rcond=None)[0]
    return a,b,tx,ty
def mk(cp):
    a,b,tx,ty=fit(cp)
    def sk2ll(x,y): return ll(a*x-b*y+tx, -(b*x+a*y)+ty)
    def ll2sk(la,lo):
        E,N=xy(la,lo); u=E-tx; v=-(N-ty); d=a*a+b*b
        return ((a*u+b*v)/d, (a*v-b*u)/d)
    return sk2ll,ll2sk,(a,b,tx,ty)
if __name__=='__main__':
    ways=load(); print(len(ways),'ways')
    br=cross(ways,'South Broad Street','Assunpink Creek'); print('bridge',br)
    for a,b in [('Pennington Avenue','Calhoun Street'),('East Hanover Street','North Montgomery Street'),('Perry Street','North Montgomery Street'),('Perry Street','North Stockton Street'),('East State Street','North Montgomery Street'),('East Hanover Street','North Stockton Street'),('Martin Luther King Jr Boulevard','Fountain Avenue'),('Academy Street','North Montgomery Street'),('East Front Street','South Broad Street'),('Perry Street','North Broad Street'),('Academy Street','North Stockton Street'),('West State Street','Calhoun Street'),('East Front Street','South Montgomery Street')]:
        print(a,'x',b,cross(ways,a,b))
    cp=[c for c in CP if c[3]]
    if br: cp.append(('Queen Street bridge',2265,1490,br[0][0],br[0][1]))
    sk2ll,ll2sk,(a,b,tx,ty)=mk(cp)
    print('scale m/px',math.hypot(a,b),'rot deg',math.degrees(math.atan2(b,a)))
    for n,x,y,la,lo in cp:
        p=sk2ll(x,y); print(' ',n,'resid m',round(math.hypot(*(np.array(xy(*p))-np.array(xy(la,lo))))))
    for n,x,y in [('barracks',1960,1430),('presb church',2385,1100),('junction',2255,645),('O Rall guns',2100,745),('G church alley W',2085,892),('G church alley E',2220,892),('G third E of Queen',2345,970),('G second E of Queen',2360,1148),
                  ('H Lossberg N',2575,665),('H Lossberg S',2545,820),('H Rall N',2525,860),('H Rall S',2485,1010),('H Knyp N',2505,1025),('H Knyp S',2590,1185),('K Loss a',2650,715),('K Loss b',2895,645),('K Rall a',2670,725),('K Rall b',2700,900),
                  ('I a N',2180,690),('I a S',2180,830),('I b N',2325,770),('I b S',2325,920),('L bar W',2640,1340),('L bar E',2770,1340),('M',2420,1365),('n',2215,895),('R1 N',2000,800),('R1 S',2000,970),('R2 N',2000,1040),('R2 S',2000,1220),
                  ('T e1 N',2392,890),('T e1 S',2392,1050),('T e2 N',2397,1090),('T e2 S',2397,1280),('X s W',2470,1205),('X s E',2770,1205),('X n W',2550,672),('X n E',2860,672),('S far N',2960,700),('S far S',2990,900),('Q south W',2550,1675),('Q south E',2700,1675)]:
        p=sk2ll(x,y); print(f'  {n:20s} {p[0]:.5f}, {p[1]:.5f}')
