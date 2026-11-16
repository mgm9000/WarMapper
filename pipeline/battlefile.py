"""The common battle file: one format for every battle (docs/battle-file.md describes it in full).

tools/export_battles.py gathers each battle's record from the master workbook and hands it to write(), which checks it
against the format and saves playbacks/<battle>/battle.json. The playback pages read nothing else.
"""
import json, os, re

FORMAT = 'warmapper-battle/1'
ECHELONS = ['army', 'corps', 'division', 'brigade', 'regiment', 'battalion', 'squadrons', 'battery', 'company', 'section', 'detachment', 'headquarters']
BRANCHES = ['infantry', 'cavalry', 'artillery']
METHODS = ['stated', 'inferred', 'interpolated']
LEVELS = ['high', 'medium', 'low']
LABEL_KINDS = ['road', 'water', 'area', 'town', 'place', 'wood', 'landmark']
LINE_KINDS = ['road', 'rail', 'water', 'former-water']
AREA_KINDS = ['wood', 'water']
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
        if not (bs.get('current') or bs.get('map') or bs.get('series')): bad.append('playback base %s: needs "current", "map" or "series"' % bs.get('id'))
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
    missing = sorted(want - set(catalogue))
    assert not missing, 'cited but not in the source list: %s' % missing
    return {k: catalogue[k] for k in sorted(want)}
