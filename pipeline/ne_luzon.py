"""Cut data/osm/luzon1899.txt, the current-map drawing for the Luzon 1899 playback, from Natural Earth (public domain, 1:10m).

  python3 -I pipeline/ne_luzon.py <folder with the Natural Earth geojson files>

Files read (github.com/nvkelso/natural-earth-vector, geojson/, downloaded 21 Nov 2026): ne_10m_land, ne_10m_roads,
ne_10m_railroads, ne_10m_rivers_lake_centerlines, ne_10m_lakes. Kept inside 14.2-18.8 N, 119.6-122.7 E: land outlines cut to that
box (Ci, closed), major highways (Hm), secondary highways (Hp), other roads (Hs), railways (Rr), rivers (Wr) and lakes (Fl).
Natural Earth is drawn for small scales: lines are good to a few hundred metres, and it has few rivers (in this box, the Cagayan).
The format is that of data/osm/manila.txt: code|name|lat,lon;dlat,dlon;... in units of 0.00001 degree.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osm_manila as om
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, S, E, N = 119.6, 14.2, 122.7, 18.8
ROAD = {'Major Highway': 'Hm', 'Secondary Highway': 'Hp', 'Road': 'Hs', 'Beltway': 'Hm', 'Bypass': 'Hp'}


def box_clip(ring):
    """A closed ring of (lon, lat) cut to the box (Sutherland-Hodgman)."""
    for axis, lim, low in ((0, W, False), (0, E, True), (1, S, False), (1, N, True)):
        ins = (lambda p: p[axis] <= lim) if low else (lambda p: p[axis] >= lim); out = []
        for i, b in enumerate(ring):
            a = ring[i - 1]
            if ins(a) != ins(b):
                t = (lim - a[axis]) / (b[axis] - a[axis]); out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            if ins(b): out.append(b)
        ring = out
        if len(ring) < 3: return []
    return ring


def runs(line):
    """The parts of a line of (lon, lat) that lie inside the box."""
    cur = []; out = []
    for p in line:
        if W <= p[0] <= E and S <= p[1] <= N: cur.append(p)
        else:
            if len(cur) > 1: out.append(cur)
            cur = []
    if len(cur) > 1: out.append(cur)
    return out


def lines_of(g):
    t = g['type']; c = g['coordinates']
    return [c] if t == 'LineString' else c if t == 'MultiLineString' else [r for r in c] if t == 'Polygon' else [r for p in c for r in p]


def main(folder):
    def feats(name): return json.load(open(os.path.join(folder, name + '.geojson'), encoding='utf-8'))['features']
    out = []
    for f in feats('ne_10m_land'):
        g = f['geometry']
        for poly in ([g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']):
            ring = [(p[0], p[1]) for p in poly[0]]
            if not any(W <= x <= E and S <= y <= N for x, y in ring): continue
            cut = box_clip(ring[:-1] if ring[0] == ring[-1] else ring)
            if len(cut) < 3 or om.area_ha([(y, x) for x, y in cut] + [(cut[0][1], cut[0][0])]) < 400: continue      # islands under 4 sq km are left out
            body = om.enc([(y, x) for x, y in cut] + [(cut[0][1], cut[0][0])], 250)
            if body: out.append('Ci||' + body)
    for name, code_of in (('ne_10m_roads', lambda p: ROAD.get(p.get('type'))), ('ne_10m_railroads', lambda p: 'Rr'), ('ne_10m_rivers_lake_centerlines', lambda p: 'Wr')):
        for f in feats(name):
            code = code_of(f['properties']); g = f['geometry']
            if not code or not g: continue
            for ln in lines_of(g):
                for run in runs([(p[0], p[1]) for p in ln]):
                    body = om.enc([(y, x) for x, y in run], 120)
                    if body: out.append('%s|%s|%s' % (code, str(f['properties'].get('name') or '').replace('|', ' '), body))
    for f in feats('ne_10m_lakes'):
        g = f['geometry']
        for ring in lines_of(g)[:1]:
            if any(W <= p[0] <= E and S <= p[1] <= N for p in ring):
                body = om.enc([(p[1], p[0]) for p in ring], 150)
                if body: out.append('Fl|%s|%s' % (f['properties'].get('name') or '', body))
    out.sort(); path = os.path.join(ROOT, 'data', 'osm', 'luzon1899.txt')
    open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    import collections; print(len(out), 'lines', os.path.getsize(path) // 1024, 'KB', dict(collections.Counter(l[:2] for l in out)))


if __name__ == '__main__':
    main(sys.argv[1])
