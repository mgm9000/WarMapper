"""The Cowpens, January 1781: the reconstructed base map's features, to data/recon/cowpens-1781.geojson.

  python3 -I pipeline/recon/cowpens_1781.py        writes data/recon/cowpens-1781.geojson and prints what it wrote

What this is. A WarMapper reconstruction, not a period map. No map of 1781 shows this ground. The roads below are the roads Bearss
drew in 1967 on his surveyed base (S107) as the roads of the battle, fitted to the ground by pipeline/georef/cowpens_bearss.py, and,
beyond the edge of his sheet, roads read off the US Geological Survey's 1959 sheet (S108) where Mills's map of 1825 (S110) has a road
leaving the Cowpens crossroads the same way. The page draws them in period dress on today's ground (the terrain), which the park has
kept much as it was. Nothing here has been checked by a historian.

How each road was checked.
  The road through the field is the park's trace of the Green River Road as OpenStreetMap draws it (S39). Bearss's road matches it to
  a median of 4 m; the 1975 photo map (S109) shows its bed; the 1959 sheet has SC 11 on it; Landers's 1928 sketch (S103) has the
  highway of 1928 on it.
  Bearss's other roads were each laid over the 1959 sheet: his road east of the field, his roads to the Pacolet, to Island Ford and to
  Mill Gap all lie within about 20-50 m of a road of 1959 (the road east, old SC 110, the road north and SC 11 west), and the road east
  shows as a track on the 1975 photo map. So they are `medium`.
  Beyond his sheet the lines are the 1959 roads (picked from the sheet, reprojected to WGS 84 on a grid of 0.00002 degrees: the
  picks below are pixels of that grid) or, for Tarleton's approach, today's Green River Road. They are `low`: a road of 1959 or of
  today on the line Mills gives, not a survey of 1781.
  Landers (1928) also draws an "Old Mill Gap Road" east of the field some 20 degrees south of Bearss's; his sketch is fitted only by
  its western road and drifts that far out, and the 1959 sheet and the 1975 photo map have the road where Bearss has it. His
  "Green River Road" running north to it is the 1959 road used below for Tarleton's approach.
The streams are today's (OpenStreetMap), which follow the wooded draws of the 1975 photo map and the blue lines of the 1959 sheet.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import cowpens_geo as G

OUT = os.path.join(ROOT, 'data', 'recon', 'cowpens-1781.geojson')
BEARSS = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'cowpens_bearss_fit.json')))
SHEET = [-81.832, 35.112, -81.778, 35.148]          # west, south, east, north
DAY = '1781-01-17'
GRID = (-81.840, 35.155, 0.00002)                   # the 1959 sheet reprojected: west, north, degrees a pixel


def g59(pts): return [[round(GRID[0] + x * GRID[2], 6), round(GRID[1] - y * GRID[2], 6)] for x, y in pts]


# 1959 sheet picks (pixels of the reprojected grid)
CONNECTOR = [(2648, 1150), (2640, 1230), (2628, 1300), (2622, 1330), (2615, 1400), (2600, 1450), (2575, 1495), (2540, 1540), (2500, 1580), (2475, 1603)]
SOUTH = [(1185, 1250), (1150, 1290), (1120, 1370), (1085, 1450), (1060, 1530), (1025, 1610), (980, 1680), (950, 1750), (935, 1850), (950, 1950),
         (985, 2050), (1000, 2150), (995, 2200)]
NORTH = [(1015, 520), (1030, 480), (1050, 420), (1068, 370), (1090, 300), (1110, 255), (1140, 180)]
WEST = [(900, 612), (860, 590), (800, 560), (750, 540), (600, 472), (450, 410), (300, 385)]


def osm(code=None, name=None):
    out = []
    for ln in open(os.path.join(ROOT, 'data', 'osm', 'cowpens.txt'), encoding='utf-8'):
        c, n, body = ln.rstrip('\n').split('|', 2); la = lo = 0; pts = []
        for i, pr in enumerate(body.split(';')):
            a, b = pr.split(','); la, lo = (int(a), int(b)) if i == 0 else (la + int(a), lo + int(b)); pts.append([lo / 1e5, la / 1e5])
        if (code is None or c == code) and (name is None or n == name): out.append((n, pts))
    return out


def inside(p): return SHEET[0] <= p[0] <= SHEET[2] and SHEET[1] <= p[1] <= SHEET[3]


def clip(pts):
    """The parts of a line inside the sheet, each cut where it crosses the edge."""
    def cross(a, b):
        t = 1.0
        for k, (lo, hi) in ((0, (SHEET[0], SHEET[2])), (1, (SHEET[1], SHEET[3]))):
            for e in (lo, hi):
                if (a[k] - e) * (b[k] - e) < 0: t = min(t, (e - a[k]) / (b[k] - a[k]))
        return [round(a[0] + (b[0] - a[0]) * t, 6), round(a[1] + (b[1] - a[1]) * t, 6)]
    runs, cur = [], []
    for i, p in enumerate(pts):
        if inside(p):
            if not cur and i > 0: cur.append(cross(p, pts[i - 1]))
            cur.append(p)
        elif cur:
            cur.append(cross(cur[-1], p)); runs.append(cur); cur = []
    if cur: runs.append(cur)
    return [r for r in runs if len(r) > 1]


def snap(q, line):
    """The point of `line` nearest `q`: where a branch Bearss draws from the road meets the trace (his crossing lies 10-25 m off it)."""
    qx, qy = G._xy((q[1], q[0])); best = None
    for a, b in zip(line, line[1:]):
        ax, ay = G._xy((a[1], a[0])); bx, by = G._xy((b[1], b[0])); dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((qx - ax) * dx + (qy - ay) * dy) / max(1e-9, dx * dx + dy * dy))); px, py = ax + t * dx, ay + t * dy
        d = math.hypot(qx - px, qy - py)
        if best is None or d < best[0]: best = (d, px, py)
    la, lo = G._ll(best[1], best[2]); return [lo, la]


def nearest_index(pts, q):
    qx, qy = G._xy((q[1], q[0])); return min(range(len(pts)), key=lambda i: math.hypot(G._xy((pts[i][1], pts[i][0]))[0] - qx, G._xy((pts[i][1], pts[i][0]))[1] - qy))


FEATURES = []


def smooth(pts, k=3, step=12):
    """Bearss's roads come off the scan as thinned pixels, a metre or two of jitter each: a running mean over 2k+1 points, then a point
    every `step` metres, ends kept."""
    xy = [G._xy((p[1], p[0])) for p in pts]; out = []
    for i in range(len(xy)):
        a, b = max(0, i - k), min(len(xy), i + k + 1)
        out.append(xy[i] if i in (0, len(xy) - 1) else (sum(q[0] for q in xy[a:b]) / (b - a), sum(q[1] for q in xy[a:b]) / (b - a)))
    keep = [out[0]]
    for q in out[1:-1]:
        if math.hypot(q[0] - keep[-1][0], q[1] - keep[-1][1]) >= step: keep.append(q)
    keep.append(out[-1])
    return [[G._ll(*q)[1], G._ll(*q)[0]] for q in keep]


def feat(fid, layer, kind, pts, desc, source, method, confidence, precision, basis, cls=None, name=None):
    for n, run in enumerate(clip(pts)):
        p = {'id': fid + ('' if n == 0 else '-%d' % (n + 1)), 'layer': layer, 'kind': kind, 'desc': desc, 'from': DAY, 'to': DAY, 'source_id': source, 'method': method,
             'confidence': confidence, 'precision_m': precision, 'basis': basis, 'review': 'Needs review'}
        if cls: p['class'] = cls
        if name: p['name'] = name
        FEATURES.append({'type': 'Feature', 'properties': p, 'geometry': {'type': 'LineString', 'coordinates': run}})


def main():
    trace = osm('Tk', 'Historic Green River Road')[0][1]
    feat('COW81-ROAD-FIELD', 'road-field', 'road', trace, 'The Mill Gap road (today the Historic Green River Road) through the field', 'S107', 'traced', 'medium', 25,
         "The park's trace of the road, as OpenStreetMap draws it (S39). Bearss draws the road of the battle here (S107, Plate I): fitted to the ground, his road lies "
         "4 m from the trace at the median, 15 m at the 90th percentile. The 1975 photo map (S109) shows the old road bed on the same line, and SC 11 ran on it in 1959 (S108).",
         cls='main', name='Mill Gap road')
    R = {k: smooth(v) for k, v in BEARSS['roads'].items()}
    for k in ('to-island-ford', 'to-mill-gap'): R[k][0] = snap(R[k][0], trace)          # the fork, on the trace
    R['to-pacolet'][-1] = snap(R['to-pacolet'][-1], trace)                                # the crossing, on the trace
    mg = R['mill-gap']; cut = nearest_index(mg, trace[0])          # Bearss's road east of where the park's trace ends
    mg[cut] = trace[0]
    feat('COW81-ROAD-EAST', 'roads-bearss', 'road', mg[:cut + 1][::-1], 'The Mill Gap road east of the field, towards Cherokee Ford on the Broad', 'S107', 'traced', 'medium', 40,
         "Bearss's road (S107, Plate I) from where the park's trace ends to the edge of his sheet. Bearss: the Mill Gap road \"crossed the Broad at Cherokee Ford\" (p. 8). "
         "A road of the 1959 sheet (S108) and a track on the 1975 photo map (S109) lie on the same line. Landers (1928) draws his \"Old Mill Gap Road\" some 20 degrees further south.",
         cls='main', name='Mill Gap road')
    feat('COW81-ROAD-PACOLET', 'roads-bearss', 'road', R['to-pacolet'][::-1], 'The road to the Pacolet and Spartanburg', 'S107', 'traced', 'medium', 40,
         "Bearss's road \"To Pacolet River\" (S107, Plate I), the road from present day Spartanburg to Island Ford (p. 8). It lies within about 20 m of old SC 110 on the 1959 sheet (S108) "
         "and about 50 m of the road Landers draws south from the field in 1928 (S103).", name='road to the Pacolet')
    feat('COW81-ROAD-ISLAND', 'roads-bearss', 'road', R['to-island-ford'], 'The road to Island Ford on the Broad', 'S107', 'traced', 'medium', 40,
         "Bearss's road \"To Island Ford\" (S107, Plate I). It lies within about 25 m of Landers's road \"To Island Ford\" (1928, S103) and of the road north on the 1959 sheet (S108).", name='road to Island Ford')
    feat('COW81-ROAD-MILLGAP-W', 'roads-bearss', 'road', R['to-mill-gap'], 'The Mill Gap road west, towards Mill Gap in the mountains', 'S107', 'traced', 'medium', 40,
         "Bearss's road \"To Mill Gap\" (S107, Plate I): the Mill Gap road \"ran northwestwardly into the mountains\" (p. 8). The park's trace follows it to SC 11, and SC 11 of 1959 (S108) runs on it.", cls='main', name='Mill Gap road')
    ends = {k: v for k, v in R.items()}
    LOW = ("Beyond the edge of Bearss's sheet: the road of the 1959 sheet (S108) on the line Mills's map of 1825 (S110) gives a road leaving the Cowpens crossroads. "
           "Picked from the 1959 sheet, which is drawn at 1:62,500 (about 30 m of line). A road of 1959, not a survey of 1781.")
    feat('COW81-ROAD-GREENRIVER-N', 'roads-beyond', 'road', [mg[0]] + g59(CONNECTOR), "Tarleton's approach: the Green River road north to the Mill Gap road", 'S108', 'traced', 'low', 60,
         "The road of the 1959 sheet (S108) from the end of today's Green River Road north to where Bearss's Mill Gap road leaves his sheet. Landers (1928, S103) names it \"Green River Road\". "
         "It is the way between the two that Bearss and Landers both imply; it is not on Bearss's sheet. Gap CG06.", cls='main', name='Green River road')
    feat('COW81-ROAD-SOUTH', 'roads-beyond', 'road', [ends['to-pacolet'][0]] + g59(SOUTH), 'The road to the Pacolet and Spartanburg, south of Bearss\'s sheet', 'S108', 'traced', 'low', 60, LOW, name='road to the Pacolet')
    feat('COW81-ROAD-NORTH', 'roads-beyond', 'road', [ends['to-island-ford'][-1]] + g59(NORTH), 'The road to Island Ford, north of Bearss\'s sheet', 'S108', 'traced', 'low', 60, LOW, name='road to Island Ford')
    feat('COW81-ROAD-WEST', 'roads-beyond', 'road', [ends['to-mill-gap'][-1]] + g59(WEST), 'The Mill Gap road west of Bearss\'s sheet', 'S108', 'traced', 'low', 60, LOW, cls='main', name='Mill Gap road')
    grr = osm('Ht', 'Green River Road')[0][1]
    if grr[0][1] < grr[-1][1]: grr = grr[::-1]                    # from its north end
    feat('COW81-ROAD-GREENRIVER-S', 'road-approach', 'road', grr, "Tarleton's approach: today's Green River Road", 'S39', 'traced', 'low', 80,
         "Today's Green River Road (OpenStreetMap, S39), the road the playback brings Tarleton up from Thicketty Creek. It runs on, as a road of 1959 (S108), to the Mill Gap road east of the field. "
         "That it is the road of 1781 is the playback's reading (CG06), not a source's.", cls='main', name='Green River road')
    for n, (name, pts) in enumerate(osm('Ws')):
        feat('COW81-STREAM-%02d' % (n + 1), 'streams', 'stream', pts, name or 'A branch', 'S39', 'traced', 'medium', 30,
             "Today's stream (OpenStreetMap, S39). Streams keep their beds: these follow the wooded draws of the 1975 photo map (S109) and the blue lines of the 1959 sheet (S108). "
             "Bearss puts Morgan's camp in the ravine at the head of the branch east of the park road (S107, p. 8 and Plate I).", name=name or None)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    G_ = {'type': 'FeatureCollection', 'name': 'cowpens-1781', 'title': 'The Cowpens, January 1781: reconstructed base map (WarMapper)',
          'note': 'A WarMapper reconstruction, not a period map: the roads Bearss drew in 1967 as the roads of the battle, fitted to the ground, and beyond his sheet roads of the '
                  'USGS 1959 sheet on the lines Mills (1825) gives. See pipeline/recon/cowpens_1781.py. [longitude, latitude], WGS 84.',
          'sheet': SHEET, 'features': FEATURES}
    json.dump(G_, open(OUT, 'w'), indent=0)
    from collections import Counter
    print(OUT, len(FEATURES), dict(Counter(f['properties']['layer'] for f in FEATURES)))


if __name__ == '__main__':
    main()
