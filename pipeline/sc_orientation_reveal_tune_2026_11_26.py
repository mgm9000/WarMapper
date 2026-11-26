"""26 Nov 2026, late morning: Morgan's second set of corrections to the South Carolina orientation's year reveal.
  - "At the end of 1776, move steadily over 2 secs to 1779": years with no clash (1777, 1778) get no reveal of their own; the clock crosses
    them together and steadily in 2 seconds (orientation.reveal.empty_seconds).
  - "Eliminate the 'continue' button": no recap stop at the end of 1779 (orientation.reveal.stop false); the map goes straight on month by month.
Safe to run again. Run: python3 pipeline/sc_orientation_reveal_tune_2026_11_26.py, then tools/export_battles.py and tools/build.py.
"""
import json, os
import openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
wb = openpyxl.load_workbook(WAR); PS = wb['Playback settings']; h = [c.value for c in PS[1]]
for r in range(2, PS.max_row + 1):
    if PS.cell(r, 1).value == 'sc-orientation' and PS.cell(r, 2).value == 'orientation.reveal':
        v = json.loads(PS.cell(r, 3).value); v['empty_seconds'] = 2; v['stop'] = False; v.pop('title', None)
        PS.cell(r, 3, json.dumps(v))
        PS.cell(r, h.index('what it does') + 1, "1775 to 1779 play a year at a time: all of a year's clashes come on together, grow into a large "
                "symbol, stop for 3 seconds with a dated bubble on each, then shrink to their standard size. Years with no clash (1777, 1778) are "
                "crossed steadily in 2 seconds. No stop at the end of 1779: from 1780 the map runs month by month.")
        PS.cell(r, h.index('why') + 1, "Morgan, 26 Nov 2026: 'Show all events for the year at once', the same for 1776 to 1779; later the same "
                "morning: 'At the end of 1776, move steadily over 2 secs to 1779' and 'Eliminate the continue button'. Replaces orientation.phases.")
PL = wb['Playbacks']; ph = [c.value for c in PL[1]]
for r in range(2, PL.max_row + 1):
    if PL.cell(r, 1).value == 'sc-orientation':
        PL.cell(r, ph.index('opening_text') + 1, "South Carolina, early 1775: the royal government still stands. Press play: each year to 1779 "
                "comes onto the map at once, with a note on each event, and from 1780 the fights come on month by month, each drawn for the side that won it.")
wb.save(WAR); print('done')
