"""18 Nov 2026: the smaller Trenton edits made by hand during testing, replayed onto Morgan's workbook (with the source register)."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB)
PB = wb['Playbacks']; h = [c.value for c in PB[1]]
for r in PB.iter_rows(min_row=2):
    if r[0].value == 'trenton': r[h.index('time_zero')].value = '1776-12-25 00:00'
PS = wb['Playback settings']
have = {(r[0].value, r[1].value) for r in PS.iter_rows(min_row=2)}
if ('trenton', 'follow.side_from.CR') not in have:
    last = max(x[0].row for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'); PS.insert_rows(last + 1, 1)
    for j in range(1, 5):
        if PS.cell(last, j).has_style: PS.cell(last + 1, j)._style = copy.copy(PS.cell(last, j)._style)
    for j, v in enumerate(['trenton', 'follow.side_from.CR', '1776-12-26T07:00', 'Follow leaves this side (by its code) out of the frame until this time, so the camera stays on the crossing and the march while the garrison sleeps.'], 1): PS.cell(last + 1, j).value = v
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'trenton' and r[1].value == 'about.7':
        r[2].value = ("The army is drawn as one symbol on the Pennsylvania bank until each brigade crosses; the order of crossing beyond Stephen's brigade first, Greene's division before Sullivan's "
                      "and the guns last is not recorded, so the brigades are spaced evenly through the night. Before Birmingham the brigades march with their divisions; Formations, in the Layers menu, "
                      "draws them as their division when zoomed out. Routes taken, also in Layers, draws the roads each unit has marched. The escapes (the dragoons to Princeton, the jägers to Bordentown, "
                      "about fifty of the Knyphausen regiment to Crosswicks) follow roads the sources do not give.")
# the register's evidence columns, for the new rows
P = wb['Positions']; ph = [c.value for c in P[1]]
PAGES = {'T00': ('S21; S20; S59 p. 43', None), 'T62': ('S59 p. 45; S61', 'S61'), 'T63': ('S20; S21', None), 'T64': ('S59 p. 48; S61', 'S61'), 'T65': ('S61', None)}
for r in P.iter_rows(min_row=2):
    if r[1].value == 'ARW-TP' and r[0].value in PAGES:
        r[ph.index('source_pages')].value, r[ph.index('cross_checked_by')].value = PAGES[r[0].value]
R = wb['Read me']
merged = [str(x) for x in R.merged_cells.ranges]; heights = {k: v.height for k, v in R.row_dimensions.items() if v.height}
for x in merged: R.unmerge_cells(x)
R.insert_rows(4, 5)
for x in merged:
    a, b = x.split(':'); ra, rb = int(a[1:]), int(b[1:]); sh = 5 if ra >= 4 else 0
    R.merge_cells('%s%d:%s%d' % (a[0], ra + sh, b[0], rb + sh))
for k in sorted(heights, reverse=True):
    if k >= 4: R.row_dimensions[k + 5].height = heights[k]
for k in range(4, 9): R.merge_cells('A%d:D%d' % (k, k)); R.row_dimensions[k].height = None
for k in (5, 6, 7): R.row_dimensions[k].height = 58
T = ['What changed on 18 November 2026 (later): Trenton crossing, escapes, routes taken and the 1777 map',
     "Crossing: Trenton now opens at 4 p.m. on 25 December with the army as one symbol behind McKonkey's Ferry (new row T00). Each brigade crosses in turn and waits on the New Jersey bank (Tracks: starts_from_row T00, starts_at and the new start_move_minutes). The order beyond Stephen first, Greene before Sullivan and the guns last is not recorded.",
     "Escapes: the British dragoons now ride to Princeton (T62, route RT12), the jägers go to Bordentown (T63, RT13; see TC18), and a new unit, the men of the Knyphausen regiment who forded the Assunpink (T-HE-KNYPX, T64 and T65, RT14), makes for Crosswicks. The playback runs to 11:30. New event TE16. The new rows have source_pages and cross_checked_by filled in.",
     "Maps: Faden's 1777 map was rebuilt from the full scan at 7 m a pixel (it was 12) in four pieces; a new map row, faden-1777-sheet, is the engraving as printed, reached by the 1:1 button, with units placed on it by the same fit (Maps column xy_from). Routes taken (playback setting trails) draws the roads each unit has marched."]
for i, txt in enumerate(T):
    c = R.cell(4 + i, 1); src = R.cell(9 if i == 0 else 10, 1)
    if src.has_style: c._style = copy.copy(src._style)
    c.value = txt
wb.save(WB); print('rest done')
