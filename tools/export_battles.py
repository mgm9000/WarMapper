"""Write every battle's battle file, or check the ones already written.

A battle file (playbacks/<battle>/battle.json) is the one format every battle's data comes in: docs/battle-file.md.
Each battle has a recipe (playbacks/<battle>/prep.py) that gathers its record and writes the file; this runs them.

  python3 tools/export_battles.py              write all battle files, then check them
  python3 tools/export_battles.py ypres        one battle only
  python3 tools/export_battles.py --check      check the files as they stand, without rewriting them

After exporting, run tools/build.py to put the new data into the pages.
"""
import json, os, runpy, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import battlefile

BATTLES = ['gettysburg', 'trenton', 'ypres']


def main(argv):
    args = list(argv); check_only = '--check' in args
    if check_only: args.remove('--check')
    battles = args or BATTLES; failed = 0
    for b in battles:
        assert b in BATTLES, b
        folder = os.path.join(ROOT, 'playbacks', b)
        if not check_only:
            runpy.run_path(os.path.join(folder, 'prep.py'), run_name='__main__')
        path = os.path.join(folder, 'battle.json')
        bad = battlefile.validate(json.load(open(path, encoding='utf-8')), folder)
        print('%s: %s' % (b, 'meets the format' if not bad else '%d problem(s)\n  %s' % (len(bad), '\n  '.join(bad[:40]))))
        failed += bool(bad)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
