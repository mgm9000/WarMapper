# WarMapper

WarMapper is a battlefield study guide on a map: pick a battle, then watch it unfold over maps drawn at the time and over today's ground.

This repository holds the proof-of-concept work: battle data for three pilot battles and a playback prototype of each.

**Status: prototype. None of the history here has been checked by a historian.** Every position cites a source and states how sure it is, but treat all of it as unreviewed.

## Website

The playbacks are served with GitHub Pages at https://mgm9000.github.io/WarMapper/ once Pages is switched on for this repository (Settings, Pages, deploy from the `main` branch, root folder). `index.html` at the top of the repository is the landing page.

## What is here

| Folder | Contents |
| --- | --- |
| `index.html`, `assets/` | The landing page for the website and its three preview images. |
| `playbacks/` | One folder per battle: its battle file (`battle.json`), the script that writes it (`prep.py`), its period-map images, and the built page (`index.html`). |
| `app/` | The playback, the same for every battle: `page.html` (the page), `player.js` (the rules of a playback), `core.js` (reading a battle file, the map, the clock), `core.css`, and the map library in `app/vendor/`. |
| `tools/` | `export_battles.py`, which writes every battle file from the workbook and checks it, and `build.py`, which builds the pages. |
| `docs/` | `battle-file.md`: the layout of a battle file. |
| `data/` | **`WarMapper battle data.xlsx`, the master copy of the battle data**; `base/`, the current map under each battle; `osm/`, the OpenStreetMap extracts those were cut from; `legacy/`, the two older workbooks. |
| `pipeline/` | `battlefile.py` (checks a battle file against the format), `basemaps.py` (cuts the current maps from the extracts), `pictures.py` (cuts the period-map pictures from the full scans), `georef/` (how the period maps were fitted to the ground), and `legacy/` (retired scripts). |

The three pilots:

| Battle | Dates | Scale | Position rows |
| --- | --- | --- | --- |
| Gettysburg, first day | 1 July 1863 | Brigades by the minute, with regiments and batteries for the morning | 131 |
| First Battle of Trenton | 25 to 26 December 1776 | Regiments, by the minute | 61 |
| First Ypres | 18 October to 22 November 1914 | Corps and divisions, by the day | 215 |

## What is not here yet

- **The full-resolution map scans.** The playbacks carry reduced copies of the period maps (see Credits). The original scans are too large for the repository; the scripts rebuild the reduced copies when a scan is placed under `maps/`.
- **The scripts that georeference those scans.** Only their results (the fitted parameters) are included.
- **The product requirements document.**

## Changing the data

The workbook, `data/WarMapper battle data.xlsx`, is the master copy. Edit it, then:

```
# write the battle files from the workbook (playbacks/<battle>/battle.json), checked against the format
python3 tools/export_battles.py

# build the pages, plus a single-file copy of each that opens from a folder with no web server
python3 tools/build.py --single out/
```

Python 3 with `openpyxl` (and `Pillow` and `numpy` for the two map scripts).

- A battle file that breaks the format is not written, and the script says which row is at fault: a track naming a row that does not exist, a source that is cited but not listed, a point far off the map.
- A coordinate that is wrong but still on the map cannot be caught that way. The script lists places where a unit would have to move implausibly fast between two rows; read those.
- It also lists every place where one side's symbol is drawn within 50 m of the other's, minute by minute ("contact"). Close fights show up there, and so does a unit overrun on the map without the data saying what became of it: that one needs a row that has it fall back, or `show_to` so it leaves the map.
- A new battle is new rows: a row on `Playbacks`, its units, positions and sources, its symbols on `Tracks`, and a current map in `data/base/`. No code.

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

Positions are rows in linked tables: wars, campaigns, battles, units, assignments, positions, places, routes, events, sources, plus tables of conflicts between sources and gaps in them. Times are ranges (earliest and latest), and every coordinate records how it was obtained and how precise it is. Six more sheets say how each battle is played back: `Playbacks`, `Playback settings`, `Tracks` (which position rows each symbol on the map follows), `Nations`, `Labels` and `Maps`. The `Read me` sheet explains each table and what changed in each version. Its `Checks` sheet dates from when the workbook was generated by script and is no longer updated; the export script now does the checking.

## Credits and licence

Base-map lines and place names are derived from OpenStreetMap data, © OpenStreetMap contributors, available under the Open Database License. The historical sources for each battle are listed on the `Sources` sheet of the workbook.

The map library is MapLibre GL JS, © MapLibre contributors, under the BSD 3-Clause licence (`app/vendor/MAPLIBRE-LICENSE.txt`).

The period maps shown in the playbacks:

| Playback | Map | Scan from |
| --- | --- | --- |
| Gettysburg | John B. Bachelder, *Map of the battle field of Gettysburg: First day's battle*, 1876 | Boston Public Library, Norman B. Leventhal Map Center |
| Trenton | Lt. Andreas Wiederhold, *Sketch of the engagement at Trenton, given on the 26th of December 1776* | Library of Congress, Geography and Map Division |
| First Ypres | Sketch maps in J. E. Edmonds, *Military Operations, France and Belgium, 1914*, volume II (Macmillan, 1925) | Internet Archive |

The pictures in this repository are reduced copies. When a reader zooms in on the Gettysburg or Trenton map, the playback fetches the full scan in tiles straight from the holding library's own image service (IIIF): the Boston Public Library's for the Bachelder map, the Library of Congress's for the Wiederhold sketch. Faden's 1777 map of Trenton is warped to fit the ground, so it is shown only as the copy in this repository. If the library cannot be reached, the reduced copy stays on screen. The First Ypres sketches are pages of a scanned book and have no such service set up here.

The maps themselves are old enough to be in the public domain in the United States. The Boston Public Library marks its scans "no known copyright restrictions" and the Library of Congress its as free to use; NOTICE.md lists each one.

All rights reserved: see [LICENSE](LICENSE). The repository is public to be read, not reused. Material made by others (the map scans, OpenStreetMap data, the USGS and OpenTopoMap tiles, MapLibre) keeps its own terms, listed in [NOTICE.md](NOTICE.md).
