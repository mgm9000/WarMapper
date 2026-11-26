"""26 Nov 2026, Morgan's corrections to the South Carolina orientation after his first look at the live map.

The South Carolina data changes here; the drawing changes are in app/player.js and app/core.css.
  - 1775 to 1779 play a year at a time (playback.orientation.reveal, new): all of a year's clashes come on together, grow into a large
    symbol, stop for three seconds with a dated bubble beside each, then shrink to their standard size. This replaces the event-by-event
    stretch to the end of 1777 (orientation.phases), and the recap stop moves to the end of 1779. From 1780 the map runs month by month.
  - The subtitle and the opening text say so.
Safe to run again. Run: python3 pipeline/sc_orientation_year_reveal_2026_11_26.py, then python3 tools/export_battles.py and tools/build.py.
"""
import json, os
import openpyxl
from openpyxl.styles import Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
PB = 'sc-orientation'

wb = openpyxl.load_workbook(WAR)

PS = wb['Playback settings']; ph = [c.value for c in PS[1]]
def row_of(name):
    for r in range(2, PS.max_row + 1):
        if PS.cell(r, 1).value == PB and PS.cell(r, 2).value == name: return r
    return None
r = row_of('orientation.phases')
if r: PS.delete_rows(r)
reveal = {"until": "1779-12-31", "grow_seconds": 1.6, "fade_seconds": 0.5, "hold_seconds": 3, "shrink_seconds": 1.6, "scale": 2.3,
          "title": "Where things stood at the end of 1779"}
r = row_of('orientation.reveal') or PS.max_row + 1
vals = {'playback_id': PB, 'setting': 'orientation.reveal', 'value': json.dumps(reveal),
        'what it does': "1775 to 1779 play a year at a time: all of a year's clashes come on together, grow into a large symbol, stop for "
                        "3 seconds with a dated bubble on each, then shrink to their standard size; the map stops at the end of 1779 with a "
                        "recap, then runs month by month.",
        'why': "Morgan, 26 Nov 2026, after his first look at the live map: 'Show all events for the year at once', the same for 1776 to "
               "1779. Replaces the event-by-event stretch to the end of 1777 (orientation.phases)."}
for k, v in vals.items():
    c = PS.cell(r, ph.index(k) + 1, v); c.alignment = Alignment(wrap_text=True, vertical='top')

PL = wb['Playbacks']; h = [c.value for c in PL[1]]
for r in range(2, PL.max_row + 1):
    if PL.cell(r, 1).value == PB:
        PL.cell(r, h.index('subtitle') + 1, "Who fought where, who won, and who held the towns and forts: year by year to 1779, then month by month")
        PL.cell(r, h.index('opening_text') + 1, "South Carolina, early 1775: the royal government still stands. Press play: each year to 1779 "
                "comes onto the map at once, with a note on each event, and from 1780 the fights come on month by month, each drawn for the side that won it.")
wb.save(WAR)
print('done')
