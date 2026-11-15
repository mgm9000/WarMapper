# The battle file

Every battle in WarMapper is one file, `playbacks/<battle>/battle.json`, and every battle's file has the same layout.
The playback pages read nothing else: units, where the sources put them and when, events, sources, the period maps
and the current map all come from it.

- Format name: `warmapper-battle/1` (the file says so in its first field; a page refuses a file with another name).
- Written by: each battle's recipe, `playbacks/<battle>/prep.py`. Run them all with `python3 tools/export_battles.py`.
- Checked by: `pipeline/battlefile.py`. A file that breaks a rule below is not written, and
  `python3 tools/export_battles.py --check` checks the files as they stand.
- Read by: `WM.battle()` in `app/core.js`.

## Two rules that hold everywhere

**Places are longitude and latitude**, in that order, as `[longitude, latitude]` (WGS 84, the system GPS uses), to six
decimal places (about 10 cm). The one exception is a map that is not to scale, described under Maps.

**Times are dates and clock times**, written `1863-07-01T08:00` (or `1863-07-01T08:02:30`), or a date alone,
`1914-10-25`, when the record gives only the day. They are local time at the battle. A time the record does not
give is `null`.

## Layout

| Field | What it holds |
|---|---|
| `format` | `warmapper-battle/1` |
| `id`, `title`, `subtitle` | The battle's short id and its name as shown |
| `record` | Where the data came from: the workbook, and its campaign and battle ids |
| `time` | The stretch of time the playback covers and how time is counted |
| `view` | Where on the earth the battle is |
| `opening` | The text shown before the first event |
| `sides` | The two sides |
| `units` | Every unit in the battle's order of battle, whether or not it is placed |
| `tracks` | One per symbol on the map: a unit and its recorded positions in time order |
| `events` | The named moments on the timeline |
| `sources` | Every source the file cites |
| `labels` | Names written on the map |
| `maps` | Period maps |
| `base` | The current map's roads, water, railways and woods |

### time

```json
"time": {"unit": "minute", "zero": "1863-07-01T00:00", "start": "1863-07-01T07:15", "end": "1863-07-01T10:30",
         "focus": ["1863-07-01T07:30", "1863-07-01T10:15"],
         "calendar": {"first": "1863-07-01", "numbered": true, "days": 3}}
```

- `unit` is `minute` for a battle followed by the clock, or `day` for one followed day by day (First Ypres).
- `start` and `end` are the ends of the timeline. `focus`, if given, is the part the data covers best.
- `calendar.numbered` says whether the battle has agreed, numbered days ("Day 1"); `days` is how many.
  Where the start and end dates are disputed it is `false` and no day number is shown.

### view

`origin` is a point near the middle of the action. `extent` is `[west, south, east, north]`. `presets` are named
boxes of the same form that a page can jump to. `points` are named single places a page needs.

### sides and units

```json
"sides": [{"id": "ACW-US", "code": "US", "name": "United States (Union)", "short": "Union", "colour": "blue"}]

"units": [{"id": "US-B1", "name": "1st Brigade, 1st Cavalry Division", "label": "Gamble", "side": "ACW-US",
           "nation": "United States", "branch": "cavalry", "echelon": "brigade", "sources": ["S02"],
           "assignments": [{"from": "1863-07-01", "to": "1863-07-01", "parent": "US-CAV1",
                            "commander": "Col. William Gamble", "strength": "About 1,600 strong"}]}]
```

- `branch` is `infantry`, `cavalry` or `artillery`.
- `echelon` is one of `army`, `corps`, `division`, `brigade`, `regiment`, `battalion`, `squadrons`, `battery`,
  `company`, `section`, `detachment`, `headquarters`.
- `assignments` say who the unit answered to, who commanded it and how strong it was. A unit that changed hands
  during the battle has one entry per period, with `from` and `to`.

### tracks and steps

A track is one symbol on the map. Most units have one track; a unit can have more (Gamble's brigade and its
skirmish line are two).

```json
{"id": "US-B1", "unit": "US-B1", "steps": [ ... ]}
```

A track may add: `label` and `echelon` (if the symbol's differ from the unit's), `parent` (the track this one is a
part of: a regiment inside its brigade), `hide_after` (take the symbol off the map after its last step),
`hold_until` (keep it on until this time), `loose` (a scattered line: skirmishers), `off_map` (text saying where
the unit is when that is off the map), `nudge` (shift the symbol by this many screen pixels so it does not sit on
another).

A step is one row of the record: one unit, at one place, for one stretch of time.

```json
{"id": "P04",
 "start": ["1863-07-01T08:00", "1863-07-01T08:00"], "end": ["1863-07-01T10:15", "1863-07-01T10:15"],
 "show": ["1863-07-01T08:00", "1863-07-01T10:15"],
 "at": [[-77.24664, 39.83926], [-77.25122, 39.83078]],
 "activity": "Line of battle (dismounted)", "place": "McPherson Ridge: right resting on the railroad bed ...",
 "quote": "S02: \"placed in line of battle about 1 mile in front of the seminary\" ...",
 "method": "stated", "confidence": "medium", "time_basis": "Start: source states. End: inferred",
 "location": {"source": "map_read", "basis": "Read from the Bachelder 1876 first-day map ...",
              "confidence": "medium", "precision_m": 40},
 "sources": ["S02", "S01", "S09", "S18"], "notes": "...", "review": "Needs review", "battle": "GETT-D1-AM"}
```

- `id` is the row's id in the workbook, so anything on screen can be traced back to its row.
- `start` and `end` are what the record says, each as `[earliest, latest]`. `null` means unknown.
- `show` is `[from, to]`: when the playback draws the step. This is the playback's reading of the record
  (the middle of a range, say), kept apart from the record itself.
- `at` is the position: one point, or the points of a line from one flank to the other. A step with no `at` is a
  record with no known position.
- `via` is the road or route the unit took to reach this step, as a list of points.
- `on` holds the position on a map that is not to scale, by map id, in that picture's own pixels.
- `method` is `stated` (a source puts the unit here), `inferred` (worked out from other facts) or `interpolated`.
- `confidence` is `high`, `medium` or `low`.
- `location` says how the position was found: `source` (`marker`, `map_read`, `sketch_read`, `modern_map`,
  `derived`, `estimate`), `basis` in words, `precision_m`, and `places` where a line runs through named places.
- `virtual` marks a step that is not a record of this unit: a stand-in so the symbol has somewhere to start from.
  `shared` marks a step that is a record of the unit's parent.

Steps on a track are in time order.

### events

```json
{"id": "GE04", "start": "1863-07-01T09:00", "end": "1863-07-01T09:30", "at": "1863-07-01T09:30",
 "name": "Heth deploys", "text": "Archer forms south of the pike and Davis north of it. ...",
 "steps": ["P17", "P20"], "sources": ["S04", "S05", "S18"]}
```

`start` and `end` are the range the record gives; `at` is where the timeline marks it. `label` is a shorter name
for the timeline, `quiet` marks an event shown as a dot without its name, `steps` are the rows it rests on.

### sources

`"S02": {"title": "...", "citation": "...", "type": "Primary: official report", "url": "..."}`.
Only sources the file cites are included, and every id cited anywhere in the file must be here.

### labels

`{"text": "Chambersburg Road", "alt": "Chambersburg Pike", "at": [-77.279316, 39.850271], "angle": 29, "level": 0, "kind": "road"}`

`kind` is `road`, `water`, `area`, `town`, `place`, `wood` or `landmark`. `alt` is the other name: the period's
name where `text` is today's. `level` 0 shows first; higher levels appear as the reader zooms in. `angle` turns a
name to lie along its road or stream. `approximate` marks a place put down only roughly.

### maps

A period map that has been fitted to the ground gives each picture's four corners, in the order top-left,
top-right, bottom-right, bottom-left:

```json
{"id": "bachelder-1876", "title": "...", "credit": "Bachelder, 1876 · Boston Public Library", "source": "S18",
 "images": [{"file": "map_wide.jpg", "corners": [[-77.288689, 39.857702], [-77.193011, 39.856441],
                                                 [-77.194719, 39.779435], [-77.290397, 39.780696]]}]}
```

- A second picture marked `"detail": true` is a sharper picture of part of the same map.
- `from` and `to` give the dates a map belongs to (the official history's sketch for 22 and 23 October).
- `fit` records how well the map was fitted.
- A map that is not to scale has `"georeferenced": false` and its picture's `size` in pixels in place of corners.
  It is shown as a picture in its own right, and steps carry their positions on it under `on`.

Picture files sit beside the battle file.

### base

The current map, cut down to what the battle needs, from OpenStreetMap.

```json
"base": {"credit": "© OpenStreetMap contributors",
         "lines": [["road", "m", "Chambersburg Road", "-7724475,3983460;-1150,530"]],
         "areas": [["wood", "Biesecker Woods", "..."]]}
```

- A line is `[kind, class, name, points]`. `kind` is `road`, `rail`, `water` or `former-water`. For a road the
  class is its importance, from `m` (main) down through `p`, `s`, `t`, `u`, `r` to `v` (track). For water it is
  `river`, `stream` or `canal`.
- An area is `[kind, name, points]`; `kind` is `wood` or `water`.
- Points are packed to keep the file small: the first point, then the step to each next point, as
  `longitude,latitude` in units of 0.00001 degree (about a metre).

## What is not in the file

How a playback behaves is the page's business: how a symbol moves between two steps, which symbols fold into
their parent when zoomed out, how names avoid each other. Each battle's page still holds those rules for itself.
