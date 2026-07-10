# Sprint 33 - Centre d'alertes

## Objectifs

Le Sprint 33 a pour objectif de specifier le futur centre d'alertes de la plateforme interne Veille SEO-GEO Groupe
A.P&Partner.

Ce module existe pour transformer les etats consolides par le centre de monitoring en alertes lisibles, priorisees et
exploitables par les administrateurs. Le Sprint 32 fournit deja une vision consultative de l'etat logique des
connecteurs, des synchronisations planifiees et des evenements recents. Le Sprint 33 s'appuie sur ces informations pour
identifier les situations qui necessitent une attention particuliere.

Le centre d'alertes resout les problemes suivants :

- rendre visibles les anomalies importantes sans obliger l'administrateur a analyser tous les evenements de monitoring ;
- distinguer les informations simples, les avertissements et les situations critiques ;
- eviter la duplication d'une meme anomalie active ;
- conserver une trace des alertes acquittees ou resolues ;
- fournir une base consultative claire avant l'orchestration et les automatisations futures ;
- preparer un point d'entree fonctionnel pour les sprints ulterieurs sans declencher d'action automatique.

Le centre d'alertes ne remplace pas le monitoring. Le monitoring reste la source consolidee des etats connus. Le centre
d'alertes exploite ces etats pour produire une lecture orientee incident, priorisation et suivi administratif.

Le module est strictement consultatif dans le cadre du Sprint 33 :

- aucun scheduler n'est ajoute ;
- aucune synchronisation n'est executee ;
- aucun appel Internet n'est effectue ;
- aucun connecteur n'est teste en direct ;
- aucune notification systeme native n'est envoyee ;
- aucune correction automatique n'est appliquee.

## Fonctionnement general

Une alerte est une representation fonctionnelle d'une situation detectee a partir des donnees deja connues par la
plateforme. Elle peut provenir d'un evenement de monitoring, d'un etat de connecteur, d'une planification de
synchronisation, d'un resultat SEO, d'un resultat GEO ou d'un etat de crawl deja stocke par les modules existants.

Le centre d'alertes ne produit pas de donnees par exploration directe. Il ne contacte pas les APIs externes et ne lance
aucun traitement metier. Il lit uniquement les informations disponibles dans le backend, puis applique des regles de
classification pour exposer les alertes pertinentes.

Le cycle de vie complet d'une alerte est le suivant :

1. Une anomalie ou information notable existe dans les donnees disponibles.
2. Le service d'alertes identifie cette situation comme eligible a une alerte.
3. Le service recherche si une alerte active equivalente existe deja.
4. Si aucune alerte active equivalente n'existe, une nouvelle alerte est creee avec une date `first_seen_at`.
5. Si une alerte equivalente existe deja, elle est mise a jour avec une date `last_seen_at` et les informations les plus
   recentes.
6. L'alerte reste visible tant que la situation qui l'a produite reste pertinente.
7. Un administrateur peut acquitter l'alerte pour indiquer qu'elle a ete vue et prise en compte.
8. Une alerte acquittee reste visible et conserve son statut tant que la situation n'est pas resolue.
9. Lorsque la situation d'origine n'est plus presente, l'alerte peut passer a l'etat resolu.
10. Une alerte resolue sort de la vue active par defaut, mais reste disponible dans l'historique.

Une alerte disparait de la vue active uniquement lorsqu'elle est resolue. Elle ne doit pas etre supprimee physiquement
parce que sa valeur principale est aussi historique : elle permet de comprendre quand un probleme est apparu, combien de
temps il a dure, s'il a ete acquitte et comment il s'est termine.

Les informations affichables doivent toujours rester controlees. Une alerte ne doit pas exposer de secret, de token, de
mot de passe, de cle API, d'en-tete d'autorisation ou de contenu brut provenant d'un service externe.

## Cas d'utilisation

### Synchronisation en erreur

Origine :

- derniere execution connue d'une synchronisation planifiee ;
- evenement de monitoring de type synchronisation ;
- statut fonctionnel prepare par le Sprint 31 ou expose par le Sprint 32.

Comportement attendu :

- creer une alerte si la derniere execution connue est en erreur ;
- ne pas creer plusieurs alertes actives pour la meme planification et la meme cause ;
- mettre a jour `last_seen_at` si l'erreur reste presente ;
- conserver le message fonctionnel controle lorsque disponible ;
- permettre l'acquittement par un administrateur ;
- passer l'alerte a resolue lorsque la synchronisation n'est plus en erreur.

Niveau de severite :

- `Critical` si l'erreur bloque une synchronisation essentielle ou recurrente ;
- `Warning` si l'erreur concerne une synchronisation secondaire ou non bloquante.

### Synchronisation en retard

Origine :

- date de prochaine execution theorique issue des planifications ;
- date de derniere execution connue ;
- etat consolide par le monitoring.

Comportement attendu :

- creer une alerte lorsqu'une synchronisation active depasse son echeance attendue ;
- tenir compte de la frequence configuree pour eviter les faux positifs ;
- maintenir une seule alerte active par planification en retard ;
- mettre a jour `last_seen_at` tant que le retard persiste ;
- resoudre l'alerte lorsque la synchronisation retrouve un etat conforme.

Niveau de severite :

- `Warning` par defaut ;
- `Critical` si le retard depasse un seuil fonctionnel important ou concerne une source critique.

### Expiration prochaine d'un jeton

Origine :

- etat connu d'un connecteur ;
- date d'expiration deja stockee lorsqu'elle existe ;
- information consolidee par le monitoring sans test en direct.

Comportement attendu :

- creer une alerte avant l'expiration lorsque l'information est disponible ;
- afficher une formulation claire sans exposer la valeur du jeton ;
- maintenir l'alerte active tant que le jeton reste proche de l'expiration ;
- passer en critique si le jeton est considere expire ou inutilisable ;
- resoudre l'alerte lorsque l'etat connu du connecteur indique une configuration valide.

Niveau de severite :

- `Warning` si l'expiration est proche ;
- `Critical` si le jeton est expire ou empeche l'utilisation du connecteur.

### Erreur critique

Origine :

- evenement de monitoring critique ;
- etat systeme interne deja persiste ;
- anomalie fonctionnelle bloquante identifiee par un module existant.

Comportement attendu :

- creer une alerte critique visible en priorite ;
- ne pas masquer l'alerte meme si elle est acquittee ;
- conserver un message court et exploitable ;
- historiser les dates d'apparition, de derniere observation, d'acquittement et de resolution ;
- resoudre uniquement lorsque la cause n'est plus presente dans les donnees connues.

Niveau de severite :

- `Critical`.

### Erreur SEO

Origine :

- resultat d'audit SEO deja stocke ;
- evenement de monitoring lie au module SEO ;
- indicateur technique ou contenu signale comme bloquant par les modules existants.

Comportement attendu :

- creer une alerte lorsque l'erreur SEO depasse un niveau fonctionnel defini ;
- rattacher l'alerte au site, a l'URL ou a l'analyse lorsque l'information existe ;
- conserver le contexte minimal permettant de comprendre l'origine ;
- eviter la duplication pour la meme URL, le meme site et la meme cause active ;
- resoudre lorsque l'erreur n'est plus presente dans le dernier etat connu.

Niveau de severite :

- `Warning` pour une erreur importante mais non bloquante ;
- `Critical` pour une erreur SEO bloquante sur un site ou une URL prioritaire.

### Erreur GEO

Origine :

- resultat d'analyse GEO deja stocke ;
- evenement de monitoring lie au module GEO ;
- anomalie de citation, de visibilite ou de comparaison de modele deja produite par le module GEO.

Comportement attendu :

- creer une alerte lorsque le module GEO remonte une anomalie significative ;
- rattacher l'alerte a la marque, au modele IA, a la requete ou a l'analyse lorsque disponible ;
- ne pas declencher de nouvelle analyse GEO ;
- maintenir l'alerte tant que l'anomalie reste presente dans le dernier etat connu ;
- resoudre l'alerte lorsque les donnees connues indiquent un retour a la normale.

Niveau de severite :

- `Info` pour une variation notable mais non urgente ;
- `Warning` pour une degradation importante ;
- `Critical` uniquement si une anomalie GEO est explicitement qualifiee comme bloquante par les regles metier.

### Erreur Crawl

Origine :

- dernier crawl connu ;
- evenement de monitoring lie au crawler ;
- statut d'execution ou resultat technique deja stocke.

Comportement attendu :

- creer une alerte si un crawl planifie ou attendu echoue ;
- rattacher l'alerte au site ou au crawl lorsque possible ;
- conserver le message fonctionnel controle ;
- ne pas relancer le crawl ;
- resoudre l'alerte lorsque le dernier etat connu du crawl n'indique plus l'erreur.

Niveau de severite :

- `Warning` par defaut ;
- `Critical` si le crawl concerne un site prioritaire ou si l'erreur empeche toute analyse technique.

### Connecteur indisponible

Origine :

- etat logique du connecteur expose par le monitoring ;
- evenement de monitoring de type connecteur ;
- configuration connue incomplete, invalide ou en erreur.

Comportement attendu :

- creer une alerte lorsque le connecteur est connu comme indisponible ;
- ne jamais tester le connecteur en direct dans le cadre du centre d'alertes ;
- indiquer le connecteur concerne et le type d'indisponibilite lorsque disponible ;
- ne jamais afficher de secret de configuration ;
- resoudre l'alerte lorsque l'etat consolide indique que le connecteur est de nouveau disponible.

Niveau de severite :

- `Warning` si le connecteur est incomplet ou necessite une attention ;
- `Critical` si le connecteur est indispensable a un flux actif et connu comme indisponible.

## Niveaux de severite

Les niveaux de severite doivent rester simples, coherents et comprenables par un administrateur.

### Info

Le niveau `Info` represente une information notable qui ne necessite pas d'action urgente.

Il peut signaler :

- une variation de statut utile a connaitre ;
- une degradation mineure ;
- une situation a surveiller ;
- un evenement fonctionnel non bloquant.

Une alerte `Info` ne doit pas etre utilisee pour masquer une erreur reelle. Elle sert a informer et a contextualiser.

### Warning

Le niveau `Warning` represente une situation anormale qui necessite une attention administrative, mais qui ne bloque pas
necessairement le fonctionnement global de la plateforme.

Il peut signaler :

- une synchronisation en retard ;
- une erreur sur un module non critique ;
- une configuration incomplete ;
- une expiration prochaine ;
- une degradation fonctionnelle importante.

Une alerte `Warning` doit etre visible dans la liste principale et incluse dans les compteurs de synthese.

### Critical

Le niveau `Critical` represente une situation bloquante, urgente ou susceptible d'impacter fortement la fiabilite des
donnees affichees.

Il peut signaler :

- une source essentielle indisponible ;
- une erreur persistante sur une synchronisation critique ;
- un jeton expire bloquant un connecteur ;
- une erreur systeme ou metier majeure ;
- une anomalie qui empeche la supervision correcte d'un perimetre important.

Une alerte `Critical` doit etre priorisee dans l'interface et rester visible tant qu'elle n'est pas resolue, meme si elle
a ete acquittee.

## Etats d'une alerte

Les etats d'une alerte permettent de separer la presence de la situation d'origine et la prise en compte par un
administrateur.

### Active

L'etat `Active` signifie que la situation d'origine est toujours consideree comme presente ou pertinente.

Une alerte active :

- apparait dans la vue active par defaut ;
- est incluse dans les compteurs de synthese ;
- peut etre acquittee ;
- peut etre resolue uniquement lorsque les donnees connues indiquent que la cause n'est plus presente.

### Acknowledged

L'etat `Acknowledged` signifie qu'un administrateur a vu l'alerte et indique qu'elle est prise en compte.

Une alerte acquittee :

- reste visible ;
- conserve sa severite ;
- reste rattachee a sa cause ;
- reste incluse dans l'historique ;
- ne doit pas etre consideree comme resolue ;
- peut redevenir simplement active si la logique d'affichage souhaite distinguer une nouvelle observation importante.

L'acquittement n'est pas une correction. Il ne declenche aucune action automatique.

### Resolved

L'etat `Resolved` signifie que la situation d'origine n'est plus presente dans les donnees connues ou qu'elle a ete
fermee selon une regle fonctionnelle valide.

Une alerte resolue :

- sort de la vue active par defaut ;
- reste consultable dans l'historique ;
- conserve ses dates de creation, de derniere observation, d'acquittement et de resolution ;
- ne doit pas etre supprimee automatiquement ;
- peut etre reutilisee comme trace d'audit fonctionnel.

### Transitions possibles

Transitions autorisees :

- `Active` vers `Acknowledged` lorsqu'un administrateur acquitte l'alerte ;
- `Active` vers `Resolved` lorsque la cause n'est plus presente ;
- `Acknowledged` vers `Resolved` lorsque la cause n'est plus presente ;
- `Acknowledged` vers `Active` si une nouvelle observation significative justifie de remettre l'alerte en avant ;
- `Resolved` vers `Active` uniquement si la meme cause reapparait et que la strategie retenue est de rouvrir l'alerte
  historique.

Transitions non attendues :

- `Resolved` vers `Acknowledged` sans reactivation ;
- suppression physique d'une alerte active ;
- resolution automatique sans condition metier explicite ;
- acquittement considere comme resolution.

## Historique

Le centre d'alertes doit conserver une trace exploitable de l'apparition, de l'evolution et de la cloture des alertes.

Les principes d'historique sont les suivants :

- une alerte creee conserve sa date de premiere observation ;
- une alerte deja existante et toujours pertinente met a jour sa date de derniere observation ;
- une alerte acquittee conserve la date et l'utilisateur d'acquittement lorsque l'information est disponible ;
- une alerte resolue conserve la date de resolution et la raison fonctionnelle lorsque disponible ;
- une alerte resolue reste consultable dans l'historique ;
- l'historique ne doit pas stocker de donnees sensibles ;
- l'historique doit rester filtrable par severite, etat, source, type et periode.

Champs temporels attendus :

- `first_seen_at` : date et heure de premiere detection de la situation ;
- `last_seen_at` : date et heure de derniere observation de la situation ;
- `acknowledged_at` : date et heure d'acquittement lorsque l'alerte a ete acquittee ;
- `resolved_at` : date et heure de resolution lorsque l'alerte est resolue ;
- `created_at` : date et heure de creation de l'enregistrement ;
- `updated_at` : date et heure de derniere mise a jour.

La conservation doit permettre de comprendre :

- combien d'alertes sont actives ;
- combien d'alertes ont ete acquittees ;
- combien d'alertes ont ete resolues ;
- quelles sources produisent le plus d'alertes ;
- quelles alertes sont recurrentes ;
- quelles alertes critiques ont dure le plus longtemps.

La duree exacte de retention pourra etre precisee lors de l'implementation, mais le Sprint 33 pose le principe suivant :
les alertes resolues restent conservees tant qu'aucune politique de purge explicite n'est definie.

## Modele de donnees

Le futur modele fonctionnel propose est `Alert`.

Ce modele represente une alerte exploitable par un administrateur. Il ne represente pas un evenement brut de monitoring,
mais une situation qualifiee a suivre.

Champs fonctionnels attendus :

- `id` : identifiant interne unique de l'alerte ;
- `title` : titre court, lisible et stable de l'alerte ;
- `message` : description fonctionnelle de la situation ;
- `severity` : niveau de severite, avec les valeurs attendues `Info`, `Warning` ou `Critical` ;
- `status` : etat de l'alerte, avec les valeurs attendues `Active`, `Acknowledged` ou `Resolved` ;
- `source_type` : origine logique de l'alerte, par exemple GSC, GA4, Bing, SEO, GEO, crawl ou systeme ;
- `source_id` : identifiant optionnel de l'objet source lorsque l'alerte est rattachee a une ressource connue ;
- `category` : categorie fonctionnelle de l'alerte, par exemple synchronisation, connecteur, systeme ou import ;
- `deduplication_key` : cle fonctionnelle permettant d'eviter les doublons d'alertes actives ;
- `metadata` : informations complementaires structurees et non sensibles ;
- `first_seen_at` : date et heure de premiere observation ;
- `last_seen_at` : date et heure de derniere observation ;
- `acknowledged_at` : date et heure d'acquittement ;
- `acknowledged_by_user_id` : utilisateur ayant acquitte l'alerte lorsque disponible ;
- `resolved_at` : date et heure de resolution ;
- `created_at` : date et heure de creation ;
- `updated_at` : date et heure de derniere modification.

Contraintes fonctionnelles attendues :

- `title`, `severity`, `status`, `source_type`, `category`, `deduplication_key`, `first_seen_at` et `last_seen_at` sont des informations
  essentielles ;
- `metadata` ne doit jamais contenir de secret ;
- `deduplication_key` doit permettre d'identifier une meme cause active ;
- une alerte doit pouvoir exister sans rattachement a un site lorsque la source est systeme ou connecteur ;
- une alerte issue d'une planification doit conserver son contexte dans `metadata` lorsque cette information existe ;
- les champs d'acquittement restent vides tant que l'alerte n'a pas ete acquittee ;
- les champs de resolution restent vides tant que l'alerte n'est pas resolue.

Le modele doit rester extensible afin de couvrir les futures alertes liees a l'orchestrateur sans refondre la structure.

## API REST prevue

Les endpoints REST prevus doivent rester reserves a l'administration et strictement consultatifs, sauf pour les actions
fonctionnelles d'acquittement et de resolution manuelle.

Prefixe retenu :

`/api/v1/alerts`

### GET /api/v1/alerts/summary

Methode HTTP :

- `GET`

Role :

- fournir la synthese du centre d'alertes ;
- alimenter les compteurs et le resume de la page Desktop.

Parametres :

- aucun parametre obligatoire ;
- filtres optionnels possibles par periode ou perimetre si le projet les normalise lors de l'implementation.

Reponse attendue :

- nombre total d'alertes ;
- nombre d'alertes actives ;
- nombre d'alertes acquittees ;
- nombre d'alertes resolues ;
- nombre d'alertes par severite ;
- date de la derniere alerte observee ;

### GET /api/v1/alerts

Methode HTTP :

- `GET`

Role :

- lister les alertes avec pagination, filtres et tri ;
- alimenter le tableau principal du centre d'alertes.

Parametres :

- `page` : numero de page ;
- `page_size` : taille de page ;
- `status` : filtre par etat ;
- `severity` : filtre par severite ;
- `source` : filtre par origine logique, transmis au backend comme `source_type` ;
- `category` : filtre par categorie fonctionnelle ;
- `search` : recherche textuelle sur le titre ou le message ;
- `sort` : tri autorise, par exemple derniere observation ou severite.

Reponse attendue :

- liste paginee d'alertes ;
- metadonnees de pagination ;
- informations minimales necessaires a l'affichage ;
- aucun secret ni detail sensible.

### GET /api/v1/alerts/{alert_id}

Methode HTTP :

- `GET`

Role :

- consulter le detail d'une alerte ;
- afficher le contexte fonctionnel et l'historique principal.

Parametres :

- `alert_id` : identifiant de l'alerte.

Reponse attendue :

- titre ;
- message ;
- severite ;
- etat ;
- source ;
- rattachements fonctionnels ;
- metadata non sensible ;
- dates `first_seen_at`, `last_seen_at`, `acknowledged_at` et `resolved_at` ;
- informations d'acquittement et de resolution lorsque disponibles.

### POST /api/v1/alerts/refresh-from-monitoring

Methode HTTP :

- `POST`

Role :

- generer ou mettre a jour les alertes a partir des evenements Monitoring deja persistes.

Parametres :

- aucun parametre obligatoire.

Reponse attendue :

- nombre d'alertes creees ;
- nombre d'alertes mises a jour ;
- nombre d'evenements Monitoring analyses ;
- liste des alertes creees ou mises a jour.

Contraintes :

- ne declenche aucun traitement externe ;
- ne lance aucune synchronisation ;
- ne contacte aucun connecteur.

### POST /api/v1/alerts/{alert_id}/acknowledge

Methode HTTP :

- `POST`

Role :

- marquer une alerte comme vue et prise en compte par un administrateur.

Parametres :

- `alert_id` : identifiant de l'alerte ;
- commentaire optionnel d'acquittement si cette fonctionnalite est retenue lors de l'implementation.

Reponse attendue :

- alerte mise a jour ;
- etat `Acknowledged` ;
- date d'acquittement ;
- utilisateur ayant acquitte lorsque disponible.

Contraintes :

- ne corrige pas l'alerte ;
- ne declenche aucune action automatique ;
- ne doit pas etre disponible sans droits administrateur.

### POST /api/v1/alerts/{alert_id}/resolve

Methode HTTP :

- `POST`

Role :

- marquer une alerte comme resolue lorsque la situation est consideree comme terminee.

Parametres :

- `alert_id` : identifiant de l'alerte ;
- aucun parametre obligatoire.

Reponse attendue :

- alerte mise a jour ;
- etat `Resolved` ;
- date de resolution ;

Contraintes :

- ne supprime pas l'alerte ;
- ne lance aucune verification externe ;
- ne declenche aucune synchronisation ;
- doit rester reserve aux administrateurs.

## Architecture Backend

L'architecture backend attendue respecte la separation deja definie dans le projet.

Routes

↓

Services

↓

Repositories

↓

Models

Responsabilites des routes :

- declarer les endpoints REST ;
- verifier l'authentification et les droits administrateur ;
- valider les parametres d'entree ;
- deleguer au service d'alertes ;
- retourner les schemas de reponse ;
- ne contenir aucune logique metier ;
- ne jamais contacter directement un connecteur externe.

Responsabilites des services :

- appliquer les regles de creation fonctionnelle des alertes ;
- gerer la deduplication ;
- gerer les transitions d'etat ;
- determiner les niveaux de severite selon les regles metier ;
- consolider les informations issues du monitoring ;
- preparer les messages fonctionnels affichables ;
- garantir l'absence de donnees sensibles dans les reponses ;
- decider quand une alerte peut etre acquittee ou resolue.

Responsabilites des repositories :

- lire et persister les alertes ;
- appliquer les filtres autorises ;
- appliquer la pagination ;
- appliquer les tris autorises ;
- rechercher une alerte active par cle de deduplication ;
- mettre a jour les champs d'etat et d'historique ;
- ne porter aucune regle metier.

Responsabilites des models :

- representer la structure persistante des alertes ;
- rester coherent avec les schemas Pydantic futurs ;
- permettre les rattachements fonctionnels aux sources existantes ;
- ne stocker aucun secret ;
- rester evolutif pour les futurs besoins d'orchestration.

Le centre d'alertes doit s'integrer au backend existant. Il ne doit pas creer une architecture parallele et ne doit pas
dupliquer les responsabilites du monitoring.

## Architecture Desktop

L'architecture Desktop prevue suit le flux impose dans le projet.

Page

↓

Service

↓

ApiClient

↓

API REST

Responsabilites de la page :

- afficher le resume des alertes ;
- afficher la liste paginee ;
- afficher les filtres ;
- afficher les etats de chargement, d'erreur et d'absence de donnees ;
- permettre l'acquittement et la resolution manuelle lorsque l'utilisateur a les droits ;
- ne contenir aucune logique metier.

Responsabilites du service Desktop :

- encapsuler les appels REST du centre d'alertes ;
- exposer des methodes de consultation et d'action fonctionnelle ;
- transmettre les filtres et la pagination a l'API ;
- convertir les erreurs HTTP en erreurs exploitables par la page.

Responsabilites d'ApiClient :

- rester le point unique de communication HTTP ;
- appliquer les mecanismes existants d'authentification ;
- centraliser les erreurs reseau et API ;
- ne pas connaitre les regles metier des alertes.

Responsabilites de l'API REST :

- rester la source de verite ;
- appliquer les droits ;
- appliquer les regles metier ;
- fournir les donnees deja qualifiees au Desktop.

Le Desktop ne doit pas recalculer la severite, ne doit pas deduire l'etat d'une alerte et ne doit pas interroger
directement les donnees de monitoring, PostgreSQL ou les connecteurs externes.

## Interface Desktop

La future interface Desktop doit etre une page d'administration consultative, coherente avec le design existant de
l'application, l'inspiration Windows 11, le mode sombre natif et les conventions deja utilisees.

### Resume

La zone de resume doit afficher :

- nombre d'alertes actives ;
- nombre d'alertes critiques ;
- nombre d'alertes en warning ;
- nombre d'alertes informatives ;
- nombre d'alertes acquittees ;
- nombre d'alertes resolues recemment ;
- date de derniere alerte observee.

### Filtres

Filtres attendus :

- etat : active, acquittee, resolue ;
- severite : info, warning, critical ;
- source : monitoring, synchronisation, connecteur, SEO, GEO, crawl, systeme ;
- site ;
- connecteur ;
- planification ;
- periode ;
- recherche textuelle ;
- affichage des alertes resolues ou non.

Les filtres doivent etre combines sans declencher de traitement externe. Ils servent uniquement a interroger l'API REST.

### Colonnes

Colonnes principales du tableau :

- severite ;
- titre ;
- source ;
- perimetre concerne ;
- etat ;
- premiere observation ;
- derniere observation ;
- acquittement ;
- resolution ;
- actions.

Le tableau doit etre trie par priorite fonctionnelle, puis par date de derniere observation decroissante lorsque le
backend expose ce tri.

### Badges

Badges attendus :

- badge de severite ;
- badge d'etat ;
- badge de source ;
- badge de connecteur lorsque disponible ;
- badge de site ou de perimetre lorsque disponible.

Les badges doivent rester courts et lisibles.

### Couleurs

Codification fonctionnelle attendue :

- `Info` : couleur neutre ou bleue discrete ;
- `Warning` : couleur d'avertissement visible mais non agressive ;
- `Critical` : couleur d'urgence forte et prioritaire ;
- `Active` : etat visible ;
- `Acknowledged` : etat attenue mais toujours present ;
- `Resolved` : etat discret, oriente historique.

Les couleurs ne doivent pas etre le seul moyen de comprehension. Les libelles et badges doivent rester explicites.

### Boutons

Boutons attendus :

- actualiser ;
- acquitter ;
- resoudre ;
- voir le detail ;
- reinitialiser les filtres.

Les boutons ne doivent pas lancer de synchronisation, de crawl, de test de connecteur ou d'appel externe.

### Navigation

La page doit etre accessible depuis la navigation d'administration ou depuis le centre de monitoring si l'architecture de
navigation le prevoit.

La navigation attendue :

- entree vers le centre d'alertes ;
- lien possible depuis le monitoring vers les alertes filtrees ;
- retour possible vers le monitoring ;
- consultation du detail sans perdre le contexte de liste lorsque c'est possible.

## Notifications Desktop

Le Sprint 33 ne depend pas d'un systeme de notifications Windows ou d'un mecanisme natif du systeme d'exploitation.

Les notifications Desktop attendues sont internes a l'application :

- compteur visible dans la page ou la navigation ;
- mise en evidence des alertes critiques dans le centre d'alertes ;
- message applicatif apres acquittement ;
- message applicatif apres resolution ;
- indication claire lorsqu'une action echoue ;
- mise a jour de la liste apres une action utilisateur.

Le comportement attendu reste consultatif :

- aucune notification push native ;
- aucun email ;
- aucun SMS ;
- aucun webhook ;
- aucun son systeme ;
- aucune execution en arriere-plan ;
- aucune surveillance temps reel obligatoire.

Le rafraichissement peut etre manuel dans ce sprint. Un rafraichissement automatique ne doit pas etre considere comme
necessaire pour terminer le Sprint 33.

## Regles metier

Regles fonctionnelles principales :

- une meme alerte active ne doit pas etre dupliquee ;
- la deduplication doit s'appuyer sur une cle fonctionnelle stable ;
- une alerte active reste visible tant que sa cause est consideree comme presente ;
- une alerte acquittee reste visible ;
- une alerte acquittee n'est pas consideree comme resolue ;
- une alerte resolue reste dans l'historique ;
- une alerte resolue ne doit pas etre supprimee automatiquement ;
- une alerte critique reste prioritaire meme lorsqu'elle est acquittee ;
- une alerte ne doit jamais contenir de secret ;
- une alerte ne doit jamais exposer de token, cle API, mot de passe ou en-tete d'autorisation ;
- le Desktop ne doit pas recalculer la severite ;
- le Desktop ne doit pas recalculer l'etat ;
- les routes ne doivent pas contenir de logique metier ;
- les repositories ne doivent pas porter les regles de severite ou de transition ;
- les services portent les regles de detection, de deduplication et de transition ;
- l'acquittement doit enregistrer une date ;
- l'acquittement doit enregistrer l'utilisateur lorsque disponible ;
- la resolution doit enregistrer une date ;
- la resolution doit conserver une raison fonctionnelle lorsque fournie ;
- la resolution ne doit pas declencher de verification externe ;
- la creation ou mise a jour d'une alerte ne doit pas lancer de synchronisation ;
- la creation ou mise a jour d'une alerte ne doit pas appeler Internet ;
- les alertes doivent etre filtrables ;
- les listes doivent etre paginees ;
- les messages doivent etre comprehensibles par un administrateur ;
- les messages techniques bruts doivent etre evites lorsqu'ils ne sont pas necessaires ;
- les alertes issues du monitoring doivent rester coherentes avec les etats consolides du Sprint 32 ;
- les alertes issues des synchronisations doivent rester coherentes avec les planifications du Sprint 31 ;
- une alerte rattachee a une ressource supprimee ou devenue inaccessible doit rester consultable avec son contexte
  historique minimal ;
- les actions d'acquittement et de resolution doivent etre reservees aux administrateurs ;
- la consultation doit respecter les regles d'authentification existantes ;
- aucun traitement automatique ne doit etre declenche depuis le centre d'alertes.

## Criteres d'acceptation

Le Sprint 33 pourra etre considere comme termine lors de son implementation future si les criteres suivants sont
respectes :

- un centre d'alertes consultatif est disponible pour les administrateurs ;
- les alertes exploitent les donnees deja consolidees par le monitoring ;
- aucune execution automatique n'est ajoutee ;
- aucun scheduler n'est ajoute ;
- aucun appel Internet n'est effectue par le module ;
- les niveaux `Info`, `Warning` et `Critical` sont representes ;
- les etats `Active`, `Acknowledged` et `Resolved` sont representes ;
- une alerte active equivalente n'est pas dupliquee ;
- une alerte peut etre acquittee ;
- une alerte acquittee reste visible ;
- une alerte peut etre resolue ;
- une alerte resolue reste dans l'historique ;
- les dates `first_seen_at` et `last_seen_at` sont gerees ;
- les dates d'acquittement et de resolution sont conservees lorsque pertinentes ;
- les alertes sont listables avec pagination ;
- les alertes sont filtrables par severite, etat, source et periode ;
- un endpoint de synthese fournit les compteurs principaux ;
- un endpoint de detail permet de consulter une alerte ;
- les endpoints sont proteges par authentification et droits administrateur lorsque necessaire ;
- aucune information sensible n'est exposee ;
- l'architecture backend respecte le flux Routes, Services, Repositories, Models ;
- l'architecture Desktop respecte le flux Page, Service, ApiClient, API REST ;
- le Desktop ne contient aucune logique metier ;
- l'interface affiche les filtres, colonnes, badges, couleurs, boutons et resume attendus ;
- les actions Desktop ne declenchent aucune synchronisation, aucun crawl et aucun test de connecteur ;
- les tests futurs couvrent les regles de deduplication, transitions, filtres, droits et absence d'appel externe ;
- la documentation reste coherente avec les Sprints 31 et 32.

## Hors perimetre

Le Sprint 33 exclut explicitement :

- scheduler ;
- orchestration ;
- execution automatique ;
- synchronisations automatiques ;
- relance automatique ;
- tests en direct des connecteurs ;
- appels Internet ;
- appels aux APIs Google Search Console ;
- appels aux APIs Google Analytics ;
- appels aux APIs Bing Webmaster Tools ;
- appels a des modeles IA externes ;
- lancement de crawl ;
- lancement d'analyse SEO ;
- lancement d'analyse GEO ;
- emails ;
- SMS ;
- webhooks ;
- notifications Windows natives ;
- notifications push systeme ;
- files de taches ;
- workers ;
- Celery ;
- Redis ;
- correction automatique ;
- modification automatique d'une planification ;
- modification automatique d'un connecteur ;
- exports ;
- rapports PDF ;
- refonte du monitoring ;
- refonte de l'administration ;
- nouvelle dependance technique non justifiee ;
- stockage de secrets dans les alertes.

Le Sprint 33 definit le cadre du centre d'alertes. Il ne doit pas anticiper l'orchestration reelle des traitements.

## Preparation du Sprint 34

Le Sprint 33 prepare le Sprint 34 en fournissant une couche de priorisation et de suivi des situations anormales.

L'orchestrateur futur aura besoin de connaitre :

- quelles sources sont en erreur ;
- quelles synchronisations sont en retard ;
- quelles alertes critiques existent ;
- quelles alertes ont deja ete prises en compte ;
- quelles alertes sont resolues ;
- quelles causes sont recurrentes ;
- quels perimetres doivent etre evites ou traites en priorite.

Le centre d'alertes permettra a l'orchestrateur de s'appuyer sur un etat fonctionnel qualifie, sans devoir interpreter
directement tous les evenements de monitoring.

Le Sprint 34 pourra utiliser cette base pour definir des regles d'orchestration plus robustes :

- ne pas lancer une action si une alerte critique bloque le connecteur concerne ;
- prioriser une synchronisation en retard ;
- eviter une relance sur une source deja connue comme indisponible ;
- contextualiser les decisions d'execution avec l'historique des alertes ;
- separer clairement la detection, la consultation et l'action.

Cette separation est essentielle. Le Sprint 33 observe, qualifie et historise. Le Sprint 34 pourra orchestrer, mais devra
le faire a partir d'un socle d'alertes deja structure, filtre et auditable.
