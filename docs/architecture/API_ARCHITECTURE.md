# Software API Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle de l'API REST  
Version du document : 1.0  
Statut : Référence technique API  
Périmètre : endpoints FastAPI, contrats JSON, versionnement, pagination, erreurs, sécurité, compatibilité Desktop  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes d'architecture API](#2-principes-darchitecture-api)
3. [Vue d'ensemble de l'architecture API](#3-vue-densemble-de-larchitecture-api)
4. [Versionnement de l'API](#4-versionnement-de-lapi)
5. [Structure des routes](#5-structure-des-routes)
6. [Méthodes HTTP](#6-méthodes-http)
7. [Codes HTTP](#7-codes-http)
8. [Contrats JSON](#8-contrats-json)
9. [Schémas Pydantic et API](#9-schémas-pydantic-et-api)
10. [Pagination standard](#10-pagination-standard)
11. [Filtres](#11-filtres)
12. [Tri](#12-tri)
13. [Recherche](#13-recherche)
14. [Endpoints CRUD standards](#14-endpoints-crud-standards)
15. [Endpoints non-CRUD](#15-endpoints-non-crud)
16. [Authentification API future](#16-authentification-api-future)
17. [Autorisation et permissions](#17-autorisation-et-permissions)
18. [Erreurs API normalisées](#18-erreurs-api-normalisées)
19. [Validation des entrées](#19-validation-des-entrées)
20. [OpenAPI / Swagger](#20-openapi--swagger)
21. [Tags API](#21-tags-api)
22. [Santé et monitoring API](#22-santé-et-monitoring-api)
23. [Import / Export](#23-import--export)
24. [API et Desktop](#24-api-et-desktop)
25. [API et modules existants](#25-api-et-modules-existants)
26. [API et modules futurs](#26-api-et-modules-futurs)
27. [Performance API](#27-performance-api)
28. [Sécurité API](#28-sécurité-api)
29. [Compatibilité et dépréciation](#29-compatibilité-et-dépréciation)
30. [Tests API](#30-tests-api)
31. [Qualité des endpoints](#31-qualité-des-endpoints)
32. [Conventions de nommage](#32-conventions-de-nommage)
33. [Anti-patterns interdits](#33-anti-patterns-interdits)
34. [Pattern officiel pour créer un nouvel endpoint](#34-pattern-officiel-pour-créer-un-nouvel-endpoint)
35. [Checklist avant Pull Request API](#35-checklist-avant-pull-request-api)
36. [Roadmap API](#36-roadmap-api)
37. [Annexes](#37-annexes)

---

## 1. Présentation

### 1.1 Rôle de l'API

L'API REST FastAPI de Veille SEO-GEO Groupe A.P&Partner est le contrat officiel entre les clients et le backend. Elle
expose les fonctionnalités métier du projet sous forme d'endpoints versionnés, documentés, testés et stables.

Les clients actuels et futurs sont :

- le Desktop PySide6 ;
- Swagger / OpenAPI ;
- des clients HTTP internes ;
- des intégrations futures ;
- des comptes de service futurs ;
- des automatisations contrôlées.

L'API ne doit pas être pensée comme une simple façade technique. Elle est le produit contractuel du backend. Chaque
endpoint définit une promesse de compatibilité, de structure JSON, de code HTTP, de sécurité et de comportement.

### 1.2 Place dans l'écosystème global

```text
Desktop PySide6
Swagger / OpenAPI
Clients HTTP futurs
Intégrations futures
        |
        | HTTP REST / JSON
        v
FastAPI API /api/v1
        |
        v
Routes
        |
        v
Services métier
        |
        v
Repositories
        |
        v
PostgreSQL
```

### 1.3 Objectifs techniques

| Objectif | Description | Impact |
|---|---|---|
| Stabilité | Contrats JSON prévisibles | Desktop robuste |
| Versionnement | Préfixe `/api/v1` obligatoire | Évolutions contrôlées |
| Cohérence REST | Méthodes et routes standardisées | API lisible |
| Documentation | OpenAPI utile et maintenue | Développeurs autonomes |
| Pagination | Listes bornées et exploitables | Performance |
| Erreurs normalisées | Codes internes et HTTP cohérents | UI propre |
| Sécurité | Auth/RBAC futurs intégrés | Protection données |
| Testabilité | Endpoints couverts par Pytest | Régressions limitées |

### 1.4 Objectifs de stabilité

Une réponse API utilisée par le Desktop ne doit pas changer silencieusement. Les champs essentiels, codes HTTP, noms
de routes, formes de pagination et formats d'erreur doivent rester stables jusqu'à la version 1.0, sauf versionnement
explicite ou dépréciation documentée.

### 1.5 Objectifs de maintenabilité

L'API doit rester maintenable par :

- conventions de route homogènes ;
- schémas Pydantic spécialisés ;
- routes fines ;
- erreurs partagées ;
- pagination commune ;
- documentation OpenAPI soignée ;
- tests route par route ;
- absence de logique métier dans les routes.

### 1.6 Objectifs de sécurité

L'API sera le point d'application de :

- authentification Bearer future ;
- autorisation RBAC ;
- protection des endpoints administratifs ;
- validation stricte des entrées ;
- rate limiting futur ;
- logs sans secrets ;
- erreurs sans fuite technique ;
- audit des actions sensibles.

### 1.7 Objectifs de compatibilité Desktop

Le Desktop doit pouvoir :

- appeler des endpoints stables ;
- afficher des listes paginées ;
- distinguer validation, conflit, permission, expiration et erreur serveur ;
- rafraîchir les données sans recharger toute l'application ;
- gérer API indisponible ou lente ;
- évoluer sans modification majeure à chaque changement backend.

### 1.8 Contraintes

| Contrainte | Règle |
|---|---|
| Version | Tous les endpoints métier sous `/api/v1` |
| Architecture | Route -> Service -> Repository -> Model |
| Contrats | JSON typé par Pydantic |
| Routes | Pas de logique métier |
| Listes | Pagination standard |
| Erreurs | Format normalisé cible |
| Sécurité | Auth/RBAC intégrables |
| Desktop | Compatibilité ascendante |

### 1.9 Principes directeurs

1. L'API est un contrat, pas une implémentation exposée.
2. Chaque endpoint doit avoir une responsabilité claire.
3. Les routes restent fines et délèguent aux services.
4. Les réponses sont typées, documentées et testées.
5. Les listes sont paginées par défaut.
6. Les erreurs sont structurées et exploitables par le Desktop.
7. La compatibilité ascendante prime sur la facilité court terme.

---

## 2. Principes d'architecture API

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| REST | Interface standard et prévisible | Ressources, méthodes HTTP | Endpoint verbeux incohérent |
| JSON stable | Contrat Desktop/API durable | Schémas Pydantic | Dict libre non typé |
| Versionnement obligatoire | Préparer v2 sans casser v1 | `/api/v1` | Route sans préfixe |
| Routes cohérentes | Lisibilité développeur | pluriel, ids explicites | Mix singulier/pluriel |
| Réponses cohérentes | UI plus simple | response_model | Structures différentes par module |
| Erreurs normalisées | Desktop peut réagir | code/message/request_id | Stack trace exposée |
| Pagination standard | Performance | `items,total,page,page_size,pages` | Liste géante |
| Filtres standardisés | API prévisible | query params documentés | Payload POST pour simple filtre |
| Tri standardisé | Tables Desktop | `sort`, `order` | Tri non documenté |
| OpenAPI de qualité | Contrat lisible | tags, summaries, exemples | Docs automatiques pauvres |
| Compatibilité ascendante | Réduire dette client | ajouter plutôt que casser | Suppression silencieuse champ |
| Routes sans métier | Respect backend archi | appel service | SQLAlchemy en route |
| Appels services uniquement | Testabilité | `service.list()` | route appelle repository |

### 2.2 Cohérence avec BACKEND_ARCHITECTURE.md

La présente spécification API complète `docs/architecture/BACKEND_ARCHITECTURE.md`. Elle précise comment exposer les
cas d'usage backend en HTTP REST sans déplacer les responsabilités métier vers les routes.

```text
API_ARCHITECTURE.md
  |
  +-- nommage endpoints
  +-- méthodes HTTP
  +-- codes HTTP
  +-- contrats JSON
  +-- pagination/filtres/tri

BACKEND_ARCHITECTURE.md
  |
  +-- couches backend
  +-- services
  +-- repositories
  +-- models
  +-- migrations
```

### 2.3 Règle fondamentale

Une route API doit répondre à la question :

```text
Quelle ressource ou action HTTP est exposée ?
```

Elle ne doit pas répondre à :

```text
Comment la règle métier est-elle calculée ?
Comment la base est-elle requêtée ?
Comment les données sont-elles persistées ?
```

---

## 3. Vue d'ensemble de l'architecture API

### 3.1 Diagramme principal

```text
Client Desktop
      |
      | HTTP REST / JSON
      v
FastAPI Router /api/v1
      |
      v
Route
      |
      v
Service
      |
      v
Repository
      |
      v
PostgreSQL
```

### 3.2 Vue logique

```text
API Contract Layer
  |
  +-- Routes
  +-- HTTP methods
  +-- Query parameters
  +-- Request schemas
  +-- Response schemas
  +-- Error schemas

Application Layer
  |
  +-- Services
  +-- Business use cases
  +-- Domain validation

Persistence Boundary
  |
  +-- Repositories
  +-- SQLAlchemy
  +-- PostgreSQL
```

### 3.3 Vue physique

```text
Windows Desktop
  |
  | HTTP
  v
FastAPI process
  |
  v
Uvicorn / ASGI
  |
  v
SQLAlchemy sessions
  |
  v
PostgreSQL server
```

### 3.4 Vue par responsabilités

| Élément | Responsabilité |
|---|---|
| Router `/api/v1` | Préfixe et agrégation routes |
| Route | Endpoint HTTP et schéma de réponse |
| Dependency | DB, pagination, auth future |
| Service | Règle métier et orchestration |
| Repository | Requêtes SQLAlchemy |
| Schema | Contrat JSON |
| Exception handler futur | Format d'erreur uniforme |

### 3.5 Cycle requête/réponse

```text
HTTP Request
    |
    v
Path matching
    |
    v
Query/body validation
    |
    v
Dependency injection
    |
    v
Service call
    |
    v
Repository access
    |
    v
Domain result
    |
    v
Pydantic serialization
    |
    v
HTTP Response
```

### 3.6 Contrat Desktop/FastAPI

```text
Desktop Page
    |
    v
ApiClient
    |
    v
GET /api/v1/resource
    |
    v
FastAPI route
    |
    v
JSON response
    |
    v
Desktop state: data / empty / error / forbidden
```

### 3.7 Diagramme de séquence liste paginée

```text
Desktop          ApiClient          FastAPI Route          Service          Repository
   |                |                     |                   |                  |
   | load table     |                     |                   |                  |
   |--------------->|                     |                   |                  |
   |                | GET /websites       |                   |                  |
   |                |-------------------->|                   |                  |
   |                |                     | validate params   |                  |
   |                |                     | call service      |                  |
   |                |                     |------------------>|                  |
   |                |                     |                   | list paginated   |
   |                |                     |                   |----------------->|
   |                |                     |                   | items,total      |
   |                |                     |                   |<-----------------|
   |                |                     | WebsiteList       |                  |
   |                |<--------------------|                   |                  |
   | render table   |                     |                   |                  |
   |<---------------|                     |                   |                  |
```

---

## 4. Versionnement de l'API

### 4.1 Préfixe officiel

Tous les endpoints métier doivent être exposés sous :

```text
/api/v1
```

Exemples :

```text
GET /api/v1/websites
GET /api/v1/entities
GET /api/v1/admin/health
```

### 4.2 Justification

Le versionnement permet :

- de stabiliser le contrat Desktop ;
- d'ajouter une future `/api/v2` sans casser v1 ;
- de documenter clairement les breaking changes ;
- de maintenir plusieurs clients pendant une transition ;
- de structurer OpenAPI.

### 4.3 Versions futures

```text
/api/v1  -> version stable initiale
/api/v2  -> rupture de contrat future
```

Une nouvelle version est nécessaire quand un changement ne peut pas être rendu compatible.

### 4.4 Tableau de stratégie

| Situation | Compatible v1 | Nécessite v2 | Stratégie recommandée |
|---|---:|---:|---|
| Ajouter champ optionnel | Oui | Non | Ajouter et documenter |
| Ajouter endpoint | Oui | Non | Ajouter sous `/api/v1` |
| Renommer champ existant | Non | Oui | Déprécier ancien, préparer v2 |
| Supprimer champ utilisé | Non | Oui | Dépréciation puis v2 |
| Changer type d'un champ | Non | Oui | Nouveau champ ou v2 |
| Ajouter filtre optionnel | Oui | Non | Documenter OpenAPI |
| Changer format pagination | Non | Oui | Éviter en v1 |
| Rendre auth obligatoire | Dépend | Peut-être | Coordonner avec Desktop |
| Changer code HTTP succès | Risqué | Peut-être | Maintenir si possible |

### 4.5 Dépréciation

Un champ ou endpoint déprécié doit :

- rester disponible pendant une période de transition ;
- être documenté ;
- avoir une alternative ;
- être signalé dans le changelog API ;
- éventuellement utiliser des headers de dépréciation futurs.

### 4.6 Changelog API

Chaque changement de contrat doit être documenté :

- endpoint ajouté ;
- champ ajouté ;
- champ déprécié ;
- erreur ajoutée ;
- permission ajoutée ;
- comportement modifié.

---

## 5. Structure des routes

### 5.1 Routes CRUD standard

```text
GET    /api/v1/websites
POST   /api/v1/websites
GET    /api/v1/websites/{website_id}
PUT    /api/v1/websites/{website_id}
PATCH  /api/v1/websites/{website_id}
DELETE /api/v1/websites/{website_id}
```

### 5.2 Conventions

| Élément | Convention | Exemple |
|---|---|---|
| Ressource | Pluriel | `/websites` |
| Path parameter | `<resource>_id` | `{website_id}` |
| Sous-ressource | Ressource enfant | `/websites/{website_id}/urls` |
| Action longue | Nom métier clair | `/reports/{report_id}/download` |
| Import | Sous-route action | `/configuration/import` |
| Export | Sous-route action | `/configuration/export` |
| Administration | Préfixe `/admin` | `/admin/settings` |
| Health | Route dédiée | `/health` |

### 5.3 Pluriel

Les noms de ressources doivent être au pluriel :

```text
/websites
/entities
/keywords
/competitors
/reports
/prompts
```

### 5.4 Kebab-case ou snake_case

Dans les chemins d'URL, privilégier le kebab-case pour les ressources composées si nécessaire :

```text
/api-keys
/ai-providers
/system-parameters
```

Les champs JSON et query parameters utilisent `snake_case`.

### 5.5 Sous-ressources

Utiliser une sous-ressource quand la relation est naturelle :

```text
GET /api/v1/entities/{entity_id}/websites
GET /api/v1/websites/{website_id}/urls
GET /api/v1/reports/{report_id}/exports
```

Ne pas créer de sous-ressource trop profonde.

### 5.6 Routes d'action

Une route d'action est acceptable si l'opération n'est pas un CRUD simple :

```text
POST /api/v1/crawler/jobs
POST /api/v1/reports/{report_id}/generate
POST /api/v1/prompts/{prompt_id}/test
```

Règle : préférer une ressource de job quand l'action est longue.

---

## 6. Méthodes HTTP

### 6.1 Tableau complet

| Méthode | Usage | Idempotence | Payload | Réponse | Code standard | Exemple projet |
|---|---|---:|---|---|---:|---|
| GET | Lire liste ou détail | Oui | Non | Objet ou liste | 200 | `GET /websites` |
| POST | Créer ou déclencher action | Non | Oui | Objet créé ou job | 201/202 | `POST /reports` |
| PUT | Remplacer/mettre à jour | Oui si même payload | Oui | Objet modifié | 200 | `PUT /websites/{id}` |
| PATCH | Mise à jour partielle | Souvent oui | Oui partiel | Objet modifié | 200 | `PATCH /keywords/{id}` |
| DELETE | Supprimer | Oui côté résultat | Non | Vide | 204 | `DELETE /websites/{id}` |
| OPTIONS | Capacités HTTP | Oui | Non | Headers | 204/200 | CORS futur |
| HEAD | Métadonnées | Oui | Non | Headers seuls | 200 | Vérification fichier futur |

### 6.2 GET

GET ne modifie jamais l'état serveur. Il sert à :

- lister ;
- lire un détail ;
- télécharger via route dédiée si nécessaire ;
- consulter santé et configuration non sensible.

### 6.3 POST

POST sert à :

- créer une ressource ;
- lancer un job ;
- importer ;
- exécuter une analyse IA ;
- demander une génération de rapport.

### 6.4 PUT vs PATCH

| Méthode | Usage recommandé |
|---|---|
| PUT | Mise à jour complète ou convention existante du projet |
| PATCH | Mise à jour partielle future quand le contrat le distingue clairement |

### 6.5 DELETE

DELETE doit retourner `204 No Content` si la suppression réussit. Pour les suppressions sensibles, le service doit
appliquer les règles métier et l'audit futur.

---

## 7. Codes HTTP

### 7.1 Tableau des codes

| Code | Signification | Usage projet | Exemple | Message utilisateur |
|---:|---|---|---|---|
| 200 | Succès | Lecture, mise à jour | website lu | Données chargées |
| 201 | Créé | Création | site créé | Élément créé |
| 202 | Accepté | Job long futur | crawl lancé | Traitement lancé |
| 204 | Pas de contenu | Suppression | site supprimé | Élément supprimé |
| 400 | Requête invalide métier | Paramètre incohérent | période invalide | Requête incorrecte |
| 401 | Non authentifié | Token absent/expiré futur | access expiré | Reconnexion requise |
| 403 | Interdit | Permission manquante | admin requis | Accès refusé |
| 404 | Introuvable | Ressource absente | site inconnu | Ressource introuvable |
| 409 | Conflit | Doublon, état incompatible | URL déjà utilisée | Conflit de données |
| 422 | Validation | Pydantic | URL trop courte | Champs invalides |
| 429 | Trop de requêtes | Rate limit futur | login répété | Trop de tentatives |
| 500 | Erreur interne | Exception non prévue | erreur serveur | Erreur technique |
| 503 | Indisponible | DB/API externe down | PostgreSQL down | Service indisponible |

### 7.2 Exemple 404

```json
{
  "error": {
    "code": "WEBSITE_NOT_FOUND",
    "message": "Le site demandé est introuvable.",
    "details": null,
    "request_id": "req_01"
  }
}
```

### 7.3 Exemple 409

```json
{
  "error": {
    "code": "WEBSITE_URL_ALREADY_EXISTS",
    "message": "Un site utilise déjà cette URL.",
    "details": {
      "field": "url"
    },
    "request_id": "req_02"
  }
}
```

### 7.4 Exemple 422

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Certains champs sont invalides.",
    "details": [
      {
        "field": "url",
        "message": "L'URL doit contenir au moins 8 caractères."
      }
    ],
    "request_id": "req_03"
  }
}
```

---

## 8. Contrats JSON

### 8.1 Règles générales

| Sujet | Convention |
|---|---|
| Encodage | UTF-8 |
| Noms de champs | snake_case |
| Dates | ISO 8601 |
| Booléens | true/false |
| Identifiants | int ou uuid selon modèle |
| Valeur absente | `null` seulement si autorisé |
| Listes | tableau JSON |
| Objets imbriqués | utilisés avec prudence |

### 8.2 Création

```json
{
  "entity_id": 1,
  "name": "Europ-Arm",
  "url": "https://www.europ-arm.com",
  "cms": "WordPress",
  "is_active": true
}
```

### 8.3 Modification

```json
{
  "name": "Europ-Arm officiel",
  "cms": "WordPress",
  "is_active": true
}
```

### 8.4 Lecture

```json
{
  "id": 1,
  "entity_id": 10,
  "name": "Europ-Arm",
  "url": "https://www.europ-arm.com",
  "cms": "WordPress",
  "is_active": true,
  "created_at": "2026-06-29T09:42:00Z",
  "updated_at": "2026-06-29T09:42:00Z"
}
```

### 8.5 Liste

```json
{
  "items": [
    {
      "id": 1,
      "entity_id": 10,
      "name": "Europ-Arm",
      "url": "https://www.europ-arm.com",
      "cms": "WordPress",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 8.6 Erreur

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Vous ne disposez pas de la permission nécessaire.",
    "details": {
      "permission": "websites:update"
    },
    "request_id": "req_04"
  }
}
```

### 8.7 Compatibilité JSON

| Changement | Compatible | Règle |
|---|---:|---|
| Ajouter champ optionnel | Oui | Documenter |
| Ajouter valeur enum | Risqué | Vérifier clients |
| Supprimer champ | Non | Déprécier |
| Renommer champ | Non | Nouvelle version |
| Changer type | Non | Nouvelle version |
| Rendre nullable | Risqué | Tester Desktop |

---

## 9. Schémas Pydantic et API

### 9.1 Lien avec BACKEND_ARCHITECTURE.md

Les schémas Pydantic sont le contrat API. Ils sont documentés en détail dans `BACKEND_ARCHITECTURE.md`; ici, ils sont
décrits du point de vue exposition HTTP.

### 9.2 Tableau de nommage

| Type de schéma | Convention | Exemple |
|---|---|---|
| Création | `<Resource>Create` | `WebsiteCreate` |
| Mise à jour | `<Resource>Update` | `WebsiteUpdate` |
| Lecture | `<Resource>Read` | `WebsiteRead` |
| Liste paginée | `<Resource>List` ou `<Resource>ListResponse` | `WebsiteList` |
| Erreur | `ErrorResponse` futur | `ErrorResponse` |
| Action | `<Action>Request` | `ReportGenerateRequest` |

### 9.3 Champs dépréciés futurs

Si un champ doit être remplacé :

1. ajouter le nouveau champ ;
2. conserver l'ancien ;
3. documenter la dépréciation ;
4. ajouter avertissement changelog ;
5. supprimer seulement en `/api/v2`.

### 9.4 Validation et sérialisation

| Étape | Responsable |
|---|---|
| Type entrant | Pydantic |
| Format URL/email/date | Pydantic |
| Règle métier | Service |
| Champs exposés | Response schema |
| Pagination | Schema générique |

---

## 10. Pagination standard

### 10.1 Format officiel

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 10.2 Champs

| Champ | Description |
|---|---|
| `items` | Éléments de la page courante |
| `total` | Nombre total d'éléments correspondant aux filtres |
| `page` | Page courante, commence à 1 |
| `page_size` | Nombre maximal d'éléments par page |
| `pages` | Nombre total de pages |

### 10.3 Paramètres

| Paramètre | Défaut | Limite |
|---|---:|---:|
| `page` | 1 | minimum 1 |
| `page_size` | 20 | maximum 100 |
| `search` ou `q` | null | longueur bornée future |
| `sort` | null | whitelist |
| `order` | asc | `asc` ou `desc` |

### 10.4 Erreurs

| Cas | Code |
|---|---:|
| `page < 1` | 422 |
| `page_size > max` | 422 |
| `order` invalide | 422 |
| `sort` non autorisé | 400 ou 422 selon implémentation |

### 10.5 Exemple Websites

```text
GET /api/v1/websites?page=1&page_size=20
```

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 10.6 Compatibilité Desktop

Le Desktop doit pouvoir consommer systématiquement :

- `items` pour remplir les tables ;
- `total` pour afficher le nombre total ;
- `page` et `pages` pour la navigation ;
- `page_size` pour le sélecteur de taille.

---

## 11. Filtres

### 11.1 Principes

Les filtres sont transmis en query parameters pour les listes. Ils doivent être simples, documentés et validés.

### 11.2 Exemples

```text
GET /api/v1/websites?is_active=true
GET /api/v1/keywords?intent=transactional
GET /api/v1/reports?created_after=2026-01-01
```

### 11.3 Types de filtres

| Type | Exemple | Règle |
|---|---|---|
| Booléen | `is_active=true` | true/false |
| Texte | `cms=WordPress` | valeur exacte ou validée |
| Date | `created_after=2026-01-01` | ISO 8601 |
| Relation | `entity_id=1` | id existant selon service |
| Enum | `intent=transactional` | valeurs autorisées |
| Statut | `status=ready` | enum documentée |

### 11.4 Filtres recommandés par module

| Module | Filtres recommandés |
|---|---|
| Websites | `is_active`, `entity_id`, `cms` |
| Entities | `is_active`, `market`, `owner_id` futur |
| Keywords | `entity_id`, `website_id`, `intent`, `priority`, `tag` |
| Competitors | `entity_id`, `market`, `is_active` |
| Reports | `type`, `status`, `created_after`, `created_before` |
| SEO | `website_id`, `severity`, `category`, `date` |
| GEO | `entity_id`, `model`, `prompt_id`, `date` |
| IA | `provider_id`, `model_id`, `status` |
| Crawler | `website_id`, `status`, `started_after` |
| Logs | `level`, `module`, `created_after` |

### 11.5 Filtres complexes

Si les filtres deviennent trop complexes pour une URL lisible, créer un endpoint de recherche dédié documenté, sans
remplacer les filtres simples.

---

## 12. Tri

### 12.1 Paramètres

Deux styles sont acceptables, mais le projet doit rester cohérent par endpoint :

```text
GET /api/v1/websites?sort=name&order=asc
GET /api/v1/keywords?sort=-created_at
```

Le style `sort` + `order` est actuellement le plus explicite.

### 12.2 Champs autorisés

Chaque endpoint doit définir une whitelist :

| Module | Champs de tri recommandés |
|---|---|
| Websites | `name`, `url`, `created_at`, `is_active` |
| Entities | `name`, `created_at`, `is_active` |
| Keywords | `keyword`, `position`, `volume`, `created_at` |
| Reports | `created_at`, `status`, `type` |
| Logs | `created_at`, `level`, `module` |

### 12.3 Erreurs

Un champ de tri invalide ne doit pas être ignoré silencieusement. Réponse recommandée :

```json
{
  "error": {
    "code": "INVALID_SORT_FIELD",
    "message": "Le champ de tri demandé n'est pas autorisé.",
    "details": {
      "field": "unknown"
    },
    "request_id": "req_05"
  }
}
```

### 12.4 Tri multiple futur

Le tri multiple peut être introduit plus tard :

```text
GET /api/v1/keywords?sort=priority,-created_at
```

Il doit être documenté avant usage.

---

## 13. Recherche

### 13.1 Paramètre officiel

Le paramètre recommandé pour la recherche texte est :

```text
q
```

Exemples :

```text
GET /api/v1/websites?q=armurerie
GET /api/v1/competitors?q=riffaut
```

Le projet contient aussi une notion `search` côté pagination existante. Tant qu'elle existe, elle doit être supportée
ou migrée avec prudence. Une convergence vers `q` peut être documentée avant la v1.

### 13.2 Recherche simple

Recherche simple :

- nom ;
- URL ;
- libellé ;
- description courte ;
- champs explicitement autorisés.

### 13.3 Recherche avancée future

La recherche avancée pourra inclure :

- full-text PostgreSQL ;
- opérateurs ;
- pondération ;
- recherche globale multi-modules ;
- sauvegarde de filtres.

### 13.4 Performance

La recherche doit :

- être paginée ;
- utiliser des index si volumétrie ;
- limiter la longueur de requête ;
- éviter `ilike` non maîtrisé sur très grosses tables sans stratégie.

---

## 14. Endpoints CRUD standards

### 14.1 Matrice CRUD

| Opération | Méthode | Route | Payload | Réponse | Erreurs attendues |
|---|---|---|---|---|---|
| List | GET | `/resources` | Non | Liste paginée | 400, 422 |
| Detail | GET | `/resources/{id}` | Non | ResourceRead | 404 |
| Create | POST | `/resources` | CreateSchema | ResourceRead | 400, 409, 422 |
| Replace/Update | PUT | `/resources/{id}` | UpdateSchema | ResourceRead | 404, 409, 422 |
| Partial update | PATCH | `/resources/{id}` | PartialSchema | ResourceRead | 404, 409, 422 |
| Delete | DELETE | `/resources/{id}` | Non | 204 | 404, 409 |

### 14.2 Tests attendus

Chaque ressource CRUD importante doit tester :

- création réussie ;
- lecture détail ;
- liste paginée ;
- recherche/filtre si disponible ;
- mise à jour ;
- suppression ;
- ressource inconnue ;
- conflit métier ;
- validation payload.

### 14.3 Exemple conceptuel Websites

```text
GET    /api/v1/websites
POST   /api/v1/websites
GET    /api/v1/websites/{website_id}
PUT    /api/v1/websites/{website_id}
DELETE /api/v1/websites/{website_id}
```

---

## 15. Endpoints non-CRUD

### 15.1 Quand créer une route d'action

Créer une route d'action si l'opération :

- lance un job ;
- importe ou exporte ;
- génère un rapport ;
- déclenche un crawl ;
- teste un prompt ;
- synchronise un connecteur ;
- télécharge un artefact.

### 15.2 Exemples

```text
POST /api/v1/configuration/import
GET  /api/v1/configuration/export
POST /api/v1/crawler/jobs
GET  /api/v1/reports/{report_id}/download
POST /api/v1/prompts/{prompt_id}/test
POST /api/v1/ai/models/{model_id}/test
```

### 15.3 Jobs longs

Les opérations longues ne doivent pas bloquer une requête HTTP pendant plusieurs minutes.

Pattern recommandé :

```text
POST /api/v1/crawler/jobs
        |
        v
202 Accepted + job_id
        |
        v
GET /api/v1/crawler/jobs/{job_id}
```

### 15.4 Réponse job

```json
{
  "id": 123,
  "type": "crawler",
  "status": "queued",
  "created_at": "2026-06-29T09:42:00Z"
}
```

---

## 16. Authentification API future

### 16.1 Référence

L'architecture détaillée d'authentification est définie dans `docs/architecture/AUTHENTICATION.md`.

### 16.2 Header officiel

```http
Authorization: Bearer <access_token>
```

### 16.3 Codes

| Cas | Code |
|---|---:|
| Token absent | 401 |
| Token expiré | 401 |
| Token invalide | 401 |
| Compte désactivé | 403 |
| Permission insuffisante | 403 |

### 16.4 Intégration route

Les routes protégées devront utiliser des dépendances centralisées :

```text
current_user = Depends(get_current_user)
permission = Depends(require_permission("websites:read"))
```

### 16.5 Refresh token

Le refresh token appartient aux endpoints d'authentification. Les endpoints métier ne doivent pas gérer directement
le refresh.

---

## 17. Autorisation et permissions

### 17.1 Types d'endpoints

| Type | Description |
|---|---|
| Public | Health minimal, login futur |
| Authentifié | Modules métier |
| Admin | Administration |
| Système | Santé détaillée, jobs internes |
| API key futur | Intégrations techniques |

### 17.2 Matrice permissions

| Endpoint | Auth requise | Permission | Rôle minimum | Notes |
|---|---:|---|---|---|
| `GET /websites` | Oui futur | `websites:read` | Consultation | Liste sites |
| `POST /websites` | Oui futur | `websites:create` | SEO/Marketing | Création |
| `PUT /websites/{id}` | Oui futur | `websites:update` | SEO/Marketing | Modification |
| `DELETE /websites/{id}` | Oui futur | `websites:delete` | Admin | Action sensible |
| `GET /entities` | Oui futur | `entities:read` | Consultation | Liste entités |
| `GET /keywords` | Oui futur | `keywords:read` | Consultation | Table SEO |
| `POST /keywords` | Oui futur | `keywords:create` | SEO | Ajout mot-clé |
| `GET /competitors` | Oui futur | `competitors:read` | Consultation | Concurrents |
| `GET /reports` | Oui futur | `reports:read` | Consultation | Rapports |
| `POST /reports` | Oui futur | `reports:create` | Marketing/SEO | Génération |
| `GET /seo/*` | Oui futur | `seo:read` | SEO | Audit |
| `GET /geo/*` | Oui futur | `geo:read` | Marketing/SEO | Visibilité IA |
| `POST /crawler/jobs` | Oui futur | `crawler:execute` | SEO/Admin | Job long |
| `GET /admin/users` | Oui futur | `users:read` | Admin | Administration |
| `POST /admin/roles` | Oui futur | `roles:create` | Super Admin | Critique |
| `GET /admin/logs` | Oui futur | `logs:read` | Admin | Sensible |

### 17.3 Contrôle route/service

- La route vérifie l'authentification et la permission générale.
- Le service vérifie les règles métier contextuelles.
- Le repository ne décide jamais des permissions.

---

## 18. Erreurs API normalisées

### 18.1 Format officiel cible

```json
{
  "error": {
    "code": "WEBSITE_NOT_FOUND",
    "message": "Le site demandé est introuvable.",
    "details": null,
    "request_id": "req_..."
  }
}
```

### 18.2 Champs

| Champ | Rôle |
|---|---|
| `code` | Code stable exploitable par Desktop |
| `message` | Message utilisateur ou développeur contrôlé |
| `details` | Détails structurés non sensibles |
| `request_id` | Corrélation logs/support |

### 18.3 Catalogue

| Code interne | HTTP | Description |
|---|---:|---|
| `VALIDATION_ERROR` | 422 | Payload ou query invalide |
| `BAD_REQUEST` | 400 | Requête incohérente |
| `NOT_AUTHENTICATED` | 401 | Auth future absente |
| `TOKEN_EXPIRED` | 401 | Token expiré |
| `PERMISSION_DENIED` | 403 | Permission absente |
| `RESOURCE_NOT_FOUND` | 404 | Ressource générique absente |
| `WEBSITE_NOT_FOUND` | 404 | Site absent |
| `WEBSITE_URL_ALREADY_EXISTS` | 409 | Doublon URL |
| `INVALID_SORT_FIELD` | 400 | Tri non autorisé |
| `RATE_LIMITED` | 429 | Trop de requêtes |
| `INTERNAL_ERROR` | 500 | Erreur non prévue |
| `SERVICE_UNAVAILABLE` | 503 | Dépendance indisponible |

### 18.4 Erreurs de validation

Les erreurs Pydantic peuvent être adaptées au format cible via un exception handler futur.

---

## 19. Validation des entrées

### 19.1 Niveaux

| Niveau | Responsable | Exemple |
|---|---|---|
| Type | Pydantic | `page: int` |
| Format | Pydantic | URL, email |
| Bornes | Pydantic/Query | `page_size <= 100` |
| Métier | Service | URL unique |
| Persistence | PostgreSQL | unique constraint |

### 19.2 Validations par type

| Type de champ | Validation |
|---|---|
| URL | protocole, longueur, format |
| Email | format email |
| Date | ISO 8601, cohérence période |
| Booléen | true/false |
| Enum | valeurs autorisées |
| Texte | min/max, trim futur |
| Identifiant | entier positif ou UUID |
| Liste | taille maximale future |

### 19.3 400 vs 422

| Code | Usage |
|---|---|
| 422 | Structure ou type invalide |
| 400 | Requête syntaxiquement valide mais incohérente |

---

## 20. OpenAPI / Swagger

### 20.1 Rôle

OpenAPI est la documentation vivante de l'API. Elle doit être utile au Desktop, aux développeurs backend et aux futurs
clients HTTP.

### 20.2 Exigences

| Élément | Règle |
|---|---|
| `summary` | Court et clair |
| `description` | Explique le comportement |
| `tags` | Module officiel |
| `response_model` | Obligatoire sauf réponse vide |
| Status code | Déclaré |
| Query params | Typés et décrits |
| Payload | Schema Pydantic |
| Exemples futurs | Ajouter pour endpoints complexes |

### 20.3 Checklist OpenAPI

| Contrôle | OK |
|---|---|
| Tag correct | |
| Summary clair | |
| Description utile | |
| Response model défini | |
| Codes HTTP cohérents | |
| Query params décrits | |
| Payload nommé | |
| Pas de champ secret exposé | |

---

## 21. Tags API

### 21.1 Tags officiels

| Tag | Module | Description | Public cible |
|---|---|---|---|
| Administration | Admin | Santé, paramètres, fournisseurs, logs | Admin |
| Users | Utilisateurs | Comptes utilisateurs | Admin |
| Roles | Rôles | Rôles RBAC | Admin |
| Permissions | Permissions | Droits atomiques | Super Admin |
| Configuration | Configuration | Import/export, settings | Admin |
| Websites | Sites web | Sites suivis | Marketing/SEO |
| Entities | Entités | Marques du groupe | Marketing |
| Keywords | Mots-clés | Suivi SEO | SEO |
| Competitors | Concurrents | Veille concurrentielle | Marketing/SEO |
| Reports | Rapports | Génération et lecture | Tous rôles autorisés |
| SEO | SEO | Audits et recommandations | SEO |
| GEO | GEO | Visibilité IA générative | Marketing/SEO |
| Crawler | Crawler | Jobs d'exploration | SEO/Admin |
| IA | IA | Providers, modèles, exécutions | Admin/SEO |
| Prompts | Prompts | Prompts GEO/IA | Content/SEO |
| Logs | Logs | Journaux techniques | Admin |
| Health | Santé | Disponibilité API | Système/Desktop |

---

## 22. Santé et monitoring API

### 22.1 Endpoints cibles

```text
GET /api/v1/health
GET /api/v1/health/db
GET /api/v1/version
```

### 22.2 Santé API

`GET /api/v1/health` doit rester léger :

```json
{
  "status": "ok"
}
```

### 22.3 Santé DB future

```json
{
  "status": "ok",
  "database": "ok",
  "latency_ms": 12
}
```

### 22.4 Version

```json
{
  "app_name": "Veille SEO-GEO Groupe A.P&Partner",
  "api_version": "v1",
  "backend_version": "0.1.0"
}
```

### 22.5 Usage Desktop

Le Desktop utilise la santé pour :

- afficher Backend connecté/indisponible ;
- décider si un refresh est possible ;
- afficher une erreur propre ;
- diagnostiquer environnement local.

---

## 23. Import / Export

### 23.1 Configuration

Endpoints existants ou cibles :

```text
GET  /api/v1/admin/config/export
POST /api/v1/admin/config/import
```

### 23.2 Principes

| Sujet | Règle |
|---|---|
| Sécurité | Admin requis |
| Format | JSON structuré |
| Idempotence | Import doit éviter doublons |
| Audit futur | Obligatoire |
| Secrets | Ne jamais exporter en clair |
| Erreurs | Détail par section |

### 23.3 Exemple résultat import

```json
{
  "status": "partial_success",
  "created": 12,
  "updated": 4,
  "errors": [
    {
      "section": "ai_providers",
      "message": "Fournisseur déjà existant."
    }
  ]
}
```

### 23.4 Exports volumineux

Les exports volumineux futurs doivent passer par un job :

```text
POST /api/v1/reports/exports
GET  /api/v1/reports/exports/{export_id}
GET  /api/v1/reports/exports/{export_id}/download
```

---

## 24. API et Desktop

### 24.1 Contrat spécifique Desktop

Le Desktop dépend de :

- URLs versionnées ;
- réponses JSON stables ;
- pagination standard ;
- erreurs normalisées ;
- health check rapide ;
- codes HTTP cohérents.

### 24.2 Diagramme

```text
Desktop Page
    |
    v
ApiClient
    |
    v
GET /api/v1/resource
    |
    v
Paginated JSON
    |
    v
UI Table
```

### 24.3 États UI liés à l'API

| Réponse API | État Desktop |
|---|---|
| 200 + items | Table remplie |
| 200 + items vide | Empty state |
| 401 futur | Reconnexion |
| 403 futur | Accès refusé |
| 404 | Message introuvable |
| 409 | Message conflit |
| 422 | Erreur formulaire |
| 500 | Erreur serveur |
| timeout | API indisponible |

### 24.4 Temps de réponse

| Type endpoint | Objectif |
|---|---:|
| Health | < 500 ms local |
| Liste standard | < 1 s local |
| Détail | < 1 s local |
| Création simple | < 1 s local |
| Job long | 202 rapide |

---

## 25. API et modules existants

### 25.1 Synthèse

| Module | Endpoints existants ou attendus | Responsabilité | Pagination | Permissions futures |
|---|---|---|---:|---|
| Administration | `/admin/*` | Settings, providers, logs, health | Oui selon liste | Admin |
| Users | `/users` | Comptes | Oui futur | Users |
| Roles | `/roles` | Rôles | Oui | Roles |
| Permissions | `/permissions` | Permissions | Oui | Permissions |
| Configuration | `/admin/config/export`, `/admin/config/import` | Config | Non/Action | Admin |
| Websites | `/websites` | Sites | Oui | Websites |
| Entities | `/entities` | Entités | Oui | Entities |

### 25.2 Websites

Contrat principal :

```text
GET /api/v1/websites
```

Réponse paginée avec `WebsiteRead`.

### 25.3 Administration

Les endpoints admin doivent être protégés dès que l'authentification est active. Les données sensibles comme clés API
ne doivent jamais être exposées en clair.

---

## 26. API et modules futurs

### 26.1 Matrice modules futurs

| Module | Endpoint racine | CRUD | Pagination | Filtres | Permissions | Priorité |
|---|---|---:|---:|---:|---|---|
| Keywords | `/keywords` | Oui | Oui | Oui | `keywords:*` | Haute |
| Competitors | `/competitors` | Oui | Oui | Oui | `competitors:*` | Haute |
| URLs | `/urls` | Oui | Oui | Oui | `urls:*` | Haute |
| Reports | `/reports` | Oui | Oui | Oui | `reports:*` | Haute |
| SEO | `/seo` | Partiel | Oui | Oui | `seo:*` | Haute |
| GEO | `/geo` | Partiel | Oui | Oui | `geo:*` | Haute |
| Crawler | `/crawler` | Jobs | Oui | Oui | `crawler:*` | Moyenne |
| Prompts | `/prompts` | Oui | Oui | Oui | `prompts:*` | Haute |
| IA | `/ai` | Oui | Oui | Oui | `ai:*` | Moyenne |
| Logs | `/admin/logs` | Lecture | Oui | Oui | `logs:*` | Moyenne |
| API Keys | `/admin/api-keys` | Oui | Oui | Oui | `api_keys:*` | Haute |
| Configuration avancée | `/admin/settings` | Oui | Oui | Oui | `configuration:*` | Moyenne |

---

## 27. Performance API

### 27.1 Règles

- Toute liste potentiellement volumineuse est paginée.
- `page_size` maximum est borné.
- Les filtres doivent être appliqués en SQL.
- Les champs de tri doivent être indexés si usage fréquent.
- Éviter les réponses énormes.
- Éviter les requêtes N+1.
- Les jobs longs retournent 202.
- Le cache futur doit respecter les permissions.

### 27.2 Checklist performance

| Contrôle | OK |
|---|---|
| Liste paginée | |
| `page_size` borné | |
| Filtres SQL | |
| Tri whitelisté | |
| Index identifié | |
| Relations chargées efficacement | |
| Pas de job long synchrone | |
| Réponse JSON raisonnable | |

### 27.3 Streaming futur

Le streaming peut être envisagé pour :

- téléchargements de rapports ;
- exports volumineux ;
- logs en temps réel futurs.

---

## 28. Sécurité API

### 28.1 Principes

| Sujet | Règle |
|---|---|
| Validation | Tout payload validé |
| Authentification | Bearer future |
| Autorisation | RBAC future |
| Secrets | Jamais exposés |
| CORS | Strict si clients web |
| Rate limiting | Login et endpoints sensibles |
| Audit | Actions admin |
| Erreurs | Pas de stack trace |
| Logs | Pas de données sensibles |

### 28.2 Protection admin

Tout endpoint `/admin/*` doit être considéré sensible. Même en phase initiale, sa conception doit prévoir :

- auth obligatoire future ;
- permissions dédiées ;
- audit ;
- réponses sans secrets.

### 28.3 Liens documentaires

- `AUTHENTICATION.md` : architecture complète auth/RBAC.
- futur `SECURITY.md` : durcissement global, headers, déploiement.

---

## 29. Compatibilité et dépréciation

### 29.1 Stratégie

| Situation | Stratégie |
|---|---|
| Nouveau besoin Desktop | Ajouter champ ou endpoint compatible |
| Champ à renommer | Ajouter nouveau champ, déprécier ancien |
| Champ à supprimer | Reporter à v2 |
| Endpoint remplacé | Garder ancien pendant transition |
| Code erreur ajouté | Documenter et tester |
| Permission ajoutée | Coordonner Desktop |

### 29.2 Headers futurs

Headers de dépréciation possibles :

```text
Deprecation: true
Sunset: 2027-01-01
Link: <https://docs internes>; rel="deprecation"
```

### 29.3 Règle d'or

Ne jamais casser silencieusement le Desktop.

---

## 30. Tests API

### 30.1 Types de tests

| Test | Objectif |
|---|---|
| Route succès | Vérifier code et payload |
| Validation | Vérifier 422 |
| Erreur métier | Vérifier 404/409 |
| Pagination | Vérifier structure |
| Filtres | Vérifier résultat |
| Tri | Vérifier ordre |
| Permissions futures | Vérifier 401/403 |
| OpenAPI futur | Vérifier schémas exposés |

### 30.2 Commandes

```powershell
py -m pytest
py -m ruff check .
```

### 30.3 Checklist tests API

| Contrôle | OK |
|---|---|
| Liste paginée testée | |
| Détail testé | |
| Création testée | |
| Mise à jour testée | |
| Suppression testée | |
| 404 testé | |
| 409 testé si applicable | |
| 422 testé | |
| Filtres testés | |
| Auth future testée si endpoint protégé | |

---

## 31. Qualité des endpoints

### 31.1 Règles

- Nom explicite.
- Route versionnée.
- Méthode HTTP correcte.
- `response_model` présent.
- Codes HTTP cohérents.
- Pas de logique métier.
- Appel service.
- Erreurs propres.
- Tests associés.

### 31.2 Checklist qualité API

| Contrôle | OK |
|---|---|
| Endpoint sous `/api/v1` | |
| Tag correct | |
| Summary clair | |
| Response model | |
| Pagination si liste | |
| Erreurs documentées | |
| Pas SQLAlchemy dans route | |
| Service appelé | |
| Tests route | |

---

## 32. Conventions de nommage

### 32.1 Routes

| Élément | Convention | Exemple |
|---|---|---|
| Ressource | pluriel | `/websites` |
| Composé | kebab-case | `/api-keys` |
| Admin | préfixe `/admin` | `/admin/settings` |
| ID | `{resource_id}` | `{website_id}` |

### 32.2 Path parameters

| Ressource | Paramètre |
|---|---|
| website | `website_id` |
| entity | `entity_id` |
| keyword | `keyword_id` |
| report | `report_id` |
| user | `user_id` |

### 32.3 Query parameters

| Usage | Nom |
|---|---|
| Page | `page` |
| Taille page | `page_size` |
| Recherche | `q` ou `search` selon standard retenu |
| Tri | `sort` |
| Ordre | `order` |
| Actif | `is_active` |
| Date après | `created_after` |
| Date avant | `created_before` |

### 32.4 Body fields

Champs JSON en `snake_case` :

```json
{
  "entity_id": 1,
  "is_active": true,
  "created_after": "2026-01-01"
}
```

### 32.5 Error codes

Convention recommandée :

```text
UPPER_SNAKE_CASE
```

Exemples :

```text
WEBSITE_NOT_FOUND
PERMISSION_DENIED
VALIDATION_ERROR
```

---

## 33. Anti-patterns interdits

### 33.1 Tableau

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Endpoint sans `/api/v1` | Contrat non versionné | Préfixe versionné |
| Route avec logique métier | Dette et duplication | Service |
| Réponse non typée | Contrat instable | `response_model` |
| Liste non paginée | Performance faible | Pagination standard |
| Erreur brute SQLAlchemy | Fuite technique | Erreur normalisée |
| Message technique exposé | Sécurité/UX | Message contrôlé |
| Champ JSON incohérent | Desktop fragile | Convention snake_case |
| Endpoint admin non protégé | Faille sécurité | Auth/RBAC futur |
| Duplication d'endpoint | Confusion | Réutiliser ressource |
| Breaking change silencieux | Casse Desktop | Dépréciation/version |
| POST pour simple lecture | REST incohérent | GET avec query params |
| Suppression avec 200 inutile | Contrat flou | 204 No Content |

---

## 34. Pattern officiel pour créer un nouvel endpoint

### 34.1 Étapes

1. Définir le besoin métier.
2. Vérifier le module concerné.
3. Créer ou adapter le schéma Pydantic.
4. Créer ou adapter le service.
5. Créer ou adapter le repository.
6. Ajouter la route.
7. Définir `response_model`.
8. Définir les codes HTTP.
9. Ajouter tests API.
10. Ajouter tests service.
11. Vérifier OpenAPI.
12. Vérifier Desktop si concerné.

### 34.2 Diagramme

```text
Besoin endpoint
      |
      v
Contrat JSON
      |
      v
Schema Pydantic
      |
      v
Service
      |
      v
Repository
      |
      v
Route FastAPI
      |
      v
Tests API + Service
```

### 34.3 Checklist

| Contrôle | OK |
|---|---|
| Route versionnée | |
| Méthode correcte | |
| Schéma entrée si payload | |
| Schéma sortie | |
| Service appelé | |
| Pas de SQLAlchemy route | |
| Codes HTTP définis | |
| Erreurs prévues | |
| Tests ajoutés | |
| OpenAPI lisible | |
| Desktop compatible | |

---

## 35. Checklist avant Pull Request API

| Contrôle | Commande ou action | OK |
|---|---|---|
| Statut Git | `git status` | |
| Stat diff | `git diff --stat` | |
| Espaces | `git diff --check` | |
| Tests | `py -m pytest` | |
| Ruff | `py -m ruff check .` | |
| Endpoints versionnés | revue routes | |
| Response model | revue routes | |
| Pagination | listes | |
| Tests API | pytest | |
| Erreurs propres | revue cas erreur | |
| Documentation | docs si contrat change | |
| Pas de secrets | revue diff | |

---

## 36. Roadmap API

### 36.1 API admin

- settings ;
- providers IA ;
- modèles IA ;
- clés API ;
- logs ;
- santé.

### 36.2 Websites

- CRUD stable ;
- pagination ;
- filtres ;
- Desktop table.

### 36.3 Entities

- CRUD ;
- relations sites et mots-clés ;
- filtres par statut.

### 36.4 Keywords

- CRUD ;
- import/export ;
- suivi positions ;
- filtres SEO.

### 36.5 Competitors

- CRUD ;
- comparaison ;
- veille marché.

### 36.6 Reports

- génération ;
- historique ;
- téléchargement ;
- planification future.

### 36.7 SEO

- audits ;
- recommandations ;
- indexation ;
- performance.

### 36.8 GEO

- prompts ;
- citations ;
- réponses IA ;
- scores.

### 36.9 Crawler

- jobs ;
- résultats ;
- erreurs ;
- progression.

### 36.10 IA / Prompts / Logs

- providers ;
- modèles ;
- prompts ;
- exécutions ;
- logs paginés.

### 36.11 Auth complète

- login ;
- refresh ;
- `/me` ;
- RBAC ;
- permissions par endpoint.

### 36.12 API stable v1

- contrats stabilisés ;
- OpenAPI propre ;
- erreurs normalisées ;
- compatibilité Desktop validée.

---

## 37. Annexes

### 37.1 Glossaire

| Terme | Définition |
|---|---|
| API | Contrat HTTP entre clients et backend |
| Endpoint | Route HTTP exposée |
| Ressource | Objet métier exposé |
| Payload | Corps JSON d'une requête |
| Response model | Schéma Pydantic de sortie |
| Pagination | Découpage d'une liste |
| Filtre | Restriction des résultats |
| Tri | Ordonnancement des résultats |
| Breaking change | Changement incompatible |

### 37.2 Abréviations

| Abréviation | Signification |
|---|---|
| REST | Representational State Transfer |
| JSON | JavaScript Object Notation |
| HTTP | Hypertext Transfer Protocol |
| CRUD | Create, Read, Update, Delete |
| RBAC | Role-Based Access Control |
| SEO | Search Engine Optimization |
| GEO | Generative Engine Optimization |
| IA | Intelligence artificielle |

### 37.3 Modèle de réponse paginée

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 37.4 Modèle d'erreur

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Message lisible.",
    "details": null,
    "request_id": "req_..."
  }
}
```

### 37.5 Matrice CRUD récapitulative

| Action | Méthode | Route | Succès |
|---|---|---|---:|
| List | GET | `/resources` | 200 |
| Detail | GET | `/resources/{id}` | 200 |
| Create | POST | `/resources` | 201 |
| Update | PUT/PATCH | `/resources/{id}` | 200 |
| Delete | DELETE | `/resources/{id}` | 204 |

### 37.6 Checklist rapide développeur

| Question | Réponse attendue |
|---|---|
| Mon endpoint est-il sous `/api/v1` ? | Oui |
| La méthode HTTP est-elle correcte ? | Oui |
| Ai-je un `response_model` ? | Oui |
| La route appelle-t-elle un service ? | Oui |
| La liste est-elle paginée ? | Oui si liste |
| Les erreurs sont-elles propres ? | Oui |
| Les tests API existent-ils ? | Oui |
| Le Desktop reste-t-il compatible ? | Oui |

### 37.7 Résumé architectural

L'API de Veille SEO-GEO Groupe A.P&Partner est le contrat stable entre les clients et le backend. Elle doit rester
versionnée, cohérente, documentée, testée et compatible avec le Desktop. Chaque endpoint doit respecter l'architecture
backend officielle :

```text
Route -> Service -> Repository -> Model
```

Les routes exposent HTTP, les services portent le métier, les repositories accèdent aux données, les schémas Pydantic
définissent les contrats JSON, et les erreurs normalisées permettent au Desktop de fournir une expérience fiable.
