"""25 Nov 2026, Session 5 of claude/sc-orientation-prompt.md: assemble the HIST 340 South Carolina chapter. Safe to run again.

1. Adds the sheet "Next links" to every war workbook, after Links (the war workbooks must keep the same sheets). One row per pair of
   playbacks that follow one another in a course chapter, both of the same war:
     link_id          N01, N02 ...
     from_playback    the playback_id that comes first (the orientation)
     to_playback      the playback_id that comes next (Cowpens)
     label            optional: the next playback's name as the first one shows it (default: its title)
     back_label       optional: the first playback's name as the next one shows it (default: its title)
     opens_at         optional: where the next one opens. Empty: on its own opening view (wide, no symbols until play; SR-02, SR-04)
     back_opens_at    optional: where the first one opens when the reader goes back. Empty: at its end, the closing pane
     chapter          the course chapter the pair belongs to (courses/<course>/course.json), for the record
     notes
   The first playback offers the next one at its end ("Next in this chapter"); the next one offers the way back at the top of its pane.
2. Fills the one row of the South Carolina chapter: the orientation leads on to Cowpens.
3. Adds a line to each war workbook's Read me sheet.
"""
import os
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'WarMapper battle data')
COLS = [('link_id', 9), ('from_playback', 18), ('to_playback', 18), ('label', 30), ('back_label', 30), ('opens_at', 18), ('back_opens_at', 18),
        ('chapter', 22), ('notes', 60)]
ROWS = {'Revolutionary War.xlsx': [
    ['N01', 'sc-orientation', 'cowpens', 'Battle of Cowpens', 'South Carolina, 1775 to Cowpens: the orientation', None, None, 'hist-340-sc',
     'HIST 340, 16 Jan: the chapter "South Carolina: from the orientation to Guilford Courthouse". The orientation ends on 17 Jan 1781, the '
     'morning of Cowpens; Cowpens opens on its own wide view so its landing rules hold. Greene\'s campaign and Guilford Courthouse join the '
     'chain when they are built (Cowpens to the campaign, the campaign to Guilford). Session 5, 25 Nov 2026.']]}
README = ('Next links (25 Nov 2026)', 'One row per pair of playbacks that follow one another in a course chapter (for HIST 340: the South Carolina '
          'orientation, then Cowpens). The first one offers the next at its end, "Next in this chapter"; the next one offers the way back at the top '
          'of its side pane. Columns: link_id, from_playback and to_playback (playback ids from Playbacks, of this war), label and back_label '
          '(optional names), opens_at (optional: where the next one opens; its own opening view if empty), back_opens_at (optional: where the '
          'first one opens going back; its end if empty), chapter (the course chapter id), notes.')

for f in sorted(os.listdir(FOLDER)):
    if not f.endswith('.xlsx') or f == 'Sources and notes.xlsx' or f.startswith('~$'): continue
    path = os.path.join(FOLDER, f); wb = openpyxl.load_workbook(path); changed = False
    if 'Next links' not in wb.sheetnames:
        ws = wb.create_sheet('Next links', wb.sheetnames.index('Links') + 1)
        for c, (name, w) in enumerate(COLS, 1):
            x = ws.cell(1, c, name); x.font = Font(bold=True); x.fill = PatternFill('solid', fgColor='E2EFDA'); x.alignment = Alignment(wrap_text=True, vertical='top')
            ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w
        ws.freeze_panes = 'B2'; changed = True
    ws = wb['Next links']
    have = {ws.cell(r, 1).value for r in range(2, ws.max_row + 1)}
    for row in ROWS.get(f, []):
        if row[0] in have: continue
        ws.append(row); changed = True
        for c in range(1, len(row) + 1): ws.cell(ws.max_row, c).alignment = Alignment(wrap_text=True, vertical='top')
    rm = wb['Read me']
    if not any(rm.cell(r, 1).value == README[0] for r in range(1, rm.max_row + 1)):
        rm.append([]); rm.append(list(README)); rm.cell(rm.max_row, 2).alignment = Alignment(wrap_text=True, vertical='top'); changed = True
    if changed: wb.save(path); print(f, 'updated')
    else: print(f, 'already done')
