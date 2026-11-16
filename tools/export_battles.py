"""Write every battle's battle file from the master workbook, or check the ones already written.

The workbook (data/WarMapper battle data.xlsx) is the master copy of the battle data. This script reads it and writes one battle file
per row of its Playbacks sheet (playbacks/<playback>/battle.json, in the format docs/battle-file.md describes). No battle has a script
of its own: a new battle is new rows in the workbook.

  python3 tools/export_battles.py              write all battle files, then check them
  python3 tools/export_battles.py ypres        one battle only
  python3 tools/export_battles.py --check      check the files as they stand, without rewriting them

A battle file that breaks the format is not written. Positions that would have a unit move implausibly fast are listed as warnings.
After exporting, run tools/build.py to put the new data into the pages.
"""
import datetime as dt, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import battlefile as bf

WORKBOOK = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx')
BRANCH = {'horse artillery': 'artillery'}
ECHELON = {'regiment (part)': 'regiment'}
VIRTUAL_NOTE = "Shown leaving its division's last recorded position. Where the unit itself was at this moment is not in the sources read."


def load():
    """Every sheet as a list of rows, each a dict by column heading."""
    import openpyxl
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True, data_only=True); out = {}
    for ws in wb.worksheets:
        it = ws.iter_rows(values_only=True); head = next(it, None)
        if not head: continue
        out[ws.title] = [dict(zip(head, r)) for r in it if r and r[0] not in (None, '')]
    return out


def yes(v): return v is True or str(v or '').strip().lower() in ('yes', 'y', 'true', '1')
def blank(v): return v is None or str(v).strip() == ''
def text(v): return None if blank(v) else (v.strip() if isinstance(v, str) else v)
def num(v): return int(v) if isinstance(v, float) and v.is_integer() else v
def when(v):
    """A time as the workbook writes it ('1863-07-01 08:00', a date, 'unknown') -> the battle file's form."""
    if isinstance(v, dt.datetime): v = v.strftime('%Y-%m-%d %H:%M:%S' if v.second else '%Y-%m-%d %H:%M') if (v.hour or v.minute or v.second) else v.strftime('%Y-%m-%d')
    elif isinstance(v, dt.date): v = v.isoformat()
    return bf.iso(v)
def points(s):
    """'lat, lon; lat, lon' -> [[lon, lat], ...]"""
    return [bf.ll(*[float(x) for x in q.split(',')]) for q in str(s).split(';') if q.strip()]


def settings(rows):
    """The Playback settings sheet -> nested settings. 'bases.1.label' is the label of the first base; a value written [..] is a list."""
    root = {}
    for r in rows:
        v = r['value']
        if isinstance(v, str) and v.strip()[:1] in '[{': v = json.loads(v)
        path = str(r['setting']).split('.'); node = root
        for i, seg in enumerate(path):
            last = i == len(path) - 1; key = int(seg) - 1 if seg.isdigit() else seg
            nxt = None if last else ([] if path[i + 1].isdigit() else {})
            if isinstance(node, list):
                while len(node) <= key: node.append(None)
                if last: node[key] = num(v)
                else:
                    if node[key] is None: node[key] = nxt
                    node = node[key]
            else:
                if last: node[key] = num(v)
                else: node = node.setdefault(key, nxt)
    return root


def export(pb, W):
    """One battle file, from the workbook's rows for the playback `pb` (a row of the Playbacks sheet)."""
    name, camp = pb['playback_id'], pb['campaign_id']
    mine = lambda rows: [r for r in rows if r.get('playback_id') == name]
    war = [c for c in W['Campaigns'] if c['campaign_id'] == camp][0]['war_id']
    P = {p['pos_id']: p for p in W['Positions'] if p['campaign_id'] == camp}
    routes = {r['route_id']: r for r in W['Routes'] if r['campaign_id'] == camp}
    way = lambda r: points(r['waypoints (lat, lon; ...)'])
    link = {(r['from_pos_id'], r['to_pos_id']): r for r in routes.values() if yes(r.get('playback'))}
    units = {u['unit_id']: u for u in W['Units']}

    def geometry(p):
        if blank(p['lat']): return None
        pts = [bf.ll(p['lat'], p['lon'])]
        if not blank(p.get('via')): pts += points(p['via'])
        if not blank(p['line_end_lat']): pts.append(bf.ll(p['line_end_lat'], p['line_end_lon']))
        return pts

    def step(pid, tr):
        assert pid in P, 'Tracks: track %s names row %s, which is not a Positions row of campaign %s' % (tr['track_id'], pid, camp)
        p = P[pid]; se, sl, ee, el = [when(p[k]) for k in ('start_earliest', 'start_latest', 'end_earliest', 'end_latest')]
        frm = when(p.get('show_from')) or sl or se; to = when(p.get('show_to')) or ee or el or frm
        at = None if text(tr.get('off_map')) else geometry(p)
        src = text(p['coord_source'])
        loc = {'source': None if src == 'none' else src, 'basis': text(p['coordinate_basis']), 'confidence': text(p['coordinate_confidence']),
               'precision_m': int(p['coord_precision_m']) if not blank(p['coord_precision_m']) else None}
        return {'id': pid, 'start': [se, sl], 'end': [ee, el], 'show': [frm, to], 'at': at,
                'on': {p['map_id']: [[float(v) for v in q.split(',')] for q in str(p['map_xy']).split(';')]} if not blank(p.get('map_xy')) else None,
                'along': True if yes(p.get('moves_along_line')) else None,
                'activity': text(p['activity']), 'place': text(p['place_description']), 'quote': text(p['source_wording']), 'method': text(p['position_method']),
                'confidence': text(p['overall_confidence']), 'time_basis': text(p['time_basis']), 'location': loc, 'sources': bf.ids(p['source_ids']), 'notes': text(p['notes']),
                'review': text(p['review_status']), 'battle': text(p['battle_id']), 'shared': True if p['unit_id'] != tr['unit_id'] else None}

    tracks = []
    for tr in mine(W['Tracks']):
        ids = bf.ids(tr.get('rows')) or [k for k, p in P.items() if p['unit_id'] == tr['unit_id']]
        steps = [step(i, tr) for i in ids]
        if not blank(tr.get('starts_from_row')):   # the symbol sets off from a row of its division's: a stand-in first step
            v = step(tr['starts_from_row'], tr); at = when(tr['starts_at']); who = units[P[v['id']]['unit_id']]['map_label']
            v.update(show=[at, at], virtual=True, shared=None, activity="With %s's column" % who, method='interpolated', confidence='low', notes=VIRTUAL_NOTE)
            steps.insert(0, v)
        steps.sort(key=lambda s: (s['show'][0], s['show'][1]))
        for a, b in zip(steps, steps[1:]):
            if b['show'][0] < a['show'][1]: a['show'][1] = b['show'][0]          # two rows of one symbol cannot overlap: the earlier one gives way
            r = link.get((a['id'], b['id']))
            if r and a['at'] and b['at']: b['via'] = way(r)                       # the record gives the route between the two rows
            elif a.get('virtual') and not blank(tr.get('start_route')) and b['at']:
                b['via'] = way(routes[tr['start_route']])[:int(tr['start_route_points'])] + [b['at'][0]]
        tracks.append({'id': tr['track_id'], 'unit': tr['unit_id'], 'label': text(tr.get('label')), 'echelon': text(tr.get('echelon')), 'parent': text(tr.get('part_of_track')),
                       'hide_after': True if yes(tr.get('hide_after_last_row')) else None, 'hold_until': when(tr.get('hold_until')), 'loose': True if yes(tr.get('loose')) else None,
                       'off_map': text(tr.get('off_map')), 'nudge': [float(v) for v in str(tr['nudge']).split(',')] if not blank(tr.get('nudge')) else None, 'steps': steps})
    used = {s['id'] for t in tracks for s in t['steps']}

    sides = [{'id': s['side_id'], 'code': s['code'], 'name': s['name'], 'short': s['short'], 'colour': s['frame']} for s in W['Sides'] if s['war_id'] == war]
    side_ids = {s['id'] for s in sides}; assign = {}
    for a in W['Assignments']: assign.setdefault(a['unit_id'], []).append(a)
    ulist = []
    for u in W['Units']:
        if u['side_id'] not in side_ids: continue
        br = str(u['branch']).lower(); ech = str(u['echelon']).lower()
        ulist.append({'id': u['unit_id'], 'name': u['unit_name'], 'label': u['map_label'], 'side': u['side_id'], 'nation': text(u.get('nation')), 'branch': BRANCH.get(br, br), 'echelon': ECHELON.get(ech, ech),
                      'sources': bf.ids(u['source_ids']), 'notes': text(u['notes']),
                      'assignments': [{'from': when(a['valid_from']), 'to': when(a['valid_to']), 'parent': text(a['parent_unit_id']), 'commander': text(a['commander']),
                                       'strength': text(a['strength / equipment']), 'sources': bf.ids(a['source_ids']), 'notes': text(a['notes'])} for a in assign.get(u['unit_id'], [])]})
    events = []
    for e in W['Events']:
        if e['campaign_id'] != camp or str(e.get('timeline') or 'name').lower() == 'off': continue
        events.append({'id': e['event_id'], 'start': when(e['time_earliest']), 'end': when(e['time_latest']), 'at': when(e.get('playback_at')) or when(e['time_earliest']), 'name': e['name'],
                       'label': text(e.get('playback_label')), 'text': text(e.get('playback_text')) or e['summary'], 'quiet': True if str(e.get('timeline')).lower() == 'dot' else None,
                       'steps': [s for s in bf.ids(e['pos_ids']) if s in used], 'sources': bf.ids(e['source_ids']), 'battle': text(e['battle_id'])})
    events.sort(key=lambda e: e['at'])
    labels = [{'text': l['text'], 'alt': text(l.get('other_name')), 'at': bf.ll(l['lat'], l['lon']), 'angle': num(l['angle']) if not blank(l.get('angle')) else None,
               'level': num(l['level']) if not blank(l.get('level')) else None, 'kind': l['kind'], 'show': text(l.get('show')), 'approximate': True if yes(l.get('approximate')) else None} for l in mine(W['Labels'])]
    maps = {}
    for m in mine(W['Maps']):
        mp = maps.setdefault(m['map_id'], {'id': m['map_id'], 'title': m['title'], 'short': text(m.get('short')), 'label': text(m.get('label')), 'credit': m['credit'], 'source': text(m.get('source_id')),
              'georeferenced': False if str(m.get('fitted_to_ground')).lower() == 'no' else None, 'size': [int(v) for v in str(m['size_px']).split(',')] if not blank(m.get('size_px')) else None,
              'from': when(m.get('from')), 'to': when(m.get('to')), 'fit': json.loads(m['fit']) if not blank(m.get('fit')) else None, 'scale_note': text(m.get('scale_note')),
              'off_note': {'until': when(m['off_note_until']), 'text': m['off_note_text']} if not blank(m.get('off_note_until')) else None, 'images': []})
        mp['images'].append({'file': m['file'], 'detail': True if yes(m.get('detail')) else None,
                             'corners': None if blank(m.get('tl_lat')) else [bf.ll(m[c + '_lat'], m[c + '_lon']) for c in ('tl', 'tr', 'br', 'bl')]})
    S = settings(mine(W['Playback settings'])); presets = S.pop('preset', None)
    if 'rear' in S: S['rear']['at'] = bf.ll(S['rear'].pop('lat'), S['rear'].pop('lon'))
    base = json.load(open(os.path.join(ROOT, 'data', 'base', name + '.json'), encoding='utf-8'))
    battle = {'id': pb['battle_file_id'], 'title': pb['title'], 'subtitle': text(pb.get('subtitle')),
              'record': {'workbook': os.path.splitext(os.path.basename(WORKBOOK))[0], 'campaign': camp, 'battles': bf.ids(pb.get('record_battles'))},
              'time': {'unit': pb['time_unit'], 'zero': when(pb['time_zero']), 'start': when(pb['time_start']), 'end': when(pb['time_end']),
                       'focus': [when(pb['focus_start']), when(pb['focus_end'])] if not blank(pb.get('focus_start')) else None,
                       'calendar': {'first': when(pb['calendar_first']), 'numbered': yes(pb['days_numbered']), 'days': num(pb.get('calendar_days'))}},
              'view': {'origin': bf.ll(pb['origin_lat'], pb['origin_lon']), 'extent': [float(pb[k]) for k in ('west', 'south', 'east', 'north')], 'presets': presets},
              'opening': {'label': text(pb.get('opening_label')), 'text': text(pb.get('opening_text'))}, 'playback': S,
              'sides': sides, 'nations': [{k: n[k] for k in ('name', 'short', 'code', 'colour', 'dark', 'paper')} for n in mine(W.get('Nations', []))],
              'units': ulist, 'tracks': tracks, 'events': events, 'labels': labels, 'maps': list(maps.values()), 'base': base}
    catalogue = {s['source_id']: {'title': s['title'], 'citation': text(s['citation']), 'type': text(s['type']), 'url': text(s['url'])} for s in W['Sources']}
    battle['sources'] = bf.used_sources(bf.clean(battle), catalogue, [base['source']] if base.get('source') in catalogue else [])
    return battle


def pace(battle):
    """Warnings: places where a symbol would have to move implausibly fast between two rows. A wrong coordinate that is still on the map shows up here."""
    day = battle['time']['unit'] == 'day'; limit = 50000 if day else 250      # metres per day, or per minute
    def stamp(s): return dt.datetime.fromisoformat(s if len(s) > 10 else s + 'T00:00')
    def mid(pts): return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
    out = []
    for tr in battle['tracks']:
        st = [s for s in tr['steps'] if s.get('at')]
        for a, b in zip(st, st[1:]):
            pa, pc = mid(a['at']), mid(b['at']); d = math.hypot((pa[0] - pc[0]) * 111320 * math.cos(math.radians(pa[1])), (pa[1] - pc[1]) * 111040)
            gap = (stamp(b['show'][0]) - stamp(a['show'][1])).total_seconds() / (86400 if day else 60)
            gap = max(gap, 1 if day else 3)
            if d / gap > limit: out.append('%s: from row %s to row %s is %.1f km in %s' % (tr['id'], a['id'], b['id'], d / 1000, ('%g days' % gap) if day else ('%g minutes' % gap)))
    return out


def main(argv):
    args = list(argv); check_only = '--check' in args
    if check_only: args.remove('--check')
    failed = 0
    if check_only:
        for b in (args or sorted(d for d in os.listdir(os.path.join(ROOT, 'playbacks')) if os.path.exists(os.path.join(ROOT, 'playbacks', d, 'battle.json')))):
            folder = os.path.join(ROOT, 'playbacks', b); bad = bf.validate(json.load(open(os.path.join(folder, 'battle.json'), encoding='utf-8')), folder)
            print('%s: %s' % (b, 'meets the format' if not bad else '%d problem(s)\n  %s' % (len(bad), '\n  '.join(bad[:40])))); failed += bool(bad)
        return 1 if failed else 0
    W = load()
    for pb in W['Playbacks']:
        if args and pb['playback_id'] not in args: continue
        folder = os.path.join(ROOT, 'playbacks', pb['playback_id']); os.makedirs(folder, exist_ok=True)
        battle = bf.write(export(pb, W), os.path.join(folder, 'battle.json'))
        for w in pace(battle): print('  check this:', w)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
