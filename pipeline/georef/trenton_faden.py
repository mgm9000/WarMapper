"""Faden's 1777 'Plan of the operations of General Washington' (Boston Public Library, Leventhal Map Center, commonwealth:wd3768583),
fitted to the ground for the Trenton playback.

The engraving is badly out of shape against the ground: fitted as a whole (affine), towns are 1 to 9 km from where they are, and even
inside the area of the battle Pennington and Maidenhead are 3 to 4 km out. So the scan is rubber-sheeted: it is warped smoothly
(a thin-plate spline on 12 towns and crossings) so each of them lands on its real place, the way georeferencing tools such as Allmaps do.
Outside the ring of towns the spline runs on smoothly. Cranbury and Allentown, in the east and outside the
battle, are left out: they are 6.5 and 7 km out on the engraving, and pulling them into place tears that part of the sheet. The result is a picture in Web Mercator, north up, that the
playback lays down by its four corners.

Usage: python3 -I trenton_faden.py SCAN.jpg OUT.webp FIT.json     (SCAN: the full image from the library's IIIF service, 7551 x 5174)
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
RES = 12.0                            # metres on the ground per pixel of the picture, at this latitude
R = 6378137.0


def merc(lon, lat): return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def unmerc(x, y): return math.degrees(x / R), math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2)


def main(scan, out, fitpath):
    from scipy.ndimage import zoom, map_coordinates
    k = 1 / math.cos(math.radians(40.25)); step = RES * k                      # mercator metres per output pixel
    G = np.array([merc(p[4], p[3]) for p in POINTS]); S = np.array([[p[1], p[2]] for p in POINTS], float)
    A = np.c_[S, np.ones(len(S))]; ax = np.linalg.lstsq(A, G[:, 0], rcond=None)[0]; ay = np.linalg.lstsq(A, G[:, 1], rcond=None)[0]
    aff = lambda x, y: (ax @ [x, y, 1], ay @ [x, y, 1])
    misfit = np.hypot(A @ ax - G[:, 0], A @ ay - G[:, 1]) / k
    # where the sheet's border lands: the spline from scan to ground, sampled along the border (the spline runs on smoothly past the
    # outermost towns, so no extra points are needed at the edge, and none can pull against a town's real place)
    x0, y0, x1, y1 = CROP; fwd = ThinPlateSplineTransform.from_estimate(S, G)
    edge = np.array([(x, y) for x in np.linspace(x0, x1, 60) for y in (y0, y1)] + [(x, y) for y in np.linspace(y0, y1, 60) for x in (x0, x1)])
    E = fwd(edge); gx0, gx1 = E[:, 0].min(), E[:, 0].max(); gy0, gy1 = E[:, 1].min(), E[:, 1].max()
    W, H = int((gx1 - gx0) / step) + 1, int((gy1 - gy0) / step) + 1
    O = np.c_[(G[:, 0] - gx0) / step, (gy1 - G[:, 1]) / step]; Sall = S        # output pixel (col, row) of each town
    t = ThinPlateSplineTransform.from_estimate(O, Sall)
    # the spline is worked out on a coarse grid and filled in between, and the scan is read at half size, so the job fits in memory
    g = 8; gc, gr = np.meshgrid(np.arange(0, W + g, g), np.arange(0, H + g, g)); src = t(np.c_[gc.ravel(), gr.ravel()]).reshape(gr.shape + (2,))
    fx = zoom(src[:, :, 0], g, order=1)[:H, :W] / 2; fy = zoom(src[:, :, 1], g, order=1)[:H, :W] / 2
    im = Image.open(scan).convert('RGB'); im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS); img = np.asarray(im)
    o = np.zeros((H, W, 4), np.uint8)
    for c in range(3): o[:, :, c] = map_coordinates(img[:, :, c], [fy, fx], order=1, cval=0)
    inside = (fx >= x0 / 2) & (fx < x1 / 2) & (fy >= y0 / 2) & (fy < y1 / 2); o[:, :, 3] = np.where(inside, 255, 0)
    Image.fromarray(o, 'RGBA').save(out, 'WEBP', quality=82, method=6)
    tl, br = unmerc(gx0, gy1), unmerc(gx0 + W * step, gy1 - H * step)
    corners = [[round(tl[0], 6), round(tl[1], 6)], [round(br[0], 6), round(tl[1], 6)], [round(br[0], 6), round(br[1], 6)], [round(tl[0], 6), round(br[1], 6)]]
    fit = {'method': 'rubber-sheet (thin-plate spline)', 'points': [{'name': p[0], 'scan_px': [p[1], p[2]], 'lat': p[3], 'lon': p[4], 'whole_map_fit_misfit_m': int(m)} for p, m in zip(POINTS, misfit)],
           'whole_map_fit_rms_m': int(np.sqrt((misfit ** 2).mean())), 'crop': CROP, 'm_per_px': RES, 'size': [W, H], 'corners_tl_tr_br_bl': corners}
    json.dump(fit, open(fitpath, 'w'), indent=1)
    print('size', W, H, 'corners', corners, 'whole-map misfit rms', fit['whole_map_fit_rms_m'], 'm, max', int(misfit.max()))


if __name__ == '__main__': main(*sys.argv[1:4])
