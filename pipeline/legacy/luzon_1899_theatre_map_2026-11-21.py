"""21 Nov 2026 (Morgan: "you can put the reduced copy in the public repo"): a third period map for the Luzon 1899 playback, the War
Department's Theatre of military operations in Luzon, 1899 (second edition), from the University of Minnesota's scan: the north
sheet, and (Morgan the same day: "yes", fit the south sheet too) the upper part of the south sheet, so the map reaches Manila.

Adds Sources S77, two Maps rows (fitted by pipeline/georef/luzon_georef.py, 'theatre' and 'theatre_s'), a fourth base map in the settings,
and gap G-LZ7. Run once, after luzon_1899_campaign_2026-11-21.py; it refuses to run twice.

How the picture got here: the holder's image service answers a person's browser but puts a browser check in front of this
workspace, so each sheet was viewed in Morgan's browser in pieces at one-fifth size and the pieces joined
(playbacks/luzon1899/theatre-1899-north.webp, 2400 x 1872, and theatre-1899-south.webp, 2400 x 1166; a strip of glare is cut from
the foot of the one and the head of the other). Zoomed in, the playback fetches the north sheet's full scan from the holder; the
player takes one such service a map, so the south sheet stays at the reduced copy.
"""
import copy, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'pipeline', 'georef'))
import luzon_georef as LG
import openpyxl

WB = os.path.join(ROOT, 'data', 'WarMapper battle data.xlsx'); wb = openpyxl.load_workbook(WB)
assert any(r[0].value == 'luzon1899' for r in wb['Playbacks'].iter_rows(min_row=2)), 'run luzon_1899_campaign first'
assert not any(r[0].value == 'S77' for r in wb['Sources'].iter_rows(min_row=2)), 'already applied'


def head(ws): return [c.value for c in ws[1]]


def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r


def add(sheet, values):
    ws = wb[sheet]; h = head(ws); src = last_row(ws); r = src + 1
    for k in values: assert k in h, '%s has no column %r' % (sheet, k)
    for j in range(1, len(h) + 1):
        s = ws.cell(src, j)
        if s.has_style: ws.cell(r, j)._style = copy.copy(s._style)
    for k, v in values.items(): ws.cell(r, h.index(k) + 1).value = v
    return r


f = LG.Fit('theatre'); c = f.corners(); s = f.summary(); g = LG.Fit('theatre_s'); c2 = g.corners(); s2 = g.summary()
add('Sources', {'source_id': 'S77', 'title': 'Theatre of military operations in Luzon, 1899 (second edition), in two sheets', 'author': "War Department, Adjutant General's Office, Military Information Division", 'date': '1899',
                'type': 'Period map (official, compiled in Washington)', 'citation': 'Washington, 1899. Scale about 1:212,000. University of Minnesota Libraries, John R. Borchert Map Library, G8062.L8S1 1899 .U5 (UMN_ALMA 9931048490001701); Minnesota Digital Library p16022coll230:4183. Sheet 1 (south) is image 4181, sheet 2 (north) image 4182.',
                'page verified?': 'yes (record and both sheets viewed 21 Nov 2026)', 'url': 'https://geo.btaa.org/catalog/p16022coll230:4183',
                'rights': 'Holder\'s statement: "Use of this item may be governed by US and international copyright laws. You may be able to use this item, but copyright and other considerations may apply." The map is a US War Department publication of 1899.',
                'notes': 'PW-M05 in the candidate list (the Hawaii copy, PW-M04, is still unread). USED from 21 Nov 2026 as a period map of the Luzon 1899 playback: the north sheet fitted on %d towns, RMS %d m, worst %d m; the upper part of the south sheet (Manila Bay to Lake Taal) on %d churches, RMS %d m, worst %d m (pipeline/georef/luzon_georef.py). Morgan approved reduced copies in the public repository on 21 Nov 2026.' % (s['points'], s['rms_m'], s['max_m'], s2['points'], s2['rms_m'], s2['max_m']),
                'used_for': 'PHW-LUZ99', 'kind': 'map', 'rights_status': 'holder gives no clear statement; US government work of 1899', 'may_host': 'yes (reduced copy; Morgan, 21 Nov 2026)', 'rights_checked': 'yes', 'site': 'geo.btaa.org; cdm16022.contentdm.oclc.org', 'war': 'PHW'})
add('Maps', {'playback_id': 'luzon1899', 'map_id': 'theatre-1899', 'title': 'War Department, Theatre of military operations in Luzon, 1899 (second edition)', 'short': '1899 theatre map', 'label': 'Luzon theatre, 1899 (War Dept)',
             'credit': 'War Department, Military Information Division, 1899 · University of Minnesota Libraries, Borchert Map Library', 'source_id': 'S77', 'fitted_to_ground': 'yes', 'file': 'theatre-1899-north.webp',
             'tl_lat': round(c[0][0], 6), 'tl_lon': round(c[0][1], 6), 'tr_lat': round(c[1][0], 6), 'tr_lon': round(c[1][1], 6), 'br_lat': round(c[2][0], 6), 'br_lon': round(c[2][1], 6), 'bl_lat': round(c[3][0], 6), 'bl_lon': round(c[3][1], 6),
             'fit': json.dumps({'method': 'affine (shift, turn, scale, shear) by least squares on town symbols matched to churches and town centres, Lingayen to Malolos, solved together with the south sheet and five ties along the join; the east coast was left out', 'points': s['points'],
                                'rms_m': s['rms_m'], 'max_m': s['max_m'], 'm_per_px': s['m_per_px'], 'script': 'pipeline/georef/luzon_georef.py'}),
             'scale_note': 'Scale about 1:212,000 on the sheet; the scan is about 18 m per pixel.', 'approx_m_per_px': s['m_per_px'],
             'note': 'The War Department\'s printed map of the theatre, compiled in Washington in 1899 from older Spanish mapping, on two sheets: Lingayen Gulf to Malolos, and Manila Bay to Lake Taal. It is the clearest of the three period maps and not the truest: fitted on 32 towns, places on the north sheet fall about 1.7 km from where they are (3.5 km at worst), and the Pacific coast is some 5 km out; the south sheet is within about half a kilometre at Manila and 1.4 km around Laguna de Bay (3.8 km at worst), and Cavite is 3 to 5 km out. The two sheets are fitted together so that they meet. Units are drawn at the true places. Zoomed in, the north sheet sharpens; the south sheet does not.',
             'iiif_service': 'https://cdm16022.contentdm.oclc.org/iiif/2/p16022coll230:4182', 'iiif_tile': 1024, 'iiif_scale_factors': '[1, 2, 4, 8, 16]',
             'iiif_width': 11998, 'iiif_height': 9451, 'iiif_region': '0, 0, %d, %d' % (f.W, f.H), 'iiif_reduced': round(2400 / f.W, 5)})
add('Maps', {'playback_id': 'luzon1899', 'map_id': 'theatre-1899', 'file': 'theatre-1899-south.webp', 'source_id': 'S77',
             'tl_lat': round(c2[0][0], 6), 'tl_lon': round(c2[0][1], 6), 'tr_lat': round(c2[1][0], 6), 'tr_lon': round(c2[1][1], 6), 'br_lat': round(c2[2][0], 6), 'br_lon': round(c2[2][1], 6), 'bl_lat': round(c2[3][0], 6), 'bl_lon': round(c2[3][1], 6),
             'fit': json.dumps({'method': 'affine by least squares on town symbols matched to churches around Manila and Laguna de Bay, solved together with the north sheet and five ties along the join; Cavite left out', 'points': s2['points'], 'rms_m': s2['rms_m'], 'max_m': s2['max_m'],
                                'm_per_px': s2['m_per_px'], 'script': 'pipeline/georef/luzon_georef.py'}),
             'note': 'The south sheet, upper part (rows 141 to 6000 of the scan p16022coll230:4181). A second picture of the same map.', 'iiif_reduced': round(2400 / g.W, 5)})
for k, v, w in [('bases.4.id', 'wd99', 'A third period map, added 21 Nov 2026'), ('bases.4.label', 'Luzon theatre, 1899 (War Dept)', None), ('bases.4.short', 'Theatre', None), ('bases.4.map', 'theatre-1899', None), ('bases.4.backdrop', 'current', None)]:
    add('Playback settings', {'playback_id': 'luzon1899', 'setting': k, 'value': v, 'what it does': w})
PS = wb['Playback settings']; h = head(PS); hit = 0
for r in PS.iter_rows(min_row=2):
    if r[0].value == 'luzon1899' and r[h.index('setting')].value == 'about.6':
        r[h.index('value')].value = ('The three period maps are the Army\'s and the War Department\'s own. They were compiled from reconnaissance and older Spanish maps, not surveyed, so towns on them can be one to five '
                                     'kilometres from where they are; units are drawn at the true places.'); hit += 1
assert hit == 1
add('Gaps', {'gap_id': 'G-LZ7', 'battle_id': 'PHW-FALL99', 'gap': 'The theatre map (S77) is fitted for the campaign country only, with one straight fit a sheet',
             'effect on the data': 'East of about 121.1 E the map is several kilometres out (Baler 4.8 km), and Cavite 3 to 5 km. The two sheets meet to within about 0.6 km on the railway north of Manila and 1 to 2 km at the edges. The south sheet has no full-resolution zoom and stops at Lake Taal.',
             'how to close it': 'Warp both sheets to the control points as one picture (as Trenton\'s Faden map is), and let a map name more than one image service.', 'status in v2': 'Open (21 Nov 2026).'})
wb.save(WB); print('theatre map added:', s)
