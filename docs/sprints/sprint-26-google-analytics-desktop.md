# Sprint 26 — Google Analytics 4 Desktop

## Objectif

Le Sprint 26 a pour objectif de cadrer l'integration du module Google Analytics 4 dans l'application Desktop de la plateforme Veille SEO-GEO Groupe A.P&Partner.

Ce sprint concerne exclusivement le Desktop. Il s'appuie sur le backend Google Analytics 4 livre lors des Sprints 25 et 25A. Le Desktop ne recree aucune logique Google Analytics, ne calcule pas les indicateurs metier et ne contourne pas l'API REST.

Objectifs principaux :

- afficher les proprietes GA4 disponibles ;
- consulter les metriques GA4 importees ;
- afficher une vue Overview exploitable par l'utilisateur ;
- proposer les vues Traffic, Acquisition, Engagement, Conversions, Revenue et History ;
- declencher un import manuel via l'endpoint REST existant ;
- gerer recherche, filtres, pagination, actualisation et erreurs HTTP ;
- definir les tests Desktop avec `httpx.MockTransport`.

Aucune implementation n'est incluse dans ce document.

## Architecture

L'architecture Desktop obligatoire est la suivante :

```text
Page
    |
    v
Service
    |
    v
ApiClient
    |
    v
API REST
```

Le Desktop est uniquement une couche d'interface et de consommation REST.

Contraintes d'architecture :

- la page gere l'affichage, les interactions utilisateur et les etats visuels ;
- le service Desktop encapsule les appels REST Google Analytics 4 ;
- `ApiClient` realise les appels HTTP communs vers l'API FastAPI ;
- l'API REST reste le seul point d'entree vers les donnees Google Analytics ;
- toute la logique metier reste cote backend.

Le Desktop ne communique jamais directement avec PostgreSQL, SQLAlchemy ou Google Analytics. Il ne manipule aucun token Google et ne lance aucun appel Internet vers Google Analytics.

## Fonctionnalites prevues

### Affichage des proprietes GA4

La page Desktop doit permettre de consulter les proprietes Google Analytics 4 exposees par le backend.

Informations attendues selon la reponse REST disponible :

- identifiant interne ;
- identifiant de propriete GA4 ;
- nom de propriete ;
- compte associe ;
- identifiant de mesure lorsque disponible ;
- site associe lorsque disponible ;
- etat actif ou inactif ;
- expiration de token lorsque exposee par l'API.

Le Desktop affiche uniquement les donnees retournees par l'API. Il ne decide pas de l'etat metier d'une propriete.

### Vue Overview

La vue Overview doit afficher la synthese GA4 calculee cote backend.

Indicateurs attendus :

- sessions ;
- utilisateurs ;
- nouveaux utilisateurs ;
- sessions engagees ;
- pages vues ;
- duree moyenne de session ;
- taux d'engagement ;
- conversions ;
- revenu total.

Les valeurs sont consommees depuis l'endpoint REST `overview`. Le Desktop ne recalcule pas les ratios, moyennes ou totaux.

### Consultation paginee des metriques

La page Desktop doit permettre de consulter les metriques GA4 importees avec pagination.

Colonnes attendues :

- date ;
- propriete ;
- source ;
- medium ;
- campagne ;
- categorie d'appareil ;
- pays ;
- utilisateurs ;
- nouveaux utilisateurs ;
- sessions ;
- sessions engagees ;
- pages vues ;
- duree moyenne ;
- taux d'engagement ;
- conversions ;
- revenu total.

La pagination est fournie par l'API REST. Le Desktop transmet les parametres et affiche les resultats.

### Traffic

La vue Traffic doit presenter les agregats de trafic retournes par le backend, notamment par source.

Le Desktop ne groupe pas les donnees localement. Il affiche la dimension, les metriques associees et les filtres appliques.

### Acquisition

La vue Acquisition doit presenter les agregats d'acquisition retournes par le backend, notamment par medium.

Les calculs d'acquisition restent cote Service backend.

### Engagement

La vue Engagement doit presenter les agregats d'engagement retournes par le backend, notamment par categorie d'appareil.

Le Desktop affiche les indicateurs fournis sans recalculer le taux d'engagement ou la duree moyenne.

### Conversions

La vue Conversions doit presenter les agregats de conversions retournes par le backend.

Le Desktop ne definit pas les regles de conversion. Il affiche uniquement les donnees exposees par l'API REST.

### Revenue

La vue Revenue doit presenter les agregats de revenus retournes par le backend, notamment par campagne lorsque les donnees existent.

Le Desktop ne transforme pas les montants, ne convertit pas les devises et ne cree pas de logique commerciale locale.

### History

La vue History doit afficher l'historique enrichi des imports Google Analytics 4.

Informations attendues :

- identifiant d'import ;
- propriete ;
- nom de propriete ;
- identifiant GA4 ;
- date de debut ;
- date de fin ;
- statut ;
- lignes importees ;
- duree ;
- message d'erreur eventuel.

Les erreurs sont affichees sous forme utilisateur sans exposer de secret.

### Import manuel

Le Desktop doit permettre de declencher un import manuel via l'endpoint REST existant.

Flux attendu :

```text
Utilisateur
    |
    v
Page Desktop
    |
    v
Service Desktop
    |
    v
ApiClient
    |
    v
POST /api/v1/google-analytics/import
    |
    v
Backend GA4
```

Le Desktop transmet la propriete, la date de debut, la date de fin et les options exposees par l'API. Le backend realise l'import et retourne le resultat. Aucun appel Google Analytics n'est realise par le Desktop.

### Recherche

La recherche Desktop doit utiliser les parametres REST disponibles. Elle peut s'appliquer aux listes paginees qui exposent un champ `search`, notamment les metriques et l'historique.

La recherche est transmise au backend. Le Desktop n'effectue pas de filtrage metier local sur un jeu de donnees complet.

### Filtres

Les filtres Desktop doivent reprendre les filtres REST disponibles :

- `website_id` ;
- `property_id` ;
- `date_from` ;
- `date_to` ;
- `import_id` ;
- `source` ;
- `medium` ;
- `campaign` ;
- `device_category` ;
- `country` ;
- `status` pour l'historique ;
- `search` lorsque l'endpoint le supporte.

Le Desktop ne doit pas inventer de filtre non supporte par l'API.

### Pagination

La pagination doit reutiliser les conventions REST existantes du projet.

Elements attendus :

- page courante ;
- taille de page ;
- nombre total d'elements ;
- nombre total de pages ;
- liste des elements.

Le Desktop transmet les parametres de pagination a l'API REST et affiche la reponse.

### Actualisation

La page Desktop doit permettre de rafraichir les donnees visibles.

L'actualisation relance les appels REST necessaires avec les filtres courants. Elle ne declenche pas d'import sauf action explicite de l'utilisateur sur l'import manuel.

### Gestion des erreurs HTTP

Le Desktop doit gerer les erreurs HTTP retournees par l'API :

- `400` pour une requete invalide ;
- `401` pour une authentification absente ou expiree ;
- `403` pour des droits insuffisants ;
- `404` pour une ressource introuvable ;
- `422` pour une validation de payload ou de parametres ;
- `500` pour une erreur serveur controlee.

Le service Desktop remonte une erreur exploitable par la page. La page affiche un message utilisateur clair sans exposer de detail technique sensible.

### Tests Desktop

Les tests Desktop doivent couvrir le service Google Analytics 4, les appels via `ApiClient` et les reactions attendues face aux reponses REST simulees.

Ils doivent utiliser exclusivement `httpx.MockTransport` pour simuler l'API REST.

## Endpoints REST consommes

Le Sprint 26 consomme uniquement les endpoints REST existants des Sprints 25 et 25A. Aucun endpoint nouveau n'est defini dans ce document.

Prefixe REST :

```text
/api/v1/google-analytics
```

Endpoints de proprietes GA4 disponibles :

| Methode | Endpoint | Usage Desktop |
|---|---|---|
| `GET` | `/properties` | Lister les proprietes GA4 |
| `POST` | `/properties` | Creer une propriete GA4 si l'interface future l'expose |
| `PUT` | `/properties/{property_id}` | Mettre a jour une propriete GA4 si l'interface future l'expose |
| `DELETE` | `/properties/{property_id}` | Supprimer ou desactiver une propriete selon la regle backend |

Endpoints de consultation GA4 disponibles :

| Methode | Endpoint | Usage Desktop |
|---|---|---|
| `GET` | `/metrics` | Consulter les metriques GA4 paginees |
| `GET` | `/overview` | Afficher les KPIs de synthese |
| `GET` | `/traffic` | Afficher les agregats de trafic |
| `GET` | `/acquisition` | Afficher les agregats d'acquisition |
| `GET` | `/engagement` | Afficher les agregats d'engagement |
| `GET` | `/conversions` | Afficher les agregats de conversions |
| `GET` | `/revenue` | Afficher les agregats de revenus |
| `GET` | `/history` | Afficher l'historique enrichi des imports |

Endpoints d'import disponibles :

| Methode | Endpoint | Usage Desktop |
|---|---|---|
| `POST` | `/import` | Declencher un import manuel |
| `GET` | `/imports` | Lister les imports GA4 |
| `GET` | `/imports/{import_id}` | Consulter le detail d'un import |

Endpoints OAuth existants, non prioritaires pour l'ecran Desktop de consultation :

| Methode | Endpoint | Usage Desktop |
|---|---|---|
| `POST` | `/oauth/connect` | Connexion OAuth via backend si une interface admin future l'expose |
| `POST` | `/oauth/refresh` | Rafraichissement manuel via backend si une interface admin future l'expose |

Le Desktop ne doit pas appeler d'endpoint non documente dans les routes existantes. Les endpoints `events` ou `transactions` ne sont pas consommes, car ils ne sont pas presents dans le backend GA4 existant.

## Architecture logicielle

### Page

La page Google Analytics 4 Desktop gere uniquement l'interface :

- affichage des onglets ou sections ;
- tableaux ;
- filtres ;
- champs de recherche ;
- boutons d'actualisation et d'import manuel ;
- indicateurs de chargement ;
- messages d'erreur ;
- etats vides.

La page ne contient aucune logique metier. Elle ne communique pas directement avec l'API REST et ne calcule pas les indicateurs GA4.

### Service

Le service Desktop Google Analytics 4 encapsule les appels REST necessaires a la page.

Responsabilites :

- appeler les endpoints GA4 via `ApiClient` ;
- transmettre les filtres et parametres de pagination ;
- retourner a la page des donnees structurees ;
- convertir les erreurs HTTP en erreurs Desktop exploitables ;
- conserver une interface simple pour la page.

Le service ne contient aucune regle metier Google Analytics. Il ne calcule pas les KPIs, n'agrege pas les metriques et ne decide pas des statuts d'import.

### ApiClient

`ApiClient` realise les appels HTTP vers l'API REST.

Responsabilites :

- construire les requetes HTTP ;
- appliquer la configuration d'API existante ;
- transmettre les jetons applicatifs de session lorsque necessaire ;
- traiter les erreurs techniques HTTP selon les conventions Desktop ;
- rester reutilisable par les autres modules Desktop.

Le Sprint 26 doit reutiliser le client HTTP existant. Aucun nouveau client HTTP dedie a Google Analytics ne doit etre cree sans justification explicite.

### Backend

Toute la logique metier reste cote backend :

- validation des periodes ;
- validation des proprietes ;
- pagination et filtres SQLAlchemy ;
- calculs d'agregats ;
- calculs de KPIs ;
- import manuel ;
- idempotence ;
- OAuth ;
- appels Google Analytics ;
- persistance PostgreSQL ;
- normalisation des erreurs.

## Contraintes

Contraintes obligatoires du Sprint 26 :

- aucune logique metier Desktop ;
- aucun acces direct a PostgreSQL ;
- aucun acces direct a SQLAlchemy ;
- aucun acces direct a Google Analytics ;
- aucun appel Internet Google depuis le Desktop ;
- aucune manipulation de secret Google cote Desktop ;
- aucune duplication de logique backend ;
- aucune creation d'endpoint REST ;
- aucune modification du backend dans ce sprint de cadrage ;
- consommation exclusive des endpoints REST deja disponibles ;
- reutilisation de `ApiClient` ;
- tests Desktop sans acces reseau reel.

## Tests prevus

Les tests Desktop doivent utiliser `httpx.MockTransport` pour simuler les reponses de l'API REST.

Aucun test ne doit effectuer d'appel Internet. Aucun test ne doit appeler Google Analytics. Aucun test ne doit acceder a PostgreSQL.

Tests de service prevus :

- recuperation paginee des proprietes GA4 ;
- recuperation de la vue Overview ;
- recuperation paginee des metriques ;
- recuperation Traffic ;
- recuperation Acquisition ;
- recuperation Engagement ;
- recuperation Conversions ;
- recuperation Revenue ;
- recuperation History ;
- declenchement d'un import manuel ;
- transmission des filtres ;
- transmission de la recherche ;
- transmission de la pagination ;
- actualisation avec conservation des filtres ;
- gestion des erreurs `400`, `401`, `403`, `404`, `422` et `500` ;
- absence d'appel Internet.

Tests de page prevus :

- affichage d'un etat de chargement ;
- affichage des donnees retournees par le service ;
- affichage d'un etat vide ;
- affichage d'un message d'erreur ;
- reaction au bouton d'actualisation ;
- reaction au bouton d'import manuel ;
- mise a jour des filtres et de la pagination.

Les tests doivent verifier que le Desktop reste un consommateur REST et ne porte aucune logique metier GA4.

## Criteres de validation

Le Sprint 26 sera considere termine lorsque les criteres suivants seront respectes lors de l'implementation future :

- l'ecran Desktop Google Analytics 4 existe et respecte l'architecture `Page -> Service -> ApiClient -> API REST` ;
- les proprietes GA4 sont consultables depuis l'API REST ;
- la vue Overview consomme l'endpoint REST existant ;
- les metriques sont consultables avec pagination ;
- les vues Traffic, Acquisition, Engagement, Conversions, Revenue et History consomment les endpoints REST existants ;
- l'import manuel est declenche uniquement via `POST /api/v1/google-analytics/import` ;
- la recherche est transmise au backend ;
- les filtres disponibles sont transmis au backend ;
- la pagination est geree via les reponses REST ;
- l'actualisation relance les appels REST sans logique locale supplementaire ;
- les erreurs HTTP sont affichees proprement ;
- les tests Desktop utilisent `httpx.MockTransport` ;
- aucun test ne realise d'appel Internet ;
- aucun acces direct a PostgreSQL n'existe cote Desktop ;
- aucun appel direct a Google Analytics n'existe cote Desktop ;
- aucune logique metier backend n'est dupliquee dans le Desktop ;
- aucun endpoint non existant n'est invente ;
- les outils qualite disponibles du projet passent lors de l'implementation future.

Ce document constitue le cadrage documentaire du Sprint 26. Il ne contient aucune implementation et ne modifie pas l'architecture existante.
