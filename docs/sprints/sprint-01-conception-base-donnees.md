# Sprint 01 — Conception de la base de données

**Statut :** À réaliser

## Objectif

Concevoir et mettre en place l'ensemble de la structure de la base de données PostgreSQL qui servira de fondation à toute l'application.

Ce sprint ne comprend aucun développement d'interface utilisateur ni de logique métier.

---

# Livrables attendus

## Modèles SQLAlchemy

Créer les modèles SQLAlchemy correspondant aux principales entités du projet.

Les modèles doivent être organisés dans :

```
backend/app/models/
```

Les relations entre les tables devront être correctement définies.

---

## Tables principales

Créer les modèles suivants :

- users
- roles
- permissions
- entities
- websites
- competitors
- keywords
- keyword_positions
- urls
- url_audits
- seo_tags
- technical_issues
- geo_prompts
- geo_results
- geo_sources
- content_calendar
- content_items
- project_tasks
- automations
- reports
- software_versions
- audit_logs

---

## Relations

Définir toutes les relations SQLAlchemy :

- One-to-One
- One-to-Many
- Many-to-Many

Utiliser :

- Foreign Keys
- contraintes
- index
- cascades lorsque cela est pertinent

---

## Types de données

Utiliser les types PostgreSQL adaptés :

- UUID
- VARCHAR
- TEXT
- BOOLEAN
- INTEGER
- BIGINT
- TIMESTAMP
- JSONB
- ARRAY lorsque nécessaire

Éviter les champs génériques de type TEXT lorsqu'un type plus adapté existe.

---

## Colonnes communes

Chaque table devra comporter au minimum :

- id
- created_at
- updated_at

Selon les besoins :

- deleted_at
- created_by
- updated_by

Prévoir la possibilité d'un soft delete lorsque cela est pertinent.

---

## Contraintes

Mettre en place :

- NOT NULL
- UNIQUE
- INDEX
- CHECK lorsque nécessaire

Créer des index sur les colonnes fréquemment utilisées.

---

## Alembic

Créer la première migration complète.

La migration doit permettre :

- la création de toutes les tables
- la création des contraintes
- la création des index

La migration doit être reproductible sur une base vide.

---

## Documentation

Documenter :

- les tables
- les relations
- les clés étrangères

Mettre à jour :

- ARCHITECTURE.md
- README.md si nécessaire

---

# Hors périmètre

Ne pas développer :

- endpoints FastAPI
- interface React
- authentification
- logique métier
- appels API
- scraping
- intelligence artificielle

Ce sprint concerne uniquement la couche de persistance.

---

# Critères d'acceptation

Le sprint est considéré terminé si :

✓ Tous les modèles SQLAlchemy sont créés.

✓ Toutes les migrations Alembic fonctionnent.

✓ La base PostgreSQL est créée sans erreur.

✓ Les relations entre les tables sont valides.

✓ Les contraintes sont correctement appliquées.

✓ Les index principaux sont créés.

✓ La documentation de la base est mise à jour.

---

# Résultat attendu

À la fin du Sprint 01, la structure complète de la base de données est opérationnelle.

Aucune fonctionnalité métier n'est encore disponible, mais l'ensemble du modèle de données est prêt à être utilisé par les futurs développements.

---

# Prompt Codex

Respecte les fichiers AGENTS.md, ARCHITECTURE.md et README.md.

Implémente exclusivement la couche de persistance.

Ne crée aucun endpoint FastAPI.

Ne crée aucun composant React.

Ne développe aucune logique métier.

Produis des modèles SQLAlchemy propres, fortement typés et documentés.

Utilise PostgreSQL comme cible principale.

Crée également la migration Alembic correspondante.

À la fin, explique les choix de modélisation effectués.