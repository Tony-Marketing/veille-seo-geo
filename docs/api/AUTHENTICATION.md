# API Authentification

Ce document définit les recommandations d'authentification pour l'API de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de base de cadrage pour les développements backend FastAPI, le client Desktop PySide6 utilisant `httpx`, et le futur frontend React. Les exemples ci-dessous sont conceptuels : ils illustrent l'architecture attendue, mais ne prétendent pas refléter des fichiers déjà présents dans le code.

## 1. Objectif du document

L'objectif est de définir une base commune pour :

- authentifier les utilisateurs et les clients applicatifs ;
- protéger les routes sensibles ;
- encadrer les rôles et permissions ;
- harmoniser les réponses et erreurs liées à l'authentification ;
- préparer les tests de sécurité et de non-régression ;
- garantir que l'architecture `Routes -> Services -> Repositories -> Models` reste respectée.

Cette documentation ne fige pas une implémentation définitive. Les choix précis, notamment le format des jetons, la durée de session et les mécanismes de rotation, sont à valider lors de l'implémentation.

## 2. Périmètre de l'authentification API

Le périmètre couvre les usages suivants :

- connexion utilisateur ;
- déconnexion utilisateur ;
- renouvellement de session ou de jeton ;
- vérification de l'identité courante ;
- protection des endpoints sensibles ;
- contrôle des droits administrateur ;
- authentification du client Desktop ;
- préparation de l'authentification du futur frontend React ;
- journalisation des événements d'authentification ;
- audit des tentatives, succès, échecs et changements de privilèges.

Hors périmètre de ce document :

- pagination des listes, à documenter dans `docs/api/PAGINATION.md` ;
- filtrage avancé, à documenter dans `docs/api/FILTERING.md` ;
- format global des erreurs applicatives, à documenter dans `docs/api/ERROR_HANDLING.md` ;
- détail complet des endpoints d'administration, documenté dans `docs/api/API_ADMINISTRATION.md`.

## 3. Principes généraux de sécurité

Les principes suivants sont recommandés pour toute implémentation :

| Principe | Règle recommandée | Impact attendu |
|---|---|---|
| Séparation des responsabilités | Les routes délèguent aux services, les services délèguent aux repositories | Code testable et maintenable |
| Moindre privilège | Chaque rôle reçoit uniquement les permissions nécessaires | Réduction du risque d'abus |
| Défense en profondeur | Contrôle d'identité, contrôle de rôle, validation des entrées, journalisation | Protection contre les erreurs isolées |
| Secrets hors code | Les secrets sont lus depuis l'environnement | Pas de secret exposé dans Git |
| Réponses sobres | Les erreurs ne révèlent pas si un email existe | Limitation de l'énumération d'utilisateurs |
| Traçabilité | Les événements sensibles sont journalisés | Audit et investigation facilités |

Les routes FastAPI ne doivent jamais contenir de logique métier. Elles doivent valider la requête, appeler un service et retourner une réponse sérialisée.

## 4. Acteurs concernés

| Acteur | Description | Besoin principal |
|---|---|---|
| Administrateur | Utilisateur interne disposant de droits élevés | Gérer les paramètres, utilisateurs, fournisseurs et journaux |
| Utilisateur interne | Collaborateur utilisant la plateforme | Accéder aux modules SEO, GEO, projets et rapports selon ses droits |
| Service backend | Composant interne exécutant une tâche applicative | Vérifier les droits, persister les données, produire les journaux |
| Client Desktop PySide6 | Application bureautique utilisant `httpx` | Communiquer avec FastAPI en HTTP REST |
| Futur client React | Interface web prévue ultérieurement | Utiliser la même API d'authentification de façon sécurisée |

Le client Desktop et le futur client React ne doivent jamais accéder directement à PostgreSQL. Toute interaction avec les données passe par FastAPI.

## 5. Modèle d'authentification recommandé

Le modèle recommandé est une authentification par jeton court et renouvelable :

- un jeton d'accès de courte durée pour appeler l'API ;
- un mécanisme de renouvellement contrôlé ;
- une révocation côté serveur pour les sessions invalidées ;
- une journalisation des connexions, déconnexions et renouvellements ;
- une séparation claire entre identité, rôle et permissions.

Deux approches peuvent être étudiées :

| Option | Usage recommandé | Points d'attention |
|---|---|---|
| Jeton Bearer JWT signé | API REST, Desktop, futur React | Rotation, expiration courte, révocation à prévoir |
| Session serveur avec identifiant opaque | Environnements internes ou besoin de révocation forte | Stockage serveur, nettoyage des sessions expirées |

Le choix final est à valider lors de l'implémentation. Dans les deux cas, les endpoints sensibles doivent exiger une identité authentifiée et des droits adaptés.

## 6. Connexion utilisateur

La connexion utilisateur doit :

- recevoir des identifiants via une requête HTTPS ;
- valider les entrées avec un schéma Pydantic ;
- déléguer la vérification au service d'authentification ;
- interroger le repository utilisateur uniquement depuis le service ;
- comparer le mot de passe avec un algorithme de hachage robuste ;
- retourner une réponse standardisée en cas de succès ;
- retourner une erreur sobre en cas d'échec.

Endpoint conceptuel recommandé :

| Méthode | Chemin conceptuel | Authentification requise | Description |
|---|---|---:|---|
| `POST` | `/api/v1/auth/login` | Non | Authentifie un utilisateur et ouvre une session |

La réponse ne doit jamais contenir le mot de passe, le hash du mot de passe, les secrets internes ou des informations permettant d'identifier la raison exacte de l'échec.

## 7. Déconnexion utilisateur

La déconnexion doit invalider la session ou le jeton renouvelable associé à l'utilisateur.

Endpoint conceptuel recommandé :

| Méthode | Chemin conceptuel | Authentification requise | Description |
|---|---|---:|---|
| `POST` | `/api/v1/auth/logout` | Oui | Révoque la session courante |

La déconnexion devrait retourner `204 No Content` lorsque l'opération est réussie et ne nécessite pas de corps de réponse.

## 8. Renouvellement de session ou de jeton

Le renouvellement permet de maintenir une session active sans demander une nouvelle saisie du mot de passe.

Recommandations :

- renouveler uniquement avec un jeton ou identifiant prévu pour cet usage ;
- limiter la durée de vie maximale d'une session ;
- journaliser chaque renouvellement ;
- détecter les renouvellements suspects ;
- révoquer les anciens jetons si une rotation stricte est retenue.

Endpoint conceptuel recommandé :

| Méthode | Chemin conceptuel | Authentification requise | Description |
|---|---|---:|---|
| `POST` | `/api/v1/auth/refresh` | Selon modèle choisi | Renouvelle le jeton ou la session |

## 9. Protection des routes sensibles

Les routes sensibles doivent utiliser des dépendances FastAPI dédiées, par exemple :

- `get_current_user` pour récupérer l'utilisateur authentifié ;
- `require_authenticated_user` pour imposer une session valide ;
- `require_admin` pour imposer un rôle administrateur ;
- `require_permission("permission.name")` pour vérifier une permission précise.

Ces dépendances doivent rester fines et déléguer la logique complexe à des services spécialisés si nécessaire.

Exemples de routes sensibles :

| Module | Endpoint conceptuel | Protection recommandée |
|---|---|---|
| Administration | `/api/v1/admin/*` | `require_admin` |
| Projets | `/api/v1/projects/*` | Utilisateur authentifié et permissions projet |
| Rapports | `/api/v1/reports/*` | Utilisateur authentifié et droits de lecture |
| Configuration IA | `/api/v1/admin/ai-providers/*` | Administrateur |
| Journaux d'audit | `/api/v1/admin/audit-logs/*` | Administrateur ou auditeur autorisé |

## 10. Gestion des rôles et permissions

Les rôles regroupent des permissions, mais la décision finale devrait se baser sur des permissions explicites lorsque le périmètre fonctionnel devient plus fin.

Rôles de départ recommandés :

| Rôle | Description | Usage recommandé |
|---|---|---|
| `admin` | Accès complet aux fonctions d'administration | Paramétrage, utilisateurs, journaux, secrets masqués |
| `manager` | Pilotage des modules et projets | Supervision SEO, GEO, planning, rapports |
| `user` | Utilisateur interne standard | Consultation et contribution selon permissions |
| `readonly` | Lecture seule | Audit, consultation, reporting |
| `service` | Compte technique backend | Automatisations internes contrôlées |

Les permissions doivent être documentées et testées au fur et à mesure de l'ajout des modules.

## 11. Droits administrateur

Les droits administrateur sont sensibles et doivent être limités.

Matrice de droits recommandée :

| Action | `admin` | `manager` | `user` | `readonly` | `service` |
|---|---:|---:|---:|---:|---:|
| Consulter le tableau de bord admin | Oui | Non | Non | Non | Non |
| Gérer les utilisateurs | Oui | Non | Non | Non | Non |
| Gérer les paramètres globaux | Oui | Non | Non | Non | Non |
| Gérer les fournisseurs IA | Oui | Non | Non | Non | Non |
| Consulter les journaux d'audit | Oui | Non | Non | Lecture possible si validée | Non |
| Consulter les rapports métier | Oui | Oui | Selon droits | Oui | Non |
| Lancer une automatisation interne | Oui | Selon droits | Non | Non | Oui, si autorisé |
| Modifier ses propres informations | Oui | Oui | Oui | Oui | Non |

Toute élévation de privilège doit être explicitement journalisée.

## 12. Authentification du client Desktop

Le client Desktop PySide6 doit communiquer exclusivement avec FastAPI via HTTP REST, par exemple avec `httpx`.

Recommandations :

- ne jamais embarquer de secret global en clair dans le client Desktop ;
- stocker les jetons utilisateur dans un stockage local sécurisé lorsque disponible ;
- purger les jetons lors de la déconnexion ;
- utiliser HTTPS dans les environnements exposés ;
- gérer proprement les erreurs `401`, `403` et les expirations de session ;
- ne jamais accéder directement à PostgreSQL depuis le Desktop.

Le Desktop agit comme un client applicatif utilisateur, pas comme un service backend de confiance.

## 13. Authentification du futur frontend React

Le futur frontend React devra réutiliser les mêmes principes API :

- communication uniquement via FastAPI ;
- gestion de session compatible avec le navigateur ;
- protection contre les attaques XSS et CSRF selon le mode de stockage retenu ;
- rafraîchissement contrôlé de session ;
- redirection vers la page de connexion en cas de `401` ;
- affichage sobre des erreurs en cas de `403`.

Le choix entre stockage en mémoire, cookie sécurisé `HttpOnly`, ou autre mécanisme est à valider lors de l'implémentation React.

## 14. Gestion des erreurs d'authentification

Les erreurs d'authentification doivent être cohérentes, sobres et non ambiguës pour le client.

Principes recommandés :

- ne pas indiquer si l'email ou le mot de passe est incorrect ;
- distinguer une absence d'authentification (`401`) d'un manque de droits (`403`) ;
- utiliser `422` pour les erreurs de validation Pydantic ;
- utiliser `429` pour la limitation de tentatives ;
- journaliser les erreurs sensibles côté serveur sans exposer les détails au client.

## 15. Codes HTTP recommandés

| Code | Usage recommandé dans l'authentification |
|---:|---|
| `200` | Connexion réussie, session renouvelée, profil courant retourné |
| `201` | Création éventuelle d'un compte ou d'une session persistée, si retenu |
| `204` | Déconnexion réussie sans corps de réponse |
| `400` | Requête invalide hors validation de schéma, état incohérent |
| `401` | Identité absente, jeton invalide, jeton expiré |
| `403` | Identité valide mais permission insuffisante |
| `404` | Ressource liée introuvable sans révéler d'information sensible |
| `409` | Conflit fonctionnel, par exemple session déjà révoquée selon modèle |
| `422` | Erreur de validation Pydantic |
| `429` | Trop de tentatives ou quota de sécurité dépassé |
| `500` | Erreur serveur inattendue |

## 16. Structure recommandée des réponses API liées à l'authentification

Réponse conceptuelle de connexion réussie :

```json
{
  "data": {
    "access_token": "token_court",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "user_123",
      "email": "utilisateur@example.com",
      "display_name": "Utilisateur interne",
      "roles": ["user"],
      "permissions": ["reports.read"]
    }
  },
  "meta": {
    "request_id": "req_123",
    "authenticated": true
  }
}
```

La présence d'un `refresh_token` dans la réponse est à valider selon le modèle retenu. Si un cookie sécurisé est utilisé, le jeton de renouvellement ne devrait pas être exposé dans le corps JSON.

## 17. Structure recommandée des erreurs API liées à l'authentification

Erreur conceptuelle :

```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Identifiants invalides.",
    "details": null
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

Codes d'erreur applicatifs recommandés :

| Code applicatif | HTTP | Description |
|---|---:|---|
| `AUTH_INVALID_CREDENTIALS` | `401` | Identifiants invalides ou utilisateur non autorisé |
| `AUTH_TOKEN_EXPIRED` | `401` | Jeton expiré |
| `AUTH_TOKEN_INVALID` | `401` | Jeton illisible, mal signé ou révoqué |
| `AUTH_PERMISSION_DENIED` | `403` | Permission insuffisante |
| `AUTH_TOO_MANY_ATTEMPTS` | `429` | Trop de tentatives |
| `AUTH_SESSION_REVOKED` | `401` | Session révoquée |

Le format global devra rester cohérent avec `docs/api/ERROR_HANDLING.md` lorsqu'il sera créé.

## 18. Sécurité des mots de passe

Recommandations :

- hacher les mots de passe avec un algorithme robuste et adapté, par exemple Argon2id ou bcrypt selon les dépendances validées ;
- ne jamais stocker de mot de passe en clair ;
- ne jamais journaliser un mot de passe, même partiellement ;
- imposer une politique minimale de complexité ;
- prévoir une rotation ou réinitialisation sécurisée si cette fonctionnalité est ajoutée ;
- comparer les secrets avec des mécanismes résistants aux attaques temporelles lorsque pertinent.

L'ajout d'une dépendance de hachage doit être justifié explicitement au moment de l'implémentation si elle n'est pas déjà présente.

## 19. Stockage sécurisé des secrets

Les secrets doivent être stockés hors du code source.

Exemples de secrets concernés :

- clé de signature des jetons ;
- secret de chiffrement applicatif ;
- paramètres de base PostgreSQL ;
- clés API externes ;
- secrets utilisés par des comptes techniques.

Les secrets ne doivent jamais être envoyés au client Desktop ou React, sauf jeton utilisateur strictement nécessaire au fonctionnement de la session.

## 20. Variables d'environnement

Variables à prévoir selon le modèle retenu :

| Variable | Usage recommandé | Exemple conceptuel |
|---|---|---|
| `APP_ENV` | Environnement courant | `development`, `staging`, `production` |
| `AUTH_ACCESS_TOKEN_EXPIRE_SECONDS` | Durée du jeton d'accès | `900` |
| `AUTH_REFRESH_TOKEN_EXPIRE_SECONDS` | Durée du renouvellement | `604800` |
| `AUTH_TOKEN_SECRET` | Signature ou chiffrement des jetons | Secret long et aléatoire |
| `AUTH_TOKEN_ALGORITHM` | Algorithme de signature si JWT | `HS256` ou autre choix validé |
| `AUTH_MAX_LOGIN_ATTEMPTS` | Limite anti brute force | `5` |
| `AUTH_LOCK_WINDOW_SECONDS` | Fenêtre de limitation | `900` |

Les valeurs de production doivent être définies dans l'environnement de déploiement, jamais dans Git.

## 21. Protection contre les attaques courantes

| Menace | Risque | Mesure recommandée |
|---|---|---|
| Brute force | Tentatives répétées de connexion | Limitation par IP, utilisateur et fenêtre temporelle |
| Énumération d'utilisateurs | Déduction de l'existence d'un compte | Message d'erreur générique |
| Token volé | Utilisation frauduleuse d'une session | Expiration courte, révocation, rotation |
| Session expirée | Appels API avec identité obsolète | Réponse `401`, renouvellement contrôlé |
| Élévation de privilèges | Accès à des droits non autorisés | Vérification serveur des rôles et permissions |

Les contrôles critiques doivent être côté backend. Le client ne doit jamais être considéré comme source de vérité pour les permissions.

## 22. Journalisation des événements d'authentification

Événements à journaliser :

- tentative de connexion réussie ;
- tentative de connexion échouée ;
- déconnexion ;
- renouvellement de session ;
- jeton rejeté ;
- accès refusé par manque de permissions ;
- changement de rôle ;
- révocation de session ;
- verrouillage temporaire après trop de tentatives.

Les journaux ne doivent pas contenir de mot de passe, de jeton complet ou de secret. Les identifiants techniques peuvent être tronqués ou hachés lorsque nécessaire.

## 23. Audit et traçabilité

L'audit doit permettre de répondre aux questions suivantes :

- quel utilisateur a réalisé l'action ;
- depuis quel client ou adresse connue ;
- à quel moment ;
- sur quelle ressource ;
- avec quel résultat ;
- quel identifiant de requête permet de relier les logs.

Structure conceptuelle d'un événement :

```json
{
  "event_type": "auth.login.success",
  "user_id": "user_123",
  "client_type": "desktop",
  "ip_address": "192.0.2.10",
  "user_agent": "APPartnerDesktop/1.0",
  "request_id": "req_123",
  "created_at": "2026-06-30T10:00:00Z"
}
```

La table d'audit éventuelle doit être créée via une migration Alembic explicite.

## 24. Tests à prévoir

Tests recommandés :

| Type de test | Cas à couvrir |
|---|---|
| Tests unitaires services | Connexion réussie, mot de passe invalide, utilisateur inactif |
| Tests repositories | Recherche utilisateur par email, révocation de session |
| Tests API | `401`, `403`, `422`, `429`, réponse de connexion |
| Tests sécurité | Brute force, jeton expiré, jeton révoqué |
| Tests Desktop | Gestion `401`, renouvellement, déconnexion locale |
| Tests régression | Protection des routes admin et endpoints sensibles |

Les tests doivent être placés dans `tests/` selon l'organisation existante du projet.

## 25. Exemples conceptuels de routes FastAPI

Exemple conceptuel, à adapter à l'implémentation réelle :

```python
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: CurrentUser = Depends(require_authenticated_user)):
    await auth_service.logout(current_user.session_id)
```

La route ne contient pas la vérification du mot de passe. Elle délègue au service.

## 26. Exemples conceptuels de schémas Pydantic

Exemple conceptuel compatible avec Pydantic v2 :

```python
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class AuthUserResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    roles: list[str]
    permissions: list[str]


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
```

Les schémas Pydantic gèrent les entrées et sorties API. Ils ne remplacent pas les modèles SQLAlchemy.

## 27. Exemples conceptuels de services

Exemple conceptuel :

```python
class AuthService:
    def __init__(self, user_repository: UserRepository, token_service: TokenService) -> None:
        self.user_repository = user_repository
        self.token_service = token_service

    async def login(self, payload: LoginRequest) -> AuthTokenResponse:
        user = await self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        token = self.token_service.create_access_token(user)
        return build_auth_response(user=user, token=token)
```

Le service contient la logique métier : vérification du compte, contrôle de l'état utilisateur, création du jeton et formatage applicatif.

## 28. Exemples conceptuels de repositories

Exemple conceptuel SQLAlchemy 2.x :

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
```

Le repository contient uniquement l'accès aux données. Il ne décide pas si un utilisateur a le droit de se connecter.

## 29. Exemples conceptuels côté Desktop avec `httpx`

Exemple conceptuel PySide6 côté client Desktop :

```python
import httpx


async def login(api_base_url: str, email: str, password: str) -> dict:
    async with httpx.AsyncClient(base_url=api_base_url, timeout=10.0) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        response.raise_for_status()
        return response.json()
```

Le Desktop doit traiter les erreurs HTTP de manière explicite :

| Code | Comportement Desktop recommandé |
|---:|---|
| `401` | Demander une reconnexion ou tenter un renouvellement contrôlé |
| `403` | Afficher un message d'accès refusé |
| `422` | Signaler une saisie invalide |
| `429` | Demander d'attendre avant une nouvelle tentative |
| `500` | Afficher un message d'erreur serveur non technique |

## 30. Critères d'acceptation

Une première implémentation sera acceptable si :

- les routes d'authentification existent et délèguent aux services ;
- aucune logique métier n'est codée directement dans les routes ;
- les repositories isolent les accès SQLAlchemy ;
- les schémas Pydantic valident les entrées et sorties ;
- les mots de passe sont hachés ;
- les routes sensibles sont protégées ;
- les erreurs `401` et `403` sont correctement distinguées ;
- les événements sensibles sont journalisés ;
- les migrations Alembic nécessaires sont explicites ;
- aucun `Base.metadata.create_all()` ou `Base.metadata.drop_all()` n'est utilisé dans les migrations ;
- le client Desktop communique uniquement avec FastAPI.

## 31. Checklist de conformité

| Point de contrôle | Statut attendu |
|---|---|
| Architecture `Routes -> Services -> Repositories -> Models` respectée | Obligatoire |
| Routes sans logique métier | Obligatoire |
| Accès PostgreSQL uniquement côté backend | Obligatoire |
| Schémas Pydantic séparés des modèles SQLAlchemy | Obligatoire |
| Endpoints sensibles protégés | Obligatoire |
| Secrets hors Git | Obligatoire |
| Migrations Alembic explicites | Obligatoire |
| Tests Pytest prévus ou ajoutés selon périmètre | Obligatoire |
| Réponses d'erreur homogènes | À aligner avec `ERROR_HANDLING.md` |
| Compatibilité futur React | À valider lors de l'implémentation |

## 32. Points à éviter

À éviter strictement :

- mettre la vérification du mot de passe dans une route FastAPI ;
- appeler PostgreSQL directement depuis le Desktop ;
- exposer un hash de mot de passe dans une réponse API ;
- retourner un message indiquant qu'un email existe ;
- stocker une clé de signature dans le code ;
- utiliser un jeton sans expiration ;
- protéger uniquement l'interface et pas l'API ;
- confondre authentification et autorisation ;
- utiliser `Base.metadata.create_all()` dans une migration ;
- utiliser `Base.metadata.drop_all()` dans une migration ;
- créer une dépendance externe sans justification.

## 33. Liens avec les futurs documents

| Document | Lien avec l'authentification |
|---|---|
| `docs/api/ERROR_HANDLING.md` | Définira le format global des erreurs API, à harmoniser avec les erreurs d'authentification |
| `docs/api/PAGINATION.md` | Documentera la pagination des listes protégées, par exemple journaux et utilisateurs |
| `docs/api/FILTERING.md` | Documentera les filtres sur les ressources protégées |
| `docs/api/API_ADMINISTRATION.md` | Décrit les endpoints d'administration qui devront rester protégés par droits adaptés |

## Diagramme de flux conceptuel

Flux de connexion recommandé :

```text
Client Desktop / React
        |
        | POST /api/v1/auth/login
        v
Route FastAPI
        |
        | appelle
        v
AuthService
        |
        | lit utilisateur
        v
UserRepository
        |
        | requête SQLAlchemy
        v
PostgreSQL
        |
        | résultat
        v
AuthService
        |
        | vérifie mot de passe + crée jeton
        v
Route FastAPI
        |
        | réponse JSON
        v
Client Desktop / React
```

Ce flux rappelle que la logique métier reste dans les services et que le client ne communique jamais directement avec la base de données.
