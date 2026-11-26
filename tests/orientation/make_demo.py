"""The orientation test: a playback of made-up events, to try the orientation style without Morgan's data.

Everything here is invented: a war called "Test war", three sides (Red, Blue, Black), places with made-up names on the ground of South
Carolina (so the modern topographic map has something to show), and a dozen events over 1801 to 1803. None of it is history. It is built
from rows in this file, laid on top of the real workbooks in memory, by the same exporter every battle uses, so it tests the
real path: rows -> tools/export_battles.py -> pipeline/battlefile.py -> app/player.js. Nothing is written to the workbooks.

  python3 tests/orientation/make_demo.py        write tests/orientation/demo/battle.json and index.html, and run the orientation checks

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


def main():
    W = rows(); pb = [p for p in W['Playbacks'] if p['playback_id'] == PB][0]
    os.makedirs(OUT, exist_ok=True)
    battle = bf.write(E.export(pb, W), os.path.join(OUT, 'battle.json'))
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(build.page(PB, '../../../app', '../../../', folder=OUT))
    fail, warn = CC.rules(battle, W)
    for w in warn: print('  warn', w)
    for f in fail: print('  FAIL', f)
    print('orientation test: %d clashes, %d places, %d events; rules %s' % (len(battle['clashes']), len(battle['places']), len(battle['events']), 'kept' if not fail else 'BROKEN'))
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
