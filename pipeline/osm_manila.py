"""Cut data/osm/manila.txt from an Overpass export (raw OSM data, JSON, 'out geom').

  python3 -I pipeline/osm_manila.py <manila-osm.json> [<manila-coast.json>]

Morgan ran the query on overpass-turbo.eu on 21 Nov 2026 (roads, railways, waterways and water in 14.43-14.71 N, 120.87-121.06 E).
Kept: motorways and trunk roads (Hm), primary (Hp), secondary (Hs), tertiary (Ht), railways (Rr), rivers and canals (Wr), named
streams (Ws), and water bodies over 3 hectares (Fl). Lines are thinned to about 6 m.
The second file is the coastline (natural=coastline in 14.40-14.75 N, 120.85-121.06 E, downloaded the same day): its ways are joined
end to end into the shore of Manila Bay (Cs, open, land on the left as OpenStreetMap draws coastlines) and islands (Ci, closed).
Without a second file the shore lines already in data/osm/manila.txt are kept. One line per way, as in data/osm/gettysburg.txt:
code|name|lat,lon;dlat,dlon;...  in units of 0.00001 degree.
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (14.43, 120.87, 14.71, 121.06)
KY = 110574.0; KX = 111320.0 * math.cos(math.radians(14.58))
HW = {'motorway': 'Hm', 'trunk': 'Hm', 'primary': 'Hp', 'secondary': 'Hs', 'tertiary': 'Ht'}


def thin(pts, tol):
    """Douglas-Peucker, in metres."""
    if len(pts) < 3: return pts
    keep = [0, len(pts) - 1]; stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop(); ax, ay = pts[a][1] * KX, pts[a][0] * KY; bx, by = pts[b][1] * KX, pts[b][0] * KY
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1e-9; worst = 0; wi = None
        for i in range(a + 1, b):
            px, py = pts[i][1] * KX - ax, pts[i][0] * KY - ay
            d = abs(px * dy - py * dx) / L if L > 1e-6 else math.hypot(px, py)
            if d > worst: worst, wi = d, i
        if wi is not None and worst > tol: keep.append(wi); stack += [(a, wi), (wi, b)]
    return [pts[i] for i in sorted(keep)]


def area_ha(pts):
    s = 0
    for (la1, lo1), (la2, lo2) in zip(pts, pts[1:]): s += lo1 * KX * la2 * KY - lo2 * KX * la1 * KY
    return abs(s) / 2 / 1e4


def enc(pts, tol=6):
    q = [(round(la * 1e5), round(lo * 1e5)) for la, lo in thin(pts, tol)]; body = []; prev = None
    for p in q:
        if p == prev: continue
        body.append('%d,%d' % (p if prev is None else (p[0] - prev[0], p[1] - prev[1]))); prev = p
    return ';'.join(body) if len(body) > 1 else ''


def coast(src):
    """The coastline ways joined into chains: 'Cs' for an open one (the shore), 'Ci' for a closed one (an island)."""
    ways = [[(g['lat'], g['lon']) for g in e['geometry'] if g] for e in json.load(open(src, encoding='utf-8'))['elements']
            if e.get('type') == 'way' and e.get('geometry') and e.get('tags', {}).get('natural') == 'coastline']
    first = {w[0]: i for i, w in enumerate(ways)}; lasts = set(w[-1] for w in ways); used = [False] * len(ways); out = []
    order = [i for i, w in enumerate(ways) if w[0] not in lasts] + list(range(len(ways)))    # chains that begin nowhere first, then rings
    for i in order:
        if used[i]: continue
        c = list(ways[i]); used[i] = True
        while c[-1] != c[0] and c[-1] in first and not used[first[c[-1]]]:
            j = first[c[-1]]; used[j] = True; c += ways[j][1:]
        body = enc(c)
        if body: out.append('%s||%s' % ('Ci' if c[0] == c[-1] else 'Cs', body))
    return out


def main(src, coast_src=None):
    path = os.path.join(ROOT, 'data', 'osm', 'manila.txt')
    shore = coast(coast_src) if coast_src else [l.rstrip('\n') for l in open(path, encoding='utf-8') if l[:2] in ('Cs', 'Ci')]
    out = []
    for e in json.load(open(src, encoding='utf-8'))['elements']:
        if e.get('type') != 'way' or 'geometry' not in e: continue
        t = e.get('tags', {}); name = str(t.get('name', '')).replace('|', ' ').replace('\n', ' ')[:80]
        pts = [(g['lat'], g['lon']) for g in e['geometry'] if g]
        if len(pts) < 2: continue
        if t.get('highway') in HW: code = HW[t['highway']]
        elif t.get('railway') == 'rail': code = 'Rr'
        elif t.get('waterway') in ('river', 'canal'): code = 'Wr'
        elif t.get('waterway') == 'stream' and name: code = 'Ws'
        elif t.get('natural') == 'water' and pts[0] == pts[-1] and area_ha(pts) >= 3: code = 'Fl'
        else: continue
        if not any(BOX[0] <= la <= BOX[2] and BOX[1] <= lo <= BOX[3] for la, lo in pts): continue
        body = enc(pts)
        if body: out.append('%s|%s|%s' % (code, name, body))
    out = sorted(out) + sorted(shore)
    open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    import collections
    print(len(out), 'ways', os.path.getsize(path) // 1024, 'KB', dict(collections.Counter(l[:2] for l in out)))


if __name__ == '__main__':
    main(*sys.argv[1:3])
