# Sprint 24A — Google Search Console Backend

## 1. Objectif

Le Sprint 24A a pour objectif de créer le socle backend Google Search Console de la plateforme Veille SEO-GEO Groupe
A.P&Partner.

Ce sprint prépare l'intégration des données Google Search Console dans l'application, sans ajouter d'interface Desktop
et sans modifier le Dashboard existant. Il doit fournir une couche backend claire, testable et extensible, qui sera
consommée ensuite par le Sprint 24B Desktop.

Principes obligatoires :

- le backend est l'unique point d'accès aux données Google Search Console ;
- le Desktop ne communique jamais directement avec Google ;
- le Desktop ne communique jamais directement avec PostgreSQL ;
- le Sprint 24B consommera uniquement les endpoints REST créés dans ce sprint.

Le Sprint 24A doit donc isoler les accès Google, les règles métier et la persistance afin de garantir une séparation
stricte entre le backend, la base de données et les futures interfaces utilisatrices.

## 2. Architecture backend

L'architecture obligatoire suit le découpage existant du projet :

```text
Routes
    -> Services
        -> Repositories
            -> Models
```

Responsabilités attendues :

- les routes exposent uniquement l'API REST ;
- les services contiennent la logique métier ;
- les repositories réalisent uniquement les accès SQLAlchemy ;
- les models représentent les tables PostgreSQL ;
- les schemas Pydantic gèrent les entrées et sorties de l'API.

La logique métier ne doit pas être placée dans les routes API. Les routes doivent valider les paramètres, appeler le
service approprié et retourner une réponse structurée. Les services orchestrent les règles métier, les appels au
connecteur Google Search Console, la journalisation des imports et la gestion des erreurs. Les repositories restent
limités aux opérations de lecture et d'écriture en base.

## 3. Périmètre fonctionnel

Le Sprint 24A couvre la préparation backend des familles fonctionnelles suivantes :

- propriétés Google Search Console ;
- performances ;
- indexation ;
- sitemaps ;
- imports manuels ;
- historique des imports ;
- préparation OAuth.

Les propriétés Google Search Console permettent d'identifier les sites disponibles et suivis par la plateforme. Les
performances couvrent les métriques issues de Google Search Console, comme les clics, impressions, positions moyennes et
taux de clic. L'indexation doit préparer le stockage des informations de couverture. Les sitemaps doivent permettre de
suivre les fichiers déclarés et leur état. Les imports manuels doivent offrir une première capacité de synchronisation
déclenchée côté backend. L'historique des imports doit rendre chaque synchronisation traçable et auditable.

La préparation OAuth doit poser les bases de l'authentification Google côté backend, sans exposer de secret au Desktop
et sans implémenter d'appel Google côté client.

## 4. Modèles SQLAlchemy prévus

Les modèles SQLAlchemy prévus pour l'implémentation future sont les suivants.

`GoogleSearchConsoleProperty`

Ce modèle représente une propriété Google Search Console rattachée à un site suivi par la plateforme. Il doit permettre
de stocker l'identifiant de propriété Google, son type, son URL ou domaine, son état d'activation et les métadonnées
nécessaires au suivi.

`GoogleSearchConsolePerformance`

Ce modèle représente les données de performance issues de Google Search Console. Il doit permettre d'historiser les
métriques par propriété, période et dimensions utiles, notamment page, requête, pays, appareil ou type de recherche
lorsque ces dimensions sont supportées par le périmètre retenu.

`GoogleSearchConsoleIndexCoverage`

Ce modèle représente les informations d'indexation et de couverture. Il doit permettre de conserver l'état des URLs ou
des groupes d'URLs analysés, les catégories de couverture et les données nécessaires au suivi des problèmes
d'indexation.

`GoogleSearchConsoleSitemap`

Ce modèle représente les sitemaps connus pour une propriété. Il doit permettre de stocker l'URL du sitemap, les dates
connues, l'état de traitement et les informations de suivi utiles.

`GoogleSearchConsoleImport`

Ce modèle représente un import Google Search Console. Il doit journaliser les déclenchements, les paramètres de période,
les statuts, les erreurs éventuelles, les volumes importés et les dates d'exécution afin de rendre les synchronisations
traçables.

Aucun modèle ne doit contenir de logique métier. Les modèles servent uniquement à représenter les tables PostgreSQL et
leurs relations.

## 5. Migration Alembic

La migration Alembic du Sprint 24A devra être explicite et lisible. Elle devra créer les tables, index et contraintes
nécessaires aux modèles Google Search Console.

Interdictions obligatoires :

- ne jamais utiliser `Base.metadata.create_all()` ;
- ne jamais utiliser `Base.metadata.drop_all()`.

La migration devra utiliser les primitives Alembic explicites :

- `op.create_table()` ;
- `op.create_index()` ;
- `op.drop_index()` ;
- `op.drop_table()`.

Les opérations de downgrade devront être cohérentes avec les opérations d'upgrade. Les index devront être nommés de
manière explicite afin de faciliter la maintenance et les futures évolutions.

## 6. Connecteur Google Search Console

Le connecteur Google Search Console prévu doit isoler toute communication avec les API Google. Il ne doit pas dépendre
des routes API et ne doit pas porter la logique métier de la plateforme.

Le connecteur devra être :

- injectable ;
- mockable ;
- indépendant des services métier ;
- sans secret codé en dur ;
- sans appel Internet pendant les tests.

Le service métier devra pouvoir recevoir une implémentation réelle du connecteur en production et une implémentation
mockée pendant les tests. Cette séparation garantit des tests déterministes et évite tout couplage entre la logique
métier et l'infrastructure Google.

## 7. OAuth

Le Sprint 24A prépare l'authentification OAuth Google côté backend.

Contraintes obligatoires :

- aucun secret en dur dans le code ;
- stockage sécurisé des tokens et informations sensibles ;
- réutilisation du chiffrement existant si une solution est déjà disponible dans le projet ;
- aucune authentification Google côté Desktop.

Le Desktop ne doit jamais recevoir de secret Google ni gérer directement les échanges OAuth avec Google. Toute
authentification, conservation de token, rotation ou révocation doit être conçue comme une responsabilité backend.

## 8. Services métier

Le service métier principal prévu est `GoogleSearchConsoleService`.

Il devra gérer :

- lecture des propriétés ;
- lecture des performances ;
- lecture de l'indexation ;
- lecture des sitemaps ;
- lancement d'import ;
- historisation ;
- gestion des erreurs ;
- orchestration du connecteur.

Le service doit être la couche de coordination entre les routes REST, le connecteur Google Search Console et les
repositories. Il doit centraliser les règles d'idempotence, la validation métier des périodes d'import, la transformation
des réponses du connecteur et la journalisation des résultats d'import.

## 9. Repositories

Le repository Google Search Console devra être limité aux accès SQLAlchemy.

Opérations attendues :

- lecture ;
- création ;
- mise à jour ;
- suppression ;
- upsert ou idempotence si nécessaire.

Aucune logique métier ne doit être placée dans le repository. Les repositories ne décident pas quand importer, comment
interpréter les erreurs Google ou quelle stratégie métier appliquer. Ils exécutent uniquement les opérations de
persistance demandées par le service.

## 10. API REST

Les endpoints REST prévus doivent couvrir les familles suivantes :

- propriétés ;
- performances ;
- indexation ;
- sitemaps ;
- import manuel ;
- historique des imports.

Les routes ne doivent pas inventer d'implémentation complexe. Elles doivent rester fines, appeler le service
`GoogleSearchConsoleService`, gérer les entrées et sorties via les schemas Pydantic, puis retourner des réponses
prévisibles.

Toutes les routes devront être protégées par les mécanismes d'authentification et de permission existants dans le
backend. Le Sprint 24A ne doit pas créer un système de sécurité parallèle.

Compléments REST ajoutés pour le Sprint 24B :

- `/performances` accepte les filtres `start_date`, `end_date`, `page`, `query`, `country` et `device`.
- Les propriétés exposent `last_sync_at`, calculé depuis le dernier import terminé avec succès ou partiellement.
- `/indexation` expose les agrégats `valid_pages`, `excluded_pages`, `errors` et `warnings`.
- Les sitemaps exposent `url_count`, calculé depuis les contenus importés lorsqu'ils sont disponibles.
- Les imports exposent `duration_seconds`, calculé depuis `started_at` et `completed_at`.

Ces compléments sont calculés côté service et n'ajoutent aucune colonne SQLAlchemy ni migration Alembic.

## 11. Import des données

Le flux d'import attendu est le suivant :

```text
Google Search Console
    -> Connecteur
        -> Service
            -> Repository
                -> PostgreSQL
```

Les imports devront être :

- idempotents ;
- journalisés ;
- testables ;
- indépendants du Desktop.

L'idempotence doit éviter la création de doublons lorsqu'un import est relancé sur la même propriété, la même période et
les mêmes dimensions. La journalisation doit permettre de comprendre ce qui a été importé, quand, avec quel statut et
avec quelle erreur éventuelle.

Le Desktop ne doit pas déclencher d'appel Google direct. Il pourra uniquement demander au backend de lancer ou consulter
un import via les endpoints REST prévus.

## 12. Tests prévus

Les tests attendus pour l'implémentation future sont :

- tests modèles ;
- tests repository ;
- tests service ;
- tests connecteur mock ;
- tests routes API ;
- tests import idempotent.

Contraintes de test :

- aucun appel Internet ;
- connecteur Google mocké ;
- tests déterministes.

Les tests de service devront vérifier l'orchestration, les cas d'erreur et l'idempotence. Les tests de repository devront
valider les accès SQLAlchemy sans logique métier. Les tests de routes devront vérifier les statuts HTTP, les réponses
Pydantic et l'application des mécanismes d'authentification ou permission existants.

## 13. Hors périmètre

Le Sprint 24A ne comprend pas :

- interface Desktop ;
- Dashboard ;
- Google Analytics 4 ;
- Bing Webmaster Tools ;
- planification automatique ;
- appels Google depuis le Desktop ;
- refactor global.

Ce sprint ne doit pas modifier les fonctionnalités existantes hors du périmètre Google Search Console backend. Il ne
doit pas introduire de refactor transversal ni réorganiser l'architecture du projet.

## 14. Fichiers prévus pour l'implémentation future

Les fichiers suivants sont prévus pour l'implémentation future. Ils ne sont pas créés par cette documentation :

- `backend/app/models/google_search_console.py`
- `backend/app/schemas/google_search_console.py`
- `backend/app/repositories/google_search_console.py`
- `backend/app/services/google_search_console.py`
- `backend/app/connectors/__init__.py`
- `backend/app/connectors/google_search_console.py`
- `backend/alembic/versions/20260707_0007_create_google_search_console.py`
- `backend/app/api/v1/routes/google_search_console.py`
- `tests/models/test_google_search_console_models.py`
- `tests/repositories/test_google_search_console_repository.py`
- `tests/services/test_google_search_console_service.py`
- `tests/connectors/test_google_search_console_connector.py`
- `tests/api/test_google_search_console_routes.py`

## 15. Conclusion

Le Sprint 24A constitue le socle backend indispensable avant le Sprint 24B. Il prépare l'intégration Google Search
Console en respectant la séparation entre API REST, services métier, repositories, modèles SQLAlchemy, connecteur Google
et stockage PostgreSQL.

Ce socle prépare les sprints suivants :

- Sprint 24B — Google Search Console Desktop ;
- Sprint 25 — Google Analytics 4 Backend ;
- Sprint 26 — Google Analytics 4 Desktop ;
- Sprint 27 — Bing Webmaster Tools.

Le résultat attendu du Sprint 24A est un backend Google Search Console fiable, testable, sécurisé et indépendant du
Desktop, prêt à être consommé par les interfaces futures.
