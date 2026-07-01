# Sprint 13 - Securisation des routes metier

## Objectif

Securiser les routes metier FastAPI en imposant une authentification JWT et des permissions serveur explicites.

## Perimetre

- Routes FastAPI metier.
- Factory CRUD.
- Dependances de securite existantes.
- Seed des permissions.
- Tests API.
- Documentation du sprint.

## Hors perimetre

- Desktop.
- Services metier.
- Repositories.
- Modeles SQLAlchemy.
- Schemas Pydantic.
- Migrations Alembic.
- URLs publiques de l'API.
- Pagination.

## Architecture

La securite reste appliquee au niveau des routes FastAPI.

```text
Routes
-> Services
-> Repositories
-> Models
```

La factory CRUD conserve son comportement existant et accepte maintenant des dependances optionnelles par operation.

## Permissions

Convention officielle : `resource.action`.

| Ressource | Lecture | Creation | Modification | Suppression |
|---|---|---|---|---|
| Websites | `website.read` | `website.write` | `website.write` | `website.delete` |
| Entities | `entity.read` | `entity.write` | `entity.write` | `entity.delete` |
| Keywords | `keyword.read` | `keyword.write` | `keyword.write` | `keyword.delete` |
| Competitors | `competitor.read` | `competitor.write` | `competitor.write` | `competitor.delete` |
| URLs | `url.read` | `url.write` | `url.write` | `url.delete` |
| Reports | `report.read` | `report.write` | `report.write` | `report.delete` |
| Project Tasks | `project_task.read` | `project_task.write` | `project_task.write` | `project_task.delete` |

Les routes `Users`, `Roles` et `Permissions` conservent `require_admin`.

## Fichiers modifies

- `backend/app/api/v1/routes/factory.py`
- `backend/app/api/v1/routes/entities.py`
- `backend/app/api/v1/routes/websites.py`
- `backend/app/api/v1/routes/competitors.py`
- `backend/app/api/v1/routes/keywords.py`
- `backend/app/api/v1/routes/urls.py`
- `backend/app/api/v1/routes/reports.py`
- `backend/app/api/v1/routes/project_tasks.py`
- `scripts/seed_admin.py`
- `tests/conftest.py`
- `tests/api/test_websites_routes.py`

## Fichiers crees

- `tests/api/test_business_route_security.py`
- `docs/sprints/sprint-13-security-routes.md`

## Strategie de securite

- Sans JWT : `401`.
- JWT valide sans permission : `403`.
- Permission correcte : comportement fonctionnel inchange.
- Objet inexistant apres autorisation : `404`.
- Superadmin : acces autorise via le bypass existant de `user_has_permission`.

## Tests realises

- Tests des routes Websites existantes avec superadmin.
- Tests 401 sur routes metier sans JWT.
- Tests 403 sur routes metier sans permission.
- Tests CRUD autorises avec permissions explicites.
- Tests CRUD autorises avec superadmin.
- Tests 404 apres autorisation.

## Resultats Ruff

Commande executee avec le runtime Python disponible :

```text
python -m ruff check .
All checks passed!
```

## Resultats Pytest

Commande executee avec le runtime Python disponible :

```text
python -m pytest
113 passed, 2 warnings
```

## Limites connues

- Le Desktop n'est pas modifie dans ce sprint.
- La navigation Desktop ne masque pas encore les actions selon les permissions.
- Les bases deja initialisees devront recevoir les nouvelles permissions via le seed ou une procedure d'administration.
