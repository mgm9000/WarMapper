# Retired scripts

These built the data before the workbook became the master copy (15 Nov 2026). They are kept for the record and are not run any more;
several will not run from this folder without changes.

| File | What it did |
| --- | --- |
| `build_workbook.py` | Generated the pilot workbook (v7) and its Checks sheet from the Gettysburg v2 workbook and the two data modules. |
| `trenton_data.py`, `ypres_data.py`, `ypres_v7.py` | The Trenton and First Ypres rows, written as code. |
| `check_ypres.py` | A check on the Ypres rows. |
| `prep_gettysburg.py`, `prep_trenton.py`, `prep_ypres.py` | Wrote each battle's battle file. Replaced by `tools/export_battles.py`, which reads the workbook. The Gettysburg one also worked out where road and stream names go; those names are now rows on the workbook's Labels sheet. |
| `make_workbook_v8.py` | Run once: made `data/WarMapper battle data.xlsx` from the v7 workbook and the three battle files. |

The two older workbooks are in `data/legacy/`.
