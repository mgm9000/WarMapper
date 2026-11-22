"""Fit of "Manila y sus arrabales" (War Department, 1898; Yale image 15249769, 4,551 x 7,118 px) to the ground.

  python3 pipeline/georef/manila_arrabales_fit.py <scan.jpg>      writes pipeline/georef/manila_arrabales_fit.json and prints the fit

The sheet's border is divided into numbered parts (16, 17, 18 down the east side), not into degrees, so it cannot place the sheet on the
ground. It is placed instead on the ground of the engineer map of 1899 (S78, pipeline/georef/manila_haan_fit.json), which shows
the same city six months later:

  1. A first placing from two landmarks both maps draw as rings: the Bilibid prison and the Paco cemetery.
  2. Then the street lines of the two maps are matched. The ink lines of this sheet (thinned to centre lines) are carried to the ground
     by the placing so far; each point takes the nearest ink line of the engineer map, if one lies within a gate; an affine placing is
     fitted to the pairs; and so on, the gate closing from 45 m to 12 m.
  The result is an affine placing (a shift, a turn, a scale and a shear). What is left over at the matched points, and at the two rings
  (which the second step does not use), says how good it is. South of Malate there is nothing to match against: there the placing is
carried on from the north. One check does not depend on the engineer map: someone has pencilled on the sheet that one border division
is 1.37 miles, and by this fit it is 1.373 miles.

  3. The south. Below Malate the sheet stops being a survey: the strip to Pasay was drawn on it by hand in 1898. Carried on by the
     placing above, it does not fall on today's ground. Two things can be measured against streets that are still there (from the
     OpenStreetMap extract, data/osm/manila.txt):
       - Its Calle Real, the double line nearest the shore, runs a steady 115 to 126 m east of today's F. B. Harrison Street (the same
         road) all the way from sheet y 5533 to y 6900.
       - Its crossing of Calle Real and the road to Pasay church (y 6760) falls 287 m south-east of today's F. B. Harrison Street x
         A. Arnaiz Avenue: 110 m across the road and about 255 m along it.
     So south of where the engineer map stops (sheet y 4470) every point is slid, by an amount that depends only on how far south it
     is. The slide across the road grows evenly from nothing at y 4470 to its full 120 m at y 5533 and stays; the slide along the road
     grows evenly from nothing at y 4470 to 255 m at y 6760. Beyond y 6760 the slide stays as it is there.
     What this rests on: that the sheet's Calle Real is today's F. B. Harrison Street, and its road to Pasay church today's A. Arnaiz
     Avenue. Between Malate and Pasay nothing fixes how far along the road a point lies, so it may be 150 m out that way.
     A second crossing was tried and left out: if the sheet's dashed road is today's Pablo Ocampo Street, it gives a slide 70 m
     different from this one; nothing on the sheet says that it is. Features placed this way are low confidence.
"""
import sys, os, json, math
import numpy as np, cv2
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'recon'))
import manila_1899 as M

FIT = M.FIT; H = M.haan()
en = lambda ll: np.array([[(lo - FIT['lon0']) * FIT['kx'], (la - FIT['lat0']) * FIT['ky']] for lo, la in ll])
RINGS = [('Bilibid prison, centre of the ring', (2702.5, 1849.4), (997.9, 1704.0)), ('Paco cemetery, centre of the ring', (3138.0, 3758.0), (1162.8, 2405.2))]   # this sheet px, engineer map px
FRAME = (810, 400, 4215, 5210)        # the drawn city inside the neat line (x0, y0, x1, y1); the strip south of it is not used for the fit
SEAM_Y = 4470                         # where the engineer map stops (its south edge, about 14.573 N)
CROSSING = ("Calle Real x the road to Pasay church; today F. B. Harrison Street x A. Arnaiz Avenue", (3745, 6760), (120.99387, 14.54613))   # sheet px, today's place (OpenStreetMap)
ACROSS = (5533, (-116.0, -38.0))      # at this y and south of it: from the sheet's Calle Real to the nearest point of today's F. B. Harrison Street, in metres east and north (mean of five picks, 115 to 126 m)
PARTS = (2016, 3635)                 # the border's numbered divisions "18" and "17" on the east side (y, to about 5 px). A pencil note on the sheet gives one division as 1.37 miles


def ink(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(cv2.resize(g, None, fx=0.25, fy=0.25), 41); bg = cv2.resize(bg, (g.shape[1], g.shape[0]))
    return ((bg.astype(np.int16) - g) > 60).astype(np.uint8)


def main(scan):
    im = cv2.imread(scan); assert im is not None and im.shape[:2] == (7118, 4551), 'needs the 4,551 x 7,118 scan'
    m = ink(im); x0, y0, x1, y1 = FRAME; keep = np.zeros_like(m); keep[y0:y1, x0:x1] = 1; m &= keep
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    big = np.maximum(st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT]); ok = big >= 120; ok[0] = False     # streets hang together; lettering and tree dots do not
    sk = skeletonize(ok[lab]); ys, xs = np.nonzero(sk); P = np.stack([xs, ys], 1)[::4].astype(float)
    # the engineer map's ink lines on the ground, a point every 3 m or so
    T = []
    for line in M.DETAIL['lines']:
        q = en(H(line))
        for a, b in zip(q, q[1:]):
            k = max(1, int(np.hypot(*(b - a)) / 3)); T.extend(a + (b - a) * np.arange(k)[:, None] / k)
    T = np.array(T); tree = cKDTree(T)
    # 1: two rings -> a turn, a scale and a shift (y of the sheet runs south)
    g = en(H([r[2] for r in RINGS])); a = np.array([r[1] for r in RINGS])
    z = lambda p: complex(p[0], -p[1]); c = (complex(*g[1]) - complex(*g[0])) / (z(a[1]) - z(a[0])); d = complex(*g[0]) - c * z(a[0])
    A = np.array([[c.real, c.imag, d.real], [c.imag, -c.real, d.imag]])       # ground = A . (x, y, 1)
    first = (abs(c), math.degrees(math.atan2(c.imag, c.real)))
    hom = np.c_[P, np.ones(len(P))]
    for gate in (45, 35, 25, 18, 12, 12, 12):
        G = hom @ A.T; dist, idx = tree.query(G); use = dist < gate
        A = np.linalg.lstsq(hom[use], T[idx[use]], rcond=None)[0].T
    G = hom @ A.T; dist, idx = tree.query(G); use = dist < 12
    ring = [float(np.hypot(*(np.array([*r[1], 1]) @ A.T - gg))) for r, gg in zip(RINGS, g)]
    sx, sy = np.hypot(A[0, 0], A[1, 0]), np.hypot(A[0, 1], A[1, 1]); turn = math.degrees(math.atan2(A[1, 0], A[0, 0]))
    part_m = (PARTS[1] - PARTS[0]) * sy
    out = {'scan': 'Yale Digital Collections image 15249769, 4551 x 7118', 'affine': [[round(v, 8) for v in row] for row in A], 'lon0': FIT['lon0'], 'lat0': FIT['lat0'], 'kx': FIT['kx'], 'ky': FIT['ky'],
           'rings': [{'what': r[0], 'sheet_px': r[1], 'engineer_px': r[2], 'left_over_m': round(e, 1)} for r, e in zip(RINGS, ring)],
           'matched_points': int(use.sum()), 'of_points': int(len(P)), 'median_m': round(float(np.median(dist[use])), 1), 'p90_m': round(float(np.percentile(dist[use], 90)), 1),
           'm_per_px': [round(sx, 4), round(sy, 4)], 'turn_deg': round(turn, 2), 'first_placing': {'m_per_px': round(first[0], 4), 'turn_deg': round(first[1], 2)},
           'border_division': {'px': PARTS[1] - PARTS[0], 'm_by_this_fit': round(part_m), 'miles_by_this_fit': round(part_m / 1609.344, 3), 'pencil_note_on_sheet_miles': 1.37}}
    what, px, (lon, lat) = CROSSING
    e, n_ = np.array([*px, 1.0]) @ A.T; full = np.array([(lon - FIT['lon0']) * FIT['kx'] - e, (lat - FIT['lat0']) * FIT['ky'] - n_])     # the whole slide at the Pasay crossing
    across = np.array(ACROSS[1]); along = full - across                                    # what is left is along the road
    part = (ACROSS[0] - SEAM_Y) / (px[1] - SEAM_Y)
    out['south'] = {'seam_y': SEAM_Y, 'crossing': {'what': what, 'sheet_px': px, 'today': [lon, lat], 'apart_m': round(float(np.hypot(*full)))},
                    'across_road_m': round(float(np.hypot(*across))), 'along_road_m': round(float(np.hypot(*along))),
                    'slides': [{'y': ACROSS[0], 'slide_m': [round(float(v), 1) for v in across + along * part]}, {'y': px[1], 'slide_m': [round(float(v), 1) for v in full]}]}
    json.dump(out, open(os.path.join(HERE, 'manila_arrabales_fit.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'affine'}, indent=1))
    return A, P, G, use, T


if __name__ == '__main__':
    main(sys.argv[1])
