"""Manila: the city in fine detail, from "Manila y sus arrabales" (War Department, 1898): the plan's own ink, lifted off its paper.

  python3 pipeline/recon/manila_1898_ink.py <scan.jpg> [--preview out.jpg]

Writes playbacks/manila/manila-1898-ink.webp, the same at a half and a quarter of the size (-2, -4: the page shows the small ones first
and fetches the full one only when the reader comes close, as a map of the time printed at three scales would), and
pipeline/recon/manila_1898_ink.json (where the picture's corners fall on the ground).

The reconstructed map's own lines are too few for a reader who zooms right in: the engineer map of 1899 they come from was read at
3.6 m a pixel. This plan of the city was scanned at 1.36 m a pixel (Yale Digital Collections image 15249769, 4,551 x 7,118) and draws
every street, block and public building, with the street names. So for the closest zooms the page lays the plan's ink itself over the
reconstruction: every dark mark of the print, kept as it is (lines at their own width, lettering, building numbers, trees and marsh
signs), with the paper made clear so the reconstruction's paper, water and relief show between the lines. Nothing is redrawn.

What is taken: the city as surveyed, inside the neat line, from the top of the sheet to where the engineer map stops (sheet y 4470;
below that the sheet is a hand-drawn strip that does not fall on the ground, and pipeline/recon/manila_1898_linework.py takes its
lines one by one). Left out: the title, the three keys to numbered buildings, the inset and the margins.

Where it falls: by the sheet's fit to the engineer map (pipeline/georef/manila_arrabales_fit.json: 31,292 matched points, median 5.7 m,
nine in ten within 10.5 m). North of the seam that fit is a plain affine placing, so the picture is laid down by its four corners.
It is the city of 1898, six months before the battle. Nobody has checked it mark by mark.

It also says which of the engineer map's own lines (pipeline/recon/manila_1899_detail.json) this plan draws too, in finer detail: a
line of which seven points in ten lie within 16 m of the plan's ink. Those lines give way to the plan at the closest zooms, so a street
edge is not drawn twice a few metres apart; the engineer map's other lines (dykes, field lines, trenches the plan does not have) stay.
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manila_1899 as M

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
ARR = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'manila_arrabales_fit.json')))
OUT = os.path.join(ROOT, 'playbacks', 'manila', 'manila-1898-ink.webp'); META = os.path.join(HERE, 'manila_1898_ink.json')
BOX = (810, 410, 4092, 4470)                      # left, top, right, bottom on the scan: inside the neat line, down to the seam
LEFT_OUT = [(2790, 760, 4092, 1300),              # the title
            (1190, 3490, 1975, 4335),             # key: Edificios militares
            (810, 4300, 2345, 4470)]              # keys: Edificios civiles, Edificios religiosos (their top edge)
INK = (0x33, 0x29, 0x1f)                          # the reconstruction's ink (--rc-ink)
FADE = 70                                         # the picture fades out over its last pixels at the seam, where the traced lines take over


def ground(x, y):
    A = np.array(ARR['affine']); e, n = A @ np.array([x, y, 1.0])
    return [round(float(ARR['lon0'] + e / ARR['kx']), 6), round(float(ARR['lat0'] + n / ARR['ky']), 6)]


def to_sheet(ll):
    """Ground (longitude, latitude) -> pixels of the 1898 scan, north of the seam: the fit turned round."""
    A = np.array(ARR['affine']); q = np.array(ll, float); en = np.c_[(q[:, 0] - ARR['lon0']) * ARR['kx'], (q[:, 1] - ARR['lat0']) * ARR['ky']]
    return (np.linalg.inv(A[:, :2]) @ (en - A[:, 2]).T).T


if __name__ == '__main__':
    im = cv2.imread(sys.argv[1]); assert im is not None and im.shape[:2] == (7118, 4551), 'needs the 4,551 x 7,118 scan'
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    bg = cv2.medianBlur(cv2.resize(g, None, fx=0.25, fy=0.25), 41); bg = cv2.resize(bg, (g.shape[1], g.shape[0]))   # the paper, without the ink
    d = bg.astype(np.float32) - g                                    # how much darker than the paper
    a = np.clip((d - 24.0) / 46.0, 0, 1); a = a * a * (3 - 2 * a)    # clear below 24 grey levels, full ink from 70
    solid = (d > 38).astype(np.uint8)                                # specks: separate marks of under 5 pixels are dust, not print
    n, lab, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    dust = np.isin(lab, np.where(st[:, cv2.CC_STAT_AREA] < 5)[0]); near = cv2.dilate(solid & ~dust.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    a[~near] = 0                                                     # only ink within two pixels of a real mark is kept (soft edges stay)
    for x0, y0, x1, y1 in LEFT_OUT: a[y0:y1, x0:x1] = 0
    x0, y0, x1, y1 = BOX; a = a[y0:y1, x0:x1].copy()
    a[-FADE:] *= np.linspace(1, 0, FADE)[:, None]
    rgba = np.zeros(a.shape + (4,), np.uint8); rgba[..., 0], rgba[..., 1], rgba[..., 2] = INK; rgba[..., 3] = (a * 255).round()
    Image.fromarray(rgba, 'RGBA').save(OUT, 'WEBP', lossless=True, method=6, exact=True)
    files = []                                                       # [from this zoom, file]: the smallest first
    for div, zoom in ((4, 13.6), (2, 14.7)):
        w, h = (x1 - x0) // div, (y1 - y0) // div; s = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
        s = np.clip(s ** 0.72 * 1.12, 0, 1)                          # a thin line reduced goes pale: it is inked back in, as an engraver would for the smaller scale
        r = np.zeros((h, w, 4), np.uint8); r[..., 0], r[..., 1], r[..., 2] = INK; r[..., 3] = (s * 255).round(); name = OUT.replace('.webp', '-%d.webp' % div)
        Image.fromarray(r, 'RGBA').save(name, 'WEBP', lossless=True, method=6, exact=True); files.append([zoom, os.path.basename(name)])
    files.append([15.7, os.path.basename(OUT)])
    corners = [ground(x0, y0), ground(x1, y0), ground(x1, y1), ground(x0, y1)]                # top-left, top-right, bottom-right, bottom-left
    # the engineer map's lines that this plan draws too
    far = cv2.distanceTransform((a < 0.5).astype(np.uint8), cv2.DIST_L2, 5); H = M.haan(); gate = 16.0 / ARR['m_per_px'][0]; twice = []
    for i, line in enumerate(M.DETAIL['lines']):
        px = to_sheet(H(line)) - (x0, y0); ok = (px[:, 0] >= 0) & (px[:, 1] >= 0) & (px[:, 0] < a.shape[1] - 1) & (px[:, 1] < a.shape[0] - FADE)
        if ok.mean() < 0.999: continue                                                           # only lines wholly under the picture
        if len(px) < 8:                                                                          # a short line: test points every few metres along it
            seg = np.linspace(0, len(px) - 1, 12); px = np.c_[np.interp(seg, range(len(px)), px[:, 0]), np.interp(seg, range(len(px)), px[:, 1])]
        if (far[px[:, 1].round().astype(int), px[:, 0].round().astype(int)] <= gate).mean() >= 0.7: twice.append(i)
    meta = {'scan': ARR['scan'], 'file': os.path.relpath(OUT, ROOT), 'files': files, 'box_px': list(BOX), 'size': [x1 - x0, y1 - y0], 'corners': corners,
            'm_per_px': ARR['m_per_px'], 'left_out_px': [list(r) for r in LEFT_OUT], 'ink_share': round(float((a > 0.5).mean()), 4),
            'fit': {'matched_points': ARR['matched_points'], 'median_m': ARR['median_m'], 'p90_m': ARR['p90_m']},
            'engineer_lines_drawn_here_too': {'gate_m': 16, 'share_of_points': 0.7, 'lines': twice}}
    json.dump(meta, open(META, 'w'), separators=(',', ':'))
    print('%s: %d x %d, %d bytes, ink on %.1f%% of it; corners %s' % (os.path.basename(OUT), x1 - x0, y1 - y0, os.path.getsize(OUT), 100 * meta['ink_share'], corners))
    print('sizes: ' + ', '.join('%s from zoom %s (%d bytes)' % (f, z, os.path.getsize(os.path.join(os.path.dirname(OUT), f))) for z, f in files))
    print('engineer-map lines this plan draws too: %d of %d' % (len(twice), len(M.DETAIL['lines'])))
    if '--preview' in sys.argv:
        paper = np.full(a.shape + (3,), (184, 217, 231), np.float32); v = paper * (1 - a[..., None]) + np.array(INK[::-1], np.float32) * a[..., None]
        cv2.imwrite(sys.argv[sys.argv.index('--preview') + 1], v[1700:2600, 900:2100].astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 85])
