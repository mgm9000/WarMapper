"""27 Nov 2026: gap SCG06 closed. Ward, The War of the Revolution, vol. 2, chs. 67-73 and notes (S92), cross-checked with the CMH
chronology (Coakley and Conn 1975, new S148), Stedman vol. II (new S149), Burke Davis 1962 (new S150), the Cowpens staff ride's letters
appendix (S95, appendix D), Seymour's journal (S100), Tarleton (S97) and McCrady vol. 2 (S132). The full findings are in the WarMapper
Project doc claude/scg06-ward-crosscheck.md. Morgan approved the changes on 27 Nov 2026. Safe to run again: every cell is set, and every
appended sentence is added only if it is not there already.

What changes on the map or in the text the player shows:
  A1 Hammond's Store: 30 Dec 1780, about 12:00, settled by Morgan's report to Greene of 31 Dec 1780 (printed in S95, pp. 164-165):
     Washington was sent off on the 29th and came up with the Loyalists 'next day, about twelve o'clock'. SCH17 high; Ward's 28 Dec
     (counted from the day the news came) and Seymour's 31 Dec (the follow-up at Fort Williams) recorded as rejected readings.
  A2 Cheraw: Greene's camp from 26 Dec 1780 (Greene to Morgan, 29 Dec 1780, S95 p. 163: 'We arrived here the 26th inst.').
  A3 Cowpens, CH06: Ward puts Tate on Howard's right and Triplett on his left (from Johnson, Schenck and Lossing). Recorded under
     reading B. Confidence stays medium (not lowered as first proposed): reading A rests on Howard's own statement (S98), a report,
     and Ward cites no report (SR-20).
  A4 Georgetown, 24-25 Jan 1781: renamed 'Georgetown raid' (Lee's memoir via Ward p. 753, n. 23; CMH p. 126; Davis).
  Tearcoat Swamp: drawn as the night of 25-26 Oct 1780 (CMH p. 124 gives 26 Oct), as Black Mingo is drawn.
  Guilford, GCE14: the event text now says the grapeshot story is disputed (GH08).
  GH11 (new): which Virginia brigade stood north of the road in the second line. Data kept (Lawson north); Ward and Davis recorded.

Run: python3 pipeline/scg06_ward_crosscheck_2026_11_27.py, then python3 tools/export_battles.py, then python3 tools/build.py.
"""
import os
import openpyxl
from openpyxl.styles import Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
TODAY = '2026-11-27'
WHO = 'Claude (Opus), SCG06 cross-check, 27 Nov 2026; approved by Morgan'
REVIEW = 'Cross-checked by Opus (SCG06, 27 Nov 2026); approved by Morgan'
WARD = 'Ward (S92)'
CMH = 'CMH chronology (S148)'


def head(ws): return [c.value for c in ws[1]]


def find(ws, key):
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == key: return r
    return None


def put(ws, key, values, create=True):
    h = head(ws); r = find(ws, key)
    if r is None:
        if not create: raise KeyError(key)
        r = ws.max_row + 1; ws.cell(r, 1, key)
    for k, v in values.items():
        assert k in h, '%s: no column %s' % (ws.title, k)
        c = ws.cell(r, h.index(k) + 1, v); c.alignment = Alignment(wrap_text=True, vertical='top')
    return r


def get(ws, key, col):
    r = find(ws, key); h = head(ws)
    assert r, '%s: no row %s' % (ws.title, key)
    return ws.cell(r, h.index(col) + 1).value


def ids(*parts):
    out = []
    for p in parts:
        for s in str(p or '').replace(',', ';').split(';'):
            s = s.strip()
            if s and s not in out: out.append(s)
    return '; '.join(out)


def add(old, new, sep='\n'):
    old = old or ''
    return old if new in old else (old + (sep if old else '') + new)


def extend(ws, key, src=(), **cols):
    """Append a sentence to each named text column of a row, and add source ids."""
    v = {c: add(get(ws, key, c), t, ' ' if c in ('notes', 'basis', 'history', 'summary') else '\n') for c, t in cols.items()}
    if src: v['source_ids'] = ids(get(ws, key, 'source_ids'), *src)
    put(ws, key, v, create=False)


wb = openpyxl.load_workbook(WAR)
HY, CL, CT, EV, UN = wb['Hypotheses'], wb['Clashes'], wb['Control'], wb['Events'], wb['Units']

# ---------------------------------------------------------------- A1 Hammond's Store ------------------------------------------------------
put(HY, 'SCH17', dict(
    reading_a="30 Dec 1780, about 12:00 (Morgan to Greene, Camp on Pacolet, 31 Dec 1780, printed in S95, pp. 164-165: Washington sent on "
              "the 29th, came up with them 'next day, about twelve o'clock, at Hammond's store-house, forty miles from our camp'; ABT, "
              "Wikipedia, the Archives list, McCrady, vol. 2, Appendix B, pp. 745-746)",
    reading_b="29 Dec (McCrady's narrative, vol. 2, p. 27)",
    reading_c="28 Dec (Ward, vol. 2, p. 752, by count of days; CMH chronology p. 125)",
    evidence_for="Morgan's report, written the day after the news came in, gives the 29th for Washington's start and the next day for the "
                 "fight; Morgan to Greene, 4 Jan 1781 (S95, p. 166), and Greene's reply of 8 Jan acknowledge it.",
    evidence_against="Ward counts 'two days after his arrival at the Pacolet' (25 Dec) and 'the next day', which gives 28 Dec, but Morgan's "
                     "letter shows the 27th was the day the news of the Loyalists came, not the day Washington left (Ward's note 21 cites "
                     "Gordon, G. W. Greene and Seymour, not Morgan's letter). CMH gives 28 Dec without a source. Seymour's journal (PMHB 7, "
                     "1883, p. 293) has Washington detached on 31 Dec 'to Fort William': that is the follow-up at Fort Williams, which "
                     "Morgan's letter of 4 Jan describes separately.",
    adopted_reading='30 Dec 1780, about 12:00 (reading a)',
    adopted_because="Settled by Morgan's own report (SR-20). The 28th and 31st are explained above and rejected; the 29th is McCrady's "
                    "narrative and 'the 3d of December' (vol. 2, p. 24) a slip.",
    confidence='high', status='Decided', decided_by='Morgan (27 Nov 2026), on Morgan to Greene, 31 Dec 1780', decided_on=TODAY,
    reviewed_on=TODAY, next_step='None.',
    source_ids=ids(get(HY, 'SCH17', 'source_ids'), 'S95', 'S92', 'S148', 'S100'),
    history=add(get(HY, 'SCH17', 'history'), "Settled 27 Nov 2026 (SCG06 cross-check): Morgan's report of 31 Dec 1780 in the staff ride's "
                "appendix D gives 30 Dec, about noon; Ward's 28 Dec and Seymour's 31 Dec recorded and rejected; confidence high.", ' ')),
    create=False)
put(CL, 'SCC38', dict(
    captured="Morgan reported to Greene on 31 Dec: 150 killed and wounded and about 40 taken, 'without the loss of a man' (S95, pp. 164-165)",
    other_reading="Same result, another day: McCrady's narrative gives the 29th (vol. 2, p. 27); Ward (vol. 2, p. 752) and the CMH chronology "
                  "(p. 125) give 28 Dec, counting from the day the news came; Seymour's journal gives 31 Dec, the follow-up at Fort Williams.",
    other_source_ids='S132; S92; S148; S100',
    overall_confidence='high',
    source_ids=ids(get(CL, 'SCC38', 'source_ids'), 'S95'),
    notes=add(get(CL, 'SCC38', 'notes'), "Settled 27 Nov 2026: Morgan to Greene, Camp on Pacolet, 31 Dec 1780 (printed in S95, pp. 164-165): "
              "Washington left on the 29th and struck 'next day, about twelve o'clock', 40 miles from Morgan's camp (SCH17).", ' '),
    review_status=REVIEW), create=False)
put(EV, 'SCE38', dict(source_ids=ids(get(EV, 'SCE38', 'source_ids'), 'S95')), create=False)

# ---------------------------------------------------------------- A2 Cheraw ----------------------------------------------------------------
put(CT, 'SCP17-4', dict(
    **{'from': '1780-12-26'},
    basis="Greene to Morgan, 'Camp on the Cheraws, on the east side of the Pedee', 29 Dec 1780: 'We arrived here the 26th inst.' (printed in "
          "S95, p. 163); Cornwallis to Tarleton, 26 Dec, has Greene marching on 'Wednesday last', 20 Dec (S95, p. 173); Ward, vol. 2, "
          "p. 752, and Greene's letter of 28 Dec (S137) agree. The camp was on the east side of the Pee Dee, 'nearly opposite Cheraw Hill' "
          "(McCrady, vol. 2, p. 15): the sources place his camp, not a garrison in the village, so inferred.",
    method='inferred', confidence='medium', source_ids=ids('S95', get(CT, 'SCP17-4', 'source_ids'), 'S92'),
    notes=add(get(CT, 'SCP17-4', 'notes'), 'Date moved from 28 Dec to 26 Dec on 27 Nov 2026 (SCG06 cross-check): 28 Dec was the date of a letter '
              'written in the camp, not the day of arrival.', ' '),
    review_status=REVIEW), create=False)

# ---------------------------------------------------------------- A3 Cowpens CH06 ----------------------------------------------------------
extend(HY, 'CH06', src=('S92', 'S150'),
       evidence_against="S92 Ward, vol. 2, p. 757 and his map on p. 759: Tate's Virginia militia and a small Georgia company on Howard's right, "
                        "Triplett's Virginians on his left (his note 10 cites Johnson, Schenck and Lossing, not a participant).",
       evidence_for="S150 Davis, p. 23: Triplett and Tate in the main line, flanks not given; Beatty's Georgians on its outer right.",
       history="Cross-checked 27 Nov 2026 (SCG06): Ward recorded under reading B; confidence kept at medium because reading A rests on "
               "Howard's own statement (S98) and Ward cites no report.")
put(UN, 'C-US-TRIP', dict(notes=add(get(UN, 'C-US-TRIP', 'notes'), "Ward (S92, p. 757) splits them: Tate on Howard's right, Triplett on his "
                                    "left; recorded under CH06.", ' ')), create=False)

# ---------------------------------------------------------------- A4 Georgetown ------------------------------------------------------------
put(EV, 'SCE40', dict(name='Georgetown raid',
                      summary="Marion and Lee surprise the garrison and take its commander, but without guns they cannot break into the "
                              "post, and withdraw. [T40]",
                      source_ids=ids(get(EV, 'SCE40', 'source_ids'), 'S92', 'S148', 'S150')), create=False)

# ---------------------------------------------------------------- Tearcoat Swamp: the night of 25-26 Oct -------------------------------------
put(EV, 'SCE33', dict(time_latest='1780-10-26', source_ids=ids(get(EV, 'SCE33', 'source_ids'), 'S148')), create=False)
put(CL, 'SCC33', dict(
    notes=add(get(CL, 'SCC33', 'notes'), "The CMH chronology (S148, p. 124) gives 26 Oct; the attack came at midnight, so it is drawn as the "
              "night of 25-26 Oct 1780 (27 Nov 2026), as Black Mingo is.", ' '),
    review_status=REVIEW), create=False)
extend(HY, 'SCH18', src=('S148',),
       evidence_for="S148 CMH chronology, p. 124: 26 Oct 1780 (a third source for October against McCrady's September).",
       history="27 Nov 2026 (SCG06): CMH added; drawn as the night of 25-26 Oct.")
put(HY, 'SCH18', dict(adopted_reading='The night of 25-26 Oct 1780 (reading a)'), create=False)

# ---------------------------------------------------------------- second sources for the South Carolina rows ----------------------------------
SC = {
    'SCH04': "S148 CMH chronology, p. 117: 20 Jun 1779; 1,200 Patriots attacked the British and Hessian rearguard, losing more than 300 to 130.",
    'SCH05': "S148 CMH chronology, p. 119: Clinton's expedition landed on Simmons Island, 10-11 Feb 1780; p. 120: the siege began on 1 Apr; "
             "surrender 12 May. (Its narrative, p. 70, says Johns Island.)",
    'SCH06': "S148 CMH chronology, p. 122: Rocky Mount on 1 Aug 1780 (a second source for 1 Aug).",
    'SCH07': "S148 CMH chronology, p. 122: Hanging Rock, 6 Aug 1780; the Loyalist garrison defeated, nearly 200 lost to 53.",
    'SCH08': "S148 CMH chronology, p. 123: 18 Aug 1780, an ambuscade two miles from Musgrove's Mill on the north bank of the Enoree.",
    'SCH09': "S148 CMH chronology, p. 125: Halfway Swamp, 12-13 Dec 1780, 'with inconclusive results'.",
    'SCH12': "S148 CMH chronology, pp. 122-123: 15 Aug 1780, the post guarding Wateree Ferry and its 30 men.",
    'SCH13': "S148 CMH chronology, p. 125: Tarleton's 270 defeated by Sumter on the south bank of the Tyger. S92 Ward, vol. 2, p. 747: "
             "Americans 3 killed and 4 wounded; Tarleton admitted 51; his claim rested on Sumter's withdrawal across the Tyger.",
    'SCH14': "S148 CMH chronology, p. 124: 29 Sep 1780.",
    'SCH16': "S148 CMH chronology, p. 125: 4 Dec 1780.",
}
for k, t in SC.items():
    extend(HY, k, src=('S148', 'S92') if k == 'SCH13' else ('S148',), evidence_for=t,
           history='27 Nov 2026 (SCG06): CMH chronology added as a further source.')
extend(HY, 'SCH15', src=('S148',), evidence_against="S148 CMH chronology, p. 123: 20 Aug 1780 (one more source for reading c; it cites no "
       "report, so the day stays open).", history='27 Nov 2026 (SCG06): CMH recorded under reading c; still open.')
extend(CL, 'SCC28', notes="To check (27 Nov 2026): the CMH chronology (S148, p. 123) puts the ambush two miles from the mill on the north bank "
       "of the Enoree; confirm this point is the ambush ground, not the mill (gap SCG05).")
put(CT, 'SCP03-2', dict(source_ids=ids(get(CT, 'SCP03-2', 'source_ids'), 'S148')), create=False)
for e in ('SCE13', 'SCE14', 'SCE15', 'SCE16', 'SCE17', 'SCE18', 'SCE19', 'SCE21', 'SCE22', 'SCE24', 'SCE25', 'SCE26', 'SCE27', 'SCE28',
          'SCE29', 'SCE30', 'SCE31', 'SCE32', 'SCE34', 'SCE35', 'SCE36', 'SCE37', 'SCE38', 'SCE39'):
    put(EV, e, dict(source_ids=ids(get(EV, e, 'source_ids'), 'S148')), create=False)

# ---------------------------------------------------------------- Cowpens hypotheses ---------------------------------------------------------
COW = {
    'CH01': ('evidence_against', ('S92', 'S149', 'S150'),
             "S92 Ward, vol. 2, p. 758: up at 03:00 and five hours on the march before sighting the Americans (his note 12: Stedman); p. 764: "
             "'the battle was not over until about ten o'clock' (note 3: Johnson). S149 Stedman, vol. II, p. 320: 'came in sight of the enemy "
             "about eight in the morning' (he was not there). McCrady, vol. 2, pp. 41, 43, follows him. S150 Davis, p. 25: the scouts came in "
             "'just before eight o'clock'. None of these was present; reading A rests on the eyewitnesses above."),
    'CH02': ('evidence_against', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 760: the main lines fought for 'nearly half an hour'; p. 764: over 'about ten o'clock'. S150 Davis, p. 40: "
             "'little more than an hour'."),
    'CH03': ('evidence_against', ('S92', 'S148', 'S132', 'S100'),
             "Reading B's figures are sums of parts, not counts: S92 Ward, vol. 2, p. 755: about 1,040; S148 CMH, p. 126: about 1,025; McCrady, "
             "vol. 2, p. 31: the parts from Greene's letter, and Johnson's 970 and 910. For reading A: S100 Seymour: 'not eight hundred'; "
             "Morgan to Greene, 15 Jan 1781 (S95, p. 170): 200 South Carolina and Georgia and 140 North Carolina volunteers, two-thirds of "
             "them likely to fight."),
    'CH05': ('evidence_for', ('S150',),
             "S150 Davis, p. 23: McDowell on the right of Pickens's line; Cunningham's Georgians on the left of the skirmish line."),
    'CH08': ('evidence_for', ('S150',),
             "S150 Davis, p. 35: Morgan rode 'about fifty paces, according to his later memory'."),
    'CH10': ('evidence_for', ('S92', 'S150'),
             "S92 Ward, vol. 2, pp. 760-761, and S150 Davis, pp. 32-33: Washington and McCall rout the dragoons riding down the militia, then "
             "take the British flank at the bayonet charge."),
    'CH11': ('evidence_against', ('S92',),
             "S92 Ward, vol. 2, p. 761: 'Pickens's riflemen, having made a complete circuit of the field', came up on the right; McArthur "
             "surrendered to Pickens (leans to reading B)."),
    'CH12': ('evidence_for', ('S92', 'S150'),
             "S92 Ward, vol. 2, pp. 761-762, and S150 Davis, p. 39: a sergeant parries, a fourteen-year-old bugler fires, Tarleton wounds "
             "Washington's horse."),
    'CH14': ('evidence_against', ('S92',),
             "S92 Ward, vol. 2, p. 758: the line was hardly formed before Tarleton opened with the guns (leans to reading B). Tarleton himself "
             "(S97, p. 216): 'The disposition being completed, the front line received orders to advance'."),
    'CH15': ('evidence_for', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 758 and map p. 759; S150 Davis, pp. 29-30 (the reserve 150 yards behind, left of the 7th)."),
    'CH16': ('evidence_against', ('S150',),
             "S150 Davis, p. 29: Tarleton formed 'some 400 to 500 yards from the enemy', then advanced to 300 yards (reading B)."),
    'CH17': ('evidence_against', ('S150',),
             "S150 Davis, p. 32: 'A Captain Ogilvie, who led the dragoon party on the right flank of Tarleton' (reading B)."),
}
for k, (col, src, t) in COW.items():
    extend(HY, k, src=src, **{col: t}, history='27 Nov 2026 (SCG06): Ward, Davis and others recorded; the adopted reading is unchanged.')
extend(UN, 'C-BR-RA1', notes="Ward's text (S92, p. 758) has the guns in the centre and on the left; his own map (p. 759) has them in the gaps "
       "either side of the Legion, as drawn.")
extend(UN, 'C-US-MCD', notes="Ward calls him Joseph on p. 752 and 'Major Charles McDowell' on p. 757.")

# ---------------------------------------------------------------- Guilford ----------------------------------------------------------------
GUI = {
    'GH01': ('evidence_against', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 787: the British column seen 'about midday' (note 9: Lossing), half an hour's cannonade, and the advance "
             "'about half-past one' (reading B). S150 Davis, p. 151: 'almost 1:30 p.m. when the first of the enemy appeared' (later still)."),
    'GH04': ('evidence_against', ('S92', 'S150'),
             "S92 Ward's map, vol. 2, p. 789: Butler north of the road, Eaton south. S150 Davis, pp. 148-149: 'General Eaton on the left and "
             "General Butler on the right'. Both older narratives; Babits and Howard (2009) not yet read."),
    'GH05': ('evidence_for', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 786, and S150 Davis, p. 150: on the courthouse hill, north of the road; Huger's Virginians on the right, "
             "the Marylanders by the road."),
    'GH06': ('evidence_for', ('S92', 'S148'),
             "S92 Ward, vol. 2, p. 784: 'over 4,400 rank and file'. S148 CMH, p. 127: about 4,500, of them 2,800 militia."),
    'GH07': ('evidence_against', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 787: Macleod pushed three guns forward in the opening duel. S150 Davis, p. 161: Macleod's 'twin "
             "three-pounders' fired the grape."),
    'GH08': ('evidence_for', ('S92', 'S150'),
             "S92 Ward, vol. 2, p. 792: Cornwallis ordered grape into the melee; 'it is said' O'Hara begged him not to. S150 Davis, p. 161: "
             "Macleod and the wounded O'Hara both begged him to hold his fire; he was 'adamant'. Both older narratives."),
    'GH09': ('evidence_for', ('S92',),
             "S92 Ward, vol. 2, p. 786: about 300 yards, then about 550 (note 8: Schenck)."),
    'GH10': ('evidence_against', ('S92',),
             "S92 Ward, vol. 2, p. 785: Lee met Tarleton 'three or four miles from Guilford'."),
}
for k, (col, src, t) in GUI.items():
    extend(HY, k, src=src, **{col: t}, history='27 Nov 2026 (SCG06): Ward, Davis and CMH recorded; the adopted reading is unchanged.')
for k in ('GH04', 'GH08'):
    put(HY, k, dict(next_step='Read Babits and Howard, Long, Obstinate, and Bloody (2009), the study the newer sources follow; the older '
                              'narratives (Ward 1952, Davis 1962) read the other way.'), create=False)
put(HY, 'GH11', dict(
    battle_id='GUIL', question='Which Virginia brigade stood north of the road in the second line?',
    reading_a='Lawson north of the road, Stevens south',
    reading_b='Stevens north (on the American right), Lawson south',
    reading_c=None,
    evidence_for="S144 p. 95: Lawson's regiments (Randolph, Holcombe, Skipwith) right to left north of the road; p. 98: Stevens's (Stuart, "
                 "Moffett, Cocke, Perkins) south of it.",
    evidence_against="S92 Ward, vol. 2, p. 789 (map) and p. 790: Webster, on the British left (north), strikes 'Stevens's men, the American "
                     "right wing of that line' (but the same page has the rest of Stevens's brigade holding Leslie, south of the road). "
                     "S150 Davis, p. 149: 'Stevens commanded on the right of this line and Lawson on the left'.",
    adopted_reading='Lawson north, Stevens south (reading a), as drawn',
    adopted_because='The staff ride follows the newer study (Babits and Howard); Ward contradicts himself, and neither older narrative cites a '
                    'report for the placing. Not settled.',
    confidence='low', status='Open', decided_by=WHO, decided_on=TODAY, reviewed_on=TODAY, rows='G-US-LAWS; G-US-STEV',
    source_ids='S144; S92; S150',
    next_step='Read Babits and Howard, Long, Obstinate, and Bloody (2009), and the Virginia officers\' letters (St. George Tucker).',
    history='New on 27 Nov 2026 (SCG06 cross-check).'))
put(EV, 'GCE14', dict(summary=add(get(EV, 'GCE14', 'summary'), "Whether he fired knowingly into his own Guards, over O'Hara's protest, is "
                                  "disputed (GH08).", ' ')), create=False)
extend(UN, 'G-US-2MD', notes="Ward (S92, p. 784) calls it the 5th Maryland; Davis (S150) and the newer studies the 2nd.")
extend(UN, 'G-US-EATON', notes="Ward (S92, pp. 783-784) calls him 'Pinketham Eaton'; Davis (S150) and Hatch (S138) Thomas Eaton.")
extend(UN, 'G-US-LAWS', notes="Which side of the road: GH11.")
extend(UN, 'G-US-STEV', notes="Which side of the road: GH11.")
wb.save(WAR)

# ---------------------------------------------------------------- sources and the gap ----------------------------------------------------
sb = openpyxl.load_workbook(SHARED); SO, SCAND, GA = sb['Sources'], sb['Source candidates'], sb['Gaps']
put(SO, 'S92', dict(
    title='"Before Cowpens" to "Guilford Court House," chapters 68-73, in The War of the Revolution, volume 2',
    citation='Christopher Ward, The War of the Revolution, ed. John Richard Alden, vol. 2 (New York: Macmillan, 1952), pp. 747-794 (ch. 67 '
             'ends p. 747; ch. 68 pp. 748-754; ch. 69 pp. 755-762, map p. 759; ch. 70 pp. 763-769; ch. 71 pp. 770-776; ch. 72 pp. 777-783; '
             'ch. 73 pp. 784-794, map p. 789), notes pp. 916-920',
    **{'page verified?': 'yes: pp. 747-794 and notes pp. 916-920 read from page images Morgan supplied, 27 Nov 2026 (p. 915, ch. 68 note 1, not seen)'},
    rights='In copyright. Page images supplied by Morgan; cited by page; not hosted, not quoted at length.',
    notes="Read 27 Nov 2026 for gap SCG06 (findings: claude/scg06-ward-crosscheck.md in the WarMapper Project). Ward's notes show where he "
          "rests on reports: Morgan's December march (ch. 68 n. 19: Kirkwood, Seymour), the Georgetown raid (n. 23: Lee), the 18 Jan and "
          "6 Feb waypoints (ch. 70 n. 4, ch. 71 n. 7). Elsewhere he follows 19th-century histories (Johnson, Schenck, Lossing, G. W. "
          "Greene). Slips noted: Guilford camp 'April 14' for 14 Mar; Tarleton over the Enoree and Tyger on the 15th (14th); Lee's Legion "
          "with Greene on 13 Jan (by 8 Jan); 'Major Charles McDowell'; 'Pinketham Eaton'; '5th Maryland'.",
    used_for='course page HIST 340 (class 4); SC orientation, COWP and GUIL cross-checks (recorded in Hypotheses)',
    local_copy='not in the repository (Morgan\'s page images)'), create=False)
put(SO, 'S148', dict(
    title='The War of the American Revolution: Narrative, Chronology, and Bibliography', author='Robert W. Coakley and Stetson Conn',
    date='1975', type='Official history: narrative and Army chronology',
    citation='Robert W. Coakley and Stetson Conn, The War of the American Revolution: Narrative, Chronology, and Bibliography (Washington, '
             'D.C.: U.S. Army Center of Military History, CMH Pub 70-6-1, 1975; reprinted 2010)',
    **{'page verified?': 'yes (text layer of the PDF Morgan supplied; PDF page = printed page + 14)'},
    rights='U.S. Army publication, sold by the GPO; no rights statement read. Cited, not hosted.',
    notes="Read 27 Nov 2026 (SCG06): narrative pp. 68-76 and the chronology pp. 115-132. The chronology gives a date, strength and result for "
          "nearly every South Carolina action of 1779-1781 but cites no sources. Its narrative's Cowpens and Guilford figures are those of "
          "S85/S87, and its Cowpens losses those of Ward (from F. V. Greene): count those as one source, not two.",
    used_for='SC orientation; COWP; GUIL', kind='official history', war='ARW', rights_status='public domain (to confirm)', may_host='check',
    rights_checked=TODAY, site='history.army.mil', page_offset='PDF page = printed page + 14'))
put(SO, 'S149', dict(
    title='The History of the Origin, Progress, and Termination of the American War, vol. II', author='Charles Stedman', date='1794',
    type='Early secondary, by a British officer who served under Cornwallis (not at Cowpens)',
    citation='C. Stedman, The History of the Origin, Progress, and Termination of the American War, 2 vols. (London, 1794), vol. II, about p. 320',
    **{'page verified?': 'no: read in the Internet Archive OCR text, page markers unreliable (about p. 320)'},
    url='https://archive.org/details/historyoforiginp02sted', rights='Public domain.',
    notes="Read 27 Nov 2026 (SCG06) for Tarleton's night march to Cowpens: marched at three in the morning, 'came in sight of the enemy about "
          "eight in the morning'. The source of Ward's and McCrady's 08:00 (CH01).",
    used_for='COWP (CH01)', kind='book', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='archive.org'))
put(SO, 'S150', dict(
    title='The Cowpens-Guilford Courthouse Campaign', author='Burke Davis', date='1962',
    type='Secondary: narrative history (Great Battles of History), no notes',
    citation='Burke Davis, The Cowpens-Guilford Courthouse Campaign (Philadelphia: J. B. Lippincott, 1962)',
    **{'page verified?': 'yes (text of the scan Morgan supplied, by printed page)'},
    rights='In copyright. Cited by page; not hosted, not quoted at length.',
    notes="Read 27 Nov 2026 (SCG06): Cowpens pp. 18-48, the retreat, Guilford pp. 147-192. Quotes the eyewitnesses but gives no notes, so it "
          "adds readings and settles none (SR-20). Recorded under CH01, CH02, CH05, CH06, CH08, CH10, CH12, CH15-17, GH01, GH04, GH05, GH07, "
          "GH08 and GH11.",
    used_for='COWP; GUIL (cross-checks)', kind='book', war='ARW', rights_status='in copyright', may_host='no: link and cite',
    rights_checked=TODAY, local_copy="Morgan's PDF, not in the repository"))
put(SO, 'S95', dict(notes=add(get(SO, 'S95', 'notes'), "Read again 27 Nov 2026 (SCG06): chapter 2 (pp. 17-42), appendix B (pp. 95-120) and "
                              "appendix D, the letters of 1 Dec 1780-20 Jan 1781 (pp. 161-185): Greene to Morgan, 29 Dec ('We arrived here "
                              "the 26th inst.'); Morgan to Greene, 31 Dec (Hammond's Store, 30 Dec) and 4 Jan (Fort Williams); Greene to "
                              "Morgan, 8 Jan (Lee 'just arrived'); Morgan to Greene, 15 Jan, Burr's Mill on Thicketty Creek.", ' ')),
    create=False)
put(SO, 'S97', dict(notes=add(get(SO, 'S97', 'notes'), "Read 27 Nov 2026 (SCG06), pp. 210-216: the Enoree and Tyger passed on the 14th; "
                              "the Pacolet before daylight on the 16th; marched at three on the 17th; Thicketty Creek passed 'before dawn'.",
                              ' ')), create=False)
put(SO, 'S100', dict(notes=add(get(SO, 'S100', 'notes'), "Seymour also read 27 Nov 2026 (SCG06) in the PMHB printing (vol. 7, 1883, "
                               "pp. 292-295, through the losthistory.net transcription): Morgan's march of 21-25 Dec 1780, 58 miles; "
                               "Washington detached on 31 Dec 'to Fort William'.", ' ')), create=False)
put(SO, 'S132', dict(notes=add(get(SO, 'S132', 'notes'), "Read 27 Nov 2026 (SCG06), pp. 24, 27-31, 39, 41, 43-44, 50: Tarleton's crossings "
                               "(14 and 16 Jan), his march at three, in view about eight (following Stedman); Morgan's parts and Johnson's "
                               "totals.", ' ')), create=False)
put(SO, 'S21', dict(notes=add(get(SO, 'S21', 'notes'), "Morgan supplied the HathiTrust scan (Cornell copy, coo1.ark:/13960/t0cv52w44, 559 "
                              "PDF pages) on 27 Nov 2026; it can close TG06 (page check) and TG02 (illustration no. 55).", ' ')),
    create=False)
put(SCAND, 'SC-MAP13', dict(title='Ward, The War of the Revolution, vol. 2, chs. 68-73', holder="Morgan's page images",
                            access='Read 27 Nov 2026 from page images Morgan supplied (now S92).', status='read',
                            notes='Closed gap SCG06.'), create=False)
put(GA, 'SCG06', {'v9 update': add(get(GA, 'SCG06', 'v9 update'), "Closed 27 Nov 2026: Ward chs. 67-73 and notes read (S92), with the CMH "
                  "chronology (S148), Stedman (S149), Davis (S150) and the staff ride's letters (S95). Changes: Hammond's Store settled "
                  "30 Dec (high); Cheraw from 26 Dec; Georgetown raid; Tearcoat 25-26 Oct; GH11 opened; every reading recorded in "
                  "Hypotheses. Not covered: SCH01-SCH03.", ' ')}, create=False)
sb.save(SHARED)
print('done')
