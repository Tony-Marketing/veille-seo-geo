# API Filtrage

Ce document définit les recommandations de filtrage pour les endpoints de liste de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

Il complète directement `docs/api/AUTHENTICATION.md`, `docs/api/ERROR_HANDLING.md` et `docs/api/PAGINATION.md`. Il sert de référence commune pour les routes FastAPI, les services backend, les repositories SQLAlchemy, les schémas Pydantic v2, le client Desktop PySide6 utilisant `httpx`, le futur frontend React et les futurs endpoints SEO, GEO, contenus, sites, mots-clés, concurrents, rapports et configuration.

Les exemples sont conceptuels. Ils décrivent les conventions recommandées, sans prétendre que les classes, fonctions ou endpoints existent déjà dans le code.

## 1. Objectif du document

L'objectif est de définir un cadre stable pour :

- exposer des filtres cohérents sur les endpoints de liste ;
- valider strictement les paramètres de filtre ;
- appliquer les droits utilisateur avant de retourner les données ;
- construire des requêtes SQLAlchemy sûres ;
- éviter toute injection SQL ;
- conserver une compatibilité avec la pagination et le tri ;
- harmoniser le comportement du Desktop PySide6 et du futur frontend React ;
- préparer les développements SEO, GEO, contenus, sites, concurrents, rapports et configuration.

Cette documentation ne fige pas une implémentation définitive. Les champs filtrables exacts doivent être validés endpoint par endpoint lors de l'implémentation.

## 2. Périmètre du filtrage API

Le filtrage s'applique aux endpoints de liste qui retournent une collection potentiellement volumineuse.

Le périmètre couvre :

- filtres simples par égalité ;
- filtres textuels ;
- filtres par identifiant ;
- filtres par statut ;
- filtres par dates et périodes ;
- filtres booléens ;
- filtres numériques ;
- filtres par liste de valeurs ;
- filtres par relations SQLAlchemy ;
- recherche textuelle simple ;
- validation des paramètres ;
- erreurs standardisées ;
- compatibilité avec pagination et tri.

Hors périmètre détaillé :

- la pagination, déjà documentée dans `docs/api/PAGINATION.md` ;
- le format global des erreurs, déjà documenté dans `docs/api/ERROR_HANDLING.md` ;
- l'authentification et les droits, déjà documentés dans `docs/api/AUTHENTICATION.md` ;
- la recherche avancée plein texte, qui peut être étudiée plus tard.

## 3. Principes généraux

Principes recommandés :

| Principe | Règle recommandée | Objectif |
|---|---|---|
| Liste blanche | Autoriser explicitement les champs filtrables | Éviter les champs arbitraires |
| Validation stricte | Valider les types et formats avec Pydantic v2 | Réponses prévisibles |
| Sécurité SQL | Construire les clauses avec SQLAlchemy | Empêcher l'injection SQL |
| Droits d'abord | Appliquer le périmètre utilisateur avant les résultats | Ne pas exposer de données interdites |
| Cohérence | Réutiliser les erreurs standardisées | API stable pour Desktop et React |
| Performance | Prévoir index et requêtes sélectives | Limiter la charge PostgreSQL |

Le filtrage doit être effectué côté backend. Le Desktop ou le futur React ne doivent pas recevoir une liste complète pour filtrer localement lorsque le volume peut grandir.

## 4. Endpoints concernés par le filtrage

Endpoints typiquement concernés :

| Endpoint conceptuel | Filtres recommandés |
|---|---|
| `GET /api/v1/sites` | `q`, `status`, `is_active` |
| `GET /api/v1/projects` | `q`, `status`, `created_from`, `created_to` |
| `GET /api/v1/keywords` | `q`, `site_id`, `intent`, `status` |
| `GET /api/v1/contents` | `q`, `type`, `category`, `status` |
| `GET /api/v1/competitors` | `q`, `site_id`, `is_active` |
| `GET /api/v1/reports` | `type`, `status`, `created_from`, `created_to` |
| `GET /api/v1/admin/audit-logs` | `user_id`, `source`, `created_from`, `created_to` |
| `GET /api/v1/geo/results` | `provider`, `source`, `created_from`, `created_to` |

Les filtres exacts sont à valider selon les modèles et les besoins fonctionnels de chaque module.

## 5. Endpoints non concernés par le filtrage

Le filtrage n'est généralement pas applicable aux endpoints :

- retournant une ressource unique ;
- créant une ressource ;
- mettant à jour une ressource ;
- supprimant une ressource ;
- de connexion ou déconnexion ;
- de santé système ;
- d'export direct de fichier ;
- retournant une configuration unique.

| Endpoint conceptuel | Filtrage | Raison |
|---|---:|---|
| `GET /api/v1/admin/health` | Non | Réponse unique |
| `POST /api/v1/auth/login` | Non | Authentification |
| `GET /api/v1/sites/{site_id}` | Non | Ressource unique |
| `PUT /api/v1/projects/{project_id}` | Non | Modification ciblée |
| `DELETE /api/v1/reports/{report_id}` | Non | Suppression ciblée |

## 6. Rôle dans l'architecture `Routes -> Services -> Repositories -> Models`

Le filtrage doit respecter la chaîne obligatoire :

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

| Couche | Responsabilité filtrage | À éviter |
|---|---|---|
| Route FastAPI | Recevoir les paramètres et déclencher leur validation | Écrire des clauses SQL |
| Schémas Pydantic | Valider types, formats et contraintes simples | Accéder à la base |
| Service | Appliquer règles métier, droits et compatibilités | Faire du SQL brut |
| Repository | Construire la requête SQLAlchemy avec champs autorisés | Décider des permissions |
| Model | Représenter les tables et relations | Porter la logique de filtre |
| Client Desktop / React | Envoyer les paramètres et afficher les résultats | Accéder directement à PostgreSQL |

## 7. Relation entre filtrage, pagination et tri

Le filtrage, le tri et la pagination doivent être combinés dans un ordre stable :

```text
1. Authentification
2. Autorisation
3. Validation des paramètres
4. Filtres
5. Tri
6. Pagination
7. Réponse standardisée
```

Cet ordre garantit que :

- l'utilisateur ne voit que les données autorisées ;
- le total paginé correspond aux résultats filtrés ;
- le tri s'applique sur le jeu filtré ;
- la pagination ne masque pas des erreurs de filtre.

## 8. Cohérence avec `docs/api/PAGINATION.md`

Les filtres doivent être compatibles avec la structure paginée :

```json
{
  "items": [],
  "meta": {},
  "links": {}
}
```

Les liens de pagination doivent conserver les filtres actifs.

Exemple :

```text
/api/v1/keywords?q=seo&site_id=site_123&page=2&limit=25&sort=created_at:desc
```

Le champ `total_items` doit représenter le nombre de résultats après droits et filtres.

## 9. Cohérence avec `docs/api/ERROR_HANDLING.md`

Les erreurs de filtrage doivent utiliser le format standard :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le filtre demandé est invalide.",
  "details": {
    "parameter": "status"
  },
  "code": "FILTER_INVALID_VALUE",
  "status_code": 400,
  "path": "/api/v1/projects",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Les erreurs ne doivent pas exposer de requête SQL, de nom interne sensible, de stack trace, de token ou de secret.

## 10. Cohérence avec `docs/api/AUTHENTICATION.md`

Les endpoints sensibles doivent être protégés avant l'application des filtres.

Règles recommandées :

- `401` si l'utilisateur n'est pas authentifié ;
- `403` si l'utilisateur est authentifié mais non autorisé ;
- filtrage uniquement dans le périmètre de données autorisé ;
- aucun filtre ne doit permettre de deviner l'existence d'une ressource interdite ;
- les volumes retournés doivent être calculés après application des droits.

## 11. Modèle de filtrage recommandé

Le modèle recommandé utilise des paramètres de requête explicites et documentés :

```text
GET /api/v1/keywords?q=seo&site_id=site_123&intent=informational&status=active
```

Caractéristiques :

- paramètres nommés clairement ;
- types validés ;
- champs filtrables listés côté backend ;
- opérateurs implicites simples ;
- recherche avancée reportée si besoin ;
- compatibilité avec `page`, `limit` et `sort`.

Il n'est pas recommandé d'exposer un mini-langage de requête libre tant que le besoin n'est pas confirmé.

## 12. Filtres simples par égalité

Les filtres par égalité comparent une valeur attendue à un champ autorisé.

Exemples :

| Paramètre | Exemple | Signification |
|---|---|---|
| `status` | `status=active` | Ressources actives |
| `type` | `type=seo` | Ressources de type SEO |
| `provider` | `provider=chatgpt` | Résultats d'un fournisseur |
| `source` | `source=manual` | Source des données |

Ces filtres doivent être mappés explicitement vers des colonnes SQLAlchemy autorisées.

## 13. Filtres par texte partiel

Le filtre textuel partiel recommandé utilise `q`.

Exemple :

```text
GET /api/v1/sites?q=appartner
```

Recommandations :

- limiter les champs recherchés ;
- normaliser les espaces ;
- appliquer une longueur minimale si nécessaire ;
- éviter les recherches trop coûteuses ;
- prévoir des index ou une stratégie de recherche adaptée si le volume augmente.

## 14. Filtres par identifiant

Les filtres par identifiant permettent de restreindre par relation ou parent.

Exemples :

| Paramètre | Exemple | Usage |
|---|---|---|
| `site_id` | `site_id=site_123` | Mots-clés ou contenus d'un site |
| `project_id` | `project_id=project_123` | Rapports ou tâches d'un projet |
| `user_id` | `user_id=user_123` | Journaux d'audit |

Les identifiants doivent être validés au format attendu et soumis aux droits utilisateur.

## 15. Filtres par statut

Le filtre `status` doit utiliser une liste de valeurs autorisées par ressource.

Exemple :

```text
GET /api/v1/reports?status=ready
```

Exemples de statuts possibles, à valider selon les modules :

| Module | Statuts conceptuels |
|---|---|
| Projets | `active`, `archived`, `paused` |
| Rapports | `pending`, `processing`, `ready`, `failed` |
| Contenus | `draft`, `published`, `archived` |
| Sites | `active`, `inactive` |

Un statut inconnu doit produire une erreur standardisée.

## 16. Filtres par dates

Les dates doivent utiliser le format ISO 8601.

Paramètres recommandés :

| Paramètre | Usage |
|---|---|
| `created_from` | Date minimale de création |
| `created_to` | Date maximale de création |
| `updated_from` | Date minimale de mise à jour |
| `updated_to` | Date maximale de mise à jour |

Exemple :

```text
GET /api/v1/reports?created_from=2026-06-01&created_to=2026-06-30
```

Le fuseau horaire doit être traité explicitement lors de l'implémentation.

## 17. Filtres par périodes

Les périodes combinent une date de début et une date de fin.

Règles recommandées :

- `created_from` doit être inférieur ou égal à `created_to` ;
- `updated_from` doit être inférieur ou égal à `updated_to` ;
- une période trop large peut être autorisée ou limitée selon le module ;
- les dates doivent être interprétées de manière cohérente côté serveur.

Une période incohérente doit retourner une erreur `400` ou `422` selon le type de validation retenu.

## 18. Filtres booléens

Les filtres booléens doivent utiliser des valeurs explicites.

Formats recommandés :

| Valeur | Interprétation |
|---|---|
| `true` | Vrai |
| `false` | Faux |

Exemples :

```text
GET /api/v1/sites?is_active=true
GET /api/v1/reports?has_errors=false
```

Les variantes ambiguës comme `yes`, `no`, `1`, `0` sont à éviter sauf besoin de compatibilité explicitement validé.

## 19. Filtres numériques

Les filtres numériques doivent être bornés et validés.

Exemples conceptuels :

| Paramètre | Usage possible |
|---|---|
| `min_position` | Position SEO minimale |
| `max_position` | Position SEO maximale |
| `min_score` | Score d'audit minimal |
| `max_score` | Score d'audit maximal |

Les noms de paramètres numériques doivent rester explicites. Les opérateurs génériques comme `score[gte]` sont à valider avant adoption.

## 20. Filtres par listes de valeurs

Le format recommandé pour les listes simples est une liste séparée par virgules :

```text
GET /api/v1/reports?status=ready,failed
```

Règles recommandées :

- limiter le nombre de valeurs ;
- valider chaque valeur ;
- ignorer les espaces autour des valeurs ou les refuser explicitement ;
- retourner une erreur si une valeur est inconnue ;
- ne jamais injecter directement les valeurs dans du SQL brut.

## 21. Filtres par relations

Les filtres relationnels doivent être explicites :

| Paramètre | Relation conceptuelle |
|---|---|
| `site_id` | Ressource liée à un site |
| `project_id` | Ressource liée à un projet |
| `user_id` | Ressource liée à un utilisateur |
| `provider` | Résultat lié à un fournisseur IA |

Le service doit vérifier que l'utilisateur peut accéder à la relation demandée avant de retourner les résultats.

## 22. Filtres de recherche textuelle simple

Le paramètre `q` est recommandé pour une recherche textuelle simple.

Champs possibles selon module :

| Module | Champs recherchables conceptuels |
|---|---|
| Sites | `name`, `domain` |
| Mots-clés | `keyword`, `intent` |
| Contenus | `title`, `slug` |
| Concurrents | `name`, `domain` |
| Rapports | `name`, `type` |

La recherche textuelle simple doit rester limitée aux champs autorisés.

## 23. Recherche avancée, si prévue plus tard

Une recherche avancée peut être étudiée plus tard si les besoins dépassent `q`.

À prévoir avant activation :

- syntaxe documentée ;
- validation stricte ;
- protection contre requêtes coûteuses ;
- tests de sécurité ;
- index adaptés ;
- compatibilité Desktop et React ;
- stratégie d'erreurs standardisée.

Il n'est pas recommandé d'introduire une recherche avancée sans besoin fonctionnel clair.

## 24. Paramètres recommandés

| Paramètre | Type recommandé | Usage |
|---|---|---|
| `q` | chaîne | Recherche textuelle simple |
| `status` | chaîne ou liste | Statut métier |
| `site_id` | identifiant | Filtre par site |
| `type` | chaîne | Type de ressource |
| `category` | chaîne | Catégorie |
| `intent` | chaîne | Intention SEO ou contenu |
| `source` | chaîne | Source des données |
| `provider` | chaîne | Fournisseur IA |
| `created_from` | date ISO 8601 | Début période création |
| `created_to` | date ISO 8601 | Fin période création |
| `updated_from` | date ISO 8601 | Début période mise à jour |
| `updated_to` | date ISO 8601 | Fin période mise à jour |
| `is_active` | booléen | Ressource active |
| `has_errors` | booléen | Ressource avec erreurs |

Tous les paramètres ne sont pas applicables à tous les endpoints.

## 25. Paramètres déconseillés ou à éviter

Paramètres à éviter :

| Paramètre | Raison |
|---|---|
| `where` | Trop proche d'une clause SQL |
| `sql` | Risque de confusion et d'injection |
| `filter` libre | Trop vague sans schéma strict |
| `column` | Expose une logique interne |
| `field` dynamique | Risque de champ non autorisé |
| `operator` libre | Complexité et surface d'attaque |
| `query` si `q` est déjà utilisé | Incohérence API |

Une API interne ne doit jamais accepter une clause SQL ou une expression de filtre libre directement depuis le client.

## 26. Convention de nommage des paramètres de filtres

Conventions recommandées :

- utiliser `snake_case` ;
- privilégier des noms métier ;
- éviter les noms de colonnes internes ;
- suffixer les bornes temporelles avec `_from` et `_to` ;
- utiliser `_id` pour les relations par identifiant ;
- utiliser `is_` ou `has_` pour les booléens.

Exemples :

| Recommandé | À éviter |
|---|---|
| `created_from` | `createdAtStart` |
| `site_id` | `siteId` |
| `is_active` | `activeFlag` |
| `has_errors` | `errors` |

## 27. Convention de format des dates

Format recommandé :

```text
YYYY-MM-DD
```

ou, si l'heure est nécessaire :

```text
YYYY-MM-DDTHH:MM:SSZ
```

Recommandations :

- documenter le fuseau attendu ;
- privilégier UTC côté API ;
- convertir explicitement les dates locales côté client si nécessaire ;
- valider les dates avec Pydantic v2 ;
- refuser les dates invalides.

## 28. Convention de format des booléens

Formats recommandés :

```text
is_active=true
has_errors=false
```

Les booléens doivent rester lisibles et prévisibles. Les alias comme `yes`, `no`, `on`, `off` sont déconseillés.

## 29. Convention de format des listes

Format recommandé :

```text
status=ready,failed
provider=chatgpt,gemini
```

Règles recommandées :

- séparer par virgule ;
- limiter le nombre d'éléments ;
- valider chaque élément ;
- refuser les éléments vides ;
- conserver l'ordre uniquement si un besoin fonctionnel le justifie.

## 30. Convention de format des recherches textuelles

Recommandations pour `q` :

- longueur minimale recommandée : `2` ou `3` caractères selon module ;
- longueur maximale recommandée : `100` caractères ;
- suppression des espaces inutiles ;
- pas d'interprétation comme expression régulière ;
- pas d'exécution comme SQL ;
- échappement géré par SQLAlchemy et le dialecte PostgreSQL.

Une recherche vide doit être ignorée ou rejetée selon la règle du module, mais le comportement doit rester documenté.

## 31. Champs filtrables autorisés

Chaque endpoint doit définir sa liste blanche de champs filtrables.

Exemple conceptuel :

| Endpoint | Champs filtrables autorisés |
|---|---|
| `GET /api/v1/sites` | `q`, `status`, `is_active` |
| `GET /api/v1/keywords` | `q`, `site_id`, `intent`, `status` |
| `GET /api/v1/reports` | `type`, `status`, `created_from`, `created_to`, `has_errors` |
| `GET /api/v1/geo/results` | `provider`, `source`, `created_from`, `created_to` |

Tout champ non listé doit être ignoré explicitement ou rejeté. Le comportement recommandé est de rejeter les filtres inconnus.

## 32. Champs non filtrables

Champs à ne pas exposer comme filtres :

- mots de passe ou hash ;
- tokens ;
- clés API ;
- secrets ;
- champs internes de sécurité ;
- colonnes techniques non utiles ;
- champs très coûteux à filtrer sans index ;
- champs contenant des données sensibles ;
- noms exacts de contraintes ou index SQL.

Exemples :

| Champ | Raison |
|---|---|
| `password_hash` | Secret de sécurité |
| `api_key_encrypted_value` | Secret chiffré |
| `refresh_token_hash` | Donnée sensible |
| `internal_error_trace` | Détail technique |

## 33. Validation des filtres avec Pydantic v2

Pydantic v2 doit valider :

- types ;
- longueurs ;
- formats de dates ;
- booléens ;
- listes ;
- valeurs d'énumération ;
- cohérence simple entre champs.

Exemple conceptuel :

```python
from datetime import date

from pydantic import BaseModel, Field, model_validator


class ReportFilters(BaseModel):
    q: str | None = Field(default=None, min_length=2, max_length=100)
    status: str | None = None
    created_from: date | None = None
    created_to: date | None = None
    has_errors: bool | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "ReportFilters":
        if self.created_from and self.created_to and self.created_from > self.created_to:
            raise ValueError("created_from must be before or equal to created_to")
        return self
```

Les messages finaux exposés au client doivent rester alignés avec `ERROR_HANDLING.md`.

## 34. Validation métier dans les services

Les services doivent valider les règles dépendantes du contexte métier.

Exemples :

- vérifier que `site_id` appartient au périmètre utilisateur ;
- vérifier que `project_id` est accessible ;
- refuser un filtre réservé aux administrateurs ;
- vérifier la compatibilité entre `type` et `category` ;
- appliquer des valeurs autorisées spécifiques à un module.

La validation métier ne doit pas être placée dans les routes.

## 35. Construction sécurisée des requêtes SQLAlchemy

Les repositories doivent construire les filtres avec SQLAlchemy, jamais par concaténation SQL.

Exemple conceptuel recommandé :

```python
allowed_statuses = {"ready", "failed", "processing"}

if filters.status is not None:
    if filters.status not in allowed_statuses:
        raise InvalidFilterValueError(parameter="status")
    statement = statement.where(Report.status == filters.status)
```

Les colonnes utilisées doivent être sélectionnées depuis une liste blanche définie côté backend.

## 36. Interdiction des champs dynamiques non contrôlés

Il est interdit d'utiliser directement un nom de champ fourni par l'utilisateur pour accéder à une colonne.

À éviter :

```python
column = getattr(Report, user_input)
statement = statement.where(column == value)
```

Approche recommandée :

```python
FILTER_COLUMNS = {
    "status": Report.status,
    "type": Report.type,
    "provider": Report.provider,
}

column = FILTER_COLUMNS.get(filter_name)
if column is None:
    raise UnknownFilterError(parameter=filter_name)
```

Cette liste blanche doit être maintenue par endpoint ou par repository.

## 37. Protection contre l'injection SQL

Règles obligatoires :

- ne jamais concaténer des paramètres utilisateur dans du SQL brut ;
- ne jamais accepter de clause `where` libre ;
- ne jamais exposer un opérateur SQL libre ;
- utiliser les expressions SQLAlchemy ;
- valider les noms de filtres ;
- valider les valeurs ;
- limiter les recherches textuelles coûteuses ;
- tester les entrées malveillantes.

Exemples d'entrées à tester :

```text
q=' OR 1=1 --
status=active;DROP TABLE users
sort=password_hash:asc
```

Ces entrées doivent être rejetées ou traitées comme valeurs inoffensives selon le paramètre concerné.

## 38. Comportement avec filtres inconnus

Comportement recommandé : rejeter les filtres inconnus avec une erreur standardisée.

Exemple :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le filtre demandé n'est pas autorisé.",
  "details": {
    "parameter": "unknown_filter"
  },
  "code": "FILTER_UNKNOWN_PARAMETER",
  "status_code": 400,
  "path": "/api/v1/reports",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Ignorer silencieusement un filtre inconnu est déconseillé, car cela peut masquer une erreur client.

## 39. Comportement avec filtres invalides

Un filtre invalide doit produire :

- `422` si le type ou le format est invalide selon Pydantic ;
- `400` si la valeur est bien formée mais non autorisée métier ;
- un code interne stable ;
- un `request_id` ;
- un message public clair.

Exemples :

| Cas | HTTP | Code |
|---|---:|---|
| `created_from=not-a-date` | `422` | `FILTER_INVALID_DATE` |
| `status=unknown` | `400` | `FILTER_INVALID_VALUE` |
| `is_active=maybe` | `422` | `FILTER_INVALID_BOOLEAN` |
| `provider=unknown_ai` | `400` | `FILTER_INVALID_PROVIDER` |

## 40. Comportement avec filtres incompatibles

Certains filtres peuvent être incompatibles.

Exemples :

- `created_from` supérieur à `created_to` ;
- `updated_from` supérieur à `updated_to` ;
- `type=seo` combiné à une catégorie réservée GEO ;
- `provider=chatgpt` sur un endpoint qui ne gère pas les fournisseurs IA.

Réponse recommandée : `400` avec un code comme `FILTER_INCOMPATIBLE_PARAMETERS`.

## 41. Comportement avec filtres vides

Filtres vides :

| Exemple | Comportement recommandé |
|---|---|
| `q=` | Ignorer ou rejeter selon module, à documenter |
| `status=` | Rejeter avec `FILTER_EMPTY_VALUE` |
| `site_id=` | Rejeter avec `FILTER_EMPTY_VALUE` |
| `provider=,gemini` | Rejeter la liste |

Le comportement recommandé par défaut est de rejeter les filtres vides pour éviter les résultats ambigus.

## 42. Comportement avec aucun résultat

Aucun résultat n'est pas une erreur.

Réponse recommandée :

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
    "self": "/api/v1/reports?status=ready&page=1&limit=25",
    "first": "/api/v1/reports?status=ready&page=1&limit=25",
    "previous": null,
    "next": null,
    "last": null
  }
}
```

Le code HTTP recommandé est `200`.

## 43. Comportement avec pagination

Les filtres doivent être appliqués avant la pagination.

Exemple :

```text
GET /api/v1/reports?status=ready&page=2&limit=25
```

Le backend doit :

- appliquer les droits ;
- appliquer `status=ready` ;
- compter les résultats filtrés ;
- appliquer `offset` et `limit` ;
- retourner les liens avec `status=ready`.

## 44. Comportement avec tri

Le tri doit être appliqué après les filtres et avant la pagination.

Exemple :

```text
GET /api/v1/keywords?site_id=site_123&sort=created_at:desc&page=1&limit=25
```

Les champs de tri doivent aussi être explicitement autorisés, comme documenté dans `PAGINATION.md`.

## 45. Ordre recommandé d'application

Ordre recommandé :

| Étape | Responsable principal |
|---|---|
| Authentification | Dépendance FastAPI / sécurité |
| Autorisation | Service |
| Validation des paramètres | Pydantic v2 / route |
| Filtres | Service puis repository |
| Tri | Repository |
| Pagination | Repository |
| Réponse standardisée | Service / schémas de sortie |

Cet ordre doit être testé sur les endpoints sensibles.

## 46. Codes HTTP recommandés pour le filtrage

| Code | Usage recommandé |
|---:|---|
| `200` | Résultats filtrés retournés, y compris liste vide |
| `400` | Filtre inconnu, valeur non autorisée, incompatibilité métier |
| `401` | Authentification absente ou invalide |
| `403` | Droits insuffisants pour filtrer ou consulter la collection |
| `404` | Ressource relationnelle introuvable si l'exposition est autorisée |
| `422` | Format invalide selon Pydantic v2 |
| `500` | Erreur serveur inattendue |

Les erreurs doivent suivre le format standard de `ERROR_HANDLING.md`.

## 47. Structure recommandée d'une réponse filtrée

Une réponse filtrée doit rester une réponse paginée standard.

Exemple :

```json
{
  "items": [
    {
      "id": "keyword_123",
      "keyword": "audit seo",
      "intent": "commercial",
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
    "self": "/api/v1/keywords?q=audit&status=active&page=1&limit=25",
    "first": "/api/v1/keywords?q=audit&status=active&page=1&limit=25",
    "previous": null,
    "next": null,
    "last": "/api/v1/keywords?q=audit&status=active&page=1&limit=25"
  }
}
```

## 48. Structure recommandée d'une erreur de filtrage

Format recommandé :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le filtre demandé est invalide.",
  "details": {
    "parameter": "provider"
  },
  "code": "FILTER_INVALID_PROVIDER",
  "status_code": 400,
  "path": "/api/v1/geo/results",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Les détails doivent rester sûrs pour la production.

## 49. Filtrage et droits utilisateur

Les droits utilisateur doivent limiter le périmètre avant le retour des résultats.

Exemples :

- un utilisateur ne peut filtrer que les sites auxquels il a accès ;
- un manager peut voir plusieurs projets selon son périmètre ;
- un administrateur peut accéder aux journaux d'audit ;
- un utilisateur standard ne doit pas filtrer les logs d'administration.

Un filtre comme `user_id` peut être réservé aux administrateurs selon le module.

## 50. Filtrage et données sensibles

Le filtrage ne doit jamais exposer indirectement des données sensibles.

À éviter :

- permettre de filtrer par email complet si cela révèle des utilisateurs ;
- indiquer qu'un identifiant interdit existe ;
- filtrer sur des secrets ou tokens ;
- exposer des totaux globaux hors périmètre ;
- distinguer trop précisément une ressource absente d'une ressource interdite.

Le service doit arbitrer entre `403`, `404` et réponse vide selon le contexte sécurité.

## 51. Filtrage et performances PostgreSQL

Recommandations :

- éviter les filtres non indexés sur de grands volumes ;
- limiter les recherches textuelles partielles coûteuses ;
- appliquer les filtres avant la pagination ;
- éviter les jointures inutiles ;
- surveiller les plans de requête des endpoints volumineux ;
- limiter la taille des listes de valeurs ;
- prévoir des index adaptés.

Les endpoints de journaux, mots-clés, URLs et résultats GEO doivent faire l'objet d'une attention particulière.

## 52. Filtrage et index SQL

Index à étudier selon volume :

| Module | Champ | Justification |
|---|---|---|
| Sites | `status` | Filtre fréquent |
| Mots-clés | `site_id` | Relation fréquente |
| Mots-clés | `intent` | Segmentation SEO |
| Rapports | `created_at` | Périodes |
| Rapports | `status` | Suivi de traitement |
| Audit logs | `user_id` | Recherche admin |
| Résultats GEO | `provider` | Comparaison IA |
| Résultats GEO | `created_at` | Historisation |

Toute modification d'index doit passer par une migration Alembic explicite.

## 53. Filtrage et relations SQLAlchemy

Les relations doivent être filtrées de manière explicite.

Exemple conceptuel :

```python
statement = select(Keyword).where(Keyword.site_id == filters.site_id)
```

Pour des relations plus complexes, il est recommandé de :

- limiter les jointures ;
- nommer clairement les relations ;
- éviter les jointures dynamiques depuis des paramètres utilisateur ;
- tester les volumes ;
- vérifier les droits sur la ressource liée.

## 54. Filtrage des sites web

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `q` | Recherche par nom ou domaine |
| `status` | Statut du site |
| `is_active` | Site actif ou non |
| `created_from` | Date de création minimale |
| `created_to` | Date de création maximale |

Les domaines, URLs et données techniques doivent être normalisés avant comparaison si nécessaire.

## 55. Filtrage des mots-clés

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `q` | Recherche dans le mot-clé |
| `site_id` | Mots-clés d'un site |
| `project_id` | Mots-clés d'un projet |
| `intent` | Intention de recherche |
| `status` | Statut de suivi |

Les filtres de position ou volume de recherche peuvent être ajoutés plus tard si le modèle de données le justifie.

## 56. Filtrage des contenus

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `q` | Recherche titre ou slug |
| `site_id` | Contenus d'un site |
| `type` | Type de contenu |
| `category` | Catégorie |
| `status` | Brouillon, publié, archivé |
| `updated_from` | Mise à jour depuis |
| `updated_to` | Mise à jour jusqu'à |

Les filtres doivent éviter d'exposer des contenus non autorisés.

## 57. Filtrage des concurrents

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `q` | Recherche nom ou domaine |
| `site_id` | Concurrents associés à un site |
| `category` | Catégorie concurrentielle |
| `is_active` | Concurrent actif |

Les relations entre sites et concurrents doivent être validées côté service.

## 58. Filtrage des rapports

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `type` | Type de rapport |
| `status` | État de génération |
| `source` | Source du rapport |
| `has_errors` | Rapport en erreur |
| `created_from` | Début période |
| `created_to` | Fin période |

Les rapports peuvent contenir des données sensibles ; les droits doivent être appliqués avant tout comptage.

## 59. Filtrage des configurations

Filtres recommandés pour les configurations listables :

| Paramètre | Usage |
|---|---|
| `q` | Recherche par nom |
| `type` | Type de configuration |
| `source` | Origine |
| `is_active` | Configuration active |
| `updated_from` | Mise à jour depuis |

Les valeurs secrètes ou chiffrées ne doivent jamais être filtrables directement.

## 60. Filtrage des données GEO

Filtres recommandés :

| Paramètre | Usage |
|---|---|
| `provider` | Modèle ou fournisseur IA |
| `source` | Source de collecte |
| `site_id` | Site concerné |
| `project_id` | Projet concerné |
| `created_from` | Début d'historique |
| `created_to` | Fin d'historique |
| `q` | Recherche textuelle simple |

Les données GEO doivent rester extensibles pour de nouveaux fournisseurs.

## 61. Filtrage des résultats IA génératives

Fournisseurs à prévoir :

| Fournisseur | Valeur de filtre recommandée |
|---|---|
| ChatGPT | `chatgpt` |
| Gemini | `gemini` |
| Claude | `claude` |
| Copilot | `copilot` |
| Perplexity | `perplexity` |

Exemple :

```text
GET /api/v1/geo/results?provider=chatgpt&created_from=2026-06-01
```

La liste des fournisseurs autorisés doit être gérée côté backend, idéalement via configuration ou données administrables si le module le prévoit.

## 62. Comportement recommandé côté Desktop PySide6 avec `httpx`

Le Desktop doit :

- construire les paramètres de filtre explicitement ;
- ne pas envoyer de filtres vides ;
- conserver les filtres lors du changement de page ;
- afficher un état vide si aucun résultat ;
- traiter les erreurs standardisées ;
- ne jamais accéder directement à PostgreSQL.

Exemple conceptuel :

```python
import httpx


async def list_reports(api_base_url: str, token: str, filters: dict[str, str]) -> dict:
    async with httpx.AsyncClient(base_url=api_base_url, timeout=10.0) as client:
        response = await client.get(
            "/api/v1/reports",
            params=filters,
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code >= 400:
        return {"error": response.json()}

    return response.json()
```

## 63. Comportement recommandé côté futur frontend React

Le futur frontend React doit :

- centraliser les filtres dans le service API ;
- synchroniser les filtres avec l'URL si l'UX le prévoit ;
- conserver filtres, tri et pagination ensemble ;
- afficher clairement les filtres actifs ;
- réinitialiser `page` à `1` lorsqu'un filtre change ;
- gérer les erreurs `400`, `401`, `403`, `422` et `500`.

Le frontend peut prévalider les champs, mais la validation de référence reste côté backend.

## 64. Exemples conceptuels d'URL avec filtres

Exemples valides :

```text
GET /api/v1/sites?q=appartner&is_active=true
GET /api/v1/keywords?site_id=site_123&intent=commercial&status=active
GET /api/v1/reports?type=seo&status=ready&created_from=2026-06-01&created_to=2026-06-30
GET /api/v1/geo/results?provider=chatgpt,gemini&created_from=2026-06-01
GET /api/v1/competitors?site_id=site_123&is_active=true&page=1&limit=25
```

Exemples invalides :

```text
GET /api/v1/reports?where=status='ready'
GET /api/v1/sites?is_active=maybe
GET /api/v1/geo/results?provider=unknown_ai
GET /api/v1/keywords?created_from=2026-07-01&created_to=2026-06-01
GET /api/v1/reports?password_hash=abc
```

## 65. Exemples conceptuels de réponses JSON filtrées

Exemple de résultats GEO filtrés :

```json
{
  "items": [
    {
      "id": "geo_result_001",
      "provider": "chatgpt",
      "source": "scheduled_scan",
      "brand_visibility_score": 78
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
    "self": "/api/v1/geo/results?provider=chatgpt&page=1&limit=25",
    "first": "/api/v1/geo/results?provider=chatgpt&page=1&limit=25",
    "previous": null,
    "next": null,
    "last": "/api/v1/geo/results?provider=chatgpt&page=1&limit=25"
  }
}
```

## 66. Exemples conceptuels d'erreurs de filtrage

Filtre inconnu :

```json
{
  "error": "BAD_REQUEST",
  "message": "Le filtre demandé n'est pas autorisé.",
  "details": {
    "parameter": "password_hash"
  },
  "code": "FILTER_UNKNOWN_PARAMETER",
  "status_code": 400,
  "path": "/api/v1/reports",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Période invalide :

```json
{
  "error": "BAD_REQUEST",
  "message": "La période de filtrage est invalide.",
  "details": {
    "from": "created_from",
    "to": "created_to"
  },
  "code": "FILTER_INVALID_DATE_RANGE",
  "status_code": 400,
  "path": "/api/v1/reports",
  "method": "GET",
  "request_id": "req_124",
  "timestamp": "2026-06-30T10:01:00Z"
}
```

## 67. Exemples conceptuels de schémas Pydantic

Exemple conceptuel :

```python
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ReportStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ReportFilters(BaseModel):
    q: str | None = Field(default=None, min_length=2, max_length=100)
    status: ReportStatus | None = None
    type: str | None = Field(default=None, max_length=50)
    created_from: date | None = None
    created_to: date | None = None
    has_errors: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "ReportFilters":
        if self.created_from and self.created_to and self.created_from > self.created_to:
            raise ValueError("Invalid date range")
        return self
```

Le schéma valide les paramètres. Il ne décide pas des droits et n'accède pas aux données.

## 68. Exemples conceptuels de service

Exemple conceptuel :

```python
class ReportService:
    def __init__(self, report_repository: ReportRepository) -> None:
        self.report_repository = report_repository

    async def list_reports(
        self,
        current_user: CurrentUser,
        filters: ReportFilters,
        pagination: PaginationParams,
    ) -> PaginatedResponse[ReportResponse]:
        access_scope = current_user.report_scope()
        self._validate_filter_permissions(current_user=current_user, filters=filters)

        result = await self.report_repository.list_reports(
            access_scope=access_scope,
            filters=filters,
            pagination=pagination,
        )

        return build_paginated_response(result=result, pagination=pagination)
```

Le service applique le périmètre utilisateur et les validations métier.

## 69. Exemples conceptuels de repository SQLAlchemy

Exemple conceptuel :

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_reports(
        self,
        access_scope: ReportAccessScope,
        filters: ReportFilters,
        pagination: PaginationParams,
    ) -> PaginatedResult[Report]:
        statement = select(Report).where(Report.project_id.in_(access_scope.project_ids))

        if filters.status is not None:
            statement = statement.where(Report.status == filters.status)

        if filters.created_from is not None:
            statement = statement.where(Report.created_at >= filters.created_from)

        if filters.created_to is not None:
            statement = statement.where(Report.created_at <= filters.created_to)

        if filters.has_errors is not None:
            statement = statement.where(Report.has_errors.is_(filters.has_errors))

        if filters.q is not None:
            statement = statement.where(Report.name.ilike(f"%{filters.q}%"))

        statement = statement.offset(pagination.offset).limit(pagination.limit)
        result = await self.session.execute(statement)
        return PaginatedResult(items=list(result.scalars().all()), total_items=0)
```

Cet exemple reste conceptuel. Le calcul de `total_items` doit être ajouté avec une requête adaptée aux performances.

## 70. Exemples conceptuels de route FastAPI

Exemple conceptuel :

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("", response_model=PaginatedResponse[ReportResponse])
async def list_reports(
    filters: ReportFilters = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: CurrentUser = Depends(require_authenticated_user),
    report_service: ReportService = Depends(get_report_service),
):
    return await report_service.list_reports(
        current_user=current_user,
        filters=filters,
        pagination=pagination,
    )
```

La route lit les paramètres, impose l'authentification et délègue au service.

## 71. Tests à prévoir

Tests recommandés :

| Type de test | Cas à couvrir |
|---|---|
| Schémas Pydantic | Dates, booléens, listes, valeurs invalides |
| Services | Droits utilisateur, filtres réservés, relations accessibles |
| Repositories | Clauses SQLAlchemy, listes de valeurs, dates, booléens |
| Routes FastAPI | `200`, `400`, `401`, `403`, `422` |
| Sécurité | Injection SQL, filtres inconnus, champs sensibles |
| Pagination | `total_items` après filtres et droits |
| Desktop | Construction query string et gestion erreurs |
| React futur | Conservation filtres dans URL et pagination |

Les tests doivent rester dans le périmètre de filtrage et respecter les conventions du projet.

## 72. Critères d'acceptation

Une implémentation de filtrage sera acceptable si :

- les champs filtrables sont explicitement autorisés ;
- les filtres inconnus ou invalides produisent des erreurs standardisées ;
- les droits sont appliqués avant le retour des données ;
- les filtres sont compatibles avec pagination et tri ;
- les requêtes sont construites avec SQLAlchemy sans concaténation SQL brute ;
- les données sensibles ne sont pas filtrables ;
- le Desktop peut consommer les réponses via HTTP REST ;
- le futur React peut réutiliser le même contrat ;
- les tests couvrent validation, sécurité et pagination ;
- les liens paginés conservent les filtres actifs.

## 73. Checklist de conformité

| Point de contrôle | Statut attendu |
|---|---|
| Architecture `Routes -> Services -> Repositories -> Models` respectée | Obligatoire |
| Desktop uniquement via FastAPI REST | Obligatoire |
| Champs filtrables en liste blanche | Obligatoire |
| Validation Pydantic v2 | Obligatoire |
| Validation métier dans les services | Obligatoire |
| Requêtes SQLAlchemy sécurisées | Obligatoire |
| Aucune concaténation SQL brute | Obligatoire |
| Erreurs alignées avec `ERROR_HANDLING.md` | Obligatoire |
| Pagination compatible avec `PAGINATION.md` | Obligatoire |
| Authentification alignée avec `AUTHENTICATION.md` | Obligatoire |
| Données sensibles non filtrables | Obligatoire |
| Tests Pytest prévus | Obligatoire |

## 74. Points à éviter

À éviter strictement :

- accepter un paramètre `where` libre ;
- concaténer des paramètres utilisateur dans du SQL brut ;
- exposer des noms de colonnes sensibles ;
- filtrer sur `password_hash`, tokens ou secrets ;
- appliquer la pagination avant les filtres ;
- calculer `total_items` hors périmètre utilisateur ;
- ignorer silencieusement les filtres inconnus ;
- coder la logique métier dans les routes ;
- laisser le Desktop accéder directement à PostgreSQL ;
- introduire une recherche avancée sans cadrage dédié.

## 75. Liens avec les documents API

| Document | Lien avec le filtrage |
|---|---|
| `docs/api/AUTHENTICATION.md` | Définit l'identité et les droits à appliquer avant filtrage |
| `docs/api/ERROR_HANDLING.md` | Définit le format des erreurs pour filtres invalides |
| `docs/api/PAGINATION.md` | Définit la pagination à appliquer après les filtres |
| `docs/api/API_ADMINISTRATION.md` | Contient des endpoints administratifs qui devront filtrer sans exposer de secrets |

## Matrice de responsabilité

| Responsabilité | Route FastAPI | Schéma Pydantic | Service | Repository | Desktop / React |
|---|---:|---:|---:|---:|---:|
| Recevoir les paramètres | Oui | Non | Non | Non | Envoie |
| Valider types et formats | Déclenche | Oui | Non | Non | Prévalidation possible |
| Valider règles métier | Non | Partiel | Oui | Non | Non |
| Vérifier les droits | Dépendance | Non | Oui | Non | Non |
| Définir les champs autorisés | Non | Partiel | Oui | Oui | Non |
| Construire les clauses SQLAlchemy | Non | Non | Non | Oui | Non |
| Appliquer pagination et tri | Non | Non | Coordonne | Oui | Consomme |
| Formater la réponse | Oui | Oui | Coordonne | Non | Consomme |
| Afficher erreurs | Non | Non | Non | Non | Oui |

## Matrice types de filtres, paramètres et validation

| Type de filtre | Paramètres exemples | Validation principale | Responsabilité applicative |
|---|---|---|---|
| Texte partiel | `q` | Longueur, normalisation | Pydantic puis repository |
| Égalité | `status`, `type` | Valeurs autorisées | Pydantic / service |
| Identifiant | `site_id`, `project_id` | Format et droits | Pydantic / service |
| Date | `created_from`, `created_to` | Format ISO, cohérence | Pydantic / service |
| Booléen | `is_active`, `has_errors` | `true` / `false` | Pydantic |
| Liste | `provider=chatgpt,gemini` | Chaque valeur autorisée | Pydantic / service |
| Relation | `user_id`, `site_id` | Accès à la relation | Service |
| Numérique | `min_score`, `max_score` | Bornes et cohérence | Pydantic / service |

## Diagramme de flux d'une requête filtrée

Flux conceptuel :

```text
Client Desktop / React
        |
        | GET /api/v1/reports?status=ready&created_from=2026-06-01&page=1
        v
Route FastAPI
        |
        | dépendances auth + validation Pydantic
        v
Service métier
        |
        | droits + validation métier + périmètre utilisateur
        v
Repository SQLAlchemy
        |
        | WHERE autorisés + ORDER BY + LIMIT/OFFSET
        v
PostgreSQL
        |
        | résultats filtrés et autorisés
        v
Repository SQLAlchemy
        |
        | PaginatedResult
        v
Service métier
        |
        | réponse paginée standardisée
        v
Route FastAPI
        |
        | JSON items + meta + links
        v
Client Desktop / React
```

Ce flux garantit que les filtres sont validés, sécurisés et appliqués dans le périmètre utilisateur, sans accès direct des clients à PostgreSQL.
