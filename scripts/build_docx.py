#!/usr/bin/env python3
"""Convertit un manuscrit Markdown en fichier Word (.docx) avec table des matières,
notes de bas de page, pages de partie, numéros de page, format A4 et césure.

Usage :
    python build_docx.py livre.md -o livre.docx

Dépendance : pandoc. La table des matières est un champ Word : à l'ouverture,
clic droit > Mettre à jour les champs.
"""
import argparse, re, subprocess, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REF = HERE / 'assets' / 'reference.docx'

def preprocess(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, flags=re.S)
    meta, body = (text[:m.end()], text[m.end():]) if m else ('', text)
    lang = 'fr'
    if meta:
        lm = re.search(r'^lang:\s*"?([\w-]+)', meta, flags=re.M)
        lang = lm.group(1) if lm else 'fr'
        if 'toc-title' not in meta:
            meta = meta.rstrip()[:-3] + f'toc-title: "{"Table des matières" if lang.startswith("fr") else "Contents"}"\n---\n'
    def part(mm):
        num, _, title = mm.group(1).partition(' — ')
        out = f'::: {{custom-style="Partie"}}\n{num}\n:::\n\n'
        if title:
            out += f'::: {{custom-style="Partie titre"}}\n{title}\n:::\n'
        return out
    body = re.sub(r'^# (.+)$', part, body, flags=re.M)        # parties
    body = re.sub(r'^(#{2,6}) ', lambda mm: '#' * (len(mm.group(1)) - 1) + ' ', body, flags=re.M)
    return meta + body

def post(path):
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; z.close()
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
              '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
    files['word/footer1.xml'] = footer.encode()
    rels = files['word/_rels/document.xml.rels'].decode()
    if 'footer1.xml' not in rels:
        rels = rels.replace('</Relationships>', '<Relationship Id="rIdFtr1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
    files['word/_rels/document.xml.rels'] = rels.encode()
    ct = files['[Content_Types].xml'].decode()
    if 'footer1.xml' not in ct:
        ct = ct.replace('</Types>', '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
    files['[Content_Types].xml'] = ct.encode()
    d = files['word/document.xml'].decode()
    sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFtr1"/><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1418" w:right="1361" w:bottom="1418" w:left="1361" w:header="709" w:footer="709" w:gutter="0"/><w:titlePg/></w:sectPr>')
    d = re.sub(r'<w:sectPr\b.*?</w:sectPr>', '', d, flags=re.S).replace('<w:sectPr />', '')
    files['word/document.xml'] = d.replace('</w:body>', sect + '</w:body>').encode()
    st = files['word/settings.xml'].decode()
    if 'autoHyphenation' not in st:
        st = re.sub(r'(<w:settings[^>]*>)', r'\1<w:autoHyphenation/>', st, count=1)
    files['word/settings.xml'] = st.encode()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as o:
        for n in ['[Content_Types].xml'] + [n for n in files if n != '[Content_Types].xml']:
            o.writestr(n, files[n])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manuscrit')
    ap.add_argument('-o', '--output', default=None)
    a = ap.parse_args()
    out = a.output or Path(a.manuscrit).stem + '.docx'
    md = preprocess(Path(a.manuscrit).read_text(encoding='utf-8'))
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as t:
        t.write(md)
    cmd = ['pandoc', t.name, '-o', out, '--toc', '--toc-depth=1']
    if REF.exists():
        cmd.append(f'--reference-doc={REF}')
    subprocess.run(cmd, check=True)
    post(out)
    print(f'Word écrit : {out}')

if __name__ == '__main__':
    main()
