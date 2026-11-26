"""Guilford Courthouse, March 1781: the reconstructed base map's features, to data/recon/guilford-1781.geojson.

  python3 -I pipeline/recon/guilford_1781.py        writes data/recon/guilford-1781.geojson and prints what it wrote

What this is. A WarMapper reconstruction, not a period map. Inside the battlefield the lines are the ground as Charles Hatch drew it for the
National Park Service in 1971 on his five troop movement plans (S138): the Great Salisbury (New Garden) road, the Reedy Fork road, Hunting and
Little Horsepen creeks, the vales, the fences round the fields, the courthouse and the houses. They were picked by eye from the plates and laid
on the ground by the park boundary (pipeline/guilford_geo.py), so they carry Hatch's own judgement and about 75 m of doubt, and they are the
same lines his unit symbols stand on. West of his sheet, to New Garden Meeting House, the road is the road of the US Geological Survey's 1951
sheets (S146), picked from the sheets reprojected to WGS 84: a road of 1951 on the line of the great road, not a survey of 1781.
Nothing here has been checked by a historian.

How it was checked. Hatch's park boundary, fitted, lies 4 to 23 m from today's. His Hunting Creek crosses the road about 70 m east of where the
USGS draws Richland Creek today, and his road at the west edge of the old park about 70 m south of today's New Garden Road: so the creeks and
fences are `low`, the road `low` to `medium` only where the park still keeps its trace.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import guilford_geo as G

OUT = os.path.join(ROOT, 'data', 'recon', 'guilford-1781.geojson')
SHEET = [-79.9050, 36.0720, -79.8250, 36.1420]          # west, south, east, north: the south margin, below New Garden, has no roads traced and carries the sheet's title
DAY = '1781-03-15'
Q51 = (-79.905, 36.1255, 0.06 / 1686, 0.0425 / 1473)   # the 1951 sheets reprojected: west, north, degrees of longitude and of latitude a pixel


def q51(pts): return [[round(Q51[0] + x * Q51[2], 6), round(Q51[1] - y * Q51[3], 6)] for x, y in pts]
def p1(pts): return [[b, a] for a, b in (G.hp(1, x, y) for x, y in pts)]          # plate 1 pixels -> [lon, lat]
def g2(pts): return [[b, a] for a, b in (G.gp(2, x, y) for x, y in pts)]          # the gridded view of plate 2 -> [lon, lat]


# ---- Hatch, plate 1 (pixels of the plate turned north-up, 2,160 wide)
ROAD_E = [(855, 772), (900, 745), (1000, 705), (1100, 650), (1200, 580), (1260, 540), (1300, 507), (1350, 497), (1400, 497), (1500, 510), (1560, 514), (1605, 500), (1650, 490),
          (1687, 481), (1760, 478), (1830, 468), (1900, 455), (2000, 448)]
REEDY = [(1687, 481), (1676, 445), (1655, 385), (1642, 330), (1648, 250), (1641, 180), (1636, 112)]
HUNTING = [(1535, 255), (1572, 330), (1594, 400), (1603, 460), (1607, 500), (1624, 560), (1640, 612), (1650, 700), (1662, 790)]
VALE_N = [(1045, 262), (1110, 350), (1180, 442), (1240, 490), (1268, 506)]
RAVINE = [(1290, 512), (1250, 560), (1200, 640), (1130, 690), (1085, 755), (1055, 845)]
# ---- Hatch, plate 2 (pixels of the gridded working view)
ROAD_W = [(0, 632), (60, 640), (97, 648), (160, 640), (230, 620), (300, 600), (360, 578), (430, 560), (500, 545), (553, 538), (600, 528)]
HORSEPEN = [(62, 505), (80, 560), (92, 610), (97, 648), (110, 680), (128, 700), (150, 740), (185, 820), (195, 850)]
VALE_W = [(80, 540), (150, 510), (200, 480), (250, 400), (275, 320)]
VALE_S = [(128, 700), (200, 800), (260, 840), (330, 870), (410, 905)]
FIELDS = [('the fenced fields north of the road, in front of the first line', [(385, 435), (520, 405), (548, 505), (408, 540), (385, 435)]),
          ('the western fenced field north of the road', [(335, 470), (385, 460), (408, 540), (350, 560), (335, 470)]),
          ('the fields south of the road, "previously planted in corn"', [(330, 590), (560, 548), (590, 650), (350, 705), (330, 590)]),
          ('the fence dividing the corn fields', [(445, 568), (470, 678)]),
          ('the southern field in front of the first line', [(500, 773), (610, 755), (640, 830), (520, 855), (500, 773)]),
          ('the old fields with hedge rows north-west of the third line', [(915, 120), (975, 78), (1065, 200), (1000, 245), (915, 120)]),
          ('the open fields with hedge rows south of the road, west of Hunting Creek', [(1060, 345), (1185, 320), (1225, 460), (1115, 490), (1060, 345)]),
          ('the open fields with hedge rows further south', [(1115, 490), (1345, 435), (1362, 545), (1140, 600), (1115, 490)]),
          ('the open field about the courthouse', [(1305, 210), (1410, 190), (1492, 176), (1545, 455), (1320, 462), (1305, 210)])]
HOUSES = [('Guilford Courthouse', (1430, 272)), ('house across the road from the courthouse', (1435, 327)), ('house south of the courthouse', (1410, 352)), ('outbuilding', (1395, 360)),
          ('house west of Hunting Creek', (1259, 360)), ('building at the Reedy Fork road', (1355, 287)), ('Hoskins house', (318, 662)), ('Hoskins outbuilding', (309, 659))]
# ---- the 1951 sheets (pixels of the reprojected grid)
APPROACH = [(1215, 10), (1180, 50), (1140, 90), (1090, 140), (1040, 190), (990, 235), (940, 280), (850, 300), (790, 310), (740, 360), (700, 420), (640, 520), (610, 610), (560, 660),
            (520, 690), (478, 720), (440, 790), (395, 850), (370, 905), (372, 960), (385, 1040), (400, 1100), (425, 1165), (440, 1232)]
SALISBURY_SW = [(440, 1232), (400, 1236), (330, 1262), (220, 1300), (140, 1325), (40, 1300)]
BALLINGER = [(370, 905), (300, 895), (230, 900), (150, 905), (30, 925)]
HORSEPEN_MAIN = [(1265, 395), (1205, 385), (1140, 290), (1090, 225), (1010, 232), (940, 262), (850, 280), (700, 260), (560, 180), (480, 60)]


def square(c, half=6):
    la, lo = c; dy = half / 110950.0; dx = half / (111320.0 * 0.8077)
    return [[round(lo - dx, 6), round(la - dy, 6)], [round(lo + dx, 6), round(la - dy, 6)], [round(lo + dx, 6), round(la + dy, 6)], [round(lo - dx, 6), round(la + dy, 6)], [round(lo - dx, 6), round(la - dy, 6)]]


def feat(fid, layer, kind, desc, coords, src, conf, prec, basis, **more):
    p = dict(id=fid, layer=layer, kind=kind, desc=desc, source_id=src, method='traced', confidence=conf, precision_m=prec, basis=basis, review='Needs review', **{'from': DAY, 'to': DAY})
    p.update(more)
    return dict(type='Feature', properties=p, geometry=dict(type='LineString', coordinates=coords))


def build():
    F = []
    HB = 'Picked by eye from Hatch\'s plate %s (S138) and laid on the ground by the park boundary (pipeline/guilford_geo.py). '
    west = g2(ROAD_W); east = p1(ROAD_E)
    F.append(feat('GUI81-ROAD-FIELD', 'road-field', 'road', 'The Great Salisbury road (New Garden road) across the battlefield', west + east, 'S138', 'low', 75,
                  HB % '1 and 2' + 'West of the old park his road lies about 70 m south of today\'s New Garden Road; inside the park it runs near the trace the park keeps as the Historic New Garden Road.',
                  name='Great Salisbury road', **{'class': 'main'}))
    F.append(feat('GUI81-ROAD-REEDY', 'road-field', 'road', 'The Reedy Fork road, north from the courthouse (Greene\'s line of retreat)', p1(REEDY), 'S138', 'low', 75, HB % '1' + 'Greene: "We retreated in good order to the Reedy-fork river" (S140).',
                  name='Reedy Fork road', **{'class': 'main'}))
    ap = q51(APPROACH)[::-1]
    F.append(feat('GUI81-ROAD-APPROACH', 'road-approach', 'road', 'The great road from New Garden Meeting House to Little Horsepen Creek', ap + [west[0]], 'S146', 'low', 150,
                  'New Garden Road as the US Geological Survey drew it in 1951 (S146), before the suburbs, picked from the sheets reprojected to WGS 84; the last 300 m is a straight join to Hatch\'s road. '
                  'A road of 1951 on the line of the great road (S138, p. 30; S144, p. 73), not a survey of 1781.', name='Great Salisbury road', **{'class': 'main'}))
    F.append(feat('GUI81-ROAD-SW', 'road-approach', 'road', 'The great road south-west of New Garden, towards Deep River', q51(SALISBURY_SW), 'S146', 'low', 300,
                  'The main road west from Guilford College on the 1951 sheet (S146). Which road of 1781 Cornwallis\'s column came by is not established here: Lee has the meeting house "near the point where the road from Deep River intersects the great road" (S141).',
                  name='road from Deep River'))
    F.append(feat('GUI81-ROAD-BALLINGER', 'road-approach', 'road', 'The cross road at New Garden (Ballinger Road)', q51(BALLINGER), 'S146', 'low', 300,
                  'Ballinger Road on the 1951 sheet (S146). The staff ride puts the last of the morning\'s fights at "the Ballenger and Great Salisbury Cross Roads" (S144, p. 74).', name='cross road'))
    F.append(feat('GUI81-HUNTING', 'streams', 'stream', 'Hunting Creek (Richland Creek today)', p1(HUNTING), 'S138', 'low', 75, HB % '1' + 'The USGS draws Richland Creek about 70 m west of this line at the road.', name='Hunting Creek'))
    F.append(feat('GUI81-HORSEPEN', 'streams', 'stream', 'Little Horsepen Creek, where the British column crossed and deployed', g2(HORSEPEN), 'S138', 'low', 75, HB % '2', name='Little Horsepen Creek'))
    F.append(feat('GUI81-HORSEPEN-MAIN', 'streams', 'stream', 'Horsepen Creek, west of the battlefield', q51(HORSEPEN_MAIN), 'S146', 'low', 150, 'The stream of the 1951 sheet (S146).', name='Horsepen Creek'))
    for fid, desc, pts, plate in (('GUI81-VALE-N', 'The vale in front of the third line', VALE_N, 1), ('GUI81-RAVINE', 'The ravine south of the road', RAVINE, 1)):
        F.append(feat(fid, 'streams', 'stream', desc, p1(pts), 'S138', 'low', 75, HB % '1' + 'Hatch draws it as a vale; whether water ran in it in March 1781 is not said.'))
    for fid, desc, pts in (('GUI81-VALE-W', 'The vale north of the British left', VALE_W), ('GUI81-VALE-S', 'The vale south of the British right', VALE_S)):
        F.append(feat(fid, 'streams', 'stream', desc, g2(pts), 'S138', 'low', 75, HB % '2'))
    for i, (desc, pts) in enumerate(FIELDS, 1):
        F.append(feat('GUI81-FENCE-%d' % i, 'fences', 'detail', 'Fence: ' + desc, g2(pts), 'S138', 'low', 75,
                      HB % '2' + 'Hatch\'s "cultivated or open field enclosures (all other woods)", which he rests on the British plan of 1781 and on Cornwallis\'s and Greene\'s descriptions (S138, pp. 30-32).'))
    for i, (desc, pt) in enumerate(HOUSES, 1):
        c = G.gp(2, *pt)
        F.append(feat('GUI81-HOUSE-%d' % i, 'houses', 'detail', desc, square(c), 'S138', 'low', 75, HB % '2' + 'A building Hatch marks; drawn as a small square, not to its size.', name=desc if i in (1, 7) else None))
    return F


def main():
    F = build()
    fc = dict(type='FeatureCollection', name='guilford-1781', title='Guilford Courthouse, March 1781: a WarMapper reconstruction',
              note='Written by pipeline/recon/guilford_1781.py. Every feature carries its source, method, confidence and dates.', sheet=SHEET, features=F)
    json.dump(fc, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    kinds = {}
    for f in F: kinds[f['properties']['layer']] = kinds.get(f['properties']['layer'], 0) + 1
    print('wrote', OUT, len(F), 'features', kinds)
    print('join: 1951 road ends', F[2]['geometry']['coordinates'][-2], 'Hatch road starts', F[2]['geometry']['coordinates'][-1])


if __name__ == '__main__':
    main()
