"""18 Nov 2026: Birmingham at about 06:00 (Elliott; the driving tour) and Greene's road by Parkway Avenue (the driving tour; OpenStreetMap)."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); head = lambda ws: [c.value for c in ws[1]]
D = '1776-12-26 '
S = wb['Sources']; sh = head(S)
if 'S63' not in {r[0].value for r in S.iter_rows(min_row=2)}:
    like = S.max_row; r = like + 1
    row = {'source_id': 'S63', 'title': "Washington's Route to Trenton: driving tour", 'author': 'Washington Crossing Park Association', 'date': 'undated',
           'type': 'Modern secondary: driving-tour leaflet (PDF)', 'citation': 'Washington Crossing Park Association, Titusville, N.J.; roadside signs by the Crossroads of the American Revolution National Heritage Area',
           'page verified?': 'n/a (one page)', 'url': 'https://static1.squarespace.com/static/5b5503d73917eed698765c67/t/620e78714269f42f34c4d409/1645115507082/drivingtour.pdf',
           'rights': 'In copyright. Cited and linked, not hosted.', 'used_for': 'TREN', 'kind': 'reference', 'war': 'ARW', 'rights_status': 'in copyright', 'may_host': 'no: link and cite',
           'rights_checked': '2026-11-18', 'site': 'squarespace.com',
           'notes': "Named by Morgan, 18 Nov 2026. Traces the march on today's roads: Continental Lane and Route 546, Bear Tavern Road over Jacobs Creek to Birmingham (Bear Tavern Road and Upper Ferry Road) at about 6 a.m.; "
                    "Sullivan on by Grand Avenue, Sullivan Way and West State Street; Greene with Washington by Upper Ferry Road, Parkway Avenue and Pennington Road to the Battle Monument; battle at about 8 a.m. Used for the time at Birmingham and Greene's road."}
    for j, n in enumerate(sh, 1):
        if S.cell(like, j).has_style: S.cell(r, j)._style = copy.copy(S.cell(like, j)._style)
        if row.get(n) is not None: S.cell(r, j).value = row[n]
P = wb['Positions']; ph = head(P); pc = lambda n: ph.index(n)
for r in P.iter_rows(min_row=2):
    if r[1].value != 'ARW-TP': continue
    if r[0].value == 'T03':
        for n, v in (('start_earliest', D + '05:00'), ('start_latest', D + '05:30'), ('end_earliest', D + '05:00'), ('end_latest', D + '05:30'), ('show_from', D + '05:10'), ('show_to', D + '05:10'),
                     ('time_basis', 'About 05:10: the army reached Birmingham about two hours after setting off at 04:00 (S59, p. 44; S63), and the creek is a little over half way by the road. A modern marker gives 6 AM (S29).'),
                     ('source_ids', 'S59; S63; S29'), ('source_pages', 'S59 p. 44'), ('cross_checked_by', 'S63')):
            r[pc(n)].value = v
    if r[0].value == 'T04':
        for n, v in (('start_earliest', D + '05:45'), ('start_latest', D + '06:15'), ('end_earliest', D + '05:45'), ('end_latest', D + '06:30'), ('show_from', D + '06:00'), ('show_to', D + '06:00'),
                     ('time_basis', 'About 06:00: two hours after the march began (S59, p. 44); the driving tour gives 6 a.m. (S63). A modern marker gives 7 AM (S29). See TC02.'),
                     ('source_ids', 'S21; S22; S28; S29; S33; S59; S63'), ('source_pages', 'S59 p. 44; S22 p. 8'), ('cross_checked_by', 'S63')):
            r[pc(n)].value = v
GREENE = ('40.26605, -74.81902; 40.26805, -74.81454; 40.26791, -74.81343; 40.26766, -74.81189; 40.26751, -74.81094; 40.26737, -74.81000; 40.26705, -74.80907; 40.26631, -74.80714; '
          '40.26591, -74.80617; 40.26554, -74.80532; 40.26453, -74.80359; 40.26378, -74.80231; 40.26319, -74.80132; 40.26207, -74.79950; 40.26133, -74.79833; 40.26061, -74.79750; '
          '40.25905, -74.79596; 40.25646, -74.79357; 40.25423, -74.79151; 40.25156, -74.78907; 40.24932, -74.78696; 40.24705, -74.78487; 40.24505, -74.78369; 40.24403, -74.78278; '
          '40.24318, -74.78171; 40.24251, -74.78057; 40.24209, -74.77960; 40.24129, -74.77780; 40.24063, -74.77627; 40.24032, -74.77561; 40.23818, -74.77461; 40.23531, -74.77185')
R = wb['Routes']; rh = head(R); rc = lambda n: rh.index(n)
for r in R.iter_rows(min_row=2):
    if r[1].value != 'ARW-TP': continue
    if r[0].value == 'RT01': r[rc('end')].value = D + '05:10'
    if r[0].value == 'RT02': r[rc('start')].value = D + '05:10'; r[rc('end')].value = D + '06:00'
    if r[0].value == 'RT03':
        r[rc('start')].value = D + '06:00'; r[rc('waypoints (lat, lon; ...)')].value = GREENE; r[rc('source_ids')].value = 'S21; S22; S63; S39'
        r[rc('confidence')].value = 'medium'
        r[rc('source_wording')].value = ("Paraphrase: Greene's wing turned left at Birmingham onto Upper Ferry Road, which becomes Parkway Avenue, and right onto Pennington Road (S63); "
                                         "it took a short road from Birmingham to the Scotch Road (S22) and joined the Pennington road about a mile beyond the village (S21).")
        r[rc('notes')].value = ("Traced along today's Upper Ferry Road and Parkway Avenue (OpenStreetMap, 18 Nov 2026) to Pennington Road, as the driving tour gives it (S63). "
                                "Parkway Avenue passes the south end of today's Scotch Road, so it also fits the Scotch Road accounts. Replaces a straight guess and a loop up Scotch Road.")
E = wb['Events']; eh = head(E)
for r in E.iter_rows(min_row=2):
    if r[0].value == 'TE05' and r[1].value == 'ARW-TP':
        r[eh.index('time_earliest')].value = D + '05:45'; r[eh.index('time_latest')].value = D + '06:30'; r[eh.index('playback_at')].value = D + '06:00'
        r[eh.index('source_ids')].value = 'S21; S22; S28; S59; S63'
C = wb['Conflicts']; chh = head(C); last = chh[-1]
if not str(last).startswith('v11'):
    j = len(chh) + 1; C.cell(1, j).value = 'v11 update (18 Nov 2026)'; C.cell(1, j)._style = copy.copy(C.cell(1, j - 1)._style)
    for k in range(2, C.max_row + 1): C.cell(k, j)._style = copy.copy(C.cell(k, j - 1)._style)
    chh.append('v11 update (18 Nov 2026)')
for r in C.iter_rows(min_row=2):
    if r[0].value == 'TC02':
        C.cell(r[0].row, len(chh)).value = ("Elliott has the army take about two hours to reach Birmingham (S59, p. 44), and the march began at 04:00; the Washington Crossing Park Association's driving tour gives 6 a.m. (S63). "
                                            "The split is now shown at about 06:00, and Jacobs Creek at about 05:10. The marker's 7 AM (S29) is the outlier.")
        r[chh.index('how the pilot handled it')].value = 'Split placed at Birmingham at about 06:00 (S59; S63). The 7 a.m. halt is kept as T05 with low confidence.'
G = wb['Gaps']; gh = head(G)
for r in G.iter_rows(min_row=2):
    if r[0].value == 'TG02':
        G.cell(r[0].row, gh.index('v9 update') + 1).value = ("18 Nov 2026: Greene's road from Birmingham now follows today's Upper Ferry Road and Parkway Avenue to Pennington Road, as the driving tour does (S63); "
                                                             "it passes the south end of today's Scotch Road. The straight guess is gone. The pickets are unchanged.")
Rm = wb['Read me']
merged = [str(x) for x in Rm.merged_cells.ranges]; heights = {k: v.height for k, v in Rm.row_dimensions.items() if v.height}
for x in merged: Rm.unmerge_cells(x)
Rm.insert_rows(4, 3)
for x in merged:
    a, b = x.split(':'); ra, rb = int(a[1:]), int(b[1:]); s = 3 if ra >= 4 else 0
    Rm.merge_cells('%s%d:%s%d' % (a[0], ra + s, b[0], rb + s))
for k in sorted(heights, reverse=True):
    if k >= 4: Rm.row_dimensions[k + 3].height = heights[k]
for k in range(4, 7): Rm.merge_cells('A%d:D%d' % (k, k)); Rm.row_dimensions[k].height = None
Rm.row_dimensions[5].height = 72
for i, txt in enumerate(["What changed on 18 November 2026 (route check): Birmingham at 6 a.m.; Greene's road by Parkway Avenue",
                         "Checked against the Washington Crossing Park Association's driving tour (new source S63). The army now reaches Birmingham at about 06:00 (T04; event TE05), two hours after the march began, as Elliott (S59) and the tour have it, and Jacobs Creek at about 05:10 (T03). "
                         "Greene's road (RT03) now follows today's Upper Ferry Road and Parkway Avenue to Pennington Road, as the tour gives it, in place of a loop up Scotch Road and a straight guess; it passes the south end of today's Scotch Road. Sullivan's road already matched the tour (Bear Tavern Road, Grand Avenue, Sullivan Way, West State Street). See TC02 (v11 column) and TG02."]):
    c = Rm.cell(4 + i, 1); src = Rm.cell(7 if i == 0 else 8, 1)
    if src.has_style: c._style = copy.copy(src._style)
    c.value = txt
wb.save(WB); print('routes done')
