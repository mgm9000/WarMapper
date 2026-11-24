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
| 1st Lieut. W. G. Haan, *Map of the City of Manila and vicinity showing operations of Second Division, 8th Army Corps, from February 4th to February 28th 1899* | National Archives, identifier 109182890 (read from the copy on Wikimedia Commons) | A work of the U.S. Army: public domain in the United States. The National Archives' own use statement has not been read (its catalogue refuses automated readers) | No picture of it is in the repository. Lines read from it are in `data/recon/manila-1899.geojson`, drawn as the Manila base "1899 (reconstructed)" |
| Capt. W. L. Siebert, Corps of Engineers, *Map of central Luzon, showing a portion of the field of operations of the 8th Army Corps* (1899) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | `playbacks/luzon1899/siebert-1899.webp` (reduced copy; the full scan is streamed from the library) |
| Lt. H. P. Howard, *Map of northern Luzon*, prepared under Brig. Gen. S. B. M. Young (1900) | Boston Public Library, Leventhal Map Center | No known copyright restrictions | `playbacks/luzon1899/young-1900.webp` (reduced copy; the full scan is streamed from the library) |
| War Department, Military Information Division, *Theatre of military operations in Luzon, 1899* (second edition), both sheets | University of Minnesota Libraries, John R. Borchert Map Library (Minnesota Digital Library) | US War Department publication of 1899; the holder's statement is general ("may be governed by US and international copyright laws") | `playbacks/luzon1899/theatre-1899-north.webp` and `theatre-1899-south.webp` (reduced copies, joined from views of the holder's scans; the north sheet's full scan is streamed from the holder) |
| Robert Mills, *Spartanburgh District, South Carolina*, surveyed by J. Whitten 1820, for Mills's Atlas (1825), in a pen-and-ink tracing made for the Union army (1865) | Library of Congress, Geography and Map Division | Public domain | `playbacks/cowpens/mills-1825.webp` (cut and reduced, fitted to the ground) |
| Lt. Col. H. L. Landers, Army War College, two sketches of the Cowpens (April 1928), House Document 328, 70th Congress | Internet Archive (`historicalstatem00army`) | Public domain (US government work) | `playbacks/cowpens/landers-1928-1.webp` and `landers-1928-2.webp` |
| Edwin C. Bearss, National Park Service, *The Battle of Cowpens: Troop Movement Maps*, Plates I to IV (1967) | Morgan's copy; South Carolina State Library | Public domain (US government work; the copy carries no copyright notice) | `playbacks/cowpens/bearss-plate-1.webp` to `-4.webp`; its roads are the roads of the Cowpens base "1781 with terrain" (`data/recon/cowpens-1781.geojson`) |
| U.S. Geological Survey, *Cowpens, S.C.*, 1:62,500 (1959), and *Cowpens NE, S.C.*, orthophoto map, 1:24,000 (1975) | USGS Historical Topographic Map Collection | Public domain (US government work) | `playbacks/cowpens/usgs-1959.webp` and `usgs-1975.webp` (reprojected and cut) |
| National Park Service, *Park Map - Cowpens National Battlefield* | National Park Service (NPGallery) | Public domain (US government work) | `playbacks/cowpens/nps-park-map.webp` (reduced) |

## Modern map data and tiles

| Material | Terms | How it is used |
|---|---|---|
| OpenStreetMap data | © OpenStreetMap contributors, [Open Database License](https://www.openstreetmap.org/copyright) | Today's roads, water and names, cut down into `data/base/` and the battle files (the fall-back current map and the place names); at Cowpens also the park's trace of the road, today's Green River Road and the streams of the reconstructed base |
| USGS Topo base map and aerial photography, The National Map | Public domain (US government work) | Streamed from `basemap.nationalmap.gov` for Gettysburg, Trenton and Cowpens |
| Mapzen Terrain Tiles on AWS Open Data (elevation) | Open data; see the [attribution](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) | The terrain of the reconstructed bases (Manila 1899, Cowpens 1781) and the terrain shading, read by the page |
| Natural Earth (1:10m land, roads, railroads, rivers, lakes) | Public domain, [naturalearthdata.com](https://www.naturalearthdata.com/about/terms-of-use/) | The fall-back current map under Luzon 1899 (`data/base/luzon1899.json`) |
| OpenTopoMap | Map style CC-BY-SA, opentopomap.org; data © OpenStreetMap contributors, SRTM | Streamed from `tile.opentopomap.org` for First Ypres, Manila and Luzon 1899 |

## Software

| Package | Licence | Where |
|---|---|---|
| MapLibre GL JS | BSD 3-Clause, text in `app/vendor/MAPLIBRE-LICENSE.txt` | `app/vendor/` |

## Written sources

The battle data cites published histories, reports and markers. These are listed, with their terms where known, on the `Sources` sheet of `data/WarMapper battle data.xlsx`. No text is copied from works in copyright beyond short quotations.
