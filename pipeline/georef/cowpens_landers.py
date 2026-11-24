"""The Army War College's two sketches of the Cowpens (Lt. Col. H. L. Landers, April 1928; House Document 328, 70th Congress, plates
facing p. 78), fitted to the ground for the Cowpens playback.

  python3 -I cowpens_landers.py PLATE1.jpg PLATE2.jpg OUTDIR      (archive.org item historicalstatem00army, page images n96 and n98,
                                                                  saved by Morgan as historicalstatem00army_0099.jpg and _0101.jpg)

Plate 1 ("Battle of the Cowpens ... Roads are shown as at present ... Sketch made in April 1928") is drawn north up at 4 inches to
the mile: its bar gives 1 mile = 694 pixels of the page image, 2.32 m a pixel. Its main road is the 1928 highway on the bed of the
old road through the field, which the park keeps as its trace. So the plate is fitted to the trace like Bearss's plates
(cowpens_bearss.py): the centre line of its main road, picked from the page, matched to the trace by a rigid fit at the plate's own
scale, ignoring the plate's road beyond either end of the trace.
Plate 2 ("Battle Formation Shown in sketch") is a diagram of the lines on the same two roads, with a bar of its own. It is fitted the
same way, by its main road.
"""
import json, math, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline')); sys.path.insert(0, HERE)
import cowpens_geo as G
import cowpens_bearss as B

PLATE1_M_PER_PX = 1609.344 / 694
PLATE1_ROAD = [(135, 95), (240, 170), (300, 215), (355, 268), (390, 340), (420, 410), (455, 480), (490, 550), (520, 610), (560, 660),
               (620, 710), (700, 760), (800, 805), (900, 845), (985, 880), (1030, 905)]

PLATE2_M_PER_PX = 500 * 0.9144 / 687
PLATE2_ROAD = [(37, 98), (172, 490), (306, 784), (404, 1054), (502, 1250), (588, 1422), (735, 1593), (931, 1777), (1054, 1887)]


def dark_centre(g, poly, w=10):
    """Centre of the dark ink across the road at points every 4 px along the picked line: the middle of its two edges."""
    a = np.asarray(g, float); out = []
    P = [np.array(p, float) for p in poly]
    for p, q in zip(P, P[1:]):
        d = q - p; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
        for s in np.arange(0, L, 4):
            c = p + u * s; prof = []
            for k in range(-w, w + 1):
                x, y = (c + n * k).round().astype(int)
                prof.append(255 - a[y, x] if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] else 0)
            prof = np.array(prof); dk = np.nonzero(prof > 90)[0]
            if len(dk) >= 2: out.append(c + n * ((dk.min() + dk.max()) / 2 - w))
    return np.array(out)


def fit(pts, mpp, th0):
    dense, T = B.trace(); P = np.c_[pts[:, 0], -pts[:, 1]]; best = None
    for th in np.radians(np.arange(th0 - 15, th0 + 16, 3)):
        M0 = mpp * np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]); q = P @ M0.T
        u = (dense[0] - dense[-1]) / np.hypot(*(dense[0] - dense[-1]))
        for sh in np.linspace(-800, 800, 17):
            r = B.icp(P, M0, dense.mean(0) - q.mean(0) + u * sh, dense, T, final=20)
            if r is None: continue
            score = np.mean(np.minimum(r[2], 60)) - len(r[2]) * 0.01
            if best is None or score < best[0]: best = (score, r)
    return best[1]


def main(p1, p2, outdir):
    g = Image.open(p1).convert('L'); pts = dark_centre(g, PLATE1_ROAD)
    M, t, d, i = fit(pts, PLATE1_M_PER_PX, 0)
    W, H = g.size
    def ll(x, y): gx, gy = np.array([x, -y]) @ M.T + t; la, lo = G._ll(gx, gy); return [round(float(lo), 6), round(float(la), 6)]
    res = {'plate1': {'m_per_px': round(PLATE1_M_PER_PX, 3), 'turn_deg': round(math.degrees(math.atan2(M[1, 0], M[0, 0])), 2), 'M': M.tolist(), 't': t.tolist(),
                      'road_points': int(len(d)), 'mean_m': round(float(d.mean()), 1), 'median_m': round(float(np.median(d)), 1), 'p90_m': round(float(np.percentile(d, 90)), 1),
                      'corners': [ll(0, 0), ll(W, 0), ll(W, H), ll(0, H)]}}
    g2 = Image.open(p2).convert('L'); pts2 = dark_centre(g2, PLATE2_ROAD, 18)
    M2, t2, d2, _ = fit(pts2, PLATE2_M_PER_PX, 0); W2, H2 = g2.size
    def ll2(x, y): gx, gy = np.array([x, -y]) @ M2.T + t2; la, lo = G._ll(gx, gy); return [round(float(lo), 6), round(float(la), 6)]
    res['plate2'] = {'m_per_px': round(PLATE2_M_PER_PX, 4), 'turn_deg': round(math.degrees(math.atan2(M2[1, 0], M2[0, 0])), 2), 'M': M2.tolist(), 't': t2.tolist(),
                     'road_points': int(len(d2)), 'mean_m': round(float(d2.mean()), 1), 'median_m': round(float(np.median(d2)), 1), 'p90_m': round(float(np.percentile(d2, 90)), 1),
                     'corners': [ll2(0, 0), ll2(W2, 0), ll2(W2, H2), ll2(0, H2)]}
    for n, (gg, out) in {1: (g, 'landers-1928-1.webp'), 2: (g2, 'landers-1928-2.webp')}.items():
        Image.open(p1 if n == 1 else p2).convert('RGB').save(os.path.join(outdir, out), quality=70, method=6)
    json.dump(res, open(os.path.join(HERE, 'cowpens_landers_fit.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:4])
