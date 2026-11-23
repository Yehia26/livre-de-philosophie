#!/usr/bin/env python3
"""Compose un manuscrit Markdown en PDF de livre (140 x 210 mm) ou en PDF A4.

Usage :
    python build_book.py livre.md -o livre.pdf [--format livre|a4] [--fonts DOSSIER]

Conventions du manuscrit : voir references/manuscrit.md.
Dépendances : pandoc, weasyprint (pip install weasyprint), pyyaml.
"""
import argparse, html as H, os, re, subprocess, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None
from weasyprint import HTML

# ---------------------------------------------------------------- lecture
def read_manuscript(path):
    text = Path(path).read_text(encoding='utf-8')
    meta = {}
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, flags=re.S)
    if m:
        block = m.group(1)
        if yaml:
            meta = yaml.safe_load(block) or {}
        else:
            for line in block.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"')
        text = text[m.end():]
    return meta, text

def md_to_html(md):
    r = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html5', '--wrap=none'],
                       input=md, capture_output=True, text=True, check=True)
    return r.stdout

# ---------------------------------------------------------------- notes
def footnotes_inline(src):
    """Remplace les appels de note pandoc par des notes de bas de page flottantes."""
    sec = re.search(r'<section[^>]*class="footnotes[^"]*"[^>]*>.*?</section>', src, flags=re.S)
    if not sec:
        return src
    notes = {}
    for li in re.finditer(r'<li id="fn(\d+)"[^>]*>(.*?)</li>', sec.group(0), flags=re.S):
        body = li.group(2)
        body = re.sub(r'<a href="#fnref\d+"[^>]*>.*?</a>', '', body, flags=re.S)
        body = re.sub(r'</?p>', ' ', body).strip()
        notes[li.group(1)] = body
    src = src[:sec.start()] + src[sec.end():]
    src = re.sub(r'<a href="#fn(\d+)"[^>]*class="footnote-ref"[^>]*>.*?</a>',
                 lambda m: f'<span class="fn">{notes.get(m.group(1), "")}</span>', src, flags=re.S)
    return src

# ---------------------------------------------------------------- typographie
def fr_typo(text):
    text = text.replace('&#39;', '’').replace("'", '’')
    text = re.sub(r'\s+([;:!?»])', ' ' + r'\1', text)
    text = re.sub(r'«\s+', '« ', text)
    text = re.sub(r'(?<![\w-])([IVX]{1,5})(e|re|er)(?=[\s,.;])', r'\1<sup class="ord">\2</sup>', text)
    text = re.sub(r'(?<![\w-])(\d{1,2})(e|re|er)(?=[\s,.;])', r'\1<sup class="ord">\2</sup>', text)
    return text.replace('...', '…')

def en_typo(text):
    return text.replace('...', '…')

def on_text(src, fn):
    pieces = re.split(r'(<[^>]+>)', src)
    for i, p in enumerate(pieces):
        if p and not p.startswith('<'):
            pieces[i] = fn(p)
    return ''.join(pieces)

# ---------------------------------------------------------------- structure
PART_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)
CHAP_RE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)

def strip_tags(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def structure(src, labels):
    toc = []
    def part(m):
        txt = strip_tags(m.group(1))
        num, _, title = txt.partition(' — ')
        if not title:
            num, title = '', txt
        toc.append(('part', num, title))
        return (f'<section class="partie"><p class="pnum">{H.escape(num)}</p>'
                f'<p class="ptitre">{H.escape(title)}</p></section>')
    def chap(m):
        txt = strip_tags(m.group(1))
        i = len(toc)
        mm = re.match(r'((?:Chapitre|Chapter)\s+\d+)\s+—\s+(.*)', txt)
        if mm:
            label, title = mm.group(1), mm.group(2)
            num = re.sub(r'\D', '', label)
            toc.append(('chap', f'c{i}', num, title))
            return (f'<h2 id="c{i}" class="chap"><span class="label">{H.escape(label)}</span>'
                    f'<span class="titre">{H.escape(title)}</span></h2>')
        mm = re.match(r'(Conclusion|Annexe|Appendix)\s+—\s+(.*)', txt)
        if mm:
            toc.append(('other', f'c{i}', '', txt))
            return (f'<h2 id="c{i}" class="chap"><span class="label">{H.escape(mm.group(1))}</span>'
                    f'<span class="titre">{H.escape(mm.group(2))}</span></h2>')
        toc.append(('other', f'c{i}', '', txt))
        return f'<h2 id="c{i}" class="chap nolabel"><span class="titre">{H.escape(txt)}</span></h2>'
    # Parts and chapters must be processed in document order to keep the TOC ordered.
    out, pos = [], 0
    for m in re.finditer(r'<h1[^>]*>.*?</h1>|<h2[^>]*>.*?</h2>', src, flags=re.S):
        out.append(src[pos:m.start()])
        g = m.group(0)
        out.append(part(PART_RE.match(g)) if g.startswith('<h1') else chap(CHAP_RE.match(g)))
        pos = m.end()
    out.append(src[pos:])
    src = ''.join(out)
    src = re.sub(r'(</h2>)\s*<p>', r'\1<p class="first">', src)
    for names, cls in ((labels['gloss'], 'gloss'), (labels['biblio'], 'biblio')):
        for name in names:
            i = src.find(f'<span class="titre">{name}</span></h2>')
            if i < 0:
                continue
            k = src.find('<h2', i + 10)
            k = len(src) if k < 0 else k
            seg = src[i:k].replace('<p>', f'<p class="{cls}">').replace('<p class="first">', f'<p class="{cls} first">')
            src = src[:i] + seg + src[k:]
    return src, toc

def lead_words(src):
    def lead(m):
        txt = m.group(2)
        acc = []
        for w in txt.split(' '):
            acc.append(w)
            if len(acc) >= 3 or re.search(r'[,;:.?!]$', w):
                break
        head = ' '.join(acc); rest = txt[len(head):]; tail = ''
        mm = re.match(r'^(.*?)([,;:.?! ]+)$', head)
        if mm:
            head, tail = mm.group(1), mm.group(2)
        return f'{m.group(1)}<span class="lead">{head}</span>{tail}{rest}'
    return re.sub(r'(</h2><p class="first">)([^<]{20,})', lead, src)

def toc_html(toc, title):
    rows = []
    for it in toc:
        if it[0] == 'part':
            rows.append(f'<li class="tpart"><span class="tp1">{H.escape(it[1])}</span><br>{H.escape(it[2])}</li>')
        else:
            _, cid, num, t = it
            n = f'<span class="tnum">{num}.</span> ' if num else ''
            cls = 'tchap' if num else 'tother'
            rows.append(f'<li class="{cls}"><a href="#{cid}">{n}{H.escape(t)}</a></li>')
    return (f'<section class="toc"><h2 class="tochead"><span class="titre">{H.escape(title)}</span></h2>'
            f'<ul>{"".join(rows)}</ul></section>')

# ---------------------------------------------------------------- polices
def font_faces(fonts_dir):
    cands = [fonts_dir] if fonts_dir else []
    here = Path(__file__).resolve().parent.parent
    cands += [here / 'assets' / 'fonts', Path.home() / '.fonts', Path.home() / '.local/share/fonts']
    faces = []
    for d in cands:
        if not d or not Path(d).is_dir():
            continue
        for w in (400, 500, 600):
            for st in ('normal', 'italic'):
                for ext in ('ttf', 'otf', 'woff', 'woff2'):
                    f = Path(d) / f'eb-garamond-latin-{w}-{st}.{ext}'
                    if f.exists():
                        faces.append(f'@font-face {{ font-family: "BookSerif"; src: url("{f.resolve().as_uri()}"); '
                                     f'font-weight: {w}; font-style: {st}; }}')
                        break
        if faces:
            break
    if not faces:
        print('Avertissement : EB Garamond introuvable (lancez scripts/get_fonts.py) ; police serif du système utilisée.',
              file=sys.stderr)
    return '\n'.join(faces)

# ---------------------------------------------------------------- CSS
def css(fmt, running, faces, lang):
    if fmt == 'a4':
        page = '@page { size: A4; margin: 25mm 24mm 25mm 24mm; @bottom-center { content: counter(page); font: 10pt "BookSerif", serif; } @footnote { border-top: 0.4pt solid #888; padding-top: 3pt; margin-top: 10pt; } }'
        sides, body_size, chap_top = '', '11.5pt', '30mm'
    else:
        page = '@page { size: 140mm 210mm; margin: 19mm 16mm 22mm 20mm; @bottom-center { content: counter(page); font: 9.5pt "BookSerif", serif; color: #333; } @footnote { border-top: 0.4pt solid #888; padding-top: 3pt; margin-top: 9pt; } }'
        sides = (f'@page :left {{ margin-left: 16mm; margin-right: 20mm; @top-center {{ content: "{running}"; font: italic 9pt "BookSerif", serif; color: #444; }} }}\n'
                 '@page :right { margin-left: 20mm; margin-right: 16mm; @top-center { content: string(chap, first-except); font: italic 9pt "BookSerif", serif; color: #444; } }')
        body_size, chap_top = '10.6pt', '28mm'
    return faces + '\n' + page + '\n' + sides + r'''
@page :blank { @top-center { content: none; } @bottom-center { content: none; } }
@page front { @top-center { content: none; } @bottom-center { content: none; } }
@page partie { @top-center { content: none; } @bottom-center { content: none; } }
@page tocp { @top-center { content: none; } }
body { font-family: "BookSerif", "EB Garamond", "DejaVu Serif", serif; font-size: BODY; line-height: 1.38; color: #111;
       font-variant-numeric: oldstyle-nums; font-kerning: normal; }
p { margin: 0; text-align: justify; text-indent: 1.3em; hyphens: auto; orphans: 2; widows: 2; }
p.first { text-indent: 0; }
strong { font-weight: 600; }
sup.ord { font-size: 0.68em; vertical-align: 0.42em; line-height: 0; }
.fauxtitre, .titre-page, .epigraphe { page: front; break-after: right; }
.fauxtitre p { text-indent: 0; text-align: center; margin-top: 52mm; font-size: 15pt; letter-spacing: 1.5pt; }
.titre-page p { text-indent: 0; text-align: center; }
.titre-page .t0 { margin-top: 30mm; font-size: 12pt; letter-spacing: 1pt; }
.titre-page .t1 { margin-top: 12mm; font-size: 26pt; font-weight: 500; line-height: 1.15; }
.titre-page .t2 { margin-top: 7mm; font-size: 13pt; font-style: italic; }
.epigraphe blockquote { margin: 55mm 0 0 30mm; font-style: italic; }
.epigraphe p { text-indent: 0; text-align: left; }
.epigraphe .src { font-style: normal; margin-top: 3mm; font-size: 0.9em; text-align: right; }
section.partie { page: partie; break-before: right; break-after: right; text-align: center; }
section.partie p { text-indent: 0; text-align: center; }
.pnum { margin-top: 58mm; font-size: 10pt; letter-spacing: 2.5pt; text-transform: uppercase; }
.ptitre { margin-top: 6mm; font-size: 18pt; font-style: italic; line-height: 1.25; }
h2.chap { break-before: right; margin: CHAPTOP 0 12mm 0; text-align: center; font-weight: normal; counter-reset: footnote; }
h2.chap .label { display: block; font-size: 9.5pt; letter-spacing: 2.5pt; text-transform: uppercase; margin-bottom: 5mm; }
h2.chap .titre { display: block; font-size: 17pt; line-height: 1.2; font-style: italic; string-set: chap content(); }
h2.chap::after { content: "❧"; display: block; font-size: 11pt; margin-top: 6mm; color: #555; font-style: normal; }
span.lead { text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.7pt; }
h3 { font-size: 1em; font-weight: normal; font-style: italic; text-align: center; margin: 7mm 0 3mm; break-after: avoid; }
blockquote { margin: 3mm 6mm; font-size: 0.95em; }
.fn { float: footnote; font-size: 8.2pt; line-height: 1.28; text-align: justify; text-indent: 0; font-style: normal;
      font-weight: normal; font-variant: normal; letter-spacing: 0; text-transform: none; }
::footnote-call { content: counter(footnote); vertical-align: 0.38em; font-size: 0.68em; line-height: 0; }
::footnote-marker { content: counter(footnote) ".\2002"; }
p.gloss { text-indent: -1.3em; padding-left: 1.3em; margin-bottom: 1.6mm; }
p.biblio { font-size: 0.89em; text-indent: -1.3em; padding-left: 1.3em; margin-bottom: 1.2mm; text-align: left; }
section.toc { page: tocp; }
h2.tochead { break-before: right; text-align: center; font-weight: normal; margin: 28mm 0 10mm; string-set: chap content(); }
h2.tochead .titre { font-size: 17pt; font-style: italic; }
.toc ul { list-style: none; padding: 0; margin: 0; }
.toc li { text-indent: 0; font-size: 10pt; margin: 0 0 1.6mm; text-align: left; }
.toc li.tpart { text-align: center; margin: 5mm 0 3mm; font-style: italic; }
.toc li.tpart .tp1 { font-style: normal; font-size: 8.5pt; letter-spacing: 2pt; text-transform: uppercase; }
.toc li.tchap, .toc li.tother { padding-left: 1.4em; text-indent: -1.4em; }
.toc .tnum { display: inline-block; width: 1.4em; text-indent: 0; }
.toc a::after { content: leader(" . ") target-counter(attr(href), page); }
a { color: inherit; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin: 4mm 0 5mm; font-size: 7.5pt; line-height: 1.22; page-break-inside: avoid; }
th, td { border-top: 0.4pt solid #888; border-bottom: 0.4pt solid #888; padding: 1.6pt 2pt; vertical-align: top; text-align: left; }
td p, th p { text-indent: 0; text-align: left; }
'''.replace('BODY', body_size).replace('CHAPTOP', chap_top)

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manuscrit')
    ap.add_argument('-o', '--output', default=None)
    ap.add_argument('--format', choices=['livre', 'a4'], default='livre')
    ap.add_argument('--fonts', default=None, help='dossier contenant eb-garamond-latin-*.ttf')
    a = ap.parse_args()

    meta, md = read_manuscript(a.manuscrit)
    lang = str(meta.get('lang', 'fr'))
    fr = lang.startswith('fr')
    labels = {'gloss': ['Glossaire', 'Glossary'], 'biblio': ['Bibliographie', 'Bibliography']}
    title = meta.get('title', 'Sans titre')
    subtitle = meta.get('subtitle', '')
    author = meta.get('author', '')
    running = meta.get('running_head', title).replace('"', '\\"')

    src = md_to_html(md)
    src = footnotes_inline(src)
    src, toc = structure(src, labels)
    src = on_text(src, fr_typo if fr else en_typo)
    src = lead_words(src)

    front = f'<section class="fauxtitre"><p>{H.escape(title)}</p></section><section class="titre-page">'
    if author:
        front += f'<p class="t0">{H.escape(author)}</p>'
    front += f'<p class="t1">{H.escape(title)}</p>'
    if subtitle:
        front += f'<p class="t2">{H.escape(subtitle)}</p>'
    front += '</section>'
    if meta.get('epigraph'):
        front += (f'<section class="epigraphe"><blockquote><p>{H.escape(meta["epigraph"])}</p>'
                  f'<p class="src">{meta.get("epigraph_source", "")}</p></blockquote></section>')

    toc_title = 'Table des matières' if fr else 'Contents'
    doc = (f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><style>'
           f'{css(a.format, running, font_faces(a.fonts), lang)}</style></head>'
           f'<body>{front}{src}{toc_html(toc, toc_title)}</body></html>')
    out = a.output or (Path(a.manuscrit).stem + ('-livre.pdf' if a.format == 'livre' else '-a4.pdf'))
    HTML(string=doc, base_url=os.getcwd()).write_pdf(out)
    print(f'PDF écrit : {out} ({len(toc)} entrées de table)')

if __name__ == '__main__':
    main()
