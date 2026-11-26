"""Check every quotation in a battle's pipeline script against the texts it was read from, with its page. Run before the pull request.

  python3 pipeline/checks/quote_check.py guilford_2026_11_26 --foot H=hatch.txt --pdf K=skinner.txt:20 --pdf C=report.txt:14 --ids H=S138 K=S144 C=S145

The battle's script (in pipeline/) must hold its rows as POS, HYP, SOURCES, UNITS, ROUTES and GAPS, as the Guilford Courthouse script does.
The texts are not in the repository (they are Morgan's copies): give each one a letter and a path.
  --foot X=file          a scan's text whose printed page number stands alone on a line at the foot of each page (the Internet Archive's text of a typescript)
  --pdf  X=file:offset   the output of `pdftotext -layout` (pages divided by form feeds); the PDF page is the printed page plus the offset
  --ids  X=S138 ...      which source each letter is, so a position row's source_pages can be compared

It prints (1) every quotation that is not found, or found only loosely, in any text, and (2) every quotation found on a page its row does not cite.
A quotation is anything between double quotation marks; it is split at "..." and pieces under four words are checked word for word.
Written 26 Nov 2026 after the Cowpens audit moved many page numbers (a scan that prints its page number at the foot shifts every citation by one).
"""
import argparse, difflib, importlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'recon'))


def norm(s): return re.sub(r'[^a-z0-9 ]', '', s.lower().replace('-', ' ').replace('’', '').replace("'", '')).split()


def foot(path, first=11):
    """Pages of a text whose page number closes the page."""
    out = []; page = []; cur = 0
    for ln in open(path, encoding='utf-8', errors='ignore').read().split('\n'):
        t = ln.strip()
        if re.fullmatch(r'\d{1,3}', t) and ((cur == 0 and int(t) == first) or (cur and 0 < int(t) - cur <= 3)):
            cur = int(t); out.append((cur, ' '.join(page))); page = []
        else: page.append(t)
    return out + [(cur + 1, ' '.join(page))]


def pdf(path, offset): return [(i + 1 - offset, pg) for i, pg in enumerate(open(path, encoding='utf-8', errors='ignore').read().split('\f'))]


def index(pages):
    words = []; where = []
    for p, t in pages:
        w = norm(t); words += w; where += [p] * len(w)
    pos = {}
    for i in range(len(words) - 2): pos.setdefault(tuple(words[i:i + 3]), []).append(i)
    return words, where, pos


def find(q, idx):
    """For each text: (how closely the best passage matches, 0 to 1; its page)."""
    qw = norm(q); best = {}
    for name, (words, where, pos) in idx.items():
        if len(qw) < 4:
            k = ' ' + ' '.join(qw) + ' '; best[name] = (1.0, None) if k in ' ' + ' '.join(words) + ' ' else (0, None); continue
        cands = {}
        for j in range(len(qw) - 2):
            for i in pos.get(tuple(qw[j:j + 3]), [])[:50]: cands[i - j] = cands.get(i - j, 0) + 1
        b = (0, None)
        for st in sorted(cands, key=lambda k: -cands[k])[:6]:
            for d in (-1, 0, 1, 2):
                st0 = max(0, st); r = difflib.SequenceMatcher(None, qw, words[st0:st0 + len(qw) + d], autojunk=False).ratio()
                if r > b[0]: b = (r, where[st0] if st0 < len(where) else None)
        best[name] = b
    return best


def quotes(s):
    out = []
    for q in re.findall(r'"([^"]*)"', s or ''): out += [x.strip() for x in re.split(r'\s*\.\.\.\s*|\s*\[[^\]]*\]\s*', q) if norm(x)]
    return out


def cited(pages, sid):
    out = set()
    for m in re.finditer(r'%s[^;]*' % sid, pages or ''):
        for a, b in re.findall(r'(\d{1,3})(?:-(\d{1,3}))?', re.sub(r'(plans?|Maps?|maps?) \d+', '', m.group(0)[len(sid):])):
            a = int(a); b = int(b) if b else a; out |= set(range(a, b + 1))
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('script'); ap.add_argument('--foot', nargs='*', default=[]); ap.add_argument('--pdf', nargs='*', default=[]); ap.add_argument('--ids', nargs='*', default=[])
    a = ap.parse_args(argv); M = importlib.import_module(a.script); idx = {}
    for x in a.foot: k, p = x.split('=', 1); idx[k] = index(foot(p))
    for x in a.pdf: k, p = x.split('=', 1); p, off = p.rsplit(':', 1); idx[k] = index(pdf(p, int(off)))
    sid = dict(x.split('=') for x in a.ids)
    rows = [(p['pos_id'], ' '.join(str(p.get(k) or '') for k in ('source_wording', 'notes')), p['source_pages']) for p in getattr(M, 'POS', [])]
    rows += [('time basis', t, '') for t in sorted({p['time_basis'] for p in getattr(M, 'POS', [])})]   # the clock's reasons cite their own pages in the text
    rows += [(h['hypothesis_id'], ' '.join(str(h.get(k) or '') for k in ('evidence_for', 'evidence_against', 'adopted_because', 'next_step')), '') for h in getattr(M, 'HYP', [])]
    rows += [(s['source_id'], s['notes'], '') for s in getattr(M, 'SOURCES', [])] + [(u[0], '%s %s' % (u[8] or '', u[11] or ''), '') for u in getattr(M, 'UNITS', [])]
    rows += [(r['route_id'], '%s %s' % (r['source_wording'], r.get('notes') or ''), '') for r in getattr(M, 'ROUTES', [])] + [(g[0], ' '.join(g[1:]), '') for g in getattr(M, 'GAPS', [])]
    seen = {}; loose = wrong = 0
    for rid, text, pages in rows:
        for q in quotes(text):
            k = ' '.join(norm(q))
            if k in seen: seen[k][0].append((rid, pages)); continue
            seen[k] = ([(rid, pages)], q, find(q, idx))
    print('(1) quotations not found, or found loosely')
    for k, (at, q, f) in seen.items():
        r, pg = max(f.values(), key=lambda v: v[0])
        if r < 0.9: loose += 1; print('  %-8s %-10s %s' % (at[0][0], 'NOT FOUND' if r < 0.6 else 'loose %.2f' % r, q[:110]))
    print('(2) quotations found on a page their position row does not cite')
    for k, (at, q, f) in seen.items():
        hits = {(n, v[1]) for n, v in f.items() if v[0] >= 0.85 and v[1] is not None and n in sid}
        for rid, pages in at:
            if pages and hits and not any(pg in cited(pages, sid[n]) for n, pg in hits):
                wrong += 1; print('  %-8s found %s; cites %s | %s' % (rid, ', '.join('%s p. %s' % (sid[n], pg) for n, pg in sorted(hits)), pages, q[:70]))
    print('%d quotations; %d loose or not found; %d on a page not cited' % (len(seen), loose, wrong))


if __name__ == '__main__':
    main(sys.argv[1:])
