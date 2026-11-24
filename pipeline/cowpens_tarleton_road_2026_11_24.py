"""Cowpens: Tarleton's road between today's Green River Road and the old trace (24 Nov 2026, at Morgan's request).

Routes RC01 to RC06 (Tarleton's march in, the British escapes, Washington's pursuit) crossed the 900 m between the north-west end of
today's Green River Road and the east end of the park's trace in a straight line (gap CG06). They now follow the road the maps show:
north on a road of the 1959 USGS sheet (S108) that Landers (1928, S103) names "Green River Road", then west on Bearss's Mill Gap road
(S107), as data/recon/cowpens-1781.geojson draws them (features COW81-ROAD-GREENRIVER-N and COW81-ROAD-EAST). Only the waypoints of
that stretch change, and CP40, the column at about 06:28, which is placed "about 3.3 km by road from the field": it moves about 1 km up
today's Green River Road so it stays 3.3 km by the longer road, and RC01 starts there. It stops if RC01 no longer has the straight-line point.
"""
import json, math, os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cowpens_geo as G
from cowpens_audit_2026_11_24 import header, last_row, rows_by_id, setv, add_note, add_src

WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
SHARED = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
GUESS = (35.13132, -81.79743)                      # the one point of the straight line between the two
GRR_END, TRACE_END = (35.12294, -81.79050), (35.13162, -81.80223)
F = {f['properties']['id']: f['geometry']['coordinates'] for f in json.load(open(os.path.join(ROOT, 'data', 'recon', 'cowpens-1781.geojson')))['features']}


def road():
    """From the end of today's Green River Road to the end of the trace, a point every 30 m or so, both ends left out."""
    pts = [(p[1], p[0]) for p in F['COW81-ROAD-GREENRIVER-N'][::-1]] + [(p[1], p[0]) for p in F['COW81-ROAD-EAST'][::-1]]
    out = [GRR_END]
    for p in pts[1:]:
        if dist(out[-1], p) >= 30 and dist(p, TRACE_END) >= 15: out.append((round(p[0], 5), round(p[1], 5)))
    return out[1:]


def dist(a, b): a, b = G._xy(a), G._xy(b); return math.hypot(b[0] - a[0], b[1] - a[1])


def cut(pts, m):
    """The route from `m` metres along it: its first point moved up the road."""
    for i in range(len(pts) - 1):
        d = dist(pts[i], pts[i + 1])
        if m <= d:
            f = m / d; p = (round(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, 5), round(pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f, 5))
            return [p] + pts[i + 1:]
        m -= d


def length(pts): return sum(math.hypot(G._xy(b)[0] - G._xy(a)[0], G._xy(b)[1] - G._xy(a)[1]) for a, b in zip(pts, pts[1:]))


def main():
    wb = openpyxl.load_workbook(WAR); ws = wb['Routes']; ids = rows_by_id(ws); h = header(ws)
    col = h.index('waypoints (lat, lon; ...)') + 1; mid = road()
    for rid in ('RC01', 'RC02', 'RC03', 'RC04', 'RC05', 'RC06'):
        r = ids[rid]; pts = [tuple(float(v) for v in q.split(',')) for q in ws.cell(r, col).value.split(';')]
        k = pts.index(GUESS); assert rid != 'RC01' or k
        before, after = pts[k - 1], pts[k + 1]
        seg = mid if before == GRR_END else mid[::-1]
        assert {before, after} == {GRR_END, TRACE_END}, (rid, before, after)
        new = pts[:k] + seg + pts[k + 1:]
        if rid == 'RC01':     # CP40 is placed "about 3.3 km by road from the field": keep that, by the longer road
            new = cut(new, length(new) - length(pts)); start = new[0]
        print('%s: %d -> %d waypoints, %.0f -> %.0f m' % (rid, len(pts), len(new), length(pts), length(new)))
        ws.cell(r, col).value = '; '.join('%.5f, %.5f' % p for p in new)
        setv(ws, r, 'notes', lambda v: v.replace("a straight guess across to the east end of the old trace at the park's east trailhead",
                                                 "north on the road the 1959 USGS sheet shows there (S108; Landers's \"Green River Road\", S103) to Bearss's Mill Gap road, west along it to the east end of the old trace (S107)")
                                         + ' 24 Nov 2026, at Morgan\'s request: the 900 m that were a straight line now follow that road, as the reconstructed map draws it (gap CG06).')
        setv(ws, r, 'source_ids', add_src('S107', 'S108', 'S103'))
    ps = wb['Positions']; pids = rows_by_id(ps)
    setv(ps, pids['CP40'], 'lat', start[0]); setv(ps, pids['CP40'], 'lon', start[1])
    setv(ps, pids['CP40'], 'coordinate_basis', lambda v: v.replace('The modern road is taken as the old one (CG06).',
         'The modern road is taken as the old one, and then the road the maps show to the old trace (CG06).')
         + ' 24 Nov 2026: moved about 1 km up today\'s Green River Road, to stay about 3.3 km by road from the field now that the road runs by the maps (a bend north and west) and not in a straight line.')
    setv(ps, pids['CP40'], 'source_ids', add_src('S107', 'S108'))
    gp = wb['Gaps']; gids = rows_by_id(gp)
    setv(gp, gids['CG06'], 'status in v2', 'Partly closed, 24 Nov 2026: at Morgan\'s request routes RC01 to RC06 follow the road the maps show (a road of 1959 north, then Bearss\'s Mill Gap road west), rated low. Still open: no source of 1781 names that road, and the column\'s place at 06:20 is an estimate.')
    wb['Read me'].append(['Tarleton\'s road (24 Nov 2026)', 'Routes RC01 to RC06 follow the road the maps show between today\'s Green River Road and the old trace, in place of a straight line; CG06 partly closed. Written by pipeline/cowpens_tarleton_road_2026_11_24.py.'])
    sh = openpyxl.load_workbook(SHARED); rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026 (later still): Tarleton\'s road at Cowpens')
    rm.cell(2, 1, 'Revolutionary War.xlsx: at Morgan\'s request, routes RC01 to RC06 (Tarleton\'s march in, the British escapes, Washington\'s pursuit) leave the straight line across the 900 m between today\'s Green River Road and the old trace, '
                  'and follow the road the maps show there: north on a road of the 1959 USGS sheet (S108) that Landers (1928, S103) calls "Green River Road", then west on Bearss\'s Mill Gap road (S107). CP40 moves about 1 km up the road so it stays 3.3 km by road from the field. Gap CG06 partly closed. Written by pipeline/cowpens_tarleton_road_2026_11_24.py.')
    wb.save(WAR); sh.save(SHARED)


if __name__ == '__main__':
    main()
