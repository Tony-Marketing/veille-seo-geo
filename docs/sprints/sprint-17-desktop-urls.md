# Sprint 17 - Desktop URLs

## Nature du document

Ce document est une reconstitution documentaire.

Il ne s'agit pas d'une copie du document historique original du Sprint 17. La reconstitution repose uniquement sur
l'etat actuel du depot, l'historique Git local disponible, les fichiers Backend suivis par Git, la documentation des
sprints voisins et les traces compilees `.pyc` retrouvees dans le dossier de travail.

Aucun code n'a ete recree pour etablir ce document.

## Contexte

Les sprints precedents ont installe les fondations Desktop et Backend suivantes :

- Sprint 08 : shell Desktop PySide6, navigation et pages de modules ;
- Sprint 09 : `ApiClient` Desktop pour communiquer avec l'API FastAPI ;
- Sprint 10 : authentification Desktop et session utilisateur ;
- Sprint 11 et Sprint 12 : module Desktop Websites et CRUD ;
- Sprint 13 : securisation des routes metier par JWT et permissions RBAC ;
- Sprint 14 : module Desktop Entities ;
- Sprint 15 : module Desktop Keywords ;
- Sprint 16 : module Desktop Competitors.

La documentation Sprint 16 annonce que le Sprint 17 devait etre consacre au module Desktop URLs. La documentation
Sprint 18 mentionne ensuite les URLs comme un module Desktop de reference, mais le code source Desktop URLs n'est pas
present dans le depot Git suivi.

## Informations retrouvees lors de l'audit

L'audit a confirme les points suivants :

- le Backend URLs est present et suivi par Git ;
- les endpoints `/api/v1/urls` existent ;
- les schemas Pydantic `UrlCreate`, `UrlUpdate`, `UrlRead` et `UrlList` existent ;
- les permissions `url.read`, `url.write` et `url.delete` sont initialisees dans le script d'administration ;
- les routes URLs sont couvertes par les tests API de securite metier ;
- aucun fichier source Desktop URLs suivi par Git n'existe dans l'etat actuel ;
- aucun commit local disponible ne contient de fichier source Desktop URLs ;
- des fichiers `.pyc` locaux indiquent qu'un module Desktop URLs a probablement existe ou ete execute localement.

Traces compilees identifiees :

- `desktop/services/__pycache__/urls_service.cpython-312.pyc`
- `desktop/ui/__pycache__/urls_page.cpython-312.pyc`
- `desktop/ui/dialogs/__pycache__/url_dialog.cpython-312.pyc`
- `tests/desktop/__pycache__/test_urls_service.cpython-312-pytest-9.1.1.pyc`

Ces fichiers `.pyc` ne constituent pas du code source maintenable et ne doivent pas etre utilises comme base directe
de developpement sans reimplementation explicite.

## Fonctionnalites attendues

D'apres les traces retrouvees et la philosophie des sprints 14 a 18, le Sprint 17 devait vraisemblablement couvrir :

- consultation paginee des URLs ;
- recherche textuelle ;
- creation d'une URL ;
- modification d'une URL ;
- suppression d'une URL apres confirmation ;
- rafraichissement manuel ;
- pagination avec actions precedent et suivant ;
- validations Desktop minimales ;
- gestion des erreurs HTTP ;
- gestion des erreurs reseau ;
- tests de la couche Service Desktop.

Le module devait rester limite a un CRUD Desktop simple, sans crawl, audit technique avance, export, statistiques ou
graphiques.

## Endpoints Backend utilises

Endpoints REST disponibles cote Backend :

| Methode HTTP | Endpoint | Operation | Permission |
| --- | --- | --- | --- |
| `GET` | `/api/v1/urls` | Liste paginee des URLs | `url.read` |
| `GET` | `/api/v1/urls/{item_id}` | Consultation d'une URL par identifiant | `url.read` |
| `POST` | `/api/v1/urls` | Creation d'une URL | `url.write` |
| `PUT` | `/api/v1/urls/{item_id}` | Modification d'une URL | `url.write` |
| `DELETE` | `/api/v1/urls/{item_id}` | Suppression d'une URL | `url.delete` |

Chemins relatifs attendus via `ApiClient` :

- `GET /urls`
- `POST /urls`
- `PUT /urls/{id}`
- `DELETE /urls/{id}`

L'endpoint de liste utilise les parametres communs de pagination :

- `page`
- `page_size`
- `search`
- `sort`
- `order`

Le repository Backend configure la recherche sur le champ `url`.

## Champs API identifies

Champs acceptes en creation avec `UrlCreate` :

| Champ | Type | Obligatoire | Validation |
| --- | --- | --- | --- |
| `website_id` | `int | None` | Non | aucune validation service specifique identifiee |
| `url` | `str` | Oui | longueur minimum `8`, longueur maximum `500` |
| `status_code` | `int | None` | Non | entre `100` et `599` |
| `is_indexable` | `bool` | Non | valeur par defaut `True` |

Champs acceptes en modification avec `UrlUpdate` :

| Champ | Type | Obligatoire | Validation |
| --- | --- | --- | --- |
| `website_id` | `int | None` | Non | aucune validation service specifique identifiee |
| `url` | `str | None` | Non | si fourni : longueur minimum `8`, longueur maximum `500` |
| `status_code` | `int | None` | Non | entre `100` et `599` |
| `is_indexable` | `bool | None` | Non | booleen |

Champs exposes en lecture avec `UrlRead` :

- `id`
- `website_id`
- `url`
- `status_code`
- `is_indexable`
- `created_at`
- `updated_at`

## Architecture prevue

Architecture Desktop attendue :

```text
UrlsPage
    -> URLsService
        -> ApiClient
            -> API REST
```

Regles attendues :

- aucune connexion directe a PostgreSQL ;
- aucun import SQLAlchemy dans le Desktop ;
- aucun appel HTTP direct depuis la page ;
- aucune logique metier Backend dans l'interface ;
- passage obligatoire par un service Desktop dedie et `ApiClient`.

## Composants Desktop identifies par les fichiers `.pyc`

Les traces compilees indiquent les composants probables suivants :

- `desktop/services/urls_service.py`
- `desktop/ui/urls_page.py`
- `desktop/ui/dialogs/url_dialog.py`
- `tests/desktop/test_urls_service.py`

Elements retrouves dans `urls_service.pyc` :

- `PaginatedUrls`
- `URLsServiceError`
- `URLsService`
- `list_urls`
- `create_url`
- `update_url`
- `delete_url`
- `_parse_paginated_response`
- `_parse_url_response`
- `_to_service_error`

Elements retrouves dans `urls_page.pyc` :

- `URLsPage`
- `load_urls`
- `search_urls`
- `previous_page`
- `next_page`
- `create_url`
- `edit_url`
- `delete_url`
- `_populate_table`
- `_selected_url`
- `_update_pagination_actions`
- `_website_label`
- `_status_code_label`

Elements retrouves dans `url_dialog.pyc` :

- `URLDialog`
- champs `website_id`, `status_code`, `is_indexable` ;
- constantes `MIN_STATUS_CODE` et `MAX_STATUS_CODE` ;
- `payload`
- `_accept_if_valid`
- `_validation_error`

Elements retrouves dans `test_urls_service.pyc` :

- chargement via `GET /urls?page=1&page_size=100` ;
- recherche via `GET /urls?page=2&page_size=5&search=audit` ;
- creation via `POST /urls` ;
- modification via `PUT /urls/1` ;
- suppression via `DELETE /urls/1` ;
- tests d'erreurs d'acces ;
- tests d'erreurs reseau ;
- tests de backend indisponible ;
- tests de payload invalide.

## Limites de la reconstitution

Cette reconstitution a des limites importantes :

- le document historique original n'a pas ete retrouve ;
- les fichiers source Desktop URLs ne sont pas presents dans Git ;
- les fichiers `.pyc` ne permettent pas de garantir l'implementation exacte ;
- les libelles, colonnes et messages utilisateur ne peuvent etre reconstitues qu'a titre indicatif ;
- l'integration exacte dans `MainWindow` et la navigation Desktop n'est pas verifiable dans le code source actuel ;
- aucune branche distante disponible localement ne permet de restaurer le Sprint 17 ;
- aucune correction ou reimplementation du Sprint 17 n'est realisee dans ce document.

## Hors perimetre

Ne fait pas partie de cette reconstitution :

- recreer le code Desktop URLs ;
- modifier le Backend URLs ;
- creer des tests URLs ;
- modifier la navigation Desktop ;
- extraire ou decompiler les `.pyc` pour produire du code ;
- corriger l'historique Git ;
- creer un commit ou une Pull Request.
