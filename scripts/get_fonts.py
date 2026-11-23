#!/usr/bin/env python3
"""Télécharge EB Garamond (licence SIL OFL) depuis le paquet npm @fontsource/eb-garamond
et l'installe en .ttf dans assets/fonts/. À lancer une fois, avant build_book.py.

Dépendances : npm, fonttools et brotli (pip install fonttools brotli).
"""
import shutil, subprocess, tarfile, tempfile
from pathlib import Path
from fontTools.ttLib import TTFont

DEST = Path(__file__).resolve().parent.parent / 'assets' / 'fonts'

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['npm', 'pack', '@fontsource/eb-garamond'], cwd=tmp, check=True, capture_output=True)
        tgz = next(Path(tmp).glob('*.tgz'))
        with tarfile.open(tgz) as tf:
            tf.extractall(tmp, filter='data') if hasattr(tarfile, 'data_filter') else tf.extractall(tmp)
        files = Path(tmp) / 'package' / 'files'
        for w in (400, 500, 600):
            for st in ('normal', 'italic'):
                src = files / f'eb-garamond-latin-{w}-{st}.woff'
                f = TTFont(src); f.flavor = None
                f.save(DEST / f'eb-garamond-latin-{w}-{st}.ttf')
        lic = Path(tmp) / 'package' / 'LICENSE'
        if lic.exists():
            shutil.copy(lic, DEST / 'OFL.txt')
    print(f'Polices installées dans {DEST}')

if __name__ == '__main__':
    main()
