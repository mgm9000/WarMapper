"""Manila, Feb 1899: the Signal Corps map (S64) south of the Pasig, tied to the ground again.

  python3 pipeline/georef/manila_georef_south.py        prints the fit, what is left at each point, and two checks

Why. manila_georef.py puts the whole sheet on the ground with one affine fit through nine churches and landmarks (171 m rms). The sheet
is a sketch, and south of the city that fit fails: it puts the map's own Pasay 1.3 km south-east of Pasay, and its San Pedro Macati
300 m from the church. The troop lines the map draws there (the line "on the Pasay road" of the evening of 5 February) were read off
the map correctly and then carried to the wrong ground.

How. A second fit for the part of the sheet south of the Pasig only: a smoothed thin-plate spline through the places below, which bends
between them as a sketch needs. Five are the churches and landmarks of the first fit (Wikidata, S73). Five are places the War
Department's 1898 plan (S79) or today's streets fix: the fort on the beach at Malate, blockhouses 13 and 14, the cross roads at Pasay,
and the place the road from Pasay meets the beach (those five as S79 places them: pipeline/georef/manila_arrabales_fit.py). San Pedro
Macati church is taken from the map's own town block, not from where the first fit would put it.
Pixel picks are good to 25-75 px (60-190 m). What a row gains is that it is right against the places near it; nothing here makes a
sketch into a survey, and rows placed with it are good to about 200 m.

Rows that were read from the sheet keep their reading: their old coordinates are turned back into scan pixels by the first fit
(which is how they were made) and then carried to the ground by this one.
"""
import sys, os, math, json
import numpy as np
from scipy.interpolate import RBFInterpolator
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'recon'))
import manila_georef as W

# (name, scan x, scan y, lon, lat, where the ground place is from)
CP = [('Baluarte de San Diego', 5081, 3375, 120.976, 14.5854, 'S73 (Wikidata Q18708349)'),
      ('Paco cemetery', 5148, 2798, 120.9888, 14.58132, 'S73 (Wikidata Q7123089)'),
      ('Santa Ana church', 5150, 1770, 121.013764, 14.581953, 'S73 (Wikidata Q16933257)'),
      ('Malacanang Palace', 4625, 2590, 120.994524, 14.593857, 'S73 (Wikidata Q942688)'),
      ('Paranaque church', 8556, 2700, 120.992, 14.5002, 'S73 (Wikidata Q2385428)'),
      ('San Pedro Macati church (the town block on the river)', 5635, 1035, 121.03137, 14.5659, 'S73 (Wikidata); the block read from the scan'),
      ('Malate Fort', 5850, 2880, 120.986526, 14.564271, 'S79: the fort on the beach'),
      ('Blockhouse 13', 5720, 2500, 120.998369, 14.565814, 'S79: the work pencilled 13'),
      ('Blockhouse 14', 5820, 2520, 120.996897, 14.563024, 'S79: the work pencilled 14'),
      ('Pasay cross roads', 7030, 2200, 121.000118, 14.54677, 'S79: the cross roads by the church, slid to today\'s streets'),
      ('The road from Pasay at the beach', 7020, 2600, 120.99303, 14.545534, 'S79: where its road from Pasay church meets the shore')]
SMOOTH = 2.0e4
_P = np.array([(c[1], c[2]) for c in CP], float); _E = np.array([((c[3] - W.LON0) * W.KX, (c[4] - W.LAT0) * W.KY) for c in CP])
_F = RBFInterpolator(_P, _E, kernel='thin_plate_spline', smoothing=SMOOTH)
SOUTH_OF = 4950          # scan x: the sheet has north to the left, so larger x is further south. Rows read at x >= this are re-placed


def px2ll(x, y):
    e, n = _F(np.array([[x, y]], float))[0]; return W.LAT0 + n / W.KY, W.LON0 + e / W.KX


def replace(lat, lon):
    """A coordinate made by the first fit -> the same reading by this fit, if it lies in the southern part; else None."""
    x, y = W.ll2px(lat, lon)
    if x < SOUTH_OF: return None
    la, lo = px2ll(x, y); return round(la, 6), round(lo, 6)


def left_over():
    out = []
    for i, c in enumerate(CP):
        la, lo = px2ll(c[1], c[2]); d = math.hypot((lo - c[3]) * W.KX, (la - c[4]) * W.KY)
        keep = [j for j in range(len(CP)) if j != i]; f = RBFInterpolator(_P[keep], _E[keep], kernel='thin_plate_spline', smoothing=SMOOTH)
        e, n = f(_P[i:i + 1])[0]; loo = math.hypot(e - _E[i, 0], n - _E[i, 1])
        la0, lo0 = W.px2ll(c[1], c[2]); old = math.hypot((lo0 - c[3]) * W.KX, (la0 - c[4]) * W.KY)
        out.append((c[0], round(d), round(loo), round(old)))
    return out


if __name__ == '__main__':
    r = left_over()
    print('%-56s %8s %12s %10s' % ('place', 'left over', 'if left out', 'first fit'))
    for name, d, loo, old in r: print('%-56s %6d m %10d m %8d m' % (name, d, loo, old))
    print('rms %.0f m; leaving each out in turn %.0f m; the first fit at these places %.0f m' % tuple(math.sqrt(sum(v[k] ** 2 for v in r) / len(r)) for k in (1, 2, 3)))
