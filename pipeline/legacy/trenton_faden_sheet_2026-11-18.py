"""18 Nov 2026: Faden's 1777 map rebuilt sharper in four pieces, plus the engraving as printed (the 1:1 view)."""
import copy, json, openpyxl, shutil, os
ROOT = '/home/claude/warmapper'; WB = ROOT + '/data/WarMapper battle data.xlsx'
fit = json.load(open('/home/claude/work/faden/v2/fit.json'))
wb = openpyxl.load_workbook(WB); M = wb['Maps']; h = [c.value for c in M[1]]
if 'xy_from' not in h:
    j = len(h) + 1; M.cell(1, j).value = 'xy_from'; M.cell(1, j)._style = copy.copy(M.cell(1, j - 1)._style); h.append('xy_from')
col = lambda n: h.index(n) + 1
row = [r[0].row for r in M.iter_rows(min_row=2) if r[0].value == 'trenton' and r[1].value == 'faden-1777'][0]
vals = {n: M.cell(row, col(n)).value for n in h}
vals['note'] = ("Faden's engraving, published in London in April 1777, is out of proportion: against the ground it is about 45% too narrow one way, and laid down whole its towns are "
                "1 to 7 km from where they are. So this view stretches it smoothly so 12 towns and crossings fall on their real places and the units line up with it; lettering and roads "
                "are bent as a result, most in the east. The 1:1 button shows the engraving as printed, unstretched and at full detail, with the units placed on it by the same fit.")
vals['fit'] = json.dumps({'method': 'rubber-sheet: warped (thin-plate spline) so 12 towns and crossings fall on their real places', 'points': 12, 'misfit_m': 0, 'm_per_px': 7})
M.delete_rows(row, 1)
for i, c in enumerate(fit['pieces']):
    M.insert_rows(row + i, 1)
    for j in range(1, len(h) + 1):
        s = M.cell(row + i + 1, j) if row + i + 1 <= M.max_row else None
        if s is not None and s.has_style: M.cell(row + i, j)._style = copy.copy(s._style)
    v = dict(vals, file='faden-1777-%d.webp' % i)
    for k, (lon, lat) in zip(('tl', 'tr', 'br', 'bl'), c): v[k + '_lat'] = lat; v[k + '_lon'] = lon
    if i: v.update(note=None, fit=None)
    for n, x in v.items(): M.cell(row + i, col(n)).value = x
r = row + 4; M.insert_rows(r, 1)
for j in range(1, len(h) + 1):
    if M.cell(r - 1, j).has_style: M.cell(r, j)._style = copy.copy(M.cell(r - 1, j)._style)
sh = {'playback_id': 'trenton', 'map_id': 'faden-1777-sheet', 'title': "Faden, Plan of the operations of General Washington (1777), as printed", 'short': '1777 sheet',
      'credit': 'Faden, 1777 · Boston Public Library', 'source_id': 'S37', 'fitted_to_ground': 'no', 'size_px': '%d, %d' % tuple(fit['sheet']['size']), 'file': 'faden-1777-sheet.jpg',
      'scale_note': 'Roughly; the engraving is out of proportion', 'approx_m_per_px': 15,
      'note': "The engraving as Faden printed it, not stretched to the ground. Units are placed on it by the same fit that stretches the 1777 map, so they sit where the engraving draws the places they were at. Press 1777 map to go back.",
      'iiif_service': 'https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:wd3768583', 'iiif_width': 7551, 'iiif_height': 5174, 'iiif_tile': 1024,
      'iiif_scale_factors': '[1, 2, 4, 8, 16, 32, 64]', 'iiif_region': ', '.join(map(str, fit['crop'])), 'iiif_reduced': fit['sheet']['reduced'], 'xy_from': 'pipeline/georef/trenton_faden_fit.json'}
for n, x in sh.items(): M.cell(r, col(n)).value = x
PS = wb['Playback settings']
last = max(x[0].row for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton')
have = {x[1].value for x in PS.iter_rows(min_row=2) if x[0].value == 'trenton'}
add = [('bases.5.id', 'fs', 'A base reached from another (of): not on the base bar'), ('bases.5.label', '1777 sheet', None), ('bases.5.short', '1777', None),
       ('bases.5.map', 'faden-1777-sheet', None), ('bases.5.of', 'fd', 'The 1:1 button on that base opens this one; that base\'s button brings it back')]
for k, v, d in add:
    if k in have: continue
    PS.insert_rows(last + 1, 1); last += 1
    for j in range(1, 5):
        if PS.cell(last - 1, j).has_style: PS.cell(last, j)._style = copy.copy(PS.cell(last - 1, j)._style)
    PS.cell(last, 1).value = 'trenton'; PS.cell(last, 2).value = k; PS.cell(last, 3).value = v; PS.cell(last, 4).value = d
wb.save(WB)
d = ROOT + '/playbacks/trenton/'
for f in os.listdir('/home/claude/work/faden/v2'):
    if f.endswith(('.webp', '.jpg')): shutil.copy('/home/claude/work/faden/v2/' + f, d + f)
shutil.copy('/home/claude/work/faden/v2/fit.json', ROOT + '/pipeline/georef/trenton_faden_fit.json')
print('maps done')
