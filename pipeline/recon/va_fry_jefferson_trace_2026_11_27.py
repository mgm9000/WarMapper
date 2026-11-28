"""Fry and Jefferson (S152), southern Virginia: snap the picks to the engraving (SC storyline Session 2, 27 Nov 2026).

  python3 -I pipeline/recon/va_fry_jefferson_trace_2026_11_27.py STRIP.jpg     writes pipeline/recon/va_fry_jefferson_traced.json

STRIP is the Library of Congress IIIF region 2000,5400,9400,3000 at width 4700 of service:gmd:gmd388:g3880:g3880:ct000370. Rivers are snapped
with pipeline/recon/sc_1775_trace.py, the Great Wagon Road with the road snapper of sc_1775_roads_2026_11_26.py; every line was checked by eye
on overlays and picked again where the snap ran onto a creek (the Banister onto the Stinking River, the Meherrin onto Fountains Creek).
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sc_1775_trace as T, sc_1775_roads_2026_11_26 as RD, va_fry_jefferson_picks_2026_11_27 as P


def main(strip):
    g = np.asarray(Image.open(strip).convert('RGB'), dtype=np.float32).max(axis=2) / 255.0
    T._G[strip] = gaussian_filter(g, 0.8); gr = gaussian_filter(g, 0.6); out = {}
    for k, f in P.F.items():
        if f.get('straight'): line = [list(map(float, p)) for p in f['pts']]
        elif f['kind'] == 'river': line = [list(map(float, p)) for p in T.snap(strip, f['pts'])]
        else: line = [list(map(float, p)) for p in RD.rdp(RD.smooth(RD.snap(gr, f['pts'])), 1.2)]
        out[k] = dict(kind=f['kind'], name=f['name'], picks=f['pts'], line=line, **{a: b for a, b in f.items() if a not in ('kind', 'name', 'pts')})
        print(k, len(f['pts']), 'picks ->', len(line), 'points')
    json.dump(out, open(os.path.join(HERE, 'va_fry_jefferson_traced.json'), 'w'))


if __name__ == '__main__':
    main(sys.argv[1])
