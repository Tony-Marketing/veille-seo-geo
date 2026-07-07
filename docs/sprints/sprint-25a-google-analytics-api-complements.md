# Sprint 25A - Google Analytics 4 API Complements

## 1. Objectif du sprint

Le Sprint 25A a pour objectif de cadrer les complements d'API REST Google Analytics 4 necessaires au futur Desktop
Google Analytics. Il s'inscrit dans la continuite du Sprint 25, qui a livre le socle backend GA4 : modeles SQLAlchemy,
migration Alembic, repositories, services, connecteur injectable, preparation OAuth, schemas Pydantic, routes REST,
import manuel, historique des imports et tests backend.

Ce sprint ne vise pas a recreer le module Google Analytics 4. Il prepare l'exploitation des donnees GA4 deja importees
par une API REST plus complete, plus filtrable et directement consommable par le futur Sprint 26 Desktop.

L'objectif fonctionnel est de definir les contrats attendus pour :

- consulter les donnees GA4 avec pagination complete ;
- appliquer des filtres REST avances ;
- trier les resultats de maniere explicite ;
- exposer des agregats calcules cote backend ;
- fournir des KPIs directement exploitables par le Dashboard Desktop ;
- enrichir la consultation de l'historique des imports ;
- stabiliser des reponses REST homogenes pour les futurs ecrans Desktop.

Le Desktop Google Analytics futur devra rester un consommateur d'API. Il ne devra pas repliquer les calculs, contourner
les services backend ou acceder directement a la base de donnees. Le Sprint 25A prepare donc une API lisible,
testable, stable et conforme a l'architecture existante.

## 2. Hors perimetre

Le Sprint 25A est volontairement limite aux complements d'API REST backend. Les elements suivants sont explicitement
hors perimetre :

- aucune migration Alembic ;
- aucun nouveau modele SQLAlchemy ;
- aucune modification Desktop ;
- aucun composant React, PySide6 ou interface utilisateur ;
- aucune modification du Dashboard existant ;
- aucun appel Internet dans les tests ;
- aucune logique metier cote Desktop ;
- aucune synchronisation automatique ;
- aucun scheduler ou worker ;
- aucun export CSV, PDF ou Excel ;
- aucune refonte du module Google Analytics 4 ;
- aucune creation d'architecture parallele ;
- aucune modification de schema de base de donnees ;
- aucun secret ajoute au depot.

Les endpoints envisages devront s'appuyer sur les tables, modeles, repositories, services, schemas et routes existants.
Si une capacite attendue ne peut pas etre supportee sans modification de structure de donnees, elle devra etre signalee
comme limite fonctionnelle et non contournee par une migration ou un modele supplementaire dans ce sprint.

Le Desktop ne doit contenir aucune logique metier. Les calculs de totaux, ratios, moyennes, tendances, groupements,
normalisations et conversions de donnees restent exclusivement des responsabilites backend, principalement dans la
couche Service.

## 3. Architecture retenue

L'architecture retenue reste celle du backend existant :

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

Cette architecture doit etre respectee pour chaque complement d'API REST Google Analytics 4.

### 3.1 Routes

Les routes exposent les endpoints HTTP. Elles declarent les chemins, methodes, parametres de requete, dependances et
schemas de reponse. Elles doivent rester fines et previsibles.

Responsabilites des routes :

- recevoir les parametres REST ;
- appliquer les validations de forme prevues par FastAPI et Pydantic ;
- injecter le service approprie ;
- appeler une methode de service dediee ;
- retourner une reponse structuree.

Les routes ne doivent pas contenir de logique metier. Elles ne doivent pas construire de requetes SQLAlchemy, calculer
des KPIs, agreger des metriques, manipuler directement les models ou appeler le connecteur Google Analytics.

### 3.2 Services

Les services portent les regles metier et les calculs backend. Ils orchestrent la validation fonctionnelle, les appels
aux repositories, la transformation des donnees et la construction des reponses applicatives.

Responsabilites des services :

- valider la coherence fonctionnelle des filtres ;
- appliquer les valeurs par defaut de pagination et de tri ;
- calculer les agregats ;
- calculer les KPIs ;
- normaliser les donnees retournees aux routes ;
- gerer les cas limites ;
- convertir les erreurs techniques en erreurs applicatives controlees.

Tous les calculs destines au Desktop doivent etre effectues dans cette couche. Le service est le seul endroit ou doivent
vivre les calculs de sessions, utilisateurs, engagement, duree moyenne, conversions, revenus, tendances ou syntheses.

### 3.3 Repositories

Les repositories encapsulent les acces SQLAlchemy. Ils fournissent des methodes specialisees, reutilisables et
testables pour lire les donnees GA4 existantes.

Responsabilites des repositories :

- appliquer les filtres SQLAlchemy demandes par le service ;
- realiser la pagination ;
- compter les lignes correspondant aux criteres ;
- recuperer les donnees triees ;
- produire les selections necessaires aux agregats ;
- exposer des methodes dediees a la recherche.

Les repositories ne doivent pas decider des regles metier. Ils ne doivent pas connaitre les routes FastAPI, ne doivent
pas construire de reponse REST finale et ne doivent jamais appeler l'API Google Analytics.

### 3.4 Models

Les models SQLAlchemy representent les tables existantes creees lors du Sprint 25. Le Sprint 25A ne doit ni ajouter ni
modifier ces models.

Responsabilites des models :

- representer la structure persistante deja disponible ;
- porter les relations et contraintes existantes ;
- rester coherents avec la migration Alembic deja livree.

Aucune logique metier ne doit etre ajoutee aux models. Toute limite liee a la structure existante doit etre documentee
et traitee au niveau service ou repository, sans migration dans ce sprint.

## 4. Fonctionnalites prevues

### 4.1 Pagination complete

Les endpoints de liste devront prevoir une pagination complete afin de supporter les futurs tableaux Desktop et les
volumes importants de donnees GA4.

Parametres et champs attendus :

- `page` : numero de page demande ;
- `page_size` : nombre d'elements par page ;
- `total` : nombre total d'elements correspondant aux filtres ;
- `pages` : nombre total de pages disponibles.

La pagination devra etre calculee cote backend. Les valeurs par defaut devront etre explicites et les valeurs extremes
devront etre controlees afin d'eviter des reponses trop volumineuses. La pagination devra rester compatible avec les
filtres et le tri.

### 4.2 Filtres REST avances

Les endpoints devront pouvoir recevoir des filtres REST avances pour preparer les usages Desktop de consultation,
diagnostic et analyse marketing.

Filtres envisages :

- `entity_id` : filtrage par entite interne ;
- `property_id` : filtrage par propriete Google Analytics 4 ;
- `date_from` : debut de periode ;
- `date_to` : fin de periode ;
- `metric` : selection ou filtrage par metrique ;
- `dimension` : selection ou filtrage par dimension ;
- `status` : filtrage par statut, notamment pour l'historique ;
- `import_id` : filtrage par import source ;
- `search` : recherche textuelle sur les champs compatibles.

La validation fonctionnelle des filtres devra etre portee par les services. Les repositories devront recevoir des
criteres deja interpretes et les appliquer via SQLAlchemy. Aucun endpoint ne devra contenir de logique de filtrage
complexe directement dans la route.

### 4.3 Tri

Les endpoints de consultation devront prevoir un tri explicite pour alimenter les tableaux Desktop.

Parametres envisages :

- `sort_by` : champ de tri demande ;
- `sort_order` : ordre de tri, par exemple ascendant ou descendant.

Le service devra verifier que le champ de tri est autorise pour l'endpoint concerne. Le repository appliquera ensuite
le tri SQLAlchemy correspondant. Les champs non autorises devront produire une erreur controlee ou etre remplaces par
un tri par defaut documente.

### 4.4 Agregats backend

Les agregats devront etre calcules exclusivement cote Service. Les routes ne devront jamais agreger les donnees et le
Desktop ne devra jamais recalculer les indicateurs metier a partir de donnees brutes lorsque le backend peut les
fournir.

Agregats envisages :

- sessions ;
- utilisateurs ;
- nouveaux utilisateurs ;
- engagement ;
- duree moyenne ;
- transactions ;
- revenus ;
- conversions.

Les calculs devront tenir compte des filtres appliques. Par exemple, une synthese filtree par propriete et periode devra
retourner des agregats limites a cette propriete et a cette periode. Les ratios, moyennes et indicateurs derives devront
etre calcules de maniere explicite dans le service, avec gestion des divisions par zero et des donnees absentes.

### 4.5 KPIs

Un endpoint de synthese devra etre prevu afin d'alimenter directement le Dashboard Desktop Google Analytics.

Cet endpoint devra retourner une vision consolidee et exploitable sans traitement metier cote Desktop. Les KPIs
envisages incluent notamment :

- total des sessions ;
- total des utilisateurs ;
- total des nouveaux utilisateurs ;
- taux d'engagement ;
- duree moyenne des sessions ;
- total des conversions ;
- total des transactions ;
- total des revenus ;
- evolution par rapport a une periode de comparaison lorsque les donnees disponibles le permettent.

La reponse devra etre concue comme une cible fonctionnelle et non comme un schema JSON definitif. Les details exacts du
contrat Pydantic seront definis pendant l'implementation, en coherence avec les schemas existants.

### 4.6 Historique enrichi

L'historique des imports devra etre enrichi pour fournir au Desktop des informations de suivi operationnel claires.

Informations attendues :

- date de lancement ou de fin ;
- duree d'execution ;
- statut ;
- propriete concernee ;
- utilisateur ou acteur ayant declenche l'import lorsque disponible ;
- volume importe.

L'historique devra permettre de diagnostiquer rapidement les imports reussis, echoues, partiels ou en attente. Les
erreurs devront rester lisibles sans exposer de secret, de token ou de detail sensible.

### 4.7 Endpoints specialises

Les endpoints specialises devront preparer les futures vues Desktop sans deplacer la logique metier cote client.

Endpoints envisages :

- `overview` : vue generale et synthese de la periode ;
- `traffic` : analyse du trafic par source, medium, campagne ou canal disponible ;
- `acquisition` : acquisition utilisateurs et sessions ;
- `engagement` : engagement, durees et interactions ;
- `conversions` : conversions et objectifs ;
- `events` : evenements GA4 disponibles ;
- `revenue` : revenus, transactions et indicateurs commerciaux ;
- `history` : historique enrichi des imports.

Ces endpoints devront rester des complements de lecture et de synthese. Ils ne doivent pas declencher de migration, ne
doivent pas modifier la structure de donnees et ne doivent pas creer de logique Desktop.

### 4.8 Reponses REST enrichies

Les reponses REST devront tendre vers une structure homogene afin de simplifier la consommation par le futur Desktop.

Structure cible fonctionnelle :

- `success` : indique si la reponse applicative est valide ;
- `generated_at` : date de generation de la reponse ;
- `filters` : filtres effectivement appliques ;
- `pagination` : informations de pagination lorsque l'endpoint retourne une liste ;
- `data` : donnees ou synthese retournee.

Cette structure constitue une cible fonctionnelle. Elle ne doit pas etre lue comme un schema JSON definitif. Les schemas
Pydantic exacts devront etre definis pendant l'implementation en reutilisant les conventions existantes du backend.

### 4.9 Repository

Le repository Google Analytics devra etre etendu par des methodes specialisees adaptees aux complements d'API REST.

Principes attendus :

- methodes dediees a la recherche ;
- methodes dediees a la pagination ;
- methodes dediees au comptage ;
- methodes dediees aux agregats ;
- methodes dediees a l'historique enrichi.

Ces methodes devront rester orientees acces aux donnees. Les calculs metier, la selection des KPIs et la forme finale
des reponses devront rester dans la couche Service.

## 5. Strategie de tests

La strategie de tests du Sprint 25A devra verifier les complements REST sans appel Internet. Les connecteurs injectables
et les mocks existants devront etre utilises pour garantir des tests deterministes.

Tests prevus :

- pagination avec valeurs par defaut ;
- pagination avec pages vides ;
- pagination avec limites hautes et basses ;
- filtres par entite, propriete, periode, metrique, dimension, statut, import et recherche ;
- combinaison de plusieurs filtres ;
- tri ascendant et descendant ;
- tri sur champ non autorise ;
- agregats simples ;
- agregats filtres par periode et propriete ;
- gestion des donnees absentes dans les agregats ;
- endpoint de KPIs ;
- endpoints specialises ;
- structure des reponses REST enrichies ;
- historique enrichi ;
- cas limites de periode invalide ;
- cas limites de propriete inexistante ;
- absence d'appel Internet pendant les tests.

Les tests devront confirmer que :

- les routes restent fines ;
- les services portent les calculs ;
- les repositories portent uniquement les acces SQLAlchemy ;
- les mocks remplacent tout connecteur externe ;
- aucun test ne depend d'un compte Google, d'un token OAuth ou d'un acces reseau.

## 6. Livrables attendus

Lors de l'implementation ulterieure du Sprint 25A, les livrables attendus seront :

- routes REST complementaires Google Analytics 4 ;
- schemas Pydantic de requete et de reponse si necessaires ;
- methodes de service pour pagination, filtres, tri, agregats, KPIs et historique enrichi ;
- methodes de repository specialisees pour recherche, pagination, comptage et agregats ;
- endpoints specialises de consultation et de synthese ;
- tests backend couvrant routes, services et repositories ;
- documentation technique des endpoints ajoutes si le perimetre le justifie.

Ces livrables devront etre developpes par extension du module existant. Ils ne devront pas introduire de nouveau modele,
de migration Alembic ou de logique Desktop.

## 7. Criteres de validation

Le Sprint 25A sera considere valide si les criteres suivants sont respectes :

- architecture `Routes -> Services -> Repositories -> Models` respectee ;
- separation stricte des responsabilites ;
- aucune logique metier dans les routes ;
- aucune logique metier dans le Desktop ;
- aucun fichier Desktop modifie ;
- aucune migration Alembic creee ;
- aucun nouveau modele SQLAlchemy cree ;
- aucun appel Internet durant les tests ;
- connecteurs externes remplaces par des mocks ou doubles de test ;
- pagination complete disponible sur les endpoints concernes ;
- filtres REST avances valides et testes ;
- tri explicite disponible et controle ;
- agregats calcules cote Service ;
- endpoint de KPIs exploitable par le futur Dashboard Desktop ;
- historique enrichi disponible ;
- reponses REST homogenes ;
- Ruff OK ;
- Pytest OK.

Le Sprint 25A doit preparer le Sprint 26 sans anticiper l'interface Desktop. Toute demande necessitant un changement de
base de donnees, une migration ou une logique client devra etre sortie du perimetre et documentee comme dependance ou
limite pour un sprint ulterieur.

## 8. Choix d'implementation retenus

L'implementation du Sprint 25A a ete limitee a l'extension du module Google Analytics 4 existant. Aucun modele
SQLAlchemy, aucune migration Alembic, aucun fichier Desktop, aucun ApiClient Desktop et aucun Dashboard n'ont ete
modifies.

Endpoints retenus :

- `GET /api/v1/google-analytics/metrics` : consultation paginee des metriques GA4 importees ;
- `GET /api/v1/google-analytics/overview` : synthese KPI calculee cote backend ;
- `GET /api/v1/google-analytics/traffic` : agregats groupes par source ;
- `GET /api/v1/google-analytics/acquisition` : agregats groupes par medium ;
- `GET /api/v1/google-analytics/engagement` : agregats groupes par categorie d'appareil ;
- `GET /api/v1/google-analytics/conversions` : agregats de conversions groupes par source ;
- `GET /api/v1/google-analytics/revenue` : agregats de revenus groupes par campagne ;
- `GET /api/v1/google-analytics/history` : historique enrichi des imports.

Les endpoints `events` et `transactions` n'ont pas ete crees, car le modele de donnees issu du Sprint 25 ne contient
pas de table evenementielle detaillee ni de champ transaction. Le sprint respecte donc la regle de ne jamais inventer de
donnees.

Les filtres disponibles pour les metriques sont limites aux donnees reellement presentes :

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
- `search`.

Le filtre `entity_id` n'a pas ete expose directement, car le modele Google Analytics existant contient `website_id` mais
pas de relation directe vers une entite metier. Une correspondance eventuelle entre entite et site devra etre traitee
dans un sprint ulterieur si le modele du projet l'exige.

Le tri utilise une liste blanche par famille de donnees. Les champs arbitraires sont rejetes avec une erreur controlee.
La pagination reutilise la structure existante du projet avec `items`, `total`, `page`, `page_size` et `pages`.

Les repositories appliquent les filtres, la pagination, le tri, les comptages et les agregats SQLAlchemy. Les services
gardent la responsabilite des validations fonctionnelles, des ratios, des moyennes ponderees, des KPIs et des reponses
specialisees. Les routes restent limitees aux dependances FastAPI, aux parametres HTTP et a la serialisation.
