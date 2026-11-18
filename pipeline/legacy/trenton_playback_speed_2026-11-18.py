"""18 Nov 2026 (Morgan): Trenton plays at one speed throughout, and the night of the crossing is skipped after two seconds."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); PS = wb['Playback settings']
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'trenton' and r[1].value == 'lead.rate':
        r[2].value = 5; r[3].value = 'Time units per second in that stretch (5, the same as the battle, since 18 Nov 2026: the march no longer runs faster than the fight)'
last = max(x[0].row for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'); have = {x[1].value for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'}
D = 'While playing, after after_seconds in this stretch the clock jumps to its end (moving the clock by hand is not affected); note is shown as it jumps.'
for k, v in [('skip.1.from', '1776-12-25T18:00'), ('skip.1.to', '1776-12-26T03:00'), ('skip.1.after_seconds', 2),
             ('skip.1.note', 'The crossing takes all night: on to 03:00, with the army over the river.')]:
    if k in have: continue
    PS.insert_rows(last + 1, 1); last += 1
    for j in range(1, 5):
        if PS.cell(last - 1, j).has_style: PS.cell(last, j)._style = copy.copy(PS.cell(last - 1, j)._style)
    for j, x in enumerate(['trenton', k, v, D if k == 'skip.1.from' else None], 1): PS.cell(last, j).value = x
R = wb['Routes']; rh = [c.value for c in R[1]]
kinds = {r[0].value: r[rh.index('kind')].value for r in R.iter_rows(min_row=2) if r[1].value == 'ARW-TP'}
assert all(kinds[k] == 'escape' for k in ('RT12', 'RT13', 'RT14')), kinds
wb.save(WB); print('playback settings done')
