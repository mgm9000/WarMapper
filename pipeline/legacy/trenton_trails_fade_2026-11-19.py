"""19 Nov 2026 (Morgan): on the Trenton map, remove the route lines once units stop moving.
Once a unit has stood still for 10 minutes, the roads it took to get there fade out over the next 10 minutes."""
import openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); PS = wb['Playback settings']
have = {(r[0].value, r[1].value): r for r in PS.iter_rows(min_row=2)}
rows = [('trenton', 'trails.fade_after', 10, 'Once a unit has stood still this many minutes, the routes it took to get there fade out (Morgan, 19 Nov 2026).'),
        ('trenton', 'trails.fade_over', 10, 'How many minutes the routes take to fade out.')]
anchor = have[('trenton', 'trails.opacity')][0].row
for i, row in enumerate(rows):
    if (row[0], row[1]) in have:
        for c, v in zip(have[(row[0], row[1])], row): c.value = v
    else:
        PS.insert_rows(anchor + 1 + i)
        for c, v in enumerate(row, 1): PS.cell(anchor + 1 + i, c, v)
wb.save(WB); print('trails fade set')
