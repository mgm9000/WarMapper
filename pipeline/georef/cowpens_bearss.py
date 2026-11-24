"""Bearss's four troop-movement maps of the Cowpens (1967), fitted to the ground for the Cowpens playback.

  python3 -I cowpens_bearss.py PDF OUTDIR        PDF: Bearss, The Battle of Cowpens (NPS, 1967), 39 pages, Morgan's copy
                                                 (Historical Info/History 340/battle-of-cowpens.pdf). Writes OUTDIR/bearss-plate-<n>.webp
                                                 and pipeline/georef/cowpens_bearss_fit.json, and prints the fit.

The plates (PDF pages 17, 26, 29, 30: Plates I to IV) are drawn on one surveyed base: contours, the roads, nothing else. The scale bar
reads 1,125 feet = 299.5 pixels at 300 dpi, so 1.145 m a pixel, and the four plates share it.

How Plate I was tied to the ground.
  1. Bearss's roads are solid double lines and his contours dashed, so a program keeps the long solid marks inside the frame, closes each
     double line into a band and thins it to a centre line.
  2. The road Bearss calls the Mill Gap road is the road the park keeps as the Historic Green River Road: Bearss puts Morgan's camp "near
     the intersection of the Mill Gap road and the road from present day Spartanburg ... crossing Broad River at Island Ford" (p. 8), and
     the park's trace runs from where Tarleton came onto the field to SC 11, past that crossing. So the plate's Mill Gap road (from the
     lower-left edge to the crossing, then on towards Island Ford) is matched to the trace as OpenStreetMap draws it (data/osm/cowpens.txt):
     a rigid fit (turn and shift; the scale is the plate's own bar), iterated closest points, ignoring the plate's road where it runs on
     past either end of the trace.
  3. Checked by fitting to each half of the trace in turn and measuring the other half, and by today's streams, which were not used:
     the head of the stream east of the park road falls in Bearss's camp ravine.
Plates II to IV were registered to Plate I by their contours (an affine fit of the blurred pages, by correlation): the base map is the
same on all four, and they differ from Plate I only by how each page lies in the scan (30 to 70 m).

The roads and corridor picks below are pixels of Plate I at 300 dpi.
"""
import json, math, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import cowpens_geo as G

PAGES = {1: 17, 2: 26, 3: 29, 4: 30}                     # plate -> PDF page
FRAME = {1: (156, 256, 3124, 2246), 2: (158, 229, 3129, 2222), 3: (163, 209, 3135, 2204), 4: (143, 194, 3118, 2186)}   # the neat line
LEGEND = (1940, 1600, 3124, 2246)                         # Plate I's legend box, left out of the road search
M_PER_PX = 1125 * 0.3048 / 299.5                          # the scale bar: 1,125 feet over 299.5 pixels
# rough lines along each road of Plate I, to pick its centre-line pixels out of everything else that is long and solid
MILL_GAP = [(384, 1772), (533, 1612), (789, 1357), (959, 1165), (1257, 910), (1427, 793), (1704, 718), (1959, 654), (2098, 644)]
MILL_GAP_IN = [(1959, 650), (2050, 640), (2150, 645), (2250, 660), (2330, 680), (2390, 705)]             # on through Morgan's line to the crossing
SHARED = [(2390, 705), (2500, 760), (2600, 805), (2700, 850), (2800, 890), (2880, 912), (2910, 920)]   # the crossing to the fork: both roads
TO_MILL_GAP = [(2910, 917), (3000, 900), (3110, 880)]
TO_ISLAND_FORD = [(2915, 925), (2990, 980), (3050, 1030), (3095, 1072)]
TO_PACOLET = [(2035, 265), (2080, 360), (2130, 440), (2180, 510), (2240, 570), (2290, 620), (2350, 670), (2390, 700)]
ROADS_TRACED = {'mill-gap': MILL_GAP + MILL_GAP_IN[1:], 'shared': SHARED, 'to-mill-gap': TO_MILL_GAP, 'to-island-ford': TO_ISLAND_FORD, 'to-pacolet': TO_PACOLET}


def render(pdf, page, dpi=300):
    d = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(dpi), '-png', pdf, os.path.join(d, 'p')], check=True)
    return Image.open(os.path.join(d, os.listdir(d)[0])).convert('L')


def road_pixels(g):
    """Centre lines of Bearss's solid lines (roads and the long strokes of symbols) on Plate I, as an array of [x, y] pixels."""
    from scipy import ndimage as nd
    from skimage.morphology import skeletonize, closing, disk
    a = np.asarray(g) < 140; x0, y0, x1, y1 = FRAME[1]
    m = np.zeros_like(a); m[y0 + 8:y1 - 8, x0 + 8:x1 - 8] = True; a &= m
    lx0, ly0, lx1, ly1 = LEGEND; a[ly0 - 8:ly1 + 8, lx0 - 8:lx1 + 8] = False
    lab, _ = nd.label(a, structure=np.ones((3, 3))); keep = np.zeros_like(a)
    for i, s in enumerate(nd.find_objects(lab)):
        if max(s[0].stop - s[0].start, s[1].stop - s[1].start) > 250: keep |= lab == i + 1
    sk = skeletonize(nd.binary_fill_holes(closing(keep, disk(9))))
    ys, xs = np.nonzero(sk); return np.c_[xs, ys].astype(float)


def corridor(pts, poly, w=10):
    out = np.zeros(len(pts), bool)
    for a, b in zip(poly, poly[1:]):
        a, b = np.array(a, float), np.array(b, float); d = b - a
        t = np.clip(((pts - a) @ d) / (d @ d), 0, 1); out |= np.hypot(*(pts - (a + t[:, None] * d)).T) < w
    return pts[out]


def trace():
    from scipy.spatial import cKDTree
    tr = np.array([G._xy(p) for p in G.ROAD]); dense = []
    for a, b in zip(tr, tr[1:]):
        n = int(np.hypot(*(b - a))) + 1; dense += [a + (b - a) * k / n for k in range(n)]
    dense = np.array(dense); return dense, cKDTree(dense)


def rigid(A, B):
    ma, mb = A.mean(0), B.mean(0); U, S, Vt = np.linalg.svd((A - ma).T @ (B - mb))
    D = np.diag([1, np.sign(np.linalg.det(Vt.T @ U.T))]); R = Vt.T @ D @ U.T; return R, mb - R @ ma


def icp(P, M, t, dense, T, iters=80, final=25):
    """P: plate pixels as (x, -y). Returns M (2x2: turn and scale), t, and the distances of the matched points."""
    for it in range(iters):
        q = P @ M.T + t; d, i = T.query(q); k = (i > 3) & (i < len(dense) - 4) & (d < max(final, 120 - it * 3))
        if k.sum() < 50: return None
        R, tt = rigid(q[k], dense[i[k]]); M = R @ M; t = R @ t + tt
    q = P @ M.T + t; d, i = T.query(q); k = (i > 3) & (i < len(dense) - 4)
    return M, t, d[k], i[k]


def fit_plate1(g):
    sk = road_pixels(g); path = np.vstack([corridor(sk, MILL_GAP + MILL_GAP_IN[1:], 12), corridor(sk, SHARED, 12)])
    dense, T = trace(); P = np.c_[path[:, 0], -path[:, 1]]; best = None
    for th in np.radians(np.arange(115, 160, 3)):
        M0 = M_PER_PX * np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]); q = P @ M0.T
        u = (dense[0] - dense[-1]) / np.hypot(*(dense[0] - dense[-1]))
        for sh in np.linspace(-600, 600, 13):
            r = icp(P, M0, dense.mean(0) - q.mean(0) + u * sh, dense, T)
            if r is None: continue
            score = np.mean(np.minimum(r[2], 60)) - len(r[2]) * 0.01
            if best is None or score < best[0]: best = (score, r)
    M, t, d, i = best[1]
    # check: fit to each half of the trace, measure the other
    cum = np.r_[0, np.cumsum(np.hypot(*np.diff(dense, axis=0).T))]; q = P @ M.T + t; dd, ii = T.query(q); kk = (ii > 3) & (ii < len(dense) - 4)
    checks = []
    for lo, hi in ((0, 1100), (1100, 2400)):
        tr = kk & (cum[ii] >= lo) & (cum[ii] < hi); te = kk & ~tr
        Mi, ti = M.copy(), t.copy()
        for _ in range(60):
            qq = P[tr] @ Mi.T + ti; d2, i2 = T.query(qq); k2 = (i2 > 3) & (i2 < len(dense) - 4) & (d2 < 40)
            R, tt = rigid(qq[k2], dense[i2[k2]]); Mi = R @ Mi; ti = R @ ti + tt
        dt, _ = T.query(P[te] @ Mi.T + ti)
        moved = max(np.hypot(*((np.array([x, -y]) @ Mi.T + ti) - (np.array([x, -y]) @ M.T + t))) for x, y in ((2390, 705), (1700, 705), (2250, 960)))
        checks.append({'fit_on_m': [lo, hi], 'other_half_mean_m': round(float(dt.mean()), 1), 'other_half_p90_m': round(float(np.percentile(dt, 90)), 1),
                       'largest_shift_of_crossing_camp_british_line_m': round(float(moved), 0)})
    return M, t, d, checks, sk


def register(A, B):
    """The affine warp that takes Plate I pixels to the same ground on another plate, from their blurred contours."""
    import cv2
    def prep(g): a = 255 - np.asarray(g, np.uint8); a = cv2.GaussianBlur(a, (0, 0), 8); return cv2.resize(a.astype(np.float32) / 255, None, fx=0.2, fy=0.2)
    a, b = prep(A), prep(B); best = None
    for dx in (-20, 0, 20):
        for dy in (-20, 0, 20):
            W = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
            try: cc, W = cv2.findTransformECC(a, b, W, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 150, 1e-5), None, 3)
            except cv2.error: continue
            if best is None or cc > best[0]: best = (cc, W.copy())
    cc, W = best; W[:, 2] /= 0.2; return cc, W


def to_ll(M, t, x, y):
    gx, gy = np.array([x, -y]) @ M.T + t; la, lo = G._ll(gx, gy); return [round(lo, 6), round(la, 6)]


def main(pdf, outdir):
    plates = {n: render(pdf, p) for n, p in PAGES.items()}
    M, t, d, checks, sk = fit_plate1(plates[1])
    fit = {'made': '2026-11-24', 'm_per_px': round(M_PER_PX, 4), 'turn_deg': round(math.degrees(math.atan2(M[1, 0], M[0, 0])) % 360, 2),
           'plate1_to_ground': {'M': M.tolist(), 't': t.tolist(), 'units': 'plate pixels (x, -y) at 300 dpi -> metres (KX*lon, KY*lat) of cowpens_geo'},
           'road_match': {'points': int(len(d)), 'mean_m': round(float(d.mean()), 1), 'median_m': round(float(np.median(d)), 1), 'p90_m': round(float(np.percentile(d, 90)), 1)},
           'checks': checks, 'plates': {}}
    for n, g in plates.items():
        if n == 1: Wi = np.array([[1, 0, 0], [0, 1, 0]], float); cc = 1.0
        else:
            cc, W = register(plates[1], g); A = np.vstack([W, [0, 0, 1]]); Wi = np.linalg.inv(A)[:2]   # plate n -> Plate I pixels
        x0, y0, x1, y1 = FRAME[n]; x0 -= 6; y0 -= 6; x1 += 6; y1 += 6
        def c(x, y): p = Wi @ [x, y, 1]; return to_ll(M, t, p[0], p[1])
        fit['plates'][n] = {'page': PAGES[n], 'match_to_plate_1': round(float(cc), 3), 'to_plate_1': Wi.tolist(), 'crop': [x0, y0, x1, y1],
                            'corners': [c(x0, y0), c(x1, y0), c(x1, y1), c(x0, y1)]}
        g.crop((x0, y0, x1, y1)).save(os.path.join(outdir, 'bearss-plate-%d.webp' % n), quality=72, method=6)
    # Bearss's roads on the ground, for the reconstruction (pipeline/recon/cowpens_1781.py)
    roads = {}
    for k, poly in ROADS_TRACED.items():
        # the program's centre line where it found one; the hand picks where lettering or a symbol broke the road
        P = np.array(poly, float); seg = np.cumsum(np.r_[0, np.hypot(*np.diff(P, axis=0).T)])
        def param(q):
            best = (1e9, 0)
            for j in range(len(P) - 1):
                d = P[j + 1] - P[j]; u = np.clip((q - P[j]) @ d / (d @ d), 0, 1); e = np.hypot(*(q - P[j] - u * d))
                if e < best[0]: best = (e, seg[j] + u * np.hypot(*d))
            return best[1]
        sk_pts = corridor(sk, poly, 12); have = sorted(param(q) for q in sk_pts)
        pts = [(param(q), q) for q in sk_pts]
        for j, q in enumerate(P):
            if not have or min(abs(seg[j] - h) for h in have) > 20: pts.append((seg[j], q))
        pts.sort(key=lambda r: r[0]); step = []
        for _, q in pts:
            if not step or np.hypot(*(q - step[-1])) >= 9: step.append(q)
        roads[k] = [to_ll(M, t, x, y) for x, y in step]
    fit['roads'] = roads
    json.dump(fit, open(os.path.join(HERE, 'cowpens_bearss_fit.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in fit.items() if k not in ('roads', 'plates')}, indent=1))
    for n, p in fit['plates'].items(): print('plate', n, 'match', p['match_to_plate_1'], p['corners'])


if __name__ == '__main__':
    main(*sys.argv[1:3])
