"""Playback presets (24 Nov 2026, session B of claude/consistency-rules-prompt.md).

Shared settings move out of each battle's Playback settings rows into one Playback presets sheet in Sources and notes.xlsx. A battle names
the presets it is based on (based_on) and keeps only the rows where it differs, each with a reason in the new `why` column.
tools/export_battles.py lays the presets on one another and then the battle's own rows (resolve), so the battle file reads as before.

Each step is one commit and is run once, in order:

  python3 pipeline/presets_2026_11_24.py refactor     presets that hold only what the battles already share: every battle file unchanged
  python3 pipeline/presets_2026_11_24.py <step>       one of the unifications Morgan approved (see STEPS at the end)

A step stops if it has already been run.
"""
import json, os, sys, datetime as dt
import openpyxl
from copy import copy

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
WARS = {'U.S. Civil War': ['gettysburg'], 'Revolutionary War': ['trenton', 'cowpens'], 'World War I': ['ypres'], 'Philippine War': ['manila', 'luzon1899']}
HEAD = ['playback_id', 'setting', 'value', 'what it does', 'why']
PHEAD = ['preset', 'setting', 'value', 'what it does', 'why']
SHEET = 'Playback presets'


def parse(v):
    """A cell as the exporter reads it: [..] and {..} are JSON, whole floats are integers."""
    if isinstance(v, str) and v.strip()[:1] in '[{': return json.loads(v)
    if isinstance(v, float) and v.is_integer(): return int(v)
    return v


class Book:
    """The four war workbooks' Playback settings sheets and the shared Playback presets sheet, as lists of rows (dicts) to edit and write back."""
    def __init__(self):
        self.wb = {w: openpyxl.load_workbook(os.path.join(FOLDER, w + '.xlsx')) for w in WARS}
        self.sh = openpyxl.load_workbook(SHARED)
        self.rows = {}
        for w, wb in self.wb.items():
            ws = wb['Playback settings']; head = [c.value for c in ws[1]]
            for r in ws.iter_rows(min_row=2, values_only=True):
                if not r or r[0] in (None, ''): continue
                d = dict(zip(head, r)); self.rows.setdefault(d['playback_id'], []).append(
                    {'setting': d['setting'], 'value': d['value'], 'what': d.get('what it does'), 'why': d.get('why')})
        self.presets = {}
        if SHEET in self.sh.sheetnames:
            ws = self.sh[SHEET]
            for r in ws.iter_rows(min_row=2, values_only=True):
                if not r or r[0] in (None, ''): continue
                d = dict(zip(PHEAD, r)); self.presets.setdefault(d['preset'], []).append(
                    {'setting': d['setting'], 'value': d['value'], 'what': d.get('what it does'), 'why': d.get('why')})

    def get(self, pb, setting):
        for r in self.rows[pb]:
            if r['setting'] == setting: return r
        return None

    def set(self, pb, setting, value, why=None, what=None, after=None):
        r = self.get(pb, setting)
        if r is None:
            r = {'setting': setting, 'value': value, 'what': what, 'why': why}
            rows = self.rows[pb]; at = next((i + 1 for i, x in enumerate(rows) if x['setting'] == after), len(rows)) if after else len(rows)
            rows.insert(at, r)
        else:
            r['value'] = value
            if why is not None: r['why'] = why
            if what is not None: r['what'] = what
        return r

    def drop(self, pb, setting):
        n = len(self.rows[pb]); self.rows[pb] = [r for r in self.rows[pb] if r['setting'] != setting]; return n - len(self.rows[pb])

    def pset(self, preset, setting, value, what=None, why=None):
        rows = self.presets.setdefault(preset, [])
        for r in rows:
            if r['setting'] == setting:
                r['value'] = value
                if what is not None: r['what'] = what
                if why is not None: r['why'] = why
                return
        rows.append({'setting': setting, 'value': value, 'what': what, 'why': why})

    def pget(self, preset, setting):
        return next((r for r in self.presets.get(preset, []) if r['setting'] == setting), None)

    def save(self, war_note, shared_note):
        for w, wb in self.wb.items():
            ws = wb['Playback settings']; style = [copy(c._style) for c in ws[2]] if ws.max_row > 1 else None
            if ws.max_row > 1: ws.delete_rows(2, ws.max_row)
            for i, h in enumerate(HEAD): ws.cell(1, i + 1, h)._style = copy(ws.cell(1, 1)._style)
            ws.column_dimensions['E'].width = 60
            n = 2
            for pb in WARS[w]:
                for r in self.rows[pb]:
                    for i, v in enumerate([pb, r['setting'], r['value'], r['what'], r['why']]):
                        c = ws.cell(n, i + 1, v)
                        if style: c._style = copy(style[min(i, len(style) - 1)])
                    n += 1
            if war_note: wb['Read me'].append(list(war_note))
            wb.save(os.path.join(FOLDER, w + '.xlsx'))
        if SHEET not in self.sh.sheetnames:
            ws = self.sh.create_sheet(SHEET, 1)
            for i, h in enumerate(PHEAD): ws.cell(1, i + 1, h).font = openpyxl.styles.Font(bold=True)
            for col, wd in zip('ABCDE', (16, 30, 60, 60, 70)): ws.column_dimensions[col].width = wd
            ws.freeze_panes = 'C2'
        ws = self.sh[SHEET]
        if ws.max_row > 1: ws.delete_rows(2, ws.max_row)
        n = 2
        for p in PRESET_ORDER + [p for p in self.presets if p not in PRESET_ORDER]:
            for r in self.presets.get(p, []):
                for i, v in enumerate([p, r['setting'], r['value'], r['what'], r['why']]):
                    ws.cell(n, i + 1, v).alignment = openpyxl.styles.Alignment(wrap_text=True, vertical='top')
                n += 1
        if shared_note:
            rm = self.sh['Read me']; rm.insert_rows(1, 3); rm.cell(1, 1, shared_note[0]); rm.cell(2, 1, shared_note[1])
        self.sh.save(SHARED)


PRESET_ORDER = ['all', 'tactical', 'operational', 'us-maps', 'world-maps', 'civil-war']
BASED_ON = {'gettysburg': ['tactical', 'us-maps', 'civil-war'], 'trenton': ['tactical', 'us-maps'], 'cowpens': ['tactical', 'us-maps'],
            'manila': ['tactical', 'world-maps'], 'ypres': ['operational', 'world-maps'], 'luzon1899': ['operational', 'world-maps']}
MEMBERS = {p: [b for b, c in BASED_ON.items() if p in c] for p in PRESET_ORDER[1:]}
MEMBERS['all'] = list(BASED_ON)
# What each preset holds at the start: settings the battles already share. `from` is the battle whose value the preset takes; the others
# that differ keep their own row. Every battle of the preset must already set the value, so no battle file changes.
START = {
    'tactical': [('style', 'trenton'), ('scale_bar', 'trenton'), ('question_mark', 'trenton'), ('zoom.max', 'trenton'), ('zoom.follow_max', 'trenton'),
                 ('zoom.min_factor', 'trenton')],
    'operational': [('style', 'ypres'), ('scale_bar', 'ypres'), ('question_mark', 'ypres'), ('zoom.min_factor', 'ypres')],
    'us-maps': [('modern.' + k, 'gettysburg') for k in ('tiles', 'max_zoom', 'credit', 'name', 'about', 'rights', 'link')],
    'world-maps': [('modern.' + k, 'ypres') for k in ('tiles', 'max_zoom', 'credit', 'name', 'about', 'rights', 'link')],
    'civil-war': [('rules.pace.' + k, 'gettysburg') for k in ('infantry', 'cavalry', 'artillery')],
}
WHY_PRESET = {
    'all': 'Every battle.', 'tactical': 'A battlefield, followed by the clock (Gettysburg, Trenton, Manila, Cowpens).',
    'operational': 'A front or a campaign, followed by the day (First Ypres, Luzon 1899).',
    'us-maps': 'Ground in the United States: the USGS topographic map and aerial photography (PRD, 17 Nov 2026).',
    'world-maps': 'Ground outside the United States: OpenTopoMap (PRD, 17 Nov 2026; to revisit before a product).',
    'civil-war': 'March pace of Civil War infantry, cavalry and artillery, from the Gettysburg rows.'}
# Reasons for the rows a battle keeps where it differs from its presets: only what the record says (docs/standing-rules.md).
WHY_OWN = {
    ('cowpens', 'modern.about'): 'Adds that no map of the time shows this ground: Cowpens has no period map.',
    ('cowpens', 'zoom.follow_max'): 'A small field (the fight is about 1 km across): the camera comes closer than on larger battlefields (Morgan, 24 Nov 2026, SR-27).',
    ('manila', 'arrows.min_km'): 'Trial limit for a field of about 12 km (Morgan, 21 Nov 2026); kept as the pattern for small fields (SR-06, 24 Nov).',
    ('luzon1899', 'modern.about'): 'Says "the campaign\'s own names" where a battle says "the battle\'s".',
    ('cowpens', 'bases.3.imagery.about'): 'Says what the aerial photograph shows of this field: the park keeps it open much as in 1781, the woods are thicker.',
    ('cowpens', 'arrows.min_km'): 'The whole field is half a mile long, so the limit is far below a campaign\'s (PR 61); kept as the pattern for small fields (SR-06, 24 Nov).',
}


def base_kind(rows, n):
    """'current', 'satellite' (USGS aerial photography) or None, for base number n of a battle."""
    g = {r['setting'].split('.', 2)[2]: r['value'] for r in rows if r['setting'].startswith('bases.%d.' % n)}
    if parse(g.get('current')) is True: return 'current'
    if 'USGSImageryOnly' in str(g.get('imagery.tiles', '')): return 'satellite'
    return None


def flat_presets(B, pb):
    """{setting: value} of the presets a battle is based on, laid on one another (all first)."""
    out = {}
    for p in ['all'] + BASED_ON[pb]:
        for r in B.presets.get(p, []): out[r['setting']] = r['value']
    return out


def tidy(B, pb):
    """Take off a battle's rows that say what its presets say; turn its standard maps into bases.N.use rows; give the rows that differ
    their reason where the record has one. Returns (rows taken off, rows that differ)."""
    F = flat_presets(B, pb); rows = B.rows[pb]; gone = []; differ = []
    nums = sorted({int(r['setting'].split('.')[1]) for r in rows if r['setting'].startswith('bases.')})
    for n in nums:
        k = base_kind(rows, n)
        if not k or not any(s.startswith('base.%s.' % k) for s in F): continue
        pre = 'bases.%d.' % n
        if not B.get(pb, pre + 'use'): B.set(pb, pre + 'use', k, what='A standard map from the presets (base.%s): its rows below are only where this battle differs' % k, after=pre + 'id')
        for r in list(B.rows[pb]):
            s = r['setting']
            if s.startswith(pre) and s != pre + 'use':
                t = 'base.%s.%s' % (k, s[len(pre):])
                if t in F and parse(F[t]) == parse(r['value']): B.drop(pb, s); gone.append(s)
                elif t in F: differ.append(s)
    for r in list(B.rows[pb]):
        s = r['setting']
        if s in F and not s.startswith('base.'):
            if parse(F[s]) == parse(r['value']): B.drop(pb, s); gone.append(s)
            else:
                differ.append(s)
                if (pb, s) in WHY_OWN and not r.get('why'): r['why'] = WHY_OWN[(pb, s)]
    return gone, differ


def refactor(B):
    assert SHEET not in B.sh.sheetnames, 'already done: Sources and notes.xlsx has a %s sheet' % SHEET
    what = {}
    for pb, rows in B.rows.items():
        for r in rows: what.setdefault(r['setting'], r['what'])
    # every battle: the current map's place on the menu
    B.pset('all', 'base.current.label', 'Current map', 'The standard current map (a battle takes it with bases.N.use = current): its label on the Type of map menu', WHY_PRESET['all'] + ' SR-03.')
    B.pset('all', 'base.current.current', True, 'It is the current map: today\'s topographic map from the modern tile service', 'SR-03 (17 Nov 2026).')
    for p, keys in START.items():
        for s, frm in keys:
            for b in MEMBERS[p]: assert B.get(b, s), '%s: %s does not set %s, so the preset cannot hold it without changing it' % (p, b, s)
            B.pset(p, s, B.get(frm, s)['value'], what.get(s), WHY_PRESET[p])
    # the USGS aerial photography, the same for the three battles in the United States
    sat = [{r['setting'].split('.', 2)[2]: r for r in B.rows[b] if r['setting'].startswith('bases.%d.' % n)}
           for b in MEMBERS['us-maps'] for n in range(1, 12) if base_kind(B.rows[b], n) == 'satellite']
    assert len(sat) == 3
    for k in sat[0]:
        if k == 'clip': continue
        if all(k in g for g in sat):
            vals = [g[k]['value'] for g in sat]; v = max(set(map(str, vals)), key=lambda x: [str(y) for y in vals].count(x)); v = vals[[str(y) for y in vals].index(v)]
            B.pset('us-maps', 'base.satellite.' + k, v, 'The standard aerial photography base (bases.N.use = satellite)' if k == 'id' else None, WHY_PRESET['us-maps'] if k == 'id' else None)
    report = {}
    for pb in BASED_ON:
        B.set(pb, 'based_on', json.dumps(BASED_ON[pb]), what='The presets this battle is based on (Playback presets sheet in Sources and notes.xlsx), laid on in turn after "all"; this battle\'s own rows win over them',
              after='page_title')
        report[pb] = tidy(B, pb)
    return report


def tidy_all(B):
    return {pb: tidy(B, pb) for pb in BASED_ON}


def symbols(B):
    """SR-11: units outside the current event keep 70% strength on every battle (Morgan, 24 Nov 2026)."""
    assert not B.pget('all', 'event_dim'), 'already done'
    B.pset('all', 'event_dim', 0.7, 'How strongly units outside the current event are drawn (0 to 1; the player\'s own default is 0.32)',
           'SR-11: unit symbols stay clearly visible on every battle (Morgan, 24 Nov 2026).')
    return tidy_all(B)


def glide(B):
    """SR-04: the slow ease in from the whole ground, made at Cowpens, for every battle followed by the clock."""
    assert not B.pget('tactical', 'follow.glide_seconds'), 'already done'
    B.pset('tactical', 'follow.glide_seconds', 14, 'When play is first pressed, the camera eases in from the whole ground over this many seconds (the player\'s default is 6)',
           'SR-04: open zoomed out, then ease in slowly, on every battle (Morgan, 24 Nov 2026; values from the Cowpens review, PR 68).')
    B.pset('tactical', 'follow.glide_rate', 0.006, 'How fast the camera eases in after the hold (the player\'s default is 0.03)', 'SR-04, as above.')
    return tidy_all(B)


def ease(B):
    """SR-04 for the battles with no Follow (followed by the day): the same slow ease in from the whole ground. Needs the player's
    opening_ease setting (app/player.js, same commit)."""
    assert not B.pget('operational', 'opening_ease'), 'already done'
    B.pset('operational', 'opening_ease', 0.006, 'Without Follow: how fast the camera eases in from the whole ground when play is first pressed (the player\'s default is 0.03)',
           'SR-04: open zoomed out, then ease in slowly, on every battle (Morgan, 24 Nov 2026), as Follow does on the battlefields.')
    return tidy_all(B)


def routes(B):
    """SR-16: every battle has the routes-taken layer, fading on the battle's time scale (Morgan, 24 Nov 2026)."""
    assert not B.pget('all', 'trails.on'), 'already done'
    B.pset('all', 'trails.on', True, 'Routes taken: the road each unit has marched so far, drawn under the units as the clock runs (Layers: Routes taken)',
           'SR-16: every battle has the routes-taken layer (Morgan, 24 Nov 2026).')
    B.pset('all', 'trails.opacity', 0.55, 'How strongly the routes taken are drawn (0 to 1)', 'SR-16; the Trenton value (19 Nov 2026).')
    B.pset('all', 'trails.fade_seconds', 4, 'Worked out by the exporter: once a unit has stood still for this many seconds of play, its routes fade out over as many again (gives trails.fade_after and trails.fade_over in the battle\'s time unit)',
           'SR-16: routes fade on the battle\'s own time scale (Morgan, 24 Nov 2026).')
    for pb, why in (('trenton', 'Morgan\'s decision when the fade was made, at Trenton (19 Nov 2026).'),
                    ('manila', 'Kept as set while reviewing Manila (Morgan, 24 Nov 2026: Manila and Cowpens keep theirs).'),
                    ('cowpens', 'Kept as set while reviewing Cowpens (Morgan, 24 Nov 2026: Manila and Cowpens keep theirs).')):
        for s in ('trails.fade_after', 'trails.fade_over'): B.get(pb, s)['why'] = why
    B.get('cowpens', 'trails.opacity')['why'] = 'Kept as set while reviewing Cowpens (24 Nov 2026).'
    return tidy_all(B)


def arrows(B):
    """SR-06 and SR-07: arrows on every battle, the shortest move that earns one scaled to the battle, running a few seconds of play ahead."""
    assert not B.pget('all', 'arrows.reach_seconds'), 'already done'
    B.pset('all', 'arrows.on', True, 'Arrows ahead of a long move', 'SR-06: arrows ahead of long moves (Morgan, 21 Nov 2026).')
    B.pset('all', 'arrows.reach_seconds', 6, 'Worked out by the exporter: an arrow runs this many seconds of play ahead of its unit, not to the end of a long road (gives arrows.reach_minutes in the battle\'s time unit)',
           'SR-07: "Arrows will run ahead depending on the time scale being used" (Morgan, 24 Nov 2026). 6 s is the Cowpens value (6 minutes at 1 minute a second).')
    B.pset('tactical', 'arrows.min_share', 0.06, 'Worked out by the exporter: a move shorter than this share of the width of the battle\'s ground gets no arrow (gives arrows.min_km)',
           'SR-06: the limit scales with the battle (Morgan, 24 Nov 2026). 6% is Manila\'s 700 m trial on 12 km of ground.')
    B.pset('operational', 'arrows.min_km', 20, 'Moves shorter than this many km get no arrow', 'SR-06: 20 km stays for campaigns (Morgan, 21 and 24 Nov 2026).')
    for pb in BASED_ON: B.drop(pb, 'arrows.on')
    assert B.get('cowpens', 'arrows.reach_minutes')['value'] == 6; B.drop('cowpens', 'arrows.reach_minutes')   # what reach_seconds gives at 1 minute a second
    return tidy_all(B)


def modern(B):
    """SR-26: the Current map's button reads "Modern" on every battle (Morgan, 24 Nov 2026)."""
    assert not B.pget('all', 'base.current.short'), 'already done'
    B.pset('all', 'base.current.short', 'Modern', 'The short word on the Current map\'s button', 'SR-26: "Modern" on every battle (Morgan, 24 Nov 2026, over "Today" and "Now").')
    for pb in BASED_ON:
        for r in list(B.rows[pb]):
            n = r['setting'].split('.')
            if len(n) == 3 and n[0] == 'bases' and n[2] == 'short' and B.get(pb, 'bases.%s.use' % n[1]) and B.get(pb, 'bases.%s.use' % n[1])['value'] == 'current': B.drop(pb, r['setting'])
    return tidy_all(B)


def note(B):
    """SR-25: no "Times are estimates" note under the clock on any map (Morgan, 24 Nov 2026)."""
    n = sum(B.drop(pb, s) for pb in ('trenton', 'cowpens') for s in ('time_note.from', 'time_note.text'))
    assert n == 4, 'already done'
    return tidy_all(B)


MAIN = {   # SR-15: the one main map of each battle that had more than one on the menu; the others are offered from the map details
    'trenton': ('fd', {'sk': 'Lt. Wiederhold\'s sketch of the fight in the town (1776), drawn by a Hessian officer who was there; not to scale.'}),
    'ypres': ('day', {'m14': 'Sketch A of the British official history (1925): the whole Ypres front on one sheet.'}),
    'luzon1899': ('c99', {'n00': 'Howard\'s map of northern Luzon for General Young (1900): the autumn campaign in the north.',
                          'wd99': 'The War Department\'s map of the theatre of operations in Luzon (1899, second edition).'}),
}


def menu(B):
    """SR-15: one main map on the Type of map menu for every battle (Morgan, 24 Nov 2026); the others from the map details."""
    for pb, (main, others) in MAIN.items():
        for bid, txt in others.items():
            n = next(r['setting'].split('.')[1] for r in B.rows[pb] if r['setting'].endswith('.id') and r['setting'].startswith('bases.') and r['value'] == bid)
            assert not B.get(pb, 'bases.%s.hidden' % n), 'already done'
            B.set(pb, 'bases.%s.hidden' % n, True, why='SR-15: one main map on the Type of map menu (Morgan, 24 Nov 2026); the main map here is %s.' % main,
                  what='Kept off the Type of map menu: the map details offer it, with the note', after='bases.%s.id' % n)
            B.set(pb, 'bases.%s.note' % n, txt, after='bases.%s.hidden' % n)
    return tidy_all(B)


def align(B):
    """SR-27: the battlefields share deepest zoom, Follow's deepest zoom, blend and the meaning of a question mark, and each has the division
    view where it has divisions (Morgan, 24 Nov 2026: 8, 2.2, 4 minutes, overall; Cowpens keeps Follow 2.4)."""
    assert not B.pget('tactical', 'rules.blend'), 'already done'
    B.pset('tactical', 'rules.blend', 4, 'Minutes over which a unit shifts from one row to the next when they meet', 'SR-27: the battlefields share their settings (Morgan, 24 Nov 2026).')
    for r in B.presets['tactical']:
        if r['setting'] in ('zoom.max', 'zoom.follow_max', 'question_mark'): r['why'] = 'SR-27: the battlefields share their settings (Morgan, 24 Nov 2026).'
    for pb, s in (('gettysburg', 'zoom.max'), ('gettysburg', 'zoom.follow_max'), ('gettysburg', 'question_mark'), ('manila', 'zoom.max'), ('manila', 'zoom.follow_max'), ('trenton', 'rules.blend')):
        assert B.drop(pb, s) == 1, (pb, s)
    a = B.get('gettysburg', 'about.2'); old = 'A question mark means the location is a loose estimate.'
    assert old in a['value']; a['value'] = a['value'].replace(old, 'A question mark means low confidence.')
    for s, v, what in (('formations.echelon', 'division', None), ('formations.below', 0.11, 'Zoomed out below this (screen pixels per metre), the brigades of each division are drawn as the division'),
                       ('formations.label', 'Divisions', None), ('formations.on', False, None)):
        B.set('manila', s, v, what=what, why='SR-27: each battlefield has the division view where it has divisions (Anderson\'s and MacArthur\'s); 0.11 is Gettysburg\'s 0.155 for ground half as wide again.' if s == 'formations.below' else None)
    return tidy_all(B)


def main(argv):
    step = argv[0] if argv else ''
    assert step in STEPS, 'which step? one of: ' + ', '.join(STEPS)
    B = Book(); report = STEPS[step][0](B)
    title, war, shared = STEPS[step][1:]
    B.save([title, war], [shared[0], shared[1] + ' Written by pipeline/presets_2026_11_24.py %s.' % step])
    for pb, (gone, differ) in (report or {}).items():
        print('%s: %d rows now come from presets; %d differ from them: %s' % (pb, len(gone), len(differ), ', '.join(differ) or 'none'))


STEPS = {
    'refactor': (refactor, 'Playback presets (24 Nov 2026)',
                 'Rows that say the same as the battle\'s presets are taken off Playback settings; based_on names the presets; the new why column gives the reason where a battle differs. See the Playback presets sheet in Sources and notes.xlsx.',
                 ('What changed on 24 November 2026 (night): playback presets',
                  'New sheet Playback presets: the settings battles share (all, tactical, operational, us-maps, world-maps, civil-war). Each war\'s Playback settings has a based_on row per battle and a why column, and no longer repeats what its presets say. Every battle file is unchanged.')),
    'symbols': (symbols, 'Presets: 70% symbol strength (24 Nov 2026)', 'event_dim 0.7 now comes from the preset "all" (SR-11).',
                ('What changed on 24 November 2026 (night): symbols stay clearly visible', 'Playback presets, all: event_dim 0.7. Gettysburg, Trenton, First Ypres, Manila and Luzon 1899 change; Cowpens had it already.')),
    'glide': (glide, 'Presets: the slow ease in (24 Nov 2026)', 'follow.glide_seconds 14 and follow.glide_rate 0.006 now come from the preset "tactical" (SR-04).',
              ('What changed on 24 November 2026 (night): the slow ease in', 'Playback presets, tactical: follow.glide_seconds 14, follow.glide_rate 0.006 (from Cowpens). Gettysburg, Trenton and Manila change.')),
    'ease': (ease, 'Presets: the slow ease in without Follow (24 Nov 2026)', 'opening_ease 0.006 comes from the preset "operational" (SR-04).',
             ('What changed on 24 November 2026 (night): the slow ease in without Follow', 'Playback presets, operational: opening_ease 0.006 (new setting). First Ypres and Luzon 1899 change.')),
    'routes': (routes, 'Presets: routes taken on every battle (24 Nov 2026)', 'trails.on, trails.opacity and trails.fade_seconds come from the preset "all" (SR-16).',
               ('What changed on 24 November 2026 (night): routes taken on every battle', 'Playback presets, all: trails on, opacity 0.55, fading after 4 seconds of play. Gettysburg, First Ypres and Luzon 1899 change; Trenton, Manila and Cowpens keep their fade times.')),
    'arrows': (arrows, 'Presets: arrows scaled to the battle (24 Nov 2026)', 'arrows.on, arrows.reach_seconds (all), arrows.min_share (tactical) and arrows.min_km 20 (operational) come from the presets (SR-06, SR-07).',
               ('What changed on 24 November 2026 (night): arrows scaled to the battle', 'Playback presets: arrows on everywhere; the shortest move with an arrow is 6% of the battle\'s width on a battlefield, 20 km on a campaign; an arrow runs 6 seconds of play ahead. Manila and Cowpens keep their limits.')),
    'modern': (modern, 'Presets: the "Modern" button (24 Nov 2026)', 'The Current map\'s short word comes from the preset "all" (SR-26).',
               ('What changed on 24 November 2026 (night): the "Modern" button', 'Playback presets, all: base.current.short "Modern". All six battles change.')),
    'note': (note, 'No "Times are estimates" note (24 Nov 2026)', 'Trenton and Cowpens: time_note rows removed (SR-25).',
             ('What changed on 24 November 2026 (night): no note under the clock', 'Trenton and Cowpens no longer show "Times are estimates" under the clock (SR-25).')),
    'menu': (menu, 'One main map on the menu (24 Nov 2026)', 'Trenton, First Ypres and Luzon 1899: the other period maps are hidden from the Type of map menu and offered from the map details (SR-15).',
             ('What changed on 24 November 2026 (night): one main map on the menu', 'Trenton (main: Faden 1777), First Ypres (main: the sketch of the day) and Luzon 1899 (main: Siebert 1899) keep one period map on the Type of map menu (SR-15).')),
    'align': (align, 'Battlefields aligned (24 Nov 2026)', 'Gettysburg, Trenton and Manila take the tactical preset\'s zoom, blend and question mark; Manila gets the division view (SR-27).',
              ('What changed on 24 November 2026 (night): battlefields aligned', 'Playback presets, tactical: rules.blend 4. Gettysburg deepest zoom 8, Follow 2.2, question mark = overall; Manila deepest zoom 8, Follow 2.2, division view; Trenton blend 4 (SR-27).')),
}

if __name__ == '__main__':
    main(sys.argv[1:])
