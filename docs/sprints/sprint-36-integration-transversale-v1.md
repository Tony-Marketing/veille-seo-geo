# Sprint 36 — Intégration transversale Version 1.0

## Objectif

Le Sprint 36 est un sprint d'intégration destiné à transformer les fonctionnalités déjà développées en une Version 1.0 cohérente, stable et exploitable. Il vise à relier les modules existants, à harmoniser leurs interactions et à valider les parcours transversaux sans étendre le périmètre métier de la plateforme.

Ce sprint repose sur les principes suivants :

- aucune nouvelle fonctionnalité métier ;
- aucun nouveau modèle SQLAlchemy ;
- aucune migration Alembic ;
- aucun refactor global ;
- réutilisation maximale des composants, services, repositories, routes, pages et clients existants.

La valeur attendue réside dans la cohérence de l'ensemble : les fonctionnalités existantes doivent former une chaîne métier continue, compréhensible et fiable, depuis la sélection d'un site jusqu'à la restitution consolidée dans le Dashboard V2.

## Contexte

Tous les sprints précédents sont terminés et fusionnés dans `main`. Le Sprint 36 intervient après la livraison des différents modules métier et des composants transversaux nécessaires à leur exploitation commune.

Les jalons récents comprennent notamment :

- l'Orchestrateur des traitements, terminé ;
- le Dashboard V2, terminé.

La plateforme dispose donc déjà des briques nécessaires pour gérer les sites, les mots-clés, les crawls, les analyses SEO et GEO, les données issues des connecteurs externes, les rapports, le monitoring, les alertes et la restitution exécutive. Le présent sprint ne crée pas de nouvelle brique : il vérifie et consolide leurs interactions afin d'aboutir à une Version 1.0 intégrée.

## Chaîne métier

Le parcours transversal de référence est le suivant :

```text
Website
  → Keywords
  → Crawls
  → SEO Analysis
  → GEO Analysis
  → Google Search Console
  → Google Analytics 4
  → Bing Webmaster Tools
  → Reports
  → Monitoring
  → Alertes
  → Dashboard V2
```

Rôle de chaque étape :

1. **Website** : constitue le contexte principal du parcours. Le site sélectionné détermine le périmètre des données, traitements, filtres et restitutions affichés dans les autres modules.
2. **Keywords** : centralise les mots-clés suivis pour le site et fournit le contexte sémantique utilisé par les analyses et les restitutions.
3. **Crawls** : collecte les données techniques et éditoriales des URLs du site afin d'alimenter les contrôles et analyses ultérieurs.
4. **SEO Analysis** : exploite les données disponibles pour identifier les problèmes, scores et recommandations liés au référencement naturel.
5. **GEO Analysis** : mesure et qualifie la visibilité du site ou de la marque dans les moteurs d'IA générative, notamment au travers des réponses et citations suivies.
6. **Google Search Console** : apporte les données de performance organique, d'indexation, de requêtes, de clics, d'impressions, de CTR et de positions.
7. **Google Analytics 4** : apporte les données d'audience, d'acquisition, de sessions et d'engagement nécessaires à l'analyse des usages.
8. **Bing Webmaster Tools** : complète les signaux de visibilité, d'indexation et de performance issus de l'écosystème Bing.
9. **Reports** : consolide les résultats des différents modules dans des restitutions exploitables et rattachées au bon contexte Website.
10. **Monitoring** : reçoit et expose les événements opérationnels produits par les traitements, les synchronisations et les modules métier.
11. **Alertes** : transforme les anomalies pertinentes en alertes actionnables, sans créer de doublons pour un même événement ou une même situation active.
12. **Dashboard V2** : synthétise les indicateurs, états, tendances, alertes et recommandations issus des modules existants dans une vue cohérente et synchronisée.

La chaîne ne suppose pas que toutes les étapes soient exécutées systématiquement de manière séquentielle. Elle définit le contexte partagé, les dépendances fonctionnelles et la circulation attendue des informations entre les modules.

## Objectifs fonctionnels

Le Sprint 36 doit permettre de valider et d'homogénéiser les comportements transversaux suivants :

- **navigation transversale** : permettre le passage entre les modules de la chaîne métier sans rupture de parcours ni perte d'information utile ;
- **conservation du contexte Website** : préserver le site sélectionné pendant la navigation et lors des actions déclenchées depuis un module source ;
- **propagation des filtres** : transmettre les filtres compatibles, notamment le site, la période, la source, le statut ou la sévérité, vers les écrans cibles ;
- **rafraîchissement automatique après traitement** : actualiser les vues concernées après la fin d'un traitement, sans obliger l'utilisateur à reconstruire manuellement son contexte ;
- **Dashboard synchronisé** : garantir que le Dashboard V2 reflète les dernières données disponibles et les états produits par les modules existants ;
- **alimentation du Monitoring** : vérifier que les traitements et synchronisations pertinents génèrent les événements attendus et exploitables ;
- **alimentation des Alertes sans duplication** : s'assurer qu'une même anomalie ne crée pas plusieurs alertes actives équivalentes et que leur cycle de vie reste cohérent ;
- **homogénéisation des états Desktop** : harmoniser les comportements de chargement, absence de données, données partielles, succès et erreur ;
- **validation des parcours utilisateur** : tester les scénarios principaux de bout en bout, depuis le choix d'un Website jusqu'à la consultation du Dashboard V2, du Monitoring ou des Alertes.

## Architecture

L'architecture de la plateforme reste inchangée. Le Sprint 36 doit intégrer les modules dans les couches existantes sans créer d'architecture parallèle.

### Backend

```text
Routes
  → Services
  → Repositories
  → Models
```

- les routes assurent l'exposition HTTP, la validation des entrées, l'authentification et l'appel aux services ;
- les services portent l'orchestration applicative et la logique métier ;
- les repositories centralisent les accès aux données au moyen de SQLAlchemy ;
- les models représentent les structures persistées existantes.

Aucune logique métier ne doit être ajoutée dans les routes. Les routes doivent rester fines et déléguer les traitements aux services existants.

### Desktop

```text
Page
  → Service
  → ApiClient
  → API REST
```

- la page gère l'affichage et les interactions utilisateur ;
- le service Desktop prépare les appels et adapte les réponses pour l'interface ;
- `ApiClient` centralise les échanges HTTP, l'authentification et la gestion commune des erreurs ;
- l'API REST constitue l'unique point d'accès aux fonctions et données backend.

Aucune logique métier ne doit être ajoutée dans les pages Desktop. Les pages ne doivent ni recalculer des règles backend ni contourner les services Desktop et `ApiClient`.

## Contraintes techniques

Les contraintes suivantes sont obligatoires :

- aucune migration Alembic ;
- aucun nouveau modèle SQLAlchemy ;
- aucune nouvelle architecture ni couche parallèle ;
- aucun accès direct à PostgreSQL depuis le Desktop ;
- aucune API externe appelée directement depuis le Desktop ;
- aucune logique métier ajoutée dans les routes backend ;
- aucune logique métier ajoutée dans les pages Desktop ;
- aucune duplication volontaire d'un service, repository, client ou composant existant ;
- aucune rupture des contrats API existants sans nécessité explicitement validée.

## Stratégie d'intégration

La stratégie repose sur une consolidation progressive de l'existant :

1. **Réutiliser les services existants** pour toutes les opérations métier, synchronisations, analyses et agrégations déjà prises en charge.
2. **Vérifier les contrats entre modules** afin que les identifiants, filtres, statuts et réponses soient transmis de manière cohérente.
3. **Synchroniser les modules** après les traitements en actualisant uniquement les vues et données concernées.
4. **Conserver un contexte Website commun** au cours de la navigation, avec des règles de repli explicites lorsque le module cible ne prend pas en charge un filtre.
5. **Limiter les duplications** en centralisant les comportements communs dans les composants déjà prévus à cet effet.
6. **Homogénéiser les comportements Desktop** pour les chargements, rafraîchissements, erreurs, données vides ou partielles et confirmations de succès.
7. **Valider l'idempotence fonctionnelle** du Monitoring et des Alertes afin que les actualisations successives ne produisent pas de doublons.
8. **Contrôler la restitution Dashboard V2** après les actions principales pour vérifier la cohérence des données agrégées.

Chaque ajustement futur devra rester local, justifié par un parcours d'intégration identifié et compatible avec les conventions déjà en place.

## Tests prévus

### Backend

Les tests backend devront couvrir les intégrations avec :

- **Dashboard** : agrégation des données existantes, filtres, données partielles, états de santé et recommandations ;
- **Monitoring** : création et mise à jour des événements attendus après les traitements ;
- **Alertes** : génération, actualisation, résolution et absence de duplication ;
- **Scheduler** : sélection des traitements dus, conservation du contexte et idempotence de la planification ;
- **Worker** : exécution, transitions d'état, succès, erreurs, reprises et alimentation du Monitoring et des Alertes.

Les tests d'intégration devront vérifier les contrats entre routes, services et repositories sans déplacer la logique métier hors des services.

### Desktop

Les tests Desktop devront couvrir :

- la navigation entre les modules ;
- la propagation du contexte Website et des filtres compatibles ;
- le rafraîchissement après traitement ;
- les états de chargement ;
- les erreurs API, réseau, authentification, autorisation et validation ;
- les données partielles ;
- les scénarios de succès ;
- la synchronisation de l'affichage avec les données renvoyées par l'API ;
- l'usage exclusif de la chaîne `Page → Service → ApiClient → API REST`.

## Critères de validation

Le Sprint 36 pourra être considéré comme validé si :

- Ruff est OK ;
- Pytest est OK ;
- aucun nouveau warning bloquant n'est introduit ;
- aucune régression fonctionnelle ou technique n'est constatée ;
- l'architecture existante est respectée ;
- les routes backend restent exemptes de logique métier ;
- les pages Desktop restent exemptes de logique métier ;
- le contexte Website est conservé dans les parcours concernés ;
- les filtres compatibles sont propagés correctement ;
- le Dashboard V2 reflète les données et états disponibles ;
- le Monitoring est alimenté par les traitements attendus ;
- les Alertes sont alimentées sans duplication ;
- les états Desktop sont cohérents pour le chargement, l'erreur, les données partielles et le succès ;
- aucune migration Alembic ni aucun nouveau modèle SQLAlchemy n'est ajouté.

## Hors périmètre

Le Sprint 36 exclut explicitement :

- toute nouvelle fonctionnalité métier ;
- tout refactor global ;
- toute nouvelle table ;
- toute nouvelle migration Alembic ;
- tout nouveau modèle SQLAlchemy ;
- toute nouvelle architecture ;
- toute évolution React, le Desktop existant restant la cible de l'intégration ;
- toute réécriture complète d'un module existant ;
- tout accès direct du Desktop à PostgreSQL ;
- tout appel direct du Desktop à une API externe ;
- toute modification non nécessaire à la validation des parcours transversaux de la Version 1.0.

Le Sprint 36 est donc strictement un sprint d'intégration, de cohérence et de validation. Il consolide les composants déjà livrés pour constituer la Version 1.0 sans élargir le périmètre fonctionnel ni modifier les fondations techniques de la plateforme.
