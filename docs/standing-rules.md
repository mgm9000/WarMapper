# WarMapper standing rules (the register)

Started 24 Nov 2026 by session A of `claude/consistency-rules-prompt.md`. Master copy: this file, in the repo, versioned with the code.
Read-only mirror for chats outside the repo: `claude/standing-rules.md` in the WarMapper Project (refreshed at the end of every session).

**What this is for.** Morgan makes decisions while reviewing one map. Some reach every battle by themselves (they live in the shared player,
`app/player.js`, or the exporter, `tools/export_battles.py`). Others are set battle by battle in the workbook's `Playback settings` sheet
(`claude/battle-file-format.md`) or were decided on one map and never carried to the next. This file lists every rule, where Morgan decided it,
where it is built in, how to check it, and whether each of the six playbacks follows it.

**How a rule is kept (since 24 Nov 2026, session B).** Each entry says what enforces it:
- **preset**: the value is in the Playback presets sheet (`Sources and notes.xlsx`, `docs/presets.md`), so every battle based on that preset
  gets it and a battle that differs must give a reason in the `why` column;
- **exporter**: `tools/export_battles.py` works it out for every battle (start map, arrow limits, reach and fade times);
- **player**: the shared player (`app/player.js`) does it the same way for every battle;
- **check**: `python3 tools/consistency_check.py` fails (or warns) when a battle breaks it;
- **document only**: only this file and a person's review keep it (visual judgement, sources, data still to gather).
Run `python3 tools/consistency_check.py --against main` before every pull request; `tools/screenshots.py` gives pictures to compare.

**Sources.** Every entry cites where Morgan's decision was recorded: the Project memory file for WarMapper (`areas/military-map-explorer.md`, "memory"),
the PRD's dated progress notes ("PRD"), the tracker's Summary note ("tracker"), the Project prompts, and pull request descriptions ("PR n").
No rule was invented. Where no reason was recorded the entry says so.

**Status codes.** A = applied. A* = the rule applies and Morgan has decided to bring the battle in line, but the work is not done yet (see Follow-ups at the end). E = exception (Morgan's reason given). N = not applicable. ? = ask Morgan. Columns: Gettysburg, Trenton, First Ypres, Manila, Luzon 1899, Cowpens and, since 26 Nov 2026, Guilford Courthouse.

**Answers of 24 Nov 2026.** Morgan answered the batch of questions on 24 Nov. His answers are in each rule's entry and listed under "Answers from Morgan" and "Follow-ups" at the end. Session A changed nothing in the player, the exporter or the workbooks. Session B (branch `presets-and-checks`, the same night) built the presets and the check and carried out F-2 and most of F-3; the matrix below is that branch.

## Matrix (as of 24 Nov 2026, evening: `main` after pull request 72, then the session C audit; the Guilford Courthouse column added 26 Nov 2026 on branch `guilford-courthouse`)

| Rule | Gettysburg | Trenton | First Ypres | Manila | Luzon 1899 | Cowpens | Guilford CH | Enforced by |
|---|---|---|---|---|---|---|---|---|
| SR-01 24-hour time | A | A | A | A | A | A | A | player (clock); check (texts) |
| SR-02 Landing view | A | A | A | A | A | A | A | exporter (reconstruction first); player; check |
| SR-03 Current map is a modern topographic map | A | A | A | A | A | A | A | preset (us-maps, world-maps, all); check |
| SR-04 Open zoomed out, hold on the whole ground, ease in slowly | A | A | A | A | A | A | A | player; preset (tactical, operational); check |
| SR-05 Day pauses and summaries | N | N | A | N | A | N | N | player; check |
| SR-06 Arrows ahead of long moves (limit scales with the battle) | A | A | A | A | A | A | A | preset and exporter; check |
| SR-07 Arrows run ahead of their unit by a time-scale reach | A | A | A | A | A | A | A | preset and exporter; check |
| SR-08 Ships (boats at Trenton, naval gunfire at Ypres) | N | A* | A* | A | A | N | N | document only |
| SR-09 Map credits in the i button | A | A | A | A | A | A | A | player; check (every map has a credit) |
| SR-10 Units visibly move; the enemy is shown | A | A | A | A | A | A | A | check (both sides); document |
| SR-11 Symbols stay clearly visible (70%); moves and arrows smooth | A | A | A | A | A | A | A | preset (all); player; check |
| SR-12 Reconstructed maps carry detail at every zoom | N | N | N | A | N | A | A | document only (screenshots) |
| SR-13 No reconstruction banner on the map | N | N | N | A | N | A | A | player |
| SR-14 Elevation-derived terrain labelled, cleaned, never period | N | N | N | A | N | A | A | player; document |
| SR-15 One main map on the Type of map menu | A | A | A | A | A | A | A | check |
| SR-16 Routes taken: layer on every battle; routes fade | A | A | A* | A | A | A | A | preset (all) and exporter; player; check |
| SR-17 Events tied to units on the map | A | A | A* | A | A | A | A | player; check (warning) |
| SR-18 Follow camera: smooth, keeps up | A | A | N | A | N | A | A | player |
| SR-19 Scholarly history, where it cites the reports, settles dates and names; both readings kept | A* | A* | A* | A* | A | A* | A* | document only |
| SR-20 Every time and position cross-checked | A | A | A | A | A | A | A | document only (audit) |
| SR-21 Never `stated` or `high` without a cited source | A | A | A | A | A | A | A | check (a source is cited); audit |
| SR-22 Rights: host only public-domain or open material | A | A | A | A | A | A | A | check (warning); document |
| SR-23 The workbook is master; CSV copies current | A | A | A | A | A | A | A | exporter; check |
| SR-24 Controls and layout on phones, tablets and desktops | A | A | A | A | A | A | A | player; check (labels); screenshots |
| SR-25 No "Times are estimates" note under the clock | A | A | A | A | A | A | A | check |
| SR-26 Current-map button reads "Modern" | A | A | A | A | A | A | A | preset (all); check |
| SR-27 Tactical battles share their settings unless a reason is recorded | A | A | N | A | N | A | A | preset (tactical); check (reasons) |
| SR-28 Orientations: clashes by who won, shape and colour, sourced, both readings where disputed | N | N | N | N | N | N | N | preset (orientation); player; check |
| SR-29 Orientations: control of places, dated and sourced | N | N | N | N | N | N | N | player; check |
| SR-30 Orientations: month by month, busy months slower, one stop at the end | N | N | N | N | N | N | N | preset (orientation); player; check |
| SR-31 Reconstructed maps follow the clock (dated lines) | N | N | N | A | N | A | A | player |
| SR-36 A regional map under a battle in a chapter (option B) | N | N | N | N | N | A* | A* | player; exporter (format check) |

Since 25 Nov 2026 there is a seventh kind of playback, the **orientation** (clashes and places, no units), built for the HIST 340 South
Carolina chapter and tried so far only on made-up rows (`tests/orientation/make_demo.py`). No orientation is on the site yet, so it has no
column; the section "Orientations" below says which rules reach it.

Notes on the matrix. Guilford Courthouse (26 Nov 2026): the carry-forward check before it was built found every rule that reaches a tactical battle already kept by the presets, the exporter or the player; SR-19 is A* because the standard modern study (Babits and Howard, 2009) has not been read, and SR-12 and SR-14 are met by a reconstruction whose lines are Hatch's (1971) on today's terrain. `python3 tools/consistency_check.py --against main` passes with it. SR-01: the eight a.m./p.m. texts were converted in the session C audit (24 Nov; Morgan's yes), so all six now pass; SR-16: First Ypres has the layer
but no route on record, so it draws nothing and the switch is not offered until routes are entered (F-7). SR-23: the out-of-date Philippine War
CSV was exported on this branch (Morgan's "Accepted" review marks). SR-07: the arrow lead time (how long before a unit sets off its arrow appears) is not scaled like the reach: see F-8.


---

## SR-01 24-hour time everywhere

- **Decided:** 18 Nov 2026 (memory; PRD "Trenton corrections and a 24-hour clock", PR 28).
- **Rule:** the clock, the timeline and the panel show times as 24-hour (07:45), never a.m. or p.m.
- **Why:** not recorded beyond Morgan's wish.
- **Scope:** all battles.
- **Built in:** shared player (clock, timeline, panel); exporter times. Event and summary text is typed by hand in each war's workbook (manual).
- **Check:** `grep -rn "a\.m\.\|p\.m\." "data/WarMapper battle data/csv/<war>/Events.csv" "…/Summaries.csv"`.
- **Enforced by:** player shows the clock and timeline in 24-hour time; `consistency_check.py` fails on a.m. or p.m. in an event, summary, opening, About or unit-panel text (a source's own wording, quoted in a row, is left as written).
- **Status:** all six applied. **Session C audit (24 Nov, evening):** the check found eight texts still on a.m./p.m. (Gettysburg GE04 playback text, GE07, GE12, GE13, GE19; Trenton TE03; First Ypres YE09 and the summary of 31 Oct). Morgan said yes to converting them as proposed; done in the three workbooks, re-exported, check clean. Manila had passed since session B.

## SR-02 Landing view

- **Decided:** 17 Nov 2026 (memory; PRD "Landing view and the current map", PR 20). Manila exception 22 Nov (PRD, PR 50 and 57). Cowpens: "at Morgan's choice" 24 Nov (PRD, PR 63).
- **Rule (updated 24 Nov 2026, Morgan's answer):** a battle opens on its own reconstructed map if it has one; otherwise on its period map if one covers the opening view; otherwise on a modern topographic map. It opens on the whole map with no units or lines; they appear when play starts. (Morgan first typed the order "reconstructed, modern topo, period map", then chose "reconstruction first, then the 17 Nov rule", so Gettysburg and Trenton keep their period maps.)
- **Why:** not recorded beyond Morgan's decision.
- **Scope:** all battles. Manila (22 Nov) and Cowpens (24 Nov) were exceptions; with the updated rule they simply follow it.
- **Built in:** shared player `startBase()`; per-battle setting `start_base` (Manila `r99t`, Cowpens `r81t`).
- **Check:** open each playback fresh: the first map and an empty field. `Playback settings.csv`: `start_base`.
- **Enforced by:** exporter: a battle with a reconstructed map on the menu opens on it unless it sets `start_base` (Manila's and Cowpens's rows are gone); player: otherwise its period map over the opening view, else the current map; check: fails if a battle with a reconstruction opens elsewhere, or if it would open on a map kept off the menu.
- **Status:** all applied. Gettysburg and Trenton open on their period maps, First Ypres and Luzon on the modern map, Manila and Cowpens on their reconstructions. The player's default `startBase()` still reads "period map, else modern" and Manila and Cowpens set `start_base` by hand; a new battle with a reconstruction needs the shared default to prefer it (Follow-up F-2). **Session B (24 Nov, branch `presets-and-checks`):** all six open as the rule says; the default now prefers the reconstruction (exporter).
- **Since PR 66 (24 Nov):** where a battle opens on a period map it now fills about the middle quarter of the screen, with today's map around it.

## SR-03 "Current map" is a modern topographic map, readable under the units

- **Decided:** 17 Nov 2026 (memory; PRD, PR 20). Muting, terrain shading, scale bar: PRD 16 and 18 Nov, PR 18 and 32.
- **Rule:** the Current map is a modern topographic map for every battle (USGS Topo for US battles, OpenTopoMap elsewhere). The modern map is muted, with a terrain shading layer and a scale bar on every map. The battle's own drawing of today's roads is only the fall-back when the service cannot be reached.
- **Scope:** all battles. **Built in:** shared player; per-battle `modern.*` settings.
- **Check:** `Playback settings.csv`: `modern.tiles` is set for every playback; open the Current map and look.
- **Enforced by:** preset: `us-maps` (USGS topographic map) or `world-maps` (OpenTopoMap) gives `modern.*`; `all` gives the standard Current map (`bases.N.use = current`); check: fails without a modern map or a current base.
- **Status:** all applied. OpenTopoMap is "to revisit before a product" (PRD 17 Nov).

## SR-04 Open zoomed out, then ease in slowly

- **Decided:** 24 Nov 2026 (memory: "start zoomed out so the viewer gets the context of the surrounding terrain, then zoom in slowly"; PRD, PR 66).
- **Rule:** every playback opens one zoom level wider than its first view (twice as wide); pressing play eases the camera in. A link to a moment or view opens there; Start over returns to the wide opening.
- **Scope:** all battles. **Built in:** shared player (`playback.opening_zoom_out`, default 1; Follow `glide_seconds`, default 6 s).
- **Check:** open each playback, press play, watch the first 10 seconds.
- **Enforced by:** player (opening one zoom level wide); preset `tactical`: Follow eases in over 14 s at 0.006 a frame; preset `operational`: `opening_ease` 0.006 (new setting, the battles without Follow); a battle whose first units come later holds with `follow.hold_until` (Cowpens 06:12); check: fails if Follow eases in faster than 10 s or a battle without Follow has no `opening_ease`.
- **Added 24 Nov 2026 (Morgan's answer):** every battle holds on the whole ground until its first units are on the map, then eases in slowly (Cowpens: `follow.hold_until` 06:12, `follow.glide_rate` 0.006, on `main` since pull request 70).
- **Status:** the wide opening is applied everywhere (PR 66 table: opening zooms 10.95, 10.26, 9.18, 10.74, 5.40, 12.49). The hold-then-ease is built for Cowpens only (on `main` since pull request 70): Cowpens applied, A* for the other five (Follow-up F-2; First Ypres and Luzon have no Follow and need the same idea in their own ease). **Session B (24 Nov, branch `presets-and-checks`):** done for all six (presets `tactical` and `operational`).

## SR-05 Day pauses and summaries

- **Decided:** 19 Nov 2026 (memory; PRD "Menus, day pauses and summaries", PR 37).
- **Rule:** a battle longer than two days stops at the end of each day (or week) with a summary and a Continue button. Two to seven days: pause by default. Over 14 days: ask the viewer first (daily and weekly summaries).
- **Scope:** all battles longer than two days. **Built in:** shared player `day_pause`; `Summaries` sheet.
- **Check:** `battle.json`: `time` length; `summaries` present where over two days.
- **Enforced by:** player (`day_pause`); check: fails if a playback over two days has pauses turned off, warns if it has no summaries.
- **Status:** First Ypres (36 days, 41 summaries) and Luzon 1899 (about 10 months, 45 summaries): applied, "ask" by default. Gettysburg (Day 1), Trenton, Manila and Cowpens run two days or less: not applicable.

## SR-06 Arrows ahead of long moves

- **Decided:** 21 Nov 2026 (memory; PRD, PR 44). Manila trial limit 21 Nov (memory, PR 48).
- **Rule:** a move over 20 km is prefaced with an arrow from the unit's place to its next one along the approximate route, not a straight line. **Updated 24 Nov 2026 (Morgan's answer):** the shortest move that earns an arrow scales with the battle, instead of being 20 km everywhere: Manila's 700 m and Cowpens's 250 m become the pattern for a small field, 20 km stays for campaigns. The values for Gettysburg and Trenton are to be chosen with Morgan.
- **Scope:** all battles; limit per battle. **Built in:** shared player `arrows` (`on`, `min_km`, `lead`).
- **Check:** `Playback settings.csv`: `arrows.*`; play a long move.
- **Enforced by:** preset and exporter: on a battlefield (`tactical`, `arrows.min_share` 0.06) the limit is 6% of the width of the battle's ground: Gettysburg 0.5 km, Trenton 1.3 km; on a campaign (`operational`) 20 km. Manila 0.7 km and Cowpens 0.25 km keep their own, with reasons. Check: fails if a battle has no limit.
- **Status:** First Ypres and Luzon: applied at 20 km (campaign scale). Gettysburg and Trenton run on the 20 km default, so they get no arrows on moves of a few kilometres: A* (F-2). Manila 0.7 km and Cowpens 0.25 km: A* (the trial and the PR 61 value become the pattern). **Session B (24 Nov, branch `presets-and-checks`):** done for all six (Gettysburg 0.5 km, Trenton 1.3 km by the 6% rule).

## SR-07 Arrows run just ahead of their unit

- **Decided:** 24 Nov 2026 (PRD, PR 65, "at Morgan's request": Ogilvie's arrows were standing at the field while he was 3 km off).
- **Rule:** an arrow reaches only a short way ahead of its unit, not to the end of a long road. **Morgan, 24 Nov (his own words): "Arrows will run ahead depending on the time scale being used."** So the reach is not a fixed 6 minutes everywhere: it follows the battle's time scale (minutes at a field battle, days at a campaign).
- **Scope:** all battles. **Built in:** shared player `arrows.reach_minutes` (Cowpens 6).
- **Check:** `Playback settings.csv`: `arrows.reach_minutes`; watch a long move.
- **Enforced by:** preset and exporter: `all`, `arrows.reach_seconds` 6: an arrow runs 6 seconds of play ahead of its unit, worked out at the opening speed (Gettysburg and Trenton 18 min, Manila 60 min, Cowpens 6 min, First Ypres 3 days, Luzon 6 days). Check: fails without a reach.
- **Status:** Cowpens applied (6 minutes). Every other battle: A*, once the shared player takes the reach from the time scale (F-2). **Session B (24 Nov, branch `presets-and-checks`):** done for all six (6 seconds of play).

## SR-08 Ships

- **Decided:** 21 Nov 2026 (memory; PRD, PR 45).
- **Rule:** draw ships whenever they are part of the battle, deliver units or give gunfire support to a battle on land. Show the ship with the ground unit's symbol beside it, then the unit landing; the ship fades unless it stays in the battle.
- **Scope:** all battles. **Built in:** `branch` naval units in the workbook (only the Philippine War workbook has any: 11).
- **Check:** `Units.csv` for `Naval`; look for ship symbols in play.
- **Enforced by:** document only (it needs units and sources; F-5).
- **Status:** Manila and Luzon: applied. Gettysburg and Cowpens: no ships: N. Trenton (the army crosses the Delaware in boats) and First Ypres (British naval gunfire off the Belgian coast): **Morgan, 24 Nov: show them where the sources support them.** A* for both (F-5). The notes do not say whether either was considered before.

## SR-09 Map credits behind the info button

- **Decided:** 21 Nov 2026 (memory; PRD, PR 46). Phones 18 Nov (PR 33), touch screens 19 Nov (PR 35).
- **Rule:** credits sit in the i button on every map and every screen size.
- **Scope:** all battles. **Built in:** shared player.
- **Check:** open each playback at phone, tablet and desktop width; no credit line outside the i panel.
- **Enforced by:** player (credits in the i panel, shown for five seconds as a map opens); check: fails if a map, imagery, reconstruction or the modern map has no credit.
- **Status:** all applied (shared player; not re-tested in this session).

## SR-10 Units visibly move; the enemy is shown too

- **Decided:** 21 Nov 2026 (memory, on the Manila playback; PRD, PR 48). The memory entry says "every playback's units".
- **Rule:** units move so a viewer can see it; the enemy side is on the map, not only US forces.
- **Scope:** all battles. **Built in:** data (Positions and Tracks) plus the shared player.
- **Check:** `battle.json`: tracks per side. Today: Gettysburg 27 and 26; Trenton 20 and 16; First Ypres 24 and 26; Manila 22 and 7; Luzon 34 and 9; Cowpens 14 and 11.
- **Enforced by:** check: fails if only one side has units on the map; how well they move stays a person's review.
- **Status:** all applied. The Filipino side at Manila and Luzon is thin, and at Manila mostly inferred and low confidence (PRD, PR 48).

## SR-11 Symbols stay clearly visible; movements and arrows are smooth

- **Decided:** 24 Nov 2026 (memory; PRD, PR 65, "Morgan found four faults").
- **Rule:** unit symbols stay clearly visible (not faint), and movements and arrows are smooth, with nothing popping in and out or jumping. **Updated 24 Nov 2026 (Morgan's answer):** units outside the current event keep 70% strength on every battle (default `event_dim` 0.7).
- **Scope:** all battles. **Built in:** the player fixes for jumps are shared (PR 65: they also removed jumps at Trenton, Gettysburg and Manila). Symbol strength outside the current event is `playback.event_dim`: 0.32 by default, 0.7 at Cowpens only.
- **Check:** `Playback settings.csv`: `event_dim`; `__wm.scene()` samples (PR 65).
- **Enforced by:** preset `all`: `event_dim` 0.7 on every battle; player: smooth moves; check: fails below 0.7.
- **Status:** Cowpens applied. Gettysburg, Trenton, Manila, Luzon: smooth moves applied, symbol strength still at 0.32: A* (F-2: change the shared default to 0.7). First Ypres: its events name no rows, so nothing dims yet; once F-4 gives them rows it needs 0.7: A*. **Session B (24 Nov, branch `presets-and-checks`):** done for all six (preset `all`).

## SR-12 Reconstructed maps carry terrain and city detail, and zooming in gives commensurate detail across the whole window

- **Decided:** 21 and 22 Nov 2026 (memory; PRD, PR 48 and 56).
- **Rule:** a reconstructed period-style map carries terrain and city detail; zooming in gives more detail everywhere on screen, with no empty margin on any screen shape.
- **Scope:** every battle that has a reconstructed map. **Built in:** `Reconstructions` and `Recon layers` sheets, `bases[].terrain`.
- **Check:** zoom in at the opening view and at the edge of the sheet; no blank margin.
- **Enforced by:** document only: look at the screenshots (`tools/screenshots.py`, close view).
- **Status:** Manila and Cowpens: applied (Cowpens not re-checked visually here). The other four have no reconstructed map: N.

## SR-13 No reconstruction banner on the map itself

- **Decided:** 22 Nov 2026 (memory; PRD, PR 55). **Rule:** the "reconstruction" label sits in the i panel, not on the map. The sheet's own title still calls it a reconstruction.
- **Scope:** every reconstructed map. **Built in:** shared player. **Check:** open the reconstructed base.
- **Status:** Manila and Cowpens: applied; others N.
- **Enforced by:** player (no banner on any reconstructed map).

## SR-14 Terrain from today's elevation data is labelled, cleaned, never drawn as a period feature

- **Decided:** 22 Nov 2026 (PRD, PR 53; "the rule this sets for other battles"; memory).
- **Rule:** terrain from today's elevation data is labelled as such, cleaned of buildings where a city stands, and never drawn as a period feature. The relief panel says what a battle's heights are.
- **Scope:** all battles with a terrain base. **Built in:** `bases[].terrain`; map-details panel.
- **Check:** open the map details (i) of the terrain base.
- **Enforced by:** player (labels and the relief panel); document.
- **Status:** Manila and Cowpens: applied. Others N (their terrain shading is on today's map and labelled "Terrain shading on today's map").

## SR-15 One main map on the Type of map menu

- **Decided:** 22 Nov 2026 (memory; PRD "Manila opens on the terrain map", PR 57: "the pattern for other battles").
- **Rule:** one main map on the menu; supporting maps are offered from the map details (base keys `hidden` and `note`).
- **Scope:** all battles. **Built in:** `Playback settings`: `bases.N.hidden`, `bases.N.note`.
- **Check:** `Playback settings.csv`: count bases without `hidden` or `of` that are period or reconstructed maps.
- **Enforced by:** check: fails unless exactly one map besides the current map and the aerial photography is on the Type of map menu. Main maps chosen 24 Nov (session B): Trenton Faden 1777, First Ypres the sketch of the day, Luzon Siebert 1899; the others are in the map details.
- **Status:** Gettysburg (one period map), Manila and Cowpens: applied. Trenton (two), First Ypres (two) and Luzon (three): **Morgan, 24 Nov: do the same.** A* (F-3). **Session B (24 Nov, branch `presets-and-checks`):** done for Trenton, First Ypres and Luzon.

## SR-16 Routes taken fade

- **Decided:** 19 Nov 2026 at Trenton (memory; PRD, PR 36). Made shared 24 Nov (PR 68, on `main` since pull request 70): a route also fades once its unit moves on without one.
- **Rule:** once a unit has stood still, the routes it took to get there fade out. **Updated 24 Nov 2026 (Morgan's answer): every battle has the routes-taken layer.**
- **Scope:** all battles. **Built in:** `trails.*` settings; shared player.
- **Check:** `Playback settings.csv`: `trails.on`.
- **Enforced by:** preset `all`: routes on, opacity 0.55, fading after 4 seconds of play over 4 more, worked out by the exporter (Gettysburg 12 min, First Ypres 2 days, Luzon 4 days); Trenton (10 min, 19 Nov), Manila (120 and 60) and Cowpens (6 and 6, opacity 0.5) keep theirs with reasons; player: the switch is offered only where a battle has a route; check: fails without the layer.
- **Status:** Trenton, Manila, Cowpens: applied. Gettysburg, First Ypres, Luzon have no routes layer: A* (F-3; fade times to be set for each battle's scale). **Session B (24 Nov, branch `presets-and-checks`):** done for Gettysburg and Luzon; First Ypres has the layer but no routes yet (F-7).

## SR-17 Events tied to units on the map

- **Decided:** 23 Nov 2026 (PRD and tracker, PR 59, BP-32).
- **Rule:** a current event highlights its units and arrows and dims the rest; picking an event frames its rows.
- **Scope:** all battles. **Built in:** events `steps`; shared player.
- **Check:** `battle.json`: events with `steps`.
- **Enforced by:** player (BP-32); check: warns on events that name no rows (First Ypres, 15 of 15).
- **Status:** Gettysburg 19 of 19 events, Trenton 14 of 14, Manila 8 of 8, Luzon 28 of 28, Cowpens 14 of 14: applied. First Ypres 0 of 15: **Morgan, 24 Nov: give them their rows** (the known BP-32 gap). A* (F-4).

## SR-18 Follow camera

- **Decided:** 17 and 18 Nov 2026 (PRD, PR 23, 28, 31). **Rule:** Follow keeps the units in view, does not pulse, pauses when the reader moves the map, and eases by time.
- **Scope:** battles followed by the clock. **Built in:** shared player; `follow.*`.
- **Check:** play with Follow on; the zoom does not change direction repeatedly.
- **Enforced by:** player.
- **Status:** Gettysburg, Trenton, Manila, Cowpens: applied. First Ypres and Luzon have no Follow (followed by the day): N.

## SR-19 A scholarly history read against the reports settles dates and names; the reports stay on record where they disagree

- **Decided:** 22 Nov 2026, Luzon 1899: "Linn wins" (PRD, PR 52). Scope settled 24 Nov 2026 by Morgan ("only if it cites the reports").
- **Rule:** read a scholarly history against the primary reports. Where the history cites the reports or maps it relied on, its reading settles the date or name and is the playback's; the other readings stay in the `Hypotheses` sheet. Where it does not cite them, the playback keeps the better-sourced reading.
- **Scope:** all battles.
- **Built in:** manual (data and the `Hypotheses` sheet, 59 disputed points at 23 Nov).
- **Check:** `Hypotheses.csv`: the adopted reading and who decided.
- **Enforced by:** document only (F-6).
- **Status:** Luzon applied. Elsewhere the notes keep the other reading: Gettysburg keeps Bachelder's times over Reardon and Vossler (C03, C13, 17 Nov); Trenton keeps the 1929 History of Trenton and Stryker over Elliott (TC14, TC15). A* for Gettysburg, Trenton, First Ypres, Manila and Cowpens: each battle's disputed points are to be re-read against this rule (F-6). Gettysburg C03 and C13 and Trenton TC14 and TC15 are the first to look at.

## SR-20 Every time and position is cross-checked against at least one other authoritative source

- **Decided:** 23 Nov 2026 (HIST 340 build prompt, standing rules). Earlier checks: Gettysburg against Reardon and Vossler and the Official Records (17 Nov, PR 21); Trenton against Elliott (17 Nov, PR 26); Luzon against Linn (22 Nov, PR 52); Cowpens audit and Bearss (24 Nov, PR 62).
- **Scope:** all battles. **Built in:** `source_pages` and `cross_checked_by` columns on Positions (manual).
- **Check:** empty `cross_checked_by` on a Positions row; the audit step (Opus subagent) of the Project instructions.
- **Enforced by:** document only (the audit step).
- **Status:** applied for all six according to the PRD notes. First Ypres had the German account added to its Hypotheses sheet (23 Nov, PR 59); no full row-by-row pass is recorded.

## SR-21 Never rate a position `stated` or `high` without a cited source

- **Decided:** standing since the project began (Project instructions; PRD MS-2; Manila prompt 21 Nov).
- **Rule:** a position is `stated` or `high` only if a cited source says so; if unsure, `inferred` or `low`. A reconstructed feature is `high` only when a cited source supports it and a person has checked it.
- **Scope:** all battles. **Built in:** `confidence` and `method` columns; manual review.
- **Check:** a quick check is that no `high` row lacks a source: today none (high rows: Gettysburg 2, Trenton 1, Manila 2, Luzon 24, Cowpens 0, First Ypres 0). It does not show that the source says it; the Opus audit does.
- **Enforced by:** check: fails if a row is `stated` or `high` with no source cited; that the source says so stays the audit's job.
- **Status:** all applied. Luzon's 24 `high` rows have not had an audit recorded.

## SR-22 Rights: host only public-domain or openly licensed material

- **Decided:** PRD (link-and-stream, no scans hosted; undated, in the first week); NOTICE.md; licence 17 Nov (memory, PR 24); restated 23 Nov (HIST 340 prompt).
- **Rule:** host only public-domain or openly licensed material; everything else is linked and cited, never copied. Imagery is streamed, not hosted.
- **Scope:** all battles. **Built in:** `Sources.csv` `rights` column; `maps[].credit`.
- **Check:** every source and map in each `battle.json` has `rights`, `credit` and `source` (true today for all six).
- **Enforced by:** check: warns on a cited source with no rights recorded; document.
- **Status:** all applied.

## SR-23 The workbook is master; the battle files and CSV copies come from it

- **Decided:** 15 Nov 2026 (memory; PRD "Workbook as master"). Split by war 23 Nov (PR 59).
- **Rule:** edit the workbook; the exporter writes every `battle.json`; each sheet has a CSV copy that reads line by line in git.
- **Scope:** all battles. **Built in:** `tools/export_battles.py`.
- **Check:** `python3 tools/export_battles.py --check`. On `main` today: all six meet the format; `csv/Philippine War/Positions.csv` is out of date against its workbook.
- **Enforced by:** exporter; check: rebuilds every battle and fails if a battle file, page or CSV copy is not what the workbooks give.
- **Status:** applied. The out-of-date Philippine War CSV (Manila and Luzon) was exported on branch `presets-and-checks` (24 Nov, session B).

## SR-24 Controls and layout on phones, tablets and desktops

- **Decided:** 18 to 22 Nov 2026 (PRD, PR 29, 33, 34, 35, 37, 51). **Rule:** a Start over button; Type of map, Follow, Map options and Battle options menus; a text sheet on phones; a fold-away narrower pane on tablets; a draggable pane on desktops.
- **Scope:** all battles. **Built in:** shared player. **Check:** open each at three widths.
- **Status:** all applied (shared; not re-tested in this session).
- **Enforced by:** player; check: fails if a unit on the map has no name or label; screenshots at phone and desktop widths.

---

## SR-25 No "Times are estimates" note under the clock

- **Decided:** 24 Nov 2026 (Morgan's answer, in his words: "Dont show 'times are estimates' under the clock on all maps").
- **Rule:** the clock carries no "Times are estimates" note on any map.
- **Scope:** all battles. **Built in:** `Playback settings`: `time_note.from`, `time_note.text`.
- **Check:** `Playback settings.csv`: no `time_note.*` row.
- **Enforced by:** check: fails if a battle shows a note under the clock. Trenton's and Cowpens's rows were removed (session B).
- **Status:** Trenton and Cowpens set the note: A* (F-3: remove). The others never had it: N. How sure a time is stays in the details of each row. **Session B (24 Nov, branch `presets-and-checks`):** done (Trenton, Cowpens).

## SR-26 The current-map button reads "Modern"

- **Decided:** 24 Nov 2026 (Morgan's answer: he chose a third word, "Modern", over "Today" and "Now").
- **Rule:** the short word for the Current map button is "Modern" on all battles. The long label stays "Current map" (SR-03).
- **Scope:** all battles. **Built in:** `Playback settings`: `bases.N.short` of the current map.
- **Check:** `Playback settings.csv`: the base with `current` true has `short` "Modern".
- **Enforced by:** preset `all`: `base.current.short` "Modern"; check: fails on any other word.
- **Status:** Gettysburg, Trenton, Cowpens say "Today"; First Ypres, Manila, Luzon say "Now": A* for all six (F-3). **Session B (24 Nov, branch `presets-and-checks`):** done for all six (preset `all`).

## SR-27 Tactical battles share their settings unless a reason is recorded

- **Decided:** 24 Nov 2026 (Morgan's answer: "Align battlefield settings").
- **Rule:** the battles followed by the clock (Gettysburg, Trenton, Manila, Cowpens) use one value for deepest zoom, Follow's deepest zoom, blend minutes and the question-mark meaning, and each has the division view where it has divisions. A difference needs a recorded reason (scale, or the ground).
- **Scope:** tactical battles. **Built in:** `Playback settings`: `zoom.max`, `zoom.follow_max`, `rules.blend`, `question_mark`, `formations.*`.
- **Check:** the inventory table in `docs/playback-settings-inventory.md`.
- **Enforced by:** preset `tactical`: deepest zoom 8, Follow's deepest 2.2, blend 4 minutes, question mark = overall (Morgan's values, 24 Nov); Manila has the division view; check: lists every row where a battle differs from its presets and whether it gives a reason. Cowpens keeps Follow 2.4 (a small field). Gettysburg's `zoom.min_factor` was 0.96 (preset 0.9) with no recorded reason; Morgan chose to align it on 24 Nov (session C).
- **Status:** today Gettysburg 1.95 against Trenton and Cowpens 8 (Manila 1.6); Trenton blend 3 against 4; Gettysburg question mark `location` against `overall`; Manila has no division view. A* for the four; First Ypres and Luzon are operational: N. The values are to be chosen in the follow-up session, and Morgan is asked before they change (F-3). **Session B (24 Nov, branch `presets-and-checks`):** done (Morgan's values); one difference without a reason, Gettysburg `zoom.min_factor`. **Session C audit (24 Nov, evening): Morgan said align; the 0.96 row was deleted, so Gettysburg now takes the preset 0.9.**

## SR-28 Orientations: clashes drawn by who won, by shape as well as colour, from cited sources

- **Decided:** 25 Nov 2026 (Morgan's answers, Session 1 of `claude/sc-orientation-prompt.md`; approved the design the same day).
- **Rule:** an orientation shows no unit detail. Each clash is a crossed-swords symbol in the colour of the side that won: red British
  (a Loyalist win counts as British; the pane says Loyalist), blue American, black Cherokee (the legend word is "Cherokee", not "Indian").
  Colour is never the only cue: square British, circle American, triangle Cherokee, and a grey diamond where no side won. A post or stores
  taken with no fight recorded is a small flag in the taker's colour. Where the sources disagree the symbol carries a dagger; the result
  drawn is the one the sources settle on (SR-19) and the pane gives both readings with their sources; grey is only for a result that stays
  indecisive. A clash stands out (with a ring; larger until 26 Nov 2026) in its own month, then stays on the map **at full strength** (Morgan chose this over
  70% or fading), so the end shows the whole record. Where a fleet fought (Sullivan's Island 1776, Charleston 1780), a small ship mark in
  that side's colour stands beside the symbol (Morgan, 25 Nov 2026: orientations only; SR-08 is unchanged for battles).
- **Scope:** every orientation (Morgan, 25 Nov 2026: "Every orientation"). A later one that differs gives a reason, as with presets.
- **Built in:** shared player (`ORI` block in `app/player.js`); battle file `clashes` (docs/battle-file.md); workbook sheet `Clashes`.
- **Enforced by:** check (`orientation_rules` in `tools/consistency_check.py`): every result cites a source, a `stated` or `high` result
  has one (SR-21), and a disputed one cites the other reading's sources; the format check refuses a `won_by` that is not a side.
- **Status:** built and tested on made-up rows (pull request of 25 Nov 2026). South Carolina data comes in Sessions 2 and 3.
- **Corrections of 26 Nov 2026 (Morgan, after his first look at the live map):** the key no longer lists the ship mark or the dagger; ships
  and daggers stay on the map, and the side pane explains the dagger. Later the same morning the key also lost "Ring: this month" and
  "Town, no side on record yet" (Morgan); the ring and the town mark stay on the map. Month by month, a clash no longer swells and shrinks: it fades in at its
  own size and a plain ring marks its month ("the symbols 'pulse' ... that doesn't look good"). Found the same day: on a reconstructed map
  a style rule for its town dots painted every circle of the orientation dark brown, so American circles looked black and the month's ring
  was a dark disc; the orientation's circles are now exempt (class `os`). **Scope:** every orientation (Morgan, 26 Nov 2026, asked "all
  future orientations or only South Carolina?": "yes", all). Built in the shared orientation style.

## SR-29 Orientations: control of places, each change dated and sourced

- **Decided:** 25 Nov 2026 (Morgan's request: "showing the current state of which side controls which towns and villages").
- **Rule:** towns, villages, forts and ports each carry a small marker of the holder's shape and colour; contested (no side firmly holds it)
  is a hollow grey diamond. In South Carolina, Cherokee towns are a fourth state (black triangle) until the cession of 20 May 1777
  (Morgan, 25 Nov 2026). Each change of hands is a dated row with its basis, method, confidence and sources. The markers show throughout
  play (Battle options can hide them) and the closing pane lists who held what.
- **Scope:** every orientation. **Built in:** shared player; battle file `places`; sheets `Control places` and `Control`.
- **Enforced by:** check: every change of control cites a source; `stated` or `high` needs one (SR-21).
- **Correction of 26 Nov 2026 (Morgan: "Show towns on map from the beginning"):** towns, villages, ports and settlements show from the
  opening view, with their names, as a plain town mark (no side) until a change of control is on record; a fort or post shows once it is on
  record. This is an exception to SR-02's empty opening field: the towns are part of the map, the clashes still wait for play. A place's
  marker no longer swells when it changes hands. **Scope:** every orientation (Morgan, 26 Nov 2026: "yes", all future orientations); built in
  the shared orientation style.

## SR-30 Orientations: month by month, busy months slower, one stop at the end

- **Decided:** 25 Nov 2026. Morgan first asked for "a pause at each year"; asked again, he chose **one stop at the end only** (confirmed
  the same day). Busy months play slower (his yes): about a second a month plus half a second for each event in the month, at speeds of 2,
  1 and ½ seconds a month. Gaps in the list (South Carolina 1777 and 1778) are not filled from other lists: they are flagged on the timeline,
  on the map and in the year's summary (Morgan, 25 Nov 2026).
- **Rule:** the clock shows the month; the forward and back buttons move a month. Each year has a summary, shown in the pane while that
  year plays; the stop at the end shows the closing summary, the wins by side and year, and who held what. It opens on its own base map,
  zoomed out and with no symbols, and eases in when play is pressed (SR-02, SR-04); the camera stays on the whole state (no Follow, SR-18 N).
- **Correction of 25 Nov 2026 (afternoon), South Carolina only (Morgan: "South Carolina only"):** 1775 to 1777 plays event by event, each event half a second after the one before; the playback stops at the end of 1777 with a recap of 1775 to 1777 (the year summaries, the gap, who held which places); Continue runs it month by month from 1778. Set in South Carolina's own Playback settings rows (`orientation.phases`, until 1777-12-31), not in the preset, so other orientations stay month by month with one stop at the end.
- **Correction of 26 Nov 2026, South Carolina (Morgan):** the event-by-event stretch is replaced by a **year reveal for 1775 to 1779**: all of
  a year's clashes come on together, grow slowly into a large symbol and ring, the map stops while a bubble beside each gives the date and
  what happened (3 seconds, between half-second fades), the bubbles fade and the symbols shrink to their standard size; then the next year.
  1777 and 1778, with no clash drawn, hold for the same time on their gap notes. The recap stop moves to the end of 1779; from 1780 the map
  runs month by month. The forward and back buttons move a year until 1780. Set in South Carolina's own Playback settings
  (`orientation.reveal`; `orientation.phases` removed). On a phone the bubbles give the date, the name and who won only.
- **Second correction of 26 Nov 2026, South Carolina (Morgan):** "At the end of 1776, move steadily over 2 secs to 1779": 1777 and 1778 (no
  clash drawn) get no reveal of their own and are crossed together in 2 seconds (`empty_seconds` 2). "Eliminate the 'continue' button":
  no recap stop at the end of 1779 (`stop` false); 1780 runs month by month straight on. 1779 is revealed like the years before it.
- **Third correction of 26 Nov 2026, South Carolina (Morgan):** month by month from 1780, each month with a clash stops at its end with a
  bubble on each of its clashes, as the years before (`months` true; the symbols keep their size, so nothing pulses). A stop with three or
  more bubbles lasts 5 seconds, otherwise 3 (`many` 3, `hold_many_seconds` 5; years and months). 1777-1778: one box on the map, "Relative
  calm and little military activity on land in South Carolina in 1777-1778", for 3 seconds, then the 2-second crossing to 1779
  (`empty_text`, `empty_hold_seconds` 3); the map's gap notes give way to it there, the pane keeps them. The main roads are named on the
  map like the rivers (Labels, kind `road`; short forms of the traced roads' names, approximate), the name set just above its road.
- **Scope:** every orientation. **Built in:** preset `orientation` (`day_pause` false, `orientation.month_seconds` 1,
  `orientation.event_seconds` 0.5, `orientation.speeds` [2, 1, 0.5], `opening_ease` 0.006); shared player.
- **Enforced by:** check: an orientation that pauses during play fails; a year without a summary, or no closing summary, is a warning.

## SR-31 Reconstructed maps follow the clock

- **Decided:** 25 Nov 2026 (Morgan's answer, Session 4 of `claude/sc-orientation-prompt.md`: "Yes, every reconstruction (Recommended)").
- **Rule:** a line of a reconstructed map is drawn only on the days its `from` and `to` cover, compared by the day: a fort comes on when it was
  built, a boundary goes when the land was ceded, siege lines show only in their year.
- **Scope:** every reconstruction. Manila's and Cowpens's lines cover their battles' days, so they look as before (screenshots, 25 Nov).
- **Built in:** shared player (`rcDateTick` in `app/player.js`: the date is added to every layer's filter of a reconstruction).
- **Check:** open the South Carolina orientation in 1776 and in 1778: the Cherokee boundary shows, then is gone.
- **Enforced by:** player.
- **Also decided in Session 4 (South Carolina only):** the Cherokee boundary as Mouzon draws it, to the cession of 20 May 1777, and no inferred
  settlement line; the close-up ink of a Charleston siege plan, like Manila's 1898 plan, to be added after Morgan has judged the look of the pilot.

## SR-32 Orientations: forces on the move, one symbol a side

- **Decided:** 26 and 27 Nov 2026 (Morgan, 26 Nov: "I don't need to see subordinate units for these movements. Just one unit symbol per side
  for each of the movements/engagements"; 27 Nov, Session 1 of `claude/sc-storyline-prompt.md`, the design approved the same day).
- **Rule:** a movement in an orientation is one symbol per side, the force as the sources name it, its commander as the label: the battles'
  unit frame in the side's colour with its branch mark and an army or detachment mark, so it is never taken for a clash. Mounted riflemen who
  fought on foot are **Dragoons** (Morgan's words: "use the word 'Dragoons'. Use a infantry cross and inside the rectangle a small horse
  shoe"). While a force moves the clock runs a day at a time (0.3 s a day) and the date shows; months again once no force moves (five more
  days first, so the route can fade). All forces on the move are drawn **at full strength** (not the battles' 70%, SR-11). The route follows
  Mouzon's road where a source names the road, otherwise a straight dashed line; both `inferred` and `low` unless a source describes the
  road. When a movement reaches its fight in 1a the symbol leaves, the route fades and the clash stays; in a campaign (1c) the armies stay on
  the map. A force beyond the screen shows at its edge with its name and where it set out from; no new events are added for its start.
  A reveal year with a force on the move plays its months, and a clash a force marches to comes on as it is reached; the year's reveal follows.
- **Scope:** every orientation (Morgan, 27 Nov 2026: "Every orientation" for the symbol, Dragoons, routes, full strength and the edge).
  The choice of movements for South Carolina (M1 to M8, M3 Waxhaws only with a route, M7 as standing pairs) is this chapter's.
- **Built in:** shared player; preset `orientation` (`event_dim` 1, `orientation.move_day_seconds` 0.3, `move_tail_days` 5, `trails.fade_after`
  2 and `fade_over` 5 days); exporter (`via_basis`, Routes `along_recon`, a straight route for a force with none on record); format (`dragoons`).
- **Status:** built and tested on made-up rows (`tests/orientation/make_demo.py`). South Carolina's movements come in Sessions 3 and 5.
- **Carry-forward:** SR-06, SR-07 and SR-16 (arrows ahead of long moves, their reach, routes taken) now reach orientations through the forces
  on the move, at campaign scale (arrows only for moves over 20 km); SR-11's 70% is replaced in orientations by full strength.

## SR-33 The connection rule: every movement meets an event on the map

- **Decided:** 26 Nov 2026 (Morgan: "Each movement should connect in timing and location with the actions/events currently on the map");
  made a check 27 Nov 2026.
- **Rule:** every force on the move is tied to at least one event: an event names one of its waypoints (Events `pos_ids`); that waypoint is
  at the event's clash, or at the place whose change of hands the event is, within the larger of the two `precision_m`; and its dates overlap
  the event's. Waypoints are steps, not new events. Where a waypoint reaches a place with a Control row held then by the other side and no event
  ties them, the arrival must not contradict the row: shown to Morgan, neither changed quietly.
- **Scope:** every orientation. **Enforced by:** check (`movement_rules` in `tools/consistency_check.py`: fails; the control case warns). The
  made-up test moves a waypoint 48 km off its fight and the check catches it.

## SR-34 Campaign orientations play in legs

- **Decided:** 27 Nov 2026 (Morgan: "for 1c use text callouts and symbols like you used for 1a"; the six legs of 1c; the design approved
  with 0.5 s a day).
- **Rule:** a campaign orientation plays in named stretches of days (Summaries kind `leg`), 0.5 s a day, each ending in a stop with a bubble on
  each of its clashes and on each force whose waypoint carries a callout (3 s, 5 s with three or more), then runs on by itself (SR-30: no
  Continue). The pane shows the leg's summary and its events; back and forward move a leg. At its end the clashes fade and the places fly
  their flags (SR-28), then the closing summary, the bridge and Next.
- **Scope:** every orientation that has legs. **Built in:** player; preset `orientation.legs.day_seconds`; format (`leg`, step `callout`).
- **Status:** built and tested on made-up rows; 1c's legs come in Sessions 4 and 5.

## SR-35 The storyline gate: a summary, a bridge and Next at the end of every section

- **Decided:** 27 Nov 2026 (Morgan: "At the end of 1a to 1d, there should be a summary and have the user click 'next' to move to the next
  section of the campaign"; Next "on the map and in the pane").
- **Rule:** every playback in a chapter, battles included, ends with an end summary whose last paragraph (the bridge, "What came next")
  leads on to the next section; a Next button shows on the map and in the pane once the clock reaches the end; the next playback's opening
  picks up the thread. The last of a chapter leads back to its course page. The transitions are these, not extra screens.
- **Scope:** every course chapter. **Enforced by:** player; `tools/build.py` for a chapter marked `"gate": true` (every playback built, an
  end summary with a bridge, linked both ways, the last to the course page); the South Carolina chapter is marked in Session 5.

## SR-36 A regional map under a battle (option B)

- **Decided:** 27 Nov 2026 (Morgan: "Maps should be able to zoom out so the viewer can see a large scale. For this work it should include South
  Carolina, North Carolina and Southern Virginia"; he chose option B after seeing the prototype on Cowpens; the window 84.9° W to 75.5° W,
  30.9° N to 37.6° N).
- **Rule:** a battle in a chapter with a regional map keeps its own reconstructed battlefield; under it lies the regional map, to which the
  reader can zoom out. The battlefield fades in as the reader closes on the field, and each side is one symbol when zoomed out. Arriving from
  Next, the battle opens on the region and eases in (SR-02, SR-04).
- **Scope:** battles in a chapter that has a regional map (Cowpens and Guilford Courthouse: A*, the data comes with the regional map in
  Session 2). **Built in:** player (`bases[].region`); exporter (a reconstruction another playback owns, and its names); format check.
- **Data (Session 2, 27 Nov 2026):** the regional map is `sc-1775`, extended to North Carolina (to 77° W and the Dan). Cowpens and Guilford
  Courthouse: `bases.1.region` = `rgn`, a hidden base `rgn` (recon `sc-1775`, terrain over the window at tile zoom 8), `groups` one symbol a
  side ("Morgan's detachment" and "Tarleton's detachment"; "Greene's army" and "Cornwallis's army"), `opening_zoom_out` 4. 1a's terrain covers
  the same window at zoom 9. Measured on an emulated phone: 1a 30.8 s and 17 MB to the relief (main: 22.5 s, 12 MB); Cowpens 15.4 s, 10 MB.

## Orientations: which rules reach them (carry-forward check of 25 Nov 2026)

Checked at the start of Session 1 of `claude/sc-orientation-prompt.md`, and shown to Morgan before his answers.

- **Apply as written:** SR-01 (dates written "21 Apr 1775"), SR-02, SR-03 and SR-26, SR-04, SR-09, SR-12 to SR-14 (for the reconstructed
  base map of Session 4), SR-15, SR-19 to SR-25.
- **Session 4 (25 Nov 2026, branch `sc-orientation-base-map`):** the reconstructed base map is built as a pilot: it is the main map on the menu and the
  page opens on it (SR-02, SR-15), with terrain from today's elevation labelled as today's ground (SR-14), no banner (SR-13), credits in the i
  button (SR-09) and Mouzon's own map, fitted, in the map details. SR-12 (detail at every zoom) is not yet met: only the main lines are traced.
- **Carried over in a new form:** SR-05 day pauses became SR-30 (one stop at the end); SR-11 (70% strength) became SR-28's full strength for
  past clashes, at Morgan's choice; SR-17 (events tied to units) became events tied to their clash or place (BP-35); SR-08 ships became the
  ship mark of SR-28.
- **Not applicable (no units):** SR-06, SR-07, SR-10, SR-16, SR-18, SR-27, F-8.
- **Still open from before, not touched:** the main maps of Trenton, First Ypres and Luzon, and the satellite view (both "decide later").

## Project-wide rules (no per-battle status)

- Wording: "battlefield study guide" or "military history map study guide"; audience "service members" (not "tour guide" or "military officers"). Memory, 13 to 15 Nov 2026.
- Licence: all rights reserved, copyright holder Starfishient LLC; public to read, not to reuse. Memory, 17 Nov 2026.
- Work on a branch, open a pull request, don't merge. Ask Morgan before stacking on an unmerged branch. Prompt of 24 Nov.
- Model rule: Sonnet default; Opus or Fable before changing the format, the workbook schema or shared playback rules, or setting a position from conflicting sources; after two failed fixes, move up a tier. Project instructions.
- Morgan's folder on the Mac is `Documents/Starfishient/WarMapper`; the workbooks are in the repo under `data/WarMapper battle data/`.

## Answers from Morgan (27 Nov 2026): the South Carolina storyline

Session 1 of `claude/sc-storyline-prompt.md` (branch `sc-storyline-design`). Four batches, the prototype of the regional map, then the design
(`claude/sc-storyline-session1-design.md` in the Project), approved: "Approve, build it".

- The storyline: four sections (1a the orientation to 17 Jan 1781, 1b Cowpens, 1c Greene and Cornwallis to Guilford, 1d Guilford
  Courthouse); the transitions are the bridge, Next and the next page's opening. Scope: this chapter.
- 1a's movements: M1, M2, M4, M5, M6 and M8 moving; M3 Waxhaws with a route if the sources give one; M7 as standing pairs. Scope: this chapter.
- Pacing: a day at a time inside a movement, 0.3 s a day. When it ends: the symbol leaves, the route fades, the clash stays. The symbol:
  the unit frame with an army or detachment mark. The Overmountain Men: "Dragoons", the infantry cross with a horseshoe inside. Routes:
  along Mouzon's road where named. Overlaps: all at full strength. Entering: from the edge, with where they came from. Scope: every
  orientation ("Every orientation", asked for these together) (SR-32).
- 1c: Greene's army (Morgan's detachment until 30 Jan) and Cornwallis's army; Williams's light corps a second symbol, 8 to 14 Feb; the six
  legs; Cowpens and Guilford as markers on 1c; control places Cheraw, Salisbury, Hillsborough, Charlotte and Halifax. Scope: 1c.
- Next: on the map and in the pane; Guilford's returns to the course page. Scope: every chapter (SR-35).
- The zoom-out: option B, the regional map under the battles; the window 84.9° W to 75.5° W, 30.9° N to 37.6° N (SR-36).
- Flags at the end: every orientation, at its closing stop (the open question of 26 Nov, closed).
- Guilford Courthouse: all three choices confirmed (every position low; the retreating Continentals one symbol; the empty margin south of
  New Garden). The four Cowpens choices "ask again": far places at the edge (now SR-32's edge), other maps in the i button (apply), broken units
  off the map (not applicable), a column as one symbol (now one symbol per side).
- Priority of the five new requirements (movement symbols, the connection rule, legs, the storyline gate, the regional base): all P1.
- Not asked, stated in the design: SR-05's day pauses do not reach orientations (the legs stop by themselves; SR-30).

## Session 2 of the SC storyline (27 Nov 2026): the regional base map, for Morgan to look at

Branch `sc-storyline-regional-base`. No new rule and no answer yet; what was built, and what is asked.

- `sc-1775` now holds North Carolina: 23 new features (ids NC75-), the rivers Catawba, Broad, Yadkin to the Pee Dee, Haw, Reedy Fork,
  Troublesome Creek, Deep, Cape Fear, Dan and Roanoke; the coast to 77° W; the Virginia line; ten roads of the 1781 campaign's ground. Sheet
  83.45° W to 77° W, 31.95° N to 36.75° N. Every feature `traced`, `low` or `medium`, with its basis; nothing `high`.
- South Carolina did not move: the fit is extended with every reviewed South Carolina vertex held where it was (largest move 20 m).
- Mouzon's neatline (36° 37′) is about 10 km south of the lower Dan ferries; he draws the Dan and Roanoke on into the margin, which is traced.
- Morgan's answers (27 Nov 2026, evening), scope this chapter's regional map:
  - **The Catawba fold: "fix it".** Done: the 26 Nov fit had matched Mouzon's Catawba below the 1772 line to the river above today's state
    line. Refitted with a control where today's state line reaches the Catawba. The Catawba and the road from the Catawba Nation to Charlotte
    move up to 18.6 km, the Cherokee path's east end 11 km, the 1772 and 1764 lines up to 12 km, and the Broad above the Pacolet 6.8 km.
    Everywhere else South Carolina moves at most 20 m.
  - **A Virginia map above Mouzon's edge: "add it".** Done from Fry and Jefferson (S152, drawn 1751; LoC printing of 1755): the Staunton,
    Banister, Meherrin, Nottoway and Appomattox and the Great Wagon Road, 36.75° N to 37.6° N, fitted on Richmond, Petersburg, City Point,
    two ties to Mouzon and the rivers matched to today's. Fry and Jefferson draw almost no roads in the southside, and nothing at the Dan
    ferries of 1781.
  - **PRD and tracker: "add them".**

## Answers from Morgan (26 Nov 2026): Guilford Courthouse

Session 4 of `claude/hist-340-build-prompt.md` (branch `guilford-courthouse`). Asked before building, as the carry-forward check requires.

- Main map: the reconstructed 1781 map, as at Cowpens (SR-02, SR-15). Scope: Guilford Courthouse; the rule itself is every battle's.
- Where it starts: with the morning fights near New Garden (Lee against Tarleton), not at the cannonade. Scope: Guilford Courthouse only.
- The four choices made for Cowpens were each asked again, and all four apply: places far off the map are shown at its edge with an arrow and a
  distance; the other maps are offered in the map details (the i button), not on the menu; units that break are taken off the map; a column
  on the march is one symbol until it deploys. Scope: Cowpens and Guilford Courthouse. Ask again for the next battle.
- The chapter: Cowpens leads on to Guilford Courthouse for now (`Next links` row N02). Morgan also asked for a map of Greene's and the British
  movements between the two battles: that is the campaign playback, to be built in Session 5 "as planned", when N02 is replaced by two rows.
- The "pilot report" on Cowpens could not be found (repo, Project, Morgan's folder). Morgan approved a list of its improvements rebuilt from the
  Cowpens follow-up work, to be used for every battle built for HIST 340 from now on:
  1. read the National Park Service's troop movement study first, and take positions from its plans where it has them;
  2. rate cautiously, and audit the ratings and the page citations before the pull request, not after;
  3. check where each source prints its page numbers (a scan that prints them at the foot shifts every citation by one);
  4. build the reconstructed map, the other maps, the opening hold and the column settings in the same session as the positions.
- Sources: Morgan downloaded the copies himself (`Historical Info/History 340/Guilford Courthouse`); Babits and Howard (2009) and Baker
  (1981) could not be had and were not read.

Decisions the session made, confirmed by Morgan on 27 Nov 2026 (Session 1 of `claude/sc-storyline-prompt.md`):
- Every Guilford position is rated low (the plans are good to about 75 m on today's ground, and none of the accounts fixes a place closer).
- The retreating Continentals are shown as one symbol on the Reedy Fork road ("a column on the march is one symbol", carried to the retreat).
- The reconstructed sheet has an empty margin south of New Garden, so its title does not lie on the morning fights.

Notes for whoever builds the next battle:
- Ids are shared by all the war workbooks: a new battle's phase, event and route ids must not repeat another war's (Gettysburg already uses
  `PH-G`, `GE` and `RG`; Guilford Courthouse uses `PH-GC`, `GCE` and `RGC`). The exporter stops and says so.
- `python3 pipeline/checks/quote_check.py` checks every quotation in a battle's script against the texts read, with its page (item 2 above).

## Answers from Morgan (25 Nov 2026): the South Carolina orientation

Two batches and a design approval, Session 1 of `claude/sc-orientation-prompt.md`.

- Where it ends: at Cowpens, 17 Jan 1781, with control as it stood that day. Rows T40 to T50 go into the data as a later second stage.
- Black is labelled "Cherokee"; Cherokee towns are a control state of their own until May 1777.
- Disputed results: settled by the sources (SR-19), grey only where indecisive; a capture with no fight is a flag.
- Loyalist wins count as British. The 1777 and 1778 gap is flagged, not filled from the SC Archives list.
- Past clashes stay at full strength. Pause only at the end (replaces "a pause at each year"); busy months slower.
- Ships: a small ship mark at Sullivan's Island and Charleston.
- The design approved ("Approve, build it"). Scope of all of the above: every orientation.
- Correction, the same afternoon: South Carolina plays 1775 to 1777 event by event (half a second each), stops at the end of 1777 with a recap of those years and who held what, then runs month by month. Scope: South Carolina only.

## Answers from Morgan (26 Nov 2026): corrections to the South Carolina map

After his first look at the live orientation.
1. Towns show from the beginning (SR-29).
2. Asked what the black solid and dashed lines are: the solid lines are the main roads of 1775 traced from Mouzon; the dash-dot lines are
   the boundaries (the Cherokee line of 1766-67, gone after the cession of May 1777, and the lines with North Carolina of 1764 and 1772).
3. and 4. 1775 to 1779: each year's events at once, growing into a large circle, a 3-second stop with dated bubbles, then shrinking (SR-30).
5. The key loses the ship and the dagger; the dagger is explained in the side pane (SR-28).
6. The 1780 symbols "pulse": the month's clashes swelled and shrank each month, and on the reconstructed map their rings were drawn as dark
   discs (SR-28). Fixed.
Scope: the year reveal is South Carolina's own setting. Towns from the start, the shorter key and the steady month-by-month symbols apply to
every orientation (Morgan's answer the same morning: "yes" to all future orientations).

Later the same morning (26 Nov 2026):
- 1777 and 1778 crossed steadily in 2 seconds; no Continue stop at the end of 1779; 1779 revealed like the years before; 1780 month by month (SR-30).
- The key loses "Ring: this month" and "Town, no side on record yet" (SR-28; all orientations, as his earlier answer).
- Asked whether clicking a battle showing nothing in the pane was by design: no, a bug. On the reconstructed map the click was taken over
  by the traced river or road under the symbol, and where a battle sat on a town the town won. Fixed for every orientation: a battle is
  picked first, then a place, and a traced line only when neither is under the click.

Afternoon (26 Nov 2026): the 1775 base map re-traced and refitted (Morgan: "yes do that job"; run on Opus, project rule 2).
- Asked why some roads took odd angles (above the Catawba Nation): the tracing was right; Session 4's fit of Mouzon's map folded the ground
  over on itself there (303 points along the traced lines, 26 on roads). The refit (`pipeline/georef/sc_mouzon_refit_2026_11_26.py`) drops
  the pairs on 20th-century reservoirs and on the Pee Dee, Little Pee Dee, Waccamaw and Black, stiffens the fit, and adds seven towns as
  controls and two ties across the eastern gap of the scan. No road turns back on itself now.
- The trade: every control is held within 0.5 km (Georgetown and Winyah Bay a few km), but left out in turn a control is found again a
  median 5 km off (Session 4: 1.1 km, folds and all). Roads are now given as good to about 1 km at the towns and 3-5 km between them
  (`precision_m` 4000, confidence low); the Pee Dee, Little Pee Dee and Waccamaw drop to low.
- All 13 roads snapped to Mouzon's double lines from end to end (two had followed a river or a creek); road ends joined to the town or road
  they meet; each river one line across the scan's mounted sections (Lynches Creek was in three pieces).
- Still open: the Congarees. Mouzon's "Old Fort" lies north-west of the Broad and Saluda's meeting as traced, Fort Granby south of it on the
  ground; the meeting or the fort is misread, so the Congarees is not a control and the roads there end some 9 km from the workbook's Granby.

Midday (26 Nov 2026), after pull request 84 was merged: "At end of 1780. Fade out all the actions to the default fade %. Show which towns
are controlled by British with a small Union Jack wavy flag, or the Americans with the original American wavy flag."
- Built as `playback.orientation.flags` (South Carolina's own row, from 1780-12-31). At the end of 1780, after December's bubbles, the map
  stops: the clashes so far fade to the standard 70% (SR-11's `event_dim`), and each place held by one side takes its flag. The British flag
  is the Union flag as it was in 1780 (no St Patrick's cross until 1801); the American is the Stars and Stripes of 14 June 1777, 13 stars in a
  ring. Contested places keep the grey diamond. Forts and posts take flags too, like the towns. Clashes of January 1781 come on at full strength.
- Later the same day: "Fade the action symbol more. Make the flags 10% bigger." The clashes now fade to 40% (`dim` 0.4, South Carolina's
  own value, not the battles' 70%) and the flags are drawn 10% larger (`scale` 1.1).
- Scope: South Carolina only for now (Morgan: "for now do this just for South Carolina but keep it as an open question").
- **Open question:** should every orientation fade its clashes and fly flags at the end of its last full year? **Answered 27 Nov 2026:
  every orientation, at its closing stop** (South Carolina keeps its stop at the end of 1780). Built in the preset `orientation` (clashes to
  40%, flags 10% larger); a playback names its sides' flags.

## Answers from Morgan (24 Nov 2026)

Batch 1 (four questions) and a follow-up (three questions), both answered the same evening.

**Cowpens-only fixes: make them the same everywhere?**
- Symbols at 70% strength: yes, every battle (SR-11).
- Slow hold, then ease in: yes, every battle (SR-04).
- Routes-taken lines on Gettysburg, First Ypres and Luzon: yes (SR-16).
- Arrows run just ahead of the unit: not ticked; Morgan wrote "Arrows will run ahead depending on the time scale being used" (SR-07).

**Maps and menus**
- One main map on the Type of map menu for every battle: yes (SR-15).
- Open on the reconstruction: yes; of his order "reconstructed, modern topo, period map" he then chose "reconstruction first, then the 17 Nov rule" (SR-02).
- Current-map button word: "Modern" (SR-26; typed in Other).
- Satellite view for First Ypres, Manila and Luzon: not ticked. **Open: decide later** (needs a non-US imagery provider and a rights check; PRD already lists Ypres imagery as unresolved).

**Sources and wording**
- Boats at Trenton and ships at Ypres where sources support them: yes (SR-08).
- Convert the nine a.m./p.m. texts: yes (SR-01).
- "Times are estimates" note: not on any map (SR-25). Morgan did not tick it as a thing to add; he wrote that it should not show.
- Scholarly history wins: after the explanation, "only if it cites the reports" (SR-19).

**Technical**
- Align battlefield settings: yes (SR-27). Scale the arrow limit with the battle: yes (SR-06). Name First Ypres's event rows: yes (SR-17).
- Open a pull request for the stuck pull requests 67 and 68: yes (F-1). Done the same evening: pull request 70, merged.

## Follow-ups

Model per the project rules in brackets. Each is a separate session or pull request; the register's A* entries point here.

- **F-1 (done, 24 Nov):** pull request 70 carried pull requests 67 and 68 (Cowpens far-town labels, Cowpens second review, the shared rule that a route fades once its unit moves on) from `cowpens-orientation-towns` onto `main`; Morgan merged it with pull request 69.
- **F-2 (done on branch `presets-and-checks`, session B, 24 Nov; Opus):** shared player and exporter: default symbol strength 0.7 (SR-11); hold-then-ease opening for every battle, including those without Follow (SR-04); arrow limit and arrow reach that scale with the battle's size and time scale, with values for Gettysburg and Trenton agreed with Morgan (SR-06, SR-07); a default start map that prefers the battle's reconstruction (SR-02).
- **F-3 (done: on branch `presets-and-checks`, and the a.m./p.m. texts in the session C audit; values for SR-27 chosen by Morgan, 24 Nov):** routes layer for Gettysburg, First Ypres, Luzon (SR-16); hide the extra period maps for Trenton, First Ypres, Luzon (SR-15); button word "Modern" on all six (SR-26); remove `time_note` from Trenton and Cowpens (SR-25); align battlefield settings (SR-27); convert the a.m./p.m. texts (SR-01: done in the session C audit, 24 Nov); run the export so `csv/Philippine War/Positions.csv` is current (SR-23).
- **F-4 (Opus; ties events to position rows):** name the position rows behind First Ypres's 15 events (SR-17). Then SR-11's 70% applies there too.
- **F-5 (Fable or Opus; needs sources):** Delaware boats at Trenton and naval gunfire at First Ypres, with units, sources and confidence (SR-08).
- **F-6 (Opus; conflicting sources):** re-read every battle's Hypotheses rows against SR-19; Gettysburg C03, C13 and Trenton TC14, TC15 first.
- **F-7 (Sonnet or Opus; needs sources):** routes for First Ypres's moves (Routes sheet, `playback` yes), so its routes-taken layer draws something (SR-16).
- **F-8 (Opus; changes the shared rules; asked 24 Nov, session C, Morgan: scale it with the battle):** make the arrow lead time scale with the battle like the reach (SR-07) by a preset. Today Gettysburg and Trenton use the player's default of 45 minutes, First Ypres 3 days (default), Manila 30 minutes, Cowpens 3 minutes, Luzon 1899 4 days; the three explicit values have no reason written. Propose values to Morgan before building; the check should then compare the lead with the preset.
- **Answered, 24 Nov (session C): Gettysburg's `zoom.min_factor` 0.96 against the tactical 0.9: align.** Done.
- **Ask Morgan (asked again 24 Nov, session C; Morgan: decide later):** the main map chosen for Trenton (Faden 1777), First Ypres (the sketch of the day) and Luzon (Siebert 1899) on 24 Nov (session B); to change one, move the `hidden` row to the other base.
- **Open, decide later (asked again 24 Nov, session C; Morgan: keep deferred):** satellite view for First Ypres, Manila and Luzon. Needs a non-US imagery source and a rights check; the three battles stay recorded as without it.

## Audit of 24 Nov 2026, evening (session C)

Run on `main` after pull request 72. Rebuild from the workbooks: all six current. Before the edits the check reported eight failures, all SR-01. Warnings left: opposing symbols within 50 m (Trenton 17, Gettysburg 11, Cowpens 63: where the lines meet in the fighting); implausibly fast moves (Luzon 9, Gettysburg 1: the Luzon ones are ship, transport and long-column moves, which the check does not yet allow for); SR-17 First Ypres 15 of 15 events without rows (F-4). A gap the check could not see: per-battle settings that no preset covers (arrow lead) have no reason written, so they are not listed as differences; F-8 closes it for the arrow lead.

Morgan's answers: Gettysburg zoom-out limit, align to 0.9 (done). Arrow lead, scale with the battle (F-8). Main maps for Trenton, First Ypres and Luzon, decide later. Eight a.m./p.m. texts, yes as proposed (done). Satellite view, keep deferred. First follow-up to run: F-8.
