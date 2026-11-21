"""21 Nov 2026: Manila Bay added to the Manila current-map drawing (coastline export from Morgan); the note on gap G-PW3 is brought up to date.
Run once."""
import os, openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx'); wb = openpyxl.load_workbook(WB); ws = wb['Gaps']; h = [c.value for c in ws[1]]
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 1).value == 'G-PW3':
        c = ws.cell(r, h.index('status in v2') + 1); assert 'is not in it' in str(c.value), 'already applied'
        c.value = ('Closed 21 Nov 2026: cut from two Overpass exports Morgan downloaded (pipeline/osm_manila.py, pipeline/basemaps.py). Main roads, railways, rivers, '
                   'esteros, larger water bodies and Manila Bay. The shore is today\'s (port and reclaimed land), not that of 1899.')
        break
else: raise SystemExit('G-PW3 not found')
wb.save(WB); print('G-PW3 note updated')
