"""21 Nov 2026: the Manila current-map drawing now exists (data/osm/manila.txt, data/base/manila.json), so gap G-PW3 is closed.
Run once."""
import os, openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx'); wb = openpyxl.load_workbook(WB); ws = wb['Gaps']; h = [c.value for c in ws[1]]
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 1).value == 'G-PW3':
        assert 'Closed' not in str(ws.cell(r, h.index('status in v2') + 1).value), 'already applied'
        ws.cell(r, h.index('status in v2') + 1).value = 'Closed 21 Nov 2026: cut from an Overpass export Morgan downloaded (pipeline/osm_manila.py, pipeline/basemaps.py). Main roads, railways, rivers, esteros and larger water bodies; the shore of Manila Bay is not in it.'
        break
else: raise SystemExit('G-PW3 not found')
wb.save(WB); print('G-PW3 closed')
