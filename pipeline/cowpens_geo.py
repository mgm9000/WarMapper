"""The ground at the Cowpens, for placing units: the Historic Green River Road as OpenStreetMap draws it, and a way to say
"so many metres up the road from where Tarleton came onto the field, so many metres to one side of it".

The sources give distances, not coordinates: lines so many yards apart, "about 100 yards" to the rear, a flank on the head of a ravine.
The one line on today's ground that every account is tied to is the road, which still runs through the battlefield as a gravel trace.
So every position is measured from one point on it, the south-east end of the Battlefield Trail loop (35.13294, -81.81012), where the
staff ride handbook's Vantage 6 and the NPS wayside "The British Army" put the head of Tarleton's column as it came out of the woods.

  at(a, off)        a point: `a` metres up the road (north-west) from that point, `off` metres to the south-west of the road (the
                    American right, the British left); a negative `off` is to the north-east. Lines are laid square to the road there.
  line(a, o1, o2)   the two ends of a line across the road at `a`, from `o1` to `o2`
  along(a1, a2)     the road itself between two distances, as waypoints
"""
import math

# Historic Green River Road, south-east to north-west (data/osm/cowpens.txt; OpenStreetMap, 24 Nov 2026 UTC, thinned to 3 m)
ROAD = [(35.13162, -81.80223), (35.13150, -81.80482), (35.13159, -81.80547), (35.13197, -81.80699), (35.13252, -81.80891),
        (35.13294, -81.81012), (35.13407, -81.81274), (35.13449, -81.81357), (35.13513, -81.81438), (35.13584, -81.81513),
        (35.14100, -81.81881), (35.14175, -81.81967), (35.14218, -81.82024), (35.14231, -81.82041), (35.14241, -81.82069)]
ZERO = 5                                    # the index of the trail end: the point distances are counted from
KY = 110940.0; KX = 111320.0 * math.cos(math.radians(35.135))


def _xy(p): return (p[1] * KX, p[0] * KY)
def _ll(x, y): return (round(y / KY, 6), round(x / KX, 6))


_XY = [_xy(p) for p in ROAD]
_CUM = [0.0]
for _a, _b in zip(_XY, _XY[1:]): _CUM.append(_CUM[-1] + math.hypot(_b[0] - _a[0], _b[1] - _a[1]))
_Z = _CUM[ZERO]
EAST = -_Z                                  # the east end of the trace, as a distance from the zero point


def _on(a):
    """The point on the road `a` metres up it from the zero point (a straight run on past either end)."""
    d = a + _Z
    for i in range(len(_XY) - 1):
        if d <= _CUM[i + 1] or i == len(_XY) - 2:
            if d < _CUM[i] and i > 0: continue
            f = (d - _CUM[i]) / (_CUM[i + 1] - _CUM[i]); p, q = _XY[i], _XY[i + 1]
            return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)
    return _XY[-1]


def _dir(a, reach=45):
    """Which way the road runs at `a`: from `reach` metres behind to `reach` metres ahead, so a line square to it does not swing at a bend."""
    p, q = _on(a - reach), _on(a + reach); n = math.hypot(q[0] - p[0], q[1] - p[1])
    return ((q[0] - p[0]) / n, (q[1] - p[1]) / n)


def at(a, off=0.0):
    x, y = _on(a); ux, uy = _dir(a)
    return _ll(x - uy * off, y + ux * off)           # the left of a walker heading north-west is the south-west side


def line(a, o1, o2): return at(a, o1), at(a, o2)


def along(a1, a2, step=60):
    """The road between two distances, as waypoints (every bend, and no gap longer than `step`)."""
    lo, hi = min(a1, a2), max(a1, a2)
    ds = sorted(set([lo, hi] + [c - _Z for c in _CUM if lo < c - _Z < hi]))
    out = []
    for d0, d1 in zip(ds, ds[1:]):
        n = max(1, int((d1 - d0) // step)); out += [d0 + (d1 - d0) * k / n for k in range(n)]
    out.append(hi)
    pts = [at(d) for d in out]
    return pts if a1 <= a2 else pts[::-1]


def bearing(a):
    ux, uy = _dir(a); return (math.degrees(math.atan2(ux, uy)) + 360) % 360


if __name__ == '__main__':
    for a in (-200, 0, 70, 205, 330, 480, 565, 1010): print(a, at(a), round(bearing(a)), line(a, -100, 100))
