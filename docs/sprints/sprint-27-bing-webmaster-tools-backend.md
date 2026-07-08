# Sprint 27 — Bing Webmaster Tools Backend

## Objectif

Le Sprint 27 a pour objectif de cadrer l’intégration backend complète de Bing Webmaster Tools dans la plateforme interne Veille SEO-GEO Groupe A.P&Partner.

Ce document prépare l’implémentation future du module backend Bing Webmaster Tools, sans réaliser d’implémentation technique dans ce sprint de cadrage documentaire.

Objectifs principaux :

- définir le périmètre backend attendu ;
- cadrer les modèles SQLAlchemy prévisionnels ;
- cadrer la migration Alembic prévisionnelle ;
- cadrer les schémas Pydantic prévisionnels ;
- cadrer les repositories, services, connecteur et routes REST ;
- rappeler les contraintes de sécurité, d’idempotence et de tests ;
- préparer une base de travail claire pour l’implémentation ultérieure.

## Contexte

L’application permet de piloter les performances SEO et GEO de plusieurs sites web. Après les modules Google Search Console et Google Analytics, Bing Webmaster Tools doit compléter les sources de données SEO disponibles côté backend.

Le Sprint 27 doit rester strictement backend. Le Desktop PySide6 n’est pas concerné par ce sprint. Aucune interface utilisateur, aucun écran Desktop et aucun appel direct depuis le Desktop vers Bing Webmaster Tools ne doivent être prévus dans ce périmètre.

Le module devra respecter l’architecture backend existante du dépôt et s’intégrer sans créer d’architecture parallèle.

Flux obligatoire :

```text
Routes
    ↓
Services
    ↓
Repositories
    ↓
Models
```

Les routes FastAPI ne doivent contenir aucune logique métier. Les services contiennent la logique métier. Les repositories contiennent uniquement les accès SQLAlchemy. Les modèles représentent les tables PostgreSQL. Les schémas Pydantic gèrent les entrées et sorties API.

## Périmètre inclus

Le périmètre prévisionnel du Sprint 27 inclut :

- modèles SQLAlchemy dédiés à Bing Webmaster Tools ;
- migration Alembic explicite ;
- schémas Pydantic d’entrée et de sortie ;
- repositories SQLAlchemy ;
- services métier ;
- connecteur Bing Webmaster Tools injectable ;
- routes REST backend ;
- OAuth si nécessaire selon le mode d’authentification retenu ;
- import des données Bing Webmaster Tools ;
- endpoints REST paginés et filtrables ;
- documentation du sprint ;
- tests backend, repository, service et API ;
- tests avec connecteur fake ou mock ;
- absence totale d’appel Internet pendant les tests.

## Périmètre exclu

Le Sprint 27 exclut explicitement :

- toute modification Desktop PySide6 ;
- toute modification du client HTTP Desktop ;
- toute interface utilisateur ;
- tout écran, composant ou service Desktop ;
- toute intégration React ou frontend web ;
- toute synchronisation automatique planifiée ;
- tout worker, scheduler ou tâche périodique ;
- tout export CSV, PDF ou Excel ;
- toute refonte d’un module existant ;
- toute duplication de l’architecture Google Search Console ou Google Analytics sans adaptation ;
- toute exposition de secret dans le code, les logs ou les réponses API ;
- tout appel Internet réel dans les tests.

Le Desktop ne doit pas être concerné par ce sprint. Il consommera éventuellement les endpoints REST dans un sprint ultérieur.

## Architecture backend attendue

L’implémentation future devra respecter strictement la séparation suivante :

```text
Client HTTP futur
    ↓
Routes FastAPI
    ↓
Services métier
    ↓
Repositories SQLAlchemy
    ↓
Models SQLAlchemy
    ↓
PostgreSQL
```

Le connecteur Bing Webmaster Tools sera une dépendance technique utilisée par la couche service. Il ne devra pas être appelé depuis les routes, les repositories ou les modèles.

Responsabilités attendues :

- les routes déclarent les endpoints, paramètres, dépendances et schémas API ;
- les routes appellent les services et ne contiennent aucune logique métier ;
- les services orchestrent les règles métier, imports, idempotence, erreurs et connecteur ;
- les repositories encapsulent uniquement les accès SQLAlchemy ;
- les modèles SQLAlchemy décrivent les tables, relations, index et contraintes ;
- les schémas Pydantic décrivent les contrats API sans exposer de secret ;
- le connecteur isole les échanges avec Bing Webmaster Tools et reste mockable.

## Modèles SQLAlchemy prévisionnels

Les modèles suivants sont proposés comme base de conception, sans création dans ce sprint documentaire :

- `BingWebmasterConnection` ;
- `BingWebmasterSite` ;
- `BingWebmasterMetric` ;
- `BingWebmasterCrawlStat` ;
- `BingWebmasterSitemap` ;
- `BingWebmasterImportRun`.

Tables prévisionnelles :

- `bing_webmaster_connections` ;
- `bing_webmaster_sites` ;
- `bing_webmaster_metrics` ;
- `bing_webmaster_crawl_stats` ;
- `bing_webmaster_sitemaps` ;
- `bing_webmaster_import_runs`.

Les noms définitifs devront être alignés avec les conventions existantes du dépôt au moment de l’implémentation.

### `BingWebmasterConnection`

Représente une connexion Bing Webmaster Tools configurée côté backend.

Champs conceptuels possibles :

- identifiant interne ;
- nom affichable ;
- type d’authentification ;
- état actif ou inactif ;
- métadonnées OAuth si nécessaire ;
- référence chiffrée vers les secrets ou tokens ;
- date de dernière synchronisation réussie ;
- dates de création et de modification.

Aucun token ne devra être stocké en clair.

### `BingWebmasterSite`

Représente un site Bing Webmaster Tools rattaché à une connexion.

Champs conceptuels possibles :

- identifiant interne ;
- identifiant de connexion ;
- identifiant ou URL du site côté Bing ;
- URL canonique ;
- nom affichable ;
- état de vérification ;
- date de dernière importation ;
- métadonnées utiles à l’analyse SEO ;
- dates de création et de modification.

### `BingWebmasterMetric`

Représente les métriques importées depuis Bing Webmaster Tools.

Champs conceptuels possibles :

- identifiant interne ;
- identifiant du site Bing ;
- identifiant de l’import source ;
- date de mesure ;
- impressions ;
- clics ;
- position moyenne ;
- CTR ;
- requête ou page lorsque disponible ;
- pays, appareil ou dimension complémentaire lorsque disponible ;
- dates de création et de modification.

L’idempotence devra empêcher la création de doublons lors d’une relance d’import.

### `BingWebmasterCrawlStat`

Représente les statistiques de crawl exposées par Bing Webmaster Tools.

Champs conceptuels possibles :

- identifiant interne ;
- identifiant du site Bing ;
- identifiant de l’import source ;
- date de mesure ;
- pages explorées ;
- erreurs de crawl ;
- avertissements ;
- statut ou type d’erreur ;
- dates de création et de modification.

### `BingWebmasterSitemap`

Représente les sitemaps connus par Bing Webmaster Tools.

Champs conceptuels possibles :

- identifiant interne ;
- identifiant du site Bing ;
- URL du sitemap ;
- statut ;
- nombre d’URL soumises ;
- nombre d’URL indexées lorsque disponible ;
- dernière soumission ;
- dernière lecture par Bing ;
- dates de création et de modification.

### `BingWebmasterImportRun`

Représente l’historique des imports Bing Webmaster Tools.

Champs conceptuels possibles :

- identifiant interne ;
- identifiant de connexion ;
- identifiant de site Bing ;
- période demandée ;
- statut d’exécution ;
- lignes reçues ;
- lignes créées ;
- lignes mises à jour ;
- lignes ignorées ;
- code d’erreur contrôlé ;
- message d’erreur sans secret ;
- date de début ;
- date de fin ;
- durée d’exécution.

## Migration Alembic prévisionnelle

La future migration Alembic devra être explicite et traçable. Elle ne devra pas s’appuyer sur la création automatique des tables depuis les métadonnées SQLAlchemy.

Interdictions dans la future migration :

```python
Base.metadata.create_all()
Base.metadata.drop_all()
```

La migration devra utiliser les opérations Alembic explicites adaptées :

```python
op.create_table(...)
op.create_index(...)
op.create_unique_constraint(...)
op.drop_index(...)
op.drop_table(...)
```

La migration devra prévoir :

- clés primaires ;
- clés étrangères ;
- index nécessaires aux filtres et à la pagination ;
- contraintes d’unicité utiles à l’idempotence ;
- colonnes d’audit cohérentes avec les conventions existantes ;
- downgrade explicite et ordonné.

## Schémas Pydantic prévisionnels

Les schémas Pydantic devront séparer les usages API :

- création de connexion ;
- mise à jour de connexion ;
- lecture de connexion ;
- liste paginée de connexions ;
- lecture de site Bing ;
- liste paginée de sites ;
- demande d’import ;
- résultat d’import ;
- lecture de métriques ;
- lecture de statistiques de crawl ;
- lecture de sitemaps ;
- lecture de l’historique d’imports ;
- réponses d’erreur contrôlées si nécessaire.

Les schémas ne devront jamais exposer :

- token d’accès ;
- refresh token ;
- client secret ;
- clé API ;
- valeur chiffrée brute ;
- détail technique sensible.

## Repositories prévisionnels

Les repositories devront être limités aux accès SQLAlchemy.

Repositories conceptuels possibles :

- repository des connexions Bing Webmaster Tools ;
- repository des sites ;
- repository des métriques ;
- repository des statistiques de crawl ;
- repository des sitemaps ;
- repository des imports.

Responsabilités attendues :

- lire les entités ;
- créer les entités ;
- mettre à jour les entités ;
- désactiver ou supprimer logiquement lorsque nécessaire ;
- appliquer les filtres SQLAlchemy ;
- fournir la pagination ;
- appliquer les contraintes d’idempotence demandées par les services ;
- ne jamais appeler Bing Webmaster Tools ;
- ne jamais contenir de logique métier.

## Services prévisionnels

Les services porteront la logique métier du module Bing Webmaster Tools.

Services conceptuels possibles :

- service de gestion des connexions ;
- service de découverte ou synchronisation des sites ;
- service d’import des métriques ;
- service d’import des statistiques de crawl ;
- service d’import des sitemaps ;
- service de consultation et agrégation légère lorsque nécessaire.

Responsabilités attendues :

- valider les paramètres fonctionnels ;
- vérifier les connexions actives ;
- orchestrer repositories et connecteur ;
- gérer l’idempotence des imports ;
- normaliser les données reçues ;
- transformer les erreurs techniques en erreurs métier ;
- journaliser les imports sans secret ;
- garantir que les routes restent fines.

## Connecteur Bing Webmaster Tools

Le connecteur Bing Webmaster Tools devra isoler toute communication avec Bing.

Responsabilités attendues :

- construire les appels techniques vers Bing Webmaster Tools ;
- gérer l’authentification ou OAuth si nécessaire ;
- renouveler ou préparer le renouvellement des tokens si le mécanisme est retenu ;
- récupérer les sites disponibles ;
- récupérer les métriques SEO ;
- récupérer les statistiques de crawl ;
- récupérer les sitemaps ;
- convertir les réponses techniques en structures exploitables par les services ;
- lever des erreurs contrôlables par les services.

Contraintes :

- connecteur injectable ;
- connecteur fake ou mockable pour les tests ;
- aucun secret codé en dur ;
- aucun appel direct depuis les routes ;
- aucun appel direct depuis les repositories ;
- aucun appel Internet pendant les tests.

## Routes REST prévisionnelles

Préfixe recommandé :

```text
/api/v1/bing-webmaster-tools
```

Routes prévisionnelles :

```text
GET    /api/v1/bing-webmaster-tools/connections
POST   /api/v1/bing-webmaster-tools/connections
GET    /api/v1/bing-webmaster-tools/connections/{connection_id}
PATCH  /api/v1/bing-webmaster-tools/connections/{connection_id}
DELETE /api/v1/bing-webmaster-tools/connections/{connection_id}

GET    /api/v1/bing-webmaster-tools/sites
GET    /api/v1/bing-webmaster-tools/sites/{bing_site_id}

POST   /api/v1/bing-webmaster-tools/import

GET    /api/v1/bing-webmaster-tools/metrics
GET    /api/v1/bing-webmaster-tools/crawl-stats
GET    /api/v1/bing-webmaster-tools/sitemaps
GET    /api/v1/bing-webmaster-tools/import-runs
```

Les endpoints de liste devront être paginés. Les filtres attendus pourront inclure, selon les données disponibles :

- `connection_id` ;
- `bing_site_id` ;
- `website_id` ;
- `date_from` ;
- `date_to` ;
- `status` ;
- `search` ;
- `page` ;
- `page_size`.

Les routes ne devront contenir aucune logique métier, aucune requête SQLAlchemy directe et aucun appel direct au connecteur Bing Webmaster Tools.

## Sécurité et secrets

Contraintes de sécurité obligatoires :

- aucun token en clair dans Git ;
- aucun token en clair dans les logs ;
- aucun secret exposé dans les réponses API ;
- aucun client secret exposé au Desktop ;
- aucune valeur chiffrée brute exposée via les schémas de lecture ;
- réutilisation du mécanisme existant de chiffrement des secrets si disponible ;
- séparation stricte entre configuration, stockage chiffré et réponses API ;
- messages d’erreur contrôlés et nettoyés ;
- connecteur mockable ou fake pour les tests ;
- aucun appel Internet pendant les tests.

Si OAuth est nécessaire, le backend devra rester responsable des échanges sensibles. Le Desktop ne devra jamais manipuler de refresh token ni de client secret.

## Imports et idempotence

Les imports devront être idempotents. Relancer un import sur la même connexion, le même site, la même période et les mêmes dimensions ne devra pas créer de doublons.

Points à cadrer lors de l’implémentation :

- clé fonctionnelle d’idempotence pour les métriques ;
- clé fonctionnelle d’idempotence pour les statistiques de crawl ;
- clé fonctionnelle d’idempotence pour les sitemaps ;
- statut d’import en cas de succès, échec ou résultat partiel ;
- volumes reçus, créés, mis à jour et ignorés ;
- gestion des relances après erreur ;
- conservation d’un historique exploitable pour diagnostic.

Les règles d’idempotence devront être décidées dans les services et appliquées via les repositories.

## Tests prévisionnels

Les familles de tests à prévoir sont :

- tests modèles ;
- tests repositories ;
- tests services ;
- tests routes API ;
- tests d’import idempotent ;
- tests pagination, filtres et recherche ;
- tests de gestion d’erreurs ;
- tests avec connecteur fake ou mock ;
- tests de non-exposition des secrets ;
- confirmation qu’aucun appel Internet n’est fait pendant les tests.

Les tests ne devront pas dépendre de Bing Webmaster Tools réel. Le connecteur devra être remplacé par un fake ou un mock dans tous les tests automatisés.

## Fichiers à créer lors de l’implémentation

Liste prévisionnelle à confirmer au moment de l’implémentation selon l’architecture réelle du dépôt :

- modèle SQLAlchemy Bing Webmaster Tools ;
- migration Alembic dédiée et explicite ;
- schémas Pydantic Bing Webmaster Tools ;
- repository ou repositories Bing Webmaster Tools ;
- service ou services Bing Webmaster Tools ;
- connecteur Bing Webmaster Tools ;
- routeur FastAPI Bing Webmaster Tools ;
- tests modèles ;
- tests repositories ;
- tests services ;
- tests routes API ;
- documentation API complémentaire si un nouveau contrat REST est ajouté.

Les chemins définitifs devront suivre les conventions existantes du dépôt.

## Fichiers potentiellement modifiés lors de l’implémentation

Liste prévisionnelle à confirmer au moment de l’implémentation :

- registre des routes API pour inclure le routeur Bing Webmaster Tools ;
- initialisation des modèles si le dépôt utilise un registre explicite ;
- initialisation des schémas si le dépôt utilise des exports centralisés ;
- configuration applicative si de nouvelles variables d’environnement sont nécessaires ;
- documentation technique liée aux API ou aux connecteurs.

Toute modification devra rester limitée au périmètre backend Bing Webmaster Tools et être justifiée avant application.

## Critères d’acceptation

L’implémentation future du Sprint 27 sera acceptable si :

- l’architecture backend est respectée ;
- les routes ne contiennent aucune logique métier ;
- les services sont responsables de la logique métier ;
- les repositories sont limités aux accès SQLAlchemy ;
- les modèles SQLAlchemy restent cohérents avec PostgreSQL et Alembic ;
- la migration Alembic est explicite ;
- aucun `Base.metadata.create_all()` ou `Base.metadata.drop_all()` n’est utilisé en migration ;
- les secrets ne sont pas exposés ;
- les imports sont idempotents ;
- les endpoints de liste sont paginés ;
- les filtres prévus sont testés ;
- les erreurs sont contrôlées et sans secret ;
- les tests utilisent un connecteur fake ou mock ;
- les tests ne font aucun appel Internet ;
- Ruff est OK ;
- Pytest est OK.

## Commandes de validation prévues

Commandes à prévoir pour l’implémentation future :

```powershell
git status --short
git diff --stat
git diff --check
python -m ruff check .
python -m pytest
```

Pour ce sprint documentaire, seules les commandes suivantes doivent être exécutées après création du fichier Markdown :

```powershell
git status --short
git diff --stat
git diff --check
```

## Notes d’implémentation

Choix appliqués lors de l’implémentation du Sprint 27 :

- connecteur Bing Webmaster Tools placé dans `backend/app/connectors/bing_webmaster_tools.py`, conformément aux conventions existantes des connecteurs Google ;
- connecteur par défaut non configuré afin d’éviter tout appel externe involontaire ;
- fake déterministe disponible pour les tests sans Internet ;
- routeur enregistré via `backend/app/api/v1/router.py` sans modification de `backend/app/main.py` ;
- modèles exportés dans `backend/app/models/__init__.py` pour permettre la création des tables dans la base de test ;
- tri whitelisté dans le repository, sur le modèle du module Google Analytics 4 ;
- secrets chiffrés via le mécanisme existant `encrypt_secret` / `decrypt_secret` et jamais exposés dans les schémas de sortie.
