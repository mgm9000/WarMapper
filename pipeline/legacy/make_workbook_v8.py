"""One-off: make the master workbook (data/WarMapper battle data.xlsx) from the v7 pilot workbook and the three battle files
as they stood on 15 Nov 2026. It adds what only the per-battle scripts knew: when each row is shown, which rows make up each symbol,
the playback settings, map labels, period maps, nations. After this the workbook is edited directly and this script is not run again.
Usage: python3 make_workbook_v8.py <repo root>"""
import sys, json, os, openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
R = sys.argv[1]
SRC = R + '/data/Military Map Explorer data pilot v7.xlsx'; OUT = R + '/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(SRC)
BT = {b: json.load(open('%s/playbacks/%s/battle.json' % (R, b), encoding='utf-8')) for b in ('gettysburg', 'trenton', 'ypres')}
CAMP = {'gettysburg': 'ACW-GETT', 'trenton': 'ARW-TP', 'ypres': 'WW1-FL14'}
HEAD = Font(bold=True, color='FFFFFF'); FILL = PatternFill('solid', fgColor='1F3A5F'); NEW = PatternFill('solid', fgColor='2E6B4F')
def t(s): return None if s is None else s.replace('T', ' ')          # the workbook writes times as 'YYYY-MM-DD HH:MM'
def header(ws): return [c.value for c in ws[1]]
def add_cols(ws, names):
    h = header(ws); n = len(h)
    for i, name in enumerate(names):
        c = ws.cell(1, n + 1 + i, name); c.font = HEAD; c.fill = NEW; c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.column_dimensions[c.column_letter].width = 22
    return {name: n + 1 + i for i, name in enumerate(names)}
def rows_by_id(ws):
    return {ws.cell(r, 1).value: r for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value}
def sheet(name, cols, rows, widths=None):
    ws = wb.create_sheet(name)
    for i, c in enumerate(cols):
        x = ws.cell(1, i + 1, c); x.font = HEAD; x.fill = FILL; x.alignment = Alignment(wrap_text=True, vertical='top')
        ws.column_dimensions[x.column_letter].width = (widths or {}).get(c, 18)
    for r in rows:
        ws.append([r.get(c) for c in cols])
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'C2'; return ws

# ---- Positions: when the playback shows each row; positions on a map that is not to scale ----
ws = wb['Positions']; col = add_cols(ws, ['show_from', 'show_to', 'moves_along_line', 'map_id', 'map_xy']); rid = rows_by_id(ws); H = header(ws)
for b, B in BT.items():
    for tr in B['tracks']:
        for s in tr['steps']:
            if s.get('virtual') or s.get('shared'): continue
            r = rid[s['id']]
            ws.cell(r, col['show_from'], t(s['show'][0])); ws.cell(r, col['show_to'], t(s['show'][1]))
            if s.get('along'): ws.cell(r, col['moves_along_line'], 'yes')
            for mid, xy in (s.get('on') or {}).items():
                ws.cell(r, col['map_id'], mid); ws.cell(r, col['map_xy'], '; '.join('%g, %g' % (x, y) for x, y in xy))
            if s['id'] == 'T05': ws.cell(r, H.index('notes') + 1, s['notes'])   # carries the note on when the playback shows the halt
# ---- Events: how the playback's timeline uses each ----
ws = wb['Events']; col = add_cols(ws, ['timeline', 'playback_at', 'playback_label', 'playback_text']); rid = rows_by_id(ws); H = header(ws)
used = {}
for b, B in BT.items():
    for e in B['events']: used[e['id']] = e
for eid, r in rid.items():
    e = used.get(eid)
    if not e: ws.cell(r, col['timeline'], 'off'); continue
    ws.cell(r, col['timeline'], 'dot' if e.get('quiet') else 'name'); ws.cell(r, col['playback_at'], t(e['at']))
    if e.get('label'): ws.cell(r, col['playback_label'], e['label'])
    if e['text'] != ws.cell(r, H.index('summary') + 1).value: ws.cell(r, col['playback_text'], e['text'])
# ---- Routes: whether the playback moves the unit along the route (Gettysburg's two are not used yet) ----
ws = wb['Routes']; col = add_cols(ws, ['playback']); H = header(ws)
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 1).value: ws.cell(r, col['playback'], 'yes' if ws.cell(r, H.index('campaign_id') + 1).value == 'ARW-TP' else 'no')
# ---- Sides: the short code and the name the panel uses ----
ws = wb['Sides']; col = add_cols(ws, ['code', 'short']); rid = rows_by_id(ws)
for B in BT.values():
    for s in B['sides']: ws.cell(rid[s['id']], col['code'], s['code']); ws.cell(rid[s['id']], col['short'], s['short'])

# ---- Playbacks: one row per playback ----
PB = []
for b, B in BT.items():
    T, V = B['time'], B['view']
    PB.append({'playback_id': b, 'battle_file_id': B['id'], 'campaign_id': CAMP[b], 'record_battles': '; '.join(B['record']['battles']), 'title': B['title'], 'subtitle': B['subtitle'],
               'time_unit': T['unit'], 'time_zero': t(T['zero']), 'time_start': t(T['start']), 'time_end': t(T['end']),
               'focus_start': t(T['focus'][0]) if T.get('focus') else None, 'focus_end': t(T['focus'][1]) if T.get('focus') else None,
               'calendar_first': T['calendar']['first'], 'days_numbered': 'yes' if T['calendar']['numbered'] else 'no', 'calendar_days': T['calendar'].get('days'),
               'origin_lat': V['origin'][1], 'origin_lon': V['origin'][0], 'west': V['extent'][0], 'south': V['extent'][1], 'east': V['extent'][2], 'north': V['extent'][3],
               'opening_label': B['opening']['label'], 'opening_text': B['opening']['text']})
sheet('Playbacks', list(PB[0].keys()), PB, {'title': 30, 'subtitle': 40, 'opening_text': 60, 'record_battles': 26})
# ---- Playback settings: one setting per row ----
WHAT = {'page_title': 'The browser tab title', 'style': 'tactical (a battlefield) or operational (a front)', 'scale_bar': 'yards or km', 'rate': 'Time units played per second',
        'question_mark': 'What marks a unit as doubtful: location (how sure the place is) or overall',
        'bounds': 'Map id: the reader cannot pan beyond this map', 'follow.min': 'Smallest box the camera frames, metres [width, height]', 'follow.margin': 'Space around the units, metres',
        'follow.exclude': 'Tracks the camera ignores', 'follow.empty': 'The view shown while no unit is placed (a preset)', 'zoom.max': 'Closest zoom, screen pixels per metre',
        'zoom.fold': 'Below this zoom units fold into their parent', 'zoom.labels': 'From this zoom, level 1 names show', 'zoom.towns_until': 'Town names hide above this zoom',
        'zoom.follow_max': 'Closest the Follow camera goes', 'zoom.landmarks_from': 'Landmarks show from this zoom', 'zoom.minor_roads_from': 'Side streets show from this zoom',
        'zoom.force_names_from': 'From this zoom, main units keep their names even when crowded', 'zoom.full_names': 'From this zoom, a place shows its other name too', 'zoom.woods_from': 'Wood names show from this zoom',
        'zoom.min_factor': 'How far out the reader can zoom (1 = the whole battle just fits)', 'fold.label': 'Name of the button that switches folding', 'fold.formation': 'Hide a unit while its parent formation has its own line and the reader is zoomed out',
        'fold.sides': 'Side codes that folding by formation applies to', 'rules.blend': 'Minutes over which a unit shifts from one row to the next when they meet',
        'lead.share': 'Share of the timeline given to the stretch before the focus', 'lead.rate': 'Time units per second in that stretch', 'lead.step': 'Minutes an arrow key moves in that stretch',
        'time_note.from': 'From this time a note shows under the clock', 'time_note.text': 'The note', 'rear.side': 'Side code whose symbols sit towards the rear point', 'rear.lat': 'The rear point', 'rear.lon': 'The rear point',
        'preset': 'A named view: [west, south, east, north]', 'bases': 'A map the reader can put under the units; the first is the opening one', 'views': 'A named-view button', 'groups': 'Units drawn as one symbol when zoomed right out',
        'texts': 'The sentence under this state in the unit panel', 'found': 'Words for how a place was found', 'about': 'A paragraph under "About this prototype"'}
SET = []
def flat(pb, path, v):
    if isinstance(v, dict):
        for k, x in v.items(): flat(pb, path + [k], x)
    elif isinstance(v, list) and v and all(not isinstance(x, (dict, list)) for x in v) and path[0] != 'about':
        SET.append({'playback_id': pb, 'setting': '.'.join(path), 'value': json.dumps(v)})
    elif isinstance(v, list):
        for i, x in enumerate(v): flat(pb, path + [str(i + 1)], x)
    else: SET.append({'playback_id': pb, 'setting': '.'.join(path), 'value': v})
for b, B in BT.items():
    P = json.loads(json.dumps(B['playback']))
    P['question_mark'] = 'location' if b == 'gettysburg' else 'overall'
    if 'rear' in P: lon, lat = P['rear'].pop('at'); P['rear']['lat'] = lat; P['rear']['lon'] = lon
    flat(b, [], P)
    for name, box in B['view'].get('presets', {}).items(): SET.append({'playback_id': b, 'setting': 'preset.' + name, 'value': json.dumps(box)})
for s in SET:
    k = s['setting']; s['what it does'] = WHAT.get(k) or WHAT.get(k.split('.')[0]) or ''
sheet('Playback settings', ['playback_id', 'setting', 'value', 'what it does'], SET, {'setting': 26, 'value': 70, 'what it does': 60})
# ---- Tracks: one row per symbol on the map ----
TR = []
ROUTES = {}
ws = wb['Routes']; H = header(ws)
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[0]: ROUTES[r[0]] = [[round(float(q.split(',')[1]), 6), round(float(q.split(',')[0]), 6)] for q in str(r[H.index('waypoints (lat, lon; ...)')]).split(';')]
for b, B in BT.items():
    for tr in B['tracks']:
        st = tr['steps']; row = {'playback_id': b, 'track_id': tr['id'], 'unit_id': tr['unit'], 'rows': '; '.join(s['id'] for s in st if not s.get('virtual')),
               'label': tr.get('label'), 'echelon': tr.get('echelon'), 'part_of_track': tr.get('parent'), 'hide_after_last_row': 'yes' if tr.get('hide_after') else None,
               'hold_until': t(tr.get('hold_until')), 'loose': 'yes' if tr.get('loose') else None, 'off_map': tr.get('off_map'),
               'nudge': ('%g, %g' % tuple(tr['nudge'])) if tr.get('nudge') is not None else None}
        if st[0].get('virtual'):   # the symbol sets off from a row of its division's, at a given time, along part of a route
            row['starts_from_row'] = st[0]['id']; row['starts_at'] = t(st[0]['show'][0]); via = st[1].get('via')
            if via:
                head = via[:-1]; hit = [(rid_, len(head)) for rid_, w in ROUTES.items() if w[:len(head)] == head]
                assert hit, (tr['id'], head[:2]); row['start_route'], row['start_route_points'] = hit[0]
        TR.append(row)
sheet('Tracks', ['playback_id', 'track_id', 'unit_id', 'rows', 'label', 'echelon', 'part_of_track', 'hide_after_last_row', 'hold_until', 'loose', 'off_map', 'nudge', 'starts_from_row', 'starts_at', 'start_route', 'start_route_points'], TR, {'rows': 40, 'off_map': 40})
# ---- Nations, Labels, Maps ----
NA = [dict(n, playback_id=b) for b, B in BT.items() for n in B.get('nations', [])]
sheet('Nations', ['playback_id', 'name', 'short', 'code', 'colour', 'dark', 'paper'], NA)
LB = [{'playback_id': b, 'text': l['text'], 'other_name': l.get('alt'), 'lat': l['at'][1], 'lon': l['at'][0], 'angle': l.get('angle'), 'level': l.get('level'), 'kind': l['kind'],
       'show': l.get('show'), 'approximate': 'yes' if l.get('approximate') else None} for b, B in BT.items() for l in B['labels']]
sheet('Labels', ['playback_id', 'text', 'other_name', 'lat', 'lon', 'angle', 'level', 'kind', 'show', 'approximate'], LB, {'text': 28, 'other_name': 22})
MP = []
for b, B in BT.items():
    for m in B['maps']:
        for im in m['images']:
            c = im.get('corners') or [[None, None]] * 4
            MP.append({'playback_id': b, 'map_id': m['id'], 'title': m['title'], 'short': m.get('short'), 'label': m.get('label'), 'credit': m['credit'], 'source_id': m.get('source'),
                       'fitted_to_ground': 'no' if m.get('georeferenced') is False else 'yes', 'size_px': ('%d, %d' % tuple(m['size'])) if m.get('size') else None,
                       'from': m.get('from'), 'to': m.get('to'), 'file': im['file'], 'detail': 'yes' if im.get('detail') else None,
                       'tl_lat': c[0][1], 'tl_lon': c[0][0], 'tr_lat': c[1][1], 'tr_lon': c[1][0], 'br_lat': c[2][1], 'br_lon': c[2][0], 'bl_lat': c[3][1], 'bl_lon': c[3][0],
                       'fit': json.dumps(m['fit']) if m.get('fit') else None, 'scale_note': m.get('scale_note'),
                       'off_note_until': t((m.get('off_note') or {}).get('until')), 'off_note_text': (m.get('off_note') or {}).get('text')})
sheet('Maps', list(MP[0].keys()), MP, {'title': 40, 'credit': 30, 'fit': 40, 'off_note_text': 40})
# ---- Read me ----
ws = wb['Read me']; r = ws.max_row + 2
for line in ['This workbook is the master copy of the battle data (since 15 Nov 2026). The playbacks are written from it by tools/export_battles.py; nothing else feeds them.',
             'New sheets: Playbacks (one row per playback), Playback settings (one setting per row), Tracks (one row per symbol on the map: which Positions rows it follows), Nations, Labels (names on the map), Maps (period maps and where they sit).',
             'New columns, shaded green: Positions (show_from, show_to: when the playback draws the row; map_id, map_xy: its place on a map that is not to scale), Events (timeline, playback_at, playback_label, playback_text), Routes (playback), Sides (code, short).',
             'The Checks sheet was written when the workbook was last generated (v7). It is not updated by hand edits; the export script runs its own checks and refuses to write a battle file that fails them.']:
    ws.cell(r, 1, line); r += 1
wb.move_sheet('Playbacks', -(len(wb.sheetnames) - 2)); wb.save(OUT)
print('wrote', OUT, len(SET), 'settings', len(TR), 'tracks', len(LB), 'labels', len(MP), 'map pictures')
