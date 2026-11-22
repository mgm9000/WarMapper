"""Manila, February 1899: the reconstructed base map's features, from pixel picks on two period maps to data/recon/manila-1899.geojson.

  python3 pipeline/recon/manila_1899.py            writes data/recon/manila-1899.geojson and prints what it wrote
  python3 pipeline/recon/manila_1899.py --fit      prints the fit of the engineer map and its residuals

What this is. A WarMapper reconstruction, not a period map: the lines below were read off two 1899 Army maps and are drawn by the
playback in period dress. Nothing here has been checked by a person.

Sources.
  S78  1st Lieut. W. G. Haan, "Map of the City of Manila and vicinity showing operations of Second Division, 8th Army Corps, from
       February 4th to February 28th 1899" (compiled from surveys by Co. A, U.S. Engineers; 1,200 feet to 1 inch). National Archives
       identifier 109182890. The picks are pixels of the 3,840 x 2,847 copy of the scan on Wikimedia Commons (the 11,998 x 8,896
       original could not be fetched: the host limits full-size downloads). North of the Pasig and the city as far south as Malate.
  S64  Sgt. J. H. Warking, Signal Corps, "Map of Manila and vicinity ...", February 1899 (Library of Congress). Used only where the
       engineer map ends: the shore north of the Vitas canal and south of Malate, and the Pasig above Santa Ana. A sketchier map.

How the engineer map was tied to the ground (pipeline/georef/manila_haan_fit.json holds the numbers).
  1. A first fit from the map's rivers and creeks: the blue water tint was separated by colour, thinned to centre lines, and matched
     to today's waterways (the OpenStreetMap extract in data/osm/manila.txt) by an iterated closest-point affine fit: 2,389 matched
     points, median distance 2.8 scan px (about 10 m).
  2. Checked at street junctions that still exist. South of Calle Azcarraga and east to San Juan the map agrees with today's streets
     to 5-25 m (Intramuros' streets fall on today's to a few metres). In Tondo it runs 40-55 m south, and at Caloocan about 150 m
     south-east: the map itself is weaker there (the ground was taken on 10 February).
  3. So the final fit is a smoothed thin-plate spline through 9 junctions and bridges, the railway (each traced point moved across
     the track onto today's line, which keeps the 1892 right of way) and anchors from step 1 where step 2 confirmed it.
     Residual at the 9 control points 17 m rms (40 m at worst); leaving each out in turn 27 m rms (55 m at worst, at Caloocan).
     Two points kept out as checks: the Calle Iris - Calle Alix junction 42 m, the Ayala bridge 33 m (both rebuilt since).
  The Warking pieces use that map's own fit (pipeline/georef/manila_georef.py, about 170 m) and are then slid to meet the engineer
  map's line where the two join.

How the features were read ("method" on each feature).
  traced        pixel by pixel from gridded crops of the scan, by Claude (an AI model) reading the picture; not machine-vectorised.
  AI-extracted  separated by a program: the water tint taken out by colour inside the inked bank lines, the outline vectorised, then
                gaps under lettering closed and leaks cut by hand (pipeline/recon/manila_1899_water.py).
  interpolated  not on any map: the closing edges of the bay's area beyond the drawing.
Confidence is never "high": no feature has been checked against a second period map by a person. "medium" is a feature read from the
surveyed engineer map where the fit is good; "low" is anything from the Signal Corps map, anything machine-extracted without clear
banks, and blockhouses 2 to 6 (no control point near them).
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'georef'))
import manila_georef as warking            # the Signal Corps map's affine fit

FIT = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'manila_haan_fit.json')))
PICKS = json.load(open(os.path.join(HERE, 'manila_1899_picks.json')))
DETAIL = json.load(open(os.path.join(HERE, 'manila_1899_detail.json')))      # the map's own ink lines and water wash, by program (manila_1899_linework.py)
DETAIL_S = json.load(open(os.path.join(HERE, 'manila_1898_detail.json')))    # the 1898 sheet's ink lines south of Malate, by program (manila_1898_linework.py)
ARR = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'manila_arrabales_fit.json')))   # the 1898 sheet's fit, and its slide in the south
OUT = os.path.join(ROOT, 'data', 'recon', 'manila-1899.geojson')
HAAN, WARK, ARRAB = 'S78', 'S64', 'S79'
SHEET = [120.930, 14.520, 121.057, 14.681]   # west, south, east, north: the edge of the reconstructed sheet
FROM, TO = '1899-02-04', '1899-02-28'      # the engineer map's own span; the Signal Corps map is of 5 to 10 February


def haan():
    """scan pixel -> [lon, lat] by the smoothed thin-plate spline of the fit file."""
    from scipy.interpolate import RBFInterpolator
    P = np.array(FIT['pairs']); f = RBFInterpolator(P[:, :2], P[:, 2:], kernel='thin_plate_spline', smoothing=FIT['smoothing'])
    def ll(pts):
        m = f(np.atleast_2d(np.asarray(pts, float)))
        return [[round(FIT['lon0'] + e / FIT['kx'], 6), round(FIT['lat0'] + n / FIT['ky'], 6)] for e, n in m]
    return ll


def arrabales(pts):
    """1898 sheet pixel -> [lon, lat]: the affine fit, then south of the seam the slide that ties the hand-drawn strip to today's streets
    (pipeline/georef/manila_arrabales_fit.py says why). The slide depends only on how far south the point is."""
    A = np.array(ARR['affine']); S = ARR['south']; ys = [S['seam_y']] + [k['y'] for k in S['slides']]; sl = [[0.0, 0.0]] + [k['slide_m'] for k in S['slides']]
    out = []
    for x, y in pts:
        e, n = A @ np.array([x, y, 1.0])
        e += float(np.interp(y, ys, [v[0] for v in sl])); n += float(np.interp(y, ys, [v[1] for v in sl]))
        out.append([round(ARR['lon0'] + e / ARR['kx'], 6), round(ARR['lat0'] + n / ARR['ky'], 6)])
    return out


def wark(pts):
    out = []
    for x, y in pts:
        la, lo = warking.px2ll(x, y); out.append([round(lo, 6), round(la, 6)])
    return out


def metres(a, b):
    return math.hypot((a[0] - b[0]) * 111320 * math.cos(math.radians(a[1])), (a[1] - b[1]) * 110574)


def join(line, to, keep='after'):
    """Slide a whole line so that the point of it nearest to `to` lands on `to`, and keep the part beyond that point.
    Returns the line (starting or ending at `to`) and how far it was moved, in metres."""
    best = None
    for i, (a, b) in enumerate(zip(line, line[1:])):
        vx, vy = b[0] - a[0], b[1] - a[1]; L = vx * vx + vy * vy or 1e-12
        f = max(0.0, min(1.0, ((to[0] - a[0]) * vx + (to[1] - a[1]) * vy) / L)); q = [a[0] + f * vx, a[1] + f * vy]; d = metres(q, to)
        if best is None or d < best[0]: best = (d, i, q)
    d, i, q = best; dx, dy = to[0] - q[0], to[1] - q[1]
    mv = lambda p: [round(p[0] + dx, 6), round(p[1] + dy, 6)]
    part = [list(to)] + [mv(p) for p in line[i + 1:]] if keep == 'after' else [mv(p) for p in line[:i + 1]] + [list(to)]
    return part, d


def build():
    H = haan(); feats = []; n = {}

    def add(layer, kind, geom, coords, source, method, conf, prec, basis, name=None, desc=None, **more):
        n[layer] = n.get(layer, 0) + 1
        p = {'id': 'MNL99-%s-%d' % (layer.upper(), n[layer]), 'layer': layer, 'kind': kind, 'name': name, 'desc': desc, 'from': FROM, 'to': TO, 'source_id': source,
             'method': method, 'confidence': conf, 'precision_m': prec, 'basis': basis, 'review': 'Needs review'}
        p.update(more); feats.append({'type': 'Feature', 'properties': {k: v for k, v in p.items() if v is not None}, 'geometry': {'type': geom, 'coordinates': coords}})

    B_H = 'Read from gridded crops of the engineer map (3,840-px copy), 3 to 6 scan px a pick (10-25 m).'
    B_W = 'Read from the Signal Corps map (full scan, crops at half size); placed by that map\'s own fit (about 170 m) and slid to meet the engineer map\'s line.'

    # ---- shoreline ----
    north = H(PICKS['shore_n']); south = H(PICKS['shore_s'])
    add('shore', 'shore', 'LineString', north, HAAN, 'traced', 'medium', 30, B_H, desc='Bay shore from the Vitas canal mouth to the north mole of the Pasig', part='Tondo and San Nicolas')
    add('shore', 'shore', 'LineString', south, HAAN, 'traced', 'medium', 25, B_H, desc='Bay shore from the south side of the Pasig mouth to Malate', part='Walled City, Ermita and Malate')
    wn, dn = join(wark(PICKS['wk_shore_n'])[::-1], north[0], 'before')      # north to south, ending at the Vitas canal
    B_S = ('Read from crops of "Manila y sus arrabales" (War Department, 1898; 4,551 x 7,118 scan) and checked by laying the picks back on the scan. Placed by that sheet\'s fit to the engineer map; '
           'south of Malate, where the sheet is a hand-drawn strip, slid to today\'s F. B. Harrison Street crossings as well (pipeline/georef/manila_arrabales_fit.py). The shore is that of 1898.')
    mid = arrabales(PICKS['arr_shore'])                       # Malate to Pasay, from the 1898 sheet
    ws, ds = join(wark(PICKS['wk_shore_s']), mid[-1])
    add('shore-outer', 'shore', 'LineString', wn, WARK, 'traced', 'low', 250, B_W + ' Slid %d m. The outer edge of the Dagat-Dagatan lagoons and the Navotas sand spit; the map is schematic here.' % dn,
        desc='Outer shore north of the Vitas canal, to the Navotas spit')
    add('shore-south', 'shore', 'LineString', [south[-1]] + mid, ARRAB, 'traced', 'low', 100, B_S, desc='Bay shore from Malate past the fort on the beach to Pasay')
    add('shore-outer', 'shore', 'LineString', ws, WARK, 'traced', 'low', 400, B_W + ' Slid %d m to meet the shore of the 1898 sheet west of Pasay.' % ds, desc='Bay shore south of Pasay, towards Paranaque')
    # the bay: everything west of the shore, closed well beyond the drawing
    print('joins: north shore moved %d m, south shore %d m' % (dn, ds))
    chain = wn[:-1] + north + south + mid + ws[1:]
    W_, S_, E_, N_ = SHEET
    sea = [[W_, N_], [chain[0][0], N_]] + chain + [[chain[-1][0], S_], [W_, S_]]
    add('sea', 'sea', 'Polygon', [sea + [sea[0]]], HAAN, 'interpolated', 'low', 250, 'The area west of the traced shoreline, out to the edge of the sheet. Its landward edge is the shore layers; the other edges are the sheet\'s.',
        name='Manila Bay')
    add('harbour', 'breakwater', 'LineString', H(PICKS['breakwater']), HAAN, 'traced', 'medium', 30, B_H, name='Jetty', desc='The long jetty south of the river mouth, from the light at its head')
    add('harbour', 'breakwater', 'LineString', H(PICKS['north_mole']), HAAN, 'traced', 'medium', 30, B_H, desc='North mole of the Pasig mouth')

    # ---- rivers ----
    B_A = 'The blue water tint of the engineer map, separated by colour inside the inked bank lines and vectorised (about 4 m a pixel); gaps under lettering closed and three leaks cut by hand.'
    pasig = H(PICKS['pasig'])
    add('pasig', 'river', 'Polygon', [pasig + [pasig[0]]], HAAN, 'AI-extracted', 'medium', 25, B_A + ' The island below Malacanang is left as land. The outline stops at the mole heads and at the sheet\'s south edge.', name='Pasig River')
    east_end = max(pasig, key=lambda p: p[0] - p[1])          # the south-east end, where the river leaves the sheet
    up, du = join(wark(PICKS['wk_pasig']), east_end)
    print('join: upper Pasig moved %d m, %d points kept' % (du, len(up)))
    add('pasig-upper', 'stream', 'LineString', up, WARK, 'traced', 'low', 250, B_W + ' Slid %d m. A centre line only: the width is taken from the engineer map where the two meet.' % du,
        name='Pasig River', desc='The Pasig above Santa Ana, past San Pedro Macati', width_m=110)
    add('sanjuan', 'stream', 'LineString', H(PICKS['sanjuan']), HAAN, 'traced', 'medium', 25, B_H + ' Centre line; the map draws it about 30 m wide.', name='San Juan River', width_m=30)
    for rings in PICKS['lagoons']:
        add('lagoons', 'water', 'Polygon', [(lambda r: r + [r[0]])(H(r)) for r in rings], HAAN, 'AI-extracted', 'low', 60,
            'The water tint north of Tondo, separated by colour and vectorised. Fish ponds, dykes and open water are not told apart, and the outline is cut where the tint fades.', desc='Lagoons and fish ponds behind the Tondo beach')
    for ring in PICKS['moat']:
        r = H(ring); add('moat', 'water', 'Polygon', [r + [r[0]]], HAAN, 'AI-extracted', 'medium', 25, 'The water tint around the walls, separated by colour and vectorised.', desc='Moat of the Walled City')

    # ---- the Walled City ----
    w = H(PICKS['walls'])
    add('walls', 'wall', 'Polygon', [w + [w[0]]], HAAN, 'traced', 'medium', 20, B_H + ' The main wall only, in 43 points: bastions, gates and outworks are simplified away. Today\'s streets inside fall on the map\'s to a few metres.',
        name='Intramuros', desc='Walls of the Walled City (Intramuros), main line')

    # ---- railway and roads ----
    add('rail', 'rail', 'LineString', H(PICKS['rail']), HAAN, 'traced', 'medium', 40, B_H + ' Tied across the track to today\'s line; the map is weaker north of blockhouse 1 (40-60 m).',
        name='Manila and Dagupan Railway', desc='Railway from the station in Tondo to Caloocan and north')
    R = [('road_caloocan', 'main', None, 'Road from Tondo to Caloocan', 40), ('road_malabon', 'main', 'Malabon Road', 'Road from Caloocan to Malabon', 60),
         ('road_azcarraga', 'main', 'Calle de Azcarraga', 'Paseo and Calle de Azcarraga, then Calle de Iris', 25), ('road_santamesa', 'main', 'Calle de Alix', 'Calle de Alix and the Santa Mesa road, over the San Juan bridge and on towards Mariquina', 25),
         ('road_reservoir', 'main', None, 'Road to the reservoir (El Deposito)', 25), ('road_laloma', 'main', None, 'Road to the Chinese Hospital and La Loma church', 50),
         ('road_bh3', 'minor', None, 'Road from the Chinese Hospital to blockhouse 3', 60), ('road_north', 'minor', None, 'Road north past Lico', 60),
         ('road_real_malate', 'main', None, 'Shore road through Ermita and Malate', 25), ('road_paco', 'main', None, 'Road from the Walled City to Paco', 25),
         ('road_santaana', 'main', None, 'Road from Paco to Santa Ana', 25), ('road_herran', 'minor', None, 'Road from Malate to the Paco bridge', 25), ('road_faura', 'minor', None, 'Road from the shore to the Paco cemetery', 25)]
    for key, cls, name, desc, prec in R:
        add('roads', 'road', 'LineString', H(PICKS[key]), HAAN, 'traced', 'low' if prec >= 50 else 'medium', prec, B_H + (' The name is lettered on the map.' if name else ' The map letters no name on it.'), name=name, desc=desc, **{'class': cls})

    # ---- blockhouses ----
    for num, px in PICKS['blockhouses'].items():
        weak = num in ('2', '3', '4', '5', '6')
        add('blockhouses', 'blockhouse', 'Point', H([px])[0], HAAN, 'traced', 'low' if weak else 'medium', 80 if weak else 40,
            'The blockhouse symbol on the engineer map.' + (' No control point lies near it: the place depends on the fit between Caloocan and Santa Mesa.' if weak else ''), name='Blockhouse %s' % num, number=int(num))

    # ---- the engineer map's own detail, taken from the scan by program (pipeline/recon/manila_1899_linework.py) ----
    inside = lambda q: SHEET[0] <= q[0] <= SHEET[2] and SHEET[1] <= q[1] <= SHEET[3]
    PARTS = [('Caloocan, La Loma, Lico and the country north of the city', 0, 0, 3840, 1150),
             ('Tondo, Binondo and Santa Cruz', 0, 1150, 1000, 1990), ('Quiapo, San Miguel and Sampaloc', 1000, 1150, 1500, 2110), ('Santa Mesa and Pandacan', 1500, 1150, 2130, 2110),
             ('San Juan del Monte, the reservoir and the road to the waterworks', 2130, 1150, 3840, 2110), ('The Walled City, Ermita and Malate', 0, 1990, 1000, 2847),
             ('Paco and the esteros south of the Pasig', 1000, 2110, 1600, 2847), ('Santa Ana and the Pasig bends', 1600, 2110, 3840, 2847)]
    part_of = lambda x, y: next(i for i, (_, x0, y0, x1, y1) in enumerate(PARTS) if x0 <= x < x1 and y0 <= y < y1)
    B_L = ('Every dark ink line of the engineer map inside this part of the sheet, separated from the scan by a program, thinned to centre lines and vectorised (about 2 m), then placed by '
           'the map\'s fit. Small separate marks (most lettering, the dots of trails, hedge rings) were dropped by size. Nobody has checked it line by line: it holds street and block edges, '
           'dykes, fences, banks and hachures, and also what the program cannot tell from them, such as letters that touch a line and field works drawn after 4 February.')
    groups = [[] for _ in PARTS]
    for line in DETAIL['lines']:
        ll = [q for q in H(line) if inside(q)]
        if len(ll) >= 2: groups[part_of(*line[len(line) // 2])].append(ll)
    for (name, *_), lines in zip(PARTS, groups):
        if lines: add('linework', 'detail', 'MultiLineString', lines, HAAN, 'AI-extracted', 'low', 30, B_L, desc='Streets, blocks, dykes and field lines: ' + name, part=name)
    B_E = ('The engineer map\'s blue water wash in this part of the sheet, separated by colour and vectorised by a program (about 3 m), less the water the hand-checked layers hold. '
           'Esteros, creeks and ponds are not told apart; a creek is cut where the wash fades or lettering covers it, and a few stains may be among them.')
    wgroups = [[] for _ in PARTS]
    for rings in DETAIL['water']:
        poly = [(lambda r: r + [r[0]])(H(r)) for r in rings]
        if all(inside(q) for q in poly[0]): wgroups[part_of(*rings[0][0])].append(poly)
    for (name, *_), polys in zip(PARTS, wgroups):
        if polys: add('esteros', 'water', 'MultiPolygon', polys, HAAN, 'AI-extracted', 'low', 30, B_E, desc='Esteros, creeks and ponds: ' + name, part=name)
    # ---- south of where the engineer map stops: the 1898 sheet ----
    edge = lambda q: 14.57325 - (q[0] - 120.98165) * 0.035            # the engineer map's south edge on the ground (14.5733 N at the shore, 14.5727 at Santa Ana)
    south_lines = []
    for line in DETAIL_S['lines']:
        ll = arrabales(line); mid_pt = ll[len(ll) // 2]
        ll = [q for q in ll if inside(q)]
        if len(ll) >= 2 and mid_pt[1] < edge(mid_pt) - 0.0001: south_lines.append(ll)
    add('linework-south', 'detail', 'MultiLineString', south_lines, ARRAB, 'AI-extracted', 'low', 100,
        'Every dark ink line of the 1898 sheet south of where the engineer map stops, separated from the scan by a program, thinned and vectorised, then placed as the shore of this layer\'s map is. '
        'It holds roads, field lines, the estero and marsh behind Malate, the old Spanish line of works by blockhouses 13 and 14, and the trenches the Americans dug in August 1898. Nobody has checked it line by line, '
        'and it is the ground of 1898, six months before the battle.', desc='Roads, field lines, marsh and old works: Malate, Singalong and the strip to Pasay', part='Malate to Pasay')
    add('roads-south', 'road', 'LineString', arrabales(PICKS['arr_road_real'][3:]), ARRAB, 'traced', 'low', 100, B_S + ' The road drawn as a double line nearest the shore; the sheet letters it "Calle Real" in Malate.',
        name='Calle Real', desc='Calle Real from the fort at Malate to the road to Pasay church', **{'class': 'main'})
    for num, px in PICKS['arr_blockhouses'].items():
        add('blockhouses-south', 'blockhouse', 'Point', arrabales([px])[0], ARRAB, 'traced', 'low', 120,
            'A work on the old Spanish line of the 1898 sheet with "%s" written beside it in pencil by an unknown hand; taken to be blockhouse %s. Placed as the shore of this map is.' % (num, num), name='Blockhouse %s' % num, number=int(num))
    # insurgent field works: the legend's "Insurg." mark (a row of humps), where the map draws it by blockhouses 1 and 2
    B_I = ('The legend\'s mark for insurgent works (a row of humps), read from a crop of the engineer map at three times its size, 3 to 5 scan px a pick. Short pieces only: the map '
           'shows them by blockhouses 1 and 2 and nowhere else on the sheet. Those south of the American line of 5 to 10 February were Filipino works facing the city before the battle.')
    for i, (line, desc) in enumerate(PICKS['insurgent_works']):
        add('works-ph', 'entrenchment', 'LineString', H(line), HAAN, 'traced', 'low', 80, B_I, desc=desc, side='PH')
    for x in feats:        # nothing is drawn beyond the sheet's edge
        g = x['geometry']
        if g['type'] == 'LineString':
            g['coordinates'] = [p for p in g['coordinates'] if SHEET[0] <= p[0] <= SHEET[2] and SHEET[1] <= p[1] <= SHEET[3]]
    return {'type': 'FeatureCollection', 'name': 'manila-1899', 'sheet': SHEET, 'title': 'Manila, February 1899: reconstructed base map (WarMapper)',
            'note': 'A WarMapper reconstruction, not a period map. Features were read from two 1899 Army maps; see pipeline/recon/manila_1899.py. [longitude, latitude], WGS 84.',
            'features': feats}


if __name__ == '__main__':
    if '--fit' in sys.argv:
        print('engineer map: %d control points, %d railway points, %d anchors; smoothing %g' % (FIT['n_real'], FIT['n_rail'], FIT['n_anchor'], FIT['smoothing']))
        print('residual %.1f m rms, %.1f m at worst; leaving each out in turn %.1f m rms' % (FIT['rms_m'], FIT['max_m'], FIT['loo_rms_m']))
        for r, e in zip(FIT['real'], FIT['loo_m']): print('  %-66s left out: %3d m' % (r[0], e))
        for c in FIT['check']: print('  check, not used: %-70s %5.1f m' % (c[0], c[5]))
        sys.exit(0)
    G = build(); os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('{"type":"FeatureCollection","name":%s,"title":%s,"note":%s,"sheet":%s,"features":[\n' % tuple(json.dumps(G[k]) for k in ('name', 'title', 'note', 'sheet')))
        f.write(',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in G['features'])); f.write('\n]}\n')
    by = {}
    for x in G['features']: by.setdefault(x['properties']['layer'], []).append(x)
    for k, v in by.items(): print('%-12s %2d feature(s)  %s  %s' % (k, len(v), v[0]['properties']['method'], '/'.join(sorted(set(x['properties']['confidence'] for x in v)))))
    lon = [p[0] for x in G['features'] if x['geometry']['type'] == 'LineString' for p in x['geometry']['coordinates']]; lat = [p[1] for x in G['features'] if x['geometry']['type'] == 'LineString' for p in x['geometry']['coordinates']]
    print('lines span %.4f to %.4f E, %.4f to %.4f N; %d features, %d bytes' % (min(lon), max(lon), min(lat), max(lat), len(G['features']), os.path.getsize(OUT)))
    for x in G['features']:
        if x['geometry']['type'].startswith('Multi'): print('  %-22s %5d parts  %s' % (x['properties']['id'], len(x['geometry']['coordinates']), x['properties']['part']))
