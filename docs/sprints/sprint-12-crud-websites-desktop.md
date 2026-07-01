# Sprint 12 - CRUD Websites Desktop

## Objectif

Le Sprint 12 transforme le module Desktop Websites en module de gestion complet des sites Web.

Le sprint permet de :

- consulter les sites ;
- creer un site ;
- modifier un site ;
- supprimer un site apres confirmation ;
- rafraichir automatiquement la liste apres chaque operation ;
- afficher des messages d'erreur utilisateurs.

## Contexte

Le Sprint 11 a livre le module Desktop Websites en lecture seule.

Le backend Websites expose deja les endpoints REST necessaires et respecte l'architecture projet :

```text
Routes -> Services -> Repositories -> Models
```

Le Desktop reste decouple du backend et communique uniquement via HTTP REST :

```text
WebsitesPage -> WebsitesService -> ApiClient -> FastAPI
```

Aucune modification backend, SQLAlchemy ou Alembic n'a ete necessaire pour ce sprint.

## Perimetre

### Inclus

- Extension du service Desktop Websites avec les operations de creation, modification et suppression.
- Ajout d'un dialogue Desktop reutilisable pour creer et modifier un site.
- Ajout des boutons `Ajouter`, `Modifier`, `Supprimer` et conservation de `Rafraichir`.
- Confirmation utilisateur avant suppression.
- Rechargement automatique de la liste apres creation, modification et suppression.
- Validation Desktop minimale avant envoi API :
  - nom obligatoire ;
  - URL obligatoire ;
  - URL HTTP(S) avec domaine ;
  - identifiant d'entite numerique si renseigne.
- Gestion lisible des erreurs API et reseau.

### Exclu

- Modification backend.
- Modification des routes FastAPI.
- Modification des schemas Pydantic backend.
- Modification des modeles SQLAlchemy.
- Migration Alembic.
- Acces direct Desktop a PostgreSQL.
- Import de modeles SQLAlchemy backend dans le Desktop.
- Tests UI PySide6 avec `pytest-qt`.

## Architecture

Le flux Desktop reste :

```text
WebsitesPage
    -> WebsitesService
        -> ApiClient
            -> FastAPI
```

`WebsitesPage` gere l'affichage, la selection, les dialogues et les messages utilisateur.

`WebsitesService` centralise les appels REST, le parsing des reponses et la traduction des erreurs `ApiClientError`.

`ApiClient` reste un client HTTP generique. Il n'a pas ete modifie.

## Endpoints reutilises

- `GET /api/v1/websites`
- `POST /api/v1/websites`
- `PUT /api/v1/websites/{id}`
- `DELETE /api/v1/websites/{id}`

## Fichiers crees

- `desktop/ui/dialogs/website_dialog.py`
- `docs/sprints/sprint-12-crud-websites-desktop.md`

## Fichiers modifies

- `desktop/services/websites_service.py`
- `desktop/ui/websites_page.py`
- `tests/desktop/test_websites_service.py`

## Fichiers non modifies

- `desktop/core/api_client.py`
- `backend/`
- `backend/alembic/`
- modeles SQLAlchemy
- schemas Pydantic backend
- routes FastAPI

## Strategie de tests

Les tests automatiques restent limites a la couche Service Desktop, sans ajout de `pytest-qt`.

Tests ajoutes ou completes :

- creation via `POST /websites` ;
- modification via `PUT /websites/{id}` ;
- suppression via `DELETE /websites/{id}` ;
- mapping des erreurs `401`, `403`, `404`, `409`, `422` ;
- erreurs reseau sur operation d'ecriture ;
- payload API inattendu sur ressource unique.

Les routes backend Websites existantes ont ete relancees pour verifier le contrat REST reutilise par le Desktop.

## Criteres d'acceptation

- Il est possible d'ajouter un site depuis le Desktop.
- Il est possible de modifier le site selectionne.
- Il est possible de supprimer le site selectionne apres confirmation.
- La liste est rechargee automatiquement apres chaque operation.
- Les validations Desktop minimales sont appliquees avant appel API.
- Les erreurs API courantes sont affichees avec un message utilisateur.
- Aucune modification backend n'a ete necessaire.
- Ruff passe.
- Pytest passe.

## Resultats Ruff

Commande executee :

```powershell
& "C:\Users\assistant.marketing\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m ruff check desktop tests
```

Resultat :

```text
All checks passed!
```

## Resultats Pytest

Commande ciblee executee :

```powershell
& "C:\Users\assistant.marketing\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pytest tests/desktop/test_websites_service.py tests/api/test_websites_routes.py
```

Resultat :

```text
28 passed, 1 warning
```

Commande globale executee :

```powershell
& "C:\Users\assistant.marketing\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pytest
```

Resultat :

```text
79 passed, 1 warning
```

## Points de vigilance

- Les tests UI PySide6 restent manuels pour ce sprint, car aucune infrastructure `pytest-qt` n'est introduite.
- Le warning Pytest provient de `fastapi.testclient` et signale une deprecation Starlette liee a `httpx`.
- Les validations Desktop restent volontairement minimales ; les validations metier restent cote backend.
