# Sprint 24B - Google Search Console Desktop

## 1. Objectif

Le Sprint 24B documente l'exploitation, depuis l'application Desktop, du backend Google Search Console developpe au
Sprint 24A.

Ce sprint ne cree aucune integration Google directe cote Desktop. Le Desktop reste une interface de consultation et de
declenchement via l'API REST existante ou future.

Principes obligatoires :

- le Desktop consomme exclusivement l'API REST ;
- aucun acces PostgreSQL direct depuis le Desktop n'est autorise ;
- aucune communication directe avec Google n'est effectuee depuis le Desktop ;
- aucune authentification Google n'est geree dans le Desktop ;
- toute la logique metier reste cote backend.

Le Sprint 24B constitue donc une couche de restitution Desktop au-dessus du backend Google Search Console. Il ne
remplace pas le backend du Sprint 24A et ne contourne pas ses services.

## 2. Architecture

Architecture Desktop cible :

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

Le Desktop ne connait pas les repositories, les models SQLAlchemy, les schemas internes du backend ni les connecteurs
Google. Il appelle uniquement des endpoints REST exposes par le backend.

La logique metier reste cote backend :

- validation des droits ;
- lecture et ecriture PostgreSQL ;
- import des donnees Google Search Console ;
- normalisation des resultats ;
- historisation des imports ;
- gestion des erreurs metier ;
- orchestration des connecteurs externes.

Le Desktop est responsable de l'affichage, des filtres de consultation, des etats de chargement et de la presentation
lisible des erreurs retournees par l'API.

## 3. Fonctionnalites

Le Sprint 24B prepare les fonctionnalites Desktop suivantes.

### 3.1 Consultation des proprietes

La page Desktop doit permettre de consulter les proprietes Google Search Console disponibles via l'API REST.

Donnees attendues :

- liste des proprietes ;
- etat de chaque propriete ;
- derniere synchronisation connue.

Le Desktop ne synchronise pas lui-meme les proprietes. Il affiche les informations retournees par le backend.

### 3.2 Performances

La consultation des performances doit permettre d'afficher les indicateurs issus de Google Search Console deja importes
par le backend.

Indicateurs prevus :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- filtres.

Filtres possibles :

- propriete ;
- periode ;
- page ;
- requete ;
- pays ;
- appareil.

Le Desktop transmet les filtres a l'API REST. Le calcul, l'agregation et la verification des droits restent cote
backend.

### 3.3 Indexation

La consultation de l'indexation doit restituer les informations d'etat disponibles via le backend.

Donnees prevues :

- pages valides ;
- pages exclues ;
- erreurs ;
- avertissements.

L'objectif est de donner une lecture claire de la couverture d'indexation sans que le Desktop n'interprete directement
les donnees brutes Google.

### 3.4 Sitemaps

La vue Sitemaps doit presenter les sitemaps connus pour une propriete.

Donnees prevues :

- URL ;
- statut ;
- derniere lecture ;
- nombre d'URL.

Le Desktop ne soumet pas directement de sitemap a Google. Toute action future devra passer par un endpoint REST dedie
et rester orchestree par le backend.

### 3.5 Import manuel

L'import manuel est declenche depuis le Desktop uniquement par appel d'un endpoint REST.

Flux attendu :

```text
Utilisateur
    |
    v
GSCPage
    |
    v
GSCService
    |
    v
ApiClient
    |
    v
Endpoint REST d'import
    |
    v
Backend Google Search Console
```

Le Desktop ne recupere pas directement les donnees Google. Il demande au backend de lancer l'import, puis affiche le
statut ou le resultat retourne par l'API.

Le backend reste responsable de :

- l'appel au connecteur Google Search Console ;
- la gestion des quotas ;
- la normalisation des donnees ;
- la persistance ;
- la journalisation ;
- la gestion des erreurs.

### 3.6 Historique des imports

Le Desktop doit permettre de consulter l'historique des imports Google Search Console exposes par l'API.

Donnees a afficher :

- date ;
- duree ;
- statut ;
- elements importes ;
- erreurs.

L'historique doit aider a comprendre la fraicheur des donnees et les eventuels echecs d'import.

## 4. Integration Dashboard

Le Dashboard defini au Sprint 23 pourra progressivement exploiter les donnees Google Search Console via l'API REST.

Le Dashboard ne doit pas effectuer lui-meme d'import. Il consomme les donnees deja disponibles et exposees par le backend.

Premieres metriques envisagees :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- date de synchronisation.

Integration cible :

```text
DashboardPage
    |
    v
DashboardService
    |
    v
ApiClient
    |
    v
API REST
    |
    v
Backend Dashboard + donnees GSC
```

Les donnees Google Search Console enrichissent le Dashboard. Elles ne remplacent pas les donnees de crawl, SEO ou GEO
deja prevues.

## 5. Architecture Desktop

Architecture cible du module Desktop Google Search Console :

```text
GSCPage
    |
    v
GSCService
    |
    v
ApiClient
    |
    v
Backend REST
```

Responsabilites de `GSCPage` :

- afficher les proprietes ;
- afficher les performances ;
- afficher les donnees d'indexation ;
- afficher les sitemaps ;
- afficher l'historique des imports ;
- proposer un declenchement d'import manuel ;
- gerer les etats de chargement ;
- afficher les erreurs lisibles.

Responsabilites de `GSCService` :

- appeler les endpoints REST Google Search Console ;
- transmettre les filtres ;
- normaliser les retours pour la page ;
- transformer les erreurs API en messages exploitables par l'interface ;
- ne jamais acceder directement a PostgreSQL ;
- ne jamais appeler Google directement.

Responsabilites de `ApiClient` :

- centraliser les appels HTTP ;
- appliquer la configuration d'URL API ;
- gerer les erreurs HTTP ;
- gerer les erreurs reseau ;
- retourner les donnees JSON au service Desktop.

## 6. Fichiers prevus

Fichiers prevus pour une implementation future, sans creation dans le cadre de cette documentation :

```text
desktop/services/gsc_service.py
desktop/ui/gsc_page.py
tests/desktop/test_gsc_service.py
```

Ces fichiers ne sont pas crees par le present document.

## 7. Fichiers qui seront modifies

Fichiers susceptibles d'etre modifies lors de l'implementation future :

```text
desktop/ui/main_window.py
desktop/core/constants.py
desktop/core/api_client.py
```

`desktop/core/api_client.py` ne devra etre modifie que si necessaire, par exemple pour exposer une methode generique
deja compatible avec les besoins du service Google Search Console.

Aucun fichier backend, aucune route FastAPI, aucun modele SQLAlchemy, aucune migration Alembic et aucun fichier Python
source ne sont modifies dans le cadre du present Sprint 24B documentaire.

## 8. Tests prevus

Les tests Desktop futurs devront utiliser exclusivement `MockTransport`. Ils ne devront appeler ni une vraie API
backend, ni Google, ni PostgreSQL.

Tests prevus :

- recuperation des proprietes ;
- recuperation des performances ;
- recuperation des donnees d'indexation ;
- recuperation des sitemaps ;
- import manuel ;
- erreurs HTTP ;
- erreurs reseau.

Principes de test :

- simuler les reponses REST avec `MockTransport` ;
- verifier les chemins appeles ;
- verifier les parametres transmis ;
- verifier la normalisation des payloads ;
- verifier la transformation des erreurs en exceptions ou resultats lisibles ;
- garantir qu'aucun connecteur Google n'est utilise cote Desktop.

Exemples de cas :

| Cas | Attendu |
| --- | --- |
| API retourne les proprietes | `GSCService` retourne une liste exploitable par la page. |
| API retourne les performances | Les metriques sont transmises sans recalcul metier Desktop. |
| API retourne une erreur HTTP | Le service remonte une erreur Desktop lisible. |
| Erreur reseau | Le service remonte une erreur normalisee. |
| Import manuel accepte | Le service retourne le statut d'import fourni par l'API. |

## 9. Hors perimetre

Le Sprint 24B ne comprend pas :

- OAuth Desktop ;
- authentification Google ;
- appels directs Google ;
- suppression des donnees ;
- planification automatique des imports ;
- creation de connecteur Google ;
- modification du backend Google Search Console ;
- modification des routes FastAPI ;
- modification des models SQLAlchemy ;
- migration Alembic ;
- modification des tests existants ;
- creation de code Python dans le cadre du present document.

Toute evolution de ces sujets devra faire l'objet d'un sprint separe.

## 10. Contraintes d'implementation future

L'implementation future devra respecter les contraintes suivantes :

- travailler par extension du Desktop existant ;
- reutiliser `ApiClient` ;
- ne pas dupliquer un client HTTP dedie ;
- ne pas importer de code backend dans le Desktop ;
- conserver les traitements metier cote backend ;
- afficher les absences de donnees comme des etats normaux lorsque l'API les retourne ainsi ;
- distinguer erreurs reseau, erreurs HTTP et donnees absentes ;
- documenter toute nouvelle API consommee.

Le module Desktop Google Search Console doit rester une interface cliente. Il ne devient ni un connecteur, ni un moteur
d'import, ni une couche de persistance.

## 11. Conclusion

Le Sprint 24B constitue la premiere integration Desktop de Google Search Console.

Il s'appuie sur le backend Google Search Console du Sprint 24A et prepare une consultation structuree des proprietes, des
performances, de l'indexation, des sitemaps et de l'historique des imports depuis l'application Desktop.

Cette integration respecte l'architecture :

```text
GSCPage -> GSCService -> ApiClient -> Backend REST
```

Elle prepare les futurs sprints :

- Sprint 25 Google Analytics 4 Backend ;
- Sprint 26 Google Analytics 4 Desktop ;
- Sprint 27 Bing Webmaster Tools.

Le principe directeur reste constant : le Desktop consomme l'API REST, le backend porte la logique metier, et aucune
communication directe avec Google ou PostgreSQL n'est effectuee depuis l'application Desktop.
