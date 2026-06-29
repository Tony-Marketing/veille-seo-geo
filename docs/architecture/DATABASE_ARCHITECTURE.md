# Software Database Architecture Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Document : Architecture officielle base de données  
Version du document : 1.0  
Statut : Référence technique PostgreSQL, SQLAlchemy et Alembic  
Périmètre : tables, modèles, repositories, relations, contraintes, index, migrations, intégrité, performance et sécurité  

---

## Table des matières

1. [Présentation](#1-présentation)
2. [Principes d'architecture database](#2-principes-darchitecture-database)
3. [Vue d'ensemble de l'architecture database](#3-vue-densemble-de-larchitecture-database)
4. [Arborescence liée à la base de données](#4-arborescence-liée-à-la-base-de-données)
5. [PostgreSQL](#5-postgresql)
6. [SQLAlchemy 2.x](#6-sqlalchemy-2x)
7. [Alembic](#7-alembic)
8. [Convention de nommage des tables](#8-convention-de-nommage-des-tables)
9. [Convention de nommage des colonnes](#9-convention-de-nommage-des-colonnes)
10. [Clés primaires](#10-clés-primaires)
11. [Clés étrangères et relations](#11-clés-étrangères-et-relations)
12. [Contraintes](#12-contraintes)
13. [Index](#13-index)
14. [Timestamps et audit](#14-timestamps-et-audit)
15. [Soft delete vs hard delete](#15-soft-delete-vs-hard-delete)
16. [Transactions](#16-transactions)
17. [Sessions SQLAlchemy](#17-sessions-sqlalchemy)
18. [Modèles existants](#18-modèles-existants)
19. [Modèles futurs](#19-modèles-futurs)
20. [Schéma relationnel cible](#20-schéma-relationnel-cible)
21. [Pagination et performance database](#21-pagination-et-performance-database)
22. [Recherche et full-text futur](#22-recherche-et-full-text-futur)
23. [JSON / JSONB futur](#23-json--jsonb-futur)
24. [Données sensibles](#24-données-sensibles)
25. [Configuration et paramètres](#25-configuration-et-paramètres)
26. [Migrations de données](#26-migrations-de-données)
27. [Tests database](#27-tests-database)
28. [Performance PostgreSQL](#28-performance-postgresql)
29. [Sécurité database](#29-sécurité-database)
30. [Sauvegardes et restauration](#30-sauvegardes-et-restauration)
31. [Anti-patterns interdits](#31-anti-patterns-interdits)
32. [Pattern officiel pour créer une nouvelle table](#32-pattern-officiel-pour-créer-une-nouvelle-table)
33. [Checklist avant Pull Request database](#33-checklist-avant-pull-request-database)
34. [Roadmap database](#34-roadmap-database)
35. [Annexes](#35-annexes)

---

## 1. Présentation

### 1.1 Rôle de la base de données

La base PostgreSQL est la source persistante des données métier de Veille SEO-GEO Groupe A.P&Partner. Elle conserve les
utilisateurs, rôles, permissions, entités, sites web, paramètres, fournisseurs IA, modèles IA, logs, et les futurs
objets SEO, GEO, crawler, prompts, rapports, contenus et performances.

La base ne doit jamais être accédée directement par le Desktop. Les accès passent exclusivement par le backend FastAPI,
puis par les services métier et les repositories SQLAlchemy.

### 1.2 Place de PostgreSQL dans l'écosystème global

```text
Desktop PySide6
      |
      | HTTP REST / JSON
      v
FastAPI Routes
      |
      v
Services métier
      |
      v
Repositories
      |
      v
SQLAlchemy Session
      |
      v
PostgreSQL
```

PostgreSQL n'est pas seulement un stockage. Il est un garant d'intégrité : contraintes uniques, clés étrangères,
nullabilité, index et transactions protègent la cohérence des données.

### 1.3 Objectifs techniques

| Objectif | Description | Impact |
|---|---|---|
| Cohérence | Modèles, migrations et schémas alignés | Moins de dette |
| Intégrité | Contraintes DB explicites | Données fiables |
| Performance | Index conçus avec les usages API | Réponses rapides |
| Maintenabilité | Tables nommées et documentées | Évolution v1.0 |
| Sécurité | Secrets protégés, accès backend uniquement | Surface réduite |
| Auditabilité | Historique et logs futurs | Traçabilité |
| Réversibilité | Downgrades Alembic cohérents | Déploiements maîtrisés |

### 1.4 Objectifs d'intégrité

L'intégrité doit être assurée à plusieurs niveaux :

| Niveau | Rôle |
|---|---|
| Pydantic | Valider la forme entrante |
| Service | Appliquer les règles métier |
| Repository | Construire les accès cohérents |
| SQLAlchemy Model | Représenter colonnes et relations |
| PostgreSQL | Garantir contraintes finales |
| Alembic | Versionner les changements |

### 1.5 Objectifs de performance

- Toutes les grandes listes doivent être paginées.
- Les colonnes utilisées en filtre ou jointure doivent être indexées si la volumétrie le justifie.
- Les clés étrangères doivent être pensées pour les lectures fréquentes.
- Les requêtes N+1 doivent être évitées.
- Les logs et résultats crawler/GEO doivent prévoir archivage ou partitionnement futur.

### 1.6 Contraintes

| Contrainte | Règle |
|---|---|
| Desktop | Aucun accès PostgreSQL |
| Routes | Aucune requête SQLAlchemy directe |
| Repositories | Seule couche d'accès SQLAlchemy |
| Migrations | Opérations Alembic explicites |
| Models | Cohérents avec migrations |
| Données sensibles | Jamais stockées en clair si secret |
| Suppressions | Contrôlées, auditables, non destructives par défaut |

### 1.7 Principes directeurs

1. La base est versionnée par migrations explicites.
2. Les modèles SQLAlchemy reflètent les tables, ils ne remplacent pas les migrations.
3. Les repositories sont la frontière d'accès aux données.
4. Les contraintes importantes appartiennent aussi à PostgreSQL.
5. Les index sont conçus selon les endpoints API.
6. Les suppressions destructives sont exceptionnelles.
7. Par défaut, relationnel avant JSONB.

---

## 2. Principes d'architecture database

### 2.1 Tableau des principes

| Principe | Raison | Application dans le projet | Anti-pattern associé |
|---|---|---|---|
| PostgreSQL relationnel principal | Intégrité et requêtes robustes | Tables normalisées | Tout stocker en JSONB |
| SQLAlchemy comme ORM | Abstraction Python typée | Models + repositories | SQL brut dispersé |
| Alembic pour migrations | Historique contrôlé | `op.create_table` explicite | `create_all()` en migration |
| Models persistants | Représenter tables | `backend/app/models/` | Logique métier dans model |
| Repositories accès DB | Couche unique SQLAlchemy | `backend/app/repositories/` | SQLAlchemy dans routes |
| Contraintes fortes | Prévenir données invalides | unique, FK, nullable | Validation UI seulement |
| Index dès conception | Performance API | FK, dates, recherche | Ajouter index trop tard |
| Cohérence models/migrations | Éviter divergence | revue PR | Model modifié sans migration |
| Sécurité données | Protéger secrets | hash, masquage | clés API en clair |
| Auditabilité future | Traçabilité | audit_logs, timestamps | actions non tracées |

### 2.2 Règle de frontière

```text
Route FastAPI
  |
  +-- Interdit : session.query(...)
  |
  v
Service
  |
  +-- orchestre
  |
  v
Repository
  |
  +-- autorisé : SQLAlchemy
```

### 2.3 Cohérence avec les autres documents

| Document | Relation database |
|---|---|
| `BACKEND_ARCHITECTURE.md` | Définit les couches et responsabilités |
| `API_ARCHITECTURE.md` | Définit pagination, filtres et erreurs consommant la DB |
| `AUTHENTICATION.md` | Définit users, roles, permissions, refresh_tokens, audit |
| `DESKTOP_ARCHITECTURE.md` | Rappelle l'interdiction d'accès DB depuis Desktop |
| `UI_UX.md` | Influence les besoins de tables, filtres, logs et états |

---

## 3. Vue d'ensemble de l'architecture database

### 3.1 Diagramme minimal

```text
FastAPI Service
      |
      v
Repository
      |
      v
SQLAlchemy Session
      |
      v
SQLAlchemy Model
      |
      v
PostgreSQL Table
```

### 3.2 Vue logique

```text
Domain data
  |
  +-- Administration
  +-- Websites / Entities
  +-- Keywords / Competitors
  +-- SEO / URLs / Contents
  +-- GEO / AI / Prompts
  +-- Reports
  +-- Logs / Audit
  +-- Configuration

Persistence architecture
  |
  +-- SQLAlchemy models
  +-- Alembic migrations
  +-- PostgreSQL constraints
  +-- PostgreSQL indexes
```

### 3.3 Vue physique

```text
Backend Python process
  |
  v
SQLAlchemy Engine
  |
  v
Connection pool
  |
  v
PostgreSQL database
  |
  +-- public schema
  +-- application tables
  +-- indexes
  +-- constraints
  +-- alembic_version
```

### 3.4 Vue par responsabilités

| Élément | Responsabilité |
|---|---|
| Service | Règles métier et transaction métier |
| Repository | Requêtes SQLAlchemy |
| Session | Unité de travail |
| Model | Mapping table Python |
| Migration | Changement structurel explicite |
| PostgreSQL | Intégrité, contraintes, stockage |

### 3.5 Cycle transactionnel

```text
Service use case
      |
      v
Open request-scoped session
      |
      v
Repository reads/writes
      |
      v
Flush if needed
      |
      v
Commit
      |
      +-- success -> return response
      |
      +-- error -> rollback -> mapped error
```

### 3.6 Lien models, repositories et migrations

```text
Alembic migration
      |
      | crée / modifie structure réelle
      v
PostgreSQL table
      ^
      | doit rester alignée
      |
SQLAlchemy model
      ^
      |
Repository queries model
```

---

## 4. Arborescence liée à la base de données

### 4.1 Emplacements

```text
backend/app/models/
backend/app/repositories/
backend/app/schemas/
backend/app/services/
backend/alembic/
backend/alembic/versions/
tests/
```

### 4.2 Tableau des dossiers

| Dossier | Rôle | Peut contenir | Ne doit jamais contenir |
|---|---|---|---|
| `backend/app/models/` | Mapping SQLAlchemy | tables, relations, contraintes ORM | routes, Pydantic API |
| `backend/app/repositories/` | Accès données | requêtes SQLAlchemy, pagination DB | logique HTTP, UI |
| `backend/app/schemas/` | Contrats API | Pydantic create/update/read | session SQLAlchemy |
| `backend/app/services/` | Métier | règles, orchestration, transactions | SQL brut dispersé |
| `backend/alembic/` | Configuration migrations | `env.py`, versions | modèles métier |
| `backend/alembic/versions/` | Scripts migration | `op.create_table`, index, FK | `Base.metadata.create_all()` |
| `tests/` | Validation | fixtures, tests API/services | données prod réelles |

### 4.3 Conventions associées

- Toute table persistante doit avoir un modèle SQLAlchemy.
- Toute modification structurelle doit avoir une migration Alembic.
- Tout accès DB applicatif doit passer par un repository.
- Les schemas Pydantic ne doivent pas remplacer les contraintes DB.

---

## 5. PostgreSQL

### 5.1 Rôle

PostgreSQL fournit :

- stockage relationnel ;
- transactions ACID ;
- contraintes ;
- index ;
- JSONB si justifié ;
- recherche full-text future ;
- intégrité référentielle.

### 5.2 Types recommandés

| Besoin | Type PostgreSQL recommandé | Type SQLAlchemy associé | Remarques |
|---|---|---|---|
| Identifiant entier | `integer` / `bigint` | `Integer`, `BigInteger` | Standard actuel possible |
| Identifiant futur global | `uuid` | `UUID` | Utile pour sessions/tokens |
| Texte court | `varchar(n)` | `String(n)` | Ajouter longueur |
| Texte long | `text` | `Text` | Contenu, logs |
| Booléen | `boolean` | `Boolean` | `is_active` |
| Date/heure | `timestamp with time zone` | `DateTime(timezone=True)` | Recommandé |
| Nombre décimal | `numeric(p,s)` | `Numeric` | Coûts IA |
| JSON structuré | `jsonb` | `JSON`/dialect JSONB | Seulement justifié |
| Enum | `varchar` ou enum PG | `Enum`/`String` | Prudence migrations |
| URL | `varchar(255/500)` | `String` | Index selon usage |

### 5.3 Timestamps

Les tables métier doivent prévoir :

- `created_at` ;
- `updated_at` ;
- `deleted_at` si soft delete.

### 5.4 Transactions

Les transactions doivent être courtes. Les opérations longues comme crawler, import massif ou génération rapport doivent
être découpées en jobs et états persistants.

### 5.5 Intégrité référentielle

Les clés étrangères doivent protéger :

- sites liés aux entités ;
- mots-clés liés aux sites/entités ;
- résultats GEO liés aux prompts et modèles IA ;
- rapports liés aux entités et périodes ;
- logs liés aux utilisateurs si applicable.

---

## 6. SQLAlchemy 2.x

### 6.1 Rôle

SQLAlchemy représente les tables en Python et permet aux repositories de construire des requêtes robustes sans disperser
de SQL brut dans l'application.

### 6.2 Concepts

| Concept | Usage |
|---|---|
| Declarative model | Classe représentant une table |
| Column | Colonne persistante |
| ForeignKey | Relation DB |
| relationship | Navigation ORM |
| Index | Performance |
| UniqueConstraint | Unicité |
| Session | Unité de travail |

### 6.3 Exemple conceptuel de modèle propre

```python
class Website(Base):
    """Site web suivi par la plateforme."""

    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    url = Column(String(255), nullable=False, unique=True, index=True)
    cms = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
```

### 6.4 Séparation models/repositories

Le modèle décrit la structure. Le repository exécute les requêtes.

```text
Model
  |
  +-- colonnes
  +-- relations
  +-- contraintes ORM

Repository
  |
  +-- select
  +-- filters
  +-- pagination
  +-- create/update/delete
```

### 6.5 Erreurs à éviter

- Méthodes métier lourdes dans les modèles.
- Relations sans réflexion sur `ondelete`.
- Colonnes nullable par facilité.
- Modèle modifié sans migration.
- Index défini uniquement dans le modèle mais absent de migration.

---

## 7. Alembic

### 7.1 Rôle

Alembic versionne les changements de structure PostgreSQL. Il est la source d'historique des évolutions de base.

### 7.2 Structure d'une migration

```text
revision = "..."
down_revision = "..."

def upgrade():
    op.create_table(...)
    op.create_index(...)

def downgrade():
    op.drop_index(...)
    op.drop_table(...)
```

### 7.3 Interdiction absolue en migration

Les migrations Alembic ne doivent jamais utiliser :

```python
Base.metadata.create_all()
Base.metadata.drop_all()
```

Elles doivent utiliser :

```python
op.create_table(...)
op.drop_table(...)
op.create_index(...)
op.drop_index(...)
```

Ces appels `Base.metadata.create_all()` peuvent être acceptables uniquement dans les tests, par exemple dans
`tests/conftest.py`, pour construire un schéma isolé de test. Ils restent interdits dans `backend/alembic/versions/`.

### 7.4 Exemple conceptuel Alembic

```python
def upgrade() -> None:
    op.create_table(
        "websites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("url", name="uq_websites_url"),
    )
    op.create_index("ix_websites_entity_id", "websites", ["entity_id"])
    op.create_index("ix_websites_is_active", "websites", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_websites_is_active", table_name="websites")
    op.drop_index("ix_websites_entity_id", table_name="websites")
    op.drop_table("websites")
```

### 7.5 Checklist Alembic

| Contrôle | OK |
|---|---|
| `revision` défini | |
| `down_revision` correct | |
| `upgrade()` explicite | |
| `downgrade()` explicite | |
| Pas de `Base.metadata.create_all()` | |
| Pas de `Base.metadata.drop_all()` | |
| Contraintes nommées | |
| Index créés explicitement | |
| FK avec `ondelete` réfléchi | |
| Nullabilité volontaire | |
| Données initiales justifiées | |
| Downgrade non destructeur au-delà du nécessaire | |

---

## 8. Convention de nommage des tables

### 8.1 Règles

- Noms en anglais.
- `snake_case`.
- Noms explicites.
- Pluriel recommandé pour collections.
- Tables pivot nommées avec les deux ressources.
- Pas de préfixes techniques inutiles.

### 8.2 Tableau

| Type de table | Convention | Exemple correct | Exemple interdit |
|---|---|---|---|
| Ressource métier | pluriel snake_case | `websites` | `tblWebsite` |
| Pivot N-N | `<left>_<right>` | `role_permissions` | `rolesPerms` |
| Logs | suffixe `_logs` | `audit_logs` | `log1` |
| Jobs | suffixe `_jobs` | `crawler_jobs` | `crawler_queue_tmp` |
| Résultats | suffixe `_results` | `geo_results` | `data_json` |
| Paramètres | nom explicite | `settings` | `config_table` |

### 8.3 Tables actuelles et futures

| Domaine | Tables |
|---|---|
| Administration | `users`, `roles`, `permissions`, `settings` |
| Websites | `entities`, `websites`, `urls` |
| SEO | `keywords`, `seo_audits`, `seo_recommendations` |
| GEO | `geo_queries`, `geo_results`, `prompts` |
| IA | `ai_providers`, `ai_models`, `prompt_runs` |
| Reports | `reports`, `report_exports` |
| Logs | `audit_logs`, `error_logs`, `login_history` |

---

## 9. Convention de nommage des colonnes

### 9.1 Tableau détaillé

| Colonne | Usage | Convention |
|---|---|---|
| `id` | Clé primaire | Toujours `id` |
| `created_at` | Création | timestamp timezone |
| `updated_at` | Modification | timestamp timezone |
| `deleted_at` | Soft delete futur | nullable |
| `created_by` | Audit futur | FK user nullable |
| `updated_by` | Audit futur | FK user nullable |
| `is_active` | Activation | bool non nullable |
| `name` | Nom lisible | varchar borné |
| `slug` | Identifiant lisible URL | unique si utilisé |
| `url` | URL site/page | varchar borné, unique selon contexte |
| `entity_id` | FK entité | `<resource>_id` |
| `website_id` | FK website | index recommandé |
| `metadata` | Métadonnées JSON futures | JSONB si justifié |

### 9.2 Booléens

Les booléens doivent commencer par :

- `is_` ;
- `has_` ;
- `can_` si capacité.

Exemples :

```text
is_active
is_system
has_errors
```

### 9.3 Dates

| Besoin | Convention |
|---|---|
| Début | `started_at` |
| Fin | `finished_at` |
| Expiration | `expires_at` |
| Révocation | `revoked_at` |
| Dernière utilisation | `last_used_at` |

---

## 10. Clés primaires

### 10.1 Recommandation actuelle

Pour les tables métier simples, une clé primaire entière auto-incrémentée reste acceptable et cohérente avec les
modules existants.

### 10.2 UUID futur

Les UUID sont recommandés pour :

- sessions ;
- refresh tokens ;
- jobs publics ;
- exports ;
- objets dont l'identifiant ne doit pas être devinable ;
- intégrations futures.

### 10.3 Comparaison

| Type | Avantages | Limites | Usage recommandé |
|---|---|---|---|
| Integer | Simple, compact, performant | Devinable | Tables métier internes |
| BigInteger | Plus grande capacité | Plus lourd | Volumétrie élevée |
| UUID | Non séquentiel, intégration facile | Plus volumineux | Sessions, tokens, jobs |

### 10.4 Implications API/Desktop

Le Desktop ne doit pas supposer qu'un identifiant est toujours un entier. Les contrats Pydantic doivent définir le type
par ressource.

---

## 11. Clés étrangères et relations

### 11.1 Types de relations

```text
1-N : Entity -> Websites
N-N : Roles <-> Permissions
1-N : Website -> URLs futures
1-N : Prompt -> PromptRuns futures
```

### 11.2 Exemple existant

```text
websites.entity_id -> entities.id
ondelete="SET NULL"
```

Cette règle permet de conserver un site si l'entité est supprimée ou détachée, tout en indiquant que le lien n'existe
plus.

### 11.3 Tableau `ondelete`

| Cas | ondelete recommandé | Exemple | Risque |
|---|---|---|---|
| Parent supprimé mais enfant conservable | `SET NULL` | website -> entity | Orphelins contrôlés |
| Enfant sans parent invalide | `CASCADE` avec prudence | role_permissions -> roles | Suppression massive |
| Suppression parent interdite si enfants | `RESTRICT` | user avec audit_logs | Blocage nécessaire |
| Historique à préserver | `SET NULL` ou `RESTRICT` | audit_logs -> users | Perte audit si cascade |

### 11.4 Tables pivot

Les tables N-N doivent avoir :

- FK vers les deux tables ;
- contrainte unique composite ;
- index sur chaque FK ;
- timestamps si attribution auditée.

---

## 12. Contraintes

### 12.1 Types

| Contrainte | Usage |
|---|---|
| Primary key | Identité ligne |
| Unique | Unicité métier |
| Foreign key | Intégrité relationnelle |
| Not null | Donnée obligatoire |
| Check | Règle simple DB |
| Exclusion future | Contraintes de période avancées |

### 12.2 Matrice responsabilités

| Règle | Database | Service | Pydantic | Commentaire |
|---|---:|---:|---:|---|
| URL non vide | Oui | Oui | Oui | Défense en profondeur |
| URL unique website | Oui | Oui | Non | Service pour message propre |
| `page_size <= 100` | Non | Non | Oui | Paramètre API |
| Suppression dernier admin | Non | Oui | Non | Règle métier |
| FK entity valide | Oui | Oui | Non | DB garantit |
| Email format | Non | Non | Oui | Validation entrée |
| Hash mot de passe présent | Oui | Oui | Non | Sécurité |

### 12.3 Contraintes métier simples

Une contrainte DB est adaptée si :

- la règle est stable ;
- la règle est locale à une table ;
- la règle protège une incohérence grave.

Exemple : `url` unique dans `websites`.

---

## 13. Index

### 13.1 Principes

Les index accélèrent les lectures mais ralentissent les écritures et consomment de l'espace. Ils doivent correspondre à
des usages API réels : filtres, tris, jointures, recherches.

### 13.2 Tableau recommandations

| Colonne / Cas | Index recommandé | Justification | Module concerné |
|---|---|---|---|
| `websites.url` | unique index | éviter doublons, lookup | Websites |
| `websites.entity_id` | index FK | filtrer par entité | Websites |
| `is_active` | index si filtre fréquent | tables actives/inactives | Websites, Entities |
| `created_at` | index | tri et périodes | Reports, Logs |
| `keywords.keyword` | index ou full-text futur | recherche mots-clés | Keywords |
| `keywords.entity_id` | index FK | filtres entité | Keywords |
| `competitors.domain` | unique/index | lookup domaine | Competitors |
| `reports.status` | index | listes par statut | Reports |
| `logs.level` + `created_at` | composite futur | diagnostic | Logs |
| `crawler_jobs.status` | index | suivi jobs | Crawler |

### 13.3 Index composites

Utiliser un index composite quand les requêtes filtrent souvent par plusieurs colonnes :

```text
(website_id, created_at)
(entity_id, is_active)
(module, level, created_at)
```

### 13.4 Full-text futur

Pour contenus, prompts, logs et keywords volumineux, envisager :

- GIN ;
- tsvector ;
- trigram.

---

## 14. Timestamps et audit

### 14.1 Timestamps standards

| Colonne | Usage |
|---|---|
| `created_at` | Date de création |
| `updated_at` | Dernière modification |
| `deleted_at` | Suppression logique future |

### 14.2 Audit futur

| Colonne/table | Usage |
|---|---|
| `created_by` | Utilisateur créateur |
| `updated_by` | Dernier modificateur |
| `audit_logs` | Journal des actions sensibles |
| `login_history` | Connexions |
| `error_logs` | Erreurs applicatives |

### 14.3 Diagramme événements auditables

```text
User action
    |
    +-- create website
    +-- update role
    +-- export report
    +-- revoke session
    +-- import configuration
    |
    v
Service
    |
    v
AuditService futur
    |
    v
audit_logs
```

### 14.4 Lien avec AUTHENTICATION.md

Les tables `audit_logs`, `login_history`, `refresh_tokens`, `users`, `roles` et `permissions` doivent respecter les
principes de traçabilité et de révocation définis dans `AUTHENTICATION.md`.

---

## 15. Soft delete vs hard delete

### 15.1 Définitions

| Type | Description |
|---|---|
| Hard delete | Suppression physique de la ligne |
| Soft delete | Marquage via `deleted_at` ou état |

### 15.2 Recommandations par donnée

| Type de donnée | Suppression recommandée | Raison |
|---|---|---|
| Utilisateurs | Soft delete | Audit et sécurité |
| Rôles système | Pas de suppression | Intégrité RBAC |
| Permissions système | Pas de suppression | Stabilité sécurité |
| Websites | Soft delete futur ou hard contrôlé initial | Historique SEO |
| Keywords | Soft delete si historiques | Suivi positions |
| Reports | Soft delete | Conservation |
| Logs techniques | Archivage/purge contrôlée | Volumétrie |
| Refresh tokens | Révocation, puis purge | Sécurité |
| Configuration | Historisation future | Rollback |

### 15.3 Implications API/UI

Le Desktop doit voir :

- éléments actifs par défaut ;
- éléments supprimés seulement via filtre admin ;
- actions de restauration futures si soft delete.

### 15.4 Risques hard delete

- perte historique ;
- audit incomplet ;
- FK cassées si mal configurées ;
- impossibilité de restaurer.

---

## 16. Transactions

### 16.1 Diagramme de séquence

```text
Service          Repository          Session          PostgreSQL
  |                  |                  |                  |
  | start use case   |                  |                  |
  |----------------->| query/create     |                  |
  |                  |----------------->| SQL              |
  |                  |                  |----------------->|
  |                  |                  | result           |
  |                  |<-----------------|<-----------------|
  | validate state   |                  |                  |
  | commit           |                  |                  |
  |------------------------------------>| COMMIT           |
  | success          |                  |----------------->|
```

### 16.2 Règles

- Transaction courte.
- Pas d'appel réseau externe long pendant transaction ouverte.
- Rollback en cas d'exception.
- Flush seulement si nécessaire.
- Commit au niveau cohérent avec la convention du projet.

### 16.3 Responsabilités

| Couche | Responsabilité transaction |
|---|---|
| Route | Ne gère pas la transaction métier |
| Service | Définit l'unité métier |
| Repository | Utilise la session fournie |
| Session dependency | Ouvre/ferme et sécurise |

---

## 17. Sessions SQLAlchemy

### 17.1 Cycle de vie

```text
Request starts
    |
    v
Session created
    |
    v
Repositories use session
    |
    v
Commit / rollback
    |
    v
Session closed
```

### 17.2 Portée

La portée recommandée est une session par requête API.

### 17.3 Tests

Les tests peuvent utiliser une session isolée avec rollback ou reconstruction de schéma selon la stratégie du projet.

### 17.4 Anti-patterns

- Session globale partagée.
- Session créée dans le Desktop.
- Session créée dans un modèle.
- Session non fermée.
- Transaction longue autour d'un crawl complet.

---

## 18. Modèles existants

### 18.1 Tableau complet

| Modèle/table | Rôle | Relations | Contraintes attendues | Index | Évolutions futures |
|---|---|---|---|---|---|
| `users` | Comptes | rôles, logs | email unique, hash not null | email, state | MFA, sessions |
| `roles` | Rôles RBAC | permissions, users | code/name unique | code | hiérarchie |
| `permissions` | Droits | roles | code unique | module/action | granularité |
| `settings` | Paramètres | admin | clé unique | key | version config |
| `entities` | Marques groupe | websites, keywords futurs | name unique possible | name, active | marchés |
| `websites` | Sites suivis | entity nullable | url unique, entity FK | url, entity_id, active | audit SEO |
| `ai_providers` | Fournisseurs IA | ai_models | name unique | name | statuts |
| `ai_models` | Modèles IA | provider | provider FK | provider_id | coûts |
| `api_keys` | Clés externes | user/provider futur | secret hash/chiffré | provider | rotation |
| `audit_logs` | Audit | user nullable | append-only | created_at, actor | recherche |
| `error_logs` | Erreurs | module | niveau/date | level, created_at | purge |

### 18.2 Websites et Entities

```text
entities
   |
   | 1-N
   v
websites
```

`websites.entity_id` doit rester nullable si `ondelete="SET NULL"` est utilisé.

---

## 19. Modèles futurs

### 19.1 Matrice complète

| Table future | Module | Relations principales | Index recommandés | Priorité |
|---|---|---|---|---|
| `keywords` | Keywords | entity, website, urls | keyword, entity_id, website_id | Haute |
| `competitors` | Competitors | entity | domain, entity_id | Haute |
| `urls` | URLs/SEO | website | website_id, url, status_code | Haute |
| `pages` | Contents | url, website | website_id, slug | Moyenne |
| `contents` | Content | page/entity | page_id, updated_at | Moyenne |
| `reports` | Reports | entity, user | status, created_at, type | Haute |
| `crawler_jobs` | Crawler | website, user | status, website_id, created_at | Haute |
| `crawler_results` | Crawler | job, url | job_id, url_id, severity | Haute |
| `geo_queries` | GEO | prompt, entity | entity_id, model_id, created_at | Haute |
| `geo_results` | GEO | query, model | query_id, score, created_at | Haute |
| `ai_platforms` | IA | providers/models | name | Moyenne |
| `prompts` | Prompts | entity, user | module, version, active | Haute |
| `prompt_runs` | Prompts/IA | prompt, model | prompt_id, model_id, created_at | Haute |
| `api_keys` | Admin | provider/user | provider_id, active | Haute |
| `logs` | Logs | module/user | level, module, created_at | Moyenne |
| `audit_logs` | Audit | user/target | actor, event_type, created_at | Haute |
| `notifications` | UI/System | user | user_id, read_at | Basse |
| `settings` | Config | none/user | key | Haute |

### 19.2 Risques spécifiques

| Domaine | Risque | Prévention |
|---|---|---|
| Crawler | Volumétrie massive | pagination, archivage |
| GEO | Payload IA variable | JSONB justifié + champs indexables |
| Logs | Croissance rapide | purge/partition future |
| Reports | Fichiers lourds | stockage externe futur ou métadonnées |
| API keys | Secrets | chiffrement/masquage |

---

## 20. Schéma relationnel cible

### 20.1 Diagramme global conceptuel

```text
users ----< user_roles >---- roles ----< role_permissions >---- permissions
  |
  +----< audit_logs
  +----< login_history
  +----< reports

entities ----< websites ----< urls ----< crawler_results >---- crawler_jobs
   |              |             |
   |              |             +----< seo_audits
   |              |
   +----< keywords
   +----< competitors
   +----< reports
   +----< prompts ----< prompt_runs >---- ai_models ----< ai_providers
   +----< geo_queries ----< geo_results

settings
api_keys ---- ai_providers
error_logs
notifications ---- users
```

### 20.2 Domaines

| Domaine | Tables principales |
|---|---|
| Administration | users, roles, permissions, settings |
| Sites | entities, websites, urls |
| SEO | keywords, seo_audits, seo_recommendations |
| GEO | prompts, geo_queries, geo_results |
| IA | ai_providers, ai_models, prompt_runs |
| Crawler | crawler_jobs, crawler_results |
| Reports | reports, report_exports |
| Logs | audit_logs, error_logs, login_history |

---

## 21. Pagination et performance database

### 21.1 Lien API

`API_ARCHITECTURE.md` définit la réponse paginée :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

La base doit permettre d'alimenter cette structure efficacement.

### 21.2 OFFSET / LIMIT

Pattern initial :

```sql
SELECT *
FROM websites
WHERE is_active = true
ORDER BY name ASC
LIMIT 20 OFFSET 0;
```

### 21.3 Coûts

`OFFSET` devient coûteux sur grandes tables. Pour logs, crawler et résultats GEO massifs, prévoir plus tard :

- keyset pagination ;
- curseurs ;
- archivage ;
- partitionnement.

### 21.4 Comptage total

`COUNT(*)` peut être coûteux. Sur très gros volumes, envisager :

- compte approximatif ;
- cache ;
- filtre obligatoire ;
- tables d'agrégats.

---

## 22. Recherche et full-text futur

### 22.1 Recherche simple

La recherche initiale peut utiliser `ILIKE` sur colonnes bornées :

```sql
WHERE name ILIKE '%armurerie%'
```

### 22.2 Risques

- scans complets ;
- lenteur sur tables volumineuses ;
- mauvaise pertinence ;
- difficulté multilingue.

### 22.3 Full-text futur

Cas adaptés :

- contenus ;
- prompts ;
- rapports ;
- logs ;
- mots-clés ;
- concurrents.

### 22.4 Index futurs

| Cas | Index |
|---|---|
| Recherche texte simple | trigram GIN |
| Full-text contenu | tsvector GIN |
| Logs par message | full-text ou trigram |
| Keywords | btree + trigram selon besoin |

---

## 23. JSON / JSONB futur

### 23.1 Règle claire

Par défaut : relationnel. JSONB uniquement quand justifié.

### 23.2 Cas acceptables

| Cas | Justification |
|---|---|
| Résultats IA bruts | Structures variables selon modèle |
| Métadonnées crawler | Données techniques flexibles |
| Snapshots API externes | Conservation brut contrôlée |
| Configuration flexible | Paramètres peu requêtés |
| Payloads externes | Audit technique |

### 23.3 Risques

| Risque | Impact |
|---|---|
| Perte de contraintes | Données incohérentes |
| Requêtes complexes | Maintenance difficile |
| Index spécifiques | Coût technique |
| Dette cachée | Migration future difficile |

### 23.4 Bonne pratique

Même avec JSONB, extraire en colonnes les champs filtrés ou triés fréquemment.

---

## 24. Données sensibles

### 24.1 Types

| Donnée | Stockage recommandé |
|---|---|
| Mot de passe | Hash Argon2id |
| Refresh token | Hash |
| Clé API externe | Chiffrement ou secret manager futur |
| Access token | Ne pas persister sauf blacklist JTI |
| Logs sécurité | Sans secrets |
| Données utilisateur | Minimisation |

### 24.2 Liens documentaires

- `AUTHENTICATION.md` pour tokens, sessions, RBAC.
- futur `SECURITY.md` pour chiffrement, secrets, déploiement.

### 24.3 Masquage

Les réponses API et logs ne doivent exposer que :

```text
sk_live_********1234
```

jamais la valeur complète.

---

## 25. Configuration et paramètres

### 25.1 Tables de configuration

Les paramètres applicatifs doivent être :

- typés ;
- validés ;
- exportables ;
- importables ;
- auditables ;
- non destructifs par défaut.

### 25.2 Import/export

| Sujet | Règle |
|---|---|
| Import | Idempotent si possible |
| Export | Ne pas inclure secrets en clair |
| Version | Prévoir version de format |
| Traçabilité | Audit futur |
| Rollback | Prévoir sauvegarde avant import massif |

### 25.3 Module administration

Le module administration existant est la surface API pour settings, providers IA, modèles IA, clés API et santé. Les
tables correspondantes doivent privilégier contraintes fortes et auditabilité.

---

## 26. Migrations de données

### 26.1 Types

| Type | Description |
|---|---|
| Structurelle | Ajout table/colonne/index |
| Donnée | Backfill, normalisation |
| Destructive | Suppression table/colonne |
| Corrective | Correction données incohérentes |

### 26.2 Backfill

Pattern :

```text
1. Ajouter colonne nullable
2. Remplir données
3. Valider couverture
4. Rendre non nullable si nécessaire
```

### 26.3 Checklist migration de données

| Contrôle | OK |
|---|---|
| Volume estimé | |
| Backup avant migration critique | |
| Migration idempotente si possible | |
| Downgrade réfléchi | |
| Données sensibles protégées | |
| Temps d'exécution estimé | |
| Tests avec données réalistes futurs | |
| Plan rollback | |

---

## 27. Tests database

### 27.1 Stratégie

Les tests database vérifient :

- contraintes ;
- repositories futurs ;
- services ;
- migrations futures ;
- pagination ;
- conflits ;
- intégrité relationnelle.

### 27.2 `Base.metadata.create_all()` en test

Acceptable uniquement dans les tests, par exemple dans `tests/conftest.py`, si la stratégie de test le nécessite.
Interdit dans les migrations.

### 27.3 Commandes

```powershell
py -m pytest
py -m ruff check .
```

### 27.4 Checklist tests

| Contrôle | OK |
|---|---|
| Contrainte unique testée | |
| FK testée | |
| Suppression testée | |
| Pagination testée | |
| Service couvre règle métier | |
| Repository futur testé si requête complexe | |
| Migration future testée si critique | |

---

## 28. Performance PostgreSQL

### 28.1 Points de vigilance

- Requêtes lentes.
- N+1 ORM.
- Pagination profonde.
- Logs volumineux.
- Résultats crawler massifs.
- JSONB non indexé.
- Transactions longues.

### 28.2 Checklist performance

| Contrôle | OK |
|---|---|
| Index sur FK fréquentes | |
| Index sur filtres fréquents | |
| Tri couvert par index si besoin | |
| Pas de N+1 identifié | |
| Pagination obligatoire | |
| Transactions courtes | |
| Logs archivables | |
| EXPLAIN futur sur requêtes critiques | |

### 28.3 Eager/lazy loading

| Cas | Recommandation |
|---|---|
| Afficher table simple | éviter relations inutiles |
| Détail avec relations | chargement explicite |
| Export | batch/pagination |
| Rapport | requêtes agrégées |

---

## 29. Sécurité database

### 29.1 Accès

La base doit être accessible uniquement par le backend et les outils d'administration autorisés. Le Desktop n'a aucun
accès direct.

### 29.2 Droits minimaux

| Compte | Droits |
|---|---|
| Application | CRUD nécessaire |
| Migration | DDL contrôlé |
| Lecture reporting futur | Lecture limitée |
| Admin DB | Usage exceptionnel |

### 29.3 Secrets

- `DATABASE_URL` dans `.env` ou variable d'environnement.
- Pas de mot de passe DB dans Git.
- Rotation future documentée.

### 29.4 Sauvegardes et chiffrement futur

Prévoir :

- chiffrement au repos selon infrastructure ;
- chiffrement sauvegardes ;
- contrôle accès backups ;
- audit accès données sensibles.

---

## 30. Sauvegardes et restauration

### 30.1 Stratégie future

| Sujet | Recommandation |
|---|---|
| Fréquence | quotidienne minimum en production |
| Rétention | selon politique interne |
| Avant migration critique | backup obligatoire |
| Test restauration | périodique |
| Environnements | prod, staging, dev séparés |
| Secrets | backups protégés |

### 30.2 Restauration

Un plan de restauration doit préciser :

- source du backup ;
- durée cible ;
- validation post-restore ;
- cohérence Alembic ;
- communication aux utilisateurs.

---

## 31. Anti-patterns interdits

### 31.1 Tableau

| Anti-pattern | Pourquoi c'est dangereux | Alternative correcte |
|---|---|---|
| `Base.metadata.create_all()` dans migration | Structure non versionnée explicitement | `op.create_table` |
| `Base.metadata.drop_all()` dans migration | Destruction massive | `op.drop_table` ciblé |
| Suppression table sans stratégie | Perte données | plan migration + backup |
| Colonne nullable par facilité | Données incohérentes | nullabilité réfléchie |
| Index oubliés | API lente | index dès conception |
| Logique métier dans model | Couplage persistence/métier | service |
| Accès DB depuis route | Violation architecture | repository |
| Accès DB depuis Desktop | Faille architecture | API REST |
| JSONB par paresse | Dette et contraintes faibles | modèle relationnel |
| Migration non réversible | Rollback impossible | downgrade explicite |
| Contrainte absente | Données invalides | unique/FK/check |
| Relation sans `ondelete` réfléchi | Suppression imprévisible | choisir CASCADE/SET NULL/RESTRICT |

---

## 32. Pattern officiel pour créer une nouvelle table

### 32.1 Étapes

1. Définir le besoin métier.
2. Définir les relations.
3. Définir le modèle SQLAlchemy.
4. Définir les contraintes.
5. Définir les index.
6. Créer une migration Alembic explicite.
7. Créer ou adapter repository.
8. Créer ou adapter service.
9. Créer ou adapter schemas.
10. Créer ou adapter routes.
11. Écrire tests.
12. Valider Ruff/Pytest.

### 32.2 Diagramme

```text
Besoin métier
      |
      v
Modèle relationnel
      |
      v
SQLAlchemy Model
      |
      v
Alembic migration explicite
      |
      v
Repository
      |
      v
Service
      |
      v
Schema + Route
      |
      v
Tests
```

### 32.3 Checklist

| Contrôle | OK |
|---|---|
| Table nommée correctement | |
| PK définie | |
| FK définies | |
| `ondelete` réfléchi | |
| Nullabilité volontaire | |
| Contraintes uniques | |
| Index nécessaires | |
| Timestamps | |
| Migration explicite | |
| Downgrade cohérent | |
| Model aligné migration | |
| Tests ajoutés | |

---

## 33. Checklist avant Pull Request database

| Contrôle | Commande ou action | OK |
|---|---|---|
| Statut Git | `git status` | |
| Stat diff | `git diff --stat` | |
| Espaces | `git diff --check` | |
| Tests | `py -m pytest` | |
| Ruff | `py -m ruff check .` | |
| Migration explicite | revue migration | |
| Pas de `create_all/drop_all` | recherche texte | |
| Downgrade cohérent | revue | |
| Contraintes vérifiées | revue | |
| Index vérifiés | revue | |
| Relations vérifiées | revue | |
| Pas de secret | revue diff | |
| Documentation mise à jour | docs | |

---

## 34. Roadmap database

### 34.1 Administration

- users ;
- roles ;
- permissions ;
- settings ;
- API keys ;
- logs.

### 34.2 Websites / Entities

- entities ;
- websites ;
- urls ;
- relations SEO.

### 34.3 Keywords

- keywords ;
- positions ;
- tags ;
- imports.

### 34.4 Competitors

- competitors ;
- domains ;
- market tracking.

### 34.5 URLs / Pages / Contents

- urls ;
- pages ;
- contents ;
- metadata SEO.

### 34.6 Crawler

- crawler_jobs ;
- crawler_results ;
- errors ;
- performance metrics.

### 34.7 SEO

- seo_audits ;
- seo_recommendations ;
- indexation snapshots.

### 34.8 GEO / IA / Prompts

- prompts ;
- prompt_runs ;
- geo_queries ;
- geo_results ;
- ai_providers ;
- ai_models.

### 34.9 Reports

- reports ;
- report_exports ;
- schedules future.

### 34.10 Logs / Audit

- audit_logs ;
- error_logs ;
- login_history ;
- security events.

### 34.11 Performance / Archivage / Sauvegardes

- indexes avancés ;
- archivage logs ;
- backups testés ;
- version stable v1.

---

## 35. Annexes

### 35.1 Glossaire

| Terme | Définition |
|---|---|
| Table | Structure relationnelle PostgreSQL |
| Model | Classe SQLAlchemy mappée à une table |
| Repository | Couche d'accès aux données |
| Migration | Script Alembic versionnant la structure |
| FK | Clé étrangère |
| PK | Clé primaire |
| Index | Structure d'accélération de requête |
| Soft delete | Suppression logique |
| Hard delete | Suppression physique |
| JSONB | Type PostgreSQL JSON binaire indexable |

### 35.2 Abréviations

| Abréviation | Signification |
|---|---|
| DB | Database |
| ORM | Object Relational Mapper |
| FK | Foreign Key |
| PK | Primary Key |
| DDL | Data Definition Language |
| DML | Data Manipulation Language |
| SEO | Search Engine Optimization |
| GEO | Generative Engine Optimization |
| IA | Intelligence artificielle |

### 35.3 Conventions rapides

| Besoin | Règle |
|---|---|
| Nouvelle table | Model + migration explicite |
| Nouvelle relation | FK + index + `ondelete` |
| Nouvelle liste API | index filtres + pagination |
| Secret | hash/chiffrement, jamais clair |
| Suppression | soft delete par défaut si historique |
| JSONB | seulement justifié |
| Migration | jamais `create_all/drop_all` |

### 35.4 Modèle de migration Alembic

```python
def upgrade() -> None:
    op.create_table(
        "example_table",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_example_table_name"),
    )
    op.create_index("ix_example_table_name", "example_table", ["name"])


def downgrade() -> None:
    op.drop_index("ix_example_table_name", table_name="example_table")
    op.drop_table("example_table")
```

### 35.5 Modèle de table métier

```text
<resources>
  id
  name
  is_active
  created_at
  updated_at
  deleted_at future if needed
  foreign keys
  unique constraints
  indexes
```

### 35.6 Matrice relationnelle rapide

| Parent | Enfant | Relation | ondelete recommandé |
|---|---|---|---|
| entities | websites | 1-N | SET NULL ou RESTRICT selon besoin |
| websites | urls | 1-N | CASCADE ou RESTRICT selon historique |
| roles | role_permissions | 1-N pivot | CASCADE |
| permissions | role_permissions | 1-N pivot | CASCADE/RESTRICT |
| prompts | prompt_runs | 1-N | RESTRICT |
| crawler_jobs | crawler_results | 1-N | CASCADE si job supprimable |
| users | audit_logs | 1-N | SET NULL/RESTRICT |

### 35.7 Checklist développeur

| Question | Réponse attendue |
|---|---|
| Ai-je créé une migration explicite ? | Oui |
| Le model correspond-il à la migration ? | Oui |
| Les FK ont-elles un `ondelete` réfléchi ? | Oui |
| Les colonnes nullable sont-elles justifiées ? | Oui |
| Les index couvrent-ils les filtres fréquents ? | Oui |
| Ai-je évité JSONB par facilité ? | Oui |
| La suppression est-elle maîtrisée ? | Oui |
| Les tests couvrent-ils les contraintes importantes ? | Oui |

### 35.8 Résumé architectural

L'architecture database officielle de Veille SEO-GEO Groupe A.P&Partner repose sur PostgreSQL, SQLAlchemy 2.x,
repositories et Alembic. Les repositories sont la seule couche d'accès aux données, les modèles représentent les tables,
et les migrations Alembic décrivent explicitement chaque évolution structurelle.

La règle centrale est non négociable :

```text
Pas de Base.metadata.create_all() ni Base.metadata.drop_all() dans les migrations.
```

Cette spécification doit guider tout ajout de table, relation, index, contrainte, migration ou modèle jusqu'à la version
1.0 du projet.
