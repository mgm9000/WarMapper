"""South Carolina, 1775-1781: the reconstructed base map's features, to data/recon/sc-1775.geojson (Session 4 of claude/sc-orientation-prompt.md).

  python3 -I pipeline/recon/sc_1775.py        writes data/recon/sc-1775.geojson and prints what it wrote

What this is. A WarMapper reconstruction, not a period map: the rivers, the sea coast, the main roads and the boundary lines of Henry
Mouzon's "An accurate map of North and South Carolina with their Indian frontiers" (London, Sayer and Bennett, 1775; Library of Congress,
g3900.ar139404, public domain, S135), laid on today's ground. A pilot: the whole state at the level of its main lines, for Morgan to judge
the look before the rest is traced (25 Nov 2026).

How it was read (pipeline/recon/sc_1775_picks.py, sc_1775_traced.json). Points were picked by hand every 50-100 pixels on a half-resolution
crop of the scan (full scan x = 2 * crop x, y = 3600 + 2 * crop y), from gridded views. Rivers and the coast were then snapped by program to
the engraved line (pipeline/recon/sc_1775_trace.py: the least-cost path through the dark ink between two picks) and the result checked by eye
on overlays. Roads and boundary lines keep the hand picks (Mouzon draws roads as faint double lines, which the snapping does not follow well).

How it was laid on the ground (pipeline/georef/sc_mouzon_fit.py, sc_mouzon_fit.json). The scan is of a map cut into sections and mounted on
cloth; the sections are fitted one by one (above and below the gap at crop y 1222, left and right of the seam at crop x 4232), each by a
thin-plate spline with a plane, from 14 point controls (Ninety Six, Fort Charlotte, Monck's Corner and Fort Johnson as the workbook places
them; Esseneca, loosely; the meeting of rivers, the river mouths and the North Carolina line at the sea from Natural Earth, S136) and from
matching Mouzon's rivers, coast and North Carolina line to the same river, coast or state line in Natural Earth, seven times over.
Rivers keep their beds at this scale (the reservoirs of the 20th century aside), and the state line follows the lines of 1735-72.
Left out in turn, a point control is found again 0.1-4.4 km from where it belongs (median 1.1 km); in the far north-west, where Mouzon has
little to fit to, 26 km (Esseneca). So: rivers and coast good to about 1-2 km where Natural Earth has the river, roads to about 3-5 km, and
the Cherokee country in the north-west to no better than 10 km.
"""
import json, math, os, sys
import numpy as np
from scipy.interpolate import RBFInterpolator

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
TR = json.load(open(os.path.join(HERE, 'sc_1775_traced.json')))
FIT = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'sc_mouzon_fit.json')))
OUT = os.path.join(ROOT, 'data', 'recon', 'sc-1775.geojson')
SHEET = [-83.45, 31.95, -78.45, 35.3]          # west, south, east, north
SY, SX = FIT['seam']['y'], FIT['seam']['x']
KX, KY = 111.32 * math.cos(math.radians(33.5)), 110.9


def panel(x, y): return ('U' if y < SY else 'L') + ('L' if x < SX else 'R')


def models():
    P = FIT['pairs']; M = {}
    for pn in ['UL', 'UR', 'LL', 'LR']:
        X, Y, W = [], [], []
        for m, g, sd in P:
            p2 = panel(*m)
            if p2 == pn or (abs(m[1] - SY) < 160 and p2[1] == pn[1]) or (abs(m[0] - SX) < 160 and p2[0] == pn[0]): X.append(m); Y.append(g); W.append(sd)
        if len(X) < 12: X = [p[0] for p in P]; Y = [p[1] for p in P]; W = [p[2] for p in P]
        M[pn] = RBFInterpolator(np.array(X, float), np.array(Y, float), kernel='thin_plate_spline', smoothing=np.array(W) ** 2 * 8.0, degree=1)
    return M


MOD = models()


def ground(pts):
    out = []
    for x, y in pts:
        e, n = MOD[panel(x, y)](np.array([[x, y]], float))[0]
        out.append([round(e / KX - 81.0, 6), round(n / KY + 33.5, 6)])
    return out


def smooth(ll, k=1):
    if len(ll) < 5: return ll
    out = [ll[0]]
    for i in range(1, len(ll) - 1):
        a, b = max(0, i - k), min(len(ll), i + k + 1)
        out.append([round(sum(p[0] for p in ll[a:b]) / (b - a), 6), round(sum(p[1] for p in ll[a:b]) / (b - a), 6)])
    return out + [ll[-1]]


WIDTH = {'Santee River': 300, 'Savannah River': 250, 'Pee Dee River': 250, 'Congaree River': 180, 'Cooper River': 400, 'Broad River': 150,
         'Saluda River': 150, 'Wateree River': 150, 'Catawba River': 150, 'Waccamaw River': 150, 'Edisto or Ponpon River': 100, 'Ashley River': 150,
         'Combahee River': 100, 'North Fork of Edisto': 60, 'Black River': 60, 'Lynches Creek': 50, 'Little Pee Dee River': 60,
         'Pacolet River': 40, 'Tyger River': 40, 'Enoree River': 40}
MAIN = {'Santee River', 'Savannah River', 'Pee Dee River', 'Congaree River', 'Cooper River', 'Broad River', 'Saluda River', 'Wateree River', 'Catawba River'}
MATCHED = ('riv-savannah', 'riv-broad', 'riv-saluda', 'riv-congaree', 'riv-wateree', 'riv-catawba', 'riv-santee', 'riv-peedee', 'riv-littlepeedee',
           'riv-lynches', 'riv-edisto', 'riv-waccamaw', 'riv-cooper')
DATES = {'bnd-cherokee-lower': ('1766-11-01', '1777-05-19'), 'bnd-cherokee-upper': ('1766-11-01', '1777-05-19'), 'bnd-nc-1772': ('1772-06-01', '1781-12-31'),
         'bnd-nc-old': ('1764-01-01', '1781-12-31'), 'bnd-nc-1764e': ('1764-01-01', '1781-12-31')}
LAYER = {'river': 'rivers', 'shore': 'coast', 'road': 'roads', 'boundary': 'boundaries'}
SCAN = 'Mouzon 1775 (S135), Library of Congress g3900.ar139404'
FEATURES = []


def feat(fid, f, coords):
    kind = f['kind']; name = f['name']; d0, d1 = DATES.get(fid, ('1775-01-01', '1781-12-31'))
    matched = fid.startswith(MATCHED) and f.get('confidence') != 'low'
    p = {'id': 'SC75-' + fid.upper(), 'layer': LAYER[kind], 'kind': 'stream' if kind == 'river' else kind, 'name': name, 'desc': name,
         'from': d0, 'to': d1, 'source_id': 'S135', 'method': 'traced', 'review': 'Needs review'}
    if kind == 'river':
        p.update(width_m=WIDTH.get(name, 40), min_px=1.6 if name in MAIN else 1.0, confidence='medium' if matched else 'low', precision_m=1500 if matched else 4000,
                 basis='Picked by hand along Mouzon\'s river on the scan (%s) and snapped by program to the engraved line. Laid on the ground by the fit of the map, '
                       'which matched Mouzon\'s rivers to today\'s (Natural Earth, S136)%s.' % (SCAN, '' if matched else '; this river has no line in Natural Earth, so it follows the fit of the rivers round it'))
    elif kind == 'shore':
        p.update(confidence='low', precision_m=1500, basis='Mouzon\'s outer sea coast (%s), snapped to the engraved line and fitted to today\'s coast (Natural Earth, S136). '
                 'Inlets, islands and the sounds behind them are not traced yet.' % SCAN)
    elif kind == 'road':
        p.update(confidence='low', precision_m=4000, basis='Picked by hand along Mouzon\'s double line (%s), every 100-150 pixels of the half-resolution scan (about 9-14 km). '
                 'Where it runs between the fitted towns and crossings it is good to a few kilometres; the bends between picks are not drawn.' % SCAN)
        if f.get('cls'): p['class'] = f['cls']
    elif kind == 'boundary':
        p.update(confidence='low', precision_m=5000 if 'cherokee' in fid else 3000, basis='Mouzon\'s line (%s), picked by hand; the North Carolina lines were fitted to today\'s state line, '
                 'which follows them (Natural Earth, S136). %s' % (SCAN, 'Mouzon draws it from the Savannah at a corner tree, past DeWitt\'s Corner, to a corner tree on the Reedy River and north to the 1772 line. '
                 'The Cherokee ceded the land east of it in 1766-67 and nearly all the rest in South Carolina at DeWitt\'s Corner, 20 May 1777, so it is drawn until then.' if 'cherokee' in fid else ''))
    FEATURES.append({'type': 'Feature', 'properties': p, 'geometry': {'type': 'LineString', 'coordinates': coords}})


def main():
    shores = {}
    for fid, f in TR.items():
        if f['kind'] not in LAYER: continue
        ll = ground(f['line'])
        if f['kind'] in ('river', 'shore'): ll = smooth(ll)
        feat(fid, f, ll)
        if f['kind'] == 'shore': shores[fid] = ll
    # the sea: the traced coast from the Savannah to the North Carolina line, closed offshore. The sounds behind the coast are not sea here.
    ring = shores['shore-sw-1'] + shores['shore-sw-2'] + shores['shore-central-1'] + shores['shore-central-2'] + shores['shore-ne']
    ring = [[-80.75, 31.95]] + ring + [[-78.45, 33.80], [-78.45, 31.95], [-80.75, 31.95]]
    FEATURES.append({'type': 'Feature', 'properties': {'id': 'SC75-SEA', 'layer': 'coast', 'kind': 'sea', 'name': 'The Atlantic', 'desc': 'The sea, inside the traced coast',
                     'from': '1775-01-01', 'to': '1781-12-31', 'source_id': 'S135', 'method': 'interpolated', 'confidence': 'low', 'precision_m': 1500,
                     'basis': 'Closed offshore from the traced coast; the inlets and sounds behind the coast are left as land until they are traced.', 'review': 'Needs review'},
                     'geometry': {'type': 'Polygon', 'coordinates': [ring]}})
    G = {'type': 'FeatureCollection', 'name': 'sc-1775', 'title': 'South Carolina, 1775-1781: reconstructed base map (WarMapper)',
         'note': 'A WarMapper reconstruction, not a period map: the main lines of Mouzon\'s map of 1775, fitted to the ground. See pipeline/recon/sc_1775.py. [longitude, latitude], WGS 84.',
         'sheet': SHEET, 'features': FEATURES}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(G, open(OUT, 'w'), indent=0)
    from collections import Counter
    print(OUT, len(FEATURES), dict(Counter(f['properties']['layer'] for f in FEATURES)))


if __name__ == '__main__':
    main()
