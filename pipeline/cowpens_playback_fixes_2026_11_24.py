"""Cowpens: how the playback looks and moves, after Morgan's review of 24 Nov 2026.

  1. It opened close in on the field. It now opens on the whole ground ("Tarleton's approach" first among the views) and the Follow
     camera eases in over 10 seconds once play is pressed.
  2. Symbols were often faint: every unit not named in the current key event was drawn at a third of its strength (BP-32), and
     switched between the two. Here they keep 70% (playback.event_dim), and the player now eases the change.
  3. Moves jumped. Tarleton's eight units marched the 3 km of road on top of one another (each from CP40 along RC01), so the
     layout pushed them about. The column is now one symbol, Tarleton's detachment, which marches RC01 to a new row, CP138, at the
     edge of the field at 06:53 (setting off at 06:22 with its advance guard, about 6 km/h); its units set off from there to their first rows (06:55 to 06:58) and are drawn coming out of it.
     Steps that meet blend over 4 minutes (the player's default) instead of 2. Two jumps were the player's own and are fixed there.
  4. Arrows ran the whole road ahead of a unit, so their heads stood at the field long before the unit came into view (Ogilvie at
     06:22 to 06:45). An arrow now reaches 6 minutes' march ahead (playback.arrows.reach_minutes).

It stops if CP138 is already a row.
"""
import os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cowpens_geo as G
from cowpens_audit_2026_11_24 import header, last_row, add, rows_by_id, setv, add_note

WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
SHARED = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
PB = 'cowpens'; DAY = '1781-01-17 '
UNITS = ['C-BR-HQ', 'C-BR-LI', 'C-BR-LEGI', 'C-BR-7', 'C-BR-RA1', 'C-BR-RA2', 'C-BR-71', 'C-BR-LEGC', 'C-BR-17']   # Ogilvie rides ahead, as before
LAT, LON = G.at(-200, 0)                                                         # where RC01 ends: 200 m short of the head of the column's place on the field


def main():
    wb = openpyxl.load_workbook(WAR)
    ps = wb['Positions']; pids = rows_by_id(ps); h = header(ps)
    assert 'CP138' not in pids, 'CP138 is already a row: this script has run'
    src = {c: ps.cell(pids['CP40'], i + 1).value for i, c in enumerate(h)}
    r = last_row(ps) + 1
    row = dict(src)
    row.update({'pos_id': 'CP138', 'unit_name': '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r, 'side': '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r,
                'start_earliest': DAY + '06:45', 'start_latest': DAY + '07:45', 'end_earliest': DAY + '06:50', 'end_latest': DAY + '07:50',
                'time_basis': 'Worked out: the column, marching the road from CP40, reaches here as its units must set off to be on their first rows at 06:55 to 06:58 (CP51 to CP131). '
                              'An hour later at the latest, with the Army War College\'s clock (S103, p. 66; CH01).',
                'activity': 'Column comes up to the field and deploys', 'place_description': 'On the road, about 200 m short of where the head of the column came out onto the field',
                'lat': LAT, 'lon': LON, 'coord_source': 'derived', 'coord_precision_m': 150,
                'coordinate_basis': 'Placed by distance along the Historic Green River Road as OpenStreetMap draws it (S39), counted from the south-east end of the Battlefield Trail loop (35.13294, -81.81012), '
                                    'where the staff ride\'s Vantage 6 (S95, p. 77) and the NPS wayside "The British Army" (S105) put the head of Tarleton\'s column as it came onto the field. 200 m short of that point: '
                                    'the end of route RC01. A place for the column as one body before it forms; no source puts it here.',
                'coordinate_confidence': 'low', 'source_ids': 'S95; S105', 'source_wording': 'None: no source places the column at this spot. The head of the column\'s place on the field is from S95 (p. 77, Vantage 6) and S105.',
                'position_method': 'inferred', 'overall_confidence': 'low',
                'notes': '24 Nov 2026 (Morgan\'s review of the playback): added so the column is drawn as one symbol on the road, its units coming out of it at the field, instead of eight symbols marching on top of one another. '
                         'Replaces nothing the sources say: the units\' own rows are unchanged.',
                'review_status': 'Needs review', 'show_from': DAY + '06:53', 'show_to': DAY + '06:54',
                'map_link': '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=17/"&O%d&"/"&P%d,"Open map"))' % (r, r, r, r, r),
                'source_pages': 'S95 p. 77', 'cross_checked_by': 'S105'})
    for k in [k for k in row if k.startswith(('changed in', 'your_review', 'check:'))]: row[k] = None
    add(ps, row)
    rt = wb['Routes']; rids = rows_by_id(rt)
    setv(rt, rids['RC01'], 'to_pos_id', 'CP138'); setv(rt, rids['RC01'], 'end', DAY + '06:53'); setv(rt, rids['RC01'], 'start', DAY + '06:22')
    # the column sets off with its advance guard (Ogilvie, 06:22): 3.1 km in 31 minutes, about 6 km/h, not 25 minutes at 8 km/h
    setv(ps, pids['CP40'], 'show_from', DAY + '06:16'); setv(ps, pids['CP40'], 'show_to', DAY + '06:22')
    setv(ps, pids['CP40'], 'notes', add_note('24 Nov 2026: shown 06:16 to 06:22 (was 06:20 to 06:28), so the column sets off with its advance guard and marches the 3.1 km to the field at about 6 km/h.'))
    setv(rt, rids['RC01'], 'notes', add_note('24 Nov 2026: the route of the column as one symbol (C-BR-TARL), from CP40 to CP138 at the edge of the field (06:28 to 06:53); its units set off from CP138, not from CP40.'))
    tk = wb['Tracks']; th = header(tk)
    for i in range(2, last_row(tk) + 1):
        if tk.cell(i, 1).value != PB: continue
        tid = tk.cell(i, 2).value
        def put(col, v): tk.cell(i, th.index(col) + 1).value = v
        if tid == 'C-BR-TARL': put('rows', 'CP40; CP138')
        if tid in UNITS: put('starts_from_row', 'CP138'); put('starts_at', DAY + '06:53'); put('start_route', None)
    st = wb['Playback settings']; sh_ = header(st)
    have = {st.cell(i, 2).value: i for i in range(2, last_row(st) + 1) if st.cell(i, 1).value == PB}
    def setting(k, v, what=None):
        if k in have: st.cell(have[k], 3).value = v; (what and st.cell(have[k], 4, what))
        else:
            n = last_row(st) + 1; st.cell(n, 1, PB); st.cell(n, 2, k); st.cell(n, 3, v)
            if what: st.cell(n, 4, what)
            have[k] = n
    for a, b in (('preset', 'approach'), ('label', 'Tarleton\'s approach'), ('short', 'Approach')): setting('views.1.' + a, b)
    for a, b in (('preset', 'field'), ('label', 'The battlefield'), ('short', 'Field')): setting('views.2.' + a, b)
    st.cell(have['views.1.preset'], 4, 'Named views; the first is the one the page opens on (since 24 Nov: the whole ground, then Follow eases in)')
    setting('follow.glide_seconds', 10, 'Once play is pressed, the camera eases in from the whole ground to the action over this many seconds')
    setting('event_dim', 0.7, 'Units not named in the current key event are drawn at this strength (the player\'s default is 0.32; at Cowpens it made most symbols faint)')
    setting('arrows.reach_minutes', 6, 'An arrow runs this many minutes of march ahead of its unit, not to the end of the road')
    setting('rules.blend', 4, 'Minutes over which a unit shifts from one row to the next when they meet (was 2: the moves looked like jumps)')
    wb['Read me'].append(['Cowpens playback review (24 Nov 2026)', 'Opens on the whole ground; symbols less faint; Tarleton\'s column one symbol to the field (new row CP138), its units coming out of it; arrows reach 6 minutes ahead; blend 4 minutes. See pipeline/cowpens_playback_fixes_2026_11_24.py.'])
    sh = openpyxl.load_workbook(SHARED); rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026 (evening): the Cowpens playback after Morgan\'s review')
    rm.cell(2, 1, 'Revolutionary War.xlsx, Cowpens: the page opens on the whole ground and eases in; units outside the current event keep 70% of their strength; Tarleton\'s column marches as one symbol (C-BR-TARL, rows CP40 and a new row CP138) '
                  'and its eight units set off from CP138 instead of marching the road on top of one another; arrows reach 6 minutes ahead; rows that meet blend over 4 minutes. No source reading changed. '
                  'With player fixes for two jumps (a move along a route that began away from the unit, and the end of a route into a line) and eased event dimming. Written by pipeline/cowpens_playback_fixes_2026_11_24.py.')
    wb.save(WAR); sh.save(SHARED); print('written: CP138 at', LAT, LON)


if __name__ == '__main__':
    main()
