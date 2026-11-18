"""Record the check of Trenton against Elliott (CMH), the 1929 history (S22) and two Journal of the American Revolution articles,
and the Trenton and Ypres playback improvements, in the master workbook. Run once (17 Nov 2026)."""
import copy, openpyxl
WB = '/home/claude/warmapper/data/WarMapper battle data.xlsx'
wb = openpyxl.load_workbook(WB)
D = '1776-12-26 '


def head(ws): return [c.value for c in ws[1]]


def add(ws, rowdict, like):
    h = head(ws); r = ws.max_row + 1
    for j, name in enumerate(h, 1):
        c = ws.cell(r, j); src = ws.cell(like, j)
        if src.has_style: c._style = copy.copy(src._style)
        if rowdict.get(name) is not None: c.value = rowdict[name]
    return r


def newcol(ws, title, width):
    j = ws.max_column + 1
    c = ws.cell(1, j); c.value = title; c._style = copy.copy(ws.cell(1, j - 1)._style)
    ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = width
    for r in range(2, ws.max_row + 1): ws.cell(r, j)._style = copy.copy(ws.cell(r, j - 1)._style)
    return j


def addsrc(cell, *ss):
    for s in ss:
        if s not in str(cell.value or ''): cell.value = (str(cell.value) + '; ' if cell.value else '') + s


# ---------------------------------------------------------------- sources
S = wb['Sources']; sh = head(S)
add(S, {'source_id': 'S59', 'title': 'The New Jersey Campaign, 1776-1777 (The U.S. Army Campaigns of the Revolutionary War)', 'author': 'Steven E. Elliott',
        'date': '2025', 'type': 'Modern secondary: Army campaign booklet, 99 pages', 'citation': 'U.S. Army Center of Military History, Washington, D.C. ISBN 978-1-959302-16-2',
        'page verified?': 'yes (PDF pages)', 'url': None,
        'rights': 'U.S. Army publication; the cover painting is credited to the Metropolitan Museum of Art. Cited, not hosted.',
        'notes': 'Supplied by Morgan as a PDF (71-45_trenton.pdf). Pages 38 to 49 (the forces, the crossing, the march and the battle) were read in full on 17 Nov 2026. '
                 'Used to check the Trenton rows: see the check column on the Positions sheet and the v10 column on Conflicts. Its Map 4 (the battle) is a picture and was not compared.',
        'used_for': 'TREN'}, like=S.max_row)
add(S, {'source_id': 'S60', 'title': 'Christmas Night, 1776: How Did They Cross?', 'author': 'William M. Welsch', 'date': '2020-12-24',
        'type': 'Modern secondary: journal article', 'citation': 'Journal of the American Revolution, 24 December 2020 (first published two years earlier)',
        'page verified?': 'n/a (web page)', 'url': 'https://allthingsliberty.com/2020/12/christmas-night-1776-how-did-they-cross/',
        'rights': 'In copyright. Cited and linked, not hosted.',
        'notes': "From the Journal's Battle of Trenton tag, named by Morgan. Read through a summarising tool. Gives the order of crossing, the times from Knox and Washington, and the boats.",
        'used_for': 'TREN'}, like=S.max_row)
add(S, {'source_id': 'S61', 'title': "The Hessians Who Escaped Washington's Trap at Trenton", 'author': 'Andrew A. Zellers-Frederick', 'date': '2018-04-18',
        'type': 'Modern secondary: journal article', 'citation': 'Journal of the American Revolution, 18 April 2018. Relies chiefly on Fischer, Washington\'s Crossing, and Stryker.',
        'page verified?': 'n/a (web page)', 'url': 'https://allthingsliberty.com/2018/04/the-hessians-who-escaped-washingtons-trap-at-trenton/',
        'rights': 'In copyright. Cited and linked, not hosted.',
        'notes': "From the Journal's Battle of Trenton tag, named by Morgan. Read through a summarising tool. Gives who escaped, by which way, and Fischer's itemised list of 368. "
                 "Two other articles under the tag (Deitch on Rall; Britton on Monroe) could not be opened from here; the rest cover the lead-up, Princeton or later memory.",
        'used_for': 'TREN'}, like=S.max_row)
for r in S.iter_rows(min_row=2):
    if r[0].value == 'S22':
        n = r[sh.index('notes')]
        n.value = ((n.value + ' ') if n.value else '') + 'Supplied again by Morgan as a PDF and read in full for the battle (pages 8 to 12) on 17 Nov 2026, alongside Elliott (S59).'

# ---------------------------------------------------------------- positions: the check, row by row
P = wb['Positions']; ph = head(P)
cj = newcol(P, 'check: Elliott (S59), S22 and JAR (S60, S61)', 60)
CHECK = {
 'T01': "Agrees: the ferrymen began taking the army over after nightfall, which came about 1600 (S59, p. 42); the troops reached the landing about 5 p.m. (S60).",
 'T02': "Agrees: the infantry were over by 0300 and the artillery an hour later (S59, p. 43). S60 has Knox's 2 a.m. for the infantry and Washington's 3 a.m. for the guns; all agree the march began about 4 a.m. See TC13.",
 'T03': "Agrees: at Jacob's Creek the gunners unharnessed and hauled the guns over a steep ravine in the early light (S59, p. 44). No clock time.",
 'T04': "Agrees: the army divided at Birmingham (S59, p. 44; S22, p. 9). S22 lists the brigades of each wing and keeps Birmingham against the Bear Tavern argument. See TC02.",
 'T05': "Distance differs: Greene's division halted 800 yards from the enemy's posts and deployed into three columns (S59, p. 46); this row has about 500 yards from the editors of Washington's papers.",
 'T06': "Agrees: twenty-four soldiers in a cooper's shop guarded the Pennington Road (S59, p. 44); a corporal and 24 men under Wiederhold, about half a mile out (S61). See TC10.",
 'T08': "Agrees: a company of jaegers guarded the River Road at the Hermitage, Dickinson's house (S59, p. 44); about 50 under Lt. von Grothausen (S61). See TC03.",
 'T09': "Agrees: the jaegers tried to re-form near the barracks and fired a volley before fleeing over the Assunpink with twenty dragoons (S59, p. 45).",
 'T10': "Agrees: Rall also posted guards on the Princeton Road (S59, p. 44). No strength given.",
 'T11': "Time differs: S61, citing Fischer, has Sgt. Müller's 18 men hold the bridge for over an hour so that musicians, surgeons and families could get away. This row ends at 08:27, when Sullivan holds the bridge (T56). See TC16.",
 'T13': "Strength: about 100 (S61); Fischer's list 150 (in S61). See TC07.",
 'T17': "Agrees: the dragoons crossed the bridge at the first alarm and got away to Princeton (S59, p. 45; S61).",
 'T19': "Agrees: shortly before eight the advance of Greene's division came on the Pennington Road picket, fired three volleys, and Wiederhold fell back to Altenbockum's company (S22, p. 10). S59 has both columns at their starting points around 0800 (p. 45); S61 says about 7:30. See TC01.",
 'T20': "Agrees: Wiederhold was nearly surrounded and fell back to Altenbockum's company (S22, p. 10).",
 'T21': "Agrees, as for T20 (S22, p. 10).",
 'T22': "Agrees: Flahaven's party drove the Hermitage post back, pressed by Glover's brigade (S22, p. 10). S59 has Stark's New Hampshire men and forty New Jersey recruits, with four guns, at the head of the column (p. 45).",
 'T23': "Agrees: the jaegers fell back through the lower town toward the barracks and over the bridge (S59, p. 45). Shown reaching the bridge at 08:14 (was 08:02), so the 1.8 km is covered at a run.",
 'T55': "Agrees: Sullivan's column reached its starting point a mile west of the town centre around 0800 (S59, p. 45). S22 has Sullivan's gun heard before Greene's attack opened (p. 10).",
 'T56': "Agrees: Sullivan's men took the barracks and made for the bridge; Glover's and St. Clair's brigades went through the lower town to the bridges (S59, pp. 45, 47).",
 'T24': "Agrees: Forrest's six guns swept Queen Street from where the Battle Monument stands (S22, p. 11); Knox's artillery unlimbered on the high ground at the head of King and Queen Streets (S59, p. 46).",
 'T25': "Agrees: Hamilton's New York company fired down King Street (S22, p. 11).",
 'T26': "Agrees: Washington on the high ground at today's Princeton Avenue (S22, p. 11); near the guns, from where he could watch the attack (S59, p. 46).",
 'T57': "Agrees in general (S59, p. 46).",
 'T27': "Agrees: Stirling's brigade in reserve (S59, p. 46).",
 'T28': "Differs: S59 puts Stephen's brigade in the centre of Greene's three columns, Mercer to the west and de Fermoy to the east (p. 46). S22 sends Hand's riflemen with Scott's and Lawson's battalions (Stephen's Virginians) through the fields on the left to the Princeton road (p. 11); this row follows S22. See TC14.",
 'T29': "Agrees: de Fermoy's brigade on the east, to cut the Princeton road (S59, pp. 46-47); Hand's riflemen to the Princeton road (S22, p. 11).",
 'T59': "Agrees in place: Washington ordered Hand's and Haussegger's regiments of de Fermoy's brigade to extend the line east, which stopped Rall's first counter-attack from the orchard (S59, p. 47).",
 'T30': "Agrees: Mercer's brigade got into the houses and fired from cover (S59, p. 47; S22, p. 11).",
 'T31': "Agrees: the Rall and Lossberg regiments tried to form along King and Queen Streets (S59, p. 46). Which regiment was in which street is not said. See TC11.",
 'T32': "Agrees, as for T31 (S59, p. 46).",
 'T34': "Agrees: two 3-pounders came into action at the north end of King Street and were abandoned under Knox's fire (S59, p. 46).",
 'T35': "Partly: S59 has the Germans briefly retake their guns and Stirling's brigade take them back, Lt. James Monroe of the 3d Virginia being wounded (p. 47). This row gives the taking to William Washington's party, as Stryker does. See TC12.",
 'T36': "Agrees: reinforcements from Stirling's brigade (S59, p. 47).",
 'T37': "Partly: S59 has the two regiments withdraw east to the orchard and counter-attack first northward toward the Princeton road, then westward into the town (p. 47); S22 has them fall back to the low ground called The Swamp, between Stockton and Montgomery Streets north of Perry (p. 12). See TC08 and TC15.",
 'T38': "Partly, as for T37.",
 'T61': "Agrees: the Knyphausen regiment stayed in the south of the town and took no part in the attack from the orchard (S59, p. 48).",
 'T39': "Order differs: S22 has Rall shot from his horse on Queen Street in front of Isaac Yard's house during the attack (p. 12), which this row follows. S59 has him mortally wounded just after ordering the retreat to the orchard, after the second counter-attack failed (p. 47). See TC15.",
 'T40': "As for T39.",
 'T41': "Agrees: Lt. Col. Scheffer surrendered the two regiments (S59, p. 47); in the orchard, with Maj. von Hanstein, to one of Washington's aides, probably Baylor (S22, p. 12).",
 'T42': "Agrees, as for T41.",
 'T43': "Not in S59 or S22: S22 has an aide, probably Baylor, receive the surrender (p. 12). This row follows Stryker (S21).",
 'T46': "Agrees: Stark's men led Sullivan's column (S59, p. 45).",
 'T47': "Agrees: two 6-pounders and two 3-pounders went with Stark (S59, p. 45). The batteries are not named.",
 'T48': "Agrees in general: Glover's brigade at the bridges (S59, p. 47).",
 'T49': "Agrees: St. Clair's brigade at the bridges (S59, p. 47).",
 'T50': "Agrees: Dechow found the bridge held too firmly and the regiment went north and east along the creek looking for a ford (S59, p. 48); S22 has Sullivan block the bridge with infantry and guns (pp. 11-12).",
 'T51': "Time and place: S59 has the regiment lay down its arms a quarter mile from the other two, shortly after them, with only fifty men getting over the creek (p. 48). S61 has about 50 ford it under Biesenrodt's officers. See TC05.",
 'T53': "Agrees: a tidal ice jam below the falls stopped Ewing opposite the South Trenton Ferry (S59, p. 48).",
 'T54': "Agrees: Cadwalader gave up opposite Burlington, tried again at Dunk's Ferry six miles down, landed about 600 infantry but no guns, and recalled them after three hours (S59, pp. 48-49).",
}
seen = set()
for r in P.iter_rows(min_row=2):
    if r[1].value == 'ARW-TP' and r[0].value in CHECK: P.cell(r[0].row, cj).value = CHECK[r[0].value]; seen.add(r[0].value)
    if r[1].value == 'ARW-TP' and r[0].value == 'T23':
        r[ph.index('show_from')].value = D + '08:14'
        addsrc(r[ph.index('source_ids')], 'S59')
assert seen == set(CHECK), set(CHECK) - seen

# ---------------------------------------------------------------- conflicts
C = wb['Conflicts']; ch = head(C)
vj = newcol(C, 'v10 check: Elliott (S59), S22, JAR (S60, S61)', 70)
V10 = {
 'TC01': "S59: both columns reached their starting points around 0800 (p. 45). S22: shortly before eight o'clock (p. 10). S61: about 7:30. The range 07:30 to 08:00 stands.",
 'TC02': "S59 and S22 both divide the army at Birmingham; S22 weighs the Bear Tavern argument and keeps Birmingham (pp. 8-9). This one could be closed.",
 'TC03': "S59: a company of jaegers at the Hermitage (p. 44). S61: about 50 under Lt. von Grothausen. Both lean to the whole company, not Stryker's smaller figure.",
 'TC04': "S59: the battle lasted only an hour (p. 48).",
 'TC05': "S59: the Knyphausen regiment laid down its arms shortly after the other two (p. 48). With S33 that is two modern accounts against Stryker's hour.",
 'TC06': "S59: 1,382 effectives on 26 December (Rall 512, Knyphausen 429, Lossberg 345, 50 jaegers, 20 dragoons, six guns); 22 killed, 83 badly wounded and 896 surrendered (pp. 41, 48). S61: Fischer's itemised list of those who escaped totals 368.",
 'TC07': "S61: about 100 at Crosswicks; Fischer's list gives 150.",
 'TC08': "S59: east to the orchard, then a counter-attack north toward the Princeton road, then one west into the town, then the retreat to the orchard (p. 47). S22: to The Swamp, between Stockton and Montgomery Streets north of Perry, then a bayonet attack, then the orchard (p. 12).",
 'TC09': "S59: none killed; two officers and two privates wounded; an unknown number died of exposure on the night march (p. 48).",
 'TC10': "Pennington road: twenty-four soldiers (S59, p. 44); a corporal and 24 men (S61).",
 'TC11': "S59: the Rall and Lossberg regiments tried to form along King and Queen Streets (p. 46), without saying which was where.",
 'TC12': "S59: reinforcements from Stirling's brigade retook the guns, and Monroe of the 3d Virginia was wounded there (p. 47).",
}
for r in C.iter_rows(min_row=2):
    if r[0].value in V10: C.cell(r[0].row, vj).value = V10[r[0].value]
like = [r[0].row for r in C.iter_rows(min_row=2) if r[0].value == 'TC12'][0]
NEW = [
 ('TC13', 'When was the crossing complete?',
  "S60: Knox put the infantry over by about 2 a.m. and Washington the artillery by about 3 a.m. | S59: the infantry by 0300 and the artillery an hour later (p. 43) | S61: all over by about 4 a.m. | S22: four o'clock (p. 8). All agree the march began about 4 a.m.",
  'Event TE03 now holds 02:00 to 04:00.'),
 ('TC14', "Where was Stephen's brigade in Greene's attack?",
  "S59: in the centre of the three columns, Mercer to the west and de Fermoy to the east (p. 46). | S22: Hand's riflemen and Scott's and Lawson's battalions (Stephen's Virginians) ran through the fields on the left to the Princeton road (p. 11).",
  'Row T28 keeps S22: Stephen toward the Princeton road, low confidence.'),
 ('TC15', 'Where and when was Rall shot?',
  "S22: shot from his horse on Queen Street in front of Isaac Yard's house during the attack from The Swamp (p. 12). | S59: mortally wounded just after ordering the retreat to the orchard, when the second counter-attack had failed (p. 47).",
  'Row T39 keeps S22 and Stryker: shot on Queen Street.'),
 ('TC16', 'How long did the bridge guard hold?',
  "S61, citing Fischer: Sgt. Müller's 18 men held the Assunpink bridge for over an hour. | S59: Sullivan's men took the barracks and headed for the bridge; Glover's and St. Clair's brigades reached the bridges (pp. 45, 47).",
  'Row T11 ends at 08:27, when Sullivan holds the bridge (T56).'),
 ('TC17', 'How strong was the von Lossberg regiment?',
  'S21: 467 men and 16 officers. | S59: 345 soldiers (p. 41).', 'Both figures on the assignment record; none chosen.'),
]
for cid, q, says, how in NEW:
    add(C, {'conflict_id': cid, 'battle_id': 'TREN', 'question': q, 'what the sources say': says, 'how the pilot handled it': how, 'status': 'Open'}, like=like)

# ---------------------------------------------------------------- events
E = wb['Events']; eh = head(E); col = lambda n: eh.index(n)
ev = {r[0].value: r for r in E.iter_rows(min_row=2) if r[1].value == 'ARW-TP'}


def setev(eid, **kw):
    for k, v in kw.items(): ev[eid][col(k)].value = v


setev('TE03', time_earliest=D + '02:00', time_latest=D + '04:00',
      summary="The last troops and guns reach the New Jersey bank, about three hours late. Knox had the infantry over by about 2 a.m.; the Army's campaign history has 3 a.m., with the guns an hour later.")
addsrc(ev['TE03'][col('source_ids')], 'S59', 'S60')
addsrc(ev['TE04'][col('source_ids')], 'S59', 'S60', 'S22')
addsrc(ev['TE05'][col('source_ids')], 'S59')
addsrc(ev['TE06'][col('source_ids')], 'S59', 'S22')
addsrc(ev['TE09'][col('source_ids')], 'S59')
setev('TE12', summary="Lt. Col. Scheffer surrenders the Rall and von Lossberg regiments in the orchard east of the town.")
addsrc(ev['TE12'][col('source_ids')], 'S59')
setev('TE13', summary="The Knyphausen regiment, cut off from the bridge, surrenders by the Assunpink a quarter mile away, shortly after the others. About fifty men get over the creek.")
addsrc(ev['TE13'][col('source_ids')], 'S59', 'S61')
add(E, {'event_id': 'TE15', 'campaign_id': 'ARW-TP', 'battle_id': 'TREN', 'time_earliest': D + '08:05', 'time_latest': D + '08:25', 'name': 'Escape over the bridge',
        'summary': "The jägers and the twenty British dragoons get away over the Assunpink bridge before Sullivan's men reach it.",
        'pos_ids': 'T23', 'source_ids': 'S59; S61', 'timeline': 'dot', 'playback_at': D + '08:15'}, like=ev['TE13'][0].row)

# ---------------------------------------------------------------- units and assignments
A = wb['Assignments']; ah = head(A); ac = lambda n: ah.index(n)
STR = {'T-US-STIR': '673 (S59)', 'T-US-STEPH': '549 (S59)', 'T-US-MERC': '838 (S59)', 'T-US-FERM': '638 (S59)', 'T-US-STCL': '500 (S59)',
       'T-US-GLOV': '977 (S59)', 'T-US-SARG': '827 (S59)', 'T-US-EWING': '826 Pennsylvania Associators (S59)',
       'T-US-CADW': "1,500, mostly Philadelphia Associators, with Hitchcock's 822 New England Continentals (S59)"}
for r in A.iter_rows(min_row=2):
    u = r[1].value; s = r[ac('strength / equipment')]
    if u in STR:
        s.value = (s.value + '; ' if s.value else '') + STR[u]; addsrc(r[ac('source_ids')], 'S59')
    if u == 'T-HE-RALL': r[ac('commander')].value = 'Lt. Col. Balthasar Brethauer'; s.value += '; 512 (S59)'; addsrc(r[ac('source_ids')], 'S59')
    if u == 'T-HE-LOSS': r[ac('commander')].value = 'Lt. Col. Franz Scheffer'; s.value += '; 345 (S59). See TC17'; addsrc(r[ac('source_ids')], 'S59')
    if u == 'T-HE-KNYP': s.value += '; 429 effectives (S59)'; addsrc(r[ac('source_ids')], 'S59')
    if u == 'T-HE-BDE': s.value += '; 1,382 effectives (S59)'; addsrc(r[ac('source_ids')], 'S59')
    if u == 'T-HE-JAG': s.value += '; about 50 under Lt. von Grothausen (S61)'; addsrc(r[ac('source_ids')], 'S61')

# ---------------------------------------------------------------- gaps
G = wb['Gaps']; gh = head(G); gj = gh.index('v9 update') + 1
for r in G.iter_rows(min_row=2):
    if r[0].value == 'TG03': G.cell(r[0].row, gj).value = '17 Nov 2026: brigade strengths are now from Elliott (S59), on the assignment records. Regiments are still missing.'
    if r[0].value == 'TG07': G.cell(r[0].row, gj).value = '17 Nov 2026: Elliott (S59) gives only 0300, 0800 and "an hour" for the battle; the 1929 history (S22) gives none inside the battle. Unchanged.'
    if r[0].value == 'TG09': G.cell(r[0].row, gj).value = "17 Nov 2026: S61 now says who got away and by which way (bridge, ford, Crosswicks road). The routes are still not drawn."
like = [r[0].row for r in G.iter_rows(min_row=2) if r[0].value == 'TG11'][0]
add(G, {'gap_id': 'TG12', 'battle_id': 'TREN', 'gap': "Elliott's battle map is not compared",
        'effect on the data': "Elliott's Map 4 (the battle of Trenton) is a picture. Only the booklet's text was read, so where it draws each brigade has not been set against the workbook.",
        'how to close it': 'Look at the map page of the PDF and compare it with the rows, as for the Wiederhold sketch.'}, like=like)

# ---------------------------------------------------------------- tracks: the two wings come out of the army column; brigades march the whole way
T = wb['Tracks']; th = head(T); tc = lambda n: th.index(n)
GREENE_WAY = 'RT01; RT02; RT03; RT05; RT06'; SULL_WAY = 'RT01; RT02; RT04; RT07'
drop = None
for r in T.iter_rows(min_row=2):
    if r[0].value != 'trenton': continue
    t = r[1].value
    if t == 'T-US-ARMY': drop = r[0].row; continue
    if t == 'T-US-GREENE': r[tc('rows')].value = 'T01; T02; T03; T04; T05; T19; T57'
    if t == 'T-US-SULL': r[tc('rows')].value = 'T01; T02; T03; T04; T55; T56'
    if r[tc('starts_from_row')].value == 'T19':
        r[tc('starts_from_row')].value = 'T02'; r[tc('starts_at')].value = D + '04:00'; r[tc('start_route')].value = GREENE_WAY
    elif r[tc('starts_from_row')].value == 'T55':
        r[tc('starts_from_row')].value = 'T02'; r[tc('starts_at')].value = D + '04:05'; r[tc('start_route')].value = SULL_WAY
    if t == 'T-US-ADVF':
        r[tc('starts_from_row')].value = 'T02'; r[tc('starts_at')].value = D + '04:05'; r[tc('start_route')].value = 'RT01; RT02; RT04'; r[tc('start_route_points')].value = 11
        r[tc('hide_after_last_row')].value = 'yes'
assert drop
T.delete_rows(drop, 1)

# ---------------------------------------------------------------- playback settings
PS = wb['Playback settings']
FDESC = [r[3].value for r in PS.iter_rows(min_row=2) if r[0].value == 'gettysburg' and r[1].value == 'formations.echelon'][0]
SAT = {r[1].value: (r[2].value, r[3].value) for r in PS.iter_rows(min_row=2) if r[0].value == 'gettysburg' and str(r[1].value).startswith('bases.3.')}
last = {}
for r in PS.iter_rows(min_row=2): last[r[0].value] = r[0].row


def setting(pb, key, val, desc):
    for r in PS.iter_rows(min_row=2):
        if r[0].value == pb and r[1].value == key: r[2].value = val; return
    PS.insert_rows(last[pb] + 1, 1); j = last[pb] + 1
    for k in list(last):
        if last[k] > last[pb]: last[k] += 1
    for c in range(1, 5):
        src = PS.cell(last[pb], c)
        if src.has_style: PS.cell(j, c)._style = copy.copy(src._style)
    PS.cell(j, 1).value = pb; PS.cell(j, 2).value = key; PS.cell(j, 3).value = val; PS.cell(j, 4).value = desc; last[pb] = j


for k, (v, d) in SAT.items():
    if k == 'bases.3.clip': continue
    setting('trenton', k.replace('bases.3.', 'bases.4.'), v, d)
setting('trenton', 'bases.4.title', 'Aerial photography of the ground today, from the USGS (M switches maps)', SAT['bases.3.title'][1])
for k, v in (('echelon', 'division'), ('below', 0.3), ('label', 'Divisions'), ('on', 'False')): setting('trenton', 'formations.' + k, v, FDESC)
setting('trenton', 'about.6', "The current map is the US Geological Survey's topographic map, and Satellite its aerial photography, both streamed from the USGS. "
        "If they cannot be reached, a simplified drawing of OpenStreetMap streets is shown instead.", None)
setting('trenton', 'about.7', "Before Birmingham the army marches as one column, drawn as Greene's and Sullivan's divisions side by side; the brigades are drawn along their division's road the whole way. "
        "Where each brigade was in the column is not recorded. Formations, in the Layers menu, draws the brigades as their division when zoomed out.", 'A paragraph under "About this prototype"')

ADESC = ('Units that come into the battle after it opens are drawn coming up the day before they are first placed: out of their parent formation if it is on the map, '
         'otherwise from `km` behind their own lines (towards the point `<side>.lat, lon`, or along `<side>.bearing`, degrees from north). The approach is marked as not recorded.')
for k, v in (('arrival.lead', 1), ('arrival.km', 10), ('arrival.AL.lat', 50.838691), ('arrival.AL.lon', 2.713852), ('arrival.GE.bearing', 90)): setting('ypres', k, v, ADESC)
for k, v in (('echelon', 'corps'), ('below', 0.045), ('label', 'Corps'), ('on', 'False')):
    setting('ypres', 'formations.' + k, v, FDESC.replace('the brigades of each division are drawn as the division', 'the units of each formation are drawn as the formation'))
setting('ypres', 'about.7', "A unit that joins the battle after 18 October is drawn coming up the day before: out of its corps if the corps is on the map, otherwise from about 10 km behind its own side's lines. "
        "Its approach is not in the sources read. Formations, in the Layers menu, draws divisions as their corps when zoomed out.", 'A paragraph under "About this prototype"')
# Ypres's current map is now the OpenTopoMap tiles, with the drawing as the fallback
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'ypres' and r[1].value == 'about.5':
        r[2].value = ("The current map is OpenTopoMap, a topographic map drawn from OpenStreetMap, with 1914 spellings in brackets when you zoom in. "
                      "If it cannot be reached, a simplified drawing of today's roads, canals and villages is shown instead; its woods and the old Ypres-Comines canal are approximate.")

# ---------------------------------------------------------------- read me
R = wb['Read me']
merged = [str(x) for x in R.merged_cells.ranges]; heights = {k: v.height for k, v in R.row_dimensions.items() if v.height}
for x in merged: R.unmerge_cells(x)
R.insert_rows(4, 5)
for x in merged:
    a, b = x.split(':'); ra, rb = int(a[1:]), int(b[1:]); sh = 5 if ra >= 4 else 0
    R.merge_cells('%s%d:%s%d' % (a[0], ra + sh, b[0], rb + sh))
for k in sorted(heights, reverse=True):
    if k >= 4: R.row_dimensions[k + 5].height = heights[k]
for k in range(4, 9): R.merge_cells('A%d:D%d' % (k, k)); R.row_dimensions[k].height = None
R.row_dimensions[5].height = 72; R.row_dimensions[6].height = 58; R.row_dimensions[7].height = 72
for i, txt in enumerate(['What changed on 17 November 2026 (later): Trenton checked against Elliott; Trenton and Ypres playbacks',
                         "Trenton was checked against The New Jersey Campaign, 1776-1777 by Steven E. Elliott (U.S. Army Center of Military History; source S59), the 1929 History of Trenton (S22, read again in full) "
                         "and two Journal of the American Revolution articles (S60 on the crossing, S61 on the Hessians who escaped). 46 Trenton rows now say in the new column \"check: Elliott (S59), S22 and JAR (S60, S61)\" whether the sources agree. "
                         "The v10 column on Conflicts adds what they say to TC01 to TC12, and TC13 to TC17 are new.",
                         "What the check changed in the data: the crossing now ends between 2 and 4 a.m. (TE03); the jäger picket reaches the bridge at 08:14, not 08:02; one event was added (the escape over the bridge); "
                         "two Hessian commanders and nine American brigade strengths come from Elliott. No position was moved: where the books disagree (Stephen's brigade, where Rall fell) the rows keep the 1929 history and Stryker and the disagreement is a conflict.",
                         "Playbacks: at Trenton the army marches as Greene's and Sullivan's divisions, which part at Birmingham, and every brigade marches from the ferry instead of appearing in the town; a Satellite map and a Formations view were added. "
                         "At Ypres a unit that joins after the first day is drawn coming up, out of its corps or from behind its own lines, and a Formations view (corps) was added. On Tracks, start_route can now name several routes in order."]):
    c = R.cell(4 + i, 1); src = R.cell(9 if i == 0 else 10, 1)
    if src.has_style: c._style = copy.copy(src._style)
    c.value = txt
wb.save(WB)
print('checked rows', len(CHECK))
