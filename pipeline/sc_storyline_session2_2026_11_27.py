"""SC storyline, Session 2 (27 Nov 2026, Opus): the regional base map. Workbook rows.

  python3 -I pipeline/sc_storyline_session2_2026_11_27.py

Run after pipeline/recon/sc_1775.py has written data/recon/sc-1775.geojson (North Carolina to 77 W and the Dan). It writes:
  Sources and notes.xlsx  Sources S151 (Collet 1770); a Read me entry.
  Revolutionary War.xlsx  Reconstructions and Recon layers (sc-1775 is now the Carolinas); Labels: a `recon` column (the reconstruction a
                          name belongs to, for the regional hand-off), the North Carolina towns and rivers, and the recon of the
                          names already there; Playback settings: sc-orientation's terrain widened to the chapter's window
                          (84.9 W to 75.5 W, 30.9 N to 37.6 N, Session 1 question 13b); Cowpens and Guilford Courthouse: the regional map
                          under the battlefield (bases.1.region, a hidden regional base, groups, opening_zoom_out 4, as Session 1 designed);
                          Maps: Mouzon fitted, both Carolinas; Georeference: the North Carolina controls.
"""
import json, math, os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, 'recon'))
import sc_1775 as RC
WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
SHARED = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
PB, RID = 'sc-orientation', 'sc-1775'
# Tile zoom of the terrain over the window, measured 27 Nov 2026 on an emulated phone (390 x 844, CPU slowed 4 times, 9 Mbit/s): sc-orientation at
# zoom 9 over the window 30.8 s and 17.3 MB until the relief is drawn (on main, zoom 9 over South Carolina's old extent: 22.5 s, 11.6 MB); at zoom 8
# 13.2 s, 9.1 MB; Cowpens with the region at zoom 8 15.4 s, 10.4 MB (at zoom 9 30.8 s, 18.2 MB). Zoom 8 is visibly coarser close in (around
# Camden at 5 km to the scale bar), so the orientation keeps zoom 9, its reviewed look; the battles' regional map, seen only zoomed out, takes 8.
ZOOM = int(os.environ.get('TERRAIN_ZOOM', '9')); REGION_ZOOM = int(os.environ.get('REGION_ZOOM', '8'))
WINDOW = [-84.9, 30.9, -75.5, 37.6]


def headers(ws): return [c.value for c in ws[1]]


def upsert(ws, keycols, row):
    h = headers(ws); ki = [h.index(k) for k in keycols]
    for r in ws.iter_rows(min_row=2):
        if all(r[i].value == row[k] for i, k in zip(ki, keycols)):
            for k, v in row.items():
                if k in h: r[h.index(k)].value = v
            return 'updated'
    ws.append([row.get(c) for c in h]); return 'added'


def setting(ws, pb, key, value, what=None, why=None):
    h = headers(ws)
    for r in ws.iter_rows(min_row=2):
        if r[h.index('playback_id')].value == pb and r[h.index('setting')].value == key:
            r[h.index('value')].value = value
            if what is not None: r[h.index('what it does')].value = what
            if why is not None: r[h.index('why')].value = why
            return 'updated'
    ws.append([{'playback_id': pb, 'setting': key, 'value': value, 'what it does': what, 'why': why}.get(c) for c in h]); return 'added'


def get_setting(ws, pb, key):
    h = headers(ws)
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[h.index('playback_id')] == pb and r[h.index('setting')] == key: return r[h.index('value')]


SOURCE = {'source_id': 'S151', 'title': 'A compleat map of North-Carolina from an actual survey', 'author': 'John Collet; engraved by John Abraham Bayly; published by Samuel Hooper',
          'date': '1770', 'type': 'Period map: printed map of North Carolina at about nine miles to the inch',
          'citation': 'John Collet, A Compleat Map of North-Carolina from an Actual Survey (London: S. Hooper, 1 May 1770). Library of Congress, Geography and Map Division, G3900 1770 .C6, copy 1 (g3900.ar150000).',
          'page verified?': 'n/a (a map)', 'url': 'https://www.loc.gov/item/83693769/',
          'rights': 'Published 1770. Public domain; the Library of Congress gives its digitized maps as free to use and reuse.',
          'notes': 'Read 27 Nov 2026 from the Library of Congress IIIF service (service:gmd:gmd390:g3900:g3900:ar150000, 13,949 x 9,524). Used to cross-check, by eye, the North Carolina '
                   'names and roads traced from Mouzon (S135), which for North Carolina follows it closely: the Trading Path, the road by Bowes Ordinary to New Garden, the Western or '
                   'Trading Path to Hillsborough, the Shallow Ford road, Hillsborough to Granville and Bute court houses. Spellings differ (Mouzon "Balten", Collet "Batten"; '
                   '"Bows Ord", "Bowes Ord"; "Charlottesburg", "Charlottesburgh"). Not traced, not fitted, not hosted.',
          'used_for': 'SC-ORI (the regional map: North Carolina)', 'kind': 'map', 'war': 'ARW', 'rights_status': 'public domain', 'may_host': 'yes', 'rights_checked': '2026-11-27', 'site': 'loc.gov'}

ABOUT = ("This is a WarMapper reconstruction, not a period map. Its lines are those of Henry Mouzon's map of the two Carolinas (1775), laid on today's ground: the rivers and "
         "the sea coast fitted to today's courses, which they keep, and the main roads and boundary lines carried with them. Mouzon's map was made for the colonies' trade and land "
         "grants, not as a survey: his roads are good to a few kilometres, his up-country less. South Carolina is traced at the level of its main lines; North Carolina (since 27 Nov 2026) "
         "only for the ground of the campaign of 1781, from Charlotte and Salisbury to Guilford, Hillsborough, Halifax and the Dan. Nothing here has been checked by a historian.")
NOTE = ("Rivers and coast good to about 1-2 km where today's river is in Natural Earth; roads and boundaries to 3-5 km; the far north-west to no better than 10 km. In North Carolina "
        "nine towns hold the fit, each found again 1.3-6.6 km from its site when left out. Not yet traced: inlets, islands and sounds, swamps, the lesser roads, ferries and fords; in "
        "North Carolina the Neuse, the Tar and the sounds (east of 77 W, beyond the sheet), the rivers and roads of the mountains and of the east, and Mouzon's towns other than those named. "
        "Guilford Court House is not on Mouzon's map (it was built in 1774): its name is placed where the battle's playback has it.")
CREDIT = 'WarMapper reconstruction from Mouzon, 1775 (Library of Congress), fitted with Natural Earth; North Carolina checked against Collet, 1770 (Library of Congress)'
HOW_NC = {'rivers': ' North Carolina (27 Nov 2026): the Catawba and Broad above the 1772 line, the Yadkin to the Pee Dee, the Haw with Reedy Fork and Troublesome Creek, the Deep, the Cape Fear, the Dan and the Roanoke, picked and snapped the same way and matched to Natural Earth (Reedy Fork and Troublesome Creek, which it lacks, follow the fit and are low).',
          'coast': ' North Carolina (27 Nov 2026): the outer coast from Little River past Cape Fear to Bogue, to the sheet\'s edge at 77 W; the sea is closed across the inlets and the mouth of the Cape Fear.',
          'roads': ' North Carolina (27 Nov 2026): ten roads of the 1781 campaign\'s ground, snapped the same way: Charlotte and Camden to Salisbury, the Trading Path to Hillsborough, the road by the Quaker meeting houses to Guilford and the Haw, Salem towards the Dan, the Shallow Ford road, Hillsborough to Halifax and north towards the Dan, Salisbury to Oliphant\'s Mill. Checked against Collet 1770 (S151).',
          'boundaries': ' North Carolina (27 Nov 2026): the line between Virginia and North Carolina, found from Mouzon\'s red, column by column, and fitted to today\'s state line.'}

TOWNS = [  # text, other name, M on the scan, level  (names as Mouzon spells them, except where noted)
    ('Charlotte', None, (3112, -79), 0), ('Salisbury', None, (3483, -588), 0), ('Salem', 'Old Salem, Winston-Salem', (3743, -1068), 2),
    ('Bethabara', None, (3717, -1135), 2), ('Bethania', None, (3632, -1155), 2), ('Hillsborough', None, (4772, -1057), 0),
    ('Halifax', None, (6094, -1235), 0), ('Cross Creek', 'Fayetteville', (4940, 70), 1), ('Wilmington', None, (5738, 1300), 0)]
RIVERS = [('Yadkin River', 0), ('Dan River', 0), ('Cape Fear River', 0), ('Roanoke River', 1), ('Haw River', 1), ('Deep River', 1), ('Reedy Fork', 2), ('Troublesome Creek', 2)]


def river_label(name, level, feats):
    F = [f for f in feats if f['properties'].get('kind') == 'stream' and f['properties'].get('name') == name and f['properties']['id'].startswith('NC75')]
    if not F: return None
    c = max(F, key=lambda f: len(f['geometry']['coordinates']))['geometry']['coordinates']; i = len(c) // 2
    a, b = c[max(0, i - 3)], c[min(len(c) - 1, i + 3)]
    ang = math.degrees(math.atan2(-(b[1] - a[1]) * 110.9, (b[0] - a[0]) * 92.8))
    ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
    return {'playback_id': PB, 'text': name, 'other_name': None, 'lat': round(c[i][1], 5), 'lon': round(c[i][0], 5), 'angle': round(ang), 'level': level, 'kind': 'water',
            'show': 'recon', 'approximate': None, 'recon': RID}


def terrain_json(old, zoom):
    t = json.loads(old); t['extent'] = WINDOW; t['zoom'] = zoom
    px = {8: 500, 9: 250}[zoom]
    t['about'] = ("In the United States these tiles come from the USGS's National Elevation Dataset, a survey of the bare ground with no buildings or trees in it. Over the two Carolinas "
                  "they are read at about %d m a pixel, so bumps narrower than about %d m are taken off and the rest smoothed. This is today's ground. The big lakes (Marion, Moultrie, "
                  "Murray, Wateree, Hartwell, Thurmond and Keowee in South Carolina; Norman, High Rock, Badin, Tillery, Jordan, Falls, Kerr and Gaston further north) are reservoirs of the "
                  "20th century: their flat floors are today's water, and in 1775 the rivers ran in their valleys." % (px, max(300, px + 50)))
    t['beyond'] = ("Beyond the dotted line Mouzon's map stops (north at the Dan, east at 77 W, and the west edge of his South Carolina): only today's relief and sea are drawn there, so "
                   "the map fills the window.")
    return json.dumps(t)


def main():
    wb = openpyxl.load_workbook(SHARED)
    print('Sources S151', upsert(wb['Sources'], ['source_id'], SOURCE))
    rm = wb['Read me']
    if not str(rm.cell(1, 1).value or '').startswith('What changed on 27 November 2026: the regional base map'): rm.insert_rows(1, 3)
    rm.cell(1, 1).value = 'What changed on 27 November 2026: the regional base map (SC storyline, Session 2)'
    rm.cell(2, 1).value = ('Revolutionary War.xlsx: the reconstruction sc-1775 now holds North Carolina to 77 W and the Dan (data/recon/sc-1775.geojson, 67 features: 23 new, NC75-...; '
                           'no South Carolina line moves more than 22 m). Labels gain a recon column; the North Carolina towns and rivers are named. sc-orientation\'s terrain covers the '
                           'chapter\'s window (84.9 W to 75.5 W, 30.9 N to 37.6 N) at tile zoom %d (the battles\' regional map at %d). Cowpens and Guilford Courthouse open on the regional map and ease in to the field '
                           '(bases.1.region, a hidden base rgn, groups, opening_zoom_out 4). Mouzon fitted (the map details) covers both Carolinas. Sources: S151 Collet 1770. Scripts: '
                           'pipeline/recon/nc_1775_*_2026_11_27.py, pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py, pipeline/georef/carolinas_mouzon_picture_2026_11_27.py, '
                           'pipeline/sc_storyline_session2_2026_11_27.py.' % (ZOOM, REGION_ZOOM))
    wb.save(SHARED)

    G = json.load(open(RC.OUT)); feats = G['features']
    wb = openpyxl.load_workbook(WAR)
    print('Reconstructions', upsert(wb['Reconstructions'], ['recon_id'], {'recon_id': RID, 'title': 'The Carolinas, 1775 to 1781: a WarMapper reconstruction', 'about': ABOUT, 'notes': NOTE, 'credit': CREDIT}))
    ws = wb['Recon layers']; h = headers(ws)
    for r in ws.iter_rows(min_row=2):
        lid = r[h.index('layer_id')].value
        if r[h.index('recon_id')].value == RID and lid in HOW_NC and 'North Carolina (27 Nov 2026)' not in (r[h.index('how_read')].value or ''):
            r[h.index('how_read')].value = (r[h.index('how_read')].value or '') + HOW_NC[lid]
    # Labels: a recon column; the names of a reconstruction say so
    ws = wb['Labels']; h = headers(ws)
    if 'recon' not in h: ws.cell(1, len(h) + 1).value = 'recon'; h = headers(ws)
    own = {'sc-orientation': RID, 'cowpens': 'cowpens-1781', 'guilford-courthouse': 'guilford-1781'}
    for r in ws.iter_rows(min_row=2):
        pb = r[h.index('playback_id')].value; show = r[h.index('show')].value
        if pb in own and show in ('recon', 'both') and not r[h.index('recon')].value: r[h.index('recon')].value = own[pb]
    for t, other, m, lvl in TOWNS:
        lon, lat = RC.ground([m])[0]
        upsert(ws, ['playback_id', 'text', 'show'], {'playback_id': PB, 'text': t, 'other_name': other, 'lat': round(lat, 5), 'lon': round(lon, 5), 'angle': None, 'level': lvl,
                                                     'kind': 'town', 'show': 'recon', 'approximate': 'yes', 'recon': RID})
    upsert(ws, ['playback_id', 'text', 'show'], {'playback_id': PB, 'text': 'Guilford Court House', 'other_name': None, 'lat': 36.135127, 'lon': -79.834392, 'angle': None, 'level': 0,
                                                 'kind': 'town', 'show': 'recon', 'approximate': None, 'recon': RID})   # not on Mouzon: where the battle's playback has it
    for nm, lvl in RIVERS:
        r = river_label(nm, lvl, feats)
        if r: upsert(ws, ['playback_id', 'text', 'show'], r)
    # Playback settings: 1a's terrain over the window; the battles' regional hand-off
    ws = wb['Playback settings']
    old = get_setting(ws, PB, 'bases.1.terrain'); terr = terrain_json(old, ZOOM); rterr = terrain_json(old, REGION_ZOOM)
    print(PB, 'terrain', setting(ws, PB, 'bases.1.terrain', terr))
    setting(ws, PB, 'bases.3.note', "Henry Mouzon's map of the two Carolinas (1775), which the reconstruction is traced from, resampled onto the ground. Good to a few kilometres; stretched at the edges of the sections it was mounted in.")
    REG_NOTE = ("Mouzon's map of the two Carolinas (1775) as a WarMapper reconstruction: the ground the battle was part of, from the Savannah to the Dan. Zoomed out, each side is one symbol; "
                "zoom in and the battlefield's own map fades in over it.")
    for pb, n, groups in [('cowpens', 11, [{'side': 'US', 'below': 0.03, 'label': "Morgan's detachment", 'echelon': 'detachment'}, {'side': 'CR', 'below': 0.03, 'label': "Tarleton's detachment", 'echelon': 'detachment'}]),
                          ('guilford-courthouse', None, [{'side': 'US', 'below': 0.03, 'label': "Greene's army", 'echelon': 'army'}, {'side': 'CR', 'below': 0.03, 'label': "Cornwallis's army", 'echelon': 'army'}])]:
        h2 = headers(ws); used = [int(str(r[h2.index('setting')]).split('.')[1]) for r in ws.iter_rows(min_row=2, values_only=True) if r[h2.index('playback_id')] == pb and str(r[h2.index('setting')] or '').startswith('bases.')]
        have = [int(str(r[h2.index('setting')]).split('.')[1]) for r in ws.iter_rows(min_row=2, values_only=True) if r[h2.index('playback_id')] == pb and r[h2.index('setting')] and str(r[h2.index('setting')]).endswith('.id') and r[h2.index('value')] == 'rgn']
        k = have[0] if have else max(used) + 1
        setting(ws, pb, 'bases.1.region', 'rgn', 'The regional map under the battlefield (since 27 Nov 2026, Morgan\'s option B): zoom out to the region', 'SC storyline Session 1, question 13 (27 Nov 2026)')
        for key, val in [('id', 'rgn'), ('label', 'The Carolinas, 1775 to 1781'), ('short', 'Region'), ('recon', RID), ('hidden', True), ('note', REG_NOTE), ('terrain', rterr)]:
            setting(ws, pb, 'bases.%d.%s' % (k, key), val)
        setting(ws, pb, 'groups', json.dumps(groups), 'Zoomed right out, each side is one symbol', 'SC storyline: one symbol a side on the regional map (Session 1, 27 Nov 2026)')
        setting(ws, pb, 'opening_zoom_out', 4, 'The page opens this many zoom levels wider than its first view, on the regional map, then eases in', 'SR-02, SR-04; SC storyline Session 1 (27 Nov 2026)')
        print(pb, 'region base', k)
    # Maps: Mouzon fitted, both Carolinas
    W_, S_, E_, N_ = G['sheet']
    F = json.load(open(os.path.join(ROOT, 'pipeline', 'georef', 'sc_mouzon_fit.json')))
    loo = {p['name']: p.get('loo_m') for p in F['PC'] if p.get('added') == '2026-11-27' and p.get('loo_m')}
    print('Maps', upsert(wb['Maps'], ['playback_id', 'map_id'], {'playback_id': PB, 'map_id': 'mouzon-1775-fitted',
        'title': 'Mouzon, An accurate map of North and South Carolina (1775), fitted to the ground', 'size_px': '5000,4509',
        'tl_lat': N_, 'tl_lon': W_, 'tr_lat': N_, 'tr_lon': E_, 'br_lat': S_, 'br_lon': E_, 'bl_lat': S_, 'bl_lon': W_,
        'fit': json.dumps({'method': 'thin-plate spline with a plane for each section of the cloth-mounted copy, from point controls and the rivers, coast and state lines matched to Natural Earth '
                                     '(pipeline/georef/sc_mouzon_fit.py, the refit of 26 Nov 2026, and its extension to North Carolina, sc_mouzon_fit_nc_2026_11_27.py); the picture is the scan resampled onto the ground (Web Mercator)',
                           'controls': len(F['PC']) - 1, 'loo_km_nc': {k: round(v / 1000, 1) for k, v in loo.items()}}),
        'note': 'Resampled from half-resolution crops of the Library of Congress scan (pipeline/georef/carolinas_mouzon_picture_2026_11_27.py). The bands and the wedge in the middle are '
                'the gaps between the sections of the cloth-mounted copy; at the edges of the sections, and in the corners, the picture is stretched. Mouzon\'s two harbour insets are left out.'}))
    # Georeference: the North Carolina controls
    ws = wb['Georeference']
    if not any(str(c.value or '').startswith('Georeference: North Carolina, Mouzon 1775') for c in ws['A']):
        ws.append([]); ws.append(['Georeference: North Carolina, Mouzon 1775 (27 Nov 2026)'])
        ws.append(['The fit of South Carolina extended north and east (pipeline/georef/sc_mouzon_fit_nc_2026_11_27.py): every vertex of the reviewed South Carolina lines held where it was '
                   '(none moves more than 22 m), nine North Carolina towns as point controls, a tie across the vertical gap on the Pee Dee, and the North Carolina rivers, coast and Virginia '
                   'line matched to Natural Earth (S136). Pixels as in South Carolina\'s block, carried past its crop (negative y is north of it).'])
        ws.append([]); ws.append(['Control point', 'pixel x', 'pixel y', 'lat', 'lon', 'misfit left out (m)', 'source'])
        for p in F['PC']:
            if p.get('added') == '2026-11-27': ws.append([p['name'], p['m'][0], p['m'][1], p['lonlat'][1], p['lonlat'][0], p.get('loo_m'), p['source']])
    wb.save(WAR); print('saved')


if __name__ == '__main__':
    main()
