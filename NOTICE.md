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
| Sgt. J. H. Warking, Signal Corps, *Map of Manila and vicinity: showing positions of troops prior to the battle of February 5th* (1899) | Library of Congress, Geography and Map Division | Public domain (US government work) | `playbacks/manila/warking-1899.webp` (reduced copy; the full scan is streamed from the library) |
| Capt. W. L. Siebert, Corps of Engineers, *Map of central Luzon, showing a portion of the field of operations of the 8th Army Corps* (1899) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | `playbacks/luzon1899/siebert-1899.webp` (reduced copy; the full scan is streamed from the library) |
| Lt. H. P. Howard, *Map of northern Luzon*, prepared under Brig. Gen. S. B. M. Young (1900) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | `playbacks/luzon1899/young-1900.webp` (reduced copy; the full scan is streamed from the library) |

## Modern map data and tiles

| Material | Terms | How it is used |
|---|---|---|
| OpenStreetMap data | © OpenStreetMap contributors, [Open Database License](https://www.openstreetmap.org/copyright) | Today's roads, water and names, cut down into `data/base/` and the battle files (the fall-back current map and the place names) |
| USGS Topo base map and aerial photography, The National Map | Public domain (US government work) | Streamed from `basemap.nationalmap.gov` for Gettysburg and Trenton |
| Natural Earth (1:10m land, roads, railroads, rivers, lakes) | Public domain, [naturalearthdata.com](https://www.naturalearthdata.com/about/terms-of-use/) | The fall-back current map under Luzon 1899 (`data/base/luzon1899.json`) |
| OpenTopoMap | Map style CC-BY-SA, opentopomap.org; data © OpenStreetMap contributors, SRTM | Streamed from `tile.opentopomap.org` for First Ypres, Manila and Luzon 1899 |

## Software

| Package | Licence | Where |
|---|---|---|
| MapLibre GL JS | BSD 3-Clause, text in `app/vendor/MAPLIBRE-LICENSE.txt` | `app/vendor/` |

## Written sources

The battle data cites published histories, reports and markers. These are listed, with their terms where known, on the `Sources` sheet of `data/WarMapper battle data.xlsx`. No text is copied from works in copyright beyond short quotations.
