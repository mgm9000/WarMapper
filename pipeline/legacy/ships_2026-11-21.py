"""21 Nov 2026 (Morgan: "add ship symbols whenever they are a part of the battle or delivering units to the battle, or if they are
providing naval gunfire support to a battle on the land"; and "move units more slowly in the Luzon campaign so viewers can see the
movement and the arrows").

Ships are units of the naval branch with rows of their own, wherever the reports read have them firing in support, landing men or
carrying troops:
  Manila, 4-5 Feb    Charleston and Callao off the northern flank, one vessel off the southern (S65)
  Luzon 1899         the Navy off Caloocan (10 Feb); the Army's river gunboats on the Pasig (March), across Laguna de Bay with
                     Lawton (April), at Guagua and up the Rio Grande with Kobbe (May); the Samar at San Fernando de la Union
                     (20 Nov), Vigan and Laoag; the Oregon and the Callao at Vigan (25-28 Nov), with the landing party and the
                     company of the 33rd they put ashore; the Wheeling and a landing force at Laoag (10 Dec); the Newark and
                     Helena at Aparri (10-11 Dec). Young goes on from Vigan to Laoag in the Samar (11 Dec).
Every place at sea is an estimate: the reports say "off" a town and no more. No naval report was read; this is the Army's account.

Luzon 1899 also plays at a day a second (it opened at a week a second), and skips the two quiet stretches of the rains.
Run once, after luzon_1899_routes_2026-11-21.py; it refuses to run twice.
"""
import copy, os
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx'); wb = openpyxl.load_workbook(WB)
assert any(r[0].value == 'LZ-US-SHIPS' for r in wb['Units'].iter_rows(min_row=2)), 'run luzon_1899_routes first'
assert not any(r[0].value == 'LZ-US-SAMAR' for r in wb['Units'].iter_rows(min_row=2)), 'already applied'


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
P = wb['Positions']; ph = head(P); ROW = {r[0].value: r for r in P.iter_rows(min_row=2) if r[0].value}
def val(pid, col): return ROW[pid][ph.index(col)].value
def put(pid, col, v): ROW[pid][ph.index(col)].value = v


def pos(pid, unit, battle, se, sl, show, show_to, ee, place, la, lo, prec, src_kind, basis, act, src, wording, method, conf, tb, notes=None):
    row = add('Positions', {'pos_id': pid, 'campaign_id': 'PHW-LUZ99', 'battle_id': battle, 'unit_id': unit, 'start_earliest': se, 'start_latest': sl, 'end_earliest': ee, 'end_latest': ee, 'time_basis': tb,
                            'activity': act, 'place_description': place, 'geometry': 'point', 'lat': la, 'lon': lo, 'coord_source': src_kind, 'coord_precision_m': prec, 'coordinate_basis': basis,
                            'coordinate_confidence': 'low', 'source_ids': src + ('; S73' if src_kind == 'modern_map' else ''), 'source_wording': wording, 'position_method': method, 'overall_confidence': conf, 'notes': notes,
                            'review_status': 'Needs review', 'show_from': show, 'show_to': show_to, 'changed in v8': 'New, 21 Nov 2026 (ships).'})
    P.cell(row, ph.index('unit_name') + 1).value = '=INDEX(Units!$B:$B,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('side') + 1).value = '=INDEX(Units!$D:$D,MATCH(D%d,Units!$A:$A,0))' % row
    P.cell(row, ph.index('map_link') + 1).value = '=IF(O%d="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&O%d&"&mlon="&P%d&"#map=12/"&O%d&"/"&P%d,"Open map"))' % (row, row, row, row, row)
    ROW[pid] = P[row]


SEA = 'Offshore of the place named, a few kilometres out. The report says "off" or "opposite" and no more; not from a gazetteer.'
TOWN = 'The place the report names, at its coordinates on Wikidata (S73).'
# ---------------------------------------------------------------- units
U = [  # id, name, label, branch, echelon, sources, notes, commander, from, to
    ('PH-US-NAVY-N', 'Charleston and Callao, off the northern flank at Manila (4-5 February 1899)', 'Charleston, Callao', 'Naval', 'S65',
     'S65: "Admiral Dewey had placed two vessels a short distance off shore to the north and one to the south of our flanks where they rested on Manila Bay"; Otis names the two in his telegram at daybreak.', None, D+'02-04', D+'02-05'),
    ('PH-US-NAVY-S', 'A Navy vessel off the southern flank at Manila (4-5 February 1899)', 'Navy', 'Naval', 'S65', 'S65 does not name her.', None, D+'02-04', D+'02-05'),
    ('LZ-US-NAVY-CAL', 'Navy vessels off Caloocan (10 February 1899)', 'Navy', 'Naval', 'S65', 'S65 does not name them.', None, D+'02-10', D+'02-10'),
    ('LZ-US-GUNB', 'Army gunboats on the Pasig, Laguna de Bay and the Rio Grande (the Laguna de Bay and others)', 'Gunboats', 'Naval', 'S65',
     'River steamers armed and manned by the Army. S65: the Laguna de Bay, "a former Pasig River passenger steamboat", with "machine and six-pounder guns and heavy sheet-iron protection" and two officers and 65 men. One boat in March, three on the lake in April, two at Guagua in May: taken here as one flotilla, which the report does not say in terms.',
     'Capt. Randolph, 3rd Artillery, then Capt. Grant, Utah Artillery', D+'03-10', D+'05-31'),
    ('LZ-US-SAMAR', 'Gunboat Samar', 'Samar', 'Naval', 'S68; S74; S75', 'A small gunboat, one of those bought from Spain.', 'Ensign Mustin', D+'11-20', D+'12-11'),
    ('LZ-US-OREGON', 'Battleship Oregon', 'Oregon', 'Naval', 'S74; S75', 'S74: joined Wheaton\'s convoy "direct from Hongkong".', 'Capt. Wilde', D+'11-08', D+'12-05'),
    ('LZ-US-CALLAO', 'Gunboat Callao', 'Callao', 'Naval', 'S74', 'In Wheaton\'s convoy on 6-7 November (drawn there with the transports). The scan of S74 spells her "C7aUao", "Oillao" and "CaU<<": taken to be the Callao.', None, D+'11-26', D+'11-29'),
    ('LZ-US-NEWARK', 'Newark and Helena (Capt. McCalla\'s force at Aparri)', 'Newark, Helena', 'Naval', 'S74', None, 'Capt. McCalla', D+'12-10', D+'12-15'),
    ('LZ-US-WHEEL', 'Gunboat Wheeling', 'Wheeling', 'Naval', 'S74', None, 'Cmdr. W. L. Burwell', D+'12-10', D+'12-13'),
    ('LZ-US-VIG-LP', 'Landing party from the ships at Vigan (about 200 sailors and marines)', 'Landing party', 'Infantry', 'S75; S74', 'S75 (Parker): "landed force of 200"; S74: "a battalion of marines".', None, D+'11-25', D+'12-05'),
    ('LZ-US-33-CO', 'A company of the 33rd Infantry sent to Vigan by sea', 'Co., 33 Inf', 'Infantry', 'S74', 'S74: "one company of Hare\'s regiment to Vigan on the gunboat Callao, to hold that place until the arrival of General Young or Colonel Hare". Which company was not read.', None, D+'11-27', D+'12-05'),
    ('LZ-US-LAO-LP', 'Landing force at Laoag (about 100 men: 50 from the Wheeling, 50 soldiers with one gun)', 'Landing force', 'Infantry', 'S74', None, 'Lt. Kaiser, Navy; Capt. Koehler with the gun', D+'12-10', D+'12-15'),
]
n = max(int(str(r[0].value)[1:]) for r in wb['Assignments'].iter_rows(min_row=2) if r[0].value and str(r[0].value)[1:].isdigit())
for uid, name, label, branch, src, notes, cmd, a, b in U:
    ech = 'Company' if uid == 'LZ-US-33-CO' else 'Detachment'
    add('Units', {'unit_id': uid, 'unit_name': name, 'map_label': label, 'side_id': 'PHW-US', 'nation': 'United States', 'branch': branch, 'echelon': ech, 'source_ids': src, 'sourced?': 'yes',
                  'notes': (notes or '') + (' Echelon means nothing for ships; the symbol shows none.' if branch == 'Naval' else '') or None})
    n += 1; add('Assignments', {'assign_id': 'A%03d' % n, 'unit_id': uid, 'commander': cmd, 'valid_from': a, 'valid_to': b, 'source_ids': src})

# ---------------------------------------------------------------- Manila, 4-5 February (by the clock)
MN = 'PHW-MNL'
pos('M39', 'PH-US-NAVY-N', MN, '1899-02-04 18:00', '1899-02-05 06:00', '1899-02-04 20:30', '1899-02-05 20:00', 'unknown', 'Manila Bay, off Tondo and the Vitas blockhouse', 14.6320, 120.9480, 1500, 'estimate',
    'Where the northern line met the bay, about a kilometre out. S65 says "a short distance off shore"; not read from a map.',
    'Off the northern flank. At daybreak Otis asks for their fire on the Filipino line north of the Vitas blockhouse', 'S65',
    'S65: "Admiral Dewey had placed two vessels a short distance off shore to the north and one to the south of our flanks where they rested on Manila Bay"; Otis to Dewey at daybreak on the 5th: "Charleston and Callao could give efficient aid in that vicinity"; at 6:50 a.m.: "A sharp raking firing of one half hour just to north of blockhouse on Vitas Pass would reach insurgent line"; that evening: "We owe you gratitude for your great aid."',
    'stated', 'low', 'In place by the night of 4 February. The hours they fired are not given.')
pos('M40', 'PH-US-NAVY-S', MN, '1899-02-04 18:00', '1899-02-05 06:00', '1899-02-04 20:30', '1899-02-05 20:00', 'unknown', 'Manila Bay, off Malate and Fort San Antonio Abad', 14.5560, 120.9720, 1500, 'estimate',
    'Where the southern line met the bay, about a kilometre out. S65 says "a short distance off shore"; not read from a map.',
    'Off the southern flank. In the afternoon Otis asks Dewey to keep her forward to help the advance down the coast to Pasay', 'S65',
    'S65: "two vessels a short distance off shore to the north and one to the south of our flanks"; Otis to Dewey on the 5th: "Will you keep vessel to the front to assist advance down coast?"',
    'stated', 'low', 'In place by the night of 4 February. Whether she moved down the coast with the advance is not given.', 'S65 does not name her.')
for uid, pid in [('PH-US-NAVY-N', 'M39'), ('PH-US-NAVY-S', 'M40')]:
    add('Tracks', {'playback_id': 'manila', 'track_id': uid, 'unit_id': uid, 'rows': pid, 'echelon': 'detachment'})

# ---------------------------------------------------------------- Luzon 1899 (by the day)
AFT, ML, LW, FA, YO = 'PHW-MNL-AFTER', 'PHW-MALOLOS', 'PHW-LAWTON', 'PHW-FALL99', 'PHW-YOUNG'
SF, VIG, LAO, FAB, APA = (16.640, 120.290), (17.550, 120.330), (18.200, 120.500), (16.175, 120.385), (18.400, 121.640)
T = []  # (id, track, unit, battle, earliest, latest, shown from, to, place, lat, lon, precision, estimate|modern_map, activity, sources, wording, method, confidence, time basis, notes)
def row(*a): T.append(a)
row('LZ096', 'L-NAVY-CAL', 'LZ-US-NAVY-CAL', AFT, D+'02-10', D+'02-10', D+'02-10', D+'02-10', 'Manila Bay, off Caloocan', 14.6550, 120.9250, 3000, 'estimate',
    'Shell the Filipino trenches at Caloocan for half an hour before the assault', 'S65', 'S65 p. 171: "The attack, preceded by a fire of thirty minutes from the guns of the Navy vessels on and in front of Caloocan"',
    'stated', 'low', 'Afternoon of 10 February.', 'S65 does not name the ships. Not followed after.')
row('LZ097', 'L-GUNB', 'LZ-US-GUNB', AFT, D+'03-10', D+'03-17', D+'03-13', D+'03-17', 'Pasig River at Pasig', 14.5605, 121.0765, 2500, 'modern_map',
    'The gunboat Laguna de Bay helps Wheaton\'s brigade clear the Pasig, opens the river to the lake and scatters the boats gathered there', 'S65',
    'S65 p. 185: "The gunboat Laguna de Bay, Captain Grant, of the Utah Artillery, commanding, assisted greatly in these affairs, opened the river to the lake which she entered, dispersed the insurgents\' shipping"',
    'stated', 'low', 'Between 10 and 17 March; shown from the 13th, as Wheaton\'s brigade is.', None)
row('LZ098', 'L-GUNB', 'LZ-US-GUNB', LW, D+'04-08', D+'04-09', D+'04-08', D+'04-08', 'Pasig River at Manila', 14.5958, 120.9772, 2500, 'modern_map',
    'Three gunboats take the cascoes of Lawton\'s expedition in tow', 'S65', 'S65 p. 189: "With these troops in several cascoes, towed by three of our gunboats, he proceeded across the lake on April 9"',
    'inferred', 'low', 'Crossed the lake on 9 April (stated). That they set out from Manila is taken from the expedition\'s doing so.', None)
row('LZ099', 'L-GUNB', 'LZ-US-GUNB', LW, D+'04-10', D+'04-10', D+'04-10', D+'04-15', 'Laguna de Bay, off Santa Cruz', 14.2950, 121.4050, 3000, 'estimate',
    'Off Santa Cruz while Lawton takes the town and searches the river for the launches hidden there', 'S65',
    'S65 p. 189: he "proceeded across the lake on April 9, captured on the following day Santa Cruz"; "The water of the lake had become very low and the boats could not be passed over the bar at the river\'s mouth."',
    'inferred', 'low', 'With the expedition, 10 to 16 April.', 'What the gunboats did in the fight is not in S65.')
row('LZ100', 'L-GUNB', 'LZ-US-GUNB', LW, D+'04-17', D+'04-17', D+'04-17', D+'04-17', 'Pasig River at Manila', 14.5958, 120.9772, 2500, 'modern_map',
    'Back with the expedition and its prizes', 'S65', 'S65 p. 190: "He returned on April 17, bringing six steam launches and two cascoes which the enemy had concealed near Santa Cruz."', 'inferred', 'low', '17 April.', None)
row('LZ101', 'L-GUNB', 'LZ-US-GUNB', LW, D+'05-07', D+'05-08', D+'05-08', D+'05-08', 'Guagua, on the Guagua River', 14.9644, 120.6339, 2500, 'modern_map',
    'Two gunboats under Grant, with stores for MacArthur, run past the trenches at Sexmoan, take them in flank and clear Guagua. MacArthur\'s troops do not come and they go back to Manila', 'S65',
    'S65 p. 195: "On May 7 Captain Grant, of the Utah Artillery, with two gunboats, was instructed to proceed from Manila to Guagua with supplies for MacArthur\'s troops"; fired on at Sexmoan "by some five hundred of the enemy", he "opened a deadly fire striking the insurgents in flank"; "he returned to Manila on the following day."',
    'stated', 'medium', 'Ordered on 7 May; the day of the fight is not given (the 7th or 8th). Shown on the 8th.', None)
row('LZ102', 'L-GUNB', 'LZ-US-GUNB', LW, D+'05-10', D+'05-10', D+'05-10', D+'05-16', 'Rio Grande at Calumpit', 14.9161, 120.7690, 2000, 'modern_map',
    'Find the mouth of the Rio Grande and reach Calumpit; then clear the banks up to Candaba, with a sharp fight at San Luis', 'S65',
    'S65 p. 196: he "was directed to find the mouth of the Rio Grande and pass up that stream to Calumpit, which place he successfully reached without marked incident on May 10. He was then directed to proceed up the river and clear the banks of insurgents as far as Candaba, which he accomplished, having a sharp engagement at San Luis."',
    'stated', 'medium', '10 May (stated). The day of the run to Candaba and back is not given.', None)
row('LZ103', 'L-GUNB', 'LZ-US-GUNB', LW, D+'05-17', D+'05-17', D+'05-17', D+'05-18', 'Rio Grande at Candaba', 15.0918, 120.8280, 2000, 'modern_map',
    'With Kobbe\'s column, towing cascoes with 20,000 rations for Lawton', 'S65', 'S65 p. 198: Kobbe was to go up the river "attended by the gunboats which were to haul cascoes loaded with twenty thousand extra rations. This command left Calumpit May 16 and reached Candaba the following day"',
    'stated', 'medium', '17 May.', None)
row('LZ104', 'L-GUNB', 'LZ-US-GUNB', LW, D+'05-19', D+'05-25', D+'05-21', D+'05-23', 'Rio Grande at Arayat', 15.1514, 120.7730, 2500, 'modern_map',
    'Up the river with Kobbe to Arayat, as far as the boats can go', 'S65', 'S65 p. 200 (18 May): "Kobbe and gunboats started up river this morning at six."; p. 196: "These boats could navigate this river as far up as Arayat"',
    'inferred', 'low', 'As Kobbe\'s row: after 18 May, the day not given; shown from the 21st.', 'S65 p. 203: one gunboat was left in the Rio Grande to cover Candaba and San Luis. Not followed after.')
row('LZ105', 'L-SAMAR', 'LZ-US-SAMAR', YO, D+'11-20', D+'11-21', D+'11-20', D+'11-24', 'Off San Fernando de la Union', SF[0], SF[1], 4000, 'estimate',
    'Shells the works at San Fernando at Young\'s signal and drives the riflemen off the hills; the next day brings Young stores from San Fabian', 'S68; S74',
    'S68, printing Young\'s report: "flag communication was gained with gunboat Samar, Ensign Mustin commanding. He was requested to open on the works at San Fernando at 2.30 p. m."; "until the Samar\'s guns frightened them away"; S74: supplies "forwarded on that day [21 November] from San Fabian by the naval gunboat Samar"',
    'stated', 'medium', '20 November, 2.30 p.m. (stated).', 'Her run to San Fabian and back on the 21st is not drawn.')
row('LZ106', 'L-SAMAR', 'LZ-US-SAMAR', YO, D+'11-25', D+'11-25', D+'11-25', D+'11-27', 'At anchor off Vigan', VIG[0] - 0.02, VIG[1], 4000, 'estimate',
    'Reaches the anchorage off Vigan on the afternoon of the 25th with Lt. Col. Parker; the next morning the ships shell the trenches and land 200 men', 'S75',
    'S75 (Parker): "Lieutenant Mustin knows of no anchorages on this stretch of coast except at Narbacan."; "Overtook Oregon at anchorage near Vigan, p. m. November 25. On the morning of this date [26 November] war ships shelled trenches"',
    'inferred', 'low', '25 and 26 November.', 'That Parker travelled in the Samar is taken from his naming her commander; he does not say so in terms. Where she was from 27 November to 10 December was not read.')
row('LZ107', 'L-SAMAR', 'LZ-US-SAMAR', YO, D+'12-10', D+'12-11', D+'12-10', D+'12-10', 'At anchor off Vigan', VIG[0] - 0.02, VIG[1], 4000, 'estimate',
    'Takes Young and twenty troopers aboard for Laoag', 'S74', 'S74 (Young, Vigan, 10 Dec): "Leave to-morrow morning on Samar with 20 men of my escort for Laoag."; "I left Vigan 8 a. m. on Samar"', 'stated', 'medium', 'Sailed at 8 a.m. on 11 December.', None)
row('LZ108', 'L-SAMAR', 'LZ-US-SAMAR', YO, D+'12-11', D+'12-11', D+'12-11', D+'12-11', 'Off Laoag', LAO[0] - 0.02, LAO[1], 4000, 'estimate',
    'Lands Young at Laoag in the afternoon; sent back with his dispatch that night', 'S74', 'S74 (Young, Laoag): "I left Vigan 8 a. m. on Samar, reaching Laoag at [hour blurred] p. m."; "I send Samar with this dispatch to-night."', 'stated', 'medium', '11 December.', 'Not followed after.')
row('LZ109', 'L-OREGON', 'LZ-US-OREGON', FA, D+'11-08', D+'11-24', D+'11-22', D+'11-24', 'Lingayen Gulf, off San Fabian', FAB[0] + 0.03, FAB[1] - 0.03, 5000, 'estimate',
    'In Lingayen Gulf with the Callao and the Samar, under orders to co-operate with the army', 'S74',
    'S74: Wheaton\'s convoy was "subsequently joined by the Oregon, direct from Hongkong"; Rear-Admiral Watson, about 22 November: "Left Oregon, Callao, and Samar in Lingayen Gulf with orders to cooperate."',
    'stated', 'low', 'Joined after 7 November; Watson\'s telegram is of about 22 November (its date is blurred in the scan). Shown from the 22nd.', 'The ships\' names in Watson\'s telegram are cleaned by eye from a poor scan.')
row('LZ110', 'L-OREGON', 'LZ-US-OREGON', YO, D+'11-25', D+'11-25', D+'11-25', D+'12-05', 'At anchor off Vigan', VIG[0], VIG[1], 4000, 'estimate',
    'At anchor off Vigan on the 25th. On the morning of the 26th the ships shell the trenches and land about 200 sailors and marines, who occupy the town', 'S75; S74',
    'S75 (Parker, Vigan, 26 Nov, 1 p.m.): "Overtook Oregon at anchorage near Vigan, p. m. November 25. On the morning of this date war ships shelled trenches; ran out 50 to 100 insurgents; landed force of 200 and occupied this town"; S74: the Callao reported "that the Oregon had landed a battalion of marines at Vigan on the previous day"',
    'stated', 'medium', '25 and 26 November (Parker, on the spot). Otis\'s telegram has the Navy in Vigan on the 24th: see C-LZ3.', 'When she left Vigan was not read: shown to 5 December, when Young arrived, then the symbol fades.')
row('LZ111', 'L-CALLAO', 'LZ-US-CALLAO', YO, D+'11-26', D+'11-26', D+'11-26', D+'11-26', 'Off Vigan', VIG[0] + 0.02, VIG[1], 4000, 'estimate',
    'With the ships at the landing', 'S74', 'S74: she reached San Fabian on the 27th "reporting that the Oregon had landed a battalion of marines at Vigan on the previous day"', 'inferred', 'low',
    '26 November.', 'That she was at Vigan on the 26th is taken from her bringing the news; the report does not say where she had been.')
row('LZ112', 'L-CALLAO', 'LZ-US-CALLAO', YO, D+'11-27', D+'11-27', D+'11-27', D+'11-27', 'Lingayen Gulf, off San Fabian', FAB[0], FAB[1], 4000, 'estimate',
    'Brings Wheaton word of Vigan and takes a company of the 33rd Infantry aboard', 'S74',
    'S74: "the U. S. gunboat Callao had just arrived"; Wheaton "would send one company of Hare\'s regiment to Vigan on the gunboat Callao, to hold that place until the arrival of General Young or Colonel Hare"', 'stated', 'medium', '27 November.', None)
row('LZ113', 'L-CALLAO', 'LZ-US-CALLAO', YO, D+'11-28', D+'11-28', D+'11-28', D+'11-29', 'Off Vigan', VIG[0] + 0.02, VIG[1], 4000, 'estimate',
    'Lands the company at Vigan', 'S74', 'S74: "one company proceeding to that point by gunboat which would reach there the following day"', 'inferred', 'low', '28 November is the plan Wheaton telegraphed; her arrival was not read.', 'Not followed after.')
row('LZ114', 'L-33CO', 'LZ-US-33-CO', YO, D+'11-27', D+'11-27', D+'11-27', D+'11-27', 'San Fabian', 16.15, 120.45, 2500, 'modern_map',
    'Embarks in the Callao for Vigan', 'S74', 'S74: Wheaton "would send one company of Hare\'s regiment to Vigan on the gunboat Callao"', 'inferred', 'low', '27 November.', None)
row('LZ115', 'L-33CO', 'LZ-US-33-CO', YO, D+'11-28', D+'11-28', D+'11-28', D+'12-05', 'Vigan', 17.5748, 120.3890, 1500, 'modern_map',
    'Lands to hold Vigan until Young or Hare arrives', 'S74', 'S74: "to hold that place until the arrival of General Young or Colonel Hare"; "one company proceeding to that point by gunboat which would reach there the following day"',
    'inferred', 'low', '28 November is the plan; the landing itself was not read.', 'Shown to 5 December, when Young arrived; not followed after.')
row('LZ116', 'L-VIGLP', 'LZ-US-VIG-LP', YO, D+'11-25', D+'11-25', D+'11-25', D+'11-25', 'Aboard the ships off Vigan', VIG[0], VIG[1] + 0.012, 4000, 'estimate',
    'Aboard, the night before the landing', 'S75', 'S75 (Parker): "Overtook Oregon at anchorage near Vigan, p. m. November 25."', 'inferred', 'low', '25 November.', 'Drawn so that the landing can be seen.')
row('LZ117', 'L-VIGLP', 'LZ-US-VIG-LP', YO, D+'11-26', D+'11-26', D+'11-26', D+'12-05', 'Vigan', 17.5748, 120.3890, 1500, 'modern_map',
    'Lands after the ships shell the trenches and occupies Vigan, to bells and a band', 'S75; S74',
    'S75 (Parker): "landed force of 200 and occupied this town amidst great acclamations, reception by entire populace, band escorting, bells ringing"; S74: "a battalion of marines"', 'stated', 'medium',
    'Morning of 26 November.', 'Shown to 5 December, when Young arrived; not followed after.')
row('LZ118', 'L-NEWARK', 'LZ-US-NEWARK', YO, D+'12-10', D+'12-10', D+'12-10', D+'12-15', 'Off Aparri, at the mouth of the Cagayan River', APA[0], APA[1], 5000, 'estimate',
    'McCalla\'s ships reach Aparri with stores for Batchelor and land a force. On the 11th Tirona, the Filipino commander in the valley, surrenders to him', 'S74',
    'S74 (Manila, 10 Dec): "Large naval force reaches Aparri to-day."; Otis: Watson "dispatched the naval vessels Newark and Helena, Captain McCalla commanding"; "Tirona, the insurgent general, surrendered the provinces of the Cagayan Valley to Captain McCalla of the Navy on the 11th of December"',
    'stated', 'medium', '10 December is the day Manila expected them; the surrender was on the 11th.', 'S74: Batchelor "received the supplies sent for him by the Navy at the head waters of river navigation"; the boats that took them up the river are not drawn.')
row('LZ119', 'L-WHEEL', 'LZ-US-WHEEL', YO, D+'12-10', D+'12-11', D+'12-10', D+'12-13', 'Off Laoag', LAO[0], LAO[1], 4000, 'estimate',
    'Lands fifty men at Laoag and lies off the town', 'S74',
    'S74 (Young, Vigan, 10 Dec): "Navy landed force at Laoag to-day"; "The 100 men landed at Laoag include 50 men from the U. S. S. Wheeling, and 50 men sent by me with one gun"; a letter to Young is dated "U. S. S. Wheeling, off Laoag, P. I., December 11, 1899"',
    'stated', 'medium', '10 and 11 December.', 'Not followed after the 13th.')
row('LZ120', 'L-LAOLP', 'LZ-US-LAO-LP', YO, D+'12-10', D+'12-10', D+'12-10', D+'12-15', 'Laoag', 18.1938, 120.5940, 1500, 'modern_map',
    'Landed from the Wheeling and from Vigan to hold Laoag, where some 1,500 Spanish prisoners are found', 'S74',
    'S74 (Young): "Navy landed force at Laoag to-day, consisting of 100 men, also Captain Koehler, Thirty-seventh Infantry, with one gun."; Cmdr. Burwell: "There are about 1,500 Spanish prisoners here"', 'stated', 'medium', '10 December.', None)
row('LZ121', 'L-YOUNG', 'LZ-US-YOUNG', YO, D+'12-11', D+'12-11', D+'12-11', D+'12-15', 'Laoag', 18.1938, 120.5940, 1500, 'modern_map',
    'By sea in the Samar to Laoag with twenty troopers, to direct the pursuit of Tinio and the rescue of the American prisoners', 'S74',
    'S74 (Young, Laoag): "I left Vigan 8 a. m. on Samar, reaching Laoag at [hour blurred] p. m."; "I remain here to-night with navy, under command of Lieutenant Kaiser, Navy, and 20 cavalrymen under Lieutenant Bell, dismounted, brought with me on the Samar."',
    'stated', 'high', '11 December.', 'This is Young and his escort; his columns were in the mountains (Hare, Howze) and on the coast road (Swigert). Not followed after: he meant to go on to Bangui and come back the next day.')
by = {}
for t in T: by.setdefault(t[1], []).append(t)
for t in T:
    nxt = [x for x in by[t[1]] if x[6] > t[6]]
    pos(t[0], t[2], t[3], t[4], t[5], t[6], t[7], nxt[0][4] if nxt else 'unknown', t[8], t[9], t[10], t[11], t[12], SEA if t[12] == 'estimate' else TOWN, t[13], t[14], t[15], t[16], t[17], t[18], t[19])
# Young's row at Vigan now ends when he sails
put('LZ044', 'show_to', D+'12-10'); put('LZ044', 'end_earliest', D+'12-11'); put('LZ044', 'end_latest', D+'12-11')
TR = wb['Tracks']; th = head(TR)
for r in TR.iter_rows(min_row=2):
    if r[0].value == 'luzon1899' and r[1].value == 'L-YOUNG': r[th.index('rows')].value += '; LZ121'
ECH = {'L-33CO': 'company'}
for trk, rows in by.items():
    if trk != 'L-YOUNG':
        add('Tracks', {'playback_id': 'luzon1899', 'track_id': trk, 'unit_id': rows[0][2], 'rows': '; '.join(x[0] for x in rows), 'echelon': ECH.get(trk, 'detachment'), 'hide_after_last_row': 'yes'})

# ---------------------------------------------------------------- routes: up and down the coast of Ilocos, clear of the land; the lake and the rivers
COAST = [FAB, (16.400, 120.270), (16.600, 120.240), SF, (16.850, 120.300), (17.050, 120.370), (17.250, 120.370), (17.450, 120.370), VIG, (17.750, 120.350), (17.980, 120.420), LAO]
def coast(a, b):
    i, j = COAST.index(a), COAST.index(b)
    return COAST[i + 1:j] if i < j else COAST[j + 1:i][::-1]
LAKE = [(14.5605, 121.0765), (14.535, 121.105), (14.420, 121.130), (14.300, 121.200), (14.240, 121.300)]
BAY_GUAGUA = [(14.600, 120.940), (14.720, 120.780), (14.800, 120.680), (14.880, 120.630)]
BAY_RIO = [(14.880, 120.630), (14.790, 120.680), (14.780, 120.720), (14.840, 120.740)]
R = [
    ('LZ098', 'LZ099', LAKE, 'S65 p. 189: "towed by three of our gunboats, he proceeded across the lake on April 9". The track is not given: drawn down the Pasig and round the south of Talim Island, as the expedition\'s is.', 'low', 'S65'),
    ('LZ099', 'LZ100', LAKE[::-1], 'S65 p. 190: "He returned on April 17". The way back is taken to be the way out.', 'low', 'S65'),
    ('LZ100', 'LZ101', BAY_GUAGUA, 'S65 p. 195: "from Manila to Guagua"; "He found the entrance of the Guagua River without difficulty, proceeded up stream until Sexmoan was reached". Drawn across the head of Manila Bay; the channel is not given.', 'low', 'S65'),
    ('LZ101', 'LZ102', BAY_RIO, 'S65 p. 196: back to Manila, then "to find the mouth of the Rio Grande and pass up that stream to Calumpit". The call at Manila on the 9th is not drawn.', 'low', 'S65'),
    ('LZ102', 'LZ103', [(15.0400, 120.7919)], 'S65 p. 198: up the Rio Grande by San Luis to Candaba.', 'medium', 'S65'),
    ('LZ103', 'LZ104', [], 'S65 p. 200: "Kobbe and gunboats started up river this morning at six."', 'low', 'S65'),
    ('LZ105', 'LZ106', coast(SF, VIG), 'S75 (Parker): up the coast to the anchorage near Vigan. Drawn clear of the land.', 'low', 'S75'),
    ('LZ107', 'LZ108', coast(VIG, LAO), 'S74 (Young): "I left Vigan 8 a. m. on Samar, reaching Laoag" that afternoon. Drawn clear of the land.', 'low', 'S74'),
    ('LZ109', 'LZ110', coast(FAB, VIG), 'S75 (Parker): "The Oregon has gone to Vigan." Drawn clear of the land.', 'low', 'S75'),
    ('LZ111', 'LZ112', coast(VIG, FAB), 'S74: she reached San Fabian on the 27th with news of Vigan. Drawn clear of the land.', 'low', 'S74'),
    ('LZ112', 'LZ113', coast(FAB, VIG), 'S74: "one company proceeding to that point by gunboat which would reach there the following day". Drawn clear of the land.', 'low', 'S74'),
    ('LZ114', 'LZ115', [FAB] + coast(FAB, VIG) + [VIG], 'S74: by the gunboat Callao to Vigan, then ashore. Drawn clear of the land.', 'low', 'S74'),
    ('LZ044', 'LZ121', [VIG] + coast(VIG, LAO) + [LAO], 'S74 (Young): "I left Vigan 8 a. m. on Samar, reaching Laoag" that afternoon. Drawn clear of the land, then ashore.', 'low', 'S74'),
]
k = max(int(str(r[0].value)[2:]) for r in wb['Routes'].iter_rows(min_row=2) if r[0].value and str(r[0].value).startswith('RL'))
fmt = lambda p: '%.5f, %.5f' % (p[0], p[1])
for a, b, way, wording, conf, src in R:
    k += 1; pts = [(val(a, 'lat'), val(a, 'lon'))] + list(way) + [(val(b, 'lat'), val(b, 'lon'))]
    add('Routes', {'route_id': 'RL%02d' % k, 'campaign_id': 'PHW-LUZ99', 'battle_id': val(b, 'battle_id'), 'unit_id': val(b, 'unit_id'), 'kind': 'voyage', 'start': val(a, 'show_to'), 'end': val(b, 'show_from'),
                   'from_pos_id': a, 'to_pos_id': b, 'waypoints (lat, lon; ...)': '; '.join(fmt(p) for p in pts), 'source_ids': src, 'source_wording': wording, 'confidence': conf,
                   'notes': 'By water. The track is not in the report.', 'playback': 'yes'})

# ---------------------------------------------------------------- events
E = wb['Events']; eh = head(E)
for r in E.iter_rows(min_row=2):
    extra = {'LE02': 'LZ096', 'LE05': 'LZ099', 'LE14': 'LZ105', 'LE15': 'LZ110; LZ106; LZ117', 'LE18': 'LZ118'}.get(r[0].value)
    if extra:
        c = r[eh.index('pos_ids')]; c.value = (c.value + '; ' if c.value else '') + extra
add('Events', {'event_id': 'LE20', 'campaign_id': 'PHW-LUZ99', 'battle_id': YO, 'time_earliest': D+'12-10', 'time_latest': D+'12-11', 'name': 'Laoag',
               'summary': 'The Wheeling lands a force at Laoag on the 10th, where some 1,500 Spanish prisoners are found. Young follows by sea in the Samar on the 11th to direct the pursuit of Tinio, who holds the American prisoners.',
               'pos_ids': 'LZ119; LZ120; LZ121; LZ108', 'source_ids': 'S74', 'timeline': 'name', 'playback_at': D+'12-11', 'playback_label': 'Laoag',
               'playback_text': 'The Navy lands a force at Laoag, and Young follows from Vigan by sea in the gunboat Samar. His columns are in the mountains after Tinio, who holds the American prisoners.'})

# ---------------------------------------------------------------- settings: Luzon plays at a day a second and skips the quiet stretches; a note on ships in both playbacks
PS = wb['Playback settings']; h = head(PS); hit = 0; nxt = {'luzon1899': 1, 'manila': 1}
for r in PS.iter_rows(min_row=2):
    pb, key = r[0].value, str(r[h.index('setting')].value)
    if pb == 'luzon1899' and key == 'rate': r[h.index('value')].value = 1; r[h.index('what it does')].value = 'Days played per second (1 since 21 Nov 2026, so the moves and the arrows ahead of them can be followed; it was a week a second)'; hit += 1
    if pb in nxt and key.startswith('about.'): nxt[pb] = max(nxt[pb], int(key.split('.')[1]) + 1)
assert hit == 1
for kv in [('skip.1.from', D+'06-04'), ('skip.1.to', D+'08-11'), ('skip.1.after_seconds', 3), ('skip.1.note', 'The rains: nothing on record moves until August. On to 11 August.'),
           ('skip.2.from', D+'08-20'), ('skip.2.to', D+'10-10'), ('skip.2.after_seconds', 3), ('skip.2.note', 'MacArthur holds Angeles while new regiments arrive. On to 10 October and the fall campaign.')]:
    add('Playback settings', {'playback_id': 'luzon1899', 'setting': kv[0], 'value': kv[1], 'what it does': 'While playing, a quiet stretch is shown for a moment and then skipped' if kv[0].endswith('from') else None})
SHIPS = 'Ships are drawn where the reports read have them firing in support of the troops, landing men or carrying them. Their places on the water are estimates (the reports say "off" a town and no more), and this is the Army\'s account: no naval report was read.'
for pb in ('luzon1899', 'manila'):
    add('Playback settings', {'playback_id': pb, 'setting': 'about.%d' % nxt[pb], 'value': SHIPS})
add('Gaps', {'gap_id': 'G-LZ9', 'battle_id': YO, 'gap': 'Ships are placed from the Army\'s reports alone',
             'effect on the data': 'Ship positions are estimates off the towns named; several ships are unnamed (Caloocan, the southern flank at Manila); when ships came and went is mostly not given, so symbols appear for the action and fade.',
             'how to close it': 'The Navy Department\'s annual reports for 1899 and 1900 (Watson, McCalla, Wilde) and the ships\' logs.', 'status in v2': 'Open (21 Nov 2026).'})
wb.save(WB)
print('ship and landing units', len(U), 'position rows', len(T) + 2, 'routes', len(R))
