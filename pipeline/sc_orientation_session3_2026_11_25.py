"""25 Nov 2026, Session 3 of claude/sc-orientation-prompt.md (redone the same evening: the first run's branch was never pushed).
Winners, disputed points and control for the South Carolina orientation. Safe to run again: every row is set, not appended twice.

How the readings were settled (SR-19): where the lists and web pages disagree, McCrady's History of South Carolina in the Revolution
(1901, 1902; public domain; he cites Drayton, Moultrie, Tarleton, Lee, the Sumter papers and Gibbes's documents) settles the date or
the result, or the commander's own letter does. Where McCrady follows a memoir and not the reports (Halfway Swamp, after James), the
better-sourced reading is kept and his is recorded. Morgan's own choices (25 Nov 2026) are kept as he made them: Esseneca drawn as a
Cherokee and Loyalist win (black), Halfway Swamp grey, Rocky Mount and Davie's raid on 1 Aug 1780, and the seven clashes Session 2
could not place drawn. Every other reading stays on the Hypotheses sheet. Page numbers are McCrady's printed pages, read in the
Internet Archive text of historyofsouthca00mccr (1775-1780) and historyofsouthca00mccra (1780-1783).

Run: python3 pipeline/sc_orientation_session3_2026_11_25.py, then python3 tools/export_battles.py.
"""
import json, os
import openpyxl
from openpyxl.styles import Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
TODAY = '2026-11-25'
WHO = 'Claude (Opus), Session 3 redo, by SR-19; Morgan to confirm'
REVIEW = 'Settled by Opus (SR-19); Morgan to review'


def head(ws): return [c.value for c in ws[1]]


def find(ws, key):
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value == key: return r
    return None


def put(ws, key, values, create=True):
    """Set the named columns of the row whose first cell is `key`; add the row if it is missing."""
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
    """Join source ids, keeping the order and dropping repeats."""
    out = []
    for p in parts:
        for s in str(p or '').replace(',', ';').split(';'):
            s = s.strip()
            if s and s not in out: out.append(s)
    return '; '.join(out)


def note(old, new):
    """Add a sentence to a notes cell once."""
    old = old or ''
    return old if new in old else (old + (' ' if old else '') + new)


def drop(ws, key):
    r = find(ws, key)
    if r: ws.delete_rows(r)


wb = openpyxl.load_workbook(WAR)

# ---------------------------------------------------------------- events: dates and summaries ----------------------------------------------
EV = wb['Events']
events = {
    'SCE04': dict(add='S131'),
    'SCE10': dict(summary="The Cherokee, with Loyalists under Cameron, ambush Williamson's column at Esseneca before dawn; his men break, "
                          "Hammond's charge drives the attackers off, and the town is burned. [T10]", add='S131'),
    'SCE11': dict(summary="Williamson's men beat a large Cherokee war party (Pickens's Ring Fight near Tamassee) and burn the Lower Towns. [T11]", add='S131'),
    'SCE15': dict(add='S131'),
    'SCE16': dict(playback_at='1780-05-12', add='S131'),
    'SCE17': dict(add='S131'), 'SCE18': dict(add='S131'),
    'SCE20': dict(summary="Captain John McClure's Whigs rout a Loyalist muster at Alexander's Old Field (Beckhamville). [T20]", add='S131; S122'),
    'SCE21': dict(add='S131; S122'),
    'SCE22': dict(t0='1780-08-01', t1='1780-08-01', summary="Sumter attacks Turnbull's post three times and cannot take it; he withdraws. [T22]", add='S131; S122'),
    'SCE23': dict(t0='1780-08-01', t1='1780-08-01', add='S131'),
    'SCE24': dict(add='S131'),
    'SCE26': dict(t0='1780-08-15', t1='1780-08-15', summary="Sumter's men under Colonel Taylor take Cary's redoubt at Wateree Ferry and a convoy "
                                                          "on its way from Ninety Six. [T26]", add='S131; S122'),
    'SCE28': dict(t0='1780-08-18', t1='1780-08-18', add='S131'),
    'SCE29': dict(t0='1780-08-25', t1='1780-08-25', summary="Marion surprises the guard at Sumter's Great Savannah plantation near Nelson's Ferry "
                                                          "and frees about 150 Maryland Continentals taken at Camden. [T29]", add='S131; S133'),
    'SCE30': dict(add='S122'),
    'SCE31': dict(t0='1780-09-28', t1='1780-09-29', add='S131'),
    'SCE35': dict(add='S131; S122'),
    'SCE36': dict(t0='1780-12-04', t1='1780-12-04', summary="Washington's dragoons bluff Colonel Rugeley's Loyalists out of their fortified barn at "
                                                          "Clermont with a log painted as a cannon; they surrender without a shot. [T36]", add='S131; S132; S120'),
    'SCE37': dict(t0='1780-12-12', t1='1780-12-13', summary="Marion meets Major McLeroth's detachment of the 64th Foot; McLeroth answers with a "
                                                          "challenge to a fight of twenty picked men, then slips away, and a shot is fired at Singleton's Mill the "
                                                          "next day. [T37]", add='S132; S122'),
    'SCE38': dict(t0='1780-12-30', t1='1780-12-30', add='S132'),
}
for k, e in events.items():
    v = {'source_ids': ids(get(EV, k, 'source_ids'), e.get('add'))}
    if 't0' in e: v.update(time_earliest=e['t0'], time_latest=e['t1'])
    if 'summary' in e: v['summary'] = e['summary']
    if 'playback_at' in e: v['playback_at'] = e['playback_at']
    put(EV, k, v, create=False)

# ---------------------------------------------------------------- clashes ------------------------------------------------------------------
CL = wb['Clashes']
upd = {
    'SCC04': dict(won_by='indecisive', result_method='stated', overall_confidence='high', add='S131',
                  note="McCrady (vol. 1, pp. 90-91): the Loyalists appeared on Sunday 19 Nov, the siege lasted two days, and a parley was called at "
                       "sunset on the 21st; the treaty followed the next morning. Settled: 19-21 Nov, no winner."),
    'SCC10': dict(won_by='CH', result_method='inferred', overall_confidence='medium', disputed='yes', other_won_by='US',
                  result="The ambush breaks Williamson's column before Hammond's charge drives the attackers off (Morgan's reading: a Cherokee and Loyalist win of the ambush)",
                  other_reading="ABT scores Esseneca an American victory: the Patriots rallied, drove the force off and burned the town. McCrady "
                                "(vol. 1, pp. 196-197) also has the Indians driven off and both halves of the town burned, after the ambush had put "
                                "Williamson's men to flight.",
                  other_source_ids='S120; S131', add='S131',
                  note="McCrady (vol. 1, pp. 196-197): ambushed about two in the morning of 1 Aug in Essenecca town; Salvador shot and scalped; the "
                       "Indians lost one killed and three wounded, Williamson three dead of wounds and fourteen badly hurt. He names the Indians "
                       "only; the SC Encyclopedia names Cameron's Loyalists with them. Morgan's choice (25 Nov 2026): the only black symbol."),
    'SCC11': dict(won_by='US', result_method='inferred', overall_confidence='medium', add='S131',
                  note="McCrady (vol. 1, p. 197): on 12 Aug Williamson attacked and defeated a large body of Indians, 16 Indian dead against 6 "
                       "killed and 17 wounded; he does not name Tamassee or Pickens. Settled for the Patriots; ABT's inconclusive stays as the other reading."),
    'SCC15': dict(won_by='CR', result_method='stated', overall_confidence='high', add='S131',
                  note="McCrady (vol. 1, pp. 386-390): Lincoln ordered the retreat after nearly an hour, 'despairing of accomplishing his object'; "
                       "the British then fell back to Beaufort. Settled: a British success; the NPS 'inconclusive' stays as the other reading."),
    'SCC16': dict(won_by='CR', overall_confidence='high', add='S131',
                  note="McCrady (vol. 1): landing on John's Island 11 Feb (p. 431), the Ashley crossed 29 Mar (pp. 431-432), ground broken 31 Mar "
                       "(p. 455), the garrison marched out about eleven on 12 May (p. 504). Drawn on 12 May (the event's playback_at)."),
    'SCC17': dict(add='S131', note="McCrady (vol. 1, pp. 467-468): Tarleton struck at three in the morning, about 14 Apr."),
    'SCC18': dict(add='S131', note="McCrady (vol. 1, pp. 494-495): White's cavalry routed at the ferry after Tarleton marched there on 6 May."),
    'SCC22': dict(won_by='CR', result_method='stated', overall_confidence='medium', add='S131; S122',
                  note="McCrady (vol. 1, pp. 624-625): 1 Aug; Sumter tried three times, Neel was killed, and he withdrew. The HMdb Rocky Mount "
                       "marker (228191) also gives 1 Aug. Morgan's choice (25 Nov 2026): 1 Aug for both Rocky Mount and Davie's raid."),
    'SCC23': dict(won_by='US', result_method='stated', overall_confidence='medium', add='S131',
                  note="McCrady (vol. 1, pp. 624-625): 1 Aug; Davie routed three companies near the post, took about sixty horses and a hundred "
                       "muskets, and lost no man."),
    'SCC24': dict(won_by='US', result_method='inferred', overall_confidence='medium', add='S131',
                  note="McCrady (vol. 1, pp. 626-631): the Loyalist camp was routed but the British square not taken; the Americans plundered the "
                       "camp and withdrew unpursued, which cost Sumter 'the full fruits' of the attack (p. 628). Drawn for the Americans, as ABT "
                       "and Sumter's own report score it; the NPS reading stays as the other."),
    'SCC28': dict(won_by='US', result_method='stated', overall_confidence='high', add='S131',
                  note="McCrady (vol. 1, pp. 686-698): the expedition left on the evening of 17 Aug and fought at dawn, so 18 Aug. Settled."),
    'SCC31': dict(won_by='US', result_method='stated', overall_confidence='medium', disputed='yes', other_won_by='US', hypothesis_id='SCH14',
                  other_reading="Same result, three dates: 28 Sep (NPS timeline, Wikipedia's infobox), 29 Sep (Wikipedia's body, citing Crawford), "
                                "and 'about the 14th of September' (McCrady, vol. 1, about p. 735, following James's memoir).",
                  other_source_ids='S118; S121; S131', add='S131',
                  note="The attack came about midnight, so it is drawn on the night of 28-29 Sep; McCrady's 14 Sep is recorded, not followed, "
                       "because he follows James and cites no report for the day."),
    'SCC37': dict(won_by='indecisive', result_method='inferred', overall_confidence='medium', disputed='yes', other_won_by='US',
                  result="Marion cuts off pickets and presses McLeroth's column; McLeroth answers with a challenge, then slips away; no battle",
                  other_reading="The NPS timeline scores it for Marion: he engaged a larger party, which retreated. McCrady (vol. 2, pp. 101-104, "
                                "following James) puts the encounter about the middle of February 1781 and says the British 'shouldered their muskets "
                                "and retreated' when the picked men advanced. The 2010 Clarendon County marker gives 12 Dec 1780, 'according to tradition'.",
                  other_source_ids='S118; S132; S122', add='S132; S122',
                  note="Morgan (25 Nov 2026): grey; the British were Major McLeroth's 64th Foot, not Loyalists (McCrady, vol. 2, p. 101: 'Major "
                       "McLeroth, of the Sixty-fourth Regiment'). Date kept at 12-13 Dec 1780 (the Archives list, NPS, the marker): McCrady's "
                       "February follows James, not a report."),
    'SCC38': dict(won_by='US', result_method='stated', overall_confidence='medium', disputed='yes', other_won_by='US', hypothesis_id='SCH17',
                  other_reading="Same result, other days: McCrady gives 20 Dec in his table of 1780 (vol. 1, about p. 849) and the 29th in vol. 2 "
                                "(p. 27); his vol. 2, p. 24 reads 'the 3d of December', which looks like a slip for the 30th.",
                  other_source_ids='S131; S132', add='S132',
                  note="30 Dec 1780 kept: ABT, Wikipedia and the Archives list agree, and Morgan reported to Greene from the Pacolet on 31 Dec."),
}
for k, u in upd.items():
    v = {c: u[c] for c in ('won_by', 'result_method', 'overall_confidence', 'disputed', 'other_won_by', 'result', 'other_reading',
                           'other_source_ids', 'hypothesis_id') if c in u}
    v['source_ids'] = ids(get(CL, k, 'source_ids'), u.get('add'))
    if u.get('note'): v['notes'] = note(get(CL, k, 'notes'), u['note'])
    v['review_status'] = REVIEW
    put(CL, k, v, create=False)

new_clashes = [
    dict(clash_id='SCC20', event_id='SCE20', kind='fight', won_by='US', result_method='stated', result="A Whig party routs a Loyalist muster",
         place="Alexander's Old Field (Beckhamville)", lat=34.5905, lon=-80.92, coord_source='marker', coord_precision_m=500,
         coordinate_basis="HMdb 13688, 'Alexander's Old Fields', at 34 35.43 N 80 55.2 W (S122); the 1942 Beckhamville marker (HMdb 13689) stands beside it.",
         coordinate_confidence='medium', overall_confidence='medium', source_ids='S116; S122; S131',
         notes="The marker and the Archives list give 6 Jun 1780; McCrady (vol. 1, about p. 588) calls it Beckham's Old Field and gives no day."),
    dict(clash_id='SCC21', event_id='SCE21', kind='fight', won_by='US', result_method='stated', result="Huck's detachment surprised at dawn; Huck killed",
         place="Williamson's Plantation (Huck's Defeat), Brattonsville", lat=34.86585, lon=-81.17352, coord_source='marker', coord_precision_m=300,
         coordinate_basis="HMdb 275162, the Huck's Defeat trail marker at Historic Brattonsville, 34 51.951 N 81 10.411 W (S122); the battle was on Williamson's lane beside it.",
         coordinate_confidence='medium', overall_confidence='high', source_ids='S116; S118; S131; S122',
         notes="McCrady (vol. 1, pp. 597-599): attacked at dawn on 12 Jul; Huck shot while rallying his men; the Whigs lost one man."),
    dict(clash_id='SCC26', event_id='SCE26', kind='fight', won_by='US', result_method='stated',
         result="Cary's redoubt at Wateree Ferry and the convoy from Ninety Six taken", captured="The redoubt and its garrison, and the convoy's wagons",
         captured_by='US', disputed='yes', other_won_by='US', other_reading="Same result; the ABT Fishing Creek page, as Morgan's list reads it, puts the raid on 16-17 Aug.",
         other_source_ids='S127', hypothesis_id='SCH12', place="Cary's Fort, Wateree Ferry (west bank)", lat=34.2435, lon=-80.6540,
         coord_source='derived', coord_precision_m=2000,
         coordinate_basis="HMdb 225424, 'Patriots Landing', at 34 14.608 N 80 39.241 W (S122), says Cary's Fort was about a mile downstream; drawn at the marker.",
         coordinate_confidence='low', overall_confidence='high', source_ids='S116; S118; S131; S122',
         notes="McCrady (vol. 1, p. 668): the morning of 15 Aug 1780, Taylor's men surprised the garrison and then took the convoy. Settled: 15 Aug."),
    dict(clash_id='SCC29', event_id='SCE29', kind='fight', won_by='US', result_method='stated',
         result="The guard surprised; about 150 Continental prisoners freed",
         captured="22 regulars and 2 Loyalists taken; about 150 Maryland Continentals freed (Marion to Horry, 27 Aug 1780)", captured_by='US',
         disputed='yes', other_won_by='US',
         other_reading="Same result, two days. McCrady (vol. 1, pp. 699-700) has Marion attack before day on 21 Aug, following Marion's letter to "
                       "Peter Horry of 27 Aug ('On the 20th instant'). Marion's report to Gates of 29 Aug says 'the 25th', and a British account "
                       "has the prisoners halting at Sumter's house on the night of the 24th. ABT: '20 or 25' August.",
         other_source_ids='S131; S133', hypothesis_id='SCH15', place="Great Savannah (Sumter's plantation), near Nelson's Ferry",
         lat=33.50, lon=-80.40, coord_source='derived', coord_precision_m=8000,
         coordinate_basis="Sumter's Great Savannah plantation, about six miles above Nelson's Ferry on the north side of the Santee, now in the "
                          "Santee National Wildlife Refuge (ABT); the site is not marked. Placed between the Fort Watson mound (33.5390, -80.4376, "
                          "HMdb 301930, S122) and the drowned ferry.",
         coordinate_confidence='low', overall_confidence='medium', source_ids='S118; S131; S133; S122',
         notes="Drawn on 25 Aug, Marion's own date in his report to Gates; the two letters of his disagree, so the date is medium."),
    dict(clash_id='SCC30', event_id='SCE30', kind='fight', won_by='US', result_method='stated',
         result="Barfield's Loyalist advance party, then his main body, dispersed", place="Blue Savannah, Marion County",
         lat=34.0716, lon=-79.3057, coord_source='marker', coord_precision_m=5000,
         coordinate_basis="HMdb 311842, 'Battle of Blue Savannah', at Ariel Cross Roads, 34 4.295 N 79 18.34 W (S122); the second skirmish was "
                          "about three miles north, by the Carolina bay called Blue Savannah.",
         coordinate_confidence='low', overall_confidence='medium', source_ids='S116; S118; S122',
         notes="The 1955 DAR marker (HMdb 18080) gave 13 Aug 1780; its replacement, the NPS timeline and the Archives list give 4 Sep. Not in McCrady's pages read."),
    dict(clash_id='SCC35', event_id='SCE35', kind='fight', won_by='US', result_method='stated',
         result="Tarleton's attack beaten back; Sumter badly wounded; Tarleton takes the ground the next morning",
         disputed='yes', other_won_by='CR',
         other_reading="Tarleton claimed a victory and Cornwallis accepted it; Tarleton held the field the next morning, after the Americans had "
                       "left in the night. McCrady (vol. 1, pp. 829-830) reports the claim and rejects it: Sumter's men held the field at the close.",
         other_source_ids='S131; S121', hypothesis_id='SCH13', place="Blackstock's Plantation, Tyger River",
         lat=34.689, lon=-81.818, coord_source='derived', coord_precision_m=1500,
         coordinate_basis="HMdb 11111, 'Battle of Blackstock's', at 34 38.715 N 81 49.059 W (S122), says the battle was three miles north on the "
                          "south side of the Tyger; placed three miles north of the marker.",
         coordinate_confidence='low', overall_confidence='high', source_ids='S116; S118; S121; S131; S122',
         notes="Settled for the Americans by McCrady (vol. 1, pp. 829-830), who reads both sides' reports."),
    dict(clash_id='SCC36', event_id='SCE36', kind='capture', won_by='US', result_method='stated',
         result="Rugeley's fortified barn surrenders to Washington's dragoons without a shot (the 'Quaker gun')",
         captured="Colonel Rugeley and 103 rank and file (Cornwallis, as McCrady quotes him, vol. 2, pp. 12-13)", captured_by='US',
         disputed='yes', other_won_by='US',
         other_reading="Same result, other days: the Archives list gives 1 Dec 1780 and a Journal of the American Revolution article 30 Nov.",
         other_source_ids='S116', hypothesis_id='SCH16', place="Rugeley's Mill (Clermont), north of Camden", lat=34.43, lon=-80.60,
         coord_source='derived', coord_precision_m=6000,
         coordinate_basis="Clermont, about thirteen miles north of Camden on the road to Charlotte, near the meeting of Flat Rock and Grannies "
                          "Quarter creeks (ABT; the Liberty Trail, S120); the site is not marked. Placed on that road thirteen miles north of Camden.",
         coordinate_confidence='low', overall_confidence='medium', source_ids='S131; S132; S120; S116',
         notes="4 Dec 1780: McCrady's table (vol. 1, about p. 849), ABT and the Liberty Trail."),
]
for c in new_clashes:
    k = c.pop('clash_id'); c['playback_id'] = 'sc-orientation'; c['review_status'] = REVIEW
    put(CL, k, c)

# ---------------------------------------------------------------- places and control -------------------------------------------------------
CP, CT = wb['Control places'], wb['Control']
places = [
    ('SCP08', 'Beaufort', 'town', 32.433, -80.683, 'derived', 1500, "Wikipedia's coordinate for the town (S121).", 'medium', 'S121; S131; S87', 'Today: Beaufort.'),
    ('SCP09', 'Georgetown', 'port', 33.37444, -79.29389, 'derived', 1500, "Wikipedia's coordinate for the town (S121).", 'medium', 'S121; S87; S132', 'Today: Georgetown.'),
    ('SCP10', 'Dorchester', 'village', 32.9495, -80.1719, 'marker', 300, "Colonial Dorchester State Historic Site (Wikipedia, S121); HMdb 301139 at 32 56.891 N 80 10.256 W (S122).",
     'medium', 'S121; S122; S134', 'Today: Colonial Dorchester State Historic Site (the town was abandoned after the war).'),
    ('SCP11', "Monck's Corner", 'post', 33.19667, -80.00667, 'derived', 800, "Wikipedia's coordinate for the Battle of Monck's Corner (S121).", 'medium', 'S121; S131', "Today: Moncks Corner."),
    ('SCP12', 'Orangeburg', 'village', 33.50333, -80.87222, 'derived', 1500, "Wikipedia's coordinate for the city (S121).", 'medium', 'S121; S134; S118', 'Today: Orangeburg.'),
    ('SCP13', 'Fort Granby (the Congarees)', 'fort', 33.965, -81.041, 'derived', 1000, "Wikipedia's coordinate for the former town of Granby (S121); the fort was James Cayce's house nearby.",
     'medium', 'S121; S134; S132', 'Today: Cayce (the Cayce Historical Museum has a replica, not on the site).'),
    ('SCP14', 'Fort Galphin (Silver Bluff)', 'fort', 33.35, -81.87, 'derived', 5000, "About five miles west-north-west of Jackson, SC, on a bluff over the Savannah (SC Historic Properties "
     "record S108042001100174, S134); placed from that description.", 'low', 'S134', 'Today: Silver Bluff, Aiken County. Called Fort Dreadnought by the British.'),
    ('SCP15', 'Camden', 'town', 34.23422, -80.60403, 'marker', 500, "HMdb 23390, on the British fortifications of 1780, at 34 14.053 N 80 36.242 W (S122): the town and its palisade.",
     'medium', 'S122; S131; S121', 'Today: Camden (the Historic Camden Revolutionary War Site).'),
    ('SCP16', 'Winnsboro', 'village', 34.37694, -81.08806, 'derived', 1500, "Wikipedia's coordinate for the town (S121).", 'medium', 'S121; S132', 'Today: Winnsboro.'),
    ('SCP17', 'Cheraw (the Cheraws)', 'village', 34.69389, -79.89111, 'derived', 1500, "Wikipedia's coordinate for the town (S121); Greene's camp was on the east bank just above it.",
     'medium', 'S121; S131; S137', 'Today: Cheraw.'),
    ('SCP18', 'Kingstree', 'village', 33.66639, -79.82917, 'derived', 1500, "Wikipedia's coordinate for the town (S121).", 'medium', 'S121', 'Today: Kingstree.'),
]
for (k, name, kind, lat, lon, src, prec, basis, conf, sids, notes) in places:
    put(CP, k, dict(playback_id='sc-orientation', name=name, kind=kind, lat=lat, lon=lon, coord_source=src, coord_precision_m=prec,
                    coordinate_basis=basis, coordinate_confidence=conf, source_ids=sids, notes=notes))

PATRIOT = ("Under the Patriot government from 1775 (McCrady, vol. 1, chs. I-VI); the day the town passed to it was not read", 'inferred', 'low', 'S131')
control = [
    ('SCP01-2', 'SCP01', '1780-05-12', 'CR', "Lincoln surrenders the city and army; the garrison marched out about eleven (McCrady, vol. 1, p. 504)", 'SCE16', 'stated', 'high', 'S129; S121; S131'),
    ('SCP02-3', 'SCP02', '1780-04-07', 'CR', "The fleet anchors by 'the remains of Fort Johnson' as it passes Fort Moultrie on 7-9 Apr (McCrady, vol. 1, pp. 460-461); when the British first occupied it was not read",
     'SCE16', 'inferred', 'low', 'S131'),
    ('SCP03-2', 'SCP03', '1780-05-07', 'CR', "The garrison accepts terms on 7 May (McCrady, vol. 1, pp. 491-492)", 'SCE16', 'stated', 'high', 'S121; S131'),
    ('SCP04-3', 'SCP04', '1780-06-01', 'contested', "After the fall of Charleston the backcountry posts went to the Crown or were left; no source read says which for Fort Charlotte",
     None, 'inferred', 'low', 'S131'),
    ('SCP05-2', 'SCP05', '1780-06-01', 'CR', "Balfour's post after the fall of Charleston (McCrady, vol. 1, ch. XXVI); the day it was set up was not read", None, 'inferred', 'medium', 'S131; S128'),
    ('SCP06-2', 'SCP06', '1776-08-16', 'US', "Williamson builds Fort Rutledge at Essenecca and leaves 300 men (McCrady, vol. 1, p. 198)", None, 'stated', 'high', 'S131; S130'),
    ('SCP06-4', 'SCP06', '1780-06-01', 'contested', "No source read puts the fort under either side after the fall of Charleston", None, 'inferred', 'low', 'S131'),
    ('SCP07-3', 'SCP07', '1776-08-12', 'contested', "The Lower Towns burned in Williamson's August 1776 campaign (McCrady, vol. 1, pp. 196-198); the Ring Fight near Tamassee on 12 Aug",
     'SCE11', 'inferred', 'medium', 'S131; S123; S130'),
    ('SCP08-1', 'SCP08', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP08-2', 'SCP08', '1779-06-20', 'CR', "After Stono the British fall back to Beaufort (McCrady, vol. 1, pp. 386-390); a British base after Charleston (AMH vol. 1, p. 92). "
     "Whether it stayed British through the autumn of 1779 was not read", 'SCE15', 'inferred', 'medium', 'S131; S87'),
    ('SCP09-1', 'SCP09', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP09-2', 'SCP09', '1780-06-01', 'CR', "A British base after the fall of Charleston (AMH vol. 1, p. 92); a garrison under Campbell in January 1781 (McCrady, vol. 2, p. 87); "
     "the day it was occupied was not read", None, 'inferred', 'low', 'S87; S132'),
    ('SCP10-1', 'SCP10', '1775-04-21', 'US', "Fortified by the Patriots in 1775, its garrison briefly under Francis Marion (SC State Parks, S134)", None, 'stated', 'medium', 'S134'),
    ('SCP10-2', 'SCP10', '1780-05-12', 'CR', "Occupied by British troops in April or May 1780 (the pages read differ); drawn from the surrender of the city", 'SCE16', 'inferred', 'low', 'S134'),
    ('SCP11-1', 'SCP11', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP11-2', 'SCP11', '1780-04-14', 'CR', "Tarleton surprises Huger there (McCrady, vol. 1, pp. 467-468); a British post afterwards", 'SCE17', 'inferred', 'medium', 'S131'),
    ('SCP12-1', 'SCP12', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP12-2', 'SCP12', '1780-06-01', 'CR', "A British post in 1780-81 (the 'Orangeburg Post', S134; it fell on 11 May 1781, NPS timeline); the month it was set up was not read",
     None, 'inferred', 'low', 'S134; S118'),
    ('SCP13-1', 'SCP13', '1780-06-01', 'CR', "Fortified by the British after the fall of Charleston (FortWiki and the Cayce marker, S134); Sumter attacked it on 19 Feb 1781 "
     "(McCrady, vol. 2, pp. 105-106); the month it was set up was not read", None, 'inferred', 'low', 'S134; S132'),
    ('SCP14-1', 'SCP14', '1780-06-01', 'CR', "Taken over by the British in 1780 and named Fort Dreadnought; captured by Lee's men on 21 May 1781 (FortWiki; SC Historic Properties, S134); "
     "the month was not read", None, 'inferred', 'low', 'S134'),
    ('SCP15-1', 'SCP15', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP15-2', 'SCP15', '1780-06-01', 'CR', "Lord Rawdon's headquarters after the fall of Charleston (McCrady, vol. 1, ch. XXVI); British redoubts from 1780 (HMdb 23390, S122); "
     "the day the army arrived was not read", None, 'inferred', 'medium', 'S131; S122; S121'),
    ('SCP16-1', 'SCP16', '1780-11-01', 'CR', "Cornwallis's winter camp after he fell back from Charlotte (McCrady, vol. 2, pp. 17, 26); he arrived in late October, the day was not read",
     None, 'inferred', 'low', 'S132'),
    ('SCP17-1', 'SCP17', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP17-2', 'SCP17', '1780-06-01', 'CR', "McArthur's post at the Cheraws (McCrady, vol. 1, ch. XXIX); the day it was set up was not read", None, 'inferred', 'low', 'S131'),
    ('SCP17-3', 'SCP17', '1780-07-24', 'contested', "McArthur is ordered to leave the Cheraws for Lynch's Creek about 24 Jul (McCrady, vol. 1, pp. 642-646)", None, 'inferred', 'medium', 'S131'),
    ('SCP17-4', 'SCP17', '1780-12-28', 'US', "Greene writes from 'Camp at the Cheraws on the east side of Pedee' on 28 Dec 1780 (S137); his army marched from Charlotte on 20 Dec "
     "(McCrady, vol. 2, p. 15)", None, 'stated', 'high', 'S137; S132'),
    ('SCP18-1', 'SCP18', '1775-04-21', 'US') + PATRIOT[:1] + (None,) + PATRIOT[1:],
    ('SCP18-2', 'SCP18', '1780-08-27', 'contested', "Fighting at King's Tree on 27 Aug 1780 (Wikipedia, S121); no source read puts the village under either side afterwards",
     None, 'inferred', 'low', 'S121'),
]
for (k, place, frm, held, basis, ev, meth, conf, sids) in control:
    put(CT, k, dict(cplace_id=place, **{'from': frm}, held_by=held, basis=basis, event_id=ev, method=meth, confidence=conf, source_ids=sids,
                    review_status=REVIEW))
drop(CT, 'SCP06-3'); drop(CT, 'SCP07-2')   # the 1777 cession rows: Esseneca was American from Aug 1776, Tamassee burned and contested (sourced above)

# ---------------------------------------------------------------- hypotheses ---------------------------------------------------------------
HY = wb['Hypotheses']


def settle(k, adopted, because, conf, by=WHO, status='Proposed', rc=None, add=None, nxt='Morgan to confirm; cross-check against Ward, ch. 68, when read.'):
    v = dict(adopted_reading=adopted, adopted_because=because, confidence=conf, status=status, decided_by=by, decided_on=TODAY, reviewed_on=TODAY,
             next_step=nxt, source_ids=ids(get(HY, k, 'source_ids'), add),
             history=note(get(HY, k, 'history'), 'Settled on 25 Nov 2026 (Session 3, redone in the evening): %s.' % adopted))
    if rc: v['reading_c'] = rc
    put(HY, k, v, create=False)


settle('SCH01', '19-21 Nov 1775 (reading a); no winner, a truce', "McCrady, vol. 1, pp. 90-91: the Loyalists appeared on Sunday 19 Nov, the siege lasted two days, a parley at sunset on the 21st.", 'high', add='S131')
settle('SCH02', 'A Cherokee and Loyalist win of the ambush (black)', "Morgan's choice, 25 Nov 2026. McCrady, vol. 1, pp. 196-197: the column was ambushed and fled before Hammond's charge; the town was burned after.", 'medium',
       by='Morgan (25 Nov 2026)', status='Decided', add='S131')
settle('SCH03', 'Patriot victory (reading a)', "McCrady, vol. 1, p. 197: on 12 Aug Williamson attacked and defeated a large body of Indians (16 dead against 6 killed). He does not name Tamassee or the Ring Fight.", 'medium', add='S131')
settle('SCH04', 'British victory (reading a)', "McCrady, vol. 1, pp. 386-390: Lincoln ordered the retreat after nearly an hour and failed in his object.", 'high', add='S131')
settle('SCH05', '29 Mar-12 May 1780 (reading a); the symbol lands on 12 May', "McCrady, vol. 1, pp. 431-432, 455, 504: landing 11 Feb, Ashley crossed 29 Mar, ground broken 31 Mar, surrender 12 May.", 'high', add='S131')
settle('SCH06', '1 Aug 1780 for both', "Morgan's choice, 25 Nov 2026. McCrady, vol. 1, pp. 624-625, and the Rocky Mount marker (HMdb 228191) give 1 Aug.", 'medium', by='Morgan (25 Nov 2026)', status='Decided', add='S131; S122')
settle('SCH07', 'American (reading a)', "McCrady, vol. 1, pp. 626-631: the Loyalist camp routed, the square not taken, the Americans withdrew unpursued after plundering; Sumter's report and ABT score it American.", 'medium', add='S131')
settle('SCH08', '18 Aug 1780 (reading a)', "McCrady, vol. 1, pp. 686-698: the party left on the evening of 17 Aug and fought at dawn.", 'high', add='S131')
settle('SCH09', 'Grey: no battle; 12-13 Dec 1780', "Morgan's choice, 25 Nov 2026: grey, and the British were the 64th Foot (McCrady, vol. 2, p. 101). The date stays with the Archives list, NPS and the marker; McCrady's February follows James.",
       'medium', by='Morgan (25 Nov 2026)', status='Decided', rc="About the middle of February 1781 (McCrady, vol. 2, pp. 101-104, following James)", add='S132; S122')
settle('SCH12', '15 Aug 1780 (reading a)', "McCrady, vol. 1, p. 668: the morning of 15 Aug.", 'high', add='S131')
settle('SCH13', 'American victory (reading a)', "McCrady, vol. 1, pp. 829-830: Sumter's men held the field at the close; Tarleton came onto it only the next morning.", 'high', add='S131')
settle('SCH14', 'The night of 28-29 Sep 1780', "The attack came about midnight. McCrady, vol. 1, about p. 735, says 'about the 14th of September', following James; recorded, not followed.",
       'medium', rc="About 14 Sep 1780 (McCrady, vol. 1, about p. 735)", add='S131')
for (k, q, a, b, c, adopted, because, conf, sids) in [
    ('SCH15', "Great Savannah (Nelson's Ferry), Aug 1780: what day?", "25 Aug 1780 (Marion to Gates, 29 Aug; the British account of the 24th's halt)",
     "21 Aug 1780 (McCrady, vol. 1, pp. 699-700, after Marion to Horry, 27 Aug: 'the 20th instant')", "20 Aug (ABT's lead date)", '25 Aug 1780 (reading a)',
     "Marion's two letters disagree; the report to his commander, two days later, and the British account of the halt at Sumter's house on the 24th agree on the 25th.", 'medium', 'S131; S133; S118'),
    ('SCH16', "Rugeley's Mill, Dec 1780: what day?", "4 Dec 1780 (McCrady's table, vol. 1, about p. 849; ABT; the Liberty Trail)", "1 Dec 1780 (the Archives list)", "30 Nov 1780 (a Journal of the American Revolution article)",
     '4 Dec 1780 (reading a)', "McCrady's table and two later accounts agree; the others are recorded.", 'medium', 'S131; S120; S116'),
    ('SCH17', "Hammond's Store, Dec 1780: what day?", "30 Dec 1780 (ABT, Wikipedia, the Archives list)", "29 Dec (McCrady, vol. 2, p. 27)", "20 Dec (McCrady's table, vol. 1, about p. 849)",
     '30 Dec 1780 (reading a)', "McCrady's own pages disagree with each other (20th, 29th, and a '3d' that looks like a slip); the other three sources agree.", 'medium', 'S131; S132; S116; S121'),
]:
    put(HY, k, dict(battle_id=None, question=q, reading_a=a, reading_b=b, reading_c=c, evidence_for='See the readings.', evidence_against='See the readings.',
                    adopted_reading=adopted, adopted_because=because, confidence=conf, status='Proposed', decided_by=WHO, decided_on=TODAY, reviewed_on=TODAY,
                    rows={'SCH15': 'T29', 'SCH16': 'T36', 'SCH17': 'T38'}[k], source_ids=sids, next_step='Morgan to confirm.',
                    history='New on 25 Nov 2026 (Session 3, redone in the evening).'))

# ---------------------------------------------------------------- summaries ----------------------------------------------------------------
SU = wb['Summaries']; sh = head(SU)
texts = {
    ('year', '1775-01-01'): ("1775: the Patriots take the forts",
        "The royal government loses its grip. Patriot leaders carry off the arms in Charleston in April, and the Crown's forts at Fort Charlotte "
        "(July) and Fort Johnson (September) are taken without a fight. In November Loyalists besiege Williamson's camp at Ninety Six for two "
        "days until a truce ends it; in December the Patriots break the Loyalist camp at Great Cane Brake and the Snow Campaign scatters the rest.",
        'S116; S117; S118; S120; S131'),
    ('year', '1776-01-01'): ("1776: the fort holds, the Cherokee war",
        "In June the palmetto fort on Sullivan's Island drives off the British fleet, and Breach Inlet stops the landing. From July the Cherokee "
        "strike the frontier. Williamson's column is ambushed at Esseneca on 1 August, the one Cherokee win drawn here, then beats a war party "
        "on 12 August and burns the Lower Towns; Fort Rutledge is built at Esseneca.", 'S116; S118; S119; S123; S131'),
    ('year', '1779-01-01'): ("1779: the war comes south",
        "Moultrie beats Gardiner's detachment on Port Royal Island in February. In May Prevost reaches the Charleston lines and draws off when "
        "Lincoln hurries back. On 20 June Lincoln's attack on the rear guard at Stono Ferry is repulsed, and the British fall back to Beaufort.",
        'S116; S118; S121; S131'),
    ('year', '1780-01-01'): ("1780: Charleston falls, then the partisan war",
        "Clinton lands in February, crosses the Ashley on 29 March, and Lincoln surrenders the city and army on 12 May. Tarleton wins at Monck's "
        "Corner, Lenud's Ferry and the Waxhaws, and British posts run inland to Camden, Ninety Six and the Cheraws. The partisans answer: Huck's "
        "Defeat, Rocky Mount and Hanging Rock, Sumter's raid at Wateree Ferry, Musgrove Mill and Marion's raids. Gates is routed at Camden on "
        "16 August and Sumter at Fishing Creek two days later. Kings Mountain in October turns the tide; Blackstock's, Rugeley's and Hammond's "
        "Store follow.", 'S116; S118; S121; S131; S132'),
    ('year', '1781-01-01'): ("1781: Cowpens",
        "Greene's army rests at the Cheraws, and Morgan's detachment works west of the Broad. On 17 January Morgan beats Tarleton at Cowpens. "
        "The playback ends here; the later actions are loaded as data for a second stage.", 'S118; S121; S132; S137'),
    ('end', '1781-01-17'): ("Where things stood on 17 January 1781",
        "The British hold Charleston and its harbour forts, Beaufort, Georgetown, Dorchester, Monck's Corner, Orangeburg, Fort Granby, Fort "
        "Galphin, Camden, Ninety Six and Cornwallis's camp at Winnsboro. Greene's army holds the Cheraws. Fort Charlotte, Esseneca, Tamassee and "
        "Kingstree are drawn as contested: no source read puts them under either side after June 1780. Who held what is reconstructed from the "
        "sources named on each place, not from a survey of the time, and several posts are dated only to the month.", 'S131; S132; S87; S134; S137'),
}
for r in range(2, SU.max_row + 1):
    row = {h: SU.cell(r, i + 1).value for i, h in enumerate(sh)}
    t = texts.get((row['kind'], row['from'])) if row['playback_id'] == 'sc-orientation' else None
    if t:
        for col, val in zip(('title', 'text', 'source_ids'), t): SU.cell(r, sh.index(col) + 1, val)
        SU.cell(r, sh.index('how written') + 1, 'Written by Claude (Opus) from the rows, 25 Nov 2026 (Session 3, redone)')

# ---------------------------------------------------------------- playback settings ---------------------------------------------------------
PS = wb['Playback settings']; ph = head(PS)


def setting(name, value, why=None):
    for r in range(2, PS.max_row + 1):
        if PS.cell(r, 1).value == 'sc-orientation' and PS.cell(r, 2).value == name:
            PS.cell(r, 3, value)
            if why and 'why' in ph: PS.cell(r, ph.index('why') + 1, why)
            return
    r = PS.max_row + 1; PS.cell(r, 1, 'sc-orientation'); PS.cell(r, 2, name); PS.cell(r, 3, value)
    if why and 'why' in ph: PS.cell(r, ph.index('why') + 1, why)


setting('about', json.dumps([
    "Dates and results come from the South Carolina Archives list of actions (Lipscomb), the National Park Service, the American Battlefield "
    "Trust and Wikipedia, each checked against at least one other. Where they disagree, McCrady's History of South Carolina in the Revolution "
    "(1901-02), which cites the memoirs and letters of the time, or a commander's own report settles the reading; the others are kept.",
    "A clash is drawn in the colour and shape of the side that won it. A grey diamond is a fight no source scores as a win. A dagger marks a "
    "result or a date on which the sources disagree; the pane gives both readings.",
    "Who held each place is reconstructed from the sources named on it, not from a survey of the time; several posts are dated only to the "
    "month and marked low. Positions come from markers, park and encyclopedia coordinates, or a place a source describes, each with its "
    "precision. 1777 and 1778 are flagged as gaps in the list."], ensure_ascii=False))
setting('sides.CR.name', 'British Crown forces (British regulars and Loyalist militia)', "In South Carolina most fights on the Crown side were Loyalist militia's (Session 3, 25 Nov 2026); this playback only")
setting('sides.CR.short', 'British and Loyalist', "In South Carolina most fights on the Crown side were Loyalist militia's (Session 3, 25 Nov 2026); this playback only")
wb.save(WAR)

# ---------------------------------------------------------------- sources and gaps ---------------------------------------------------------
sb = openpyxl.load_workbook(SHARED); SO = sb['Sources']
src = {
    'S131': dict(title="The History of South Carolina in the Revolution, 1775-1780", author='Edward McCrady', date='1901', type='Secondary: state history',
                 citation='McCrady, The History of South Carolina in the Revolution, 1775-1780 (New York: Macmillan, 1901). Printed page numbers.',
                 url='https://archive.org/details/historyofsouthca00mccr', rights='Public domain (published 1901).',
                 notes="Read 25 Nov 2026 in the Internet Archive text, at the pages for each disputed point. He cites Drayton, Moultrie, Lee, Tarleton, Stedman, Davie and the Sumter papers.",
                 used_for='SC orientation', kind='history', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='archive.org'),
    'S132': dict(title="The History of South Carolina in the Revolution, 1780-1783", author='Edward McCrady', date='1902', type='Secondary: state history',
                 citation='McCrady, The History of South Carolina in the Revolution, 1780-1783 (New York: Macmillan, 1902). Printed page numbers.',
                 url='https://archive.org/details/historyofsouthca00mccra', rights='Public domain (published 1902).',
                 notes="Read 25 Nov 2026 in the Internet Archive text (Rugeley's, Greene's march to the Cheraws, Hammond's Store, Halfway Swamp, the posts).",
                 used_for='SC orientation', kind='history', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='archive.org'),
    'S133': dict(title="Francis Marion's letters of August 1780 on Great Savannah", author='Francis Marion', date='1780-08-27; 1780-08-29', type='Primary: letters',
                 citation="Marion to Horatio Gates, 29 Aug 1780 (ABT primary-source page); Marion to Peter Horry, 27 Aug 1780 (Gibbes, Documentary History of the American Revolution, vol. 3, no. 20, p. 11).",
                 url='https://battlefields.org/learn/primary-sources/i-am-certain-they-will-desert-francis-marion-battle-great-savannah',
                 rights="The letters are public domain; the web transcriptions and their notes are cited, not copied.",
                 notes="Read 25 Nov 2026. To Gates: 'the 25th'; to Horry: 'the 20th instant'.", used_for='SC orientation', kind='letter', war='ARW',
                 rights_status='public domain', may_host='no: link and cite', rights_checked=TODAY, site='battlefields.org; losthistory.net'),
    'S134': dict(title="Fort and post pages: Fort Granby, Fort Galphin, Dorchester, Orangeburg", author='FortWiki; northamericanforts.com; SC Historic Properties Record; SC State Parks',
                 date='n.d.', type='Web pages',
                 citation="fortwiki.com (Fort Granby, Fort Galphin, Fort Dorchester); northamericanforts.com, Interior South Carolina; schpr.sc.gov record S108042001100174 (Fort Galphin); "
                          "southcarolinaparks.com, Colonial Dorchester.",
                 url='https://www.fortwiki.com/Fort_Granby', rights='Copyrighted: cited and cross-checked; nothing copied or hosted.',
                 notes="Read 25 Nov 2026 (search results and pages). Used for when the posts were occupied, which McCrady's pages read do not date.",
                 used_for='SC orientation', kind='reference', war='ARW', rights_status='in copyright', may_host='no: link and cite', rights_checked=TODAY, site='several'),
    'S137': dict(title="Nathanael Greene to George Washington, 28 December 1780", author='Nathanael Greene', date='1780-12-28', type='Primary: letter',
                 citation="Greene to Washington, 'Camp at the Cheraws on the east side of Pedee', 28 Dec 1780; Founders Online, The Papers of George Washington.",
                 url='https://founders.archives.gov/documents/Washington/03-29-02-0431',
                 rights="The letter is public domain; the editorial notes are cited, not copied.", notes='Read 25 Nov 2026 (heading and note 1).',
                 used_for='SC orientation', kind='letter', war='ARW', rights_status='public domain', may_host='no: link and cite', rights_checked=TODAY, site='founders.archives.gov'),
}
for k, v in src.items(): put(SO, k, v)
sb.save(SHARED)

wb = openpyxl.load_workbook(WAR); drop(wb['Gaps'], 'SCG01') if get(wb['Gaps'], 'SCG01', 'gap_id') and 'Ward' in str(get(wb['Gaps'], 'SCG01', 'gap')) else None; wb.save(WAR)
sb = openpyxl.load_workbook(SHARED); GA = sb['Gaps']   # the South Carolina gaps live in the shared workbook (SCG01-SCG05, Session 2)
put(GA, 'SCG06', {'battle_id': 'SCOR', 'gap': "Ward, The War of the Revolution, vol. 2, ch. 68 ('Before Cowpens'), the syllabus reading, was not read for the South Carolina orientation.",
                  'effect on the data': 'The readings settled by McCrady and the reports are not cross-checked against Ward.',
                  'how to close it': "Read Morgan's copy (war_cowpens.pdf, Canvas) against the Hypotheses rows SCH01-SCH17 and note agreement or difference by page.",
                  'v9 update': 'New on 25 Nov 2026 (Session 3, redone).'})
put(GA, 'SCG03', {'v9 update': note(get(GA, 'SCG03', 'v9 update'), "25 Nov 2026 (Session 3): T20, T21, T26, T29, T30, T35 and T36 now have clashes, placed from markers "
                  "or a place a source describes (Great Savannah and Rugeley's low, 6-8 km).")}, create=False)
sb.save(SHARED)
print('done')
