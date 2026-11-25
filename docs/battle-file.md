# The battle file

Every battle in WarMapper is one file, `playbacks/<battle>/battle.json`, and every battle's file has the same layout.
The playback pages read nothing else: units, where the sources put them and when, events, sources, the period maps
and the current map all come from it.

- Format name: `warmapper-battle/1` (the file says so in its first field; a page refuses a file with another name).
- Written by: `python3 tools/export_battles.py`, from the master workbooks (`data/WarMapper battle data/`: one per war, read as one set of tables, and `Sources and notes.xlsx`, which holds the sources every war shares). The last section says which sheet each part comes from.
- Checked by: `pipeline/battlefile.py`. A file that breaks a rule below is not written, and
  `python3 tools/export_battles.py --check` checks the files as they stand.
- Read by: `WM.battle()` in `app/core.js`, and played by `WM.play()` in `app/player.js`. No battle has code of its own.

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
| `record` | Where the data came from: the set of workbooks (`WarMapper battle data`), and the campaign and battle ids |
| `time` | The stretch of time the playback covers and how time is counted |
| `view` | Where on the earth the battle is |
| `playback` | How this battle is played back: the settings the shared player reads |
| `opening` | The text shown before the first event |
| `sides` | The two sides |
| `nations` | Optional: the nations within the sides, where they need their own name or colour |
| `units` | Every unit in the battle's order of battle, whether or not it is placed |
| `tracks` | One per symbol on the map: a unit and its recorded positions in time order |
| `events` | The named moments on the timeline |
| `links` | Optional. The campaign this battle is part of, or the battles inside this campaign (BP-34) |
| `sources` | Every source the file cites |
| `labels` | Names written on the map |
| `maps` | Period maps |
| `reconstructions` | Optional. Reconstructed base maps: maps WarMapper draws itself, from lines read off period maps |
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
boxes of the same form that the playback can jump to.

### sides and units

```json
"sides": [{"id": "ACW-US", "code": "US", "name": "United States (Union)", "short": "Union", "colour": "blue"}]

"units": [{"id": "US-B1", "name": "1st Brigade, 1st Cavalry Division", "label": "Gamble", "side": "ACW-US",
           "nation": "United States", "branch": "cavalry", "echelon": "brigade", "sources": ["S02"],
           "assignments": [{"from": "1863-07-01", "to": "1863-07-01", "parent": "US-CAV1",
                            "commander": "Col. William Gamble", "strength": "About 1,600 strong"}]}]
```

- `branch` is `infantry`, `cavalry`, `artillery` or `naval`. A naval unit (transports, gunboats) is drawn as a ship, without a frame or
  an echelon mark; its `echelon` is still required and means nothing.
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
part of: a regiment inside its brigade), `hide_after` (take the symbol off the map after its last step; during play, a unit whose higher unit is still on the map slides into that unit's symbol over 2.5 seconds instead of vanishing, and one with no higher unit fades out over the battle's `rules.linger`, 2 minutes by default),
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
- `via` is the road or route the unit took to reach this step, as a list of points. In a battle followed by the day, a step with a
  `via` is reached by moving along it over the whole time since the step before; without one the move is a straight line on the
  last day.
- `on` holds the position on a map that is not to scale, by map id, in that picture's own pixels.
- `leaving` (true) marks a step reached by a route of kind `escape`: Follow lets the unit go off the screen from when it sets off.
- `via_on` holds the route (`via`) on such a picture, by map id, where the exporter works it out (see `xy_from` below).
- `method` is `stated` (a source puts the unit here), `inferred` (worked out from other facts) or `interpolated`.
- `confidence` is `high`, `medium` or `low`.
- `location` says how the position was found: `source` (`marker`, `map_read`, `sketch_read`, `modern_map`,
  `derived`, `estimate`), `basis` in words, `confidence` and `precision_m`.
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

Since 23 Nov 2026 (BP-32) the player uses `steps` to tie an event to the map: the event's units are the tracks that carry those rows,
with the formations above them and the parts below them. While the event is current (until the next one begins, and no longer than its
record's end or 45 minutes, or two days in a battle followed by the day, after its mark), its units and their arrows stand out and the
other symbols are dimmed (Battle options: Highlight the units in the current event). How far is `playback.event_dim`: their strength, 0.32 unless set (Cowpens 0.7, since 24 Nov 2026); since then a unit eases between the two over about half a second instead of switching. Picking an event in the side pane moves the clock to
it and frames its rows; a unit's details list the events that name it. An event with no `steps` is shown as before, and the export lists
it (First Ypres: none of its 15 events names its rows yet). An event about a place with no unit (a bridge blown, a town taken empty)
cannot be tied to the map this way: that would need a place on the event, which the format does not have.

### summaries

Optional. A summary of a day or a week, shown when the playback stops at the end of one (see `day_pause`).

```json
{"kind": "day", "from": "1914-10-19", "to": "1914-10-19", "title": "The encounter",
 "text": "Four new German reserve corps strike the Allied cavalry screen. ...", "sources": ["S40", "S41"]}
```

`kind` is `day` or `week`; `from` and `to` are the dates it covers (the same date for a day). Where a day has no summary
the pause shows that day's events, and the units whose record changes that day, instead.

### links

Optional (since 23 Nov 2026, BP-34). A campaign followed by the day and the battles inside it, each followed by the minute, link to each
other: the campaign's file lists its battles, and each battle's file names its campaign.

```json
"links": [{"kind": "battle", "playback": "manila", "title": "Manila, 4-5 February 1899", "label": "Manila",
           "from": "1899-02-04T18:00", "to": "1899-02-05T20:00", "at": "1899-02-04T20:00", "unit": "minute"}]
```

- `kind` is `battle` (a battle inside this campaign) or `campaign` (the campaign this battle is part of). `playback` is the other
  playback's folder under `playbacks/`; `title` its title, and `label` the shorter name to show, if there is one.
- `from` and `to` are the other playback's own start and end (`time.start` and `time.end` of its file); `unit` its time unit.
- `at`, on a battle link, is where the battle opens from the campaign; left out, at its start, or at the campaign's date if that is later.
- The player shows a battle link on the campaign's timeline as a band over the battle's dates, lists the battles in the side pane, and
  while the clock is on a battle's dates offers to open it there (`#at=` in the address, as a copied link). A campaign link is offered at
  the top of the battle's side pane, and opens the campaign at the date on the battle's clock. A file with no `links` shows none of this.

### sources

`"S02": {"title": "...", "author": "...", "date": "1863", "citation": "...", "type": "Primary: official report", "url": "...", "rights": "..."}`.
A period map's details panel is made from the source its `source` names.
Only sources the file cites are included, and every id cited anywhere in the file must be here.

### labels

`{"text": "Chambersburg Road", "alt": "Chambersburg Pike", "at": [-77.279316, 39.850271], "angle": 29, "level": 0, "kind": "road"}`

`kind` is `road`, `water`, `area`, `town`, `place`, `wood`, `landmark`, `ridge` or `hill`. A `ridge` is named along its crest
(give its `angle`), a `hill` with a summit mark; both are drawn in the brown of relief, ahead of road names, and a level-0 ridge or hill is
named even where units cover it (beneath them). `alt` is the other name: the period's
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
- `from` and `to` give the dates a map belongs to (the official history's sketch for 22 and 23 October), or the times (Bearss's four phase maps at Cowpens, 06:00 to 07:11 and so on): a base with `series` shows the one for the moment on the clock.
- `fit` records how well the map was fitted.
- A map that is not to scale has `"georeferenced": false` and its picture's `size` in pixels in place of corners.
  It is shown as a picture in its own right, and steps carry their positions on it under `on`.
  A map fitted to the ground may come in several pieces side by side (`images`, none marked `detail`), so no piece is wider than a phone can show (4096 pixels); the player treats them as one sheet.
  In the workbook a picture not to scale can take its positions from a fit instead of from readings (Maps column `xy_from`, a fit file with the control points and crop): the exporter places every step and route on it.

- `iiif` says where the holding library serves the full scan as zoomable tiles (the IIIF image service), so the
  playback can show full detail when the reader zooms in: `service` (its address), `width`, `height`, `tile` and
  `scale_factors` (from the service's own description), `region` (the part of the scan the first picture shows, as
  `[left, top, right, bottom]` in scan pixels) and `reduced` (how large that picture is against the scan). A picture
  may carry its own `reduced`; tiles are fetched only once the reader zooms past what the pictures on screen can show.

Picture files sit beside the battle file.

### reconstructions

Optional. A reconstructed base map is not a picture. It is a set of lines read off period maps, which the page draws live in the manner
of a map of the time (toned paper, water in a wash with lines along the shore, double-line roads, a railway with its ties, period
lettering, relief shaded from elevation tiles). It stays sharp at any zoom and lies on the same ground as the units. It is always
labelled a reconstruction: the map-details panel (the i button) opens by saying so, and lists every layer with its source. Since
22 Nov 2026 no banner sits on the map itself (Morgan's choice); the sheet's own title, drawn on it when zoomed out, also calls it a
reconstruction. Tapping a line shows that line's own record.

```json
"reconstructions": [{"id": "manila-1899", "title": "Manila and vicinity, February 1899: a WarMapper reconstruction",
  "label": "1899 (reconstructed)", "about": "This is a WarMapper reconstruction, not a period map. ...", "credit": "...",
  "made": "2026-11-21", "review": "Needs review", "file": "data/recon/manila-1899.geojson", "sheet": [120.93, 14.52, 121.057, 14.681],
  "layers": [{"id": "shore", "title": "The 1899 shore, Vitas canal to Malate", "kind": "shore", "source": "S78", "link": "https://...",
              "link_label": "The engineer map (scan)", "method": "traced", "confidence": "medium", "from": "1899-02-04", "to": "1899-02-28",
              "how": "Read point by point from gridded crops of the scan.", "features": 2}],
  "features": [{"id": "MNL99-SHORE-1", "layer": "shore", "kind": "shore", "shape": "line", "at": ["12096364,1462496;13,-1;..."],
                "from": "1899-02-04", "to": "1899-02-28", "source": "S78", "method": "traced", "confidence": "medium", "precision_m": 30,
                "basis": "Read from gridded crops of the engineer map ...", "review": "Needs review"}]}]
```

- Every feature carries what a unit position carries (MS-2): its shape, the dates it holds for (`from`, `to`), its `source`, how it was
  read (`method`) and how sure it is (`confidence`, with `precision_m` and `basis` in words).
- `method` is `traced` (read point by point from the map), `AI-extracted` (separated from the scan by a program, then checked by eye)
  or `interpolated` (not on any map: a closing edge, a join).
- `confidence` is `high`, `medium` or `low`. A feature is `high` only when a cited source supports it and a person has checked it;
  if unsure it is `low`. Low-confidence shore lines are drawn dashed.
- `kind` is `sea`, `shore`, `river`, `stream`, `water`, `wall`, `road`, `rail`, `breakwater`, `blockhouse`, `detail` (the period map's
  own fine lines: street and block edges, dykes, field lines, hachures; drawn thin, from the zoom at which they can be read),
  `entrenchment` (field works; `side` is the code of the side that dug them, and they are drawn in a dashed red-brown line) or `ink`.
- An `ink` feature is a picture, not a line: every dark mark of a period map, kept as printed, with the paper made clear, laid over the
  reconstruction for the closest zooms, where the traced lines run out of detail (Manila: the War Department's 1898 plan of the city,
  with its blocks, public buildings and street names). Its `shape` is `area` and its `at` the picture's four corners, from the top-left
  clockwise. `file` is the picture, beside the battle file; `from_zoom` the map zoom it comes in at; `files`, optional, the same picture
  at several sizes as `[[zoom, file], ...]`, smallest first, each fetched only when the reader comes that close. It carries a source,
  method and confidence like any feature, and a tap on it shows them. A traced feature with `under` (the id of an ink picture) is the
  same thing drawn more coarsely: it fades out as that picture comes in, so nothing is drawn twice. A single-file page does not carry
  the ink pictures; it simply shows none.
  `shape` is `point` (`at` is one `[longitude, latitude]`), `line` or `area` (`at` is a list of packed lines, as in `base`: an area's
  first is its outline and the rest are holes), `lines` (several lines under one record: `at` is the list of them) or `areas` (several
  areas under one record: `at` is a list of areas, each a list of packed rings). `lines` and `areas` are for what a program takes
  from a scan by the thousand: one record, with its source, method and confidence, covers a district's worth, and `part` names the
  district. A `stream` may give `width_m`, its width on the ground; a `road` a `class` (`main` or `minor`).
- Relief on a reconstructed map is shaded from elevation tiles of zoom 11 at most (`relief_zoom` on the reconstruction changes that),
  enlarged smoothly: finer tiles show today's buildings as bumps on flat ground. A base with `terrain` (see `bases[].terrain`) reads
  finer tiles instead and cleans the buildings out first, then draws its own relief and contour lines.
- A layer groups features of one kind from one source. Its `link` opens the original map the layer was read from.
- `sheet` is the edge of the reconstruction, `[west, south, east, north]`: nothing is drawn beyond it, and a border is drawn on it.
- A base shows it with `"recon": id` (see `bases`). Names for it are labels with `show: "recon"`.

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

## playback

The rules of a playback are the same for every battle and live in `app/player.js`: where a unit is between two
steps, how symbols and names are laid out, the side panel, the timeline. What differs from battle to battle is
set here. Everything is optional; a battle file with no `playback` section plays on the current map with the
defaults.

```json
"playback": {
  "page_title": "Trenton 1776 Playback", "style": "tactical", "scale_bar": "yards", "rate": 3,
  "lead": {"share": 0.30, "rate": 18, "step": 5},
  "follow": {"min": [700, 520], "margin": 90, "exclude": ["T-HE-PKFER"], "empty": "march"},
  "bases": [{"id": "mod", "label": "Current map", "short": "Today", "current": true},
            {"id": "sk", "label": "1776 sketch", "short": "1776", "map": "wiederhold-1776"}],
  "zoom": {"max": 8, "follow_max": 2.2, "labels": 0.12, "towns_until": 0.09},
  "about": ["..."]
}
```

| Setting | What it does |
|---|---|
| `style` | `tactical` for a battlefield (larger symbols, a question mark on a loose position) or `operational` for a front (smaller symbols, thinner roads). Defaults from `time.unit`. |
| `scale_bar` | `yards` or `km`: the measure the scale bar writes first. The other follows under it, and both change as the reader zooms. |
| `question_mark` | What marks a unit as doubtful (a question mark, a dashed symbol): `location`, how sure the place is, or `overall` (the default). |
| `clock_title` | The battle's name in the date box on the map. Defaults to `title`. |
| `rate` | The play speed the page opens at: it opens on the time step nearest this many time units a second. The step button then sets both how far the back and forward buttons and arrow keys move and how fast it plays (one step a second). A battle followed by the day may set a rate below 1: with the 1-day step it then plays that many days a second (Ypres: 0.5). |
| `lead` | Squeezes the stretch before `time.focus` (a night march before a fight) into a `share` of the timeline, played at its own `rate`, with arrow keys moving `step` units. `until` (a time) ends the faster play earlier, so a march that matters plays at the normal rate; the timeline keeps its `share`. |
| `time_note` | A line under the clock from a given time on (`from`, `text`). |
| `follow` | Shows the Follow button: the camera keeps the units in view. `min` is the smallest box it frames, in metres; `margin` the space around the units; `exclude` tracks it ignores; `empty` the preset shown while no unit is placed. With Follow on, + and - tighten or widen the camera; zoomed in, it centres on where the action is: where opposing units are within `contact` metres of each other (800 by default on a battlefield, 5,000 on a front), otherwise where units are moving. | It frames every unit on the map now and every unit due on it within `lookahead` minutes (30 by default; not used for battles counted in days), so a column still far off is in view before it arrives and the camera closes in as the forces meet. `ease` is how quickly the camera catches up (0.1 of the way each frame by default). When play is first pressed from the opening view, the camera glides in slowly from the whole map over `glide_seconds` (6 by default), at `glide_rate` (the share of the way it closes each frame, 0.03 by default). `hold_until` (a time) keeps the camera on the wide opening view until that moment, so it does not close in on the first unit and pull back out as the rest come on; the glide starts then (Cowpens: 06:12, when Morgan's lines are on the map).
| `follow.pause_seconds` | Optional (4 by default). Moving or zooming the map by hand pauses Follow for this long after the last touch; it then carries on, keeping the reader's zoom. On a fitted period map with no detail to stream, Follow comes no closer than about 2.5 screen pixels to a pixel of the picture. |
| `skip` | Optional list of `{from, to, after_seconds, note}`. While playing, after `after_seconds` (2) inside the stretch the clock jumps to `to`, showing `note` (Trenton: the night of the crossing). Moving the clock by hand is not affected. |
| `follow.side_from` | Optional. By side code, a time before which Follow leaves that side out of what it frames (Trenton: the garrison sleeps while the army crosses). |
| `views` | Named views as buttons, each a `preset` from `view.presets` with a `label` and `short` label. The first is the opening view. |
| `opening_zoom_out` | Optional. Since 24 Nov 2026 every battle opens zoomed out, at Morgan's request, so the reader sees the ground around the battle first: the page stands this many zoom levels wider than its first view (or than the whole battle, with no views), 1 unless set (twice as wide; 0 turns it off). Once play is pressed the camera eases in: by Follow where the battle has it, otherwise to the first view. A link to a moment or a view opens there, as before. Not on a picture not drawn to scale, which has no ground around it. |
| `bases` | The maps the reader can put under the units, in button order (which one a battle opens on: see `start_base`). Each is the current map (`"current": true`), one period map (`"map": id`), the period map for the date on the timeline (`"series": true`: the maps that have `from` and `to`), aerial or satellite imagery (`"imagery": {...}`, below) or a reconstructed base map (`"recon": id`, one of the file's `reconstructions`: drawn by the page, never with the modern map under or around it, and with no fade slider). `backdrop` says what a period map lies on: `paper` or `current` (the current map shows around it). `clip` cuts the current map, or the imagery, to a period map's edge. `fade` adds the Fade map button. |
| `bases[].hidden`, `bases[].note` | Optional. `hidden: true` keeps a base off the Type of map menu; the map details (the i button) offer it instead, under "Other maps of this ground", with its `note` (a line on what it is) and a link to the original where its map's source has one. Opened that way, its own map details offer the way back to the main base. At least one base must be on the menu. Added 22 Nov 2026 (Manila: the Signal Corps map and the plain reconstruction). |
| `bases[].of` | Optional. Names another base. This base is not on the base bar: the 1:1 button on that base opens it where the reader is looking, and that base's button brings the reader back (Trenton: Faden's engraving as printed, behind the fitted 1777 map). Such a map carries a `lookup` table (place to picture pixel) for the hop. |
| `bases[].terrain` | Only on a base with `recon`: the terrain version of that reconstruction, which shows more of the ground the closer the reader looks. The page reads the elevation tiles of `hillshade` once, over `extent`, and a background worker cleans them and keeps the surface. From it come one relief picture (shading, a tint that deepens with height and, beyond the sheet, today's sea); contour lines for what is on screen, made afresh as the reader moves or zooms, sampled a few screen pixels apart so they stay smooth curves at any zoom; and spot heights for the summits on screen. `zoom` is the tile zoom read (12 by default, about 37 m a pixel at Manila: the cleaned surface holds nothing finer). `extent` is `[west, south, east, north]`: the ground worked. Left out, it is the reconstruction's `sheet`. Set wider than the sheet, the terrain runs on past the sheet's edge so the map fills a window of any shape; the sheet's frame gives way to a thin dotted line where the traced maps stop, and the reader can go no further out than where the extent just covers the window, nor past its edge. `open_m` takes off every bump narrower than that many metres before anything else (the tiles are a radar surface and carry buildings; 230 by default); `smooth_m` smooths what is left (60); `relief` exaggerates the heights for the shading (4); `tint: false` leaves the height tint out. `steps` is `[[zoom, metres, metres of the heavier lines], ...]`, lowest zoom first: from each zoom the contours close in to that interval (default `[[0,20,100],[11.2,10,50],[12.4,5,25],[13.4,2,10],[14.4,1,5],[15.6,0.5,5]]`; the third number is five times the second if left out). The heavier lines carry their heights; lines at half metres are drawn dashed, as form lines. `doubt` marks doubtful ground: a rise of more than `rise_m` (2.5) above ground lower than `below_m` (9) that is narrower than `across_m` (600) is, on a delta under a modern city, almost always a mass of buildings the cleaning could not take off, so its contours are drawn dotted, at whole metres only and without heights; `doubt: false` turns that off. `about` replaces the panel's account of what the heights are and how they were cleaned (the default is Manila's, a radar survey under a city), and `beyond` its sentence on the ground past the sheet's edge (Cowpens, 24 Nov 2026: the US tiles are a survey of the bare ground). `spots_from` is the zoom from which spot heights show (12.6); none is given on doubtful ground, nor where the cleaning took off more than 3 m on average. The map-details panel says what all this is: today's ground, cleaned, not a survey of 1899. Added 22 Nov 2026 (Manila); `extent`, the three-part `steps` and spot heights later the same day. |
| `bases[].imagery` | Imagery streamed from a tile service while that base is shown: `tiles`, the https address of one tile with `{z}`, `{x}` and `{y}` in it (standard web-map tiles); `credit`, the provider's required attribution; `max_zoom`, the deepest level the service has (the map enlarges past it); and, for the map-details panel, `name`, `about`, `rights`, `date` and `link`. Names from the current map are drawn over it. The page needs no key for it, so only services free to use without one belong here. |
| `bounds` | A map id: the edge of the battle's own maps. The Fit button frames it, and without a `surround` the reader cannot zoom out past it. |
| `modern` | The modern map: today's topographic map from a tile service. It is what a `current` base shows, it shows through a period map that is turned down, and it lies around a period map where that ends, so the reader can zoom out past the edge of the sheet. `tiles`, `credit`, `max_zoom`, `name`, `about`, `rights` and `link` as for `bases[].imagery`; `reach` is how far out the reader can go, in widths of the bounds map (4 by default, or 2 widths of the battle's extent where there is no bounds map). Under a period map at full strength the tiles are asked for only while part of the screen lies beyond the picture. The battle's own `base` data is the fall-back: it is drawn in place of the modern map if the service cannot be reached (four failed tiles), so an offline copy still has a current map. On the modern map the battle's `road`, `water` and `town` labels are left off, since the map names those itself; landmarks, ridges, hills, places and woods are still named. A map that is not to scale cannot have the modern map around it. |
| `start_base` | The id of the base a battle opens on. Left out, the exporter gives it the battle's first reconstructed map on the Type of map menu, if it has one (since 24 Nov 2026, SR-02); otherwise the rule is: a period map if it covers all of the opening view (the first of `views`, else the extent), otherwise the current map. |
| `zoom` | Zoom levels in screen pixels per metre: `max`; `follow_max`; `fold` (below it, units fold into their parent); `labels` (from it, level 1 names show); `towns_until`; `landmarks_from`; `woods_from`; `full_names` (from it, a place's other name shows); `minor_roads_from`; `force_names_from`; `phone_names` (on a phone, below it, artillery, detachments and other small parts show no name; default 0.6, or `full_names` for an operational battle). |
| `fold` | `label` names the button that switches folding of tracks that have a `parent`. `formation: true` also hides a unit while its parent formation has a line of its own on the map and the reader is zoomed out; `sides` limits that to the sides listed. |
| `formations` | Optional. Zoomed out below `below` (screen pixels per metre), the units under each formation of the given `echelon` (`division` by default) are drawn as that formation: one symbol where theirs would sit, with their lines kept as its front. A unit is gathered by walking up its assignments at that moment; a unit that is itself of that echelon (a corps with its own track) is drawn as its own formation. Zooming in past `below`, or tapping the formation, breaks it out into its units. The reader turns it on and off in the Layers menu ("`label` when zoomed out"); `on` sets whether it starts on. |
| `formations.until`, `formations.also` | Optional. Before `until` the formations are drawn whatever the zoom (Trenton: Greene, Sullivan and Knox stay whole until the first shots). `also` names units that count as formations though not of the echelon (Knox's artillery). Where a formation has its own track, its symbol stands where that track is. |
| `trails` | Optional. `on` (true by default when the block is there) draws the routes taken: the road each unit has marched so far (its `via` routes), under the units and growing with the clock; `opacity` how strongly; `fade_after` (time units): once a unit has stood still this long, the routes it took to get there fade out, over `fade_over` (Trenton: 10 and 10 minutes). A route also fades, over a third of `fade_over`, once the unit moves on from its end by a step that has no route of its own (forming a line, a charge), so it is not left lying on the map apart from the unit. Layers menu: Routes taken, offered only where the battle has a route on record (since 24 Nov 2026). |
| `arrows` | Optional. Before a unit sets off on a long move, and while it is on it, an arrow runs from the unit to where the record next puts it, along the step's `via` (straight where there is none). On in every battle unless `on` is false. `min_km`: how long a move earns an arrow (20 unless set). `lead`: how long before the unit sets off the arrow appears, in the battle's time unit (3 days or 45 minutes unless set). The reader can switch the arrows off; the switch is offered only where some move is long enough. | `reach_minutes` (optional, since 24 Nov 2026): the arrow runs only so many minutes of the move ahead of the unit, so its head travels with the unit instead of standing at the far end of a long road (Cowpens: 6).
| `opening_ease` | Optional, for a battle without Follow (0.03 by default). When play is first pressed from the wide opening view, the camera eases in to the battle's own first view by this share of the way each frame: smaller is slower. Added 24 Nov 2026 (SR-04: First Ypres and Luzon take 0.006 from the preset `operational`, the rate Follow uses on the battlefields). |
| `day_pause` | Optional. A battle longer than two days can stop at the end of each day (or week) while it plays: the map stays where it is, the text pane shows the summary (`summaries`) and a Continue button goes on. Up to seven days the pauses are on each day; longer, the reader is asked the first time they press play. `false` never pauses; `"day"`, `"week"`, `"off"` or `"ask"` sets the starting choice. Days end at midnight (`time.zero` is a midnight); a battle followed by the day ends each day at nightfall. Battle options: Pause and summary. Battle options also offers *Where units began and ended each day* on any battle longer than a day and a half. |
| `hillshade` | Optional. On a reconstructed base map the same elevation tiles are shaded in the map's own brown ink. Terrain shading drawn over today's map from elevation tiles, outside the muting, so ridges and valleys stay plain. On for every battle by default, from the Mapzen Terrain Tiles on AWS Open Data (Terrarium encoding). `false` turns it off; an object overrides `tiles`, `encoding`, `max_zoom`, `exaggeration` (0 to 1, default 0.8), `credit`, `link`. Layers menu: Terrain shading on today's map. |
| `arrival` | Optional, for the exporter (not read by the player). A unit first placed after the battle opens gets a stand-in first step `lead` days earlier (1 by default), marked as an approach not recorded: at the middle of its parent formation's line if that formation is already on the map, otherwise `km` (10) behind its own first position, towards the point `<side code>.lat, lon` or along `<side code>.bearing` (degrees from north). Tracks with `starts_from_row`, `part_of_track` or `off_map` are left alone. |
| `groups` | Zoomed out below `below`, the units of a `side` (but for `except`) are drawn as one symbol with this `label`. |
| `rear` | A unit's symbol sits behind its own line: on the side away from the nearest enemy within about 2.5 km (8 km for an operational battle). Where no enemy is that near, `rear` decides: a point (`at`) behind one `side`'s line, so that side's symbols sit on that side of their lines and the other side's on the far side. Failing both, symbols sit to the east. |
| `rules` | `blend`: minutes over which a unit shifts from one step to the next when they meet. `near`: metres within which no march is drawn. `pace`: march pace in metres a minute, one number or one per branch (`infantry`, `cavalry`, `artillery`), used for moves into a step marked `march`. For day battles, `lead` (the part of a day before nightfall in which the move happens) and `linger` (days a unit stays after the sources drop it, fading as they pass). |
| `texts`, `found` | Wording for this battle: the sentence under each state (`stated`, `inferred`, `moving`, `after`, `unplaced`, `offthis`, `lost`), and the words for how a place was found (`map_read`, `sketch_read` and so on). |
| `about` | The paragraphs under "About this prototype". |

Elsewhere in the file the player also reads:

- `nations`: `{"name", "short"}` gives a nation its own name in the panel ("Hessian"); with `code`, `colour` (and
  `dark`, `paper` for the dark theme and for period maps) its units get their own colour and the panel lists
  units by nation.
- On a label, `show`: `current` (the default: drawn where today's map shows), `period`, `both`, or `recon` (drawn only on a reconstructed base map, in period lettering: the names read from its source maps; a reconstructed base draws no other labels), or `far`: a place too far off to zoom out to (the nearest towns of the time, for orientation). While it is off screen it is named at the edge of the map, on the line from the middle of the screen towards it, with an arrow and its straight-line distance in miles from the middle of the screen; on screen it is drawn as a town. It is named on every base, a reconstruction too, kept clear of the buttons over the map, and turned off with place names. Its point is not checked against the battle's extent.
- On a step, `along: true`: the step's line is the path the unit moves along during the step.
- On a step, `march: true`: with nothing on record between the previous step and this one, the unit leaves when the previous step ends
  and moves here at the battle's `rules.pace`, then waits ("Arrived: time inferred"), instead of drifting slowly across the whole gap.
- `note`: anything the reader should know about the picture (a repair, a missing part), shown in the map details.
- On a map that is not to scale, `scale_note` (shown in place of the scale bar), `approx_m_per_px` (metres on the
  ground per pixel of `size` where the map is nearest to true: with it a rough scale bar is drawn, marked "about",
  and `scale_note` goes under it) and `off_note` (`until`, `text`: a note shown while the action is off that map).
- In `base`, `widths`: a river's width on the ground in metres, by name.

## What is not in the file

Code. The page (`app/page.html`) and the player are the same for every battle; `tools/build.py` writes the
battle file into the page.

## Where each part comes from in the workbooks

Every sheet below is on each war's workbook, but for `Sources`, which is in `Sources and notes.xlsx`.

| Part of the battle file | Sheet |
|---|---|
| `id`, `title`, `subtitle`, `time`, `view`, `opening`, `record` | `Playbacks`: one row per playback |
| `playback`, and `view.presets` | `Playback settings`: one setting per row. `bases.1.label` is the label of the first base; a value written `[..]` is a list. Since 24 Nov 2026 a battle's `based_on` row names its presets (`Playback presets` sheet of `Sources and notes.xlsx`), which the exporter lays on first; the battle's own rows win, and its `why` column says why a row differs. `bases.N.use` takes a standard map from the presets. Some values are worked out from the battle (arrow limit, arrow reach, fade times, the start map): see `docs/presets.md`. The battle file holds the result, so it reads as before |
| `sides` | `Sides`: the sides of the playback's war. A playback that needs its own words for a side sets `sides.<code>.short` and `sides.<code>.name` on `Playback settings` (since 23 Nov 2026: the Crown side is "Hessian and British" at Trenton and "British" at Cowpens); they replace the war's `short` and `name` in that playback's file and are not copied into its `playback` section |
| `nations` | `Nations` |
| `units` and their `assignments` | `Units`, `Assignments`: every unit of the campaign's war, but for units that only another playback of that war draws (Manila and Luzon 1899 share one war) |
| `tracks` | `Tracks`: one row per symbol. `rows` lists the `Positions` rows it follows; left empty, it follows every row of its unit. `starts_from_row`, `starts_at` and `start_route` (and `start_move_minutes`, how long it takes to reach its first row, such as a river crossing) give a symbol a stand-in start from a row of its division's (`start_route` may name several routes in order, `RT01; RT02`; `start_route_points` caps the points taken from the last) |
| steps | `Positions`. `show_from` and `show_to` are when the playback draws the row; left empty, it is drawn from its latest start to its earliest end. Where two rows of one symbol overlap, the earlier gives way. `arrive_at_pace` (yes) is the step's `march` |
| a step's `via` | `Routes`: a route from one row to the next, where its `playback` column says yes |
| `events` | `Events`: those of the battles the playback's `record_battles` names. `timeline` is `name`, `dot` or `off`; `playback_at`, `playback_label` and `playback_text` are the playback's moment, short name and wording where they differ from the record's |
| `summaries` | `Summaries`: one row per day or week (`kind`, `from`, `to`, `title`, `text`, `source_ids`) |
| `links` | `Links`: one row per campaign playback and battle playback inside it, both of one war (`campaign_playback`, `battle_playback`, `label`, `campaign_label`, `opens_at`). The dates come from each one's `Playbacks` row |
| `sources` | `Sources`: only those the battle cites |
| `labels` | `Labels` |
| `maps` | `Maps`: one row per picture; the `iiif_...` columns on a map's first picture |
| `reconstructions` | `Reconstructions`: one row per reconstructed base map (title, label, about, credit, file). `Recon layers`: one row per layer (title, kind, source_id, link, method, confidence, from, to, how_read). The lines are in the GeoJSON the row names (`data/recon/<id>.geojson`), where every feature repeats its own source, method, confidence and dates; the script that wrote it is in `pipeline/recon/` |
| `base` | Not in the workbook: `data/base/<playback>.json`, cut from OpenStreetMap by `pipeline/basemaps.py` |
