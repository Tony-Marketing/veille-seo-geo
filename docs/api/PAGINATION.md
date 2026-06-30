# API Pagination

Ce document définit les recommandations de pagination pour les endpoints de liste de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence commune pour les routes FastAPI, les services backend, les repositories SQLAlchemy, les schémas Pydantic v2, le client Desktop PySide6 utilisant `httpx`, le futur frontend React et le futur document `docs/api/FILTERING.md`.

Les exemples ci-dessous sont conceptuels. Ils illustrent les conventions recommandées, sans prétendre que les classes, fonctions ou endpoints existent déjà dans le code.

## 1. Objectif du document

L'objectif est de définir une pagination API stable, prévisible et performante pour :

- limiter la taille des réponses HTTP ;
- éviter les chargements excessifs côté PostgreSQL ;
- fournir une structure de réponse cohérente au Desktop et au futur React ;
- faciliter les tests backend et clients ;
- préparer l'ajout futur de filtres documenté dans `docs/api/FILTERING.md` ;
- respecter l'architecture obligatoire `Routes -> Services -> Repositories -> Models`.

Cette documentation ne fige pas une implémentation définitive. Les valeurs par défaut, limites maximales et champs triables doivent être validés lors de l'implémentation de chaque module.

## 2. Périmètre de la pagination API

La pagination concerne les endpoints qui retournent une collection de ressources.

Exemples de collections concernées :

- utilisateurs ;
- projets ;
- rapports ;
- mots-clés ;
- URLs ;
- concurrents ;
- journaux d'audit ;
- journaux d'erreurs ;
- paramètres listables ;
- fournisseurs IA ;
- modèles IA ;
- résultats SEO ou GEO historisés.

La pagination ne remplace pas le filtrage. Les filtres seront documentés séparément dans `docs/api/FILTERING.md`.

## 3. Principes généraux

Principes recommandés :

| Principe | Règle recommandée | Objectif |
|---|---|---|
| Stabilité | Réponse paginée avec `items`, `meta` et `links` | Même contrat pour Desktop et futur React |
| Sécurité | Respecter authentification et droits avant retour des données | Ne pas exposer de ressources non autorisées |
| Performance | Appliquer pagination au niveau SQLAlchemy/PostgreSQL | Éviter les listes complètes en mémoire |
| Cohérence | Utiliser les erreurs de `ERROR_HANDLING.md` | Paramètres invalides gérés de façon standardisée |
| Extensibilité | Préparer filtres et tris sans casser le contrat | Compatibilité avec les modules futurs |

La pagination doit être appliquée côté backend. Le client Desktop ou React ne doit pas recevoir une liste complète pour paginer localement lorsque la collection peut grandir.

## 4. Endpoints concernés par la pagination

Un endpoint doit être paginé lorsqu'il peut retourner plusieurs éléments ou lorsque le volume peut augmenter.

| Endpoint conceptuel | Pagination recommandée | Justification |
|---|---:|---|
| `GET /api/v1/projects` | Oui | Liste potentiellement évolutive |
| `GET /api/v1/keywords` | Oui | Volume SEO élevé |
| `GET /api/v1/urls` | Oui | Volume technique élevé |
| `GET /api/v1/reports` | Oui | Historique croissant |
| `GET /api/v1/admin/audit-logs` | Oui | Journaux volumineux |
| `GET /api/v1/admin/error-logs` | Oui | Journaux volumineux |
| `GET /api/v1/admin/ai-providers` | Oui, même si petit volume | Contrat API stable |
| `GET /api/v1/admin/ai-models` | Oui | Liste extensible |

Même les petites listes peuvent utiliser le format paginé si elles sont exposées comme collections administrables.

## 5. Endpoints non concernés par la pagination

La pagination n'est pas recommandée pour :

- récupération d'une ressource unique par identifiant ;
- création d'une ressource ;
- mise à jour d'une ressource ;
- suppression d'une ressource ;
- endpoints de santé ;
- endpoints de connexion ou déconnexion ;
- endpoints d'export qui retournent un fichier ou un flux ;
- endpoints de configuration globale retournant un objet unique.

| Endpoint conceptuel | Pagination | Raison |
|---|---:|---|
| `GET /api/v1/admin/health` | Non | Réponse unique |
| `POST /api/v1/auth/login` | Non | Authentification |
| `GET /api/v1/projects/{project_id}` | Non | Ressource unique |
| `DELETE /api/v1/projects/{project_id}` | Non | Action sur une ressource |
| `GET /api/v1/admin/config/export` | Non, sauf export listable séparé | Flux ou objet d'export |

## 6. Rôle dans l'architecture `Routes -> Services -> Repositories -> Models`

La pagination doit respecter la chaîne :

```text
Routes FastAPI
      |
      v
Services métier
      |
      v
Repositories SQLAlchemy
      |
      v
Models SQLAlchemy / PostgreSQL
```

Responsabilités recommandées :

| Couche | Responsabilité pagination | À éviter |
|---|---|---|
| Route FastAPI | Lire et valider les paramètres via Pydantic ou dépendance | Construire des requêtes SQL |
| Service | Appliquer les règles métier et les droits | Charger toutes les lignes en mémoire |
| Repository | Appliquer `limit`, `offset`, tri et comptage SQLAlchemy | Décider des permissions |
| Model | Représenter les tables et index utiles | Porter la logique de pagination |
| Client Desktop / React | Consommer `items`, `meta`, `links` | Accéder directement à PostgreSQL |

## 7. Modèle de pagination recommandé

Le modèle recommandé est une pagination par page et limite :

```text
GET /api/v1/projects?page=1&limit=25&sort=created_at:desc
```

Ce modèle est simple à comprendre pour le Desktop, le futur React et les tests.

Champs principaux :

- `page` : numéro de page, à partir de `1` ;
- `limit` : nombre maximum d'éléments par page ;
- `offset` : position calculée ou explicitement acceptée selon les endpoints ;
- `sort` : tri simple recommandé.

L'usage de curseurs peut être étudié plus tard pour des volumes très importants, mais il n'est pas recommandé comme modèle par défaut tant qu'il n'est pas nécessaire.

## 8. Pagination par page et limite

La pagination par page et limite repose sur la formule :

```text
offset = (page - 1) * limit
```

Exemples :

| `page` | `limit` | `offset` calculé |
|---:|---:|---:|
| `1` | `25` | `0` |
| `2` | `25` | `25` |
| `3` | `50` | `100` |

La valeur `offset` doit être cohérente avec `page` et `limit`. Il est recommandé d'exposer `page` et `limit` comme interface principale, puis de calculer `offset` côté backend.

## 9. Paramètres recommandés

| Paramètre | Type | Obligatoire | Description |
|---|---|---:|---|
| `page` | entier | Non | Numéro de page, à partir de `1` |
| `limit` | entier | Non | Nombre d'éléments par page |
| `offset` | entier | Non | Position de départ, plutôt calculée côté backend |
| `sort` | chaîne | Non | Champ et direction de tri |

Format recommandé pour `sort` :

```text
sort=created_at:desc
sort=name:asc
```

Les champs triables doivent être explicitement autorisés par endpoint.

## 10. Paramètres déconseillés ou à éviter

Paramètres à éviter :

| Paramètre | Raison |
|---|---|
| `per_page` | Redondant avec `limit` |
| `size` | Moins explicite que `limit` |
| `start` | Ambigu par rapport à `offset` |
| `skip` | Terme orienté ORM, moins stable côté API |
| `order_by` | Peut inciter à exposer des noms SQL internes |
| `direction` séparé sans champ | Risque d'incohérence avec `sort` |

Il est recommandé de standardiser sur `page`, `limit`, `offset` et `sort` pour éviter des variantes entre modules.

## 11. Valeurs par défaut recommandées

Valeurs proposées :

| Paramètre | Valeur par défaut recommandée | À valider selon module |
|---|---:|---|
| `page` | `1` | Oui |
| `limit` | `25` | Oui |
| `sort` | `created_at:desc` si disponible | Oui |
| `offset` | Calculé depuis `page` et `limit` | Oui |

Pour des listes de référence peu volumineuses, un `limit` par défaut de `50` peut être étudié. Pour des journaux volumineux, `25` reste recommandé.

## 12. Limites minimales et maximales recommandées

| Paramètre | Minimum recommandé | Maximum recommandé |
|---|---:|---:|
| `page` | `1` | À valider, pas de maximum fixe par défaut |
| `limit` | `1` | `100` |
| `offset` | `0` | À valider selon performance |

Une limite supérieure stricte doit être appliquée côté backend. Une demande comme `limit=10000` ne doit pas déclencher une requête massive.

## 13. Structure standard d'une réponse paginée

Format recommandé :

```json
{
  "items": [],
  "meta": {
    "page": 1,
    "limit": 25,
    "offset": 0,
    "total_items": 0,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  },
  "links": {
    "self": "/api/v1/projects?page=1&limit=25",
    "first": "/api/v1/projects?page=1&limit=25",
    "previous": null,
    "next": null,
    "last": null
  }
}
```

Le champ `items` doit toujours être présent, même lorsque la liste est vide.

## 14. Champs recommandés dans `meta`

| Champ | Type | Description |
|---|---|---|
| `page` | entier | Page courante |
| `limit` | entier | Nombre maximum d'éléments demandés |
| `offset` | entier | Position de départ calculée |
| `total_items` | entier | Nombre total d'éléments accessibles après droits et filtres |
| `total_pages` | entier | Nombre total de pages |
| `has_next` | booléen | Indique si une page suivante existe |
| `has_previous` | booléen | Indique si une page précédente existe |

Le `total_items` doit refléter les ressources accessibles par l'utilisateur et les filtres appliqués, pas le total global de la table.

## 15. Champs recommandés dans `links`

| Champ | Type | Description |
|---|---|---|
| `self` | chaîne | URL de la page courante |
| `first` | chaîne | URL de la première page |
| `previous` | chaîne ou `null` | URL de la page précédente |
| `next` | chaîne ou `null` | URL de la page suivante |
| `last` | chaîne ou `null` | URL de la dernière page |

Les liens doivent conserver les paramètres utiles : `limit`, `sort` et futurs filtres documentés dans `FILTERING.md`.

## 16. Structure recommandée du champ `items`

Le champ `items` contient uniquement les ressources sérialisées par les schémas Pydantic de sortie.

Exemple :

```json
{
  "items": [
    {
      "id": "project_123",
      "name": "Audit SEO Groupe",
      "status": "active"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 25,
    "offset": 0,
    "total_items": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "links": {
    "self": "/api/v1/projects?page=1&limit=25",
    "first": "/api/v1/projects?page=1&limit=25",
    "previous": null,
    "next": null,
    "last": "/api/v1/projects?page=1&limit=25"
  }
}
```

Les objets dans `items` ne doivent pas exposer de champs sensibles non prévus par le schéma de sortie.

## 17. Convention de nommage pour les listes paginées

Nommage recommandé :

| Élément | Convention |
|---|---|
| Conteneur de liste | `PaginatedResponse[T]` ou équivalent |
| Données | `items` |
| Métadonnées | `meta` |
| Liens | `links` |
| Schéma paramètres | `PaginationParams` |
| Schéma meta | `PaginationMeta` |
| Schéma liens | `PaginationLinks` |

Les noms exacts sont à valider lors de l'implémentation selon les conventions existantes du backend.

## 18. Gestion du tri simple

Le tri simple recommandé utilise un seul champ et une direction :

```text
sort=created_at:desc
```

Directions recommandées :

| Direction | Signification |
|---|---|
| `asc` | Croissant |
| `desc` | Décroissant |

Chaque endpoint doit définir une liste blanche de champs triables.

Exemple conceptuel :

| Endpoint | Champs triables recommandés |
|---|---|
| `GET /api/v1/projects` | `name`, `created_at`, `updated_at`, `status` |
| `GET /api/v1/admin/audit-logs` | `created_at`, `event_type`, `user_id` |
| `GET /api/v1/reports` | `created_at`, `name`, `status` |

## 19. Gestion du tri multiple, si prévu plus tard

Le tri multiple peut être étudié plus tard, par exemple :

```text
sort=status:asc,created_at:desc
```

À prévoir avant activation :

- validation stricte de chaque champ ;
- validation stricte de chaque direction ;
- ordre de priorité documenté ;
- tests de stabilité ;
- impact sur les index PostgreSQL ;
- compatibilité Desktop et futur React.

Tant que le besoin n'est pas confirmé, le tri simple est recommandé.

## 20. Relation entre pagination et filtrage

La pagination s'applique après les règles de droits et après les filtres.

Ordre logique recommandé :

```text
1. Authentification
2. Autorisation
3. Filtres
4. Tri
5. Pagination
6. Sérialisation
```

Cela garantit que `total_items` correspond bien aux ressources accessibles et filtrées.

## 21. Comportement attendu avec les filtres futurs

Quand `docs/api/FILTERING.md` sera créé, les liens paginés devront conserver les paramètres de filtre.

Exemple conceptuel :

```text
/api/v1/projects?status=active&page=2&limit=25&sort=created_at:desc
```

Les filtres invalides devront produire des erreurs standardisées alignées avec `docs/api/ERROR_HANDLING.md`.

## 22. Gestion des paramètres invalides

Paramètres invalides courants :

| Cas | HTTP recommandé | Code interne recommandé |
|---|---:|---|
| `page=0` | `422` | `PAGINATION_INVALID_PAGE` |
| `limit=0` | `422` | `PAGINATION_INVALID_LIMIT` |
| `limit=10000` | `422` ou `400` | `PAGINATION_LIMIT_TOO_HIGH` |
| `offset=-1` | `422` | `PAGINATION_INVALID_OFFSET` |
| `sort=unknown:asc` | `400` | `PAGINATION_INVALID_SORT_FIELD` |
| `sort=name:up` | `400` | `PAGINATION_INVALID_SORT_DIRECTION` |

La structure d'erreur doit respecter `docs/api/ERROR_HANDLING.md`.

## 23. Codes HTTP recommandés pour la pagination

| Code | Usage recommandé |
|---:|---|
| `200` | Liste paginée retournée avec succès |
| `400` | Paramètre fonctionnel invalide, par exemple champ de tri non autorisé |
| `401` | Utilisateur non authentifié ou session expirée |
| `403` | Droits insuffisants sur la collection |
| `422` | Paramètre invalide selon Pydantic v2 |
| `500` | Erreur serveur inattendue |

Les erreurs doivent conserver `request_id`, `path`, `method`, `status_code`, `code` et `message` selon le format standard.

## 24. Cohérence avec `docs/api/ERROR_HANDLING.md`

Les erreurs de pagination doivent appliquer les principes suivants :

- ne pas créer un format d'erreur spécifique à la pagination ;
- utiliser des codes internes stables ;
- ne pas exposer de détails SQL ;
- inclure un `request_id` ;
- distinguer validation (`422`) et règle fonctionnelle (`400`) ;
- retourner `500` uniquement pour les erreurs inattendues.

Exemple de code interne recommandé :

```text
PAGINATION_INVALID_LIMIT
```

## 25. Pagination et authentification

Les endpoints sensibles doivent vérifier l'authentification avant de retourner une liste paginée.

Cas recommandés :

| Situation | Réponse |
|---|---|
| Session absente | `401` |
| Session expirée | `401` |
| Jeton invalide | `401` |
| Utilisateur authentifié | Application des droits puis pagination |

La pagination ne doit jamais permettre de contourner une protection d'accès.

## 26. Pagination et droits utilisateur

Les droits doivent être appliqués avant le comptage et avant la récupération paginée.

Exemple :

- un administrateur peut voir `1000` projets ;
- un utilisateur interne peut voir `12` projets ;
- `total_items` doit valoir `12` pour cet utilisateur, pas `1000`.

Cette règle évite d'exposer indirectement le volume de données non autorisées.

## 27. Pagination et performances PostgreSQL

Recommandations :

- appliquer `LIMIT` et `OFFSET` dans la requête SQL ;
- éviter de charger toute la table en mémoire ;
- surveiller le coût des grands offsets ;
- utiliser des index adaptés au tri et aux filtres ;
- limiter la valeur maximale de `limit` ;
- prévoir une pagination par curseur plus tard si certains volumes deviennent très importants.

Pour les journaux volumineux, le tri par date descendante avec index est généralement recommandé.

## 28. Pagination et index SQL

Les champs fréquemment utilisés pour le tri ou les filtres doivent être indexés lorsque cela est justifié.

Exemples d'index à étudier :

| Ressource | Champ | Usage |
|---|---|---|
| Journaux d'audit | `created_at` | Tri chronologique |
| Journaux d'erreurs | `created_at` | Tri chronologique |
| Projets | `status` | Filtre futur |
| Projets | `created_at` | Tri |
| Mots-clés | `project_id` | Filtre par projet |

Toute modification de structure de base doit passer par une migration Alembic explicite.

## 29. Pagination avec SQLAlchemy 2.x

La pagination SQLAlchemy doit rester dans les repositories.

Approche conceptuelle :

```python
statement = (
    select(Project)
    .order_by(Project.created_at.desc())
    .offset(pagination.offset)
    .limit(pagination.limit)
)
```

Le comptage total doit utiliser une requête adaptée, à valider selon les besoins de performance.

## 30. Recommandations repository

Le repository doit :

- recevoir des paramètres déjà validés ;
- appliquer `limit`, `offset` et tri autorisé ;
- retourner les éléments et le total si nécessaire ;
- isoler SQLAlchemy ;
- ne pas vérifier les droits métier ;
- ne pas sérialiser en JSON.

Exemple de retour conceptuel :

```python
PaginatedResult(items=projects, total_items=total_items)
```

## 31. Recommandations service

Le service doit :

- vérifier les droits métier ;
- choisir les restrictions applicables à l'utilisateur ;
- appeler le repository avec des paramètres validés ;
- construire les métadonnées de pagination ;
- lever des exceptions métier si nécessaire ;
- ne pas écrire de SQL direct.

Le service est le bon endroit pour garantir que `total_items` reflète uniquement les ressources accessibles.

## 32. Recommandations route FastAPI

La route FastAPI doit :

- déclarer les paramètres de requête ;
- valider les paramètres via Pydantic ou dépendance ;
- récupérer l'utilisateur courant si l'endpoint est protégé ;
- appeler le service ;
- retourner le schéma de réponse paginée ;
- éviter toute logique métier.

La route ne doit pas calculer les droits utilisateur ni construire des requêtes SQLAlchemy.

## 33. Recommandations schémas Pydantic v2

Schémas recommandés :

| Schéma conceptuel | Rôle |
|---|---|
| `PaginationParams` | Valider `page`, `limit`, `sort` |
| `PaginationMeta` | Décrire les métadonnées |
| `PaginationLinks` | Décrire les liens |
| `PaginatedResponse[T]` | Envelopper `items`, `meta`, `links` |

Les contraintes Pydantic doivent produire des erreurs alignées avec `docs/api/ERROR_HANDLING.md`.

## 34. Gestion des listes vides

Une liste vide doit retourner `200` avec `items: []`.

Exemple :

```json
{
  "items": [],
  "meta": {
    "page": 1,
    "limit": 25,
    "offset": 0,
    "total_items": 0,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  },
  "links": {
    "self": "/api/v1/projects?page=1&limit=25",
    "first": "/api/v1/projects?page=1&limit=25",
    "previous": null,
    "next": null,
    "last": null
  }
}
```

Une liste vide n'est pas une erreur.

## 35. Gestion des pages hors limites

Deux comportements sont possibles :

| Option | Comportement | Recommandation |
|---|---|---|
| Retourner `items: []` | `200` avec page demandée vide | Simple pour les clients |
| Retourner une erreur | `400` ou `404` | Plus strict, à justifier |

Le comportement recommandé par défaut est `200` avec `items: []` si `page` est valide mais au-delà des résultats.

Exemple : `page=999` sur une liste de 2 pages retourne une page vide avec `has_next=false`.

## 36. Gestion des limites trop élevées

Une limite supérieure doit être imposée.

Exemple :

```text
GET /api/v1/projects?limit=10000
```

Réponse recommandée :

- `422` si la contrainte Pydantic rejette la valeur ;
- `400` si la valeur est techniquement valide mais non autorisée par une règle API ;
- code interne `PAGINATION_LIMIT_TOO_HIGH`.

Il n'est pas recommandé de réduire silencieusement `limit` sans l'indiquer, car cela rend le comportement difficile à tester.

## 37. Gestion des tris invalides

Cas invalides :

- champ non autorisé ;
- direction inconnue ;
- format de tri incorrect ;
- tentative d'utiliser un nom de colonne interne non exposé.

Réponse recommandée :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le paramètre de tri est invalide.",
  "details": {
    "parameter": "sort"
  },
  "code": "PAGINATION_INVALID_SORT_FIELD",
  "status_code": 400,
  "path": "/api/v1/projects",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Les champs triables doivent être documentés ou exposés via la documentation API.

## 38. Comportement recommandé côté Desktop PySide6 avec `httpx`

Le Desktop doit :

- envoyer `page`, `limit` et `sort` via query string ;
- lire `items`, `meta` et `links` ;
- désactiver ou masquer les boutons précédent/suivant selon `has_previous` et `has_next` ;
- gérer les erreurs standardisées ;
- ne jamais accéder directement à PostgreSQL ;
- conserver le `request_id` en cas d'erreur pour support.

Exemple de comportement :

| Situation | Comportement Desktop |
|---|---|
| `items` vide sur page 1 | Afficher un état vide |
| `items` vide sur page élevée | Afficher une page vide ou revenir à la dernière page selon UX validée |
| `401` | Demander une reconnexion |
| `403` | Afficher accès refusé |
| `422` | Corriger ou réinitialiser les paramètres |

## 39. Comportement recommandé côté futur frontend React

Le futur frontend React doit :

- utiliser le même contrat `items`, `meta`, `links` ;
- synchroniser les paramètres de pagination avec l'URL si pertinent ;
- gérer les états chargement, vide, erreur et succès ;
- préserver les futurs filtres dans les liens ;
- ne jamais supposer que le total global est visible sans droits ;
- centraliser le traitement des erreurs API.

Les composants React de liste pourront s'appuyer sur `meta.has_next`, `meta.has_previous` et `meta.total_pages`.

## 40. Exemples conceptuels de réponses JSON paginées

Réponse paginée avec résultats :

```json
{
  "items": [
    {
      "id": "report_001",
      "name": "Rapport SEO mensuel",
      "status": "ready"
    },
    {
      "id": "report_002",
      "name": "Rapport GEO citations",
      "status": "processing"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 25,
    "offset": 0,
    "total_items": 2,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "links": {
    "self": "/api/v1/reports?page=1&limit=25&sort=created_at:desc",
    "first": "/api/v1/reports?page=1&limit=25&sort=created_at:desc",
    "previous": null,
    "next": null,
    "last": "/api/v1/reports?page=1&limit=25&sort=created_at:desc"
  }
}
```

## 41. Exemples conceptuels d'erreurs de pagination

Limite invalide :

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Le paramètre de pagination est invalide.",
  "details": {
    "parameter": "limit",
    "max": 100
  },
  "code": "PAGINATION_LIMIT_TOO_HIGH",
  "status_code": 422,
  "path": "/api/v1/projects",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Tri invalide :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le champ de tri demandé n'est pas autorisé.",
  "details": {
    "parameter": "sort"
  },
  "code": "PAGINATION_INVALID_SORT_FIELD",
  "status_code": 400,
  "path": "/api/v1/projects",
  "method": "GET",
  "request_id": "req_124",
  "timestamp": "2026-06-30T10:01:00Z"
}
```

## 42. Exemples conceptuels de paramètres de requête

Exemples valides :

```text
GET /api/v1/projects
GET /api/v1/projects?page=1&limit=25
GET /api/v1/projects?page=2&limit=25&sort=created_at:desc
GET /api/v1/admin/audit-logs?page=1&limit=50&sort=created_at:desc
```

Exemples invalides :

```text
GET /api/v1/projects?page=0
GET /api/v1/projects?limit=0
GET /api/v1/projects?limit=10000
GET /api/v1/projects?sort=password_hash:asc
GET /api/v1/projects?sort=name:up
```

## 43. Exemples conceptuels de schémas Pydantic

Exemple conceptuel compatible Pydantic v2 :

```python
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=25, ge=1, le=100)
    sort: str | None = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    page: int
    limit: int
    offset: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginationLinks(BaseModel):
    self: str
    first: str
    previous: str | None
    next: str | None
    last: str | None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta
    links: PaginationLinks
```

Le schéma valide les entrées et sorties API. Il ne doit pas accéder à la base de données.

## 44. Exemples conceptuels de service

Exemple conceptuel :

```python
class ProjectService:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self.project_repository = project_repository

    async def list_projects(
        self,
        current_user: CurrentUser,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ProjectResponse]:
        access_scope = current_user.project_scope()
        result = await self.project_repository.list_projects(
            access_scope=access_scope,
            pagination=pagination,
        )
        return build_paginated_response(
            items=result.items,
            total_items=result.total_items,
            pagination=pagination,
            base_path="/api/v1/projects",
        )
```

Le service applique les règles métier et les droits, puis délègue l'accès aux données au repository.

## 45. Exemples conceptuels de repository SQLAlchemy

Exemple conceptuel SQLAlchemy 2.x :

```python
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_projects(
        self,
        access_scope: ProjectAccessScope,
        pagination: PaginationParams,
    ) -> PaginatedResult[Project]:
        base_statement = select(Project).where(Project.id.in_(access_scope.project_ids))

        count_statement = select(func.count()).select_from(base_statement.subquery())
        total_items = await self.session.scalar(count_statement)

        items_statement = (
            base_statement
            .order_by(Project.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        result = await self.session.execute(items_statement)

        return PaginatedResult(
            items=list(result.scalars().all()),
            total_items=total_items or 0,
        )
```

Le repository ne décide pas des droits, mais applique le périmètre fourni par le service.

## 46. Exemples conceptuels de route FastAPI

Exemple conceptuel :

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    pagination: PaginationParams = Depends(),
    current_user: CurrentUser = Depends(require_authenticated_user),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.list_projects(
        current_user=current_user,
        pagination=pagination,
    )
```

La route lit les paramètres, impose l'authentification si nécessaire, puis appelle le service.

## 47. Tests à prévoir

Tests recommandés :

| Type de test | Cas à couvrir |
|---|---|
| Schémas Pydantic | `page`, `limit`, `sort`, valeurs invalides |
| Services | Droits appliqués avant `total_items` |
| Repositories | `limit`, `offset`, tri, total SQL |
| Routes FastAPI | Réponse `200`, erreurs `401`, `403`, `422` |
| Erreurs | Format aligné avec `ERROR_HANDLING.md` |
| Desktop | Navigation page suivante/précédente et erreurs |
| Performance | Absence de chargement complet en mémoire |

Les tests doivent rester ciblés sur le périmètre de pagination et ne pas introduire de refactor hors sujet.

## 48. Critères d'acceptation

Une implémentation de pagination sera acceptable si :

- les endpoints de liste retournent `items`, `meta` et `links` ;
- `page` commence à `1` ;
- `limit` possède une borne maximale ;
- les erreurs de paramètres sont standardisées ;
- les droits utilisateur sont appliqués avant le comptage ;
- les repositories appliquent `limit` et `offset` côté SQLAlchemy ;
- le Desktop peut consommer la réponse sans logique spécifique par module ;
- le futur React peut réutiliser le même contrat ;
- les liens conservent les paramètres utiles ;
- les tests couvrent les cas principaux.

## 49. Checklist de conformité

| Point de contrôle | Statut attendu |
|---|---|
| Architecture `Routes -> Services -> Repositories -> Models` respectée | Obligatoire |
| Desktop uniquement via FastAPI REST | Obligatoire |
| Paramètres validés par Pydantic v2 ou dépendance dédiée | Obligatoire |
| `items` toujours présent | Obligatoire |
| `meta` complet | Obligatoire |
| `links` complet ou justifié | Recommandé |
| `limit` borné | Obligatoire |
| Erreurs alignées avec `ERROR_HANDLING.md` | Obligatoire |
| Authentification alignée avec `AUTHENTICATION.md` | Obligatoire |
| Filtres futurs préservés dans les liens | À prévoir |
| Tests Pytest prévus | Obligatoire |

## 50. Points à éviter

À éviter strictement :

- retourner une liste brute sans `meta` pour un endpoint paginé ;
- charger toute une table puis découper en Python ;
- laisser le client choisir une limite illimitée ;
- exposer des noms de colonnes SQL internes dans `sort` ;
- calculer `total_items` avant d'appliquer les droits ;
- faire accéder le Desktop directement à PostgreSQL ;
- coder la logique métier dans les routes FastAPI ;
- créer une pagination différente par module sans justification ;
- créer `docs/api/FILTERING.md` dans le cadre de cette tâche.

## 51. Liens avec les documents API

| Document | Lien avec la pagination |
|---|---|
| `docs/api/AUTHENTICATION.md` | Définit l'authentification à appliquer avant les listes sensibles |
| `docs/api/ERROR_HANDLING.md` | Définit le format des erreurs pour paramètres invalides |
| `docs/api/FILTERING.md` | Définira les filtres à combiner avec `page`, `limit` et `sort` |
| `docs/api/API_ADMINISTRATION.md` | Contient des endpoints admin listables qui devront rester paginés et protégés |

## Matrice de responsabilité

| Responsabilité | Route FastAPI | Service | Repository | Desktop / React |
|---|---:|---:|---:|---:|
| Lire `page` et `limit` | Oui | Non | Non | Envoie |
| Valider la forme des paramètres | Oui | Possible | Non | Prévalidation possible |
| Vérifier les droits métier | Non | Oui | Non | Non |
| Appliquer le périmètre utilisateur | Non | Oui | Oui, sur périmètre reçu | Non |
| Appliquer `limit` et `offset` SQL | Non | Non | Oui | Non |
| Calculer `total_items` autorisé | Non | Coordonne | Oui | Non |
| Construire `meta` et `links` | Possible | Recommandé | Non | Consomme |
| Afficher la navigation | Non | Non | Non | Oui |
| Gérer les erreurs standardisées | Handler | Lève exceptions | Convertit erreurs données | Affiche |

## Diagramme de flux d'une requête paginée

Flux conceptuel :

```text
Client Desktop / React
        |
        | GET /api/v1/projects?page=2&limit=25&sort=created_at:desc
        v
Route FastAPI
        |
        | valide les paramètres et récupère l'utilisateur
        v
Service métier
        |
        | applique droits + règles métier
        v
Repository SQLAlchemy
        |
        | SELECT avec ORDER BY + OFFSET + LIMIT
        v
PostgreSQL
        |
        | lignes + total autorisé
        v
Repository SQLAlchemy
        |
        | résultat paginé
        v
Service métier
        |
        | construit meta + links
        v
Route FastAPI
        |
        | réponse JSON
        v
Client Desktop / React
```

Ce flux rappelle que la pagination est pilotée par l'API et appliquée au niveau des repositories, sans accès direct du Desktop ou du futur React à PostgreSQL.
