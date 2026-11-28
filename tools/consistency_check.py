"""Check that every WarMapper battle keeps to the shared rules (docs/standing-rules.md, docs/presets.md).

  python3 tools/consistency_check.py                    rebuild every battle, then report (1) to (4) below
  python3 tools/consistency_check.py --against main     also list, battle by battle, what changed since main (a branch, a commit or a tag)
  python3 tools/consistency_check.py --against main --expect trenton,cowpens
                                                        and fail if any other battle's file changed (a change you did not mean to make)

(1) Rebuild. Every battle file is written again from the workbooks, in a temporary folder, and compared with the one in the repo, and
    every page with its battle file. A difference means the workbooks or the exporter changed and the export (or build) was not run.
(2) Changes since another version (--against): for each battle, the playback settings that changed (before -> after) and the other parts
    of the battle file that changed. Battles with no change are listed as such.
(3) Presets: for each battle, the presets it is based on and every row of its own that differs from them, with its reason (the why
    column) or "no reason recorded". Rows that only repeat a preset are listed too: they can go.
(4) Rules a program can check, each named by its number in the register. A broken rule fails the check; a warning (units of the two
    sides drawn on top of each other, a difference with no reason) is listed but does not.

Exit code 0 when nothing failed. It changes no file.
"""
import argparse, json, math, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import export_battles as E
import battlefile as bf

AMPM = re.compile(r'\b\d{1,2}(?::\d{2})?\s?(?:[ap]\.\s?m\.|[AP]M\b|[ap]m\b)|\b(?:a\.m\.|p\.m\.)', re.I)


def flat(o, pre=''):
    """{'zoom.max': 8, 'bases.2.short': 'Modern', ...}: a nested setting as the dotted names of the Playback settings sheet."""
    out = {}
    if isinstance(o, dict):
        for k, v in o.items(): out.update(flat(v, pre + str(k) + '.'))
    elif isinstance(o, list) and o and all(isinstance(v, dict) for v in o):
        for i, v in enumerate(o): out.update(flat(v, pre + str(i + 1) + '.'))
    else: out[pre[:-1]] = o
    return out


def show(v):
    s = json.dumps(v, ensure_ascii=False); return s if len(s) <= 70 else s[:67] + '...'


def rebuild(W):
    """{playback: (battle file text as the exporter writes it now, the battle)}, each written to a temporary file beside the battle's own
    (where its map pictures are, which the format check looks for) and removed again."""
    import contextlib, io
    out = {}
    for pb in W['Playbacks']:
        folder = os.path.join(ROOT, 'playbacks', pb['playback_id']); os.makedirs(folder, exist_ok=True)
        fd, p = tempfile.mkstemp(prefix='.check-', suffix='.json', dir=folder); os.close(fd)
        try:
            with contextlib.redirect_stdout(io.StringIO()): b = bf.write(E.export(pb, W), p)
            out[pb['playback_id']] = (open(p, encoding='utf-8').read(), b)
        finally: os.remove(p)
    return out


def page_current(name):
    """Whether the page has the battle file the repo has (tools/build.py writes it in)."""
    sys.path.insert(0, os.path.join(ROOT, 'tools')); import build
    p = os.path.join(ROOT, 'playbacks', name, 'index.html')
    return os.path.exists(p) and open(p, encoding='utf-8').read() == build.page(name, '../../app')


def changes(old, new):
    """Lines saying what changed in one battle file: settings one by one, the rest by part."""
    lines = []
    a, b = flat(old.get('playback') or {}), flat(new.get('playback') or {})
    for k in sorted(set(a) | set(b)):
        if a.get(k, '<unset>') != b.get(k, '<unset>'):
            lines.append('  setting %s: %s -> %s' % (k, show(a[k]) if k in a else 'not set', show(b[k]) if k in b else 'not set'))
    for part in sorted(set(old) | set(new)):
        if part == 'playback' or old.get(part) == new.get(part): continue
        if part == 'tracks':
            A = {s['id']: s for t in old['tracks'] for s in t['steps']}; B = {s['id']: s for t in new['tracks'] for s in t['steps']}
            ch = [i for i in set(A) | set(B) if A.get(i) != B.get(i)]
            lines.append('  tracks: %d steps changed (%s)' % (len(ch), ', '.join(sorted(ch)[:12]) + (' ...' if len(ch) > 12 else '')))
        else: lines.append('  %s changed' % part)
    return lines


def git_file(ref, path):
    try: return subprocess.run(['git', 'show', '%s:%s' % (ref, path)], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError: return None


def overrides(W, name):
    """(presets, [(setting, own value, preset value, why)], [settings that only repeat a preset]) for one battle."""
    rows = [r for r in W['Playback settings'] if r.get('playback_id') == name]
    own = E.settings(rows); names = E.chain(own); P = E.preset_table(W); F = {}
    for n in names: F.update(flat(E.settings(P.get(n, []))))
    use = {m.group(1): str(r['value']) for r in rows for m in [re.match(r'bases\.(\d+)\.use$', str(r['setting']))] if m}
    pb = next(p for p in W['Playbacks'] if p['playback_id'] == name)
    D = {k: v for k, v in F.items() if not k.startswith('base.')}; D = E.settings([{'setting': k, 'value': json.dumps(v) if isinstance(v, (list, dict)) else v} for k, v in D.items()])
    D.setdefault('rate', own.get('rate'))
    if D.get('rate') is None: D.pop('rate')
    E.derive(D, {'time_unit': pb['time_unit'], 'extent': [float(pb[k]) for k in ('west', 'south', 'east', 'north')]})
    for k, v in flat(D).items():
        if k not in F and k != 'rate': F[k] = v          # worked out from the battle (arrows.min_km, arrows.reach_minutes, trails.fade_after ...)
    diff, same = [], []
    for r in rows:
        s = str(r['setting']); v = E.settings([{'setting': 'x', 'value': r['value']}])['x']
        m = re.match(r'bases\.(\d+)\.(.+)$', s)
        key = 'base.%s.%s' % (use[m.group(1)], m.group(2)) if m and m.group(1) in use and m.group(2) != 'use' else s
        if key in F:
            if F[key] == v: same.append(s)
            else: diff.append((s, v, F[key], E.text(r.get('why'))))
    return names, diff, same


def rules(b, W):
    """(failures, warnings) for one battle file: the rules of the register that a program can check."""
    P = b.get('playback') or {}; fail = []; warn = []; day = b['time']['unit'] == 'day'
    ori = P.get('style') == 'orientation'   # an orientation (25 Nov 2026): clashes and places, no units, so the rules about units do not apply
    bases = P.get('bases') or []
    # SR-01: 24-hour time in everything shown as the playback's own words (a source's own wording, quoted, keeps its form)
    shown = [('event %s' % e['id'], (e.get('name') or '') + ' ' + (e.get('label') or '') + ' ' + (e.get('text') or '')) for e in b['events']]
    shown += [('summary %s' % s['from'], s['title'] + ' ' + s['text']) for s in b.get('summaries', [])]
    shown += [('opening text', (b.get('opening') or {}).get('text') or '')] + [('about %d' % (i + 1), t) for i, t in enumerate(P.get('about') or [])]
    shown += [('texts.%s' % k, v) for k, v in (P.get('texts') or {}).items()]
    shown += [('clash %s' % c['id'], ' '.join(str(c.get(k) or '') for k in ('result', 'captured', 'place')) + ' ' + str((c.get('other') or {}).get('text') or '')) for c in b.get('clashes', [])]
    for where, t in shown:
        m = AMPM.search(t)
        if m: fail.append('SR-01 24-hour time: %s says "%s"' % (where, t[max(0, m.start() - 25):m.end() + 5].strip()))
    # SR-02: a battle with its own reconstructed map opens on it
    recon = [x for x in bases if x.get('recon') and not x.get('hidden')]
    if recon:
        start = P.get('start_base')
        if start and start not in [x['id'] for x in recon]: fail.append('SR-02 landing view: it has a reconstructed map (%s) but opens on %s' % (recon[0]['id'], start))
        if not start and bases and not bases[0].get('recon'): fail.append('SR-02 landing view: it has a reconstructed map (%s) but does not open on it' % recon[0]['id'])
    def covers(q, box):                               # the player's inQuad: is point q inside the four corners
        sg = 0
        for i in range(4):
            p0, p1 = box[i], box[(i + 1) % 4]; c = (p1[0] - p0[0]) * (q[1] - p0[1]) - (p1[1] - p0[1]) * (q[0] - p0[0])
            if c:
                if sg and (c > 0) != (sg > 0): return False
                sg = c
        return True
    def start_map():                                  # the player's startBase(): start_base, else a period map over the opening view, else current
        if P.get('start_base'): return next((x for x in bases if x['id'] == P['start_base']), None)
        V = b['view']; bx = (V.get('presets') or {}).get((P.get('views') or [{}])[0].get('preset')) if P.get('views') else None; bx = bx or V['extent']
        dx, dy = (bx[2] - bx[0]) * 0.04, (bx[3] - bx[1]) * 0.04
        C = [[bx[0] + dx, bx[1] + dy], [bx[2] - dx, bx[1] + dy], [bx[2] - dx, bx[3] - dy], [bx[0] + dx, bx[3] - dy]]
        maps_ = {m['id']: m for m in b['maps']}
        for x in bases:
            m = maps_.get(x.get('map'))
            if m and m.get('georeferenced') is not False and not x.get('series') and m['images'] and m['images'][0].get('corners') and all(covers(c, m['images'][0]['corners']) for c in C): return x
        return next((x for x in bases if x.get('current')), bases[0] if bases else None)
    sb = start_map()
    if sb and sb.get('hidden'): fail.append('SR-02 landing view: it opens on %s, which is kept off the Type of map menu' % sb['id'])
    # SR-03 and SR-26: the Current map is today's topographic map, and its button says "Modern"
    cur = [x for x in bases if x.get('current')]
    if not cur: fail.append('SR-03 current map: no base is the current map')
    if not (P.get('modern') or {}).get('tiles'): fail.append('SR-03 current map: no modern topographic map (modern.tiles)')
    for x in cur:
        if x.get('short') != 'Modern': fail.append('SR-26 the current-map button says "%s", not "Modern"' % x.get('short'))
    # SR-04: opens wide and eases in when play is pressed
    if P.get('opening_zoom_out') is not None and P['opening_zoom_out'] < 1: fail.append('SR-04 opening view: opening_zoom_out is %s (at least 1)' % P['opening_zoom_out'])
    if P.get('follow') and (P['follow'].get('glide_seconds') or 6) < 10: fail.append('SR-04 opening view: Follow eases in over %s s (the rule is a slow ease: 10 s or more)' % (P['follow'].get('glide_seconds') or 6))
    if not P.get('follow') and not P.get('opening_ease'): fail.append('SR-04 opening view: no Follow and no opening_ease, so nothing eases in slowly from the whole ground')
    # SR-05: longer than two days, it pauses at each day's end with a summary
    import datetime as dt
    span = lambda v: dt.datetime.fromisoformat(v if len(v) > 10 else v + 'T00:00')
    n = (span(b['time']['end']) - span(b['time']['start'])).total_seconds() / 86400   # the days this playback covers
    if ori: orientation_rules(b, fail, warn); return fail, warn
    if n > 2 and P.get('day_pause') is False: fail.append('SR-05 day pauses: %.0f days and day_pause is off' % n)
    if n > 2 and not b.get('summaries'): warn.append('SR-05 day pauses: %.0f days and no summaries (the pause shows the day\'s events instead)' % n)
    # SR-06 and SR-07: arrows ahead of long moves, scaled to the battle, running a little way ahead
    A = P.get('arrows') or {}
    if A.get('on') is False: fail.append('SR-06 arrows: switched off')
    if A.get('min_km') is None: fail.append('SR-06 arrows: no limit set for this battle (the player would use 20 km)')
    if not A.get('reach_minutes'): fail.append('SR-07 arrows: no reach (reach_minutes): an arrow would run to the end of a long road')
    # SR-09: every map shown carries its credit (the player shows it, then keeps it in the i panel)
    maps = {m['id']: m for m in b['maps']}; recs = {r['id']: r for r in b.get('reconstructions', [])}
    for x in bases:
        if x.get('map') and not (maps.get(x['map']) or {}).get('credit'): fail.append('SR-09 credits: map %s has no credit' % x['map'])
        if x.get('imagery') and not x['imagery'].get('credit'): fail.append('SR-09 credits: imagery base %s has no credit' % x['id'])
        if x.get('recon') and not (recs.get(x['recon']) or {}).get('credit'): fail.append('SR-09 credits: reconstruction %s has no credit' % x['recon'])
    if not (P.get('modern') or {}).get('credit'): fail.append('SR-09 credits: the modern map has no credit')
    # SR-10: units of both sides on the map
    units = {u['id']: u for u in b['units']}
    sides = {units[t['unit']]['side'] for t in b['tracks'] if any(s.get('at') for s in t['steps'])}
    if len(sides) < 2: fail.append('SR-10 both sides: only %s has units on the map' % ', '.join(sides))
    # SR-11: symbols outside the current event stay clearly visible
    if (P.get('event_dim') if P.get('event_dim') is not None else 0.32) < 0.7: fail.append('SR-11 symbols: units outside the current event drawn at %s (the rule is 0.7)' % (P.get('event_dim') if P.get('event_dim') is not None else '0.32, the default'))
    # SR-15: one main map on the Type of map menu (the current map and the satellite view besides)
    main = [x['id'] for x in bases if not x.get('hidden') and not x.get('of') and not x.get('current') and not x.get('imagery')]
    if len(main) != 1: fail.append('SR-15 one main map: %d on the Type of map menu (%s)' % (len(main), ', '.join(main) or 'none'))
    # SR-16: the routes-taken layer
    if not (P.get('trails') or {}) or (P.get('trails') or {}).get('on') is False: fail.append('SR-16 routes taken: no routes-taken layer')
    # SR-17: events tied to the units on the map
    bare = [e['id'] for e in b['events'] if not e.get('steps')]
    if bare: warn.append('SR-17 events: %d of %d name no position rows (%s)' % (len(bare), len(b['events']), ', '.join(bare[:6]) + (' ...' if len(bare) > 6 else '')))
    # SR-21: never stated or high without a cited source
    for t in b['tracks']:
        for s in t['steps']:
            if s.get('virtual'): continue
            if (s.get('method') == 'stated' or s.get('confidence') == 'high') and not s.get('sources'):
                fail.append('SR-21 sources: row %s is %s with no source' % (s['id'], 'stated' if s.get('method') == 'stated' else 'high'))
    # SR-22: every source and map says what its rights are
    for k, s in (b.get('sources') or {}).items():
        if not s.get('rights'): warn.append('SR-22 rights: source %s has no rights recorded' % k)
    # SR-24 (labels and hover): every unit on the map has a name and a label
    for t in b['tracks']:
        u = units[t['unit']]
        if not (t.get('label') or u.get('label')) or not u.get('name'): fail.append('SR-24 labels: track %s has no %s' % (t['id'], 'label' if u.get('name') else 'name'))
    # SR-25: no "Times are estimates" note under the clock
    if P.get('time_note'): fail.append('SR-25 clock note: "%s" is shown under the clock' % P['time_note'].get('text'))
    # SR-27: the battlefields share their settings unless a reason is recorded (checked with the presets, below)
    # opposing symbols drawn on top of each other (battles followed by the clock)
    hits = E.contacts(b)
    if hits: warn.append('units of the two sides drawn within 50 m of each other: %d times (first: %s)' % (len(hits), hits[0]))
    over = E.pace(b)
    if over: warn.append('implausibly fast moves: %d (first: %s)' % (len(over), over[0]))
    return fail, warn


def orientation_rules(b, fail, warn):
    """The rules of an orientation playback (SR-28 to SR-30, 25 Nov 2026), and the shared rules that still apply to it. The rules about
    units (SR-05 day pauses, SR-06 and SR-07 arrows, SR-10 both sides' units, SR-16 routes, SR-17 events tied to units) do not: it has
    none. Morgan's choice for the pauses: one stop, at the end (no day_pause), with a summary for each year and a closing summary."""
    P = b.get('playback') or {}; bases = P.get('bases') or []
    maps = {m['id']: m for m in b['maps']}; recs = {r['id']: r for r in b.get('reconstructions', [])}
    for x in bases:   # SR-09, SR-15, SR-25 as for every battle
        if x.get('map') and not (maps.get(x['map']) or {}).get('credit'): fail.append('SR-09 credits: map %s has no credit' % x['map'])
        if x.get('imagery') and not x['imagery'].get('credit'): fail.append('SR-09 credits: imagery base %s has no credit' % x['id'])
        if x.get('recon') and not (recs.get(x['recon']) or {}).get('credit'): fail.append('SR-09 credits: reconstruction %s has no credit' % x['recon'])
    if not (P.get('modern') or {}).get('credit'): fail.append('SR-09 credits: the modern map has no credit')
    main = [x['id'] for x in bases if not x.get('hidden') and not x.get('of') and not x.get('current') and not x.get('imagery')]
    if len(main) > 1: fail.append('SR-15 one main map: %d on the Type of map menu (%s)' % (len(main), ', '.join(main)))
    if not main: warn.append('SR-15 one main map: no period or reconstructed map yet (the modern map only)')
    if P.get('time_note'): fail.append('SR-25 clock note: "%s" is shown under the clock' % P['time_note'].get('text'))
    if P.get('day_pause') not in (False, None): fail.append('SR-05 (orientation): it pauses during play (day_pause %r); Morgan chose one stop, at the end' % P.get('day_pause'))
    # SR-28: every clash is drawn by who won, from a cited source; a disputed one gives both readings
    C = b.get('clashes', [])
    if not C: warn.append('SR-28 clashes: an orientation with no clashes')
    for c in C:
        if not c.get('sources'): fail.append('SR-28 clashes: %s has no source for its result' % c['id'])
        if (c.get('method') == 'stated' or c.get('confidence') == 'high') and not c.get('sources'): fail.append('SR-21 sources: clash %s is %s with no source' % (c['id'], 'stated' if c.get('method') == 'stated' else 'high'))
        if c.get('disputed') and not (c.get('other') or {}).get('sources'): fail.append('SR-28 clashes: %s is disputed but its other reading cites no source' % c['id'])
    # SR-29: every change of control is dated and sourced
    for p in b.get('places', []):
        if not p.get('control'): warn.append('SR-29 control: %s has no record of who held it' % p['id'])
        for h in p.get('control', []):
            if not h.get('sources'): fail.append('SR-29 control: %s from %s (%s) has no source' % (p['id'], h['from'], h['held_by']))
            if (h.get('method') == 'stated' or h.get('confidence') == 'high') and not h.get('sources'): fail.append('SR-21 sources: %s from %s is %s with no source' % (p['id'], h['from'], h.get('method') or h.get('confidence')))
    # the pane's summaries: one for each year played, and one at the end
    y0, y1 = int(b['time']['start'][:4]), int(b['time']['end'][:4]); S = b.get('summaries', [])
    have = {y for x in S if x['kind'] == 'year' for y in range(int(x['from'][:4]), int(x['to'][:4]) + 1)}
    miss = [str(y) for y in range(y0, y1 + 1) if y not in have]
    if miss and not any(x['kind'] == 'leg' for x in S): warn.append('SR-28 summaries: no year summary for %s' % ', '.join(miss))
    if not any(x['kind'] == 'end' for x in S): warn.append('SR-28 summaries: no closing summary (kind end)')
    if any(x['kind'] == 'end' and not x.get('bridge') for x in S) and any(x['kind'] == 'next' for x in b.get('links', [])):
        warn.append('Storyline: the closing summary has no bridge to what comes next (Summaries, column bridge)')
    movement_rules(b, fail, warn)
    for k, s in (b.get('sources') or {}).items():   # SR-22
        if not s.get('rights'): warn.append('SR-22 rights: source %s has no rights recorded' % k)


def metres(p, q):
    """Distance in metres between two [lon, lat] points (an equirectangular approximation: good to well under 1% at these distances)."""
    import math
    k = math.cos(math.radians((p[1] + q[1]) / 2))
    return math.hypot((p[0] - q[0]) * 111320 * k, (p[1] - q[1]) * 110574)


def movement_rules(b, fail, warn):
    """The connection rule (27 Nov 2026, Morgan: "each movement should connect in timing and location with the actions/events currently on
    the map"). In an orientation every force's symbol (a track) is a movement or a standing pair at a clash, and:
      - it is tied to at least one event: an event names one of its waypoints (Events pos_ids);
      - that waypoint is at the event's clash, or at the place whose change of hands the event is: no further from it than the larger of
        the two precision_m;
      - and the waypoint's dates overlap the event's (compared by the day).
    A waypoint at a place with a record of who held it, held then by the force's enemy with no event tying the two, is a warning: the
    arrival must not contradict the Control row (show Morgan; change neither quietly)."""
    steps = {s['id']: (tr, s) for tr in b.get('tracks', []) for s in tr['steps']}
    side = {u['id']: u['side'] for u in b.get('units', [])}; code = {sd['id']: sd['code'] for sd in b.get('sides', [])}
    clash = {c['event']: c for c in b.get('clashes', [])}; changed = {}
    for p in b.get('places', []):
        for h in p.get('control', []):
            if h.get('event'): changed[h['event']] = p
    centre = lambda g: [sum(q[0] for q in g) / len(g), sum(q[1] for q in g) / len(g)]
    tied = {}
    for e in b['events']:
        for sid in e.get('steps', []):
            if sid not in steps: continue
            tr, st = steps[sid]; tied.setdefault(tr['id'], []).append(e['id'])
            target = clash.get(e['id']) or changed.get(e['id'])
            if not target: fail.append('Connection rule: event %s names %s\'s waypoint %s but has no clash or change of hands on the map' % (e['id'], tr['id'], sid)); continue
            if not st.get('at'): fail.append('Connection rule: %s waypoint %s (event %s) has no place' % (tr['id'], sid, e['id'])); continue
            d = metres(centre(st['at']), target['at']); lim = max((st.get('location') or {}).get('precision_m') or 0, (target.get('location') or {}).get('precision_m') or 0)
            if d > lim: fail.append('Connection rule: %s waypoint %s is %.1f km from %s (event %s), more than the precision of either (%.1f km)' % (tr['id'], sid, d / 1000, target['id'], e['id'], lim / 1000))
            a, z = st['show'][0][:10], st['show'][1][:10]; ea, ez = e['start'][:10], e['end'][:10]
            if z < ea or a > ez: fail.append('Connection rule: %s waypoint %s (%s to %s) is not on the dates of event %s (%s to %s)' % (tr['id'], sid, a, z, e['id'], ea, ez))
    for tr in b.get('tracks', []):
        if tr['id'] not in tied: fail.append('Connection rule: %s (%s) is tied to no event on the map (Events pos_ids)' % (tr['id'], tr.get('label') or tr['unit']))
        me = code.get(side.get(tr['unit']))
        for st in tr['steps']:
            if not st.get('at') or st['id'] in {s for e in b['events'] for s in e.get('steps', [])}: continue
            for p in b.get('places', []):
                lim = max((st.get('location') or {}).get('precision_m') or 0, (p.get('location') or {}).get('precision_m') or 0)
                if metres(centre(st['at']), p['at']) > lim: continue
                held = [h for h in p.get('control', []) if (h.get('from') or '') <= st['show'][0][:10]]
                if held and held[-1]['held_by'] not in (me, 'contested'):
                    warn.append('Connection rule (control): %s waypoint %s is at %s on %s, which the record has held by %s then; check it against the Control row' % (tr['id'], st['id'], p['name'], st['show'][0][:10], held[-1]['held_by']))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('--against'); ap.add_argument('--expect', default=None)
    a = ap.parse_args(argv)
    W = E.load(); R = rebuild(W); failed = 0
    print('(1) Rebuild from the workbooks')
    for name, (text, b) in R.items():
        path = os.path.join(ROOT, 'playbacks', name, 'battle.json')
        have = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if have != text:
            failed += 1; print('  %s: FAIL, the battle file in the repo is not what the workbooks give (run tools/export_battles.py)' % name)
            if have: print('\n'.join(changes(json.loads(have), b)))
        elif not page_current(name): failed += 1; print('  %s: FAIL, the page is out of date (run tools/build.py)' % name)
        else: print('  %s: battle file and page current' % name)
    stale = E.check_csv()
    if stale: failed += 1; print('  FAIL, CSV copies out of date: %s' % ', '.join(stale))
    if a.against:
        print('\n(2) Changes since %s' % a.against); expect = set((a.expect or '').split(',')) - {''}
        for name, (text, b) in R.items():
            old = git_file(a.against, 'playbacks/%s/battle.json' % name)
            if old is None: print('  %s: new' % name); continue
            lines = changes(json.loads(old), b)
            if not lines: print('  %s: unchanged' % name); continue
            bad = a.expect is not None and name not in expect
            if bad: failed += 1
            print('  %s: %s%d change(s)' % (name, 'FAIL, not expected to change: ' if bad else '', len(lines))); print('\n'.join(lines))
    print('\n(3) Presets and the rows that differ from them')
    for name in R:
        names, diff, same = overrides(W, name)
        print('  %s: based on %s' % (name, ', '.join(names)))
        for s, v, pv, why in diff: print('    %s = %s (preset: %s): %s' % (s, show(v), show(pv), why or 'NO REASON RECORDED'))
        if not diff: print('    no differences')
        if same: print('    repeat a preset and can go: %s' % ', '.join(same))
    print('\n(4) Rules')
    for name, (text, b) in R.items():
        fail, warn = rules(b, W); failed += len(fail)
        print('  %s: %s' % (name, 'all checked rules kept' if not fail else '%d rule(s) broken' % len(fail)))
        for f in fail: print('    FAIL ' + f)
        for w in warn: print('    warn ' + w)
    print('\n%s' % ('Nothing failed.' if not failed else '%d failure(s).' % failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
