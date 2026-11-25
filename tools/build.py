"""Build the playback pages.

Every battle's page is the same page (app/page.html) with that battle's battle file written into it (battle.json, in the one format
all battles share: docs/battle-file.md; tools/export_battles.py writes them). The pages share the app/ folder: the map library
(MapLibre GL JS), core.js (the map, the clock, reading a battle file), player.js (the playback) and core.css.

  python3 tools/build.py                     build playbacks/<battle>/index.html for the website (all battles), and the course pages
  python3 tools/build.py ypres               one battle only
  python3 tools/build.py courses             the course pages only: courses/<course>/index.html, from courses/<course>/course.json
                                             and the template courses/page.html (format: courses/README.md)
  python3 tools/build.py --bundle OUT        also write OUT/<battle>/ : the page with its own copy of app/ and its images, to host on its own
  python3 tools/build.py --single OUT        also write OUT/<battle>.html : one file with everything inside it, which opens from a folder with no web server
"""
import os, re, sys, json, html, base64, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTLES = ['gettysburg', 'trenton', 'ypres', 'manila', 'luzon1899', 'cowpens']
APP_FILES = ['vendor/maplibre-gl.js', 'vendor/maplibre-gl.css', 'vendor/MAPLIBRE-LICENSE.txt', 'core.js', 'player.js', 'core.css']
HEAD = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">%s'
        '<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%%}[hidden]{display:none!important}</style></head><body>\n')
MIME = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}


def read(path):
    return open(path, encoding='utf-8').read()


SITE = 'https://mgm9000.github.io/WarMapper/'   # the main page; a page on the site links to it relatively, a single file (offline copy, artifact) to the site itself


def page(battle, app, home='../../', folder=None):
    """The page as one HTML document, with the shared files referenced under the path `app` and a link back to the main page at `home`.
    `folder` is where the battle file is, if not playbacks/<battle> (the orientation test, tests/orientation/demo)."""
    d = folder or os.path.join(ROOT, 'playbacks', battle)
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


# ---- course pages: courses/<course>/course.json + courses/page.html -> courses/<course>/index.html ----------------------------------
MONTH3 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
RIGHTS_CLASS = {'public domain': 'pd', 'in copyright': 'cr', 'not confirmed': 'nc'}
ACCESS_WORDS = {'link': 'Link', 'canvas': 'On Canvas (no link)', 'book': 'A book to buy (no link)'}


def esc(t):
    return html.escape(str(t), quote=True)


def t24(text):
    """Times are written in 24-hour format everywhere on the site: '11:59 pm' becomes '23:59', '8 am' becomes '08:00'."""
    def one(m):
        h, mi, ap = int(m.group(1)), m.group(2) or '00', m.group(3).lower()
        h = h % 12 + (12 if ap == 'p' else 0)
        return '%02d:%s' % (h, mi)
    return re.sub(r'\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\b\.?', one, text, flags=re.I)


def short_date(iso):
    d = datetime.date.fromisoformat(iso)
    return '%s %d %s' % (d.strftime('%a'), d.day, MONTH3[d.month - 1])


def validate_course(c, cdir):
    """The rules the course file has to keep (README of the courses folder): stop the build, saying which entry is at fault."""
    ids = [e['id'] for e in c['entries']]
    assert len(ids) == len(set(ids)), 'duplicate entry ids in %s' % cdir
    for e in c['entries']:
        assert e['kind'] in ('class', 'due', 'exam'), e['id']
        d = datetime.date.fromisoformat(e['date'])
        assert d.strftime('%A') == e['weekday'], '%s: %s is not a %s' % (e['id'], e['date'], e['weekday'])
        assert e.get('date_status'), '%s: date_status missing (a date that is not confirmed says "placeholder: update")' % e['id']
        for r in e.get('readings', []):
            assert r['rights']['hosted'] is False, '%s: nothing is hosted from a reading (%s)' % (e['id'], r['id'])
            assert r['rights']['status'] in RIGHTS_CLASS, '%s: rights status %r' % (e['id'], r['rights']['status'])
            if r['access'] == 'link':
                assert r['links'], '%s: a linked reading has no link (%s)' % (e['id'], r['id'])
                assert all(l['url'].startswith('https://') for l in r['links']), r['id']
            else:
                assert not r['links'], '%s: Canvas-only and book readings are named with no link (%s)' % (e['id'], r['id'])
        for slot in e.get('playbacks', []):
            if slot.get('playback'):
                assert os.path.exists(os.path.join(ROOT, 'playbacks', slot['playback'], 'index.html')), '%s: playback %r is not built' % (slot['id'], slot['playback'])
    nums = [e['number'] for e in c['entries'] if e['kind'] == 'class']
    assert nums == list(range(1, len(nums) + 1)), 'class numbers must run 1, 2, 3 ...'
    slot_ids = [x['id'] for e in c['entries'] for x in e.get('playbacks', [])]
    assert len(slot_ids) == len(set(slot_ids)), 'duplicate playback slot ids'
    for e in c['entries']:
        for x in e.get('playbacks', []):
            for k in x.get('children', []) + ([x['parent']] if x.get('parent') else []):
                assert k in slot_ids, '%s: %s is not a slot' % (x['id'], k)


def render_reading(r):
    out = ['<li id="%s">' % esc(r['id']), '<p class="rt">%s</p>' % esc(r['text']), '<p class="meta">']
    rs = r['rights']
    out.append('<span class="badge %s">%s</span>' % (RIGHTS_CLASS[rs['status']], esc(rs['status'].capitalize())))
    out.append('<span>%s</span>' % esc(r['kind'][0].upper() + r['kind'][1:]))
    if r['access'] != 'link':
        out.append('<span class="where">%s</span>' % esc(ACCESS_WORDS[r['access']]))
    out.append('</p>')
    if r['links']:
        out.append('<ul class="links">' + ''.join('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (esc(l['url']), esc(l['label'])) for l in r['links']) + '</ul>')
    if r.get('editor_note'):
        out.append('<p class="enote">Note: %s</p>' % esc(r['editor_note']))
    out.append('</li>')
    return ''.join(out)


def render_slot(slot, titles):
    built = bool(slot.get('playback'))
    out = ['<div class="slot%s" id="slot-%s" data-slot="%s" data-kind="%s">' % (' built' if built else '', esc(slot['id']), esc(slot['id']), esc(slot['kind']))]
    out.append('<p class="kind">%s</p><p class="st">%s</p><p class="sd">%s. Reading: %s.</p>' % (esc(slot['kind'].capitalize()), esc(slot['title']), esc(slot['dates']), esc(slot['amh'])))
    if slot.get('children'):
        out.append('<p class="sub">Battles in this campaign: %s</p>' % ', '.join('<a href="#slot-%s">%s</a>' % (esc(k), esc(titles[k])) for k in slot['children']))
    if built:
        out.append('<p class="state"><a href="../../playbacks/%s/">Open the playback</a></p>' % esc(slot['playback']))
    else:
        out.append('<p class="state">Not built yet</p>')
    out.append('</div>')
    return ''.join(out)


def render_entry(e, titles):
    when = '<span>%s</span><time datetime="%s">%s</time>' % (esc(e['weekday']), esc(e['date']), esc(short_date(e['date']).split(' ', 1)[1]))
    if e.get('time'):
        when += '<span>%s</span>' % esc(e['time'])
    when += '<span class="placeholder">%s</span>' % esc(e['date_status'])
    if e['kind'] == 'class':
        head = '<p class="when"><span class="num">Class %d</span>%s</p>' % (e['number'], when)
        out = ['<article class="day%s" id="%s">' % (' exam' if e.get('exam') else '', esc(e['id'])), head, '<h3>%s</h3>' % esc(e['title'])]
        if e['readings']:
            out.append('<h4>Readings</h4><ul class="readings">' + ''.join(render_reading(r) for r in e['readings']) + '</ul>')
        if e.get('syllabus_reading_context'):
            out.append('<p class="snote">%s</p>' % esc(t24(e['syllabus_reading_context'])))
        for n in e.get('syllabus_notes', []):
            out.append('<p class="snote">%s</p>' % esc(t24(n)))
        if e.get('playbacks'):
            out.append('<h4>Playbacks</h4><div class="slots">' + ''.join(render_slot(s, titles) for s in e['playbacks']) + '</div>')
        out.append('<details><summary>The syllabus’s own wording</summary><p>%s</p><p>%s</p></details>' % (esc(e['syllabus_heading']), esc(e['syllabus_reading_line'] or '(no reading)')))
        out.append('</article>')
        return ''.join(out)
    kind = 'Due' if e['kind'] == 'due' else 'Exam'
    out = ['<aside class="due" id="%s">' % esc(e['id']), '<p class="when"><span class="num">%s</span>%s</p>' % (kind, when), '<h3>%s</h3>' % esc(e['title'])]
    if e.get('note'):
        out.append('<p class="snote">%s</p>' % esc(e['note']))
    out.append('</aside>')
    return ''.join(out)


def course_page(cdir):
    """courses/<course>/index.html: every class day with its readings, rights and playback slots, written from course.json."""
    c = json.load(open(os.path.join(cdir, 'course.json'), encoding='utf-8'))
    assert c['format'] == 'warmapper-course/1', c['format']
    validate_course(c, cdir)
    tpl = read(os.path.join(ROOT, 'courses', 'page.html'))
    title = '%s %s: course guide' % (c['code'], c['title'])
    header = [
        '    <p class="eyebrow">Course guide</p>',
        '    <h1>%s<br>%s</h1>' % (esc(c['code']), esc(c['title'])),
        '    <p class="lead">A battlefield study guide for %s: each class day lists its readings and, as they are built, the battle playbacks that go with it, on maps drawn at the time and on today’s ground.</p>' % esc(c['audience']),
        '    <div class="note"><p><b>Term dates are not yet known.</b> Every date is a placeholder marked “update”. Class days are numbered, and meet on %s, %s.</p>' % (esc(' and '.join(c['meets']['weekdays'])), esc(t24(c['meets']['time'])))
        + '<p>Readings are text and links only: nothing copyrighted is hosted here. Readings on Canvas or in books are named with no link.</p></div>',
    ]
    parts = []
    for e in c['entries']:
        if e['kind'] == 'class' and (not parts or parts[-1][0] != e['part']):
            parts.append([e['part'], []])
        if parts:
            parts[-1][1].append(e)
    nav = '    <nav class="jump" aria-label="Parts of the course"><ul>' + ''.join('<li><a href="#part-%d">%s</a></li>' % (i + 1, esc(p.split(':')[0])) for i, (p, _) in enumerate(parts)) + '</ul></nav>'
    header.append(nav)
    titles = {x['id']: x['title'] for e in c['entries'] for x in e.get('playbacks', [])}
    body = []
    for i, (p, es) in enumerate(parts):
        body.append('    <section aria-labelledby="part-%d"><h2 id="part-%d">%s</h2>' % (i + 1, i + 1, esc(p)))
        body.extend('      ' + render_entry(e, titles) for e in es)
        body.append('    </section>')
    flags = ''.join('<li>%s</li>' % esc(f) for f in c.get('syllabus_flags', []))
    body.append('    <details><summary>Notes on the syllabus</summary><ul>%s</ul><p>%s</p></details>' % (flags, esc(c['term']['quizzes'])))
    footer = ['    <p>%s</p>' % esc(c['reading_rules']),
              '    <p>Prototype: none of the history on WarMapper has been checked by a historian. Data, sources and code: <a href="https://github.com/mgm9000/WarMapper">github.com/mgm9000/WarMapper</a></p>']
    out = tpl
    for mark, text in (('__PAGETITLE__', esc(title)), ('__DESCRIPTION__', esc('%s: readings for each class day and the WarMapper battle playbacks that go with them.' % title)), ('__HOME__', '../../')):
        out = out.replace(mark, text)
    out = out.replace('__HEADER__', '\n'.join(header)).replace('__BODY__', '\n'.join(body)).replace('__FOOTER__', '\n'.join(footer))
    return out


def build_courses():
    root = os.path.join(ROOT, 'courses')
    for name in sorted(os.listdir(root)):
        cdir = os.path.join(root, name)
        if os.path.exists(os.path.join(cdir, 'course.json')):
            out = course_page(cdir)
            open(os.path.join(cdir, 'index.html'), 'w', encoding='utf-8').write(out)
            print('courses/%s' % name, 'index.html', len(out.encode('utf-8')))


def main(argv):
    args = list(argv); bundle = single_dir = None
    if '--bundle' in args: i = args.index('--bundle'); bundle = args[i + 1]; del args[i:i + 2]
    if '--single' in args: i = args.index('--single'); single_dir = args[i + 1]; del args[i:i + 2]
    only_courses = 'courses' in args
    if only_courses: args.remove('courses')
    battles = args or ([] if only_courses else BATTLES)
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
    if only_courses or not argv:
        build_courses()


if __name__ == '__main__':
    main(sys.argv[1:])
