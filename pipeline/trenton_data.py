"""Trenton pilot data (25-26 Dec 1776), version 2: coordinates from a current street map (OpenStreetMap, S39)
and Wiederhold's sketch (S36). Imported by build_v4.py and by the playback prep.
Quotes are only used where the fetched page returned them verbatim; everything else in source_wording is marked 'Paraphrase:'."""

D25, D26 = '1776-12-25', '1776-12-26'
def t(h, d=D26): return f'{d} {h}'
UNK = 'unknown'

# ---- places: (lat, lon, coord_source, precision_m, basis, sketch pixel or None) ----
MK = 'Marker coordinates (Historical Marker Database)'
OSM = 'Placed on the current street map (OpenStreetMap, S39)'
SK = "Read from Wiederhold's sketch (S36), fitted to six points in the town centre (10-28 m misfit) and placed on the current street map"
EST = 'Estimated by Claude from the place description; not measured'
C = {
 'landing':   (40.29672, -74.86753, 'marker', 30, MK + ': "The Christmas Night Crossing", River Drive, New Jersey bank (S27)', None),
 'beartav':   (40.30918, -74.84857, 'modern_map', 40, OSM + ': Bear Tavern Road at Washington Crossing-Pennington Road', None),
 'jacobs':    (40.29080, -74.84043, 'marker', 100, MK + ': "Washington\'s March to Trenton", Jacobs Creek Road (S29); the ford was "a few hundred feet away"', None),
 'birm':      (40.26605, -74.81902, 'marker', 50, MK + ': "An Historic Crossroad", Bear Tavern Road at West Upper Ferry Road (S28)', None),
 'monument':  (40.22575, -74.76478, 'marker', 20, MK + ': Trenton Battle Monument, head of Warren and Broad Streets (S24)', (2255, 650)),
 'headking':  (40.22560, -74.76500, 'modern_map', 40, OSM + ': head of Warren Street (King Street), beside the monument', (2085, 505)),
 'headqueen': (40.22530, -74.76455, 'modern_map', 40, OSM + ': head of Broad Street (Queen Street), just below the monument', (2265, 730)),
 'rallhq':    (40.22248, -74.76587, 'marker', 20, MK + ': "Headquarters of Colonel Johann Gottlieb Rall", 151 North Warren Street (S25)', (2060, 850)),
 'stmich':    (40.22220, -74.76552, 'marker', 20, MK + ': front of St. Michael\'s Church, North Warren Street (S26)', (2170, 850)),
 'barracks':  (40.21948, -74.76850, 'marker', 20, MK + ': Old Barracks, Barrack Street (S30)', (1960, 1430)),
 'bridge':    (40.21816, -74.76413, 'modern_map', 15, OSM + ': South Broad Street over the Assunpink Creek', (2265, 1490)),
 'qfront':    (40.21898, -74.76418, 'modern_map', 15, OSM + ': South Broad Street at East Front Street (Queen and Front)', (2279, 1341)),
 'kstate':    (40.22030, -74.76589, 'modern_map', 15, OSM + ': Warren Street at State Street (King and Second)', (2095, 1125)),
 'khanover':  (40.22104, -74.76577, 'modern_map', 15, OSM + ': Warren Street at East Hanover Street (King Street at Pinkerton\'s alley)', (2095, 990)),
 'qstate':    (40.22015, -74.76421, 'modern_map', 15, OSM + ': Broad Street at State Street (Queen and Second)', (2290, 1125)),
 'qperry':    (40.22272, -74.76437, 'modern_map', 100, OSM + ': Broad Street at Perry Street; how far down Queen Street is not stated', (2301, 738)),
 'yard':      (40.22150, -74.76428, 'modern_map', 40, OSM + ': Broad Street about 200 feet north of East Hanover Street', (2297, 935)),
 'grave':     (40.22190, -74.76500, 'derived', 40, 'About 45 m east of the St. Michael\'s Church marker (S26), on the line the sketch marks G: the churchyard behind the church', (2190, 892)),
 'pettys':    (40.22258, -74.76555, 'sketch_read', 60, SK + '. Letter O, on King Street just north of Rall\'s headquarters', (2100, 745)),
 'gknyp':     (40.22021, -74.76364, 'sketch_read', 60, SK + '. Southern bar marked G, on Second Street just east of Queen Street', (2360, 1148)),
 'nguns':     (40.22171, -74.76497, 'sketch_read', 60, SK + '. Letter N, by the alley behind the English Church', (2215, 895)),
 'second':    (40.22022, -74.76505, 'modern_map', 40, OSM + ': State Street (Second Street) between Warren and Broad', (2187, 1134)),
 'meeting':   (40.22124, -74.76206, 'modern_map', 30, OSM + ': East Hanover Street at North Montgomery Street, the Friends Meeting House corner', (2567, 998)),
 'hlossN':    (40.22330, -74.76220, 'sketch_read', 60, SK + '. Bar marked H, labelled Lossberg', (2575, 665)),
 'hlossS':    (40.22233, -74.76235, 'sketch_read', 60, SK, (2545, 820)),
 'hrallN':    (40.22207, -74.76249, 'sketch_read', 60, SK + '. Bar marked H, labelled Rall', (2525, 860)),
 'hrallS':    (40.22113, -74.76272, 'sketch_read', 60, SK, (2485, 1010)),
 'hknypN':    (40.22104, -74.76255, 'sketch_read', 60, SK + '. Bar marked H, labelled Knyphausen', (2505, 1025)),
 'hknypS':    (40.22009, -74.76176, 'sketch_read', 60, SK, (2590, 1185)),
 'ikingN':    (40.22296, -74.76538, 'sketch_read', 60, SK + '. Western bar marked I, on King Street by the English Church', (2180, 690)),
 'ikingS':    (40.22210, -74.76529, 'sketch_read', 60, SK, (2180, 830)),
 'iqueenN':   (40.22254, -74.76416, 'sketch_read', 60, SK + '. Eastern bar marked I, on Queen Street', (2325, 770)),
 'iqueenS':   (40.22161, -74.76407, 'sketch_read', 60, SK, (2325, 920)),
 'klossW':    (40.22303, -74.76157, 'sketch_read', 60, SK + '. Northern bar at K: along Perry Street between Montgomery and Stockton Streets', (2650, 715)),
 'klossE':    (40.22358, -74.75963, 'sketch_read', 60, SK, (2895, 645)),
 'krallN':    (40.22298, -74.76140, 'sketch_read', 60, SK + '. Southern bar at K: between Montgomery and Stockton Streets, south of Perry Street', (2670, 725)),
 'krallS':    (40.22191, -74.76105, 'sketch_read', 60, SK, (2700, 900)),
 'kcentre':   (40.22260, -74.76100, 'sketch_read', 80, SK + '. Middle of the ground marked K', (2714, 789)),
 'lW':        (40.21916, -74.76126, 'sketch_read', 60, SK + '. Bar beside the letter L, by the creek', (2640, 1340)),
 'lE':        (40.21922, -74.76021, 'sketch_read', 60, SK, (2770, 1340)),
 'mguns':     (40.21890, -74.76302, 'sketch_read', 60, SK + '. Letter M, in the low ground by the creek', (2420, 1365)),
 'creeklow':  (40.21900, -74.76150, 'estimate', 200, EST + '. Low ground by the Assunpink east of Queen Street', (2609, 1363)),
 'mercN':     (40.22220, -74.76677, 'sketch_read', 60, SK + '. Two bars marked R, behind the houses on the west side of King Street', (2000, 800)),
 'mercS':     (40.21960, -74.76651, 'sketch_read', 60, SK, (2000, 1220)),
 'stirEN':    (40.22183, -74.76354, 'sketch_read', 60, SK + '. Two bars marked T, just east of Queen Street', (2392, 890)),
 'stirES':    (40.21942, -74.76326, 'sketch_read', 60, SK, (2397, 1280)),
 'xsW':       (40.21991, -74.76272, 'sketch_read', 60, SK + '. Southern line marked X, along today\'s East State Street', (2470, 1205)),
 'xsE':       (40.22006, -74.76029, 'sketch_read', 60, SK, (2770, 1205)),
 'xnW':       (40.22325, -74.76240, 'sketch_read', 60, SK + '. Northern line marked X, along today\'s Perry Street', (2550, 672)),
 'xnE':       (40.22340, -74.75990, 'sketch_read', 60, SK, (2860, 672)),
 'sfarN':     (40.22327, -74.75907, 'sketch_read', 80, SK + '. Far eastern bar marked S, east of Stockton Street', (2960, 700)),
 'sfarS':     (40.22205, -74.75870, 'sketch_read', 80, SK, (2990, 900)),
 'gloverW':   (40.21704, -74.76178, 'sketch_read', 120, SK + '. Bar marked Q south of the creek; beyond the fitted area', (2550, 1675)),
 'gloverE':   (40.21712, -74.76057, 'sketch_read', 120, SK, (2700, 1675)),
 'howell':    (40.23163, -74.76951, 'sketch_read', 200, 'Pennington Avenue about 800 m from the head of the town. Distance scaled from Wiederhold\'s sketch (S36) against Calhoun\'s house; the sketch is not to scale outside the town', (1090, 440)),
 'halt500':   (40.23531, -74.77185, 'derived', 300, 'Derived: 500 yards beyond the picket position (howell) along Pennington Avenue (S39)', (600, 495)),
 'calhoun':   (40.22906, -74.76852, 'modern_map', 80, OSM + ': Pennington Avenue at Calhoun Street, taken as the site of Alexander Calhoun\'s house', (1530, 440)),
 'hermitage': (40.22770, -74.78340, 'modern_map', 150, OSM + ': West State Street at Colonial Avenue. The Hermitage stood on what is now Colonial Avenue', (1110, 1320)),
 'riverrd':   (40.22459, -74.77735, 'modern_map', 150, OSM + ': West State Street, the River Road into the town', (1340, 1280)),
 'foxchase':  (40.22871, -74.76022, 'sketch_read', 250, 'Brunswick Avenue about 500 m from the head of the town. Distance scaled from Wiederhold\'s sketch (S36), letter D; the sketch is not to scale outside the town', (2867, 237)),
 'washpost':  (40.22855, -74.76367, 'modern_map', 50, OSM + ': Martin Luther King Jr Boulevard (formerly Princeton Avenue) at Fountain Avenue', (2170, 440)),
 'brunsblk':  (40.22753, -74.76199, 'sketch_read', 200, 'Brunswick Avenue about 300 m from the head of the town. From the bar marked S at the right of the American line on Wiederhold\'s sketch (S36)', (2660, 500)),
 'fermoy':    (40.22830, -74.76080, 'estimate', 300, EST + '. On the Brunswick (Princeton) road beyond Stephen, toward the Maidenhead road picket', (2800, 330)),
 'ferry':     (40.20750, -74.76300, 'estimate', 500, EST + '. Trenton Ferry landing below the town', (2930, 2310)),
}
def pt(k): return [C[k]]
def ln(a, b): return [C[a], C[b]]

UNITS = [
 # id, name, label, side, nation, branch, echelon, parent, commander, strength, sources, notes
 ('T-US-ARMY', "Washington's army (Trenton force)", 'Washington', 'ARW-US', 'United States', 'Infantry', 'Army', '', 'Gen. George Washington', 'About 2,400 (S21; S27); 2,420 (S34)', 'S20; S21', 'The whole crossing force. Brigade strengths are not in the sources read (TG03).'),
 ('T-US-HQ', "Washington's headquarters", 'Washington (HQ)', 'ARW-US', 'United States', 'Infantry', 'Headquarters', 'T-US-ARMY', 'Gen. George Washington', '', 'S21; S22', 'Rode with Greene\'s division.'),
 ('T-US-GREENE', "Greene's division (left wing)", 'Greene', 'ARW-US', 'United States', 'Infantry', 'Division', 'T-US-ARMY', 'Maj. Gen. Nathanael Greene', '', 'S21; S22', 'Upper column, by the Scotch and Pennington roads. Wiederhold\'s sketch marks "Gen. Greene\'s Brigade" (U) at the head of the town.'),
 ('T-US-SULL', "Sullivan's division (right wing)", 'Sullivan', 'ARW-US', 'United States', 'Infantry', 'Division', 'T-US-ARMY', 'Maj. Gen. John Sullivan', '', 'S21; S22', 'Lower column, by the River Road. Wiederhold\'s sketch marks "Gen. Sullivan\'s Brigade" (Q).'),
 ('T-US-STEPH', "Stephen's brigade", 'Stephen', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-GREENE', 'Brig. Gen. Adam Stephen', '', 'S21; S22; S36', 'Advance of the army. Scott\'s and Lawson\'s battalions named in S22.'),
 ('T-US-MERC', "Mercer's brigade", 'Mercer', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-GREENE', 'Brig. Gen. Hugh Mercer', '', 'S21; S22; S36', ''),
 ('T-US-STIR', "Lord Stirling's brigade", 'Stirling', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-GREENE', 'Brig. Gen. William Alexander, Lord Stirling', '', 'S21; S22; S36', 'Reserve of the left wing. Weedon\'s regiment named in S33.'),
 ('T-US-FERM', "De Fermoy's brigade", 'Fermoy', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-GREENE', 'Brig. Gen. Matthias Alexis Roche de Fermoy', '', 'S21; S22', 'Hand\'s riflemen and the German Battalion (S20 note 7; S33). Not marked on Wiederhold\'s sketch.'),
 ('T-US-STCL', "St. Clair's brigade", 'St. Clair', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-SULL', 'Brig. Gen. Arthur St. Clair', '', 'S21; S22', ''),
 ('T-US-STARK', "Stark's regiment", 'Stark', 'ARW-US', 'United States', 'Infantry', 'Regiment', 'T-US-STCL', 'Col. John Stark', '', 'S21; S33', ''),
 ('T-US-GLOV', "Glover's brigade", 'Glover', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-SULL', 'Col. John Glover', '', 'S21; S22', 'Glover\'s own 14th Continental Regiment manned the boats (S33).'),
 ('T-US-SARG', "Sargent's brigade", 'Sargent', 'ARW-US', 'United States', 'Infantry', 'Brigade', 'T-US-SULL', 'Col. Paul Dudley Sargent', '', 'S21; S22', 'No position during the attack in the sources read (TG04).'),
 ('T-US-ADVW', "Capt. William Washington's advance party", 'W. Washington', 'ARW-US', 'United States', 'Infantry', 'Detachment', 'T-US-GREENE', 'Capt. William Washington', '40 men (S21)', 'S21', '3rd Virginia Regiment (S33). Lt. James Monroe was with it.'),
 ('T-US-ADVF', "Capt. John Flahaven's advance party", 'Flahaven', 'ARW-US', 'United States', 'Infantry', 'Detachment', 'T-US-SULL', 'Capt. John Flahaven', '40 men (S21)', 'S21', ''),
 ('T-US-FORR', "Forrest's battery", 'Forrest', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-GREENE', 'Capt. Forrest', 'Six guns (S22)', 'S21; S22', ''),
 ('T-US-HAM', "Hamilton's battery (New York)", 'Hamilton', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-GREENE', 'Capt. Alexander Hamilton', '', 'S21; S22', ''),
 ('T-US-BAUM', "Bauman's battery", 'Bauman', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-GREENE', 'Capt. Bauman', '', 'S21; S22', 'No position during the attack in the sources read (TG04).'),
 ('T-US-MOUL', "Moulder's battery", 'Moulder', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-SULL', 'Capt. Moulder', '', 'S21; S22', ''),
 ('T-US-NEIL', "Neil's battery", 'Neil', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-SULL', 'Capt. Neil', '', 'S21; S22', 'No position during the attack in the sources read (TG04).'),
 ('T-US-HUGG', "Hugg's battery", 'Hugg', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-SULL', 'Capt. Hugg', '', 'S21; S22', 'No position during the attack in the sources read (TG04).'),
 ('T-US-SARGB', "Sargent's battery", 'Sargent (bty)', 'ARW-US', 'United States', 'Artillery', 'Battery', 'T-US-SULL', 'Capt. Sargent', '', 'S21; S22', 'No position during the attack in the sources read (TG04).'),
 ('T-US-EWING', "Ewing's brigade (Pennsylvania militia)", 'Ewing', 'ARW-US', 'United States', 'Infantry', 'Brigade', '', 'Brig. Gen. James Ewing', '', 'S20', 'Did not cross. Was to seize the Assunpink bridge.'),
 ('T-US-CADW', "Cadwalader's force", 'Cadwalader', 'ARW-US', 'United States', 'Infantry', 'Brigade', '', 'John Cadwalader', '', 'S20', 'Did not complete its crossing from Bristol.'),

 ('T-HE-BDE', "Rall's brigade", 'Rall', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Brigade', '', 'Col. Johann Gottlieb Rall', 'About 1,400 (S22); 1,500 (S35); 1,520 (S34)', 'S21; S22', 'Garrison of Trenton. See TC06 on its strength.'),
 ('T-HE-RALL', 'Rall regiment', 'Rall Regt', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Regiment', 'T-HE-BDE', '', '512 men and 11 officers on duty (S21)', 'S21; S36', 'The regiment "of the day" on 26 December.'),
 ('T-HE-LOSS', 'Von Lossberg regiment', 'Lossberg', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Regiment', 'T-HE-BDE', '', '467 men and 16 officers (S21)', 'S21; S36', 'Lt. Col. Scheffer and Maj. von Hanstein surrendered the Rall and Lossberg regiments (S22).'),
 ('T-HE-KNYP', 'Von Knyphausen regiment', 'Knyphausen', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Regiment', 'T-HE-BDE', 'Maj. Friedrich von Dechow', '429 men and 12 officers (S21)', 'S21; S33; S36', 'Wiederhold\'s own regiment.'),
 ('T-HE-ALT', "Capt. von Altenbockum's company (Lossberg)", 'Altenbockum', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Company', 'T-HE-LOSS', 'Capt. von Altenbockum', '', 'S21; S36', ''),
 ('T-HE-JAG', 'Jäger company', 'Jägers', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Company', 'T-HE-BDE', 'Lt. von Grothausen', '50 (S22; S36)', 'S21; S22', ''),
 ('T-GB-16LD', '16th Light Dragoons (detachment)', '16 LD', 'ARW-CR', 'Great Britain', 'Cavalry', 'Detachment', 'T-HE-BDE', '', '20 (S22; S34)', 'S21; S22', 'The only British troops in the garrison.'),
 ('T-HE-ARTR', "Rall regiment's guns", 'Rall guns', 'ARW-CR', 'Hesse-Cassel', 'Artillery', 'Section', 'T-HE-RALL', '', 'Two brass 3-pounders (S21)', 'S21; S36', ''),
 ('T-HE-ARTL', "Von Lossberg regiment's guns", 'Lossberg guns', 'ARW-CR', 'Hesse-Cassel', 'Artillery', 'Section', 'T-HE-LOSS', '', 'Two 3-pounders', 'S21; S36', 'Six 3-pounders in the brigade (S21; S34).'),
 ('T-HE-ARTK', "Von Knyphausen regiment's guns", 'Knyphausen guns', 'ARW-CR', 'Hesse-Cassel', 'Artillery', 'Section', 'T-HE-KNYP', 'Lt. Fischer', 'Two 3-pounders', 'S21; S36', ''),
 ('T-HE-PKPEN', 'Pennington road picket', 'Wiederhold', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-BDE', 'Lt. Andreas Wiederhold', 'See TC10', 'S21; S22; S36', 'Wiederhold drew the sketch (S36).'),
 ('T-HE-PKRIV', 'River road picket (jägers)', 'Jäger picket', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-JAG', '', 'See TC03', 'S21; S22; S36', ''),
 ('T-HE-PKMAI', 'Maidenhead road picket', 'Fox Chase picket', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-BDE', '', 'See TC10', 'S21; S36', 'The principal picket.'),
 ('T-HE-PKBRG', 'Assunpink bridge guard', 'Bridge guard', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-BDE', '', 'A sergeant and 18 men (S21)', 'S21', ''),
 ('T-HE-PKFER', 'Trenton Ferry picket', 'Ferry picket', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-BDE', '', 'See TC10', 'S21; S36', ''),
 ('T-HE-PKCRO', 'Crosswicks drawbridge detachment', 'Crosswicks', 'ARW-CR', 'Hesse-Cassel', 'Infantry', 'Detachment', 'T-HE-BDE', '', 'See TC07', 'S21', 'About 7 miles from Trenton; off the battle map.'),
]

INF = 'Inferred from the sequence of events; no clock time in the sources read'
P = []
def row(pid, unit, se, sl, ee, el, tb, act, place, geom, srcs, say, method, oc, notes='', battle='TREN', ch=''):
    P.append(dict(pos_id=pid, unit_id=unit, battle_id=battle, se=se, sl=sl, ee=ee, el=el, time_basis=tb, activity=act, place=place, geom=geom,
                  source_ids=srcs, say=say, method=method, oc=oc, notes=notes, ch4=ch))
MAP = 'Coordinates replaced: '
NEW = 'New in v4: read from Wiederhold\'s sketch.'

# --- the crossing and the march (campaign rows: no battle tag) ---
row('T01', 'T-US-ARMY', t('17:00', D25), t('19:00', D25), t('02:00'), t('03:00'), 'Start: "as soon as it grew dark" (S20), hour inferred. End: about 2 a.m. (Knox, S20 note 3) or about 3 a.m. (S20; S21)',
    'Crossing the Delaware', "McKonkey's Ferry to the New Jersey bank", pt('landing'), 'S20; S21; S27',
    'Paraphrase: the artillery was not all over until about three o\'clock (S20).', 'stated', 'medium', 'Regiments began moving to the ferry about 2 to 3 p.m. on 25 December (S21).', battle='')
row('T02', 'T-US-ARMY', t('03:00'), t('04:00'), t('04:00'), t('04:00'), 'S20: near four before the troops took up their line of march',
    'Forming for the march', 'New Jersey bank at the ferry', pt('landing'), 'S20; S21', 'Paraphrase: it was near four before the troops took up their line of march (S20).', 'stated', 'medium', '', battle='')
row('T03', 'T-US-ARMY', t('06:00'), t('06:00'), t('06:00'), t('06:00'), 'Modern marker gives 6 AM (S29); no period source read',
    'Fording Jacobs Creek', 'Jacobs Creek ravine on the Bear Tavern Road', pt('jacobs'), 'S29', 'Paraphrase: the marker times the crossing of the creek at 6 AM and says the guns were lowered into the ravine and hauled out.', 'stated', 'low',
    'The only source for this time is a modern marker.', battle='')
row('T04', 'T-US-ARMY', t('06:30'), t('07:00'), t('06:30'), t('07:00'), 'Disputed: see TC02',
    'Halt; army divides into two columns', 'Birmingham crossroads (West Trenton)', pt('birm'), 'S21; S22; S28; S29; S33',
    'Paraphrase: the army marched through the Bear Tavern to Birmingham and divided there; Washington stopped briefly at Benjamin Moore\'s (S21).', 'stated', 'medium',
    'First light appeared about here (S33, citing Fischer). S22 notes that some historians put the division at Bear Tavern.', battle='')
row('T05', 'T-US-GREENE', UNK, t('07:00'), t('07:45'), t('08:00'), 'S20 editors\' note 6: about 7 a.m.',
    'Halt short of the Hessian picket', 'Pennington Road, about 500 yards from the Hessian advance guard', pt('halt500'), 'S20',
    'Paraphrase: the upper division halted about 500 yards from the Hessian advance guard around 7 a.m. (S20, editors\' note 6).', 'stated', 'low',
    'Cannot be squared with a 7 a.m. division at Birmingham, more than four miles back (TC02).', ch=MAP + 'moved with the picket position.')
# --- Hessian garrison before the attack ---
EVE = t('20:00', D25)
row('T06', 'T-HE-PKPEN', t('16:00', D25), EVE, t('07:30'), t('08:00'), 'Start: after the alarm on Christmas evening, when the post was reinforced (S21). End: TC01',
    'Picket post', "Richard Howell's house (cooper shop), Pennington Road", pt('howell'), 'S21; S33; S36', 'Sketch legend A: "picquet of 1 officer and 25 privet" (S36).', 'stated', 'medium',
    'Paraphrase of S21: a corporal and 15 men, reinforced to an officer, an NCO and 19 men. "About a mile northwest of Trenton" (S33). Strength: TC10.', ch=MAP + 'now about 800 m from the head of the town, scaled from the sketch (v3 estimate was 1.2 km).')
row('T07', 'T-HE-ALT', D25, D25, t('07:45'), t('08:05'), INF, 'Quarters', "Alexander Calhoun's house, Pennington Road", pt('calhoun'), 'S21; S36',
    'Sketch legend B: Captain de Altenbockum\'s company of Lossberg\'s regiment (S36).', 'stated', 'medium', 'Paraphrase of S21: the company was quartered at Calhoun\'s house (pp. 92-98, p. 148).', ch=MAP + 'the Pennington Avenue and Calhoun Street corner on the current map (v3 estimate was 160 m off).')
row('T08', 'T-HE-PKRIV', D25, D25, t('07:48'), t('08:05'), 'End: about three minutes after the upper picket was struck (S20; S21)',
    'Picket post', 'The Hermitage (Gen. Philemon Dickinson\'s house), River Road', pt('hermitage'), 'S21; S22; S36',
    '"a commissioned officer and fifty men" and "a sergeant and fifteen men" are both given (S21). Sketch legend F: a detachment of 1 officer and 50 hunters (S36).', 'stated', 'medium', 'Strength: TC03.', ch=MAP + 'West State Street at Colonial Avenue on the current map (v3 estimate was about 300 m off).')
row('T09', 'T-HE-JAG', D25, D25, t('07:48'), t('08:10'), INF, 'Quarters', 'Old Barracks, where the River Road meets Front Street', pt('barracks'), 'S21; S30',
    'Paraphrase: the jägers were quartered in the old barracks, with a post at Dickinson\'s house (S21).', 'stated', 'medium', '')
row('T10', 'T-HE-PKMAI', D25, D25, t('08:00'), UNK, INF, 'Picket post', 'Fox Chase Tavern, Maidenhead (Brunswick) road', pt('foxchase'), 'S21; S33; S36',
    'Sketch legend D: picket of 1 captain, 1 officer and 75 men (S36).', 'stated', 'low',
    'Paraphrase of S21: about 70 men; the principal picket. Hand\'s riflemen and the German Battalion "attacked the outpost there" (S33). What became of it is not in the sources read.', ch=MAP + 'about 500 m up Brunswick Avenue, scaled from the sketch.')
row('T11', 'T-HE-PKBRG', D25, D25, t('08:10'), t('08:45'), INF, 'Guard post', 'Queen Street bridge over the Assunpink', pt('bridge'), 'S21',
    'Paraphrase: a sergeant and 18 men; its soldiers left the post without firing a shot (S21).', 'stated', 'medium', 'S21 gives 18 men in one place and 19 in another.', ch=MAP + 'the bridge on the current map.')
row('T12', 'T-HE-PKFER', D25, D25, t('08:10'), UNK, INF, 'Picket post', 'Trenton Ferry road and landing', pt('ferry'), 'S21; S36',
    'Sketch legend E: detachment of 1 officer and 30 privates, which retired to Burlington (S36).', 'stated', 'low', 'Paraphrase of S21: one officer and 27 men; withdrew toward Bordentown. Still an estimate: the sketch is not to scale here.')
row('T13', 'T-HE-PKCRO', D25, D25, t('10:00'), UNK, 'S21: news of the defeat reached it around 10 a.m.', 'Detached post', 'Crosswicks drawbridge', None, 'S21',
    'Paraphrase: took no part and escaped capture; heard of the disaster around 10 a.m. (S21).', 'stated', 'medium', 'Off the battle map; no coordinates.')
row('T14', 'T-HE-RALL', D25, D25, t('07:45'), t('08:05'), INF, 'Quarters', 'King and Second Streets: the jail, post office and taverns', pt('kstate'), 'S21',
    'Paraphrase: quartered at King and Second Streets in the jail, the post office, the City Tavern, the Bull Head Tavern and nearby houses (S21, pp. 92-98).', 'stated', 'medium', '', ch=MAP + 'the Warren and State Street corner on the current map (v3 was about 70 m off).')
row('T15', 'T-HE-LOSS', D25, D25, t('07:45'), t('08:05'), INF, 'Quarters', 'King Street, including the English Church', pt('stmich'), 'S21; S26',
    'Paraphrase: quartered on King Street, including the English Church and several houses (S21, pp. 92-98).', 'stated', 'medium', 'The English Church is St. Michael\'s.')
row('T16', 'T-HE-KNYP', D25, D25, t('07:45'), t('08:05'), INF, 'Quarters', 'Queen and Second Streets, including the Presbyterian Church', pt('qstate'), 'S21',
    'Paraphrase: quartered at Queen and Second Streets, including the Presbyterian Church and the village school (S21, pp. 92-98).', 'stated', 'medium', '', ch=MAP + 'the Broad and State Street corner on the current map.')
row('T17', 'T-GB-16LD', D25, D25, t('07:45'), t('08:15'), INF, 'Quarters', "Friends' Meeting House, Third (Hanover) Street", pt('meeting'), 'S21; S20',
    "Paraphrase: the dragoons were in the Friends' Meeting House (S21). The British light horse escaped (S20, note 10).", 'stated', 'medium', 'Escape route not in the sources read.', ch=MAP + 'the East Hanover and Montgomery Street corner on the current map.')
row('T18', 'T-HE-ARTR', D25, D25, t('08:00'), t('08:15'), INF, 'Guns parked', 'King Street, by Rall\'s headquarters', pt('rallhq'), 'S21; S25',
    'Paraphrase: the artillerymen were in the Methodist Church and the English Church; the guns stood in King Street (S21).', 'stated', 'medium', '')
# --- the attack on the outposts ---
row('T19', 'T-US-GREENE', t('07:30'), t('08:00'), t('07:45'), t('08:05'), 'Disputed: see TC01', 'Attack on the picket', "Howell's house, Pennington Road", pt('howell'), 'S20; S21; S22; S36',
    '"exactly at eight OClock" (S20, Washington). "shortly after half past seven" (Lt. Piel, in S21). "nearly eight o\'clock" (S21).', 'stated', 'medium',
    'Paraphrase of S22: Greene\'s advance guard routed the Pennington Road picket. Sketch letter P: the attack toward picket A and company B.', ch=MAP + 'moved with the picket position.')
row('T20', 'T-HE-PKPEN', t('07:45'), t('08:05'), t('08:00'), t('08:15'), INF, 'Falling back on the supporting company', "Toward Calhoun's house", pt('calhoun'), 'S21',
    "Paraphrase: the picket fell back across the fields toward Rall's quarters and was forced toward the von Altenbockum company (S21).", 'stated', 'low', '', ch=MAP + 'moved with Calhoun\'s house.')
row('T21', 'T-HE-ALT', t('08:00'), t('08:15'), t('08:15'), t('08:30'), INF, 'Retiring into the town', 'By Queen Street', pt('qperry'), 'S21',
    'Paraphrase: the company retired by Queen Street after its captain was wounded (S21).', 'stated', 'low', 'Point is on Queen Street at the upper end of the town; how far it retired is not stated.', ch=MAP + 'Broad Street at Perry Street.')
row('T22', 'T-US-ADVF', t('07:48'), t('08:03'), t('07:55'), t('08:10'), 'About three minutes after the upper column (S20; S21)', 'Attack on the jäger picket', 'The Hermitage, River Road', pt('hermitage'), 'S20; S21',
    'Paraphrase: about three minutes later Sullivan\'s troops, led by Captain John Flahaven, struck the jäger picket at the Hermitage (S21).', 'stated', 'medium', '', ch=MAP + 'moved with the Hermitage.')
row('T23', 'T-HE-PKRIV', t('07:55'), t('08:10'), t('08:15'), t('08:30'), INF, 'Retreating to the bridge', 'Along Front Street to the Queen Street bridge', ln('barracks', 'bridge'), 'S21; S20',
    'Paraphrase: the jägers retreated along Front Street toward the Queen Street bridge; one was captured, the rest escaped and some fled to Bordentown (S21).', 'stated', 'low',
    'Drawn as the stretch from the barracks to the bridge. Lt. von Grothausen escaped with fifty jägers (S20, note 10).')
row('T55', 'T-US-SULL', t('07:50'), t('08:10'), t('08:05'), t('08:25'), INF, 'Entering the town by the River Road', 'River Road (West State Street)', pt('riverrd'), 'S21; S22; S36',
    'Sketch legend Q: "Gen. Sullivan\'s Brigade", drawn on the lower road into the town (S36).', 'stated', 'medium', 'Paraphrase of S22: Sullivan\'s men pushed the Hermitage outpost back toward the town.', ch=NEW)
row('T56', 'T-US-SULL', t('08:15'), t('08:40'), t('09:00'), t('10:00'), INF, 'Holding the bridge', 'Queen Street bridge over the Assunpink', pt('bridge'), 'S20; S22; S36',
    'Sketch legend Q, written beside the bridge (S36).', 'stated', 'medium', 'Paraphrase of S22: the Knyphausen regiment\'s attempt on the bridge was blocked by Sullivan.', ch=NEW)
# --- the fight in the town ---
row('T24', 'T-US-FORR', t('07:50'), t('08:10'), t('09:00'), t('10:00'), INF, 'In battery, firing down King and Queen Streets', 'Head of King and Queen Streets', pt('monument'), 'S21; S22; S24; S36',
    '"Marks site of major gun emplacement at Battle of Trenton December 25, 1776." (S24; the marker\'s date is a day early).', 'stated', 'high',
    'Paraphrase of S22: Forrest\'s six-gun battery stood at the junction of King and Queen Streets. Sketch letter W: American artillery, drawn along the head of the town.')
row('T25', 'T-US-HAM', t('07:50'), t('08:10'), t('09:00'), t('10:00'), INF, 'In battery, firing down King Street', 'Head of King Street', pt('headking'), 'S21; S22; S36',
    'Paraphrase: Hamilton\'s New York artillery fired down King Street (S22).', 'stated', 'medium', '', ch=MAP + 'set at the head of Warren Street, beside the monument.')
row('T26', 'T-US-HQ', t('07:50'), t('08:10'), t('09:00'), t('10:00'), INF, "Washington's post", 'High ground on Princeton Avenue, opposite Fountain Avenue', pt('washpost'), 'S21; S22; S36',
    'Sketch legend V: the place where General Washington posted himself to watch every motion and give his orders (S36).', 'stated', 'medium',
    'Paraphrase of S21: on what is now Princeton Avenue, opposite Fountain Avenue. The sketch draws V just north-west of the head of the town.', ch=MAP + 'the Fountain Avenue corner on the current map (v3 estimate was 75 m off).')
row('T57', 'T-US-GREENE', t('07:50'), t('08:10'), t('09:00'), t('10:00'), INF, 'At the head of the town', 'Head of Queen Street', pt('headqueen'), 'S23; S36',
    'Sketch legend U: "Gen. Greene\'s Brigade", marked at the head of Queen Street and on the line above the town (S36).', 'stated', 'medium',
    'Paraphrase of S23: Greene\'s division, with Washington in the lead, occupied the high ground at the head of the town.', ch=NEW)
row('T27', 'T-US-STIR', t('07:50'), t('08:10'), t('08:15'), t('08:35'), INF, 'Reserve at the head of the town', 'Head of King Street', pt('headking'), 'S21; S36',
    'Paraphrase: Stirling\'s reserve moved to the head of King Street (S21). Sketch letter T at the left of the line above the town.', 'stated', 'medium', '', ch=MAP + 'head of Warren Street.')
row('T28', 'T-US-STEPH', t('07:55'), t('08:15'), t('08:25'), t('08:45'), INF, 'Blocking the road to Princeton', 'Brunswick (Maidenhead) road, north-east of the town', pt('brunsblk'), 'S20; S21; S22; S36',
    'Paraphrase: Stephen\'s and de Fermoy\'s brigades blocked the Brunswick road toward Maidenhead (S21). Sketch letter S at the right of the line above the town.', 'stated', 'low',
    'Washington: the enemy tried to file off by a road on their right toward Princeton and a body of troops thrown in their way checked them (S20).', ch=MAP + 'about 300 m up Brunswick Avenue, from the sketch.')
row('T58', 'T-US-STEPH', t('08:25'), t('08:45'), t('09:00'), t('10:00'), INF, 'Closing on the Hessians from the north', 'North side of the ground where they surrendered', ln('xnW', 'xnE'), 'S36',
    'Sketch legend X: "attack at the last to K and L"; dotted lines lead to this line from the bars marked S (S36).', 'stated', 'medium', 'Runs along today\'s Perry Street between Montgomery and Stockton Streets.', ch=NEW)
row('T29', 'T-US-FERM', t('07:55'), t('08:15'), t('08:25'), t('08:45'), INF, 'Blocking the road to Princeton', 'Fields on the left, across the Princeton road', pt('fermoy'), 'S20; S22; S33',
    'Paraphrase: Hand\'s riflemen and the Scott and Lawson battalions moved through the fields on the left to take the Princeton road (S22).', 'stated', 'low', 'Still an estimate: the brigade is not marked on the sketch.')
row('T59', 'T-US-FERM', t('08:25'), t('08:45'), t('09:00'), t('10:00'), INF, 'Closing the ring on the east', 'East of the ground where the Hessians surrendered', ln('sfarN', 'sfarS'), 'S36; S20',
    'Sketch: a bar marked S (Stephen) east of the surrender ground (S36).', 'inferred', 'low',
    'Assumption: the sketch labels this bar S, but Stephen is also drawn north of the ground. It is given to de Fermoy here as the other brigade sent to cut the Princeton road. S20 note 7: Hand and the German Battalion blocked the enemy\'s flank.', ch=NEW)
row('T30', 'T-US-MERC', t('08:00'), t('08:20'), t('09:00'), t('10:00'), INF, 'Fighting from behind the houses', 'West (left) side of King Street', ln('mercN', 'mercS'), 'S33; S36',
    'Sketch legend R: "Gen. Mercer\'s Brigade", two bars behind the houses on the west side of King Street (S36).', 'stated', 'medium',
    'Paraphrase of S33: Mercer\'s men took houses on the left side of King Street and helped break the Hessian advance.', ch=MAP + 'now a line read from the sketch; a period source replaces the modern summary.')
row('T31', 'T-HE-RALL', t('07:45'), t('08:05'), t('08:10'), t('08:25'), INF, 'Formed', "King Street, facing east, near Pinkerton's alley", pt('khanover'), 'S21; S33; S36',
    "Paraphrase: the Rall regiment formed on King Street facing east, near Pinkerton's alley, now East Hanover Street (S21).", 'stated', 'medium',
    'The sketch marks a forming place (G) on Third Street just east of Queen Street, about 150 m east of here (TC11).', ch=MAP + 'the Warren and East Hanover Street corner on the current map.')
row('T32', 'T-HE-LOSS', t('07:45'), t('08:05'), t('08:10'), t('08:25'), INF, 'Formed', 'Graveyard behind the English Church, on Church alley', pt('grave'), 'S21; S36',
    'Paraphrase: the von Lossberg regiment formed in the graveyard behind the English Church (S21). Sketch: a bar marked G on the alley by the church.', 'stated', 'medium', '')
row('T33', 'T-HE-KNYP', t('07:45'), t('08:05'), t('08:10'), t('08:25'), INF, 'Formed', 'Second Street, just east of Queen Street', pt('gknyp'), 'S36; S33',
    'Sketch legend G: "place where the regiment formed itself"; the southern G bar lies on Second Street east of Queen (S36).', 'stated', 'medium',
    'Which regiment formed at which G is not written on the sketch; the Knyphausen regiment was quartered here (TC11). S33 says "the lower end of Queen Street".', ch=MAP + 'read from the sketch; a period source replaces the modern summary.')
row('T34', 'T-HE-ARTR', t('08:05'), t('08:20'), t('08:15'), t('08:35'), INF, 'In action; guns lost', "King Street, near the bridge over Petty's Run", pt('pettys'), 'S21; S33; S36',
    'Sketch legend O: Rall\'s cannons, "instantly dismounted" (S36).', 'stated', 'medium',
    "Paraphrase of S21: the two brass three-pounders were lost near the bridge over Petty's Run on King Street. They fired six rounds each (S33).", ch=MAP + 'read from the sketch (letter O), on King Street just north of the headquarters.')
row('T35', 'T-US-ADVW', t('08:10'), t('08:30'), t('08:15'), t('08:40'), INF, 'Taking the Hessian guns', "King Street, near the bridge over Petty's Run", pt('pettys'), 'S21; S20',
    "Paraphrase: Captain William Washington's and Lieutenant Monroe's men took the guns, and both officers were wounded (S21).", 'stated', 'medium', '', ch=MAP + 'moved with the guns.')
row('T60', 'T-HE-ARTK', t('08:05'), t('08:20'), t('08:15'), t('08:35'), INF, 'In action', 'By the alley behind the English Church', pt('nguns'), 'S36',
    'Sketch legend N: Knyphausen\'s cannons (S36).', 'stated', 'medium', 'The sketch places these guns in the town; Stryker has them later stalled near the creek (T45).', ch=NEW)
row('T36', 'T-US-STIR', t('08:15'), t('08:35'), t('08:35'), t('09:00'), INF, 'Advancing into the town', 'Just east of Queen Street, from Third Street to Front Street', ln('stirEN', 'stirES'), 'S36; S33',
    'Sketch legend T: "Gen. Lord Stirling\'s Brigade", two bars just east of Queen Street (S36).', 'stated', 'medium',
    "Paraphrase of S33: Weedon's men advanced down King Street after the Hessian guns were taken. The sketch puts Stirling's bars east of Queen Street, not on King Street.", ch=MAP + 'now the line the sketch gives; v3 drew it on King Street from a modern summary.')
row('T37', 'T-HE-RALL', t('08:10'), t('08:25'), t('08:25'), t('08:45'), INF, 'Line of battle east of the town', 'East edge of the village, along today\'s Montgomery Street', ln('hrallN', 'hrallS'), 'S36; S22; S33',
    'Sketch legend H: "place where the Hessians formed a line of battle"; the middle bar is labelled Rall (S36).', 'stated', 'medium',
    'Paraphrase of S22: Rall and von Lossberg fell back to "The Swamp". S33: "a field outside town". See TC08.', ch=MAP + 'now the line the sketch gives, between today\'s Academy and East Hanover Streets.')
row('T38', 'T-HE-LOSS', t('08:10'), t('08:25'), t('08:25'), t('08:45'), INF, 'Line of battle east of the town', 'East edge of the village, along today\'s Montgomery Street', ln('hlossN', 'hlossS'), 'S36; S22; S33',
    'Sketch legend H; the northern bar is labelled Lossberg (S36).', 'stated', 'medium', 'Between today\'s Perry and Academy Streets.', ch=MAP + 'now the line the sketch gives.')
row('T61', 'T-HE-KNYP', t('08:10'), t('08:25'), t('08:30'), t('08:50'), INF, 'Line of battle, covering the left flank', 'East edge of the village, south of the other two regiments', ln('hknypN', 'hknypS'), 'S36',
    'Sketch legend I: the attack of Lossberg and Rall on the town, "at which time Knyphausen covered the left flank" (S36).', 'stated', 'medium', 'Between today\'s East Hanover and East State Streets.', ch=NEW)
row('T39', 'T-HE-RALL', t('08:25'), t('08:45'), t('08:35'), t('09:00'), INF, 'Counter-attack into the town; Rall shot', "Queen Street, near Isaac Yard's house", ln('iqueenN', 'iqueenS'), 'S21; S22; S36',
    '"Forward! Forward!" (Rall, in S22). Sketch legend I: "attack of the two regiments Lossberg and Rall to the town" (S36).', 'stated', 'medium',
    "Paraphrase of S21: Rall was mortally wounded near Isaac Yard's house on Queen Street, about 200 feet north of Pinkerton's alley. Which regiment stood on which street is not written on the sketch (TC11).", ch=MAP + 'now the eastern bar marked I on the sketch, on Queen Street.')
row('T40', 'T-HE-LOSS', t('08:25'), t('08:45'), t('08:35'), t('09:00'), INF, 'Counter-attack into the town', 'King Street, by the English Church', ln('ikingN', 'ikingS'), 'S36; S33',
    'Sketch legend I; the western bar lies on King Street by the church (S36).', 'stated', 'low', 'Which regiment stood on which street is not written on the sketch (TC11).', ch=MAP + 'now the western bar marked I on the sketch.')
row('T41', 'T-HE-RALL', t('08:35'), t('09:00'), t('08:45'), t('10:00'), 'End: TC04', 'Surrounded; surrendered', "Orchard east of the Friends' Meeting House", ln('krallN', 'krallS'), 'S20; S21; S22; S36',
    '"lay down their Arms" (S20). Sketch legend K: "place at which Lossberg and Rall surrendered" (S36).', 'stated', 'medium',
    'Paraphrase of S21: the two regiments surrendered in the orchard east of the Friends\' Meeting House; Lord Stirling received their swords. On the current map the ground lies between Montgomery and Stockton Streets, at and south of Perry Street.', ch=MAP + 'now read from the sketch; the v3 estimate was about 150 m to the south-east.')
row('T42', 'T-HE-LOSS', t('08:35'), t('09:00'), t('08:45'), t('10:00'), 'End: TC04', 'Surrounded; surrendered', "Orchard east of the Friends' Meeting House", ln('klossW', 'klossE'), 'S20; S21; S22; S36',
    'Sketch legend K (S36).', 'stated', 'medium', 'The northern bar at K, along today\'s Perry Street.', ch=MAP + 'now read from the sketch.')
row('T43', 'T-US-STIR', t('08:35'), t('09:00'), t('09:00'), t('10:00'), INF, 'Receiving the surrender', "Orchard east of the Friends' Meeting House", pt('kcentre'), 'S21',
    'Paraphrase: Lord Stirling received their swords (S21).', 'stated', 'medium', '', ch=MAP + 'moved to the ground marked K on the sketch.')
row('T44', 'T-HE-ARTL', t('08:15'), t('08:45'), t('08:45'), t('09:30'), INF, 'Stuck and abandoned', 'Marshy ground near the creek', pt('mguns'), 'S21; S36',
    'Sketch legend M: Lossberg\'s cannons "which sunk in the morass" (S36).', 'stated', 'medium', 'Paraphrase of S21: the guns became stuck in marshy ground near the creek and were abandoned.', ch=MAP + 'read from the sketch (letter M).')
row('T45', 'T-HE-ARTK', t('08:20'), t('08:45'), t('08:45'), t('09:30'), INF, 'Stalled and abandoned', 'Near the creek', pt('creeklow'), 'S21',
    "Paraphrase: Lt. Fischer's two von Knyphausen guns were stalled near the creek; his horse was shot and the guns were later abandoned (S21).", 'stated', 'low', 'Still an estimate: the sketch shows these guns only at N, in the town (T60).')
# --- Sullivan's wing ---
row('T46', 'T-US-STARK', t('08:05'), t('08:25'), t('08:30'), t('09:00'), INF, 'Pushing through the lower town', 'Along Second Street', pt('second'), 'S21; S33',
    "Paraphrase: Stark's regiment and Moulder's battery pushed along Second Street (S21).", 'stated', 'medium', 'S33: Stark led a bayonet charge against the Knyphausen regiment.', ch=MAP + 'State Street on the current map.')
row('T47', 'T-US-MOUL', t('08:05'), t('08:25'), t('08:30'), t('09:00'), INF, 'Advancing with Stark', 'Along Second Street', pt('second'), 'S21', 'Paraphrase: as T46.', 'stated', 'medium', 'Same point as T46.', ch=MAP + 'as T46.')
row('T48', 'T-US-GLOV', t('08:10'), t('08:40'), t('09:00'), t('10:00'), INF, 'Holding the far bank', 'High ground south of the Assunpink', ln('gloverW', 'gloverE'), 'S21; S36',
    'Sketch: a bar marked Q (Sullivan) on the rising ground south of the creek (S36).', 'stated', 'medium', "Paraphrase of S21: Glover's brigade took position on the high ground south of the Assunpink.", ch=MAP + 'now the bar the sketch draws south of the creek.')
row('T49', 'T-US-STCL', t('08:25'), t('08:45'), t('09:00'), t('10:30'), INF, 'Closing on the Knyphausen regiment', 'South of the surrender ground, along today\'s East State Street', ln('xsW', 'xsE'), 'S36; S21; S22',
    'Sketch legend X: "attack at the last to K and L"; the southern line marked X (S36).', 'inferred', 'low',
    'Assumption: the sketch does not name the troops on this line. Given to St. Clair because Captain von Biesenrodt surrendered after St. Clair\'s threat (S21) and Sullivan\'s division took the southern part of town (S22).', ch=MAP + 'now the southern line marked X on the sketch.')
row('T50', 'T-HE-KNYP', t('08:30'), t('08:50'), t('08:45'), t('09:15'), INF, 'Trying for the bridge; cut off', 'Queen and Front Streets, by the Assunpink bridge', pt('qfront'), 'S21; S22; S33',
    'Paraphrase: Major von Dechow surrendered at the corner of Queen and Front Streets (S21).', 'stated', 'medium', 'S22: the regiment was hemmed in at the bridge.', ch=MAP + 'the Broad and Front Street corner on the current map.')
row('T51', 'T-HE-KNYP', t('08:45'), t('09:15'), t('09:00'), t('10:30'), 'Disputed: see TC05', 'Surrendered', 'Low ground by the Assunpink, east of Queen Street', ln('lW', 'lE'), 'S21; S33; S36',
    'Sketch legend L: "where Knyphausen surrendered" (S36).', 'stated', 'medium',
    'Paraphrase of S21: Captain von Biesenrodt surrendered after St. Clair\'s threat, about an hour after the other regiments; some tried to ford the creek and several drowned. S33 says "minutes after". Near today\'s East Front and Montgomery Streets.', ch=MAP + 'read from the sketch (letter L).')
# --- units with no position ---
row('T52', 'T-US-SARG', t('08:00'), t('08:00'), t('09:00'), t('10:00'), INF, 'In Sullivan\'s column', 'Not stated in the sources read', None, 'S21; S22', 'Paraphrase: listed in Sullivan\'s division on the River Road (S21; S22).', 'stated', 'low', 'Gap TG04.')
row('T53', 'T-US-EWING', D26, D26, D26, D26, 'S20', 'Unable to cross', 'Pennsylvania bank opposite Trenton', None, 'S20',
    'Paraphrase: Ewing was to seize the bridge over the Assunpink but could not cross because of the ice (S20).', 'stated', 'medium', 'S33: its artillery fired across the river during the battle.')
row('T54', 'T-US-CADW', D26, D26, D26, D26, 'S20', 'Crossing abandoned', 'Bristol and Dunk\'s Ferry', None, 'S20',
    'Paraphrase: Cadwalader got part of his infantry over but could not embark his artillery, and stopped (S20).', 'stated', 'medium', 'Off the battle map.')

# ---- routes: waypoints are (lat, lon) on the current street map ----
R_LAND_BEAR = [(40.29672, -74.86753), (40.29747, -74.86458), (40.29793, -74.86385), (40.30821, -74.85338), (40.30874, -74.85244), (40.30918, -74.84857)]
R_BEAR_JAC = [(40.30918, -74.84857), (40.30681, -74.84806), (40.30028, -74.84826), (40.29916, -74.84800), (40.29491, -74.84496), (40.29348, -74.84351), (40.29175, -74.84041), (40.29080, -74.84043)]
R_JAC_BIRM = [(40.29080, -74.84043), (40.28923, -74.84116), (40.28753, -74.83932), (40.28361, -74.83698), (40.28116, -74.83454), (40.27970, -74.83287), (40.27691, -74.82831), (40.27559, -74.82675),
              (40.27402, -74.82559), (40.27157, -74.82478), (40.26983, -74.82349), (40.26887, -74.82210), (40.26605, -74.81902)]
R_GREENE = [(40.26605, -74.81902), (40.26805, -74.81454), (40.27442, -74.80383), (40.27030, -74.79979), (40.26457, -74.80178), (40.26378, -74.80231), (40.24330, -74.77606), (40.24032, -74.77561), (40.23818, -74.77461), (40.23531, -74.77185)]
R_SULL = [(40.26605, -74.81902), (40.25666, -74.81597), (40.25284, -74.81521), (40.25049, -74.81385), (40.24886, -74.81219), (40.24251, -74.80730), (40.23953, -74.80314), (40.23756, -74.80316), (40.23610, -74.79869),
          (40.23228, -74.79099), (40.22790, -74.78295), (40.22760, -74.78107), (40.22689, -74.77938), (40.22459, -74.77735)]
R_PENN_IN = [(40.23531, -74.77185), (40.23470, -74.77126), (40.23219, -74.76971), (40.23163, -74.76951)]
R_PENN_TOWN = [(40.23163, -74.76951), (40.22955, -74.76879), (40.22906, -74.76852), (40.22610, -74.76491), (40.22530, -74.76455)]
R_RIVER_TOWN = [(40.22459, -74.77735), (40.22235, -74.77479), (40.22052, -74.76810), (40.22030, -74.76589), (40.21938, -74.76606), (40.21898, -74.76418), (40.21816, -74.76413)]
def W(*keys): return [(C[k][0], C[k][1]) for k in keys]
ROUTES = [
 # id, campaign, battle, unit, kind, start, end, from_pos, to_pos, waypoints, sources, wording, confidence, notes
 ('RT01', 'ARW-TP', '', 'T-US-ARMY', 'march', t('04:00'), t('06:00'), 'T02', 'T03', R_LAND_BEAR + R_BEAR_JAC[1:], 'S21; S29; S39',
  'Paraphrase: the army marched through the Bear Tavern (S21).', 'medium', 'Traced along today\'s Washington Crossing-Pennington Road and Bear Tavern Road.'),
 ('RT02', 'ARW-TP', '', 'T-US-ARMY', 'march', t('06:00'), t('06:45'), 'T03', 'T04', R_JAC_BIRM, 'S21; S28; S39', 'Paraphrase: the army marched through the Bear Tavern and Birmingham (S21).', 'medium', 'Traced along today\'s Bear Tavern Road.'),
 ('RT03', 'ARW-TP', 'TREN', 'T-US-GREENE', 'march', t('06:45'), t('07:30'), 'T04', 'T05', R_GREENE, 'S21; S22; S39',
  'Paraphrase: Greene\'s wing took the Scotch road and joined the Pennington road about a mile beyond the village (S21).', 'low',
  'Upper Ferry Road and the surviving part of Scotch Road are traced. From the south end of today\'s Scotch Road to the Pennington Road the old line is lost; that leg is a straight guess (TG02).'),
 ('RT04', 'ARW-TP', 'TREN', 'T-US-SULL', 'march', t('06:45'), t('08:00'), 'T04', 'T55', R_SULL, 'S21; S22; S39', 'Paraphrase: Sullivan\'s wing took the River road (S21).', 'medium', 'Traced along today\'s Sullivan Way and West State Street.'),
 ('RT05', 'ARW-TP', 'TREN', 'T-US-GREENE', 'attack', t('07:30'), t('07:45'), 'T05', 'T19', R_PENN_IN, 'S21; S39', 'Paraphrase: Greene\'s division forced the upper picket (S21).', 'medium', ''),
 ('RT06', 'ARW-TP', 'TREN', 'T-US-GREENE', 'attack', t('07:45'), t('08:10'), 'T19', 'T57', R_PENN_TOWN, 'S21; S23; S39',
  'Paraphrase: Greene\'s division, with Washington in the lead, occupied the high ground at the head of the town after skirmishing on the Pennington Road (S23).', 'medium', ''),
 ('RT07', 'ARW-TP', 'TREN', 'T-US-SULL', 'attack', t('08:05'), t('08:30'), 'T55', 'T56', R_RIVER_TOWN, 'S21; S22; S39',
  'Paraphrase: Sullivan\'s men pushed the Hermitage outpost back toward town and took the southern part of it (S22).', 'low', 'Which streets the column used inside the town is not stated.'),
 ('RT08', 'ARW-TP', 'TREN', 'T-HE-RALL', 'retreat', t('08:10'), t('08:25'), 'T31', 'T37', W('khanover', 'yard', 'hrallS'), 'S22; S36', 'Paraphrase: Rall and von Lossberg fell back out of the town (S22).', 'low', 'See TC08.'),
 ('RT09', 'ARW-TP', 'TREN', 'T-HE-RALL', 'attack', t('08:25'), t('08:45'), 'T37', 'T39', W('hrallN', 'iqueenS'), 'S21; S22; S36', '"Forward! Forward!" (Rall, in S22).', 'low', ''),
 ('RT10', 'ARW-TP', 'TREN', 'T-HE-RALL', 'retreat', t('08:35'), t('09:00'), 'T39', 'T41', W('iqueenN', 'hlossS', 'krallN'), 'S21; S22; S36',
  'Paraphrase: after Rall fell the troops retreated to the apple orchard at the eastern edge of the village (S22).', 'low', ''),
 ('RT11', 'ARW-TP', 'TREN', 'T-HE-PKRIV', 'escape', t('07:55'), t('08:30'), 'T08', 'T23', W('hermitage', 'riverrd', 'barracks', 'bridge'), 'S21; S20',
  'Paraphrase: those not killed or taken fled down the road toward Bordentown (S20).', 'low', 'Ends at the bridge; the road to Bordentown is off the map.'),
]

EVENTS = [
 ('TE01', 'ARW-TP', '', t('17:00', D25), t('19:00', D25), 'Crossing begins', "The army begins crossing the Delaware at McKonkey's Ferry as it grows dark.", 'T01', 'S20; S21'),
 ('TE02', 'ARW-TP', '', t('19:00', D25), t('20:00', D25), 'Alarm at Trenton', 'A party fires on the Pennington road picket on Christmas evening; the garrison turns out and the post is reinforced.', 'T06', 'S21'),
 ('TE03', 'ARW-TP', '', t('02:00'), t('03:00'), 'Crossing complete', 'The last troops and guns reach the New Jersey bank, about three hours late.', 'T01', 'S20; S21'),
 ('TE04', 'ARW-TP', '', t('04:00'), t('04:00'), 'March begins', 'The column sets off for Trenton, about nine miles away.', 'T02', 'S20'),
 ('TE05', 'ARW-TP', '', t('06:30'), t('07:00'), 'Army divides', 'At Birmingham Greene takes the upper road and Sullivan the River Road.', 'T04', 'S21; S22; S28'),
 ('TE06', 'ARW-TP', 'TREN', t('07:30'), t('08:00'), 'First shots', "Greene's advance drives in Lt. Wiederhold's picket on the Pennington Road.", 'T19; T06', 'S20; S21; S36'),
 ('TE07', 'ARW-TP', 'TREN', t('07:48'), t('08:03'), "Sullivan's attack", 'About three minutes later the lower column strikes the jäger picket at the Hermitage.', 'T22; T08', 'S20; S21'),
 ('TE08', 'ARW-TP', 'TREN', t('07:50'), t('08:10'), 'Guns open', "Forrest's and Hamilton's batteries open from the head of King and Queen Streets.", 'T24; T25', 'S21; S22; S24'),
 ('TE09', 'ARW-TP', 'TREN', t('08:10'), t('08:35'), 'Hessian guns taken', "The Rall regiment's two guns are lost on King Street, just north of the headquarters.", 'T34; T35', 'S21; S36'),
 ('TE10', 'ARW-TP', 'TREN', t('08:10'), t('08:25'), 'Line of battle', 'The three regiments form a line along the east edge of the village.', 'T37; T38; T61', 'S36'),
 ('TE11', 'ARW-TP', 'TREN', t('08:25'), t('09:00'), 'Rall shot', "Rall leads the Rall and Lossberg regiments back into the town and is mortally wounded on Queen Street.", 'T39; T40', 'S21; S22; S36'),
 ('TE12', 'ARW-TP', 'TREN', t('08:45'), t('10:00'), 'Surrender in the orchard', 'The Rall and von Lossberg regiments lay down their arms east of the town.', 'T41; T42; T43', 'S20; S21; S22; S36'),
 ('TE13', 'ARW-TP', 'TREN', t('09:00'), t('10:30'), 'Knyphausen surrenders', 'The Knyphausen regiment, cut off from the bridge, surrenders by the Assunpink.', 'T50; T51', 'S21; S33; S36'),
 ('TE14', 'ARW-TP', '', t('12:00'), t('12:00'), 'Return to Pennsylvania', 'The army starts back across the Delaware with its prisoners.', '', 'S33'),
]

CONFLICTS = [
 ('TC01', 'TREN', 'When were the first shots fired?', 'Washington: the upper division reached the advanced post "exactly at eight OClock" (S20). Stryker: about 7:45, and "nearly eight o\'clock". Lt. Piel: "shortly after half past seven" (in S21). CDB90 starts the battle at 08:00 (S34).',
  'Held as a range, 07:30 to 08:00, on T19 and event TE06.', '', 'Open', ''),
 ('TC02', 'TREN', 'When and where did the army divide?', 'A modern marker times the split at Birmingham at 7 AM (S29). The editors of Washington\'s papers have the upper division halted 500 yards from the Hessian picket around 7 a.m. (S20, note 6). The two points are more than four miles apart. S22 adds that some historians put the split at Bear Tavern.',
  'Split placed at Birmingham, 06:30 to 07:00. The 7 a.m. halt is kept as T05 with low confidence.', '', 'Open', 'Measured on the current map: Birmingham to the halt is about 6 km by the route drawn.'),
 ('TC03', 'TREN', 'How strong was the River road picket?', 'Stryker gives both "a commissioned officer and fifty men" and "a sergeant and fifteen men" (S21). The jäger company was 50 in all (S22), part of it quartered at the barracks.',
  'Strength left open on the unit record.', '', 'Open', 'Wiederhold\'s sketch, legend F: one officer and 50 jägers. That supports the larger figure, though it may count the whole company.'),
 ('TC04', 'TREN', 'How long did the fighting last?', 'CDB90: 08:00 to 09:30, ninety minutes (S34). Trenton Historical Society tour: over by 10 a.m., roughly two hours (S23). The Lossberg quartermaster: the regiment defended about two hours (in S21). S33 calls it short and gives no figure.',
  'Surrender rows end between 08:45 and 10:00.', '', 'Open', 'The sketch gives no times.'),
 ('TC05', 'TREN', 'How long after the others did the Knyphausen regiment surrender?', 'Stryker: Captain von Biesenrodt surrendered "about an hour after the other regiments" (S21, as summarised). Wikipedia, citing Wood 2003: "minutes after the rest of the brigade" (S33).',
  'T51 runs from 08:45-09:15 to 09:00-10:30.', '', 'Open', 'The sketch gives separate surrender places (K and L) about 450 m apart, but no times.'),
 ('TC06', 'TREN', 'How many Hessians were there, and how many were taken?', 'Garrison: about 1,400 (S22; S33), 1,500 (S35, from the Park Service), 1,520 (S34). Prisoners: 23 officers and 886 men (Washington, S20); 918 on the enclosed return (S20, note 15); 868 on the Hessian officers\' list (S21); 896 (S33, citing Fischer). CDB90 counts 996 Hessian casualties in all (S34).',
  'All figures recorded on the unit and battle records; none chosen.', '', 'Open', ''),
 ('TC07', 'TREN', 'How strong was the Crosswicks detachment?', 'Stryker gives three officers and 100 men in one place and four officers and 82 men in another (S21).', 'Left open; the detachment took no part.', '', 'Open', ''),
 ('TC08', 'TREN', 'Where did the Rall and Lossberg regiments go when they left King Street?', 'The 1929 history: they fell back to "The Swamp", north of Perry Street between Stockton and Montgomery (S22). Wikipedia, citing Fischer: "a field outside town", then a final attack, then the orchard (S33). Stryker places the surrender in the orchard east of the Friends\' Meeting House (S21).',
  'Sequence used: formed in the town, line of battle on the east edge, counter-attack to King and Queen Streets, surrender east of the town.', '', 'Open',
  'Largely settled by the sketch. It draws a line of battle (H) along today\'s Montgomery Street, the attack into the town (I) on King and Queen Streets, and the surrender ground (K) between Montgomery and Stockton Streets at Perry Street. That is the block the 1929 history calls the Swamp, and about 110 m from the Friends\' Meeting House. The three descriptions are one place.'),
 ('TC09', 'TREN', 'What were the American losses?', 'Washington: two officers and one or two privates wounded (S20). Tilghman: two officers slightly wounded, two privates killed and two wounded (S20, note 9). Wikipedia, citing Fischer: two died of exposure on the march and five were wounded (S33). CDB90: 12 (S34).',
  'Not used in position data.', '', 'Open', ''),
 ('TC10', 'TREN', 'How strong were the pickets?', 'Pennington road: an officer, an NCO and 19 men (S21); 1 officer and 25 privates (sketch, A). Maidenhead road: about 70 men (S21); 1 captain, 1 officer and 75 men (sketch, D). Ferry: 1 officer and 27 men (S21); 1 officer and 30 privates (sketch, E).',
  'Both figures recorded; none chosen. Wiederhold commanded the Pennington road picket himself.', '', 'Open', 'New in v4.'),
 ('TC11', 'TREN', 'Which regiment was where at G and I?', 'The sketch marks three forming places (G) and two attack positions (I) without naming the regiment at each. Stryker has the Rall regiment forming on King Street at Pinkerton\'s alley, about 150 m west of the nearest G, and Rall shot on Queen Street. Wikipedia, citing Wood, has Rall\'s regiment advancing up King Street and Lossberg up Queen Street.',
  'Rall regiment: formed at King Street and Pinkerton\'s alley (Stryker); counter-attack on Queen Street, where Rall fell. Lossberg: formed behind the church; counter-attack on King Street. Knyphausen: formed at the southern G.', '', 'Open', 'New in v4. The Hessian court of inquiry testimony, printed in Stryker, should settle it.'),
 ('TC12', 'TREN', 'Where did Stirling\'s brigade go?', 'Wikipedia, citing Wood: Weedon\'s men advanced down King Street after the guns were taken (S33). The sketch draws Stirling\'s bars (T) just east of Queen Street, from Third Street to Front Street. Stryker: Stirling received the surrender in the orchard.',
  'T36 uses the sketch line east of Queen Street.', '', 'Open', 'New in v4. A brigade could have done both; the sketch shows one moment.'),
]

GAPS = [
 ('TG01', 'TREN', 'Only one period map has been read, and it is a sketch', 'Wiederhold drew from memory as a prisoner, not from a survey. Inside the town centre it fits the current street map to 10-28 m on six points. North of the English Church it is compressed to about half scale, and outside the town it is not to scale at all.',
  'Read Faden\'s 1777 plan (S37) and Fischer\'s plan (S38) and compare. Georeference the sketch in Allmaps with more control points.'),
 ('TG02', 'TREN', 'Some outposts and one road are still approximate', 'The Pennington road picket and the Maidenhead road picket are scaled from the sketch (200 to 250 m). The ferry picket is an estimate. The old line of the Scotch Road south of today\'s road is lost, so that leg of Greene\'s route is a straight guess.',
  'Stryker\'s map of the outposts (his illustration no. 55); an 18th- or 19th-century road map of Ewing Township.'),
 ('TG03', 'TREN', 'American order of battle is incomplete', 'Brigades and batteries are named, but regiments and brigade strengths are missing. The Wikipedia order-of-battle tables did not come through legibly.',
  'Stryker\'s appendices and Wright, The Continental Army (1983).'),
 ('TG04', 'TREN', 'Five American units have no position during the attack', 'Sargent\'s brigade and the batteries of Bauman, Neil, Hugg and Sargent cannot be drawn.', 'Stryker pp. 150-190, read in full; the Hessian court of inquiry.'),
 ('TG05', 'TREN', 'Two assignments on the sketch are assumptions', 'The sketch does not name the troops on the southern line marked X (given here to St. Clair) or separate de Fermoy from Stephen (the far eastern bar marked S is given here to de Fermoy). Both rows are marked "inferred".',
  'Stryker pp. 160-190 and the American accounts he prints.'),
 ('TG06', 'TREN', 'Stryker was read through an automated summary', 'The book\'s text was read in four 100,000-character sections through a summarising tool. Page numbers are approximate, and wording marked "Paraphrase" is not a quotation.',
  'Check each paraphrased row against the page images before it is accepted.'),
 ('TG07', 'TREN', 'Almost no clock times inside the battle', 'Between the first shots and the surrender the sources read give no times, and the sketch gives none. Every start and end in that stretch is an inferred range.',
  'Wiederhold\'s and Piel\'s diaries and the court of inquiry testimony, which Stryker prints.'),
 ('TG08', 'TREN', 'Hessian written accounts not read directly', 'Wiederhold\'s diary, Piel and the court of inquiry are used only as Stryker reports them. Wiederhold\'s sketch has now been read directly.', 'Read Stryker\'s appendices; then the published translations.'),
 ('TG09', 'TREN', 'Escape routes are not drawn', 'The dragoons, most of the jägers and several hundred others got away over the bridge toward Bordentown or through the woods toward Princeton. Only the jäger picket\'s route is in the data.', 'Stryker pp. 188-195.'),
 ('TG10', 'TREN', 'Clock time is local time', 'There was no standard time in 1776 or 1863. All times are as the sources give them.', 'Keep as stated; note it wherever times from different places are compared.'),
 ('TG11', 'TREN', 'The sketch legend was read by eye', 'Wiederhold\'s handwriting and English are irregular. The legend entries quoted here are my reading of the scan.', 'Compare with the Library of Congress catalogue transcription or a published one.'),
]

SOURCES = [
 ('S20', 'Washington to John Hancock, 27 December 1776', 'George Washington', '1776-12-27', 'Primary: commander\'s report', 'Papers of George Washington, Revolutionary War Series, vol. 7; Founders Online', 'yes (online text)', 'https://founders.archives.gov/documents/Washington/03-07-02-0355', 'Letter text public domain. Editors\' notes are modern: facts only', 'Read through a summarising tool; three phrases returned verbatim.', 'TREN'),
 ('S21', 'The Battles of Trenton and Princeton', 'William S. Stryker', '1898', 'Early secondary, printing primary documents', 'Boston: Houghton, Mifflin, 1898. Pages 84-233 read', 'no (see TG06)', 'https://archive.org/details/BattlesOfTrentonAndPrinceton', 'Public domain', 'The main written source. Prints Hessian diaries and the court of inquiry. Read in sections through a summarising tool.', 'TREN'),
 ('S22', 'A History of Trenton 1679-1929, chapter 3: The Two Battles of Trenton', 'Trenton Historical Society', '1929', 'Early secondary', 'Princeton University Press, 1929, pp. 3-14 of the chapter PDF', 'yes (PDF pages)', 'https://trentonhistory.org/wp-content/uploads/History-of-Trenton-1679-1929-Ch3-Two-Battles-of-Trenton.pdf', 'Published 1929; public domain in the US as far as I know', '', 'TREN'),
 ('S23', 'Battles of Trenton tour script', 'Trenton Historical Society', 'modern', 'Modern secondary: tour guide', '', 'n/a', 'https://www.trentonhistory.org/Tour/Battles_of_Trenton_Script.pdf', 'Facts only', 'Ties 1776 street names to today\'s.', 'TREN'),
 ('S24', 'Marker: Trenton Battle Monument', 'Trenton Bicentennial Committee', 'not stated', 'Reference: coordinates', 'Historical Marker Database, m=4151', 'n/a', 'https://www.hmdb.org/m.asp?m=4151', 'Facts only', '40 13.545 N, 74 45.887 W. Its text dates the battle 25 December.', 'TREN'),
 ('S25', 'Marker: Headquarters of Colonel Johann Gottlieb Rall', 'Cathedral Corporation', '1919', 'Reference: coordinates', 'Historical Marker Database, m=3796', 'n/a', 'https://www.hmdb.org/m.asp?m=3796', 'Facts only', '40 13.349 N, 74 45.952 W. 151 North Warren Street.', 'TREN'),
 ('S26', 'Marker on St. Michael\'s Church: Route Taken by Washington', 'Sons of the American Revolution', '1914', 'Reference: coordinates', 'Historical Marker Database, m=3790', 'n/a', 'https://www.hmdb.org/m.asp?m=3790', 'Facts only', '40 13.332 N, 74 45.931 W. Used only for the church\'s position.', 'TREN'),
 ('S27', 'Marker: The Christmas Night Crossing', '', 'modern', 'Reference: coordinates', 'Historical Marker Database, m=7274', 'n/a', 'https://www.hmdb.org/m.asp?m=7274', 'Facts only', '40 17.803 N, 74 52.052 W. New Jersey bank.', 'TREN'),
 ('S28', 'Marker: An Historic Crossroad', '', 'modern', 'Reference: coordinates', 'Historical Marker Database, m=9877', 'n/a', 'https://www.hmdb.org/m.asp?m=9877', 'Facts only', '40 15.963 N, 74 49.141 W. Birmingham crossroads.', 'TREN'),
 ('S29', 'Marker: Washington\'s March to Trenton', '', 'modern', 'Modern secondary: marker with timeline', 'Historical Marker Database, m=94734', 'n/a', 'https://www.hmdb.org/m.asp?m=94734', 'Facts only', '40 17.448 N, 74 50.426 W. Gives clock times with no source.', 'TREN'),
 ('S30', 'Marker: Old Barracks', '', 'not stated', 'Reference: coordinates', 'Historical Marker Database, m=3756', 'n/a', 'https://www.hmdb.org/m.asp?m=3756', 'Facts only', '40 13.169 N, 74 46.11 W.', 'TREN'),
 ('S31', 'Marker: The Second Battle of Trenton', '', 'modern', 'Reference: coordinates', 'Historical Marker Database, m=189472', 'n/a', 'https://www.hmdb.org/m.asp?m=189472', 'Facts only', 'No longer used for a coordinate in v4; the street corner comes from S39.', 'TREN'),
 ('S32', 'Trenton Revolutionary War sites', 'revolutionarywarnewjersey.com', 'modern', 'Reference: addresses', '', 'n/a', 'https://revolutionarywarnewjersey.com/new_jersey_revolutionary_war_sites/towns/trenton_nj_revolutionary_war_sites.htm', 'Facts only', 'Street addresses of surviving sites.', 'TREN'),
 ('S33', 'Battle of Trenton', 'Wikipedia', 'modern', 'Modern tertiary: cross-check', 'Cites Fischer, Washington\'s Crossing (2004) and Wood, Battles of the Revolutionary War (2003)', 'no', 'https://en.wikipedia.org/wiki/Battle_of_Trenton', 'Facts only', 'No longer the only source for any position in v4.', 'TREN'),
 ('S34', 'CDB90: CAA Database of Battles, 1990 (open edition)', 'US Army Concepts Analysis Agency; ed. J. B. Arnold', '1990; 2026', 'Dataset: battle level', 'Battles 85 (Trenton) and 199 (Gettysburg)', 'n/a', 'https://github.com/jrnold/CDB90', 'Data CC0', 'Times, strengths, frontage, Wikidata links.', 'TREN; GETT'),
 ('S35', 'The War Atlas open dataset', 'Purcell Analytics', '2026-07', 'Dataset: battle level', 'Records trenton_b and gettysburg_b', 'n/a', 'https://github.com/Purcell-Analytics/war_atlas_data', 'CC BY 4.0: credit required', 'Wikidata IDs and strength figures.', 'TREN; GETT'),
 ('S36', 'Sketch of the engagement at Trenton, given on the 26th of December 1776', 'Lt. Andreas Wiederhold, von Knyphausen regiment', '1776', 'Primary: participant\'s map', 'Library of Congress, Geography and Map Division, G3814.T7 (ar126700); scan supplied by Morgan, 4,454 x 2,886 pixels', 'yes (scan)', 'https://www.loc.gov/item/gm71002184/', 'Public domain', 'USED in v4. Legend letters A to X read by eye. A sketch, not a survey: see the Georeference sheet and TG01.', 'TREN'),
 ('S37', 'Plan of the operations of General Washington against the King\'s troops in New Jersey', 'William Faden', '1777', 'Primary-era map', 'London, 1777. Library of Congress, 74692205', 'no', 'https://www.loc.gov/item/74692205/', 'Public domain', 'NOT YET USED. Covers Trenton and Princeton.', 'TREN'),
 ('S38', 'Plan of the affair at Trenton, 26 December 1776', 'Lt. Fischer (Hessian artillery)', '1776-77', 'Primary: participant\'s map', 'Seen only as a search result; not examined', 'no', 'https://jetty.klnpa.org/islandora/47515', 'Not checked', 'NOT YET USED. Attribution unverified.', 'TREN'),
 ('S39', 'OpenStreetMap: streets, roads and waterways of Trenton and Ewing', 'OpenStreetMap contributors', '2026-11-13', 'Current map data', 'Overpass API extract, 13 Nov 2026 (UTC): 188 ways, simplified', 'n/a', 'https://www.openstreetmap.org/copyright', 'Open Database License: credit "© OpenStreetMap contributors"', 'Used for street-corner coordinates, the march routes and the current-map view of the playback.', 'TREN'),
]

# sketch <-> current map fit, for the Georeference sheet
SKETCH_FIT = dict(scale=0.689, rot=-4.4, points=[
 ('Queen and Second Streets (Broad and State)', 2290, 1125, 40.22015, -74.76421, 19), ('King and Second Streets (Warren and State)', 2095, 1125, 40.22030, -74.76589, 11),
 ('Queen and Third Streets (Broad and East Hanover)', 2290, 990, 40.22096, -74.76425, 23), ('King and Third Streets (Warren and East Hanover)', 2095, 990, 40.22104, -74.76577, 10),
 ('English Church (St. Michael\'s)', 2190, 850, 40.22220, -74.76535, 28), ('Queen Street bridge over the Assunpink', 2265, 1490, 40.21816, -74.76413, 13)])
