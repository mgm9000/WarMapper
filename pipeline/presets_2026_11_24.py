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
}

if __name__ == '__main__':
    main(sys.argv[1:])
