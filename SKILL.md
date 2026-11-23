---
name: livre-de-philosophie
description: Écrire un livre de philosophie ou d'essai d'idées complet à partir d'une idée, même brève, appuyé sur une recherche bibliographique étendue en anglais, français et allemand, avec une architecture adaptée au sujet, puis le publier en PDF livre, PDF A4 et Word. À utiliser quand quelqu'un veut transformer une intuition, une thèse ou une théorie en ouvrage argumenté.
---

# Livre de philosophie à partir d'une idée

Ce skill transforme une idée (trois lignes ou trois pages) en un livre de philosophie ou de pensée : une thèse défendue pas à pas, avec ses concepts, ses arguments, ses cas, ses objections et ses sources vérifiées. Il produit un manuscrit, puis un PDF au format livre (140 × 210 mm), un PDF A4 et un fichier Word.

Le livre défend une thèse. Ce n'est ni un cours d'histoire de la philosophie ni une compilation d'opinions. Les auteurs y interviennent parce qu'ils ont défendu une réponse à la question du livre, pas parce qu'ils figurent au programme.

## Déroulé

Suivre les étapes dans l'ordre. La recherche vient avant le plan : c'est l'état de la littérature qui décide de la forme du livre.

1. **Comprendre l'idée.** Reformuler en une phrase la thèse, et en une question la question directrice. Si l'idée est trop vague pour cela, poser au plus trois questions (thèse visée, public, longueur). Sinon, prendre les valeurs par défaut : français, public cultivé non spécialiste, style analytique accessible.
2. **État de la littérature.** Rechercher sur le web le plus d'ouvrages et d'articles possible sur la question, **au moins en anglais, en français et en allemand**, et dans d'autres langues si le sujet l'exige. Tenir un fichier de corpus, puis dresser la carte des positions : familles de réponses, lignes de partage, débats propres à une tradition, lacunes. Suivre `references/recherche.md` (lexique multilingue, sources par langue, planchers de volume, statut de lecture de chaque texte).
3. **Plan conceptuel.** Dresser la carte des concepts de la théorie : définitions, distinction-clé, principes, fondement, rivales, objections, cas. Voir `references/methode.md`, section « Plan conceptuel ».
4. **Architecture.** Déduire la structure du livre de la nature de l'idée, de la carte des positions et de la taille du corpus. Il n'y a pas de plan type : proposer deux ou trois architectures justifiées et en recommander une. Voir `references/methode.md`, section « Architecture ». Les étapes 2 à 4 forment un point de contrôle : montrer à l'auteur le bilan du corpus, la carte des positions, le plan conceptuel et les architectures possibles, et attendre son accord avant de rédiger, parce qu'un plan faux coûte un livre entier.
5. **Rédaction.** Rédiger chapitre par chapitre, l'introduction en dernier ou réécrite à la fin. Respecter les règles de style de `references/methode.md` : longs paragraphes explicatifs, pas d'intertitres dans les chapitres, titres naturels, exemples variés, notes par chapitre. Citer les auteurs dans leur langue d'origine quand c'est utile, avec sa propre traduction signalée. Pour un livre long, écrire et enregistrer chaque chapitre avant de passer au suivant.
6. **Évaluation par un expert.** Relire le livre dans le rôle d'un chercheur reconnu du domaine, qui maîtrise la tradition analytique et la tradition continentale, et le noter selon la grille de `references/evaluation.md`. Lister les faiblesses numérotées, les corriger, puis refaire une évaluation. Viser au moins deux tours.
7. **Vérification complète.** Vérifier chaque référence et chaque citation, puis la cohérence interne. Voir `references/evaluation.md`, section « Vérification ». Corriger et faire un rapport : confirmé, corrigé, non vérifiable.
8. **Mise en forme.** Écrire le manuscrit selon `references/manuscrit.md`, puis lancer les scripts (section suivante). Ouvrir le PDF et regarder quelques pages avant de le livrer.

À la fin de chaque étape, dire à l'auteur ce qui a été fait en une ou deux phrases et lui proposer la suite.

## Règles absolues sur les sources

- Ne jamais inventer une citation, une page, une date ou une référence. Une citation entre guillemets n'est écrite que si sa formulation et sa page ont été vérifiées (recherche web ou texte fourni).
- À défaut de vérification, paraphraser et citer l'ouvrage sans page, ou signaler la lacune à l'auteur.
- Traduire soi-même et l'indiquer (« Je traduis ») plutôt qu'attribuer une traduction publiée non vérifiée.
- Pour les faits d'actualité et les textes de loi, vérifier sur une source primaire (journal officiel, Légifrance, décision publiée).

## Mise en forme : les scripts

Les scripts sont dans `scripts/`. Ils prennent un manuscrit Markdown qui suit les conventions de `references/manuscrit.md`.

```bash
pip install weasyprint pyyaml fonttools brotli --break-system-packages   # une fois
python scripts/get_fonts.py                                              # une fois : EB Garamond (licence OFL)
python scripts/build_book.py livre.md -o livre.pdf                       # PDF livre 140 × 210 mm
python scripts/build_book.py livre.md --format a4 -o livre-a4.pdf        # PDF A4
python scripts/build_docx.py livre.md -o livre.docx                      # Word
```

Le PDF livre comporte un faux-titre, une page de titre, une épigraphe facultative, une page par partie, des ouvertures de chapitre centrées, des titres courants, des notes en bas de page, la typographie française (espaces insécables, apostrophes, ordinaux) et une table des matières finale avec numéros de page. Le Word a une table des matières à mettre à jour à l'ouverture (clic droit, « Mettre à jour les champs »).

Si le skill est utilisé sans accès aux scripts (par exemple sur claude.ai sans le dépôt), rédiger le livre dans un document, puis produire le PDF et le Word avec les outils disponibles en respectant la même mise en page.

## Après la livraison

L'auteur voudra souvent réorienter le livre : changer le titre, déplacer l'exemple d'ouverture, renforcer une thèse, intégrer une objection. Pour chaque demande :
- chercher tous les passages concernés (introduction, chapitres, conclusion, glossaire), pas seulement le premier ;
- modifier, puis vérifier que les renvois et le glossaire restent cohérents ;
- régénérer les trois fichiers et dire en quelques lignes ce qui a changé et où.

Quand l'auteur avance une idée qui contredit le livre, la discuter honnêtement avant de l'intégrer : dire ce qu'elle a de juste, l'objection la plus forte qu'elle appelle, et la formulation qui la rend défendable.
