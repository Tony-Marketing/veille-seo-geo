# Git Workflow

Ce document décrit le workflow Git officiel du projet.

Toutes les contributions doivent respecter ce processus.

---

# Branche principale

La branche :

main

contient uniquement du code stable.

Aucun développement direct ne doit être réalisé sur cette branche.

---

# Développement

Chaque fonctionnalité est développée dans une branche dédiée.

Exemple :

sprint-05

sprint-06

bugfix-login

feature-dashboard

---

# Workflow

Créer une nouvelle branche

↓

Développer avec Codex

↓

Relire les modifications

↓

Lancer Ruff

↓

Lancer Pytest

↓

Corriger les éventuelles erreurs

↓

Créer le commit

↓

Push GitHub

↓

Créer une Pull Request

↓

Revue de code

↓

Merge dans main

↓

Suppression de la branche

---

# Commits

Les messages de commit suivent la convention :

```
type: description
```

Exemples :

```
feat: ajout du module website

fix: correction du repository keywords

docs: ajout du sprint 06

refactor: simplification du service websites

test: ajout des tests API websites

chore: mise à jour des dépendances
```

---

# Pull Requests

Chaque Pull Request doit :

- concerner un seul sprint ou une seule fonctionnalité ;
- rester de taille raisonnable ;
- contenir une description claire ;
- passer les tests avant le merge.

---

# Revue de code

Avant chaque merge, vérifier :

- architecture respectée ;
- imports cohérents ;
- absence de duplication ;
- séparation Routes / Services / Repositories ;
- typage Python ;
- migrations Alembic ;
- tests.

---

# Architecture

Il est interdit de :

- créer une architecture parallèle ;
- déplacer les dossiers principaux ;
- recréer des modules existants.

Toute évolution doit compléter l'architecture existante.

---

# Dépendances

Les dépendances Python sont installées uniquement via :

```
requirements.txt
```

Ne jamais installer des packages individuellement sans mettre à jour ce fichier.

---

# Tests

Avant chaque commit :

```
ruff check .
```

puis

```
pytest
```

Les tests doivent être verts avant toute Pull Request.

---

# Développement avec Codex

Codex intervient uniquement comme développeur.

Il ne doit jamais :

- créer un commit ;
- créer une Pull Request ;
- pousser sur GitHub.

Le développeur reste responsable de :

- la validation du code ;
- l'exécution des tests ;
- la création des commits ;
- la création des Pull Requests.

---

# Documentation

Chaque sprint doit être documenté dans :

```
docs/sprints/
```

Toute nouvelle fonctionnalité doit respecter le document de sprint correspondant.

Les documents de référence du projet sont :

- README.md
- AGENTS.md
- docs/ARCHITECTURE.md
- docs/GIT_WORKFLOW.md
- docs/CHANGELOG.md