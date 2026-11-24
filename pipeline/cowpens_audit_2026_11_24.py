"""24 Nov 2026: Cowpens, after the audit of its 90 position rows and a reading of Bearss (1967). Run once.

  python3 pipeline/cowpens_audit_2026_11_24.py

Morgan approved seven changes (24 Nov): the audit's findings, with Bearss's distances where the two agree.
  1. Ratings: five rows marked `stated` that no source places become `inferred`; eight `medium` ratings become `low`.
  2. The British first line moves back from 70 m to -85 m up the road: Bearss's Plate I puts it 292 m in front of the skirmish line,
     against 135 m before (CH16). Everything placed from it moves with it (the guns, the 71st, the reserve cavalry, the flank dragoons, Tarleton).
  3. The British infantry surrender about 180 m (200 yards) back from where Howard's volley struck it (Bearss), not at once; Morgan's camp
     moves to the ravine north-east of the road where Bearss draws it; Washington's charge ends behind the British right, as its wording says.
  4. Page numbers: Fleming's handbook (S104) and the 1928 Army War College study (S103) print the page number at the foot of the page, so every
     page cited from them was one too low (the page split read each number as the top of a page). Five page errors in the staff ride (S95) too.
  5. A Park Service wayside cited as a second witness is taken off where it stands 140 to 215 m from the unit as drawn (CP85, CP95, CP104).
     After the move in 3, the surrender rows (CP56, CP66, CP76) lie about 30 m from wayside 13030, so it stays there.
  6. Two new hypotheses (CH16, CH17); Bearss added as evidence to CH01, CH02, CH05, CH06, CH08, CH09 and CH14; Bearss is source S107; gap CG01 closed.
  7. The two captured 3-pounders leave the map at 07:51 instead of standing as British symbols until 08:30.

It stops if source S107 is already in Sources and notes.xlsx. The audit report is on the pull request.
"""
import os, re, sys
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cowpens_geo as G

FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'WarMapper battle data')
WAR = os.path.join(FOLDER, 'Revolutionary War.xlsx'); SHARED = os.path.join(FOLDER, 'Sources and notes.xlsx')
DAY, TODAY = '1781-01-17', '2026-11-24'
def T(hm): return '%s %s' % (DAY, hm)
at, line = G.at, G.line
FRAME = ('Placed by distance along the Historic Green River Road as OpenStreetMap draws it (S39), counted from the south-east end of the Battlefield Trail loop (35.13294, -81.81012), '
         'where the staff ride\'s Vantage 6 (S95, p. 77) and the NPS wayside "The British Army" (S105) put the head of Tarleton\'s column as it came onto the field. ')
B_BRIT = FRAME + ('The line of battle is 85 m short of that point (at -85 m) and square to the road: Bearss\'s Plate I draws it 292 m (320 yards) in front of the skirmish line (205 m up the road), '
                  'and his text has it close "to within 300 yards of Morgan\'s skirmish line" (S107, p. 17). Tarleton\'s own "within three hundred yards of the enemy" (S97) fits it. '
                  'Morgan\'s "four hundred yards in front of our advanced corps" (S96) would put it 75 m further back, and the NPS wayside "Form the Line of Battle" 220 m further forward (CH16). '
                  'Each unit has its share of about 340 yards by its strength (S95, p. 91), in Tarleton\'s order from right to left.')
BEARSS_URL = 'https://dc.statelibrary.sc.gov/items/ef5e6740-8015-4647-88b3-9820a8382285'
S107 = {'source_id': 'S107', 'title': 'The Battle of Cowpens: A Documented Narrative & Troop Movement Maps', 'author': 'Edwin C. Bearss', 'date': '1967-10-15',
        'type': 'Modern secondary: National Park Service study, with four troop movement maps on a surveyed base',
        'citation': 'Edwin C. Bearss, The Battle of Cowpens: A Documented Narrative & Troop Movement Maps (Washington: Office of Archeology and Historic Preservation, National Park Service, 15 October 1967). Reprinted, Johnson City, Tenn.: Overmountain Press, 1996. Plates I to IV: Troop Movements of Phases I to IV.',
        'page verified?': 'yes (text read by printed page, 24 Nov 2026; the four plates read from the page images)',
        'url': BEARSS_URL,
        'rights': 'National Park Service study of 1967 by an NPS historian: a U.S. government work, public domain. Morgan\'s copy carries no copyright notice. The 1996 Overmountain Press reprint is a separate edition and is not the copy used.',
        'notes': 'Read 24 Nov 2026 from Morgan\'s copy (Historical Info/History 340/battle-of-cowpens.pdf, 39 pages). Printed pages: the camp, p. 8; the ground and the knolls, p. 11; the British deployment, p. 17; the battle, pp. 18-22; notes on the order of battle, p. 14. '
                 'Plates I (after p. 12), II (after p. 20), III and IV (after p. 21) are drawn to scale (a bar of 1,125 feet; 1.145 m to a pixel at 300 dpi) on a contour base whose heights (920 to 980 feet) match today\'s elevation data along the road. '
                 'The plates do not agree with each other to better than about 100 m: Plate II draws Howard\'s line some 100 m further forward than Plate I. Distances were measured on Plate I between unit symbols along the road: British line to skirmishers 292 m, skirmishers to militia 109 m, militia to Howard 132 m. '
                 'Not fitted to the ground yet; a candidate base map (gap CG02).',
        'used_for': 'COWP', 'kind': 'official history', 'war': 'ARW', 'rights_status': 'public domain', 'may_host': 'yes (confirm before hosting the plates)', 'rights_checked': TODAY,
        'site': 'dc.statelibrary.sc.gov (South Carolina State Library); Morgan\'s Mac', 'local_copy': 'Historical Info/History 340/battle-of-cowpens.pdf'}

# ------------------------------------------------------------------ position rows: field -> new value (a callable takes the old value)
def add_note(s): return lambda old: ((old + ' ') if old else '') + s
def add_src(*ids): return lambda old: '; '.join(dict.fromkeys([x.strip() for x in (old or '').split(';') if x.strip()] + list(ids)))
def drop_src(*ids): return lambda old: '; '.join(x.strip() for x in (old or '').split(';') if x.strip() and x.strip() not in ids)
def geom(g):
    if isinstance(g[0], tuple): return {'geometry': 'line', 'lat': g[0][0], 'lon': g[0][1], 'line_end_lat': g[1][0], 'line_end_lon': g[1][1]}
    return {'geometry': 'point', 'lat': g[0], 'lon': g[1], 'line_end_lat': None, 'line_end_lon': None}

AUD = 'Audit of 24 Nov 2026: '
EDITS = {
    # 1. ratings
    'CP07': {'position_method': 'inferred', 'notes': add_note(AUD + 'was `stated`; no source says where in Pickens\'s line the riflemen went.')},
    'CP08': {'position_method': 'inferred', 'notes': add_note(AUD + 'was `stated`; no source says where in Pickens\'s line the riflemen went.')},
    'CP112': {'position_method': 'inferred', 'notes': add_note(AUD + 'was `stated`; the sources say only that they left the field, not where they went.')},
    'CP127': {'position_method': 'inferred', 'notes': add_note(AUD + 'was `stated`; the sources say only that they escaped, not where they went.')},
    'CP137': {'position_method': 'inferred', 'notes': add_note(AUD + 'was `stated`; the sources say only that he escaped down the road, not where he was at this time.')},
    'CP05': {'overall_confidence': 'low', 'notes': add_note(AUD + 'overall `medium` to `low`: the staff ride (S95, p. 50) takes Hammond\'s order, the reverse of these rows (CH05). Bearss (S107, p. 14) follows Morgan, as these rows do.')},
    'CP06': {'overall_confidence': 'low', 'notes': add_note(AUD + 'overall `medium` to `low`: the staff ride (S95, p. 50) takes Hammond\'s order, the reverse of these rows (CH05). Bearss (S107, p. 14) follows Morgan, as these rows do.')},
    'CP10': {'overall_confidence': 'low', 'coordinate_confidence': 'low', 'coord_precision_m': 100,
             'notes': add_note(AUD + 'both confidences `medium` to `low`. The places given for this line run from 278 m up the road (wayside 77693) to 400 m (the staff ride\'s walk); the staff ride also thinks Pickens\'s men were "probably ... centered on his left flank" rather than across the road (S95, p. 50). '
                               'Bearss draws the line about 110 m behind the skirmishers and 130 m in front of Howard, and wider than here, about 450 m flank to flank (S107, Plate I).')},
    'CP03': {'overall_confidence': 'low', 'coordinate_confidence': 'low', 'notes': add_note(AUD + 'both `medium` to `low`: Howard says Morgan rode ahead to choose the ground, not where he stood when the line faced about.')},
    'CP102': {'notes': add_note(AUD + 'wayside 13031 is cited for what happened (the order to Wallace), not for the place: it stands about 300 m up the road, 140 m short of this row.')},
}
# 2. the British first line, and what is placed from it
for pid, o1, o2 in (('CP51', -175, -90), ('CP61', -85, 45), ('CP71', 50, 135)):
    EDITS[pid] = dict(geom(line(-85, o1, o2)), coordinate_basis=B_BRIT, overall_confidence='low', source_ids=add_src('S107'), cross_checked_by='S107; S97',
                      source_pages=add_src('S107 p. 17 and Plate I'),
                      notes=add_note(AUD + 'moved back 155 m (from 70 m up the road), and overall `medium` to `low`. See CH16.'))
for pid, o in (('CP81', -88), ('CP91', 48)):
    EDITS[pid] = dict(geom(at(-80, o)), coordinate_basis=FRAME + 'A few metres in front of the line at -85 m up the road, in the gap Tarleton gives it (CH16).',
                      notes=add_note(AUD + 'moved back with the British line (CH16).'))
EDITS['CP43'] = dict(geom(at(-85, 185)), coordinate_basis=B_BRIT, notes=add_note(AUD + 'moved back with the British line (CH16). Which flank Ogilvie held is disputed (CH17).'))
EDITS['CP121'] = dict(geom(at(-85, -215)), coordinate_basis=B_BRIT, notes=add_note(AUD + 'moved back with the British line (CH16). Bearss names Ogilvie as the captain of these right-flank dragoons (CH17).'))
EDITS['CP131'] = dict(geom(at(-115, 0)), coordinate_basis=B_BRIT + ' Tarleton is drawn 30 m behind the centre of the line.', notes=add_note(AUD + 'moved back with the British line (CH16).'))
EDITS['CP101'] = dict(geom(line(-222, 60, 170)), coordinate_basis=B_BRIT + ' The 71st is 137 m (150 yards) behind that line and reaching a little beyond its left.',
                      overall_confidence='low', coordinate_confidence='low', source_ids=add_src('S107'),
                      notes=add_note(AUD + 'moved back with the British line (CH16), and both confidences `medium` to `low`: Hanger says the 71st was "but 300 yards" behind (S95, p. 159 n. 29), Mackenzie that it "remained near a mile distant" (S102, in S95 p. 152), and Bearss that the reserve "was about a mile away" when Tarleton sent for it (S107, p. 19). See CH14.'))
EDITS['CP111'] = dict(geom(at(-270, 40)), coordinate_basis=B_BRIT + ' The reserve cavalry is put 185 m behind the line, just behind the 71st: Tarleton gives it no distance of its own.',
                      notes=add_note(AUD + 'moved back with the British line (CH16).'))
# 3. the surrender, Morgan's camp, Washington's charge
SURR = FRAME + ('About 360 m up the road: Bearss has the light infantry, the Legion infantry and the 7th overtaken and surrendering "about 200 yards from the point of disaster" (S107, p. 21), '
                'counted here from where Howard\'s volley struck them (538 m). The NPS wayside "Double Envelopment" stands about 330 m up the road. An estimate.')
for pid in ('CP56', 'CP66', 'CP76'):
    EDITS[pid] = {'coordinate_basis': SURR, 'source_ids': add_src('S107'), 'notes': add_note(AUD + 'moved back 95 m (from 455 m), after Bearss. It now lies about 30 m from wayside 13030, which stays as the second witness.')}
for pid, o1, o2 in (('CP56', -175, -90), ('CP66', -85, 45), ('CP76', 50, 135)): EDITS[pid].update(geom(line(360, o1, o2)))
for pid in ('CP85', 'CP95'):
    EDITS[pid] = {'cross_checked_by': drop_src('S105'), 'show_to': T('07:51'), 'end_earliest': T('07:51'), 'end_latest': T('08:51'),
                  'notes': add_note(AUD + 'wayside 13029 ("A Race for the Grasshopper") is cited for who took the guns, not where: it stands about 306 m up the road, 215 m from the guns as drawn (CG05). It is no longer the second witness. The gun now leaves the map at 07:51, once taken.')}
EDITS['CP104'] = {'cross_checked_by': drop_src('S105'), 'source_ids': add_src('S107'),
                  'notes': add_note(AUD + 'wayside 13030 stands about 140 m from this row and is no longer cited as its second witness. Bearss: the 71st "slowly pulled back" until Howard\'s right wing and the militia closed on it (S107, p. 21).')}
CAMP = at(555, -375)
EDITS['CP01'] = dict(geom(CAMP), coordinate_basis=FRAME + ('About 555 m up the road and 375 m north-east of it, in a ravine: measured on Bearss\'s Plate I, which draws the camp level with the main line and off the road to the north-east, '
                     'and his text puts it "in a wooded ravine, about 1,000 yards northwest of the cabin of Robert Scruggs" (S107, p. 8). The staff ride puts it about 300 m north of its Vantage 1 (S95, p. 72), some 500 m from here: not reconciled.'),
                     position_method='stated', coordinate_confidence='low', coord_precision_m=250, source_ids=add_src('S107'), cross_checked_by='S107', source_pages=add_src('S107 p. 8 and Plate I'),
                     notes=add_note(AUD + 'moved from the road 1 km up it to where Bearss draws the camp.'))
EDITS['CP35'] = dict(geom(at(470, -140)), coordinate_basis=FRAME + 'Behind the British right, about 70 m behind where it stood when Howard\'s volley struck it (538 m) and 140 m north-east of the road, beyond the light infantry. From the staff ride\'s map 14 (S95, p. 61) and Bearss\'s Plate IV. An estimate.',
                     source_ids=add_src('S107'), notes=add_note(AUD + 'moved from behind the British centre to behind its right, as the wording says.'))

# 4. page numbers, row by row (the S104 and S103 pages are shifted for every row further down)
PAGE_FIXES = {
    'CP40': [('S97 in S95 p. 147', 'S97 in S95 p. 148')],
    'CP41': [('S97 in S95 p. 147', 'S97 in S95 p. 148'), ('S95 pp. 51, 77', 'S95 pp. 50, 51, 77')],
    'CP56': [('S97 in S95 p. 82', 'S97 in S95 p. 150'), ('S101 in S95 p. 135', 'S101 in S95 p. 134')],
    'CP66': [('S97 in S95 p. 82', 'S97 in S95 p. 150'), ('S101 in S95 p. 135', 'S101 in S95 p. 134')],
    'CP76': [('S97 in S95 p. 82', 'S97 in S95 p. 150'), ('S101 in S95 p. 135', 'S101 in S95 p. 134')],
    'CP35': [('S101 in S95 pp. 137, 135', 'S101 in S95 pp. 137, 134')],
    'CP21': [('S98 in S95 pp. 126-127', 'S98 in S95 pp. 126, 128-129')],
    'CP22': [('S98 in S95 pp. 126-127', 'S98 in S95 pp. 126, 128-129')],
    'CP23': [('S98 in S95 pp. 126-127', 'S98 in S95 pp. 126, 128-129')],
    'CP34': [('S98 in S95 p. 128', 'S98 in S95 p. 127')],
}
for pid in ('CP53', 'CP63', 'CP73'): PAGE_FIXES[pid] = [('about 30 to 50 yards (S104, p. 66)', 'about 30 yards (S104, p. 66)')]   # applied after the S104 shift

# the Park Service handbook (S104) and the 1928 study (S103): the printed page sits at the foot, so every page read was one too low
SPECIAL_S104 = {'85': '88', '81': '81-82', '69-70': '70-71', '53-77': '54-78', '85-88': '88-91'}
def shift(m, special):
    prefix, num = m.group(1), m.group(2)
    if num in special:
        new = special[num]
        return (prefix[:-3] + 'pp. ' if ('-' in new or ',' in new) and prefix.endswith(' p. ') else prefix) + new
    if '-' in num:
        a, b = num.split('-'); return '%s%d-%d' % (prefix, int(a) + 1, int(b) + 1)
    return '%s%d' % (prefix, int(num) + 1)
RX = {s: re.compile(r'(%s,? (?:p|pp)\. )(\d+(?:-\d+)?)' % s) for s in ('S104', 'S103')}
def fix_pages(text):
    if not isinstance(text, str): return text
    text = text.replace('S103 p. 66: "the action having lasted', '@@P69@@')
    text = RX['S104'].sub(lambda m: shift(m, SPECIAL_S104), text)
    text = RX['S103'].sub(lambda m: shift(m, {'65-66': '66, 69'}), text)
    text = text.replace('@@P69@@', 'S103 p. 69: "the action having lasted')
    text = text.replace('S104, opening of the narrative (seen in the Project Gutenberg text; the text of the Archive scan has lost the line)', 'S104, Prologue by George Scheer, before p. 12')
    text = text.replace('S104, opening of the narrative', 'S104, Prologue by George Scheer, before p. 12')
    return text

# ------------------------------------------------------------------ hypotheses
def H(hid, q, a, b, c, ev_for, ev_against, adopted, because, conf, rows, srcs, nxt):
    return dict(hypothesis_id=hid, battle_id='COWP', question=q, reading_a=a, reading_b=b, reading_c=c, evidence_for=ev_for, evidence_against=ev_against, adopted_reading=adopted, adopted_because=because,
                confidence=conf, status='Proposed', decided_by='Claude, after the audit; Morgan approved the change on 24 Nov 2026', decided_on=TODAY, reviewed_on=None, rows=rows, source_ids=srcs, next_step=nxt,
                history='New on 24 Nov 2026, from the audit of the Cowpens rows and the reading of Bearss.')
NEW_HYP = [
    H('CH16', 'How far in front of the Americans did Tarleton form his line?', 'About 300 yards in front of the skirmish line (-85 m up the road)', 'About 400 yards in front of the skirmish line (Morgan)', 'About 150 yards in front of the skirmishers, 300 in front of the militia (the NPS wayside; Graham)',
      'S107 Bearss p. 17: "closed to within 300 yards of Morgan\'s skirmish line"; Plate I measures 292 m.\nS97 Tarleton, in S95 p. 78: instructed "to advance within three hundred yards of the enemy".\nS107 p. 18: dragoons seen "400 yards in front of his skirmishers".',
      'S96 Morgan, in S95 p. 123: "four hundred yards in front of our advanced corps" (reading B, 75 m further back).\nS105 wayside 13423 "Form the Line of Battle", about 135 m up the road: the 7th "formed in this immediate area" (reading C).\nGraham (1856), as the audit read him: "within three hundred yards of the line of the militia".',
      'A', 'Bearss measured it on a surveyed base, and it fits Tarleton\'s own figure. Until 24 Nov the rows followed C, which put the line 135 m from the skirmishers while quoting Morgan\'s 400 yards.', 'low',
      'CP51; CP61; CP71; CP81; CP91; CP101; CP111; CP121; CP131; CP43', 'S96; S97; S105; S107', 'Fit Bearss\'s Plate I to the ground and read the line from it.'),
    H('CH17', 'Which flank did Ogilvie\'s dragoons hold?', 'The British left: two troops of Legion cavalry under Ogilvie; the 17th Light Dragoons on the right', 'The British right: Ogilvie commanded the 50 dragoons on the right, the 17th Light Dragoons, who rode down the militia', None,
      'S95 p. 76: "On the extreme left flank stood two troops of British Legion cavalry under Captain Ogilvie"; "To their right were stationed the fifty troopers of the 17th Light Dragoons."',
      'S107 Bearss p. 18: Tarleton "ordered Captain Ogilvie, who commanded the 50 dragoons on the right, to charge the retreating Americans"; the charge is made by "the hard-riding men of the 17th Light Dragoons". Plates II and III draw "Ogilvie" on the British right.',
      'A, for the names', 'The charge on the militia is drawn by the right-flank troop either way; only the name on the left-flank symbol depends on this. The staff ride is followed, as for the other units.', 'low',
      'CP41; CP42; CP43; CP44; CP45; CP46; CP47; CP121; CP124', 'S95; S97; S107', 'Read Tarleton (1787) on which captain led which flank.'),
]
HYP_ADD = {   # hypothesis -> column -> text added
    'CH01': {'evidence_for': '\nS107 Bearss p. 18: "It was about 7 a.m."; p. 22: "The battle had commenced about 7 a.m."'},
    'CH02': {'evidence_for': '\nS107 Bearss p. 22: it "had continued for nearly an hour".'},
    'CH05': {'evidence_for': '\nS107 Bearss p. 14 n. 28 and Plate I: McDowell on the right, Cunningham on the left, as Morgan reported.'},
    'CH06': {'evidence_against': '\nS107 Bearss p. 14 n. 26 and Plate I: Triplett-Beaty on Howard\'s right and 100 yards to its rear, Tate-Buchanan on the left (following Hammond).'},
    'CH08': {'evidence_against': '\nS107 Bearss p. 20 and Plate III: the line fell back across "the swale separating the knolls" and "started up the hillock on which the cavalry had been posted"; the plate draws it facing about some 330 m (360 yards) behind its first position, past the crossroads.'},
    'CH09': {'evidence_for': '\nS107 Bearss p. 18: the militia "filed off toward the left end of Howard\'s line".'},
    'CH14': {'evidence_against': '\nS107 Bearss p. 19: "The reserve at this time was about a mile away."'},
}
for hid in HYP_ADD: HYP_ADD[hid]['history'] = '\n24 Nov 2026: Bearss (S107) added to the evidence; the adopted reading is unchanged.'


def header(ws): return [c.value for c in ws[1]]
def last_row(ws):
    r = ws.max_row
    while r > 1 and ws.cell(r, 1).value in (None, ''): r -= 1
    return r
def add(ws, row):
    h = header(ws); r = last_row(ws) + 1
    for k in row: assert k in h, '%s: no column %r' % (ws.title, k)
    for c, name in enumerate(h, 1):
        if row.get(name) is not None: ws.cell(r, c, row[name])
    return r
def rows_by_id(ws, idcol=1):
    return {ws.cell(r, idcol).value: r for r in range(2, last_row(ws) + 1) if ws.cell(r, idcol).value}
def setv(ws, r, col, value):
    h = header(ws); assert col in h, '%s: no column %r' % (ws.title, col)
    c = ws.cell(r, h.index(col) + 1); c.value = value(c.value) if callable(value) else value


def wp(pts): return '; '.join('%.5f, %.5f' % p for p in pts)
MODERN = [(35.11533, -81.78412), (35.11650, -81.78463), (35.11705, -81.78496), (35.11735, -81.78522), (35.11965, -81.78809), (35.12036, -81.78881), (35.12083, -81.78920), (35.12153, -81.78966), (35.12294, -81.79050)]
LINK = [(35.13132, -81.79743), (35.13162, -81.80223)]
ROUTES = {'RC02': G.along(G.EAST, -270)[::-1] + LINK[::-1][1:] + MODERN[::-1],
          'RC10': [at(625, -150), at(560, -250), at(480, -230), at(470, -140)],
          'RC11': [at(-222, 115), at(150, 215), at(440, 200)]}


def main():
    sh = openpyxl.load_workbook(SHARED); wb = openpyxl.load_workbook(WAR)
    if 'S107' in rows_by_id(sh['Sources']): print('S107 is already in the workbook: nothing done'); return
    # sources
    add(sh['Sources'], S107)
    src = sh['Sources']; ids = rows_by_id(src)
    setv(src, ids['S97'], 'citation', lambda v: v.replace('pp. 147-151', 'pp. 148-151'))
    setv(src, ids['S103'], 'notes', lambda v: v.replace('(pp. 65-66)', '(pp. 66, 69)') + ' 24 Nov 2026: the book prints its page numbers at the foot; every page cited from it before this date was one too low and has been corrected.')
    setv(src, ids['S104'], 'notes', lambda v: v.replace('(pp. 53-77)', '(pp. 54-78)').replace('(pp. 85-88)', '(pp. 88-91)') + ' 24 Nov 2026: the book prints its page numbers at the foot; every page cited from it before this date was one too low and has been corrected ("the bend in the road", "less than an hour" and "advanced at sunrise" are on p. 88). "Some 830 soldiers" is in George Scheer\'s Prologue, before p. 12.')
    cand = sh['Source candidates']; cids = rows_by_id(cand)
    setv(cand, cids['SC-SOU03'], 'status', 'used: now source S107')
    setv(cand, cids['SC-SOU03'], 'notes', add_note('Read on 24 Nov 2026 from Morgan\'s copy (Historical Info/History 340/battle-of-cowpens.pdf): now S107.'))
    rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026: Cowpens after its audit')
    rm.cell(2, 1, 'Revolutionary War.xlsx, Cowpens only: the 90 position rows were audited against their sources, and Bearss\'s 1967 study was read (new source S107). Five rows marked `stated` became `inferred` and eight `medium` ratings became `low`; '
                  'three `medium` rows remain (CP20, CP24, CP32). The British first line moved back 155 m (CH16), the British surrender back 95 m, Morgan\'s camp to the ravine Bearss draws, and Washington\'s charge to behind the British right. '
                  'Every page cited from S103 and S104 moved up one (both books print page numbers at the foot), with five fixes to S95 pages. New hypotheses CH16 and CH17; Bearss added to seven others; gap CG01 closed. '
                  'Written by pipeline/cowpens_audit_2026_11_24.py.')
    # positions
    ws = wb['Positions']; pos = rows_by_id(ws); h = header(ws)
    cow = [p for p in pos if ws.cell(pos[p], h.index('battle_id') + 1).value == 'COWP']
    assert len(cow) == 90, len(cow)
    for pid in cow:
        r = pos[pid]
        for col in ('time_basis', 'coordinate_basis', 'source_wording', 'notes', 'source_pages'): setv(ws, r, col, fix_pages)
    for pid, fields in EDITS.items():
        for col, v in fields.items(): setv(ws, pos[pid], col, v)
    for pid, pairs in PAGE_FIXES.items():
        for col in ('source_pages', 'coordinate_basis', 'source_wording', 'notes'):
            c = ws.cell(pos[pid], h.index(col) + 1)
            for a, b in pairs:
                if isinstance(c.value, str) and a in c.value: c.value = c.value.replace(a, b)
    # units and assignments, events, hypotheses, gaps: the shifted pages
    for sheet, key, pred in (('Units', 'unit_id', lambda i: i.startswith('C-')), ('Assignments', 'unit_id', lambda i: i.startswith('C-')), ('Events', 'event_id', lambda i: i.startswith('CE')),
                             ('Hypotheses', 'hypothesis_id', lambda i: i.startswith('CH')), ('Gaps', 'gap_id', lambda i: i.startswith('CG')), ('Battles', 'battle_id', lambda i: i == 'COWP')):
        s = wb[sheet]; hh = header(s)
        for r in range(2, last_row(s) + 1):
            v = s.cell(r, hh.index(key) + 1).value
            if v and pred(v):
                for c in range(1, len(hh) + 1):
                    if isinstance(s.cell(r, c).value, str) and not s.cell(r, c).value.startswith('='): s.cell(r, c).value = fix_pages(s.cell(r, c).value)
    hy = wb['Hypotheses']; hids = rows_by_id(hy)
    for hid, cols in HYP_ADD.items():
        for col, text in cols.items(): setv(hy, hids[hid], col, lambda old, t=text: (old or '') + t)
    for hrow in NEW_HYP: add(hy, hrow)
    gp = wb['Gaps']; gids = rows_by_id(gp)
    setv(gp, gids['CG01'], 'status in v2', 'Closed, 24 Nov 2026: read from Morgan\'s copy (S107). Its distances moved the British first line (CH16) and the surrender, and gave two new disputed points (CH16, CH17).')
    setv(gp, gids['CG02'], 'how to close it', add_note('24 Nov 2026: Bearss\'s four plates (S107) are a public-domain National Park Service work drawn to scale on a contour base that matches today\'s ground: the best candidate so far, not yet fitted.'))
    setv(gp, gids['CG05'], 'effect on the data', add_note('Audit of 24 Nov 2026: the database\'s monument converts to 369 m up the road, against 482 m for OpenStreetMap\'s, and its "Continental Army" wayside to 380 m. If those are right, Howard\'s line and all placed from it lie about 100 m further south-east, and the three `medium` rows (CP20, CP24, CP32) should become `low`.'))
    # routes
    rt = wb['Routes']; rids = rows_by_id(rt)
    for rid, pts in ROUTES.items(): setv(rt, rids[rid], 'waypoints (lat, lon; ...)', wp(pts))
    # the captured guns leave the map; the camp label follows the camp
    tr = wb['Tracks']; th = header(tr)
    for r in range(2, last_row(tr) + 1):
        if tr.cell(r, th.index('playback_id') + 1).value == 'cowpens' and tr.cell(r, th.index('track_id') + 1).value in ('C-BR-RA1', 'C-BR-RA2'):
            tr.cell(r, th.index('hide_after_last_row') + 1).value = 'yes'
    lb = wb['Labels']; lh = header(lb)
    for r in range(2, last_row(lb) + 1):
        if lb.cell(r, lh.index('playback_id') + 1).value == 'cowpens' and (lb.cell(r, lh.index('text') + 1).value or '').startswith('Morgan\'s camp'):
            lb.cell(r, lh.index('lat') + 1).value, lb.cell(r, lh.index('lon') + 1).value = CAMP
    # source use row for Bearss
    su = wb['Source uses']; r = last_row(su) + 1
    add(su, dict(source_id='S107', title=S107['title'], campaign_id='ARW-SOU', playback_id='cowpens',
                 positions='=COUNTIFS(Positions!$X:$X,"*"&$A%d&"*",Positions!$B:$B,$C%d)' % (r, r), events='=COUNTIFS(Events!$I:$I,"*"&$A%d&"*",Events!$B:$B,$C%d)' % (r, r),
                 routes='=COUNTIFS(Routes!$K:$K,"*"&$A%d&"*",Routes!$B:$B,$C%d)' % (r, r), units='=COUNTIFS(Units!$J:$J,"*"&$A%d&"*",Units!$A:$A,"C-*")' % r,
                 period_maps='=COUNTIFS(Maps!$G:$G,$A%d,Maps!$A:$A,$D%d)' % (r, r), total='=SUM(E%d:I%d)' % (r, r)))
    rmw = wb['Read me']; rmw.append(['Cowpens audit (24 Nov 2026)', 'Ratings, five positions and many page numbers changed after the audit and the reading of Bearss (S107); new hypotheses CH16 and CH17. See the change log in "Sources and notes.xlsx" and pipeline/cowpens_audit_2026_11_24.py.'])
    wb.save(WAR); sh.save(SHARED)
    print('Cowpens audit fixes written: %d rows edited, %d new hypotheses' % (len(set(EDITS) | set(PAGE_FIXES)), len(NEW_HYP)))


if __name__ == '__main__':
    main()
