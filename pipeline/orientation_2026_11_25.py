"""Orientation playbacks: the sheets and the preset (25 Nov 2026, Session 1 of claude/sc-orientation-prompt.md).

An orientation is a playback with no unit detail: dated clashes drawn as crossed-swords symbols in the colour and shape of the side that
won, played month by month, and the places each side held (docs/battle-file.md: clashes, places, summaries of kind year and end).
This script, run once:

- adds three sheets, with their headings and no rows, to every war workbook (each war workbook keeps the same sheets in the same order):
  Clashes (one row per clash or capture, tied to its event), Control places (one row per town, village, fort or port) and Control (one
  row each time a place changes hands);
- adds the preset `orientation` to the Playback presets sheet of Sources and notes.xlsx, so a later orientation (another state, another
  war) is data only;
- notes both in each workbook's Read me.

No battle file changes: none of the six playbacks has rows on the new sheets or uses the new preset.

  python3 pipeline/orientation_2026_11_25.py
"""
import os, sys
import openpyxl
from openpyxl.styles import Alignment, Font

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
WARS = ['Philippine War', 'Revolutionary War', 'U.S. Civil War', 'World War I']

SHEETS = {
    'Clashes': [
        ('clash_id', 'The clash\'s own id (C01, C02 ...); unique across the workbooks'),
        ('playback_id', 'The orientation playback it is drawn in'),
        ('event_id', 'The event (Events sheet) it belongs to: its dates, name and words come from there'),
        ('kind', 'fight (a clash of arms) or capture (a post or stores taken with no fight recorded: drawn as a flag)'),
        ('won_by', 'The code of the side that won (Sides sheet), or indecisive. For a capture, the side that took it'),
        ('result_method', 'stated (a cited source says who won) or inferred'),
        ('result', 'The result in a few words, as the pane shows it'),
        ('captured', 'What was taken: prisoners, guns, stores, the post'),
        ('captured_by', 'The code of the side that took it'),
        ('ships', 'The code of a side whose ships fought there: a small ship mark beside the symbol (Morgan, 25 Nov 2026: orientations only)'),
        ('disputed', 'yes if the sources disagree on the date or the result: the symbol carries a dagger and the pane gives both readings'),
        ('other_won_by', 'The other reading: who it says won'),
        ('other_reading', 'The other reading, in words'),
        ('other_source_ids', 'The sources of the other reading'),
        ('hypothesis_id', 'The Hypotheses row that records the disagreement (SR-19)'),
        ('place', 'Where it happened, in words'),
        ('lat', 'Latitude of the symbol'),
        ('lon', 'Longitude of the symbol'),
        ('coord_source', 'How the place was found: marker, map_read, modern_map, derived, estimate'),
        ('coord_precision_m', 'Good to about this many metres'),
        ('coordinate_basis', 'How the place was found, in words'),
        ('coordinate_confidence', 'high, medium or low'),
        ('overall_confidence', 'high, medium or low (never high without a cited source: SR-21)'),
        ('source_ids', 'Sources for the result and the place (S01; S02)'),
        ('notes', ''),
        ('review_status', ''),
    ],
    'Control places': [
        ('cplace_id', 'The place\'s own id (CP01 ...); unique across the workbooks'),
        ('playback_id', 'The orientation playback it is drawn in'),
        ('name', 'Its name at the time'),
        ('kind', 'city, town, village, fort, port, post or settlement'),
        ('lat', 'Latitude'),
        ('lon', 'Longitude'),
        ('coord_source', 'How the place was found: marker, map_read, modern_map, derived, estimate'),
        ('coord_precision_m', 'Good to about this many metres'),
        ('coordinate_basis', 'How the place was found, in words'),
        ('coordinate_confidence', 'high, medium or low'),
        ('source_ids', 'Sources for the place'),
        ('notes', ''),
    ],
    'Control': [
        ('control_id', 'The row\'s own id (CT01 ...); unique across the workbooks'),
        ('cplace_id', 'The place (Control places sheet)'),
        ('from', 'The date from which it is held this way (YYYY-MM-DD)'),
        ('held_by', 'The code of the side that holds it (Sides sheet), or contested (no side firmly holds it)'),
        ('basis', 'Why, in words: the capture, the evacuation, the treaty'),
        ('event_id', 'The event that changed it, if there is one'),
        ('method', 'stated (a cited source says who held it) or inferred'),
        ('confidence', 'high, medium or low (never high without a cited source: SR-21)'),
        ('source_ids', 'Sources'),
        ('notes', ''),
        ('review_status', ''),
    ],
}

WHY = 'Orientation playbacks (Morgan, 25 Nov 2026: HIST 340 South Carolina chapter).'
PRESET = [
    ('style', 'orientation', 'Draw the playback as an orientation: clashes by who won, places by who held them, no unit detail', WHY),
    ('scale_bar', 'km', 'The scale bar writes kilometres first', 'A state-wide map.'),
    ('day_pause', False, 'No stop at each day or year end while it plays; it stops once, at the end, with the closing summary',
     'Morgan, 25 Nov 2026: "pause only at the end"; each year\'s summary is in the pane while that year plays.'),
    ('opening_ease', 0.006, 'The slow ease in from the wide opening view when play is pressed', 'SR-04, as the preset operational.'),
    ('zoom.min_factor', 0.85, 'How far out past the whole ground the reader can zoom', 'As the preset operational.'),
    ('zoom.max', 0.3, 'The closest zoom, in screen pixels per metre', 'An orientation shows towns, not units.'),
    ('orientation.month_seconds', 1, 'Seconds of play for a month at the opening speed', 'Morgan, 25 Nov 2026: about a month a second.'),
    ('orientation.event_seconds', 0.5, 'Seconds of play added to a month for each event in it, so a busy month plays slower',
     'Morgan, 25 Nov 2026: slow down busy months (August 1780 has six events).'),
    ('orientation.speeds', '[2, 1, 0.5]', 'The speeds the step button offers, as seconds for a month: slow, normal, fast', 'Morgan, 25 Nov 2026: adjustable.'),
]


def main():
    for w in WARS:
        path = os.path.join(FOLDER, w + '.xlsx'); wb = openpyxl.load_workbook(path)
        for name, cols in SHEETS.items():
            if name in wb.sheetnames: sys.exit('%s already has the sheet %s: this script has been run' % (w, name))
            ws = wb.create_sheet(name)
            for i, (h, _) in enumerate(cols): ws.cell(1, i + 1, h).font = Font(bold=True)
            ws.freeze_panes = 'B2'
        rm = wb['Read me']
        rm.append(['What changed on 25 November 2026', 'Three new sheets for orientation playbacks: Clashes (one row per clash or capture, tied to its '
                   'event: who won, what was taken, the other reading where the sources disagree), Control places (towns, villages, forts and ports) '
                   'and Control (one row each time a place changes hands). Empty for this war. Written by pipeline/orientation_2026_11_25.py.'])
        for name, cols in SHEETS.items():
            rm.append(['Sheet: ' + name, '; '.join('%s: %s' % (h, d) for h, d in cols if d)])
        wb.save(path)
    sh = openpyxl.load_workbook(SHARED); ws = sh['Playback presets']
    if any(r[0] == 'orientation' for r in ws.iter_rows(min_row=2, values_only=True)): sys.exit('the preset orientation is already there')
    for st, v, what, why in PRESET:
        ws.append(['orientation', st, v, what, why])
        for c in ws[ws.max_row]: c.alignment = Alignment(wrap_text=True, vertical='top')
    rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 25 November 2026: the preset orientation')
    rm.cell(2, 1, 'A preset for orientation playbacks (clashes by who won, places by who held them, played month by month, one stop at the end). '
                  'No battle uses it yet. Written by pipeline/orientation_2026_11_25.py.')
    sh.save(SHARED)


if __name__ == '__main__':
    main()
