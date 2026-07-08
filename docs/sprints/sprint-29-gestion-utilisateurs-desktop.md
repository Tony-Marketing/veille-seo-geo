# Sprint 29 — Gestion utilisateurs Desktop

Statut : implémentation Desktop réalisée — aucun backend modifié

## Objectif

Le Sprint 29 ajoute un module Desktop d'administration des utilisateurs, rôles et permissions dans l'application interne Veille SEO-GEO Groupe A.P&Partner.

Le module respecte l'architecture Desktop obligatoire :

```text
UsersPage -> UsersService -> ApiClient -> API REST
```

La page PySide6 gère uniquement l'affichage et les interactions utilisateur. Le service Desktop encapsule les appels REST. `ApiClient` reste le point unique de communication HTTP. Aucun accès direct Desktop à PostgreSQL, SQLAlchemy, aux repositories backend ou aux modèles backend n'a été ajouté.

## Contexte

Le Sprint 29 suit les sprints Desktop précédents afin de stabiliser l'administration applicative avant les travaux futurs de planification, monitoring, alertes et exports consolidés.

L'application possède déjà une authentification au lancement. Les routes REST d'administration utilisateurs, rôles et permissions existaient déjà et sont protégées côté backend par `require_admin`. Le Sprint 29 peut donc être réalisé sans refonte de l'authentification et sans complément backend.

## Endpoints backend utilisés

Endpoints existants consommés par le Desktop :

- `GET /api/v1/users` : liste paginée des utilisateurs avec `page`, `page_size`, `search`, `sort`, `order` ;
- `POST /api/v1/users` : création d'utilisateur ;
- `PUT /api/v1/users/{user_id}` : modification utilisateur, activation/désactivation via `is_active`, modification du mot de passe si `password` est renseigné ;
- `GET /api/v1/roles` : consultation paginée des rôles ;
- `GET /api/v1/permissions` : consultation paginée des permissions.

Les endpoints CRUD `GET /{id}` et `DELETE /{id}` existent aussi côté backend via la factory CRUD, mais ne sont pas utilisés par l'interface Sprint 29.

## Développements réalisés

Le Sprint 29 implémente :

- service Desktop `UsersService` ;
- page Desktop `UsersPage` ;
- formulaire `UserDialog` de création et modification utilisateur ;
- entrée de navigation `Utilisateurs` ;
- lazy loading de `UsersPage` dans `MainWindow` ;
- liste paginée des utilisateurs ;
- recherche utilisateur via le paramètre backend `search` ;
- actualisation manuelle ;
- consultation des rôles ;
- consultation des permissions ;
- création utilisateur ;
- modification utilisateur ;
- activation et désactivation via `PUT /users/{user_id}` ;
- modification du mot de passe via `PUT /users/{user_id}` si le champ est renseigné ;
- gestion des erreurs HTTP ;
- gestion des erreurs réseau ;
- tests Desktop du service avec `httpx.MockTransport`.

## Fichiers créés

- `desktop/services/users_service.py` ;
- `desktop/ui/users_page.py` ;
- `desktop/ui/dialogs/user_dialog.py` ;
- `tests/desktop/test_users_service.py`.

## Fichiers modifiés

- `desktop/core/constants.py` ;
- `desktop/ui/main_window.py` ;
- `tests/desktop/test_main_window_lazy_loading.py` ;
- `docs/sprints/sprint-29-gestion-utilisateurs-desktop.md`.

## Backend

Aucun fichier backend n'a été modifié.

Le backend existant suffit pour cette version Desktop minimale et cohérente :

- les routes `/api/v1/users`, `/api/v1/roles` et `/api/v1/permissions` existent déjà ;
- les listes utilisent le format paginé standard `items`, `total`, `page`, `page_size`, `pages` ;
- les utilisateurs acceptent `role_ids`, `is_active`, `is_superadmin` et `password` ;
- le mot de passe est hashé par le service backend existant ;
- les routes sont protégées par `require_admin`.

## React

Aucun fichier React n'a été modifié.

## Hors périmètre respecté

Le Sprint 29 n'ajoute pas :

- refonte de l'authentification ;
- SSO ;
- OAuth externe ;
- double facteur 2FA ;
- récupération de mot de passe par email ;
- audit avancé ;
- gestion multi-tenant complexe ;
- scheduler ;
- monitoring global ;
- alertes ;
- exports consolidés ;
- nouvelle dépendance ;
- logique métier côté Desktop ;
- accès direct Desktop à PostgreSQL.

## Stratégie de tests

Tests Desktop ajoutés dans `tests/desktop/test_users_service.py` avec `httpx.MockTransport`.

Couverture prévue et implémentée :

- liste utilisateurs avec recherche, pagination et tri ;
- création utilisateur ;
- modification utilisateur ;
- activation/désactivation via update utilisateur ;
- liste des rôles ;
- liste des permissions ;
- mapping des erreurs HTTP ;
- mapping des erreurs réseau ;
- backend indisponible ;
- payload paginé invalide ;
- payload ressource invalide.

Le test de lazy loading `tests/desktop/test_main_window_lazy_loading.py` est mis à jour pour couvrir la nouvelle entrée `Utilisateurs`.

Aucun appel Internet n'est nécessaire pendant les tests.

## Commandes de validation

Commandes à exécuter en fin de Sprint 29 :

```powershell
git status --short
git diff --stat
git diff --check
python -m ruff check .
python -m pytest
```

## Résultats de validation

Résultats obtenus pendant le Sprint 29 :

- `git diff --check` : OK, uniquement des avertissements CRLF Windows non bloquants ;
- `python -m ruff check .` : la commande littérale `python` n'est pas disponible dans le PATH de cette session ;
- Ruff exécuté avec le Python embarqué Codex : `All checks passed!` ;
- `python -m pytest` : la commande littérale `python` n'est pas disponible dans le PATH de cette session ;
- Pytest exécuté avec le Python embarqué Codex : `388 passed, 2 warnings`.

Les deux avertissements Pytest ne sont pas bloquants :

- `StarletteDeprecationWarning` lié à `fastapi.testclient` ;
- `PytestCacheWarning` Windows sur la création de `.pytest_cache`.

## Notes de prudence

Points à conserver pour les évolutions futures :

- ne pas casser l'authentification existante ;
- ne pas exposer d'action sensible sans protection administrateur ;
- ne pas stocker de mot de passe en clair ;
- ne pas introduire de secret ;
- ne pas modifier React ;
- ne pas refondre le backend inutilement ;
- ne pas contourner `ApiClient` côté Desktop ;
- ne pas placer de logique métier dans les pages PySide6.
