"""South Carolina orientation, Session 4 (25 Nov 2026, Opus): the reconstructed period base map, a pilot for Morgan's look check.

Adds to the workbooks, idempotently (run it again and nothing changes):
- Sources and notes.xlsx: S135 (Mouzon 1775, the map traced) and S136 (Natural Earth, used to fit it to the ground); candidate rows
  SC-MAP01 to SC-MAP14 for the other maps and studies found and not yet read or traced, each with its rights.
- Revolutionary War.xlsx: the Reconstructions row sc-1775 and its four Recon layers; the names read from Mouzon for it (Labels, show
  recon); the fitted picture of Mouzon's map as a map (Maps, mouzon-1775-fitted); the bases of the sc-orientation playback (the
  reconstruction with terrain first, the modern map, Mouzon's map in the map details); a Georeference block saying how Mouzon was fitted.

Source ids S131 to S134 are left free: Session 3 (branch sc-orientation-winners-control, not on main when this ran) uses them.

  python3 -I pipeline/recon/sc_1775.py
  python3 -I pipeline/sc_orientation_session4_2026_11_25.py
  python3 tools/export_battles.py
"""
import json, math, os, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'recon'))
import sc_1775 as RC
FOLDER = os.path.join(ROOT, 'data', 'WarMapper battle data')
SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx'); WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx')
PB = 'sc-orientation'; RID = 'sc-1775'
TODAY = '2026-11-25'
MOUZON_ITEM = 'https://www.loc.gov/item/74692510/'
MOUZON_IIIF = 'https://tile.loc.gov/image-services/iiif/service:gmd:gmd390:g3900:g3900:ar139404'

SOURCES = [
    dict(source_id='S135', title='An accurate map of North and South Carolina with their Indian frontiers', author='Henry Mouzon and others; engraved by Samuel Turner Sparrow; published by Robert Sayer and John Bennett',
         date='1775', type='Period map: printed map of both provinces at about 1:530,000 (69 1/2 miles to a degree), with insets of Port Royal and Charleston harbours',
         citation='Henry Mouzon and others, An Accurate Map of North and South Carolina with Their Indian Frontiers ... London: Robert Sayer and J. Bennett, 30 May 1775. 1 map on 2 sheets, 101 x 142 cm. '
                  'Library of Congress, Geography and Map Division, G3900 1775 .M61 (LCCN 74692510); the copy scanned is g3900.ar139404 (16,912 x 12,132 pixels).',
         **{'page verified?': 'n/a (a map)'}, url=MOUZON_ITEM,
         rights='Published 1775. Public domain; the Library of Congress gives its digitized maps as free to use and reuse ("Library of Congress, Geography and Map Division").',
         notes='Read 25 Nov 2026 from the Library of Congress IIIF service (%s), as a half-resolution crop of the South Carolina part (full scan x 0-11,800, y 3,600-11,800). '
               'Traced for the pilot of the reconstructed base map of the South Carolina orientation: the rivers, sea coast, main roads, the Cherokee boundary and the lines with North Carolina. '
               'The copy is sectioned and mounted on cloth: the sections are fitted one by one (pipeline/georef/sc_mouzon_fit.py). Mouzon names the districts "Precincts".' % MOUZON_IIIF,
         used_for='SC-ORI', kind='map', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='loc.gov', local_copy='', page_offset='', part_of=''),
    dict(source_id='S136', title='Natural Earth 1:10m physical vectors (rivers and lake centrelines, rivers of North America, coastline, state lines)', author='Natural Earth (Nathaniel Vaughn Kelso, Tom Patterson and contributors)',
         date='2026 (version 5)', type='Current map data', citation='Natural Earth, 1:10m: ne_10m_rivers_lake_centerlines, ne_10m_rivers_north_america, ne_10m_coastline, ne_10m_admin_1_states_provinces_lines (GeoJSON from github.com/nvkelso/natural-earth-vector, downloaded 25 Nov 2026).',
         **{'page verified?': 'n/a'}, url='https://www.naturalearthdata.com/about/terms-of-use/', rights='Public domain (Natural Earth terms of use: no permission needed, credit optional).',
         notes='Used only to lay Mouzon 1775 on the ground: the meeting of rivers, the river mouths and the state line at the sea as point controls, and its rivers, coast and North Carolina line as lines to fit Mouzon\'s to. Generalized for 1:10,000,000: good to about half a kilometre to a kilometre. Nothing of it is drawn on the map.',
         used_for='SC-ORI', kind='dataset', war='ARW', rights_status='public domain', may_host='yes', rights_checked=TODAY, site='naturalearthdata.com', local_copy='', page_offset='', part_of=''),
]

CANDIDATES = [
    ('SC-MAP01', 'A map of South Carolina and a part of Georgia (De Brahm, revised by John Stuart; Faden, 1780)', 'Library of Congress, G&M (LCCN 74692514; scan g3910.ct001281, 18,140 x 20,449)', 'https://www.loc.gov/item/74692514/',
     'The low country and midlands at about twice Mouzon\'s scale, revised in 1780 from the Indian superintendent\'s surveys: coast, islands, rivers, parishes, roads and bridges. Does not reach the up-country (Ninety Six district north of the Saluda, the Cowpens).',
     'IIIF scan reachable; looked at whole, not traced.', 'Published 1780; public domain (LOC: free to use).', 'located', 'P1', 'Next: trace the coast, Sea Islands and low-country roads from it, at closer zooms than Mouzon.'),
    ('SC-MAP02', 'A map of the province of South Carolina (James Cook, 1773)', 'Library of Congress, G&M (LCCN 74692124); also David Rumsey Map Collection', 'https://www.loc.gov/item/74692124/',
     'The province survey commissioned in 1770, at about 1:600,000: rivers, roads, ferries, bridges, swamps, parishes, churches, townships and the new line of 1772. Mouzon used it.',
     'Catalogue read; scan not yet opened.', 'Published 1773; public domain.', 'located', 'P1', 'A second reading of the roads and ferries; its IIIF id is still to be found.'),
    ('SC-MAP03', 'A map of South Carolina and a part of Georgia (De Brahm, Jefferys, 1757)', 'Library of Congress, G&M (LCCN 75693002)', 'https://www.loc.gov/item/75693002/',
     'The first state of SC-MAP01: the coast surveyed in the 1750s.', 'Catalogue read.', 'Published 1757; public domain.', 'located', 'P2', 'For the coast only, if Faden 1780 needs a check.'),
    ('SC-MAP04', 'A sketch of the environs of Charlestown in South Carolina (George F. Sproule, 1780)', 'Library of Congress, G&M (gm71000637)', 'https://www.loc.gov/item/gm71000637/',
     'British engineer\'s sketch of the country round Charleston during the siege.', 'Catalogue read.', '1780; public domain.', 'located', 'P1', 'Candidate for the Charleston close-up ink (Morgan, 25 Nov 2026: after the pilot).'),
    ('SC-MAP05', 'A sketch of the operations before Charlestown, the capital of South Carolina (J. F. W. Des Barres, 1780)', 'Library of Congress (LCCN 73691556); New York Public Library', 'https://www.loc.gov/item/73691556/',
     'Printed plan of the siege with an inset of Charlestown harbour (about 1:43,000).', 'Catalogue read.', '1780; public domain.', 'located', 'P1', 'Candidate for the Charleston close-up ink.'),
    ('SC-MAP06', 'Plan de la ville de Charlestown, de ses retranchements et du siege faits par les Anglois en 1780', 'Library of Congress, G&M (manuscript)', 'https://collections.leventhalmap.org/search/commonwealth:q524nc51v',
     'Manuscript plan of the town, its lines and the British siege works.', 'Listing read (ARGO).', '1780; public domain (LOC).', 'located', 'P1', 'Candidate for the 1780 siege lines on the reconstruction (dated).'),
    ('SC-MAP07', 'The investiture of Charleston, S.C. by the English army in 1780, with the position of each corps', 'Library of Congress, G&M (gm71000638), manuscript, about 1:17,500', 'https://www.loc.gov/item/gm71000638/',
     'Manuscript plan of the siege with the British corps.', 'Catalogue read.', '1780; public domain.', 'located', 'P2', ''),
    ('SC-MAP08', 'Plan of the siege of Charlestown in South Carolina (Faden, for Tarleton\'s History, 1787)', 'New York Public Library; Leventhal Map Center (Mount Vernon copy)', 'https://digitalcollections.nypl.org/items/b443bc10-538d-0135-4240-0008547c5997',
     'Printed siege plan.', 'Listing read.', '1787; public domain.', 'located', 'P2', ''),
    ('SC-MAP09', 'A plan of the attack of Fort Sulivan, near Charles Town in South Carolina (Faden, 1776)', 'Library of Congress, G&M', 'https://www.loc.gov/maps/?q=attack+of+fort+sulivan',
     'Plan of Sullivan\'s Island and the attack of 28 June 1776.', 'Named in the University of South Carolina\'s Pinckney papers map list; not opened.', '1776; public domain.', 'located', 'P2', 'Item address to be confirmed.'),
    ('SC-MAP10', 'Atlas of the State of South Carolina (Robert Mills, 1825): the state map and the district maps', 'Library of Congress; David Rumsey Map Collection; South Carolina State Library', 'https://www.loc.gov/item/2007627909/',
     'District maps at two miles to an inch, surveyed 1816-20: the first survey-grade roads and towns of the whole state, 44 years after the war.', 'Spartanburgh sheet read for Cowpens (S110).', '1825; public domain.', 'located', 'P1',
     'For the roads between Mouzon\'s picks: a road on Mills\'s sheet on the line Mouzon gives (as at Cowpens).'),
    ('SC-MAP11', 'Park handbooks and maps: Cowpens, Kings Mountain, Ninety Six (National Park Service)', 'National Park Service', 'https://www.nps.gov/nisi/',
     'Park maps of the forts and lines; handbooks on the southern campaign.', 'Ninety Six pages read in Session 3 (S128).', 'US government works: public domain.', 'located', 'P2', ''),
    ('SC-MAP12', 'Pearson and Woodward, US Army staff and war college studies of the southern campaign (DTIC)', 'Defense Technical Information Center', 'https://discover.dtic.mil/',
     'Studies of Greene\'s campaign; maps.', 'Not found or read in this session.', 'US government works: public domain.', 'to find', 'P2', 'Named in the prompt; to be read before use.'),
    ('SC-MAP13', 'Ward, The War of the Revolution, vol. 2, ch. 68 "Before Cowpens"', 'Morgan\'s PDF from Canvas', '',
     'The narrative before Cowpens.', 'Not read: Morgan\'s folder was not reachable (as in Session 3, gap SCG06).', 'In copyright: read for cross-checking, cite by page, never host.', 'located', 'P1', ''),
    ('SC-MAP14', 'Mouzon 1775, other digitized copies (Newberry Library; Boston Public Library; University of Georgia; East Carolina University; UNC)', 'Newberry (Ayer 133 .M888 1775); Leventhal Map Center; Digital Library of Georgia; ECU MC0016; UNC North Carolina Maps', 'https://collections.newberry.org/archive/-2KXJ8ZSQ38TO6.html',
     'The same map; the Newberry copy is uncut and its rights are "No copyright - United States".', 'Listings read.', 'Public domain.', 'located', 'P2', 'A copy not cut into sections would fit better than the Library of Congress copy.'),
]

LAYERS = [
    ('rivers', 1, 'Rivers, as Mouzon draws them (1775), fitted to today\'s courses', 'stream', 'traced', 'medium',
     'Picked by hand every 50-100 pixels of a half-resolution crop and snapped by program to the engraved line; fitted to the ground by matching them to today\'s rivers (Natural Earth). Rivers with no line in Natural Earth (Pacolet, Tyger, Enoree, Black, Ashley, Combahee) follow the fit and are low.'),
    ('coast', 2, 'The sea coast, as Mouzon draws it, and the sea', 'shore', 'traced', 'low',
     'The outer coast snapped to the engraved line and fitted to today\'s coast. Inlets, islands and the sounds behind them are not traced yet: the sea is closed across the harbour mouths.'),
    ('roads', 3, 'The main roads of 1775, as Mouzon draws them', 'road', 'traced', 'low',
     'Picked by hand along Mouzon\'s double lines every 100-150 pixels (about 9-14 km), not snapped. Good to a few kilometres between the fitted towns and crossings.'),
    ('boundaries', 4, 'The Cherokee boundary (to 20 May 1777) and the lines with North Carolina (1735-72)', 'boundary', 'traced', 'low',
     'Picked by hand; the North Carolina lines fitted to today\'s state line, which follows them.'),
]

# names read from Mouzon for the reconstruction: crop pixel (or [lon, lat]), kind, level
NAMES = [
    ('Augusta', (2314, 2268), 'town', 0), ('Savannah', (3095, 3918), 'town', 0), ('Purrysburg', (3053, 3644), 'town', 1), ('Catawba Town', (3120, 365), 'town', 1),
    ('NINETY SIX PRECINCT', (2450, 1300), 'area', 0), ('CAMDEN PRECINCT', (2950, 1000), 'area', 0), ('CHERAWS PRECINCT', (3950, 800), 'area', 0),
    ('GEORGETOWN PRECINCT', (4700, 1450), 'area', 0), ('ORANGEBURG PRECINCT', (2950, 2250), 'area', 0), ('CHARLESTOWN PRECINCT', (3650, 2800), 'area', 0),
    ('BEAUFORT PRECINCT', (3150, 3150), 'area', 0), ('CATAWBA NATION', (3060, 320), 'area', 1), ('NORTH CAROLINA', (3700, 150), 'area', 0), ('GEORGIA', (1700, 2850), 'area', 0),
    ('ATLANTIC OCEAN', [-78.95, 32.45], 'area', 0),
]
RIVER_NAMES = [('Santee River', 0), ('Savannah River', 0), ('Pee Dee River', 0), ('Congaree River', 0), ('Wateree River', 0), ('Broad River', 0), ('Saluda River', 0),
               ('Catawba River', 1), ('Edisto or Ponpon River', 1), ('Cooper River', 1), ('Ashley River', 1), ('Combahee River', 1), ('Black River', 1), ('Lynches Creek', 1),
               ('Little Pee Dee River', 1), ('Waccamaw River', 1), ('Enoree River', 1), ('Tyger River', 1), ('Pacolet River', 1), ('North Fork of Edisto', 1)]
TODAY_NAME = {'Edisto or Ponpon River': 'Edisto River', 'Lynches Creek': 'Lynches River', 'Pee Dee River': 'Great Pee Dee River', 'Santee River': 'Lake Marion in part', 'Saluda River': 'Lake Murray in part'}


def headers(ws): return [c.value for c in ws[1]]


def upsert(ws, keycols, row):
    h = headers(ws); key = tuple(row.get(k) for k in keycols)
    for r in ws.iter_rows(min_row=2):
        if tuple(r[h.index(k)].value for k in keycols) == key:
            for k, v in row.items(): r[h.index(k)].value = v
            return 'updated'
    ws.append([row.get(k) for k in h]); return 'added'


def river_label(name, level, feats):
    F = [f for f in feats if f['properties'].get('kind') == 'stream' and f['properties'].get('name') == name]
    if not F: return None
    c = max(F, key=lambda f: len(f['geometry']['coordinates']))['geometry']['coordinates']; i = len(c) // 2
    a, b = c[max(0, i - 3)], c[min(len(c) - 1, i + 3)]
    ang = math.degrees(math.atan2(-(b[1] - a[1]) * 110.9, (b[0] - a[0]) * 92.8))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    return {'playback_id': PB, 'text': name, 'other_name': TODAY_NAME.get(name), 'lat': c[i][1], 'lon': c[i][0], 'angle': round(ang), 'level': level, 'kind': 'water', 'show': 'recon', 'approximate': None}


def main():
    wb = openpyxl.load_workbook(SHARED)
    for s in SOURCES: print('Sources', s['source_id'], upsert(wb['Sources'], ['source_id'], s))
    hc = headers(wb['Source candidates'])
    for c in CANDIDATES:
        row = dict(zip(['candidate_id', 'title', 'holder', 'url', 'what it holds', 'access', 'rights', 'status', 'priority', 'notes'], [c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9]]))
        row.update(war='ARW', battles='SC-ORI', added=TODAY); print('Candidate', c[0], upsert(wb['Source candidates'], ['candidate_id'], row))
    wb.save(SHARED)

    G = json.load(open(RC.OUT)); feats = G['features']
    wb = openpyxl.load_workbook(WAR)
    rec = {'playback_id': PB, 'recon_id': RID, 'title': 'South Carolina, 1775 to 1781: a WarMapper reconstruction', 'label': '1775 (reconstructed)',
           'about': 'This is a WarMapper reconstruction, not a period map. Its lines are those of Henry Mouzon\'s map of the two Carolinas (1775), laid on today\'s ground: '
                    'the rivers and the sea coast fitted to today\'s courses, which they keep, and the main roads and boundary lines carried with them. '
                    'Mouzon\'s map was made for the colonies\' trade and land grants, not as a survey: his roads are good to a few kilometres, his up-country less. '
                    'A first pilot: only the main lines are traced. Nothing here has been checked by a historian.',
           'file': 'data/recon/sc-1775.geojson', 'style': 'period-1899', 'made': TODAY, 'review_status': 'Needs review',
           'notes': 'Rivers and coast good to about 1-2 km where today\'s river is in Natural Earth; roads and boundaries to 3-5 km; the far north-west (the Cherokee country) to no better than 10 km. '
                    'Not yet traced: inlets, islands and sounds, swamps, the lesser roads, ferries and fords, and the towns, which the orientation\'s places mark.',
           'credit': 'WarMapper reconstruction from Mouzon, 1775 (Library of Congress), fitted with Natural Earth'}
    print('Reconstructions', upsert(wb['Reconstructions'], ['recon_id'], rec))
    for lid, order, title, kind, method, conf, how in LAYERS:
        print('Recon layers', lid, upsert(wb['Recon layers'], ['recon_id', 'layer_id'], {'recon_id': RID, 'layer_id': lid, 'order': order, 'title': title, 'kind': kind, 'source_id': 'S135',
              'link': MOUZON_ITEM, 'link_label': 'Mouzon 1775 (Library of Congress)', 'method': method, 'confidence': conf, 'from': '1775-01-01', 'to': '1781-12-31', 'how_read': how,
              'review_status': 'Needs review', 'notes': None}))
    ws = wb['Labels']
    for nm, at, kind, lvl in NAMES:
        ll = at if isinstance(at, list) else RC.ground([at])[0]
        upsert(ws, ['playback_id', 'text', 'show'], {'playback_id': PB, 'text': nm, 'other_name': None, 'lat': round(ll[1], 5), 'lon': round(ll[0], 5), 'angle': None, 'level': lvl, 'kind': kind, 'show': 'recon',
               'approximate': 'yes' if kind == 'town' else None})
    for nm, lvl in RIVER_NAMES:
        r = river_label(nm, lvl, feats)
        if r: upsert(ws, ['playback_id', 'text', 'show'], r)
    m = {'playback_id': PB, 'map_id': 'mouzon-1775-fitted', 'title': 'Mouzon, An accurate map of North and South Carolina (1775), South Carolina, fitted to the ground', 'short': 'Mouzon 1775',
         'label': 'Mouzon 1775, fitted', 'credit': 'Mouzon, 1775 · Library of Congress', 'source_id': 'S135', 'fitted_to_ground': 'yes', 'file': 'mouzon-1775-fitted.webp',
         'tl_lat': 35.3, 'tl_lon': -83.45, 'tr_lat': 35.3, 'tr_lon': -78.45, 'br_lat': 31.95, 'br_lon': -78.45, 'bl_lat': 31.95, 'bl_lon': -83.45,
         'fit': json.dumps({'method': 'thin-plate spline with a plane for each section of the cloth-mounted copy, from 14 point controls and the rivers, coast and North Carolina line matched to Natural Earth (pipeline/georef/sc_mouzon_fit.py); the picture is the scan resampled onto the ground (Web Mercator)',
                            'controls': 14, 'loo_km': {'median': 1.1, 'max_inland': 4.4, 'north_west': 26.4}}),
         'note': 'Resampled from a half-resolution crop of the Library of Congress scan. The white bands are the gaps between the sections of the cloth-mounted copy; at the edges of the sections, and in the north-west and north-east corners, the picture is stretched.'}
    print('Maps', upsert(wb['Maps'], ['playback_id', 'map_id'], m))
    ws = wb['Playback settings']; h = headers(ws)
    # the bases: the reconstruction with terrain first (SR-02, SR-15), the modern map, Mouzon's map in the map details
    drop = [r for r in ws.iter_rows(min_row=2) if r[h.index('playback_id')].value == PB and str(r[h.index('setting')].value or '').startswith('bases.')]
    for r in drop[::-1]: ws.delete_rows(r[0].row)
    terrain = {'zoom': 9, 'extent': [-84.9, 30.9, -77.0, 36.2], 'open_m': 300, 'smooth_m': 400, 'relief': 6, 'spots_from': 9.6, 'doubt': False,
               'steps': [[0, 100, 500], [8.6, 50, 250], [10.2, 20, 100], [11.6, 10, 50]],
               'about': 'In the United States these tiles come from the USGS\'s National Elevation Dataset, a survey of the bare ground with no buildings or trees in it. Over a whole state they are read at about 250 m a pixel, '
                        'so bumps narrower than about 300 m are taken off and the rest smoothed over about 400 m. This is today\'s ground. The big lakes (Marion, Moultrie, Murray, Wateree, Hartwell, Thurmond, Keowee and others) are '
                        'reservoirs of the 20th century: their flat floors are today\'s water, and in 1775 the rivers ran in their valleys.',
               'beyond': 'Beyond the dotted line Mouzon\'s South Carolina stops: only today\'s relief and sea are drawn there, so the map fills the window.'}
    rows = [('bases.1.id', 'r75t'), ('bases.1.label', '1775 with terrain'), ('bases.1.short', '1775'), ('bases.1.recon', RID), ('bases.1.terrain', json.dumps(terrain)),
            ('bases.2.use', 'current'), ('bases.2.id', 'mod'),
            ('bases.3.id', 'mz75'), ('bases.3.label', 'Mouzon 1775, fitted'), ('bases.3.short', 'Mouzon'), ('bases.3.map', 'mouzon-1775-fitted'), ('bases.3.backdrop', 'current'), ('bases.3.hidden', True),
            ('bases.3.note', 'Henry Mouzon\'s map of the two Carolinas (1775), which the reconstruction is traced from, resampled onto the ground. Good to a few kilometres; stretched at the edges of the sections it was mounted in.')]
    for k, v in rows: ws.append([{'playback_id': PB, 'setting': k, 'value': v}.get(c) for c in h])
    # the Georeference sheet: a block saying how Mouzon was fitted
    ws = wb['Georeference']
    if not any(str(c.value or '').startswith('Georeference: South Carolina, Mouzon 1775') for c in ws['A']):
        ws.append([]); ws.append(['Georeference: South Carolina, Mouzon 1775'])
        ws.append(['How Mouzon\'s map of 1775 (S135) was laid on the ground for the South Carolina reconstruction (pipeline/georef/sc_mouzon_fit.py, sc_mouzon_fit.json)'])
        ws.append(['The Library of Congress copy is cut into sections and mounted on cloth. Each section (above and below the gap at crop y 1222, left and right of the seam at crop x 4232) is fitted by a thin-plate spline with a plane, from the point controls below and from '
                   'Mouzon\'s rivers, coast and North Carolina line matched seven times over to the same lines in Natural Earth (S136). Pixels are of the half-resolution crop: full scan x = 2 x, y = 3600 + 2 y. Misfit is the distance at which a control is found when it is left out of the fit.'])
        ws.append([]); ws.append(['Control point', 'pixel x', 'pixel y', 'lat', 'lon', 'misfit left out (m)', 'source'])
        loo = {'Ninety Six': 4400, 'Fort Charlotte': 270, "Monck's Corner": 3430, 'Fort Johnson': 4180, 'Esseneca (Sennekaw)': 26410, 'Broad and Saluda meet (the Congaree)': 18220,
               'Wateree and Congaree meet (the Santee)': 1410, 'Lynches Creek meets the Pee Dee': 360, 'Little Pee Dee meets the Pee Dee': 200, 'Edisto forks': 1120, 'Pee Dee at Winyah Bay': 410,
               'Savannah River mouth': 920, 'NC line at the sea, Little River': 570, 'Santee mouth': 60}
        for pc in RC.FIT['PC']:
            ws.append([pc['name'], pc['m'][0], pc['m'][1], pc['lonlat'][1], pc['lonlat'][0], loo.get(pc['name']), pc['source']])
    wb.save(WAR); print('saved')


if __name__ == '__main__':
    main()
