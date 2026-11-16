"""Add the rest of 1 July 1863 to the master workbook: brigades of both armies, read from the Bachelder first-day map (S18).

This script was run once, on 15 November 2026, and is kept as the record of how rows P39 to P109 were made. Running it again would add them twice.
Positions are scan pixels of the Bachelder sheet (picks in gettysburg_day1_picks.txt), turned into latitude and longitude with the fit in
pipeline/georef/gettysburg_georef.py.
"""
import copy, sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/pipeline/georef')
import gettysburg_georef as G
import openpyxl

WB = ROOT + '/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB)
D = '1863-07-01 '
GK = 'Commander: general knowledge, not yet checked against a source.'


def ll(p):
    lat, lon = G.px2ll(p[0], p[1]); return round(lat, 5), round(lon, 5)


def head(ws): return [c.value for c in ws[1]]


def add(ws, rowdict, like):
    """Append a row, copying the look of row `like`."""
    h = head(ws); r = ws.max_row + 1
    for j, name in enumerate(h, 1):
        c = ws.cell(r, j); src = ws.cell(like, j)
        if src.has_style: c._style = copy.copy(src._style)
        if name in rowdict and rowdict[name] is not None: c.value = rowdict[name]
    ws.row_dimensions[r].height = ws.row_dimensions[like].height
    return r


# ---------------------------------------------------------------- sources
S = wb['Sources']
add(S, {'source_id': 'S49', 'title': 'The Battle of Gettysburg (National Park Civil War Series): the first day', 'author': 'Not stated on the page',
        'date': 'modern', 'type': 'Modern secondary: park series booklet', 'citation': 'Eastern National, National Park Civil War Series, as reproduced at npshistory.com',
        'page verified?': 'n/a', 'url': 'https://npshistory.com/publications/civil_war_series/16/sec4.htm', 'rights': 'Copyrighted; facts only, no text copied',
        'notes': 'Read through a reading tool, in summary. Used for the order of the afternoon fighting, a few times ("about 11:30 A.M.", "about 2:30 P.M.", "about 4 P.M.") and brigade names. It gives no positions on Cemetery Hill by unit.',
        'used_for': 'GETT'}, like=S.max_row)
for r in S.iter_rows(min_row=2):
    if r[0].value == 'S16':
        r[9].value = 'Used to cross-check times, and for the times of events of the afternoon of 1 July that no primary source read here gives. Its own sourcing was not reviewed.'
    if r[0].value == 'S18':
        r[9].value = (r[9].value or '') + ' Whole first day (November 2026): the brigade bars of both armies for the rest of 1 July were read from the same scan, with the times printed beside them.'

# ---------------------------------------------------------------- units and assignments
U = wb['Units']; A = wb['Assignments']
u_like = [i for i, r in enumerate(U.iter_rows(min_row=1), 1) if r[0].value == 'CS-PEND'][0]
a_like = [i for i, r in enumerate(A.iter_rows(min_row=1), 1) if r[0].value == 'A032'][0]
anum = [141]


def unit(uid, name, label, side, ech, parent, commander, src='S18', known='partly', notes=None, strength=None, asrc=None, anote=None):
    us = side == 'US'
    add(U, {'unit_id': uid, 'unit_name': name, 'map_label': label, 'side_id': 'ACW-US' if us else 'ACW-CS', 'nation': 'United States' if us else 'Confederate States',
            'branch': 'Infantry', 'echelon': ech, 'source_ids': src, 'sourced?': known, 'notes': notes}, like=u_like)
    add(A, {'assign_id': 'A%03d' % anum[0], 'unit_id': uid, 'parent_unit_id': parent, 'commander': commander, 'strength / equipment': strength,
            'valid_from': '1863-07-01', 'valid_to': '1863-07-01', 'source_ids': asrc or src, 'notes': anote}, like=a_like); anum[0] += 1


NB = 'Named on the map (S18). ' + GK
unit('US-1C', 'First Corps, Army of the Potomac', 'I Corps', 'US', 'Corps', None, 'Maj. Gen. Abner Doubleday (after Reynolds fell)', 'S18; S16', 'partly',
     'The map prints "Gen. Doubleday Com\'d\'g 1st Corps". Maj. Gen. John F. Reynolds led the corps and the left wing until he was killed that morning (S16).')
unit('US-1C-1', '1st Division, First Corps', 'Wadsworth', 'US', 'Division', 'US-1C', 'Brig. Gen. James S. Wadsworth', 'S18; S16', 'partly', 'Division named on the map and in S16. Rank and first name: general knowledge.')
unit('US-MER', "1st Brigade, 1st Division, First Corps (the Iron Brigade)", 'Meredith', 'US', 'Brigade', 'US-1C-1', 'Brig. Gen. Solomon Meredith', 'S18; S16', 'partly',
     'Regiments on the map: 2nd and 7th Wisconsin, 19th Indiana, 24th Michigan in line, 6th Wisconsin detached to the railroad cut. ' + GK)
unit('US-CUT', '2nd Brigade, 1st Division, First Corps', 'Cutler', 'US', 'Brigade', 'US-1C-1', 'Brig. Gen. Lysander Cutler', 'S18; S16', 'partly',
     'Regiments on the map: 76th and 147th New York and 56th Pennsylvania north of the railroad; 14th New York State Militia (14th Brooklyn) and 95th New York south of the pike. ' + GK)
unit('US-1C-2', '2nd Division, First Corps', 'Robinson', 'US', 'Division', 'US-1C', 'Brig. Gen. John C. Robinson', 'S18; S49', 'partly', 'Division named on the map and in S49. Rank and first name: general knowledge.')
unit('US-PAUL', '1st Brigade, 2nd Division, First Corps', 'Paul', 'US', 'Brigade', 'US-1C-2', 'Brig. Gen. Gabriel R. Paul', notes='Regiments on the map: 16th Maine, 94th and 104th New York, 107th Pennsylvania, 13th Massachusetts. ' + NB)
unit('US-BAX', '2nd Brigade, 2nd Division, First Corps', 'Baxter', 'US', 'Brigade', 'US-1C-2', 'Brig. Gen. Henry Baxter', notes='Regiments on the map: 90th, 88th and 11th Pennsylvania, 12th Massachusetts, 83rd and 97th New York. ' + NB)
unit('US-1C-3', '3rd Division, First Corps', 'Rowley', 'US', 'Division', 'US-1C', 'Brig. Gen. Thomas A. Rowley', 'S18; S49', 'yes', "Doubleday's own division, under Rowley while Doubleday led the corps (S49). The map prints ROWLEY beside both brigades.")
unit('US-BID', '1st Brigade, 3rd Division, First Corps', 'Biddle', 'US', 'Brigade', 'US-1C-3', 'Col. Chapman Biddle', 'S18; S49', 'yes', 'Regiments on the map: 151st, 142nd and 121st Pennsylvania, 20th New York State Militia. Commander per S49.')
unit('US-STONE', '2nd Brigade, 3rd Division, First Corps', 'Stone', 'US', 'Brigade', 'US-1C-3', 'Col. Roy Stone', 'S18; S49', 'partly', 'Regiments on the map: 143rd, 149th and 150th Pennsylvania. Brigade named in S49; rank and first name: general knowledge.')
unit('US-11C', 'Eleventh Corps, Army of the Potomac', 'XI Corps', 'US', 'Corps', None, 'Maj. Gen. Carl Schurz (Howard commanding the field)', 'S18; S16', 'yes',
     'The map prints "Gen. Schurz Com\'d\'g 11\' Corps" and, on Cemetery Hill, "Gen\'l Howard Com\'g the field after Gen. Reynolds\' death".')
unit('US-11C-1', '1st Division, Eleventh Corps', 'Barlow', 'US', 'Division', 'US-11C', 'Brig. Gen. Francis C. Barlow', 'S18; S16', 'partly', 'The map prints "Barlow\'s Division". Barlow was badly wounded and left on the field (S16). Rank and first name: general knowledge.')
unit('US-GIL', '1st Brigade, 1st Division, Eleventh Corps', 'von Gilsa', 'US', 'Brigade', 'US-11C-1', 'Col. Leopold von Gilsa', 'S18; S16', 'partly', 'Regiments on the map: 54th and 68th New York, 153rd Pennsylvania. ' + GK)
unit('US-AMES', '2nd Brigade, 1st Division, Eleventh Corps', 'Ames', 'US', 'Brigade', 'US-11C-1', 'Brig. Gen. Adelbert Ames', notes='Regiments on the map: 107th, 75th and 25th Ohio, 17th Connecticut. ' + NB)
unit('US-11C-3', '3rd Division, Eleventh Corps', 'Schimmelfennig', 'US', 'Division', 'US-11C', 'Brig. Gen. Alexander Schimmelfennig', 'S18', 'yes', 'The map prints "Schurz\'s Division, Schimmelphennig Commanding".')
unit('US-AMS', '1st Brigade, 3rd Division, Eleventh Corps', 'von Amsberg', 'US', 'Brigade', 'US-11C-3', 'Col. George von Amsberg', notes="Schimmelfennig's own brigade. Regiments on the map: 157th and 45th New York, 74th Pennsylvania, 61st Ohio, 82nd Illinois. " + NB)
unit('US-KRZ', '2nd Brigade, 3rd Division, Eleventh Corps', 'Krzyzanowski', 'US', 'Brigade', 'US-11C-3', 'Col. Wladimir Krzyzanowski', notes='Regiments on the map: 119th and 58th New York, 26th Wisconsin, 82nd Ohio, 75th Pennsylvania. ' + NB)
unit('US-11C-2', '2nd Division, Eleventh Corps', 'Steinwehr', 'US', 'Division', 'US-11C', 'Brig. Gen. Adolph von Steinwehr', 'S18; S16', 'partly', 'The map prints "Steinwehr\'s Div." on Cemetery Hill; S16 has the division held there as the reserve. Rank and first name: general knowledge.')
unit('US-COS', '1st Brigade, 2nd Division, Eleventh Corps', 'Coster', 'US', 'Brigade', 'US-11C-2', 'Col. Charles R. Coster', notes='The map spells the name Costar. Regiments on the map at the brickyard: 27th Pennsylvania, 154th and 134th New York; the 73rd Pennsylvania is drawn at the edge of the town. ' + NB)
unit('US-SMI', '2nd Brigade, 2nd Division, Eleventh Corps', 'Smith', 'US', 'Brigade', 'US-11C-2', 'Col. Orland Smith', notes='Regiments on the map: 55th and 73rd Ohio, 136th New York, 33rd Massachusetts. ' + NB)
unit('CS-PER', "McGowan's Brigade, Pender's Division", 'Perrin', 'CS', 'Brigade', 'CS-PEND', 'Col. Abner Perrin', 'S18; S49', 'partly',
     "The map prints McGOWAN S.C.; the brigade was led that day by Perrin (S49 names it Perrin's brigade). South Carolina regiments 1st, 12th, 13th and 14th on the map. Rank and first name: general knowledge.")
unit('CS-SCA', "Scales's Brigade, Pender's Division", 'Scales', 'CS', 'Brigade', 'CS-PEND', 'Brig. Gen. Alfred M. Scales', 'S18; S49', 'partly', 'North Carolina regiments 13th, 16th, 22nd, 34th and 38th on the map. Rank and first name: general knowledge.')
unit('CS-LANE', "Lane's Brigade, Pender's Division", 'Lane', 'CS', 'Brigade', 'CS-PEND', 'Brig. Gen. James H. Lane', notes='North Carolina regiments 7th, 18th, 28th, 33rd and 37th on the map. ' + NB)
unit('CS-THO', "Thomas's Brigade, Pender's Division", 'Thomas', 'CS', 'Brigade', 'CS-PEND', 'Brig. Gen. Edward L. Thomas', notes='Georgia regiments. The map marks the brigade as supporting the artillery north of the pike. ' + NB)
unit('CS-RODES', "Rodes's Division, Second Corps", 'Rodes', 'CS', 'Division', None, 'Maj. Gen. Robert E. Rodes', 'S18; S49', 'partly', 'The map prints "Rodes\' Division, Ewell\'s Corps". Rank and first name: general knowledge.')
unit('CS-DOLES', "Doles's Brigade, Rodes's Division", 'Doles', 'CS', 'Brigade', 'CS-RODES', 'Brig. Gen. George Doles', 'S18; S49', 'partly', 'Georgia regiments 4th, 12th, 21st and 44th on the map. Rank and first name: general knowledge.')
unit('CS-IVER', "Iverson's Brigade, Rodes's Division", 'Iverson', 'CS', 'Brigade', 'CS-RODES', 'Brig. Gen. Alfred Iverson', 'S18; S49', 'partly', 'North Carolina regiments 5th, 12th, 20th and 23rd on the map. S49: the brigade lost about 800 men. Rank and first name: general knowledge.')
unit('CS-DAN', "Daniel's Brigade, Rodes's Division", 'Daniel', 'CS', 'Brigade', 'CS-RODES', 'Brig. Gen. Junius Daniel', 'S18; S49', 'partly', 'The map spells the name Daniels. North Carolina regiments 32nd, 43rd, 45th and 53rd and the 2nd Battalion on the map. Rank and first name: general knowledge.')
unit('CS-RAM', "Ramseur's Brigade, Rodes's Division", 'Ramseur', 'CS', 'Brigade', 'CS-RODES', 'Brig. Gen. Stephen D. Ramseur', 'S18; S49', 'partly', 'North Carolina regiments 2nd, 4th, 14th and 30th on the map. Rank and first name: general knowledge.')
unit('CS-ONEAL', "O'Neal's Brigade, Rodes's Division", "O'Neal", 'CS', 'Brigade', 'CS-RODES', "Col. Edward A. O'Neal", 'S18; S49', 'partly', 'Alabama regiments on the map; the 5th Alabama and a battalion of sharpshooters are drawn apart, on the plain. Rank and first name: general knowledge.')
unit('CS-EARLY', "Early's Division, Second Corps", 'Early', 'CS', 'Division', None, 'Maj. Gen. Jubal A. Early', 'S18; S16', 'partly', 'The map prints "Early\'s Division". Rank and first name: general knowledge.')
unit('CS-GORD', "Gordon's Brigade, Early's Division", 'Gordon', 'CS', 'Brigade', 'CS-EARLY', 'Brig. Gen. John B. Gordon', 'S18; S16', 'partly', 'Georgia regiments 13th, 31st, 38th, 60th and 61st on the map; the 26th Georgia is drawn apart, with the artillery. Rank and first name: general knowledge.')
unit('CS-HAYS', "Hays's Brigade, Early's Division", 'Hays', 'CS', 'Brigade', 'CS-EARLY', 'Brig. Gen. Harry T. Hays', notes='Louisiana regiments 5th, 6th, 7th, 8th and 9th on the map. ' + NB)
unit('CS-AVERY', "Hoke's Brigade, Early's Division", 'Avery', 'CS', 'Brigade', 'CS-EARLY', 'Col. Isaac E. Avery', notes="The map prints HOKE N.C.; Hoke was absent wounded and Avery led the brigade (general knowledge, not yet checked). North Carolina regiments 6th, 21st and 57th on the map.")

# ---------------------------------------------------------------- positions
P = wb['Positions']; ph = head(P)
p_like = [i for i, r in enumerate(P.iter_rows(min_row=1), 1) if r[0].value == 'P37'][0]
pnum = [39]; made = {}
BASIS = 'Read from the Bachelder 1876 first-day map (S18), georeferenced; good to about 20-40 m. '
NOTIME = 'No time is printed beside these bars. '


def pos(key, unit_id, pts, label, show, activity, place, start=None, end=None, basis='', notes=None, method='stated', conf='medium', cconf='medium', src='S18', csrc='map_read',
        prec=40, tb=None, wording=None, review='Needs review'):
    """label: the time printed on the map, quoted, or None. start/end: (earliest, latest) clock times or 'unknown'."""
    pid = 'P%02d' % pnum[0]; pnum[0] += 1; made[key] = pid
    t = lambda v: v if v in (None, 'unknown') else D + v
    st = start or ('unknown', 'unknown'); en = end or ('unknown', 'unknown')
    row = {'pos_id': pid, 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'unit_id': unit_id, 'start_earliest': t(st[0]), 'start_latest': t(st[1]), 'end_earliest': t(en[0]), 'end_latest': t(en[1]),
           'time_basis': tb or ('Map label "%s" (S18)' % label if label else NOTIME.strip()), 'activity': activity, 'place_description': place,
           'coord_source': csrc, 'coord_precision_m': prec, 'coordinate_confidence': cconf, 'source_ids': src, 'source_wording': wording or (('Map label: "%s"' % label) if label else None),
           'position_method': method, 'overall_confidence': conf, 'notes': notes, 'review_status': review, 'changed in v7': None,
           'show_from': D + show[0], 'show_to': D + show[1]}
    if pts:
        L = [ll(p) for p in pts]
        row.update(geometry='line' if len(L) > 1 else 'point', lat=L[0][0], lon=L[0][1])
        if len(L) > 1: row.update(line_end_lat=L[-1][0], line_end_lon=L[-1][1])
        if len(L) > 2: row['via'] = '; '.join('%.5f, %.5f' % q for q in L[1:-1])
        row['coordinate_basis'] = (BASIS if csrc == 'map_read' else '') + basis
    else:
        row.update(geometry='none'); row['coordinate_basis'] = basis or None
    r = add(P, row, like=p_like)
    P.cell(r, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=16/"&O%d&"/"&P%d,"Open map"))' % (r, r, r, r, r)
    for name in ('your_review_v1', 'changed in v2', 'changed in v3', 'changed in v4', 'changed in v5', 'changed in v6', 'reviewer_notes', 'place_ids'):
        P.cell(r, ph.index(name) + 1).value = None
    return pid


FACE = lambda who, t: NOTIME + "%s, which faces them, is labelled %s." % (who, t)
EVE = ("Estimate. The sources read (S16, S49) say only that the two corps fell back through the town and were rallied on Cemetery Hill; none read here places this brigade. "
       "The point is set on the hill, apart from the other brigades so the symbols do not stack.")


def evening(key, unit_id, p, place='Cemetery Hill'):
    pos(key, unit_id, [p], None, ('16:45', '17:30'), 'Rallied after the retreat through the town', place, start=('16:30', '17:00'), basis=EVE, method='inferred', conf='low', cconf='low',
        src='S16; S49', csrc='estimate', prec=300, tb='S16: the troops fall back to Cemetery Hill and are rallied there about 4:30 p.m. S49: Howard orders both corps back about 4 P.M.')


# ---- Buford's cavalry, afternoon
pos('gam4', 'US-B1', [(3650, 3710), (3600, 3970)], '4 P.M.', ('15:45', '16:15'), 'Line of battle (dismounted)', 'Seminary Ridge south of the Fairfield road, at the Shultz house and woods',
    start=('unknown', '16:00'), basis='lat/lon = north end; line_end = south end.', wording='Map label: "GAMBLE 1\' Brig. 1\' Div. Cav. 4 P.M. (Dismounted)"')
pos('dev2', 'US-B2', [(5430, 3310)], None, ('12:30', '15:30'), 'In column, east of the town', 'Between the York and Hanover roads, west of Rock Creek',
    basis='Centre of a group of columns labelled "Devin 2\' Brig. Cav. 1\' Division".', conf='low', tb=NOTIME + 'The time shown is a guess at early afternoon.',
    notes='When the brigade came here and when it left are not on the map.')
pos('buf430', 'US-CAV1', [(4050, 4130)], '4.30 P.M.', ('16:30', '17:30'), 'Division in column of squadrons', 'Fields south-west of the town, between the Emmitsburg road and Seminary Ridge (hill 432)',
    start=('unknown', '16:30'), basis='Centre of the columns labelled "1\' Div. Cavalry, Buford, 4.30 P.M.". The map does not say which columns are which brigade.',
    wording='Map label: "1\' Div. Cavalry BUFORD 4.30 P.M."')

# ---- First Corps
pos('mer1', 'US-MER', [(3012, 3090), (3030, 3300), (3042, 3440), (2905, 3515)], '10.15 A.M. - 3 P.M.', ('10:15', '15:00'), 'Line of battle', "Herbst (McPherson) Woods, east bank of Willoughby Run",
    start=('10:15', '10:15'), end=('15:00', '15:00'), basis='From the north: 2nd Wisconsin, 7th Wisconsin, 19th Indiana, then the 24th Michigan bent back across the run.',
    wording='Map label: "MEREDITH 1\' WADSWORTH 10.15 A.M. - 3 P.M."')
pos('mer2', 'US-MER', [(3640, 3200), (3640, 3420)], '4 P.M.', ('15:45', '16:10'), 'Last line, at the barricade', 'In front of the Lutheran Seminary',
    start=('unknown', '16:00'), basis='lat/lon = north end; line_end = south end.', wording='Map label: "MEREDITH 1\' 4 P.M."')
evening('mer3', 'US-MER', (4800, 4460))
pos('cut1', 'US-CUT', [(3440, 2950), (3525, 2800), (3620, 2650)], '10.15 A.M.', ('10:15', '10:30'), 'Line of battle, engaged (right wing)', 'North of the railroad bed, on the ridge east of the McPherson farm',
    start=('10:15', '10:15'), basis='From the south: 147th New York, 56th Pennsylvania, 76th New York. The two regiments south of the pike are row cut1L.',
    wording='Map label: "WADSWORTH CUTLER 2\'d 10.15 A.M."')
pos('cut1L', 'US-CUT', [(3088, 2895), (3028, 3085)], '10.15 A.M.', ('10:15', '10:25'), 'Line of battle (left wing)', 'South of the Chambersburg Pike, west of the McPherson buildings',
    start=('10:15', '10:15'), basis='14th New York State Militia and 95th New York.', wording='Map label: "CUTLER 2\'d 14 N.Y.S.M. 10.15 A.M."')
pos('cut2L', 'US-CUT', [(3272, 2828), (3445, 2990), (3530, 2980)], '10.30 A.M.', ('10:30', '11:00'), 'Charge on the railroad cut', 'South edge of the unfinished railroad cut',
    start=('10:30', '10:30'), basis='From the west: 14th New York State Militia, 95th New York, then the 6th Wisconsin of Meredith\'s brigade.',
    wording='Map label: "95\' N.Y. 2\'d 10.30 A.M."', notes="Davis's bars in the cut are row P38.")
pos('cut3', 'US-CUT', [(3700, 2660), (3800, 2665), (3785, 2830)], '3-4 P.M.', ('15:00', '16:00'), 'Line of battle', 'Oak Ridge, in the woods north of the railroad',
    start=('unknown', '15:00'), end=('16:00', 'unknown'), wording='Map label: "CUTLER 3-4 P.M."', notes='Where the brigade stood between 10:30 and 3 p.m. is not read from the map.')
evening('cut4', 'US-CUT', (4830, 4540))
pos('paul1', 'US-PAUL', [(3850, 3430)], '1-3 P.M.', ('13:00', '15:00'), 'In reserve, in column', 'East of the Lutheran Seminary',
    start=('unknown', '13:00'), end=('15:00', '15:00'), basis='Centre of five columns.', wording='Map label: "ROBINSON\'S DIV. PAUL 1\' 1-3 P.M."')
pos('paul2', 'US-PAUL', [(3835, 2640), (3875, 2480), (3935, 2470), (4010, 2495), (4160, 2500)], '3-4 P.M.', ('15:10', '16:00'), 'Line of battle', 'Oak Ridge at the Mummasburg road, the right of the First Corps',
    start=('unknown', '15:00'), end=('16:00', 'unknown'), basis='The line runs north along the ridge, then east: 16th Maine, 94th and 104th New York, 107th Pennsylvania, 13th Massachusetts.',
    wording='Map label: "PAUL 1\' 3-4 P.M."', src='S18; S49', notes='S49: the 16th Maine held the Mummasburg road to cover the retreat and lost 232 of 298 men.')
evening('paul3', 'US-PAUL', (4540, 4480))
pos('bax1', 'US-BAX', [(3950, 2295), (3865, 2310), (3850, 2450), (3830, 2620)], '1-3 P.M.', ('13:00', '15:00'), 'Line of battle', 'Oak Ridge, from the Mummasburg road south',
    start=('unknown', '13:00'), end=('15:00', '15:00'), basis='The 90th Pennsylvania faces north along the road; the rest face west.', wording='Map label: "BAXTER 2\'d 1-3 P.M."')
pos('bax2', 'US-BAX', [(3895, 2780), (3800, 3170)], '3-4 P.M.', ('15:10', '16:00'), 'Line of battle', 'East slope of Oak Ridge, north of the railroad',
    start=('unknown', '15:00'), end=('16:00', 'unknown'), wording='Map label: "BAXTER 2\'d 3-4 P.M."')
evening('bax3', 'US-BAX', (4520, 4560))
pos('sto1', 'US-STONE', [(3207, 3175), (3265, 2985), (3400, 3050)], '11 A.M. - 3.30 P.M.', ('11:00', '15:30'), 'Line of battle', 'McPherson farm: facing west on the ridge, then back along the Chambersburg Pike facing north',
    start=('11:00', '11:00'), end=('15:30', '15:30'), basis='150th Pennsylvania faces west; 149th and 143rd face north along the pike.', wording='Map label: "ROWLEY STONE 2\'d 11 A.M. 3.30 P.M."')
pos('sto2', 'US-STONE', [(3605, 3100), (3570, 3280), (3540, 3360)], '4 P.M.', ('15:50', '16:10'), 'Last line', 'Seminary Ridge, north of the seminary',
    start=('unknown', '16:00'), wording='Map label: "STONE 2\'d 4 P.M."')
evening('sto3', 'US-STONE', (4680, 4500))
pos('bid1', 'US-BID', [(3305, 3260), (3145, 3700)], '11 A.M.', ('11:00', '14:25'), 'Line of battle', 'Open ridge south of Herbst Woods, toward the Fairfield road',
    start=('11:00', '11:00'), basis='From the north: 151st and 142nd Pennsylvania, 20th New York State Militia, 121st Pennsylvania.', wording='Map label: "ROWLEY BIDDLE 1\' 11 A.M."')
pos('bid2', 'US-BID', [(3150, 3592), (3400, 3630)], '2.30 P.M.', ('14:30', '15:15'), 'Line of battle', 'Across the ridge south of Herbst Woods',
    start=('14:30', '14:30'), basis='The bars run east and west.', wording='Map label: "BIDDLE 2.30 P.M."', conf='low', notes='Read as a change of front. A reviewer should confirm which way this line faces.')
pos('bid3', 'US-BID', [(3640, 3440), (3650, 3540), (3690, 3585)], '4 P.M.', ('15:50', '16:10'), 'Last line', 'Seminary Ridge, south of the seminary',
    start=('unknown', '16:00'), wording='Map label: "BIDDLE 1\' 4 P.M."')
evening('bid4', 'US-BID', (4660, 4580))

# ---- Eleventh Corps
pos('ams1', 'US-AMS', [(4150, 2700), (4420, 2690)], None, ('13:00', '15:15'), 'First position', 'North of the town, west of the Carlisle road',
    start=('unknown', 'unknown'), tb=NOTIME + 'S16 has the corps forming north of the town at 1:00 p.m.', src='S18; S16', conf='low',
    basis='Bars of the 157th New York, 74th Pennsylvania, 61st Ohio and 82nd Illinois, labelled "V. Amsberg 1\'".', notes='The map also draws a skirmish line farther north, not entered here.')
pos('ams2', 'US-AMS', [(4215, 2190), (4340, 2300), (4500, 2430), (4570, 2465)], '3.30 P.M.', ('15:30', '15:40'), 'Advanced line, engaged', 'Fields between the Mummasburg and Carlisle roads',
    start=('unknown', '15:30'), wording='Map label: "3.30 P.M. AMSBERG"', notes="Doles's 3.30 line (row dol3) lies about 75 m from it.")
pos('xi345', 'US-11C', [(4450, 2915), (4760, 2950)], '3.45 P.M.', ('15:45', '16:00'), 'Rallying line', 'North edge of the town, near the Kitzman house and the college',
    start=('unknown', '15:45'), wording='Map label: "Portions of the 1st & 3d Div\'s 11\' Corps 3.45 P.M."', notes='The map does not say which brigades. The playback draws it for the two brigades of the 3rd Division.')
evening('ams3', 'US-AMS', (4560, 4330))
pos('krz1', 'US-KRZ', [(4650, 2420), (4530, 2640)], None, ('14:30', '15:35'), 'In column of regiments, then engaged', 'East of the Carlisle road, north of the almshouse',
    start=('unknown', 'unknown'), tb=NOTIME + "Doles's and von Amsberg's lines beside it are labelled 3.30 P.M.", conf='low', basis='A line through five regimental columns.')
evening('krz2', 'US-KRZ', (4700, 4360))
pos('gil1', 'US-GIL', [(4925, 2060), (5060, 2200)], None, ('14:30', '15:10'), 'Line of battle', "Blocher's (Barlow's) Knoll, along Rock Creek",
    start=('unknown', '15:00'), tb=FACE("Gordon's line", '3 P.M.'), conf='low')
pos('ames1', 'US-AMES', [(4640, 2390), (4710, 2300), (4800, 2245), (4890, 2285), (4940, 2330)], None, ('14:30', '15:10'), 'Line of battle', "Blocher's (Barlow's) Knoll and the fields west of it",
    start=('unknown', '15:00'), tb=FACE("Gordon's line", '3 P.M.'), conf='low', basis='From the west: 107th, 75th and 25th Ohio, 17th Connecticut.')
pos('ames2', 'US-AMES', [(5080, 2710), (5230, 2800)], None, ('15:25', '15:40'), 'Second line', 'North-east of the almshouse',
    start=('unknown', 'unknown'), tb=NOTIME + "It lies between Gordon's 3 P.M. line and Hays's 3.45 P.M. line.", conf='low')
evening('ames3', 'US-AMES', (4790, 4180), 'East Cemetery Hill')
evening('gil2', 'US-GIL', (4870, 4290), 'East Cemetery Hill')
pos('cos1', 'US-COS', [(4620, 4270), (4800, 4235)], None, ('14:00', '15:15'), 'In reserve', 'East Cemetery Hill',
    start=('unknown', '14:00'), tb=NOTIME + 'S16 has the division arriving at 2:00 p.m. and held on Cemetery Hill.', src='S18; S16', basis='Open bars (a first position) labelled COSTAR.')
pos('cos2', 'US-COS', [(4860, 3025), (4940, 3090), (5010, 3160), (5070, 3235)], '3.45', ('15:40', '15:55'), 'Line of battle, covering the retreat', "North-east edge of the town, south of Stevens Run (the brickyard)",
    start=('unknown', '15:45'), basis='From the west: 27th Pennsylvania, 154th and 134th New York.', wording='Map label: "COSTAR 1\' 3.45"')
evening('cos3', 'US-COS', (4710, 4250), 'East Cemetery Hill')
pos('smi1', 'US-SMI', [(4640, 4310), (4590, 4420), (4605, 4610)], None, ('14:00', '17:30'), 'In reserve, holding the hill', 'Cemetery Hill, along the Taneytown and Emmitsburg roads',
    start=('unknown', '14:00'), tb=NOTIME + 'S16 has the division arriving at 2:00 p.m. and held on Cemetery Hill.', src='S18; S16')

# ---- Heth's division
pos('arc2', 'CS-ARCH', [(2987, 3083), (2935, 3370)], None, ('10:15', '10:45'), 'Line of battle, engaged', 'West bank of Willoughby Run, opposite Herbst Woods',
    start=('10:15', '10:15'), tb=FACE("Meredith's line", '10.15 A.M.'), basis='Thin bars with the regiment numbers of the brigade; the 1st Tennessee is drawn a little to the south.')
pos('arc3', 'CS-ARCH', [(2310, 3870), (2400, 3740)], None, ('13:00', '17:30'), 'Re-formed on the right of the division', 'Herr Ridge, south of the Springs road woods',
    start=('unknown', 'unknown'), prec=60, conf='low', tb=NOTIME + 'S16 has the brigade repulsed and Archer taken by 11:30 a.m.', src='S18; S16',
    basis='Read near the edge of a crop of the scan, so less exact than the other rows.')
pos('dav4', 'CS-DAV', [(3140, 2875), (3285, 2780)], '3.30 P.M.', ('15:30', '15:50'), 'Line of battle', 'North of the Chambersburg Pike, west of the McPherson farm',
    start=('unknown', '15:30'), wording='Map label: "DAVIS MISS. 3.30 P.M."', notes='Where the brigade re-formed between the railroad cut and 3.30 p.m. is not read from the map.')
pos('pet2', 'CS-PETT', [(2370, 3450)], None, ('11:00', '14:30'), 'Waiting in the woods', 'Herr Ridge woods, south of the pike',
    start=('unknown', 'unknown'), tb=NOTIME + 'S49 has Heth attacking again about 2:30 P.M.; S16 has Pettigrew attacking at 3:00 p.m.', src='S18; S49; S16', conf='low', basis='Centre of four thin bars.')
pos('pet3', 'CS-PETT', [(3185, 3265), (3080, 3650)], None, ('15:00', '15:45'), 'Line of battle after the attack', 'McPherson Ridge, east of Willoughby Run, where Meredith and Biddle had stood',
    start=('14:30', '15:00'), tb=NOTIME + "The First Corps lines it took are labelled to 2.30 and 3 P.M. S49: about 2:30 P.M.; S16: 3:00 p.m.", src='S18; S49; S16',
    basis='From the north: 11th, 26th, 47th and 52nd North Carolina.')
pos('bro2', 'CS-BROCK', [(2560, 3040)], None, ('11:00', '14:30'), 'Waiting in the woods', 'Herr Ridge woods, south of the pike',
    start=('unknown', 'unknown'), tb=NOTIME + 'S49 has Heth attacking again about 2:30 P.M.', src='S18; S49', conf='low', basis='Centre of four thin bars.')
pos('bro3', 'CS-BROCK', [(3200, 2930), (3085, 3270)], None, ('15:00', '15:45'), 'Line of battle after the attack', 'McPherson Ridge, from the pike south to Herbst Woods',
    start=('14:30', '15:30'), tb=NOTIME + "Stone's line, which it faces, is labelled to 3.30 P.M.", src='S18; S49')

# ---- Pender's division
P3 = "Lane's bars in the same line are labelled 3 P.M."
pos('sca1', 'CS-SCA', [(1960, 2935), (2300, 2450)], None, ('14:00', '15:20'), 'Line of battle, in support of Heth', 'Herr Ridge, south of the Chambersburg Pike',
    start=('unknown', '15:00'), tb=NOTIME + P3, basis='From the south: 16th, 22nd, 34th, 13th and 38th North Carolina.')
pos('sca2', 'CS-SCA', [(3610, 3045), (3500, 3180), (3440, 3250), (3385, 3415)], '4 P.M.', ('16:00', '16:15'), 'Attacking the seminary line', 'The swale west of Seminary Ridge, south of the pike',
    start=('unknown', '16:00'), wording='Map label: "SCALES N.C. 4 P.M."')
pos('per1', 'CS-PER', [(2190, 3380), (2260, 3090), (2350, 2850)], None, ('14:00', '15:20'), 'Line of battle, in support of Heth', 'Herr Ridge, behind the woods',
    start=('unknown', '15:00'), tb=NOTIME + P3)
pos('per2', 'CS-PER', [(3440, 3400), (3436, 3590), (3515, 3665), (3560, 3685)], '4 P.M.', ('16:00', '16:15'), 'Attacking the seminary line', 'West of the seminary, down to the Fairfield road',
    start=('unknown', '16:00'), wording='Map label: "McGOWAN S.C. 4 P.M."')
pos('lan1', 'CS-LANE', [(2195, 3430), (2110, 3900)], '3 P.M.', ('14:00', '15:20'), 'Line of battle, on the right', 'Herr Ridge, south of the Springs road woods',
    start=('unknown', '15:00'), wording='Map label: "LANE N.C. 3 P.M."', prec=60, basis='The south end is read near the edge of a crop of the scan.')
pos('lan2', 'CS-LANE', [(3470, 3765), (3440, 3990), (3410, 4130), (3345, 4250)], '4 P.M.', ('16:00', '16:15'), 'Line of battle', 'West of Seminary Ridge, south of the Fairfield road',
    start=('unknown', '16:00'), wording='Map label: "LANE N.C. 4 P.M."', basis='From the north: 33rd, 18th, 28th and 37th North Carolina; the 7th is drawn deployed to the right.')
pos('tho1', 'CS-THO', [(2360, 2440), (2500, 2250)], None, ('14:00', '17:30'), 'In reserve, supporting the artillery', 'Herr Ridge, north of the Chambersburg Pike',
    start=('unknown', 'unknown'), tb=NOTIME + P3, conf='low')

# ---- Rodes's division
pos('ive1', 'CS-IVER', [(3200, 1525), (3590, 1520)], '1 P.M.', ('13:00', '14:15'), 'Line of battle', 'Oak Hill, north of the Forney farm', start=('unknown', '13:00'),
    wording='Map label: "IVERSON N.C." in the line labelled 1 P.M.')
pos('ive2', 'CS-IVER', [(3925, 2240), (3840, 2390), (3760, 2520)], None, ('14:35', '15:10'), 'Attack, repulsed', "Forney's field, in front of Baxter's line on Oak Ridge",
    start=('14:30', 'unknown'), tb=NOTIME + 'S16 has Rodes attacking at 2:30 p.m.', src='S18; S16; S49', basis='From the north: 5th, 20th, 23rd and 12th North Carolina.')
pos('one1', 'CS-ONEAL', [(3680, 1490), (4240, 1505)], '1 P.M.', ('13:00', '14:15'), 'Line of battle', 'Oak Hill, east of the Cobean farm', start=('unknown', '13:00'), wording='Map label: "O\'NEAL ALA. 1 P.M."')
pos('one2', 'CS-ONEAL', [(3990, 2225), (4190, 2310)], None, ('14:30', '15:10'), 'Attack, repulsed', 'East slope of Oak Ridge at the McLean farm',
    start=('14:30', 'unknown'), tb=NOTIME + 'S16 has Rodes attacking at 2:30 p.m.', src='S18; S16; S49')
pos('dol1', 'CS-DOLES', [(4290, 1510), (4790, 1530)], '1 P.M.', ('13:00', '13:45'), 'Line of battle', 'The plain east of Oak Hill, across the Newville road', start=('unknown', '13:00'), wording='Map label: "DOLES GA. 1 P.M."')
pos('dol1b', 'CS-DOLES', [(4160, 1975), (4720, 2000)], None, ('14:15', '14:50'), 'Line of battle', 'North of the Blocher farm', start=('unknown', 'unknown'), tb=NOTIME + 'It lies between the lines labelled 1 P.M. and 3 P.M.', conf='low')
pos('dol2', 'CS-DOLES', [(4500, 2210), (4650, 2160), (4800, 2110)], '3 P.M.', ('15:00', '15:15'), 'Advancing', 'South of the Blocher farm lane', start=('unknown', '15:00'), wording='Map label: "DOLES GA. 3 P.M."',
    basis='44th, 4th and 12th Georgia; the 21st is drawn apart to the west.')
pos('dol3', 'CS-DOLES', [(4150, 2100), (4265, 2135), (4330, 2200), (4400, 2280), (4480, 2380)], '3.30 P.M.', ('15:30', '15:50'), 'Line of battle, engaged', 'Fields between the Mummasburg and Carlisle roads',
    start=('unknown', '15:30'), wording='Map label: "DOLES GA. 3.30 P.M."')
pos('dan1', 'CS-DAN', [(3200, 2115), (3810, 2150)], None, ('14:15', '14:50'), 'Line of battle', 'South slope of Oak Hill, at the Forney farm',
    start=('unknown', 'unknown'), tb=NOTIME + 'It lies between the 1 P.M. line and the brigade\'s 3.30 P.M. line.', conf='low')
pos('dan2', 'CS-DAN', [(3250, 2685), (3515, 2850)], '3 1/2 P.M.', ('15:30', '15:50'), 'Line of battle', 'North edge of the railroad cut, facing Stone', start=('unknown', '15:30'), wording='Map label: "DANIELS N.C. 3 1/2 P.M."')
pos('ram1', 'CS-RAM', [(3830, 2135), (4090, 2145)], None, ('14:30', '15:05'), 'In reserve', 'North of the McLean farm, on Oak Ridge', start=('unknown', 'unknown'), tb=NOTIME + 'S49 has Ramseur renewing the attack after Iverson and O\'Neal failed.', src='S18; S49', conf='low')
pos('ram2', 'CS-RAM', [(3900, 2390), (3800, 2640)], None, ('15:20', '16:00'), 'Attack', "Forney's field, against the angle on Oak Ridge",
    start=('unknown', 'unknown'), tb=FACE("Paul's line", '3-4 P.M.'), src='S18; S49', conf='low')

# ---- Early's division
pos('gor1', 'CS-GORD', [(5215, 1565), (5530, 1840)], None, ('14:30', '14:50'), 'Deployed for the attack', 'West of the Harrisburg road, north of Rock Creek',
    start=('unknown', 'unknown'), tb=NOTIME + 'Open bars (a first position). The next line is labelled 3 P.M.', conf='low')
pos('gor2', 'CS-GORD', [(4795, 2000), (4950, 2022), (5080, 2070), (5190, 2110)], '3 P.M.', ('15:00', '15:25'), 'Attack', "Rock Creek at Blocher's (Barlow's) Knoll",
    start=('unknown', '15:00'), wording='Map label: "GORDON GA. 3 P.M."', notes='S16 puts this attack at 3:30 p.m.; see the Conflicts sheet.')
pos('hay1', 'CS-HAYS', [(5480, 1555), (5790, 1750)], None, ('14:30', '15:10'), 'Deployed', 'Across the Harrisburg road', start=('unknown', 'unknown'), tb=NOTIME + 'Open bars (a first position).', conf='low')
pos('hay2', 'CS-HAYS', [(4860, 2850), (4960, 2930), (5060, 3010), (5130, 3060)], '3.45 P.M.', ('15:45', '16:00'), 'Line of battle, advancing on the town', 'North-east of the town, north of Stevens Run',
    start=('unknown', '15:45'), wording='Map label: "HAYS LA. 3.45 P.M."')
pos('ave1', 'CS-AVERY', [(5800, 1770), (6100, 1925)], None, ('14:30', '15:10'), 'Deployed', 'East of the Harrisburg road', start=('unknown', 'unknown'), tb=NOTIME + 'Open bars (a first position).', conf='low')
pos('ave2', 'CS-AVERY', [(5130, 3065), (5210, 3130), (5300, 3210)], '3.45 P.M.', ('15:45', '16:00'), 'Line of battle, advancing on the town', 'North-east of the town, from Stevens Run to the railroad',
    start=('unknown', '15:45'), wording='Map label: "HOKE N.C." in the line labelled 3.45 P.M.')

# ---------------------------------------------------------------- tracks
T = wb['Tracks']; th = head(T)
rows = {r[1].value: r for r in T.iter_rows(min_row=2) if r[0].value == 'gettysburg'}
col = lambda name: th.index(name)
m = made


def extend(track, keys): rows[track][col('rows')].value += '; ' + '; '.join(m[k] for k in keys)


extend('US-B1', ['gam4', 'buf430']); extend('US-B2', ['dev2', 'buf430'])
extend('CS-ARCH', ['arc2', 'arc3']); extend('CS-DAV', ['dav4']); extend('CS-PETT', ['pet2', 'pet3']); extend('CS-BROCK', ['bro2', 'bro3'])
for t in ('US-6NY', 'US-B2-sk', 'US-A2-R', 'US-A2-N', 'US-A2-P'): rows[t][col('hide_after_last_row')].value = 'yes'
t_like = rows['CS-BROCK'][0].row; g_last = max(r[0].row for r in rows.values())
new = [('US-MER', ['mer1', 'mer2', 'mer3']), ('US-CUT', ['cut1', 'cut3', 'cut4']), ('US-CUT-L', ['cut1L', 'cut2L']), ('US-PAUL', ['paul1', 'paul2', 'paul3']), ('US-BAX', ['bax1', 'bax2', 'bax3']),
       ('US-STONE', ['sto1', 'sto2', 'sto3']), ('US-BID', ['bid1', 'bid2', 'bid3', 'bid4']), ('US-GIL', ['gil1', 'gil2']), ('US-AMES', ['ames1', 'ames2', 'ames3']),
       ('US-AMS', ['ams1', 'ams2', 'xi345', 'ams3']), ('US-KRZ', ['krz1', 'xi345', 'krz2']), ('US-COS', ['cos1', 'cos2', 'cos3']), ('US-SMI', ['smi1']),
       ('CS-SCA', ['sca1', 'sca2']), ('CS-PER', ['per1', 'per2']), ('CS-LANE', ['lan1', 'lan2']), ('CS-THO', ['tho1']),
       ('CS-IVER', ['ive1', 'ive2']), ('CS-ONEAL', ['one1', 'one2']), ('CS-DOLES', ['dol1', 'dol1b', 'dol2', 'dol3']), ('CS-DAN', ['dan1', 'dan2']), ('CS-RAM', ['ram1', 'ram2']),
       ('CS-GORD', ['gor1', 'gor2']), ('CS-HAYS', ['hay1', 'hay2']), ('CS-AVERY', ['ave1', 'ave2'])]
T.insert_rows(g_last + 1, len(new))        # keep the Gettysburg tracks together; the sheet has no formulas
for i, (tid, keys) in enumerate(new):
    r = g_last + 1 + i
    for j in range(1, len(th) + 1):
        c = T.cell(r, j); s = T.cell(t_like, j)
        if s.has_style: c._style = copy.copy(s._style)
    T.cell(r, 1).value = 'gettysburg'; T.cell(r, 2).value = tid; T.cell(r, 3).value = 'US-CUT' if tid == 'US-CUT-L' else tid
    T.cell(r, col('rows') + 1).value = '; '.join(m[k] for k in keys)
    if tid == 'US-CUT-L':
        T.cell(r, col('label') + 1).value = 'Cutler, left wing'; T.cell(r, col('echelon') + 1).value = 'regiment'; T.cell(r, col('hide_after_last_row') + 1).value = 'yes'

# ---------------------------------------------------------------- events
E = wb['Events']; eh = head(E)
e_rows = [r for r in E.iter_rows(min_row=2) if r[1].value == 'ACW-GETT']; e_like = e_rows[-1][0].row
for r in e_rows:
    if r[0].value == 'GE06': r[eh.index('summary')].value = "Davis is in line against Cutler's brigade of the First Corps north of the pike, Meredith's brigade meets Archer at Willoughby Run, and the cavalry is relieved."; r[eh.index('pos_ids')].value = 'P37; P05; %s; %s' % (m['mer1'], m['cut1'])
EV = [('GE07', '10:30', '10:30', 'Railroad cut', "The 6th Wisconsin, 95th New York and 14th Brooklyn charge Davis's men in the unfinished railroad cut. The map times it 10.30 a.m.", ['cut2L'], 'S18', None),
      ('GE08', '10:50', '10:50', 'Reynolds killed', 'Reynolds is shot while placing the Iron Brigade at Herbst Woods, and Doubleday takes over the First Corps. The time is from a modern timeline; no primary source read here gives it.', ['mer1'], 'S16', None),
      ('GE09', '11:30', '11:30', 'Morning attack fails', "Heth's two brigades are driven back, Archer is a prisoner, and the firing dies down. The rest of the First Corps comes up over the next half hour.", ['arc2', 'sto1', 'bid1'], 'S16; S49', None),
      ('GE10', '13:00', '13:00', 'Rodes on Oak Hill', "Rodes's division is in line on Oak Hill, north of the First Corps, as two divisions of the Eleventh Corps form north of the town.", ['ive1', 'one1', 'dol1', 'bax1', 'ams1'], 'S18; S16', None),
      ('GE11', '14:30', '14:30', 'Rodes attacks', "O'Neal and Iverson attack Oak Ridge one after the other and are thrown back by Baxter's brigade; Iverson loses about 800 men.", ['ive2', 'one2', 'bax1'], 'S16; S49', None),
      ('GE12', '14:30', '15:00', 'Heth attacks again', "Pettigrew and Brockenbrough cross Willoughby Run against Meredith, Biddle and Stone. One source says about 2:30, another 3:00; the map shows the Union line here until 3 p.m.", ['pet3', 'bro3', 'mer1', 'bid2'], 'S49; S16; S18', '15:00'),
      ('GE13', '15:00', '15:30', 'Early strikes', "Gordon's brigade hits the knoll on Rock Creek that anchors the Eleventh Corps's right. The map times Gordon's line 3 p.m.; a modern timeline says 3:30.", ['gor2', 'gil1', 'ames1'], 'S18; S16', '15:05'),
      ('GE14', '15:30', '15:30', 'McPherson Ridge lost', "Stone gives up the McPherson farm as Daniel and Davis close on it, and Doles drives in the Eleventh Corps's left.", ['sto1', 'dan2', 'dav4', 'dol3', 'ams2'], 'S18', None),
      ('GE15', '15:45', '15:45', 'North of town breaks', "Hays and Avery sweep past Coster's brigade at the brickyard and the Eleventh Corps falls back into the streets.", ['hay2', 'ave2', 'cos2', 'xi345'], 'S18', None),
      ('GE16', '16:00', '16:00', 'Seminary Ridge', "Pender's brigades attack the last First Corps line at the seminary. About now Howard orders both corps back to Cemetery Hill.", ['sca2', 'per2', 'lan2', 'mer2', 'sto2', 'bid3', 'gam4'], 'S18; S49', None),
      ('GE17', '16:30', '16:30', 'Cemetery Hill', "The two corps rally on Cemetery Hill around Steinwehr's division as Hancock arrives. Ewell is told to take the hill if practicable and does not attack.", ['smi1', 'buf430', 'mer3', 'ams3'], 'S16; S49', '16:45')]
for eid, a, b, name, text, keys, src, at in EV:
    add(E, {'event_id': eid, 'campaign_id': 'ACW-GETT', 'battle_id': 'GETT-D1', 'time_earliest': D + a, 'time_latest': D + b, 'name': name, 'summary': text, 'pos_ids': '; '.join(m[k] for k in keys),
            'source_ids': src, 'timeline': 'name', 'playback_at': D + (at or a)}, like=e_like)

# ---------------------------------------------------------------- conflicts and gaps
C = wb['Conflicts']; ch = head(C); c_like = [r[0].row for r in C.iter_rows(min_row=2) if r[0].value == 'C09'][0]
for cid, q, says, how, comment in [
    ('C10', "When did Early's division attack?", 'S18 (the map): Gordon\'s line at the knoll is labelled "3 P.M." and Hays\'s and Hoke\'s lines near the town "3.45 P.M." | S16: Gordon hits the Union right at 3:30 p.m. and the Eleventh Corps withdraws at 4:00.',
     'Used the map: 3:00 for Gordon (row %s), 3:45 for Hays and Avery.' % m['gor2'], 'The reports of Early and Gordon have not been read.'),
    ('C11', "When did Heth's second attack go in?", 'S49: "about 2:30 P.M." | S16: Pettigrew attacks at 3:00 p.m. | S18 (the map): Meredith\'s line is labelled "10.15 A.M. - 3 P.M.", Biddle changes position at "2.30 P.M.", Stone holds until "3.30 P.M.".',
     'Held as a range, 2:30 to 3:00, on rows %s and %s; the playback shows the Confederate line on the ridge from 3:00.' % (m['pet3'], m['bro3']), "Heth's and Pettigrew's brigade reports for the afternoon have not been read."),
    ('C12', 'When was Reynolds killed?', 'S16: 10:50 a.m. | The map labels the Iron Brigade\'s line, which he was placing, from "10.15 A.M.". Other accounts, not read here, give times from about 10:15 to 10:45.',
     'The event uses 10:50 from S16 and says where the time comes from.', 'Needs a primary source.')]:
    add(C, {'conflict_id': cid, 'battle_id': 'GETT-D1', 'question': q, 'what the sources say': says, 'how the pilot handled it': how, 'comment': comment, 'status': 'Open'}, like=c_like)
Gp = wb['Gaps']; g_like = [r[0].row for r in Gp.iter_rows(min_row=2) if r[0].value == 'G17'][0]
for gid, gap, effect, close in [
    ('G18', 'The afternoon of 1 July rests on the map alone', 'The %d new rows come from Bachelder\'s map, with two modern summaries for the order of events. No brigade or division report for the afternoon has been read, so nothing cross-checks the map.' % (pnum[0] - 39),
     "Read the reports of Doubleday, Howard, Schurz, Rodes, Early, Pender and the brigade commanders in the Official Records, vol. 27."),
    ('G19', 'Evening positions on Cemetery Hill are estimates', 'Eleven Union brigades end the day at a point placed on the hill by eye (marked estimate, 300 m). The sources read say only that the corps rallied there.',
     "Read Bachelder's second-day map, which draws each brigade on the hill, and the reports. Accounts not read here send Wadsworth's division on to Culp's Hill that evening."),
    ('G20', 'Units left out of the afternoon', "Smith's brigade of Early's division, the artillery of both sides, Calef's battery after 10:15, the 6th Wisconsin as a separate unit, and all regiments after the morning are not entered. Commanders of the new brigades are from general knowledge.",
     'Add them from the map and check commanders against the order of battle in the Official Records.'),
    ('G21', 'Long stretches with no position', "Cutler's right wing from 10:30 to 3 p.m., Davis from the railroad cut to 3:30, Gamble from 10:40 to 4 p.m. and Devin for most of the day have no row. The playback draws a slow straight move between the rows on either side, or nothing.",
     'Read the brigade reports; the map draws some intermediate positions that were not picked.')]:
    add(Gp, {'gap_id': gid, 'battle_id': 'GETT-D1', 'gap': gap, 'effect on the data': effect, 'how to close it': close}, like=g_like)

# ---------------------------------------------------------------- playback and settings
PB = wb['Playbacks']; bh = head(PB)
for r in PB.iter_rows(min_row=2):
    if r[0].value == 'gettysburg':
        s = lambda k, v: setattr(r[bh.index(k)], 'value', v)
        s('battle_file_id', 'gettysburg-day1'); s('title', 'Gettysburg, the first day'); s('subtitle', "Buford's cavalry, then the First and Eleventh Corps, against Heth, Pender, Rodes and Early")
        s('time_end', D + '17:30'); s('focus_end', D + '17:00')
PS = wb['Playback settings']
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'gettysburg' and r[1].value == 'about.1':
        r[2].value = ("Unit positions come from the WarMapper battle data workbook (%d rows for this day). The morning is built from the Official Records, War Department tablets and Bachelder's map; "
                      "from 10:15 on, the brigade positions and most of the times are read from Bachelder's map alone. Nothing here has been checked by a historian." % (pnum[0] - 1))
B = wb['Battles']; bth = head(B)
for r in B.iter_rows(min_row=2):
    if r[0].value == 'GETT-D1': r[bth.index('coord_source')].value = 'West and north of the town'

# ---------------------------------------------------------------- housekeeping: filters, drop-downs, counts, read me
last = P.max_row
P.auto_filter.ref = 'A1:AM%d' % last
for dv in P.data_validations.dataValidation:
    dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange('%s2:%s%d' % (str(dv.sqref)[:2].rstrip('0123456789'), str(dv.sqref)[:2].rstrip('0123456789'), last))
U.auto_filter.ref = 'A1:L%d' % U.max_row; E.auto_filter.ref = 'A1:I%d' % E.max_row; A.auto_filter.ref = 'A1:I%d' % A.max_row
R = wb['Read me']
for row in R.iter_rows():
    for c in row:
        if isinstance(c.value, str) and c.value.startswith('=COUNTIF') and '315' in c.value: c.value = c.value.replace('315', str(last))
R['A2'].value = R['A2'].value.replace('the first morning at Gettysburg', 'the first day at Gettysburg')
merged = [str(x) for x in R.merged_cells.ranges]; heights = {k: v.height for k, v in R.row_dimensions.items() if v.height}
for x in merged: R.unmerge_cells(x)
R.insert_rows(4, 5)
for x in merged:        # openpyxl moves the cells but not the merged ranges or the row heights
    a, b = x.split(':'); ra, rb = int(a[1:]), int(b[1:]); sh = 5 if ra >= 4 else 0
    R.merge_cells('%s%d:%s%d' % (a[0], ra + sh, b[0], rb + sh))
for k in sorted(heights, reverse=True):
    if k >= 4: R.row_dimensions[k + 5].height = heights[k]
for k in range(4, 9): R.merge_cells('A%d:D%d' % (k, k)); R.row_dimensions[k].height = None
R.row_dimensions[5].height = 58; R.row_dimensions[6].height = 58
for i, txt in enumerate(['What changed on 15 November 2026: Gettysburg, the whole first day',
                         "Gettysburg only. The playback now runs from 7:15 a.m. to 5:30 p.m. %d position rows (P39 to P%d), 34 units, 25 tracks, 11 events (GE07 to GE17), 3 conflicts (C10 to C12) and 4 gaps (G18 to G21) are new. The brigades of the First and Eleventh Corps and of Heth's, Pender's, Rodes's and Early's divisions are entered; regiments and batteries after the morning are not." % (pnum[0] - 39, pnum[0] - 1),
                         "Every new position with coordinate source map_read was read from Bachelder's first-day map (S18) and carries the time printed beside its bars. Where the map prints no time the time_basis column says so and says what the shown time rests on. The eleven evening rows on Cemetery Hill are estimates (G19). All new rows are marked Needs review.",
                         None, None]):
    c = R.cell(4 + i, 1); src = R.cell(9 if i == 0 else (10 if txt else 8), 1)
    if src.has_style: c._style = copy.copy(src._style)
    c.value = txt
wb.save(WB)
print('positions P39 to P%d; assignments to A%03d' % (pnum[0] - 1, anum[0] - 1))
print(made)
