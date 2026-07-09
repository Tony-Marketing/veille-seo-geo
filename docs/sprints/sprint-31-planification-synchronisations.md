# Sprint 31 — Planification des synchronisations

## 1. Objectifs

Le Sprint 31 a pour objectif de cadrer la mise en place d'une couche de planification des synchronisations dans la
plateforme Veille SEO-GEO Groupe A.P&Partner.

Ce sprint existe pour répondre à un besoin devenu transversal : les modules de collecte, d'analyse et de consultation
existent progressivement, mais leur déclenchement reste essentiellement manuel ou isolé par module. La plateforme doit
désormais disposer d'un socle commun permettant de déclarer quand une synchronisation doit être lancée, sur quel
périmètre, avec quel statut et selon quelle fréquence.

Objectifs fonctionnels principaux :

- centraliser la gestion des planifications de synchronisation ;
- permettre à un administrateur d'activer ou de désactiver une planification ;
- associer une planification à un type de synchronisation identifié ;
- définir une fréquence attendue pour chaque synchronisation ;
- suivre le statut fonctionnel d'une planification ;
- afficher les dates de dernière et de prochaine exécution théorique ;
- préparer un historique minimal des exécutions ;
- fournir une base technique stable pour les futures exécutions automatiques.

Bénéfices attendus pour l'application :

- homogénéiser le pilotage des imports et analyses ;
- éviter la duplication de mécanismes de planification dans chaque module ;
- rendre les synchronisations plus lisibles pour les administrateurs ;
- préparer les futurs sprints d'automatisation réelle sans introduire immédiatement de scheduler distribué ;
- améliorer la traçabilité des tâches prévues, désactivées, en attente ou en erreur ;
- fournir un contrat API réutilisable par le Desktop.

Le Sprint 31 est un sprint de conception et de préparation fonctionnelle. Il ne doit pas déclencher de synchronisation
réelle massive et ne doit pas modifier l'architecture globale du projet.

## 2. Contexte

La plateforme dispose déjà de plusieurs modules techniques ou fonctionnels liés à la collecte et à l'analyse de données :

- Google Search Console ;
- Google Analytics 4 ;
- Bing Webmaster Tools ;
- Crawls ;
- SEO Analysis ;
- GEO Analysis.

Ces modules couvrent des usages complémentaires :

- récupération de données de performance SEO ;
- récupération de données analytics ;
- récupération de données Bing ;
- exploration technique des sites ;
- analyse SEO ;
- analyse GEO et visibilité dans les réponses d'IA générative.

Chaque module possède ou prévoit ses propres services, repositories, connecteurs, modèles et endpoints REST. Cette
organisation modulaire doit être conservée.

La couche de planification devient nécessaire car les besoins d'exploitation ne se limitent plus au déclenchement manuel
d'une action. L'application doit pouvoir représenter des intentions récurrentes :

- synchroniser les données Google Search Console chaque jour ;
- importer les métriques Google Analytics 4 chaque matin ;
- vérifier Bing Webmaster Tools chaque semaine ;
- programmer un crawl mensuel ;
- préparer des analyses SEO ou GEO régulières ;
- désactiver temporairement une planification sans supprimer sa configuration.

Le Sprint 31 ne remplace pas les modules existants. Il ajoute une couche transverse qui décrit les planifications et leurs
états, tout en laissant l'exécution métier réelle aux services spécialisés de chaque module lors de sprints ultérieurs.

## 3. Périmètre du sprint

Le périmètre prévu du Sprint 31 inclut la conception et la future implémentation d'une gestion centralisée des
planifications de synchronisation.

Éléments inclus :

- création conceptuelle d'une entité de planification de synchronisation ;
- gestion des types de synchronisation supportés ;
- gestion des fréquences disponibles ;
- activation et désactivation d'une planification ;
- statut fonctionnel d'une planification ;
- association optionnelle à un site ou à une ressource cible selon les modules existants ;
- stockage de la date de dernière exécution connue ;
- calcul de la prochaine exécution théorique ;
- historique minimal du dernier résultat connu ;
- consultation paginée des planifications ;
- consultation du détail d'une planification ;
- création d'une planification ;
- édition d'une planification ;
- désactivation logique d'une planification ;
- endpoints REST protégés ;
- service backend portant les règles de calcul et de validation ;
- repository backend limité à l'accès aux données ;
- modèle de données préparé pour les évolutions futures ;
- service Desktop consommant exclusivement l'API REST ;
- page Desktop de gestion des planifications ;
- tests prévisionnels API, services, repositories et Desktop.

Le calcul de la prochaine exécution doit être déterministe et testable. Il doit dépendre de la fréquence, de l'état actif,
de la date de référence et de la dernière exécution connue.

L'historique minimal attendu ne constitue pas un journal complet d'exécution. Il doit seulement permettre d'afficher les
dernières informations utiles à l'administrateur : dernier statut, dernier message contrôlé, dernière date d'exécution et
prochaine date prévue.

## 4. Hors périmètre

Le Sprint 31 exclut explicitement :

- aucun scheduler distribué ;
- aucun Celery ;
- aucun Redis ;
- aucun worker asynchrone dédié ;
- aucune file de tâches ;
- aucune orchestration distribuée ;
- aucune exécution réelle massive ;
- aucune synchronisation réelle ;
- aucun appel réel aux API Google Search Console ;
- aucun appel réel aux API Google Analytics 4 ;
- aucun appel réel aux API Bing Webmaster Tools ;
- aucun lancement réel de crawl ;
- aucune analyse SEO réelle déclenchée automatiquement ;
- aucune analyse GEO réelle déclenchée automatiquement ;
- aucun React ;
- aucune refonte de l'architecture ;
- aucune duplication des services existants ;
- aucune logique métier dans les routes API ;
- aucune logique métier dans le Desktop ;
- aucun accès direct Desktop à PostgreSQL ;
- aucun accès direct Desktop aux connecteurs externes ;
- aucune nouvelle dépendance technique sans justification explicite ;
- aucune modification fonctionnelle des modules GSC, GA4, Bing, Crawls, SEO Analysis ou GEO Analysis ;
- aucune notification utilisateur ;
- aucun monitoring avancé ;
- aucun tableau de bord temps réel ;
- aucune stratégie de reprise automatique après échec.

Le sprint prépare la représentation et l'administration des planifications. L'exécution effective et automatisée sera
traitée dans un sprint ultérieur.

## 5. Architecture backend

L'architecture backend obligatoire reste la suivante :

```text
Routes
↓
Services
↓
Repositories
↓
Models
```

Responsabilités attendues par couche :

- les routes déclarent les endpoints, les paramètres, les dépendances de sécurité et les schémas de réponse ;
- les routes ne contiennent aucune logique métier ;
- les routes appellent les services ;
- les services portent les règles métier de planification ;
- les services valident les transitions d'état ;
- les services calculent la prochaine exécution théorique ;
- les services contrôlent les erreurs fonctionnelles ;
- les services décident quand une planification peut être créée, modifiée, activée ou désactivée ;
- les repositories encapsulent uniquement les accès SQLAlchemy ;
- les repositories appliquent les filtres, la pagination et les tris autorisés ;
- les repositories ne calculent aucune règle métier ;
- les modèles représentent les tables et leurs relations ;
- les schémas Pydantic décrivent les contrats d'entrée et de sortie de l'API.

La couche de planification ne doit pas appeler directement les connecteurs externes. Elle peut uniquement stocker et
exposer une intention de synchronisation. Les futurs services d'exécution devront utiliser cette intention pour déclencher
les services métier spécialisés, mais cette orchestration reste hors périmètre du Sprint 31.

Les endpoints de planification devront être intégrés dans l'API existante sans créer d'architecture parallèle. Le préfixe
exact devra respecter les conventions du projet au moment de l'implémentation.

## 6. Architecture Desktop

L'architecture Desktop obligatoire reste la suivante :

```text
Page
↓
Service
↓
ApiClient
↓
API REST
```

Responsabilités attendues :

- la page Desktop gère l'affichage, les interactions utilisateur, les états de chargement, les erreurs et les états vides ;
- le service Desktop encapsule les appels REST liés aux planifications ;
- `ApiClient` reste le point unique de communication HTTP ;
- l'API REST reste la source unique de vérité ;
- le backend reste responsable de la validation, du calcul de prochaine exécution et des règles métier.

Le Desktop ne contient aucune logique métier. Il ne doit pas recalculer les statuts, ne doit pas décider de la prochaine
exécution et ne doit pas lancer directement une synchronisation.

Le Desktop transmet les intentions utilisateur à l'API REST :

- créer une planification ;
- modifier une planification ;
- activer une planification ;
- désactiver une planification ;
- consulter la liste ;
- consulter le détail ;
- actualiser l'affichage.

Les erreurs HTTP doivent être converties en messages utilisateur clairs sans exposer de détail technique sensible.

## 7. Modèle de données proposé

Le futur modèle fonctionnel proposé est `SyncSchedule`.

Ce modèle représente une planification de synchronisation, c'est-à-dire une configuration indiquant qu'un type de tâche
doit être exécuté selon une fréquence donnée sur un périmètre fonctionnel défini.

Champs fonctionnels attendus :

- `id` : identifiant interne unique de la planification ;
- `name` : nom lisible par l'administrateur ;
- `description` : description optionnelle du rôle de la planification ;
- `sync_type` : type de synchronisation concerné ;
- `frequency` : fréquence attendue ;
- `status` : état fonctionnel courant ;
- `is_active` : indicateur d'activation ou de désactivation ;
- `website_id` : référence optionnelle au site concerné lorsque la synchronisation est liée à un site ;
- `target_id` : identifiant optionnel d'une ressource cible spécifique lorsque le module en a besoin ;
- `target_type` : type optionnel de ressource cible lorsque plusieurs périmètres sont possibles ;
- `last_run_at` : date et heure de dernière exécution connue ;
- `last_run_status` : dernier résultat fonctionnel connu ;
- `last_run_message` : message contrôlé associé au dernier résultat ;
- `next_run_at` : date et heure théorique de prochaine exécution ;
- `timezone` : fuseau horaire de référence pour le calcul des échéances ;
- `created_at` : date de création ;
- `updated_at` : date de dernière modification ;
- `created_by_user_id` : utilisateur ayant créé la planification lorsque l'information est disponible ;
- `updated_by_user_id` : dernier utilisateur ayant modifié la planification lorsque l'information est disponible.

Le modèle doit permettre d'exprimer une planification sans dépendre d'un module unique. Les types GSC, GA4, Bing, Crawl,
SEO et GEO doivent pouvoir cohabiter dans la même structure.

La présence de `last_run_at`, `last_run_status` et `last_run_message` sert uniquement d'historique minimal. Un historique
complet des exécutions pourra être introduit plus tard via une entité dédiée.

Le calcul de `next_run_at` doit être effectué par la couche service. Le repository ne doit pas porter cette règle.

Le modèle ne doit stocker aucun secret, aucune clé API, aucun token externe et aucune donnée sensible issue des
connecteurs.

## 8. États possibles

Les états fonctionnels doivent être simples, lisibles et compatibles avec une future automatisation.

États proposés :

- `Active` ;
- `Désactivée` ;
- `En attente` ;
- `Erreur`.

Signification attendue :

- `Active` : la planification est activée et possède une prochaine exécution théorique calculée ;
- `Désactivée` : la planification existe mais ne doit pas être prise en compte pour une exécution future ;
- `En attente` : la planification est activée mais n'a pas encore été exécutée ou attend son premier passage ;
- `Erreur` : la dernière exécution connue a échoué ou la planification présente une anomalie fonctionnelle contrôlée.

Le statut ne doit pas être utilisé comme mécanisme de verrouillage distribué. Il représente uniquement une information
fonctionnelle affichable et exploitable par l'API.

Les transitions attendues :

- une nouvelle planification active peut démarrer en `En attente` ;
- une planification en attente devient `Active` après calcul valide de la prochaine exécution ;
- une planification active peut devenir `Désactivée` sur action administrateur ;
- une planification désactivée peut redevenir `En attente` ou `Active` lors de sa réactivation ;
- une planification peut passer en `Erreur` si son dernier résultat connu est un échec contrôlé ;
- une planification en erreur peut revenir à `Active` après correction ou nouvelle validation.

## 9. Types de synchronisations

Les types de synchronisations prévus couvrent les modules déjà présents ou prévus dans l'application.

Types attendus :

- `GSC` ;
- `GA4` ;
- `Bing` ;
- `Crawl` ;
- `SEO` ;
- `GEO`.

Description fonctionnelle :

- `GSC` : synchronisation des données Google Search Console ;
- `GA4` : synchronisation des données Google Analytics 4 ;
- `Bing` : synchronisation des données Bing Webmaster Tools ;
- `Crawl` : planification d'un crawl technique ;
- `SEO` : planification d'une analyse SEO ;
- `GEO` : planification d'une analyse GEO.

Chaque type doit rester découplé de son exécution réelle. Le Sprint 31 décrit la planification, pas le déclenchement des
connecteurs ni l'analyse effective.

La liste doit rester extensible afin d'ajouter ultérieurement d'autres sources ou traitements sans refondre la structure.

## 10. Fréquences

Les fréquences fonctionnelles prévues sont :

- `Manuel` ;
- `Horaire` ;
- `Quotidien` ;
- `Hebdomadaire` ;
- `Mensuel`.

Comportement attendu :

- `Manuel` : aucune prochaine exécution automatique n'est calculée ; la planification peut servir de configuration
  réutilisable pour un déclenchement manuel futur ;
- `Horaire` : la prochaine exécution théorique est calculée à intervalle horaire depuis la date de référence retenue ;
- `Quotidien` : la prochaine exécution théorique est calculée une fois par jour ;
- `Hebdomadaire` : la prochaine exécution théorique est calculée une fois par semaine ;
- `Mensuel` : la prochaine exécution théorique est calculée une fois par mois.

Le service backend devra définir précisément la date de référence utilisée :

- dernière exécution connue lorsqu'elle existe ;
- date de création ou date de réactivation lorsque la planification n'a jamais été exécutée ;
- date courante contrôlée en tests pour garantir un calcul déterministe.

Pour les fréquences calendaires, le comportement en cas de fin de mois, changement d'heure ou fuseau horaire devra être
documenté au moment de l'implémentation. Le Sprint 31 doit au minimum prévoir le champ de fuseau horaire et des tests
associés.

## 11. API REST prévue

Les endpoints REST prévus doivent permettre de gérer les planifications sans exécuter réellement les synchronisations.

Préfixe recommandé :

```text
/api/v1/sync-schedules
```

Endpoints prévisionnels :

- `GET /api/v1/sync-schedules` : lister les planifications avec pagination, filtres et recherche ;
- `POST /api/v1/sync-schedules` : créer une planification ;
- `GET /api/v1/sync-schedules/{schedule_id}` : consulter le détail d'une planification ;
- `PATCH /api/v1/sync-schedules/{schedule_id}` : modifier une planification ;
- `POST /api/v1/sync-schedules/{schedule_id}/enable` : activer une planification ;
- `POST /api/v1/sync-schedules/{schedule_id}/disable` : désactiver une planification ;
- `POST /api/v1/sync-schedules/{schedule_id}/recalculate` : recalculer la prochaine exécution théorique si ce choix est
  retenu à l'implémentation.

Filtres prévisionnels pour la liste :

- type de synchronisation ;
- fréquence ;
- statut ;
- état actif ou inactif ;
- site associé ;
- recherche textuelle ;
- date de prochaine exécution ;
- page ;
- taille de page.

Rôle des endpoints :

- exposer une gestion administrative des planifications ;
- garantir des réponses paginées pour les listes ;
- appliquer les validations côté backend ;
- protéger les actions d'écriture ;
- ne jamais lancer directement une synchronisation réelle ;
- ne jamais exposer de secret ou donnée technique sensible.

Les routes doivent rester fines et déléguer toute règle au service.

## 12. Interface Desktop prévue

La future interface Desktop doit permettre à un administrateur de piloter les planifications via l'API REST.

Fonctionnalités attendues :

- liste des synchronisations planifiées ;
- recherche ;
- filtres par type, statut, fréquence et état actif ;
- affichage de la fréquence ;
- affichage du statut ;
- affichage de la dernière exécution connue ;
- affichage de la prochaine exécution théorique ;
- création d'une planification ;
- édition d'une planification ;
- activation d'une planification ;
- désactivation d'une planification ;
- actualisation de la liste ;
- consultation d'un détail simple ;
- affichage des messages d'erreur contrôlés.

La liste devra permettre une lecture rapide des informations suivantes :

- nom de la planification ;
- type de synchronisation ;
- site ou cible associée lorsque disponible ;
- fréquence ;
- statut ;
- état actif ;
- dernière exécution ;
- prochaine exécution.

La création et l'édition devront collecter uniquement les informations nécessaires :

- nom ;
- description optionnelle ;
- type ;
- fréquence ;
- site ou cible lorsque le type le nécessite ;
- état actif ;
- fuseau horaire si exposé à l'utilisateur.

La page Desktop ne doit pas contenir de maquette graphique dans ce document. Elle devra respecter le design existant de
l'application Desktop et les conventions déjà utilisées pour les autres modules.

## 13. Sécurité

Les endpoints de planification doivent être protégés.

Contraintes de sécurité attendues :

- authentification obligatoire pour accéder aux endpoints ;
- droits administrateur requis pour créer, modifier, activer ou désactiver une planification ;
- consultation limitée selon les règles de sécurité existantes du projet ;
- validation stricte des types de synchronisation ;
- validation stricte des fréquences ;
- validation des identifiants de site ou de cible ;
- validation des transitions d'état ;
- messages d'erreur contrôlés ;
- aucune exposition de secret ;
- aucune donnée sensible dans les logs ;
- aucune clé API, token ou identifiant externe confidentiel dans les réponses ;
- aucune exécution réelle déclenchée par un endpoint de configuration.

La sécurité doit rester appliquée côté backend. Le Desktop peut adapter l'affichage selon les erreurs reçues, mais il ne
doit pas porter la logique d'autorisation.

Les validations doivent empêcher :

- la création d'une fréquence inconnue ;
- la création d'un type de synchronisation inconnu ;
- l'activation d'une planification invalide ;
- l'association à une cible inexistante lorsque la cible est obligatoire ;
- les mises à jour incohérentes de statut ;
- les payloads incomplets ou ambigus.

## 14. Tests prévus

Les tests prévus devront couvrir les couches concernées sans déclencher de synchronisation réelle.

Tests API prévus :

- liste paginée des planifications ;
- création d'une planification valide ;
- refus d'un type inconnu ;
- refus d'une fréquence inconnue ;
- consultation d'un détail ;
- modification d'une planification ;
- activation d'une planification ;
- désactivation d'une planification ;
- refus sans authentification ;
- refus sans droits administrateur pour les actions d'écriture ;
- validation des filtres ;
- absence de déclenchement d'une synchronisation réelle.

Tests services prévus :

- calcul de prochaine exécution horaire ;
- calcul de prochaine exécution quotidienne ;
- calcul de prochaine exécution hebdomadaire ;
- calcul de prochaine exécution mensuelle ;
- absence de prochaine exécution automatique pour une fréquence manuelle ;
- transition d'activation ;
- transition de désactivation ;
- gestion d'une planification en erreur ;
- validation d'un type de synchronisation ;
- validation d'une fréquence ;
- contrôle des messages d'erreur fonctionnels.

Tests repository prévus :

- création d'une planification ;
- lecture par identifiant ;
- liste paginée ;
- filtres par type ;
- filtres par fréquence ;
- filtres par statut ;
- filtres par état actif ;
- mise à jour ;
- désactivation logique si le modèle retient cette approche ;
- tris autorisés ;
- absence de logique métier dans le repository.

Tests Desktop prévus :

- appel du service Desktop pour lister les planifications ;
- appel du service Desktop pour créer une planification ;
- appel du service Desktop pour modifier une planification ;
- appel du service Desktop pour activer une planification ;
- appel du service Desktop pour désactiver une planification ;
- affichage des états de chargement ;
- affichage d'un état vide ;
- affichage des erreurs HTTP contrôlées ;
- transmission des filtres ;
- transmission de la pagination ;
- absence de logique métier Desktop ;
- absence d'appel direct aux connecteurs externes ;
- absence d'appel direct à PostgreSQL.

Les tests Desktop devront simuler l'API REST. Aucun test ne devra appeler les API externes GSC, GA4, Bing, ni lancer de
crawl ou d'analyse réelle.

## 15. Critères d'acceptation

Le Sprint 31 sera considéré terminé lors de l'implémentation future si les critères suivants sont respectés :

- une entité de planification de synchronisation existe ;
- les types GSC, GA4, Bing, Crawl, SEO et GEO sont représentés ;
- les fréquences Manuel, Horaire, Quotidien, Hebdomadaire et Mensuel sont représentées ;
- une planification peut être créée depuis l'API REST ;
- une planification peut être consultée depuis l'API REST ;
- les planifications peuvent être listées avec pagination ;
- les planifications peuvent être filtrées par type, fréquence, statut et état actif ;
- une planification peut être modifiée ;
- une planification peut être activée ;
- une planification peut être désactivée ;
- le statut fonctionnel est exposé ;
- la date de dernière exécution connue est exposée lorsqu'elle existe ;
- la date de prochaine exécution théorique est calculée par le service backend ;
- la fréquence manuelle ne crée pas d'exécution automatique implicite ;
- aucune synchronisation réelle n'est déclenchée par la gestion des planifications ;
- les routes ne contiennent aucune logique métier ;
- les services portent les règles de validation et de calcul ;
- les repositories restent limités aux accès aux données ;
- le Desktop respecte le flux `Page -> Service -> ApiClient -> API REST` ;
- le Desktop ne contient aucune logique métier ;
- les endpoints d'écriture sont protégés par droits administrateur ;
- aucun secret n'est stocké ou exposé par ce module ;
- les tests API, services, repositories et Desktop couvrent le périmètre prévu ;
- les outils qualité disponibles du projet passent ;
- aucune modification React n'est introduite ;
- aucune refonte d'architecture n'est réalisée ;
- aucune dépendance Celery, Redis ou scheduler distribué n'est ajoutée.

## 16. Évolutions prévues

Le Sprint 31 prépare plusieurs évolutions possibles pour les sprints suivants.

Évolutions envisagées :

- mise en place d'un scheduler réel ;
- ajout de workers ;
- exécution automatique des synchronisations ;
- branchement des planifications sur les services GSC ;
- branchement des planifications sur les services GA4 ;
- branchement des planifications sur les services Bing Webmaster Tools ;
- lancement automatisé des crawls ;
- lancement automatisé des analyses SEO ;
- lancement automatisé des analyses GEO ;
- historique complet des exécutions ;
- journalisation détaillée des durées, volumes et erreurs ;
- notifications en cas d'échec ;
- notifications en cas de succès critique ;
- monitoring des synchronisations ;
- tableau de bord d'état des tâches ;
- relance manuelle depuis une planification ;
- reprise contrôlée après erreur ;
- limitation de concurrence ;
- verrouillage d'exécution ;
- priorisation des tâches ;
- gestion des fenêtres horaires autorisées ;
- stratégie de rétention des historiques.

Ces évolutions devront être développées progressivement. Le Sprint 31 doit donc privilégier une structure simple,
extensible et suffisamment découplée pour permettre l'ajout ultérieur d'une exécution réelle sans refonte du modèle de
planification.

