"""Manila, February 1899: the engineer map's own ink lines and water tint, taken from the scan by program.

  python3 pipeline/recon/manila_1899_linework.py <scan.jpg> [--preview out.png]

Writes pipeline/recon/manila_1899_detail.json: pixel coordinates on the 3,840 x 2,847 copy of the Haan map (National Archives 109182890),
the same copy the hand picks were read from. pipeline/recon/manila_1899.py turns them into ground coordinates with the map's fit.
The scan is not in the repository: fetch it, then run this.

What it does (method "AI-extracted": separated by a program; nobody has checked the result line by line).

  Ink lines ("lines"). Every dark pixel that is not coloured (the yellow unit lettering and the red quarters dots are left out by colour),
  inside the drawn part of the sheet (the title, the legend, the compass and the scale bar are masked). Small separate marks are dropped:
  that removes most lettering, the dots of trails and city limits, and the little rings of hedges. What is left is thinned to centre
  lines, followed pixel by pixel into lines, and simplified to 0.6 px (about 2 m). So the result holds street and block edges, dykes,
  fences, river banks, the walls and their outworks, the railway, and the hachures of the hills east of the San Juan. It also holds what
  the program cannot tell apart from them: letters that touch a line, larger lettering, and the trench lines the engineers drew after
  the battle (those are cut out along a hand-drawn corridor, TRENCH below, because they are not ground of 4 February).

  Water ("water"). The pale blue wash, as in manila_1899_water.md, over the whole sheet at one threshold, less what the hand-checked
  layers already hold (the Pasig, the moat, the Tondo lagoons, the bay). These are the esteros, creeks and ponds.
"""
import sys, os, json
import numpy as np, cv2
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'manila_1899_detail.json')
PICKS = json.load(open(os.path.join(HERE, 'manila_1899_picks.json')))

# the drawn part of the sheet (scan px): everything else is title, legend, compass, scale bar or margin
DRAWN = [(236, 96), (1640, 96), (1640, 650), (2260, 650), (2260, 1240), (3740, 1240), (3740, 1760), (2520, 1760), (2520, 2652), (236, 2652)]
# lettering too large to fall out by size: boxes around it (x0, y0, x1, y1)
LETTERS = [(430, 330, 640, 400),        # CALOOCAN
           (2000, 1330, 3200, 1420),    # Rolling Land
           (2500, 1640, 2900, 1740)]    # Rolling Land (south)
# the American trench line of 5 to 28 February and its lettering (AMERICAN INTRENCHMENTS), drawn after the battle: a corridor along it
TRENCH = [[(742, 130), (790, 290), (880, 500), (1000, 640), (1075, 700)],                       # Montana, 3d Artillery
          [(1075, 700), (1140, 830), (1260, 960), (1280, 1060), (1420, 1150), (1630, 1250), (1790, 1340), (1810, 1420)],   # Pennsylvania, South Dakota, Colorado
          [(1810, 1420), (1860, 1500), (1950, 1600), (2050, 1660)]]
TRENCH_WIDE = 46        # px either side: the lettering runs beside the line


def poly_mask(shape, pts):
    m = np.zeros(shape, np.uint8); cv2.fillPoly(m, [np.array(pts, np.int32)], 1); return m


def bay_mask(shape):
    """West of the traced shore, and outside the jetty."""
    shore = PICKS['shore_n'] + PICKS['shore_s']; m = np.zeros(shape, np.uint8)
    cv2.fillPoly(m, [np.array([(0, 0), (shore[0][0], 0)] + shore + [(shore[-1][0], shape[0]), (0, shape[0])], np.int32)], 1)
    return m


def ink_mask(im):
    b, g, r = [im[:, :, i].astype(np.int16) for i in range(3)]
    lum = (0.114 * b + 0.587 * g + 0.299 * r)
    bg = cv2.medianBlur(cv2.resize(lum.astype(np.uint8), None, fx=0.25, fy=0.25), 41); bg = cv2.resize(bg, (im.shape[1], im.shape[0])).astype(np.int16)
    dark = (bg - lum) > 30                                   # ink against the paper around it
    coloured = ((r - b) > 45) | ((r - g) > 40)               # yellow lettering, red dots, the orange wash on one trench
    m = (dark & ~coloured).astype(np.uint8)
    m &= poly_mask(m.shape, DRAWN)
    for x0, y0, x1, y1 in LETTERS: m[y0:y1, x0:x1] = 0
    m[cv2.dilate(bay_mask(m.shape), np.ones((7, 7), np.uint8)) > 0] = 0      # the bay: its lettering and the lines drawn along the shore (the shore itself is a traced layer)
    t = np.zeros(m.shape, np.uint8)
    for line in TRENCH: cv2.polylines(t, [np.array(line, np.int32)], False, 1, TRENCH_WIDE * 2)
    m[t > 0] = 0
    return m


def drop_small(m, side=30, area=14):
    """Lettering, dots, dashes and hedge rings are small separate marks; streets, banks and dykes hang together."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    w, h, a = st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT], st[:, cv2.CC_STAT_AREA]
    big = np.maximum(w, h)
    keep = (big >= side) | ((big >= 13) & (a <= big * 3.4))      # thin strokes stay (a fence, a bridge, a broken street edge); so do a few letter stems
    keep &= a >= area; keep[0] = False
    return keep[lab].astype(np.uint8), int(keep.sum()), n - 1


def follow(sk):
    """Follow a one-pixel skeleton into lines: from every end or junction along the pixels with two neighbours."""
    H, W = sk.shape; S = sk.astype(bool)
    nb = ndi.convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode='constant') - 1
    node = S & (nb != 2)
    seen = np.zeros_like(S); lines = []
    D = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def nbrs(y, x):
        return [(y + dy, x + dx) for dy, dx in D if 0 <= y + dy < H and 0 <= x + dx < W and S[y + dy, x + dx]]

    ys, xs = np.nonzero(node)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        for q in nbrs(y0, x0):
            if seen[q] and not node[q]: continue
            path = [(y0, x0), q]; prev = (y0, x0); cur = q
            if node[cur]:
                if (y0, x0) < cur: lines.append(path)
                continue
            seen[cur] = True
            while True:
                nx = [p for p in nbrs(*cur) if p != prev and not (seen[p] and not node[p])]
                nodes = [p for p in nx if node[p]]
                if nodes: nx = nodes[:1]
                if not nx: break
                prev, cur = cur, nx[0]; path.append(cur)
                if node[cur]: break
                seen[cur] = True
            lines.append(path)
    # closed loops with no junction (a block standing alone)
    rest = S & ~seen & ~node; lab, n = ndi.label(rest, np.ones((3, 3)))
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 12: continue
        start = (int(ys[0]), int(xs[0])); path = [start]; seen[start] = True; cur = start
        while True:
            nx = [p for p in nbrs(*cur) if not seen[p] and not node[p]]
            if not nx: break
            cur = nx[0]; seen[cur] = True; path.append(cur)
        path.append(start); lines.append(path)
    return lines


def simplify(path, eps=0.6):
    pts = np.array([[x, y] for y, x in path], np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(pts, eps, False)[:, 0, :].round(1).tolist()


def water(im, shape):
    b, r = im[:, :, 0].astype(np.int16), im[:, :, 2].astype(np.int16)
    blur = cv2.GaussianBlur((b - r).astype(np.float32), (0, 0), 2)
    bg = cv2.medianBlur(cv2.resize(blur, None, fx=0.125, fy=0.125).clip(-128, 127).astype(np.int8).view(np.uint8), 51)
    rel = blur - cv2.resize(bg.view(np.int8).astype(np.float32), (im.shape[1], im.shape[0]))
    lum = 0.114 * im[:, :, 0].astype(np.int16) + 0.587 * im[:, :, 1].astype(np.int16) + 0.299 * r
    lbg = cv2.medianBlur(cv2.resize(lum.astype(np.uint8), None, fx=0.25, fy=0.25), 41); lbg = cv2.resize(lbg, (im.shape[1], im.shape[0])).astype(np.int16)
    m = ((rel > 4.5) & ((lbg - lum) < 20)).astype(np.uint8) & poly_mask(shape, DRAWN)      # the wash, not the blue-black ink itself
    have = np.zeros(shape, np.uint8)                       # what the hand-checked layers already hold
    cv2.fillPoly(have, [np.array(PICKS['pasig'], np.int32)], 1)
    for ring in PICKS['moat']: cv2.fillPoly(have, [np.array(ring, np.int32)], 1)
    for rings in PICKS['lagoons']: cv2.fillPoly(have, [np.array(rings[0], np.int32)], 1)
    have |= bay_mask(shape)
    have[:1800, 2330:] = 1        # east of the San Juan the dense hachures read as tint: no water is taken there
    have[:700, :560] = 1          # the lagoon coast north of Vitas: the wash is a band along a shore the Signal Corps map supplies
    have = cv2.dilate(have, np.ones((13, 13), np.uint8))
    m[have > 0] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))      # across the bank lines and bridges
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    m[have > 0] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 90]).astype(np.uint8)
    cs, hier = cv2.findContours(keep, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE); out = []
    if hier is None: return out, keep
    hier = hier[0]
    for i, c in enumerate(cs):
        if hier[i][3] != -1: continue                       # a hole: taken with its parent
        outer = cv2.approxPolyDP(c, 0.8, True)[:, 0, :].tolist()
        if len(outer) < 4: continue
        rings = [outer]; j = hier[i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) >= 40:
                h = cv2.approxPolyDP(cs[j], 0.8, True)[:, 0, :].tolist()
                if len(h) >= 4: rings.append(h)
            j = hier[j][0]
        out.append(rings)
    return out, keep


if __name__ == '__main__':
    scan = sys.argv[1]; im = cv2.imread(scan); assert im is not None and im.shape[:2] == (2847, 3840), 'needs the 3,840 x 2,847 copy'
    m = cv2.morphologyEx(ink_mask(im), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))     # mend one-pixel breaks
    m, kept, total = drop_small(m)
    sk = skeletonize(m > 0)
    raw = follow(sk)
    lines = [simplify(p) for p in raw if len(p) >= 7]          # spurs of a few pixels are noise
    wat, wm = water(im, m.shape)
    json.dump({'scan': '3840 x 2847 copy of National Archives 109182890', 'lines': lines, 'water': wat}, open(OUT, 'w'), separators=(',', ':'))
    print('ink: %d of %d marks kept; %d lines, %d points; water: %d areas; %d bytes' % (kept, total, len(lines), sum(len(l) for l in lines), len(wat), os.path.getsize(OUT)))
    if '--preview' in sys.argv:
        v = np.full(im.shape, 255, np.uint8); v[wm > 0] = (230, 200, 160)
        for l in lines: cv2.polylines(v, [np.array(l, np.float32).round().astype(np.int32)], False, (40, 30, 20), 1, cv2.LINE_AA)
        cv2.imwrite(sys.argv[sys.argv.index('--preview') + 1], v)
