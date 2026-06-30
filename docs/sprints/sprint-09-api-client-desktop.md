# Sprint 09 - Connexion du Desktop à l'API FastAPI

## 1. Titre du sprint

**Sprint 09 - Connexion du Desktop à l'API FastAPI**

Ce sprint consolide la connexion technique entre le client Desktop PySide6 et l'API FastAPI.

Il s'inscrit dans la continuité directe du Sprint 08, qui a ajouté le shell Desktop PySide6, la navigation, les pages initiales, le thème sombre, un premier `ApiClient` et un affichage d'état backend.

## 2. Objectif du sprint

L'objectif du Sprint 09 est de consolider l'existant plutôt que de recréer une nouvelle architecture.

Le sprint doit permettre de :

- documenter précisément le périmètre de connexion Desktop/API ;
- tester le client API Desktop existant ;
- tester le healthcheck public backend ;
- durcir légèrement `ApiClient` si les tests révèlent un besoin ;
- préparer une gestion d'erreurs API Desktop plus robuste ;
- conserver une séparation stricte `Desktop -> FastAPI -> PostgreSQL` ;
- éviter tout développement métier complet à ce stade.

## 3. Contexte

Le projet **Veille SEO-GEO Groupe A.P&Partner** repose sur :

| Couche | Technologie |
| --- | --- |
| Backend | Python 3.13 |
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Base de données | PostgreSQL |
| Validation | Pydantic v2 |
| Tests | Pytest |
| Linting | Ruff |
| Desktop | PySide6 + httpx |
| Frontend futur | React |

Le backend doit respecter l'architecture :

```text
Routes -> Services -> Repositories -> Models
```

Le Desktop doit rester un client HTTP REST. Il ne doit jamais accéder directement à PostgreSQL ni importer les modèles SQLAlchemy backend.

## 4. État initial constaté

L'analyse préalable a confirmé :

- branche de travail prévue : `sprint-09` ;
- état Git propre avant création du document ;
- shell Desktop déjà présent ;
- client API Desktop déjà présent ;
- configuration API Desktop déjà présente ;
- healthcheck public backend déjà présent ;
- aucun test Desktop dédié existant ;
- aucun test dédié pour `GET /api/v1/health` ;
- dépendances `httpx` et `PySide6` déjà présentes.

## 5. Éléments déjà disponibles depuis Sprint 08

Le Sprint 08 a mis en place la base Desktop suivante :

| Élément | Fichier | État |
| --- | --- | --- |
| Point d'entrée Desktop | `desktop/main.py` | Existant |
| Création application Qt | `desktop/app.py` | Existant |
| Client API REST | `desktop/core/api_client.py` | Existant |
| Configuration Desktop | `desktop/core/config.py` | Existant |
| Constantes de navigation | `desktop/core/constants.py` | Existant |
| Fenêtre principale | `desktop/ui/main_window.py` | Existant |
| Dashboard | `desktop/ui/dashboard_page.py` | Existant |
| Page Websites | `desktop/ui/websites_page.py` | Existant |
| Sidebar | `desktop/widgets/sidebar.py` | Existant |
| Topbar | `desktop/widgets/topbar.py` | Existant |
| Statusbar | `desktop/widgets/statusbar.py` | Existant |
| Style sombre | `desktop/styles/dark.qss` | Existant |

Le sprint 09 doit donc renforcer et tester cette base, pas la remplacer.

## 6. Problème à résoudre

Le Desktop dispose déjà d'un premier client API, mais la connexion Desktop/API n'est pas encore suffisamment sécurisée par les tests.

Les points à traiter sont :

- absence de tests dédiés pour `ApiClient` ;
- absence de tests dédiés pour le healthcheck public ;
- gestion d'erreurs API encore minimale ;
- absence de couverture des erreurs réseau côté Desktop ;
- absence de vérification automatisée du comportement de `check_health()`.

## 7. Périmètre fonctionnel

Le sprint couvre :

- vérification de disponibilité de l'API depuis le Desktop ;
- affichage d'un état backend lisible dans le shell Desktop ;
- appel du healthcheck public `GET /api/v1/health` ;
- gestion initiale des erreurs API côté Desktop ;
- tests du client API Desktop ;
- tests du healthcheck public backend.

Le sprint ne couvre pas les modules métier complets.

## 8. Périmètre technique

Le périmètre technique recommandé est :

| Type | Élément |
| --- | --- |
| Documentation | `docs/sprints/sprint-09-api-client-desktop.md` |
| Tests Desktop | `tests/desktop/test_api_client.py` |
| Tests API | `tests/api/test_health_routes.py` |
| Desktop | `desktop/core/api_client.py` si nécessaire |
| Configuration | `desktop/core/config.py` optionnel |
| Dashboard | `desktop/ui/dashboard_page.py` optionnel |
| Fixtures | `tests/conftest.py` uniquement si nécessaire |

Toute modification doit rester locale au besoin de connexion Desktop/API.

## 9. Hors périmètre

Sont explicitement hors périmètre :

- login Desktop complet ;
- stockage persistant de token ;
- refresh token ;
- authentification Desktop complète ;
- CRUD métier complet ;
- modules SEO complets ;
- modules GEO complets ;
- modules mots-clés complets ;
- modules concurrents complets ;
- modules rapports complets ;
- accès direct Desktop à PostgreSQL ;
- import des modèles SQLAlchemy backend dans le Desktop ;
- contournement des routes FastAPI ;
- refactor global du shell Desktop ;
- migration Alembic ;
- modification des modèles SQLAlchemy ;
- modification des repositories métier ;
- modification des services métier.

## 10. Architecture cible

L'architecture cible du sprint est :

```text
Desktop PySide6
   |
   v
ApiClient Desktop
   |
   v
httpx
   |
   v
FastAPI
   |
   v
GET /api/v1/health
```

Pour les futurs modules métier, le flux complet restera :

```text
Desktop PySide6 -> httpx -> FastAPI Routes -> Services -> Repositories -> PostgreSQL
```

## 11. Règle fondamentale Desktop -> FastAPI -> PostgreSQL

Règle obligatoire :

```text
Desktop -> FastAPI -> PostgreSQL
```

Le Desktop :

- communique uniquement avec FastAPI via HTTP REST ;
- ne se connecte jamais directement à PostgreSQL ;
- n'importe jamais les modèles SQLAlchemy backend ;
- ne contourne jamais les routes API ;
- ne simule pas les droits backend.

Le backend reste responsable :

- des règles métier ;
- des permissions ;
- de l'accès à la base ;
- des transactions ;
- de la sécurité.

## 12. Fichiers à créer

Fichiers à créer pendant le sprint :

| Fichier | Objectif |
| --- | --- |
| `docs/sprints/sprint-09-api-client-desktop.md` | Documentation du sprint |
| `tests/desktop/test_api_client.py` | Tests du client API Desktop |
| `tests/api/test_health_routes.py` | Tests du healthcheck public backend |

Le présent document correspond au premier fichier de cette liste.

## 13. Fichiers à modifier potentiellement

Fichiers pouvant être modifiés plus tard dans ce sprint, uniquement si nécessaire :

| Fichier | Raison possible |
| --- | --- |
| `desktop/core/api_client.py` | Durcir erreurs, faciliter tests, enrichir healthcheck |
| `desktop/core/config.py` | Rendre l'URL API configurable si validé |
| `desktop/ui/dashboard_page.py` | Améliorer le message d'état API si nécessaire |
| `tests/conftest.py` | Ajuster les imports Desktop uniquement si nécessaire |

Aucune modification n'est prévue sur les couches métier backend.

## 14. Fichiers à ne pas modifier

À ne pas modifier dans ce sprint :

- modèles SQLAlchemy ;
- repositories métier ;
- services métier ;
- migrations Alembic ;
- routes métier non concernées ;
- fichiers de documentation development déjà créés ;
- fichiers de configuration sensibles ;
- `.env` ;
- dépendances, sauf besoin bloquant explicitement validé.

Aucune migration Alembic n'est prévue.

## 15. Détail du client API Desktop attendu

Le client API Desktop attendu doit :

- rester centralisé dans `desktop/core/api_client.py` ;
- utiliser `httpx` ;
- appliquer un timeout ;
- exposer des méthodes HTTP simples ;
- normaliser les erreurs réseau ;
- normaliser les erreurs de statut HTTP ;
- retourner `None` sur `204 No Content` ;
- parser le JSON lorsque la réponse en contient ;
- proposer `check_health()`.

Comportements attendus à tester :

| Cas | Résultat attendu |
| --- | --- |
| `GET` réussi | payload JSON retourné |
| `204 No Content` | `None` retourné |
| erreur HTTP | `ApiClientError` |
| erreur réseau | `ApiClientError` |
| health `{"status": "ok"}` | `True` |
| health indisponible | `False` |

## 16. Détail du healthcheck backend attendu

Le healthcheck public existe déjà :

```text
GET /api/v1/health
```

Réponse attendue :

```json
{
  "status": "ok"
}
```

Ce sprint doit ajouter un test dédié pour garantir que cet endpoint reste disponible pour le Desktop.

Le healthcheck admin existe aussi :

```text
GET /api/v1/admin/health
```

Il est protégé par authentification admin et ne remplace pas le healthcheck public utilisé par le Desktop.

## 17. Détail de la configuration API côté Desktop

La configuration actuelle est :

```python
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
HTTP_TIMEOUT_SECONDS = 5.0
```

Comportement attendu :

- les pages Desktop ne codent pas l'URL API en dur ;
- le client API utilise `API_BASE_URL` ;
- le healthcheck utilise le chemin relatif `/health` ;
- avec l'URL actuelle, `/health` cible bien `http://127.0.0.1:8000/api/v1/health`.

Une configuration par variable d'environnement peut être envisagée plus tard, mais elle n'est pas obligatoire pour le sprint.

## 18. Détail de la gestion d'erreurs API côté Desktop

La gestion initiale attendue doit distinguer :

| Situation | Comportement attendu |
| --- | --- |
| API indisponible | message lisible, pas de crash |
| Timeout | erreur Desktop normalisée |
| Statut HTTP 4xx/5xx | erreur Desktop normalisée |
| Réponse inattendue | message lisible côté UI |
| Healthcheck KO | dashboard indique backend indisponible |

Les erreurs ne doivent jamais exposer :

- token ;
- mot de passe ;
- clé API ;
- secret ;
- stack trace brute à l'utilisateur.

## 19. Détail des tests Desktop attendus

Créer plus tard :

```text
tests/desktop/test_api_client.py
```

Tests recommandés :

- `test_get_returns_json_payload`
- `test_delete_or_no_content_returns_none`
- `test_http_status_error_raises_api_client_error`
- `test_request_error_raises_api_client_error`
- `test_check_health_returns_true_for_ok_status`
- `test_check_health_returns_false_when_api_client_error`
- `test_api_client_builds_urls_from_base_url`

Ces tests doivent mocker `httpx`. Ils ne doivent pas appeler une vraie API.

## 20. Détail des tests backend attendus

Créer plus tard :

```text
tests/api/test_health_routes.py
```

Tests recommandés :

- `test_public_health_route_returns_ok`
- `test_public_health_route_does_not_require_authentication`
- éventuellement `test_admin_health_requires_authentication`
- éventuellement `test_admin_health_requires_admin`

Le test principal doit garantir :

```text
GET /api/v1/health -> 200 {"status": "ok"}
```

## 21. Critères d'acceptation

Le sprint sera acceptable si :

- le document Sprint 09 existe ;
- `ApiClient` est couvert par des tests ;
- `GET /api/v1/health` est couvert par un test ;
- le Desktop continue à utiliser FastAPI via HTTP REST ;
- aucun accès Desktop direct à PostgreSQL n'est introduit ;
- aucun import de modèle SQLAlchemy backend n'est introduit côté Desktop ;
- aucune migration Alembic n'est créée ;
- les tests passent ;
- Ruff ne signale pas d'erreur sur le périmètre ;
- l'application Desktop démarre toujours.

## 22. Commandes de validation

Commandes PowerShell recommandées :

```powershell
git status --short
ruff check desktop tests
pytest tests/desktop tests/api/test_health_routes.py
pytest
git diff --check
```

Si `tests/desktop/` n'existe pas encore au début du sprint, il sera créé uniquement avec les tests du client API.

## 23. Validation manuelle backend + Desktop

Lancer le backend :

```powershell
python -m uvicorn backend.app.main:app --reload
```

Lancer le Desktop :

```powershell
python desktop/main.py
```

Vérifications manuelles :

- le Desktop démarre ;
- le dashboard affiche l'état backend ;
- si le backend est lancé, l'état est connecté ;
- si le backend est arrêté, l'état est indisponible ;
- l'application ne crashe pas si l'API est indisponible.

## 24. Risques identifiés

| Risque | Impact | Réponse recommandée |
| --- | --- | --- |
| Recréer un client API déjà existant | Duplication | Consolider `desktop/core/api_client.py` |
| Refactor global du shell | Régression UI | Limiter les changements |
| Tests Desktop difficiles à importer | Échec Pytest | Ajuster `tests/conftest.py` seulement si nécessaire |
| Erreurs HTTP trop peu détaillées | Diagnostic limité | Améliorer `ApiClientError` si utile |
| Auth Desktop trop ambitieuse | Hors périmètre | Préparer seulement, sans login complet |
| Confusion `/health` vs `/api/v1/health` | Healthcheck KO | Garder `API_BASE_URL` avec `/api/v1` |
| Accès PostgreSQL Desktop | Violation architecture | Interdiction stricte |

## 25. Découpage recommandé de l'implémentation

Étapes courtes recommandées :

1. Créer le document de sprint.
2. Ajouter `tests/api/test_health_routes.py`.
3. Ajouter `tests/desktop/test_api_client.py`.
4. Exécuter les tests ciblés.
5. Ajuster `desktop/core/api_client.py` uniquement si nécessaire.
6. Exécuter Ruff sur `desktop` et `tests`.
7. Exécuter la suite Pytest.
8. Lancer backend + Desktop manuellement.
9. Mettre à jour le compte rendu de sprint si nécessaire.

## 26. Checklist avant commit

- [ ] Branche active : `sprint-09`.
- [ ] Aucun fichier hors périmètre modifié.
- [ ] `docs/sprints/sprint-09-api-client-desktop.md` créé.
- [ ] Tests Desktop du client API ajoutés.
- [ ] Tests backend healthcheck ajoutés.
- [ ] Aucun accès Desktop direct à PostgreSQL.
- [ ] Aucun import de modèles SQLAlchemy backend côté Desktop.
- [ ] Aucune migration Alembic créée.
- [ ] Ruff exécuté.
- [ ] Pytest exécuté.
- [ ] `git diff --check` sans erreur.

## 27. Checklist avant Pull Request

- [ ] La Pull Request cible `main`.
- [ ] Le sprint consolide l'existant du Sprint 08.
- [ ] Le périmètre reste limité à la connexion Desktop/API.
- [ ] Les modules métier complets ne sont pas développés.
- [ ] L'authentification Desktop complète reste hors périmètre.
- [ ] Les tests ciblés passent.
- [ ] La validation manuelle Desktop est documentée.
- [ ] Aucun secret n'est présent.
- [ ] Aucun fichier temporaire n'est commité.

## 28. Résultat attendu en fin de sprint

En fin de sprint :

- le Sprint 09 est documenté ;
- le client API Desktop est testé ;
- le healthcheck public backend est testé ;
- le Desktop continue à afficher l'état API ;
- les erreurs API de base sont gérées proprement ;
- aucune architecture parallèle n'est introduite ;
- aucune migration Alembic n'est créée ;
- aucun module métier complet n'est développé ;
- le projet reste prêt pour les prochaines vues Desktop et le futur frontend React.

## Matrice de responsabilités

| Élément | Desktop PySide6 | ApiClient | FastAPI | Backend métier | Tests |
| --- | --- | --- | --- | --- | --- |
| Afficher l'état API | Oui | Non | Non | Non | Vérifie indirectement |
| Construire l'appel HTTP | Non | Oui | Non | Non | Vérifie |
| Exposer `/api/v1/health` | Non | Non | Oui | Non | Vérifie |
| Accéder à PostgreSQL | Non | Non | Non | Via repositories uniquement | Non |
| Gérer les erreurs réseau | UI lisible | Normalise | Non | Non | Vérifie |
| Protéger endpoints sensibles | Non | Transmet auth future | Oui | Oui | Vérifie |
| Stocker des tokens | Hors périmètre | Préparation future | Non | Non | Non |
| Modules métier complets | Hors périmètre | Hors périmètre | Hors périmètre | Hors périmètre | Hors périmètre |

## Diagramme ASCII du flux healthcheck

```text
DashboardPage
    |
    | refresh_backend_status()
    v
ApiClient.check_health()
    |
    | get("/health")
    v
httpx
    |
    | GET http://127.0.0.1:8000/api/v1/health
    v
FastAPI backend
    |
    | {"status": "ok"}
    v
DashboardPage affiche "Backend : connecté"
```

## Notes de sécurité

Le Sprint 09 ne doit introduire aucun secret.

Interdits :

- token écrit en clair ;
- mot de passe en clair ;
- clé API en clair ;
- fichier `.env` commité ;
- log contenant un secret ;
- URL PostgreSQL dans le Desktop ;
- import SQLAlchemy backend dans le Desktop.

L'authentification Desktop complète est hors périmètre. Si une préparation est nécessaire, elle doit rester limitée au futur support de headers HTTP dans `ApiClient`.
