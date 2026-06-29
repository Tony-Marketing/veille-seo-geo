# Software Backend Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle du backend  
Version du document : 1.0  
Statut : Référence technique backend  
Périmètre : FastAPI, services, repositories, modèles SQLAlchemy, schémas Pydantic, Alembic, tests, sécurité backend  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes d'architecture backend](#2-principes-darchitecture-backend)
3. [Vue d'ensemble de l'architecture backend](#3-vue-densemble-de-larchitecture-backend)
4. [Arborescence backend officielle](#4-arborescence-backend-officielle)
5. [Cycle de vie d'une requête API](#5-cycle-de-vie-dune-requête-api)
6. [`backend/app/main.py`](#6-backendappmainpy)
7. [Couche Routes](#7-couche-routes)
8. [Couche Services](#8-couche-services)
9. [Couche Repositories](#9-couche-repositories)
10. [Couche Models](#10-couche-models)
11. [Couche Schemas](#11-couche-schemas)
12. [Dépendances FastAPI](#12-dépendances-fastapi)
13. [Gestion de la base de données](#13-gestion-de-la-base-de-données)
14. [Migrations Alembic](#14-migrations-alembic)
15. [Pagination, filtres et tri](#15-pagination-filtres-et-tri)
16. [Gestion des erreurs backend](#16-gestion-des-erreurs-backend)
17. [Sécurité backend](#17-sécurité-backend)
18. [Configuration backend](#18-configuration-backend)
19. [Tests backend](#19-tests-backend)
20. [Qualité de code](#20-qualité-de-code)
21. [Conventions de nommage](#21-conventions-de-nommage)
22. [Pattern officiel pour créer un nouveau module backend](#22-pattern-officiel-pour-créer-un-nouveau-module-backend)
23. [Modules existants](#23-modules-existants)
24. [Modules futurs](#24-modules-futurs)
25. [Intégration Desktop](#25-intégration-desktop)
26. [Performance backend](#26-performance-backend)
27. [Observabilité backend](#27-observabilité-backend)
28. [Anti-patterns interdits](#28-anti-patterns-interdits)
29. [Checklist avant Pull Request backend](#29-checklist-avant-pull-request-backend)
30. [Roadmap backend](#30-roadmap-backend)
31. [Annexes](#31-annexes)

---

## 1. Présentation

### 1.1 Rôle du backend

Le backend de Veille SEO-GEO Groupe A.P&Partner est la source de vérité métier de la plateforme. Il expose une API REST
FastAPI consommée par le client Desktop PySide6, par la documentation interactive Swagger/OpenAPI, et par de futurs
clients HTTP internes ou automatisations contrôlées.

Le backend porte les responsabilités suivantes :

- validation des entrées API ;
- authentification et autorisation futures ;
- orchestration des règles métier ;
- accès contrôlé à PostgreSQL via SQLAlchemy ;
- gestion des transactions ;
- exposition de contrats JSON stables ;
- migrations Alembic explicites ;
- journalisation, audit et observabilité futures ;
- protection des données internes du groupe.

Le Desktop ne doit jamais devenir une source de logique métier. Il affiche les données et appelle l'API. Le backend
décide, valide, persiste et audite.

### 1.2 Place dans l'écosystème global

```text
Utilisateur interne
        |
        v
Desktop PySide6
        |
        | HTTP REST / JSON
        v
FastAPI Backend
        |
        v
Services métier
        |
        v
Repositories SQLAlchemy
        |
        v
PostgreSQL
```

Le backend est le pivot entre les surfaces utilisateur et les données persistantes. Il doit rester indépendant du
Desktop, tout en fournissant des contrats API adaptés aux besoins de l'interface.

### 1.3 Objectifs techniques

| Objectif | Description | Impact attendu |
|---|---|---|
| Architecture stable | Respect strict `Routes -> Services -> Repositories -> Models` | Maintenance durable |
| Contrats API clairs | Schémas Pydantic explicites | Compatibilité Desktop |
| Persistance maîtrisée | SQLAlchemy dans les repositories uniquement | Couplage réduit |
| Migrations explicites | Alembic avec opérations déclarées | Évolution DB contrôlée |
| Tests ciblés | Routes, services et comportements métier | Régressions limitées |
| Sécurité intégrée | Préparation auth/RBAC/audit | Security by Design |
| Observabilité future | Logs, audit, métriques | Diagnostic rapide |

### 1.4 Objectifs de maintenabilité

Le backend doit pouvoir évoluer pendant plusieurs années sans dette structurelle. Cela implique :

- des modules cohérents et spécialisés ;
- des services courts et testables ;
- des repositories sans logique métier ;
- des modèles SQLAlchemy lisibles ;
- des schémas Pydantic séparés par intention ;
- des migrations traçables ;
- des tests compréhensibles ;
- une documentation mise à jour lors des changements de contrat.

### 1.5 Objectifs de sécurité

Le backend doit appliquer les principes définis dans `docs/architecture/AUTHENTICATION.md` :

- routes privées protégées ;
- RBAC centralisé ;
- validation systématique des entrées ;
- secrets hors code ;
- logs sans secrets ;
- erreurs non divulgatrices ;
- audit des actions sensibles ;
- refus par défaut en cas d'incertitude.

### 1.6 Objectifs de testabilité

Le backend doit être testable à trois niveaux :

| Niveau | Objectif | Exemple |
|---|---|---|
| API | Vérifier les contrats HTTP | `GET /api/v1/websites` paginé |
| Service | Vérifier les règles métier | rejet doublon URL |
| Repository futur | Vérifier requêtes complexes | filtres SEO, tri, pagination |

### 1.7 Contraintes

| Contrainte | Règle |
|---|---|
| Architecture | Routes -> Services -> Repositories -> Models |
| Routes | Pas de logique métier |
| Repositories | Pas de logique HTTP ni Pydantic |
| Models | Pas de logique métier complexe |
| Desktop | Aucune dépendance backend -> Desktop |
| PostgreSQL | Accès via SQLAlchemy, pas depuis Desktop |
| Migrations | Alembic explicite, pas `create_all` |
| Tests | Pytest et Ruff doivent passer avant PR |

### 1.8 Principes directeurs

1. Le backend est l'autorité métier.
2. Une route expose un cas d'usage, elle ne l'implémente pas.
3. Un service orchestre les règles métier.
4. Un repository encapsule l'accès aux données.
5. Un modèle représente la structure persistante.
6. Un schéma Pydantic représente un contrat API.
7. Une migration décrit explicitement une évolution de structure.
8. Tout comportement important doit être testable.

---

## 2. Principes d'architecture backend

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| Séparation stricte des responsabilités | Réduire couplage et dette | Routes, services, repositories, models séparés | Route qui écrit directement en base |
| Architecture en couches | Clarifier le flux de données | `Routes -> Services -> Repositories -> Models` | Service qui dépend d'une route |
| Indépendance des routes | Routes fines et lisibles | Route appelle un service | Logique métier dans endpoint |
| Services métier | Centraliser règles et orchestration | `WebsiteService`, `AdminService` | Règles dispersées dans routes |
| Repositories données | Isoler SQLAlchemy | `WebsiteRepository` | SQLAlchemy dans route |
| Models persistants | Représenter les tables | Classes SQLAlchemy | Validation API dans model |
| Schemas Pydantic | Contrat entrée/sortie | `WebsiteCreate`, `WebsiteRead` | Retourner model brut non contrôlé |
| Migrations explicites | Contrôler évolution DB | `op.create_table` | `Base.metadata.create_all()` dans migration |
| Tests systématiques | Prévenir régressions | `tests/api`, `tests/services` | Tester seulement manuellement |
| Sécurité centralisée | Éviter contournements | dépendances auth futures | Vérification rôle copiée partout |
| Pas de dépendance Desktop | Backend indépendant | Aucun import `desktop` | Backend qui connaît PySide6 |

### 2.2 Architecture en couches

```text
Route
  |
  | reçoit HTTP, valide payload, choisit code HTTP
  v
Service
  |
  | applique règles métier, orchestre repositories
  v
Repository
  |
  | construit requêtes SQLAlchemy
  v
Model
  |
  | représente table et relations
  v
PostgreSQL
```

### 2.3 Conséquence pratique

Si une modification métier est demandée, la première question doit être :

```text
Cette règle appartient-elle au service ?
Cette requête appartient-elle au repository ?
Ce contrat appartient-il au schema ?
Cette contrainte appartient-elle au model et à la migration ?
```

### 2.4 Matrice des responsabilités

| Responsabilité | Route | Service | Repository | Model | Schema |
|---|---:|---:|---:|---:|---:|
| Code HTTP | Oui | Non | Non | Non | Non |
| Validation structure payload | Oui via Pydantic | Non | Non | Non | Oui |
| Validation métier | Non | Oui | Non | Limité | Non |
| Transaction métier | Non | Oui | Support | Non | Non |
| Requête SQLAlchemy | Non | Non | Oui | Non | Non |
| Définition table | Non | Non | Non | Oui | Non |
| Sérialisation API | Non | Non | Non | Non | Oui |
| Pagination réponse | Déclare | Orchestre | Calcule requête | Non | Définit contrat |
| Autorisation future | Dépendance | Politique métier | Non | Non | Non |

---

## 3. Vue d'ensemble de l'architecture backend

### 3.1 Diagramme principal

```text
Client Desktop / Swagger / Client HTTP
        |
        v
FastAPI Routes
        |
        v
Services
        |
        v
Repositories
        |
        v
SQLAlchemy Models
        |
        v
PostgreSQL
```

### 3.2 Vue logique

```text
API Layer
  |
  +-- Routers
  +-- Dependencies
  +-- Request validation
  +-- Response schemas

Business Layer
  |
  +-- Services
  +-- Business rules
  +-- Domain errors
  +-- Use cases

Data Access Layer
  |
  +-- Repositories
  +-- Query construction
  +-- Persistence operations

Persistence Layer
  |
  +-- SQLAlchemy Models
  +-- Alembic migrations
  +-- PostgreSQL constraints
```

### 3.3 Vue physique

```text
Process backend Python 3.13
  |
  v
FastAPI application
  |
  v
Uvicorn / ASGI runtime
  |
  v
SQLAlchemy Engine + Sessions
  |
  v
PostgreSQL database
```

### 3.4 Vue par responsabilités

| Couche | Responsabilité | Exemple projet |
|---|---|---|
| `main.py` | Créer app et inclure router | `app.include_router(api_router)` |
| `api/v1/routes` | Endpoints REST | `websites.py`, `admin.py` |
| `services` | Règles métier | `WebsiteService` |
| `repositories` | Accès DB | `WebsiteRepository` |
| `models` | Tables | `Website`, `User`, `Role` |
| `schemas` | Contrats API | `WebsiteCreate`, `WebsiteRead` |
| `core` | Config, DB, sécurité | `database.py`, `config.py` |
| `alembic` | Évolution DB | `versions/*.py` |
| `tests` | Validation | `tests/api`, `tests/services` |

### 3.5 Cycle requête/réponse

```text
HTTP Request
    |
    v
FastAPI routing
    |
    v
Pydantic request parsing
    |
    v
Dependency injection
    |
    v
Service method
    |
    v
Repository query
    |
    v
SQLAlchemy session
    |
    v
PostgreSQL
    |
    v
SQLAlchemy model instances
    |
    v
Service result
    |
    v
Pydantic response model
    |
    v
HTTP Response
```

---

## 4. Arborescence backend officielle

### 4.1 Arborescence cible

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── alembic/
│   ├── env.py
│   └── versions/
└── ...
tests/
├── api/
└── services/
```

### 4.2 Dossiers backend

| Dossier | Rôle | Peut contenir | Ne doit jamais contenir |
|---|---|---|---|
| `backend/app/api/` | Définition API | routers, dependencies | logique métier lourde |
| `backend/app/api/v1/routes/` | Routes versionnées | endpoints REST | SQLAlchemy direct |
| `backend/app/core/` | Infrastructure | config, DB, sécurité | modules métier |
| `backend/app/models/` | Modèles SQLAlchemy | tables, relations | schémas Pydantic |
| `backend/app/repositories/` | Accès aux données | requêtes SQLAlchemy | codes HTTP |
| `backend/app/schemas/` | Contrats Pydantic | create/update/read/list | session DB |
| `backend/app/services/` | Logique métier | règles, orchestration | FastAPI Response |
| `backend/alembic/` | Migrations | env, versions | `create_all` |
| `tests/api/` | Tests endpoints | TestClient | dépendance Desktop |
| `tests/services/` | Tests métier | services, repositories mockés ou DB test | tests UI |

### 4.3 Conventions d'organisation

- Un module fonctionnel important possède idéalement un fichier dans `routes`, `schemas`, `services`, `repositories` et `models`.
- Les routes sont versionnées sous `/api/v1`.
- Les migrations sont dans `backend/alembic/versions`.
- Les tests suivent la même granularité que les couches.
- Les noms de fichiers restent en snake_case.

### 4.4 Exemple module Websites

```text
backend/app/api/v1/routes/websites.py
backend/app/schemas/websites.py
backend/app/services/websites.py
backend/app/repositories/websites.py
backend/app/models/...
tests/api/test_websites_routes.py
tests/services/test_websites_services.py
```

---

## 5. Cycle de vie d'une requête API

### 5.1 Flux complet

```text
HTTP Request
    |
    v
FastAPI Router
    |
    v
Dependency Injection
    |
    v
Service
    |
    v
Repository
    |
    v
SQLAlchemy Session
    |
    v
PostgreSQL
    |
    v
Response Schema
    |
    v
HTTP Response
```

### 5.2 Diagramme de séquence

```text
Client          Route          Dependency          Service          Repository          DB
  |               |                |                  |                  |              |
  | HTTP request  |                |                  |                  |              |
  |-------------->|                |                  |                  |              |
  |               | parse payload  |                  |                  |              |
  |               |--------------->| get_db/session   |                  |              |
  |               |<---------------| db session       |                  |              |
  |               | call service   |                  |                  |              |
  |               |---------------------------------->|                  |              |
  |               |                |                  | validate rules   |              |
  |               |                |                  | query repository |              |
  |               |                |                  |----------------->|              |
  |               |                |                  |                  | SQLAlchemy   |
  |               |                |                  |                  |------------->|
  |               |                |                  |                  | result       |
  |               |                |                  |                  |<-------------|
  |               |                |                  | domain result    |              |
  |               |<----------------------------------|                  |              |
  | serialize     |                |                  |                  |              |
  |<--------------|                |                  |                  |              |
```

### 5.3 Validation d'entrée

La validation d'entrée est assurée par :

- types Python ;
- schémas Pydantic ;
- paramètres `Query`, `Path`, `Body` ;
- contraintes Pydantic ;
- dépendances communes comme la pagination.

### 5.4 Injection des dépendances

Les dépendances typiques sont :

- session DB ;
- utilisateur courant futur ;
- admin requis futur ;
- pagination ;
- filtres communs ;
- services construits depuis repositories.

### 5.5 Transaction

Le modèle transactionnel doit être explicite :

```text
Route
  |
  v
Service
  |
  +-- repository.create(...)
  +-- repository.update(...)
  +-- commit/rollback selon convention du projet
```

Les opérations métier multi-étapes doivent être traitées comme une unité cohérente.

### 5.6 Sérialisation de sortie

La sortie est contrôlée par les schémas Pydantic. Une route ne doit pas exposer accidentellement des champs internes
comme un hash de mot de passe, une clé API brute ou un champ technique non destiné au client.

---

## 6. `backend/app/main.py`

### 6.1 Rôle

`backend/app/main.py` crée l'application FastAPI et inclut le routeur principal. Il définit les métadonnées OpenAPI
et les endpoints globaux comme la santé de l'application.

### 6.2 Responsabilités

| Responsabilité | Description |
|---|---|
| Créer l'app FastAPI | Titre, version, description |
| Inclure les routers | `api_router` versionné |
| Définir health simple | Endpoint de disponibilité |
| Préparer middleware futur | CORS, correlation ID, sécurité |
| Exposer OpenAPI | Documentation développeur |

### 6.3 À ne pas contenir

`main.py` ne doit pas contenir :

- logique métier ;
- requêtes SQLAlchemy ;
- création de tables ;
- routes métier longues ;
- règles de sécurité copiées ;
- configuration secrète en dur ;
- code Desktop.

### 6.4 Middlewares futurs

| Middleware | Usage |
|---|---|
| CORS | Clients web futurs |
| Correlation ID | Traçabilité requêtes |
| Request logging | Observabilité |
| Security headers | Durcissement HTTP |
| Rate limiting | Protection brute force |

### 6.5 Santé de l'application

Le health endpoint doit rester rapide, stable et non sensible. Les diagnostics détaillés doivent être placés dans des
endpoints admin protégés.

---

## 7. Couche Routes

### 7.1 Rôle

Les routes FastAPI exposent les cas d'usage au format HTTP. Elles convertissent une requête en appel de service, puis
convertissent le résultat en réponse API.

### 7.2 Responsabilités autorisées

- définir `APIRouter` ;
- déclarer path, method, status code ;
- déclarer `response_model` ;
- recevoir payload Pydantic ;
- recevoir paramètres `Query` ou `Path` ;
- injecter DB, user futur, service ;
- appeler une méthode de service ;
- retourner le résultat ;
- définir un `Response` vide pour 204.

### 7.3 Interdictions

Une route ne doit jamais :

- contenir de logique métier ;
- construire une requête SQLAlchemy ;
- modifier directement un modèle ;
- appeler PostgreSQL ;
- appeler une autre route ;
- gérer un algorithme métier complexe ;
- vérifier les rôles avec du code copié ;
- exposer des champs non contrôlés.

### 7.4 Tableau route

| Autorisé dans une route | Interdit dans une route | Alternative correcte |
|---|---|---|
| Déclarer `response_model` | Calculer un score SEO | Service SEO |
| Appeler `service.create(payload)` | `db.query(Model)` | Repository |
| Dépendance `get_db` | `model.password_hash = ...` | Service + repository |
| Paramètres pagination | Boucles métier complexes | Service |
| Lever/laisser exception HTTP normalisée | Capturer toutes erreurs sans stratégie | Exception handler/service |
| Retourner `Response(204)` | Sérialiser manuellement gros objets | Schema Pydantic |

### 7.5 Exemple conceptuel de route propre

```python
@router.get("", response_model=WebsiteList)
def list_websites(
    params: PaginationParams = Depends(pagination_params),
    service: WebsiteService = Depends(get_service),
) -> WebsiteList:
    """Retourne les sites paginés."""

    return service.list(params)
```

Cette route :

- ne connaît pas SQLAlchemy ;
- ne sait pas comment la pagination est requêtée ;
- délègue la règle au service ;
- expose un contrat Pydantic.

### 7.6 Codes HTTP

| Action | Code succès |
|---|---:|
| Liste | 200 |
| Lecture détail | 200 |
| Création | 201 |
| Mise à jour | 200 |
| Suppression | 204 |
| Action asynchrone future | 202 |

---

## 8. Couche Services

### 8.1 Rôle

Les services forment la couche métier. Ils orchestrent les repositories, appliquent les règles fonctionnelles, gèrent
les erreurs métier et garantissent la cohérence des cas d'usage.

### 8.2 Responsabilités

| Responsabilité | Exemple |
|---|---|
| Validation métier | Refuser URL website dupliquée |
| Orchestration | Créer rapport + audit futur |
| Cohérence | Empêcher suppression d'un rôle système |
| Transactions | Grouper plusieurs écritures |
| Erreurs métier | Lever conflit, not found |
| Idempotence | Éviter double import futur |
| Appels repositories | Lire, créer, modifier |

### 8.3 Ce qu'un service ne doit pas faire

- manipuler les objets `Request` ou `Response` FastAPI ;
- contenir des décorateurs de route ;
- écrire du SQL brut si SQLAlchemy couvre le besoin ;
- exposer des modèles non contrôlés à des clients ;
- importer le Desktop ;
- décider de détails d'affichage UI.

### 8.4 Services existants et futurs

| Service | Responsabilité | Repositories utilisés | Tests attendus |
|---|---|---|---|
| Administration | Dashboard admin, paramètres, logs, providers IA | Admin, settings, logs, API keys | Routes + services |
| Websites | Gestion des sites | WebsiteRepository | CRUD, pagination, doublons |
| Entities | Gestion entités | EntityRepository | CRUD, contraintes |
| Keywords | Mots-clés | KeywordRepository | import, filtres, doublons |
| Competitors | Concurrents | CompetitorRepository | comparaison, CRUD |
| Reports | Rapports | ReportRepository | génération, statuts |
| SEO | Audits SEO | SEO repositories futurs | règles score, recommandations |
| GEO | Visibilité IA | GEO repositories futurs | citations, modèles |
| Crawler | Crawls | Crawl repositories futurs | jobs, statuts |
| Prompts | Prompts IA | PromptRepository futur | versions, validation |
| IA | Fournisseurs et modèles | AI repositories | exécution, coûts, erreurs |
| Configuration | Import/export config | multiples repositories | intégrité import |

### 8.5 Idempotence

Les services qui déclenchent des jobs, imports ou exports doivent prévoir l'idempotence. Exemple :

```text
Demande import keywords
        |
        v
Vérifier fichier/import déjà traité
        |
        v
Créer job unique ou retourner job existant
```

### 8.6 Gestion des erreurs métier

Les services doivent produire des erreurs explicites :

- ressource introuvable ;
- conflit d'unicité ;
- état incompatible ;
- permission métier future ;
- validation fonctionnelle.

---

## 9. Couche Repositories

### 9.1 Rôle

Les repositories encapsulent l'accès aux données via SQLAlchemy. Ils construisent les requêtes, appliquent filtres,
tri et pagination au niveau persistence, puis retournent des modèles ou résultats simples à la couche service.

### 9.2 Responsabilités autorisées

- `select`, `where`, `order_by`, `join` ;
- création d'entité SQLAlchemy ;
- mise à jour d'attributs persistants ;
- suppression contrôlée ;
- pagination ;
- tri ;
- filtres ;
- comptage ;
- chargements relationnels.

### 9.3 Interdictions

Un repository ne doit pas :

- contenir de logique métier ;
- lever des erreurs HTTP FastAPI ;
- importer des schémas Pydantic ;
- importer le Desktop ;
- décider qu'un utilisateur a le droit d'agir ;
- sérialiser une réponse API ;
- envoyer des emails ou appeler des connecteurs externes.

### 9.4 Tableau repository

| Autorisé dans un repository | Interdit dans un repository | Alternative correcte |
|---|---|---|
| `session.add(model)` | `raise HTTPException` | Service ou exception métier mappée |
| `select(Model)` | Vérifier rôle utilisateur | Authorization service futur |
| `count()` | Construire JSON API | Schema Pydantic |
| `where(Model.name.ilike(...))` | Calculer score GEO | Service GEO |
| `delete(model)` | Envoyer notification | Service |
| `joinedload` | Lire variables UI | Page Desktop |

### 9.5 Pagination repository

Le repository peut calculer :

- `items` ;
- `total` ;
- offset ;
- limit ;
- order.

Le service assemble ensuite le contrat paginé attendu.

---

## 10. Couche Models

### 10.1 Rôle

Les modèles SQLAlchemy représentent les tables PostgreSQL, les colonnes, les relations et les contraintes côté ORM.

### 10.2 Responsabilités

| Élément | Description |
|---|---|
| Table | Nom de table |
| Colonnes | Types, nullabilité, défauts |
| Relations | Foreign keys, relationships |
| Contraintes | Unique, check, foreign keys |
| Index | Performance requêtes |
| Timestamps | `created_at`, `updated_at` |

### 10.3 Conventions modèles

| Sujet | Convention |
|---|---|
| Classe | PascalCase, singulier |
| Table | snake_case, pluriel si cohérent existant |
| Colonne | snake_case |
| PK | `id` |
| FK | `<resource>_id` |
| Booléen | `is_active`, `is_deleted` |
| Timestamps | `created_at`, `updated_at`, `deleted_at` si soft delete |
| Relation | nom explicite |

### 10.4 Logique dans models

Les modèles peuvent contenir de petites propriétés techniques simples si nécessaire, mais ne doivent pas contenir de
logique métier complexe. Exemple autorisé : propriété calculée locale sans accès DB. Exemple interdit : méthode qui
déclenche un crawl ou vérifie une permission.

### 10.5 Contraintes et migrations

Toute contrainte ajoutée au modèle doit être reflétée dans une migration Alembic explicite.

---

## 11. Couche Schemas

### 11.1 Rôle

Les schémas Pydantic v2 définissent les contrats d'entrée et de sortie de l'API. Ils protègent l'API contre les
payloads invalides et contrôlent les champs exposés aux clients.

### 11.2 Types de schémas

| Type | Usage | Exemple |
|---|---|---|
| Create | Création | `WebsiteCreate` |
| Update | Mise à jour partielle ou complète | `WebsiteUpdate` |
| Read | Sortie détail | `WebsiteRead` |
| List | Sortie paginée | `WebsiteList` |
| Filter futur | Filtres complexes | `KeywordFilters` |
| Action futur | Payload action | `ReportGenerateRequest` |

### 11.3 Convention de nommage

```text
WebsiteCreate
WebsiteUpdate
WebsiteRead
WebsiteListResponse
```

Le projet peut utiliser un alias comme `WebsiteList = PaginatedResponse[WebsiteRead]` si cette convention est déjà en
place. L'important est que le contrat reste clair.

### 11.4 Schémas paginés

Structure standard :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 11.5 Erreurs à éviter

| Erreur | Risque | Alternative |
|---|---|---|
| Réutiliser Create pour Update | Champs obligatoires incorrects | Schema Update dédié |
| Exposer hash ou secret | Fuite de données | Schema Read contrôlé |
| Mettre accès DB dans schema | Couplage | Service/repository |
| Mélanger entrée et sortie | Contrat instable | Schemas séparés |
| Validation métier lourde | Difficile à tester | Service |

---

## 12. Dépendances FastAPI

### 12.1 Rôle

Les dépendances FastAPI factorisent les éléments transverses :

- session DB ;
- pagination ;
- utilisateur courant futur ;
- rôle admin futur ;
- permissions futures ;
- filtres communs ;
- construction de services.

### 12.2 Session DB

La dépendance `get_db` fournit une session SQLAlchemy par requête. Elle doit garantir fermeture propre et rollback en
cas d'erreur selon la convention du projet.

### 12.3 Pagination

La dépendance pagination doit standardiser :

- `page` ;
- `page_size` ;
- `search` ;
- `sort` ;
- `order`.

### 12.4 Authentification future

Voir `docs/architecture/AUTHENTICATION.md`. Côté backend, les dépendances futures doivent fournir :

- `get_current_user` ;
- `require_admin` ;
- `require_permission("module:action")`.

### 12.5 Interdits

- Copier la même logique de pagination dans chaque route.
- Copier la même logique de sécurité dans chaque endpoint.
- Construire des dépendances qui importent le Desktop.
- Masquer des erreurs critiques sans audit.

---

## 13. Gestion de la base de données

### 13.1 SQLAlchemy Session

La session SQLAlchemy représente l'unité de travail avec PostgreSQL. Elle doit rester dans la couche backend.

### 13.2 Cycle de vie

```text
HTTP request
    |
    v
Create DB session
    |
    v
Use repositories
    |
    v
Commit or rollback
    |
    v
Close session
```

### 13.3 Diagramme de transaction

```text
Service method
    |
    v
repository.get(...)
    |
    v
repository.update(...)
    |
    v
flush if id/defaults needed
    |
    v
commit
    |
    +-- success -> refresh/return
    |
    +-- error -> rollback -> raise domain error
```

### 13.4 Commit, flush, refresh

| Opération | Usage |
|---|---|
| `flush` | Envoyer changements sans terminer transaction |
| `commit` | Valider transaction |
| `rollback` | Annuler transaction |
| `refresh` | Recharger valeurs générées |

### 13.5 Erreurs SQLAlchemy

Les erreurs SQLAlchemy doivent être capturées au niveau approprié et transformées en erreurs métier ou API lisibles.
Exemple : une violation d'unicité peut devenir une erreur de conflit `409`.

### 13.6 Contraintes PostgreSQL

Les contraintes DB sont une protection finale, mais ne remplacent pas la validation métier dans les services.

---

## 14. Migrations Alembic

### 14.1 Principe absolu

Les migrations Alembic ne doivent jamais utiliser :

```python
Base.metadata.create_all()
Base.metadata.drop_all()
```

Elles doivent utiliser des instructions explicites :

```python
op.create_table(...)
op.drop_table(...)
op.create_index(...)
op.drop_index(...)
```

### 14.2 Structure d'une migration

```text
revision identifiers
    |
    v
upgrade()
    |
    +-- op.create_table
    +-- op.create_index
    +-- op.add_column
    +-- op.create_foreign_key
    |
    v
downgrade()
    |
    +-- opérations inverses explicites
```

### 14.3 Naming

| Élément | Convention |
|---|---|
| Fichier | timestamp ou revision + description |
| Table | snake_case |
| Index | `ix_<table>_<column>` |
| Unique | `uq_<table>_<column>` |
| FK | `fk_<table>_<column>_<target>` |
| Check | `ck_<table>_<rule>` |

### 14.4 Contraintes

Toute migration doit déclarer explicitement :

- colonnes ;
- nullabilité ;
- valeurs par défaut ;
- clés primaires ;
- clés étrangères ;
- index ;
- contraintes uniques ;
- contraintes check si nécessaire.

### 14.5 Données initiales

Les données initiales doivent être limitées aux valeurs système nécessaires :

- rôles système ;
- permissions système ;
- paramètres de base.

Elles doivent être idempotentes ou clairement contrôlées.

### 14.6 Checklist migration

| Contrôle | OK |
|---|---|
| `upgrade()` explicite | |
| `downgrade()` explicite | |
| Pas de `Base.metadata.create_all()` | |
| Pas de `Base.metadata.drop_all()` | |
| Contraintes nommées | |
| Index utiles ajoutés | |
| Nullabilité réfléchie | |
| FK cohérentes | |
| Données initiales justifiées | |
| Test de migration futur prévu | |

---

## 15. Pagination, filtres et tri

### 15.1 Standard API

Les endpoints de liste doivent utiliser une réponse paginée stable.

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 15.2 Paramètres

| Paramètre | Type | Défaut | Limite |
|---|---|---:|---:|
| `page` | int | 1 | >= 1 |
| `page_size` | int | 20 | 100 max par défaut |
| `search` | str/null | null | longueur limitée future |
| `sort` | str/null | null | whitelist |
| `order` | `asc/desc` | `asc` | valeurs fixes |

### 15.3 Règles

- Le repository applique `offset` et `limit`.
- Le service retourne `items`, `total`, `page`, `page_size`, `pages`.
- Le tri doit être limité à des colonnes autorisées.
- La recherche doit être maîtrisée pour éviter requêtes trop coûteuses.
- Les filtres doivent être explicites.

### 15.4 Exemple Websites

```text
GET /api/v1/websites?page=1&page_size=20&search=Europ&sort=name&order=asc
```

### 15.5 Matrice pagination par module

| Module | Pagination | Search | Sort | Filtres |
|---|---:|---:|---:|---:|
| Websites | Oui | Oui | Oui | actif, entité |
| Entities | Oui | Oui | Oui | statut |
| Keywords | Oui | Oui | Oui | entité, priorité, position |
| Competitors | Oui | Oui | Oui | marché, entité |
| Reports | Oui | Oui | Oui | type, statut, période |
| Logs | Oui | Oui | Oui | niveau, module, date |

---

## 16. Gestion des erreurs backend

### 16.1 Principes

Les erreurs doivent être :

- prévisibles ;
- documentées ;
- testées ;
- non divulgatrices ;
- mappées vers un code HTTP adapté ;
- utiles pour le Desktop.

### 16.2 Tableau des erreurs

| Erreur | Code HTTP | Couche qui la produit | Format attendu | Exemple |
|---|---:|---|---|---|
| Validation payload | 422 | FastAPI/Pydantic | détail validation | URL trop courte |
| Ressource introuvable | 404 | Service | erreur structurée | website absent |
| Conflit | 409 | Service/DB mappée | erreur structurée | URL déjà utilisée |
| Permission future | 403 | Auth dependency | erreur auth | permission manquante |
| Non authentifié futur | 401 | Auth dependency | erreur auth | token expiré |
| Erreur DB | 500 ou 409 | Repository/Service | message générique | contrainte |
| Erreur inattendue | 500 | Handler global | correlation id | exception non prévue |

### 16.3 Format cible

```json
{
  "error": {
    "code": "website_url_already_exists",
    "message": "Un site utilise déjà cette URL.",
    "correlation_id": "req_123"
  }
}
```

### 16.4 Messages internes vs utilisateur

| Type | Exemple | Exposition |
|---|---|---|
| Message utilisateur | `Un site utilise déjà cette URL.` | Oui |
| Détail technique | nom contrainte SQL | Logs seulement |
| Stack trace | traceback Python | Jamais en production |
| Correlation ID | `req_123` | Oui |

---

## 17. Sécurité backend

### 17.1 Référence

La référence complète est `docs/architecture/AUTHENTICATION.md`. Cette section décrit l'intégration backend.

### 17.2 Protection des routes

| Type route | Protection |
|---|---|
| Health public | Public minimal |
| Auth login futur | Public avec rate limit |
| Modules métier | Authentification requise |
| Administration | Admin ou permission spécifique |
| Logs | Permission élevée |
| API keys | Permission critique |

### 17.3 Validation des entrées

Toute entrée externe doit être validée par :

- Pydantic ;
- contraintes service ;
- contraintes DB ;
- whitelists pour tri/filtres ;
- limites de taille.

### 17.4 Secrets

Les secrets doivent être stockés hors code :

- `.env` local non versionné ;
- variables d'environnement ;
- coffre futur ;
- hash ou chiffrement pour secrets persistés.

### 17.5 Logs sans secrets

Ne jamais logger :

- mot de passe ;
- token ;
- clé API brute ;
- secret OAuth ;
- payload sensible complet.

### 17.6 Sécurité future

| Sujet | Intégration |
|---|---|
| RBAC | Dépendance `require_permission` |
| Rate limiting | Middleware ou dépendance |
| CORS | Configuration stricte |
| Headers sécurité | Middleware |
| Audit | Service dédié |
| Session | Tables refresh tokens |

---

## 18. Configuration backend

### 18.1 Rôle

La configuration backend centralise les paramètres applicatifs, secrets et environnements.

### 18.2 Paramètres typiques

| Paramètre | Usage | Sensible |
|---|---|---:|
| `APP_NAME` | Nom API | Non |
| `APP_VERSION` | Version API | Non |
| `DATABASE_URL` | Connexion PostgreSQL | Oui |
| `JWT_SECRET_KEY` futur | Signature token HS256 | Oui |
| `JWT_PRIVATE_KEY` futur | Signature RS256 | Oui |
| `LOG_LEVEL` | Niveau logs | Non |
| `CORS_ORIGINS` futur | Origines autorisées | Non |
| `ENVIRONMENT` | dev/test/prod | Non |

### 18.3 Environnements

| Environnement | Usage | Base |
|---|---|---|
| Dev | Développement local | PostgreSQL local ou conteneur |
| Test | Pytest | Base isolée ou SQLite selon stratégie actuelle |
| Staging | Recette | PostgreSQL staging |
| Production | Usage interne stable | PostgreSQL production |

### 18.4 Lien futur

Un document `CONFIGURATION.md` pourra détailler :

- variables obligatoires ;
- rotation secrets ;
- gestion environnements ;
- configuration Alembic ;
- configuration déploiement.

---

## 19. Tests backend

### 19.1 Stratégie

Les tests backend doivent vérifier les contrats API et les règles métier. Les tests doivent rester rapides, déterministes
et isolés.

### 19.2 Types de tests

| Type | Dossier | Objectif |
|---|---|---|
| API | `tests/api/` | Statuts HTTP, payloads, routes |
| Services | `tests/services/` | Règles métier |
| Repositories futurs | `tests/repositories/` | Requêtes complexes |
| Auth futurs | `tests/auth/` | Login, permissions, tokens |
| Migrations futurs | `tests/migrations/` | Upgrade/downgrade |

### 19.3 Fixtures

`tests/conftest.py` doit fournir :

- application test ;
- client test ;
- session DB test ;
- nettoyage entre tests ;
- overrides FastAPI ;
- fixtures utilisateurs futures.

### 19.4 Usage de `Base.metadata.create_all()`

`Base.metadata.create_all()` est interdit dans les migrations Alembic. Il peut être acceptable dans les tests si la
stratégie de test l'utilise pour créer rapidement un schéma isolé. Cette exception ne doit jamais être copiée dans
`backend/alembic/versions`.

### 19.5 Tests pagination

Chaque module listé doit tester :

- `total` ;
- `page` ;
- `page_size` ;
- `pages` ;
- longueur `items` ;
- filtres ;
- recherche ;
- tri si implémenté.

### 19.6 Commandes

```powershell
py -m pytest
py -m ruff check .
```

### 19.7 Checklist tests avant PR

| Contrôle | OK |
|---|---|
| Tests API ajoutés ou mis à jour | |
| Tests service ajoutés ou mis à jour | |
| Cas erreur couverts | |
| Pagination couverte | |
| Doublons/conflits couverts | |
| Auth future couverte si impactée | |
| Fixtures isolées | |
| `py -m pytest` passe | |
| `py -m ruff check .` passe | |

---

## 20. Qualité de code

### 20.1 Règles

| Sujet | Règle |
|---|---|
| Ruff | Obligatoire |
| Typage | Type hints pertinents |
| Imports | Triés |
| Docstrings | Fonctions publiques importantes |
| Fonctions | Courtes et spécialisées |
| Exceptions | Explicites |
| Duplication | Évitée |
| Couplage | Limité par couches |

### 20.2 Checklist qualité

| Contrôle | OK |
|---|---|
| Route fine | |
| Service testable | |
| Repository sans HTTP | |
| Model cohérent migration | |
| Schema sans secret exposé | |
| Erreurs explicites | |
| Pas de duplication évidente | |
| Imports propres | |
| Types lisibles | |

---

## 21. Conventions de nommage

### 21.1 Fichiers

| Type | Convention | Exemple |
|---|---|---|
| Route | pluriel module | `websites.py` |
| Service | pluriel ou domaine | `websites.py` |
| Repository | pluriel ou domaine | `websites.py` |
| Model | domaine | `entities.py` |
| Schema | pluriel ou domaine | `websites.py` |
| Test API | `test_<module>_routes.py` | `test_websites_routes.py` |
| Test service | `test_<module>_services.py` | `test_websites_services.py` |

### 21.2 Classes

| Type | Convention | Exemple |
|---|---|---|
| Model | PascalCase singulier | `Website` |
| Service | PascalCase + Service | `WebsiteService` |
| Repository | PascalCase + Repository | `WebsiteRepository` |
| Create schema | PascalCase + Create | `WebsiteCreate` |
| Update schema | PascalCase + Update | `WebsiteUpdate` |
| Read schema | PascalCase + Read | `WebsiteRead` |

### 21.3 Fonctions et variables

| Élément | Convention |
|---|---|
| Fonction | snake_case |
| Variable | snake_case |
| Constante | UPPER_SNAKE_CASE |
| Paramètre ID | `item_id`, ou `<resource>_id` |
| Dépendance service | `get_service` ou nom explicite |

### 21.4 Migrations Alembic

| Élément | Convention |
|---|---|
| Revision message | court et descriptif |
| Fichier | date/revision + action |
| Upgrade | opérations dans ordre création |
| Downgrade | ordre inverse |

---

## 22. Pattern officiel pour créer un nouveau module backend

### 22.1 Exemple : module `keywords`

```text
1. Model SQLAlchemy
2. Schemas Pydantic
3. Repository
4. Service
5. Route
6. Migration Alembic explicite
7. Tests service
8. Tests API
9. Documentation
10. Ruff / Pytest
```

### 22.2 Diagramme module

```text
backend/app/models/keywords.py
        |
        v
backend/app/schemas/keywords.py
        |
        v
backend/app/repositories/keywords.py
        |
        v
backend/app/services/keywords.py
        |
        v
backend/app/api/v1/routes/keywords.py
        |
        v
tests/services/test_keywords_services.py
tests/api/test_keywords_routes.py
```

### 22.3 Checklist module

| Étape | Contrôle | OK |
|---|---|---|
| Model | Table, colonnes, contraintes | |
| Migration | `op.create_table` explicite | |
| Schemas | Create, Update, Read, List | |
| Repository | CRUD + pagination | |
| Service | Règles métier | |
| Route | Endpoints REST fins | |
| Router | Inclus dans `api_router` | |
| Tests service | Succès + erreurs | |
| Tests API | Codes HTTP + payloads | |
| Ruff | Passe | |
| Pytest | Passe | |
| Documentation | Mise à jour si contrat public | |

### 22.4 Séquence de création

```text
Développeur
  |
  v
Définit modèle + migration
  |
  v
Définit schemas
  |
  v
Crée repository
  |
  v
Crée service
  |
  v
Expose route
  |
  v
Ajoute tests
  |
  v
Lance qualité
```

---

## 23. Modules existants

### 23.1 Synthèse

| Module | Rôle | Fichiers attendus | Tests existants | Évolutions futures |
|---|---|---|---|---|
| Administration | Paramètres, providers IA, logs, santé | routes/admin, services/admin, schemas/admin | Oui | RBAC complet |
| Users | Gestion comptes | routes/users, models/auth/admin selon existant | Partiel/futur | Auth complète |
| Roles | Rôles | routes/roles, repositories/role | Oui selon état | Matrice permissions |
| Permissions | Permissions | routes/permissions, repositories/permission | Oui selon état | Granularité module |
| Configuration import/export | Export/import paramètres | admin service | Oui selon état | Versioning config |
| Websites | Sites web | websites route/service/repository/schema | Oui | CRUD Desktop complet |
| Entities | Entités groupe | entities modules | Selon état | Relations sites/mots-clés |

### 23.2 Administration

Responsabilité :

- dashboard admin ;
- paramètres ;
- fournisseurs IA ;
- modèles IA ;
- clés API ;
- logs ;
- santé système.

### 23.3 Websites

Responsabilité :

- créer, lire, mettre à jour, supprimer des sites ;
- pagination ;
- recherche ;
- filtre actif ;
- prévention doublons URL.

### 23.4 Entities

Responsabilité :

- représenter les entités/marques du groupe ;
- associer sites, mots-clés, rapports et analyses futures.

---

## 24. Modules futurs

### 24.1 Matrice modules

| Module | Modèle | Schémas | Repository | Service | Route | Tests | Migration |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keywords | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Competitors | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| URLs | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Reports | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| SEO | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| GEO | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Crawler | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Prompts | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| IA | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Logs | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| API keys | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Configuration avancée | Oui | Oui | Oui | Oui | Oui | Oui | Oui |

### 24.2 Approche

Chaque module futur doit suivre :

```text
Contrat métier
  |
  v
Modèle + migration
  |
  v
Schemas
  |
  v
Repository
  |
  v
Service
  |
  v
Route
  |
  v
Tests
```

### 24.3 Points spécifiques

| Module | Point d'attention |
|---|---|
| SEO | Volumétrie URL et scores |
| GEO | Historisation réponses IA |
| Crawler | Jobs asynchrones |
| Reports | Génération et stockage |
| Prompts | Versioning |
| IA | Coûts, latence, erreurs providers |
| Logs | Pagination stricte |
| API keys | Secrets chiffrés/masqués |

---

## 25. Intégration Desktop

### 25.1 Contrat REST stable

Le Desktop consomme les endpoints `/api/v1`. Le backend doit maintenir des réponses stables ou introduire une nouvelle
version API en cas de rupture.

### 25.2 Diagramme

```text
Desktop Page
    |
    v
ApiClient
    |
    v
GET /api/v1/<module>
    |
    v
FastAPI route
    |
    v
Service
    |
    v
Repository
```

### 25.3 Règles de compatibilité

| Changement backend | Impact Desktop | Règle |
|---|---|---|
| Ajout champ optionnel | Faible | Compatible |
| Suppression champ | Fort | Versionner ou coordonner |
| Changement pagination | Fort | Éviter |
| Nouveau code erreur | Moyen | Documenter |
| Auth obligatoire | Fort | Coordonner avec Desktop |

### 25.4 Erreurs pour Desktop

Les erreurs doivent permettre au Desktop de distinguer :

- API indisponible ;
- validation invalide ;
- permission refusée ;
- session expirée future ;
- conflit métier ;
- erreur serveur.

### 25.5 Absence de dépendance inverse

Le backend ne doit jamais importer :

- `desktop.*` ;
- PySide6 ;
- fichiers QSS ;
- logique de widgets.

---

## 26. Performance backend

### 26.1 Principes

| Principe | Application |
|---|---|
| Pagination obligatoire | Grandes listes |
| Éviter N+1 | `selectinload`/`joinedload` si nécessaire |
| Index utiles | Colonnes filtrées/triées |
| Requêtes filtrées | Ne pas charger puis filtrer en Python |
| Limites page_size | Protéger DB |
| Jobs asynchrones futurs | Crawls, rapports lourds |
| Cache futur | Données peu volatiles |

### 26.2 Checklist performance

| Contrôle | OK |
|---|---|
| Endpoint liste paginé | |
| Tri whitelisted | |
| Filtre appliqué SQL | |
| Pas de N+1 évident | |
| Index prévu pour filtre fréquent | |
| Page size max | |
| Export lourd non synchrone | |
| Tests volumétrie futurs prévus | |

### 26.3 Requêtes lentes

Les requêtes lentes futures doivent être observées via :

- logs SQL si activés ;
- métriques ;
- traces ;
- endpoint admin santé ;
- analyse PostgreSQL.

---

## 27. Observabilité backend

### 27.1 Objectif

L'observabilité doit permettre de diagnostiquer :

- erreurs API ;
- lenteurs ;
- échecs DB ;
- erreurs providers IA ;
- erreurs auth futures ;
- actions admin sensibles.

### 27.2 Logs

| Type | Exemple |
|---|---|
| Applicatif | route appelée, durée |
| Erreur | exception normalisée |
| Sécurité | login échoué futur |
| Audit | rôle modifié |
| Performance | requête lente |

### 27.3 Métriques futures

| Métrique | Usage |
|---|---|
| `http_requests_total` | Volume API |
| `http_request_duration` | Latence |
| `db_query_duration` | Performance DB |
| `auth_failures_total` | Sécurité |
| `jobs_running` | Crawls/rapports |

### 27.4 Traces futures

Une trace doit pouvoir relier :

```text
Request ID
  |
  +-- Route
  +-- Service
  +-- Repository
  +-- SQL
  +-- External connector future
```

---

## 28. Anti-patterns interdits

### 28.1 Tableau

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Logique métier dans les routes | Duplication, tests difficiles | Service |
| SQLAlchemy dans les routes | Couplage API/DB | Repository |
| Pydantic dans repositories | Couplage API/persistence | Service convertit |
| `Base.metadata.create_all()` dans migrations | Migration non contrôlée | `op.create_table` |
| Endpoint admin non protégé | Faille sécurité | `require_admin` futur |
| Suppression destructive non contrôlée | Perte données | Soft delete/confirmation/service |
| Secrets dans le code | Fuite | Variables env |
| Tests trop larges | Fragiles | Tests ciblés |
| Duplication logique pagination | Incohérence | Dépendance commune |
| Desktop importé dans backend | Couplage inverse | REST |
| SQL brut inutile | Risque injection/maintenance | SQLAlchemy |
| Response model absent | Contrat flou | Schema Pydantic |

### 28.2 Exemple interdit

```text
Route /websites
  |
  +-- db.query(Website)
  +-- vérifie doublon
  +-- commit
  +-- construit dict JSON
```

### 28.3 Exemple correct

```text
Route /websites
  |
  +-- WebsiteService.create(payload)
        |
        +-- WebsiteRepository.exists_by_url
        +-- WebsiteRepository.create
  |
  +-- response_model WebsiteRead
```

---

## 29. Checklist avant Pull Request backend

| Contrôle | Commande ou action | OK |
|---|---|---|
| Statut Git | `git status` | |
| Stat diff | `git diff --stat` | |
| Espaces/fin lignes | `git diff --check` | |
| Tests | `py -m pytest` | |
| Ruff | `py -m ruff check .` | |
| Migration vérifiée | upgrade/downgrade relus | |
| Pas de secrets | scan manuel | |
| Architecture respectée | Routes -> Services -> Repositories -> Models | |
| Documentation à jour | docs si contrat change | |
| Tests API | ajoutés ou adaptés | |
| Tests service | ajoutés ou adaptés | |
| Erreurs | codes HTTP cohérents | |
| Pagination | standard respecté | |

---

## 30. Roadmap backend

### 30.1 Socle administration

- utilisateurs ;
- rôles ;
- permissions ;
- paramètres ;
- logs ;
- providers IA.

### 30.2 Websites / Entities

- sites ;
- entités ;
- relations ;
- pagination ;
- CRUD complet.

### 30.3 Keywords

- mots-clés ;
- volumes ;
- positions ;
- tags ;
- import/export.

### 30.4 Competitors

- concurrents ;
- domaines ;
- comparaison ;
- historique.

### 30.5 Reports

- génération ;
- statuts ;
- export ;
- planification future.

### 30.6 SEO

- audits ;
- URLs ;
- balises ;
- indexation ;
- performances.

### 30.7 GEO

- prompts ;
- réponses IA ;
- citations ;
- visibilité par modèle ;
- historique.

### 30.8 Crawler

- jobs ;
- files d'exécution futures ;
- résultats ;
- erreurs.

### 30.9 IA

- fournisseurs ;
- modèles ;
- coûts ;
- latence ;
- erreurs.

### 30.10 Authentification complète

- login ;
- tokens ;
- refresh ;
- RBAC ;
- audit sécurité.

### 30.11 Observabilité

- logs structurés ;
- métriques ;
- traces ;
- requêtes lentes.

### 30.12 API stable v1

- contrats stabilisés ;
- documentation OpenAPI ;
- compatibilité Desktop ;
- politique de versionnement.

---

## 31. Annexes

### 31.1 Glossaire

| Terme | Définition |
|---|---|
| Route | Endpoint FastAPI exposé en HTTP |
| Service | Couche métier |
| Repository | Couche accès aux données |
| Model | Classe SQLAlchemy représentant une table |
| Schema | Classe Pydantic représentant un contrat API |
| Migration | Script Alembic modifiant la structure DB |
| Fixture | Préparation de contexte de test |
| Pagination | Découpage d'une liste en pages |
| RBAC | Autorisation par rôles |

### 31.2 Abréviations

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| DB | Database |
| ORM | Object Relational Mapper |
| FK | Foreign Key |
| PK | Primary Key |
| CRUD | Create, Read, Update, Delete |
| SEO | Search Engine Optimization |
| GEO | Generative Engine Optimization |
| IA | Intelligence artificielle |

### 31.3 Diagramme récapitulatif

```text
Client
  |
  v
FastAPI Route
  |
  +-- Pydantic input
  +-- Dependencies
  |
  v
Service
  |
  +-- Business rules
  +-- Domain errors
  |
  v
Repository
  |
  +-- SQLAlchemy queries
  |
  v
Model
  |
  v
PostgreSQL
  |
  v
Pydantic response
```

### 31.4 Conventions rapides

| Besoin | Règle |
|---|---|
| Ajouter endpoint | Route fine + service |
| Ajouter règle métier | Service |
| Ajouter requête DB | Repository |
| Ajouter table | Model + migration |
| Ajouter payload API | Schema |
| Ajouter liste | Pagination standard |
| Ajouter sécurité | Dépendance centralisée |
| Ajouter test | API + service |

### 31.5 Checklist développeur

| Question | Réponse attendue |
|---|---|
| Ma route contient-elle de la logique métier ? | Non |
| Mon service est-il testable ? | Oui |
| Mon repository dépend-il de FastAPI ? | Non |
| Mon model correspond-il à une migration ? | Oui |
| Mon schema expose-t-il un secret ? | Non |
| Ma liste est-elle paginée ? | Oui si nécessaire |
| Mes erreurs sont-elles cohérentes ? | Oui |
| Ruff et Pytest passent-ils ? | Oui |

### 31.6 Modèle de structure de module

```text
backend/app/models/<module>.py
backend/app/schemas/<module>.py
backend/app/repositories/<module>.py
backend/app/services/<module>.py
backend/app/api/v1/routes/<module>.py
backend/alembic/versions/<revision>_<module>.py
tests/api/test_<module>_routes.py
tests/services/test_<module>_services.py
```

### 31.7 Résumé architectural

L'architecture backend officielle de Veille SEO-GEO Groupe A.P&Partner repose sur une séparation stricte des couches :

```text
Routes -> Services -> Repositories -> Models
```

Les routes exposent l'API, les services portent la logique métier, les repositories isolent SQLAlchemy, les modèles
décrivent PostgreSQL, les schémas Pydantic forment les contrats API, les migrations Alembic décrivent explicitement
les évolutions de structure, et les tests garantissent la stabilité.

Cette spécification doit être appliquée à tout développement backend jusqu'à la version 1.0 et rester cohérente avec
`docs/UI_UX.md`, `docs/architecture/AUTHENTICATION.md` et `docs/architecture/DESKTOP_ARCHITECTURE.md`.
