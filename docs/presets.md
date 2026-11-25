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
| `all` | every battle | The Current map's place on the Type of map menu |
| `tactical` | battles followed by the clock: Gettysburg, Trenton, Manila, Cowpens | Style, scale bar, what a question mark means, deepest zoom, Follow's deepest zoom, how far out the reader can zoom |
| `operational` | battles followed by the day: First Ypres, Luzon 1899 | Style, scale bar, question mark, how far out the reader can zoom |
| `us-maps` | ground in the United States: Gettysburg, Trenton, Cowpens | The USGS topographic map (the modern map) and the USGS aerial photography (`base.satellite`) |
| `world-maps` | ground elsewhere: First Ypres, Manila, Luzon 1899 | OpenTopoMap as the modern map |
| `civil-war` | Gettysburg (and the next Civil War battle) | March pace by branch |

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

Give it a `based_on` row (one of `tactical` or `operational`, and one of `us-maps` or `world-maps`, and its war's preset if there is one),
its Current map as `bases.N.use = current`, and only the rows its data needs (titles, texts, views, Follow box, label zooms, maps).
Anything else it sets is a difference from the presets and needs a `why`.
