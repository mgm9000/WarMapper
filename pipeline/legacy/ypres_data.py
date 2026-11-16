"""First Ypres pilot data: 18 October to 22 November 1914, corps and divisions, one step per day.
Coordinates come from OpenStreetMap place nodes (yp/osm_raw.txt) or are worked out from them."""
import math
import os as _os0
OSMF = _os0.path.join(_os0.path.dirname(_os0.path.dirname(_os0.path.abspath(__file__))), 'data', 'osm', 'ypres.txt')
OSM = {}
for _l in open(OSMF, encoding='utf-8').read().split('\n'):
    if _l.startswith('p'):
        _k, _n, _c = _l.split('|'); _a, _b = _c.split(',')
        OSM.setdefault(_n, (50 + int(_a) / 1e4, 2 + int(_b) / 1e4))

# ---------- places: key -> (name in the 1914 sources, name today, lat, lon, coord_source, precision m, basis) ----------
PL = {}
def osm(key, old, modern, prec=800):
    la, lo = OSM[modern]
    PL[key] = (old, modern.split(' - ')[0], round(la, 5), round(lo, 5), 'modern_map', prec, f'OpenStreetMap place node for {modern.split(" - ")[0]} (S39); the unit was at or near the village, not at this exact point')
def est(key, old, modern, la, lo, prec, how, src='estimate'):
    PL[key] = (old, modern, la, lo, src, prec, how)
def off(key, base, north_m, east_m, what, prec=1000):
    b = PL[base]; la = b[2] + north_m / 111040; lo = b[3] + east_m / (111320 * math.cos(math.radians(b[2])))
    PL[key] = (what, '', round(la, 5), round(lo, 5), 'derived', max(prec, b[5]), f'{what}: placed {abs(north_m)} m {"north" if north_m >= 0 else "south"} and {abs(east_m)} m {"east" if east_m >= 0 else "west"} of {b[0]} to keep the two sides apart on the map; not a surveyed position')

for k, o, m in [('IEPE', 'Ypres', 'Ieper'), ('ZONN', 'Zonnebeke', 'Zonnebeke'), ('LANG', 'Langemarck', 'Langemark'), ('POEL', 'Poelcappelle', 'Poelkapelle'), ('PASS', 'Passchendaele', 'Passendale'),
                ('WROZ', 'Westroosebeke', 'Westrozebeke'), ('BECE', 'Becelaere', 'Beselare'), ('GHEL', 'Gheluvelt', 'Geluveld'), ('ZAND', 'Zandvoorde', 'Zandvoorde'),
                ('HOLL', 'Hollebeke', 'Hollebeke'), ('HOUT', 'Houthem', 'Houthem'), ('KORW', 'Kortewilde', 'Kortewilde'), ('VELD', 'Veldhoek', 'Veldhoek'), ('POLD', 'Polderhoek', 'Polderhoek'),
                ('REUT', 'Reutel', 'Reutel'), ('KEIB', 'Keiberg', 'Keiberg'), ('BROO', 'Cross-roads east of Zonnebeke (Broodseinde)', 'Broodseinde'),
                ('STJU', 'St. Julien', 'Sint-Juliaan'), ('WIEL', 'Wieltje', 'Wieltje'), ('PILK', 'Pilckem', 'Pilkem'), ('BIKS', 'Bixschoote', 'Bikschote'), ('NOOR', 'Noordschoote', 'Noordschote'),
                ('MERK', 'Merckem', 'Merkem'), ('LUIG', 'Luyghem', 'Luigem'), ('HOUL', 'Houthulst', 'Houthulst'), ('KLER', 'Clercken', 'Klerken'), ('WOUM', 'Woumen', 'Woumen'), ('DIKS', 'Dixmude', 'Diksmuide'),
                ('ESEN', 'Eessen', 'Esen'), ('BEER', 'Beerst', 'Beerst'), ('VLAD', 'Vladsloo', 'Vladslo'), ('KEIE', 'Keyem', 'Keiem'), ('SCHO', 'Schoore', 'Schore'), ('SCHB', 'Schoorbakke', 'Schoorbakke'),
                ('TERV', 'Tervaete', 'Tervate'), ('STUI', 'Stuyvekenskerke', 'Stuivekenskerke'), ('PERV', 'Pervyse', 'Pervijze'), ('RAMS', 'Ramscappelle', 'Ramskapelle'), ('NIEU', 'Nieuport', 'Nieuwpoort'),
                ('STJO', 'St. Georges', 'Sint-Joris'), ('MANN', 'Mannekensvere', 'Mannekensvere'), ('WEST', 'Westende', 'Westende'), ('KAAS', 'Caeskerke', 'Kaaskerke'), ('STAD', 'Staden', 'Staden'),
                ('ROES', 'Roulers', 'Roeselare'), ('HOOG', 'Hooglede', 'Hooglede'), ('GITS', 'Gits', 'Gits'), ('HAND', 'Handzaeme', 'Handzame'), ('ZARR', 'Zarren', 'Zarren'), ('TORH', 'Thourout', 'Torhout'),
                ('LICH', 'Lichtervelde', 'Lichtervelde'), ('ARDO', 'Ardoye', 'Ardooie'), ('MOOR', 'Moorslede', 'Moorslede'), ('DADI', 'Dadizeele', 'Dadizele'), ('ROLK', 'Rolleghem-Cappelle', 'Rollegem-Kapelle'),
                ('MENE', 'Menin', 'Menen'), ('GELU', 'Gheluwe', 'Geluwe'), ('WERV', 'Wervicq', 'Wervik'), ('COMI', 'Comines', 'Comines'), ('TENB', 'Tenbrielen', 'Ten Brielen'), ('WARN', 'Warneton', 'Warneton'),
                ('DEUL', 'Deulemont', 'Deûlémont'), ('PONR', 'Pont Rouge', 'Pont Rouge'), ('FREL', 'Frelinghien', 'Frelinghien'), ('LETQ', 'Le Touquet', 'Le Touquet'), ('MESS', 'Messines', 'Mesen - Messines'),
                ('WYTS', 'Wytschaete', 'Wijtschate'), ('OOST', 'Oosttaverne', 'Oosttaverne'), ('STEL', 'St. Eloi', 'Sint-Elooi'), ('VOOR', 'Voormezeele', 'Voormezele'), ('WULV', 'Wulverghem', 'Wulvergem'),
                ('NIEK', 'Neuve Eglise', 'Nieuwkerke'), ('LOKR', 'Locre', 'Loker'), ('BAIL', 'Bailleul', 'Bailleul'), ('POPE', 'Poperinghe', 'Poperinge'), ('ELVE', 'Elverdinghe', 'Elverdinge'),
                ('VLAM', 'Vlamertinghe', 'Vlamertinge'), ('GRAV', "'s Graventafel", "'s Graventafel"), ('MOSS', 'Mosselmarkt', 'Mosselmarkt'), ('ZILL', 'Zillebeke', 'Zillebeke')]:
    osm(k, o, m)
est('KRUI', 'Kruiseik (Kruiseecke)', 'Kruiseke', 50.8158, 3.0216, 300, 'OpenStreetMap hamlet node "Kruiseke", read in the browser but not kept in the extract file', 'modern_map')
est('POEZ', 'Poezelhoek', 'Poezelhoek', 50.8404, 3.013, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('LEGH', 'Le Gheer', 'Le Gheer', 50.7315, 2.9121, 300, 'OpenStreetMap hamlet node "Le Gheer - Gheer", read in the browser but not kept in the extract file', 'modern_map')
est('STYV', 'St. Yves', 'Saint-Yvon', 50.7431, 2.8897, 300, 'OpenStreetMap node "St Yvon", read in the browser but not kept in the extract file', 'modern_map')
est('TERH', 'Terhand', 'Terhand', 50.8424, 3.0606, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('WATD', 'Waterdamhoek', 'Waterdam', 50.8749, 3.0649, 400, 'OpenStreetMap hamlet node "Waterdam", read in the browser but not kept in the extract file', 'modern_map')
est('KOEK', 'Koekuit', 'Koekuit', 50.929, 2.920, 700, 'Not found as an OpenStreetMap place node. Placed from memory about 1.7 km north of Langemark on the Houthulst road')
est('KORT', 'Kortekeer Cabaret', 'Kortekeer', 50.914, 2.884, 700, 'Not found as an OpenStreetMap place node. Placed a mile north of Pilkem on the Bixschoote-Langemarck road (S42)')
est('MANG', 'Mangelaere', 'Mangelare', 50.935, 2.908, 900, 'Not found as an OpenStreetMap place node. Placed from memory north-north-west of Langemark')
est('STEE', 'Steenstraat', 'Steenstrate', 50.9166, 2.8477, 300, 'Where the Lizerne-Bixschoote road crosses the Ypres-Yser canal, read from the OpenStreetMap canal line (S39)')
est('HSAS', 'Het Sas', 'Het Sas', 50.903, 2.853, 500, 'The canal lock north of Boezinge; placed on the OpenStreetMap canal line from memory')
est('DRIE', 'Drie Grachten', 'Drie Grachten', 50.946, 2.8268, 400, 'A bend in the OpenStreetMap canal line that matches Drie Grachten; name not confirmed against the map')
est('KNOK', 'Canal mouth on the Yser (Fort Knocke)', 'Knokkebrug', 50.981, 2.8058, 500, 'Northern end of the OpenStreetMap canal line')
est('GXR', 'Gheluvelt cross-roads (Menin road and the Kruiseik-Becelaere road)', '', 50.8272, 3.0152, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('HOOGE', 'Hooge', 'Hooge', 50.8458, 2.9443, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('HERE', 'Herenthage wood, east edge', '', 50.8358, 2.9765, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('HERC', 'Herenthage Chateau', '', 50.8391, 2.9698, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('SHRE', 'Woods north-east of Klein Zillebeke ("Shrewsbury Forest" on the 1925 map)', '', 50.8269, 2.9582, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('KLZ', 'Klein Zillebeke', 'Klein-Zillebeke', 50.8193, 2.9507, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('ZWAR', 'Zwarteleen', 'Zwarteleen', 50.8243, 2.9337, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('H60', 'Hill 60', 'Hill 60', 50.8237, 2.9286, 100, 'OpenStreetMap node "Hill 60 Krater", read in the browser', 'modern_map')
est('VERB', 'Verbranden Molen', 'Verbrandenmolen', 50.8185, 2.9165, 700, 'Not found as an OpenStreetMap place node. Placed from memory south of Zillebeke')
est('CANB', 'Bend of the Ypres-Comines canal north of Hollebeke', '', 50.811, 2.925, 800, 'This stretch of the old canal is not in OpenStreetMap as a waterway; placed from memory')
est('BLUF', 'Canal bank west of the bend (later "the Bluff")', '', 50.8139, 2.9167, 500, 'Placed from memory at the Palingbeek cutting')
est('WAMB', 'Wambeke', 'Wambeke', 50.776, 2.935, 900, 'Not found as an OpenStreetMap place node. Placed from memory between Oosttaverne and Garde Dieu')
est('GARD', 'Garde Dieu', 'Gapaard / Garde-Dieu', 50.7721, 2.9462, 250, 'Read from Sketch A of the British official history (S40), tied to 21 villages on the current map with a typical misfit of about 150 m', 'map_read')
est('DOUV', 'River Douve south-east of Messines', '', 50.752, 2.900, 800, 'The Douve is not in the extract; placed from memory')
est('PWE', 'Polygon Wood, east edge', 'Polygoonbos', 50.853, 2.9952, 300, 'East side of the OpenStreetMap outline box of Polygoonbos (S39). The wood of 1914 was not the same shape')
est('PWSE', 'Polygon Wood, south-east corner', 'Polygoonbos', 50.849, 2.994, 300, 'From the OpenStreetMap outline box of Polygoonbos (S39)')
est('PWS', 'Polygon Wood, south edge', 'Polygoonbos', 50.8485, 2.987, 300, 'From the OpenStreetMap outline box of Polygoonbos (S39)')
est('PWSW', 'Polygon Wood, south-west corner', 'Polygoonbos', 50.8485, 2.9785, 300, 'From the OpenStreetMap outline box of Polygoonbos (S39)')
est('NONB', 'Nonne Bosschen', 'Nonnebossen', 50.8497, 2.9699, 300, 'Centre of the OpenStreetMap outline box of Nonnebossen (S39)')
est('HOUF', 'Houthulst Forest', 'Vrijbos', 50.9614, 2.9592, 1200, 'Centre of the OpenStreetMap outline box of Vrijbos, the remnant of the forest (S39). The forest of 1914 was larger')
est('PSTN', 'Railway station north-west of Poelcappelle', '', 50.921, 2.949, 600, 'Placed from memory; the railway is gone')
for a in [('BECEW', 'BECE', 0, -900, 'Behind (west of) Becelaere'), ('KRUIW', 'KRUI', 300, -1000, 'West of Kruiseik'), ('KRUINE', 'KRUI', 700, 700, 'North-east of Kruiseik'), ('KRUISE', 'KRUI', -1300, 300, 'South-east of Kruiseik, towards Wervicq'),
          ('ZANDNE', 'ZAND', 400, 900, 'North-east of Zandvoorde'), ('ZANDN', 'ZAND', 900, 0, 'North of Zandvoorde'), ('ZANDNW', 'ZAND', 900, -900, 'North-west of Zandvoorde'), ('ZANDW', 'ZAND', 200, -1300, 'West of Zandvoorde'),
          ('GXRE', 'GXR', 0, 600, 'Menin road east of the Gheluvelt cross-roads'), ('GHELE', 'GHEL', -200, 380, 'Menin road about 400 yards east of Gheluvelt'), ('GHELS', 'GHEL', -500, 0, 'South of Gheluvelt'),
          ('GHELNW', 'GHEL', 300, -420, 'Menin road just west of Gheluvelt'), ('GHELSW', 'GHEL', -50, -450, 'South-west edge of Gheluvelt'),
          ('VELDE', 'VELD', -170, 250, 'Menin road in front (east) of Veldhoek'), ('VELDW', 'VELD', -40, -220, 'Menin road just west of Veldhoek'), ('HEREW', 'HERE', 0, -500, 'Herenthage wood, west part'), ('HERES', 'HERE', -500, -550, 'Southern part of Herenthage wood'),
          ('SHREE', 'SHRE', -170, 700, 'East of the woods north-east of Klein Zillebeke'), ('SHREW', 'SHRE', 110, -350, 'West part of the woods north-east of Klein Zillebeke'),
          ('KLZE', 'KLZ', -50, 650, 'East of Klein Zillebeke'), ('ZWARE', 'ZWAR', 0, 400, 'East edge of Zwarteleen'), ('CANBE', 'CANB', -170, 650, 'East of the canal bend, towards Hollebeke'),
          ('CANBS', 'CANB', -400, 200, 'South of the canal bend'), ('CANBSW', 'CANB', -220, -560, 'South-west of the canal bend'), ('HOLLNE', 'HOLL', 320, 820, 'North-east of Hollebeke, on the canal'), ('HOLLW', 'HOLL', -600, -1400, 'West of Hollebeke'),
          ('NBSE', 'NONB', -470, 460, 'South-east of Nonne Bosschen'), ('GUARD', 'PWS', -450, -280, 'Between Polygon Wood and the Menin road'), ('PWSS', 'PWS', -170, 0, 'Just south of Polygon Wood'), ('POLDW', 'POLD', 50, -430, 'West of Polderhoek'), ('POLDE', 'POLD', 0, 350, 'East of Polderhoek'),
          ('REUTW', 'REUT', 0, -500, 'West of Reutel'), ('REUTE', 'REUT', 0, 500, 'East of Reutel'), ('POEZE', 'POEZ', 0, 600, 'East of Poezelhoek'), ('BROOE', 'BROO', 100, 600, 'East of the Broodseinde cross-roads'), ('BROONE', 'BROO', 400, 500, 'North-east of the Broodseinde cross-roads'),
          ('ZONNE', 'ZONN', -900, 900, 'Zonnebeke road east of the village (towards Molenaarelst)'), ('ZONNN', 'ZONN', 800, 200, 'North of Zonnebeke'), ('ZONNNW', 'ZONN', 300, -300, 'Zonnebeke station, north-west of the village'),
          ('GRAVW', 'GRAV', 0, -800, "West of 's Graventafel on the Zonnebeke-Langemarck road"), ('MOSSW', 'MOSS', -700, -1100, 'West of Passchendaele'), ('LANGE', 'LANG', 0, 1600, 'About 1,700 yards east of Langemarck'),
          ('LANGN', 'LANG', 450, 0, 'North edge of Langemarck'), ('LANGW', 'LANG', 100, -700, 'West edge of Langemarck'), ('KOEKS', 'KOEK', -550, -150, 'South of Koekuit'), ('KOEKN', 'KOEK', 500, 100, 'North of Koekuit'),
          ('BIKSSE', 'BIKS', -380, 300, 'South-east edge of Bixschoote'), ('BIKSN', 'BIKS', 700, 0, 'North of Bixschoote'), ('BIKSNE', 'BIKS', 450, 1000, 'North-east of Bixschoote'), ('MANGS', 'MANG', -350, -200, 'South of Mangelaere'),
          ('IIIW', 'BIKS', 100, 900, 'German line east of Bixschoote'), ('IIIC', 'KOEK', -220, -150, 'German line at Koekuit'), ('POELW', 'POEL', 0, -850, 'West of Poelcappelle'), ('POELS', 'POEL', -850, 350, 'South of Poelcappelle'),
          ('STEEW', 'STEE', 0, -260, 'West bank of the canal at Steenstraat'), ('STEEE', 'STEE', 0, 260, 'East bank of the canal at Steenstraat'), ('DRIEW', 'DRIE', 0, -260, 'West bank of the canal at Drie Grachten'), ('DRIEE', 'DRIE', 0, 260, 'East bank of the canal at Drie Grachten'),
          ('KNOKW', 'KNOK', 0, -300, 'West bank at the canal mouth'), ('HSASNE', 'HSAS', 600, 500, 'North-east of Het Sas'), ('PILKN', 'PILK', 470, 0, 'North of Pilckem'), ('NOORE', 'NOOR', 0, 700, 'East of Noordschoote, across the canal'),
          ('STJUN', 'STJU', 1500, 2200, 'Between Poelcappelle and St. Julien'), ('KEIBS', 'KEIB', -500, -300, 'South-west of Keiberg'), ('STADE', 'STAD', 0, 1500, 'East of Staden'),
          ('MESSE', 'MESS', 0, 700, 'East edge of Messines'), ('MESSNE', 'MESS', 750, 800, 'North-east of Messines'), ('MESSE2', 'MESS', 0, 1200, 'East of Messines'), ('MESSN', 'MESS', 1100, -250, 'Ridge north of Messines'),
          ('MESSNW', 'MESS', 500, -600, 'West edge of the ridge at Messines'), ('MESSSW', 'MESS', -600, -350, 'South-west of Messines'), ('WAMBS', 'WAMB', -350, 0, 'South of Wambeke'), ('OOSTE', 'OOST', 0, 950, 'East of Oosttaverne'),
          ('MIDSE', 'STEL', -900, 900, 'Between St. Eloi and Hollebeke'), ('WYTSE', 'WYTS', 0, 400, 'East edge of Wytschaete'), ('WYTSE2', 'WYTS', 0, 950, 'Just east of Wytschaete'), ('WYTSW', 'WYTS', 0, -750, 'West of Wytschaete'),
          ('WYTSS', 'WYTS', -650, -50, 'South of Wytschaete'), ('WYTSNE', 'WYTS', 700, 450, 'North-east of Wytschaete'), ('WULVE', 'WULV', 0, 1150, 'East of Wulverghem'), ('VOORE', 'VOOR', -500, 300, 'East of Voormezeele'),
          ('DOUVE', 'DOUV', 0, 1000, 'The Douve east of the British line'), ('STYVE', 'STYV', 0, 700, 'East of St. Yves'), ('STYVN', 'STYV', 950, 250, 'The Douve north of St. Yves'), ('LEGHE', 'LEGH', 0, 700, 'East of Le Gheer'),
          ('WARNNW', 'WARN', 350, -700, 'North-west of Warneton'), ('WARNW', 'WARN', 0, -1300, 'West of Warneton'), ('PONRW', 'PONR', 0, -900, 'West of Pont Rouge'), ('WARNN', 'WARN', 900, 300, 'North of Warneton'), ('COMIN', 'COMI', 700, -300, 'North of Comines, across the Lys'),
          ('TENBW', 'TENB', 0, -900, 'West of Tenbrielen'), ('WERVN', 'WERV', 900, 0, 'North of Wervicq'), ('DEULN', 'DEUL', 600, -200, 'North of Deulemont'),
          ('STJOS', 'STJO', -900, 500, 'West bank of the Yser south of St. Georges'), ('SCHBW', 'SCHB', -200, -1100, 'West of Schoorbakke'), ('TERVSW', 'TERV', -1200, -200, 'South-west of Tervaete'), ('DIKSN', 'DIKS', 800, -700, 'The Yser north of Dixmude'),
          ('KAASN', 'KAAS', 1100, -600, 'Railway north of Caeskerke'), ('OOSKE', 'KAAS', 1300, -200, 'Railway embankment east of Oostkerke'), ('BEERW', 'BEER', 0, -1500, 'The Yser bank west of Beerst'), ('WOUMW', 'WOUM', -100, -1300, 'West of Woumen'),
          ('WOUMS', 'WOUM', -900, 0, 'South of Woumen'), ('NIEUS', 'NIEU', -1500, -700, 'Behind Nieuport')]:
    off(*a)

D = lambda s: '1914-' + s
SIDE_A, SIDE_G = 'WW1-ALL', 'WW1-GER'
# ---------- units: id, name, label, side, nation, branch, echelon, sources, notes ----------
U = [
 ('Y-BR-BEF', 'British Expeditionary Force', 'BEF', SIDE_A, 'Great Britain', 'Infantry', 'Army', 'S44', 'Headquarters only; no position rows.'),
 ('Y-BR-1C', 'I Corps', 'I Corps', SIDE_A, 'Great Britain', 'Infantry', 'Corps', 'S40', 'No position rows of its own: its divisions are placed.'),
 ('Y-BR-4C', 'IV Corps', 'IV Corps', SIDE_A, 'Great Britain', 'Infantry', 'Corps', 'S40', 'No position rows of its own.'),
 ('Y-BR-CC', 'Cavalry Corps', 'Cav Corps', SIDE_A, 'Great Britain', 'Cavalry', 'Corps', 'S40', 'No position rows of its own.'),
 ('Y-BR-3C', 'III Corps', 'III Corps', SIDE_A, 'Great Britain', 'Infantry', 'Corps', 'S40', 'Only its left division is in the pilot; the 6th Division is south of the map.'),
 ('Y-BR-1D', '1st Division', '1 Div', SIDE_A, 'Great Britain', 'Infantry', 'Division', 'S40; S42; S43', ''),
 ('Y-BR-2D', '2nd Division', '2 Div', SIDE_A, 'Great Britain', 'Infantry', 'Division', 'S40; S42', ''),
 ('Y-BR-7D', '7th Division', '7 Div', SIDE_A, 'Great Britain', 'Infantry', 'Division', 'S40; S42; S46', ''),
 ('Y-BR-3CD', '3rd Cavalry Division', '3 Cav Div', SIDE_A, 'Great Britain', 'Cavalry', 'Division', 'S40; S42', ''),
 ('Y-BR-1CD', '1st Cavalry Division', '1 Cav Div', SIDE_A, 'Great Britain', 'Cavalry', 'Division', 'S40; S42', ''),
 ('Y-BR-2CD', '2nd Cavalry Division', '2 Cav Div', SIDE_A, 'Great Britain', 'Cavalry', 'Division', 'S40; S42', ''),
 ('Y-BR-4D', '4th Division', '4 Div', SIDE_A, 'Great Britain', 'Infantry', 'Division', 'S40', 'Fought the battle of Armentieres; kept here because it held the flank of the Messines sector.'),
 ('Y-BR-3D', '3rd Division (II Corps brigades on the Menin road)', '3 Div', SIDE_A, 'Great Britain', 'Infantry', 'Division', 'S41; S42', 'A mixed force of II Corps brigades. The sources disagree on what to call it: see YC03.'),
 ('Y-BR-BULF', "Bulfin's Force, from 1 November Cavan's", 'Bulfin / Cavan', SIDE_A, 'Great Britain', 'Infantry', 'Brigade', 'S42; S43', 'An improvised group of battalions from several brigades, about a brigade and a half strong. Drawn as a brigade.'),
 ('Y-FR-8A', "French forces in Flanders (d'Urbal's army detachment, later Eighth Army)", 'Fr 8th Army', SIDE_A, 'France', 'Infantry', 'Army', 'S46', 'Headquarters only; no position rows.'),
 ('Y-FR-9C', 'IX Corps', 'IX Corps (Fr)', SIDE_A, 'France', 'Infantry', 'Corps', 'S44; S47', 'No position rows of its own.'),
 ('Y-FR-16C', 'XVI Corps', 'XVI Corps (Fr)', SIDE_A, 'France', 'Infantry', 'Corps', 'S41; S44', 'No position rows of its own.'),
 ('Y-FR-2CC', "de Mitry's cavalry corps", 'de Mitry', SIDE_A, 'France', 'Cavalry', 'Corps', 'S40', ''),
 ('Y-FR-87T', '87th Territorial Division', '87 Terr (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S40; S42; S46', ''),
 ('Y-FR-89T', '89th Territorial Division', '89 Terr (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S40', ''),
 ('Y-FR-17D', '17th Division', '17 Div (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S44; S46; S47', ''),
 ('Y-FR-18D', '18th Division', '18 Div (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S44; S46', ''),
 ('Y-FR-31D', '31st Division', '31 Div (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S44; S46', ''),
 ('Y-FR-32D', '32nd Division', '32 Div (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S45; S46', ''),
 ('Y-FR-MOUS', "Moussy's detachment", 'Moussy (Fr)', SIDE_A, 'France', 'Infantry', 'Brigade', 'S42; S43', 'A detachment of several battalions; size not given in the sources read. Drawn as a brigade.'),
 ('Y-FR-42D', '42nd Division', '42 Div (Fr)', SIDE_A, 'France', 'Infantry', 'Division', 'S40; S44', ''),
 ('Y-FR-FM', 'Naval Brigade (fusiliers marins)', 'Naval Bde (Fr)', SIDE_A, 'France', 'Infantry', 'Brigade', 'S40; S41', ''),
 ('Y-BE-ARMY', 'Belgian Army', 'Belgian Army', SIDE_A, 'Belgium', 'Infantry', 'Army', 'S40; S44', 'Six divisions, drawn as one line. The battle of the Yser is outside the British definition of First Ypres.'),
 ('Y-GE-4A', 'Fourth Army', '4th Army (Ge)', SIDE_G, 'Germany', 'Infantry', 'Army', 'S41', 'Headquarters only; no position rows.'),
 ('Y-GE-6A', 'Sixth Army', '6th Army (Ge)', SIDE_G, 'Germany', 'Infantry', 'Army', 'S41; S44', 'Headquarters only; no position rows.'),
 ('Y-GE-AGF', 'Army Group Fabeck', 'Gp Fabeck', SIDE_G, 'Germany', 'Infantry', 'Army', 'S41', 'An army group formed for the attack of 30 October. No position rows of its own. Echelon set to Army for want of a better code.'),
 ('Y-GE-AGL', 'Army Group Linsingen', 'Gp Linsingen', SIDE_G, 'Germany', 'Infantry', 'Army', 'S41', 'Formed for the attack of 10-11 November. No position rows of its own.'),
 ('Y-GE-PLET', "Plettenberg's Corps", 'Plettenberg', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', 'No position rows of its own.'),
 ('Y-GE-3RC', 'III Reserve Corps', 'III Res', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-22RC', 'XXII Reserve Corps', 'XXII Res', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-23RC', 'XXIII Reserve Corps', 'XXIII Res', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-26RC', 'XXVI Reserve Corps', 'XXVI Res', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-27RC', 'XXVII Reserve Corps', 'XXVII Res', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-HKK', 'Army cavalry (I, II, IV and V Cavalry Corps)', 'Ge cavalry', SIDE_G, 'Germany', 'Cavalry', 'Corps', 'S40; S41', 'Four cavalry corps drawn as one line; the sources read do not separate them day by day.'),
 ('Y-GE-15C', 'XV Corps', 'XV Corps', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-2BC', 'II Bavarian Corps', 'II Bav', SIDE_G, 'Germany', 'Infantry', 'Corps', 'S41', ''),
 ('Y-GE-5RD', '5th Reserve Division', '5 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', 'Only one row: its time on the Yser is covered by the corps row.'),
 ('Y-GE-9RD', '9th Reserve Division', '9 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41', ''),
 ('Y-GE-43RD', '43rd Reserve Division', '43 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-44RD', '44th Reserve Division', '44 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-45RD', '45th Reserve Division', '45 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S40; S41; S46', ''),
 ('Y-GE-46RD', '46th Reserve Division', '46 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S40; S41; S46', ''),
 ('Y-GE-51RD', '51st Reserve Division', '51 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S40; S41; S46', ''),
 ('Y-GE-52RD', '52nd Reserve Division', '52 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S40; S41; S46', ''),
 ('Y-GE-53RD', '53rd (Saxon) Reserve Division', '53 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S40; S41; S46', ''),
 ('Y-GE-54RD', '54th (Wurttemberg) Reserve Division', '54 Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-3CD', '3rd Cavalry Division', '3 Cav (Ge)', SIDE_G, 'Germany', 'Cavalry', 'Division', 'S41; S46', ''),
 ('Y-GE-30D', '30th Division', '30 Div (Ge)', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-39D', '39th Division', '39 Div (Ge)', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41', ''),
 ('Y-GE-26D', '26th (Wurttemberg) Division', '26 Div (Ge)', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41', ''),
 ('Y-GE-6BRD', '6th Bavarian Reserve Division', '6 Bav Res', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41', ''),
 ('Y-GE-3D', '3rd Division', '3 Div (Ge)', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-4D', '4th Division', '4 Div (Ge)', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41; S46', ''),
 ('Y-GE-GD', "Winckler's Guard Division", 'Guard Div', SIDE_G, 'Germany', 'Infantry', 'Division', 'S41', 'A composite division of the Guard Corps.'),
]
GK = 'Commander from general knowledge, not from the sources read: check.'
# ---------- assignments: unit, parent, commander, strength, from, to, sources, notes ----------
A = [
 ('Y-BR-BEF', '', 'Field Marshal Sir John French', '', D('10-18'), D('11-22'), 'S44', ''),
 ('Y-BR-1C', 'Y-BR-BEF', 'Lt. Gen. Sir Douglas Haig', '', D('10-19'), D('11-22'), 'S40', ''),
 ('Y-BR-4C', 'Y-BR-BEF', 'Lt. Gen. Sir Henry Rawlinson', '', D('10-18'), D('10-26'), 'S40', GK + ' End date is when its troops passed to I Corps, also from general knowledge.'),
 ('Y-BR-CC', 'Y-BR-BEF', 'Lt. Gen. Edmund Allenby', '', D('10-18'), D('11-22'), 'S40', ''),
 ('Y-BR-3C', 'Y-BR-BEF', 'Lt. Gen. William Pulteney', '', D('10-18'), D('11-22'), 'S40', GK),
 ('Y-BR-1D', 'Y-BR-1C', 'Maj. Gen. S. H. Lomax', '', D('10-19'), D('10-31'), 'S42', 'Lomax was wounded when his headquarters at Hooge was shelled on 31 October (S42).'),
 ('Y-BR-1D', 'Y-BR-1C', 'Brig. Gen. H. J. S. Landon (acting)', '', D('10-31'), D('11-22'), 'S43', 'S43 speaks of "Landon\'s line" from 31 October. How long he held the command is not in the sources read.'),
 ('Y-BR-2D', 'Y-BR-1C', 'Maj. Gen. C. C. Monro', '', D('10-19'), D('11-22'), 'S40', GK),
 ('Y-BR-7D', 'Y-BR-4C', 'Maj. Gen. Thompson Capper', '', D('10-16'), D('10-26'), 'S46', ''),
 ('Y-BR-7D', 'Y-BR-1C', 'Maj. Gen. Thompson Capper', '', D('10-27'), D('11-05'), 'S46', 'Date of transfer to I Corps from general knowledge.'),
 ('Y-BR-3CD', 'Y-BR-4C', 'Maj. Gen. Julian Byng', '', D('10-16'), D('10-26'), 'S40; S46', ''),
 ('Y-BR-3CD', 'Y-BR-1C', 'Maj. Gen. Julian Byng', '', D('10-27'), D('11-22'), 'S40; S46', 'Parent after 26 October inferred from where it fought.'),
 ('Y-BR-1CD', 'Y-BR-CC', 'Maj. Gen. H. de B. de Lisle', '', D('10-18'), D('11-22'), 'S40; S46', ''),
 ('Y-BR-2CD', 'Y-BR-CC', 'Maj. Gen. Hubert Gough', '', D('10-18'), D('11-22'), 'S40; S46', ''),
 ('Y-BR-4D', 'Y-BR-3C', '', '', D('10-18'), D('11-22'), 'S40', 'Commander not in the sources read.'),
 ('Y-BR-3D', 'Y-BR-1C', '', '', D('11-05'), D('11-20'), 'S41; S42', 'Commander not in the sources read. Under I Corps while on the Menin road (inferred).'),
 ('Y-BR-BULF', 'Y-BR-1C', 'Brig. Gen. E. S. Bulfin', '', D('10-30'), D('11-01'), 'S42; S43', 'Bulfin was wounded on 1 November (S43).'),
 ('Y-BR-BULF', 'Y-BR-1C', 'Brig. Gen. the Earl of Cavan', '', D('11-01'), D('11-20'), 'S43', ''),
 ('Y-FR-8A', '', "Gen. Victor d'Urbal", '', D('10-20'), D('11-22'), 'S46', GK),
 ('Y-FR-9C', 'Y-FR-8A', 'Gen. Pierre Dubois', '', D('10-22'), D('11-22'), 'S44', GK),
 ('Y-FR-16C', 'Y-FR-8A', '', '', D('10-30'), D('11-22'), 'S44', 'Commander not in the sources read.'),
 ('Y-FR-2CC', 'Y-FR-8A', 'Gen. Antoine de Mitry', '', D('10-17'), D('11-22'), 'S40', ''),
 ('Y-FR-87T', 'Y-FR-8A', 'Gen. Roy', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-FR-89T', 'Y-FR-8A', '', '', D('10-14'), D('11-22'), 'S40', 'Commander not in the sources read.'),
 ('Y-FR-17D', 'Y-FR-9C', 'Gen. Guignabaudet', '', D('10-23'), D('11-22'), 'S46', ''),
 ('Y-FR-18D', 'Y-FR-9C', 'Gen. Lefevre', '', D('10-24'), D('11-22'), 'S46', ''),
 ('Y-FR-31D', 'Y-FR-16C', 'Gen. Vidal', '', D('10-25'), D('11-22'), 'S46', 'S43 calls Vidal a commander of "the Ninth French Corps" on 2 November; S46 lists him with the 31st Division. See YG09.'),
 ('Y-FR-32D', 'Y-FR-16C', 'Gen. Bouchez', '', D('10-31'), D('11-22'), 'S46', ''),
 ('Y-FR-MOUS', 'Y-FR-9C', 'Gen. Moussy', '', D('10-31'), D('11-22'), 'S43', 'S43 gives Moussy to "the 16th French Corps". Parent uncertain.'),
 ('Y-FR-42D', 'Y-FR-8A', 'Gen. Paul Grossetti', '', D('10-20'), D('11-22'), 'S40', ''),
 ('Y-FR-FM', 'Y-FR-8A', "Rear Adm. Pierre Ronarc'h", '', D('10-16'), D('11-22'), 'S40', GK),
 ('Y-BE-ARMY', '', 'King Albert I', '', D('10-18'), D('11-22'), 'S44', ''),
 ('Y-GE-4A', '', 'Duke Albrecht of Wurttemberg', '', D('10-10'), D('11-22'), 'S41', 'S41 dates the army\'s part to 10 October to 16 November.'),
 ('Y-GE-6A', '', 'Crown Prince Rupprecht of Bavaria', '', D('10-18'), D('11-22'), 'S44', ''),
 ('Y-GE-AGF', 'Y-GE-6A', 'Gen. Max von Fabeck', '', D('10-27'), D('11-20'), 'S41', ''),
 ('Y-GE-AGL', 'Y-GE-6A', 'Gen. Alexander von Linsingen', '', D('11-08'), D('11-18'), 'S41', ''),
 ('Y-GE-PLET', 'Y-GE-AGL', 'Gen. von Plettenberg', '', D('11-08'), D('11-18'), 'S41', ''),
 ('Y-GE-3RC', 'Y-GE-4A', 'Gen. Hans von Beseler', '5th and 6th Reserve Divisions, 4th Ersatz Division; from 3 November also the 44th and 9th Reserve Divisions', D('10-14'), D('11-17'), 'S41', ''),
 ('Y-GE-22RC', 'Y-GE-4A', 'Gen. Eugen von Falkenhayn', '43rd and 44th Reserve Divisions', D('10-14'), D('11-22'), 'S41', ''),
 ('Y-GE-23RC', 'Y-GE-4A', 'Gen. Georg von Kleist', '45th and 46th Reserve Divisions', D('10-14'), D('11-22'), 'S41', ''),
 ('Y-GE-26RC', 'Y-GE-4A', 'Gen. Otto von Hugel', '51st and 52nd Reserve Divisions', D('10-14'), D('11-22'), 'S41', ''),
 ('Y-GE-27RC', 'Y-GE-4A', 'Gen. Adolph von Carlowitz', '53rd (Saxon) and 54th (Wurttemberg) Reserve Divisions', D('10-14'), D('10-27'), 'S41', ''),
 ('Y-GE-27RC', 'Y-GE-4A', 'Gen. Richard von Schubert', '53rd (Saxon) and 54th (Wurttemberg) Reserve Divisions', D('10-27'), D('11-22'), 'S41', 'S41: Carlowitz was relieved on 27 October.'),
 ('Y-GE-HKK', 'Y-GE-6A', 'Gen. Georg von der Marwitz', '', D('10-19'), D('11-22'), 'S41', 'S41 names Marwitz for the army cavalry on the left of the Fourth Army.'),
 ('Y-GE-15C', 'Y-GE-AGF', 'Gen. Berthold von Deimling', '30th and 39th Divisions', D('10-27'), D('11-08'), 'S41', ''),
 ('Y-GE-15C', 'Y-GE-AGL', 'Gen. Berthold von Deimling', "30th and 39th Divisions; Hofmann's Composite Division from 16 November", D('11-08'), D('11-18'), 'S41', 'The same corps under a second parent: the case the Assignments table exists for.'),
 ('Y-GE-2BC', 'Y-GE-AGF', 'Gen. Karl von Martini', '3rd and 4th Bavarian Divisions', D('10-27'), D('11-05'), 'S41', ''),
 ('Y-GE-2BC', 'Y-GE-AGF', 'Gen. Otto von Stetten', '3rd and 4th Bavarian Divisions', D('11-05'), D('11-20'), 'S41', 'S41: Martini was relieved on 5 November.'),
 ('Y-GE-5RD', 'Y-GE-3RC', 'Lt. Gen. Richard Voigt', '', D('10-14'), D('11-17'), 'S46', ''),
 ('Y-GE-9RD', 'Y-GE-3RC', '', '', D('11-03'), D('11-17'), 'S41', 'Commander not in the sources read.'),
 ('Y-GE-43RD', 'Y-GE-22RC', 'Lt. Gen. Karl Stenger', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-44RD', 'Y-GE-22RC', 'Lt. Gen. Eugen von Dorrer', '', D('10-14'), D('11-02'), 'S46', ''),
 ('Y-GE-44RD', 'Y-GE-3RC', 'Lt. Gen. Eugen von Dorrer', '', D('11-03'), D('11-17'), 'S41; S46', 'S41 lists the division with the III Reserve Corps group from 3 November.'),
 ('Y-GE-45RD', 'Y-GE-23RC', 'Lt. Gen. Albert Schopflin', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-46RD', 'Y-GE-23RC', 'Lt. Gen. Bruno Hahn', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-51RD', 'Y-GE-26RC', 'Lt. Gen. Ferdinand Waenker von Dankenschweil', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-52RD', 'Y-GE-26RC', 'Lt. Gen. Emil Waldorf', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-53RD', 'Y-GE-27RC', 'Lt. Gen. Hans von Watzdorf', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-54RD', 'Y-GE-27RC', 'Lt. Gen. Paul von Schaefer', '', D('10-14'), D('11-22'), 'S46', ''),
 ('Y-GE-3CD', 'Y-GE-HKK', 'Lt. Gen. Kurt von Unger', '', D('10-19'), D('11-22'), 'S46', ''),
 ('Y-GE-30D', 'Y-GE-15C', 'Lt. Gen. Friedrich von Gontard', '', D('10-27'), D('11-18'), 'S46', ''),
 ('Y-GE-39D', 'Y-GE-15C', '', '', D('10-27'), D('11-18'), 'S41', 'Commander not in the sources read.'),
 ('Y-GE-26D', 'Y-GE-AGF', 'Lt. Gen. Wilhelm, Duke of Urach', '', D('10-27'), D('11-20'), 'S41', ''),
 ('Y-GE-6BRD', 'Y-GE-AGF', '', '', D('10-28'), D('11-20'), 'S41', 'Commander not in the sources read.'),
 ('Y-GE-3D', 'Y-GE-AGF', 'Lt. Gen. Ferdinand von Trossel', '', D('11-01'), D('11-20'), 'S41; S46', ''),
 ('Y-GE-4D', 'Y-GE-PLET', 'Lt. Gen. Erich Freyer', '', D('11-09'), D('11-18'), 'S41; S46', ''),
 ('Y-GE-GD', 'Y-GE-PLET', 'Lt. Gen. Arnold von Winckler', '', D('11-09'), D('11-18'), 'S41', ''),
]

P = []
def R(unit, d0, d1, act, place, keys, srcs, say, method, oc, notes='', battle='YPRES1', sl=None, el=None, tb=None):
    """d0/d1 are MM-DD. A row holds from the evening of d0 to the evening of d1."""
    pid = f'Y{len(P)+1:03d}'
    P.append(dict(pos_id=pid, unit_id=unit, battle_id=battle, se=D(d0), sl=D(sl) if sl and sl != 'unknown' else (sl or D(d0)), ee=D(d1), el=D(el) if el and el != 'unknown' else (el or D(d1)),
                  time_basis=tb or 'Dates only. A row runs from the evening of the first date to the evening of the last; the end is the day before the next row for this unit unless a source gives it.',
                  activity=act, place=place, keys=list(keys), source_ids=srcs, say=say, method=method, oc=oc, notes=notes))
    return pid
NB = ''  # no battle: before the battle or outside it
st, inf = 'stated', 'inferred'

# ===== British =====
R('Y-BR-7D', '10-16', '10-17', 'Covering position, entrenching', 'Zandvoorde, Gheluvelt, Zonnebeke', ['ZAND', 'GHEL', 'ZONN'], 'S40', '"on the line Zandvoorde—Gheluvelt—Zonnebeke" (S40 p.107)', st, 'medium', 'Before the battle.', NB)
R('Y-BR-7D', '10-18', '10-18', 'Wheeled forward towards Menin', 'Zandvoorde, Kruiseik, Terhand, Waterdamhoek', ['ZAND', 'KRUI', 'TERH', 'WATD'], 'S40', '"a wheel forward pivoting on its right" (S40 p.115); night position Zandvoorde—Terhand—Waterdamhoek (p.120)', st, 'medium', '', NB)
R('Y-BR-7D', '10-19', '10-20', 'Attack on Menin abandoned; fell back and dug in', 'Zandvoorde, Kruiseik, behind Becelaere, Zonnebeke', ['ZAND', 'KRUI', 'BECEW', 'ZONN'], 'S40', '"passed behind Becelaere to Zonnebeke" (S40 p.134); night 20/21: "Zandvoorde—Kruiseecke—Zonnebeke" (p.148)', st, 'medium', 'The order to abandon the attack came at 1 p.m. on the 19th.')
R('Y-BR-7D', '10-21', '10-24', 'Holding; left drawn back from Zonnebeke', 'Kruiseik, Poezelhoek, Reutel, front of Polygon Wood, Zonnebeke station', ['KRUI', 'POEZ', 'REUT', 'PWE', 'ZONNNW'], 'S40; S44', '"Thence the brigade front ran south-eastwards past the front of Polygon Wood" (S40 p.156)', st, 'medium', 'S44: the division lost Polygon Wood for a time on the 24th.')
R('Y-BR-7D', '10-25', '10-26', 'Holding the Kruiseik salient', 'Menin road at the cross-roads, Kruiseik, towards Zandvoorde', ['GXR', 'KRUI', 'ZANDNE'], 'S42; S44', '"posted in some advance trenches east of the village" (S42, 25 October)', inf, 'low', 'The line is inferred from the brigades named. S44: German attacks of 25-26 October fell on the 7th Division here.')
R('Y-BR-7D', '10-27', '10-28', 'Kruiseik lost; line west of it', 'Menin road at the cross-roads, west of Kruiseik, north of Zandvoorde', ['GXR', 'KRUIW', 'ZANDN'], 'S41; S42', '"driven back from east of Kruiseik to a position west of Kruiseik" (S42)', st, 'low', 'S41 dates the fall of Kruiseik to the 26th.')
R('Y-BR-7D', '10-29', '10-29', 'Driven back on Gheluvelt', 'South of the Menin road at Gheluvelt, to north of Zandvoorde', ['GHELE', 'GHELS', 'ZANDN'], 'S42', '"on the 29th we lost Kruiseik and were driven back to Gheluvelt" (S42)', st, 'low', '', 'YP-GHEL')
R('Y-BR-7D', '10-30', '10-30', 'Right turned back after Zandvoorde fell', 'South of Gheluvelt to the woods north-west of Zandvoorde', ['GHELS', 'ZANDNW'], 'S42', '"was to be held at all costs" (S42: Haig\'s order for the line Gheluvelt to the canal north of Hollebeke)', inf, 'low', 'S42 names the 21st and 22nd Brigades between Gheluvelt and Bulfin\'s Force; the line itself is inferred.', 'YP-GHEL')
R('Y-BR-7D', '10-31', '11-04', 'Holding south of the Menin road', 'Menin road at Veldhoek, Herenthage wood, woods to the south', ['VELDE', 'HERE', 'SHRE'], 'S42; S43', '"the Northamptons on the left, in touch with the R. Welsh Fusiliers in the 7th Division" (S42, night of 2 November)', inf, 'low', 'Three shattered brigades; S42 puts the 20th Brigade in reserve at Hooge Chateau on 2 November.', 'YP-GHEL')
R('Y-BR-7D', '11-05', '11-06', 'Relieved; resting', 'Locre and Bailleul', ['LOKR', 'BAIL'], 'S42; S43', '"The 20th Brigade went back to Locre, and the 22nd to Bailleul" (S42)', st, 'medium', 'The 22nd Brigade was brought back by bus on 6 November for the fight at Zwarteleen (S42). Where the division went next is not in the sources read.', el='unknown')
# 1st Division
R('Y-BR-1D', '10-20', '10-20', 'Marching up', 'Elverdinghe to Poperinghe', ['ELVE', 'POPE'], 'S40', '"the 1st Division marched from Hazebrouck through Poperinghe towards Elverdinghe" (S40 p.146)', st, 'medium', '', NB)
R('Y-BR-1D', '10-21', '10-23', 'Attack halted; holding the north face', 'East of Langemarck, Koekuit, Bixschoote, the canal at Steenstraat', ['LANGE', 'KOEK', 'BIKSSE', 'STEE'], 'S40; S47', '"turned westwards to the canal at Steenstraat" (S40 p.163); the Guards Brigade held "a very extended line, three miles long" from Koekuit to Bixschoote', st, 'medium', 'Kortekeer Cabaret, behind this line, was lost on the 22nd and retaken on the 23rd. French cavalry and Territorials held the canal end.', 'YP-LANG')
R('Y-BR-1D', '10-24', '10-24', 'Relieved by French Territorials; in reserve', 'Ypres', ['IEPE'], 'S42; S47', '"The 1st Division went into reserve at Ypres" (S42)', st, 'medium', '', 'YP-LANG')
R('Y-BR-1D', '10-25', '10-28', 'In line between the 2nd and 7th Divisions', 'West of Reutel, Poezelhoek, Menin road at the cross-roads', ['REUTW', 'POEZ', 'GXR'], 'S42', '"came up on the right of the 2nd Division" (S42)', st, 'low', 'S42: from west of Reutel to the Menin road. S41 says the Germans took Reutel in these days.')
R('Y-BR-1D', '10-29', '10-30', 'Cross-roads lost; line across the Menin road east of Gheluvelt', 'West of Reutel, Polderhoek, Menin road east of Gheluvelt', ['REUTW', 'POLD', 'GHELE'], 'S43; S44', '"The line of the 3rd Brigade had been drawn up across the Menin road" (S43, about 400 yards east of Gheluvelt)', st, 'low', '', 'YP-GHEL')
R('Y-BR-1D', '10-31', '11-10', 'New line in front of Veldhoek after Gheluvelt fell', 'South-west corner of Polygon Wood to the Menin road east of Veldhoek', ['PWSW', 'VELDE'], 'S43', '"about four hundred yards in advance of Veldhoek" (S43)', st, 'low', 'Gheluvelt was retaken by the 2nd Worcestershire in the afternoon of the 31st, then given up when the line was straightened. Polderhoek Chateau was lost on 1 November (S41).', 'YP-GHEL')
R('Y-BR-1D', '11-11', '11-15', "Line broken by the Guard and restored a little further back", 'South-west corner of Polygon Wood, east of Nonne Bosschen, Menin road west of Veldhoek', ['PWSW', 'NBSE', 'VELDW'], 'S42; S43', '"capturing all the front line trenches of the 1st Brigade" (S42)', inf, 'low', 'How far back the new line lay is not in the sources read; drawn about 300 m behind the old one.', 'YP-NONNE')
R('Y-BR-1D', '11-16', '11-21', 'Relieved by the French', 'Not given in the sources read', [], 'S44', '"I Corps was relieved by the French IX Corps and XVI Corps" (S44, for 15 to 22 November)', st, 'low', 'No position: the day of relief and the rest area are not in the sources read.', sl='11-17')
# 2nd Division
R('Y-BR-2D', '10-20', '10-20', 'Outposts north-east of Ypres', 'Wieltje, Pilckem, Steenstraat', ['WIEL', 'PILK', 'STEE'], 'S40', '"on the line Wieltje—Pilckem—Steenstraat" (S40 p.146)', st, 'medium', '', NB)
R('Y-BR-2D', '10-21', '10-23', 'Advance halted; entrenched', "Zonnebeke station, north-north-west to a point east of Langemarck", ['ZONNNW', 'GRAVW', 'LANGE'], 'S40', '"from Zonnebeke Station N.N.W." to a point 1,700 yards east of Langemarck (S40 p.163)', st, 'medium', '', 'YP-LANG')
R('Y-BR-2D', '10-24', '11-15', 'Holding Polygon Wood and the Zonnebeke road', 'Zonnebeke road east of the village, east and south edges of Polygon Wood', ['ZONNE', 'PWE', 'PWSE', 'PWS'], 'S42; S44', '"For twenty-two consecutive days from the date of the advance they occupied the Polygon wood trenches" (S42)', st, 'low', 'The 6th Brigade pushed forward to the Passchendaele-Becelaere road on 24 and 27 October (S42). On 11 November the 1st King\'s held the south edge of the wood (S42; S43). Relief date: see YC02.', sl='10-24')
P[-1]['se'] = D('10-23')
R('Y-BR-2D', '11-16', '11-21', 'Relieved by the French', 'Not given in the sources read', [], 'S44', '"I Corps was relieved by the French IX Corps and XVI Corps" (S44, for 15 to 22 November)', st, 'low', 'No position.', sl='11-17')
# 3rd Cavalry Division
R('Y-BR-3CD', '10-16', '10-18', 'Screening the left of the 7th Division', 'Passchendaele and Poelcappelle', ['PASS', 'POEL'], 'S40', '"near Poelcappelle" (S40 p.105, 16 October); "near Passchendaele" (p.107, 17 October)', st, 'medium', '', NB)
R('Y-BR-3CD', '10-19', '10-19', 'Took Ledeghem, then fell back', 'Passchendaele and Poelcappelle', ['PASS', 'POEL'], 'S40', '"withdraw the 6th Cavalry Brigade from Moorslede to Passchendaele" (S40 p.134)', st, 'medium', 'The 6th Cavalry Brigade took Ledeghem about 10.30 a.m.')
R('Y-BR-3CD', '10-20', '10-20', 'Holding until I Corps came up', 'Zonnebeke, St. Julien, Langemarck', ['ZONN', 'STJU', 'LANG'], 'S40', 'Night 20/21: "Zonnebeke—St. Julien—Langemarck" (S40 p.148)', st, 'medium', '')
R('Y-BR-3CD', '10-21', '10-29', 'In the Zandvoorde trenches', 'Zandvoorde to the canal north of Hollebeke', ['ZAND', 'HOLLNE'], 'S40; S42', '"the 3rd Cavalry Division took over the right of the 7th Division line near Zandvoorde" (S40 p.157)', st, 'medium', 'The 6th Cavalry Brigade held the two canal crossings north of Hollebeke (S42).')
R('Y-BR-3CD', '10-30', '10-30', 'Driven off the Zandvoorde ridge', 'Klein Zillebeke', ['KLZ'], 'S42; S43', '"reformed at Klein Zillebeke in the rear" (S43)', st, 'medium', 'The trenches were lost soon after nine in the morning (S42).', 'YP-GHEL')
R('Y-BR-3CD', '10-31', '11-05', 'Corps reserve, sent wherever the line gave', 'Verbranden Molen', ['VERB'], 'S42; S41', '"kept at Verbranden Molen ready for emergencies" (S42, 31 October)', st, 'low', 'One brigade or another was in the line most days. S41 puts the division in Herenthage wood on 1 November.')
R('Y-BR-3CD', '11-06', '11-17', 'Counter-attack at Zwarteleen; then holding the ridge', 'Zwarteleen and the ridge west of Klein Zillebeke', ['ZWARE', 'SHREW'], 'S42; S43', '"regained, at the point of the bayonet, the whole of the position lost" (S42, 6 November)', st, 'low', 'Shares this ground with Cavan\'s Force; the sources do not separate them. S43: the division repelled the attack of 17 November.')
# 1st and 2nd Cavalry Divisions
R('Y-BR-1CD', '10-18', '10-19', 'Probing the Lys crossings', 'West of Pont Rouge and Warneton', ['PONRW', 'WARNW'], 'S40; S45', '"to within three hundred yards of Pont Rouge" (S40 p.115, 2nd Cavalry Brigade)', inf, 'low', 'The split between the two cavalry divisions on these days is inferred.', 'MESS14')
R('Y-BR-1CD', '10-20', '10-20', 'Holding the line facing Warneton', 'St. Yves to Messines', ['STYV', 'MESSE'], 'S40', '"on the general line St. Yves—Messines" (S40 p.144, 6 p.m.)', st, 'medium', '', 'MESS14')
R('Y-BR-1CD', '10-21', '10-30', 'Holding Messines', 'The Douve to Messines', ['DOUV', 'MESSE'], 'S40; S42', '"part of its front up to the Douve" was taken over by the 4th Division (S40 p.153)', st, 'medium', '', 'MESS14')
R('Y-BR-1CD', '10-31', '10-31', 'Fighting in Messines', 'Messines', ['MESS'], 'S42; S41', '"by 2 p.m. they were all in the town" (S42)', st, 'medium', '', 'MESS14')
R('Y-BR-1CD', '11-01', '11-02', 'Messines lost; withdrawn behind the French', 'Wulverghem', ['WULV'], 'S42', '"withdrawn to Wulverghem" (S42)', st, 'low', 'S42 does not date the withdrawal; "early November". Not followed after this.', 'MESS14', el='unknown')
R('Y-BR-2CD', '10-18', '10-19', 'Attack across the Lys made no progress', 'North-west of Warneton, Houthem, west of Tenbrielen', ['WARNNW', 'HOUT', 'TENBW'], 'S45', '"attacked from Deûlémont to Tenbrielen but made no progress" (S45, citing Edmonds)', inf, 'low', 'The split between the two cavalry divisions on these days is inferred.', 'MESS14')
R('Y-BR-2CD', '10-20', '10-20', 'Holding from Garde Dieu to Kortewilde', 'Garde Dieu, the Wambeke, Houthem, Kortewilde', ['GARD', 'WAMB', 'HOUT', 'KORW'], 'S40', '"through Garde Dieu along the Wambeke stream to Houthem and Kortewilde" (S40 p.144)', st, 'medium', '', 'MESS14')
R('Y-BR-2CD', '10-21', '10-29', 'Kortewilde lost; holding from Messines to the canal', 'North-east of Messines, east of Oosttaverne, Hollebeke', ['MESSNE', 'OOSTE', 'HOLL'], 'S40; S42', '"Kortewilde was occupied by the enemy" (S40 p.153)', st, 'low', 'S42 gives the cavalry line on 30 October as from the canal at Hollebeke to the Douve south of Messines.', 'MESS14')
R('Y-BR-2CD', '10-30', '10-31', 'Hollebeke lost; holding St. Eloi and Wytschaete', 'Canal bend, between St. Eloi and Hollebeke, east of Wytschaete', ['CANB', 'MIDSE', 'WYTSE'], 'S41; S44', '"pushed out of Zandvoorde, Hollebeke and Hollebeke Château" (S44, citing Edmonds)', inf, 'low', 'Wytschaete fell in the night of 31 October to 1 November (S42).', 'MESS14')
R('Y-BR-2CD', '11-01', '11-02', 'In reserve', 'Bailleul', ['BAIL'], 'S42', '"went into reserve at Bailleul" (S42)', st, 'low', 'Undated in S42 ("early November"). Not followed after this.', 'MESS14', el='unknown')
# 4th Division
R('Y-BR-4D', '10-18', '10-20', 'Holding the left of III Corps', 'Le Gheer to Le Touquet on the Lys', ['LEGH', 'LETQ'], 'S40', '"northward to Le Gheer in front of Ploegsteert Wood" (S40 p.107)', st, 'medium', 'Part of the battle of Armentieres, which is not in the pilot.', NB)
R('Y-BR-4D', '10-21', '11-22', 'Line extended to the Douve', 'The Douve, St. Yves, Le Gheer, Le Touquet', ['STYVN', 'STYV', 'LEGH', 'LETQ'], 'S40; S43', '"the 12th Brigade taking over from the Lys at Frelinghien to the Warnave stream" (S40 p.151)', st, 'low', 'Not followed day by day after 22 October; S43 has it still at Ploegsteert on 9 November. The end date is the end of the battle, not a source date.', NB)
# Bulfin / Cavan
R('Y-BR-BULF', '10-30', '10-31', 'Filled the gap after Zandvoorde fell', 'Woods north-east of Klein Zillebeke, Klein Zillebeke, the canal bend', ['SHRE', 'KLZ', 'CANB'], 'S42; S43', '"the cavalry position from Klein Zillebeke to the canal had just been taken over by Lord Cavan" (S42, night of the 30th)', st, 'low', '', 'YP-GHEL')
R('Y-BR-BULF', '11-01', '11-05', 'Holding, with the French on the right', 'Woods north-east of Klein Zillebeke to Klein Zillebeke', ['SHRE', 'KLZ'], 'S42; S43', '"Lord Cavan, of the 4th Brigade, took over the command" (S43, 1 November)', st, 'low', 'On 2 November the Germans broke into the woods behind and were cleared out by the 2nd Grenadiers (S42).')
R('Y-BR-BULF', '11-06', '11-20', 'French gave way on the right; line restored west of Klein Zillebeke', 'Woods north-east of Klein Zillebeke to Zwarteleen', ['SHRE', 'ZWARE'], 'S42; S43', '"The French troops ... now found the position more than they could support" (S42, 6 November)', inf, 'low', 'End date inferred: the 2nd Grenadiers went into reserve on 18 November (S42).', el='unknown')
P[-1]['ee'] = D('11-18')
# 3rd Division
R('Y-BR-3D', '11-06', '11-10', 'Took over from the 7th Division south of the Menin road', 'Menin road at Veldhoek, Herenthage wood, woods to the south', ['VELDE', 'HERE', 'SHRE'], 'S41; S42; S43', '"a sharp attack on the 3rd Division, which had now taken over the line south of the Menin road" (S41, British editors\' note 93, 7 November)', st, 'low', 'S42 names the 7th and 15th Brigades. S43 says the 5th Division: see YC03.', sl='11-07')
P[-1]['se'] = D('11-05')
R('Y-BR-3D', '11-11', '11-20', 'Pressed back in Herenthage wood', 'Menin road west of Veldhoek, west part of Herenthage wood, woods to the south', ['VELDW', 'HEREW', 'SHREW'], 'S41', '"the Herenthage Château fell for the time into German hands" (S41, British editors\' note 112, 14 November)', inf, 'low', 'The line is inferred. Attacks of 13, 14 and 17 November were beaten off (S41 notes). See YC06.', 'YP-NONNE', el='unknown')
# ===== French and Belgian =====
R('Y-FR-2CC', '10-18', '10-18', 'Pushed out to Roulers', 'Roulers and Hooglede', ['ROES', 'HOOG'], 'S40', '"occupied Roulers and Hooglede" (S40 p.116)', st, 'medium', '', NB)
R('Y-FR-2CC', '10-19', '10-19', 'Driven back; night outposts', 'Passchendaele, Westroosebeke, Houthulst, Zarren', ['PASS', 'WROZ', 'HOUL', 'ZARR'], 'S40', 'Paraphrase: night outposts on the line Passchendaele, Westroosebeke, Houthulst, Zarren (S40 p.133)', st, 'medium', '')
R('Y-FR-2CC', '10-20', '10-20', 'Forced back behind Houthulst Forest', 'Koekuit, Mangelaere, Merckem', ['KOEK', 'MANG', 'MERK'], 'S40', '"forced to retire behind Houthulst Forest" (S40 p.145)', st, 'low', 'S40 names Langemarck and Koekuit; the western end is inferred.')
R('Y-FR-2CC', '10-21', '10-23', 'Withdrew behind the canal', 'West bank of the canal, Steenstraat to the Yser', ['STEEW', 'DRIEW', 'KNOKW'], 'S40; S44', '"the French cavalry corps received orders to withdraw west of the canal" (S40 p.161, about 2 p.m. on the 21st)', st, 'low', 'S44: dug in from Steenstraat to Dixmude by nightfall. Not followed after this.', el='unknown')
R('Y-FR-87T', '10-14', '10-19', 'In and behind Ypres', 'Between Poperinghe and Ypres', ['VLAM'], 'S40', 'Paraphrase: the two Territorial divisions were between Poperinghe and Ypres on 15 October (S40 p.103)', st, 'low', '', NB)
R('Y-FR-87T', '10-20', '10-23', 'Holding Bixschoote and the canal', 'Bixschoote to Steenstraat', ['BIKSSE', 'STEE'], 'S40', '"Bixschoote and along the canal towards Dixmude" (S40 p.148, both Territorial divisions)', st, 'low', 'A brigade attacked towards Merckem on the 22nd and was driven back (S40 p.174). The split between the two divisions is inferred.', 'YP-LANG')
R('Y-FR-87T', '10-24', '10-28', 'Relieved the British 1st Division', 'Bixschoote, Koekuit, east of Langemarck', ['BIKSSE', 'KOEKS', 'LANGE'], 'S42; S47', '"a Division of the 87th Territorials relieving the 1st Division between Bixschoote and Langemarck" (S42)', st, 'low', 'When the Territorials were themselves relieved is not in the sources read.', el='unknown')
R('Y-FR-89T', '10-20', '10-23', 'Holding the canal', 'West bank of the canal north of Steenstraat', ['STEEW', 'DRIEW', 'NOOR'], 'S40', '"Bixschoote and along the canal towards Dixmude" (S40 p.148, both Territorial divisions)', inf, 'low', 'Not followed after this.', 'YP-LANG', el='unknown')
R('Y-FR-17D', '10-24', '11-22', 'Took over from the British 2nd Division', "East of Langemarck, west of 's Graventafel, north of Zonnebeke", ['LANGE', 'GRAVW', 'ZONNN'], 'S42; S44; S47', 'Paraphrase: a French division replaced the British 2nd Division on its front (S47); S42 gives the stretch as Langemarck to Zonnebeke', st, 'low', 'Its counter-attack through the British line on the 23rd failed (S47). Attacked towards Passchendaele on 24-25 October (S44). Not followed day by day; see YG02 and YC02.', sl='10-24')
P[-1]['se'] = D('10-23')
R('Y-FR-18D', '10-29', '11-09', 'In the Langemarck sector', 'Kortekeer, Koekuit, east of Langemarck', ['KORT', 'KOEKS', 'LANGE'], 'S44', '"recaptured Bixschoote and Kortekeer Cabaret" (S44, of the 17th, 18th and 31st Divisions on 29 October)', inf, 'low', 'S44 puts the division in this fighting but gives no sector. The line is inferred.')
R('Y-FR-18D', '11-10', '11-22', 'Line drawn back towards Pilckem', 'Het Sas, north of Pilckem, Langemarck', ['HSAS', 'PILKN', 'LANGN', 'LANGE'], 'S41', '"the 44th Reserve Division pushed forward till close up to HET SAS" (S41, 10 November)', inf, 'low', 'The formation holding this stretch after 10 November is not named in the sources read. Langemarck itself was still held.')
R('Y-FR-31D', '10-29', '11-09', 'Retook Bixschoote and Kortekeer Cabaret', 'Steenstraat to Bixschoote', ['STEE', 'BIKSSE'], 'S44; S41', '"recaptured Bixschoote and Kortekeer Cabaret" (S44, 29 October)', inf, 'low', 'The Germans stormed Bixschoote again on 30 October and gained ground on 5 November (S41). Part of the division fought on the Menin road under Vidal on 2 November (S43): see YG09.')
R('Y-FR-31D', '11-10', '11-22', 'Driven back to the canal', 'West bank of the canal, Drie Grachten to Het Sas', ['DRIEW', 'STEEW', 'HSAS'], 'S41', '"by evening the canal had been reached along almost its whole length" (S41, 10 November)', inf, 'low', 'The formation holding the canal is not named in the sources read.')
R('Y-FR-32D', '11-01', '11-09', 'Holding the ridge west of Wytschaete and Messines', 'St. Eloi, west of Wytschaete, east of Wulverghem', ['STEL', 'WYTSW', 'WULVE'], 'S44; S45', '"the ridges to the west of the Wytschaete–Messines line were held by the French 32nd Division" (S45)', st, 'low', 'S41: six regiments of the XVI Corps counter-attacked at Wytschaete in the night of 31 October. See YC04.', 'MESS14')
P[-1]['se'] = D('10-31')
R('Y-FR-32D', '11-10', '11-22', 'St. Eloi lost', 'East of Voormezeele, west of Wytschaete, east of Wulverghem', ['VOORE', 'WYTSW', 'WULVE'], 'S41', '"took the high ground on which ST. ELOI is situated" (S41, of the Bavarians, 9-10 November)', inf, 'low', 'Which French troops held St. Eloi is not in the sources read.')
R('Y-FR-MOUS', '11-01', '11-06', 'Between the British right and the canal', 'Klein Zillebeke to the canal bend', ['KLZ', 'CANB'], 'S42; S43', '"French Territorials between them and the canal at Hollebeke" (S42); "Moussy\'s regiments to the north of the canal" (S43)', st, 'low', 'Driven out on 6 November (S41; S42).')
R('Y-FR-MOUS', '11-07', '11-22', 'Reformed on the right of the British', 'Hill 60 to the canal bank', ['H60', 'BLUF'], 'S42', '"some 300 of the French ... had reformed, on his right" (S42, 6 November)', inf, 'low', 'S41 claims Hill 60 for the XV Corps on 11 November: see YC05.', el='unknown')
R('Y-FR-42D', '10-20', '10-23', 'Detraining', 'Behind Nieuport', ['NIEUS'], 'S40', '"began detraining and concentrating near Nieuport" (S40 p.147)', st, 'medium', '', 'YSER')
R('Y-FR-42D', '10-24', '11-01', 'Sent to the centre of the Yser line', 'Pervyse', ['PERV'], 'S44', '"The French sent the rest of the 42nd Division to the centre" (S44)', st, 'low', 'Place inferred from "the centre". Not followed after the floods.', 'YSER', el='unknown')
R('Y-FR-FM', '10-16', '11-09', 'Holding the Dixmude bridgehead', 'Dixmude', ['DIKS'], 'S40; S41', 'Paraphrase: the Naval Brigade and Belgian troops held the Dixmude bridgehead (S40 p.117)', st, 'medium', 'Attacked on 16, 19, 20 and 25 October.', 'YSER')
R('Y-FR-FM', '11-10', '11-22', 'Driven across the Yser', 'Caeskerke', ['KAAS'], 'S41', '"DIXMUDE was captured, and the French had been driven back across the canal" (S41)', st, 'low', 'Place inferred: the west bank opposite Dixmude.', 'YSER')
R('Y-BE-ARMY', '10-18', '10-23', 'Holding the Yser', 'Nieuport, St. Georges, Schoorbakke, Tervaete, north of Dixmude', ['NIEU', 'STJO', 'SCHB', 'TERV', 'DIKSN'], 'S40; S41', 'Paraphrase: the Belgian divisions held the river from the sea to Dixmude (S40 p.117)', st, 'medium', 'The outposts east of the river (Keyem, Schoore) fell on the 18th. The Germans crossed at Tervaete on 22-24 October.', 'YSER')
R('Y-BE-ARMY', '10-24', '11-22', 'On the railway embankment behind the floods', 'Nieuport, Ramscappelle, Pervyse, north of Caeskerke', ['NIEU', 'RAMS', 'PERV', 'KAASN'], 'S41; S44', '"the railway embankment on the line RAMSCAPPELLE-PERVYSE" (S41)', st, 'medium', 'The army fell back from the river to the railway between 24 and 26 October; the row starts on the first of those days. The sluices were opened at the end of October and the ground between river and railway flooded.', 'YSER')
# ===== German: Fourth Army =====
R('Y-GE-3RC', '10-18', '10-23', 'Attacking the Yser line', 'Westende, Mannekensvere, Schoore, Keyem', ['WEST', 'MANN', 'SCHO', 'KEIE'], 'S41; S40', '"It captured LEKE, and KEYEM, defended by the 4th Belgian Division" (S41, 6th Reserve Division, 18 October)', st, 'medium', '', 'YSER')
R('Y-GE-3RC', '10-24', '10-30', 'Across the Yser', 'West bank from St. Georges to Tervaete', ['STJOS', 'SCHBW', 'STUI', 'TERVSW'], 'S41', '"five battalions of the 44th Reserve Division succeeded in crossing the YSER" (S41, 24 October)', st, 'low', 'On 30 October parts reached the railway at Ramscappelle and Pervyse (S41).', 'YSER')
R('Y-GE-3RC', '10-31', '10-31', 'Withdrew behind the Yser as the floods rose', 'Mannekensvere, Schoore, Keyem', ['MANN', 'SCHO', 'KEIE'], 'S41', 'Paraphrase: the troops west of the river were withdrawn in the night of 30-31 October because of the flooding (S41)', st, 'low', '', 'YSER')
R('Y-GE-3RC', '11-01', '11-02', 'Moved south as reserve', 'Zarren to Staden', ['ZARR', 'STAD'], 'S41', '"the III Reserve Corps was moved southwards to the district ZARREN-STADEN" (S41)', st, 'medium', '')
R('Y-GE-3RC', '11-03', '11-17', 'Main attack either side of Langemarck', 'East of Bixschoote, Koekuit, west of Poelcappelle', ['IIIW', 'IIIC', 'POELW'], 'S41; S44', '"on both sides of LANGEMARCK, facing the front HET SAS-ST. JULIEN" (S41)', st, 'low', 'Ordered away on 17 November (S44).')
R('Y-GE-22RC', '10-18', '10-19', 'Marching up', 'Thourout', ['TORH'], 'S41', '"The XXII Reserve Corps to the line AERTRYCKE-THOUROUT" (S41, order for the 18th)', st, 'medium', 'On the 19th it "advanced on BEERST and DIXMUDE" (S41).', 'YSER')
R('Y-GE-22RC', '10-20', '11-09', 'Closing round Dixmude', 'Beerst, Eessen, Woumen', ['BEER', 'ESEN', 'WOUM'], 'S41; S40', '"closed in round Dixmude" (S40 p.170, from the German account)', st, 'medium', 'From 3 November the corps guarded the whole front from Dixmude to the coast (S41); that stretch is not drawn.', 'YSER')
R('Y-GE-22RC', '11-10', '11-22', 'Dixmude taken', 'The Yser west of Beerst, Dixmude, west of Woumen', ['BEERW', 'DIKS', 'WOUMW'], 'S41', '"DIXMUDE was captured, and the French had been driven back across the canal" (S41)', st, 'medium', '', 'YSER')
R('Y-GE-43RD', '10-20', '10-20', 'Took Vladsloo and Eessen', 'Vladsloo', ['VLAD'], 'S41', 'Paraphrase: the 43rd Reserve Division took Vladsloo and occupied Eessen (S41)', st, 'medium', '', 'YSER')
R('Y-GE-43RD', '10-21', '11-09', 'South of Dixmude', 'Woumen', ['WOUM'], 'S41', '"had taken the château south of DIXMUDE, and WOUMEN" (S41)', st, 'medium', 'Assaulted Dixmude on 25 October. Part of the division crossed the Yser on 30 October and came back.', 'YSER')
R('Y-GE-43RD', '11-10', '11-22', 'In Dixmude', 'Dixmude', ['DIKS'], 'S41', '"DIXMUDE was captured, and the French had been driven back across the canal" (S41)', st, 'medium', '', 'YSER')
R('Y-GE-44RD', '10-20', '10-28', 'North of Dixmude', 'Beerst', ['BEER'], 'S41', '"captured BEERST and reached the canal bank west of KASTEELHOEK" (S41)', st, 'medium', '', 'YSER')
R('Y-GE-44RD', '10-29', '10-30', 'Across the Yser', 'Railway embankment east of Oostkerke', ['OOSKE'], 'S41', '"the 44th Reserve Division was in full advance towards the railway embankment east of OOSTKERKE" (S41)', st, 'low', 'Where it was from 31 October to 9 November is not in the sources read.', 'YSER')
R('Y-GE-44RD', '11-10', '11-17', 'Close up to Het Sas', 'North-east of Het Sas', ['HSASNE'], 'S41', '"the 44th Reserve Division pushed forward till close up to HET SAS" (S41)', st, 'low', '')
R('Y-GE-23RC', '10-18', '10-18', 'Marching up', 'Lichtervelde to Ardoye', ['LICH', 'ARDO'], 'S41', '"The XXIII Reserve Corps to the line LICHTERVELDE-ARDOYE" (S41, order for the 18th)', st, 'medium', '', NB)
R('Y-GE-23RC', '10-19', '10-19', 'Driving in the French cavalry', 'Handzaeme, Gits, east of Staden', ['HAND', 'GITS', 'STADE'], 'S41', '"took HANDZAEME after severe street fighting" (S41)', st, 'medium', '')
R('Y-GE-23RC', '10-20', '10-20', 'Up to Houthulst Forest', 'Clercken to the east edge of Houthulst Forest', ['KLER', 'HOUF'], 'S41', '"a line from CLERCKEN to the eastern edge of HOUTHULST Forest" (S41)', st, 'medium', '')
R('Y-GE-23RC', '10-21', '11-02', 'On the canal and before Bixschoote', 'Luyghem, Merckem, north of Bixschoote, Mangelaere', ['LUIG', 'MERK', 'BIKSN', 'MANG'], 'S41', '"stormed the strongly entrenched village of MERCKEM" (S41, 21 October)', st, 'low', 'Entered Bixschoote on 22 October and lost it in the night; stormed it again on 30 October and fell back to its north edge (S41).')
R('Y-GE-23RC', '11-03', '11-09', 'Attack sector narrowed', 'East of Noordschoote to north of Bixschoote', ['NOORE', 'BIKSN'], 'S41', '"the XXIII Reserve Corps in the sector NOORDSCHOOTE-BIXSCHOOTE" (S41)', st, 'medium', '')
R('Y-GE-23RC', '11-10', '11-22', 'On the canal', 'East bank of the canal, Drie Grachten to Steenstraat', ['DRIEE', 'STEEE'], 'S41', '"by evening the canal had been reached along almost its whole length" (S41)', st, 'low', 'Lost and retook ground south-west of Bixschoote on 14 November (S41).')
R('Y-GE-45RD', '10-19', '10-19', 'Took Handzaeme', 'Handzaeme', ['HAND'], 'S41; S40', '"the 45th Reserve Division reached Handzaeme" (S40 p.168)', st, 'medium', '')
R('Y-GE-45RD', '10-21', '11-09', 'On the right, towards the canal', 'South of Woumen to Luyghem', ['WOUMS', 'LUIG'], 'S40', '"extending to Woumen (two miles south of Dixmude)" (S40 p.170)', st, 'low', 'Where it was on the 20th is not in the sources read.')
R('Y-GE-45RD', '11-10', '11-22', 'Reached the canal', 'East bank of the canal at Drie Grachten', ['DRIEE'], 'S41', '"by evening the canal had been reached along almost its whole length" (S41, naming the 45th Reserve Division)', st, 'low', '')
R('Y-GE-46RD', '10-19', '10-19', 'Reached Staden', 'Staden', ['STAD'], 'S40; S41', '"the 46th, Staden" (S40 p.168)', st, 'medium', 'S41 has the division only "close to" Staden on the 19th and taking it on the 20th.')
R('Y-GE-46RD', '10-20', '10-21', 'Cleared Houthulst Forest', 'Houthulst Forest', ['HOUF'], 'S41', '"had completely driven the enemy out of HOUTHULST Forest" (S41, 21 October)', st, 'medium', '')
R('Y-GE-46RD', '10-22', '11-02', 'Against the Bixschoote-Langemarck line', 'North-east of Bixschoote, Mangelaere, north of Koekuit', ['BIKSNE', 'MANGS', 'KOEKN'], 'S41', '"against the line BIXSCHOOTE-LANGEMARCK" (S41)', st, 'low', 'Broke in at Kortekeer Cabaret on the 22nd. Not followed after 2 November.', 'YP-LANG', el='unknown')
R('Y-GE-26RC', '10-19', '10-19', 'Took Roulers', 'Roulers to Moorslede', ['ROES', 'MOOR'], 'S41', '"ROULERS was taken by the 233rd, 234th and 235th Reserve Infantry Regiments" (S41)', st, 'medium', '')
R('Y-GE-26RC', '10-20', '11-22', 'Facing Langemarck and Zonnebeke', 'Station north-west of Poelcappelle, Poelcappelle, west of Passchendaele, cross-roads east of Zonnebeke', ['PSTN', 'POELS', 'MOSSW', 'BROONE'], 'S41', '"POELKAPPELLE, PASSCHENDAELE and east of ZONNEBEKE" (S41, 25-27 October)', st, 'low', 'Attacked Langemarck on 22 and 30 October without taking it. The line hardly moved in a month; it is not followed day by day.')
R('Y-GE-51RD', '10-19', '10-19', 'Took Roulers', 'Roulers', ['ROES'], 'S40', '"captured Roulers from the French" (S40 p.168)', st, 'medium', '')
R('Y-GE-51RD', '10-20', '11-22', 'At Poelcappelle', 'Station north-west of Poelcappelle to Poelcappelle', ['PSTN', 'POEL'], 'S41; S40', '"reached a line from the railway-station north-west of POELCAPPELLE" (S41)', st, 'low', 'Took Westroosebeke on the way on the 20th. Not followed after October.', el='unknown')
R('Y-GE-52RD', '10-19', '10-19', 'Reached Moorslede', 'Moorslede', ['MOOR'], 'S41', '"the 52nd Reserve Division reached MORSLEDE, its objective for the day" (S41)', st, 'medium', '')
R('Y-GE-52RD', '10-20', '11-22', 'On the Passchendaele ridge', 'Passchendaele to Keiberg', ['PASS', 'KEIB'], 'S41', '"had taken PASSCHENDAELE, KEIBERG and the high ground between them" (S41)', st, 'low', 'Not followed after October.', el='unknown')
R('Y-GE-27RC', '10-19', '10-19', 'First contact with British cavalry', 'Rolleghem-Cappelle', ['ROLK'], 'S41', '"the XXVII Reserve Corps had come into contact with the 3rd British Cavalry Division" (S41)', st, 'medium', '')
R('Y-GE-27RC', '10-20', '10-23', 'Took Becelaere', 'Keiberg, Becelaere, Terhand', ['KEIBS', 'BECE', 'TERH'], 'S41; S40', '"had succeeded in driving the 7th British Division out of BECELAERE" (S41)', st, 'medium', 'Attacked between Gheluvelt and Keiberg on the 21st (S40 p.170).')
R('Y-GE-27RC', '10-24', '10-30', 'Held on the Reutel line', 'East of the Broodseinde cross-roads, Reutel, Poezelhoek', ['BROOE', 'REUTE', 'POEZE'], 'S41; S44', '"from the cross-roads east of ZONNEBEKE through REUTEL to POEZELHOEK" (S41)', st, 'low', 'Took the Gheluvelt cross-roads in fog on the 29th (S44).')
R('Y-GE-27RC', '10-31', '11-08', 'Gheluvelt taken; left on the Menin road', 'East of the Broodseinde cross-roads, Reutel, Polderhoek, Menin road west of Gheluvelt', ['BROOE', 'REUT', 'POLDE', 'GHELNW'], 'S41', '"with the left flank resting on the GHELUVELT-YPRES main road" (S41, 3 November)', st, 'low', 'S41 says it took "Poezelhoek" chateau from the British 1st Division on 1 November; the chateau is the one at Polderhoek.', 'YP-GHEL')
R('Y-GE-27RC', '11-09', '11-22', 'Sector shortened when the Guard came in', 'East of the Broodseinde cross-roads, Reutel, Polderhoek', ['BROOE', 'REUT', 'POLDE'], 'S41', '"held up by wire entanglements which had not been destroyed by our guns" (S41, 10 November)', inf, 'low', 'The left boundary after 9 November is inferred from the Guard\'s sector.')
R('Y-GE-54RD', '10-20', '10-30', 'At Becelaere', 'Becelaere', ['BECE'], 'S41', '"had succeeded in driving the 7th British Division out of BECELAERE" (S41)', st, 'medium', '')
R('Y-GE-54RD', '10-31', '11-10', 'Took Gheluvelt with the 30th Division', 'Gheluvelt', ['GHEL'], 'S41', '"by 3 P.M. the whole place with its château and park was in German possession" (S41)', st, 'medium', '', 'YP-GHEL')
R('Y-GE-54RD', '11-11', '11-11', 'Attacked Polygon Wood without success', 'South-east of Polygon Wood', ['POLDW'], 'S41', '"The Germans in this quarter would seem to have belonged to the 54th Reserve Division" (S41, British editors\' note 105)', st, 'low', 'The identification is the British editors\', not the German text\'s.', 'YP-NONNE')
R('Y-GE-53RD', '10-20', '11-22', 'Northern half of the corps line', 'South-west of Keiberg to east of the Broodseinde cross-roads', ['KEIBS', 'BROOE'], 'S40; S41', 'Paraphrase: the 53rd Reserve Division was in action against the British 3rd Cavalry Division and 7th Division on 19 October (S40 p.168)', inf, 'low', 'No source read places this division after the 19th. It is put in the half of the corps line the 54th did not hold.', el='unknown')
# ===== German: Sixth Army cavalry =====
R('Y-GE-HKK', '10-19', '10-20', 'Cavalry screen on the Lys', 'Gheluwe, north of Wervicq, north of Comines, Warneton', ['GELU', 'WERVN', 'COMIN', 'WARN'], 'S41', '"from its position on the line MENIN-WARNETON" (S41, of the XIII Corps, which the cavalry replaced)', st, 'low', '', 'MESS14')
R('Y-GE-HKK', '10-21', '10-29', 'Dismounted attacks on the British cavalry', 'South-east of Kruiseik, Kortewilde, Houthem, Garde Dieu, north of Deulemont', ['KRUISE', 'TENBW', 'KORW', 'GARD', 'DEULN'], 'S40; S41', '"from the Douve to the Comines Canal" (S40 p.154); "from the Gheluvelt road southward to St. Yves" (p.170)', st, 'low', 'Stetten\'s group (3rd, 7th and Bavarian Cavalry Divisions) attacked the line Kruiseik-Zandvoorde from 25 October (S41).', 'MESS14')
R('Y-GE-HKK', '10-30', '11-22', 'South of the new army group', 'The Douve, east of St. Yves, east of Le Gheer, Frelinghien', ['DOUVE', 'STYVE', 'LEGHE', 'FREL'], 'S41', '"was ordered to advance on ST. YVES and PLOEGSTEERT Wood" (S41, I Cavalry Corps, 30 October)', st, 'low', 'The I Cavalry Corps was relieved by the II on 4 November (S41). Not followed day by day.', NB)
R('Y-GE-3CD', '10-20', '10-25', 'North-east of Kruiseik', 'North-east of Kruiseik', ['KRUINE'], 'S41', '"captured a hostile position north-east of KRUISEIK" (S41)', st, 'medium', '')
R('Y-GE-3CD', '10-26', '10-29', 'Took Kruiseik', 'Kruiseik', ['KRUI'], 'S41', '"was able to capture KRUISEIK on the 26th after heavy street fighting" (S41)', st, 'medium', 'Not followed after the army group took over this front.', el='unknown')
# ===== German: Army Group Fabeck =====
R('Y-GE-15C', '10-29', '10-29', 'Assembled behind the cavalry', 'North of Wervicq', ['WERVN'], 'S41; S44', '"the assembly of the Army Group Fabeck was completed without disturbance" (S41)', inf, 'low', 'Place inferred from S44: the group was "rushed up to Deûlémont and Werviq".', 'YP-GHEL')
R('Y-GE-15C', '10-30', '10-30', 'Attacked south of the Menin road', 'West of Kruiseik to Zandvoorde', ['KRUIW', 'ZAND'], 'S41', '"with its left wing on ZANDVOORDE" (S41)', st, 'low', '', 'YP-GHEL')
R('Y-GE-15C', '10-31', '11-01', 'Through Gheluvelt and towards Klein Zillebeke', 'South-west edge of Gheluvelt, west of Zandvoorde, east of Klein Zillebeke', ['GHELSW', 'ZANDW', 'KLZE'], 'S41', '"reach the eastern edge of the HERENTHAGE Wood" (S41, 30th Division, 1 November)', st, 'low', '', 'YP-GHEL')
R('Y-GE-15C', '11-02', '11-05', 'Slow progress in the woods', 'South-west edge of Gheluvelt, east of the woods, east of Klein Zillebeke, east of the canal bend', ['GHELSW', 'SHREE', 'KLZE', 'CANBE'], 'S41', '"held up by the difficult wooded country east of ZWARTELEEN" (S41, 2 November)', st, 'low', '')
R('Y-GE-15C', '11-06', '11-08', 'Took Klein Zillebeke', 'South-west edge of Gheluvelt, east of the woods, Klein Zillebeke, the canal bend', ['GHELSW', 'SHREE', 'KLZ', 'CANB'], 'S41', '"the 39th Division delivered a heavy attack near KLEIN ZILLEBEKE" (S41)', st, 'low', '')
R('Y-GE-15C', '11-09', '11-22', "Southern part of its old sector, under Linsingen", 'East of the woods, Klein Zillebeke, the canal bend', ['SHREE', 'KLZ', 'CANB'], 'S41', '"the capture of Hill 60 near ZWARTELEEN was of exceptional importance" (S41, 11 November)', st, 'low', 'The line is not moved for Hill 60: see YC05. Gained more ground in the Zwarteleen woods on 14 November (S41).')
R('Y-GE-30D', '10-30', '10-30', 'Took Zandvoorde', 'Zandvoorde', ['ZAND'], 'S41', 'Paraphrase: Zandvoorde was taken by the 30th Division (S41)', st, 'medium', '', 'YP-GHEL')
R('Y-GE-30D', '10-31', '10-31', 'Took Gheluvelt with the 54th Reserve Division', 'South of Gheluvelt', ['GHELS'], 'S41', '"by 3 P.M. the whole place with its château and park was in German possession" (S41)', st, 'medium', '', 'YP-GHEL')
R('Y-GE-30D', '11-01', '11-08', 'East edge of Herenthage wood; into Veldhoek', 'South-west edge of Gheluvelt', ['GHELSW'], 'S41', '"entered VELDHOEK and established itself firmly" (S41, 2 November)', st, 'low', 'Drawn short of Veldhoek: the British accounts keep their line east of it until 11 November. Not followed after 8 November.', el='unknown')
R('Y-GE-39D', '10-31', '11-05', 'Left of the corps, in the small woods', 'West of Zandvoorde', ['ZANDW'], 'S41', '"the 39th Infantry Division was able to advance only some 500 yards" (S41, 31 October)', st, 'low', '', 'YP-GHEL')
R('Y-GE-39D', '11-06', '11-22', 'Took Klein Zillebeke', 'Klein Zillebeke', ['KLZ'], 'S41', '"the 39th Division delivered a heavy attack near KLEIN ZILLEBEKE" (S41)', st, 'low', 'S41: it drove out French troops and took about 400 prisoners. Not followed after this.', el='unknown')
R('Y-GE-2BC', '10-30', '10-30', 'Took Hollebeke', 'Hollebeke to Wambeke', ['HOLL', 'WAMB'], 'S41', '"took possession of the château, and finally also of the village of HOLLEBEKE" (S41)', st, 'medium', '', 'MESS14')
R('Y-GE-2BC', '10-31', '11-09', 'Astride the canal; up to Oosttaverne', 'South of the canal bend, west of Hollebeke, Oosttaverne', ['CANBS', 'HOLLW', 'OOST'], 'S41', '"the left of the Corps advanced as far as OOSTTAVERNE" (S41, 31 October)', st, 'low', 'Reached the canal bend on 1 November (S41).', 'MESS14')
R('Y-GE-2BC', '11-10', '11-22', 'Took St. Eloi', 'South-west of the canal bend, St. Eloi, north-east of Wytschaete', ['CANBSW', 'STEL', 'WYTSNE'], 'S41', '"took the high ground on which ST. ELOI is situated" (S41, 9-10 November)', st, 'low', 'See YC07 for a different account of the St. Eloi fighting.')
R('Y-GE-26D', '10-30', '10-30', 'Closing on Messines', 'South of Wambeke to east of Messines', ['WAMBS', 'MESSE2'], 'S41', '"with its left wing on MESSINES" (S41)', st, 'medium', '', 'MESS14')
R('Y-GE-26D', '10-31', '11-22', 'Took Messines and its ridge', 'West edge of the ridge at Messines to south-west of the village', ['MESSNW', 'MESSSW'], 'S41', '"the 26th Infantry Division held almost the whole of the famous ridge" (S41, 1 November)', st, 'medium', 'Not followed after 3 November. See YC04.', 'MESS14')
R('Y-GE-6BRD', '10-28', '10-29', 'Army reserve', 'Dadizeele', ['DADI'], 'S41', '"arrived at DADIZEELE as Army Reserve" (S41)', st, 'medium', 'One of its regiments attacked at Gheluvelt on the 29th (S41).', NB)
R('Y-GE-6BRD', '10-30', '10-30', 'Moving up', 'Menin to Wervicq', ['MENE', 'WERV'], 'S41', '"moved to the line MENIN-WERWICQ" (S41)', st, 'medium', '', NB)
R('Y-GE-6BRD', '10-31', '11-01', 'Attacks on Wytschaete', 'Just east of Wytschaete', ['WYTSE2'], 'S41', '"by 4 P.M. had reached the eastern edge of WYTSCHAETE" (S41, 1 November)', st, 'medium', '', 'MESS14')
R('Y-GE-6BRD', '11-02', '11-22', 'Took Wytschaete', 'Wytschaete', ['WYTS'], 'S41', '"the village, as far as its western edge, was in German hands" (S41, 2 November)', st, 'medium', 'Stormed the park of Wytschaete on 13 November (S41). See YC04.', 'MESS14')
R('Y-GE-3D', '11-01', '11-01', 'Army group reserve', 'North of Comines and Warneton', ['COMIN', 'WARNN'], 'S41', '"arrived in the area COMINES-WARNETON, north of the LYS" (S41)', st, 'medium', '', NB)
R('Y-GE-3D', '11-02', '11-22', 'In line between Wytschaete and Messines', 'South of Wytschaete to the ridge north of Messines', ['WYTSS', 'MESSN'], 'S41', '"consisting of the 3rd and 26th Infantry Divisions" (S41, of Group Urach, 3 November)', st, 'low', 'Not followed after 3 November.', 'MESS14')
# ===== German: Army Group Linsingen =====
R('Y-GE-4D', '11-09', '11-10', 'Came into line south of the Menin road', 'South-west edge of Gheluvelt to east of the woods', ['GHELSW', 'SHREE'], 'S41', '"were placed under the commander of the Guard Corps" (S41)', inf, 'low', 'S41 gives the northern part of the XV Corps sector; the line is inferred.')
R('Y-GE-4D', '11-11', '11-18', 'Pushing into Herenthage wood', 'East edge to the southern part of Herenthage wood', ['HERE', 'HERES'], 'S41', '"In the southern part of the HERENTHAGE Wood the 4th Infantry Division pushed on" (S41)', st, 'low', 'Attacked again on 13, 14 and 17 November. See YC06.', 'YP-NONNE')
R('Y-GE-GD', '11-09', '11-10', 'Came into line north of the Menin road', 'West of Polderhoek to the Menin road west of Gheluvelt', ['POLDW', 'GHELNW'], 'S41', '"were placed under the commander of the Guard Corps" (S41)', inf, 'low', 'The division reached Roubaix on 7 November (S41). The line is inferred.')
R('Y-GE-GD', '11-11', '11-18', 'Attack of the Guard', 'South edge of Polygon Wood to the Menin road in front of Veldhoek', ['PWSS', 'GUARD', 'VELDE'], 'S41; S42; S43', '"the strong position along the southern edge of the POLYGON Wood" (S41, 3rd Guard Regiment)', st, 'low', 'The 1st Guard Regiment broke through into Nonne Bosschen and was driven out the same day. The line drawn is where the sources leave the Guard that night: on the old British front line.', 'YP-NONNE')
R('Y-GE-9RD', '11-10', '11-10', 'Attacked towards St. Julien and was pulled out', 'Between Poelcappelle and St. Julien', ['STJUN'], 'S41', '"decided to pull out the main body of the 9th Reserve Division" (S41)', st, 'low', 'Place inferred from "in the direction of St. Julien".')
R('Y-GE-5RD', '11-05', '11-05', 'Attack on Langemarck failed', 'West edge of Langemarck', ['LANGW'], 'S41', '"had forced its way close up to the western edge of LANGEMARCK" (S41)', st, 'medium', '')

EVENTS = [
 # id, campaign, battle, earliest, latest, name, summary, pos ids, sources  (pos ids filled below by unit/date lookup)
 ('YE01', '10-19', '10-19', 'Encounter', "Four new German reserve corps strike the Allied cavalry screen. Roulers falls and the British 7th Division gives up its advance on Menin.", 'YPRES1', 'S40; S41'),
 ('YE02', '10-20', '10-20', 'Ridge lost', 'The Germans take Passchendaele and Becelaere. The British I Corps arrives behind Ypres.', 'YPRES1', 'S40; S41'),
 ('YE03', '10-21', '10-21', 'I Corps halted', "Haig's attack towards Poelcappelle and Langemarck is stopped in the afternoon; the French cavalry withdraws behind the canal.", 'YP-LANG', 'S40; S47'),
 ('YE04', '10-22', '10-23', 'Langemarck', 'The Germans break in at Kortekeer Cabaret on the 22nd; the British retake it on the 23rd. Mass attacks on Langemarck fail.', 'YP-LANG', 'S41; S42; S44'),
 ('YE05', '10-24', '10-24', 'French take over', 'The French IX Corps and Territorials relieve the British 2nd and 1st Divisions in the north. The Germans cross the Yser at Tervaete.', 'YP-LANG', 'S41; S42; S47'),
 ('YE06', '10-26', '10-26', 'Kruiseik lost', "German cavalry and the XXVII Reserve Corps take Kruiseik from the 7th Division.", 'YPRES1', 'S41; S42'),
 ('YE07', '10-29', '10-29', 'Cross-roads lost', 'A dawn attack in fog takes the cross-roads south-east of Gheluvelt. Army Group Fabeck assembles behind the cavalry.', 'YP-GHEL', 'S41; S44'),
 ('YE08', '10-30', '10-30', 'Fabeck attacks', 'Zandvoorde and Hollebeke fall to the new army group. The Belgians flood the Yser plain and the Germans there withdraw that night.', 'YP-GHEL', 'S41; S42; S44'),
 ('YE09', '10-31', '10-31', 'Gheluvelt', 'Gheluvelt falls about 1.30 p.m.; the 2nd Worcestershire retake it and the line is re-formed in front of Veldhoek. Messines is stormed.', 'YP-GHEL', 'S41; S42; S43'),
 ('YE10', '11-01', '11-02', 'Messines ridge lost', 'Messines and Wytschaete pass to the Germans. The French XVI Corps takes over west of the ridge.', 'MESS14', 'S41; S42; S45'),
 ('YE11', '11-05', '11-06', '7th Division relieved', 'Brigades of II Corps take over south of the Menin road. On the 6th the Germans take Klein Zillebeke and are checked at Zwarteleen.', 'YPRES1', 'S41; S42'),
 ('YE12', '11-10', '11-10', 'Dixmude and St. Eloi', 'Dixmude falls, the Germans reach the canal north of Ypres, and the Bavarians take St. Eloi.', 'YPRES1', 'S41'),
 ('YE13', '11-11', '11-11', 'Nonne Bosschen', "The Prussian Guard breaks through north of the Menin road, reaches Nonne Bosschen and is driven out.", 'YP-NONNE', 'S41; S42; S43'),
 ('YE14', '11-17', '11-17', 'Offensive called off', 'A last attack south of the Menin road fails and the Fourth Army gives up the offensive.', 'YPRES1', 'S41; S42'),
 ('YE15', '11-22', '11-22', 'End (British date)', 'The French have taken over the salient from the British I Corps. The British official history ends the battle here.', 'YPRES1', 'S44; S47'),
]

CONFLICTS = [
 ('YC01', 'YPRES1', 'When did the battle end?', 'S47: the French say 13 November, the British 22 November, the Germans 30 November. S41: the Fourth Army gave up the offensive on 17 November. S44: 22 November in the summary box, but the text has the Yser floods ending the battle on 30 November.',
  'Battle record ends between 17 and 22 November. The playback runs to 22 November.', 'National official histories define the battle differently, in time and in ground. A battle record needs room for more than one definition.', 'Open'),
 ('YC02', 'YP-LANG', 'When, and by whom, was the British 2nd Division relieved?', 'S47: replaced on its front by a French division on 23 October. S42: relieved in the night of 23-24 October by the French "18th Corps (9th Army)". S44: the French IX Corps took over the north end of the salient on 23 October.',
  'Start of the rows for the British 2nd Division at Polygon Wood and the French 17th Division held as a range, 23 to 24 October. Unit taken as the 17th Division of IX Corps.', 'Hamilton (S42) wrote in 1916 without the French order of battle; "18th Corps" looks like a slip for the 18th or 17th Division of IX Corps.', 'Open'),
 ('YC03', 'YPRES1', 'Which British division took over from the 7th Division on 5-7 November?', "S41, British editors' note: the 3rd Division had taken over south of the Menin road by 7 November. S42: the 7th and 15th Brigades. S43: \"The trenches were now held by the Fifth Division (Morland's)\".",
  'Recorded as the 3rd Division with a note. Start held as a range, 5 to 7 November.', 'The 7th Brigade belonged to the 3rd Division and the 15th to the 5th, so both names have something behind them. The relieving force was a mixture.', 'Open'),
 ('YC04', 'MESS14', 'Who held Messines and Wytschaete on 1 and 2 November?', 'S45: the Germans had both by the morning of 1 November. S41: Messines cleared to its western edge on 1 November; Wytschaete entered and lost twice, then taken by 5 p.m. on 2 November. S42: "at 11 a.m. on the 2nd, both Messines and Wytschaete were retaken by the French", and again on 6 November.',
  'German account followed: Messines German from 31 October to 1 November, Wytschaete from 2 November. French line drawn west of both.', 'Hamilton may be describing French counter-attacks that got into the villages and did not stay.', 'Open'),
 ('YC05', 'YPRES1', 'Did the Germans take Hill 60 on 11 November?', 'S41: the XV Corps captured Hill 60 near Zwarteleen on 11 November. None of the British sources read mentions it. As far as I know the hill is usually said to have been lost by French troops in December 1914.',
  'Line not moved. Hill 60 left on the Allied side with a note on both rows.', 'Needs a French source or the later chapters of the British official history.', 'Open'),
 ('YC06', 'YP-NONNE', 'Who held Herenthage wood and its chateau after 14 November?', "S41: \"HERENTHAGE Wood was completely taken by the Guard on the 14th November\". S41, British editors' note: the chateau fell and was recovered the same day by the 2nd King's Own Yorkshire Light Infantry.",
  'British line kept in the west part of the wood, German line in the east and south.', '', 'Open'),
 ('YC07', 'YPRES1', 'Who broke through at St. Eloi, and when?', 'S44, citing a 2006 history: on 11 November the German 3rd and 26th Divisions broke through at St. Eloi and reached Zwarteleen. S41: the 5th Bavarian Brigade stormed St. Eloi on 9-10 November; the 3rd and 26th Divisions were on the Messines ridge; Zwarteleen was the XV Corps.',
  'German account followed.', 'St. Eloi and Zwarteleen are four kilometres apart on opposite sides of the canal. The S44 sentence may run two events together.', 'Open'),
 ('YC08', 'YP-GHEL', 'What are the dates of the battle of Gheluvelt?', 'S47 and S44 summary: 29 to 31 October. S44 section heading: to 1 November. S40 chapter titles carry "Battle of Gheluvelt" through 5 November.',
  'Battle record: 29 to 31 October, with the wider dates in the notes.', '', 'Open'),
 ('YC09', 'YP-LANG', 'Where was the break-in of 22 October?', 'S42: the 1st Brigade was attacked "at Pilkem". S40, S44, S47: the German break-in was at Kortekeer Cabaret, about a mile north of Pilckem.',
  'Kortekeer Cabaret used.', 'Hamilton names the nearest village; the others name the inn on the road.', 'Open'),
 ('YC10', 'YPRES1', 'Where was the German 46th Reserve Division on 19 October?', 'S40 (summarising the German account): it reached Staden. S41 itself: it was close to Staden on the 19th and took it on the 20th.',
  'The row for the 19th is placed at Staden with a note.', 'A day\'s difference at division level; shows the cost of working from summaries.', 'Open'),
]

GAPS = [
 ('YG01', 'YPRES1', 'The British official history could be read only to page 176 (22 October)', 'British positions after 22 October come from two popular histories of 1916 and from editors\' notes in the German account. They are thinner and less exact than the first four days.', 'Read chapters VI to XVIII of the 1925 volume and, above all, its daily situation maps (maps 11 to 39).'),
 ('YG02', 'YPRES1', 'No French source was read', 'French divisions are placed from British and German accounts. Several rows say only that a French division was somewhere in a sector, and two do not know which division held the line.', 'Read the French official history (Les armees francaises dans la Grande Guerre, tome I, volume 4) and its maps.'),
 ('YG03', 'YPRES1', 'German positions rest on one account', 'The 1917 General Staff monograph is written at corps level and to a purpose. Divisions are placed only where it happens to name them.', 'Read the German official history (Der Weltkrieg, volume 5 and 6) and a modern study such as Sheldon (2010).'),
 ('YG04', 'YPRES1', 'Positions were not taken from a period map', 'Every coordinate is a modern village centre or a point worked out from one. A line "at Zandvoorde" is drawn through the church, not along the trenches.', 'Georeference the official history\'s situation maps, as was done with Bachelder for Gettysburg.'),
 ('YG05', 'YPRES1', 'Sector lines are straight lines between named places', 'The front between two villages is drawn straight. Opposing lines are held apart by offsets I chose, so the width of no man\'s land on the map means nothing.', 'Trace the lines from period maps. Until then the playback should be read as a diagram.'),
 ('YG06', 'YPRES1', 'Some hamlets and features are placed from memory', 'About two dozen places (Koekuit, Kortekeer Cabaret, Klein Zillebeke, Zwarteleen, Hooge, Terhand, Garde Dieu, the canal bend and others) are not in the OpenStreetMap extract and carry coord_source "estimate". They are listed on the Places sheet.', 'Look each up on a 1914 trench map or the Belgian topographic map.'),
 ('YG07', 'YPRES1', 'Quotations came through a reading tool', 'The long sources were read in 100,000-character pieces by a tool that returns extracts. The quoted wording is short and probably exact, but none of it has been checked against the page.', 'Check each quotation against the page before anything is published. The Sources sheet marks every one "No" under page verified.'),
 ('YG08', 'YPRES1', 'End dates are mostly inferred', 'A row ends the day before the next row for the same unit unless a source gives the date. Where the sources stop following a unit the end is "unknown" and the playback shows its last recorded position.', 'Daily situation maps would settle most of these.'),
 ('YG09', 'YPRES1', 'Improvised groups are only partly modelled', "Bulfin's and Cavan's forces, Moussy's and Vidal's detachments, Stetten's cavalry group and Group Urach cut across divisions. Two are in the data as units; the rest are mentioned in notes. A division can be in two places at once when part of it is detached.", 'Decide whether a detachment is a unit, an assignment or a note. For now: a unit when the sources place it on its own for more than a day.'),
 ('YG10', 'YPRES1', 'Nothing below division, and the edges are cut off', 'Brigades and regiments are left out. The British II Corps at La Bassee and the 6th Division at Armentieres are south of the map; the German Marine Division and the fighting at Nieuport are barely touched.', 'A second pass at brigade level for the crisis days (29 October to 2 November, 11 November) would test the zoom from operational to tactical scale.'),
 ('YG11', 'YPRES1', 'No strengths', 'The Assignments table has no strength for any Ypres unit.', 'The official histories give ration strengths for some dates.'),
 ('YG12', 'YPRES1', 'Outside datasets do not cover the battle', 'Neither CDB90 nor the War Atlas dataset has a record for First Ypres (both have Second and Third Ypres). Only the war and the battle carry a Wikidata ID.', 'Look up Wikidata IDs for the three sub-battles, Messines 1914 and the Yser, and for the divisions.'),
 ('YG13', 'YPRES1', 'Woods are today\'s, not 1914\'s', 'Polygon Wood, Nonne Bosschen and Houthulst Forest are drawn from the bounding boxes of their modern outlines. Herenthage wood and the woods round Klein Zillebeke are not drawn at all.', 'Take the 1914 wood outlines from a period map.'),
]

SOURCES = [
 ('S40', 'Military Operations, France and Belgium, 1914, volume II: Antwerp, La Bassee, Armentieres, Messines, and Ypres, October-November 1914', 'Brig. Gen. J. E. Edmonds', '1925', 'Official history (British)', 'Macmillan, 1925. Read: pp. 96 to 176 only (to 22 October)', 'No', 'https://archive.org/details/3edmilitaryopera02edmouoft', 'Public domain in the United States (published 1925); Crown copyright expired', 'Read through a reading tool in pieces; pages after 176 could not be reached (YG01). Page numbers are as the tool reported them.', 'YPRES1'),
 ('S41', 'Ypres, 1914: An Official Account Published by Order of the German General Staff', 'Otto Schwink; English translation with notes by the Historical Section (Military Branch), Committee of Imperial Defence', '1919', 'Official account (German), with British editorial notes', 'Constable, 1919; Project Gutenberg ebook 44234', 'No', 'https://gutenberg.org/ebooks/44234', 'Public domain', 'German text of 1917. The numbered notes are the British translators\' and are cited as such.', 'YPRES1'),
 ('S42', 'The First Seven Divisions: Being a Detailed Account of the Fighting from Mons to Ypres', 'Lord Ernest Hamilton', '1916', 'Popular history by a serving officer', 'Hurst and Blackett, 1916; Project Gutenberg ebook 39158', 'No', 'https://gutenberg.org/ebooks/39158', 'Public domain', 'Written from unit diaries and letters, without the French or German side.', 'YPRES1'),
 ('S43', 'The British Campaign in France and Flanders, 1914', 'Arthur Conan Doyle', '1916', 'Popular history', 'Hodder and Stoughton, 1916; Project Gutenberg ebook 65042', 'No', 'https://gutenberg.org/ebooks/65042', 'Public domain', 'Read from 29 October on only.', 'YPRES1'),
 ('S44', 'First Battle of Ypres', 'Wikipedia contributors', 'read 12 Nov 2026', 'Encyclopedia article (tertiary)', 'Cites Edmonds 1925, Sheldon 2010, Beckett 2006, Strachan 2001', 'n/a', 'https://en.wikipedia.org/wiki/First_Battle_of_Ypres', 'CC BY-SA 4.0', 'Used for dates, the French reliefs and the last ten days. Everything taken from it needs a better source.', 'YPRES1'),
 ('S45', 'Battle of Messines (1914)', 'Wikipedia contributors', 'read 12 Nov 2026', 'Encyclopedia article (tertiary)', 'Cites Edmonds 1925 and Beckett 2006', 'n/a', 'https://en.wikipedia.org/wiki/Battle_of_Messines_(1914)', 'CC BY-SA 4.0', '', 'YPRES1'),
 ('S46', 'First Battle of Ypres order of battle', 'Wikipedia contributors', 'read 12 Nov 2026', 'Encyclopedia list (tertiary)', 'Cites Lomas, First Ypres 1914 (Osprey, 1998)', 'n/a', 'https://en.wikipedia.org/wiki/First_Battle_of_Ypres_order_of_battle', 'CC BY-SA 4.0', 'Commanders only. The page lists no Belgian formations and has lost some headings.', 'YPRES1'),
 ('S47', 'First battle of Ypres, 19 October-22 November 1914; Battle of Langemarck, 21-24 October 1914', 'J. Rickard', 'read 12 Nov 2026', 'Web article (tertiary)', 'historyofwar.org', 'n/a', 'https://www.historyofwar.org/articles/battles_ypres1.html', 'Copyright the author; facts only used', '', 'YPRES1'),
 ('S48', 'Wikidata: First Battle of Ypres (Q853976)', 'Wikidata contributors', 'read 12 Nov 2026', 'Identifier', '', 'n/a', 'https://www.wikidata.org/wiki/Q853976', 'CC0', 'ID found by search; the item page itself was not opened.', 'YPRES1'),
]

CH6 = {'TERH', 'KLZ', 'GARD', 'GXR', 'POEZ', 'HERC', 'SHRE', 'ZWAR', 'HOOGE', 'HERE', 'SHREE', 'SHREW', 'KLZE', 'ZWARE', 'HEREW', 'HERES', 'GXRE', 'POEZE', 'POLDE'}   # places moved or added in v6
def ll(key): return (PL[key][2], PL[key][3])

# v7: lines read from the dated sketches (kept in its own file)
import os as _os
exec(compile(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ypres_v7.py'), encoding='utf-8').read(), 'ypres_v7.py', 'exec'), globals())
