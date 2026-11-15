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
| `playbacks/` | One folder per battle: its page (`index.html`), its battle file (`battle.json`) and its period-map images. |
| `app/` | What every playback shares: `core.js` (reading a battle file, the map, the clock, the controls), `core.css`, and the map library in `app/vendor/`. |
| `tools/` | `export_battles.py`, which writes and checks the battle files, and `build.py`, which builds the pages. |
| `docs/` | `battle-file.md`: the layout of a battle file. |
| `data/` | The pilot workbook (all three battles as linked tables), the Gettysburg source workbook, and the OpenStreetMap extracts used to draw the base maps. |
| `pipeline/` | The scripts and data modules that build the workbook and run its checks, and `battlefile.py`, which checks a battle file against the format. |

The three pilots:

| Battle | Dates | Scale | Position rows |
| --- | --- | --- | --- |
| Gettysburg, first morning | 1 July 1863 | Regiments and batteries, by the minute | 38 |
| Trenton | 25 to 26 December 1776 | Regiments, by the minute | 61 |
| First Ypres | 18 October to 22 November 1914 | Corps and divisions, by the day | 215 |

## What is not here yet

- **The full-resolution map scans.** The playbacks carry reduced copies of the period maps (see Credits). The original scans are too large for the repository; the scripts rebuild the reduced copies when a scan is placed under `maps/`.
- **The scripts that georeference those scans.** Only their results (the fitted parameters) are included.
- **The product requirements document.**

## Rebuilding

Python 3 with `openpyxl` and `Pillow`.

```
# the workbook, with its checks
python3 pipeline/build_workbook.py "data/Gettysburg Day 1 data pilot v2.xlsx" out.xlsx

# the battle files (playbacks/<battle>/battle.json), checked against the format
python3 tools/export_battles.py

# one playback: its battle file, then its page
python3 tools/export_battles.py ypres
python3 tools/build.py ypres

# all three pages, plus a single-file copy of each that opens from a folder with no web server
python3 tools/build.py --single out/
```

The Gettysburg playback covers the morning only.

## How the playbacks are built

The map is drawn with [MapLibre GL JS](https://maplibre.org/), an open-source map library, kept in `app/vendor/` so the site has no outside dependency apart from web fonts. The site is static: no server, no database, no keys.

- **Each battle is one battle file**, `playbacks/<battle>/battle.json`, and every battle's file has the same layout: units, where the sources put them and when, events, sources, the period maps and the current map. Places are longitude and latitude; times are dates and clock times. [`docs/battle-file.md`](docs/battle-file.md) describes it. The Gettysburg file is written from the workbook; the Trenton and First Ypres files are written from the data modules the workbook's rows for those battles are made from.
- **`app/core.js`** reads the battle file and runs the map (base layers, period-map images, the camera, picking a unit), the clock (play, slider, scrolling over the timeline, arrow keys) and the date box.
- **Each battle's `page.src.html`** holds what is still particular to that playback: where each unit is drawn between two recorded positions, how its units are laid out and drawn, and its side panel.
- **Units and names** are drawn in an SVG layer on top of the map, so they stay sharp and can be laid out to avoid each other.
- **Coordinates.** For drawing, `core.js` lays each battle out on a flat grid in metres, east and south of a point the battle file names. Trenton's 1776 sketch is not to scale, so it is shown as a picture in its own right and units carry separate positions on it.

A browser will not let a page opened straight from a folder hand its images to the map, so `playbacks/*/index.html` must be served by a web server (GitHub Pages, or `python3 -m http.server` in this folder). The single-file copies carry their images inside the page and do not need one.

## How the data is organised

Positions are rows in linked tables: wars, campaigns, battles, units, assignments, positions, places, routes, events, sources, plus tables of conflicts between sources and gaps in them. Times are ranges (earliest and latest), every coordinate records how it was obtained and how precise it is, and automated checks run on every build. The `Read me` sheet of the workbook explains each table and what changed in each version.

## Credits and licence

Base-map lines and place names are derived from OpenStreetMap data, © OpenStreetMap contributors, available under the Open Database License. The historical sources for each battle are listed on the `Sources` sheet of the workbook.

The map library is MapLibre GL JS, © MapLibre contributors, under the BSD 3-Clause licence (`app/vendor/MAPLIBRE-LICENSE.txt`).

The period maps shown in the playbacks:

| Playback | Map | Scan from |
| --- | --- | --- |
| Gettysburg | John B. Bachelder, *Map of the battle field of Gettysburg: First day's battle*, 1876 | Boston Public Library, Norman B. Leventhal Map Center |
| Trenton | Lt. Andreas Wiederhold, *Sketch of the engagement at Trenton, given on the 26th of December 1776* | Library of Congress, Geography and Map Division |
| First Ypres | Sketch maps in J. E. Edmonds, *Military Operations, France and Belgium, 1914*, volume II (Macmillan, 1925) | Internet Archive |

The maps themselves are old enough to be in the public domain in the United States. The terms the holding institutions set for reuse of their scans have not all been checked.

No licence has been chosen for this repository yet.
