# Database Design Specification

## 1. Informations générales

| Élément | Description |
|---|---|
| Projet | Veille SEO-GEO Groupe A.P&Partner |
| Document | Spécification de conception de la base de données |
| Statut | Référence de conception haut niveau et opérationnelle |
| Périmètre | PostgreSQL, SQLAlchemy 2.x, Alembic, cohérence FastAPI, Pydantic, Desktop et futur React |
| Public cible | Responsable projet, développeur backend, futur intervenant data, contributeur documentation |
| Relation avec le cahier des charges | Traduit les besoins métier en familles de données et principes de persistance |
| Relation avec la SRS | Traduit les exigences logicielles en entités, relations, contraintes et index |
| Relation avec l'architecture | Respecte `Routes -> Services -> Repositories -> Models` et les documents `docs/architecture/` |

Ce document définit la conception de données attendue pour **Veille SEO-GEO Groupe A.P&Partner**.

Il prépare les futures migrations Alembic, modèles SQLAlchemy, repositories et schémas Pydantic
sans créer d'implémentation. Les tables proposées sont des cibles de conception à valider lors
des développements. Elles ne constituent pas un script SQL prêt à exécuter.

Ce document ne modifie pas :

- les modèles SQLAlchemy existants ;
- les migrations Alembic existantes ;
- les repositories ;
- les routes API ;
- les tests ;
- les fichiers Desktop.

## 2. Objectifs de conception de la base

### 2.1 Objectifs principaux

La base PostgreSQL doit permettre de :

- centraliser les référentiels métier ;
- garantir la cohérence des relations ;
- supporter l'évolution des modules SEO et GEO ;
- historiser les observations utiles ;
- tracer les actions sensibles ;
- sécuriser les données sensibles ;
- fournir des accès performants aux listes, filtres et rapports ;
- rester compatible avec FastAPI, Pydantic, Desktop PySide6 et futur React.

### 2.2 Objectifs de qualité

| Objectif | Traduction database | Impact attendu |
|---|---|---|
| Centralisation | Référentiels normalisés | Source de vérité unique |
| Cohérence | Contraintes FK, unique et nullabilité | Moins de données invalides |
| Évolutivité | Tables spécialisées par domaine | Ajout de modules sans refonte globale |
| Traçabilité | Timestamps, audit, logs | Diagnostic et responsabilité |
| Performance | Index sur filtres et jointures | Réponses API rapides |
| Sécurité | Secrets exclus ou protégés | Réduction du risque de fuite |
| Compatibilité | Identifiants et contrats stables | Desktop et futur React robustes |

### 2.3 Principes directeurs

1. PostgreSQL est la source persistante des données métier.
2. Les repositories sont la seule couche applicative autorisée à accéder aux données.
3. Les modèles SQLAlchemy représentent les tables, mais ne remplacent pas les migrations.
4. Les migrations Alembic décrivent explicitement chaque évolution structurelle.
5. Les contraintes importantes doivent exister en base et pas uniquement dans Pydantic.
6. Les données temporelles SEO/GEO doivent être datées et historisables.
7. Les données sensibles ne doivent jamais être stockées ou exposées en clair sans nécessité validée.
8. Le Desktop ne doit jamais accéder directement à PostgreSQL.

## 3. Vue d'ensemble du modèle de données

### 3.1 Domaines fonctionnels

| Domaine | Rôle dans la base |
|---|---|
| Administration | Utilisateurs, rôles, permissions et accès |
| Sites web | Référentiel des sites suivis |
| Mots-clés | Requêtes suivies, intentions, catégories et rattachements |
| Contenus | Sujets, pages, briefs, statuts éditoriaux et associations |
| Concurrents | Acteurs suivis, domaines et rattachements |
| SEO | Performances, positions, pages, requêtes, métriques et historiques |
| GEO | Plateformes IA, prompts, réponses, mentions, citations, scores et historiques |
| Rapports | Synthèses, périodes, filtres, statuts et exports |
| Configuration | Paramètres applicatifs et configuration par module |
| Logs | Événements techniques et applicatifs |
| Audit | Actions sensibles et changements métier importants |

### 3.2 Séparation conceptuelle

Les domaines sont séparés pour éviter la confusion entre :

- référentiel stable et historique temporel ;
- données métier et logs techniques ;
- configuration non sensible et secrets ;
- SEO classique et observations GEO ;
- données éditoriales et données de reporting.

### 3.3 Priorité de modélisation

| Priorité | Domaines concernés | Justification |
|---|---|---|
| Critique | Administration, sites web, configuration, logs/audit | Socle de sécurité et de pilotage |
| Haute | Mots-clés, SEO, GEO | Valeur métier centrale |
| Moyenne | Contenus, concurrents, rapports | Exploitation progressive |
| Future | Automatisations avancées, connecteurs externes détaillés | À cadrer dans la roadmap |

## 4. Diagramme ASCII global

```text
users ----< user_roles >---- roles ----< role_permissions >---- permissions
  |
  +----< audit_logs

websites ----< keywords ----< keyword_metrics
   |              |
   |              +----< content_keywords >---- contents
   |
   +----< website_competitors >---- competitors ----< competitor_domains
   |
   +----< seo_pages ----< seo_metrics
   |
   +----< geo_queries ----< geo_results ----< geo_mentions
   |                              |
   |                              +---- ai_platforms
   |
   +----< reports ----< report_exports

configuration_settings ----< configuration_imports
application_logs
audit_logs
```

Ce diagramme est volontairement conceptuel. Il ne représente pas toutes les colonnes, toutes
les contraintes ni tous les historiques possibles.

## 5. Conventions de nommage

### 5.1 Tables

| Règle | Convention | Exemple |
|---|---|---|
| Nom de table | `snake_case` pluriel | `websites`, `keywords` |
| Table d'association | deux domaines au pluriel | `content_keywords` |
| Table historique | suffixe explicite | `seo_metrics`, `geo_results` |
| Logs | nom fonctionnel clair | `application_logs`, `audit_logs` |
| Configuration | préfixe domaine si utile | `configuration_settings` |

### 5.2 Colonnes

| Type de colonne | Convention | Exemple |
|---|---|---|
| Identifiant primaire | `id` | `id` |
| Clé étrangère | `<table_singulier>_id` | `website_id`, `role_id` |
| Horodatage création | `created_at` | `created_at` |
| Horodatage modification | `updated_at` | `updated_at` |
| Désactivation | `is_active` ou `disabled_at` | `is_active` |
| Statut | `status` | `status` |
| Code métier | `code` | `code` |
| Nom affichable | `name` ou `title` | `name`, `title` |
| Métadonnées | `metadata` ou nom spécialisé | `analysis_metadata` |

### 5.3 Clés et contraintes

| Élément | Convention | Exemple |
|---|---|---|
| Primary key | `pk_<table>` | `pk_websites` |
| Foreign key | `fk_<source>_<target>` | `fk_keywords_websites` |
| Unique constraint | `uq_<table>_<colonnes>` | `uq_websites_url` |
| Check constraint | `ck_<table>_<règle>` | `ck_reports_period` |
| Index simple | `ix_<table>_<colonne>` | `ix_keywords_website_id` |
| Index composite | `ix_<table>_<col1>_<col2>` | `ix_seo_metrics_website_date` |

### 5.4 Booléens, statuts et timestamps

| Élément | Règle |
|---|---|
| Booléen | Préfixe `is_`, `has_`, `can_` |
| Statut | Valeurs contrôlées par service et éventuellement contrainte |
| Timestamps | `DateTime(timezone=True)` |
| Date métier | `Date` si l'heure n'apporte rien |
| Soft delete | `is_active`, `archived_at` ou `deleted_at` selon module |

### 5.5 JSON et JSONB

Les champs JSON/JSONB doivent rester exceptionnels et justifiés. Ils sont acceptables pour :

- métadonnées d'import ;
- détails variables d'un provider IA ;
- payload d'analyse non critique ;
- snapshot de filtre de rapport ;
- résultat brut contrôlé si le schéma est instable.

Ils ne doivent pas remplacer des relations stables, des colonnes filtrées ou des contraintes
métier connues.

## 6. Types de données recommandés

| Besoin | Type SQLAlchemy recommandé | Usage attendu |
|---|---|---|
| Identifiant standard | `Integer` | Tables métier courantes |
| Identifiant très volumineux futur | `BigInteger` | Logs ou métriques très volumineux si nécessaire |
| Libellé court | `String(length)` | Nom, code, statut, email |
| Texte long | `Text` | Description, notes, prompt, réponse IA |
| Booléen | `Boolean` | Actif, archivé, visible |
| Horodatage | `DateTime(timezone=True)` | Création, mise à jour, exécution |
| Date métier | `Date` | Période de rapport, date de métrique |
| Valeur décimale | `Numeric` | Scores, coûts, positions moyennes, métriques |
| Donnée structurée variable | `JSON` ou `JSONB` | Métadonnées validées |
| Valeur contrôlée | Enum applicatif ou `String` contrôlé | Statuts, types, intentions |
| UUID | UUID si besoin futur validé | Exposition publique ou synchronisation externe |

### 6.1 Integer et BigInteger

`Integer` est suffisant pour les tables métier initiales. `BigInteger` peut être envisagé pour
des tables de logs, mesures SEO/GEO ou événements très volumineux si la volumétrie le justifie.

### 6.2 String et Text

`String(length)` doit être utilisé pour les champs bornés et fréquemment filtrés. `Text` doit
être réservé aux contenus longs, notes, prompts, réponses IA et messages de logs.

### 6.3 Numeric

`Numeric` est recommandé pour les scores, taux, coûts et valeurs où une précision stable est
utile. Les entiers restent préférables pour les positions simples ou compteurs.

### 6.4 Enums applicatifs

Les valeurs contrôlées peuvent être représentées par des chaînes validées côté Pydantic et
service. Une contrainte base peut renforcer les statuts critiques. Les enums doivent rester
évolutifs pour ne pas bloquer inutilement les migrations.

## 7. Principes transverses

### 7.1 Timestamps

| Colonne | Rôle | Recommandation |
|---|---|---|
| `created_at` | Date de création | Obligatoire sur tables métier |
| `updated_at` | Dernière modification | Obligatoire si modification possible |
| `archived_at` | Archivage | Optionnel selon module |
| `deleted_at` | Suppression logique | À utiliser avec prudence |
| `observed_at` | Observation SEO/GEO | Obligatoire sur données temporelles |
| `executed_at` | Exécution d'un traitement | Logs, imports, rapports |

### 7.2 Soft delete et désactivation

La désactivation doit être préférée à la suppression physique pour :

- sites ;
- utilisateurs ;
- concurrents ;
- mots-clés ;
- contenus ;
- rapports ;
- configuration active.

La suppression physique peut rester possible pour des tables d'association ou données
temporaires sans valeur historique.

### 7.3 Idempotence

Les imports et synchronisations doivent s'appuyer sur des clés naturelles ou contraintes
uniques pour éviter les doublons :

- `code` pour rôles, permissions et paramètres ;
- `url` ou `domain` normalisés pour sites et concurrents ;
- couple `website_id` + `keyword` pour mots-clés si validé ;
- couple `platform_id` + `code` pour plateformes IA ;
- identifiant externe si une intégration validée en fournit un.

### 7.4 Pagination et filtres

Les tables destinées aux listes Desktop/API doivent prévoir des index sur :

- identifiant de rattachement ;
- statut ;
- date ;
- type ;
- période ;
- plateforme IA ;
- site web ;
- niveau de log.

### 7.5 Données sensibles

Les mots de passe, tokens, secrets et clés API ne doivent jamais être stockés en clair. Les
réponses API ne doivent exposer que des valeurs masquées ou des empreintes non réversibles
lorsque le besoin métier existe.

## 8. Domaine Administration

### 8.1 Tables proposées

| Table | Objectif |
|---|---|
| `users` | Comptes utilisateurs internes |
| `roles` | Rôles applicatifs |
| `permissions` | Permissions fines par module/action |
| `user_roles` | Association utilisateurs/rôles |
| `role_permissions` | Association rôles/permissions |
| `refresh_tokens` | Sessions longues futures si authentification complète |

### 8.2 `users`

| Élément | Description |
|---|---|
| Objectif | Stocker les comptes utilisateurs internes |
| Colonnes principales | `id`, `email`, `full_name`, `password_hash`, `is_active`, `last_login_at`, `created_at`, `updated_at` |
| Contraintes | `email` unique, `password_hash` nullable uniquement si stratégie d'invitation future |
| Relations | `user_roles`, `audit_logs`, logs si acteur connu |
| Index recommandés | `email`, `is_active`, `created_at` |
| Règles métier | Pas de mot de passe en clair, désactivation plutôt que suppression |

### 8.3 `roles`

| Élément | Description |
|---|---|
| Objectif | Définir les profils d'accès |
| Colonnes principales | `id`, `code`, `name`, `description`, `is_system`, `is_active`, `created_at`, `updated_at` |
| Contraintes | `code` unique, rôles système protégés |
| Relations | `user_roles`, `role_permissions` |
| Index recommandés | `code`, `is_active` |
| Règles métier | Un rôle système ne doit pas être supprimé sans procédure validée |

### 8.4 `permissions`

| Élément | Description |
|---|---|
| Objectif | Lister les droits applicatifs |
| Colonnes principales | `id`, `code`, `module`, `action`, `description`, `created_at` |
| Contraintes | `code` unique |
| Relations | `role_permissions` |
| Index recommandés | `code`, `module`, `action` |
| Règles métier | Les permissions servent d'autorité côté API |

### 8.5 Associations administration

| Table | Colonnes clés | Contraintes | Suppression |
|---|---|---|---|
| `user_roles` | `user_id`, `role_id` | unique sur le couple | Suppression possible de l'association |
| `role_permissions` | `role_id`, `permission_id` | unique sur le couple | Suppression possible de l'association |

Ces tables doivent être simples, indexées sur leurs clés étrangères, et auditées au niveau
service pour les modifications sensibles.

## 9. Domaine Sites web

### 9.1 Tables proposées

| Table | Objectif |
|---|---|
| `websites` | Référentiel principal des sites |
| `website_types` | Typologie optionnelle des sites |
| `website_status_history` | Historique optionnel des changements de statut |

### 9.2 `websites`

| Élément | Description |
|---|---|
| Objectif | Identifier les sites suivis |
| Colonnes principales | `id`, `name`, `url`, `domain`, `website_type_id`, `status`, `is_active`, `created_at`, `updated_at` |
| Contraintes | URL ou domaine unique selon règle validée, URL non nulle |
| Relations | Mots-clés, contenus, concurrents, SEO, GEO, rapports |
| Index recommandés | `url`, `domain`, `status`, `is_active`, `website_type_id` |
| Règles métier | Désactivation sans destruction des historiques |

### 9.3 `website_types`

| Élément | Description |
|---|---|
| Objectif | Classer les sites si le besoin est confirmé |
| Colonnes principales | `id`, `code`, `name`, `description`, `is_active` |
| Contraintes | `code` unique |
| Relations | `websites` |
| Index recommandés | `code`, `is_active` |
| Règles métier | Ne pas multiplier les types sans usage de filtre ou reporting |

### 9.4 Rattachements

Un site peut être rattaché :

- à des mots-clés ;
- à des contenus ;
- à des concurrents ;
- à des pages SEO ;
- à des requêtes GEO ;
- à des rapports ;
- à des logs ou audits via identifiants de ressource.

## 10. Domaine Mots-clés

### 10.1 Tables proposées

| Table | Objectif |
|---|---|
| `keywords` | Référentiel des mots-clés suivis |
| `keyword_categories` | Catégories métier |
| `keyword_metrics` | Mesures temporelles associées |
| `keyword_imports` | Traçabilité des imports |

### 10.2 `keywords`

| Élément | Description |
|---|---|
| Objectif | Stocker les requêtes suivies |
| Colonnes principales | `id`, `website_id`, `keyword`, `intent`, `category_id`, `target_url`, `status`, `priority`, `created_at`, `updated_at` |
| Contraintes | Mot-clé non vide, `website_id` obligatoire si suivi par site |
| Relations | `websites`, `keyword_categories`, contenus, métriques SEO |
| Index recommandés | `website_id`, `keyword`, `intent`, `status`, `category_id` |
| Règles métier | Doublons contrôlés par couple `website_id` + `keyword` si validé |

### 10.3 `keyword_categories`

| Élément | Description |
|---|---|
| Objectif | Organiser les mots-clés par univers ou priorité métier |
| Colonnes principales | `id`, `code`, `name`, `description`, `is_active` |
| Contraintes | `code` unique |
| Relations | `keywords` |
| Index recommandés | `code`, `is_active` |
| Règles métier | Catégories maintenues par profils autorisés |

### 10.4 `keyword_metrics`

| Élément | Description |
|---|---|
| Objectif | Historiser des valeurs de performance par mot-clé |
| Colonnes principales | `id`, `keyword_id`, `metric_date`, `position`, `volume`, `source`, `metadata`, `created_at` |
| Contraintes | `keyword_id` non nul, date non nulle |
| Relations | `keywords` |
| Index recommandés | `keyword_id`, `metric_date`, couple `keyword_id` + `metric_date` |
| Règles métier | Une métrique est une observation datée, pas une valeur permanente |

## 11. Domaine Contenus

### 11.1 Tables proposées

| Table | Objectif |
|---|---|
| `contents` | Fiches contenus |
| `content_types` | Types de contenus |
| `content_keywords` | Association contenus/mots-clés |
| `content_versions` | Historique ou versions futures |
| `content_status_history` | Changements de statut éditorial |

### 11.2 `contents`

| Élément | Description |
|---|---|
| Objectif | Suivre les sujets, pages et briefs éditoriaux |
| Colonnes principales | `id`, `website_id`, `title`, `url`, `content_type_id`, `status`, `author_user_id`, `brief`, `priority`, `created_at`, `updated_at` |
| Contraintes | Titre non nul, site requis si contenu lié à un site |
| Relations | `websites`, `content_types`, `users`, `content_keywords` |
| Index recommandés | `website_id`, `status`, `content_type_id`, `author_user_id` |
| Règles métier | Le module ne remplace pas un CMS |

### 11.3 `content_keywords`

| Élément | Description |
|---|---|
| Objectif | Relier un contenu à plusieurs mots-clés |
| Colonnes principales | `content_id`, `keyword_id`, `is_primary`, `created_at` |
| Contraintes | unique sur `content_id` + `keyword_id` |
| Relations | `contents`, `keywords` |
| Index recommandés | `content_id`, `keyword_id` |
| Règles métier | Un mot-clé principal peut être contrôlé par service si nécessaire |

### 11.4 Historisation éditoriale

L'historisation peut porter sur :

- changements de statut ;
- changements de brief ;
- auteur ou responsable ;
- date de publication ou mise à jour ;
- associations aux mots-clés.

Cette historisation doit rester proportionnée. Un versioning complet de CMS est hors périmètre.

## 12. Domaine Concurrents

### 12.1 Tables proposées

| Table | Objectif |
|---|---|
| `competitors` | Référentiel des concurrents |
| `competitor_domains` | Domaines ou URLs concurrentes |
| `website_competitors` | Association sites/concurrents |
| `competitor_notes` | Notes de veille optionnelles |

### 12.2 `competitors`

| Élément | Description |
|---|---|
| Objectif | Identifier les acteurs suivis |
| Colonnes principales | `id`, `name`, `status`, `market`, `priority`, `created_at`, `updated_at` |
| Contraintes | Nom non nul, unicité à valider selon marché |
| Relations | Domaines, sites, résultats SEO/GEO |
| Index recommandés | `name`, `status`, `market`, `priority` |
| Règles métier | Actif/inactif plutôt que suppression destructive |

### 12.3 `competitor_domains`

| Élément | Description |
|---|---|
| Objectif | Stocker les domaines ou URLs des concurrents |
| Colonnes principales | `id`, `competitor_id`, `domain`, `url`, `is_primary`, `created_at` |
| Contraintes | Domaine unique si normalisé et validé |
| Relations | `competitors` |
| Index recommandés | `competitor_id`, `domain`, `is_primary` |
| Règles métier | Un concurrent peut avoir plusieurs domaines |

### 12.4 `website_competitors`

| Élément | Description |
|---|---|
| Objectif | Associer des concurrents à des sites suivis |
| Colonnes principales | `website_id`, `competitor_id`, `priority`, `created_at` |
| Contraintes | unique sur `website_id` + `competitor_id` |
| Relations | `websites`, `competitors` |
| Index recommandés | `website_id`, `competitor_id` |
| Règles métier | La comparaison doit toujours avoir un périmètre clair |

## 13. Domaine SEO

### 13.1 Tables proposées

| Table | Objectif |
|---|---|
| `seo_pages` | Pages ou URLs analysées |
| `seo_queries` | Requêtes observées depuis une source SEO |
| `seo_metrics` | Mesures temporelles de performance |
| `seo_positions` | Positions par mot-clé, page et période |
| `seo_imports` | Imports de données externes |
| `seo_data_sources` | Sources de données éventuelles |

### 13.2 `seo_pages`

| Élément | Description |
|---|---|
| Objectif | Représenter les pages suivies dans un site |
| Colonnes principales | `id`, `website_id`, `url`, `title`, `status_code`, `canonical_url`, `created_at`, `updated_at` |
| Contraintes | `website_id` non nul, URL non nulle |
| Relations | `websites`, `seo_metrics`, `seo_positions` |
| Index recommandés | `website_id`, `url`, `status_code` |
| Règles métier | Une page est rattachée à un site |

### 13.3 `seo_queries`

| Élément | Description |
|---|---|
| Objectif | Stocker des requêtes observées dans les sources SEO |
| Colonnes principales | `id`, `website_id`, `query`, `source`, `created_at` |
| Contraintes | Query non vide |
| Relations | `websites`, `keywords` si rapprochement possible |
| Index recommandés | `website_id`, `query`, `source` |
| Règles métier | La requête observée peut différer d'un mot-clé suivi |

### 13.4 `seo_metrics`

| Élément | Description |
|---|---|
| Objectif | Historiser les indicateurs SEO par site, page ou requête |
| Colonnes principales | `id`, `website_id`, `seo_page_id`, `metric_date`, `metric_name`, `metric_value`, `source`, `created_at` |
| Contraintes | Date, nom et valeur de métrique requis selon type |
| Relations | `websites`, `seo_pages`, sources |
| Index recommandés | `website_id`, `metric_date`, `metric_name`, `source` |
| Règles métier | Les métriques sont append-only autant que possible |

### 13.5 `seo_positions`

| Élément | Description |
|---|---|
| Objectif | Suivre les positions temporelles |
| Colonnes principales | `id`, `keyword_id`, `website_id`, `seo_page_id`, `position`, `observed_at`, `source` |
| Contraintes | Position positive si renseignée, date non nulle |
| Relations | `keywords`, `websites`, `seo_pages` |
| Index recommandés | `keyword_id`, `website_id`, `observed_at`, couple `keyword_id` + `observed_at` |
| Règles métier | Une position n'écrase pas l'historique précédent |

### 13.6 Imports SEO

Les imports SEO doivent stocker :

- source ;
- acteur ;
- date d'import ;
- nombre de lignes traitées ;
- nombre de lignes créées, mises à jour, ignorées ou en erreur ;
- résumé d'erreurs non sensible ;
- métadonnées contrôlées.

## 14. Domaine GEO

### 14.1 Plateformes IA suivies

Les plateformes de référence sont :

- ChatGPT ;
- Gemini ;
- Claude ;
- Copilot ;
- Perplexity.

Le modèle doit permettre l'ajout futur d'une plateforme sans refonte globale.

### 14.2 Tables proposées

| Table | Objectif |
|---|---|
| `ai_platforms` | Référentiel des plateformes IA |
| `geo_queries` | Requêtes ou prompts suivis |
| `geo_results` | Résultats observés par plateforme et date |
| `geo_responses` | Réponses textuelles ou snapshots contrôlés |
| `geo_mentions` | Mentions de marques, sites ou concurrents |
| `geo_citations` | Citations ou sources mentionnées |
| `geo_visibility_scores` | Scores éventuels de visibilité |

### 14.3 `ai_platforms`

| Élément | Description |
|---|---|
| Objectif | Identifier les plateformes IA |
| Colonnes principales | `id`, `code`, `name`, `provider`, `is_active`, `created_at`, `updated_at` |
| Contraintes | `code` unique |
| Relations | `geo_results`, configuration IA |
| Index recommandés | `code`, `is_active`, `provider` |
| Règles métier | Les noms commerciaux sont des libellés, pas des dépendances techniques fortes |

### 14.4 `geo_queries`

| Élément | Description |
|---|---|
| Objectif | Stocker les prompts ou requêtes GEO suivis |
| Colonnes principales | `id`, `website_id`, `keyword_id`, `name`, `prompt`, `intent`, `status`, `created_at`, `updated_at` |
| Contraintes | Prompt non vide, contexte métier recommandé |
| Relations | `websites`, `keywords`, `geo_results` |
| Index recommandés | `website_id`, `keyword_id`, `status`, `intent` |
| Règles métier | Un prompt doit être contextualisé et datable lors des exécutions |

### 14.5 `geo_results`

| Élément | Description |
|---|---|
| Objectif | Historiser un résultat GEO observé |
| Colonnes principales | `id`, `geo_query_id`, `ai_platform_id`, `observed_at`, `status`, `visibility_score`, `metadata`, `created_at` |
| Contraintes | Requête, plateforme et date obligatoires |
| Relations | `geo_queries`, `ai_platforms`, réponses, mentions, citations |
| Index recommandés | `geo_query_id`, `ai_platform_id`, `observed_at`, `status` |
| Règles métier | Une observation ne doit pas être présentée comme vérité permanente |

### 14.6 `geo_responses`

| Élément | Description |
|---|---|
| Objectif | Conserver une réponse observée ou un extrait contrôlé |
| Colonnes principales | `id`, `geo_result_id`, `response_text`, `response_hash`, `language`, `created_at` |
| Contraintes | `geo_result_id` unique si une seule réponse par résultat |
| Relations | `geo_results` |
| Index recommandés | `geo_result_id`, `response_hash` |
| Règles métier | Éviter de stocker des contenus sensibles inutiles |

### 14.7 `geo_mentions` et `geo_citations`

| Table | Objectif | Colonnes principales | Index recommandés |
|---|---|---|---|
| `geo_mentions` | Identifier marques, sites ou concurrents mentionnés | `geo_result_id`, `mention_type`, `website_id`, `competitor_id`, `label`, `position`, `sentiment` | `geo_result_id`, `mention_type`, `website_id`, `competitor_id` |
| `geo_citations` | Identifier les sources citées | `geo_result_id`, `url`, `domain`, `title`, `citation_position` | `geo_result_id`, `domain`, `url` |

Les mentions doivent distinguer :

- marque interne ;
- site interne ;
- concurrent ;
- source externe ;
- mention non classée.

### 14.8 Scores GEO

Les scores GEO sont optionnels. S'ils sont ajoutés, ils doivent préciser :

- méthode ;
- version de méthode ;
- période ;
- plateforme ;
- périmètre ;
- date de calcul.

## 15. Domaine Rapports

### 15.1 Tables proposées

| Table | Objectif |
|---|---|
| `reports` | Rapports métier |
| `report_types` | Types de rapports |
| `report_exports` | Exports produits |
| `report_sections` | Sections ou blocs de rapport futurs |
| `report_generation_jobs` | Suivi futur des générations |

### 15.2 `reports`

| Élément | Description |
|---|---|
| Objectif | Stocker les rapports ou demandes de rapport |
| Colonnes principales | `id`, `title`, `report_type_id`, `website_id`, `period_start`, `period_end`, `status`, `filters`, `created_by_user_id`, `created_at`, `updated_at` |
| Contraintes | Période cohérente, statut contrôlé |
| Relations | `websites`, `users`, exports |
| Index recommandés | `website_id`, `status`, `period_start`, `period_end`, `created_by_user_id` |
| Règles métier | Un rapport doit toujours avoir un périmètre compréhensible |

### 15.3 `report_exports`

| Élément | Description |
|---|---|
| Objectif | Tracer les exports de rapports |
| Colonnes principales | `id`, `report_id`, `format`, `status`, `file_reference`, `exported_by_user_id`, `exported_at` |
| Contraintes | Rapport et format obligatoires |
| Relations | `reports`, `users` |
| Index recommandés | `report_id`, `format`, `status`, `exported_at` |
| Règles métier | Les exports sensibles doivent être auditables |

## 16. Domaine Configuration

### 16.1 Tables proposées

| Table | Objectif |
|---|---|
| `configuration_settings` | Paramètres applicatifs non secrets |
| `configuration_versions` | Versions ou snapshots futurs |
| `configuration_imports` | Historique des imports |
| `configuration_exports` | Historique des exports |
| `api_keys` | Références de clés ou secrets masqués/chiffrés selon stratégie |
| `ai_providers` | Fournisseurs IA |
| `ai_models` | Modèles IA |

### 16.2 `configuration_settings`

| Élément | Description |
|---|---|
| Objectif | Stocker des paramètres non secrets |
| Colonnes principales | `id`, `module`, `key`, `value`, `value_type`, `is_sensitive`, `description`, `updated_by_user_id`, `created_at`, `updated_at` |
| Contraintes | unique sur `module` + `key` |
| Relations | `users` pour modification |
| Index recommandés | `module`, `key`, `is_sensitive` |
| Règles métier | Les valeurs sensibles ne doivent pas être stockées en clair |

### 16.3 Import/export configuration

| Élément | Règle de conception |
|---|---|
| Import | Stocker résumé, statut, acteur, erreurs non sensibles |
| Export | Stocker format, acteur, date, périmètre, exclusion secrets |
| Idempotence | Utiliser `module` + `key` ou `code` comme clé de rapprochement |
| Conflits | Stocker le résultat de résolution sans payload sensible complet |
| Versionnement | Envisager snapshot si besoin de restauration contrôlée |

### 16.4 Fournisseurs et modèles IA

Les tables `ai_providers` et `ai_models` doivent permettre :

- activation/désactivation ;
- nom et code stables ;
- rattachement provider/modèle ;
- paramètres non secrets ;
- coût ou limites futures si validés ;
- compatibilité avec les plateformes GEO.

## 17. Domaine Logs et audit

### 17.1 Tables proposées

| Table | Objectif |
|---|---|
| `application_logs` | Logs techniques et applicatifs |
| `error_logs` | Erreurs normalisées si séparation nécessaire |
| `audit_logs` | Actions sensibles et métier |
| `desktop_error_logs` | Erreurs Desktop remontées si besoin futur |

### 17.2 `application_logs`

| Élément | Description |
|---|---|
| Objectif | Stocker des événements applicatifs utiles |
| Colonnes principales | `id`, `level`, `event_code`, `module`, `message`, `request_id`, `metadata`, `created_at` |
| Contraintes | Niveau et date obligatoires |
| Relations | Utilisateur optionnel si connu |
| Index recommandés | `level`, `module`, `event_code`, `created_at`, `request_id` |
| Règles métier | Aucun secret, token ou payload sensible complet |

### 17.3 `audit_logs`

| Élément | Description |
|---|---|
| Objectif | Conserver les traces durables d'actions sensibles |
| Colonnes principales | `id`, `actor_user_id`, `action`, `resource_type`, `resource_id`, `before`, `after`, `metadata`, `created_at` |
| Contraintes | Action, ressource et date requises selon cas |
| Relations | `users` si acteur identifié |
| Index recommandés | `actor_user_id`, `action`, `resource_type`, `created_at` |
| Règles métier | Append-only, pas de secret dans `before` ou `after` |

### 17.4 Conservation et filtrage

Les logs doivent être filtrables par :

- période ;
- niveau ;
- module ;
- action ;
- acteur ;
- type de ressource ;
- request ID.

La politique de conservation détaillée est future, mais la structure doit permettre une purge
ou un archivage contrôlé.

## 18. Relations principales

| Entité source | Entité cible | Cardinalité | Type de relation | Suppression | Remarque |
|---|---|---|---|---|---|
| `users` | `roles` | N-N | `user_roles` | Supprimer association | Auditer changement |
| `roles` | `permissions` | N-N | `role_permissions` | Supprimer association | Auditer changement |
| `websites` | `keywords` | 1-N | FK | Restreindre ou désactiver | Garder historique |
| `websites` | `contents` | 1-N | FK | Restreindre ou désactiver | Contenus liés au site |
| `contents` | `keywords` | N-N | `content_keywords` | Supprimer association | Pas de destruction des objets |
| `websites` | `competitors` | N-N | `website_competitors` | Supprimer association | Comparaison métier |
| `competitors` | `competitor_domains` | 1-N | FK | Cascade contrôlée possible | Domaine dépendant |
| `websites` | `seo_pages` | 1-N | FK | Restreindre | Historique SEO |
| `keywords` | `seo_positions` | 1-N | FK | Restreindre | Données temporelles |
| `websites` | `geo_queries` | 1-N | FK | Restreindre | Prompts par périmètre |
| `geo_queries` | `geo_results` | 1-N | FK | Restreindre | Historique GEO |
| `ai_platforms` | `geo_results` | 1-N | FK | Restreindre | Plateforme requise |
| `geo_results` | `geo_mentions` | 1-N | FK | Cascade contrôlée | Détail dépendant |
| `geo_results` | `geo_citations` | 1-N | FK | Cascade contrôlée | Détail dépendant |
| `reports` | `report_exports` | 1-N | FK | Restreindre ou cascade contrôlée | Export dépendant |
| `users` | `audit_logs` | 1-N | FK nullable | Set null | Garder audit même si user désactivé |

## 19. Contraintes d'intégrité

### 19.1 Clés primaires

Toutes les tables persistantes doivent avoir une clé primaire stable. Les tables d'association
peuvent utiliser une clé primaire composite ou un identifiant technique selon les besoins de
traçabilité.

### 19.2 Clés étrangères

Les clés étrangères doivent être explicites et indexées lorsque utilisées en filtre ou jointure.
Les suppressions doivent être choisies selon la valeur historique de la donnée.

### 19.3 Nullabilité

| Type de champ | Règle |
|---|---|
| Identifiants de rattachement critiques | Non nullable |
| Libellés métier obligatoires | Non nullable |
| Métadonnées optionnelles | Nullable |
| Auteur ou acteur historique | Nullable si conservation nécessaire |
| Champs futurs | Nullable tant que non obligatoires |

### 19.4 Unicité

| Ressource | Unicité candidate |
|---|---|
| Utilisateur | `email` |
| Rôle | `code` |
| Permission | `code` |
| Site | `url` ou `domain` normalisé |
| Type de site | `code` |
| Catégorie mot-clé | `code` |
| Mot-clé | `website_id` + `keyword` si validé |
| Concurrent domaine | `domain` |
| Plateforme IA | `code` |
| Paramètre configuration | `module` + `key` |

### 19.5 Contraintes métier

Les contraintes métier complexes doivent rester dans les services. La base doit toutefois
renforcer les règles simples et structurelles :

- non-nullité ;
- unicité ;
- intégrité référentielle ;
- contraintes de date simples ;
- contraintes de valeur simple si stable.

## 20. Indexation et performance

### 20.1 Principes

Les index doivent être conçus à partir des usages API et Desktop :

- listes paginées ;
- filtres par site ;
- filtres par période ;
- filtres par statut ;
- recherche par nom ou code ;
- comparaison par plateforme IA ;
- consultation des logs.

### 20.2 Index recommandés par domaine

| Domaine | Index candidats | Justification |
|---|---|---|
| Administration | `users.email`, `roles.code`, `permissions.code` | Connexion, RBAC |
| Sites | `websites.url`, `websites.domain`, `websites.status` | Recherche et filtres |
| Mots-clés | `keywords.website_id`, `keywords.keyword`, `keywords.intent` | Tables SEO |
| Contenus | `contents.website_id`, `contents.status`, `contents.content_type_id` | Suivi éditorial |
| Concurrents | `competitors.status`, `competitor_domains.domain` | Veille |
| SEO | `seo_metrics.website_id`, `seo_metrics.metric_date` | Historique par site |
| GEO | `geo_results.ai_platform_id`, `geo_results.observed_at` | Comparaison IA |
| Rapports | `reports.website_id`, `reports.status`, `reports.period_start` | Consultation |
| Configuration | `configuration_settings.module`, `configuration_settings.key` | Chargement paramètres |
| Logs | `application_logs.created_at`, `application_logs.level` | Filtrage |
| Audit | `audit_logs.actor_user_id`, `audit_logs.resource_type`, `audit_logs.created_at` | Traçabilité |

### 20.3 Index composites

Les index composites recommandés doivent correspondre aux filtres fréquents :

- `website_id` + `status` ;
- `website_id` + `metric_date` ;
- `keyword_id` + `observed_at` ;
- `geo_query_id` + `ai_platform_id` + `observed_at` ;
- `module` + `key` ;
- `resource_type` + `resource_id` ;
- `level` + `created_at`.

## 21. Historisation

### 21.1 Données à historiser

| Donnée | Historisation recommandée | Raison |
|---|---|---|
| Positions SEO | Oui | Suivi temporel |
| Métriques SEO | Oui | Analyse d'évolution |
| Résultats GEO | Oui | Réponses IA variables |
| Mentions GEO | Oui | Comparaison présence/absence |
| Rapports | Oui | Traçabilité décisionnelle |
| Configuration | Partielle | Audit et restauration future |
| Rôles/permissions | Audit | Sécurité |
| Logs | Oui avec conservation | Diagnostic |

### 21.2 Mise à jour vs historique

Les référentiels peuvent être mis à jour :

- sites ;
- mots-clés ;
- contenus ;
- concurrents ;
- rôles ;
- configuration.

Les observations doivent plutôt être ajoutées :

- positions SEO ;
- métriques SEO ;
- réponses GEO ;
- citations GEO ;
- logs ;
- audit.

## 22. Suppression, archivage et désactivation

### 22.1 Règles générales

| Action | Usage recommandé |
|---|---|
| Désactivation | Sites, utilisateurs, concurrents, mots-clés |
| Archivage | Rapports, contenus, anciennes configurations |
| Suppression association | Tables N-N sans valeur historique directe |
| Suppression physique | Données temporaires ou erreurs d'import non persistantes |
| Suppression avec audit | Toute action sensible autorisée |

### 22.2 Conservation des historiques

La désactivation d'un site, mot-clé, concurrent ou utilisateur ne doit pas supprimer les
historiques SEO/GEO, rapports, logs ou audits existants.

### 22.3 Contraintes de suppression

Les FK doivent éviter les suppressions accidentelles de référentiels utilisés par des historiques.
Les cascades doivent être limitées aux détails strictement dépendants, par exemple mentions ou
citations d'un résultat GEO supprimé dans un contexte contrôlé.

## 23. Import/export de configuration

### 23.1 Modèle compatible

Les tables d'import/export doivent stocker :

- acteur ;
- date ;
- statut ;
- version ou format ;
- périmètre ;
- résumé ;
- erreurs non sensibles ;
- nombre d'éléments créés, mis à jour, ignorés ou en conflit.

### 23.2 Idempotence

Un import idempotent s'appuie sur des clés stables :

- `module` + `key` pour configuration ;
- `code` pour rôles, permissions, plateformes IA ;
- identifiants externes validés si présents ;
- empreinte de fichier ou version si utile.

### 23.3 Non-destruction par défaut

Un import ne doit pas :

- supprimer des paramètres absents du fichier ;
- écraser un secret ;
- désactiver massivement des éléments ;
- modifier des rôles système sans validation ;
- masquer des conflits.

### 23.4 Journalisation

Chaque import ou export de configuration doit produire :

- un log applicatif ;
- un audit si l'action est sensible ;
- un résumé consultable ;
- aucun secret en clair.

## 24. Données sensibles et sécurité

### 24.1 Classification

| Donnée | Stockage recommandé | Export | Log | Audit |
|---|---|---|---|---|
| Mot de passe | Hash uniquement | Jamais | Jamais | Événement sans valeur |
| Token session | Hash ou stockage sécurisé futur | Jamais | Jamais | Révocation possible |
| Clé API | Chiffrée/secret store futur, masquée | Jamais en clair | Jamais | Rotation auditée |
| Secret JWT | Hors DB, variable d'environnement | Jamais | Jamais | Changement audit si applicable |
| Prompt GEO sensible | Stockage limité et droits adaptés | Contrôlé | Métadonnées seulement | Selon usage |
| Rapport | DB/fichier contrôlé | Selon permission | Métadonnées | Export audit |
| Logs audit | DB protégée | Contrôlé | Non applicable | Append-only |

### 24.2 Règles mots de passe

Les mots de passe ne doivent jamais être stockés en clair. La table `users` doit stocker un
hash, pas la valeur originale. Les resets futurs doivent utiliser des tokens courts, non
réutilisables et non exposés.

### 24.3 Règles clés API

Les clés API externes ne doivent pas être visibles en clair dans :

- base non chiffrée ;
- logs ;
- audit ;
- exports ;
- réponses API ;
- Desktop.

Une réponse API peut exposer une valeur masquée ou une empreinte non réversible.

## 25. Cohérence SQLAlchemy 2.x

### 25.1 Modèles déclaratifs

Les modèles SQLAlchemy doivent représenter les tables avec les conventions du projet :

- classes en PascalCase ;
- colonnes typées ;
- relations explicites ;
- `Mapped` et `mapped_column()` selon l'architecture existante ;
- cohérence avec les migrations.

### 25.2 Relations

Les relations doivent être définies lorsque cela améliore la lisibilité et la testabilité.
`back_populates` est recommandé lorsqu'une navigation bidirectionnelle est utile.

### 25.3 Lazy loading

Le chargement paresseux doit être utilisé avec prudence. Les repositories doivent choisir les
stratégies de chargement adaptées pour éviter les problèmes N+1 sur les vues Desktop/API.

### 25.4 Responsabilités interdites aux modèles

Les modèles ne doivent pas contenir :

- logique métier complexe ;
- appels API ;
- dépendances Desktop ;
- sérialisation Pydantic ;
- décisions de permission ;
- transformations d'import/export lourdes.

## 26. Cohérence Pydantic v2

### 26.1 Schémas d'entrée

Les schémas d'entrée doivent valider :

- types ;
- formats ;
- longueurs ;
- champs obligatoires ;
- structures d'import ;
- valeurs contrôlées simples.

### 26.2 Schémas de sortie

Les schémas de sortie doivent contrôler :

- champs exposés ;
- absence de secrets ;
- formes paginées ;
- formats de date ;
- cohérence Desktop/React.

### 26.3 Schémas create/update/read

| Schéma | Rôle |
|---|---|
| Create | Champs nécessaires à la création |
| Update | Champs modifiables uniquement |
| Read | Champs exposés au client |
| List | Forme paginée ou résumé |
| Detail | Détail contrôlé d'une ressource |

### 26.4 Cohérence avec la base

Une validation Pydantic ne remplace pas :

- une contrainte unique ;
- une FK ;
- une nullabilité ;
- une contrainte de type ;
- une règle transactionnelle métier.

## 27. Cohérence FastAPI, Desktop et futur React

### 27.1 Contrat API stable

La base doit soutenir des contrats API stables :

- identifiants cohérents ;
- timestamps sérialisables ;
- statuts lisibles ;
- listes paginées ;
- filtres applicables côté repository ;
- erreurs différenciables.

### 27.2 Desktop PySide6

Le Desktop doit consommer les données via FastAPI uniquement. La conception de base ne doit
jamais supposer :

- connexion directe Desktop à PostgreSQL ;
- lecture de tables depuis PySide6 ;
- logique métier côté Desktop ;
- secret accessible au client.

### 27.3 Futur React

Le futur React réutilisera les mêmes contrats REST. Les tables doivent donc soutenir :

- pagination standard ;
- filtres explicites ;
- tri contrôlé ;
- statuts cohérents ;
- erreurs standardisées ;
- permissions côté API.

## 28. Exigences Alembic

### 28.1 Principes obligatoires

Les migrations Alembic doivent être :

- versionnées ;
- lisibles ;
- explicites ;
- relues ;
- réversibles lorsque possible ;
- cohérentes avec les modèles SQLAlchemy ;
- adaptées à PostgreSQL.

### 28.2 Instructions explicites

Les migrations doivent utiliser des opérations explicites comme :

- `op.create_table(...)` ;
- `op.drop_table(...)` ;
- `op.create_index(...)` ;
- `op.drop_index(...)` ;
- création explicite de clés primaires ;
- création explicite de contraintes uniques ;
- création explicite de contraintes étrangères ;
- définition explicite de nullabilité ;
- création explicite d'index nécessaires.

### 28.3 Interdictions

Les migrations Alembic ne doivent jamais utiliser :

- `Base.metadata.create_all()` ;
- `Base.metadata.drop_all()`.

Ces appels contournent l'historique de migration et rendent l'évolution de structure trop
opaque.

### 28.4 Ordre de création

L'ordre recommandé est :

1. tables référentielles ;
2. tables principales ;
3. tables d'association ;
4. tables historiques ;
5. index ;
6. contraintes complémentaires si non créées avec la table.

L'ordre de suppression doit suivre l'ordre inverse en tenant compte des clés étrangères.

### 28.5 Vérifications après migration

Après une migration, les vérifications attendues sont :

- cohérence avec les modèles SQLAlchemy ;
- absence de secret dans les données initiales ;
- index nécessaires présents ;
- contraintes uniques et FK présentes ;
- tests disponibles exécutés ;
- migration relue avant PR.

## 29. Table de proposition des entités principales

| Domaine | Table proposée | Rôle | Priorité | Dépendances | Remarques |
|---|---|---|---|---|---|
| Administration | `users` | Comptes internes | Critique | Aucune | Hash mot de passe uniquement |
| Administration | `roles` | Profils d'accès | Critique | Aucune | Codes uniques |
| Administration | `permissions` | Droits fins | Critique | Aucune | Codes uniques |
| Administration | `user_roles` | Association comptes/rôles | Critique | `users`, `roles` | Audit au service |
| Administration | `role_permissions` | Association rôles/droits | Critique | `roles`, `permissions` | Audit au service |
| Sites | `websites` | Référentiel sites | Critique | `website_types` optionnel | URL unique |
| Sites | `website_types` | Typologie | Secondaire | Aucune | À créer si besoin réel |
| Mots-clés | `keywords` | Requêtes suivies | Haute | `websites` | Filtres SEO/GEO |
| Mots-clés | `keyword_categories` | Catégories | Moyenne | Aucune | Codes uniques |
| Mots-clés | `keyword_metrics` | Historique métriques | Future | `keywords` | Append-only |
| Contenus | `contents` | Fiches éditoriales | Haute | `websites`, `users` | Pas un CMS |
| Contenus | `content_keywords` | Association SEO éditoriale | Haute | `contents`, `keywords` | Couple unique |
| Concurrents | `competitors` | Acteurs suivis | Haute | Aucune | Actif/inactif |
| Concurrents | `competitor_domains` | Domaines suivis | Haute | `competitors` | Domaine indexé |
| Concurrents | `website_competitors` | Comparaison par site | Haute | `websites`, `competitors` | Couple unique |
| SEO | `seo_pages` | Pages suivies | Haute | `websites` | URL indexée |
| SEO | `seo_metrics` | Mesures SEO | Haute | `websites`, `seo_pages` | Date indexée |
| SEO | `seo_positions` | Positions | Haute | `keywords`, `websites` | Historique |
| GEO | `ai_platforms` | Plateformes IA | Critique | Aucune | ChatGPT, Gemini, Claude, Copilot, Perplexity |
| GEO | `geo_queries` | Prompts suivis | Critique | `websites`, `keywords` | Prompt texte |
| GEO | `geo_results` | Observations GEO | Critique | `geo_queries`, `ai_platforms` | Date obligatoire |
| GEO | `geo_mentions` | Mentions marque/site/concurrent | Haute | `geo_results` | Analyse comparative |
| GEO | `geo_citations` | Sources citées | Moyenne | `geo_results` | URL/domain |
| Rapports | `reports` | Rapports | Haute | `websites`, `users` | Période |
| Rapports | `report_exports` | Exports | Moyenne | `reports`, `users` | Audit export |
| Configuration | `configuration_settings` | Paramètres | Critique | `users` optionnel | Pas de secret clair |
| Configuration | `configuration_imports` | Imports | Haute | `users` | Résumé non sensible |
| Configuration | `configuration_exports` | Exports | Haute | `users` | Secrets exclus |
| Logs | `application_logs` | Logs applicatifs | Haute | `users` optionnel | Sans secrets |
| Audit | `audit_logs` | Actions sensibles | Critique | `users` optionnel | Append-only |

## 30. Matrice de criticité des données

| Type de donnée | Criticité | Confidentialité | Historisation | Audit | Stratégie recommandée |
|---|---|---|---|---|---|
| Mots de passe | Critique | Très élevée | Non | Événement seulement | Hash, jamais clair |
| Clés API | Critique | Très élevée | Rotation | Oui | Masquage/chiffrement/secret store futur |
| Rôles et permissions | Critique | Élevée | Audit | Oui | Codes uniques, modifications tracées |
| Sites web | Haute | Moyenne | Statut | Oui si action sensible | Désactivation |
| Mots-clés | Haute | Moyenne | Métriques | Selon action | Unicité contrôlée |
| Contenus | Haute | Moyenne | Statuts/versions futures | Selon action | Rattachement site |
| Concurrents | Moyenne | Moyenne | Statut | Selon action | Actif/inactif |
| Métriques SEO | Haute | Moyenne | Oui | Non systématique | Append-only daté |
| Résultats GEO | Haute | Élevée | Oui | Selon action | Datés et contextualisés |
| Rapports | Haute | Élevée | Oui | Export audit | Périmètre et période |
| Configuration | Critique | Variable | Version future | Oui | Non destructif |
| Logs techniques | Moyenne | Élevée | Conservation | Non | Sans secrets |
| Audit | Critique | Élevée | Oui | Natif | Append-only |

## 31. Matrice d'indexation

| Usage | Colonnes candidates | Type d'index | Justification | Priorité |
|---|---|---|---|---|
| Connexion utilisateur | `users.email` | Unique | Recherche par email | Critique |
| Résolution RBAC | `roles.code`, `permissions.code` | Unique | Droits stables | Critique |
| Liste sites | `websites.status`, `websites.is_active` | Simple/composite | Filtres Desktop | Critique |
| Recherche site | `websites.domain`, `websites.url` | Unique ou simple | Prévention doublons | Critique |
| Liste mots-clés | `keywords.website_id`, `keywords.status` | Composite | Filtre par site | Haute |
| Recherche mot-clé | `keywords.keyword` | Simple ou trigram futur | Recherche textuelle | Moyenne |
| Métriques SEO | `seo_metrics.website_id`, `seo_metrics.metric_date` | Composite | Séries temporelles | Haute |
| Positions SEO | `seo_positions.keyword_id`, `seo_positions.observed_at` | Composite | Historique position | Haute |
| Résultats GEO | `geo_results.geo_query_id`, `geo_results.ai_platform_id`, `geo_results.observed_at` | Composite | Comparaison IA | Haute |
| Mentions GEO | `geo_mentions.website_id`, `geo_mentions.competitor_id` | Simple | Présence marque/concurrent | Haute |
| Rapports | `reports.website_id`, `reports.status`, `reports.period_start` | Composite | Filtres rapports | Moyenne |
| Configuration | `configuration_settings.module`, `configuration_settings.key` | Unique composite | Idempotence | Critique |
| Logs | `application_logs.level`, `application_logs.created_at` | Composite | Filtrage logs | Haute |
| Audit | `audit_logs.resource_type`, `audit_logs.resource_id` | Composite | Recherche par ressource | Haute |

## 32. Règles de validation des données

### 32.1 Trois niveaux de validation

| Niveau | Responsabilité | Exemple |
|---|---|---|
| Pydantic | Forme, types, champs requis | URL valide, date présente |
| Service | Règles métier | Pas de doublon actif, permission, statut autorisé |
| Base PostgreSQL | Intégrité finale | FK, unique, not null, check simple |

### 32.2 Cohérence attendue

Une règle critique doit être protégée à plusieurs niveaux lorsque possible :

- Pydantic rejette les payloads invalides ;
- service vérifie la cohérence métier ;
- repository applique les requêtes SQLAlchemy ;
- PostgreSQL garantit l'intégrité structurelle.

### 32.3 Exemples conceptuels

| Exemple | Validation Pydantic | Validation service | Contrainte base |
|---|---|---|---|
| Création site | URL présente | URL normalisée non déjà active | unique URL/domain |
| Création mot-clé | Texte non vide | Pas de doublon pour site | unique possible `website_id` + `keyword` |
| Import config | Structure conforme | Non destructif, droits admin | unique `module` + `key` |
| Résultat GEO | Plateforme et date présentes | Prompt actif et plateforme autorisée | FK vers `geo_queries` et `ai_platforms` |
| Export rapport | Format valide | Permission export | FK vers rapport et utilisateur |

## 33. Risques de conception

### 33.1 Matrice des risques

| Risque | Impact | Prévention |
|---|---|---|
| Sur-normalisation | Modèle difficile à utiliser | Normaliser les référentiels stables, simplifier le reste |
| Sous-normalisation | Données incohérentes | FK et tables d'association pour relations fortes |
| Volumétrie SEO/GEO | Lenteurs | Index, pagination, archivage futur |
| JSONB excessif | Requêtes difficiles, contraintes faibles | Relationnel par défaut |
| Index insuffisants | API lente | Index sur filtres et jointures |
| Trop d'index | Écritures ralenties | Index justifiés par usages |
| Suppression destructrice | Perte historique | Soft delete, restrictions FK |
| Secrets dans logs | Fuite sécurité | Allowlist et masquage |
| Dette de migration | Déploiements fragiles | Alembic explicite et revue |
| Divergence model/migration | Bugs runtime | Revue croisée modèle/migration |

### 33.2 Points de vigilance

- Ne pas créer de tables génériques capables de tout stocker sans contraintes.
- Ne pas utiliser JSONB pour des données filtrées tous les jours.
- Ne pas exposer les IDs internes comme seule garantie de sécurité.
- Ne pas créer d'accès direct DB pour Desktop ou futur React.
- Ne pas stocker les réponses IA sensibles sans besoin clair.
- Ne pas oublier les dates sur les observations SEO/GEO.

## 34. Hors périmètre de ce document

Ce document ne crée pas :

- migrations Alembic ;
- modèles SQLAlchemy ;
- repositories ;
- routes FastAPI ;
- schémas Pydantic ;
- endpoints ;
- tests ;
- scripts d'import ;
- scripts de seed ;
- données initiales ;
- configuration de production ;
- schéma SQL complet.

Il ne remplace pas :

- `DATABASE_ARCHITECTURE.md` ;
- la future roadmap ;
- les documents API ;
- les migrations réelles ;
- les décisions de sécurité de production.

## 35. Synthèse finale

La conception de données de **Veille SEO-GEO Groupe A.P&Partner** doit soutenir une plateforme
interne modulaire, traçable, sécurisée et évolutive.

Les principes à respecter sont :

- PostgreSQL comme source persistante ;
- SQLAlchemy 2.x comme représentation applicative ;
- Alembic comme historique explicite des évolutions ;
- repositories comme seule couche d'accès aux données ;
- services comme lieu des règles métier ;
- Pydantic comme contrat API ;
- Desktop et futur React comme clients HTTP REST uniquement ;
- relationnel par défaut, JSONB seulement si justifié ;
- soft delete ou désactivation pour les référentiels importants ;
- historique append-only pour les observations SEO/GEO ;
- logs et audit sans secrets.

La prochaine étape logique sera de transformer cette conception en roadmap de développement,
puis en migrations Alembic explicites, modèles SQLAlchemy, repositories, services, schémas
Pydantic et tests ciblés, dans l'ordre défini par les priorités projet.

## 36. Annexes conceptuelles

### 36.1 Exemple conceptuel : création d'un site

Un site créé dans `websites` fournit l'identifiant de rattachement aux mots-clés, contenus,
pages SEO, prompts GEO et rapports. La contrainte d'unicité sur URL ou domaine évite les
doublons fonctionnels.

### 36.2 Exemple conceptuel : observation SEO

Une position SEO est ajoutée dans une table temporelle avec une date d'observation. Elle ne
remplace pas la position précédente afin de préserver l'évolution historique.

### 36.3 Exemple conceptuel : résultat GEO

Une requête GEO est exécutée ou observée sur ChatGPT, Gemini, Claude, Copilot ou Perplexity.
Le résultat stocke la plateforme, la date, le statut, la réponse éventuelle, les mentions et
les citations identifiées.

### 36.4 Exemple conceptuel : import de configuration

Un import de configuration rapproche les paramètres par `module` + `key`, met à jour uniquement
les éléments validés, ignore les secrets bruts, journalise le résumé et produit un audit.

### 36.5 Exemple conceptuel : export de rapport

Un export de rapport est rattaché à `reports`, à l'utilisateur ayant lancé l'action et au format
produit. L'audit conserve les métadonnées de l'export sans stocker le contenu complet dans les logs.
