"""The current map under each battle: today's roads, water, railways and woods, cut down from the OpenStreetMap extracts in data/osm/
and saved as data/base/<battle>.json (the "base" part of a battle file: docs/battle-file.md). Run it when an extract changes:

  python3 pipeline/basemaps.py            all three
  python3 pipeline/basemaps.py ypres      one

Each battle's extract was taken a little differently, so each has its own short reader here.
"""
import sys, os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline')); sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'georef'))
import battlefile as bf
CREDIT = '© OpenStreetMap contributors'


def gettysburg():
    """Cut exactly to the edge of the 1876 sheet, so the current map ends where the period map does and another map can lie around both. The cutting is done in the sheet's own pixels, then every point goes back to longitude and latitude."""
    import gettysburg_georef as g
    X0, Y0, X1, Y1 = 650, 1178, 7300, 8120; SC = 0.8
    CW, CH = round((X1 - X0) * SC), round((Y1 - Y0) * SC)
    def back(p): la, lo = g.px2ll(p[0] / SC + X0, p[1] / SC + Y0); return bf.ll(la, lo)
    def inside(p): return 0 <= p[0] <= CW and 0 <= p[1] <= CH
    def cut(a, b):
        """The part of the segment a-b that lies on the sheet, or None (Liang-Barsky)."""
        t0, t1 = 0.0, 1.0; dx, dy = b[0] - a[0], b[1] - a[1]
        for pp, q in ((-dx, a[0]), (dx, CW - a[0]), (-dy, a[1]), (dy, CH - a[1])):
            if pp == 0:
                if q < 0: return None
            else:
                r = q / pp
                if pp < 0: t0 = max(t0, r)
                else: t1 = min(t1, r)
        if t0 > t1: return None
        return (a[0] + dx * t0, a[1] + dy * t0), (a[0] + dx * t1, a[1] + dy * t1)
    def pieces(pts):
        """The runs of a line that lie on the sheet, each ending exactly at the sheet's edge where the line leaves it."""
        out = []; cur = []
        for a, b in zip(pts, pts[1:]):
            c = cut(a, b)
            if not c:
                if len(cur) > 1: out.append(cur)
                cur = []; continue
            if not cur or cur[-1] != c[0]:
                if len(cur) > 1: out.append(cur)
                cur = [c[0]]
            cur.append(c[1])
            if c[1] != b:          # left the sheet inside this segment
                out.append(cur); cur = []
        if len(cur) > 1: out.append(cur)
        return [c for c in out if sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(c, c[1:])) > 2]   # drop a corner clipped to almost nothing
    def trim(poly):
        """A wood or a lake cut to the sheet (Sutherland-Hodgman; the sheet is a plain box in its own pixels)."""
        for axis, lim, keep_low in ((0, 0, False), (0, CW, True), (1, 0, False), (1, CH, True)):
            ins = (lambda p: p[axis] <= lim) if keep_low else (lambda p: p[axis] >= lim)
            out = []
            for i, b in enumerate(poly):
                a = poly[i - 1]
                if ins(a) != ins(b):
                    t = (lim - a[axis]) / (b[axis] - a[axis]); out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                if ins(b): out.append(b)
            poly = out
            if len(poly) < 3: return []
        return poly
    def enc(pts): return bf.pack([back(p) for p in pts])
    ROAD = {'Hm': 'm', 'Hp': 'p', 'Hs': 's', 'Ht': 't', 'Hu': 'u', 'Hr': 'r', 'Hv': 'v'}
    lines = []; areas = []
    for ln in open(ROOT + '/data/osm/gettysburg.txt', encoding='utf-8'):
        code, name, body = ln.rstrip('\n').split('|', 2); la = lo = 0; pts = []
        for i, pr in enumerate(body.split(';')):
            a, b = pr.split(','); la, lo = (int(a), int(b)) if i == 0 else (la + int(a), lo + int(b))
            x, y = g.ll2px(la / 1e5, lo / 1e5); pts.append(((float(x) - X0) * SC, (float(y) - Y0) * SC))
        if code[0] == 'P': continue
        if code in ('Fw', 'Fl'):
            if pts[0] == pts[-1]: pts = pts[:-1]
            cutp = trim(pts)
            if len(cutp) >= 3: areas.append(['wood' if code == 'Fw' else 'water', name, enc(cutp + [cutp[0]])])
            continue
        for run in pieces(pts):
            if code in ROAD: lines.append(['road', ROAD[code], name, enc(run)])
            elif code == 'Rr': lines.append(['rail', '', name, enc(run)])
            elif code == 'Ra': continue
            else: lines.append(['water', 'river' if code == 'Wr' else 'stream', name, enc(run)])
    return {'credit': CREDIT, 'source': 'S39', 'lines': lines, 'areas': areas}


def trenton():
    import trenton_geo as geo
    lines = []
    for w in geo.load():
        kind = 'water' if w['zone'] == 'W' else 'road'
        lines.append([kind, 'river' if kind == 'water' else w['cls'], w['name'], bf.pack([bf.ll(a, b) for a, b in w['pts']])])
    return {'credit': CREDIT, 'source': 'S39', 'lines': lines, 'areas': [], 'widths': {'Delaware River': 270}}   # the Delaware is drawn 270 m wide


def ypres():
    LAT0, LON0 = 50.8522, 2.8846; KX = 111320 * math.cos(math.radians(LAT0)); KY = 111040
    def LL(x, y): return bf.ll(LAT0 - y / KY, LON0 + x / KX)   # metres east and south of the centre of Ypres -> [longitude, latitude]
    def XY(la, lo): return [(lo - LON0) * KX, -(la - LAT0) * KY]
    def dec(s):
        out = []; a = b = 0
        for i, t in enumerate(s.split(';')):
            x, y = t.split(','); x, y = int(x), int(y)
            a, b = (x, y) if i == 0 else (a + x, b + y)
            out.append(bf.ll(50 + a / 1e4, 2 + b / 1e4))
        return out
    KIND = {'w': 'water', 'm': 'road', 'r': 'road', 's': 'road'}
    lines, areas = [], []
    for l in open(ROOT + '/data/osm/ypres.txt', encoding='utf-8').read().split('\n'):
        if not l or l[0] == 'p': continue
        k, name, body = l.split('|')
        if k in 'wmrs': lines.append([KIND[k], ('river' if name in ('IJzer', 'Lys') else 'canal') if k == 'w' else k, name, bf.pack(dec(body))])
        elif k == 'f': areas.append(['wood', 'Ploegsteert Wood', bf.pack(dec(body))])
        elif k == 'b':   # a wood given only as a box: drawn as an oval over it
            a, b, c, d = [int(v) for v in body.split(',')]; p1 = XY(50 + a / 1e4, 2 + b / 1e4); p2 = XY(50 + c / 1e4, 2 + d / 1e4)
            cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2; rx, ry = abs(p2[0] - p1[0]) / 2, abs(p2[1] - p1[1]) / 2
            if name == 'Vrijbos': rx *= 1.9; ry *= 1.5   # the forest of 1914 was much larger than today's remnant
            pts = [LL(cx + rx * math.cos(t / 12 * math.pi), cy + ry * math.sin(t / 12 * math.pi)) for t in range(24)]
            areas.append(['wood', {'Vrijbos': 'Houthulst Forest', 'Polygoonbos': 'Polygon Wood', 'Nonnebossen': 'Nonne Bosschen'}[name], bf.pack(pts)])
    # the old Ypres-Comines canal is not a waterway in OpenStreetMap between Ypres and Houthem: drawn from memory, dashed
    lines.append(['former-water', 'canal', 'Former Ypres-Comines canal (approximate)', bf.pack([bf.ll(a, b) for a, b in ((50.8367, 2.8793), (50.8139, 2.9167), (50.811, 2.925), (50.803, 2.937), (50.7867, 2.9663))])])
    return {'credit': CREDIT, 'source': 'S39', 'lines': lines, 'areas': areas}


MAKE = {'gettysburg': gettysburg, 'trenton': trenton, 'ypres': ypres}
if __name__ == '__main__':
    for b in (sys.argv[1:] or list(MAKE)):
        base = MAKE[b](); path = '%s/data/base/%s.json' % (ROOT, b)
        json.dump(base, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(b, len(base['lines']), 'lines', len(base['areas']), 'areas', os.path.getsize(path) // 1024, 'KB')
