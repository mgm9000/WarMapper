"""Mouzon 1775 (S135), North Carolina: snap the picks to the engraving (SC storyline Session 2, 27 Nov 2026).

  python3 -I pipeline/recon/nc_1775_trace_2026_11_27.py NORTH.jpg SC.jpg EAST.jpg     writes pipeline/recon/nc_1775_traced.json

The three pictures are Library of Congress IIIF regions of service:gmd:gmd390:g3900:g3900:ar139404, all at half resolution:
  NORTH  region 0,0,16912,3600 at width 8456        (North Carolina above South Carolina's crop)
  SC     region 0,3600,11800,8200 at width 5900     (the crop South Carolina was picked on)
  EAST   region 11800,3600,5112,4000 at width 2556  (the coast east of it, Cape Fear to Bogue)
They are pasted into one canvas in M coordinates (canvas y = M y + 1800). Rivers and the coast are snapped with
pipeline/recon/sc_1775_trace.py (the least-cost path through the ink between two picks), roads with the road snapper of
pipeline/recon/sc_1775_roads_2026_11_26.py (through the light gap between Mouzon's two road lines, within about 2 km of the picks).
Every line was then checked by eye on overlays at 1:1 to 1:4 and picked again where the snap ran onto a creek, hill shading or the
border of the sheet (the Yadkin round the Horse Shoe, the Dan below Wart Mountain, the Roanoke at Cotton Ferry).
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sc_1775_trace as T, sc_1775_roads_2026_11_26 as RD, nc_1775_picks_2026_11_27 as P
Image.MAX_IMAGE_PIXELS = None
OY = 1800


def canvas(north, sc, east):
    c = Image.new('RGB', (8456, OY + 4100), (255, 255, 255))
    c.paste(Image.open(north).convert('RGB'), (0, 0)); c.paste(Image.open(sc).convert('RGB'), (0, OY)); c.paste(Image.open(east).convert('RGB'), (5900, OY))
    return c


def main(north, sc, east):
    path = '/tmp/nc_1775_canvas.jpg'; canvas(north, sc, east).save(path, quality=92)   # the canvas the lines were checked on
    g = np.asarray(Image.open(path).convert('RGB'), dtype=np.float32).max(axis=2) / 255.0
    T._G[path] = gaussian_filter(g, 0.8); gr = gaussian_filter(g, 0.6)
    to_c = lambda p: (p[0], p[1] + OY); to_m = lambda p: [round(float(p[0]), 1), round(float(p[1]) - OY, 1)]
    out = {}
    for k, f in P.F.items():
        c = [to_c(p) for p in f['pts']]
        if f.get('straight'): line = [list(p) for p in f['pts']]
        elif f['kind'] in ('river', 'shore'): line = [to_m(p) for p in T.snap(path, c)]
        else: line = [to_m(p) for p in RD.rdp(RD.smooth(RD.snap(gr, c)), 1.2)]
        out[k] = dict(kind=f['kind'], name=f['name'], picks=f['pts'], line=line, **{a: b for a, b in f.items() if a not in ('kind', 'name', 'pts')})
        print(k, len(f['pts']), 'picks ->', len(line), 'points')
    json.dump(out, open(os.path.join(HERE, 'nc_1775_traced.json'), 'w'))


if __name__ == '__main__':
    main(*sys.argv[1:4])
