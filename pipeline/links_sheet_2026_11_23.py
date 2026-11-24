"""23 Nov 2026 (BP-34): add the Links sheet to every war workbook, after Playbacks. Run once.

One row per campaign playback and battle playback that link to each other (both of the same war):
  link_id            L01, L02 ...
  campaign_playback  the playback_id of the campaign (usually followed by the day)
  battle_playback    the playback_id of the battle inside it (usually followed by the minute)
  label              optional: the battle's name as the campaign lists it (default: the battle playback's title)
  campaign_label     optional: the campaign's name as the battle names it (default: the campaign playback's title)
  opens_at           optional: the moment the battle opens at from the campaign (default: the battle playback's start)
  notes
The dates of each come from its Playbacks row. With no rows, no battle file has a links section.
"""
import os
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'WarMapper battle data')
COLS = [('link_id', 9), ('campaign_playback', 18), ('battle_playback', 18), ('label', 30), ('campaign_label', 30), ('opens_at', 18), ('notes', 60)]
for f in sorted(os.listdir(FOLDER)):
    if not f.endswith('.xlsx') or f == 'Sources and notes.xlsx': continue
    path = os.path.join(FOLDER, f); wb = openpyxl.load_workbook(path)
    if 'Links' in wb.sheetnames: continue
    ws = wb.create_sheet('Links', wb.sheetnames.index('Playbacks') + 1)
    for c, (name, w) in enumerate(COLS, 1):
        x = ws.cell(1, c, name); x.font = Font(bold=True); x.fill = PatternFill('solid', fgColor='E2EFDA'); x.alignment = Alignment(wrap_text=True, vertical='top')
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w
    ws.freeze_panes = 'B2'
    rm = wb['Read me']; rm.append([]); rm.append(['Links (23 Nov 2026)', 'One row per campaign playback and battle playback inside it (BP-34). '
        'The campaign lists its battles, with a button that opens each at its date; the battle links back to the campaign at the date on its clock. '
        'Columns: link_id, campaign_playback, battle_playback (playback ids from Playbacks), label and campaign_label (optional names), opens_at '
        '(optional: where the battle opens from the campaign; its start if empty), notes. Dates come from Playbacks.'])
    rm.cell(rm.max_row, 2).alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(path); print(f)
