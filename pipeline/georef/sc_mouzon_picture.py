"""Mouzon 1775 resampled onto the ground (Web Mercator) for the map details: python3 -I pipeline/georef/sc_mouzon_picture.py CROP.jpg, where CROP is the
Library of Congress IIIF region 0,3600,11800,8200 at width 5900 of service:gmd:gmd390:g3900:g3900:ar139404. Writes playbacks/sc-orientation/mouzon-1775-fitted.webp."""
import json,math,os,sys,numpy as np
from scipy.interpolate import RBFInterpolator, RegularGridInterpolator
from scipy.ndimage import map_coordinates
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
FIT=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sc_mouzon_fit.json')))
SY,SX=FIT['seam']['y'],FIT['seam']['x']; KX,KY=111.32*math.cos(math.radians(33.5)),110.9
def panel(x,y): return ('U' if y<SY else 'L')+('L' if x<SX else 'R')
P=FIT['pairs']; INV={}
for pn in ['UL','UR','LL','LR']:
    sel=[p for p in P if panel(*p[0])==pn]
    INV[pn]=RBFInterpolator(np.array([p[1] for p in sel]),np.array([p[0] for p in sel],float),kernel='thin_plate_spline',smoothing=8.0*np.array([p[2] for p in sel])**2,degree=1)
W,S,E,N=-83.45,31.95,-78.45,35.3
def my(lat): return math.log(math.tan(math.pi/4+math.radians(lat)/2))
w=4096; h=int(round(w*(my(N)-my(S))/math.radians(E-W))); print('size',w,h)
step=16; gx=np.arange(0,w+step,step); gy=np.arange(0,h+step,step)
lon=W+(E-W)*gx/w; mys=my(N)-(my(N)-my(S))*gy/h; lat=np.degrees(2*np.arctan(np.exp(mys))-math.pi/2)
LO,LA=np.meshgrid(lon,lat); G=np.c_[((LO+81.0)*KX).ravel(),((LA-33.5)*KY).ravel()]
best=np.full((G.shape[0],2),np.nan)
for pn,f in INV.items():
    m=f(G); ok=np.array([panel(x,y)==pn for x,y in m])&np.isnan(best[:,0]); best[ok]=m[ok]
mx=best[:,0].reshape(LO.shape); myy=best[:,1].reshape(LO.shape)
yy,xx=np.mgrid[0:h,0:w]
fx=RegularGridInterpolator((gy,gx),np.nan_to_num(mx,nan=-1e4),bounds_error=False,fill_value=-1e4)
fy=RegularGridInterpolator((gy,gx),np.nan_to_num(myy,nan=-1e4),bounds_error=False,fill_value=-1e4)
pts=np.c_[yy.ravel(),xx.ravel()]; X=fx(pts).reshape(h,w); Y=fy(pts).reshape(h,w)
src=np.asarray(Image.open(sys.argv[1]).convert('RGB'))
out=np.zeros((h,w,4),np.uint8)
for c in range(3): out[...,c]=map_coordinates(src[...,c],[Y,X],order=1,cval=255)
inside=(X>=0)&(Y>=0)&(X<src.shape[1]-1)&(Y<src.shape[0]-1)
out[...,3]=np.where(inside,255,0)
pass
Image.fromarray(out,'RGBA').save(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),'playbacks','sc-orientation','mouzon-1775-fitted.webp'),quality=72,method=6)
print(json.dumps({'corners':[[W,N],[E,N],[E,S],[W,S]],'size':[w,h]}))
