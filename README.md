# WarMapper

WarMapper is a battlefield study guide on a map: pick a battle, then watch it unfold over maps drawn at the time and over today's ground.

This repository holds the proof-of-concept work: battle data for three pilot battles and a playback prototype of each.

**Status: prototype. None of the history here has been checked by a historian.** Every position cites a source and states how sure it is, but treat all of it as unreviewed.

## What is here

| Folder | Contents |
| --- | --- |
| `playbacks/` | One folder per battle. `index.html` is the playback; open it in a browser. |
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
python3 playbacks/ypres/build.py
```

The Gettysburg playback is still built from the older v2 workbook and covers the morning only.

## How the data is organised

Positions are rows in linked tables: wars, campaigns, battles, units, assignments, positions, places, routes, events, sources, plus tables of conflicts between sources and gaps in them. Times are ranges (earliest and latest), every coordinate records how it was obtained and how precise it is, and automated checks run on every build. The `Read me` sheet of the workbook explains each table and what changed in each version.

## Credits and licence

Base-map lines and place names are derived from OpenStreetMap data, © OpenStreetMap contributors, available under the Open Database License. The historical sources for each battle are listed on the `Sources` sheet of the workbook.

The period maps shown in the playbacks:

| Playback | Map | Scan from |
| --- | --- | --- |
| Gettysburg | John B. Bachelder, *Map of the battle field of Gettysburg: First day's battle*, 1876 | Boston Public Library, Norman B. Leventhal Map Center |
| Trenton | Lt. Andreas Wiederhold, *Sketch of the engagement at Trenton, given on the 26th of December 1776* | Library of Congress, Geography and Map Division |
| First Ypres | Sketch maps in J. E. Edmonds, *Military Operations, France and Belgium, 1914*, volume II (Macmillan, 1925) | Internet Archive |

The maps themselves are old enough to be in the public domain in the United States. The terms the holding institutions set for reuse of their scans have not all been checked.

No licence has been chosen for this repository yet.
