import math, json, numpy as np
LAT0,LON0=39.8309,-77.2311
p=math.radians(LAT0)
MLAT=111132.92-559.82*math.cos(2*p)+1.175*math.cos(4*p)
MLON=111412.84*math.cos(p)-93.5*math.cos(3*p)
def ll2m(lat,lon): return ((lon-LON0)*MLON,(lat-LAT0)*MLAT)
def m2ll(e,n): return (LAT0+n/MLAT, LON0+e/MLON)
CP=[('Schmucker Hall (Lutheran Seminary)',3745,3433,39.83194,-77.24472),
    ('Pennsylvania Hall (Penn College)',4444,3168,39.83500,-77.23472),
    ('Lincoln Square centre',4680,3530,39.83090,-77.23110),
    ('Big Round Top summit',4203,7560,39.78625,-77.23919)]
# similarity: E = a*x - b*y + tx ; N = -(b*x + a*y) + ty   (image y down)
A=[];B=[]
for _,x,y,lat,lon in CP:
    e,n=ll2m(lat,lon)
    A.append([x,-y,1,0]); B.append(e)
    A.append([-y,-x,0,1]); B.append(n)
sol,res,rk,sv=np.linalg.lstsq(np.array(A,float),np.array(B,float),rcond=None)
a,b,tx,ty=sol
def px2ll(x,y):
    e=a*x-b*y+tx; n=-a*y-b*x+ty
    return m2ll(e,n)
def ll2px(lat,lon):
    e,n=ll2m(lat,lon); e-=tx; n-=ty
    # e = a x - b y ; n = -b x - a y
    det=-(a*a+b*b)
    x=(e*(-a)-(-b)*n)/det; y=(a*n-(-b)*e)/det
    return x,y
if __name__=='__main__':
    print('scale m/px',math.hypot(a,b),'rotation deg',math.degrees(math.atan2(b,a)))
    for name,x,y,lat,lon in CP:
        la,lo=px2ll(x,y); de=(lo-lon)*MLON; dn=(la-lat)*MLAT
        print(f'{name:38s} residual {math.hypot(de,dn):5.1f} m  (E {de:+.1f}, N {dn:+.1f})')
    for name,lat,lon in [('Buford memorial (pike at McPherson Ridge)',39.83795,-77.25165),('Archer tablet (Meredith Ave)',39.83488,-77.25465),('Calef tablet',39.83198,-77.25114),('Gamble tablet',39.8350,-77.2500),('Devin tablet',39.84512,-77.24670),('Davis tablet Reynolds Ave',39.8383,-77.2478),('150th PA marker ~300ft from McPherson barn',39.83687,-77.25223)]:
        print(name,[round(v) for v in ll2px(lat,lon)])
    print('Herr Tavern px (2484,2545) ->',px2ll(2484,2545))
    json.dump({'a':a,'b':b,'tx':tx,'ty':ty},open('fit.json','w'))
