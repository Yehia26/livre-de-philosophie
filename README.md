# livre-de-philosophie — un skill Claude

Ce skill apprend à Claude à écrire un livre de philosophie ou d'essai d'idées complet à partir d'une idée, même brève, et à le publier en **PDF format livre (140 × 210 mm)**, **PDF A4** et **Word**.

Il a été mis au point en écrivant *Éthique des situations. Vers une axiologie des attentes* (environ 210 pages), et reprend la méthode suivie : recherche multilingue, plan conceptuel, architecture adaptée au sujet, rédaction, évaluation par un expert, vérification complète des sources, mise en page.

## Ce que fait le skill

1. Reformule l'idée en thèse et en question directrice.
2. Fait l'**état de la littérature** sur le web, avec le plus d'ouvrages possible, au moins en anglais, en français et en allemand, et dresse la carte des positions.
3. Dresse un **plan conceptuel** (concepts, distinctions, principes, rivales, objections).
4. Déduit l'**architecture** du sujet et du débat : pas de plan type, mais deux ou trois structures possibles soumises à l'auteur.
5. **Rédige** chapitre par chapitre (style analytique accessible, longs paragraphes, exemples variés, notes).
6. Se soumet à une **évaluation d'expert** notée, puis corrige.
7. **Vérifie** chaque référence et la cohérence interne, sans jamais inventer de citation.
8. **Met en page** le livre avec les scripts fournis.

## Installation

**Sur claude.ai ou l'application Claude** : téléchargez le dépôt en `.zip` (bouton *Code → Download ZIP*), puis dans *Paramètres → Capacités → Skills*, ajoutez le fichier `.zip`. Demandez ensuite : « Écris un livre de philosophie à partir de cette idée : … ».

**Dans Claude Code** :

```bash
git clone https://github.com/Yehia26/livre-de-philosophie ~/.claude/skills/livre-de-philosophie
```

**Pour utiliser les scripts seuls** :

```bash
pip install weasyprint pyyaml fonttools brotli
python scripts/get_fonts.py                      # installe EB Garamond (licence SIL OFL)
python scripts/build_book.py assets/exemple.md -o exemple.pdf
python scripts/build_book.py assets/exemple.md --format a4 -o exemple-a4.pdf
python scripts/build_docx.py assets/exemple.md -o exemple.docx
```

Il faut aussi `pandoc` (https://pandoc.org) et, pour `get_fonts.py`, `npm`.

## Structure

```
SKILL.md                    instructions principales
references/recherche.md     recherche multilingue, corpus, carte des positions
references/methode.md       plan conceptuel, architecture adaptative, introduction, style, notes
references/evaluation.md    grille d'évaluation d'expert, vérification complète
references/manuscrit.md     conventions du manuscrit Markdown
scripts/build_book.py       Markdown → PDF livre ou A4 (WeasyPrint)
scripts/build_docx.py       Markdown → Word (pandoc)
scripts/get_fonts.py        téléchargement d'EB Garamond
assets/reference.docx       styles Word
assets/exemple.md           manuscrit d'exemple
```

## Licence

MIT pour le code et les textes du skill. La police EB Garamond, téléchargée par `get_fonts.py`, est sous licence SIL Open Font License.
