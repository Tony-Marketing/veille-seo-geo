# Software Logging and Observability Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle de logging et d'observabilité  
Version du document : 1.0  
Statut : Référence technique logging, audit technique et observabilité  
Périmètre : Desktop, API, backend, services, repositories, PostgreSQL, IA/GEO futures, crawler futur, rapports, incidents  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes de logging](#2-principes-de-logging)
3. [Vue d'ensemble de l'architecture logging](#3-vue-densemble-de-larchitecture-logging)
4. [Typologie des logs](#4-typologie-des-logs)
5. [Niveaux de logs](#5-niveaux-de-logs)
6. [Format standard des logs](#6-format-standard-des-logs)
7. [Identifiants de corrélation](#7-identifiants-de-corrélation)
8. [Logging backend FastAPI](#8-logging-backend-fastapi)
9. [Logging API REST](#9-logging-api-rest)
10. [Logging Desktop PySide6](#10-logging-desktop-pyside6)
11. [Logging ApiClient](#11-logging-apiclient)
12. [Logging services métier](#12-logging-services-métier)
13. [Logging repositories et database](#13-logging-repositories-et-database)
14. [Logs de sécurité](#14-logs-de-sécurité)
15. [Logs d'audit](#15-logs-daudit)
16. [Logs d'erreur](#16-logs-derreur)
17. [Logs de performance](#17-logs-de-performance)
18. [Logs IA / GEO futurs](#18-logs-ia--geo-futurs)
19. [Logs crawler futurs](#19-logs-crawler-futurs)
20. [Logs rapports et exports](#20-logs-rapports-et-exports)
21. [Données interdites dans les logs](#21-données-interdites-dans-les-logs)
22. [Masquage et anonymisation](#22-masquage-et-anonymisation)
23. [Gestion des environnements](#23-gestion-des-environnements)
24. [Destinations des logs](#24-destinations-des-logs)
25. [Rétention des logs](#25-rétention-des-logs)
26. [Monitoring futur](#26-monitoring-futur)
27. [Alerting futur](#27-alerting-futur)
28. [Health checks](#28-health-checks)
29. [Observabilité des imports/exports](#29-observabilité-des-importsexports)
30. [Observabilité des migrations](#30-observabilité-des-migrations)
31. [Gestion des incidents](#31-gestion-des-incidents)
32. [Tests du logging](#32-tests-du-logging)
33. [Qualité et conventions](#33-qualité-et-conventions)
34. [Anti-patterns interdits](#34-anti-patterns-interdits)
35. [Pattern officiel pour ajouter un événement de log](#35-pattern-officiel-pour-ajouter-un-événement-de-log)
36. [Checklist avant Pull Request logging](#36-checklist-avant-pull-request-logging)
37. [Roadmap logging et observabilité](#37-roadmap-logging-et-observabilité)
38. [Annexes](#38-annexes)

---

## 1. Présentation

### 1.1 Rôle du document

Ce document définit la stratégie officielle de journalisation et d'observabilité de Veille SEO-GEO Groupe A.P&Partner.
Il décrit quoi logger, quoi ne jamais logger, comment structurer les événements, comment corréler Desktop, API,
backend, base de données et futurs appels IA/GEO, et comment préparer le monitoring, l'audit technique et l'analyse
d'incidents.

Il complète :

- `SECURITY.md` pour les règles de sécurité et les données interdites dans les logs ;
- `AUTHENTICATION.md` pour les événements d'identité, sessions, RBAC et révocation ;
- `API_ARCHITECTURE.md` pour `request_id`, erreurs API et réponses normalisées ;
- `BACKEND_ARCHITECTURE.md` pour les responsabilités des couches ;
- `DATABASE_ARCHITECTURE.md` pour les événements base, migrations et transactions ;
- `DESKTOP_ARCHITECTURE.md` pour les logs côté client Desktop.

### 1.2 Vision logging/observabilité

La vision est :

> Produire des logs structurés, minimaux, corrélables et actionnables, permettant de diagnostiquer un incident sans
> exposer de secret, de token, de mot de passe, de clé API ou de donnée métier sensible.

Les logs doivent aider à comprendre :

- une erreur API ;
- un timeout Desktop ;
- un refus de permission ;
- une erreur PostgreSQL ;
- un import configuration ;
- un export sensible ;
- un appel IA futur ;
- un crawl futur ;
- une migration ;
- un incident de production futur.

### 1.3 Objectifs

| Objectif | Description | Impact |
|---|---|---|
| Traceability | Suivre une requête de bout en bout | Debug rapide |
| Auditability | Tracer les actions sensibles | Conformité et sécurité |
| Privacy by Design | Minimiser les données loguées | Réduction fuite |
| Security by Design | Interdire secrets et tokens | Protection |
| Least Data Logging | Logger le nécessaire, pas plus | Moins de risque |
| Actionable Logs | Produire des logs utiles | Analyse incident |
| Structured Logs | Format machine-readable | Monitoring futur |

### 1.4 Risques d'une mauvaise journalisation

| Risque | Impact |
|---|---|
| Token dans log | Compromission de session |
| Clé API dans traceback | Fuite fournisseur externe |
| Payload complet de login | Exposition mot de passe |
| Logs sans request_id | Incident difficile à diagnostiquer |
| Logs trop bavards | Bruit, coût, fuite de données |
| Logs insuffisants | Impossibilité d'audit |
| Stack trace exposée à l'utilisateur | Fuite technique |
| Audit absent sur admin | Non-traçabilité |

### 1.5 Périmètres couverts

| Périmètre | Couvert |
|---|---:|
| Backend FastAPI | Oui |
| API REST | Oui |
| Desktop PySide6 | Oui |
| ApiClient | Oui |
| Services métier | Oui |
| Repositories/DB | Oui |
| Logs sécurité | Oui |
| Audit | Oui |
| IA/GEO future | Oui |
| Crawler futur | Oui |
| Monitoring/alerting futur | Oui |

### 1.6 Périmètres non couverts

Ce document ne définit pas encore :

- le choix final d'un outil SIEM ;
- une stack exacte Prometheus/Grafana/ELK ;
- les dashboards d'exploitation finaux ;
- une procédure SOC complète ;
- une politique juridique de rétention.

### 1.7 Principes clés

```text
Traceability
Auditability
Privacy by Design
Security by Design
Least Data Logging
Actionable Logs
Structured Logs
```

---

## 2. Principes de logging

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| Logs structurés | Exploitables par outils futurs | JSON conceptuel | messages libres impossibles à parser |
| Logs actionnables | Accélérer diagnostic | event code + contexte | "ça plante" |
| Logs minimaux | Réduire fuite et bruit | champs nécessaires | dump complet payload |
| Absence de secrets | Sécurité | masquage systématique | token dans log |
| Niveaux cohérents | Prioriser incidents | INFO/WARNING/ERROR | tout logger en ERROR |
| Horodatage systématique | Chronologie | timestamp UTC | logs sans date |
| Corrélation | Suivre requête | request_id/correlation_id | logs isolés |
| Types séparés | Clarté | technique, métier, sécurité, audit | tout mélanger |
| Message utilisateur séparé | Sécurité UX | erreur propre + log interne | stack trace UI |
| Rétention maîtrisée | RGPD/coût | règles par type | logs infinis |

### 2.2 Logs minimaux mais suffisants

Un bon log doit répondre à :

- quel événement ?
- quand ?
- où ?
- pour quelle ressource ?
- par quel acteur si disponible ?
- avec quel résultat ?
- comment retrouver la requête ?

Il ne doit pas contenir :

- secrets ;
- payloads complets sensibles ;
- dumps SQL complets ;
- informations personnelles inutiles.

### 2.3 Séparation des types

```text
Technical logs
  +-- erreurs, durée, santé

Business logs
  +-- website.created, report.generated

Security logs
  +-- permission.denied, token.invalid

Audit logs
  +-- action durable et consultable
```

---

## 3. Vue d'ensemble de l'architecture logging

### 3.1 Diagramme principal

```text
Desktop PySide6
      |
      | request_id futur
      v
FastAPI API /api/v1
      |
      v
Routes
      |
      v
Services
      |
      v
Repositories
      |
      v
PostgreSQL
      |
      v
Logs / Audit / Metrics futurs
```

### 3.2 Vue logique

```text
Log Sources
  |
  +-- Desktop
  +-- ApiClient
  +-- API routes
  +-- Services
  +-- Repositories
  +-- PostgreSQL
  +-- External APIs future

Log Types
  |
  +-- Technical
  +-- Business
  +-- Security
  +-- Audit
  +-- Performance

Observability Outputs
  |
  +-- Console dev
  +-- Files future
  +-- audit_logs table future
  +-- metrics future
  +-- alerts future
```

### 3.3 Vue physique

```text
Developer workstation
  |
  +-- Desktop logs local future
  +-- Backend console logs

Staging future
  |
  +-- structured backend logs
  +-- audit DB

Production future
  |
  +-- centralized logs
  +-- metrics
  +-- alerts
  +-- audit retention
```

### 3.4 Vue par responsabilités

| Couche | Responsabilité logging |
|---|---|
| Desktop | événements UI, réseau, états sans secrets |
| ApiClient | endpoint, méthode, durée, code HTTP |
| Route | request_id, statut, validation, erreurs API |
| Service | événements métier, audit déclenché |
| Repository | erreurs DB, requêtes lentes futures |
| Database | contraintes, indisponibilité, migrations |
| Security | refus permissions, auth future |
| Audit | événements durables et sensibles |

### 3.5 Cycle d'une requête loguée

```text
Desktop action
    |
    v
ApiClient adds request_id future
    |
    v
FastAPI receives request
    |
    v
Route logs request summary
    |
    v
Service logs business event if relevant
    |
    v
Repository logs DB error/performance if relevant
    |
    v
API logs response status + duration
    |
    v
Desktop logs UI state update if relevant
```

### 3.6 Flux d'audit

```text
Sensitive action
    |
    v
Service validates action
    |
    v
Business change persisted
    |
    v
Audit event created
    |
    v
audit_logs future
```

### 3.7 Événements sécurité

```text
Auth / permission / admin event
      |
      +-- security log
      |
      +-- audit log if durable action
      |
      +-- alert future if critical
```

---

## 4. Typologie des logs

### 4.1 Tableau

| Type de log | Objectif | Exemple | Destination future | Niveau typique |
|---|---|---|---|---|
| Technique | Diagnostiquer erreurs | `api.request.failed` | console/centralisé | ERROR |
| Applicatif | Suivre fonctionnement | `app.started` | console | INFO |
| Métier | Suivre action métier | `website.created` | backend logs | INFO |
| API | Suivre requêtes HTTP | `api.request.completed` | centralisé | INFO |
| Sécurité | Détecter abus | `permission.denied` | sécurité/alerting | WARNING |
| Audit | Trace durable | `role.updated` | DB audit | INFO |
| Desktop | Diagnostiquer client | `desktop.api.timeout` | local futur | WARNING |
| Database | Diagnostiquer DB | `db.transaction.rollback` | backend logs | ERROR |
| Crawler futur | Suivre crawls | `crawler.job.completed` | centralisé | INFO |
| IA/GEO futur | Suivre appels modèles | `ai.call.failed` | centralisé | WARNING |
| Configuration | Changements settings | `config.import.completed` | audit/logs | INFO |
| Performance | Mesurer latence | `api.slow_request` | metrics/logs | WARNING |
| Incident | Analyse critique | `security.secret_leak_detected` | alerting | CRITICAL |

### 4.2 Différence log vs audit

| Log | Audit |
|---|---|
| Diagnostic technique | Trace durable |
| Peut être temporaire | Conservation plus longue |
| Peut être agrégé | Doit être consultable |
| Peut contenir erreur technique redacted | Ne contient jamais secret |
| Sert aux développeurs | Sert sécurité, admin, conformité |

---

## 5. Niveaux de logs

### 5.1 Tableau complet

| Niveau | Signification | Usage autorisé | Usage interdit | Exemple projet | Environnement |
|---|---|---|---|---|---|
| DEBUG | Diagnostic détaillé | dev local contrôlé | production standard | paramètres pagination sans secret | dev |
| INFO | Événement normal | démarrage, action métier réussie | bruit par ligne traitée massive | `website.created` | tous |
| WARNING | Situation anormale récupérable | retry, permission refusée, API lente | erreur critique silencieuse | `api.external.timeout` | tous |
| ERROR | Échec opération | exception, 500, DB rollback | secrets/stack côté user | `db.commit.failed` | tous |
| CRITICAL | Incident majeur | DB indisponible, secret leak suspect | usage fréquent | `app.startup.failed` | tous |

### 5.2 Règles

- DEBUG interdit en production sauf contexte temporaire contrôlé.
- ERROR ne doit pas exposer de données sensibles.
- CRITICAL doit être rare, actionnable et surveillé.
- WARNING est adapté aux comportements suspects ou dégradés.
- INFO doit rester utile, pas bavard.

---

## 6. Format standard des logs

### 6.1 Format JSON conceptuel

```json
{
  "timestamp": "2026-06-29T10:15:30Z",
  "level": "INFO",
  "service": "backend",
  "module": "websites",
  "event": "website.created",
  "message": "Website created",
  "request_id": "req_...",
  "correlation_id": "corr_...",
  "user_id": 1,
  "resource_type": "website",
  "resource_id": 12,
  "duration_ms": 34
}
```

### 6.2 Champs

| Champ | Statut | Source | Description |
|---|---|---|---|
| `timestamp` | Obligatoire | logger | UTC ISO 8601 |
| `level` | Obligatoire | logger | DEBUG/INFO/WARNING/ERROR/CRITICAL |
| `service` | Obligatoire | app | backend, desktop, worker futur |
| `module` | Recommandé | code | websites, reports, auth |
| `event` | Obligatoire | code | nom stable machine-readable |
| `message` | Obligatoire | code | message court |
| `request_id` | Recommandé/futur | middleware | requête HTTP |
| `correlation_id` | Futur | client/middleware | corrélation multi-actions |
| `trace_id` | Futur | tracing | trace distribuée |
| `span_id` | Futur | tracing | étape de trace |
| `user_id` | Optionnel | auth future | acteur |
| `resource_type` | Optionnel | service | type ressource |
| `resource_id` | Optionnel | service | id ressource |
| `duration_ms` | Optionnel | mesure | durée |
| `status_code` | API | route | code HTTP |
| `error_code` | Erreur | exception | code interne |

### 6.3 Champs interdits

| Champ interdit | Raison |
|---|---|
| `password` | secret |
| `access_token` | secret |
| `refresh_token` | secret |
| `api_key` en clair | secret |
| `authorization` complet | secret |
| `database_url` | credentials |
| payload complet sensible | fuite |

---

## 7. Identifiants de corrélation

### 7.1 Définitions

| Identifiant | Rôle |
|---|---|
| `request_id` | Identifie une requête HTTP unique |
| `correlation_id` | Relie plusieurs requêtes d'un même parcours |
| `trace_id` | Trace distribuée future |
| `span_id` | Étape interne future |

### 7.2 Propagation cible

```text
Desktop -> ApiClient -> FastAPI -> Service -> Repository -> PostgreSQL
```

### 7.3 Diagramme de séquence

```text
Desktop          ApiClient          FastAPI          Service          Repository          PostgreSQL
   |                |                 |                 |                  |                  |
   | action         |                 |                 |                  |                  |
   |--------------->| create req_id   |                 |                  |                  |
   |                |---------------->| attach context  |                  |                  |
   |                |                 |---------------->| use context      |                  |
   |                |                 |                 |----------------->| query            |
   |                |                 |                 |                  |----------------->|
   |                |                 |                 |                  | result           |
   |                |                 | log response    |                  |                  |
   |<---------------|<----------------|                 |                  |                  |
```

### 7.4 Usage dans les erreurs

Le `request_id` doit apparaître dans :

- réponse d'erreur API future ;
- logs backend ;
- logs Desktop liés ;
- audit si action sensible.

---

## 8. Logging backend FastAPI

### 8.1 Tableau par couche

| Couche | Événements à logger | Événements à éviter | Niveau recommandé |
|---|---|---|---|
| Startup | app started, config non sensible | secrets env | INFO |
| Shutdown | app stopped | dumps mémoire | INFO |
| Routes | request completed/failed | body complet sensible | INFO/WARNING/ERROR |
| Services | actions métier | payload complet | INFO |
| Repositories | erreurs DB, slow query future | SQL avec secrets | WARNING/ERROR |
| Migrations futures | start/end/fail revision | données sensibles | INFO/ERROR |
| Health | dégradation | chaque ping en prod bruyant | WARNING |
| Import/export | résultat, durée | contenu exporté | INFO/WARNING |
| Admin | action sensible | secrets modifiés | INFO/WARNING |

### 8.2 Logs au démarrage

Autorisé :

- version app ;
- environnement ;
- niveau de logs ;
- statut configuration non sensible.

Interdit :

- `DATABASE_URL` ;
- secrets JWT ;
- clés API.

---

## 9. Logging API REST

### 9.1 Champs autorisés

| Champ | Autorisé |
|---|---:|
| méthode HTTP | Oui |
| chemin | Oui |
| code HTTP | Oui |
| durée | Oui |
| request_id | Oui |
| user_id futur | Oui |
| IP future | Oui avec politique |
| user-agent futur | Oui avec prudence |
| payload complet | Non |
| Authorization | Non |

### 9.2 Exemple conceptuel

```json
{
  "timestamp": "2026-06-29T10:15:30Z",
  "level": "INFO",
  "service": "backend",
  "module": "api",
  "event": "api.request.completed",
  "method": "GET",
  "path": "/api/v1/websites",
  "status_code": 200,
  "duration_ms": 42,
  "request_id": "req_123",
  "user_id": 1
}
```

### 9.3 Tableau événements API

| Événement API | Niveau | Champs autorisés | Champs interdits |
|---|---|---|---|
| Request success | INFO | method, path, status, duration | body sensible |
| Validation error | WARNING | fields invalides, error_code | payload complet |
| 401 futur | WARNING | request_id, path | token |
| 403 futur | WARNING | permission, user_id | token |
| 404 | INFO/WARNING | resource_type | existence sensible excessive |
| 500 | ERROR | error_code, request_id | stack client |
| Slow request | WARNING | duration, path | payload |

---

## 10. Logging Desktop PySide6

### 10.1 Événements Desktop

| Événement Desktop | Log autorisé | Log interdit | Niveau |
|---|---|---|---|
| Lancement | version, environnement | secrets config | INFO |
| Fermeture | code sortie | tokens | INFO |
| API indisponible | endpoint, erreur réseau | Authorization | WARNING |
| Timeout | endpoint, durée | body sensible | WARNING |
| Navigation | page source/cible | données table | INFO/DEBUG |
| Refresh table | module, durée | items complets | INFO |
| Erreur UI | composant, message redacted | stack affichée user | ERROR |
| Auth future | état général | mot de passe/token | INFO/WARNING |

### 10.2 Règles

- Ne jamais logger tokens.
- Ne jamais logger clés API.
- Ne jamais logger mots de passe.
- Ne jamais logger payload complet sensible.
- Préférer métadonnées et identifiants.

### 10.3 Logs locaux futurs

Les logs Desktop locaux doivent être :

- bornés en taille ;
- rotatifs ;
- sans secrets ;
- désactivables ou configurables ;
- utiles au support interne.

---

## 11. Logging ApiClient

### 11.1 Diagramme

```text
Page UI -> ApiClient -> FastAPI -> Response -> UI State
```

### 11.2 Champs ApiClient

| Sujet | Log autorisé |
|---|---|
| méthode | GET/POST/PUT/DELETE |
| endpoint | path sans secret |
| durée | `duration_ms` |
| status code | oui |
| timeout | oui |
| retry futur | tentative |
| refresh futur | succès/échec sans token |
| headers | seulement allowlist |
| body | jamais complet si sensible |

### 11.3 Masquage Authorization

```text
Authorization: Bearer <redacted>
```

### 11.4 Retry futur

Logger :

- tentative ;
- délai ;
- endpoint ;
- résultat.

Ne pas logger :

- payload sensible répété ;
- token ;
- refresh token.

---

## 12. Logging services métier

### 12.1 Tableau par module

| Module | Événement métier | Niveau | Audit requis | Données autorisées |
|---|---|---|---:|---|
| Websites | `website.created` | INFO | Oui futur | website_id, entity_id |
| Websites | `website.deleted` | WARNING | Oui | website_id |
| Entities | `entity.updated` | INFO | Oui futur | entity_id |
| Keywords | `keyword.import.completed` | INFO | Oui si massif | count, entity_id |
| Competitors | `competitor.created` | INFO | Optionnel | competitor_id |
| Reports | `report.generated` | INFO | Oui | report_id, type |
| Reports | `report.exported` | INFO | Oui | report_id, format |
| SEO | `seo.audit.completed` | INFO | Optionnel | website_id, score |
| GEO | `geo.analysis.completed` | INFO | Oui selon sensibilité | entity_id, model |
| Crawler | `crawler.job.started` | INFO | Oui | job_id, website_id |
| IA | `ai.call.failed` | WARNING | Optionnel | provider, model |
| Prompts | `prompt.updated` | INFO | Oui | prompt_id |
| Administration | `role.updated` | WARNING | Oui | role_id |
| Configuration | `config.import.completed` | INFO | Oui | counts |

### 12.2 Règle service

Le service est le bon endroit pour logger un événement métier, car il connaît le cas d'usage sans exposer la couche HTTP
ni les détails SQL.

---

## 13. Logging repositories et database

### 13.1 Tableau DB

| Événement DB | Niveau | Message autorisé | Message interdit |
|---|---|---|---|
| Violation contrainte | WARNING | contrainte, ressource | payload complet |
| Rollback transaction | ERROR/WARNING | request_id, type erreur | données sensibles |
| Timeout DB futur | ERROR | durée, opération | connection string |
| Requête lente future | WARNING | table, durée | SQL avec valeurs sensibles |
| Connexion DB échouée | CRITICAL | DB unavailable | credentials |
| Migration échouée | CRITICAL | revision, étape | données sensibles |

### 13.2 Règles

- Ne pas logger la chaîne de connexion.
- Ne pas logger les credentials.
- Ne pas logger dumps complets de modèles.
- Ne pas logger SQL brut avec valeurs sensibles.
- Préférer table/opération/durée/request_id.

---

## 14. Logs de sécurité

### 14.1 Matrice sécurité

| Événement sécurité | Niveau | Audit obligatoire | Alerte future | Données interdites |
|---|---|---:|---:|---|
| Login réussi futur | INFO | Oui | Non | mot de passe |
| Login échoué futur | WARNING | Oui | Si répété | mot de passe |
| Compte bloqué futur | WARNING | Oui | Oui | secrets |
| Token expiré | INFO/WARNING | Non | Non | token |
| Token invalide | WARNING | Oui si répété | Oui | token |
| Permission refusée | WARNING | Optionnel | Si répété | token |
| Accès admin | INFO | Oui | Non | payload sensible |
| Changement rôle | WARNING | Oui | Oui si critique | secrets |
| Changement permission | WARNING | Oui | Oui | secrets |
| Changement mot de passe | WARNING | Oui | Non | mot de passe |
| Clé API modifiée | WARNING | Oui | Oui | clé brute |
| Export sensible | INFO/WARNING | Oui | Selon volume | contenu |
| Import configuration | INFO/WARNING | Oui | Si erreur | secrets importés |

### 14.2 Comportement suspect

Exemples :

- nombreux 401 ;
- nombreux 403 ;
- réutilisation refresh token futur ;
- export massif ;
- tentatives répétées admin ;
- API key invalide répétée.

---

## 15. Logs d'audit

### 15.1 Différence audit/logging

L'audit doit être durable, consultable et structuré. Il ne remplace pas les logs techniques.

### 15.2 Format conceptuel

```json
{
  "event": "permission.updated",
  "actor_user_id": 1,
  "target_type": "role",
  "target_id": 3,
  "action": "update",
  "before": {},
  "after": {},
  "request_id": "req_...",
  "created_at": "2026-06-29T10:15:30Z"
}
```

### 15.3 Limites

- Ne pas stocker de secret dans `before` ou `after`.
- Masquer les champs sensibles.
- Limiter les données volumineuses.
- Ne pas stocker de payload IA complet sans justification.

### 15.4 Actions auditées

| Domaine | Actions |
|---|---|
| Utilisateurs | create, update, disable, unlock |
| Rôles | create, update, delete |
| Permissions | grant, revoke |
| Configuration | import, export, update |
| Websites | create, update, delete |
| Reports | generate, export, delete |
| IA/GEO | analysis sensitive future |
| API keys | create, rotate, disable |

---

## 16. Logs d'erreur

### 16.1 Tableau

| Erreur | Message utilisateur | Log interne | Niveau | Données interdites |
|---|---|---|---|---|
| Validation API | Champs invalides | field errors redacted | WARNING | payload complet |
| Métier attendue | Conflit de données | domain error code | WARNING | données sensibles |
| Database | Service indisponible | exception class, request_id | ERROR | DB URL |
| Desktop réseau | API indisponible | endpoint, timeout | WARNING | token |
| IA future | Fournisseur indisponible | provider, code | WARNING/ERROR | API key/prompt sensible |
| Inattendue | Erreur technique | stack interne | ERROR | stack côté utilisateur |

### 16.2 Stack traces

Les stack traces peuvent être conservées dans les logs internes sécurisés en développement/staging. En production, elles
doivent être contrôlées et ne jamais être retournées au client.

---

## 17. Logs de performance

### 17.1 Métriques

| Métrique | Seuil normal | Warning | Critique | Action |
|---|---:|---:|---:|---|
| API health | < 500 ms | > 1 s | > 3 s | vérifier backend |
| Liste websites | < 1 s | > 2 s | > 5 s | index/pagination |
| Requête DB | < 100 ms | > 500 ms | > 2 s | EXPLAIN futur |
| Export rapport | job async | > seuil job | échec | inspect job |
| Appel IA futur | < 10 s | > 20 s | timeout | retry/quota |
| Crawl futur | selon job | lent | bloqué | inspect crawler |

### 17.2 Champs performance

- `duration_ms` ;
- `operation` ;
- `module` ;
- `resource_type` ;
- `count` si non sensible ;
- `status`.

---

## 18. Logs IA / GEO futurs

### 18.1 Tableau

| Événement IA/GEO | Log autorisé | Log interdit | Audit requis |
|---|---|---|---:|
| Appel modèle | provider, model, duration, status | clé API, prompt sensible | Selon cas |
| Timeout IA | provider, timeout | clé API | Non/alerte |
| Quota atteint | provider, quota type | token fournisseur | Oui si impact |
| Résultat stocké | result_id, score | réponse complète sensible | Selon sensibilité |
| Prompt run | prompt_id, run_id | contenu prompt sensible | Oui si admin |
| Erreur provider | provider, error_code | payload complet | Non |

### 18.2 Coûts et tokens futurs

Si disponibles, les tokens/coûts peuvent être logués comme métriques agrégées, jamais avec un contenu confidentiel.

---

## 19. Logs crawler futurs

### 19.1 Tableau

| Événement crawler | Niveau | Champs autorisés | Champs interdits |
|---|---|---|---|
| Job démarré | INFO | job_id, website_id | contenu page |
| Job terminé | INFO | counts, duration | dump résultats |
| URL visitée | DEBUG/INFO agrégé | status_code, duration | HTML complet |
| Erreur réseau | WARNING | url domaine, code | credentials |
| robots.txt bloquant | INFO/WARNING | website_id | contenu inutile |
| Limite atteinte | WARNING | limit, job_id | payload complet |
| Page ignorée | DEBUG | raison | HTML |

### 19.2 Règles

- Ne pas logger HTML complet.
- Ne pas logger cookies externes.
- Ne pas logger headers sensibles.
- Agréger les événements par job pour éviter le bruit.

---

## 20. Logs rapports et exports

### 20.1 Événements

| Événement | Niveau | Audit |
|---|---|---:|
| Rapport généré | INFO | Oui |
| Rapport échoué | ERROR | Oui si critique |
| Rapport téléchargé | INFO | Oui |
| Export CSV/PDF | INFO | Oui |
| Export configuration | WARNING/INFO | Oui |
| Export massif | WARNING | Oui + alerte future |

### 20.2 Règles

- Ne jamais logger le contenu complet exporté.
- Logger métadonnées uniquement : type, format, nombre, acteur.
- Audit obligatoire pour export sensible.
- Masquer secrets dans export configuration.

---

## 21. Données interdites dans les logs

### 21.1 Liste explicite

Interdits :

- mots de passe ;
- hash de mot de passe si inutile ;
- tokens ;
- refresh tokens ;
- access tokens ;
- clés API ;
- secrets JWT ;
- `.env` ;
- chaînes de connexion complètes ;
- payload complet de login ;
- clés OpenAI/Gemini/Claude/Copilot/Perplexity ;
- données personnelles inutiles ;
- contenus confidentiels ;
- prompts sensibles ;
- réponses IA sensibles ;
- dumps SQL complets.

### 21.2 Matrice

| Donnée | Peut être loguée ? | Forme autorisée | Forme interdite |
|---|---:|---|---|
| Mot de passe | Non | Aucune | clair/hash |
| Access token | Non | `<redacted>` | valeur complète |
| Refresh token | Non | `<redacted>` | valeur complète |
| API key | Non | masque suffixe 4 chars | valeur complète |
| Email | Oui avec prudence | email ou masqué | listes massives inutiles |
| URL publique | Oui | URL sans secrets | query tokenisée |
| Prompt | Rarement | prompt_id | contenu sensible |
| Réponse IA | Rarement | result_id, score | contenu complet |
| SQL | Rarement | opération/table | SQL avec valeurs |
| `.env` | Non | Aucune | contenu complet |

---

## 22. Masquage et anonymisation

### 22.1 Exemples

```text
sk-************************abcd
anthropic-****************efgh
user***@example.com
Authorization: Bearer <redacted>
postgresql://<redacted>
```

### 22.2 Règles

| Donnée | Masquage |
|---|---|
| Email | conserver domaine si utile |
| API key | garder 4 derniers caractères |
| Token | redacted complet |
| DB URL | redacted complet |
| Header Authorization | redacted complet |
| Payload sensible | champs allowlist uniquement |

### 22.3 Pseudonymisation future

Pour analyses longues, utiliser `user_id` ou identifiant pseudonymisé plutôt que données personnelles directes si
suffisant.

---

## 23. Gestion des environnements

### 23.1 Tableau

| Environnement | Niveau minimal | Destination | Données autorisées | Rétention |
|---|---|---|---|---|
| Développement | DEBUG/INFO | console | non sensibles | courte |
| Test | WARNING/ERROR sauf besoin | console test | synthétiques | temporaire |
| Staging futur | INFO/WARNING/ERROR | centralisé futur | anonymisées si possible | moyenne |
| Production future | INFO/WARNING/ERROR | centralisé sécurisé | minimales | définie |

### 23.2 Règles

- DEBUG possible en développement.
- DEBUG contrôlé en staging.
- DEBUG interdit en production standard.
- Secrets jamais logués quel que soit l'environnement.

---

## 24. Destinations des logs

### 24.1 Tableau

| Destination | Usage | Environnement | Risque | Protection |
|---|---|---|---|---|
| Console | dev/debug | dev/test | fuite écran | pas de secrets |
| Fichier local futur | Desktop/backend local | dev/support | exposition poste | rotation + redaction |
| `audit_logs` table future | audit durable | staging/prod | données sensibles | accès admin |
| Service externe futur | centralisation | staging/prod | transfert données | chiffrement |
| Monitoring futur | métriques | staging/prod | bruit | agrégation |
| SIEM futur | sécurité | prod | coût/volume | filtrage |

### 24.2 Logs Desktop locaux

Ils doivent être bornés, rotatifs et sans secrets. L'utilisateur ne doit pas avoir à manipuler des fichiers contenant
des données sensibles.

---

## 25. Rétention des logs

### 25.1 Recommandations

| Type | Rétention recommandée |
|---|---|
| Logs DEBUG dev | courte, locale |
| Logs techniques INFO | 7 à 30 jours futur |
| Logs erreurs | 30 à 90 jours futur |
| Logs sécurité | 90 jours à 1 an futur |
| Audit admin | 1 an+ selon politique |
| Logs IA détaillés | minimiser, durée courte |
| Logs crawler détaillés | courte, agrégats plus longs |

### 25.2 Rotation

Prévoir :

- rotation par taille ;
- rotation par date ;
- purge automatique ;
- archivage si conformité ;
- suppression RGPD future si applicable.

---

## 26. Monitoring futur

### 26.1 Diagramme

```text
FastAPI logs
   |
   +-- metrics API
   +-- errors 5xx
   +-- latency
   +-- DB health
   +-- IA quotas
   +-- crawler jobs
   |
   v
Monitoring backend futur
   |
   +-- dashboards
   +-- alerts
   +-- incident analysis
```

### 26.2 Métriques

| Métrique | Usage |
|---|---|
| uptime | disponibilité |
| 5xx rate | erreurs serveur |
| 4xx rate | erreurs client/auth |
| latency p95 | performance |
| db health | PostgreSQL |
| jobs running | crawler/reports |
| ai calls | coûts/quota |
| export count | sécurité |

---

## 27. Alerting futur

### 27.1 Tableau

| Événement | Gravité | Alerte | Destinataire futur | Action |
|---|---|---:|---|---|
| DB indisponible | Critique | Oui | admin technique | restaurer service |
| 5xx élevé | Élevée | Oui | dev/backend | inspect logs |
| Brute force | Élevée | Oui | sécurité/admin | bloquer compte/IP |
| API key invalide | Moyenne | Oui si répété | admin | rotation |
| Quota IA atteint | Moyenne | Oui | marketing/admin | ajuster quotas |
| Export massif | Élevée | Oui | admin | vérifier acteur |
| Migration échouée | Critique | Oui | dev/backend | rollback |
| Crawler bloqué | Moyenne | Oui | SEO/admin | inspect job |

---

## 28. Health checks

### 28.1 Endpoints

```text
GET /api/v1/health
GET /api/v1/health/db
GET /api/v1/version
```

### 28.2 Logging

- Ne pas logger chaque health check en production si bruit excessif.
- Logger les changements d'état : OK -> dégradé, dégradé -> OK.
- Logger DB down en ERROR/CRITICAL selon impact.

### 28.3 Lien API

Voir `API_ARCHITECTURE.md` pour les contrats de santé et version.

---

## 29. Observabilité des imports/exports

### 29.1 Champs autorisés

| Champ | Usage |
|---|---|
| actor_user_id | acteur |
| import/export type | configuration, report |
| count_created | métrique |
| count_updated | métrique |
| count_failed | métrique |
| duration_ms | performance |
| request_id | corrélation |

### 29.2 Données interdites

- contenu complet importé ;
- secrets importés ;
- export complet ;
- clés API ;
- tokens.

### 29.3 Erreurs

Les erreurs d'import doivent loguer la section et le code d'erreur, pas le payload complet.

---

## 30. Observabilité des migrations

### 30.1 Événements

| Événement | Niveau | Champs |
|---|---|---|
| Migration démarrée | INFO | revision |
| Migration terminée | INFO | revision, duration |
| Migration échouée | CRITICAL | revision, error_code |
| Rollback | WARNING | revision |
| Backup préalable futur | INFO | backup_id |

### 30.2 Règles

- Ne pas logger données migrées ligne par ligne.
- Ne pas logger secrets contenus dans données.
- Loguer revision et durée.
- Voir `DATABASE_ARCHITECTURE.md` pour migrations explicites.

---

## 31. Gestion des incidents

### 31.1 Guide d'analyse

```text
Incident détecté
    |
    v
Récupérer request_id/correlation_id
    |
    v
Identifier période
    |
    v
Filtrer par event/module/user/resource
    |
    v
Vérifier sécurité/audit
    |
    v
Corréler API, service, DB, Desktop
    |
    v
Documenter cause et correction
```

### 31.2 Incidents couverts

| Incident | Logs utiles |
|---|---|
| Fuite secret | Git diff, audit config, logs redaction |
| Compte compromis | login, permission, audit |
| Endpoint admin exposé | API access, 403/200 admin |
| Erreur API critique | request_id, stack interne |
| DB indisponible | db health, connection errors |
| Corruption données | audit, migrations |
| Export accidentel | report/export audit |
| Quota IA dépassé | ai call logs |
| Dépendance externe down | external api errors |

---

## 32. Tests du logging

### 32.1 Tests futurs

| Test | Objectif |
|---|---|
| Présence log critique | action admin produit audit |
| Absence secret | token non présent |
| Erreur API | request_id présent |
| Permission | 403 logué sans token |
| Import/export | audit métadonnées |
| Masquage | clé API masquée |
| Performance | slow request log futur |

### 32.2 Commandes

```powershell
py -m pytest
py -m ruff check .
```

### 32.3 Checklist tests logging

| Contrôle | OK |
|---|---|
| Aucun secret dans logs de test | |
| Log d'erreur contient request_id futur | |
| Audit action sensible testé | |
| 401/403 futurs testés | |
| Import/export logue métadonnées | |
| Masquage testé | |

---

## 33. Qualité et conventions

### 33.1 Noms d'événements

Convention :

```text
domain.resource_action
```

ou :

```text
resource.action
```

Exemples :

| Event | Usage |
|---|---|
| `website.created` | création site |
| `auth.login_failed` | échec connexion futur |
| `api.request.completed` | requête API terminée |
| `permission.denied` | permission refusée |
| `report.exported` | export rapport |
| `config.import_failed` | import configuration échoué |
| `ai.call_failed` | appel IA échoué |
| `crawler.job_completed` | crawl terminé |

### 33.2 Règles

- Event codes en anglais, stables, machine-readable.
- Messages courts.
- Champs structurés.
- Pas de phrases variables comme identifiants.
- Pas de logs uniquement en français pour les codes machine.

---

## 34. Anti-patterns interdits

### 34.1 Tableau

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Logger un token | compromission session | `<redacted>` |
| Logger un mot de passe | compromission compte | jamais |
| Logger `.env` | fuite secrets | jamais |
| Logger payload complet | fuite données | champs allowlist |
| Logger exception brute vers utilisateur | fuite technique | message propre + log interne |
| Logger SQL avec secrets | fuite DB | table/opération/durée |
| Logs sans contexte | inutile | event + request_id |
| Logs trop bavards | bruit/coût/fuite | agrégation |
| Logs impossibles à corréler | debug lent | request_id/correlation_id |
| Event codes en français libre | parsing difficile | codes anglais stables |
| ERROR pour tout | alert fatigue | niveaux cohérents |
| Pas d'audit admin | non-traçabilité | audit obligatoire |

---

## 35. Pattern officiel pour ajouter un événement de log

### 35.1 Étapes

1. Identifier le type d'événement.
2. Choisir le niveau.
3. Choisir les champs.
4. Vérifier les données sensibles.
5. Ajouter request_id/correlation_id si disponible.
6. Choisir event code.
7. Documenter l'événement si critique.
8. Ajouter test si nécessaire.

### 35.2 Checklist

| Contrôle | OK |
|---|---|
| Event code stable | |
| Niveau correct | |
| Pas de secret | |
| Pas de payload sensible | |
| request_id prévu | |
| Message actionnable | |
| Audit séparé si action sensible | |
| Test ajouté si critique | |

### 35.3 Diagramme

```text
Nouvel événement
      |
      v
Classer type
      |
      v
Choisir niveau + champs
      |
      v
Redaction secrets
      |
      v
Logger structuré
      |
      v
Test / documentation si critique
```

---

## 36. Checklist avant Pull Request logging

| Contrôle | Commande ou action | OK |
|---|---|---|
| Statut Git | `git status` | |
| Stat diff | `git diff --stat` | |
| Espaces | `git diff --check` | |
| Tests | `py -m pytest` | |
| Ruff | `py -m ruff check .` | |
| Aucun secret logué | revue diff | |
| Aucun payload sensible | revue logs | |
| Erreurs propres | revue handlers | |
| Logs utiles | revue event codes | |
| Pas de bruit excessif | revue fréquence | |
| Documentation mise à jour | docs | |

---

## 37. Roadmap logging et observabilité

### 37.1 Phase 1 - Logs console structurés

- event codes ;
- niveaux cohérents ;
- redaction secrets ;
- conventions.

### 37.2 Phase 2 - Logs API avec request_id

- middleware request_id ;
- réponse d'erreur avec request_id ;
- propagation service/repository.

### 37.3 Phase 3 - Logs erreurs normalisés

- exception handlers ;
- codes d'erreur ;
- logs internes sans fuite.

### 37.4 Phase 4 - Logs audit

- audit_logs ;
- actions admin ;
- exports ;
- configuration.

### 37.5 Phase 5 - Logs sécurité

- auth ;
- RBAC ;
- permission denied ;
- comportements suspects.

### 37.6 Phase 6 - Logs performance

- durée API ;
- durée DB ;
- slow requests ;
- jobs.

### 37.7 Phase 7 - Logs Desktop

- démarrage ;
- ApiClient ;
- erreurs réseau ;
- session future.

### 37.8 Phase 8 - Monitoring et alerting

- métriques ;
- dashboards ;
- alertes ;
- seuils.

### 37.9 Phase 9 - Centralisation

- logs centralisés ;
- recherches ;
- rétention ;
- accès contrôlé.

### 37.10 Phase 10 - v1 stable

- standards appliqués ;
- tests sécurité/logging ;
- incident playbooks ;
- dashboards observabilité.

---

## 38. Annexes

### 38.1 Glossaire

| Terme | Définition |
|---|---|
| Log | Événement enregistré pour diagnostic |
| Audit | Trace durable d'une action sensible |
| Request ID | Identifiant d'une requête HTTP |
| Correlation ID | Identifiant d'un parcours multi-requêtes |
| Trace ID | Identifiant de trace distribuée future |
| Redaction | Masquage de données sensibles |
| Metric | Valeur mesurable agrégée |
| Alert | Notification sur seuil ou événement |

### 38.2 Abréviations

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| DB | Database |
| IA | Intelligence artificielle |
| GEO | Generative Engine Optimization |
| SEO | Search Engine Optimization |
| PII | Personally Identifiable Information |
| SIEM | Security Information and Event Management |

### 38.3 Modèle de log JSON

```json
{
  "timestamp": "2026-06-29T10:15:30Z",
  "level": "INFO",
  "service": "backend",
  "module": "websites",
  "event": "website.created",
  "message": "Website created",
  "request_id": "req_123",
  "user_id": 1,
  "resource_type": "website",
  "resource_id": 12
}
```

### 38.4 Modèle d'audit JSON

```json
{
  "event": "role.updated",
  "actor_user_id": 1,
  "target_type": "role",
  "target_id": 2,
  "action": "update",
  "request_id": "req_123",
  "created_at": "2026-06-29T10:15:30Z"
}
```

### 38.5 Matrice données sensibles rapide

| Donnée | Log |
|---|---|
| Mot de passe | Jamais |
| Token | Jamais |
| API key | Masquée uniquement |
| Email | Avec prudence |
| Prompt | ID seulement par défaut |
| Rapport | Métadonnées |
| SQL | Pas de valeurs sensibles |

### 38.6 Checklist rapide développeur

| Question | Réponse attendue |
|---|---|
| Le log est-il utile ? | Oui |
| Le niveau est-il correct ? | Oui |
| Y a-t-il un secret ? | Non |
| Le log est-il corrélable ? | Oui si requête |
| L'action est-elle sensible ? | Audit prévu |
| Le message est-il actionnable ? | Oui |
| Le volume est-il maîtrisé ? | Oui |

### 38.7 Liens internes

| Sujet | Document |
|---|---|
| Sécurité globale | `docs/architecture/SECURITY.md` |
| Authentification | `docs/architecture/AUTHENTICATION.md` |
| API | `docs/architecture/API_ARCHITECTURE.md` |
| Backend | `docs/architecture/BACKEND_ARCHITECTURE.md` |
| Database | `docs/architecture/DATABASE_ARCHITECTURE.md` |
| Desktop | `docs/architecture/DESKTOP_ARCHITECTURE.md` |

### 38.8 Résumé architectural

L'observabilité de Veille SEO-GEO Groupe A.P&Partner doit produire des logs structurés, corrélables, minimaux et
sécurisés. Les logs doivent aider au diagnostic sans jamais exposer secrets, tokens, mots de passe, clés API ou données
sensibles. Les événements techniques, métier, sécurité et audit doivent rester distingués.

La cible v1.0 est une chaîne cohérente :

```text
Desktop -> ApiClient -> API -> Services -> Repositories -> PostgreSQL -> Logs/Audit/Metrics
```

Chaque événement important doit être compréhensible, filtrable, relié à une requête ou action, et exploitable lors
d'une analyse incident.
