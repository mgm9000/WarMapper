"""21 Nov 2026 (Morgan: "show Wheaton's force moving by ship from Manila", "preface long unit movements with arrows ... follow the
approximate routes", "do large units breakdown to their subordinate units if zoomed in? If not, lets see if that works well").

For the Luzon 1899 playback this adds to the master workbook:
  - a row for Wheaton's expedition at Manila before it sailed (6 Nov), its sea route to San Fabian, and the ships that carried it
    as a unit of their own (a ship symbol beside the troops' symbol; it stays off the beach while they land, then fades);
  - a Routes row for each move that took more than a day or went by a road, railway, river or coast the reports name or imply, so
    the symbol follows it and the player can draw an arrow ahead of the move (about 50 routes; each says what is stated and what
    is only the likely way);
  - a trial of a large unit breaking down when the reader zooms in: MacArthur's division by brigade for the advance of 24-27 March
    (Hale's and H. G. Otis's brigades as parts of his symbol, Wheaton's brigade on the Caloocan line beside them);
  - the settings that turn the arrows and the breakdown on.
Run once, after luzon_1899_theatre_map_2026-11-21.py; it refuses to run twice.

Waypoints are present-day coordinates of the towns a route passes (Wikidata, S73, read 21 Nov 2026). A route through towns is good to a
few kilometres between them: it is where the road or railway runs today, joined by straight lines. Sea and lake routes are drawn
clear of the land; no report gives the ships' track.
"""
import copy, os
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx'); wb = openpyxl.load_workbook(WB)
assert any(r[0].value == 'S77' for r in wb['Sources'].iter_rows(min_row=2)), 'run luzon_1899_theatre_map first'
assert not any(str(r[0].value).startswith('RL') for r in wb['Routes'].iter_rows(min_row=2)), 'already applied'


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


D = '1899-'
# ---------------------------------------------------------------- towns a route passes: (lat, lon), Wikidata (S73) unless marked
C = {'Tinajeros': (14.6733, 120.9690), 'Malinta': (14.6941, 120.9688), 'Meycauayan': (14.7351, 120.9570), 'Marilao': (14.7578, 120.9490), 'Bocaue': (14.7955, 120.9259), 'Bigaa': (14.8145, 120.9085),
     'Guiguinto': (14.8333, 120.8833), 'Malolos': (14.8423, 120.8116), 'Apalit': (14.9537, 120.7724), 'Santo Tomas (Pampanga)': (15.0000, 120.7500), 'San Fernando (Pampanga)': (15.0284, 120.6931),
     'Mexico': (15.0645, 120.7203), 'Arayat': (15.1514, 120.7730), 'San Luis (Pampanga)': (15.0400, 120.7919), 'Mabalacat': (15.2167, 120.5833), 'Bamban': (15.2742, 120.5669), 'Capas': (15.3372, 120.5900),
     'Paniqui': (15.6681, 120.5789), 'Moncada': (15.7331, 120.5725), 'Cabiao': (15.2496, 120.8588), 'Santa Rosa': (15.4232, 120.9376), 'Talavera': (15.5844, 120.9192), 'San Jose (Nueva Ecija)': (15.7922, 120.9895),
     'Lupao': (15.8794, 120.8994), 'Umingan': (15.9289, 120.8419), 'San Manuel': (16.0656, 120.6667), 'Binalonan': (16.0500, 120.6000), 'Villasis': (15.9000, 120.5833), 'Urdaneta': (15.9736, 120.5672),
     'Manaoag': (16.0439, 120.4856), 'Sison (Alava)': (16.1667, 120.5167), 'Rosario (La Union)': (16.2333, 120.4833), 'Tubao': (16.3479, 120.4128), 'Aringay': (16.3982, 120.3555), 'Caba': (16.4316, 120.3446),
     'Bauang': (16.5333, 120.3333), 'San Fernando (La Union)': (16.6157, 120.3179), 'San Juan (La Union)': (16.6667, 120.3333), 'Bacnotan': (16.7197, 120.3481), 'Balaoan': (16.8211, 120.4033),
     'Bangar': (16.8930, 120.4243), 'Tagudin': (16.9361, 120.4464), 'Santa Cruz (Ilocos Sur)': (17.0853, 120.4553), 'Santa Lucia': (17.1222, 120.4494), 'Candon': (17.1933, 120.4492),
     'Santiago (Ilocos Sur)': (17.2947, 120.4453), 'Santa Maria (Ilocos Sur)': (17.3719, 120.4814), 'Santa': (17.4860, 120.4344), 'Salcedo': (17.1517, 120.5361), 'Concepcion (Gregorio del Pilar)': (17.1483, 120.6111),
     'Tirad Pass': (17.1500, 120.6333), 'Angaqui': (17.1383, 120.6764), 'San Ildefonso': (15.0789, 120.9419), 'Angat': (14.9277, 121.0290), 'San Rafael': (14.9500, 120.9667),
     'San Jose del Monte': (14.8100, 121.0481), 'San Francisco del Monte': (14.6417, 121.0178), 'Solano': (16.5186, 121.1806), 'Bagabag': (16.6044, 121.2521), 'Cordon': (16.6667, 121.4500),
     'Santiago (Isabela)': (16.6833, 121.5500), 'Cauayan': (16.7667, 121.7833), 'Ilagan': (17.1490, 121.8891), 'Tumauini': (17.2667, 121.8000), 'Cabagan': (17.4333, 121.7667), 'Tuguegarao': (17.6135, 121.7305),
     'Iguig': (17.7517, 121.7364), 'Amulung': (17.8387, 121.7235), 'Pasig': (14.5605, 121.0765), 'Manila': (14.5958, 120.9772), 'Caloocan': (14.6517, 120.9728),
     # not from a gazetteer: the old town of Novaliches (today's Novaliches Bayan, Quezon City), placed between Wikidata's points for places named for it; good to 2-3 km
     'Novaliches': (14.7220, 121.0400)}
# drawn clear of the land: no report gives the ships' track
SEA = [(14.590, 120.930), (14.500, 120.750), (14.412, 120.560), (14.400, 120.400), (14.550, 120.250), (14.800, 120.060), (15.000, 119.950), (15.400, 119.820), (15.800, 119.720), (16.200, 119.680),
       (16.500, 119.740), (16.600, 119.960), (16.520, 120.180), (16.320, 120.360)]
LAKE = [(14.5605, 121.0765), (14.535, 121.105), (14.420, 121.130), (14.300, 121.200), (14.240, 121.300)]      # down the Pasig to the lake at Napindan, then round the south of Talim Island

P = wb['Positions']; ph = head(P)
ROW = {r[0].value: r for r in P.iter_rows(min_row=2) if r[0].value}
def val(pid, col): return ROW[pid][ph.index(col)].value


def pos(pid, unit, battle, se, sl, show, show_to, ee, el, place, la, lo, prec, cconf, basis, act, src, wording, method, conf, tb, notes=None):
    row = add('Positions', {'pos_id': pid, 'campaign_id': 'PHW-LUZ99', 'battle_id': battle, 'unit_id': unit, 'start_earliest': se, 'start_latest': sl, 'end_earliest': ee, 'end_latest': el, 'time_basis': tb,
                            'activity': act, 'place_description': place, 'geometry': 'point', 'lat': la, 'lon': lo, 'coord_source': 'modern_map', 'coord_precision_m': prec, 'coordinate_basis': basis,
                            'coordinate_confidence': cconf, 'source_ids': src + '; S73', 'source_wording': wording, 'position_method': method, 'overall_confidence': conf, 'notes': notes, 'review_status': 'Needs review',
                            'show_from': show, 'show_to': show_to, 'changed in v8': 'New, 21 Nov 2026 (Luzon 1899: routes, voyage, brigades).'})
    P.cell(row, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=12/"&O%d&"/"&P%d,"Open map"))' % (row, row, row, row, row)
    ROW[pid] = P[row]


TOWN = 'The place the report names, at its coordinates on Wikidata (S73). The column was at or about it, not on the spot.'
ROUGH = 'A rough place: the report gives a river or a road, not the spot. See the notes.'
O = 'S65 pp. 186-188'
# ---------------------------------------------------------------- 1. Wheaton's expedition at Manila before it sailed
pos('LZ083', 'LZ-US-WHE-X', 'PHW-FALL99', D+'11-05', D+'11-06', D+'11-03', D+'11-05', D+'11-06', D+'11-06', 'Manila', 14.5958, 120.9772, 2500, 'low',
    'Manila, the base of the corps (Wikidata, S73). The report does not name the port the expedition sailed from.',
    'Embarking for Lingayen Gulf: the 13th Infantry, eleven companies of the 33rd, a platoon of the 6th Artillery, on two transports and two coasters, with a naval convoy', 'S74',
    'S74: "When General MacArthur\'s troops were directed to advance from Angeles on November 5, General Wheaton was ordered to proceed to Lingayen Gulf and make lodgment at or near San Fabian."; "He sailed on the morning of November 6, and arrived opposite San Fabian the following day."',
    'inferred', 'medium', 'Sailed on the morning of 6 November (stated). The day the force embarked is not given; it is shown at Manila from 3 November.',
    'The report names the transports (the scan reads "Sheridan" and "Aztec", cleaned by eye) and two chartered coasters. The sea route is not in the report: it is drawn out of Manila Bay past Corregidor, up the coast of Zambales and round Cape Bolinao.')
T = wb['Tracks']; th = head(T)
for r in T.iter_rows(min_row=2):
    if r[0].value == 'luzon1899' and r[1].value == 'L-WHE-F': r[th.index('rows')].value = 'LZ083; LZ049'
# the ships that carried it (Morgan, 21 Nov: "add a ship symbol with the ground symbol next to it. Then show the ground unit landing and the ship symbol can fade away")
add('Units', {'unit_id': 'LZ-US-SHIPS', 'unit_name': "Transports and naval convoy of Wheaton's expedition (November 1899)", 'map_label': 'Transports', 'side_id': 'PHW-US', 'nation': 'United States', 'branch': 'Naval',
              'echelon': 'Detachment', 'source_ids': 'S74', 'sourced?': 'yes',
              'notes': 'S74: "the Government transports Sheridan and Aztec and two coasting vessels chartered for this service", convoyed by two naval vessels and joined by the Oregon from Hongkong. The scan is poor: the transports\' names are cleaned by eye and the convoy\'s names read "C7aUao and Manila" (taken to be the gunboats Callao and Manila). Echelon means nothing for ships; the symbol shows none.'})
n0 = max(int(str(r[0].value)[1:]) for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value and str(r[0].value)[1:].isdigit())
add('Assignments', {'assign_id': 'A%03d' % (n0 + 1), 'unit_id': 'LZ-US-SHIPS', 'parent_unit_id': 'LZ-US-WHE-X', 'valid_from': D+'11-06', 'valid_to': D+'11-08', 'source_ids': 'S74', 'notes': 'Under Wheaton for the voyage is a drawing choice: the Navy\'s ships were not his to command.'})
ANCHOR = (16.175, 120.385)      # about 4 km off the beach at San Fabian: "arrived opposite San Fabian"
pos('LZ094', 'LZ-US-SHIPS', 'PHW-FALL99', D+'11-05', D+'11-06', D+'11-03', D+'11-05', D+'11-06', D+'11-06', 'Manila Bay, off the city', 14.5850, 120.9550, 3000, 'low',
    'The anchorage off Manila. The report does not name the port; not from a gazetteer.', 'Loading the expedition', 'S74',
    'S74: "His transportation was the Government transports Sheridan and Aztec and two coasting vessels chartered for this service." "He sailed on the morning of November 6"', 'inferred', 'medium',
    'Sailed on the morning of 6 November (stated). Shown at Manila from 3 November, as the troops are.')
pos('LZ095', 'LZ-US-SHIPS', 'PHW-FALL99', D+'11-07', D+'11-07', D+'11-07', D+'11-08', 'unknown', 'unknown', 'Lingayen Gulf, off San Fabian', ANCHOR[0], ANCHOR[1], 4000, 'low',
    'Offshore of San Fabian; the report says "opposite San Fabian" and no more. Not from a gazetteer.', 'Off San Fabian: the Navy shells the trenches and 2,000 men are landed in two hours and twenty minutes; stores are still coming through the surf on the 8th', 'S74',
    'S74: "arrived opposite San Fabian the following day"; Wheaton, 8 Nov: "Landed one battalion Thirteenth and one of the Thirty-third Infantry at 4:40, the Navy firing on the insurgent trenches"; "Will soon complete unloading of supplies, which surf on beach renders difficult."',
    'stated', 'low', 'Arrived on the afternoon of 7 November; still unloading on the 8th.', 'Not followed after the 8th: the symbol fades and leaves the map. Where the ships went next was not read.')
add('Tracks', {'playback_id': 'luzon1899', 'track_id': 'L-SHIPS', 'unit_id': 'LZ-US-SHIPS', 'rows': 'LZ094; LZ095', 'echelon': 'detachment', 'hide_after_last_row': 'yes'})

# ---------------------------------------------------------------- 3. the trial: MacArthur's division by brigade, 24-27 March
add('Units', {'unit_id': 'LZ-US-WHE-B', 'unit_name': "Wheaton's brigade on the Caloocan line (advance on Malolos, March 1899)", 'map_label': 'Wheaton', 'side_id': 'PHW-US', 'nation': 'United States', 'branch': 'Infantry',
              'echelon': 'Brigade', 'source_ids': 'S65', 'sourced?': 'yes',
              'notes': 'S65 p. 186: Wheaton "was directed to take command of the left of this line from La Loma to Caloocan", with the 2nd Oregon, the 3rd and 22nd Infantry, a battalion of the 23rd and, some days later, the 13th Minnesota. One of the three brigades of the First Division after 17 March; Otis ordered it directly.'})
n = n0 + 1
for a in [('PH-US-2-1', 'PH-US-2DIV', 'Brig. Gen. Harrison G. Otis', D+'03-17', D+'04-30', 'S65', 'S65 p. 186: after 17 March the brigades of the Second Division were "commanded by ... Brigadier Generals Hale, Otis and Hall". When Otis left the brigade was not read.'),
          ('PH-US-2-2', 'PH-US-2DIV', 'Brig. Gen. Irving Hale', D+'03-17', D+'05-31', 'S65', None),
          ('LZ-US-WHE-B', 'PH-US-CORPS', 'Brig. Gen. Loyd Wheaton', D+'03-24', D+'03-27', 'S65', None)]:
    n += 1; add('Assignments', dict(zip(['unit_id', 'parent_unit_id', 'commander', 'valid_from', 'valid_to', 'source_ids', 'notes'], a), assign_id='A%03d' % n))
ML = 'PHW-MALOLOS'
B = [  # (id, track, unit, earliest, latest, shown from, to, place, lat, lon, precision, coordinate confidence, basis, activity, wording, method, confidence, time basis, notes)
    ('LZ084', 'L-OTIS', 'PH-US-2-1', D+'03-24', D+'03-24', D+'03-24', D+'03-24', 'Behind La Loma', 14.6272, 120.9936, 2000, 'low', TOWN, 'Withdrawn from the trenches and assembled for the advance',
     O + ': the troops "were withdrawn from the trenches and assembled behind La Loma and the Deposito"; "the left (Otis\'s)"', 'inferred', 'low', 'Night of 24 March (stated).',
     'Both brigades assembled "behind La Loma and the Deposito"; which was at which is not said. Otis\'s was the left brigade, so it is drawn at La Loma.'),
    ('LZ085', 'L-OTIS', 'PH-US-2-1', D+'03-25', D+'03-25', D+'03-25', D+'03-25', 'Tulihan River, below Novaliches', 14.7050, 121.0150, 3000, 'low', ROUGH, 'Reached the Tulihan River below Novaliches and got its guns and wagons across with great labour',
     O + ': "The brigade struck the Tulihan River some distance below Novaliches, crossed its artillery and transportation only by a great deal of labor because of the high banks and the dense growth of brush"', 'stated', 'low', 'The first day of the advance, 25 March.',
     '"Some distance below Novaliches" is all the report gives: drawn on the river about 3 km downstream of the town. Not from a gazetteer.'),
    ('LZ086', 'L-OTIS', 'PH-US-2-1', D+'03-27', D+'03-27', D+'03-27', D+'03-27', 'Polo', 14.7072, 120.9472, 1500, 'medium', TOWN, 'With the division at Polo',
     O + ': "Early the next morning both brigades marched towards the railway"; the enemy stood at Polo "the following day, from which he was driven by General MacArthur\'s united troops"', 'stated', 'medium', 'As the division\'s row for Polo.',
     'After Polo the division is shown as one symbol again; where each brigade was on the way to Malolos was not read.'),
    ('LZ087', 'L-HALE', 'PH-US-2-2', D+'03-24', D+'03-24', D+'03-24', D+'03-24', 'Behind the Deposito', 14.60421, 121.03176, 2000, 'low', TOWN, 'Withdrawn from the trenches and assembled for the advance',
     O + ': the troops "were withdrawn from the trenches and assembled behind La Loma and the Deposito"; "the right brigade (Hale\'s)"', 'inferred', 'low', 'Night of 24 March (stated).',
     'Which brigade assembled at which place is not said. Hale\'s was the right brigade, so it is drawn at the Deposito.'),
    ('LZ088', 'L-HALE', 'PH-US-2-2', D+'03-25', D+'03-25', D+'03-25', D+'03-25', 'Novaliches', 14.7220, 121.0400, 3000, 'low', 'The old town of Novaliches, placed between Wikidata\'s points for places named for it; not from a gazetteer. Good to 2 or 3 km.',
     'Fought its way through San Francisco del Monte to Novaliches and the Tulihan ford', O + ': "Hale\'s brigade moving by San Francisco del Monte encountered serious difficulties there and beyond"; "the right brigade continued on to Novaliches and took the designated western route"; "the entire day was consumed when the right bank of the river was attained"',
     'stated', 'low', 'The first day of the advance, 25 March.', None),
    ('LZ089', 'L-HALE', 'PH-US-2-2', D+'03-27', D+'03-27', D+'03-27', D+'03-27', 'Polo', 14.7072, 120.9472, 1500, 'medium', TOWN, 'With the division at Polo',
     O + ': "Early the next morning both brigades marched towards the railway"; the enemy stood at Polo "the following day, from which he was driven by General MacArthur\'s united troops"', 'stated', 'medium', 'As the division\'s row for Polo.', None),
    ('LZ090', 'L-WHE-M', 'LZ-US-WHE-B', D+'03-24', D+'03-24', D+'03-24', D+'03-24', 'Caloocan', 14.6517, 120.9728, 1500, 'medium', TOWN, 'Holding the left of the line, La Loma to Caloocan',
     O + ': "Brigadier General Wheaton was directed to take command of the left of this line from La Loma to Caloocan"', 'stated', 'medium', 'In place by 24 March.', 'The brigade held a line 3 km long; the symbol is at its left, Caloocan.'),
    ('LZ091', 'L-WHE-M', 'LZ-US-WHE-B', D+'03-25', D+'03-25', D+'03-25', D+'03-25', 'Tulihan River at Tinajeros', 14.6733, 120.9690, 2500, 'low', ROUGH, 'Drove the Filipino line back across the Tulihan River; halted on the south bank',
     O + ': "Some time before evening it had driven him from all of his intrenchments back and across the Tulihan River which it was about to cross in pursuit, when its advance was arrested"', 'stated', 'low', 'Evening of 25 March.',
     'The report gives the river, not the spot: drawn at Tinajeros, where the Caloocan road and the railway reach the river.'),
    ('LZ092', 'L-WHE-M', 'LZ-US-WHE-B', D+'03-26', D+'03-26', D+'03-26', D+'03-27', 'North of the Tulihan, at Malinta', 14.6941, 120.9688, 2500, 'low', ROUGH, 'Crossed the Tulihan at two points and, with the flanking brigades, drove the Filipino army beyond Polo',
     O + ': "it was permitted to renew the attack and quickly passing the river at two points, and aided by the flanking troops, completely routed the enemy and drove him northward and beyond Polo"', 'inferred', 'low', '26 March.',
     'The report does not name Malinta: the symbol is put there because it is the ground between the river and Polo on the railway (Wikidata\'s point for the Battle of Malinta marker). Not followed after this.'),
]
for b in B:
    nxt = [x for x in B if x[1] == b[1] and x[5] > b[5]]
    pos(b[0], b[2], ML, b[3], b[4], b[5], b[6], nxt[0][3] if nxt else 'unknown', nxt[0][3] if nxt else 'unknown', b[7], b[8], b[9], b[10], b[11], b[12], b[13], 'S65', b[14], b[15], b[16], b[17], b[18])
# the Filipino army on the evening of the 25th: behind the Tulihan, not still at Caloocan with Wheaton's brigade past it
for r in P.iter_rows(min_row=2):
    if r[0].value == 'LZ069':
        r[ph.index('show_to')].value = D+'03-24'; r[ph.index('end_earliest')].value = D+'03-25'; r[ph.index('end_latest')].value = D+'03-25'
pos('LZ093', 'LZ-PH-NORTH', ML, D+'03-25', D+'03-25', D+'03-25', D+'03-25', D+'03-26', D+'03-26', 'North bank of the Tulihan River, at Malinta', 14.6941, 120.9688, 2500, 'low', ROUGH,
    'Driven from its trenches before Caloocan and back across the Tulihan River', 'S65', O + ': Wheaton\'s brigade "had driven him from all of his intrenchments back and across the Tulihan River"', 'stated', 'low', 'Evening of 25 March.',
    'The report gives the river, not the spot: drawn at Malinta, on the railway north of it.')
for r in T.iter_rows(min_row=2):
    if r[0].value == 'luzon1899' and r[1].value == 'L-NORTH': r[th.index('rows')].value = r[th.index('rows')].value.replace('LZ069; ', 'LZ069; LZ093; '); assert 'LZ093' in r[th.index('rows')].value
add('Events', {'event_id': 'LE19', 'campaign_id': 'PHW-LUZ99', 'battle_id': ML, 'time_earliest': D+'03-25', 'time_latest': D+'03-25', 'name': 'The advance on Malolos begins',
               'summary': 'MacArthur\'s column marches at dawn: Hale\'s brigade by San Francisco del Monte to Novaliches, H. G. Otis\'s to the Tulihan River below it, to turn the Filipino left, while Wheaton\'s brigade drives the Filipino line from Caloocan back across the river.',
               'pos_ids': 'LZ085; LZ088; LZ091; LZ093', 'source_ids': 'S65', 'timeline': 'name', 'playback_at': D+'03-25', 'playback_label': 'Advance begins',
               'playback_text': 'MacArthur\'s division marches at dawn to turn the Filipino left by Novaliches, while Wheaton\'s brigade attacks up the railway from Caloocan. Zoom in on Manila to see the brigades.'})
for trk, unit, part in [('L-OTIS', 'PH-US-2-1', 'L-MAC'), ('L-HALE', 'PH-US-2-2', 'L-MAC'), ('L-WHE-M', 'LZ-US-WHE-B', None)]:
    add('Tracks', {'playback_id': 'luzon1899', 'track_id': trk, 'unit_id': unit, 'rows': '; '.join(b[0] for b in B if b[1] == trk), 'echelon': 'brigade', 'part_of_track': part, 'hide_after_last_row': 'yes'})

# ---------------------------------------------------------------- 2. routes: (from row, to row, the way between, kind, wording, confidence, sources)
RAIL = 'The reports give the two places. The advance was up the Manila-Dagupan railway, and the route is drawn along it through the stations between.'
ROAD = 'The reports give the two places, not the road. Drawn along the main road through the towns between.'
R = [
    ('LZ002', 'LZ003', ['Tinajeros', 'Malinta'], 'march', 'Zoomed out, the division is one symbol and is drawn up the railway, the short way. Its two brigades went round by Novaliches (' + O + '): zoom in to see them.', 'low', 'S65'),
    ('LZ003', 'LZ004', ['Meycauayan', 'Marilao', 'Bocaue', 'Bigaa', 'Guiguinto'], 'march', 'S65 p. 188: "it was necessary to repair the railway over which the advance had been made"', 'medium', 'S65'),
    ('LZ004', 'LZ005', [], 'march', RAIL, 'medium', 'S65'),
    ('LZ005', 'LZ006', ['Apalit', 'Santo Tomas (Pampanga)'], 'march', 'S65 p. 194: "MacArthur\'s success at Santo Tomas and San Fernando"', 'medium', 'S65'),
    ('LZ007', 'LZ008', ['Mabalacat'], 'march', RAIL, 'medium', 'S74'), ('LZ008', 'LZ009', ['Capas'], 'march', 'S74: "MacArthur\'s troops occupied Capas yesterday"; Bell entered Tarlac the next evening.', 'medium', 'S74'),
    ('LZ010', 'LZ011', ['Paniqui', 'Moncada'], 'march', RAIL, 'medium', 'S74'),
    ('LZ012', 'LZ013', LAKE, 'voyage', 'S65 p. 189: "With these troops in several cascoes, towed by three of our gunboats, he proceeded across the lake on April 9"', 'low', 'S65'),
    ('LZ013', 'LZ014', LAKE[::-1] + ['Manila'], 'voyage', 'S65 p. 190: "He returned on April 17". The way back is taken to be the way out.', 'low', 'S65'),
    ('LZ014', 'LZ015', ['Novaliches', 'San Jose del Monte'], 'march', 'S65 p. 191: Lawton "started from near Caloocan on April 22" by Novaliches and San Jose; "He in person reached Nozagaray on April 25"', 'medium', 'S65'),
    ('LZ015', 'LZ016', ['Angat', 'San Rafael'], 'march', ROAD, 'low', 'S65'),
    ('LZ016', 'LZ017', ['San Ildefonso'], 'march', 'S65 p. 196: "The enemy has a large force at San Ildefonso and San Miguel"; Lawton took both on 14-15 May.', 'medium', 'S65'),
    ('LZ018', 'LZ019', ['Cabiao'], 'march', 'S65 p. 201: "Lawton descending the Rio Grande"', 'medium', 'S65'),
    ('LZ020', 'LZ021', ['Mexico'], 'march', ROAD, 'low', 'S74'), ('LZ021', 'LZ022', [], 'march', 'S74: troops crossed "to the east bank of the river" at Arayat for "an advance on Cabiao".', 'medium', 'S74'),
    ('LZ023', 'LZ024', ['Santa Rosa'], 'march', ROAD, 'low', 'S74'),
    ('LZ025', 'LZ026', ['San Jose (Nueva Ecija)', 'Lupao', 'Umingan'], 'march', 'S68 gives this road for Young (San Jose, Lupao, Humingan); that Lawton followed it is taken from his being behind Young.', 'low', 'S68; S74'),
    ('LZ027', 'LZ028', ['San Manuel', 'Binalonan'], 'march', 'S74: Lawton\'s telegram of 17 Nov is dated "on road between San Nicolas and San Manuel".', 'medium', 'S74'),
    ('LZ029', 'LZ030', ['Binalonan'], 'march', ROAD, 'low', 'S74'),
    ('LZ031', 'LZ032', ['Mexico', 'Arayat'], 'march', 'S74: Young was "clearing the road to Arayat"; the column crossed there for Cabiao.', 'medium', 'S74'),
    ('LZ035', 'LZ036', ['Talavera', 'San Jose (Nueva Ecija)', 'Lupao', 'Umingan'], 'march', 'S68: Young\'s road from Cabanatuan by San Jose, Lupao and Humingan.', 'medium', 'S68'),
    ('LZ036', 'LZ037', ['Villasis'], 'march', 'S75 (Batson): "marched my battalion to Asingan"; "Left Villasis at 6 a. m., arriving at Binalonan at about 11 a. m."', 'medium', 'S75'),
    ('LZ038', 'LZ039', ['Sison (Alava)'], 'march', 'S75 (Batson): "marched my battalion through Alava to San Rosario". Alava is today\'s Sison.', 'medium', 'S75'),
    ('LZ039', 'LZ040', ['Tubao'], 'march', 'S75 (Batson): "I arrived at Tubao about 12 o\'clock noon", then the ford of the Aringay River.', 'high', 'S75'),
    ('LZ040', 'LZ041', ['Caba', 'Bauang'], 'march', 'The coast road; S68 has Aguinaldo a day ahead "on the coast road".', 'low', 'S68'),
    ('LZ041', 'LZ042', ['San Juan (La Union)', 'Bacnotan', 'Balaoan'], 'march', 'The coast road. S68: "Swigert examined country around Namacpacan, Balauang, and Bangar."', 'low', 'S68'),
    ('LZ042', 'LZ043', ['Bangar', 'Tagudin', 'Santa Cruz (Ilocos Sur)', 'Santa Lucia', 'Candon', 'Santiago (Ilocos Sur)', 'Santa Maria (Ilocos Sur)'], 'march', 'The coast road north; S68 has Tinio holding trenches across it at Tagudin.', 'low', 'S68; S74'),
    ('LZ043', 'LZ044', ['Santa'], 'march', ROAD, 'low', 'S74'),
    ('LZ046', 'LZ047', ['San Luis (Pampanga)'], 'voyage', 'S65 p. 198: up the Rio Grande with the gunboats; they had "a sharp engagement at San Luis".', 'medium', 'S65'),
    ('LZ094', 'LZ095', SEA, 'voyage', 'S74: "He sailed on the morning of November 6, and arrived opposite San Fabian the following day." The track is not given: drawn out past Corregidor, up the Zambales coast and round Cape Bolinao.', 'low', 'S74'),
    ('LZ083', 'LZ049', SEA + [ANCHOR], 'voyage', 'S74: "He sailed on the morning of November 6, and arrived opposite San Fabian the following day." The track is not given: drawn out past Corregidor, up the Zambales coast and round Cape Bolinao, then from the ships to the beach.', 'low', 'S74'),
    ('LZ051', 'LZ052', ['Salcedo', 'Concepcion (Gregorio del Pilar)'], 'march', 'S68 gives Candon and the pass; the trail between is drawn through the towns at the foot of it.', 'low', 'S68'),
    ('LZ052', 'LZ053', ['Angaqui'], 'march', 'S71 marks the fight of 2 Dec "between Lingay and Angaqui"; March reached Cervantes on the 3rd.', 'medium', 'S71; S68'),
    ('LZ055', 'LZ056', ['Solano', 'Bagabag', 'Cordon', 'Santiago (Isabela)', 'Cauayan', 'Ilagan', 'Tumauini', 'Cabagan', 'Tuguegarao', 'Iguig', 'Amulung'], 'march',
     'S74 (Batchelor): "I expect to reach Ilagan in about five days and Aparri on or about December 12." Down the Cagayan valley; the towns between are those on the valley road today.', 'low', 'S74'),
    ('LZ061', 'LZ062', ['Urdaneta', 'Manaoag'], 'march', 'S68, printing Lawton\'s letter of 19 Nov: Aguinaldo "passed out via Urdaneta, Manaoag and Pozorubio".', 'medium', 'S68; S74'),
    ('LZ062', 'LZ063', ['Sison (Alava)', 'Rosario (La Union)'], 'march', 'Young followed his trail through Alava and Rosario to Tubao (S75).', 'low', 'S75'),
    ('LZ063', 'LZ064', ['Aringay', 'Caba', 'Bauang', 'San Fernando (La Union)', 'San Juan (La Union)', 'Bacnotan'], 'march', 'S68: "Aguinaldo slept in Balauang, on the coast road".', 'medium', 'S68'),
    ('LZ064', 'LZ065', ['Bangar', 'Tagudin', 'Santa Cruz (Ilocos Sur)', 'Santa Lucia'], 'march', 'S68: he "passed through Bangar 10 a. m. November 21"; on up the coast road to Candon.', 'medium', 'S68'),
    ('LZ065', 'LZ066', ['Salcedo', 'Concepcion (Gregorio del Pilar)', 'Tirad Pass'], 'march', 'S68: "by mountain trail southeast to Lepanto", "leaving Pilar to fortify and hold the mountain pass in his rear, near Angaqui".', 'low', 'S68'),
    ('LZ070', 'LZ071', ['Meycauayan', 'Marilao', 'Bocaue', 'Bigaa', 'Guiguinto', 'Malolos'], 'march', 'S65 p. 188: MacArthur "pressed northward the enemy who stubbornly contested every village"; it retreated from Malolos on Calumpit.', 'medium', 'S65'),
    ('LZ071', 'LZ072', ['Apalit', 'Santo Tomas (Pampanga)', 'San Fernando (Pampanga)'], 'march', 'Driven from Santo Tomas and San Fernando on 4-5 May, in MacArthur\'s front until the 17th (S65 pp. 194, 197, 200). The symbol moves up the railway through those days.', 'low', 'S65'),
    ('LZ072', 'LZ073', ['Mabalacat', 'Bamban', 'Capas'], 'march', 'S65 p. 200: "Luna had retreated on Tarlac". Drawn up the railway.', 'low', 'S65'),
    ('LZ076', 'LZ077', ['San Ildefonso'], 'march', 'S65 p. 196: "a large force at San Ildefonso and San Miguel".', 'low', 'S65'),
    ('LZ080', 'LZ081', ['Santa Cruz (Ilocos Sur)', 'Santa Lucia', 'Candon', 'Santiago (Ilocos Sur)', 'Santa Maria (Ilocos Sur)'], 'march', 'The coast road north, ahead of Young.', 'low', 'S68; S74'),
    ('LZ084', 'LZ085', [], 'march', O + ': Otis\'s brigade, "keeping to the left and retired", was to strike the Novaliches road near Balintauag.', 'low', 'S65'),
    ('LZ087', 'LZ088', ['San Francisco del Monte'], 'march', O + ': "Hale\'s brigade to that point by San Francisco del Monte and Bagbag"', 'medium', 'S65'),
    ('LZ085', 'LZ086', [], 'march', O + ': "both brigades marched towards the railway" by "the road which strikes the railway south of Polo".', 'low', 'S65'),
    ('LZ088', 'LZ089', [], 'march', O + ': "both brigades marched towards the railway" by "the road which strikes the railway south of Polo".', 'low', 'S65'),
    ('LZ090', 'LZ091', [], 'march', O, 'low', 'S65'), ('LZ091', 'LZ092', [], 'march', O, 'low', 'S65'),
]
fmt = lambda p: '%.5f, %.5f' % (p[0], p[1])
for i, (a, b, way, kind, wording, conf, src) in enumerate(R, 1):
    pts = [(val(a, 'lat'), val(a, 'lon'))] + [C[w] if isinstance(w, str) else w for w in way] + [(val(b, 'lat'), val(b, 'lon'))]
    names = [w for w in way if isinstance(w, str)]
    add('Routes', {'route_id': 'RL%02d' % i, 'campaign_id': 'PHW-LUZ99', 'battle_id': val(b, 'battle_id'), 'unit_id': val(b, 'unit_id'), 'kind': kind, 'start': val(a, 'show_to'), 'end': val(b, 'show_from'),
                   'from_pos_id': a, 'to_pos_id': b, 'waypoints (lat, lon; ...)': '; '.join(fmt(p) for p in pts), 'source_ids': src + '; S73', 'source_wording': wording, 'confidence': conf,
                   'notes': ('Through ' + ', '.join(names) + '.' if names else 'Straight from one to the other.') + (' Drawn clear of the land; the track is not in the report.' if kind == 'voyage' and not names else ''), 'playback': 'yes'})

# ---------------------------------------------------------------- settings
PS = wb['Playback settings']; h = head(PS); hit = 0
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'luzon1899' and r[h.index('setting')].value == 'texts.moving':
        r[h.index('value')].value = 'The reports give the places reached and the dates. Between them the symbol follows the railway, road, river or coast the column took, as far as the reports say; the route is approximate.'; hit += 1
assert hit == 1
for k, v, w in [('arrows.on', True, 'Arrows ahead: before a long move and during it, an arrow from the unit to where the record next puts it, along the route'), ('arrows.min_km', 20, 'Moves shorter than this get no arrow'),
                ('arrows.lead', 4, 'Days before the unit sets off that the arrow appears'), ('zoom.fold', 0.006, 'Zoomed in past this (screen pixels per metre), a unit with parts on record is shown by its parts'),
                ('fold.label', 'Brigades', 'The name of the parts in the Battle options menu'),
                ('about.8', 'A trial: for the advance of 24 to 27 March, MacArthur\'s division is shown by brigade when you zoom in on Manila (Hale, H. G. Otis, and Wheaton beside them). The brigades\' places are rough, from one paragraph of Otis\'s report.', None)]:
    add('Playback settings', {'playback_id': 'luzon1899', 'setting': k, 'value': v, 'what it does': w})
add('Gaps', {'gap_id': 'G-LZ8', 'battle_id': 'PHW-FALL99', 'gap': 'Routes are towns joined by straight lines, and many are the likely way, not a stated one',
             'effect on the data': 'A symbol on the move, and the arrow ahead of it, can be a few kilometres off the road, railway or river. %d of the %d routes rest on a report\'s wording; the rest follow the railway or main road because the reports give only the two ends.' % (sum(1 for r in R if r[5] in ('medium', 'high')), len(R)),
             'how to close it': 'Trace the railway, the roads and the lines of operation from the 1899 maps (S69, S71, S77).', 'status in v2': 'Open (21 Nov 2026).'})
wb.save(WB)
print('routes', len(R), 'stated or part-stated', sum(1 for r in R if r[5] in ('medium', 'high')), 'new position rows', 4 + len(B))
