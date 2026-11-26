"""26 Nov 2026, late morning: Morgan's third set of corrections to the South Carolina orientation.
  - Month by month (from 1780): a stop at the end of each month with a clash, with a bubble on each of its clashes, as the years before.
  - Where three or more bubbles are up, the stop lasts 5 seconds (years and months); otherwise 3.
  - 1777-1778: one box on the map, "Relative calm and little military activity on land in South Carolina", for 3 seconds; then the clock
    moves steadily to 1779 (2 seconds, as before).
  - The main roads are named on the map, as the rivers are: one label each, at the middle of the traced line, along its direction. The
    names are short forms of the traced roads' own names (from Mouzon 1775), marked approximate.
Safe to run again. Run: python3 pipeline/sc_orientation_month_bubbles_2026_11_26.py, then tools/export_battles.py and tools/build.py.
"""
import json, math, os
import openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
GEO = os.path.join(ROOT, 'data', 'recon', 'sc-1775.geojson')
PB = 'sc-orientation'
SHORT = {'SC75-ROAD-CHEROKEE-PATH': 'Cherokee Path', 'SC75-ROAD-CATAWBA-CHARLOTTE': 'Road to Charlotte',
         'SC75-ROAD-CHARLOTTE-CAMDEN': 'Road to Camden', 'SC75-ROAD-NINETYSIX-CONGAREES': 'Ninety Six Road',
         'SC75-ROAD-CAMDEN-NELSONS': "Road to Nelson's Ferry", 'SC75-ROAD-CAMDEN-CHERAWS': 'Road to the Cheraws',
         'SC75-ROAD-CONGAREES-ORANGEBURG': 'Road to Orangeburg', 'SC75-ROAD-ORANGEBURG': 'Orangeburg Road',
         'SC75-ROAD-ORANGEBURG-CHARLESTON': 'Road to Charleston', 'SC75-ROAD-KINGS-HIGHWAY-NE': "King's Highway",
         'SC75-ROAD-GEORGETOWN-SANTEE': 'Road to the Santee', 'SC75-ROAD-CHARLESTON-SAVANNAH': 'Road to Purrysburg',
         'SC75-ROAD-FORTMOORE-EAST': 'Road from Fort Moore'}

def label_point(c):
    """The middle of the line by length, and its direction there as the map's text angle (clockwise from east, kept readable)."""
    k = math.cos(math.radians(34)); seg = []; tot = 0
    for a, b in zip(c, c[1:]):
        d = math.hypot((b[0] - a[0]) * k, b[1] - a[1]); seg.append((a, b, d)); tot += d
    half = tot / 2; run = 0
    for a, b, d in seg:
        if run + d >= half:
            f = (half - run) / d if d else 0; x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            ang = math.degrees(math.atan2(-(b[1] - a[1]), (b[0] - a[0]) * k))
            if ang > 90: ang -= 180
            if ang < -90: ang += 180
            return round(y, 5), round(x, 5), round(ang)
        run += d

wb = openpyxl.load_workbook(WAR)
PS = wb['Playback settings']; h = [c.value for c in PS[1]]
for r in range(2, PS.max_row + 1):
    if PS.cell(r, 1).value == PB and PS.cell(r, 2).value == 'orientation.reveal':
        v = json.loads(PS.cell(r, 3).value)
        v.update({'months': True, 'many': 3, 'hold_many_seconds': 5,
                  'empty_text': 'Relative calm and little military activity on land in South Carolina in 1777-1778', 'empty_hold_seconds': 3})
        PS.cell(r, 3, json.dumps(v))
        PS.cell(r, h.index('what it does') + 1, "1775 to 1779 play a year at a time: all of a year's clashes grow into a large symbol, stop with a dated "
                "bubble on each, then shrink to their standard size. 1777-1778, with no clash, show one box (3 seconds) and are crossed in 2 seconds. "
                "From 1780, month by month, each month with a clash stops at its end with a bubble on each. A stop with three or more bubbles lasts "
                "5 seconds, otherwise 3.")
        PS.cell(r, h.index('why') + 1, "Morgan, 26 Nov 2026, three rounds the same morning: the year reveal; 1777-78 crossed in 2 seconds and no "
                "Continue; then bubbles month by month, 5 seconds for three or more, and one box for 1777-1778.")
LB = wb['Labels']; lh = [c.value for c in LB[1]]
for r in range(LB.max_row, 1, -1):
    if LB.cell(r, 1).value == PB and LB.cell(r, lh.index('kind') + 1).value == 'road': LB.delete_rows(r)
g = json.load(open(GEO))
for f in g['features']:
    fid = f['properties'].get('id')
    if fid in SHORT and f['geometry']['type'] == 'LineString':
        lat, lon, ang = label_point(f['geometry']['coordinates'])
        r = LB.max_row + 1
        for k, val in {'playback_id': PB, 'text': SHORT[fid], 'lat': lat, 'lon': lon, 'angle': ang, 'level': 0, 'kind': 'road', 'show': 'recon',
                       'approximate': 'yes'}.items():
            LB.cell(r, lh.index(k) + 1, val)
wb.save(WAR); print('done')
