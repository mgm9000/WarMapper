"""Rodes's and Early's divisions march onto the field instead of appearing (Morgan, 17 Nov 2026). Run once."""
import copy, json, sys
import openpyxl
sys.path.insert(0, '/home/claude/warmapper/pipeline/georef'); import gettysburg_georef as G
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'; wb = openpyxl.load_workbook(WB); D = '1863-07-01 '
R2 = json.load(open('/tmp/routes2.json'))
def head(ws): return [c.value for c in ws[1]]
def add(ws, d, like):
    h = head(ws); r = ws.max_row + 1
    for j, n in enumerate(h, 1):
        c = ws.cell(r, j); s = ws.cell(like, j)
        if s.has_style: c._style = copy.copy(s._style)
        if d.get(n) is not None: c.value = d[n]
    return r

# sources
S = wb['Sources']
add(S, {'source_id': 'S57', 'title': "Report of Lt. Gen. Richard S. Ewell, Second Corps", 'author': 'Ewell', 'date': '1863', 'type': 'Primary: official report',
        'citation': 'Official Records, Series I, Vol. 27, Part 2, p. 444', 'page verified?': 'search extract only',
        'url': 'https://civilwar.com/official-record/931-gettysburg-campaign-part-ii/190127-444-series-i-volume-xxvii-ii-serial-44-gettysburg-campaign-part-ii.html',
        'rights': 'Public domain (US government publication)', 'notes': "Read in a search extract for the approach of 1 July: Rodes's division at Heidlersburg the night before, its column turned toward Gettysburg by the Middletown road, and Early sent directly down the Heidlersburg road.", 'used_for': 'GETT'}, S.max_row)
add(S, {'source_id': 'S58', 'title': "Report of Maj. Gen. Jubal A. Early, Early's Division", 'author': 'Early', 'date': '1863', 'type': 'Primary: official report',
        'citation': 'Official Records, Series I, Vol. 27, Part 2, p. 468', 'page verified?': 'read through a reading tool',
        'url': 'https://civilwar.com/official-record/931-gettysburg-campaign-part-ii/190151-468-series-i-volume-xxvii-ii-serial-44-gettysburg-campaign-part-ii.html',
        'rights': 'Public domain (US government publication)', 'notes': "Read for the approach and deployment of 1 July: camped about 3 miles from Heidlersburg; came on by the direct road from Heidlersburg; formed across that road with Gordon on the right, Hays in the centre and Avery (Hoke's brigade) on the left, Smith behind Avery. No clock times on the page.", 'used_for': 'GETT'}, S.max_row)
for r in S.iter_rows(min_row=2):
    if r[0].value == 'S50': r[head(S).index('notes')].value += " Page 552, read 17 Nov 2026 for the approach: from Heidlersburg the division turned toward Gettysburg at Middletown, heard the cannonade within 4 miles of the town, and moved down along the wooded ridge; Doles, O'Neal and Iverson deployed left to right. No clock times on the page."

# positions: where each division's column sets off, and Ramseur's reserve near 1 p.m.
P = wb['Positions']; ph = head(P); like = [r[0].row for r in P.iter_rows(min_row=2) if r[0].value == 'P92'][0]
last = max(int(r[0].value[1:]) for r in P.iter_rows(min_row=2) if r[0].value and str(r[0].value).startswith('P') and r[0].value[1:].isdigit())
ids = []
def pos(d):
    global last; last += 1; pid = 'P%d' % last; ids.append(pid)
    base = {'pos_id': pid, 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'review_status': 'Needs review'}
    base.update(d); r = add(P, base, like)
    for n in ('unit_name', 'side', 'map_link', 'your_review_v1', 'changed in v2', 'changed in v3', 'changed in v4', 'changed in v5', 'changed in v6', 'changed in v7', 'reviewer_notes', 'place_ids', 'check: Reardon and Vossler (S55)'):
        if n in ph: P.cell(r, ph.index(n) + 1).value = None
    P.cell(r, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r
    return pid
r0, h0 = R2['r'][0], R2['h'][0]
rod = pos({'unit_id': 'CS-RODES', 'start_earliest': 'unknown', 'start_latest': D + '11:45', 'end_earliest': D + '11:45', 'end_latest': 'unknown', 'show_from': D + '11:45', 'show_to': D + '11:45',
           'time_basis': "Estimate: no source read gives a clock time for the approach. Set so the column, at a march pace of about 3 km an hour, reaches the lines Bachelder labels 1 P.M.",
           'activity': 'In column on the Middletown road, coming down from Middletown (Biglerville)', 'place_description': 'Middletown road (today Biglerville Road), about 3.5 km north of Oak Hill',
           'geometry': 'point', 'lat': r0[0], 'lon': r0[1], 'coord_source': 'estimate', 'coord_precision_m': 500, 'coordinate_confidence': 'low',
           'coordinate_basis': "On the road the reports name, at the north edge of the road data used here; how far up the road the column was at this moment is not known.",
           'source_ids': 'S50; S57', 'source_wording': 'S50, p. 552: "within 4 miles of the town"', 'position_method': 'inferred', 'overall_confidence': 'low',
           'notes': "Where Rodes's brigades set off from in the playback. The road and the direction are from Rodes (S50, p. 552) and Ewell (S57, p. 444); the time and the distance are estimates."})
ear = pos({'unit_id': 'CS-EARLY', 'start_earliest': 'unknown', 'start_latest': D + '13:30', 'end_earliest': D + '13:30', 'end_latest': 'unknown', 'show_from': D + '13:30', 'show_to': D + '13:30',
           'time_basis': "Estimate: no source read gives a clock time for the approach. Set so the column reaches the open bars Bachelder draws for Early's first line, and Gordon's line labelled 3 P.M., in time.",
           'activity': 'In column on the Heidlersburg road, coming down from Heidlersburg', 'place_description': 'Heidlersburg road (today Old Harrisburg Road), about 3 km north-east of the knoll on Rock Creek',
           'geometry': 'point', 'lat': h0[0], 'lon': h0[1], 'coord_source': 'estimate', 'coord_precision_m': 500, 'coordinate_confidence': 'low',
           'coordinate_basis': "On the road the reports name, at the north-east edge of the road data used here.",
           'source_ids': 'S58; S57; S55', 'source_wording': 'S58, p. 468: "on the direct road from Heidlersburg"', 'position_method': 'inferred', 'overall_confidence': 'low',
           'notes': "Where Early's brigades set off from in the playback. The road is from Early (S58, p. 468), Ewell (S57, p. 444) and Reardon and Vossler (S55, p. 25: down the Harrisburg Road from the northeast); the time and the distance are estimates."})
lat, lon = G.px2ll(4150, 1340); x2 = G.px2ll(4000, 1335)
ram = pos({'unit_id': 'CS-RAM', 'start_earliest': 'unknown', 'start_latest': D + '13:00', 'end_earliest': D + '14:30', 'end_latest': 'unknown', 'show_from': D + '13:00', 'show_to': D + '14:30',
           'time_basis': "No time is printed beside these bars. They stand behind the brigades labelled 1 P.M.", 'activity': 'In reserve, behind the first line', 'place_description': 'North of Oak Hill, behind O\'Neal',
           'geometry': 'line', 'lat': round(float(x2[0]), 5), 'lon': round(float(x2[1]), 5), 'line_end_lat': round(float(lat), 5), 'line_end_lon': round(float(lon), 5),
           'coord_source': 'map_read', 'coord_precision_m': 60, 'coordinate_confidence': 'medium', 'coordinate_basis': "Read from the Bachelder 1876 first-day map (S18), georeferenced; read near the top edge of the sheet.",
           'source_ids': 'S18; S50', 'source_wording': None, 'position_method': 'stated', 'overall_confidence': 'low',
           'notes': "Rodes (S50, p. 552) has his other two brigades and the artillery close up behind the first line."})

# routes
RT = wb['Routes']; rl = [r[0].row for r in RT.iter_rows(min_row=2) if r[0].value == 'RG03'][0]
fmt = lambda pts: '; '.join('%.5f, %.5f' % (a, b) for a, b in pts)
add(RT, {'route_id': 'RG04', 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'unit_id': 'CS-RODES', 'kind': 'march', 'start': D + '11:45', 'end': D + '13:00', 'from_pos_id': rod,
         'waypoints (lat, lon; ...)': fmt(R2['r'][:4]), 'source_ids': 'S50; S57', 'source_wording': 'Down the Middletown road, then along the wooded ridge.', 'confidence': 'low',
         'notes': "Today's Biglerville Road, from OpenStreetMap, to about 1 km north of the lines; from there each brigade goes straight to its line.", 'playback': 'no'}, rl)
add(RT, {'route_id': 'RG05', 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'unit_id': 'CS-EARLY', 'kind': 'march', 'start': D + '13:30', 'end': D + '14:30', 'from_pos_id': ear,
         'waypoints (lat, lon; ...)': fmt(R2['h'][:4]), 'source_ids': 'S58; S57; S55', 'source_wording': 'The direct road from Heidlersburg.', 'confidence': 'low',
         'notes': "Today's Old Harrisburg Road, from OpenStreetMap, to about 1.3 km short of the line; from there each brigade goes straight to its place in the line.", 'playback': 'no'}, rl)

# tracks
T = wb['Tracks']; th = head(T); c = lambda n: th.index(n)
SET = {'CS-IVER': (rod, '11:45', 'RG04'), 'CS-ONEAL': (rod, '11:50', 'RG04'), 'CS-DOLES': (rod, '11:55', 'RG04'), 'CS-RAM': (rod, '12:00', 'RG04'), 'CS-DAN': (rod, '12:50', 'RG04'),
       'CS-GORD': (ear, '13:30', 'RG05'), 'CS-HAYS': (ear, '13:35', 'RG05'), 'CS-AVERY': (ear, '13:40', 'RG05')}
for r in T.iter_rows(min_row=2):
    if r[0].value == 'gettysburg' and r[1].value in SET:
        row, at, rt = SET[r[1].value]
        r[c('starts_from_row')].value = row; r[c('starts_at')].value = D + at; r[c('start_route')].value = rt; r[c('start_route_points')].value = 4
        if r[1].value == 'CS-RAM': r[c('rows')].value = ram + '; ' + r[c('rows')].value
wb.save(WB); print('rows', ids)
