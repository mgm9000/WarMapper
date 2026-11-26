import json,math
import os
NE=os.environ.get('NE_DIR','natural-earth')+'/'   # the GeoJSON files of github.com/nvkelso/natural-earth-vector (geojson/), downloaded
BOX=(-84.0,31.5,-78.0,35.6)
def _lines(g):
    if not g: return []
    return [g['coordinates']] if g['type']=='LineString' else g['coordinates']
def inb(c): return BOX[0]<=c[0]<=BOX[2] and BOX[1]<=c[1]<=BOX[3]
def rivers():
    R={}
    for f in ['ne_10m_rivers_north_america','ne_10m_rivers_lake_centerlines']:
        for ft in json.load(open(NE+f+'.geojson'))['features']:
            n=ft['properties'].get('name')
            for l in _lines(ft['geometry']):
                if any(inb(c) for c in l): R.setdefault(n,[]).append([tuple(c[:2]) for c in l])
    return R
def coast():
    out=[]
    for ft in json.load(open(NE+'ne_10m_coastline.geojson'))['features']:
        for l in _lines(ft['geometry']):
            if any(inb(c) for c in l): out.append([tuple(c[:2]) for c in l])
    return out
def borders():
    out=[]
    for ft in json.load(open(NE+'ne_10m_admin_1_states_provinces_lines.geojson'))['features']:
        p=ft['properties']; nm=' '.join(str(v) for v in p.values() if isinstance(v,str))
        for l in _lines(ft['geometry']):
            if any(inb(c) for c in l): out.append((nm,[tuple(c[:2]) for c in l]))
    return out
K=(111.32*math.cos(math.radians(33.5)),110.9)
def xy(ll): return ((ll[0]+81.0)*K[0],(ll[1]-33.5)*K[1])
def ll(p): return (p[0]/K[0]-81.0,p[1]/K[1]+33.5)
def nearest(p,lines):
    """p in km xy; lines lists of lonlat; returns (dist,point_xy)"""
    best=(1e9,None)
    for l in lines:
        q=[xy(c) for c in l]
        for a,b in zip(q,q[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy+1e-12)))
            x,y=a[0]+t*dx,a[1]+t*dy; d=math.hypot(p[0]-x,p[1]-y)
            if d<best[0]: best=(d,(x,y))
    return best
