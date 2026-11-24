"""Split the single master workbook into one workbook per war, plus one shared workbook (run once, 23 Nov 2026).

  python3 pipeline/split_workbook.py "data/WarMapper battle data.xlsx" "data/WarMapper battle data"

Before 23 Nov 2026 the battle data was one workbook, data/WarMapper battle data.xlsx. This script wrote the folder that replaces it:

  Sources and notes.xlsx   Read me (the change log), Sources, Source candidates, and the two gaps that belong to no one war
  <war>.xlsx               every other sheet, the same sheets in the same order in each file, holding only that war's rows

A row goes to the war its own ids name: a campaign, a battle, a side, a unit, a playback or a reconstruction (see WAR_OF below).
Rows keep the order they had, so a playback's rows come out in the same order and every battle file is written exactly as before.
Formulas that point at their own row (Positions unit_name, map_link; Source uses) are moved to the row's new place. Styles, column
widths, frozen panes, filters and drop-downs are copied. The script is kept as the record of how the split was made; it is not part of
the export, and running it again would overwrite the folder with a split of the old file.
"""
import copy, os, sys
import openpyxl
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FILES = {'ARW': 'Revolutionary War', 'ACW': 'U.S. Civil War', 'PHW': 'Philippine War', 'WW1': 'World War I'}
SHARED = 'Sources and notes'
SHARED_SHEETS = ('Sources', 'Source candidates')      # one register for every war: an S-id is never used twice
# Georeference is a page of notes, not a table: which rows of it are about which war (1-based rows of the old sheet)
GEOREF = {'ACW': (2, 46), 'ARW': (49, 121), 'WW1': (124, 138)}
GEOREF_TITLE = {'ACW': 'Georeference: Gettysburg, the Bachelder map', 'ARW': "Georeference: Trenton, Wiederhold's sketch",
                'WW1': 'Georeference: First Ypres, the sketch maps of the British official history',
                'PHW': 'Georeference: the Philippine War maps are fitted by the scripts in pipeline/georef/ (no table here)'}


def rows_of(ws):
    it = ws.iter_rows(values_only=True); head = next(it)
    return head, [dict(zip(head, r)) for r in it]


def copy_cell(src, dst, value):
    dst.value = value
    if src.has_style:
        dst.font = copy.copy(src.font); dst.fill = copy.copy(src.fill); dst.border = copy.copy(src.border)
        dst.alignment = copy.copy(src.alignment); dst.number_format = src.number_format; dst.protection = copy.copy(src.protection)


def moved(value, col, old_row, new_row):
    """A formula written for row old_row, rewritten for row new_row."""
    if isinstance(value, str) and value.startswith('=') and old_row != new_row:
        return Translator(value, origin='%s%d' % (col, old_row)).translate_formula('%s%d' % (col, new_row))
    return value


def copy_sheet(ws, out, keep_rows, title_of=None, header_rows=1, freeze=None):
    """Copy the header row(s) and the rows numbered keep_rows (1-based, in order) of ws into a new sheet of workbook out."""
    new = out.create_sheet(ws.title)
    width = ws.max_column
    plan = list(range(1, header_rows + 1)) + list(keep_rows)
    for new_r, old_r in enumerate(plan, 1):
        for c in range(1, width + 1):
            s = ws.cell(old_r, c); col = get_column_letter(c)
            v = moved(s.value, col, old_r, new_r)
            if title_of and old_r > header_rows: v = title_of(old_r, c, v)
            if s.value is None and not s.has_style: continue
            copy_cell(s, new.cell(new_r, c), v)
        h = ws.row_dimensions[old_r].height
        if h: new.row_dimensions[new_r].height = h
    for k, d in ws.column_dimensions.items():
        if d.width: new.column_dimensions[k].width = d.width
        if d.hidden: new.column_dimensions[k].hidden = True
    where = {o: n for n, o in enumerate(plan, 1)}
    for m in ws.merged_cells.ranges:
        if m.min_row in where and m.max_row in where and where[m.max_row] - where[m.min_row] == m.max_row - m.min_row:
            new.merge_cells(start_row=where[m.min_row], start_column=m.min_col, end_row=where[m.max_row], end_column=m.max_col)
    new.freeze_panes = freeze if freeze is not None else ws.freeze_panes
    last = len(plan)
    if ws.auto_filter.ref and last > header_rows: new.auto_filter.ref = 'A1:%s%d' % (get_column_letter(width), last)
    for dv in ws.data_validations.dataValidation:      # the drop-downs, over the whole of the copied column
        cols = sorted({str(r).split(':')[0].rstrip('0123456789') for r in str(dv.sqref).split()})
        nd = DataValidation(type=dv.type, formula1=dv.formula1, allow_blank=dv.allow_blank)
        for col in cols: nd.add('%s2:%s%d' % (col, col, max(last, 2) + 200))
        new.add_data_validation(nd)
    new.sheet_properties.tabColor = ws.sheet_properties.tabColor
    return new


def main(src, folder):
    wb = openpyxl.load_workbook(src)
    V = {ws.title: rows_of(ws) for ws in wb.worksheets if ws.title not in ('Read me', 'Georeference')}
    get = lambda s: V[s][1]
    camp = {r['campaign_id']: r['war_id'] for r in get('Campaigns') if r['campaign_id']}
    bat = {r['battle_id']: camp[r['campaign_id']] for r in get('Battles') if r['battle_id']}
    side = {r['side_id']: r['war_id'] for r in get('Sides') if r['side_id']}
    unit = {r['unit_id']: side[r['side_id']] for r in get('Units') if r['unit_id']}
    pb = {r['playback_id']: camp[r['campaign_id']] for r in get('Playbacks') if r['playback_id']}
    rec = {r['recon_id']: pb[r['playback_id']] for r in get('Reconstructions') if r['recon_id']}
    WAR_OF = {'Wars': lambda r: r['war_id'], 'Campaigns': lambda r: r['war_id'], 'Battles': lambda r: camp.get(r['campaign_id']),
              'Phases': lambda r: bat.get(r['battle_id']), 'Sides': lambda r: r['war_id'], 'Units': lambda r: side.get(r['side_id']),
              'Assignments': lambda r: unit.get(r['unit_id']), 'Positions': lambda r: camp.get(r['campaign_id']),
              'Routes': lambda r: camp.get(r['campaign_id']), 'Events': lambda r: camp.get(r['campaign_id']),
              'Summaries': lambda r: pb.get(r['playback_id']), 'Conflicts': lambda r: bat.get(r['battle_id']),
              'Gaps': lambda r: bat.get(r['battle_id']), 'Places': lambda r: 'WW1',        # every place on the sheet is a Ypres place
              'Source uses': lambda r: camp.get(r['campaign_id']), 'Checks': lambda r: bat.get(r['battle']),
              'Playback settings': lambda r: pb.get(r['playback_id']), 'Playbacks': lambda r: pb.get(r['playback_id']),
              'Tracks': lambda r: pb.get(r['playback_id']), 'Nations': lambda r: pb.get(r['playback_id']),
              'Labels': lambda r: pb.get(r['playback_id']), 'Maps': lambda r: pb.get(r['playback_id']),
              'Reconstructions': lambda r: pb.get(r['playback_id']), 'Recon layers': lambda r: rec.get(r['recon_id'])}
    title = {r['source_id']: r['title'] for r in get('Sources') if r['source_id']}
    os.makedirs(folder, exist_ok=True)
    order = [ws.title for ws in wb.worksheets]
    loose = {}                                          # rows that belong to no one war: they go to the shared file
    for war, name in FILES.items():
        out = openpyxl.Workbook(); out.remove(out.active)
        for s in order:
            ws = wb[s]
            if s in SHARED_SHEETS: continue
            if s == 'Read me': readme(out, ws, war); continue
            if s == 'Georeference':
                a, b = GEOREF.get(war, (0, -1))
                g = copy_sheet(ws, out, range(a, b + 1))
                g['A1'] = GEOREF_TITLE[war]
                continue
            head, rows = V[s]; f = WAR_OF[s]; keep = []
            for i, r in enumerate(rows, 2):
                if all(v is None for v in r.values()): continue
                w = f(r)
                if w == war: keep.append(i)
                elif w not in FILES: loose.setdefault(s, set()).add(i)
            def plain_title(old_r, c, v, s=s, head=head, rows=rows):   # Source uses: the title, as text (Sources is in the shared file)
                if s == 'Source uses' and head[c - 1] == 'title': return title.get(rows[old_r - 2]['source_id'])
                return v
            copy_sheet(ws, out, keep, title_of=plain_title, freeze='C2' if s == 'Units' else None)
        out.save(os.path.join(folder, name + '.xlsx'))
    out = openpyxl.Workbook(); out.remove(out.active)
    shared_readme(out, wb['Read me'])
    for s in SHARED_SHEETS: copy_sheet(wb[s], out, range(2, wb[s].max_row + 1))
    for s, rows in sorted(loose.items()): copy_sheet(wb[s], out, sorted(rows))
    out.save(os.path.join(folder, SHARED + '.xlsx'))
    print('written:', ', '.join(sorted(os.listdir(folder))), '| shared rows:', {k: len(v) for k, v in loose.items()})


COUNTS = [('Position rows', '=COUNTA(Positions!A:A)-1'), ('Rows with coordinates', '=COUNTIF(Positions!O:O,"<>")-1'),
          ('Rows still needing review', '=COUNTIF(Positions!AC:AC,"Needs review")'), ('Rows accepted', '=COUNTIF(Positions!AC:AC,"Accepted")'),
          ('Units', '=COUNTA(Units!A:A)-1'), ('Events', '=COUNTA(Events!A:A)-1'), ('Disputed points', '=COUNTA(Conflicts!A:A)-1'),
          ('Gaps logged', '=COUNTA(Gaps!A:A)-1'), ('Playbacks', '=COUNTA(Playbacks!A:A)-1')]


def readme(out, old, war):
    """A war's own Read me: what is in the file, how it fits with the others, and its counts."""
    ws = out.create_sheet('Read me'); ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 110
    bold = copy.copy(old['A1'].font)
    lines = [('WarMapper battle data: %s' % FILES[war], None),
             ('What this file is', 'The battle data for one war. Every war has a workbook like this one, with the same sheets in the same order; '
              'a sheet with nothing for this war keeps its headings so the layout stays the same.'),
             ('Where the rest is', 'Sources, Source candidates and the change log of the battle data are in "Sources and notes.xlsx", in the same folder. '
              'Every source id (S01, S02 ...) is listed there once, for every war: add a new source there, with the next free id.'),
             ('How it is used', 'python3 tools/export_battles.py reads every workbook in the folder and writes each playback\'s battle file '
              '(playbacks/<playback>/battle.json). It also writes each sheet as a CSV file under csv/ in this folder, so GitHub can show what changed.'),
             ('Split', 'Written on 23 Nov 2026 from the single workbook "WarMapper battle data.xlsx", which it replaces (pipeline/split_workbook.py). '
              'Every row and every id is as it was.'),
             (None, None), ('Counts', None)] + COUNTS
    for i, (a, b) in enumerate(lines, 1):
        ws.cell(i, 1, a); ws.cell(i, 2, b)
        if a and (b is None or i == 1): ws.cell(i, 1).font = bold
        ws.cell(i, 2).alignment = openpyxl.styles.Alignment(wrap_text=True, vertical='top')


def shared_readme(out, old):
    """The shared Read me: the change log as it was, with a new first entry for the split. The old counts block, whose formulas
    counted rows of the single workbook, is replaced by a pointer to the counts on each war's Read me."""
    ws = out.create_sheet('Read me')
    for k, d in old.column_dimensions.items():
        if d.width: ws.column_dimensions[k].width = d.width
    new = [('What changed on 23 November 2026: the workbook is split by war',),
           ('The battle data is now one workbook per war (Revolutionary War, U.S. Civil War, Philippine War, World War I) and this one, '
            'Sources and notes, in the folder data/WarMapper battle data/. Each war\'s workbook has the same sheets in the same order and holds only '
            'that war\'s rows. This file holds what every war shares: this change log, Sources and Source candidates (one register, so an S-id '
            'is never used twice), and the two gaps that belong to no one war. No id changed, and every battle file is written exactly as before. '
            'export_battles.py reads all five files, and writes each sheet as a CSV file under csv/ so a change shows line by line on GitHub.',),
           (None,)]
    off = len(new); counts = None
    for i, r in enumerate(new, 1):
        ws.cell(i, 1, r[0]).alignment = openpyxl.styles.Alignment(wrap_text=True, vertical='top')
    ws.cell(1, 1).font = copy.copy(old['A2'].font)
    ws.merge_cells('A2:D2'); ws.row_dimensions[2].height = 90
    for r in range(1, old.max_row + 1):
        a = old.cell(r, 1).value
        if a == 'Counts': counts = r
        if counts and r >= counts and r <= counts + 14:             # the old counts block
            if r == counts:
                ws.cell(r + off, 1, 'Counts: each war\'s own counts are now on the Read me sheet of its workbook.').font = copy.copy(old.cell(r, 1).font)
            continue
        for c in range(1, old.max_column + 1):
            s = old.cell(r, c)
            if s.value is None and not s.has_style: continue
            copy_cell(s, ws.cell(r + off, c), s.value)
        if old.row_dimensions[r].height: ws.row_dimensions[r + off].height = old.row_dimensions[r].height
    for m in old.merged_cells.ranges:
        if counts and counts <= m.min_row <= counts + 14: continue
        ws.merge_cells(start_row=m.min_row + off, start_column=m.min_col, end_row=m.max_row + off, end_column=m.max_col)


if __name__ == '__main__':
    main(*sys.argv[1:3])
