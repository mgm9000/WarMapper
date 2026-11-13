"""Build data.json for the First Ypres playback from the pilot data module and the OpenStreetMap extract."""
import sys, os, json, math, datetime as dt
S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
sys.path.insert(0, S + 'pipeline')
import ypres_data as YP
LAT0, LON0 = 50.8522, 2.8846
KX = 111320 * math.cos(math.radians(LAT0)); KY = 111040
def M(la, lo): return [round((lo - LON0) * KX), round(-(la - LAT0) * KY)]
D0 = dt.date(1914, 10, 18)
def day(s): return (dt.date.fromisoformat(s) - D0).days
def nice(s):
    d = dt.date.fromisoformat(s); return f'{d.day} {"October" if d.month == 10 else "November"}'
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
        t0 = day(sl if sl != 'unknown' else se); t1 = day(ee)
        ts = nice(se) if se == sl else f'{nice(se)} to {nice(sl)}'
        te = nice(ee) if ee == el else (f'{nice(ee)} or later; not followed after this' if el == 'unknown' else f'{nice(ee)} to {nice(el)}')
        k = dict(id=p['pos_id'], t0=t0, t1=t1, open=1 if el == 'unknown' else 0, ts=ts, te=te, g=[M(x[2], x[3]) for x in g] or None, act=p['activity'], place=p['place'],
                 src=p['source_ids'], say=p['say'], method=p['method'], oc=p['oc'], notes=p['notes'], bat=p['battle_id'],
                 pl=[[x[0], x[1], x[4], x[5]] for x in g])
        if p.get('pbasis'): k['basis'] = p['pbasis']
        if g:
            k['cs'] = max((x[4] for x in g), key=lambda v: CS[v]); k['prec'] = max(x[5] for x in g)
            mid = g[len(g) // 2]; k['lat'] = mid[2]; k['lon'] = mid[3]
        ks.append(k)
    par = [[day(a[4]), day(a[5]), a[1], a[2], a[3]] for a in YP.A if a[0] == uid]
    tracks.append(dict(id=uid, name=name, label=label, side='AL' if side == YP.SIDE_A else 'GE', nation=nation, ech=ech.lower(), branch={'Infantry': 'inf', 'Cavalry': 'cav'}[branch], par=par, notes=notes, k=ks))
UN = {u[0]: u[1] for u in YP.U}
# base map
ways, woods = [], []
def dec(s):
    out = []; a = b = 0
    for i, t in enumerate(s.split(';')):
        x, y = t.split(','); x, y = int(x), int(y)
        if i == 0: a, b = x, y
        else: a, b = a + x, b + y
        out.append(M(50 + a / 1e4, 2 + b / 1e4))
    return out
def path(pts, close=False): return 'M' + 'L'.join(f'{p[0]} {p[1]}' for p in pts) + ('Z' if close else '')
for l in open(S + 'data/osm/ypres.txt', encoding='utf-8').read().split('\n'):
    if not l or l[0] == 'p': continue
    k, name, body = l.split('|')
    if k in 'wmrs': ways.append([k, name, path(dec(body))])
    elif k == 'f': woods.append(['Ploegsteert Wood', path(dec(body), True)])
    elif k == 'b':
        a, b, c, d = [int(v) for v in body.split(',')]; p1 = M(50 + a / 1e4, 2 + b / 1e4); p2 = M(50 + c / 1e4, 2 + d / 1e4)
        cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2; rx, ry = abs(p2[0] - p1[0]) / 2, abs(p2[1] - p1[1]) / 2
        if name == 'Vrijbos': rx *= 1.9; ry *= 1.5   # the forest of 1914 was much larger than today's remnant
        pts = [[round(cx + rx * math.cos(t / 12 * math.pi)), round(cy + ry * math.sin(t / 12 * math.pi))] for t in range(24)]
        woods.append([{'Vrijbos': 'Houthulst Forest', 'Polygoonbos': 'Polygon Wood', 'Nonnebossen': 'Nonne Bosschen'}[name], path(pts, True)])
# the old Ypres-Comines canal is not a waterway in OpenStreetMap between Ypres and Houthem: drawn from memory, dashed
ways.append(['x', 'Former Ypres-Comines canal (approximate)', path([M(50.8367, 2.8793), M(50.8139, 2.9167), M(50.811, 2.925), M(50.803, 2.937), M(50.7867, 2.9663)])])
used = {k for p in list(YP.P) + list(YP.ORIG.values()) for k in p['keys']}
BIG = {'IEPE', 'DIKS', 'NIEU', 'ROES', 'MENE', 'POPE', 'MESS', 'LANG', 'ZONN', 'PASS', 'GHEL', 'COMI', 'HOUL', 'TORH', 'STAD', 'WERV', 'BAIL', 'WYTS', 'PERV', 'BIKS', 'WARN'}
SKIP = {'PWE', 'PWSE', 'PWS', 'PWSW', 'CANB', 'BLUF', 'GXR', 'HERE', 'HERC', 'SHRE', 'DOUV', 'PSTN', 'KNOK', 'NONB', 'HOUF'}
labels = []
for k, v in YP.PL.items():
    if v[4] == 'derived' or k in SKIP or not v[1] or (k not in used and k not in BIG and k not in ('HOOGE', 'ZILL', 'H60')): continue
    old = v[0].split(' (')[0]; new = v[1]
    if k in ('SHRE', 'HERC', 'HERE', 'GXR'): continue
    labels.append(dict(t=new, o=old if old.lower() != new.lower() else '', p=M(v[2], v[3]), l=0 if k in BIG else 1, e=1 if v[4] == 'estimate' else 0))
for nm, la, lo in (('Polygon Wood', 50.8532, 2.9868), ('Nonne Bosschen', 50.8497, 2.9699), ('Houthulst Forest', 50.9614, 2.9592), ('Ploegsteert Wood', 50.737, 2.897)):
    labels.append(dict(t=nm, o='', p=M(la, lo), l=2, e=0))
events = [dict(id=e[0], t0=day(YP.D(e[1])), t1=day(YP.D(e[2])), name=e[3], text=e[4]) for e in YP.EVENTS]
sources = {s[0]: dict(title=s[1], url=s[7]) for s in YP.SOURCES}
sources['S39'] = dict(title='OpenStreetMap (place coordinates and base map)', url='https://www.openstreetmap.org/copyright')
hist = json.load(open(S + 'playbacks/ypres/hist.json'))
out = dict(hist=hist, tracks=tracks, ways=ways, woods=woods, labels=labels, events=events, sources=sources, un=UN, ext=[M(51.17, 2.68), M(50.70, 3.21)], days=35)
json.dump(out, open(S + 'playbacks/ypres/data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(tracks), 'tracks', sum(len(t['k']) for t in tracks), 'rows', len(ways), 'ways', len(labels), 'labels', len(json.dumps(out)) // 1024, 'KB', out['ext'])
