# Software Desktop Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle du client Desktop  
Version du document : 1.0  
Statut : Référence technique Desktop  
Périmètre : application Desktop PySide6, shell, navigation, pages, widgets, ApiClient, états UI  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes d'architecture](#2-principes-darchitecture)
3. [Vue d'ensemble de l'architecture Desktop](#3-vue-densemble-de-larchitecture-desktop)
4. [Arborescence officielle](#4-arborescence-officielle)
5. [Cycle de vie de l'application](#5-cycle-de-vie-de-lapplication)
6. [`main.py`](#6-mainpy)
7. [`app.py`](#7-apppy)
8. [Configuration Desktop](#8-configuration-desktop)
9. [Constantes Desktop](#9-constantes-desktop)
10. [ApiClient](#10-apiclient)
11. [MainWindow](#11-mainwindow)
12. [Système de navigation](#12-système-de-navigation)
13. [Pages UI](#13-pages-ui)
14. [Pattern officiel pour créer une nouvelle page](#14-pattern-officiel-pour-créer-une-nouvelle-page)
15. [Widgets réutilisables](#15-widgets-réutilisables)
16. [Sidebar](#16-sidebar)
17. [TopBar](#17-topbar)
18. [StatusBar](#18-statusbar)
19. [Thème QSS](#19-thème-qss)
20. [Ressources graphiques](#20-ressources-graphiques)
21. [Gestion des états](#21-gestion-des-états)
22. [Gestion des erreurs](#22-gestion-des-erreurs)
23. [Communication entre composants](#23-communication-entre-composants)
24. [Threading et performances](#24-threading-et-performances)
25. [Authentification future](#25-authentification-future)
26. [Intégration avec le backend FastAPI](#26-intégration-avec-le-backend-fastapi)
27. [Module Websites](#27-module-websites)
28. [Modules futurs](#28-modules-futurs)
29. [Logging Desktop](#29-logging-desktop)
30. [Tests Desktop](#30-tests-desktop)
31. [Qualité de code](#31-qualité-de-code)
32. [Conventions de nommage](#32-conventions-de-nommage)
33. [Anti-patterns interdits](#33-anti-patterns-interdits)
34. [Checklist ajout de module](#34-checklist-ajout-de-module)
35. [Checklist avant Pull Request](#35-checklist-avant-pull-request)
36. [Roadmap Desktop](#36-roadmap-desktop)
37. [Annexes](#37-annexes)

---

## 1. Présentation

### 1.1 Rôle du Desktop

Le client Desktop de Veille SEO-GEO Groupe A.P&Partner est l'interface graphique interne utilisée pour piloter les
modules SEO, GEO, IA, sites web, entités, mots-clés, concurrents, rapports et administration. Il est développé en
Python 3.13 avec PySide6 et communique exclusivement avec le backend FastAPI via HTTP REST.

Le Desktop est un client graphique léger. Il ne porte pas la logique métier principale, ne connaît pas la structure
interne des repositories backend et n'accède jamais directement à PostgreSQL. Son rôle est de présenter les données,
d'orchestrer les interactions utilisateur et d'appeler l'API centrale par l'intermédiaire d'un client HTTP unique.

### 1.2 Vision du client Desktop

La vision Desktop est la suivante :

> Construire une application interne stable, rapide, modulaire et professionnelle, comparable à un outil de pilotage
> d'entreprise, où chaque module peut évoluer indépendamment sans rompre la cohérence globale.

Le Desktop doit rester :

- clair pour les utilisateurs métier ;
- prévisible pour les développeurs ;
- robuste face aux erreurs réseau ;
- cohérent avec l'identité UI/UX officielle ;
- extensible pour les futurs modules ;
- strictement découplé de la base de données.

### 1.3 Place dans l'écosystème global

```text
Utilisateur interne
        |
        v
Desktop PySide6
        |
        | HTTP REST / JSON
        v
API FastAPI
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

Le Desktop n'est pas une alternative au backend. Il est une surface d'utilisation. Toute règle métier, autorisation,
validation complexe, écriture durable et lecture de données persistantes doit passer par l'API.

### 1.4 Objectifs techniques

| Objectif | Description | Impact attendu |
|---|---|---|
| Modularité | Une page par module, widgets réutilisables | Ajout de modules sans refactor global |
| Centralisation HTTP | Tous les appels passent par `ApiClient` | Gestion homogène des erreurs et tokens |
| Configuration unique | URL API, nom, version dans `config.py` | Déploiement plus simple |
| Style centralisé | Couleurs et apparence dans QSS | Cohérence avec `docs/UI_UX.md` |
| Responsabilités claires | `core`, `ui`, `widgets`, `styles`, `resources` | Maintenance durable |
| Résilience | États loading, empty, error, disconnected | UX fiable |
| Testabilité | Classes courtes, dépendances explicites | Validation plus simple |

### 1.5 Objectifs UX

| Objectif UX | Traduction Desktop |
|---|---|
| Navigation rapide | Sidebar persistante |
| Contexte visible | TopBar, StatusBar, page active |
| Données fiables | Messages d'erreur API et rafraîchissement clair |
| Lecture dense | Tables professionnelles, colonnes stables |
| Évolutivité | Place prévue pour recherche, notifications, permissions |
| Sobriété | Thème sombre, design orienté outil de travail |

### 1.6 Contraintes

| Contrainte | Règle |
|---|---|
| PostgreSQL | Aucun accès direct depuis Desktop |
| Backend | Aucun import direct de services, repositories ou models backend |
| API | Communication REST uniquement |
| UI/UX | Respect de `docs/UI_UX.md` |
| Sécurité | Respect de `docs/architecture/AUTHENTICATION.md` |
| Couleurs | Pas de couleurs métier codées en dur dans les widgets |
| Dépendances | Pas de dépendance Desktop non justifiée |
| Architecture | Pas de classe géante centralisant toute l'application |

### 1.7 Principes directeurs

1. Le Desktop affiche, l'API décide.
2. Les pages orchestrent l'interface, les widgets restent génériques.
3. `ApiClient` est le seul point de sortie HTTP.
4. Les erreurs doivent être visibles, lisibles et non destructives.
5. La navigation doit rester stable pendant toute l'évolution du produit.
6. Le thème visuel doit être centralisé dans QSS.
7. Toute extension doit s'ajouter à l'existant sans refactor global.

---

## 2. Principes d'architecture

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet |
|---|---|---|
| Séparation interface/backend | Éviter duplication métier et couplage | Les pages appellent `ApiClient`, jamais SQLAlchemy |
| Aucun accès PostgreSQL | Sécurité et cohérence architecture | Pas de driver DB dans Desktop |
| REST exclusif | Contrat stable entre Desktop et API | `API_BASE_URL` pointe vers `/api/v1` |
| Client API centralisé | Gestion homogène erreurs, auth, timeout | `desktop/core/api_client.py` |
| Widgets réutilisables | Éviter duplication UI | `desktop/widgets/` pour Sidebar, TopBar, StatusBar |
| Pages isolées | Évolutivité par module | `desktop/ui/*_page.py` |
| QSS centralisé | Cohérence graphique | `desktop/styles/dark.qss` |
| Configuration centralisée | Déploiement et environnements | `desktop/core/config.py` |
| Constantes partagées | Navigation stable | `desktop/core/constants.py` |
| Extensibilité modulaire | Préparer SEO, GEO, IA, rapports | Ajout page + constants + MainWindow |
| Respect UI/UX | Cohérence produit | Alignement avec `docs/UI_UX.md` |

### 2.2 Séparation stricte interface/backend

Le Desktop ne doit jamais réimplémenter :

- la validation métier complexe ;
- le calcul de score SEO/GEO ;
- la gestion des permissions ;
- la persistance ;
- les règles de suppression ;
- les contraintes d'unicité ;
- les appels aux connecteurs externes.

Ces responsabilités appartiennent au backend.

### 2.3 Centralisation des appels HTTP

```text
Page UI
  |
  +-- Interdit : httpx.get(...)
  |
  +-- Autorisé : self.api_client.get(...)
```

La centralisation permet :

- l'authentification future ;
- le refresh token automatique futur ;
- les timeouts uniformes ;
- le logging technique ;
- le mapping des erreurs ;
- la simulation en tests.

### 2.4 Cohérence avec UI_UX.md

`docs/UI_UX.md` est la source de vérité pour :

- couleurs ;
- densité ;
- structure générale ;
- composants ;
- états ;
- tables ;
- formulaires ;
- navigation ;
- accessibilité.

Le présent document définit comment traduire cette vision dans l'architecture Desktop.

---

## 3. Vue d'ensemble de l'architecture Desktop

### 3.1 Vue arborescente courte

```text
desktop/
    main.py
    app.py
    core/
    ui/
    widgets/
    resources/
    styles/
```

### 3.2 Vue globale Desktop/API

```text
+------------------------+
| PySide6 Desktop        |
| - MainWindow           |
| - Pages                |
| - Widgets              |
| - ApiClient            |
+-----------+------------+
            |
            | HTTP REST / JSON
            v
+-----------+------------+
| FastAPI Backend        |
| - Routes               |
| - Dependencies         |
+-----------+------------+
            |
            v
+-----------+------------+
| Services               |
+-----------+------------+
            |
            v
+-----------+------------+
| Repositories           |
+-----------+------------+
            |
            v
+-----------+------------+
| PostgreSQL             |
+------------------------+
```

### 3.3 Vue logique

```text
Presentation Layer
  |
  +-- MainWindow
  +-- Pages UI
  +-- Widgets
  +-- QSS Theme

Desktop Core Layer
  |
  +-- Config
  +-- Constants
  +-- ApiClient
  +-- Future SessionManager

Backend Boundary
  |
  +-- REST API
  +-- JSON contracts
  +-- HTTP status codes
```

### 3.4 Vue physique

```text
Windows workstation
  |
  v
Python 3.13 process
  |
  v
QApplication event loop
  |
  +-- MainWindow
  +-- Widgets
  +-- Pages
  |
  v
HTTPS requests to backend
  |
  v
Backend host
```

### 3.5 Vue par responsabilités

| Couche | Responsabilité | Exemple |
|---|---|---|
| Entrypoint | Lancer l'application | `main.py` |
| Bootstrap | Créer QApplication, charger QSS | `app.py` |
| Core | Config, constantes, HTTP | `core/` |
| Shell | Fenêtre principale et layout | `ui/main_window.py` |
| Pages | Écrans métier | `ui/websites_page.py` |
| Widgets | Composants réutilisables | `widgets/sidebar.py` |
| Styles | Apparence centralisée | `styles/dark.qss` |
| Resources | Images, icônes, logos | `resources/` |

---

## 4. Arborescence officielle

### 4.1 Arborescence cible Sprint 08

```text
desktop/
├── main.py
├── app.py
├── core/
│   ├── api_client.py
│   ├── config.py
│   └── constants.py
├── ui/
│   ├── main_window.py
│   ├── dashboard_page.py
│   ├── websites_page.py
│   ├── entities_page.py
│   ├── keywords_page.py
│   ├── competitors_page.py
│   ├── reports_page.py
│   └── administration_page.py
├── widgets/
│   ├── sidebar.py
│   ├── topbar.py
│   └── statusbar.py
├── resources/
│   ├── icons/
│   └── logo/
└── styles/
    └── dark.qss
```

### 4.2 Responsabilités par dossier

| Dossier | Rôle | Peut contenir | Ne doit jamais contenir |
|---|---|---|---|
| `desktop/` | Racine du client Desktop | Entrypoints, sous-dossiers | Logique métier backend |
| `desktop/core/` | Services techniques Desktop | Config, ApiClient, constantes | Widgets Qt complexes |
| `desktop/ui/` | Pages et fenêtres | MainWindow, pages métier | Repositories, SQL, models backend |
| `desktop/widgets/` | Composants réutilisables | Sidebar, TopBar, StatusBar | Appels API métier directs sauf cas générique validé |
| `desktop/styles/` | Styles QSS | Thèmes, variantes futures | Code Python |
| `desktop/resources/` | Assets | Icônes, logo, images | Données métier ou secrets |

### 4.3 Responsabilités par fichier

| Fichier | Rôle | Responsabilité | Interdits |
|---|---|---|---|
| `main.py` | Point d'entrée | Appeler le bootstrap | Construire toute l'UI |
| `app.py` | Bootstrap Qt | QApplication, QSS, MainWindow | Logique métier |
| `core/config.py` | Configuration | APP_NAME, APP_VERSION, API_BASE_URL | Secrets en dur |
| `core/constants.py` | Constantes | Pages, labels, identifiants | Appels API |
| `core/api_client.py` | HTTP REST | get/post/put/delete, erreurs | UI Qt |
| `ui/main_window.py` | Shell principal | Composition et navigation | Logique métier backend |
| `ui/*_page.py` | Page module | UI et appels via ApiClient | SQL, repositories |
| `widgets/sidebar.py` | Navigation | Menu et sélection | Décision permission serveur |
| `widgets/topbar.py` | Contexte haut | Titre, recherche future | Appels métier lourds |
| `widgets/statusbar.py` | État bas | Messages système | Persistance |
| `styles/dark.qss` | Thème | Couleurs, états visuels | Données dynamiques |

### 4.4 Conventions associées

- Un fichier de page se termine par `_page.py`.
- Une classe de page se termine par `Page`.
- Un widget réutilisable ne dépend pas d'une page spécifique.
- Les libellés de navigation viennent de `constants.py`.
- Les URLs API viennent de `config.py`.
- Les styles sont exprimés en QSS, pas dans les pages, sauf nécessité technique ponctuelle.

---

## 5. Cycle de vie de l'application

### 5.1 Flux de démarrage

```text
desktop/main.py
      |
      v
desktop/app.py
      |
      v
QApplication
      |
      v
Chargement du QSS
      |
      v
MainWindow
      |
      v
Initialisation Widgets
      |
      v
Dashboard
```

### 5.2 Diagramme de séquence de démarrage

```text
OS / user          main.py          app.py          QApplication          MainWindow          Dashboard
   |                 |                |                  |                    |                  |
   | py desktop/main |                |                  |                    |                  |
   |---------------->|                |                  |                    |                  |
   |                 | run app        |                  |                    |                  |
   |                 |--------------->|                  |                    |                  |
   |                 |                | create app       |                    |                  |
   |                 |                |----------------->|                    |                  |
   |                 |                | load QSS         |                    |                  |
   |                 |                | instantiate      |                    |                  |
   |                 |                |------------------------------------>|                  |
   |                 |                |                  |                    | build pages      |
   |                 |                |                  |                    |----------------->|
   |                 |                | show window      |                    |                  |
   |                 |                | event loop       |                    |                  |
   |                 |<---------------|                  |                    |                  |
```

### 5.3 Étapes détaillées

| Étape | Responsable | Description |
|---|---|---|
| Point d'entrée | `main.py` | Lance la fonction de bootstrap |
| Création app | `app.py` | Instancie `QApplication` |
| Configuration globale | `app.py` | Nom application, style global |
| Chargement thème | `app.py` | Lit `styles/dark.qss` |
| Fenêtre principale | `MainWindow` | Assemble shell |
| ApiClient | `MainWindow` ou futur container | Crée le client API partagé |
| Widgets | `MainWindow` | TopBar, Sidebar, StatusBar |
| Pages | `MainWindow` | Crée et enregistre pages |
| Page initiale | `MainWindow` | Affiche Dashboard |
| Boucle Qt | `QApplication` | Attend événements |

### 5.4 Fermeture

À la fermeture :

- Qt ferme la boucle d'événements ;
- les requêtes en cours futures devront être annulées proprement ;
- les ressources temporaires doivent être libérées ;
- une déconnexion API explicite ne doit être faite que si l'utilisateur clique "Déconnexion" ;
- les logs futurs doivent être flushés.

---

## 6. `main.py`

### 6.1 Rôle

`desktop/main.py` est le point d'entrée exécutable de l'application. Il doit rester minimal.

### 6.2 Responsabilités

| Doit faire | Ne doit pas faire |
|---|---|
| Importer la fonction de lancement | Construire des widgets |
| Appeler la fonction de bootstrap | Charger des données métier |
| Retourner un code de sortie | Appeler directement l'API |
| Être lisible immédiatement | Gérer la navigation |

### 6.3 Gestion du code de sortie

Le point d'entrée doit transmettre le code de sortie de la boucle Qt au système. Cela permet :

- diagnostic de lancement ;
- packaging futur ;
- tests de démarrage ;
- intégration avec scripts internes.

### 6.4 Exceptions de démarrage

Les exceptions critiques futures doivent être gérées au niveau bootstrap, pas dans les pages. Exemple :

- fichier QSS introuvable ;
- erreur d'initialisation Qt ;
- configuration invalide ;
- impossibilité d'ouvrir la fenêtre.

### 6.5 Exemple conceptuel

```python
from app import run_desktop_app


if __name__ == "__main__":
    raise SystemExit(run_desktop_app())
```

Cet exemple illustre la philosophie : `main.py` délègue.

---

## 7. `app.py`

### 7.1 Rôle

`desktop/app.py` est le bootstrap de l'application Qt. Il centralise la création de `QApplication`, le chargement du
style et l'instanciation de `MainWindow`.

### 7.2 Responsabilités

| Responsabilité | Description |
|---|---|
| Créer `QApplication` | Initialiser la boucle Qt |
| Configurer le nom | Utiliser `APP_NAME` |
| Charger QSS | Lire `desktop/styles/dark.qss` |
| Créer `MainWindow` | Instancier le shell principal |
| Afficher fenêtre | `window.show()` |
| Lancer boucle Qt | `application.exec()` |

### 7.3 Règles

- Ne pas faire d'appel API métier dans `app.py`.
- Ne pas construire directement les pages dans `app.py`.
- Ne pas mettre de constantes de navigation dans `app.py`.
- Ne pas coder le thème dans Python.
- Remonter un code de sortie clair.

### 7.4 Gestion des erreurs critiques

| Erreur | Comportement attendu |
|---|---|
| QSS absent | Démarrer avec style par défaut ou afficher erreur critique selon mode |
| MainWindow impossible | Retourner code non nul |
| Configuration invalide | Message technique clair |
| Erreur Qt | Log critique futur |

---

## 8. Configuration Desktop

### 8.1 Rôle de `config.py`

`desktop/core/config.py` centralise les paramètres applicatifs du client Desktop.

### 8.2 Paramètres actuels

| Paramètre | Valeur cible | Rôle |
|---|---|---|
| `APP_NAME` | `Veille SEO-GEO Groupe A.P&Partner` | Nom affiché |
| `APP_VERSION` | `0.1.0` | Version Desktop |
| `API_BASE_URL` | `http://127.0.0.1:8000/api/v1` | Base API REST |
| `HTTP_TIMEOUT_SECONDS` | `5.0` | Timeout HTTP |

### 8.3 Paramètres futurs

| Paramètre futur | Usage |
|---|---|
| `ENVIRONMENT` | `dev`, `staging`, `production` |
| `LOG_LEVEL` | Niveau logs Desktop |
| `TOKEN_STORAGE_MODE` | Stockage sécurisé tokens |
| `REQUEST_RETRY_COUNT` | Retry contrôlé |
| `API_HEALTH_PATH` | Endpoint santé |
| `THEME_NAME` | Thème actif |
| `FEATURE_FLAGS` | Activation progressive |

### 8.4 Environnements

| Environnement | API | Usage |
|---|---|---|
| Dev | `http://127.0.0.1:8000/api/v1` | Développement local |
| Staging | URL interne de recette | Validation métier |
| Production | URL interne sécurisée | Usage stable |

### 8.5 Erreurs à éviter

- URL API codée directement dans une page.
- Secret ou clé API dans `config.py`.
- Modification manuelle de plusieurs fichiers pour changer d'environnement.
- Dépendance à une variable non documentée.

---

## 9. Constantes Desktop

### 9.1 Rôle de `constants.py`

`desktop/core/constants.py` centralise les noms stables de pages et les identifiants de navigation.

### 9.2 Contenu attendu

| Type | Exemple | Usage |
|---|---|---|
| Nom de page | `PAGE_DASHBOARD` | Mapping navigation |
| Label module | `Tableau de bord` | Affichage Sidebar |
| Liste navigation | `NAVIGATION_PAGES` | Construction Sidebar |
| Identifiant futur | `dashboard` | Permissions, routes internes |

### 9.3 Conventions

- Constantes en majuscules.
- Préfixe `PAGE_` pour les pages principales.
- Libellés utilisateur cohérents avec `UI_UX.md`.
- Pas de logique conditionnelle dans `constants.py`.

### 9.4 Évolutions futures

La navigation future pourra distinguer :

- `page_id` interne ;
- `label` affiché ;
- `icon` Lucide ;
- `required_permission` ;
- `route` interne ;
- `is_visible`.

Exemple conceptuel :

```text
NavigationItem(
  id="websites",
  label="Websites",
  icon="Globe",
  required_permission="websites:read"
)
```

---

## 10. ApiClient

### 10.1 Rôle

`desktop/core/api_client.py` est le seul composant autorisé à effectuer des appels HTTP vers le backend FastAPI.

```text
Page UI
  |
  v
ApiClient
  |
  v
HTTP REST
  |
  v
FastAPI
```

### 10.2 Responsabilités

| Responsabilité | Description |
|---|---|
| Construire les URLs | Base URL + path |
| Exécuter les requêtes | Via `httpx` |
| Appliquer timeout | Éviter blocage indéfini |
| Parser JSON | Retourner payload Python |
| Gérer erreurs réseau | Convertir en erreur lisible |
| Préparer auth future | Ajouter Bearer token |
| Préparer refresh futur | Renouveler tokens |
| Centraliser logging futur | Tracer erreurs API |

### 10.3 Méthodes attendues

| Méthode | Usage |
|---|---|
| `get(path, params=None)` | Lecture |
| `post(path, json=None)` | Création/action |
| `put(path, json=None)` | Modification complète ou partielle selon contrat API |
| `delete(path)` | Suppression |
| `check_health()` | Vérification API |

### 10.4 Pourquoi centraliser

Sans centralisation :

- chaque page gérerait ses propres erreurs ;
- les timeouts seraient incohérents ;
- l'authentification future serait dupliquée ;
- les tests seraient plus difficiles ;
- les changements d'API seraient coûteux.

### 10.5 Timeouts

| Type d'appel | Timeout cible |
|---|---:|
| Health check | 2 à 5 s |
| Liste paginée | 5 à 10 s |
| Création/modification | 10 s |
| Export futur | Job asynchrone recommandé |
| Crawl futur | Jamais en requête bloquante longue |

### 10.6 Gestion des erreurs réseau

| Erreur | Cause | Comportement ApiClient | Comportement UI |
|---|---|---|---|
| Timeout | Backend lent | Lever erreur normalisée | Message + réessayer |
| Connection refused | API arrêtée | Lever erreur API indisponible | Bandeau ou message page |
| DNS | Hôte introuvable | Lever erreur réseau | Message configuration |
| HTTP 500 | Erreur serveur | Lever erreur API | Message non bloquant |
| HTTP 401 futur | Token absent/expiré | Tenter refresh futur | Reconnexion si échec |
| HTTP 403 futur | Permission manquante | Lever erreur forbidden | Page accès refusé |
| JSON invalide | Réponse non conforme | Lever erreur parsing | Message technique propre |

### 10.7 Réponses paginées

Les listes backend doivent être traitées comme paginées lorsque le contrat l'indique.

Exemple `GET /api/v1/websites` :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

### 10.8 Règles de parsing paginé

| Champ | Type | Usage |
|---|---|---|
| `items` | list | Lignes de table |
| `total` | int | Nombre total |
| `page` | int | Page courante |
| `page_size` | int | Taille page |
| `pages` | int | Nombre total de pages |

Une page UI ne doit jamais supposer qu'un endpoint paginé retourne directement une liste.

### 10.9 Authentification future

Le futur `ApiClient` devra :

- ajouter `Authorization: Bearer <access_token>` ;
- détecter `401 token_expired` ;
- appeler `/auth/refresh` ;
- rejouer une requête idempotente si pertinent ;
- déclencher une déconnexion si refresh échoue ;
- ne jamais logger les tokens.

### 10.10 Retry futur

Les retries doivent être contrôlés :

- pas de retry infini ;
- pas de retry automatique sur actions non idempotentes sans idempotency key ;
- backoff progressif ;
- message utilisateur si l'opération est retardée.

### 10.11 Diagramme de séquence d'un appel API réussi

```text
User          Page UI          ApiClient          FastAPI          Service          Repository
 | click        |                  |                 |                |                 |
 |------------->|                  |                 |                |                 |
 |              | get("/websites") |                 |                |                 |
 |              |----------------->|                 |                |                 |
 |              |                  | HTTP GET        |                |                 |
 |              |                  |---------------->|                |                 |
 |              |                  |                 | route          |                 |
 |              |                  |                 |--------------->|                 |
 |              |                  |                 |                | query           |
 |              |                  |                 |                |---------------->|
 |              |                  |                 |                | data            |
 |              |                  |                 |                |<----------------|
 |              |                  |                 | response       |                 |
 |              |                  |<----------------|                |                 |
 |              | update table     |                 |                |                 |
 |<-------------|                  |                 |                |                 |
```

### 10.12 Diagramme de séquence d'un appel API en erreur

```text
User          Page UI          ApiClient          FastAPI / Network          StatusBar
 | action       |                  |                      |                     |
 |------------->|                  |                      |                     |
 |              | call API         |                      |                     |
 |              |----------------->|                      |                     |
 |              |                  | timeout / 500 / down |                     |
 |              |                  |<---------------------|                     |
 |              | ApiClientError   |                      |                     |
 |              |<-----------------|                      |                     |
 |              | show error state |                      |                     |
 |              | update status    |                      |-------------------->|
```

---

## 11. MainWindow

### 11.1 Rôle

`desktop/ui/main_window.py` est le conteneur principal de l'application. Il assemble le shell, instancie les pages,
gère la navigation et expose un cadre stable.

### 11.2 Composition

```text
+----------------------------------------------------------------------------------+
| TopBar                                                                           |
+----------------------+-----------------------------------------------------------+
| Sidebar              | Central Content / QStackedWidget                         |
|                      |                                                           |
| Navigation           | Page active                                               |
|                      |                                                           |
+----------------------+-----------------------------------------------------------+
| StatusBar                                                                        |
+----------------------------------------------------------------------------------+
```

### 11.3 Responsabilités

| Responsabilité | Description |
|---|---|
| Créer `ApiClient` partagé | Même client pour les pages |
| Créer les pages | Dashboard, Websites, placeholders |
| Enregistrer les pages | Mapping nom -> widget |
| Créer widgets shell | Sidebar, TopBar, StatusBar |
| Gérer navigation | Changer la page active |
| Mettre à jour statut | Afficher module actif |

### 11.4 Responsabilités interdites

`MainWindow` ne doit pas :

- appeler directement les endpoints métier ;
- parser les réponses `websites` ;
- contenir les règles métier ;
- gérer les formulaires complexes ;
- connaître SQLAlchemy ;
- stocker des secrets ;
- devenir une classe géante.

### 11.5 État actif

L'état actif comprend :

- page courante ;
- libellé de module ;
- sélection Sidebar ;
- message StatusBar ;
- breadcrumb futur ;
- permissions visibles futures.

---

## 12. Système de navigation

### 12.1 Principe

La navigation principale passe par la Sidebar. Chaque entrée correspond à une page enregistrée dans `MainWindow`.

### 12.2 Mapping

```text
Sidebar item label
        |
        v
MainWindow.show_page(label)
        |
        v
pages[label]
        |
        v
QStackedWidget.setCurrentWidget(page)
```

### 12.3 Diagramme de séquence

```text
User          Sidebar          MainWindow          QStackedWidget          StatusBar
 | click item    |                  |                    |                    |
 |-------------->|                  |                    |                    |
 |               | current changed  |                    |                    |
 |               |----------------->|                    |                    |
 |               |                  | find page          |                    |
 |               |                  |------------------->|                    |
 |               |                  | set current page   |                    |
 |               |                  |------------------->|                    |
 |               |                  | update status      |                    |
 |               |                  |--------------------------------------->|
```

### 12.4 Page active

La page active doit être visible :

- visuellement dans la Sidebar ;
- textuellement dans la StatusBar ;
- demain dans la TopBar via breadcrumb ;
- demain dans les permissions et menus.

### 12.5 Évolutions futures

| Évolution | Description |
|---|---|
| Breadcrumb | `Module > Objet > Détail` |
| Historique | Back/forward interne |
| Deep links internes | Ouvrir directement une vue |
| Permissions | Masquer ou désactiver menus |
| Favoris | Accès rapide aux vues fréquentes |
| Recherche | Filtrer modules et commandes |

### 12.6 Navigation conditionnelle selon rôle

Quand l'authentification sera active, la navigation devra se construire depuis les permissions effectives retournées
par `/me`. Le Desktop peut masquer un menu, mais l'API doit rester l'autorité finale.

---

## 13. Pages UI

### 13.1 Architecture générale des pages

Une page UI est un widget PySide6 autonome responsable :

- de construire sa vue ;
- de déclencher ses appels via `ApiClient` ;
- d'afficher loading, empty, error, success ;
- de rester isolée des autres pages ;
- de ne pas porter de logique métier backend.

### 13.2 Tableau des pages actuelles

| Page | Rôle actuel | Responsabilité future | Dépendances autorisées | Dépendances interdites |
|---|---|---|---|---|
| `DashboardPage` | Accueil, état backend | KPI SEO/GEO, alertes, activité | `ApiClient`, config | SQL, repositories |
| `WebsitesPage` | Table sites via API | CRUD Websites, filtres, pagination | `ApiClient` | Accès PostgreSQL |
| `EntitiesPage` | Placeholder | Gestion entités | `ApiClient` futur | Models backend |
| `KeywordsPage` | Placeholder | Mots-clés, import/export | `ApiClient` futur | Logique SEO lourde |
| `CompetitorsPage` | Placeholder | Concurrents, comparaison | `ApiClient` futur | Scraping direct |
| `ReportsPage` | Placeholder | Rapports, génération | `ApiClient` futur | Génération locale métier |
| `AdministrationPage` | Placeholder | Users, rôles, API, logs | `ApiClient` futur | Secrets en clair |

### 13.3 Comportements obligatoires

| Comportement | Description |
|---|---|
| Loading | Afficher pendant chargement non instantané |
| Empty | Afficher si aucune donnée |
| Error | Afficher message propre sans crash |
| Refresh | Permettre rechargement si pertinent |
| Pagination | Respecter le contrat API |
| Permissions futures | Désactiver actions non autorisées |

### 13.4 Relation avec ApiClient

```text
Page
 |
 +-- reçoit ApiClient au constructeur
 |
 +-- appelle get/post/put/delete
 |
 +-- transforme payload API en affichage
 |
 +-- ne connaît pas transport interne
```

---

## 14. Pattern officiel pour créer une nouvelle page

### 14.1 Étapes

1. Créer un fichier dans `desktop/ui/`, par exemple `seo_page.py`.
2. Créer une classe `SeoPage(QWidget)`.
3. Ajouter une constante `PAGE_SEO` dans `constants.py`.
4. Ajouter le label à la liste de navigation.
5. Ajouter l'entrée visuelle dans la Sidebar si la Sidebar ne se base pas automatiquement sur la liste.
6. Instancier la page dans `MainWindow._build_pages()`.
7. Connecter la navigation.
8. Prévoir `loading`, `empty`, `error`.
9. Tester le lancement avec `py desktop/main.py`.
10. Lancer Ruff.

### 14.2 Checklist nouvelle page

| Contrôle | OK |
|---|---|
| Fichier dans `desktop/ui/` | |
| Classe nommée en PascalCase | |
| Hérite de `QWidget` ou composant adapté | |
| Reçoit `ApiClient` si elle appelle l'API | |
| N'appelle jamais `httpx` directement | |
| N'importe aucun module backend | |
| Utilise les constantes de navigation | |
| Gère API indisponible | |
| Gère réponse vide | |
| Respecte QSS et `UI_UX.md` | |
| Est enregistrée dans `MainWindow` | |
| Ruff passe | |

### 14.3 Exemple conceptuel

```text
desktop/ui/seo_page.py
  |
  +-- class SeoPage(QWidget)
        |
        +-- build header
        +-- build table
        +-- load data via ApiClient
        +-- display states
```

---

## 15. Widgets réutilisables

### 15.1 Rôle du dossier `widgets/`

`desktop/widgets/` contient les composants réutilisables qui ne sont pas des pages métier complètes.

### 15.2 Tableau widgets

| Widget | Rôle | Peut contenir | Ne doit pas contenir |
|---|---|---|---|
| Sidebar | Navigation principale | Liste modules, état actif | Appels métier, SQL |
| TopBar | Contexte global | Titre, recherche future, profil | Logique page spécifique |
| StatusBar | Messages système | Module actif, API future | Persistance |
| Future SearchBar | Recherche globale | Signaux, texte, raccourci | Appels non centralisés |
| Future DataTable | Table générique | Colonnes, pagination, tri | Règles métier module |
| Future EmptyState | État vide | Icône, message, action | Appels API |
| Future ErrorState | État erreur | Message, retry callback | Parsing métier |

### 15.3 Widget générique vs page métier

| Question | Si oui | Si non |
|---|---|---|
| Réutilisable dans plusieurs pages ? | Widget | Page ou composant local |
| Dépend d'un endpoint spécifique ? | Page | Widget possible |
| Contient une action métier ? | Page | Widget possible |
| Sert au shell global ? | Widget | Page |

### 15.4 Règles de création

- Construire des widgets petits.
- Exposer des méthodes simples.
- Communiquer par signaux/callbacks.
- Ne pas importer les pages dans les widgets.
- Ne pas charger de données métier dans un widget générique.

---

## 16. Sidebar

### 16.1 Rôle

La Sidebar est la navigation principale persistante de l'application.

### 16.2 Structure cible

```text
+------------------------------+
| Logo / App                   |
| Version                      |
+------------------------------+
| API status future            |
+------------------------------+
| Tableau de bord              |
| Websites                     |
| Entities                     |
| Keywords                     |
| Competitors                  |
| Reports                      |
| Administration               |
+------------------------------+
| User future                  |
+------------------------------+
```

### 16.3 Dimensions recommandées

| Élément | Dimension |
|---|---:|
| Largeur ouverte | 220 à 260 px |
| Largeur compacte future | 56 à 72 px |
| Hauteur item | 36 à 44 px |
| Padding horizontal | 12 à 16 px |
| Espacement items | 4 px |

### 16.4 État actif

| État | Apparence |
|---|---|
| Normal | Texte secondaire |
| Hover | Surface plus claire |
| Actif | Fond primary, texte blanc |
| Disabled futur | Texte faible, pas d'action |
| Alerte future | Badge à droite |

### 16.5 Interaction avec MainWindow

La Sidebar ne change pas directement le `QStackedWidget`. Elle signale le changement demandé à `MainWindow`, qui
reste responsable de la navigation.

---

## 17. TopBar

### 17.1 Rôle

La TopBar donne le contexte de l'application et accueillera les fonctions transverses.

### 17.2 Variante actuelle

```text
+----------------------------------------------------------------------------------+
| Veille SEO-GEO Groupe A.P&Partner                                                |
+----------------------------------------------------------------------------------+
```

### 17.3 Variante future avec recherche

```text
+----------------------------------------------------------------------------------+
| Websites > Liste des sites              [Rechercher Ctrl+K] [API OK] [Admin]     |
+----------------------------------------------------------------------------------+
```

### 17.4 Variante future avec notifications

```text
+----------------------------------------------------------------------------------+
| GEO > Analyse IA                    [Recherche] [3 alertes] [Admin]              |
+----------------------------------------------------------------------------------+
```

### 17.5 Éléments futurs

| Élément | Usage |
|---|---|
| Titre | Module courant |
| Breadcrumb | Contexte hiérarchique |
| Recherche | Recherche globale |
| Notifications | Alertes, rapports, erreurs |
| Profil | Utilisateur, rôle, déconnexion |
| Badge API | État backend compact |

---

## 18. StatusBar

### 18.1 Rôle

La StatusBar affiche des informations système discrètes et persistantes.

### 18.2 Contenu actuel

- message "Prêt" ;
- module actif ;
- messages simples.

### 18.3 Contenu futur

| Élément | Exemple |
|---|---|
| Backend | `API OK` |
| Temps réponse | `128 ms` |
| Module actif | `Websites` |
| Version | `v0.1.0` |
| Synchronisation | `Dernière sync 09:42` |
| Auth | `Admin` |
| Erreur non bloquante | `API lente` |

### 18.4 Exemples de statuts

| Situation | Message |
|---|---|
| Démarrage | `Initialisation...` |
| Prêt | `Prêt` |
| Navigation | `Module actif : Websites` |
| Refresh | `Rafraîchissement des sites...` |
| API indisponible | `Backend indisponible` |
| Données chargées | `128 sites chargés` |

---

## 19. Thème QSS

### 19.1 Rôle de `dark.qss`

`desktop/styles/dark.qss` centralise l'apparence visuelle du client Desktop.

### 19.2 Règles

- Couleurs principales dans QSS.
- Object names Qt utilisés pour cibler les zones.
- Pas de palette dispersée dans les widgets.
- Styles cohérents avec `docs/UI_UX.md`.
- Les exceptions en Python doivent être rares et justifiées.

### 19.3 Tableau styles

| Élément | Style attendu | Source |
|---|---|---|
| Fond global | Sombre, sobre | `UI_UX.md` palette surfaces |
| TopBar | Surface sombre, bordure basse | QSS |
| Sidebar | Surface très sombre | QSS |
| StatusBar | Surface sombre, bordure haute | QSS |
| Boutons | Primary, hover, disabled | QSS |
| Tables | Header sombre, lignes alternées | QSS |
| Labels titres | Taille et graisse | QSS |

### 19.4 Évolutions futures

| Évolution | Description |
|---|---|
| Multi-thèmes | `dark.qss`, `light.qss`, `high_contrast.qss` |
| Tokens QSS | Commentaires et variables simulées |
| Préférences utilisateur | Choix thème |
| Accessibilité | Contraste renforcé |

---

## 20. Ressources graphiques

### 20.1 Dossiers

| Dossier | Usage |
|---|---|
| `desktop/resources/icons/` | Icônes applicatives |
| `desktop/resources/logo/` | Logo AP ou produit |

### 20.2 Formats recommandés

| Type | Format |
|---|---|
| Icônes simples | SVG si supporté, sinon PNG |
| Logo | SVG source + PNG export |
| Images raster | PNG optimisé |
| Icône Windows future | ICO |

### 20.3 Conventions de nommage

| Ressource | Convention |
|---|---|
| Icône module | `module-websites.svg` |
| Icône action | `action-refresh.svg` |
| Logo produit | `logo-veille-seo-geo.svg` |
| Logo groupe | `logo-ap-partner.svg` |

### 20.4 Tailles

| Usage | Taille |
|---|---:|
| Sidebar | 18 à 20 px |
| Bouton | 16 à 18 px |
| Logo header | 24 à 32 px |
| Empty state | 32 à 48 px |
| Icône application | 256 px source |

---

## 21. Gestion des états

### 21.1 États UI officiels

| État | Définition | Affichage attendu | Action possible | Comportement technique |
|---|---|---|---|---|
| Loading | Données en chargement | Spinner, skeleton ou message | Attendre/annuler futur | Désactiver action concernée |
| Empty | Aucune donnée | Message vide utile | Ajouter ou modifier filtres | Table vide stable |
| Error | Échec opération | Message lisible | Réessayer, détails | Capturer exception |
| Success | Action réussie | Toast ou statut | Continuer | Rafraîchir si nécessaire |
| Disconnected | API inaccessible | Bandeau ou message page | Réessayer | Ne pas crasher |
| Unauthorized futur | Non connecté | Login | Se reconnecter | Effacer session invalide |
| Forbidden futur | Permission absente | Page accès refusé | Retour/contact admin | Ne pas masquer erreur API |
| Stale data | Données anciennes | Badge "non à jour" | Rafraîchir | Conserver affichage |
| Refreshing | Mise à jour en cours | Bouton disabled | Attendre | Éviter double appel |

### 21.2 Hiérarchie des états

```text
Page
 |
 +-- Loading initial
 |
 +-- Loaded
 |     |
 |     +-- Data
 |     +-- Empty
 |
 +-- Error
 |
 +-- Refreshing overlay
```

### 21.3 Messages adaptés au projet

| Cas | Message |
|---|---|
| Sites vides | `Aucun site web n'est disponible pour les filtres actuels.` |
| API offline | `Impossible de contacter l'API Veille SEO-GEO.` |
| Timeout | `Le backend met trop de temps à répondre.` |
| Permissions | `Vous n'avez pas accès à ce module.` |
| Refresh | `Actualisation des données...` |

---

## 22. Gestion des erreurs

### 22.1 Types d'erreurs

| Erreur | Origine | Traitement |
|---|---|---|
| Réseau | Connexion impossible | Message API indisponible |
| Timeout | Backend lent | Message + retry |
| JSON invalide | Contrat cassé | Message technique propre |
| Réponse inattendue | Champs manquants | Message page |
| 401 futur | Session expirée | Refresh ou login |
| 403 futur | Permission | Accès refusé |
| 500 | Backend | Message erreur serveur |
| UI | Exception widget | Log futur + fallback |

### 22.2 Flux d'erreur

```text
Action utilisateur
      |
      v
Page appelle ApiClient
      |
      v
Erreur ?
  |        |
 Non      Oui
  |        |
  v        v
Afficher  Normaliser erreur
données        |
               v
        Page affiche état error
               |
               v
        StatusBar mise à jour
```

### 22.3 Règles

- Ne jamais laisser une exception réseau fermer l'application.
- Ne pas afficher une stack trace brute à l'utilisateur final.
- Prévoir une action de retry si l'erreur est récupérable.
- Ne pas effacer les données déjà affichées si un refresh échoue, sauf si elles sont invalides.
- Indiquer quand les données peuvent être obsolètes.

---

## 23. Communication entre composants

### 23.1 Mécanismes autorisés

| Mécanisme | Usage |
|---|---|
| Signaux Qt | Communication widget -> parent |
| Slots Qt | Réaction parent ou page |
| Callbacks simples | Navigation, actions locales |
| Méthodes publiques courtes | Mise à jour d'état |
| Objet partagé contrôlé | `ApiClient`, futur session context |

### 23.2 Règles de couplage

```text
Widget enfant
  |
  +-- émet signal ou callback
  |
  v
Parent
  |
  +-- décide l'action
```

Un widget générique ne doit pas connaître les détails d'une page métier.

### 23.3 Exemple conceptuel

```text
Sidebar item selected
        |
        v
Callback on_page_selected(page_name)
        |
        v
MainWindow.show_page(page_name)
        |
        v
StatusBar.set_message(...)
```

### 23.4 Interdits

- Importer `MainWindow` dans un widget générique pour agir directement sur le shell.
- Importer une page dans une autre sans nécessité validée.
- Utiliser des variables globales mutables pour partager l'état.
- Déclencher des appels API cachés depuis un widget de pure présentation.

### 23.5 Matrice de communication autorisée

| Source | Destination | Mécanisme | Autorisé | Exemple |
|---|---|---|---:|---|
| Sidebar | MainWindow | Callback ou signal | Oui | Changement de page |
| MainWindow | StatusBar | Méthode publique | Oui | Message module actif |
| Page | ApiClient | Méthode directe | Oui | `get("/websites")` |
| Widget générique | ApiClient | Direct | Non | Sidebar ne charge pas les sites |
| Page A | Page B | Direct | Non | Passer par parent ou état partagé futur |
| ApiClient | Widget | Direct | Non | ApiClient ne connaît pas Qt |
| Worker futur | Page | Signal Qt | Oui | Données chargées |

### 23.6 Matrice de couplage cible

| Couche source | Core | UI pages | Widgets | Backend | PostgreSQL |
|---|---:|---:|---:|---:|---:|
| Core | Oui | Non | Non | REST seulement | Non |
| UI pages | Oui | Limité | Oui | Via ApiClient | Non |
| Widgets | Limité | Non | Oui | Non | Non |
| Styles | Non | Non | Non | Non | Non |
| Resources | Non | Non | Non | Non | Non |

---

## 24. Threading et performances

### 24.1 Principe

L'interface Qt ne doit pas être bloquée par des appels réseau longs, imports, exports, crawls ou calculs.

### 24.2 État actuel

Le Sprint 08 pose les fondations. Les appels simples peuvent être synchrones au début, mais l'architecture doit évoluer
vers des workers pour les opérations longues.

### 24.3 Règles futures

| Sujet | Règle |
|---|---|
| Appels API longs | Hors thread UI |
| Crawls | Job backend asynchrone |
| Exports | Job backend ou worker dédié |
| Pagination | Obligatoire pour grandes listes |
| Lazy loading | Pour détails non visibles |
| Refresh | Contrôlé, pas de boucle agressive |
| UI updates | Toujours dans le thread Qt principal |

### 24.4 Worker futur

```text
Page
 |
 | start worker
 v
QThread / Worker
 |
 | ApiClient call
 v
FastAPI
 |
 | result signal
 v
Page updates UI
```

### 24.5 Checklist performance

| Contrôle | OK |
|---|---|
| Aucun traitement long dans un handler de clic | |
| Les listes sont paginées | |
| Les boutons sont désactivés pendant un refresh | |
| Les appels concurrents sont limités | |
| Les erreurs worker sont remontées à la page | |
| Les tables ne reconstruisent pas inutilement tout l'écran | |
| Les données non visibles sont chargées à la demande | |

---

## 25. Authentification future

### 25.1 Référence

L'architecture complète est définie dans `docs/architecture/AUTHENTICATION.md`. Cette section décrit uniquement
l'impact côté Desktop.

### 25.2 Composants Desktop futurs

| Composant | Rôle |
|---|---|
| `LoginWindow` | Écran connexion |
| `SessionManager` | État utilisateur et tokens |
| `TokenStore` | Stockage sécurisé OS |
| `PermissionContext` | Permissions effectives |
| `AuthenticatedApiClient` | Bearer + refresh |

### 25.3 Flux futur

```text
Desktop démarre
      |
      v
Refresh token présent ?
      |
      +-- Non -> LoginWindow
      |
      +-- Oui -> /auth/refresh
                  |
                  +-- OK -> /auth/me -> MainWindow
                  +-- KO -> LoginWindow
```

### 25.4 Permissions UI

Le Desktop pourra :

- masquer les menus sans permission ;
- désactiver des boutons ;
- afficher un message d'accès refusé ;
- adapter les actions de table.

Mais l'API reste l'autorité finale.

### 25.5 Expiration session

| Cas | Comportement |
|---|---|
| Access expiré | Refresh transparent |
| Refresh expiré | Login requis |
| Session révoquée | Déconnexion forcée |
| 403 permission | Accès refusé |
| API indisponible | Mode dégradé |

### 25.6 Diagramme de séquence du refresh futur

```text
Page UI          ApiClient          SessionManager          Auth API          TokenStore
  | request         |                     |                    |                 |
  |---------------->|                     |                    |                 |
  |                 | access expired      |                    |                 |
  |                 |-------------------->|                    |                 |
  |                 |                     | read refresh       |                 |
  |                 |                     |-------------------------------------->|
  |                 |                     | refresh token      |                 |
  |                 |                     |<--------------------------------------|
  |                 |                     | POST /auth/refresh |                 |
  |                 |                     |------------------->|                 |
  |                 |                     | new tokens         |                 |
  |                 |                     |<-------------------|                 |
  |                 |                     | store refresh      |                 |
  |                 |                     |-------------------------------------->|
  |                 | replay request      |                    |                 |
  |<----------------|                     |                    |                 |
```

---

## 26. Intégration avec le backend FastAPI

### 26.1 Règles d'appel API

- Utiliser `API_BASE_URL`.
- Versionner via `/api/v1`.
- Appeler uniquement des endpoints REST.
- Respecter les contrats JSON.
- Traiter les codes HTTP.
- Ne jamais importer `backend.app.*` dans `desktop/`.

### 26.2 Matrice modules/endpoints futurs

| Module Desktop | Endpoint API futur | Usage |
|---|---|---|
| Dashboard | `GET /dashboard` | KPI globaux |
| Websites | `GET /websites` | Liste sites |
| Websites | `POST /websites` | Création site |
| Entities | `GET /entities` | Liste entités |
| Keywords | `GET /keywords` | Liste mots-clés |
| Competitors | `GET /competitors` | Liste concurrents |
| Reports | `GET /reports` | Liste rapports |
| Reports | `POST /reports` | Génération rapport |
| Administration | `GET /admin/health` | Santé système |
| Logs | `GET /admin/error-logs` | Logs |
| API | `GET /admin/api-keys` | Clés API |
| Auth future | `POST /auth/login` | Connexion |
| Auth future | `POST /auth/refresh` | Refresh |

### 26.3 Pagination

Les endpoints de liste doivent être consommés avec :

```text
page
page_size
search
sort
order
```

### 26.4 Compatibilité

Le Desktop doit être tolérant :

- champ optionnel absent ;
- liste vide ;
- page hors plage ;
- message d'erreur structuré ;
- backend indisponible.

Il ne doit pas être tolérant :

- contrat fondamental cassé sans message ;
- réponse non JSON pour endpoint JSON ;
- permissions contournées côté client.

### 26.5 Matrice de compatibilité des contrats API

| Changement backend | Compatible Desktop | Action attendue |
|---|---:|---|
| Ajout champ optionnel | Oui | Ignorer si non utilisé |
| Suppression champ obligatoire | Non | Erreur réponse inattendue |
| Renommage champ | Non | Adapter Desktop et documenter |
| Ajout endpoint | Oui | Aucun impact |
| Changement code HTTP | Risqué | Mettre à jour gestion erreurs |
| Passage liste vers pagination | Non si non prévu | Toujours anticiper pagination |
| Ajout permission requise | Oui si 403 géré | Adapter UI permissions |
| Changement version `/api/v2` | Non automatique | Stratégie de migration |

---

## 27. Module Websites

### 27.1 Objectif

Websites est le premier module réel du Desktop. Il affiche les sites suivis par la plateforme.

### 27.2 Endpoint

```text
GET /api/v1/websites
```

### 27.3 Réponse paginée

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

### 27.4 Table UI

| Colonne | Source | Format |
|---|---|---|
| Nom | `name` | Texte |
| URL | `url` | Texte/URL future |
| Actif | `is_active` | Oui/Non, badge futur |
| Entité | `entity_id` ou `entity.name` futur | Texte |

### 27.5 Flux

```text
User ouvre Websites
        |
        v
WebsitesPage.load_websites()
        |
        v
ApiClient.get("/websites")
        |
        v
FastAPI
        |
        v
Réponse paginée
        |
        v
Validation fields
        |
        v
Remplissage table
```

### 27.6 États

| État | Affichage |
|---|---|
| API OK avec données | Table remplie |
| API OK vide | Message aucun site |
| API indisponible | Message propre sans crash |
| Réponse invalide | Message réponse inattendue |
| Refresh | Bouton désactivé temporairement |

### 27.7 Évolutions CRUD

| Fonction | Pattern |
|---|---|
| Ajouter | Modal ou page formulaire |
| Modifier | Panneau latéral ou modal |
| Supprimer | Confirmation |
| Filtrer | Toolbar |
| Importer | Job backend |
| Exporter | Endpoint export |

---

## 28. Modules futurs

### 28.1 Tableau des modules

| Module | Rôle | Type UI principal | Endpoint cible |
|---|---|---|---|
| Entities | Marques/entités groupe | Table + détail | `/entities` |
| Keywords | Mots-clés | Table dense | `/keywords` |
| Competitors | Concurrents | Table + comparaison | `/competitors` |
| Reports | Rapports | Liste + preview | `/reports` |
| Administration | Paramètres système | Tabs + tables | `/admin/*` |
| SEO | Audits SEO | Dashboard + recommandations | `/seo/*` |
| GEO | Visibilité IA | Graphiques + tables | `/geo/*` |
| Crawler | Crawls sites | Jobs + progression | `/crawler/*` |
| IA | Exécutions IA | Logs + résultats | `/ai/*` |
| Prompts | Prompts IA/GEO | Table + éditeur | `/prompts` |
| Logs | Logs système | Table filtrée | `/admin/logs` |
| Configuration | Paramètres | Formulaires | `/admin/settings` |

### 28.2 Approche d'évolution

Chaque module doit suivre le même cycle :

```text
Page placeholder
      |
      v
Lecture API
      |
      v
Table/filtres
      |
      v
CRUD
      |
      v
États avancés
      |
      v
Permissions
```

---

## 29. Logging Desktop

### 29.1 Objectif

Le logging Desktop futur doit aider au diagnostic sans exposer de secrets.

### 29.2 Niveaux

| Niveau | Usage |
|---|---|
| INFO | Démarrage, fermeture, navigation |
| WARNING | API lente, retry, réponse inattendue |
| ERROR | Erreur API, erreur UI récupérée |
| CRITICAL | Impossible de démarrer |

### 29.3 À journaliser

- démarrage application ;
- version Desktop ;
- environnement ;
- endpoint appelé sans query sensible ;
- code HTTP ;
- temps de réponse ;
- erreur normalisée ;
- fermeture.

### 29.4 À ne jamais logger

| Donnée | Raison |
|---|---|
| Mot de passe | Secret |
| Access token | Secret |
| Refresh token | Secret |
| Clés API externes | Secret |
| Données personnelles inutiles | Minimisation |
| Corps complet d'une réponse sensible | Confidentialité |

### 29.5 Logs backend futurs

Les erreurs Desktop critiques pourront être envoyées au backend via un endpoint dédié, mais uniquement après validation
de la politique de confidentialité et sans secrets.

---

## 30. Tests Desktop

### 30.1 Stratégie

| Type | Objectif |
|---|---|
| Tests unitaires | ApiClient, parsing, helpers |
| Tests widgets | Construction widgets sans crash |
| Tests pages | États loading/error/empty |
| Tests intégration | API mockée |
| Tests manuels | Démarrage et navigation |
| Ruff | Qualité statique |

### 30.2 Validation manuelle minimale

```text
py desktop/main.py
```

Contrôler :

- fenêtre ouverte ;
- thème chargé ;
- navigation entre pages ;
- Websites sans crash API offline ;
- StatusBar mise à jour ;
- fermeture propre.

### 30.3 Checklist de validation

| Contrôle | OK |
|---|---|
| Application démarre | |
| Dashboard visible | |
| Navigation Sidebar fonctionne | |
| Websites gère API indisponible | |
| Websites gère réponse vide | |
| Aucun accès PostgreSQL | |
| Aucun import backend | |
| Ruff passe | |
| Pas de fichiers parasites suivis | |

### 30.4 Matrice de tests Desktop

| Élément | Test unitaire | Test widget | Test intégration | Test manuel |
|---|---:|---:|---:|---:|
| `ApiClient` | Oui | Non | Oui | Oui |
| `MainWindow` | Limité | Oui | Oui | Oui |
| `Sidebar` | Oui | Oui | Non | Oui |
| `StatusBar` | Oui | Oui | Non | Oui |
| `WebsitesPage` | Parsing | Oui | API mockée | API réelle/offline |
| QSS | Non | Snapshot futur | Non | Oui |
| Navigation | Oui | Oui | Oui | Oui |
| Auth future | Oui | Oui | Oui | Oui |

### 30.5 Diagramme de séquence d'un test manuel de démarrage

```text
Développeur          Terminal          main.py          app.py          MainWindow
    |                  |                 |                |                |
    | py desktop/main  |                 |                |                |
    |----------------->|                 |                |                |
    |                  | start process   |                |                |
    |                  |---------------->|                |                |
    |                  |                 | run app        |                |
    |                  |                 |--------------->|                |
    |                  |                 |                | create window  |
    |                  |                 |                |--------------->|
    |                  | window visible  |                |                |
    |<-----------------|                 |                |                |
```

---

## 31. Qualité de code

### 31.1 Règles Python

| Sujet | Règle |
|---|---|
| Typage | Type hints pertinents |
| Docstrings | Classes et méthodes publiques |
| Imports | Triés par Ruff |
| Classes | Courtes et spécialisées |
| Méthodes privées | Préfixe `_` |
| Nommage | PascalCase classes, snake_case fonctions |
| Exceptions | Normalisées |

### 31.2 Règles PySide6

- Construire les widgets dans le constructeur ou méthode dédiée.
- Utiliser layouts Qt, pas positions absolues.
- Nommer les widgets stylés avec `setObjectName`.
- Ne pas bloquer le thread UI.
- Connecter clairement signaux et slots.
- Éviter les widgets monolithiques.

### 31.3 Taille des classes

| Type | Taille cible |
|---|---:|
| Widget simple | < 150 lignes |
| Page standard | < 300 lignes |
| Page complexe | Découper avant 500 lignes |
| ApiClient | Peut croître mais doit rester structuré |
| MainWindow | Ne doit pas porter les détails métier |

---

## 32. Conventions de nommage

### 32.1 Fichiers

| Type | Convention | Exemple |
|---|---|---|
| Page | `module_page.py` | `websites_page.py` |
| Widget | `name.py` | `sidebar.py` |
| Core | nom fonctionnel | `api_client.py` |
| Style | thème | `dark.qss` |
| Ressource | kebab-case | `module-websites.svg` |

### 32.2 Classes

| Type | Convention | Exemple |
|---|---|---|
| Page | PascalCase + Page | `WebsitesPage` |
| Widget | PascalCase | `Sidebar` |
| Client | PascalCase | `ApiClient` |
| Erreur | PascalCase + Error | `ApiClientError` |

### 32.3 Méthodes

| Type | Convention | Exemple |
|---|---|---|
| Action publique | snake_case | `load_websites` |
| Helper privé | `_snake_case` | `_populate_table` |
| Slot Qt | verbe clair | `show_page` |
| Validation | `_parse_*` | `_parse_paginated_response` |

### 32.4 Signaux futurs

| Signal | Convention |
|---|---|
| Page changée | `page_selected` |
| Refresh demandé | `refresh_requested` |
| Erreur survenue | `error_occurred` |
| Données chargées | `data_loaded` |

### 32.5 QSS

| Élément | Convention |
|---|---|
| ObjectName | PascalCase descriptif |
| Page title | `PageTitle` |
| Table | `DataTable` |
| Sidebar | `Sidebar` |
| Status label | `StatusBarLabel` |

---

## 33. Anti-patterns interdits

### 33.1 Tableau des anti-patterns

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| Requête `httpx` directe dans une page | Erreurs et auth dupliquées | Utiliser `ApiClient` |
| Accès PostgreSQL depuis Desktop | Violation architecture et sécurité | Passer par FastAPI |
| Import `backend.app.*` dans Desktop | Couplage fort | Contrat REST |
| Logique métier dans l'UI | Incohérence backend | Service backend |
| URL API codée en dur | Déploiement fragile | `config.py` |
| Couleurs codées en dur | UI incohérente | QSS |
| Classe géante | Maintenance difficile | Découper pages/widgets |
| Duplication de table | Incohérence | Widget DataTable futur |
| Suppression séparation core/ui/widgets | Dette technique | Respect arborescence |
| Tokens loggés | Faille sécurité | Masquage strict |
| Retry infini | Charge backend | Retry borné |
| UI bloquée | Mauvaise UX | Worker futur |

### 33.2 Exemple interdit

```text
WebsitesPage
  |
  +-- importe psycopg
  +-- lit PostgreSQL
  +-- calcule règles métier
```

### 33.3 Exemple correct

```text
WebsitesPage
  |
  +-- ApiClient.get("/websites")
  |
  +-- affiche la réponse paginée
```

---

## 34. Checklist ajout de module

| Étape | Contrôle | OK |
|---|---|---|
| Page | Fichier créé dans `desktop/ui/` | |
| Classe | Nom PascalCase + `Page` | |
| Constants | Ajout `PAGE_*` | |
| Sidebar | Entrée visible ou générée | |
| MainWindow | Page enregistrée | |
| ApiClient | Aucun `httpx` direct | |
| États | Loading/empty/error prévus | |
| UI | Respect QSS et `UI_UX.md` | |
| API | Endpoint versionné `/api/v1` | |
| Pagination | Contrat respecté si liste | |
| Auth future | Permission prévue | |
| Documentation | Document module mis à jour si nécessaire | |
| Tests | Lancement + Ruff | |

---

## 35. Checklist avant Pull Request

| Contrôle | OK |
|---|---|
| `py desktop/main.py` démarre | |
| Navigation entre pages vérifiée | |
| API indisponible gérée sans crash | |
| API disponible testée si possible | |
| Ruff passe | |
| Pytest backend passe si changement transversal | |
| Aucun fichier parasite ajouté | |
| Aucun secret ajouté | |
| Aucun import backend dans Desktop | |
| Aucun accès PostgreSQL | |
| `docs/UI_UX.md` respecté | |
| `AUTHENTICATION.md` respecté pour auth | |
| Tables paginées correctement | |
| Messages utilisateur lisibles | |
| Documentation à jour | |

---

## 36. Roadmap Desktop

### 36.1 v0.1 shell

- Entrypoint ;
- QApplication ;
- MainWindow ;
- Sidebar ;
- TopBar ;
- StatusBar ;
- thème sombre ;
- Websites lecture API.

### 36.2 v0.2 modules CRUD

- CRUD Websites ;
- CRUD Entities ;
- CRUD Keywords ;
- formulaires ;
- confirmations ;
- tables plus robustes.

### 36.3 v0.3 dashboard KPI

- KPI SEO ;
- KPI GEO ;
- état API ;
- alertes ;
- activité récente.

### 36.4 v0.4 authentification

- Login ;
- tokens ;
- `/me` ;
- permissions ;
- menus conditionnels ;
- déconnexion.

### 36.5 v0.5 charts

- graphiques SEO ;
- graphiques GEO ;
- comparaisons IA ;
- périodes.

### 36.6 v0.6 reports

- génération rapports ;
- preview ;
- exports ;
- historique.

### 36.7 v0.7 GEO monitor

- prompts ;
- citations ;
- modèles IA ;
- suivi visibilité.

### 36.8 v0.8 configuration

- API keys ;
- paramètres ;
- logs ;
- santé système.

### 36.9 v0.9 packaging

- packaging Windows ;
- icône application ;
- configuration environnement ;
- logs locaux.

### 36.10 v1.0 version interne stable

- UX stable ;
- authentification complète ;
- modules principaux ;
- documentation alignée ;
- tests essentiels ;
- monitoring erreurs.

---

## 37. Annexes

### 37.1 Glossaire

| Terme | Définition |
|---|---|
| Desktop | Client graphique PySide6 |
| Shell | Structure globale MainWindow + navigation |
| Page | Écran principal d'un module |
| Widget | Composant réutilisable |
| QSS | Feuille de style Qt |
| ApiClient | Client HTTP REST centralisé |
| Backend | API FastAPI |
| Endpoint | Route REST appelée par Desktop |
| State | État UI : loading, error, empty |
| Placeholder | Page temporaire sans fonction métier complète |

### 37.2 Abréviations

| Abréviation | Signification |
|---|---|
| UI | User Interface |
| UX | User Experience |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| QSS | Qt Style Sheets |
| CRUD | Create, Read, Update, Delete |
| SEO | Search Engine Optimization |
| GEO | Generative Engine Optimization |
| IA | Intelligence artificielle |

### 37.3 Diagramme récapitulatif

```text
main.py
  |
  v
app.py
  |
  +-- QApplication
  +-- load dark.qss
  +-- MainWindow
          |
          +-- ApiClient
          +-- TopBar
          +-- Sidebar
          +-- QStackedWidget
          |      |
          |      +-- DashboardPage
          |      +-- WebsitesPage
          |      +-- EntitiesPage
          |      +-- KeywordsPage
          |      +-- CompetitorsPage
          |      +-- ReportsPage
          |      +-- AdministrationPage
          |
          +-- StatusBar
```

### 37.4 Conventions rapides

| Besoin | Règle rapide |
|---|---|
| Ajouter page | `ui/*_page.py` + constants + MainWindow |
| Appeler API | Toujours `ApiClient` |
| Ajouter style | `dark.qss` |
| Ajouter widget | `widgets/` si réutilisable |
| Ajouter ressource | `resources/icons` ou `resources/logo` |
| Gérer liste | Réponse paginée |
| Gérer erreur | Message propre + retry si possible |

### 37.5 Checklist rapide développeur

| Question | Réponse attendue |
|---|---|
| Ai-je importé le backend dans Desktop ? | Non |
| Ai-je appelé PostgreSQL ? | Non |
| Ai-je utilisé `ApiClient` ? | Oui |
| Ai-je prévu API offline ? | Oui |
| Ai-je respecté QSS ? | Oui |
| Ai-je ajouté la page à la navigation ? | Oui si nécessaire |
| Ai-je testé le démarrage ? | Oui |
| Ai-je lancé Ruff ? | Oui |

### 37.6 Résumé architectural

L'architecture Desktop officielle de Veille SEO-GEO Groupe A.P&Partner repose sur un shell PySide6 modulaire, un
client API centralisé, des pages isolées par module, des widgets réutilisables, une configuration partagée et un thème
QSS commun. Le Desktop reste volontairement léger : il présente les données, déclenche les actions utilisateur et
communique avec FastAPI. Il ne contient ni logique métier principale, ni accès base de données, ni import backend.

Cette spécification doit être appliquée à tous les futurs sprints Desktop afin de conserver une application stable,
maintenable et cohérente avec les documents `docs/UI_UX.md` et `docs/architecture/AUTHENTICATION.md`.
