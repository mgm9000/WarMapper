# WarMapper

WarMapper is a battlefield study guide on a map: pick a battle, then watch it unfold over maps drawn at the time and over today's ground.

This repository holds the proof-of-concept work: battle data for six pilot playbacks (five battles and one campaign) and a prototype of each.

**Status: prototype. None of the history here has been checked by a historian.** Every position cites a source and states how sure it is, but treat all of it as unreviewed.

## Website

The playbacks are served with GitHub Pages at https://mgm9000.github.io/WarMapper/ once Pages is switched on for this repository (Settings, Pages, deploy from the `main` branch, root folder). `index.html` at the top of the repository is the landing page.

## What is here

| Folder | Contents |
| --- | --- |
| `index.html`, `assets/` | The landing page for the website and its preview images. |
| `playbacks/` | One folder per battle: its battle file (`battle.json`), the script that writes it (`prep.py`), its period-map images, and the built page (`index.html`). |
| `app/` | The playback, the same for every battle: `page.html` (the page), `player.js` (the rules of a playback), `core.js` (reading a battle file, the map, the clock), `core.css`, and the map library in `app/vendor/`. |
| `courses/` | Course pages: `page.html` (the template), and one folder per course with `course.json` (its class days, readings and playback slots) and the built `index.html`. See `courses/README.md`. |
| `tools/` | `export_battles.py`, which writes every battle file from the workbooks and checks it, and `build.py`, which builds the battle pages and the course pages. |
| `docs/` | `battle-file.md`: the layout of a battle file. |
| `data/` | **`WarMapper battle data/`, the master copy of the battle data**: one workbook per war and `Sources and notes.xlsx` (see Changing the data), with a CSV copy of every sheet under `csv/`; `base/`, the current map under each battle; `recon/`, the lines of each reconstructed base map as GeoJSON (Manila 1899); `osm/`, the OpenStreetMap extracts those were cut from (Natural Earth for Luzon 1899); `legacy/`, the two older workbooks. |
| `pipeline/` | `battlefile.py` (checks a battle file against the format), `basemaps.py` (cuts the current maps from the extracts), `pictures.py` (cuts the period-map pictures from the full scans), `georef/` (how the period maps were fitted to the ground), `recon/` (how a reconstructed base map's lines were read from period maps), and `legacy/` (retired scripts). |

The six pilots:

| Battle | Dates | Scale | Position rows |
| --- | --- | --- | --- |
| Gettysburg, first day | 1 July 1863 | Brigades by the minute, with regiments and batteries for the morning | 131 |
| First Battle of Trenton | 25 to 26 December 1776 | Regiments, by the minute | 61 |
| First Ypres | 18 October to 22 November 1914 | Corps and divisions, by the day | 215 |
| Manila (Philippine War), data pilot | 4 to 5 February 1899 | Brigades and regiments, by the hour; Filipino commands inferred | 38 |
| Luzon 1899 (Philippine War), data pilot | 4 February to 15 December 1899 | Columns and headquarters at the towns the reports name, by the day; the Filipino side from American reports | 82 |
| Battle of Cowpens | 17 January 1781 | Battalions, regiments and troops by the minute, 06:00 to 08:30; every unit placed by a distance the sources give along the Green River Road (no map of the time exists); clock times are the Army staff ride's reconstruction | 90 |

## A reconstructed base map (proof of concept, Manila)

The Manila playback has a third base, **1899 (reconstructed)**: the shore of 1899 (most of today's bay front was reclaimed later), the Pasig, the walls of Intramuros, the main roads, the railway and the blockhouses, read from two Army maps of February 1899 and drawn by the page in the manner of a map of the time. It is a reconstruction and says so first in the map details (the i button; since 22 Nov 2026 there is no banner on the map); every line records its source, how it was read and how sure it is, and can be tapped. Since the second pass of 21 November 2026 it also carries the engineer map's own street, block, dyke and field lines and its esteros, taken from the scan by program (`pipeline/recon/manila_1899_linework.py`, which needs `opencv-python` and `scikit-image` and the scan itself); those are marked AI-extracted and low confidence, and nobody has checked them line by line. `pipeline/recon/manila_1899_check_1898.md` records a check of the traced lines against a second map. From Malate south to Pasay, where the engineer map stops, the shore, Calle Real, blockhouses 13 and 14 and the ground's own lines come from the War Department's 1898 *Manila y sus arrabales* (Yale): `pipeline/georef/manila_arrabales_fit.py` fits that sheet and says how its hand-drawn southern strip is slid to today's streets, and `pipeline/recon/manila_1898_linework.py` takes its lines. The lines are in `data/recon/manila-1899.geojson`, the layers on the workbook's `Reconstructions` and `Recon layers` sheets, and `pipeline/recon/manila_1899.py` says how they were read. To rebuild the GeoJSON: `python3 pipeline/recon/manila_1899.py` (needs `numpy` and `scipy`).

Since 22 Nov 2026 Manila opens on its fourth base, **1899 with terrain**, and the Type of map menu offers only it and today's map: the Signal Corps map and the plain reconstruction are marked `hidden` and are offered, with a link to each original, in the map details (the i button). The terrain base is the same reconstruction made to show more the closer one looks, and to fill the window on a desktop, a tablet or a phone. The ground: the page reads elevation tiles once (zoom 12, over 40 km by 31 km, wider than the reconstruction's sheet), a worker cleans them (the tiles are a radar survey of 2000 that measured buildings as well as the ground: every bump narrower than about 230 m is taken off, the rest smoothed) and from that surface draws relief, contour lines for what is on screen (every 20 m zoomed right out, closing in to 10, 5, 2, 1 and half a metre, always sampled a few screen pixels apart so the lines stay smooth) and spot heights. Beyond the sheet's edge, marked by a dotted line, only that terrain and today's shore are drawn. It is today's ground and the map details say so. The city: from zoom 13.6 the ink of the War Department's 1898 plan of the city (Yale; 1.36 m a pixel, fitted to the engineer map to about 6 m) is laid over the reconstruction, with its blocks, public buildings, bridges and, closest in, street names; `pipeline/recon/manila_1898_ink.py` lifts the ink off the scan and writes the three pictures `playbacks/manila/manila-1898-ink*.webp`, and the engineer-map lines the plan also draws give way to it. The settings are `terrain` on the base and the `ink` feature of the reconstruction (see `docs/battle-file.md`); the code is in `app/player.js`, under "the terrain version of a reconstructed map" and "a period map's own ink".

## Cowpens (17 January 1781): how it was placed

Cowpens is the first battle built for the HIST 340 course page (`courses/hist-340/`, the 16 January class). No map made at the time shows the ground, and the accounts give distances, not places: the lines so many yards apart, the main line falling back "about 100 yards". The one line every account is tied to is the Green River Road, which still crosses the battlefield as a gravel trace. So every unit is placed by distance along that road as OpenStreetMap draws it, counted from the south-east end of the park's Battlefield Trail, where the Army's staff ride handbook and a National Park Service wayside put the head of Tarleton's column as it came onto the field (`pipeline/cowpens_geo.py`). The main line is fixed by the Washington Light Infantry monument of 1856, by which an Army War College study of 1928 says Howard's line ran. No position is rated above medium, and after the audit of 24 Nov 2026 only three are medium (Howard's line in its two positions and Washington's reserve); the rest are low. The clock (first shots about 07:00, the end about 07:50) is the staff ride's; eyewitnesses say only "about sunrise".

The rows were written by `pipeline/cowpens_2026_11_23.py`, which holds every row with its sources and can be read as the record of how the battle was built. The seventeen points where the sources disagree are on the `Hypotheses` sheet (CH01 to CH17) and the known gaps on `Gaps` (CG01 to CG08). On 24 Nov 2026 the rows were audited against their sources and checked against Bearss's troop movement maps (National Park Service, 1967; source S107): `pipeline/cowpens_audit_2026_11_24.py` made the changes, and says why. Fleming's handbook (S104) and the 1928 Army War College study (S103) print their page numbers at the foot of the page: count a page from the number below it, not above it. The playback opens on today's topographic map; it has no period map.

## What is not here yet

- **The full-resolution map scans.** The playbacks carry reduced copies of the period maps (see Credits). The original scans are too large for the repository; the scripts rebuild the reduced copies when a scan is placed under `maps/`.
- **The scripts that georeference those scans.** Only their results (the fitted parameters) are included.
- **The product requirements document.**

## Changing the data

The battle data is kept in workbooks, in the folder `data/WarMapper battle data/`. They are the master copy. Since 23 Nov 2026 there is one per war, and one that every war shares:

| Workbook | What it holds |
| --- | --- |
| `Revolutionary War.xlsx` | Trenton; Cowpens |
| `U.S. Civil War.xlsx` | Gettysburg |
| `Philippine War.xlsx` | Manila and Luzon 1899 |
| `World War I.xlsx` | First Ypres |
| `Sources and notes.xlsx` | The change log (`Read me`), `Sources` and `Source candidates`: one register of sources for every war, so a source id (S01, S02 ...) is never used twice. Also the two gaps that belong to no one war. |

Every war's workbook has the same sheets in the same order (a sheet with nothing for that war keeps its headings), and holds only that war's rows: the export stops if a row names another war's campaign, side or playback, or if an id is used in two workbooks. A new war is a new workbook with the same sheets. Edit a workbook, then:

```
# write the battle files from the workbooks (playbacks/<battle>/battle.json), checked against the format,
# and a CSV copy of every sheet (data/WarMapper battle data/csv/<workbook>/<sheet>.csv)
python3 tools/export_battles.py

# build the pages, plus a single-file copy of each that opens from a folder with no web server
python3 tools/build.py --single out/
```

Python 3 with `openpyxl` (and `Pillow` and `numpy` for the two map scripts).

- A battle file that breaks the format is not written, and the script says which row is at fault: a track naming a row that does not exist, a source that is cited but not listed, a point far off the map.
- A coordinate that is wrong but still on the map cannot be caught that way. The script lists places where a unit would have to move implausibly fast between two rows; read those.
- It also lists every place where one side's symbol is drawn within 50 m of the other's, minute by minute ("contact"). Close fights show up there, and so does a unit overrun on the map without the data saying what became of it: that one needs a row that has it fall back, or `show_to` so it leaves the map.
- A new battle is new rows in its war's workbook: a row on `Playbacks`, its units, positions and sources, its symbols on `Tracks`, and a current map in `data/base/`. No code. Its sources go on `Sources` in `Sources and notes.xlsx`, with the next free id.
- `python3 tools/export_battles.py --check` checks the battle files as they stand, that each workbook holds one war and no id twice, and that the CSV copies match the workbooks.

### Editing the workbooks

A workbook is a binary file, so GitHub cannot merge two edited copies of it. If two people start from different copies of the same workbook, one set of edits overwrites the other. So work from a fresh download, and do not edit the files on GitHub's web page, which has no spreadsheet editor.

1. **Download the current workbook** for the war you are working on from `data/WarMapper battle data/` on the `main` branch before each editing session. Do not start from an older copy on your computer.
2. **Edit that copy** in Excel and save it. A new source goes in `Sources and notes.xlsx`, so download that one too.
3. **Send it back**, either by uploading it to the repository as a replacement for the file in `data/WarMapper battle data/`, or by handing it to whoever is running the export. They run the two scripts above, which regenerate every `battle.json` and page from it and refresh the CSV copies, and open a pull request.
4. **Read the change.** On the pull request, the CSV copies show each changed row of each sheet line by line, so you can see exactly what an edit did.
5. **Merge the pull request.** The site updates a minute or two later.

Tell the other person which workbook you are editing, and have them hold off on that one until your file comes back. Two people can now work on two different wars at once; `Sources and notes.xlsx` is shared by every war, so only one person at a time should add sources. The CSV copies are written by the export: do not edit them by hand (the check fails if they no longer match their workbook).

The Gettysburg playback covers the first day, 7:15 a.m. to 5:30 p.m. After 10:15 a.m. it rests on Bachelder's 1876 map alone: brigade positions and the times printed beside them. The reports for the afternoon have not been read, and the Union brigades' places on Cemetery Hill at the end of the day are estimates.

## How the playbacks are built

The map is drawn with [MapLibre GL JS](https://maplibre.org/), an open-source map library, kept in `app/vendor/` so the site has no outside dependency apart from web fonts. The site is static: no server, no database, no keys.

- **Each battle is one battle file**, `playbacks/<battle>/battle.json`, and every battle's file has the same layout: units, where the sources put them and when, events, sources, the period maps and the current map. Places are longitude and latitude; times are dates and clock times. [`docs/battle-file.md`](docs/battle-file.md) describes it. All of them are written from the workbook by one script.
- **`app/core.js`** reads the battle file and runs the map (base layers, period-map images, the camera, picking a unit), the clock (play, slider, scrolling over the timeline, arrow keys) and the date box.
- **`app/player.js`** is the playback itself, the same for every battle: where a unit is between two recorded positions, which units fold into their parent when zoomed out, how symbols and names are laid out, the base-map switch, the timeline and the side panel. What differs from battle to battle is data, in the battle file's `playback` section. No battle has code of its own: `tools/build.py` writes each battle file into the one page, `app/page.html`.
- **What a reader can do** in every playback: play, scrub or step through time (the step can be changed), jump between key events, read the current event on the map, switch base maps and turn the period map down to see today's map through it, choose what is drawn from the Layers menu (units, names, period-style symbols, one side's point of view), open the details of the map on screen, go full screen, and copy a link that reopens the same moment, place and unit.
- **Units and names** are drawn in an SVG layer on top of the map, so they stay sharp and can be laid out to avoid each other.
- **Coordinates.** For drawing, `core.js` lays each battle out on a flat grid in metres, east and south of a point the battle file names. Trenton's 1776 sketch is not to scale, so it is shown as a picture in its own right and units carry separate positions on it.

A browser will not let a page opened straight from a folder hand its images to the map, so `playbacks/*/index.html` must be served by a web server (GitHub Pages, or `python3 -m http.server` in this folder). The single-file copies carry their images inside the page and do not need one.

## How the data is organised

Positions are rows in linked tables: wars, campaigns, battles, units, assignments, positions, places, routes, events, sources, plus a table of hypotheses (one row per point where the sources disagree: the competing readings, the evidence for and against each with its source and page, the reading the playback follows, how sure it is, and who decided) and one of gaps in the sources. The tables of one war are in that war's workbook; sources are in the shared one. Times are ranges (earliest and latest), and every coordinate records how it was obtained and how precise it is. Six more sheets say how each battle is played back: `Playbacks`, `Playback settings`, `Tracks` (which position rows each symbol on the map follows), `Nations`, `Labels` and `Maps`. The `Read me` sheet of `Sources and notes.xlsx` explains each table and what changed in each version; each war's own `Read me` says what is in it and counts its rows. Its `Checks` sheet dates from when the workbook was generated by script and is no longer updated; the export script now does the checking.

## Credits and licence

Base-map lines and place names are derived from OpenStreetMap data, © OpenStreetMap contributors, available under the Open Database License. The drawing under the Luzon 1899 playback is made with Natural Earth, which is in the public domain. The historical sources for each battle are listed on the `Sources` sheet of `data/WarMapper battle data/Sources and notes.xlsx`.

The map library is MapLibre GL JS, © MapLibre contributors, under the BSD 3-Clause licence (`app/vendor/MAPLIBRE-LICENSE.txt`).

The period maps shown in the playbacks:

| Playback | Map | Scan from |
| --- | --- | --- |
| Gettysburg | John B. Bachelder, *Map of the battle field of Gettysburg: First day's battle*, 1876 | Boston Public Library, Norman B. Leventhal Map Center |
| Trenton | Lt. Andreas Wiederhold, *Sketch of the engagement at Trenton, given on the 26th of December 1776* | Library of Congress, Geography and Map Division |
| First Ypres | Sketch maps in J. E. Edmonds, *Military Operations, France and Belgium, 1914*, volume II (Macmillan, 1925) | Internet Archive |
| Manila | Sgt. J. H. Warking, Signal Corps, *Map of Manila and vicinity showing positions of troops prior to the battle of February 5th ...*, 1899 | Library of Congress, Geography and Map Division |
| Manila, "1899 (reconstructed)" | Not a period map: drawn by the playback from lines read off 1st Lieut. W. G. Haan, *Map of the City of Manila and vicinity showing operations of Second Division, 8th Army Corps, from February 4th to February 28th 1899* (no picture of it is in the repository), and off the Warking map | National Archives (identifier 109182890), from the copy on Wikimedia Commons |
| Luzon 1899 | Capt. W. L. Siebert, Corps of Engineers, *Map of central Luzon, showing a portion of the field of operations of the 8th Army Corps*, 1899; Lt. H. P. Howard, *Map of northern Luzon* prepared under Brig. Gen. S. B. M. Young, 1900; War Department, *Theatre of military operations in Luzon, 1899*, both sheets | Boston Public Library, Norman B. Leventhal Map Center (the first two); University of Minnesota Libraries, John R. Borchert Map Library (the third) |

The pictures in this repository are reduced copies. When a reader zooms in on the Gettysburg or Trenton map, the playback fetches the full scan in tiles straight from the holding library's own image service (IIIF): the Boston Public Library's for the Bachelder map, the Library of Congress's for the Wiederhold sketch. Faden's 1777 map of Trenton is warped to fit the ground, so it is shown only as the copy in this repository. If the library cannot be reached, the reduced copy stays on screen. The Luzon maps are fetched the same way, two from the Boston Public Library and one from the University of Minnesota's collection in the Minnesota Digital Library. The First Ypres sketches are pages of a scanned book and have no such service set up here.

The maps themselves are old enough to be in the public domain in the United States. The Boston Public Library marks its scans "no known copyright restrictions" and the Library of Congress its as free to use; NOTICE.md lists each one.

All rights reserved: see [LICENSE](LICENSE). The repository is public to be read, not reused. Material made by others (the map scans, OpenStreetMap data, the USGS and OpenTopoMap tiles, MapLibre) keeps its own terms, listed in [NOTICE.md](NOTICE.md).
