# Sprint 05 — Gestion des sites web

**Statut :** À réaliser

---

# Objectif

Mettre en place le premier module métier de l'application permettant de gérer les sites web du Groupe A.P&Partner.

Ce module constitue la base de l'ensemble de l'application. Tous les autres modules (SEO, GEO, mots-clés, rapports, crawl, IA...) seront rattachés à un site web.

Le Sprint 05 doit uniquement permettre la gestion CRUD des sites web.

---

# Contexte

L'application est désormais capable de gérer :

* l'architecture backend ;
* la base de données ;
* l'authentification ;
* les utilisateurs.

Le premier module métier consiste à administrer les sites web suivis par la plateforme.

---

# Périmètre

Le sprint comprend exclusivement :

* création d'un site web ;
* consultation d'un site web ;
* modification d'un site web ;
* suppression d'un site web ;
* liste paginée des sites.

Aucune autre fonctionnalité ne doit être développée.

---

# Architecture

Toutes les nouvelles fonctionnalités doivent être développées exclusivement dans :

```text
backend/app/
```

Respecter strictement l'architecture :

```text
Routes
    ↓
Services
    ↓
Repositories
    ↓
Models
```

Aucune logique métier dans les Routes.

Aucun accès SQLAlchemy direct hors Repository.

---

# Base de données

Créer une table :

```text
websites
```

## Colonnes

| Nom        | Type        | Contraintes            |
| ---------- | ----------- | ---------------------- |
| id         | Integer     | PK                     |
| name       | String(150) | NOT NULL               |
| url        | String(255) | UNIQUE - NOT NULL      |
| cms        | String(50)  | NULL                   |
| is_active  | Boolean     | NOT NULL - défaut TRUE |
| created_at | DateTime    | NOT NULL               |
| updated_at | DateTime    | NOT NULL               |

---

# Migration Alembic

Créer une migration contenant uniquement :

* création de la table `websites`
* index nécessaires
* contrainte UNIQUE sur `url`

Aucune autre modification de base de données.

---

# SQLAlchemy

Créer le modèle :

```text
Website
```

Utiliser exclusivement SQLAlchemy 2.x :

* Mapped
* mapped_column()
* type hints

---

# Schémas Pydantic

Créer :

* WebsiteCreate
* WebsiteUpdate
* WebsiteRead
* WebsiteList

Utiliser exclusivement Pydantic v2.

---

# Repository

Créer :

```text
WebsiteRepository
```

Responsabilités :

* récupération de la liste ;
* récupération par identifiant ;
* recherche par URL ;
* création ;
* modification ;
* suppression.

Aucune logique métier.

---

# Service

Créer :

```text
WebsiteService
```

Responsabilités :

* validations métier ;
* vérification de l'unicité de l'URL ;
* gestion des erreurs ;
* pagination.

Le Service est l'unique point d'entrée de la logique métier.

---

# API REST

Créer les endpoints suivants.

## Liste

```http
GET /api/v1/websites
```

Paramètres :

* page
* page_size
* search
* is_active

Retour paginé.

---

## Consultation

```http
GET /api/v1/websites/{id}
```

---

## Création

```http
POST /api/v1/websites
```

---

## Modification

```http
PUT /api/v1/websites/{id}
```

---

## Suppression

```http
DELETE /api/v1/websites/{id}
```

---

# Validation

L'URL d'un site doit être unique.

En cas de doublon :

Retour HTTP :

```text
409 Conflict
```

Un identifiant inexistant doit retourner :

```text
404 Not Found
```

---

# Documentation OpenAPI

Tous les endpoints doivent être documentés.

Utiliser :

* response_model
* status_code
* summary
* description

---

# Tests

Créer les tests suivants :

* création ;
* lecture ;
* liste ;
* pagination ;
* recherche ;
* modification ;
* suppression ;
* conflit d'URL ;
* 404.

Tous les tests doivent passer.

---

# Hors périmètre

Ne pas développer :

* crawler ;
* mots-clés ;
* concurrents ;
* dashboard ;
* React ;
* templates HTML ;
* authentification supplémentaire ;
* gestion des rôles ;
* statistiques.

---

# Critères d'acceptation

✓ CRUD complet des sites web.

✓ Architecture respectée.

✓ Repository sans logique métier.

✓ Service contenant la logique métier.

✓ Documentation OpenAPI complète.

✓ Migration Alembic.

✓ Tests Pytest verts.

✓ Ruff sans erreur.

✓ Aucune fonctionnalité hors périmètre.

---

# Definition of Done

Le Sprint est terminé uniquement si :

* le modèle SQLAlchemy est créé ;
* les schémas Pydantic sont créés ;
* le Repository est créé ;
* le Service est créé ;
* les Routes sont créées ;
* la migration Alembic est créée ;
* la documentation OpenAPI est complète ;
* tous les tests passent ;
* Ruff ne retourne aucune erreur ;
* aucune architecture parallèle n'a été créée.

---

# Contraintes Codex

Ne jamais :

* créer une architecture parallèle ;
* déplacer les dossiers principaux ;
* modifier l'organisation existante ;
* développer des fonctionnalités appartenant à un autre sprint ;
* créer de commit ;
* créer de Pull Request.

Le développement doit rester strictement limité au périmètre de ce Sprint.
