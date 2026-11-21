"""20 Nov 2026 (Morgan's brief "Philippine War 1899 data pilot"): the fourth war, scoped to the 1899 campaign in central and
northern Luzon, with one playback: Manila, 4-5 February 1899.

Adds to the master workbook:
  Wars, Campaigns, Battles (Manila and skeleton rows for the later 1899 phases), Sides, Nations, Sources (S64-S73),
  Source candidates (SC for the items not used or not online), Units and Assignments (8th Army Corps from the January 1899 roster
  and Otis's report; Filipino commands only as far as Taylor's notes go), Positions, Tracks, Events, Labels, Maps (Warking's
  Signal Corps map, fitted by pipeline/georef/manila_georef.py), Playbacks and Playback settings, Conflicts and Gaps.
Every new Positions row is "Needs review". Run once; it refuses to run twice.

Sources read (see notes in the PR): Otis's report, Manila printing 1899 (S65), pp. 161-167, checked against the page images;
the January 1899 roster (S66); Taylor's 1903 compilation (S67), footnotes only; Warking's map (S64), read from crops of the
full-resolution LoC scan with a pixel grid.
"""
import copy, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'georef'))
import manila_georef as G
import openpyxl

WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx')
wb = openpyxl.load_workbook(WB)
assert not any(r[0].value == 'PHW' for r in wb['Wars'].iter_rows(min_row=2)), 'already applied'
TODAY = '2026-11-20'


def head(ws): return [c.value for c in ws[1]]


def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r


def add(sheet, values, like=None):
    """Append one row; copy the cell styles of the row `like` (default the last filled row)."""
    ws = wb[sheet]; h = head(ws); src = like or last_row(ws); r = last_row(ws) + 1
    for k in values:
        assert k in h, '%s has no column %r' % (sheet, k)
    for j in range(1, len(h) + 1):
        s = ws.cell(src, j)
        if s.has_style: ws.cell(r, j)._style = copy.copy(s._style)
    for k, v in values.items(): ws.cell(r, h.index(k) + 1).value = v
    return r


def px(x, y):
    la, lo = G.px2ll(x, y); return round(float(la), 6), round(float(lo), 6)


# ---------------------------------------------------------------- war, campaign, battles
add('Wars', {'war_id': 'PHW', 'name': 'Philippine War', 'start_year': 1899, 'end_year': 1903,
             'notes': 'Named and dated as in the pilot brief ("The Philippine War, 1899-1903"). The United States declared the war over on 4 July 1902; '
                      'fighting went on in places after that. Pilot scope: the 1899 campaign in central and northern Luzon. Wikidata id not checked.'})
add('Campaigns', {'campaign_id': 'PHW-LUZ99', 'war_id': 'PHW', 'name': 'Luzon campaign of 1899 (central and northern Luzon)', 'start_date': '1899-02-04',
                  'end_date': '1899-12-31', 'notes': 'Pilot scope from the brief. Start: the outbreak at Manila on the evening of 4 Feb 1899 (S65). End date is the end of the year, not a historical boundary.'})
BAT = [
    ('PHW-MNL', None, 'Battle of Manila (1899)', '1899-02-04 20:30', '1899-02-04 20:30', '1899-02-05 17:00', '1899-02-05 17:00', 14.595, 121.0,
     'Otis (S65, p. 161): the battle "commenced at half past eight o\'clock on the evening of February 4" and "continued until five the next evening". '
     'Playback: manila (built 20 Nov 2026). The point is the middle of the American line, not a single spot.', 15),
    ('PHW-MALOLOS', None, 'Advance on Malolos (MacArthur), March 1899', '1899-03-24', '1899-03-24', None, None, None, None,
     'Skeleton row. PIS pamphlet (S68, p. 10): "The first northern campaign began March 24, under command of General MacArthur." End date not yet sourced. '
     'Maps: LoC 2009582412 (Second Division, 1 Mar-31 May 1899; candidate) and PW-M01 (S69). Playback: not started.', None),
    ('PHW-LAWTON', None, "Lawton's northern expedition, April-May 1899", None, None, None, None, None, None,
     'Skeleton row. Dates not yet sourced (PIS S68 has "Northern Campaign of April and May"; Lawton ordered north on 14 May per Otis as quoted in S68). '
     'Map: PW-M01 (S69). Playback: not started.', None),
    ('PHW-FALL99', None, 'Fall campaign, October-December 1899', '1899-10-11', '1899-10-11', '1900-01-05', '1900-01-05', None, None,
     'Skeleton row. Dates are those of Young\'s itinerary printed on PW-M03 (S71): "between October 11, 1899, and January 5, 1900" (his brigade only, not the whole campaign). '
     'Maps: PW-M03 (S71), PW-M02 (S70, Madrid meridian). Playback: not started.', None),
    ('PHW-YOUNG', 'PHW-FALL99', "Young's pursuit of Aguinaldo (provisional cavalry brigade), northern Luzon", '1899-10-11', '1899-10-11', '1900-01-05', '1900-01-05', None, None,
     'Skeleton row. Dates from the title block of PW-M03 (S71). Playback: not started.', None),
]
for bid, par, name, se, sl, ee, el, la, lo, notes, ext in BAT:
    add('Battles', {'battle_id': bid, 'campaign_id': 'PHW-LUZ99', 'parent_battle_id': par, 'name': name, 'start_earliest': se, 'start_latest': sl,
                    'end_earliest': ee, 'end_latest': el, 'lat': la, 'lon': lo, 'coord_precision': 'battle' if la else None,
                    'coord_source': 'Middle of the line on S64, fitted' if la else None, 'notes': notes, 'extent_km': ext})

add('Sides', {'side_id': 'PHW-US', 'war_id': 'PHW', 'name': 'United States (Department of the Pacific and Eighth Army Corps)', 'frame': 'blue', 'colour': '124F93',
              'notes': 'Frame colour is a drawing convention, not a judgement.', 'code': 'US', 'short': 'American'})
add('Sides', {'side_id': 'PHW-PH', 'war_id': 'PHW', 'name': 'Philippine Republic (Army of the Philippine Republic)', 'frame': 'red', 'colour': 'B02A1C',
              'notes': 'The American reports of 1899 call them "insurgents"; the pilot quotes that word only where it quotes them.', 'code': 'PH', 'short': 'Filipino'})
add('Nations', {'playback_id': 'manila', 'name': 'United States', 'short': 'American'})
add('Nations', {'playback_id': 'manila', 'name': 'Philippines', 'short': 'Filipino'})

# ---------------------------------------------------------------- sources
SRC = [
    ('S64', 'Map of Manila and vicinity: showing positions of troops prior to the battle of February 5th and location of the military telegraph lines then in operation, also positions and locations after the capture of Caloocan, February 10, 1899',
     'J. H. Warking, Sergt., Vol. Signal Corps, under Lt. Col. R. E. Thompson, Chief Signal Officer', '1899-02',
     'Primary-era map: troop positions drawn by the Signal Corps, February 1899',
     'Manila, February 1899. Scale 1:25,000 (scale bar in yards). Blue-line photocopy, 48 x 69 cm, oriented with north to the left. Library of Congress, Geography and Map Division, G8064.M5 1899 .W3, digital id g8064m ct002453 (scan 11,533 x 7,657 px). Includes "Index to troops engaged and their final positions".',
     'yes (scan)', 'https://www.loc.gov/item/2009582402/', 'LoC map collections: published before 1922 and/or by the US government; LoC "not aware of any U.S. copyright protection". Credit: Library of Congress, Geography and Map Division.',
     'USED from 20 Nov 2026: the period map of the Manila playback (PW-M07 in the brief). The 1998 LoC list spells the compiler "Watkins"; the item record and the title block say Warking. "Former ... outpost" labels mark positions before the battle; the heavy double-dashed lines named for regiments match the index of final positions (after 10 Feb).',
     'PHW-MNL', 'map', 'public domain (US)', 'yes', 'yes, with holder credit', 'loc.gov'),
    ('S65', 'Report of E. S. Otis, commanding Department of the Pacific and 8th Army Corps, military governor in the Philippine Islands', 'Maj. Gen. Elwell S. Otis', '1899',
     "Primary: commander's report", 'Manila, P.I., 1899. 274 pp. University of Michigan copy, Internet Archive ahz9383.0001.001.umich.edu. The same report is printed in the Annual Reports of the War Department for 1899 (PW-T01, HathiTrust 102278231).',
     'yes, pp. 161-167 against the page images', 'https://archive.org/details/ahz9383.0001.001.umich.edu', 'Public domain (US government work, 1899)',
     'USED from 20 Nov 2026: the battle of 4-5 Feb, with the telegrams and their clock times (pp. 161-167). Page numbers are the printed ones.',
     'PHW-MNL', 'official report', 'public domain (US)', 'yes', 'yes', 'archive.org'),
    ('S66', 'Roster of troops serving in the Department of the Pacific and Eighth Army Corps, January 1899', "Adjutant General's Office, Department of the Pacific and Eighth Army Corps", '1899-01',
     'Primary: official roster', 'Manila, January 1899. Bancroft Library copy (University of California), Internet Archive rosteroftroopsse00unitrich.',
     'yes (organization section)', 'https://archive.org/details/rosteroftroopsse00unitrich', 'Not in copyright (Internet Archive: NOT_IN_COPYRIGHT)',
     'USED from 20 Nov 2026: divisions, brigades, commanders and companies as of January 1899. Strength tables not used (the OCR is unreadable).',
     'PHW-MNL', 'official report', 'public domain (US)', 'yes', 'yes', 'archive.org'),
    ('S67', 'Compilation of Philippine insurgent records', 'John R. M. Taylor (War Department, Bureau of Insular Affairs)', '1903',
     'Primary: captured Filipino records, translated and annotated by the US War Department',
     "Washington, Gov't print. off., 1903 (68 pp. issued; galley). Library of Congress copy, Internet Archive compilationofphi00unit. The fuller compilation is LCCN 07003191 (PW-A02).",
     'no (footnotes read in the text file only)', 'https://archive.org/details/compilationofphi00unit', 'Library of Congress: "unaware of any copyright restrictions for this item"',
     "USED from 20 Nov 2026 for the Filipino commands around Manila, which Taylor's footnotes date to August-September 1898. The telegrams are Filipino documents; the footnotes are an American officer's.",
     'PHW-MNL', 'official records volume', 'public domain (US)', 'yes', 'yes', 'archive.org'),
    ('S68', 'Luzon campaign, from February to December, 1899', 'Philippine Information Society', '1901-04-22',
     'Partisan compilation (anti-imperialist): dates and cross-checks only', 'Boston, Philippine Information Society, First series IX, 22 April 1901. Boston Public Library copy, Internet Archive luzoncampaignfro00phil.',
     'no', 'https://archive.org/details/luzoncampaignfro00phil', 'Public domain (1901)',
     'Not used for positions. Its pamphlet VII, "Outbreak of Hostilities, February 4, 1899", is the one on the opener: not yet found.',
     'PHW-LUZ99', 'book', 'public domain', 'yes', 'yes', 'archive.org'),
    ('S69', 'Map of central Luzon, showing a portion of the field of operations of the 8th Army Corps, Major Gen. Elwell S. Otis, commanding', 'US Army Corps of Engineers; compiled by Capt. Wm. L. Siebert [Sibert]', '1899-11',
     'Primary-era map', 'Compiled Manila, November 1899; printed [1900] in the Annual Reports of the War Department, FY 1900 ("War 56 2"). Scale about 1:264,000; 67 x 38 cm. Boston Public Library, Leventhal Map & Education Center, G8062.L8S1 1899 .U5 (06_01_018384); IIIF commonwealth:5m60tz00z (4,619 x 7,621).',
     'yes (record)', 'https://collections.leventhalmap.org/search/commonwealth:c821kr77c', 'No known copyright restrictions. No known restrictions on use. (Boston Public Library)',
     'PW-M01. For the Malolos and Lawton phases. Not yet fitted.', 'PHW-LUZ99', 'map', 'no known restrictions', 'yes', 'yes, with holder credit', 'collections.leventhalmap.org'),
    ('S70', 'Map of northern Luzon, showing a portion of the field of operations of the 8th Army Corps, Major General Elwell S. Otis commanding', 'US Engineer Office, 8th Army Corps', '1900',
     'Primary-era map', '[1900], Annual Reports of the War Department, FY 1900. Scale 1:400,000; 81 x 105 cm. Prime meridian: Madrid. Map and legend in Spanish. Boston Public Library G8062.L8S1 1900 .U52 (06_01_018383); IIIF commonwealth:tt44sv024 (11,855 x 9,495).',
     'yes (record)', 'https://collections.leventhalmap.org/search/commonwealth:bn99df13n', 'No known copyright restrictions. No known restrictions on use. (Boston Public Library)',
     'PW-M02. Madrid meridian: longitudes to be shifted before fitting. Not yet fitted.', 'PHW-LUZ99', 'map', 'no known restrictions', 'yes', 'yes, with holder credit', 'collections.leventhalmap.org'),
    ('S71', 'Map of northern Luzon [fall campaign of 1899, provisional cavalry brigade]', 'Prepared under Brig. Gen. S. B. M. Young; compiled by 1st Lt. H. P. Howard, 3d Cavalry', '1900',
     'Primary-era map', 'Washington, Norris Peters Co., 1900; from Serial Set 4075 H.doc.2/7. Scale about 1:610,000; on sheet 75 x 38 cm. Includes "Itinerary and list of troops under command of General Young between October 11, 1899, and January 5, 1900." Boston Public Library G8062.L8S1 1899 .H69 (06_01_018444); IIIF commonwealth:wp98cr75t (3,200 x 6,272).',
     'yes (record)', 'https://collections.leventhalmap.org/search/commonwealth:4f16g891g', 'No known copyright restrictions. No known restrictions on use. (Boston Public Library)',
     'PW-M03. For the pursuit of Aguinaldo. Prime meridian not stated on the record: check the sheet. Not yet fitted.', 'PHW-LUZ99', 'map', 'no known restrictions', 'yes', 'yes, with holder credit', 'collections.leventhalmap.org'),
    ('S72', 'Military map of the isle of Luzon', 'War Department, Adjutant General\'s Office, Military Information Division', '1900',
     'Primary-era map: overview', '[1900] printing, 2 sheets, 131 x 97 cm; scale about 1:550,000; inset Manila. Prime meridian: Manila. Boston Public Library G8062.L8 1900 .U55; IIIF commonwealth:sn00dg67f and commonwealth:tx31t1153.',
     'yes (record)', 'https://collections.leventhalmap.org/search/commonwealth:cc08kx74j', 'No known copyright restrictions. No known restrictions on use. (Boston Public Library)',
     'PW-M09 (BPL copy; the brief\'s 2d ed. 1899 is the Yale copy, not checked). Overview only.', 'PHW-LUZ99', 'map', 'no known restrictions', 'yes', 'yes, with holder credit', 'collections.leventhalmap.org'),
    ('S73', 'Wikidata: coordinates of churches and landmarks in Metro Manila', 'Wikidata contributors', '2026-11-20',
     'Reference: coordinates', 'SPARQL box query, read 20 Nov 2026. Items used are named in pipeline/georef/manila_georef.py and in each position row.',
     'n/a', 'https://query.wikidata.org/', 'CC0', 'USED for the control points of S64 and for places named in the reports (powder magazine, El Deposito, San Pedro Macati church).',
     'PHW-MNL', 'reference', 'open licence (CC0)', 'yes', None, 'wikidata.org'),
]
SH = ['source_id', 'title', 'author', 'date', 'type', 'citation', 'page verified?', 'url', 'rights', 'notes', 'used_for', 'kind', 'rights_status', 'may_host', 'rights_checked', 'site']
for s in SRC:
    v = dict(zip(SH, s)); v['war'] = 'PHW'; add('Sources', v)

CAND = [
    ('PW-M04 Theatre of Military Operations in Luzon, 1899 (MID; NGM vol. x plate 5 reprint)', 'University of Hawaii at Manoa (eVols)', 'https://evols.library.manoa.hawaii.edu/items/a92efaec-8bf4-43c2-9a8a-df1078e90e7f',
     'Approx 1:200,000; E120°00\'-E121°55\'31"/N15°06\'-N14°03\'; 58 x 94 cm; TIFF 85 MB; IIIF enabled', 'Record behind a Cloudflare check; not read', 'unclear (to Morgan)', 'blocked', 'P0'),
    ('PW-M05 Theatre of military operations in Luzon, 1899 (UMN copy)', 'University of Minnesota via BTAA Geoportal', 'https://geo.btaa.org/catalog/p16022coll230:4183',
     '114 x 92 cm; relief by spot heights', 'Record behind a browser check; not read', 'unclear (to Morgan)', 'blocked', 'P1'),
    ('PW-M06 Location of troops in the Philippine Islands, March 31, 1900', 'Library of Congress, G8061.S1 1900 .U5 (LCCN 2012586634)', 'https://www.loc.gov/item/2012586634/',
     '72 x 53 cm; Mindanao inset ca. 1:4,000,000; garrisons at 31 Mar 1900', 'IIIF service id not yet found', 'ok to include (LoC: free to use and reuse unless stated)', 'found', 'P2'),
    ('PW-M08 Sellner, Plan of Cavite, Manila, Morong, Bulacan and Pampanga ... to May 1, 1899 (1:100,000)', 'Library of Congress (in person only, per its 1998 list)', 'https://webarchive.library.unt.edu/eot2008/20090109115034/http:/www.loc.gov/rr/hispanic/1898/mapphil.html',
     '47 x 77 cm; American operations Feb-May 1899', 'No online record or scan found (20 Nov 2026)', 'unclear', 'not online', 'P1'),
    ('Map showing operations of Second Division, 8th Army Corps, from March 1st to May 31st 1899 (Shunk, Ourand)', 'Library of Congress G3701.S57 1899 .S5 (LCCN 2009582412)', 'https://www.loc.gov/item/2009582412/',
     '76 x 69 cm, col.; raster image online', 'For the Malolos phase', 'ok to include (LoC map collections advisory)', 'found', 'P0'),
    ('Haan, Map of the City of Manila and Vicinity, showing operations of Second Division, 8th Army Corps, 4-28 Feb 1899', 'Filipinas Heritage Library G 8062 M2 1899; printed in the 1899 annual report', 'https://www.filipinaslibrary.org.ph/biblio/42273',
     'Second Division operations during February 1899', 'No online scan found yet; would be the best Second Division map for the opener', 'unclear', 'found', 'P1'),
    ('PW-T01 Report of Maj. Gen. E. S. Otis ... 1899 (Annual Reports of the War Department, Serial Set 4073)', 'HathiTrust (Yale copy) 102278231', 'https://catalog.hathitrust.org/Record/102278231',
     'Otis with the subordinate commanders\' reports (Anderson, MacArthur, King, Ovenshine, H. G. Otis, Hale) and their maps', 'Not reachable from the workspace; the Manila printing (S65) was read instead. The subordinate reports are the next thing to read.', 'ok to include (US government work)', 'located', 'P0'),
    ('PW-T03 Ramsey, The Savage Wars of Peace (CSI Press, 2007)', 'DTIC ADA474912', 'https://apps.dtic.mil/sti/pdfs/ADA474912.pdf', '1900-02 pacification', 'Later phases', 'US Government publication', 'found', 'P2'),
    ('PW-T04 Marple, The Philippine Scouts ... Northern Luzon, 1899 (CGSC thesis)', 'DTIC ADA138032', 'https://apps.dtic.mil/sti/pdfs/ADA138032.pdf', 'Northern Luzon 1899', 'Year not confirmed', 'US Government publication', 'found', 'P1'),
    ('PW-A01 NARA RG 395, Records of US Army Overseas Operations and Commands (Philippine Insurrection)', 'National Archives', 'https://www.archives.gov/research/guide-fed-records/groups/395.html', 'About 51 linear feet', 'Mostly not online', 'US Government records', 'found', 'P3'),
]
for i, (title, holder, url, holds, access, rights, status, pr) in enumerate(CAND, 1):
    add('Source candidates', {'candidate_id': 'SC-PW%02d' % i, 'title': title, 'holder': holder, 'url': url, 'war': 'PHW', 'battles': 'PHW-MNL; PHW-LUZ99',
                              'what it holds': holds, 'access': access, 'rights': rights, 'status': status, 'priority': pr, 'added': TODAY})

# ---------------------------------------------------------------- units and assignments
# (id, name, label, side, branch, echelon, sources, notes)
UNITS = [
    ('PH-US-CORPS', 'Department of the Pacific and Eighth Army Corps', 'Otis (8th Corps)', 'PHW-US', 'Infantry', 'Corps', 'S66; S65', None),
    ('PH-US-1DIV', 'First Division, Eighth Army Corps', 'Anderson', 'PHW-US', 'Infantry', 'Division', 'S66; S65', 'All troops south of the Pasig (S65, p. 162).'),
    ('PH-US-1-1', '1st Brigade, First Division', 'King', 'PHW-US', 'Infantry', 'Brigade', 'S66; S65', None),
    ('PH-US-1-2', '2nd Brigade, First Division', 'Ovenshine', 'PHW-US', 'Infantry', 'Brigade', 'S66; S65', None),
    ('PH-US-2DIV', 'Second Division, Eighth Army Corps', 'MacArthur', 'PHW-US', 'Infantry', 'Division', 'S66; S65', 'North of the Pasig.'),
    ('PH-US-2-1', '1st Brigade, Second Division', 'H. G. Otis', 'PHW-US', 'Infantry', 'Brigade', 'S66', 'Brig. Gen. Harrison Gray Otis, not the corps commander.'),
    ('PH-US-2-2', '2nd Brigade, Second Division', 'Hale', 'PHW-US', 'Infantry', 'Brigade', 'S66', None),
    ('PH-US-PROV', 'Provost Guard, Manila', 'Hughes (Provost)', 'PHW-US', 'Infantry', 'Brigade', 'S66; S65', 'Held the city; lent battalions of the 1st Tennessee to the front on 5 Feb (S65, pp. 162, 165).'),
    ('PH-US-CAL', '1st California Volunteer Infantry', '1 Cal', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', 'Col. James F. Smith (S65, p. 165: "Smith (Colonel of California regiment)").'),
    ('PH-US-WASH', '1st Washington Volunteer Infantry', '1 Wash', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', None),
    ('PH-US-IDA', '1st Idaho Volunteer Infantry', '1 Idaho', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', '8 companies (S66).'),
    ('PH-US-NDAK', '1st North Dakota Volunteer Infantry', '1 N Dak', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', '8 companies (S66).'),
    ('PH-US-14INF', '14th US Infantry', '14 Inf', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', 'HQ, band and 10 companies (S66).'),
    ('PH-US-4CAV', '4th US Cavalry (troops C, E, G, I, K, L)', '4 Cav', 'PHW-US', 'Cavalry', 'Battalion', 'S66; S65; S64', 'Six troops, dismounted in the battle as far as the sources read say.'),
    ('PH-US-MTNBTY', 'Separate Mountain Battery', 'Mtn Bty', 'PHW-US', 'Artillery', 'Battery', 'S66; S64', 'First Division troops.'),
    ('PH-US-NEB', '1st Nebraska Volunteer Infantry', '1 Neb', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', 'Col. John M. Stotsenburg (S65 names him with the regiment).'),
    ('PH-US-SDAK', '1st South Dakota Volunteer Infantry', '1 S Dak', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', None),
    ('PH-US-COL', '1st Colorado Volunteer Infantry', '1 Colo', 'PHW-US', 'Infantry', 'Regiment', 'S66; S64', None),
    ('PH-US-KANS', '20th Kansas Volunteer Infantry', '20 Kans', 'PHW-US', 'Infantry', 'Regiment', 'S66; S64', 'Col. Frederick Funston (not in the sources read; Wikipedia only).'),
    ('PH-US-MONT', '1st Montana Volunteer Infantry', '1 Mont', 'PHW-US', 'Infantry', 'Regiment', 'S66; S65; S64', None),
    ('PH-US-PENN', '10th Pennsylvania Volunteer Infantry', '10 Pa', 'PHW-US', 'Infantry', 'Regiment', 'S66; S64', 'HQ and 8 companies (S66).'),
    ('PH-US-3ART', '3rd US Artillery (batteries G, H, K, L, serving as infantry)', '3 Arty', 'PHW-US', 'Artillery', 'Battalion', 'S66; S64', 'Heavy artillery batteries in the 1st Brigade, Second Division (S66). That they fought as infantry is not stated in the sources read.'),
    ('PH-US-UTAH', 'Utah Light Artillery (batteries A and B)', 'Utah Bty', 'PHW-US', 'Artillery', 'Battery', 'S66; S64', 'Second Division troops (S66).'),
    ('PH-US-TENN2', '1st Tennessee Volunteer Infantry (second battalion lent by the Provost Guard)', '1 Tenn (2nd bn)', 'PHW-US', 'Infantry', 'Battalion', 'S65', 'S65 p. 165: borrowed from the Provost Marshal in the afternoon of 5 Feb and taken to the centre of Anderson\'s line.'),
    ('PH-US-TENN', '1st Tennessee Volunteer Infantry (battalion lent by the Provost Guard)', '1 Tenn (bn)', 'PHW-US', 'Infantry', 'Battalion', 'S66; S65', 'S66 has the regiment split between the Provost Guard (8 companies) and the District of Cavite (HQ and 4 companies). S65: one battalion sent to MacArthur in the morning of 5 Feb, a second to Anderson\'s centre in the afternoon.'),
    # Filipino commands: only as far as Taylor's notes (S67) and the American reports go.
    ('PH-PH-MNL', 'Army of the Philippine Republic about Manila', 'Ricarte (Aug 1898)', 'PHW-PH', 'Infantry', 'Army', 'S67',
     'Taylor (S67) puts Gen. Artemio Ricarte "in command of entire insurgent army about Manila" in August 1898 and says the failure of the attack of 4-5 Feb "greatly impaired his prestige". Who commanded on 4 Feb 1899 is not stated in the sources read. Strength not in the sources read.'),
    ('PH-PH-Z3', 'Third zone of Manila (Col. Luciano San Miguel)', '3rd zone (San Miguel)', 'PHW-PH', 'Infantry', 'Brigade',
     'S67; S65', 'Taylor (S67): "Col. San Miguel. It was in this zone that outbreak of February 4 occurred." Echelon "brigade" is a drawing choice for a zone command; its size is not in the sources read.'),
    ('PH-PH-Z4', 'Fourth zone, Caloocan', '4th zone (Caloocan)', 'PHW-PH', 'Infantry', 'Brigade', 'S67',
     'Taylor (S67): Lt. Col. Pilar "commanding 4th zone, Caloocan", 22 Aug 1898; Pantaleon Garcia "at this time in command at Caloocan" (Aug 1898). Who held it on 4 Feb 1899 is not in the sources read.'),
    ('PH-PH-SOUTH', 'Filipino forces south of Manila (Pineda/Pasay)', 'South of Manila', 'PHW-PH', 'Infantry', 'Brigade', 'S67',
     'Taylor (S67): Gen. Mariano Noriel "in command of insurgents south of Manila", July-Aug 1898, at Pineda (Pasay) and Paranaque. Not shown to be his on 4 Feb 1899.'),
    ('PH-PH-SPM', 'Filipino forces at San Pedro Macati', 'S. Pedro Macati', 'PHW-PH', 'Infantry', 'Brigade', 'S67',
     'Taylor (S67): Gen. Pio del Pilar at San Pedro Macati, Aug 1898; his command "extended to meet that of Noriel, at Pineda". Not shown to be his on 4 Feb 1899.'),
    ('PH-PH-SAGUNS', 'Filipino guns at Santa Ana (two Krupp guns)', '2 Krupp guns', 'PHW-PH', 'Artillery', 'Section', 'S64; S65',
     'S64 marks "2 Krupp Guns of Insurgents" beside Santa Ana; S65 (p. 167): on 5 Feb "two Krupp guns captured".'),
]
UH = ['unit_id', 'unit_name', 'map_label', 'side_id', 'branch', 'echelon', 'source_ids', 'notes']
for u in UNITS:
    v = dict(zip(UH, u)); v['nation'] = 'United States' if u[3] == 'PHW-US' else 'Philippines'; v['sourced?'] = 'yes'; add('Units', v)

A = [  # (unit, parent, commander, from, to, sources, notes)
    ('PH-US-CORPS', None, 'Maj. Gen. Elwell S. Otis', '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-1DIV', 'PH-US-CORPS', 'Maj. Gen. Thomas M. Anderson', '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-1-1', 'PH-US-1DIV', 'Brig. Gen. Charles King', '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-1-2', 'PH-US-1DIV', 'Brig. Gen. Samuel Ovenshine', '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-2DIV', 'PH-US-CORPS', 'Maj. Gen. Arthur MacArthur', '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-2-1', 'PH-US-2DIV', 'Brig. Gen. Harrison Gray Otis', '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-2-2', 'PH-US-2DIV', 'Brig. Gen. Irving Hale', '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-PROV', 'PH-US-CORPS', 'Brig. Gen. Robert P. Hughes', '1899-01-01', '1899-02-28', 'S66; S65', None),
    # January roster (C-PW1): then as Otis's narrative of 5 Feb has them
    ('PH-US-CAL', 'PH-US-1-1', 'Col. James F. Smith', '1899-01-01', '1899-02-28', 'S66; S65', '12 companies (S66). In King\'s brigade both in January (S66) and on 5 Feb (S65).'),
    ('PH-US-WASH', 'PH-US-1-2', None, '1899-01-01', '1899-02-03', 'S66', 'January roster: Ovenshine\'s brigade. See C-PW1.'),
    ('PH-US-WASH', 'PH-US-1-1', None, '1899-02-04', '1899-02-28', 'S65', 'On 5 Feb Otis has the Washingtons in King\'s brigade (p. 164). See C-PW1.'),
    ('PH-US-IDA', 'PH-US-1-2', None, '1899-01-01', '1899-02-03', 'S66', 'January roster: Ovenshine\'s brigade. See C-PW1.'),
    ('PH-US-IDA', 'PH-US-1-1', None, '1899-02-04', '1899-02-28', 'S65', 'On 5 Feb Otis has the Idahos in King\'s brigade (p. 164). See C-PW1.'),
    ('PH-US-NDAK', 'PH-US-1-2', None, '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-14INF', 'PH-US-1-1', None, '1899-01-01', '1899-02-03', 'S66', 'January roster: King\'s brigade. See C-PW1.'),
    ('PH-US-14INF', 'PH-US-1-2', 'Capt. Murphy (the part in the centre, 5 Feb)', '1899-02-04', '1899-02-28', 'S65', 'On 5 Feb Otis lists it with the 1st North Dakota and 4th Cavalry on Ovenshine\'s line (p. 166). See C-PW1.'),
    ('PH-US-4CAV', 'PH-US-1-1', None, '1899-01-01', '1899-02-03', 'S66', 'January roster: King\'s brigade. See C-PW1.'),
    ('PH-US-4CAV', 'PH-US-1-2', None, '1899-02-04', '1899-02-28', 'S65', 'As the 14th Infantry. "Wheeler\'s troop of the 4th Cavalry" fought in the centre (p. 164).'),
    ('PH-US-MTNBTY', 'PH-US-1DIV', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-NEB', 'PH-US-2-2', 'Col. John M. Stotsenburg', '1899-01-01', '1899-02-28', 'S66; S65', None),
    ('PH-US-SDAK', 'PH-US-2-2', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-COL', 'PH-US-2-2', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-KANS', 'PH-US-2-1', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-MONT', 'PH-US-2-1', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-PENN', 'PH-US-2-1', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-3ART', 'PH-US-2-1', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-UTAH', 'PH-US-2DIV', None, '1899-01-01', '1899-02-28', 'S66', None),
    ('PH-US-TENN', 'PH-US-PROV', None, '1899-01-01', '1899-02-28', 'S66; S65', 'Lent to MacArthur in the morning of 5 Feb (S65).'),
    ('PH-US-TENN2', 'PH-US-PROV', None, '1899-01-01', '1899-02-28', 'S65', 'Lent to Anderson in the afternoon of 5 Feb (S65).'),
    ('PH-PH-MNL', None, 'Gen. Artemio Ricarte (August 1898)', '1898-08-01', '1898-09-30', 'S67', 'Dated by Taylor to August 1898. Not shown for February 1899.'),
    ('PH-PH-Z3', 'PH-PH-MNL', 'Col. Luciano San Miguel', '1898-08-15', '1899-02-04', 'S67', 'Taylor names San Miguel as chief of the 3rd zone (Aug 1898) and puts the outbreak of 4 Feb in this zone; the dates of his command are not given.'),
    ('PH-PH-Z4', 'PH-PH-MNL', 'Lt. Col. Pilar (Aug 1898); Pantaleon Garcia (Aug 1898)', '1898-08-01', '1898-09-30', 'S67', 'Dated by Taylor to August 1898.'),
    ('PH-PH-SOUTH', 'PH-PH-MNL', 'Gen. Mariano Noriel (July-Aug 1898)', '1898-07-15', '1898-09-30', 'S67', 'Dated by Taylor to July-August 1898.'),
    ('PH-PH-SPM', 'PH-PH-MNL', 'Gen. Pio del Pilar (Aug 1898)', '1898-08-01', '1898-09-30', 'S67', 'Dated by Taylor to August 1898.'),
]
AH = ['unit_id', 'parent_unit_id', 'commander', 'valid_from', 'valid_to', 'source_ids', 'notes']
na = [0]
existing = [r[0].value for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value]
base_n = max(int(str(i)[1:]) for i in existing if str(i)[1:].isdigit())
for a in A:
    base_n += 1; v = dict(zip(AH, a)); v['assign_id'] = 'A%03d' % base_n; add('Assignments', v)

# ---------------------------------------------------------------- positions
D4, D5 = '1899-02-04 ', '1899-02-05 '
pos_ids = [r[0].value for r in wb['Positions'].iter_rows(min_row=2) if r[0].value]
PN = [0]
ROWS = {}
MAPB = 'Read from the full-resolution LoC scan of S64 (pixel grid over crops), fitted to the ground by pipeline/georef/manila_georef.py (affine, 9 points, RMS 171 m).'


def pos(key, unit, start, end, show, act, place, geo, src, wording, method='stated', conf='medium', cconf='medium', how='map_read', prec=250, basis=MAPB,
        tb='', notes='', line=None, battle='PHW-MNL', xy=None):
    """geo: ('px', x, y) | ('ll', lat, lon) | None (not placed). line: second end, same form."""
    PN[0] += 1; pid = 'M%02d' % PN[0]; ROWS[key] = pid
    if geo is None: la = lo = None; how = 'none'; prec = None; cconf = None; basis = 'Not placed: the sources read do not say where the unit was.'
    elif geo[0] == 'px': la, lo = px(geo[1], geo[2])
    else: la, lo = geo[1], geo[2]
    le = (None, None)
    if line: le = px(line[1], line[2]) if line[0] == 'px' else (line[1], line[2])
    v = {'pos_id': pid, 'campaign_id': 'PHW-LUZ99', 'battle_id': battle, 'unit_id': unit, 'start_earliest': start[0], 'start_latest': start[1],
         'end_earliest': end[0], 'end_latest': end[1], 'time_basis': tb, 'activity': act, 'place_description': place, 'geometry': 'line' if line else 'point',
         'lat': la, 'lon': lo, 'line_end_lat': le[0], 'line_end_lon': le[1], 'coord_source': how, 'coord_precision_m': prec, 'coordinate_basis': basis,
         'coordinate_confidence': cconf, 'source_ids': src, 'source_wording': wording, 'position_method': method, 'overall_confidence': conf,
         'notes': notes or None, 'review_status': 'Needs review', 'show_from': show[0], 'show_to': show[1], 'changed in v8': 'New, 20 Nov 2026 (Manila pilot).'}
    if geo and geo[0] == 'px':
        v['map_id'] = 'warking-1899'
    r = add('Positions', v, like=last_row(wb['Positions']))
    P = wb['Positions']; ph = head(P)
    P.cell(r, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % r
    P.cell(r, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=16/"&O%d&"/"&P%d,"Open map"))' % (r, r, r, r, r)
    return pid


WD = 'Wikidata coordinates (S73) of a place the report names; the unit was at or about it, not on the exact spot.'
T0, T1 = D4 + '18:00', D5 + '20:00'
PRE = (D4 + '18:00', D4 + '20:30')
TB_PRE = 'Before the first shot (20:30, 4 Feb: S65 p. 161). The map title says these are positions "prior to the battle of February 5th".'
# --- American positions before the battle ("Former ... outpost" labels on S64)
pos('neb0', 'PH-US-NEB', PRE, (D4 + '20:30', D5 + '06:00'), (T0, D5 + '05:00'), 'Outpost line at Santa Mesa', 'Santa Mesa, east of the city boundary',
    ('px', 4560, 1710), 'S64; S65', 'Map label: "Former Nebraska Outpost". S65: "the insurgent troops near Santa Mesa opened a spirited fire on our troops there stationed"', tb=TB_PRE)
pos('col0', 'PH-US-COL', PRE, (D4 + '20:30', D5 + '06:00'), (T0, D5 + '06:00'), 'Outpost', 'South of Blockhouse 5, on the road to Santa Mesa',
    ('px', 3870, 2360), 'S64', 'Map label: "Former Colo. Outpost"', tb=TB_PRE)
pos('penn0', 'PH-US-PENN', PRE, (D4 + '20:30', D5 + '08:00'), (T0, D5 + '08:00'), 'Outpost', 'On the road east of San Lazaro, below La Loma',
    ('px', 3450, 3015), 'S64', 'Map label: "Former Outpost ... 10th Penna" (the word between is not legible)', tb=TB_PRE, cconf='medium')
pos('art0', 'PH-US-3ART', PRE, (D4 + '20:30', D5 + '12:00'), (T0, D5 + '12:00'), 'Outpost', 'Tondo, at the Canal de la Reyna',
    ('px', 3560, 3630), 'S64', 'Map label: "Former 3rd Arty outpost (Later 20th Kans)"', tb=TB_PRE)
pos('king0', 'PH-US-1-1', PRE, (D4 + '20:30', D5 + '07:45'), (T0, D5 + '07:45'), 'Holding the line, under orders not to attack until told (from midnight)',
    'From the Pasig at Santa Ana south to Blockhouse 12', ('px', 5130, 1880), 'S65; S64',
    'S65 p. 164: "General King had asked to swing his brigade (the left of which rested on the Pasig near Santa Ana) to the left"; p. 162: Anderson was "directed to hold them in readiness to receive a morning attack, but not to attack until further instructed."',
    method='inferred', conf='low', cconf='low', prec=500, line=('px', 5410, 2380),
    basis='The left end is stated (the Pasig near Santa Ana); the line is drawn from there along the blockhouse line on S64 to Blockhouse 12. Where King\'s right ended is not stated.',
    tb=TB_PRE)
pos('oven0', 'PH-US-1-2', PRE, (D4 + '20:30', D5 + '15:30'), (T0, D5 + '15:30'), 'Holding the line, under orders not to attack until told (from midnight); back on it in the afternoon',
    'From Blockhouse 12 past Blockhouses 13 and 14 to the beach at Malate fort', ('px', 5410, 2380), 'S65; S64',
    'S65 p. 162: "General Anderson, who commanded all troops south of the Pasig, consisting of King\'s and Ovenshine\'s brigades"; p. 164: "the right of Anderson\'s line".',
    method='inferred', conf='low', cconf='low', prec=500, line=('px', 5950, 2880),
    basis='Drawn along the blockhouse line on S64 from Blockhouse 12 to Malate fort on the beach. The sources read give no line for this brigade before the battle.', tb=TB_PRE,
    notes='S65 p. 165: in the afternoon Ovenshine\'s troops "on the right of the line had returned to the original position of the morning, fearing the shells from the guns of the Monadnock". So the brigade is kept on this line until it swings left late in the afternoon.')
# --- 5 February: the north (MacArthur)
pos('neb1', 'PH-US-NEB', (D5 + '05:00', D5 + '09:00'), ('unknown', 'unknown'), (D5 + '06:00', D5 + '09:30'), 'Attacked and took Blockhouses 6 and 7 (6 burned)',
    'Blockhouse 7, Santa Mesa', ('px', 4080, 1680), 'S65; S64', 'S65 p. 162: Stotsenburg "had attacked early in the morning, drove the enemy from the blockhouses in his front"; telegram: "Stotsenburg reports he has captured blockhouses 6 and 7 - burned 6."',
    tb='"Early in the morning" (S65). No clock time.', prec=150, conf='medium')
pos('ten1', 'PH-US-TENN', (D5 + '08:00', D5 + '10:00'), ('unknown', 'unknown'), (D5 + '09:30', D5 + '11:00'), 'Sent to fill the gap on Stotsenburg\'s left',
    'Beside the 1st Nebraska, Santa Mesa', ('px', 3980, 1760), 'S65', 'S65 p. 162: "He had called for troops to fill gap on Stotsenburg\'s left and a battalion of the 1st Tennessee regiment of the Provost Guard under the command of its colonel was sent him"',
    method='inferred', conf='low', cconf='low', prec=400, basis='Placed just west of Blockhouse 7, "on Stotsenburg\'s left". No position given.', tb='Morning of 5 Feb (S65). No clock time.')
pos('neb2', 'PH-US-NEB', (D5 + '11:20', D5 + '11:20'), ('unknown', 'unknown'), (D5 + '11:20', D5 + '11:50'), 'Crossing the San Juan River at the bridge',
    'San Juan bridge, on the road from Santa Mesa to San Juan del Monte', ('px', 4285, 1540), 'S65; S64',
    'S65 p. 163 (MacArthur\'s telegram): "At 11:20 a. m. Stotsenburg is crossing San Juan River at the bridge"', tb='Telegram time, 11:20 (S65).', conf='high', cconf='medium', prec=150)
pos('ten2', 'PH-US-TENN', (D5 + '11:00', D5 + '13:00'), ('unknown', 'unknown'), (D5 + '12:00', T1), 'With the Nebraskans at the powder magazine',
    'Almacen de Polvora (powder magazine), San Juan', ('ll', 14.60572, 121.02245), 'S65; S73',
    'S65 p. 163: "The Nebraska regiment and Tennessee battalion advanced rapidly during the morning and captured the powder house and Deposito"',
    how='modern_map', basis=WD, prec=200, tb='"During the morning" (S65); placed after the 11:20 crossing.', conf='medium')
pos('neb3', 'PH-US-NEB', (D5 + '12:00', D5 + '13:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '12:30', T1), 'Holding the water reservoir (El Deposito) and San Juan del Monte',
    'El Deposito, San Juan del Monte', ('ll', 14.60421, 121.03176), 'S65; S73; S64',
    'S65 p. 163: "captured the powder house and Deposito"; p. 167 (Otis to Dewey, close of the day): "On the north we hold the water reservoir, San Juan del Monte, and all blockhouses."',
    how='modern_map', basis=WD, prec=250, tb='"During the morning" (S65), after the 11:20 crossing; held at the close of the day.', conf='medium',
    notes='S64\'s index gives the final position of the 1st Nebraska as "Waterworks"; Otis wrote "Waterworks must wait" on the morning of the 5th and took the pumping station later.')
pos('sdak1', 'PH-US-SDAK', (D5 + '08:00', D5 + '12:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '11:00', T1), 'Drove the enemy from their entrenchments as far west as the Lico road; line beyond Blockhouse 4',
    'Along the city boundary between the Lico road and Blockhouse 5', ('px', 3140, 2740), 'S65; S64',
    'S65 p. 163: "the South Dakota regiment on the left drove the enemy from all their intrenchments as far to the westward as the Lico road"; map label "1st So. Dakota"; index: "Beyond Blockhouse No 4".',
    line=('px', 3485, 2320), tb='Morning of 5 Feb (S65). The map line is its final position (after 10 Feb); shown here from late morning.', conf='medium')
pos('col1', 'PH-US-COL', (D5 + '06:00', D5 + '12:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '09:00', T1), 'Line near Blockhouses 5 and 6',
    'Along the city boundary from below Blockhouse 5 to Blockhouse 6', ('px', 3550, 2300), 'S64',
    'Map label "1st Colorado"; index: "Near Blockhouses 5 and 6."', line=('px', 3870, 1830), method='inferred',
    tb='Not timed in the sources read. The map line is its final position (after 10 Feb); shown from mid-morning because Otis says MacArthur pressed back the enemy "in his entire front" that morning.', conf='low')
pos('penn1', 'PH-US-PENN', (D5 + '12:00', D5 + '17:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '14:00', T1), 'Line at La Loma, by the Chinese Hospital',
    'La Loma, west of the Chinese Hospital', ('px', 2975, 2900), 'S64; S65',
    'Map label "10th Pennsylvania"; index: "Vicinity of La Loma". S65 p. 163 (MacArthur): "try and occupy Chinese Hospital and extend the line to the left from that point"; "This line was established during the afternoon".',
    line=('px', 3305, 2795), method='inferred', tb='Afternoon of 5 Feb (S65), for the line; the regiment\'s part in it is the map\'s final position.', conf='low')
pos('utah1', 'PH-US-UTAH', (D5 + '12:00', D5 + '17:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '14:00', T1), 'Two guns at La Loma',
    'La Loma, by the cemetery', ('px', 2850, 2840), 'S64', 'Map label: "Utah Light Arty. 2 guns"; index: "La Loma and Caloocan"', method='inferred', conf='low',
    tb='As the 10th Pennsylvania.')
pos('hgo1', 'PH-US-2-1', (D5 + '12:00', D5 + '17:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '14:00', T1), 'Line from the Chinese Hospital to the coast',
    'From the Chinese Hospital to the shore at Tondo', ('px', 3190, 2850), 'S65; S64',
    'S65 p. 163 (Otis to MacArthur, about noon): "Think line you suggest from coast to Chinese Hospital your proper one"; "This line was established during the afternoon".',
    line=('px', 3560, 3630), method='inferred', cconf='low', prec=500, conf='low',
    basis='The two ends are stated (the Chinese Hospital; "the coast"); the coast end is put at the Tondo outpost on S64. Which regiment held which part is not in the sources read.',
    tb='Afternoon of 5 Feb (S65).')
# --- 5 February: the south (Anderson)
pos('king1', 'PH-US-1-1', (D5 + '07:45', D5 + '12:30'), (D5 + '12:30', D5 + '17:00'), (D5 + '12:30', D5 + '17:00'), 'Swung left to the Pasig; took Santa Ana',
    'Santa Ana', ('px', 5150, 1770), 'S65', 'S65 p. 165 (Anderson, Battery Knoll, 12:30 p.m.): "King has taken Santa Ana. 200 prisoners."', tb='Telegram sent 12:30 (S65); the attack was allowed from 7:45 (S65 p. 163).',
    conf='high', cconf='medium', prec=250)
pos('cal1', 'PH-US-CAL', (D5 + '12:00', D5 + '12:30'), (D5 + '17:00', D5 + '20:00'), (D5 + '12:30', D5 + '18:00'), 'Two battalions entering San Pedro Macati',
    'San Pedro Macati', ('ll', 14.5659, 121.03137), 'S65; S73',
    'S65 p. 165 (Anderson, 12:30): "Last seen of Smith (Colonel of California regiment meaning) was advancing on the right with two battalions and entering San Pedro Macati."',
    how='modern_map', basis=WD + ' (San Pedro Macati church)', prec=300, tb='Telegram sent 12:30 (S65).', conf='medium',
    notes='Smith did not stop: on 6 Feb Otis found he had gone on up the Pasig to Pasig, Pateros or Taguig (S65 p. 167). The index of S64 gives "Near San Pedro Macati" as the final position.')
pos('wash1', 'PH-US-WASH', (D5 + '07:45', D5 + '12:30'), (D5 + '12:30', D5 + '16:45'), (D5 + '12:30', D5 + '16:45'), 'With King\'s brigade in the swing to the Pasig at Santa Ana',
    'Between Santa Ana and the Pasig', ('px', 5250, 1700), 'S65', 'S65 p. 164: "the Californias, Washingtons and Idahos responding with great vigor, the movement was attended with signal success."',
    method='inferred', cconf='low', prec=500, conf='low', basis='Placed beside Santa Ana; the report names the regiment in the movement but not its place in it.', tb='As King\'s brigade.')
pos('ida1', 'PH-US-IDA', (D5 + '07:45', D5 + '12:30'), (D5 + '12:30', D5 + '16:45'), (D5 + '12:30', D5 + '16:45'), 'With King\'s brigade in the swing to the Pasig at Santa Ana',
    'South of Santa Ana', ('px', 5250, 1900), 'S65', 'S65 p. 164: "the Californias, Washingtons and Idahos responding with great vigor"',
    method='inferred', cconf='low', prec=500, conf='low', basis='Placed beside Santa Ana; the report names the regiment in the movement but not its place in it.', tb='As King\'s brigade.')
pos('14a', 'PH-US-14INF', (D5 + '07:45', D5 + '12:30'), (D5 + '15:00', D5 + '16:30'), (D5 + '09:00', D5 + '16:00'), 'Part of the regiment under Capt. Murphy pressing the entrenchments in the jungle at the centre; advanced to Blockhouse 14',
    'Blockhouse 14', ('px', 5810, 2520), 'S65; S64', 'S65 p. 164: "This position was pressed by a portion of the 14th Infantry under Captain Murphy and Wheeler\'s troop of the 4th Cavalry"; p. 165 (Anderson, 12:30): "Captain Murphy said to have advanced to blockhouse 14, but insurgents still hold flanking position on his right."',
    tb='Morning to afternoon of 5 Feb; at Blockhouse 14 by 12:30 (S65).', conf='medium', prec=200)
pos('cav1', 'PH-US-4CAV', (D5 + '07:45', D5 + '12:30'), (D5 + '15:00', D5 + '16:30'), (D5 + '09:00', D5 + '16:00'), 'Wheeler\'s troop with Murphy\'s men in the jungle at the centre',
    'Beside Blockhouse 14', ('px', 5760, 2600), 'S65', 'S65 p. 164: "Wheeler\'s troop of the 4th Cavalry, which advanced slowly, shooting the insurgents in their formidable intrenchments"',
    method='inferred', cconf='low', prec=400, conf='low', basis='Placed beside the 14th Infantry at Blockhouse 14; one troop only.', tb='As the 14th Infantry.')
TBE = 'Otis to Anderson at 4:45 p.m. (S65 p. 166) has them on the Pasay road; Barry\'s telegram of about 4:30 says Ovenshine has taken Pasay.'
pos('14b', 'PH-US-14INF', (D5 + '16:00', D5 + '16:45'), (D5 + '20:00', D5 + '20:00'), (D5 + '16:30', T1), 'On the Pasay road; east of and in Pasay',
    'Pasay road, running into Pasay', ('px', 6830, 1720), 'S65; S64', 'S65 p. 166: "First North Dakota, 14th Infantry and 4th Cavalry on Pasay road."; S64 index: "East of and in Pasay"; map label "14th U.S. Infty".',
    line=('px', 7040, 2120), tb=TBE, conf='medium')
pos('ndak1', 'PH-US-NDAK', (D5 + '16:00', D5 + '16:45'), (D5 + '20:00', D5 + '20:00'), (D5 + '16:30', T1), 'On the Pasay road',
    'Pasay road, north-east of the 14th Infantry', ('px', 6500, 1580), 'S65; S64', 'S65 p. 166: "First North Dakota, 14th Infantry and 4th Cavalry on Pasay road."; map label "1st N. Dakota"; index: "Between 51st Iowa and 14th U S Infty".',
    line=('px', 6820, 1700), tb=TBE, conf='medium', notes='The 51st Iowa beside it on S64 came up after 5 Feb; it is not in this playback.')
pos('cav2', 'PH-US-4CAV', (D5 + '16:00', D5 + '16:45'), (D5 + '20:00', D5 + '20:00'), (D5 + '16:30', T1), 'Between Pasay and the beach',
    'West of Pasay, towards the beach', ('px', 7060, 2260), 'S65; S64', 'S65 p. 166: "...4th Cavalry on Pasay road."; S64 index: "Between Pasay and Beach".',
    method='inferred', cconf='low', prec=400, conf='medium', basis='Placed just west of Pasay town on S64; the stretch to the beach was not read.', tb=TBE)
pos('mtn1', 'PH-US-MTNBTY', (D5 + '16:00', D5 + '17:00'), (D5 + '20:00', D5 + '20:00'), (D5 + '16:30', T1), 'On the road from Pasay to San Pedro Macati',
    'Pasay road', ('px', 6700, 1610), 'S64', 'Map label "Mountain Battery"; index: "Road from Pasay to S. Pedro Macati".', method='inferred', conf='low',
    tb='Final position on S64 (after 10 Feb); shown from the evening of 5 Feb, when the Pasay road became the line.')
TBK = 'S65 p. 166 (4:45 p.m.): "King must fall out and take position on that road to-night." Final positions from the S64 index.'
pos('cal2', 'PH-US-CAL', (D5 + '17:00', D5 + '20:00'), ('1899-02-06 00:00', '1899-02-06 12:00'), (D5 + '19:00', T1), 'On the Pasay road near San Pedro Macati (the battalions that did not go on up the Pasig)',
    'Pasay road near San Pedro Macati', ('px', 5990, 1290), 'S65; S64', 'Map label "Calif. Battn"; index: "Near San Pedro Macati".', line=('px', 6150, 1470), method='inferred', conf='low', tb=TBK,
    notes='Two battalions went on up the Pasig with Smith (S65 p. 167). This row is the regiment\'s place on the new line.')
pos('ida2', 'PH-US-IDA', (D5 + '17:00', D5 + '20:00'), ('1899-02-06 00:00', '1899-02-06 12:00'), (D5 + '18:30', T1), 'On the Pasay road',
    'Pasay road between Pasay and San Pedro Macati', ('px', 6150, 1470), 'S65; S64', 'Map label "1st Idaho"; index: "Between Pasay and S. Pedro Macati".', line=('px', 6300, 1530), method='inferred', conf='low', tb=TBK)
pos('wash2', 'PH-US-WASH', (D5 + '17:00', D5 + '20:00'), ('1899-02-06 00:00', '1899-02-06 12:00'), (D5 + '18:30', T1), 'At San Pedro Macati',
    'San Pedro Macati', ('ll', 14.5659, 121.03137), 'S65; S64; S73', 'S64 index: "San Pedro Macati". S65 p. 166: "King must fall out and take position on that road to-night."',
    how='modern_map', basis=WD + ' (San Pedro Macati church)', prec=300, method='inferred', conf='low', tb=TBK)
pos('king2', 'PH-US-1-1', (D5 + '17:00', D5 + '20:00'), ('1899-02-06 00:00', '1899-02-06 12:00'), (D5 + '18:30', T1), 'Fallen out of Santa Ana to the Pasay road for the night',
    'Pasay road, San Pedro Macati end', ('px', 5990, 1290), 'S65', 'S65 p. 166: "King must fall out and take position on that road to-night. That will be your permanent line."',
    line=('px', 6300, 1530), method='inferred', conf='medium', tb=TBK)
pos('oven1', 'PH-US-1-2', (D5 + '16:00', D5 + '16:30'), (D5 + '20:00', D5 + '20:00'), (D5 + '16:30', T1), 'Took Pasay without resistance; line on the Pasay road',
    'Pasay road, Pasay end', ('px', 6500, 1580), 'S65', 'S65 p. 165-166 (Barry, 4:30): "Word has just been received that Ovenshine has taken Pasay without resistance."; "placed his entire line firmly on the Pasay road".',
    line=('px', 7040, 2120), tb='Telegram of about 4:30 p.m. (S65; the time is blurred in the scan).', conf='medium')
pos('ten3', 'PH-US-TENN2', (D5 + '14:00', D5 + '16:00'), (D5 + '17:00', D5 + '20:00'), (D5 + '14:00', T1), 'Second battalion sent to the centre of Anderson\'s line, arriving after the ground was carried',
    'Centre of Anderson\'s line, near Blockhouse 14', ('px', 5700, 2450), 'S65',
    'S65 p. 165: "Another battalion of the Tennessee regiment was borrowed from the Provost Marshal and was conducted by my Aid, Captain Sanders, to the center of this line but did not arrive until the ground had been carried."',
    method='inferred', cconf='low', prec=500, conf='low', basis='Placed at the centre of the southern line, by Blockhouse 14.', tb='Afternoon of 5 Feb (S65). No clock time.',
    notes='A second battalion, drawn as its own symbol; it appears when it reaches the line.')
# --- Filipino positions (inferred; only places the American reports or the map name)
TBF = 'Night of 4 Feb (S65). Who held this ground is from Taylor\'s notes, which date the commands to August-September 1898 (S67).'
pos('z3a', 'PH-PH-Z3', (D4 + '20:30', D4 + '20:30'), ('unknown', 'unknown'), (T0, D5 + '09:30'), 'Lines facing the American outposts; opened fire after the picket\'s shot; driven from the blockhouses next morning (not followed after)',
    'East of Santa Mesa, in front of Blockhouses 6 and 7', ('px', 4450, 1500), 'S65; S67',
    'S65 p. 161: "the insurgent troops near Santa Mesa opened a spirited fire on our troops there stationed"; S67: "Col. San Miguel. It was in this zone that outbreak of February 4 occurred."',
    method='inferred', cconf='low', prec=600, conf='low', basis='Placed between the Nebraska outpost and the San Juan River, "near Santa Mesa". Their lines are not drawn on S64 as read.', tb=TBF)
pos('z4a', 'PH-PH-Z4', (D4 + '20:30', D4 + '20:30'), ('unknown', 'unknown'), (T0, T1), 'At Caloocan; reinforced by rail through the night and the morning',
    'Caloocan', ('px', 2154, 3434), 'S65; S67', 'S65 p. 161: "a few straggling shots on the extreme left in the direction of Caloocan"; p. 163: "Reported that insurgent troops were arriving all night and this morning for service in your front"; the railway "forwarding to Caloocan its troops from the north".',
    method='inferred', cconf='low', prec=800, conf='low', basis='At Caloocan church on S64; the extent of their lines is not in the sources read.', tb=TBF)
pos('sa1', 'PH-PH-SAGUNS', (D4 + '20:30', D4 + '20:30'), ('unknown', 'unknown'), (T0, D5 + '12:30'), 'Two Krupp guns at Santa Ana',
    'West of Santa Ana, by the road', ('px', 5000, 1790), 'S64; S65', 'Map label: "2 Krupp Guns of Insurgents"; S65 p. 167: "two Krupp guns captured".', conf='medium', cconf='medium', prec=150,
    tb='The map marks them; when they came is not stated. Shown until King took Santa Ana (12:30, 5 Feb).')
pos('sa2', 'PH-PH-SPM', (D4 + '20:30', D4 + '20:30'), ('unknown', 'unknown'), (T0, D5 + '11:45'), 'At San Pedro Macati (not followed after the Californians entered it)',
    'San Pedro Macati', ('ll', 14.5659, 121.03137), 'S67; S65', 'S67: Pio del Pilar at San Pedro Macati, Aug 1898; his command "extended to meet that of Noriel, at Pineda". S65 p. 165: Smith "entering San Pedro Macati" at 12:30.',
    how='modern_map', basis=WD, method='inferred', cconf='low', prec=800, conf='low', tb=TBF)
pos('so1', 'PH-PH-SOUTH', (D4 + '20:30', D4 + '20:30'), ('unknown', 'unknown'), (T0, D5 + '15:15'), 'Entrenched in the jungle and swamp facing the centre and right of Anderson\'s line',
    'Between Singalong and Pasay, in front of Blockhouses 13 and 14', ('px', 6000, 2350), 'S65; S67',
    'S65 p. 164: "at the center in the jungle and swamp they held on with great tenacity"; Taylor (S67): Noriel "in command of insurgents south of Manila" (1898).',
    method='inferred', cconf='low', prec=800, conf='low', basis='Placed in front of Blockhouses 13 and 14; the extent is not in the sources read.', tb=TBF)
pos('so2', 'PH-PH-SOUTH', (D5 + '15:30', D5 + '16:30'), ('unknown', 'unknown'), (D5 + '15:30', D5 + '17:00'), 'Driven out in a sharp fight when Ovenshine swung left; Pasay left without resistance (not followed after)',
    'East of Pasay', ('px', 7300, 2000), 'S65', 'S65 p. 166 (Barry): "Insurgents driven out in sharp fight when General Ovenshine advanced toward Pasay."',
    method='inferred', cconf='low', prec=1000, conf='low', basis='Where they went is not stated; placed beyond Pasay.', tb='About 4:30 p.m., 5 Feb (S65).')

# ---------------------------------------------------------------- tracks
TR = [('PH-US-NEB', ['neb0', 'neb1', 'neb2', 'neb3'], None), ('PH-US-COL', ['col0', 'col1'], None), ('PH-US-PENN', ['penn0', 'penn1'], None),
      ('PH-US-3ART', ['art0'], 'PH-US-2-1'), ('PH-US-SDAK', ['sdak1'], None), ('PH-US-UTAH', ['utah1'], None), ('PH-US-2-1', ['hgo1'], None),
      ('PH-US-TENN', ['ten1', 'ten2'], None), ('PH-US-TENN2', ['ten3'], None), ('PH-US-1-1', ['king0', 'king1', 'king2'], None), ('PH-US-1-2', ['oven0', 'oven1'], None),
      ('PH-US-CAL', ['cal1', 'cal2'], None), ('PH-US-WASH', ['wash1', 'wash2'], None), ('PH-US-IDA', ['ida1', 'ida2'], None),
      ('PH-US-14INF', ['14a', '14b'], None), ('PH-US-4CAV', ['cav1', 'cav2'], None), ('PH-US-NDAK', ['ndak1'], None), ('PH-US-MTNBTY', ['mtn1'], None),
      ('PH-PH-Z3', ['z3a'], None), ('PH-PH-Z4', ['z4a'], None), ('PH-PH-SAGUNS', ['sa1'], None), ('PH-PH-SPM', ['sa2'], None), ('PH-PH-SOUTH', ['so1', 'so2'], None)]
ECH = {u[0]: u[5].lower() for u in UNITS}
for uid, keys, part in TR:
    add('Tracks', {'playback_id': 'manila', 'track_id': uid, 'unit_id': uid, 'rows': '; '.join(ROWS[k] for k in keys), 'echelon': ECH[uid],
                   'hide_after_last_row': 'yes' if uid.startswith('PH-PH') else None})

# ---------------------------------------------------------------- events
EV = [
    ('ME01', D4 + '20:30', D4 + '20:30', 'First shot at Santa Mesa', 'An American picket of the 1st Nebraska fires on a Filipino soldier who will not halt; the Filipino lines near Santa Mesa open fire. Otis puts the start of the battle at half past eight.',
     'neb0; z3a', 'S65', 'First shot', 'A Nebraska picket near Santa Mesa fires on a Filipino soldier who will not halt, and the lines open fire. The battle begins at 20:30.'),
    ('ME02', D5 + '00:00', D5 + '04:00', 'Firing along the north front through the night', 'An exchange of fire from the Pasig to the Lico road, about two miles, with occasional shots at Paco and towards Caloocan. Heavy firing at midnight and at 4 a.m. Anderson is told at midnight to hold, not attack.',
     'king0; oven0', 'S65', 'Night firing', 'Fire is exchanged along the north front from the Pasig to the Lico road; heavy at midnight and at 04:00. South of the Pasig, Anderson is told to hold and not attack.'),
    ('ME03', D5 + '05:00', D5 + '09:00', 'Stotsenburg takes Blockhouses 6 and 7', 'The 1st Nebraska attacks early in the morning and drives the Filipinos from the blockhouses in its front.',
     'neb1', 'S65', 'Blockhouses 6 and 7', 'The 1st Nebraska attacks at first light and takes Blockhouses 6 and 7.'),
    ('ME04', D5 + '07:45', D5 + '07:45', 'Anderson allowed to attack', 'Permission for the First Division to attack is given at 7:45 a.m., with a caution to watch its flanks and the monitor Monadnock\'s fire.',
     'king1; 14a', 'S65', 'South attacks', 'Anderson\'s division south of the Pasig is allowed to attack. King swings his brigade left towards the Pasig.'),
    ('ME05', D5 + '11:20', D5 + '11:20', 'Nebraskans cross the San Juan bridge', 'MacArthur reports Stotsenburg crossing the San Juan River at the bridge at 11:20; the Nebraskans and a Tennessee battalion take the powder magazine and the reservoir (El Deposito).',
     'neb2; ten2; neb3', 'S65', 'San Juan bridge', 'The Nebraskans cross the San Juan River at the bridge and take the powder magazine and the reservoir, El Deposito.'),
    ('ME06', D5 + '12:30', D5 + '12:30', 'King takes Santa Ana', 'Anderson reports from Battery Knoll at 12:30 that King has taken Santa Ana with 200 prisoners; Filipinos trying to cross the Pasig are drowned. Colonel Smith\'s Californians are entering San Pedro Macati.',
     'king1; cal1; sa1', 'S65', 'Santa Ana', 'King\'s brigade takes Santa Ana; many Filipinos drown trying to cross the Pasig. The Californians enter San Pedro Macati.'),
    ('ME07', D5 + '16:30', D5 + '16:30', 'Ovenshine takes Pasay', 'Ovenshine swings part of his line left, routs the Filipinos in front of Murphy and places his line on the Pasay road; Pasay is taken without resistance.',
     'oven1; 14b; so2', 'S65', 'Pasay', 'Ovenshine swings left, clears the ground in front of the centre and takes Pasay without resistance.'),
    ('ME08', D5 + '17:00', D5 + '17:00', 'Close of the day', 'The new line: on the south the road from Pasay to San Pedro Macati; on the north the reservoir, San Juan del Monte and all the blockhouses, and MacArthur\'s line from opposite San Pedro Macati to the bay.',
     'neb3; hgo1; king2; ndak1', 'S65', 'Evening line', 'The battle ends about 17:00. The Americans hold the road from Pasay to San Pedro Macati in the south, and the reservoir, San Juan del Monte and the blockhouses in the north.'),
]
for eid, a, b, name, summ, pids, src, lab, txt in EV:
    add('Events', {'event_id': eid, 'campaign_id': 'PHW-LUZ99', 'battle_id': 'PHW-MNL', 'time_earliest': a, 'time_latest': b, 'name': name, 'summary': summ,
                   'pos_ids': '; '.join(ROWS[k] for k in pids.split('; ')), 'source_ids': src, 'timeline': 'name', 'playback_at': b, 'playback_label': lab, 'playback_text': txt})

# ---------------------------------------------------------------- labels (places named in the reports, on the fitted map)
LAB = [('Santa Mesa', ('px', 4250, 1770), 'town'), ('Santa Ana', ('px', 5150, 1770), 'town'), ('San Juan del Monte', ('px', 4300, 934), 'town'),
       ('Caloocan', ('px', 2154, 3434), 'town'), ('Pasay', ('px', 7070, 2200), 'town'), ('San Pedro Macati', ('ll', 14.5659, 121.03137), 'town'),
       ('La Loma', ('px', 2920, 3033), 'town'), ('Paco', ('px', 5250, 2500), 'town'), ('Malate', ('px', 5500, 2975), 'town'), ('Tondo', ('px', 3800, 3700), 'town'),
       ('Walled City', ('px', 4800, 3420), 'town'), ('Blockhouse 6', ('px', 3900, 1790), 'landmark'), ('Blockhouse 7', ('px', 4080, 1680), 'landmark'),
       ('Blockhouse 5', ('px', 3710, 2090), 'landmark'), ('Blockhouse 14', ('px', 5810, 2520), 'landmark'), ('Chinese Hospital', ('px', 3190, 2850), 'landmark'),
       ('Powder magazine', ('ll', 14.60572, 121.02245), 'landmark'), ('El Deposito (reservoir)', ('ll', 14.60421, 121.03176), 'landmark'),
       ('San Juan bridge', ('px', 4285, 1540), 'landmark')]
for text, g, kind in LAB:
    la, lo = px(g[1], g[2]) if g[0] == 'px' else (g[1], g[2])
    add('Labels', {'playback_id': 'manila', 'text': text, 'lat': la, 'lon': lo, 'kind': kind, 'show': 'both', 'approximate': 'yes' if g[0] == 'px' else None})

# ---------------------------------------------------------------- the map
c = G.corners(); res = G.residuals(); import math
rms = round(math.sqrt(sum(d * d for _, d in res) / len(res)))
import json
add('Maps', {'playback_id': 'manila', 'map_id': 'warking-1899', 'title': 'Warking, Map of Manila and vicinity showing positions of troops prior to the battle of February 5th (Signal Corps, 1899)',
             'short': '1899 map', 'label': 'Signal Corps map, Feb 1899', 'credit': 'Warking, Signal Corps, 1899 · Library of Congress', 'source_id': 'S64', 'fitted_to_ground': 'yes',
             'file': 'warking-1899.webp', 'tl_lat': round(float(c[0][0]), 6), 'tl_lon': round(float(c[0][1]), 6), 'tr_lat': round(float(c[1][0]), 6), 'tr_lon': round(float(c[1][1]), 6),
             'br_lat': round(float(c[2][0]), 6), 'br_lon': round(float(c[2][1]), 6), 'bl_lat': round(float(c[3][0]), 6), 'bl_lon': round(float(c[3][1]), 6),
             'fit': json.dumps({'method': 'affine (shift, turn, scale, shear) by least squares on 9 places that still stand', 'points': len(res), 'rms_m': rms,
                                'max_m': max(d for _, d in res), 'm_per_px': 2.6, 'script': 'pipeline/georef/manila_georef.py'}),
             'scale_note': 'Scale 1:25,000 on the sheet; the scan is a reduced photocopy, about 2.6 m per pixel.', 'approx_m_per_px': 2.6,
             'note': 'A blue-line photocopy drawn with north to the left; shown turned to north-up. Fitted to the ground on nine places that still stand (churches, the Walled City\'s south bastion, Paco cemetery, Malacanang): places on it fall within about 170 m of where they are, at worst 270 m. "Former ... outpost" labels are positions before the battle; the heavy double-dashed lines named for regiments are their final positions, after the capture of Caloocan on 10 Feb.',
             'iiif_service': 'https://tile.loc.gov/image-services/iiif/service:gmd:gmd8:g8064:g8064m:ct002453', 'iiif_width': 11533, 'iiif_height': 7657, 'iiif_tile': 512,
             'iiif_scale_factors': '[1, 2, 4, 8, 16, 32]', 'iiif_region': '0, 0, 11533, 7657', 'iiif_reduced': round(2884 / 11533, 5)})

# ---------------------------------------------------------------- playback
ext = (120.935, 14.525, 121.045, 14.665)
add('Playbacks', {'playback_id': 'manila', 'battle_file_id': 'manila-1899', 'campaign_id': 'PHW-LUZ99', 'record_battles': 'PHW-MNL',
                  'title': 'Manila, 4-5 February 1899', 'subtitle': 'The first battle of the Philippine War: the Eighth Army Corps against the Army of the Philippine Republic around Manila',
                  'time_unit': 'minute', 'time_zero': '1899-02-04 00:00', 'time_start': T0, 'time_end': T1, 'focus_start': D4 + '20:30', 'focus_end': D5 + '17:00',
                  'calendar_first': '1899-02-04', 'days_numbered': 'no', 'origin_lat': 14.595, 'origin_lon': 121.0,
                  'west': ext[0], 'south': ext[1], 'east': ext[2], 'north': ext[3], 'opening_label': 'Before 20:30',
                  'opening_text': 'Evening of 4 February 1899. The Eighth Army Corps holds a line of blockhouses around Manila, with the Filipino army entrenched facing it. Press play: the first shot is fired at Santa Mesa at 20:30.'})
OTM = {'tiles': 'https://a.tile.opentopomap.org/{z}/{x}/{y}.png', 'max_zoom': 17, 'credit': 'OpenTopoMap (CC-BY-SA); data: OpenStreetMap contributors, SRTM', 'name': 'OpenTopoMap',
       'about': "Today's ground: OpenTopoMap, a topographic map drawn from OpenStreetMap with contours and hill shading from satellite radar heights. Place names on it are today's spellings; the battle's own names are written over it. It is streamed from opentopomap.org while it is on screen, so it needs a connection.",
       'rights': 'Map: CC-BY-SA, OpenTopoMap. Data: Open Database License, OpenStreetMap contributors; SRTM heights', 'link': 'https://opentopomap.org/about'}
S = [('page_title', 'Manila 1899 Playback', 'The browser tab title'), ('style', 'tactical', 'tactical (a battlefield) or operational (a front)'),
     ('scale_bar', 'yards', 'yards or km'), ('rate', 10, 'Time units played per second'), ('clock_title', 'Battle of Manila', "The battle's name in the date box"),
     ('lead.share', 0.12, 'Share of the timeline given to the stretch before the focus'), ('lead.rate', 10, 'Time units per second in that stretch'),
     ('bases.1.id', 'p99', 'A map the reader can put under the units; the first is the opening one'), ('bases.1.label', 'Signal Corps map, Feb 1899', None), ('bases.1.short', '1899', None),
     ('bases.1.map', 'warking-1899', None), ('bases.1.backdrop', 'current', None),
     ('bases.2.id', 'now', None), ('bases.2.label', 'Current map', None), ('bases.2.short', 'Now', None), ('bases.2.current', True, None),
     ('views.1.preset', 'lines', 'Named views'), ('views.1.label', 'The lines around Manila', None), ('views.1.short', 'Lines', None), ('views.2.preset', 'sheet', None), ('views.2.label', 'The whole 1899 map', None), ('views.2.short', 'Map', None), ('preset.lines', '[120.955, 14.528, 121.048, 14.662]', 'A named view: [west, south, east, north]'), ('preset.sheet', '[120.874, 14.429, 121.058, 14.705]', None),
     ('start_base', 'p99', 'The period map covers the whole battle (the landing-view rule)'), ('bounds', 'warking-1899', 'The map that bounds the view')]
S += [('modern.' + k, v, 'The modern map (OpenTopoMap, as Ypres)') for k, v in OTM.items()]
S += [('zoom.max', 1.6, 'Closest zoom, screen pixels per metre'), ('zoom.min_factor', 0.9, None), ('zoom.follow_max', 0.6, None), ('zoom.labels', 0.12, None), ('zoom.towns_until', 0.3, None),
      ('follow.min', '[3000, 2000]', 'Smallest box the camera frames, metres'), ('follow.margin', 300, None),
      ('texts.stated', 'A report or the Signal Corps map puts the unit here.', None),
      ('texts.inferred', 'Worked out from the reports or the order of events; the sources read do not put this unit here.', None),
      ('texts.after', 'The sources read do not follow this unit further. It is shown where they last put it.', None),
      ('texts.unplaced', 'The sources read do not say where the unit was.', None),
      ('found.map_read', 'read from the Signal Corps map of February 1899', None), ('found.modern_map', 'at a place named in the report (its present-day coordinates)', None),
      ('question_mark', 'overall', None),
      ('about.1', 'Data pilot, 20 November 2026. Positions come from Otis\'s report of 1899 (the telegrams and their clock times), the January 1899 roster of the Eighth Army Corps, and the Signal Corps map of February 1899 with its index of final positions. Nothing here has been checked by a historian.', None),
      ('about.2', 'The Filipino side is thin: the sources read are American, and Taylor\'s notes on the Filipino commands around Manila date from August-September 1898. Every Filipino position is inferred, and the commanders named are those of 1898.', None),
      ('about.3', 'Many clock times are ranges: the reports give "early in the morning" or "during the afternoon". Telegram times (11:20, 12:30, about 16:30, 16:45) are exact to the minute.', None),
      ('about.4', 'The 1899 map is a blue-line photocopy drawn with north to the left, shown turned to north-up and fitted to today\'s ground to within about 170 m (at worst 270 m).', None),
      ('about.5', 'Symbols are blue for the Americans and red for the Filipino army; the colours are a drawing convention.', None)]
for k, v, w in S:
    add('Playback settings', {'playback_id': 'manila', 'setting': k, 'value': v, 'what it does': w})

# ---------------------------------------------------------------- conflicts and gaps
add('Conflicts', {'conflict_id': 'C-PW1', 'battle_id': 'PHW-MNL', 'question': 'Which brigade were the Washington, Idaho, 14th Infantry and 4th Cavalry in on 4-5 Feb?',
                  'what the sources say': 'S66 (January 1899): King = 4th Cav, 14th Inf, 1st California; Ovenshine = 1st Washington, 1st Idaho, 1st North Dakota. | S65 (5 Feb): King\'s swing was made by "the Californias, Washingtons and Idahos"; Ovenshine\'s line was "First North Dakota, 14th Infantry and 4th Cavalry".',
                  'how the pilot handled it': 'Assignments follow the roster until 3 Feb and Otis from 4 Feb.', 'comment': 'The brigades were evidently reorganized between January and the battle. A general order of late January would settle it.', 'status': 'Open'})
add('Conflicts', {'conflict_id': 'C-PW2', 'battle_id': 'PHW-MNL', 'question': 'Where were the 1st Nebraska at the close of 5 Feb: the reservoir or the waterworks?',
                  'what the sources say': 'S65: Nebraskans and a Tennessee battalion "captured the powder house and Deposito"; Otis had wired "Waterworks must wait". | S64 index: 1st Neb. "Waterworks".',
                  'how the pilot handled it': 'El Deposito at the close of 5 Feb; the waterworks (pumping station) is later than this playback.', 'status': 'Open'})
add('Conflicts', {'conflict_id': 'C-PW3', 'battle_id': 'PHW-MNL', 'question': 'Which lines on the Signal Corps map are 4 Feb and which later?',
                  'what the sources say': 'S64 title: positions prior to the battle of 5 Feb and after the capture of Caloocan, 10 Feb. No legend found on the sheet. "Former ... outpost" labels; heavy double-dashed lines named for regiments match the index of final positions.',
                  'how the pilot handled it': '"Former" labels = before the battle; named heavy lines = final, shown from the time Otis\'s report puts the line there on 5 Feb.', 'status': 'Open'})
for gid, gap, eff, how in [
    ('G-PW1', 'The subordinate reports (Anderson, MacArthur, King, Ovenshine, H. G. Otis, Hale) were not read', 'Most regiments\' positions before and during the battle rest on Otis and the map alone; several are not placed.', 'Read the 1899 Annual Report volumes (HathiTrust 102278231) for the reports and their maps.'),
    ('G-PW2', 'No Filipino-side source for February 1899 was read', 'Every Filipino position is inferred; commanders are those of 1898.', 'Read Taylor\'s full compilation (PW-A02) for the Feb 1899 zone orders, and a Filipino history of the battle.'),
    ('G-PW3', 'No OpenStreetMap extract for Manila', 'The battle file\'s own current-map drawing is empty: if OpenTopoMap cannot be reached the current map is blank.', 'Cut data/base/manila.json with pipeline/basemaps.py once an extract can be downloaded.'),
    ('G-PW4', 'Kansas, Montana and 3rd Artillery in the battle', 'Only the brigade line is drawn on 5 Feb; the regiments\' parts in it are not.', 'MacArthur\'s and H. G. Otis\'s reports.')]:
    add('Gaps', {'gap_id': gid, 'battle_id': 'PHW-MNL', 'gap': gap, 'effect on the data': eff, 'how to close it': how, 'status in v2': 'Open (20 Nov 2026).'})

wb.save(WB)
print('positions', len(ROWS), 'units', len(UNITS), 'events', len(EV))
