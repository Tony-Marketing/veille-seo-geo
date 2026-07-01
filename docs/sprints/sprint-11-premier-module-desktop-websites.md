# Sprint 11 - Premier module métier Desktop : Gestion des sites Web

## Objectif

Le Sprint 11 vise à transformer la page Desktop Websites existante en premier module métier exploitable en lecture seule.

Le sprint doit permettre de récupérer les sites Web depuis l'API FastAPI, de les afficher dans la page Desktop existante, et de gérer proprement les principaux états utilisateur : chargement, liste vide, erreurs d'authentification, erreurs d'autorisation et indisponibilité du backend.

Aucun CRUD complet n'est inclus dans ce sprint.

## Contexte

Le backend Websites existe déjà avec une architecture conforme au projet :

```text
Routes FastAPI -> Service -> Repository -> Modèle SQLAlchemy -> Base de données
```

Le Desktop existe déjà avec PySide6, un shell principal, une session utilisateur en mémoire, un service d'authentification et un ApiClient centralisé.

Les sprints précédents ont posé :

- Sprint 08 : shell Desktop et page Websites initiale ;
- Sprint 09 : ApiClient Desktop et gestion des erreurs réseau/API ;
- Sprint 10 : authentification Desktop, session utilisateur en mémoire et injection Bearer.

Le Sprint 11 doit étendre l'existant, sans recréer d'architecture.

Décision validée pour ce sprint :

- Sprint 11 = Desktop Websites en lecture seule ;
- aucune modification backend ;
- les routes Websites backend restent inchangées ;
- les erreurs 401/403 sont gérées et testées côté Desktop via mocks ;
- aucun CRUD ;
- aucun tri, recherche ou pagination interactive Desktop ;
- aucun stockage persistant de session ;
- aucun accès direct Desktop à PostgreSQL ;
- aucun import de modèles SQLAlchemy backend dans le Desktop.

## Architecture concernée

### Backend

Fichiers existants concernés en lecture uniquement :

- `backend/app/api/v1/routes/websites.py`
- `backend/app/services/websites.py`
- `backend/app/repositories/websites.py`
- `backend/app/models/entities.py`
- `backend/app/schemas/websites.py`
- `backend/app/schemas/pagination.py`
- `backend/app/core/security.py`
- `backend/app/api/v1/dependencies.py`

Endpoint principal :

- `GET /api/v1/websites`

Réponse attendue :

- `items`
- `total`
- `page`
- `page_size`
- `pages`

Paramètres déjà disponibles côté backend :

- `page`
- `page_size`
- `search`
- `sort`
- `order`
- `is_active`

Ces paramètres ne seront pas exposés sous forme de recherche, tri ou pagination interactive dans le Desktop pendant ce sprint.

### Desktop

Fichiers existants concernés :

- `desktop/ui/websites_page.py`
- `desktop/core/api_client.py`
- `desktop/core/session.py`
- `desktop/services/auth_service.py`
- `desktop/ui/main_window.py`
- `desktop/ui/login_dialog.py`
- `desktop/widgets/statusbar.py`
- `desktop/widgets/topbar.py`
- `desktop/widgets/sidebar.py`

Le Desktop communique uniquement avec FastAPI via `ApiClient`.

## Analyse

Le backend fournit déjà la liste paginée des sites via `GET /api/v1/websites`.

Le repository `WebsiteRepository` supporte :

- pagination ;
- recherche simple sur `name`, `url`, `cms` ;
- tri si la colonne existe ;
- filtre `is_active`.

Le service `WebsiteService` retourne une réponse paginée basée sur `WebsiteRead`.

Le modèle `Website` contient :

- `id`
- `entity_id`
- `name`
- `url`
- `cms`
- `is_active`
- `created_at`
- `updated_at`

La page Desktop `WebsitesPage` existe déjà et appelle :

```python
ApiClient.get("/websites", params={"page": 1, "page_size": 100})
```

Elle affiche déjà un tableau avec :

- Nom
- URL
- Actif
- Entité

Le bouton `Rafraîchir` existe déjà.

L'authentification Bearer est déjà injectée par `ApiClient` lorsqu'une session contient un token.

Point de cadrage important : les routes backend Websites restent inchangées pendant le Sprint 11. Les cas `401 Unauthorized` et `403 Forbidden` seront donc couverts côté Desktop par tests mockés du client API ou du service Desktop, sans modifier la protection backend.

## Périmètre inclus

Le Sprint 11 inclut uniquement :

- récupérer les sites Web depuis l'API FastAPI ;
- afficher les sites dans `desktop/ui/websites_page.py` ;
- utiliser le Bearer token déjà géré par `ApiClient` ;
- gérer un état de chargement ;
- gérer une liste vide ;
- gérer explicitement une erreur `401 Unauthorized` côté Desktop ;
- gérer explicitement une erreur `403 Forbidden` côté Desktop ;
- gérer un backend indisponible ;
- gérer les erreurs réseau ;
- conserver un bouton d'actualisation ;
- ajouter les tests nécessaires au comportement Desktop ;
- documenter le sprint.

## Périmètre exclu

Le Sprint 11 exclut :

- création d'un site ;
- modification d'un site ;
- suppression d'un site ;
- CRUD complet ;
- recherche Desktop ;
- tri Desktop ;
- pagination Desktop interactive ;
- import/export ;
- dashboard ;
- configuration ;
- mots-clés ;
- concurrents ;
- GEO ;
- stockage persistant de session ;
- refactor global Desktop ;
- refactor global backend ;
- modification backend ;
- modification des routes Websites backend ;
- accès direct Desktop à PostgreSQL ;
- import de modèles SQLAlchemy backend dans le Desktop.

## Fichiers potentiellement concernés

### Backend

Aucun fichier backend ne doit être modifié pendant ce sprint.

Fichiers backend analysés ou utilisés comme contrat existant :

- `backend/app/api/v1/routes/websites.py`
- `backend/app/services/websites.py`
- `backend/app/repositories/websites.py`
- `backend/app/models/entities.py`
- `backend/app/schemas/websites.py`
- `backend/app/schemas/pagination.py`

### Desktop

Fichiers probablement modifiés pendant l'implémentation :

- `desktop/ui/websites_page.py`

Fichier créé pendant l'implémentation :

- `desktop/services/websites_service.py`

Rôle envisagé de `desktop/services/websites_service.py` :

- isoler l'appel API Websites ;
- centraliser le parsing de la réponse paginée ;
- garder `WebsitesPage` centrée sur l'affichage ;
- faciliter les tests des erreurs `401`, `403`, réseau et backend indisponible via mocks.

Fichier potentiellement modifié seulement si justifié :

- `desktop/core/api_client.py`

### Tests

Tests créés pendant l'implémentation :

- `tests/desktop/test_websites_service.py`

Tests UI non créés pendant ce sprint :

- `tests/desktop/test_websites_page.py`

Raison : aucune infrastructure de tests Qt dédiée (`pytest-qt`, `qtbot` ou équivalent) n'existe actuellement dans le dépôt. Le sprint ne doit pas créer une infrastructure complète uniquement pour tester cette page.

Tests potentiellement modifiés :

- `tests/desktop/test_api_client_auth.py`, uniquement pour non-régression Bearer si nécessaire.

Aucun test backend Websites ne doit être modifié pour ce sprint, sauf ajustement documentaire ou besoin explicitement validé hors périmètre courant.

### Documentation

Fichier de documentation du sprint :

- `docs/sprints/sprint-11-premier-module-desktop-websites.md`

## Stratégie de tests

### Tests existants à conserver

Backend :

- `tests/api/test_websites_routes.py`
- `tests/services/test_websites_services.py`

Desktop :

- `tests/desktop/test_api_client.py`
- `tests/desktop/test_api_client_auth.py`
- `tests/desktop/test_auth_service.py`

### Tests à prévoir

Service Desktop Websites :

- appel de `/websites` avec `page=1` et `page_size=100` ;
- parsing de la réponse paginée ;
- liste vide ;
- propagation ou traduction de l'erreur `401` ;
- propagation ou traduction de l'erreur `403` ;
- propagation ou traduction des erreurs réseau ;
- propagation ou traduction d'un backend indisponible.

Page Desktop Websites :

- affichage de l'état de chargement ;
- affichage des lignes dans le tableau ;
- affichage d'un message lisible si la liste est vide ;
- affichage d'un message lisible en cas de `401` ;
- affichage d'un message lisible en cas de `403` ;
- affichage d'un message lisible si le backend est indisponible ;
- affichage d'un message lisible en cas d'erreur réseau ;
- fonctionnement du bouton d'actualisation.

Les erreurs `401` et `403` seront simulées via mocks Desktop. Aucune modification backend n'est prévue pour produire ces statuts sur les routes Websites pendant ce sprint.

## Critères de validation

Le sprint sera valide si :

- la branche active est `sprint-11` ;
- la page Websites affiche les sites retournés par l'API ;
- le Desktop utilise `ApiClient` et n'appelle jamais PostgreSQL directement ;
- le Desktop n'importe aucun modèle SQLAlchemy backend ;
- le header Bearer est envoyé lorsque la session contient un token ;
- le bouton `Rafraîchir` recharge la liste ;
- un état de chargement est visible ;
- une liste vide affiche un message clair ;
- une erreur `401` mockée affiche un message clair ;
- une erreur `403` mockée affiche un message clair ;
- un backend indisponible affiche un message clair ;
- une erreur réseau ne provoque pas de crash ;
- aucun CRUD n'est ajouté ;
- aucune recherche, tri ou pagination Desktop interactive n'est ajoutée ;
- aucun stockage persistant de session n'est ajouté ;
- aucune route backend Websites n'est modifiée ;
- les tests ciblés passent ;
- Ruff passe sur le périmètre modifié ;
- aucun commit ni push n'est effectué sans demande explicite.

## Risques éventuels

- Les routes Websites backend ne sont pas protégées dans le cadre du Sprint 11 : le Desktop peut envoyer un Bearer token, mais les statuts `401` et `403` devront être testés via mocks côté Desktop.
- La page Websites charge actuellement les données dans son constructeur, ce qui peut produire un appel avant que l'utilisateur soit connecté selon le cycle d'initialisation de la fenêtre principale.
- Les tests de widgets PySide6 peuvent demander une fixture Qt spécifique si elle n'existe pas encore.
- Ajouter une méthode métier spécifique dans `ApiClient` pourrait transformer le client HTTP en service métier ; un service Desktop dédié est préférable si la logique dépasse un simple appel.
- Le sprint peut facilement dériver vers un CRUD complet ; cette dérive doit être évitée.
- Le Desktop ne doit pas réimplémenter les permissions métier : il affiche des messages, mais la sécurité réelle reste une responsabilité backend.
