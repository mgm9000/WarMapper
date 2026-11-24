"""Cowpens: the nearest towns of 1781, named at the edge of the map (24 Nov 2026, at Morgan's request).

No town or village stood near the Cowpens in January 1781 (Spartanburg was laid out as a courthouse village in 1785, Gaffney's land
was bought in 1804, the town of Cowpens chartered in 1880). The nearest places a reader of the campaign knows are 30 to 110 km off,
too far to zoom out to, so they are labels with show "far": the player names each at the edge of the map, on the line from the middle
of the screen towards it, with how far it is in a straight line. Positions, each checked against a second source:

  Gilbert Town, N.C.   35.40694, -81.94361  Gilbert Town Historic District (NRHP nomination, 2006, S112); NC highway marker O-4 stands
                                            about 2.5 km south-west of it on US 221 ("Rutherford County seat, 1781-85")
  Charlotte, N.C.      35.22694, -80.84333  the Mecklenburg courthouse of 1780 at Trade and Tryon Streets (NCpedia, Battle of Charlotte,
                                            S113); NC highway marker L-18 on South Tryon Street, a block away
  Winnsborough, S.C.   34.37707, -81.08796  the town centre, U.S. Census gazetteer via Wikipedia (S114); Cornwallis's quarters of Oct 1780 - Jan 1781 at
                                            127 N. Zion Street lie in it (Town of Winnsboro history: "about 20 dwellings" in 1780)
  Ninety Six, S.C.     34.14520, -82.01985  the colonial village at Ninety Six National Historic Site (NPS, S115), two miles south of
                                            today's town; the site's "Town of Ninety Six" marker stands here

All are marked approximate: a town is a few hundred metres across, and the distance shown is rounded to the mile.
It stops if the Labels sheet already has a "far" label for Cowpens.
"""
import os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from cowpens_audit_2026_11_24 import header, last_row, add

WAR = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Revolutionary War.xlsx')
SHARED = os.path.join(ROOT, 'data', 'WarMapper battle data', 'Sources and notes.xlsx')
PB = 'cowpens'
TOWNS = [('Gilbert Town', 35.40694, -81.94361), ('Charlotte', 35.22694, -80.84333),
         ('Winnsborough', 34.37707, -81.08796), ('Ninety Six', 34.14520, -82.01985)]
SOURCES = [
    ('S112', 'Gilbert Town Historic District, Rutherford County, North Carolina (National Register of Historic Places nomination)',
     'Philip Thomason and Steven D. Smith', '2006', 'Register nomination: survey and history of the site',
     'Thomason, Philip, and Steven D. Smith. "Gilbert Town Historic District." National Register of Historic Places nomination, North Carolina State Historic Preservation Office, February 2006.',
     'https://files.nc.gov/ncdcr/nr/RF0336.pdf',
     'Gilbert Town: William Gilbert\'s house, store, tavern, mill and smithy, three miles north-east of Rutherfordton; the Rutherford County seat in 1781-85; '
     'Ferguson\'s camp in September 1780. Position 35.40694, -81.94361 as the register entry gives it (read from the Wikipedia entry for the district), checked against NC highway marker O-4 on US 221, about 2.5 km away.'),
    ('S113', 'Charlotte, Battle of (NCpedia)', 'NCpedia (State Library of North Carolina)', 'n.d.', 'Reference article',
     'NCpedia, "Charlotte, Battle of." State Library of North Carolina.', 'https://www.ncpedia.org/charlotte-battle',
     'The 1780 courthouse stood at what is now the intersection of Trade and Tryon Streets; Cornwallis held the village from 26 Sept to 12 Oct 1780. '
     'Position 35.22694, -80.84333, checked against NC highway marker L-18 (South Tryon Street between Trade and 4th).'),
    ('S114', 'Winnsboro History (Town of Winnsboro)', 'Town of Winnsboro', 'n.d.', 'Town history page',
     'Town of Winnsboro, "Winnsboro History."', 'https://townofwinnsboro.com/winnsboro-history',
     'Position 34.37707, -81.08796: the town centre as the U.S. Census gazetteer gives it (read from Wikipedia, "Winnsboro, South Carolina"; not read from the gazetteer itself). Town of Winnsboro history: about 20 dwellings when Cornwallis wintered there in 1780-81; he marched from it on 8 Jan 1781. '
     'Cornwallis\'s quarters (127 N. Zion Street) lie within a few hundred metres.'),
    ('S115', 'Ninety Six National Historic Site: History and Culture', 'National Park Service', 'n.d.', 'Park history pages',
     'National Park Service, Ninety Six National Historic Site, "History & Culture" and online tour stop 13.', 'https://www.nps.gov/nisi/learn/historyculture/index.htm',
     'The courthouse village (about 12 houses, a courthouse and a jail in 1775-80), the British post Morgan was sent to threaten; two miles south of today\'s town. '
     'Position 34.14520, -82.01985, at the site\'s "Town of Ninety Six" marker (HMdb 11304), checked against the park\'s location on SC 248.'),
]


def main():
    wb = openpyxl.load_workbook(WAR)
    lb = wb['Labels']; h = header(lb)
    assert not any(lb.cell(r, 1).value == PB and lb.cell(r, h.index('show') + 1).value == 'far' for r in range(2, last_row(lb) + 1)), 'already done'
    for t, la, lo in TOWNS:
        add(lb, dict(playback_id=PB, text=t, other_name=None, lat=la, lon=lo, angle=None, level=0, kind='town', show='far', approximate='yes'))
    st = wb['Playback settings']
    n = last_row(st) + 1
    st.cell(n, 1, PB); st.cell(n, 2, 'about.9')
    st.cell(n, 3, 'No town or village stood near the Cowpens in 1781: Spartanburg was laid out in 1785, Gaffney in the 1800s, the town of Cowpens in 1880. '
                  'The nearest places named in the campaign are shown at the edge of the map, with an arrow and their distance in a straight line from the middle of the screen: '
                  'Gilbert Town in North Carolina (the Rutherford County seat, where Ferguson camped before Kings Mountain), Charlotte (the village Cornwallis held in the autumn of 1780), '
                  'Winnsborough (Cornwallis\'s winter camp, which he left on 8 January) and Ninety Six (the British post Morgan was sent to threaten).')
    wb['Read me'].append(['Cowpens: nearest towns (24 Nov 2026)', 'Four labels with show "far" (Gilbert Town, Charlotte, Winnsborough, Ninety Six), named at the edge of the map for orientation; about.9. Sources S112-S115. See pipeline/cowpens_far_towns_2026_11_24.py.'])
    sh = openpyxl.load_workbook(SHARED); so = sh['Sources']; sh_h = header(so)
    have = {so.cell(r, 1).value for r in range(2, last_row(so) + 1)}
    for sid, title, author, date, typ, cit, url, notes in SOURCES:
        assert sid not in have, sid
        add(so, {'source_id': sid, 'title': title, 'author': author, 'date': date, 'type': typ, 'citation': cit, 'page verified?': 'n/a (a web page)',
                 'url': url, 'rights': 'Used for a position and a fact only; nothing hosted.', 'notes': 'Read 24 Nov 2026. ' + notes, 'used_for': 'COWP',
                 'kind': 'reference', 'war': 'ARW', 'rights_status': 'not hosted', 'may_host': 'no', 'rights_checked': '2026-11-24', 'site': url.split('/')[2]})
    rm = sh['Read me']; rm.insert_rows(1, 3)
    rm.cell(1, 1, 'What changed on 24 November 2026 (night): the nearest towns at Cowpens')
    rm.cell(2, 1, 'Revolutionary War.xlsx, Cowpens: four Labels rows with show "far" (new): Gilbert Town, Charlotte, Winnsborough and Ninety Six, the nearest places of 1781, '
                  'named at the edge of the map with an arrow and a straight-line distance, since the reader cannot zoom out 30 to 110 km. Sources S112 to S115 (positions, each '
                  'checked against a second source). Playback setting about.9 explains them. Written by pipeline/cowpens_far_towns_2026_11_24.py.')
    wb.save(WAR); sh.save(SHARED); print('written')


if __name__ == '__main__':
    main()
