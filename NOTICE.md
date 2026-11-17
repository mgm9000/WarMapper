# Third-party material

WarMapper's own code, data and documentation are covered by [LICENSE](LICENSE) (all rights reserved). The material below was made by others. It is included or used under its own terms, which this repository does not change.

## Period maps

| Map | Held by | Terms | Used in |
|---|---|---|---|
| John B. Bachelder, *Map of the battle field of Gettysburg: First day's battle* (1876) | Boston Public Library, Norman B. Leventhal Map & Education Center | No known copyright restrictions | `playbacks/gettysburg/` (reduced copies; the full scan is streamed from the library) |
| John B. Bachelder, *Second day's battle* sheet (1876) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | Read to place the evening lines of 1 July; not hosted |
| Andreas Wiederhold, *Sketch of the engagement at Trenton* (1776) | Library of Congress, Geography and Map Division | Public domain | `playbacks/trenton/sketch.jpg` |
| William Faden, *Plan of the operations of General Washington against the King's troops in New Jersey* (1777) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | `playbacks/trenton/faden-1777.webp` (warped to fit the ground) |
| *Military Operations, France and Belgium, 1914*, vol. 2 (1925), Sketch A and Sketches 4 to 14 | British official history | Public domain in the United States (published 1925) | `playbacks/ypres/` |

## Modern map data and tiles

| Material | Terms | How it is used |
|---|---|---|
| OpenStreetMap data | © OpenStreetMap contributors, [Open Database License](https://www.openstreetmap.org/copyright) | Today's roads, water and names, cut down into `data/base/` and the battle files (the fall-back current map and the place names) |
| USGS Topo base map and aerial photography, The National Map | Public domain (US government work) | Streamed from `basemap.nationalmap.gov` for Gettysburg and Trenton |
| OpenTopoMap | Map style CC-BY-SA, opentopomap.org; data © OpenStreetMap contributors, SRTM | Streamed from `tile.opentopomap.org` for First Ypres |

## Software

| Package | Licence | Where |
|---|---|---|
| MapLibre GL JS | BSD 3-Clause, text in `app/vendor/MAPLIBRE-LICENSE.txt` | `app/vendor/` |

## Written sources

The battle data cites published histories, reports and markers. These are listed, with their terms where known, on the `Sources` sheet of `data/WarMapper battle data.xlsx`. No text is copied from works in copyright beyond short quotations.
