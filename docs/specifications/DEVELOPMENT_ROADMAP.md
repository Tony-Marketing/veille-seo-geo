# Feuille de route de développement

## 1. Informations générales

| Élément | Description |
| --- | --- |
| Projet | Veille SEO-GEO Groupe A.P&Partner |
| Nature du document | Roadmap opérationnelle de développement |
| Périmètre | Backend FastAPI, base PostgreSQL, Desktop PySide6, préparation React, documentation et gouvernance |
| Public cible | Responsable projet, développeur backend, développeur desktop, futur intervenant frontend, relecteur technique |
| Statut | Document de cadrage évolutif |
| Niveau de détail | Pilotage par phases, lots et sprints recommandés |

Cette feuille de route traduit les documents de spécification du dossier
`docs/specifications/` en plan de développement progressif.

Elle s'appuie sur :

- le cahier des charges fonctionnel et métier ;
- la spécification des exigences logicielles ;
- la spécification de conception de base de données ;
- l'architecture existante du dépôt ;
- les règles projet définies dans la documentation interne.

Elle ne remplace pas les documents de spécification. Elle organise l'ordre
de réalisation, les dépendances, les priorités, les validations et les jalons
nécessaires pour faire avancer le projet sans casser l'existant.

### 1.1 Rôle du document

Le document sert à :

- prioriser les chantiers ;
- découper le projet en lots limités ;
- proposer des sprints testables ;
- clarifier les dépendances entre modules ;
- rappeler les validations attendues avant merge ;
- maintenir la stabilité de `main` ;
- préparer les évolutions futures sans les imposer immédiatement.

### 1.2 Relation avec le cahier des charges

Le cahier des charges décrit le besoin métier, le périmètre fonctionnel global,
les utilisateurs, les modules attendus, les limites et les critères de réussite.

La présente roadmap reprend ces besoins et les organise en séquence de
développement.

### 1.3 Relation avec la SRS

La spécification des exigences logicielles détaille les exigences fonctionnelles,
non fonctionnelles, les rôles, les permissions, les règles métier et les critères
d'acceptation.

La roadmap utilise ces exigences comme base de découpage, sans les dupliquer
endpoint par endpoint.

### 1.4 Relation avec la spécification base de données

La spécification de conception de base de données décrit les familles de tables,
les relations principales, les contraintes, les statuts, l'historisation et les
règles de migration.

La roadmap en déduit l'ordre prudent des migrations et les dépendances entre
modèles, sans détailler le schéma complet.

## 2. Principes directeurs de la roadmap

La roadmap doit préserver la stabilité du projet tout en permettant une avancée
régulière.

### 2.1 Progression par petits lots

Chaque lot doit rester :

- limité ;
- compréhensible ;
- testable ;
- relisable ;
- mergeable sans modification parasite.

Un sprint ne doit pas mélanger plusieurs chantiers majeurs si ces chantiers
peuvent être livrés séparément.

### 2.2 Stabilité de `main`

La branche `main` doit rester stable.

Les développements ne doivent jamais être faits directement sur `main`.

Chaque sprint ou lot doit utiliser une branche dédiée, puis une Pull Request
vers `main`.

### 2.3 Branches dédiées

Une branche dédiée doit correspondre à un objectif clair :

- une phase documentaire ;
- un module backend ;
- une évolution desktop ;
- une correction ciblée ;
- une préparation technique limitée.

La branche doit éviter les modifications hors périmètre.

### 2.4 Tests avant merge

Avant merge, les validations adaptées au périmètre doivent être exécutées.

Pour du code backend :

- tests Pytest ciblés ;
- Ruff ;
- vérification des migrations si nécessaire ;
- contrôle des erreurs API ;
- vérification de la séparation routes, services, repositories et models.

Pour du Desktop :

- vérification des appels HTTP REST ;
- gestion des erreurs API ;
- états de chargement, vide et erreur ;
- cohérence avec les écrans existants.

Pour de la documentation :

- cohérence des chemins ;
- absence de contradiction avec l'architecture ;
- absence de promesse technique non validée ;
- vérification du diff.

### 2.5 Documentation continue

Chaque sprint significatif doit mettre à jour la documentation utile.

La documentation ne doit pas être repoussée en fin de projet, car elle sert de
référence aux prochains lots.

### 2.6 Architecture stable

L'architecture backend obligatoire reste :

```text
Routes -> Services -> Repositories -> Models
```

Les règles associées sont structurantes :

- les routes FastAPI ne contiennent pas de logique métier ;
- les routes appellent les services ;
- les services contiennent la logique métier ;
- les repositories contiennent uniquement l'accès aux données SQLAlchemy ;
- les modèles SQLAlchemy représentent les tables ;
- les schémas Pydantic gèrent les entrées et sorties API ;
- le Desktop communique uniquement avec FastAPI via HTTP REST ;
- le Desktop ne doit jamais accéder directement à PostgreSQL.

### 2.7 Priorité aux fondations

Les fonctionnalités avancées SEO, GEO, reporting et Desktop dépendent d'un socle
stable.

L'ordre recommandé est donc :

1. gouvernance et documentation ;
2. fondations backend ;
3. authentification, administration et configuration ;
4. référentiels métier ;
5. modules SEO et GEO ;
6. reporting ;
7. Desktop exploitable ;
8. observabilité et durcissement ;
9. préparation React.

### 2.8 Séparation des surfaces

Le projet doit conserver une séparation claire entre :

- backend FastAPI ;
- base PostgreSQL ;
- application Desktop PySide6 ;
- futur frontend React.

Le backend doit exposer des contrats API cohérents et réutilisables par le
Desktop actuel et par le futur frontend React.

## 3. Vue d'ensemble des phases

| Phase | Intitulé | Objectif principal | Priorité |
| --- | --- | --- | --- |
| Phase 0 | Socle documentaire et gouvernance | Stabiliser le cadre projet | Critique |
| Phase 1 | Fondations backend | Consolider l'architecture API et métier | Critique |
| Phase 2 | Administration et configuration | Sécuriser les accès et les paramètres | Critique |
| Phase 3 | Gestion des sites et référentiels | Poser les entités métier centrales | Critique |
| Phase 4 | Mots-clés et contenus | Structurer le pilotage éditorial | Importante |
| Phase 5 | SEO | Suivre la visibilité et les performances SEO | Importante |
| Phase 6 | GEO | Suivre la visibilité dans les IA génératives | Importante |
| Phase 7 | Rapports et exports | Consolider les restitutions | Importante |
| Phase 8 | Application Desktop | Rendre les modules exploitables par les utilisateurs internes | Importante |
| Phase 9 | Observabilité, audit et durcissement | Fiabiliser l'exploitation | Importante |
| Phase 10 | Préparation frontend React | Préparer une interface web future | Secondaire |
| Phase future | Extensions avancées | Ajouter les intégrations et automatisations validées | Future |

## 4. Diagramme ASCII global de progression

```text
[Phase 0]
   |
   v
[Phase 1] -> [Phase 2] -> [Phase 3] -> [Phase 4]
   |             |             |             |
   |             v             v             v
   |        [Config]      [Sites]       [Mots-cles]
   |                                      [Contenus]
   v
[Phase 5 SEO] ---> [Phase 7 Rapports] ---> [Phase 8 Desktop]
   |
   v
[Phase 6 GEO] ---> [Phase 9 Audit/Durcissement]
   |
   v
[Phase 10 Preparation React] ---> [Extensions futures]
```

Ce diagramme indique un enchaînement recommandé. Il ne signifie pas que toutes
les phases doivent être strictement linéaires. Certains travaux peuvent avancer
en parallèle lorsque les dépendances sont stables.

## 5. Synthèse des dépendances majeures

| Élément | Dépend de | Bloque | Priorité | Remarque |
| --- | --- | --- | --- | --- |
| Architecture backend | Documentation architecture | Tous les modules backend | Critique | À respecter dans chaque sprint code |
| Authentification | Fondations backend | Administration, configuration sensible, exports | Critique | Doit protéger les endpoints sensibles |
| Rôles et permissions | Authentification | Administration, audit, actions sensibles | Critique | Base du contrôle d'accès |
| Configuration | Authentification, administration | Imports, exports, paramètres modules | Critique | Import/export non destructifs |
| Sites web | Fondations backend | Mots-clés, contenus, SEO, GEO, rapports | Critique | Entité métier centrale |
| Mots-clés | Sites web | SEO, contenus, rapports | Importante | Nécessite filtres et rattachements |
| Contenus | Sites web, mots-clés | Suivi éditorial, analyse SEO/GEO | Importante | Ne doit pas devenir un CMS complet initialement |
| Concurrents | Sites web | Comparaisons SEO/GEO | Importante | Statut actif/inactif recommandé |
| SEO | Sites, mots-clés, pages | Rapports, Desktop SEO | Importante | Commencer par un périmètre initial mesurable |
| GEO | Sites, concurrents, plateformes IA | Rapports GEO, comparaison IA | Importante | Évolutif par plateformes |
| Rapports | Sites, SEO, GEO, configuration | Exports utilisateurs, Desktop reporting | Importante | Automatisation future seulement |
| Logs et audit | Authentification, actions sensibles | Durcissement, support exploitation | Importante | Distinguer logs techniques et audit métier |
| Desktop | API stable | Utilisation interne quotidienne | Importante | HTTP REST uniquement |
| React futur | API stable, contrats JSON | Interface web future | Secondaire | Préparation progressive |

## 6. Lots de développement recommandés

| Lot | Objectif | Livrable attendu | Priorité |
| --- | --- | --- | --- |
| Documentation | Cadrer les décisions | Documents `docs/specifications/` cohérents | Critique |
| Base technique | Stabiliser FastAPI et les conventions | Structure API claire et testable | Critique |
| Authentification | Identifier les utilisateurs | Auth API et protections initiales | Critique |
| Administration | Gérer utilisateurs, rôles et permissions | Interface API admin sécurisée | Critique |
| Configuration | Centraliser les paramètres | API configuration et import/export contrôlé | Critique |
| Sites | Gérer les sites web | CRUD sites, statuts, filtres | Critique |
| Mots-clés | Gérer les requêtes métier | CRUD mots-clés et catégorisation | Importante |
| Contenus | Structurer la production éditoriale | Briefs, statuts, rattachements | Importante |
| Concurrents | Suivre les concurrents | CRUD concurrents et rattachements | Importante |
| SEO | Suivre les performances SEO | Métriques, historiques, filtres | Importante |
| GEO | Suivre les performances IA génératives | Requêtes, plateformes, résultats | Importante |
| Rapports | Restituer les analyses | Rapports filtrables et exports | Importante |
| Logs/Audit | Suivre les actions et erreurs | Journalisation exploitable | Importante |
| Desktop | Exploiter l'API en interne | Écrans PySide6 prioritaires | Importante |
| Préparation React | Préparer l'interface web future | Contrats API réutilisables | Secondaire |

## 7. Roadmap par phases

### 7.1 Phase 0 : socle documentaire et gouvernance

| Élément | Description |
| --- | --- |
| Objectif | Stabiliser le cadre de décision avant les prochains développements |
| Périmètre | Cahier des charges, SRS, conception base de données, roadmap |
| Livrables | Documents Markdown dans `docs/specifications/` |
| Dépendances | Documentation existante |
| Critères d'entrée | Branche dédiée, fichiers existants identifiés |
| Critères de sortie | Documents cohérents, diff documentaire propre |
| Risques | Redondance entre documents, promesses non validées |
| Priorité | Critique |

La phase 0 est documentaire uniquement. Elle ne doit pas modifier le backend,
le Desktop, les migrations, les tests ou les dépendances.

### 7.2 Phase 1 : fondations backend

| Élément | Description |
| --- | --- |
| Objectif | Consolider l'architecture backend et les conventions API |
| Périmètre | FastAPI, routes, services, repositories, models, schemas, erreurs |
| Livrables | Socle backend testable et cohérent |
| Dépendances | Architecture existante, documentation backend |
| Critères d'entrée | Documentation de référence disponible |
| Critères de sortie | Routes sans logique métier, services testables, repositories isolés |
| Risques | Refactor trop large, duplication de patterns |
| Priorité | Critique |

Cette phase doit rester centrée sur les fondations nécessaires aux modules.
Elle ne doit pas intégrer plusieurs domaines métier à la fois.

### 7.3 Phase 2 : administration et configuration

| Élément | Description |
| --- | --- |
| Objectif | Sécuriser les accès et centraliser les paramètres |
| Périmètre | Utilisateurs, rôles, permissions, paramètres applicatifs, import/export |
| Livrables | Administration protégée, configuration contrôlée |
| Dépendances | Authentification et fondations API |
| Critères d'entrée | Modèle d'utilisateur et règles d'accès définis |
| Critères de sortie | Endpoints sensibles protégés, actions auditables |
| Risques | Permissions trop permissives, import destructif |
| Priorité | Critique |

Le Sprint 06 est connu comme terminé pour l'interface d'administration backend.
Les prochains sprints doivent s'appuyer sur ce socle sans le casser.

### 7.4 Phase 3 : gestion des sites et référentiels

| Élément | Description |
| --- | --- |
| Objectif | Poser les entités centrales nécessaires aux modules SEO/GEO |
| Périmètre | Sites web, statuts, types, URL principale, rattachements futurs |
| Livrables | Module sites exploitable via API |
| Dépendances | Fondations backend, permissions |
| Critères d'entrée | Accès API sécurisé, modèles de base prêts |
| Critères de sortie | CRUD sites testé, filtres utiles, unicité contrôlée |
| Risques | Modèle trop large, règles d'unicité insuffisantes |
| Priorité | Critique |

Les sites servent de point d'ancrage aux mots-clés, contenus, concurrents,
mesures SEO, mesures GEO et rapports.

### 7.5 Phase 4 : mots-clés et contenus

| Élément | Description |
| --- | --- |
| Objectif | Structurer les requêtes ciblées et la production éditoriale |
| Périmètre | Mots-clés, intentions, catégories, URL cible, contenus, briefs |
| Livrables | Modules mots-clés et contenus reliés aux sites |
| Dépendances | Sites web |
| Critères d'entrée | Module sites stable |
| Critères de sortie | Données filtrables, exportables, rattachées aux sites |
| Risques | Confusion avec outil éditorial complet, suppression mal contrôlée |
| Priorité | Importante |

Cette phase prépare les analyses SEO/GEO sans chercher à couvrir toute la chaîne
éditoriale avancée.

### 7.6 Phase 5 : SEO

| Élément | Description |
| --- | --- |
| Objectif | Suivre les performances SEO initiales |
| Périmètre | Positions, visibilité, pages, requêtes, périodes, historiques |
| Livrables | Module SEO initial, filtres et exports de base |
| Dépendances | Sites, mots-clés, données temporelles |
| Critères d'entrée | Référentiels stables |
| Critères de sortie | Consultation par site, période et indicateur |
| Risques | Volumétrie, dépendance aux imports externes |
| Priorité | Importante |

Le périmètre initial doit privilégier la consultation structurée et
l'historisation avant les automatisations avancées.

### 7.7 Phase 6 : GEO

| Élément | Description |
| --- | --- |
| Objectif | Suivre la visibilité dans les IA génératives |
| Périmètre | Plateformes IA, prompts, réponses observées, mentions, citations |
| Livrables | Module GEO initial pour ChatGPT, Gemini, Claude, Copilot, Perplexity |
| Dépendances | Sites, concurrents, configuration, historique |
| Critères d'entrée | Entités de référence disponibles |
| Critères de sortie | Résultats consultables par site, plateforme et période |
| Risques | Variabilité des réponses IA, coûts API, comparabilité des mesures |
| Priorité | Importante |

Le module GEO doit rester extensible afin d'ajouter de nouvelles plateformes sans
refonte globale.

### 7.8 Phase 7 : rapports et exports

| Élément | Description |
| --- | --- |
| Objectif | Produire des restitutions exploitables |
| Périmètre | Rapports par site, période, modules inclus, exports |
| Livrables | Rapports initialement générables à la demande |
| Dépendances | Sites, SEO, GEO, configuration |
| Critères d'entrée | Données sources disponibles |
| Critères de sortie | Rapport consultable et exportable selon les droits |
| Risques | Agrégations incohérentes, exports trop larges |
| Priorité | Importante |

L'automatisation complète des rapports est une évolution future, pas une
obligation du premier lot reporting.

### 7.9 Phase 8 : application Desktop

| Élément | Description |
| --- | --- |
| Objectif | Donner une interface interne exploitable aux utilisateurs |
| Périmètre | Écrans prioritaires PySide6, navigation, appels HTTP REST |
| Livrables | Desktop connecté à l'API FastAPI |
| Dépendances | API stable, authentification, modules prioritaires |
| Critères d'entrée | Contrats API documentés et testés |
| Critères de sortie | États loading/empty/error et erreurs API gérés |
| Risques | Couplage trop fort au backend, accès direct interdit à la base |
| Priorité | Importante |

Le Desktop doit rester client de l'API. Aucun accès direct à PostgreSQL n'est
autorisé.

### 7.10 Phase 9 : observabilité, audit et durcissement

| Élément | Description |
| --- | --- |
| Objectif | Fiabiliser l'exploitation et les diagnostics |
| Périmètre | Logs techniques, audit métier, erreurs API, actions sensibles |
| Livrables | Journalisation exploitable et consultation contrôlée |
| Dépendances | Authentification, administration, modules métiers |
| Critères d'entrée | Actions sensibles identifiées |
| Critères de sortie | Logs filtrables, absence de secrets dans les traces |
| Risques | Surjournalisation, données sensibles exposées |
| Priorité | Importante |

Cette phase complète les modules existants et sécurise leur exploitation
quotidienne.

### 7.11 Phase 10 : préparation frontend React

| Élément | Description |
| --- | --- |
| Objectif | Préparer une future interface web sans développer le frontend complet |
| Périmètre | Contrats API, pagination, filtres, erreurs, authentification réutilisable |
| Livrables | API compatible avec Desktop et futur React |
| Dépendances | API stable |
| Critères d'entrée | Modules prioritaires disponibles |
| Critères de sortie | Réponses JSON cohérentes et documentées |
| Risques | Anticipation excessive, duplication avec Desktop |
| Priorité | Secondaire |

Le frontend React complet n'est pas dans le périmètre immédiat de cette roadmap.

### 7.12 Phase future : extensions avancées

| Élément | Description |
| --- | --- |
| Objectif | Étendre la plateforme après stabilisation des modules principaux |
| Périmètre | Automatisations, intégrations externes avancées, analyses enrichies |
| Livrables | À définir après validation métier |
| Dépendances | Socle stable, modules testés, besoins validés |
| Critères d'entrée | Arbitrage projet explicite |
| Critères de sortie | Non applicable à ce stade |
| Risques | Dispersion fonctionnelle, complexité d'intégration |
| Priorité | Future |

Les extensions avancées doivent être décidées au cas par cas.

## 8. Proposition de sprints

Les sprints ci-dessous sont indicatifs. Ils doivent être ajustés selon l'état
réel du code, les priorités métier et les retours de revue.

Ils ne signifient pas que tous les travaux sont déjà réalisés.

### 8.1 Sprint documentaire courant : spécifications

| Élément | Description |
| --- | --- |
| Nom | Lot documentaire `docs/specifications/` |
| Objectif | Finaliser le cadrage documentaire haut niveau |
| Périmètre inclus | Cahier des charges, SRS, conception base de données, roadmap |
| Périmètre exclu | Code backend, Desktop, migrations, tests, dépendances |
| Zones concernées | `docs/specifications/` |
| Critères d'acceptation | Documents cohérents, chemins corrects, aucune modification hors périmètre |
| Tests attendus | Vérifications Git et contrôle Markdown manuel |
| Documentation attendue | Les quatre documents du lot |
| Risques | Redondance, incohérence de vocabulaire |

Fichiers du lot :

- `docs/specifications/CAHIER_DES_CHARGES.md` ;
- `docs/specifications/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` ;
- `docs/specifications/DATABASE_DESIGN_SPECIFICATION.md` ;
- `docs/specifications/DEVELOPMENT_ROADMAP.md`.

Ce lot est documentaire uniquement.

### 8.2 Sprint 06 : administration backend

| Élément | Description |
| --- | --- |
| Statut | Connu comme terminé |
| Nom | Interface d'administration backend |
| Objectif | Fournir les capacités d'administration backend |
| Périmètre inclus | Utilisateurs, accès admin, protections associées selon l'existant |
| Périmètre exclu | Refonte globale de l'authentification |
| Zones concernées | Backend administration et documentation API administration |
| Critères d'acceptation | Endpoints admin protégés et comportements documentés |
| Tests attendus | Tests des droits admin existants ou ciblés |
| Documentation attendue | Documentation d'administration tenue à jour |
| Risques | Régression des protections admin |

Les sprints suivants doivent considérer ce sprint comme un socle, pas comme un
chantier à reconstruire.

### 8.3 Sprint 07 indicatif : configuration backend

| Élément | Description |
| --- | --- |
| Nom | Configuration applicative contrôlée |
| Objectif | Stabiliser les paramètres applicatifs et les imports/exports |
| Périmètre inclus | Paramètres, validation, import/export non destructif, audit minimal |
| Périmètre exclu | Automatisation complexe, interface React |
| Zones concernées | Routes configuration, services, repositories, models, schemas, tests |
| Critères d'acceptation | Import idempotent autant que possible, export filtré selon droits |
| Tests attendus | Tests services, API, droits, idempotence |
| Documentation attendue | Mise à jour configuration si comportement ajouté |
| Risques | Écrasement involontaire de paramètres, secrets exposés |

### 8.4 Sprint 08 indicatif : sites web

| Élément | Description |
| --- | --- |
| Nom | Référentiel sites web |
| Objectif | Mettre en place le module sites comme pivot métier |
| Périmètre inclus | Création, consultation, modification, désactivation, filtres |
| Périmètre exclu | Analyse SEO complète, reporting avancé |
| Zones concernées | Backend sites, migrations associées, tests ciblés |
| Critères d'acceptation | URL principale validée, unicité contrôlée, statut exploitable |
| Tests attendus | Tests routes, services, repositories, contraintes |
| Documentation attendue | Documentation module ou API si nécessaire |
| Risques | Mauvais modèle de statut, duplication d'URL |

### 8.5 Sprint 09 indicatif : mots-clés

| Élément | Description |
| --- | --- |
| Nom | Référentiel mots-clés |
| Objectif | Gérer les mots-clés rattachés aux sites |
| Périmètre inclus | CRUD, catégorisation, intention, URL cible, filtres, export |
| Périmètre exclu | Suivi complet des positions automatisées |
| Zones concernées | Backend mots-clés, migrations, tests |
| Critères d'acceptation | Mots-clés filtrables par site, statut et intention |
| Tests attendus | Tests validation, permissions, suppression contrôlée |
| Documentation attendue | Notes sur règles métier si ajoutées |
| Risques | Suppression cassant les historiques futurs |

### 8.6 Sprint 10 indicatif : contenus

| Élément | Description |
| --- | --- |
| Nom | Contenus et briefs éditoriaux |
| Objectif | Structurer les contenus liés aux sites et mots-clés |
| Périmètre inclus | Types, briefs, statuts, rattachements, historisation minimale |
| Périmètre exclu | CMS complet, publication automatique |
| Zones concernées | Backend contenus, schémas, services, tests |
| Critères d'acceptation | Contenus consultables par site, mot-clé, statut et auteur |
| Tests attendus | Tests services, filtres, transitions de statut |
| Documentation attendue | Règles de statut documentées si nécessaires |
| Risques | Surmodélisation éditoriale |

### 8.7 Sprint 11 indicatif : concurrents

| Élément | Description |
| --- | --- |
| Nom | Concurrents et rattachements |
| Objectif | Préparer les comparaisons SEO/GEO |
| Périmètre inclus | CRUD concurrents, domaines, statuts, rattachements aux sites |
| Périmètre exclu | Scoring concurrentiel avancé |
| Zones concernées | Backend concurrents, relations, tests |
| Critères d'acceptation | Concurrents actifs/inactifs rattachables à plusieurs sites |
| Tests attendus | Tests relations, droits, filtres |
| Documentation attendue | Règles de rattachement si ajoutées |
| Risques | Relations trop rigides pour les comparaisons futures |

### 8.8 Sprint 12 indicatif : SEO initial

| Élément | Description |
| --- | --- |
| Nom | Suivi SEO initial |
| Objectif | Introduire les métriques SEO de base |
| Périmètre inclus | Positions, pages, requêtes, périodes, historiques, filtres |
| Périmètre exclu | Intégrations externes avancées non validées |
| Zones concernées | Backend SEO, modèles, services, exports, tests |
| Critères d'acceptation | Consultation par site, période et indicateur |
| Tests attendus | Tests agrégation, filtrage, pagination, permissions |
| Documentation attendue | Description des indicateurs initiaux |
| Risques | Volumétrie, ambiguïté des métriques |

### 8.9 Sprint 13 indicatif : GEO initial

| Élément | Description |
| --- | --- |
| Nom | Suivi GEO initial |
| Objectif | Mesurer la visibilité dans les IA génératives |
| Périmètre inclus | Plateformes IA, prompts, réponses, mentions, citations, historique |
| Périmètre exclu | Automatisation massive des requêtes IA |
| Zones concernées | Backend GEO, configuration plateformes, tests |
| Critères d'acceptation | Résultats consultables par site, plateforme, requête et période |
| Tests attendus | Tests modèles, services, filtres, permissions |
| Documentation attendue | Description des plateformes et limites initiales |
| Risques | Variabilité des réponses IA, coûts d'usage, interprétation des scores |

Plateformes initiales ciblées :

- ChatGPT ;
- Gemini ;
- Claude ;
- Copilot ;
- Perplexity.

### 8.10 Sprint 14 indicatif : rapports et exports

| Élément | Description |
| --- | --- |
| Nom | Rapports initiaux |
| Objectif | Consolider les données SEO/GEO dans des restitutions |
| Périmètre inclus | Rapports par site, période, modules inclus, exports contrôlés |
| Périmètre exclu | Planification automatique complète |
| Zones concernées | Backend rapports, exports, permissions, tests |
| Critères d'acceptation | Rapport générable à la demande et exportable selon droits |
| Tests attendus | Tests filtres, droits, formats, erreurs |
| Documentation attendue | Règles de génération et limites |
| Risques | Agrégations imprécises, export de données non autorisées |

### 8.11 Sprint 15 indicatif : Desktop modules prioritaires

| Élément | Description |
| --- | --- |
| Nom | Desktop connecté aux modules prioritaires |
| Objectif | Rendre l'application Desktop exploitable sur les modules clés |
| Périmètre inclus | Navigation, sites, mots-clés, SEO/GEO initial, erreurs API |
| Périmètre exclu | Interface React, accès PostgreSQL direct |
| Zones concernées | Desktop PySide6, client HTTP, écrans prioritaires |
| Critères d'acceptation | Appels HTTP REST uniquement, états loading/empty/error gérés |
| Tests attendus | Vérifications manuelles, tests client si existants |
| Documentation attendue | Mise à jour Desktop si comportement ajouté |
| Risques | Couplage aux détails internes du backend |

### 8.12 Sprint 16 indicatif : logs, audit et durcissement

| Élément | Description |
| --- | --- |
| Nom | Observabilité et audit |
| Objectif | Améliorer le suivi technique et métier |
| Périmètre inclus | Logs techniques, audit des actions sensibles, filtres, conservation |
| Périmètre exclu | Supervision externe avancée non validée |
| Zones concernées | Backend logging, audit, administration, tests |
| Critères d'acceptation | Actions sensibles tracées sans secret |
| Tests attendus | Tests audit, erreurs, permissions |
| Documentation attendue | Règles de journalisation |
| Risques | Exposition de données sensibles dans les logs |

### 8.13 Sprint 17 indicatif : préparation React

| Élément | Description |
| --- | --- |
| Nom | Préparation API pour futur React |
| Objectif | Stabiliser les contrats réutilisables par une future interface web |
| Périmètre inclus | Pagination, filtres, erreurs standardisées, réponses JSON cohérentes |
| Périmètre exclu | Développement complet du frontend React |
| Zones concernées | API, schemas, documentation |
| Critères d'acceptation | Contrats lisibles, cohérents et compatibles Desktop |
| Tests attendus | Tests API et validation des erreurs |
| Documentation attendue | Conventions API mises à jour |
| Risques | Anticipation excessive sans besoin utilisateur immédiat |

## 9. Backend - fondations

### 9.1 Objectifs

Les fondations backend doivent garantir :

- une structure FastAPI lisible ;
- une séparation stricte des responsabilités ;
- des schémas Pydantic cohérents ;
- des erreurs API standardisées ;
- des services testables ;
- des repositories isolés ;
- des migrations explicites.

### 9.2 Étapes recommandées

| Étape | Description | Validation attendue |
| --- | --- | --- |
| Inventaire | Identifier les modules existants | Aucun doublon créé |
| Routes | Vérifier les conventions API | Routes sans logique métier |
| Services | Centraliser la logique métier | Tests services ciblés |
| Repositories | Encapsuler SQLAlchemy | Pas de SQL brut inutile |
| Models | Représenter les tables | Cohérence avec migrations |
| Schemas | Valider entrées/sorties | Pydantic v2 respecté |
| Erreurs | Standardiser les réponses | Desktop capable de les afficher |
| Tests | Couvrir les comportements principaux | Pytest ciblé OK |

### 9.3 Contraintes structurantes

- Ne pas ajouter de logique métier dans les routes.
- Ne pas appeler directement SQLAlchemy depuis les routes.
- Ne pas contourner les services pour les opérations métier.
- Ne pas utiliser `Base.metadata.create_all()` dans les migrations.
- Ne pas utiliser `Base.metadata.drop_all()` dans les migrations.
- Ne pas modifier les dépendances sans décision explicite.

## 10. Backend - authentification et administration

### 10.1 Objectifs

L'authentification et l'administration doivent protéger les fonctions sensibles
et permettre une gestion contrôlée des utilisateurs internes.

### 10.2 Périmètre recommandé

- utilisateurs ;
- rôles ;
- permissions ;
- activation et désactivation ;
- endpoints admin ;
- audit des actions sensibles ;
- tests de droits.

### 10.3 Validations attendues

| Validation | Attendu |
| --- | --- |
| Authentification | Un utilisateur non authentifié ne peut pas accéder aux endpoints protégés |
| Autorisation | Un utilisateur sans rôle adapté ne peut pas exécuter une action sensible |
| Administration | Les endpoints admin exigent des droits admin |
| Audit | Les actions sensibles sont traçables |
| Erreurs | Les refus d'accès sont explicites sans divulguer d'information sensible |

### 10.4 Points de vigilance

- Le Sprint 06 est considéré terminé.
- Les prochains lots ne doivent pas réécrire ce socle.
- Toute extension doit rester compatible avec les protections existantes.
- Les secrets ne doivent jamais être exposés dans les réponses ou les logs.

## 11. Backend - configuration

### 11.1 Objectifs

Le module configuration doit centraliser les paramètres applicatifs et fournir
des mécanismes d'import/export contrôlés.

### 11.2 Étapes recommandées

| Étape | Description | Validation |
| --- | --- | --- |
| Paramètres | Identifier les paramètres gérés | Typage et validation clairs |
| Lecture | Permettre la consultation autorisée | Droits respectés |
| Modification | Encadrer les changements sensibles | Audit actif |
| Export | Produire un export exploitable | Secrets exclus ou masqués |
| Import | Appliquer une configuration | Non destructif autant que possible |
| Idempotence | Réexécuter un import identique | Pas d'effet indésirable |

### 11.3 Contraintes

- Les imports doivent être aussi non destructifs et idempotents que possible.
- Les actions sensibles doivent être réservées aux rôles autorisés.
- Les exports ne doivent pas exposer de secrets.
- Les erreurs d'import doivent être explicites.

## 12. Backend - sites web

### 12.1 Objectifs

Le module sites web est le pivot des données métier.

Il doit permettre :

- la création d'un site ;
- la consultation ;
- la modification ;
- la désactivation éventuelle ;
- la gestion du statut ;
- la gestion du type de site ;
- la validation de l'URL principale ;
- les rattachements futurs aux données SEO/GEO.

### 12.2 Ordre recommandé

| Ordre | Travail | Raison |
| --- | --- | --- |
| 1 | Définir les champs essentiels | Éviter une table trop large |
| 2 | Ajouter les contraintes d'unicité | Prévenir les doublons |
| 3 | Implémenter service et repository | Respecter l'architecture |
| 4 | Exposer les routes | Donner accès au Desktop et futur React |
| 5 | Ajouter tests | Sécuriser les comportements |
| 6 | Documenter les règles utiles | Faciliter les prochains modules |

### 12.3 Limites initiales

- Ne pas intégrer immédiatement toutes les métriques SEO.
- Ne pas mélanger sites et concurrents dans une seule entité si les usages
  diffèrent.
- Ne pas rendre obligatoire une intégration externe dès le premier lot.

## 13. Backend - mots-clés

### 13.1 Objectifs

Le module mots-clés doit structurer les requêtes suivies par site.

### 13.2 Périmètre recommandé

- création ;
- consultation ;
- modification ;
- suppression contrôlée ;
- catégorisation ;
- intention de recherche ;
- URL cible ;
- association à un site ;
- filtres ;
- export ;
- préparation du suivi de performance.

### 13.3 Validations attendues

| Validation | Attendu |
| --- | --- |
| Association site | Un mot-clé doit être rattaché à un site lorsque requis |
| Unicité | Les doublons significatifs sont contrôlés |
| Suppression | Les suppressions ne cassent pas les historiques |
| Filtres | Les listes sont filtrables par site, statut, catégorie ou intention |
| Export | Les exports respectent les droits |

### 13.4 Risques

- Définir trop tôt des métriques complexes.
- Autoriser une suppression qui rend les mesures futures incohérentes.
- Mélanger mots-clés SEO et prompts GEO sans distinction claire.

## 14. Backend - contenus

### 14.1 Objectifs

Le module contenus doit soutenir la production éditoriale et son exploitation
SEO/GEO.

### 14.2 Périmètre recommandé

- types de contenus ;
- briefs ;
- statuts éditoriaux ;
- rattachement à un site ;
- rattachement à des mots-clés ;
- auteur ou rédacteur ;
- suivi éditorial initial ;
- historisation minimale ;
- exploitation SEO/GEO future.

### 14.3 Limites initiales

- Ne pas construire un CMS complet.
- Ne pas gérer la publication automatique sans validation métier.
- Ne pas complexifier les workflows éditoriaux au-delà des statuts nécessaires.

### 14.4 Exemple conceptuel

Un contenu peut être rattaché à un site, à plusieurs mots-clés et à un statut
éditorial. Ce rattachement permet ensuite d'analyser si les contenus produits
contribuent aux performances SEO ou à la visibilité GEO.

## 15. Backend - concurrents

### 15.1 Objectifs

Le module concurrents doit permettre la veille comparative.

### 15.2 Périmètre recommandé

- création d'un concurrent ;
- domaine principal ;
- rattachement à un ou plusieurs sites ;
- statut actif ou inactif ;
- préparation des comparaisons SEO ;
- préparation des comparaisons GEO.

### 15.3 Validations attendues

| Validation | Attendu |
| --- | --- |
| Rattachement | Un concurrent peut être lié aux sites pertinents |
| Statut | Les concurrents inactifs restent historisables |
| Comparaison | Les données futures SEO/GEO peuvent les référencer |
| Droits | Les actions de modification sont contrôlées |

### 15.4 Exemple conceptuel

Un site interne peut suivre plusieurs concurrents directs. Les mêmes concurrents
peuvent ensuite être utilisés pour comparer la présence dans les résultats SEO
et dans les réponses des IA génératives.

## 16. Backend - SEO

### 16.1 Objectifs

Le module SEO doit fournir une vision structurée des performances organiques.

### 16.2 Périmètre initial recommandé

- métriques ;
- périodes ;
- pages ;
- requêtes ;
- historiques ;
- consultation par site ;
- filtres ;
- exports ;
- imports éventuels de données externes après validation.

### 16.3 Approche recommandée

| Étape | Description |
| --- | --- |
| Définition | Clarifier les indicateurs initiaux |
| Stockage | Prévoir l'historique temporel |
| Consultation | Permettre les vues par site et période |
| Filtrage | Ajouter les filtres essentiels |
| Export | Encadrer les sorties |
| Tests | Vérifier agrégations et permissions |

### 16.4 Limites initiales

- Ne pas intégrer immédiatement tous les outils externes.
- Ne pas automatiser des imports tant que les formats ne sont pas validés.
- Ne pas confondre métriques SEO et métriques GEO.

## 17. Backend - GEO

### 17.1 Objectifs

Le module GEO doit mesurer la visibilité des sites, marques ou concurrents dans
les réponses des IA génératives.

### 17.2 Plateformes initiales

- ChatGPT ;
- Gemini ;
- Claude ;
- Copilot ;
- Perplexity.

### 17.3 Périmètre recommandé

- plateformes IA ;
- requêtes GEO ;
- prompts ;
- réponses observées ;
- mentions ;
- citations ;
- visibilité ;
- historique ;
- comparaison par plateforme ;
- comparaison avec concurrents.

### 17.4 Validations attendues

| Validation | Attendu |
| --- | --- |
| Plateforme | Chaque résultat est associé à une plateforme IA |
| Requête | La requête ou le prompt est historisé |
| Réponse | La réponse observée est conservée selon les règles prévues |
| Mention | Les mentions de site, marque ou concurrent sont identifiables |
| Historique | Les résultats sont comparables dans le temps |
| Droits | Les consultations et exports respectent les permissions |

### 17.5 Exemple conceptuel

Une requête GEO peut être exécutée ou enregistrée pour plusieurs plateformes IA.
Les réponses observées permettent ensuite de comparer si le site interne, la
marque ou un concurrent est mentionné, cité ou absent.

### 17.6 Limites initiales

- Ne pas lancer de scraping massif non contrôlé.
- Ne pas promettre une mesure parfaitement stable sur des réponses IA variables.
- Ne pas ajouter de plateforme sans modèle de configuration extensible.

## 18. Backend - rapports

### 18.1 Objectifs

Le module rapports doit consolider les données utiles pour les utilisateurs
internes.

### 18.2 Périmètre recommandé

- rapports par site ;
- période ;
- modules inclus ;
- statut ;
- consultation ;
- export ;
- future automatisation possible.

### 18.3 Ordre recommandé

| Ordre | Travail | Validation |
| --- | --- | --- |
| 1 | Définir les types de rapports initiaux | Périmètre lisible |
| 2 | Sélectionner les sources de données | Données disponibles |
| 3 | Gérer les filtres | Site, période, module |
| 4 | Produire un résultat consultable | Format cohérent |
| 5 | Ajouter export contrôlé | Droits respectés |
| 6 | Tester | Agrégations et erreurs validées |

### 18.4 Limites initiales

- L'automatisation planifiée est future.
- Les exports doivent rester maîtrisés.
- Les rapports ne doivent pas compenser des données sources incohérentes.

## 19. Backend - logs et audit

### 19.1 Objectifs

Les logs et l'audit doivent aider au diagnostic technique et au suivi des actions
sensibles.

### 19.2 Distinction attendue

| Type | Usage | Exemples |
| --- | --- | --- |
| Logs techniques | Diagnostic et exploitation | Erreurs API, exceptions, latence |
| Audit métier | Traçabilité des actions sensibles | Modification utilisateur, import config, export |

### 19.3 Périmètre recommandé

- journalisation des erreurs API ;
- journalisation des erreurs Desktop remontées si prévu ;
- audit des actions sensibles ;
- consultation filtrée ;
- conservation adaptée ;
- absence de secrets dans les traces.

### 19.4 Points de vigilance

- Les logs ne doivent pas exposer de mots de passe, tokens ou clés API.
- Les audits doivent être exploitables par l'administration.
- La conservation doit rester compatible avec les besoins internes.

## 20. Application Desktop PySide6

### 20.1 Rôle du Desktop

L'application Desktop est l'interface interne immédiate pour consulter et piloter
les modules prioritaires.

Elle doit rester un client de l'API FastAPI.

### 20.2 Contraintes obligatoires

- Communication HTTP REST uniquement.
- Utilisation de `httpx` ou du client HTTP existant.
- Aucun accès direct à PostgreSQL.
- Aucun contournement des endpoints FastAPI.
- Gestion des erreurs API.
- Respect des états de chargement, vide et erreur.

### 20.3 Écrans prioritaires

| Écran | Rôle | Dépendance |
| --- | --- | --- |
| Authentification | Accéder à l'application | API auth |
| Administration | Gérer les accès si autorisé | API admin |
| Configuration | Consulter ou modifier les paramètres | API configuration |
| Sites | Gérer les sites suivis | API sites |
| Mots-clés | Consulter et filtrer les mots-clés | API mots-clés |
| SEO | Consulter les performances SEO | API SEO |
| GEO | Consulter les résultats GEO | API GEO |
| Rapports | Consulter ou exporter des rapports | API rapports |

### 20.4 Validations Desktop

| Validation | Attendu |
| --- | --- |
| Appels API | Les écrans passent par HTTP REST |
| Erreurs | Les erreurs API sont affichées clairement |
| Chargement | Les actions longues ont un état visible |
| Vide | Les listes sans résultat sont compréhensibles |
| Droits | Les actions non autorisées ne sont pas proposées ou sont refusées proprement |
| Cohérence | Les libellés restent alignés avec la documentation |

## 21. Futur frontend React

### 21.1 Objectif

La roadmap doit préparer le futur frontend React sans imposer son développement
immédiat.

### 21.2 Préparations attendues côté API

- contrats JSON cohérents ;
- pagination ;
- filtres ;
- tri lorsque pertinent ;
- erreurs standardisées ;
- authentification réutilisable ;
- statuts HTTP cohérents ;
- séparation backend/frontend stricte.

### 21.3 Points à éviter

- Développer un frontend React complet avant stabilisation de l'API.
- Introduire des endpoints spécifiques au Desktop empêchant la réutilisation.
- Dupliquer la logique métier côté client.

### 21.4 Exemple conceptuel

Une liste paginée de sites exposée par l'API doit pouvoir être consommée par le
Desktop PySide6 aujourd'hui et par une table React demain, sans changement de
logique métier.

## 22. Données et migrations

### 22.1 Principes

Les évolutions de données doivent être prudentes, explicites et réversibles
lorsque cela est raisonnable.

### 22.2 Ordre recommandé des migrations

| Ordre | Famille | Justification |
| --- | --- | --- |
| 1 | Utilisateurs, rôles, permissions | Sécurité et administration |
| 2 | Configuration | Paramètres nécessaires aux modules |
| 3 | Sites | Entité pivot |
| 4 | Mots-clés | Dépend des sites |
| 5 | Contenus | Dépend des sites et mots-clés |
| 6 | Concurrents | Dépend des sites |
| 7 | SEO | Dépend des sites, mots-clés, périodes |
| 8 | GEO | Dépend des sites, concurrents, plateformes |
| 9 | Rapports | Dépend des données sources |
| 10 | Logs et audit | Transverse |

### 22.3 Contraintes Alembic

- Les migrations Alembic doivent être explicites.
- Ne pas utiliser `Base.metadata.create_all()` dans les migrations.
- Ne pas utiliser `Base.metadata.drop_all()` dans les migrations.
- Les contraintes doivent être nommées lorsque cela aide la maintenance.
- Les index doivent répondre à des usages de filtrage ou d'unicité identifiés.
- Les migrations doivent éviter les changements destructifs non validés.

### 22.4 Prudence sur les relations

Les relations doivent permettre :

- l'historisation ;
- la suppression contrôlée ;
- les statuts actifs/inactifs ;
- les rattachements multiples lorsque le métier le nécessite ;
- l'évolution des plateformes IA.

## 23. Tests et qualité

### 23.1 Outils

| Outil | Usage |
| --- | --- |
| Pytest | Tests unitaires et intégration backend |
| Ruff | Linting Python |
| Alembic | Migrations explicites |
| Vérifications Git | Contrôle du diff et des espaces |
| Vérifications Desktop | Contrôles fonctionnels manuels ou tests disponibles |

### 23.2 Tests backend attendus

- tests routes ;
- tests services ;
- tests repositories ;
- tests permissions ;
- tests validation Pydantic ;
- tests erreurs ;
- tests pagination et filtres ;
- tests imports/exports ;
- tests migrations lorsque pertinent.

### 23.3 Tests Desktop attendus

- affichage des écrans prioritaires ;
- appels API corrects ;
- gestion des erreurs ;
- états loading/empty/error ;
- absence d'accès direct à PostgreSQL.

### 23.4 Vérifications documentaires

Pour les lots documentaires :

- vérifier les chemins ;
- vérifier la cohérence des termes ;
- éviter les doublons excessifs ;
- vérifier l'absence de contradiction avec les documents existants ;
- exécuter les vérifications Git demandées.

## 24. Documentation continue

### 24.1 Documents à maintenir

| Type | Emplacement attendu | Moment de mise à jour |
| --- | --- | --- |
| Spécifications | `docs/specifications/` | Lors de cadrages structurants |
| Architecture | `docs/architecture/` | Lors de décisions techniques |
| API | `docs/api/` | Lors d'ajouts ou changements API |
| Design | `docs/design/` ou documentation UI | Lors de changements d'interface |
| Notes de sprint | À définir selon gouvernance | Lors des livraisons significatives |

### 24.2 Règles

- Documenter les changements importants dans le même sprint.
- Ne pas créer de documentation contradictoire.
- Ne pas transformer les documents d'architecture en backlog.
- Garder les spécifications alignées avec l'état réel du projet.

## 25. Critères de fin de sprint

Chaque sprint doit vérifier les points suivants avant d'être considéré terminé.

- Périmètre du sprint respecté.
- Aucun changement hors périmètre non expliqué.
- Architecture `Routes -> Services -> Repositories -> Models` respectée.
- Routes FastAPI sans logique métier.
- Services testables.
- Repositories limités à l'accès SQLAlchemy.
- Schémas Pydantic cohérents.
- Migrations Alembic explicites si applicables.
- Aucun `Base.metadata.create_all()` dans les migrations.
- Aucun `Base.metadata.drop_all()` dans les migrations.
- Desktop sans accès direct à PostgreSQL si Desktop concerné.
- Tests Pytest exécutés lorsque du code backend change.
- Ruff exécuté lorsque du code Python change.
- Erreurs API vérifiées lorsque des endpoints changent.
- Permissions vérifiées lorsque des endpoints sensibles changent.
- Imports/exports non destructifs autant que possible.
- Documentation mise à jour si nécessaire.
- Aucun secret ajouté.
- `git status` vérifié.
- `git diff --stat` vérifié.
- `git diff --check` vérifié.
- Pull Request claire et limitée.

## 26. Critères de merge

Une branche ne doit être mergée que si les critères suivants sont respectés.

- Branche dédiée au sprint ou au lot.
- Aucune modification directe sur `main`.
- Pas de modification parasite.
- Pas de fichier supprimé ou renommé sans décision explicite.
- Tests exécutés selon le périmètre.
- Ruff OK si code Python modifié.
- `git diff --check` OK.
- Migrations contrôlées si applicables.
- Documentation cohérente.
- Secrets absents du diff.
- Pull Request relue.
- `main` protégée.
- Merge effectué uniquement lorsque la branche est propre.
- Après merge, retour sur `main`, pull, puis suppression de branche si elle
  n'est plus utile.

## 27. Matrice de priorisation

| Module | Priorité | Valeur métier | Risque | Dépendances | Recommandation |
| --- | --- | --- | --- | --- | --- |
| Documentation | Critique | Élevée | Faible | Aucune | Finaliser avant nouveaux gros chantiers |
| Fondations backend | Critique | Élevée | Moyen | Architecture existante | Stabiliser avant modules métiers |
| Auth/Admin | Critique | Élevée | Élevé | Backend | Préserver le Sprint 06 terminé |
| Configuration | Critique | Élevée | Moyen | Auth/Admin | Traiter avant imports/exports avancés |
| Sites | Critique | Élevée | Moyen | Backend, permissions | Développer tôt |
| Mots-clés | Importante | Élevée | Moyen | Sites | Développer après sites |
| Contenus | Importante | Moyenne | Moyen | Sites, mots-clés | Garder un périmètre simple |
| Concurrents | Importante | Moyenne | Moyen | Sites | Préparer SEO/GEO comparatif |
| SEO | Importante | Élevée | Élevé | Sites, mots-clés | Commencer par indicateurs initiaux |
| GEO | Importante | Élevée | Élevé | Sites, concurrents, config | Développer par itérations |
| Rapports | Importante | Élevée | Moyen | SEO/GEO | Livrer génération simple d'abord |
| Logs/Audit | Importante | Moyenne | Moyen | Auth, modules sensibles | Renforcer après premiers modules |
| Desktop | Importante | Élevée | Moyen | API stable | Brancher progressivement |
| React futur | Secondaire | Moyenne | Moyen | API stable | Préparer sans développer tout de suite |

## 28. Matrice des risques roadmap

| Risque | Probabilité | Impact | Mitigation | Phase concernée |
| --- | --- | --- | --- | --- |
| Dispersion fonctionnelle | Moyenne | Élevé | Limiter chaque sprint à un objectif | Toutes |
| Régression administration | Moyenne | Élevé | Tests de droits et revue ciblée | Phase 2 |
| Modèle de données trop rigide | Moyenne | Élevé | Suivre la spécification base de données | Phases 3 à 7 |
| Imports destructifs | Faible à moyenne | Élevé | Idempotence et validations | Phase 2 |
| Volumétrie SEO | Moyenne | Moyen à élevé | Pagination, index, filtres | Phase 5 |
| Variabilité GEO | Élevée | Moyen | Historiser et documenter les limites | Phase 6 |
| Secrets dans logs | Faible | Élevé | Masquage et revue sécurité | Phase 9 |
| Couplage Desktop/backend | Moyenne | Moyen | API REST stable et client HTTP | Phase 8 |
| Anticipation React excessive | Moyenne | Moyen | Préparer contrats sans construire l'UI complète | Phase 10 |
| Documentation obsolète | Moyenne | Moyen | Documentation continue par sprint | Toutes |

## 29. Matrice de validation par lot

| Lot | Validation fonctionnelle | Validation technique | Validation documentaire | Validation Git |
| --- | --- | --- | --- | --- |
| Documentation | Cohérence métier | Chemins et Markdown propres | Spécifications alignées | Status, stat, check |
| Fondations backend | Comportements API de base | Pytest, Ruff, architecture | Architecture à jour | Diff limité |
| Auth/Admin | Droits conformes | Tests permissions | API admin documentée | PR dédiée |
| Configuration | Import/export contrôlé | Tests idempotence | Règles config documentées | Diff vérifié |
| Sites | CRUD et filtres | Tests routes/services/repos | Règles sites si nécessaires | Migration contrôlée |
| Mots-clés | Association et filtres | Tests validation | Règles mots-clés | Diff propre |
| Contenus | Statuts et rattachements | Tests services | Statuts éditoriaux | Diff propre |
| Concurrents | Rattachements sites | Tests relations | Règles concurrentielles | Diff propre |
| SEO | Consultation indicateurs | Tests agrégations | Indicateurs décrits | Diff contrôlé |
| GEO | Résultats par plateforme | Tests historiques | Limites GEO décrites | Diff contrôlé |
| Rapports | Génération et export | Tests droits et formats | Règles reporting | Diff contrôlé |
| Logs/Audit | Actions sensibles tracées | Tests audit | Règles logs | Diff contrôlé |
| Desktop | Écrans utilisables | Vérifications HTTP REST | Documentation Desktop | Diff limité |
| React futur | Contrats réutilisables | Tests API | Conventions API | Diff limité |

## 30. Jalons recommandés

### 30.1 Jalon 1 : socle documentaire validé

Le dossier `docs/specifications/` contient les documents structurants et
cohérents.

Critère principal : la suite du projet peut être pilotée sans ambiguïté majeure.

### 30.2 Jalon 2 : backend stable

Le backend respecte l'architecture obligatoire et fournit des conventions
stables.

Critère principal : les prochains modules peuvent être ajoutés sans refactor
global.

### 30.3 Jalon 3 : administration stable

Les utilisateurs, rôles, permissions et endpoints admin sont protégés.

Critère principal : les actions sensibles sont réservées aux profils autorisés.

### 30.4 Jalon 4 : configuration stable

Les paramètres applicatifs sont gérés de manière contrôlée.

Critère principal : import/export non destructifs autant que possible.

### 30.5 Jalon 5 : sites et mots-clés opérationnels

Les sites et mots-clés peuvent être gérés, filtrés et rattachés.

Critère principal : les modules SEO/GEO disposent de leurs référentiels.

### 30.6 Jalon 6 : SEO initial

Les indicateurs SEO initiaux sont consultables par site et période.

Critère principal : les utilisateurs peuvent suivre une évolution SEO de base.

### 30.7 Jalon 7 : GEO initial

Les résultats GEO initiaux sont historisés par plateforme IA.

Critère principal : les utilisateurs peuvent comparer la visibilité dans les IA
génératives.

### 30.8 Jalon 8 : rapports initiaux

Les données prioritaires peuvent être consolidées en rapports.

Critère principal : un rapport par site et période est consultable et exportable.

### 30.9 Jalon 9 : Desktop exploitable

Le Desktop permet d'utiliser les modules prioritaires via l'API.

Critère principal : les utilisateurs internes peuvent travailler sans accès
direct à PostgreSQL.

### 30.10 Jalon 10 : préparation React

Les contrats API sont suffisamment cohérents pour préparer une interface React.

Critère principal : le futur frontend peut consommer les mêmes API que le
Desktop.

## 31. Workflow Git obligatoire

### 31.1 Règles

- Ne jamais développer directement sur `main`.
- Créer une branche dédiée par sprint ou par lot.
- Garder les commits courts et ciblés.
- Tester avant commit.
- Vérifier l'état Git avant Pull Request.
- Ouvrir une Pull Request vers `main`.
- Merger uniquement lorsque la branche est propre.
- Revenir sur `main` après merge.
- Pull sur `main`.
- Supprimer la branche si elle n'est plus utile.

### 31.2 Commandes de contrôle recommandées

Les contrôles suivants doivent être utilisés selon le contexte :

- `git status --short` ;
- `git diff --stat` ;
- `git diff --check` ;
- Pytest pour les modifications code ;
- Ruff pour les modifications Python.

### 31.3 Points de vigilance Git

- Ne pas indexer de fichier hors périmètre.
- Ne pas inclure de secrets.
- Ne pas mélanger documentation, backend et Desktop dans un même sprint sauf
  nécessité claire.
- Ne pas conserver une branche longue avec trop de sujets.

## 32. Hors périmètre de la roadmap immédiate

Les éléments suivants ne font pas partie de la roadmap immédiate :

- frontend React complet immédiat ;
- automatisations destructives ;
- scraping massif non contrôlé ;
- intégrations externes avancées non validées ;
- refactor global non planifié ;
- accès direct du Desktop à PostgreSQL ;
- modifications directes de `main` ;
- génération automatique de rapports planifiés sans validation métier ;
- remplacement de l'architecture existante ;
- ajout de dépendances sans justification explicite.

## 33. Recommandation de prochaine étape après ce lot documentaire

Après validation et merge de la branche documentaire `docs-specifications`, la
suite logique est de revenir à un sprint backend ciblé.

La recommandation est :

1. partir de `main` à jour ;
2. créer une branche dédiée au prochain lot ;
3. choisir un seul module prioritaire ;
4. éviter de lancer plusieurs gros chantiers en parallèle ;
5. privilégier un lot configuration, sites ou mots-clés selon l'état réel du code ;
6. exécuter les tests et contrôles qualité avant Pull Request ;
7. mettre à jour la documentation utile dans le même sprint.

Le choix du prochain module doit tenir compte de l'état existant du dépôt. Si un
module est déjà partiellement implémenté, il faut l'étendre plutôt que le
réécrire.

## 34. Exemples conceptuels de découpage

### 34.1 Exemple : lot sites web

Un sprint sites web peut couvrir la gestion d'un site, son statut et son URL
principale, mais exclure les métriques SEO et GEO. Cette limite rend le sprint
plus simple à tester et évite de mélanger référentiel et analyse.

### 34.2 Exemple : lot GEO initial

Un sprint GEO initial peut enregistrer une requête, une plateforme IA et une
réponse observée. Il peut exclure l'automatisation massive des requêtes afin de
stabiliser d'abord le modèle et les règles de consultation.

### 34.3 Exemple : lot Desktop

Un sprint Desktop peut brancher l'écran sites sur l'API existante et gérer les
états loading, empty et error. Il doit exclure tout accès direct à PostgreSQL et
toute logique métier côté interface.

## 35. Synthèse finale

La roadmap recommande une progression graduelle :

- cadrer d'abord ;
- stabiliser le backend ;
- sécuriser l'administration et la configuration ;
- construire les référentiels métier ;
- ajouter progressivement SEO, GEO et rapports ;
- connecter le Desktop aux API stables ;
- renforcer logs, audit et qualité ;
- préparer React sans développer le frontend complet trop tôt.

Le projet doit avancer par lots limités, branches dédiées, tests adaptés et
Pull Requests relues.

La stabilité de `main`, la séparation des responsabilités et la cohérence
documentaire sont les garanties principales pour éviter la dispersion
fonctionnelle.

Cette roadmap est un document vivant. Elle doit être révisée lorsque les modules
progressent, lorsque les priorités métier changent ou lorsque de nouvelles
contraintes techniques sont validées.
