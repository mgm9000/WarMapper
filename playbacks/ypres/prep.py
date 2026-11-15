"""First Ypres, October and November 1914: write this battle's battle file (battle.json).

The record comes from the pilot data module (pipeline/ypres_data.py, which is also what the workbook's Flanders rows are made from),
the OpenStreetMap extract, and the fits of the official history's sketches (hist.json). What is set here is only what the playback
adds: when each row is shown, and which place names are worth a label.
"""
import sys, os, json, math, datetime as dt
S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
sys.path.insert(0, S + 'pipeline')
import ypres_data as YP
import battlefile as bf
HERE = S + 'playbacks/ypres/'
LAT0, LON0 = 50.8522, 2.8846
KX = 111320 * math.cos(math.radians(LAT0)); KY = 111040
def M(la, lo): return bf.ll(la, lo)
def LL(x, y):
    """a point in metres east and south of the centre of Ypres (how the sketches were fitted) -> [longitude, latitude]"""
    return bf.ll(LAT0 - y / KY, LON0 + x / KX)
D0 = dt.date(1914, 10, 18)
def day(s): return (dt.date.fromisoformat(s) - D0).days
CS = {'modern_map': 0, 'map_read': 0, 'derived': 1, 'estimate': 2}
tracks = []
for u in YP.U:
    uid, name, label, side, nation, branch, ech, srcs, notes = u
    rows = [p for p in YP.P if p['unit_id'] == uid]
    if not rows: continue
    ks = []
    for p in rows:
        g = YP.geom(p)
        se, sl, ee, el = p['se'], p['sl'], p['ee'], p['el']
        # shown from the latest start the record gives to its earliest end (a record whose latest end is unknown is one the sources stop following)
        k = dict(id=p['pos_id'], start=[bf.iso(se), bf.iso(sl)], end=[bf.iso(ee), bf.iso(el)], show=[sl if sl != 'unknown' else se, ee],
                 at=[M(x[2], x[3]) for x in g] or None, activity=p['activity'], place=p['place'], quote=p['say'], method=p['method'], confidence=p['oc'],
                 time_basis=p['time_basis'], sources=bf.ids(p['source_ids']), notes=p['notes'], battle=p['battle_id'])
        if g:   # each place the line runs through: its 1914 name, its name today, how it was placed and how closely
            k['location'] = dict(source=max((x[4] for x in g), key=lambda v: CS[v]), basis=p.get('pbasis'), precision_m=max(x[5] for x in g),
                                 places=[dict(name=x[0], today=x[1], source=x[4], precision_m=x[5]) for x in g])
        ks.append(k)
    tracks.append(dict(id=uid, unit=uid, steps=ks))
units = []
for u in YP.U:
    uid, name, label, side, nation, branch, ech, srcs, notes = u
    units.append(dict(id=uid, name=name, label=label, side=side, nation=nation, branch=branch.lower(), echelon=ech.lower(), sources=bf.ids(srcs), notes=notes,
                      assignments=[dict(parent=a[1], commander=a[2], strength=a[3], sources=bf.ids(a[6]), notes=a[7], **{'from': a[4], 'to': a[5]}) for a in YP.A if a[0] == uid]))
# base map
lines, areas = [], []
def dec(s):
    out = []; a = b = 0
    for i, t in enumerate(s.split(';')):
        x, y = t.split(','); x, y = int(x), int(y)
        if i == 0: a, b = x, y
        else: a, b = a + x, b + y
        out.append(M(50 + a / 1e4, 2 + b / 1e4))
    return out
KIND = {'w': ('water', 'canal'), 'm': ('road', 'm'), 'r': ('road', 'r'), 's': ('road', 's')}
for l in open(S + 'data/osm/ypres.txt', encoding='utf-8').read().split('\n'):
    if not l or l[0] == 'p': continue
    k, name, body = l.split('|')
    if k in 'wmrs': lines.append([KIND[k][0], ('river' if name in ('IJzer', 'Lys') else 'canal') if k == 'w' else KIND[k][1], name, bf.pack(dec(body))])
    elif k == 'f': areas.append(['wood', 'Ploegsteert Wood', bf.pack(dec(body))])
    elif k == 'b':
        a, b, c, d = [int(v) for v in body.split(',')]; XY = lambda la, lo: [(lo - LON0) * KX, -(la - LAT0) * KY]; p1 = XY(50 + a / 1e4, 2 + b / 1e4); p2 = XY(50 + c / 1e4, 2 + d / 1e4)
        cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2; rx, ry = abs(p2[0] - p1[0]) / 2, abs(p2[1] - p1[1]) / 2
        if name == 'Vrijbos': rx *= 1.9; ry *= 1.5   # the forest of 1914 was much larger than today's remnant
        pts = [LL(cx + rx * math.cos(t / 12 * math.pi), cy + ry * math.sin(t / 12 * math.pi)) for t in range(24)]   # an oval over the wood's extent
        areas.append(['wood', {'Vrijbos': 'Houthulst Forest', 'Polygoonbos': 'Polygon Wood', 'Nonnebossen': 'Nonne Bosschen'}[name], bf.pack(pts)])
# the old Ypres-Comines canal is not a waterway in OpenStreetMap between Ypres and Houthem: drawn from memory, dashed
lines.append(['former-water', 'canal', 'Former Ypres-Comines canal (approximate)', bf.pack([M(50.8367, 2.8793), M(50.8139, 2.9167), M(50.811, 2.925), M(50.803, 2.937), M(50.7867, 2.9663)])])
used = {k for p in list(YP.P) + list(YP.ORIG.values()) for k in p['keys']}
BIG = {'IEPE', 'DIKS', 'NIEU', 'ROES', 'MENE', 'POPE', 'MESS', 'LANG', 'ZONN', 'PASS', 'GHEL', 'COMI', 'HOUL', 'TORH', 'STAD', 'WERV', 'BAIL', 'WYTS', 'PERV', 'BIKS', 'WARN'}
SKIP = {'PWE', 'PWSE', 'PWS', 'PWSW', 'CANB', 'BLUF', 'GXR', 'HERE', 'HERC', 'SHRE', 'DOUV', 'PSTN', 'KNOK', 'NONB', 'HOUF'}
labels = []
for k, v in YP.PL.items():
    if v[4] == 'derived' or k in SKIP or not v[1] or (k not in used and k not in BIG and k not in ('HOOGE', 'ZILL', 'H60')): continue
    old = v[0].split(' (')[0]; new = v[1]
    if k in ('SHRE', 'HERC', 'HERE', 'GXR'): continue
    labels.append(dict(text=new, alt=old if old.lower() != new.lower() else '', at=M(v[2], v[3]), level=0 if k in BIG else 1, kind='place', approximate=(v[4] == 'estimate') or None))
for nm, la, lo in (('Polygon Wood', 50.8532, 2.9868), ('Nonne Bosschen', 50.8497, 2.9699), ('Houthulst Forest', 50.9614, 2.9592), ('Ploegsteert Wood', 50.737, 2.897)):
    labels.append(dict(text=nm, at=M(la, lo), level=2, kind='wood'))
LOUD = {'YE01', 'YE04', 'YE09', 'YE11', 'YE13', 'YE14'}   # the events named on the timeline; the rest are marked with a dot
steps_used = {k['id'] for t in tracks for k in t['steps']}
events = [dict(id=e[0], start=YP.D(e[1]), end=YP.D(e[2]), at=YP.D(e[1]), name=e[3], text=e[4], quiet=(e[0] not in LOUD) or None, battle=e[5], sources=bf.ids(e[6]),
               steps=[x for x in bf.ids(e[7] if len(e) > 7 else '') if x in steps_used]) for e in YP.EVENTS]
catalogue = {s_[0]: dict(title=s_[1], citation=s_[5], type=s_[4], url=s_[7]) for s_ in YP.SOURCES}
catalogue['S39'] = dict(title='OpenStreetMap (place coordinates and base map)', url='https://www.openstreetmap.org/copyright')

# ---- the official history's maps: Sketch A for the whole battle, and the sketch for each run of days. Each was fitted as a
#      north-up picture (hist.json: its top-left corner and metres per pixel, in metres east and south of the centre of Ypres) ----
hist = json.load(open(HERE + 'hist.json'))
def placed(h): return [LL(h['x0'], h['y0']), LL(h['x0'] + h['w'] * h['res'], h['y0']), LL(h['x0'] + h['w'] * h['res'], h['y0'] + h['h'] * h['res']), LL(h['x0'], h['y0'] + h['h'] * h['res'])]
def date(n): return (D0 + dt.timedelta(days=n)).isoformat()
maps = [dict(id='official-history-sketch-a', title='Sketch A, British official history (1925)', credit='Sketch A, official history (1925)', source='S40',
             images=[dict(file=hist['A']['src'], corners=placed(hist['A']))])]
for h in hist['days']:
    maps.append(dict(id='official-history-' + h['sk'].lower().replace(' ', '-'), title=h['sk'] + ', British official history (1925)', short=h['sk'], label=h['label'], credit='official history (1925)', source='S40',
                     fit=dict(points=h.get('n'), misfit_m=h.get('rms')), images=[dict(file=h['src'], corners=placed(h))], **{'from': date(h['d0']), 'to': date(h['d1'])}))
def box(x0, y0, x1, y1):
    a, b = LL(x0, y1), LL(x1, y0); return [a[0], a[1], b[0], b[1]]
battle = dict(id='ypres-1914', title='First Ypres', subtitle='October and November 1914',
    record=dict(workbook='Military Map Explorer data pilot v7', campaign='WW1-FL14', battles=['YPRES1', 'YP-LANG', 'YP-GHEL', 'YP-NONNE', 'MESS14', 'YSER']),
    # time runs in days; a whole day is nightfall on that date. The battle's start and end dates are not agreed, so its days are not numbered
    time=dict(unit='day', zero=D0.isoformat(), start=D0.isoformat(), end=date(35), calendar=dict(first=D0.isoformat(), numbered=False)),
    view=dict(origin=bf.ll(LAT0, LON0), extent=[2.68, 50.70, 3.21, 51.17], presets=dict(salient=box(-6600, -10600, 15800, 13800), front=box(-13200, -34500, 21500, 15800)),
              points=dict(allied_rear=LL(-12000, 1500))),   # roughly Poperinghe: Allied symbols sit on this side of their line
    opening=dict(label='Before the battle', text="The Allies are pushing east from Ypres and along the Lys, expecting only cavalry in front of them. Four new German reserve corps are a day's march away."),
    sides=[dict(id='WW1-ALL', code='AL', name='Allies (British, French and Belgian)', short='Allied', colour='blue'), dict(id='WW1-GER', code='GE', name='Germany', short='German', colour='red')],
    units=units, tracks=tracks, events=events, labels=labels, maps=maps,
    base=dict(credit='\u00a9 OpenStreetMap contributors', source='S39', lines=lines, areas=areas))
battle['sources'] = bf.used_sources(battle, catalogue, ['S39'])
bf.write(battle, HERE + 'battle.json')
