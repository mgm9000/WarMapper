"""18 Nov 2026 (Morgan): Ypres units move too fast across the timeline. Play at half a day a second (was 0.85, which the player
rounded up to a whole day a second); the player now spreads each move over a full day, eased, instead of the last two-thirds of one."""
import openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB); PS = wb['Playback settings']; n = 0
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'ypres' and r[1].value == 'rate':
        r[2].value = 0.5; r[3].value = 'Days per second while playing with the 1-day step (0.5 since 18 Nov 2026: slower, so moves read smoothly; was 0.85)'; n += 1
assert n == 1, n
wb.save(WB); print('ypres rate 0.5')
