# Course pages

A course page lists every class meeting of a course, with its readings and the battle playbacks that go with each day.

| File | What it is |
| --- | --- |
| `page.html` | The template, the same for every course. `tools/build.py` fills it in. |
| `<course>/course.json` | The data for one course (format `warmapper-course/1`). Edit this, not the page. |
| `<course>/index.html` | The built page. Do not edit by hand; run `python3 tools/build.py courses`. |

## What `course.json` holds

- `entries`: every class meeting (`kind` "class"), paper due date ("due") and exam ("exam"), in order. Each has a `weekday`, a `date` and a `date_status`. While the term dates are unknown, every `date_status` says "placeholder: update"; change the date and the status, then rebuild.
- `readings` (on a class): the reading as the syllabus words it, its `kind`, its `rights` (`status`: "public domain", "in copyright" or "not confirmed"; `hosted` is always false), and how to reach it (`access`: "link", "canvas" or "book"). A "canvas" or "book" reading has no link.
- `playbacks` (on a class): the slots for battle playbacks. A slot with `"playback": null` shows "Not built yet". When `playbacks/<id>/index.html` exists, set `playback` to that folder name and the slot links to it. A slot of kind "campaign" lists its battles in `children`; each battle names its campaign in `parent`.
- `chapters` (on a class, since 25 Nov 2026): an ordered group of that day's playback slots read as one chapter, e.g. orientation, battle, campaign, battle (`id`, `title`, `about`, `order`: the slot ids in order, `readings`: the ids of the day's readings that go with it, `reading_note`). The page shows the chapter as a numbered list; slots in no chapter are listed after it as before. Two built neighbours in a chapter must lead on to each other: a row on the war workbook's `Next links` sheet gives the first playback a "Next in this chapter" button at its end and the second a way back.
- `syllabus_flags`: places where the syllabus looks wrong or odd, kept for the instructor.

## What the build checks

Entry ids are unique; each weekday matches its date; every entry has a date status; nothing is hosted; a linked reading has an https link and a Canvas or book reading has none; class numbers run 1, 2, 3 and so on; a slot that names a playback names one that is built. A chapter lists only that day's slots and readings, puts no slot in two chapters, and two built neighbours in it link to each other. A failed check stops the build and names the entry.

Times are written in 24-hour form (23:59, not 11:59 pm).
