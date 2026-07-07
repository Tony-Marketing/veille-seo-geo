# Sprint 25 - Google Analytics 4 Backend

## 1. Objectifs du Sprint
Le Sprint 25 ouvre l'integration backend complete de Google Analytics 4 dans la plateforme Veille SEO-GEO Groupe A.P&Partner. Le Sprint 24B a termine l'integration Desktop de Google Search Console. Le module Google Search Console est operationnel et sert de reference d'architecture pour ce nouveau module. Le Sprint 25 doit creer le cadrage backend permettant une implementation ulterieure claire, testable et securisee. Le Desktop Google Analytics 4 est explicitement reserve au Sprint 26.
Ce sprint doit preparer un module GA4 autonome, sans melanger sa logique avec Google Search Console, le Dashboard ou le Desktop. Objectifs fonctionnels principaux :
| Objectif | Description | Resultat attendu |
|---|---|---|
| Proprietes GA4 | Gerer les proprietes Google Analytics 4 suivies par la plateforme | Referentiel backend des proprietes |
| OAuth | Preparer OAuth 2.0 cote backend | Connexion securisee sans secret cote client |
| Import manuel | Declencher un import GA4 a la demande | Import tracable et idempotent |
| Donnees Analytics | Stocker metriques et dimensions minimales | Historique exploitable par les sprints suivants |
| Historique | Journaliser chaque import | Audit, diagnostic et suivi operationnel |
| API REST | Exposer les contrats backend conceptuels | Consommation future par le Sprint 26 |
| Tests | Definir une strategie de tests isoles | Aucun appel Internet pendant les tests |
Le Sprint 25 doit livrer un socle backend. Il ne doit pas livrer d'interface utilisateur. Il ne doit pas livrer de graphiques. Il ne doit pas livrer de synchronisation automatique. Il ne doit pas livrer de planification.
Les donnees GA4 devront pouvoir etre exploitees plus tard par les modules SEO, GEO, Dashboard et reporting. Ces exploitations croisees ne sont pas realisees dans ce sprint. Le module doit etre concu pour evoluer sans reecriture globale. Les futures implementations devront respecter les conventions existantes du depot.

## 2. Perimetre
Le perimetre du Sprint 25 est strictement backend. Il couvre les elements necessaires a l'integration future de Google Analytics 4. Il doit rester coherent avec l'architecture backend officielle du projet. Flux obligatoire :

```text
Routes
  |
  v
Services
  |
  v
Repositories
  |
  v
Models

```

### 2.1 Proprietes Google Analytics 4
Le module devra permettre de referencer les proprietes GA4 suivies par la plateforme. Une propriete GA4 represente une source Analytics rattachee a un site, une entite ou un contexte marketing interne. Le referentiel devra conserver l'identifiant GA4, le nom affichable, l'etat d'activation et les metadonnees utiles. Le systeme devra supporter plusieurs proprietes. Une propriete inactive ne devra pas etre importee par defaut.
La suppression physique devra etre evitee lorsque des donnees importees existent deja.

### 2.2 OAuth preparatoire
Le Sprint 25 doit preparer OAuth 2.0 cote backend. Le backend doit etre le seul responsable des echanges OAuth avec Google. Le Desktop ne doit jamais recevoir de client secret. Le Desktop ne doit jamais manipuler de refresh token. Les tokens devront etre chiffres avant stockage.
Aucun secret ne devra etre present dans le depot. Le renouvellement des tokens doit etre prevu mais pas automatise dans ce sprint.

### 2.3 Import manuel
Le module devra prevoir un import manuel declenche via API REST. L'import manuel devra accepter une propriete GA4 et une periode. Il devra recuperer les metriques et dimensions standard du sprint. Il devra produire un historique d'execution. Il devra etre idempotent.
Il devra etre testable avec un connecteur mocke.

### 2.4 Stockage des donnees
Le Sprint 25 doit prevoir le stockage durable des donnees importees. Les familles de donnees sont :
- proprietes GA4 ;
- metriques GA4 ;
- dimensions GA4 ;
- imports GA4.
Le stockage doit etre suffisamment generique pour ajouter des metriques ou dimensions plus tard. Il ne doit pas etre concu uniquement pour un premier ecran Desktop. Il doit preparer l'analyse marketing, SEO, GEO et reporting.

### 2.5 Historique des imports
Chaque import devra etre tracable. L'historique devra permettre d'identifier la propriete, la periode, les metriques, les dimensions et le statut. Il devra conserver les volumes recus, crees, mis a jour et ignores. Il devra conserver les erreurs controlees sans exposer de secret. Il devra permettre de diagnostiquer une relance d'import.

### 2.6 Routes REST
Le Sprint 25 doit prevoir les routes REST backend. Ces routes seront consommees par le Sprint 26 Desktop. Elles devront rester fines. Elles devront utiliser des schemas Pydantic dedies. Elles devront appeler les services.
Elles ne devront contenir aucune logique metier.

### 2.7 Tests
Les tests futurs devront couvrir models, repositories, services, connecteur, OAuth et routes. Aucun test ne devra effectuer d'appel Internet reel. Le connecteur GA4 devra etre injectable et mockable. La couverture attendue doit etre comparable au Sprint 24A Google Search Console Backend.

## 3. Hors perimetre
Le Sprint 25 ne couvre pas les interfaces utilisateur. Le Sprint 25 ne couvre pas le Desktop. Le Sprint 25 ne couvre pas React. Le Sprint 25 ne couvre pas les graphiques. Le Sprint 25 ne couvre pas le Dashboard.
Le Sprint 25 ne couvre pas les synchronisations automatiques. Le Sprint 25 ne couvre pas le monitoring. Le Sprint 25 ne couvre pas la planification. Le Sprint 25 ne couvre pas les taches periodiques. Le Sprint 25 ne couvre pas les workers.
Le Sprint 25 ne couvre pas les alertes. Le Sprint 25 ne couvre pas les exports CSV, PDF ou Excel. Le Sprint 25 ne couvre pas le rapprochement avance entre GA4 et Google Search Console. Le Sprint 25 ne couvre pas l'analyse GEO enrichie par GA4. Le Sprint 25 ne couvre pas les rapports decisionnels.
Le Sprint 25 ne couvre pas la refonte d'un module existant. Le Sprint 25 ne couvre pas la creation d'une architecture parallele. Table de hors perimetre :
| Element exclu | Raison |
|---|---|
| Desktop PySide6 | Reserve au Sprint 26 |
| React | Non concerne par ce sprint backend |
| Graphiques | Necessitent une interface future |
| Dashboard | Exploitation prevue plus tard |
| Synchronisation automatique | Necessite scheduler ou worker |
| Monitoring | Sujet d'observabilite futur |
| Taches periodiques | Hors socle initial |
| Exports | Non necessaires pour l'import backend |
| Reporting avance | Depend des donnees stabilisees |
| Appels Google depuis Desktop | Interdits par architecture |
| Secrets cote client | Interdits par securite |
| Refactor global | Hors perimetre |
Aucune page Desktop ne doit etre creee. Aucun composant React ne doit etre cree. Aucune navigation utilisateur ne doit etre modifiee. Aucun graphique ne doit etre ajoute.

## 4. Architecture
L'architecture backend obligatoire est la suivante :

```text
Client HTTP futur
        |
        v
Routes FastAPI
        |
        v
Services metier
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
Le connecteur GA4 est une dependance technique appelee par la couche service. Il ne doit pas etre appele depuis les routes. Il ne doit pas etre appele depuis les repositories. Il ne doit pas etre appele depuis les models. Vue cible :

```text
POST /api/v1/google-analytics/import
        |
        v
Route REST GA4
        |
        v
GoogleAnalyticsService
        |
        +------------------------------+
        |                              |
        v                              v
GoogleAnalyticsConnector       GoogleAnalyticsRepository
        |                              |
        v                              v
Google Analytics Data API       SQLAlchemy Models
                                       |
                                       v
                                  PostgreSQL

```

### 4.1 Routes
Les routes exposent les cas d'usage HTTP. Elles declarent les methodes, chemins, parametres, schemas d'entree et schemas de sortie. Elles injectent les dependances necessaires. Elles appellent les services. Elles retournent des reponses controlees.
Elles ne construisent pas de requetes SQLAlchemy. Elles ne transforment pas les reponses Google. Elles ne decident pas de l'idempotence. Elles ne chiffrent pas les tokens directement. Elles ne contiennent aucune logique metier.

### 4.2 Services
Les services portent toute la logique metier. Ils valident les periodes d'import. Ils valident les proprietes. Ils orchestrent OAuth, connecteur et repositories. Ils interpretent les reponses du connecteur.
Ils appliquent les regles d'idempotence. Ils normalisent les metriques et dimensions. Ils journalisent les imports. Ils convertissent les erreurs techniques en erreurs metier.

### 4.3 Repositories
Les repositories sont limites aux acces SQLAlchemy. Ils lisent, creent, mettent a jour et desactivent les donnees. Ils peuvent executer des upserts si le service le demande. Ils ne decident pas des regles metier. Ils ne connaissent pas les routes FastAPI.
Ils n'appellent jamais Google. Ils ne manipulent pas les reponses brutes de l'API Google.

### 4.4 Models
Les models representent les tables PostgreSQL. Ils definissent colonnes, relations, index et contraintes conceptuelles. Ils ne contiennent pas de logique metier. Ils ne contiennent pas de logique OAuth. Ils ne contiennent pas de logique HTTP.
Ils doivent rester coherents avec les migrations Alembic futures.

### 4.5 Schemas
Les schemas Pydantic representent les contrats API. Ils distinguent creation, mise a jour, lecture, listes, imports et OAuth. Ils ne sont pas des models SQLAlchemy. Ils ne doivent pas exposer de secret. Ils doivent preparer des reponses stables pour le Sprint 26.

### 4.6 Connecteur GA4
Le connecteur GA4 isole toute communication avec Google Analytics. Il construit les appels techniques. Il gere les erreurs techniques Google. Il retourne des donnees exploitables par le service. Il ne persiste rien.
Il ne porte pas les regles metier de la plateforme. Il doit etre injectable. Il doit etre mockable. Il ne doit contenir aucun secret code en dur.

## 5. Modele de donnees
Cette section decrit conceptuellement les futures tables. Elle ne contient aucun code SQLAlchemy. Elle ne contient aucune migration Alembic. Vue globale :

```text
google_analytics_properties
        |
        +-- google_analytics_metrics
        |
        +-- google_analytics_dimensions
        |
        +-- google_analytics_imports

```

### 5.1 `google_analytics_properties`
Cette table representera les proprietes Google Analytics 4 suivies par la plateforme.
| Champ | Role | Remarque |
|---|---|---|
| `id` | Identifiant interne | Cle primaire |
| `property_id` | Identifiant GA4 | Identifiant fourni par Google |
| `display_name` | Nom affichable | Pour administration et Desktop futur |
| `website_id` | Site interne associe | Relation future si applicable |
| `account_name` | Compte Google associe | Metadonnee optionnelle |
| `currency_code` | Devise | Utile pour `totalRevenue` |
| `time_zone` | Fuseau horaire GA4 | Important pour les dates |
| `is_active` | Etat interne | Desactivation sans suppression |
| `last_import_at` | Dernier import reussi | Suivi operationnel |
| `created_at` | Creation | Audit |
| `updated_at` | Modification | Audit |
Contraintes conceptuelles :
- `property_id` doit etre unique dans le perimetre retenu ;
- une propriete inactive ne doit pas etre importee par defaut ;
- la suppression physique doit etre evitee si des donnees existent ;
- les dates doivent suivre les conventions backend existantes.

### 5.2 `google_analytics_metrics`
Cette table representera les metriques importees depuis GA4. Une ligne correspondra a une propriete, une date et une combinaison de dimensions.
| Champ | Role | Remarque |
|---|---|---|
| `id` | Identifiant interne | Cle primaire |
| `property_id` | Propriete interne | Reference propriete |
| `import_id` | Import source | Reference historique |
| `date` | Date de mesure | Dimension temporelle |
| `source` | Source trafic | Nullable selon import |
| `medium` | Medium trafic | Nullable selon import |
| `campaign` | Campagne | Nullable |
| `device_category` | Type d'appareil | Desktop, mobile, tablet |
| `country` | Pays | Analyse geographique |
| `users` | Utilisateurs | Metrique GA4 |
| `new_users` | Nouveaux utilisateurs | Metrique GA4 |
| `sessions` | Sessions | Metrique GA4 |
| `engaged_sessions` | Sessions engagees | Metrique GA4 |
| `screen_page_views` | Pages vues | Metrique GA4 |
| `average_session_duration` | Duree moyenne | Decimal |
| `engagement_rate` | Taux d'engagement | Decimal |
| `conversions` | Conversions | Numerique |
| `total_revenue` | Revenus | Decimal |
| `created_at` | Creation | Audit |
| `updated_at` | Modification | Audit |
Regles conceptuelles :
- relancer un import identique ne doit pas creer de doublons ;
- les metriques numeriques doivent etre normalisees avant persistance ;
- les valeurs absentes doivent etre traitees explicitement ;
- l'idempotence est decidee par le service et appliquee par le repository.

### 5.3 `google_analytics_dimensions`
Cette table referencera les dimensions GA4 supportees. Elle permettra d'etendre la liste sans disperser les constantes dans toutes les couches.
| Champ | Role | Remarque |
|---|---|---|
| `id` | Identifiant interne | Cle primaire |
| `name` | Nom technique GA4 | Exemple : `source` |
| `display_name` | Nom affichable | Libelle interne |
| `description` | Description | Documentation courte |
| `is_default` | Dimension par defaut | Import standard |
| `is_active` | Dimension active | Extension progressive |
| `created_at` | Creation | Audit |
| `updated_at` | Modification | Audit |
Dimensions minimales :
| Dimension GA4 | Usage |
|---|---|
| `date` | Historisation quotidienne |
| `source` | Acquisition |
| `medium` | Acquisition |
| `campaign` | Campagnes marketing |
| `deviceCategory` | Appareil |
| `country` | Geographie |

### 5.4 `google_analytics_imports`
Cette table historisera les imports GA4.
| Champ | Role | Remarque |
|---|---|---|
| `id` | Identifiant interne | Cle primaire |
| `property_id` | Propriete importee | Reference interne |
| `requested_start_date` | Debut demande | Date |
| `requested_end_date` | Fin demandee | Date |
| `metrics_requested` | Metriques demandees | Structure serialisee ou adaptee |
| `dimensions_requested` | Dimensions demandees | Structure serialisee ou adaptee |
| `status` | Statut import | Pending, running, success, failed, partial |
| `rows_received` | Lignes recues | Diagnostic |
| `rows_created` | Lignes creees | Audit |
| `rows_updated` | Lignes mises a jour | Audit |
| `rows_skipped` | Lignes ignorees | Idempotence |
| `error_code` | Code erreur | Sans secret |
| `error_message` | Message controle | Sans secret |
| `started_at` | Debut execution | Duree |
| `completed_at` | Fin execution | Duree |
| `created_by_user_id` | Utilisateur declencheur | Audit |
| `created_at` | Creation | Audit |
Statuts conceptuels :
| Statut | Signification |
|---|---|
| `pending` | Import cree mais non execute |
| `running` | Import en cours |
| `success` | Import termine sans erreur |
| `failed` | Import echoue |
| `partial` | Import termine avec donnees partielles |

## 6. OAuth
La strategie retenue est OAuth 2.0. OAuth doit etre gere cote backend. Le Desktop ne doit jamais recevoir ni stocker de secret Google. Les tokens sont des secrets applicatifs. Ils doivent etre chiffres avant stockage.
Ils ne doivent jamais etre retournes par l'API. Ils ne doivent jamais apparaitre dans les logs. Principes obligatoires :
| Sujet | Regle |
|---|---|
| Protocole | OAuth 2.0 |
| Client secret | Jamais en dur |
| Stockage tokens | Chiffre |
| Logs | Aucun token |
| Tests | Tokens fictifs uniquement |
| Connecteur | Injectable et mockable |
| Refresh | Prevu mais non automatise |
Le service OAuth devra reutiliser un mecanisme de chiffrement existant si le projet en possede un. Si aucun mecanisme n'existe, l'implementation future devra justifier l'ajout d'une solution dediee. Le renouvellement manuel pourra etre expose via endpoint. Le renouvellement automatique periodique est hors perimetre. Cas OAuth a prevoir en tests :
- token valide ;
- token absent ;
- token expire ;
- refresh reussi ;
- refresh refuse ;
- acces propriete refuse ;
- quota Google atteint ;
- reponse OAuth invalide.
Le connecteur GA4 devra recevoir les credentials depuis le service. Il ne devra pas lire directement des secrets depuis les routes. Il devra pouvoir etre remplace par une implementation de test.

## 7. Import manuel
L'import manuel est le premier mode d'integration GA4. Il doit permettre a un utilisateur autorise de demander l'import d'une propriete sur une periode. Flux cible :

```text
Utilisateur autorise
        |
        v
POST /api/v1/google-analytics/import
        |
        v
Route REST
        |
        v
GoogleAnalyticsService
        |
        +--> Valide propriete
        +--> Valide periode
        +--> Cree historique import
        +--> Appelle GoogleAnalyticsConnector
        +--> Normalise resultats
        +--> Applique idempotence
        +--> Persiste metriques
        +--> Met a jour historique
        |
        v
Reponse API

```
Metriques minimales :
| Metrique GA4 | Description | Type conceptuel |
|---|---|---|
| `users` | Utilisateurs | Entier |
| `newUsers` | Nouveaux utilisateurs | Entier |
| `sessions` | Sessions | Entier |
| `engagedSessions` | Sessions engagees | Entier |
| `screenPageViews` | Pages vues | Entier |
| `averageSessionDuration` | Duree moyenne | Decimal |
| `engagementRate` | Taux d'engagement | Decimal |
| `conversions` | Conversions | Numerique |
| `totalRevenue` | Revenus totaux | Decimal |
Dimensions minimales :
| Dimension GA4 | Description |
|---|---|
| `date` | Date de mesure |
| `source` | Source de trafic |
| `medium` | Medium de trafic |
| `campaign` | Campagne |
| `deviceCategory` | Categorie d'appareil |
| `country` | Pays |
La persistance pourra utiliser des noms snake_case. Le mapping entre noms GA4 et noms internes devra etre centralise. L'idempotence attendue repose conceptuellement sur :

```text
property_id
+ date
+ source
+ medium
+ campaign
+ device_category
+ country

```
Relancer le meme import ne doit pas creer de doublons. Une ligne existante pourra etre mise a jour, ignoree ou remplacee de maniere controlee selon la strategie retenue. Le service decide la strategie. Le repository applique l'operation demandee. L'historique indique les lignes creees, mises a jour et ignorees.
Erreurs a prevoir :
| Erreur | Traitement attendu |
|---|---|
| Propriete inconnue | Erreur metier controlee |
| Propriete inactive | Refus d'import |
| Periode invalide | Validation service |
| Token absent | Erreur OAuth controlee |
| Token expire | Refresh manuel possible |
| Acces Google refuse | Import echoue |
| Quota atteint | Import echoue avec code dedie |
| Reponse vide | Import termine avec zero ligne |
| Format inattendu | Import echoue sans crash non maitrise |

## 8. Endpoints REST prevus
Cette section est conceptuelle. Elle ne contient aucun code FastAPI. Prefixe recommande :

```text
/api/v1/google-analytics

```
Endpoints minimaux :
| Methode | Endpoint conceptuel | Role |
|---|---|---|
| `GET` | `/properties` | Lister les proprietes GA4 |
| `POST` | `/properties` | Creer une propriete GA4 |
| `PUT` | `/properties/{id}` | Mettre a jour une propriete |
| `DELETE` | `/properties/{id}` | Desactiver ou supprimer selon regle |
| `POST` | `/import` | Declencher un import manuel |
| `GET` | `/imports` | Lister les imports |
| `GET` | `/imports/{id}` | Lire le detail d'un import |
| `POST` | `/oauth/connect` | Initialiser ou finaliser OAuth |
| `POST` | `/oauth/refresh` | Rafraichir manuellement un token |
Vue conceptuelle :

```text
GET    /api/v1/google-analytics/properties
POST   /api/v1/google-analytics/properties
PUT    /api/v1/google-analytics/properties/{id}
DELETE /api/v1/google-analytics/properties/{id}
POST   /api/v1/google-analytics/import GET    /api/v1/google-analytics/imports GET    /api/v1/google-analytics/imports/{id} POST   /api/v1/google-analytics/oauth/connect POST   /api/v1/google-analytics/oauth/refresh ``` Toutes les routes devront etre authentifiees. Les actions sensibles devront exiger des droits administrateur ou une permission dediee. Les erreurs devront suivre les conventions API existantes.
Les reponses devront etre controlees par schemas Pydantic.

## 9. Services prevus
Cette section decrit les services futurs sans implementation.

### 9.1 `GoogleAnalyticsService`
Service metier principal du module. Responsabilites :
- lister les proprietes ;
- creer une propriete ;
- mettre a jour une propriete ;
- desactiver une propriete ;
- valider une demande d'import ;
- creer l'historique d'import ;
- appeler le connecteur GA4 ;
- normaliser metriques et dimensions ;
- appliquer l'idempotence ;
- demander la persistance ;
- mettre a jour le statut final ;
- preparer les reponses API.
Le service ne doit pas dependre du Desktop. Le service ne doit pas exposer de token. Le service doit etre testable avec un connecteur mocke.

### 9.2 `GoogleAnalyticsConnector`
Connecteur technique vers Google Analytics 4. Responsabilites :
- construire les requetes vers l'API GA4 ;
- transmettre metriques et dimensions ;
- gerer les erreurs techniques Google ;
- parser les reponses ;
- retourner une structure exploitable par le service ;
- ne rien persister ;
- ne pas decider des regles metier ;
- ne contenir aucun secret en dur.
Le connecteur doit etre injectable. Il doit pouvoir utiliser un transport HTTP simule en tests.

### 9.3 `GoogleAnalyticsOAuthService`
Service dedie a OAuth. Responsabilites :
- preparer la connexion OAuth ;
- traiter le retour OAuth si necessaire ;
- chiffrer les tokens ;
- dechiffrer uniquement au moment utile ;
- rafraichir manuellement un token ;
- tracer les erreurs OAuth ;
- masquer toute donnee sensible.
Ce service ne doit pas etre melange avec la logique d'import.

## 10. Repositories prevus
Les repositories GA4 seront limites aux acces SQLAlchemy. Un repository principal pourra suffire au demarrage. Des repositories specialises pourront etre ajoutes si la complexite augmente. Responsabilites conceptuelles :
| Responsabilite | Description |
|---|---|
| Proprietes | Lire, creer, mettre a jour, desactiver |
| Metriques | Inserer ou mettre a jour de facon idempotente |
| Dimensions | Lire dimensions actives ou par defaut |
| Imports | Creer et mettre a jour l'historique |
| Filtres | Appliquer les filtres SQL necessaires |
| Pagination | Fournir les listes paginees si necessaire |
Operations minimales :
- `list_properties` ;
- `get_property_by_id` ;
- `get_property_by_google_id` ;
- `create_property` ;
- `update_property` ;
- `deactivate_property` ;
- `create_import` ;
- `update_import_status` ;
- `list_imports` ;
- `get_import_by_id` ;
- `upsert_metrics` ou operation equivalente ;
- `list_default_dimensions`.
Interdictions :
- pas d'appel HTTP ;
- pas de logique OAuth ;
- pas de logique metier autonome ;
- pas de dependance FastAPI ;
- pas de secret en clair dans les logs ;
- pas de schema Pydantic impose comme objet interne.
Les noms exacts devront suivre les conventions du code existant.

## 11. Schemas Pydantic prevus
Les schemas Pydantic representent les contrats API. Ils ne remplacent pas les models SQLAlchemy. Ils ne doivent jamais exposer de token OAuth brut. Schemas conceptuels :
| Schema | Role |
|---|---|
| `GoogleAnalyticsPropertyCreate` | Entree creation propriete |
| `GoogleAnalyticsPropertyUpdate` | Entree mise a jour propriete |
| `GoogleAnalyticsPropertyRead` | Sortie lecture propriete |
| `GoogleAnalyticsPropertyList` | Liste ou page de proprietes |
| `GoogleAnalyticsImportRequest` | Entree declenchement import |
| `GoogleAnalyticsImportRead` | Sortie detail import |
| `GoogleAnalyticsImportList` | Liste ou page d'imports |
| `GoogleAnalyticsImportSummary` | Resume resultat import |
| `GoogleAnalyticsMetricRead` | Lecture future metrique |
| `GoogleAnalyticsDimensionRead` | Lecture future dimension |
| `GoogleAnalyticsOAuthConnectRequest` | Entree connexion OAuth |
| `GoogleAnalyticsOAuthConnectResponse` | Reponse OAuth sans secret |
| `GoogleAnalyticsOAuthRefreshRequest` | Entree refresh manuel |
| `GoogleAnalyticsOAuthRefreshResponse` | Resultat refresh sans token brut |
Regles de validation :
- propriete obligatoire pour un import ;
- dates obligatoires pour un import ;
- `start_date` inferieur ou egal a `end_date` ;
- metriques limitees a la liste supportee ;
- dimensions limitees a la liste supportee ;
- sorties sans secrets ;
- erreurs compatibles avec le Desktop futur.
Champs a ne jamais exposer :
- access token ;
- refresh token ;
- client secret ;
- code OAuth brut inutile ;
- reponse OAuth complete ;
- header Authorization ;
- detail technique Google sensible.

## 12. Tests
Les tests devront etre precis, rapides et deterministes. Ils devront utiliser pytest. Ils devront suivre une couverture similaire au Sprint 24A. Aucun test ne doit effectuer d'appel Internet. Le connecteur doit etre mockable.
`MockTransport` ou un equivalent devra etre utilise lorsque le connecteur HTTP est teste.

### 12.1 Tests models
Tests a prevoir :
- creation d'une propriete ;
- contraintes d'unicite ;
- relations propriete, metriques et imports ;
- valeurs par defaut ;
- timestamps ;
- statuts d'import.

### 12.2 Tests repositories
Tests a prevoir :
- creation d'une propriete ;
- lecture par identifiant interne ;
- lecture par identifiant GA4 ;
- mise a jour ;
- desactivation ;
- creation d'un import ;
- mise a jour du statut ;
- listing des imports ;
- insertion idempotente des metriques ;
- absence de doublons sur relance.

### 12.3 Tests services
Tests a prevoir :
- refus propriete inconnue ;
- refus propriete inactive ;
- refus periode invalide ;
- import reussi avec connecteur mocke ;
- import avec reponse vide ;
- import partiel ;
- erreur OAuth ;
- quota atteint ;
- idempotence sur import repete ;
- historique correctement renseigne ;
- absence de token dans les reponses.

### 12.4 Tests connecteur
Tests a prevoir :
- construction de requete GA4 ;
- mapping des metriques ;
- mapping des dimensions ;
- parsing d'une reponse valide ;
- parsing d'une reponse vide ;
- erreur 401 ;
- erreur 403 ;
- erreur 429 ;
- erreur 500 ;
- aucun appel reseau reel.

### 12.5 Tests routes API
Tests a prevoir :
- `GET /properties` ;
- `POST /properties` ;
- `PUT /properties/{id}` ;
- `DELETE /properties/{id}` ;
- `POST /import` ;
- `GET /imports` ;
- `GET /imports/{id}` ;
- `POST /oauth/connect` ;
- `POST /oauth/refresh` ;
- authentification obligatoire ;
- refus sans droits requis ;
- validation payload ;
- codes HTTP attendus ;
- format de reponse Pydantic.

### 12.6 Commandes qualite attendues
Commandes a executer apres implementation future :

```powershell
py -m ruff check .
py -m pytest

```
Si Black est utilise dans le projet au moment de l'implementation, il devra etre applique selon les conventions existantes. Matrice minimale :
| Couche | Tests requis | Reseau autorise |
|---|---|---|
| Models | Oui | Non |
| Repositories | Oui | Non |
| Services | Oui | Non |
| Connecteur | Oui avec transport simule | Non |
| Routes | Oui | Non |
| OAuth | Oui avec mocks | Non |

## 13. Securite
La securite est obligatoire des le Sprint 25. GA4 implique des donnees marketing sensibles et des tokens OAuth.

### 13.1 Authentification obligatoire
Toutes les routes GA4 devront etre protegees. Aucun endpoint GA4 ne doit etre public. Les tests devront verifier le refus des acces non authentifies.

### 13.2 Droits administrateur
Les actions sensibles devront exiger des droits administrateur ou une permission dediee. Actions sensibles :
- connexion OAuth ;
- refresh OAuth ;
- creation de propriete ;
- modification de propriete ;
- suppression ou desactivation de propriete ;
- declenchement d'import manuel.
La consultation pourra etre ouverte a d'autres roles si la matrice de permissions future le prevoit.

### 13.3 Chiffrement des secrets
Les tokens OAuth doivent etre chiffres. Le client secret ne doit pas etre versionne. Les secrets doivent rester dans l'environnement ou un mecanisme securise. Le depot Git ne doit contenir aucun secret reel.

### 13.4 Logs
Les logs ne doivent pas contenir :
- access token ;
- refresh token ;
- client secret ;
- code OAuth ;
- header Authorization ;
- reponse OAuth brute ;
- donnees personnelles inutiles.

### 13.5 Donnees personnelles
Le Sprint 25 doit eviter tout stockage inutile de donnees personnelles. Les dimensions retenues sont agregees et marketing. Le module ne doit pas collecter d'identifiants utilisateurs individuels.

## 14. Criteres de validation
Le Sprint 25 sera valide lors de l'implementation future si les criteres suivants sont respectes. Architecture :
- architecture `Routes -> Services -> Repositories -> Models` respectee ;
- aucune logique metier dans les routes ;
- aucune requete SQLAlchemy dans les routes ;
- aucun appel HTTP Google dans les routes ;
- connecteur GA4 isole ;
- services testables ;
- repositories limites aux acces SQLAlchemy ;
- schemas Pydantic dedies.
Fonctionnel :
- proprietes GA4 gerees cote backend ;
- OAuth prepare cote backend ;
- import manuel disponible ;
- metriques minimales importables ;
- dimensions minimales importables ;
- historique d'import persistant ;
- idempotence verifiee ;
- erreurs controlees.
Securite :
- routes authentifiees ;
- actions sensibles reservees aux administrateurs ou permissions dediees ;
- aucun secret dans le depot ;
- tokens chiffres ;
- tokens jamais exposes par API ;
- logs sans secrets.
Tests :
- tests models presents ;
- tests repositories presents ;
- tests services presents ;
- tests connecteur presents ;
- tests routes presents ;
- tests OAuth presents ;
- aucun appel reseau pendant les tests ;
- connecteur mocke ;
- `MockTransport` ou equivalent utilise lorsque pertinent.
Qualite :
- Ruff OK ;
- Pytest OK ;
- documentation mise a jour ;
- aucune regression des tests existants ;
- aucune nouvelle dependance non justifiee ;
- migrations Alembic explicites lors de l'implementation future ;
- coherence avec l'architecture backend officielle.
Checklist finale :
| Critere | Attendu |
|---|---|
| Ruff | OK |
| Pytest | OK |
| Architecture | Respectee |
| Reseau en tests | Aucun appel reel |
| Documentation | Mise a jour |
| Secrets | Aucun dans Git |
| OAuth | Tokens chiffres |
| Idempotence | Testee |
| Desktop | Non modifie |
| Dashboard | Non modifie |

## 15. Preparation des Sprints suivants
Le Sprint 25 doit etre concu comme un socle durable.

### 15.1 Sprint 25A
Sprint 25A pourra completer ou durcir le backend GA4. Axes possibles :
- enrichissement des filtres ;
- durcissement OAuth ;
- amelioration de l'idempotence ;
- meilleure granularite des imports ;
- optimisation repository ;
- documentation API plus detaillee ;
- tests de cas limites supplementaires.
Sprint 25A ne doit pas introduire de Desktop si la separation est maintenue.

### 15.2 Sprint 26
Sprint 26 sera dedie au Desktop Google Analytics 4. Il consommera exclusivement l'API REST backend. Il ne devra pas appeler Google directement. Il ne devra pas acceder a PostgreSQL. Il ne devra pas manipuler SQLAlchemy.
Il devra afficher proprietes, imports, resultats et erreurs exposees par l'API. Le Sprint 25 doit donc produire des contrats API stables.

### 15.3 Sprint 27
Sprint 27 pourra ouvrir Bing Webmaster Tools ou un autre connecteur de visibilite. Le Sprint 25 doit servir de modele :
- connecteur isole ;
- services metier ;
- repositories SQLAlchemy ;
- imports idempotents ;
- historique d'import ;
- tests sans reseau.

### 15.4 Sprint 28
Sprint 28 pourra consolider les donnees SEO, GSC et GA4. Le Sprint 25 doit permettre les rapprochements futurs :
- trafic organique ;
- sources et mediums ;
- pages vues ;
- conversions ;
- revenus ;
- comparaison avec performances GSC.
Ces croisements ne sont pas developpes dans le Sprint 25.

### 15.5 Sprint 29
Sprint 29 pourra preparer le reporting et les indicateurs consolides. Les donnees GA4 devront permettre :
- suivi par date ;
- suivi par campagne ;
- suivi par source ;
- suivi par medium ;
- suivi par appareil ;
- suivi par pays ;
- suivi des conversions ;
- suivi du revenu.

### 15.6 Sprint 30
Sprint 30 pourra traiter l'automatisation et la planification. Le Sprint 25 doit preparer cette evolution sans la developper. Preparations utiles :
- historique d'import clair ;
- statuts d'import ;
- periodes demandees ;
- erreurs normalisees ;
- idempotence ;
- separation service/connecteur ;
- absence de dependance Desktop.
Les taches periodiques ne sont pas dans le Sprint 25. Elles doivent pouvoir etre ajoutees plus tard sans reecrire le module.

## 16. Synthese operationnelle
Le Sprint 25 est le socle backend Google Analytics 4. Il doit respecter l'architecture backend officielle. Il doit preparer OAuth sans exposer de secret. Il doit permettre des imports manuels. Il doit stocker les metriques et dimensions minimales.
Il doit historiser les imports. Il doit fournir les contrats REST futurs pour le Desktop. Il doit etre teste sans appel reseau. Il doit preparer les sprints 25A, 26, 27, 28, 29 et 30. Ce document est la reference de developpement du Sprint 25.
Toute implementation future devra s'y conformer sauf decision de cadrage explicite contraire.

