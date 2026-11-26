"""Screenshots of every playback at the same views, to compare maps side by side after a change.

  python3 tools/screenshots.py                               all six battles, phone and desktop widths, into the default folder
  python3 tools/screenshots.py --out ~/somewhere             into another folder
  python3 tools/screenshots.py --before ~/.../2026-11-25-0910 also lay the earlier set beside the new one (before and after)
  python3 tools/screenshots.py cowpens trenton               some battles only

For each battle it takes three views at each of two widths (phone 390 x 844, desktop 1440 x 900):
  1-opening   the page as it opens (the whole ground, no units yet)
  2-mid       the middle of the battle (the middle of time.focus where there is one), units on, the battle's own camera
  3-close     the same moment, zoomed in two levels on where the action is
and writes index.html, a contact sheet: one row per battle, the six pictures side by side (with --before, each beside its earlier one).
It also writes errors.txt: anything a page logged as an error, by battle. The pages are served from this repo, so it shows this branch.

Where the pictures go: by default ~/Documents/Starfishient/WarMapper/screenshots/<date and time>-<branch>/, outside the repo. The repo is
public and the pictures carry map tiles (OpenTopoMap and OpenStreetMap ask for attribution and share-alike), so they are not committed.

Needs, once: python3 -m pip install playwright, then python3 -m playwright install chromium (about 150 MB). The map tiles are fetched
from the internet as the pages ask for them; where they cannot be reached the pages draw their own fall-back map, and the contact sheet
says so.
"""
import argparse, datetime as dt, functools, html, http.server, json, os, re, subprocess, sys, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTLES = ['gettysburg', 'trenton', 'ypres', 'manila', 'luzon1899', 'cowpens', 'guilford-courthouse']
SIZES = [('phone', 390, 844), ('desktop', 1440, 900)]
VIEWS = ['1-opening', '2-mid', '3-close']
NET = re.compile(r'Failed to load resource|Failed to fetch|CORS policy|net::ERR|AJAXError|NetworkError', re.I)


def serve():
    """A local web server for the repo (the pages need one for their workers and pictures); returns its address."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Quiet, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return 'http://127.0.0.1:%d/' % srv.server_address[1]


def middle(b):
    """The moment for the mid-play view: the middle of time.focus, else of the whole timeline, in the battle's own form of time."""
    T = b['time']; a, z = (T.get('focus') or [None, None])
    if not (a and z): a, z = T['start'], T['end']
    p = lambda s: dt.datetime.fromisoformat(s if len(s) > 10 else s + 'T00:00')
    m = p(a) + (p(z) - p(a)) / 2
    return m.strftime('%Y-%m-%d') if T['unit'] == 'day' else m.strftime('%Y-%m-%dT%H:%M')


def branch():
    try: return subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip() or 'repo'
    except Exception: return 'repo'


def shoot(battles, out, settle):
    from playwright.sync_api import sync_playwright
    url = serve(); errors = {}; tiles = {'ok': 0, 'failed': 0}
    with sync_playwright() as pw:
        try: br = pw.chromium.launch()
        except Exception: br = pw.chromium.launch(channel='chrome')   # a Chrome already on the computer
        for name in battles:
            b = json.load(open(os.path.join(ROOT, 'playbacks', name, 'battle.json'), encoding='utf-8')); at = middle(b)
            for size, w, h in SIZES:
                ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if size == 'phone' else 1, is_mobile=size == 'phone', has_touch=size == 'phone')
                page = ctx.new_page(); log = errors.setdefault(name, [])
                page.on('console', lambda m, s=size: log.append('%s: %s' % (s, m.text)) if m.type == 'error' and not NET.search(m.text) else None)   # a tile that cannot be fetched is not a fault of the page
                page.on('pageerror', lambda e, s=size: log.append('%s: %s' % (s, e)))
                page.on('requestfinished', lambda r: tiles.__setitem__('ok', tiles['ok'] + 1) if '/tile' in r.url or 'tile.' in r.url else None)
                page.on('requestfailed', lambda r: tiles.__setitem__('failed', tiles['failed'] + 1) if '/tile' in r.url or 'tile.' in r.url or 'terrarium' in r.url else None)
                def go(hash_, shot):
                    page.goto('about:blank')   # a new hash alone does not reload the page, and the player reads the link only as it starts
                    page.goto(url + 'playbacks/%s/index.html%s' % (name, hash_)); page.wait_for_function('window.__wm', timeout=30000)
                    page.wait_for_timeout(settle * 1000); page.screenshot(path=os.path.join(out, '%s-%s-%s.png' % (name, shot, size)))
                go('', '1-opening')
                go('#at=' + at, '2-mid')
                f = page.evaluate('(function(){var f=__wm.focus(),m=__wm.mv.map;return f?[f[0],f[1],m.getZoom()+2]:[m.getCenter().lng,m.getCenter().lat,m.getZoom()+2]})()')
                go('#at=%s&view=%.6f,%.6f,%.2f' % (at, f[0], f[1], f[2]), '3-close')
                ctx.close()
            print('%s: %d pictures%s' % (name, len(SIZES) * len(VIEWS), (', %d error(s)' % len(errors[name])) if errors[name] else ''))
        br.close()
    return errors, tiles


def sheet(out, battles, before, tiles):
    """index.html: one row per battle, the pictures side by side; with `before`, each new picture beside the earlier one."""
    rel = lambda p: os.path.relpath(p, out)
    rows = []
    for name in battles:
        cells = []
        for size, _, _ in SIZES:
            for v in VIEWS:
                f = '%s-%s-%s.png' % (name, v, size); new = '<img src="%s" loading="lazy">' % html.escape(f)
                old = os.path.join(before, f) if before else None
                pic = ('<div class="pair"><figure><figcaption>before</figcaption><img src="%s" loading="lazy"></figure><figure><figcaption>after</figcaption>%s</figure></div>' % (html.escape(rel(old)), new)) if old and os.path.exists(old) else new
                cells.append('<td><div class="cap">%s, %s</div>%s</td>' % (v[2:], size, pic))
        rows.append('<tr><th>%s</th>%s</tr>' % (name, ''.join(cells)))
    note = '' if tiles['ok'] or not tiles['failed'] else '<p class="warn">The map tile services could not be reached, so the maps show each page\'s own fall-back drawing, not the topographic map.</p>'
    doc = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>WarMapper screenshots</title><style>body{font:14px system-ui;margin:16px}'
           'table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px;vertical-align:top}th{writing-mode:vertical-rl;transform:rotate(180deg)}'
           'img{max-width:260px;display:block}.pair{display:flex;gap:4px}.pair img{max-width:200px}.cap{font-size:12px;color:#555;margin-bottom:4px}'
           'figure{margin:0}figcaption{font-size:11px;color:#777}.warn{color:#a40}</style></head><body><h1>WarMapper screenshots</h1>'
           '<p>%s. Made %s from branch %s.%s</p>%s<table>%s</table></body></html>') % (
        'Before and after' if before else 'One set', dt.datetime.now().strftime('%d %b %Y %H:%M'), html.escape(branch()),
        (' Earlier set: ' + html.escape(before)) if before else '', note, ''.join(rows))
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(doc)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('battles', nargs='*'); ap.add_argument('--out'); ap.add_argument('--before'); ap.add_argument('--settle', type=float, default=4,
                    help='seconds to let each view draw before the picture (default 4)')
    a = ap.parse_args(argv); battles = a.battles or BATTLES
    out = os.path.expanduser(a.out or os.path.join('~', 'Documents', 'Starfishient', 'WarMapper', 'screenshots', dt.datetime.now().strftime('%Y-%m-%d-%H%M') + '-' + branch()))
    if os.path.abspath(out).startswith(ROOT + os.sep): sys.exit('Put the pictures outside the repo (it is public): %s' % out)
    os.makedirs(out, exist_ok=True)
    errors, tiles = shoot(battles, out, a.settle)
    open(os.path.join(out, 'errors.txt'), 'w', encoding='utf-8').write(''.join('%s\n%s\n\n' % (n, '\n'.join(e) or 'none') for n, e in errors.items()))
    sheet(out, battles, os.path.expanduser(a.before) if a.before else None, tiles)
    print('Contact sheet: %s' % os.path.join(out, 'index.html'))
    return 1 if any(errors.values()) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
