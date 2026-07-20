# Sprint 37 — Moteur de recommandations SEO/GEO

## Statut du document

Ce document constitue le cadrage fonctionnel et architectural du Sprint 37. Il décrit le besoin, les sources, les
contrats envisagés et les critères de validation du futur moteur de recommandations SEO/GEO.

Il n'autorise aucune implémentation. Les choix de persistance, de schémas, d'API et d'interface devront être confirmés
par une analyse technique du dépôt et une validation explicite du périmètre avant tout développement.

## Objectif

Le Sprint 37 a pour objectif d'introduire une couche transverse de recommandations capable d'exploiter les données déjà
disponibles dans la Version 1.0. Il ne crée aucune nouvelle source de données : il consolide les constats, résultats,
événements et alertes produits ou persistés par les modules existants.

Le moteur devra transformer ces constats dispersés en recommandations :

- compréhensibles ;
- priorisées ;
- actionnables ;
- rattachées au bon Website ;
- traçables jusqu'à leur source ;
- cohérentes entre les modules.

La finalité du sprint est de faciliter le passage de l'observation à l'action, sans remplacer les analyses sources et
sans dupliquer leur logique métier.

## Contexte

La Version 1.0 dispose déjà des modules suivants :

- **SEO Analysis** ;
- **GEO Analysis** ;
- **Crawls** ;
- **Google Search Console** ;
- **Google Analytics 4** ;
- **Bing Webmaster Tools** ;
- **Monitoring** ;
- **Alertes** ;
- **Dashboard V2**.

Ces modules produisent déjà des informations exploitables : problèmes SEO, recommandations GEO, métriques de
visibilité et d'audience, états de synchronisation, événements opérationnels, alertes et recommandations déterministes
du Dashboard V2. Ces informations restent toutefois réparties entre plusieurs modèles, services, endpoints et écrans.

Le dépôt contient notamment des recommandations GEO persistées et une agrégation déterministe de recommandations dans
le Dashboard V2. Le Sprint 37 devra partir de cet existant, définir les responsabilités du moteur transverse et éviter
la création d'un second mécanisme concurrent portant les mêmes règles.

Le moteur de recommandations devra rester une couche de consolidation et de priorisation. Il ne devra ni recalculer les
analyses complètes des modules sources, ni appeler directement les connecteurs externes, ni modifier silencieusement les
données d'origine.

## Fonctionnalités attendues

### Agrégation des recommandations existantes

Le moteur devra collecter les recommandations, constats et signaux pertinents fournis par les services et repositories
existants. Chaque élément agrégé devra conserver son Website, sa source et, lorsque cela est possible, la référence de
l'objet d'origine : analyse, page crawlée, alerte, événement, import ou période.

### Consolidation des résultats

Les données issues de formats différents devront être normalisées dans une représentation fonctionnelle commune. La
consolidation devra préserver l'information utile de la source sans imposer à celle-ci le modèle interne d'un autre
module.

### Suppression des doublons

Le moteur devra éviter que plusieurs signaux équivalents produisent plusieurs recommandations actives identiques. La
stratégie de déduplication devra être déterministe et documentée. Elle pourra s'appuyer, après validation technique, sur
une combinaison stable comprenant notamment le Website, la source, la catégorie, la règle et l'objet concerné.

La déduplication ne devra pas fusionner des recommandations distinctes uniquement parce que leurs titres sont proches.
Elle devra aussi tenir compte du cycle de vie : la réapparition d'un problème résolu devra suivre une règle explicite.

### Calcul d'une priorité

Une priorité devra être calculée à partir de règles métier connues, par exemple la gravité du constat source, son
impact, sa récurrence, son étendue et la confiance accordée aux données disponibles. Les facteurs réellement retenus,
leurs valeurs et leurs éventuelles pondérations devront être définis et testés lors de l'implémentation.

### Classement des recommandations

Les recommandations devront pouvoir être classées de manière stable, en donnant la priorité aux actions les plus
importantes selon les règles validées. Les critères secondaires devront être explicites afin qu'un même jeu de données
produise le même ordre.

### Filtrage par Website

Toutes les consultations, synthèses et actions de cycle de vie devront respecter le contexte Website. Le moteur devra
permettre un filtrage explicite par `website_id` et ne jamais mélanger les données de sites différents dans une
recommandation individuelle.

### Préparation de l'alimentation du Dashboard V2

Le moteur devra prévoir une synthèse réutilisable par le Dashboard V2. Le Dashboard demeure une couche de restitution :
il devra consommer les résultats du moteur sans dupliquer les règles d'agrégation, de déduplication ou de priorité.

L'analyse technique devra déterminer comment faire évoluer l'endpoint existant de recommandations du Dashboard V2
sans rupture de contrat ni maintien de deux calculs concurrents.

### Préparation des futurs rapports

La représentation fonctionnelle devra permettre aux futurs rapports de filtrer et synthétiser les recommandations par
Website, source, catégorie, priorité, impact et statut. Le Sprint 37 ne comprend toutefois aucun nouvel export ni aucun
format avancé de rapport.

## Sources de recommandations

Les exemples ci-dessous cadrent les signaux fonctionnels envisagés. Ils ne définissent pas encore les seuils, périodes
de comparaison ou règles de génération, qui devront être validés avant implémentation.

### SEO Analysis

Les analyses SEO peuvent notamment signaler :

- un Title manquant ;
- une Meta Description absente ;
- un H1 absent ;
- un contenu insuffisant ;
- des images sans attribut `alt` ;
- des erreurs techniques détectées par les analyseurs existants.

Le moteur devra réutiliser les résultats SEO disponibles et ne pas réimplémenter les analyseurs dans le service de
recommandations.

### GEO Analysis

Les analyses GEO peuvent notamment signaler :

- une visibilité IA faible ;
- une absence de citations ;
- un score GEO faible.

Les recommandations GEO déjà persistées devront être réutilisées et normalisées, avec conservation de leur analyse,
de leur source et de leur niveau de priorité d'origine.

### Crawls

Les crawls fournissent le contexte technique et les pages sur lesquels reposent une partie des constats SEO. Le Sprint
37 privilégiera leur exploitation via les services d'analyse existants. Toute recommandation générée directement à
partir d'un crawl devra correspondre à une règle distincte, validée et non déjà couverte par SEO Analysis.

### Google Search Console

Les données Google Search Console peuvent notamment permettre de détecter :

- une baisse du CTR ;
- une baisse des impressions ;
- une baisse des clics.

Une baisse devra toujours être définie par une période de référence, un seuil et un volume suffisants. Le moteur ne
devra pas conclure à une anomalie à partir d'une variation non contextualisée.

### Google Analytics 4

Les données Google Analytics 4 peuvent notamment permettre de détecter :

- une baisse du trafic ;
- une baisse de l'engagement.

Les règles devront préciser les métriques, périodes, segments et seuils comparés afin que la recommandation soit
reproductible et explicable.

### Bing Webmaster Tools

Les données Bing Webmaster Tools peuvent notamment signaler :

- des erreurs d'indexation ;
- un sitemap invalide.

Le moteur devra s'appuyer sur les données déjà importées et ne pas appeler directement le connecteur Bing.

### Monitoring

Le Monitoring peut notamment signaler :

- un connecteur indisponible ;
- une synchronisation échouée.

Les recommandations opérationnelles devront conserver la référence de l'événement source et éviter de transformer
chaque répétition technique d'un même incident en nouvelle recommandation active.

### Alertes

Le centre d'Alertes peut notamment signaler :

- des alertes critiques ;
- des alertes récurrentes.

Le moteur devra éviter de dupliquer une alerte sous forme de plusieurs recommandations équivalentes. La frontière entre
alerte et recommandation devra rester claire : l'alerte signale une situation, tandis que la recommandation formule
l'action priorisée envisagée pour la traiter.

## Modèle métier envisagé

Une recommandation est envisagée avec les propriétés fonctionnelles suivantes :

| Propriété | Rôle fonctionnel envisagé |
| --- | --- |
| `id` | Identifiant unique de la recommandation. |
| `website_id` | Website auquel la recommandation est rattachée. |
| `source` | Module ou type de signal à l'origine de la recommandation. |
| `category` | Catégorie fonctionnelle utilisée pour le filtrage et la synthèse. |
| `title` | Intitulé court et actionnable. |
| `description` | Explication du constat, du contexte et de l'action recommandée. |
| `priority` | Niveau de priorité calculé selon les règles validées. |
| `impact` | Domaine d'impact principal. |
| `difficulty` | Niveau d'effort estimé. |
| `score` | Valeur de classement calculée ; son échelle reste à définir. |
| `status` | État courant dans le cycle de vie. |
| `created_at` | Date de création de la recommandation. |
| `updated_at` | Date de dernière mise à jour. |
| `metadata` | Contexte complémentaire structuré, limité aux données utiles et non sensibles. |

Cette liste constitue un cadrage fonctionnel et ne préjuge pas de la structure technique finale. Elle ne décide ni du
type des identifiants, ni de la persistance, ni des relations, ni des index, ni du format physique des métadonnées.

Le nom `metadata` décrit ici une propriété du contrat fonctionnel. Comme ce nom est réservé par SQLAlchemy Declarative,
l'éventuelle représentation technique devra utiliser un attribut interne compatible tout en conservant, si elle est
validée, une clé API explicite.

Des références vers les objets sources pourront être nécessaires pour garantir la traçabilité et la déduplication.
Elles devront être cadrées après inventaire des identifiants et contrats réellement disponibles.

## Priorisation

### Priority

- `Critical` ;
- `High` ;
- `Medium` ;
- `Low`.

### Impact

- `SEO` ;
- `GEO` ;
- `Technique` ;
- `Performance` ;
- `Business`.

### Difficulty

- `Easy` ;
- `Medium` ;
- `Hard`.

Les règles de calcul devront rester déterministes et explicables. À données et règles identiques, le moteur devra
produire la même priorité et le même score. Chaque recommandation devra pouvoir exposer les principaux facteurs ayant
conduit à son classement.

La relation entre `priority` et `score`, l'échelle du score, les seuils, les pondérations, le traitement des données
partielles et l'ordre de départage devront être documentés avant leur implémentation. La difficulté pourra contribuer au
classement, mais ne devra pas masquer un impact critique.

## Statuts

Les états fonctionnels envisagés sont :

- `OPEN` : recommandation active et non encore prise en charge ;
- `ACKNOWLEDGED` : recommandation reconnue ou prise en compte ;
- `RESOLVED` : action réalisée ou situation source résolue ;
- `IGNORED` : recommandation explicitement écartée.

Ces statuts préparent le futur cycle de vie sans imposer une implémentation particulière. Les transitions autorisées,
les permissions, la conservation de l'historique, la réouverture et le comportement lors d'une nouvelle occurrence
devront être définis pendant l'analyse technique.

## Architecture cible

L'architecture proposée respecte les couches officielles du projet.

### Backend

```text
Routes
  ↓
RecommendationService
  ↓
RecommendationRepository
  ↓
Recommendation
```

- les routes exposent les contrats HTTP, valident les entrées et appellent `RecommendationService` ;
- `RecommendationService` porte l'agrégation, la consolidation, la déduplication, la priorité et le cycle de vie ;
- `RecommendationRepository` centralise uniquement les accès aux données nécessaires ;
- `Recommendation` représente ici l'entité métier envisagée, sans préjuger de son mode de persistance final.

Aucune logique métier ne doit être placée dans les routes. Une route ne devra ni calculer un score, ni dédupliquer des
recommandations, ni interroger directement les repositories des modules sources.

### Desktop

```text
RecommendationsPage
  ↓
RecommendationsService
  ↓
ApiClient
  ↓
API REST
```

- `RecommendationsPage` gère l'affichage, les filtres et les interactions utilisateur ;
- `RecommendationsService` adapte les paramètres et réponses pour le Desktop ;
- `ApiClient` reste l'unique client HTTP et centralise l'authentification et les erreurs ;
- l'API REST constitue l'unique accès du Desktop aux recommandations.

Aucune logique métier ne doit être placée dans les pages Desktop. La page ne devra ni recalculer les priorités, ni
fusionner les sources, ni accéder directement à PostgreSQL ou aux API externes.

L'analyse précédant l'implémentation devra confirmer les fichiers à créer ou étendre et déterminer comment réutiliser
les recommandations du Dashboard V2 et de GEO Analysis sans duplication.

## Intégration Dashboard

Le moteur pourra alimenter le Dashboard V2 avec les informations suivantes :

- nombre de recommandations ouvertes ;
- recommandations critiques ;
- répartition par priorité ;
- répartition par catégorie ;
- recommandations récentes.

Ces indicateurs devront respecter le filtre Website et les permissions de l'utilisateur. Le Dashboard pourra présenter
une synthèse et proposer une navigation vers le futur écran de recommandations, mais il ne devra pas porter les règles
de calcul.

La définition de « récente », la période des synthèses, le traitement des statuts et les règles de comptage devront être
explicites. Les recommandations critiques ne devront pas être confondues avec les alertes critiques, même lorsqu'elles
proviennent du même signal source.

## API REST envisagée

Les endpoints suivants sont proposés :

| Méthode | Endpoint | Objectif envisagé |
| --- | --- | --- |
| `GET` | `/api/v1/recommendations` | Lister les recommandations avec filtres, tri et pagination. |
| `GET` | `/api/v1/recommendations/{id}` | Consulter le détail d'une recommandation. |
| `GET` | `/api/v1/recommendations/summary` | Obtenir la synthèse destinée notamment au Dashboard V2. |
| `PATCH` | `/api/v1/recommendations/{id}/status` | Modifier le statut selon les transitions et permissions autorisées. |

La route statique `/summary` devra être déclarée de manière à ne pas être capturée par la route dynamique `/{id}`.
L'ordre des routes ou un contrat de chemin non ambigu devra être confirmé pendant l'analyse technique.

### Filtres possibles

- `website_id` ;
- `source` ;
- `category` ;
- `priority` ;
- `status` ;
- `search` ;
- `page` ;
- `page_size` ;
- `sort` ;
- `order`.

Les valeurs autorisées, valeurs par défaut, champs de tri, limites de pagination, permissions et formats de réponse
devront suivre les conventions API existantes. Les listes devront être filtrables et paginées de manière stable.

Cette API constitue une proposition de conception. Elle sera validée lors de l'analyse technique précédant
l'implémentation, notamment au regard de l'endpoint existant `/api/v1/dashboard-v2/recommendations`, des contrats de
pagination et des permissions déjà en place.

## Hors périmètre

Le Sprint 37 ne comprend pas :

- l'intelligence artificielle générative ;
- le machine learning ;
- l'analyse prédictive ;
- le frontend React ;
- une API publique ;
- les exports avancés ;
- les notifications automatiques ;
- de nouvelles sources de données externes ;
- un refactor global ;
- une réécriture des moteurs SEO ou GEO ;
- un appel direct aux connecteurs externes depuis le moteur de recommandations ;
- une architecture parallèle au Dashboard V2 ou aux services existants.

## Critères d'acceptation

Lors de sa future implémentation, le Sprint 37 pourra être considéré comme validé si :

- l'architecture officielle est respectée ;
- les modules et données existants sont réutilisés ;
- aucune logique métier n'est placée dans les routes ou les pages Desktop ;
- aucune logique métier existante n'est dupliquée ;
- l'agrégation conserve la source et le contexte Website ;
- la déduplication et la priorité reposent sur des règles déterministes, explicables et testées ;
- l'intégration du Dashboard V2 est prévue sans calcul concurrent ;
- l'API validée est filtrable, triable et paginée ;
- les permissions et erreurs suivent les conventions du projet ;
- les tests adaptés couvrent les services, repositories, routes, schémas et services Desktop concernés ;
- les cas nominaux, données partielles, doublons, erreurs et transitions de statut sont testés ;
- Ruff est valide ;
- Pytest est valide ;
- la documentation technique et fonctionnelle est alignée sur l'implémentation réelle ;
- aucune régression n'est introduite dans les modules de la Version 1.0.

## Contraintes

Le présent travail de cadrage crée uniquement :

```text
docs/sprints/sprint-37-recommendations-engine.md
```

Il ne doit entraîner :

- aucune modification d'un fichier existant ;
- aucune modification de code ;
- aucun modèle SQLAlchemy ;
- aucun schéma Pydantic ;
- aucune migration Alembic ;
- aucun endpoint ;
- aucun test ;
- aucune nouvelle dépendance ;
- aucun commit ;
- aucun push ;
- aucune Pull Request.

Toute implémentation future devra commencer par l'analyse du dépôt, la vérification des composants réutilisables, la
liste précise des fichiers concernés et la validation du périmètre.
