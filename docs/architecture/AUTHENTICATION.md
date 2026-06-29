# Software Authentication Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle d'authentification et d'autorisation  
Version du document : 1.0  
Statut : Référence d'architecture  
Périmètre : Desktop PySide6, API FastAPI, services d'authentification, RBAC, sessions, audit  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Vue d'ensemble](#2-vue-densemble)
3. [Terminologie](#3-terminologie)
4. [Modèle de sécurité](#4-modèle-de-sécurité)
5. [Flux d'authentification](#5-flux-dauthentification)
6. [Architecture JWT](#6-architecture-jwt)
7. [Authentification Desktop](#7-authentification-desktop)
8. [Authentification API](#8-authentification-api)
9. [Architecture RBAC](#9-architecture-rbac)
10. [Permissions](#10-permissions)
11. [Politique de sécurité](#11-politique-de-sécurité)
12. [Sessions](#12-sessions)
13. [Journalisation](#13-journalisation)
14. [Audit](#14-audit)
15. [API](#15-api)
16. [Base de données](#16-base-de-données)
17. [Interface Desktop](#17-interface-desktop)
18. [Cas d'erreurs](#18-cas-derreurs)
19. [Évolutions futures](#19-évolutions-futures)
20. [Checklist](#20-checklist)
21. [Annexes](#21-annexes)

---

## 1. Présentation

### 1.1 Présentation générale

Veille SEO-GEO Groupe A.P&Partner est une plateforme interne destinée à centraliser le pilotage SEO, GEO et IA du
groupe. L'application combine un client Desktop PySide6 et une API REST FastAPI. Le Desktop ne communique jamais
directement avec PostgreSQL : toute opération passe par l'API, puis par les services métier, les repositories et les
modèles SQLAlchemy.

L'authentification et l'autorisation sont des fondations critiques. Elles protègent :

- les données des entités du groupe ;
- les performances SEO et GEO ;
- les configurations de connecteurs externes ;
- les clés API et paramètres IA ;
- les rapports stratégiques ;
- les journaux d'audit ;
- les comptes utilisateurs, rôles et permissions.

Ce document définit l'architecture cible à respecter jusqu'à la version 1.0. Il ne décrit pas une implémentation
FastAPI particulière ; il définit les contrats, les responsabilités, les flux, les tables, les erreurs, les règles de
sécurité et les comportements attendus côté Desktop.

### 1.2 Vision

La vision sécurité du projet est :

> Une architecture d'identité centralisée, traçable et évolutive, où chaque action sensible est authentifiée,
> autorisée, journalisée et révoquable, sans jamais exposer la base PostgreSQL au client Desktop.

L'utilisateur doit pouvoir travailler efficacement, mais l'application doit refuser silencieusement toute hypothèse de
confiance implicite. Chaque requête API est traitée comme non fiable jusqu'à validation complète de l'identité, du
jeton, de la session et des permissions.

### 1.3 Objectifs

| Objectif | Description | Impact |
|---|---|---|
| Authentifier | Vérifier l'identité réelle de l'utilisateur | Accès contrôlé |
| Autoriser | Vérifier les droits sur chaque module/action | Moindre privilège |
| Tracer | Enregistrer les événements importants | Audit et conformité |
| Révoquer | Couper immédiatement une session ou un refresh token | Réponse incident |
| Expirer | Limiter la durée d'exposition des jetons | Réduction du risque |
| Segmenter | Séparer utilisateurs, rôles, permissions et sessions | Maintenabilité |
| Étendre | Préparer MFA, SSO, OIDC, comptes de service | Pérennité |

### 1.4 Pourquoi une architecture de sécurité robuste

Le projet manipule des données internes à forte valeur :

- stratégie de visibilité des marques ;
- performances des sites ;
- historiques de mots-clés ;
- prompts et résultats IA ;
- configurations API externes ;
- journaux de sécurité ;
- droits administrateurs.

Une architecture faible exposerait le projet à :

- accès non autorisé ;
- fuite de données ;
- modification frauduleuse de rapports ;
- suppression de sites ou mots-clés ;
- exécution non maîtrisée de connecteurs IA ;
- contournement des permissions ;
- impossibilité d'auditer une action.

### 1.5 Principes Security by Design

| Principe | Règle projet |
|---|---|
| Sécurité par défaut | Un utilisateur sans permission explicite n'a aucun accès métier |
| Validation systématique | Chaque requête authentifiée valide token, session et permissions |
| Séparation des responsabilités | Routes, services, authorization service et repositories ont des rôles distincts |
| Secrets protégés | Aucun secret dans le code, les logs ou les réponses API |
| Échec sécurisé | En cas d'incertitude, refuser l'accès |
| Traçabilité | Les actions sensibles produisent des événements d'audit |
| Révocabilité | Sessions et refresh tokens peuvent être invalidés |
| Minimisation | Les tokens contiennent seulement les claims nécessaires |

### 1.6 Principes Least Privilege

Le principe de moindre privilège impose qu'un utilisateur dispose uniquement des droits nécessaires à son rôle courant.

Exemples :

- un rédacteur peut consulter et proposer du contenu, mais ne peut pas modifier les connecteurs API ;
- un profil SEO peut lancer un audit SEO, mais ne peut pas supprimer un utilisateur ;
- un manager peut consulter les rapports et valider certaines actions, mais ne peut pas changer la politique de mot de passe ;
- un invité peut lire certains rapports publiés, mais ne peut ni exporter ni modifier.

### 1.7 Principes Zero Trust

Zero Trust signifie :

- ne jamais faire confiance à une requête parce qu'elle vient du Desktop officiel ;
- ne jamais supposer qu'un token est valide sans vérification cryptographique ;
- ne jamais supposer qu'un compte existe encore ;
- ne jamais supposer qu'une session n'a pas été révoquée ;
- ne jamais accepter une permission côté client sans vérification serveur ;
- ne jamais exposer PostgreSQL au Desktop.

### 1.8 Objectifs de l'architecture

| Domaine | Objectif v1.0 |
|---|---|
| Authentification | Login/password sécurisé avec tokens courts |
| Autorisation | RBAC fin par module et action |
| Sessions | Refresh rotation, révocation, timeout |
| Desktop | Stockage sécurisé, refresh automatique, UX claire |
| API | Bearer token obligatoire pour endpoints privés |
| Audit | Événements utilisateur, admin, API et sécurité |
| Base | Tables normalisées, index, contraintes |
| Évolutions | Préparation MFA, OIDC, SSO et comptes de service |

---

## 2. Vue d'ensemble

### 2.1 Architecture générale

```text
+---------------------------+
| Desktop PySide6           |
| - Login UI                |
| - Secure token storage    |
| - ApiClient REST          |
+-------------+-------------+
              |
              | HTTPS / Authorization: Bearer <access_token>
              v
+-------------+-------------+
| FastAPI REST API          |
| - Routes                  |
| - Dependencies            |
| - Middleware              |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Authentication Service    |
| - Password verification   |
| - JWT creation            |
| - Refresh rotation        |
| - Revocation checks       |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Authorization Service     |
| - RBAC                    |
| - Permissions             |
| - Policy checks           |
+-------------+-------------+
              |
              v
+-------------+-------------+
| Repositories              |
| - Users                   |
| - Roles                   |
| - Permissions             |
| - Sessions                |
+-------------+-------------+
              |
              v
+-------------+-------------+
| PostgreSQL                |
| - users                   |
| - roles                   |
| - permissions             |
| - refresh_tokens          |
| - audit_logs              |
+---------------------------+
```

### 2.2 Vue logique

```text
Identity Layer
  |
  +-- User identity
  +-- Credentials
  +-- Session state
  +-- Token lifecycle

Access Control Layer
  |
  +-- Roles
  +-- Permissions
  +-- Module policies
  +-- Action policies

Application Layer
  |
  +-- Dashboard
  +-- Websites
  +-- Entities
  +-- Keywords
  +-- Competitors
  +-- SEO
  +-- GEO
  +-- IA
  +-- Reports
  +-- Administration

Audit Layer
  |
  +-- Login history
  +-- Security events
  +-- Admin changes
  +-- API access logs
```

### 2.3 Vue physique

```text
Utilisateur
  |
  | Desktop Windows
  v
+--------------------+        HTTPS        +--------------------+
| PySide6 Desktop    | ------------------> | FastAPI Backend    |
| Local secure store | <------------------ | Uvicorn / ASGI     |
+--------------------+                     +----------+---------+
                                                       |
                                                       | SQLAlchemy
                                                       v
                                            +----------+---------+
                                            | PostgreSQL         |
                                            | Auth + business DB |
                                            +--------------------+
```

### 2.4 Vue des composants

```text
Desktop
  |
  +-- LoginWindow
  +-- SessionManager
  +-- TokenStore
  +-- ApiClient
  +-- PermissionAwareNavigation

API
  |
  +-- Auth Routes
  +-- CurrentUser Dependency
  +-- Permission Dependency
  +-- AuthenticationService
  +-- AuthorizationService
  +-- TokenService
  +-- PasswordService
  +-- AuditService

Persistence
  |
  +-- UserRepository
  +-- RoleRepository
  +-- PermissionRepository
  +-- RefreshTokenRepository
  +-- LoginHistoryRepository
  +-- AuditLogRepository
```

### 2.5 Règle de frontière Desktop/API

| Interdit | Autorisé |
|---|---|
| Desktop -> PostgreSQL direct | Desktop -> API REST |
| Desktop vérifie les permissions seul | API vérifie les permissions |
| Desktop stocke mot de passe | Desktop stocke tokens selon politique sécurisée |
| Desktop décide qu'une session est valide | API confirme via token/session |
| Desktop lit les rôles en base | API retourne `/me` et permissions effectives |

### 2.6 Flux standard d'une requête privée

```text
Desktop
  |
  | GET /api/v1/websites
  | Authorization: Bearer access_token
  v
FastAPI route
  |
  v
Token validation
  |
  v
User active check
  |
  v
Session/revocation check
  |
  v
Permission check: websites:read
  |
  v
WebsiteService
  |
  v
WebsiteRepository
  |
  v
PostgreSQL
```

---

## 3. Terminologie

### 3.1 Glossaire d'identité

| Terme | Définition projet |
|---|---|
| Utilisateur | Personne physique ou acteur interne disposant d'un compte applicatif |
| Compte | Enregistrement persistant dans `users`, lié à une identité et à un état |
| Session | Période d'utilisation authentifiée, liée à un refresh token ou identifiant de session |
| Identité | Ensemble stable des informations permettant de reconnaître un utilisateur |
| Credential | Secret ou preuve utilisée pour authentifier, par exemple mot de passe |
| Authentification | Processus qui vérifie l'identité de l'utilisateur |
| Autorisation | Processus qui vérifie si l'utilisateur peut effectuer une action |
| Principal | Entité authentifiée utilisée par l'API pour prendre une décision d'accès |

### 3.2 Glossaire JWT

| Terme | Définition |
|---|---|
| JWT | JSON Web Token signé, transportant des claims |
| Access Token | Token court utilisé pour appeler l'API |
| Refresh Token | Token long permettant d'obtenir un nouvel access token |
| Claim | Champ déclaratif dans le payload JWT |
| Header | Partie JWT indiquant type et algorithme |
| Payload | Partie JWT contenant les claims |
| Signature | Partie garantissant intégrité et authenticité |
| Audience (`aud`) | Destinataire prévu du token |
| Issuer (`iss`) | Émetteur du token, l'API du projet |
| Subject (`sub`) | Identifiant du compte utilisateur |
| JTI (`jti`) | Identifiant unique du token |
| Expiration (`exp`) | Date limite de validité |
| Issued At (`iat`) | Date d'émission |
| Not Before (`nbf`) | Date avant laquelle le token est invalide |

### 3.3 Glossaire autorisation

| Terme | Définition |
|---|---|
| Permission | Droit atomique, par exemple `websites:read` |
| Rôle | Groupe de permissions attribué à un utilisateur |
| RBAC | Role-Based Access Control, autorisation basée sur les rôles |
| ACL | Access Control List, liste de droits par ressource spécifique |
| Scope | Portée d'un token ou droit d'accès déclaré |
| Policy | Règle d'autorisation métier |
| Effective permissions | Permissions finales calculées via rôles et restrictions |

### 3.4 Glossaire session

| Terme | Définition |
|---|---|
| Refresh Rotation | Création d'un nouveau refresh token à chaque renouvellement |
| Revocation | Invalidation explicite d'un token ou d'une session |
| Blacklist | Liste des tokens révoqués ou JTI interdits |
| Expiration | Fin de validité programmée |
| Timeout | Délai maximal avant échec d'une opération |
| Idle Timeout | Expiration après inactivité |
| Absolute Timeout | Expiration maximale même avec activité |
| Device Binding | Association optionnelle d'une session à un poste |

### 3.5 Glossaire audit

| Terme | Définition |
|---|---|
| Audit log | Événement durable décrivant une action importante |
| Login history | Historique des connexions et échecs |
| Security event | Événement lié à la sécurité |
| Actor | Utilisateur ou système ayant déclenché l'action |
| Target | Ressource concernée par l'action |
| Correlation ID | Identifiant reliant plusieurs logs d'une même opération |

---

## 4. Modèle de sécurité

### 4.1 Principes du modèle

Le modèle de sécurité repose sur cinq couches :

```text
1. Transport sécurisé
2. Authentification de l'utilisateur
3. Validation de session/token
4. Autorisation RBAC
5. Audit et journalisation
```

### 4.2 Diagramme de décision d'accès

```text
Requête API reçue
       |
       v
Endpoint public ?
   |          |
  Oui        Non
   |          |
   v          v
 Traiter   Token présent ?
              |        |
             Non      Oui
              |        |
              v        v
            401     Token valide ?
                       |       |
                      Non     Oui
                       |       |
                       v       v
                      401   User actif ?
                               |      |
                              Non    Oui
                               |      |
                               v      v
                              403  Session révoquée ?
                                      |      |
                                     Oui    Non
                                      |      |
                                      v      v
                                     401  Permission OK ?
                                             |      |
                                            Non    Oui
                                             |      |
                                             v      v
                                            403   Service métier
```

### 4.3 Cycle de vie d'une identité

```text
Invitation ou création admin
        |
        v
Compte créé
        |
        v
Mot de passe initial défini
        |
        v
Compte actif
        |
        +--> Connexions et sessions
        |
        +--> Changement de rôles
        |
        +--> Changement de mot de passe
        |
        +--> Blocage temporaire
        |
        +--> Désactivation
        |
        v
Compte archivé ou supprimé selon politique RGPD
```

### 4.4 États d'un compte

| État | Description | Connexion | Action admin |
|---|---|---:|---|
| Pending | Compte créé mais non activé | Non | Activer, renvoyer invitation |
| Active | Compte utilisable | Oui | Modifier rôles, désactiver |
| Locked | Bloqué après échecs ou décision admin | Non | Débloquer |
| PasswordExpired | Mot de passe à renouveler | Limité | Forcer changement |
| Disabled | Désactivé | Non | Réactiver ou archiver |
| Deleted | Suppression logique | Non | Non réversible sans restauration |

### 4.5 Flux d'autorisation métier

```text
Route: POST /api/v1/reports
        |
        v
Permission requise: reports:create
        |
        v
Policy: l'utilisateur peut-il créer pour cette entité ?
        |
        v
Policy: quota ou limite applicable ?
        |
        v
Service métier
```

### 4.6 Séparation authentication/authorization

| Couche | Responsabilité | Ne doit pas faire |
|---|---|---|
| AuthenticationService | Vérifier identité, créer tokens | Décider des droits métier |
| AuthorizationService | Vérifier rôles et permissions | Vérifier les mots de passe |
| Routes | Déclarer dépendances d'accès | Porter la logique métier |
| Services métier | Appliquer règles fonctionnelles | Lire directement les tokens |
| Repositories | Persister et lire les données | Prendre des décisions de sécurité |

---

## 5. Flux d'authentification

### 5.1 Connexion

```text
Desktop              API Route             AuthService          UserRepository        TokenService
   | POST /login        |                       |                      |                    |
   | email/password     |                       |                      |                    |
   |------------------->|                       |                      |                    |
   |                    | validate payload      |                      |                    |
   |                    |---------------------->|                      |                    |
   |                    |                       | find user by email   |                    |
   |                    |                       |--------------------->|                    |
   |                    |                       | user + password hash |                    |
   |                    |                       |<---------------------|                    |
   |                    |                       | verify password      |                    |
   |                    |                       | check account state  |                    |
   |                    |                       | create session       |                    |
   |                    |                       |------------------------------------------->|
   |                    |                       | access + refresh                         |
   |                    |                       |<-------------------------------------------|
   | 200 tokens + user  |                       |                      |                    |
   |<-------------------|                       |                      |                    |
```

### 5.2 Validation d'une requête authentifiée

```text
Desktop                 FastAPI Dependency          TokenService          AuthorizationService
   | GET /websites             |                         |                         |
   | Bearer access_token       |                         |                         |
   |-------------------------->|                         |                         |
   |                           | decode + verify         |                         |
   |                           |------------------------>|                         |
   |                           | claims                  |                         |
   |                           |<------------------------|                         |
   |                           | load current user       |                         |
   |                           | check websites:read     |                         |
   |                           |--------------------------------------------------->|
   |                           | allowed                 |                         |
   |                           |<---------------------------------------------------|
   | 200 data                  |                         |                         |
   |<--------------------------|                         |                         |
```

### 5.3 Création Access Token

```text
Inputs
  |
  +-- user_id
  +-- session_id
  +-- roles_version
  +-- audience
  +-- issuer
  +-- expiration
  |
  v
Claims minimalistes
  |
  v
Signature
  |
  v
Access Token court
```

### 5.4 Création Refresh Token

```text
Generate random secure token
        |
        v
Hash refresh token
        |
        v
Store hash in refresh_tokens
        |
        v
Return raw token once to Desktop
        |
        v
Desktop stores in secure storage
```

### 5.5 Renouvellement

```text
Desktop              API /refresh          AuthService          RefreshTokenRepo      TokenService
   | refresh_token       |                      |                       |                  |
   |-------------------->|                      |                       |                  |
   |                     | validate             |                       |                  |
   |                     |--------------------->|                       |                  |
   |                     |                      | hash + lookup         |                  |
   |                     |                      |---------------------->|                  |
   |                     |                      | token record          |                  |
   |                     |                      |<----------------------|                  |
   |                     |                      | check expiry/revoked  |                  |
   |                     |                      | revoke old token      |                  |
   |                     |                      | create new refresh    |                  |
   |                     |                      | create access         |----------------->|
   |                     |                      | tokens                |<-----------------|
   | 200 new tokens      |                      |                       |                  |
   |<--------------------|                      |                       |                  |
```

### 5.6 Déconnexion

```text
Desktop
  |
  | POST /logout refresh_token
  v
API
  |
  v
Revoke refresh token
  |
  v
Optionally blacklist access token JTI
  |
  v
Audit logout
  |
  v
Desktop clears secure token storage
```

### 5.7 Expiration

| Token | Expiration recommandée | Comportement |
|---|---:|---|
| Access token | 10 à 15 minutes | Refresh automatique |
| Refresh token idle | 8 à 12 heures | Reconnexion si inactif |
| Refresh token absolute | 7 à 30 jours selon politique | Reconnexion obligatoire |
| Reset password token | 15 à 30 minutes | Usage unique |
| Invitation token | 24 à 72 heures | Renvoi invitation |

### 5.8 Révocation

```text
Admin action / security event
          |
          v
Select active refresh tokens
          |
          v
Mark revoked_at, revoked_reason
          |
          v
Increment user security_version
          |
          v
Future refresh rejected
          |
          v
Access token rejected if version/JTI policy active
```

### 5.9 Changement de mot de passe

```text
User submits current password + new password
        |
        v
Verify current password
        |
        v
Validate password policy
        |
        v
Hash with Argon2id
        |
        v
Update password hash
        |
        v
Revoke other sessions
        |
        v
Audit password_changed
```

### 5.10 Suppression de compte

```text
Admin requests user deletion
        |
        v
Check permission users:delete
        |
        v
Prevent deleting last Super Administrator
        |
        v
Revoke sessions
        |
        v
Soft delete or anonymize according to policy
        |
        v
Audit user_deleted
```

### 5.11 Blocage de compte

```text
Failed login attempts reach threshold
        |
        v
Set locked_until or state Locked
        |
        v
Revoke active refresh tokens if severe
        |
        v
Audit account_locked
        |
        v
Notify admin if policy requires
```

---

## 6. Architecture JWT

### 6.1 Structure

Un JWT contient trois parties :

```text
base64url(header).base64url(payload).base64url(signature)
```

### 6.2 Header

Exemple :

```json
{
  "typ": "JWT",
  "alg": "RS256",
  "kid": "auth-key-2026-01"
}
```

### 6.3 Payload access token

Exemple cible :

```json
{
  "iss": "veille-seo-geo-api",
  "aud": "veille-seo-geo-desktop",
  "sub": "user:42",
  "sid": "session:8f9b7f",
  "jti": "token:2d0c4b",
  "iat": 1782720000,
  "nbf": 1782720000,
  "exp": 1782720900,
  "type": "access",
  "roles_version": 12,
  "security_version": 4
}
```

### 6.4 Claims autorisés

| Claim | Obligatoire | Description |
|---|---:|---|
| `iss` | Oui | Émetteur |
| `aud` | Oui | Audience |
| `sub` | Oui | Identité utilisateur |
| `sid` | Oui | Identifiant de session |
| `jti` | Oui | Identifiant unique token |
| `iat` | Oui | Date d'émission |
| `nbf` | Oui | Pas valide avant |
| `exp` | Oui | Expiration |
| `type` | Oui | `access` ou autre type |
| `roles_version` | Recommandé | Détection changements RBAC |
| `security_version` | Recommandé | Révocation globale utilisateur |

### 6.5 Claims interdits

| Claim ou donnée | Raison |
|---|---|
| Mot de passe | Secret absolu |
| Hash de mot de passe | Secret exploitable |
| Clés API externes | Donnée sensible |
| Liste complète permissions | Risque de token volumineux et obsolète |
| Données métier SEO/GEO | Hors périmètre identité |
| Informations personnelles inutiles | Minimisation |

### 6.6 Algorithme

| Algorithme | Usage | Avantages | Limites | Recommandation |
|---|---|---|---|---|
| HS256 | Signature symétrique | Simple, rapide | Secret partagé, rotation moins propre | Acceptable en développement |
| RS256 | Signature asymétrique | Clé privée API, clé publique validation | Gestion de clés plus complexe | Recommandé v1.0 |

Recommandation officielle :

- développement initial possible en HS256 si secret fort ;
- cible v1.0 : RS256 avec `kid`, rotation de clés et stockage sécurisé des clés privées.

### 6.7 Durée de vie

| Jeton | Durée cible | Justification |
|---|---:|---|
| Access token | 15 min | Limiter exposition |
| Refresh token idle | 12 h | Journée de travail |
| Refresh token absolute | 14 jours | Confort Desktop contrôlé |
| Token reset password | 30 min | Réduction risque email |
| Token invitation | 72 h | Onboarding interne |

### 6.8 Rotation refresh token

Chaque appel `/refresh` doit :

1. vérifier le refresh token courant ;
2. révoquer le refresh token courant ;
3. créer un nouveau refresh token ;
4. créer un nouvel access token ;
5. journaliser la rotation.

Si un refresh token déjà révoqué est réutilisé, considérer une possible compromission.

### 6.9 Blacklist et révocation

| Méthode | Usage | Coût |
|---|---|---|
| Revocation refresh token | Obligatoire | Faible |
| Blacklist access JTI | Pour incidents critiques | Moyen |
| `security_version` utilisateur | Révocation globale | Faible |
| `roles_version` | Invalidation après changement de droits | Faible |

### 6.10 Stockage côté Desktop

| Donnée | Stockage |
|---|---|
| Access token | Mémoire uniquement si possible |
| Refresh token | Stockage sécurisé OS |
| Email dernier utilisateur | Préférence locale non sensible |
| Mot de passe | Jamais stocké |
| Permissions cache | Possible, mais toujours revérifiées API |

### 6.11 Cookies vs Authorization Header

| Option | Avantages | Limites | Décision Desktop |
|---|---|---|---|
| Cookie HttpOnly | Bon pour web browser | Moins naturel Desktop REST | Non prioritaire |
| Authorization Bearer | Simple pour Desktop API | Protection stockage côté client nécessaire | Retenu |

---

## 7. Authentification Desktop

### 7.1 Principes Desktop

Le Desktop est un client non fiable du point de vue serveur. Il améliore l'expérience utilisateur, mais ne décide pas
des accès. Il doit :

- demander les identifiants ;
- transmettre via HTTPS ;
- stocker les tokens selon la politique ;
- ajouter `Authorization: Bearer` aux requêtes privées ;
- rafraîchir les tokens ;
- afficher clairement les erreurs ;
- effacer les tokens à la déconnexion ;
- ne jamais contacter PostgreSQL.

### 7.2 Premier lancement

```text
+----------------------------------------------------------+
| Veille SEO-GEO Groupe A.P&Partner                        |
|                                                          |
| Connexion requise                                        |
|                                                          |
| Email                                                    |
| [admin@groupe-appartner.fr]                              |
| Mot de passe                                             |
| [**********************]                                 |
|                                                          |
| [ ] Se souvenir de ce poste                              |
|                                                          |
| [Se connecter]                                           |
|                                                          |
| API : vérification...                                    |
+----------------------------------------------------------+
```

### 7.3 Connexion réussie

```text
LoginWindow
    |
    v
POST /login
    |
    v
Tokens reçus
    |
    v
Refresh token stocké
    |
    v
GET /me
    |
    v
Navigation filtrée par permissions
    |
    v
MainWindow affichée
```

### 7.4 Connexion automatique

Au démarrage :

```text
Desktop démarre
      |
      v
Refresh token présent ?
   |          |
  Non        Oui
   |          |
   v          v
 Login    POST /refresh
              |
              v
        Refresh OK ?
          |       |
         Non     Oui
          |       |
          v       v
        Login   GET /me + MainWindow
```

### 7.5 Refresh automatique

Le Desktop doit anticiper l'expiration :

- si access token expire dans moins de 60 secondes, tenter `/refresh` ;
- si `/refresh` échoue pour expiration, afficher l'écran de connexion ;
- si l'API est indisponible, passer en état dégradé ;
- ne pas multiplier les refresh concurrents.

### 7.6 Session expirée

```text
+----------------------------------------------------------+
| Session expirée                                          |
|                                                          |
| Votre session a expiré. Reconnectez-vous pour continuer. |
| Les données non enregistrées doivent être conservées      |
| localement lorsque cela est possible.                    |
|                                                          |
| [Se reconnecter]                                         |
+----------------------------------------------------------+
```

### 7.7 Perte Internet

Comportement :

- bannière "Connexion réseau indisponible" ;
- ne pas déconnecter immédiatement ;
- suspendre les opérations d'écriture ;
- retenter selon backoff ;
- indiquer si les données affichées peuvent être obsolètes.

### 7.8 API indisponible

```text
+----------------------------------------------------------------------------------+
| API indisponible                                                                  |
| Impossible de contacter le backend. Les actions nécessitant le serveur sont        |
| temporairement bloquées.                                                          |
| [Réessayer] [Détails techniques]                                                  |
+----------------------------------------------------------------------------------+
```

### 7.9 Déconnexion forcée

Déclencheurs :

- compte désactivé ;
- mot de passe changé ;
- session révoquée par administrateur ;
- refresh token compromis ;
- permissions critiques modifiées.

### 7.10 Comportement UI attendu

| Situation | Comportement |
|---|---|
| Identifiants invalides | Message sous formulaire, pas de détail excessif |
| Compte bloqué | Message clair, contacter administrateur |
| Permission insuffisante | Page 403 Desktop avec action retour |
| Session expirée | Modal de reconnexion |
| API offline | Bandeau global + actions désactivées |
| Refresh réussi | Transparent pour l'utilisateur |

---

## 8. Authentification API

### 8.1 Authorization Bearer

Toutes les routes privées doivent accepter :

```http
Authorization: Bearer <access_token>
```

Les routes publiques doivent être explicitement déclarées publiques.

### 8.2 Pipeline API

```text
HTTP Request
    |
    v
Correlation ID middleware
    |
    v
Authentication dependency
    |
    v
Token validation
    |
    v
Current user injection
    |
    v
Permission dependency
    |
    v
Route handler
    |
    v
Service
    |
    v
Repository
```

### 8.3 Validation

La validation doit vérifier :

| Vérification | Erreur |
|---|---|
| Header présent | 401 |
| Format Bearer valide | 401 |
| Signature valide | 401 |
| `exp` non expiré | 401 |
| `nbf` respecté | 401 |
| `iss` attendu | 401 |
| `aud` attendu | 401 |
| `type == access` | 401 |
| JTI non révoqué si blacklist active | 401 |
| User existe | 401 ou 403 selon cas |
| User actif | 403 |
| Session non révoquée | 401 |

### 8.4 Injection utilisateur

L'API doit fournir une dépendance conceptuelle :

```text
get_current_user()
  |
  +-- validate token
  +-- load user
  +-- verify user state
  +-- attach effective permissions context
```

### 8.5 Gestion des erreurs

| Cas | Code | Réponse |
|---|---:|---|
| Aucun token | 401 | `not_authenticated` |
| Token expiré | 401 | `token_expired` |
| Token invalide | 401 | `invalid_token` |
| Compte désactivé | 403 | `account_disabled` |
| Permission insuffisante | 403 | `permission_denied` |
| Session révoquée | 401 | `session_revoked` |

### 8.6 Séquence route privée

```text
Client          FastAPI          TokenService          UserRepo          AuthzService
  |               |                   |                   |                  |
  | GET private   |                   |                   |                  |
  |-------------->|                   |                   |                  |
  |               | validate token    |                   |                  |
  |               |------------------>|                   |                  |
  |               | claims            |                   |                  |
  |               |<------------------|                   |                  |
  |               | load user         |                   |                  |
  |               |-------------------------------------->|                  |
  |               | user              |                   |                  |
  |               |<--------------------------------------|                  |
  |               | check permission  |                   |                  |
  |               |-------------------------------------------------------->|
  |               | allowed           |                   |                  |
  |               |<--------------------------------------------------------|
  | 200           |                   |                   |                  |
  |<--------------|                   |                   |                  |
```

---

## 9. Architecture RBAC

### 9.1 Principe

Le système RBAC définit des rôles composés de permissions atomiques. Un utilisateur peut avoir plusieurs rôles.
Les permissions effectives sont l'union des permissions de ses rôles, éventuellement restreintes par des règles métier.

### 9.2 Arbre des rôles

```text
Super Administrateur
  |
  +-- Administrateur
  |     |
  |     +-- Manager
  |     |     |
  |     |     +-- Marketing
  |     |     +-- SEO
  |     |     +-- Content Manager
  |     |
  |     +-- API
  |
  +-- Consultation
        |
        +-- Invité
```

### 9.3 Rôles officiels

| Rôle | Responsabilité | Niveau |
|---|---|---:|
| Super Administrateur | Contrôle complet, sécurité, rôles, configuration critique | 100 |
| Administrateur | Administration fonctionnelle et technique | 90 |
| Manager | Pilotage, rapports, validation | 70 |
| Marketing | Suivi campagnes, rapports, contenus | 60 |
| SEO | Audits, mots-clés, websites, crawler | 60 |
| Content Manager | Contenus, prompts éditoriaux, rapports contenu | 50 |
| Rédacteur | Contribution contenu et consultation limitée | 40 |
| Consultation | Lecture des dashboards et rapports autorisés | 20 |
| API | Compte technique ou intégration | Variable |
| Invité | Accès temporaire très limité | 10 |

### 9.4 Matrice responsabilités par rôle

| Responsabilité | Super Admin | Admin | Manager | Marketing | SEO | Content | Rédacteur | Consultation | API | Invité |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gérer utilisateurs | Oui | Oui | Non | Non | Non | Non | Non | Non | Non | Non |
| Gérer rôles | Oui | Limité | Non | Non | Non | Non | Non | Non | Non | Non |
| Gérer permissions | Oui | Non | Non | Non | Non | Non | Non | Non | Non | Non |
| Configurer API | Oui | Oui | Non | Non | Non | Non | Non | Non | Limité | Non |
| Lire dashboard | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non | Limité |
| Gérer websites | Oui | Oui | Oui | Oui | Oui | Non | Non | Lecture | Selon scope | Non |
| Gérer keywords | Oui | Oui | Oui | Oui | Oui | Non | Non | Lecture | Selon scope | Non |
| Lancer crawler | Oui | Oui | Oui | Non | Oui | Non | Non | Non | Selon scope | Non |
| Gérer prompts | Oui | Oui | Oui | Oui | Oui | Oui | Lecture | Lecture | Selon scope | Non |
| Générer rapports | Oui | Oui | Oui | Oui | Oui | Oui | Non | Lecture | Selon scope | Non |
| Lire logs | Oui | Oui | Non | Non | Non | Non | Non | Non | Non | Non |

### 9.5 Permission naming

Format obligatoire :

```text
module:action
```

Exemples :

```text
websites:read
websites:create
websites:update
websites:delete
reports:export
admin:configure
```

### 9.6 Permissions effectives

```text
User
 |
 +-- Role A ---- permissions
 |
 +-- Role B ---- permissions
 |
 v
Union permissions
 |
 v
Restrictions contextuelles
 |
 v
Effective permissions
```

### 9.7 Règles contextuelles futures

| Règle | Exemple |
|---|---|
| Restriction par entité | Marketing Europ-Arm ne voit que Europ-Arm |
| Restriction par module | Rédacteur ne voit pas Administration |
| Restriction par environnement | Compte API sandbox seulement |
| Restriction horaire | Accès admin bloqué hors plage |
| Restriction IP | Administration depuis réseau interne |

---

## 10. Permissions

### 10.1 Actions standard

| Action | Description |
|---|---|
| `read` | Lire une ressource |
| `create` | Créer une ressource |
| `update` | Modifier une ressource |
| `delete` | Supprimer une ressource |
| `export` | Exporter des données |
| `import` | Importer des données |
| `admin` | Administrer un module |
| `validate` | Valider une action ou un rapport |
| `configure` | Modifier une configuration |
| `execute` | Lancer un job, crawl ou analyse |

### 10.2 Matrice complète par module

| Module | Read | Create | Update | Delete | Export | Import | Admin | Validate | Configure | Execute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Dashboard | Oui | Non | Non | Non | Oui | Non | Non | Non | Oui | Non |
| Websites | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Entities | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Keywords | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Competitors | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Crawler | Oui | Oui | Oui | Oui | Oui | Non | Oui | Non | Oui | Oui |
| SEO | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| GEO | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| LLM | Oui | Oui | Oui | Oui | Oui | Non | Oui | Oui | Oui | Oui |
| IA | Oui | Oui | Oui | Oui | Oui | Non | Oui | Oui | Oui | Oui |
| Prompts | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui |
| Reports | Oui | Oui | Oui | Oui | Oui | Non | Oui | Oui | Oui | Oui |
| Logs | Oui | Non | Non | Oui | Oui | Non | Oui | Non | Oui | Non |
| API | Oui | Oui | Oui | Oui | Oui | Non | Oui | Oui | Oui | Oui |
| Users | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Roles | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Permissions | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Configuration | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Oui | Non |
| Audit | Oui | Non | Non | Non | Oui | Non | Oui | Non | Oui | Non |

### 10.3 Matrice rôle/module synthétique

| Module | Super Admin | Admin | Manager | Marketing | SEO | Content | Rédacteur | Consultation | API | Invité |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Dashboard | Admin | Admin | Read | Read | Read | Read | Read | Read | None | Read |
| Websites | Admin | Admin | Update | Update | Update | Read | None | Read | Scoped | None |
| Entities | Admin | Admin | Update | Read | Read | Read | None | Read | Scoped | None |
| Keywords | Admin | Admin | Update | Update | Admin | Read | None | Read | Scoped | None |
| Competitors | Admin | Admin | Update | Read | Update | Read | None | Read | Scoped | None |
| Crawler | Admin | Admin | Execute | Read | Execute | None | None | None | Scoped | None |
| SEO | Admin | Admin | Validate | Read | Admin | Read | None | Read | Scoped | None |
| GEO | Admin | Admin | Validate | Read | Update | Update | Read | Read | Scoped | None |
| Prompts | Admin | Admin | Validate | Update | Update | Admin | Create | Read | Scoped | None |
| Reports | Admin | Admin | Validate | Create | Create | Create | Read | Read | Scoped | Read |
| Logs | Admin | Read | None | None | None | None | None | None | None | None |
| API | Admin | Admin | None | None | None | None | None | None | Scoped | None |
| Users | Admin | Admin | None | None | None | None | None | None | None | None |
| Roles | Admin | Read | None | None | None | None | None | None | None | None |
| Configuration | Admin | Update | None | None | None | None | None | None | None | None |

### 10.4 Permissions critiques

| Permission | Risque | Contrôle renforcé |
|---|---|---|
| `users:delete` | Suppression compte | Confirmation + audit |
| `roles:update` | Escalade privilège | Super Admin seulement |
| `permissions:update` | Escalade globale | Super Admin seulement |
| `api_keys:read_secret` | Fuite secret | Éviter si possible |
| `configuration:update` | Impact global | Audit détaillé |
| `logs:delete` | Perte traçabilité | Interdit ou très restreint |
| `reports:delete` | Perte historique | Confirmation |

---

## 11. Politique de sécurité

### 11.1 Mots de passe

| Règle | Valeur cible |
|---|---|
| Longueur minimale | 14 caractères |
| Longueur recommandée | 16 caractères ou plus |
| Complexité | Majuscule, minuscule, chiffre, caractère spécial recommandés |
| Liste interdite | Mots de passe compromis ou évidents |
| Réutilisation | Interdire les 5 derniers mots de passe |
| Expiration | Pas d'expiration arbitraire sauf politique interne |
| Changement forcé | Oui après compromission ou reset admin |

### 11.2 Hashing

Algorithme recommandé : Argon2id.

| Paramètre | Recommandation |
|---|---|
| Algorithme | Argon2id |
| Sel | Unique par mot de passe |
| Pepper | Optionnel, stocké hors base |
| Migration | Supporter anciens hashes si nécessaire |

### 11.3 Tentatives et blocage

| Règle | Valeur |
|---|---|
| Échecs avant ralentissement | 3 |
| Échecs avant blocage temporaire | 5 |
| Durée blocage initiale | 15 min |
| Blocage renforcé | Backoff progressif |
| Notification admin | Après seuil critique |

### 11.4 Rate limiting

| Endpoint | Limite indicative |
|---|---|
| `/login` | 5 tentatives / 15 min / compte et IP |
| `/refresh` | 30 / heure / session |
| `/forgot-password` | 3 / heure / email |
| `/reset-password` | 5 / heure / IP |
| endpoints admin | Limite selon sensibilité |

### 11.5 Journalisation sécurité

Journaliser :

- login réussi ;
- login échoué ;
- refresh réussi ;
- refresh suspect ;
- logout ;
- changement mot de passe ;
- reset mot de passe ;
- compte bloqué ;
- compte débloqué ;
- changement de rôle ;
- changement de permission ;
- accès refusé répété.

### 11.6 Données à ne jamais journaliser

| Donnée | Raison |
|---|---|
| Mot de passe | Secret |
| Refresh token brut | Secret |
| Access token complet | Secret |
| Clé API externe complète | Secret |
| Hash complet si non nécessaire | Réduction risque |
| Données personnelles inutiles | RGPD |

### 11.7 OWASP

Contrôles à aligner avec :

- OWASP ASVS ;
- OWASP Top 10 ;
- OWASP API Security Top 10 ;
- recommandations JWT ;
- recommandations password storage.

### 11.8 RGPD

Principes :

- minimisation des données ;
- durée de conservation documentée ;
- accès aux données personnelles limité ;
- suppression ou anonymisation selon politique ;
- audit des accès administratifs.

---

## 12. Sessions

### 12.1 Architecture session

```text
User
 |
 +-- Session Desktop PC-A
 |     +-- Refresh token family A
 |     +-- Access tokens courts
 |
 +-- Session Desktop PC-B
 |     +-- Refresh token family B
 |     +-- Access tokens courts
 |
 +-- Session API service account
       +-- API key or token policy future
```

### 12.2 Connexions simultanées

| Profil | Sessions autorisées |
|---|---:|
| Super Administrateur | 3 à 5 |
| Administrateur | 3 |
| Utilisateur standard | 2 à 3 |
| Invité | 1 |
| API | Selon configuration |

### 12.3 Multi-desktop

Chaque poste doit avoir une session distincte, avec :

- device label ;
- created_at ;
- last_seen_at ;
- ip approximative ;
- user agent Desktop ;
- état révoqué ou actif.

### 12.4 Déconnexion distante

Un utilisateur ou administrateur autorisé doit pouvoir révoquer :

- une session précise ;
- toutes les sessions sauf courante ;
- toutes les sessions d'un utilisateur ;
- toutes les sessions après incident.

### 12.5 Idle Timeout

L'idle timeout est mesuré depuis la dernière activité significative :

- requête API privée ;
- refresh token ;
- action utilisateur.

### 12.6 Absolute Timeout

Même avec activité, une session doit expirer après une durée absolue.

### 12.7 Séquence session expirée

```text
Desktop          API             AuthService
  | request        |                   |
  |--------------->|                   |
  |                | token expired     |
  | 401            |                   |
  |<---------------|                   |
  | refresh        |                   |
  |--------------->| validate refresh  |
  |                |------------------>|
  |                | expired           |
  | 401            |<------------------|
  |<---------------|                   |
  | show login     |                   |
```

---

## 13. Journalisation

### 13.1 Principes

Les logs opérationnels servent au diagnostic. Les audit logs servent à la traçabilité métier et sécurité. Ils ne
doivent pas être confondus.

### 13.2 Niveaux

| Niveau | Usage |
|---|---|
| DEBUG | Diagnostic local, jamais en production standard |
| INFO | Événement normal |
| WARNING | Situation anormale mais récupérable |
| ERROR | Échec d'une opération |
| CRITICAL | Incident sécurité ou indisponibilité majeure |

### 13.3 Événements à journaliser

| Événement | Log opérationnel | Audit |
|---|---:|---:|
| Login réussi | Oui | Oui |
| Login échoué | Oui | Oui |
| Refresh réussi | Optionnel | Non ou faible |
| Refresh réutilisé | Oui | Oui |
| Logout | Oui | Oui |
| Permission refusée | Oui | Selon seuil |
| Changement rôle | Oui | Oui |
| Suppression utilisateur | Oui | Oui |
| Export rapport | Optionnel | Oui |
| Erreur API externe | Oui | Non sauf impact sécurité |

### 13.4 Format recommandé

```json
{
  "timestamp": "2026-06-29T09:42:00Z",
  "level": "WARNING",
  "event": "auth.login_failed",
  "correlation_id": "req_123",
  "actor_user_id": null,
  "target": "user:admin@groupe-appartner.fr",
  "ip": "192.0.2.10",
  "reason": "invalid_credentials"
}
```

### 13.5 À ne jamais journaliser

Voir section 11.6. Toute donnée secrète doit être masquée.

---

## 14. Audit

### 14.1 Objectif

L'audit permet de répondre à :

- qui a fait quoi ;
- quand ;
- depuis quel contexte ;
- sur quelle ressource ;
- avec quel résultat ;
- selon quelle permission.

### 14.2 Audit utilisateur

| Action | Détail |
|---|---|
| Connexion | succès/échec, IP, poste |
| Déconnexion | utilisateur, session |
| Changement mot de passe | utilisateur, méthode |
| Export rapport | rapport, format |
| Lancement crawl | site, paramètres |

### 14.3 Audit administrateur

| Action | Sensibilité |
|---|---|
| Création utilisateur | Haute |
| Modification rôle | Critique |
| Modification permission | Critique |
| Déblocage compte | Haute |
| Révocation session | Haute |
| Configuration API | Critique |

### 14.4 Audit API

| Événement | Description |
|---|---|
| Token invalide répété | Potentiel abus |
| Rate limit atteint | Protection brute force |
| Accès refusé répété | Potentiel contournement |
| Erreur signature JWT | Token falsifié ou mauvais secret |

### 14.5 Audit sécurité

| Événement | Niveau |
|---|---|
| Réutilisation refresh token révoqué | Critique |
| Escalade de rôle | Critique |
| Désactivation Super Admin | Critique |
| Suppression logs | Critique |
| Tentatives massives login | Haute |
| Changement de politique mot de passe | Haute |

---

## 15. API

### 15.1 Conventions générales

Base cible :

```text
/api/v1/auth
```

Format d'erreur :

```json
{
  "error": {
    "code": "invalid_credentials",
    "message": "Identifiants invalides.",
    "correlation_id": "req_123"
  }
}
```

### 15.2 POST /login

Entrée :

```json
{
  "email": "admin@groupe-appartner.fr",
  "password": "mot-de-passe",
  "device_name": "PC Marketing",
  "remember_device": true
}
```

Sortie :

```json
{
  "access_token": "eyJ...",
  "refresh_token": "rfr_...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": 42,
    "email": "admin@groupe-appartner.fr",
    "display_name": "Admin",
    "roles": ["Administrateur"]
  }
}
```

Codes :

| Code | Cas |
|---:|---|
| 200 | Connexion réussie |
| 400 | Payload invalide |
| 401 | Identifiants invalides |
| 403 | Compte bloqué ou désactivé |
| 429 | Trop de tentatives |

### 15.3 POST /logout

Entrée :

```json
{
  "refresh_token": "rfr_..."
}
```

Sortie :

```json
{
  "status": "logged_out"
}
```

### 15.4 POST /refresh

Entrée :

```json
{
  "refresh_token": "rfr_..."
}
```

Sortie :

```json
{
  "access_token": "eyJ...",
  "refresh_token": "rfr_new...",
  "token_type": "bearer",
  "expires_in": 900
}
```

Codes :

| Code | Cas |
|---:|---|
| 200 | Refresh réussi |
| 401 | Refresh expiré, révoqué ou invalide |
| 403 | Compte désactivé |
| 409 | Réutilisation suspecte |

### 15.5 GET /me

Sortie :

```json
{
  "id": 42,
  "email": "admin@groupe-appartner.fr",
  "display_name": "Admin",
  "roles": ["Administrateur"],
  "permissions": [
    "dashboard:read",
    "websites:read",
    "websites:create"
  ],
  "account_state": "active"
}
```

### 15.6 POST /change-password

Entrée :

```json
{
  "current_password": "ancien",
  "new_password": "nouveau-long-et-solide"
}
```

Codes :

| Code | Cas |
|---:|---|
| 204 | Mot de passe changé |
| 400 | Politique non respectée |
| 401 | Mot de passe actuel invalide |

### 15.7 POST /forgot-password

Entrée :

```json
{
  "email": "user@groupe-appartner.fr"
}
```

Réponse toujours neutre :

```json
{
  "status": "if_account_exists_email_sent"
}
```

### 15.8 POST /reset-password

Entrée :

```json
{
  "token": "rst_...",
  "new_password": "nouveau-long-et-solide"
}
```

### 15.9 POST /unlock

Endpoint administrateur.

Entrée :

```json
{
  "user_id": 42,
  "reason": "Vérification effectuée par l'administrateur"
}
```

Permissions :

```text
users:admin
```

### 15.10 GET /sessions

Retourne les sessions de l'utilisateur courant ou d'un utilisateur ciblé selon permission.

### 15.11 DELETE /sessions/{session_id}

Révoque une session.

### 15.12 POST /roles/{role_id}/permissions

Endpoint critique réservé Super Administrateur.

---

## 16. Base de données

### 16.1 Diagramme relationnel

```text
+---------+       +------------+       +-------+
| users   |       | user_roles |       | roles |
|---------|       |------------|       |-------|
| id PK   |<----->| user_id FK |       | id PK |
| email   |       | role_id FK |<----->| name  |
| hash    |       +------------+       +---+---+
| state   |                                |
+----+----+                                |
     |                                     |
     |                                     v
     |                              +------------------+
     |                              | role_permissions |
     |                              |------------------|
     |                              | role_id FK       |
     |                              | permission_id FK |
     |                              +---------+--------+
     |                                        |
     v                                        v
+----------------+                   +-------------+
| refresh_tokens |                   | permissions |
|----------------|                   |-------------|
| id PK          |                   | id PK       |
| user_id FK     |                   | code        |
| token_hash     |                   | module      |
| expires_at     |                   | action      |
| revoked_at     |                   +-------------+
+----------------+
     |
     v
+---------------+
| login_history |
+---------------+

+------------+
| audit_logs |
+------------+
```

### 16.2 users

| Colonne | Type | Contrainte |
|---|---|---|
| id | integer/uuid | PK |
| email | varchar | unique, not null |
| display_name | varchar | not null |
| password_hash | text | not null |
| state | enum/text | not null |
| failed_login_count | integer | default 0 |
| locked_until | timestamp | nullable |
| password_changed_at | timestamp | nullable |
| security_version | integer | default 1 |
| created_at | timestamp | not null |
| updated_at | timestamp | not null |
| deleted_at | timestamp | nullable |

Index :

- unique `users.email`;
- index `users.state`;
- index `users.deleted_at`.

### 16.3 roles

| Colonne | Type | Contrainte |
|---|---|---|
| id | integer/uuid | PK |
| name | varchar | unique |
| code | varchar | unique |
| description | text | nullable |
| level | integer | not null |
| is_system | boolean | default false |

### 16.4 permissions

| Colonne | Type | Contrainte |
|---|---|---|
| id | integer/uuid | PK |
| code | varchar | unique, ex `websites:read` |
| module | varchar | not null |
| action | varchar | not null |
| description | text | nullable |
| is_system | boolean | default true |

### 16.5 user_roles

| Colonne | Type | Contrainte |
|---|---|---|
| user_id | FK | users.id |
| role_id | FK | roles.id |
| assigned_by | FK | users.id nullable |
| assigned_at | timestamp | not null |

Contrainte unique :

```text
(user_id, role_id)
```

### 16.6 role_permissions

| Colonne | Type | Contrainte |
|---|---|---|
| role_id | FK | roles.id |
| permission_id | FK | permissions.id |
| granted_by | FK | users.id nullable |
| granted_at | timestamp | not null |

Contrainte unique :

```text
(role_id, permission_id)
```

### 16.7 refresh_tokens

| Colonne | Type | Contrainte |
|---|---|---|
| id | uuid | PK |
| user_id | FK | users.id |
| session_id | uuid | not null |
| token_hash | text | unique, not null |
| family_id | uuid | not null |
| device_name | varchar | nullable |
| created_at | timestamp | not null |
| last_used_at | timestamp | nullable |
| expires_at | timestamp | not null |
| revoked_at | timestamp | nullable |
| revoked_reason | varchar | nullable |
| replaced_by_id | FK | refresh_tokens.id nullable |

Index :

- `refresh_tokens.user_id`;
- `refresh_tokens.session_id`;
- `refresh_tokens.token_hash`;
- `refresh_tokens.expires_at`;
- `refresh_tokens.revoked_at`.

### 16.8 login_history

| Colonne | Type | Contrainte |
|---|---|---|
| id | uuid | PK |
| user_id | FK | nullable si email inconnu |
| email_attempted | varchar | nullable |
| success | boolean | not null |
| failure_reason | varchar | nullable |
| ip_address | inet/text | nullable |
| user_agent | text | nullable |
| created_at | timestamp | not null |

### 16.9 audit_logs

| Colonne | Type | Contrainte |
|---|---|---|
| id | uuid | PK |
| event_type | varchar | not null |
| actor_user_id | FK | nullable |
| target_type | varchar | nullable |
| target_id | varchar | nullable |
| module | varchar | nullable |
| action | varchar | not null |
| result | varchar | not null |
| metadata | jsonb | nullable |
| correlation_id | varchar | nullable |
| created_at | timestamp | not null |

### 16.10 Contraintes critiques

| Contrainte | Raison |
|---|---|
| Email unique | Identité stable |
| Permission code unique | RBAC cohérent |
| Role code unique | Administration claire |
| Refresh token hash unique | Détection réutilisation |
| FK avec restrictions | Intégrité relationnelle |
| Soft delete users | Préserver audit |

---

## 17. Interface Desktop

### 17.1 Écran connexion

```text
+----------------------------------------------------------+
| Logo Groupe A.P&Partner                                  |
| Veille SEO-GEO                                           |
|                                                          |
| Email                                                    |
| [________________________________________________]       |
| Mot de passe                                             |
| [________________________________________________]       |
|                                                          |
| [ ] Se souvenir de ce poste                              |
|                                                          |
| [Connexion]                                              |
|                                                          |
| Mot de passe oublié                                      |
| API : OK                                                 |
+----------------------------------------------------------+
```

### 17.2 État erreur identifiants

```text
+----------------------------------------------------------+
| Connexion impossible                                     |
| Identifiants invalides ou compte indisponible.           |
|                                                          |
| Email                                                    |
| [admin@groupe-appartner.fr_______________________]       |
| Mot de passe                                             |
| [****************_______________________________]        |
|                                                          |
| [Connexion]                                              |
+----------------------------------------------------------+
```

### 17.3 Session expirée

```text
+----------------------------------------------------------+
| Session expirée                                          |
| Reconnectez-vous pour continuer à utiliser l'application.|
|                                                          |
| [Se reconnecter] [Quitter]                               |
+----------------------------------------------------------+
```

### 17.4 Permission insuffisante

```text
+----------------------------------------------------------------------------------+
| Accès refusé                                                                      |
| Vous ne disposez pas de la permission `reports:export`.                           |
| Contactez un administrateur si cet accès est nécessaire.                          |
| [Retour]                                                                          |
+----------------------------------------------------------------------------------+
```

### 17.5 Déconnexion

Flux :

```text
User clicks logout
      |
      v
POST /logout
      |
      v
Clear token store
      |
      v
Show login window
```

---

## 18. Cas d'erreurs

### 18.1 Catalogue

| Code erreur | Cause | API | Desktop |
|---|---|---:|---|
| `jwt_expired` | Access token expiré | 401 | Tenter refresh |
| `jwt_invalid` | Signature ou format invalide | 401 | Déconnecter |
| `refresh_expired` | Refresh expiré | 401 | Reconnexion |
| `refresh_reused` | Token révoqué réutilisé | 409 | Déconnexion forcée |
| `api_unavailable` | Backend indisponible | 503/timeout | Bandeau erreur |
| `network_lost` | Internet perdu | N/A | Mode dégradé |
| `account_locked` | Compte bloqué | 403 | Message blocage |
| `permission_denied` | Droit manquant | 403 | Page accès refusé |
| `user_deleted` | Compte supprimé | 403 | Déconnexion forcée |
| `server_error` | Erreur interne | 500 | Message + retry |

### 18.2 JWT expiré

```text
401 token_expired
    |
    v
Desktop appelle /refresh
    |
    +-- succès : rejoue la requête
    +-- échec : affiche reconnexion
```

### 18.3 Permission insuffisante

Ne jamais afficher un bouton actif si `/me` indique que la permission est absente. Malgré cela, l'API doit toujours
revérifier.

### 18.4 Utilisateur supprimé

Comportement :

- invalider session ;
- supprimer tokens locaux ;
- afficher "Compte indisponible" ;
- ne pas révéler trop de détails si contexte sensible.

### 18.5 API indisponible

Le Desktop doit distinguer :

- API inaccessible ;
- API accessible mais non authentifiée ;
- API accessible mais base indisponible ;
- API accessible mais permission refusée.

---

## 19. Évolutions futures

### 19.1 MFA

Méthodes candidates :

- TOTP ;
- OTP email ;
- push interne ;
- WebAuthn ;
- passkeys.

### 19.2 TOTP

Flux cible :

```text
Login password OK
        |
        v
MFA required
        |
        v
Desktop asks TOTP
        |
        v
POST /mfa/verify
        |
        v
Tokens issued
```

### 19.3 Passkeys, FIDO2, WebAuthn

Objectif :

- réduire dépendance au mot de passe ;
- renforcer comptes administrateurs ;
- préparer authentification moderne.

### 19.4 Azure AD / Microsoft Entra ID

Cas d'usage :

- SSO interne ;
- gestion centralisée des utilisateurs ;
- MFA entreprise ;
- groupes synchronisés vers rôles.

### 19.5 Google Workspace

Possible si les équipes utilisent Google pour identité ou documents.

### 19.6 LDAP

Option pour environnements historiques, non prioritaire si Entra ID est disponible.

### 19.7 OpenID Connect et OAuth2

Architecture future :

```text
Desktop
  |
  v
System browser / Device code flow
  |
  v
Identity Provider
  |
  v
Backend callback or token exchange
  |
  v
Application session
```

### 19.8 API Keys

Les API keys doivent être réservées aux intégrations techniques, jamais aux utilisateurs humains.

### 19.9 Service Accounts

Comptes dédiés :

- pas de login Desktop ;
- permissions strictes ;
- rotation de secret ;
- audit renforcé ;
- expiration optionnelle.

---

## 20. Checklist

### 20.1 Checklist développement

| Contrôle | OK |
|---|---|
| La route privée utilise une dépendance current user | |
| La permission requise est déclarée explicitement | |
| Aucun accès direct Desktop -> PostgreSQL | |
| Le service ne lit pas directement le JWT | |
| Les erreurs utilisent un code stable | |
| Les actions sensibles sont auditées | |
| Les tests couvrent 401 et 403 | |
| Les secrets ne sont pas loggés | |

### 20.2 Checklist sécurité

| Contrôle | OK |
|---|---|
| Access token court | |
| Refresh token stocké hashé | |
| Refresh rotation implémentée | |
| Révocation possible | |
| Rate limiting login | |
| Politique mot de passe appliquée | |
| Argon2id utilisé | |
| Dernier Super Admin protégé | |
| Audit des changements RBAC | |

### 20.3 Checklist mise en production

| Contrôle | OK |
|---|---|
| HTTPS obligatoire | |
| Secrets hors Git | |
| Clés JWT fortes | |
| Rotation clés planifiée | |
| Logs centralisés | |
| Sauvegardes PostgreSQL | |
| Monitoring erreurs auth | |
| Procédure révocation incident | |
| Politique RGPD validée | |

### 20.4 Checklist Pull Request

| Contrôle | OK |
|---|---|
| Aucun endpoint privé sans protection | |
| Permissions nommées selon `module:action` | |
| Pas de logique métier dans les routes | |
| Pas de décision d'autorisation côté Desktop uniquement | |
| Migration Alembic si table modifiée | |
| Documentation mise à jour si contrat modifié | |
| Tests unitaires et intégration ajoutés | |

### 20.5 Checklist audit

| Contrôle | OK |
|---|---|
| Les événements critiques sont présents | |
| Les logs ne contiennent pas de secrets | |
| Les exports sensibles sont tracés | |
| Les changements de rôle sont traçables | |
| Les révocations de session sont traçables | |
| Les accès refusés répétés sont détectables | |

---

## 21. Annexes

### 21.1 Abréviations

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| JWT | JSON Web Token |
| RBAC | Role-Based Access Control |
| ACL | Access Control List |
| MFA | Multi-Factor Authentication |
| OTP | One-Time Password |
| TOTP | Time-based One-Time Password |
| OIDC | OpenID Connect |
| SSO | Single Sign-On |
| JTI | JWT ID |

### 21.2 Conventions

| Élément | Convention |
|---|---|
| Permission | `module:action` |
| Rôle système | Code stable en minuscules |
| Event audit | `domain.action` |
| Correlation ID | `req_<id>` |
| Session ID | UUID |
| Refresh token brut | Préfixe logique optionnel `rfr_` |

### 21.3 Références

Références conceptuelles :

- OWASP Application Security Verification Standard ;
- OWASP API Security Top 10 ;
- RFC 7519 JSON Web Token ;
- bonnes pratiques Argon2id ;
- recommandations OAuth2/OIDC pour clients natifs.

### 21.4 Diagramme récapitulatif

```text
Desktop
  |
  | Bearer access token
  v
FastAPI
  |
  +-- Authenticate
  |     +-- Verify JWT
  |     +-- Verify user
  |     +-- Verify session
  |
  +-- Authorize
  |     +-- Load roles
  |     +-- Load permissions
  |     +-- Check policy
  |
  +-- Execute
  |     +-- Service
  |     +-- Repository
  |     +-- PostgreSQL
  |
  +-- Audit
        +-- Security events
        +-- Admin events
        +-- Business events
```

### 21.5 Résumé architectural

L'architecture officielle d'authentification et d'autorisation de Veille SEO-GEO Groupe A.P&Partner repose sur :

- une authentification centralisée par l'API ;
- des access tokens courts ;
- des refresh tokens rotatifs, hashés et révocables ;
- une autorisation RBAC par permissions atomiques ;
- une séparation stricte Desktop/API/PostgreSQL ;
- une journalisation sans secrets ;
- un audit durable des actions sensibles ;
- une préparation aux évolutions MFA, SSO, OIDC et comptes de service.

Cette spécification doit être respectée par tous les sprints qui touchent à l'identité, aux sessions, aux rôles, aux
permissions, à l'administration, aux connecteurs API ou aux opérations sensibles du projet.
