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

The refit of 26 Nov 2026 (pipeline/georef/sc_mouzon_refit_2026_11_26.py). Session 4's fit folded the map over on itself in places (303
points along the traced lines, 26 on roads: the road to Charlotte above the Catawba Nation turned back on itself). The refit drops the
pairs on 20th-century reservoirs and on the Pee Dee, Little Pee Dee, Waccamaw and Black, stiffens the splines, and adds seven places as
point controls (Camden, Orangeburg, Charles Town, Georgetown, Dorchester, Beaufort, Long Bluff) and two ties across the eastern gap. Every
control is now held within 0.5 km (Winyah Bay 3.6, Georgetown 1.9) and nothing folds; but left out in turn a control is found again a
median 5 km off (0-17 km; Camden 17): between the controls Mouzon's own drawing is out by that much, and the stiffer fit no longer hides
it. The roads are traced again from end to end on the engraved lines, the rivers are one line each across the sections, and road ends
are joined where Mouzon has them meet.

North Carolina (SC storyline Session 2, 27 Nov 2026). The sheet now runs north to 36.75 N, where Mouzon draws the Dan and the Roanoke into
the margin above his neatline (36 37' N), and east to 77 W, so it holds Charlotte, Salisbury, Salem, Guilford Court House, Hillsborough,
Halifax, the Cape Fear and the Dan; the Neuse and the sounds east of 77 W are not traced and are left outside it. The North Carolina lines
(pipeline/recon/nc_1775_picks_2026_11_27.py, nc_1775_trace_2026_11_27.py, nc_1775_traced.json) are features of their own, ids NC75-...,
so that no reviewed South Carolina feature changes: a North Carolina line that carries one on starts on the same point of the ground as
its end (`joins`, `extends`). The fit is extended by pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py, which moves no South Carolina vertex
more than 22 m. Lines are cut at the sheet's east edge. The sea is closed along the North Carolina coast too.
"""
import json, math, os, sys
import numpy as np
from scipy.interpolate import RBFInterpolator

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
TR = json.load(open(os.path.join(HERE, 'sc_1775_traced.json')))
FIT = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'sc_mouzon_fit.json')))
OUT = os.path.join(ROOT, 'data', 'recon', 'sc-1775.geojson')
SHEET = [-83.45, 31.95, -77.0, 36.75]          # west, south, east, north (27 Nov 2026; South Carolina alone was -78.45 east, 35.3 north)
NC = json.load(open(os.path.join(HERE, 'nc_1775_traced.json')))
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
        M[pn] = RBFInterpolator(np.array(X, float), np.array(Y, float), kernel='thin_plate_spline', smoothing=np.array(W) ** 2 * FIT.get('smoothing', {}).get(pn, 8.0), degree=1)   # stiffer since the refit of 26 Nov 2026
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
MATCHED = ('riv-savannah', 'riv-broad', 'riv-saluda', 'riv-congaree', 'riv-wateree', 'riv-catawba', 'riv-santee',
           'riv-lynches', 'riv-edisto', 'riv-cooper')   # since the refit of 26 Nov 2026 the Pee Dee, Little Pee Dee and Waccamaw are no longer matched
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
        p.update(width_m=WIDTH.get(name, 40), min_px=1.6 if name in MAIN else 1.0, confidence='medium' if matched else 'low', precision_m=2500 if matched else 4000,
                 basis='Picked by hand along Mouzon\'s river on the scan (%s) and snapped by program to the engraved line. Laid on the ground by the fit of the map, '
                       'which matched Mouzon\'s rivers to today\'s (Natural Earth, S136)%s.' % (SCAN, '' if matched else '; this river has no line in Natural Earth, so it follows the fit of the rivers round it'))
    elif kind == 'shore':
        p.update(confidence='low', precision_m=1500, basis='Mouzon\'s outer sea coast (%s), snapped to the engraved line and fitted to today\'s coast (Natural Earth, S136). '
                 'Inlets, islands and the sounds behind them are not traced yet.' % SCAN)
    elif kind == 'road':
        p.update(confidence='low', precision_m=4000, basis='Traced along Mouzon\'s double line (%s): snapped by program to the gap between the two engraved lines, from end to end, within '
                 'about 2 km of the hand-picked line, and checked by eye (pipeline/recon/sc_1775_roads_2026_11_26.py, 26 Nov 2026). Its ends are joined to the road or town it meets '
                 'where Mouzon draws them meeting (another road within 3 km, a town within 6.5 km). Laid on the ground by the fit of the map: within about 1 km at the towns the fit holds (Camden, Orangeburg, '
                 'Charles Town, Georgetown, Dorchester, Beaufort, Ninety Six, Long Bluff), about 3-5 km between them.' % SCAN)
        if f.get('cls'): p['class'] = f['cls']
    elif kind == 'boundary':
        p.update(confidence='low', precision_m=5000 if 'cherokee' in fid else 3000, basis='Mouzon\'s line (%s), picked by hand; the North Carolina lines were fitted to today\'s state line, '
                 'which follows them (Natural Earth, S136). %s' % (SCAN, 'Mouzon draws it from the Savannah at a corner tree, past DeWitt\'s Corner, to a corner tree on the Reedy River and north to the 1772 line. '
                 'The Cherokee ceded the land east of it in 1766-67 and nearly all the rest in South Carolina at DeWitt\'s Corner, 20 May 1777, so it is drawn until then.' if 'cherokee' in fid else ''))
    FEATURES.append({'type': 'Feature', 'properties': p, 'geometry': {'type': 'LineString', 'coordinates': coords}})


SEAMS = [(0, 99999, 1213, 1229), (4166, 4253, 0, 1229), (4208, 4253, 1213, 99999)]   # the blank strips between the mounted sections of the scan (the last: North Carolina, 27 Nov 2026)


NCSEAMS = [(0, 99999, 1213, 1229), (4212, 4248, -1900, 1229), (4208, 4253, 1213, 99999)]   # North Carolina's lines: only the blank strips themselves (27 Nov 2026)


def off_seams(pts, seams=SEAMS):
    return [p for p in pts if not any(a <= p[0] <= b and c <= p[1] <= d for a, b, c, d in seams)]


def km(a, b): return math.hypot((a[0] - b[0]) * KX, (a[1] - b[1]) * KY)


def no_reversals(ll, minlen=0.3):
    """Drop the points where a road turns back on itself (more than 120 degrees) on the ground: a kink left by the fit or the snapping."""
    changed = True
    while changed and len(ll) > 2:
        changed = False; R = [ll[0]]
        for i in range(1, len(ll) - 1):
            a, b, c = R[-1], ll[i], ll[i + 1]
            u = ((b[0] - a[0]) * KX, (b[1] - a[1]) * KY); v = ((c[0] - b[0]) * KX, (c[1] - b[1]) * KY)
            if math.hypot(*u) > 1e-6 and math.hypot(*v) > 1e-6 and (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v)) < -0.5 and min(math.hypot(*u), math.hypot(*v)) < 3 * minlen + 2:
                changed = True; continue
            R.append(b)
        R.append(ll[-1]); ll = R
    return ll


def turn_back(a, b, c):
    """True where the line a-b-c turns back on itself (more than 120 degrees) on the ground."""
    u = ((b[0] - a[0]) * KX, (b[1] - a[1]) * KY); v = ((c[0] - b[0]) * KX, (c[1] - b[1]) * KY)
    nu, nv = math.hypot(*u), math.hypot(*v)
    return nu > 1e-6 and nv > 1e-6 and (u[0] * v[0] + u[1] * v[1]) / (nu * nv) < -0.5


def trim_hooks(ll, most=1.5):
    """Cut off a short hook (up to `most` km) where a line's end turns back on itself: left where a trace runs into the strip between
    the scan's mounted sections, which the two sections' fits do not quite agree on."""
    for _ in (0, 1):
        for i in range(len(ll) - 2, 0, -1):
            tail = sum(km(p, q) for p, q in zip(ll[i:], ll[i + 1:]))
            if tail > most: break
            if turn_back(ll[i - 1], ll[i], ll[i + 1]): ll = ll[:i + 1]; break
        ll = ll[::-1]
    return ll


def add_end(ll, end, q, most=1.5):
    """Join a line's end to q. Where q lies behind the end (the line ran a little past the junction), the overshoot, up to `most` km,
    is cut back first; where it lies further behind than that, the end is left as it is."""
    ll = list(ll) if end == -1 else list(ll[::-1])
    cut = 0.0
    while len(ll) > 2 and turn_back(ll[-2], ll[-1], q):
        cut += km(ll[-2], ll[-1])
        if cut > most: return ll if end == -1 else ll[::-1], False
        ll.pop()
    ll.append(q)
    return (ll if end == -1 else ll[::-1]), True


def nearest_on(pt, line):
    best, bd = None, 1e9
    for a, b in zip(line, line[1:]):
        vx, vy = (b[0] - a[0]) * KX, (b[1] - a[1]) * KY; L = vx * vx + vy * vy
        u = 0 if not L else max(0, min(1, ((pt[0] - a[0]) * KX * vx + (pt[1] - a[1]) * KY * vy) / L))
        q = [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u]; d = km(pt, q)
        if d < bd: bd, best = d, q
    return best, bd


def places():
    import csv
    f = os.path.join(ROOT, 'data', 'WarMapper battle data', 'csv', 'Revolutionary War', 'Control places.csv')
    return [[float(r['lon']), float(r['lat'])] for r in csv.DictReader(open(f)) if r['playback_id'] == 'sc-orientation']


def join_roads(roads):
    """Where Mouzon's roads meet at a town or at each other, make them meet on the ground too (the fit leaves their ends a little apart):
      1. an end within 6.5 km of one of the orientation's places goes to the place;
      2. two ends still loose within 1.5 km of each other meet at the point between them;
      3. an end still loose within 3 km of another road joins that road.
    Where the new end lies behind the old (the road ran a little past the junction), the overshoot, up to 3 km, is cut back first."""
    P = places(); done = set()

    def put(k, end, q, force):
        new, ok = add_end(roads[k], end, q, most=3.0)
        if ok or force: roads[k] = new if ok else ([q] + roads[k] if end == 0 else roads[k] + [q])
        if ok or force: done.add((k, end))
    for k in roads:
        for end in (0, -1):
            c = [(km(roads[k][end], q), q) for q in P]; c = [x for x in c if x[0] < 6.5]
            if not c: continue
            q = list(min(c)[1]); ll = roads[k] if end == -1 else roads[k][::-1]
            # over its last 5 km a road comes steadily nearer the town: a point that lies further from it than the point before is
            # dropped (the fit bends the ground round a town it holds, and could swing a road's last km past the town and back)
            run, i = 0.0, len(ll) - 1
            while i > 0 and run < 5.0: run += km(ll[i - 1], ll[i]); i -= 1
            tail = [ll[i]]
            for p in ll[i + 1:]:
                if km(p, q) < km(tail[-1], q): tail.append(p)
            ll = ll[:i] + tail
            roads[k] = ll if end == -1 else ll[::-1]
            put(k, end, q, False)
    E = [(k, e) for k in roads for e in (0, -1) if (k, e) not in done]
    for i, (k, e) in enumerate(E):
        for k2, e2 in E[i + 1:]:
            if k2 == k or (k, e) in done or (k2, e2) in done: continue
            a, b = roads[k][e], roads[k2][e2]
            if km(a, b) < 1.5:
                m = [round((a[0] + b[0]) / 2, 6), round((a[1] + b[1]) / 2, 6)]
                roads[k][e] = m; roads[k2][e2] = list(m); done.update({(k, e), (k2, e2)})
    for k in roads:
        for end in (0, -1):
            if (k, end) in done: continue
            best = min((nearest_on(roads[k][end], l2) for k2, l2 in roads.items() if k2 != k), key=lambda x: x[1])
            if best[1] < 3.0: put(k, end, [round(best[0][0], 6), round(best[0][1], 6)], best[1] < 1.0)
    return roads


def join_rivers(pieces):
    """The pieces of one river, cut where the scan's mounted sections meet, joined end to end where they come within 8 km."""
    out = []
    left = list(pieces)
    while left:
        fid, f, ll = left.pop(0); chain = list(ll); ids = [fid]; grew = True
        while grew:
            grew = False
            for j, (fid2, f2, l2) in enumerate(left):
                for A, B, how in ((chain[-1], l2[0], 'tail'), (chain[-1], l2[-1], 'tailr'), (chain[0], l2[-1], 'head'), (chain[0], l2[0], 'headr')):
                    if km(A, B) < 8.0:
                        seg = l2 if how in ('tail', 'head') else l2[::-1]
                        chain = chain + seg if how.startswith('tail') else seg + chain
                        ids.append(fid2); left.pop(j); grew = True; break
                if grew: break
        out.append((ids, f, chain))
    return out


NCSCAN = 'Mouzon 1775 (S135), Library of Congress g3900.ar139404; the North Carolina part checked against Collet 1770 (S151, g3900.ar150000)'
NC_MATCHED = ('riv-catawba-nc', 'riv-broad-nc', 'riv-yadkin', 'riv-peedee-nc', 'riv-haw', 'riv-deep', 'riv-capefear', 'riv-dan', 'riv-roanoke')
NC_WIDTH = {'Yadkin River': 200, 'Haw River': 80, 'Deep River': 80, 'Cape Fear River': 200, 'Dan River': 120, 'Roanoke River': 200, 'Reedy Fork': 30, 'Troublesome Creek': 30}
NC_MAIN = {'Yadkin River', 'Cape Fear River', 'Dan River', 'Roanoke River', 'Catawba River', 'Pee Dee River', 'Haw River', 'Deep River', 'Broad River'}


def clip_east(ll, east=SHEET[2]):
    """The line up to the sheet's east edge (cut where it first crosses it)."""
    out = [ll[0]]
    for a, b in zip(ll, ll[1:]):
        if b[0] > east:
            if a[0] <= east: u = (east - a[0]) / (b[0] - a[0]); out.append([east, round(a[1] + (b[1] - a[1]) * u, 6)])
            break
        out.append(b)
    return out


def nc_feat(fid, f, coords):
    kind = f['kind']; name = f['name']
    p = {'id': 'NC75-' + fid.upper(), 'layer': LAYER[kind], 'kind': 'stream' if kind == 'river' else kind, 'name': name, 'desc': name,
         'from': '1775-01-01', 'to': '1781-12-31', 'source_id': 'S135', 'method': 'traced', 'review': 'Needs review'}
    fit = ('Laid on the ground by the fit of the map, extended to North Carolina on 27 Nov 2026 (pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py): '
           'nine towns hold it (Charlotte, Salisbury, Salem, Bethabara, New Garden, Hillsborough, Halifax, Cross Creek, Wilmington), each found again '
           '1.3-6.6 km from its site when left out, and the rivers, coast and Virginia line matched to Natural Earth (S136).')
    if kind == 'river':
        m = fid in NC_MATCHED
        p.update(width_m=NC_WIDTH.get(name, WIDTH.get(name, 40)), min_px=1.6 if name in NC_MAIN else 1.0, confidence='medium' if m else 'low', precision_m=2500 if m else 4000,
                 basis='Picked by hand along Mouzon\'s river on the scan (%s) and snapped by program to the engraved line. %s%s' % (NCSCAN, fit,
                       ' This river lies a median 0.3-0.75 km from today\'s course in Natural Earth.' if m else ' This river has no line in Natural Earth, so it follows the fit of the rivers round it.'))
        if f.get('joins'): p['basis'] += ' It carries on the South Carolina line of the same river from the point where that line ends.'
        if fid in JOINS: p['basis'] += (' There the fit of 26 Nov 2026 folds the ground (it puts the end of the South Carolina line some 8 km off today\'s river), so the first '
                                        'kilometres of this line are left out and it joins that end straight, over %.1f km.' % JOINS[fid])
    elif kind == 'shore':
        p.update(confidence='low', precision_m=1500, basis='Mouzon\'s outer sea coast (%s), snapped to the engraved line, from Little River past Cape Fear to Bogue; fitted to today\'s coast '
                 '(Natural Earth, S136), a median 0.4 km from it. %s Inlets, islands and the sounds behind them are not traced yet: the sea is closed across the inlets and the mouth of the Cape Fear. Cut at the sheet\'s edge, 77 W.' % (NCSCAN, fit))
    elif kind == 'road':
        p.update(confidence='low', precision_m=4000, basis='Traced along Mouzon\'s double line (%s): snapped by program to the gap between the two engraved lines, within about 2 km of the '
                 'hand-picked line, and checked by eye on overlays. %s Good to about 1-2 km at the towns that hold the fit, 3-5 km between them. Named by the places Mouzon has it join; '
                 'which armies used it is for the playbacks to show, from their sources.' % (NCSCAN, fit))
        if f.get('cls'): p['class'] = f['cls']
        if f.get('extends'): p['basis'] += ' It carries on a South Carolina road from the point where that road ends.'
    elif kind == 'boundary':
        p.update(confidence='low', precision_m=3000, basis='Mouzon\'s line between Virginia and North Carolina (%s), found from the red he colours it, column by column; fitted to today\'s state line, '
                 'which follows the line run in 1728 and carried west in 1749 (Natural Earth, S136), within about 1 km. Cut at the sheet\'s edge, 77 W.' % NCSCAN)
    FEATURES.append({'type': 'Feature', 'properties': p, 'geometry': {'type': 'LineString', 'coordinates': coords}})


JOINS = {}   # North Carolina lines joined straight across a fold of the fit: km of the straight join


def north_carolina(built):
    """The North Carolina lines: their own features, after South Carolina's. `built`: {SC feature id: its coordinates as written}."""
    def sc_line(link):   # the built South Carolina feature that `link` (a traced id) became
        fam = (link.rsplit('-', 1)[0] if link[-1].isdigit() else link).upper()
        c = [v for k, v in built.items() if k in ('SC75-' + link.upper(), 'SC75-' + fam)]
        return c[0] if c else None
    out = {}
    for fid, f in NC.items():
        ll = ground(off_seams(f['line'], NCSEAMS) if f['kind'] in ('road', 'river') else f['line'])
        if f['kind'] in ('river', 'shore'): ll = smooth(ll)
        if f['kind'] == 'road': ll = no_reversals(ll)
        link = f.get('joins') or f.get('extends')
        L = sc_line(link) if link else None
        if link: assert L, 'no built South Carolina line for %s (%s)' % (link, fid)
        if L:   # the end nearer the South Carolina line goes onto it: on the point nearest it, or across a seam (up to 8 km) to it
            (q0, d0), (q1, d1) = nearest_on(ll[0], L), nearest_on(ll[-1], L)
            end, q, d = (0, q0, d0) if d0 <= d1 else (-1, q1, d1)
            q = [round(q[0], 6), round(q[1], 6)]; assert d < 8.0, '%s is %.1f km from %s' % (fid, d, link)
            if d < 1.0: ll[end] = q
            else: ll = [q] + ll if end == 0 else ll + [q]
            # Where the 26 Nov fit folds the ground at a South Carolina end (the Catawba at the 1772 line), the first km of the North Carolina line
            # run back on themselves: they are cut, up to the last point where the line turns back in its first 30 km, and the line joins the end straight.
            ll = ll if end == 0 else ll[::-1]
            run, last = 0.0, None
            for i in range(1, len(ll) - 1):
                run += km(ll[i - 1], ll[i])
                if run > 30: break
                if turn_back(ll[i - 1], ll[i], ll[i + 1]): last = i
            if last:
                j = last + 1
                while j < len(ll) - 1 and turn_back(ll[0], ll[j], ll[j + 1]): j += 1
                JOINS[fid] = round(km(ll[0], ll[j]), 1); ll = [ll[0]] + ll[j:]
            ll = ll if end == 0 else ll[::-1]
        out[fid] = ll
    # roads that Mouzon has meet a North Carolina road or town meet it on the ground: an end within 1.5 km of another line's point goes to it
    roads = {k: v for k, v in out.items() if NC[k]['kind'] == 'road'}
    for k, ll in roads.items():
        for end in (0, -1):
            best = min(((nearest_on(ll[end], l2)) for k2, l2 in roads.items() if k2 != k), key=lambda x: x[1], default=(None, 99))
            if best[1] < 1.5: ll[end] = [round(best[0][0], 6), round(best[0][1], 6)]
    for fid, ll in out.items():
        ll = clip_east(ll) if NC[fid]['kind'] in ('shore', 'boundary', 'river', 'road') else ll
        if len(ll) >= 2: nc_feat(fid, NC[fid], ll)
    return out


def main():
    shores = {}; roads = {}; rivers = {}
    for fid, f in TR.items():
        if f['kind'] not in LAYER: continue
        ll = ground(off_seams(f['line']) if f['kind'] in ('road', 'river') else f['line'])
        if f['kind'] in ('river', 'shore'): ll = smooth(ll)
        if f['kind'] == 'road': roads[fid] = no_reversals(ll); continue
        if f['kind'] == 'river': rivers.setdefault(f['name'], []).append((fid, f, trim_hooks(ll))); continue
        feat(fid, f, ll)
        if f['kind'] == 'shore': shores[fid] = ll
    for name, pieces in rivers.items():   # since 26 Nov 2026: one line for each river, joined across the seams of the scan
        for ids, f, chain in join_rivers(pieces):
            fid = ids[0].rsplit('-', 1)[0] if len(ids) > 1 and ids[0][-1].isdigit() else ids[0]
            if len(ids) > 1: f = dict(f, confidence='low' if any(TR[i].get('confidence') == 'low' for i in ids) else f.get('confidence'))
            feat(fid, f, chain)
            if len(ids) > 1: FEATURES[-1]['properties']['basis'] += (' Traced in %d pieces, one on each mounted section of the scan; joined here across the strip where the sections meet, '
                                                                      'which the scan does not show (a straight line of 2-6 km).' % len(ids))
    for fid, ll in join_roads(roads).items(): feat(fid, TR[fid], no_reversals(ll))
    built = {f['properties']['id']: f['geometry']['coordinates'] for f in FEATURES if f['geometry']['type'] == 'LineString'}
    nc = north_carolina(built)   # since 27 Nov 2026
    ncshore = clip_east(nc['shore-nc'])
    # the sea: the traced coast from the Savannah to the North Carolina line, closed offshore. The sounds behind the coast are not sea here.
    ring = shores['shore-sw-1'] + shores['shore-sw-2'] + shores['shore-central-1'] + shores['shore-central-2'] + shores['shore-ne']
    ring = [[-80.75, 31.95]] + ring + ncshore[1:] + [[SHEET[2], 31.95], [-80.75, 31.95]]   # since 27 Nov 2026 along the North Carolina coast to the sheet's edge
    FEATURES.append({'type': 'Feature', 'properties': {'id': 'SC75-SEA', 'layer': 'coast', 'kind': 'sea', 'name': 'The Atlantic', 'desc': 'The sea, inside the traced coast',
                     'from': '1775-01-01', 'to': '1781-12-31', 'source_id': 'S135', 'method': 'interpolated', 'confidence': 'low', 'precision_m': 1500,
                     'basis': 'Closed offshore from the traced coast, from the Savannah to the sheet\'s east edge at 77 W; the inlets and sounds behind the coast are left as land until they are traced.', 'review': 'Needs review'},
                     'geometry': {'type': 'Polygon', 'coordinates': [ring]}})
    G = {'type': 'FeatureCollection', 'name': 'sc-1775', 'title': 'The Carolinas, 1775-1781: reconstructed base map (WarMapper)',
         'note': 'A WarMapper reconstruction, not a period map: the main lines of Mouzon\'s map of 1775, fitted to the ground; South Carolina since 25 Nov 2026, North Carolina to 77 W since 27 Nov 2026. See pipeline/recon/sc_1775.py. [longitude, latitude], WGS 84.',
         'sheet': SHEET, 'features': FEATURES}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(G, open(OUT, 'w'), indent=0)
    from collections import Counter
    print(OUT, len(FEATURES), dict(Counter(f['properties']['layer'] for f in FEATURES)))


if __name__ == '__main__':
    main()
