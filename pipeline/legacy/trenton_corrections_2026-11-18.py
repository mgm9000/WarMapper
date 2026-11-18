"""18 Nov 2026 (Morgan's Trenton corrections): start at 18:00; the army crosses as one, splits into Greene and Sullivan,
which (with Knox's artillery) stay whole until the first shots; 'Crossing the Delaware' named on the timeline."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); head = lambda ws: [c.value for c in ws[1]]
D25, D26 = '1776-12-25 ', '1776-12-26 '


def add(ws, d, like):
    h = head(ws); r = ws.max_row + 1
    for j, n in enumerate(h, 1):
        if ws.cell(like, j).has_style: ws.cell(r, j)._style = copy.copy(ws.cell(like, j)._style)
        if d.get(n) is not None: ws.cell(r, j).value = d[n]


PB = wb['Playbacks']; h = head(PB)
for r in PB.iter_rows(min_row=2):
    if r[0].value == 'trenton':
        r[h.index('time_start')].value = D25 + '18:00'
        r[h.index('opening_text')].value = ("Christmas evening: Washington's army stands behind McKonkey's Ferry on the Pennsylvania bank and begins to cross the ice-choked Delaware. "
                                            "The crossing runs through the night, about three hours late; on the New Jersey bank the army forms in two divisions, Greene's and Sullivan's.")
P = wb['Positions']; ph = head(P); pc = lambda n: ph.index(n)
for r in P.iter_rows(min_row=2):
    if r[1].value != 'ARW-TP': continue
    if r[0].value == 'T00':
        r[pc('show_from')].value = D25 + '18:00'; r[pc('show_to')].value = D25 + '18:00'; r[pc('activity')].value = 'Begins to cross'
        r[pc('notes')].value = "The whole army is drawn as one symbol, crossing through the night; it divides into Greene's and Sullivan's divisions on the New Jersey bank."
    if r[0].value == 'T01':
        r[pc('show_from')].value = D26 + '03:00'; r[pc('show_to')].value = D26 + '03:30'; r[pc('activity')].value = 'Across the Delaware'
T = wb['Tracks']; th = head(T); tc = lambda n: th.index(n)
for r in T.iter_rows(min_row=2):
    if r[0].value != 'trenton': continue
    t = r[1].value; rows = str(r[tc('rows')].value or '')
    if t == 'T-US-ARMY': r[tc('rows')].value = 'T00; T01'
    elif rows.startswith('T01; T02'):
        r[tc('rows')].value = rows[len('T01; '):]
        for n in ('starts_from_row', 'starts_at', 'start_move_minutes'): r[tc(n)].value = None
like = [r[0].row for r in T.iter_rows(min_row=2) if r[0].value == 'trenton'][-1]
if 'T-US-KNOX' not in {r[1].value for r in T.iter_rows(min_row=2)}:
    add(T, {'playback_id': 'trenton', 'track_id': 'T-US-KNOX', 'unit_id': 'T-US-KNOX', 'rows': 'T02; T03; T04; T05', 'hide_after_last_row': 'yes', 'nudge': '-26, 14'}, like)
U = wb['Units']
if 'T-US-KNOX' not in {r[0].value for r in U.iter_rows(min_row=2)}:
    k = [r[0].row for r in U.iter_rows(min_row=2) if r[0].value == 'T-US-FORR'][0]
    add(U, {'unit_id': 'T-US-KNOX', 'unit_name': "Knox's artillery (Col. Henry Knox)", 'map_label': 'Knox', 'side_id': 'ARW-US', 'nation': 'United States', 'branch': 'Artillery',
            'echelon': 'Brigade', 'symbol_code': '10031000181303000000', 'source_ids': 'S59; S21', 'sourced?': 'yes',
            'notes': "Knox commanded the army's artillery and rode with Washington in Greene's column; the batteries of that column (Forrest, Hamilton, Bauman) are drawn under him. Sullivan's batteries stay with Sullivan."}, k)
A = wb['Assignments']; ah = head(A)
if 'T-US-KNOX' not in {r[1].value for r in A.iter_rows(min_row=2)}:
    nid = max(int(str(r[0].value)[1:]) for r in A.iter_rows(min_row=2) if str(r[0].value)[1:].isdigit())
    k = [r[0].row for r in A.iter_rows(min_row=2) if r[1].value == 'T-US-FORR'][0]
    add(A, {'assign_id': 'A%03d' % (nid + 1), 'unit_id': 'T-US-KNOX', 'parent_unit_id': 'T-US-ARMY', 'commander': 'Col. Henry Knox', 'strength / equipment': '418 gunners, 18 guns (S59)',
            'valid_from': '1776-12-25', 'valid_to': '1776-12-26', 'source_ids': 'S59'}, k)
    for r in A.iter_rows(min_row=2):
        if r[1].value in ('T-US-FORR', 'T-US-HAM', 'T-US-BAUM'):
            r[ah.index('parent_unit_id')].value = 'T-US-KNOX'
            n = ah.index('notes') if 'notes' in ah else None
            if n is not None: r[n].value = ((r[n].value + ' ') if r[n].value else '') + "Marched in Greene's column; drawn under Knox, who directed the guns there (18 Nov 2026; was under Greene)."
PS = wb['Playback settings']
last = max(x[0].row for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'); have = {x[1].value for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'}
for k, v, d in [('formations.until', '1776-12-26T07:45', 'Before this time the formations are drawn whatever the zoom (Trenton: Greene, Sullivan and Knox stay whole until the first shots).'),
                ('formations.also', 'T-US-KNOX', 'Units that count as formations though not of the echelon (Trenton: Knox\'s artillery).')]:
    if k in have: continue
    PS.insert_rows(last + 1, 1); last += 1
    for j in range(1, 5):
        if PS.cell(last - 1, j).has_style: PS.cell(last, j)._style = copy.copy(PS.cell(last - 1, j)._style)
    for j, x in enumerate(['trenton', k, v, d], 1): PS.cell(last, j).value = x
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'trenton' and r[1].value == 'about.7':
        r[2].value = ("The army crosses the Delaware as one symbol and divides on the New Jersey bank into Greene's and Sullivan's divisions; Greene, Sullivan and Knox's artillery are drawn whole "
                      "until the first shots, then as their brigades and batteries. Formations, in the Layers menu, draws them whole again when zoomed out. Routes taken, also in Layers, draws the roads "
                      "each unit has marched. The escapes (the dragoons to Princeton, the jägers to Bordentown, about fifty of the Knyphausen regiment to Crosswicks) follow roads the sources do not give.")
E = wb['Events']; eh = head(E)
for r in E.iter_rows(min_row=2):
    if r[1].value != 'ARW-TP': continue
    if r[0].value == 'TE01':
        r[eh.index('name')].value = 'Crossing the Delaware'; r[eh.index('timeline')].value = 'name'; r[eh.index('playback_at')].value = D25 + '18:15'
        r[eh.index('summary')].value = "At dusk the army begins to cross the Delaware at McKonkey's Ferry in Durham boats and ferries, in sleet and floating ice; the crossing runs about three hours late."
    if r[0].value == 'TE03': r[eh.index('timeline')].value = 'dot'; r[eh.index('playback_at')].value = D26 + '03:00'
R = wb['Read me']
c = R.cell(5, 1)
if c.value and 'Crossing: Trenton now opens' in c.value:
    c.value = ("Crossing (revised the same day at Morgan's request): Trenton opens at 18:00 on 25 December. The army crosses as one symbol (T00 to T01) and divides on the New Jersey bank "
               "into Greene's and Sullivan's divisions; they and Knox's artillery (new unit T-US-KNOX, with Forrest, Hamilton and Bauman under him) are drawn whole until the first shots "
               "(playback settings formations.until and formations.also). 'Crossing the Delaware' (TE01) is now named on the timeline. All times on the maps and timeline are 24-hour.")
wb.save(WB); print('corrections done')

# follow camera: a wider closest view, so the crossing shows both banks
wb = openpyxl.load_workbook(WB)
for r in wb['Playback settings'].iter_rows(min_row=2):
    if r[0].value == 'trenton' and r[1].value == 'follow.min': r[2].value = '[1600, 1100]'
wb.save(WB)
