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
| `playbacks/` | One folder per battle: its page (`index.html`), its data (`data.json`) and its period-map images. |
| `app/` | What every playback shares: `core.js` (the map, the clock, the controls), `core.css`, and the map library in `app/vendor/`. |
| `tools/` | `build.py`, which builds the pages. |
| `data/` | The pilot workbook (all three battles as linked tables), the Gettysburg source workbook, and the OpenStreetMap extracts used to draw the base maps. |
| `pipeline/` | The scripts and data modules that build the workbook and run its checks. |

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

# a playback: export the data, then build the page
python3 playbacks/ypres/prep.py
python3 tools/build.py ypres

# all three pages, plus a single-file copy of each that opens from a folder with no web server
python3 tools/build.py --single out/
```

The Gettysburg playback is still built from the older v2 workbook and covers the morning only.

## How the playbacks are built

The map is drawn with [MapLibre GL JS](https://maplibre.org/), an open-source map library, kept in `app/vendor/` so the site has no outside dependency apart from web fonts. The site is static: no server, no database, no keys.

- **`app/core.js`** runs the map (base layers, period-map images, the camera, picking a unit), the clock (play, slider, scrolling over the timeline, arrow keys) and the date box.
- **Each battle's `page.src.html`** holds what is particular to that battle: its events, where each unit is at a given time, how its units are drawn, and its side panel.
- **Units and names** are drawn in an SVG layer on top of the map, so they stay sharp and can be laid out to avoid each other.
- **Coordinates.** Each battle's data is in a flat frame of its own (the 1876 sheet for Gettysburg, metres from a town centre for Trenton and Ypres). `data.json` carries the `frame` that turns those points into longitude and latitude.

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
