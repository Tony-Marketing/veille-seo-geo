# Sprint 32 - Centre de monitoring

## Objectif

Le Sprint 32 a pour objectif de specifier le futur centre de monitoring de la plateforme interne Veille SEO-GEO Groupe
A.P&Partner.

Ce module doit fournir une vue consolidee de supervision permettant aux administrateurs de comprendre rapidement l'etat
logique du systeme, des connecteurs et des synchronisations planifiees.

Le sprint ne vise pas a executer des traitements. Il prepare une interface consultative et une architecture backend
dediee a la restitution d'informations de monitoring.

## Contexte

Les Sprints 1 a 31 sont consideres comme termines. Ils ont progressivement pose les bases du backend FastAPI, du Desktop,
des modules SEO/GEO, des connecteurs externes, de l'administration, de la gestion des utilisateurs et de la planification
des synchronisations.

Le Sprint 31 a introduit la planification des synchronisations. Cette planification decrit les intentions d'execution,
les frequences et les parametres de synchronisation, mais aucun scheduler reel n'existe encore dans l'application.

Le Sprint 32 apporte donc une vue consolidee de supervision sans declencher de traitement, sans scheduler, sans appel
Internet et sans synchronisation automatique. Il permet uniquement de consulter l'etat connu du systeme a partir des
donnees deja presentes ou preparees par les modules existants.

## Objectifs fonctionnels

Le centre de monitoring doit fournir une lecture synthetique et operationnelle de l'etat de la plateforme.

Les fonctionnalites attendues sont :

- une vue generale du systeme ;
- l'etat des synchronisations connues ;
- les dernieres executions repertoriees ;
- les prochaines executions calculees a partir des planifications existantes ;
- les evenements recents de monitoring ;
- l'etat logique des connecteurs ;
- des statistiques globales exploitables par un administrateur.

Le module est uniquement consultatif. Il ne doit pas permettre de lancer une synchronisation, de modifier une
planification, de tester un connecteur, de corriger une erreur ou de contacter une API externe.

## Hors perimetre

Les elements suivants sont explicitement hors perimetre du Sprint 32 :

- scheduler ;
- execution reelle de traitements ;
- synchronisations automatiques ;
- alertes ;
- notifications ;
- exports ;
- React ;
- appels Internet ;
- modification de connecteurs externes ;
- creation de nouvelles integrations ;
- automatisation des recuperations de donnees ;
- modification des roles ou permissions existants ;
- modification du fonctionnement de l'authentification ;
- creation de composants Desktop reutilisables hors page Monitoring.

## Architecture Backend

L'architecture backend attendue respecte la separation de responsabilites deja definie dans le projet.

Routes

↓

Services

↓

Repositories

↓

Models

Les regles suivantes doivent etre respectees lors de l'implementation future :

- aucune logique metier dans les routes ;
- les routes FastAPI valident l'acces, deleguent aux services et retournent les schemas de reponse ;
- la logique metier reste centralisee dans les services ;
- les services consolident les donnees issues des repositories ;
- les repositories sont limites aux acces SQLAlchemy ;
- les modeles SQLAlchemy representent uniquement la structure persistante ;
- les schemas de reponse utilisent Pydantic v2 ;
- toute evolution de structure passe par une migration Alembic explicite ;
- aucun appel direct aux API externes ne doit etre effectue depuis les routes ou les repositories ;
- les donnees affichees doivent etre paginees lorsque le volume peut devenir important.

Le centre de monitoring devra rester compatible avec les modules existants, notamment les synchronisations planifiees,
les connecteurs et les evenements systeme futurs.

## Architecture Desktop

L'architecture Desktop prevue suit le flux deja impose au sein du projet.

Page

↓

Service

↓

ApiClient

↓

API REST

La future page Monitoring ne doit contenir aucune logique metier. Elle doit uniquement afficher les donnees retournees
par le service Desktop et gerer les interactions de consultation.

Les regles suivantes s'appliquent :

- aucun acces direct a PostgreSQL depuis le Desktop ;
- aucun acces direct aux API externes depuis le Desktop ;
- aucun calcul metier structurel dans la page ;
- les appels HTTP passent exclusivement par ApiClient ;
- le service Desktop encapsule les appels REST du monitoring ;
- la page doit rester compatible avec le lazy loading existant ;
- les erreurs d'acces ou de chargement doivent etre presentees clairement a l'utilisateur.

## Modele de donnees envisage

Le futur modele MonitoringEvent servira a historiser les evenements consultables dans le centre de monitoring.

Champs envisages :

- id : identifiant unique de l'evenement ;
- event_type : categorie fonctionnelle de l'evenement ;
- severity : niveau de gravite ;
- source : origine logique de l'evenement ;
- message : resume lisible par un administrateur ;
- details : informations complementaires structurees, sans donnee sensible ;
- created_at : date et heure de creation de l'evenement.

Les futurs Enum envisages devront permettre de normaliser les valeurs affichees et filtrees.

Types d'evenements envisages :

- synchronisation ;
- connecteur ;
- systeme ;
- administration ;
- securite ;
- import ;
- analyse.

Niveaux de severite envisages :

- information ;
- avertissement ;
- erreur ;
- critique.

Sources logiques envisagees :

- Google Search Console ;
- Google Analytics ;
- Bing Webmaster Tools ;
- crawler ;
- module SEO ;
- module GEO ;
- administration ;
- systeme interne.

Le champ details ne doit pas exposer de secret, de token, de cle API, de mot de passe, d'en-tete d'autorisation ou de
donnee personnelle non necessaire a la supervision.

## Endpoints REST prevus

Les endpoints REST prevus sont reserves a l'administration et exposes sous le prefixe d'API existant.

### GET /api/v1/admin/monitoring/overview

Cet endpoint fournit la synthese globale du centre de monitoring.

Il doit restituer les indicateurs de haut niveau necessaires a l'ecran principal :

- nombre total de connecteurs connus ;
- nombre de connecteurs consideres comme actifs ;
- nombre de connecteurs necessitant une attention ;
- nombre de synchronisations planifiees ;
- nombre de synchronisations actives ;
- nombre d'evenements recents ;
- date de derniere activite connue ;
- etat logique global du systeme.

Cet endpoint ne lance aucun traitement et ne contacte aucun service externe.

### GET /api/v1/admin/monitoring/events

Cet endpoint liste les evenements recents de monitoring.

Il doit permettre d'alimenter le journal de supervision de la page Monitoring avec une approche paginee et filtrable.
Les filtres futurs pourront porter sur la source, le type d'evenement, la severite et la periode de creation.

La reponse doit rester strictement consultative et ne doit pas exposer de details sensibles.

### GET /api/v1/admin/monitoring/connectors

Cet endpoint restitue l'etat logique des connecteurs connus par la plateforme.

Il doit permettre d'afficher, pour chaque connecteur, son nom, son statut logique, la derniere activite connue, les
eventuelles erreurs recentes et une indication de configuration lorsque cette information est disponible sans exposer de
secret.

Il ne doit pas tester les connecteurs en direct et ne doit pas effectuer d'appel Internet.

### GET /api/v1/admin/monitoring/sync-schedules

Cet endpoint restitue les synchronisations planifiees issues du Sprint 31.

Il doit permettre d'afficher les planifications existantes, leur statut, leur frequence, leur derniere execution connue
et leur prochaine execution theorique lorsqu'elle peut etre determinee a partir des donnees disponibles.

Il ne doit pas declencher de synchronisation et ne doit pas creer de tache planifiee.

## Interface Desktop prevue

La future page Monitoring doit etre integree a l'application Desktop comme une page d'administration consultative.

Elle doit respecter le design existant, l'inspiration Windows 11, le mode sombre natif et les conventions Desktop deja
utilisees dans le projet.

Widgets envisages :

- indicateurs globaux ;
- sante des connecteurs ;
- prochaines synchronisations ;
- derniers evenements ;
- tableau des planifications.

Les indicateurs globaux doivent donner une lecture rapide de l'etat general du systeme.

La sante des connecteurs doit distinguer les connecteurs operationnels, incomplets, en erreur logique ou sans activite
connue.

La zone des prochaines synchronisations doit afficher les prochaines dates calculees ou l'absence de prochaine execution
lorsque la planification ne permet pas de l'etablir.

La zone des derniers evenements doit presenter un historique court, trie par date decroissante, avec une indication de
severite.

Le tableau des planifications doit permettre a l'administrateur de verifier les synchronisations configurees sans les
modifier et sans les executer.

Aucune capture d'ecran, aucun code et aucun appel direct a une source de donnees externe ne sont attendus dans le cadre
de cette specification.

## Securite

Le centre de monitoring est une fonctionnalite d'administration.

Les endpoints doivent etre proteges par require_admin et necessiter une authentification obligatoire.

Les reponses ne doivent exposer aucune information sensible :

- aucun mot de passe ;
- aucun token ;
- aucune cle API ;
- aucun secret de configuration ;
- aucun en-tete d'autorisation ;
- aucun contenu brut issu d'une API externe lorsque ce contenu n'est pas necessaire a la supervision.

Les erreurs doivent rester informatives pour l'administrateur sans reveler de details techniques exploitables.

## Tests prevus

Les tests attendus lors de l'implementation future couvrent les couches principales du module.

Tests modeles :

- validation de la structure persistante du futur evenement de monitoring ;
- coherence des champs obligatoires ;
- coherence des valeurs enumerees.

Tests repositories :

- creation et lecture des evenements de monitoring ;
- filtrage par type, source, severite et date ;
- tri decroissant par date de creation ;
- pagination des evenements.

Tests services :

- consolidation de la vue generale ;
- calcul des statistiques globales ;
- lecture des connecteurs sans appel externe ;
- lecture des synchronisations planifiees sans execution ;
- absence d'exposition de donnees sensibles.

Tests routes :

- refus sans authentification ;
- refus sans droits administrateur ;
- acces autorise avec droits administrateur ;
- contrats de reponse conformes aux schemas prevus ;
- pagination des evenements ;
- absence de declenchement de traitement.

Tests Desktop :

- chargement de la page Monitoring ;
- appel du service Desktop attendu ;
- affichage des indicateurs globaux ;
- affichage des connecteurs ;
- affichage des evenements ;
- affichage des planifications ;
- gestion des erreurs API ;
- absence d'acces direct a PostgreSQL ;
- absence d'appel direct a une API externe.

Tests lazy loading :

- la page Monitoring est chargee uniquement a la navigation ;
- l'ajout de la page ne casse pas le lazy loading existant ;
- une erreur de chargement de la page ne bloque pas le reste de l'application.

## Criteres d'acceptation

Le Sprint 32 pourra etre considere comme termine lorsque les criteres suivants seront satisfaits lors de son
implementation :

- une page Desktop Monitoring consultative est disponible pour les administrateurs ;
- les endpoints REST d'administration du monitoring sont disponibles ;
- l'acces aux endpoints est protege par authentification et require_admin ;
- la vue generale restitue les indicateurs globaux prevus ;
- les connecteurs sont affiches avec un etat logique sans test en direct ;
- les synchronisations planifiees issues du Sprint 31 sont consultables ;
- les prochaines executions theoriques sont affichees lorsqu'elles sont determinables ;
- les derniers evenements de monitoring sont consultables ;
- aucune synchronisation n'est executee par le module ;
- aucun scheduler n'est ajoute ;
- aucun appel Internet n'est effectue par les endpoints du monitoring ;
- aucune information sensible n'est exposee ;
- la logique metier backend reste dans les services ;
- les repositories restent limites a SQLAlchemy ;
- le Desktop respecte le flux Page, Service, ApiClient, API REST ;
- le lazy loading Desktop reste operationnel ;
- les tests prevus sont ajoutes et passent ;
- la documentation du sprint reste coherente avec les evolutions implementees.

## Evolutions prevues

Le Sprint 32 sert de socle de supervision pour plusieurs evolutions fonctionnelles.

### Sprint 33 - Alertes et notifications

Le Sprint 33 pourra s'appuyer sur les evenements et etats consolides par le monitoring pour definir des alertes,
prioriser les incidents et notifier les administrateurs.

### Sprint 34 - Exports consolides

Le Sprint 34 pourra exploiter les donnees de supervision pour produire des exports consolides a destination du pilotage
interne, sans melanger la consultation temps reel et la generation de rapports.

### Sprint 35 - Profils editoriaux IA

Le Sprint 35 pourra beneficier du monitoring pour suivre l'etat des traitements lies aux profils editoriaux IA et
identifier les sources ou modules necessitant une attention.

### Sprint 36 - Briefs IA

Le Sprint 36 pourra reutiliser les informations de monitoring pour contextualiser la generation de briefs IA, notamment
l'etat des sources, la fraicheur des donnees et les evenements recents.

## Conclusion

Le Sprint 32 introduit une vision consolidee et consultative de l'etat de la plateforme Veille SEO-GEO Groupe
A.P&Partner.

Il clarifie le futur cadre de supervision sans anticiper le scheduler, les alertes, les notifications ou les exports.
Cette separation permet de poser une base technique saine, securisee et extensible pour les prochains sprints, tout en
respectant l'architecture existante du backend et du Desktop.
