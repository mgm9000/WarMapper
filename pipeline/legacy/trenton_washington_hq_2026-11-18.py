"""18 Nov 2026 (Morgan): Washington's headquarters ran ahead of Greene and Knox from 07:30 and passed the Hessian picket before it was attacked.
Cause: the HQ track went straight from Birmingham (T04) to Washington's post (T26), so it kept moving while Greene's column halted at T05.
Sources: Washington rode with Greene's division (S21, S22); he was at the head of it when the picket was attacked, then posted himself
on the high ground above the town (S22 p. 11; S23; S59 p. 46). Fix: HQ shares Greene's halt (T05) and the attack on the picket (T19),
then goes on to its post along the first part of RT06."""
import openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); T = wb['Tracks']; h = [c.value for c in T[1]]; col = lambda k: h.index(k)
done = False
for r in T.iter_rows(min_row=2):
    if r[0].value == 'trenton' and r[col('track_id')].value == 'T-US-HQ':
        assert r[col('rows')].value in ('T02; T03; T04; T26', 'T02; T03; T04; T05; T19; T26'), r[col('rows')].value
        r[col('rows')].value = 'T02; T03; T04; T05; T19; T26'
        r[col('start_route')].value = 'RT06'; r[col('start_route_points')].value = 3
        r[col('nudge')].value = '0, -26'
        done = True
assert done
wb.save(WB); print('HQ track fixed')
