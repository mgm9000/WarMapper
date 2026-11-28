"""Fry and Jefferson (S152), southern Virginia, fitted to the ground (SC storyline Session 2, 27 Nov 2026).

  NE_DIR=natural-earth python3 -I pipeline/georef/va_fry_jefferson_fit_2026_11_27.py     writes pipeline/georef/va_fry_jefferson_fit.json

Morgan, 27 Nov 2026: a Virginia map above Mouzon's edge, "add it". Fry and Jefferson's map of Virginia (drawn 1751; the Library of Congress
copy used is a printing of 1755, g3880.ct000370) is fitted by one thin-plate spline with a plane (not section by section: there are too
few known places in each section of the mounted copy), from
  - CONTROLS: Richmond (St. John's Church), Petersburg (Blandford Church) and City Point, at their sites (NRHP coordinates), 1.5 km;
  - TIES to the Mouzon reconstruction, so that the two maps meet where they overlap: the Occoneachey Islands (where the Staunton meets the
    Dan) and Lower Saura Town, each at the point of the ground where the fitted Mouzon puts it (sc_mouzon_fit.json), 2 km;
  - the Staunton (Natural Earth's Roanoke), the Meherrin and the Nottoway matched to today's rivers, and Fry and Jefferson's dividing line
    to today's state line, seven times over (as sc_mouzon_fit.py), 6 km. Pairs on Smith Mountain, Leesville, Kerr and Gaston lakes dropped.
Natural Earth has no James or Appomattox here, so the north-east is held by the three controls alone.
"""
import json, math, os, sys
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'recon'))
TR = json.load(open(os.path.join(ROOT, 'pipeline', 'recon', 'va_fry_jefferson_traced.json')))
OUT = os.path.join(HERE, 'va_fry_jefferson_fit.json')
NE = os.environ.get('NE_DIR', 'natural-earth') + '/'
KX, KY = 92.83, 110.9
SD = float(os.environ.get('VA_SD', '14'))   # km: the river and line pairs. 6 and 10 left folds on the Staunton at the Blue Ridge and on the lower Meherrin; 18 lost the upper Staunton's match
def xy(ll): return ((ll[0] + 81.0) * KX, (ll[1] - 33.5) * KY)
def ll(p): return (p[0] / KX - 81.0, p[1] / KY + 33.5)
CONTROLS = [('Richmond (St. John\'s Church)', (3236, 152), (-77.41972, 37.53139), 1.5, 'St. John\'s Church, NRHP 66000920'),
            ('Petersburg (Blandford Church)', (3244, 450), (-77.38778, 37.22583), 1.5, 'Blandford Church, NRHP 72001513'),
            ('City Point (the James and the Appomattox meet)', (3440, 418), (-77.277222, 37.316806), 1.5, 'Appomattox Manor, NRHP 69000015')]
TIES = [('Occoneachey Islands (the Staunton meets the Dan)', (2268, 1100), (5143, -1722), 2.0), ('Lower Saura Town', (1418, 1297), (4262, -1495), 2.0)]
MATCH = {'riv-staunton': ['Roanoke'], 'riv-meherrin': ['Meherrin'], 'riv-nottoway': ['Nottoway'], 'bnd-va-nc': 'STATE'}
RES = {'Smith Mountain': (-79.80, -79.40, 36.95, 37.20), 'Leesville': (-79.45, -79.30, 37.00, 37.12), 'Kerr': (-78.80, -78.20, 36.45, 36.72), 'Gaston': (-78.20, -77.75, 36.45, 36.62)}


def lines(f, keep):
    out = []
    for ft in json.load(open(NE + f + '.geojson'))['features']:
        g = ft['geometry']
        if not g or not keep(ft['properties']): continue
        for l in ([g['coordinates']] if g['type'] == 'LineString' else g['coordinates']):
            if any(-81.5 < c[0] < -76.5 and 36.3 < c[1] < 37.9 for c in l): out.append([tuple(c[:2]) for c in l])
    return out


def targets():
    T = {}
    for k, v in MATCH.items():
        if v == 'STATE':
            T[k] = lines('ne_10m_admin_1_states_provinces_lines', lambda p: (lambda s: 'Virginia' in s and 'North Carolina' in s)(' '.join(str(x) for x in p.values() if isinstance(x, str))))
        else:
            T[k] = [l for f in ('ne_10m_rivers_north_america', 'ne_10m_rivers_lake_centerlines') for l in lines(f, lambda p: p.get('name') in v)]
    return T


def seg_tree(L):
    A, B = [], []
    for l in L:
        q = [xy(c) for c in l]
        for a, b in zip(q, q[1:]): A.append(a); B.append(b)
    A, B = np.array(A), np.array(B); return A, B, cKDTree((A + B) / 2)


def nearest(p, T):
    A, B, tr = T; best = (1e9, None)
    for i in np.atleast_1d(tr.query(p, k=min(40, len(A)))[1]):
        a, b = A[i], B[i]; d = b - a; t = max(0, min(1, np.dot(np.array(p) - a, d) / (np.dot(d, d) + 1e-12))); q = a + t * d; dd = np.hypot(*(np.array(p) - q))
        if dd < best[0]: best = (dd, q)
    return best


def inres(g):
    lo, la = ll(g); return any(a <= lo <= b and c <= la <= d for a, b, c, d in RES.values())


def model(P, smooth=20.0):
    X = np.array([p[0] for p in P], float); Y = np.array([p[1] for p in P], float); W = np.array([p[2] for p in P])
    return RBFInterpolator(X, Y, kernel='thin_plate_spline', smoothing=W ** 2 * smooth, degree=1)


def samples(step=10):
    out = []
    for fid in MATCH:
        pts = TR[fid]['line']; acc = 0
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L / step))
            for j in range(1, n + 1):
                acc += L / n
                if acc >= step: acc = 0; out.append((fid, (a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n)))
    return out


def main():
    import sc_1775 as RC   # the fitted Mouzon, for the ties
    base = [[list(map(float, v)), list(xy(g)), sd] for _, v, g, sd, _ in CONTROLS]
    ties = []
    for nm, v, m, sd in TIES:
        g = RC.ground([m])[0]; ties.append((nm, v, g)); base.append([list(map(float, v)), list(xy(g)), sd])
    Tg = {k: seg_tree(v) for k, v in targets().items()}
    M = model(base, 50.0); S = samples()
    for it, lim in enumerate([30, 20, 14, 10, 8, 7, 6]):
        P = M(np.array([s[1] for s in S])); pairs = []
        for (fid, v), p in zip(S, P):
            d, q = nearest(p, Tg[fid])
            if d < lim and not inres(q): pairs.append([list(map(float, v)), [round(float(q[0]), 4), round(float(q[1]), 4)], SD])
        M = model(base + pairs)
        print('iter', it, 'pairs', len(pairs))
    full = base + pairs
    # how well it holds, and what each control gives when left out
    res = {}
    for i, (nm, v, *_rest) in enumerate([(c[0], c[1]) for c in CONTROLS] + [(t[0], t[1]) for t in ties]):
        g = np.array(full[i][1]); e = float(np.hypot(*(M(np.array([v], float))[0] - g)))
        M2 = model([p for j, p in enumerate(full) if j != i]); l = float(np.hypot(*(M2(np.array([v], float))[0] - g)))
        res[nm] = {'held_km': round(e, 2), 'left_out_km': round(l, 1)}; print('%-50s held %.2f km, left out %.1f km' % (nm, e, l))
    for k in MATCH:
        G = M(np.array(TR[k]['line'][::3], float)); ds = [nearest(g, Tg[k])[0] for g in G if not inres(nearest(g, Tg[k])[1])]
        print('%-14s to today: median %.2f km, 90%% %.1f km' % (k, np.median(ds), np.percentile(ds, 90)))
    # folds along the traced lines
    nf = 0
    for k, v in TR.items():
        for p in v['line'][::3]:
            p = np.array(p, float); a = M(np.array([p, p + [2, 0], p + [0, 2]])); J = np.array([a[1] - a[0], a[2] - a[0]]).T
            if np.linalg.det(J) >= 0: nf += 1
    print('points on folded ground:', nf)
    json.dump({'note': 'Fry and Jefferson (S152) fitted to the ground; see pipeline/georef/va_fry_jefferson_fit_2026_11_27.py. V: pixel of the half-resolution strip (full x = 2000 + 2x, y = 5400 + 2y); g: km east and north of 81 W, 33.5 N.',
               'smoothing': 20.0, 'pairs': full, 'controls': [{'name': c[0], 'v': list(c[1]), 'lonlat': list(c[2]), 'sd_km': c[3], 'source': c[4]} for c in CONTROLS],
               'ties': [{'name': t[0], 'v': list(t[1]), 'lonlat': [round(x, 6) for x in t[2]], 'source': 'the fitted Mouzon (sc-1775)'} for t in ties], 'result': res}, open(OUT, 'w'))


if __name__ == '__main__':
    main()
