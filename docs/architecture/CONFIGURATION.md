# Configuration Architecture Specification

Projet : **Veille SEO-GEO Groupe A.P&Partner**  
Statut : document de référence officiel  
Portée : configuration backend, Desktop, API, base de données, sécurité, logging, environnements et modules futurs  
Version documentaire : 1.0

---

## 1. Présentation

Ce document définit l'architecture officielle de configuration du projet **Veille SEO-GEO Groupe A.P&Partner**. Il décrit où placer la configuration, comment la valider, comment séparer les environnements, comment protéger les secrets et comment éviter la dispersion de paramètres critiques dans le code.

La configuration doit rester lisible, centralisée, explicite et sécurisée. Elle ne doit jamais devenir une collection de constantes isolées dans les routes, les services, les pages Desktop ou les scripts de migration.

### 1.1 Rôle du document

| Élément | Description |
|---|---|
| Rôle principal | Définir les règles de configuration communes au backend, au Desktop, à l'API, à PostgreSQL, à Alembic, au logging et aux modules futurs. |
| Public cible | Développeurs backend, développeurs Desktop, responsables architecture, responsables sécurité, relecteurs de Pull Request. |
| Horizon | Maintenable jusqu'à la version 1.0 et extensible après stabilisation interne. |
| Niveau de détail | Spécification d'architecture, pas tutoriel `.env` ni simple inventaire de variables. |

### 1.2 Vision de configuration

La configuration du projet doit suivre une logique simple :

```text
Configuration explicite
        |
        v
Validation stricte au démarrage
        |
        v
Comportement prévisible
        |
        v
Sécurité par défaut
        |
        v
Maintenance durable
```

Une application de veille SEO, GEO et IA manipule des informations sensibles : configuration de sites, clés API externes, paramètres crawler, rapports stratégiques, résultats IA et données utilisateurs. La configuration doit donc être considérée comme un composant d'architecture à part entière.

### 1.3 Objectifs

| Objectif | Description |
|---|---|
| Centraliser | Regrouper les paramètres dans des points identifiés plutôt que les disperser. |
| Sécuriser | Garder secrets, clés API, tokens et mots de passe hors du dépôt Git. |
| Valider | Refuser une configuration critique absente ou incohérente dès le démarrage. |
| Séparer | Distinguer clairement développement, test, staging futur et production future. |
| Documenter | Chaque paramètre important doit avoir un rôle, un type, une sensibilité et une valeur attendue. |
| Préparer | Anticiper authentification, IA, crawler, rapports, CI/CD et production. |

### 1.4 Risques liés à une mauvaise configuration

| Risque | Conséquence possible |
|---|---|
| Secret dans Git | Compromission de clés API, comptes, tokens ou base de données. |
| URL codée en dur | Desktop ou backend difficile à déployer sur plusieurs environnements. |
| Valeur par défaut dangereuse | Debug actif en production, CORS trop ouvert, JWT faible. |
| Configuration dispersée | Maintenance fragile, comportements incohérents, bugs silencieux. |
| Absence de validation | Erreurs tardives, démarrage partiel, données incohérentes. |
| Logs contenant la configuration sensible | Fuite indirecte de secrets et non-conformité sécurité. |

### 1.5 Périmètres couverts

| Périmètre | Inclus |
|---|---|
| Backend | Paramètres FastAPI, settings, sécurité, logging, API, PostgreSQL. |
| Desktop | `desktop/core/config.py`, URL API, version, paramètres UI futurs. |
| API | Préfixe `/api/v1`, pagination, timeouts, CORS futur, request_id futur. |
| Base de données | URL PostgreSQL, pool futur, Alembic, environnements. |
| Sécurité | Secrets, JWT, clés API, CORS, HTTPS, debug, exports. |
| Logging | Niveaux, destinations, format structuré futur, rétention future. |
| Modules futurs | IA/GEO, crawler, rapports, import/export, configuration utilisateur. |

### 1.6 Périmètres non couverts

| Périmètre | Document de référence |
|---|---|
| Détail complet JWT/RBAC | `docs/architecture/AUTHENTICATION.md` |
| Contrat REST complet | `docs/architecture/API_ARCHITECTURE.md` |
| Modèles SQLAlchemy et migrations détaillées | `docs/architecture/DATABASE_ARCHITECTURE.md` |
| Journalisation détaillée | `docs/architecture/LOGGING.md` |
| Sécurité globale | `docs/architecture/SECURITY.md` |
| Architecture Desktop | `docs/architecture/DESKTOP_ARCHITECTURE.md` |

### 1.7 Principes directeurs

```text
Centralized Configuration
Secure Defaults
Environment Separation
Explicit Configuration
Validated Configuration
No Secrets in Git
Least Privilege
Operational Clarity
```

Ces principes doivent guider toute nouvelle variable, tout nouveau fichier de configuration, toute option d'environnement et toute évolution du module Administration.

---

## 2. Principes de configuration

La configuration doit être conçue comme un contrat interne. Un développeur doit pouvoir comprendre en quelques minutes où se trouve un paramètre, pourquoi il existe, s'il est sensible et comment il est validé.

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| Configuration centralisée | Réduire les divergences et faciliter la maintenance. | Backend dans `backend/app/core/`, Desktop dans `desktop/core/config.py`, variables d'environnement pour secrets. | Définir `API_BASE_URL` dans plusieurs pages Desktop. |
| Configuration explicite | Rendre le comportement lisible. | Variables nommées clairement : `DATABASE_URL`, `API_V1_PREFIX`, `LOG_LEVEL`. | Paramètres implicites cachés dans une fonction utilitaire. |
| Validation stricte | Détecter les erreurs avant exécution métier. | Fail fast si `DATABASE_URL` critique est absente en production. | Laisser l'application démarrer puis échouer au premier appel DB. |
| Valeurs par défaut sûres | Éviter les comportements dangereux par défaut. | `APP_DEBUG=false` hors développement, CORS restreint en production. | Debug actif par défaut. |
| Séparation des environnements | Éviter l'utilisation de données réelles en test. | Bases, secrets et clés API distincts par environnement. | Même base PostgreSQL pour dev et test. |
| Secrets hors dépôt | Protéger clés et mots de passe. | `.env` local non commité, secrets GitHub Actions futurs. | Commit d'une clé OpenAI ou d'une chaîne PostgreSQL. |
| Pas de configuration métier dispersée | Préserver l'architecture. | Les règles métier restent dans services, les paramètres dans settings. | Seuils SEO codés dans une route. |
| Pas d'URL codée en dur hors config | Permettre dev, staging, production. | Desktop utilise `API_BASE_URL` central. | `http://127.0.0.1:8000` dans chaque widget. |
| Compatibilité backend/Desktop | Maintenir le contrat REST. | API versionnée `/api/v1`, Desktop configurable. | Desktop dépendant d'un chemin interne backend. |
| Configuration testable | Garantir les comportements en CI future. | Fixtures et overrides de configuration. | Tests dépendants de secrets réels. |

### 2.1 Règles absolues

| Règle | Statut |
|---|---|
| Ne jamais commiter `.env`. | Obligatoire |
| Ne jamais commiter clé API, token, mot de passe, secret JWT ou chaîne de connexion réelle. | Obligatoire |
| Ne jamais lire PostgreSQL depuis le Desktop. | Obligatoire |
| Ne jamais placer de logique métier dans la configuration. | Obligatoire |
| Ne jamais dupliquer une URL API dans plusieurs widgets. | Obligatoire |
| Documenter tout nouveau paramètre significatif. | Obligatoire |

---

## 3. Vue d'ensemble de l'architecture de configuration

La configuration circule depuis les sources autorisées vers les composants applicatifs. Elle ne doit pas être reconstruite localement dans chaque module.

### 3.1 Vue backend

```text
.env / variables système
        |
        v
Backend settings
        |
        v
FastAPI
        |
        v
Routes / Services / Repositories / API
        |
        v
PostgreSQL / Connecteurs futurs
```

### 3.2 Vue Desktop

```text
desktop/core/config.py
        |
        v
Desktop PySide6
        |
        v
ApiClient
        |
        v
FastAPI /api/v1
```

### 3.3 Vue logique

```text
Sources de configuration
    |
    +-- Variables d'environnement
    +-- .env local non commité
    +-- Constantes Desktop publiques
    +-- Paramètres base non sensibles futurs
    |
    v
Validation et normalisation
    |
    v
Consommateurs
    |
    +-- FastAPI
    +-- Services backend
    +-- Repositories via session DB
    +-- ApiClient Desktop
    +-- Logging futur
    +-- Connecteurs IA/GEO futurs
```

### 3.4 Vue physique

```text
repository/
├── backend/
│   └── app/
│       └── core/
│           └── settings futurs
├── desktop/
│   └── core/
│       ├── config.py
│       ├── api_client.py
│       └── constants.py
├── docs/
│   └── architecture/
│       └── CONFIGURATION.md
└── .env                (local, jamais commité)
```

### 3.5 Vue des secrets

```text
Secret réel
   |
   +-- .env local
   +-- variable système
   +-- GitHub Actions secret futur
   |
   v
Chargement contrôlé
   |
   v
Objet settings backend
   |
   +-- Jamais affiché en clair
   +-- Jamais logué
   +-- Jamais exporté
```

### 3.6 Vue des paramètres publics

```text
Paramètre public
   |
   +-- APP_NAME
   +-- APP_VERSION
   +-- API_V1_PREFIX
   +-- Pagination par défaut
   +-- Thème UI futur
   |
   v
Documentation
   |
   v
Utilisation directe autorisée si centralisée
```

### 3.7 Vue par environnement

```text
Développement
    |
    +-- secrets locaux fictifs ou personnels
    +-- debug possible
    +-- logs console

Test
    |
    +-- secrets factices
    +-- base isolée
    +-- comportements déterministes

Staging futur
    |
    +-- secrets dédiés
    +-- données non critiques
    +-- configuration proche production

Production future
    |
    +-- secrets forts
    +-- debug interdit
    +-- CORS restreint
    +-- logs sans données sensibles
```

### 3.8 Cycle de chargement

```text
Lecture sources
      |
      v
Fusion selon priorité
      |
      v
Validation types et cohérence
      |
      v
Masquage secrets pour logs
      |
      v
Publication settings
      |
      v
Démarrage application
```

---

## 4. Types de configuration

Chaque paramètre doit appartenir à une catégorie. Cette classification évite de mélanger configuration technique, préférences utilisateur, secrets et règles métier.

| Type de configuration | Exemple | Stockage recommandé | Sensibilité | Validation requise |
|---|---|---|---|---|
| Applicative | `APP_ENV`, `APP_NAME`, `APP_VERSION` | Settings backend ou config Desktop | Faible | Oui |
| Backend | `APP_DEBUG`, `ALLOWED_HOSTS` futur | Variables d'environnement / settings | Moyenne | Oui |
| Desktop | `API_BASE_URL`, thème futur | `desktop/core/config.py`, config locale future | Faible à moyenne | Oui |
| API | `API_V1_PREFIX`, `DEFAULT_PAGE_SIZE` | Settings backend | Faible | Oui |
| Base de données | `DATABASE_URL` | `.env` / variable système | Élevée | Oui |
| Alembic | URL DB de migration | Variables d'environnement | Élevée | Oui |
| Authentification | `JWT_SECRET_KEY`, durées tokens | Secret manager futur / `.env` local | Critique | Oui |
| Sécurité | CORS, HTTPS, rate limit | Settings backend | Moyenne à élevée | Oui |
| Logging | `LOG_LEVEL`, format futur | Settings backend/Desktop | Faible | Oui |
| IA/GEO future | `OPENAI_API_KEY`, modèles | Secret store futur / `.env` | Critique | Oui |
| Crawler futur | timeout, user-agent, profondeur | Settings backend / DB non sensible | Moyenne | Oui |
| Rapports | formats export, taille max | Settings backend / DB | Moyenne | Oui |
| Import/export | version format, limites | Settings backend / DB | Moyenne | Oui |
| Utilisateur future | préférences UI | Base de données | Faible | Oui |
| Organisationnelle future | nom groupe, politiques | Base de données | Moyenne | Oui |

### 4.1 Matrice de classification rapide

| Question | Si oui | Stockage probable |
|---|---|---|
| Le paramètre contient-il un secret ? | Configuration sensible | `.env`, variable système, secret manager futur |
| Le paramètre change-t-il selon l'utilisateur ? | Préférence utilisateur | Base de données |
| Le paramètre influence-t-il le comportement technique global ? | Configuration applicative | Settings centralisés |
| Le paramètre est-il lié à l'UI Desktop ? | Configuration Desktop | `desktop/core/config.py` ou config locale future |
| Le paramètre est-il une règle métier ? | Règle métier | Service, pas fichier de configuration |

---

## 5. Configuration backend

Le backend est la source de vérité métier. Sa configuration doit être centralisée dans la couche `backend/app/core/` et consommée par les composants autorisés.

### 5.1 Emplacement attendu

| Emplacement | Rôle |
|---|---|
| `backend/app/core/` | Paramètres backend centralisés, settings futurs, sécurité, logging, DB. |
| `.env` local | Valeurs sensibles ou spécifiques environnement, jamais commit. |
| Variables système | Valeurs injectées par environnement ou CI/CD future. |
| Tests | Overrides contrôlés et secrets factices. |

### 5.2 Rôle de `backend/app/core/`

`backend/app/core/` doit contenir la configuration transversale du backend : settings, base de données, sécurité, logging et autres composants globaux. Il ne doit pas contenir de logique métier SEO, GEO, crawler ou rapports.

| Peut contenir | Ne doit jamais contenir |
|---|---|
| Settings applicatifs | Logique métier de création de rapport |
| Configuration DB | Requêtes SQL métier |
| Paramètres sécurité | Secrets codés en dur |
| Configuration logging | Routes FastAPI |
| Paramètres API globaux | Code Desktop |

### 5.3 Usage futur de settings Pydantic

Le projet pourra évoluer vers un objet settings typé, validé et centralisé. L'objectif est d'éviter les accès dispersés à `os.environ`.

Exemple conceptuel :

```python
class BackendSettings(BaseSettings):
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str
    log_level: str = "INFO"
```

Cet exemple est conceptuel. Toute implémentation réelle devra suivre les conventions du dépôt et être introduite dans un sprint dédié.

### 5.4 Paramètres backend attendus

| Paramètre | Rôle | Type | Défaut dev | Secret ? | Validation |
|---|---|---|---|---|---|
| `APP_ENV` | Environnement courant | enum string | `development` | Non | Valeur connue |
| `APP_DEBUG` | Mode debug | bool | `true` possible en dev | Non | Interdit en prod |
| `APP_NAME` | Nom application backend | string | Projet | Non | Non vide |
| `APP_VERSION` | Version backend | string | `0.1.0` | Non | SemVer recommandé |
| `API_V1_PREFIX` | Préfixe API | string | `/api/v1` | Non | Commence par `/api/` |
| `DATABASE_URL` | Connexion PostgreSQL | string | local | Oui | URL valide |
| `LOG_LEVEL` | Niveau de log | enum | `INFO` | Non | Niveau autorisé |
| `CORS_ALLOWED_ORIGINS` futur | Origines autorisées | list | local | Non | Restreint en prod |
| `JWT_SECRET_KEY` futur | Signature JWT | string | secret dev | Oui | Longueur forte |

### 5.5 Règles backend

| Règle | Justification |
|---|---|
| Les routes ne lisent pas directement `.env`. | Elles doivent dépendre de settings centralisés ou de dépendances. |
| Les services ne construisent pas les URLs externes en dur. | Les connecteurs futurs doivent recevoir une configuration validée. |
| Les repositories ne connaissent pas l'environnement. | Ils reçoivent une session SQLAlchemy déjà configurée. |
| Les tests utilisent une configuration isolée. | Éviter l'écriture dans une base réelle. |

---

## 6. Configuration Desktop

Le Desktop PySide6 est un client graphique léger. Il communique exclusivement avec le backend via HTTP REST et ne doit jamais contenir d'accès PostgreSQL.

### 6.1 Fichier officiel

`desktop/core/config.py` est le point actuel de configuration Desktop. Il centralise au minimum :

| Paramètre Desktop | Rôle | Valeur actuelle | Valeur future | Sensibilité |
|---|---|---|---|---|
| `APP_NAME` | Nom affiché dans la fenêtre Desktop | `Veille SEO-GEO Groupe A.P&Partner` | Stable | Faible |
| `APP_VERSION` | Version Desktop | `0.1.0` | Versionnée par release | Faible |
| `API_BASE_URL` | URL de base API REST | `http://127.0.0.1:8000/api/v1` | Configurable par environnement | Moyenne |
| `REQUEST_TIMEOUT` futur | Timeout HTTP ApiClient | Non défini | 5 à 15 secondes | Faible |
| `THEME_NAME` futur | Thème UI | sombre | multi-thèmes | Faible |
| `WINDOW_SIZE` futur | Taille fenêtre par défaut | non centralisé | configurable | Faible |

### 6.2 Règles Desktop

| Règle | Application |
|---|---|
| Les pages UI ne codent pas l'URL API en dur. | Elles utilisent `ApiClient`, lui-même configuré depuis `config.py`. |
| Le Desktop ne stocke pas de secrets en clair. | Les tokens futurs devront utiliser un stockage sécurisé adapté. |
| Le Desktop ne lit jamais `.env` backend. | La configuration Desktop reste séparée. |
| Le Desktop affiche des erreurs propres si l'API est absente. | Pas de crash lors d'un backend indisponible. |
| Les paramètres UI suivent `docs/UI_UX.md`. | Cohérence visuelle et fonctionnelle. |

### 6.3 Configuration locale future

Une configuration Desktop locale pourra être ajoutée dans un sprint futur pour gérer :

| Paramètre futur | Exemple | Raison |
|---|---|---|
| URL API distante | `https://veille-api.internal/api/v1` | Connexion à un serveur partagé. |
| Thème | `dark` | Préférences utilisateur. |
| Taille fenêtre | `1440x900` | Confort utilisateur. |
| Dernière page ouverte | `dashboard` | Productivité. |
| Langue future | `fr-FR` | Internationalisation éventuelle. |

Cette configuration locale ne doit pas contenir de secrets non protégés.

---

## 7. Configuration API

L'API REST est le contrat stable entre le Desktop, Swagger/OpenAPI et les futurs clients HTTP.

### 7.1 Paramètres API

| Paramètre API | Rôle | Défaut recommandé | Sensibilité | Document lié |
|---|---|---|---|---|
| `API_V1_PREFIX` | Préfixe de version | `/api/v1` | Faible | `API_ARCHITECTURE.md` |
| `DEFAULT_PAGE_SIZE` | Taille page défaut | `20` | Faible | `API_ARCHITECTURE.md` |
| `MAX_PAGE_SIZE` | Limite page | `100` | Faible | `API_ARCHITECTURE.md` |
| `API_TIMEOUT_SECONDS` futur | Timeout serveur externe | `30` | Faible | `BACKEND_ARCHITECTURE.md` |
| `REQUEST_ID_HEADER` futur | Nom header request id | `X-Request-ID` | Faible | `LOGGING.md` |
| `RATE_LIMIT_ENABLED` futur | Activer limitation | `true` en prod | Faible | `SECURITY.md` |
| `CORS_ALLOWED_ORIGINS` futur | Origines autorisées | restreint | Moyenne | `SECURITY.md` |

### 7.2 Pagination

Le format paginé officiel doit rester stable :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

| Champ | Source de configuration possible | Règle |
|---|---|---|
| `page` | Query parameter | Minimum 1 |
| `page_size` | Query parameter + défaut settings | Maximum contrôlé |
| `total` | Repository/service | Calcul cohérent avec filtres |
| `pages` | Service/API | Dérivé de `total` et `page_size` |
| `items` | Repository | Liste typée par schéma Pydantic |

### 7.3 CORS futur

| Environnement | CORS recommandé |
|---|---|
| Développement | Localhost Desktop/API si nécessaire. |
| Test | Désactivé ou strict selon tests. |
| Staging futur | Origines staging uniquement. |
| Production future | Origines explicitement autorisées, jamais wildcard. |

---

## 8. Configuration base de données

La base PostgreSQL est la source persistante des données métier. Sa configuration est sensible et doit rester hors Git.

### 8.1 Paramètres DB

| Paramètre DB | Exemple | Secret ? | Environnement | Commentaire |
|---|---|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://user:***@localhost:5432/veille` | Oui | Tous | Chaîne complète jamais commitée. |
| `DB_HOST` futur | `localhost` | Non seul | Tous | Peut être séparé si pas d'URL complète. |
| `DB_PORT` futur | `5432` | Non | Tous | Valeur standard PostgreSQL. |
| `DB_NAME` futur | `veille_dev` | Moyenne | Tous | Peut révéler environnement. |
| `DB_USER` futur | `veille_app` | Moyenne | Tous | Ne suffit pas seul mais reste sensible. |
| `DB_PASSWORD` futur | `********` | Oui | Tous | Jamais logué. |
| `DB_POOL_SIZE` futur | `5` | Non | Prod future | À calibrer selon charge. |
| `DB_ECHO_SQL` futur | `false` | Non | Dev seulement | Interdit en production. |

### 8.2 Chaîne de connexion

La chaîne de connexion complète ne doit jamais être commitée, affichée en clair dans les logs ou exposée dans une erreur utilisateur.

Exemple conceptuel interdit dans Git :

```text
DATABASE_URL=postgresql+psycopg://real_user:real_password@prod-host:5432/prod_db
```

Exemple conceptuel autorisé dans un `.env.example` futur :

```env
DATABASE_URL=postgresql+psycopg://veille_user:change_me@localhost:5432/veille_dev
```

### 8.3 Echo SQL

| Environnement | `DB_ECHO_SQL` |
|---|---|
| Développement | Possible temporairement, avec prudence. |
| Test | Généralement désactivé sauf diagnostic. |
| Staging futur | Désactivé par défaut. |
| Production future | Interdit. |

---

## 9. Configuration Alembic

Alembic versionne l'évolution du schéma PostgreSQL. Sa configuration doit utiliser les mêmes sources sécurisées que le backend pour accéder à la base.

### 9.1 Règles Alembic

| Règle | Justification |
|---|---|
| Les migrations ne contiennent pas de secrets. | Une migration est commitée, donc publique au dépôt. |
| La connexion DB vient de l'environnement. | Évite de figer une base dans le code. |
| Les migrations restent explicites. | Cohérence avec `DATABASE_ARCHITECTURE.md`. |
| Les migrations ne contiennent pas de configuration métier. | Elles structurent la base, pas les comportements applicatifs. |

### 9.2 Interdictions

Les migrations Alembic ne doivent jamais utiliser :

```python
Base.metadata.create_all()
Base.metadata.drop_all()
```

Elles doivent utiliser des instructions explicites :

```python
op.create_table(...)
op.create_index(...)
op.drop_index(...)
op.drop_table(...)
```

### 9.3 Variables nécessaires

| Variable | Usage | Secret | Source |
|---|---|---|---|
| `DATABASE_URL` | Connexion migration | Oui | `.env` local ou variable système |
| `APP_ENV` | Contrôle environnement | Non | Variable système |
| `ALEMBIC_CONFIG` futur | Chemin config | Non | CLI ou environnement |

---

## 10. Configuration authentification

L'authentification future s'appuiera sur les règles définies dans `AUTHENTICATION.md`. Ce document ne duplique pas l'architecture JWT/RBAC, mais précise les paramètres à configurer.

| Paramètre auth | Sensibilité | Valeur dev | Valeur prod future | Stockage |
|---|---|---|---|---|
| `JWT_SECRET_KEY` | Critique | Secret local fort | Secret long, rotatable | Secret store futur / variable système |
| `JWT_ALGORITHM` | Faible | `HS256` possible | Selon décision architecture | Settings |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Moyenne | `15` à `60` | Court | Settings |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Moyenne | `7` à `30` | Selon politique | Settings |
| `JWT_ISSUER` | Faible | `veille-seo-geo` | Valeur officielle | Settings |
| `JWT_AUDIENCE` | Faible | `veille-desktop` | Clients autorisés | Settings |
| `PASSWORD_MIN_LENGTH` | Faible | `12` | `12+` | Settings |
| `LOGIN_RATE_LIMIT` futur | Moyenne | souple | strict | Settings |
| `MFA_ENABLED` futur | Faible | `false` | selon déploiement | Settings |

### 10.1 Règles

| Règle | Description |
|---|---|
| Le secret JWT n'est jamais codé en dur. | Il doit provenir d'une source sécurisée. |
| Les durées de tokens sont configurables. | Elles peuvent évoluer sans modifier la logique métier. |
| Les politiques de mot de passe sont centralisées. | Elles doivent être testables et documentées. |
| Les paramètres d'auth ne sont pas exportés en clair. | Le module Administration doit masquer ou exclure les secrets. |

---

## 11. Configuration sécurité

La sécurité dépend fortement de paramètres correctement séparés par environnement.

### 11.1 Matrice sécurité par environnement

| Paramètre | Dev | Test | Staging futur | Production future |
|---|---|---|---|---|
| `APP_DEBUG` | Possible | `false` recommandé | `false` | `false` obligatoire |
| HTTPS | Optionnel local | Non requis | Requis | Obligatoire |
| CORS | Local restreint | Restreint | Restreint | Jamais wildcard |
| JWT secret | Local fort | Factice fort | Dédié | Fort, rotatable |
| Rate limiting | Optionnel | Testable | Activé | Activé |
| Admin par défaut | Possible local | Factice | Contrôlé | Désactivé/changé |
| Logs sensibles | Interdits | Interdits | Interdits | Interdits |
| Exports secrets | Interdits | Interdits | Interdits | Interdits |

### 11.2 Paramètres sécurité futurs

| Paramètre | Rôle | Sensibilité | Règle |
|---|---|---|---|
| `CORS_ALLOWED_ORIGINS` | Limiter clients web futurs | Moyenne | Liste explicite |
| `HTTPS_ONLY` | Imposer HTTPS | Faible | `true` en prod |
| `SECURE_COOKIES` futur | Cookies auth si utilisés | Faible | `true` en prod |
| `RATE_LIMIT_PER_MINUTE` | Limiter abus API | Faible | Défaut prudent |
| `MAINTENANCE_MODE` futur | Bloquer usage temporaire | Faible | Message propre |
| `EXPORT_MAX_ROWS` | Limiter fuite données | Moyenne | Contrôle par rôle |

---

## 12. Configuration logging

La configuration du logging doit suivre `LOGGING.md`. Elle doit favoriser des logs utiles, corrélables et sans secrets.

| Paramètre logging | Dev | Test | Prod future | Risque |
|---|---|---|---|---|
| `LOG_LEVEL` | `DEBUG` possible | `WARNING` ou `INFO` | `INFO` | Trop bavard si mal réglé |
| `LOG_FORMAT` futur | texte ou JSON | JSON testable | JSON structuré | Incohérence d'analyse |
| `LOG_DESTINATION` futur | console | console | console/service central | Fuite fichier local |
| `AUDIT_ENABLED` futur | possible | actif tests | actif | Audit manquant |
| `LOG_RETENTION_DAYS` futur | faible | faible | défini | Conservation excessive |
| `REQUEST_ID_ENABLED` futur | actif | actif | actif | Diagnostic difficile sinon |

### 12.1 Logs de démarrage autorisés

| Champ | Log autorisé ? | Forme |
|---|---|---|
| `APP_ENV` | Oui | valeur claire |
| `APP_VERSION` | Oui | valeur claire |
| `API_V1_PREFIX` | Oui | valeur claire |
| `DATABASE_URL` | Non en clair | valeur masquée ou statut présent/absent |
| `JWT_SECRET_KEY` | Non | jamais |
| Clés IA | Non | jamais |

---

## 13. Configuration IA/GEO future

Les modules IA et GEO utiliseront des fournisseurs externes. Leur configuration est sensible car elle implique clés API, quotas, coûts, modèles et potentiellement données internes envoyées à des services tiers.

| Plateforme | Paramètres | Secret ? | Stockage recommandé | Risque principal |
|---|---|---|---|---|
| OpenAI | `OPENAI_API_KEY`, modèle, timeout | Oui pour clé | Secret store futur / `.env` dev | Fuite clé, coût non maîtrisé |
| Gemini | `GEMINI_API_KEY`, modèle | Oui | Secret store futur / `.env` dev | Fuite clé |
| Claude | `ANTHROPIC_API_KEY`, modèle | Oui | Secret store futur / `.env` dev | Fuite prompts |
| Copilot | clé ou intégration future | Oui | À définir | Contrat API évolutif |
| Perplexity | `PERPLEXITY_API_KEY`, modèle | Oui | Secret store futur / `.env` dev | Quotas |
| Google Search Console | client id/secret | Oui partiel | Secret store futur | OAuth |
| GA4 | credentials | Oui | Secret store futur | Données analytiques |
| Services SEO externes | token | Oui | Secret store futur | Fuite données concurrentielles |

### 13.1 Paramètres IA/GEO non secrets

| Paramètre | Exemple | Usage |
|---|---|---|
| `AI_DEFAULT_TIMEOUT_SECONDS` | `60` | Limiter appels longs. |
| `AI_MAX_RETRIES` | `2` | Contrôler retry. |
| `AI_DEFAULT_MODEL` | `gpt-*` conceptuel | Modèle par défaut. |
| `GEO_RESULT_RETENTION_DAYS` futur | `365` | Historisation. |
| `AI_STORE_RESPONSES` futur | `true/false` | Politique stockage. |

### 13.2 Règles IA/GEO

| Règle | Description |
|---|---|
| Les clés API ne sont jamais stockées dans Git. | Même pour environnement de test. |
| Les prompts sensibles ne sont pas logués en clair. | Voir `LOGGING.md`. |
| Les quotas doivent être configurables. | Éviter coûts non maîtrisés. |
| Les erreurs fournisseur sont normalisées. | Ne pas exposer de réponse brute sensible. |

---

## 14. Configuration crawler future

Le crawler devra être strictement configurable pour éviter les surcharges, les timeouts et les comportements imprévisibles.

| Paramètre crawler | Rôle | Défaut recommandé | Sensibilité | Validation |
|---|---|---|---|---|
| `CRAWLER_USER_AGENT` | Identifier le crawler | `VeilleSEO-GEOBot/0.1` | Faible | Non vide |
| `CRAWLER_TIMEOUT_SECONDS` | Timeout HTTP | `15` | Faible | > 0 |
| `CRAWLER_MAX_DEPTH` | Profondeur max | `3` | Faible | borné |
| `CRAWLER_MAX_PAGES` | Limite pages | `500` | Faible | borné |
| `CRAWLER_RESPECT_ROBOTS` futur | Respect robots.txt | `true` | Faible | bool |
| `CRAWLER_CONCURRENCY` | Parallélisme | `2` à `5` | Faible | limite |
| `CRAWLER_DELAY_MS` | Délai requêtes | `500` | Faible | >= 0 |
| `CRAWLER_MAX_PAGE_SIZE_MB` | Taille max page | `5` | Faible | limite |
| `CRAWLER_STORE_HTML` futur | Stockage HTML | `false` par défaut | Moyenne | politique |

### 14.1 Flux crawler configurable

```text
Configuration crawler
        |
        v
Validation limites
        |
        v
Crawler service futur
        |
        v
Requêtes HTTP externes
        |
        v
Résultats normalisés
        |
        v
Repositories / PostgreSQL
```

---

## 15. Configuration rapports future

Les rapports SEO, GEO et IA peuvent contenir des données stratégiques. Leur configuration doit contrôler formats, volume, conservation et sécurité.

| Paramètre rapport | Rôle | Défaut recommandé | Risque |
|---|---|---|---|
| `REPORT_EXPORT_FORMATS` | Formats autorisés | `pdf,csv` futur | Format non maîtrisé |
| `REPORT_MAX_ROWS` | Limite export | `10000` | Exfiltration volumineuse |
| `REPORT_TEMP_DIR` | Répertoire temporaire | système temp | Fuite fichiers |
| `REPORT_RETENTION_DAYS` | Conservation | à définir | Conservation excessive |
| `REPORT_WATERMARK_ENABLED` futur | Marquage rapports | `true` en prod | Partage non tracé |
| `REPORT_DOWNLOAD_TOKEN_TTL` futur | Accès téléchargement | court | URL persistante |

### 15.1 Règles

| Règle | Justification |
|---|---|
| Les exports ne doivent pas contenir de secrets. | Éviter fuite de clés ou tokens. |
| Les rapports sensibles nécessitent permission. | Respect RBAC futur. |
| Les fichiers temporaires doivent expirer. | Limiter exposition locale. |
| Les téléchargements doivent être audités. | Traçabilité. |

---

## 16. Configuration import/export

Le module Administration permet ou permettra d'importer et d'exporter de la configuration. Cette fonctionnalité doit être non destructive, versionnée et sécurisée.

### 16.1 Objectifs

| Objectif | Description |
|---|---|
| Idempotence | Réimporter le même fichier ne doit pas créer de doublons inattendus. |
| Non-destruction | L'import ne supprime pas de données sans option validée explicitement. |
| Validation | Le fichier importé est validé avant application. |
| Versionnement | Le format d'import/export porte une version. |
| Sécurité | Les secrets ne sont jamais exportés en clair. |
| Audit | Toute opération import/export est tracée. |

### 16.2 Format conceptuel d'export

```json
{
  "format_version": "1.0",
  "exported_at": "2026-06-29T10:15:30Z",
  "application": "Veille SEO-GEO Groupe A.P&Partner",
  "modules": {
    "websites": [],
    "entities": [],
    "configuration": {}
  },
  "secrets_included": false
}
```

### 16.3 Paramètres import/export

| Paramètre | Rôle | Défaut | Sensibilité |
|---|---|---|---|
| `CONFIG_EXPORT_VERSION` | Version format | `1.0` | Faible |
| `CONFIG_EXPORT_INCLUDE_SECRETS` | Inclusion secrets | `false` obligatoire | Critique |
| `CONFIG_IMPORT_DRY_RUN` futur | Simulation | `true` possible | Faible |
| `CONFIG_IMPORT_MAX_SIZE_MB` | Taille fichier | `10` | Faible |
| `CONFIG_EXPORT_PAGE_SIZE` | Pagination export | `1000` | Faible |

### 16.4 États import/export

| État | Comportement attendu |
|---|---|
| Fichier valide | Prévisualisation puis application contrôlée. |
| Version inconnue | Refus avec message clair. |
| Champ secret détecté | Refus ou masquage selon politique. |
| Conflit d'identifiant | Résolution documentée ou refus. |
| Import partiel | Transaction ou rapport d'échec clair. |

---

## 17. Environnements

La séparation des environnements évite que les tests, le développement ou la staging future n'affectent les données réelles.

| Environnement | Objectif | Données réelles | Secrets réels | Logs | Restrictions |
|---|---|---|---|---|---|
| Développement | Travail local | Non | Secrets locaux dédiés | Console, debug possible | Pas de données production |
| Test | Validation automatisée | Non | Fictifs | Réduits | Déterministe |
| Staging futur | Préproduction | Données anonymisées | Secrets dédiés | Structurés | Proche production |
| Production future | Usage interne stable | Oui | Secrets réels | Contrôlés | Sécurité maximale |

### 17.1 Configuration attendue par environnement

| Paramètre | Dev | Test | Staging futur | Production future |
|---|---|---|---|---|
| `APP_ENV` | `development` | `test` | `staging` | `production` |
| `APP_DEBUG` | possible `true` | `false` | `false` | `false` |
| `DATABASE_URL` | DB locale | DB test | DB staging | DB production |
| `LOG_LEVEL` | `DEBUG`/`INFO` | `WARNING`/`INFO` | `INFO` | `INFO`/`WARNING` |
| Clés IA | test/dédiées | factices | dédiées | production |
| CORS | local | strict | staging | strict |

### 17.2 Paramètres interdits en production

| Paramètre ou valeur | Raison |
|---|---|
| `APP_DEBUG=true` | Fuite d'information et comportement non durci. |
| `CORS_ALLOWED_ORIGINS=*` | Exposition excessive. |
| `DB_ECHO_SQL=true` | Risque de logs sensibles. |
| Secrets faibles ou exemple | Compromission. |
| Base de test | Risque perte ou incohérence. |

---

## 18. Variables d'environnement

Les variables d'environnement suivent une convention lisible : majuscules, `SNAKE_CASE`, noms explicites, pas d'ambiguïté.

### 18.1 Liste conceptuelle

| Variable | Rôle | Type | Obligatoire | Secret | Environnement | Défaut éventuel |
|---|---|---|---|---|---|---|
| `APP_ENV` | Environnement | enum | Oui | Non | Tous | `development` |
| `APP_DEBUG` | Debug | bool | Oui | Non | Tous | `false` |
| `DATABASE_URL` | Connexion DB | URL | Oui backend | Oui | Tous backend | Aucun en prod |
| `JWT_SECRET_KEY` | Signature JWT future | string | Oui auth | Oui | Tous auth | Aucun en prod |
| `JWT_ALGORITHM` | Algorithme JWT | string | Oui auth | Non | Tous auth | `HS256` conceptuel |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée access | int | Oui auth | Non | Tous auth | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Durée refresh | int | Oui auth | Non | Tous auth | `14` |
| `API_V1_PREFIX` | Préfixe API | string | Oui | Non | Tous | `/api/v1` |
| `LOG_LEVEL` | Niveau log | enum | Oui | Non | Tous | `INFO` |
| `OPENAI_API_KEY` | Clé OpenAI future | string | Si module actif | Oui | IA/GEO | Aucun |
| `GEMINI_API_KEY` | Clé Gemini future | string | Si module actif | Oui | IA/GEO | Aucun |
| `GOOGLE_SEARCH_CONSOLE_CLIENT_ID` | OAuth GSC futur | string | Si module actif | Moyen | SEO | Aucun |
| `GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET` | OAuth GSC futur | string | Si module actif | Oui | SEO | Aucun |

### 18.2 Convention de nommage

| Type | Convention | Exemple correct | Exemple interdit |
|---|---|---|---|
| Environnement | `APP_*` | `APP_ENV` | `ENVIRONMENT_MODE_UNCLEAR` |
| Base de données | `DATABASE_*` ou `DB_*` | `DATABASE_URL` | `POSTGRES_PASSWORD_IN_CODE` |
| JWT | `JWT_*` | `JWT_SECRET_KEY` | `SECRET` |
| API | `API_*` | `API_V1_PREFIX` | `ROUTE_BASE` |
| Logging | `LOG_*` | `LOG_LEVEL` | `VERBOSE` |
| IA | fournisseur explicite | `OPENAI_API_KEY` | `AI_KEY` |

### 18.3 Exemple conceptuel `.env` local

```env
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg://veille_user:change_me@localhost:5432/veille_dev
JWT_SECRET_KEY=change_me_local_secret_only
```

Cet exemple est conceptuel. Un fichier `.env` réel ne doit jamais être commité.

---

## 19. Fichiers `.env`

Le fichier `.env` sert à stocker les paramètres locaux sensibles ou dépendants d'un environnement. Il doit être exclu du dépôt.

| Fichier | Commit autorisé ? | Contenu | Remarques |
|---|---|---|---|
| `.env` | Non | Secrets et valeurs locales | Doit rester local. |
| `.env.local` futur | Non | Overrides développeur | Jamais commit. |
| `.env.test` futur | Non par défaut | Valeurs test locales | Éviter secrets réels. |
| `.env.example` futur | Oui | Valeurs fictives uniquement | Peut documenter les variables. |
| `.env.production` | Non | Secrets production | Interdit dans Git. |

### 19.1 Règles `.env`

| Règle | Description |
|---|---|
| Ne jamais commiter `.env`. | Même si les valeurs semblent temporaires. |
| Ne jamais mettre de secret réel dans `.env.example`. | Utiliser `change_me` ou valeurs fictives. |
| Ne jamais logger le contenu `.env`. | Même en debug. |
| Séparer les environnements. | Une base de test ne doit pas pointer vers production. |
| Faire tourner les secrets compromis. | Toute fuite implique rotation immédiate. |

---

## 20. Configuration par défaut

Les valeurs par défaut doivent faciliter le développement sans affaiblir la production.

| Paramètre | Défaut autorisé ? | Défaut recommandé | Risque |
|---|---|---|---|
| `APP_ENV` | Oui | `development` | Mauvais environnement si non explicite. |
| `APP_DEBUG` | Oui | `false` | Debug en production si défaut dangereux. |
| `API_V1_PREFIX` | Oui | `/api/v1` | Contrat API incohérent. |
| `DEFAULT_PAGE_SIZE` | Oui | `20` | Réponses trop lourdes. |
| `MAX_PAGE_SIZE` | Oui | `100` | Exports involontaires. |
| `DATABASE_URL` | Non en prod | Aucun | Connexion mauvaise base. |
| `JWT_SECRET_KEY` | Non en prod | Aucun | Secret faible. |
| `LOG_LEVEL` | Oui | `INFO` | Logs trop bavards. |
| `CORS_ALLOWED_ORIGINS` | Non en prod | Liste explicite | Exposition. |

### 20.1 Valeurs par défaut dangereuses

| Valeur | Pourquoi elle est dangereuse |
|---|---|
| `APP_DEBUG=true` en production | Expose détails techniques. |
| `CORS_ALLOWED_ORIGINS=*` | Autorise trop de clients. |
| `JWT_SECRET_KEY=secret` | Facilement devinable. |
| `DATABASE_URL` pointant vers production en local | Risque de modification accidentelle. |
| `LOG_LEVEL=DEBUG` en production | Peut exposer des informations internes. |

---

## 21. Validation de configuration

La configuration critique doit être validée au démarrage. Une application mal configurée doit échouer tôt avec un message clair plutôt que démarrer dans un état incohérent.

### 21.1 Flux de validation

```text
Load config
    |
    v
Validate types
    |
    v
Validate required values
    |
    v
Validate environment rules
    |
    v
OK ?
    |
    +-- Yes -> Start app
    |
    +-- No  -> Fail fast with clean error
```

### 21.2 Validations attendues

| Type | Validation |
|---|---|
| URL | Format valide, schéma attendu, pas vide. |
| Booléen | Valeurs explicites `true/false`. |
| Entier | Bornes minimales et maximales. |
| Durée | Positive, cohérente avec politique sécurité. |
| Secret | Présent si requis, longueur minimale, pas valeur exemple en prod. |
| Environnement | Valeur dans liste autorisée. |
| Liste | Éléments non vides, format cohérent. |
| CORS | Pas de wildcard en production. |
| DB | URL présente et environnement cohérent. |

### 21.3 Matrice validation par criticité

| Criticité | Exemple | Comportement si invalide |
|---|---|---|
| Critique | `DATABASE_URL`, `JWT_SECRET_KEY` | Arrêt démarrage. |
| Élevée | CORS production, debug production | Arrêt démarrage ou erreur bloquante. |
| Moyenne | pagination max, timeout | Défaut sûr ou erreur selon contexte. |
| Faible | nom application, thème | Défaut sûr. |

---

## 22. Priorité de résolution

La résolution de configuration doit suivre un ordre prévisible.

### 22.1 Ordre officiel

1. Variables d'environnement.
2. `.env` local.
3. Fichier de configuration local futur.
4. Valeurs par défaut sûres.
5. Configuration base future pour paramètres non sensibles.

### 22.2 Diagramme

```text
Variables d'environnement
        |
        v
.env local non commité
        |
        v
Config locale future
        |
        v
Défauts sûrs
        |
        v
Config persistée non sensible future
```

### 22.3 Règles de conflit

| Situation | Résolution |
|---|---|
| Variable système et `.env` définissent la même clé | Variable système prioritaire. |
| Valeur absente mais défaut sûr existe | Utiliser défaut si non critique. |
| Valeur absente et critique | Refuser le démarrage. |
| Valeur présente mais invalide | Refuser ou corriger uniquement si règle documentée. |
| Paramètre secret présent en base | Refuser s'il n'est pas chiffré selon stratégie future. |

---

## 23. Configuration persistée en base

Certaines configurations peuvent être stockées en base, notamment les préférences utilisateur ou paramètres métier non secrets. La base ne doit pas devenir un coffre de secrets sans mécanisme de chiffrement.

| Type de paramètre | Stockage DB autorisé ? | Conditions | Risque |
|---|---|---|---|
| Préférences utilisateur | Oui | Non sensible | Faible |
| Options d'affichage | Oui | Valeurs validées | Faible |
| Paramètres SEO/GEO non secrets | Oui | Historisés si nécessaire | Moyen |
| Configuration rapports | Oui | Permissions admin | Moyen |
| Statut de modules | Oui | Contrôle admin | Faible |
| Clés API | Non en clair | Chiffrement futur requis | Critique |
| Tokens | Non en clair | Stockage sécurisé spécialisé | Critique |
| Mots de passe | Jamais en clair | Hash uniquement | Critique |
| JWT secret | Non | Variable système ou secret store | Critique |

### 23.1 Règles

| Règle | Description |
|---|---|
| Une configuration en base doit être validée. | Pas de valeur libre non contrôlée. |
| Les changements sensibles doivent être audités. | Voir `LOGGING.md` et `SECURITY.md`. |
| Les secrets ne sont pas exportés en clair. | Import/export administration doit exclure ou masquer. |
| Les paramètres critiques de démarrage ne dépendent pas uniquement de la base. | La base doit pouvoir démarrer avant de lire sa configuration. |

---

## 24. Configuration sensible

Une configuration sensible est toute valeur permettant un accès, une signature, une exfiltration, une élévation de privilège ou une connexion à un service.

### 24.1 Matrice des données sensibles

| Donnée sensible | Stockage autorisé | Affichage UI | Logging | Export |
|---|---|---|---|---|
| Mot de passe | Jamais en clair, hash uniquement | Jamais | Jamais | Jamais |
| Token d'accès | Stockage sécurisé futur | Masqué | Jamais | Jamais |
| Refresh token | Stockage sécurisé futur | Jamais | Jamais | Jamais |
| Clé API | Secret store futur / `.env` dev | Partiel masqué | Jamais | Jamais en clair |
| Secret JWT | Variable système / secret store | Jamais | Jamais | Jamais |
| Chaîne DB | `.env` / variable système | Jamais | Masquée seulement | Jamais |
| OAuth client secret | Secret store futur | Jamais | Jamais | Jamais |
| Certificat privé futur | Secret store | Jamais | Jamais | Jamais |

### 24.2 Formes autorisées de masquage

```text
sk-************************abcd
anthropic-****************efgh
postgresql://user:****@host:5432/db
user***@example.com
```

---

## 25. Gestion des clés API

Les clés API externes seront critiques pour les modules IA, GEO, SEO et analytics.

### 25.1 Cycle de vie

```text
Création clé
    |
    v
Stockage sécurisé
    |
    v
Validation de connexion
    |
    v
Utilisation via connecteur
    |
    v
Rotation périodique
    |
    v
Révocation si compromise
```

### 25.2 Règles par fournisseur

| Service | Clé | Stockage | Affichage | Audit |
|---|---|---|---|---|
| OpenAI | `OPENAI_API_KEY` | Secret store futur / `.env` dev | Masqué | Création, test, rotation |
| Gemini | `GEMINI_API_KEY` | Secret store futur / `.env` dev | Masqué | Création, test, rotation |
| Claude | `ANTHROPIC_API_KEY` | Secret store futur / `.env` dev | Masqué | Création, test, rotation |
| Copilot | à définir | Secret store futur | Masqué | Selon intégration |
| Perplexity | `PERPLEXITY_API_KEY` | Secret store futur / `.env` dev | Masqué | Création, test, rotation |
| Google Search Console | OAuth | Secret store futur | Masqué | Consentement, refresh |
| GA4 | credentials | Secret store futur | Masqué | Accès analytics |
| Services SEO | token | Secret store futur | Masqué | Accès externe |

### 25.3 Interdictions

| Interdiction | Raison |
|---|---|
| Clé API dans Git | Fuite immédiate. |
| Clé API dans logs | Fuite indirecte. |
| Clé API affichée en clair | Capture écran ou accès non autorisé. |
| Clé API exportée | Diffusion incontrôlée. |
| Clé API codée dans connecteur | Maintenance impossible et secret exposé. |

---

## 26. Configuration Desktop/API

Le contrat entre Desktop et backend repose sur `API_BASE_URL`, le préfixe versionné `/api/v1`, les timeouts et la gestion propre des erreurs.

### 26.1 Diagramme

```text
desktop/core/config.py
        |
        v
ApiClient
        |
        v
FastAPI /api/v1
        |
        v
Réponse JSON normalisée
        |
        v
Page Desktop
```

### 26.2 Paramètres du contrat

| Paramètre | Côté | Rôle |
|---|---|---|
| `API_BASE_URL` | Desktop | URL complète vers `/api/v1`. |
| `API_V1_PREFIX` | Backend | Préfixe route stable. |
| Timeout HTTP futur | Desktop | Éviter blocage UI. |
| Pagination | Backend/API/Desktop | Tables Desktop cohérentes. |
| Erreurs normalisées | Backend/API | Messages UI propres. |
| Auth Bearer future | Desktop/API | Sessions sécurisées. |

### 26.3 Erreurs attendues

| Situation | Comportement Desktop |
|---|---|
| API absente | Message propre, pas de crash. |
| URL mal configurée | État déconnecté, action corrective future. |
| Timeout | Message temporaire, possibilité de rafraîchir. |
| 401 futur | Session expirée, retour login. |
| 403 futur | Accès refusé, menu/action désactivé. |

---

## 27. Configuration et tests

Les tests ne doivent pas dépendre de secrets réels ni de ressources production.

### 27.1 Principes

| Principe | Application |
|---|---|
| Secrets factices | Les tests utilisent des valeurs non sensibles. |
| Base isolée | Une base de test séparée ou fixtures contrôlées. |
| Overrides explicites | La configuration test surcharge les valeurs critiques. |
| Tests déterministes | Pas de dépendance à une API externe réelle sans mock. |
| Nettoyage | Les données de test ne polluent pas dev/prod. |

### 27.2 Variables test

| Variable | Valeur test recommandée | Remarque |
|---|---|---|
| `APP_ENV` | `test` | Permet règles spécifiques. |
| `APP_DEBUG` | `false` | Sauf diagnostic. |
| `DATABASE_URL` | DB test | Jamais production. |
| `JWT_SECRET_KEY` | `test_secret_not_for_prod` | Facteur non réel. |
| `OPENAI_API_KEY` | valeur factice | Aucun appel réel. |

### 27.3 Commandes de validation

```powershell
py -m pytest
py -m ruff check .
```

### 27.4 Checklist tests configuration

- Vérifier que la configuration test ne pointe pas vers production.
- Vérifier que les secrets réels ne sont pas requis pour lancer les tests.
- Vérifier que les valeurs invalides produisent une erreur claire.
- Vérifier que les valeurs par défaut sont sûres.
- Vérifier que les tests ne loguent aucun secret.

---

## 28. Configuration et CI/CD futur

Même si une chaîne CI/CD complète n'est pas encore définie, la configuration doit anticiper GitHub Actions ou un système équivalent.

### 28.1 Principes CI/CD

| Élément | Règle |
|---|---|
| Secrets CI | Stockés dans le coffre de secrets CI, jamais dans le dépôt. |
| Variables non sensibles | Définies comme variables d'environnement CI. |
| Tests | Utilisent secrets factices ou services isolés. |
| Migrations | Exécutées avec URL DB dédiée à l'environnement. |
| Déploiement futur | Staging puis production avec validation. |
| Logs CI | Ne doivent pas afficher secrets. |

### 28.2 Flux futur

```text
Push branche
    |
    v
CI charge variables non sensibles
    |
    v
CI injecte secrets protégés si nécessaires
    |
    v
Tests / Ruff
    |
    v
Validation migrations
    |
    v
Déploiement futur contrôlé
```

---

## 29. Configuration et documentation

Chaque nouveau paramètre doit être documenté. La documentation évite les paramètres orphelins et les comportements implicites.

### 29.1 Checklist documentation

- Ajouter le paramètre dans le document d'architecture concerné.
- Préciser son rôle.
- Préciser son type.
- Préciser s'il est obligatoire.
- Préciser s'il est secret.
- Préciser sa valeur par défaut.
- Préciser les environnements concernés.
- Mettre à jour `.env.example` futur si applicable.
- Vérifier l'impact Desktop/API/backend.
- Ajouter une note de migration si le changement casse une configuration existante.

### 29.2 Tableau de documentation minimale

| Champ | Obligatoire |
|---|---|
| Nom du paramètre | Oui |
| Description | Oui |
| Type | Oui |
| Sensibilité | Oui |
| Défaut | Oui si applicable |
| Environnement | Oui |
| Validation | Oui |
| Document lié | Oui |

---

## 30. Configuration et observabilité

La configuration influence les logs, le monitoring futur et la capacité à diagnostiquer un incident.

### 30.1 Logs de configuration au démarrage

| Élément | Log recommandé | Exemple |
|---|---|---|
| Environnement | Oui | `APP_ENV=development` |
| Version | Oui | `APP_VERSION=0.1.0` |
| Préfixe API | Oui | `API_V1_PREFIX=/api/v1` |
| Niveau log | Oui | `LOG_LEVEL=INFO` |
| URL DB | Non en clair | `DATABASE_URL=present` |
| Secret JWT | Non | Jamais |
| Clé IA | Non | Jamais |

### 30.2 Erreurs de configuration observables

| Erreur | Log interne | Message utilisateur |
|---|---|---|
| `DATABASE_URL` absente | Paramètre requis manquant | Configuration backend invalide. |
| `API_BASE_URL` invalide | URL Desktop invalide | Backend inaccessible. |
| Secret faible en prod | Secret rejeté | Configuration sécurité invalide. |
| CORS wildcard prod | Règle prod violée | Configuration sécurité invalide. |

---

## 31. Configuration et sécurité Git

La configuration doit respecter les règles de sécurité Git définies dans `SECURITY.md`.

### 31.1 Fichiers interdits

| Élément | Statut |
|---|---|
| `.env` | Interdit au commit |
| Secrets | Interdits |
| Tokens | Interdits |
| Mots de passe | Interdits |
| Clés API | Interdites |
| Certificats privés | Interdits |
| Dumps de configuration sensibles | Interdits |
| Chaînes de connexion réelles | Interdites |

### 31.2 Commandes de vérification

```powershell
git status
git diff --stat
git diff --check
```

### 31.3 Checklist sécurité Git

- Vérifier qu'aucun `.env` n'est ajouté.
- Vérifier qu'aucune clé API n'apparaît dans le diff.
- Vérifier qu'aucun token n'apparaît dans le diff.
- Vérifier qu'aucune chaîne PostgreSQL réelle n'apparaît dans le diff.
- Vérifier que les exemples utilisent des valeurs fictives.
- Vérifier que les fichiers staged non liés ne sont pas modifiés.

---

## 32. Configuration et import/export administration

Le module Administration doit permettre d'importer et exporter des configurations non sensibles de manière contrôlée.

### 32.1 Règles fonctionnelles

| Règle | Description |
|---|---|
| Import non destructif | Ne supprime pas d'élément existant sans validation explicite. |
| Export paginé | Évite les fichiers massifs. |
| Idempotence | Réimport maîtrisé. |
| Validation | Le fichier est validé avant écriture. |
| Conflits | Les collisions sont listées. |
| Version du format | Chaque fichier indique sa version. |
| Secrets exclus | Aucun secret en clair dans l'export. |
| Audit | Opération tracée. |
| Permissions admin | Réservé aux profils autorisés. |

### 32.2 Flux import administration

```text
Fichier importé
      |
      v
Validation format
      |
      v
Validation sécurité
      |
      v
Détection conflits
      |
      v
Prévisualisation
      |
      v
Application transactionnelle
      |
      v
Audit
```

### 32.3 Champs exclus des exports

| Champ | Raison |
|---|---|
| Clés API | Secret critique. |
| Tokens | Accès utilisateur ou externe. |
| Mots de passe/hash inutiles | Données sensibles. |
| Secret JWT | Compromission auth. |
| Chaîne DB | Compromission base. |
| Refresh tokens | Compromission session. |

---

## 33. Gestion des erreurs de configuration

Les erreurs de configuration doivent être explicites pour les développeurs, mais ne doivent jamais exposer de secrets.

| Erreur | Gravité | Comportement attendu | Message |
|---|---|---|---|
| Variable manquante critique | Critique | Arrêt démarrage | `Configuration invalide : DATABASE_URL manquante.` |
| Valeur invalide | Élevée | Refus démarrage ou défaut sûr | `LOG_LEVEL doit être DEBUG, INFO, WARNING, ERROR ou CRITICAL.` |
| Secret absent | Critique | Arrêt si fonctionnalité active | `JWT_SECRET_KEY requis pour l'authentification.` |
| URL invalide | Élevée | Refus ou état déconnecté Desktop | `API_BASE_URL invalide.` |
| Environnement inconnu | Élevée | Refus démarrage | `APP_ENV doit être development, test, staging ou production.` |
| Clé API invalide | Moyenne | Désactiver fournisseur ou signaler | `Clé OpenAI non valide ou absente.` |
| DB inaccessible | Critique backend | Erreur santé / arrêt selon contexte | `Base de données indisponible.` |
| Configuration incohérente | Élevée | Refus | `APP_DEBUG=true interdit en production.` |
| Desktop API indisponible | Moyenne | Message UI propre | `Backend indisponible. Réessayez plus tard.` |

### 33.1 Diagramme de traitement

```text
Erreur configuration
        |
        v
Critique ?
        |
        +-- Oui -> Fail fast / message développeur propre
        |
        +-- Non -> Défaut sûr ou fonctionnalité désactivée
                    |
                    v
              Log sans secret
```

---

## 34. Anti-patterns interdits

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Secret dans le code | Fuite dans Git et historique. | Variable d'environnement ou secret store futur. |
| `.env` commit | Expose tous les secrets locaux. | `.env.example` avec valeurs fictives. |
| URL codée en dur partout | Déploiements fragiles. | Paramètre centralisé. |
| Configuration dispersée | Maintenance difficile. | Settings centralisés. |
| Clés API en base non chiffrées | Fuite via DB ou export. | Secret store/chiffrement futur. |
| Logs contenant configuration sensible | Fuite indirecte. | Masquage strict. |
| Export contenant secrets | Diffusion incontrôlée. | Exclusion ou masquage. |
| Valeur par défaut dangereuse | Sécurité affaiblie. | Défaut sûr et validation prod. |
| Debug activé en production | Exposition technique. | `APP_DEBUG=false`. |
| CORS wildcard en production | Surface d'attaque large. | Origines explicites. |
| Desktop avec accès direct DB | Violation architecture. | ApiClient HTTP REST uniquement. |
| Configuration modifiée sans documentation | Perte de traçabilité. | Mettre à jour docs et `.env.example` futur. |
| `os.environ` lu partout | Couplage et duplication. | Objet settings central. |
| Tests dépendants de secrets réels | Fragilité et fuite. | Secrets factices et mocks. |

---

## 35. Pattern officiel pour ajouter un paramètre

Tout nouveau paramètre doit suivre un cycle de décision documenté.

### 35.1 Étapes

1. Définir le besoin.
2. Classifier le paramètre.
3. Déterminer s'il est secret.
4. Choisir l'emplacement.
5. Définir la valeur par défaut.
6. Ajouter la validation.
7. Documenter.
8. Tester.
9. Vérifier les logs.
10. Vérifier l'export.
11. Vérifier la sécurité.

### 35.2 Checklist ajout de paramètre

- Le paramètre a un nom clair.
- Le type est défini.
- La sensibilité est définie.
- L'environnement concerné est défini.
- La valeur par défaut est sûre.
- La validation est prévue.
- Les logs ne l'exposent pas si sensible.
- L'import/export le traite correctement.
- Les tests n'ont pas besoin de secret réel.
- La documentation est mise à jour.

### 35.3 Exemple conceptuel

Besoin : ajouter un timeout pour les appels IA.

| Décision | Valeur |
|---|---|
| Nom | `AI_DEFAULT_TIMEOUT_SECONDS` |
| Type | entier |
| Secret | non |
| Défaut | `60` |
| Validation | entre 1 et 300 |
| Stockage | settings backend |
| Logs | valeur autorisée |
| Tests | vérifier valeur invalide |

---

## 36. Checklist avant Pull Request configuration

Cette checklist s'applique à toute Pull Request modifiant la configuration, les settings, les fichiers d'exemple ou les paramètres d'environnement.

### 36.1 Commandes

```powershell
git status
git diff --stat
git diff --check
py -m pytest
py -m ruff check .
```

### 36.2 Checklist

- Aucun secret n'est présent dans le diff.
- Aucun `.env` n'est ajouté.
- Aucune clé API n'est ajoutée.
- Aucune chaîne de connexion réelle n'est ajoutée.
- La documentation est mise à jour.
- Les paramètres sont validés.
- Les valeurs par défaut sont sûres.
- L'impact Desktop est vérifié.
- L'impact API est vérifié.
- L'impact backend est vérifié.
- L'impact base de données est vérifié.
- Les logs ne révèlent pas de valeur sensible.
- Les exports n'incluent pas de secret.
- Les tests passent.
- Ruff passe.

---

## 37. Roadmap configuration

La configuration évoluera par phases jusqu'à une version interne stable.

| Phase | Objectif | Résultat attendu |
|---|---|---|
| v0.1 | Configuration Desktop stabilisée | `APP_NAME`, `APP_VERSION`, `API_BASE_URL`. |
| v0.2 | Configuration backend centralisée | Settings backend cohérents. |
| v0.3 | `.env.example` futur | Documentation opérationnelle des variables. |
| v0.4 | Validation stricte | Fail fast sur paramètres critiques. |
| v0.5 | Configuration test | Environnement test isolé. |
| v0.6 | Import/export renforcé | Format versionné, secrets exclus. |
| v0.7 | Clés API sécurisées | Masquage, rotation, audit. |
| v0.8 | Multi-environnements | Dev/test/staging/prod clairement séparés. |
| v0.9 | Configuration UI | Préférences Desktop et profils. |
| v1.0 | Production-ready | Configuration stable, sécurisée, documentée. |

### 37.1 Principes de roadmap

| Principe | Application |
|---|---|
| Ne pas tout configurer trop tôt | Ajouter quand un module en a besoin. |
| Toujours documenter | Éviter les paramètres fantômes. |
| Sécuriser avant production | Secrets, CORS, debug, logs. |
| Préserver compatibilité Desktop | Toute évolution API doit être maîtrisée. |

---

## 38. Annexes

### 38.1 Glossaire

| Terme | Définition |
|---|---|
| Configuration | Ensemble de paramètres qui contrôlent le comportement technique ou applicatif. |
| Secret | Valeur qui donne accès à une ressource ou protège une signature. |
| `.env` | Fichier local de variables d'environnement, non commité. |
| Settings | Objet centralisé représentant la configuration validée. |
| Valeur par défaut | Valeur utilisée si aucun paramètre explicite n'est fourni. |
| Fail fast | Arrêt immédiat en cas de configuration critique invalide. |
| Secret store | Coffre de secrets futur pour production. |
| Environnement | Contexte d'exécution : dev, test, staging, production. |
| CORS | Politique contrôlant les origines HTTP autorisées. |

### 38.2 Abréviations

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| DB | Database |
| JWT | JSON Web Token |
| RBAC | Role-Based Access Control |
| IA | Intelligence Artificielle |
| GEO | Generative Engine Optimization |
| SEO | Search Engine Optimization |
| CI/CD | Continuous Integration / Continuous Deployment |

### 38.3 Modèle conceptuel `.env.example`

```env
# Application
APP_ENV=development
APP_DEBUG=false
APP_NAME=Veille SEO-GEO Groupe A.P&Partner
APP_VERSION=0.1.0

# API
API_V1_PREFIX=/api/v1
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Database
DATABASE_URL=postgresql+psycopg://veille_user:change_me@localhost:5432/veille_dev

# Authentication future
JWT_SECRET_KEY=change_me_with_a_strong_local_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14

# Logging
LOG_LEVEL=INFO

# AI providers future
OPENAI_API_KEY=change_me
GEMINI_API_KEY=change_me
ANTHROPIC_API_KEY=change_me
PERPLEXITY_API_KEY=change_me
```

Ce modèle est destiné à un futur `.env.example`. Les valeurs sont fictives et ne doivent pas être utilisées en production.

### 38.4 Matrice secrets

| Élément | Secret | Stockage dev | Stockage prod futur | Export |
|---|---|---|---|---|
| `DATABASE_URL` | Oui | `.env` | Secret store / variable système | Non |
| `JWT_SECRET_KEY` | Oui | `.env` | Secret store | Non |
| `OPENAI_API_KEY` | Oui | `.env` | Secret store | Non |
| `APP_VERSION` | Non | Code/settings | Code/settings | Oui |
| `API_V1_PREFIX` | Non | Settings | Settings | Oui |
| `LOG_LEVEL` | Non | Settings/env | Settings/env | Oui |

### 38.5 Matrice environnements

| Critère | Dev | Test | Staging futur | Prod future |
|---|---|---|---|---|
| Secrets réels | Non recommandé | Non | Dédiés | Oui |
| Données réelles | Non | Non | Anonymisées | Oui |
| Debug | Possible | Non | Non | Non |
| Logs debug | Possible | Rare | Contrôlé | Non |
| CORS wildcard | Éviter | Non | Non | Non |
| Tests auto | Oui | Oui | Oui | Avant déploiement |

### 38.6 Checklist rapide développeur

- Je sais où placer le paramètre.
- Je sais s'il est secret.
- Je sais sa valeur par défaut.
- Je sais comment il est validé.
- Je sais s'il doit être documenté dans `.env.example` futur.
- Je sais s'il peut être exporté.
- Je sais s'il peut être logué.
- Je sais quels environnements sont concernés.

### 38.7 Résumé architectural

```text
Configuration projet
    |
    +-- Backend settings
    |       |
    |       +-- API
    |       +-- DB
    |       +-- Security
    |       +-- Logging
    |       +-- IA/GEO future
    |
    +-- Desktop config
    |       |
    |       +-- APP_NAME
    |       +-- APP_VERSION
    |       +-- API_BASE_URL
    |
    +-- Secrets
    |       |
    |       +-- .env local
    |       +-- variables système
    |       +-- secret store futur
    |
    +-- Configuration DB future
            |
            +-- paramètres non sensibles
            +-- préférences utilisateur
            +-- options modules
```

### 38.8 Liens internes

| Document | Rôle |
|---|---|
| `docs/architecture/SECURITY.md` | Règles sécurité et secrets. |
| `docs/architecture/LOGGING.md` | Logs et observabilité. |
| `docs/architecture/AUTHENTICATION.md` | Authentification, JWT, RBAC. |
| `docs/architecture/API_ARCHITECTURE.md` | Contrat API et paramètres REST. |
| `docs/architecture/BACKEND_ARCHITECTURE.md` | Couches backend et responsabilités. |
| `docs/architecture/DATABASE_ARCHITECTURE.md` | PostgreSQL, SQLAlchemy, Alembic. |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | Desktop PySide6 et ApiClient. |
| `docs/UI_UX.md` | Identité UI/UX officielle. |
