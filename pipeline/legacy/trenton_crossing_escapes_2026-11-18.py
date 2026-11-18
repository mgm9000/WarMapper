"""18 Nov 2026: Trenton crossing staged (the army as one, brigades crossing in turn), escapes shown, routes taken drawn."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB)
head = lambda ws: [c.value for c in ws[1]]


def add(ws, d, like=None):
    h = head(ws); r = ws.max_row + 1; like = like or ws.max_row
    for j, n in enumerate(h, 1):
        if ws.cell(like, j).has_style: ws.cell(r, j)._style = copy.copy(ws.cell(like, j)._style)
        if d.get(n) is not None: ws.cell(r, j).value = d[n]
    return r


def newcol(ws, title):
    h = head(ws)
    if title in h: return h.index(title) + 1
    j = len(h) + 1; ws.cell(1, j).value = title; ws.cell(1, j)._style = copy.copy(ws.cell(1, j - 1)._style); return j


D25, D26 = '1776-12-25 ', '1776-12-26 '
P = wb['Positions']
FERRY_PA = (40.29580, -74.87370)
POS = [
 dict(pos_id='T00', unit_id='T-US-ARMY', start_earliest=D25 + '14:00', start_latest=D25 + '15:00', end_earliest=D26 + '02:00', end_latest=D26 + '03:00',
      time_basis='Start: the regiments began moving to the ferry about 2 to 3 p.m. (S21). End: the last guns were over about 3 a.m. (S20; S59).', activity='Waiting to cross',
      place_description="Behind McKonkey's Ferry, Pennsylvania bank", geometry='point', lat=FERRY_PA[0], lon=FERRY_PA[1], coord_source='derived', coord_precision_m=300,
      coordinate_basis="The Pennsylvania landing of McKonkey's Ferry (today's Washington Crossing Historic Park), as used to fit Faden's map; the army waited in the fields behind it.",
      coordinate_confidence='medium', source_ids='S21; S20; S59', source_wording='Paraphrase: the regiments moved to the ferry in the afternoon and crossed through the night (S21; S59).',
      position_method='inferred', overall_confidence='medium', show_from=D25 + '16:00', show_to=D26 + '02:30',
      notes="Drawn as one symbol for the whole army until each brigade crosses. The order of crossing beyond Stephen's brigade first, Greene's division before Sullivan's and the guns last is not recorded: the brigades are spaced evenly through the night."),
 dict(pos_id='T62', unit_id='T-GB-16LD', start_earliest=D26 + '09:15', start_latest=D26 + '10:30', end_earliest=D26 + '11:30', end_latest=D26 + '11:30',
      time_basis='Arrival not recorded; about an hour and a half at a trot for 11 miles', activity='Reached Princeton', place_description="Princeton, where General Leslie's brigade lay",
      geometry='point', lat=40.3487, lon=-74.6593, coord_source='modern_map', coord_precision_m=500, coordinate_basis='Princeton town centre (Nassau Hall) on the current map',
      coordinate_confidence='high', source_ids='S59; S61', source_wording='Paraphrase: the twenty dragoons got over the Assunpink bridge as the attack began and rode for Princeton (S59, p. 45; S61).',
      position_method='stated', overall_confidence='medium', show_from=D26 + '09:45', show_to=D26 + '11:30', notes='Their road from the bridge is not recorded; it is drawn round the east of the town by the Quaker Bridge road.'),
 dict(pos_id='T63', unit_id='T-HE-PKRIV', start_earliest=D26 + '10:00', start_latest=D26 + '11:30', end_earliest=D26 + '11:30', end_latest=D26 + '11:30',
      time_basis='Arrival not recorded; about two and a half hours on foot for 7 miles', activity="Reached Bordentown (von Donop's brigade)", place_description='Bordentown',
      geometry='point', lat=40.1462, lon=-74.7118, coord_source='modern_map', coord_precision_m=500, coordinate_basis='Bordentown town centre on the current map', coordinate_confidence='high',
      source_ids='S20; S21', source_wording='Paraphrase: those not killed or taken fled down the road toward Bordentown (S20); some jägers fled to Bordentown (S21).',
      position_method='stated', overall_confidence='low', show_from=D26 + '10:50', show_to=D26 + '11:30', notes='S61 thinks the jägers followed the dragoons toward Princeton. See TC18.'),
 dict(pos_id='T64', unit_id='T-HE-KNYPX', start_earliest=D26 + '09:00', start_latest=D26 + '09:30', end_earliest=D26 + '09:15', end_latest=D26 + '09:45',
      time_basis='Inferred: just before the regiment surrendered', activity='Over the Assunpink by a ford', place_description='South bank of the Assunpink, east of the town',
      geometry='point', lat=40.21750, lon=-74.75800, coord_source='derived', coord_precision_m=300, coordinate_basis='Placed on the south bank of the Assunpink about half a mile above the bridge; the ford is not located in the sources read.',
      coordinate_confidence='low', source_ids='S59; S61', source_wording='Paraphrase: about fifty men of the regiment got over the creek, some by a ford after probing the marsh and some by swimming (S59, p. 48; S61).',
      position_method='inferred', overall_confidence='low', show_from=D26 + '09:15', show_to=D26 + '09:25'),
 dict(pos_id='T65', unit_id='T-HE-KNYPX', start_earliest=D26 + '11:00', start_latest=D26 + '12:30', end_earliest=D26 + '11:30', end_latest=D26 + '12:30',
      time_basis='Arrival not recorded; about two hours on foot for 7 miles', activity='Over the Crosswicks drawbridge', place_description='Crosswicks',
      geometry='point', lat=40.1543, lon=-74.6513, coord_source='modern_map', coord_precision_m=500, coordinate_basis='Crosswicks village on the current map', coordinate_confidence='high',
      source_ids='S61', source_wording="Paraphrase: Biesenrodt's party crossed the Crosswicks drawbridge and reached General Leslie about ten hours later (S61).",
      position_method='stated', overall_confidence='low', show_from=D26 + '11:25', show_to=D26 + '11:30', notes='Shown only as far as Crosswicks; the playback ends at 11:30.'),
]
like = [r[0].row for r in P.iter_rows(min_row=2) if r[0].value == 'T61'][0]
have = {r[0].value for r in P.iter_rows(min_row=2)}
for d in POS:
    if d['pos_id'] in have: continue
    d.update(campaign_id='ARW-TP', battle_id='TREN', review_status='Needs review'); add(P, d, like)

U = wb['Units']
if 'T-HE-KNYPX' not in {r[0].value for r in U.iter_rows(min_row=2)}:
    k = [r[0].row for r in U.iter_rows(min_row=2) if r[0].value == 'T-HE-KNYP'][0]
    add(U, dict(unit_id='T-HE-KNYPX', unit_name='Von Knyphausen regiment: the men who got away', map_label='Knyphausen (escaped)', side_id='ARW-CR', nation='Hesse-Cassel',
                branch='Infantry', echelon='Detachment', symbol_code='10061000161211000000', source_ids='S59; S61', **{'sourced?': 'yes'},
                notes='About fifty men under Capt. von Biesenrodt who forded or swam the Assunpink before the regiment surrendered.'), k)
    A = wb['Assignments']; a = [r[0].row for r in A.iter_rows(min_row=2) if r[1].value == 'T-HE-KNYP'][0]
    nid = 'A%03d' % (max(int(str(r[0].value)[1:]) for r in A.iter_rows(min_row=2) if str(r[0].value).startswith('A') and str(r[0].value)[1:].isdigit()) + 1)
    add(A, {'assign_id': nid, 'unit_id': 'T-HE-KNYPX', 'parent_unit_id': 'T-HE-KNYP', 'commander': 'Capt. von Biesenrodt', 'strength / equipment': 'about 50 (S59); about 53 (S61)',
            'valid_from': '1776-12-26', 'valid_to': '1776-12-26', 'source_ids': 'S59; S61'}, a)

R = wb['Routes']; like = [r[0].row for r in R.iter_rows(min_row=2) if r[0].value == 'RT11'][0]
RT = [
 ('RT12', 'T-GB-16LD', 'escape', D26 + '08:00', D26 + '09:45', 'T17', 'T62',
  '40.22124, -74.76206; 40.21900, -74.76390; 40.21816, -74.76413; 40.21650, -74.75900; 40.22300, -74.74000; 40.24600, -74.71500; 40.27200, -74.69600; 40.29500, -74.68300; 40.32000, -74.67200; 40.34870, -74.65930',
  'S59; S61', 'Paraphrase: over the Assunpink bridge and away to Princeton (S59; S61).', 'low', 'The road is not recorded: drawn over the bridge, round the east of the town and up the Quaker Bridge road, keeping clear of the American column on the Princeton road.'),
 ('RT13', 'T-HE-PKRIV', 'escape', D26 + '08:22', D26 + '10:50', 'T23', 'T63',
  '40.21816, -74.76413; 40.21200, -74.75800; 40.20300, -74.74400; 40.19000, -74.72900; 40.17500, -74.71800; 40.16000, -74.71300; 40.14620, -74.71180',
  'S20; S21', 'Paraphrase: they fled down the road toward Bordentown (S20).', 'low', 'Drawn along the road down the Delaware by Lamberton and White Horse; the exact road is not recorded.'),
 ('RT14', 'T-HE-KNYPX', 'escape', D26 + '09:25', D26 + '11:25', 'T64', 'T65',
  '40.21750, -74.75800; 40.21000, -74.74000; 40.19800, -74.72000; 40.18400, -74.69800; 40.16800, -74.67300; 40.15430, -74.65130',
  'S61', "Paraphrase: they made for the Crosswicks drawbridge (S61).", 'low', 'Drawn straight across country to Crosswicks; the road is not recorded.'),
]
have = {r[0].value for r in R.iter_rows(min_row=2)}
for rid, u, kind, s, e, a, b, w, src, sw, conf, n in RT:
    if rid in have: continue
    add(R, {'route_id': rid, 'campaign_id': 'ARW-TP', 'battle_id': 'TREN', 'unit_id': u, 'kind': kind, 'start': s, 'end': e, 'from_pos_id': a, 'to_pos_id': b,
            'waypoints (lat, lon; ...)': w, 'source_ids': src, 'source_wording': sw, 'confidence': conf, 'notes': n, 'playback': 'yes'}, like)

T = wb['Tracks']; mj = newcol(T, 'start_move_minutes'); th = head(T); c = lambda n: th.index(n)
CROSS = {'T-US-ADVW': '18:00', 'T-US-STEPH': '18:15', 'T-US-GREENE': '18:45', 'T-US-HQ': '19:15', 'T-US-MERC': '19:30', 'T-US-FERM': '20:30', 'T-US-STIR': '21:30',
         'T-US-SULL': '22:30', 'T-US-STARK': '23:00', 'T-US-ADVF': '23:15', 'T-US-STCL': '23:45', 'T-US-GLOV': '00:30', 'T-US-MOUL': '01:15', 'T-US-FORR': '01:45', 'T-US-HAM': '02:00'}
for r in T.iter_rows(min_row=2):
    if r[0].value != 'trenton': continue
    t = r[1].value
    if t in CROSS:
        hh = CROSS[t]; day = D25 if hh >= '12' else D26
        r[c('starts_from_row')].value = 'T00'; r[c('starts_at')].value = day + hh; T.cell(r[0].row, mj).value = 30
        assert str(r[c('rows')].value).startswith('T01; T02'), t
    if t == 'T-GB-16LD': r[c('rows')].value = 'T17; T62'; r[c('hide_after_last_row')].value = None
    if t == 'T-HE-PKRIV': r[c('rows')].value = 'T08; T23; T63'; r[c('hide_after_last_row')].value = None
tracks = {r[1].value for r in T.iter_rows(min_row=2) if r[0].value == 'trenton'}
like = [r[0].row for r in T.iter_rows(min_row=2) if r[0].value == 'trenton'][-1]
if 'T-US-ARMY' not in tracks:
    add(T, {'playback_id': 'trenton', 'track_id': 'T-US-ARMY', 'unit_id': 'T-US-ARMY', 'rows': 'T00', 'hide_after_last_row': 'yes'}, like)
if 'T-HE-KNYPX' not in tracks:
    add(T, {'playback_id': 'trenton', 'track_id': 'T-HE-KNYPX', 'unit_id': 'T-HE-KNYPX', 'rows': 'T64; T65', 'starts_from_row': 'T50', 'starts_at': D26 + '09:00', 'start_move_minutes': 15}, like)

PB = wb['Playbacks']; ph = head(PB)
for r in PB.iter_rows(min_row=2):
    if r[0].value == 'trenton':
        r[ph.index('time_zero')].value = D25 + '12:00'; r[ph.index('time_start')].value = D25 + '16:00'; r[ph.index('time_end')].value = D26 + '11:30'
        r[ph.index('calendar_first')].value = '1776-12-25'; r[ph.index('calendar_days')].value = 2
        r[ph.index('opening_label')].value = 'Before the crossing'
        r[ph.index('opening_text')].value = ("Christmas afternoon: Washington's army waits behind McKonkey's Ferry on the Pennsylvania bank. Through the night each brigade crosses the ice-choked river "
                                             "and forms on the New Jersey bank; the crossing runs about three hours late.")

PS = wb['Playback settings']
last = max(x[0].row for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'); have = {x[1].value for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'}
for k, v, d in [('trails.on', True, 'Routes taken: the road each unit has marched so far, drawn under the units as the clock runs (Layers: Routes taken).'),
                ('trails.opacity', 0.55, 'How strongly the routes taken are drawn (0 to 1).')]:
    if k in have: continue
    PS.insert_rows(last + 1, 1); last += 1
    for j in range(1, 5):
        if PS.cell(last - 1, j).has_style: PS.cell(last, j)._style = copy.copy(PS.cell(last - 1, j)._style)
    PS.cell(last, 1).value = 'trenton'; PS.cell(last, 2).value = k; PS.cell(last, 3).value = v; PS.cell(last, 4).value = d

C = wb['Conflicts']; ch = head(C)
if 'TC18' not in {r[0].value for r in C.iter_rows(min_row=2)}:
    like = [r[0].row for r in C.iter_rows(min_row=2) if r[0].value == 'TC17'][0]
    add(C, {'conflict_id': 'TC18', 'battle_id': 'TREN', 'question': 'Where did the jägers go?',
            'what the sources say': "S20 and S21: down the road toward Bordentown (some of them, S21). | S61: they followed the dragoons, so probably toward Princeton (its inference).",
            'how the pilot handled it': 'The jäger picket (T-HE-PKRIV) is drawn going to Bordentown (T63), low confidence.', 'status': 'Open'}, like)

E = wb['Events']; eh = head(E)
if 'TE16' not in {r[0].value for r in E.iter_rows(min_row=2)}:
    like = [r[0].row for r in E.iter_rows(min_row=2) if r[0].value == 'TE15'][0]
    add(E, {'event_id': 'TE16', 'campaign_id': 'ARW-TP', 'battle_id': 'TREN', 'time_earliest': D26 + '09:15', 'time_latest': D26 + '11:30', 'name': 'The escapers get away',
            'summary': "The British dragoons reach Princeton, the jägers Bordentown, and about fifty men of the Knyphausen regiment, who forded the Assunpink, make for Crosswicks. Some 400 to 600 of the garrison got away in all.",
            'pos_ids': 'T62; T63; T65', 'source_ids': 'S20; S21; S59; S61', 'timeline': 'dot', 'playback_at': D26 + '10:30'}, like)
wb.save(WB); print('data done')
