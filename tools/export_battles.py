"""Write every battle's battle file from the master workbook, or check the ones already written.

The workbooks in data/WarMapper battle data/ are the master copy of the battle data: one per war (the same sheets in each, holding only
that war's rows) and "Sources and notes.xlsx" (the change log, Sources and Source candidates, which every war shares). This script reads
them all as one set of tables and writes one battle file per row of the Playbacks sheets (playbacks/<playback>/battle.json, in the format
docs/battle-file.md describes). No battle has a script of its own: a new battle is new rows in its war's workbook. It also writes every
sheet as a CSV file (data/WarMapper battle data/csv/<workbook>/<sheet>.csv), so a change to a workbook can be read line by line in git.

  python3 tools/export_battles.py              write all battle files, then check them
  python3 tools/export_battles.py ypres        one battle only
  python3 tools/export_battles.py --check      check the files as they stand, without rewriting them (and that the CSV copies are current)

A battle file that breaks the format is not written. Positions that would have a unit move implausibly fast are listed as warnings, and so
are places where one side's symbol is drawn on top of the other's (a unit overrun on the map without the data saying what became of it).
After exporting, run tools/build.py to put the new data into the pages.
"""
import csv, datetime as dt, io, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import battlefile as bf

WORKBOOK = os.path.join(ROOT, 'data', 'WarMapper battle data')   # the folder of workbooks; its name is the record's "workbook"
SHARED = 'Sources and notes'                                       # the workbook every war shares
CSV_DIR = os.path.join(WORKBOOK, 'csv')
BRANCH = {'horse artillery': 'artillery'}
ECHELON = {'regiment (part)': 'regiment'}
ARRIVAL_NOTE = "The approach is not recorded in the sources read. The unit is drawn coming up from %s the day before it is first placed."
VIRTUAL_NOTE = "Shown leaving its division's last recorded position. Where the unit itself was at this moment is not in the sources read."
# a row's own id, on the sheets whose ids must not repeat across the workbooks (a war's rows sit in one workbook only)
IDS = {'Wars': 'war_id', 'Campaigns': 'campaign_id', 'Battles': 'battle_id', 'Phases': 'phase_id', 'Sides': 'side_id', 'Units': 'unit_id',
       'Assignments': 'assign_id', 'Positions': 'pos_id', 'Routes': 'route_id', 'Events': 'event_id', 'Hypotheses': 'hypothesis_id',
       'Gaps': 'gap_id', 'Places': 'place_id', 'Sources': 'source_id', 'Source candidates': 'candidate_id', 'Playbacks': 'playback_id',
       'Reconstructions': 'recon_id', 'Links': 'link_id', 'Clashes': 'clash_id', 'Control places': 'cplace_id', 'Control': 'control_id'}


def workbooks():
    """The workbooks of the folder, the war workbooks first (by name), then the shared one."""
    names = sorted(f[:-5] for f in os.listdir(WORKBOOK) if f.endswith('.xlsx') and not f.startswith('~$'))
    assert SHARED in names, 'no "%s.xlsx" in %s' % (SHARED, WORKBOOK)
    return [n for n in names if n != SHARED] + [SHARED]


def load():
    """Every sheet as a list of rows, each a dict by column heading: a sheet that more than one workbook has is read as one, the rows of
    each workbook in turn. Each war workbook holds one war: a row naming another war's campaign, side or playback stops the export, and so
    does an id used twice, or a war workbook whose sheets differ from the others'."""
    import openpyxl
    out = {}; layout = {}; whose = {}
    for name in workbooks():
        wb = openpyxl.load_workbook(os.path.join(WORKBOOK, name + '.xlsx'), read_only=True, data_only=True)
        if name != SHARED: layout[name] = [ws.title for ws in wb.worksheets]
        for ws in wb.worksheets:
            it = ws.iter_rows(values_only=True); head = next(it, None)
            if not head: continue
            rows = [dict(zip(head, r)) for r in it if r and r[0] not in (None, '')]
            for r in rows: whose[id(r)] = name
            out.setdefault(ws.title, []).extend(rows)
    first = next(iter(layout.values()), [])
    for name, sheets in layout.items():
        assert sheets == first, '%s.xlsx: its sheets (%s) differ from the other war workbooks\' (%s)' % (name, ', '.join(sheets), ', '.join(first))
    for sheet, key in IDS.items():
        seen = {}
        for r in out.get(sheet, []):
            k = r.get(key)
            if k in (None, ''): continue
            assert k not in seen, '%s: id %s is in both %s.xlsx and %s.xlsx (or twice in one)' % (sheet, k, seen[k], whose[id(r)])
            seen[k] = whose[id(r)]
    war_of = {}                                       # each war workbook's war, from its Wars sheet
    for r in out.get('Wars', []): war_of.setdefault(whose[id(r)], set()).add(r['war_id'])
    for name, w in war_of.items(): assert len(w) == 1, '%s.xlsx: its Wars sheet must name one war, not %s' % (name, ', '.join(sorted(w)))
    war_of = {n: next(iter(w)) for n, w in war_of.items()}
    camp = {r['campaign_id']: r['war_id'] for r in out.get('Campaigns', [])}
    side = {r['side_id']: r['war_id'] for r in out.get('Sides', [])}
    pb = {r['playback_id']: camp.get(r['campaign_id']) for r in out.get('Playbacks', [])}
    test = {'Campaigns': lambda r: r['war_id'], 'Sides': lambda r: r['war_id'], 'Units': lambda r: side.get(r['side_id']),
            'Positions': lambda r: camp.get(r['campaign_id']), 'Routes': lambda r: camp.get(r['campaign_id']), 'Events': lambda r: camp.get(r['campaign_id']),
            'Playbacks': lambda r: camp.get(r['campaign_id'])}
    for s in ('Tracks', 'Playback settings', 'Labels', 'Maps', 'Summaries', 'Nations', 'Reconstructions', 'Clashes', 'Control places'): test[s] = lambda r: pb.get(r['playback_id'])
    cpl = {r['cplace_id']: pb.get(r['playback_id']) for r in out.get('Control places', [])}
    test['Control'] = lambda r: cpl.get(r['cplace_id'])
    for sheet, f in test.items():
        for r in out.get(sheet, []):
            name = whose[id(r)]
            if name == SHARED: continue
            assert f(r) == war_of.get(name), '%s.xlsx, %s: the row %s belongs to %s, not to this workbook\'s war (%s)' % (
                name, sheet, next(iter(r.values())), f(r), war_of.get(name))
    title = {r['source_id']: r['title'] for r in out.get('Sources', [])}
    for r in out.get('Source uses', []):
        assert r['source_id'] in title, '%s.xlsx, Source uses: %s is not on the Sources sheet' % (whose[id(r)], r['source_id'])
    return out


def cell_text(v):
    """A cell as the CSV copy writes it: formulas as written, dates and times as the workbook's own form, numbers without a needless .0."""
    if v is None: return ''
    if isinstance(v, dt.datetime): return v.strftime('%Y-%m-%d %H:%M:%S' if v.second else '%Y-%m-%d %H:%M') if (v.hour or v.minute or v.second) else v.strftime('%Y-%m-%d')
    if isinstance(v, dt.date): return v.isoformat()
    if isinstance(v, float) and v.is_integer(): return str(int(v))
    return str(v)


def csv_copies():
    """{path: text}: every sheet of every workbook as CSV, formulas as written, trailing empty rows and columns left off."""
    import openpyxl
    files = {}
    for name in workbooks():
        wb = openpyxl.load_workbook(os.path.join(WORKBOOK, name + '.xlsx'), read_only=True)
        for ws in wb.worksheets:
            rows = [[cell_text(v) for v in r] for r in ws.iter_rows(values_only=True)]
            while rows and not any(rows[-1]): rows.pop()
            width = max((max((i + 1 for i, v in enumerate(r) if v), default=0) for r in rows), default=0)
            buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
            for r in rows: w.writerow((r + [''] * width)[:width])
            files[os.path.join(CSV_DIR, name, ws.title + '.csv')] = buf.getvalue()
    return files


def write_csv():
    files = csv_copies()
    for path, text in files.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != text: open(path, 'w', encoding='utf-8').write(text)
    stale = [os.path.join(d, f) for d, _, fs in os.walk(CSV_DIR) for f in fs if os.path.join(d, f) not in files]
    for p in stale: os.remove(p)                       # a sheet that is gone
    return len(files)


def check_csv():
    """The CSV copies that do not match their workbook: they are written by the export, never edited by hand."""
    files = csv_copies(); bad = []
    for path, text in files.items():
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != text: bad.append(os.path.relpath(path, ROOT))
    have = {os.path.join(d, f) for d, _, fs in os.walk(CSV_DIR) for f in fs} if os.path.isdir(CSV_DIR) else set()
    bad += [os.path.relpath(p, ROOT) + ' (no such sheet)' for p in sorted(have - set(files))]
    return bad


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


EVERY = 'all'       # the preset every battle starts from, before the ones its based_on row names


def preset_table(W):
    """{preset: [rows]} from the Playback presets sheet of the shared workbook (columns preset, setting, value, what it does, why)."""
    out = {}
    for r in W.get('Playback presets', []):
        out.setdefault(str(r['preset']).strip(), []).append({'setting': r['setting'], 'value': r['value']})
    return out


def merge(into, over):
    """Lay `over` on `into`: names inside names are merged, anything else (a value, a list) replaces what was there."""
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(into.get(k), dict): merge(into[k], v)
        else: into[k] = json.loads(json.dumps(v))
    return into


def chain(own):
    """The presets a battle is based on, in the order they are laid on: `all`, then those its based_on row names."""
    named = own.get('based_on') or []
    if isinstance(named, str): named = [n.strip() for n in named.split(',') if n.strip()]
    return [EVERY] + [n for n in named if n != EVERY]


def resolve(rows, W, battle=None):
    """A battle's playback settings: its presets laid on one another in turn (Playback presets sheet), then its own rows on top. The battle
    file gets the result, so it reads as if the battle had set everything itself: the format and the player are unchanged by presets.
    - based_on (the battle's own row) names its presets, e.g. ["tactical", "us-maps"]; `all` comes first for every battle.
    - A preset's base.<name>.* is a standard map for the Type of map menu; a battle's bases.N.use = <name> takes it, and the battle's own
      bases.N.* rows win over it.
    - Worked out from the battle itself (where the battle does not set the value): arrows.min_share (a share of the width of the battle's
      ground, view extent) gives arrows.min_km; arrows.reach_seconds (seconds of play at the opening speed) gives arrows.reach_minutes;
      trails.fade_seconds gives trails.fade_after and trails.fade_over. These three never reach the battle file themselves.
    - start_base, where the battle does not set it: its first reconstructed map on the Type of map menu, if it has one (SR-02); otherwise
      the player's own rule (a period map that covers the opening view, else the current map)."""
    own = settings(rows); P = preset_table(W); names = chain(own); out = {}
    for n in names:
        assert n in P, 'Playback settings: based_on names the preset %r, which is not on the Playback presets sheet' % n
        merge(out, settings(P[n]))
    own.pop('based_on', None)
    templates = out.pop('base', {}) or {}
    for b in own.get('bases') or []:
        if b and b.get('use'):
            t = templates.get(b['use']); assert t, 'Playback settings: bases use %r, which no preset of this battle defines (base.%s.*)' % (b['use'], b['use'])
            u = b.pop('use'); full = merge(json.loads(json.dumps(t)), b); b.clear(); b.update(full)
    out = merge(out, own)
    if battle is not None: derive(out, battle)
    return out


def derive(S, battle):
    """The values a preset asks to be worked out from the battle's size and time scale (see resolve)."""
    rate = S.get('rate') or (1 if battle['time_unit'] == 'day' else 5)
    A = S.get('arrows') or {}; share = A.pop('min_share', None); secs = A.pop('reach_seconds', None)
    if share is not None and 'min_km' not in A:
        w, s_, e, n = battle['extent']; width = (e - w) * 111.32 * math.cos(math.radians((s_ + n) / 2))
        A['min_km'] = round(share * width, 2 if share * width < 1 else 1)
    if secs is not None and 'reach_minutes' not in A: A['reach_minutes'] = num(round(secs * rate, 2))
    if 'start_base' not in S:   # SR-02: a battle with its own reconstructed map on the menu opens on it (Morgan, 24 Nov 2026)
        rc = [x for x in S.get('bases') or [] if x and x.get('recon') and not x.get('hidden')]
        if rc: S['start_base'] = rc[0]['id']
    T = S.get('trails') or {}; fs = T.pop('fade_seconds', None)
    if fs is not None:
        if 'fade_after' not in T: T['fade_after'] = num(round(fs * rate, 2))
        if 'fade_over' not in T: T['fade_over'] = num(round(fs * rate, 2))


def in_order(o):
    """The playback settings with every set of names in alphabetical order (lists keep theirs: bases, views, about). The player looks
    settings up by name, so the order means nothing to it; a fixed order keeps a battle file the same whichever rows, of the battle or of
    its presets, a setting comes from."""
    if isinstance(o, dict): return {k: in_order(o[k]) for k in sorted(o)}
    if isinstance(o, list): return [in_order(v) for v in o]
    return o


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
                          'name': p.get('name'), 'desc': p.get('desc'), 'class': p.get('class'), 'width_m': p.get('width_m'), 'min_px': p.get('min_px'), 'number': p.get('number'), 'side': p.get('side'), 'part': p.get('part'), 'file': p.get('file'), 'from_zoom': p.get('from_zoom'), 'files': p.get('files'), 'under': p.get('under'),
                          'from': bf.iso(p.get('from')), 'to': bf.iso(p.get('to')), 'source': p.get('source_id'), 'method': p.get('method'), 'confidence': p.get('confidence'),
                          'precision_m': p.get('precision_m'), 'basis': p.get('basis'), 'review': p.get('review')})
        for l in layers: l['features'] = sum(1 for f in feats if f['layer'] == l['id'])
        out.append({'id': rid, 'title': r['title'], 'label': text(r.get('label')), 'about': text(r.get('about')), 'note': text(r.get('notes')), 'credit': text(r.get('credit')), 'style': text(r.get('style')),
                    'made': when(r.get('made')), 'review': text(r.get('review_status')), 'file': r['file'], 'sheet': G.get('sheet'), 'layers': layers, 'features': feats})
    return out


def links(pb, W):
    """BP-34: a campaign playback and the battle playbacks inside it link to each other (Links sheet: one row per pair, both of one war).
    The campaign's file lists its battles, each with the stretch of time the battle's playback covers; the battle's file names its campaign.
    Times come from the Playbacks rows, so they cannot drift apart. `at` is where the battle opens from the campaign (its start if empty)."""
    rows = {r['playback_id']: r for r in W['Playbacks']}; out = []
    camp_of = {r['playback_id']: r['campaign_id'] for r in W['Playbacks']}
    war = {c['campaign_id']: c['war_id'] for c in W['Campaigns']}
    for r in W.get('Links', []):
        c, b = text(r.get('campaign_playback')), text(r.get('battle_playback'))
        assert c in rows and b in rows, 'Links %s: %s and %s must both be rows on Playbacks' % (r['link_id'], c, b)
        assert war[camp_of[c]] == war[camp_of[b]], 'Links %s: %s and %s are not of the same war' % (r['link_id'], c, b)
        assert c != b, 'Links %s: a playback cannot link to itself' % r['link_id']
        if pb['playback_id'] == c:
            o = rows[b]
            out.append({'kind': 'battle', 'playback': b, 'title': o['title'], 'label': text(r.get('label')), 'from': when(o['time_start']), 'to': when(o['time_end']),
                        'at': when(r.get('opens_at')), 'unit': o['time_unit']})
        elif pb['playback_id'] == b:
            o = rows[c]
            out.append({'kind': 'campaign', 'playback': c, 'title': o['title'], 'label': text(r.get('campaign_label')), 'from': when(o['time_start']), 'to': when(o['time_end']),
                        'unit': o['time_unit']})
    out.sort(key=lambda x: (x['kind'], x['from']))
    return out


def located(r):
    """How a clash or a place was put on the map, from the same columns the Positions sheet uses."""
    src = text(r.get('coord_source'))
    return {'source': None if src == 'none' else src, 'basis': text(r.get('coordinate_basis')), 'confidence': text(r.get('coordinate_confidence')),
            'precision_m': int(r['coord_precision_m']) if not blank(r.get('coord_precision_m')) else None}


def orientation(pb, W):
    """An orientation's clashes and places (since 25 Nov 2026): the Clashes sheet, one row per clash or capture, tied to its event; the
    Control places sheet, one row per town, village, fort or port; the Control sheet, one row each time a place changes hands."""
    name = pb['playback_id']
    clashes = []
    for r in [r for r in W.get('Clashes', []) if r.get('playback_id') == name]:
        other = {'won_by': text(r.get('other_won_by')), 'text': text(r.get('other_reading')), 'sources': bf.ids(r.get('other_source_ids'))} if yes(r.get('disputed')) else None
        clashes.append({'id': r['clash_id'], 'event': r['event_id'], 'kind': text(r.get('kind')) or 'fight', 'won_by': text(r.get('won_by')), 'at': bf.ll(r['lat'], r['lon']),
                        'place': text(r.get('place')), 'result': text(r.get('result')), 'captured': text(r.get('captured')), 'captured_by': text(r.get('captured_by')),
                        'ships': text(r.get('ships')), 'disputed': True if yes(r.get('disputed')) else None, 'other': other, 'hypothesis': text(r.get('hypothesis_id')),
                        'method': text(r.get('result_method')), 'confidence': text(r.get('overall_confidence')), 'location': located(r),
                        'sources': bf.ids(r.get('source_ids')), 'notes': text(r.get('notes')), 'review': text(r.get('review_status'))})
    changes = {}
    for r in W.get('Control', []): changes.setdefault(r['cplace_id'], []).append(r)
    places = []
    for r in [r for r in W.get('Control places', []) if r.get('playback_id') == name]:
        ctl = [{'from': when(h['from']), 'held_by': text(h['held_by']), 'basis': text(h.get('basis')), 'event': text(h.get('event_id')), 'method': text(h.get('method')),
                'confidence': text(h.get('confidence')), 'sources': bf.ids(h.get('source_ids')), 'notes': text(h.get('notes')), 'review': text(h.get('review_status'))}
               for h in changes.get(r['cplace_id'], [])]
        ctl.sort(key=lambda h: h['from'] or '')
        places.append({'id': r['cplace_id'], 'name': r['name'], 'kind': text(r.get('kind')), 'at': bf.ll(r['lat'], r['lon']), 'location': located(r),
                       'sources': bf.ids(r.get('source_ids')), 'notes': text(r.get('notes')), 'control': ctl})
    return clashes, places


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

    S = resolve(mine(W['Playback settings']), W, {'time_unit': pb['time_unit'], 'extent': [float(pb[k]) for k in ('west', 'south', 'east', 'north')]})
    ARR = S.get('arrival')   # units that come into the battle late are drawn coming up, not appearing
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
    presets = S.pop('preset', None)
    own = S.pop('sides', None) or {}                  # a playback's own names for the sides (sides.<code>.short, sides.<code>.name): a war's sides are shared by its playbacks
    for sd in sides: sd.update({k: v for k, v in (own.get(sd['code']) or {}).items() if k in ('short', 'name')})
    if 'rear' in S: S['rear']['at'] = bf.ll(S['rear'].pop('lat'), S['rear'].pop('lon'))
    S = in_order(S)
    bp = os.path.join(ROOT, 'data', 'base', name + '.json')   # an orientation without its own cut of today's ground draws the modern map only
    base = json.load(open(bp, encoding='utf-8')) if os.path.exists(bp) else {'credit': '', 'lines': [], 'areas': []}
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
    cl, pl = orientation(pb, W)
    if cl: battle['clashes'] = cl
    if pl: battle['places'] = pl
    lk = links(pb, W)
    if lk: battle['links'] = lk
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
        if not args:
            load()                                       # the workbooks themselves: one war each, no id twice
            stale = check_csv()
            print('workbooks: %s' % ('CSV copies current' if not stale else 'CSV copies out of date (run the export):\n  ' + '\n  '.join(stale)))
            failed += bool(stale)
        return 1 if failed else 0
    W = load()
    for pb in W['Playbacks']:
        if args and pb['playback_id'] not in args: continue
        folder = os.path.join(ROOT, 'playbacks', pb['playback_id']); os.makedirs(folder, exist_ok=True)
        battle = bf.write(export(pb, W), os.path.join(folder, 'battle.json'))
        for w in pace(battle): print('  check this:', w)
        bare = [e['id'] for e in battle['events'] if not e.get('steps')]
        if bare: print('  events with no position rows (BP-32 cannot tie them to units on the map): %s' % ', '.join(bare))
        for w in contacts(battle): print('  contact:', w)
    print('CSV copies: %d sheets' % write_csv())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
