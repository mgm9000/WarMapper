"""Refit of Mouzon 1775 to the ground, 26 Nov 2026: no folds along the roads.

  python3 -I pipeline/georef/sc_mouzon_refit_2026_11_26.py     rewrites pairs and smoothing in pipeline/georef/sc_mouzon_fit.json

Why. Morgan asked why some roads took very odd angles (above the Catawba Nation the road to Charlotte turned back on itself). The road was
traced right; the fit was folded there. Session 4's fit (sc_mouzon_fit.py: per-section thin-plate splines from 14 point controls and some
1,350 pairs that match Mouzon's rivers, coast and North Carolina line to today's, every 12 pixels) bends to follow every pair, and where
pairs disagree it turns the map over on itself: checked along every traced line, 303 points sat on folded ground, 26 of them on roads.

What changes (the ICP pairs are kept as 'pairs_icp', so this can be run again):
  - Pairs on 20th-century reservoirs are dropped (Marion, Moultrie, Wateree, Wylie, Murray, Greenwood, Thurmond, Russell, Hartwell,
    Keowee, Parr, Fishing Creek). Natural Earth draws a centre line down each lake, not the river of 1775.
  - Pairs on the Pee Dee, Little Pee Dee, Waccamaw and Black rivers are dropped. Mouzon draws that low country well out of true with
    itself, and matching it line for line folded the map there; the point controls on those rivers (their meetings with the Pee Dee, the
    Pee Dee at Winyah Bay, the North Carolina line at the sea) are kept.
  - The splines are stiffer (smoothing 40 a km squared west of the seam, 200 east of it, against 8).
  - Seven places are added as point controls, read on the scan where Mouzon draws them, so that his roads meet where the towns are:
    Camden (the court house), Orangeburg (the court house), Charles Town (the walled town on the point), Georgetown, Dorchester,
    Beaufort and Long Bluff (the Cheraws court house). Their places are the workbook's (Control places), the town's centre or the
    marker's; weights 1-3 km (3 km for Camden, Georgetown and Long Bluff, which Mouzon has furthest out of place against
    their neighbours: held hard, the fit made a dimple round each that bent the roads into them). Left out: Cheraw (Mouzon's road to it is not traced to the town) and the Congarees (Mouzon's 'Old Fort'
    sits north-west of the Broad and Saluda's meeting as traced, but Fort Granby is south of it on the ground; held to both, the fit
    folded there).
  - Two seam ties hold the upper right section's lower edge to the lower right one where the Pee Dee and Little Pee Dee cross the gap.
Result: every control is held within 0.5 km (Pee Dee at Winyah Bay 3.6, Georgetown 1.9); nothing folds along the traced lines and no road
turns back on itself on the ground. Left out in turn, a control is found again a median 5.0 km from where it belongs (0-17 km; Camden 17,
Georgetown 11.6, Esseneca 11.2 against 26); Session 4's fit, folds and all, gave 1.1 km. That is Mouzon's own drawing between his
towns; the stiffer fit no longer bends to hide it, so the controls carry the map and the roads are given as good to 3-5 km between them.
"""
import json, math, os
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
FITF = os.path.join(HERE, 'sc_mouzon_fit.json')
TRF = os.path.join(os.path.dirname(HERE), 'recon', 'sc_1775_traced.json')
KX, KY = 92.83, 110.9
RES = {'Marion': (-80.55, -80.05, 33.40, 33.70), 'Moultrie': (-80.15, -79.90, 33.20, 33.40), 'Wateree': (-80.95, -80.75, 34.30, 34.50),
       'Wylie': (-81.15, -80.95, 35.00, 35.25), 'Murray': (-81.60, -81.15, 34.00, 34.15), 'Greenwood': (-82.15, -81.90, 34.15, 34.35),
       'Thurmond': (-82.60, -82.10, 33.60, 34.05), 'Russell': (-82.85, -82.55, 34.00, 34.30), 'Hartwell': (-83.10, -82.75, 34.35, 34.65),
       'Keowee': (-83.00, -82.85, 34.70, 35.00), 'Parr': (-81.40, -81.30, 34.25, 34.40), 'Fishing Creek': (-80.95, -80.85, 34.55, 34.70)}
EXTRA = [   # name, M(x, y) on the half-resolution crop, (lon, lat), sd_km, source
    ('Camden (court house)', (3447, 1164), (-80.60403, 34.23422), 3.0, 'workbook SCP15 (HMdb 23390)'),
    ('Orangeburg (court house)', (3311, 2186), (-80.87222, 33.50333), 1.5, 'workbook SCP12'),
    ('Charles Town (the walled town)', (4054, 3024), (-79.9311, 32.7765), 1.0, 'Broad and Meeting Streets (S117)'),
    ('Georgetown', (4764, 2214), (-79.29389, 33.37444), 3.0, 'workbook SCP09'),
    ('Dorchester', (3877, 2805), (-80.1719, 32.9495), 1.5, 'workbook SCP10'),
    ('Beaufort', (3455, 3452), (-80.6698, 32.4316), 1.0, 'the town (workbook SCP08: 32.433, -80.683)'),
    ('Long Bluff (Cheraws court house)', (4337, 846), (-79.838, 34.508), 3.0, 'SC marker Long Bluff, Society Hill: the site 3/4 mile east, on the Pee Dee'),
    # Seam ties. Without the Pee Dee pairs the upper right section has nothing to hold its lower edge, and the Pee Dee and Little Pee Dee
    # came out 15 and 9 km from where the lower right section (held by the meetings of the rivers and Winyah Bay) carries on. Each river's
    # last point above the gap at crop y 1222 is tied to where the lower section puts its first point below it (some 2 km on).
    ('Pee Dee at the seam (tie)', (4594, 1199), (-79.674, 34.240), 2.5, 'the lower right section: crop (4580, 1242)'),
    ('Little Pee Dee at the seam (tie)', (4834, 1182), (-79.306, 34.255), 2.5, 'the lower right section: crop (4828, 1242)'),
]
DROP = ['riv-peedee', 'riv-littlepeedee', 'riv-waccamaw', 'riv-black']
SMOOTH = {'UL': 40.0, 'LL': 40.0, 'UR': 200.0, 'LR': 200.0}


def main():
    F = json.load(open(FITF)); TR = json.load(open(TRF))
    if 'pairs_icp' not in F: F['pairs_icp'] = F['pairs']
    if 'PC_session4' not in F: F['PC_session4'] = F['PC']
    npc = len(F['PC_session4']); P = F['pairs_icp']
    extra = [[list(m), [round((ll[0] + 81.0) * KX, 4), round((ll[1] - 33.5) * KY, 4)], sd] for _, m, ll, sd, _ in EXTRA]
    F['PC'] = F['PC_session4'] + [{'name': n, 'm': list(m), 'lonlat': list(ll), 'sd_km': sd, 'source': src, 'added': '2026-11-26'} for n, m, ll, sd, src in EXTRA]
    pts, own = [], []
    for k, v in TR.items():
        if v['kind'] in ('river', 'shore', 'boundary'):
            fam = k.rsplit('-', 1)[0] if k[-1].isdigit() else k
            for p in v['line']: pts.append(p); own.append(fam)
    T = cKDTree(pts)
    def fam(m): d, i = T.query(m); return own[i] if d < 15 else '?'
    def inres(g):
        lon = g[0] / KX - 81.0; lat = g[1] / KY + 33.5
        return any(a <= lon <= b and c <= lat <= d for a, b, c, d in RES.values())
    keep = P[:npc] + extra + [p for p in P[npc:] if not inres(p[1]) and fam(p[0]) not in DROP]
    F['pairs'] = keep; F['smoothing'] = SMOOTH
    F['refit'] = {'date': '2026-11-26', 'pairs_icp': len(P), 'pairs': len(keep), 'dropped_reservoirs': sorted(RES), 'dropped_rivers': DROP,
                  'why': 'Session 4 fit folded the map along some lines (the road to Charlotte turned back on itself); see sc_mouzon_refit_2026_11_26.py.'}
    json.dump(F, open(FITF, 'w'))
    print('pairs', len(P), '->', len(keep))


if __name__ == '__main__':
    main()
