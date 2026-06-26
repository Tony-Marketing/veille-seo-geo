# Sprint 02 — Développement de l'API REST

**Statut :** À réaliser

---

# Objectif

Développer l'ensemble de l'architecture API du projet en s'appuyant sur les modèles de données créés lors du Sprint 01.

À l'issue de ce sprint, le backend devra exposer des endpoints REST complets permettant d'interagir avec les principales entités de l'application.

Aucune interface React ne sera développée durant ce sprint.

---

# Livrables attendus

## Architecture API

Créer l'organisation suivante :

```
backend/app/

api/
    v1/
        routes/

services/

repositories/

schemas/
```

Toutes les routes devront être regroupées par domaine fonctionnel.

---

# Schémas Pydantic

Créer les schémas :

- Create
- Update
- Read
- List

pour chaque entité métier.

Exemple :

```
EntityCreate

EntityUpdate

EntityRead

EntityList
```

Tous les schémas devront être fortement typés.

---

# Repositories

Créer un repository pour chaque entité principale.

Chaque repository devra encapsuler l'ensemble des accès à PostgreSQL.

Les routes API ne devront jamais accéder directement à SQLAlchemy.

---

# Services

Créer une couche métier entre :

Routes

↓

Services

↓

Repositories

↓

Base PostgreSQL

Toute logique métier devra être implémentée dans les services.

---

# Endpoints REST

Créer les opérations CRUD pour les principales entités :

## Entités

- GET
- GET par ID
- POST
- PUT
- DELETE

---

## Sites

- GET
- POST
- PUT
- DELETE

---

## Concurrents

- GET
- POST
- PUT
- DELETE

---

## Mots-clés

- GET
- POST
- PUT
- DELETE

---

## URLs

- GET
- POST
- PUT
- DELETE

---

## Rapports

- GET
- POST
- DELETE

---

## Tâches Projet

- GET
- POST
- PUT
- DELETE

---

# Pagination

Toutes les listes devront intégrer :

- pagination
- tri
- recherche
- filtres

Les paramètres devront être standardisés.

Exemple :

```
?page=1

?page_size=50

?sort=name

?order=asc
```

---

# Gestion des erreurs

Toutes les erreurs devront utiliser :

HTTPException

avec des messages explicites.

Les réponses devront être homogènes sur toute l'application.

---

# Validation

Toutes les données devront être validées avec Pydantic.

Aucune donnée ne devra être enregistrée sans validation préalable.

---

# Documentation Swagger

Chaque endpoint devra être documenté automatiquement.

La documentation Swagger devra être immédiatement exploitable.

---

# Tests

Créer des tests unitaires pour :

- les repositories
- les services
- les endpoints principaux

Utiliser Pytest.

---

# Documentation

Mettre à jour :

- README.md
- ARCHITECTURE.md

Ajouter les nouvelles routes dans :

```
docs/api/
```

---

# Hors périmètre

Ne pas développer :

- interface React
- authentification
- rôles utilisateurs
- connecteurs Google
- OpenAI
- Gemini
- scraping
- GEO
- dashboard
- rapports PDF

Le sprint concerne exclusivement le backend REST.

---

# Critères d'acceptation

Le sprint est considéré terminé si :

✓ Tous les endpoints CRUD fonctionnent.

✓ Les schémas Pydantic sont créés.

✓ Les repositories sont opérationnels.

✓ Les services métier sont séparés des routes.

✓ Swagger documente automatiquement toutes les API.

✓ Les tests principaux passent avec succès.

✓ Le backend peut être utilisé indépendamment d'une interface graphique.

---

# Résultat attendu

À la fin du Sprint 02, le backend constitue une API REST complète, proprement architecturée et prête à être consommée par le frontend React qui sera développé lors du Sprint 03.

---

# Prompt Codex

Respecte strictement les fichiers :

- AGENTS.md
- ARCHITECTURE.md
- README.md
- CONTRIBUTING.md

Travaille exclusivement sur le backend.

N'implémente aucune interface React.

Respecte l'architecture suivante :

Routes
↓
Services
↓
Repositories
↓
PostgreSQL

Ne place jamais de logique métier dans les routes.

Crée un repository et un service dédiés pour chaque entité.

Implémente des endpoints REST complets (CRUD) avec FastAPI.

Utilise Pydantic pour toutes les validations.

Ajoute une pagination, un tri et des filtres cohérents sur les endpoints de liste.

Documente automatiquement toutes les routes dans Swagger.

Produis également les tests unitaires nécessaires.

À la fin de ton travail :

- explique l'organisation des fichiers créés ;
- justifie les choix d'architecture ;
- liste les endpoints disponibles ;
- indique les tests réalisés ;
- n'effectue aucune modification en dehors du périmètre de ce sprint.