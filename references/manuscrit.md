# Conventions du manuscrit Markdown

Les scripts `build_book.py` et `build_docx.py` lisent un fichier Markdown (syntaxe pandoc) qui suit ces conventions.

## En-tête

```yaml
---
title: "Éthique des situations"
subtitle: "Vers une axiologie des attentes"
author: "Nom de l'auteur"          # facultatif
lang: fr-FR                        # fr-… active la typographie française
running_head: "Éthique des situations"   # titre courant des pages paires (par défaut : title)
epigraph: "« Quand il faut, dans les cas où il faut… »"   # facultatif
epigraph_source: "Aristote, <em>Éthique à Nicomaque</em>, II, 6"
---
```

## Structure

- Une **partie** est un titre de niveau 1, sous la forme `# Première partie — Titre de la partie`. Elle devient une page à part.
- Un **chapitre** est un titre de niveau 2 :
  - `## Chapitre 3 — Chaque domaine a-t-il ses règles ?` (numéro et titre séparés par un tiret cadratin) ;
  - `## Introduction`, `## Glossaire`, `## Bibliographie` (sans numéro) ;
  - `## Conclusion — Titre` ou `## Annexe — Titre`.
- Pas de titres de niveau 3 dans les chapitres.
- Le glossaire : un paragraphe par entrée, `**Terme.** Définition.`
- La bibliographie : un paragraphe par œuvre, `Nom, Prénom, *Titre*, Lieu, Éditeur, année.`

## Notes

Notes pandoc : appel `[^12]` dans le texte, définition `[^12]: Texte de la note.` n'importe où dans le fichier (le plus simple : en fin de chapitre). Les numéros doivent être uniques dans tout le fichier ; l'affichage repart à 1 à chaque chapitre dans le PDF livre.

## Exemple minimal

Voir `assets/exemple.md`.
