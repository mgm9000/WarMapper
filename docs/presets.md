# Playback presets

Since 24 Nov 2026 (session B of `claude/consistency-rules-prompt.md`). The rules every battle shares live in one place, and a battle
says only where it differs, and why.

## How it works, in plain words

- The sheet **Playback presets** in `Sources and notes.xlsx` holds named sets of playback settings (columns: preset, setting, value, what it
  does, why). The settings are the same ones a battle's **Playback settings** sheet uses (`claude/battle-file-format.md`, section playback).
- Each battle has one row `based_on` in its war's **Playback settings**: the presets it takes, e.g. `["tactical", "us-maps"]`.
  The preset **all** comes first for every battle without being named. Then each named preset is laid on in turn (a later one wins), then
  the battle's own rows (the battle wins).
- A battle keeps a row only where it differs from its presets. The **why** column says why. `python3 tools/consistency_check.py` lists
  every such row and says which have no reason.
- Standard maps for the Type of map menu: a preset's `base.<name>.*` rows describe one (`base.current`: the Current map;
  `base.satellite`: the USGS aerial photography). A battle's `bases.N.use = <name>` takes it, with its own `bases.N.*` rows for what differs
  (its `id`, a `clip`).
- Some values are worked out from the battle itself, so they scale with it without anyone choosing a number: see "Worked out from the
  battle" below.
- `tools/export_battles.py` does all of this when it writes the battle file. The battle file reads as if the battle had set everything
  itself: the format (`warmapper-battle/1`) and the player are not changed by presets.

## The presets

| Preset | For | What it holds |
|---|---|---|
| `all` | every battle | The Current map's place on the menu and its button word "Modern" (SR-03, SR-26); symbols outside the current event at 70% (SR-11); the routes-taken layer, fading after 4 seconds of play (SR-16); arrows on, running 6 seconds of play ahead (SR-06, SR-07) |
| `tactical` | battles followed by the clock: Gettysburg, Trenton, Manila, Cowpens | Style, yards scale bar, question mark = overall, deepest zoom 8, Follow's deepest 2.2, zoom-out limit 0.9, blend 4 minutes (SR-27); the slow ease in, 14 s at 0.006 (SR-04); arrow limit 6% of the battle's width (SR-06). It turns Follow on: a battle followed by the clock has it |
| `operational` | battles followed by the day: First Ypres, Luzon 1899 | Style, km scale bar, question mark, zoom-out limit 0.85; the slow ease in without Follow, `opening_ease` 0.006 (SR-04); arrow limit 20 km (SR-06) |
| `us-maps` | ground in the United States: Gettysburg, Trenton, Cowpens | The USGS topographic map (the modern map) and the USGS aerial photography (`base.satellite`) |
| `world-maps` | ground elsewhere: First Ypres, Manila, Luzon 1899 | OpenTopoMap as the modern map |
| `civil-war` | Gettysburg (and the next Civil War battle) | March pace by branch |
| `orientation` | orientation playbacks (since 25 Nov 2026; the first is the HIST 340 South Carolina chapter's opening, to come) | Style `orientation`, km scale bar; no pause during play, one stop at the end (Morgan, 25 Nov 2026); the slow ease in, `opening_ease` 0.006 (SR-04); zoom-out limit 0.85 and closest zoom 0.3; about a month a second, plus half a second for each event in the month, at speeds of 2, 1 and ½ seconds a month (Morgan, 25 Nov 2026); since 27 Nov 2026 (Morgan, every orientation): all symbols at full strength (`event_dim` 1), a day at a time while a force moves (0.3 s a day, 5 more days for its route to fade, routes fading 2 days after over 5), legs at 0.5 s a day, and flags at the closing stop (clashes to 40%, flags 10% larger) |

There is no preset yet for the Revolutionary War, the Philippine War or the First World War: their battles share nothing beyond the presets
above. The next battle of a war is the time to start one (Guilford Courthouse for the Revolutionary War, say), with what it shares with the
battle before it.

## Where a battle differs, and why (24 Nov 2026)

| Battle | Differs in | Why |
|---|---|---|
| Trenton | routes fade after 10 minutes, over 10 | Morgan's decision when the fade was made (19 Nov) |
| Manila | arrow limit 0.7 km; routes fade 120 and 60 minutes | The 21 Nov trial; kept as set while reviewing Manila (Morgan, 24 Nov) |
| Cowpens | arrow limit 0.25 km; Follow's deepest 2.4; routes 6 and 6 minutes, opacity 0.5; the modern map's and the aerial photograph's About text | A field half a mile long; a small field; kept as set while reviewing Cowpens (Morgan, 24 Nov); the text says what is particular to this ground |
| Luzon 1899 | the modern map's About text | Says "campaign" for "battle" |

`python3 tools/consistency_check.py` prints this list from the workbooks as they stand.

The full list of values is the sheet itself (and its CSV copy, `data/WarMapper battle data/csv/Sources and notes/Playback presets.csv`).

## Worked out from the battle

A preset may give one of these; the battle file gets the value worked out, never the preset's number itself. A battle that sets the value
itself keeps its own.

| Preset setting | Gives | How |
|---|---|---|
| `arrows.min_share` | `arrows.min_km` | That share of the width of the battle's ground (the east-west size of `view.extent`) |
| `arrows.reach_seconds` | `arrows.reach_minutes` | That many seconds of play at the opening speed (`rate`), in the battle's time unit |
| `trails.fade_seconds` | `trails.fade_after`, `trails.fade_over` | That many seconds of play at the opening speed |

## Adding a battle

Give it a `based_on` row (one of `tactical`, `operational` or `orientation`, and one of `us-maps` or `world-maps`, and its war's preset if there is one),
its Current map as `bases.N.use = current`, and only the rows its data needs (titles, texts, views, Follow box, label zooms, maps).
Anything else it sets is a difference from the presets and needs a `why`.

An orientation (another state, another war) is data only (since 27 Nov 2026 also its forces on the move: Units, Tracks, Positions, Routes and the Events `pos_ids` that tie each to its event; a campaign's legs on the Summaries sheet; its sides' flags in `orientation.flags.sides`): its Playbacks row (time unit `day`), `based_on` ["orientation", "us-maps"] (or
`world-maps`), its Current map, its events, and rows on the Clashes, Control places, Control and Summaries sheets (docs/battle-file.md:
clashes, places). `tests/orientation/make_demo.py` builds one from made-up rows, as a worked example.
