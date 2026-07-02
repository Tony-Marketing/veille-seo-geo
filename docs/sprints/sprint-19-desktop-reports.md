# Sprint 19 - Desktop Reports

## Objectif

Le Sprint 19 livre le module Desktop Reports en reproduisant la philosophie des modules Desktop metier deja presents :

- Websites ;
- Entities ;
- Keywords ;
- Competitors ;
- Project Tasks.

Le module Reports permet de consulter, rechercher, creer, modifier et supprimer des rapports via l'API REST existante.

Le Backend reste strictement inchange.

## Contexte

Le Sprint 18 Project Tasks est termine et fusionne. Avant le developpement Reports, un audit a confirme :

- le Backend Reports est deja disponible ;
- le Backend URLs est disponible ;
- le module Desktop URLs n'est plus present sous forme de code source suivi par Git ;
- des traces `.pyc` prouvent qu'un module Desktop URLs a probablement existe localement ;
- une reconstitution documentaire du Sprint 17 a ete creee dans `docs/sprints/sprint-17-desktop-urls.md`.

Le Sprint 19 s'appuie donc sur les modules Desktop effectivement presents dans le depot, principalement Project Tasks
pour la recherche et la pagination.

## Analyse de l'API Reports

### Endpoints disponibles

| Methode HTTP | Endpoint | Operation | Permission |
| --- | --- | --- | --- |
| `GET` | `/api/v1/reports` | Liste paginee des rapports | `report.read` |
| `GET` | `/api/v1/reports/{item_id}` | Consultation d'un rapport | `report.read` |
| `POST` | `/api/v1/reports` | Creation d'un rapport | `report.write` |
| `PUT` | `/api/v1/reports/{item_id}` | Modification d'un rapport | `report.write` |
| `DELETE` | `/api/v1/reports/{item_id}` | Suppression d'un rapport | `report.delete` |

Le Desktop utilise les chemins relatifs suivants via `ApiClient` :

- `GET /reports`
- `POST /reports`
- `PUT /reports/{id}`
- `DELETE /reports/{id}`

### Champs disponibles

Champs acceptes par `ReportCreate` :

| Champ | Type | Obligatoire | Validation |
| --- | --- | --- | --- |
| `entity_id` | `int | None` | Non | aucune validation service specifique identifiee |
| `title` | `str` | Oui | longueur minimum `2`, longueur maximum `200` |
| `report_type` | `str | None` | Non | longueur maximum `80` |
| `status` | `str` | Non | longueur maximum `50`, defaut `draft` |

Champs acceptes par `ReportUpdate` :

| Champ | Type | Obligatoire | Validation |
| --- | --- | --- | --- |
| `entity_id` | `int | None` | Non | aucune validation service specifique identifiee |
| `title` | `str | None` | Non | si fourni : longueur minimum `2`, longueur maximum `200` |
| `report_type` | `str | None` | Non | longueur maximum `80` |
| `status` | `str | None` | Non | longueur maximum `50` |

Champs exposes par `ReportRead` :

- `id`
- `entity_id`
- `title`
- `report_type`
- `status`
- `created_at`
- `updated_at`

### Fonctionnalites disponibles

Fonctionnalites Backend utilisees :

- liste paginee ;
- recherche via le parametre `search` ;
- creation ;
- modification ;
- suppression ;
- securisation RBAC.

La recherche Reports est configuree cote repository sur :

- `title`
- `report_type`
- `status`

### Contraintes

Contraintes identifiees :

- le Desktop ne doit pas inventer de champs absents de l'API ;
- aucun objet `entity` imbrique n'est expose par l'API actuelle ;
- aucun endpoint d'export, de generation ou de telechargement de rapport n'existe ;
- aucune liste fermee de statuts ou de types de rapport n'est fournie par le Backend ;
- aucune modification Backend n'est necessaire.

## Architecture retenue

Architecture appliquee :

```text
ReportsPage
    -> ReportsService
        -> ApiClient
            -> API REST
```

Responsabilites :

| Composant | Responsabilite |
| --- | --- |
| `ReportsPage` | Affichage, recherche, pagination, selection, actions utilisateur, confirmations et messages. |
| `ReportsService` | Appels REST, parsing des reponses paginees, mapping des erreurs API et reseau. |
| `ReportDialog` | Collecte des champs de creation/modification et validations Desktop minimales. |
| `ApiClient` | Client HTTP REST centralise existant. |

Regles respectees :

- aucun acces direct a PostgreSQL ;
- aucun import SQLAlchemy dans le Desktop ;
- aucun appel HTTP direct depuis la page ;
- aucune modification du Backend ;
- aucune nouvelle dependance.

## Ecrans prevus

### Page Reports

La page Reports remplace le placeholder et contient :

- titre de page ;
- champ de recherche ;
- bouton `Rechercher` ;
- bouton `Ajouter` ;
- bouton `Modifier` ;
- bouton `Supprimer` ;
- bouton `Rafraichir` ;
- tableau des rapports ;
- boutons `Precedent` et `Suivant` ;
- libelle de pagination ;
- zone de message utilisateur.

Colonnes affichees :

- `Titre`
- `Type`
- `Statut`
- `Entite`

### Dialogue Report

Le dialogue sert a la creation et a la modification.

Champs :

- `Titre` ;
- `Type` ;
- `Statut` ;
- `Entite ID`.

Les validations Desktop restent alignees sur les schemas Pydantic existants.

## Services crees

Fichier cree :

- `desktop/services/reports_service.py`

Methodes principales :

- `list_reports`
- `create_report`
- `update_report`
- `delete_report`

Codes d'erreur exposes :

- `unauthorized`
- `forbidden`
- `not_found`
- `conflict`
- `validation_error`
- `server_error`
- `backend_unavailable`
- `network_error`
- `unexpected`

## Dialogs crees

Fichier cree :

- `desktop/ui/dialogs/report_dialog.py`

Validations :

- `title` obligatoire ;
- `title` entre 2 et 200 caracteres ;
- `report_type` limite a 80 caracteres ;
- `status` limite a 50 caracteres ;
- `entity_id` numerique lorsqu'il est renseigne.

## Tests ajoutes

Fichier cree :

- `tests/desktop/test_reports_service.py`

Tests couverts :

- chargement de la liste ;
- transmission de la recherche ;
- parsing de pagination ;
- liste vide ;
- creation ;
- modification ;
- suppression ;
- erreurs `401`, `403`, `404`, `409`, `422`, `500` ;
- erreurs reseau ;
- backend indisponible ;
- payload pagine invalide ;
- payload ressource invalide.

## Gestion des erreurs

### Erreurs HTTP

Les erreurs HTTP sont transformees en erreurs de service puis en messages utilisateur lisibles dans la page.

Cas geres :

- `401` ;
- `403` ;
- `404` ;
- `409` ;
- `422` ;
- `5xx`.

### Erreurs reseau

Cas geres :

- timeout ;
- erreur de connexion ;
- backend indisponible.

### Validations utilisateur

Les validations Desktop evitent les payloads manifestement invalides, sans dupliquer de logique metier Backend.

## Liste des fichiers

### Nouveaux fichiers

- `docs/sprints/sprint-17-desktop-urls.md`
- `desktop/services/reports_service.py`
- `desktop/ui/dialogs/report_dialog.py`
- `tests/desktop/test_reports_service.py`

### Fichiers modifies

- `desktop/ui/reports_page.py`
- `desktop/ui/main_window.py`
- `docs/sprints/sprint-19-desktop-reports.md`

### Fichiers explicitement non modifies

- `backend/`
- `backend/alembic/`
- routes FastAPI ;
- schemas Pydantic ;
- services Backend ;
- repositories Backend ;
- modeles SQLAlchemy ;
- `desktop/core/api_client.py` ;
- `desktop/core/constants.py`.

## Deroulement du Sprint

1. Reconstitution documentaire du Sprint 17 Desktop URLs.
2. Verification des endpoints et schemas Reports existants.
3. Creation de `ReportsService`.
4. Creation de `ReportDialog`.
5. Remplacement du placeholder `ReportsPage` par une page CRUD paginee.
6. Injection de l'`ApiClient` existant depuis `MainWindow`.
7. Ajout des tests du service Reports.
8. Execution des controles qualite.

## Criteres de validation

Le Sprint 19 est valide si :

- la page Reports consomme l'API REST via `ReportsService` ;
- la consultation paginee fonctionne ;
- la recherche est transmise a l'API ;
- la creation fonctionne ;
- la modification fonctionne ;
- la suppression demande confirmation ;
- les erreurs HTTP et reseau sont gerees ;
- les validations Desktop sont presentes ;
- aucun Backend n'est modifie ;
- Ruff passe ;
- Pytest passe.

## Risques

Risques identifies :

- supposer des champs absents de l'API Reports ;
- confondre un rapport CRUD simple avec une generation de rapport ;
- exposer `entity_id` de maniere technique faute d'objet `entity` imbrique ;
- reintroduire par erreur le Sprint 17 URLs au lieu de le documenter ;
- modifier le Backend alors que les endpoints existent deja.

## Hors perimetre

Ne fait pas partie du Sprint 19 :

- modification Backend ;
- modification Alembic ;
- modification des schemas Pydantic ;
- modification des modeles SQLAlchemy ;
- reimplementation du Sprint 17 Desktop URLs ;
- export PDF, CSV, DOCX ou XLSX ;
- generation automatique de rapport ;
- telechargement de rapport ;
- upload de fichiers ;
- graphiques ;
- filtres avances non exposes par l'API ;
- nouvelle dependance ;
- commit ;
- push ;
- Pull Request.
