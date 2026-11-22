"""Manila: the ground south of Malate, from "Manila y sus arrabales" (War Department, 1898), taken from the scan by program.

  python3 pipeline/recon/manila_1898_linework.py <scan.jpg> [--preview out.png]

Writes pipeline/recon/manila_1898_detail.json: the ink lines of the sheet's southern part as pixel coordinates on the 4,551 x 7,118
scan (Yale Digital Collections image 15249769). pipeline/recon/manila_1899.py places them with the sheet's fit
(pipeline/georef/manila_arrabales_fit.json) and keeps those south of where the engineer map of 1899 stops.

The method is that of manila_1899_linework.py (dark ink, small separate marks dropped, thinned, followed, simplified), with sizes
three times larger because this scan is that much finer. The sheet is a black print with no water wash, so no water is taken. What
the lines hold: roads, field and property lines, the estero behind Malate, the old Spanish line of works from the fort on the beach
by blockhouses 14 and 13 (its teeth are on the line), and the trenches the Americans dug south of it in August 1898, which someone
drew on the sheet by hand. The marsh signs, trees, houses and nearly all lettering fall out by size. Nobody has checked the result.
"""
import sys, os, json
import numpy as np, cv2
from skimage.morphology import skeletonize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manila_1899_linework as L

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'manila_1898_detail.json')
PICKS = json.load(open(os.path.join(HERE, 'manila_1899_picks.json')))
# the drawn ground from Malate south: inside the neat line as far as it goes, then the strip drawn below it
DRAWN = [(2450, 4300), (4118, 4300), (4118, 5215), (4470, 5215), (4470, 6960), (3300, 6960), (2450, 4700)]
WORDS = [(3220, 5200, 3335, 5265), (3820, 5690, 3880, 5840), (4150, 5760, 4215, 5910), (2880, 5110, 3010, 5260)]   # Cemetery, Swamp, Swamp, a pencilled note on guns

if __name__ == '__main__':
    im = cv2.imread(sys.argv[1]); assert im is not None and im.shape[:2] == (7118, 4551), 'needs the 4,551 x 7,118 scan'
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(cv2.resize(g, None, fx=0.25, fy=0.25), 41); bg = cv2.resize(bg, (g.shape[1], g.shape[0]))
    m = ((bg.astype(np.int16) - g) > 38).astype(np.uint8) & L.poly_mask(g.shape, DRAWN)
    for x0, y0, x1, y1 in WORDS: m[y0:y1, x0:x1] = 0
    sea = np.zeros(g.shape, np.uint8); s = PICKS['arr_shore']      # west of the traced shore is the bay
    cv2.fillPoly(sea, [np.array([(0, s[0][1] - 400), (s[0][0], s[0][1] - 400)] + s + [(s[-1][0], 7118), (0, 7118)], np.int32)], 1)
    m[cv2.erode(sea, np.ones((25, 25), np.uint8)) > 0] = 0         # the shore line itself stays in
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m, kept, total = L.drop_small(m, side=75, area=40)
    lines = [L.simplify(p, 1.2) for p in L.follow(skeletonize(m > 0)) if len(p) >= 12]
    json.dump({'scan': 'Yale Digital Collections image 15249769, 4551 x 7118', 'lines': lines}, open(OUT, 'w'), separators=(',', ':'))
    print('ink: %d of %d marks kept; %d lines, %d points; %d bytes' % (kept, total, len(lines), sum(len(l) for l in lines), os.path.getsize(OUT)))
    if '--preview' in sys.argv:
        v = im.copy()
        for l in lines: cv2.polylines(v, [np.array(l, np.float32).round().astype(np.int32)], False, (255, 60, 0), 3, cv2.LINE_AA)
        cv2.polylines(v, [np.array(s, np.int32)], False, (0, 0, 255), 3)
        for k in PICKS['arr_blockhouses'].values(): cv2.circle(v, tuple(k), 22, (255, 0, 200), 3)
        cv2.polylines(v, [np.array(PICKS['arr_road_real'], np.int32)], False, (0, 160, 0), 3)
        cv2.imwrite(sys.argv[sys.argv.index('--preview') + 1], cv2.resize(v[4250:6980, 2400:4500], None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 82])
