# Sprint 34 - Orchestrateur de traitements planifies

## 1. Presentation

Le Sprint 34 a pour objectif de specifier la mise en place du premier orchestrateur de traitements planifies de la
plateforme interne Veille SEO-GEO Groupe A.P&Partner.

Jusqu'au Sprint 33, l'application dispose deja de modules fonctionnels importants : authentification, administration,
utilisateurs, sites web, entites, mots-cles, concurrents, URLs, crawls, analyses SEO, analyses GEO, rapports,
connecteurs Google Search Console, Google Analytics 4, Bing Webmaster Tools, planifications de synchronisations,
monitoring et centre d'alertes.

Ces modules permettent de declarer des donnees, de consulter des etats, de superviser des evenements et de faire
apparaitre des alertes. En revanche, les traitements restent majoritairement declenches manuellement ou par des actions
fonctionnelles ponctuelles. Le Sprint 34 marque donc une evolution structurante : la plateforme commence a executer
automatiquement les traitements planifies, en respectant une orchestration centralisee, tracable, robuste et compatible
avec les modules deja en place.

La valeur apportee par ce sprint est operationnelle :

- transformer les planifications du Sprint 31 en intentions executables ;
- creer un mecanisme commun d'orchestration au lieu de multiplier les declencheurs par module ;
- suivre chaque execution de bout en bout ;
- journaliser les evenements importants produits par les traitements ;
- alimenter automatiquement le centre de monitoring introduit au Sprint 32 ;
- generer ou actualiser automatiquement les alertes preparees au Sprint 33 ;
- preparer les futurs tableaux de bord et integrations transversales des Sprints 35 a 40.

Le Sprint 34 depend directement des sprints precedents :

- Sprint 31 : planifications de synchronisations, frequences, statut actif, prochaine execution theorique ;
- Sprint 32 : evenements de monitoring, vues de supervision, etat logique des synchronisations ;
- Sprint 33 : centre d'alertes, generation d'alertes depuis les evenements connus, cycle de vie des alertes.

Le Sprint 34 ne doit pas remplacer ces modules. Il doit les utiliser comme socle et ajouter une couche d'orchestration
transverse.

Ce document constitue le cahier des charges officiel du Sprint 34. Il reste au niveau conception fonctionnelle et
technique. Il ne contient aucun code d'implementation, aucune migration, aucune definition SQL et aucune modification de
l'architecture existante.

## 2. Perimetre

### Inclus

Le Sprint 34 couvre la conception et la future implementation d'un orchestrateur permettant d'executer automatiquement
les traitements planifies.

Elements inclus dans le perimetre fonctionnel :

- identification des planifications eligibles a une execution ;
- creation d'une unite de travail persistante pour chaque execution attendue ;
- orchestration des traitements par type fonctionnel ;
- execution par worker controle ;
- routage vers des handlers specialises ;
- appel aux services metier existants lorsque le traitement est supporte ;
- suivi de l'etat d'une execution ;
- historisation des dates de creation, de demarrage, de fin et d'echec ;
- journalisation controlee des evenements produits ;
- alimentation automatique du monitoring ;
- generation ou actualisation automatique des alertes lorsque les conditions sont reunies ;
- consultation des executions depuis l'API REST ;
- action d'administration limitee pour relancer ou annuler une execution lorsque c'est fonctionnellement autorise ;
- page Desktop de supervision des traitements planifies ;
- strategie de tests complete pour les couches futures.

Elements inclus dans le perimetre technique :

- conception d'un scheduler applicatif ;
- conception d'une queue persistante basee sur PostgreSQL ;
- conception d'un worker applicatif ;
- conception de handlers par type de traitement ;
- specification des transitions d'etat ;
- specification de la concurrence, du verrouillage et de l'idempotence ;
- specification des donnees de suivi necessaires ;
- specification des endpoints REST ;
- specification de l'integration Desktop.

Le Sprint 34 doit rester compatible avec les services existants. La logique metier specifique a chaque domaine doit
rester dans les services concernes : Google Search Console, Google Analytics 4, Bing Webmaster Tools, Crawls, SEO
Analysis, GEO Analysis, Reports, Monitoring et Alerts.

### Exclus

Le Sprint 34 exclut explicitement :

- aucune refonte de l'architecture backend ;
- aucune reecriture des services existants ;
- aucun remplacement des modules de planification, monitoring ou alertes ;
- aucun deplacement de logique metier dans les routes API ;
- aucun acces direct du Desktop a PostgreSQL ;
- aucun appel direct du Desktop aux connecteurs externes ;
- aucune orchestration distribuee multi-noeuds avancee ;
- aucun Celery impose ;
- aucun Redis impose ;
- aucun moteur externe de queue impose ;
- aucune notification native systeme ;
- aucun tableau de bord V2 complet ;
- aucune refonte de l'interface Desktop existante ;
- aucune strategie de scaling horizontal complexe ;
- aucune execution parallele non controlee ;
- aucune suppression automatique de jobs historiques ;
- aucun stockage de secret dans les journaux ;
- aucune exposition de jeton, cle API ou en-tete d'autorisation ;
- aucun traitement metier non encore supporte par les services existants.

Les traitements dont les services metier ne sont pas encore prets devront etre representes comme non supportes ou
reportes. L'orchestrateur ne doit pas inventer une logique metier absente. Il doit deleguer uniquement a des services
existants ou a des handlers explicitement prevus.

## 3. Architecture generale

L'architecture cible du Sprint 34 ajoute une couche transverse entre les planifications et les services metier.

Flux principal :

```text
SyncSchedule
      |
      v
Scheduler
      |
      v
Queue PostgreSQL
      |
      v
Worker
      |
      v
Handler
      |
      v
Service metier existant
      |
      v
Monitoring
      |
      v
Alertes
```

Vue par responsabilite :

```text
Planifications
      |
      |  selection des executions dues
      v
Scheduler
      |
      |  creation idempotente des jobs
      v
Queue persistante
      |
      |  reservation controlee
      v
Worker
      |
      |  execution et transitions d'etat
      v
Handlers specialises
      |
      |  delegation fonctionnelle
      v
Services metier existants
```

Flux de supervision :

```text
Worker
  |
  | evenement d'execution
  v
Journal d'execution
  |
  | evenement consolide
  v
MonitoringEvent
  |
  | classification fonctionnelle
  v
AlertService
  |
  v
Alertes actives ou resolues
```

Flux Desktop :

```text
Page Desktop Orchestrateur
      |
      v
Service Desktop
      |
      v
ApiClient
      |
      v
API REST
      |
      v
Services backend
      |
      v
Repositories
      |
      v
PostgreSQL
```

Composants principaux :

- Scheduler : detecte les planifications dues et cree les jobs a executer ;
- Queue : stocke les travaux en attente, reserves, en cours, termines ou en erreur ;
- Worker : reserve un job, l'execute, gere les transitions d'etat et les retries ;
- Handlers : adaptent un type de job vers le service metier approprie ;
- Services metier existants : realisent le traitement fonctionnel deja prevu par chaque module ;
- Monitoring : recoit les evenements d'execution et expose l'etat consolide ;
- Alertes : transforme les anomalies pertinentes en alertes exploitables.

Le projet doit conserver la separation existante :

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

L'orchestrateur ne doit pas creer une architecture parallele. Il doit s'integrer au backend FastAPI existant et respecter
les conventions deja appliquees dans les modules de planification, monitoring et alertes.

## 4. Modele de donnees previsionnel

Le modele de donnees ci-dessous est previsionnel. Il decrit les futures tables probablement necessaires, sans SQL et sans
implementation.

### OrchestrationJob

Role :

- representer une unite de travail executable issue d'une planification ou d'une demande administrative controlee ;
- permettre le suivi du cycle de vie complet d'un traitement ;
- servir de source principale pour la queue persistante.

Principaux champs envisages :

- identifiant unique ;
- reference optionnelle vers la planification d'origine ;
- type de traitement ;
- statut courant ;
- priorite ;
- payload fonctionnel controle ;
- cle d'idempotence ;
- nombre de tentatives effectuees ;
- nombre maximal de tentatives ;
- date de creation ;
- date de disponibilite dans la queue ;
- date de reservation ;
- date de debut ;
- date de fin ;
- date de dernier echec ;
- message fonctionnel court ;
- detail technique controle ;
- identifiant du worker ayant reserve le job ;
- date d'expiration du verrou ;
- date de creation et date de mise a jour.

Relations :

- relation optionnelle vers SyncSchedule ;
- relation un-vers-plusieurs vers OrchestrationJobLog ;
- relation optionnelle vers MonitoringEvent lorsque l'evenement principal est cree ;
- relation fonctionnelle indirecte vers Alert via MonitoringEvent.

Index envisages :

- statut et date de disponibilite ;
- type de traitement et statut ;
- planification d'origine ;
- cle d'idempotence unique lorsque disponible ;
- date de creation ;
- date de reservation ;
- date d'expiration du verrou.

### OrchestrationJobLog

Role :

- conserver les etapes importantes d'une execution ;
- fournir une trace consultable par les administrateurs ;
- aider au diagnostic sans exposer de donnees sensibles.

Principaux champs envisages :

- identifiant unique ;
- reference vers le job ;
- niveau de journalisation ;
- evenement ;
- message fonctionnel ;
- contexte structure controle ;
- date de creation.

Relations :

- relation plusieurs-vers-un vers OrchestrationJob.

Index envisages :

- job et date de creation ;
- niveau ;
- evenement ;
- date de creation.

### OrchestrationWorkerHeartbeat

Role :

- suivre les workers connus par le systeme ;
- detecter les reservations abandonnees ;
- faciliter la supervision operationnelle.

Principaux champs envisages :

- identifiant unique ;
- identifiant logique du worker ;
- statut du worker ;
- date du dernier signal ;
- job courant optionnel ;
- version applicative optionnelle ;
- metadonnees techniques controlees ;
- date de creation et date de mise a jour.

Relations :

- relation optionnelle vers OrchestrationJob pour le job courant.

Index envisages :

- identifiant logique du worker ;
- statut ;
- date du dernier signal ;
- job courant.

### OrchestrationLock

Role :

- empecher plusieurs schedulers de creer les memes jobs ;
- empecher plusieurs workers de reserver la meme execution ;
- rendre la concurrence explicite et observable.

Principaux champs envisages :

- identifiant unique ;
- nom du verrou ;
- proprietaire ;
- date d'acquisition ;
- date d'expiration ;
- contexte controle.

Relations :

- aucune relation forte obligatoire ;
- relation fonctionnelle avec le scheduler ou le worker qui acquiert le verrou.

Index envisages :

- nom du verrou unique ;
- date d'expiration ;
- proprietaire.

### Extension de SyncSchedule

Role :

- continuer a representer l'intention de synchronisation ;
- fournir au scheduler les informations necessaires pour calculer les executions dues.

Champs potentiellement utiles selon l'existant :

- derniere execution planifiee ;
- derniere execution reussie ;
- derniere execution en erreur ;
- prochaine execution theorique ;
- statut fonctionnel ;
- indicateur actif ;
- type de synchronisation ;
- frequence ;
- cible fonctionnelle.

Relations :

- relation un-vers-plusieurs vers OrchestrationJob.

Index envisages :

- actif et prochaine execution ;
- type de synchronisation ;
- statut ;
- cible fonctionnelle.

## 5. Scheduler

Le scheduler est responsable de la transformation des planifications dues en jobs persistants.

Responsabilites :

- lire les planifications actives ;
- identifier les planifications dont la prochaine execution est due ;
- verifier qu'aucun job equivalent n'est deja en attente, reserve ou en cours ;
- creer un job avec une cle d'idempotence stable ;
- mettre a jour les dates fonctionnelles necessaires sur la planification ;
- produire un evenement de monitoring lorsque la creation de job echoue ;
- ne jamais executer directement le traitement metier.

Cycle de fonctionnement :

```text
Demarrage du cycle
      |
      v
Acquisition du verrou scheduler
      |
      v
Lecture des planifications actives dues
      |
      v
Verification d'idempotence
      |
      v
Creation des jobs manquants
      |
      v
Mise a jour des dates de planification
      |
      v
Journalisation et monitoring
      |
      v
Liberation ou expiration du verrou
```

Frequence d'execution :

- le cycle doit etre regulier et court ;
- une frequence indicative de l'ordre de la minute peut etre envisagee ;
- la frequence exacte doit rester configurable ;
- le scheduler doit etre capable de reprendre apres une interruption sans creer de doublons.

Gestion de la concurrence :

- un seul cycle scheduler doit creer des jobs pour une meme fenetre fonctionnelle ;
- les jobs doivent etre crees avec une cle d'idempotence ;
- la selection des planifications dues doit tenir compte des jobs deja existants ;
- les verrous doivent expirer pour eviter un blocage permanent.

Verrouillage :

- un verrou logique doit proteger le cycle global du scheduler ;
- un verrou ou une contrainte d'idempotence doit proteger chaque job issu d'une planification ;
- l'expiration du verrou doit permettre une reprise par un autre cycle si le precedent s'interrompt.

Idempotence :

- relancer le scheduler plusieurs fois sur la meme fenetre ne doit pas creer plusieurs jobs equivalents ;
- la cle d'idempotence doit inclure au minimum la planification, le type de traitement et la fenetre d'execution ;
- une planification desactivee ne doit pas produire de nouveau job ;
- un job deja en cours ne doit pas etre remplace par un nouveau job identique.

Reprise apres incident :

- si le scheduler s'arrete avant la creation d'un job, le cycle suivant doit pouvoir le creer ;
- si le scheduler s'arrete apres la creation d'un job, la cle d'idempotence doit eviter le doublon ;
- si le verrou reste present, son expiration doit permettre la reprise ;
- tout incident doit etre converti en evenement de monitoring controle.

## 6. Worker

Le worker est responsable de l'execution des jobs presents dans la queue.

Responsabilites :

- reserver un job disponible ;
- poser ou renouveler un verrou de reservation ;
- passer le job dans l'etat approprie ;
- appeler le handler correspondant au type de traitement ;
- enregistrer les logs d'execution ;
- produire les evenements de monitoring ;
- declencher la generation ou l'actualisation des alertes lorsque necessaire ;
- appliquer la strategie de retry ;
- liberer proprement le job en cas de succes, echec ou annulation.

Cycle d'execution :

```text
Worker actif
    |
    v
Selection d'un job disponible
    |
    v
Reservation atomique
    |
    v
Passage a l'etat running
    |
    v
Execution du handler
    |
    v
Succes ?
   / \
  /   \
 v     v
done  retry ou failed
  \     /
   \   /
    v v
Monitoring et alertes
```

Transitions d'etat envisagees :

```text
pending
  |
  v
reserved
  |
  v
running
  |
  +----> succeeded
  |
  +----> retry_scheduled
  |
  +----> failed
  |
  +----> cancelled
```

Regles de transition :

- un job pending peut etre reserve ;
- un job reserve peut devenir running ;
- un job running peut finir en succeeded, failed ou retry_scheduled ;
- un job retry_scheduled redevient eligible apres une date de disponibilite ;
- un job cancelled ne doit plus etre execute ;
- un job succeeded ne doit jamais etre relance automatiquement ;
- un job failed peut etre relance uniquement si une action ou une regle de retry l'autorise.

Reprise apres erreur :

- un worker interrompu peut laisser un job reserve ou running ;
- l'expiration du verrou doit permettre de remettre le job en attente ou en retry ;
- les jobs depassant un delai maximal d'execution doivent etre signales au monitoring ;
- les jobs bloques doivent alimenter le centre d'alertes.

Gestion des retries :

- le nombre de tentatives doit etre limite ;
- chaque tentative doit etre journalisee ;
- le delai entre deux tentatives doit eviter les boucles rapides ;
- les erreurs fonctionnelles non recuperables ne doivent pas etre retentees inutilement ;
- les erreurs temporaires peuvent etre retentees selon une strategie progressive ;
- l'epuisement des retries doit produire un etat failed et une alerte potentielle.

Journalisation :

- chaque changement d'etat important doit etre journalise ;
- les messages doivent etre lisibles par un administrateur ;
- les details techniques doivent rester controles ;
- aucun secret ne doit etre journalise ;
- les erreurs externes doivent etre resumees sans exposer de payload sensible ;
- les journaux doivent permettre de comprendre quoi, quand, pourquoi et par quel worker.

## 7. Handlers

Les handlers adaptent un type de job vers le service metier existant.

Role :

- isoler la logique d'orchestration de la logique metier ;
- centraliser le routage par type de traitement ;
- valider le payload fonctionnel necessaire a l'execution ;
- appeler le service metier approprie ;
- retourner un resultat normalise au worker ;
- convertir les erreurs metier en statuts exploitables par l'orchestrateur.

Types de traitements envisages :

- synchronisation Google Search Console ;
- synchronisation Google Analytics 4 ;
- synchronisation Bing Webmaster Tools ;
- execution de crawl ;
- analyse SEO ;
- analyse GEO ;
- generation ou rafraichissement de rapport ;
- rafraichissement de monitoring ;
- generation ou actualisation d'alertes.

Interactions avec les services metier existants :

- le handler Google Search Console doit deleguer au service Google Search Console ;
- le handler Google Analytics 4 doit deleguer au service Google Analytics ;
- le handler Bing Webmaster Tools doit deleguer au service Bing Webmaster Tools ;
- le handler Crawl doit deleguer au service Crawls ou au moteur de crawl deja prevu ;
- le handler SEO doit deleguer au service SEO Analysis ;
- le handler GEO doit deleguer au service GEO Analysis ;
- le handler Reports doit deleguer au service Reports ;
- le handler Monitoring doit deleguer au service Monitoring ;
- le handler Alerts doit deleguer au service Alerts.

Le handler ne doit pas :

- acceder directement aux connecteurs externes si un service metier existe ;
- ecrire directement en base hors contrat repository/service ;
- recalculer des regles appartenant au domaine metier ;
- masquer une erreur bloquante ;
- produire des logs contenant des secrets.

Resultat normalise attendu :

- statut fonctionnel de sortie ;
- message court ;
- details controles ;
- indicateurs utiles pour le monitoring ;
- reference eventuelle vers l'objet metier produit ou mis a jour ;
- indication sur le caractere retentable ou non de l'erreur.

## 8. API REST prevue

Les endpoints ci-dessous sont envisages pour administrer et consulter l'orchestrateur. Les URLs exactes devront respecter
les conventions du routeur API existant au moment de l'implementation.

### GET /api/v1/orchestration/jobs

Objectif :

- lister les jobs d'orchestration avec pagination et filtres.

Role fonctionnel :

- alimenter la page Desktop ;
- permettre a un administrateur de filtrer par statut, type, planification, periode ou recherche ;
- consulter l'etat operationnel sans declencher de traitement.

### GET /api/v1/orchestration/jobs/{job_id}

Objectif :

- consulter le detail d'un job.

Role fonctionnel :

- afficher les dates, le statut, les tentatives, les messages et le contexte controle ;
- fournir une vue de diagnostic sans exposer de secret.

### GET /api/v1/orchestration/jobs/{job_id}/logs

Objectif :

- lister les journaux associes a un job.

Role fonctionnel :

- permettre de comprendre le deroulement d'une execution ;
- fournir une trace paginee, ordonnee et filtrable.

### POST /api/v1/orchestration/jobs/{job_id}/retry

Objectif :

- demander une relance controlee d'un job eligible.

Role fonctionnel :

- permettre a un administrateur de relancer un job en erreur lorsque la regle metier l'autorise ;
- creer une nouvelle tentative sans dupliquer l'historique ;
- produire un evenement de monitoring.

### POST /api/v1/orchestration/jobs/{job_id}/cancel

Objectif :

- annuler un job qui n'a pas encore atteint un etat terminal non annulable.

Role fonctionnel :

- empecher l'execution d'un job pending, reserved ou retry_scheduled ;
- tracer l'annulation administrative ;
- eviter une suppression physique.

### GET /api/v1/orchestration/summary

Objectif :

- retourner une synthese de l'orchestrateur.

Role fonctionnel :

- afficher les compteurs principaux : jobs en attente, en cours, reussis, en erreur, bloques, retentes ;
- afficher la derniere activite ;
- afficher l'etat logique du scheduler et des workers.

### GET /api/v1/orchestration/workers

Objectif :

- lister les workers connus.

Role fonctionnel :

- superviser les workers actifs ou inactifs ;
- identifier les reservations abandonnees ;
- aider au diagnostic operationnel.

### POST /api/v1/orchestration/scheduler/run-once

Objectif :

- declencher un cycle scheduler manuel controle.

Role fonctionnel :

- permettre une action administrative de diagnostic ou de rattrapage ;
- respecter les memes regles d'idempotence que le scheduler automatique ;
- ne pas executer directement les jobs crees.

Ce endpoint doit etre strictement protege et reserve aux administrateurs autorises.

## 9. Integration Desktop

Le Sprint 34 prevoit une nouvelle page Desktop dediee a l'orchestrateur des traitements.

Architecture attendue :

```text
Page
 |
 v
Service
 |
 v
ApiClient
 |
 v
API REST
```

La page Desktop ne doit contenir aucune logique metier. Elle doit afficher les donnees renvoyees par l'API REST et
transmettre les actions utilisateur au service Desktop.

Fonctionnalites prevues :

- afficher une synthese de l'orchestrateur ;
- afficher les jobs recents ;
- filtrer par statut ;
- filtrer par type de traitement ;
- filtrer par periode ;
- rechercher par message, cle d'idempotence ou identifiant ;
- consulter le detail d'un job ;
- consulter les journaux d'un job ;
- relancer un job eligible ;
- annuler un job eligible ;
- rafraichir la vue ;
- afficher les erreurs utilisateur de facon claire.

Informations affichees :

- identifiant du job ;
- type de traitement ;
- statut ;
- planification d'origine lorsque disponible ;
- priorite ;
- nombre de tentatives ;
- date de creation ;
- date de disponibilite ;
- date de debut ;
- date de fin ;
- worker associe ;
- message court ;
- prochain retry lorsque disponible.

Actions disponibles :

- actualiser ;
- consulter ;
- relancer si autorise ;
- annuler si autorise ;
- nettoyer les filtres.

Etats visuels attendus :

- chargement ;
- liste vide ;
- erreur de chargement ;
- action en cours ;
- action reussie ;
- action refusee ;
- statut critique visible.

La page doit rester coherente avec les pages Desktop existantes de planification, monitoring et alertes. Elle ne doit pas
introduire de navigation parallele ni contourner le client API existant.

## 10. Securite

Endpoints proteges :

- tous les endpoints d'orchestration doivent etre proteges ;
- la consultation doit etre limitee aux utilisateurs autorises ;
- les actions de retry, cancel et run-once doivent etre reservees aux administrateurs ;
- les erreurs d'autorisation doivent rester explicites sans exposer de details internes.

Gestion des erreurs :

- les erreurs fonctionnelles doivent etre distinguees des erreurs techniques ;
- les erreurs retentables doivent etre marquees comme telles ;
- les erreurs non retentables doivent eviter les retries inutiles ;
- les messages exposes au Desktop doivent etre courts, comprehensibles et controles ;
- les traces techniques completes ne doivent pas etre exposees a l'utilisateur final.

Prevention des doubles executions :

- cle d'idempotence obligatoire pour les jobs issus de planifications ;
- verrou scheduler pour la creation de jobs ;
- reservation atomique cote worker ;
- verification du statut avant chaque transition ;
- expiration controlee des verrous ;
- interdiction de relancer un job deja running ou succeeded.

Protection des donnees sensibles :

- aucun token ne doit etre stocke dans les logs d'orchestration ;
- aucune cle API ne doit apparaitre dans les payloads consultables ;
- aucun en-tete d'autorisation ne doit etre persiste ;
- les reponses externes brutes doivent etre filtrees avant journalisation ;
- les payloads doivent contenir uniquement le contexte utile a l'execution.

Principes de journalisation :

- journaliser les decisions importantes ;
- journaliser les transitions d'etat ;
- journaliser les erreurs sous forme controlee ;
- journaliser les actions administratives ;
- conserver une trace suffisante pour le diagnostic ;
- ne pas transformer les logs en stockage de donnees metier completes.

## 11. Strategie de tests

Les tests devront couvrir les categories suivantes lors de l'implementation future.

### Migrations

- creation des tables d'orchestration ;
- contraintes d'idempotence ;
- index de queue ;
- relations avec les planifications ;
- compatibilite avec les migrations precedentes.

### Modeles

- valeurs par defaut ;
- relations ;
- statuts autorises ;
- dates importantes ;
- contraintes de nullable ;
- coherence des champs de suivi.

### Repositories

- selection des jobs disponibles ;
- reservation atomique ;
- filtres pagines ;
- recherche ;
- creation idempotente ;
- mise a jour des transitions ;
- recuperation des jobs bloques.

### Services

- creation de jobs depuis planifications ;
- calcul de l'eligibilite ;
- validation des transitions ;
- gestion des erreurs ;
- production des evenements de monitoring ;
- integration avec le service d'alertes.

### Scheduler

- detection des planifications dues ;
- absence de doublon ;
- respect des planifications inactives ;
- reprise apres interruption ;
- verrouillage ;
- idempotence ;
- comportement avec plusieurs cycles consecutifs.

### Worker

- reservation d'un job ;
- execution reussie ;
- echec retentable ;
- echec non retentable ;
- retries ;
- expiration de verrou ;
- job bloque ;
- journalisation.

### Handlers

- routage par type ;
- validation du payload ;
- delegation au service metier ;
- resultat normalise ;
- conversion des erreurs ;
- absence d'appel direct lorsque le service metier existe.

### API

- securite des endpoints ;
- pagination ;
- filtres ;
- consultation detaillee ;
- retry autorise ;
- retry refuse ;
- annulation autorisee ;
- annulation refusee ;
- cycle scheduler manuel protege.

### Desktop

- chargement de la synthese ;
- affichage de la liste ;
- filtres ;
- detail d'un job ;
- affichage des logs ;
- relance ;
- annulation ;
- gestion des erreurs HTTP ;
- etats vides et chargement.

## 12. Risques

### Concurrence

Plusieurs cycles scheduler ou plusieurs workers peuvent tenter d'agir sur les memes jobs. Le risque principal est la
creation de doublons ou la reservation simultanee d'une meme execution.

Mesures attendues :

- verrous explicites ;
- reservation atomique ;
- cles d'idempotence ;
- transitions d'etat strictes ;
- tests de concurrence.

### Double execution

Un meme traitement peut etre execute deux fois si le scheduler ou le worker ne verifie pas correctement l'existant.

Mesures attendues :

- unicite fonctionnelle des jobs planifies ;
- verification avant execution ;
- statut terminal non relancable automatiquement ;
- logs exploitables.

### Jobs bloques

Un worker interrompu peut laisser un job dans un etat reserve ou running.

Mesures attendues :

- expiration des verrous ;
- heartbeat worker ;
- detection des jobs depassant leur duree maximale ;
- evenement de monitoring ;
- alerte active si le blocage persiste.

### Montee en charge

L'accumulation des planifications peut produire un volume important de jobs et de logs.

Mesures attendues :

- index adaptes ;
- pagination obligatoire ;
- priorisation ;
- limitation des retries ;
- conservation controlee des logs.

### Perte de donnees

Une mauvaise gestion des transitions peut faire perdre la trace d'une execution.

Mesures attendues :

- persistence avant execution ;
- journalisation des transitions ;
- etats terminaux explicites ;
- absence de suppression physique automatique.

### Evolutivite

L'orchestrateur doit rester compatible avec les futurs traitements SEO, GEO, rapports et automatisations.

Mesures attendues :

- handlers specialises ;
- types de jobs extensibles ;
- payloads controles ;
- services metier conserves comme source de logique fonctionnelle.

### Coherence avec les futurs sprints

Le Sprint 34 prepare des vues et automatisations futures. Une specification trop rigide pourrait bloquer les Sprints 35
a 40.

Mesures attendues :

- endpoints consultatifs clairs ;
- modele de donnees extensible ;
- statut d'execution normalise ;
- separation stricte entre orchestration et metier ;
- documentation maintenue.

## 13. Criteres d'acceptation

Le Sprint 34 pourra etre considere comme termine lorsque les criteres suivants seront respectes pendant son
implementation future :

- un scheduler identifie les planifications dues sans creer de doublons ;
- les jobs sont persistants et consultables ;
- les jobs suivent des transitions d'etat documentees ;
- un worker peut reserver et executer un job de facon controlee ;
- les handlers deleguent aux services metier existants ;
- les erreurs sont journalisees sans exposer de donnees sensibles ;
- les retries sont limites et tracables ;
- les jobs bloques peuvent etre detectes ;
- le monitoring est alimente automatiquement par les executions ;
- les alertes peuvent etre generees ou actualisees depuis les anomalies d'execution ;
- l'API REST permet de consulter la synthese, les jobs et les logs ;
- les actions de retry et d'annulation sont protegees et controlees ;
- la page Desktop affiche la synthese, la liste, les details et les logs ;
- le Desktop utilise uniquement le flux Page, Service, ApiClient, API REST ;
- les tests couvrent migrations, modeles, repositories, services, scheduler, worker, handlers, API et Desktop ;
- aucun secret n'est stocke ou affiche dans les journaux ;
- la documentation reste coherente avec les Sprints 31, 32 et 33.

## 14. Preparation des futurs sprints

### Sprint 35 - Dashboard V2

Le Sprint 34 prepare le Dashboard V2 en produisant des donnees d'exploitation fiables :

- nombre de jobs en attente ;
- nombre de jobs en cours ;
- taux de succes ;
- taux d'erreur ;
- traitements en retard ;
- jobs bloques ;
- dernieres executions ;
- alertes issues de l'orchestrateur ;
- etat global des automatisations.

Ces informations pourront alimenter une vue plus operationnelle du tableau de bord sans demander au Dashboard de
recalculer lui-meme les etats metier.

### Sprint 36 - Integration transversale Version 1.0

Le Sprint 34 prepare l'integration transversale en stabilisant un mecanisme commun d'execution.

Les modules suivants pourront s'appuyer sur ce socle :

- connecteurs externes ;
- crawls ;
- analyses SEO ;
- analyses GEO ;
- rapports ;
- monitoring ;
- alertes ;
- automatisations administratives.

L'integration transversale pourra ainsi s'appuyer sur des contrats communs : job, statut, logs, monitoring, alerte,
handler et service metier.

### Evolutions futures

Le Sprint 34 doit rester compatible avec les evolutions suivantes :

- priorisation avancee des traitements ;
- fenetres horaires d'execution ;
- quotas par connecteur ;
- limitation de concurrence par site ;
- orchestration de workflows multi-etapes ;
- dependances entre jobs ;
- relances manuelles avancees ;
- archivage des anciennes executions ;
- supervision temps reel ;
- notifications utilisateurs ;
- automatisations metier plus riches ;
- execution distribuee si le besoin apparait.

Le principe directeur reste le meme : l'orchestrateur coordonne, les services metier executent, le monitoring observe et
les alertes priorisent.

## Conclusion

Le Sprint 34 introduit le socle d'execution automatique de la plateforme Veille SEO-GEO Groupe A.P&Partner. Il transforme
les planifications en traitements suivis, journalises et supervises, tout en preservant l'architecture modulaire deja en
place.

Ce sprint doit etre implemente avec prudence : la robustesse, l'idempotence, la tracabilite et la separation des
responsabilites sont plus importantes que la multiplication rapide des traitements supportes. Une orchestration fiable
sur quelques types de jobs bien maitrises aura plus de valeur qu'une automatisation large mais fragile.
