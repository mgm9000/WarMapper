"""20 Nov 2026 (Morgan): at 10:00 the regiments of Archer's and Davis's brigades vanished, because the workbook had only their 9:30 line.
Adds where Bachelder's 1876 first-day map (S18) draws them next:
  Archer's five along Willoughby Run, with their numbers printed beside the bars (the same place as the brigade row P78), 10:15 to 10:45;
  Davis's three in the line labelled "DAVIS MISS 10.15 A.M." (as P37), 10:15 to 10:25;
  the 42nd and 2nd Mississippi in the railroad cut, where the map prints "42' Miss." and "2' Miss." (as P38), 10:30 to 10:50.
After that the regiments merge into their brigades on the map (the player now slides them in rather than dropping them).
Also fills Archer's brigade between its rout (10:45) and 13:00: Shepard (S06) says it fell back across the field and re-formed behind
the brigades supporting it, staying in the woods for some hours; the point is P79's, the brigade's next recorded place.
Pixel picks were read from 2x crops of the full-resolution scan through its IIIF service. All new rows are "Needs review"."""
import copy, sys
sys.path.insert(0, '/home/claude/warmapper/pipeline/georef')
import gettysburg_georef as G
import openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); P = wb['Positions']; T = wb['Tracks']
ph = [c.value for c in P[1]]; th = [c.value for c in T[1]]
D = '1863-07-01 '
ids = [r[0].value for r in P.iter_rows(min_row=2) if r[0].value]
assert not any(r[ph.index('notes')].value and 'MERGE-20NOV' in str(r[ph.index('notes')].value) for r in P.iter_rows(min_row=2)), 'already applied'
nxt = [max(int(i[1:]) for i in ids if str(i).startswith('P') and str(i)[1:].isdigit()) + 1]
like = [i for i, r in enumerate(P.iter_rows(min_row=1), 1) if r[0].value == 'P78'][0]
ll = lambda p: tuple(round(v, 5) for v in G.px2ll(*p))
lerp = lambda a, b, f: (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
BASIS = 'Read from the Bachelder 1876 first-day map (S18), full-resolution scan, georeferenced; good to about 20-40 m. lat/lon = first end; line_end = second end.'
made = {}
def add(key, unit, a, b, show, start, act, place, basis, src, wording, conf='medium', cconf='medium', method='stated', tb='', notes='', geo='px'):
    pid = 'P%d' % nxt[0]; nxt[0] += 1; made[key] = pid
    r = P.max_row + 1
    for j in range(1, len(ph) + 1):
        s = P.cell(like, j)
        if s.has_style: P.cell(r, j)._style = copy.copy(s._style)
    A = ll(a) if geo == 'px' else a; Bp = ll(b) if geo == 'px' else b
    v = {'pos_id': pid, 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'unit_id': unit, 'start_earliest': D + start, 'start_latest': D + start,
         'end_earliest': 'unknown', 'end_latest': 'unknown', 'time_basis': tb, 'activity': act, 'place_description': place, 'geometry': 'line',
         'lat': A[0], 'lon': A[1], 'line_end_lat': Bp[0], 'line_end_lon': Bp[1], 'coord_source': 'map_read' if geo == 'px' else 'estimate', 'coord_precision_m': 40 if geo == 'px' else 150,
         'coordinate_basis': basis, 'coordinate_confidence': cconf, 'source_ids': src, 'source_wording': wording, 'position_method': method, 'overall_confidence': conf,
         'notes': (notes + ' ' if notes else '') + '[MERGE-20NOV] Added 20 Nov 2026 so the regiments do not vanish at 10:00.', 'review_status': 'Needs review',
         'show_from': D + show[0], 'show_to': D + show[1], 'changed in v8': 'New, 20 Nov 2026.'}
    for k, x in v.items(): P.cell(r, ph.index(k) + 1).value = x
    P.cell(r, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=16/"&O%d&"/"&P%d,"Open map"))' % (r, r, r, r, r)
    return pid

# Archer's brigade along Willoughby Run (as P78): 7 TN on its own bar at the north; one long bar with 14 TN, 5 AL Bn and 13 AL; 1 TN a little south
TBA = "As P78: no time printed beside these bars; Meredith's line, which faces them, is labelled 10.15 A.M."
PL = 'Along Willoughby Run, at the west edge of Herbst Woods'
add('7tn', 'CS-7TN', (3025, 3002), (2990, 3072), ('10:15', '10:45'), '10:15', 'Line of battle, engaged', PL, BASIS, 'S18; S06', 'Map label: "7\' Tenn."', tb=TBA)
top, bot = (2985, 3082), (2927, 3382)
for i, (u, lab) in enumerate([('CS-14TN', "14' Tenn."), ('CS-5ALB', "5' Ala. Batt."), ('CS-13AL', "13' Ala.")]):
    add(u, u, lerp(top, bot, i / 3), lerp(top, bot, (i + 1) / 3), ('10:15', '10:45'), '10:15', 'Line of battle, engaged', PL,
        BASIS + ' One bar carries three regiment numbers; it is split in thirds, in the order the numbers are printed.', 'S18; S06', 'Map label: "%s"' % lab, cconf='low', tb=TBA)
add('1tn', 'CS-1TN', (2972, 3375), (2985, 3460), ('10:15', '10:45'), '10:15', 'Line of battle, engaged', PL + ', on the right of the brigade', BASIS, 'S18; S06', 'Map label: "1\' Tenn."', tb=TBA)
# Davis's brigade, the line labelled 10.15 A.M. (as P37)
TBD = 'Map label "DAVIS MISS 10.15 A.M." (S18)'
PD = 'East of Willoughby Run, north of the Chambersburg Pike'
add('55nc', 'CS-55NC', (3510, 2570), (3650, 2565), ('10:15', '10:25'), '10:15', 'Line of battle, engaged; the left of the brigade', PD, BASIS, 'S18; S05', 'Map label: "55\' N.C."', tb=TBD)
add('2ms', 'CS-2MS', (3400, 2665), (3492, 2577), ('10:15', '10:25'), '10:15', 'Line of battle, engaged; the centre of the brigade', PD, BASIS, 'S18; S05', 'Map label: "2\' Miss."', tb=TBD)
add('42ms', 'CS-42MS', (3347, 2735), (3390, 2675), ('10:15', '10:25'), '10:15', 'Line of battle, engaged; the right of the brigade, next to the pike', PD, BASIS, 'S18; S05',
    'Map label: "Miss." (the number is not legible; Davis puts the 42nd on the right)', cconf='low', tb=TBD)
# the railroad cut (as P38): the 42nd at the west end, the 2nd at the east end
w, e = (39.83867, -77.25071), (39.83719, -77.24813); mid = lerp(w, e, 0.5); mid = (round(mid[0], 5), round(mid[1], 5))
TBC = 'As P38: the map gives these bars no time; the 95th New York beside them is labelled 10.30 A.M.'
PC = 'Unfinished railroad cut north of the Chambersburg Pike'
add('42ms-cut', 'CS-42MS', w, mid, ('10:30', '10:50'), '10:30', 'In the unfinished railroad cut', PC, 'P38 split in two at its middle: the map prints "42\' Miss." at the west end and "2\' Miss." at the east end.',
    'S18; S05; S12', 'Map label: "42\' Miss."', conf='low', geo='ll', tb=TBC, notes='Davis (S05): the 2nd and 42nd Mississippi took a Union flag and prisoners there; some officers and men were left in the cut and captured.')
add('2ms-cut', 'CS-2MS', mid, e, ('10:30', '10:50'), '10:30', 'In the unfinished railroad cut', PC, 'P38 split in two at its middle: the map prints "42\' Miss." at the west end and "2\' Miss." at the east end.',
    'S18; S05; S12', 'Map label: "2\' Miss."', conf='low', geo='ll', tb=TBC)
# Archer's brigade between the rout and 13:00 (stand-in at P79)
p79 = [r for r in P.iter_rows(min_row=2) if r[0].value == 'P79'][0]
g = lambda k: p79[ph.index(k)].value
add('arch-reform', 'CS-ARCH', (g('lat'), g('lon')), (g('line_end_lat'), g('line_end_lon')), ('11:15', '12:59'), '11:00', 'Fallen back across Willoughby Run; re-forming behind the supporting brigades',
    'Herr Ridge, south of the Springs road woods', 'Stand-in: the brigade\'s next recorded place (P79). Shepard says only that it re-formed behind the brigade supporting it.', 'S06; S11',
    'Shepard (S06): fell back across the field and re-formed behind the supporting brigade; Col. Fry took command; some hours in the woods', conf='low', cconf='low', method='inferred', geo='ll',
    tb='Shepard gives no clock time; the start follows the brigade\'s rout at about 10:45 (P78).', notes='About 75 men, Archer among them, could not get back over the run and were captured (S06).')
# tracks
rows = {r[1].value: r for r in T.iter_rows(min_row=2) if r[0].value == 'gettysburg'}
ext = {'CS-7TN': ['7tn'], 'CS-14TN': ['CS-14TN'], 'CS-5ALB': ['CS-5ALB'], 'CS-13AL': ['CS-13AL'], 'CS-1TN': ['1tn'], 'CS-55NC': ['55nc'], 'CS-2MS': ['2ms', '2ms-cut'], 'CS-42MS': ['42ms', '42ms-cut']}
for tid, keys in ext.items():
    c = rows[tid][th.index('rows')]; c.value = c.value + '; ' + '; '.join(made[k] for k in keys)
c = rows['CS-ARCH'][th.index('rows')]; assert c.value == 'P14; P16; P17; P18; P78; P79', c.value
c.value = 'P14; P16; P17; P18; P78; %s; P79' % made['arch-reform']
wb.save(WB); print(made)
