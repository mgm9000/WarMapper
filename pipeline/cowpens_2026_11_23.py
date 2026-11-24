"""23 Nov 2026: the Battle of Cowpens, 17 January 1781, added to the Revolutionary War workbook. Run once.

  python3 pipeline/cowpens_2026_11_23.py

It adds the campaign, the battle and its phases, the order of battle (Units, Assignments), the positions by the clock, the routes,
the events, the hypotheses (one per disputed point), the gaps, the playback with its settings, tracks and labels, and the source-use
rows to `Revolutionary War.xlsx`, and the new sources (and what became of the Cowpens candidates) to `Sources and notes.xlsx`.
Run it again and it does nothing: it stops if the playback `cowpens` is already on the Playbacks sheet.

Where every position comes from is said on its own row (coordinate_basis, source_wording, source_pages, cross_checked_by). In short:
the sources give distances along and across the Green River Road, not coordinates, so every unit is placed by distance from one point
on the road as OpenStreetMap draws it (pipeline/cowpens_geo.py). No position is rated above medium.
"""
import os, sys
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cowpens_geo as G

FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx'); SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
CAMP, BATTLE, PB, DAY = 'ARW-SOU', 'COWP', 'cowpens', '1781-01-17'
TODAY = '2026-11-23'


def T(hm): return '%s %s' % (DAY, hm)
def plus(hm, minutes):
    h, m = [int(x) for x in hm.split(':')]; t = h * 60 + m + minutes
    return '%02d:%02d' % (t // 60, t % 60)


# ---------------------------------------------------------------- sources (Sources and notes.xlsx)
MONCURE_URL = 'https://archive.org/details/DTIC_ADA530379'
SOURCES = [
    dict(source_id='S95', title='The Cowpens Staff Ride and Battlefield Tour', author='Lt. Col. John Moncure', date='1996',
         type='Modern secondary: Army staff ride handbook, with the eyewitness documents in its appendixes',
         citation='John Moncure, The Cowpens Staff Ride and Battlefield Tour (Fort Leavenworth, Kans.: Combat Studies Institute, U.S. Army Command and General Staff College, 1996), x + 208 pp., 15 maps. DTIC ADA530379.',
         **{'page verified?': 'yes (text of the scan read by printed page; maps 8 to 15 and the order-of-battle charts, pp. 91-94, read from the page images)'},
         url=MONCURE_URL,
         rights='U.S. Army publication. Its report page (SF 298) is marked "Approved for public release; distribution unlimited". The cover painting belongs to the State of South Carolina. Cited and linked; no page of it is hosted.',
         notes='Read 23 Nov 2026: chapter 3 (the battle, pp. 43-63) and its notes (pp. 65-70), chapter 4 (the staff ride, twelve vantage points with distances along the road, pp. 71-85), appendix A (order of battle, pp. 91-94) and the battle documents of appendix C (pp. 121-155). Its maps 8 to 14 give a clock time each (0700 to 0750), which the playback follows; the handbook itself says no evidence remains of the time the action began (p. 51) and gives sunrise as 0707 (note 28, p. 67). The maps are not to scale in their troop symbols: on map 12 Howard falls back some 500 yards by the scale bar, against 80 to 100 yards in the text, so they were read for which unit stood on which flank, not for distances. Morgan supplied a PDF earlier (StaffRideHB_Cowpens.pdf); this reading used the Internet Archive copy of the same DTIC scan.',
         used_for='COWP', kind='book', war='ARW', rights_status='public domain (to confirm)', may_host='check', rights_checked=TODAY, site='archive.org; govinfo.gov', local_copy='Historical Info (StaffRideHB_Cowpens.pdf, Morgan\'s Mac; not opened in this session)', page_offset=None, part_of=None),
    dict(source_id='S96', title='Morgan to Greene, camp near Cane Creek, 19 January 1781 (report of the action at the Cowpens)', author='Brig. Gen. Daniel Morgan', date='1781-01-19',
         type='Primary: commander\'s report, two days after the battle',
         citation='Daniel Morgan to Nathanael Greene, 19 January 1781; as printed in Moncure (S95), appendix C, pp. 122-125. First printed widely in James Graham, The Life of General Daniel Morgan (New York, 1856).',
         **{'page verified?': 'yes (pages of S95); the pages of Graham were not checked'}, url=MONCURE_URL,
         rights='Public domain (1781). Read in a U.S. Army publication.',
         notes='Gives the hour ("about sunrise"), the warning "an hour before daylight" with Tarleton five miles off, the order of the lines with the flanks of the militia, the British line "four hundred yards in front of our advanced corps", the retirement of "about fifty paces", the strengths (800 against 1,150 or 1,037) and the losses. Read in full.',
         used_for='COWP', kind='official report', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S97', title='A History of the Campaigns of 1780 and 1781, in the Southern Provinces of North America (the Cowpens passages)', author='Lt. Col. Banastre Tarleton', date='1787',
         type='Primary: the British commander\'s own account, published six years later',
         citation='Banastre Tarleton, A History of the Campaigns of 1780 and 1781 (London: T. Cadell, 1787); the Cowpens passages as printed in Moncure (S95), pp. 77-78, 81, 82, 84 and appendix C, pp. 147-151.',
         **{'page verified?': 'yes (pages of S95); the pages of the 1787 edition were not checked'}, url='https://archive.org/details/bim_eighteenth-century_a-history-of-the-campaig_tarleton-lieutenant-gen_1787',
         rights='Public domain (1787).',
         notes='The march from 03:00, the order of the British line from right to left, the dragoons on each flank, the 71st and about 200 cavalry in reserve 150 yards back, the advance to within 300 yards, the order to the 71st and the reserve cavalry, the cavalry that would not charge, and the last charge. Written to defend his conduct: Mackenzie (S102) answers it.',
         used_for='COWP', kind='book', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of=None),
    dict(source_id='S98', title='Lt. Col. John Eager Howard: two accounts of the Cowpens', author='John Eager Howard', date='after 1781 (the second about 1804)',
         type='Primary: participant, written years later',
         citation='John Eager Howard, notes on the battle and answers to questions about it; as printed in Moncure (S95), appendix C, pp. 126-131.',
         **{'page verified?': 'yes (pages of S95)'}, url=MONCURE_URL, rights='Public domain. Read in a U.S. Army publication.',
         notes='The commander of the main line: Triplett and Tate on his left, Wallace on his right; the order to Wallace that went wrong; the retreat to "the rising ground near Washington\'s horse", "about 100 yards"; the British "within 30 yards"; the guns; the militia horses "in the rear of my left flank"; Washington\'s charge.',
         used_for='COWP', kind='memoir', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S99', title='Maj. Samuel Hammond: notes of Morgan\'s order of battle', author='Samuel Hammond', date='1781 (notes of that evening; printed 1851)',
         type='Primary: participant\'s notes of the general order, written from memory the same evening',
         citation='Samuel Hammond, notes on the order of 16 January 1781 and the ground; as printed in Moncure (S95), appendix C, pp. 131-133 (from Joseph Johnson, Traditions and Reminiscences, Charleston, 1851).',
         **{'page verified?': 'yes (pages of S95)'}, url=MONCURE_URL, rights='Public domain. Read in a U.S. Army publication.',
         notes='The only record of the order itself, and of the ground: a small ridge across the road and a like one 300 to 500 yards in rear. It puts Cunningham on the right and McDowell on the left of the front line, the reverse of Morgan\'s report (CH05), and Triplett on the right of the second line (CH06).',
         used_for='COWP', kind='memoir', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S100', title='Journals of the Delaware Regiment: Lt. Thomas Anderson and Sgt. Maj. William Seymour', author='Thomas Anderson; William Seymour', date='1781',
         type='Primary: two journals kept in the Continental line',
         citation='Thomas Anderson, journal, entry for 17 January 1781, and William Seymour, journal, the same day; as printed in Moncure (S95), appendix C, pp. 139-142.',
         **{'page verified?': 'yes (pages of S95)'}, url=MONCURE_URL, rights='Public domain. Read in a U.S. Army publication.',
         notes='Anderson: in order of battle "by day Light", the British "Halted and Form\'d the Line in Full View", "about Sunrise they began the attack", the volley at "ten Or fifteen yards". Seymour: the militia "about two hundred yards" in front, Kirkwood\'s company against the British left, and the only clock time on the American side, "about seven o\'clock in the morning".',
         used_for='COWP', kind='diary', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S101', title='Memoirs and pension statements of the militia and the dragoons at the Cowpens', author='Joseph McJunkin; Thomas Young; James Collins; John Thomas; William Neel; Henry Connally; John Baldwin; James Simmons; James Kelley', date='1803 to the 1840s',
         type='Primary: participants, written or sworn long afterwards',
         citation='As printed in Moncure (S95), appendix C: McJunkin, pp. 133-135; Young, pp. 135-138; Connally, pp. 138-139; Kelley, pp. 142-143; Simmons, pp. 143-144; Baldwin, p. 144; Neel, pp. 144-145; Thomas, p. 145; Collins, pp. 145-146.',
         **{'page verified?': 'yes (pages of S95)'}, url=MONCURE_URL, rights='Public domain. Read in a U.S. Army publication.',
         notes='Old men\'s memories: good for what a man saw, weak on time and order. McJunkin: the three lines 150 yards apart. Young: the cavalry "in rear of the left wing of the regulars", the British cavalry on the American right. Simmons: Washington\'s four charges and the 17th Light Dragoons. Thomas: the retreat of "aboutt 80 yards" and the firing of "about an hour and forty minutes". Connally: the horses "about four hundred paces in the rear".',
         used_for='COWP', kind='memoir', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S102', title='Strictures on Lt. Col. Tarleton\'s History (the Cowpens letter)', author='Lt. Roderick Mackenzie, 71st Regiment', date='1787',
         type='Primary: British participant, written against Tarleton',
         citation='Roderick Mackenzie, Strictures on Lt. Col. Tarleton\'s History (London, 1787); the Cowpens letter as printed in Moncure (S95), appendix C, pp. 151-153, with Moncure\'s notes 32-34 (p. 68) on Hanger\'s reply.',
         **{'page verified?': 'yes (pages of S95)'}, url=MONCURE_URL, rights='Public domain (1787). Read in a U.S. Army publication.',
         notes='Wounded and taken with the 71st. Has the pursuit begin at two o\'clock, not three, and the attack made in haste before the line was formed and the reserve was up.',
         used_for='COWP', kind='memoir', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of='S95'),
    dict(source_id='S103', title='Historical Statements Concerning the Battle of Kings Mountain and the Battle of the Cowpens, South Carolina', author='Historical Section, Army War College (Lt. Col. H. L. Landers, F.A.)', date='1928',
         type='Early secondary: Army War College study printed for Congress, with sketch maps and photographs of the ground',
         citation='70th Congress, 1st Session, House Document No. 328 (Washington: Government Printing Office, 1928). The Battle of the Cowpens, pp. 46-78 and the plates facing p. 78.',
         **{'page verified?': 'partly: page numbers read from the running heads in the scan\'s text (pp. 64-66); the plates not seen'},
         url='https://archive.org/details/historicalstatem00army',
         rights='U.S. government publication of 1928: public domain.',
         notes='Read 23 Nov 2026 for the Cowpens part. Follows Morgan for the lines. Has the British deployment "completed at about 8 o\'clock" and the action last "about 50 minutes" (pp. 65-66). The caption of its 1928 photograph of the Washington Light Infantry monument: "Howard\'s line ran very close to where this monument is located." Its sketch map of the battle (No. 3, facing p. 78) could not be fetched as a picture from the workspace: a candidate for a period map.',
         used_for='COWP', kind='official history', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='archive.org', local_copy=None, page_offset=None, part_of=None),
    dict(source_id='S104', title='Cowpens: "Downright Fighting", The Story of Cowpens (National Park Handbook 135)', author='Thomas J. Fleming', date='1988',
         type='Modern secondary: National Park Service handbook',
         citation='Thomas J. Fleming, Cowpens: "Downright Fighting" (Washington, D.C.: Division of Publications, National Park Service, 1988), 96 pp. ISBN 0-912627-33-6.',
         **{'page verified?': 'yes (text of the scan read by printed page)'}, url='https://archive.org/details/cowpens00nati',
         rights='National Park Service publication (Government Printing Office, 1988). The Internet Archive marks it public domain and Project Gutenberg carries it (ebook 62413). Its paintings and maps may carry their own credits. Cited and linked, not hosted.',
         notes='Read 23 Nov 2026 for the battle (pp. 53-77) and the park guide (pp. 85-88). Morgan "some 830"; Tarleton about 1,100 with about 350 horsemen; the militia 150 yards ahead of Howard and the riflemen another hundred; Ogilvie\'s 50 Legion dragoons sent at the skirmishers; the 71st 150 yards behind the Fusiliers; "in less than an hour"; the deciding fight "just beyond the bend in the road"; the 1932 monument "originally stood in the center of Morgan\'s third line".',
         used_for='COWP', kind='book', war='ARW', rights_status='public domain (to confirm)', may_host='check', rights_checked=TODAY, site='archive.org; gutenberg.org', local_copy=None, page_offset=None, part_of=None),
    dict(source_id='S105', title='Wayside exhibits on the battlefield, Cowpens National Battlefield (as recorded in the Historical Marker Database)', author='National Park Service; coordinates and transcriptions by Historical Marker Database contributors', date='waysides about 2008; database pages read 2026-11-23',
         type='Reference: what the National Park Service says happened at each spot, with coordinates',
         citation='Historical Marker Database (hmdb.org), markers 13423 Form the Line of Battle; 13028 Skirmishers Retreat, British Advance; 13065 Sharpshooters at the Skirmish Line; 77693 Let \'em Get Within Killin\' Distance; 13031 Colonel Howard\'s Misunderstood Order; 13029 A Race for the Grasshopper; 13030 Double Envelopment; 11357 The British Army; 13025 Sword Clash on Green River Road; 13064 The Continental Army at Cowpens; 11356 January 17, 1781; 13385 Washington Light Infantry Monument.',
         **{'page verified?': 'n/a (web pages)'}, url='https://www.hmdb.org/m.asp?m=13423',
         rights='The wayside texts are National Park Service work; the database pages and photographs are their contributors\'. Facts and coordinates only; short quotations.',
         notes='Read 23 Nov 2026 through the browser on Morgan\'s Mac. Used as the second witness for where each line stood on today\'s ground. The coordinates are to a thousandth of a minute, but several markers share a figure and the monument is 125 m from where OpenStreetMap has it: treat them as good to about 50 m (CG05).',
         used_for='COWP', kind='reference', war='ARW', rights_status='facts only', may_host='no: link and cite', rights_checked=TODAY, site='hmdb.org', local_copy=None, page_offset=None, part_of=None),
    dict(source_id='S106', title='Cowpens Audio Tour Stop 7: Sharpshooters at the Skirmish Line', author='National Park Service, Cowpens National Battlefield', date='2022-04-09 (last updated)',
         type='Reference: National Park Service web page',
         citation='National Park Service, "Sharpshooters at the Skirmish Line", Cowpens National Battlefield, page last updated 9 April 2022.',
         **{'page verified?': 'n/a (web page)'}, url='https://www.nps.gov/places/sharpshooters-at-the-skirmish-line.htm',
         rights='U.S. government work (National Park Service web page). The photograph is credited to NPS / Mike Puckett.',
         notes='Read 23 Nov 2026. About 150 picked riflemen "around 100 yards in front of the main militia line"; part of the Legion cavalry sent to disperse them; John Savage\'s shot.',
         used_for='COWP', kind='reference', war='ARW', rights_status='public domain', may_host='yes (the text)', rights_checked=TODAY, site='nps.gov', local_copy=None, page_offset=None, part_of=None),
]

# what became of the Cowpens candidates on Source candidates (status and a note added; nothing deleted)
CANDIDATES = {
    'SC-SOU02': ('used: now source S95', 'Read on 23 Nov 2026 from the Internet Archive copy of the DTIC scan (ADA530379); now S95, with the documents of its appendix C as S96 to S102.'),
    'SC-SOU03': ('read in part; not used', 'NOT read on 23 Nov 2026: the PDF is on Morgan\'s Mac (battle-of-cowpens.pdf) and the folder was not connected to that session; the South Carolina State Library and npshistory.com copies could not be reached from the workspace. Its troop movement maps are the first thing to read before the Cowpens positions are accepted (gap CG01).'),
    'SC-SOU06': ('located', '23 Nov 2026: the park page nps.gov/cowp/planyourvisit/maps.htm lists a "Cowpens battle map"; not fetched. The wayside exhibits were read instead, through the Historical Marker Database (S105).'),
}
NEW_CANDIDATES = [
    ('SC-SOU08', 'Sketch map of the Battle of the Cowpens (No. 3, facing p. 78) in House Document 328', 'Army War College, Historical Section, 1928 (S103); Internet Archive scan', 'https://archive.org/details/historicalstatem00army', 'ARW', 'COWP',
     'The Army War College\'s 1928 sketch of the lines on the ground, made from a visit in April 1928.', 'The text was read; the page image could not be fetched from the workspace (the archive\'s image servers are not on its allowed list).',
     'U.S. government publication of 1928: public domain. May be hosted.', 'located', 'P1', TODAY, 'The best candidate for a period map of Cowpens that may be hosted: see gap CG02.'),
    ('SC-SOU09', 'A Devil of a Whipping: The Battle of Cowpens', 'Lawrence E. Babits (University of North Carolina Press, 1998); Internet Archive lending copy', 'https://archive.org/details/devilofwhippingb0000babi', 'ARW', 'COWP',
     'The standard modern study, built on the pension files: unit by unit positions, strengths about double Morgan\'s 800, and its own timing.', 'Lending copy; not read.',
     'In copyright. Link and cite only.', 'located', 'P1', TODAY, 'Not read. The NPS administrative history reports its finding that Morgan had about 2,000 men (see CH03).'),
]

# ---------------------------------------------------------------- campaign, battle, phases
CAMPAIGN = dict(campaign_id=CAMP, war_id='ARW', name='Greene\'s campaign in the Carolinas, 1780-81 (Cowpens to Guilford Courthouse)', start_date='1780-12-20', end_date='1781-03-15',
                wikidata_qid=None, notes='Morgan\'s detachment west of the Broad from 20 December 1780 (S95, map 3) to the battle of Guilford Courthouse. Cowpens is its first battle in the workbook; Guilford Courthouse and the campaign playback are to follow under this id.')
BATTLE_ROW = dict(battle_id=BATTLE, campaign_id=CAMP, parent_battle_id=None, name='Battle of Cowpens', start_earliest=T('07:00'), start_latest=T('08:00'), end_earliest=T('07:50'), end_latest=T('09:00'),
                  lat=35.135021, lon=-81.814875, coord_precision='battle', coord_source='OpenStreetMap (S39): the Washington Light Infantry monument of 1856, by which Howard\'s line ran (S103)',
                  wikidata_qid='Q1326527', cdb90_id=None, war_atlas_slug=None,
                  notes='Start: "about sunrise" (S96), "about seven o\'clock" (S100), deployment complete "at about 8 o\'clock" (S103): see CH01. End: the staff ride\'s last map is 0750 and it has the field won "not yet nine o\'clock" (S95, pp. 61-62). The Wikidata id is the item a Wikidata search by place returned at the coordinates Wikipedia gives the battle; its label was not read: confirm.',
                  extent_km=6)
PHASES = [
    ('PH-C1', 'Forming for battle', '06:00', '06:58', 'S95; S96; S100', 'From the warning "an hour before daylight" to the two lines in sight of each other.'),
    ('PH-C2', 'Skirmishers and militia', '07:00', '07:35', 'S95; S96', 'Staff ride maps 8 to 11: 0700 to 0730.'),
    ('PH-C3', 'The main line: retreat, volley and bayonet', '07:35', '07:50', 'S95; S98', 'Staff ride maps 12 and 13: 0740 and 0745.'),
    ('PH-C4', 'Envelopment and pursuit', '07:50', '08:30', 'S95; S96', 'Staff ride map 14: 0750. The pursuit ran 22 to 24 miles and is off the map.'),
]

# ---------------------------------------------------------------- order of battle
US, CR = 'ARW-US', 'ARW-CR'
SYM = {('Infantry', 'Brigade'): '181211', ('Infantry', 'Regiment'): '171211', ('Infantry', 'Battalion'): '161211', ('Infantry', 'Company'): '151211', ('Infantry', 'Detachment'): '141211',
       ('Infantry', 'Headquarters'): '001211', ('Cavalry', 'Headquarters'): '001213', ('Cavalry', 'Squadrons'): '161213', ('Cavalry', 'Company'): '151213', ('Cavalry', 'Detachment'): '141213', ('Artillery', 'Section'): '131303'}
# unit_id, name, map label, side, nation, branch, echelon, sources, notes, parent, commander, strength, assignment sources, assignment notes
UNITS = [
    ('C-US-MORGAN', 'Morgan\'s detachment (the "flying army")', 'Morgan', US, 'United States', 'Infantry', 'Brigade', 'S95; S96', 'The whole American force. Its strength is disputed by a factor of two: CH03.',
     None, 'Brig. Gen. Daniel Morgan', '"We fought only eight hundred men, two-thirds of which were militia" (S96). 1,117 by the staff ride\'s charts: Howard 350, Pickens 650, cavalry 117 (S95, pp. 92-94). "Some 830" (S104). Tarleton counted about 1,920 (S97).', 'S95; S96; S97; S104', None),
    ('C-US-HQ', 'Morgan\'s headquarters', 'Morgan (HQ)', US, 'United States', 'Infantry', 'Headquarters', 'S96; S98', 'Aide Maj. Edward Giles and brigade major Capt. Brookes are named in Morgan\'s report (S96).',
     'C-US-MORGAN', 'Brig. Gen. Daniel Morgan', None, 'S96', None),
    ('C-US-HOW', 'Howard\'s line: the Continental light infantry and the Virginians (the main line)', 'Howard', US, 'United States', 'Infantry', 'Battalion', 'S95; S96; S98', 'The third and main line. The staff ride calls it the Delaware-Maryland Regiment (+).',
     'C-US-MORGAN', 'Lt. Col. John Eager Howard', '"About 350 men" (Howard, S98; S95, p. 92). Under 450 (S103, p. 66). Mackenzie says 250 Continentals; Tarleton 500 (S95, p. 92 n. 5).', 'S95; S98; S103', None),
    ('C-US-MDDE', 'Maryland and Delaware light infantry (Continentals)', 'MD and DE Continentals', US, 'United States', 'Infantry', 'Battalion', 'S95; S98; S100', 'Picked men of the two Maryland regiments with the Delaware company (S98). Companies on the staff ride\'s chart: Beatty (MD), Kirkwood (DE), Anderson, Dobson (MD) (S95, p. 92).',
     'C-US-HOW', 'Lt. Col. John Eager Howard', 'About 320 Continentals (S104, opening of the narrative). Formed in two ranks over about 200 yards (S95, p. 48).', 'S95; S104', None),
    ('C-US-KIRK', 'Kirkwood\'s Delaware company', 'Kirkwood', US, 'United States', 'Infantry', 'Company', 'S95; S100', 'Not placed on the map: no source read says where in the line it stood. It "wheeled to the right and attacked their left flank" (Seymour, S100).',
     'C-US-MDDE', 'Capt. Robert Kirkwood', None, 'S95; S100', None),
    ('C-US-WALL', 'Wallace\'s Virginia company', 'Wallace', US, 'United States', 'Infantry', 'Company', 'S95; S98', 'The right of Howard\'s line. "Virginia regulars" to Howard (S98); Virginia militia on the staff ride\'s chart (S95, p. 92). Its attempt to change front began the retreat.',
     'C-US-HOW', 'Capt. Wallace', None, 'S98', None),
    ('C-US-TRIP', 'Triplett\'s and Tate\'s Virginia militia', 'Triplett and Tate', US, 'United States', 'Infantry', 'Battalion', 'S95; S96; S98', 'Two companies of Virginia riflemen, many of them former Continentals; Buchanan\'s Augusta men with Tate (S96; Neel, S101). Which flank they held is disputed: CH06.',
     'C-US-HOW', 'Maj. Francis Triplett; Capt. Tate', None, 'S96; S98; S101', None),
    ('C-US-PICK', 'Pickens\'s militia (the second line)', 'Pickens', US, 'United States', 'Infantry', 'Brigade', 'S95; S96', 'Volunteers of North Carolina, South Carolina and Georgia. Pickens did not command them all, but they served in his line (S95, p. 93 n. 7). Maj. James Jackson of Georgia acted as brigade major.',
     'C-US-MORGAN', 'Col. Andrew Pickens', '650 (S95, p. 93). Tarleton took the line for "about one thousand" (S97).', 'S95; S97', None),
    ('C-US-MCD', 'McDowell\'s North Carolina riflemen (skirmishers)', 'McDowell', US, 'United States', 'Infantry', 'Battalion', 'S95; S96; S104', 'Half of the skirmish line. On the right by Morgan\'s report, on the left by Hammond\'s notes: CH05.',
     'C-US-PICK', 'Maj. Joseph McDowell', '140 (S95, p. 93; S104, p. 60)', 'S95; S104', None),
    ('C-US-CUN', 'Cunningham\'s Georgians (skirmishers)', 'Cunningham', US, 'United States', 'Infantry', 'Battalion', 'S95; S96; S99', 'The other half of the skirmish line, with the dismounted part of McCall\'s state troops under Maj. Samuel Hammond (S99). On the left by Morgan\'s report: CH05.',
     'C-US-PICK', 'Maj. John Cunningham', None, 'S95; S96', None),
    ('C-US-BRAN', 'Brandon\'s regiment (South Carolina militia)', 'Brandon', US, 'United States', 'Infantry', 'Regiment', 'S95; S96; S101', 'With Lt. Col. William Farr. "A column marches up in front of Brandon\'s men" (McJunkin, S101).',
     'C-US-PICK', 'Col. Thomas Brandon', None, 'S95; S96', None),
    ('C-US-THOM', 'Thomas\'s regiment (South Carolina militia)', 'Thomas', US, 'United States', 'Infantry', 'Regiment', 'S95; S96', None,
     'C-US-PICK', 'Col. John Thomas', None, 'S95; S96', None),
    ('C-US-HAYS', 'Hays\'s regiment (South Carolina militia)', 'Hays', US, 'United States', 'Infantry', 'Regiment', 'S95; S96', 'Morgan writes "Hay".',
     'C-US-PICK', 'Col. Hays', None, 'S95; S96', None),
    ('C-US-MCC', 'McCall\'s South Carolina state troops (dismounted part)', 'McCall', US, 'United States', 'Infantry', 'Battalion', 'S95; S96; S99', 'The part of McCall\'s regiment not yet equipped as dragoons, under Maj. Samuel Hammond (S99); Morgan lists "McCall" on the left of the line (S96).',
     'C-US-PICK', 'Maj. Samuel Hammond', None, 'S96; S99', None),
    ('C-US-ROE', 'Roebuck\'s battalion (South Carolina militia)', 'Roebuck', US, 'United States', 'Infantry', 'Battalion', 'S95; S101', 'On the staff ride\'s chart and in McJunkin\'s list; no source read says where in the line it stood. Not placed.',
     'C-US-PICK', 'Lt. Col. Benjamin Roebuck', None, 'S95; S101', None),
    ('C-US-WASH', 'Washington\'s cavalry (the reserve)', 'Washington', US, 'United States', 'Cavalry', 'Squadrons', 'S95; S96; S98', 'The 3d Continental Light Dragoons with McCall\'s mounted volunteers.',
     'C-US-MORGAN', 'Lt. Col. William Washington', 'About 117: 72 dragoons and 45 mounted militia (S95, p. 94). Tarleton saw 120 (S97).', 'S95; S97', None),
    ('C-US-3LD', '3d Continental Light Dragoons', '3d Light Dragoons', US, 'United States', 'Cavalry', 'Squadrons', 'S95; S101', 'Troops under Fauntleroy and Jones on the staff ride\'s chart (S95, p. 94). Drawn as part of Washington\'s cavalry.',
     'C-US-WASH', 'Lt. Col. William Washington', '72, counted by Josiah Martin on 16 January (S95, p. 94 n. 10)', 'S95', None),
    ('C-US-MCCM', 'McCall\'s mounted volunteers', 'McCall (mounted)', US, 'United States', 'Cavalry', 'Company', 'S95; S101; S103', 'Enrolled as dragoons the night before the battle and given sabres (McJunkin, S101; S103, pp. 63-64). Drawn as part of Washington\'s cavalry.',
     'C-US-WASH', 'Lt. Col. James McCall', '45 (S95, p. 94; S103, pp. 63-64)', 'S95; S103', None),

    ('C-BR-TARL', 'Tarleton\'s detachment', 'Tarleton', CR, 'Great Britain', 'Infantry', 'Brigade', 'S95; S97', 'The whole British force. See CH04 for its strength.',
     None, 'Lt. Col. Banastre Tarleton', '1,126 (S95, p. 91). Morgan: "not less than one thousand one hundred and fifty" with the baggage guard; "their own officers confess that they fought one thousand and thirty-seven" (S96). About 1,100 (S104).', 'S95; S96; S104', None),
    ('C-BR-HQ', 'Tarleton and his staff', 'Tarleton (HQ)', CR, 'Great Britain', 'Cavalry', 'Headquarters', 'S95; S97', None,
     'C-BR-TARL', 'Lt. Col. Banastre Tarleton', None, 'S97', None),
    ('C-BR-LI', 'Light infantry (companies of the 16th, the 71st and the Prince of Wales\'s American Regiment)', 'Light infantry', CR, 'Great Britain', 'Infantry', 'Battalion', 'S95; S97', 'The right of the British line. One of its companies was provincial (the Prince of Wales\'s American Regiment).',
     'C-BR-TARL', 'Not named in the sources read', '150 (S95, p. 91). The light company of the 71st alone was 69 on the return of 15 January (S95, p. 91 n. 3).', 'S95', None),
    ('C-BR-LEGI', 'British Legion infantry', 'Legion infantry', CR, 'Loyalist', 'Infantry', 'Battalion', 'S95; S97', 'The centre of the British line. Provincials raised in the middle colonies; many of them prisoners enlisted after Camden (S95, p. 56).',
     'C-BR-TARL', 'Not named in the sources read', '300 (S95, p. 91). The whole Legion, horse and foot, was 451 on the return of 15 January (S95, p. 91 n. 1).', 'S95', None),
    ('C-BR-7', '7th Regiment of Foot (Royal Fusiliers), 1st Battalion', '7th Fusiliers', CR, 'Great Britain', 'Infantry', 'Battalion', 'S95; S97; S104', 'The left of the British line. Mostly recruits (S95, p. 76).',
     'C-BR-TARL', 'Maj. Timothy Newmarsh', '176: 167 rank and file and 9 officers (S95, p. 91 n. 4)', 'S95; S104', None),
    ('C-BR-71', '71st Regiment of Foot (Fraser\'s Highlanders), 1st Battalion', '71st Highlanders', CR, 'Great Britain', 'Infantry', 'Battalion', 'S95; S97; S104', 'The reserve, then the left of the attack on Howard.',
     'C-BR-TARL', 'Maj. Archibald McArthur', '200 (Tarleton; S95, p. 91). 249 on the return of 15 January (S95, p. 91 n. 3).', 'S95; S97', None),
    ('C-BR-RA1', 'Royal Artillery: 3-pounder with the right of the line', '3-pdr (right)', CR, 'Great Britain', 'Artillery', 'Section', 'S95; S97', 'One of two light 3-pounders ("grasshoppers"). The first part of the line advanced "under the fire of a 3-pounder" (S97).',
     'C-BR-TARL', 'Not named in the sources read', 'About 20 gunners for the two guns (S95, p. 91); Babits says 36 (S95, p. 91 n. 2)', 'S95', None),
    ('C-BR-RA2', 'Royal Artillery: 3-pounder with the 7th Regiment', '3-pdr (left)', CR, 'Great Britain', 'Artillery', 'Section', 'S95; S97', '"The other 3-pounder was given to the right division of the 7th" (S97).',
     'C-BR-TARL', 'Not named in the sources read', None, 'S97', None),
    ('C-BR-17', '17th Light Dragoons (troop)', '17th Light Dragoons', CR, 'Great Britain', 'Cavalry', 'Company', 'S95; S97; S101', 'The dragoons on the right flank (S95, p. 76), who rode down the militia and were met by Washington (Simmons, S101).',
     'C-BR-TARL', 'A captain (S97); not named in the sources read', '50 (S95, p. 91; S97)', 'S95; S97', None),
    ('C-BR-OGIL', 'British Legion cavalry: Ogilvie\'s advance guard', 'Ogilvie', CR, 'Loyalist', 'Cavalry', 'Company', 'S95; S97; S104', 'Two troops sent ahead before dawn; then the fifty dragoons on the left flank (S95, p. 76).',
     'C-BR-LEGC', 'Capt. David Ogilvie', '50 (S95, p. 76; S104, p. 62)', 'S95; S104', None),
    ('C-BR-LEGC', 'British Legion cavalry (the reserve)', 'Legion cavalry', CR, 'Loyalist', 'Cavalry', 'Squadrons', 'S95; S97', 'In reserve with the 71st. It would not charge and left the field (S97).',
     'C-BR-TARL', 'Lt. Col. Banastre Tarleton', '"Near two hundred cavalry" in reserve (S97); 250 Legion cavalry in all (S95, p. 91); Mackenzie puts all the British cavalry at 350 (S95, p. 91 n. 1)', 'S95; S97', None),
    ('C-BR-BAG', 'Baggage and its guard', 'Baggage', CR, 'Great Britain', 'Infantry', 'Detachment', 'S95; S97', 'Left on the ground of the night\'s camp till daybreak "under the protection of a detachment of each corps" (S97), about twelve miles from the field (S96); under Lt. Fraser of the 71st (S95, p. 85). Off the map; not placed.',
     'C-BR-TARL', 'Lt. Fraser, 71st Regiment', None, 'S95; S97', None),
]

# ---------------------------------------------------------------- positions
TB = ('Clock from the staff ride\'s maps (S95, maps 8 to 14: 0700 to 0750). They fit "about sunrise" (Morgan, S96; Anderson, S100) and "about seven o\'clock" (Seymour, S100); '
      'sunrise was 0707 (S95, p. 67 n. 28). The Army War College study has the attack begin about 8 o\'clock (S103, p. 65), so the latest time is an hour later. See CH01.')
TB_PRE = 'Before the fighting: "an hour before daylight" for the warning and "by day Light" for the line (S96; S100). The clock times are estimates from sunrise at 0707 (S95, p. 67 n. 28).'
FRAME = ('Placed by distance along the Historic Green River Road as OpenStreetMap draws it (S39), counted from the south-east end of the Battlefield Trail loop (35.13294, -81.81012), '
         'where the staff ride\'s Vantage 6 (S95, p. 77) and the NPS wayside "The British Army" (S105) put the head of Tarleton\'s column as it came onto the field. ')
B_BRIT = FRAME + ('The line of battle is 70 m up the road from that point and square to it: between that point and the NPS wayside "Form the Line of Battle", where the 7th Regiment "formed in this immediate area" '
                  '(about 135 m up the road and 100 m south-west of it, S105). Each unit has its share of about 340 yards by its strength (S95, p. 91), in Tarleton\'s order from right to left.')
B_SKIRM = FRAME + ('205 m up the road: the staff ride puts the centre of the skirmish line 200 m from Vantage 6 (S95, p. 78) and the NPS wayside "Sharpshooters at the Skirmish Line" stands about 205 m up the road (S105).')
B_MIL = FRAME + ('330 m up the road. The sources differ: 150 yards in front of Howard (McJunkin, S101; S104, p. 55) or 200 (Seymour, S100); on the ground, 400 m from Vantage 6 by the staff ride (S95, p. 78) '
                 'and about 275 m by the NPS wayside "Let \'em Get Within Killin\' Distance" (S105). 330 m lies between them and is 150 m in front of Howard\'s line as placed. See CH07.')
B_HOW = FRAME + ('480 m up the road, abreast of the Washington Light Infantry monument (35.13502, -81.81488, S39): "Howard\'s line ran very close to where this monument is located" (S103, plate facing p. 78). '
                 'The staff ride puts the centre of the line 500 m from Vantage 6, its left about 100 m north-east of the road (S95, p. 79).')
B_HOW2 = FRAME + ('565 m up the road, at the bend: about 85 m behind the first position. Morgan says "about fifty paces" (S96), Thomas "aboutt 80 yards" (S101), Howard "about 100 yards" (S98); '
                  'the staff ride walks 100 m from Vantage 8 to Vantage 10 (S95, p. 82), and the NPS handbook puts the deciding fight "just beyond the bend in the road" (S104, p. 85). See CH08.')
REV = 'Needs review'
POS = []   # rows, in order


def P(pid, unit, show, activity, place, geom, basis, cconf, prec, sources, wording, method, conf, pages, cross, notes=None, tb=TB, start=None, end=None, csrc='derived'):
    """One Positions row. `show` is (from, to) as HH:MM. The record's own times are a range: from the shown time to an hour later (CH01),
    unless `start` / `end` give them. `geom` is one (lat, lon) or a pair of them (a line, flank to flank)."""
    f, t = show
    se, sl = start or (T(f), T(plus(f, 60))); ee, el = end or (T(t), T(plus(t, 60)))
    line = isinstance(geom[0], tuple)
    a, b = (geom if line else (geom, None))
    POS.append(dict(pos_id=pid, campaign_id=CAMP, battle_id=BATTLE, unit_id=unit, start_earliest=se, start_latest=sl, end_earliest=ee, end_latest=el, time_basis=tb,
                    activity=activity, place_description=place, geometry='line' if line else 'point', lat=a[0], lon=a[1], line_end_lat=b[0] if b else None, line_end_lon=b[1] if b else None,
                    coord_source=csrc, coord_precision_m=prec, coordinate_basis=basis, coordinate_confidence=cconf, source_ids=sources, source_wording=wording, position_method=method,
                    overall_confidence=conf, notes=notes, review_status=REV, show_from=T(f), show_to=T(t), source_pages=pages, cross_checked_by=cross))


at, line = G.at, G.line
CAMP_AT = at(1010, 0)
# ---- the Americans
P('CP01', 'C-US-MORGAN', ('06:00', '06:12'), 'In camp; called to arms', 'Morgan\'s camp at the Cowpens, on the Green River Road north-west of the field', CAMP_AT,
  'The staff ride puts the camp about 300 m north of its Vantage 1, which is beside today\'s visitor centre (S95, p. 72 and map 15): on the Green River Road about 1 km up it from the trail end, as OpenStreetMap draws the road (S39). Hammond puts the front line only "three hundred to three hundred and fifty yards" from the camp (S99), which would bring it half as far: not reconciled.',
  'low', 300, 'S95; S96; S99; S100; S39',
  'S96: "An hour before daylight one of my scouts returned and informed me that Lieut. Col. Tarleton had advanced within five miles of our camp." S100 (Anderson): "Before day Reced Information ... We got up and put Ourselves in Order of Battle by day Light".',
  'stated', 'low', 'S95 p. 72; S96 in S95 p. 122; S100 in S95 p. 140', 'S100',
  notes='Morgan reached the Cowpens "about sundown" on 16 January (S95, p. 46). The place of the camp is the least sure point on the map.', tb=TB_PRE, start=('1781-01-16 17:00', '1781-01-16 18:00'), end=(T('05:45'), T('06:30')))
P('CP02', 'C-US-HQ', ('06:40', '07:33'), 'With the militia line', 'Behind the centre of Pickens\'s line, on the Green River Road', at(350, 0), B_MIL, 'low', 100, 'S95; S98; S101',
  'S98 (Howard): "Morgan, who had mostly been with the militia". S101 (Young): Morgan "galloped along the lines, cheering the men, and telling them not to fire until we could see the whites of their eyes."',
  'stated', 'low', 'S98 in S95 p. 127; S101 in S95 p. 136; S95 p. 52', 'S101', notes='Sources put him with the militia, not at a spot: drawn just behind the centre of their line.')
P('CP03', 'C-US-HQ', ('07:41', '07:48'), 'Choosing the ground for the line to halt and face about', 'The rising ground near Washington\'s horse, where Howard\'s line re-formed', at(585, 0), B_HOW2, 'medium', 80, 'S95; S96; S98',
  'S98 (Howard): Morgan "ordered me to keep with the men, until we came to the rising ground near Washington\'s horse; and he rode forward to fix on the most proper place for us to halt and face about."',
  'stated', 'medium', 'S98 in S95 pp. 127-128; S95 p. 58', 'S95')
P('CP04', 'C-US-HQ', ('07:53', '08:30'), 'On the field after the surrender', 'Among the captured guns and prisoners, on the Green River Road', at(505, 0), B_HOW, 'low', 120, 'S95; S96',
  'S96: "We pushed our advantage so effectually, that they never had an opportunity of rallying". Paraphrase: Morgan left the field the same morning to secure the prisoners (S96).',
  'inferred', 'low', 'S96 in S95 pp. 123-124', 'S95', notes='No source places Morgan at this moment; drawn with Howard\'s line.')

SK_W = ('S96: "Maj. McDowail, of the North Carolina volunteers, was posted on the right flank in front of the line, one hundred and fifty yards; and Maj. Cunningham, of the Georgia volunteers, on the left, at the same distance in front." '
        'S106: about 150 riflemen "around 100 yards in front of the main militia line". S95, p. 78: Vantage 7, 200 m from Vantage 6, is "the center of the skirmish line".')
for pid, unit, o1, o2, side in (('CP05', 'C-US-MCD', 12, 125, 'right (south-west) of the road'), ('CP06', 'C-US-CUN', -12, -125, 'left (north-east) of the road')):
    P(pid, unit, ('06:35', '07:18'), 'Skirmish line: riflemen behind trees', 'The skirmish line, %s' % side, line(205, o1, o2), B_SKIRM + ' The two commands are drawn either side of the road, each over about 125 yards.', 'medium', 60,
      'S95; S96; S99; S105; S106; S39', SK_W, 'stated', 'medium', 'S96 in S95 p. 123; S95 pp. 50, 75, 78; S99 in S95 p. 132', 'S105; S106',
      notes='Which of the two was on the right is disputed: Morgan\'s report is followed (McDowell right, Cunningham left); Hammond\'s notes of the order have it the other way (CH05).', tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
for pid, unit, o1, o2 in (('CP07', 'C-US-MCD', 145, 185), ('CP08', 'C-US-CUN', -145, -185)):
    P(pid, unit, ('07:21', '07:23'), 'Fallen back on the militia line', 'The flank of Pickens\'s line', line(330, o1, o2), B_MIL, 'low', 80, 'S95; S96; S100; S105',
      'S96: "McDowail and Cunningham gave them a heavy and galling fire, and retreated to the regiments intended for their support." S100 (Anderson): the riflemen "Fought Well Disputing the ground ... Flying from One tree to another".',
      'stated', 'low', 'S96 in S95 p. 123; S100 in S95 p. 140; S95 p. 52 and map 10 (0720)', 'S105', notes='The sources say they fell back into the militia line, not where in it: drawn on the flank next to their own side of the road. From here they are part of Pickens\'s line.')

MIL_W = ('S96: "The volunteers from North Carolina, South Carolina, and Georgia, under the command of the brave and valuable Col Pickens, were situated to guard the flanks ... Colonels Brannon and Thomas, of the South Carolinans, were posted on the right of Maj. McDowail, '
         'and Cols. Hay and McCall, of the same corps, on the left of Maj. Cunningham." S105: "The American second line of defense stood in position here." S101 (McJunkin): the militia "at the distance of 150 yards" in front of the regulars.')
P('CP10', 'C-US-PICK', ('06:35', '07:31'), 'Line of battle (militia)', 'Pickens\'s line across the Green River Road, on the first rise', line(330, 140, -140), B_MIL + ' The line is drawn 280 m long, the width of the field (200 to 250 m, S95, p. 45) and a little over.', 'medium', 80,
  'S95; S96; S100; S101; S104; S105; S39', MIL_W, 'stated', 'medium', 'S96 in S95 p. 123; S95 pp. 50, 74-75, 78; S101 in S95 pp. 133-134; S100 in S95 p. 141; S104 p. 55', 'S105; S104',
  tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
for pid, unit, o1, o2, who in (('CP11', 'C-US-BRAN', 140, 75, 'the right of the line'), ('CP12', 'C-US-THOM', 72, 5, 'right of the road'), ('CP13', 'C-US-HAYS', -5, -72, 'left of the road'), ('CP14', 'C-US-MCC', -75, -140, 'the left of the line')):
    P(pid, unit, ('06:35', '07:31'), 'Line of battle (militia)', 'Pickens\'s line, %s' % who, line(330, o1, o2), B_MIL + ' Morgan gives the order of the regiments by flank, not their ground: each is given a quarter of the line.', 'low', 100,
      'S95; S96; S101; S105; S39', MIL_W, 'inferred', 'low', 'S96 in S95 p. 123; S95 pp. 50, 93', 'S105',
      notes='Morgan\'s order from right to left is followed: Brandon, Thomas, Hays, McCall (S96). The share of the line each held is not in any source read.', tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
P('CP15', 'C-US-PICK', ('07:36', '07:44'), 'Withdrawn; re-forming near the horses', 'In rear of the left of Howard\'s line, towards the militia\'s horses', at(650, -120),
  FRAME + 'In rear of Howard\'s left: about 170 m behind his first line and 120 m north-east of the road. Howard has the horses "tied in the woods in the rear of my left flank" (S98); Connally has them "about four hundred paces in the rear of the line of Battle" (S101), which would be twice as far back.',
  'low', 150, 'S95; S96; S98; S101',
  'S96: "The whole of Col Pickens\' command then kept up a fire by regiments, retreating agreeably to their orders." S98: "The militia fell into our rear, and part of them fell into the rear of my right flank where they afterwards renewed the action." S95, p. 56: they "streamed around both flanks but mostly around the left".',
  'stated', 'low', 'S96 in S95 p. 123; S98 in S95 pp. 128-129; S95 p. 56 and map 12 (0740); S101 in S95 p. 139', 'S95',
  notes='Drawn as one body round Howard\'s left. Baldwin and Thomas have the militia divide to right and left (S101): CH09. Many made for their horses and did not come back (S104, p. 67).')
P('CP16', 'C-US-PICK', ('07:50', '08:30'), 'Back into the fight: round the British left, on the 71st', 'South-west of the road, on the flank and rear of the 71st', (at(520, 240), at(430, 255)),
  FRAME + 'A line along the south-west side of the fight, 240 to 255 m from the road, abreast of the ground between Howard\'s two positions and of the British left: the staff ride\'s map 14 has the militia sweep round Howard\'s right onto the British left (S95, p. 61). Distances from the road are an estimate.',
  'low', 150, 'S95; S98; S101; S105',
  'S98: part of the militia "fell into the rear of my right flank where they afterwards renewed the action". S95, p. 60: "Pickens\' militia, which had regrouped behind the Continental Line, appeared on the American right, sweeping around behind the other British flank." S105 (Double Envelopment): "The militia reformed and surged against the right and left."',
  'stated', 'low', 'S98 in S95 p. 128; S95 pp. 60-61 and map 14 (0750); Pickens in S95 pp. 125-126', 'S105',
  notes='Who ordered the militia back in is not known: CH11. "That part of the 71st which was there surrendered to me" (Pickens, S95, p. 125).')

HOW_W = ('S96: "The light infantry, commanded by Lieut. Col. Howard, and the Virginia militia under the command of Major Triplett, were formed on a rising ground, and extended a line in front." '
         'S103: "Howard\'s line ran very close to where this monument is located." S95, p. 79: Vantage 8 "is the center of the line of the initial position of the Continental Line, the left flank of which extended about 100 meters to the northeast."')
HOW2_W = ('S96: "We retired in good order about fifty paces, formed, and advanced on the enemy, and gave them a fortunate volley". S98 (Howard): Morgan "ordered me to retreat to Washington\'s horse about 100 yards, and there form ... '
          'The enemy pressed upon us in rather disorder ... They were by this time within 30 yards of us with two field pieces".')
HOW3_W = ('S98 (Howard): "I ordered a charge with the bayonet ... As the line approached, I observed their artillery a short distance in front". S100 (Anderson): "We let them Come Within ten Or fifteen yards of us then give them a full Volley and at the Same time Charged them home."')
PARTS = (('C-US-WALL', 115, 80, 'the right of the line'), ('C-US-MDDE', 78, -50, 'the centre, across the road'), ('C-US-TRIP', -53, -115, 'the left of the line'))
P('CP20', 'C-US-HOW', ('06:35', '07:39'), 'Line of battle (the main line)', 'Howard\'s line across the Green River Road, by the Washington Light Infantry monument', line(480, 115, -115), B_HOW, 'medium', 60,
  'S95; S96; S98; S103; S104; S39', HOW_W, 'stated', 'medium', 'S96 in S95 p. 122; S95 pp. 48, 74, 79; S103 plate facing p. 78; S98 in S95 p. 126', 'S103; S95', tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
for i, (unit, o1, o2, who) in enumerate(PARTS):
    P('CP%d' % (21 + i), unit, ('06:35', '07:39'), 'Line of battle (the main line)', 'Howard\'s line, %s' % who, line(480, o1, o2), B_HOW + ' The share of the line each part held is an estimate: the Continentals in two ranks over about 130 m, the Virginians on either flank.',
      'low', 80, 'S95; S96; S98; S103; S39', HOW_W + ' S98 (Howard): "I am positive that Triplett and Tate were on my left"; Wallace\'s company was "on my right".', 'stated', 'low',
      'S98 in S95 pp. 126-127; S95 pp. 48, 50', 'S95', notes='Howard is followed for the flanks; Morgan\'s report puts Tate and Buchanan in support of the right (CH06).', tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
P('CP24', 'C-US-HOW', ('07:42', '07:46'), 'Fallen back; faces about and fires', 'The rising ground at the bend of the Green River Road', line(565, 115, -115), B_HOW2, 'medium', 70,
  'S95; S96; S98; S100; S101; S104; S39', HOW2_W, 'stated', 'medium', 'S96 in S95 p. 123; S98 in S95 pp. 127-128; S101 (Thomas) in S95 p. 145; S95 pp. 58, 82 and map 13 (0745); S104 p. 85', 'S98; S104')
for i, (unit, o1, o2, who) in enumerate(PARTS):
    P('CP%d' % (25 + i), unit, ('07:42', '07:46'), 'Fallen back; faces about and fires', 'Howard\'s second position, %s' % who, line(565, o1, o2), B_HOW2, 'low', 90,
      'S95; S96; S98; S39', HOW2_W, 'inferred', 'low', 'S98 in S95 pp. 127-128; S95 p. 58', 'S95', notes='The line kept its order as it fell back (S98); the parts are drawn as in the first position.')
P('CP28', 'C-US-HOW', ('07:50', '08:30'), 'Bayonet charge; among the British line and its guns', 'Between Howard\'s two positions, across the Green River Road', line(508, 115, -115),
  FRAME + 'About 55 m forward of the second position: the British were 10 to 30 yards from it when it fired (S98; S100), and their guns "a short distance in front" (S98).', 'low', 90,
  'S95; S98; S100; S105', HOW3_W, 'inferred', 'low', 'S98 in S95 p. 127; S100 in S95 p. 140; S95 pp. 58-60 and map 14 (0750)', 'S100; S105',
  notes='NPS wayside "A Race for the Grasshopper": Capt. Anderson of Maryland took one gun, Capt. Kirkwood the other (S105); Howard names Anderson and Ewing (S98).')
for i, (unit, o1, o2, who) in enumerate(PARTS):
    P('CP%d' % (29 + i), unit, ('07:50', '08:30'), 'Bayonet charge', 'Howard\'s line going forward, %s' % who, line(508, o1, o2), FRAME + 'About 55 m forward of the second position, as its line (CP28).', 'low', 100,
      'S95; S98; S100', HOW3_W, 'inferred', 'low', 'S98 in S95 p. 127; S100 in S95 p. 140', 'S95')

P('CP32', 'C-US-WASH', ('06:35', '07:32'), 'In reserve', 'In rear of the left of Howard\'s line, on the rise', at(590, -90),
  FRAME + 'About 110 m behind Howard\'s first line and 90 m north-east of the road: the staff ride has the cavalry "about 100 yards behind the left flank of the army" (S95, p. 51); Howard fell back "about 100 yards" to "the rising ground near Washington\'s horse" (S98).',
  'medium', 100, 'S95; S96; S98; S99; S101',
  'S96: the dragoons "were posted at such a distance in their rear, as not to be subjected to the line of fire directed at them, and to be so near as to be able to charge them should they be broken." S101 (Young): "The cavalry formed in rear of the centre, or rather in rear of the left wing of the regulars." S98: not behind the rise "but on the summit; for I had a full view of him as we retreated".',
  'stated', 'medium', 'S96 in S95 pp. 122-123; S98 in S95 pp. 126, 128; S101 in S95 p. 136; S95 p. 51', 'S98; S101', tb=TB_PRE + ' ' + TB, start=(T('06:15'), T('06:45')))
P('CP33', 'C-US-WASH', ('07:35', '07:38'), 'First charge: on the dragoons cutting down the militia', 'In rear of the American left, towards the militia\'s horses', at(610, -235),
  FRAME + 'About 235 m north-east of the road behind Howard\'s left, where the British dragoons caught the militia making for their horses (S98). The distance from the road is an estimate.', 'low', 150, 'S95; S96; S98; S101; S104',
  'S96: "Lieut. Col Washington, having been informed that the Tarleton was cutting down our riflemen on the left, pushed forward, and charged them with such firmness, that ... [they] broke and fled." S101 (Simmons): "your first charge was made on the enemy\'s Cavalry, (who were cutting down our Militia) ... leaving in the course of ten minutes 18 of their brave 17th Dragoons dead on the spot".',
  'stated', 'low', 'S96 in S95 p. 123; S101 in S95 pp. 143, 134; S98 in S95 p. 129; S95 pp. 56, 79-80 and map 11 (0730)', 'S101; S104', notes='Howard puts this charge at the moment of his own bayonet charge, not before it (S98): CH10.')
P('CP34', 'C-US-WASH', ('07:41', '07:46'), 'Re-formed behind the left of the main line', 'Behind the left of Howard\'s second position', at(625, -150), B_HOW2 + ' The cavalry is drawn 60 m behind the left of that line.', 'low', 120, 'S95; S98',
  'S98 (Howard): the line fell back "to the rising ground near Washington\'s horse". S95, p. 60: "Washington now parried the fixing attack on the American left flank and moved forward, past Triplett\'s flank".',
  'inferred', 'low', 'S98 in S95 p. 128; S95 p. 60 and map 13 (0745)', 'S95')
P('CP35', 'C-US-WASH', ('07:49', '07:52'), 'Charge round the British right and into their rear', 'Behind the right of the broken British line, north-east of the road', at(410, -40),
  FRAME + 'Behind the British line, about 45 m beyond where it gave way and 40 m north-east of the road, from the staff ride\'s map 14 (S95, p. 61). An estimate.', 'low', 150, 'S95; S101; S105',
  'S95, p. 60: Washington "moved forward, past Triplett\'s flank and behind the right flank of the now crumbling British line." S101 (Young): "making a sort of circuit at full speed, came up in the rear of the British line, shouting and charging like madmen." S101 (McJunkin): "Washington darts before them with his cavalry and they too ground their arms."',
  'stated', 'low', 'S95 pp. 60-61 and map 14 (0750); S101 in S95 pp. 137, 135', 'S101; S105')
P('CP36', 'C-US-WASH', ('07:55', '07:58'), 'Meets Tarleton\'s last charge; the sword fight', 'On the Green River Road at the south-east end of the field', at(-10, 0),
  FRAME + 'At that point: the NPS wayside "Sword Clash on Green River Road" stands there and says the clash was "Nearby" (S105). The staff ride has Tarleton turn "several hundred yards away from the scene of triumph and surrender" (S95, p. 62).', 'low', 150, 'S95; S98; S101; S105',
  'S105: "Nearby, retreating British officers of the 17th Light Dragoons, clashed with pursuing American horsemen led by Lt. Col. William Washington." S98 (Howard): "In the pursuit he had got a head of his men, perhaps 30 yards. Three of the british officers observing this wheeled about and made a charge at him."',
  'stated', 'low', 'S95 p. 62; S98 in S95 pp. 129-130; S105 (marker 13025)', 'S105; S98', notes='What happened in it is disputed: CH12.')
P('CP37', 'C-US-WASH', ('08:16', '08:30'), 'Pursuit of Tarleton down the Green River Road', 'Off the field to the south-east', (35.12294, -81.79050),
  'The north-west end of today\'s Green River Road (S39), taken as the old road by which Tarleton had come; the stretch between it and the old trace in the park is not known (CG06).', 'low', 500, 'S95; S96; S98; S39',
  'S96: Tarleton "was pursued twenty-four miles, but owing to our having taken a wrong trail at first, we could never overtake him." Pickens: "We pursued with Coln Washington 22 miles" (S95, p. 126).',
  'inferred', 'low', 'S96 in S95 p. 124; S95 pp. 62, 126', 'S95', notes='The pursuit ran 22 to 24 miles; only its start is on the map.', csrc='modern_map')

# ---- the British
COL_AT = (35.11533, -81.78412)   # on today's Green River Road, 1,040 m short of its north-west end (data/osm/cowpens.txt)
P('CP40', 'C-BR-TARL', ('06:20', '06:28'), 'Column on the march', 'On the Green River Road, about two miles south-east of the field', COL_AT,
  'A point on today\'s Green River Road (S39) about 3.3 km by road from the field. The sources give no place for the column at any hour after 03:00: it is put here so that it reaches the field about dawn. The modern road is taken as the old one (CG06).', 'low', 800, 'S95; S96; S97; S102; S39',
  'S97: "at three o\'clock in the morning on the 17th, the pickets being called in, the British troops ... were directed to follow the route the Americans had taken the previous evening ... Before dawn, Thickelle creek was passed, when an advanced guard of cavalry was ordered to the front." S96: an hour before daylight Tarleton "had advanced within five miles of our camp".',
  'inferred', 'low', 'S97 in S95 p. 147; S96 in S95 p. 122; S102 in S95 p. 152', 'S96; S102', notes='Mackenzie has the march begin at two o\'clock (S102): CH13.', tb=TB_PRE, start=(T('06:00'), T('07:00')), end=(T('06:30'), T('07:30')), csrc='modern_map')

OG = 'C-BR-OGIL'
P('CP41', OG, ('06:45', '06:52'), 'Advance guard: drives in the American vedettes', 'On the Green River Road at the edge of the field', at(-150, 0), FRAME + '150 m short of that point on the road: the pickets were "several miles ahead" earlier (S95, p. 50); this is the last of the drive, an estimate.', 'low', 200, 'S95; S97; S101; S104',
  'S101 (Young): "It was about day that the pickets were driven in." S97: an advanced guard of cavalry "was ordered to the front"; S104, p. 53: two troops of Legion cavalry under Capt. David Ogilvie sent to reinforce the vanguard, who found the Americans "drawn up in an open wood in battle formation".',
  'inferred', 'low', 'S97 in S95 p. 147; S101 in S95 p. 136; S104 p. 53; S95 pp. 51, 77', 'S104', tb=TB_PRE, start=(T('06:30'), T('07:00')), end=(T('06:50'), T('07:20')))
P('CP42', OG, ('07:02', '07:06'), 'Sent to drive in the skirmishers; met by rifle fire', 'In front of the skirmish line, on the Green River Road', at(160, 0), B_SKIRM + ' The dragoons are drawn 45 m short of the skirmishers.', 'low', 100, 'S95; S104; S105; S106',
  'S105 (The British Army): Tarleton "ordered a detachment of cavalry forward to scatter the American skirmishers." S104, p. 62: "He turned to the 50 British Legion dragoons commanded by Captain Ogilvie and ordered them to \'drive in\' the skirmishers." S95, p. 77: "Tarleton ordered Ogilvie to scatter the skirmishers".',
  'stated', 'low', 'S95 pp. 52, 77; S104 p. 62; S105 (marker 11357); S106', 'S104; S105', notes='The first shots. McJunkin and Young credit John Savage with the first (S101).')
P('CP43', OG, ('07:09', '07:11'), 'On the left flank of the line', 'Left of the 7th Regiment', at(70, 185), B_BRIT, 'low', 120, 'S95; S97',
  'S97: "A captain, with fifty dragoons, was placed on each flank of the corps, who formed the British front line, to protect their own, and threaten the flanks of the enemy". S95, p. 76: "On the extreme left flank stood two troops of British Legion cavalry under Captain Ogilvie."',
  'stated', 'low', 'S97 in S95 p. 78; S95 p. 76 and map 8 (0700)', 'S95')
for pid, a, o, show, act in (('CP44', 190, 195, ('07:19', '07:22'), 'Advancing on the left flank'), ('CP45', 290, 200, ('07:28', '07:33'), 'On the left flank, facing the militia line'), ('CP46', 435, 290, ('07:37', '07:44'), 'On the left flank, beyond the 71st')):
    P(pid, OG, show, act, 'Left flank of the British line', at(a, o), FRAME + '%d m up the road with the line, on its left: the dragoons are assumed to have kept their place on the flank as the line went forward.' % a, 'low', 150, 'S95; S97',
      'S97: the dragoons on each flank were "to protect their own, and threaten the flanks of the enemy". S101 (Young): "I soon found that the British cavalry had charged the American right."', 'inferred', 'low', 'S97 in S95 p. 78; S95 maps 9 to 12; S101 in S95 p. 137', 'S95',
      notes='No source read follows this troop after the line advanced. Young\'s British cavalry on the American right may be this troop (CH10).')
P('CP47', OG, ('07:51', '07:54'), 'Driven off with the wreck of the line', 'South-east end of the field, south-west of the road', at(60, 120), FRAME + 'An estimate: back where the line had formed.', 'low', 200, 'S95; S97',
  'S97: "About two hundred dragoons forsook their leader, and left the field of battle."', 'inferred', 'low', 'S97 in S95 p. 84', 'S95', notes='Not recorded: drawn leaving with the rest of the Legion cavalry.')
P('CP48', OG, ('08:22', '08:30'), 'Left the field', 'Off the field to the south-east, on the road they came by', COL_AT, 'On today\'s Green River Road (S39), where the column is first drawn (CP40): the way they had come.', 'low', 500, 'S95; S97; S39',
  'S97: "About two hundred dragoons forsook their leader, and left the field of battle."', 'inferred', 'low', 'S97 in S95 p. 84', 'S95', csrc='modern_map')

LINE_W = ('S97: "The light infantry were then ordered to file to the right till they became equal to the flank of the American front line: The legion infantry were added to their left; and, under the fire of a 3-pounder, this part of the British troops was instructed to advance within three hundred yards of the enemy. '
          'This situation being acquired, the 7th regiment was commanded to form upon the left of the legion infantry, and the other 3-pounder was given to the right division of the 7th". S96: "The enemy drew up in single line of battle, four hundred yards in front of our advanced corps."')
ADV_W = 'S96: "their whole line moved on with the greatest impetuosity, shouting as they advanced." S100 (Anderson): "about Sunrise they began the attack by the Discharge of two pieces of cannon and three Huzzas advancing briskly On our riflemen".'
MILF_W = ('S105 (Let \'em Get Within Killin\' Distance): the militia "fought well and shot with deadly effect". S101 (Young): "The militia fired first. It was for a time, pop - pop - pop - and then a whole volley". '
          'S100 (Anderson): "the Enemy Seeing us Standing in Such good Order Halted for Some time to dress their line Which Outflanked ours Considerably".')
MAIN_W = ('S97: "As the contest between British infantry in the front line and the continentals seemed equally balanced, neither retreating, Lieutenant-colonel Tarleton thought the advance of the 71st into line, and a movement of cavalry in reserve to threaten the enemy\'s right flank, would put a victorious period into the action." '
          'S100 (Anderson): "The then advanced On boldly under a Very heavy fire until the got Within a few yards of us but their line Was So much longer than ours the turn\'d our Flanks".')
RUSH_W = ('S97: "the continentals and back woodsmen gave ground: The British rushed forwards ... An unexpected fire at this instant from the Americans, who came about as they were retreating, stopped the British, and threw them into confusion." S98: "They were by this time within 30 yards of us".')
SURR_W = ('S97: "an unaccountable panic extended itself along the whole line." S101 (McJunkin): "One battalion throws down their arms and the men fall to the earth. Another commences flight, but Washington darts before them with his cavalry and they too ground their arms." S96: "five hundred and two non-commissioned officers and privates prisoners".')
FRONT = (('C-BR-LI', -175, -90, 'the right of the line', 'CP5'), ('C-BR-LEGI', -85, 45, 'the centre, across the road', 'CP6'), ('C-BR-7', 50, 135, 'the left of the line', 'CP7'))
STAGES = ((70, ('06:58', '07:10'), 'Line of battle', B_BRIT, 'low', 100, LINE_W, 'stated', 'medium', 'S97 in S95 pp. 77-78; S96 in S95 p. 123; S95 p. 76 and map 8 (0700); S105 (markers 13423, 11357, 11356); S104 p. 63', 'S105; S104', 'S95; S96; S97; S104; S105; S39'),
          (190, ('07:19', '07:22'), 'Advancing; the skirmishers fall back before it', FRAME + '190 m up the road: just short of the skirmish line (205 m) as its riflemen went back, at the hour of the staff ride\'s map 10.', 'low', 100, ADV_W, 'inferred', 'low', 'S96 in S95 p. 123; S100 in S95 p. 140; S95 p. 52 and maps 9, 10 (0710, 0720)', 'S100', 'S95; S96; S100'),
          (290, ('07:28', '07:33'), 'Under the fire of the militia line', FRAME + '290 m up the road: 40 m (about 45 yards) short of the militia line as placed. The militia held their fire to "killing distance", about 30 to 50 yards (S104, p. 65).', 'low', 100, MILF_W, 'inferred', 'low', 'S101 in S95 p. 136; S100 in S95 p. 140; S95 pp. 52, 56 and map 11 (0730); S104 p. 65; S105 (marker 77693)', 'S105; S104', 'S95; S100; S101; S104; S105'),
          (435, ('07:37', '07:41'), 'Firing on the main line', FRAME + '435 m up the road: 45 m short of Howard\'s first line. The two lines fired on each other at close musket range; no source gives the distance.', 'low', 100, MAIN_W, 'inferred', 'low', 'S97 in S95 p. 81; S100 in S95 p. 140; S95 pp. 56-58', 'S100', 'S95; S97; S100'),
          (538, ('07:44', '07:46'), 'Rushing on after the retiring line; struck by its volley', FRAME + '538 m up the road: 27 m (30 yards) short of Howard\'s second position, as Howard has it; Anderson says 10 or 15 yards (S100).', 'low', 90, RUSH_W, 'stated', 'low', 'S97 in S95 pp. 81, 82; S98 in S95 p. 128; S100 in S95 p. 140; S95 map 13 (0745)', 'S98; S100', 'S95; S97; S98; S100'),
          (455, ('07:50', '08:30'), 'Broken; lays down its arms', FRAME + 'About 455 m up the road: driven back some 80 m from where the volley struck it, and ridden round there. An estimate.', 'low', 120, SURR_W, 'inferred', 'low', 'S97 in S95 p. 82; S101 in S95 p. 135; S96 in S95 p. 124; S95 pp. 60-62 and map 14 (0750); S105 (marker 13030)', 'S105', 'S95; S96; S97; S101; S105'))
for unit, o1, o2, who, pre in FRONT:
    for i, (a, show, act, basis, cconf, prec, wording, method, conf, pages, cross, srcs) in enumerate(STAGES):
        note = None
        if i == 0 and unit == 'C-BR-7': note = 'Mackenzie has the attack begin before the 7th was fully formed (S102); the NPS wayside says the same (S105). See CH14.'
        if i >= 1: note = (note or '') + 'The unit is assumed to have kept its place in the line as it went forward.'
        P('%s%d' % (pre, i + 1), unit, show, act, 'British line, %s' % who, line(a, o1, o2), basis, cconf, prec, srcs, wording, method, conf, pages, cross, notes=note,
          start=(T('06:50'), T('08:00')) if i == 0 else None)

GUNS = (('C-BR-RA1', -88, 'CP8', 'Between the light infantry and the Legion infantry'), ('C-BR-RA2', 48, 'CP9', 'With the right of the 7th Regiment'))
GUN_W = ('S97: the first part of the line advanced "under the fire of a 3-pounder ... and the other 3-pounder was given to the right division of the 7th". S96: "In front moved two pieces of artillery." S98 (Howard): "Their artillery was not thrown into the rear, but was advanced a little at the head of the line, and was taken".')
for unit, o, pre, where in GUNS:
    for i, (a, show, act) in enumerate(((75, ('06:58', '07:10'), 'In action in the line'), (195, ('07:19', '07:22'), 'Advancing with the line'), (295, ('07:28', '07:33'), 'Firing on the militia line'), (440, ('07:37', '07:41'), 'Firing on the main line'))):
        P('%s%d' % (pre, i + 1), unit, show, act, where, at(a, o), FRAME + 'A few metres in front of the line at %d m up the road, in the gap Tarleton gives it.' % a, 'low', 100, 'S95; S96; S97; S98', GUN_W, 'stated' if i == 0 else 'inferred', 'low',
          'S97 in S95 p. 78; S96 in S95 p. 123; S98 in S95 p. 128; S95 p. 52', 'S96; S98', start=(T('06:50'), T('08:00')) if i == 0 else None)
    P('%s5' % pre, unit, ('07:44', '08:30'), 'Left in front as the line broke; taken at the bayonet', where + '; between Howard\'s two positions', at(522, o), FRAME + 'About 520 m up the road: "a short distance in front" of Howard\'s line as it charged from its second position (S98).', 'low', 90,
      'S95; S96; S98; S105', 'S98 (Howard): "As the line approached, I observed their artillery a short distance in front, and called to Captain Ewing, who was near me, to take it. Captain Anderson ... made a long leap which brought him upon the gun". S96: the British fled "leaving their fieldpieces in our possession".',
      'stated', 'low', 'S98 in S95 pp. 127-129; S96 in S95 p. 123; S95 p. 60; S105 (marker 13029)', 'S105; S96', notes='The gunners fought to the last; Howard saved the man who would not give up his match (S98).')

R71 = 'C-BR-71'
P('CP101', R71, ('06:58', '07:35'), 'In reserve', 'About 150 yards behind the left of the 7th Regiment', line(-67, 60, 170), B_BRIT + ' The 71st is 137 m (150 yards) behind that line and reaching a little beyond its left.', 'medium', 120, 'S95; S97; S103; S104',
  'S97: "the 1st battalion of the 71st was desired to extend a little to the left of the 7th regiment, and to remain one hundred and fifty yards in the rear. This body of infantry, and near two hundred cavalry, composed the reserve."',
  'stated', 'medium', 'S97 in S95 p. 78; S103 p. 65; S104 p. 63; S95 map 8 (0700)', 'S103; S104', notes='Mackenzie has the reserve not yet clear of the woods when the attack began (S102; S95, p. 58).', start=(T('06:50'), T('08:00')))
P('CP102', R71, ('07:39', '07:41'), 'Brought up on the left of the 7th to turn Howard\'s right', 'Left of the British line, beyond Howard\'s right flank', line(440, 150, 250), FRAME + '440 m up the road and 150 to 250 m south-west of it: beyond the left of the 7th and outside Howard\'s right flank (115 m from the road as placed).', 'low', 120, 'S95; S97; S98; S105',
  'S97: "The 71st were desired to pass the 7th before they gave their fire, and were directed not to entangle their right flank with the left of the other battalion." S98 (Howard): "their line extended much further than mine particularly on my right, where they were pressing forward to gain my flank."',
  'stated', 'low', 'S97 in S95 p. 81; S98 in S95 p. 128; S95 pp. 56-58 and map 12 (0740); S105 (marker 13031)', 'S98; S105')
P('CP103', R71, ('07:44', '07:46'), 'Pressing round Howard\'s right as his line falls back', 'South-west of the road, on the right of Howard\'s second position', line(538, 120, 215), FRAME + '538 m up the road with the rest of the line, 120 to 215 m south-west of the road. An estimate.', 'low', 120, 'S95; S97; S98; S100',
  RUSH_W + ' S100 (Seymour): "they then thought to surround our right flank, to prevent which Captain Kirkwood with his company wheeled to the right and attacked their left flank".', 'inferred', 'low', 'S97 in S95 p. 81; S100 in S95 p. 141; S95 map 13 (0745)', 'S100')
P('CP104', R71, ('07:52', '08:30'), 'Broken into squads; surrenders', 'South-west of the road, between the militia and Howard\'s right', line(470, 130, 200), FRAME + 'About 470 m up the road, 130 to 200 m south-west of it: between Howard\'s right and the militia that came round it. An estimate.', 'low', 150, 'S95; S98; S101; S105',
  'S98 (Howard): "In the pursuit, I was led towards the right, in among the 71st, who were broken into squads, and as I called to them to surrender, they laid down their arms, and the officers delivered up their swords." Pickens: "That part of the 71st which was there surrendered to me" (S95, p. 125).',
  'stated', 'low', 'S98 in S95 p. 127; S95 pp. 125-126, 60-62; S105 (marker 13030)', 'S105', notes='Pickens says Maj. McArthur gave up his sword "some distance from the battlefield" (S95, p. 126).')

LC = 'C-BR-LEGC'
P('CP111', LC, ('06:58', '07:50'), 'In reserve', 'Behind the 71st, by the Green River Road', at(-115, 40), B_BRIT + ' The reserve cavalry is put 185 m behind the line, just behind the 71st: Tarleton gives it no distance of its own.', 'low', 200, 'S95; S97; S104',
  'S97: "This body of infantry [the 71st], and near two hundred cavalry, composed the reserve." S96: "Lieut. Col Tarleton, with his cavalry, was posted in the rear of the line."', 'stated', 'low', 'S97 in S95 p. 78; S96 in S95 p. 123; S95 map 8 (0700); S104 p. 63', 'S96; S104',
  notes='Ordered to form on the left and outflank Howard\'s right, and then to form 400 yards to the right to cover the infantry, it did neither (S97; S95, pp. 56, 84; S104, pp. 69-70).', start=(T('06:50'), T('08:00')))
P('CP112', LC, ('08:22', '08:30'), 'Left the field without charging', 'Off the field to the south-east, on the road they came by', COL_AT, 'On today\'s Green River Road (S39), where the column is first drawn (CP40): the way they had come.', 'low', 500, 'S95; S97; S39',
  'S97: "all attempts to restore order, recollection, or courage, proved fruitless. About two hundred dragoons forsook their leader, and left the field of battle."', 'stated', 'low', 'S97 in S95 p. 84; S101 (Simmons) in S95 p. 143', 'S101', csrc='modern_map')

D17 = 'C-BR-17'
D_W = 'S97: "A captain, with fifty dragoons, was placed on each flank". S95, p. 76: "To their right were stationed the fifty troopers of the 17th Light Dragoons."'
P('CP121', D17, ('06:58', '07:10'), 'On the right flank of the line', 'Right of the light infantry', at(70, -215), B_BRIT, 'low', 120, 'S95; S97; S105', D_W + ' S105 (January 17, 1781): "The right flank of the British army formed in this general area".', 'stated', 'low', 'S97 in S95 p. 78; S95 p. 76 and map 8 (0700); S105 (marker 11356)', 'S95; S105', start=(T('06:50'), T('08:00')))
for pid, a, show in (('CP122', 190, ('07:19', '07:22')), ('CP123', 290, ('07:28', '07:31'))):
    P(pid, D17, show, 'Advancing on the right flank', 'Right flank of the British line', at(a, -225), FRAME + '%d m up the road with the line, on its right: the dragoons are assumed to have kept their place on the flank.' % a, 'low', 150, 'S95; S97', D_W, 'inferred', 'low', 'S97 in S95 p. 78; S95 maps 9 to 11', 'S95')
P('CP124', D17, ('07:34', '07:36'), 'Charges the retiring militia round the American left', 'In rear of the American left, towards the militia\'s horses', at(600, -250), FRAME + 'About 250 m north-east of the road behind Howard\'s left, where Howard has the British cavalry pursue the militia "to their horses" (S98). An estimate.', 'low', 150, 'S95; S98; S101; S104',
  'S98 (Howard): "a large body of british cavalry passes round my left flank and pursued the flying militia to their horses." S95, p. 79: "the fifty troopers of the 17th Light Dragoons fell upon them in pursuit, cutting and slashing". S104, p. 66: "Tarleton ordered the 50 dragoons on his right flank to pursue Pickens".',
  'stated', 'low', 'S98 in S95 p. 129; S95 pp. 56, 79-80 and map 11 (0730); S101 in S95 pp. 134, 139, 143; S104 p. 66', 'S101; S104')
P('CP125', D17, ('07:40', '07:50'), 'Beaten off by Washington; fallen back by the way it came', 'North-east of the road, towards the south-east end of the field', at(240, -270), FRAME + 'An estimate: back down the north-east side of the field.', 'low', 200, 'S95; S98; S101',
  'S98 (Howard): "I observed the enemy\'s cavalry retreating the way the[y] had advanced, by our left flank, and Washington in pursuit of them". S101 (Simmons): 18 of the 17th Dragoons left dead.', 'inferred', 'low', 'S98 in S95 p. 129; S101 in S95 p. 143', 'S101')
P('CP126', D17, ('07:54', '07:57'), 'Tarleton\'s last charge', 'On the Green River Road at the south-east end of the field', at(15, -15), FRAME + 'At that point: see CP36.', 'low', 150, 'S95; S97; S105',
  'S95, p. 62: Tarleton "took fifty loyal troopers - most of them regulars from the 17th Light Dragoons - again into the fray where, once again, they were repulsed." S105: "retreating British officers of the 17th Light Dragoons, clashed with pursuing American horsemen".',
  'stated', 'low', 'S95 pp. 62, 85; S97 in S95 p. 84; S105 (marker 13025)', 'S105', notes='Tarleton says fourteen officers and forty horsemen (as Howard quotes him, S98).')
P('CP127', D17, ('08:24', '08:30'), 'Retreat with Tarleton', 'Off the field to the south-east', COL_AT, 'On today\'s Green River Road (S39), where the column is first drawn (CP40): the way they had come.', 'low', 500, 'S95; S96; S39',
  'S96: "Tarleton, with the small remains of his cavalry, and a few scattered infantry he had mounted on his wagon-horses, made their escape."', 'stated', 'low', 'S96 in S95 p. 124; S95 p. 62', 'S95', csrc='modern_map')

HQ = 'C-BR-HQ'
P('CP131', HQ, ('06:55', '07:10'), 'Reconnoitres and forms the line', 'On the Green River Road behind the centre of the line', at(40, 0), B_BRIT, 'low', 120, 'S95; S97; S104',
  'S97: "He discovered that the American commander had formed a front line of about one thousand militia, and had composed his second line and reserve of five hundred continental light infantry, one hundred and twenty of Washington\'s cavalry, and three hundred back woodsmen."',
  'inferred', 'low', 'S97 in S95 p. 77; S104 p. 62', 'S104', notes='Where Tarleton himself stood is not recorded: drawn behind the centre of his line.', start=(T('06:45'), T('07:55')))
for pid, a, show in (('CP132', 160, ('07:19', '07:22')), ('CP133', 255, ('07:28', '07:33')), ('CP134', 400, ('07:37', '07:46'))):
    P(pid, HQ, show, 'With the advancing line', 'On the Green River Road behind the line', at(a, 0), FRAME + '%d m up the road, behind the centre of the line. Not recorded.' % a, 'low', 150, 'S95; S97',
      'S97: "Lieutenant-colonel Tarleton thought the advance of the 71st into line, and a movement of cavalry in reserve to threaten the enemy\'s right flank, would put a victorious period into the action."', 'inferred', 'low', 'S97 in S95 p. 81', 'S95')
P('CP135', HQ, ('07:50', '07:52'), 'Rides back to bring on the Legion cavalry', 'With the reserve cavalry by the Green River Road', at(-100, 30), FRAME + 'With the reserve cavalry (CP111).', 'low', 200, 'S95; S97; S104',
  'S97: he sent orders to the cavalry "to form about four hundred yards to the right of the enemy, in order to check them, whilst he endeavoured to rally the infantry to protect the guns ... all attempts to restore order, recollection, or courage, proved fruitless."',
  'stated', 'low', 'S97 in S95 p. 84; S104 pp. 69-70', 'S104')
P('CP136', HQ, ('07:54', '07:57'), 'Last charge; crosses swords with Washington', 'On the Green River Road at the south-east end of the field', at(5, 5), FRAME + 'At that point: see CP36.', 'low', 150, 'S95; S97; S98; S105',
  'S95, p. 62: "Tarleton turned at bay several hundred yards away from the scene of triumph and surrender, and Washington and Tarleton crossed swords". S98 (Howard): "The third person, who Washington thinks was Tarleton, made a thrust at him which he parryed."',
  'stated', 'low', 'S95 pp. 62, 85; S98 in S95 p. 130; S105 (marker 13025)', 'S105; S98', notes='See CH12.')
P('CP137', HQ, ('08:24', '08:30'), 'Retreat down the Green River Road', 'Off the field to the south-east', COL_AT, 'On today\'s Green River Road (S39), where the column is first drawn (CP40): the way they had come.', 'low', 500, 'S95; S96; S104; S39',
  'S96: "Tarleton, with the small remains of his cavalry ... made their escape. He was pursued twenty-four miles". S104, p. 81: he crossed the Broad at Hamilton\'s Ford.', 'stated', 'low', 'S96 in S95 p. 124; S104 p. 81', 'S104', csrc='modern_map')

# ---------------------------------------------------------------- routes
def wp(pts): return '; '.join('%.5f, %.5f' % p for p in pts)
MODERN = [(35.11533, -81.78412), (35.11650, -81.78463), (35.11705, -81.78496), (35.11735, -81.78522), (35.11965, -81.78809), (35.12036, -81.78881), (35.12083, -81.78920), (35.12153, -81.78966), (35.12294, -81.79050)]   # today's Green River Road, its last 1,040 m (data/osm/cowpens.txt)
LINK = [(35.13132, -81.79743), (35.13162, -81.80223)]                                # the east trailhead (S39) and the east end of the old trace: a straight guess between the two roads
IN = MODERN + LINK + G.along(G.EAST, -200)[1:]                                          # along the old trace to 200 m short of the field
R_NOTE = 'Today\'s Green River Road to its north-west end, a straight guess across to the east end of the old trace at the park\'s east trailhead, then the Historic Green River Road as OpenStreetMap draws it (S39). The middle stretch is not known: CG06.'
ROUTES = [
    dict(route_id='RC01', unit_id='C-BR-TARL', kind='march', start=T('06:28'), end=T('06:58'), from_pos_id='CP40', to_pos_id=None, wps=IN, source_ids='S95; S97; S39',
         source_wording='S97: the troops "were directed to follow the route the Americans had taken the previous evening". S95, p. 45: the British "must come (northwest along Mill Gap Road)".', confidence='low', notes=R_NOTE, playback='yes'),
]
for rid, unit, f, t, kind, wording in (('RC02', 'C-BR-LEGC', 'CP111', 'CP112', 'escape', 'S97: "About two hundred dragoons forsook their leader, and left the field of battle."'),
                                       ('RC03', 'C-BR-OGIL', 'CP47', 'CP48', 'escape', 'S97: "About two hundred dragoons forsook their leader, and left the field of battle."'),
                                       ('RC04', 'C-BR-17', 'CP126', 'CP127', 'escape', 'S96: Tarleton "with the small remains of his cavalry ... made their escape."'),
                                       ('RC05', 'C-BR-HQ', 'CP136', 'CP137', 'escape', 'S96: Tarleton "with the small remains of his cavalry ... made their escape."'),
                                       ('RC06', 'C-US-WASH', 'CP36', 'CP37', 'pursuit', 'S96: "He was pursued twenty-four miles, but owing to our having taken a wrong trail at first, we could never overtake him."')):
    a0 = {'CP111': -115, 'CP47': 0, 'CP126': 0, 'CP136': 0, 'CP36': 0}[f]
    pts = G.along(G.EAST, a0)[::-1] + LINK[::-1][1:] + (MODERN[::-1][:1] if kind == 'pursuit' else MODERN[::-1])
    ROUTES.append(dict(route_id=rid, unit_id=unit, kind=kind, start=None, end=None, from_pos_id=f, to_pos_id=t, wps=pts, source_ids='S95; S96; S97; S39', source_wording=wording, confidence='low', notes=R_NOTE, playback='yes'))
ROUTES += [
    dict(route_id='RC07', unit_id='C-US-PICK', kind='withdrawal', start=T('07:31'), end=T('07:36'), from_pos_id='CP10', to_pos_id='CP15', wps=[at(330, -60), at(400, -170), at(520, -185), at(650, -120)], source_ids='S95; S96; S98',
         source_wording='S95, p. 56: "they streamed around both flanks but mostly around the left". S98: "The militia fell into our rear".', confidence='low', notes='Round the left of Howard\'s line, clear of its front. Drawn as one body; part went round the right (CH09).', playback='yes'),
    dict(route_id='RC08', unit_id='C-US-PICK', kind='attack', start=T('07:44'), end=T('07:50'), from_pos_id='CP15', to_pos_id='CP16', wps=[at(650, -120), at(665, 40), at(625, 215), at(520, 248)], source_ids='S95; S98',
         source_wording='S95, p. 60: the militia "regrouped behind the Continental Line, appeared on the American right, sweeping around behind the other British flank."', confidence='low', notes='Behind Howard\'s second position and round its right. The staff ride\'s map 14 shows the sweep; the path is an estimate.', playback='yes'),
    dict(route_id='RC09', unit_id='C-BR-17', kind='attack', start=T('07:31'), end=T('07:34'), from_pos_id='CP123', to_pos_id='CP124', wps=[at(290, -225), at(430, -250), at(600, -250)], source_ids='S95; S98',
         source_wording='S98: "a large body of british cavalry passes round my left flank and pursued the flying militia to their horses."', confidence='low', notes='Round the left of Howard\'s line (115 m from the road as placed).', playback='yes'),
    dict(route_id='RC10', unit_id='C-US-WASH', kind='attack', start=T('07:46'), end=T('07:49'), from_pos_id='CP34', to_pos_id='CP35', wps=[at(625, -150), at(545, -240), at(440, -160), at(410, -40)], source_ids='S95; S101',
         source_wording='S101 (Young): "making a sort of circuit at full speed, came up in the rear of the British line".', confidence='low', notes='Past the left of Howard\'s line and in behind the British right, as on the staff ride\'s map 14.', playback='yes'),
    dict(route_id='RC11', unit_id='C-BR-71', kind='attack', start=T('07:35'), end=T('07:39'), from_pos_id='CP101', to_pos_id='CP102', wps=[at(-67, 115), at(150, 215), at(440, 200)], source_ids='S95; S97',
         source_wording='S97: "The 71st were desired to pass the 7th before they gave their fire, and were directed not to entangle their right flank with the left of the other battalion."', confidence='low', notes='Up the south-west side of the field, outside the left of the 7th.', playback='yes'),
]

# ---------------------------------------------------------------- events
EVENTS = [
    ('CE01', '06:00', '06:30', 'Morgan forms for battle', 'About an hour before daylight a scout reports Tarleton within five miles. Morgan turns his men out and puts them in three lines across the Green River Road: riflemen in front, Pickens\'s militia behind them, and Howard\'s Continentals and Virginians on the rise behind, with Washington\'s cavalry in reserve.', 'CP01', 'S95; S96; S100', 'name', '06:05', None),
    ('CE02', '06:30', '07:00', 'The pickets are driven in', 'About day, Tarleton\'s advance guard of Legion dragoons drives in Capt. Inman\'s mounted pickets on the Green River Road and finds the Americans drawn up to fight.', 'CP41', 'S95; S97; S101; S104', 'name', '06:46', 'Pickets driven in'),
    ('CE03', '06:50', '08:00', 'Tarleton deploys', 'The British come out of the woods and form one line in sight of the Americans: light infantry on the right, the Legion infantry in the centre, the 7th Fusiliers on the left, a 3-pounder in each gap and fifty dragoons on each flank. The 71st Highlanders and about 200 Legion cavalry stand in reserve 150 yards back.', 'CP51; CP61; CP71; CP81; CP91; CP101; CP111; CP121; CP131', 'S95; S96; S97; S100', 'name', '06:58', None),
    ('CE04', '07:00', '08:05', 'First shots', 'Tarleton sends Ogilvie\'s Legion dragoons to drive in the riflemen in front. The riflemen fire from behind the trees and the dragoons come back with empty saddles. Militia veterans gave John Savage of Brandon\'s regiment the first shot.', 'CP42; CP05; CP06', 'S95; S101; S104; S105; S106', 'name', '07:03', None),
    ('CE05', '07:10', '08:10', 'The British line advances', 'About sunrise the two guns open and the whole line comes on with three cheers. Morgan answers along the militia line: "They gave us the British halloo, boys, give them the Indian halloo."', 'CP52; CP62; CP72; CP82; CP92', 'S95; S96; S100; S101', 'name', '07:12', 'The line advances'),
    ('CE06', '07:20', '08:20', 'The skirmishers fall back', 'McDowell\'s and Cunningham\'s riflemen, having picked off officers at long range, fall back on Pickens\'s line.', 'CP07; CP08; CP52; CP62; CP72', 'S95; S96; S100', 'name', '07:21', None),
    ('CE07', '07:28', '08:30', 'The militia volleys', 'Pickens\'s militia hold their fire until the British are within killing distance, then fire by regiments: "pop, pop, pop, and then a whole volley". The British line halts to dress and comes on again.', 'CP10; CP53; CP63; CP73', 'S95; S96; S100; S101; S105', 'name', '07:29', None),
    ('CE08', '07:31', '08:36', 'The militia withdraw; dragoons ride them down', 'As ordered, the militia file off round Howard\'s line, most of them round its left, to re-form in rear. The 17th Light Dragoons on Tarleton\'s right charge after them towards their horses; Washington\'s cavalry strikes the dragoons and drives them back.', 'CP15; CP124; CP33', 'S95; S96; S98; S101; S104', 'name', '07:34', 'Militia withdraw'),
    ('CE09', '07:37', '08:41', 'Line against line', 'The British infantry close on Howard\'s line and the two fire at close range, neither giving way. Tarleton orders up the 71st on his left to turn Howard\'s right, and the reserve cavalry to follow it; the cavalry does not come.', 'CP20; CP54; CP64; CP74; CP102', 'S95; S97; S98; S100', 'name', '07:38', None),
    ('CE10', '07:39', '08:42', 'Howard\'s line falls back', 'Howard orders his right company to face the Highlanders. The order goes wrong; the company faces about, and the rest of the line, taking it for a retreat, marches to the rear in good order. Morgan picks the ground for it to halt, about 80 to 100 yards back.', 'CP24; CP03; CP103', 'S95; S96; S98; S101', 'name', '07:40', 'Howard falls back'),
    ('CE11', '07:45', '08:46', 'Face about: volley and bayonet', 'The British, sure the day is won, rush on out of order. At 10 to 30 yards Howard\'s line faces about and fires; then it charges with the bayonet. The British line stops, breaks and runs.', 'CP24; CP55; CP65; CP75; CP103', 'S95; S96; S97; S98; S100', 'name', '07:45', 'Volley and bayonet'),
    ('CE12', '07:50', '08:52', 'Double envelopment', 'Washington\'s cavalry rides round the British right and into their rear; Pickens\'s militia come back into the fight round the American right, onto the 71st. The infantry throw down their arms. The gunners fight to the last by their two 3-pounders, which are taken.', 'CP28; CP35; CP16; CP56; CP66; CP76; CP104; CP85; CP95', 'S95; S96; S98; S101; S105', 'name', '07:50', None),
    ('CE13', '07:54', '09:00', 'Tarleton\'s last charge', 'The Legion cavalry will not charge and about 200 of them leave the field. Tarleton leads some fifty horsemen, most of them of the 17th Light Dragoons, at the American cavalry and is beaten off; he and Washington cross swords before he rides away down the Green River Road.', 'CP136; CP126; CP36; CP112', 'S95; S96; S97; S98; S105', 'name', '07:55', None),
    ('CE14', '08:00', '09:00', 'Pursuit', 'Washington and Pickens follow Tarleton for 22 to 24 miles without catching him; the British burn most of their baggage. Morgan counts over 500 prisoners, two guns and two colours for 12 killed and about 60 wounded, and marches off the field the same day to get the prisoners away from Cornwallis.', 'CP37; CP137; CP04', 'S95; S96; S104', 'name', '08:08', None),
]

# ---------------------------------------------------------------- hypotheses
def H(hid, q, a, b, c, ev_for, ev_against, adopted, because, conf, rows, srcs, nxt):
    return dict(hypothesis_id=hid, battle_id=BATTLE, question=q, reading_a=a, reading_b=b, reading_c=c, evidence_for=ev_for, evidence_against=ev_against, adopted_reading=adopted, adopted_because=because,
                confidence=conf, status='Proposed', decided_by='Claude (pilot default); Morgan to confirm', decided_on=TODAY, reviewed_on=None, rows=rows, source_ids=srcs, next_step=nxt, history='New on 23 Nov 2026 with the Cowpens rows.')


HYP = [
    H('CH01', 'At what hour did the fighting begin?', 'About sunrise, 07:00 to 07:10', 'About 08:00', 'Mid-morning (10 or 11 o\'clock)',
      'S96 Morgan, in S95 p. 122: "about sunrise".\nS100 Anderson, in S95 p. 140: "about Sunrise they began the attack".\nS100 Seymour, in S95 p. 141: "about seven o\'clock in the morning".\nS101 Neel, in S95 p. 144: "stood in ranks till Sun rise, at which time the battle commenced".\nS95 p. 67 n. 28: sunrise at 0707 (U.S. Naval Observatory); maps 8 to 14 run 0700 to 0750.\nS104 p. 85: the British "advanced at sunrise".',
      'S103 p. 65: "The British deployment being completed at about 8 o\'clock, Tarleton ordered his troops to attack."\nS95 p. 51: "No evidence remains of the time the engagement began."\nS101 Wells, in S95 p. 147: "about 10 or 11 Oclock A. M." (the handbook calls his account fanciful).',
      'A', 'Five eyewitnesses say sunrise and one gives the clock; the staff ride\'s maps are built on it. Every row keeps an hour\'s range for reading B.', 'medium', 'CP05; CP10; CP20; CP51; CE04; CE05', 'S95; S96; S100; S101; S103; S104',
      'Find what the 1928 study rests its 8 o\'clock on (Cornwallis\'s dispatch?). Read Babits on the timing.'),
    H('CH02', 'How long did the action last?', 'About 50 minutes ("less than an hour")', 'About an hour and forty minutes', None,
      'S95 maps 8 to 14: 0700 to 0750, and "Not yet nine o\'clock" (p. 62).\nS103 p. 66: "the action having lasted about 50 minutes".\nS104 p. 85: "In less than an hour".\nS105 marker 13030: "In less than an hour".',
      'S101 Thomas, in S95 p. 145: "The shot & firing continued about an hour and forty minutes".\nS100 Seymour, in S95 p. 141: "continued till late in the afternoon" (the pursuit).',
      'A', 'Three studies agree, and the distances are short. Thomas may count from the first shots at the pickets.', 'medium', 'CE12; CE13', 'S95; S100; S101; S103; S104; S105', 'None.'),
    H('CH03', 'How many men did Morgan have?', 'About 800 to 830', 'About 1,100', 'About 1,900 to 2,000',
      'S96 Morgan, in S95 p. 124: "We fought only eight hundred men, two-thirds of which were militia."\nS104, opening of the narrative (seen in the Project Gutenberg text; the text of the Archive scan has lost the line): "some 830 soldiers - 320 seasoned Continentals, a troop of light dragoons, and the rest militia".\nS95 pp. 92-94: Howard 350, Pickens 650, cavalry 117 (1,117).',
      'S97 Tarleton, in S95 p. 77: a front line of about 1,000 militia, 500 Continentals, 120 cavalry and 300 backwoodsmen.\nThe NPS administrative history of the park reports that Babits, from the pension files, puts Morgan at about 2,000 (seen in a search extract only; Babits not read).',
      'No figure adopted: the staff ride\'s chart (B) is shown unit by unit, with Morgan\'s own total on his row', 'The sources read cannot settle it, and the playback does not depend on it. Frontages are drawn from the ground (200 yards for Howard, the width of the field for Pickens), not from numbers.', 'low',
      'CP10; CP20', 'S95; S96; S97; S104', 'Read Babits, A Devil of a Whipping (SC-SOU09), and Bearss (SC-SOU03).'),
    H('CH04', 'How many men did Tarleton have?', 'About 1,050 to 1,150', 'About 1,300', None,
      'S95 p. 91: 1,126 by unit.\nS96 Morgan, in S95 p. 124: "not less than one thousand one hundred and fifty" with the baggage guard; "Their own officers confess that they fought one thousand and thirty-seven."\nS104 p. 53: about 350 horsemen in some 1,100.',
      'S100 Seymour, in S95 p. 141: "thirteen hundred in the field of their best troops".\nS95 p. 91 nn. 1, 3: the returns of 15 January show 451 in the Legion and 249 in the 71st, more than the chart gives.',
      'A', 'The unit figures of the staff ride are used on each unit\'s row.', 'medium', 'CP51; CP61; CP71; CP101', 'S95; S96; S100; S104', 'None.'),
    H('CH05', 'Which half of the skirmish line was on the right?', 'McDowell (North Carolina) on the right, Cunningham (Georgia) on the left', 'Cunningham on the right, McDowell on the left', None,
      'S96 Morgan, in S95 p. 123: "Maj. McDowail ... was posted on the right flank in front of the line ... and Maj. Cunningham ... on the left".\nS103 p. 64 follows Morgan.',
      'S99 Hammond, in S95 p. 132: "Colonel Cunningham will take post on the right, Major McDowal on the left of the line, southwest of the road ... Major Hammond will take post on the left of the road".\nS95 p. 50 accepts Hammond for the skirmish line, "as his account is so detailed, and he was actually among them".',
      'A for rows CP05 and CP06', 'Morgan wrote two days after; Hammond\'s notes were printed seventy years later. But the staff ride prefers Hammond, and this could as well go the other way.', 'low', 'CP05; CP06; CP07; CP08', 'S95; S96; S99; S103',
      'Morgan to decide. Babits may settle it from the pension files.'),
    H('CH06', 'Where did the Virginia militia stand in the main line?', 'Triplett and Tate on the left, Wallace on the right', 'Tate (with Buchanan) on the right', 'Triplett on the right',
      'S98 Howard, in S95 p. 126: "I am positive that Triplett and Tate were on my left."\nS95 p. 50: "Howard was certainly in a better position to know".',
      'S96 Morgan, in S95 p. 123: "Capts. Tate and Buchanan, with the Augusta riflemen, to support the right of the line."\nS99 Hammond, in S95 p. 132: "The Virginia militia, commanded by Major Triplet ... will form to the right of the second line".\nS101 Neel, in S95 p. 144: "the Militia on the right of the Regulars".',
      'A', 'The commander of the line says he is positive, and the staff ride follows him.', 'medium', 'CP21; CP22; CP23', 'S95; S96; S98; S99; S101', 'None.'),
    H('CH07', 'How far in front of Howard was the militia line, and where is it on the ground?', '150 yards in front; about 330 m up the road from the trail end', '200 yards in front; 275 m up the road (the NPS wayside)', '150 m in front of a line 500 m up the road, but 400 m by the staff ride\'s own paces',
      'S101 McJunkin, in S95 p. 133: "at the distance of 150 yards".\nS104 p. 55: "about 150 yards ahead of Howard".\nS95 p. 75: "about 150 meters in front of the Continental Line".',
      'S100 Seymour, in S95 p. 141: "advanced about two hundred yards".\nS101 Thomas, in S95 p. 145: the riflemen "200 yards to the front".\nS105 marker 77693, about 275 m up the road: "The American second line of defense stood in position here."\nS95 p. 78: the militia line 200 m beyond the skirmish line, that is 400 m from Vantage 6.',
      'A', 'It keeps the 150 yards most accounts give, measured from a main line fixed by the monument, and falls between the two places given on the ground.', 'low', 'CP10; CP11; CP12; CP13; CP14', 'S95; S100; S101; S104; S105',
      'Bearss\'s troop movement maps (SC-SOU03); a visit with a GPS, or the park\'s own GIS.'),
    H('CH08', 'How far did Howard\'s line fall back?', 'About fifty paces', 'About 80 yards', 'About 100 yards',
      'S101 Thomas, in S95 p. 145: "They retreated from aboutt 80 yards".\nS98 Howard, in S95 p. 128: "to retreat to Washington\'s horse about 100 yards".\nS95 p. 58: "80 to 100 yards to the rear"; p. 82: 100 m.',
      'S96 Morgan, in S95 p. 123: "We retired in good order about fifty paces".', 'B to C: 85 m', 'Howard led the line and Thomas was in it; the bend in the road, where the NPS handbook puts the deciding fight, is 85 m behind the first position.', 'medium', 'CP24; CP25; CP26; CP27', 'S95; S96; S98; S101; S104', 'None.'),
    H('CH09', 'Which way did the militia go off?', 'Round the left of Howard\'s line', 'Round both flanks', 'Through or round the right',
      'S95 p. 56: "they streamed around both flanks but mostly around the left".\nS98 Howard, in S95 p. 129: the horses were "in the rear of my left flank", and the dragoons that chased the militia passed "round my left flank".',
      'S101 Baldwin, in S95 p. 144: "to divide to the right & left & form in the rear".\nS101 Thomas, in S95 p. 145: they "broke in the centre and flanked the right and left of the musquetry".\nS98 Howard, in S95 p. 128: "part of them fell into the rear of my right flank".\nS105 marker 13065: they "funneled back though the Continental line".',
      'A, drawn as one body', 'One symbol cannot go both ways; the larger part and the cavalry fight were on the left. The text of the event says "most of them".', 'low', 'CP15; RC07', 'S95; S98; S101; S105', 'Split Pickens\'s line into two symbols if the pension files give the regiments by flank.'),
    H('CH10', 'When and where did the cavalry fight?', 'Two fights: Washington beats the 17th Light Dragoons behind the American left as the militia withdraw, then rides round the British right at the end', 'One fight, at the moment of the bayonet charge', 'A British charge on the American right as well',
      'S101 Simmons, in S95 p. 143: a first charge on the cavalry cutting down the militia, a third on the right wing of their infantry, a fourth in pursuit.\nS96 Morgan, in S95 p. 123: Washington charged those "cutting down our riflemen on the left".\nS95 pp. 56, 60 and maps 11, 14.\nS101 Young, in S95 p. 136: "the cavalry was twice, during the action, between our army and the enemy".',
      'S98 Howard, in S95 p. 129: "this charge was made at the same moment that I charged the infantry".\nS101 Young, in S95 p. 137: "the British cavalry had charged the American right" (perhaps Ogilvie\'s troop from the British left).',
      'A', 'Simmons rode in it and the staff ride follows him. Ogilvie\'s troop is kept on the British left without a charge of its own, since only Young has one.', 'low', 'CP33; CP35; CP124; CP46', 'S95; S96; S98; S101', 'Read Babits on Ogilvie\'s charge.'),
    H('CH11', 'Who brought the militia back into the fight?', 'Morgan', 'Pickens, on his own', 'It is not known',
      'S101 Collins (S95 p. 60): Morgan rode among the militia: "Form, form, my brave fellows! give them one more fire and the day is ours."\nS95 p. 83: "Morgan is the most likely source for the order."',
      'S95 p. 60: "We must conclude that the return of the militia was the consequence of the initiative of a commander - which one, we may never know."\nS95 p. 69 n. 49: Bailey and Waring credit Pickens.',
      'C: the event text names no one', 'The staff ride itself leaves it open.', 'low', 'CP16; CE12', 'S95; S101', 'None.'),
    H('CH12', 'What happened between Washington and Tarleton at the end?', 'Three British officers attacked Washington, who was saved by a sergeant and by his young servant\'s pistol; Tarleton fired and rode off', 'Tarleton with fourteen officers and forty men drove Washington\'s horse back', None,
      'S98 Howard, in S95 pp. 129-130, from Washington himself.\nS105 marker 13025.\nS95 p. 62.',
      'S97 Tarleton, as Howard quotes him (S95 p. 130): "14 officers & 40 men charged Washington\'s horse and drove them back". Howard: "This is not correct. This affair checked Washington\'s pursuit, but he did not fall back."\nS101 Kelley, in S95 p. 143: Washington "disabled Tarltons fingers" (hearsay).',
      'A, at the south-east end of the field', 'Both sides agree there was a last clash of horse; where is given only by the NPS wayside ("Nearby").', 'low', 'CP36; CP126; CP136; CE13', 'S95; S97; S98; S101; S105', 'None.'),
    H('CH13', 'When did Tarleton march?', '03:00', '02:00', None, 'S97 Tarleton, in S95 p. 147: "at three o\'clock in the morning".\nS103 p. 65: "broke camp at 3 o\'clock".',
      'S102 Mackenzie, in S95 p. 152: "The pursuit re-commenced by two o\'clock the next morning".', 'A', 'The commander\'s own hour; the march is off the map either way.', 'medium', 'CP40', 'S95; S97; S102; S103', 'None.'),
    H('CH14', 'Did Tarleton attack before his line was formed?', 'No: he formed with care', 'Yes: the 7th was not fully formed and the reserve not clear of the woods', 'He halted nearly half an hour first',
      'S97 Tarleton, in S95 pp. 77-78: the deployment step by step, "the animation of the officers and the alacrity of the soldiers".\nS100 Anderson, in S95 p. 140: the British "Halted and Form\'d the Line in Full View ... We look\'d at each other for a Considerable time".',
      'S102 Mackenzie (S95 pp. 51-52, 58, 68 n. 33): a hurried onrush; the reserve not yet out of the Thicketty Creek underbrush.\nS105 marker 13423: "Tarleton initiated the battle before they were completely deployed."\nHanger (S95 p. 52): Tarleton halted the troops "near half an hour".',
      'A for the map; B noted on the rows of the 7th and the 71st', 'The playback shows the line complete at 0700, as the staff ride\'s map 8 does. An American officer in the line saw a long pause.', 'low', 'CP71; CP101', 'S95; S97; S100; S102; S105', 'None.'),
    H('CH15', 'In what order did the British line stand?', 'Light infantry on the right, Legion infantry in the centre, the 7th on the left; the 71st in reserve behind the left', 'The 71st opposite the American right, the 7th opposite the American left, the Legion in the centre, light companies on both flanks', None,
      'S97 Tarleton, in S95 pp. 77-78: the light infantry filed to the right, the Legion infantry "added to their left", the 7th "upon the left of the legion infantry", the 71st 150 yards in rear and a little to the left.\nS95 p. 76 and map 8; S104 p. 63; S105 marker 13423 (the 7th on the south-west side of the road).',
      'S96 Morgan, in S95 p. 123: "The first battalion of the 71st regiment was opposed to our right, the 7th regiment to our left, the infantry of the legion to our centre, the light companies on our flanks."',
      'A', 'Tarleton formed the line. Morgan saw it from the far side through open woods; his 71st "opposed to our right" fits where the 71st came into the fight later.', 'medium', 'CP51; CP61; CP71; CP101', 'S95; S96; S97; S104; S105', 'None.'),
]

GAPS = [
    ('CG01', 'Bearss\'s troop movement maps have not been read', 'Edwin C. Bearss, The Battle of Cowpens: A Documented Narrative and Troop Movement Maps (National Park Service, 1967) is the one study that draws every unit on a surveyed base. The PDF is on Morgan\'s Mac; the folder was not connected on 23 Nov 2026 and the online copies could not be reached. Every position therefore rests on distances given in words, laid along today\'s road.', 'Connect the WarMapper folder (or attach battle-of-cowpens.pdf), read the maps, and compare each line with its row.'),
    ('CG02', 'No period or park map is under the units', 'The staff ride\'s maps 8 to 14 (S95) are a U.S. Army work and could be hosted, but their troop symbols are two to three times too large for their own scale bar and a move of 80 to 100 yards is drawn as 500: fitted to the ground they would contradict the rows. The 1928 Army War College sketch (SC-SOU08) and the park\'s battle map (SC-SOU06) could not be fetched as pictures. The playback opens on today\'s topographic map, as the landing rule says when no period map covers the view.', 'Fetch the 1928 sketch (public domain) and the park map; fit whichever is to scale; add it as a base.'),
    ('CG03', 'Three readings are not done', 'Ward, The War of the Revolution, chapters 68-69 (S92, the class reading) was not supplied. Babits, A Devil of a Whipping (SC-SOU09), the standard modern study, is in copyright and was not read. American Military History, pp. 96-98 (S87) was read in session 1 for its pages only and has not been checked against these rows.', 'Morgan to attach war_cowpens.pdf; read AMH pp. 96-98 from the PDF in Historical Info.'),
    ('CG04', 'The clock is a reconstruction', 'One eyewitness gives one clock time ("about seven o\'clock"); the rest say sunrise. The minute-by-minute times are the staff ride\'s (0700 to 0750) with the steps between them spaced by eye. The order of events is sound; any single time could be 10 minutes out within the hour, and the whole hour could be an hour later (CH01).', 'None: say so on the page (done, in the time note and About).'),
    ('CG05', 'The monument and the waysides are placed to about 50 m', 'OpenStreetMap puts the Washington Light Infantry monument at 35.13502, -81.81488, on the trail; the Historical Marker Database puts it 125 m to the south-east. OpenStreetMap is followed because the trail turns at that point. The wayside coordinates come from the same database.', 'A visit with a GPS, or the park\'s GIS data (NPS IRMA).'),
    ('CG06', 'Tarleton\'s road south-east of the park is a guess', 'The old trace ends at the park\'s east trailhead. Today\'s Green River Road is taken as its continuation towards Thicketty Creek, and the 900 m between the two is a straight line. The column\'s place at 06:20 is an estimate too.', 'A county road map of the 19th century (Mills\'s Atlas, 1825, Spartanburgh District) or Bearss\'s historic base map.'),
    ('CG07', 'Shares of each line are apportioned, and four units are not placed', 'The stretch each militia regiment and each part of Howard\'s and Tarleton\'s lines held is its share by strength or an even split, not a source\'s statement. Roebuck\'s battalion, Kirkwood\'s company and the baggage guard are in the order of battle but not on the map; Inman\'s pickets are named in the events only.', 'Babits and Bearss.'),
    ('CG08', 'First editions not checked', 'Morgan\'s report, Tarleton, Howard, Hammond, Mackenzie and the memoirs are cited by the page of the staff ride that prints them (S95), not by the page of their first printing.', 'Check Tarleton (1787) and Graham (1856) on the Internet Archive; both texts are there.'),
]

# ---------------------------------------------------------------- playback
OPENING = ('Before daylight on 17 January 1781. Daniel Morgan\'s detachment is in camp at the Cowpens, a well-known pasture ground on the Green River Road. Banastre Tarleton, sent by Cornwallis to destroy it, '
           'has been marching since three in the morning and is five miles off. Morgan has chosen to stand here. Press play: the units come onto the map as they form.')
PLAYBACK = dict(playback_id=PB, battle_file_id='cowpens-1781', campaign_id=CAMP, record_battles=BATTLE, title='Battle of Cowpens, 17 January 1781', subtitle='Morgan\'s three lines and the double envelopment of Tarleton',
                time_unit='minute', time_zero='1781-01-17 00:00', time_start=T('06:00'), time_end=T('08:30'), focus_start=T('06:55'), focus_end=T('08:05'), calendar_first=DAY, days_numbered='no', calendar_days=1,
                origin_lat=35.1345, origin_lon=-81.8135, west=-81.8300, south=35.1130, east=-81.7800, north=35.1450, opening_label='Before daylight', opening_text=OPENING)
USGS = 'https://basemap.nationalmap.gov/arcgis/rest/services/'
SETTINGS = [
    ('page_title', 'Battle of Cowpens (1781) Playback', None), ('clock_title', 'Cowpens', None), ('style', 'tactical', None), ('scale_bar', 'yards', None), ('rate', 1, 'Minutes a second the page opens at'),
    ('lead.share', 0.2, 'The forming-up before 06:55 takes this share of the timeline'), ('lead.rate', 4, None), ('lead.step', 5, None),
    ('time_note.from', '1781-01-17T06:00', None), ('time_note.text', 'Times are estimates', 'The clock is the staff ride\'s reconstruction: see CH01 and CG04'),
    ('sides.CR.short', 'British', 'This playback\'s own name for the side (the war\'s Sides row says "Hessian and British", for Trenton)'),
    ('sides.CR.name', 'British Crown forces (British regulars and Loyalist provincials)', None),
    ('follow.min', '[620, 460]', 'Smallest box the camera frames, metres'), ('follow.margin', 70, None), ('follow.empty', 'field', None), ('follow.lookahead', 12, 'Minutes ahead the camera looks'),
    ('preset.field', '[-81.8205, 35.1298, -81.8055, 35.1392]', 'A named view: [west, south, east, north]'), ('preset.approach', '[-81.8300, 35.1130, -81.7800, 35.1450]', None),
    ('views.1.preset', 'field', 'Named views'), ('views.1.label', 'The battlefield', None), ('views.1.short', 'Field', None),
    ('views.2.preset', 'approach', None), ('views.2.label', 'Tarleton\'s approach', None), ('views.2.short', 'Approach', None),
    ('bases.1.id', 'mod', None), ('bases.1.label', 'Current map', None), ('bases.1.short', 'Today', None), ('bases.1.current', True, None),
    ('bases.2.id', 'sat', None), ('bases.2.label', 'Satellite', None), ('bases.2.short', 'Sat', None), ('bases.2.title', 'Aerial photography of the ground today, from the USGS (M switches maps)', None),
    ('bases.2.imagery.tiles', USGS + 'USGSImageryOnly/MapServer/tile/{z}/{y}/{x}', None), ('bases.2.imagery.max_zoom', 16, None), ('bases.2.imagery.credit', 'USDA, USGS The National Map: Orthoimagery', None),
    ('bases.2.imagery.name', 'Aerial photography (USGS)', None),
    ('bases.2.imagery.about', 'Today\'s ground from the air: photography from the US Department of Agriculture\'s National Agriculture Imagery Program (about 1 m detail), served free by the USGS National Map. The field is kept open by the National Park Service much as it was in 1781; the woods around it are thicker than the open wood of the battle.', None),
    ('bases.2.imagery.rights', 'Public domain (US government work)', None), ('bases.2.imagery.link', USGS + 'USGSImageryOnly/MapServer', None),
    ('modern.tiles', USGS + 'USGSTopo/MapServer/tile/{z}/{y}/{x}', None), ('modern.max_zoom', 16, None), ('modern.credit', 'USGS The National Map', None), ('modern.name', 'USGS Topo base map', None),
    ('modern.about', 'Today\'s ground: the US Geological Survey\'s topographic base map, with roads, streams, contours and hill shading. It is streamed from the USGS while it is on screen, so it needs a connection. No map of the time shows this ground: see the About text.', None),
    ('modern.rights', 'Public domain (US government work)', None), ('modern.link', USGS + 'USGSTopo/MapServer', None), ('modern.reach', 3, None),
    ('zoom.max', 8, 'Closest zoom, screen pixels per metre'), ('zoom.min_factor', 0.9, None), ('zoom.follow_max', 2.4, None), ('zoom.fold', 0.45, 'Zoomed in past this, Pickens\'s and Howard\'s lines are shown by their parts'),
    ('zoom.labels', 0.3, None), ('zoom.landmarks_from', 0.25, None),
    ('fold.label', 'Regiments and companies', None),
    ('arrows.on', True, 'Arrows ahead of a move'), ('arrows.min_km', 0.25, 'Moves shorter than this get no arrow. The whole field is half a mile long, so the limit is far below the 20 km of a campaign'), ('arrows.lead', 3, 'Minutes before the unit sets off that the arrow appears'),
    ('trails.on', True, 'Routes taken: the way a unit has come is drawn behind it'), ('trails.opacity', 0.5, None), ('trails.fade_after', 6, None), ('trails.fade_over', 6, None),
    ('rules.blend', 2, 'Minutes over which a unit shifts from one row to the next when they meet'),
    ('rear.side', 'US', 'Symbols sit behind their own lines: the American rear is up the road to the north-west'), ('rear.lat', 35.1410), ('rear.lon', -81.8188),
    ('question_mark', 'overall', None),
    ('texts.stated', 'A report, an eyewitness, the Army\'s staff ride or a National Park Service wayside puts the unit here.', None),
    ('texts.inferred', 'Worked out from the sequence of events and from where its line stood; no source names this unit at this spot.', None),
    ('texts.moving', 'No source records this stretch. The unit is drawn moving between two recorded positions.', None),
    ('found.derived', 'placed by a distance the sources give, measured along the Green River Road on today\'s map', None),
    ('found.modern_map', 'a point on today\'s road map', None),
    ('about.1', 'Unit positions come from the Revolutionary War workbook (the Cowpens rows), built from Morgan\'s report, Tarleton\'s and Howard\'s accounts, the journals and memoirs of men in the ranks, the Army\'s 1996 staff ride handbook, the Army War College study of 1928 and the National Park Service\'s handbook and waysides. Nothing here has been checked by a historian.', None),
    ('about.2', 'No map made at the time shows this ground, and the accounts give distances, not places. Every unit is therefore placed by distance along the Green River Road, which still crosses the field, counted from the spot where Tarleton\'s column came out of the woods. Lines may be 50 to 100 m from where they really stood; none is rated better than medium.', None),
    ('about.3', 'The clock follows the staff ride\'s maps: first shots about 07:00, the end about 07:50. Eyewitnesses say only "about sunrise", which was at 07:07; one Army study puts everything an hour later. Tap a unit to see the range of times its record allows.', None),
    ('about.4', 'Solid symbols are positions a source gives. Dashed symbols are worked out or are the last position on record. A question mark means the place is doubtful.', None),
    ('about.5', 'Symbols are blue for the Americans and red for the British and Loyalist troops. Zoom in to see Pickens\'s line by its regiments and Howard\'s by its parts.', None),
    ('about.6', 'The current map is the US Geological Survey\'s topographic map, and Satellite its aerial photography, both streamed from the USGS. If they cannot be reached, a simplified drawing of OpenStreetMap roads and streams is shown instead.', None),
    ('about.7', 'Where the sources disagree (the hour, the numbers, which riflemen were on the right, how far Howard fell back, who brought the militia back), the workbook\'s Hypotheses sheet gives each reading and says which one the playback follows.', None),
]
NATIONS = [('United States', 'American'), ('Great Britain', 'British'), ('Loyalist', 'Loyalist (provincial)')]
ST = T('06:12')
# track_id, unit, rows, part_of, hide_after, loose, nudge, starts_from_row, starts_at, start_route
TRACKS = [
    ('C-US-MORGAN', 'C-US-MORGAN', 'CP01', None, 'yes', None, None, None, None, None),
    ('C-US-HQ', 'C-US-HQ', 'CP02; CP03; CP04', None, None, None, '0, -24', 'CP01', ST, None),
    ('C-US-MCD', 'C-US-MCD', 'CP05; CP07', None, 'yes', 'yes', None, 'CP01', ST, None),
    ('C-US-CUN', 'C-US-CUN', 'CP06; CP08', None, 'yes', 'yes', None, 'CP01', ST, None),
    ('C-US-PICK', 'C-US-PICK', 'CP10; CP15; CP16', None, None, None, None, 'CP01', ST, None),
    ('C-US-BRAN', 'C-US-BRAN', 'CP11', 'C-US-PICK', 'yes', None, None, None, None, None),
    ('C-US-THOM', 'C-US-THOM', 'CP12', 'C-US-PICK', 'yes', None, None, None, None, None),
    ('C-US-HAYS', 'C-US-HAYS', 'CP13', 'C-US-PICK', 'yes', None, None, None, None, None),
    ('C-US-MCC', 'C-US-MCC', 'CP14', 'C-US-PICK', 'yes', None, None, None, None, None),
    ('C-US-HOW', 'C-US-HOW', 'CP20; CP24; CP28', None, None, None, None, 'CP01', ST, None),
    ('C-US-WALL', 'C-US-WALL', 'CP21; CP25; CP29', 'C-US-HOW', None, None, None, None, None, None),
    ('C-US-MDDE', 'C-US-MDDE', 'CP22; CP26; CP30', 'C-US-HOW', None, None, None, None, None, None),
    ('C-US-TRIP', 'C-US-TRIP', 'CP23; CP27; CP31', 'C-US-HOW', None, None, None, None, None, None),
    ('C-US-WASH', 'C-US-WASH', 'CP32; CP33; CP34; CP35; CP36; CP37', None, None, None, None, 'CP01', ST, None),
    ('C-BR-TARL', 'C-BR-TARL', 'CP40', None, 'yes', None, None, None, None, None),
    ('C-BR-OGIL', 'C-BR-OGIL', 'CP41; CP42; CP43; CP44; CP45; CP46; CP47; CP48', None, None, None, None, 'CP40', T('06:22'), 'RC01'),
    ('C-BR-HQ', 'C-BR-HQ', 'CP131; CP132; CP133; CP134; CP135; CP136; CP137', None, None, None, '0, 24', 'CP40', T('06:28'), 'RC01'),
    ('C-BR-LI', 'C-BR-LI', 'CP51; CP52; CP53; CP54; CP55; CP56', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-LEGI', 'C-BR-LEGI', 'CP61; CP62; CP63; CP64; CP65; CP66', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-7', 'C-BR-7', 'CP71; CP72; CP73; CP74; CP75; CP76', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-RA1', 'C-BR-RA1', 'CP81; CP82; CP83; CP84; CP85', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-RA2', 'C-BR-RA2', 'CP91; CP92; CP93; CP94; CP95', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-71', 'C-BR-71', 'CP101; CP102; CP103; CP104', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-LEGC', 'C-BR-LEGC', 'CP111; CP112', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
    ('C-BR-17', 'C-BR-17', 'CP121; CP122; CP123; CP124; CP125; CP126; CP127', None, None, None, None, 'CP40', T('06:28'), 'RC01'),
]
# text, other name, lat, lon, angle, level, kind, show, approximate
LABELS = [
    ('Green River Road', 'Mill Gap Road', 35.13352, -81.81145, 28, 0, 'road', None, None),
    ('Green River Road', 'Mill Gap Road', 35.13830, -81.81690, 60, 1, 'road', None, None),
    ('Washington Light Infantry monument (1856)', None, 35.135021, -81.814875, None, 0, 'landmark', None, None),
    ('U.S. Monument (1932) and visitor centre', None, 35.136816, -81.818138, None, 1, 'landmark', None, None),
    ('Morgan\'s camp, night of 16 January', None, CAMP_AT[0], CAMP_AT[1], None, 1, 'place', None, 'yes'),
    ('Head of Tarleton\'s column comes onto the field', None, 35.13285, -81.80985, None, 1, 'place', None, 'yes'),
    ('Island Creek', None, 35.12961, -81.82589, -26, 1, 'water', None, None),
    ('Long Branch', None, 35.12539, -81.80760, 42, 1, 'water', None, None),
    ('Zekial Creek', None, 35.11910, -81.79299, -34, 1, 'water', None, None),
    ('to the Broad River, about 6 miles', None, 35.14215, -81.82020, None, 1, 'place', None, 'yes'),
    ('from Thicketty Creek and the Pacolet', None, 35.11480, -81.78330, None, 1, 'place', None, 'yes'),
    ('Chesnee Highway (SC 11)', None, 35.13249, -81.79914, 36, 1, 'road', None, None),
]
SOURCE_USE = ['S95', 'S96', 'S97', 'S98', 'S99', 'S100', 'S101', 'S102', 'S103', 'S104', 'S105', 'S106', 'S39']


# ---------------------------------------------------------------- writing
def header(ws): return [c.value for c in ws[1]]
def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r
def add(ws, row):
    """Append a row given by column heading; a heading the row does not name is left empty. Returns the row number."""
    h = header(ws); r = last_row(ws) + 1
    for k in row: assert k in h, '%s: no column %r' % (ws.title, k)
    for c, name in enumerate(h, 1):
        v = row.get(name)
        if v is not None: ws.cell(r, c, v)
    return r


def main():
    wb = openpyxl.load_workbook(WAR)
    if any(ws_row[0].value == PB for ws_row in wb['Playbacks'].iter_rows(min_row=2)): print('cowpens is already in the workbook: nothing done'); return
    sh = openpyxl.load_workbook(SHARED)
    # sources
    ws = sh['Sources']; have = {r[0].value for r in ws.iter_rows(min_row=2)}
    for s in SOURCES:
        assert s['source_id'] not in have, s['source_id']; add(ws, s)
    ws = sh['Source candidates']; h = header(ws)
    for row in ws.iter_rows(min_row=2):
        cid = row[0].value
        if cid in CANDIDATES:
            st, note = CANDIDATES[cid]; row[h.index('status')].value = st
            old = row[h.index('notes')].value; row[h.index('notes')].value = ((old + ' ') if old else '') + note
    for c in NEW_CANDIDATES: add(ws, dict(zip(h, c)))
    ws = sh['Read me']; ws.insert_rows(1, 3)
    ws.cell(1, 1, 'What changed on 23 November 2026 (evening): the Battle of Cowpens')
    ws.cell(2, 1, 'Revolutionary War.xlsx: a second campaign (ARW-SOU, Greene\'s campaign in the Carolinas) and its first battle, Cowpens, 17 January 1781 (playback "cowpens"): 31 units, %d position rows (CP01 to CP137), 11 routes, 14 events, '
                  '15 hypotheses (CH01 to CH15) and 8 gaps (CG01 to CG08). Sources S95 to S106 are new here: the Army\'s 1996 staff ride handbook and the eyewitness documents it prints, the Army War College study of 1928, the National Park Service handbook, '
                  'and the park\'s waysides. Two candidates added (SC-SOU08, SC-SOU09). Every position is placed by a distance the sources give, measured along the Green River Road on today\'s map (pipeline/cowpens_geo.py); none is rated above medium. '
                  'Not read: Bearss (1967), Ward, Babits. Written by pipeline/cowpens_2026_11_23.py. The exporter now reads one new kind of setting, sides.<code>.short and sides.<code>.name, so a playback can name a side for itself (the Crown side is "Hessian and British" for Trenton and "British" here); no battle file format change.' % len(POS))
    # the war workbook
    add(wb['Campaigns'], CAMPAIGN); add(wb['Battles'], BATTLE_ROW)
    for pid, label, s, e, src, note in PHASES: add(wb['Phases'], dict(phase_id=pid, battle_id=BATTLE, label=label, start=T(s), end=T(e), source_ids=src, notes=note))
    n = max(int(r[0].value[1:]) for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value)
    for other in ('U.S. Civil War', 'Philippine War', 'World War I'):   # assignment ids run on across the workbooks
        o = openpyxl.load_workbook(os.path.join(FOLDER, other + '.xlsx'), read_only=True)
        n = max([n] + [int(r[0][1:]) for r in o['Assignments'].iter_rows(min_row=2, values_only=True) if r and r[0]])
    for (uid, name, label, side, nation, branch, ech, src, notes, parent, cmd, strength, asrc, anote) in UNITS:
        code = '100%s1000%s000000' % ('3' if side == US else '6', SYM[(branch, ech)])
        add(wb['Units'], {'unit_id': uid, 'unit_name': name, 'map_label': label, 'side_id': side, 'nation': nation, 'branch': branch, 'echelon': ech, 'symbol_code': code, 'source_ids': src, 'sourced?': 'yes', 'notes': notes})
        n += 1
        add(wb['Assignments'], {'assign_id': 'A%03d' % n, 'unit_id': uid, 'parent_unit_id': parent, 'commander': cmd, 'strength / equipment': strength, 'valid_from': DAY, 'valid_to': DAY, 'source_ids': asrc, 'notes': anote})
    ws = wb['Positions']
    for p in POS:
        r = last_row(ws) + 1
        p = dict(p, unit_name='=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r, side='=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r,
                 map_link='=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=17/"&O%d&"/"&P%d,"Open map"))' % (r, r, r, r, r))
        add(ws, p)
    for rt in ROUTES:
        add(wb['Routes'], {'route_id': rt['route_id'], 'campaign_id': CAMP, 'battle_id': BATTLE, 'unit_id': rt['unit_id'], 'kind': rt['kind'], 'start': rt['start'], 'end': rt['end'], 'from_pos_id': rt['from_pos_id'], 'to_pos_id': rt['to_pos_id'],
                           'waypoints (lat, lon; ...)': wp(rt['wps']), 'source_ids': rt['source_ids'], 'source_wording': rt['source_wording'], 'confidence': rt['confidence'], 'notes': rt['notes'], 'playback': rt['playback']})
    ids = {p['pos_id'] for p in POS}
    for (eid, t0, t1, name, summary, rows, src, tl, at_, label) in EVENTS:
        for x in rows.split('; '): assert x in ids, (eid, x)
        add(wb['Events'], dict(event_id=eid, campaign_id=CAMP, battle_id=BATTLE, time_earliest=T(t0), time_latest=T(t1), name=name, summary=summary, pos_ids=rows, source_ids=src, timeline=tl, playback_at=T(at_), playback_label=label))
    for hrow in HYP: add(wb['Hypotheses'], hrow)
    for gid, gap, effect, close in GAPS: add(wb['Gaps'], {'gap_id': gid, 'battle_id': BATTLE, 'gap': gap, 'effect on the data': effect, 'how to close it': close, 'status in v2': 'Open (new on 23 Nov 2026).'})
    add(wb['Playbacks'], PLAYBACK)
    for s in SETTINGS: add(wb['Playback settings'], {'playback_id': PB, 'setting': s[0], 'value': s[1], 'what it does': s[2] if len(s) > 2 else None})
    for name, short in NATIONS: add(wb['Nations'], dict(playback_id=PB, name=name, short=short))
    for (tid, unit, rows, part, hide, loose, nudge, sfr, sat, sroute) in TRACKS:
        for x in rows.split('; '): assert x in ids, (tid, x)
        add(wb['Tracks'], dict(playback_id=PB, track_id=tid, unit_id=unit, rows=rows, part_of_track=part, hide_after_last_row=hide, loose=loose, nudge=nudge, starts_from_row=sfr, starts_at=sat, start_route=sroute))
    for (text, other, lat, lon, angle, level, kind, show, approx) in LABELS:
        add(wb['Labels'], dict(playback_id=PB, text=text, other_name=other, lat=lat, lon=lon, angle=angle, level=level, kind=kind, show=show, approximate=approx))
    titles = {s['source_id']: s['title'] for s in SOURCES}; titles['S39'] = 'OpenStreetMap: place coordinates and the current maps under each battle'
    ws = wb['Source uses']
    for sid in SOURCE_USE:
        r = last_row(ws) + 1
        add(ws, dict(source_id=sid, title=titles[sid], campaign_id=CAMP, playback_id=PB,
                     positions='=COUNTIFS(Positions!$X:$X,"*"&$A%d&"*",Positions!$B:$B,$C%d)' % (r, r), events='=COUNTIFS(Events!$I:$I,"*"&$A%d&"*",Events!$B:$B,$C%d)' % (r, r),
                     routes='=COUNTIFS(Routes!$K:$K,"*"&$A%d&"*",Routes!$B:$B,$C%d)' % (r, r), units='=COUNTIFS(Units!$J:$J,"*"&$A%d&"*",Units!$A:$A,"C-*")' % r,
                     period_maps='=COUNTIFS(Maps!$G:$G,$A%d,Maps!$A:$A,$D%d)' % (r, r), total='=SUM(E%d:I%d)' % (r, r)))
    rm = wb['Read me']; rm.append([]); rm.append(['Cowpens (23 Nov 2026)', 'The Battle of Cowpens, 17 January 1781, added as campaign ARW-SOU, battle COWP, playback "cowpens": rows CP01 to CP137, units C-..., events CE01 to CE14, routes RC01 to RC11, '
                                                 'hypotheses CH01 to CH15, gaps CG01 to CG08. See the change log in "Sources and notes.xlsx" and pipeline/cowpens_2026_11_23.py.'])
    wb.save(WAR); sh.save(SHARED)
    print('Cowpens: %d units, %d positions, %d routes, %d events, %d hypotheses, %d gaps, %d sources' % (len(UNITS), len(POS), len(ROUTES), len(EVENTS), len(HYP), len(GAPS), len(SOURCES)))


if __name__ == '__main__':
    main()
