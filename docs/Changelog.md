# Changelog

Toutes les évolutions importantes du projet **Veille SEO-GEO Groupe A.P&Partner** sont documentées dans ce fichier.

Le format est inspiré de **Keep a Changelog**.

---

## Sprint 37 — Moteur de recommandations SEO/GEO

### Ajout

- moteur transverse de consolidation, déduplication et priorisation des recommandations persistées ;
- cycle de vie `OPEN`, `ACKNOWLEDGED`, `RESOLVED` et `IGNORED` ;
- API REST filtrable et paginée avec synthèse et mise à jour du statut ;
- permissions `recommendation.read` et `recommendation.write` ;
- page Desktop Recommandations et intégration à la navigation ;
- alimentation des recommandations du Dashboard V2 par le moteur transverse.

---

# Version 0.1.0 (En développement)

## Sprint 00 — Initialisation du projet

### Ajout

- Initialisation du dépôt Git
- Création de l'architecture du projet
- Mise en place de FastAPI
- Mise en place de SQLAlchemy 2.x
- Mise en place d'Alembic
- Configuration PostgreSQL
- Configuration Pytest
- Configuration Ruff
- Documentation initiale

---

## Sprint 01 — Conception de la base de données

### Ajout

- Modèle relationnel
- Conception des entités
- Relations SQLAlchemy
- Migrations Alembic

---

## Sprint 02 — Développement de l'API REST

### Ajout

- Structure REST
- Organisation des routes
- Schémas Pydantic
- Documentation OpenAPI

---

## Sprint 03 — Authentification et gestion des utilisateurs

### Ajout

- Authentification JWT
- Gestion des utilisateurs
- Gestion des rôles
- Gestion des permissions

---

## Sprint 04 — Développement du Frontend

### Ajout

- Préparation de l'architecture Frontend
- Organisation des futurs composants

---

## Sprint 05 — Gestion des sites web

### Ajout

- Module Website
- CRUD complet des sites web
- Repository Website
- Service Website
- Routes REST
- Migration Alembic
- Tests unitaires
- Documentation API

---

## Sprint 06 — Interface d'administration Backend

### Ajout

- Interface d'administration
- Dashboard
- Navigation
- Gestion des sites web
- Templates communs
- Pages d'erreur
- Interface interne de développement
