# Per-battle playback settings: inventory

Morgan's answers to the unexplained differences below are recorded in `docs/standing-rules.md` ("Answers from Morgan" and "Follow-ups"). This file is the snapshot they answered from.

Written 24 Nov 2026 (session A of `claude/consistency-rules-prompt.md`). Nothing was changed: this reads the `Playback settings` sheets
(`data/WarMapper battle data/csv/<war>/Playback settings.csv`) of the six playbacks as they stand on `main` (after pull request 66).
`·` means the battle sets nothing and the shared player's default applies. **Bold** marks a row where the battles differ.
Cowpens is read from `main` as it stood after pull request 66; pull requests 67 and 68 (see the last section) changed it and reached `main` on 24 Nov (pull request 70). The brackets show what they changed.

Settings that are text, lists of maps or per-map details are summarised in the last rows (maps on the menu, satellite, button word), not
copied. The full list is in the CSVs.

| Setting | Gettysburg | Trenton | First Ypres | Manila | Luzon 1899 | Cowpens | Class |
|---|---|---|---|---|---|---|---|
| Style (tactical or operational) | **tactical** | **tactical** | **operational** | **tactical** | **operational** | **tactical** | scale |
| Scale bar first measure | **yards** | **yards** | **km** | **yards** | **km** | **yards** | scale |
| Opening play speed (time units a second) | **3** | **3** | **0.5** | **10** | **1** | **1** | scale |
| Current map tile service | **USGS** | **USGS** | **OpenTopoMap** | **OpenTopoMap** | **OpenTopoMap** | **USGS** | scale |
| Current map reach (widths of the bounds map) | **4** | **·** | **·** | **·** | **·** | **3** | data |
| Bounds map (limits zoom-out and Fit) | **bachelder-1876** | **·** | **·** | **warking-1899** | **·** | **·** | data |
| Opens on | **landing rule** | **landing rule** | **landing rule** | **r99t** | **landing rule** | **r81t** | decided |
| Follow camera | **yes** | **yes** | **none** | **yes** | **none** | **yes** | scale |
| Follow: smallest box (m) | **[1000, 660]** | **[1600, 1100]** | **·** | **[3000, 2000]** | **·** | **[620, 460]** | scale |
| Follow: margin (m) | **140** | **90** | **·** | **300** | **·** | **70** | scale |
| Follow: opening glide (s; default 6) | **·** | **·** | **·** | **·** | **·** | **10 (PR 68, on `main` since PR 70: 14)** | unexplained |
| Follow: hold on whole ground until | **·** | **·** | **·** | **·** | **·** | **· (PR 68, on `main` since PR 70: 1781-01-17T06:12)** | unexplained |
| Follow: glide ease | **·** | **·** | **·** | **·** | **·** | **· (PR 68, on `main` since PR 70: 0.006)** | unexplained |
| Follow: look-ahead (min; default 30) | **·** | **·** | **·** | **·** | **·** | **12** | scale |
| Deepest zoom (screen px per m) | **1.95** | **8** | **0.6** | **1.6** | **0.05** | **8** | unexplained |
| Follow: deepest zoom | **1.04** | **2.2** | **·** | **0.6** | **·** | **2.4** | unexplained |
| Zoom below which units fold into parent | **0.215** | **·** | **0.05** | **·** | **0.006** | **0.45** | scale |
| Zoom at which level-1 names show | **0.273** | **0.12** | **0.034** | **0.12** | **0.0024** | **0.3** | scale |
| Blend between rows (min; default 4) | **4** | **3** | **·** | **·** | **·** | **4** | unexplained |
| March pace by branch | **yes** | **default** | **default** | **default** | **default** | **default** | data |
| What a question mark / dashed symbol means | **location** | **overall** | **overall** | **overall** | **overall** | **overall** | unexplained |
| Lead-in compressed (share of timeline) | **·** | **0.3** | **·** | **0.12** | **·** | **0.2** | data |
| "Times are estimates" note | **·** | **yes** | **·** | **·** | **·** | **yes** | unexplained |
| Routes taken (trails) layer | **·** | **True** | **·** | **True** | **·** | **True** | unexplained |
| Trails: fade after stop (min) | **·** | **10** | **·** | **120** | **·** | **6** | scale |
| Arrow: shortest move that earns one (km) | **·** | **·** | **·** | **0.7** | **20** | **0.25** | decided |
| Arrow: reach ahead of the unit (min) | **·** | **·** | **·** | **·** | **·** | **6** | unexplained |
| Strength of symbols outside the current event (default 0.32) | **·** | **·** | **·** | **·** | **·** | **0.7** | unexplained |
| Division / corps view when zoomed out | **yes** | **yes** | **yes** | **none** | **none** | **none** | scale |
| Fold button name | **Regiments** | **·** | **·** | **·** | **Brigades** | **Regiments and companies** | data |
| Stretches the clock skips while playing | **none** | **yes** | **none** | **none** | **yes** | **none** | decided |
| Named views (buttons) | **none** | **none** | **2** | **2** | **3** | **2** | unexplained |
| Satellite view | **yes** | **yes** | **none** | **none** | **none** | **yes** | unexplained |
| Period maps on the Type of map menu | **1** | **2** | **2** | **1** | **3** | **1** | decided |
| Current-map button word | **Today** | **Today** | **Now** | **Now** | **Now** | **Today** | unexplained |

## Sorting the differences

**Explained by era or scale** (a 1781 field battle, a 17-hour fight, a four-month campaign, a year). Leave alone:
style, scale bar, tile service (USGS for the United States, OpenTopoMap elsewhere, PRD 17 Nov), Follow on or off (not offered where the playback runs by the day),
Follow box and margin, look-ahead, fold and label zooms, trail fade times, lead-in compression, division view for Gettysburg, Trenton and Ypres
(a few hundred men at Cowpens need none). Opening play speed is scale-driven, but only Trenton (one speed, 18 Nov), Ypres (half a day a second, 19 Nov) and
Luzon (a day a second, 21 Nov) have a decision recorded; Gettysburg 3, Manila 10 and Cowpens 1 minute a second were chosen with the build and not by Morgan, as far as the notes show.

**Recorded decisions** (each one is in the register, `docs/standing-rules.md`):
Manila opens on its terrain reconstruction (22 Nov, PR 50 and 57); Cowpens opens on its 1781 reconstruction ("at Morgan's choice", 24 Nov, PR 63);
the Type of map menu carries one main map at Manila and Cowpens (22 Nov, PR 57); arrows ahead of moves, 20 km as the rule, with a 700 m trial at Manila (21 Nov, PR 48) and 250 m at Cowpens (PR 61, no decision of Morgan's recorded);
the clock skips the night at Trenton (18 Nov, PR 29) and the rains at Luzon (PR 45).

**Data-driven** (what the sources and the ground need, not a taste): current-map reach, the bounds map, march pace (only Gettysburg's rows use it),
fold button wording, `rear`, `arrival`, `groups`, `sides`, `texts`.

**Unexplained** (no scale reason, no recorded decision): these are asked in one batch and the answers go in the register.
1. Opening glide: Cowpens takes 10 s (14 s on PR 68); the others take the default 6 s. PR 68 also gives Cowpens alone `follow.hold_until` and `follow.glide_rate`.
2. Symbol strength outside the current event: Cowpens 0.7 (PR 65), the others 0.32 (the default). Morgan's rule of 24 Nov, that unit symbols stay clearly visible, was written for every battle.
3. Arrows that travel just ahead of their unit (`arrows.reach_minutes`): Cowpens only, though PR 65's title says arrows travel with their units.
4. Routes taken (trails): Trenton, Manila, Cowpens. Gettysburg, First Ypres and Luzon 1899 have none. The fade rule was decided at Trenton (19 Nov) and made shared by PR 68.
5. Deepest zoom: Gettysburg 1.95 pixels per metre against 8 at Trenton and Cowpens (1.6 at Manila). Deepest Follow zoom: 1.04, 2.2, 0.6, 2.4.
6. Blend between rows: Trenton 3 minutes; Gettysburg and Cowpens 4; PR 65 calls 4 the default.
7. The meaning of a question mark or dashed symbol: Gettysburg `location`; every other battle `overall`.
8. The "Times are estimates" note under the clock: Trenton and Cowpens only.
9. Named views: Gettysburg and Trenton have none; the other four have two or three.
10. Satellite view: Gettysburg, Trenton and Cowpens. First Ypres, Manila and Luzon have none (USGS imagery covers only the United States; PRD says Ypres needs another provider and its terms).
11. Maps on the Type of map menu: Trenton shows two period maps, First Ypres two, Luzon three. The rule of 22 Nov is one main map and the rest in the map details.
12. Current-map button word: "Today" (Gettysburg, Trenton, Cowpens) against "Now" (First Ypres, Manila, Luzon).
13. Division view: not set for Manila, although it has two divisions; for Luzon and Cowpens it is scale.

## Other things found while reading (not settings)

- **Pull requests 67 and 68 were not on `main` when this was written (fixed by pull request 70, merged 24 Nov).** Both are marked merged on GitHub, but 67 was merged into `opening-wide` after `opening-wide` (PR 66) had already gone to `main`, and 68 was merged into `cowpens-orientation-towns`. Their content (the far-town labels, the Cowpens second review, and the shared rule that a route fades once its unit moves on) is on the branch `cowpens-orientation-towns` only. The PRD and tracker call them "waiting to be merged after 66".
- `python3 tools/export_battles.py --check` on `main`: all six battles meet the format, but `data/WarMapper battle data/csv/Philippine War/Positions.csv` is out of date against its workbook (run the export).
- Nine event texts still write a time as a.m. or p.m.: First Ypres YE09 and the `ypres` playback text; Manila ME02, ME04; Trenton TE03; Gettysburg GE04, GE07, GE12, GE13, GE19. Some are a source's time quoted beside the playback's, which is a judgement call.
- First Ypres's 15 events name no position rows, so the event highlighting of 23 Nov (BP-32) does nothing there. The tracker records this.
