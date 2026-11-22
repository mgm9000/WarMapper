"""The common battle file: one format for every battle (docs/battle-file.md describes it in full).

tools/export_battles.py gathers each battle's record from the master workbook and hands it to write(), which checks it
against the format and saves playbacks/<battle>/battle.json. The playback pages read nothing else.
"""
import json, os, re

FORMAT = 'warmapper-battle/1'
ECHELONS = ['army', 'corps', 'division', 'brigade', 'regiment', 'battalion', 'squadrons', 'battery', 'company', 'section', 'detachment', 'headquarters']
BRANCHES = ['infantry', 'cavalry', 'artillery', 'naval']      # naval (ships: transports, gunboats) added 21 Nov 2026
METHODS = ['stated', 'inferred', 'interpolated']
LEVELS = ['high', 'medium', 'low']
LABEL_KINDS = ['road', 'water', 'area', 'town', 'place', 'wood', 'landmark', 'ridge', 'hill']
LINE_KINDS = ['road', 'rail', 'water', 'former-water']
AREA_KINDS = ['wood', 'water']
LABEL_SHOWS = ['current', 'period', 'both', 'recon']
# reconstructed base maps (21 Nov 2026): what a traced feature is, how it was read, and the shapes it can take
RECON_KINDS = ['sea', 'shore', 'river', 'stream', 'water', 'wall', 'road', 'rail', 'breakwater', 'blockhouse', 'detail', 'entrenchment', 'ink']
RECON_METHODS = ['traced', 'AI-extracted', 'interpolated']
RECON_SHAPES = ['point', 'line', 'area', 'lines', 'areas']
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?)?$')


# ---------- helpers for the recipes ----------
def iso(s):
    """'1863-07-01 08:00' (the workbook's way of writing a time) -> '1863-07-01T08:00'; 'unknown' or nothing -> None."""
    s = str(s or '').strip()
    if not s or s == 'unknown': return None
    s = s.replace(' ', 'T')
    assert ISO.match(s), s
    return s


def at_minute(day, minutes):
    """A moment as minutes from midnight of `day` ('YYYY-MM-DD'); minutes may be negative, above 1440 or a fraction."""
    import datetime as dt
    t = dt.datetime.fromisoformat(day) + dt.timedelta(seconds=round(minutes * 60))
    return t.strftime('%Y-%m-%dT%H:%M:%S' if t.second else '%Y-%m-%dT%H:%M')


def ll(lat, lon):
    """A point as the file holds it: [longitude, latitude], to about 10 cm."""
    return [round(float(lon), 6), round(float(lat), 6)]


def ids(s):
    """'S02; S01' -> ['S02', 'S01']"""
    return [x.strip() for x in str(s or '').split(';') if x.strip()]


def pack(points):
    """A base-map line as text: the first point, then the step to each next point, in units of 0.00001 degree
    ('lon,lat;dlon,dlat;...'). About a third the size of plain numbers, and exact to a metre."""
    out = []; px = py = 0
    for i, (lon, lat) in enumerate(points):
        x, y = round(lon * 1e5), round(lat * 1e5)
        if i and x == px and y == py: continue
        out.append('%d,%d' % ((x, y) if not out else (x - px, y - py))); px, py = x, y
    return ';'.join(out)


def clean(o):
    """Drop empty values (None, '', [], {}), so a field that has nothing to say is simply absent from the file."""
    if isinstance(o, dict):
        return {k: v for k, v in ((k, clean(v)) for k, v in o.items()) if v not in (None, '', [], {})}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


# ---------- the check ----------
def validate(b, folder=None):
    """Return a list of problems (empty when the battle file is sound). `folder` is where its map pictures should be."""
    bad = []

    def need(o, keys, where):
        for k in keys:
            if k not in o: bad.append('%s: no "%s"' % (where, k))

    def time_ok(v, where, allow_none=False):
        if v is None and allow_none: return
        if not (isinstance(v, str) and ISO.match(v)): bad.append('%s: not a date or time: %r' % (where, v))

    def point_ok(p, where):
        if not (isinstance(p, list) and len(p) == 2 and all(isinstance(v, (int, float)) for v in p) and -180 <= p[0] <= 180 and -90 <= p[1] <= 90):
            bad.append('%s: not a [longitude, latitude] point: %r' % (where, p)); return
        w, s, e, n = b['view']['extent']; mx, my = (e - w) * 2, (n - s) * 2
        if not (w - mx <= p[0] <= e + mx and s - my <= p[1] <= n + my): bad.append('%s: point far outside the battle\'s extent (longitude and latitude swapped?): %r' % (where, p))

    need(b, ['format', 'id', 'title', 'time', 'view', 'sides', 'units', 'tracks', 'events', 'sources', 'labels', 'maps', 'base'], 'battle')
    if bad: return bad
    if b['format'] != FORMAT: bad.append('format is %r, expected %r' % (b['format'], FORMAT))
    T = b['time']; need(T, ['unit', 'zero', 'start', 'end', 'calendar'], 'time')
    if T.get('unit') not in ('minute', 'day'): bad.append('time.unit must be "minute" or "day"')
    for k in ('zero', 'start', 'end'): time_ok(T.get(k), 'time.' + k)
    if T.get('start', '') > T.get('end', ''): bad.append('time.start is after time.end')
    need(T.get('calendar', {}), ['first', 'numbered'], 'time.calendar')
    V = b['view']; need(V, ['origin', 'extent'], 'view')
    if len(V.get('extent', [])) != 4 or not (V['extent'][0] < V['extent'][2] and V['extent'][1] < V['extent'][3]): bad.append('view.extent must be [west, south, east, north]'); return bad
    point_ok(V['origin'], 'view.origin')
    for name, box in V.get('presets', {}).items():
        if len(box) != 4 or not (box[0] < box[2] and box[1] < box[3]): bad.append('view.presets.%s must be [west, south, east, north]' % name)

    sides = {}
    for s in b['sides']:
        need(s, ['id', 'code', 'name', 'short', 'colour'], 'side'); sides[s.get('id')] = s
    units = {}
    for u in b['units']:
        w = 'unit %s' % u.get('id'); need(u, ['id', 'name', 'label', 'side', 'branch', 'echelon'], w)
        if u.get('id') in units: bad.append(w + ': listed twice')
        units[u.get('id')] = u
        if u.get('side') not in sides: bad.append(w + ': unknown side %r' % u.get('side'))
        if u.get('branch') not in BRANCHES: bad.append(w + ': unknown branch %r' % u.get('branch'))
        if u.get('echelon') not in ECHELONS: bad.append(w + ': unknown echelon %r' % u.get('echelon'))
        for a in u.get('assignments', []):
            for k in ('from', 'to'): time_ok(a.get(k), w + ' assignment.' + k, True)
    for u in b['units']:
        for a in u.get('assignments', []):
            if a.get('parent') and a['parent'] not in units: bad.append('unit %s: parent %r is not in units' % (u['id'], a['parent']))

    sources = b['sources']
    for sid, s in sources.items(): need(s, ['title'], 'source ' + sid)
    maps = {}
    for m in b['maps']:
        w = 'map %s' % m.get('id'); need(m, ['id', 'title', 'credit', 'images'], w); maps[m.get('id')] = m
        for k in ('from', 'to'):
            if k in m: time_ok(m[k], w + '.' + k)
        if m.get('georeferenced', True) is False:
            need(m, ['size'], w)
        if m.get('iiif'):
            I = m['iiif']; need(I, ['service', 'width', 'height', 'tile', 'scale_factors', 'region', 'reduced'], w + ' iiif')
            r = I.get('region', [])
            if len(r) != 4 or not (0 <= r[0] < r[2] <= I.get('width', 0) and 0 <= r[1] < r[3] <= I.get('height', 0)): bad.append(w + ': iiif region must be [left, top, right, bottom] inside the scan')
            if not str(I.get('service', '')).startswith('https://'): bad.append(w + ': iiif service must be an https address')
        for im in m.get('images', []):
            need(im, ['file'], w + ' image')
            if m.get('georeferenced', True):
                if len(im.get('corners', [])) != 4: bad.append(w + ': a placed picture needs four corners (top-left, top-right, bottom-right, bottom-left)')
                else:
                    for c in im['corners']: point_ok(c, w + ' corner')
            if folder and not os.path.exists(os.path.join(folder, im.get('file', ''))): bad.append(w + ': picture file not found: %s' % im.get('file'))

    step_ids = set(); tracks = {}
    for tr in b['tracks']:
        w = 'track %s' % tr.get('id'); need(tr, ['id', 'unit', 'steps'], w)
        if tr.get('id') in tracks: bad.append(w + ': listed twice')
        tracks[tr.get('id')] = tr
        if tr.get('unit') not in units: bad.append(w + ': unit %r is not in units' % tr.get('unit'))
        if tr.get('echelon') and tr['echelon'] not in ECHELONS: bad.append(w + ': unknown echelon %r' % tr['echelon'])
        if 'hold_until' in tr: time_ok(tr['hold_until'], w + '.hold_until')
        if not tr.get('steps'): bad.append(w + ': no steps')
        last = None
        for st in tr.get('steps', []):
            x = '%s step %s' % (w, st.get('id')); need(st, ['id', 'start', 'end', 'show', 'activity', 'method', 'confidence', 'sources'], x)
            step_ids.add(st.get('id'))
            for k in ('start', 'end'):
                r = st.get(k, [])
                if len(r) != 2: bad.append(x + ': %s must be [earliest, latest]' % k); continue
                for v in r: time_ok(v, x + '.' + k, True)
                if r[0] and r[1] and r[0][:10] > r[1][:10]: bad.append(x + ': %s earliest is after latest' % k)
            sh = st.get('show', [])
            if len(sh) != 2: bad.append(x + ': show must be [from, to]')
            else:
                for v in sh: time_ok(v, x + '.show')
                if all(isinstance(v, str) for v in sh):
                    if len(sh[0]) == len(sh[1]) and sh[0] > sh[1]: bad.append(x + ': shown from a time after it ends')
                    if last and len(last) == len(sh[0]) and sh[0] < last: bad.append(x + ': steps are not in time order')
                    last = sh[0]
            for p in st.get('at', []): point_ok(p, x + '.at')
            for p in st.get('via', []): point_ok(p, x + '.via')
            for mid in st.get('on', {}):
                if mid not in maps: bad.append(x + ': drawn on a map that is not in maps: %r' % mid)
            if st.get('method') not in METHODS: bad.append(x + ': unknown method %r' % st.get('method'))
            if st.get('confidence') not in LEVELS: bad.append(x + ': unknown confidence %r' % st.get('confidence'))
            for sid in st.get('sources', []):
                if sid not in sources: bad.append(x + ': source %r is not in sources' % sid)
    for tr in b['tracks']:
        if tr.get('parent') and tr['parent'] not in tracks: bad.append('track %s: parent track %r not found' % (tr['id'], tr['parent']))

    P = b.get('playback', {})
    for bs in P.get('bases', []):
        need(bs, ['id', 'label'], 'playback base')
        if bs.get('map') and bs['map'] not in maps: bad.append('playback base %s: map %r is not in maps' % (bs.get('id'), bs['map']))
        if bs.get('clip') and bs['clip'] not in maps: bad.append('playback base %s: clip map %r is not in maps' % (bs.get('id'), bs['clip']))
        im = bs.get('imagery')
        if im is not None:
            t = str(im.get('tiles', '')) if isinstance(im, dict) else ''
            if not (t.startswith('https://') and all(k in t for k in ('{z}', '{x}', '{y}'))):
                bad.append('playback base %s: imagery.tiles must be an https address with {z}, {x} and {y}' % bs.get('id'))
            if not (isinstance(im, dict) and im.get('credit')): bad.append('playback base %s: imagery needs a credit' % bs.get('id'))
        if not (bs.get('current') or bs.get('map') or bs.get('series') or im or bs.get('recon')): bad.append('playback base %s: needs "current", "map", "series", "imagery" or "recon"' % bs.get('id'))
        if bs.get('recon') and bs['recon'] not in [r.get('id') for r in b.get('reconstructions', [])]: bad.append('playback base %s: reconstruction %r is not in reconstructions' % (bs.get('id'), bs['recon']))
        tr = bs.get('terrain')   # the terrain version of a reconstruction (22 Nov 2026): relief and contours worked out in the page
        if tr is not None:
            if not bs.get('recon'): bad.append('playback base %s: terrain needs a reconstruction ("recon")' % bs.get('id'))
            if not isinstance(tr, dict): bad.append('playback base %s: terrain must be an object' % bs.get('id'))
            else:
                for k in ('zoom', 'open_m', 'smooth_m', 'relief', 'spots_from'):
                    if k in tr and not (isinstance(tr[k], (int, float)) and tr[k] > 0): bad.append('playback base %s: terrain.%s must be a positive number' % (bs.get('id'), k))
                st = tr.get('steps', [])
                if not (isinstance(st, list) and all(isinstance(q, list) and len(q) in (2, 3) and all(isinstance(v, (int, float)) and v >= 0 for v in q) and q[1] > 0 for q in st)):
                    bad.append('playback base %s: terrain.steps must be [[zoom, metres, metres of the heavier lines], ...]' % bs.get('id'))
                elif [q[0] for q in st] != sorted(q[0] for q in st): bad.append('playback base %s: terrain.steps must go from the lowest zoom up' % bs.get('id'))
                ex = tr.get('extent')
                if ex is not None and not (isinstance(ex, list) and len(ex) == 4 and all(isinstance(v, (int, float)) for v in ex) and ex[0] < ex[2] and ex[1] < ex[3]):
                    bad.append('playback base %s: terrain.extent must be [west, south, east, north]' % bs.get('id'))
    if P.get('surround') is not None: bad.append("playback.surround is now called playback.modern")
    su = P.get('modern')
    if su is not None:
        t = str(su.get('tiles', '')) if isinstance(su, dict) else ''
        if not (t.startswith('https://') and all(k in t for k in ('{z}', '{x}', '{y}'))): bad.append('playback.modern.tiles must be an https address with {z}, {x} and {y}')
        if not (isinstance(su, dict) and su.get('credit')): bad.append('playback.modern needs a credit')
        if isinstance(su, dict) and su.get('reach') is not None and not (isinstance(su['reach'], (int, float)) and 1 < su['reach'] <= 40): bad.append('playback.modern.reach must be a number above 1 and up to 40')
    fm = P.get('formations')
    if fm is not None and not (isinstance(fm, dict) and isinstance(fm.get('below'), (int, float)) and fm['below'] > 0): bad.append('playback.formations needs a number `below`')
    if P.get('start_base') and P['start_base'] not in [b.get('id') for b in P.get('bases', [])]: bad.append('playback.start_base names no base')
    if P.get('bounds') and P['bounds'] not in maps: bad.append('playback.bounds: map %r is not in maps' % P['bounds'])
    for v in P.get('views', []):
        if v.get('preset') not in V.get('presets', {}): bad.append('playback view: preset %r is not in view.presets' % v.get('preset'))
    if P.get('follow', {}).get('empty') and P['follow']['empty'] not in V.get('presets', {}): bad.append('playback.follow.empty: no such preset')
    for tid in P.get('follow', {}).get('exclude', []):
        if tid not in tracks: bad.append('playback.follow.exclude: track %r not found' % tid)
    if P.get('style') and P['style'] not in ('tactical', 'operational'): bad.append('playback.style must be "tactical" or "operational"')
    codes = {s.get('code') for s in b['sides']}
    for g in P.get('groups', []):
        if g.get('side') not in codes: bad.append('playback group %r: unknown side code' % g.get('label'))
    for n in b.get('nations', []): need(n, ['name', 'short'], 'nation')
    last = None
    for x in b.get('summaries', []):   # optional: day and week summaries for the pauses
        w = 'summary %s %s' % (x.get('kind'), x.get('from')); need(x, ['kind', 'from', 'to', 'title', 'text'], w)
        if x.get('kind') not in ('day', 'week'): bad.append(w + ': kind must be "day" or "week"')
        for k in ('from', 'to'): time_ok(x.get(k), w + '.' + k)
        if isinstance(x.get('from'), str) and isinstance(x.get('to'), str) and x['to'] < x['from']: bad.append(w + ': ends before it starts')
    for e in b['events']:
        w = 'event %s' % e.get('id'); need(e, ['id', 'start', 'end', 'at', 'name', 'text'], w)
        for k in ('start', 'end', 'at'): time_ok(e.get(k), w + '.' + k)
        if last and isinstance(e.get('at'), str) and len(last) == len(e['at']) and e['at'] < last: bad.append(w + ': events are not in time order')
        last = e.get('at')
        for sid in e.get('steps', []):
            if sid not in step_ids: bad.append(w + ': step %r is not on any track' % sid)
        for sid in e.get('sources', []):
            if sid not in sources: bad.append(w + ': source %r is not in sources' % sid)
    for l in b['labels']:
        need(l, ['text', 'at', 'kind'], 'label %r' % l.get('text'))
        if l.get('kind') not in LABEL_KINDS: bad.append('label %r: unknown kind %r' % (l.get('text'), l.get('kind')))
        if 'at' in l: point_ok(l['at'], 'label %r' % l.get('text'))
        if l.get('show') and l['show'] not in LABEL_SHOWS: bad.append('label %r: show must be one of %s' % (l.get('text'), ', '.join(LABEL_SHOWS)))
    # reconstructed base maps: every feature says what it is, where it came from, how it was read and how sure it is
    packed = re.compile(r'^-?\d+,-?\d+(;-?\d+,-?\d+)+$')
    for r in b.get('reconstructions', []):
        w = 'reconstruction %s' % r.get('id'); need(r, ['id', 'title', 'label', 'about', 'layers', 'features'], w)
        if r.get('sheet') is not None and not (len(r['sheet']) == 4 and r['sheet'][0] < r['sheet'][2] and r['sheet'][1] < r['sheet'][3]): bad.append(w + ': sheet must be [west, south, east, north]')
        lay = {}
        for l in r.get('layers', []):
            x = '%s layer %s' % (w, l.get('id')); need(l, ['id', 'title', 'kind', 'source', 'method', 'confidence'], x); lay[l.get('id')] = l
            if l.get('kind') not in RECON_KINDS: bad.append(x + ': unknown kind %r' % l.get('kind'))
            if l.get('source') not in sources: bad.append(x + ': source %r is not in sources' % l.get('source'))
            if l.get('link') and not str(l['link']).startswith('https://'): bad.append(x + ': link must be an https address')
        seen = set()
        for f in r.get('features', []):
            x = '%s feature %s' % (w, f.get('id')); need(f, ['id', 'layer', 'kind', 'shape', 'at', 'from', 'to', 'source', 'method', 'confidence'], x)
            if f.get('id') in seen: bad.append(x + ': listed twice')
            seen.add(f.get('id'))
            if f.get('layer') not in lay: bad.append(x + ': layer %r is not in layers' % f.get('layer'))
            if f.get('kind') not in RECON_KINDS: bad.append(x + ': unknown kind %r' % f.get('kind'))
            if f.get('shape') not in RECON_SHAPES: bad.append(x + ': unknown shape %r' % f.get('shape'))
            if f.get('method') not in RECON_METHODS: bad.append(x + ': method must be one of %s' % ', '.join(RECON_METHODS))
            if f.get('confidence') not in LEVELS: bad.append(x + ': unknown confidence %r' % f.get('confidence'))
            if f.get('source') not in sources: bad.append(x + ': source %r is not in sources' % f.get('source'))
            for k in ('from', 'to'): time_ok(f.get(k), x + '.' + k)
            if f.get('kind') == 'ink':           # a period map's own ink as a picture (22 Nov 2026): the area is the picture's four corners, from the top-left clockwise
                if f.get('shape') != 'area' or not f.get('file'): bad.append(x + ': an ink picture needs shape "area" (its four corners) and a file')
                elif isinstance(f.get('at'), list) and f['at'] and isinstance(f['at'][0], str) and f['at'][0].count(';') not in (3, 4): bad.append(x + ': the area of an ink picture is its four corners')
                if f.get('from_zoom') is not None and not isinstance(f['from_zoom'], (int, float)): bad.append(x + ': from_zoom must be a number')
                fl = f.get('files')
                if fl is not None and not (isinstance(fl, list) and fl and all(isinstance(q, list) and len(q) == 2 and isinstance(q[0], (int, float)) and isinstance(q[1], str) for q in fl) and [q[0] for q in fl] == sorted(q[0] for q in fl)):
                    bad.append(x + ': files must be [[zoom, file], ...], the smallest picture first')
            if f.get('under') and f['under'] not in [g.get('id') for g in r.get('features', []) if g.get('kind') == 'ink']: bad.append(x + ': under %r names no ink picture' % f.get('under'))
            if f.get('shape') == 'point': point_ok(f.get('at'), x + '.at')
            elif f.get('shape') == 'areas':        # several areas: each a list of packed rings, the outline first
                if not (isinstance(f.get('at'), list) and f['at'] and all(isinstance(a, list) and a and all(isinstance(q, str) and packed.match(q) for q in a) for a in f['at'])): bad.append(x + ': at must be a list of areas, each a list of packed rings')
                else:
                    q = f['at'][0][0].split(';')[0].split(','); point_ok([int(q[0]) / 1e5, int(q[1]) / 1e5], x + '.at')
            elif not (isinstance(f.get('at'), list) and f['at'] and all(isinstance(q, str) and packed.match(q) for q in f['at'])): bad.append(x + ': at must be packed lines (lon,lat;dlon,dlat;...)')
            else:
                q = f['at'][0].split(';')[0].split(','); point_ok([int(q[0]) / 1e5, int(q[1]) / 1e5], x + '.at')
            if f.get('side') and f['side'] not in [sd.get('code') for sd in b.get('sides', [])]: bad.append(x + ': side %r is not a side code' % f.get('side'))
    B = b['base']; need(B, ['credit', 'lines', 'areas'], 'base')
    for l in B.get('lines', []):
        if len(l) != 4 or l[0] not in LINE_KINDS or not re.match(r'^-?\d+,-?\d+(;-?\d+,-?\d+)+$', l[3]): bad.append('base line not understood: %r' % (l[:3],)); break
    for a in B.get('areas', []):
        if len(a) != 3 or a[0] not in AREA_KINDS or not re.match(r'^-?\d+,-?\d+(;-?\d+,-?\d+){2,}$', a[2]): bad.append('base area not understood: %r' % (a[:2],)); break
    return bad


def write(battle, path):
    """Check the battle and save it. Refuses to write a file that does not meet the format."""
    battle = clean(dict(battle, format=FORMAT))
    # the lists the format always has, even when a battle has nothing to put in them
    for k in ('events', 'labels', 'maps'): battle.setdefault(k, [])
    battle['base'] = dict({'lines': [], 'areas': []}, **battle.get('base', {}))
    bad = validate(battle, os.path.dirname(path))
    if bad:
        raise SystemExit('battle file not written, %d problem(s):\n  ' % len(bad) + '\n  '.join(bad[:40]))
    order = ['format', 'id', 'title', 'subtitle', 'record', 'time', 'view', 'playback', 'opening', 'sides', 'nations', 'units', 'tracks', 'events', 'sources', 'labels', 'maps', 'base']
    battle = {k: battle[k] for k in order if k in battle} | {k: v for k, v in battle.items() if k not in order}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(battle, f, ensure_ascii=False, separators=(',', ':'))
    n = sum(len(t['steps']) for t in battle['tracks'])
    print('%s: %d units, %d tracks, %d steps, %d events, %d maps, %d KB' % (battle['id'], len(battle['units']), len(battle['tracks']), n, len(battle['events']), len(battle['maps']), os.path.getsize(path) // 1024))
    return battle


def used_sources(battle, catalogue, extra=()):
    """The sources a battle file needs: every source its steps, events, units and maps cite, taken from `catalogue`
    ({id: {title, citation, type, url}}), plus any listed in `extra`."""
    want = set(extra)
    for tr in battle['tracks']:
        for st in tr['steps']: want.update(st.get('sources', []))
    for e in battle.get('events', []): want.update(e.get('sources', []))
    for u in battle['units']:
        want.update(u.get('sources', []))
        for a in u.get('assignments', []): want.update(a.get('sources', []))
    for m in battle.get('maps', []):
        if m.get('source'): want.add(m['source'])
    for r in battle.get('reconstructions', []):
        want.update(l['source'] for l in r['layers'] if l.get('source')); want.update(f['source'] for f in r['features'] if f.get('source'))
    missing = sorted(want - set(catalogue))
    assert not missing, 'cited but not in the source list: %s' % missing
    return {k: catalogue[k] for k in sorted(want)}
