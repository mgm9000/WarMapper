"""Manila, Feb 1899: Warking's Signal Corps map (LoC G8064.M5 1899 .W3, digital id g8064m ct002453) tied to the ground.

The scan (11,533 x 7,657 px, LoC IIIF) is a blue-line photocopy, "Oriented with North to the left". Nine places that are on the map
and still stand (or whose church stands where the 1899 town plaza was) were matched to their coordinates on Wikidata (read 20 Nov 2026),
and an affine fit (shift, turn, scale and shear) was taken through them by least squares. Pixel picks were read from crops of the
full-resolution scan with a 25-100 px grid drawn over them; a town block or church symbol is good to about 25-75 px (40-200 m).

  python3 pipeline/georef/manila_georef.py        prints the fit and the residual at each point
"""
import math
import numpy as np

W, H = 11533, 7657
# (name, scan x, scan y, lon, lat, Wikidata id, how the pixel was read)
CP = [
    ('Baluarte de San Diego (south corner of the Walled City)', 5081, 3375, 120.976, 14.5854, 'Q18708349', 'corner of the wall outline'),
    ('Paco cemetery (Paco Park)', 5148, 2798, 120.9888, 14.58132, 'Q7123089', 'small circle beside "Cemetery"'),
    ('San Juan del Monte (Santuario del Santo Cristo)', 4300, 934, 121.030556, 14.598333, 'Q17001741', 'town block'),
    ('Santa Ana church', 5150, 1770, 121.013764, 14.581953, 'Q16933257', 'town block east of the road'),
    ('Caloocan church', 2154, 3434, 120.97283, 14.65167, 'Q5023169', 'church symbol'),
    ('Paranaque church', 8556, 2700, 120.992, 14.5002, 'Q2385428', 'church symbol'),
    ('Las Pinas church', 9360, 3300, 120.981556, 14.481167, 'Q4348943', 'town block'),
    ('Malabon church', 1819, 4319, 120.951412, 14.658882, 'Q25052019', 'church symbol'),
    ('Malacanang Palace', 4625, 2590, 120.994524, 14.593857, 'Q942688', 'telegraph station marked "Malacanan"'),
]
LAT0 = sum(c[4] for c in CP) / len(CP); LON0 = sum(c[3] for c in CP) / len(CP)
KX = 111320 * math.cos(math.radians(LAT0)); KY = 110574
_P = np.array([(c[1], c[2], 1.0) for c in CP]); _E = np.array([((c[3] - LON0) * KX, (c[4] - LAT0) * KY) for c in CP])
_CX = np.linalg.lstsq(_P, _E[:, 0], rcond=None)[0]; _CY = np.linalg.lstsq(_P, _E[:, 1], rcond=None)[0]
_M = np.array([[_CX[0], _CX[1]], [_CY[0], _CY[1]]]); _T = np.array([_CX[2], _CY[2]])


def px2ll(x, y):
    """Scan pixel -> (lat, lon)."""
    e, n = _M @ np.array([x, y]) + _T
    return LAT0 + n / KY, LON0 + e / KX


def ll2px(lat, lon):
    e = (lon - LON0) * KX; n = (lat - LAT0) * KY
    x, y = np.linalg.solve(_M, np.array([e, n]) - _T)
    return float(x), float(y)


def residuals():
    out = []
    for c in CP:
        la, lo = px2ll(c[1], c[2]); out.append((c[0], round(math.hypot((lo - c[3]) * KX, (la - c[4]) * KY))))
    return out


def corners():
    """tl, tr, br, bl of the whole scan as (lat, lon)."""
    return [px2ll(0, 0), px2ll(W, 0), px2ll(W, H), px2ll(0, H)]


if __name__ == '__main__':
    r = residuals(); rms = math.sqrt(sum(d * d for _, d in r) / len(r))
    sx = math.hypot(_M[0, 0], _M[1, 0]); sy = math.hypot(_M[0, 1], _M[1, 1])
    print('affine fit on %d points: RMS %.0f m, max %d m; %.2f m/px along x, %.2f along y; x axis points %.0f deg from east' % (
        len(r), rms, max(d for _, d in r), sx, sy, math.degrees(math.atan2(_M[1, 0], _M[0, 0]))))
    for n, d in r: print('  %-55s %4d m' % (n, d))
    print('corners', [tuple(round(v, 6) for v in c) for c in corners()])
