# Sprint 23 - Dashboard SEO / GEO

## 1. Objectif Du Sprint

Le Sprint 23 definit la specification fonctionnelle et technique du futur Dashboard SEO / GEO de la plateforme Veille
SEO-GEO Groupe A.P&Partner.

Les sprints precedents ont installe les couches metier necessaires :

- Sprint 20 : moteur de crawl et persistance des pages ;
- Sprint 21 : moteur d'analyse SEO technique deterministe ;
- Sprint 22 : moteur d'analyse GEO modulaire ;
- Sprint 23 : restitution unifiee des resultats SEO et GEO.

Pipeline fonctionnel cible :

```text
Crawler
    -> HTML brut
        -> Analyse SEO
            -> Analyse GEO
                -> Dashboard
```

Le Dashboard est une couche de restitution. Il ne lance aucun traitement metier lourd et ne produit aucune analyse. Il
exploite uniquement les donnees deja presentes en base afin de donner une vision claire, rapide et actionnable des
performances SEO et GEO d'un site.

Objectifs principaux :

- fournir une vision globale de la sante SEO et GEO ;
- identifier rapidement les pages prioritaires ;
- comparer les scores SEO et GEO ;
- afficher les principaux signaux de crawl ;
- restituer les recommandations GEO les plus importantes ;
- preparer l'arrivee future des donnees Google Search Console ;
- preparer l'arrivee future des donnees Google Analytics 4 ;
- preparer la generation de rapports du Sprint 26.

Le present document est une specification. Il ne cree aucune route, aucun service, aucun modele, aucune migration, aucun
test et aucun code Desktop.

## 2. Perimetre

Le Sprint 23 couvre la conception du Dashboard SEO / GEO unifie.

Le perimetre fonctionnel inclut :

- definition des objectifs du Dashboard ;
- definition des cartes d'indicateurs ;
- definition des deux graphiques initiaux ;
- definition des flux de donnees ;
- definition des endpoints REST prevus ;
- definition des responsabilites backend et Desktop ;
- definition des criteres de validation ;
- preparation des evolutions des Sprints 24, 25 et 26.

Le perimetre technique inclut :

- lecture des resultats de crawl ;
- lecture des resultats SEO ;
- lecture des resultats GEO ;
- aggregation de donnees deja persistees ;
- exposition d'une API Dashboard dediee ;
- affichage Desktop via `DashboardPage`, `DashboardService` et `ApiClient`.

Le Dashboard ne doit pas devenir une couche d'analyse. Il doit rester une couche de consultation et de synthese.

## 3. Hors Perimetre

Sont explicitement hors perimetre du Sprint 23 :

- lancement d'un crawl ;
- modification du moteur de crawl ;
- nouvelle exploration HTTP ;
- telechargement d'une page distante ;
- execution d'une analyse SEO ;
- execution d'une analyse GEO ;
- appel a un provider IA ;
- creation de nouveaux scores metier ;
- creation de connecteur Google Search Console ;
- creation de connecteur Google Analytics 4 ;
- generation de rapports PDF, Word ou Excel ;
- graphiques historiques avances ;
- alertes automatiques ;
- planification d'analyses ;
- modification des modeles existants ;
- migration de base de donnees ;
- creation de code dans le cadre du present document.

Le Dashboard consomme les resultats disponibles. Si une donnee n'existe pas encore, elle doit etre affichee comme
indisponible ou reservee a une evolution future.

## 4. Principes Obligatoires

Principes structurants :

- le Dashboard ne realise aucun crawl ;
- le Dashboard ne realise aucune analyse SEO ;
- le Dashboard ne realise aucune analyse GEO ;
- le Dashboard ne realise aucune requete HTTP vers les sites analyses ;
- le Dashboard ne communique jamais directement avec PostgreSQL depuis le Desktop ;
- les routes FastAPI ne contiennent aucune logique metier ;
- les aggregations sont portees par un `DashboardService` backend ;
- les repositories existants restent responsables de la lecture des donnees ;
- le Desktop reste un client de l'API REST ;
- les donnees affichees doivent etre tracables vers les crawls, analyses SEO et analyses GEO sources.

Le Dashboard doit rester rapide, lisible et extensible.

## 5. Architecture Generale

Architecture backend cible :

```text
Routes Dashboard
    |
    v
DashboardService
    |
    +-- CrawlRepository
    +-- SeoAnalysisRepository
    +-- GeoAnalysisRepository
    |
    v
Donnees deja persistees
```

Architecture Desktop cible :

```text
DashboardPage
    |
    v
DashboardService Desktop
    |
    v
ApiClient
    |
    v
REST API
```

Architecture globale :

```text
Base PostgreSQL
    |
    +-- Crawl sessions
    +-- Crawl pages
    +-- SEO analyses
    +-- SEO issues
    +-- GEO analyses
    +-- GEO provider results
    +-- GEO recommendations
    |
    v
DashboardService
    |
    v
Dashboard API
    |
    v
Desktop Dashboard
```

Le Dashboard s'appuie sur les couches existantes. Il ne doit pas introduire une nouvelle source de verite.

## 6. Responsabilites Des Couches

| Couche | Responsabilite |
| --- | --- |
| Routes FastAPI | Exposer les endpoints Dashboard et deleguer au service. |
| DashboardService backend | Agreger les donnees crawl, SEO et GEO en objets de restitution. |
| Repositories | Lire les donnees persistantes existantes. |
| Schemas API | Normaliser les reponses du Dashboard. |
| DashboardService Desktop | Appeler l'API REST et normaliser les erreurs. |
| DashboardPage Desktop | Afficher les cartes, tableaux et graphiques. |
| ApiClient Desktop | Transport HTTP centralise. |

Les routes ne doivent pas :

- calculer des scores ;
- interroger plusieurs repositories directement pour produire une synthese ;
- lancer des traitements ;
- contenir de logique de priorisation ;
- acceder directement aux providers IA.

Le service backend peut :

- calculer des moyennes ;
- compter des anomalies ;
- classer des pages ;
- preparer les donnees pour les cartes ;
- preparer les donnees pour les graphiques ;
- choisir des valeurs de fallback lorsque certaines analyses sont absentes.

## 7. Flux De Donnees

Flux principal :

```text
Utilisateur
    |
    v
DashboardPage
    |
    v
DashboardService Desktop
    |
    v
GET /api/v1/dashboard/overview
    |
    v
DashboardService Backend
    |
    +-- lit les crawls
    +-- lit les analyses SEO
    +-- lit les issues SEO
    +-- lit les analyses GEO
    +-- lit les recommandations GEO
    |
    v
Synthese Dashboard
    |
    v
Desktop
```

Le flux ne contient aucune execution metier :

```text
Dashboard
    - ne crawle pas
    - n'analyse pas le HTML
    - n'appelle pas de Skill
    - n'appelle pas de provider IA
    - ne contacte pas de site distant
```

## 8. Donnees Sources

Le Dashboard exploite les donnees suivantes.

| Source | Donnees utiles |
| --- | --- |
| Crawl sessions | statut, pages trouvees, pages crawlees, erreurs, dates. |
| Crawl pages | URL, code HTTP, profondeur, type de contenu. |
| SEO analyses | score global, statut, pages analysees, issues totales. |
| SEO page analyses | score page, statut page, nombre d'issues. |
| SEO issues | severite, famille, critere, message. |
| GEO analyses | score GEO, score LLM, score global, statut. |
| GEO provider results | provider, modele, statut, reponses normalisees. |
| GEO recommendations | type, severite, priorite, titre, page concernee. |

Les donnees absentes doivent etre representees proprement. Exemple :

- score indisponible ;
- analyse non lancee ;
- aucune recommandation ;
- aucune page analysee ;
- dernier crawl introuvable.

## 9. Cartes Du Dashboard

Le Dashboard initial doit etre organise autour de cartes de synthese.

### 9.1 Sante SEO

Objectif : donner une lecture immediate de la qualite SEO technique.

Indicateurs :

- score SEO moyen ;
- meilleure page SEO ;
- pire page SEO ;
- nombre de pages analysees.

Regles de restitution :

- le score moyen est calcule depuis les pages SEO analysees ;
- la meilleure page est celle ayant le score SEO le plus eleve ;
- la pire page est celle ayant le score SEO le plus faible ;
- les pages sans score peuvent etre ignorees du calcul mais signalees dans les details.

### 9.2 Sante GEO

Objectif : donner une lecture immediate de la qualite GEO.

Indicateurs :

- score GEO moyen ;
- meilleure page GEO ;
- pire page GEO.

Regles de restitution :

- le score GEO moyen est calcule depuis les resultats GEO disponibles ;
- la meilleure page GEO est celle ayant le meilleur score GEO exploitable ;
- la pire page GEO est celle ayant le score GEO le plus faible ;
- si aucune analyse GEO n'existe, la carte indique que les donnees sont indisponibles.

### 9.3 Crawl

Objectif : resumer la couverture technique du dernier crawl exploitable.

Indicateur principal :

- pages crawlees.

Indicateurs secondaires possibles :

- pages en erreur ;
- date du dernier crawl ;
- statut du dernier crawl.

### 9.4 SEO

Objectif : synthese des problemes SEO par criticite.

Indicateurs :

- erreurs critiques ;
- avertissements ;
- informations.

Mapping conceptuel :

| Niveau Dashboard | Severites SEO possibles |
| --- | --- |
| Erreurs critiques | `critical`, `major` selon les conventions retenues. |
| Avertissements | `medium`, `minor`. |
| Informations | signaux faibles ou issues informatives. |

Le mapping exact devra rester coherent avec les severites produites par le moteur SEO.

### 9.5 GEO

Objectif : afficher les principales recommandations GEO.

Contenu attendu :

- titre de la recommandation ;
- type : SEO, GEO ou editorial ;
- severite ;
- priorite ;
- page concernee si disponible ;
- source de la recommandation.

Les recommandations doivent etre triees par priorite, puis severite.

### 9.6 Pages Prioritaires

Objectif : identifier les pages necessitant une action rapide.

Critere de priorisation cible :

```text
Priorite page =
    score SEO faible
    + score GEO faible
    + nombre d'issues critiques
    + recommandations GEO prioritaires
```

La formule exacte sera definie lors de l'implementation. Elle devra rester transparente et testable.

Informations affichees :

- URL ;
- score SEO ;
- score GEO ;
- nombre d'issues critiques ;
- nombre de recommandations prioritaires ;
- action recommandee.

### 9.7 Comparaison SEO / GEO

Objectif : visualiser les ecarts entre sante SEO technique et sante GEO.

Cas utiles :

- page forte en SEO mais faible en GEO ;
- page faible en SEO mais correcte en GEO ;
- page faible sur les deux axes ;
- page forte sur les deux axes.

Representation cible :

```text
Page
    |-- Score SEO
    |-- Score GEO
    |-- Ecart
    |-- Interpretation
```

L'ecart SEO / GEO doit aider a prioriser les actions editoriales ou techniques.

## 10. Graphiques Initiaux

Le Sprint 23 documente uniquement deux graphiques initiaux.

### 10.1 Repartition Des Scores SEO

Objectif : comprendre la distribution des scores SEO.

Groupes proposes :

| Groupe | Plage |
| --- | --- |
| Faible | 0-49 |
| Moyen | 50-74 |
| Bon | 75-89 |
| Excellent | 90-100 |

Donnees attendues :

- nombre de pages par groupe ;
- score minimum ;
- score maximum ;
- score moyen.

### 10.2 Repartition Des Scores GEO

Objectif : comprendre la distribution des scores GEO.

Groupes proposes :

| Groupe | Plage |
| --- | --- |
| Faible | 0-49 |
| Moyen | 50-74 |
| Bon | 75-89 |
| Excellent | 90-100 |

Donnees attendues :

- nombre de pages par groupe ;
- score minimum ;
- score maximum ;
- score moyen.

### 10.3 Graphiques Historiques

Les graphiques historiques ne sont pas inclus dans le Sprint 23.

Ils devront etre prepares conceptuellement pour les sprints futurs :

- evolution des scores SEO ;
- evolution des scores GEO ;
- tendances par site ;
- comparaison avant / apres corrections ;
- evolution des donnees GSC et GA4.

Le Dashboard doit etre concu pour accueillir ces evolutions sans refonte.

## 11. Endpoints REST Prevus

Endpoint principal de la V1 :

```text
GET /api/v1/dashboard/overview
```

Role :

- retourner une synthese globale du Dashboard ;
- inclure les cartes principales ;
- inclure les deux distributions de scores ;
- inclure les pages prioritaires ;
- inclure les principales recommandations GEO.

Parametres possibles :

| Parametre | Role |
| --- | --- |
| `website_id` | Filtrer le Dashboard sur un site. |
| `crawl_id` | Cibler une session de crawl precise. |
| `seo_analysis_id` | Cibler une analyse SEO precise. |
| `geo_analysis_id` | Cibler une analyse GEO precise. |

Reponse conceptuelle :

```text
DashboardOverview
    |
    +-- seo_health
    +-- geo_health
    +-- crawl_summary
    +-- seo_issue_summary
    +-- geo_recommendation_summary
    +-- priority_pages
    +-- seo_geo_comparison
    +-- seo_score_distribution
    +-- geo_score_distribution
```

Endpoints futurs possibles, non inclus dans la V1 :

```text
GET /api/v1/dashboard/history
GET /api/v1/dashboard/trends
GET /api/v1/dashboard/websites/{website_id}
GET /api/v1/dashboard/websites/{website_id}/overview
GET /api/v1/dashboard/websites/{website_id}/history
GET /api/v1/dashboard/websites/{website_id}/trends
```

Ces endpoints doivent etre documentes comme evolutions possibles. Ils ne doivent pas etre implementes dans le cadre du
present document.

## 12. Modele Conceptuel De Reponse

Cette section decrit une structure conceptuelle. Elle ne definit pas de schema Pydantic effectif.

```text
DashboardOverview
    seo_health
        average_score
        best_page
        worst_page
        analyzed_pages_count

    geo_health
        average_score
        best_page
        worst_page

    crawl
        crawled_pages_count
        failed_pages_count
        latest_crawl_status
        latest_crawl_date

    seo
        critical_errors_count
        warnings_count
        information_count

    geo
        top_recommendations

    priority_pages
        url
        seo_score
        geo_score
        priority_reason

    comparison
        seo_score
        geo_score
        gap

    charts
        seo_score_distribution
        geo_score_distribution
```

## 13. Desktop

Le Desktop doit rester un client graphique.

Architecture attendue :

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
REST API
```

Responsabilites de `DashboardPage` :

- afficher les cartes ;
- afficher les graphiques ;
- afficher les pages prioritaires ;
- afficher les recommandations principales ;
- gerer les etats de chargement ;
- gerer les erreurs lisibles ;
- permettre un rafraichissement manuel.

Responsabilites du service Desktop :

- appeler `GET /api/v1/dashboard/overview` ;
- normaliser les erreurs API ;
- fournir une structure exploitable par la page ;
- ne jamais acceder a PostgreSQL.

Le Desktop ne doit pas :

- lancer un crawl ;
- lancer une analyse SEO ;
- lancer une analyse GEO ;
- recalculer les scores metier ;
- acceder aux models SQLAlchemy ;
- contourner l'API REST.

## 14. Etats De Restitution

Le Dashboard doit gerer les etats suivants :

| Etat | Comportement attendu |
| --- | --- |
| Donnees disponibles | Afficher les cartes, graphiques et listes. |
| Aucune analyse SEO | Afficher les cartes SEO comme indisponibles. |
| Aucune analyse GEO | Afficher les cartes GEO comme indisponibles. |
| Aucun crawl | Afficher un message indiquant qu'aucune base de donnees n'est disponible. |
| Erreur API | Afficher une erreur lisible et proposer de rafraichir. |
| Chargement | Afficher un etat de chargement sobre. |

Une absence de donnee ne doit pas etre traitee comme une erreur technique.

## 15. Benefices Attendus

Le Dashboard doit apporter :

- une lecture rapide de la performance globale ;
- une priorisation des pages a corriger ;
- une meilleure articulation entre SEO technique et GEO ;
- un point d'entree unique pour les equipes marketing ;
- une base evolutive pour les donnees Search Console et Analytics ;
- une future base pour les rapports.

Le Dashboard reduit le temps necessaire pour comprendre ou agir apres un crawl, une analyse SEO et une analyse GEO.

## 16. Preparation Sprint 24 - Google Search Console

Le Sprint 24 ajoutera les donnees Google Search Console.

Donnees futures :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- couverture ;
- indexation.

Integration cible :

```text
DashboardService
    |
    +-- Repositories Crawl / SEO / GEO
    +-- Futur SearchConsoleRepository
```

Le Dashboard doit pouvoir integrer ces donnees sans modifier son architecture generale.

Cartes futures possibles :

- performance organique ;
- pages avec impressions mais faible CTR ;
- pages indexables sans impressions ;
- pages avec bonnes impressions mais mauvais score SEO ;
- pages avec bon score GEO mais faible visibilite Google.

Les donnees GSC enrichiront le Dashboard. Elles ne remplaceront pas les donnees crawl, SEO ou GEO.

## 17. Preparation Sprint 25 - Google Analytics 4

Le Sprint 25 ajoutera les donnees Google Analytics 4.

Donnees futures :

- sessions ;
- utilisateurs ;
- conversions ;
- engagement ;
- trafic organique.

Integration cible :

```text
DashboardService
    |
    +-- Repositories Crawl / SEO / GEO
    +-- Futur SearchConsoleRepository
    +-- Futur AnalyticsRepository
```

Le Dashboard devra pouvoir croiser :

- score SEO et trafic organique ;
- score GEO et engagement ;
- recommandations prioritaires et conversions ;
- pages crawlees et pages reellement visitees.

Les donnees GA4 enrichiront la priorisation. Elles ne doivent pas transformer le Dashboard en moteur d'analyse autonome.

## 18. Preparation Sprint 26 - Rapports

Le Sprint 26 exploitera les donnees du Dashboard pour produire des rapports.

Le Dashboard doit donc fournir des structures de synthese :

- stables ;
- lisibles ;
- reutilisables ;
- exportables ;
- rattachees aux analyses sources.

Les rapports pourront reutiliser :

- les scores moyens ;
- les pages prioritaires ;
- les distributions ;
- les recommandations principales ;
- les comparaisons SEO / GEO.

Le Dashboard ne genere pas lui-meme les rapports pendant le Sprint 23.

## 19. Performance Et Robustesse

Le Dashboard doit rester rapide.

Principes :

- limiter les requetes inutiles ;
- utiliser des aggregations simples ;
- paginer les listes longues si necessaire ;
- ne pas charger le HTML brut ;
- ne pas charger les reponses providers completes si elles ne sont pas utiles a la synthese ;
- limiter les pages prioritaires a un nombre raisonnable ;
- prevoir des valeurs par defaut lorsque certaines donnees sont absentes.

Le Dashboard doit eviter de devenir une requete massive regroupant toute la base.

## 20. Securite Et Permissions

Le Dashboard doit respecter les permissions applicatives existantes.

Principes :

- acces authentifie ;
- permission de lecture adaptee ;
- aucun secret affiche ;
- aucune cle API exposee ;
- aucun contenu brut sensible affiche par defaut ;
- aucun acces direct Desktop a la base.

Les donnees affichees doivent rester coherentes avec les droits de l'utilisateur.

## 21. Risques

| Risque | Impact | Mitigation |
| --- | --- | --- |
| Dashboard trop charge | Interface difficile a lire | Limiter la V1 aux cartes et deux graphiques. |
| Confusion restitution / analyse | Architecture brouillee | Interdire toute execution metier depuis le Dashboard. |
| Requetes trop couteuses | Temps de chargement eleve | Aggregations ciblees et listes limitees. |
| Donnees manquantes | Cartes vides ou erreurs | Etats indisponibles clairement geres. |
| Couplage aux futurs connecteurs | Refactorisation | Ajouter GSC et GA4 comme sources supplementaires du service. |
| Priorisation opaque | Perte de confiance | Documenter la formule et les criteres utilises. |

## 22. Criteres De Validation

La specification Sprint 23 est valide si elle permet une implementation future respectant les criteres suivants :

- le Dashboard ne lance aucun crawl ;
- le Dashboard ne lance aucune analyse SEO ;
- le Dashboard ne lance aucune analyse GEO ;
- le Dashboard ne fait aucune requete HTTP vers les sites analyses ;
- le Desktop passe exclusivement par `ApiClient` ;
- les routes FastAPI restent fines ;
- les aggregations sont portees par `DashboardService` ;
- les repositories existants sont reutilises ;
- les cartes Sante SEO, Sante GEO, Crawl, SEO, GEO, Pages prioritaires et Comparaison SEO / GEO sont couvertes ;
- seuls deux graphiques initiaux sont prevus : repartition SEO et repartition GEO ;
- les donnees futures GSC et GA4 peuvent etre ajoutees sans refonte ;
- les rapports du Sprint 26 peuvent reutiliser les syntheses produites.

## 23. Conclusion

Le Sprint 23 prepare le Dashboard SEO / GEO comme une couche de restitution unifiee.

Il s'appuie sur les fondations deja livrees : crawl, analyse SEO et analyse GEO. Il ne remplace aucune de ces couches et
ne lance aucun traitement. Sa valeur principale est de transformer des resultats deja presents en une vision claire,
priorisee et actionnable.

Cette specification doit servir de reference avant toute implementation. Le developpement futur devra rester limite a la
restitution, respecter l'architecture `Routes -> DashboardService -> Repositories` cote backend, et respecter
l'architecture `DashboardPage -> DashboardService -> ApiClient -> REST API` cote Desktop.

## 24. Implementation Sprint 23

L'implementation V1 du Sprint 23 respecte l'architecture de restitution prevue.

Backend :

```text
backend/app/api/v1/routes/dashboard.py
    -> backend/app/services/dashboard.py
        -> CrawlRepository
        -> SeoAnalysisRepository
        -> GeoAnalysisRepository
```

Endpoint implemente :

```text
GET /api/v1/dashboard/overview
```

Le service agrege uniquement des donnees deja persistees. Il ne lance aucun crawl, aucune analyse SEO, aucune analyse GEO
et aucun appel provider.

Desktop :

```text
desktop/ui/dashboard_page.py
    -> desktop/services/dashboard_service.py
        -> ApiClient
            -> REST API
```

La page Desktop affiche :

- les cartes SEO et GEO ;
- le nombre de pages crawlees ;
- les distributions SEO et GEO ;
- les pages prioritaires ;
- la comparaison SEO / GEO ;
- les principaux problemes SEO ;
- les principales recommandations GEO.

Les structures de reponse incluent des emplacements dedies aux futures sources Google Search Console, Google Analytics 4
et rapports, sans implementer ces fonctionnalites dans le Sprint 23.
