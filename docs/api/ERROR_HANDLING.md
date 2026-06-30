# API Gestion des erreurs

Ce document définit les recommandations de gestion standardisée des erreurs pour l'API de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence commune pour les routes FastAPI, les services backend, les repositories SQLAlchemy, les schémas Pydantic, le client Desktop PySide6 utilisant `httpx`, le futur frontend React, et les futurs documents `PAGINATION.md` et `FILTERING.md`.

Les exemples de code sont conceptuels. Ils illustrent l'organisation attendue, sans prétendre que ces classes, fonctions ou fichiers existent déjà dans le dépôt.

## 1. Objectif du document

L'objectif est de définir un cadre commun pour :

- structurer les réponses d'erreur API ;
- associer les erreurs aux bons codes HTTP ;
- conserver une séparation claire entre erreurs métier, validation, sécurité et incidents techniques ;
- garantir une expérience cohérente entre API, Desktop et futur React ;
- préserver la sécurité en production ;
- faciliter la journalisation, l'audit et la résolution des incidents ;
- respecter l'architecture `Routes -> Services -> Repositories -> Models`.

Cette documentation ne fige pas une implémentation définitive. Les noms exacts des classes d'exceptions, modules et handlers sont à valider lors de l'implémentation.

## 2. Périmètre de la gestion des erreurs API

Le périmètre couvre :

- erreurs de validation des entrées ;
- erreurs d'authentification ;
- erreurs d'autorisation ;
- erreurs métier ;
- ressources introuvables ;
- conflits de données ;
- erreurs SQLAlchemy et PostgreSQL ;
- erreurs d'import/export de configuration ;
- erreurs inattendues ;
- format des réponses JSON d'erreur ;
- journalisation et traçabilité via `request_id` ;
- comportement attendu côté Desktop PySide6 avec `httpx` ;
- comportement prévu côté futur frontend React.

Hors périmètre détaillé :

- règles de pagination, à documenter dans `docs/api/PAGINATION.md` ;
- règles de filtrage, à documenter dans `docs/api/FILTERING.md` ;
- endpoints d'administration, couverts par `docs/api/API_ADMINISTRATION.md` ;
- détails complets de l'authentification, couverts par `docs/api/AUTHENTICATION.md`.

## 3. Principes généraux

Les erreurs doivent être :

- prévisibles pour les clients API ;
- cohérentes entre tous les modules ;
- suffisamment explicites pour permettre une correction côté client ;
- sûres pour la production ;
- traçables côté serveur ;
- testables avec Pytest ;
- compatibles avec FastAPI, Pydantic v2, SQLAlchemy 2.x et PostgreSQL.

Principes recommandés :

| Principe | Règle recommandée | Objectif |
|---|---|---|
| Cohérence | Utiliser un format JSON commun | Simplifier Desktop, futur React et tests |
| Sobriété | Ne pas exposer de détails internes en production | Réduire le risque de fuite d'information |
| Traçabilité | Inclure un `request_id` | Relier client, logs et audit |
| Séparation | Mapper les erreurs au bon niveau applicatif | Respecter l'architecture |
| Sécurité | Ne jamais exposer secrets, tokens ou stack traces | Protéger les données sensibles |

## 4. Rôle dans l'architecture `Routes -> Services -> Repositories -> Models`

La gestion des erreurs doit respecter la chaîne obligatoire :

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

| Couche | Responsabilité erreur | À éviter |
|---|---|---|
| Routes | Appeler les services, laisser les handlers formater les erreurs | Coder la logique métier ou SQL |
| Services | Déclencher les exceptions métier et sécurité | Retourner des dictionnaires d'erreur ad hoc |
| Repositories | Isoler les erreurs d'accès aux données | Décider des règles métier |
| Models | Représenter les tables et contraintes | Contenir des décisions applicatives |
| Schémas Pydantic | Valider entrées et sorties | Accéder à la base de données |

Les routes ne doivent pas contenir de logique métier. Elles peuvent déclarer les dépendances FastAPI et déléguer aux services.

## 5. Typologie des erreurs

| Type d'erreur | Description | Exemple | Couche principale |
|---|---|---|---|
| Erreur métier | Règle fonctionnelle non respectée | Projet déjà archivé | Service |
| Erreur de validation | Entrée invalide ou incomplète | Email mal formé | Pydantic / Route |
| Erreur d'authentification | Identité absente ou invalide | Jeton expiré | Sécurité API |
| Erreur d'autorisation | Identité valide mais droits insuffisants | Accès admin refusé | Service / Dépendance |
| Erreur technique | Incident applicatif contrôlé | Import impossible | Service |
| Erreur système | Incident inattendu ou infrastructure | Base indisponible | Infrastructure / Handler |

Les erreurs métier doivent être exprimées sous forme d'exceptions applicatives explicites, puis converties en réponse HTTP par un handler centralisé.

## 6. Format standard recommandé

Format JSON recommandé pour une erreur :

```json
{
  "error": "RESOURCE_NOT_FOUND",
  "message": "La ressource demandée est introuvable.",
  "details": {
    "resource": "project"
  },
  "code": "PROJECT_NOT_FOUND",
  "status_code": 404,
  "path": "/api/v1/projects/project_123",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Le champ `details` doit rester sûr pour la production. Il ne doit pas contenir de secret, token, mot de passe, stack trace brute, chaîne de connexion, clé API ou valeur sensible.

## 7. Champs recommandés

| Champ | Type recommandé | Description |
|---|---|---|
| `error` | `string` | Catégorie courte et stable de l'erreur |
| `message` | `string` | Message public compréhensible |
| `details` | `object | null` | Informations utiles et non sensibles |
| `code` | `string` | Code interne applicatif |
| `status_code` | `integer` | Code HTTP de la réponse |
| `path` | `string` | Chemin appelé |
| `method` | `string` | Méthode HTTP |
| `request_id` | `string` | Identifiant de corrélation |
| `timestamp` | `string` | Date ISO 8601 UTC |

Le format exact pourra être aligné lors de l'implémentation avec les handlers FastAPI et les besoins du client Desktop.

## 8. Règles de nommage des codes d'erreur internes

Les codes internes doivent être :

- en majuscules ;
- écrits en anglais technique ;
- stables dans le temps ;
- orientés domaine ;
- sans donnée dynamique ;
- documentés lorsqu'ils deviennent publics pour les clients.

Format recommandé :

```text
DOMAIN_REASON
```

Exemples :

| Code | Domaine | Signification |
|---|---|---|
| `AUTH_TOKEN_EXPIRED` | Authentification | Jeton expiré |
| `AUTH_PERMISSION_DENIED` | Autorisation | Droits insuffisants |
| `PROJECT_NOT_FOUND` | Projets | Projet introuvable |
| `CONFIG_IMPORT_INVALID` | Administration | Import de configuration invalide |
| `DATABASE_CONSTRAINT_VIOLATION` | Données | Contrainte PostgreSQL violée |

Les codes ne doivent pas inclure d'identifiants utilisateur, d'emails, de tokens ou de valeurs métier sensibles.

## 9. Codes HTTP recommandés et usages

| Code | Usage recommandé |
|---:|---|
| `200` | Succès avec corps de réponse |
| `201` | Ressource créée avec succès |
| `204` | Succès sans corps de réponse |
| `400` | Requête incohérente ou erreur fonctionnelle générique |
| `401` | Authentification absente, invalide ou expirée |
| `403` | Authentification valide mais droits insuffisants |
| `404` | Route ou ressource introuvable |
| `409` | Conflit de données ou d'état |
| `422` | Erreur de validation Pydantic v2 |
| `429` | Trop de requêtes ou limitation de sécurité |
| `500` | Erreur serveur inattendue |
| `503` | Service temporairement indisponible |

Les codes `200`, `201` et `204` ne sont pas des erreurs, mais ils sont listés ici pour cadrer les transitions entre réponses de succès et réponses d'erreur.

## 10. Erreurs d'authentification

Les erreurs d'authentification doivent rester cohérentes avec `docs/api/AUTHENTICATION.md`.

Codes recommandés :

| Code interne | HTTP | Message public recommandé |
|---|---:|---|
| `AUTH_INVALID_CREDENTIALS` | `401` | Identifiants invalides. |
| `AUTH_TOKEN_EXPIRED` | `401` | Session expirée. |
| `AUTH_TOKEN_INVALID` | `401` | Session invalide. |
| `AUTH_SESSION_REVOKED` | `401` | Session révoquée. |
| `AUTH_TOO_MANY_ATTEMPTS` | `429` | Trop de tentatives. Réessayez plus tard. |

Les messages ne doivent pas révéler si un email existe, si un compte est désactivé ou quel élément d'identification est incorrect.

## 11. Erreurs d'autorisation et droits insuffisants

Une erreur d'autorisation intervient quand l'utilisateur est authentifié mais n'a pas les droits requis.

Réponse recommandée :

```json
{
  "error": "FORBIDDEN",
  "message": "Accès refusé.",
  "details": null,
  "code": "AUTH_PERMISSION_DENIED",
  "status_code": 403,
  "path": "/api/v1/admin/settings",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Les permissions doivent être vérifiées côté backend. Le client Desktop ou React ne doit jamais être considéré comme source de vérité.

## 12. Erreurs de validation Pydantic v2

Les erreurs Pydantic v2 doivent être transformées en réponse stable et lisible.

Recommandations :

- retourner `422 Unprocessable Entity` ;
- conserver les champs invalides dans `details` si cela ne révèle rien de sensible ;
- éviter de renvoyer des valeurs brutes sensibles ;
- uniformiser la structure avec les autres erreurs API.

Exemple conceptuel :

```json
{
  "error": "VALIDATION_ERROR",
  "message": "La requête contient des champs invalides.",
  "details": {
    "fields": [
      {
        "name": "email",
        "reason": "Adresse email invalide."
      }
    ]
  },
  "code": "REQUEST_VALIDATION_ERROR",
  "status_code": 422,
  "path": "/api/v1/auth/login",
  "method": "POST",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

## 13. Erreurs liées aux paramètres de requête

Les paramètres de requête invalides doivent être traités comme des erreurs de validation.

Exemples :

| Paramètre | Problème | Code recommandé |
|---|---|---|
| `page` | Valeur inférieure à 1 | `REQUEST_INVALID_QUERY_PARAMETER` |
| `page_size` | Valeur trop élevée | `REQUEST_INVALID_QUERY_PARAMETER` |
| `sort` | Champ non autorisé | `REQUEST_INVALID_SORT_FIELD` |
| `order` | Sens inconnu | `REQUEST_INVALID_SORT_ORDER` |

Les règles détaillées de pagination et filtrage seront précisées dans `docs/api/PAGINATION.md` et `docs/api/FILTERING.md`.

## 14. Erreurs liées aux routes inexistantes

Une route inexistante doit retourner `404`.

Réponse recommandée :

```json
{
  "error": "NOT_FOUND",
  "message": "La route demandée est introuvable.",
  "details": null,
  "code": "ROUTE_NOT_FOUND",
  "status_code": 404,
  "path": "/api/v1/unknown",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

En production, la réponse ne doit pas lister les routes disponibles.

## 15. Erreurs liées aux ressources introuvables

Une ressource introuvable doit retourner `404` lorsque l'utilisateur est autorisé à connaître l'existence de ce type de ressource.

Exemples :

| Ressource | Code recommandé | Message public |
|---|---|---|
| Projet | `PROJECT_NOT_FOUND` | Projet introuvable. |
| Rapport | `REPORT_NOT_FOUND` | Rapport introuvable. |
| Utilisateur | `USER_NOT_FOUND` | Utilisateur introuvable. |
| Configuration | `CONFIG_NOT_FOUND` | Configuration introuvable. |

Dans certains contextes sensibles, il peut être recommandé de retourner un message générique pour éviter de révéler l'existence d'une ressource.

## 16. Erreurs liées aux conflits de données

Les conflits de données doivent retourner `409 Conflict`.

Cas typiques :

- création d'une ressource déjà existante ;
- modification d'une ressource dans un état incompatible ;
- conflit de version ou d'état ;
- tentative de réactivation d'un élément déjà actif ;
- import d'une configuration incompatible avec l'état courant.

Exemple :

```json
{
  "error": "CONFLICT",
  "message": "La ressource existe déjà.",
  "details": {
    "field": "name"
  },
  "code": "RESOURCE_ALREADY_EXISTS",
  "status_code": 409,
  "path": "/api/v1/projects",
  "method": "POST",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

## 17. Erreurs liées aux contraintes PostgreSQL

Les contraintes PostgreSQL doivent être interceptées côté repository ou dans une couche d'adaptation proche de l'accès aux données, puis converties en exception applicative.

| Contrainte | Erreur technique | Erreur API recommandée |
|---|---|---|
| Unique | Valeur déjà utilisée | `409 RESOURCE_ALREADY_EXISTS` |
| Foreign key | Référence inexistante | `400 RELATED_RESOURCE_INVALID` |
| Not null | Donnée obligatoire absente | `422 REQUEST_VALIDATION_ERROR` si détectée avant SQL |
| Check | Règle de données violée | `400 DATA_CONSTRAINT_VIOLATION` |

Les noms de tables, contraintes et index internes ne doivent pas être exposés directement au client en production.

## 18. Erreurs liées aux repositories SQLAlchemy

Les repositories doivent contenir uniquement l'accès aux données SQLAlchemy.

Recommandations :

- ne pas retourner directement une exception SQLAlchemy au client ;
- convertir les erreurs de contrainte en exceptions applicatives ;
- journaliser les erreurs techniques avec `request_id` ;
- ne pas décider des règles métier dans le repository ;
- ne pas masquer silencieusement une erreur de base de données inattendue.

Un repository peut lever une exception technique contrôlée, par exemple `RepositoryError`, qui sera ensuite mappée par le service ou le handler.

## 19. Erreurs liées aux services métier

Les services contiennent la logique métier. Ils doivent lever des exceptions applicatives explicites.

Exemples :

| Situation métier | Exception conceptuelle | HTTP |
|---|---|---:|
| Projet introuvable | `ProjectNotFoundError` | `404` |
| Action interdite sur projet archivé | `ProjectArchivedError` | `409` |
| Droits insuffisants | `PermissionDeniedError` | `403` |
| Import invalide | `ConfigurationImportInvalidError` | `400` |

Les services ne doivent pas construire eux-mêmes la réponse JSON HTTP finale. Ce rôle revient aux handlers API.

## 20. Erreurs liées aux imports/exports de configuration

Les imports et exports de configuration peuvent générer des erreurs spécifiques :

| Cas | HTTP | Code recommandé |
|---|---:|---|
| Fichier invalide | `400` | `CONFIG_IMPORT_INVALID` |
| Format non supporté | `400` | `CONFIG_FORMAT_UNSUPPORTED` |
| Conflit avec configuration existante | `409` | `CONFIG_IMPORT_CONFLICT` |
| Export impossible | `500` | `CONFIG_EXPORT_FAILED` |
| Service temporairement indisponible | `503` | `CONFIG_SERVICE_UNAVAILABLE` |

Les erreurs d'import ne doivent pas exposer le contenu complet du fichier importé si celui-ci peut contenir des secrets.

## 21. Erreurs liées au Desktop PySide6 via `httpx`

Le client Desktop doit traiter les erreurs HTTP de manière stable.

Comportement recommandé :

| HTTP | Comportement Desktop |
|---:|---|
| `400` | Afficher un message de requête invalide |
| `401` | Demander une reconnexion ou tenter un renouvellement contrôlé |
| `403` | Afficher un accès refusé |
| `404` | Indiquer que la ressource n'existe plus ou est inaccessible |
| `409` | Proposer de rafraîchir les données |
| `422` | Mettre en évidence les champs invalides |
| `429` | Demander d'attendre avant de réessayer |
| `500` | Afficher une erreur serveur générique |
| `503` | Indiquer une indisponibilité temporaire |

Le Desktop ne doit jamais accéder directement à PostgreSQL. Il communique uniquement avec FastAPI via HTTP REST.

## 22. Erreurs prévues pour le futur frontend React

Le futur frontend React devra utiliser le même format d'erreur.

Recommandations :

- centraliser le traitement des erreurs HTTP dans un service API ;
- rediriger vers la connexion en cas de `401` lorsque la session n'est plus valide ;
- afficher un accès refusé pour `403` ;
- afficher les erreurs de champs pour `422` ;
- afficher un message sobre pour `500` et `503` ;
- conserver le `request_id` visible ou copiable pour le support.

Le frontend ne doit pas interpréter les permissions comme source d'autorité. Les droits restent validés côté backend.

## 23. Gestion du `request_id` et traçabilité

Chaque requête devrait disposer d'un `request_id`.

Sources possibles :

- en-tête entrant `X-Request-ID` si fourni par un proxy ou client fiable ;
- génération serveur si absent ;
- propagation dans les logs ;
- inclusion dans chaque réponse d'erreur ;
- retour au client Desktop ou React pour faciliter le support.

En-tête recommandé :

```text
X-Request-ID: req_123
```

Le `request_id` ne doit pas être utilisé comme secret. Il sert uniquement à la corrélation.

## 24. Journalisation des erreurs

Les erreurs doivent être journalisées selon leur gravité.

Champs recommandés :

| Champ log | Description |
|---|---|
| `timestamp` | Date de l'événement |
| `level` | Niveau de log |
| `request_id` | Identifiant de corrélation |
| `method` | Méthode HTTP |
| `path` | Chemin appelé |
| `status_code` | Code HTTP retourné |
| `error_code` | Code applicatif |
| `user_id` | Identifiant utilisateur si disponible |
| `client_type` | Desktop, React, service backend |
| `duration_ms` | Durée de traitement |

Les logs techniques détaillés doivent rester côté serveur.

## 25. Niveau de logs recommandé

| Niveau | Usage recommandé |
|---|---|
| `debug` | Diagnostic local en développement, jamais pour secrets |
| `info` | Événements normaux, requêtes traitées, erreurs attendues peu sensibles |
| `warning` | Erreurs client répétées, tentatives invalides, conflits |
| `error` | Erreurs techniques ou métier graves nécessitant analyse |
| `critical` | Indisponibilité majeure, perte de service, incident sécurité |

En production, le niveau `debug` doit être désactivé ou fortement contrôlé.

## 26. Données à ne jamais journaliser

Ne jamais journaliser :

- mots de passe ;
- hash de mot de passe ;
- tokens complets ;
- refresh tokens ;
- clés API ;
- secrets de chiffrement ;
- chaînes de connexion PostgreSQL complètes ;
- contenu complet de fichiers importés pouvant contenir des secrets ;
- stack traces brutes dans les réponses client ;
- données personnelles non nécessaires à l'investigation.

Si une valeur doit être corrélée, utiliser une empreinte, un identifiant interne ou une version masquée.

## 27. Comportement en environnement développement

En développement, il est recommandé de :

- conserver le format d'erreur standard ;
- autoriser des détails techniques supplémentaires uniquement côté logs ;
- afficher éventuellement un message plus précis dans les outils développeur ;
- garder les mêmes codes HTTP qu'en production ;
- tester les handlers d'erreurs comme en production.

Même en développement, les secrets ne doivent pas être exposés dans les réponses API.

## 28. Comportement en environnement production

En production :

- ne jamais exposer de stack trace brute ;
- ne jamais exposer d'erreur SQL brute ;
- ne jamais révéler de secret ;
- retourner des messages publics sobres ;
- inclure un `request_id` ;
- journaliser les détails côté serveur ;
- retourner `500` pour les erreurs inattendues ;
- retourner `503` si un service nécessaire est temporairement indisponible.

Le client doit pouvoir afficher un message compréhensible sans connaître le détail interne.

## 29. Gestion des erreurs inattendues

Toute exception non prévue doit être interceptée par un handler global.

Comportement recommandé :

- journaliser l'exception avec stack trace côté serveur ;
- associer un `request_id` ;
- retourner une réponse `500` standardisée ;
- ne pas exposer le type Python exact en production ;
- ne pas masquer l'incident dans les logs.

Réponse publique recommandée :

```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Une erreur inattendue est survenue.",
  "details": null,
  "code": "INTERNAL_ERROR",
  "status_code": 500,
  "path": "/api/v1/reports",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

## 30. Stratégie de masquage des détails techniques

Le masquage doit être appliqué avant toute réponse au client.

À masquer :

- noms internes de contraintes PostgreSQL ;
- stack traces ;
- chemins locaux du serveur ;
- variables d'environnement ;
- requêtes SQL complètes ;
- valeurs de secrets ;
- tokens ;
- détails d'implémentation non utiles au client.

À conserver :

- message public ;
- code interne stable ;
- `request_id` ;
- code HTTP ;
- champ concerné lorsque cela est sûr ;
- indication d'action possible côté client si utile.

## 31. Exemples conceptuels de réponses JSON d'erreur

Erreur d'authentification :

```json
{
  "error": "UNAUTHORIZED",
  "message": "Session expirée.",
  "details": null,
  "code": "AUTH_TOKEN_EXPIRED",
  "status_code": 401,
  "path": "/api/v1/projects",
  "method": "GET",
  "request_id": "req_123",
  "timestamp": "2026-06-30T10:00:00Z"
}
```

Erreur de conflit :

```json
{
  "error": "CONFLICT",
  "message": "La ressource ne peut pas être modifiée dans son état actuel.",
  "details": {
    "state": "archived"
  },
  "code": "PROJECT_ARCHIVED",
  "status_code": 409,
  "path": "/api/v1/projects/project_123",
  "method": "PUT",
  "request_id": "req_124",
  "timestamp": "2026-06-30T10:01:00Z"
}
```

Erreur de service indisponible :

```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "Le service est temporairement indisponible.",
  "details": null,
  "code": "SERVICE_TEMPORARILY_UNAVAILABLE",
  "status_code": 503,
  "path": "/api/v1/admin/config/export",
  "method": "GET",
  "request_id": "req_125",
  "timestamp": "2026-06-30T10:02:00Z"
}
```

## 32. Exemples conceptuels de handlers FastAPI

Exemple conceptuel :

```python
from fastapi import Request
from fastapi.responses import JSONResponse


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    payload = {
        "error": exc.error,
        "message": exc.public_message,
        "details": exc.safe_details,
        "code": exc.code,
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method,
        "request_id": request.state.request_id,
        "timestamp": utc_now_iso(),
    }
    return JSONResponse(status_code=exc.status_code, content=payload)
```

Le handler formate la réponse. Il ne doit pas contenir de logique métier.

## 33. Exemples conceptuels de mapping d'exceptions métier

Exemple conceptuel :

```python
class AppError(Exception):
    status_code = 500
    error = "INTERNAL_SERVER_ERROR"
    code = "INTERNAL_ERROR"
    public_message = "Une erreur inattendue est survenue."
    safe_details = None


class ProjectNotFoundError(AppError):
    status_code = 404
    error = "NOT_FOUND"
    code = "PROJECT_NOT_FOUND"
    public_message = "Projet introuvable."


class PermissionDeniedError(AppError):
    status_code = 403
    error = "FORBIDDEN"
    code = "AUTH_PERMISSION_DENIED"
    public_message = "Accès refusé."
```

Les exceptions doivent rester indépendantes du framework lorsque c'est pertinent, afin de garder les services testables.

## 34. Exemples conceptuels côté service

Exemple conceptuel :

```python
class ProjectService:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self.project_repository = project_repository

    async def get_project(self, project_id: str, current_user: CurrentUser) -> Project:
        project = await self.project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError()

        if not current_user.can_read_project(project):
            raise PermissionDeniedError()

        return project
```

Le service décide des règles métier et des droits. Il ne formate pas la réponse HTTP.

## 35. Exemples conceptuels côté repository

Exemple conceptuel SQLAlchemy 2.x :

```python
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, project_id: str) -> Project | None:
        statement = select(Project).where(Project.id == project_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def save(self, project: Project) -> None:
        try:
            self.session.add(project)
            await self.session.flush()
        except IntegrityError as exc:
            raise DataConstraintViolationError() from exc
        except SQLAlchemyError as exc:
            raise RepositoryUnavailableError() from exc
```

Le repository isole SQLAlchemy. Il ne retourne pas une erreur SQL brute au client.

## 36. Exemples conceptuels côté Desktop avec `httpx`

Exemple conceptuel PySide6 / `httpx` :

```python
import httpx


class ApiClientError(Exception):
    def __init__(self, message: str, request_id: str | None = None) -> None:
        self.message = message
        self.request_id = request_id
        super().__init__(message)


async def fetch_project(api_base_url: str, token: str, project_id: str) -> dict:
    async with httpx.AsyncClient(base_url=api_base_url, timeout=10.0) as client:
        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code >= 400:
        payload = response.json()
        raise ApiClientError(
            message=payload.get("message", "Erreur API."),
            request_id=payload.get("request_id"),
        )

    return response.json()
```

Le client Desktop doit exploiter `message`, `code`, `status_code` et `request_id`, sans dépendre de détails internes.

## 37. Tests à prévoir

Tests recommandés :

| Type de test | Cas à couvrir |
|---|---|
| Tests handlers | Format JSON, `request_id`, timestamp, masquage |
| Tests validation | Erreurs Pydantic v2 en `422` |
| Tests auth | `401`, `403`, cohérence avec authentification |
| Tests repositories | Conversion `IntegrityError`, erreurs SQLAlchemy |
| Tests services | Exceptions métier explicites |
| Tests Desktop | Mapping des erreurs `httpx` |
| Tests production | Pas de stack trace dans les réponses |
| Tests logs | Absence de secrets journalisés |

Les tests doivent être placés dans `tests/` selon les conventions existantes du projet.

## 38. Critères d'acceptation

Une implémentation de gestion d'erreurs sera acceptable si :

- toutes les réponses d'erreur suivent un format commun ;
- les erreurs Pydantic v2 sont transformées en `422` cohérent ;
- les erreurs d'authentification restent alignées avec `docs/api/AUTHENTICATION.md` ;
- les erreurs d'autorisation utilisent `403` ;
- les erreurs inattendues retournent `500` sans stack trace brute ;
- les erreurs de base de données ne sont pas exposées directement ;
- chaque erreur contient un `request_id` ;
- les logs contiennent assez d'informations pour investiguer ;
- les secrets ne sont jamais renvoyés ni journalisés ;
- le Desktop peut traiter les erreurs via HTTP REST ;
- le futur React pourra réutiliser les mêmes codes et formats.

## 39. Checklist de conformité

| Point de contrôle | Statut attendu |
|---|---|
| Format d'erreur standard documenté | Obligatoire |
| Codes HTTP cohérents | Obligatoire |
| Codes internes stables | Obligatoire |
| `request_id` présent | Obligatoire |
| Stack trace absente des réponses production | Obligatoire |
| Secrets absents des réponses et logs | Obligatoire |
| Routes sans logique métier | Obligatoire |
| Services responsables des erreurs métier | Obligatoire |
| Repositories isolant SQLAlchemy | Obligatoire |
| Desktop uniquement via FastAPI REST | Obligatoire |
| Compatibilité futur React | À valider lors de l'implémentation |
| Tests Pytest prévus | Obligatoire |

## 40. Points à éviter

À éviter strictement :

- retourner des formats d'erreur différents selon les modules ;
- exposer une stack trace brute en production ;
- exposer une erreur SQLAlchemy ou PostgreSQL brute ;
- inclure un token, mot de passe ou secret dans `details` ;
- journaliser un corps de requête contenant un mot de passe ;
- coder la logique métier dans les routes FastAPI ;
- faire décider un repository d'une règle métier ;
- faire accéder le Desktop directement à PostgreSQL ;
- confondre `401` et `403` ;
- utiliser `500` pour toutes les erreurs métier ;
- créer `PAGINATION.md` ou `FILTERING.md` avant leur traitement dédié.

## 41. Liens avec les documents API

| Document | Lien avec la gestion des erreurs |
|---|---|
| `docs/api/AUTHENTICATION.md` | Définit les erreurs d'authentification et de droits à garder cohérentes |
| `docs/api/PAGINATION.md` | Précisera les erreurs liées aux paramètres `page`, `page_size`, tri et limites |
| `docs/api/FILTERING.md` | Précisera les erreurs liées aux filtres invalides ou non autorisés |
| `docs/api/API_ADMINISTRATION.md` | Décrit des endpoints d'administration qui devront utiliser le format standard |

## Matrice de correspondance erreurs, HTTP et responsabilités

| Type d'erreur | HTTP recommandé | Code exemple | Couche responsable | Client concerné |
|---|---:|---|---|---|
| Validation Pydantic | `422` | `REQUEST_VALIDATION_ERROR` | Schémas / handlers | Desktop, React |
| Authentification | `401` | `AUTH_TOKEN_EXPIRED` | Dépendances sécurité | Desktop, React |
| Autorisation | `403` | `AUTH_PERMISSION_DENIED` | Services / dépendances | Desktop, React |
| Ressource introuvable | `404` | `PROJECT_NOT_FOUND` | Services | Desktop, React |
| Conflit métier | `409` | `PROJECT_ARCHIVED` | Services | Desktop, React |
| Contrainte PostgreSQL | `409` ou `400` | `DATABASE_CONSTRAINT_VIOLATION` | Repositories / services | API |
| Trop de requêtes | `429` | `RATE_LIMIT_EXCEEDED` | Middleware / sécurité | Desktop, React |
| Erreur inattendue | `500` | `INTERNAL_ERROR` | Handler global | Tous |
| Service indisponible | `503` | `SERVICE_TEMPORARILY_UNAVAILABLE` | Infrastructure / handler | Tous |

## Diagramme de flux d'une erreur

Flux conceptuel d'une erreur métier ou technique :

```text
Client Desktop / React
        |
        | Requête HTTP REST
        v
Route FastAPI
        |
        | appelle
        v
Service métier
        |
        | peut lever une exception applicative
        v
Repository SQLAlchemy
        |
        | peut convertir une erreur SQLAlchemy
        v
Exception applicative
        |
        | interceptée par handler FastAPI
        v
Réponse JSON standardisée
        |
        | contient code + message + request_id
        v
Client Desktop / React
```

Ce flux garantit que la logique métier reste dans les services, que l'accès aux données reste dans les repositories et que le client reçoit une erreur stable sans détail sensible.
