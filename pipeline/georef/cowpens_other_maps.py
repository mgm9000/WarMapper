"""The other maps of the Cowpens, made into pictures that lie on the ground, for the playback's "Other maps of this ground".

  python3 -I cowpens_other_maps.py SRC OUTDIR      SRC: the folder of the files Morgan saved (maps-source/Cowpens) and mills_full.jpg
                                                   (Library of Congress, g3913s.cws00153, the full image from its IIIF service)
                                                   Writes OUTDIR/usgs-1959.webp, usgs-1975.webp, mills-1825.webp, nps-park-map.webp and
                                                   pipeline/georef/cowpens_other_fit.json.

USGS 1959 (Cowpens, S.C., 1:62,500, S108) and USGS 1975 (Cowpens NE, S.C., orthophoto map, 1:24,000, S109) are GeoTIFFs from the
USGS's Historical Topographic Map Collection, in NAD 27 on their own projections. They are reprojected to WGS 84 on a grid of
0.00002 degrees (about 2 m), cut to the ground the playback uses. Today's roads and the park's trace fall on them to about 10 m.
The 1975 sheet's south edge is 35.125 N: the picture stops there.

Mills's Atlas (1825, S110): the Library of Congress copy is a pen-and-ink tracing of it made for Sherman's army. Fitted by least
squares (affine) to five places: the court house at Spartanburg, Glenn Springs, Thicketty Mountain, Gaffney's Tavern (Gaffney) and
"Battle of the Cowpens", which Mills marks at a crossroads and is put at the crossing on Bearss's map. The places land 0.4 to 1 km from
where they are: at two miles to the inch that is the map, not the fit. Cut to the country around the Cowpens (MILLS_WINDOW).

The National Park Service's park map (S111) is drawn north up; its scale bar does not agree with its own roads (the bar gives 1.32 m a
pixel, the roads 1.04), so it is fitted by three road points (the trace's east end at the trailhead, the main entrance on SC 11, SC 11
at US 221A), turned and scaled, to about 30 m.
"""
import json, math, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import cowpens_geo as G
Image.MAX_IMAGE_PIXELS = None

BOX = (-81.840, 35.105, -81.770, 35.155)          # west, south, east, north: the ground cut from the USGS sheets
RES = 0.00002
TIFF = {'1959': 'SC_Cowpens_261816_1959_62500_geo.tif', '1975': 'SC_Cowpens NE_260906_1975_24000_geo.tif'}
MILLS_POINTS = [('Spartanburgh (court house)', 3158, 2955, 34.94957, -81.93205), ('Glenn Springs', 4179, 4258, 34.81986, -81.83260),
                ('Thicketty Mountain', 4268, 1350, 35.11350, -81.76882), ("Gaffney's Tavern (Gaffney)", 5460, 1700, 35.07180, -81.64982),
                ('Battle of the Cowpens (the crossing on Bearss\'s map)', 3982, 1225, None, None)]
MILLS_WINDOW = (-81.905, 35.065, -81.705, 35.195)   # the ground cut from it: Thicketty Mountain to Chesnee, the Pacolet to Island Ford (within the
                                                    # battle file's reach: twice the playback's extent each way)
NPS_POINTS = [("the trace's east end, at the trailhead", 2416, 2145, 35.13162, -81.80223), ('SC 11 at US 221A', 733, 1063, 35.14301, -81.82046),
              ('the main entrance on SC 11', 1100, 1165, 35.14193, -81.81580)]


def usgs(src, tag):
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.transform import from_bounds
    W = int(round((BOX[2] - BOX[0]) / RES)); H = int(round((BOX[3] - BOX[1]) / RES))
    out = np.full((3, H, W), 255, np.uint8); tr = from_bounds(*BOX, W, H)
    with rasterio.open(os.path.join(src, TIFF[tag])) as r:
        for b in range(3): reproject(rasterio.band(r, b + 1), out[b], dst_transform=tr, dst_crs='EPSG:4326', resampling=Resampling.bilinear, dst_nodata=255)
    return Image.fromarray(out.transpose(1, 2, 0))


def corners_box(w, s, e, n): return [[w, n], [e, n], [e, s], [w, s]]


def mills(src):
    bearss = json.load(open(os.path.join(HERE, 'cowpens_bearss_fit.json')))
    M = np.array(bearss['plate1_to_ground']['M']); t = np.array(bearss['plate1_to_ground']['t'])
    cx = G._ll(*(np.array([2390, -705]) @ M.T + t))
    pts = [p if p[3] is not None else (p[0], p[1], p[2], cx[0], cx[1]) for p in MILLS_POINTS]
    lat0 = 35.0; KX = 111320 * math.cos(math.radians(lat0)); KY = 110940
    A = np.array([[p[1], p[2], 1] for p in pts], float); Q = np.array([[p[4] * KX, p[3] * KY] for p in pts])
    X, *_ = np.linalg.lstsq(A, Q, rcond=None); res = np.hypot(*(A @ X - Q).T)
    def ll(x, y): q = np.array([x, y, 1]) @ X; return [round(float(q[0] / KX), 6), round(float(q[1] / KY), 6)]
    Ai = np.linalg.inv(np.vstack([X.T, [0, 0, 1]]))           # ground (metres) -> scan pixel
    w, s_, e, n = MILLS_WINDOW; px = [Ai @ [lo * KX, la * KY, 1] for lo in (w, e) for la in (s_, n)]
        # the pixel box round the window is wider than it on the ground (the sheet is turned): pull it in to the window's inner edges
    xs = sorted(q[0] for q in px); ys = sorted(q[1] for q in px); x0, x1, y0, y1 = int(xs[1]), int(xs[2]), int(ys[1]), int(ys[2])
    crop = (x0, y0, x1, y1)
    im = Image.open(os.path.join(src, 'mills_full.jpg')).convert('RGB').crop(crop); im = im.resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS)
    fit = {'method': 'affine (shift, turn, scale, shear) by least squares on 5 places', 'points': [{'name': p[0], 'scan_px': [p[1], p[2]], 'lat': round(p[3], 5), 'lon': round(p[4], 5), 'misfit_m': round(float(r))} for p, r in zip(pts, res)],
           'rms_m': round(float(math.sqrt((res ** 2).mean()))), 'crop': list(crop), 'reduced': 0.75, 'corners': [ll(x0, y0), ll(x1, y0), ll(x1, y1), ll(x0, y1)]}
    return im, fit


def nps(src):
    f = [n for n in os.listdir(src) if n.endswith('HiResProxy.jpg')][0]
    P = np.array([[p[1], -p[2]] for p in NPS_POINTS], float); Q = np.array([G._xy((p[3], p[4])) for p in NPS_POINTS])
    ma, mb = P.mean(0), Q.mean(0); U, S, Vt = np.linalg.svd((P - ma).T @ (Q - mb)); R = Vt.T @ U.T; sc = S.sum() / ((P - ma) ** 2).sum()
    res = np.hypot(*(((P - ma) @ R.T * sc + mb) - Q).T)
    im = Image.open(os.path.join(src, f)).convert('RGB'); W, H = im.size
    def ll(x, y): q = (np.array([x, -y]) - ma) @ R.T * sc + mb; la, lo = G._ll(*q); return [round(float(lo), 6), round(float(la), 6)]
    fit = {'method': 'turn, scale and shift by least squares on 3 road points', 'm_per_px': round(float(sc), 3), 'scale_bar_m_per_px': 1.323, 'turn_deg': round(math.degrees(math.atan2(R[1, 0], R[0, 0])), 2),
           'points': [{'name': p[0], 'map_px': [p[1], p[2]], 'lat': p[3], 'lon': p[4], 'misfit_m': round(float(r))} for p, r in zip(NPS_POINTS, res)],
           'reduced': 0.5, 'corners': [ll(0, 0), ll(W, 0), ll(W, H), ll(0, H)]}
    return im.resize((W // 2, H // 2), Image.LANCZOS), fit


def main(src, outdir):
    fits = {}
    a = usgs(src, '1959'); a = a.resize((a.width // 2, a.height // 2), Image.LANCZOS); a.save(os.path.join(outdir, 'usgs-1959.webp'), quality=70, method=6)
    fits['usgs-1959'] = {'method': 'the GeoTIFF\'s own georeference (NAD 27), reprojected to WGS 84', 'corners': corners_box(*BOX), 'm_per_px': 3.6}
    b = usgs(src, '1975'); rows = int(round((BOX[3] - 35.125) / RES)); b = b.crop((0, 0, b.width, rows)); b = b.resize((int(b.width * 0.75), int(b.height * 0.75)), Image.LANCZOS)
    b.save(os.path.join(outdir, 'usgs-1975.webp'), quality=68, method=6)
    fits['usgs-1975'] = {'method': 'the GeoTIFF\'s own georeference (NAD 27), reprojected to WGS 84', 'corners': corners_box(BOX[0], 35.125, BOX[2], BOX[3]), 'm_per_px': 2.4}
    m, fits['mills-1825'] = mills(src); m.save(os.path.join(outdir, 'mills-1825.webp'), quality=70, method=6)
    n, fits['nps-park-map'] = nps(src); n.save(os.path.join(outdir, 'nps-park-map.webp'), quality=72, method=6)
    json.dump(fits, open(os.path.join(HERE, 'cowpens_other_fit.json'), 'w'), indent=1)
    for k, v in fits.items(): print(k, v.get('rms_m', ''), [p.get('misfit_m') for p in v.get('points', [])], v['corners'])


if __name__ == '__main__':
    main(*sys.argv[1:3])
