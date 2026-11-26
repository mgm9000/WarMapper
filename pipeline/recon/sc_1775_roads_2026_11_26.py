"""Mouzon 1775 (S135): the 13 main roads traced again, 26 Nov 2026, after Morgan asked why roads broke off and took odd angles.

  python3 -I pipeline/recon/sc_1775_roads_2026_11_26.py CROP.jpg     updates the roads in pipeline/recon/sc_1775_traced.json

CROP is the Library of Congress IIIF region 0,3600,11800,8200 at width 5900 of service:gmd:gmd390:g3900:g3900:ar139404 (the half-resolution
crop Session 4 picked on). Session 4 picked each road by hand every 100-150 pixels (9-14 km) and drew straight lines between the picks. Here
each road is snapped to Mouzon's own engraving: he draws a road as two thin parallel lines, so the light gap between them is found (a grey
closing of the ink, less the ink) and the least-cost path is taken through it from one end of the road to the other, kept within 22 pixels
(about 2 km) of the hand-picked line. Two roads had hand picks on the wrong line and were picked again from gridded views of the scan
(sc_1775_road_picks_2026_11_26.json): the road from Ninety Six to the Congarees (the old picks followed the Saluda, which Mouzon also draws
double) and the last 10 km of the road from Charlotte into Camden (the old picks lay on Rocky Branch). Every road was then checked by eye on
overlays at 1:1 to 1:7. The result keeps a point every few pixels where the road bends (simplified to 1.2 px), so the bends are drawn.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import grey_closing, gaussian_filter, distance_transform_edt
from skimage.graph import route_through_array
from skimage.draw import line as dline
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
TRACED = os.path.join(HERE, 'sc_1775_traced.json')
PICKS = os.path.join(HERE, 'sc_1775_road_picks_2026_11_26.json')


def snap(g, picks, corr=22, close=7, pad=40):
    P = np.array(picks, float)
    X0 = int(max(0, P[:, 0].min() - pad)); Y0 = int(max(0, P[:, 1].min() - pad))
    X1 = int(min(g.shape[1] - 1, P[:, 0].max() + pad)); Y1 = int(min(g.shape[0] - 1, P[:, 1].max() + pad))
    w = g[Y0:Y1 + 1, X0:X1 + 1]; lo = np.percentile(w, 2); hi = np.percentile(w, 75); D = np.clip((hi - w) / (hi - lo + 1e-6), 0, 1)
    Dc = grey_closing(D, size=(close, close)); inter = np.clip(Dc - D, 0, 1) * (Dc > 0.35); inter = gaussian_filter(inter, 0.8)
    inter = np.clip(inter / (np.percentile(inter, 99.5) + 1e-6), 0, 1)          # the light gap between a road's two lines
    mask = np.ones(w.shape, bool)
    for a, b in zip(picks, picks[1:]):
        rr, cc = dline(int(a[1]) - Y0, int(a[0]) - X0, int(b[1]) - Y0, int(b[0]) - X0)
        ok = (rr >= 0) & (rr < w.shape[0]) & (cc >= 0) & (cc < w.shape[1]); mask[rr[ok], cc[ok]] = False
    dist = distance_transform_edt(mask)
    cost = 0.05 + (1 - inter) ** 3 + np.where(dist > corr, 5.0, 0.0) + 0.002 * dist   # outside the corridor: very dear
    def pre(pt, r=6):   # an end nudged onto the gap, within r pixels
        x, y = int(pt[0]) - X0, int(pt[1]) - Y0; a, b = max(0, y - r), max(0, x - r); win = cost[a:y + r + 1, b:x + r + 1]
        i = np.unravel_index(np.argmin(win), win.shape); return (a + i[0], b + i[1])
    p, _ = route_through_array(cost, pre(picks[0]), pre(picks[-1]), fully_connected=True, geometric=True)
    return [(c + X0, r + Y0) for r, c in p]


def rdp(pts, eps):
    if len(pts) < 3: return [list(map(float, p)) for p in pts]
    a = np.array(pts[0], float); b = np.array(pts[-1], float); ab = b - a; n = np.hypot(*ab) + 1e-9
    d = [abs(ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) / n for p in pts[1:-1]]; i = int(np.argmax(d)) + 1
    if d[i - 1] > eps: return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [list(map(float, pts[0])), list(map(float, pts[-1]))]


def smooth(pts, k=4):
    P = np.array(pts, float); out = P.copy()
    for i in range(len(P)): a, b = max(0, i - k), min(len(P), i + k + 1); out[i] = P[a:b].mean(0)
    out[0] = P[0]; out[-1] = P[-1]; return out.tolist()


def main(crop):
    g = np.asarray(Image.open(crop).convert('RGB'), dtype=np.float32).max(axis=2) / 255.0; g = gaussian_filter(g, 0.6)
    TR = json.load(open(TRACED)); OVR = json.load(open(PICKS))
    for k, f in TR.items():
        if f['kind'] != 'road': continue
        if k in OVR: f['picks'] = OVR[k]
        line = rdp(smooth(snap(g, f['picks'])), 1.2)
        f['line'] = [[round(x, 1), round(y, 1)] for x, y in line]; f['snapped'] = '2026-11-26'
        print(k, len(f['picks']), 'picks ->', len(f['line']), 'points')
    json.dump(TR, open(TRACED, 'w'))


if __name__ == '__main__':
    main(sys.argv[1])
