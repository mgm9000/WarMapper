"""Faden's 1777 'Plan of the operations of General Washington' (Boston Public Library, Leventhal Map Center, commonwealth:wd3768583),
fitted to the ground for the Trenton playback.

The engraving is badly out of shape against the ground: fitted as a whole (affine), towns are 1 to 9 km from where they are, and even
inside the area of the battle Pennington and Maidenhead are 3 to 4 km out. So the scan is rubber-sheeted: it is warped smoothly
(a thin-plate spline on 12 towns and crossings) so each of them lands on its real place, the way georeferencing tools such as Allmaps do.
Outside the ring of towns the spline runs on smoothly. Cranbury and Allentown, in the east and outside the
battle, are left out: they are 6.5 and 7 km out on the engraving, and pulling them into place tears that part of the sheet. The result is a picture in Web Mercator, north up, that the
playback lays down by its four corners.

Usage: python3 -I trenton_faden.py SCAN.jpg OUT.webp FIT.json [PIECES [SHEET.jpg]]     (SCAN: the full image from the library's IIIF service, 7551 x 5174)

Rebuilt 18 Nov 2026 from the full scan at 7 m a pixel (it was 12, from a half-size scan, and looked out of focus), in 2 x 2 pieces.
"""
import json, math, sys
import numpy as np
from PIL import Image
from skimage.transform import ThinPlateSplineTransform, warp
Image.MAX_IMAGE_PIXELS = None

# name, scan x, scan y, latitude, longitude: towns at their main crossroads or church as Faden draws them, and two ferries
POINTS = [('Trenton', 3690, 2600, 40.2203, -74.7655), ("McKonkey's Ferry (Pennsylvania side)", 2215, 1700, 40.2958, -74.8737), ('Pennington', 2945, 1110, 40.3286, -74.7905),
          ('Princeton', 5330, 1580, 40.3490, -74.6600), ('Kingston', 5765, 1010, 40.3750, -74.6135), ('Maidenhead (Lawrenceville)', 4755, 1990, 40.2970, -74.7295),
          ('Newtown', 1380, 2565, 40.2293, -74.9368), ('Bordentown', 4265, 3680, 40.1460, -74.7115),
          ('Crosswicks', 4985, 3570, 40.1503, -74.6528), ('Middletown (Langhorne)', 1770, 3390, 40.1745, -74.9227),
          ('Bristol', 2600, 4320, 40.1006, -74.8517), ('Trenton Ferry (Pennsylvania side)', 3530, 2840, 40.2080, -74.7770)]
CROP = (1185, 440, 6430, 4560)        # the engraved border
RES = 7.0                             # metres on the ground per pixel of the picture, at this latitude (the scan has 4.5 to 10)
SHEET_REDUCED = 0.5                   # the unstretched sheet that comes with the page; the library streams the rest
R = 6378137.0


def merc(lon, lat): return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def unmerc(x, y): return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def main(scan, out, fitpath, pieces='2', sheet_out=None):
    """OUT gets a suffix -0, -1, ... per piece (row by row) when PIECES > 1, so no piece is wider than a phone's largest texture (4096).
    SHEET_OUT, if given, is the engraving itself, unstretched, at SHEET_REDUCED of the scan's size: the 1:1 view lays units on it."""
    from scipy.ndimage import zoom, map_coordinates
    n = int(pieces); k = 1 / math.cos(math.radians(40.25)); step = RES * k                      # mercator metres per output pixel
    G = np.array([merc(p[4], p[3]) for p in POINTS]); S = np.array([[p[1], p[2]] for p in POINTS], float)
    A = np.c_[S, np.ones(len(S))]; ax = np.linalg.lstsq(A, G[:, 0], rcond=None)[0]; ay = np.linalg.lstsq(A, G[:, 1], rcond=None)[0]
    misfit = np.hypot(A @ ax - G[:, 0], A @ ay - G[:, 1]) / k
    x0, y0, x1, y1 = CROP; fwd = ThinPlateSplineTransform.from_estimate(S, G)
    edge = np.array([(x, y) for x in np.linspace(x0, x1, 60) for y in (y0, y1)] + [(x, y) for y in np.linspace(y0, y1, 60) for x in (x0, x1)])
    E = fwd(edge); gx0, gx1 = E[:, 0].min(), E[:, 0].max(); gy0, gy1 = E[:, 1].min(), E[:, 1].max()
    W, H = int((gx1 - gx0) / step) + 1, int((gy1 - gy0) / step) + 1
    W += (-W) % n; H += (-H) % n
    O = np.c_[(G[:, 0] - gx0) / step, (gy1 - G[:, 1]) / step]
    t = ThinPlateSplineTransform.from_estimate(O, S)
    im = Image.open(scan).convert('RGB'); img = np.asarray(im)                 # the full scan: no reduction, so the lettering stays sharp
    g = 8; pw, ph = W // n, H // n; corners = []
    for r in range(n):
        for c in range(n):
            ox, oy = c * pw, r * ph
            gc, gr = np.meshgrid(np.arange(ox, ox + pw + g, g), np.arange(oy, oy + ph + g, g))
            src = t(np.c_[gc.ravel(), gr.ravel()]).reshape(gr.shape + (2,))
            fx = zoom(src[:, :, 0], g, order=1)[:ph, :pw]; fy = zoom(src[:, :, 1], g, order=1)[:ph, :pw]
            o = np.zeros((ph, pw, 4), np.uint8)
            for ch in range(3): o[:, :, ch] = map_coordinates(img[:, :, ch], [fy, fx], order=3, cval=0, prefilter=False)
            o[:, :, 3] = np.where((fx >= x0) & (fx < x1) & (fy >= y0) & (fy < y1), 255, 0)
            name = out if n == 1 else out.replace('.webp', '-%d.webp' % (r * n + c))
            Image.fromarray(o, 'RGBA').save(name, 'WEBP', quality=80, method=6)
            tl = unmerc(gx0 + ox * step, gy1 - oy * step); br = unmerc(gx0 + (ox + pw) * step, gy1 - (oy + ph) * step)
            corners.append([[round(tl[0], 6), round(tl[1], 6)], [round(br[0], 6), round(tl[1], 6)], [round(br[0], 6), round(br[1], 6)], [round(tl[0], 6), round(br[1], 6)]])
            print('piece', name, pw, ph, corners[-1])
    if sheet_out:
        sh = im.crop(CROP); sh = sh.resize((round(sh.width * SHEET_REDUCED), round(sh.height * SHEET_REDUCED)), Image.LANCZOS); sh.save(sheet_out, 'JPEG', quality=84, optimize=True, progressive=True)
        print('sheet', sheet_out, sh.size)
    fit = {'method': 'rubber-sheet (thin-plate spline)', 'points': [{'name': p[0], 'scan_px': [p[1], p[2]], 'lat': p[3], 'lon': p[4], 'whole_map_fit_misfit_m': int(m)} for p, m in zip(POINTS, misfit)],
           'whole_map_fit_rms_m': int(np.sqrt((misfit ** 2).mean())), 'crop': CROP, 'm_per_px': RES, 'size': [W, H], 'pieces': corners,
           'sheet': {'reduced': SHEET_REDUCED, 'size': [round((x1 - x0) * SHEET_REDUCED), round((y1 - y0) * SHEET_REDUCED)]}}
    json.dump(fit, open(fitpath, 'w'), indent=1)
    print('size', W, H, 'whole-map misfit rms', fit['whole_map_fit_rms_m'], 'm, max', int(misfit.max()))


if __name__ == '__main__': main(*sys.argv[1:6])
