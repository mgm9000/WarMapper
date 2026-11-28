"""Mouzon 1775 resampled onto the ground (Web Mercator) for the map details, both Carolinas (SC storyline Session 2, 27 Nov 2026).

  python3 -I pipeline/georef/carolinas_mouzon_picture_2026_11_27.py NORTH.jpg SC.jpg EAST.jpg

The three pictures are those pipeline/recon/nc_1775_trace_2026_11_27.py names (Library of Congress IIIF regions of g3900.ar139404 at half
resolution). Writes playbacks/sc-orientation/mouzon-1775-fitted.webp over the sheet of data/recon/sc-1775.geojson, with the fit of
pipeline/georef/sc_mouzon_fit.json (each mounted section inverted on its own, as pipeline/georef/sc_mouzon_picture.py did for South Carolina).
"""
import json, math, os, sys
import numpy as np
from scipy.interpolate import RBFInterpolator, RegularGridInterpolator
from scipy.ndimage import map_coordinates
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIT = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'sc_mouzon_fit.json')))
SY, SX = FIT['seam']['y'], FIT['seam']['x']; KX, KY = 92.83, 110.9; OY = 1800


def panel(x, y): return ('U' if y < SY else 'L') + ('L' if x < SX else 'R')


def main(north, sc, east, width=5000):
    P = FIT['pairs']; INV = {}
    for pn in ['UL', 'UR', 'LL', 'LR']:
        sel = [p for p in P if panel(*p[0]) == pn]
        INV[pn] = RBFInterpolator(np.array([p[1] for p in sel]), np.array([p[0] for p in sel], float), kernel='thin_plate_spline',
                                  smoothing=FIT.get('smoothing', {}).get(pn, 8.0) * np.array([p[2] for p in sel]) ** 2, degree=1, neighbors=400)
    W, S, E, N = json.load(open(os.path.join(ROOT, 'data', 'recon', 'sc-1775.geojson')))['sheet']; N = min(N, 36.75)   # Mouzon's part of the sheet (north of it, Fry and Jefferson)
    my = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    w = width; h = int(round(w * (my(N) - my(S)) / math.radians(E - W))); print('size', w, h)
    step = 16; gx = np.arange(0, w + step, step); gy = np.arange(0, h + step, step)
    lon = W + (E - W) * gx / w; mys = my(N) - (my(N) - my(S)) * gy / h; lat = np.degrees(2 * np.arctan(np.exp(mys)) - math.pi / 2)
    LO, LA = np.meshgrid(lon, lat); G = np.c_[((LO + 81.0) * KX).ravel(), ((LA - 33.5) * KY).ravel()]
    best = np.full((G.shape[0], 2), np.nan)
    for pn, f in INV.items():
        m = f(G); ok = np.array([panel(x, y) == pn for x, y in m]) & np.isnan(best[:, 0]); best[ok] = m[ok]
    mx = best[:, 0].reshape(LO.shape); myy = best[:, 1].reshape(LO.shape) + OY        # canvas rows
    fx = RegularGridInterpolator((gy, gx), np.nan_to_num(mx, nan=-1e4), bounds_error=False, fill_value=-1e4)
    fy = RegularGridInterpolator((gy, gx), np.nan_to_num(myy, nan=-1e4), bounds_error=False, fill_value=-1e4)
    c = Image.new('RGB', (8456, OY + 4100), (255, 255, 255))
    c.paste(Image.open(north).convert('RGB'), (0, 0)); c.paste(Image.open(sc).convert('RGB'), (0, OY)); c.paste(Image.open(east).convert('RGB'), (5900, OY))
    src = np.asarray(c); out = np.zeros((h, w, 4), np.uint8)
    for r0 in range(0, h, 512):   # in strips, to keep memory down
        yy, xx = np.mgrid[r0:min(h, r0 + 512), 0:w]; pts = np.c_[yy.ravel(), xx.ravel()]
        X = fx(pts).reshape(yy.shape); Y = fy(pts).reshape(yy.shape)
        for k in range(3): out[r0:r0 + yy.shape[0], :, k] = map_coordinates(src[..., k], [Y, X], order=1, cval=255)
        inset = ((X > 5600) & (Y - OY > 2440)) | ((X >= 5900) & (Y - OY >= 2200))    # beyond the east strip downloaded, and Mouzon's two harbour insets (Port Royal, Charleston), in the sea off North Carolina on the sheet: not drawn
        out[r0:r0 + yy.shape[0], :, 3] = np.where((X >= 0) & (Y >= 0) & (X < src.shape[1] - 1) & (Y < src.shape[0] - 1) & ~inset, 255, 0)
    f = os.path.join(ROOT, 'playbacks', 'sc-orientation', 'mouzon-1775-fitted.webp')
    Image.fromarray(out, 'RGBA').save(f, quality=70, method=6)
    print(json.dumps({'corners': [[W, N], [E, N], [E, S], [W, S]], 'size': [w, h], 'bytes': os.path.getsize(f)}))


if __name__ == '__main__':
    main(*sys.argv[1:4])
