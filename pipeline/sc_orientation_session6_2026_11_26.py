"""26 Nov 2026, Session 6 of claude/sc-orientation-prompt.md: the fixes from the audit (claude/sc-orientation-session6-audit.md), all of
parts A and B, as Morgan approved them on 26 Nov 2026. Safe to run again: every cell is set, not appended twice.

What the audit found, read again in McCrady (S131, S132; printed pages of the Internet Archive text), his own tables (vol. 1, pp. 850-851,
the actions of 1780; vol. 2, Appendix B, pp. 743-750, every action in the state), Gibbes's 1853 volume (Marion to Horry, 27 Aug 1780,
no. 20, pp. 11-12) and the ABT copy of Marion to Gates, 29 Aug 1780:
  A1 Beaufort: Maitland's garrison was ordered to Savannah after the French fleet was seen on 4 Sep 1779 and reached it before the truce
     ran out (vol. 1, pp. 403-406); the town is contested from mid-September 1779 and British again from June 1780.
  A2 Six settled clashes still said 'PROPOSED' or 'Needs Opus' in text the player shows; rewritten to the settled readings.
  A3 Cheraw: Greene's letter and McCrady (vol. 2, p. 15) put his camp on the east bank, 'nearly opposite Cheraw Hill': inferred, medium.
  A4 Ninety Six's British row was linked to the Cowpens event; unlinked, like the other posts dated June 1780.
  B5 Rugeley's and Hammond's Store are not in the vol. 1 table; their days are in vol. 2, Appendix B (4 Dec, 30 Dec 1780).
  B6 Great Savannah: the 'British account' of the 24th had no source and is dropped; Morgan (26 Nov 2026): the date stays in dispute.
  B7 Musgrove Mill: McCrady's narrative gives 18 Aug, his two tables 19 Aug: medium.
  B8 Tearcoat Swamp: McCrady's tables put it in September 1780; recorded as SCH18, 25 Oct kept.
  B9 Black Mingo: McCrady's 'about the 14th of September' is p. 748.
  B10 Port Royal Island and Tamassee: McCrady's other days recorded (same month). Alexander's Old Field already said McCrady gives no day.
  B11 Fort Johnson 1780: the basis reworded (McCrady says only 'the remains of Fort Johnson').
  B12 Esseneca: McCrady's chapter heading and Appendix B read the other way; recorded, Morgan's choice kept.

Run: python3 pipeline/sc_orientation_session6_2026_11_26.py, then python3 tools/export_battles.py.
"""
import os
import openpyxl
from openpyxl.styles import Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
TODAY = '2026-11-26'
WHO = 'Claude (Opus), Session 6 audit, by SR-19; Morgan to confirm'
REVIEW = 'Audited by Opus (Session 6, 26 Nov 2026); Morgan to review'
APPB = 'McCrady, vol. 2, Appendix B, pp. 745-746'
TAB1 = "McCrady's table of 1780, vol. 1, p. 851"


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
    return ws.cell(r, h.index(col) + 1).value if r else None


def ids(*parts):
    out = []
    for p in parts:
        for s in str(p or '').replace(',', ';').split(';'):
            s = s.strip()
            if s and s not in out: out.append(s)
    return '; '.join(out)


def note(old, new):
    old = old or ''
    return old if new in old else (old + (' ' if old else '') + new)


wb = openpyxl.load_workbook(WAR)
CL, CT, HY, SU = wb['Clashes'], wb['Control'], wb['Hypotheses'], wb['Summaries']

# ---------------------------------------------------------------- A2 and B: clash text ------------------------------------------------------
clashes = {
    'SCC10': dict(notes="Settled: Morgan's choice (25 Nov 2026), the only black symbol; see SCH02. McCrady (vol. 1, pp. 196-197): Williamson was "
                        "ambushed about two in the morning of 1 Aug in Essenecca town; Salvador was shot and scalped; the Indians lost one killed and "
                        "three wounded, Williamson three dead of wounds and fourteen badly hurt, and his object of overtaking Cameron was defeated. "
                        "He names the Indians only; the SC Encyclopedia names Cameron's Loyalists with them. McCrady's own chapter heading reads "
                        "'Indians defeated', and his Appendix B (vol. 2) lists the action under Williamson: the American reading is kept as the other."),
    'SCC11': dict(result="Pickens's ring holds until relief; the Cherokee flee and Tamassee is burned",
                  notes="Settled for the Patriots; see SCH03. McCrady (vol. 1, p. 197): on 12 Aug Williamson attacked and defeated a large body of "
                        "Indians, 16 Indian dead against 6 killed and 17 wounded, and in this expedition burned Tomassy; he does not name Pickens or "
                        "the Ring Fight. His Appendix B (vol. 2) dates the Tomassy action 11 Aug 1776, his narrative the 12th. ABT's 'inconclusive' "
                        "stays as the other reading."),
    'SCC13': dict(notes="Cross-checked: ABT American Victory (casualties not re-read), NPS timeline (Moultrie defeated a British detachment), SC "
                        "Encyclopedia entry. McCrady has Moultrie cross on 2 Feb 1779 (vol. 1, p. 339) and dates the action 12 Feb in his Appendix B "
                        "(vol. 2); 3 Feb is kept from the Archives list and NPS. All three are February, so the map does not change."),
    'SCC15': dict(result="Lincoln's attack on the rear guard repulsed",
                  notes="Settled: a British success; see SCH04. McCrady (vol. 1, pp. 388-390): Lincoln ordered the retreat after nearly an hour, "
                        "'despairing of accomplishing his object'; the British post was soon evacuated and the army fell back to Beaufort (p. 392). "
                        "Casualties (Wikipedia): Americans 34 killed, 113 wounded, 155 missing; British 26 killed, 93 wounded, 1 missing. The NPS "
                        "'inconclusive' stays as the other reading."),
    'SCC22': dict(result="Sumter's attack fails; he withdraws"),
    'SCC24': dict(result="Heavy losses on both sides; Sumter leaves the field",
                  notes="Settled for the Americans; see SCH07. McCrady (vol. 1, pp. 626-631): the Loyalist camp was routed but the British square "
                        "not taken; the Americans plundered the camp and withdrew unpursued, which cost Sumter 'the full fruits' of the attack (p. 628). "
                        "Drawn for the Americans, as ABT and Sumter's own report score it; the NPS reading stays as the other. Casualties (ABT): "
                        "Americans 53, British 200; Sumter's own letter gives other figures."),
    'SCC28': dict(overall_confidence='medium',
                  other_reading="Same result, two dates: 18 Aug (NPS, the Archives list, Wikipedia's infobox, McCrady's narrative) against 19 Aug "
                                "(ABT, Wikipedia's lead, and McCrady's own tables: %s; %s)." % (TAB1, APPB),
                  notes="Loyalists 63 killed and 70 captured; Patriots 4 killed and 12 wounded (wayside, via Wikipedia). Edgar pp. 130-38; Buchanan "
                        "pp. 177-179. Date dagger only. McCrady's narrative (vol. 1, pp. 688-689): the party set out just before sundown on 17 Aug, "
                        "rode all night and arrived near dawn, so 18 Aug; his two tables say 19 Aug, so the day is medium. Both are August."),
    'SCC29': dict(other_reading="Same result, three days. 20 Aug: Marion to Peter Horry, Lynch's Creek, 27 Aug 1780, 'On the 20th instant' "
                                "(Gibbes 1853, no. 20, pp. 11-12), and McCrady's tables (%s; %s). 21 Aug: McCrady's narrative (vol. 1, p. 699), "
                                "the approach on the night of the 20th and the attack the next morning. 25 Aug: Marion to Gates, Port's Ferry, 29 Aug "
                                "1780, 'the 25th. Instant'. ABT: '20 or 25' August." % (TAB1, APPB),
                  notes="THE DATE IS STILL IN DISPUTE (Morgan, 26 Nov 2026). Drawn on 25 Aug, the day in Marion's report to Gates, until a source "
                        "settles it; his earlier letter, to Horry two days before, says the 20th. Every reading is August, so the map does not "
                        "change. A 'British account' of the prisoners halting at Sumter's house on the 24th, given before as a reason for the 25th, "
                        "had no source and is dropped (Session 6 audit)."),
    'SCC31': dict(other_reading="Same result, three dates: 28 Sep (NPS timeline, Wikipedia's infobox), 29 Sep (Wikipedia's body, citing Crawford), "
                                "and 'about the 14th of September' (McCrady, vol. 1, p. 748, following James's memoir; 14 Sep also in %s and %s)."
                                % (TAB1, APPB)),
    'SCC33': dict(disputed='yes', other_won_by='US', hypothesis_id='SCH18', other_source_ids='S131; S132',
                  other_reading="Same result, another month: McCrady's table of 1780 (vol. 1, p. 851) dates 'Tarcote' 14 Sep 1780 and his Appendix B "
                                "(vol. 2, pp. 745-746) September 1780; his narrative (vol. 1, pp. 751-752) gives no day and puts it after Black Mingo.",
                  notes="Cross-checked: NPS (Marion routed Tynes), ABT (American Victory; 43 casualties, all Loyalist), carolana (6 killed, 14 "
                        "wounded, 23 captured), HMdb. Boatner places it near where US 301 crosses the Black River. Date dagger: 25 Oct 1780 kept "
                        "(the Archives list, NPS, ABT); McCrady's September follows James and cites no report (SCH18)."),
    'SCC36': dict(notes="4 Dec 1780: %s, ABT and the Liberty Trail. McCrady's narrative (vol. 2, pp. 12-13) gives no day: the news came in "
                        "Greene's first hours of command. (Corrected 26 Nov 2026: the vol. 1 table cited before does not list Rugeley's.)" % APPB,
                  source_ids=ids(get(CL, 'SCC36', 'source_ids'), 'S132')),
    'SCC37': dict(notes="Settled: grey, Morgan's choice (25 Nov 2026); see SCH09. The British were Major McLeroth's 64th Foot, not Loyalists "
                        "(McCrady, vol. 2, p. 101: 'Major McLeroth, of the Sixty-fourth Regiment'). Date kept at 12-13 Dec 1780 (the Archives list, "
                        "NPS, the marker): McCrady's February follows James, not a report."),
    'SCC38': dict(other_reading="Same result, another day: McCrady's narrative gives the 29th (vol. 2, p. 27); his vol. 2, p. 24 reads 'the 3d of "
                                "December', which looks like a slip for the 30th.",
                  notes="Cross-checked: NPS (Washington's dragoons; Loyalists suffered 150 casualties), Wikipedia (Maurer p. 283; O'Neall p. 537; "
                        "Walker p. 94). No Patriot dead. 30 Dec 1780 kept: ABT, Wikipedia, the Archives list and McCrady's own %s agree, and Morgan "
                        "reported to Greene from the Pacolet on 31 Dec. (Corrected 26 Nov 2026: the vol. 1 table cited before for '20 Dec' does not "
                        "list Hammond's Store.)" % APPB),
}
for k, v in clashes.items():
    v['review_status'] = REVIEW
    put(CL, k, v, create=False)

# ---------------------------------------------------------------- A1, A3, A4, B11: control -----------------------------------------------------
put(CT, 'SCP08-2', dict(basis="After Stono the British fall back to Beaufort and Prevost leaves a post there under Maitland (McCrady, vol. 1, pp. 391-392)",
                        source_ids='S131', review_status=REVIEW), create=False)
put(CT, 'SCP08-3', dict(cplace_id='SCP08', **{'from': '1779-09-15'}, held_by='contested',
                        basis="Maitland is ordered from Beaufort to Savannah after d'Estaing's fleet is seen on 4 Sep 1779 and reaches it, by boat through "
                              "the marshes, before the truce runs out (McCrady, vol. 1, pp. 403-406); no source read puts the town under either side "
                              "afterwards. The day he left was not read: drawn mid-month",
                        event_id=None, method='inferred', confidence='low', source_ids='S131', review_status=REVIEW))
put(CT, 'SCP08-4', dict(cplace_id='SCP08', **{'from': '1780-06-01'}, held_by='CR',
                        basis="A British base after the fall of Charleston (AMH vol. 1, p. 92); the day it was occupied was not read",
                        event_id=None, method='inferred', confidence='low', source_ids='S87', review_status=REVIEW))
put(CT, 'SCP17-4', dict(method='inferred', confidence='medium',
                        basis="Greene writes from 'Camp at the Cheraws on the east side of Pedee' on 28 Dec 1780 (S137); his army marched from Charlotte "
                              "on 20 Dec and camped on the east side of the Pee Dee 'nearly opposite Cheraw Hill' (McCrady, vol. 2, p. 15). The sources "
                              "place his camp, not a garrison in the village: inferred",
                        review_status=REVIEW), create=False)
put(CT, 'SCP05-2', dict(event_id=None, review_status=REVIEW), create=False)
put(CT, 'SCP02-3', dict(basis="The fleet passes Fort Moultrie and anchors near 'the remains of Fort Johnson' on James Island (McCrady, vol. 1, p. 460); "
                              "he says only that the fort was a ruin, not who held it or from when. Drawn British from then, low",
                        review_status=REVIEW), create=False)

# ---------------------------------------------------------------- B: hypotheses -----------------------------------------------------------
def hyp(k, hist, **v):
    v.update(reviewed_on=TODAY, history=note(get(HY, k, 'history'), hist))
    put(HY, k, v, create=False)


hyp('SCH02', 'Audited 26 Nov 2026 (Session 6): McCrady\'s chapter heading ("Indians defeated") and his Appendix B (vol. 2) read the other way; recorded, Morgan\'s choice kept.',
    evidence_for="ABT: Williamson's men were hit by musket fire, Hammond's men counter-attacked with sabres, Pickens arrived and the "
                 "Cherokee-Loyalist force retreated; the Patriots burned the town. McCrady's chapter heading (vol. 1, ch. IX) reads 'Indians "
                 "defeated', and his Appendix B (vol. 2) lists Essenecca among Williamson's actions.",
    source_ids=ids(get(HY, 'SCH02', 'source_ids'), 'S132'))
hyp('SCH08', 'Audited 26 Nov 2026 (Session 6): McCrady\'s two tables give 19 Aug; confidence lowered to medium.',
    reading_b="19 Aug 1780 (ABT; Wikipedia lead; McCrady's own tables: %s, and %s)" % (TAB1, APPB),
    adopted_because="McCrady's narrative, vol. 1, pp. 688-689: the party set out just before sundown on 17 Aug, rode all night and arrived near "
                    "dawn. His two tables say 19 Aug, so the day is medium; both are August.",
    confidence='medium', source_ids=ids(get(HY, 'SCH08', 'source_ids'), 'S132'))
hyp('SCH14', 'Audited 26 Nov 2026 (Session 6): McCrady page corrected to p. 748; his tables also give 14 Sep.',
    reading_c="About 14 Sep 1780 (McCrady, vol. 1, p. 748, following James; 14 Sep also in %s and %s)" % (TAB1, APPB),
    adopted_because="The attack came about midnight. McCrady, vol. 1, p. 748, says 'about the 14th of September', following James, and his "
                    "tables repeat it; recorded, not followed, because he cites no report for the day.",
    source_ids=ids(get(HY, 'SCH14', 'source_ids'), 'S132'))
hyp('SCH15', 'Audited 26 Nov 2026 (Session 6): the unsourced British account dropped; Morgan: the date stays in dispute, 25 Aug drawn for now.',
    reading_a="25 Aug 1780 (Marion to Gates, Port's Ferry, 29 Aug 1780: 'the 25th. Instant')",
    reading_b="21 Aug 1780 (McCrady's narrative, vol. 1, p. 699: the approach on the night of the 20th, the attack next morning)",
    reading_c="20 Aug 1780 (Marion to Horry, Lynch's Creek, 27 Aug 1780: 'On the 20th instant', Gibbes 1853, no. 20, pp. 11-12; %s; %s; ABT's "
              "lead date)" % (TAB1, APPB),
    evidence_for="The 25th is the day in Marion's report to his commander.",
    evidence_against="Marion's letter to Horry is two days earlier and says the 20th; McCrady's narrative and both his tables follow the 20th "
                     "or the morning after.",
    adopted_reading='None settled: 25 Aug 1780 drawn for now; the date is still in dispute',
    adopted_because="Marion's own two letters disagree and no other report read settles the day. Morgan (26 Nov 2026): keep it marked as in "
                    "dispute. The 'British account' of the prisoners' halt on the 24th, given before as a reason, had no source and is dropped. "
                    "Every reading is August, so the map does not change.",
    confidence='low', status='Open', decided_by='Morgan (26 Nov 2026): left in dispute', decided_on=TODAY,
    next_step='Find a third report of the day (a British return, Gates\'s papers, or a scholarly study citing them); cross-check against Ward, ch. 68.',
    source_ids=ids(get(HY, 'SCH15', 'source_ids'), 'S132'))
hyp('SCH16', "Audited 26 Nov 2026 (Session 6): the table is McCrady's vol. 2, Appendix B, not the vol. 1 table (which does not list Rugeley's).",
    reading_a="4 Dec 1780 (%s; ABT; the Liberty Trail)" % APPB,
    adopted_because="McCrady's Appendix B and two later accounts agree; his narrative (vol. 2, pp. 12-13) gives no day. The others are recorded.",
    source_ids=ids(get(HY, 'SCH16', 'source_ids'), 'S132'))
hyp('SCH17', "Audited 26 Nov 2026 (Session 6): reading c ('20 Dec, McCrady's table') dropped: the vol. 1 table does not list Hammond's Store; his Appendix B gives 30 Dec.",
    reading_a="30 Dec 1780 (ABT, Wikipedia, the Archives list, %s)" % APPB,
    reading_b="29 Dec (McCrady's narrative, vol. 2, p. 27)", reading_c=None,
    adopted_because="McCrady's own Appendix B agrees with the other three sources; his narrative's 29th (p. 27) and 'the 3d of December' (p. 24, "
                    "which looks like a slip) are recorded.",
    source_ids=ids(get(HY, 'SCH17', 'source_ids'), 'S132'))
put(HY, 'SCH18', dict(battle_id=None, question='Tearcoat Swamp, 1780: 25-26 Oct or September?',
                      reading_a='25 Oct 1780, at midnight (the Archives list, NPS timeline, ABT)',
                      reading_b="September 1780 (McCrady's table of 1780, vol. 1, p. 851: 14 Sep; his Appendix B, vol. 2, pp. 745-746: Sept. 1780)",
                      reading_c=None,
                      evidence_for="Three sources agree on 25 Oct.",
                      evidence_against="McCrady's two tables put it in September; his narrative (vol. 1, pp. 751-752) gives no day and puts it after "
                                       "Black Mingo, as James does.",
                      adopted_reading='25 Oct 1780 (reading a)',
                      adopted_because="McCrady's September follows James's memoir and cites no report (as at Black Mingo and Halfway Swamp); "
                                      "the other three agree.",
                      confidence='high', status='Proposed', decided_by=WHO, decided_on=TODAY, reviewed_on=TODAY, rows='T33',
                      source_ids='S116; S118; S120; S131; S132', next_step='Morgan to confirm; cross-check against Ward, ch. 68.',
                      history='New on 26 Nov 2026 (Session 6 audit).'))

# ---------------------------------------------------------------- A1: the 1779 year summary ---------------------------------------------------
sh = head(SU)
for r in range(2, SU.max_row + 1):
    row = {h: SU.cell(r, i + 1).value for i, h in enumerate(sh)}
    if row['playback_id'] == 'sc-orientation' and row['kind'] == 'year' and row['from'] == '1779-01-01':
        SU.cell(r, sh.index('text') + 1, "Moultrie beats Gardiner's detachment on Port Royal Island in February. In May Prevost reaches the "
                "Charleston lines and draws off when Lincoln hurries back. On 20 June Lincoln's attack on the rear guard at Stono Ferry is "
                "repulsed, and the British fall back to Beaufort. In September Maitland's garrison leaves Beaufort to defend Savannah against "
                "the French and Americans, and the town is left to no one.")
        SU.cell(r, sh.index('how written') + 1, 'Written by Claude (Opus) from the rows, 25 Nov 2026 (Session 3, redone); last sentence added 26 Nov 2026 (Session 6 audit)')
wb.save(WAR)

# ---------------------------------------------------------------- sources -------------------------------------------------------------------
sb = openpyxl.load_workbook(SHARED); SO = sb['Sources']
put(SO, 'S131', dict(notes=note(get(SO, 'S131', 'notes'), "Re-read 26 Nov 2026 (Session 6 audit) at every page cited, and the table of the actions of "
                                "1780 (pp. 850-851), which runs to Long Cane, 11 Dec 1780.")), create=False)
put(SO, 'S132', dict(notes=note(get(SO, 'S132', 'notes'), "Re-read 26 Nov 2026 (Session 6 audit), with Appendix B (pp. 743-750), a table of every "
                                "action in the state with date, county and commanders.")), create=False)
put(SO, 'S133', dict(citation="Marion to Horatio Gates, Port's Ferry, 29 Aug 1780 (ABT primary-source page); Marion to Peter Horry, Lynch's Creek, "
                              "27 Aug 1780 (Gibbes, Documentary History of the American Revolution ... in 1781 and 1782, Columbia, 1853, no. 20, pp. 11-12).",
                     notes=note(get(SO, 'S133', 'notes'), "Both read again 26 Nov 2026 (Session 6 audit): to Gates, 'the 25th. Instant'; to Horry, "
                                "'On the 20th instant'. Gibbes read in the Internet Archive text (documentaryhist04gibbgoog).")), create=False)
sb.save(SHARED)
print('done')
