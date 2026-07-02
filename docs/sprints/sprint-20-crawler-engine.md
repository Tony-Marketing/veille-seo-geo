# Sprint 20 - Crawler Engine

## 1. Presentation Du Sprint

Le Sprint 20 marque le debut des fonctionnalites metier de la plateforme Veille SEO-GEO Groupe A.P&Partner.

Les sprints precedents ont installe les fondations necessaires :

- un backend FastAPI organise en couches ;
- une base PostgreSQL pilotee par SQLAlchemy et Alembic ;
- un client Desktop PySide6 connecte au backend via HTTP REST ;
- des modules Desktop CRUD pour les principales donnees de reference ;
- une separation claire entre interface, API, services, repositories et models.

L'objectif du Sprint 20 est de cadrer la conception du futur Crawler Engine. Ce moteur aura pour role d'explorer les
sites web suivis par la plateforme, de decouvrir leurs pages internes et de persister les resultats bruts du crawl afin
d'alimenter les analyses SEO, GEO, reporting et planification des sprints suivants.

Le Crawler Engine constitue donc un socle technique. Il ne produit pas encore d'analyse SEO, ne calcule pas de score et
ne fait pas appel a l'intelligence artificielle. Il prepare une base fiable de pages, URLs, statuts HTTP, redirections et
metadonnees techniques minimales issues du telechargement.

Place dans la feuille de route :

- Sprint 20 : conception et cadrage du Crawler Engine ;
- Sprint 21 : exploitation des pages crawlees pour l'analyse SEO ;
- Sprint 22 : exploitation des contenus pour l'analyse GEO avec Skill GPT ;
- Sprint 23 et suivants : tableaux de bord, connecteurs externes, rapports et planification.

Le present document est un document de conception. Il ne cree aucune API, aucun modele SQLAlchemy, aucune migration
Alembic et aucun fichier Python.

## 2. Objectifs Fonctionnels

Le futur Crawler Engine devra permettre de lancer et suivre l'exploration controlee d'un site web.

Objectifs fonctionnels principaux :

- lancer un crawl pour un site web reference dans la plateforme ;
- explorer un site web a partir d'une URL de depart ;
- decouvrir automatiquement les liens internes presents dans les pages telechargees ;
- telecharger les pages via HTTP ;
- suivre les redirections HTTP et conserver leur trace ;
- gerer les codes HTTP de reponse ;
- limiter la profondeur d'exploration ;
- limiter le nombre total de pages explorees ;
- detecter les doublons d'URL et les doublons de pages deja traitees ;
- persister les pages decouvertes et les resultats bruts du crawl ;
- suivre la progression du crawl depuis le backend et le Desktop ;
- conserver un etat exploitable en cas de crawl termine, interrompu ou en erreur.

Le moteur devra gerer les cas courants suivants :

- page repondant en `200 OK` ;
- redirection permanente ou temporaire ;
- page introuvable ;
- erreur serveur ;
- timeout reseau ;
- URL invalide ou non autorisee par les politiques de crawl ;
- lien externe ignore ;
- URL deja connue dans la session de crawl ;
- limite de profondeur atteinte ;
- limite de pages atteinte.

Le Sprint 20 ne realise aucune analyse SEO. En particulier, le Crawler Engine ne doit pas evaluer la qualite des balises,
ne doit pas calculer de score, ne doit pas interpreter le contenu et ne doit pas produire de recommandation.

## 3. Hors Perimetre

Le Sprint 20 ne traite pas les analyses et integrations metier avancees. Ces sujets seront documentes et developpes dans
les sprints suivants.

Sont explicitement hors perimetre :

- analyse Title ;
- analyse Meta Description ;
- analyse Hn ;
- analyse Canonical ;
- analyse Robots ;
- analyse JSON-LD ;
- analyse Open Graph ;
- analyse hreflang ;
- score SEO ;
- analyse GEO ;
- appels IA ;
- Skill GPT ;
- Google Search Console ;
- Google Analytics ;
- rapports ;
- export de rapports ;
- planification automatique ;
- alertes ;
- recommandations editoriales ;
- analyse concurrentielle avancee ;
- rendu JavaScript cote navigateur ;
- execution de scripts de pages web ;
- screenshots de pages ;
- audit de performance type Core Web Vitals.

Le moteur de crawl collecte les donnees brutes necessaires aux futurs modules. Il ne remplace pas les futurs services
d'analyse.

## 4. Architecture Proposee

Le futur Crawler Engine devra rester independant des routes FastAPI et respecter l'architecture backend existante :

```text
Routes
    -> Services
        -> Repositories
            -> Models
```

Le moteur sera appele par les services backend. Les routes exposeront uniquement des cas d'usage HTTP, tandis que les
services orchestreront le lancement, le suivi, l'arret et la persistance du crawl.

Architecture logique proposee :

```text
Crawler Service
        |
        v
Crawler Engine
        |
        +-- Crawl Policies
        |
        +-- Queue Manager
        |
        +-- HTTP Fetcher
        |
        +-- Link Extractor
        |
        +-- URL Normalizer
        |
        +-- Duplicate Detector
        |
        +-- Persistence
                |
                v
          Repositories
                |
                v
             Models
```

Role des composants :

| Composant | Role |
| --- | --- |
| Engine | Coordonne le cycle complet de crawl et applique les decisions globales. |
| Queue Manager | Gere les URLs en attente, les URLs en cours et l'ordre d'exploration. |
| HTTP Fetcher | Telecharge les pages via HTTP avec timeouts, gestion des erreurs et redirections. |
| Link Extractor | Extrait les liens internes depuis le HTML recu. |
| URL Normalizer | Nettoie, absolutise et canonicalise les URLs avant traitement. |
| Duplicate Detector | Evite de traiter plusieurs fois la meme URL ou une URL equivalente. |
| Crawl Policies | Porte les limites de profondeur, de volume, de domaine, de protocole et de securite. |
| Persistence | Enregistre les sessions de crawl, pages decouvertes, statuts, erreurs et progression. |

Les composants doivent rester specialises. Le moteur ne doit pas devenir une classe unique contenant toute la logique.

Principes attendus :

- le moteur ne connait pas FastAPI ;
- le moteur ne retourne pas directement de reponse HTTP ;
- le moteur n'accede pas a la base sans passer par une couche de persistance controlee ;
- les politiques de crawl sont explicites et testables ;
- les erreurs reseau sont capturees et transformees en etats persistables ;
- les futures analyses SEO/GEO pourront consommer les pages crawlees sans relancer inutilement le crawl.

## 5. Integration Au Backend

L'integration backend devra respecter la separation stricte des responsabilites.

### Routes

Les futures routes pourront exposer des actions telles que :

- demarrer un crawl ;
- demander l'arret d'un crawl ;
- consulter l'etat d'un crawl ;
- lister les pages decouvertes ;
- consulter le detail d'une page crawlee.

Les routes devront rester fines :

- validation du payload HTTP ;
- recuperation de l'utilisateur courant si necessaire ;
- appel au service backend ;
- choix du code HTTP ;
- retour d'un schema Pydantic.

Elles ne devront contenir aucune logique de crawl, aucune boucle d'exploration et aucun appel HTTP direct vers les sites
externes.

### Services

Les services backend porteront la logique metier :

- validation du site a crawler ;
- preparation de la session de crawl ;
- initialisation des politiques de crawl ;
- appel au Crawler Engine ;
- orchestration de l'arret d'un crawl ;
- calcul de l'etat de progression ;
- coordination entre moteur et repositories.

Le service sera le point d'entree applicatif du moteur. Il garantira que les regles metier restent en dehors des routes.

### Repositories

Les repositories encapsuleront l'acces aux donnees :

- creation d'une session de crawl ;
- mise a jour de l'etat d'une session ;
- enregistrement d'une page decouverte ;
- enregistrement d'un statut HTTP ;
- enregistrement d'une redirection ;
- recherche d'une page deja connue ;
- lecture paginee des resultats.

Ils ne devront pas contenir de logique HTTP, de parsing HTML ni de regle metier de crawl.

### Models Et Schemas

Les models SQLAlchemy et schemas Pydantic seront definis ulterieurement, lors du developpement effectif. Le Sprint 20 ne
cree aucun modele et aucune migration.

Le modele cible devra cependant permettre de representer au minimum :

- une session de crawl ;
- une page crawlee ;
- son URL source et son URL finale ;
- le statut HTTP ;
- la profondeur ;
- l'etat de traitement ;
- les erreurs eventuelles ;
- les dates de creation, demarrage, fin et mise a jour.

## 6. Integration Desktop

Le Desktop reste un client graphique. Il ne realise jamais le crawl lui-meme et n'accede jamais directement a
PostgreSQL.

Architecture Desktop attendue :

```text
Page
    -> Service
        -> ApiClient
            -> API REST
```

Role du Desktop :

- permettre a l'utilisateur de demarrer un crawl ;
- permettre a l'utilisateur de demander l'arret d'un crawl ;
- afficher la progression ;
- afficher l'etat courant ;
- consulter les pages decouvertes ;
- afficher les erreurs de crawl lisibles ;
- rafraichir les resultats depuis l'API ;
- presenter les limites appliquees au crawl.

Le Desktop ne doit pas :

- telecharger lui-meme les pages ;
- extraire les liens ;
- normaliser les URLs ;
- appliquer les politiques de crawl ;
- acceder a PostgreSQL ;
- importer des models SQLAlchemy ;
- contourner l'API REST.

Le futur module Desktop devra donc s'appuyer sur un service Desktop dedie, qui appellera les endpoints backend via
`ApiClient`, en coherence avec les modules deja livres.

## 7. Architecture De Fichiers Envisagee

La structure suivante est une proposition d'architecture pour le futur developpement. Elle ne doit pas etre creee dans le
cadre du present document.

```text
backend/app/crawler/
    __init__.py
    engine.py
    fetcher.py
    extractor.py
    queue.py
    normalizer.py
    duplicate_detector.py
    policies.py
    persistence.py
```

Fichiers backend susceptibles d'etre ajoutes lors du developpement futur :

```text
backend/app/api/v1/routes/crawls.py
backend/app/services/crawls.py
backend/app/repositories/crawls.py
backend/app/schemas/crawls.py
backend/app/models/crawl.py
```

Fichiers Desktop susceptibles d'etre ajoutes lors du developpement futur :

```text
desktop/services/crawls_service.py
desktop/ui/crawls_page.py
desktop/ui/dialogs/crawl_dialog.py
```

Tests susceptibles d'etre ajoutes lors du developpement futur :

```text
tests/services/test_crawls_service.py
tests/crawler/test_engine.py
tests/crawler/test_normalizer.py
tests/crawler/test_duplicate_detector.py
tests/desktop/test_crawls_service.py
```

Cette proposition devra etre verifiee au moment du developpement en fonction de l'etat exact du depot, des modules deja
presentes et des conventions etablies.

## 8. Flux De Fonctionnement

Le cycle complet du futur Crawler Engine peut etre decrit ainsi :

1. L'utilisateur selectionne un site et demande le demarrage d'un crawl depuis le Desktop.
2. La page Desktop transmet la demande au service Desktop.
3. Le service Desktop appelle l'API REST via `ApiClient`.
4. La route FastAPI recoit la demande et appelle le service backend.
5. Le service backend valide le site, les droits et les parametres.
6. Le service backend cree une session de crawl persistante.
7. Le Crawler Engine initialise les politiques de crawl.
8. Le Queue Manager place l'URL de depart dans la file.
9. Le HTTP Fetcher telecharge la page.
10. Le moteur enregistre le resultat brut : statut, URL finale, erreur eventuelle et profondeur.
11. Le Link Extractor extrait les liens depuis le HTML lorsque la reponse le permet.
12. Le URL Normalizer transforme les liens en URLs comparables et absolues.
13. Le Duplicate Detector elimine les URLs deja traitees ou deja en attente.
14. Les Crawl Policies refusent les URLs hors domaine, trop profondes ou hors limite.
15. Les nouveaux liens internes autorises sont ajoutes a la file.
16. Le moteur met a jour la progression.
17. Le cycle se repete jusqu'a epuisement de la file, limite atteinte, arret demande ou erreur bloquante.
18. La session de crawl passe dans un etat final : terminee, arretee ou en erreur.
19. Le Desktop interroge l'API pour afficher l'etat final et les resultats.

Etats possibles d'une session de crawl :

| Etat | Signification |
| --- | --- |
| `pending` | Session creee mais pas encore demarree. |
| `running` | Crawl en cours d'execution. |
| `stopping` | Arret demande, le moteur termine proprement les operations en cours. |
| `completed` | Crawl termine normalement. |
| `failed` | Crawl interrompu par une erreur bloquante. |
| `cancelled` | Crawl arrete volontairement par l'utilisateur ou le systeme. |

Indicateurs de progression a prevoir :

- nombre d'URLs en attente ;
- nombre de pages traitees ;
- nombre de pages en erreur ;
- nombre de redirections ;
- profondeur courante maximale ;
- limite de pages configuree ;
- date de debut ;
- date de derniere mise a jour ;
- duree totale lorsque le crawl est termine.

## 9. Preparation Des Futurs Sprints

Le Crawler Engine doit etre concu comme une fondation reutilisable pour les modules metier suivants.

### Sprint 21 - Analyse SEO

Les pages crawlees fourniront la matiere premiere pour analyser :

- Title ;
- Meta Description ;
- Hn ;
- Canonical ;
- Robots ;
- Open Graph ;
- JSON-LD ;
- hreflang ;
- maillage interne ;
- codes HTTP ;
- redirections.

Le Sprint 21 ne devra pas refaire l'exploration des sites si les donnees de crawl recentes sont deja disponibles.

### Sprint 22 - Analyse GEO Avec Skill GPT

Les contenus et URLs decouverts pourront alimenter l'analyse GEO :

- identification des pages de reference ;
- selection des contenus a analyser ;
- comparaison entre contenus de marque et concurrents ;
- preparation de prompts pour les modeles IA ;
- historisation des resultats GEO rattaches aux pages crawlees.

Le crawl restera distinct de l'analyse IA afin de conserver une architecture modulaire.

### Sprint 23 - Dashboard

Le Dashboard pourra exploiter les indicateurs issus du crawl :

- nombre de pages connues ;
- pages en erreur ;
- redirections ;
- profondeur moyenne ;
- evolution du volume de pages ;
- derniere date de crawl ;
- statut des crawls par site.

### Sprint 24 - Google Search Console

Les URLs crawlees pourront etre croisees avec les donnees Search Console :

- pages explorees mais sans impression ;
- pages avec impressions mais absentes du crawl ;
- pages indexables a prioriser ;
- comparaison entre visibilite Google et structure reelle du site.

### Sprint 25 - Google Analytics

Les resultats de crawl pourront etre compares aux donnees Analytics :

- pages crawlees sans trafic ;
- pages avec trafic mais non decouvertes dans le maillage ;
- priorisation des audits selon performance ;
- identification des pages importantes a surveiller.

### Sprint 26 - Rapports

Les rapports pourront utiliser les sessions de crawl comme source structuree :

- synthese du crawl ;
- liste des erreurs ;
- progression par site ;
- donnees de base pour les rapports SEO ;
- historique des explorations.

### Sprint 27 - Planification

Le moteur devra preparer la planification future :

- relance periodique de crawls ;
- priorisation selon criticite ;
- arret automatique selon limites ;
- suivi des executions planifiees ;
- comparaison entre plusieurs sessions dans le temps.

## 10. Conclusion

Le Crawler Engine est le socle technique des futures fonctionnalites metier SEO et GEO.

Sa responsabilite principale est de produire une base fiable, persistante et exploitable des pages decouvertes sur les
sites suivis. Il doit rester separe des routes FastAPI, des pages Desktop et des futures analyses afin de preserver une
architecture modulaire.

En cadrant clairement les composants du moteur, les responsabilites backend, l'integration Desktop et les limites du
perimetre, le Sprint 20 prepare un developpement progressif et robuste. Les sprints suivants pourront s'appuyer sur ce
socle pour construire les analyses SEO, GEO, dashboards, connecteurs externes, rapports et mecanismes de planification.

