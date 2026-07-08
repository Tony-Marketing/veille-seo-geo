# Sprint 28 — Bing Webmaster Tools Desktop

## Objectif

Le Sprint 28 a pour objectif d'ajouter dans l'application Desktop interne une interface de consultation et de déclenchement manuel des imports Bing Webmaster Tools.

Ce module Desktop doit s'appuyer exclusivement sur les endpoints REST existants du backend livrés au Sprint 27. Il ne doit pas recréer de logique métier, ne doit pas accéder directement à Bing Webmaster Tools et ne doit pas accéder directement à PostgreSQL.

Objectifs principaux :

- consulter les connexions Bing Webmaster Tools exposées par l'API REST ;
- consulter les sites Bing rattachés aux connexions ;
- afficher les métriques importées ;
- afficher les statistiques de crawl ;
- afficher les sitemaps ;
- afficher l'historique des imports ;
- déclencher un import manuel depuis le Desktop via le backend ;
- gérer filtres, recherche, pagination, actualisation et erreurs ;
- couvrir le service Desktop avec des tests utilisant `httpx.MockTransport`.

Aucune implémentation n'est incluse dans ce document de cadrage.

## Contexte

Le backend Bing Webmaster Tools a été livré au Sprint 27. Ce sprint a ajouté les modèles SQLAlchemy, la migration Alembic, les schémas Pydantic v2, le repository, le service métier, le connecteur Bing injectable, les routes REST FastAPI, l'import manuel idempotent, les endpoints de consultation paginés, le chiffrement des secrets via `encrypt_secret` / `decrypt_secret`, ainsi que les tests backend associés.

Le Sprint 27 a été validé avec Ruff OK, 371 tests Pytest validés, aucun appel Internet pendant les tests, aucun changement Desktop, aucun changement React et le respect de l'architecture backend obligatoire :

```text
Routes -> Services -> Repositories -> Models
```

Le Sprint 28 vient compléter le triptyque Desktop des sources de données SEO/GEO multi-sites :

- Google Search Console ;
- Google Analytics 4 ;
- Bing Webmaster Tools.

Ce sprint concerne uniquement le Desktop PySide6 et la consommation des endpoints REST existants. La logique métier reste côté backend.

## Périmètre fonctionnel prévu

Le périmètre fonctionnel prévisionnel du Sprint 28 inclut :

- service Desktop Bing Webmaster Tools ;
- page PySide6 dédiée ;
- entrée de navigation Desktop ;
- consultation des connexions Bing ;
- consultation des sites Bing ;
- vue métriques ;
- vue crawl stats ;
- vue sitemaps ;
- vue historique des imports ;
- import manuel depuis le Desktop ;
- filtres ;
- recherche ;
- pagination ;
- actualisation ;
- gestion des erreurs HTTP ;
- gestion des erreurs réseau ;
- tests Desktop avec `httpx.MockTransport`.

Le Desktop doit présenter les données fournies par l'API REST sans recalculer les règles métier du module Bing Webmaster Tools.

## Hors périmètre

Le Sprint 28 exclut explicitement :

- aucun nouveau modèle SQLAlchemy ;
- aucune migration Alembic ;
- aucun nouveau repository backend ;
- aucun nouveau service métier backend ;
- aucun connecteur Bing côté Desktop ;
- aucun appel direct à Bing Webmaster Tools depuis le Desktop ;
- aucun accès direct à PostgreSQL depuis le Desktop ;
- aucune modification React ;
- aucun scheduler ;
- aucune synchronisation automatique ;
- aucun centre de monitoring ;
- aucune alerte ;
- aucun export consolidé.

Le Desktop ne doit jamais manipuler de secret Bing ni appeler directement une API externe Bing Webmaster Tools.

## Architecture attendue

L'architecture Desktop obligatoire est la suivante :

```text
BingWebmasterToolsPage -> BingWebmasterToolsService -> ApiClient -> API REST
```

Responsabilités attendues :

- `BingWebmasterToolsPage` gère uniquement l'affichage, les interactions utilisateur et les états visuels ;
- `BingWebmasterToolsService` encapsule les appels API nécessaires au module Bing Webmaster Tools ;
- `ApiClient` reste le point unique de communication HTTP avec l'API FastAPI ;
- l'API REST reste le seul point d'entrée vers les données Bing Webmaster Tools ;
- la logique métier reste côté backend ;
- les erreurs HTTP et réseau sont transformées en messages utilisateur clairs.

Flux attendu :

```text
Utilisateur
    |
    v
BingWebmasterToolsPage
    |
    v
BingWebmasterToolsService
    |
    v
ApiClient
    |
    v
API REST FastAPI
    |
    v
Services backend
    |
    v
Repositories backend
    |
    v
PostgreSQL
```

Le Desktop ne communique jamais directement avec PostgreSQL, SQLAlchemy, Google Search Console, Google Analytics 4 ou Bing Webmaster Tools. Il consomme uniquement les endpoints REST du backend.

## Fichiers probablement concernés

Cette liste est prévisionnelle. L'implémentation réelle devra être précédée d'une vérification du code existant et se limiter aux fichiers strictement nécessaires.

Fichiers à créer pendant l'implémentation future :

- `desktop/services/bing_webmaster_tools_service.py` ;
- `desktop/ui/bing_webmaster_tools_page.py` ;
- `tests/desktop/test_bing_webmaster_tools_service.py` ;
- éventuellement `tests/desktop/test_bing_webmaster_tools_page.py` si pertinent.

Fichiers probablement modifiés pendant l'implémentation future :

- `desktop/core/constants.py` ;
- `desktop/ui/main_window.py` ;
- éventuellement `tests/desktop/test_main_window_lazy_loading.py`.

Aucun de ces fichiers ne doit être créé ou modifié dans cette tâche de cadrage documentaire, en dehors du présent document Sprint 28.

## Endpoints backend à consommer

Les endpoints exacts doivent être vérifiés dans le code livré au Sprint 27 avant toute implémentation Desktop.

Le Sprint 28 doit consommer les familles d'endpoints attendues suivantes, sans inventer d'URL ni de contrat non validé dans le code :

- connexions Bing ;
- sites Bing ;
- métriques ;
- crawl stats ;
- sitemaps ;
- imports ;
- historique des imports.

Le service Desktop devra reprendre les paramètres réellement exposés par l'API REST : pagination, filtres, recherche, identifiants de connexion, identifiants de site, dates et déclenchement d'import manuel selon les contrats backend existants.

## Tests attendus

Les tests attendus pour l'implémentation future incluent :

- tests du service Desktop avec `httpx.MockTransport` ;
- vérification des paramètres envoyés à l'API REST ;
- vérification de la pagination ;
- vérification de la recherche et des filtres ;
- vérification du déclenchement d'import manuel ;
- vérification de la gestion des erreurs HTTP ;
- vérification de la gestion des erreurs réseau ;
- vérification de l'absence d'appel Internet pendant les tests.

Les tests Desktop doivent simuler les réponses REST du backend. Ils ne doivent pas appeler Bing Webmaster Tools, PostgreSQL ou un serveur externe réel.

## Critères d'acceptation

Le Sprint 28 sera considéré comme acceptable si :

- la navigation Desktop permet d'accéder au module Bing Webmaster Tools ;
- la page Bing Webmaster Tools est accessible ;
- les données Bing sont consultables via l'API REST ;
- l'import manuel peut être déclenché depuis le Desktop ;
- les erreurs HTTP et réseau sont affichées proprement ;
- les tests Desktop nécessaires sont ajoutés ;
- Ruff est OK ;
- Pytest est OK ;
- aucun appel Internet n'est effectué pendant les tests ;
- aucun accès direct à PostgreSQL ou Bing Webmaster Tools n'existe depuis le Desktop ;
- l'architecture `Page -> Service -> ApiClient -> API REST` est respectée.

## Commandes de validation prévues

Commandes PowerShell prévues pour valider l'implémentation future :

```powershell
git status --short
git diff --stat
git diff --check
python -m ruff check .
python -m pytest
```

Ces commandes ne sont pas à exécuter pour la présente tâche documentaire, sauf demande explicite.

## Commit prévu

Commandes PowerShell prévues au moment de finaliser l'implémentation future :

```powershell
git add -A
git commit -m "Sprint 28 - Bing Webmaster Tools Desktop"
git push
```

Aucun commit ne doit être créé dans la présente tâche de cadrage documentaire.

## Suite logique après Sprint 28

Le Sprint 29 prévu est :

`Sprint 29 — Planification des synchronisations`

Objectif : automatiser les imports et traitements récurrents pour Google Search Console, Google Analytics 4, Bing Webmaster Tools, crawls, analyses SEO et analyses GEO.
