"""Data pilot v7: as v6, with the Allied lines at First Ypres read from the dated sketches of the British official history.
usage: python3 pipeline/build_workbook.py <Gettysburg v2 workbook> <output workbook>"""
import sys, os, math, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
import trenton_data as TR
import ypres_data as YP

V2, OUT = sys.argv[1:3]
v2 = openpyxl.load_workbook(V2, data_only=False)
v2v = openpyxl.load_workbook(V2, data_only=True)

F = 'Arial'
HF = Font(name=F, bold=True, color='FFFFFF', size=10); HFILL = PatternFill('solid', fgColor='1F2A44')
BF = Font(name=F, size=10); thin = Side(style='thin', color='BFBFBF'); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical='top')
FILL = {'low': 'FBE3E0', 'medium': 'FFF2CC', 'high': 'E2F0D9'}
BLUE = PatternFill('solid', fgColor='DDEBF7'); KEY = PatternFill('solid', fgColor='EDEDED')


def sheet(wb, title, headers, rows, widths, freeze=None, keycols=0):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for r in rows: ws.append(list(r) + [''] * (len(headers) - len(r)))
    for c in range(1, len(headers) + 1):
        h = ws.cell(1, c); h.font = HF; h.fill = HFILL; h.alignment = Alignment(wrap_text=True, vertical='center'); h.border = BORDER
        ws.column_dimensions[L(c)].width = widths[c - 1]
    for row in ws.iter_rows(min_row=2, max_row=max(ws.max_row, 2), max_col=len(headers)):
        for cell in row:
            cell.font = BF; cell.alignment = WRAP; cell.border = BORDER
            if cell.column <= keycols: cell.fill = KEY
    ws.freeze_panes = freeze or 'B2'
    ws.auto_filter.ref = f"A1:{L(len(headers))}{max(ws.max_row, 2)}"
    ws.row_dimensions[1].height = 32
    return ws


def table(wbk, name):
    ws = wbk[name]; rows = list(ws.iter_rows(values_only=True)); h = list(rows[0])
    return [dict(zip(h, [('' if v is None else v) for v in r])) for r in rows[1:] if r[0] not in (None, '')]


def sidc(frame, echelon, branch):
    ech = {'Army': '23', 'Corps': '22', 'Headquarters': '00', 'Division': '21', 'Brigade': '18', 'Regiment': '17', 'Regiment (part)': '17', 'Battalion': '16',
           'Battery': '15', 'Company': '15', 'Section': '13', 'Detachment': '14'}.get(echelon, '00')
    ent = {'Infantry': '121100', 'Cavalry': '121300', 'Artillery': '130300', 'Horse artillery': '130300'}.get(branch, '121100')
    return '100' + ('3' if frame == 'blue' else '6') + '10' + '0' + '0' + ech + ent + '0000'

# ============ reference tables ============
WARS = [('ACW', 'American Civil War', 1861, 1865, 'Q8676', 'civil_war', 'Pilot: Gettysburg, first day, morning.'),
        ('ARW', 'American Revolutionary War', 1775, 1783, 'Q40949', 'revolution', 'Pilot: Trenton. Wikidata ID is the one the War Atlas dataset carries for "American Revolution"; confirm it is the war and not the wider revolution.')]
WARS.append(('WW1', 'First World War', 1914, 1918, 'Q361', 'wwi', 'Pilot: First Ypres. The War Atlas dataset has Second and Third Ypres but not the First.'))
CAMPAIGNS = [('ACW-GETT', 'ACW', 'Gettysburg campaign', '1863-06-03', '1863-07-24', 'Q1377639', 'Start date and Wikidata ID from the War Atlas dataset (S35). End date is the usual one; not checked here.'),
             ('ARW-TP', 'ARW', 'Trenton and Princeton (the "Ten Crucial Days")', '1776-12-25', '1777-01-03', '', 'Wikidata ID not looked up.')]
CAMPAIGNS.append(('WW1-FL14', 'WW1', 'Flanders, October to November 1914 (the end of the "Race to the Sea")', '1914-10-10', '1914-11-30', '', 'Covers the linked battles of La Bassee, Armentieres, Messines, Ypres and the Yser. Dates are the outer limits the sources give. Wikidata ID not looked up.'))
BATTLES = [
 # id, campaign, parent, name, start_e, start_l, end_e, end_l, lat, lon, precision, coord source, wikidata, cdb90, war atlas, notes
 ('GETT', 'ACW-GETT', '', 'Battle of Gettysburg', '1863-07-01 07:30', '1863-07-01 10:00', '1863-07-03 15:00', '1863-07-03 15:00', 39.81139, -77.22583, 'battle', 'Wikidata, via CDB90 (S34)', 'Q33132', 199, 'gettysburg_b',
  'CDB90 times the battle 1 July 10:00 to 3 July 15:00 and gives frontages of 5.1 km (attacker) and 4.1 km (defender) on 1 July at 14:30. The first shot was at 07:30 (P02).'),
 ('GETT-D1', 'ACW-GETT', 'GETT', 'Gettysburg, first day', '1863-07-01 07:30', '1863-07-01 10:00', '1863-07-01 17:00', '1863-07-01 17:00', 39.8380, -77.2500, 'area', 'Pilot: McPherson Ridge', 'Q33132', 199, '', 'CDB90 active period 1: 10:00 to 17:00.'),
 ('GETT-D1-AM', 'ACW-GETT', 'GETT-D1', "Buford against Heth on the Chambersburg Pike", '1863-07-01 07:30', '1863-07-01 07:30', '1863-07-01 10:15', '1863-07-01 10:15', 39.8400, -77.2580, 'area', 'Pilot: between Herr Ridge and McPherson Ridge', '', '', '', 'The first pilot window. Not a battle with its own record anywhere else.'),
 ('TREN', 'ARW-TP', '', 'Battle of Trenton', '1776-12-26 07:30', '1776-12-26 08:00', '1776-12-26 09:30', '1776-12-26 10:30', 40.22583, -74.76472, 'battle', 'Wikidata, via CDB90 (S34)', 'Q653664', 85, 'trenton_b',
  'CDB90: 08:00 to 09:30; attacker frontage 1.3 km, defender 0.2 km; strengths 2,420 and 1,520. The CDB90 point is the Battle Monument. War Atlas places it at the town (40.2171, -74.7429).'),
]
BATTLES += [
 ('YPRES1', 'WW1-FL14', '', 'First Battle of Ypres', '1914-10-19', '1914-10-19', '1914-11-17', '1914-11-22', 50.8519, 2.8911, 'battle', 'Wikipedia article coordinates (S44)', 'Q853976', '', '',
  'British official dates 19 October to 22 November. The German account closes on 17 November; the French and German official histories use other dates again (YC01). Not in CDB90 or the War Atlas dataset.'),
 ('YP-LANG', 'WW1-FL14', 'YPRES1', 'Battle of Langemarck', '1914-10-21', '1914-10-22', '1914-10-24', '1914-10-24', 50.9135, 2.9184, 'area', 'OpenStreetMap: Langemark (S39)', '', '', '', 'British official name and dates (21 to 24 October). Edmonds starts his chapter on the 22nd.'),
 ('YP-GHEL', 'WW1-FL14', 'YPRES1', 'Battle of Gheluvelt', '1914-10-29', '1914-10-29', '1914-10-31', '1914-11-05', 50.8345, 2.9944, 'area', 'OpenStreetMap: Geluveld (S39)', '', '', '', 'Usually 29 to 31 October; Edmonds carries the name to 5 November (YC08).'),
 ('YP-NONNE', 'WW1-FL14', 'YPRES1', 'Battle of Nonne Bosschen', '1914-11-11', '1914-11-11', '1914-11-11', '1914-11-11', 50.8497, 2.9699, 'area', 'OpenStreetMap: centre of Nonnebossen (S39)', '', '', '', 'One day. Rows for the days after it that follow from the attack are filed here too.'),
 ('MESS14', 'WW1-FL14', '', 'Battle of Messines (1914)', '1914-10-12', '1914-10-12', '1914-11-02', '1914-11-02', 50.7654, 2.8984, 'area', 'OpenStreetMap: Mesen (S39)', '', '', '', 'A separate battle in the British list, fought at the same time on the right of Ypres (S45).'),
 ('YSER', 'WW1-FL14', '', 'Battle of the Yser', '1914-10-16', '1914-10-18', '1914-10-31', '1914-11-30', 51.0734, 2.7943, 'area', 'OpenStreetMap: Pervijze (S39)', '', '', '', 'Belgian and French battle on the left of Ypres. Dates as given in S44; the German official history runs it to 30 November.'),
]
EXTENT = {'GETT': 20, 'GETT-D1': 20, 'GETT-D1-AM': 20, 'TREN': 20, 'YPRES1': 45, 'YP-LANG': 15, 'YP-GHEL': 15, 'YP-NONNE': 10, 'MESS14': 20, 'YSER': 30}
BATTLES = [tuple(b) + (EXTENT[b[0]],) for b in BATTLES]
OPERATIONAL = {'WW1-FL14'}   # campaigns recorded by day at division level
PHASES = [
 ('PH-G1', 'GETT', 'Day 1 fighting (CDB90 active period 1)', '1863-07-01 10:00', '1863-07-01 17:00', 'S34', ''),
 ('PH-G2', 'GETT', 'Day 2 fighting (CDB90 active period 2)', '1863-07-02 16:00', '1863-07-02 20:30', 'S34', ''),
 ('PH-G3', 'GETT', 'Day 3 fighting (CDB90 active period 3)', '1863-07-03 05:00', '1863-07-03 10:30', 'S34', 'CDB90 ends the period at 10:30 but the battle at 15:00.'),
 ('PH-G4', 'GETT-D1-AM', 'Cavalry delaying action', '1863-07-01 07:30', '1863-07-01 10:15', 'pilot', 'Starts earlier than CDB90 counts the battle as beginning.'),
 ('PH-T1', 'TREN', 'Crossing the Delaware', '1776-12-25 17:00', '1776-12-26 03:00', 'S20; S21', 'Before the battle; shown so the playback can start here.'),
 ('PH-T2', 'TREN', 'March to Trenton', '1776-12-26 04:00', '1776-12-26 07:45', 'S20; S21', ''),
 ('PH-T3', 'TREN', 'Outposts driven in', '1776-12-26 07:30', '1776-12-26 08:10', 'S20; S21', 'See TC01.'),
 ('PH-T4', 'TREN', 'Fight in the town (CDB90 active period)', '1776-12-26 08:00', '1776-12-26 09:30', 'S34', 'See TC04.'),
]
PHASES += [
 ('PH-Y1', 'YPRES1', 'Encounter battle', '1914-10-19', '1914-10-21', 'S40', 'Edmonds, chapter V.'),
 ('PH-Y2', 'YPRES1', 'Battle of Langemarck', '1914-10-22', '1914-10-24', 'S40', 'Edmonds, chapter VI.'),
 ('PH-Y3', 'YPRES1', 'Attempted renewal of the Allied offensive', '1914-10-25', '1914-10-28', 'S40', 'Edmonds, chapter IX (title only read).'),
 ('PH-Y4', 'YPRES1', 'Battle of Gheluvelt', '1914-10-29', '1914-11-05', 'S40', 'Edmonds, chapters X to XV (titles only read).'),
 ('PH-Y5', 'YPRES1', 'Renewal of the German offensive (Zwarteleen, St. Eloi, Dixmude)', '1914-11-06', '1914-11-10', 'S40', 'Edmonds, chapter XVI (title only read).'),
 ('PH-Y6', 'YPRES1', 'Battle of Nonne Bosschen', '1914-11-11', '1914-11-11', 'S40', 'Edmonds, chapter XVII (title only read).'),
 ('PH-Y7', 'YPRES1', 'Close of the battles of Ypres', '1914-11-12', '1914-11-22', 'S40', 'Edmonds, chapter XVIII (title only read).'),
]
SIDES = [('ACW-US', 'ACW', 'United States (Union)', 'blue', '124F93', 'Frame colour is a drawing convention, not a judgement.'),
         ('ACW-CS', 'ACW', 'Confederate States', 'red', 'B02A1C', ''),
         ('ARW-US', 'ARW', 'United States (Continental Army and militia)', 'blue', '124F93', ''),
         ('ARW-CR', 'ARW', 'British Crown forces (British and German troops)', 'red', 'B02A1C', 'One side, several nations: the nation is on each unit.')]
SIDES += [('WW1-ALL', 'WW1', 'Allies (British, French and Belgian)', 'blue', '124F93', 'One side, three nations: the nation is on each unit.'),
          ('WW1-GER', 'WW1', 'Germany', 'red', 'B02A1C', '')]
FRAME = {s[0]: s[3] for s in SIDES}

# ============ Gettysburg migration ============
gu = table(v2v, 'Units'); gp = table(v2v, 'Positions'); gc = table(v2v, 'Conflicts'); gg = table(v2v, 'Gaps'); gs = table(v2v, 'Sources')
units, assigns = [], []
for u in gu:
    side = 'ACW-US' if u['side'] == 'Union' else 'ACW-CS'
    units.append([u['unit_id'], u['unit_name'], u['map_label'], side, 'United States' if side == 'ACW-US' else 'Confederate States', u['branch'], u['echelon'],
                  sidc(FRAME[side], u['echelon'], u['branch']), '', u['source_ids'], u['sourced?'], u['notes']])
    assigns.append([u['unit_id'], u['parent_unit_id'], u['commander'], u['strength / equipment'], '1863-07-01', '1863-07-01', u['source_ids'], ''])
for u in TR.UNITS:
    uid, name, label, side, nation, branch, ech, parent, cmd, strength, srcs, notes = u
    units.append([uid, name, label, side, nation, branch, ech, sidc(FRAME[side], ech, branch), '', srcs, 'yes' if srcs else 'no', notes])
    assigns.append([uid, parent, cmd, strength, '1776-12-25', '1776-12-26', srcs, ''])
for u in YP.U:
    uid, name, label, side, nation, branch, ech, srcs, notes = u
    units.append([uid, name, label, side, nation, branch, ech, sidc(FRAME[side], ech, branch), '', srcs, 'yes' if srcs else 'no', notes])
for a in YP.A: assigns.append(list(a))
for i, a in enumerate(assigns): a.insert(0, f'A{i+1:03d}')
UNIT = {u[0]: u for u in units}

TS = 'time_start (1 Jul 1863)'
def gtime(s, end=False):
    s = str(s or '').strip()
    if len(s) == 5 and s[2] == ':': return f'1863-07-01 {s}'
    if s.startswith('Jun 30'): return '1863-06-30'
    if s.startswith('Jun 29'): return '1863-06-29'
    if s.startswith('after'): return '1863-07-01 10:15'
    return 'unknown'
def csource(basis):
    b = str(basis)
    if b.startswith('Read from the Bachelder'): return 'map_read', 40
    if b.startswith('Marker or tablet'): return 'marker', 20
    if 'memorial site' in b: return 'marker', 50
    if b.startswith('Derived'): return 'derived', 200
    if b.startswith('No coordinates'): return 'none', ''
    return 'estimate', 300

RANGE = {'P17', 'P20', 'P21', 'P22', 'P23', 'P32', 'P33', 'P34', 'P35', 'P36'}
NOBATTLE = {'P01', 'P09', 'P13', 'P19', 'P25'}
pos = []
for r in gp:
    pid = r['pos_id']; se = sl = gtime(r[TS]); ee = el = gtime(r['time_end']); ch3 = ''
    if pid in RANGE: se, sl = '1863-07-01 09:00', '1863-07-01 09:30'; ch3 = 'Start is now a range: 9:00 (the map) to 9:30 (the reports). See C03.'
    if pid == 'P16': se, sl, ee, el = 'unknown', '1863-07-01 09:00', '1863-07-01 09:00', '1863-07-01 09:30'; ch3 = 'Times are now ranges: the halt ended between 9:00 (the map) and 9:30 (the reports). See C03.'
    if pid == 'P38': sl = 'unknown'; ee = el = 'unknown'; ch3 = 'Start is now "10:15 or later"; end unknown.'
    has = r['lat'] != ''; line = r['line_end_lat'] != ''
    cs, cp = csource(r['coordinate_basis']) if has else ('none', '')
    pos.append(dict(pos_id=pid, campaign_id='ACW-GETT', battle_id='' if pid in NOBATTLE else ('GETT-D1' if pid == 'P38' else 'GETT-D1-AM'), unit_id=r['unit_id'],
                    se=se, sl=sl, ee=ee, el=el, time_basis=r['time_basis'], activity=r['activity'], place=r['place_description'],
                    geometry='line' if line else ('point' if has else 'none'), lat=r['lat'], lon=r['lon'], lat2=r['line_end_lat'], lon2=r['line_end_lon'], via='',
                    coord_source=cs, coord_precision=cp, cbasis=r['coordinate_basis'], cconf=r['coordinate_confidence'], source_ids=r['source_ids'], say=r['source_wording'],
                    method=r['position_method'], oc=r['overall_confidence'], notes=r['notes'], review=r['review_status'], rnotes=r['reviewer_notes'],
                    rev1=r['your_review_v1'], ch2=r['changed in v2'], ch3=ch3, ch4='', ch5='', place_ids='', ch6='', ch7=''))
P08VIA = '39.84354, -77.23251'
for p in pos:
    if p['pos_id'] == 'P08': p['via'] = P08VIA; p['ch3'] = 'The bend in the line moved from the notes into the new "via" column.'

def conf_of(prec, src):
    if src == 'none': return 'n/a'
    return 'high' if prec <= 30 else ('medium' if prec <= 100 else 'low')
for q in TR.P:
    g = q['geom']
    if g:
        a = g[0]; b = g[-1] if len(g) > 1 else None
        prec = max(x[3] for x in g); src = a[2] if (len(g) == 1 or a[2] == b[2]) else 'derived'
        if len(g) == 1: basis = a[4]
        elif b[4] == TR.SK: basis = a[4] + ' Both ends of the bar were read.'
        else: basis = 'A line between two points. lat/lon: ' + a[4] + '. line_end: ' + b[4] + '.'
        lat, lon = a[0], a[1]; lat2, lon2 = (b[0], b[1]) if b else ('', '')
    else:
        prec, src, basis, lat, lon, lat2, lon2 = '', 'none', 'No coordinates: ' + ('off the battle map' if 'Off the' in q['notes'] or 'off the' in q['notes'] else 'position not in the sources read'), '', '', '', ''
    pos.append(dict(pos_id=q['pos_id'], campaign_id='ARW-TP', battle_id=q['battle_id'], unit_id=q['unit_id'], se=q['se'], sl=q['sl'], ee=q['ee'], el=q['el'], time_basis=q['time_basis'],
                    activity=q['activity'], place=q['place'], geometry='line' if (g and len(g) > 1) else ('point' if g else 'none'), lat=lat, lon=lon, lat2=lat2, lon2=lon2, via='',
                    coord_source=src, coord_precision=prec, cbasis=basis, cconf=conf_of(prec, src) if g else 'n/a', source_ids=q['source_ids'], say=q['say'], method=q['method'], oc=q['oc'],
                    notes=q['notes'], review='Needs review', rnotes='', rev1='', ch2='', ch3='' if q['ch4'].startswith('New') else 'New in v3', ch4=q['ch4'], ch5='', place_ids='', ch6='', ch7=''))

RANK = {'modern_map': 0, 'map_read': 0, 'derived': 1, 'estimate': 2}
def conf_op(prec): return 'high' if prec <= 500 else ('medium' if prec <= 1000 else 'low')
for q in YP.P:
    ks = q['keys']; g = YP.geom(q)
    if g:
        src = max((x[4] for x in g), key=lambda v: RANK[v]); prec = max(x[5] for x in g)
        lat, lon = g[0][2], g[0][3]; lat2, lon2 = (g[-1][2], g[-1][3]) if len(g) > 1 else ('', '')
        via = '; '.join(f'{x[2]:.5f}, {x[3]:.5f}' for x in g[1:-1])
        nm = sum(1 for x in g if x[4] == 'modern_map'); nd = sum(1 for x in g if x[4] == 'derived'); ne_ = sum(1 for x in g if x[4] == 'estimate'); nr_ = sum(1 for x in g if x[4] == 'map_read')
        parts = ([f'{nm} from OpenStreetMap village centres (S39)'] if nm else []) + ([f'{nr_} read from the 1925 official-history map (S40, Sketch A)'] if nr_ else []) + ([f'{nd} offset from a village to keep the two sides apart'] if nd else []) + ([f'{ne_} placed from memory or a description'] if ne_ else [])
        basis = q.get('cbasis') or ('A line through ' if len(g) > 1 else 'A point: ') + (f'{len(g)} places: ' if len(g) > 1 else '') + '; '.join(parts) + '. Each place is on the Places sheet.'
        cconf = conf_op(prec)
    else:
        src, prec, lat, lon, lat2, lon2, via, basis, cconf = 'none', '', '', '', '', '', '', 'No coordinates: position not in the sources read', 'n/a'
    pos.append(dict(pos_id=q['pos_id'], campaign_id='WW1-FL14', battle_id=q['battle_id'], unit_id=q['unit_id'], se=q['se'], sl=q['sl'], ee=q['ee'], el=q['el'], time_basis=q['time_basis'],
                    activity=q['activity'], place=q['place'], geometry='line' if len(g) > 1 else ('point' if g else 'none'), lat=lat, lon=lon, lat2=lat2, lon2=lon2, via=via,
                    coord_source=src, coord_precision=prec, cbasis=basis, cconf=cconf, source_ids=q['source_ids'], say=q['say'], method=q['method'], oc=q['oc'],
                    notes=q['notes'], review='Needs review', rnotes='', rev1='', ch2='', ch3='', ch4='', ch5='New in v5', place_ids='; '.join(ks), ch6=('Places re-read from the 1925 map or moved with one: ' + ', '.join(YP.PL[k][0].split(' (')[0] for k in ks if k in YP.CH6)) if any(k in YP.CH6 for k in ks) and not q.get('pts') else '', ch7=YP.V7.get(q['pos_id'], '')))

# ============ routes, events ============
def wp(pts): return '; '.join(f'{a:.5f}, {b:.5f}' for a, b in pts)
routes = [['RG01', 'ACW-GETT', 'GETT-D1-AM', 'CS-ARCH', 'march', '1863-07-01 07:30', '1863-07-01 09:00', 'P14', 'P16', '39.85350, -77.28800; 39.85096, -77.28073; 39.84369, -77.26540', 'S14; S18',
           'Route follows the Chambersburg Pike, which is nearly straight here.', 'low', 'Waypoints: head of column at Marsh Creek (P14), the First Shot marker (P02), the pike at Marye\'s guns (P16).'],
          ['RG02', 'ACW-GETT', 'GETT-D1-AM', 'CS-ARCH', 'attack', '1863-07-01 10:00', '1863-07-01 10:15', 'P17', 'P18', '39.83877, -77.26257; 39.83500, -77.25700', 'S11; S18', 'Advance from the Herr Ridge line to Willoughby Run.', 'low', 'Start is the middle of the P17 line.'],
          ['RG03', 'ACW-GETT', 'GETT-D1', 'CS-DAV', 'attack', '1863-07-01 10:00', '1863-07-01 10:15', 'P20', 'P37', '39.84336, -77.25872; 39.84089, -77.25690; 39.84126, -77.24772', 'S12; S18', 'Advance from the Herr Ridge line across the run to the 10:15 line.', 'low', 'Middle of P20, the run (P24), middle of P37.']]
for r in TR.ROUTES:
    rid, camp, bat, unit, kind, st, en, fp, tp, keys, srcs, say, conf, notes = r
    routes.append([rid, camp, bat, unit, kind, st, en, fp, tp, wp(keys), srcs, say, conf, notes])
events = [['GE01', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 07:30', '1863-07-01 07:30', 'First shot', "A picket of the 8th Illinois Cavalry fires on the head of Archer's column on the Chambersburg Pike at Knoxlyn Road.", 'P02; P14', 'S14'],
          ['GE02', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 08:00', '1863-07-01 08:00', 'Buford forms', "Gamble and Devin form line of battle and Calef's guns go into battery on the pike.", 'P04; P06; P10; P11; P12', 'S01; S02; S03'],
          ['GE03', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 09:00', '1863-07-01 09:00', 'Guns open', "Marye's battery opens from Herr Ridge while Archer's brigade halts on the pike.", 'P15; P16', 'S04; S13'],
          ['GE04', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 09:00', '1863-07-01 09:30', 'Heth deploys', 'Archer forms south of the pike and Davis north of it.', 'P17; P20', 'S04; S05; S18'],
          ['GE05', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 10:00', '1863-07-01 10:00', 'Across the run', 'Both Confederate brigades cross Willoughby Run.', 'P18; P24', 'S11; S12'],
          ['GE06', 'ACW-GETT', 'GETT-D1-AM', '1863-07-01 10:15', '1863-07-01 10:15', 'Infantry arrives', "Davis is in line against Cutler's brigade of the First Corps, and the cavalry is relieved.", 'P37; P05', 'S18; S02']]
events += [list(e) for e in TR.EVENTS]
for e in YP.EVENTS:
    eid, d0, d1, name, summ, bat, srcs = e
    events.append([eid, 'WW1-FL14', bat, YP.D(d0), YP.D(d1), name, summ, '', srcs])

# ============ conflicts, gaps, sources ============
conflicts = []
for c in gc:
    v3 = 'Held in the data as a start range, 9:00 to 9:30, on P16, P17, P20 to P23 and P32 to P36.' if c['conflict_id'] == 'C03' else ''
    conflicts.append([c['conflict_id'], 'GETT-D1-AM', c['question'], c['what the sources say'], c['how the pilot handled it'], c['comment'], c['status'], c['v2 update: what the map adds'], v3])
for c in conflicts: c.append('')
for c in TR.CONFLICTS: conflicts.append([c[0], c[1], c[2], c[3], c[4], c[5], c[6], '', '' if c[7].startswith('New in v4') else 'New in v3', c[7]])
for c in conflicts: c.append('')
for c in conflicts: c.append('')
for c in YP.CONFLICTS: conflicts.append([c[0], c[1], c[2], c[3], c[4], c[5], c[6], '', '', '', 'New in v7' if c[0] in ('YC11', 'YC12') else 'New in v5', YP.C7.get(c[0], '')])
gaps = []
for g in gg:
    v3 = {'G11': 'The disagreement is now held as a time range in the data.'}.get(g['gap_id'], '')
    gaps.append([g['gap_id'], 'GETT-D1-AM', g['gap'], g['effect on the data'], g['how to close it'], g['status in v2'], v3])
gaps.append(['G16', 'both', 'No unit has a Wikidata ID', 'Units cannot yet be joined to outside datasets. Wars and battles can.', 'Look up each unit; most Civil War regiments and Hessian regiments have an entry.', '', 'New in v3'])
gaps.append(['G17', 'both', 'Assignments cover one date range per unit', 'The table can hold changes of parent, commander and strength over time, but the pilots only span a day or two each.', 'Fill in when a second battle for the same unit is added.', '', 'New in v3'])
for g in gaps: g.append('')
G4 = {'TG01': 'Rewritten: Wiederhold\'s sketch has been read.', 'TG02': 'Mostly closed by the current street map; the remainder is listed.', 'TG05': 'Rewritten: rows that rested on a modern summary now have a period source.',
      'TG07': 'Unchanged: the sketch gives no times.', 'TG08': 'Updated: the sketch has been read directly.', 'TG11': 'New in v4.'}
for g in TR.GAPS: gaps.append([g[0], g[1], g[2], g[3], g[4], '', '' if g[0] == 'TG11' else 'New in v3', G4.get(g[0], '')])
for g in gaps: g.append('')
G6 = {'YG01': 'Partly closed: the bound sketch maps (Sketches 4, 7 to 10, 12 to 14) are now in hand and are in the playback as a backdrop. They have not yet been used to correct the rows.',
      'YG04': 'Partly closed: Sketch A of the official history is georeferenced and is a base map in the playback. Ten places have been re-read from it. The unit lines still come from text, not from the dated sketches.',
      'YG06': 'Ten of these places (Terhand, Klein Zillebeke, Zwarteleen, Hooge, Garde Dieu, Poezelhoek, the Gheluvelt cross-roads, Herenthage chateau and wood, the woods north-east of Klein Zillebeke) are now read from Sketch A. Terhand had been 880 m out and Poezelhoek 670 m.',
      'YG13': 'Unchanged, but Sketch A shows the 1914 woods and can be traced.'}
for g in gaps: g.append('')
for g in gaps: g.append('')
for g in YP.GAPS: gaps.append([g[0], g[1], g[2], g[3], g[4], '', '', '', 'New in v7' if g[0] >= 'YG14' else 'New in v5', G6.get(g[0], ''), YP.G7.get(g[0], '')])
sources = []
for s in gs:
    sources.append([s['source_id'], s['title'], s['author'], s['date'], s['type'], s['citation'], s['page verified?'], s['url'], s['rights'], s['notes'], 'GETT'])
for s in TR.SOURCES: sources.append(list(s))
for s in YP.SOURCES: sources.append(list(s))
for s in sources:
    if s[0] == 'S40': s[9] = str(s[9]) + ' v6: the bound sketch maps were taken from the same scan as page images: Sketch A (the Ypres area, two pages, with about a kilometre lost in the binding) and Sketches 4, 6 to 16. ' + YP.SOURCE_V7
    if s[0] == 'S39': s[9] = (str(s[9]) + ' ' if s[9] else '') + 'v5: also the source of village coordinates and the base map for First Ypres (a second extract, 12 Nov 2026).'; s[10] = 'TREN; YPRES1'
SRC = {s[0] for s in sources}

# ============ automated checks ============
def ptime(s, end=False):
    s = str(s).strip()
    if s in ('', 'unknown'): return None
    try:
        if len(s) == 10:
            d = dt.datetime.strptime(s, '%Y-%m-%d'); return d + dt.timedelta(hours=23, minutes=59) if end else d
        return dt.datetime.strptime(s, '%Y-%m-%d %H:%M')
    except ValueError:
        return 'bad'
def dist(a, b):
    p = math.radians((a[0] + b[0]) / 2)
    return math.hypot((a[1] - b[1]) * 111320 * math.cos(p), (a[0] - b[0]) * 111040)
def seg_dist(p, a, b):
    k = 111320 * math.cos(math.radians(p[0])); P_ = ((p[1]) * k, p[0] * 111040); A = (a[1] * k, a[0] * 111040); B = (b[1] * k, b[0] * 111040)
    vx, vy = B[0] - A[0], B[1] - A[1]; L2 = vx * vx + vy * vy
    f = 0 if L2 == 0 else max(0, min(1, ((P_[0] - A[0]) * vx + (P_[1] - A[1]) * vy) / L2))
    return math.hypot(P_[0] - (A[0] + f * vx), P_[1] - (A[1] + f * vy))
def pts(p):
    out = [(float(p['lat']), float(p['lon']))]
    for v in [x for x in str(p['via']).split(';') if x.strip()]:
        a_, b_ = v.split(','); out.append((float(a_), float(b_)))
    if p['lat2'] != '': out.append((float(p['lat2']), float(p['lon2'])))
    return out
def centre(p):
    q = pts(p); return (sum(x[0] for x in q) / len(q), sum(x[1] for x in q) / len(q))
def gap_between(a, b):
    q, r = pts(a), pts(b)
    if len(q) == 1 and len(r) == 1: return dist(q[0], r[0])
    best = 1e12
    for x in q:
        for i in range(len(r) - 1): best = min(best, seg_dist(x, r[i], r[i + 1]))
    for x in r:
        for i in range(len(q) - 1): best = min(best, seg_dist(x, q[i], q[i + 1]))
    return best
def crosses(a, b):
    def o(p1, p2, p3): return (p2[1] - p1[1]) * (p3[0] - p1[0]) - (p2[0] - p1[0]) * (p3[1] - p1[1])
    q, r = pts(a), pts(b)
    for i in range(len(q) - 1):
        for j in range(len(r) - 1):
            d1, d2, d3, d4 = o(r[j], r[j + 1], q[i]), o(r[j], r[j + 1], q[i + 1]), o(q[i], q[i + 1], r[j]), o(q[i], q[i + 1], r[j + 1])
            if d1 * d2 < 0 and d3 * d4 < 0: return True
    return False

checks = []
def flag(rule, sev, battle, rec, msg): checks.append([rule, sev, battle, rec, msg])
RULES = [
 ('K01', 'Every position names a unit that exists'), ('K02', 'Every unit has an assignment, and its parent exists'), ('K03', 'Times can be read and run in order'),
 ('K04', 'Every position cites at least one source that exists'), ('K05', 'Geometry, coordinates and coordinate source agree'), ('K06', 'Coordinates lie within the extent set for the battle (20 km for a one-day battle, 45 km for First Ypres)'),
 ('K07', 'A position stated by a source carries the source wording'), ('K08', 'A unit is not asked to move faster than it could'), ('K09', 'Opposing units are not within 150 m of each other unless a row says they are in contact'),
 ('K10', 'A regiment lies within 400 m of its brigade when both are placed'), ('K11', 'Review status is one of the four allowed values'), ('K12', 'Wars and battles carry a Wikidata ID'),
 ('K13', 'Routes and events point at positions and units that exist'),
 ('K14', 'Where positions are sector lines, the lines of opposing units do not cross'), ('K15', 'Every place a position names is on the Places sheet'),
]
BAT = {b[0]: b for b in BATTLES}; PARENT = {a[1]: a[2] for a in assigns}; POSID = {p['pos_id'] for p in pos}
for p in pos:
    b = p['battle_id'] or p['campaign_id']; pid = p['pos_id']
    if p['unit_id'] not in UNIT: flag('K01', 'error', b, pid, f"Unit {p['unit_id']} is not in the Units table.")
    T = [ptime(p['se']), ptime(p['sl']), ptime(p['ee'], True), ptime(p['el'], True)]
    if 'bad' in T: flag('K03', 'error', b, pid, 'A time is not in the form YYYY-MM-DD HH:MM, a date, or "unknown".')
    else:
        if T[0] and T[1] and T[0] > T[1]: flag('K03', 'error', b, pid, 'Earliest start is after latest start.')
        if T[2] and T[3] and T[2] > T[3]: flag('K03', 'error', b, pid, 'Earliest end is after latest end.')
        if T[0] and T[3] and T[0] > T[3]: flag('K03', 'error', b, pid, 'Starts after it ends.')
        if 'unknown' in (p['se'], p['sl'], p['ee'], p['el']): flag('K03', 'note', b, pid, 'One or more times are unknown.')
    ids = [x.strip() for x in str(p['source_ids']).split(';') if x.strip()]
    if not ids: flag('K04', 'error', b, pid, 'No source cited.')
    for i in ids:
        if i not in SRC: flag('K04', 'error', b, pid, f'Source {i} is not in the Sources table.')
    has = p['lat'] != ''
    if (p['geometry'] == 'none') == has or (p['geometry'] == 'line') != (p['lat2'] != '') or (p['coord_source'] == 'none') == has:
        flag('K05', 'error', b, pid, 'Geometry type, coordinates and coordinate source do not agree.')
    if has and p['battle_id']:
        bb = BAT[p['battle_id']]; d = dist(centre(p), (bb[8], bb[9]))
        if d > bb[16] * 1000: flag('K06', 'error', b, pid, f'{d/1000:.0f} km from the battle point; the limit for this battle is {bb[16]} km.')
    for k_ in [x.strip() for x in str(p['place_ids']).split(';') if x.strip()]:
        if k_ not in YP.PL: flag('K15', 'error', b, pid, f'Place {k_} is not on the Places sheet.')
    if p['method'] == 'stated' and not str(p['say']).strip(): flag('K07', 'review', b, pid, 'Marked "stated" but has no source wording.')
    if p['review'] not in ('Needs review', 'Accepted', 'Corrected', 'Rejected'): flag('K11', 'error', b, pid, f"Status '{p['review']}'.")
for u in units:
    if u[0] not in PARENT: flag('K02', 'error', '', u[0], 'No assignment row.')
    elif PARENT[u[0]] and PARENT[u[0]] not in UNIT: flag('K02', 'error', '', u[0], f'Parent {PARENT[u[0]]} is not in the Units table.')
# K08 speed
byunit = {}
for p in pos:
    if p['lat'] != '': byunit.setdefault(p['unit_id'], []).append(p)
for uid, rows in byunit.items():
    rows = [r for r in rows if ptime(r['se']) not in (None, 'bad')]
    rows.sort(key=lambda r: ptime(r['se']))
    lim = 15 if UNIT[uid][5] == 'Cavalry' else 6
    for a, b2 in zip(rows, rows[1:]):
        d = dist(centre(a), centre(b2))
        if a['campaign_id'] in OPERATIONAL:
            t0 = ptime(a['ee']); t1 = ptime(b2['sl']) or ptime(b2['se'])
            if d < 3000 or t0 in (None, 'bad') or t1 in (None, 'bad'): continue
            days = max(1, (t1 - t0).days); lim_d = 60 if UNIT[uid][5] == 'Cavalry' else 35
            if d / 1000 / days > lim_d: flag('K08', 'review', b2['battle_id'] or b2['campaign_id'], f"{a['pos_id']} to {b2['pos_id']}", f'{UNIT[uid][2]}: {d/1000:.0f} km in {days} day(s). Possible by rail or bus; check.')
            continue
        t0 = ptime(a['ee'], True); t1 = ptime(b2['sl'])
        if d < 150 or t0 in (None, 'bad') or t1 in (None, 'bad'): continue
        hrs = (t1 - t0).total_seconds() / 3600
        bt = b2['battle_id'] or b2['campaign_id']
        if hrs <= 0.02: flag('K08', 'note', bt, f"{a['pos_id']} to {b2['pos_id']}", f'{UNIT[uid][2]}: the two rows are {d:.0f} m apart with no time between them. The move happens inside one of the rows.')
        elif d / 1000 / hrs > lim: flag('K08', 'review', bt, f"{a['pos_id']} to {b2['pos_id']}", f'{UNIT[uid][2]}: {d:.0f} m in {hrs*60:.0f} minutes is {d/1000/hrs:.1f} km/h.')
# K09 opposing units close together
def span(p):
    s = ptime(p['se']) or ptime(p['sl']); e = ptime(p['el'], True) or ptime(p['ee'], True)
    return s, e
CONTACT = ('attack', 'surrender', 'taking', 'lost', 'receiving', 'closing', 'counter', 'cut off', 'falling back', 'retir', 'retreat')
def contact(p): return any(k in str(p['activity']).lower() for k in CONTACT)
placed = [p for p in pos if p['lat'] != '' and (p['battle_id'] or p['campaign_id'] in OPERATIONAL)]
seen = set()
for i, a in enumerate(placed):
    for b2 in placed[i + 1:]:
        if a['campaign_id'] != b2['campaign_id'] or UNIT[a['unit_id']][3] == UNIT[b2['unit_id']][3]: continue
        (s1, e1), (s2, e2) = span(a), span(b2)
        if None in (s1, e1, s2, e2) or 'bad' in (s1, e1, s2, e2): continue
        ov = (min(e1, e2) - max(s1, s2)).total_seconds() / 60
        if ov < 10: continue
        if a['campaign_id'] in OPERATIONAL:
            if a['geometry'] == 'line' and b2['geometry'] == 'line' and crosses(a, b2):
                flag('K14', 'review', a['battle_id'] or a['campaign_id'], f"{a['pos_id']} and {b2['pos_id']}", f"The lines of {UNIT[a['unit_id']][2]} and {UNIT[b2['unit_id']][2]} cross while both rows are in force. One of them is on the wrong side of the other.")
            continue
        d = gap_between(a, b2)
        if d < 150 and not (contact(a) or contact(b2)):
            flag('K09', 'review', a['battle_id'], f"{a['pos_id']} and {b2['pos_id']}", f"{UNIT[a['unit_id']][2]} and {UNIT[b2['unit_id']][2]} are {d:.0f} m apart for {ov:.0f} minutes. Check that neither row has gone stale.")
# K10 child near parent
for a in placed:
    par = PARENT.get(a['unit_id'])
    if not par or UNIT[a['unit_id']][6] not in ('Regiment', 'Regiment (part)', 'Battalion'): continue
    best = None
    for b2 in placed:
        if b2['unit_id'] != par: continue
        (s1, e1), (s2, e2) = span(a), span(b2)
        if None in (s1, e1, s2, e2): continue
        if (min(e1, e2) - max(s1, s2)).total_seconds() / 60 < 10: continue
        d = gap_between(a, b2)
        if best is None or d < best[0]: best = (d, b2)
    if best and best[0] > 400: flag('K10', 'review', a['battle_id'], f"{a['pos_id']} and {best[1]['pos_id']}", f"{UNIT[a['unit_id']][2]} is {best[0]:.0f} m from the nearest row of its brigade ({UNIT[par][2]}).")
for w in WARS:
    if not w[4]: flag('K12', 'review', '', w[0], 'No Wikidata ID.')
for b in BATTLES:
    if not b[12]: flag('K12', 'note', b[0], b[0], 'No Wikidata ID (a part of a larger battle).' if b[2] else 'No Wikidata ID: not looked up.')
for r in routes:
    if r[3] not in UNIT: flag('K13', 'error', r[2], r[0], f'Unit {r[3]} missing.')
    for x in (r[7], r[8]):
        if x and x not in POSID: flag('K13', 'error', r[2], r[0], f'Position {x} missing.')
for e in events:
    for x in [y.strip() for y in str(e[7]).split(';') if y.strip()]:
        if x not in POSID: flag('K13', 'error', e[2], e[0], f'Position {x} missing.')

# ============ write workbook ============
wb = Workbook(); wb.remove(wb.active)
sheet(wb, 'Wars', ['war_id', 'name', 'start_year', 'end_year', 'wikidata_qid', 'war_atlas_slug', 'notes'], WARS, [9, 30, 10, 10, 13, 16, 80], keycols=1)
sheet(wb, 'Campaigns', ['campaign_id', 'war_id', 'name', 'start_date', 'end_date', 'wikidata_qid', 'notes'], CAMPAIGNS, [13, 9, 44, 12, 12, 13, 80], keycols=1)
sheet(wb, 'Battles', ['battle_id', 'campaign_id', 'parent_battle_id', 'name', 'start_earliest', 'start_latest', 'end_earliest', 'end_latest', 'lat', 'lon', 'coord_precision', 'coord_source',
                      'wikidata_qid', 'cdb90_id', 'war_atlas_slug', 'notes', 'extent_km'], BATTLES, [13, 12, 14, 40, 17, 17, 17, 17, 10, 11, 11, 26, 12, 9, 15, 80, 10], keycols=1)
sheet(wb, 'Phases', ['phase_id', 'battle_id', 'label', 'start', 'end', 'source_ids', 'notes'], PHASES, [9, 13, 42, 17, 17, 12, 60], keycols=1)
sheet(wb, 'Sides', ['side_id', 'war_id', 'name', 'frame', 'colour', 'notes'], SIDES, [9, 8, 50, 8, 9, 60], keycols=1)
wu = sheet(wb, 'Units', ['unit_id', 'unit_name', 'map_label', 'side_id', 'nation', 'branch', 'echelon', 'symbol_code', 'wikidata_qid', 'source_ids', 'sourced?', 'notes'], units,
           [13, 44, 16, 9, 16, 14, 14, 23, 12, 16, 9, 70], freeze='C2', keycols=1)
for r in range(2, wu.max_row + 1): wu.cell(r, 8).number_format = '@'
sheet(wb, 'Assignments', ['assign_id', 'unit_id', 'parent_unit_id', 'commander', 'strength / equipment', 'valid_from', 'valid_to', 'source_ids', 'notes'], assigns, [9, 13, 13, 40, 44, 12, 12, 16, 40], keycols=1)

PH = ['pos_id', 'campaign_id', 'battle_id', 'unit_id', 'unit_name', 'side', 'start_earliest', 'start_latest', 'end_earliest', 'end_latest', 'time_basis', 'activity', 'place_description',
      'geometry', 'lat', 'lon', 'line_end_lat', 'line_end_lon', 'via', 'coord_source', 'coord_precision_m', 'coordinate_basis', 'coordinate_confidence', 'source_ids', 'source_wording',
      'position_method', 'overall_confidence', 'notes', 'review_status', 'reviewer_notes', 'map_link', 'your_review_v1', 'changed in v2', 'changed in v3', 'changed in v4', 'changed in v5', 'place_ids', 'changed in v6', 'changed in v7']
CI = {h: i + 1 for i, h in enumerate(PH)}; CL = {h: L(i + 1) for i, h in enumerate(PH)}
prow = []
for i, p in enumerate(pos):
    r = i + 2; la, lo, d = CL['lat'], CL['lon'], CL['unit_id']
    prow.append([p['pos_id'], p['campaign_id'], p['battle_id'], p['unit_id'], f'=INDEX(Units!$B:$B,MATCH({d}{r},Units!$A:$A,0))', f'=INDEX(Units!$D:$D,MATCH({d}{r},Units!$A:$A,0))',
                 p['se'], p['sl'], p['ee'], p['el'], p['time_basis'], p['activity'], p['place'], p['geometry'], p['lat'], p['lon'], p['lat2'], p['lon2'], p['via'], p['coord_source'], p['coord_precision'],
                 p['cbasis'], p['cconf'], p['source_ids'], p['say'], p['method'], p['oc'], p['notes'], p['review'], p['rnotes'],
                 f'=IF({la}{r}="","",HYPERLINK("https://www.openstreetmap.org/?mlat="&{la}{r}&"&mlon="&{lo}{r}&"#map=16/"&{la}{r}&"/"&{lo}{r},"Open map"))', p['rev1'], p['ch2'], p['ch3'], p['ch4'], p['ch5'], p['place_ids'], p['ch6'], p['ch7']])
wp_ = sheet(wb, 'Positions', PH, prow, [7, 11, 12, 13, 30, 9, 16, 16, 16, 16, 24, 22, 40, 9, 10, 11, 10, 11, 14, 11, 10, 44, 12, 13, 58, 11, 11, 54, 14, 40, 11, 13, 50, 44, 50, 13, 30, 50, 60], freeze='E2', keycols=1)
last = len(pos) + 1
for r in range(2, last + 1):
    for h in ('lat', 'lon', 'line_end_lat', 'line_end_lon'): wp_.cell(r, CI[h]).number_format = '0.00000'
    for h in ('coordinate_confidence', 'overall_confidence'):
        v = wp_.cell(r, CI[h]).value
        if v in FILL: wp_.cell(r, CI[h]).fill = PatternFill('solid', fgColor=FILL[v])
    wp_.cell(r, CI['review_status']).fill = PatternFill('solid', fgColor='FFFF00'); wp_.cell(r, CI['reviewer_notes']).fill = PatternFill('solid', fgColor='FFFFE0')
    wp_.cell(r, CI['map_link']).font = Font(name=F, size=10, color='0563C1', underline='single')
    for h in ('changed in v3', 'changed in v4', 'changed in v5', 'changed in v6', 'changed in v7'):
        if wp_.cell(r, CI[h]).value: wp_.cell(r, CI[h]).fill = BLUE
    for h in ('start_earliest', 'start_latest', 'end_earliest', 'end_latest'): wp_.cell(r, CI[h]).number_format = '@'
dv = DataValidation(type='list', formula1='"Needs review,Accepted,Corrected,Rejected"', allow_blank=False); wp_.add_data_validation(dv); dv.add(f"{CL['review_status']}2:{CL['review_status']}{last}")
dv2 = DataValidation(type='list', formula1='"map_read,sketch_read,modern_map,marker,derived,estimate,none"', allow_blank=False); wp_.add_data_validation(dv2); dv2.add(f"{CL['coord_source']}2:{CL['coord_source']}{last}")

sheet(wb, 'Routes', ['route_id', 'campaign_id', 'battle_id', 'unit_id', 'kind', 'start', 'end', 'from_pos_id', 'to_pos_id', 'waypoints (lat, lon; ...)', 'source_ids', 'source_wording', 'confidence', 'notes'],
      routes, [9, 11, 12, 13, 9, 16, 16, 11, 10, 50, 13, 50, 11, 50], keycols=1)
sheet(wb, 'Events', ['event_id', 'campaign_id', 'battle_id', 'time_earliest', 'time_latest', 'name', 'summary', 'pos_ids', 'source_ids'], events, [9, 11, 12, 16, 16, 24, 70, 22, 14], keycols=1)
wc = sheet(wb, 'Conflicts', ['conflict_id', 'battle_id', 'question', 'what the sources say', 'how the pilot handled it', 'comment', 'status', 'v2 update: what the map adds', 'v3 update', 'v4 update: what the sketch adds', 'v5 update', 'v7 update'], conflicts,
           [10, 12, 30, 70, 42, 40, 10, 60, 40, 60, 12, 70], keycols=1)
sheet(wb, 'Gaps', ['gap_id', 'battle_id', 'gap', 'effect on the data', 'how to close it', 'status in v2', 'v3 update', 'v4 update', 'v5 update', 'v6 update', 'v7 update'], gaps, [8, 12, 44, 60, 60, 50, 36, 44, 12, 60, 60], keycols=1)
used = {}
for q in YP.P:
    for k_ in q['keys']: used[k_] = used.get(k_, 0) + 1
wpl = sheet(wb, 'Places', ['place_id', 'name in the 1914 sources', 'name today', 'lat', 'lon', 'coord_source', 'coord_precision_m', 'how placed', 'position rows using it', 'map_link'],
            [[k_, v[0], v[1], v[2], v[3], v[4], v[5], v[6], used.get(k_, 0), f'=HYPERLINK("https://www.openstreetmap.org/?mlat="&D{i_+2}&"&mlon="&E{i_+2}&"#map=14/"&D{i_+2}&"/"&E{i_+2},"Open map")'] for i_, (k_, v) in enumerate(sorted((kv for kv in YP.PL.items() if kv[0] in used), key=lambda kv: (RANK[kv[1][4]], kv[1][0])))],
            [10, 52, 22, 10, 10, 13, 10, 90, 10, 11], keycols=1)
for r in range(2, wpl.max_row + 1):
    wpl.cell(r, 4).number_format = '0.00000'; wpl.cell(r, 5).number_format = '0.00000'; wpl.cell(r, 10).font = Font(name=F, size=10, color='0563C1', underline='single')
sheet(wb, 'Sources', ['source_id', 'title', 'author', 'date', 'type', 'citation', 'page verified?', 'url', 'rights', 'notes', 'used_for'], sources, [8, 44, 24, 11, 26, 34, 12, 48, 30, 48, 11], keycols=1)

# Georeference: copied from v2 as it stands
src = v2v['Georeference']; wg = wb.create_sheet('Georeference')
for row in src.iter_rows():
    for c in row:
        n = wg.cell(c.row, c.column, c.value)
        if c.value is not None:
            n.font = Font(name=F, size=c.font.size or 10, bold=c.font.bold, color=c.font.color.rgb if c.font.color and isinstance(c.font.color.rgb, str) else '000000')
            n.alignment = WRAP
            if c.fill and c.fill.fgColor and c.fill.fgColor.rgb == 'FF1F2A44': n.fill = HFILL
for mr in src.merged_cells.ranges: wg.merge_cells(str(mr))
for k, d in src.column_dimensions.items(): wg.column_dimensions[k].width = d.width
for k, d in src.row_dimensions.items():
    if d.height: wg.row_dimensions[k].height = d.height
wg.sheet_view.showGridLines = False
wg.insert_rows(1); wg.cell(1, 1, 'Part 1: Gettysburg, the Bachelder map. Part 2, below: Trenton, Wiederhold\'s sketch.').font = Font(name=F, size=10, italic=True)
r = wg.max_row + 3
def gput(r, vals, head=False):
    for c, v in enumerate(vals, 1):
        x = wg.cell(r, c, v); x.font = Font(name=F, size=10, bold=head, color='FFFFFF' if head else '000000'); x.alignment = WRAP
        if head: x.fill = HFILL
        if v != '': x.border = BORDER
wg.cell(r, 1, 'How Wiederhold\'s sketch of Trenton was tied to the current street map').font = Font(name=F, size=14, bold=True, color='1F2A44'); r += 1
for t_ in ('The sketch is not a survey. Six places in the town centre were matched to the same places on the current street map (OpenStreetMap, S39) and a best-fit shift, turn and uniform scale computed from them: ' + f"{TR.SKETCH_FIT['scale']} m per pixel, turned {abs(TR.SKETCH_FIT['rot'])} degrees.",
           'The fit holds from the English Church south to the creek and east to the surrender ground. North of the church the sketch is squeezed to about half scale, and the outposts are not to scale, so positions there come from markers, street corners or distances scaled along a road.'):
    c = wg.cell(r, 1, t_); c.font = BF; c.alignment = WRAP; wg.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8); wg.row_dimensions[r].height = 44; r += 1
r += 1; gput(r, ['Control point', 'pixel x', 'pixel y', 'lat', 'lon', 'misfit (m)'], True); r += 1
for p_ in TR.SKETCH_FIT['points']: gput(r, list(p_)); r += 1
r += 1; gput(r, ['Place on the sketch', 'pixel x', 'pixel y', '', '', 'lat', 'lon', 'precision (m)', '', 'how placed'], True); r += 1
TREN_GEO_DONE = True
for k, v in TR.C.items():
    if v[5]: gput(r, [k, v[5][0], v[5][1], '', '', v[0], v[1], v[3], '', v[2]]); r += 1

# Georeference, part 3: the Ypres sketches
import json as _json
_FA = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'georef', 'ypres_sketchA_fit.json'))); _FS = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'georef', 'ypres_dated_sketches_fit.json')))
r = wg.max_row + 3
wg.cell(r, 1, 'How the Ypres sketch maps of the British official history were tied to the current map').font = Font(name=F, size=14, bold=True, color='1F2A44'); r += 1
for t_ in ('Sketch A (the Ypres area) is bound across two pages; about a kilometre of ground is lost in the binding between them, so each page was fitted on its own: a shift, a turn and one scale, from villages that are both on the sketch and in OpenStreetMap (S39). The dated sketches were fitted the same way, each on its own, allowing a slightly different scale across and down the page.',
           'The misfit is the typical distance between where the fit puts a village and where OpenStreetMap has it. It mixes three things: the sketch is generalised, my reading of each village symbol is good to about 50 m, and a village is not a point.'):
    c = wg.cell(r, 1, t_); c.font = BF; c.alignment = WRAP; wg.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8); wg.row_dimensions[r].height = 44; r += 1
r += 1; gput(r, ['Sketch', 'dates shown', 'villages used', 'typical misfit (m)', 'metres per pixel', 'used for'], True); r += 1
import math as _m
for h_, nm_, n_, rms_ in (('L', 'Sketch A, left page', 19, 113), ('R', 'Sketch A, right page', 21, 149)):
    gput(r, [nm_, 'no date (topography)', n_, rms_, round(_m.hypot(_FA[h_][0], _FA[h_][1]), 2), 'Base map in the playback; ten places re-read (right page)']); r += 1
_LAB = {'sketch04': '18 to 21 October', 'sketch07': '22 and 23 October', 'sketch08': '24 and 25 October', 'sketch09': '26 to 29 October', 'sketch10': '30 and 31 October', 'sketch12': '1 to 4 November', 'sketch13': '5 to 9 November', 'sketch14': '10 and 11 November'}
for k_, v_ in sorted(_FS.items()):
    key_ = k_.split('_')[0]; gput(r, ['Sketch ' + str(int(key_[6:])), _LAB[key_], v_['n'], round(v_['rms_aff']), 14.7, 'Backdrop in the playback; British and French lines for its last date read from it (v7)']); r += 1

# Checks
order = {'error': 0, 'review': 1, 'note': 2}
checks.sort(key=lambda c: (order[c[1]], c[0], c[2], c[3]))
RN = dict(RULES)
wk = sheet(wb, 'Checks', ['rule', 'what the rule tests', 'result', 'battle', 'record', 'finding'], [[c[0], RN[c[0]], c[1], c[2], c[3], c[4]] for c in checks] or [['', '', '', '', '', 'No findings']],
           [7, 50, 9, 13, 16, 100], freeze='A2')
for r in range(2, wk.max_row + 1):
    v = wk.cell(r, 3).value
    wk.cell(r, 3).fill = PatternFill('solid', fgColor={'error': 'FBE3E0', 'review': 'FFF2CC', 'note': 'EDEDED'}.get(v, 'FFFFFF'))

# Read me
wr = wb.create_sheet('Read me', 0)
NG = len(gp); NT = len(TR.P); NK = len(pos); NY = len(YP.P)
N7A = sum(1 for q in YP.P if q.get('sk')); N7G = len(YP.MOVED)
ne = sum(1 for c in checks if c[1] == 'error'); nr = sum(1 for c in checks if c[1] == 'review'); nn = sum(1 for c in checks if c[1] == 'note')
passed = [r for r in RULES if not any(c[0] == r[0] and c[1] in ('error', 'review') for c in checks)]
lines = [
 ('Military Map Explorer data pilot v7', 'title'),
 ('Three battles in one linked set of tables: the first morning at Gettysburg (1 July 1863), Trenton (25-26 December 1776) and First Ypres (18 October to 22 November 1914). Built 12 Nov 2026.', 'body'),
 ('', 'body'),
 ('What changed in v7', 'head'),
 (f'First Ypres only. The British and French lines are now read from the dated sketch maps of the British official history: the line drawn for 21, 23, 25, 29 and 31 October and for 4, 9 and 11 November. {N7A} Allied rows carry a line read from a sketch; each holds until the day before the next sketch. Rows between those dates that rest on text are still there and say so. Positions now has {NY} Ypres rows (v6 had 143).', 'body'),
 (f'The sketches show German formations as arrows, not lines. German rows keep the places the German account names; where that put a German line on or behind the Allied line as now mapped, its points are moved 500 m clear and marked "derived" ({N7G} rows). A row whose line had to change as the Allied line moved is split by date.', 'body'),
 ('A row read from a sketch has its points in the lat, lon, via and line_end columns and no place_ids, because the points are not named places. Its place_description says which sketch and gives the ends of the line by the nearest village. The description used before v7 is kept in the notes.', 'body'),
 ('Every changed or new row says what happened in the "changed in v7" column. A row that was split keeps its pos_id for the first part of its time. Four inferred French rows are withdrawn because the sketches contradict them: ' + '; '.join(f'{k} ({UNIT[v[0]][2]}, {v[1][5:]} to {v[2][5:]}): {v[4]}' for k, v in sorted(YP.RETIRED.items())), 'body'),
 ('What the sketches changed most, as I read them: they show no French retreat towards Pilckem on 10 November (YC12); they keep St. Eloi inside the French line on 11 November (YC07); they agree with the German account that Hill 60 was lost on the 11th (YC05); they still draw the British 1st Division in reserve on 25 October (YC11); and they put "Vidal" north of Ypres on 31 October and south of it by 9 November. These are readings of a printed sketch by eye against a kilometre grid, not of the text. Two French units are new (Hély d\'Oissel\'s group; the Woillemont and Olleris detachments) and the French IX and XVI Corps now have rows of their own. Conflicts and Gaps have a "v7 update" column; YC11, YC12 and YG14 to YG17 are new.', 'body'),
 ('', 'body'),
 ('What changed in v6', 'head'),
 ('First Ypres only. The sketch maps bound into the British official history are now in hand. Sketch A, a contoured map of the Ypres area, is georeferenced and is a base map in the playback. Ten places that had been put in from memory, or that sit in a different spot on today\'s map, are now read from it; the rows that use them say so under "changed in v6". The dated sketches (18 October to 11 November) are in the playback as a backdrop but have not yet been used to correct the unit lines: that is the next step, and it will change many rows.', 'body'),
 ('', 'body'),
 ('What changed in v5', 'head'),
 (f'First Ypres added: {NY} position rows for {sum(1 for u in YP.U if any(q["unit_id"] == u[0] for q in YP.P))} corps and divisions, {len(YP.U)} units in all, {len(YP.A)} assignment rows, {len(YP.EVENTS)} events, {len(YP.CONFLICTS)} conflicts and {len(YP.GAPS)} gaps. Gettysburg and Trenton are as they were in v4: if you have reviewed rows in v4, send it back and I will merge your columns by pos_id.', 'body'),
 ('This pilot is at a different scale. Time is in days, not minutes: a row runs from the evening of its first date to the evening of its last. A position is a sector, a line through named villages, not a point. Units are corps and divisions.', 'body'),
 ('New sheet, Places: every village or feature a Ypres position uses, with its name in the 1914 sources, its name today, coordinates and how it was placed. Positions list their places in the new place_ids column. Battles has a new extent_km column so that the distance check fits the size of the battle.', 'body'),
 ('Two new checks: K14 (the lines of opposing units must not cross) and K15 (every place named is on the Places sheet). The closeness check (K09) is not run for Ypres, because the two sides\' lines are drawn apart by hand and the gap means nothing.', 'body'),
 ('Coordinate confidence for Ypres is on a wider scale than for the other two battles: high within 500 m, medium within 1 km, low beyond. Almost every Ypres row is a line through village centres, so read the playback as a diagram, not a trench map.', 'body'),
 ('One fix to older data: units with echelon "Army" now carry the symbol code for an army (23), not a blank echelon.', 'body'),
 ('', 'body'),
 ('What changed in v4', 'head'),
 ('Trenton only. Coordinates now come from the current street map (OpenStreetMap) and from Lt. Wiederhold\'s 1776 sketch, which Morgan supplied. ' + f'{sum(1 for q in TR.P if q["ch4"].startswith("Coord"))} rows have new coordinates and {sum(1 for q in TR.P if q["ch4"].startswith("New"))} rows are new; the column "changed in v4" says what changed on each. Gettysburg is untouched.', 'body'),
 ('The sketch settled where the Hessians formed, fought and surrendered: the three written descriptions of the surrender ground turn out to be one block of today\'s city (Conflicts, TC08). It also raised three new questions (TC10 to TC12).', 'body'),
 ('', 'body'),
 ('What changed in v3', 'head'),
 ('The data is now stored the way the full product would store it: one table per kind of thing, joined by IDs. A position is one record that points to a unit, a campaign, an optional battle and its sources. The nested view (war, battle, side, unit, location) is produced from these tables, not stored.', 'body'),
 (f'Gettysburg: all {NG} rows carried over with your review status and notes unchanged. Units were split into Units (who they are) and Assignments (parent, commander and strength for a date range).', 'body'),
 (f'Trenton: {NT} new position rows, {len(TR.UNITS)} units, {len(TR.ROUTES)} routes, {len(TR.CONFLICTS)} conflicts and {len(TR.GAPS)} gaps. (Row counts are as of v4.)', 'body'),
 ('', 'body'),
 ('New fields', 'head'),
 ('Times: each position has an earliest and latest start and an earliest and latest end, as "YYYY-MM-DD HH:MM", a date alone, or "unknown". Where sources disagree the two times differ. Gettysburg example: Archer\'s line starts between 9:00 (the map) and 9:30 (the reports).', 'body'),
 ('coord_source: map_read (read off a georeferenced, surveyed period map), sketch_read (read off a period sketch and placed on the current map), modern_map (a named street corner or building on the current map), marker (a monument or marker at the spot), derived (worked out from other points), estimate (placed from a description), none. coord_precision_m is my estimate of how far off the point could be.', 'body'),
 ('via: extra points along a line that bends. Routes: the path a unit took between two positions, as waypoints. Events and Phases: the chapter markers for playback.', 'body'),
 ('symbol_code: the standard 20-digit military symbol code for each unit, so any mapping tool can draw it. wikidata_qid: the public ID that joins wars and battles to outside datasets. Units do not have them yet (gap G16).', 'body'),
 ('', 'body'),
 ('Sheets and how they link', 'head'),
 ('Wars > Campaigns > Battles (a battle can have a parent battle) > Phases. Sides belong to a war. Units belong to a side. Assignments give each unit its parent, commander and strength for a date range. Positions, Routes and Events point to a unit, a campaign and, where it applies, a battle. March and camp rows have no battle.', 'body'),
 ('Conflicts, Gaps and Sources work as before, with a column saying which battle they belong to. Georeference covers both period maps.', 'body'),
 ('', 'body'),
 ('Checks', 'head'),
 (f'{len(RULES)} rules are run over the data every time the file is built, and the findings are on the Checks sheet: {ne} errors, {nr} for review, {nn} notes. {len(passed)} rules passed cleanly.', 'body'),
 ('"Review" findings are not mistakes in the file; they are places where the data itself looks doubtful, such as two opposing units drawn in the same place.', 'body'),
 ('', 'body'),
 ('How to review', 'head'),
 ('On the Positions sheet set review_status (yellow) to Accepted, Corrected or Rejected and type corrections in reviewer_notes. A correction needs a source: a report, a tablet, a map or a book with a page. An AI or search summary on its own is not a source.', 'body'),
 ('For Trenton and Ypres, wording that begins "Paraphrase:" is my summary of the source, not a quotation. Only text inside quotation marks is quoted. The Ypres quotations came through a reading tool and have not been checked against the page (gap YG07).', 'body'),
 ('', 'body'),
 ('Counts', 'head'),
]
r = 1
for t_, k in lines:
    c = wr.cell(r, 1, t_)
    c.font = Font(name=F, size=14 if k == 'title' else 10, bold=k in ('title', 'head'), color='1F2A44' if k != 'body' else '000000')
    c.alignment = Alignment(wrap_text=True, vertical='top'); wr.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    if len(t_) > 140: wr.row_dimensions[r].height = 30 if len(t_) < 290 else 44
    r += 1
bcol, rcol, lcol, ccol, scol = CL['campaign_id'], CL['review_status'], CL['lat'], CL['coord_source'], CL['coordinate_confidence']
wr.unmerge_cells(start_row=r - 1, start_column=1, end_row=r - 1, end_column=3) if False else None
wr.cell(r, 1, '').font = BF; wr.cell(r, 2, 'Gettysburg').font = Font(name=F, size=10, bold=True); wr.cell(r, 3, 'Trenton').font = Font(name=F, size=10, bold=True); wr.cell(r, 4, 'First Ypres').font = Font(name=F, size=10, bold=True); r += 1
def both(label, fg, ft, fy):
    global r
    wr.cell(r, 1, label).font = BF
    for c, f in ((2, fg), (3, ft), (4, fy)):
        x = wr.cell(r, c, f); x.font = BF; x.alignment = Alignment(horizontal='left')
    r += 1
rng = lambda col: f'Positions!{col}2:{col}{last}'
for label, crit_col, crit in (('Position rows', None, None), ('Rows with coordinates', 'has', None), ('Coordinates read from a surveyed period map', ccol, 'map_read'), ('Coordinates read from a period sketch', ccol, 'sketch_read'), ('Coordinates from the current street map', ccol, 'modern_map'), ('Coordinates from a marker', ccol, 'marker'),
                              ('Coordinates worked out or estimated', ccol, 'est'), ('Rows still needing review', rcol, 'Needs review'), ('Rows accepted', rcol, 'Accepted')):
    fs = []
    for camp in ('ACW-GETT', 'ARW-TP', 'WW1-FL14'):
        base = f'{rng(bcol)},"{camp}"'
        if crit_col is None: fs.append(f'=COUNTIF({base})')
        elif crit_col == 'has': fs.append(f'=COUNTIFS({base},{rng(lcol)},"<>")')
        elif crit == 'est': fs.append(f'=COUNTIFS({base},{rng(ccol)},"derived")+COUNTIFS({base},{rng(ccol)},"estimate")')
        else: fs.append(f'=COUNTIFS({base},{rng(crit_col)},"{crit}")')
    both(label, *fs)
YB = '"YP*"'; cz = f'Conflicts!A2:A{len(conflicts)+1}'; gz = f'Gaps!A2:A{len(gaps)+1}'; kz = f'Checks!D2:D{len(checks)+1}'
both('Units', f'=COUNTIF(Units!D2:D{len(units)+1},"ACW-*")', f'=COUNTIF(Units!D2:D{len(units)+1},"ARW-*")', f'=COUNTIF(Units!D2:D{len(units)+1},"WW1-*")')
both('Conflicts logged', f'=COUNTIF(Conflicts!B2:B{len(conflicts)+1},"GETT*")', f'=COUNTIF(Conflicts!B2:B{len(conflicts)+1},"TREN")', f'=COUNTIF({cz},"YC*")')
both('Gaps logged (shared gaps counted for both older battles)', f'=COUNTIF(Gaps!B2:B{len(gaps)+1},"GETT*")+COUNTIF(Gaps!B2:B{len(gaps)+1},"both")', f'=COUNTIF(Gaps!B2:B{len(gaps)+1},"TREN")+COUNTIF(Gaps!B2:B{len(gaps)+1},"both")', f'=COUNTIF({gz},"YG*")')
both('Check findings for review', f'=COUNTIFS(Checks!C2:C{len(checks)+1},"review",Checks!D2:D{len(checks)+1},"GETT*")', f'=COUNTIFS(Checks!C2:C{len(checks)+1},"review",Checks!D2:D{len(checks)+1},"TREN")',
     f'=COUNTIFS(Checks!C2:C{len(checks)+1},"review",{kz},"Y*")+COUNTIFS(Checks!C2:C{len(checks)+1},"review",{kz},"MESS14")+COUNTIFS(Checks!C2:C{len(checks)+1},"review",{kz},"WW1*")')
wr.column_dimensions['A'].width = 46; wr.column_dimensions['B'].width = 24; wr.column_dimensions['C'].width = 24; wr.column_dimensions['D'].width = 60
wr.sheet_view.showGridLines = False
wb.save(OUT)
print('saved', NK, 'positions;', len(units), 'units;', len(routes), 'routes;', len(events), 'events;', len(conflicts), 'conflicts;', len(gaps), 'gaps;', len(sources), 'sources')
print('checks: errors', ne, 'review', nr, 'notes', nn, '| clean rules', len(passed), 'of', len(RULES))
for c in checks:
    if c[1] != 'note': print(c)
print('notes:', [(c[0], c[3]) for c in checks if c[1] == 'note'])
