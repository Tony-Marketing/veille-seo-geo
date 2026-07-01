# Sprint 16 - Module Desktop Competitors

## 1. Objectifs

Le Sprint 16 a pour objectif de livrer le module Desktop Competitors.

Ce sprint remplace le placeholder `CompetitorsPage` par un module CRUD fonctionnel, coherent avec les modules Desktop
deja livres.

Le module Competitors reproduit fidelement l'architecture et les conventions appliquees aux modules :

- Websites ;
- Entities ;
- Keywords.

Le developpement reste une extension de l'existant. Aucune nouvelle architecture n'est introduite pour ce module.

Objectifs fonctionnels livres :

- consulter les concurrents depuis l'API REST ;
- creer un concurrent ;
- modifier un concurrent existant ;
- supprimer un concurrent apres confirmation ;
- rafraichir manuellement la liste ;
- afficher des messages utilisateur lisibles ;
- gerer les erreurs HTTP et reseau ;
- appliquer des validations Desktop minimales avant les appels API.

## 2. Contexte

Les sprints precedents ont installe les fondations necessaires au module Competitors :

- Sprint 08 : shell Desktop, navigation et placeholders de modules ;
- Sprint 09 : connexion Desktop vers API via `ApiClient` ;
- Sprint 10 : authentification Desktop et transmission du token Bearer ;
- Sprint 11 et Sprint 12 : module Websites et CRUD Desktop ;
- Sprint 13 : securisation des routes Backend par JWT et permissions RBAC ;
- Sprint 14 : module Desktop Entities ;
- Sprint 15 : module Desktop Keywords.

Le projet dispose deja d'un Backend FastAPI organise selon l'architecture :

```text
Routes
    -> Services
        -> Repositories
            -> Models
```

Le client Desktop PySide6 suit l'architecture :

```text
Page
    -> Service
        -> ApiClient
            -> API REST
```

Le Backend expose deja les endpoints CRUD securises pour les concurrents. Aucune evolution Backend n'est prevue dans le
Sprint 16.

Le Desktop doit continuer a communiquer exclusivement avec l'API REST. Il ne doit jamais acceder directement a
PostgreSQL et ne doit jamais importer les modeles SQLAlchemy du Backend.

## 3. Perimetre

Le Sprint 16 couvre uniquement le module Desktop Competitors.

Le module implemente :

- consultation paginee des concurrents ;
- creation d'un concurrent ;
- modification du concurrent selectionne ;
- suppression du concurrent selectionne apres confirmation ;
- rafraichissement manuel de la liste ;
- rechargement automatique apres creation, modification et suppression ;
- affichage de messages de succes et d'erreur ;
- gestion des erreurs HTTP renvoyees par l'API ;
- gestion des erreurs reseau ;
- validations Desktop minimales avant envoi a l'API.

Champs pris en charge cote Desktop :

- `name` : nom du concurrent ;
- `website_url` : URL optionnelle du site concurrent ;
- `entity_id` : rattachement optionnel a une entite par identifiant ;
- `is_active` : statut actif/inactif.

Les validations metier finales restent cote Backend. Le Desktop applique uniquement des controles simples pour
eviter les payloads manifestement invalides.

Les fonctionnalites SEO avancees sont hors perimetre. Le module Competitors du Sprint 16 ne doit pas introduire
d'analyse concurrentielle avancee, de comparaison SEO, de crawl, de statistiques ou de graphiques.

## 4. Architecture

L'architecture Desktop appliquee reste :

```text
CompetitorsPage
    -> CompetitorsService
        -> ApiClient
            -> API FastAPI
```

Aucune nouvelle architecture n'est introduite.

Responsabilites attendues :

- `CompetitorsPage` gere l'affichage, la selection, les boutons, les confirmations et les messages utilisateur.
- `CompetitorsService` gere les appels REST, le parsing des reponses et la traduction des erreurs `ApiClientError`.
- `CompetitorDialog` collecte les champs de creation et modification avec validation Desktop minimale.
- `ApiClient` reste le client HTTP generique existant.

Le Desktop doit continuer a respecter les regles suivantes :

- aucun acces direct a PostgreSQL ;
- aucun import de modele SQLAlchemy Backend ;
- aucune logique metier Backend dans la page PySide6 ;
- aucun appel HTTP direct depuis la page ;
- passage obligatoire par le service Desktop et `ApiClient`.

## 5. Composants Livres

Fichiers crees :

- `desktop/services/competitors_service.py`
- `desktop/ui/dialogs/competitor_dialog.py`
- `tests/desktop/test_competitors_service.py`

Fichiers modifies :

- `desktop/ui/competitors_page.py`
- `desktop/ui/main_window.py`
- `docs/sprints/sprint-16-desktop-competitors.md`

Fichiers non modifies :

- `backend/`
- `backend/app/api/v1/routes/competitors.py`
- `backend/app/services/competitors.py`
- `backend/app/repositories/competitors.py`
- `backend/app/schemas/competitors.py`
- `backend/app/models/`
- migrations Alembic ;
- `desktop/core/api_client.py`.

## 6. Backend Utilise

Le Backend Competitors existe deja et est consomme sans modification.

Endpoints REST utilises :

- `GET /api/v1/competitors`
- `GET /api/v1/competitors/{id}`
- `POST /api/v1/competitors`
- `PUT /api/v1/competitors/{id}`
- `DELETE /api/v1/competitors/{id}`

Le Desktop utilise les chemins relatifs suivants via `ApiClient` :

- `GET /competitors`
- `POST /competitors`
- `PUT /competitors/{id}`
- `DELETE /competitors/{id}`

Role des endpoints :

- `GET /competitors` : recuperer la liste paginee des concurrents ;
- `POST /competitors` : creer un concurrent ;
- `PUT /competitors/{id}` : modifier un concurrent existant ;
- `DELETE /competitors/{id}` : supprimer un concurrent existant.

L'endpoint `GET /api/v1/competitors/{id}` existe cote Backend mais n'est pas necessaire au CRUD Desktop actuel, qui
travaille a partir de la selection dans la liste paginee.

Permissions Backend attendues :

- lecture : `competitor.read` ;
- creation : `competitor.write` ;
- modification : `competitor.write` ;
- suppression : `competitor.delete`.

Schemas Backend deja disponibles :

- `CompetitorCreate`
- `CompetitorUpdate`
- `CompetitorRead`
- `CompetitorList`

Aucune route Backend, aucun schema Pydantic, aucun repository, aucun service Backend et aucune migration ne sont crees
ou modifies dans le cadre du Sprint 16.

## 7. Deroulement Du Developpement

Le developpement est realise par extension de l'existant :

1. analyse de l'existant, notamment `KeywordsService`, `KeywordDialog`, `KeywordsPage`, puis verification Entities et Websites ;
2. creation du service Desktop `CompetitorsService` ;
3. creation du dialogue `CompetitorDialog` ;
4. remplacement du placeholder `CompetitorsPage` par une page CRUD ;
5. integration de la page dans `MainWindow` avec injection du `ApiClient` existant ;
6. ajout des tests du service Desktop ;
7. validation avec les outils qualite disponibles ;
8. documentation finale du sprint et rapport d'execution.

Le developpement reste limite au module Competitors.

## 8. Tests Realises

Les tests automatiques concernent uniquement la couche Service Desktop.

Fichier cree :

```text
tests/desktop/test_competitors_service.py
```

Tests ajoutes :

- chargement de la liste via `GET /competitors` ;
- parsing d'une reponse paginee valide ;
- gestion d'une liste vide ;
- creation via `POST /competitors` ;
- modification via `PUT /competitors/{id}` ;
- suppression via `DELETE /competitors/{id}` ;
- mapping des erreurs `401` vers `unauthorized` ;
- mapping des erreurs `403` vers `forbidden` ;
- mapping des erreurs `404` vers `not_found` ;
- mapping des erreurs `409` vers `conflict` ;
- mapping des erreurs `422` vers `validation_error` ;
- mapping des erreurs `500` vers `server_error` ;
- mapping des erreurs reseau ;
- mapping du backend indisponible ;
- rejet d'un payload pagine invalide ;
- rejet d'un payload ressource invalide.

Les tests UI PySide6 automatises ne sont pas prevus pour ce sprint.

## 9. Validation

Le Sprint 16 est valide uniquement si :

- Ruff est OK ;
- Pytest est OK ;
- l'architecture Desktop `Page -> Service -> ApiClient -> API REST` est respectee ;
- le Backend reste inchange ;
- le Desktop n'importe aucun modele SQLAlchemy Backend ;
- le Desktop n'accede pas directement a PostgreSQL ;
- les erreurs HTTP et reseau sont gerees lisiblement ;
- les validations Desktop minimales sont presentes ;
- les fichiers modifies restent limites au perimetre annonce.

Commandes de validation executees en fin de developpement :

```text
python -m ruff check .
python -m pytest
```

## 10. Hors Perimetre

Le Sprint 16 ne comprend pas :

- tableaux de bord SEO ;
- statistiques ;
- crawl ;
- comparateurs ;
- import/export ;
- integration Google Search Console ;
- graphiques ;
- analyse de visibilite SEO ;
- analyse GEO ;
- scoring concurrentiel ;
- suivi de positions ;
- enrichissement automatique des donnees concurrentes ;
- refactor CRUD generique ;
- modification Backend ;
- migration Alembic ;
- modification des modeles SQLAlchemy ;
- modification des schemas Pydantic Backend ;
- modification des routes FastAPI ;
- tests UI PySide6 automatises.

## 11. Risques Et Points De Vigilance

Risques identifies :

- duplication excessive des modules Entities et Keywords sans harmonisation minimale ;
- creation prematuree d'une abstraction CRUD generique hors perimetre ;
- confusion entre concurrent simple et analyse concurrentielle avancee ;
- tentation d'ajouter des champs non exposes par le Backend actuel ;
- exposition d'identifiants techniques de maniere peu lisible pour l'utilisateur ;
- oubli des erreurs `401` et `403` liees aux permissions RBAC ;
- modification accidentelle du Backend alors que les endpoints existent deja.

Strategie de limitation :

- reprendre le modele de `KeywordsService` et `EntitiesService` ;
- limiter le module aux champs exposes par `CompetitorRead` ;
- conserver une validation Desktop minimale ;
- tester la couche Service avec transport HTTP simule ;
- documenter les limites fonctionnelles ;
- verifier en fin de sprint que le Backend est inchange.

## 12. Sprint Suivant

Le Sprint 17 sera consacre au module Desktop URLs.

Il devra appliquer la meme logique d'extension progressive :

- service Desktop dedie ;
- page CRUD ;
- dialogue si necessaire ;
- tests de la couche Service ;
- communication exclusive via `ApiClient` et API REST ;
- Backend inchange si les endpoints existants sont suffisants.
