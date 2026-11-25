"""Cowpens: Morgan's second review of the playback (24 Nov 2026, evening).

Data changes (with player changes in app/player.js):
- The light infantry, the Legion infantry, the 7th and the 71st laid down their arms where they stood (CP56, CP66, CP76, CP104) but
  stayed drawn in line until 08:30, in front of the Americans. Their rows now end at 07:56 on the map (show_to), a few minutes after they
  surrendered, and their tracks are taken off the map after their last row (hide_after_last_row), as the two guns' already are
  (CP85, CP95 end at 07:51): the unit fades over two minutes and is listed as no longer on the map. The
  readings, sources and times recorded are unchanged; only how long the row is drawn.
- Washington (CP37) reached the south-east end of the road at 08:16 while Tarleton's party (CP137, CP127) were still 1 km behind him on
  the same road, so he was drawn up to 230 m ahead of them. He is now drawn arriving there at 08:22 (show_from), so he stays behind them
  the whole way: Tarleton "was pursued twenty-four miles, but ... we could never overtake him" (S96). The row's own times are unchanged.
- The Cowpens wording for a unit no longer on the map says why (texts.after, texts.lost).
- Camera and clock: follow.hold_until 06:12 (the camera stays on the whole ground until Morgan's lines are on the map), follow.glide_rate
  0.006 with glide_seconds 14 (a slower ease in), lead.until 06:20 (the 4x play of the forming-up ends before Tarleton's column sets off,
  so its march, 06:22 to 06:53, plays at 1 minute a second).
It stops if CP56 already ends at 07:56.
"""
import os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from cowpens_audit_2026_11_24 import header, last_row, rows_by_id, setv, add_note

WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
SHARED = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
PB = 'cowpens'; DAY = '1781-01-17 '
SURRENDER = ['CP56', 'CP66', 'CP76', 'CP104']


def main():
    wb = openpyxl.load_workbook(WAR)
    ps = wb['Positions']; h = header(ps); ids = rows_by_id(ps)
    col = lambda name: h.index(name) + 1
    
    assert str(ps.cell(ids['CP56'], col('show_to')).value).strip() != DAY + '07:56', 'already done'
    for pid in SURRENDER:
        r = ids[pid]
        assert 'arms' in str(ps.cell(r, col('activity')).value) or 'surrender' in str(ps.cell(r, col('activity')).value), pid
        ps.cell(r, col('show_to')).value = DAY + '07:56'
        setv(ps, r, 'notes', add_note('24 Nov 2026, Morgan\'s review: drawn until 07:56, not 08:30. The unit surrendered here; like the guns it is then taken off the map instead of standing in line in front of the Americans. The reading and its times are unchanged.'))
    tk = wb['Tracks']; th = header(tk)
    for i in range(2, last_row(tk) + 1):
        if tk.cell(i, 1).value == PB and tk.cell(i, 2).value in ('C-BR-LI', 'C-BR-LEGI', 'C-BR-7', 'C-BR-71'):
            tk.cell(i, th.index('hide_after_last_row') + 1).value = 'yes'   # as the guns' tracks: off the map after the last row, not left standing
    r = ids['CP37']
    ps.cell(r, col('show_from')).value = DAY + '08:22'
    setv(ps, r, 'notes', add_note('24 Nov 2026, Morgan\'s review: drawn arriving at 08:22, not 08:16. At 08:16 he was drawn up to 230 m ahead of Tarleton\'s party on the same road; the sources say he never caught them (S96). Times recorded are unchanged.'))
    st = wb['Playback settings']
    have = {st.cell(i, 2).value: i for i in range(2, last_row(st) + 1) if st.cell(i, 1).value == PB}
    def setting(k, v, what=None):
        if k in have: st.cell(have[k], 3).value = v
        else:
            n = last_row(st) + 1; st.cell(n, 1, PB); st.cell(n, 2, k); st.cell(n, 3, v); have[k] = n
        if what: st.cell(have[k], 4, what)
    setting('follow.hold_until', '1781-01-17T06:12', 'The camera stays on the whole ground until this moment (Morgan\'s lines come onto the map), then eases in')
    setting('follow.glide_rate', 0.006, 'How fast the camera eases in after the hold (the player\'s default is 0.03)')
    setting('follow.glide_seconds', 14, 'Once the hold ends, the camera eases in from the whole ground to the action over this many seconds')
    setting('lead.until', '1781-01-17T06:20', 'The forming-up plays at lead.rate until here, before Tarleton\'s column sets off; its march plays at 1 minute a second')
    setting('texts.after', 'The last record for this unit. A unit that surrendered is taken off the map a few minutes after it laid down its arms.')
    setting('texts.lost', 'Not on the map any more: it surrendered, was taken or left the field. Its last record is below.')
    wb['Read me'].append(['Cowpens: second review (24 Nov 2026)', 'Surrendered infantry leave the map at 07:56 (CP56, CP66, CP76, CP104); Washington drawn arriving at 08:22 (CP37) so he stays behind Tarleton; camera holds wide until 06:12; the column marches at 1 minute a second. See pipeline/cowpens_review2_2026_11_24.py.'])
    sh = openpyxl.load_workbook(SHARED); rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026 (late): the Cowpens playback after Morgan\'s second review')
    rm.cell(2, 1, 'Revolutionary War.xlsx, Cowpens: the light infantry, Legion infantry, 7th and 71st (CP56, CP66, CP76, CP104) are drawn until 07:56, a few minutes after they laid down their arms, '
                  'not 08:30; Washington\'s pursuit (CP37) is drawn arriving at 08:22, not 08:16, so he stays behind Tarleton; settings follow.hold_until, follow.glide_rate, follow.glide_seconds, '
                  'lead.until, texts.after and texts.lost. No reading, source or recorded time changed. With player changes: a route taken fades once its unit moves on without a route. '
                  'Written by pipeline/cowpens_review2_2026_11_24.py.')
    wb.save(WAR); sh.save(SHARED); print('written')


if __name__ == '__main__':
    main()
