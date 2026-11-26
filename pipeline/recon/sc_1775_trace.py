"""Mouzon 1775 (S135): snap sparse picks to the engraved line: least-cost path through dark pixels between consecutive picks (half-res Mouzon scan)."""
import numpy as np
from PIL import Image
from skimage.graph import route_through_array
from scipy.ndimage import gaussian_filter
Image.MAX_IMAGE_PIXELS=None
_G={};_GB={}
def gray(path):
    if path not in _G:
        g=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32).max(axis=2)/255.0
        _G[path]=gaussian_filter(g,0.8)
    return _G[path]
def presnap(g,p,r=14):
    x,y=int(p[0]),int(p[1]); y0,x0=max(0,y-r),max(0,x-r); w=g[y0:y+r+1,x0:x+r+1]
    yy,xx=np.mgrid[y0-y:y0-y+w.shape[0],x0-x:x0-x+w.shape[1]]; sc=w+0.004*np.hypot(xx,yy)
    i=np.unravel_index(np.argmin(sc),sc.shape); return (x0+i[1],y0+i[0])
def unloop(P,tol=2.5):
    out=[]
    for p in P:
        cut=None
        for j in range(max(0,len(out)-400),len(out)-3):
            if abs(out[j][0]-p[0])<=tol and abs(out[j][1]-p[1])<=tol: cut=j;break
        if cut is not None: out=out[:cut]
        out.append(p)
    return out
def snap(path,picks,pad=25,power=4,floor=0.03,r=14):
    g=gray(path); out=[]
    gb=_GB.setdefault(path,gaussian_filter(g,1.5)) if path in _GB else _GB.setdefault(path,gaussian_filter(g,1.5)); picks=[presnap(gb,p,r) for p in picks]
    for (x0,y0),(x1,y1) in zip(picks,picks[1:]):
        X0,X1=int(min(x0,x1))-pad,int(max(x0,x1))+pad; Y0,Y1=int(min(y0,y1))-pad,int(max(y0,y1))+pad
        X0,Y0=max(X0,0),max(Y0,0); X1,Y1=min(X1,g.shape[1]-1),min(Y1,g.shape[0]-1)
        w=g[Y0:Y1+1,X0:X1+1]; lo=np.percentile(w,3); hi=np.percentile(w,70)
        dark=np.clip((hi-w)/(hi-lo+1e-6),0,1)
        cost=floor+(1-dark)**power
        p,_=route_through_array(cost,(int(y0)-Y0,int(x0)-X0),(int(y1)-Y0,int(x1)-X0),fully_connected=True,geometric=True)
        seg=[(c+X0,r+Y0) for r,c in p]
        out.extend(seg if not out else seg[1:])
    return rdp(unloop(out),1.0)
def rdp(pts,eps):
    if len(pts)<3: return pts
    a=np.array(pts[0],float); b=np.array(pts[-1],float); ab=b-a; n=np.hypot(*ab)+1e-9
    d=[abs(ab[0]*(p[1]-a[1])-ab[1]*(p[0]-a[0]))/n for p in pts[1:-1]]
    i=int(np.argmax(d))+1
    if d[i-1]>eps: return rdp(pts[:i+1],eps)[:-1]+rdp(pts[i:],eps)
    return [pts[0],pts[-1]]
def overlay(path,lines,box,out,ow=1500,picks=None):
    from PIL import ImageDraw
    x0,y0,x1,y1=box; im=Image.open(path).crop(box).convert('RGB'); s=ow/(x1-x0); im=im.resize((ow,int((y1-y0)*s)))
    d=ImageDraw.Draw(im); cols=[(255,0,0),(0,90,255),(0,170,0),(200,0,200),(255,120,0),(0,170,170)]
    for i,(name,l) in enumerate(lines):
        c=cols[i%len(cols)]; P=[((x-x0)*s,(y-y0)*s) for x,y in l]
        if len(P)>1: d.line(P,fill=c,width=2)
        if P: d.text((P[0][0]+3,P[0][1]+3),name,fill=c)
    for (x,y) in (picks or []): d.ellipse([(x-x0)*s-3,(y-y0)*s-3,(x-x0)*s+3,(y-y0)*s+3],outline=(0,0,0))
    im.save(out,quality=85)
