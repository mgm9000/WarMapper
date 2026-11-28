"""The orientation test: a playback of made-up events, to try the orientation style without Morgan's data.

Everything here is invented: a war called "Test war", three sides (Red, Blue, Black), places with made-up names on the ground of South
Carolina (so the modern topographic map has something to show), and a dozen events over 1801 to 1803. None of it is history. It is built
from rows in this file, laid on top of the real workbooks in memory, by the same exporter every battle uses, so it tests the
real path: rows -> tools/export_battles.py -> pipeline/battlefile.py -> app/player.js. Nothing is written to the workbooks.

  python3 tests/orientation/make_demo.py        write tests/orientation/demo/battle.json and index.html, and run the orientation checks

Since 27 Nov 2026 (Session 1 of claude/sc-storyline-prompt.md) it also builds a made-up chapter of three playbacks that follow one another:
  - the orientation above, now with forces on the move (one marching along a straight line to its fight, one of "Dragoons" coming in from
    beyond the map's edge, a standing pair at a clash), each tied to its event (the connection rule), and a closing summary with a bridge;
  - campaign-test: a made-up campaign orientation on a made-up regional map, played in two legs with callouts, two armies that stay on the
    map, a light corps for part of it, a route that follows a traced road (along_recon), flags at its closing stop, and Next;
  - battle-test: a made-up battle whose battlefield map lies over the regional map (bases.region), with one symbol a side when zoomed out,
    an end summary with a bridge, and Next to the course page.
It then runs the connection rule on a made-up movement that misses its event (it must fail) and the storyline gate on the chapter (it must
pass, and fail once a bridge is taken away).

What it exercises: a win for each side (red square, blue circle, black triangle), an indecisive clash (grey diamond), captures (flags),
ships, two disputed results (dagger, both readings), an event with no clash, a busy month (February 1803, five events), a gap year (1802),
an event-by-event opening (1801 to 1802, half a second an event) with a stop and a recap at the end of 1802, year summaries
and the closing summary, and places that change hands (one contested, one held by the Black side until it is lost).
"""
import copy, contextlib, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import export_battles as E, battlefile as bf, build, consistency_check as CC

OUT = os.path.join(HERE, 'demo')
PB = 'orientation-test'
CPB, BPB = 'campaign-test', 'battle-test'
FIX = os.path.join(HERE, 'fixtures')

SIDES = [('TST-RD', 'RD', 'Red side', 'Red', 'red'), ('TST-BL', 'BL', 'Blue side', 'Blue', 'blue'), ('TST-BK', 'BK', 'Black side', 'Black', 'black')]
SOURCES = [('TS1', 'Made-up source A (test data)'), ('TS2', 'Made-up source B (test data)'), ('TS3', 'Made-up source C (test data)')]
# id, date (or from;to), name, text
EVENTS = [
    ('X01', '1801-03-10', 'Fort Alpha taken', 'The Red side takes Fort Alpha without a fight.'),
    ('X02', '1801-05-02', 'Bravo Ford', 'The Blue side wins at Bravo Ford.'),
    ('X12', '1801-06-01', 'A truce is talked of', 'An event with no clash: nothing is drawn on the map for it.'),
    ('X03', '1801-07-15', 'Charlie Town', 'The Black side beats a Blue column near Charlie Town.'),
    ('X04', '1801-07-20', 'Delta Hill', 'A fight at Delta Hill that neither side wins.'),
    ('X05', '1801-09-05;1801-09-07', 'Echo Bay', 'Red ships and troops attack at Echo Bay. The sources disagree on who won.'),
    ('X06', '1803-02-03', 'Foxtrot Mill', 'The Red side wins at Foxtrot Mill.'),
    ('X07', '1803-02-09', 'Golf Crossroads', 'The Blue side wins at Golf Crossroads.'),
    ('X08', '1803-02-14', 'Hotel Depot taken', 'The Blue side takes the Hotel depot and its stores.'),
    ('X09', '1803-02-20', 'Testport', 'The Red side holds Testport against an attack.'),
    ('X10', '1803-02-26', 'India Swamp', 'A skirmish at India Swamp. The sources disagree on whether anyone won.'),
    ('X11', '1803-04-01', 'Juliet Field', 'The Blue side wins the last fight in this list.'),
]
# id, event, kind, won_by, lat, lon, place, result, captured, captured_by, ships, disputed (other_won_by, other_reading, other sources), confidence, sources
CLASHES = [
    ('XC01', 'X01', 'capture', 'RD', 34.95, -81.95, 'Fort Alpha', 'Fort Alpha taken without a fight', 'The fort and its powder', 'RD', None, None, 'medium', 'TS1'),
    ('XC02', 'X02', 'fight', 'BL', 34.62, -81.20, 'Bravo Ford', 'Blue victory at the ford', None, None, None, None, 'medium', 'TS1'),
    ('XC03', 'X03', 'fight', 'BK', 34.80, -82.85, 'near Charlie Town', 'The Black side ambushes a Blue column', None, None, None, None, 'low', 'TS2'),
    ('XC04', 'X04', 'fight', 'indecisive', 34.20, -82.10, 'Delta Hill', 'Both sides withdraw', None, None, None, None, 'medium', 'TS1; TS2'),
    ('XC05', 'X05', 'fight', 'RD', 32.75, -79.85, 'Echo Bay', 'The Red side lands and holds the shore', '40 prisoners', 'RD', 'RD',
     ('BL', 'Source C says the Blue battery drove the ships off and the landing failed.', 'TS3'), 'medium', 'TS1'),
    ('XC06', 'X06', 'fight', 'RD', 34.30, -80.60, 'Foxtrot Mill', 'Red victory', None, None, None, None, 'medium', 'TS2'),
    ('XC07', 'X07', 'fight', 'BL', 34.75, -80.85, 'Golf Crossroads', 'Blue victory', None, None, None, None, 'medium', 'TS2'),
    ('XC08', 'X08', 'capture', 'BL', 33.70, -80.40, 'Hotel Depot', 'The depot taken', '50 wagons of stores', 'BL', None, None, 'low', 'TS1'),
    ('XC09', 'X09', 'fight', 'RD', 32.80, -79.95, 'Testport', 'The attack on the town is beaten off', None, None, None, None, 'medium', 'TS1'),
    ('XC10', 'X10', 'fight', 'indecisive', 33.40, -79.60, 'India Swamp', 'Neither side holds the field', None, None, None,
     ('BL', 'Source B scores it a Blue victory.', 'TS2'), 'low', 'TS1'),
    ('XC11', 'X11', 'fight', 'BL', 34.10, -81.05, 'Juliet Field', 'Blue victory', None, None, None, None, 'medium', 'TS3'),
]
# place id, name, kind, lat, lon, changes: (date, held_by, basis, event)
PLACES = [
    ('XP1', 'Testport', 'port', 32.79, -79.93, [('1801-01-01', 'RD', 'Held from the start', None), ('1803-02-20', 'contested', 'Under attack', 'X09'),
                                                ('1803-04-01', 'BL', 'Given up after Juliet Field', 'X11')]),
    ('XP2', 'Fort Alpha', 'fort', 34.95, -81.95, [('1801-01-01', 'BL', 'Held from the start', None), ('1801-03-10', 'RD', 'Taken', 'X01')]),
    ('XP3', 'Charlie Town', 'settlement', 34.85, -82.95, [('1801-01-01', 'BK', 'A Black town', None), ('1802-06-01', 'BL', 'Given up by treaty', None)]),
    ('XP4', 'Bravo', 'village', 34.66, -81.25, [('1801-01-01', 'contested', 'No side holds it', None), ('1801-05-02', 'BL', 'After the ford', 'X02')]),
    ('XP5', 'Kilo', 'town', 34.25, -80.65, [('1801-01-01', 'RD', 'A Red post', None)]),
]
SUMMARIES = [('year', '1801-01-01', '1801-12-31', '1801: the first year', 'Made-up summary of 1801: a fort taken, a ford won, an ambush, a draw and a landing.'),
             ('year', '1802-01-01', '1802-12-31', '1802: a gap in the list', 'The made-up list has nothing for 1802. The gap is flagged on the map and the timeline.'),
             ('year', '1803-01-01', '1803-12-31', '1803: the busy year', 'Made-up summary of 1803: five events in February, and the last fight in April.'),
             ('end', '1803-04-15', '1803-04-15', 'Where things stood on 15 April 1803', 'The made-up closing summary: Blue holds the port, Red the inland posts.')]
BRIDGE = {PB: 'A year later the two armies meet again in the north: the next section follows them day by day.',
          CPB: 'On the morning of 20 March the Red army turns to fight at Quebec Hill: the next section is the battle.',
          BPB: 'After the battle the Red army falls back to the coast. Nothing further is built: Next returns to the course page.'}

# forces on the move in the orientation (27 Nov 2026): unit, label, side, branch, echelon, hide_after, [(pos id, date or from;to, lat, lon, place, callout, precision)]
MOVES = [('TU-RD1', 'Red column', 'TST-RD', 'infantry', 'army', True, [('TP01', '1803-03-20', 33.30, -81.60, 'Kilo: the column sets out', None, 3000),
                                                                      ('TP02', '1803-03-26', 33.75, -81.30, 'on the road north', None, 5000),
                                                                      ('TP03', '1803-04-01', 34.10, -81.05, 'Juliet Field', 'Beaten at Juliet Field, the column turns back.', 2000)]),
         ('TU-BL1', 'Blue riders', 'TST-BL', 'dragoons', 'detachment', True, [('TP04', '1803-01-26', 36.45, -81.70, 'Sierra Shoals, beyond the map: the riders gather', None, 5000),
                                                                              ('TP05', '1803-02-03', 35.30, -81.10, 'at the river', None, 5000),
                                                                              ('TP06', '1803-02-09', 34.75, -80.85, 'Golf Crossroads', 'The riders arrive in time to carry the crossroads.', 2000)]),
         ('TU-RD2', 'Red post', 'TST-RD', 'infantry', 'detachment', True, [('TP07', '1803-02-03', 34.30, -80.60, 'Foxtrot Mill', None, 2000)]),
         ('TU-BL2', 'Blue raiders', 'TST-BL', 'infantry', 'detachment', True, [('TP08', '1803-02-03', 34.30, -80.60, 'Foxtrot Mill', None, 2000)])]
MOVE_EVENTS = {'X11': 'TP03', 'X07': 'TP06', 'X06': 'TP07; TP08'}

# the made-up campaign orientation, in two legs
C_EVENTS = [('Y01', '1804-03-06', 'Kilo Ford', 'The Red army forces the ford.', 'B3; R3'), ('Y03', '1804-03-13', 'Mike Crossroads', 'The light corps and the Red van skirmish; neither holds the field.', 'L3'),
            ('Y02', '1804-03-15', 'Lima Mill', 'The Blue army turns and wins at Lima Mill.', 'B5; R5')]
C_CLASHES = [('YC1', 'Y01', 'RD', 35.20, -81.10, 'Kilo Ford'), ('YC3', 'Y03', 'indecisive', 35.60, -81.00, 'Mike Crossroads'), ('YC2', 'Y02', 'BL', 35.70, -80.20, 'Lima Mill')]
C_MOVES = [('TC-BL', 'Blue army', 'TST-BL', 'infantry', 'army', False, [('B1', '1804-03-01', 34.40, -82.10, 'Alpha Springs, where the army sets out', None, 3000),
                                                                      ('B2', '1804-03-04', 34.85, -81.65, 'on the river road', None, 3000),
                                                                      ('B3', '1804-03-06', 35.20, -81.10, 'Kilo Ford', 'Holds the ford for a morning, then gives way to the Red army.', 2000),
                                                                      ('B4', '1804-03-12', 35.55, -80.40, 'beyond Oscar', None, 3000),
                                                                      ('B5', '1804-03-15', 35.70, -80.20, 'Lima Mill', 'Turns on the Red army at Lima Mill and wins.', 2000),
                                                                      ('B6', '1804-03-19', 35.62, -80.33, 'in camp near Lima Mill', None, 3000)]),
           ('TC-RD', 'Red army', 'TST-RD', 'infantry', 'army', False, [('R1', '1804-03-01', 34.20, -81.50, 'Papa, where the army sets out', None, 3000),
                                                                     ('R2', '1804-03-04', 34.80, -81.30, 'on the north road', None, 3000),
                                                                     ('R3', '1804-03-06', 35.19, -81.11, 'Kilo Ford', 'Forces the ford and follows north.', 2000),
                                                                     ('R4', '1804-03-12', 35.45, -80.70, 'a day behind the Blue army', 'Follows the Blue army north, a day behind.', 3000),
                                                                     ('R5', '1804-03-15', 35.70, -80.21, 'Lima Mill', None, 2000),
                                                                     ('R6', '1804-03-19', 35.40, -80.60, 'falling back south', None, 3000)]),
           ('TC-LC', 'Blue light corps', 'TST-BL', 'dragoons', 'detachment', True, [('L1', '1804-03-08', 35.30, -80.95, 'leaving the army', None, 3000),
                                                                                   ('L2', '1804-03-11', 35.50, -81.10, 'west of the road', 'Draws the Red van west, away from the army.', 3000),
                                                                                   ('L3', '1804-03-13', 35.60, -81.00, 'Mike Crossroads', None, 2000)])]
C_ROUTES = [('TCR1', 'B1', 'B2', 'TR-RD1'), ('TCR2', 'B2', 'B3', 'TR-RD1'), ('TCR3', 'B3', 'B4', 'TR-RD1')]   # along the made-up traced road
C_PLACES = [('YP1', 'Oscar', 'town', 35.55, -80.45, [('1804-03-01', 'BL', 'A Blue town', None)]), ('YP2', 'Papa', 'town', 34.20, -81.50, [('1804-03-01', 'RD', 'A Red town', None)])]
C_SUMMARIES = [('leg', '1804-03-01', '1804-03-09', 'To Kilo Ford', 'The made-up first leg: both armies march north, and the Red army forces the ford at Kilo.'),
               ('leg', '1804-03-10', '1804-03-19', 'The turn at Lima Mill', 'The made-up second leg: the light corps draws the Red van west, and the Blue army turns and wins at Lima Mill.'),
               ('end', '1804-03-20', '1804-03-20', 'Where things stood on 20 March 1804', 'The made-up closing summary of the campaign.')]
REGION_LABELS = [('Alpha Springs', 34.40, -82.10, 'town'), ('Oscar', 35.55, -80.45, 'town'), ('Quebec Hill', 35.30, -81.10, 'town'), ('Kilo', 33.30, -81.60, 'town')]

# the made-up battle, on a field inside the regional map
B_UNITS = [('TB-BL1', 'Blue 1st Brigade', 'Blue 1st', 'TST-BL', 'infantry', 'brigade'), ('TB-BL2', 'Blue horse', 'Blue horse', 'TST-BL', 'cavalry', 'regiment'),
           ('TB-RD1', 'Red 1st Brigade', 'Red 1st', 'TST-RD', 'infantry', 'brigade'), ('TB-RD2', 'Red guns', 'Red guns', 'TST-RD', 'artillery', 'battery')]
B_POS = [('Q1', 'TB-BL1', '08:00', '09:00', 35.303, -81.105, 35.297, -81.095), ('Q2', 'TB-BL1', '09:15', '10:00', 35.300, -81.098, 35.294, -81.088),
         ('Q3', 'TB-BL2', '08:00', '10:00', 35.308, -81.110, None, None), ('Q4', 'TB-RD1', '08:00', '09:00', 35.292, -81.112, 35.288, -81.102),
         ('Q5', 'TB-RD1', '09:30', '10:00', 35.284, -81.122, 35.281, -81.113), ('Q6', 'TB-RD2', '08:00', '10:00', 35.289, -81.118, None, None)]
B_EVENTS = [('Z01', '08:15', 'Lines formed', 'Both sides form across the road at Quebec Hill.', 'Q1; Q4'), ('Z02', '09:30', 'Red falls back', 'The Red brigade gives way and falls back south-west.', 'Q5')]
FIELD_LABELS = [('Quebec Hill', 35.300, -81.100, 'place'), ('River road', 35.296, -81.112, 'road')]
SETTINGS = [('based_on', '["orientation", "us-maps"]'), ('page_title', 'Orientation test (made-up events)'), ('clock_title', 'Test: made-up events'),
            ('bases.1.use', 'current'), ('bases.1.id', 'mod'),
            ('orientation.gaps', '[{"from": "1802-01-01", "to": "1802-12-31", "text": "1802: no events in this list (a gap, not a quiet year)."}]'),
            ('orientation.phases', '[{"until": "1802-12-31", "event_seconds": 0.5, "title": "Where things stood at the end of 1802"}]'),
            ('about', '["A test of the orientation style with made-up events. None of it is history."]')]


def rows():
    """The real workbooks' rows, with the made-up war laid on top (in memory only)."""
    with contextlib.redirect_stdout(io.StringIO()): W = copy.deepcopy(E.load())
    W['Wars'].append({'war_id': 'TST', 'name': 'Test war'})
    W['Campaigns'].append({'campaign_id': 'TST-C', 'war_id': 'TST', 'name': 'Test campaign'})
    W['Sides'] += [{'side_id': i, 'war_id': 'TST', 'name': n, 'frame': f, 'code': c, 'short': s} for i, c, n, s, f in SIDES]
    W['Sources'] += [{'source_id': i, 'title': t, 'author': 'Nobody', 'date': '2026', 'citation': 'Made up for the orientation test', 'type': 'Test data',
                      'url': None, 'rights': 'Made up for testing'} for i, t in SOURCES]
    W['Playbacks'].append({'playback_id': PB, 'battle_file_id': 'orientation-test', 'campaign_id': 'TST-C', 'record_battles': None,
                           'title': 'Orientation test: made-up events, 1801 to 1803', 'subtitle': 'Not history: rows made up to test the orientation style',
                           'time_unit': 'day', 'time_zero': '1801-01-01', 'time_start': '1801-01-01', 'time_end': '1803-04-15', 'focus_start': None, 'focus_end': None,
                           'calendar_first': '1801-01-01', 'days_numbered': 'no', 'calendar_days': None, 'origin_lat': 33.8, 'origin_lon': -81.0,
                           'west': -83.4, 'south': 32.0, 'east': -78.5, 'north': 35.25, 'opening_label': 'Before the first event',
                           'opening_text': 'A test with made-up events. Press play: the clashes come onto the map month by month.'})
    W['Playback settings'] += [{'playback_id': PB, 'setting': k, 'value': v} for k, v in SETTINGS]
    for i, d, n, tx in EVENTS:
        a, b = (d.split(';') + [d])[:2]
        W['Events'].append({'event_id': i, 'campaign_id': 'TST-C', 'battle_id': None, 'time_earliest': a, 'time_latest': b, 'name': n, 'summary': tx,
                            'pos_ids': None, 'source_ids': 'TS1', 'timeline': 'name', 'playback_at': None, 'playback_label': None, 'playback_text': None})
    for (i, ev, kind, won, lat, lon, place, res, cap, capby, ships, other, conf, src) in CLASHES:
        W['Clashes'].append({'clash_id': i, 'playback_id': PB, 'event_id': ev, 'kind': kind, 'won_by': won, 'result_method': 'stated', 'result': res, 'captured': cap,
                             'captured_by': capby, 'ships': ships, 'disputed': 'yes' if other else None, 'other_won_by': other and other[0],
                             'other_reading': other and other[1], 'other_source_ids': other and other[2], 'hypothesis_id': None, 'place': place, 'lat': lat, 'lon': lon,
                             'coord_source': 'estimate', 'coord_precision_m': 2000, 'coordinate_basis': 'Made up', 'coordinate_confidence': 'low',
                             'overall_confidence': conf, 'source_ids': src, 'notes': None, 'review_status': 'Test data'})
    for pid, name, kind, lat, lon, ch in PLACES:
        W['Control places'].append({'cplace_id': pid, 'playback_id': PB, 'name': name, 'kind': kind, 'lat': lat, 'lon': lon, 'coord_source': 'estimate',
                                    'coord_precision_m': 1000, 'coordinate_basis': 'Made up', 'coordinate_confidence': 'low', 'source_ids': 'TS1', 'notes': None})
        for n, (d, by, basis, ev) in enumerate(ch):
            W['Control'].append({'control_id': '%s-%d' % (pid, n + 1), 'cplace_id': pid, 'from': d, 'held_by': by, 'basis': basis, 'event_id': ev,
                                 'method': 'stated', 'confidence': 'medium', 'source_ids': 'TS1', 'notes': None, 'review_status': 'Test data'})
    W['Summaries'] += [{'playback_id': PB, 'kind': k, 'from': a, 'to': b, 'title': ti, 'text': tx, 'source_ids': 'TS2'} for k, a, b, ti, tx in SUMMARIES]
    return W


def rows_storyline(W):
    """The made-up chapter (27 Nov 2026): movements in the orientation, the campaign and the battle, the shared regional map, Next links."""
    W['Campaigns'] += [{'campaign_id': 'TST-C2', 'war_id': 'TST', 'name': 'Test campaign, 1804'}, {'campaign_id': 'TST-C3', 'war_id': 'TST', 'name': 'Test battle, 1804'}]
    pos = lambda pid, camp, uid, a, b, lat, lon, place, callout, prec, lat2=None, lon2=None: {
        'pos_id': pid, 'campaign_id': camp, 'unit_id': uid, 'battle_id': None, 'start_earliest': a, 'start_latest': a, 'end_earliest': b, 'end_latest': b,
        'show_from': None, 'show_to': None, 'lat': lat, 'lon': lon, 'via': None, 'line_end_lat': lat2, 'line_end_lon': lon2, 'map_id': None, 'map_xy': None,
        'moves_along_line': None, 'arrive_at_pace': None, 'activity': 'On the move' if callout is None else 'Arrives', 'place_description': place, 'source_wording': None,
        'position_method': 'inferred', 'overall_confidence': 'low', 'time_basis': 'Made up', 'coord_source': 'estimate', 'coordinate_basis': 'Made up',
        'coordinate_confidence': 'low', 'coord_precision_m': prec, 'source_ids': 'TS1', 'notes': None, 'review_status': 'Test data', 'callout': callout}
    def forces(camp, pb, moves):
        for uid, label, side, branch, ech, hide, steps in moves:
            W['Units'].append({'unit_id': uid, 'unit_name': label, 'map_label': label, 'side_id': side, 'nation': None, 'branch': branch, 'echelon': ech, 'source_ids': 'TS1', 'notes': None})
            W['Tracks'].append({'track_id': uid, 'playback_id': pb, 'unit_id': uid, 'rows': '; '.join(x[0] for x in steps), 'hide_after_last_row': 'yes' if hide else None})
            for pid, d, lat, lon, place, callout, prec in steps:
                a, b = (d.split(';') + [d])[:2]; W['Positions'].append(pos(pid, camp, uid, a, b, lat, lon, place, callout, prec))
    forces('TST-C', PB, MOVES)
    for e in W['Events']:
        if e['event_id'] in MOVE_EVENTS: e['pos_ids'] = MOVE_EVENTS[e['event_id']]
    # the campaign orientation
    W['Playbacks'].append({'playback_id': CPB, 'battle_file_id': CPB, 'campaign_id': 'TST-C2', 'record_battles': None, 'title': 'Campaign test: made-up legs, March 1804',
                           'subtitle': 'Not history: two legs, two armies and a light corps', 'time_unit': 'day', 'time_zero': '1804-03-01', 'time_start': '1804-03-01',
                           'time_end': '1804-03-20', 'focus_start': None, 'focus_end': None, 'calendar_first': '1804-03-01', 'days_numbered': 'no', 'calendar_days': None,
                           'origin_lat': 35.0, 'origin_lon': -81.2, 'west': -82.6, 'south': 34.0, 'east': -79.9, 'north': 35.9, 'opening_label': 'Before the first leg',
                           'opening_text': 'Picking up from the orientation: the two armies set out north. Press play.'})
    TERR = lambda ext, z: json.dumps({'extent': ext, 'zoom': z, 'open_m': 300, 'smooth_m': 400, 'relief': 6, 'doubt': False, 'spots_from': 9.6,
                                      'steps': [[0, 100, 500], [8.6, 50, 250], [10.2, 20, 100], [11.6, 10, 50]] if z < 12 else [[0, 20, 100], [12.4, 5, 25], [14.4, 1, 5]]})
    REG = [-83.0, 33.5, -79.5, 36.5]
    for k, v in [('based_on', '["orientation", "us-maps"]'), ('page_title', 'Campaign test (made-up legs)'), ('clock_title', 'Test: made-up campaign'),
                 ('bases.1.id', 'rgn'), ('bases.1.label', '1800 (made-up)'), ('bases.1.short', '1800'), ('bases.1.recon', 'test-region'), ('bases.1.terrain', TERR(REG, 8)),
                 ('bases.2.use', 'current'), ('bases.2.id', 'mod'), ('orientation.flags.sides', '{"RD": "union-1606", "BL": "stars-stripes-1777"}'),
                 ('about', '["A test of a campaign played in legs, with made-up rows. None of it is history."]')]:
        W['Playback settings'].append({'playback_id': CPB, 'setting': k, 'value': v})
    for i, d, n, tx, ps in C_EVENTS:
        W['Events'].append({'event_id': i, 'campaign_id': 'TST-C2', 'battle_id': None, 'time_earliest': d, 'time_latest': d, 'name': n, 'summary': tx, 'pos_ids': ps,
                            'source_ids': 'TS1', 'timeline': 'name', 'playback_at': None, 'playback_label': None, 'playback_text': None})
    for i, ev, won, lat, lon, place in C_CLASHES:
        W['Clashes'].append({'clash_id': i, 'playback_id': CPB, 'event_id': ev, 'kind': 'fight', 'won_by': won, 'result_method': 'stated', 'result': place + ': made-up result',
                             'captured': None, 'captured_by': None, 'ships': None, 'disputed': None, 'other_won_by': None, 'other_reading': None, 'other_source_ids': None,
                             'hypothesis_id': None, 'place': place, 'lat': lat, 'lon': lon, 'coord_source': 'estimate', 'coord_precision_m': 2000, 'coordinate_basis': 'Made up',
                             'coordinate_confidence': 'low', 'overall_confidence': 'medium', 'source_ids': 'TS1', 'notes': None, 'review_status': 'Test data'})
    forces('TST-C2', CPB, C_MOVES)
    for rid, a, b, road in C_ROUTES:
        W['Routes'].append({'route_id': rid, 'campaign_id': 'TST-C2', 'from_pos_id': a, 'to_pos_id': b, 'playback': 'yes', 'kind': None, 'waypoints (lat, lon; ...)': None, 'along_recon': road})
    for pid, name, kind, lat, lon, ch in C_PLACES:
        W['Control places'].append({'cplace_id': pid, 'playback_id': CPB, 'name': name, 'kind': kind, 'lat': lat, 'lon': lon, 'coord_source': 'estimate', 'coord_precision_m': 1000,
                                    'coordinate_basis': 'Made up', 'coordinate_confidence': 'low', 'source_ids': 'TS1', 'notes': None})
        for n, (d, by, basis, ev) in enumerate(ch):
            W['Control'].append({'control_id': '%s-%d' % (pid, n + 1), 'cplace_id': pid, 'from': d, 'held_by': by, 'basis': basis, 'event_id': ev, 'method': 'stated',
                                 'confidence': 'medium', 'source_ids': 'TS1', 'notes': None, 'review_status': 'Test data'})
    W['Summaries'] += [{'playback_id': CPB, 'kind': k, 'from': a, 'to': b, 'title': ti, 'text': tx, 'source_ids': 'TS2', 'bridge': BRIDGE[CPB] if k == 'end' else None} for k, a, b, ti, tx in C_SUMMARIES]
    for x in W['Summaries']:
        if x['playback_id'] == PB and x['kind'] == 'end': x['bridge'] = BRIDGE[PB]
    W['Labels'] += [{'playback_id': CPB, 'text': t, 'other_name': None, 'lat': lat, 'lon': lon, 'angle': None, 'level': 0, 'kind': k, 'show': 'recon', 'approximate': None, 'recon': 'test-region'}
                    for t, lat, lon, k in REGION_LABELS]
    # the made-up maps: a regional sheet the campaign owns, a battlefield the battle owns
    for rid, pb, f, title in [('test-region', CPB, 'test-region.geojson', 'A made-up region, 1800: a WarMapper test'), ('test-field', BPB, 'test-field.geojson', 'A made-up field, 1804: a WarMapper test')]:
        W['Reconstructions'].append({'recon_id': rid, 'playback_id': pb, 'title': title, 'label': 'Made-up', 'about': 'Made up for the storyline test. None of it is history.',
                                     'credit': 'WarMapper test data', 'file': os.path.relpath(os.path.join(FIX, f), ROOT), 'made': '2026-11-27', 'review_status': 'Test data', 'notes': None, 'style': None})
    for rid, lid, kind in [('test-region', 'water', 'stream'), ('test-region', 'roads', 'road'), ('test-region', 'bounds', 'boundary'), ('test-field', 'froads', 'road'), ('test-field', 'fwater', 'stream')]:
        W['Recon layers'].append({'recon_id': rid, 'layer_id': lid, 'title': 'Made-up ' + lid, 'kind': kind, 'source_id': 'TS1', 'link': None, 'link_label': None, 'method': 'traced',
                                  'confidence': 'low', 'from': '1800-01-01', 'to': '1810-12-31', 'how_read': 'Made up', 'review_status': 'Test data', 'notes': None, 'order': 1})
    # the made-up battle
    W['Playbacks'].append({'playback_id': BPB, 'battle_file_id': BPB, 'campaign_id': 'TST-C3', 'record_battles': None, 'title': 'Battle test: Quebec Hill, 20 March 1804',
                           'subtitle': 'Not history: a made-up battle over the made-up region', 'time_unit': 'minute', 'time_zero': '1804-03-20T00:00', 'time_start': '1804-03-20T08:00',
                           'time_end': '1804-03-20T10:00', 'focus_start': None, 'focus_end': None, 'calendar_first': '1804-03-20', 'days_numbered': 'no', 'calendar_days': None,
                           'origin_lat': 35.30, 'origin_lon': -81.10, 'west': -81.13, 'south': 35.28, 'east': -81.07, 'north': 35.315, 'opening_label': 'Before the battle',
                           'opening_text': 'Picking up from the campaign: on the morning of 20 March the Red army turns to fight at Quebec Hill.'})
    for k, v in [('based_on', '["tactical", "us-maps"]'), ('page_title', 'Battle test (made-up)'), ('clock_title', 'Quebec Hill (test)'),
                 ('bases.1.id', 'r04t'), ('bases.1.label', '1804 (made-up)'), ('bases.1.short', '1804'), ('bases.1.recon', 'test-field'),
                 ('bases.1.terrain', TERR([-81.16, 35.27, -81.04, 35.33], 13)), ('bases.1.region', 'rgn'),
                 ('bases.2.use', 'current'), ('bases.2.id', 'mod'),
                 ('bases.3.id', 'rgn'), ('bases.3.label', 'The region, 1800 (made-up)'), ('bases.3.short', 'Region'), ('bases.3.recon', 'test-region'), ('bases.3.hidden', True),
                 ('bases.3.note', 'The made-up regional map the battlefield lies on.'), ('bases.3.terrain', TERR(REG, 8)),
                 ('groups', '[{"side": "BL", "below": 0.03, "label": "Blue army", "echelon": "army"}, {"side": "RD", "below": 0.03, "label": "Red army", "echelon": "army"}]'),
                 ('opening_zoom_out', 4), ('follow.min', '[700, 520]'), ('follow.margin', 90),
                 ('about', '["A made-up battle over a made-up regional map, to test the hand-off from the region to the field. None of it is history."]')]:
        W['Playback settings'].append({'playback_id': BPB, 'setting': k, 'value': v})
    for uid, name, label, side, br, ech in B_UNITS:
        W['Units'].append({'unit_id': uid, 'unit_name': name, 'map_label': label, 'side_id': side, 'nation': None, 'branch': br, 'echelon': ech, 'source_ids': 'TS1', 'notes': None})
        W['Tracks'].append({'track_id': uid, 'playback_id': BPB, 'unit_id': uid, 'rows': None})
    for pid, uid, a, b, lat, lon, lat2, lon2 in B_POS:
        W['Positions'].append(pos(pid, 'TST-C3', uid, '1804-03-20 ' + a, '1804-03-20 ' + b, lat, lon, 'Quebec Hill', None, 100, lat2, lon2))
    for i, a, n, tx, ps in B_EVENTS:
        W['Events'].append({'event_id': i, 'campaign_id': 'TST-C3', 'battle_id': None, 'time_earliest': '1804-03-20 ' + a, 'time_latest': '1804-03-20 ' + a, 'name': n, 'summary': tx,
                            'pos_ids': ps, 'source_ids': 'TS1', 'timeline': 'name', 'playback_at': None, 'playback_label': None, 'playback_text': None})
    W['Summaries'].append({'playback_id': BPB, 'kind': 'end', 'from': '1804-03-20', 'to': '1804-03-20', 'title': 'Quebec Hill: a made-up result',
                           'text': 'The made-up end summary: the Red brigade gives way and the Blue army holds the hill.', 'source_ids': 'TS2', 'bridge': BRIDGE[BPB]})
    W['Labels'] += [{'playback_id': BPB, 'text': t, 'other_name': None, 'lat': lat, 'lon': lon, 'angle': None, 'level': 0, 'kind': k, 'show': 'recon', 'approximate': None, 'recon': 'test-field'}
                    for t, lat, lon, k in FIELD_LABELS]
    W['Next links'] += [{'link_id': 'NT1', 'from_playback': PB, 'to_playback': CPB, 'label': 'The campaign test', 'back_label': 'The orientation test', 'opens_at': None, 'back_opens_at': None, 'chapter': 'test-chapter'},
                        {'link_id': 'NT2', 'from_playback': CPB, 'to_playback': BPB, 'label': 'The battle test', 'back_label': 'The campaign test', 'opens_at': None, 'back_opens_at': None, 'chapter': 'test-chapter'},
                        {'link_id': 'NT3', 'from_playback': BPB, 'to_playback': 'course:hist-340', 'label': 'Back to the course page', 'back_label': None, 'opens_at': None, 'back_opens_at': None, 'chapter': 'test-chapter'}]
    return W


def write(W, name, folder):
    pb = [p for p in W['Playbacks'] if p['playback_id'] == name][0]
    os.makedirs(folder, exist_ok=True)
    battle = bf.write(E.export(pb, W), os.path.join(folder, 'battle.json'))
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(build.page(name, '../../../app', '../../../', folder=folder))
    return battle


def main():
    W = rows_storyline(rows()); bad = 0; files = {}
    for name, folder in ((PB, OUT), (CPB, os.path.join(HERE, 'demo-campaign')), (BPB, os.path.join(HERE, 'demo-battle'))):
        battle = files[name] = write(W, name, folder)
        fail, warn = CC.rules(battle, W)
        for w in warn: print('  warn', w)
        for f in fail: print('  FAIL', f)
        print('%s: %d tracks, %d clashes, %d places, %d events; rules %s' % (name, len(battle['tracks']), len(battle.get('clashes', [])), len(battle.get('places', [])), len(battle['events']), 'kept' if not fail else 'BROKEN'))
        bad += bool(fail)
    # the connection rule must catch a movement that misses its event: move the Red column's last waypoint some 40 km off Juliet Field
    W2 = copy.deepcopy(W)
    for p in W2['Positions']:
        if p['pos_id'] == 'TP03': p['lat'] = 34.45; p['lon'] = -81.40
    import tempfile
    with contextlib.redirect_stdout(io.StringIO()), tempfile.TemporaryDirectory() as td: b2 = bf.write(E.export([p for p in W2['Playbacks'] if p['playback_id'] == PB][0], W2), os.path.join(td, 'battle.json'))
    f2, _ = CC.rules(b2, W2); hit = [f for f in f2 if f.startswith('Connection rule') and 'TP03' in f]
    print('connection rule on a movement that misses its event: %s' % ('caught: ' + hit[0] if hit else 'NOT CAUGHT')); bad += not hit
    # the storyline gate: the made-up chapter passes, and fails once a bridge is gone
    own = {'o': {'playback': PB}, 'c': {'playback': CPB}, 'b': {'playback': BPB}}; ch = {'id': 'test-chapter', 'order': ['o', 'c', 'b'], 'gate': True}
    g1 = build.chapter_gate(ch, own, lambda n: files[n], 'hist-340')
    nb = copy.deepcopy(files); [x.pop('bridge', None) for x in nb[CPB]['summaries'] if x['kind'] == 'end']
    g2 = build.chapter_gate(ch, own, lambda n: nb[n], 'hist-340')
    print('storyline gate on the made-up chapter: %s; with the campaign\'s bridge taken away: %s' % ('passes' if not g1 else 'FAILS: ' + '; '.join(g1), ('fails as it should (%s)' % g2[0]) if g2 else 'PASSES (wrong)'))
    bad += bool(g1) + (not g2)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
