"""27 Nov 2026, Session 1 of claude/sc-storyline-prompt.md: the orientation preset's new rows, from Morgan's answers of the same day.

Every orientation (Morgan: "Every orientation" for each of these):
  - event_dim 1: every force on the move is drawn at full strength, in the current event or not ("All at full strength").
  - orientation.move_day_seconds 0.3: while a force is on the move the clock runs a day at a time, 0.3 s a day, and goes back to
    months when no force moves; orientation.move_tail_days 5: it keeps to days for 5 days after a move ends, so the route can fade.
  - trails.fade_after 2, trails.fade_over 5 (days): a route stays 2 days after its force stops, then fades over 5 ("Symbol leaves,
    route fades").
  - orientation.legs.day_seconds 0.5: a campaign played in legs runs at 0.5 s a day (Morgan approved the design with this value).
  - orientation.flags: at its closing stop every orientation fades its clashes to 40% and flies a flag over each place a side holds,
    10% larger than the first flags (South Carolina's values of 26 Nov; Morgan, 27 Nov: "Every orientation, at its end"). A playback
    names its sides' flags (flags.sides); South Carolina keeps its own stop at the end of 1780 (flags.from).
Safe to run again. Run: python3 pipeline/storyline_presets_2026_11_27.py, then tools/export_battles.py and tools/build.py.
"""
import os
import openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
WHY = "Morgan, 27 Nov 2026 (Session 1 of claude/sc-storyline-prompt.md), for every orientation"
ROWS = [
    ('event_dim', 1, 'Symbols outside the current event keep full strength: every force on the move is drawn as strongly as the rest',
     WHY + ': "All at full strength" (in place of the battles\' 70%, SR-11).'),
    ('orientation.move_day_seconds', 0.3, 'While a force is on the move the clock runs a day at a time, this many seconds a day; months again when none moves',
     WHY + ': "Day by day, 0.3 s a day".'),
    ('orientation.move_tail_days', 5, 'Days the clock keeps to a day at a time after a move ends, so its route can fade before the months run on',
     WHY + ': "Symbol leaves, route fades".'),
    ('trails.fade_after', 2, 'Days a route stays on the map after its force stops, before it fades', WHY + ': "Symbol leaves, route fades".'),
    ('trails.fade_over', 5, 'Days over which a route fades out', WHY + ': "Symbol leaves, route fades".'),
    ('orientation.legs.day_seconds', 0.5, 'A campaign played in legs (Summaries kind leg): seconds of play for a day', WHY + ': the design approved with 0.5 s a day.'),
    ('orientation.flags.dim', 0.4, 'At the closing stop the clashes fade to this strength', WHY + ': "Every orientation, at its end" (South Carolina\'s 40%, 26 Nov).'),
    ('orientation.flags.scale', 1.1, 'Size of the flags over held places', WHY + ' (South Carolina\'s flags 10% larger, 26 Nov).'),
    ('orientation.flags.fade_seconds', 2, 'Seconds over which the clashes fade and the flags come up', WHY + '.'),
    ('orientation.flags.hold_seconds', 3, 'Seconds the flags stop holds', WHY + '.'),
]
wb = openpyxl.load_workbook(BOOK); ws = wb['Playback presets']; head = [c.value for c in ws[1]]
col = {h: i + 1 for i, h in enumerate(head)}
have = {(ws.cell(r, col['preset']).value, ws.cell(r, col['setting']).value): r for r in range(2, ws.max_row + 1)}
last = max(r for (p, _), r in have.items() if p == 'orientation')
for setting, value, what, why in ROWS:
    r = have.get(('orientation', setting))
    if r is None:
        ws.insert_rows(last + 1); r = last + 1; last = r
        have = {k: (v + 1 if v >= r else v) for k, v in have.items()}; have[('orientation', setting)] = r
    for k, v in (('preset', 'orientation'), ('setting', setting), ('value', value), ('what it does', what), ('why', why)): ws.cell(r, col[k], v)
wb.save(BOOK); print('done: %d rows' % len(ROWS))
