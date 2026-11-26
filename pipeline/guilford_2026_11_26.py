"""26 Nov 2026: the Battle of Guilford Courthouse, 15 March 1781, added to the Revolutionary War workbook. Run once.

  python3 pipeline/recon/guilford_1781.py      first: the reconstructed base map's lines (data/recon/guilford-1781.geojson)
  python3 pipeline/guilford_2026_11_26.py

It adds the battle and its phases to the campaign ARW-SOU, the order of battle (Units, Assignments), the positions by the clock, the routes, the
events, the hypotheses (one per disputed point), the gaps, the playback with its settings, tracks, labels, maps and reconstruction, the link
from Cowpens (Next links), and the source-use rows to `Revolutionary War.xlsx`, and the new sources and candidates to `Sources and notes.xlsx`.
Run it again and it does nothing: it stops if the playback `guilford-courthouse` is already on the Playbacks sheet.

Where every position comes from is said on its own row (coordinate_basis, source_wording, source_pages, cross_checked_by). In short: on the
battlefield every unit is read off one of Charles Hatch's five troop movement plans for the National Park Service (1971, S138), laid on the
ground by the park boundary (pipeline/guilford_geo.py), and checked against the Marine Corps University Press staff ride of 2021 (S144) and
the commanders' reports. The morning fights near New Garden are placed at the three road junctions the staff ride names. Every position is rated low. The clock is the staff ride's (first line attacked about 13:00, the Continentals off about 15:30).
"""
import os, sys, json, math
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'recon'))
import guilford_geo as G
import guilford_1781 as R

FOLDER = os.path.join(os.path.dirname(HERE), 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx'); SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
CAMP, BATTLE, PB, DAY = 'ARW-SOU', 'GUIL', 'guilford-courthouse', '1781-03-15'
TODAY = '2026-11-26'; REV = 'Needs review'


def T(hm): return '%s %s' % (DAY, hm)
def plus(hm, minutes):
    h, m = [int(x) for x in hm.split(':')]; t = h * 60 + m + minutes
    return '%02d:%02d' % (t // 60, t % 60)


# ---------------------------------------------------------------- sources (Sources and notes.xlsx)
IA = 'https://archive.org/details/guilfordcourthou00hatc'
MCUP = 'https://www.usmcu.edu/Outreach/Marine-Corps-University-Press/Books-by-topic/MCUP-Titles-A-Z/A-Game-of-Hare-or-Hounds/'
LOCAL = 'Historical Info/History 340/Guilford Courthouse (Morgan\'s Mac)'
def S(sid, title, author, date, typ, citation, verified, url, rights, notes, kind, status, host, site, local=None, part=None, offset=None):
    return {'source_id': sid, 'title': title, 'author': author, 'date': date, 'type': typ, 'citation': citation, 'page verified?': verified, 'url': url, 'rights': rights, 'notes': notes,
            'used_for': 'GUIL', 'kind': kind, 'war': 'ARW', 'rights_status': status, 'may_host': host, 'rights_checked': TODAY, 'site': site, 'local_copy': local, 'page_offset': offset, 'part_of': part}
SOURCES = [
    S('S138', 'Guilford Courthouse National Military Park: The Battle of Guilford Courthouse', 'Charles E. Hatch, Jr.', '1971',
      'Modern secondary: National Park Service documented narrative with five troop movement plans',
      'Charles E. Hatch, Jr., The Battle of Guilford Courthouse (Washington: National Park Service, Office of History and Historic Architecture, Eastern Service Center, July 1971), ix + 163 pp., 15 plates and 5 battle plans. Report FNP-HH-72-106; NTIS PB-208 056.',
      'yes (the scan\'s text read by printed page; the page number is printed at the foot of each page; the five plans read from the page images)', IA,
      'U.S. government work (National Park Service; the last plan carries a Government Printing Office imprint of 1976). The Internet Archive marks its scan public domain. The five plans are hosted, reduced.',
      'Read 26 Nov 2026: chapters III to VIII (pp. 21-97) and appendixes A and B (pp. 119-132). Its five plans (No. 1 the ground, No. 2 the armies deployed, No. 3 the first line gives way, No. 4 the second line, No. 5 the third line and retreat) are drawn to one scale on one base with the park boundary of 1971; they are fitted to the ground by that boundary (pipeline/guilford_geo.py) and every battlefield position is read from them. Hatch quotes the reports and memoirs at length with page references; several sources below were read in his quotations. He writes that Leslie\'s brigade stood "on the British left" (p. 45): a slip for the right, as his own plan shows.',
      'book', 'public domain', 'yes (the plans, reduced)', 'archive.org', LOCAL + ': guilfordcourthou00hatc.pdf'),
    S('S139', 'Cornwallis to Lord George Germain, Guilford, 17 March 1781 (dispatch No. 8: report of the battle)', 'Lt. Gen. Charles, Earl Cornwallis', '1781-03-17',
      'Primary: commander\'s report, two days after the battle',
      'Cornwallis to Germain, 17 March 1781; printed in Tarleton, History of the Campaigns of 1780 and 1781 (London, 1787), pp. 311-320, with the field return. Read as quoted in Hatch (S138), pp. 21, 30, 44, 55-56, 58-59, 73-74, 91-92, 96, and in Skinner (S144), pp. 119-120.',
      'yes (pages of S138 and S144); the pages of Tarleton\'s 1787 edition were not checked', IA, 'Public domain (1781). Read in U.S. government publications.',
      'The march "at daybreak", the first clash "about four miles from Guildford", the ground, the order of attack by regiment, the hour ("about half an hour past one"), the length ("an hour and a half"), the Guards\' attack and repulse, the guns, the end. The one account written on the field.',
      'official report', 'public domain', 'yes (the text)', 'archive.org', None, 'S138'),
    S('S140', 'Greene to Samuel Huntington, President of Congress, camp at the iron works, 16 March 1781; and his letters of 16 to 20 March', 'Maj. Gen. Nathanael Greene', '1781-03-16',
      'Primary: commander\'s report, the day after the battle',
      'Greene to Huntington, 16 March 1781 (printed in Tarleton, 1787, pp. 322 ff.); Greene to Jefferson, 16 March; to Nash and to Washington, 18 March; to Morgan, 20 March. Read as quoted in Hatch (S138), pp. 26 n. 15, 29-30, 35, 37, 47, 54-55, 57, 70, 74-75, 83-84.',
      'yes (pages of S138)', IA, 'Public domain (1781). Read in a U.S. government publication.',
      'The ground, the three lines and the distances between them (300 and 400 yards), the two flank corps by name, the hour ("about twelve o\'clock"), the first line breaking at 140 yards, the order to retreat when the 2nd Maryland broke, the retreat by the Reedy Fork to the iron works.',
      'official report', 'public domain', 'yes (the text)', 'archive.org', None, 'S138'),
    S('S141', 'Memoirs of the War in the Southern Department (the Guilford passages); and The Campaign of 1781 in the Carolinas', 'Lt. Col. Henry Lee; Henry Lee, Jr.', '1812; 1824',
      'Primary: participant, written thirty years later',
      'Henry Lee, Memoirs of the War in the Southern Department of the United States (1812; New York, 1869 edition), pp. 270-285; Henry Lee [Jr.], The Campaign of 1781 in the Carolinas (Philadelphia, 1824), pp. 167-196. Read as quoted in Hatch (S138), pp. 22-28, 36-39, 41-43, 50, 59, 66, 75-76, 80, 85-89, 93, and in Skinner (S144), pp. 74-75.',
      'yes (pages of S138 and S144); Lee\'s own pages were not checked', IA, 'Public domain.',
      'The fullest account of the morning: Heard\'s picket, the charge in the lane, the Guards\' volley at the meeting house, the withdrawal. Also the ground at the creek, the flank corps, the Guards and the 1st Maryland, his own separate fight and how he left it. Written to his own credit; his hours ("about ten in the forenoon" for the cannonade) are too early.',
      'memoir', 'public domain', 'yes (the text)', 'archive.org', None, 'S138'),
    S('S142', 'A History of the Campaigns of 1780 and 1781, in the Southern Provinces of North America (the Guilford passages)', 'Lt. Col. Banastre Tarleton', '1787',
      'Primary: the British cavalry commander\'s own account, published six years later',
      'Banastre Tarleton, A History of the Campaigns of 1780 and 1781 (London: T. Cadell, 1787), pp. 277-286. Read as quoted in Hatch (S138), pp. 21-22, 26-27, 34-35, 38, 43, 45-46, 56, 77, 85, 87-88, and in Skinner (S144), p. 76.',
      'yes (pages of S138 and S144); the pages of the 1787 edition were not checked', 'https://archive.org/details/bim_eighteenth-century_a-history-of-the-campaig_tarleton-lieutenant-gen_1787', 'Public domain (1787).',
      'The order of march, the picket driven in "seven miles" out, the 23rd coming up, the cavalry kept in column on the road, the last charge on the right, "upwards of two hours". The Cowpens passages of the same book are source S97.',
      'book', 'public domain', 'yes (the text)', 'archive.org', None, None),
    S('S143', 'Eyewitness accounts of Guilford Courthouse printed in Hatch (1971)', 'William Seymour; Samuel Houston; St. George Tucker; Roger Lamb; Thomas Saumarez; Dugald Stuart; James Martin; Charles Magill; Charles Stedman; the British orderly book', '1781 to 1856',
      'Primary: journals, letters and memoirs of men in both armies, and the British order of march',
      'As quoted in Hatch (S138): Sgt. Maj. William Seymour, Journal of the Southern Expedition (pp. 23-24, 32, 43, 65-66); Samuel Houston, journal, in Foote, Sketches of Virginia, 2nd series, 1856 (pp. 33, 52, 62-63, 89); Lt. Col. St. George Tucker to his wife, 18 March 1781 (pp. 44, 61, 92); Sgt. Roger Lamb, 1809 (pp. 28, 51, 60); Lt. Thomas Saumarez, 23rd Foot (pp. 47-48, 58, 91); Capt. Dugald Stuart, 71st (p. 52); Col. James Martin (pp. 53, 70); Charles Magill to Jefferson, 16 March 1781 (pp. 43, 54, 93); Charles Stedman, History of the American War, 1794 (pp. 49, 59, 63-66, 87, 96-98); "A British Orderly Book", N.C. Historical Review 9 (p. 22).',
      'yes (pages of S138); none of the originals was checked', IA, 'Public domain. Read in a U.S. government publication.',
      'Seymour gives the one clock time for the morning ("about nine o\'clock ... about the space of an hour and a half"); Houston "about ten o\'clock" for the firing heard in camp and "two hours and twenty-five minutes" for the battle; Saumarez "about one o\'clock"; the orderly book "half past five" for the march. Stedman was the British commissary and not on the field: he follows Cornwallis and Tarleton.',
      'memoir', 'public domain', 'yes (the text)', 'archive.org', None, 'S138'),
    S('S144', 'A Game of Hare & Hounds: An Operational-level Command Study of the Guilford Courthouse Campaign, 18 January-15 March 1781', 'Harold Allen Skinner, Jr.', '2021',
      'Modern secondary: Marine Corps University Press staff ride handbook, with maps by the Army University Press',
      'Harold Allen Skinner, Jr., A Game of Hare & Hounds (Quantico, Va.: Marine Corps University Press, 2021), xx + 160 pp., 24 maps. ISBN 978-1-7320031-6-3; LCCN 2020057234. Maps by Charles D. Collins, Jr., Army University Press.',
      'yes (the text read by printed page from Morgan\'s PDF; the PDF page is the printed page plus 20; maps 13, 16 and 18 read from the page images, the other battle maps not yet)', MCUP,
      'The press\'s disclaimer says its works are made by U.S. government employees in their official duties and are not eligible for copyright in the United States, and warns that some may carry other people\'s material. Cited and linked; no page of it is hosted.',
      'Read 26 Nov 2026: the New Garden stand (pp. 72-77), the battle stands 2 to 14 (pp. 80-116), the orders of battle (pp. 150-151, from Babits and Howard, pp. 219-21) and the chronology (p. 153). Its clock is the playback\'s for the afternoon. It follows Babits and Howard (2009), which has not been read here. Two things in it do not agree with each other: the stand text puts Butler\'s brigade north of the road and Eaton\'s south (p. 87), its own Map 16 the reverse (p. 89); and the chronology has the dragoons fighting at New Garden at 0400-0500 (p. 153) where the stand text has about 0700, 0900 and 1000 (pp. 72-74).',
      'book', 'public domain (to confirm)', 'check', 'usmcu.edu', LOCAL + ': STAFF RIDE Guilford Courthouse web.pdf', None, 20),
    S('S145', 'Cultural Landscape Report: Guilford Courthouse National Military Park', 'John Hiatt', '2003',
      'Modern secondary: National Park Service landscape study',
      'John Hiatt, Cultural Landscape Report: Guilford Courthouse National Military Park (Atlanta: National Park Service, Southeast Regional Office, Cultural Resources Division, 2003).',
      'partly (two passages read by printed page, pp. 4 and 22; the rest searched, not read)', 'https://archive.org/details/culturallandscap00hiat',
      'U.S. government work (National Park Service). The Internet Archive marks its scan public domain. Cited and linked; nothing of it is hosted yet.',
      'Read 26 Nov 2026 for the third line only: the park\'s staff hold that the line "actually stood about 400 yards east of its previously interpreted position" between Tour Stops 5 and 7 (p. 4), which was Schenck\'s of the 1880s (p. 22). Its maps of the ground in 1781 have not been read: see the gaps.',
      'book', 'public domain', 'yes', 'archive.org', LOCAL + ': culturallandscap00hiat.pdf'),
    S('S146', 'Guilford, N.C. and Greensboro, N.C., 7.5-minute topographic sheets, 1:24,000 (1951)', 'U.S. Geological Survey', '1951',
      'Modern map: surveyed topographic sheets', 'U.S. Geological Survey, Guilford quadrangle and Greensboro quadrangle, North Carolina, 1:24,000, 1951 (Historical Topographic Map Collection, scans 162550 and 162532, GeoTIFF).',
      'not applicable (maps)', 'https://ngmdb.usgs.gov/topoview/', 'Public domain (U.S. government work).',
      'Morgan\'s copies. The sheets end at latitude 36.125, just south of the battlefield, so they give New Garden Road before the suburbs from Guilford College to within 500 m of Little Horsepen Creek, not the field itself. Reprojected from NAD 27 polyconic to WGS 84 for picking.',
      'map', 'public domain', 'yes', 'usgs.gov', LOCAL + ': NC_Guilford_162550_1951_24000_geo.tif, NC_Greensboro_162532_1951_24000_geo.tif'),
    S('S147', 'USGS Topo base map (The National Map), as served in November 2026', 'U.S. Geological Survey', '2026',
      'Modern map: today\'s topographic base map', 'U.S. Geological Survey, The National Map, USGS Topo base map tile service, zoom 16, read 26 November 2026.',
      'not applicable (map)', 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer', 'Public domain (U.S. government work).',
      'The ground Hatch\'s plans are fitted to: it draws the park boundary, the Historic New Garden Road, Richland Creek (Hatch\'s Hunting Creek) and today\'s streets. It is also the playback\'s current map.',
      'map', 'public domain', 'yes (streamed)', 'usgs.gov'),
]
CANDIDATES = {'SC-SOU07': ('used: now source S145', '26 Nov 2026: read in part from Morgan\'s copy (the third line, pp. 4 and 22); its 1781 landscape maps not yet.'),
              'SC-SOU06': ('located', '26 Nov 2026: Morgan saved the park\'s 2023 brochure (2023.pdf) for Guilford Courthouse; its text was skimmed, its battle map not read or fitted: gap GG05.')}
# candidate_id, title, holder, url, war, battles, what it holds, access, rights, status, priority, added, notes
NEW_CANDIDATES = [
    ('SC-SOU10', 'Long, Obstinate, and Bloody: The Battle of Guilford Courthouse', 'Lawrence E. Babits and Joshua B. Howard (University of North Carolina Press, 2009)', None, 'ARW', 'GUIL',
     'The standard modern study, built on the pension files; the staff ride (S144) follows it and takes its orders of battle from pp. 219-21.', 'Not found online; Morgan could not get a copy on 26 Nov 2026.', 'In copyright. Link and cite only.', 'located', 'P1', TODAY,
     'Not read. Needed to settle GH04 (which brigade stood north of the road) and to check every regimental position (SR-19).'),
    ('SC-SOU11', 'Another Such Victory: The Story of the American Defeat at Guilford Courthouse', 'Thomas E. Baker (Eastern National, 1981, 1999); Internet Archive lending copy', 'https://archive.org/details/anothersuchvicto0000bake', 'ARW', 'GUIL',
     'The park historian\'s narrative, with the revised third line.', 'Lending copy (one hour, free account); not read.', 'In copyright. Link and cite only.', 'located', 'P2', TODAY, 'Not read.'),
    ('SC-SOU12', 'Battle of Guildford, fought on the 15th of March 1781 (the British plan engraved for Tarleton\'s History)', 'William Faden, London, 1 March 1787; Library of Congress; Leventhal Map Center; Harvard', 'https://collections.leventhalmap.org/search/commonwealth:q524nc29b', 'ARW', 'GUIL',
     'The only plan made by men who were there (scale about 1:18,600, north to the upper left). Hatch reproduces it as his Plate 4 and builds on it.', 'Online; the scan was not opened in this session.', 'Public domain (1787). May be hosted.', 'located', 'P1', TODAY,
     'The best candidate for a map of the time to offer beside the reconstruction: a sketch, so it would be shown as a picture not to scale or fitted roughly. Gap GG03.'),
    ('SC-SOU13', 'Guilford Courthouse and Its Environs', 'Charles E. Hatch, Jr. (National Park Service, December 1970)', None, 'ARW', 'GUIL',
     'Hatch\'s companion study of the village, roads, creeks, fields and woods (his chapter VIII), on which his base plan rests.', 'Catalogued (SuDoc I 29.2:G 94); no scan found.', 'U.S. government work.', 'located', 'P2', TODAY, 'Not read. Would say what each line of plan No. 1 rests on.'),
    ('SC-SOU14', 'North Carolina, 1780-\'81: being a history of the invasion of the Carolinas', 'David Schenck (Raleigh, 1889); Internet Archive', 'https://archive.org/details/northcarolina17800sche', 'ARW', 'GUIL',
     'The founder of the battleground park: the ground as he measured it in the 1880s, and the older reading of the third line.', 'Online (text); not read beyond Hatch\'s quotations.', 'Public domain (1889).', 'located', 'P3', TODAY, 'Not read.'),
]

# ---------------------------------------------------------------- battle, phases
COURT = G.hp(1, 1745, 462)                      # the courthouse as Hatch marks it
BATTLE_ROW = dict(battle_id=BATTLE, campaign_id=CAMP, parent_battle_id=None, name='Battle of Guilford Courthouse', start_earliest=T('12:00'), start_latest=T('13:30'), end_earliest=T('15:00'), end_latest=T('16:00'),
                  lat=COURT[0], lon=COURT[1], coord_precision='battle', coord_source='The courthouse as Hatch marks it on his plan No. 1 (S138), fitted to the ground by the park boundary (pipeline/guilford_geo.py)',
                  wikidata_qid=None, cdb90_id=None, war_atlas_slug=None,
                  notes='Start: "about twelve o\'clock" (Greene, S140), "about one o\'clock" (Saumarez, S143), "about half an hour past one" (Cornwallis, S139), 1300 (S144, p. 153): see GH01. End: "an hour and a half" (S139), "about two hours" (S140), "two hours and twenty-five minutes" (Houston, S143), 1530 for the Continentals (S144, p. 153) and 1545 for the end of the battle (S144, Map 24, p. 113). Wikidata id not looked up.',
                  extent_km=9)
PHASES = [
    ('PH-GC1', 'The morning fights near New Garden', '08:15', '10:00', 'S138; S141; S142; S144', 'Lee against Tarleton on the great road, four to five miles from the courthouse. The hours are disputed: GH02.'),
    ('PH-GC2', 'Greene forms three lines; Cornwallis comes up', '10:00', '12:30', 'S138; S140; S143; S144', 'From Lee\'s withdrawal to the head of the British column at Little Horsepen Creek.'),
    ('PH-GC3', 'Cannonade and the first line', '12:30', '13:20', 'S138; S139; S144', 'Staff ride maps 16 and 17: 1300 to 1330; chronology 1300 and 1315.'),
    ('PH-GC4', 'The second line and the fight in the south', '13:20', '14:40', 'S138; S144', 'Staff ride maps 18 and 19: 1330 to 1430.'),
    ('PH-GC5', 'The third line', '14:40', '15:30', 'S138; S139; S140; S144', 'Staff ride maps 20 to 23: 1445 to 1530.'),
    ('PH-GC6', 'Retreat, and the last of the fight in the south', '15:30', '16:15', 'S138; S142; S144', 'Staff ride map 24: 1545. Tarleton\'s charge on the riflemen ended the day.'),
]

# ---------------------------------------------------------------- order of battle
US, CR = 'ARW-US', 'ARW-CR'
SYM = {('Infantry', 'Army'): '231211', ('Infantry', 'Brigade'): '181211', ('Infantry', 'Regiment'): '171211', ('Infantry', 'Battalion'): '161211', ('Infantry', 'Company'): '151211',
       ('Infantry', 'Headquarters'): '001211', ('Cavalry', 'Squadrons'): '161213', ('Artillery', 'Section'): '131303'}
H, K = 'S138', 'S144'
# unit_id, name, map label, side, nation, branch, echelon, sources, notes, parent, commander, strength, assignment sources
UNITS = [
    ('G-US-ARMY', 'The Southern Army under Greene', 'Greene\'s army', US, 'United States', 'Infantry', 'Army', 'S138; S140; S144', 'The whole American force: Continentals, Virginia and North Carolina militia, riflemen and two small legions. Its strength: GH06.',
     None, 'Maj. Gen. Nathanael Greene', 'Upwards of 4,400: Continentals 1,700, militia 2,200, riflemen and volunteers 500 (S138, pp. 127-128). About 4,400 with 4,000 engaged (S144, p. 151). 1,500 Continentals and 3,000 militia (S85, p. 98). Lee: a field return of 4,449 (in S138, p. 129). Schenck: over 5,668 (in S138, p. 128).', 'S138; S144; S85'),
    ('G-US-HQ', 'Greene\'s headquarters', 'Greene (HQ)', US, 'United States', 'Infantry', 'Headquarters', 'S138; S140', 'Greene rode the first line before the action, then took post with the third line (S138, pp. 39-40).', 'G-US-ARMY', 'Maj. Gen. Nathanael Greene', None, 'S138'),
    ('G-US-EATON', 'Eaton\'s brigade, North Carolina militia (first line)', 'Eaton', US, 'United States', 'Infantry', 'Brigade', 'S138; S144', 'Men chiefly of Halifax and Warren counties (S138, p. 34). Which side of the road it held is disputed: GH04.',
     'G-US-ARMY', 'Brig. Gen. Thomas Eaton', 'Perhaps over 500 (S138, pp. 34, 127). 600 in three battalions (S144, p. 151).', 'S138; S144'),
    ('G-US-BUTLER', 'Butler\'s brigade, North Carolina militia (first line)', 'Butler', US, 'United States', 'Infantry', 'Brigade', 'S138; S144', 'Chiefly Orange, Guilford and Granville men; Capt. Arthur Forbis\'s Guilford company stood in it (S138, pp. 34, 53). GH04.',
     'G-US-ARMY', 'Brig. Gen. John Butler', 'Perhaps over 500 (S138, pp. 34, 127). 600 in four battalions and three companies (S144, p. 151).', 'S138; S144'),
    ('G-US-SING', 'Singleton\'s two 6-pounders (first line, then the left of the third)', 'Singleton\'s guns', US, 'United States', 'Artillery', 'Section', 'S138; S139', 'In the road just in front of the first line; drawn back to the Continentals before the attack (Cornwallis, in S138, p. 43 n. 42).',
     'G-US-ARMY', 'Capt. Anthony Singleton', 'Two 6-pounders; 60 gunners for the four guns (S138, p. 131); 40 for the four (S144, p. 151).', 'S138; S144'),
    ('G-US-WASH', 'Washington\'s cavalry: detachments of the 1st and 3rd Continental Light Dragoons', 'Washington', US, 'United States', 'Cavalry', 'Squadrons', 'S138; S140', 'The right flank corps with Kirkwood and Lynch. Watkins\'s Virginia militia dragoons rode with it (S138, p. 77).',
     'G-US-ARMY', 'Lt. Col. William Washington', '86 (S138, p. 131); "nearly 100 troopers" (p. 35). The staff ride gives his whole corps 238 (S144, p. 151).', 'S138; S144'),
    ('G-US-KIRK', 'Kirkwood\'s Delaware company (Continental light infantry)', 'Kirkwood', US, 'United States', 'Infantry', 'Company', 'S138; S140', 'On the right flank of the first line, then of the second and third (S138, pp. 35, 65).',
     'G-US-ARMY', 'Capt. Robert Kirkwood', 'About 80 (S138, pp. 35, 130).', 'S138'),
    ('G-US-LYNCH', 'Lynch\'s Virginia riflemen', 'Lynch', US, 'United States', 'Infantry', 'Battalion', 'S138; S140', 'On the right flank of the first line, in the woods, angled forward (S138, p. 35).',
     'G-US-ARMY', 'Col. Charles Lynch', 'Some 200 (S138, p. 35). 150 (S144, p. 151).', 'S138; S144'),
    ('G-US-LEEC', 'Lee\'s Legion: the cavalry', 'Lee (cavalry)', US, 'United States', 'Cavalry', 'Squadrons', 'S138; S141', 'Three troops under Rudolph, Eggleston and Armstrong (S138, p. 24). The left flank corps with the Legion infantry and Campbell.',
     'G-US-ARMY', 'Lt. Col. Henry Lee', 'Some 75 (S138, pp. 35, 131). The staff ride gives the Legion 240 in all (S144, p. 151).', 'S138; S144'),
    ('G-US-LEEI', 'Lee\'s Legion: the infantry', 'Legion infantry', US, 'United States', 'Infantry', 'Company', 'S138; S141', 'With Lee in the morning and on the left flank in the battle.',
     'G-US-ARMY', 'Lt. Col. Henry Lee', '82 (S138, p. 131).', 'S138'),
    ('G-US-CAMP', 'Campbell\'s riflemen (Virginia and North Carolina)', 'Campbell', US, 'United States', 'Infantry', 'Battalion', 'S138; S140; S141', 'With Lee in the morning ("part of his riflemen", Greene) and on the left flank; the last Americans engaged (S138, p. 89).',
     'G-US-ARMY', 'Col. William Campbell', 'Some 250 by Greene\'s estimate (S138, p. 35). 100, with a Virginia light infantry company of 60 beside it (S144, p. 151).', 'S138; S144'),
    ('G-US-LAWS', 'Lawson\'s brigade, Virginia militia (second line, north of the road)', 'Lawson', US, 'United States', 'Infantry', 'Brigade', 'S138; S144', 'Regiments of Randolph, Holcombe and Skipwith, right to left (S144, p. 95).',
     'G-US-ARMY', 'Brig. Gen. Robert Lawson', 'About 600 (S138, p. 132). Around 650 (S144, p. 95).', 'S138; S144'),
    ('G-US-STEV', 'Stevens\'s brigade, Virginia militia (second line, south of the road)', 'Stevens', US, 'United States', 'Infantry', 'Brigade', 'S138; S144', 'Stuart, Moffett, Cocke and Perkins, left to right (S144, p. 98); a line of sentinels twenty yards behind it (S138, p. 37).',
     'G-US-ARMY', 'Brig. Gen. Edward Stevens', 'About 600 (S138, p. 132). 750 (S144, p. 151).', 'S138; S144'),
    ('G-US-HUGER', 'Huger\'s Virginia Continental brigade (third line, right)', 'Huger', US, 'United States', 'Infantry', 'Brigade', 'S138; S140', 'Two regiments of new levies under veteran officers (S138, p. 38).',
     'G-US-ARMY', 'Brig. Gen. Isaac Huger', '778 (S138, p. 131). 900 (S144, p. 151).', 'S138; S144'),
    ('G-US-GREEN', 'Green\'s Virginia Continental regiment', 'Green', US, 'United States', 'Infantry', 'Regiment', 'S138', 'The right of the third line; drawn off unengaged to cover the retreat (S138, pp. 83, 92).', 'G-US-HUGER', 'Col. John Green', '450 (S144, p. 151).', 'S138; S144'),
    ('G-US-HAWES', 'Hawes\'s Virginia Continental regiment', 'Hawes', US, 'United States', 'Infantry', 'Regiment', 'S138', 'Huger\'s own regiment, under Hawes for the day; the last engaged (S138, p. 83).', 'G-US-HUGER', 'Lt. Col. Samuel Hawes', '450 (S144, p. 151).', 'S138; S144'),
    ('G-US-WILL', 'Williams\'s Maryland Continental brigade (third line, left)', 'Williams', US, 'United States', 'Infantry', 'Brigade', 'S138; S140', 'The 1st and 2nd Maryland, with Jaquett\'s Delaware company in the line (S138, p. 130).',
     'G-US-ARMY', 'Col. Otho Holland Williams', 'Some 630 with the Delawares (S138, p. 130).', 'S138'),
    ('G-US-1MD', '1st Maryland Regiment', '1st Maryland', US, 'United States', 'Infantry', 'Regiment', 'S138; S141', 'The one veteran regiment of the line (Lee, in S138, p. 38 n. 28).', 'G-US-WILL', 'Col. John Gunby; Lt. Col. John Eager Howard', '400 (S144, p. 151).', 'S138; S144'),
    ('G-US-2MD', '2nd Maryland Regiment', '2nd Maryland', US, 'United States', 'Infantry', 'Regiment', 'S138; S140', 'New levies; the left of the third line, by the road (S138, p. 38).', 'G-US-WILL', 'Lt. Col. Benjamin Ford', '400 (S144, p. 151).', 'S138; S144'),
    ('G-US-FIN', 'Finley\'s two 6-pounders (centre of the third line)', 'Finley\'s guns', US, 'United States', 'Artillery', 'Section', 'S138', '"In the curve of the line between his two brigades" (S138, p. 38).', 'G-US-ARMY', 'Capt. Samuel Finley', 'Two 6-pounders.', 'S138'),
    ('G-BR-ARMY', 'The British army under Cornwallis', 'Cornwallis\'s army', CR, 'Great Britain', 'Infantry', 'Army', 'S138; S139; S144', 'The column on the march; its units leave it as they deploy. Hamilton\'s Royal North Carolina Regiment went with the baggage to Bell\'s Mill and is not on the map (S139, in S138, p. 21).',
     None, 'Lt. Gen. Charles, Earl Cornwallis', 'Some 2,200, about 2,000 on the field (S138, p. 127). About 2,200 with 1,900 engaged (S144, p. 150); 1,924 on the battlefield (S144, p. 116). "1,900 regulars" (S85, p. 98).', 'S138; S144; S85'),
    ('G-BR-HQ', 'Cornwallis\'s headquarters', 'Cornwallis (HQ)', CR, 'Great Britain', 'Infantry', 'Headquarters', 'S138; S139', 'On the road with the guns; he had two horses shot under him (S138, p. 63 n. 22).', 'G-BR-ARMY', 'Lt. Gen. Charles, Earl Cornwallis', None, 'S138'),
    ('G-BR-TARL', 'British Legion: the cavalry', 'Tarleton', CR, 'Loyalist', 'Cavalry', 'Squadrons', 'S138; S142', 'The advance guard in the morning; kept in column on the road in reserve during the battle (S138, pp. 45-46).',
     'G-BR-ARMY', 'Lt. Col. Banastre Tarleton', 'Some 272 (S138, p. 45; S144, p. 74).', 'S138; S144'),
    ('G-BR-JAG', 'Ansbach Jägers', 'Jägers', CR, 'Germany', 'Infantry', 'Company', 'S138; S142', 'Riflemen from Ansbach-Bayreuth; advance guard, then the extreme left with the 33rd (S138, p. 45).', 'G-BR-ARMY', 'Capt. Friedrich von Roeder (S144, p. 150)', '84 (S138, p. 45; S144, p. 150).', 'S138; S144'),
    ('G-BR-GLI', 'Light infantry of the Guards', 'Guards light infantry', CR, 'Great Britain', 'Infantry', 'Company', 'S138; S142', 'Advance guard, then the extreme left with the 33rd.', 'G-BR-GDS', None, 'Perhaps 50 (S138, p. 45). 100 (S144, p. 74); 90 (p. 150).', 'S138; S144'),
    ('G-BR-WEB', 'Webster\'s brigade (the left)', 'Webster', CR, 'Great Britain', 'Infantry', 'Brigade', 'S138; S139', 'The 23rd and 33rd Foot, north of the road.', 'G-BR-ARMY', 'Lt. Col. James Webster (mortally wounded)', 'Less than 500 (S138, p. 45). 472 (S144, p. 150).', 'S138; S144'),
    ('G-BR-23', '23rd Foot (Royal Welch Fusiliers)', '23rd', CR, 'Great Britain', 'Infantry', 'Regiment', 'S138; S143', 'Came up to support Tarleton in the morning; next to the road on the left in the battle.', 'G-BR-WEB', 'Capt. Thomas Peter (S144, p. 150)', '238 (S138, p. 45).', 'S138; S144'),
    ('G-BR-33', '33rd Foot', '33rd', CR, 'Great Britain', 'Infantry', 'Regiment', 'S138; S139', 'Webster\'s own regiment, on the left of the 23rd.', 'G-BR-WEB', 'Lt. Col. James Webster (S138); Capt. Frederick Cornwallis (S144, p. 150)', '234 (S138, p. 45). 238 (S144, p. 150).', 'S138; S144'),
    ('G-BR-LES', 'Leslie\'s brigade (the right)', 'Leslie', CR, 'Great Britain', 'Infantry', 'Brigade', 'S138; S139', 'The 71st and the Regiment von Bose, south of the road.', 'G-BR-ARMY', 'Maj. Gen. Alexander Leslie', '565 (S138, p. 45; S144, p. 150).', 'S138; S144'),
    ('G-BR-71', '2nd Battalion, 71st Foot (Fraser\'s Highlanders)', '71st', CR, 'Great Britain', 'Infantry', 'Regiment', 'S138; S139', 'South of the road, next to it.', 'G-BR-LES', 'Capt. R. Hutchison (S144, p. 150)', '244 (S138, p. 45).', 'S138; S144'),
    ('G-BR-BOSE', 'Regiment von Bose (Hesse-Cassel)', 'von Bose', CR, 'Germany', 'Infantry', 'Regiment', 'S138; S139', 'The right of the line; drawn off south-east after Lee and Campbell.', 'G-BR-LES', 'Maj. Johann du Buy', '321 (S138, p. 45). 244 (S144, p. 150).', 'S138; S144'),
    ('G-BR-GDS', 'Brigade of Guards', 'Guards', CR, 'Great Britain', 'Infantry', 'Brigade', 'S138; S139', 'Two battalions, a grenadier and a light company, split between the two wings as supports.', 'G-BR-ARMY', 'Brig. Gen. Charles O\'Hara (wounded)', '481 (S144, p. 150).', 'S138; S144'),
    ('G-BR-1GDS', '1st Battalion of Guards', '1st Guards', CR, 'Great Britain', 'Infantry', 'Battalion', 'S138; S139', 'In support of the right; brought up on the right of von Bose and drawn into the fight in the south.', 'G-BR-GDS', 'Lt. Col. Chapple Norton', 'About 200 (S138, p. 45). 180 (S144, p. 150).', 'S138; S144'),
    ('G-BR-2GDS', '2nd Battalion of Guards', '2nd Guards', CR, 'Great Britain', 'Infantry', 'Battalion', 'S138; S139', 'In support of the left; filled the gap by the road and first reached the open ground before the Continentals.', 'G-BR-GDS', 'Lt. Col. James Stuart (killed)', 'With the grenadiers perhaps 250 (S138, p. 45). 180 (S144, p. 150).', 'S138; S144'),
    ('G-BR-GREN', 'Grenadier company of the Guards', 'Guards grenadiers', CR, 'Great Britain', 'Infantry', 'Company', 'S138; S139', 'With the 2nd Battalion.', 'G-BR-GDS', None, '90 (S144, p. 150).', 'S144'),
    ('G-BR-RA', 'Royal Artillery: Macleod\'s guns', 'Royal Artillery', CR, 'Great Britain', 'Artillery', 'Section', 'S138; S139', 'Kept to the road throughout. How many guns, and of what weight, is disputed: GH07.', 'G-BR-ARMY', 'Lt. John Macleod', 'Four 3-pounders and some 50 men (S138, p. 45). Cornwallis brings up "two three-pounders" at the third line (S139).', 'S138; S139'),
]

# ---------------------------------------------------------------- the ground
def q(x, y): return tuple(reversed(R.q51([(x, y)])[0]))          # a point on the 1951 sheets -> (lat, lon)
APP = [tuple(reversed(p)) for p in R.q51(R.APPROACH)][::-1]       # New Garden to the edge of the 1951 sheet, south-west to north-east
SW = [tuple(reversed(p)) for p in R.q51(R.SALISBURY_SW)][::-1]    # the road from Deep River, west to east
FIELD = [tuple(reversed(p)) for p in R.g2(R.ROAD_W) + R.p1(R.ROAD_E)]
ROADLL = SW + APP[1:] + FIELD                                      # the whole road, Deep River side to the Hillsboro side
REEDY = [tuple(reversed(p)) for p in R.p1(R.REEDY)]


def near(pt, line=None):
    line = line or ROADLL
    return min(range(len(line)), key=lambda i: G.metres(line[i], pt))


def road(a, b):
    """The road between the vertices nearest two points, in the order given."""
    i, j = near(a), near(b)
    seg = ROADLL[min(i, j):max(i, j) + 1]
    return seg if i <= j else seg[::-1]


MH = q(445, 1215)            # New Garden Meeting House (by the junction with the Friendly road)
JUNCT = q(440, 1232)
XROAD = q(370, 905)          # the cross road (Ballinger Road), bench mark 912 on the 1951 sheet
LANE = q(700, 420)           # "the Lane", between the 874 and 857 junctions of the 1951 sheet
BIVOUAC = q(1090, 140)       # Lee's post the night before, by his own distances
SWEDGE = q(140, 1325)
CREEK = G.gp(2, 97, 648)     # the road at Little Horsepen Creek
NORTH = G.hp(1, 1638, 150)   # the Reedy Fork road at the top of Hatch's sheet

# ---------------------------------------------------------------- positions
POS = []
B1 = ('Read from Hatch\'s plan No. %s (S138), in the pixels of the plate, and laid on the ground by the park boundary of 1971 against today\'s boundary on the USGS Topo base map (S147): '
      'pipeline/guilford_geo.py. Boundaries fit to about 15 m; Hatch\'s own creeks and road lie up to 70 m from today\'s survey, so the unit is good to about 75 m and no better than his judgement.')
BM = ('Placed at a road junction the staff ride names (S144, pp. 72-74 and Map 13), on New Garden Road as the 1951 USGS sheet draws it (S146). The fight moved along the road; the junction is a point of reference, not a measured place.')
TB_AFT = ('Clock from the staff ride\'s maps and chronology (S144, pp. 89-113, 153): the British advance 1300, the first line breaks 1315, the second line 1330 to 1430, the third line 1445 to 1530. '
          'Cornwallis has the action begin "about half an hour past one" (S139), Saumarez "about one o\'clock" (S143), Greene "about twelve" (S140): the row keeps half an hour either side (GH01).')
TB_MORN = ('The hour of the morning fights is disputed (GH02). The playback follows Seymour\'s journal, "about nine o\'clock ... about the space of an hour and a half" (S143), and the staff ride\'s end at 1000 (S144, p. 74). '
           'Lee has the sun "just risen above the trees" (S141); the staff ride\'s stand text says about 0700, 0900 and 1000, its chronology 0400-0500 (S144, pp. 72-73, 153). The row keeps from 06:30.')
TB_FORM = ('Houston: "about ten o\'clock ... we immediately fell into our ranks, and our brigades marched out" (S143, in S138, p. 33); the staff ride\'s chronology has Greene deploy at 0600 (S144, p. 153): GH03. In place by the time the British came in sight, about noon (S140).')


def P(pid, unit, show, activity, place, geom, plan, sources, wording, method, conf, pages, cross, notes=None, tb=None, prec=75, cconf='low', csrc='map_read', basis=None, early=30, late=30):
    """One Positions row. `show` is (from, to) as HH:MM; the record's own times run `early` minutes before to `late` after. `geom` is a (lat, lon) or a pair of them."""
    f, t = show; line = isinstance(geom[0], tuple); a, b = (geom if line else (geom, None))
    POS.append(dict(pos_id=pid, campaign_id=CAMP, battle_id=BATTLE, unit_id=unit, start_earliest=T(plus(f, -early)), start_latest=T(plus(f, late)), end_earliest=T(plus(t, -early)), end_latest=T(plus(t, late)),
                    time_basis=tb or TB_AFT, activity=activity, place_description=place, geometry='line' if line else 'point', lat=a[0], lon=a[1], line_end_lat=b[0] if b else None, line_end_lon=b[1] if b else None,
                    coord_source=csrc, coord_precision_m=prec, coordinate_basis=basis or (B1 % plan), coordinate_confidence=cconf, source_ids=sources, source_wording=wording, position_method=method,
                    overall_confidence=conf, notes=notes, review_status=REV, show_from=T(f), show_to=T(t), source_pages=pages, cross_checked_by=cross))


def L(n, a, b): return G.hl(n, a, b)
def D(n, a): return G.gp(n, *a)
def mid(a, b, f=0.5): return (round(a[0] + (b[0] - a[0]) * f, 6), round(a[1] + (b[1] - a[1]) * f, 6))
SRC = 'S138; S144'
M = dict(tb=TB_MORN, prec=400, csrc='modern_map', basis=BM, early=150, late=60)
F = dict(tb=TB_FORM, early=240, late=60)

# ---- the Americans: the camp, then the three lines (plan No. 2)
P('GP01', 'G-US-ARMY', ('08:00', '10:15'), 'In camp about the courthouse', 'Guilford Courthouse', COURT, 1, 'S138; S140; S143', 'S140: "The army was drawn up on a large hill of ground"; S143 Houston: "lying about our fires" until about ten. No source maps the camp.', 'inferred', 'low',
  'S138 pp. 29, 33', 'S144', 'One symbol for the army in camp; the lines come out of it from 10:15. The camp\'s extent is not known.', tb=TB_FORM, prec=400, early=120, late=60)
W1 = 'S140: the front line "just on the edge of the woods, and back of a fence, which ran parallel with the line, with an open field directly in their front". S138, p. 34: Eaton north of the road, Butler south, each with a front of perhaps 400 yards. S144, p. 84: "a large rail fence ran along the east edge of the fields".'
P('GP02', 'G-US-EATON', ('10:45', '13:14'), 'Line of battle behind the rail fence (first line)', 'North of the great road, at the east edge of the Hoskins fields', L(2, (508, 327), (548, 505)), 2, 'S138; S140; S144', W1, 'stated', 'low',
  'S138 pp. 34-35, plan 2; S140 in S138 p. 29; S144 pp. 84, 87, Map 16 p. 89', 'S144; S140', 'Which brigade stood north of the road is disputed (GH04): Hatch, and the staff ride\'s Map 16, put Eaton here.', **F)
P('GP03', 'G-US-BUTLER', ('10:45', '13:16'), 'Line of battle behind the rail fence (first line)', 'South of the great road, at the east edge of the corn fields', L(2, (570, 553), (633, 772)), 2, 'S138; S140; S144', W1 + ' S143 Stuart (71st): "a very deadly fire" from men "lying on the ground behind a rail fence".', 'stated', 'low',
  'S138 pp. 29, 34-35, 52-53, plan 2; S144 pp. 84, 93, Map 16 p. 89', 'S144; S140', 'GH04.', **F)
P('GP04', 'G-US-SING', ('10:45', '13:02'), 'Two 6-pounders in the road, in front of the first line', 'The great road at the first line', D(2, (553, 538)), 2, 'S138; S139; S141', 'S140: the front line "with two field pieces". S138, p. 36: "In the road itself ... just in advance of the line". S139: "withdrawn to the continentals before the attack".', 'stated', 'low',
  'S138 pp. 29, 36, 41-43, plan 2; S144 p. 87', 'S144; S139', None, **F)
WR = 'S140: "Washington, with the dragoons of the 1st and 3rd regiments, a detachment of light infantry composed of continental troops, and a regiment of riflemen, under Colonel Lynch, formed a corps of observation for the security of our right flank." S138, p. 35: in the woods, continuing the line "obliquely forward", the cavalry behind the join.'
P('GP05', 'G-US-LYNCH', ('10:45', '13:20'), 'Riflemen in the woods on the right flank, angled forward', 'North end of the first line', L(2, (432, 268), (492, 312)), 2, SRC + '; S140', WR, 'stated', 'low', 'S138 p. 35, plan 2; S144 p. 87, Map 16', 'S144', None, **F)
P('GP06', 'G-US-KIRK', ('10:45', '13:20'), 'On the right of the riflemen', 'Extreme right of the first line', L(2, (395, 243), (425, 262)), 2, SRC + '; S140', WR, 'stated', 'low', 'S138 p. 35, plan 2; S144 Map 16', 'S144', None, **F)
P('GP07', 'G-US-WASH', ('10:45', '13:20'), 'Cavalry in the woods behind the right flank', 'Behind the join of Eaton\'s line and the riflemen', L(2, (525, 250), (567, 282)), 2, SRC + '; S140', WR, 'stated', 'low', 'S138 p. 35, plan 2; S144 Map 16', 'S144', None, **F)
P('GP08', 'G-US-LAWS', ('10:45', '14:05'), 'Line of battle in the woods (second line)', 'North of the great road, some 300 yards behind the first line', L(2, (692, 183), (772, 458)), 2, SRC + '; S140',
  'S140: "The second line was in the woods, about three hundred yards in the rear of the first". S138, pp. 36-37: Lawson north of the road, Stevens south. S144, p. 95: Randolph on the right, Holcombe in the middle, Skipwith on the left.', 'stated', 'low',
  'S138 pp. 29, 36-37, plan 2; S144 pp. 95, Map 18 p. 99', 'S144; S140', 'The distance between the lines: GH09. Hatch draws the line about 1,000 yards long.', **F)
P('GP09', 'G-US-STEV', ('10:45', '14:28'), 'Line of battle in the woods (second line), sentinels twenty yards behind', 'South of the great road, some 300 yards behind the first line', L(2, (780, 484), (870, 745)), 2, SRC + '; S140',
  'S138, p. 37: Stevens "southward from the road"; "Some twenty yards behind his line he set up another line of sentinels". S144, p. 97: the brigade "in a reverse slope defense"; its line ran south-east into today\'s Forest Lawn Cemetery.', 'stated', 'low',
  'S138 p. 37, plan 2; S144 pp. 97-98, Map 18 p. 99', 'S144', 'GH09.', **F)
W3 = ('S140: "the continental troops about four hundred yards in the rear of the second, with a double front, as the hill drew to a point where they were posted". S138, p. 38: all north of the road, some 500 yards behind the second line; from left to right the 2nd Maryland, 1st Maryland, Hawes, Green; two guns in the curve between the brigades. '
      'S144, p. 104: the line stood "about 300 meters east" of the Regulars Marker, "on a ridgeline overlooking Richland Creek"; S145, p. 4: "about 400 yards east of its previously interpreted position".')
N3 = 'Where the third line stood was disputed for a century (GH05): Hatch, the park\'s landscape report and the staff ride agree on this eastern ground.'
P('GP10', 'G-US-GREEN', ('10:45', '15:08'), 'Line of battle (third line, right)', 'Right of the Continental line, north-west of the courthouse', L(2, (1048, 122), (1092, 165)), 2, SRC + '; S140; S145', W3, 'stated', 'low', 'S138 pp. 29, 38, plan 2; S144 pp. 104, 110; S145 p. 4', 'S144; S145', N3, **F)
P('GP11', 'G-US-HAWES', ('10:45', '15:25'), 'Line of battle (third line)', 'Left of Huger\'s brigade', L(2, (1095, 170), (1140, 222)), 2, SRC + '; S140; S145', W3, 'stated', 'low', 'S138 pp. 29, 38, plan 2; S144 pp. 104, 110; S145 p. 4', 'S144; S145', N3, **F)
P('GP12', 'G-US-FIN', ('10:45', '15:30'), 'Two 6-pounders in the curve of the third line', 'Between Huger\'s and Williams\'s brigades', D(2, (1151, 236)), 2, SRC, 'S138, p. 38: "In the curve of the line between his two brigades Greene placed two of his six pounders with Lieutenant Finley". S142: "two six-pounders were placed on a small eminence which looked upon the road".', 'stated', 'low',
  'S138 p. 38, plan 2', 'S142', 'Abandoned in the retreat, the horses being killed (S140, in S138, p. 84).', **F)
P('GP13', 'G-US-1MD', ('10:45', '14:47'), 'Line of battle (third line), hidden by a copse', 'Right of Williams\'s brigade', L(2, (1160, 240), (1200, 270)), 2, SRC + '; S140; S145', W3 + ' S141: "a small copse of wood concealing Gunby".', 'stated', 'low', 'S138 pp. 29, 38, 76, plan 2; S144 pp. 104, 110; S145 p. 4', 'S144; S145', N3, **F)
P('GP14', 'G-US-2MD', ('10:45', '15:02'), 'Line of battle (third line, left), by the road', 'Left of the Continental line, above the great road', L(2, (1215, 277), (1268, 293)), 2, SRC + '; S140; S145', W3 + ' S144, p. 110: the 2nd Maryland "positioned parallel to the New Garden Road".', 'stated', 'low', 'S138 pp. 29, 38, 75, plan 2; S144 pp. 104, 110; S145 p. 4', 'S144; S145', N3, **F)
P('GP15', 'G-US-HQ', ('10:45', '15:12'), 'Greene with the third line', 'Behind the centre of the Continental line', D(2, (1250, 200)), 2, 'S138', 'S138, p. 40: "General Greene returned to a position with his third line to await developments". The spot is not given.', 'inferred', 'low', 'S138 pp. 39-40', 'S144', 'Before this he rode along the first line (S138, p. 39).', **F)

# ---- Lee's corps in the morning, and on the left flank
P('GP20', 'G-US-LEEC', ('08:00', '08:25'), 'Lee\'s post on the great road', 'Between the courthouse and New Garden', BIVOUAC, 2, 'S141; S138', 'S141, in S138, p. 23: Lee "was immediately advanced on the road to the Quaker meeting-house, with orders to post himself within two or three miles of the court-house". The staff ride puts him at New Garden itself (S144, p. 73).', 'inferred', 'low',
  'S138 p. 23; S144 p. 73', 'S144', 'Placed about two and a half miles from the courthouse on the 1951 road. GH02 and GH10.', **dict(M, prec=800))
P('GP21', 'G-US-LEEC', ('08:40', '08:48'), 'Charge in the lane: Tarleton\'s leading section overthrown', '"The Lane", near today\'s New Garden and Hobbs roads', LANE, 2, 'S141; S144; S142',
  'S141, in S138, p. 24: "This meeting happened in a long lane, with very high curved fences on each side of the road". S144, p. 72: "near the intersection of the modern New Garden Road and Hobbs Road, is \'The Lane\'". S142: "the charge of their cavalry was spirited".', 'stated', 'low',
  'S138 pp. 23-25; S144 pp. 72, 74, Map 13 p. 77', 'S144; S142', 'Where the lane was: GH10.', **M)
P('GP22', 'G-US-LEEC', ('09:00', '09:08'), 'Rides into the Guards\' volley at the meeting house; falls back', 'New Garden Meeting House', MH, 2, 'S141; S144', 'S141, in S138, p. 25: at the meeting house "they encountered the British Guards" who gave "the American cavalry a general fire ... he ordered a retreat". S144, p. 73: the second fight at today\'s West Friendly Avenue and New Garden Road.', 'stated', 'low',
  'S138 p. 25; S144 pp. 73-74', 'S144', None, **M)
P('GP23', 'G-US-LEEC', ('09:20', '10:00'), 'Covers the infantry at the cross road; delaying action', 'The cross road north of the meeting house (Ballinger Road)', XROAD, 2, 'S144; S141', 'S144, p. 74: Lee\'s dragoons frustrated the pursuit, "allowing the American infantry time to reorganize at the Ballenger and Great Salisbury Cross Roads ... until 1000, when Lee broke contact and withdrew, unpursued". S141: he "drew off his infantry; and, covering them ... retired".', 'stated', 'low',
  'S144 pp. 73-74; S138 p. 27', 'S141', None, **M)
P('GP30', 'G-US-LEEI', ('08:00', '08:40'), 'Lee\'s post on the great road', 'Between the courthouse and New Garden', mid(BIVOUAC, APP[near(BIVOUAC, APP) + 1], 0.5), 2, 'S141; S138', 'S141: Lee "directed the infantry and rifle infantry to follow, the first on his right, and the second on his left".', 'inferred', 'low', 'S138 pp. 23-24', 'S144', None, **dict(M, prec=800))
P('GP31', 'G-US-LEEI', ('09:06', '09:25'), 'Comes up at a run and fires on the Guards', 'North of New Garden Meeting House', mid(MH, XROAD, 0.25), 2, 'S141; S144', 'S141, in S138, p. 25: "the Legion infantry came running up with trailed arms, and opened a well-aimed fire upon the guards". S144, p. 74: "his supporting light infantry and riflemen had moved up in support".', 'inferred', 'low', 'S138 p. 25; S144 p. 74', 'S144', None, **M)
P('GP32', 'G-US-LEEI', ('09:30', '10:00'), 'Reforms at the cross road; falls back', 'The cross road (Ballinger Road)', mid(XROAD, MH, 0.08), 2, 'S144; S141', 'S144, p. 74 (as GP23).', 'stated', 'low', 'S144 p. 74', 'S141', None, **M)
P('GP40', 'G-US-CAMP', ('08:00', '08:40'), 'Lee\'s post on the great road', 'Between the courthouse and New Garden', mid(BIVOUAC, APP[near(BIVOUAC, APP) - 1], 0.5), 2, 'S141; S140', 'S140, in S138, p. 26 n. 15: "Lee, with his legion, his infantry and part of his riflemen, met the enemy".', 'inferred', 'low', 'S138 pp. 23-24, 26', 'S144', 'How many of Campbell\'s riflemen went out is not said.', **dict(M, prec=800))
P('GP41', 'G-US-CAMP', ('09:10', '09:25'), 'Volley on the Guards from the left of the cavalry', 'North-west of New Garden Meeting House', (round(mid(MH, XROAD, 0.3)[0], 6), round(mid(MH, XROAD, 0.3)[1] - 0.0016, 6)), 2, 'S141; S142', 'S141, in S138, p. 25: "a volley from the riflemen under Colonel Campbell, who had taken post on the left of the cavalry". S142: "Colonel Campbell\'s mountaineers were dispersed with considerable loss".', 'stated', 'low', 'S138 pp. 25-26', 'S144', None, **M)
P('GP42', 'G-US-CAMP', ('09:30', '10:00'), 'Falls back with the Legion', 'The cross road (Ballinger Road)', (XROAD[0], round(XROAD[1] - 0.0012, 6)), 2, 'S144', 'S144, p. 74 (as GP23).', 'inferred', 'low', 'S144 p. 74', 'S141', None, **M)
WL = 'S140: "Lee, with his legion, a detachment of light infantry, and a corps of riflemen, under Colonel William Campbell, formed a corps of observation for the security of our left flank." S138, p. 35: in the woods, angled forward from the south end of the militia line, the horse behind the join.'
P('GP24', 'G-US-LEEC', ('11:15', '13:20'), 'Cavalry behind the left flank', 'Behind the south end of the first line', L(2, (700, 820), (690, 858)), 2, SRC + '; S140', WL, 'stated', 'low', 'S138 p. 35, plan 2; S144 p. 87, Map 16', 'S144', None, tb=TB_FORM, early=90, late=45)
P('GP33', 'G-US-LEEI', ('11:15', '13:20'), 'On the extreme left, in the woods', 'South end of the first line', L(2, (625, 870), (609, 898)), 2, SRC + '; S140', WL, 'stated', 'low', 'S138 p. 35, plan 2; S144 Map 16', 'S144', None, tb=TB_FORM, early=90, late=45)
P('GP43', 'G-US-CAMP', ('11:15', '13:20'), 'Riflemen in the woods on the left flank, angled forward', 'South end of the first line', L(2, (633, 787), (650, 825)), 2, SRC + '; S140', WL, 'stated', 'low', 'S138 p. 35, plan 2; S144 Map 16', 'S144', None, tb=TB_FORM, early=90, late=45)

# ---- the British: the march, the morning, the deployment
P('GP100', 'G-BR-ARMY', ('08:00', '08:22'), 'Column on the march from Deep River', 'The great road south-west of New Garden', SWEDGE, 2, 'S139; S142; S143',
  'S139: "I marched with the rest of the corps at daybreak". S143, orderly book: "ready to march precisely At half past five O\'clock". S142: "The British had proceeded seven miles on the great Salisbury road to Guilford when the light troops drove in a picket".', 'inferred', 'low',
  'S138 pp. 21-22', 'S144', 'Which road of 1781 the column came by is not established: drawn on the main road of the 1951 sheet. The camp at Deep River Friends Meeting House is off the map, 8 miles south-west (S144, p. 73).', **dict(M, prec=1000))
P('GP101', 'G-BR-ARMY', ('09:25', '10:30'), 'Head of the column up at New Garden; the army closes and reforms', 'New Garden Meeting House', JUNCT, 2, 'S142; S138', 'S142: the light infantry and Legion "made impression upon their center, before the 23d regiment arrived to give support". S138, p. 29: "Cornwallis reformed his line of march and continued".', 'inferred', 'low', 'S138 pp. 26, 29; S144 p. 74', 'S144', None, **M)
P('GP102', 'G-BR-ARMY', ('12:25', '12:34'), 'Head of the column crosses Little Horsepen Creek and comes under fire', 'The great road at Little Horsepen Creek', CREEK, 2, 'S138; S139; S144',
  'S139: "we found the rebel army posted on rising grounds about a mile and a half from the court house". S138, p. 41: the head of the column "began to move through the curving defile across Little Horse Pen Creek". S144, p. 84: lead elements "arrived at this general location around 1230".', 'stated', 'low',
  'S138 pp. 29, 41-43, plan 2; S144 p. 84', 'S144; S139', 'The staff ride\'s chronology says 1200 (p. 153).', early=45, late=45)
P('GP110', 'G-BR-TARL', ('08:15', '08:28'), 'Advance guard: drives in Heard\'s picket', 'The great road south-west of New Garden', mid(SWEDGE, JUNCT, 0.6), 2, 'S142; S141', 'S142: "the light troops drove in a picket of the enemy". S141, in S144, p. 74: Heard "followed leisurely by the enemy\'s horse".', 'inferred', 'low', 'S138 pp. 21-24; S144 pp. 73-74', 'S144', 'Where the picket stood is not known.', **dict(M, prec=1000))
P('GP111', 'G-BR-TARL', ('08:40', '08:46'), 'Charged in the lane; the leading section unhorsed; Tarleton sounds the retreat', '"The Lane"', (round(LANE[0] - 0.0009, 6), round(LANE[1] - 0.0009, 6)), 2, 'S141; S142; S144', 'S141, in S138, p. 24: "The whole of the enemy\'s section was dismounted ... Tarleton retired with celerity". S144, p. 74: "several Loyalist dragoons unhorsed and captured".', 'stated', 'low', 'S138 p. 24; S144 p. 74', 'S144', 'GH10.', **M)
P('GP112', 'G-BR-TARL', ('08:58', '09:20'), 'Falls back on the Guards light infantry at the meeting house', 'New Garden Meeting House', (round(MH[0] - 0.0012, 6), round(MH[1] - 0.0004, 6)), 2, 'S141; S144', 'S141: Tarleton "took an obscure way toward the British camp". S144, p. 74: "withdrew along a dirt trail to the east of the Salisbury Road".', 'inferred', 'low', 'S138 p. 25; S144 p. 74', 'S144', None, **M)
P('GP113', 'G-BR-TARL', ('09:30', '10:20'), 'Follows Lee to the cross road; not allowed to pursue', 'The cross road (Ballinger Road)', (round(XROAD[0] - 0.0022, 6), round(XROAD[1] + 0.0006, 6)), 2, 'S142; S144', 'S142: "The pursuit was not pushed very far, as there were many proofs ... that General Greene was at hand".', 'inferred', 'low', 'S138 p. 26; S144 p. 74', 'S144', 'Tarleton was shot in the right hand: in this morning\'s fight by his own letter to Lee (S138, p. 27 n. 20), in the fight in the south by the staff ride (S144, p. 102).', **M)
WG = 'S141, in S138, p. 25: the British Guards "displayed in a moment giving the American cavalry a general fire". S142: "the gallantry of the light infantry of the guards, assisted by the legion". S144, p. 74: "a hasty ambush by the Guards Light Infantry".'
P('GP120', 'G-BR-GLI', ('08:55', '09:25'), 'Volley on Lee\'s cavalry at the meeting house', 'New Garden Meeting House yard', (round(MH[0] - 0.0005, 6), round(MH[1] + 0.0003, 6)), 2, 'S141; S142; S144', WG, 'stated', 'low', 'S138 pp. 25-26; S144 p. 74', 'S144', None, **M)
P('GP121', 'G-BR-GLI', ('09:35', '10:20'), 'Presses Lee\'s infantry towards the cross road', 'South of the cross road', mid(XROAD, MH, 0.3), 2, 'S142; S144', 'S142 (as GP120). S144, p. 74: "A sizable meeting engagement developed".', 'inferred', 'low', 'S138 p. 26; S144 p. 74', 'S144', None, **M)
P('GP125', 'G-BR-JAG', ('08:57', '09:25'), 'With the Guards light infantry at the meeting house', 'New Garden Meeting House', (round(MH[0] - 0.0008, 6), round(MH[1] - 0.0010, 6)), 2, 'S142; S144', 'S142: "between twenty and thirty of the guards, dragoons, and yagers, were killed". S144, Map 13 draws the jägers at the junction.', 'inferred', 'low', 'S138 p. 26; S144 Map 13 p. 77', 'S144', None, **M)
P('GP126', 'G-BR-JAG', ('09:35', '10:20'), 'Follows towards the cross road', 'South of the cross road', mid(XROAD, MH, 0.4), 2, 'S144', 'S144, p. 74 (as GP121).', 'inferred', 'low', 'S144 p. 74', 'S142', None, **M)
P('GP130', 'G-BR-23', ('09:28', '10:25'), 'Comes up to support the advance guard; Lee gives way', 'On the great road at New Garden', mid(XROAD, MH, 0.55), 2, 'S142; S143; S144', 'S142: "before the 23d regiment arrived to give support to the advanced troops". S143 Lamb: "until the 23rd regiment advancing to the support of Tarleton compelled him to give way". S144, p. 74: "reinforced by the lead battalion of the 23d".', 'inferred', 'low', 'S138 pp. 26, 28; S144 p. 74', 'S144', None, **M)

WD = ('S139: "On the right, the regiment of Bose and the 71st regiment, led by Major-general Leslie, and supported by the 1st battalion of guards; on the left, the 23d and 33d regiments, led by Lieutenant-colonel Webster, and supported by the grenadiers and 2d battalion of guards ...; '
      'the Yagers and light infantry of the guards remained in the wood on the left of the guns, and the cavalry in the road". S138, pp. 45: Leslie on a 550-yard front south of the road, Webster on 450 yards north of it. S144, p. 84: the deployment "took roughly 30 minutes".')
DT = ('12:42', '13:00'); DK = dict(early=45, late=45)
P('GP140', 'G-BR-33', DT, 'Line of battle (the left of the line)', 'North of the road, east of Little Horsepen Creek', L(2, (237, 380), (262, 490)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S139 in S138 p. 44; S144 p. 84, Map 16 p. 89', 'S144; S139', None, **DK)
P('GP150', 'G-BR-23', DT, 'Line of battle, its right on the road', 'North of the road, east of Little Horsepen Creek', L(2, (262, 500), (292, 600)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84, Map 16', 'S144; S139', None, **DK)
P('GP160', 'G-BR-71', DT, 'Line of battle, its left on the road', 'South of the road, by the Hoskins house', L(2, (285, 622), (327, 745)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84, Map 16', 'S144; S139', None, **DK)
P('GP170', 'G-BR-BOSE', DT, 'Line of battle (the right of the line)', 'South of the road, on the right of the 71st', L(2, (330, 772), (372, 878)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84, Map 16', 'S144; S139', None, **DK)
P('GP180', 'G-BR-1GDS', ('12:44', '13:10'), 'In support behind the right', 'Behind the 71st and von Bose', L(2, (272, 740), (298, 806)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84', 'S144; S139', None, **DK)
P('GP190', 'G-BR-2GDS', ('12:44', '13:08'), 'In support behind the left, by the road', 'Behind the 23rd', L(2, (236, 622), (255, 683)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84', 'S144; S139', 'Hatch draws it south of the road here though it supported the left.', **DK)
P('GP200', 'G-BR-GREN', ('12:44', '13:08'), 'In support behind the left', 'Behind the 23rd, north of the road', L(2, (228, 592), (236, 614)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84', 'S144; S139', None, **DK)
P('GP127', 'G-BR-JAG', ('12:40', '13:05'), 'In the wood on the left of the guns', 'North of the road, behind the line', L(2, (187, 585), (193, 600)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84', 'S144; S139', None, **DK)
P('GP122', 'G-BR-GLI', ('12:40', '13:05'), 'In the wood on the left of the guns', 'North of the road, behind the line', L(2, (195, 605), (201, 625)), 2, SRC + '; S139', WD, 'stated', 'low', 'S138 pp. 44-45, plan 2; S144 p. 84', 'S144; S139', None, **DK)
P('GP114', 'G-BR-TARL', ('12:40', '13:28'), 'Cavalry in column in the road, in reserve', 'The great road, behind the guns', L(2, (160, 655), (218, 643)), 2, SRC + '; S139; S142', WD + ' S142: Tarleton "was ordered to keep his regiment in reserve till the infantry could penetrate through the woods".', 'stated', 'low', 'S138 pp. 44-46, plan 2; S144 p. 84', 'S144; S142', None, **DK)
P('GP210', 'G-BR-RA', ('12:35', '13:05'), 'Guns in the road answer Singleton: the cannonade', 'The great road by the Hoskins farm', D(2, (295, 605)), 2, SRC + '; S139; S141',
  'S139: "I ordered Lieutenant Macleod to bring forward the guns and cannonade their center". S141: Macleod "stationing himself in the road near the rivulet, returned our fire". S143 Tucker: "A cannonade of half an hour". S144, p. 84: 3-pounders "along the road near the Hoskins farm".', 'stated', 'low',
  'S138 pp. 41-44, plan 2; S144 p. 84', 'S144; S139', 'How many guns: GH07. Lt. O\'Hara of the artillery was killed here.', **DK)
P('GP220', 'G-BR-HQ', ('12:35', '13:10'), 'Cornwallis on the road with the guns', 'The great road by the Hoskins farm', D(2, (282, 610)), 2, 'S138; S144', 'S144, p. 84: "Cornwallis remained on the road, where he retained control of the 3-pounders" and the reserve.', 'stated', 'low', 'S144 p. 84; S138 p. 44', 'S139', None, **DK)

# ---- 13:00 to 13:20: the advance and the first line
WF = ('S139, as Tarleton words it (S142): "The militia allowed the front line to approach within one hundred and fifty yards before they gave their fire ... The Kings troops threw in their fire, and charged rapidly with their bayonets". S143 Lamb: "within forty yards of the enemy\'s line ... their whole force had their arms presented, and resting on a rail fence". '
      'S144, p. 90: the first line broke "at about 1315".')
for pid, unit, a, b, place in (('GP141', 'G-BR-33', (490, 300), (520, 400), 'the north part of Eaton\'s fence and the woods beyond'), ('GP151', 'G-BR-23', (522, 410), (548, 502), 'Eaton\'s fence, north of the road'),
                               ('GP161', 'G-BR-71', (570, 553), (600, 660), 'Butler\'s fence, south of the road'), ('GP171', 'G-BR-BOSE', (600, 665), (633, 772), 'the south part of Butler\'s fence')):
    P(pid, unit, ('13:12', '13:17'), 'Volley and bayonet charge at the rail fence', 'At ' + place, L(2, a, b), 2, SRC + '; S139; S143', WF, 'inferred', 'low', 'S138 pp. 47-52, 56, plan 3; S144 pp. 90, 93, Map 17 p. 91', 'S144; S139',
      'The regiment is put on the part of the militia line in its front; no source gives its place at the fence closer than that.')
WB = 'S140: the militia "waited the attack until the enemy got within 140 yards, when part of them began to fire, but a considerable part left the ground without firing at all". S138, plan 3: "North Carolina militia leaving the field", through and round the second line.'
P('GP16', 'G-US-EATON', ('13:26', '13:30'), 'Broken: leaving the field through the woods', 'Behind the second line, north of the road', D(3, (880, 260)), 3, SRC + '; S140', WB, 'inferred', 'low', 'S138 pp. 47-55, plan 3; S144 p. 90', 'S144; S140', 'Drawn leaving so the symbol does not vanish at the fence; then taken off the map. Most went home (S138, p. 120).')
P('GP17', 'G-US-BUTLER', ('13:28', '13:32'), 'Broken: leaving the field through the woods', 'Behind the second line, south of the road', D(3, (900, 620)), 3, SRC + '; S140', WB + ' S144, p. 93: several companies on the far left "fell back to join Colonel William Campbell\'s Virginia rifle battalion".', 'inferred', 'low', 'S138 pp. 47-55, plan 3; S144 p. 93', 'S144; S140', 'As GP16.')
P('GP18', 'G-US-SING', ('13:40', '15:02'), 'Guns on the left of the third line, by the 2nd Maryland', 'Above the great road, left of the Continental line', D(5, (1290, 298)), 5, SRC + '; S139', 'S138, p. 73: "Singleton had withdrawn his two to the left flank adjacent to the 2d Maryland". S139: the Guards "instantly attacked and defeated them, taking two six-pounders".', 'stated', 'low', 'S138 pp. 38, 73, 75, plan 5; S144 p. 110', 'S144; S139', 'Taken by the 2nd Guards about 15:02, retaken, and left on the field in the retreat.')

# ---- 13:20 to 14:40: the second line (plans No. 3 and 4)
W2 = ('S138, pp. 55-58: the flank corps overlapped the British line; Webster "changed his front to the left" with the 33rd, the jägers and Guards light infantry; the grenadiers and 2nd Guards filled the gap by the road; south of it the 71st struck Stevens almost alone. S140: the Virginians "kept up a heavy fire for a long time". '
      'S144, pp. 95-98: Lawson\'s brigade broke first, Stevens\'s when he was shot through the thigh; the second line fight ran from about 1330 to 1430.')
T2 = ('13:30', '14:15')
P('GP142', 'G-BR-33', T2, 'Changes front to the left against Lynch, Kirkwood and Washington, then Lawson\'s right', 'In the woods north of the road, at the second line', L(3, (624, 215), (660, 320)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55-56, 65-66, 70, plan 3; S144 p. 95, Map 18 p. 99', 'S144; S139')
P('GP128', 'G-BR-JAG', T2, 'On the extreme left with the 33rd', 'North end of the British line, in the woods', L(3, (600, 157), (606, 172)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55-56, 70, plan 3; S144 Map 18', 'S144; S139')
P('GP123', 'G-BR-GLI', T2, 'On the left with the 33rd', 'North end of the British line, in the woods', L(3, (611, 182), (620, 203)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55-56, 70, plan 3; S144 Map 18', 'S144; S139')
P('GP152', 'G-BR-23', ('13:30', '14:25'), 'Attacks Lawson\'s line; delayed by brushwood', 'In the woods north of the road, at the second line', L(3, (662, 337), (684, 400)), 3, SRC + '; S143', W2 + ' S143 Saumarez: the second line "was formed behind brushwood. Not being able to attack in front, the Fusiliers were obliged to take the ground to their left".', 'stated', 'low', 'S138 pp. 55, 58, 68, 70, plan 3; S144 p. 95', 'S144; S143')
P('GP201', 'G-BR-GREN', ('13:30', '14:25'), 'In the line between the 23rd and the 2nd Guards', 'North of the road, at the second line', L(3, (685, 410), (691, 425)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55-56, 70, plan 3; S144 p. 95', 'S144; S139')
P('GP191', 'G-BR-2GDS', ('13:30', '14:20'), 'Fills the gap by the road; breaks through Lawson\'s left', 'Just north of the road, at the second line', L(3, (692, 436), (708, 480)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55-56, 69-70, plan 3; S144 pp. 95, 98', 'S144; S139')
P('GP162', 'G-BR-71', ('13:30', '14:32'), 'Fights Stevens\'s brigade', 'In the woods south of the road, at the second line', L(3, (725, 500), (772, 630)), 3, SRC + '; S139', W2, 'stated', 'low', 'S138 pp. 55, 58, 68-70, plan 3; S144 pp. 97-98', 'S144; S139')
P('GP172', 'G-BR-BOSE', ('13:30', '13:50'), 'Turns south against Campbell and Lee', 'South of the 71st, facing the American left flank', L(3, (776, 683), (776, 780)), 3, SRC + '; S139', 'S139: Leslie brought "up the 1st battalion of guards to the right of the regiment of Bose". S141: Leslie turned "the regiment of Bose, with the battalion of guards, upon Lee".', 'stated', 'low', 'S138 pp. 55, 58, 63, plan 3; S144 pp. 93, 101', 'S144; S139')
P('GP181', 'G-BR-1GDS', ('13:22', '13:50'), 'Brought up on the right of von Bose', 'The extreme right, in the woods', L(3, (775, 808), (763, 868)), 3, SRC + '; S139', 'S139 (as GP172).', 'stated', 'low', 'S138 pp. 55, 63, plan 3; S144 p. 93', 'S144; S139')
P('GP211', 'G-BR-RA', ('13:30', '14:25'), 'Guns keep pace along the road', 'The great road, between the first and second lines', D(3, (655, 522)), 3, SRC + '; S139', 'S139: "the artillery keeping pace with them on the road, followed by the cavalry".', 'stated', 'low', 'S138 p. 58, plan 3', 'S144; S139')
P('GP221', 'G-BR-HQ', ('13:30', '14:25'), 'Cornwallis with the guns; rides to the right, then the left', 'The great road, between the lines', D(3, (640, 528)), 3, 'S138; S143', 'S138, pp. 60, 63 n. 22: he went to the right, where his horse was shot, then crossed to the 23rd, where Sergeant Lamb led his horse clear.', 'inferred', 'low', 'S138 pp. 60, 63', 'S144', 'He moved about the field; the symbol stays on the road.')
P('GP115', 'G-BR-TARL', ('13:35', '14:28'), 'Cavalry follow the guns along the road', 'The great road, behind the second line fight', L(4, (640, 535), (690, 515)), 4, SRC + '; S139', 'S139 (as GP211).', 'stated', 'low', 'S138 p. 58, plan 4', 'S144; S139')
WRF = 'S138, p. 65: the right flank corps "gave ground but grudgingly to fall back and fight for a time on the second line. Then in turn they dropped back evenly to the support of the third American line". S143 Seymour: "our riflemen and musketry behaved with great bravery".'
P('GP19', 'G-US-LYNCH', ('13:35', '14:15'), 'Falls back to the right of the second line', 'North of Lawson\'s line', L(3, (645, 125), (662, 163)), 3, SRC + '; S143', WRF, 'stated', 'low', 'S138 pp. 56, 65-66, plan 3; S144 p. 95', 'S144')
P('GP50', 'G-US-KIRK', ('13:35', '14:15'), 'Falls back to the right of the second line', 'North of Lawson\'s line', L(3, (636, 110), (646, 126)), 3, SRC + '; S143', WRF, 'stated', 'low', 'S138 pp. 56, 65-66, plan 3', 'S144')
P('GP51', 'G-US-WASH', ('13:35', '14:15'), 'Covers the flank corps as it falls back', 'Behind the right of the second line', L(3, (690, 150), (700, 165)), 3, SRC, WRF, 'stated', 'low', 'S138 pp. 56, 65-66, plan 3', 'S144')
WV = 'S138, plan 4: "Virginia militia leaving the field". S138, p. 69: Stevens\'s troops "moved around toward the courthouse, keeping to the woods bordering the open ground". S144, p. 95: Lawson\'s platoons "fought a delaying action to the northeast".'
P('GP52', 'G-US-LAWS', ('14:18', '14:22'), 'Broken: falling back north-east through the woods', 'Between the second and third lines, north of the road', D(4, (985, 150)), 4, SRC, WV, 'inferred', 'low', 'S138 pp. 68-69, plan 4; S144 p. 95', 'S144', 'Drawn leaving, then taken off the map.')
P('GP53', 'G-US-STEV', ('14:40', '14:44'), 'Falling back by the woods towards the courthouse; Stevens wounded', 'South of the road, east of the second line', D(4, (1150, 520)), 4, SRC, WV, 'inferred', 'low', 'S138 pp. 69-70, plan 4; S144 pp. 95, 98', 'S144', 'Drawn leaving, then taken off the map.')
WS = ('S143 Stedman, in S138, pp. 63-65: the 1st Guards, "completely broken" on a woody height, rallied behind the Regiment von Bose, and the two "were obliged to traverse the same ground in various directions". S142: the right wing "had a kind of separate action ... above a mile distant from the center". '
      'S144, pp. 100-102: the separate action in the south, 1430 to 1600.')
P('GP25', 'G-US-LEEC', ('13:35', '14:10'), 'Falls back with the flank corps', 'South-east of the first line', L(3, (925, 850), (918, 883)), 3, SRC + '; S141', WS, 'stated', 'low', 'S138 pp. 62-65, 85, 87, plan 3; S144 p. 101', 'S144')
P('GP34', 'G-US-LEEI', ('13:35', '14:10'), 'Falls back fighting', 'South-east of the first line', L(3, (848, 875), (843, 902)), 3, SRC + '; S141', WS, 'stated', 'low', 'S138 pp. 62-65, 85, 87, plan 3; S144 p. 101', 'S144')
P('GP44', 'G-US-CAMP', ('13:35', '14:10'), 'Riflemen fall back from tree to tree; militia of both lines join them', 'South-east of the first line', L(3, (868, 797), (857, 857)), 3, SRC + '; S143', WS + ' S143 Houston: "the Augusta men, and some of Col. Campbell\'s fell in at right angles on us".', 'stated', 'low', 'S138 pp. 62-65, 85, 87, plan 3; S144 pp. 93, 101', 'S144')
P('GP35', 'G-US-LEEI', ('14:30', '15:25'), 'The separate fight in the south', 'In the woods about a mile south of the road', L(4, (1105, 990), (1118, 982)), 4, SRC + '; S141', WS, 'stated', 'low', 'S138 pp. 63-65, 85, 87, plan 4; S144 pp. 101-102', 'S144', 'The foot of Hatch\'s plan 4; the fight ranged over this ground.', early=45, late=45)
P('GP45', 'G-US-CAMP', ('14:30', '15:52'), 'The separate fight in the south', 'In the woods about a mile south of the road', L(4, (1080, 968), (1100, 958)), 4, SRC + '; S142', WS, 'stated', 'low', 'S138 pp. 63-65, 85-89, plan 4; S144 pp. 101-102', 'S144', None, early=45, late=45)
P('GP173', 'G-BR-BOSE', ('14:15', '15:55'), 'The separate fight in the south', 'In the woods about a mile south of the road', L(4, (1040, 985), (1075, 975)), 4, SRC + '; S139', WS, 'stated', 'low', 'S138 pp. 63-65, 85, 87, plan 4; S144 pp. 101-102', 'S144', None, early=45, late=45)
P('GP182', 'G-BR-1GDS', ('14:15', '15:55'), 'The separate fight in the south; broken and rallied', 'In the woods about a mile south of the road', L(4, (1120, 945), (1155, 928)), 4, SRC + '; S143', WS, 'stated', 'low', 'S138 pp. 63-65, 85, 87, plan 4; S144 pp. 101-102', 'S144', None, early=45, late=45)

# ---- 14:40 to 15:30: the third line (plans No. 4 and 5)
WW = ('S143 Stedman, in S138, p. 66: Webster "gained the right of the continentals", but "the weight of their fire, obliged him ... to re-cross a ravine, and occupy an advantageous position on the opposite bank". S141: "His left was speedily routed by the Delawares and Virginians, his right, opposed by the first Maryland". '
      'S144, pp. 103-104: the 33rd, Guards light infantry and jägers reached the west edge of the swale about 1445 and were thrown back by the 1st Maryland and Hawes\'s Virginians.')
P('GP143', 'G-BR-33', ('14:40', '14:52'), 'Comes out on the old fields and attacks the right of the third line; thrown back across the vale', 'North of the road, west of the vale', L(4, (905, 165), (955, 230)), 4, SRC + '; S143', WW, 'stated', 'low', 'S138 pp. 66-67, plan 4; S144 pp. 103-104, 107', 'S144; S143')
P('GP144', 'G-BR-33', ('14:58', '15:22'), 'Reforms on the height west of the vale', 'North of the road, west of the vale', L(5, (948, 188), (990, 240)), 5, SRC + '; S139', WW, 'stated', 'low', 'S138 pp. 66-67, 83, plan 5; S144 p. 107', 'S144; S139')
P('GP145', 'G-BR-33', ('15:28', '15:45'), 'Crosses the vale again and drives Hawes\'s regiment', 'On the ground of the third line', L(5, (1085, 195), (1125, 240)), 5, SRC + '; S139', 'S139: "the Thirty-third Regiment and light infantry of the Guards ... completely routed the corps which was opposed to them". S140: "General Huger was the last that was engaged, and gave the enemy a check".', 'inferred', 'low', 'S138 pp. 74-75, 83, 91, plan 5; S144 pp. 114-115', 'S144; S139', 'Put on the ground Hawes left; Hatch\'s plan gives only arrows.')
P('GP129', 'G-BR-JAG', ('14:40', '15:25'), 'With the 33rd on the left', 'West of the vale, north of the 33rd', L(5, (930, 160), (938, 172)), 5, SRC, WW, 'stated', 'low', 'S138 pp. 66, plan 5; S144 p. 104', 'S144')
P('GP124', 'G-BR-GLI', ('14:40', '15:25'), 'With the 33rd on the left', 'West of the vale, north of the 33rd', L(5, (940, 175), (950, 190)), 5, SRC, WW, 'stated', 'low', 'S138 pp. 66, plan 5; S144 p. 104', 'S144')
P('GP153', 'G-BR-23', ('14:38', '15:20'), 'Comes out of the woods north of the road', 'West of the vale, north of the road', L(5, (917, 232), (932, 292)), 5, SRC + '; S139', 'S139: "The Twenty-third Regiment arriving at that instant from our left". S138, p. 83: the 71st "south of the Great Road" and the 23rd "north of it" reached the open ground as the Guards fell back.', 'stated', 'low', 'S138 pp. 69, 74, 83, plan 5; S144 p. 107', 'S144; S139')
P('GP154', 'G-BR-23', ('15:28', '15:45'), 'Advances on the centre of the third line; the two guns there taken', 'The centre of the third line', L(5, (1140, 222), (1165, 250)), 5, 'S138; S139', 'S138, p. 84: "the 23rd Regiment came on to the two pieces of Finley which had marked the center of the last line" ("presumably").', 'inferred', 'low', 'S138 pp. 84, 91, plan 5', 'S144', 'Hatch\'s own "presumably".')
P('GP202', 'G-BR-GREN', ('14:45', '15:45'), 'Comes up on the right of the 2nd Guards; the Guards rally on it', 'West of the vale, by the road', L(5, (965, 285), (972, 300)), 5, SRC + '; S139', 'S139: "the appearance of the grenadiers of the Guards, and of the Seventy-first Regiment ... now coming out of the wood on the right of the Guards".', 'stated', 'low', 'S138 pp. 73-74, 83, plan 5', 'S144; S139')
P('GP192', 'G-BR-2GDS', ('14:35', '14:58'), 'First to reach the clear ground before the Continentals', 'The edge of the woods, north of the road', L(4, (975, 262), (993, 305)), 4, SRC + '; S139', 'S139: "The 2d battalion of guards first gained the clear ground near Guilford court-house, and found a corps of continental infantry ... formed in the open field on the left of the road".', 'stated', 'low', 'S138 pp. 58-59, 71, plan 4; S144 p. 107', 'S144; S139')
P('GP193', 'G-BR-2GDS', ('15:02', '15:08'), 'Breaks the 2nd Maryland and takes two guns; pursues into the wood', 'The left of the third line, above the road', L(5, (1228, 278), (1282, 295)), 5, SRC + '; S139; S140',
  'S139: "they instantly attacked and defeated them, taking two six-pounders; but, pursuing into the wood with too much ardour, were thrown into confusion by a heavy fire". S140: "having broken the Second Maryland Regiment and turned our left flank". S144, p. 107: 1500 to 1515.', 'inferred', 'low', 'S138 pp. 73-76, plan 5; S144 pp. 107, 110, Map 21 p. 109', 'S144; S139', 'Put on the ground the 2nd Maryland held.')
P('GP194', 'G-BR-2GDS', ('15:18', '15:45'), 'Driven back into the field; rallied by O\'Hara on the grenadiers', 'West of the vale, by the road', L(5, (1010, 273), (1025, 318)), 5, SRC + '; S139', 'S139: "immediately charged and driven back into the field by Colonel Washington\'s dragoons, with the loss of the six pounders ... the second battalion of the Guards was soon rallied and, supported by the grenadiers, returned to the charge".', 'stated', 'low', 'S138 pp. 73-74, 77, 83, plan 5; S144 p. 107', 'S144; S139')
P('GP163', 'G-BR-71', ('14:45', '15:25'), 'Comes out of the wood south of the road, opposite the courthouse', 'South of the road, west of the ravine', L(5, (1000, 370), (1030, 448)), 5, SRC + '; S139', 'S139: the 71st, "having been impeded by some deep ravines, were now coming out of the wood on the right of the Guards, opposite to the Court House".', 'stated', 'low', 'S138 pp. 73-74, 83, plan 5; S144 p. 107', 'S144; S139')
P('GP164', 'G-BR-71', ('15:35', '15:50'), 'Pushes forward to the height at the courthouse', 'South-west of the courthouse', L(5, (1300, 335), (1318, 385)), 5, 'S138; S143', 'S143 Stedman, in S138, p. 91: "The seventy-first pushed forward to an eminence at the Court-house, on the left flank of the continentals."', 'inferred', 'low', 'S138 p. 91, plan 5', 'S144', 'The height is not marked on any plan; put west of Hunting Creek below the courthouse.')
P('GP212', 'G-BR-RA', ('15:08', '15:45'), 'Two 3-pounders on the rise where the road leaves the woods: grapeshot into the melee', 'The great road, west of the vale', D(5, (1037, 324)), 5, SRC + '; S139; S141',
  'S139: "The enemy\'s cavalry was soon repulsed by a well-directed fire from two three pounders just brought up by Lieutenant MacLeod". S141: Cornwallis "ordered his artillery to fire, sacrificing the fugitives to check the pursuit". S144, p. 107: the story that he fired on his own men by design is doubted.', 'stated', 'low', 'S138 pp. 73, 81-82, plan 5; S144 p. 107', 'S144; S139', 'GH08.')
P('GP222', 'G-BR-HQ', ('15:05', '15:45'), 'Cornwallis with the guns on the rise', 'The great road, west of the vale', D(5, (1028, 332)), 5, 'S138; S144', 'S138, pp. 81-82: he "came down from his post, where the Salisbury road enters the wood, to the hollow" and returned to the guns. S144, p. 107: "Cornwallis arrived on the west edge of the swale".', 'stated', 'low', 'S138 pp. 81-82; S144 p. 107', 'S139')
P('GP116', 'G-BR-TARL', ('15:05', '15:28'), 'Cavalry up with the guns; part advances with the Guards', 'The great road, west of the vale', L(5, (980, 343), (1025, 325)), 5, SRC + '; S139', 'S139: "Lieutenant Colonel Tarleton having advanced with part of the cavalry, the enemy were soon put to flight".', 'stated', 'low', 'S138 pp. 74, 85, plan 5; S144 p. 107', 'S144; S139')
P('GP117', 'G-BR-TARL', ('15:50', '16:00'), 'Sent to the right: charges Campbell\'s riflemen, the last fight of the day', 'In the woods about a mile south of the road', mid(D(4, (1080, 968)), D(4, (1120, 945)), 0.5), 4, 'S142; S143; S144',
  'S142: Tarleton "doubled round the right flank of the guards, and charged the Americans with considerable effect. The enemy gave way on all sides". S143 Houston: "their light horse came on us, and not being defended by our own light horse ... we were obliged to run". S144, p. 102.', 'inferred', 'low', 'S138 pp. 85-89; S144 p. 102', 'S144; S143', 'One squadron went; the other followed the Continentals (S138, p. 85).', early=45, late=45)

WK = 'S138, plan 5 and pp. 65, 73: Kirkwood\'s company and Lynch\'s riflemen "had come into the line" on the right of the Continentals; Washington "had taken a position just south of the road on an elevation with a view over the open ground".'
P('GP54', 'G-US-LYNCH', ('14:35', '15:25'), 'On the right of the third line', 'North of Green\'s regiment', L(5, (1040, 90), (1058, 118)), 5, SRC, WK, 'stated', 'low', 'S138 pp. 65, 73, plan 5; S144 p. 104', 'S144')
P('GP55', 'G-US-KIRK', ('14:35', '15:25'), 'On the extreme right of the third line; helps repulse Webster', 'North of Lynch', L(5, (1022, 72), (1033, 85)), 5, SRC + '; S141', WK + ' S141: Webster\'s left "was speedily routed by the Delawares and Virginians".', 'stated', 'low', 'S138 pp. 66, 73, plan 5; S144 p. 104', 'S144')
P('GP56', 'G-US-WASH', ('14:35', '15:03'), 'Cavalry on a rise south of the road, watching the open ground', 'South of the road, west of Hunting Creek', L(5, (1297, 388), (1315, 365)), 5, SRC, WK, 'stated', 'low', 'S138 p. 73, plan 5', 'S144')
P('GP57', 'G-US-WASH', ('15:06', '15:12'), 'Charges through the 2nd Guards from the rear', 'The left of the third line, above the road', D(5, (1248, 296)), 5, SRC + '; S139; S140',
  'S140: "Washington made a charge with the horse upon a part of the brigade of Guards. And the First Regiment of Marylanders ... followed the horse with the bayonets". S139: "immediately charged and driven back into the field by Colonel Washington\'s dragoons". S144, p. 110.', 'inferred', 'low', 'S138 pp. 73, 75, 77-78, plan 5; S144 pp. 107, 110, Map 22 p. 111', 'S144; S139')
P('GP58', 'G-US-WASH', ('15:17', '15:32'), 'Drawn back by the grapeshot; covers the retreat', 'By the Reedy Fork road', G.hp(1, 1672, 440), 1, SRC, 'S138, p. 82: "Howard and Washington drew back". S144, p. 107: they "withdrew about 300 meters to the vicinity of Reedy Fork Road". S138, p. 92: "Washington\'s cavalry was at hand" to check the pursuit.', 'stated', 'low', 'S138 pp. 82, 92; S144 p. 107', 'S144')
P('GP59', 'G-US-1MD', ('14:49', '15:01'), 'Fires on Webster\'s right and follows it to the vale', 'In front of the third line, towards the vale', L(5, (1088, 243), (1098, 270)), 5, SRC + '; S141', WW + ' S138, p. 67 (Howard): "He did not press us hard; nor did we defeat or charge upon him. We left him and charged the second battalion of guards".', 'stated', 'low', 'S138 pp. 66-67, plan 5; S144 pp. 104, 107', 'S144')
P('GP60', 'G-US-1MD', ('15:06', '15:15'), 'Faces about, fires into the Guards\' flank and charges with the bayonet', 'The left of the third line, above the road', L(5, (1225, 255), (1262, 272)), 5, SRC + '; S140; S141',
  'S140 (as GP57). S138, p. 77: "His regiment turned toward the new threat and, when at rather close range, fired into them from the flank ... Howard led a vicious charge". S144, p. 110: "Firing by division ... the veteran 1st Maryland flayed the vulnerable flank".', 'inferred', 'low', 'S138 pp. 75, 77-80, plan 5; S144 pp. 107, 110', 'S144; S140', 'Put just north of where the 2nd Maryland had stood.')
P('GP61', 'G-US-1MD', ('15:19', '15:32'), 'Draws back towards the Reedy Fork road', 'East of the third line', G.hp(1, 1640, 430), 1, SRC, 'S138, p. 82 and S144, p. 107 (as GP58).', 'stated', 'low', 'S138 p. 82; S144 p. 107', 'S144')
P('GP62', 'G-US-2MD', ('15:06', '15:10'), 'Broken: running for the courthouse', 'Behind the left of the third line', D(5, (1340, 240)), 5, SRC + '; S140', 'S138, p. 76: "the Marylanders fired but feebly and took to their heels". S144, p. 110: "the green Maryland troops broke and ran toward the courthouse". S138, plan 5: "2nd Maryland Regiment leaving the field".', 'inferred', 'low', 'S138 pp. 75-76, plan 5; S144 p. 110', 'S144; S140', 'Drawn leaving, then taken off the map.')
P('GP63', 'G-US-GREEN', ('15:14', '15:50'), 'Drawn off unengaged to cover the retreat', 'On the Reedy Fork road, north of the courthouse', G.hp(1, 1655, 385), 1, SRC + '; S141', 'S141, in S138, p. 92: Green\'s regiment "was drawn off without having tasted of battle, and ordered to a given point in the rear for the security of this movement". S144, p. 115. The point is not named.', 'inferred', 'low', 'S138 pp. 83, 92; S144 p. 115', 'S144')
P('GP64', 'G-US-HQ', ('15:15', '15:40'), 'Greene orders the retreat', 'By the Reedy Fork road', G.hp(1, 1665, 420), 1, 'S140; S138', 'S140: "appearing to be gaining our right — which would have encircled the whole of the Continental troops — I thought it most advisable to order a retreat."', 'inferred', 'low', 'S138 pp. 74-75, 81, 84; S144 p. 114', 'S144', 'He wrote that he was "very near being taken" about this time, having ridden into the enemy (S138, p. 81).')

# ---- the retreat by the Reedy Fork road, and Lee's ride round to the courthouse
WT = 'S140: "We retreated in good order to the Reedy-fork river, and crossed at the ford about three miles from the field of action". S144, pp. 115-116: the main body "broke contact with the British around 1530".'
P('GP72', 'G-US-HAWES', ('15:30', '15:36'), 'Falls back to the Reedy Fork road, the last regiment engaged', 'By the Reedy Fork road', G.hp(1, 1668, 455), 1, 'S140; S138', 'S140: "General Huger was the last that was engaged, and gave the enemy a check." Where it joined the column is not said.', 'inferred', 'low', 'S138 pp. 75, 83, 91', 'S144',
  'Shown with the army\'s column from here.')
P('GP77', 'G-US-ARMY', ('15:36', '15:42'), 'The Continentals form column on the Reedy Fork road', 'The Reedy Fork road, north of the great road', G.hp(1, 1660, 400), 1, 'S140; S138; S144', WT, 'inferred', 'low', 'S138 pp. 84, 91-93, plan 5; S144 pp. 115-116', 'S144; S140',
  'One symbol for the retreating army (as for the column on the march): Hatch draws the retreat as arrows up this road, not where each regiment marched.')
P('GP78', 'G-US-ARMY', ('15:55', '16:10'), 'Retreating to the Reedy Fork', 'The Reedy Fork road at the north edge of Hatch\'s plan', NORTH, 1, 'S140; S138; S144', WT, 'stated', 'low', 'S138 pp. 84, 91-93, plan 5; S144 pp. 115-116', 'S144; S140',
  'The ford is three miles on and the iron works on Troublesome Creek about fifteen: both off the map.', early=30, late=45)
P('GP26', 'G-US-LEEC', ('15:40', '15:58'), 'Reaches the courthouse after the army has gone', 'Near Guilford Courthouse', G.hp(1, 1790, 472), 1, 'S141; S138', 'S141, in S138, p. 85: Lee "joined his cavalry near the court-house" after "passing to the right of the British, after Greene had retreated". S138, plan 5 draws the ride as a long curve round the east.', 'stated', 'low', 'S138 pp. 85, 93, plan 5; S144 p. 102', 'S144', None, early=45, late=45)
P('GP36', 'G-US-LEEI', ('15:45', '16:00'), 'Follows Lee round to the courthouse', 'Near Guilford Courthouse', G.hp(1, 1770, 490), 1, 'S141; S138', 'S141 (as GP26): "Lee, with his infantry and one company of riflemen, pressed forward to join the continentals".', 'inferred', 'low', 'S138 p. 85, plan 5', 'S144', None, early=45, late=45)

# ---------------------------------------------------------------- routes
def wp(pts): return '; '.join('%.5f, %.5f' % p for p in pts)
def pos(pid): return next(p for p in POS if p['pos_id'] == pid)
def at(pid): p = pos(pid); return (p['lat'], p['lon'])
ROUTES = []
def RT(rid, unit, kind, a, b, pts, src, wording, notes, conf='low'):
    ROUTES.append(dict(route_id=rid, unit_id=unit, kind=kind, start=pos(a)['show_to'], end=pos(b)['show_from'], from_pos_id=a, to_pos_id=b, wps=[at(a)] + pts + [at(b)], source_ids=src, source_wording=wording, confidence=conf, notes=notes, playback='yes'))
NR = 'New Garden Road of the 1951 USGS sheets (S146), then Hatch\'s road from Little Horsepen Creek (S138): a road of 1951 on the line of the great road.'
RT('RGC01', 'G-BR-ARMY', 'march', 'GP100', 'GP101', road(SWEDGE, JUNCT)[1:-1], 'S142; S146', 'S142: "seven miles on the great Salisbury road".', 'The main road of the 1951 sheet west of Guilford College; which road of 1781 it stands for is not established.')
RT('RGC02', 'G-BR-ARMY', 'march', 'GP101', 'GP102', road(JUNCT, CREEK)[1:-1], 'S138; S139; S146', 'S138, p. 29: Cornwallis "continued along the Salisbury-Hillsboro great road".', NR)
RT('RGC03', 'G-BR-TARL', 'march', 'GP110', 'GP111', road(JUNCT, LANE)[1:-1], 'S141; S144; S146', 'S141, in S144, p. 74: Heard "followed leisurely by the enemy\'s horse".', NR)
RT('RGC04', 'G-BR-TARL', 'withdrawal', 'GP111', 'GP112', road(LANE, JUNCT)[1:-1], 'S141; S144', 'S144, p. 74: "withdrew along a dirt trail to the east of the Salisbury Road".', 'Drawn on the road; the "obscure way" he took is not known.')
for rid, unit, a, b in (('RGC05', 'G-BR-TARL', 'GP113', 'GP114'), ('RGC06', 'G-BR-GLI', 'GP121', 'GP122'), ('RGC07', 'G-BR-JAG', 'GP126', 'GP127'), ('RGC08', 'G-BR-23', 'GP130', 'GP150')):
    RT(rid, unit, 'march', a, b, road(XROAD, CREEK)[1:], 'S138; S146', 'S142: the order of march, the cavalry, Guards light infantry and jägers in the advance guard.', NR)
RT('RGC09', 'G-US-LEEC', 'march', 'GP20', 'GP21', road(BIVOUAC, LANE)[1:-1], 'S141; S146', 'S141: "took the road to the enemy at the head of the horse" (in S138, p. 24); he "had not proceeded above two miles" when he met Heard (in S144, p. 74).', NR)
RT('RGC10', 'G-US-LEEC', 'march', 'GP21', 'GP22', road(LANE, JUNCT)[1:-1], 'S141', 'S141: Lee "followed the common route by the Quaker meeting-house".', NR)
for rid, unit, a, b in (('RGC11', 'G-US-LEEC', 'GP23', 'GP24'), ('RGC12', 'G-US-LEEI', 'GP32', 'GP33'), ('RGC13', 'G-US-CAMP', 'GP42', 'GP43')):
    RT(rid, unit, 'withdrawal', a, b, road(XROAD, D(2, (553, 538)))[1:], 'S141; S144; S146', 'S144, p. 74: Lee "withdrew, unpursued, to Guilford Courthouse". S140: he "was obliged to retire, and take his position in the line".', NR + ' Then across to the left flank.')
RT('RGC14', 'G-US-SING', 'withdrawal', 'GP04', 'GP18', road(D(2, (553, 538)), D(5, (1290, 298)))[1:-1], 'S138; S139', 'S138, p. 48: "down which Singleton had withdrawn with his two 6-pounders as prearranged".', 'Hatch\'s road.')
RT('RGC15', 'G-US-LEEC', 'march', 'GP25', 'GP26', [D(5, (1180, 960)), D(5, (1330, 880)), D(5, (1460, 700)), D(5, (1500, 480)), D(5, (1490, 330))], 'S138; S141', 'S141: "passing to the right of the British".', 'The curve Hatch draws on his plan No. 5, read at five points.')
RT('RGC16', 'G-US-LEEI', 'march', 'GP35', 'GP36', [D(5, (1190, 950)), D(5, (1335, 870)), D(5, (1455, 700)), D(5, (1490, 490))], 'S138; S141', 'S141 (as RGC15).', 'As RGC15.')
RT('RGC17', 'G-US-ARMY', 'retreat', 'GP77', 'GP78', REEDY[near(at('GP77'), REEDY) + 1:-1], 'S138; S140', 'S140: "We retreated in good order to the Reedy-fork river".', 'The Reedy Fork road as Hatch draws it.')

# ---------------------------------------------------------------- events
# id, earliest, latest, name, summary, rows, sources, timeline, playback_at, label
EVENTS = [
    ('GCE01', '05:30', '08:20', 'Cornwallis marches on Guilford', 'Cornwallis leaves his camp near Deep River Friends Meeting House at daybreak, sending his baggage away under guard. Tarleton leads with the Legion cavalry, the Guards light infantry and the jägers. Greene\'s army is at Guilford Courthouse, twelve miles off; Lee\'s Legion and Campbell\'s riflemen are out on the road.',
     'GP100; GP20; GP01', 'S138; S139; S142; S143', 'name', '08:02', 'Cornwallis marches'),
    ('GCE02', '06:30', '09:00', 'Lee charges in the lane', 'Lee\'s cavalry, falling back before Tarleton\'s, turns in a fenced lane and rides down his leading section. Tarleton sounds the retreat and leaves the road. The hour is disputed.',
     'GP21; GP111', 'S138; S141; S142; S144', 'name', '08:40', 'The lane'),
    ('GCE03', '06:45', '09:15', 'The Guards fire at New Garden Meeting House', 'Lee, following by the meeting house to cut Tarleton off, rides into the Guards light infantry, who fire a volley; his horse throws him. The Legion infantry and Campbell\'s riflemen come up and the fight becomes general.',
     'GP22; GP120; GP125; GP31; GP41; GP112', 'S138; S141; S142; S144', 'name', '09:00', 'New Garden'),
    ('GCE04', '07:15', '10:30', 'The 23rd comes up; Lee draws off', 'The head of the British column, the 23rd Foot, arrives. Lee falls back to the cross road, covers his infantry with the cavalry and retires up the great road to the army, unpursued. Each side has lost perhaps 40 men.',
     'GP23; GP32; GP42; GP130; GP113; GP101', 'S138; S141; S142; S144', 'name', '09:35', 'Lee draws off'),
    ('GCE05', '06:00', '11:30', 'Greene forms three lines', 'Greene posts the North Carolina militia behind a rail fence at the edge of the woods, the Virginia militia in the woods 300 yards behind, and the Continentals on the high ground west of the courthouse, with riflemen and cavalry on each flank of the first line and two guns in the road.',
     'GP02; GP03; GP04; GP05; GP06; GP07; GP08; GP09; GP10; GP11; GP12; GP13; GP14; GP15', 'S138; S140; S143; S144', 'name', '10:45', 'Three lines'),
    ('GCE06', '12:00', '13:30', 'Cannonade; the British deploy', 'As the British column crosses Little Horsepen Creek, Singleton\'s 6-pounders open on it from the road. Macleod\'s guns answer for about half an hour while Cornwallis forms line: Webster\'s brigade left of the road, Leslie\'s right, the Guards in support, the cavalry in the road.',
     'GP102; GP210; GP04; GP140; GP150; GP160; GP170; GP180; GP190; GP114', 'S138; S139; S141; S143; S144', 'name', '12:35', 'Cannonade'),
    ('GCE07', '12:30', '13:45', 'The first line breaks', 'The British cross the muddy fields. The North Carolinians fire at 140 yards, some a second time; the British fire once at close range and charge. Most of the militia run. On both flanks the riflemen and light troops hold and fire into the ends of the British line.',
     'GP141; GP151; GP161; GP171; GP16; GP17', 'S138; S139; S140; S143; S144', 'name', '13:13', 'First line breaks'),
    ('GCE08', '13:00', '14:15', 'The flanks pull the British line apart', 'Webster turns the 33rd, the jägers and the Guards light infantry against Lynch, Kirkwood and Washington; Leslie turns von Bose and the 1st Guards against Campbell and Lee. The 2nd Guards and the grenadiers come into the line by the road. Every British foot soldier is now engaged.',
     'GP142; GP128; GP123; GP172; GP181; GP19; GP50; GP51; GP44; GP34', 'S138; S139; S144', 'name', '13:32', 'Flanks'),
    ('GCE09', '13:15', '14:45', 'The second line: the Virginians hold, then break', 'In thick woods the Virginia militia fight for the better part of an hour. Lawson\'s brigade north of the road gives way first; Stevens\'s holds against the 71st until he is shot through the thigh and orders it off.',
     'GP08; GP09; GP152; GP201; GP191; GP162; GP52; GP53', 'S138; S140; S143; S144', 'name', '13:50', 'Second line'),
    ('GCE10', '13:30', '16:00', 'The separate fight in the south', 'Von Bose and the 1st Guards follow Campbell\'s riflemen and Lee\'s infantry south-east through the woods, a mile from the road. The Guards battalion is broken on a wooded height and rallies behind the Hessians. Neither commander knows how this fight is going.',
     'GP173; GP182; GP45; GP35', 'S138; S142; S143; S144', 'name', '14:20', 'Fight in the south'),
    ('GCE11', '14:15', '15:15', 'Webster attacks the third line and is thrown back', 'Webster, first out of the woods, crosses the vale with the 33rd and the light troops against the Continental right. The 1st Maryland, Hawes\'s Virginians and Kirkwood meet him with a close volley and drive him back across the vale. He is mortally wounded.',
     'GP143; GP129; GP124; GP59; GP11; GP55; GP54', 'S138; S141; S143; S144', 'name', '14:46', 'Webster repulsed'),
    ('GCE12', '14:30', '15:30', 'The 2nd Guards break the 2nd Maryland', 'The 2nd Battalion of Guards charges the left of the Continental line. The 2nd Maryland, new levies, gives way almost without firing, and the Guards take Singleton\'s two guns and press on behind the line. Greene, seeing his left turned, orders the retreat.',
     'GP193; GP62; GP18; GP64', 'S138; S139; S140; S144', 'name', '15:02', '2nd Maryland breaks'),
    ('GCE13', '14:40', '15:40', 'Washington and the 1st Maryland strike the Guards', 'Washington\'s dragoons ride through the Guards from behind while the 1st Maryland, facing about, fires into their flank and closes with the bayonet. Lt. Col. Stuart is killed, the guns are retaken, and the Guards are driven back into the open field.',
     'GP57; GP60; GP194', 'S138; S139; S140; S141; S144', 'name', '15:07', 'Counterattack'),
    ('GCE14', '14:45', '15:45', 'Cornwallis\'s guns stop the pursuit', 'From the rise where the road leaves the woods Cornwallis has two 3-pounders fire grapeshot into the melee. It checks the Americans. The 23rd and 71st come out of the woods, and O\'Hara, though wounded, rallies the Guards on the grenadiers.',
     'GP212; GP222; GP153; GP163; GP202; GP58; GP61', 'S138; S139; S141; S144', 'name', '15:14', 'Grapeshot'),
    ('GCE15', '15:00', '16:00', 'Greene retreats by the Reedy Fork road', 'The Continentals go off in good order, Green\'s regiment and Washington covering. Hawes\'s regiment, the last engaged, checks the 33rd. The four guns are left, their horses killed. The British follow a short way and stop: Greene halts three miles off at the Reedy Fork, then marches to the iron works on Troublesome Creek.',
     'GP145; GP154; GP164; GP63; GP72; GP77; GP78', 'S138; S139; S140; S144', 'name', '15:32', 'Retreat'),
    ('GCE16', '15:15', '16:15', 'Tarleton\'s last charge', 'Hearing fire still on the right, Cornwallis sends Tarleton there with a squadron. Lee has already drawn his Legion off towards the courthouse. Tarleton charges the riflemen who remain and scatters them: the last fight of the day.',
     'GP117; GP45; GP173; GP182; GP26; GP36', 'S138; S141; S142; S143; S144', 'name', '15:52', 'Last charge'),
]

# ---------------------------------------------------------------- hypotheses
def Hy(hid, qn, a, b, c, ev_for, ev_against, adopted, because, conf, rows, srcs, nxt):
    return dict(hypothesis_id=hid, battle_id=BATTLE, question=qn, reading_a=a, reading_b=b, reading_c=c, evidence_for=ev_for, evidence_against=ev_against, adopted_reading=adopted, adopted_because=because, confidence=conf,
                status='Proposed', decided_by='Claude (session default); Morgan to confirm', decided_on=TODAY, rows=rows, source_ids=srcs, next_step=nxt, history='New on 26 Nov 2026 with the Guilford Courthouse rows.')
HYP = [
    Hy('GH01', 'At what hour did the battle (the infantry attack) begin?', 'About 13:00, after half an hour\'s cannonade from about 12:30', 'About 13:30', 'About noon',
       'S144 pp. 84, 87, 153: lead elements "around 1230", the line formed "around 1300", "1300—British advance on first line", "1315—First line breaks".\nS143 Saumarez, in S138 p. 47: "About one o\'clock the action commenced."\nS138 p. 42: the cannonade "began some time just after noon and went on for at least a half hour".',
       'S139: "about half an hour past one in the afternoon" (in S144 p. 119), for "an action which lasted an hour and a half" (in S138 p. 47).\nS140, in S138 p. 47: the "battle began about twelve o\'clock, lasted about two hours" (he may count from the cannonade).\nS141, in S138 p. 43: "About ten in the forenoon" (Hatch: much too early).\nS144 p. ix (list of maps): Map 16, "The first line deployment, 1300–1330"; Map 17, "The first line breaks, 1330".',
       'A', 'The staff ride\'s clock, which Saumarez and Hatch support, and which lies between Greene\'s hour and Cornwallis\'s. Every row keeps half an hour either side.', 'low', 'GP140; GP150; GP160; GP170; GP141; GP151; GP161; GP171; GCE06; GCE07', 'S138; S139; S140; S141; S143; S144',
       'Read Babits and Howard on the timing. The staff ride\'s map titles (1330 for the break) and its text (1315) differ by a quarter of an hour.'),
    Hy('GH02', 'At what hour were the morning fights near New Garden?', 'About 08:15 to 10:00', 'From about sunrise: 06:30 to 07:30', 'About 07:00, 09:00 and 10:00, or 04:00 to 05:00',
       'S143 Seymour, in S138 pp. 23-24: "This action began about nine o\'clock in the morning and continued about the space of an hour and a half."\nS143 Houston, in S138 p. 33: "about ten o\'clock ... we heard our light infantry and cavalry ... begin firing".\nS143 orderly book, in S138 p. 22: the army to march "precisely At half past five"; S142: the picket met after "seven miles", about three hours\' march for foot.\nS144 p. 74: Lee "broke contact" at 1000.',
       'S141, in S138 p. 25: at the meeting house "The sun had just risen above the trees".\nS144 pp. 72-73: the lane "around 0700", the second fight "around 0900", the third "around 1000".\nS144 p. 153: "0300—Cornwallis begins movement", "0400-0500—Dragoon skirmishes at New Garden Meeting House".',
       'A', 'Two journals kept at the time give nine and ten; the order to march at 05:30 makes a fight seven miles on before 07:30 unlikely for the infantry. Lee wrote thirty years later. The rows keep from 06:30.', 'low',
       'GP20; GP21; GP22; GP23; GP111; GP112; GP113; GP120; GP125; GP130; GCE02; GCE03; GCE04', 'S138; S141; S142; S143; S144', 'Read Babits and Howard, and Newsome\'s edition of the orderly book, for the hour of the march.'),
    Hy('GH03', 'When did Greene\'s army form its three lines?', 'From about 10:00, when the firing was heard', 'About 06:00', None,
       'S143 Houston, in S138 p. 33: "about ten o\'clock, lying about our fires, we heard our light infantry and cavalry ... begin firing with the enemy. Then we immediately fell into our ranks, and our brigades marched out."\nS140, in S138 p. 26 n. 15: on Lee\'s report Greene "prepared for battle".',
       'S144 p. 153: "0600—Greene feeds and deploys his men into three battle lines".\nS138 p. 29: Greene "had been awake and active that morning ... since the first confirmation was received".', 'A', 'Houston was in Stevens\'s brigade and wrote a journal. The playback shows the army in camp until 10:15.', 'low', 'GP01; GP02; GP03; GP08; GP09; GCE05', 'S138; S140; S143; S144', 'Look for other journals of the morning.'),
    Hy('GH04', 'Which North Carolina brigade stood north of the road in the first line?', 'Eaton north, Butler south', 'Butler north, Eaton south', None,
       'S138 p. 34: "Eaton\'s brigade ... was north of, with its left resting on, the New Garden Road. Butler\'s brigade ... had a like deployment on the south side", citing Caruthers (1856), p. 141, and his plans 2 and 3.\nS144 Map 16, p. 89: EATON labelled north of the road, BUTLER south.\nS144 p. 93: Butler\'s brigade against Leslie\'s 71st and von Bose, who were south of the road.',
       'S144 p. 87: "Running to the north in order from left to right was Brigadier General John Butler\'s North Carolina militia brigade ... Running to the south in order was Colonel Thomas Eaton\'s".\nS144 p. 90: "Eaton\'s North Carolina brigade broke" with "Lee\'s Corps of Observation on Eaton\'s left flank".',
       'A', 'Hatch gives his authority, and the staff ride\'s own map and one of its stands agree with him against its other text. Babits and Howard, whom the staff ride follows, have not been read (SR-19): this is the first point to settle from them.', 'low', 'GP02; GP03; GP16; GP17', 'S138; S144',
       'Read Babits and Howard (candidate SC-SOU10). If they put Butler north on the pension evidence, swap the two brigades.'),
    Hy('GH05', 'Where did the third line stand?', 'On the high ground between the vale and Hunting (Richland) Creek, west of the courthouse', 'About 400 yards further west, in the field between today\'s Tour Stops 5 and 7 (Schenck)', None,
       'S138 pp. 37-38, 73 and plans 2 to 5: "just west and across Hunting Creek from the courthouse", all north of the road.\nS145 p. 4: "the third line actually stood about 400 yards east of its previously interpreted position, i.e., the monument-marked field located between Tour Stops 5 and 7".\nS144 p. 104: "about 300 meters east of this location, on a ridgeline overlooking Richland Creek", citing Babits and Howard, p. 238; p. xx: the old marker "incorrectly identifies the area as the American third line"; later scholarship puts it "about 400 meters uphill to the east-northeast".',
       'S145 p. 22: Schenck in the 1880s "fixed the location of the third line west of Hunting Creek, maintaining that its left flank occupied the elevation at present-day Tour Stop 7"; accepted for a century.\nS145 p. 22: archeologists surveyed the revised location in 1995 "and did not uncover any military material".',
       'A', 'Three studies from 1971 to 2021 agree. Note the names: Hatch\'s "Hunting Creek" is the stream the USGS calls Richland Creek; the park today gives the name to the branch Hatch calls the vale.', 'medium', 'GP10; GP11; GP12; GP13; GP14; GP143; GP193', 'S138; S144; S145',
       'Read the landscape report\'s maps and the 1995 survey report; fit the park\'s own line.'),
    Hy('GH06', 'How strong was Greene\'s army?', 'About 4,400', 'Over 5,600', None,
       'S138 pp. 127-129: Continentals 1,700, militia 2,200, riflemen and volunteers 500; Gordon and F. V. Greene 4,444, Ward 4,463, Carrington 4,404; Lee\'s field return 4,449.\nS144 p. 151: "~4,400 with 4,000 engaged".\nS85 p. 98: "1,500 continentals and 3,000 militia".',
       'S138 p. 128: Schenck (1889) 5,668, "probably under the true figure"; Hatch thinks it inflated.\nS139, in S138 p. 21 n. 1: Cornwallis heard "nine or ten thousand", and wrote of 5,000 to 7,000.', 'A', 'The returns and every study since agree within a hundred.', 'medium', None, 'S138; S144; S85', 'None.'),
    Hy('GH07', 'How many guns had the British, and of what weight?', 'Four 3-pounders', 'Three guns in the first cannonade; two 3-pounders at the third line', 'Four 6-pounders and two 3-pounders',
       'S138 p. 45: "The artillery detachment embraced four pieces — 3-pounders — and some 50 men".\nS143 Magill, in S138 p. 43: "a heavy Cannonade with four Field Pieces".',
       'S138 p. 45 n. 52: "The Tarleton battle plan shows only three cannon in place for the opening cannonade."\nS139: "two three pounders just brought up by Lieutenant MacLeod".\nS144 p. 150 (order of battle): Royal Artillery, four 6-pounders and two 3-pounders, 50 men; its p. 84 speaks only of 3-pounders.',
       'A', 'Hatch\'s count, from the field return. The playback draws one symbol for the guns.', 'low', 'GP210; GP211; GP212', 'S138; S139; S143; S144', 'Check the field return in Tarleton and Babits and Howard\'s order of battle.'),
    Hy('GH08', 'Did Cornwallis have his guns fire into his own Guards?', 'Yes: grapeshot into the melee, friend and foe', 'The guns fired to check the American pursuit; Guardsmen were hit, but not by design', None,
       'S141, in S138 p. 82: Cornwallis "ordered his artillery to fire, sacrificing the fugitives to check the pursuit".\nS138 p. 82: "though it would be into both friend and foe alike and over the objection of the Guards commander, O\'Hara".',
       'S139: "The enemy\'s cavalry was soon repulsed by a well-directed fire from two three pounders": no word of firing on his own men.\nS144 p. 107: the grapeshot "apparently caused casualties among the guardsmen, giving rise to the assertion that Cornwallis cold-bloodedly ordered indiscriminate firing into the melee" (its note 83: Babits and Howard, pp. 161-62, "thoroughly debunks the theory").',
       'B', 'The newer study rejects the story on Babits and Howard\'s authority (not read here); Lee was in the south and did not see it. The event text says only that the guns fired grapeshot into the melee and checked the Americans.', 'low', 'GP212; GCE14', 'S138; S139; S141; S144', 'Read Babits and Howard, pp. 161-62.'),
    Hy('GH09', 'How far apart were the three lines?', 'About 300 yards, then about 500', '400 metres (437 yards), then 650 to 750 metres', '300 yards, then 400',
       'S138 pp. 36-38: the second line "some 300 yards behind the first", the third "some 500 yards behind the second"; Schenck measured the second and third "at least five hundred and fifty (550) yards apart".',
       'S140: "about three hundred yards ... about four hundred yards".\nS142: 400 and "near six hundred yards".\nS144 pp. 87, 95, 97: "About 437 yards (400 meters)"; the third line 650 m north-east of Lawson and 750 m east-north-east of Stevens.',
       'A', 'The lines are drawn where Hatch\'s plans put them: on the ground about 430 m apart at the road, then about 620 m. That is nearer the staff ride\'s figures than Hatch\'s own text.', 'low', 'GP02; GP03; GP08; GP09; GP13', 'S138; S140; S142; S144', 'Measure the park\'s marked lines.'),
    Hy('GH10', 'Where were the morning fights, and where was Lee posted?', 'At three junctions of New Garden Road: Hobbs Road ("the lane"), West Friendly Avenue (the meeting house) and Ballinger Road (the cross road)', 'All nearer the meeting house, four miles from the courthouse', None,
       'S144 pp. 72-74 and Map 13: the lane 1.8 miles north-east of the meeting house, the second fight at the West Friendly Avenue junction, the third at "the Ballenger and Great Salisbury Cross Roads" 0.6 mile north.\nS139: "About four miles from Guildford our advanced guard ... fell in with a corps of the enemy".',
       'S141, in S138 pp. 23-25: Lee was posted "within two or three miles of the court-house", met Heard "About two miles out" (Hatch\'s words), fell back, charged in the lane, then followed to the meeting house.\nS141 (in S144 p. 74): the meeting house "not more than six miles from our head-quarters".\nS144 p. 73 has Lee\'s corps at New Garden from 14 March.',
       'A', 'The staff ride names places that can be found on the map, and Lee\'s distances fit a lane between his post and the meeting house. Every morning row is rated low, good to 400 m at best.', 'low', 'GP20; GP21; GP22; GP23; GP111; GP120', 'S138; S139; S141; S144',
       'Read Babits and Howard\'s chapter on New Garden; find the old meeting house site (Hatch, p. 25 n. 13: foundation stones about 200 yards from the Guilford College campus).'),
]
GAPS = [
    ('GG01', 'Babits and Howard, Long, Obstinate, and Bloody (2009), has not been read', 'It is the standard study and the staff ride follows it. GH04 (which brigade was north of the road), the regiments inside each brigade and the hours all wait on it. No copy could be had on 26 Nov 2026.', 'Borrow or buy the book; read chapters on 15 March and the maps; re-read every Hypotheses row against it (SR-19).'),
    ('GG02', 'The plans are fitted by the park boundary, not by the ground of 1781', 'Hatch\'s creeks and road lie up to 70 m from today\'s survey, so units are good to about 75 m. His plan may also carry drafting error of its own.', 'Fit the park\'s own map of the 1781 road, fields and lines (the landscape report\'s maps; the park\'s GIS) and compare with Hatch\'s.'),
    ('GG03', 'No map of the time is offered beside the reconstruction', 'The British plan engraved for Tarleton\'s History (1787) is public domain and online (candidate SC-SOU12) but was not opened, read or fitted. Hatch says most later plans rest on it.', 'Fetch the scan (Library of Congress or Leventhal), read it against Hatch\'s plans, and offer it in the map details as a picture not to scale.'),
    ('GG04', 'The staff ride\'s battle maps 17 and 19 to 24 were not read', 'Only maps 13, 16 and 18 were looked at; the rest were cross-checked through the stand texts. A regiment\'s place on a map may differ from the text.', 'Read the remaining maps from Morgan\'s PDF and compare each with its rows.'),
    ('GG05', 'The park\'s current battle map and waysides were not read', 'The 2023 park brochure is in Morgan\'s folder; its text was skimmed and its map not read. It is the park\'s present reading of all three lines.', 'Read and fit the brochure map; note where it differs from Hatch (1971).'),
    ('GG06', 'The ground north of latitude 36.125 has no old survey map here', 'The 1951 USGS sheets Morgan found stop just south of the battlefield, so no map of the ground before the suburbs was compared with Hatch\'s plan.', 'Get the 1951 Lake Brandt (or Summerfield) 1:24,000 sheet from USGS topoView.'),
    ('GG07', 'The road Cornwallis came by south-west of New Garden is not established', 'The column is drawn on the main road of the 1951 sheet west of Guilford College. Lee says only that the road from Deep River met the great road near the meeting house.', 'Read the staff ride\'s Map 13 closely and a period road map of Guilford County.'),
    ('GG08', 'There is no fall-back drawing of today\'s roads and streams', 'OpenStreetMap could not be reached from the workspace, so data/base/guilford-courthouse.json was not made. The current map is the streamed USGS map; if it cannot be reached, only the reconstruction\'s lines and the terrain are drawn.', 'Fetch an Overpass extract for the box and build the base with pipeline/basemaps.py.'),
    ('GG09', 'No position row has been audited against its source by a second reader', 'Every row was written and rated in one session. At Cowpens an audit lowered thirteen ratings.', 'Run the Opus audit of the position rows (Session 7 of the HIST 340 prompt) if Morgan says yes.'),
]

# ---------------------------------------------------------------- playback
OPENING = ('Morning, 15 March 1781. Nathanael Greene\'s army, about 4,400 men, most of them militia, is in camp at Guilford Courthouse on ground he has chosen. Cornwallis, with some 1,900 regulars, has been marching since daybreak to attack him, twelve miles up the great road. '
           'Lee\'s Legion is out in front to meet him. Press play: the units come onto the map as they move.')
EXT = [-79.9050, 36.0720, -79.8250, 36.1420]     # the reconstruction's sheet (pipeline/recon/guilford_1781.py): its south margin carries the sheet's title, clear of New Garden
PLAYBACK = dict(playback_id=PB, battle_file_id='guilford-courthouse-1781', campaign_id=CAMP, record_battles=BATTLE, title='Battle of Guilford Courthouse, 15 March 1781', subtitle='Greene\'s three lines and Cornwallis\'s costly victory',
                time_unit='minute', time_zero='1781-03-15 00:00', time_start=T('08:00'), time_end=T('16:15'), focus_start=T('12:25'), focus_end=T('16:05'), calendar_first=DAY, days_numbered='no', calendar_days=1,
                origin_lat=36.1315, origin_lon=-79.8450, west=EXT[0], south=EXT[1], east=EXT[2], north=EXT[3], opening_label='Morning, 15 March 1781', opening_text=OPENING)
TERRAIN = {"zoom": 14, "extent": [-79.925, 36.070, -79.805, 36.155], "open_m": 20, "smooth_m": 20, "relief": 3, "spots_from": 14.4, "doubt": False,
           "about": "In the United States these tiles come from the USGS's National Elevation Dataset, a survey of the bare ground with no buildings or trees in it. Bumps narrower than about 20 m are taken off and the rest smoothed over about 20 m. Heights are in metres, good to a metre or two. This is today's ground: the park keeps the eastern half of the field, but Greensboro's streets, lakes and a cemetery have reshaped the rest since 1781.",
           "beyond": "Beyond the dotted line the roads of 1781 stop: only today's relief and contours are drawn there, so the map fills the window."}
SETTINGS = [
    ('page_title', 'Battle of Guilford Courthouse (1781) Playback', None, None),
    ('based_on', '["tactical", "us-maps"]', 'The presets this battle is based on (Playback presets sheet in Sources and notes.xlsx), laid on in turn after "all"; this battle\'s own rows win over them', None),
    ('clock_title', 'Guilford Courthouse', None, None), ('rate', 1, 'Minutes a second the page opens at', None),
    ('lead.share', 0.3, 'The morning before 12:25 takes this share of the timeline', None), ('lead.rate', 6, 'Minutes a second for the morning', None), ('lead.step', 5, None, None),
    ('sides.CR.short', 'British', 'This playback\'s own name for the side (the war\'s Sides row says "Hessian and British", for Trenton)', None),
    ('sides.CR.name', 'British Crown forces (British regulars, German troops and Loyalist provincials)', None, None),
    ('follow.min', '[900, 650]', 'Smallest box the camera frames, metres', None), ('follow.margin', 90, None, None), ('follow.empty', 'approach', None, None), ('follow.lookahead', 15, 'Minutes ahead the camera looks', None),
    ('follow.hold_until', '1781-03-15T08:10', 'The camera stays on the whole ground until both sides are on the map, then eases in', None),
    ('preset.field', '[-79.8620, 36.1210, -79.8285, 36.1400]', 'A named view: [west, south, east, north]', None), ('preset.approach', json.dumps(EXT), None, None),
    ('views.1.preset', 'approach', 'Named views; the first is the one the page opens on', None), ('views.1.label', 'New Garden to the courthouse', None, None), ('views.1.short', 'Approach', None, None),
    ('views.2.preset', 'field', None, None), ('views.2.label', 'The battlefield', None, None), ('views.2.short', 'Field', None, None),
    ('modern.reach', 3, None, None),
    ('zoom.labels', 0.2, None, None), ('zoom.landmarks_from', 0.15, None, None),
    ('arrows.lead', 5, 'Minutes before the unit sets off that the arrow appears', 'A field battle followed by the minute: the player\'s 45 minutes would show arrows long before a move (as Cowpens\'s 3; rule F-8 is still open).'),
    ('rear.side', 'US', 'Symbols sit behind their own lines: the American rear is towards the courthouse', None), ('rear.lat', COURT[0], None, None), ('rear.lon', COURT[1], None, None),
    ('texts.stated', 'A report, an eyewitness, the National Park Service\'s troop movement plans of 1971 or the Marine Corps University Press staff ride puts the unit here.', None, None),
    ('texts.inferred', 'Worked out from the sequence of events and from where its line stood; no source places this unit at this spot.', None, None),
    ('texts.moving', 'No source records this stretch. The unit is drawn moving between two recorded positions.', None, None),
    ('texts.after', 'The last record for this unit. A unit that broke, or joined the retreating column, is taken off the map a few minutes later.', None, None),
    ('texts.lost', 'Not shown any more: it broke and left the field, or marched off in the army\'s column. Its last record is below.', None, None),
    ('found.map_read', 'read from the National Park Service\'s troop movement plans (Hatch, 1971), laid on today\'s ground by the park boundary', None, None),
    ('found.modern_map', 'a road junction on the 1951 survey map', None, None),
    ('about.1', 'Unit positions come from the Revolutionary War workbook (the Guilford Courthouse rows), built from Cornwallis\'s and Greene\'s reports, Lee\'s and Tarleton\'s accounts, journals of men in the ranks, the National Park Service\'s study and troop movement plans of 1971 (Charles Hatch) and the Marine Corps University Press staff ride of 2021. Nothing here has been checked by a historian.', None, None),
    ('about.2', 'On the battlefield every unit is read from Hatch\'s five plans, laid on today\'s ground by the park boundary. Lines may be 75 m from where he drew them, and he drew them from accounts that give the order of the lines and rough distances, not places on the ground: so every position is rated low and carries a question mark.', None, None),
    ('about.3', 'The clock follows the staff ride: the British advance about 13:00, the first line breaks about 13:15, the third line is fought from 14:45 and the Continentals leave about 15:30. Cornwallis put the start at half past one, Greene about noon. The morning fights near New Garden are placed at three road junctions and may be an hour or two out. Tap a unit to see the range of times its record allows.', None, None),
    ('about.4', 'Solid symbols are positions a source gives. Dashed symbols are worked out or are the last position on record. A question mark means the place is doubtful.', None, None),
    ('about.5', 'Symbols are blue for the Americans and red for the British, German and Loyalist troops. The brigades of regulars are shown by their regiments throughout. Militia brigades that broke are taken off the map a few minutes after they leave their line, and the Continentals are shown as one column once they retreat.', None, None),
    ('about.6', 'The playback opens on "1781 with terrain", a reconstruction: the road, creeks, fences and houses as Hatch drew them in 1971, on today\'s ground, and west of his sheet the road of the 1951 survey. The map details (the i button) list each line with its source and how sure it is, and offer Hatch\'s own plans, phase by phase. The current map is the US Geological Survey\'s topographic map and Satellite its aerial photography, both streamed from the USGS.', None, None),
    ('about.7', 'Where the sources disagree (the hours, which militia brigade stood north of the road, where the third line stood, how many guns the British had, whether Cornwallis fired on his own Guards), the workbook\'s Hypotheses sheet gives each reading and says which one the playback follows.', None, None),
    ('about.8', 'Two places named in the day lie off the map and are shown at its edge with an arrow and their distance: Deep River Friends Meeting House, where Cornwallis camped the night before, and the iron works on Troublesome Creek, where Greene\'s army halted that night.', None, None),
    ('bases.1.id', 'r81t', None, None), ('bases.1.label', '1781 with terrain', None, None), ('bases.1.short', '1781', None, None), ('bases.1.recon', 'guilford-1781', None, None), ('bases.1.terrain', json.dumps(TERRAIN), None, None),
    ('bases.2.id', 'mod', None, None), ('bases.2.use', 'current', 'A standard map from the presets (base.current)', None),
    ('bases.3.use', 'satellite', 'A standard map from the presets (base.satellite): its rows below are only where this battle differs', None),
    ('bases.3.imagery.about', 'Today\'s ground from the air: photography from the US Department of Agriculture\'s National Agriculture Imagery Program (about 1 m detail), served free by the USGS National Map. The park keeps the eastern half of the battlefield in woods and fields; the ground where the British formed and the first line stood is now streets and houses.',
     None, 'Says what the aerial photograph shows of this field.'),
    ('bases.4.id', 'h71', None, None), ('bases.4.label', 'Hatch 1971, phase by phase', None, None), ('bases.4.short', 'Hatch', None, None), ('bases.4.series', True, None, None), ('bases.4.backdrop', 'current', None, None), ('bases.4.hidden', True, None, None),
    ('bases.4.note', 'Charles Hatch\'s five troop movement plans for the National Park Service (1971), each shown for its phase of the battle as the clock runs. His unit symbols are on them: the playback\'s positions were read from these plans.', None, None),
]
NATIONS = [('United States', 'American'), ('Great Britain', 'British'), ('Germany', 'German (Hesse-Cassel and Ansbach)'), ('Loyalist', 'Loyalist (provincial)')]
FORM = T('10:15'); DEP = T('12:34')
# track_id, unit, rows, part_of, hide_after, loose, nudge, starts_from_row, starts_at, start_route
TRACKS = [
    ('G-US-ARMY', 'G-US-ARMY', 'GP01', None, 'yes', None, None, None, None, None),
    ('G-US-COLUMN', 'G-US-ARMY', 'GP77; GP78', None, 'yes', None, None, None, None, None),
    ('G-US-HQ', 'G-US-HQ', 'GP15; GP64', None, 'yes', None, '0, -24', 'GP01', FORM, None),
    ('G-US-EATON', 'G-US-EATON', 'GP02; GP16', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-BUTLER', 'G-US-BUTLER', 'GP03; GP17', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-SING', 'G-US-SING', 'GP04; GP18', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-LYNCH', 'G-US-LYNCH', 'GP05; GP19; GP54', None, 'yes', 'yes', None, 'GP01', FORM, None),
    ('G-US-KIRK', 'G-US-KIRK', 'GP06; GP50; GP55', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-WASH', 'G-US-WASH', 'GP07; GP51; GP56; GP57; GP58', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-LAWS', 'G-US-LAWS', 'GP08; GP52', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-STEV', 'G-US-STEV', 'GP09; GP53', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-GREEN', 'G-US-GREEN', 'GP10; GP63', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-HAWES', 'G-US-HAWES', 'GP11; GP72', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-FIN', 'G-US-FIN', 'GP12', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-1MD', 'G-US-1MD', 'GP13; GP59; GP60; GP61', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-2MD', 'G-US-2MD', 'GP14; GP62', None, 'yes', None, None, 'GP01', FORM, None),
    ('G-US-LEEC', 'G-US-LEEC', 'GP20; GP21; GP22; GP23; GP24; GP25; GP26', None, 'yes', None, None, None, None, None),
    ('G-US-LEEI', 'G-US-LEEI', 'GP30; GP31; GP32; GP33; GP34; GP35; GP36', None, 'yes', None, None, None, None, None),
    ('G-US-CAMP', 'G-US-CAMP', 'GP40; GP41; GP42; GP43; GP44; GP45', None, 'yes', 'yes', None, None, None, None),
    ('G-BR-ARMY', 'G-BR-ARMY', 'GP100; GP101; GP102', None, 'yes', None, None, None, None, None),
    ('G-BR-HQ', 'G-BR-HQ', 'GP220; GP221; GP222', None, None, None, '0, 24', 'GP102', DEP, None),
    ('G-BR-TARL', 'G-BR-TARL', 'GP110; GP111; GP112; GP113; GP114; GP115; GP116; GP117', None, None, None, None, None, None, None),
    ('G-BR-GLI', 'G-BR-GLI', 'GP120; GP121; GP122; GP123; GP124', None, None, None, None, 'GP101', T('08:50'), None),
    ('G-BR-JAG', 'G-BR-JAG', 'GP125; GP126; GP127; GP128; GP129', None, None, 'yes', None, 'GP101', T('08:50'), None),
    ('G-BR-23', 'G-BR-23', 'GP130; GP150; GP151; GP152; GP153; GP154', None, None, None, None, 'GP101', T('09:22'), None),
    ('G-BR-33', 'G-BR-33', 'GP140; GP141; GP142; GP143; GP144; GP145', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-71', 'G-BR-71', 'GP160; GP161; GP162; GP163; GP164', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-BOSE', 'G-BR-BOSE', 'GP170; GP171; GP172; GP173', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-1GDS', 'G-BR-1GDS', 'GP180; GP181; GP182', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-2GDS', 'G-BR-2GDS', 'GP190; GP191; GP192; GP193; GP194', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-GREN', 'G-BR-GREN', 'GP200; GP201; GP202', None, None, None, None, 'GP102', DEP, None),
    ('G-BR-RA', 'G-BR-RA', 'GP210; GP211; GP212', None, None, None, None, 'GP102', T('12:30'), None),
]
# text, other name, (lat, lon), angle, level, kind, show, approximate
DEEP = (36.03139, -79.96528); IRON = (36.3072, -79.7378)
LABELS = [
    ('Great Salisbury road', 'New Garden Road', D(2, (430, 548)), -12, 0, 'road', 'recon', None), ('Great Salisbury road', 'New Garden Road', G.hp(1, 1150, 610), -30, 1, 'road', 'recon', None),
    ('Great Salisbury road', 'New Garden Road', q(690, 440), -52, 0, 'road', 'recon', None), ('Reedy Fork road', None, G.hp(1, 1660, 300), 82, 0, 'road', 'recon', None),
    ('Hunting Creek', 'Richland Creek', G.hp(1, 1640, 640), 75, 0, 'water', 'recon', None), ('Little Horsepen Creek', None, D(2, (140, 745)), 60, 0, 'water', 'recon', None), ('Horsepen Creek', None, q(860, 265), 8, 1, 'water', 'recon', None),
    ('Guilford Courthouse', None, G.hp(1, 1745, 440), None, 0, 'landmark', 'both', None), ('Hoskins house', None, D(2, (318, 680)), None, 0, 'landmark', 'both', None),
    ('New Garden Meeting House', 'Guilford College', MH, None, 0, 'landmark', 'both', 'yes'), ('"The Lane"', 'New Garden and Hobbs roads', LANE, None, 1, 'place', 'both', 'yes'),
    ('The cross road', 'Ballinger Road', XROAD, None, 1, 'place', 'both', 'yes'),
    ('corn fields', None, D(2, (455, 625)), None, 1, 'area', 'recon', None), ('fenced fields', None, D(2, (460, 465)), None, 1, 'area', 'recon', None), ('old fields', None, D(2, (985, 150)), None, 1, 'area', 'recon', None),
    ('open fields', None, D(2, (1150, 400)), None, 1, 'area', 'recon', None), ('woods', None, D(2, (640, 640)), None, 1, 'wood', 'recon', 'yes'), ('woods', None, D(2, (880, 380)), None, 1, 'wood', 'recon', 'yes'), ('woods', None, D(2, (1000, 760)), None, 1, 'wood', 'recon', 'yes'),
    ('to the Reedy Fork, 3 miles, and the iron works', None, G.hp(1, 1640, 135), None, 1, 'place', 'both', 'yes'), ('to Hillsborough', None, G.hp(1, 1990, 440), None, 1, 'place', 'both', 'yes'), ('from Deep River', None, q(120, 1300), None, 1, 'place', 'both', 'yes'),
    ('Guilford Courthouse National Military Park', None, G.topo(1820, 870), None, 1, 'area', 'current', None),
    ('Deep River Friends Meeting House', 'Cornwallis\'s camp, 14 March', DEEP, None, 0, 'town', 'far', 'yes'), ('Iron works on Troublesome Creek', 'Speedwell Furnace: Greene\'s camp, 15 March', IRON, None, 0, 'town', 'far', 'yes'),
]
SOURCE_USE = ['S138', 'S139', 'S140', 'S141', 'S142', 'S143', 'S144', 'S145', 'S146', 'S147', 'S85']
PLATES = json.load(open(os.path.join(HERE, 'georef', 'guilford_hatch_plates.json')))
PLAN = {1: ('Guilford Courthouse and the battlefield (the ground, no troops)', '08:00', '12:29'), 2: ('The armies deployed', '12:30', '13:09'), 3: ('The first line gives way', '13:10', '13:34'),
        4: ('The second line holds for a time, then breaks', '13:35', '14:39'), 5: ('Decision on the third line, and retreat', '14:40', '16:15')}
FIT = G.report()


def maps():
    out = []
    for n in range(1, 6):
        p = PLATES[str(n)]; c = p['corners']; t, f, to = PLAN[n]
        fit = dict(method='turned, scaled and shifted so the park boundary of 1971 lies on today\'s boundary (USGS Topo base map); each plate first brought onto plate 1 by its border', control_points=5,
                   off_m=[x['off_m'] for x in FIT['control']], m_per_px=p['m_per_px'], check=FIT['checks']['note'], script='pipeline/guilford_geo.py')
        out.append(dict(playback_id=PB, map_id='hatch-1971-%d' % n, title='Hatch, Battle of Guilford Courthouse, troop movement plan No. %d: %s (National Park Service, 1971)' % (n, t), short='Hatch %d' % n, label='Hatch 1971, plan %d' % n,
                        credit='Hatch, 1971 · National Park Service', source_id='S138', fitted_to_ground='yes', **{'from': T(f), 'to': T(to)}, file=p['file'],
                        tl_lat=c[0][0], tl_lon=c[0][1], tr_lat=c[1][0], tr_lon=c[1][1], br_lat=c[2][0], br_lon=c[2][1], bl_lat=c[3][0], bl_lon=c[3][1], fit=json.dumps(fit), scale_note='Scale bar: 400 feet to a division',
                        approx_m_per_px=p['m_per_px'],
                        note='Charles Hatch\'s troop movement plan No. %d for the National Park Service (drawn August 1971), with the park boundary of that year. His unit symbols are printed on it; the playback\'s positions were read from these plans. '
                             'Laid on the ground by the park boundary, to about 15 m; his creeks and road are sketched and lie up to 70 m from today\'s survey. Public domain (U.S. government work); reduced from the Internet Archive\'s scan.' % n))
    return out


RECON = dict(playback_id=PB, recon_id='guilford-1781', title='Guilford Courthouse, March 1781: a WarMapper reconstruction', label='1781 (reconstructed)',
             about='This is a WarMapper reconstruction, not a period map. On the battlefield the road, creeks, fences and houses are those Charles Hatch drew for the National Park Service in 1971, laid on the ground by the park boundary; he built them on the British plan of 1781 and on the generals\' descriptions. '
                   'West of his sheet the road to New Garden is the road of the 1951 survey. The ground is today\'s, much built over outside the park. Everything not drawn as a field was woods. Nothing here has been checked by a historian.',
             file='data/recon/guilford-1781.geojson', style='period-1899', made=TODAY, review_status=REV,
             notes='Hatch\'s lines were picked by eye from his plates (pipeline/recon/guilford_1781.py) and are good to about 75 m: his Hunting Creek lies about 70 m east of today\'s Richland Creek at the road. The roads west of his sheet are roads of 1951, rated low.',
             credit='WarMapper reconstruction from Hatch, 1971 (National Park Service) and the USGS sheets of 1951')
LAYERS = [('road-field', 1, 'The great road and the Reedy Fork road on the battlefield', 'road', 'S138', IA, 'Hatch (1971)', 'low', 'Picked by eye from Hatch\'s plans No. 1 and 2, fitted by the park boundary.'),
          ('road-approach', 2, 'The roads about New Garden, from the 1951 survey', 'road', 'S146', 'https://ngmdb.usgs.gov/topoview/', 'USGS topoView', 'low', 'Picked from the 1951 sheets reprojected to WGS 84: roads of 1951 on the lines of 1781.'),
          ('streams', 3, 'Hunting and Little Horsepen creeks and the vales', 'stream', 'S138', IA, 'Hatch (1971)', 'low', 'Picked by eye from Hatch\'s plans; Horsepen Creek from the 1951 sheet.'),
          ('fences', 4, 'The fences round the fields', 'detail', 'S138', IA, 'Hatch (1971)', 'low', 'Hatch\'s "cultivated or open field enclosures", picked by eye from his plan No. 2.'),
          ('houses', 5, 'The courthouse, the Hoskins house and the other buildings Hatch marks', 'detail', 'S138', IA, 'Hatch (1971)', 'low', 'Each drawn as a small square at the place Hatch marks.')]


# ---------------------------------------------------------------- writing
def header(ws): return [c.value for c in ws[1]]
def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r
def add(ws, row):
    h = header(ws); r = last_row(ws) + 1
    for k in row: assert k in h, '%s: no column %r' % (ws.title, k)
    for c, name in enumerate(h, 1):
        v = row.get(name)
        if v is not None: ws.cell(r, c, v)
    return r


def main():
    wb = openpyxl.load_workbook(WAR)
    if any(row[0].value == PB for row in wb['Playbacks'].iter_rows(min_row=2)): print('guilford-courthouse is already in the workbook: nothing done'); return
    sh = openpyxl.load_workbook(SHARED)
    ws = sh['Sources']; have = {r[0].value for r in ws.iter_rows(min_row=2)}
    for s in SOURCES:
        assert s['source_id'] not in have, s['source_id']; add(ws, s)
    ws = sh['Source candidates']; h = header(ws)
    for row in ws.iter_rows(min_row=2):
        if row[0].value in CANDIDATES:
            st, note = CANDIDATES[row[0].value]; row[h.index('status')].value = st
            old = row[h.index('notes')].value; row[h.index('notes')].value = ((old + ' ') if old else '') + note
    for c in NEW_CANDIDATES: add(ws, dict(zip(h, c)))
    for row in sh['Sources'].iter_rows(min_row=2):   # the textbook is now cited by a battle
        if row[0].value == 'S85':
            hh = header(sh['Sources']); cell = row[hh.index('used_for')]; cell.value = (cell.value + '; GUIL') if cell.value and 'GUIL' not in cell.value else cell.value
    rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 26 November 2026: the Battle of Guilford Courthouse')
    rm.cell(2, 1, 'Revolutionary War.xlsx: the Battle of Guilford Courthouse, 15 March 1781 (campaign ARW-SOU, battle GUIL, playback "guilford-courthouse"): %d units, %d position rows (GP01 to GP222), %d routes, %d events, %d hypotheses (GH01 to GH%02d) and %d gaps. '
                  'Sources S138 to S147 are new here: Hatch\'s National Park Service study and troop movement plans (1971), the commanders\' reports and the memoirs it quotes, the Marine Corps University Press staff ride (2021), the park\'s landscape report (2003) and the USGS maps of 1951 and today. '
                  'Five candidates added (SC-SOU10 to SC-SOU14). On the battlefield every position is read from Hatch\'s plans, laid on the ground by the park boundary (pipeline/guilford_geo.py); every one is rated low. Not read: Babits and Howard (2009), Baker, the British plan of 1787. '
                  'Written by pipeline/guilford_2026_11_26.py and pipeline/recon/guilford_1781.py. No change to the battle file format, the workbook sheets or the shared player.' % (len(UNITS), len(POS), len(ROUTES), len(EVENTS), len(HYP), len(HYP), len(GAPS)))
    # the war workbook
    for row in wb['Campaigns'].iter_rows(min_row=2):
        if row[0].value == CAMP:
            hh = header(wb['Campaigns']); c = row[hh.index('notes')]; c.value = (c.value or '') + ' 26 Nov 2026: Guilford Courthouse (battle GUIL) added; the campaign playback is still to follow.'
    add(wb['Battles'], BATTLE_ROW)
    for pid, label, s, e, src, note in PHASES: add(wb['Phases'], dict(phase_id=pid, battle_id=BATTLE, label=label, start=T(s), end=T(e), source_ids=src, notes=note))
    n = max(int(r[0].value[1:]) for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value)
    for other in ('U.S. Civil War', 'Philippine War', 'World War I'):
        o = openpyxl.load_workbook(os.path.join(FOLDER, other + '.xlsx'), read_only=True)
        n = max([n] + [int(r[0][1:]) for r in o['Assignments'].iter_rows(min_row=2, values_only=True) if r and r[0]])
    for (uid, name, label, side, nation, branch, ech, src, notes, parent, cmd, strength, asrc) in UNITS:
        code = '100%s1000%s000000' % ('3' if side == US else '6', SYM[(branch, ech)])
        add(wb['Units'], {'unit_id': uid, 'unit_name': name, 'map_label': label, 'side_id': side, 'nation': nation, 'branch': branch, 'echelon': ech, 'symbol_code': code, 'source_ids': src, 'sourced?': 'yes', 'notes': notes})
        n += 1
        add(wb['Assignments'], {'assign_id': 'A%03d' % n, 'unit_id': uid, 'parent_unit_id': parent, 'commander': cmd, 'strength / equipment': strength, 'valid_from': DAY, 'valid_to': DAY, 'source_ids': asrc})
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
    for hrow in HYP:
        for x in (hrow['rows'] or '').split('; '): assert not x or x in ids or x.startswith('GCE'), (hrow['hypothesis_id'], x)
        add(wb['Hypotheses'], hrow)
    for gid, gap, effect, close in GAPS: add(wb['Gaps'], {'gap_id': gid, 'battle_id': BATTLE, 'gap': gap, 'effect on the data': effect, 'how to close it': close, 'status in v2': 'Open (new on 26 Nov 2026).'})
    add(wb['Playbacks'], PLAYBACK)
    for s in SETTINGS: add(wb['Playback settings'], {'playback_id': PB, 'setting': s[0], 'value': s[1], 'what it does': s[2], 'why': s[3]})
    for name, short in NATIONS: add(wb['Nations'], dict(playback_id=PB, name=name, short=short))
    for (tid, unit, rows, part, hide, loose, nudge, sfr, sat, sroute) in TRACKS:
        for x in rows.split('; '): assert x in ids, (tid, x)
        add(wb['Tracks'], dict(playback_id=PB, track_id=tid, unit_id=unit, rows=rows, part_of_track=part, hide_after_last_row=hide, loose=loose, nudge=nudge, starts_from_row=sfr, starts_at=sat, start_route=sroute))
    used = {x for t in TRACKS for x in t[2].split('; ')}; assert used == ids, sorted(ids ^ used)
    for (text, other, ll, angle, level, kind, show, approx) in LABELS:
        add(wb['Labels'], dict(playback_id=PB, text=text, other_name=other, lat=ll[0], lon=ll[1], angle=angle, level=level, kind=kind, show=show, approximate=approx))
    for m in maps(): add(wb['Maps'], m)
    add(wb['Reconstructions'], RECON)
    for (lid, order, title, kind, src, link, ll, conf, how) in LAYERS:
        add(wb['Recon layers'], dict(recon_id='guilford-1781', layer_id=lid, order=order, title=title, kind=kind, source_id=src, link=link, link_label=ll, method='traced', confidence=conf, **{'from': DAY, 'to': DAY}, how_read=how, review_status=REV))
    add(wb['Next links'], dict(link_id='N02', from_playback='cowpens', to_playback=PB, label='Battle of Guilford Courthouse', back_label='Battle of Cowpens', chapter='hist-340-sc',
                               notes='HIST 340, 16 Jan: Cowpens leads on to Guilford Courthouse for now (Morgan, 26 Nov 2026). When Greene\'s campaign playback is built (Session 5), replace this row by Cowpens to the campaign and the campaign to Guilford.'))
    titles = {s['source_id']: s['title'] for s in SOURCES}; titles['S85'] = 'American Military History, volume 1'
    ws = wb['Source uses']
    for sid in SOURCE_USE:
        r = last_row(ws) + 1
        add(ws, dict(source_id=sid, title=titles[sid], campaign_id=CAMP, playback_id=PB,
                     positions='=COUNTIFS(Positions!$X:$X,"*"&$A%d&"*",Positions!$C:$C,"GUIL")' % r, events='=COUNTIFS(Events!$I:$I,"*"&$A%d&"*",Events!$C:$C,"GUIL")' % r,
                     routes='=COUNTIFS(Routes!$K:$K,"*"&$A%d&"*",Routes!$C:$C,"GUIL")' % r, units='=COUNTIFS(Units!$J:$J,"*"&$A%d&"*",Units!$A:$A,"G-*")' % r,
                     period_maps='=COUNTIFS(Maps!$G:$G,$A%d,Maps!$A:$A,$D%d)' % (r, r), total='=SUM(E%d:I%d)' % (r, r)))
    r2 = wb['Read me']; r2.append([]); r2.append(['Guilford Courthouse (26 Nov 2026)', 'The Battle of Guilford Courthouse, 15 March 1781, added to campaign ARW-SOU as battle GUIL, playback "guilford-courthouse": rows GP01 to GP222, units G-..., events GCE01 to GCE16, routes RGC01 to RGC17, '
                                           'hypotheses GH01 to GH10, gaps GG01 to GG09, five fitted maps and a reconstruction. See the change log in "Sources and notes.xlsx" and pipeline/guilford_2026_11_26.py.'])
    wb.save(WAR); sh.save(SHARED)
    print('Guilford Courthouse: %d units, %d positions, %d routes, %d events, %d hypotheses, %d gaps, %d sources' % (len(UNITS), len(POS), len(ROUTES), len(EVENTS), len(HYP), len(GAPS), len(SOURCES)))


if __name__ == '__main__':
    main()
