"""The ground at Guilford Courthouse, for placing units: Charles Hatch's five troop movement plans (National Park Service, 1971; S138),
read in the pixels of each plate and laid on the ground by the park boundary he draws.

How the plates were read. Each plan is a page of the Internet Archive's scan (guilfordcourthou00hatc, leaves n208 to n216), turned so north
is up and reduced to 2,160 by 1,600 pixels (page pixels times 1600/2601). The five plates share one base drawing but sit a little differently
on their pages, so each is first brought onto plate 1 by the four corners of its heavy border (BORDER below), then plate 1 is laid on the
ground by five points of the park boundary of 1971 that today's boundary still has, as the USGS Topo base map draws it (CONTROL below):
the north-east and south-east corners, the two ends of the half-circle on the south side, and the north-west corner. Fitted by turning,
scaling and shifting only, the five points lie 4 to 23 m from their places (pipeline/georef/guilford_hatch_fit.json).

What that is worth. Boundaries fit to about 15 m. Hatch's own creeks and road are sketched: his Hunting Creek crosses the road about 70 m east
of where the USGS draws Richland Creek today, and his road lies up to 70 m south of today's New Garden Road west of the park. A unit read off
a plate is therefore good to about 75 m on the ground, and no better than Hatch's own judgement of where it stood.

  hp(plate, x, y)       a point on plate `plate` (1 to 5), in that plate's pixels -> (lat, lon)
  gp(plate, ix, iy)     the same from the gridded working views (pixels of a view cut at (180, 150) and reduced to 0.9)
  hl(plate, a, b)       a line: two such points -> ((lat, lon), (lat, lon))
"""
import math, json, os

# top-left, top-right, bottom-right, bottom-left corners of each plate's border, in that plate's own pixels
# (outer edge of the heavy line: rows read in the bands x 400-700 and 1500-1800, columns in the bands y 300-600 and 1000-1300)
BORDER = {1: dict(top=(103, 90), bottom=(1473, 1455), left=(100, 106), right=(2041, 2050)),
          2: dict(top=(84, 82), bottom=(1456, 1450), left=(118, 118), right=(2062, 2065)),
          3: dict(top=(80, 72), bottom=(1449, 1440), left=(89, 92), right=(2033, 2039)),
          4: dict(top=(76, 76), bottom=(1446, 1442), left=(99, 96), right=(2043, 2045)),
          5: dict(top=(85, 85), bottom=(1458, 1455), left=(135, 132), right=(2081, 2082))}
# plate 1 pixels -> pixels of the USGS Topo base map at zoom 16 (tile origin x 18227, y 25702), then to longitude and latitude
CONTROL = [((1860, 421), (2034, 667), 'north-east corner of the park'), ((1871, 659), (2037, 824), 'south-east corner, on Orman Road'),
           ((1373, 818), (1669.5, 954), 'west end of the half-circle on the south boundary'), ((1459, 820), (1730, 954), 'east end of the half-circle'),
           ((1005, 457), (1386, 686), 'north-west corner, at Old Battleground Road')]
Z, X0, Y0 = 16, 18227, 25702


def _line(p, q):
    """a, b, c of the line a x + b y = c through two points"""
    a, b = q[1] - p[1], p[0] - q[0]
    return a, b, a * p[0] + b * p[1]


def _meet(l1, l2):
    d = l1[0] * l2[1] - l2[0] * l1[1]
    return ((l1[2] * l2[1] - l2[2] * l1[1]) / d, (l1[0] * l2[2] - l2[0] * l1[2]) / d)


def corners(n):
    b = BORDER[n]
    top = _line((550, b['top'][0]), (1650, b['top'][1])); bot = _line((550, b['bottom'][0]), (1650, b['bottom'][1]))
    lef = _line((b['left'][0], 450), (b['left'][1], 1150)); rig = _line((b['right'][0], 450), (b['right'][1], 1150))
    return [_meet(top, lef), _meet(top, rig), _meet(bot, rig), _meet(bot, lef)]


def _sim(src, dst):
    """Least-squares turn, scale and shift taking src onto dst (no numpy: closed form)."""
    n = len(src); mx = sum(p[0] for p in src) / n; my = sum(p[1] for p in src) / n; ux = sum(p[0] for p in dst) / n; uy = sum(p[1] for p in dst) / n
    sxx = sum((p[0] - mx) ** 2 + (p[1] - my) ** 2 for p in src)
    a = sum((p[0] - mx) * (q[0] - ux) + (p[1] - my) * (q[1] - uy) for p, q in zip(src, dst)) / sxx
    b = sum((p[0] - mx) * (q[1] - uy) - (p[1] - my) * (q[0] - ux) for p, q in zip(src, dst)) / sxx
    return a, b, ux - (a * mx - b * my), uy - (b * mx + a * my)


def _ap(t, x, y): return (t[0] * x - t[1] * y + t[2], t[1] * x + t[0] * y + t[3])


TO1 = {n: _sim(corners(n), corners(1)) for n in BORDER}
GROUND = _sim([c[0] for c in CONTROL], [c[1] for c in CONTROL])


def _ll(u, v):
    n = 2 ** Z; x = X0 + u / 256.0; y = Y0 + v / 256.0
    return (round(math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n)))), 6), round(x / n * 360 - 180, 6))


def hp(plate, x, y):
    x1, y1 = _ap(TO1[plate], x, y)
    return _ll(*_ap(GROUND, x1, y1))


def gp(plate, ix, iy): return hp(plate, 180 + ix / 0.9, 150 + iy / 0.9)
def hl(plate, a, b): return (gp(plate, *a), gp(plate, *b))


def topo(u, v):
    """A point read off the USGS Topo base map at zoom 16, in the pixels of the mosaic used for the fit -> (lat, lon)."""
    return _ll(u, v)


def metres(a, b):
    ky = 110950.0; kx = 111320.0 * math.cos(math.radians(36.13))
    return math.hypot((a[0] - b[0]) * ky, (a[1] - b[1]) * kx)


def report():
    m = 156543.03392 * math.cos(math.radians(36.13)) / 2 ** Z
    out = dict(what='Hatch (1971) plates 1 to 5 laid on the ground by the park boundary', topo_zoom=Z, topo_origin=[X0, Y0],
               plate1_to_topo=dict(a=GROUND[0], b=GROUND[1], tx=GROUND[2], ty=GROUND[3]),
               m_per_plate_px=round(math.hypot(GROUND[0], GROUND[1]) * m, 4), turn_deg=round(math.degrees(math.atan2(GROUND[1], GROUND[0])), 3),
               control=[dict(plate1=c[0], topo=c[1], what=c[2], off_m=round(math.hypot(*[p - q for p, q in zip(_ap(GROUND, *c[0]), c[1])]) * m, 1)) for c in CONTROL],
               plates={n: dict(border=[[round(v, 1) for v in c] for c in corners(n)], to_plate1=[round(v, 6) for v in TO1[n]]) for n in BORDER},
               checks=dict(note='Hatch\'s own features against today\'s survey (USGS Topo): his Hunting Creek at the road lies about 70 m east of Richland Creek; '
                                'his road at the park\'s west boundary of 1971 about 70 m south of today\'s New Garden Road.'))
    return out


if __name__ == '__main__':
    r = report(); print(json.dumps(r, indent=1)[:1500])
    for n, pt in ((1, (1745, 462)), (2, (1769, 452)), (3, (1741, 444))): print('courthouse on plate', n, hp(n, *pt))
    json.dump(r, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'georef', 'guilford_hatch_fit.json'), 'w'), indent=1)
