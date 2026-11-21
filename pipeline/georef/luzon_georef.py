"""Luzon, 1899: the campaign maps tied to the ground.

  siebert  Siebert's Map of central Luzon, Manila, November 1899 (Boston Public Library G8062.L8S1 1899 .U5; IIIF commonwealth:5m60tz00z)
  young    Howard's Map of northern Luzon for Gen. Young's report, 1900 (Boston Public Library G8062.L8S1 1899 .H69; IIIF commonwealth:wp98cr75t)

Town symbols on each scan were matched to the town's church or centre on Wikidata (read 21 Nov 2026) and an affine fit (shift, turn,
scale, shear) taken through them by least squares. Pixel picks were read from full-resolution crops with a 50-100 px grid; a town
symbol is good to about 10 px. Both are reconnaissance compilations, not surveys, and it shows: the central map sits within about
600 m of the ground (worst 1.3 km), the northern one within about 2.3 km (worst 4.7 km, in the unsurveyed interior and at Vigan).

  theatre  War Department, Theatre of military operations in Luzon, 1899, second edition, north sheet (University of Minnesota,
           Borchert Map Library G8062.L8S1 1899 .U5; IIIF cdm16022.contentdm.oclc.org p16022coll230:4182). Added 21 Nov 2026.

The theatre map was compiled in Washington from older Spanish mapping. Its 32 control points are towns from Lingayen to Malolos
and east to San Jose and Angat, the country the 1899 campaign was fought over; picks were read from a one-fifth-size copy with a
10 px grid (good to about 2 px there, 10 px on the scan, some 180 m). It sits within about 1.5 km of the ground (worst 2.9 km) and
the errors are regional, not one bad pick: Nueva Ecija is squeezed east to west. East of 121.1 E it was left unfitted on purpose:
with Baler, Bongabon and Carranglan in, the fit over the campaign country gets worse (RMS 1.9 km) and Baler is still 4.8 km out.

  python3 pipeline/georef/luzon_georef.py        prints each fit and its residuals
"""
import math
import numpy as np

MAPS = {
    'siebert': {'size': (4619, 7621), 'cp': [
        (1459, 3672, 120.5880, 15.4877, 'Tarlac church'), (2777, 4494, 120.9066, 15.3077, 'San Isidro church'),
        (3071, 3724, 120.9642, 15.4892, 'Cabanatuan cathedral'), (351, 1203, 120.3344, 16.0423, 'Dagupan church'),
        (441, 1398, 120.3570, 16.0101, 'Calasiao church'), (868, 2281, 120.4556, 15.8086, 'Bayambang church'),
        (2261, 6050, 120.7724, 14.9537, 'Apalit church'), (3079, 2417, 120.9895, 15.7922, 'San Jose cathedral'),
        (2057, 1336, 120.7478, 16.0267, 'Tayug'), (2964, 5488, 120.9419, 15.0789, 'San Ildefonso'),
        (1495, 5257, 120.5903, 15.1343, 'Angeles church'), (1929, 5705, 120.6931, 15.0284, 'San Fernando cathedral'),
        (2033, 5549, 120.7203, 15.0645, 'Mexico')]},
    'young': {'size': (3200, 6272), 'cp': [
        (1143, 5022, 120.5880, 15.4877, 'Tarlac church'), (1582, 5299, 120.9066, 15.3077, 'San Isidro church'),
        (760, 1933, 120.3890, 17.5748, 'Vigan cathedral'), (1044, 912, 120.5940, 18.1938, 'Laoag cathedral'),
        (1066, 852, 120.6120, 18.2505, 'Bacarra church'), (2242, 503, 121.4576, 18.4441, 'Abulug'),
        (2660, 1806, 121.7305, 17.6135, 'Tuguegarao cathedral'), (1859, 3580, 121.1510, 16.4839, 'Bayombong church'),
        (1904, 3522, 121.1806, 16.5186, 'Solano church'), (730, 4174, 120.3344, 16.0423, 'Dagupan church'),
        (602, 4208, 120.2313, 16.0219, 'Lingayen church'), (773, 4224, 120.3570, 16.0101, 'Calasiao church'),
        (706, 3326, 120.3179, 16.6157, 'San Fernando (La Union) cathedral'), (1659, 5048, 120.9642, 15.4892, 'Cabanatuan cathedral'),
        (1619, 5161, 120.9376, 15.4232, 'Santa Rosa church'), (1306, 5723, 120.6931, 15.0284, 'San Fernando (Pampanga) cathedral'),
        (1421, 5821, 120.7724, 14.9537, 'Apalit church'), (1350, 5659, 120.7203, 15.0645, 'Mexico')]},
    'theatre': {'size': (11998, 9451), 'cp': [
        (1870, 1300, 120.2313, 16.0219, 'Lingayen church'), (2430, 1165, 120.3344, 16.0423, 'Dagupan church'),
        (3130, 1035, 120.4411, 16.0725, 'San Jacinto church'), (3155, 2705, 120.4556, 15.8086, 'Bayambang church'),
        (3870, 3240, 120.5725, 15.7331, 'Moncada'), (5035, 1485, 120.7478, 16.0267, 'Tayug'),
        (5140, 1165, 120.7620, 16.0690, 'San Nicolas'), (5655, 2065, 120.8419, 15.9289, 'Umingan'),
        (6390, 3100, 120.9895, 15.7922, 'San Jose cathedral'), (5830, 4305, 120.9192, 15.5844, 'Talavera'),
        (5425, 4785, 120.8450, 15.5036, 'Aliaga'), (6120, 5055, 120.9642, 15.4892, 'Cabanatuan cathedral'),
        (4030, 4045, 120.5986, 15.6069, 'Gerona'), (3975, 4835, 120.5880, 15.4877, 'Tarlac church'),
        (5780, 6125, 120.9066, 15.3077, 'San Isidro church'), (5085, 7180, 120.7730, 15.1514, 'Arayat church'),
        (5385, 7530, 120.8280, 15.0918, 'Candaba church'), (6200, 7175, 120.9760, 15.1409, 'San Miguel church'),
        (5835, 8395, 120.9004, 14.9555, 'Baliuag church'), (5040, 8630, 120.7690, 14.9161, 'Calumpit church'),
        (5300, 9085, 120.8116, 14.8423, 'Malolos church'), (6600, 8490, 121.0290, 14.9277, 'Angat church'),
        (4560, 7895, 120.6931, 15.0284, 'San Fernando cathedral'), (4285, 8135, 120.6480, 15.0003, 'Bacolor'),
        (4395, 6800, 120.6600, 15.2144, 'Magalang'), (4000, 7205, 120.5903, 15.1343, 'Angeles church'),
        (3805, 1620, 120.5672, 15.9736, 'Urdaneta'), (3875, 3690, 120.5789, 15.6681, 'Paniqui'),
        (5945, 5525, 120.9376, 15.4232, 'Santa Rosa church'), (5615, 6570, 120.8588, 15.2496, 'Cabiao'),
        (5625, 8860, 120.8600, 14.8858, 'Plaridel (Quingua) church'), (6010, 7710, 120.9419, 15.0789, 'San Ildefonso')]},
}


class Fit:
    def __init__(self, name):
        m = MAPS[name]; self.W, self.H = m['size']; self.cp = m['cp']
        self.lat0 = sum(c[3] for c in self.cp) / len(self.cp); self.lon0 = sum(c[2] for c in self.cp) / len(self.cp)
        self.kx = 111320 * math.cos(math.radians(self.lat0)); self.ky = 110574
        P = np.array([(c[0], c[1], 1.0) for c in self.cp]); E = np.array([((c[2] - self.lon0) * self.kx, (c[3] - self.lat0) * self.ky) for c in self.cp])
        cx = np.linalg.lstsq(P, E[:, 0], rcond=None)[0]; cy = np.linalg.lstsq(P, E[:, 1], rcond=None)[0]
        self.M = np.array([[cx[0], cx[1]], [cy[0], cy[1]]]); self.T = np.array([cx[2], cy[2]])

    def px2ll(self, x, y):
        e, n = self.M @ np.array([x, y]) + self.T; return float(self.lat0 + n / self.ky), float(self.lon0 + e / self.kx)

    def residuals(self):
        out = []
        for c in self.cp:
            la, lo = self.px2ll(c[0], c[1]); out.append((c[4], round(math.hypot((lo - c[2]) * self.kx, (la - c[3]) * self.ky))))
        return out

    def corners(self):
        """tl, tr, br, bl of the whole scan as (lat, lon)."""
        return [self.px2ll(0, 0), self.px2ll(self.W, 0), self.px2ll(self.W, self.H), self.px2ll(0, self.H)]

    def summary(self):
        r = self.residuals(); return {'points': len(r), 'rms_m': round(math.sqrt(sum(d * d for _, d in r) / len(r))), 'max_m': max(d for _, d in r),
                                      'm_per_px': round(float(math.hypot(self.M[0, 0], self.M[1, 0])), 1)}


if __name__ == '__main__':
    for name in MAPS:
        f = Fit(name); print(name, f.summary())
        for n, d in f.residuals(): print('  %-40s %5d m' % (n, d))
        print('  corners', [tuple(round(v, 5) for v in c) for c in f.corners()])
