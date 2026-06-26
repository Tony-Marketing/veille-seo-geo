# AGENTS.md

# Veille SEO-GEO Groupe A.P&Partner

## Objectif

Ce dépôt contient le développement complet de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

L'objectif de l'application est de fournir une plateforme unique permettant de piloter :

- le référencement naturel (SEO)
- la visibilité dans les moteurs d'IA générative (GEO)
- la qualité technique des sites
- les performances des contenus
- la veille concurrentielle
- le suivi des projets marketing
- les automatisations métier

Le projet est développé principalement avec GPT Codex. Toutes les modifications doivent respecter les présentes instructions.

---

# Rôle de Codex

Codex agit comme un développeur logiciel senior.

Avant toute modification, il doit :

- comprendre la fonctionnalité existante ;
- rechercher les composants déjà présents ;
- éviter les duplications de code ;
- préserver la compatibilité avec les modules existants ;
- documenter les changements importants.

Codex ne doit jamais remplacer une fonctionnalité existante lorsqu'elle peut être étendue.

---

# Technologies imposées

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

## Qualité

- Ruff
- Black
- Pytest

---

# Architecture générale

Le projet est composé de plusieurs couches.

Frontend

↓

API FastAPI

↓

Services métier

↓

Repositories

↓

Base PostgreSQL

↓

Connecteurs externes

La logique métier ne doit jamais être écrite directement dans les routes API.

---

# Organisation des dossiers

backend/

API

Services

Repositories

Models

Schemas

Connecteurs

frontend/

Pages

Composants

Hooks

Services

Types

database/

Schéma SQL

Migrations

docs/

Documentation technique

Documentation fonctionnelle

scripts/

Scripts utilitaires

tests/

Tests unitaires

Tests d'intégration

---

# Règles de développement

Toujours privilégier :

- des fonctions courtes ;
- des modules spécialisés ;
- une architecture modulaire ;
- un code facilement testable ;
- un faible couplage entre les composants.

Éviter les fichiers contenant plusieurs milliers de lignes.

Créer un nouveau module lorsqu'une fonctionnalité devient importante.

---

# Conventions Python

Variables :

snake_case

Fonctions :

snake_case

Classes :

PascalCase

Constantes :

MAJUSCULES

Type hints obligatoires.

Exemple :

```python
def create_project(project: ProjectCreate) -> Project:
    ...
```

Les docstrings doivent utiliser le format Google.

---

# Conventions React

Tous les composants utilisent :

PascalCase

Exemples :

Dashboard.tsx

KeywordTable.tsx

ProjectCard.tsx

Les hooks commencent toujours par :

use

Exemple :

useDashboard()

useProjects()

---

# Base de données

Toutes les modifications de structure passent par Alembic.

Aucune requête SQL brute ne doit être utilisée lorsqu'une solution SQLAlchemy existe.

Les modèles doivent rester cohérents avec les schémas Pydantic.

---

# APIs externes

Toutes les intégrations doivent être isolées dans :

backend/connectors/

Exemples :

google_search_console.py

google_analytics.py

openai.py

gemini.py

claude.py

wordpress.py

pagespeed.py

Aucun appel HTTP direct dans les routes API.

---

# Modules prévus

Le projet comprendra notamment :

- Dashboard
- SEO
- GEO
- Audit technique
- Mots-clés
- URLs
- Concurrents
- Marché
- Planning
- Projets
- Rapports
- Administration

Chaque module doit pouvoir évoluer indépendamment.

---

# GEO

Le module GEO est une partie essentielle du projet.

Il doit permettre :

- l'analyse des réponses des IA génératives ;
- le suivi des citations ;
- la mesure de visibilité des marques ;
- la comparaison des modèles IA ;
- l'historisation des résultats.

Les modèles actuellement prévus sont :

- ChatGPT
- Gemini
- Claude
- Perplexity
- Mistral

Le système doit rester extensible.

---

# SEO

Le module SEO doit permettre :

- l'analyse des balises ;
- l'analyse des contenus ;
- l'audit des URLs ;
- le suivi des positions ;
- les Core Web Vitals ;
- la qualité du maillage interne.

---

# Interface utilisateur

Objectifs :

- interface moderne ;
- design inspiré de Windows 11 ;
- responsive ;
- navigation rapide ;
- mode sombre natif.

Toute nouvelle interface doit respecter le design existant.

---

# Documentation

Toute fonctionnalité importante doit être documentée dans :

docs/

Si une nouvelle API est créée, documenter :

- son objectif ;
- ses paramètres ;
- son format de réponse.

---

# Tests

Toute fonctionnalité métier importante doit comporter des tests.

Les tests doivent être placés dans :

tests/

Les nouveaux développements ne doivent pas casser les tests existants.

---

# Performance

Toujours rechercher :

- le minimum de requêtes SQL ;
- les traitements asynchrones lorsque cela est pertinent ;
- la pagination des grandes listes ;
- le cache pour les données peu volatiles.

---

# Sécurité

Ne jamais :

- enregistrer de mot de passe en clair ;
- exposer une clé API dans le code ;
- enregistrer des secrets dans Git.

Les secrets sont exclusivement stockés dans :

.env

---

# Git

Les commits doivent être :

- courts ;
- explicites ;
- en français.

Exemples :

Ajout du module GEO

Correction de l'audit SEO

Ajout de Google Search Console

Refactorisation du Dashboard

---

# Ce que Codex doit toujours faire

Avant toute modification :

1. Comprendre l'architecture existante.
2. Réutiliser le code lorsque cela est possible.
3. Respecter les conventions du projet.
4. Préserver la compatibilité.
5. Documenter les nouvelles fonctionnalités.
6. Ajouter des tests lorsque nécessaire.
7. Produire un code clair, lisible et modulaire.

---

# Ce que Codex ne doit jamais faire

- Supprimer une fonctionnalité sans demande explicite.
- Réécrire entièrement un module lorsqu'une modification locale suffit.
- Introduire une nouvelle dépendance sans justification.
- Coder de la logique métier dans les routes API.
- Dupliquer du code existant.
- Ignorer les conventions définies dans ce document.