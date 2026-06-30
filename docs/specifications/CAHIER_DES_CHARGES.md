# Cahier des charges fonctionnel et métier

## 1. Informations générales

| Élément | Description |
|---|---|
| Nom du projet | Veille SEO-GEO Groupe A.P&Partner |
| Nature de l'application | Plateforme interne de pilotage SEO, GEO, contenus, concurrents, rapports et configuration |
| Public | Utilisateurs internes du Groupe A.P&Partner |
| État du document | Document de cadrage haut niveau |
| Rôle du document | Source de vérité fonctionnelle et métier pour les futures spécifications |
| Périmètre documentaire | Besoin, modules, règles structurantes, limites, livrables et critères de réussite |

Ce cahier des charges définit le cadre fonctionnel général de l'application interne
**Veille SEO-GEO Groupe A.P&Partner**.

Il ne remplace pas les documents d'architecture, les spécifications techniques détaillées,
les modèles de données, les contrats API ou les documents de design. Il fixe le périmètre
métier attendu et sert de base aux documents futurs :

- `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` ;
- `DATABASE_DESIGN_SPECIFICATION.md` ;
- `DEVELOPMENT_ROADMAP.md`.

Le document doit pouvoir être lu par un responsable projet, un responsable SEO/GEO,
un développeur backend, un développeur Desktop et un futur intervenant frontend.

## 2. Contexte et justification

### 2.1 Évolution du SEO

Le référencement naturel reste un canal stratégique pour les entités du Groupe A.P&Partner.
Il ne se limite plus au suivi de positions. Il inclut désormais la qualité technique des sites,
la structure des contenus, les signaux de performance, la cohérence des pages, la concurrence,
les requêtes informationnelles et transactionnelles, ainsi que la capacité à prioriser les actions.

Les équipes doivent suivre des volumes croissants de données :

- sites web multiples ;
- pages et URLs à auditer ;
- mots-clés par entité, univers, intention et priorité ;
- concurrents directs ou indirects ;
- contenus publiés, à mettre à jour ou à produire ;
- indicateurs techniques et éditoriaux ;
- rapports internes et historiques d'évolution.

Un suivi dispersé rend difficile la comparaison, la priorisation et la traçabilité des décisions.

### 2.2 Apparition du GEO

Le GEO, ou **Generative Engine Optimization**, correspond à l'optimisation de la visibilité
dans les réponses produites par les moteurs d'IA générative.

Les utilisateurs ne consultent plus uniquement des résultats de recherche classiques. Ils
interrogent aussi des assistants comme ChatGPT, Gemini, Claude, Copilot ou Perplexity. Ces
outils peuvent citer des marques, recommander des sites, résumer des contenus ou orienter
un choix d'achat sans passer par une page de résultats traditionnelle.

Pour le groupe, cette évolution crée de nouveaux besoins :

- savoir si les marques sont citées ;
- comprendre dans quels contextes elles apparaissent ;
- comparer la visibilité par modèle d'IA ;
- suivre les citations, absences, erreurs et biais ;
- mesurer l'évolution dans le temps ;
- relier les observations GEO aux contenus et aux performances SEO.

### 2.3 Besoin de centralisation

Les données SEO, GEO, éditoriales, concurrentielles et techniques doivent être rassemblées
dans un outil commun. La plateforme doit permettre aux utilisateurs internes d'accéder aux
mêmes référentiels, aux mêmes historiques et aux mêmes règles de lecture.

La centralisation vise à réduire :

- les fichiers isolés ;
- les exports manuels non synchronisés ;
- les indicateurs contradictoires ;
- les décisions non tracées ;
- les pertes d'information entre équipes ;
- la difficulté à produire des rapports homogènes.

### 2.4 Limites des suivis dispersés

Les suivis dispersés posent plusieurs problèmes métier.

| Problème | Impact métier | Réponse attendue de la plateforme |
|---|---|---|
| Données réparties dans plusieurs fichiers | Lecture lente, erreurs de version | Référentiels centralisés |
| Absence d'historique commun | Difficulté à mesurer l'évolution | Historisation progressive |
| Suivi SEO et GEO séparés | Vision incomplète de la visibilité | Lecture croisée SEO/GEO |
| Reporting manuel | Temps élevé, risque d'erreur | Rapports structurés |
| Configuration non maîtrisée | Risque de perte ou d'écrasement | Import/export non destructif |
| Droits peu formalisés | Risque d'accès excessif | Rôles et permissions adaptés |

## 3. Objectifs du projet

### 3.1 Objectifs principaux

La plateforme doit permettre de :

- centraliser les données SEO, GEO, contenus, concurrents, rapports et configuration ;
- suivre les sites web gérés par le groupe ;
- analyser les mots-clés et leurs évolutions ;
- structurer les contenus et leurs statuts ;
- comparer les performances entre sites, entités et concurrents ;
- mesurer la visibilité dans les IA génératives ;
- produire des rapports exploitables ;
- fournir une interface Desktop interne stable ;
- préparer un futur frontend React sans modifier les fondations métier ;
- maintenir une architecture claire et durable.

### 3.2 Objectifs secondaires

Les objectifs secondaires sont :

- réduire les manipulations manuelles ;
- améliorer la cohérence des décisions SEO/GEO ;
- faciliter les audits internes ;
- renforcer la traçabilité des actions sensibles ;
- préparer les futures automatisations métier ;
- sécuriser progressivement les accès ;
- améliorer la lisibilité des données pour des profils non techniques.

### 3.3 Objectifs non recherchés

Le projet ne vise pas, dans son périmètre initial, à :

- remplacer tous les outils SEO externes spécialisés ;
- créer immédiatement un frontend React complet ;
- automatiser des actions destructives sans validation humaine ;
- produire un crawler massif non contrôlé ;
- fournir une plateforme publique ;
- exposer directement PostgreSQL à un client Desktop ou frontend ;
- figer définitivement tous les modèles de données avant les spécifications détaillées.

## 4. Périmètre fonctionnel global

Le périmètre global couvre les domaines suivants.

| Domaine | Rôle fonctionnel | Statut cible |
|---|---|---|
| Sites web | Référentiel des sites suivis | Socle métier prioritaire |
| SEO | Suivi naturel, audits et indicateurs | Module central |
| GEO | Visibilité dans les IA génératives | Module central |
| Mots-clés | Suivi, priorisation, analyse | Module métier prioritaire |
| Contenus | Production, optimisation, historique | Module métier attendu |
| Concurrents | Comparaison et veille | Module métier attendu |
| Rapports | Synthèses, exports, suivi décisionnel | Module transversal |
| Configuration | Paramètres, fournisseurs, imports/exports | Module transversal |
| Administration | Utilisateurs, rôles, droits, sécurité | Module sensible |
| Logs et audit | Traçabilité technique et métier | Module de contrôle |
| Desktop | Interface interne PySide6 | Surface actuelle |
| Frontend React | Interface web future | Évolution future |

Le périmètre doit rester modulaire. Chaque module doit pouvoir évoluer sans imposer une
refonte complète de l'application.

## 5. Utilisateurs cibles

### 5.1 Profils principaux

| Profil | Besoin principal | Niveau d'accès attendu |
|---|---|---|
| Administrateur | Configurer, gérer les accès, surveiller les logs | Accès étendu et protégé |
| Responsable SEO/GEO | Piloter les analyses, prioriser les actions | Accès métier avancé |
| Rédacteur | Suivre les contenus et recommandations | Accès contenu et consultation ciblée |
| Analyste | Comparer les données, produire des rapports | Accès lecture et analyse |
| Lecteur/consultation | Consulter tableaux de bord et rapports | Accès limité en lecture |

### 5.2 Profils futurs éventuels

Des profils complémentaires pourront être définis plus tard selon les besoins :

- responsable direction ;
- chef de projet marketing ;
- prestataire externe encadré ;
- support technique ;
- auditeur interne.

Ces profils futurs ne doivent pas être supposés actifs immédiatement. Ils doivent être
identifiés comme des évolutions possibles à valider.

## 6. Besoins métier principaux

### 6.1 Centraliser les données

L'application doit fournir un point d'entrée unique pour consulter les informations liées
aux sites, mots-clés, contenus, concurrents, analyses SEO, analyses GEO, rapports et paramètres.

### 6.2 Suivre les performances

Les utilisateurs doivent pouvoir suivre l'évolution des performances sur des périodes
pertinentes. Les indicateurs doivent être lisibles, comparables et contextualisés.

### 6.3 Détecter les évolutions

La plateforme doit aider à repérer :

- une progression ou régression SEO ;
- une perte de visibilité GEO ;
- une baisse de qualité technique ;
- une variation concurrentielle ;
- un contenu à mettre à jour ;
- un écart entre deux sites ou entités.

### 6.4 Comparer les sites

Les sites doivent pouvoir être comparés selon des axes métier communs :

- entité ou marque ;
- type de site ;
- thématique ;
- priorité ;
- état actif ou inactif ;
- indicateurs SEO/GEO disponibles.

### 6.5 Analyser les mots-clés

Les mots-clés doivent être exploitables par intention, priorité, site, contenu, concurrent
et historique. Le suivi doit aider à décider quelles pages créer, optimiser ou surveiller.

### 6.6 Suivre la visibilité dans les IA génératives

Le GEO doit permettre de comprendre comment les IA génératives répondent à des requêtes
liées aux marchés du groupe, aux marques, aux produits, aux conseils et aux contenus.

### 6.7 Structurer la production de contenu

Le module contenu doit aider à organiser les sujets, statuts, priorités et liens avec
les mots-clés ou analyses GEO. Il ne doit pas devenir un outil éditorial complet sans
validation ultérieure.

### 6.8 Produire des rapports

Les rapports doivent fournir des synthèses utiles pour la décision. Ils doivent rester
compréhensibles par des profils métier et pouvoir s'appuyer progressivement sur les données
centralisées.

## 7. Modules attendus

### 7.1 Vue synthétique des modules

| Module | Rôle | Priorité fonctionnelle |
|---|---|---|
| Sites web | Référencer les sites suivis | Haute |
| Mots-clés | Suivre les requêtes et intentions | Haute |
| Contenus | Structurer la production et optimisation | Moyenne à haute |
| Concurrents | Organiser la veille concurrentielle | Moyenne à haute |
| SEO | Auditer et suivre la performance naturelle | Haute |
| GEO | Mesurer la visibilité IA générative | Haute |
| Rapports | Synthétiser et partager les résultats | Moyenne |
| Configuration | Gérer paramètres et référentiels techniques | Haute |
| Administration | Gérer accès, rôles et éléments sensibles | Haute |
| Logs | Tracer actions, erreurs et événements | Haute |
| Desktop | Offrir l'interface interne actuelle | Haute |

### 7.2 Matrice d'interactions principales

| Module source | Interagit avec | Nature de l'interaction |
|---|---|---|
| Sites web | SEO, GEO, mots-clés, contenus, rapports | Point de rattachement principal |
| Mots-clés | SEO, contenus, concurrents, GEO | Analyse par intention et priorité |
| Contenus | Mots-clés, SEO, GEO, rapports | Optimisation et suivi éditorial |
| Concurrents | SEO, GEO, mots-clés, rapports | Comparaison et veille |
| Configuration | Administration, GEO, rapports | Paramètres et fournisseurs |
| Logs | Administration, sécurité, import/export | Traçabilité |
| Desktop | FastAPI | Consultation et actions via HTTP REST |

## 8. Description fonctionnelle par module

### 8.1 Module sites web

**Rôle du module**

Le module sites web constitue le référentiel des sites suivis par le groupe. Il doit permettre
de connaître les sites actifs, leur rattachement, leur état et leurs informations principales.

**Fonctions attendues**

- créer et maintenir une fiche site ;
- consulter la liste des sites ;
- filtrer les sites actifs ou inactifs ;
- rechercher un site ;
- rattacher un site à une entité ou un contexte métier lorsque disponible ;
- fournir un socle commun aux modules SEO, GEO, contenus et rapports.

**Données manipulées**

- nom du site ;
- URL ;
- statut ;
- entité ou marque associée ;
- dates de création et modification ;
- métadonnées utiles au suivi.

**Interactions avec les autres modules**

Le module sites web alimente les modules SEO, GEO, contenus, mots-clés, concurrents et rapports.
Il sert de point de rattachement pour la majorité des analyses.

**Limites du module**

Le module ne doit pas contenir à lui seul toute la logique SEO ou GEO. Il référence les sites,
mais les analyses spécialisées restent dans leurs modules.

### 8.2 Module mots-clés

**Rôle du module**

Le module mots-clés permet de suivre les requêtes importantes pour les sites et les entités
du groupe.

**Fonctions attendues**

- créer ou importer des mots-clés ;
- associer des mots-clés à un site, une entité, un contenu ou une thématique ;
- qualifier l'intention de recherche ;
- définir une priorité ;
- consulter l'historique ou les évolutions lorsqu'elles seront disponibles ;
- préparer les analyses SEO et GEO.

**Données manipulées**

- expression de recherche ;
- langue ou marché si nécessaire ;
- intention ;
- priorité ;
- volume ou indicateur externe futur ;
- position ou tendance future ;
- rattachements métier.

**Interactions avec les autres modules**

Les mots-clés alimentent les modules SEO, contenus, concurrents, GEO et rapports.

**Limites du module**

Le module ne remplace pas un outil externe complet de suivi de position. Il centralise les
informations utiles au pilotage interne et pourra intégrer des données externes validées.

### 8.3 Module contenus

**Rôle du module**

Le module contenus doit structurer les contenus existants, à créer, à optimiser ou à surveiller.

**Fonctions attendues**

- référencer les contenus liés aux sites ;
- suivre les statuts éditoriaux ;
- associer des contenus à des mots-clés ;
- relier un contenu à des recommandations SEO ou GEO ;
- identifier les contenus à mettre à jour ;
- fournir une base aux rapports éditoriaux.

**Données manipulées**

- titre ou sujet ;
- URL ou page associée ;
- statut ;
- priorité ;
- type de contenu ;
- date de publication ou de mise à jour ;
- mots-clés associés ;
- recommandations ou notes métier.

**Interactions avec les autres modules**

Les contenus se rattachent aux sites, mots-clés, analyses SEO, observations GEO et rapports.

**Limites du module**

Le module n'est pas un CMS. Il ne remplace pas WordPress, Prestashop ou d'autres systèmes de
publication. Toute intégration avancée devra être validée séparément.

### 8.4 Module concurrents

**Rôle du module**

Le module concurrents permet d'identifier et suivre les acteurs comparables aux sites ou
entités du groupe.

**Fonctions attendues**

- référencer les concurrents ;
- associer un concurrent à une entité, un site ou une thématique ;
- suivre les domaines concurrents ;
- préparer les comparaisons SEO et GEO ;
- alimenter les rapports de veille.

**Données manipulées**

- nom du concurrent ;
- domaine ou URL ;
- marché ou thématique ;
- priorité de surveillance ;
- notes d'analyse ;
- rattachements aux sites ou entités.

**Interactions avec les autres modules**

Les concurrents interagissent avec les modules SEO, GEO, mots-clés, contenus et rapports.

**Limites du module**

Le module ne doit pas lancer de scraping massif ou non contrôlé. Les données externes doivent
être collectées selon des règles validées et documentées.

### 8.5 Module SEO

**Rôle du module**

Le module SEO regroupe les analyses liées au référencement naturel classique.

**Fonctions attendues**

- suivre les indicateurs SEO principaux ;
- analyser les balises et contenus ;
- auditer les URLs ;
- suivre les performances techniques utiles ;
- identifier les problèmes prioritaires ;
- produire des recommandations exploitables.

**Données manipulées**

- URLs ;
- balises ;
- scores ou statuts d'audit ;
- positions ou tendances futures ;
- Core Web Vitals ou indicateurs techniques futurs ;
- erreurs détectées ;
- recommandations.

**Interactions avec les autres modules**

Le SEO s'appuie sur les sites, mots-clés, contenus, concurrents et rapports.

**Limites du module**

Le module ne doit pas mélanger la logique GEO avec la logique SEO. Les analyses peuvent être
comparées, mais elles restent distinguées pour conserver une lecture claire.

### 8.6 Module GEO

**Rôle du module**

Le module GEO mesure la visibilité dans les réponses des IA génératives.

**Fonctions attendues**

- définir des requêtes ou prompts de suivi ;
- suivre les réponses produites par des modèles IA ;
- identifier les citations de marques, sites ou concurrents ;
- comparer les modèles comme ChatGPT, Gemini, Claude, Copilot et Perplexity ;
- historiser les résultats lorsque le modèle de données le permettra ;
- produire des indicateurs de visibilité GEO.

**Données manipulées**

- prompts ;
- fournisseurs ou modèles IA ;
- réponses observées ;
- citations ;
- mentions de marques ;
- concurrents cités ;
- date d'analyse ;
- score ou qualification GEO future.

**Interactions avec les autres modules**

Le GEO interagit avec les sites, contenus, mots-clés, concurrents, configuration IA,
rapports, logs et administration.

**Limites du module**

Le module doit rester extensible. Il ne doit pas supposer que les modèles d'IA, leurs API ou
leurs formats de réponse resteront stables. Toute comparaison doit être présentée comme une
observation contextualisée, pas comme une vérité absolue.

### 8.7 Module rapports

**Rôle du module**

Le module rapports produit des synthèses exploitables par les équipes internes.

**Fonctions attendues**

- générer ou référencer des rapports ;
- regrouper des indicateurs SEO, GEO, contenus et concurrents ;
- filtrer par site, entité ou période ;
- préparer des exports futurs ;
- historiser les rapports importants.

**Données manipulées**

- titre du rapport ;
- période ;
- périmètre ;
- indicateurs sélectionnés ;
- statut ;
- format futur ;
- date de génération.

**Interactions avec les autres modules**

Les rapports consomment les données des modules sites, SEO, GEO, mots-clés, contenus,
concurrents, logs et administration.

**Limites du module**

Le module rapports ne doit pas devenir un moteur BI complet sans décision dédiée. Les exports
doivent rester contrôlés, sécurisés et traçables.

### 8.8 Module configuration

**Rôle du module**

Le module configuration centralise les paramètres fonctionnels et techniques non secrets
nécessaires au fonctionnement de la plateforme.

**Fonctions attendues**

- consulter les paramètres ;
- modifier les paramètres autorisés ;
- gérer les fournisseurs IA ou connecteurs configurables ;
- exporter une configuration non secrète ;
- importer une configuration de manière aussi non destructive et idempotente que possible.

**Données manipulées**

- paramètres applicatifs ;
- fournisseurs IA ;
- modèles IA ;
- options fonctionnelles ;
- configuration non secrète ;
- métadonnées d'import/export.

**Interactions avec les autres modules**

La configuration alimente l'administration, le GEO, les rapports, les logs et les futurs
connecteurs externes.

**Limites du module**

Les secrets ne doivent pas être exportés en clair. Les imports ne doivent pas écraser
massivement des données sans contrôle, validation ou traçabilité.

### 8.9 Module administration

**Rôle du module**

Le module administration gère les éléments sensibles de la plateforme.

**Fonctions attendues**

- administrer les utilisateurs lorsque l'authentification est active ;
- gérer les rôles et permissions ;
- consulter les indicateurs d'administration ;
- surveiller les erreurs et événements sensibles ;
- gérer les clés ou références de connecteurs selon les règles de sécurité ;
- contrôler les accès aux endpoints sensibles.

**Données manipulées**

- utilisateurs ;
- rôles ;
- permissions ;
- journaux ;
- paramètres sensibles masqués ;
- clés ou références de clés ;
- événements d'administration.

**Interactions avec les autres modules**

L'administration interagit avec la configuration, les logs, la sécurité, les imports/exports,
les fournisseurs IA et les modules métier protégés.

**Limites du module**

Le module administration doit être protégé par authentification et droits adaptés. Il ne doit
pas exposer de secrets, de tokens ou d'informations internes inutiles.

### 8.10 Module logs et audit

**Rôle du module**

Le module logs et audit permet de comprendre les événements techniques, métier et sensibles
sans exposer d'informations confidentielles.

**Fonctions attendues**

- consulter des logs applicatifs utiles ;
- consulter des événements d'audit ;
- tracer les actions sensibles ;
- distinguer erreurs, événements métier et actions administratives ;
- faciliter le diagnostic en cas d'incident.

**Données manipulées**

- type d'événement ;
- niveau ;
- date ;
- acteur si disponible ;
- module concerné ;
- message non sensible ;
- métadonnées autorisées.

**Interactions avec les autres modules**

Les logs et audits sont transverses. Ils concernent l'administration, la configuration,
les imports/exports, l'API, le Desktop et les modules métier.

**Limites du module**

Les logs ne doivent jamais contenir de mot de passe, token, clé API brute, secret, chaîne de
connexion ou payload sensible complet.

### 8.11 Module Desktop

**Rôle du module**

L'application Desktop PySide6 constitue l'interface interne actuelle de la plateforme.

**Fonctions attendues**

- proposer une navigation stable ;
- afficher les modules principaux ;
- consommer les données via l'API FastAPI ;
- gérer les états de chargement, erreur et absence de données ;
- préparer l'authentification future ;
- rester cohérente avec le design système existant.

**Données manipulées**

Le Desktop manipule des données reçues par HTTP REST. Il ne manipule pas directement les
tables PostgreSQL.

**Interactions avec les autres modules**

Le Desktop interagit avec FastAPI via un client HTTP centralisé. Il affiche les données des
modules métier selon les droits et les contrats API disponibles.

**Limites du module**

Le Desktop ne doit jamais accéder directement à PostgreSQL. Il ne doit pas porter la logique
métier principale, ni contourner les règles d'authentification ou d'autorisation.

## 9. Exigences générales

### 9.1 Sécurité

La sécurité doit être intégrée dès la conception. Les endpoints sensibles doivent être protégés
par authentification et droits adaptés. Les secrets doivent rester hors du code et ne jamais
être exposés dans les logs, exports ou réponses API.

### 9.2 Traçabilité

Les actions sensibles doivent être auditables. Les imports, exports, changements de rôle,
modifications de configuration et accès admin doivent pouvoir être retracés selon les
capacités disponibles.

### 9.3 Fiabilité

L'application doit éviter les comportements destructifs implicites. Les imports doivent être
contrôlés, les erreurs compréhensibles et les opérations métier testables.

### 9.4 Maintenabilité

La plateforme doit conserver une architecture modulaire, lisible et documentée. Les modules
ne doivent pas se dupliquer ni contourner les responsabilités des couches existantes.

### 9.5 Évolutivité

Le projet doit pouvoir intégrer progressivement de nouveaux sites, modules, connecteurs,
indicateurs et surfaces utilisateur sans réécriture globale.

### 9.6 Cohérence documentaire

Ce cahier des charges doit rester cohérent avec les documents d'architecture, design,
sécurité, API, Desktop, base de données et administration.

### 9.7 Compatibilité Desktop/FastAPI

Le Desktop doit continuer à consommer FastAPI via HTTP REST. Les contrats API utilisés par
le Desktop doivent rester stables ou être coordonnés en cas d'évolution.

### 9.8 Préparation du futur React

Le futur frontend React devra reprendre les intentions métier, les libellés, les états et les
règles de sécurité. Il ne doit pas imposer une duplication de logique métier côté interface.

## 10. Contraintes techniques structurantes

Ce document reste fonctionnel, mais les contraintes suivantes sont structurantes et déjà actées.

```text
Client Desktop / Futur React
        |
        v
FastAPI Routes
        |
        v
Services métier
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

### 10.1 Règles d'architecture obligatoires

- les routes FastAPI ne doivent pas contenir de logique métier ;
- les routes appellent les services ;
- les services contiennent la logique métier ;
- les repositories contiennent uniquement l'accès aux données SQLAlchemy ;
- les modèles SQLAlchemy représentent les tables ;
- les schémas Pydantic gèrent les entrées et sorties API ;
- le Desktop communique uniquement avec FastAPI via HTTP REST ;
- le Desktop ne doit jamais accéder directement à PostgreSQL ;
- les migrations Alembic doivent être explicites ;
- `Base.metadata.create_all()` ne doit pas être utilisé dans les migrations ;
- `Base.metadata.drop_all()` ne doit pas être utilisé dans les migrations.

### 10.2 Stack actuelle de référence

| Couche | Technologie actuelle |
|---|---|
| Backend | Python 3.13 |
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Base de données | PostgreSQL |
| Validation | Pydantic v2 |
| Tests | Pytest |
| Linting | Ruff |
| Desktop | PySide6 + httpx |
| Frontend web | React prévu plus tard |

## 11. Contraintes de sécurité

### 11.1 Authentification

Les endpoints privés ou sensibles doivent être protégés par une authentification adaptée.
L'authentification doit être centralisée et ne doit pas être recodée localement dans chaque
module.

### 11.2 Droits et permissions

Les droits doivent permettre de distinguer lecture, modification, administration et actions
sensibles. L'interface peut masquer des actions, mais l'API reste l'autorité finale.

### 11.3 Endpoints d'administration

Les endpoints admin doivent être considérés comme sensibles. Ils doivent appliquer des
contrôles d'accès stricts dès que le mécanisme d'authentification est disponible.

### 11.4 Données sensibles et secrets

Les secrets doivent être stockés exclusivement dans les mécanismes prévus, notamment `.env`
ou solutions futures validées. Ils ne doivent pas être présents dans le code, la documentation
opérationnelle, les logs, les exports ou les réponses API.

### 11.5 Logs

Les logs doivent être utiles au diagnostic, mais minimaux. Ils ne doivent jamais contenir de
mot de passe, token, clé API brute, secret OAuth, chaîne de connexion ou payload sensible
complet.

### 11.6 Exports

Les exports doivent éviter les secrets, être traçables et porter uniquement les données
nécessaires au besoin métier. Les exports de configuration doivent être non destructifs et
idempotents autant que possible.

## 12. Contraintes de qualité

### 12.1 Tests

Les fonctionnalités métier importantes doivent être testées. Les tests doivent couvrir les
règles métier, les cas d'erreur et les contrats API lorsque ceux-ci sont concernés.

### 12.2 Linting

Le code doit rester compatible avec Ruff. Les changements doivent éviter les contournements,
les imports inutiles et les duplications évidentes.

### 12.3 Migrations propres

Toute évolution structurelle de la base doit passer par une migration Alembic explicite.
Les migrations doivent être relues comme des livrables sensibles.

### 12.4 Documentation

Toute fonctionnalité importante doit être documentée dans le périmètre approprié. Les détails
techniques ne doivent pas être ajoutés dans ce cahier des charges lorsqu'ils appartiennent à
une spécification dédiée.

### 12.5 Branches Git et PR

Le développement doit se faire par branches. Le travail direct sur `main` est exclu. Les
changements doivent être validés avant intégration via une PR et des contrôles adaptés.

## 13. Hors périmètre initial

Les éléments suivants sont hors périmètre initial, sauf validation explicite ultérieure.

| Sujet hors périmètre | Raison |
|---|---|
| Frontend React complet immédiat | Prévu comme évolution future |
| Accès direct Desktop à PostgreSQL | Contraire à l'architecture officielle |
| Automatisation destructive sans validation | Risque métier et sécurité |
| Scraping massif non contrôlé | Risque technique, légal et réputationnel |
| Refonte globale non planifiée | Risque de dette et perte de stabilité |
| Intégrations externes avancées non validées | Dépendance API, coûts et sécurité |
| Moteur BI complet | Périmètre distinct à cadrer |
| CMS interne complet | Les CMS existants restent les outils de publication |
| Gestion publique multi-clients | L'application est interne au groupe |

## 14. Critères de réussite du projet

### 14.1 Critères métier

- les données clés sont centralisées ;
- les sites, mots-clés, contenus et concurrents sont consultables ;
- les analyses SEO et GEO peuvent être reliées aux sites ;
- les rapports fournissent une lecture exploitable ;
- les utilisateurs internes gagnent en cohérence et en temps d'analyse.

### 14.2 Critères techniques

- l'architecture `Routes -> Services -> Repositories -> Models` est respectée ;
- le Desktop communique uniquement avec FastAPI ;
- les migrations Alembic sont explicites ;
- les contrats Pydantic encadrent les entrées et sorties ;
- les tests et contrôles qualité disponibles passent avant PR.

### 14.3 Critères UX

- l'interface reste claire, sobre et orientée données ;
- les états de chargement, erreur et absence de données sont compréhensibles ;
- les modules sont accessibles via une navigation stable ;
- les profils non techniques peuvent lire les indicateurs principaux ;
- le futur React pourra reprendre les mêmes intentions.

### 14.4 Critères sécurité

- les endpoints sensibles sont protégés ;
- les droits sont adaptés aux profils ;
- aucun secret n'est exposé ;
- les actions sensibles sont auditables ;
- les exports et logs restent maîtrisés.

### 14.5 Critères maintenance

- les modules peuvent évoluer indépendamment ;
- la documentation reste cohérente ;
- les responsabilités de chaque couche restent claires ;
- les changements sont limités au périmètre demandé ;
- les futures spécifications peuvent s'appuyer sur ce document.

## 15. Risques identifiés

### 15.1 Matrice des risques

| Risque | Impact potentiel | Mesure de maîtrise |
|---|---|---|
| Complexité SEO/GEO | Modules difficiles à cadrer | Séparer SEO, GEO et rapports |
| Volumétrie | Lenteurs, requêtes lourdes | Pagination, filtres, index futurs |
| Dépendance aux API externes | Coûts, indisponibilité, changements | Connecteurs isolés et configurables |
| Dette technique | Maintenance difficile | Architecture en couches et tests |
| Incohérence documentaire | Décisions contradictoires | Mise à jour continue des docs |
| Sécurité | Fuite de données ou accès excessif | Auth, droits, logs sans secrets |
| Dispersion fonctionnelle | Produit trop large et peu lisible | Modules bornés et priorisés |

### 15.2 Points de vigilance

- éviter de mélanger backlog, architecture détaillée et besoin métier ;
- ne pas transformer le Desktop en couche métier ;
- ne pas créer d'accès direct à la base hors backend ;
- ne pas exposer de données sensibles dans les exports ;
- ne pas promettre d'intégrations externes sans validation des coûts, droits et limites API.

## 16. Principes de gouvernance du projet

### 16.1 Règles de gouvernance

- développement par branches ;
- aucune modification directe sur `main` ;
- PR vers `main` après validation ;
- documentation continue ;
- tests et linting avant intégration ;
- architecture stable ;
- changements limités au périmètre demandé ;
- aucune suppression, renommage ou déplacement de fichiers sans demande explicite.

### 16.2 Matrice de décision documentaire

| Type de décision | Document de référence |
|---|---|
| Besoin métier global | Ce cahier des charges |
| Exigences fonctionnelles détaillées | Software Requirements Specification |
| Modèle de données | Database Design Specification |
| Architecture backend | Documents `docs/architecture/` |
| Design et UX | Documents `docs/design/` et `docs/UI_UX.md` |
| Roadmap opérationnelle | Development Roadmap |
| API détaillée | Documentation API dédiée |

### 16.3 Validation des évolutions

Toute évolution majeure doit être cadrée avant développement :

- objectif métier ;
- périmètre ;
- impacts sur modules existants ;
- impacts sécurité ;
- impacts Desktop/API ;
- tests attendus ;
- documentation à mettre à jour.

## 17. Livrables attendus

### 17.1 Livrables applicatifs

| Livrable | Description |
|---|---|
| Backend FastAPI | API métier, services, repositories, modèles et schémas |
| Base PostgreSQL | Persistance structurée des données |
| Migrations Alembic | Évolution explicite du schéma |
| Application Desktop PySide6 | Interface interne actuelle |
| Documentation | Références métier, architecture, API, design et sécurité |
| Rapports | Synthèses SEO/GEO et suivi décisionnel |
| Futur frontend React | Interface web future, à cadrer plus tard |

### 17.2 Livrables documentaires futurs

- spécification des exigences logicielles ;
- spécification de conception de base de données ;
- roadmap de développement ;
- documentation API détaillée ;
- documentation des modules métier ;
- documentation d'exploitation et sécurité lorsque nécessaire.

## 18. Exemples conceptuels

Les exemples suivants illustrent des usages métier sans définir un backlog détaillé.

### 18.1 Exemple conceptuel 1 : suivi d'un site

Un responsable SEO consulte un site, voit son état, ses mots-clés prioritaires, ses contenus
associés, ses principaux signaux SEO et les observations GEO disponibles.

### 18.2 Exemple conceptuel 2 : visibilité GEO

Un analyste compare une requête sur plusieurs IA génératives. Il observe si une marque du
groupe est citée, si un concurrent apparaît et si la réponse contient une source ou une
recommandation exploitable.

### 18.3 Exemple conceptuel 3 : contenu à optimiser

Un rédacteur identifie un contenu associé à plusieurs mots-clés importants. Le contenu est
signalé comme à mettre à jour, avec des observations SEO et GEO rattachées.

### 18.4 Exemple conceptuel 4 : rapport mensuel

Un responsable produit un rapport pour une entité. Le rapport synthétise les évolutions
SEO, les signaux GEO, les contenus suivis et les concurrents les plus visibles.

### 18.5 Exemple conceptuel 5 : import de configuration

Un administrateur importe une configuration non secrète. L'import met à jour les éléments
identifiés sans écraser massivement les données existantes et produit un résultat traçable.

## 19. Synthèse finale

**Veille SEO-GEO Groupe A.P&Partner** doit devenir une plateforme interne de référence pour
piloter la visibilité organique et générative du groupe.

Le projet repose sur trois idées structurantes :

- centraliser les données utiles au pilotage SEO/GEO ;
- préserver une architecture claire, testable et durable ;
- fournir une interface interne exploitable aujourd'hui tout en préparant les évolutions futures.

Le cahier des charges fixe un cadre métier volontairement haut niveau. Les détails de contrats
API, modèles de données, migrations, composants UI, connecteurs et roadmap seront traités dans
les documents spécialisés.

La réussite du projet dépendra de la capacité à garder des modules bien bornés, une sécurité
progressive mais sérieuse, une documentation cohérente et un respect strict des responsabilités
entre Desktop, FastAPI, services, repositories, modèles et PostgreSQL.

## 20. Annexes

### 20.1 Glossaire SEO/GEO

| Terme | Définition |
|---|---|
| SEO | Optimisation de la visibilité dans les moteurs de recherche classiques |
| GEO | Optimisation et suivi de la visibilité dans les moteurs d'IA générative |
| Mot-clé | Requête ou expression suivie pour l'analyse SEO/GEO |
| Intention | Objectif probable de l'utilisateur derrière une requête |
| Citation | Mention d'une marque, d'un site ou d'une source dans une réponse IA |
| Prompt | Requête envoyée à un modèle d'IA générative |
| Rapport | Synthèse structurée destinée à la décision |
| Audit | Analyse d'un périmètre selon des critères définis |
| Connecteur | Module isolant l'intégration avec un service externe |

### 20.2 Acronymes

| Acronyme | Signification |
|---|---|
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| DB | Database |
| GEO | Generative Engine Optimization |
| HTTP | HyperText Transfer Protocol |
| IA | Intelligence artificielle |
| ORM | Object Relational Mapper |
| PR | Pull Request |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| SEO | Search Engine Optimization |
| UX | User Experience |

### 20.3 Diagramme ASCII récapitulatif

```text
Utilisateur interne
        |
        v
Desktop PySide6
        |
        | HTTP REST
        v
FastAPI
        |
        v
Services métier
        |
        v
Repositories
        |
        v
PostgreSQL
```

### 20.4 Règle de lecture du document

Ce document répond à la question : **quoi construire et pourquoi**.

Il ne répond pas en détail à :

- comment modéliser chaque table ;
- comment implémenter chaque endpoint ;
- comment organiser chaque sprint ;
- comment dessiner chaque écran ;
- comment configurer chaque connecteur externe.

Ces sujets seront traités dans les documents spécialisés prévus.
