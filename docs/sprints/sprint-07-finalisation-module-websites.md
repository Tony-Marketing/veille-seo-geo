# Sprint 07 - Finalisation du module Websites

## Objectif

Finaliser proprement le module Websites afin de rendre le CRUD des sites web exploitable, teste et coherent avec l'architecture du projet.

Le sprint complete le travail initie au Sprint 05 sans recreer le module ni modifier les fondations livrees au Sprint 06.

---

## Contexte

Le module Websites existe deja partiellement dans le code applicatif :

* modele SQLAlchemy ;
* schemas Pydantic ;
* repository ;
* service ;
* routes API ;
* modules de compatibilite pour les anciens imports Sprint 05.

Les elements manquants concernent principalement :

* une migration Alembic dediee ;
* la couverture de tests API ;
* la couverture de tests service ;
* le filtre `is_active` sur la liste des sites web.

---

## Perimetre

Le Sprint 07 couvre exclusivement :

* creation d'une migration Alembic dediee aux tables `entities` et `websites` ;
* ajout du filtre `is_active` sur `GET /api/v1/websites` ;
* validation de l'unicite de l'URL via le service existant ;
* ajout des tests API du module Websites ;
* ajout des tests service du module Websites ;
* documentation du sprint.

---

## Fichiers modifies ou crees

Fichiers crees :

* `backend/alembic/versions/20260626_0002_create_websites.py`
* `tests/api/test_websites_routes.py`
* `tests/services/test_websites_services.py`
* `docs/sprints/sprint-07-finalisation-module-websites.md`

Fichiers modifies :

* `backend/app/repositories/websites.py`
* `backend/app/services/websites.py`
* `backend/app/api/v1/routes/websites.py`

---

## Criteres d'acceptation

Le sprint est valide si :

* la migration `20260626_0002_create_websites.py` cree explicitement les tables `entities` et `websites` ;
* la migration ne s'appuie pas sur `Base.metadata.create_all()` ou `Base.metadata.drop_all()` ;
* la migration existante `20260626_0001_create_administration_backend.py` reste inchangee ;
* `GET /api/v1/websites` accepte `page`, `page_size`, `search` et `is_active` ;
* le filtre `is_active=true` retourne uniquement les sites actifs ;
* le filtre `is_active=false` retourne uniquement les sites inactifs ;
* les routes restent fines et deleguent la logique au service ;
* les repositories restent limites aux acces aux donnees ;
* les conflits d'URL retournent `409 Conflict` ;
* les ressources inexistantes retournent `404 Not Found` ;
* les tests Pytest passent ;
* Ruff ne remonte aucune erreur.

---

## Tests attendus

Tests API :

* creation d'un site ;
* lecture d'un site ;
* liste paginee ;
* recherche ;
* filtre `is_active=true` ;
* filtre `is_active=false` ;
* modification ;
* suppression ;
* conflit d'URL en `409` ;
* identifiant inexistant en `404`.

Tests service :

* creation ;
* unicite de l'URL ;
* modification ;
* conflit d'URL a la modification ;
* `404` sur ressource inexistante ;
* liste paginee ;
* filtre actif/inactif.

---

## Hors perimetre

Le Sprint 07 ne couvre pas :

* refactorisation globale des routes CRUD ;
* modification du routeur generique `create_crud_router()` ;
* modification des routes des autres modules ;
* ajout de dependance ;
* ajout d'authentification supplementaire ;
* developpement frontend ;
* crawler ;
* audit SEO ;
* module GEO ;
* statistiques ou tableaux de bord ;
* commit Git ;
* Pull Request.
