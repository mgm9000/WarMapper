"""Cowpens: a reconstructed 1781 base map and the other maps of the ground (24 Nov 2026). Writes the workbook rows; the pictures and the
lines come from pipeline/georef/cowpens_bearss.py, cowpens_landers.py, cowpens_other_maps.py and pipeline/recon/cowpens_1781.py.

  1. A WarMapper reconstruction of the ground in January 1781 (Reconstructions, Recon layers; data/recon/cowpens-1781.geojson), drawn on
     today's terrain, and the base the playback opens on ("1781 with terrain").
  2. Nine other maps of the ground, fitted to it, offered from the map details under "Other maps of this ground" (Maps; hidden bases):
     Bearss's four troop-movement maps of 1967 as one base that follows the clock, phase by phase; Landers's two sketches of 1928;
     the USGS sheets of 1959 and 1975; Mills's map of Spartanburgh District (1825); the National Park Service's park map.
  3. Sources S108 to S111; S107 may be hosted (a National Park Service work; no copyright notice in Morgan's copy); S103's plates seen.
     Gap CG02 closed; a note on CG06 (the maps show the road Tarleton probably came by; RC01 is not changed). Labels for the reconstruction.

It stops if source S108 is already in Sources and notes.xlsx.
"""
import json, math, os, sys
import openpyxl
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cowpens_geo as G
from cowpens_audit_2026_11_24 import header, last_row, add, rows_by_id, setv, add_note

DATA = os.path.join(ROOT, 'data', 'WarMapper battle data')
WAR = os.path.join(DATA, 'Revolutionary War.xlsx'); SHARED = os.path.join(DATA, 'Sources and notes.xlsx')
TODAY = '2026-11-24'; PB = 'cowpens'
FIT = {k: json.load(open(os.path.join(HERE, 'georef', f))) for k, f in (('bearss', 'cowpens_bearss_fit.json'), ('landers', 'cowpens_landers_fit.json'), ('other', 'cowpens_other_fit.json'))}
RECON = json.load(open(os.path.join(ROOT, 'data', 'recon', 'cowpens-1781.geojson')))
BEARSS_URL = 'https://dc.statelibrary.sc.gov/items/ef5e6740-8015-4647-88b3-9820a8382285'
LANDERS_URL = 'https://archive.org/details/historicalstatem00army/page/n96/mode/1up'
USGS59 = 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/HistoricalTopo/GeoTIFF/SC/SC_Cowpens_261816_1959_62500_geo.tif'
USGS75 = 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/HistoricalTopo/GeoTIFF/SC/SC_Cowpens%20NE_260906_1975_24000_geo.tif'
MILLS = 'https://www.loc.gov/item/2007627909/'
NPS = 'https://www.nps.gov/npgallery/AssetDetail/ad1a1112-bd76-4068-bba9-6e7232890013'
TOPOVIEW = 'https://ngmdb.usgs.gov/topoview/'

SOURCES = [
    dict(source_id='S108', title='Cowpens, S.C., 15-minute series topographic map, 1:62,500', author='U.S. Geological Survey', date='1959',
         type='Survey map: USGS topographic quadrangle', citation='U.S. Geological Survey, Cowpens, S.C., 15-minute series (topographic), 1:62,500 (1959). Historical Topographic Map Collection, GeoTIFF SC_Cowpens_261816_1959_62500_geo.',
         **{'page verified?': 'n/a (a map)'}, url=USGS59, rights='U.S. government work: public domain.',
         notes='Fetched by Morgan 24 Nov 2026 (maps-source/Cowpens). The oldest USGS sheet of the ground: SC 11 still runs on the old road through the field; the 1929 battlefield site and its monument are at the SC 11 / SC 110 junction. '
               'Used to check Bearss\'s roads and to carry them beyond his sheet; offered as an other map (pipeline/georef/cowpens_other_maps.py).',
         used_for='COWP', kind='map', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='USGS National Map (topoView)', local_copy='maps-source/Cowpens/SC_Cowpens_261816_1959_62500_geo.tif'),
    dict(source_id='S109', title='Cowpens NE, S.C., 7.5-minute series orthophoto map, 1:24,000', author='U.S. Geological Survey', date='1975',
         type='Survey map: USGS orthophoto quadrangle (an aerial photograph drawn to scale)', citation='U.S. Geological Survey, Cowpens NE, S.C., 7.5-minute series (orthophotomap), 1:24,000 (1975). Historical Topographic Map Collection, GeoTIFF SC_Cowpens NE_260906_1975_24000_geo.',
         **{'page verified?': 'n/a (a map)'}, url=USGS75, rights='U.S. government work: public domain.',
         notes='Fetched by Morgan 24 Nov 2026. The field from the air before the park was rebuilt (1976-79): the old road bed under the park\'s trace, and Bearss\'s road east of the field as a track. Its south edge is 35.125 N. '
               'Morgan also fetched the 1983 Cowpens sheet south of it; it is not used (the 1959 sheet covers that ground).',
         used_for='COWP', kind='map', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='USGS National Map (topoView)', local_copy='maps-source/Cowpens/SC_Cowpens NE_260906_1975_24000_geo.tif'),
    dict(source_id='S110', title='Spartanburgh District, South Carolina (Mills\'s Atlas)', author='Robert Mills; surveyed by J. Whitten, 1820; engraved by H. S. Tanner', date='1825',
         type='Period map: district map of the state atlas, here in a pen-and-ink tracing made for the Union army (1865)',
         citation='Robert Mills, Spartanburgh District, South Carolina. Surveyed by J. Whitten, 1820. Improved for Mills\' Atlas, 1825. Scale 2 miles to an inch. Library of Congress, Geography and Map Division, G3913.S7 1820 .M5 (LC Civil War maps, 2nd ed., S153: a tracing, "Approved Chas. R. Suter", Sherman #153).',
         **{'page verified?': 'n/a (a map)'}, url=MILLS, rights='Published 1825; the tracing is a U.S. Army work of 1865. Public domain; the Library of Congress gives it as free to use.',
         notes='Read 24 Nov 2026 from the Library of Congress image (IIIF service gmd391/g3913/g3913s/cws00153, 6,684 x 7,258). Marks "Battle of the Cowpens" at a crossroads of four roads, with Thicketty Mountain to the south-east. '
               'Fitted to five places to about 0.7 km: a check on the roads leaving the crossroads, and an other map for the country around.',
         used_for='COWP', kind='map', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='loc.gov', local_copy=None),
    dict(source_id='S111', title='Park Map - Cowpens National Battlefield', author='National Park Service', date='2020s',
         type='Modern map: the park\'s own map', citation='National Park Service, Harpers Ferry Center, Park Map - Cowpens National Battlefield (NPGallery asset ad1a1112-bd76-4068-bba9-6e7232890013).',
         **{'page verified?': 'n/a (a map)'}, url=NPS, rights='National Park Service map: public domain (NPGallery: "government produced and in the public domain").',
         notes='Fetched by Morgan 24 Nov 2026 (the 3,296 x 4,167 picture). Draws the "historic route of Green River Road", the trails, the monuments and the Robert Scruggs House. Its scale bar is about 27% out against its own roads; fitted by three road points.',
         used_for='COWP', kind='map', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='nps.gov (NPGallery)', local_copy='maps-source/Cowpens/ad1a1112-...HiResProxy.jpg'),
]


def LL(c): return [c[1], c[0]]   # [lon, lat] -> (lat, lon)


def map_row(mid, title, short, label, credit, source, file, corners, fit, note, m_per_px, scale_note=None, frm=None, to=None):
    (tl, tr, br, bl) = corners
    return dict(playback_id=PB, map_id=mid, title=title, short=short, label=label, credit=credit, source_id=source, fitted_to_ground='yes', file=file,
                tl_lat=tl[1], tl_lon=tl[0], tr_lat=tr[1], tr_lon=tr[0], br_lat=br[1], br_lon=br[0], bl_lat=bl[1], bl_lon=bl[0], fit=json.dumps(fit), note=note,
                approx_m_per_px=m_per_px, scale_note=scale_note, **({'from': frm} if frm else {}), **({'to': to} if to else {}))


def maps():
    B = FIT['bearss']; L = FIT['landers']; O = FIT['other']
    bfit = {'method': 'turned and shifted, at the plate\'s own scale bar, so its road lies on the park\'s trace of the road (iterated closest points)', 'm_per_px': B['m_per_px'],
            'road_points': B['road_match']['points'], 'median_m': B['road_match']['median_m'], 'p90_m': B['road_match']['p90_m'],
            'check': 'fitted to each half of the trace in turn, the other half lies %s and %s m off on average' % (B['checks'][0]['other_half_mean_m'], B['checks'][1]['other_half_mean_m'])}
    PH = [(1, 'Phase I: daybreak to 7 a.m.', '1781-01-17 06:00', '1781-01-17 07:11'), (2, 'Phase II: the British advance to the withdrawal of Pickens\'s militia', '1781-01-17 07:12', '1781-01-17 07:37'),
          (3, 'Phase III: the advance of the 71st to Howard\'s counterattack', '1781-01-17 07:38', '1781-01-17 07:49'), (4, 'Phase IV: the rout of the British', '1781-01-17 07:50', '1781-01-17 08:30')]
    rows = []
    for n, ph, a, b in PH:
        p = B['plates'][str(n)]; f = dict(bfit); f['plate'] = n
        if n > 1: f['registered_to_plate_1'] = 'by the contours of the base, correlation %.2f' % p['match_to_plate_1']
        rows.append(map_row('bearss-1967-%d' % n, 'Bearss, Battle of Cowpens: Troop Movements of %s (1967, Plate %s)' % (ph, 'I II III IV'.split()[n - 1]), 'Bearss %s' % 'I II III IV'.split()[n - 1],
                            'Bearss 1967, Plate %s' % 'I II III IV'.split()[n - 1], 'Bearss, 1967 · National Park Service', 'S107', 'bearss-plate-%d.webp' % n, p['corners'], f,
                            'Edwin Bearss\'s troop-movement map for %s, drawn for the National Park Service in 1967 on a surveyed contour base (contours in feet). His own unit symbols are printed on it and differ from this playback\'s in places '
                            '(see the Hypotheses sheet). Turned and laid on the ground by its road, to about 25 m. This playback\'s clock decides when each plate shows: Bearss\'s phases are of events, not of times.' % ph[0].lower() + ph[1:],
                            1.145, 'Scale bar: 1,125 feet', a, b))
    l1, l2 = L['plate1'], L['plate2']
    rows.append(map_row('landers-1928-1', 'Landers, Battle of the Cowpens, January 17, 1781: roads, mounds, woods and fields as at present (Army War College, 1928, plate 1)', '1928 sketch', 'Army War College sketch, 1928',
                        'Landers, 1928 · Army War College', 'S103', 'landers-1928-1.webp', l1['corners'],
                        {'method': 'turned and shifted at the plate\'s scale (4 inches to the mile) so its main road lies on the park\'s trace', 'm_per_px': l1['m_per_px'], 'turn_deg': l1['turn_deg'], 'median_m': l1['median_m'], 'p90_m': l1['p90_m']},
                        'Lt. Col. H. L. Landers\'s sketch of April 1928 for the Army War College, printed for Congress: the roads, houses, woods and 5-foot contours of 1928, with the two armies\' lines. '
                        'Fitted by its main road to about 15 m there; it is a sketch, and away from that road it drifts (its "Old Mill Gap Road" lies some 20 degrees south of where the 1959 survey has the road).', 2.32, '4 inches = 1 mile'))
    rows.append(map_row('landers-1928-2', 'Landers, Battle of the Cowpens: battle formation (Army War College, 1928, plate 2)', '1928 formation', 'Army War College formation sketch, 1928',
                        'Landers, 1928 · Army War College', 'S103', 'landers-1928-2.webp', l2['corners'],
                        {'method': 'turned and shifted at the plate\'s scale (500 yards) so its road lies on the park\'s trace', 'm_per_px': l2['m_per_px'], 'turn_deg': l2['turn_deg'], 'median_m': l2['median_m'], 'p90_m': l2['p90_m']},
                        'The Army War College\'s diagram of the two lines as they formed (1928): two roads and the units, nothing of the ground. Fitted by its road.', 0.67, 'Scale bar: 500 yards'))
    o = O['usgs-1959']; rows.append(map_row('usgs-1959', 'U.S. Geological Survey, Cowpens, S.C., 1:62,500 (1959)', 'USGS 1959', 'USGS map, 1959', 'USGS, 1959', 'S108', 'usgs-1959.webp', o['corners'],
                                            {'method': o['method']}, 'The oldest survey map of the ground: SC 11 still runs on the old road through the field, and the battlefield of 1929 is the acre at the SC 11 / SC 110 junction. '
                                            'Roads, houses, woods (green) and 20-foot contours as they were in 1959.', 3.6, '1:62,500'))
    o = O['usgs-1975']; rows.append(map_row('usgs-1975', 'U.S. Geological Survey, Cowpens NE, S.C., orthophoto map, 1:24,000 (1975)', 'Photo 1975', 'USGS photo map, 1975', 'USGS, 1975', 'S109', 'usgs-1975.webp', o['corners'],
                                            {'method': o['method']}, 'An aerial photograph of 1975 drawn to scale by the USGS: the field before the park was rebuilt, with the old road bed showing pale through it. It stops at 35.125 N, the sheet\'s edge.', 2.4, '1:24,000'))
    o = O['mills-1825']; rows.append(map_row('mills-1825', 'Mills, Spartanburgh District, South Carolina (surveyed 1820, Mills\'s Atlas 1825; Union army tracing)', 'Mills 1825', 'Mills\'s Atlas, 1825', 'Mills, 1825 · Library of Congress', 'S110', 'mills-1825.webp', o['corners'],
                                            {'method': o['method'], 'rms_m': o['rms_m'], 'points': o['points']}, 'The nearest map to the time: the district surveyed in 1820, forty years after the battle, at two miles to the inch. It marks "Battle of the Cowpens" at a crossroads of four roads. '
                                            'Fitted to five places, which land 0.4 to 1 km from where they are: a map of the country, not of the field.', 22.0, '2 miles to an inch'))
    o = O['nps-park-map']; rows.append(map_row('nps-park-map', 'National Park Service, Park Map - Cowpens National Battlefield', 'Park map', 'Park map (NPS)', 'National Park Service', 'S111', 'nps-park-map.webp', o['corners'],
                                               {'method': o['method'], 'm_per_px': o['m_per_px'], 'points': o['points']}, 'The park\'s own map: the trace of the Green River Road, the trails, the monuments and the Robert Scruggs House. Its scale bar is about 27% out; it is fitted by its roads, to about 30 m.', 2.1))
    return rows


def recon_rows():
    sheet = RECON['sheet']
    rec = dict(playback_id=PB, recon_id='cowpens-1781', title='The Cowpens, January 1781: a WarMapper reconstruction', label='1781 (reconstructed)',
               about='This is a WarMapper reconstruction, not a period map: no map of 1781 shows this ground. The roads are those Edwin Bearss drew in 1967 as the roads of the battle, laid on the ground by the road the park still keeps, '
                     'and beyond his sheet the roads of the 1959 survey on the lines Mills\'s map of 1825 gives. The ground is today\'s, which the park has kept much as it was; the streams are today\'s. Nothing here has been checked by a historian.',
               file='data/recon/cowpens-1781.geojson', style='period-1899', made=TODAY, review_status='Needs review', credit='WarMapper reconstruction from Bearss, 1967 (National Park Service), the USGS sheets of 1959 and 1975, and Mills, 1825',
               notes='Inside Bearss\'s sheet the roads are good to about 25-50 m: his road matches the park\'s trace to 4 m at the median, and his other roads lie within 20-50 m of the roads of 1959. Beyond it they are roads of 1959 '
                     '(and, for Tarleton\'s approach, today\'s Green River Road), rated low. Bearss shows no other roads, houses or fields; the ground was open woods, pastured, with no undergrowth (S107, p. 8).')
    L = [('road-field', 1, 'The Mill Gap road through the field (the park\'s Green River Road)', 'road', 'S107', BEARSS_URL, 'Bearss (1967)', 'traced', 'medium',
          'The park\'s trace (OpenStreetMap), which Bearss\'s road matches to 4 m at the median.'),
         ('roads-bearss', 2, 'Bearss\'s other roads: east to Cherokee Ford, to the Pacolet, to Island Ford, west to Mill Gap', 'road', 'S107', BEARSS_URL, 'Bearss (1967)', 'traced', 'medium',
          'Separated from the plate by program (solid lines; the contours are dashed), thinned to centre lines, fitted, smoothed; each checked against the 1959 sheet (20-50 m).'),
         ('roads-beyond', 3, 'The same roads beyond Bearss\'s sheet, as the USGS drew them in 1959', 'road', 'S108', TOPOVIEW, 'USGS topoView (1959 sheet)', 'traced', 'low',
          'Picked from the 1959 sheet reprojected to WGS 84; only roads Mills (1825) has leaving the crossroads the same way.'),
         ('road-approach', 4, 'Tarleton\'s approach: today\'s Green River Road', 'road', 'S39', 'https://www.openstreetmap.org/copyright', 'OpenStreetMap', 'traced', 'low',
          'Today\'s road, the playback\'s reading of the way Tarleton came (CG06).'),
         ('streams', 5, 'Streams', 'stream', 'S39', 'https://www.openstreetmap.org/copyright', 'OpenStreetMap', 'traced', 'medium',
          'Today\'s streams; they follow the draws of the 1975 photo map and the blue lines of 1959.')]
    lay = [dict(recon_id='cowpens-1781', layer_id=a, order=o, title=t, kind=k, source_id=s, link=u, link_label=ul, method=m, confidence=c, **{'from': '1781-01-17', 'to': '1781-01-17'}, how_read=h, review_status='Needs review')
           for a, o, t, k, s, u, ul, m, c, h in L]
    return rec, lay


def angle_at(pts, frac):
    """A point along a line and the angle (clockwise from east, -90 to 90) its text should lie at."""
    xy = [G._xy((p[1], p[0])) for p in pts]; cum = [0.0]
    for a, b in zip(xy, xy[1:]): cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    d = cum[-1] * frac; i = max(1, next(k for k in range(1, len(cum)) if cum[k] >= d))
    a, b = xy[i - 1], xy[i]; f = (d - cum[i - 1]) / max(1e-9, cum[i] - cum[i - 1]); p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
    ang = -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    while ang > 90: ang -= 180
    while ang <= -90: ang += 180
    la, lo = G._ll(*p); return round(la, 5), round(lo, 5), round(ang)


def labels():
    F = {f['properties']['id']: f['geometry']['coordinates'] for f in RECON['features']}
    B = FIT['bearss']; M = np.array(B['plate1_to_ground']['M']); t = np.array(B['plate1_to_ground']['t'])
    def plate(x, y): la, lo = G._ll(*(np.array([x, -y]) @ M.T + t)); return round(la, 6), round(lo, 6)
    out = []
    def L(text, other, lat, lon, ang, level, kind, approx=None): out.append(dict(playback_id=PB, text=text, other_name=other, lat=lat, lon=lon, angle=ang, level=level, kind=kind, show='recon', approximate=approx))
    for frac, lvl in ((0.42, 0), (0.85, 1)):
        la, lo, a = angle_at(F['COW81-ROAD-FIELD'], frac); L('Mill Gap road', 'Green River Road', la, lo, a, lvl, 'road')
    la, lo, a = angle_at(F['COW81-ROAD-EAST'], 0.5); L('Mill Gap road, to Cherokee Ford', None, la, lo, a, 1, 'road')
    la, lo, a = angle_at(F['COW81-ROAD-SOUTH'], 0.45); L('to the Pacolet and Spartanburg', None, la, lo, a, 1, 'road')
    la, lo, a = angle_at(F['COW81-ROAD-NORTH'], 0.6); L('to Island Ford', None, la, lo, a, 1, 'road')
    la, lo, a = angle_at(F['COW81-ROAD-WEST'], 0.55); L('Mill Gap road, to the mountains', None, la, lo, a, 1, 'road')
    la, lo, a = angle_at(F['COW81-ROAD-GREENRIVER-S'], 0.5); L('Green River road, from Thicketty Creek', None, la, lo, a, 1, 'road')
    L('Hannah\'s Cowpens', None, 35.1345, -81.8135, None, 0, 'place', 'yes')
    la, lo = plate(2250, 960); L('Morgan\'s camp, night of 16 January (Bearss)', None, la, lo, None, 1, 'place', 'yes')
    la, lo = plate(2840, 1000); L('Militia horses picketed (Bearss)', None, la, lo, None, 2, 'place', 'yes')
    for n, la, lo, a in (('Island Creek', 35.12961, -81.82589, -26), ('Long Branch', 35.12539, -81.8076, 42), ('Zekial Creek', 35.1191, -81.79299, -34)):
        L(n, None, la, lo, a, 1, 'water')
    return out


def bases(sat):
    """The playback's bases, in button order: the reconstruction on its terrain (where the playback opens), today's map, the satellite
    view as it was, and the other maps, hidden from the menu and offered from the map details."""
    S = [('bases.1.id', 'r81t'), ('bases.1.label', '1781 with terrain'), ('bases.1.short', '1781'), ('bases.1.recon', 'cowpens-1781'),
         ('bases.1.terrain', json.dumps({'zoom': 14, 'extent': [-81.86, 35.095, -81.75, 35.165], 'open_m': 20, 'smooth_m': 20, 'relief': 3, 'spots_from': 14.4, 'doubt': False})),
         ('bases.2.id', 'mod'), ('bases.2.label', 'Current map'), ('bases.2.short', 'Today'), ('bases.2.current', True)]
    S += [('bases.3.' + k, v) for k, v in sat.items()]
    k = 4
    def hid(i, label, short, note, **kw):
        nonlocal k
        S.extend([('bases.%d.id' % k, i), ('bases.%d.label' % k, label), ('bases.%d.short' % k, short)] + [('bases.%d.%s' % (k, a), b) for a, b in kw.items()]
                 + [('bases.%d.hidden' % k, True), ('bases.%d.note' % k, note)]); k += 1
    hid('bz', 'Bearss 1967, phase by phase', 'Bearss', 'Edwin Bearss\'s four troop-movement maps for the National Park Service (1967), each shown for its phase of the battle as the clock runs. His unit symbols are on them.', series=True, backdrop='current')
    hid('l28', 'Army War College sketch, 1928', '1928', 'Landers\'s sketch of the ground as it was in 1928: roads, houses, woods and 5-foot contours, with the two lines.', map='landers-1928-1', backdrop='current')
    hid('l28f', 'Army War College formation, 1928', '1928 F', 'The Army War College\'s diagram of the two lines as they formed (1928).', map='landers-1928-2', backdrop='current')
    hid('u59', 'USGS map, 1959', '1959', 'The oldest survey map of the ground, before the park was rebuilt: SC 11 still on the old road.', map='usgs-1959', backdrop='current')
    hid('u75', 'USGS photo map, 1975', '1975', 'An aerial photograph of 1975 drawn to scale: the field before the park was rebuilt.', map='usgs-1975', backdrop='current')
    hid('m25', 'Mills\'s Atlas, 1825', '1825', 'The nearest map to the time: the district at two miles to the inch, surveyed in 1820. It marks the battle at a crossroads. Good to about a kilometre.', map='mills-1825', backdrop='current')
    hid('nps', 'Park map (NPS)', 'Park', 'The National Park Service\'s map of the park today: trails, monuments and the trace of the road.', map='nps-park-map', backdrop='current')
    S.append(('start_base', 'r81t'))
    return S


def main():
    sh = openpyxl.load_workbook(SHARED); wb = openpyxl.load_workbook(WAR)
    src = sh['Sources']; ids = rows_by_id(src)
    assert 'S108' not in ids, 'S108 is already in Sources and notes.xlsx: this script has run'
    for s in SOURCES: add(src, s)
    setv(src, ids['S107'], 'may_host', 'yes')
    setv(src, ids['S107'], 'rights', add_note('24 Nov 2026: the title page reads Office of Archeology and Historic Preservation, National Park Service, U.S. Department of the Interior, and the copy has no copyright notice or reprint imprint: the four plates are hosted.'))
    setv(src, ids['S107'], 'notes', add_note('24 Nov 2026: the four plates are fitted to the ground (pipeline/georef/cowpens_bearss.py) and shown as one base that follows the clock; once the scans are registered the plates agree with each other (the offsets of 30-70 m were the scans\'). His roads are the roads of the reconstructed map.'))
    setv(src, ids['S103'], 'page verified?', add_note('24 Nov 2026: plates 1 and 2 (facing p. 78) seen and fitted to the ground.'))
    cand = sh['Source candidates']; cids = rows_by_id(cand)
    if 'SC-SOU08' in cids:
        setv(cand, cids['SC-SOU08'], 'status', 'used: plates of S103')
        setv(cand, cids['SC-SOU08'], 'notes', add_note('24 Nov 2026: both Cowpens plates fetched by Morgan from archive.org, fitted to the ground and offered as other maps.'))
    rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026 (later): a reconstructed 1781 map of the Cowpens, and nine other maps of the ground')
    rm.cell(2, 1, 'Revolutionary War.xlsx, Cowpens only: a WarMapper reconstruction of the ground in January 1781 (Reconstructions, Recon layers; data/recon/cowpens-1781.geojson), on today\'s terrain, is the base the playback opens on. '
                  'Nine other maps are fitted to the ground and offered under "Other maps of this ground": Bearss\'s four plates of 1967 (one base that follows the clock), Landers\'s two sketches of 1928, the USGS sheets of 1959 and 1975, Mills\'s map of 1825 and the park map. '
                  'New sources S108 to S111; S107 may be hosted. Gap CG02 closed; a note on CG06. Written by pipeline/cowpens_period_maps_2026_11_24.py.')
    # the war workbook
    mp = wb['Maps']
    for r in maps(): add(mp, r)
    rec, lay = recon_rows(); add(wb['Reconstructions'], rec)
    for l in lay: add(wb['Recon layers'], l)
    for l in labels(): add(wb['Labels'], l)
    ps = wb['Playback settings']
    old = {ps.cell(r, 2).value: r for r in range(2, last_row(ps) + 1) if ps.cell(r, 1).value == PB}
    assert 'start_base' not in old, 'cowpens already has a start_base'
    sat = {k[len('bases.2.'):]: ps.cell(r, 3).value for k, r in sorted(old.items(), key=lambda x: x[1]) if k.startswith('bases.2.')}
    assert sat.get('id') == 'sat', sat
    for k, r in sorted(old.items(), key=lambda x: -x[1]):      # the two old base rows' settings are rewritten below, with the new ones
        if k.startswith('bases.'): ps.delete_rows(r)
    S = bases(sat); at = last_row(ps) + 1
    for k2, v in S:
        ps.cell(at, 1, PB); ps.cell(at, 2, k2); ps.cell(at, 3, v); at += 1
    ps.cell(at, 1, PB); ps.cell(at, 2, 'about.8')
    ps.cell(at, 3, 'The playback opens on "1781 with terrain", a reconstruction: the roads Edwin Bearss drew in 1967 as the roads of the battle, laid on the ground by the road the park still keeps, and today\'s ground, which the park has kept open. '
                   'The map details (the i button) list each road with its source and how sure it is, and offer the other maps of this ground: Bearss\'s own maps phase by phase, the Army War College sketches of 1928, the USGS maps of 1959 and 1975, Mills\'s map of 1825 and the park map.')
    gp = wb['Gaps']; gids = rows_by_id(gp)
    setv(gp, gids['CG02'], 'status in v2', 'Closed, 24 Nov 2026: the playback opens on a reconstruction drawn from Bearss\'s roads (S107), and Bearss\'s plates, Landers\'s sketches (S103), the USGS sheets of 1959 and 1975 (S108, S109), Mills (S110) and the park map (S111) are fitted to the ground and offered as other maps.')
    setv(gp, gids['CG06'], 'how to close it', add_note('24 Nov 2026: the maps show the probable line. Bearss\'s Mill Gap road leaves the east end of the trace east-north-east (S107; a road in 1959, S108, and a track in 1975, S109); '
                                                     'a road of 1959 that Landers (1928, S103) names "Green River Road" runs from it south to the north end of today\'s Green River Road. The reconstruction draws that way (rated low). Route RC01 is not changed: that needs Morgan\'s approval.'))
    su = wb['Source uses']
    for s in SOURCES:
        r = last_row(su) + 1
        add(su, dict(source_id=s['source_id'], title=s['title'], campaign_id='ARW-SOU', playback_id=PB,
                     positions='=COUNTIFS(Positions!$X:$X,"*"&$A%d&"*",Positions!$B:$B,$C%d)' % (r, r), events='=COUNTIFS(Events!$I:$I,"*"&$A%d&"*",Events!$B:$B,$C%d)' % (r, r),
                     routes='=COUNTIFS(Routes!$K:$K,"*"&$A%d&"*",Routes!$B:$B,$C%d)' % (r, r), units='=COUNTIFS(Units!$J:$J,"*"&$A%d&"*",Units!$A:$A,"C-*")' % r,
                     period_maps='=COUNTIFS(Maps!$G:$G,$A%d,Maps!$A:$A,$D%d)' % (r, r), total='=SUM(E%d:I%d)' % (r, r)))
    wb['Read me'].append(['Cowpens period maps (24 Nov 2026)', 'A reconstructed 1781 base map (the playback opens on it) and nine other maps of the ground fitted to it; sources S108 to S111; CG02 closed. See the change log in "Sources and notes.xlsx" and pipeline/cowpens_period_maps_2026_11_24.py.'])
    wb.save(WAR); sh.save(SHARED)
    print('written: %d maps, %d recon layers, %d labels, %d base settings' % (len(maps()), len(lay), len(labels()), len(S)))


if __name__ == '__main__':
    main()
