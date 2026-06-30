# Software Requirements Specification

## 1. Informations générales

| Élément | Description |
|---|---|
| Projet | Veille SEO-GEO Groupe A.P&Partner |
| Document | Spécification des exigences logicielles |
| Statut | Référence fonctionnelle détaillée |
| Périmètre | Backend FastAPI, API REST, application Desktop PySide6, préparation React, modules métier |
| Public cible | Responsable projet, développeurs backend, développeurs Desktop, futur intervenant React, responsables SEO/GEO |
| Niveau de détail | Exigences logicielles, comportements attendus, règles métier et critères d'acceptation |
| Document source | `docs/specifications/CAHIER_DES_CHARGES.md` |

Ce document traduit le cahier des charges fonctionnel et métier en exigences logicielles
exploitables pour le développement.

Il définit :

- les exigences fonctionnelles ;
- les exigences non fonctionnelles ;
- les acteurs et rôles ;
- les permissions attendues ;
- les règles métier ;
- les comportements API, Desktop et futurs comportements React ;
- les cas d'usage principaux ;
- les critères d'acceptation globaux.

Il ne définit pas :

- le modèle complet de base de données ;
- les endpoints API un par un ;
- une roadmap sprint par sprint ;
- un guide détaillé d'interface ;
- les migrations Alembic détaillées ;
- les connecteurs externes avancés non validés.

Les détails de conception base de données seront traités dans
`docs/specifications/DATABASE_DESIGN_SPECIFICATION.md`.

La planification détaillée sera traitée dans
`docs/specifications/DEVELOPMENT_ROADMAP.md`.

## 2. Vue d'ensemble du système

### 2.1 Objectif logiciel

L'application **Veille SEO-GEO Groupe A.P&Partner** doit fournir une plateforme interne
permettant de centraliser, suivre et exploiter les données liées :

- aux sites web du groupe ;
- aux mots-clés ;
- aux contenus ;
- aux concurrents ;
- aux performances SEO ;
- aux performances GEO ;
- aux rapports ;
- à la configuration ;
- à l'administration ;
- aux logs et audits ;
- aux plateformes d'IA générative comme ChatGPT, Gemini, Claude, Copilot et Perplexity.

Le logiciel doit permettre de passer d'un suivi dispersé à un système commun, traçable,
modulaire et exploitable par les équipes internes.

### 2.2 Architecture générale

L'architecture logicielle suit une séparation stricte des responsabilités.

```text
Desktop PySide6 / Futur React
        |
        | HTTP REST / JSON
        v
FastAPI Routes
        |
        v
Services métier
        |
        v
Repositories SQLAlchemy
        |
        v
Models SQLAlchemy
        |
        v
PostgreSQL
```

### 2.3 Stack actuelle

| Couche | Technologie |
|---|---|
| Backend | Python 3.13 |
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Base de données | PostgreSQL |
| Validation | Pydantic v2 |
| Tests | Pytest |
| Linting | Ruff |
| Desktop | PySide6 + httpx |
| Frontend futur | React |

### 2.4 Séparation backend, API, Desktop et React

| Partie | Responsabilité | Limite |
|---|---|---|
| Backend | Logique métier, persistance, sécurité, orchestration | Ne dépend pas du Desktop |
| API FastAPI | Exposition REST, validation, réponses HTTP | Ne contient pas de logique métier |
| Services | Règles métier, validations fonctionnelles, orchestration | Ne gèrent pas le rendu UI |
| Repositories | Accès SQLAlchemy aux données | Ne contiennent pas de logique métier |
| Models | Représentation des tables | Ne remplacent pas les schémas API |
| Schemas Pydantic | Contrats d'entrée et de sortie API | Ne gèrent pas la persistance |
| Desktop PySide6 | Interface interne actuelle | Aucun accès direct PostgreSQL |
| Futur React | Interface web future | Aucun contournement de l'API |

### 2.5 Contraintes structurantes

Les règles suivantes sont obligatoires :

- les routes FastAPI ne doivent pas contenir de logique métier ;
- les routes appellent les services ;
- les services contiennent la logique métier ;
- les repositories contiennent uniquement l'accès aux données SQLAlchemy ;
- les modèles SQLAlchemy représentent les tables ;
- les schémas Pydantic gèrent les entrées et sorties API ;
- le Desktop communique uniquement avec FastAPI via HTTP REST ;
- le Desktop ne doit jamais accéder directement à PostgreSQL ;
- les migrations Alembic doivent être explicites ;
- `Base.metadata.create_all()` ne doit pas être utilisé dans les migrations ;
- `Base.metadata.drop_all()` ne doit pas être utilisé dans les migrations ;
- les endpoints sensibles doivent être protégés par authentification et droits adaptés ;
- les imports et exports de configuration doivent être aussi non destructifs et idempotents que possible.

## 3. Définitions et terminologie

| Terme | Définition |
|---|---|
| SEO | Search Engine Optimization, suivi de visibilité dans les moteurs de recherche classiques |
| GEO | Generative Engine Optimization, suivi de visibilité dans les réponses d'IA générative |
| IA générative | Système produisant des réponses textuelles ou synthétiques à partir de requêtes utilisateur |
| Site web | Site ou domaine interne suivi par la plateforme |
| Mot-clé | Requête ou expression suivie pour l'analyse SEO ou GEO |
| Contenu | Page, sujet, brief ou élément éditorial suivi dans la plateforme |
| Concurrent | Acteur, marque ou domaine comparé aux sites du groupe |
| Rapport | Synthèse structurée des données et analyses sur une période ou un périmètre |
| Configuration | Paramètres fonctionnels ou techniques administrables |
| Rôle | Profil d'accès attribué à un utilisateur |
| Permission | Droit d'effectuer une action sur un module ou une ressource |
| Audit | Trace durable d'une action sensible ou métier importante |
| Journalisation | Enregistrement d'événements techniques ou applicatifs |
| Import | Entrée de données ou configuration depuis un fichier ou une source externe |
| Export | Sortie contrôlée de données ou configuration |
| Soft delete | Désactivation ou archivage contrôlé sans suppression physique immédiate |

## 4. Acteurs et rôles utilisateurs

### 4.1 Administrateur

| Élément | Description |
|---|---|
| Description | Utilisateur responsable de la configuration, des accès et de la supervision |
| Droits attendus | Administration, configuration, consultation des logs, gestion des rôles |
| Limites | Ne doit pas voir les secrets en clair si un affichage masqué suffit |
| Modules accessibles | Tous les modules, selon permissions effectives |

L'administrateur est un rôle sensible. Ses actions doivent être protégées, tracées et limitées
par le principe du moindre privilège lorsque des permissions plus fines existent.

### 4.2 Responsable SEO/GEO

| Élément | Description |
|---|---|
| Description | Utilisateur chargé du pilotage SEO et GEO |
| Droits attendus | Consultation, création et modification sur sites, mots-clés, contenus, concurrents, SEO, GEO, rapports |
| Limites | Pas d'administration système par défaut |
| Modules accessibles | Sites, mots-clés, contenus, concurrents, SEO, GEO, rapports |

Ce rôle pilote les analyses et priorités. Il peut préparer des exports métier si les droits
sont accordés.

### 4.3 Rédacteur

| Élément | Description |
|---|---|
| Description | Utilisateur chargé du suivi éditorial et des contenus |
| Droits attendus | Consultation et modification ciblée des contenus, consultation des mots-clés et recommandations |
| Limites | Pas de configuration, pas d'administration, pas de suppression sensible |
| Modules accessibles | Contenus, mots-clés, sites en consultation, SEO/GEO en consultation ciblée |

Le rédacteur intervient sur la production et l'optimisation éditoriale. Il ne décide pas des
paramètres techniques globaux.

### 4.4 Analyste

| Élément | Description |
|---|---|
| Description | Utilisateur chargé de l'analyse, de la comparaison et du reporting |
| Droits attendus | Consultation étendue, filtres, exports autorisés, création de rapports selon droits |
| Limites | Modification limitée, pas d'administration par défaut |
| Modules accessibles | Sites, mots-clés, contenus, concurrents, SEO, GEO, rapports, logs en lecture limitée si autorisé |

L'analyste doit pouvoir comparer, filtrer et produire des synthèses sans altérer les référentiels
sensibles.

### 4.5 Lecteur ou consultation

| Élément | Description |
|---|---|
| Description | Utilisateur lisant les tableaux de bord et rapports |
| Droits attendus | Lecture seule |
| Limites | Aucune création, modification, suppression ou administration |
| Modules accessibles | Dashboard, rapports, vues de consultation explicitement autorisées |

Ce rôle doit être adapté aux usages de consultation interne ou de direction.

### 4.6 Rôle système ou API

| Élément | Description |
|---|---|
| Description | Identité technique future pour intégrations contrôlées |
| Droits attendus | Accès strictement limité à un périmètre machine validé |
| Limites | Pas d'accès interactif, pas de droits humains implicites |
| Modules accessibles | Selon jeton, permission et usage validé |

Ce rôle est futur et doit être utilisé uniquement pour des automatisations maîtrisées.

## 5. Matrice synthétique des permissions

Légende :

- `Oui` : permission attendue par défaut.
- `Limité` : permission possible selon périmètre ou validation.
- `Non` : permission non attendue par défaut.
- `Future` : à préciser lors de l'activation du rôle ou module.

| Module | Rôle | Consultation | Création | Modification | Suppression | Export | Administration |
|---|---|---:|---:|---:|---:|---:|---:|
| Sites | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Sites | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| Sites | Rédacteur | Oui | Non | Non | Non | Non | Non |
| Sites | Analyste | Oui | Non | Non | Non | Oui | Non |
| Sites | Lecteur | Oui | Non | Non | Non | Non | Non |
| Mots-clés | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Mots-clés | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| Mots-clés | Rédacteur | Oui | Limité | Limité | Non | Non | Non |
| Mots-clés | Analyste | Oui | Non | Non | Non | Oui | Non |
| Mots-clés | Lecteur | Oui | Non | Non | Non | Non | Non |
| Contenus | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Contenus | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| Contenus | Rédacteur | Oui | Oui | Oui | Non | Non | Non |
| Contenus | Analyste | Oui | Non | Non | Non | Oui | Non |
| Contenus | Lecteur | Oui | Non | Non | Non | Non | Non |
| Concurrents | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Concurrents | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| Concurrents | Rédacteur | Oui | Non | Non | Non | Non | Non |
| Concurrents | Analyste | Oui | Non | Non | Non | Oui | Non |
| Concurrents | Lecteur | Oui | Non | Non | Non | Non | Non |
| SEO | Administrateur | Oui | Limité | Limité | Non | Oui | Oui |
| SEO | Responsable SEO/GEO | Oui | Limité | Limité | Non | Oui | Non |
| SEO | Rédacteur | Oui | Non | Non | Non | Non | Non |
| SEO | Analyste | Oui | Non | Non | Non | Oui | Non |
| SEO | Lecteur | Oui | Non | Non | Non | Non | Non |
| GEO | Administrateur | Oui | Limité | Limité | Non | Oui | Oui |
| GEO | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| GEO | Rédacteur | Oui | Non | Non | Non | Non | Non |
| GEO | Analyste | Oui | Non | Non | Non | Oui | Non |
| GEO | Lecteur | Oui | Non | Non | Non | Non | Non |
| Rapports | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Rapports | Responsable SEO/GEO | Oui | Oui | Oui | Limité | Oui | Non |
| Rapports | Rédacteur | Oui | Non | Non | Non | Non | Non |
| Rapports | Analyste | Oui | Oui | Limité | Non | Oui | Non |
| Rapports | Lecteur | Oui | Non | Non | Non | Non | Non |
| Configuration | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Configuration | Responsable SEO/GEO | Oui | Non | Limité | Non | Limité | Non |
| Configuration | Rédacteur | Non | Non | Non | Non | Non | Non |
| Configuration | Analyste | Limité | Non | Non | Non | Non | Non |
| Configuration | Lecteur | Non | Non | Non | Non | Non | Non |
| Administration | Administrateur | Oui | Oui | Oui | Limité | Oui | Oui |
| Administration | Autres rôles | Non | Non | Non | Non | Non | Non |
| Logs/Audit | Administrateur | Oui | Non | Non | Non | Limité | Oui |
| Logs/Audit | Analyste | Limité | Non | Non | Non | Non | Non |
| Logs/Audit | Autres rôles | Non | Non | Non | Non | Non | Non |

## 6. Exigences fonctionnelles globales

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-GEN-001 | Le système doit centraliser les référentiels principaux | Critique | Responsable SEO/GEO | Les modules doivent partager des identifiants cohérents | Les sites, mots-clés, contenus et concurrents sont consultables depuis un même système |
| FR-GEN-002 | Le système doit distinguer les modules métier | Critique | Tous | Chaque module a un périmètre clair | Une donnée SEO n'est pas stockée comme donnée GEO sans justification |
| FR-GEN-003 | Le système doit gérer des statuts actifs/inactifs lorsque pertinent | Importante | Responsable SEO/GEO | La désactivation est préférée à la suppression destructrice | Un élément désactivé reste identifiable et filtrable |
| FR-GEN-004 | Le système doit fournir des listes filtrables et paginées | Critique | Analyste | Les listes volumineuses ne sont pas chargées sans limite | Une liste expose pagination, total et filtres pertinents |
| FR-GEN-005 | Le système doit préserver la compatibilité Desktop/API | Critique | Développeur Desktop | Les réponses utilisées par le Desktop ne changent pas silencieusement | Le Desktop distingue données, vide, erreur et refus d'accès |
| FR-GEN-006 | Le système doit préparer le futur frontend React | Importante | Développeur frontend | Le backend reste indépendant de la surface UI | Les contrats REST peuvent être réutilisés par un client web |
| FR-GEN-007 | Le système doit tracer les actions sensibles | Critique | Administrateur | Toute action admin sensible doit être auditée si le module le permet | Une action de configuration produit une trace exploitable |
| FR-GEN-008 | Le système doit éviter les imports destructifs | Critique | Administrateur | Un import ne supprime pas sans validation explicite | Un réimport contrôlé ne duplique pas ni n'écrase hors périmètre |

## 7. Module Sites web

### 7.1 Objectif

Le module Sites web gère le référentiel des sites suivis par la plateforme. Il constitue le
point de rattachement principal des analyses SEO, GEO, mots-clés, contenus, concurrents et
rapports.

### 7.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-SITE-001 | Créer un site web avec nom et URL principale | Critique | Responsable SEO/GEO | L'URL principale doit être valide | Le site créé apparaît dans la liste Desktop/API |
| FR-SITE-002 | Empêcher les doublons d'URL principale | Critique | Responsable SEO/GEO | Une même URL principale active ne peut pas être créée deux fois | Une tentative de doublon retourne une erreur de conflit |
| FR-SITE-003 | Modifier les informations d'un site | Importante | Responsable SEO/GEO | Les champs critiques sont validés par le service | La modification est visible après rechargement |
| FR-SITE-004 | Consulter la liste des sites | Critique | Tous les rôles autorisés | La liste est paginée et filtrable | La réponse contient items, total, page et page_size |
| FR-SITE-005 | Désactiver un site sans supprimer ses historiques | Importante | Administrateur | Une désactivation ne détruit pas les données liées | Le site passe inactif et reste consultable selon droits |
| FR-SITE-006 | Rattacher un site aux données SEO/GEO futures | Critique | Responsable SEO/GEO | Les analyses doivent pouvoir référencer un site | Les modules SEO/GEO peuvent filtrer par site |
| FR-SITE-007 | Définir un type de site si disponible | Secondaire | Responsable SEO/GEO | Le type sert au filtrage et à la comparaison | Un site peut être filtré par type lorsqu'il est renseigné |
| FR-SITE-008 | Afficher les sites dans le Desktop | Critique | Utilisateur interne | Le Desktop passe par FastAPI uniquement | Aucun accès PostgreSQL n'est nécessaire côté Desktop |

### 7.3 Comportements attendus

- Un site actif est visible dans les listes métier par défaut.
- Un site inactif peut être masqué ou affiché via filtre.
- Les champs obligatoires doivent produire des erreurs compréhensibles.
- Les URLs doivent être normalisées ou validées selon les règles du service.
- Les suppressions physiques ne doivent pas être le comportement par défaut.

### 7.4 Limites

Le module Sites web ne porte pas la logique détaillée SEO ou GEO. Il fournit un référentiel
et des rattachements.

## 8. Module Mots-clés

### 8.1 Objectif

Le module Mots-clés permet de suivre, qualifier et exploiter les requêtes importantes pour les
sites du groupe.

### 8.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-KEYWORD-001 | Créer un mot-clé | Critique | Responsable SEO/GEO | Le libellé ne doit pas être vide | Le mot-clé apparaît dans la liste du site concerné |
| FR-KEYWORD-002 | Associer un mot-clé à un site | Critique | Responsable SEO/GEO | Un mot-clé suivi doit avoir un contexte métier | Le filtre par site retourne le mot-clé associé |
| FR-KEYWORD-003 | Définir une intention de recherche | Importante | Responsable SEO/GEO | L'intention doit utiliser une valeur contrôlée | Les filtres par intention fonctionnent |
| FR-KEYWORD-004 | Renseigner une URL cible | Importante | Responsable SEO/GEO | L'URL cible doit être liée au site ou justifiée | L'URL cible est affichée dans les vues mot-clé |
| FR-KEYWORD-005 | Catégoriser un mot-clé | Importante | Responsable SEO/GEO | Les catégories aident la priorisation | Les mots-clés peuvent être filtrés par catégorie |
| FR-KEYWORD-006 | Modifier un mot-clé | Importante | Responsable SEO/GEO | La modification doit préserver l'historique futur | Les nouvelles valeurs sont visibles sans doublon |
| FR-KEYWORD-007 | Supprimer ou désactiver de façon contrôlée | Importante | Administrateur | La suppression ne doit pas casser les analyses liées | Un mot-clé supprimé ou désactivé n'apparaît plus par défaut |
| FR-KEYWORD-008 | Exporter une liste de mots-clés filtrée | Secondaire | Analyste | L'export respecte les permissions et filtres actifs | L'export ne contient que le périmètre autorisé |
| FR-KEYWORD-009 | Suivre des indicateurs de performance | Future | Responsable SEO/GEO | Les données externes doivent être importées ou connectées proprement | Les positions ou tendances sont consultables si disponibles |

### 8.3 Comportements attendus

- Les filtres doivent inclure au minimum site, statut, intention et catégorie lorsque les
  données existent.
- Les exports doivent respecter le périmètre filtré.
- Les doublons doivent être contrôlés au niveau métier.
- Les mots-clés doivent pouvoir alimenter les modules SEO, contenus, GEO et rapports.

### 8.4 Limites

Le module Mots-clés ne remplace pas immédiatement un outil externe de suivi de position.
Les intégrations de données de position sont futures ou soumises à validation.

## 9. Module Contenus

### 9.1 Objectif

Le module Contenus structure la production, l'optimisation et le suivi éditorial des pages,
briefs et sujets liés aux sites.

### 9.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-CONTENT-001 | Créer une fiche contenu | Importante | Rédacteur | Un contenu doit avoir un titre ou sujet | La fiche est visible dans le module Contenus |
| FR-CONTENT-002 | Définir un type de contenu | Importante | Rédacteur | Le type doit être contrôlé | Le contenu peut être filtré par type |
| FR-CONTENT-003 | Gérer un brief éditorial | Importante | Rédacteur | Le brief doit rester rattaché au contenu | Le brief est consultable par les rôles autorisés |
| FR-CONTENT-004 | Gérer les statuts éditoriaux | Critique | Rédacteur | Les statuts doivent être cohérents et limités | Les statuts sont filtrables et lisibles |
| FR-CONTENT-005 | Rattacher un contenu à un site | Critique | Rédacteur | Un contenu métier doit avoir un contexte site si applicable | La fiche contenu apparaît dans la vue du site |
| FR-CONTENT-006 | Rattacher un contenu à des mots-clés | Importante | Responsable SEO/GEO | Un contenu peut répondre à plusieurs intentions | Les mots-clés associés sont visibles |
| FR-CONTENT-007 | Associer un auteur ou rédacteur | Secondaire | Rédacteur | Le responsable éditorial doit être identifiable si renseigné | La fiche affiche le rédacteur |
| FR-CONTENT-008 | Historiser minimalement les changements importants | Future | Responsable SEO/GEO | Les changements de statut doivent rester traçables | L'historique est consultable lorsque disponible |
| FR-CONTENT-009 | Exploiter les signaux SEO/GEO | Future | Responsable SEO/GEO | Les recommandations doivent rester rattachées au contenu | Les vues contenu affichent les observations disponibles |

### 9.3 Comportements attendus

- Les statuts doivent être stables et compréhensibles.
- Les contenus doivent être filtrables par site, type, statut et priorité.
- Les actions éditoriales sensibles doivent être limitées par droits.
- Le module ne doit pas publier directement sur un CMS sans intégration validée.

### 9.4 Limites

Le module Contenus n'est pas un CMS. Il ne remplace pas WordPress, Prestashop ou tout autre
système de publication.

## 10. Module Concurrents

### 10.1 Objectif

Le module Concurrents permet de référencer les acteurs à surveiller et de préparer les
comparaisons SEO/GEO.

### 10.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-COMPETITOR-001 | Créer un concurrent | Importante | Responsable SEO/GEO | Le nom et le domaine doivent être validés si renseignés | Le concurrent apparaît dans la liste |
| FR-COMPETITOR-002 | Rattacher un concurrent à un ou plusieurs sites | Importante | Responsable SEO/GEO | La comparaison doit avoir un périmètre clair | Le concurrent est visible depuis les sites associés |
| FR-COMPETITOR-003 | Définir un statut actif ou inactif | Importante | Responsable SEO/GEO | Un concurrent inactif ne doit pas polluer les vues par défaut | Le filtre statut fonctionne |
| FR-COMPETITOR-004 | Préparer la comparaison SEO | Importante | Analyste | Les données SEO comparatives doivent être liées à un concurrent | Les vues SEO peuvent filtrer par concurrent si disponible |
| FR-COMPETITOR-005 | Préparer la comparaison GEO | Importante | Analyste | Les citations concurrentes doivent être distinguées | Les vues GEO affichent la présence concurrente si disponible |
| FR-COMPETITOR-006 | Ajouter des notes de veille | Secondaire | Analyste | Les notes doivent rester non sensibles | Les notes sont consultables par les rôles autorisés |

### 10.3 Comportements attendus

- Les concurrents doivent être filtrables par site, marché, statut et priorité si ces champs existent.
- Un concurrent ne doit pas être confondu avec une entité interne.
- Les comparaisons doivent indiquer leur période et leur source lorsqu'elles reposent sur des données collectées.

### 10.4 Limites

Le module ne doit pas déclencher de scraping massif non contrôlé. Toute collecte externe doit
être validée et documentée.

## 11. Module SEO

### 11.1 Objectif

Le module SEO suit la visibilité organique, les pages, les requêtes, les indicateurs et les
évolutions temporelles.

### 11.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-SEO-001 | Consulter les performances SEO d'un site | Critique | Responsable SEO/GEO | Les données doivent être filtrées par site et période | Une vue SEO affiche les indicateurs disponibles |
| FR-SEO-002 | Suivre des positions ou tendances | Importante | Responsable SEO/GEO | Les positions doivent être datées | Les variations sont lisibles par période |
| FR-SEO-003 | Analyser les pages ou URLs | Importante | Responsable SEO/GEO | Les URLs doivent être rattachées à un site | La vue page affiche le statut ou les signaux disponibles |
| FR-SEO-004 | Suivre les requêtes | Importante | Analyste | Une requête doit être liée à un mot-clé ou une source | Les requêtes sont filtrables |
| FR-SEO-005 | Afficher des indicateurs SEO | Importante | Analyste | Les indicateurs doivent être nommés et datés | Les KPI ne sont pas ambigus |
| FR-SEO-006 | Afficher l'évolution temporelle | Importante | Analyste | Toute évolution doit indiquer la période comparée | Les graphiques ou listes indiquent la période |
| FR-SEO-007 | Importer des données externes validées | Future | Administrateur | L'import doit être non destructif et traçable | Un import fournit un résultat de traitement |
| FR-SEO-008 | Filtrer les données SEO | Critique | Analyste | Les filtres doivent être appliqués côté API | Les résultats changent selon site, période, mot-clé ou statut |
| FR-SEO-009 | Exporter les données SEO autorisées | Secondaire | Analyste | L'export respecte les permissions et filtres | L'export ne contient pas de données hors périmètre |

### 11.3 Comportements attendus

- Une donnée SEO absente doit produire un état vide, pas une erreur technique.
- Les indicateurs doivent être contextualisés par site et période.
- Les imports doivent être tracés et ne pas écraser sans validation.
- Les données volumineuses doivent être paginées ou agrégées.

### 11.4 Limites

Le module SEO ne doit pas intégrer des connecteurs externes avancés sans validation dédiée.
Il ne doit pas mélanger les résultats GEO avec les signaux SEO classiques.

## 12. Module GEO

### 12.1 Objectif

Le module GEO suit la visibilité dans les réponses d'IA générative et compare les plateformes
suivies.

### 12.2 Plateformes IA suivies

Les plateformes cibles de référence sont :

- ChatGPT ;
- Gemini ;
- Claude ;
- Copilot ;
- Perplexity.

L'ajout d'une nouvelle plateforme doit rester possible sans refonte globale.

### 12.3 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-GEO-001 | Créer une requête GEO ou prompt de suivi | Critique | Responsable SEO/GEO | Le prompt doit avoir un objectif et un contexte | Le prompt est listé dans le module GEO |
| FR-GEO-002 | Associer une requête GEO à un site ou une marque | Critique | Responsable SEO/GEO | Une analyse doit avoir un périmètre métier | Les résultats sont filtrables par site ou marque |
| FR-GEO-003 | Sélectionner les plateformes IA suivies | Critique | Responsable SEO/GEO | La plateforme doit appartenir à une liste configurée | Les analyses indiquent ChatGPT, Gemini, Claude, Copilot ou Perplexity |
| FR-GEO-004 | Enregistrer une réponse observée | Importante | Responsable SEO/GEO | La réponse doit être datée et liée à une plateforme | L'historique affiche la réponse observée |
| FR-GEO-005 | Détecter ou renseigner des citations et mentions | Importante | Analyste | Les citations doivent distinguer marque, site et concurrent | La vue résultat affiche les mentions identifiées |
| FR-GEO-006 | Identifier la présence d'un site ou d'une marque | Critique | Analyste | La présence doit être contextualisée par prompt et plateforme | La présence est consultable par période |
| FR-GEO-007 | Calculer ou afficher un score de visibilité si applicable | Future | Responsable SEO/GEO | Le score doit être expliqué et stable | La vue indique l'échelle ou la méthode utilisée |
| FR-GEO-008 | Historiser les résultats GEO | Importante | Responsable SEO/GEO | Les résultats doivent être datés | Une évolution temporelle est possible |
| FR-GEO-009 | Comparer les plateformes IA | Importante | Analyste | Les plateformes doivent être comparées sur un même périmètre | Une vue comparative affiche présence, absence ou citations |
| FR-GEO-010 | Comparer les concurrents dans les réponses IA | Importante | Analyste | Les concurrents cités doivent être distincts des marques internes | Une analyse peut lister les concurrents mentionnés |
| FR-GEO-011 | Présenter les résultats IA avec prudence | Critique | Tous | Les réponses IA sont des observations, pas des vérités absolues | Les vues indiquent contexte, date et plateforme |

### 12.4 Comportements attendus

- Une analyse GEO doit toujours mentionner la plateforme, la date et le prompt.
- Les résultats doivent permettre de distinguer présence, absence, mention partielle et citation concurrente.
- Les plateformes IA ne doivent pas être confondues avec des sources SEO classiques.
- Les scores futurs doivent être documentés avant usage décisionnel.

### 12.5 Limites

Le module GEO ne garantit pas la stabilité des réponses IA. Les résultats doivent être lus comme
des observations contextualisées.

## 13. Module Rapports

### 13.1 Objectif

Le module Rapports permet de produire, consulter et exporter des synthèses SEO/GEO et métier.

### 13.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-REPORT-001 | Créer une demande de rapport | Importante | Responsable SEO/GEO | Le rapport doit avoir un périmètre et une période | Le rapport apparaît avec un statut |
| FR-REPORT-002 | Filtrer les rapports par site | Importante | Analyste | Un rapport peut être lié à un ou plusieurs sites | Le filtre par site retourne les rapports concernés |
| FR-REPORT-003 | Définir une période de rapport | Critique | Analyste | La période doit être explicite | Le rapport affiche ses dates |
| FR-REPORT-004 | Sélectionner les modules inclus | Importante | Analyste | Les modules inclus doivent être listés | Un rapport indique SEO, GEO, contenus ou concurrents |
| FR-REPORT-005 | Gérer un statut de rapport | Importante | Analyste | Les statuts doivent distinguer brouillon, prêt, erreur ou archivé | La liste affiche un statut lisible |
| FR-REPORT-006 | Consulter un rapport | Importante | Lecteur | La consultation respecte les droits | Un lecteur autorisé peut ouvrir le rapport |
| FR-REPORT-007 | Exporter un rapport | Secondaire | Analyste | L'export respecte permissions et données sensibles | L'export ne contient pas de secret |
| FR-REPORT-008 | Préparer une automatisation future | Future | Administrateur | L'automatisation doit rester contrôlée | Les statuts et métadonnées permettent un futur job |

### 13.3 Comportements attendus

- Un rapport doit afficher son périmètre et sa période.
- Les exports doivent être tracés si le contenu est sensible.
- Les rapports en erreur doivent présenter une cause compréhensible sans stack trace brute.
- La génération automatisée est future et ne doit pas être promise sans cadrage.

## 14. Module Configuration

### 14.1 Objectif

Le module Configuration centralise les paramètres applicatifs et fonctionnels non secrets,
ainsi que les réglages nécessaires aux modules.

### 14.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-CONFIG-001 | Consulter les paramètres applicatifs | Critique | Administrateur | Les paramètres sensibles sont masqués ou exclus | La vue configuration n'expose aucun secret brut |
| FR-CONFIG-002 | Modifier un paramètre autorisé | Critique | Administrateur | La modification doit être validée par le service | Le paramètre modifié est visible après rechargement |
| FR-CONFIG-003 | Configurer un module | Importante | Administrateur | La configuration doit être liée à son module | Le module utilise la valeur configurée |
| FR-CONFIG-004 | Exporter une configuration non secrète | Importante | Administrateur | Aucun secret ne doit être exporté en clair | Le fichier d'export exclut ou masque les secrets |
| FR-CONFIG-005 | Importer une configuration | Importante | Administrateur | L'import doit être non destructif autant que possible | Le résultat indique créés, mis à jour, ignorés et erreurs |
| FR-CONFIG-006 | Garantir l'idempotence des imports | Importante | Administrateur | Un même import ne doit pas créer de doublons inutiles | Un réimport stable produit le même état attendu |
| FR-CONFIG-007 | Tracer les imports et exports | Critique | Administrateur | Les actions sensibles doivent être auditées | Un événement d'audit est consultable |
| FR-CONFIG-008 | Contrôler les droits administrateur | Critique | Administrateur | Les changements de configuration sont réservés aux autorisés | Un utilisateur non autorisé reçoit un refus |

### 14.3 Comportements attendus

- Les secrets ne doivent jamais apparaître en clair.
- Un import doit fournir un résumé explicite.
- Une erreur de configuration doit être lisible sans exposer la valeur sensible.
- Les paramètres doivent être validés avant persistance.

## 15. Module Administration

### 15.1 Objectif

Le module Administration gère les utilisateurs, rôles, permissions et actions sensibles.

### 15.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-ADMIN-001 | Consulter la liste des utilisateurs | Critique | Administrateur | Seuls les administrateurs autorisés y accèdent | La liste est protégée |
| FR-ADMIN-002 | Créer ou inviter un utilisateur | Future | Administrateur | L'utilisateur doit avoir un rôle initial | Un utilisateur est créé sans mot de passe en clair |
| FR-ADMIN-003 | Modifier un rôle utilisateur | Critique | Administrateur | La modification de rôle est une action sensible | L'action est auditée |
| FR-ADMIN-004 | Activer ou désactiver un utilisateur | Importante | Administrateur | Désactiver ne supprime pas l'historique | L'utilisateur désactivé ne peut plus accéder |
| FR-ADMIN-005 | Gérer les rôles | Critique | Administrateur | Les rôles système critiques sont protégés | Les rôles ne peuvent pas être détruits sans contrôle |
| FR-ADMIN-006 | Gérer les permissions | Critique | Administrateur | Les permissions contrôlent les modules et actions | Un refus 403 est retourné sans permission |
| FR-ADMIN-007 | Protéger les endpoints admin | Critique | Administrateur | Authentification et autorisation obligatoires | Un utilisateur non autorisé ne peut pas appeler les routes admin |
| FR-ADMIN-008 | Limiter les actions sensibles | Critique | Administrateur | Les actions critiques nécessitent confirmation et audit | Une action sensible produit une trace |

### 15.3 Comportements attendus

- Les endpoints admin ne doivent pas être publics.
- Les erreurs de permission doivent être claires et non techniques.
- Les permissions doivent être appliquées côté API, pas seulement côté interface.
- Les secrets et clés ne doivent pas être renvoyés en clair.

## 16. Module Logs et audit

### 16.1 Objectif

Le module Logs et audit permet de consulter les événements techniques et les traces d'actions
sensibles sans exposer de données confidentielles.

### 16.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-LOG-001 | Journaliser les erreurs API | Critique | Administrateur | Les logs ne contiennent pas de secrets | Une erreur API est visible avec niveau et date |
| FR-LOG-002 | Journaliser les erreurs Desktop utiles | Importante | Administrateur | Le Desktop ne logue pas de token ou secret | Une erreur réseau est compréhensible |
| FR-LOG-003 | Auditer les actions sensibles | Critique | Administrateur | Les actions admin, imports et exports sont auditables | Une trace mentionne acteur, action, module et date si disponibles |
| FR-LOG-004 | Distinguer logs techniques et audit métier | Critique | Administrateur | L'audit est durable et orienté action | Les vues distinguent log et audit |
| FR-LOG-005 | Filtrer les logs | Importante | Administrateur | Les listes doivent être paginées | Les filtres niveau, période et module fonctionnent |
| FR-LOG-006 | Consulter les logs selon droits | Critique | Administrateur | Les logs peuvent contenir des informations sensibles | Les non autorisés n'accèdent pas aux logs |
| FR-LOG-007 | Définir une conservation adaptée | Future | Administrateur | La conservation dépend de l'environnement et du type | Une politique pourra être appliquée |
| FR-LOG-008 | Ne jamais exposer de payload sensible complet | Critique | Tous | Les logs utilisent une allowlist de champs | Aucun mot de passe, token ou clé API brute n'est présent |

### 16.3 Comportements attendus

- Une stack trace brute ne doit pas être affichée à l'utilisateur final.
- Les logs doivent permettre le diagnostic sans fuite.
- Les actions administratives sensibles doivent être auditables.
- Les exports de logs doivent être limités et protégés.

## 17. Application Desktop PySide6

### 17.1 Objectif

L'application Desktop PySide6 est l'interface interne actuelle. Elle doit permettre de consulter
et manipuler les modules autorisés via FastAPI.

### 17.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-DESKTOP-001 | Communiquer uniquement via HTTP REST | Critique | Développeur Desktop | Aucun accès direct PostgreSQL | Le Desktop utilise l'ApiClient et FastAPI |
| FR-DESKTOP-002 | Ne jamais importer de couche backend interne | Critique | Développeur Desktop | Le Desktop reste un client | Aucun import de repositories ou models backend |
| FR-DESKTOP-003 | Fournir une navigation stable | Critique | Utilisateur interne | Les modules principaux restent accessibles | La sidebar ou navigation indique le module actif |
| FR-DESKTOP-004 | Afficher les écrans principaux | Importante | Utilisateur interne | Les modules disponibles ont une page ou placeholder clair | L'utilisateur distingue sites, mots-clés, concurrents, rapports, administration |
| FR-DESKTOP-005 | Gérer les erreurs API | Critique | Utilisateur interne | Les erreurs réseau ne doivent pas provoquer de crash | Un message clair et une possibilité de retry sont affichés |
| FR-DESKTOP-006 | Gérer les états chargement, vide et erreur | Critique | Utilisateur interne | Un état vide n'est pas une erreur | Chaque page distingue loading, empty, error et data |
| FR-DESKTOP-007 | Respecter le design system | Importante | Développeur Desktop | Le Desktop doit rester sobre et orienté données | Les écrans suivent les conventions existantes |
| FR-DESKTOP-008 | Préparer l'authentification future | Importante | Développeur Desktop | Le token ne doit jamais être logué | L'ApiClient pourra gérer Authorization Bearer |
| FR-DESKTOP-009 | Préparer la cohérence avec React | Importante | Développeur Desktop | Les libellés et états doivent rester réutilisables | Les comportements Desktop sont transposables |

### 17.3 Comportements attendus

- L'interface doit rester utilisable si une API est indisponible.
- Les tables doivent gérer pagination, filtres et états.
- Les actions sensibles doivent demander confirmation si elles existent.
- L'interface ne doit pas décider seule des permissions finales.

## 18. Futur frontend React

### 18.1 Objectif

Le futur frontend React doit pouvoir réutiliser les contrats API et les règles métier sans
réimplémenter le backend.

### 18.2 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-REACT-001 | Réutiliser l'API REST existante | Future | Développeur frontend | L'API est indépendante de PySide6 | Les endpoints utiles ne dépendent pas du Desktop |
| FR-REACT-002 | Respecter la séparation frontend/backend | Future | Développeur frontend | Aucune logique métier principale côté React | React appelle les services via FastAPI |
| FR-REACT-003 | Consommer des contrats cohérents | Future | Développeur frontend | Les réponses sont typées et stables | Les listes, erreurs et objets sont prévisibles |
| FR-REACT-004 | Gérer pagination, filtres et tri | Future | Développeur frontend | Les conventions API sont partagées | Les tables React peuvent réutiliser les mêmes paramètres |
| FR-REACT-005 | Réutiliser l'authentification | Future | Développeur frontend | Les règles de sécurité restent côté API | React gère la session sans contourner l'autorisation |
| FR-REACT-006 | Conserver les intentions UX | Future | Développeur frontend | Les états et libellés restent cohérents | Les écrans React reprennent loading, empty, error et forbidden |

## 19. Exigences API générales

### 19.1 Exigences

| ID | Description | Priorité | Acteur principal | Règle métier associée | Critère d'acceptation |
|---|---|---|---|---|---|
| FR-API-001 | Respecter les conventions REST | Critique | Développeur backend | Les ressources sont exposées de manière cohérente | Les routes utilisent des méthodes HTTP adaptées |
| FR-API-002 | Fournir une pagination standard | Critique | Développeur backend | Les grandes listes sont paginées | La réponse liste contient items et métadonnées |
| FR-API-003 | Fournir des filtres contrôlés | Critique | Développeur backend | Les filtres non autorisés sont rejetés ou ignorés proprement | Les résultats reflètent les filtres valides |
| FR-API-004 | Fournir un tri contrôlé | Importante | Développeur backend | Les champs de tri sont whitelistés | Un tri invalide retourne une erreur claire |
| FR-API-005 | Valider les entrées avec Pydantic | Critique | Développeur backend | Les schémas définissent les contrats API | Les payloads invalides produisent des erreurs 422 |
| FR-API-006 | Standardiser les erreurs | Critique | Développeur backend | Le Desktop doit distinguer les états | Les erreurs incluent code et message exploitables |
| FR-API-007 | Utiliser des statuts HTTP cohérents | Critique | Développeur backend | Le statut reflète le résultat métier | 404, 409, 422, 401 et 403 sont utilisés correctement |
| FR-API-008 | Protéger les routes sensibles | Critique | Développeur backend | Authentification et permissions requises | Une route admin refuse un utilisateur non autorisé |
| FR-API-009 | Séparer routes, services et repositories | Critique | Développeur backend | La route ne fait pas de requête SQLAlchemy | La logique métier est testable dans le service |

### 19.2 Comportements attendus

- Les réponses doivent être compatibles Desktop et futur React.
- Les changements cassants doivent être évités ou versionnés.
- Les erreurs ne doivent pas exposer les détails internes.
- Les endpoints lourds doivent prévoir pagination ou traitement asynchrone futur.

## 20. Exigences de données

Cette section reste au niveau logiciel. Elle ne remplace pas la future conception de base de
données.

| ID | Description | Priorité | Règle attendue |
|---|---|---|---|
| FR-DATA-001 | Identifier chaque ressource persistée | Critique | Chaque ressource possède un identifiant stable |
| FR-DATA-002 | Horodater les ressources importantes | Critique | Les dates de création et mise à jour sont disponibles si pertinentes |
| FR-DATA-003 | Gérer des statuts cohérents | Importante | Les statuts utilisent des valeurs contrôlées |
| FR-DATA-004 | Représenter les relations principales | Critique | Site vers mots-clés, contenus, SEO, GEO et rapports |
| FR-DATA-005 | Appliquer l'unicité métier | Critique | URL principale, rôle ou code selon ressource |
| FR-DATA-006 | Préférer une suppression contrôlée | Importante | Désactivation ou archivage selon module |
| FR-DATA-007 | Prévoir l'historisation | Importante | Les données temporelles restent datées |
| FR-DATA-008 | Auditer les actions sensibles | Critique | Les changements admin ou configuration sont traçables |

## 21. Exigences non fonctionnelles

| ID | Catégorie | Description | Priorité | Critère d'acceptation |
|---|---|---|---|---|
| NFR-SEC-001 | Sécurité | Protéger les endpoints sensibles | Critique | Les accès non autorisés sont refusés |
| NFR-MAIN-001 | Maintenabilité | Respecter l'architecture en couches | Critique | Routes sans logique métier, services testables |
| NFR-TEST-001 | Testabilité | Permettre des tests Pytest ciblés | Critique | Les règles métier peuvent être testées au niveau service |
| NFR-PERF-001 | Performance | Paginer les grandes listes | Critique | Les endpoints de liste n'exposent pas de volume non borné |
| NFR-ROB-001 | Robustesse | Gérer les erreurs sans crash utilisateur | Critique | Desktop affiche un état erreur exploitable |
| NFR-EVOL-001 | Évolutivité | Ajouter modules ou plateformes IA sans refonte | Importante | Les plateformes IA sont configurables ou extensibles |
| NFR-OBS-001 | Observabilité | Produire logs et audits utiles | Importante | Les événements critiques sont consultables |
| NFR-PORT-001 | Portabilité | Préparer React sans changer le métier | Importante | Les contrats API ne dépendent pas de PySide6 |
| NFR-DOC-001 | Documentation | Maintenir la documentation des changements importants | Critique | Les nouveaux modules sont documentés |
| NFR-QUAL-001 | Qualité code | Respecter Ruff et conventions | Critique | Le lint passe avant PR |

## 22. Exigences de sécurité

### 22.1 Principes

| ID | Description | Priorité | Critère d'acceptation |
|---|---|---|---|
| SEC-001 | Authentifier les accès privés | Critique | Un utilisateur non authentifié ne peut pas accéder aux ressources privées |
| SEC-002 | Autoriser selon rôles et permissions | Critique | Un rôle sans permission reçoit un refus |
| SEC-003 | Protéger l'administration | Critique | Les endpoints admin ne sont pas accessibles aux rôles non autorisés |
| SEC-004 | Ne jamais exposer les secrets | Critique | Aucun secret brut dans réponses, logs ou exports |
| SEC-005 | Masquer les données sensibles | Critique | Les clés ou tokens sont affichés sous forme masquée ou exclus |
| SEC-006 | Sécuriser les exports | Importante | Les exports respectent droits et périmètre |
| SEC-007 | Nettoyer les logs | Critique | Les logs ne contiennent pas mot de passe, token ou clé API |
| SEC-008 | Ne pas divulguer d'erreurs internes | Critique | Les erreurs utilisateur restent génériques et exploitables |
| SEC-009 | Appliquer le moindre privilège | Importante | Les rôles disposent uniquement des droits nécessaires |

## 23. Exigences de qualité logicielle

| ID | Description | Priorité | Critère d'acceptation |
|---|---|---|---|
| QA-001 | Les tests Pytest doivent couvrir les fonctionnalités métier importantes | Critique | Les cas succès et erreurs sont testés |
| QA-002 | Ruff doit rester applicable | Critique | Aucune violation lint non justifiée |
| QA-003 | Les migrations Alembic doivent être explicites | Critique | Pas de `Base.metadata.create_all()` ni `drop_all()` |
| QA-004 | Les routes ne contiennent pas de logique métier | Critique | Les routes délèguent aux services |
| QA-005 | Les services sont testables | Critique | Les règles métier sont isolées |
| QA-006 | Les repositories restent isolés | Critique | Pas de FastAPI, Pydantic API ou logique métier dans repository |
| QA-007 | Les schémas Pydantic restent cohérents | Critique | Entrées et sorties sont typées |
| QA-008 | La documentation est maintenue | Importante | Toute fonctionnalité importante met à jour la documentation pertinente |

## 24. Exigences de compatibilité et d'évolution

| ID | Description | Priorité | Critère d'acceptation |
|---|---|---|---|
| EVOL-001 | Maintenir la compatibilité Desktop | Critique | Les réponses utilisées par le Desktop ne changent pas silencieusement |
| EVOL-002 | Préparer le futur React | Importante | Les contrats REST restent indépendants de PySide6 |
| EVOL-003 | Ajouter de nouvelles plateformes IA | Importante | Le module GEO peut intégrer un nouveau fournisseur sans refonte globale |
| EVOL-004 | Ajouter de nouveaux modules | Importante | Le pattern Routes -> Services -> Repositories -> Models est réutilisable |
| EVOL-005 | Préserver la compatibilité ascendante API | Importante | Les changements cassants sont évités ou documentés |
| EVOL-006 | Versionner les évolutions majeures | Future | Une nouvelle version API peut être créée si nécessaire |

## 25. Cas d'usage principaux

### 25.1 Créer un site web

| Élément | Description |
|---|---|
| Acteur | Responsable SEO/GEO |
| Préconditions | L'utilisateur est authentifié et autorisé à créer un site |
| Scénario nominal | L'utilisateur ouvre le module Sites, saisit le nom et l'URL principale, valide le formulaire, l'API crée le site |
| Exceptions | URL invalide, URL déjà existante, permission insuffisante, API indisponible |
| Résultat attendu | Le site est créé, visible dans la liste et disponible pour rattachements futurs |

### 25.2 Créer un mot-clé

| Élément | Description |
|---|---|
| Acteur | Responsable SEO/GEO |
| Préconditions | Un site existe, l'utilisateur dispose des droits de création |
| Scénario nominal | L'utilisateur saisit l'expression, choisit le site, l'intention, la catégorie et éventuellement l'URL cible |
| Exceptions | Mot-clé vide, site inexistant, doublon métier, permission insuffisante |
| Résultat attendu | Le mot-clé est disponible dans les vues filtrées du site |

### 25.3 Consulter les performances SEO d'un site

| Élément | Description |
|---|---|
| Acteur | Analyste |
| Préconditions | Le site existe et l'utilisateur a accès aux données SEO |
| Scénario nominal | L'utilisateur choisit un site et une période, consulte KPI, pages, requêtes et tendances |
| Exceptions | Aucune donnée disponible, source externe indisponible, API en erreur |
| Résultat attendu | L'utilisateur obtient une lecture contextualisée des performances SEO |

### 25.4 Suivre une requête GEO

| Élément | Description |
|---|---|
| Acteur | Responsable SEO/GEO |
| Préconditions | Le site ou la marque existe, les plateformes IA sont configurées ou renseignées |
| Scénario nominal | L'utilisateur crée un prompt, choisit les plateformes, enregistre ou consulte les réponses observées |
| Exceptions | Plateforme non disponible, prompt invalide, absence de réponse, permission insuffisante |
| Résultat attendu | La requête GEO est suivie avec plateforme, date, réponse et mentions éventuelles |

### 25.5 Comparer une plateforme IA

| Élément | Description |
|---|---|
| Acteur | Analyste |
| Préconditions | Des résultats GEO existent sur plusieurs plateformes |
| Scénario nominal | L'utilisateur filtre par prompt, période et plateformes, compare présence de marque et citations |
| Exceptions | Données partielles, plateformes non comparables, aucune réponse disponible |
| Résultat attendu | L'utilisateur visualise les différences entre ChatGPT, Gemini, Claude, Copilot et Perplexity |

### 25.6 Générer un rapport

| Élément | Description |
|---|---|
| Acteur | Analyste |
| Préconditions | L'utilisateur a accès aux modules inclus dans le rapport |
| Scénario nominal | L'utilisateur choisit site, période, modules inclus et lance la préparation du rapport |
| Exceptions | Données insuffisantes, génération en erreur, permission insuffisante |
| Résultat attendu | Un rapport est créé ou préparé avec un statut clair |

### 25.7 Exporter une configuration

| Élément | Description |
|---|---|
| Acteur | Administrateur |
| Préconditions | L'utilisateur possède les droits d'administration |
| Scénario nominal | L'utilisateur lance un export de configuration non secrète, le système exclut les secrets et trace l'action |
| Exceptions | Permission insuffisante, configuration invalide, erreur de génération |
| Résultat attendu | L'export est disponible sans secret en clair et l'action est auditée |

### 25.8 Administrer un utilisateur

| Élément | Description |
|---|---|
| Acteur | Administrateur |
| Préconditions | L'administrateur est authentifié et autorisé |
| Scénario nominal | L'administrateur consulte un utilisateur, modifie son rôle ou son statut, confirme l'action |
| Exceptions | Rôle protégé, permission insuffisante, utilisateur introuvable |
| Résultat attendu | Le changement est appliqué, protégé et audité |

## 26. Règles métier transverses

| ID | Règle | Description | Modules concernés |
|---|---|---|---|
| BR-001 | Cohérence des statuts | Les statuts doivent utiliser des valeurs contrôlées et compréhensibles | Tous |
| BR-002 | Unicité | Les doublons métier critiques doivent être refusés | Sites, mots-clés, concurrents, rôles |
| BR-003 | Suppression contrôlée | La désactivation ou l'archivage est préféré à la suppression destructive | Tous |
| BR-004 | Droits d'accès | L'API applique les permissions finales | Tous |
| BR-005 | Import/export | Les imports et exports sont non destructifs, idempotents et tracés autant que possible | Configuration, SEO, mots-clés |
| BR-006 | Historisation | Les données temporelles doivent conserver une date et un contexte | SEO, GEO, rapports |
| BR-007 | Validation | Les entrées utilisateur sont validées par Pydantic et par les services métier | API, services |
| BR-008 | Erreurs | Les erreurs doivent être explicites sans fuite technique ou secret | API, Desktop, React futur |
| BR-009 | Séparation SEO/GEO | Les signaux SEO et GEO restent distingués | SEO, GEO, rapports |
| BR-010 | Résultats IA contextualisés | Les réponses IA ne sont pas présentées comme certitudes absolues | GEO |

## 27. Critères d'acceptation globaux

| Exigence | Critère | Méthode de vérification | Priorité |
|---|---|---|---|
| Architecture en couches | Aucune logique métier dans les routes | Revue de code | Critique |
| Desktop REST uniquement | Aucun accès PostgreSQL depuis Desktop | Revue de code | Critique |
| Pagination | Les listes principales sont paginées | Tests API ou vérification manuelle | Critique |
| Permissions | Les endpoints sensibles refusent les non autorisés | Tests API | Critique |
| Pydantic | Les payloads invalides sont rejetés | Tests API | Critique |
| Imports configuration | Import non destructif autant que possible | Tests service | Importante |
| Exports | Aucun secret en clair | Revue diff et tests | Critique |
| Logs | Aucun token ou clé brute | Revue et tests | Critique |
| SEO | Consultation par site et période | Test fonctionnel | Importante |
| GEO | Comparaison par plateforme IA | Test fonctionnel | Importante |
| Rapports | Statut et période visibles | Test fonctionnel | Importante |
| Documentation | Document pertinent mis à jour | Revue PR | Importante |
| Qualité | Ruff et Pytest disponibles passent | Commandes projet | Critique |

## 28. Priorisation des exigences

### 28.1 Classification

| Niveau | Définition | Exemple |
|---|---|---|
| Critique | Nécessaire au fonctionnement sûr et cohérent | Architecture, sécurité, sites, API |
| Importante | Nécessaire à la valeur métier principale | SEO, GEO, mots-clés, rapports |
| Secondaire | Utile mais peut être différé | Exports avancés, notes, catégories étendues |
| Future | Évolution à cadrer ultérieurement | React complet, automatisations, connecteurs avancés |

### 28.2 Priorités par famille

| Famille | Priorité |
|---|---|
| Architecture et séparation des couches | Critique |
| Sécurité et permissions | Critique |
| Sites web | Critique |
| Mots-clés | Critique à importante |
| SEO | Importante |
| GEO | Critique à importante |
| Desktop | Critique |
| Configuration | Critique |
| Logs et audit | Critique |
| Rapports | Importante |
| Contenus | Importante |
| Concurrents | Importante |
| Futur React | Future |

## 29. Hors périmètre logiciel immédiat

| Hors périmètre | Justification |
|---|---|
| Frontend React complet immédiat | Prévu comme évolution future |
| Accès direct Desktop à PostgreSQL | Interdit par l'architecture |
| Automatisations destructives sans validation | Risque métier et sécurité |
| Refactor global non planifié | Hors périmètre et risqué |
| Scraping massif non contrôlé | Risque technique, légal et réputationnel |
| Intégrations externes avancées non validées | Dépendances, coûts et sécurité à cadrer |
| Documentation API endpoint par endpoint dans ce fichier | À traiter dans les documents API |
| Modèle de base complet dans ce fichier | À traiter dans la spécification database |
| Roadmap sprint par sprint dans ce fichier | À traiter dans la roadmap dédiée |

## 30. Traçabilité avec le cahier des charges

| Besoin du cahier des charges | Famille d'exigences logicielles | Exemples d'IDs |
|---|---|---|
| Centraliser les données | Exigences globales et données | FR-GEN-001, FR-DATA-004 |
| Suivre les performances SEO | Module SEO | FR-SEO-001 à FR-SEO-009 |
| Suivre la visibilité GEO | Module GEO | FR-GEO-001 à FR-GEO-011 |
| Gérer les sites web | Module Sites | FR-SITE-001 à FR-SITE-008 |
| Gérer les mots-clés | Module Mots-clés | FR-KEYWORD-001 à FR-KEYWORD-009 |
| Gérer les contenus | Module Contenus | FR-CONTENT-001 à FR-CONTENT-009 |
| Gérer les concurrents | Module Concurrents | FR-COMPETITOR-001 à FR-COMPETITOR-006 |
| Produire des rapports | Module Rapports | FR-REPORT-001 à FR-REPORT-008 |
| Gérer la configuration | Module Configuration | FR-CONFIG-001 à FR-CONFIG-008 |
| Administrer et sécuriser | Administration et sécurité | FR-ADMIN-001 à FR-ADMIN-008, SEC-001 à SEC-009 |
| Tracer et auditer | Logs et audit | FR-LOG-001 à FR-LOG-008 |
| Fournir une interface Desktop | Desktop | FR-DESKTOP-001 à FR-DESKTOP-009 |
| Préparer React | Évolution frontend | FR-REACT-001 à FR-REACT-006 |

## 31. Synthèse finale

Cette spécification logicielle définit ce que le logiciel doit garantir pour transformer le
cahier des charges métier en développements cohérents.

Le logiciel doit garantir :

- une centralisation fiable des données SEO/GEO ;
- une séparation stricte des responsabilités ;
- une API REST stable pour Desktop et futur React ;
- une application Desktop sans accès direct à PostgreSQL ;
- des modules métier bornés et évolutifs ;
- des permissions appliquées côté API ;
- des imports et exports maîtrisés ;
- des logs et audits sans secrets ;
- une qualité de code vérifiable par tests, linting et documentation.

Les principes de développement restent les suivants :

- `Routes -> Services -> Repositories -> Models` ;
- schémas Pydantic pour les contrats API ;
- migrations Alembic explicites ;
- services testables ;
- repositories isolés ;
- Desktop consommateur HTTP REST ;
- futur React préparé par des contrats API cohérents.

Ce document doit servir de référence pour les prochains développements fonctionnels. Il pourra
être enrichi lorsque de nouveaux modules seront cadrés, mais il ne doit pas devenir un schéma
de base de données, une documentation API exhaustive ou une roadmap opérationnelle.
