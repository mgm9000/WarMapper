"""Write every battle's battle file from the master workbook, or check the ones already written.

The workbook (data/WarMapper battle data.xlsx) is the master copy of the battle data. This script reads it and writes one battle file
per row of its Playbacks sheet (playbacks/<playback>/battle.json, in the format docs/battle-file.md describes). No battle has a script
of its own: a new battle is new rows in the workbook.

  python3 tools/export_battles.py              write all battle files, then check them
  python3 tools/export_battles.py ypres        one battle only
  python3 tools/export_battles.py --check      check the files as they stand, without rewriting them

A battle file that breaks the format is not written. Positions that would have a unit move implausibly fast are listed as warnings, and so
are places where one side's symbol is drawn on top of the other's (a unit overrun on the map without the data saying what became of it).
After exporting, run tools/build.py to put the new data into the pages.
"""
import datetime as dt, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import battlefile as bf

WORKBOOK = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx')
BRANCH = {'horse artillery': 'artillery'}
ECHELON = {'regiment (part)': 'regiment'}
ARRIVAL_NOTE = "The approach is not recorded in the sources read. The unit is drawn coming up from %s the day before it is first placed."
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


def sheet_positions(mp, fit, tracks):
    """Positions on an engraving shown as printed, from the same thin-plate spline that stretches it onto the ground (scan pixel <- place),
    in the pixels of the picture that comes with the page. Also a coarse table of the same (lookup) for the player to move between the two."""
    import numpy as np
    from scipy.interpolate import RBFInterpolator
    R = 6378137.0
    merc = lambda q: (R * math.radians(q[0]), R * math.log(math.tan(math.pi / 4 + math.radians(q[1]) / 2)))
    G = np.array([merc((p['lon'], p['lat'])) for p in fit['points']]); S = np.array([p['scan_px'] for p in fit['points']], float)
    f = RBFInterpolator(G, S, kernel='thin_plate_spline'); x0, y0 = fit['crop'][:2]; red = fit['sheet']['reduced']
    def px(pts):
        q = f(np.array([merc(p) for p in pts]))
        return [[round((a - x0) * red, 1), round((b - y0) * red, 1)] for a, b in q]
    for tr in tracks:
        for st in tr['steps']:
            if st.get('at') and not (st.get('on') or {}).get(mp['id']): st['on'] = dict(st.get('on') or {}, **{mp['id']: px(st['at'])})
            if st.get('via'): st['via_on'] = {mp['id']: px(st['via'])}
    P = fit['pieces']; w = min(c[0][0] for c in P); e = max(c[1][0] for c in P); s_ = min(c[2][1] for c in P); n = max(c[0][1] for c in P); N = 40
    grid = [(w + (e - w) * i / (N - 1), n - (n - s_) * j / (N - 1)) for j in range(N) for i in range(N)]
    mp['lookup'] = {'ext': [w, s_, e, n], 'n': [N, N], 'xy': [[round(a), round(b)] for a, b in px(grid)]}


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


def reconstructions(name, W):
    """Reconstructed base maps of a playback (Reconstructions and Recon layers sheets, and the GeoJSON each names): maps WarMapper draws
    itself from traced lines. Every feature keeps its own source, method, confidence and dates; a layer row gives the layer its title and
    the link to the original map."""
    out = []
    for r in [r for r in W.get('Reconstructions', []) if r.get('playback_id') == name]:
        rid = r['recon_id']; G = json.load(open(os.path.join(ROOT, r['file']), encoding='utf-8'))
        rows = sorted([l for l in W.get('Recon layers', []) if l['recon_id'] == rid], key=lambda l: l.get('order') or 0)
        layers = [{'id': l['layer_id'], 'title': l['title'], 'kind': l['kind'], 'source': text(l.get('source_id')), 'link': text(l.get('link')), 'link_label': text(l.get('link_label')),
                   'method': text(l.get('method')), 'confidence': text(l.get('confidence')), 'from': when(l.get('from')), 'to': when(l.get('to')), 'how': text(l.get('how_read')),
                   'review': text(l.get('review_status')), 'notes': text(l.get('notes'))} for l in rows]
        known = {l['id']: l for l in layers}; feats = []
        for f in G['features']:
            p = f['properties']; g = f['geometry']; lay = p.get('layer')
            assert lay in known, 'Recon layers: %s has no row for layer %r (feature %s of %s)' % (rid, lay, p.get('id'), r['file'])
            c = g['coordinates']
            shape, at = {'Point': ('point', [c]), 'LineString': ('line', [c]), 'Polygon': ('area', c), 'MultiLineString': ('lines', c), 'MultiPolygon': ('areas', c)}[g['type']]
            whole = lambda q, n: q.count(';') >= n          # packing drops repeated points: a line needs two left, a ring three
            packed = (bf.ll(c[1], c[0]) if shape == 'point' else
                      [k for k in ([q for q in (bf.pack(ring) for ring in poly) if whole(q, 3)] for poly in at) if k] if shape == 'areas' else
                      [q for q in (bf.pack(ring) for ring in at) if whole(q, 1)])
            feats.append({'id': p['id'], 'layer': lay, 'kind': p['kind'], 'shape': shape, 'at': packed,
                          'name': p.get('name'), 'desc': p.get('desc'), 'class': p.get('class'), 'width_m': p.get('width_m'), 'number': p.get('number'), 'side': p.get('side'), 'part': p.get('part'),
                          'from': bf.iso(p.get('from')), 'to': bf.iso(p.get('to')), 'source': p.get('source_id'), 'method': p.get('method'), 'confidence': p.get('confidence'),
                          'precision_m': p.get('precision_m'), 'basis': p.get('basis'), 'review': p.get('review')})
        for l in layers: l['features'] = sum(1 for f in feats if f['layer'] == l['id'])
        out.append({'id': rid, 'title': r['title'], 'label': text(r.get('label')), 'about': text(r.get('about')), 'note': text(r.get('notes')), 'credit': text(r.get('credit')), 'style': text(r.get('style')),
                    'made': when(r.get('made')), 'review': text(r.get('review_status')), 'file': r['file'], 'sheet': G.get('sheet'), 'layers': layers, 'features': feats})
    return out


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
                'march': True if yes(p.get('arrive_at_pace')) else None,
                'activity': text(p['activity']), 'place': text(p['place_description']), 'quote': text(p['source_wording']), 'method': text(p['position_method']),
                'confidence': text(p['overall_confidence']), 'time_basis': text(p['time_basis']), 'location': loc, 'sources': bf.ids(p['source_ids']), 'notes': text(p['notes']),
                'review': text(p['review_status']), 'battle': text(p['battle_id']), 'shared': True if p['unit_id'] != tr['unit_id'] else None}

    ARR = settings(mine(W['Playback settings'])).get('arrival')   # units that come into the battle late are drawn coming up, not appearing
    code = {x['side_id']: x['code'] for x in W['Sides']}; T0 = when(pb['time_start'])
    def parent_of(uid, day):   # who the unit answered to on that day, by its assignment records
        rows = [a for a in W['Assignments'] if a['unit_id'] == uid and not blank(a.get('parent_unit_id'))]
        now = [a for a in rows if (when(a['valid_from']) or '')[:10] <= day <= ((when(a['valid_to']) or '9999')[:10])]
        return (now or rows[-1:] or [{}])[0].get('parent_unit_id')
    placed = {}   # track id -> its steps, for a unit that comes up out of its parent formation

    def arrive(tr, steps):
        first = steps[0]
        if not first['at'] or first['show'][0] <= T0 or first.get('virtual'): return
        day = dt.date.fromisoformat(first['show'][0][:10]) - dt.timedelta(days=int(ARR.get('lead', 1)))
        at = day.isoformat()
        if at < T0: return
        pid = parent_of(tr['unit_id'], at); par = placed.get(pid)
        prev = [s for s in (par or []) if s['at'] and s['show'][0] <= at] if par else []
        if prev:   # its parent formation is on the map: the unit comes out of it
            g = prev[-1]['at']; c = [sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)]; geo = [c]
            whence = units[pid]['map_label'] + "'s line"
        else:      # from behind its own side's lines
            side = ARR.get(code.get(units[tr['unit_id']]['side_id'], ''), {})
            g = first['at']; c = [sum(p[0] for p in g) / len(g), sum(p[1] for p in g) / len(g)]; km = float(ARR.get('km', 10))
            if 'lat' in side: dx, dy = (side['lon'] - c[0]) * math.cos(math.radians(c[1])), side['lat'] - c[1]
            else: b = math.radians(float(side.get('bearing', 90))); dx, dy = math.sin(b), math.cos(b)
            n = math.hypot(dx, dy) or 1; dlat = km / 111.32 * dy / n; dlon = km / (111.32 * math.cos(math.radians(c[1]))) * dx / n
            geo = [[round(p[0] + dlon, 5), round(p[1] + dlat, 5)] for p in g]; whence = 'behind its own lines'
        v = dict(first); v.update(id=first['id'], show=[at, at], start=[at, at], end=[at, at], at=geo, on=None, virtual=True, shared=None, along=None, march=None,
                                  activity='Coming up (approach not recorded)', place='Not recorded', quote=None, method='interpolated', confidence='low', notes=ARRIVAL_NOTE % whence)
        steps.insert(0, v)

    tracks = []
    for tr in mine(W['Tracks']):
        ids = bf.ids(tr.get('rows')) or [k for k, p in P.items() if p['unit_id'] == tr['unit_id']]
        steps = [step(i, tr) for i in ids]
        if not blank(tr.get('starts_from_row')):   # the symbol sets off from a row of its division's: a stand-in first step
            v = step(tr['starts_from_row'], tr); at = when(tr['starts_at']); who = units[P[v['id']]['unit_id']]['map_label']
            v.update(show=[at, at], virtual=True, shared=None, activity="With %s's column" % who, method='interpolated', confidence='low', notes=VIRTUAL_NOTE)
            steps.insert(0, v)
        steps.sort(key=lambda s: (not s.get('virtual'), s['show'][0], s['show'][1]))   # a stand-in start comes first, whatever the rows after it say
        if steps and steps[0].get('virtual') and len(steps) > 1 and not blank(tr.get('start_move_minutes')):   # it takes this long to reach its first row (a crossing)
            t1 = (dt.datetime.fromisoformat(steps[0]['show'][0]) + dt.timedelta(minutes=int(tr['start_move_minutes']))).isoformat()[:16]
            b = steps[1]
            if b['show'][0] < t1: b['show'] = [t1, max(t1, b['show'][1])]
        if ARR and blank(tr.get('starts_from_row')) and blank(tr.get('part_of_track')) and not text(tr.get('off_map')): arrive(tr, steps)
        for a, b in zip(steps, steps[1:]):
            if b['show'][0] < a['show'][1]: a['show'][1] = b['show'][0]          # two rows of one symbol cannot overlap: the earlier one gives way
            r = link.get((a['id'], b['id']))
            if r and a['at'] and b['at']:
                b['via'] = way(r)                                                   # the record gives the route between the two rows
                if text(r.get('kind')) == 'escape': b['leaving'] = True   # Follow lets a unit getting away go off the screen
            elif ((a.get('virtual') and not b.get('shared')) or (a.get('shared') and not b.get('shared'))) and not blank(tr.get('start_route')) and b['at']:   # from the stand-in start, or from the last row it shares   # one route, or several in order ("RT01; RT02"); the points cap the last
                names = bf.ids(tr['start_route']); via = []
                for i, n in enumerate(names):
                    w = way(routes[n])
                    if i == len(names) - 1 and not blank(tr.get('start_route_points')): w = w[:int(tr['start_route_points'])]
                    via += w[1:] if via and w and w[0] == via[-1] else w
                b['via'] = via + [b['at'][0]]
        placed[tr['unit_id']] = steps
        tracks.append({'id': tr['track_id'], 'unit': tr['unit_id'], 'label': text(tr.get('label')), 'echelon': text(tr.get('echelon')), 'parent': text(tr.get('part_of_track')),
                       'hide_after': True if yes(tr.get('hide_after_last_row')) else None, 'hold_until': when(tr.get('hold_until')), 'loose': True if yes(tr.get('loose')) else None,
                       'off_map': text(tr.get('off_map')), 'nudge': [float(v) for v in str(tr['nudge']).split(',')] if not blank(tr.get('nudge')) else None, 'steps': steps})
    used = {s['id'] for t in tracks for s in t['steps']}

    sides = [{'id': s['side_id'], 'code': s['code'], 'name': s['name'], 'short': s['short'], 'colour': s['frame']} for s in W['Sides'] if s['war_id'] == war]
    side_ids = {s['id'] for s in sides}; assign = {}
    for a in W['Assignments']: assign.setdefault(a['unit_id'], []).append(a)
    def needed(pid):      # the units a playback draws, and the formations above them
        out = set(); todo = [text(r['unit_id']) for r in W['Tracks'] if r['playback_id'] == pid]
        while todo:
            i = todo.pop()
            if not i or i in out: continue
            out.add(i); todo += [text(x['parent_unit_id']) for x in assign.get(i, [])]
        return out
    drawn = needed(pb['playback_id']); theirs = set().union(*[needed(o['playback_id']) for o in W['Playbacks'] if o['playback_id'] != pb['playback_id']] or [set()])
    # a war can hold several playbacks: a unit only another playback draws stays out of this one, and so does a unit nobody draws that sits under one
    keep = {u['unit_id'] for u in W['Units'] if u['unit_id'] in drawn or u['unit_id'] not in theirs}; shrinking = True
    while shrinking:
        gone = {i for i in keep - drawn if any(text(x['parent_unit_id']) and text(x['parent_unit_id']) not in keep for x in assign.get(i, []))}
        keep -= gone; shrinking = bool(gone)
    ulist = []
    for u in W['Units']:
        if u['side_id'] not in side_ids or u['unit_id'] not in keep: continue
        br = str(u['branch']).lower(); ech = str(u['echelon']).lower()
        ulist.append({'id': u['unit_id'], 'name': u['unit_name'], 'label': u['map_label'], 'side': u['side_id'], 'nation': text(u.get('nation')), 'branch': BRANCH.get(br, br), 'echelon': ECHELON.get(ech, ech),
                      'sources': bf.ids(u['source_ids']), 'notes': text(u['notes']),
                      'assignments': [{'from': when(a['valid_from']), 'to': when(a['valid_to']), 'parent': text(a['parent_unit_id']), 'commander': text(a['commander']),
                                       'strength': text(a['strength / equipment']), 'sources': bf.ids(a['source_ids']), 'notes': text(a['notes'])} for a in assign.get(u['unit_id'], [])]})
    events = []; battles_of = bf.ids(pb.get('record_battles'))
    for e in W['Events']:
        if e['campaign_id'] != camp or str(e.get('timeline') or 'name').lower() == 'off': continue
        if battles_of and text(e['battle_id']) and text(e['battle_id']) not in battles_of: continue      # a campaign can hold several playbacks: each takes the events of its own battles
        events.append({'id': e['event_id'], 'start': when(e['time_earliest']), 'end': when(e['time_latest']), 'at': when(e.get('playback_at')) or when(e['time_earliest']), 'name': e['name'],
                       'label': text(e.get('playback_label')), 'text': text(e.get('playback_text')) or e['summary'], 'quiet': True if str(e.get('timeline')).lower() == 'dot' else None,
                       'steps': [s for s in bf.ids(e['pos_ids']) if s in used], 'sources': bf.ids(e['source_ids']), 'battle': text(e['battle_id'])})
    events.sort(key=lambda e: e['at'])
    # summaries of a day or a week, shown when the playback stops at the end of one (Summaries sheet; optional)
    summaries = [{'kind': r['kind'], 'from': when(r['from']), 'to': when(r['to']), 'title': r['title'], 'text': r['text'], 'sources': bf.ids(r.get('source_ids'))}
                 for r in W.get('Summaries', []) if r['playback_id'] == pb['playback_id']]
    summaries.sort(key=lambda x: (x['from'], x['kind']))
    labels = [{'text': l['text'], 'alt': text(l.get('other_name')), 'at': bf.ll(l['lat'], l['lon']), 'angle': num(l['angle']) if not blank(l.get('angle')) else None,
               'level': num(l['level']) if not blank(l.get('level')) else None, 'kind': l['kind'], 'show': text(l.get('show')), 'approximate': True if yes(l.get('approximate')) else None} for l in mine(W['Labels'])]
    maps = {}
    for m in mine(W['Maps']):
        mp = maps.setdefault(m['map_id'], {'id': m['map_id'], 'title': m['title'], 'short': text(m.get('short')), 'label': text(m.get('label')), 'credit': m['credit'], 'source': text(m.get('source_id')),
              'georeferenced': False if str(m.get('fitted_to_ground')).lower() == 'no' else None, 'size': [int(v) for v in str(m['size_px']).split(',')] if not blank(m.get('size_px')) else None,
              'from': when(m.get('from')), 'to': when(m.get('to')), 'fit': json.loads(m['fit']) if not blank(m.get('fit')) else None, 'scale_note': text(m.get('scale_note')), 'note': text(m.get('note')),
              'approx_m_per_px': float(m['approx_m_per_px']) if not blank(m.get('approx_m_per_px')) else None,
              'off_note': {'until': when(m['off_note_until']), 'text': m['off_note_text']} if not blank(m.get('off_note_until')) else None, 'iiif': None, 'images': []})
        if not blank(m.get('iiif_service')) and not mp['iiif']:   # the holding library serves the full scan as zoomable tiles
            mp['iiif'] = {'service': str(m['iiif_service']).rstrip('/'), 'width': int(m['iiif_width']), 'height': int(m['iiif_height']), 'tile': int(m['iiif_tile']),
                          'scale_factors': json.loads(m['iiif_scale_factors']), 'region': [int(v) for v in str(m['iiif_region']).split(',')], 'reduced': float(m['iiif_reduced'])}
        mp['images'].append({'file': m['file'], 'detail': True if yes(m.get('detail')) else None, 'reduced': float(m['iiif_reduced']) if not blank(m.get('iiif_reduced')) else None,
                             'corners': None if blank(m.get('tl_lat')) else [bf.ll(m[c + '_lat'], m[c + '_lon']) for c in ('tl', 'tr', 'br', 'bl')]})
    for m in mine(W['Maps']):   # a picture not to scale whose pixel for each place comes from a fit (the unstretched Faden sheet): place every step on it
        if blank(m.get('xy_from')) or maps[m['map_id']].get('lookup'): continue
        sheet_positions(maps[m['map_id']], json.load(open(os.path.join(ROOT, m['xy_from']))), tracks)
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
    if summaries: battle['summaries'] = summaries
    rc = reconstructions(name, W)
    if rc: battle['reconstructions'] = rc
    catalogue = {s['source_id']: {'title': s['title'], 'author': text(s.get('author')), 'date': str(s['date']) if not blank(s.get('date')) else None, 'citation': text(s['citation']),
                                  'type': text(s['type']), 'url': text(s['url']), 'rights': text(s.get('rights'))} for s in W['Sources']}
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


def _seg_d(a, b, c, d):
    """Distance between segments ab and cd (0 where they cross)."""
    def cross(o, p, q): return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    if a != b and c != d:
        d1, d2, d3, d4 = cross(c, d, a), cross(c, d, b), cross(a, b, c), cross(a, b, d)
        if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)): return 0.0
    def pt(p, s, e):
        vx, vy = e[0] - s[0], e[1] - s[1]; L = vx * vx + vy * vy
        f = 0 if not L else max(0, min(1, ((p[0] - s[0]) * vx + (p[1] - s[1]) * vy) / L))
        return math.hypot(p[0] - s[0] - f * vx, p[1] - s[1] - f * vy)
    return min(pt(a, c, d), pt(b, c, d), pt(c, a, b), pt(d, a, b))


def _gd(g, h):
    """Distance between two positions (points or lines)."""
    G = list(zip(g, g[1:])) or [(g[0], g[0])]; H = list(zip(h, h[1:])) or [(h[0], h[0])]
    return min(_seg_d(a, b, c, d) for a, b in G for c, d in H)


def _lerp(a, b, f):
    n = max(len(a), len(b)); a = a + [a[-1]] * (n - len(a)); b = b + [b[-1]] * (n - len(b))
    return [(p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f) for p, q in zip(a, b)]


def contacts(battle, near=50):
    """Warnings: where a symbol of one side sits on, or passes over, a symbol of the other (within `near` metres), as the playback
    draws them minute by minute. Units that met in battle are close, but one side's symbol drawn over the other's means a unit has been
    overrun on the map without the data saying so: it should fall back, be shown taken, or leave the map. Battles followed by the clock only."""
    if battle['time']['unit'] != 'minute': return []
    def stamp(s): return dt.datetime.fromisoformat(s if len(s) > 10 else s + 'T00:00')
    zero = stamp(battle['time']['zero']); T = lambda s: (stamp(s) - zero).total_seconds() / 60
    lat0 = battle['view']['origin'][1]; kx = 111320 * math.cos(math.radians(lat0)); ky = 111040
    xy = lambda p: (p[0] * kx, p[1] * ky)
    rules = (battle.get('playback') or {}).get('rules') or {}; pace = rules.get('pace'); near_m = rules.get('near', 15)
    units = {u['id']: u for u in battle['units']}; tracks = []
    for tr in battle['tracks']:
        if tr.get('off_map'): continue
        u = units[tr['unit']]; p = (pace if isinstance(pace, (int, float)) else pace.get(u['branch']) or pace.get('infantry')) if pace else 0
        ks = [{'id': s['id'], 't0': T(s['show'][0]), 't1': T(s['show'][1]), 'g': [xy(q) for q in s['at']] if s.get('at') else None, 'virtual': s.get('virtual'), 'via': bool(s.get('via')), 'march': s.get('march')} for s in tr['steps']]
        tracks.append({'id': tr['id'], 'side': u['side'], 'ks': ks, 'hide': tr.get('hide_after'), 'hold': T(tr['hold_until']) if tr.get('hold_until') else 0, 'pace': p or 0})
    def at(tr, t):
        ks = tr['ks']; n = len(ks)
        if t < ks[0]['t0']: return None
        for i, k in enumerate(ks):
            nx = ks[i + 1] if i + 1 < n else None; end = max(k['t1'], tr['hold']) if i == n - 1 else k['t1']
            if k['t0'] <= t <= end: return None if k['virtual'] else (k['g'], k['id'])
            if nx and end < t < nx['t0']:
                if not (k['g'] and nx['g']): return (k['g'], k['id']) if k['g'] else None
                ca, cb = [sum(c) / len(c) for c in zip(*k['g'])], [sum(c) / len(c) for c in zip(*nx['g'])]; d = math.hypot(ca[0] - cb[0], ca[1] - cb[1])
                if not nx['via'] and d < near_m: return (nx['g'], nx['id'])
                arr = nx['t0']
                if tr['pace'] and nx['march'] and not nx['via'] and end + max(3, d / tr['pace']) < arr:
                    arr = end + max(3, d / tr['pace'])
                    if t >= arr: return (nx['g'], nx['id'])
                return (_lerp(k['g'], nx['g'], (t - end) / (arr - end)), k['id'] + '>' + nx['id'])
        if tr['hide']: return None
        return (ks[-1]['g'], ks[-1]['id']) if ks[-1]['g'] else None
    t0, t1 = T(battle['time']['start']), T(battle['time']['end']); hits = {}
    t = t0
    while t <= t1:
        here = [(tr, at(tr, t)) for tr in tracks]; here = [(tr, a) for tr, a in here if a and a[0]]
        for i, (a, pa) in enumerate(here):
            for b, pb in here[i + 1:]:
                if a['side'] == b['side']: continue
                d = _gd(pa[0], pb[0])
                if d < near: hits.setdefault((a['id'], b['id']), []).append((t, pa[1], pb[1], d))
        t += 1
    out = []
    clock = lambda m: '%d:%02d' % (int(m // 60) % 24, int(m % 60))
    for (a, b), ts in sorted(hits.items(), key=lambda kv: kv[1][0][0]):
        runs = [[ts[0]]]
        for x in ts[1:]:
            if x[0] - runs[-1][-1][0] > 1: runs.append([x])
            else: runs[-1].append(x)
        for r in runs:
            d = min(x[3] for x in r)
            out.append('%s and %s %s %s to %s (rows %s / %s)' % (a, b, 'drawn crossing' if d < 5 else 'within %d m' % max(5, round(d)), clock(r[0][0]), clock(r[-1][0]), r[0][1], r[0][2]))
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
        for w in contacts(battle): print('  contact:', w)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
