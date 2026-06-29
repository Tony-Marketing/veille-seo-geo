# Architecture Technique

## Présentation

Ce document décrit l'architecture technique du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il constitue la référence pour l'organisation du code backend et définit les responsabilités de chaque couche de l'application.

Toutes les nouvelles fonctionnalités doivent respecter cette architecture.

---

# Technologies

Backend

* Python 3.13
* FastAPI
* SQLAlchemy 2.x
* Alembic
* PostgreSQL
* Pydantic v2

Frontend (à terme)

* React

Tests

* Pytest

Qualité

* Ruff

---

# Architecture générale

Le backend est organisé selon une architecture en couches.

Chaque couche possède une responsabilité unique.

```text
Client
    │
    ▼
Routes (FastAPI)
    │
    ▼
Services
    │
    ▼
Repositories
    │
    ▼
Models (SQLAlchemy)
    │
    ▼
PostgreSQL
```

---

# Arborescence officielle

La seule architecture backend autorisée est :

```text
backend/

└── app/
    ├── api/
    ├── core/
    ├── models/
    ├── repositories/
    ├── schemas/
    ├── services/
    ├── main.py
    └── __init__.py
```

Il est strictement interdit de créer une architecture parallèle telle que :

```text
backend/api
backend/core
backend/models
backend/repositories
backend/schemas
backend/services
backend/main.py
```

Toutes les nouvelles fonctionnalités doivent être développées exclusivement dans `backend/app/`.

---

# Responsabilités des couches

## Routes

Les routes FastAPI sont responsables de :

* recevoir les requêtes HTTP ;
* valider les paramètres ;
* appeler les Services ;
* retourner les réponses HTTP.

Les routes ne doivent contenir aucune logique métier.

---

## Services

Les Services contiennent toute la logique métier.

Ils sont responsables notamment de :

* l'orchestration des traitements ;
* les validations métier ;
* les contrôles fonctionnels ;
* les règles de gestion ;
* la levée des exceptions métier.

Les Services utilisent les Repositories.

---

## Repositories

Les Repositories assurent exclusivement les accès aux données.

Ils sont responsables de :

* la lecture ;
* l'écriture ;
* la suppression ;
* les requêtes SQLAlchemy.

Ils ne doivent contenir aucune logique métier.

---

## Models

Les Models représentent les tables de la base de données.

Ils utilisent exclusivement SQLAlchemy 2.x :

* `Mapped`
* `mapped_column()`
* `relationship()`

---

## Schemas

Les Schemas utilisent exclusivement Pydantic v2.

Ils définissent les contrats d'échange entre l'API et les clients.

---

## Core

Le dossier `core` contient :

* la configuration ;
* la connexion à la base de données ;
* la sécurité ;
* les dépendances communes.

---

# Base de données

Le projet utilise PostgreSQL comme base de données principale.

Toutes les modifications du schéma doivent être réalisées via Alembic.

Aucune modification manuelle de la structure de la base de données n'est autorisée.

---

# Dépendances entre couches

Les dépendances autorisées sont :

```text
Routes
    ↓
Services
    ↓
Repositories
    ↓
Models
```

Les dépendances inverses sont interdites.

Par exemple :

* un Repository ne doit jamais appeler un Service ;
* un Model ne doit jamais dépendre d'un Repository ;
* une Route ne doit jamais accéder directement à SQLAlchemy.

---

# Conventions de développement

Toutes les nouvelles fonctionnalités doivent respecter les principes suivants :

* typage Python ;
* séparation stricte des responsabilités ;
* réutilisation des composants existants ;
* absence de duplication de code.

Avant de créer un nouveau module, vérifier qu'un module équivalent n'existe pas déjà.

---

# Tests

Chaque fonctionnalité doit être accompagnée des tests nécessaires.

Selon le périmètre du sprint, les tests peuvent couvrir :

* les Repositories ;
* les Services ;
* les Routes ;
* les APIs.

Le projet doit conserver un ensemble de tests automatisés permettant de vérifier les fonctionnalités existantes.

---

# Documentation

Toute nouvelle fonctionnalité doit être documentée.

Les développements sont guidés par les documents présents dans :

```text
docs/sprints/
```

Chaque document de sprint constitue le cahier des charges contractuel de la fonctionnalité correspondante.

---

# Évolution de l'architecture

Toute évolution de cette architecture doit être documentée dans ce fichier avant son implémentation.

Aucune réorganisation importante du projet ne doit être réalisée sans validation préalable.
