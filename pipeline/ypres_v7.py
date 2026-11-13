# ======================================================================
# v7: Allied unit lines read from the dated sketches of the British official history (S40),
# and German lines kept on the German side of them.  Executed at the end of ypres_data.py.
# Coordinates below are km east (x) and km south (y) of Ypres, read off km-grid crops of the rectified sketches.
# ======================================================================
import math as _m, copy as _copy, datetime as _dt
LAT0, LON0 = 50.8522, 2.8846
_KX = 111.320 * _m.cos(_m.radians(LAT0)); _KY = 111.040
def km2ll(x, y): return (round(LAT0 - y / _KY, 5), round(LON0 + x / _KX, 5))
def ll2km(la, lo): return ((lo - LON0) * _KX, -(la - LAT0) * _KY)
SK = {'A': (4, '10-21', '21 October'), 'B': (7, '10-23', '23 October'), 'C': (8, '10-25', '25 October'), 'E': (9, '10-29', '29 October'),
      'F': (10, '10-31', '31 October'), 'G': (12, '11-04', '4 November'), 'H': (13, '11-09', '9 November'), 'I': (14, '11-11', 'the afternoon of 11 November')}
MAPPREC = 250

def geom(p):
    """Geometry of a row as Places-style tuples: (name 1914, name today, lat, lon, coord_source, precision_m, basis)."""
    if p.get('pts'): return [(x[4], '', x[0], x[1], x[2], x[3], '') for x in p['pts']]
    return [PL[k] for k in p['keys']]
def line(p): return [(x[2], x[3]) for x in geom(p)]

# ---------- units ----------
_i = [u[0] for u in U].index('Y-FR-MOUS') + 1
U[_i:_i] = [
 ('Y-FR-HELY', "Hély d'Oissel's group", "Hély d'Oissel (Fr)", SIDE_A, 'France', 'Cavalry', 'Division', 'S40', "Named on Sketches 9 and 12 to 14 of the official history, between de Mitry and the IX Corps. What it was made of is not in the sources read. Drawn as a division."),
 ('Y-FR-OLL', 'French detachments between the canal and St. Eloi (Woillemont, then Olleris)', 'Woillemont / Olleris (Fr)', SIDE_A, 'France', 'Infantry', 'Brigade', 'S40', 'Two names on the sketches for the same stretch: Woillemont on 31 October, Olleris on 4 November. Size not given. Drawn as a brigade.'),
]
for _n, _u in enumerate(U):
    if _u[0] == 'Y-FR-9C': U[_n] = _u[:7] + ('S40; S44; S47', 'Position rows from 29 October, when the sketches show the corps sector without naming its divisions.')
    if _u[0] == 'Y-FR-16C': U[_n] = _u[:7] + ('S40; S41; S44', 'Position rows from 4 November for the part of the corps line south of the 32nd Division.')
A += [
 ('Y-FR-HELY', 'Y-FR-8A', "Gen. Hély d'Oissel", '', D('10-29'), D('11-22'), 'S40', 'Name from the sketch labels. Parent not given in the sources read; put under the army.'),
 ('Y-FR-OLL', 'Y-FR-16C', '', '', D('10-31'), D('11-08'), 'S40', 'Parent inferred from the sector.'),
]

# ---------- helpers ----------
ORIG = {p['pos_id']: _copy.deepcopy(p) for p in P}
V7 = {}        # pos_id -> text for the "changed in v7" column
RETIRED = {}   # pos_id -> (unit, dates, why)
_ctr = [len(P)]
def _nid():
    _ctr[0] += 1; return f'Y{_ctr[0]:03d}'
def _row(unit, start):
    r = [p for p in P if p['unit_id'] == unit and D(start) in (p['se'], p['sl'])]
    assert len(r) == 1, (unit, start, [x['pos_id'] for x in r]); return r[0]
_REF = [(v[0].split(' (')[0], ll2km(v[2], v[3])) for k, v in PL.items() if v[1] and v[4] in ('modern_map', 'map_read') and k not in ('GXR', 'HERE', 'HERC', 'SHRE', 'H60')]
_DIR = ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west']
def _near(x, y):
    nm, (px, py) = min(_REF, key=lambda r: _m.hypot(r[1][0] - x, r[1][1] - y)); d = _m.hypot(px - x, py - y)
    if d < 0.35: return nm
    b = _m.degrees(_m.atan2(x - px, -(y - py))) % 360
    return f'{d:.1f} km {_DIR[int((b + 22.5) // 45) % 8]} of {nm}'
def describe(pts):
    if len(pts) == 1: return _near(*pts[0])
    s = 'from ' + _near(*pts[0]) + ' to ' + _near(*pts[-1])
    if len(pts) >= 5: s += ', by ' + _near(*pts[len(pts) // 2])
    return s
def _apply(p, sk, pts, label, extra='', oc='medium', method=None, rear=False, keep=True):
    n, _, dtxt = SK[sk]; old_place = p['place']; had = bool(p['keys'])
    p['pts'] = [km2ll(x, y) + ('map_read', MAPPREC, '') for x, y in pts]; p['keys'] = []; p['sk'] = sk; p['rear'] = rear
    p['place'] = f'As drawn on Sketch {n}: ' + describe(pts)
    if 'S40' not in p['source_ids']: p['source_ids'] = (p['source_ids'] + '; ' if p['source_ids'] else '') + 'S40'
    p['say'] = (p['say'] + ' ' if keep and p['say'] else '') + f'Sketch {n} (S40) draws {label} here for {dtxt}.'
    p['method'] = method or st; p['oc'] = oc
    p['time_basis'] = f'Dates only. The line is the one the official history draws for {dtxt}; the row keeps it until the next dated sketch or the next change in the text.'
    what = f'A line of {len(pts)} points' if len(pts) > 1 else 'A point'
    p['cbasis'] = what + f' read from Sketch {n} of the British official history (S40), which was tied to village centres on the current map (typical misfit about 150 m; reading adds about 100 m).'
    p['pbasis'] = what + f' read from Sketch {n} of the British official history, drawn for {dtxt}. Good to about {MAPPREC} m.'
    p['notes'] = ' '.join(x.strip() for x in (extra, p['notes'], (f'Place in the text sources, as used before v7: {old_place}.' if had and keep else '')) if x)
    return p
def _nice(d): return f'{int(d[3:])} {"October" if d[:2] == "10" else "November"}'
def split(unit, start, parts, label, **kw):
    """parts: (d0, d1, sketch, points[, extra note]). The first part re-uses the old row; the rest are new rows with the same text.
    A first part with no sketch keeps the old row and its text-based line and only shortens it."""
    p = _row(unit, start); o = ORIG[p['pos_id']]; out = []
    for i, part in enumerate(parts):
        d0, d1, sk, pts = part[:4]; extra = part[4] if len(part) > 4 else ''
        if i == 0: q = p
        else:
            q = _copy.deepcopy(o); q['pos_id'] = _nid(); P.append(q)
        if sk: _apply(q, sk, pts, label, extra=extra, **kw)
        if i > 0: q['se'] = q['sl'] = D(d0)
        if i < len(parts) - 1: q['ee'] = q['el'] = D(d1)
        n = SK[sk][0] if sk else 0
        if i == 0 and not sk:
            V7[q['pos_id']] = f'Row now ends on {_nice(d1)}; from the next day the line is read from a sketch. Line unchanged.'
            q['notes'] = (q['notes'] + ' ' if q['notes'] else '') + f'v7: this row now covers only the day{"s" if q["se"] != q["ee"] else ""} before the next dated sketch; its line is still from the text.'
        elif i == 0: V7[q['pos_id']] = f'Line re-read from Sketch {n}.' + (f' Row now ends on {_nice(d1)}; the rest of its time is in new rows.' if len(parts) > 1 else '')
        else: V7[q['pos_id']] = f'New in v7: part of the time of row {o["pos_id"]}, with the line from Sketch {n}.'
        out.append(q)
    return out
def new(unit, d0, d1, sk, pts, label, act, battle='YPRES1', notes='', el=None, **kw):
    q = dict(pos_id=_nid(), unit_id=unit, battle_id=battle, se=D(d0), sl=D(d0), ee=D(d1), el=el or D(d1), time_basis='', activity=act, place='', keys=[], source_ids='S40', say='', method=st, oc='medium', notes=notes)
    P.append(q); _apply(q, sk, pts, label, keep=False, **kw); V7[q['pos_id']] = f'New in v7, from Sketch {SK[sk][0]}.'
    return q
def retire(unit, start, why):
    p = _row(unit, start); RETIRED[p['pos_id']] = (unit, p['se'], p['ee'], p['activity'], why); P.remove(p)
SAME = 'The line is the same, within reading error, on Sketches {} ({}); one row covers them.'
END = 'No sketch after 11 November was read: the line is kept to the end of the battle for want of anything later.'

# ---------- British ----------
split('Y-BR-7D', '10-21', [(None, '10-22', 'A', [(7.6, -2.1), (8.1, -0.9), (8.6, 0.25), (9.0, 1.5), (9.3, 2.8), (9.7, 4.2), (7.0, 4.7)]),
                           ('10-23', '10-24', 'B', [(6.5, -2.0), (7.5, -1.4), (8.0, -0.7), (8.5, 0.3), (9.0, 1.5), (9.6, 3.0), (9.9, 4.3), (7.8, 4.6)])], 'the 7th Division')
split('Y-BR-7D', '10-25', [(None, None, 'C', [(8.5, 0.3), (8.8, 1.0), (9.0, 1.5), (9.6, 3.0), (9.9, 4.3), (7.9, 4.7)], 'The north end is put at Reutel, where the label of the 2nd Division ends; the sketch does not mark the boundary.')], 'the 7th Division')
split('Y-BR-7D', '10-29', [(None, None, 'E', [(8.58, 2.4), (8.43, 2.8), (8.48, 3.25), (8.68, 3.7), (8.68, 3.95), (8.38, 4.15), (7.88, 4.35), (7.33, 4.55)])], 'the 7th Division')
split('Y-BR-7D', '10-31', [(None, '11-03', 'F', [(6.7, 1.95), (6.4, 2.7), (6.15, 3.1)]), ('11-04', '11-04', 'G', [(6.6, 2.25), (6.15, 3.2)])], 'the 7th Division')

split('Y-BR-1D', '10-21', [(None, '10-22', 'A', [(-3.0, -7.7), (-0.3, -7.7), (1.5, -7.8), (2.55, -8.4)]), ('10-23', '10-23', 'B', [(-2.9, -7.6), (-1.0, -7.65), (0.2, -7.35), (2.3, -7.8), (2.8, -7.6)])], 'the 1st Division')
_p = _row('Y-BR-1D', '10-24')
_apply(_p, 'C', [(1.6, 0.8)], 'the 1st Division as an oval behind the front, in reserve,', extra='Sketch 8 still has the division in reserve on 25 October; S42 has it in line that day. See YC11.')
_p['ee'] = D('10-25'); _p['el'] = D('10-26'); V7[_p['pos_id']] = 'Point read from Sketch 8; end widened to 25-26 October (YC11).'
_p = _row('Y-BR-1D', '10-25'); _p['sl'] = D('10-27')
_p['notes'] += ' v7: the start is now a range, 25 to 27 October, because Sketch 8 still shows the division in reserve on the 25th (YC11). The line itself is still from the text.'
V7[_p['pos_id']] = 'Start widened to 25-27 October (YC11). Line unchanged.'
split('Y-BR-1D', '10-29', [(None, None, 'E', [(8.63, 1.1), (8.78, 1.35), (8.88, 1.7), (8.78, 2.05), (8.58, 2.4)], 'The north end is put at a break in the drawn line; the sketch does not mark the boundary with the 2nd Division.')], 'the 1st Division')
split('Y-BR-1D', '10-31', [(None, '11-03', 'F', [(7.0, 0.6), (6.85, 1.5), (6.7, 1.95)]), ('11-04', '11-08', 'G', [(6.95, 0.6), (6.75, 1.4), (6.7, 2.05)]),
                           ('11-09', '11-10', 'H', [(7.0, 0.35), (6.85, 1.1), (6.7, 1.8), (6.65, 2.1)])], 'the 1st Division')
split('Y-BR-1D', '11-11', [(None, None, 'I', [(7.1, 0.15), (6.55, 0.5), (6.4, 0.8), (6.6, 1.4)])], 'the 1st Division')

split('Y-BR-2D', '10-21', [(None, '10-22', 'A', [(2.55, -8.4), (3.6, -6.85), (4.8, -5.3), (6.0, -3.8), (6.9, -2.6)]), ('10-23', '10-23', 'B', [(2.8, -7.6), (3.15, -6.85), (4.0, -5.5), (5.1, -3.9), (6.4, -2.1)])], 'the 2nd Division')
split('Y-BR-2D', '10-24', [(None, '10-24', None, None), ('10-25', '10-28', 'C', [(8.4, -2.45), (8.5, -1.5), (8.3, -0.5), (8.5, 0.3)], 'The south end is put at Reutel; the sketch does not mark the boundary with the 7th Division.'),
                           ('10-29', '10-30', 'E', [(9.7, -2.65), (9.68, -2.1), (9.48, -1.55), (9.08, -1.0), (8.68, -0.5), (8.43, -0.1), (8.36, 0.25), (8.48, 0.65), (8.63, 1.05)]),
                           ('10-31', '11-03', 'F', [(9.55, -2.6), (9.6, -1.5), (9.3, -0.7), (9.0, -0.2), (8.4, 0.15), (7.6, 0.25), (7.1, 0.5)]),
                           ('11-04', '11-08', 'G', [(9.5, -2.6), (9.4, -1.7), (9.0, -0.7), (8.5, 0.0), (7.9, 0.2), (7.1, 0.45)]),
                           ('11-09', '11-10', 'H', [(9.45, -2.7), (9.4, -1.8), (9.1, -0.9), (8.7, -0.3), (8.0, 0.05), (7.1, 0.2)]),
                           ('11-11', None, 'I', [(9.75, -2.85), (9.7, -1.9), (9.45, -1.1), (9.0, -0.5), (8.4, -0.1), (7.3, 0.2)])], 'the 2nd Division')

split('Y-BR-3CD', '10-21', [(None, '10-22', 'A', [(6.0, 4.95), (4.4, 5.05)]),
                            ('10-23', '10-29', 'C', [(7.3, 4.75), (4.7, 4.9)], SAME.format('7, 8 and 9', '23, 25 and 29 October'))], 'the 3rd Cavalry Division')
_p = _row('Y-BR-3CD', '11-06'); _p['keys'] = ['ZWAR']; _p['place'] = 'Zwarteleen'
_p['notes'] += ' v7: drawn as a point at Zwarteleen. Sketches 13 and 14 write the division\'s name behind Cavan\'s line, not on it. Zwarteleen as read from Sketch A lies about 250 m outside Cavan\'s line as read from those sketches: the two readings differ by about their own error.'; V7[_p['pos_id']] = 'Now a point, not a line (see notes).'

split('Y-BR-2CD', '10-21', [(None, '10-22', 'A', [(3.8, 5.25), (3.4, 6.3), (3.1, 7.3), (2.7, 8.1), (1.2, 9.3)]),
                            ('10-23', '10-29', 'C', [(3.9, 5.25), (3.1, 6.3), (2.3, 7.5), (1.4, 9.05)], SAME.format('7, 8 and 9', '23, 25 and 29 October'))], 'the 2nd Cavalry Division')
split('Y-BR-2CD', '10-30', [(None, '10-30', None, None), ('10-31', '10-31', 'F', [(0.65, 5.3), (0.55, 6.0), (0.5, 6.9), (0.6, 7.9), (0.75, 8.9)])], 'the 2nd Cavalry Division')
new('Y-BR-2CD', '11-04', '11-08', 'G', [(-1.4, 9.05), (-1.1, 10.85)], 'the 2nd Cavalry Division', 'Back in line west of Messines', 'MESS14',
    'S42 has the division going into reserve at Bailleul in "early November"; the sketch has it in line on the 4th. On Sketch 13 (9 November) the 1st Cavalry Division is here instead.')
new('Y-BR-2CD', '11-11', '11-11', 'I', [(-2.35, 9.8), (-1.6, 9.95), (-1.2, 10.4), (-1.05, 10.65)], 'the 2nd Cavalry Division', 'In support behind the French line', 'MESS14',
    'The line is behind the French front, not on it. Not followed after this.', el='unknown', rear=True)

split('Y-BR-1CD', '10-21', [(None, None, 'C', [(1.27, 9.45), (1.2, 10.85)], SAME.format('4, 7, 8 and 9', '21 to 29 October'))], 'the 1st Cavalry Division')
split('Y-BR-1CD', '10-31', [(None, None, 'F', [(0.75, 8.9), (0.9, 9.5), (1.05, 9.85), (1.25, 10.3), (1.35, 10.9)])], 'the 1st Cavalry Division')
new('Y-BR-1CD', '11-09', '11-10', 'H', [(-2.75, 8.5), (-2.6, 9.1), (-2.0, 9.5), (-1.4, 9.7), (-1.1, 10.1), (-1.05, 10.6)], 'the 1st Cavalry Division', 'In support behind the French line', 'MESS14',
    'The line is behind the French front, not on it. On Sketch 14 (11 November) the 2nd Cavalry Division is here instead.', rear=True)

_4 = 'The sketch stops at its bottom edge, about 1 km short of the Lys; the line went on to the river.'
for _q in split('Y-BR-4D', '10-21', [(None, '10-30', 'C', [(1.15, 11.15), (1.6, 12.3), (2.25, 13.75), (2.5, 14.5)], SAME.format('4, 7, 8 and 9', '21 to 29 October') + ' ' + _4),
                           ('10-31', '11-03', 'F', [(1.35, 11.25), (1.6, 12.1), (2.0, 13.0), (2.5, 14.1), (2.7, 14.5)], _4),
                           ('11-04', '11-08', 'G', [(-0.9, 11.2), (0.0, 11.7), (1.45, 12.1), (1.9, 13.3), (2.4, 14.4)], 'The left now reaches west along the Douve, behind the lost Messines ridge. ' + _4),
                           ('11-09', '11-10', 'H', [(-0.75, 11.1), (0.0, 11.5), (1.4, 12.05), (1.7, 12.5), (2.0, 13.25), (2.2, 13.6), (2.5, 14.4)], _4),
                           ('11-11', None, 'I', [(-0.35, 11.0), (-0.2, 11.3), (1.0, 11.8), (1.7, 12.05), (1.6, 12.6), (1.75, 13.3), (2.25, 13.5), (2.7, 14.5)], 'The sketch draws small breaks in the line at St. Yves and Le Gheer; they are smoothed here. ' + _4 + ' ' + END)], 'the 4th Division'):
    _q['notes'] = _q['notes'].replace('Not followed day by day after 22 October; ', '').replace('S43 has it', 'S43 has the division'); _q['battle_id'] = NB

split('Y-BR-BULF', '10-30', [(None, '10-30', None, None), ('10-31', '10-31', 'F', [(6.15, 3.1), (5.5, 3.7), (4.85, 4.05)])], "Bulfin's Force")
split('Y-BR-BULF', '11-01', [(None, '11-03', None, None), ('11-04', '11-05', 'G', [(5.85, 3.35), (4.0, 3.65)])], '"Cavan"')
split('Y-BR-BULF', '11-06', [(None, '11-08', None, None), ('11-09', '11-10', 'H', [(6.15, 3.1), (5.5, 3.4), (4.9, 3.4), (4.2, 3.0), (3.75, 2.85), (3.25, 2.8)]), ('11-11', None, 'I', [(5.6, 3.35), (5.0, 3.35), (4.2, 3.0), (3.4, 2.85)])], '"Cavan"')
split('Y-BR-3D', '11-07', [(None, '11-08', None, None), ('11-09', '11-10', 'H', [(6.6, 2.25), (6.2, 2.95), (6.15, 3.1)], 'The sketch names the brigade commanders here (Shaw, Gleichen, McCracken) under the 3rd Division.')], 'the 3rd Division')
split('Y-BR-3D', '11-11', [(None, None, 'I', [(6.65, 1.55), (6.8, 1.95), (6.75, 2.1), (6.55, 2.5), (6.2, 3.0), (5.8, 3.3)], 'The north end is put where the drawn line changes from solid to broken, just north of the Menin road.')], 'the 3rd Division')

# ---------- French ----------
_p = _row('Y-FR-89T', '10-20')
_apply(_p, 'F', [(-3.95, -9.5), (-3.4, -7.6)], 'a Territorial division', extra='The same line is on every sketch from 21 October to 11 November; it is read from Sketch 10. The sketches run off their top edge here: the line went on north along the canal. ' + END)
_p['ee'] = D('11-22'); _p['el'] = 'unknown'; _p['notes'] = _p['notes'].replace('Not followed after this.', '').strip(); V7[_p['pos_id']] = 'Line re-read from Sketch 10 and carried to the end of the battle.'
split('Y-FR-87T', '10-24', [(None, '10-24', None, None), ('10-25', '10-28', 'C', [(-1.3, -7.4), (-0.9, -7.35), (0.5, -7.3), (1.9, -7.6), (2.4, -7.65)],
       'The sketch labels the whole front from the canal to beyond Langemarck "De Mitry". S42 puts the 87th Territorial Division between Bixschoote and Langemarck, so this row takes that part of the sketch line; where the division really began and ended is not shown.')],
      'this front under the name "De Mitry"', oc='low', method=inf, rear=True)
_DM = 'The sketches name the commander, not the formations. The group was French cavalry with Territorial infantry (S40; S42).'
for _d0, _d1, _sk, _pts, _x in [
    ('10-25', '10-28', 'C', [(-2.7, -7.45), (-0.9, -7.35), (0.5, -7.3), (1.9, -7.6), (2.9, -7.7), (3.9, -7.3), (4.6, -6.8)], _DM),
    ('10-29', '10-30', 'E', [(-2.55, -7.7), (-1.6, -8.35), (-1.1, -8.5), (-0.25, -8.0), (1.0, -7.85), (3.0, -7.75), (3.6, -7.7)], 'Bixschoote is inside the line on this day.'),
    ('10-31', '11-03', 'F', [(-2.6, -7.5), (-2.0, -8.25), (-1.3, -8.5), (-0.25, -8.15), (3.0, -7.7), (3.65, -7.7)], ''),
    ('11-04', '11-08', 'G', [(-2.55, -7.4), (-0.4, -7.9), (2.0, -8.25), (3.3, -8.45), (3.65, -8.3)], 'Bixschoote is now outside the line.'),
    ('11-09', '11-10', 'H', [(-2.5, -7.55), (-1.5, -7.85), (-0.2, -7.95), (2.0, -8.05), (3.0, -8.25), (3.5, -8.2)], ''),
    ('11-11', '11-22', 'I', [(-2.25, -7.3), (-1.0, -7.55), (0.0, -7.7), (2.0, -7.95), (3.0, -8.15), (3.6, -8.2)], 'The sketch also draws the line of 10 November, a few hundred metres further north at its west end. ' + END)]:
    new('Y-FR-2CC', _d0, _d1, _sk, _pts, '"De Mitry"', 'Holding the north face from the canal to north of Langemarck', 'YPRES1', _x)
_p = _row('Y-FR-2CC', '10-21'); _p['el'] = D('10-24'); _p['notes'] = _p['notes'].replace('Not followed after this.', 'Sketch 8 has the group back east of the canal by 25 October.'); V7[_p['pos_id']] = 'End is now 23-24 October: a later row follows.'

_q = split('Y-FR-17D', '10-24', [(None, '10-24', None, None), ('10-25', '10-28', 'C', [(4.75, -6.65), (5.8, -5.5), (7.0, -4.4), (7.7, -3.5), (8.1, -2.7)],
       'The sketch names the corps, not the division; the 17th was the division that relieved the British here (S47). From 29 October the corps has its own rows and the division is not shown.')], 'this front under the name "IX Corps"')
_q[-1]['ee'] = D('10-28'); _q[-1]['el'] = 'unknown'
_9 = 'The sketches show the corps sector without naming its divisions (the 17th and 18th: S44).'
for _d0, _d1, _sk, _pts, _x in [
    ('10-29', '10-30', 'E', [(6.0, -6.4), (7.0, -5.3), (8.0, -4.4), (8.6, -3.8), (9.2, -3.05)], _9 + ' The north end is put 1 km south-east of Poelcappelle, where the label of the 31st Division ends.'),
    ('10-31', '11-03', 'F', [(6.2, -6.15), (7.0, -5.3), (8.65, -3.8), (9.5, -2.95)], ''),
    ('11-04', '11-08', 'G', [(5.55, -6.1), (6.1, -5.4), (6.9, -4.95), (7.7, -4.7), (8.4, -4.1), (9.0, -3.5), (9.45, -3.05)], ''),
    ('11-09', '11-10', 'H', [(5.55, -6.05), (6.15, -5.4), (7.0, -5.0), (7.8, -4.7), (8.5, -4.1), (9.1, -3.5), (9.5, -3.0)], ''),
    ('11-11', '11-22', 'I', [(5.7, -6.1), (6.2, -5.5), (7.0, -5.05), (7.8, -4.8), (8.5, -4.3), (9.2, -3.6), (9.75, -3.0)], END)]:
    new('Y-FR-9C', _d0, _d1, _sk, _pts, 'the IX Corps', 'Holding from Poelcappelle to the Broodseinde cross-roads', 'YPRES1', _x)
_p = _row('Y-FR-18D', '10-29'); _p['keys'] = []; _p['place'] = 'Not shown'; _p['activity'] = 'In the IX Corps sector'; _p['ee'] = D('11-22'); _p['el'] = D('11-22')
_p['notes'] = 'v7: the inferred line is withdrawn. The sketches label this front "De Mitry" and "IX Corps" and do not show the 18th Division; see the IX Corps rows. S44 puts the division in the fighting of 29 October but gives no sector.'
V7[_p['pos_id']] = 'Inferred line withdrawn; no position.'
retire('Y-FR-18D', '11-10', 'An inferred French retreat towards Pilckem on 10 November. Sketch 14 shows the French line still running from the canal near Steenstraat past Kortekeer on the afternoon of the 11th.')

retire('Y-FR-31D', '10-29', 'An inferred line from Steenstraat to Bixschoote. Sketch 9 puts the 31st Division near Poelcappelle on 29 October and "De Mitry" at Bixschoote.')
retire('Y-FR-31D', '11-10', 'An inferred retreat to the canal on 10 November. Sketches 13 and 14 put "Vidal" south of Ypres, next to Cavan, on 9 and 11 November.')
new('Y-FR-31D', '10-29', '10-30', 'E', [(3.6, -7.7), (4.3, -7.4), (5.0, -7.1), (6.0, -6.4)], "the 31st Division, with Hély d'Oissel,", 'In line at Poelcappelle', 'YPRES1',
    'Where the division ends and the IX Corps begins is not marked; the break is put 1 km south-east of Poelcappelle. S44 has the division helping to retake Bixschoote and Kortekeer Cabaret on this day, some 5 km further west.', oc='low')
new('Y-FR-31D', '10-31', '11-03', 'F', [(3.85, -7.65), (5.0, -7.15), (6.1, -6.25)], '"Vidal"', 'In line from north of Langemarck to Poelcappelle (Vidal)', 'YPRES1',
    'The sketch names the commander, not the division. S43 has Vidal on the Menin road with part of his force on 2 November: see YG09.')
new('Y-FR-31D', '11-09', '11-10', 'H', [(3.2, 2.8), (2.55, 3.2), (2.35, 3.8)], '"Vidal"', "On the right of Cavan's Force, north of the canal (Vidal)", 'YPRES1',
    'The sketch names the commander. How much of the 31st Division was here is not shown. Where the group was from 4 to 8 November is not on the sketches read.')
new('Y-FR-31D', '11-11', '11-22', 'I', [(3.28, 2.83), (2.78, 2.73), (2.23, 2.73), (1.73, 2.88), (1.23, 3.2), (0.88, 3.5)], '"Vidal"', 'Bent back north of the canal', 'YP-NONNE',
    'The sketch also draws the line of the day before, running from Cavan\'s right straight to the canal near Hollebeke. By the afternoon of the 11th it had been bent back to the north-west, past Hill 60. Between the west end of this line and the left of the 32nd Division the sketch draws nothing; the canal bank is taken as the front. See YC05. ' + END)
for _d0, _d1, _sk, _pts, _x in [
    ('11-04', '11-08', 'G', [(3.85, -8.15), (4.6, -7.5), (5.1, -6.9), (5.55, -6.15)], 'On Sketch 9 (29 October) the name stands beside the 31st Division on the same stretch.'),
    ('11-09', '11-10', 'H', [(3.7, -8.05), (4.5, -7.5), (5.1, -6.9), (5.5, -6.25)], ''),
    ('11-11', '11-22', 'I', [(4.0, -8.05), (4.6, -7.6), (5.2, -7.0), (5.65, -6.2)], END)]:
    new('Y-FR-HELY', _d0, _d1, _sk, _pts, '"Hély d\'Oissel"', 'Holding either side of Poelcappelle road, between de Mitry and the IX Corps', 'YPRES1', _x)

split('Y-FR-MOUS', '11-01', [(None, '11-03', 'F', [(4.75, 4.08), (3.85, 4.42)]), ('11-04', '11-06', 'G', [(3.95, 3.6), (3.0, 3.75), (2.35, 4.1)])], '"Moussy"')
_p = _row('Y-FR-MOUS', '11-01'); _p['se'] = _p['sl'] = D('10-31'); V7[_p['pos_id']] += ' Start moved to 31 October, the date of the sketch.'
_p = _row('Y-FR-MOUS', '11-07'); _p['ee'] = D('11-08'); _p['notes'] += ' v7: from 9 November the sketches name Vidal on this stretch.'; V7[_p['pos_id']] = 'Row now ends on 8 November.'
new('Y-FR-OLL', '10-31', '11-03', 'F', [(2.15, 4.35), (1.6, 4.6), (1.0, 5.05)], '"Woillemont"', 'Holding between the canal and St. Eloi (Woillemont)', 'MESS14', '')
new('Y-FR-OLL', '11-04', '11-08', 'G', [(2.0, 4.35), (0.7, 5.15)], '"Olleris"', 'Holding between the canal and St. Eloi (Olleris)', 'MESS14', 'On Sketch 13 (9 November) the 32nd Division holds this stretch.')

_p = _row('Y-FR-32D', '11-01'); _p['ee'] = _p['el'] = D('11-03'); _p['notes'] += ' v7: from 4 November the division is drawn from the sketches.'; V7[_p['pos_id']] = 'Row now ends on 3 November.'
retire('Y-FR-32D', '11-10', 'An inferred loss of St. Eloi on 10 November, from the German account. Sketches 13 and 14 keep the French line about 1 km south-east of St. Eloi on 9 and 11 November (YC07).')
_32 = 'Division boundaries inside the French line are not marked on the sketch; the ends of this row are put by where the label sits.'
new('Y-FR-32D', '11-04', '11-08', 'G', [(0.65, 5.3), (0.25, 6.0), (-0.1, 6.8)], 'the 32nd Division', 'Holding south of St. Eloi', 'MESS14', _32, oc='low')
new('Y-FR-32D', '11-09', '11-10', 'H', [(2.2, 4.4), (1.6, 4.9), (0.5, 5.5)], 'the 32nd Division', 'Holding from the canal to south of St. Eloi', 'MESS14', _32, oc='low')
new('Y-FR-32D', '11-11', '11-22', 'I', [(2.05, 4.4), (1.4, 5.1), (0.8, 5.6)], 'the 32nd Division', 'Holding from the canal to south of St. Eloi', 'MESS14', _32 + ' ' + END, oc='low')
_16 = 'One row for the rest of the corps line, because the boundaries between the formations named on the sketch cannot be read (YG14).'
new('Y-FR-16C', '11-04', '11-08', 'G', [(-0.1, 6.8), (-0.6, 7.3), (-0.95, 7.7), (-1.1, 8.1), (-1.2, 8.7)], "the 39th and 43rd Divisions and Conneau's cavalry, under the XVI Corps,", 'Rest of the corps line, west of Wytschaete', 'MESS14', _16)
new('Y-FR-16C', '11-09', '11-10', 'H', [(0.5, 5.5), (-0.3, 6.2), (-0.8, 6.9), (-1.1, 7.7), (-1.15, 8.5), (-0.9, 9.3), (-0.6, 10.0), (-0.35, 10.6)], "the 11th, 39th and 43rd Divisions and Conneau's cavalry, under the XVI Corps,", 'Rest of the corps line, from south of St. Eloi to the Douve', 'MESS14',
    _16 + ' The number of the second division is hard to read on this sketch; it is taken as the 39th from Sketches 12 and 14.')
new('Y-FR-16C', '11-11', '11-22', 'I', [(0.8, 5.6), (-0.1, 6.1), (-0.7, 6.8), (-1.0, 7.4), (-1.6, 7.9), (-1.7, 8.4), (-1.5, 9.0), (-1.0, 9.6), (-0.75, 10.1), (-0.4, 10.9)], 'part of the 11th Division, the 39th and 43rd Divisions and the 156th Regiment, under the XVI Corps,', 'Rest of the corps line, from south of St. Eloi to the Douve', 'MESS14', _16 + ' ' + END)

_row('Y-FR-87T', '10-20')['rear'] = True      # the British 1st Division line of Sketches 4 and 7 covers this stretch
# ---------- German rows: keep them on the German side of the Allied line of each sketch ----------
SIDE = {u[0]: u[3] for u in U}
def _dd(s): return _dt.date.fromisoformat(s)
def _span(p):
    s = p['se'] if p['se'] != 'unknown' else p['sl']; e = p['el'] if p['el'] not in ('unknown', None) else p['ee']
    return _dd(s), _dd(e)
def _km(p): return [ll2km(a, b) for a, b in line(p)]
BOX = (-6.5, -10.0, 11.5, 15.5)
def _active(p, day): return _dd(p['sl'] if p['sl'] != 'unknown' else p['se']) <= day <= _span(p)[1]
def front(day):
    """The Allied front on one day as one polyline, north to south, chained from the canal. None if no row read from a sketch is in force."""
    rows = [p for p in P if SIDE[p['unit_id']] == SIDE_A and not p.get('rear') and _active(p, day)]
    if not any(p.get('sk') for p in rows): return None, []
    ls = [l for l in (_km(p) for p in rows) if len(l) > 1 and all(BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3] for x, y in l)]
    ls.sort(key=lambda l: min(q[1] for q in l)); cur = ls.pop(0)
    if cur[0][1] > cur[-1][1]: cur = cur[::-1]
    F = list(cur)
    while ls:
        e = F[-1]; j, rev, d = min(((j, r, _m.hypot((l[-1] if r else l[0])[0] - e[0], (l[-1] if r else l[0])[1] - e[1])) for j, l in enumerate(ls) for r in (0, 1)), key=lambda t: t[2])
        if d > 3.6:   # a stretch with no row in force (for example after a relief): bridge to the next line further south, if there is one
            c = [(j, r, _m.hypot((l[-1] if r else l[0])[0] - e[0], (l[-1] if r else l[0])[1] - e[1])) for j, l in enumerate(ls) for r in (0, 1) if min(q[1] for q in l) > e[1] - 0.5]
            if not c: break
            j, rev, d = min(c, key=lambda t: t[2])
            if d > 12: break
        l = ls.pop(j); F += (l[::-1] if rev else l)
    return F, ls
def _inside(g, poly):
    x, y = g; c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c
def _nearest(g, F):
    best = None
    for a, b in zip(F, F[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
        if L2 < 1e-9: continue
        t = max(0.0, min(1.0, ((g[0] - a[0]) * dx + (g[1] - a[1]) * dy) / L2)); q = (a[0] + t * dx, a[1] + t * dy); d = _m.hypot(g[0] - q[0], g[1] - q[1])
        if best is None or d < best[0]: best = (d, q, (dx / _m.sqrt(L2), dy / _m.sqrt(L2)))
    return best
MARGIN = 0.5
def _push(g, F, poly):
    g0 = g
    for step in range(12):
        d, q, (ux, uy) = _nearest(g, F); ins = _inside(g, poly)
        if not ins and d >= MARGIN - 0.03: break
        if not ins and (q == F[0] or q == F[-1]) and step == 0: break       # beyond an end of the front: leave alone
        n = (uy, -ux)                                                       # left of the direction of travel = German side
        g = (q[0] + n[0] * (MARGIN + 0.15 * step), q[1] + n[1] * (MARGIN + 0.15 * step))
    return g, _m.hypot(g[0] - g0[0], g[1] - g0[1])
def _segx(p1, p2, p3, p4):
    def o(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return o(p3, p4, p1) * o(p3, p4, p2) < 0 and o(p1, p2, p3) * o(p1, p2, p4) < 0
def _crosses(line_, F): return any(_segx(a, b, c, d) for a, b in zip(line_, line_[1:]) for c, d in zip(F, F[1:]))
_D0, _D1 = _dd(D('10-21')), _dd(D('11-22'))
FRONT = {}; LEFT = {}
_d = _D0
while _d <= _D1:
    FRONT[_d], LEFT[_d] = front(_d); _d += _dt.timedelta(days=1)
for _d in list(FRONT):      # after the British reliefs of 15 to 22 November no row follows the eastern face: keep the front of the 15th
    if _d > _dd(D('11-15')): FRONT[_d] = FRONT[_dd(D('11-15'))]
def _skof(day): return [k for k, v in SK.items() if _dd(D(v[1])) <= day][-1]
def _fit(g0, day):
    """g0: [(name, (x, y), src, prec)]. Returns [(name, (x, y), src, prec, moved km)] clear of the front of that day."""
    F = FRONT.get(day)
    if not F: return [v + (0.0,) for v in g0]
    poly = F + [(-45.0, F[-1][1]), (-45.0, F[0][1])]
    cur = list(g0)
    for dens in (None, 1.2, 0.6):
        if dens:   # add points along long stretches so the line can bend round the front
            nxt = [cur[0]]
            for a, b in zip(cur, cur[1:]):
                L = _m.hypot(b[1][0] - a[1][0], b[1][1] - a[1][1]); n = int(L // dens)
                for i in range(1, n + 1):
                    t = i / (n + 1); nxt.append((f'between {a[0]} and {b[0]}' if not a[0].startswith('between') and not b[0].startswith('between') else (a[0] if a[0].startswith('between') else b[0]), (a[1][0] + t * (b[1][0] - a[1][0]), a[1][1] + t * (b[1][1] - a[1][1])), 'derived', 1000))
                nxt.append(b)
            cur = nxt
        out = []
        for v in cur:
            g, m = _push(v[1], F, poly); out.append((v[0], g, v[2], v[3], m))
        if not _crosses([v[1] for v in out], F): break
    # drop added points that did not need to move
    return [v for v in out if not (v[0].startswith('between') and v[4] < 0.05)]
MOVED = []     # (pos_id, unit, sketch, n moved, n points, max km)
def fit_germans():
    for p in [p for p in P if SIDE[p['unit_id']] == SIDE_G and p['keys']]:
        s, e = _span(p); s = max(s, _D0)
        if e < s: continue
        g0 = [(PL[k][0].split(' (')[0], ll2km(PL[k][2], PL[k][3]), PL[k][4], PL[k][5]) for k in p['keys']]
        if not all(BOX[0] - 3 <= v[1][0] <= BOX[2] + 3 and BOX[1] - 1 <= v[1][1] <= BOX[3] + 1 for v in g0): continue
        res = []; d = s
        while d <= e:
            res.append((d, _fit(g0, d))); d += _dt.timedelta(days=1)
        def same(a, b): return len(a) == len(b) and max(_m.hypot(x[1][0] - y[1][0], x[1][1] - y[1][1]) for x, y in zip(a, b)) <= 0.3
        def ok(pts, day):
            F = FRONT.get(day)
            if not F: return True
            poly = F + [(-45.0, F[-1][1]), (-45.0, F[0][1])]
            return not _crosses([v[1] for v in pts], F) and not any(_inside(v[1], poly) for v in pts)
        groups = [[res[0]]]
        for r in res[1:]:
            if same(groups[-1][0][1], r[1]) and ok(groups[-1][0][1], r[0]): groups[-1].append(r)
            else: groups.append([r])
        if len(groups) == 1 and max(v[4] for v in groups[0][0][1]) < 0.05: continue
        o = ORIG[p['pos_id']]
        for i, grp in enumerate(groups):
            d, pts = grp[0]; k = _skof(d); n = SK[k][0]
            if i == 0: q = p
            else:
                q = _copy.deepcopy(o); q['pos_id'] = _nid(); P.append(q); q['se'] = q['sl'] = d.isoformat()
            if i < len(groups) - 1: q['ee'] = q['el'] = grp[-1][0].isoformat()
            nm = sum(1 for v in pts if v[4] >= 0.05); mx = max(v[4] for v in pts)
            if nm:
                q['pts'] = [km2ll(*v[1]) + ((v[2], v[3], v[0]) if v[4] < 0.05 else ('derived', max(v[3], 1000), v[0] + (f', moved {v[4]:.1f} km' if not v[0].startswith('between') else ''))) for v in pts]
                how = f'{nm} of {len(pts)} point{"s" if len(pts) > 1 else ""} moved or added, by up to {mx:.1f} km, to stand 500 m on the German side of the Allied line as mapped for these days (Sketch {n} of S40 where it is read from a sketch).'
                q['cbasis'] = ('A line: ' if len(pts) > 1 else 'A point: ') + how + (' The others are the places named, as on the Places sheet.' if nm < len(pts) else '')
                q['pbasis'] = how + ' Good to about 1 km.'
                q['notes'] = (q['notes'] + ' ' if q['notes'] else '') + f'v7: the places named are where the German account puts the unit; the {"line" if len(pts) > 1 else "point"} is drawn clear of the Allied line as mapped for these days.'
                if 'S40' not in q['source_ids']: q['source_ids'] += '; S40'
                MOVED.append((q['pos_id'], q['unit_id'], n, nm, len(pts), round(mx, 2)))
            else: q.pop('pts', None)
            V7[q['pos_id']] = ((f'{nm} of {len(pts)} point{"s" if len(pts) > 1 else ""} moved or added (up to {mx:.1f} km) to clear the Allied line.' if nm else 'Line unchanged.') + (f' Row now ends on {_nice(q["ee"][5:])}; the rest of its time is in new rows.' if len(groups) > 1 else '')) if i == 0 \
                else f'New in v7: part of the time of row {o["pos_id"]}' + (f', with {nm} of {len(pts)} point{"s" if len(pts) > 1 else ""} moved or added (up to {mx:.1f} km) to clear the Allied line.' if nm else ', with its line as it was.')
fit_germans()

# ---------- order: by unit as listed, then by date ----------
_ui = {u[0]: i for i, u in enumerate(U)}
P.sort(key=lambda p: (_ui[p['unit_id']], p['sl'] if p['sl'] != 'unknown' else p['se'], p['se'], p['pos_id']))

# ---------- conflicts and gaps ----------
CONFLICTS += [
 ('YC11', 'YPRES1', 'When did the British 1st Division come back into line after its relief at Langemarck?', 'S42: it "came up on the right of the 2nd Division" on 25 October. S40, Sketch 8: on 25 October it is still drawn as a reserve, an oval between Ypres and Zillebeke. S40, Sketch 9: in line east of Polygon Wood and across the Menin road by 29 October.',
  'Reserve row ends between 25 and 26 October; the row in line starts between 25 and 27 October.', 'The text of the official history for these days was not read; it would settle the date.', 'Open'),
 ('YC12', 'YPRES1', 'How far did the Germans get north of Ypres on 10 November?', 'S41: "by evening the canal had been reached along almost its whole length", and the 44th Reserve Division "pushed forward till close up to HET SAS". S40, Sketch 14: on the afternoon of 11 November the French line still runs from the canal near Steenstraat past Kortekeer to the Langemarck-Poelcappelle road, about 2.5 km north of Het Sas; the line of the 10th is drawn a few hundred metres north of that.',
  'Official-history sketch followed for the French line. German rows keep the places the German account names, but are drawn clear of the French line.', 'Het Sas is on the canal, and "close up to" may only mean the canal bank at Steenstraat. The French official history would say.', 'Open'),
]
C7 = {'YC02': 'Sketch 7 (23 October) still draws the British 2nd Division between Langemarck and Zonnebeke station, with an arrow for the "advance of the 17th Division (IX Corps)" through it; Sketch 8 (25 October) has the IX Corps on that front and the 2nd Division east of Polygon Wood. The start range of 23 to 24 October stands.',
      'YC03': 'Sketch 13 (9 November) labels the line south of the Menin road "3rd Div." with the names Shaw, Gleichen and McCracken. That supports the 3rd Division, not the 5th.',
      'YC04': 'Sketch 12 (4 November) draws the French line about 1 km west of Wytschaete and has the British cavalry and 4th Division well west of Messines. Both villages are German by the 4th on the official map.',
      'YC05': 'Sketch 14 draws the French line on the afternoon of 11 November bent back north of Hill 60, with the line of the day before south of it. The official map therefore agrees with the German account that the hill was lost on the 11th. The French row (Vidal) now follows the sketch. The German XV Corps row keeps the places the German account names (Klein Zillebeke and the canal bend) and is not carried forward to the hill.',
      'YC07': 'Sketches 13 and 14 keep the French line about 1 km south-east of St. Eloi on 9 and 11 November. The inferred row that gave up St. Eloi on the 10th is withdrawn, and the II Bavarian Corps line is drawn clear of the French line, short of the village. The German claim stands in the wording of its row.',
      'YC09': 'Sketch 7 draws the British line of 23 October through Kortekeer; nothing new on the 22nd.'}
GAPS += [
 ('YG14', 'YPRES1', 'Boundaries between formations are not marked on the sketches', 'Where one division stops and the next begins is put at breaks in the drawn line or at the ends of labels. The French XVI Corps line of 4 to 11 November is one row for several divisions because they cannot be separated.', 'The French official history and its maps; British divisional war diaries.'),
 ('YG15', 'YPRES1', 'The sketches show German formations as arrows, not lines', 'German rows still take their places from the German account. Where that would put them on or behind the Allied line as mapped, the points are moved 500 m clear of it and marked "derived".', 'German divisional histories or the Reichsarchiv maps.'),
 ('YG16', 'YPRES1', 'Only the last line on each sketch was read', 'Each sketch covers two to five days and draws the line of each; only the latest (the solid line) is in the data. Days between sketch dates keep the earlier line or fall back on the text, so the British line of 26 to 28 and 30 October and of 1 to 3 and 5 to 8 November is the least sure.', 'Read the dashed and dotted lines on Sketches 9, 10, 12, 13 and 14.'),
 ('YG17', 'YPRES1', 'Sketches 6, 11, 15 and 16 were not used', 'They are larger-scale views (the situation on 20 October, Gheluvelt on 31 October, the situation on 10 November and the Guard attack of 11 November). The Gheluvelt and Nonne Bosschen rows are less exact than they could be.', 'Georeference and read them the same way.'),
]
G7 = {'YG01': 'Largely closed for the Allied side: British and French lines for 21, 23, 25, 29 and 31 October and 4, 9 and 11 November are now read from Sketches 4, 7, 8, 9, 10, 12, 13 and 14. The text after page 176 is still unread.',
      'YG02': 'Partly closed: the sketches give the French sectors, by commander or corps, on the eight dates above. Four inferred French rows are withdrawn and replaced. Still no French source.',
      'YG03': 'Unchanged, and now sharper: German lines are text placed against a mapped Allied line (YG15).',
      'YG04': 'Closed for the Allied side on the eight sketch dates; open for the German side and for the days between.',
      'YG05': 'Closed for the rows read from sketches, which follow the drawn line with 2 to 10 points. Still true of the German rows and of the Allied rows that rest on text.',
      'YG08': 'Unchanged. Rows read from a sketch run to the day before the next sketch; that is a convention, not a source date.',
      'YG09': 'The sketches name more such groups: de Mitry, Hély d\'Oissel, Vidal, Moussy, Woillemont, Olleris, Cavan. Each is now a row or a unit; what each was made of is still not recorded.',
      'YG10': 'The dated sketches end about 9.5 km north and 14.5 km south of Ypres; rows read from them stop at those edges.'}
SOURCE_V7 = 'v7: the solid line (the latest date) on each of Sketches 4, 7, 8, 9, 10, 12, 13 and 14 was read for the British and French positions. The sketches were tied to village centres on the current map, with a typical misfit of 130 to 190 m.'
