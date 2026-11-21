"""Build the playback pages.

Every battle's page is the same page (app/page.html) with that battle's battle file written into it (battle.json, in the one format
all battles share: docs/battle-file.md; tools/export_battles.py writes them). The pages share the app/ folder: the map library
(MapLibre GL JS), core.js (the map, the clock, reading a battle file), player.js (the playback) and core.css.

  python3 tools/build.py                     build playbacks/<battle>/index.html for the website (all battles)
  python3 tools/build.py ypres               one battle only
  python3 tools/build.py --bundle OUT        also write OUT/<battle>/ : the page with its own copy of app/ and its images, to host on its own
  python3 tools/build.py --single OUT        also write OUT/<battle>.html : one file with everything inside it, which opens from a folder with no web server
"""
import os, re, sys, json, html, base64, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTLES = ['gettysburg', 'trenton', 'ypres', 'manila']
APP_FILES = ['vendor/maplibre-gl.js', 'vendor/maplibre-gl.css', 'vendor/MAPLIBRE-LICENSE.txt', 'core.js', 'player.js', 'core.css']
HEAD = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">%s'
        '<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%%}[hidden]{display:none!important}</style></head><body>\n')
MIME = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}


def read(path):
    return open(path, encoding='utf-8').read()


SITE = 'https://mgm9000.github.io/WarMapper/'   # the main page; a page on the site links to it relatively, a single file (offline copy, artifact) to the site itself


def page(battle, app, home='../../'):
    """The page as one HTML document, with the shared files referenced under the path `app` and a link back to the main page at `home`."""
    d = os.path.join(ROOT, 'playbacks', battle)
    src = read(os.path.join(ROOT, 'app', 'page.html'))
    data = read(os.path.join(d, 'battle.json'))
    b = json.loads(data)
    assert src.count('__DATA__') == 1, battle
    for mark, text in (('__PAGETITLE__', b.get('playback', {}).get('page_title') or b['title']), ('__HEADING__', b['title']), ('__TAGLINE__', b.get('subtitle', ''))):
        src = src.replace(mark, html.escape(text, quote=False))
    out = src.replace('__DATA__', data.replace('</', '<\\/')).replace('__APP__', app).replace('__HOME__', home)
    title = re.search(r'<title>.*?</title>', out).group(0)
    return HEAD % title + out.replace(title, '', 1) + '\n</body></html>\n'


def images(battle):
    d = os.path.join(ROOT, 'playbacks', battle)
    return sorted(f for f in os.listdir(d) if os.path.splitext(f)[1].lower() in MIME)


def single(battle):
    """One self-contained file: the shared styles and scripts are written into the page and the images become data URIs."""
    out = page(battle, '__APP__', SITE).replace('<a class="home" href="%s">' % SITE, '<a class="home" href="%s" target="_blank" rel="noopener">' % SITE, 1)   # from an offline copy or an artifact, the site opens in a new tab
    app = os.path.join(ROOT, 'app')
    for name in ('vendor/maplibre-gl.css', 'core.css'):
        tag = '<link rel="stylesheet" href="__APP__/%s">' % name
        assert tag in out, name
        out = out.replace(tag, '<style>\n' + read(os.path.join(app, name)) + '\n</style>')
    for name in ('vendor/maplibre-gl.js', 'core.js', 'player.js'):
        tag = '<script src="__APP__/%s"></script>' % name
        js = read(os.path.join(app, name))
        assert tag in out and '</script' not in js, name
        out = out.replace(tag, '<script>\n' + js + '\n</script>')
    d = os.path.join(ROOT, 'playbacks', battle)
    assets = []
    for f in images(battle):
        b = base64.b64encode(open(os.path.join(d, f), 'rb').read()).decode('ascii')
        assets.append('"%s":"data:%s;base64,%s"' % (f, MIME[os.path.splitext(f)[1].lower()], b))
    marker = '<script id="data"'
    assert out.count(marker) == 1
    return out.replace(marker, '<script>window.WM_ASSETS={' + ','.join(assets) + '};</script>\n' + marker)


def main(argv):
    args = list(argv); bundle = single_dir = None
    if '--bundle' in args: i = args.index('--bundle'); bundle = args[i + 1]; del args[i:i + 2]
    if '--single' in args: i = args.index('--single'); single_dir = args[i + 1]; del args[i:i + 2]
    battles = args or BATTLES
    for b in battles:
        assert b in BATTLES, b
        html = page(b, '../../app')
        open(os.path.join(ROOT, 'playbacks', b, 'index.html'), 'w', encoding='utf-8').write(html)
        print(b, 'index.html', len(html.encode('utf-8')))
        if bundle:
            out = os.path.join(bundle, b)
            for f in APP_FILES:
                os.makedirs(os.path.dirname(os.path.join(out, 'app', f)), exist_ok=True)
                shutil.copyfile(os.path.join(ROOT, 'app', f), os.path.join(out, 'app', f))
            for f in images(b): shutil.copyfile(os.path.join(ROOT, 'playbacks', b, f), os.path.join(out, f))
            open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page(b, 'app', SITE))
        if single_dir:
            os.makedirs(single_dir, exist_ok=True)
            html = single(b)
            open(os.path.join(single_dir, b + '.html'), 'w', encoding='utf-8').write(html)
            print(b, 'single file', len(html.encode('utf-8')))


if __name__ == '__main__':
    main(sys.argv[1:])
