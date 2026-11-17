"""Sketch A of the British official history is a double-page map. The scan of the book loses a strip about 1.1 km wide in the
binding between the two pages, east of Ypres, so the mosaic had a gap down its middle. This fills the strip so the sheet reads
as one: the tint is carried across from the two page edges (covering the binding's shadow on the left page), and the main roads, the canal and the river that cross the strip are
drawn in from the battle's base data (today's map) in a paler ink than the sketch's own, with a caption saying so.

Usage: python3 ypres_sketch_a_gutter.py ORIGINAL.webp OUT.webp     (ORIGINAL is the mosaic with the gap, as in the repository before 17 Nov 2026)
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
FIT = json.load(open(os.path.join(HERE, 'ypres_sketch_fits.json')))['A']
LAT0, LON0 = 50.8522, 2.8846; KX = 111320 * math.cos(math.radians(LAT0)); KY = 111040


def px(lon, lat): return ((lon - LON0) * KX - FIT['x0']) / FIT['res'], (-(lat - LAT0) * KY - FIT['y0']) / FIT['res']


def unpack(s):
    out = []; x = y = 0
    for p in s.split(';'):
        a, b = p.split(','); x += int(a); y += int(b); out.append((x / 1e5, y / 1e5))
    return out


def main(src, dst):
    im = Image.open(src).convert('RGBA'); a = np.array(im).astype(float); H, W = a.shape[:2]; op = a[:, :, 3] > 128
    L = np.full(H, -1); R = np.full(H, -1)
    for y in range(H):
        gap = np.where(~op[y, 1450:1950])[0]
        if not len(gap): continue
        xl, xr = gap.min() + 1450 - 1, gap.max() + 1450 + 1
        if xl > 60 and xr < W - 60 and op[y, xl - 30:xl].all() and op[y, xr + 1:xr + 31].all() and (xr - xl) < 200: L[y], R[y] = xl - 12, xr   # 12 px more on the left: the dark shadow of the binding
    rows = np.where(L >= 0)[0]
    # the tint at each edge: sampled a little way in from the binding shadow, then smoothed down the page so ink lines do not streak across
    cl = np.array([np.median(a[y, L[y] - 40:L[y] - 12, :3], axis=0) for y in rows]); cr = np.array([np.median(a[y, R[y] + 14:R[y] + 34, :3], axis=0) for y in rows])
    def smooth(c, k=41):
        out = np.empty_like(c)
        for i in range(len(c)): out[i] = np.median(c[max(0, i - k):i + k + 1], axis=0)
        return out
    cl, cr = smooth(cl), smooth(cr); mask = np.zeros((H, W), bool)
    for i, y in enumerate(rows):
        n = R[y] - L[y] + 1; t = np.linspace(0, 1, n)[:, None]
        a[y, L[y]:R[y] + 1, :3] = cl[i] * (1 - t) + cr[i] * t; a[y, L[y]:R[y] + 1, 3] = 255; mask[y, L[y]:R[y] + 1] = True
    out = Image.fromarray(a.astype('uint8'), 'RGBA')
    # roads and water that cross the strip, from the base data, on a layer cut to the strip
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); base = json.load(open(os.path.join(ROOT, 'data', 'base', 'ypres.json')))
    for kind, cls, name, packed in base['lines']:
        pts = [px(lo, la) for lo, la in unpack(packed)]
        if kind == 'road' and cls in ('m', 's'): d.line(pts, fill=(92, 88, 70, 255), width=3 if cls == 'm' else 2)
        elif kind in ('water', 'former-water'): d.line(pts, fill=(70, 96, 110, 255), width=3)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf', 17)
    except Exception: font = ImageFont.load_default()
    cap = "strip lost in the binding of the book: roads drawn in from today's map"
    tw = int(d.textlength(cap, font=font)) + 8; t = Image.new('RGBA', (tw, 24), (0, 0, 0, 0)); ImageDraw.Draw(t).text((4, 2), cap, fill=(92, 88, 70, 255), font=font)
    t = t.rotate(90, expand=True)
    for y0 in (rows.min() + 60, rows.min() + 60 + tw + 500):
        if y0 + tw < rows.max(): lay.alpha_composite(t, (int((L[y0 + tw // 2] + R[y0 + tw // 2]) / 2) - 12 + 30, int(y0)))
    la = np.array(lay); la[~mask] = 0; out.alpha_composite(Image.fromarray(la, 'RGBA'))
    out.save(dst, 'WEBP', quality=88, method=6); print('filled rows', len(rows), 'strip width px', int((R[rows] - L[rows]).mean()), 'about', round((R[rows] - L[rows]).mean() * FIT['res']), 'm', os.path.getsize(dst))


if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
