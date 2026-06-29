# Software Security Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle de sécurité globale  
Version du document : 1.0  
Statut : Référence sécurité projet  
Périmètre : backend, API, Desktop, base de données, secrets, logs, audit, production future  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes de sécurité](#2-principes-de-sécurité)
3. [Vue d'ensemble de l'architecture de sécurité](#3-vue-densemble-de-larchitecture-de-sécurité)
4. [Modèle de menace](#4-modèle-de-menace)
5. [Frontières de confiance](#5-frontières-de-confiance)
6. [Secrets et variables d'environnement](#6-secrets-et-variables-denvironnement)
7. [Sécurité Git et dépôt](#7-sécurité-git-et-dépôt)
8. [Sécurité backend FastAPI](#8-sécurité-backend-fastapi)
9. [Sécurité API REST](#9-sécurité-api-rest)
10. [Authentification et autorisation](#10-authentification-et-autorisation)
11. [Sécurité Desktop PySide6](#11-sécurité-desktop-pyside6)
12. [Sécurité base de données PostgreSQL](#12-sécurité-base-de-données-postgresql)
13. [Sécurité des migrations Alembic](#13-sécurité-des-migrations-alembic)
14. [Données sensibles](#14-données-sensibles)
15. [Mots de passe](#15-mots-de-passe)
16. [Clés API externes](#16-clés-api-externes)
17. [Validation des entrées](#17-validation-des-entrées)
18. [Protection contre injections](#18-protection-contre-injections)
19. [Gestion des erreurs sécurisée](#19-gestion-des-erreurs-sécurisée)
20. [Journalisation sécurisée](#20-journalisation-sécurisée)
21. [Audit](#21-audit)
22. [Sécurité des imports/exports](#22-sécurité-des-importsexports)
23. [Sécurité IA / GEO future](#23-sécurité-ia--geo-future)
24. [Sécurité Crawler future](#24-sécurité-crawler-future)
25. [Sécurité des rapports](#25-sécurité-des-rapports)
26. [Sécurité réseau](#26-sécurité-réseau)
27. [Dépendances et supply chain](#27-dépendances-et-supply-chain)
28. [Environnements](#28-environnements)
29. [RGPD et conformité](#29-rgpd-et-conformité)
30. [OWASP](#30-owasp)
31. [Sauvegardes et reprise](#31-sauvegardes-et-reprise)
32. [Gestion des incidents](#32-gestion-des-incidents)
33. [Sécurité avant mise en production](#33-sécurité-avant-mise-en-production)
34. [Tests de sécurité](#34-tests-de-sécurité)
35. [Anti-patterns interdits](#35-anti-patterns-interdits)
36. [Pattern officiel pour ajouter une fonctionnalité sensible](#36-pattern-officiel-pour-ajouter-une-fonctionnalité-sensible)
37. [Checklist avant Pull Request sécurité](#37-checklist-avant-pull-request-sécurité)
38. [Roadmap sécurité](#38-roadmap-sécurité)
39. [Annexes](#39-annexes)

---

## 1. Présentation

### 1.1 Rôle du document

Ce document définit l'architecture de sécurité globale de Veille SEO-GEO Groupe A.P&Partner. Il sert de référence
technique pour sécuriser le backend FastAPI, l'API REST, le Desktop PySide6, PostgreSQL, les secrets, les logs, les
imports/exports, les clés API externes et les futures intégrations IA, SEO et GEO.

Il complète les documents existants sans les remplacer :

- `AUTHENTICATION.md` : authentification, autorisation, JWT, RBAC, sessions ;
- `API_ARCHITECTURE.md` : contrats API, endpoints, erreurs, pagination ;
- `BACKEND_ARCHITECTURE.md` : couches Routes, Services, Repositories, Models ;
- `DATABASE_ARCHITECTURE.md` : PostgreSQL, SQLAlchemy, Alembic, contraintes ;
- `DESKTOP_ARCHITECTURE.md` : client Desktop, ApiClient, états UI.

### 1.2 Vision sécurité

La vision sécurité est :

> Concevoir chaque fonctionnalité comme si elle manipulait des données stratégiques, des secrets ou des droits
> critiques, puis appliquer des protections proportionnées dès la conception.

L'application centralise des informations SEO, GEO, IA, rapports, contenus, configurations et futures clés API. Ces
données peuvent révéler la stratégie numérique du groupe. La sécurité n'est donc pas un ajout tardif ; elle est une
contrainte d'architecture.

### 1.3 Objectifs de sécurité

| Objectif | Description | Impact attendu |
|---|---|---|
| Confidentialité | Empêcher l'accès non autorisé aux données et secrets | Réduction fuite |
| Intégrité | Empêcher les modifications non autorisées ou incohérentes | Données fiables |
| Disponibilité | Limiter abus, erreurs et opérations destructives | Continuité |
| Traçabilité | Savoir qui a fait quoi et quand | Audit |
| Révocabilité | Couper accès, tokens et clés compromis | Réponse incident |
| Défense en profondeur | Multiplier les contrôles complémentaires | Résilience |
| Moindre privilège | Accès minimal par rôle et service | Surface réduite |

### 1.4 Risques principaux

Les risques prioritaires sont :

- fuite de `.env`, tokens ou clés API ;
- endpoint admin non protégé ;
- contournement des permissions ;
- erreur API trop bavarde ;
- logs contenant des secrets ;
- accès direct PostgreSQL hors backend ;
- suppression destructive non auditée ;
- injection SQL ou payload non validé ;
- dépendance vulnérable ;
- export de rapports contenant des informations sensibles ;
- prompt injection et fuite de données vers modèles IA futurs.

### 1.5 Périmètres couverts

| Périmètre | Couvert |
|---|---:|
| Backend FastAPI | Oui |
| API REST `/api/v1` | Oui |
| Desktop PySide6 | Oui |
| PostgreSQL | Oui |
| Alembic | Oui |
| Secrets et `.env` | Oui |
| Logs et audit | Oui |
| IA/GEO future | Oui |
| Production future | Oui |

### 1.6 Périmètres non couverts

Ce document ne remplace pas :

- une politique juridique RGPD complète ;
- un plan d'infrastructure détaillé ;
- une procédure SOC ;
- un audit de sécurité externe ;
- un guide d'exploitation production final ;
- une documentation fournisseur pour OpenAI, Google, Anthropic ou autres services externes.

### 1.7 Principes directeurs

```text
Security by Design
Least Privilege
Zero Trust
Defense in Depth
Secure Defaults
Auditability
```

### 1.8 Relation avec les autres documents

```text
SECURITY.md
  |
  +-- AUTHENTICATION.md        Auth, RBAC, sessions
  +-- API_ARCHITECTURE.md      Endpoints, erreurs, contrats
  +-- BACKEND_ARCHITECTURE.md  Couches backend
  +-- DATABASE_ARCHITECTURE.md Données, migrations, contraintes
  +-- DESKTOP_ARCHITECTURE.md  Client Desktop et ApiClient
```

---

## 2. Principes de sécurité

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| Security by Design | Corriger tard coûte cher | sécurité prévue dès les specs | ajouter auth après coup |
| Least Privilege | Limiter impact d'un compte compromis | permissions par module/action | rôle admin par défaut |
| Zero Trust | Aucun client n'est fiable par nature | API valide token et permissions | faire confiance au Desktop |
| Defense in Depth | Une protection peut échouer | Pydantic + service + DB | validation UI seulement |
| Secure Defaults | Réduire erreurs humaines | endpoints privés par défaut futur | endpoint admin public |
| Secrets hors dépôt | Éviter fuite irréversible | `.env` non commité | clé API dans code |
| Logs sans secrets | Préserver confidentialité | masquage tokens/clés | token dans traceback |
| Accès DB backend only | Préserver architecture | repositories SQLAlchemy | Desktop -> PostgreSQL |
| Erreurs non bavardes | Éviter fuite technique | messages contrôlés | stack trace exposée |
| Auditabilité | Reconstituer événements | audit logs futurs | suppression sans trace |
| Préparation RGPD | Minimiser données personnelles | conservation limitée | logs éternels avec emails |
| Préparation OWASP | Couvrir risques classiques | matrices OWASP | ignorer dépendances |

### 2.2 Séparation des responsabilités

```text
Desktop
  |
  +-- affiche
  +-- appelle API
  +-- ne décide pas des droits

API / Backend
  |
  +-- authentifie
  +-- autorise
  +-- valide
  +-- applique métier

Database
  |
  +-- contraint
  +-- persiste
  +-- garantit intégrité
```

### 2.3 Défense en profondeur

Exemple pour création d'un website :

| Couche | Protection |
|---|---|
| Desktop | formulaire typé, message propre |
| API route | schema Pydantic |
| Service | vérifie URL unique et règles métier |
| Repository | requête SQLAlchemy paramétrée |
| PostgreSQL | contrainte unique sur URL |
| Audit futur | trace création |

---

## 3. Vue d'ensemble de l'architecture de sécurité

### 3.1 Diagramme principal

```text
Desktop PySide6
      |
      | HTTPS / Bearer Token futur
      v
FastAPI API /api/v1
      |
      v
Authentication / Authorization
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

### 3.2 Vue logique

```text
Identity Security
  |
  +-- users
  +-- roles
  +-- permissions
  +-- sessions futures

Application Security
  |
  +-- route protection
  +-- service validation
  +-- error handling
  +-- audit events

Data Security
  |
  +-- constraints
  +-- secrets storage
  +-- backups future
  +-- migrations safe

Client Security
  |
  +-- ApiClient only
  +-- secure token storage future
  +-- no direct DB access
```

### 3.3 Vue physique

```text
User workstation
  |
  v
Desktop process
  |
  | encrypted transport in production
  v
Backend host / FastAPI
  |
  | DB credentials from environment
  v
PostgreSQL server
  |
  v
Backups future / restricted storage
```

### 3.4 Frontières de confiance

```text
[Utilisateur] -- input non fiable --> [Desktop]
      |                                |
      | réseau non fiable              | client non fiable côté serveur
      v                                v
[API FastAPI] -- validation --> [Services] -- accès contrôlé --> [PostgreSQL]
      |
      +-- appels externes futurs --> [OpenAI / Google / SEO APIs]
```

### 3.5 Données sensibles

```text
Secrets techniques
  +-- .env
  +-- DATABASE_URL
  +-- JWT secrets future
  +-- API keys externes

Données métier sensibles
  +-- rapports SEO/GEO
  +-- prompts
  +-- résultats IA
  +-- concurrents
  +-- configuration

Données utilisateur
  +-- emails
  +-- rôles
  +-- logs d'accès
```

### 3.6 Flux de secrets

```text
.env / secret store future
        |
        v
Backend configuration
        |
        +-- DATABASE_URL -> SQLAlchemy
        +-- JWT_SECRET future -> Auth service
        +-- API keys -> Connecteurs externes
        |
        v
Jamais exposé au Desktop, aux logs ou à Git
```

### 3.7 Zones à risque

| Zone | Risque |
|---|---|
| Login futur | brute force, credential stuffing |
| Admin | escalade privilège |
| API keys | fuite secret |
| Import config | écrasement ou payload malformé |
| Export reports | exfiltration |
| Crawler | surcharge, HTML non fiable |
| IA/GEO | prompt injection, fuite données internes |
| Logs | secrets accidentels |

---

## 4. Modèle de menace

### 4.1 Matrice des menaces

| Menace | Impact | Probabilité | Protection | Document lié |
|---|---|---:|---|---|
| Accès non autorisé | Élevé | Moyenne | Auth/RBAC, 401/403 | AUTHENTICATION |
| Vol de token | Élevé | Moyenne future | tokens courts, refresh rotation | AUTHENTICATION |
| Fuite de clé API | Critique | Moyenne | secret storage, masquage | DATABASE |
| Endpoint admin non protégé | Critique | Moyenne | `require_admin` futur | API |
| Injection SQL | Élevé | Faible à moyenne | SQLAlchemy, validation | BACKEND |
| Injection JSON | Moyen | Moyenne | Pydantic, limites | API |
| Erreur bavarde | Moyen | Moyenne | handler erreurs | API |
| Brute force | Élevé | Moyenne future | rate limiting, blocage | AUTHENTICATION |
| Abus d'API | Moyen | Moyenne | pagination, rate limit | API |
| CORS mal configuré | Moyen | Faible actuel | CORS strict futur | API |
| `.env` exposé | Critique | Moyenne | gitignore, checklist | SECURITY |
| Logs avec secrets | Critique | Moyenne | masquage, règles logs | SECURITY |
| Permissions mal gérées | Élevé | Moyenne | RBAC centralisé | AUTHENTICATION |
| Suppression destructive | Élevé | Moyenne | soft delete, audit | DATABASE |
| Desktop compromis | Élevé | Faible à moyenne | API autoritaire | DESKTOP |
| DB compromise | Critique | Faible | privilèges limités, backups | DATABASE |
| Dépendance vulnérable | Élevé | Moyenne | audit dépendances | SECURITY |
| Exfiltration rapports | Élevé | Moyenne | permissions, audit, exports contrôlés | API |

### 4.2 Menaces prioritaires v1.0

1. Secrets dans Git ou logs.
2. Endpoints admin non protégés.
3. Permissions insuffisamment centralisées.
4. Exports contenant trop de données.
5. Migrations destructives non validées.
6. Dépendances non suivies.

---

## 5. Frontières de confiance

### 5.1 Diagramme

```text
Trust Boundary A: Poste utilisateur
  [Utilisateur] -> [Desktop PySide6]

Trust Boundary B: Réseau
  [Desktop] -> HTTPS -> [FastAPI]

Trust Boundary C: Backend
  [Routes] -> [Services] -> [Repositories]

Trust Boundary D: Données
  [Repositories] -> [PostgreSQL]

Trust Boundary E: Externe futur
  [Connecteurs] -> [OpenAI / Google / SEO APIs]

Trust Boundary F: Supply chain
  [GitHub / dépendances / CI future]
```

### 5.2 Tableau des frontières

| Frontière | Données traversantes | Risque | Protection |
|---|---|---|---|
| Utilisateur -> Desktop | saisies, fichiers | payload malveillant | validation UI + API |
| Desktop -> API | JSON, token futur | interception, altération | HTTPS, Bearer |
| API -> Services | objets validés | contournement métier | services centralisés |
| Services -> Repositories | requêtes données | accès excessif | repositories spécialisés |
| Repositories -> DB | SQLAlchemy | injection, erreurs DB | ORM, contraintes |
| Backend -> APIs externes | prompts, clés | fuite données | filtrage, audit |
| Dépôt Git | code/docs | secret commité | gitignore, revue |

### 5.3 Variables d'environnement

Les variables d'environnement sont une frontière sensible. Elles ne doivent pas être exposées au Desktop, aux logs ou
aux réponses API.

---

## 6. Secrets et variables d'environnement

### 6.1 Règle absolue

```text
Ne jamais commiter .env, clés API, tokens, mots de passe ou secrets.
```

### 6.2 Types de secrets

| Type de secret | Où le stocker | Où ne jamais le stocker | Rotation | Risque |
|---|---|---|---|---|
| `.env` local | poste dev, non Git | dépôt Git | selon changement | fuite globale |
| `DATABASE_URL` | variable env | code source | après incident | accès DB |
| JWT secret futur | secret manager/env | docs, logs | périodique | usurpation |
| OpenAI key future | backend secret store | Desktop, Git | régulière | coûts/fuite |
| Gemini/Claude keys | backend secret store | logs | régulière | abus API |
| Refresh token | stockage sécurisé client/hash DB | logs | rotation automatique | session volée |
| Mot de passe | hash DB | clair | reset | compromission |
| API key externe | chiffrée/masquée DB future | réponse API claire | périodique | exfiltration |

### 6.3 Checklist anti-fuite avant PR

| Contrôle | OK |
|---|---|
| Aucun `.env` ajouté | |
| Aucun token dans diff | |
| Aucune clé API visible | |
| Aucun mot de passe de test réaliste | |
| Aucun secret dans docs | |
| Aucun secret dans logs ajoutés | |
| Aucun fichier temporaire sensible | |
| `.gitignore` couvre caches et env | |

### 6.4 Masquage

Toute valeur secrète affichée doit être masquée :

```text
sk-************9a2f
```

---

## 7. Sécurité Git et dépôt

### 7.1 Fichiers interdits au commit

| Fichier/dossier | Raison |
|---|---|
| `.env` | secrets |
| `.env.*` sauf exemple explicitement vide | secrets |
| `.venv/`, `venv/` | environnement local |
| `.codex_deps/` | dépendances locales |
| `__pycache__/` | artefacts |
| `.pytest_cache/` | cache test |
| `.ruff_cache/` | cache lint |
| fichiers temporaires | bruit/risque |
| clés privées | secret critique |
| exports de rapports sensibles | données métier |

### 7.2 Commandes de vérification

```powershell
git status
git diff --stat
git diff --check
```

### 7.3 Checklist Git sécurité

| Contrôle | OK |
|---|---|
| Statut Git compris | |
| Fichiers staged attendus | |
| Aucun secret dans diff | |
| Aucun fichier généré inutile | |
| Aucun déplacement non demandé | |
| Aucun document existant modifié hors périmètre | |
| Pas de commit automatique | |

---

## 8. Sécurité backend FastAPI

### 8.1 Protections

| Risque backend | Protection recommandée | Couche responsable |
|---|---|---|
| Payload invalide | Pydantic | Route/schema |
| Logique métier contournée | Services obligatoires | Route/service |
| SQL direct dangereux | SQLAlchemy repositories | Repository |
| Erreurs bavardes | Exception handlers | API |
| Admin public | Auth/RBAC futur | Dependencies |
| CORS trop large | configuration stricte | Middleware |
| Brute force | rate limiting futur | Middleware/auth |
| Secrets loggés | règles logging | Tous |
| Réponse trop large | response_model | Route/schema |

### 8.2 Règles

- Toujours utiliser `response_model`.
- Toujours valider body/query/path.
- Ne jamais mettre de logique métier dans les routes.
- Ne jamais accéder à SQLAlchemy dans les routes.
- Prévoir un format d'erreur stable.
- Protéger les routes admin dès l'auth active.

### 8.3 Middlewares futurs

| Middleware | Usage |
|---|---|
| Correlation ID | request_id |
| Security headers | durcissement HTTP |
| Rate limiting | auth/admin |
| CORS | clients web futurs |
| Request logging | observabilité sans secrets |

---

## 9. Sécurité API REST

### 9.1 Lien API_ARCHITECTURE.md

La structure des routes, codes HTTP, erreurs, pagination et versionnement est définie dans `API_ARCHITECTURE.md`.
Cette section précise les règles de sécurité transverses.

### 9.2 Matrice endpoints

| Type d'endpoint | Auth requise | Permission requise | Risque | Protection |
|---|---:|---|---|---|
| Health simple | Non | Non | faible fuite statut | réponse minimale |
| Websites read | Oui futur | `websites:read` | fuite stratégie sites | RBAC |
| Websites write | Oui futur | `websites:create/update` | corruption données | service validation |
| Admin settings | Oui | `configuration:*` | config compromise | admin + audit |
| API keys | Oui | `api_keys:*` | fuite secrets | masquage/chiffrement |
| Logs | Oui | `logs:read` | fuite technique | filtrage |
| Reports export | Oui | `reports:export` | exfiltration | audit + permissions |
| Crawler jobs | Oui | `crawler:execute` | abus réseau | quotas/rate limit |
| IA execution | Oui | `ai:execute` | coûts/fuite | quotas/audit |

### 9.3 Protection contre énumération

Pour les ressources sensibles, les erreurs doivent éviter de révéler inutilement l'existence d'une ressource quand
l'utilisateur n'a pas le droit de la voir.

### 9.4 Exports et downloads

Les exports doivent être :

- authentifiés ;
- autorisés ;
- auditables ;
- limités en taille ;
- filtrés selon permissions ;
- sans secrets.

---

## 10. Authentification et autorisation

### 10.1 Résumé

Le document `AUTHENTICATION.md` définit :

- access token ;
- refresh token ;
- JWT ;
- RBAC ;
- permissions ;
- rôles ;
- sessions Desktop ;
- expiration ;
- révocation ;
- déconnexion.

### 10.2 Matrice profils

| Profil | Accès admin | Accès SEO | Accès GEO | Accès configuration | Accès lecture |
|---|---:|---:|---:|---:|---:|
| Super Administrateur | Oui | Oui | Oui | Oui | Oui |
| Administrateur | Oui | Oui | Oui | Oui limité | Oui |
| Manager | Non | Oui partiel | Oui partiel | Non | Oui |
| Marketing | Non | Lecture/édition ciblée | Lecture/édition ciblée | Non | Oui |
| SEO | Non | Oui | Oui partiel | Non | Oui |
| Content Manager | Non | Lecture | Prompts/contenus | Non | Oui |
| Rédacteur | Non | Non | Contribution limitée | Non | Limité |
| Consultation | Non | Lecture | Lecture | Non | Oui |
| Invité | Non | Non | Non | Non | Très limité |

### 10.3 Règle

Le Desktop peut masquer une action, mais l'API doit toujours vérifier l'autorisation.

---

## 11. Sécurité Desktop PySide6

### 11.1 Règles

- Aucun accès direct PostgreSQL.
- Appels API uniquement via `ApiClient`.
- Aucun secret codé en dur.
- Tokens futurs stockés dans un stockage sécurisé.
- Erreurs API affichées proprement.
- Logs Desktop sans secrets.
- Configuration API centralisée.
- Pas de logique de permission finale côté Desktop.

### 11.2 Tableau

| Risque Desktop | Protection | Comportement attendu |
|---|---|---|
| API indisponible | gestion erreur ApiClient | message propre |
| Token volé futur | stockage sécurisé + refresh rotation | reconnexion/révocation |
| Secret dans config | pas de secret Desktop | config non sensible |
| Données sensibles affichées | masquage selon rôle futur | UI conditionnelle |
| Logs locaux sensibles | redaction | pas de token/log secret |
| Compromission client | API autoritaire | 401/403 côté serveur |

### 11.3 Mode hors ligne futur

Le mode hors ligne ne doit jamais autoriser d'écriture locale non synchronisée sur des données sensibles sans stratégie
de conflit et de chiffrement.

---

## 12. Sécurité base de données PostgreSQL

### 12.1 Principes

- Accès DB uniquement par le backend.
- Identifiants DB hors code.
- Utilisateur PostgreSQL à privilèges limités.
- Contraintes et FK fortes.
- Suppression contrôlée.
- Sauvegardes futures.
- Logs sans secrets.
- Migrations non destructives par défaut.

### 12.2 Checklist sécurité database

| Contrôle | OK |
|---|---|
| `DATABASE_URL` hors Git | |
| Pas d'accès DB Desktop | |
| FK définies | |
| Contraintes uniques critiques | |
| Suppression maîtrisée | |
| Données sensibles hashées/chiffrées | |
| Backups futurs prévus | |
| Migration relue | |

---

## 13. Sécurité des migrations Alembic

### 13.1 Règles

Les migrations doivent être explicites. Interdits :

```python
Base.metadata.create_all()
Base.metadata.drop_all()
```

À utiliser :

```python
op.create_table(...)
op.drop_table(...)
op.create_index(...)
op.drop_index(...)
```

### 13.2 Checklist migration sécurisée

| Contrôle | OK |
|---|---|
| Migration explicite | |
| Downgrade réfléchi | |
| Pas de `create_all/drop_all` | |
| Pas de secret en données initiales | |
| Suppression destructive validée | |
| Backup prévu si critique | |
| Contraintes nommées | |
| Index nécessaires | |
| Données initiales non sensibles | |

### 13.3 Données initiales

Ne jamais insérer dans une migration :

- mot de passe réel ;
- clé API ;
- token ;
- secret JWT ;
- configuration production sensible.

---

## 14. Données sensibles

### 14.1 Tableau

| Donnée | Sensibilité | Stockage | Accès | Logging autorisé |
|---|---|---|---|---|
| Mot de passe | Critique | hash | auth service | Jamais |
| Token | Critique | hash/secure store | auth | Jamais |
| Clé API externe | Critique | chiffré/masqué futur | admin restreint | Masquée |
| `.env` | Critique | filesystem local/prod secret | backend | Jamais |
| Email utilisateur | Moyen | users | admin/auth | Oui si nécessaire |
| Rôles/permissions | Élevé | DB | admin | Oui |
| Rapports SEO/GEO | Élevé | DB/fichiers futurs | permissions | Métadonnées |
| Prompts | Élevé | DB | GEO/IA roles | Prudence |
| Résultats IA | Élevé | DB/JSONB | GEO/IA roles | Métadonnées |
| Exports | Élevé | stockage contrôlé | permission export | Audit |
| Logs audit | Élevé | DB | admin | Oui contrôlé |

### 14.2 Classification

```text
Public interne
  +-- health minimal

Interne standard
  +-- dashboards
  +-- websites visibles

Confidentiel
  +-- rapports
  +-- prompts
  +-- résultats IA

Secret
  +-- mots de passe
  +-- tokens
  +-- clés API
  +-- .env
```

---

## 15. Mots de passe

### 15.1 Règles

- Jamais de stockage en clair.
- Hash obligatoire.
- Argon2id recommandé.
- bcrypt acceptable comme alternative existante.
- Longueur minimale cible : 14 caractères.
- Blocage après tentatives répétées.
- Reset par token court, usage unique.
- Historique futur pour éviter réutilisation.

### 15.2 Flux sécurisé

```text
Password input
    |
    v
Pydantic validation
    |
    v
Password policy
    |
    v
Hash Argon2id/bcrypt
    |
    v
Store hash only
```

### 15.3 Interdits

- Mot de passe dans logs.
- Mot de passe dans audit.
- Mot de passe dans exception.
- Mot de passe dans fixtures réalistes commitées.

---

## 16. Clés API externes

### 16.1 Matrice

| Service | Type de clé | Stockage recommandé | Rotation | Risque principal |
|---|---|---|---|---|
| OpenAI | API key | backend secret store/chiffré | régulière | coûts + fuite prompts |
| Gemini | API key | backend secret store/chiffré | régulière | fuite données |
| Claude | API key | backend secret store/chiffré | régulière | abus API |
| Copilot | token/key futur | secret store | selon fournisseur | accès externe |
| Perplexity | API key | secret store | régulière | fuite requêtes |
| Google Search Console | OAuth/SA | secret store | politique Google | accès SEO |
| GA4 | OAuth/SA | secret store | politique Google | analytics |
| Services SEO | API key | chiffré/masqué | régulière | coûts/exfiltration |
| Crawl externe | token | secret store | régulière | abus crawl |

### 16.2 Règles

- Jamais dans Git.
- Jamais dans Desktop.
- Jamais en clair dans logs.
- Affichage masqué dans UI.
- Test de validité via backend.
- Rotation auditée.
- Permissions admin dédiées.

### 16.3 Réponse API masquée

```json
{
  "id": 1,
  "provider": "OpenAI",
  "masked_key": "sk-************1234",
  "is_active": true
}
```

---

## 17. Validation des entrées

### 17.1 Tableau par type

| Type de champ | Validation |
|---|---|
| URL | protocole, longueur, format |
| Email | format email |
| Date | ISO 8601 |
| Booléen | true/false |
| Identifiant | int positif ou UUID |
| JSON | taille max, structure attendue |
| Prompt | longueur max, contrôle contenu futur |
| Import config | schema strict |
| Export | filtres et permissions |
| Texte | min/max, trim |

### 17.2 Règle

La validation côté Desktop améliore l'UX, mais seule la validation backend fait autorité.

### 17.3 Payload IA futur

Les prompts et payloads IA doivent être considérés comme non fiables, même s'ils viennent d'un utilisateur interne.

---

## 18. Protection contre injections

### 18.1 Types

| Injection | Protection |
|---|---|
| SQL injection | SQLAlchemy, paramètres, pas SQL brut |
| JSON injection | Pydantic, schema strict |
| Prompt injection | filtrage, isolation contexte futur |
| HTML injection | escaping affichage futur |
| Log injection | nettoyage retours ligne/contrôle |
| Export injection | échappement CSV/Excel futur |
| Rapport injection | template sûr futur |

### 18.2 Rôle des couches

| Couche | Rôle |
|---|---|
| Pydantic | structure et types |
| Service | validation métier |
| Repository | requêtes paramétrées |
| Desktop | affichage échappé |
| Exporter futur | neutralisation formules |

### 18.3 Exports CSV futurs

Neutraliser les valeurs commençant par :

```text
=
+
-
@
```

si elles peuvent être ouvertes dans un tableur.

---

## 19. Gestion des erreurs sécurisée

### 19.1 Règles

- Ne pas exposer stack trace.
- Ne pas exposer SQL brut.
- Ne pas exposer chemin serveur.
- Ne pas exposer secrets.
- Fournir un message propre.
- Fournir un `request_id` futur.
- Logger détails techniques côté serveur seulement.

### 19.2 Catalogue

| Erreur | Message utilisateur | Log interne | Données interdites |
|---|---|---|---|
| DB down | Service temporairement indisponible | exception DB + request_id | DATABASE_URL |
| Token expiré | Session expirée | user/session id | token brut |
| Permission | Accès refusé | user + permission | secrets |
| Validation | Champs invalides | détails champs | payload sensible complet |
| API externe | Service externe indisponible | provider + code | API key |
| Erreur serveur | Erreur technique | stack trace interne | réponse au client |

### 19.3 Format cible

```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Le service est temporairement indisponible.",
    "details": null,
    "request_id": "req_..."
  }
}
```

---

## 20. Journalisation sécurisée

### 20.1 Quoi journaliser

- démarrage/arrêt backend ;
- erreurs API ;
- refus permission ;
- actions admin ;
- imports/exports ;
- rotations futures de clés ;
- erreurs connecteurs externes ;
- tentatives de connexion futures.

### 20.2 Quoi ne jamais journaliser

- mots de passe ;
- tokens ;
- clés API brutes ;
- `.env` ;
- secrets JWT ;
- payloads IA contenant données sensibles sans filtrage ;
- exports complets.

### 20.3 Tableau événements

| Événement | Niveau | Données autorisées | Données interdites |
|---|---|---|---|
| Login échoué futur | WARNING | email, IP, raison générique | mot de passe |
| Permission refusée | WARNING | user_id, permission | token |
| Config import | INFO/WARNING | acteur, résultat | secrets importés |
| API key updated | WARNING | provider, actor | clé brute |
| Report exported | INFO | report_id, actor | contenu complet |
| External API error | ERROR | provider, code | clé API |
| DB error | ERROR | request_id | URL DB |

---

## 21. Audit

### 21.1 Matrice audit

| Action | Acteur | Ressource | Données à conserver | Durée future |
|---|---|---|---|---|
| Création utilisateur | admin | user | actor, target, date | 1 an+ |
| Modification rôle | admin | role/user | ancien/nouveau rôle | 1 an+ |
| Modification permission | super admin | role/permission | permission | 1 an+ |
| Import configuration | admin | configuration | statut, erreurs | 1 an |
| Export configuration | admin | configuration | format, date | 1 an |
| Modification website | user | website | champs modifiés | 1 an |
| Suppression | user/admin | ressource | type, id, raison | 1 an+ |
| Génération rapport | user | report | type, période | 1 an |
| Appel IA sensible | user/system | provider/model | métadonnées | selon politique |
| Changement clé API | admin | provider | rotation, masque | 1 an+ |

### 21.2 Règles

- Audit append-only.
- Pas de secrets dans audit.
- Actions admin toujours auditées.
- Suppressions toujours auditées.
- Exports sensibles audités.

---

## 22. Sécurité des imports/exports

### 22.1 Import configuration

Risques :

- écrasement ;
- doublons ;
- payload malformé ;
- secrets en clair ;
- configuration non compatible.

Protections :

- permission admin ;
- schema strict ;
- dry-run futur ;
- idempotence ;
- audit ;
- backup avant import critique.

### 22.2 Export configuration

Règles :

- ne jamais exporter secrets bruts ;
- masquer clés API ;
- filtrer selon permissions ;
- auditer l'action ;
- documenter le format.

### 22.3 Lien API_ADMINISTRATION.md

Le module administration définit les endpoints d'import/export. La présente section impose les règles de sécurité
transverses qui doivent les encadrer.

---

## 23. Sécurité IA / GEO future

### 23.1 Tableau risques

| Risque IA/GEO | Impact | Protection recommandée |
|---|---|---|
| Fuite de prompts | stratégie exposée | permissions + logs sans contenu sensible |
| Fuite données internes | confidentialité | minimisation avant appel externe |
| Prompt injection | résultats manipulés | isolation contexte, validation |
| Résultats non fiables | mauvaises décisions | score de confiance, revue humaine |
| Clé IA compromise | coûts/fuite | rotation + secret store |
| Quotas dépassés | indisponibilité/coût | quotas par module |
| Logs trop détaillés | fuite | redaction |
| Stockage réponses IA | données sensibles | classification et rétention |

### 23.2 Règles d'appel IA

- Ne jamais appeler un modèle IA depuis le Desktop directement.
- Toujours passer par backend/connecteurs futurs.
- Ne pas envoyer de secrets dans les prompts.
- Journaliser métadonnées, pas nécessairement contenu complet.
- Prévoir audit pour exécutions sensibles.

---

## 24. Sécurité Crawler future

### 24.1 Risques

- surcharge d'un site ;
- crawl non autorisé ;
- HTML malveillant ;
- timeouts ;
- stockage massif ;
- SSRF futur si URLs arbitraires ;
- user-agent non identifié.

### 24.2 Protections

| Sujet | Protection |
|---|---|
| robots.txt | respect futur si applicable |
| limites | profondeur, nombre URLs, débit |
| timeouts | bornes strictes |
| user-agent | identifié |
| URLs | validation domaine autorisé |
| HTML | traiter comme non fiable |
| stockage | taille maximale |
| audit | acteur, site, paramètres |

---

## 25. Sécurité des rapports

### 25.1 Données

Les rapports peuvent contenir :

- performances SEO ;
- visibilité GEO ;
- concurrents ;
- recommandations ;
- données de configuration ;
- résultats IA.

### 25.2 Protections

- permission `reports:read/export` ;
- audit export ;
- suppression contrôlée ;
- archivage ;
- watermark futur ;
- liens de téléchargement expirables futurs ;
- pas de secrets dans rapports.

### 25.3 Exports PDF/CSV futurs

Les exports doivent neutraliser :

- formules tableur ;
- HTML non échappé ;
- données non autorisées ;
- métadonnées sensibles.

---

## 26. Sécurité réseau

### 26.1 Production

| Sujet | Règle |
|---|---|
| HTTPS | obligatoire |
| CORS | strict, pas wildcard |
| Ports | exposer uniquement nécessaire |
| Reverse proxy | futur durcissement |
| Certificats | valides et renouvelés |
| Timeouts | bornés |
| Taille requête | limitée |
| Firewall | restreindre DB |

### 26.2 Headers futurs

| Header | Usage |
|---|---|
| `Strict-Transport-Security` | HTTPS |
| `X-Content-Type-Options` | éviter sniffing |
| `Content-Security-Policy` | clients web futurs |
| `Referrer-Policy` | confidentialité |

---

## 27. Dépendances et supply chain

### 27.1 Dépendances principales

| Dépendance | Risque | Protection |
|---|---|---|
| FastAPI | vulnérabilité API | mises à jour |
| SQLAlchemy | injection/ORM bug | versions suivies |
| Alembic | migration | revue |
| Pydantic | validation | versions suivies |
| PySide6 | client Desktop | mises à jour |
| httpx | HTTP | versions suivies |

### 27.2 Checklist dépendances

| Contrôle | OK |
|---|---|
| Dépendance nécessaire | |
| Version compatible | |
| Projet maintenu | |
| Vulnérabilités connues vérifiées futur | |
| Pas de dépendance inutile | |
| Pas de dépendance depuis source non fiable | |
| Changelog lu pour upgrade majeur | |

### 27.3 Pinning

Le pinning exact peut être décidé selon stratégie projet. Les versions minimales doivent être revues régulièrement.

---

## 28. Environnements

### 28.1 Tableau

| Environnement | Données réelles | Secrets réels | Logs | Restrictions |
|---|---:|---:|---|---|
| Développement | Non | Non sauf clés dev | locaux | debug contrôlé |
| Test | Non | Non | temporaires | isolation |
| Staging futur | Données anonymisées si possible | secrets staging | centralisés | accès limité |
| Production future | Oui | Oui | centralisés sécurisés | accès strict |

### 28.2 Séparation

- Base dev différente de prod.
- Clés API dev différentes de prod.
- Logs dev non mélangés avec prod.
- Aucun export prod dans Git.

---

## 29. RGPD et conformité

### 29.1 Principes techniques

| Principe | Application |
|---|---|
| Minimisation | ne stocker que nécessaire |
| Limitation conservation | purge logs future |
| Droit d'accès futur | identifier données utilisateur |
| Droit suppression futur | soft delete/anonymisation |
| Sécurité comptes | hash, RBAC, audit |
| Exports | traçables et limités |

### 29.2 Données personnelles probables

- emails ;
- noms utilisateurs ;
- rôles ;
- logs de connexion ;
- actions d'administration.

Ce document ne constitue pas un avis juridique. Il définit les protections techniques nécessaires pour faciliter une
conformité future.

---

## 30. OWASP

### 30.1 Matrice

| Risque OWASP | Application au projet | Protection prévue | Document lié |
|---|---|---|---|
| Broken Access Control | endpoints admin | RBAC, permissions | AUTHENTICATION |
| Cryptographic Failures | secrets/tokens | hash, env, HTTPS | SECURITY |
| Injection | SQL/JSON/prompt | SQLAlchemy, Pydantic | BACKEND |
| Insecure Design | sécurité tardive | Security by Design | SECURITY |
| Security Misconfiguration | CORS/env | checklists prod | SECURITY |
| Vulnerable Components | dépendances | audit updates | SECURITY |
| Auth Failures | login futur | tokens, blocage | AUTHENTICATION |
| Data Integrity Failures | migrations/imports | Alembic explicite | DATABASE |
| Logging Failures | logs absents/secrets | logging sécurisé | SECURITY |
| SSRF futur | crawler/API externes | validation URLs | SECURITY |

---

## 31. Sauvegardes et reprise

### 31.1 Principes

- Backup PostgreSQL futur.
- Backup avant migration critique.
- Test de restauration périodique.
- Rétention documentée.
- Backups chiffrés selon infrastructure.
- Accès backups restreint.

### 31.2 Scénarios de reprise

| Scénario | Réponse |
|---|---|
| Migration échouée | rollback ou restore |
| Suppression accidentelle | restore point-in-time futur |
| Clé API compromise | rotation + audit |
| DB corrompue | restore backup |
| Rapport supprimé | restore/soft delete |

---

## 32. Gestion des incidents

### 32.1 Checklist incident

| Étape | OK |
|---|---|
| Identifier l'incident | |
| Isoler le périmètre | |
| Révoquer secrets/tokens si besoin | |
| Désactiver compte compromis | |
| Sauvegarder preuves/logs | |
| Corriger la cause | |
| Déployer correctif | |
| Documenter l'incident | |
| Mettre à jour checklists | |

### 32.2 Incidents types

| Incident | Action immédiate |
|---|---|
| Secret dans Git | révoquer secret, supprimer historique si nécessaire |
| Clé API compromise | rotation, audit usages |
| Compte compromis | désactiver, révoquer sessions |
| Dépendance vulnérable | mise à jour, tests |
| Suppression accidentelle | stopper, restaurer backup |

---

## 33. Sécurité avant mise en production

### 33.1 Checklist production

| Contrôle | OK |
|---|---|
| `.env` absent du dépôt | |
| Secrets changés | |
| HTTPS actif | |
| CORS strict | |
| JWT secret fort futur | |
| Admin par défaut changé/désactivé | |
| Logs vérifiés sans secrets | |
| Sauvegardes configurées | |
| Restauration testée | |
| Migrations validées | |
| Endpoints admin protégés | |
| Tests sécurité passés | |
| Dépendances vérifiées | |
| Debug désactivé | |

---

## 34. Tests de sécurité

### 34.1 Types

| Test | Objectif |
|---|---|
| Auth futur | 401/refresh/logout |
| Permissions | 403 par rôle |
| Admin | endpoints protégés |
| Validation | payloads invalides |
| Erreurs | pas de stack trace |
| Rate limiting futur | brute force |
| Secrets | aucun secret dans logs/diff |
| Imports/exports | secrets masqués |
| Non-régression | scénarios critiques |

### 34.2 Commandes

```powershell
py -m pytest
py -m ruff check .
```

### 34.3 Checklist tests sécurité

| Contrôle | OK |
|---|---|
| 401 testé futur | |
| 403 testé futur | |
| Payload invalide testé | |
| Endpoint admin testé | |
| Erreurs propres testées | |
| Aucun secret dans fixtures | |
| Exports sans secrets | |

---

## 35. Anti-patterns interdits

### 35.1 Tableau

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Secret dans le code | fuite durable | `.env`/secret store |
| `.env` commité | fuite complète | gitignore + revue |
| Token dans log | session compromise | redaction |
| Endpoint admin non protégé | escalade | RBAC |
| Mot de passe en clair | compromission | hash |
| Erreur technique exposée | fuite info | message contrôlé |
| Accès DB depuis Desktop | violation majeure | API REST |
| Accès DB depuis route | contournement architecture | repository |
| Permission codée partout | incohérence | dépendance centralisée |
| Suppression sans audit | perte traçabilité | service + audit |
| Export avec secrets | exfiltration | masquage |
| Clé API affichée en clair | fuite | masked_key |
| CORS wildcard prod | exposition | allowlist |
| Migration destructive non validée | perte données | backup + validation |

---

## 36. Pattern officiel pour ajouter une fonctionnalité sensible

### 36.1 Étapes

1. Identifier les données sensibles.
2. Définir les permissions.
3. Définir les validations.
4. Vérifier les logs.
5. Vérifier les erreurs.
6. Vérifier les exports.
7. Vérifier l'audit.
8. Ajouter tests.
9. Mettre à jour documentation.
10. Faire une revue sécurité avant PR.

### 36.2 Checklist

| Contrôle | OK |
|---|---|
| Données sensibles listées | |
| Permission définie | |
| Endpoint protégé | |
| Validation Pydantic | |
| Validation service | |
| Logs sans secrets | |
| Erreurs non bavardes | |
| Audit prévu | |
| Export sécurisé | |
| Tests ajoutés | |
| Documentation mise à jour | |

### 36.3 Diagramme

```text
Feature sensible
      |
      v
Data classification
      |
      v
Permissions + validation
      |
      v
Logging + audit review
      |
      v
Tests sécurité
      |
      v
Pull Request
```

---

## 37. Checklist avant Pull Request sécurité

| Contrôle | Commande ou action | OK |
|---|---|---|
| Statut Git | `git status` | |
| Stat diff | `git diff --stat` | |
| Espaces | `git diff --check` | |
| Tests | `py -m pytest` | |
| Ruff | `py -m ruff check .` | |
| Aucun secret | revue diff | |
| Aucun `.env` | revue status | |
| Aucun log sensible | revue code | |
| Endpoints protégés | revue routes | |
| Erreurs propres | revue handlers | |
| Permissions vérifiées | revue auth | |
| Documentation à jour | docs | |

---

## 38. Roadmap sécurité

### 38.1 Phase 1 - Règles Git et secrets

- `.env` ignoré ;
- checklists PR ;
- revue secrets ;
- documentation sécurité.

### 38.2 Phase 2 - Auth JWT

- login ;
- access token ;
- refresh token ;
- expiration ;
- révocation.

### 38.3 Phase 3 - RBAC complet

- rôles ;
- permissions ;
- endpoints protégés ;
- menus Desktop conditionnels.

### 38.4 Phase 4 - Audit logs

- actions admin ;
- exports ;
- modifications critiques ;
- erreurs sécurité.

### 38.5 Phase 5 - API keys chiffrées

- stockage sécurisé ;
- masquage ;
- rotation ;
- audit.

### 38.6 Phase 6 - Rate limiting

- login ;
- refresh ;
- admin ;
- IA ;
- crawler.

### 38.7 Phase 7 - MFA futur

- TOTP ;
- passkeys ;
- comptes admin prioritaires.

### 38.8 Phase 8 - Monitoring sécurité

- métriques ;
- alertes ;
- logs centralisés ;
- détection anomalies.

### 38.9 Phase 9 - Backups et production

- sauvegardes ;
- restauration testée ;
- HTTPS ;
- CORS strict ;
- durcissement.

### 38.10 Phase 10 - Revue v1.0

- revue architecture ;
- revue OWASP ;
- tests sécurité ;
- documentation finalisée.

---

## 39. Annexes

### 39.1 Glossaire

| Terme | Définition |
|---|---|
| Secret | Donnée permettant un accès ou une signature |
| Token | Jeton d'accès ou de session |
| RBAC | Contrôle d'accès par rôles |
| Audit | Trace durable d'une action importante |
| Least Privilege | Accès minimal nécessaire |
| Zero Trust | Aucune confiance implicite |
| Defense in Depth | Protections superposées |
| Prompt injection | Manipulation d'un modèle IA via prompt |
| SSRF | Server-Side Request Forgery |

### 39.2 Abréviations

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| DB | Database |
| JWT | JSON Web Token |
| MFA | Multi-Factor Authentication |
| RBAC | Role-Based Access Control |
| RGPD | Règlement général sur la protection des données |
| OWASP | Open Worldwide Application Security Project |
| SEO | Search Engine Optimization |
| GEO | Generative Engine Optimization |

### 39.3 Matrice rapide des risques

| Risque | Priorité | Document principal |
|---|---:|---|
| Secret dans Git | Critique | SECURITY |
| Auth insuffisante | Critique | AUTHENTICATION |
| Endpoint admin public | Critique | API |
| Migration destructive | Élevée | DATABASE |
| Desktop -> DB | Critique | DESKTOP |
| Export sensible | Élevée | API/SECURITY |
| Prompt injection | Moyenne à élevée | SECURITY |

### 39.4 Checklist rapide développeur

| Question | Réponse attendue |
|---|---|
| Ai-je ajouté un secret ? | Non |
| Ai-je exposé une donnée sensible ? | Non |
| L'endpoint est-il protégé si nécessaire ? | Oui |
| Les erreurs sont-elles propres ? | Oui |
| Les logs sont-ils sans secrets ? | Oui |
| Les permissions sont-elles centralisées ? | Oui |
| L'export masque-t-il les secrets ? | Oui |
| Les tests couvrent-ils le cas sécurité ? | Oui |

### 39.5 Checklist production rapide

| Contrôle | OK |
|---|---|
| HTTPS | |
| CORS strict | |
| Secrets production séparés | |
| Admin sécurisé | |
| Logs sans secrets | |
| Backups actifs | |
| Dépendances revues | |
| Tests sécurité | |
| Migrations validées | |

### 39.6 Liens internes

| Sujet | Document |
|---|---|
| UI/UX | `docs/UI_UX.md` |
| Auth/RBAC | `docs/architecture/AUTHENTICATION.md` |
| API | `docs/architecture/API_ARCHITECTURE.md` |
| Backend | `docs/architecture/BACKEND_ARCHITECTURE.md` |
| Database | `docs/architecture/DATABASE_ARCHITECTURE.md` |
| Desktop | `docs/architecture/DESKTOP_ARCHITECTURE.md` |
| Administration | `docs/api/API_ADMINISTRATION.md` |

### 39.7 Résumé architectural

La sécurité de Veille SEO-GEO Groupe A.P&Partner repose sur une application stricte des principes Security by Design,
Least Privilege, Zero Trust, Defense in Depth, Secure Defaults et Auditability.

Le Desktop appelle uniquement l'API. L'API valide, authentifie et autorise. Le backend applique les règles métier. Les
repositories accèdent seuls à PostgreSQL. Les secrets restent hors dépôt, hors logs et hors Desktop. Les actions
sensibles doivent être protégées, auditées et testées.

Cette spécification est la référence globale pour toute décision de sécurité jusqu'à la version 1.0.
