"""Open the orientation test page in a browser, play it, and check what it draws: screenshots at phone and desktop widths, and a list
of anything that is not as the design says.

  python3 tests/orientation/make_demo.py                 first: write the test page
  python3 tests/orientation/check_page.py --out DIR      then: pictures into DIR (outside the repo: they carry map tiles)

Needs playwright (python3 -m pip install playwright) and a Chrome or Chromium. Where the map tiles cannot be reached the page draws plain
ground under the symbols, which is enough to check them.
"""
import argparse, functools, http.server, json, os, re, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PAGE = 'tests/orientation/demo/index.html'
NET = re.compile(r'Failed to load resource|Failed to fetch|CORS policy|net::ERR|AJAXError|NetworkError', re.I)   # tiles out of reach: not the page's fault
SIZES = [('phone', 390, 844), ('desktop', 1440, 900)]


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return 'http://127.0.0.1:%d/' % srv.server_address[1]


def main(argv):
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=os.path.expanduser('~/orientation-shots')); ap.add_argument('--chrome', default=None)
    a = ap.parse_args(argv); os.makedirs(a.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    url = serve() + PAGE; bad = []; errs = []
    with sync_playwright() as pw:
        exe = a.chrome or next((p for p in ('/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser') if os.path.exists(p)), None)
        br = pw.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist']) if exe else pw.chromium.launch()
        for name, w, h in SIZES:
            pg = br.new_page(viewport={'width': w, 'height': h})
            pg.on('console', lambda m: errs.append('%s: %s' % (name, m.text)) if m.type == 'error' and not NET.search(m.text) else None)
            pg.on('pageerror', lambda e: errs.append('%s: page error %s' % (name, e)))
            pg.goto(url); pg.wait_for_function('window.__wm && window.__wm.orientation', timeout=30000); pg.wait_for_timeout(1500)
            if pg.evaluate('__wm.orientation.shown().length'): bad.append('%s: clashes drawn before play (SR-02)' % name)
            pg.screenshot(path=os.path.join(a.out, '%s-1-opening.png' % name))
            # the busy month: February 1803, five events
            pg.evaluate("__wm.setTime(__wm.battle.time('1803-02-27'))"); pg.wait_for_timeout(900)
            st = pg.evaluate("({m:__wm.orientation.month(),n:__wm.orientation.shown().length,clock:document.getElementById('clock').textContent,held:__wm.orientation.held('XP1')})")
            if st['m'] != '1803-02' or st['clock'] != 'February 1803': bad.append('%s: clock says %r for 27 Feb 1803' % (name, st['clock']))
            if st['n'] != 10: bad.append('%s: %d clashes on the map on 27 Feb 1803, expected 10' % (name, st['n']))
            if st['held'] != 'contested': bad.append('%s: Testport held by %r on 27 Feb 1803, expected contested' % (name, st['held']))
            pg.screenshot(path=os.path.join(a.out, '%s-2-busy-month.png' % name))
            r1 = pg.evaluate("__wm.setTime(__wm.battle.time('1803-02-10')),__wm.orientation.rate()"); r0 = pg.evaluate("__wm.setTime(__wm.battle.time('1801-11-10')),__wm.orientation.rate()")
            if not r1 < r0: bad.append('%s: the busy month plays no slower than an empty one (%.1f against %.1f days a second)' % (name, r1, r0))
            # a disputed clash, picked on the pane
            pg.evaluate("__wm.setTime(__wm.battle.time('1801-09-20'))"); pg.wait_for_timeout(400)
            pg.evaluate("__wm.select('C:XC05')"); pg.wait_for_timeout(600)
            txt = pg.inner_text('#panel').lower()
            if 'the other reading' not in txt or 'disagree' not in txt: bad.append('%s: the disputed clash does not give both readings' % name)
            pg.screenshot(path=os.path.join(a.out, '%s-3-disputed.png' % name))
            pg.evaluate("__wm.select(null)")
            # the gap year
            pg.evaluate("__wm.setTime(__wm.battle.time('1802-06-15'))"); pg.wait_for_timeout(400)
            if pg.is_hidden('#offnote'): bad.append('%s: no gap note in 1802' % name)
            # the end
            pg.evaluate("__wm.setTime(__wm.battle.time('1803-04-15'))"); pg.wait_for_timeout(900)
            txt = pg.inner_text('#panel').lower()
            if 'wins, year by year' not in txt or 'who held what' not in txt: bad.append('%s: the closing pane lacks the wins or who held what: %r' % (name, txt[:300]))
            pg.screenshot(path=os.path.join(a.out, '%s-4-end.png' % name))
            # the event-by-event opening: half a second an event, a stop at the end of 1802 with the recap, then month by month
            pg.click('#restart'); pg.wait_for_timeout(400); pg.click('#play'); pg.wait_for_timeout(6000)
            st = pg.evaluate("({h:__wm.orientation.halted(),m:__wm.orientation.month(),cont:!document.getElementById('cont').hidden,p:document.getElementById('panel').innerText.toLowerCase()})")
            if not st['h'] or st['m'] != '1802-12' or not st['cont']: bad.append('%s: after 6 s of play no stop at the end of 1802 (%r)' % (name, {k: st[k] for k in ('h', 'm', 'cont')}))
            if 'who held what' not in st['p'] or '1801' not in st['p']: bad.append('%s: the stop at the end of 1802 lacks the recap' % name)
            pg.screenshot(path=os.path.join(a.out, '%s-6-stop-1802.png' % name))
            pg.click('#cont'); pg.wait_for_timeout(1500)
            st = pg.evaluate("({h:__wm.orientation.halted(),m:__wm.orientation.month(),r:__wm.orientation.rate()})")
            if st['h'] or st['m'] < '1803-01': bad.append('%s: Continue did not go on into 1803 (%r)' % (name, st))
            # play from the start for a few seconds: no errors, the clock moves month by month
            pg.click('#restart'); pg.wait_for_timeout(500); pg.click('#play'); pg.wait_for_timeout(4000)
            m = pg.evaluate('__wm.orientation.month()')
            if m < '1801-05': bad.append('%s: after 4 s of event-by-event play the clock is still at %s' % (name, m))
            pg.screenshot(path=os.path.join(a.out, '%s-5-playing.png' % name)); pg.close()
        br.close()
    for e in errs: print('  console', e)
    for b in bad: print('  FAIL', b)
    print('orientation page: %s; pictures in %s' % ('as designed' if not bad and not errs else '%d problem(s)' % (len(bad) + len(errs)), a.out))
    return 1 if bad or errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
