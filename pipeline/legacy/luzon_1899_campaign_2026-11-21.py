"""21 Nov 2026 (Morgan: "do the entire year"): the 1899 campaign in central and northern Luzon as one day-by-day playback,
luzon1899, from the outbreak at Manila on 4 Feb to mid-December (the pursuit of Aguinaldo into the mountains of Lepanto).

Adds to the master workbook: Sources S74-S76, Units and Assignments for the columns, Positions (all "Needs review"),
Tracks, Events, week Summaries, Labels, two Maps (fitted by pipeline/georef/luzon_georef.py), the Playbacks row and settings,
Conflicts and Gaps. Run once; it refuses to run twice.

Every position is a column or headquarters placed at a town the report names, at that town's present-day coordinates (Wikidata,
read 21 Nov 2026): good to a kilometre or two, which is what these 1:264,000 to 1:610,000 maps and "reached Tayug on November 15"
support. Sources read: Otis's report of 1899 (S65), pp. 171-203; Otis's report of 1900 (S74), the telegrams of Oct-Dec 1899;
Batson's report in part 5 (S75); the engagement dates printed on Young's map (S71); and the Philippine Information Society
pamphlet (S68, partisan) where it prints Young's and March's reports, which were not found in the volumes read.
"""
import copy, datetime, json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'georef'))
import luzon_georef as LG
import manila_georef as MG
import openpyxl

WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx')
wb = openpyxl.load_workbook(WB)
assert not any(r[0].value == 'luzon1899' for r in wb['Playbacks'].iter_rows(min_row=2)), 'already applied'
T0, T1 = '1899-02-04', '1899-12-15'


def head(ws): return [c.value for c in ws[1]]


def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r


def add(sheet, values):
    ws = wb[sheet]; h = head(ws); src = last_row(ws); r = src + 1
    for k in values: assert k in h, '%s has no column %r' % (sheet, k)
    for j in range(1, len(h) + 1):
        s = ws.cell(src, j)
        if s.has_style: ws.cell(r, j)._style = copy.copy(s._style)
    for k, v in values.items(): ws.cell(r, h.index(k) + 1).value = v
    return r


def day(s, n=0): return (datetime.date.fromisoformat(s) + datetime.timedelta(days=n)).isoformat()


# ---------------------------------------------------------------- places: (lat, lon, class). c = church or town centre; r = rounded town coordinates; x = rough
_ch = MG.px2ll(3190, 2850)
PL = {
    'Chinese Hospital (La Loma), Manila': (round(float(_ch[0]), 4), round(float(_ch[1]), 4), 'c'), 'Manila': (14.5958, 120.9772, 'c'),
    'Caloocan': (14.6517, 120.9728, 'c'), 'Polo': (14.7072, 120.9472, 'c'), 'Malolos': (14.8423, 120.8116, 'c'), 'Calumpit': (14.9161, 120.7690, 'c'),
    'San Fernando (Pampanga)': (15.0284, 120.6931, 'c'), 'Angeles': (15.1343, 120.5903, 'c'), 'Mabalacat': (15.2167, 120.5833, 'r'),
    'Bamban': (15.2742, 120.5669, 'c'), 'Tarlac': (15.4877, 120.5880, 'c'), 'Gerona': (15.6069, 120.5986, 'c'), 'Moncada': (15.7331, 120.5725, 'c'),
    'Bayambang': (15.8086, 120.4556, 'c'), 'Dagupan': (16.0423, 120.3344, 'c'), 'San Fabian': (16.15, 120.45, 'r'), 'San Jacinto': (16.0725, 120.4411, 'c'),
    'Pozorrubio': (16.1167, 120.55, 'r'), 'Rosario (La Union)': (16.2333, 120.4833, 'r'), 'Tubao': (16.3479, 120.4128, 'c'), 'Aringay': (16.3982, 120.3555, 'c'),
    'San Fernando (La Union)': (16.6157, 120.3179, 'c'), 'Balaoan': (16.8211, 120.4033, 'c'), 'Namacpacan (Luna)': (16.8533, 120.3760, 'c'),
    'Tagudin': (16.9361, 120.4464, 'c'), 'Candon': (17.1933, 120.4492, 'c'), 'Narvacan': (17.4185, 120.4767, 'c'), 'Vigan': (17.5748, 120.3890, 'c'),
    'Tirad Pass': (17.15, 120.6333, 'x'), 'Angaqui (Quirino, Ilocos Sur)': (17.1383, 120.6764, 'x'), 'Cervantes': (16.9917, 120.7333, 'r'),
    'Cayan (Kayan, Tadian)': (16.9961, 120.8208, 'x'), 'Pasig': (14.5605, 121.0765, 'c'), 'Santa Cruz (Laguna)': (14.2833, 121.4167, 'r'),
    'Norzagaray': (14.9167, 121.05, 'r'), 'Baliuag': (14.9555, 120.9004, 'c'), 'San Miguel (Bulacan)': (15.1409, 120.9760, 'c'),
    'San Isidro': (15.3077, 120.9066, 'c'), 'Arayat': (15.1514, 120.7730, 'c'), 'Candaba': (15.0918, 120.8280, 'c'), 'Cabiao': (15.2496, 120.8588, 'c'),
    'Santa Rosa': (15.4232, 120.9376, 'c'), 'Cabanatuan': (15.4892, 120.9642, 'c'), 'Talavera': (15.5844, 120.9192, 'c'), 'Tayug': (16.0267, 120.7478, 'c'),
    'San Nicolas (Pangasinan)': (16.0690, 120.7620, 'c'), 'Binalonan': (16.05, 120.6, 'r'), 'Bayombong': (16.4839, 121.1510, 'c'),
    'Alcala (Cagayan)': (17.9031, 121.6556, 'x'), 'Aparri': (18.3667, 121.6333, 'r'), 'San Jose (Nueva Ecija)': (15.7922, 120.9895, 'c'),
    'Tuguegarao': (17.6135, 121.7305, 'c'), 'Laoag': (18.1938, 120.5940, 'c'),
}
PREC = {'c': (1500, 'medium', 'The town the report names, at the coordinates of its church or centre on Wikidata (S73). The column was at or about the town, not on the spot.'),
        'r': (2500, 'low', 'The town the report names, at its coordinates on Wikidata (S73), which are rounded to about a kilometre.'),
        'x': (5000, 'low', 'A rough place: see the notes. Coordinates from Wikidata (S73) for the nearest named feature.')}

# ---------------------------------------------------------------- sources
SH = ['source_id', 'title', 'author', 'date', 'type', 'citation', 'page verified?', 'url', 'rights', 'notes', 'used_for', 'kind', 'rights_status', 'may_host', 'rights_checked', 'site']
for s in [
    ('S74', 'Report of Maj. Gen. E. S. Otis, U.S. Army, commanding Division of the Philippines, military governor: September 1, 1899, to May 5, 1900', 'Maj. Gen. Elwell S. Otis', '1900',
     "Primary: commander's report, with the telegrams", 'Annual Reports of the War Department for the fiscal year ended June 30, 1900, vol. 1, part 4 (Report of the Lieutenant-General Commanding the Army). Washington, GPO, 1900. University of Michigan copy, Internet Archive annualreportswa82deptgoog.',
     'no (read in the text file; the scan is poor, so quotations are cleaned by eye)', 'https://archive.org/details/annualreportswa82deptgoog', 'Public domain (US government work, 1900)',
     'USED from 21 Nov 2026 for the fall campaign: the telegrams between Manila and Lawton, MacArthur, Wheaton and Young, Oct-Dec 1899. Several telegram dates are blurred in the scan; each row says where.',
     'PHW-FALL99; PHW-YOUNG', 'official report', 'public domain (US)', 'yes', 'yes', 'archive.org'),
    ('S75', 'Reports of subordinate officers, Division of the Philippines, 1899-1900 (including Maj. M. A. Batson, Macabebe scouts)', 'US War Department', '1900',
     'Primary: reports of subordinate officers', 'Annual Reports of the War Department for the fiscal year ended June 30, 1900, vol. 1, part 5. Washington, GPO, 1900. University of Michigan copy, Internet Archive annualreportswa50deptgoog.',
     'no (read in the text file)', 'https://archive.org/details/annualreportswa50deptgoog', 'Public domain (US government work, 1900)',
     "USED from 21 Nov 2026: Batson's report for 13-19 Nov 1899 (Tayug to Aringay), and Lt. Col. Parker's report of the Navy's landing at Vigan. Young's and March's own reports were not found in it.",
     'PHW-YOUNG', 'official report', 'public domain (US)', 'yes', 'yes', 'archive.org'),
    ('S76', 'Natural Earth, 1:10m: land, roads, railroads, rivers, lakes', 'Natural Earth', '2026-11-21', 'Current map data',
     'naturalearthdata.com; files from github.com/nvkelso/natural-earth-vector (geojson), downloaded 21 Nov 2026.', 'n/a', 'https://www.naturalearthdata.com/', 'Public domain',
     'USED for the current-map drawing under the Luzon 1899 playback (data/osm/luzon1899.txt, data/base/luzon1899.json): OpenStreetMap could not be downloaded for the whole island.',
     'PHW-LUZ99', 'reference', 'public domain', 'yes', 'yes', 'naturalearthdata.com'),
]:
    v = dict(zip(SH, s)); v['war'] = 'PHW'; add('Sources', v)

_S = wb['Sources']; _h = head(_S)
for _r in _S.iter_rows(min_row=2):
    if _r[0].value == 'S73': _r[_h.index('title')].value = 'Wikidata: coordinates of churches, towns and landmarks in Manila and Luzon'
    if _r[0].value in ('S69', 'S71'):
        f = LG.Fit('siebert' if _r[0].value == 'S69' else 'young').summary()
        _r[_h.index('notes')].value = str(_r[_h.index('notes')].value).replace('Not yet fitted.', 'USED from 21 Nov 2026 as a period map of the Luzon 1899 playback: fitted on %d towns, RMS %d m, worst %d m (pipeline/georef/luzon_georef.py). A reduced copy is in the repository; the full scan is streamed from the library.' % (f['points'], f['rms_m'], f['max_m']))
# ---------------------------------------------------------------- units
US, PH = 'PHW-US', 'PHW-PH'
UNITS = [
    ('LZ-US-WHE-PB', "Wheaton's provisional brigade (Pasig expedition, March 1899)", 'Wheaton (Pasig)', US, 'Infantry', 'Brigade', 'S65',
     'S65 p. 185: 20th and 22nd Infantry, three troops 4th Cavalry, a section of Light Battery D, 6th Artillery, two battalions 1st Washington, seven companies 2nd Oregon.'),
    ('LZ-US-KOBBE', "Kobbe's column (Rio Grande, May 1899)", 'Kobbe', US, 'Infantry', 'Brigade', 'S65', 'Maj. William A. Kobbe, 3rd Artillery. Its make-up was not read. Echelon is a drawing choice.'),
    ('LZ-US-YOUNG', "Young's provisional cavalry brigade (fall campaign of 1899)", 'Young', US, 'Cavalry', 'Brigade', 'S74; S71; S75',
     'S71 lists: 4th Cavalry, 3rd Cavalry, Scott\'s battery of the 37th Volunteer Infantry, Ballance\'s battalion of the 22nd Infantry, 24th Infantry, 33rd Volunteer Infantry, Penn\'s battalion of the 34th, Castner\'s scouts, Macabebe scouts, Dorrington\'s scouts.'),
    ('LZ-US-WHE-X', "Wheaton's expedition (San Fabian, November 1899)", 'Wheaton', US, 'Infantry', 'Brigade', 'S74', '13th Infantry and 33rd Volunteer Infantry are named with it in S74; its full make-up was not read.'),
    ('LZ-US-33', '33rd Infantry, US Volunteers', '33 Inf', US, 'Infantry', 'Regiment', 'S74', 'Col. Luther R. Hare (S74: "Colonel Hare commanding").'),
    ('LZ-US-MARCH', "March's battalion, 33rd Infantry, US Volunteers", 'March', US, 'Infantry', 'Battalion', 'S74; S68', 'Maj. Peyton C. March. S74: Young "had sent Major March\'s battalion of the Thirty-third Infantry into the mountains eastward in pursuit of Aguinaldo".'),
    ('LZ-US-BATCH', "Batchelor's battalion, 24th Infantry, with Castner's scouts", 'Batchelor', US, 'Infantry', 'Battalion', 'S74', 'Capt. Joseph B. Batchelor, 24th Infantry. S74: "three companies Twenty-fourth and Castner\'s scouts".'),
    ('LZ-PH-GOV', 'Aguinaldo and the government of the Philippine Republic', 'Aguinaldo', PH, 'Infantry', 'Headquarters', 'S65; S74; S68',
     'The seat of government and, from 13 Nov, Aguinaldo\'s own party. The American reports are the only sources read for where it was.'),
    ('LZ-PH-NORTH', 'Filipino army on the railway north of Manila (Lt. Gen. Antonio Luna commanding, to May 1899)', 'Army on the railway', PH, 'Infantry', 'Army', 'S65; S74',
     'Strengths are American estimates: about 4,000 at Caloocan (10 Feb) and at Calumpit (28 Apr); about 3,000 retiring on Tarlac (18 May). Who commanded after May is not in the sources read.'),
    ('LZ-PH-EAST', 'Filipino forces on the Baliuag-San Miguel line (April-May 1899)', 'Baliuag force', PH, 'Infantry', 'Brigade', 'S65',
     'S65: 3,000 "held at Baliuag" (28 Apr); "Generals Pilar and Geronimo" reported at San Miguel (11 May). Echelon is a drawing choice.'),
    ('LZ-PH-SJ', 'Filipino force at San Jacinto (November 1899)', 'San Jacinto force', PH, 'Infantry', 'Brigade', 'S74', 'S74: "1,200 insurgents near San Jacinto". Its commander is not in the sources read.'),
    ('LZ-PH-TINIO', "Tinio's force on the Ilocos coast (November-December 1899)", 'Tinio', PH, 'Infantry', 'Brigade', 'S68; S74',
     'Gen. Manuel Tinio. S68 (Young\'s report): "a retarding force of 600" at Tagudin.'),
    ('LZ-PH-ARI', 'Filipino force on the Aringay River (19 November 1899)', 'Aringay force', PH, 'Infantry', 'Detachment', 'S75', 'S75 (Batson): "an intrenched force of insurgents on the opposite bank". Its strength and commander are not in the sources read. Echelon is a drawing choice.'),
    ('LZ-PH-PILAR', "Del Pilar's rear guard at Tirad Pass", 'Del Pilar', PH, 'Infantry', 'Detachment', 'S68; S74; S71', 'Gen. Gregorio del Pilar, killed 2 Dec 1899. S68 (March\'s report): "a picked force from Aguinaldo\'s body guard".'),
]
UH = ['unit_id', 'unit_name', 'map_label', 'side_id', 'branch', 'echelon', 'source_ids', 'notes']
for u in UNITS:
    v = dict(zip(UH, u)); v['nation'] = 'United States' if u[3] == US else 'Philippines'; v['sourced?'] = 'yes'; add('Units', v)

AS = [
    ('PH-US-CORPS', None, 'Maj. Gen. Elwell S. Otis', '1899-03-01', '1899-12-31', 'S65; S74', None),
    ('PH-US-2DIV', 'PH-US-CORPS', 'Maj. Gen. Arthur MacArthur', '1899-03-01', '1899-12-31', 'S65; S74', None),
    ('PH-US-1DIV', 'PH-US-CORPS', 'Maj. Gen. Thomas M. Anderson', '1899-03-01', '1899-03-16', 'S65', None),
    ('PH-US-1DIV', 'PH-US-CORPS', 'Maj. Gen. Henry W. Lawton', '1899-03-17', '1899-12-18', 'S65; S74', 'S65 p. 186: "New military combinations were made on March 17, General Lawton relieving Major General Anderson". In the field he led a column, not the whole division.'),
    ('LZ-US-WHE-PB', 'PH-US-CORPS', 'Brig. Gen. Loyd Wheaton', '1899-03-10', '1899-03-17', 'S65', None),
    ('LZ-US-KOBBE', 'PH-US-CORPS', 'Maj. William A. Kobbe, 3rd Artillery', '1899-05-06', '1899-05-31', 'S65', None),
    ('LZ-US-YOUNG', 'PH-US-1DIV', 'Brig. Gen. Samuel B. M. Young', '1899-10-01', '1899-12-31', 'S74; S71', 'S74: reported late in July, given the 3rd Brigade, First Division, and sent to San Fernando "to form a provisional brigade to be attached to General Lawton\'s division".'),
    ('LZ-US-WHE-X', 'PH-US-CORPS', 'Brig. Gen. Loyd Wheaton', '1899-11-06', '1899-12-31', 'S74', None),
    ('LZ-US-33', 'LZ-US-WHE-X', 'Col. Luther R. Hare', '1899-11-07', '1899-12-31', 'S74', None),
    ('LZ-US-MARCH', 'LZ-US-YOUNG', 'Maj. Peyton C. March', '1899-11-30', '1899-12-31', 'S74; S68', 'Came from Wheaton\'s column; with Young from late November (S74).'),
    ('LZ-US-BATCH', 'LZ-US-YOUNG', 'Capt. Joseph B. Batchelor', '1899-11-20', '1899-12-31', 'S74', None),
    ('LZ-PH-GOV', None, 'Emilio Aguinaldo, President', '1899-02-04', '1899-12-31', 'S65; S74', None),
    ('LZ-PH-NORTH', 'LZ-PH-GOV', 'Lt. Gen. Antonio Luna', '1899-02-10', '1899-05-18', 'S65', 'S65 names Luna with this army from 10 Feb to 18 May 1899. Later commanders are not in the sources read.'),
    ('LZ-PH-EAST', 'LZ-PH-GOV', 'Generals Pilar and Geronimo (reported, 11 May)', '1899-04-28', '1899-05-16', 'S65', None),
    ('LZ-PH-SJ', 'LZ-PH-GOV', None, '1899-11-09', '1899-11-11', 'S74', None),
    ('LZ-PH-TINIO', 'LZ-PH-GOV', 'Gen. Manuel Tinio', '1899-11-22', '1899-12-04', 'S68; S74', None),
    ('LZ-PH-ARI', 'LZ-PH-GOV', None, '1899-11-19', '1899-11-19', 'S75', None),
    ('LZ-PH-PILAR', 'LZ-PH-GOV', 'Gen. Gregorio del Pilar', '1899-11-28', '1899-12-02', 'S68; S74', None),
]
AH = ['unit_id', 'parent_unit_id', 'commander', 'valid_from', 'valid_to', 'source_ids', 'notes']
n = max(int(str(r[0].value)[1:]) for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value and str(r[0].value)[1:].isdigit())
for a in AS:
    n += 1; v = dict(zip(AH, a)); v['assign_id'] = 'A%03d' % n; add('Assignments', v)

# ---------------------------------------------------------------- positions
# (track, unit, battle, start_earliest, start_latest, show_from, place, activity, sources, wording, method, confidence, time basis, notes)
O65 = 'Otis 1899 (S65)'
R = []


def p(track, unit, battle, se, sl, show, place, act, src, wording, method='stated', conf='medium', tb='', notes=''):
    R.append(dict(track=track, unit=unit, battle=battle, se=se, sl=sl, show=show, place=place, act=act, src=src, wording=wording, method=method, conf=conf, tb=tb, notes=notes))


D = '1899-'
MN, ML, LW, FA, YO = 'PHW-MNL-AFTER', 'PHW-MALOLOS', 'PHW-LAWTON', 'PHW-FALL99', 'PHW-YOUNG'
add('Battles', {'battle_id': 'PHW-MNL-AFTER', 'campaign_id': 'PHW-LUZ99', 'name': 'Operations around Manila, February-March 1899 (Caloocan, the Pasig line)', 'start_earliest': '1899-02-06', 'start_latest': '1899-02-06',
                'end_earliest': '1899-03-17', 'end_latest': '1899-03-17', 'notes': 'Added 21 Nov 2026 for the Luzon 1899 playback: the weeks between the battle of Manila (PHW-MNL, which has its own playback) and the advance on Malolos. S65 pp. 171-186.'})
# --- MacArthur's Second Division
p('L-MAC', 'PH-US-2DIV', MN, D+'02-04', D+'02-04', D+'02-04', 'Chinese Hospital (La Loma), Manila', 'Holding the line north of the Pasig after the battle of 4-5 February', 'S65',
  'S65 p. 171: "The northern line had a sharp protruding angle at the Chinese church, one and one-quarter miles southeast of Caloocan, thence it extended southeasterly towards the Deposito"',
  tb='Dates only. For 4-5 February hour by hour, see the Manila playback.')
p('L-MAC', 'PH-US-2DIV', MN, D+'02-10', D+'02-10', D+'02-10', 'Caloocan', 'Took Caloocan (H. G. Otis\'s brigade); line with its left on the town', 'S65',
  'S65 pp. 171-172: he "was directed to rectify his alignment, which he accomplished on the afternoon of the 10th by a very spirited attack"; "the line, with the left resting on Caloocan was occupied"', conf='high', tb='Date stated.')
p('L-MAC', 'PH-US-2DIV', ML, D+'03-26', D+'03-27', D+'03-27', 'Polo', 'Advance on Malolos: drove the Filipino army from Polo', 'S65',
  'S65 pp. 187-188: the troops "very early the next morning [25 March] proceeded on their march"; the enemy was driven "northward and beyond Polo, where he made a determined stand the following day, from which he was driven by General MacArthur\'s united troops"',
  tb='The report counts days from the start on 25 March: the Tulihan River on the 25th-26th, Polo the day after. 27 March is that count, not a stated date.')
p('L-MAC', 'PH-US-2DIV', ML, D+'03-31', D+'03-31', D+'03-31', 'Malolos', 'Entered Malolos, the Republic\'s capital, found burning', 'S65',
  'S65 p. 188: "Our troops entered Malolos, the insurgent capital, March 31. That alleged government had removed all its records and property, and its army set fire to the city when it retreated on Calumpit and Quingua"', conf='high', tb='Date stated.')
p('L-MAC', 'PH-US-2DIV', ML, D+'04-25', D+'04-28', D+'04-28', 'Calumpit', 'Forced the Bagbag and the Rio Grande at Calumpit', 'S65',
  'S65 p. 192: "General MacArthur took up his advance on the 24th"; "MacArthur\'s men effected the crossing on April 28, under the accurate concentrated fire of the guns of the Utah Light Artillery"', conf='high',
  tb='Advance from Malolos on 24 April; the part of Calumpit south of the river fell "the following day"; the river was crossed on the 28th. Shown from the 28th.')
p('L-MAC', 'PH-US-2DIV', ML, D+'05-05', D+'05-05', D+'05-05', 'San Fernando (Pampanga)', 'Took San Fernando; halted there on orders', 'S65',
  'S65 p. 193 (Otis to Lawton, 5 May): "His advance is at San Fernando."; to MacArthur the same day: "You will arrest your advance at San Fernando."', conf='high', tb='Telegram date.',
  notes='S65 p. 194 (6 May): "MacArthur\'s success at Santo Tomas and San Fernando greater than at first reported." The division stayed at San Fernando through the rains.')
p('L-MAC', 'PH-US-2DIV', FA, D+'08-01', D+'08-31', D+'08-16', 'Angeles', 'Seized Angeles (a column under Wheaton: 12th Infantry and two guns)', 'S74; S68',
  'S74: "General MacArthur was called upon to seize Angeles, and ... threw a column of troops, of which General Wheaton took command, ... into Angeles and thrust the enemy back to Magalang and Mabalacat."; S68: "During August General MacArthur ... had extended his lines 10 miles farther north to Angeles."',
  tb='August; the day is not in the sources read. Shown from the middle of the month.', notes='Headquarters moved from San Fernando to Angeles (S74). The railway to Angeles reopened on 20 September (S74).')
p('L-MAC', 'PH-US-2DIV', FA, D+'11-08', D+'11-11', D+'11-11', 'Bamban', 'Advance up the railway: at Bamban; Capas occupied the same day', 'S74',
  'S74: telegram from MacArthur datelined "Bamban, November 11, 1899"; Manila to Lawton the next day: "MacArthur\'s troops occupied Capas yesterday."', tb='Telegram dateline.',
  notes='S74 (Manila to Lawton, 6 Nov): "General MacArthur took Magalang yesterday and cleared the country between that point and Arayat." The advance began at 6 a.m. on 5 November.')
p('L-MAC', 'PH-US-2DIV', FA, D+'11-12', D+'11-12', D+'11-12', 'Tarlac', 'Advance guard under Bell entered Tarlac, the Republic\'s capital, found nearly empty', 'S74; S68',
  'S74 (MacArthur, Capas, 12 Nov): "My advance under Bell entered Tarlac at 7.10 this evening, and found it practically deserted."', tb='Telegram of 12 November (the day is blurred in the scan; S68 also gives 12 November).')
p('L-MAC', 'PH-US-2DIV', FA, D+'11-17', D+'11-17', D+'11-17', 'Gerona', 'Advance entered Gerona', 'S74',
  'S74: "on the 17th, the day General MacArthur\'s advance entered Gerona (the first railway station north of Tarlac)"', conf='high', tb='Date stated.')
p('L-MAC', 'PH-US-2DIV', FA, D+'11-19', D+'11-23', D+'11-20', 'Bayambang', 'At Bayambang, the end of the working railway', 'S74; S68',
  'S74: telegrams from MacArthur\'s headquarters datelined "Bayambang, November 19, 1899" and "Bayambang, November 23, 1899"; S68: "General MacArthur entered Bayambang November 19."',
  tb='Dateline of 19 November (Bell\'s battalion went on to the end of the track near Calasiao that day). Shown from the 20th.',
  notes='S74 (MacArthur, Bayambang, 23 Nov, as printed in S68): "The so-called Filipino Republic is destroyed ... The army itself as an organization has disappeared."')
# --- Lawton, spring
p('L-LAW-S', 'PH-US-1DIV', ML, D+'03-17', D+'03-17', D+'03-17', 'Manila', 'Lawton takes command of the First Division', 'S65',
  'S65 p. 186: "New military combinations were made on March 17, General Lawton relieving Major General Anderson"', conf='high', tb='Date stated.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'04-10', D+'04-10', D+'04-10', 'Santa Cruz (Laguna)', 'Expedition across Laguna de Bay: took Santa Cruz (1,509 men)', 'S65',
  'S65 p. 189: "he proceeded across the lake on April 9, captured on the following day Santa Cruz, which he found entrenched and strongly defended"', conf='high', tb='Dates stated.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'04-17', D+'04-17', D+'04-17', 'Caloocan', 'Back from the lake; forming a column of nearly 4,000 near Caloocan', 'S65',
  'S65 pp. 190-191: "He returned on April 17"; "He concentrated near Caloocan the 22d Infantry ... General Lawton started from near Caloocan on April 22"', tb='Returned 17 April; marched 22 April.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'04-25', D+'04-25', D+'04-25', 'Norzagaray', 'Northern expedition: reached Norzagaray by Novaliches and San Jose; joined there by the Bocaue column', 'S65',
  'S65 p. 191: "He in person reached Nozagaray on April 25 and met there the Bocaue column, which had arrived that morning"', conf='high', tb='Date stated.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'04-28', D+'05-05', D+'05-05', 'Baliuag', 'Took Baliuag; held there, scouting north and east', 'S65',
  'S65 p. 193: Baliuag "with large stores of rice and sugar was captured in a spirited attack after slight opposition"; telegram of 5 May addressed "General Lawton, Baliuag"; "Lawton holds Maasin, Baliuag and Quingua."',
  tb='Taken after 25 April and before 5 May; the day is not given. Shown from 5 May, when Otis wires him there.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'05-14', D+'05-15', D+'05-15', 'San Miguel (Bulacan)', 'Routed the Filipino force at San Ildefonso and San Miguel', 'S65',
  'S65 p. 199: "On May 14, General Lawton was given permission to advance on San Miguel"; "On the evening of May 15 he was instructed as follows: General Lawton, San Miguel."', conf='high', tb='Dates stated.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'05-17', D+'05-17', D+'05-17', 'San Isidro', 'Seized San Isidro, the Republic\'s capital since Malolos', 'S65',
  'S65 p. 199: "he seized San Isidro, the third insurgent capital, on May 17"', conf='high', tb='Date stated.')
p('L-LAW-S', 'PH-US-1DIV', LW, D+'05-19', D+'05-25', D+'05-21', 'Arayat', 'Down the Rio Grande to Arayat, meeting Kobbe\'s column; the rains end the campaign', 'S65',
  'S65 p. 201: "Lawton descending the Rio Grande and Kobbe ascending the stream struck the place on the same hour of the day, found only a small force there"',
  tb='Ordered to Arayat at midnight on 17 May "after troops have rested"; the day he reached it is not given. Shown from 21 May.',
  notes='After this the column is not followed until October. S65 p. 203: garrisons were left at Baliuag, Candaba and San Luis; San Miguel and San Isidro were given up. Lawton\'s June expedition south of Manila (Paranaque, Zapote) is outside this playback.')
# --- Lawton, fall
p('L-LAW-F', 'PH-US-1DIV', FA, D+'10-15', D+'10-16', D+'10-15', 'San Fernando (Pampanga)', 'Fall campaign: Lawton leaves Manila to lead the column up the Rio Grande (3,500 men)', 'S74',
  'S74: "General Lawton left Manila for San Fernando on October 15 with instructions to push his advance on to San Isidro"', conf='high', tb='Date stated.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'10-17', D+'10-17', D+'10-17', 'Arayat', 'Crossing the Rio Grande at Arayat', 'S74',
  'S74: "On October 17 he telegraphed from Arayat that the ferry had been completed, that troops were crossing to the east bank of the river, and that an advance on Cabiao would be made that night."', conf='high', tb='Date stated.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'10-19', D+'10-19', D+'10-19', 'Cabiao', 'At Cabiao', 'S74', 'S74: telegram from Lawton datelined "Cabiao, October 19, 1899"; the day before: "I will arrive at Cabiao with most of my force to-morrow a. m."', conf='high', tb='Telegram dateline.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'10-20', D+'10-22', D+'10-20', 'San Isidro', 'Retook San Isidro; headquarters there while supplies came up the river', 'S74; S68',
  'S74: "On October 20, the day upon which General Lawton\'s troops had seized San Isidro"; telegrams from Lawton datelined San Isidro on 28, 30 and 31 October. S68 gives 22 October.', tb='20 October (S74); S68 says 22 October: see C-LZ1.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-06', D+'11-10', D+'11-10', 'Cabanatuan', 'At Cabanatuan, cut off by floods from Young ahead', 'S74; S68',
  'S74 (Lawton, Cabanatuan, 10 Nov): "Continuous rain for twenty-four hours. All communication by road cut off. Bridges and ferry washed out ... Am much worried and anxious to get up to Young."; S68: joined Young at Cabanatuan on 6 November.',
  tb='Telegram dateline of 10 November; S68 has him there from the 6th.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-11', D+'11-13', D+'11-12', 'Talavera', 'At Talavera', 'S74', 'S74: telegrams from Manila addressed "Major-General Lawton, Talavera" and telegrams from him datelined "Talavera, November 1[?], 1899"',
  tb='Between 11 and 13 November: the second digit of the date is blurred in the scan.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-15', D+'11-15', D+'11-15', 'Tayug', 'Reached Tayug', 'S74', 'S74: "General Lawton reached Tayug on November 15, proceeded north to San Nicolas"', conf='high', tb='Date stated.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-16', D+'11-17', D+'11-16', 'San Nicolas (Pangasinan)', 'Held up by floods on the road from San Nicolas to San Manuel', 'S74',
  'S74 (Lawton, "on road between San Nicolas and San Manuel, and west Agno River, November 17, 1899"): "I have been water bound here for two days, streams both sides of me being unfordable."', tb='Telegram dateline of 17 November, "two days".')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-18', D+'11-18', D+'11-18', 'Pozorrubio', 'Overtook Young at Pozorrubio', 'S74',
  'S74 (Lawton, San Fabian, 19 Nov): "I overtook him at Pozorrubio at 10 a. m. the 18th, just ready to leave on trail of Aguinaldo."', conf='high', tb='Date and hour stated.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-19', D+'11-19', D+'11-19', 'San Fabian', 'Joined Wheaton at San Fabian', 'S74',
  'S74: Lawton\'s letter is datelined "San Fabian, November 19, 1899"; Wheaton: "General Lawton came here yesterday noon"', conf='high', tb='Dateline.')
p('L-LAW-F', 'PH-US-1DIV', FA, D+'11-21', D+'12-02', D+'12-02', 'Tayug', 'Back at Tayug, supplying Young and sending columns into the mountains', 'S74',
  'S74: "General Lawton returned to Tayug and General Wheaton continued his headquarters at San Fabian."; telegrams from Lawton datelined Tayug on 2, 3, 8 and 9 December.',
  tb='Returned after 19 November; the first Tayug dateline read is 2 December. Shown from then.',
  notes='S74 (about 25 Nov): "General Lawton, with certain troops, will return by way of San Miguel and commence active operations in southern Luzon." He was killed at San Mateo on 19 December, after this playback ends; that is not in the pages read.')
# --- Young
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'09-20', D+'10-11', D+'10-11', 'San Fernando (Pampanga)', 'Forming the brigade at San Fernando; clearing the road to Arayat', 'S74; S71',
  'S74: Young "was sent north with a squadron of the Fourth Cavalry and the Twenty-fourth Infantry to San Fernando ... He awaited at San Fernando the arrival of General Lawton"; S71: itinerary "between October 11, 1899, and January 5, 1900".',
  tb='There before Lawton came on 15 October; shown from 11 October, the first day of the itinerary on Young\'s map.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'10-18', D+'10-18', D+'10-18', 'Cabiao', 'At Cabiao, leading Lawton\'s advance', 'S74; S71',
  'S71 marks an engagement "Oct. 18" at Cabiao; S74 (Lawton, Cabiao, 19 Oct, quoting Young): "Command marched from Cabiao at 8.30 a. m."', tb='Date printed on the map; telegram of the 19th.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'10-19', D+'10-20', D+'10-20', 'San Isidro', 'Fought through to San Isidro', 'S74; S71',
  'S71 marks engagements "Oct. 19" at San Antonio and Calaba, on the road to San Isidro; S74: "October 20, the day upon which General Lawton\'s troops had seized San Isidro"', tb='Dates printed on the map; 20 October for San Isidro (S74).')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'10-27', D+'10-27', D+'10-27', 'Santa Rosa', 'Engagement at Santa Rosa', 'S71', 'S71 marks an engagement "Oct. 27" at Santa Rosa.', tb='Date printed on the map.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'10-30', D+'10-31', D+'10-31', 'Cabanatuan', 'At Cabanatuan; Aliaga taken the same day', 'S74',
  'S74 (Santa Rosa, 30 Oct): "Infantry scouts of Ballance\'s battalion, supported by one company, occupied Cabanatuan at 8 this morning."; telegram of 31 Oct datelined Cabanatuan and signed "Young, Brigadier-General".', conf='high', tb='Telegram datelines.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-11', D+'11-13', D+'11-13', 'Tayug', 'Cavalry and scouts at Tayug: stores and records of the Filipino war department captured', 'S74; S75; S68',
  'S75 (Batson): "I marched to Tayug. November 14, marched my battalion to Asingan. Was accompanied by General Young and one troop of cavalry."; S74: "The Third Cavalry and a part of the scouts were, on November 15, centered at Tayug"',
  tb='At Tayug by 13 November (Batson). S68 has Young leaving Cabanatuan on 7 November; his road by San Jose, Lupao and Humingan was not read day by day.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-16', D+'11-16', D+'11-16', 'Binalonan', 'At Binalonan about noon', 'S75',
  'S75 (Batson): "Left Villasis at 6 a. m., arriving at Binalonan at about 11 a. m. General Young, accompanied by one troop of cavalry, arrived about one hour later."', conf='high', tb='Date stated (16 November).')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-17', D+'11-17', D+'11-17', 'Pozorrubio', 'At Pozorrubio, on Aguinaldo\'s trail', 'S75; S74',
  'S75 (Batson): "I arrived at Pozorrubio at 6 p. m. General Young, accompanied by one troop of the Third Cavalry, Captain Chase\'s, arrived the following day."; S74 (Lawton): overtook him there at 10 a.m. on the 18th.', conf='high', tb='Date stated (17 November).')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-18', D+'11-18', D+'11-18', 'Rosario (La Union)', 'At Rosario about 2 p.m.', 'S75',
  'S75 (Batson): "The following day, November 18, marched my battalion through Alava to San Rosario, arriving at that place about 11 a. m. General Young, with the cavalry, arrived about 2 p. m."', conf='high', tb='Date stated.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-19', D+'11-19', D+'11-19', 'Aringay', 'Over the mountain trail to Tubao; forced the Aringay River at dusk', 'S75',
  'S75 (Batson): "I arrived at Tubao about 12 o\'clock noon"; "It was about 5.30 p. m. when my advance guard, approaching the ford, were opened fire upon from an intrenchment on the other side."', conf='high', tb='Date stated.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-20', D+'11-20', D+'11-20', 'San Fernando (La Union)', 'Took San Fernando de la Union (Chase\'s troop, 37 men, with the gunboat Samar)', 'S71; S68',
  'S71 marks an engagement "Nov. 20" at San Fernando; S68, printing Young\'s report: "I overtook Chase as he neared San Fernando and witnessed the handsomest and neatest little fight of the campaign."', tb='Date printed on the map.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'11-22', D+'11-25', D+'11-25', 'Namacpacan (Luna)', 'At Namacpacan, short of men and horseshoes, asking for infantry', 'S74; S68',
  'S74: Young "with the bulk of his remaining troops was proceeding northward from Namacpacan"; S68, printing Young\'s report: "On the 25th Swigert examined country around Namacpacan, Balauang, and Bangar."', tb='Between 22 and 25 November.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'12-04', D+'12-04', D+'12-04', 'Narvacan', 'Took the trenches east of Narvacan (Tangadan)', 'S74; S71',
  'S74 (Parker, 7 Dec): "December 4 Young took trenches east of Narvacan with loss of 1 killed and 14 wounded."; S71 marks an engagement at "M. Tangadan".', conf='high', tb='Date stated.',
  notes='Placed at Narvacan; the trenches were a few kilometres east of it.')
p('L-YOUNG', 'LZ-US-YOUNG', YO, D+'12-05', D+'12-05', D+'12-05', 'Vigan', 'Reached Vigan, held since 26 November by a Navy landing party', 'S74', 'S74 (Parker, 7 Dec): "Young, with 3 troops and train, arrived there on the 5th; also 200 marines and sailors."', conf='high', tb='Date stated.')
# --- Wheaton, Kobbe, the 33rd, March, Batchelor
p('L-WHE-S', 'LZ-US-WHE-PB', MN, D+'03-10', D+'03-13', D+'03-13', 'Pasig', 'Cleared the line of the Pasig: Guadalupe, Pasig, Pateros, Cainta, Taguig', 'S65',
  'S65 p. 185: "This brigade engaged the enemy at Guadalupe ridge near San Pedro Macati, at Pasig, Pateros, Cainta and Taguig, and drove him out and beyond these towns ... in the entire six days engaged (between March 10 and 17)"',
  tb='10 to 17 March; which day it was at Pasig is not given. Shown there from the 13th.')
p('L-KOBBE', 'LZ-US-KOBBE', LW, D+'05-16', D+'05-16', D+'05-16', 'Calumpit', 'Left Calumpit up the Rio Grande with the gunboats and rations for Lawton', 'S65', 'S65 p. 198: "This command left Calumpit May 16 and reached Candaba the following day, having encountered little opposition."', conf='high', tb='Date stated.')
p('L-KOBBE', 'LZ-US-KOBBE', LW, D+'05-17', D+'05-17', D+'05-17', 'Candaba', 'Reached Candaba', 'S65', 'S65 p. 198: "This command left Calumpit May 16 and reached Candaba the following day"', conf='high', tb='Date stated.')
p('L-KOBBE', 'LZ-US-KOBBE', LW, D+'05-19', D+'05-25', D+'05-21', 'Arayat', 'Met Lawton at Arayat', 'S65', 'S65 p. 201: "Lawton descending the Rio Grande and Kobbe ascending the stream struck the place on the same hour of the day"',
  tb='After 18 May ("Kobbe and gunboats started up river this morning at six"); the day is not given. Shown from 21 May, as Lawton.')
p('L-WHE-F', 'LZ-US-WHE-X', FA, D+'11-07', D+'11-09', D+'11-07', 'San Fabian', 'Landed from the sea at San Fabian, on Lingayen Gulf', 'S74; S68',
  'S74 (Manila to MacArthur, 8 Nov): "Wheaton should have landed at San Fabian yesterday."; (to Lawton, 10 Nov): "He secured lodgment ... at San Fabian, as directed by the department commander, and has nearly completed the landing of his supplies."; S68: reached San Fabian on 7 November.',
  tb='7 November (S74 "should have landed", S68); a telegram of the 10th says "yesterday". Shown from the 7th.', notes='S74: "General Wheaton continued his headquarters at San Fabian."')
p('L-33', 'LZ-US-33', FA, D+'11-11', D+'11-11', D+'11-11', 'San Jacinto', 'Attacked and routed about 1,200 Filipino troops near San Jacinto', 'S74',
  'S74 (Wheaton, 12 Nov): "Yesterday at 9 a. m. the Thirty-third Infantry, Colonel Hare commanding, assisted by one Gatling gun ..., attacked 1,200 insurgents near San Jacinto"', conf='high', tb='Date stated; the hour is blurred in the scan.',
  notes='From 25 November two battalions under Hare marched for Vigan (S74). Not followed here after San Jacinto.')
p('L-MARCH', 'LZ-US-MARCH', YO, D+'11-30', D+'11-30', D+'11-30', 'Candon', 'Sent into the mountains on Aguinaldo\'s trail', 'S68; S74',
  'S68, printing Young\'s report: "On the 30th March was sent on Aguinaldo\'s trail, with the assurance that I would protect his rear against Tinio."', method='inferred', conf='low',
  tb='Date stated; the starting place is not. Placed at Candon, where the report says Aguinaldo left the coast.')
p('L-MARCH', 'LZ-US-MARCH', YO, D+'12-02', D+'12-02', D+'12-02', 'Tirad Pass', 'Carried Tirad Pass; Gregorio del Pilar killed', 'S68; S74; S71',
  'S68, printing March\'s report: "I reached the summit at 4.30 p. m. and camped there for the night"; S74 (telegram): "Insurgent loss in battle of Tila Pass 52 killed and wounded"; S71 marks an engagement "Dec. 2" between Lingay and Angaqui.', tb='Date printed on Young\'s map and given in March\'s report.',
  notes='The reports call it Tila Pass. Coordinates are Wikidata\'s for Tirad Pass, rounded.')
p('L-MARCH', 'LZ-US-MARCH', YO, D+'12-03', D+'12-03', D+'12-03', 'Cervantes', 'Reached Cervantes in the evening; Aguinaldo had left the night before', 'S68',
  'S68, printing March\'s report: "I arrived the evening of the 3d and spent the 4th in resting the men and sifting evidence of his whereabouts."', tb='Date stated.')
p('L-MARCH', 'LZ-US-MARCH', YO, D+'12-05', D+'12-05', D+'12-05', 'Cayan (Kayan, Tadian)', 'On to Cayan with a picked hundred', 'S68',
  'S68, printing March\'s report: "I set out at 6 a. m. on the 5th for Cayan, with a picked force of 100 officers and men"', method='inferred', conf='low', tb='Date stated.',
  notes='Cayan is taken to be Kayan in today\'s Tadian, Mountain Province; placed at Tadian. Not followed after this.')
p('L-BATCH', 'LZ-US-BATCH', YO, D+'11-25', D+'11-30', D+'11-28', 'Bayombong', 'At Bayombong, about to march down the Cagayan valley without orders', 'S74',
  'S74 (Batchelor, Bayombong, late November): "I expect to reach Ilagan in about five days and Aparri on or about December 12."; Manila: he "proceeded north from Bayombong without instructions".', tb='The letter\'s date is blurred in the scan ("November 2[?]"). Shown from the 28th.')
p('L-BATCH', 'LZ-US-BATCH', YO, D+'12-11', D+'12-13', D+'12-13', 'Alcala (Cagayan)', 'Nearing Aparri down the Cagayan River', 'S74',
  'S74 (Manila, 13 Dec): "Captain Batchelor\'s battalion is reported as in good condition and to be making good progress in its march toward, and to be not very far from, Aparri."; another telegram: "about 40 miles" from it.', method='inferred', conf='low',
  tb='Report of 13 December.', notes='Placed on the river about 50 km above Aparri (at Alcala): "about 40 miles" is all the report gives.')
# --- the Republic's government
p('L-GOV', 'LZ-PH-GOV', ML, D+'02-04', D+'02-04', D+'02-04', 'Malolos', 'Seat of government at Malolos', 'S65', 'S65 p. 182: "the Malolos government"; p. 188: "Malolos, the insurgent capital"', tb='There since 1898; the playback begins on 4 February.')
p('L-GOV', 'LZ-PH-GOV', LW, D+'03-31', D+'05-16', D+'05-16', 'San Isidro', 'Seat of government at San Isidro', 'S65', 'S65 p. 199: "San Isidro, the third insurgent capital"', method='inferred', conf='low',
  tb='Left Malolos by 31 March; when it reached San Isidro is not in the sources read. Shown there from the day before Lawton took it.')
p('L-GOV', 'LZ-PH-GOV', LW, D+'05-17', D+'05-17', D+'05-17', 'Cabanatuan', 'Retired to Cabanatuan', 'S65', 'S65 pp. 199-200: "General Aguinaldo and cabinet with troops having retired to Cabanatuan, fourteen miles to the north"', tb='Date stated.')
p('L-GOV', 'LZ-PH-GOV', FA, D+'05-18', D+'10-28', D+'06-01', 'Tarlac', 'Seat of government at Tarlac', 'S68; S74',
  'S68: "Information gained in May indicated that Tarlac ... was the new capital chosen by the insurgents."; S74 (Young, 31 Oct): captured messages "addressed to president of republic, Tarlac".', method='inferred', conf='low',
  tb='Moved between late May and October; the day is not in the sources read. Shown from 1 June.')
p('L-GOV', 'LZ-PH-GOV', FA, D+'11-12', D+'11-13', D+'11-13', 'Bayambang', 'Council of war at Bayambang: the army to break up into guerrilla bands', 'S74; S68',
  'S74 (Manila, citing Buencamino): "Paterno left Tarlac with insurgent treasury 8th instant; Buencamino and Aguinaldo on night 13th."; S68, printing MacArthur\'s report of 1900: a council of war "held at Bayambang, Pangasinan, about November 12, 1899", and a decree "Given at Bayambang, November 12, 1899".', conf='low',
  tb='12 or 13 November: see C-LZ2.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-14', D+'11-16', D+'11-15', 'Pozorrubio', 'Escaping north between Wheaton and Young', 'S68; S74',
  'S68, printing Lawton\'s letter of 19 Nov (which is in S74): Aguinaldo "passed out via Urdaneta, Manaoag and Pozorubio, with Young in hot pursuit and fighting with his rear guard."', method='inferred', conf='low',
  tb='Between leaving Bayambang (13 Nov) and Tubao (17 Nov). Shown at Pozorrubio on the 15th.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-17', D+'11-17', D+'11-17', 'Tubao', 'At Tubao with about 400 soldiers', 'S75',
  'S75 (Batson, at San Rosario on 18 Nov): "I obtained reliable information that Aguinaldo, with about 400 soldiers, had been at Tubao on the previous day."', tb='Reported the day after.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-20', D+'11-20', D+'11-20', 'Balaoan', 'Slept at Balaoan; through Bangar the next morning', 'S68',
  'S68, printing Young\'s report: "Aguinaldo slept in Balauang, on the coast road, night of November 20: passed through Bangar 10 a. m. November 21."', tb='Date stated.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-21', D+'11-25', D+'11-23', 'Candon', 'Left the coast at Candon for the mountains of Lepanto', 'S68; S75',
  'S68, printing Young\'s report: "Aguinaldo and Tinio had separated at Candon, the former going by mountain trail southeast to Lepanto"; S75 (Parker, Vigan, 26 Nov): "Aguinaldo went to Candon, thence to ... Lepanto, where he was five days ago."', method='inferred', conf='low',
  tb='After Bangar (21 Nov) and before Angaqui (28 Nov). Parker\'s "five days ago" would put him in Lepanto by the 21st, which does not fit.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-28', D+'11-28', D+'11-28', 'Angaqui (Quirino, Ilocos Sur)', 'At Angaqui', 'S68',
  'S68, printing Young\'s report: "A captured letter showed Aguinaldo in Angaqui the 28th, intending to go to Cervantes on the 29th."', tb='Date stated.', notes='Angaqui is taken to be today\'s Quirino, Ilocos Sur (formerly Angaki).')
p('L-GOV', 'LZ-PH-GOV', YO, D+'11-29', D+'11-29', D+'11-29', 'Cervantes', 'At Cervantes until the night of 2 December', 'S68',
  'S68, printing March\'s report: Aguinaldo was "living in a convent at Cervantes"; on news of Tirad Pass he "left the town at 10 o\'clock p. m."', tb='Meant to arrive on the 29th (captured letter); left at 10 p.m. on 2 December.')
p('L-GOV', 'LZ-PH-GOV', YO, D+'12-03', D+'12-03', D+'12-03', 'Cayan (Kayan, Tadian)', 'Passed through Cayan at 2 a.m., into the mountains', 'S68',
  'S68, printing March\'s report: "I located him as passing through Cayan at 2 o\'clock a. m. 3d instant."', conf='low', tb='Date and hour stated.', notes='Not followed after this in the sources read. Placed at Tadian (see March\'s row).')
# --- the army on the railway
p('L-NORTH', 'LZ-PH-NORTH', MN, D+'02-04', D+'02-10', D+'02-04', 'Caloocan', 'Massing in front of MacArthur at Caloocan (about 4,000 by 10 Feb)', 'S65',
  'S65 p. 171: "it having been reported that Luna had placed about four thousand insurgents south of Caloocan in front of MacArthur\'s refused left"', method='inferred', tb='Reported on 10 February; shown from the start.')
p('L-NORTH', 'LZ-PH-NORTH', ML, D+'03-26', D+'03-27', D+'03-26', 'Polo', 'Driven across the Tulihan; a stand at Polo', 'S65', 'S65 p. 188: "drove him northward and beyond Polo, where he made a determined stand the following day"', tb='As MacArthur\'s row.')
p('L-NORTH', 'LZ-PH-NORTH', ML, D+'03-31', D+'03-31', D+'03-31', 'Calumpit', 'Fell back from Malolos to Calumpit and Quingua; entrenched behind the rivers', 'S65',
  'S65 p. 188: "its army set fire to the city when it retreated on Calumpit and Quingua"; p. 192: "Lieutenant General Luna commanded in person the insurgent troops north of the river and had collected a considerable force, estimated at four thousand men"', tb='Date stated for the retreat.')
p('L-NORTH', 'LZ-PH-NORTH', ML, D+'05-05', D+'05-17', D+'05-17', 'Angeles', 'Driven from Santo Tomas and San Fernando; falling back up the railway', 'S65',
  'S65 p. 197 (11 May): "Luna was in his immediate front with twenty-five hundred men"; p. 200 (MacArthur, 17 May): "informed by natives that insurgent soldiers had gone to Angeles"', method='inferred', conf='low',
  tb='Between 5 and 17 May it stood in front of San Fernando; shown at Angeles from the 17th, so the symbol moves north through those days.')
p('L-NORTH', 'LZ-PH-NORTH', ML, D+'05-18', D+'05-18', D+'05-18', 'Tarlac', 'Retired on Tarlac (about 3,000)', 'S65', 'S65 p. 200: "The following day it was ascertained that Luna had retreated on Tarlac with about three thousand men"', tb='Date stated (18 May).')
p('L-NORTH', 'LZ-PH-NORTH', FA, D+'06-01', D+'08-15', D+'08-01', 'Angeles', 'Holding the towns west and north of San Fernando, through Angeles to Arayat', 'S74',
  'S74: in August "The enemy held the towns to the west and north of San Fernando, extending from the Guagua and Porac road through Angeles, and thence east to Arayat, with outposts in the near vicinity of San Fernando."', method='inferred', conf='low',
  tb='The line as it stood in August; when it came back down from Tarlac is not in the sources read. Shown from 1 August.')
p('L-NORTH', 'LZ-PH-NORTH', FA, D+'08-01', D+'08-31', D+'08-16', 'Mabalacat', 'Pushed back from Angeles to Mabalacat and Magalang', 'S74', 'S74: MacArthur "thrust the enemy back to Magalang and Mabalacat."', conf='low',
  tb='August, as MacArthur\'s row.', notes='Not followed after MacArthur\'s advance of 5-12 November: Tarlac was found "practically deserted" on the 12th, and Wheaton wrote about the 20th, "So far as I can learn insurgent army has disintegrated."')
p('L-EAST', 'LZ-PH-EAST', LW, D+'04-24', D+'04-28', D+'04-28', 'Baliuag', 'About 3,000 held at Baliuag', 'S65', 'S65 p. 192: "three thousand were held at Baliuag, to the east"', tb='As of the Calumpit crossing, 28 April.')
p('L-EAST', 'LZ-PH-EAST', LW, D+'05-05', D+'05-11', D+'05-11', 'San Miguel (Bulacan)', 'A large force at San Ildefonso and San Miguel', 'S65',
  'S65 p. 196 (11 May): "The enemy has a large force at San Ildefonso and San Miguel, and it is now reported that Generals Pilar and Geronimo have reached latter point."', tb='Telegram of 11 May.', notes='Routed by Lawton on 14-15 May; not followed after.')
p('L-SJ', 'LZ-PH-SJ', FA, D+'11-09', D+'11-10', D+'11-10', 'San Jacinto', 'In some force at San Jacinto, on the road north from Dagupan', 'S74; S68',
  'S74 (Wheaton): "The enemy is now reported in some force at San Jacinto, and we will attack them to-day."; "Insurgents\' line is San Jacinto, Mangaldan, Dagupan"; S68 (Otis\'s cable of 25 Nov): the troops meant to escort Aguinaldo north "Wheaton struck at San Jacinto".', tb='Reported on 10-11 November.')
p('L-ARI', 'LZ-PH-ARI', YO, D+'11-19', D+'11-19', D+'11-19', 'Aringay', 'Entrenched on the north bank of the Aringay River; driven out at dusk', 'S75; S68',
  'S75 (Batson): "an intrenched force of insurgents on the opposite bank"; S68, printing Young\'s report: "information was received of enemy moving up coast road to join Tinio at Aringay."', tb='Date stated.',
  notes='Whose troops these were is not stated. Young\'s report has Filipino troops moving up the coast road "to join Tinio at Aringay"; it is not drawn as Tinio\'s force because no source read says it was.')
p('L-TINIO', 'LZ-PH-TINIO', YO, D+'11-22', D+'11-25', D+'11-25', 'Tagudin', 'Holding trenches at Tagudin with about 600', 'S68', 'S68, printing Young\'s report: "Tinio, with a retarding force of 600, was occupying and repairing trenches at Tagudin."', tb='As of about 25 November.')
p('L-TINIO', 'LZ-PH-TINIO', YO, D+'12-04', D+'12-04', D+'12-04', 'Narvacan', 'Beaten in the pass east of Narvacan (Tangadan); Tinio badly wounded', 'S74; S71',
  'S74 (Parker): "December 4 Young took trenches east of Narvacan"; Spanish prisoners put the loss "in that engagement of the 4th in the mountain pass at 200 killed and wounded"; (Manila): "Young reports the killing of General Gregorio del Pilar, severe wounding of Tinio".', method='inferred', tb='Date stated.',
  notes='That Tinio commanded here is inferred from the telegram naming him wounded. Not followed after.')
p('L-PILAR', 'LZ-PH-PILAR', YO, D+'11-28', D+'12-02', D+'11-29', 'Tirad Pass', 'Holding Tirad Pass behind Aguinaldo; overrun on 2 December', 'S68; S74; S71',
  'S68, printing Young\'s report: Aguinaldo went on "leaving Pilar to fortify and hold the mountain pass in his rear, near Angaqui"; March\'s report: "Among the dead bodies was that of Gregorio del Pilar, the general commanding insurgent forces."', tb='From Aguinaldo\'s passing (28-29 Nov) to 2 December.')

# the day a column left a place, where a report gives it: (track, place, shown from) -> the day it left
LEFT = {('L-MAC', 'Caloocan', D+'02-10'): D+'03-25', ('L-MAC', 'Malolos', D+'03-31'): D+'04-24', ('L-MAC', 'Angeles', D+'08-16'): D+'11-05',
        ('L-LAW-S', 'Manila', D+'03-17'): D+'04-09', ('L-LAW-S', 'Santa Cruz (Laguna)', D+'04-10'): D+'04-16', ('L-LAW-S', 'Caloocan', D+'04-17'): D+'04-22',
        ('L-YOUNG', 'Cabanatuan', D+'10-31'): D+'11-07', ('L-BATCH', 'Bayombong', D+'11-28'): D+'11-30', ('L-GOV', 'Malolos', D+'02-04'): D+'03-31', ('L-GOV', 'Tarlac', D+'06-01'): D+'11-13',
        ('L-NORTH', 'Caloocan', D+'02-04'): D+'03-26', ('L-NORTH', 'Calumpit', D+'03-31'): D+'04-29'}
END = {'L-LAW-S': D+'05-31', 'L-WHE-S': D+'03-17', 'L-KOBBE': D+'05-31', 'L-33': D+'11-15', 'L-MARCH': D+'12-06', 'L-GOV': D+'12-05', 'L-NORTH': D+'11-10', 'L-EAST': D+'05-14',
       'L-SJ': D+'11-11', 'L-ARI': D+'11-19', 'L-TINIO': D+'12-04', 'L-PILAR': D+'12-02'}
P = wb['Positions']; ph = head(P); ROWS = {}
by = {}
for r in R: by.setdefault(r['track'], []).append(r)
for i, r in enumerate(R, 1):
    pid = 'LZ%03d' % i; r['pid'] = pid; trk = by[r['track']]; k = trk.index(r)
    la, lo, cls = PL[r['place']]; prec, cconf, basis = PREC[cls]; left = LEFT.get((r['track'], r['place'], r['show'])); tb = r['tb']
    if k + 1 == len(trk): show_to = END.get(r['track'], T1); ee = el = 'unknown'
    elif left: show_to = day(left, -1); ee = el = show_to
    else:      # the day it left is not in the sources: it is drawn leaving in time to cover the distance at about 20 km a day
        la2, lo2, _ = PL[trk[k + 1]['place']]; km = math.hypot((la2 - la) * 110.6, (lo2 - lo) * 111.3 * math.cos(math.radians(la)))
        show_to = day(trk[k + 1]['show'], -max(1, math.ceil(km / 20))); ee = r['show']; el = day(trk[k + 1]['se'], -1) if trk[k + 1]['se'] > r['show'] else r['show']
        if km > 25: tb += ' The day it left is not in the sources read: it is drawn leaving in time to cover the %d km to %s at about 20 km a day.' % (round(km), trk[k + 1]['place'].split(' (')[0])
    if show_to < r['show']: show_to = r['show']
    v = {'pos_id': pid, 'campaign_id': 'PHW-LUZ99', 'battle_id': r['battle'], 'unit_id': r['unit'], 'start_earliest': r['se'], 'start_latest': r['sl'],
         'end_earliest': ee, 'end_latest': el, 'time_basis': tb.strip(), 'activity': r['act'], 'place_description': r['place'], 'geometry': 'point',
         'lat': la, 'lon': lo, 'coord_source': 'modern_map', 'coord_precision_m': prec, 'coordinate_basis': basis, 'coordinate_confidence': cconf, 'source_ids': r['src'] + '; S73',
         'source_wording': r['wording'], 'position_method': r['method'], 'overall_confidence': r['conf'], 'notes': r['notes'] or None, 'review_status': 'Needs review',
         'show_from': r['show'], 'show_to': show_to, 'changed in v8': 'New, 21 Nov 2026 (Luzon 1899).'}
    row = add('Positions', v)
    P.cell(row, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=12/"&O%d&"/"&P%d,"Open map"))' % (row, row, row, row, row)

# ---------------------------------------------------------------- tracks
LABEL = {'L-MAC': 'MacArthur', 'L-LAW-S': 'Lawton', 'L-LAW-F': 'Lawton'}
ECH = {'PH-US-2DIV': 'division', 'PH-US-1DIV': 'division'}; ECH.update({u[0]: u[5].lower() for u in UNITS})
for trk, rows in by.items():
    add('Tracks', {'playback_id': 'luzon1899', 'track_id': trk, 'unit_id': rows[0]['unit'], 'rows': '; '.join(r['pid'] for r in rows), 'label': LABEL.get(trk),
                   'echelon': ECH[rows[0]['unit']], 'hide_after_last_row': 'yes' if trk in END else None})

# ---------------------------------------------------------------- events
def pid(track, place, show=None):
    for r in by[track]:
        if r['place'] == place and (show is None or r['show'] == show): return r['pid']
    raise KeyError((track, place))


EV = [
    ('LE01', D+'02-04', 'War begins at Manila', 'Fighting breaks out around Manila on the evening of 4 February; by the next evening the Eighth Army Corps has driven the Filipino army from its lines around the city.',
     [pid('L-MAC', 'Chinese Hospital (La Loma), Manila')], 'S65', 'Manila', 'The war begins at Manila on the evening of 4 February. The Manila playback follows these two days hour by hour.'),
    ('LE02', D+'02-10', 'Caloocan taken', 'MacArthur swings his left onto Caloocan, driving off a Filipino force put at 4,000.', [pid('L-MAC', 'Caloocan')], 'S65', 'Caloocan', 'MacArthur\'s division takes Caloocan, the railway town north of Manila.'),
    ('LE03', D+'03-17', 'The line of the Pasig', 'Wheaton\'s provisional brigade clears Pasig, Pateros and Taguig between 10 and 17 March, cutting the Filipino forces north of Manila off from those south of it. Lawton takes over the First Division.',
     [pid('L-WHE-S', 'Pasig'), pid('L-LAW-S', 'Manila')], 'S65', 'Pasig line', 'Wheaton clears the Pasig River to the lake, cutting the Filipino forces north of Manila from those to the south. Lawton arrives and takes the First Division.'),
    ('LE04', D+'03-31', 'Malolos falls', 'MacArthur\'s division, advancing from 25 March, enters Malolos, the capital of the Republic, which its army has set on fire. The government has gone.',
     [pid('L-MAC', 'Malolos'), pid('L-NORTH', 'Calumpit')], 'S65', 'Malolos', 'After a week\'s advance up the railway MacArthur enters Malolos, the Republic\'s capital, burning and empty. The Filipino army falls back to Calumpit.'),
    ('LE05', D+'04-10', 'Lawton takes Santa Cruz', 'Lawton crosses Laguna de Bay with 1,500 men and takes Santa Cruz; he is back in Manila on the 17th.', [pid('L-LAW-S', 'Santa Cruz (Laguna)')], 'S65', 'Santa Cruz', 'Lawton crosses Laguna de Bay and takes Santa Cruz, then returns to Manila.'),
    ('LE06', D+'04-28', 'Calumpit: the Rio Grande crossed', 'MacArthur forces the Bagbag and the Rio Grande at Calumpit against Luna\'s army; Lawton, marching round by Norzagaray, is closing on Baliuag.',
     [pid('L-MAC', 'Calumpit'), pid('L-LAW-S', 'Norzagaray')], 'S65', 'Calumpit', 'MacArthur\'s men cross the Rio Grande at Calumpit under the fire of the Utah guns. Lawton\'s column is working round the Filipino left by Norzagaray.'),
    ('LE07', D+'05-05', 'San Fernando', 'MacArthur takes San Fernando and is halted there; Lawton holds Baliuag.', [pid('L-MAC', 'San Fernando (Pampanga)'), pid('L-LAW-S', 'Baliuag')], 'S65', 'San Fernando', 'MacArthur takes San Fernando and is ordered to stop there. His division will hold it through the rains.'),
    ('LE08', D+'05-17', 'San Isidro', 'Lawton seizes San Isidro, the Republic\'s capital since Malolos. Aguinaldo and his cabinet retire to Cabanatuan; Luna\'s army falls back on Tarlac. The rains then end the campaign.',
     [pid('L-LAW-S', 'San Isidro'), pid('L-GOV', 'Cabanatuan')], 'S65', 'San Isidro', 'Lawton seizes San Isidro. The Republic\'s government retires to Cabanatuan and its army to Tarlac. The rains end the spring campaign; San Isidro is given up.'),
    ('LE09', D+'08-16', 'Angeles', 'In August MacArthur pushes his line ten miles up the railway to Angeles. The day is not in the sources read.', [pid('L-MAC', 'Angeles')], 'S74; S68', 'Angeles', 'During August MacArthur moves up the railway to Angeles, which becomes his headquarters.'),
    ('LE10', D+'10-20', 'San Isidro retaken', 'Lawton\'s column, with Young\'s cavalry leading, crosses at Arayat on 17 October and retakes San Isidro on the 20th.', [pid('L-LAW-F', 'San Isidro'), pid('L-YOUNG', 'San Isidro')], 'S74', 'San Isidro again',
     'The fall campaign opens: Lawton\'s column, Young\'s cavalry leading, retakes San Isidro. The plan is three columns closing on the Filipino army: Lawton up the Rio Grande, MacArthur up the railway, Wheaton by sea to Lingayen Gulf.'),
    ('LE11', D+'11-07', 'Wheaton lands at San Fabian', 'Wheaton\'s expedition lands at San Fabian on Lingayen Gulf, behind the Filipino army. MacArthur has been advancing from Angeles since the 5th; Young leaves Cabanatuan for the north.',
     [pid('L-WHE-F', 'San Fabian')], 'S74; S68', 'San Fabian', 'Wheaton lands at San Fabian on Lingayen Gulf, across the Filipino army\'s way north. MacArthur is advancing up the railway; Young\'s cavalry heads for the mountain trails.'),
    ('LE12', D+'11-11', 'San Jacinto', 'The 33rd Infantry routs about 1,200 Filipino troops near San Jacinto. MacArthur is at Bamban.', [pid('L-33', 'San Jacinto'), pid('L-SJ', 'San Jacinto')], 'S74', 'San Jacinto',
     'Wheaton\'s 33rd Infantry routs about 1,200 Filipino troops near San Jacinto, the force that was to have escorted Aguinaldo north.'),
    ('LE13', D+'11-13', 'Tarlac falls; Aguinaldo goes north', 'MacArthur\'s advance enters Tarlac on the evening of the 12th and finds it nearly empty. At Bayambang, on the 12th or 13th, Aguinaldo and his generals agree to break the army up into guerrilla bands; he leaves for the north.',
     [pid('L-MAC', 'Tarlac'), pid('L-GOV', 'Bayambang')], 'S74; S68', 'Tarlac; Bayambang', 'MacArthur enters Tarlac, the Republic\'s capital, on the 12th. At Bayambang Aguinaldo and his generals decide to disband the army into guerrilla bands, and he sets out north with a small escort.'),
    ('LE14', D+'11-20', 'Young takes San Fernando de la Union', 'Young, following Aguinaldo through Pozorrubio, Rosario and Tubao, forces the Aringay River on the 19th and takes San Fernando on the 20th. Aguinaldo sleeps that night at Balaoan, a day ahead.',
     [pid('L-YOUNG', 'San Fernando (La Union)'), pid('L-GOV', 'Balaoan')], 'S71; S68; S75', 'San Fernando, La Union', 'Young\'s handful of cavalry and Macabebe scouts reach the coast and take San Fernando de la Union. Aguinaldo is a day ahead of them on the coast road.'),
    ('LE15', D+'11-26', 'Navy lands at Vigan', 'Warships shell the trenches at Vigan and land 200 men, who occupy the town.', [], 'S75; S74', 'Vigan', 'A Navy landing party takes Vigan, ahead of Young. (Otis\'s report says the 24th; an officer on the spot says the morning of the 26th.)'),
    ('LE16', D+'12-02', 'Tirad Pass', 'March\'s battalion of the 33rd Infantry carries Tirad Pass, held by Aguinaldo\'s rear guard under Gregorio del Pilar, who is killed. Aguinaldo leaves Cervantes that night.',
     [pid('L-MARCH', 'Tirad Pass'), pid('L-PILAR', 'Tirad Pass'), pid('L-GOV', 'Cervantes')], 'S68; S74; S71', 'Tirad Pass', 'March\'s battalion carries Tirad Pass, where Gregorio del Pilar and Aguinaldo\'s rear guard die holding it. Aguinaldo leaves Cervantes that night for the mountains.'),
    ('LE17', D+'12-05', 'Young at Vigan', 'Young beats Tinio in the pass east of Narvacan on the 4th and reaches Vigan on the 5th. March has passed Cervantes for Cayan; Aguinaldo has gone into the mountains beyond it.',
     [pid('L-YOUNG', 'Vigan'), pid('L-MARCH', 'Cayan (Kayan, Tadian)')], 'S74; S68', 'Vigan', 'Young reaches Vigan after beating Tinio east of Narvacan. Aguinaldo has disappeared into the mountains; the sources read do not follow him further.'),
    ('LE18', D+'12-13', 'Cagayan surrenders', 'Word reaches Manila that the province of Cagayan has surrendered to a Navy force landed at Aparri; Batchelor\'s battalion, marching down the valley from Bayombong, is nearing the town.',
     [pid('L-BATCH', 'Alcala (Cagayan)')], 'S74', 'Cagayan', 'The Cagayan valley surrenders to a Navy force at Aparri, as Batchelor\'s battalion comes down the river from Bayombong. The playback ends here.'),
]
for eid, when, name, summ, pids, src, lab, txt in EV:
    add('Events', {'event_id': eid, 'campaign_id': 'PHW-LUZ99', 'battle_id': 'PHW-MNL-AFTER' if when < D+'03-20' else 'PHW-MALOLOS' if when < D+'04-10' else 'PHW-LAWTON' if when < D+'08-01' else 'PHW-FALL99',
                   'time_earliest': when, 'time_latest': when, 'name': name, 'summary': summ, 'pos_ids': '; '.join(pids) or None, 'source_ids': src, 'timeline': 'name',
                   'playback_at': when, 'playback_label': lab, 'playback_text': txt})

# ---------------------------------------------------------------- week summaries (weeks run from 4 Feb; a quiet week says so)
WK = {
    D+'02-04': ('War begins at Manila', 'Fighting breaks out at Manila on the evening of the 4th. By the 5th the Eighth Army Corps holds the high ground and the waterworks around the city. On the 10th MacArthur takes Caloocan.'),
    D+'02-11': ('Around Manila', 'The corps strengthens its lines around Manila. About the 12th an attack on the outpost on the Marikina road, by the waterworks, is beaten off.'),
    D+'02-18': ('Rising in Manila', 'On the night of the 22nd armed men who have slipped into Tondo set fires in the city and attack; the provost guard drives them out the next day. The 20th Infantry lands.'),
    D+'02-25': ('Around the waterworks', 'More attacks north of the Marikina road are driven off on the 25th and 27th.'),
    D+'03-04': ('A brigade for the Pasig', 'The 22nd Infantry lands. A provisional brigade under Wheaton is formed and opens its attack towards Pasig on the 10th.'),
    D+'03-11': ('The Pasig line; Lawton arrives', 'Wheaton clears Pasig, Pateros and Taguig by the 17th. Lawton takes over the First Division that day.'),
    D+'03-18': ('Preparing to advance', 'Both divisions are regrouped into three brigades each. MacArthur\'s column gathers behind La Loma on the night of the 24th.'),
    D+'04-01': ('Malolos held', 'MacArthur rests his division at Malolos while the railway behind it is repaired.'),
    D+'05-06': ('Holding San Fernando and Baliuag', 'MacArthur is kept at San Fernando; Lawton scouts from Baliuag and takes Maasin. Gunboats find the mouth of the Rio Grande and reach Calumpit on the 10th.'),
    D+'10-21': ('San Isidro', 'Lawton gathers supplies at San Isidro. Young\'s cavalry fights at Santa Rosa on the 27th.'),
    D+'03-25': ('Malolos', 'MacArthur\'s division advances from 25 March, fights across the Tulihan and at Polo, and enters Malolos on the 31st. The Republic\'s government has left and its army falls back on Calumpit.'),
    D+'04-08': ('Santa Cruz', 'Lawton crosses Laguna de Bay on the 9th and takes Santa Cruz on the 10th.'),
    D+'04-15': ('Lawton turns north', 'Lawton returns from the lake on the 17th and gathers a column of nearly 4,000 near Caloocan to march round the Filipino left.'),
    D+'04-22': ('Calumpit', 'Lawton marches on the 22nd and reaches Norzagaray on the 25th. MacArthur advances on the 24th and forces the Rio Grande at Calumpit on the 28th.'),
    D+'04-29': ('San Fernando', 'MacArthur takes Santo Tomas and San Fernando and is halted there on 5 May. Lawton takes Baliuag.'),
    D+'05-13': ('San Isidro', 'Lawton routs the Filipino force at San Ildefonso and San Miguel and seizes San Isidro on the 17th. The Republic\'s government retires to Cabanatuan and Luna\'s army to Tarlac. Kobbe\'s column comes up the Rio Grande to Candaba.'),
    D+'05-20': ('The rains', 'Lawton and Kobbe meet at Arayat. The rains begin; San Isidro and San Miguel are given up and garrisons are left at Baliuag, Candaba and San Luis.'),
    D+'08-12': ('Angeles', 'During August MacArthur pushes up the railway from San Fernando to Angeles. The day is not in the sources read.'),
    D+'10-14': ('The fall campaign opens', 'Lawton leaves Manila on the 15th, crosses the Rio Grande at Arayat on the 17th and, with Young\'s cavalry leading, retakes San Isidro on the 20th.'),
    D+'10-28': ('Cabanatuan', 'Young\'s men occupy Cabanatuan on the 30th and Aliaga on the 31st. Floods hold up Lawton\'s supplies on the river.'),
    D+'11-04': ('Three columns', 'MacArthur advances from Angeles on the 5th. Wheaton lands at San Fabian on the 7th. Young leaves Cabanatuan for the north; Lawton is cut off behind him by floods.'),
    D+'11-11': ('The Republic\'s army breaks up', 'The 33rd Infantry wins at San Jacinto on the 11th; MacArthur enters Tarlac on the 12th. At Bayambang Aguinaldo and his generals decide to fight on as guerrillas, and he slips north between Wheaton and Young. Young reaches Pozorrubio on the 17th.'),
    D+'11-18': ('The pursuit', 'Young follows Aguinaldo over the mountains to Tubao, forces the Aringay River on the 19th and takes San Fernando de la Union on the 20th. MacArthur reaches Bayambang and reports the Republic destroyed.'),
    D+'11-25': ('Into the mountains', 'Aguinaldo leaves the coast at Candon for Lepanto. The Navy lands at Vigan on the 26th. On the 30th Young sends March\'s battalion after Aguinaldo. Batchelor sets out from Bayombong down the Cagayan valley.'),
    D+'12-02': ('Tirad Pass', 'March carries Tirad Pass on the 2nd, where Gregorio del Pilar is killed, and reaches Cervantes on the 3rd; Aguinaldo has gone on into the mountains. Young beats Tinio east of Narvacan on the 4th and enters Vigan on the 5th.'),
    D+'12-09': ('Cagayan', 'The province of Cagayan surrenders to a Navy force at Aparri as Batchelor\'s battalion nears the town. Lawton is ordered south. The sources read do not follow Aguinaldo further.'),
}
QUIET = {(D+'06-01', D+'08-11'): 'The rainy season. MacArthur\'s division holds San Fernando; the Republic\'s government is at Tarlac. Nothing in the sources read moves on this map.',
         (D+'08-19', D+'10-13'): 'MacArthur holds Angeles and the railway behind it is rebuilt (first train on 20 September). New regiments arrive for the fall campaign.'}
d = T0; k = 0
while d <= T1:
    to = min(day(d, 6), T1)
    if day(to, 7) > T1 and to < T1 and (datetime.date.fromisoformat(T1) - datetime.date.fromisoformat(to)).days <= 2: to = T1
    if d in WK: title, text = WK[d]
    else:
        q = [v for (a, b), v in QUIET.items() if a <= d <= b]
        title, text = ('A quiet week', q[0]) if q else ('No change on record', 'The sources read record no move on this map this week.')
    add('Summaries', {'playback_id': 'luzon1899', 'kind': 'week', 'from': d, 'to': to, 'title': title, 'text': text, 'source_ids': 'S65; S74; S68',
                      'how written': 'From the workbook rows for the week (Positions and Events), 21 Nov 2026. Says so where the rows have nothing.'})
    d = day(to, 1); k += 1
assert set(WK) <= {r[2].value for r in wb['Summaries'].iter_rows(min_row=2) if r[0].value == 'luzon1899'}, 'a week summary did not land on a week start'

# ---------------------------------------------------------------- labels
MAJOR = {'Manila', 'Malolos', 'San Fernando (Pampanga)', 'Tarlac', 'San Isidro', 'Cabanatuan', 'San Fabian', 'San Fernando (La Union)', 'Candon', 'Vigan', 'Tirad Pass', 'Cervantes', 'Bayombong',
         'Tuguegarao', 'Aparri', 'Laoag'}      # written at every zoom; the rest appear from the zoom.labels setting
for name in ['Manila', 'Caloocan', 'Malolos', 'Calumpit', 'San Fernando (Pampanga)', 'Angeles', 'Tarlac', 'Bayambang', 'Dagupan', 'San Fabian', 'San Jacinto', 'Pozorrubio', 'Aringay',
             'San Fernando (La Union)', 'Candon', 'Vigan', 'Tirad Pass', 'Cervantes', 'Baliuag', 'San Miguel (Bulacan)', 'San Isidro', 'Arayat', 'Cabanatuan', 'Tayug', 'Bayombong',
             'Aparri', 'Santa Cruz (Laguna)', 'Norzagaray', 'San Jose (Nueva Ecija)', 'Tuguegarao', 'Laoag', 'Pasig']:
    la, lo, cls = PL[name]; short = name.split(' (')[0] if name not in ('San Fernando (Pampanga)', 'San Fernando (La Union)') else name.replace('(', 'de ').replace(')', '').replace('de Pampanga', '(Pampanga)').replace('de La Union', 'de la Union')
    add('Labels', {'playback_id': 'luzon1899', 'text': short, 'lat': la, 'lon': lo, 'level': 0 if name in MAJOR else 1, 'kind': 'landmark' if name == 'Tirad Pass' else 'town', 'show': 'both', 'approximate': 'yes' if cls != 'c' else None})

# ---------------------------------------------------------------- maps
def map_row(mid, key, title, short, label, credit, src, file, service, reduced, note, scale_note):
    f = LG.Fit(key); c = f.corners(); s = f.summary()
    add('Maps', {'playback_id': 'luzon1899', 'map_id': mid, 'title': title, 'short': short, 'label': label, 'credit': credit, 'source_id': src, 'fitted_to_ground': 'yes', 'file': file,
                 'tl_lat': round(c[0][0], 6), 'tl_lon': round(c[0][1], 6), 'tr_lat': round(c[1][0], 6), 'tr_lon': round(c[1][1], 6), 'br_lat': round(c[2][0], 6), 'br_lon': round(c[2][1], 6),
                 'bl_lat': round(c[3][0], 6), 'bl_lon': round(c[3][1], 6),
                 'fit': json.dumps({'method': 'affine (shift, turn, scale, shear) by least squares on town symbols matched to churches and town centres', 'points': s['points'], 'rms_m': s['rms_m'],
                                    'max_m': s['max_m'], 'm_per_px': s['m_per_px'], 'script': 'pipeline/georef/luzon_georef.py'}),
                 'scale_note': scale_note, 'approx_m_per_px': s['m_per_px'], 'note': note, 'iiif_service': service, 'iiif_width': f.W, 'iiif_height': f.H, 'iiif_tile': 1024,
                 'iiif_scale_factors': '[1, 2, 4, 8, 16, 32]', 'iiif_region': '0, 0, %d, %d' % (f.W, f.H), 'iiif_reduced': round(reduced / f.W, 5)})


map_row('siebert-1899', 'siebert', 'Siebert, Map of central Luzon, showing a portion of the field of operations of the 8th Army Corps (Manila, November 1899)', '1899 map', 'Central Luzon, 1899',
        'Capt. W. L. Siebert, Corps of Engineers, 1899 · Boston Public Library', 'S69', 'siebert-1899.webp', 'https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:5m60tz00z', 1541,
        'The Army\'s own map of the country from Manila Bay to Lingayen Gulf, compiled in Manila in November 1899, with the lines of operation of Lawton, MacArthur and Wheaton. It was compiled from reconnaissance, not surveyed: fitted to today\'s ground on 13 towns, places on it fall within about 600 m of where they are (1.3 km at worst).',
        'Scale about 1:264,000 on the sheet; the scan is about 26 m per pixel.')
map_row('young-1900', 'young', 'Howard, Map of northern Luzon, prepared under Brig. Gen. S. B. M. Young, fall campaign of 1899 (1900)', '1900 map', 'Northern Luzon, 1900 (Young)',
        'Lt. H. P. Howard for Gen. Young, 1900 · Boston Public Library', 'S71', 'young-1900.webp', 'https://iiif.digitalcommonwealth.org/iiif/2/commonwealth:wp98cr75t', 1600,
        'Drawn to go with General Young\'s report, with the roads his troops used and the dates of their fights. Much of the interior had never been surveyed and the map shows it: fitted to today\'s ground on 18 towns, places on it are typically 2 km from where they are, and up to 5 km in the mountains and at Vigan. Units are drawn where the towns really are, so they can sit a little off the map\'s own town marks.',
        'Scale about 1:610,000 on the sheet; the scan is about 76 m per pixel.')

# ---------------------------------------------------------------- the playback and its settings
add('Playbacks', {'playback_id': 'luzon1899', 'battle_file_id': 'luzon-1899', 'campaign_id': 'PHW-LUZ99', 'record_battles': 'PHW-MNL-AFTER; PHW-MALOLOS; PHW-LAWTON; PHW-FALL99; PHW-YOUNG',
                  'title': 'Luzon, 1899', 'subtitle': 'The Philippine War in central and northern Luzon, day by day: from Manila to the pursuit of Aguinaldo',
                  'time_unit': 'day', 'time_zero': T0, 'time_start': T0, 'time_end': T1, 'calendar_first': T0, 'days_numbered': 'no', 'origin_lat': 16.0, 'origin_lon': 120.8,
                  'west': 119.9, 'south': 14.2, 'east': 122.2, 'north': 18.7, 'opening_label': 'Before 4 February',
                  'opening_text': 'February 1899. The Eighth Army Corps holds Manila; the Philippine Republic, with its capital at Malolos, holds the rest of Luzon. Press play: the war begins at Manila on the evening of the 4th.'})
OTM = {'tiles': 'https://a.tile.opentopomap.org/{z}/{x}/{y}.png', 'max_zoom': 17, 'credit': 'OpenTopoMap (CC-BY-SA); data: OpenStreetMap contributors, SRTM', 'name': 'OpenTopoMap',
       'about': "Today's ground: OpenTopoMap, a topographic map drawn from OpenStreetMap with contours and hill shading from satellite radar heights. Place names on it are today's spellings; the campaign's own names are written over it. It is streamed from opentopomap.org while it is on screen, so it needs a connection.",
       'rights': 'Map: CC-BY-SA, OpenTopoMap. Data: Open Database License, OpenStreetMap contributors; SRTM heights', 'link': 'https://opentopomap.org/about'}
S = [('page_title', 'Luzon 1899 Playback', 'The browser tab title'), ('style', 'operational', 'tactical (a battlefield) or operational (a front)'), ('scale_bar', 'km', 'yards or km'),
     ('rate', 3, 'Days played per second'), ('clock_title', 'Luzon campaign, 1899', "The campaign's name in the date box"),
     ('bases.1.id', 'now', 'The opening map: no period map covers Manila and northern Luzon together (the landing-view rule)'), ('bases.1.label', 'Current map', None), ('bases.1.short', 'Now', None), ('bases.1.current', True, None),
     ('bases.2.id', 'c99', None), ('bases.2.label', 'Central Luzon, 1899', None), ('bases.2.short', '1899', None), ('bases.2.map', 'siebert-1899', None), ('bases.2.backdrop', 'current', None),
     ('bases.3.id', 'n00', None), ('bases.3.label', 'Northern Luzon, 1900 (Young)', None), ('bases.3.short', '1900', None), ('bases.3.map', 'young-1900', None), ('bases.3.backdrop', 'current', None),
     ('views.1.preset', 'all', 'Named views'), ('views.1.label', 'All of the campaign', None), ('views.1.short', 'All', None),
     ('views.2.preset', 'central', None), ('views.2.label', 'Manila to Lingayen Gulf', None), ('views.2.short', 'Central', None),
     ('views.3.preset', 'north', None), ('views.3.label', 'Northern Luzon', None), ('views.3.short', 'North', None),
     ('preset.all', '[119.6, 14.15, 122.4, 18.75]', 'A named view: [west, south, east, north]'), ('preset.central', '[120.1, 14.4, 121.35, 16.35]', None), ('preset.north', '[119.9, 15.8, 122.2, 18.75]', None)]
S += [('modern.' + k, v, 'The modern map (OpenTopoMap, as Ypres and Manila)') for k, v in OTM.items()]
S += [('zoom.max', 0.05, 'Closest zoom, screen pixels per metre'), ('zoom.min_factor', 0.85, None), ('zoom.labels', 0.0024, 'Town names appear from this zoom'), ('zoom.full_names', 0.006, None),
      ('question_mark', 'overall', None),
      ('texts.stated', 'A report puts the column or headquarters at this town on this date.', None),
      ('texts.inferred', 'Worked out from the reports or the order of events; the sources read do not put it here on this date.', None),
      ('texts.moving', 'The reports give the towns reached and the dates. The road between two towns is drawn straight.', None),
      ('texts.after', 'The sources read do not follow this column further. It is shown where they last put it.', None),
      ('texts.unplaced', 'The sources read do not say where it was.', None),
      ('found.modern_map', 'at the town the report names (its present-day coordinates)', None),
      ('about.1', 'Data pilot, 21 November 2026. One symbol is a column or a headquarters, placed at the town a report names on the date it gives. Positions are good to a kilometre or two at best. Nothing here has been checked by a historian.', None),
      ('about.2', 'American positions come from General Otis\'s two reports and their telegrams, Major Batson\'s report, and the dates printed on General Young\'s map. Where a date is a range ("during August", a blurred telegram date), the row says so and says which day the symbol is shown from.', None),
      ('about.3', 'The Filipino side is thin and comes from American reports: where the Republic\'s government and its main army were said to be. Strengths are American estimates. Much of it is inferred and marked so.', None),
      ('about.4', 'Aguinaldo\'s movements after 19 November, and the fight at Tirad Pass, are taken from Young\'s and March\'s reports as printed in a 1901 anti-imperialist pamphlet (the Philippine Information Society); the reports themselves were not found in the volumes read.', None),
      ('about.5', 'Operations south and east of Manila in 1899 (Paranaque and Zapote in June, Cavite in October) are not shown. The playback ends on 15 December; Lawton was killed at San Mateo on the 19th.', None),
      ('about.6', 'The two period maps are the Army\'s own. They were compiled from reconnaissance, not surveyed, so towns on them can be one to five kilometres from where they are; units are drawn at the true places.', None),
      ('about.7', 'Symbols are blue for the Americans and red for the Philippine Republic; the colours are a drawing convention.', None)]
for k_, v, w in S:
    add('Playback settings', {'playback_id': 'luzon1899', 'setting': k_, 'value': v, 'what it does': w})
add('Nations', {'playback_id': 'luzon1899', 'name': 'United States', 'short': 'American'}); add('Nations', {'playback_id': 'luzon1899', 'name': 'Philippines', 'short': 'Filipino'})

# ---------------------------------------------------------------- conflicts and gaps
for cid, q, says, did in [
    ('C-LZ1', 'When was San Isidro retaken in the fall: 20 or 22 October?', 'S74 (Otis): "October 20, the day upon which General Lawton\'s troops had seized San Isidro". | S68 (pamphlet): "San Isidro was recaptured October 22".', 'Follows S74 (primary): 20 October.'),
    ('C-LZ2', 'When and from where did Aguinaldo leave: Tarlac on the night of the 13th, or already at Bayambang on the 12th?', 'S74 (Buencamino, captured 21 Nov): "Buencamino and Aguinaldo on night 13th" left Tarlac. | S68, printing MacArthur\'s 1900 report: a council at Bayambang "about November 12" and a decree "Given at Bayambang, November 12, 1899". | S74 (rumour, 8 Nov): "reported to have left Tarlac November 1 for Bayombong".',
     'Shown at Tarlac until the 12th and at Bayambang on the 13th; low confidence.'),
    ('C-LZ3', 'When did the Navy occupy Vigan: 24 or 26 November?', 'S74 (Otis): "Vigan, which place Navy occupied 24th instant". | S75 (Parker, on the spot, "Vigan, November 26 - 1 p. m."): "On the morning of this date war ships shelled trenches ... landed force of 200 and occupied this town".', 'Event placed on the 26th (the eyewitness).'),
    ('C-LZ4', 'When did Wheaton land at San Fabian: 7 or 9 November?', 'S74 (8 Nov): "Wheaton should have landed at San Fabian yesterday." | S74 (10 Nov): "He secured lodgment yesterday at San Fabian". | S68: 7 November.', 'Shown from the 7th.'),
]:
    add('Conflicts', {'conflict_id': cid, 'battle_id': 'PHW-FALL99', 'question': q, 'what the sources say': says, 'how the pilot handled it': did, 'status': 'Open'})
for gid, gap, eff, how in [
    ('G-LZ1', "Young's and March's own reports were not found", 'Aguinaldo\'s track after 19 November and Tirad Pass rest on a partisan pamphlet\'s printing of those reports.', 'Find Report of the Lieutenant-General Commanding the Army, 1900, part 4 as the pamphlet cites it (pp. 279, 331), or part 6 or 7 of the same volume.'),
    ('G-LZ2', 'No Filipino source read', 'Every Filipino position is where American reports said it was; commanders after May 1899 and all strengths are unknown or American estimates.', "Taylor's full compilation (PW-A02), Filipino histories."),
    ('G-LZ3', 'June to September 1899 are nearly empty', 'The government is shown at Tarlac and MacArthur at San Fernando for four months with no detail; Luna\'s death in June and the fights at San Fernando are not in.', "Otis's 1899 report after p. 203 and the 1900 report before October."),
    ('G-LZ4', 'The northern Luzon map of the 8th Army Corps (S70, Madrid meridian) is not fitted', 'Not offered as a base map.', 'Fit it from its graticule and a dozen towns.'),
    ('G-LZ5', 'Positions are towns, not ground', 'A column is a point at a town; routes between towns are straight lines.', 'Trace the lines of operation drawn on S69 and the roads on S71.'),
    ('G-LZ6', 'Young\'s northern map misfits by 2 to 5 km', 'Units can sit off the map\'s own town marks.', 'Warp the picture to the control points (the player takes four corners only, so the full-resolution zoom would be lost), or accept it.'),
]:
    add('Gaps', {'gap_id': gid, 'battle_id': 'PHW-FALL99', 'gap': gap, 'effect on the data': eff, 'how to close it': how, 'status in v2': 'Open (21 Nov 2026).'})

wb.save(WB)
print('positions', len(R), 'tracks', len(by), 'events', len(EV), 'weeks', k)
