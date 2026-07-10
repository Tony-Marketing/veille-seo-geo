# Sprint 35 - Dashboard V2

## 1. Contexte

Le Sprint 35 definit la specification fonctionnelle et technique du Dashboard V2 de la plateforme interne Veille
SEO-GEO Groupe A.P&Partner.

Les sprints precedents ont deja livre ou documente les modules necessaires a une synthese transverse :

- sites web, entites, mots-cles, URLs, concurrents et taches projet ;
- crawls et pages crawlees ;
- analyses SEO deterministes ;
- analyses GEO et recommandations associees ;
- Google Search Console ;
- Google Analytics 4 ;
- Bing Webmaster Tools ;
- planifications de synchronisation ;
- monitoring ;
- alertes ;
- orchestrateur de traitements, jobs, logs et workers.

Le Sprint 23 a introduit un premier Dashboard SEO/GEO. Cette V1 expose `GET /api/v1/dashboard/overview` et agrege les
donnees de crawl, SEO et GEO deja persistees. Le Sprint 35 doit etendre cette logique pour fournir une vue executive
multi-sites, plus operationnelle, couvrant les sources deja disponibles dans le depot.

Le Dashboard V2 reste une couche de synthese et d'agregation. Il ne lance aucun traitement, ne contacte aucun connecteur
externe et ne persiste aucun KPI.

## 2. Etat de l'existant

### Backend Dashboard existant

Le backend Dashboard V1 existe dans :

- `backend/app/api/v1/routes/dashboard.py` ;
- `backend/app/services/dashboard.py` ;
- `backend/app/schemas/dashboard.py`.

Endpoint actuel :

```text
GET /api/v1/dashboard/overview
```

Parametres actuels :

- `website_id` ;
- `crawl_id` ;
- `seo_analysis_id` ;
- `geo_analysis_id`.

Permission actuelle :

- `require_permission("crawl.read")`.

Le service actuel utilise :

- `CrawlRepository` ;
- `SeoAnalysisRepository` ;
- `GeoAnalysisRepository`.

Il calcule deja :

- resume de crawl ;
- score SEO moyen depuis les pages SEO analysees ;
- meilleure et pire page SEO ;
- compteurs d'issues SEO par severite ;
- score GEO moyen depuis les resultats providers ou `GeoAnalysis.geo_score` ;
- meilleures et pires pages GEO ;
- recommandations GEO principales ;
- pages prioritaires ;
- comparaison SEO/GEO ;
- distributions de scores SEO et GEO.

Il ne couvre pas encore :

- vue multi-sites ;
- tendances temporelles ;
- GSC ;
- GA4 ;
- Bing ;
- monitoring ;
- alertes ;
- etat des jobs et workers ;
- recommandations deterministes transverses.

### Page Dashboard Desktop existante

Le Desktop actuel contient :

- `desktop/ui/dashboard_page.py` ;
- `desktop/services/dashboard_service.py` ;
- `desktop/core/api_client.py`.

La page utilise PySide6 avec :

- `QLabel` ;
- `QPushButton` ;
- `QGroupBox` ;
- `QGridLayout` ;
- `QTableWidget` ;
- `QTableWidgetItem` ;
- `QProgressBar`.

Les graphiques actuels sont representes par des tableaux et des barres de progression. Aucune dependance de graphique
dediee comme QtCharts, matplotlib ou plotly n'est presente dans `requirements.txt`.

Le flux Desktop actuel est conforme :

```text
DashboardPage
  -> DashboardService Desktop
      -> ApiClient
          -> API REST
```

### Tests Dashboard actuels

Les tests existants couvrent :

- `tests/services/test_dashboard_service.py` ;
- `tests/api/test_dashboard_routes.py` ;
- `tests/desktop/test_dashboard_service.py` ;
- `tests/desktop/test_main_window_lazy_loading.py`.

Ils valident :

- payload vide stable sans donnees ;
- agregation crawl, SEO et GEO ;
- protection JWT de la route ;
- permission `crawl.read` ;
- mapping des erreurs HTTP dans le service Desktop ;
- lazy loading des pages Desktop.

Il n'existe pas encore de tests Dashboard V2.

## 3. Objectifs

Le Sprint 35 doit specifier le Dashboard V2 comme point d'entree executif de la plateforme.

Objectifs :

- consolider les donnees multi-sites ;
- afficher une synthese SEO, GEO, GSC, GA4 et Bing ;
- afficher la sante globale des sites suivis ;
- afficher les signaux de monitoring, alertes et orchestration ;
- fournir des tendances simples sur periode courante et periode precedente ;
- produire des recommandations deterministes issues uniquement des donnees persistees ;
- permettre une navigation rapide vers les modules sources ;
- respecter les permissions existantes ;
- preparer une implementation future sans migration ni nouvelle table.

## 4. Perimetre

Le Sprint 35 couvre uniquement la specification du Dashboard V2.

Perimetre fonctionnel cible :

- vue executive multi-sites ;
- overview global ;
- tendances ;
- liste synthetique des sites ;
- recommandations deterministes ;
- filtres globaux ;
- scoring documente ;
- etats de chargement, vide, erreur et donnees partielles ;
- navigation vers les modules existants.

Perimetre technique cible :

- nouveaux schemas Pydantic v2 ;
- nouveau repository d'agregation ;
- nouveau service backend ;
- nouvelles routes REST ;
- nouveau service Desktop ;
- evolution de la page Desktop Dashboard ;
- tests repository, service, API et Desktop lors de l'implementation future.

## 5. Hors perimetre

Sont explicitement hors perimetre du Sprint 35 :

- implementation backend dans le cadre du present document ;
- implementation Desktop dans le cadre du present document ;
- migration Alembic ;
- nouvelle table ;
- nouveau modele SQLAlchemy ;
- persistance des KPI ;
- persistance des recommandations ;
- cache persistant ;
- generation LLM ;
- appel a un provider IA ;
- appel direct aux APIs externes ;
- lancement de crawl ;
- lancement d'analyse SEO ;
- lancement d'analyse GEO ;
- lancement d'import GSC, GA4 ou Bing ;
- execution ou relance de job ;
- nouvelle dependance ;
- refonte de l'architecture ;
- suppression, renommage ou deplacement de fichiers ;
- commit, push ou Pull Request.

## 6. Decisions d'architecture

Decision retenue :

```text
Dashboard V2 = module de synthese et d'agregation a la demande.
```

Architecture backend obligatoire :

```text
Routes
  -> Services
      -> Repositories
          -> Models
```

Architecture Desktop obligatoire :

```text
Page
  -> Service Desktop
      -> ApiClient
          -> API REST
```

Decisions :

- aucune nouvelle table ;
- aucune migration Alembic ;
- aucun stockage de KPI ;
- aucun stockage de recommandation Dashboard ;
- calcul a la demande par le service backend ;
- agregations SQLAlchemy dans un repository dedie ;
- regles de scoring et de recommandation dans le service ;
- routes fines, sans logique metier ;
- ApiClient Desktop comme seul point HTTP ;
- chargement progressif cote Desktop ;
- pas de cache persistant ;
- pas de generation LLM.

Le Dashboard V2 ne remplace pas les modules sources. Il les lit et les resume.

## 7. Donnees sources reellement disponibles

Les donnees suivantes existent dans le depot et peuvent alimenter le Dashboard V2.

### Sites

Source :

- `Website`.

Champs disponibles :

- `id` ;
- `entity_id` ;
- `name` ;
- `url` ;
- `cms` ;
- `is_active` ;
- `created_at` ;
- `updated_at`.

### Crawls

Sources :

- `CrawlSession` ;
- `CrawlPage`.

Champs disponibles :

- statut de session ;
- pages trouvees ;
- pages crawlees ;
- pages en echec ;
- URLs en attente ;
- profondeur maximale ;
- demande d'annulation ;
- message d'erreur ;
- dates de debut, fin et progression ;
- code HTTP par page ;
- temps de reponse ;
- message d'erreur par page ;
- profondeur ;
- redirections.

### SEO

Sources :

- `SeoAnalysis` ;
- `SeoPageAnalysis` ;
- `SeoAnalysisIssue`.

Champs disponibles :

- statut ;
- progression ;
- score global ;
- pages totales ;
- pages analysees ;
- issues totales ;
- message d'erreur ;
- dates de debut et completion ;
- score page ;
- nombre d'issues page ;
- famille, critere, severite, code et message des issues.

### GEO

Sources :

- `GeoAnalysis` ;
- `GeoProviderResult` ;
- `GeoRecommendation`.

Champs disponibles :

- statut ;
- progression ;
- `geo_score` ;
- `llm_score` ;
- `global_score` ;
- providers demandes ;
- pages totales ;
- pages analysees ;
- nombre de resultats providers ;
- nombre de recommandations ;
- resume ;
- message d'erreur ;
- date de debut et completion ;
- provider, modele, statut, reponse normalisee et duree ;
- recommandations par type, severite, priorite, titre, description, source et impact.

### Google Search Console

Sources :

- `GoogleSearchConsoleProperty` ;
- `GoogleSearchConsolePerformance` ;
- `GoogleSearchConsoleIndexCoverage` ;
- `GoogleSearchConsoleSitemap` ;
- `GoogleSearchConsoleImport`.

Champs disponibles :

- site rattache ;
- propriete ;
- type de propriete ;
- niveau de permission ;
- actif ;
- expiration de token ;
- clics ;
- impressions ;
- CTR ;
- position ;
- page ;
- query ;
- pays ;
- device ;
- type de recherche ;
- etats d'indexation ;
- sitemaps, warnings et erreurs ;
- imports, statuts, periode, dimensions, lignes demandees et importees.

### Google Analytics 4

Sources :

- `GoogleAnalyticsProperty` ;
- `GoogleAnalyticsMetric` ;
- `GoogleAnalyticsDimension` ;
- `GoogleAnalyticsImport`.

Champs disponibles :

- site rattache ;
- propriete ;
- nom de propriete ;
- compte ;
- measurement id ;
- statut active ;
- utilisateurs ;
- nouveaux utilisateurs ;
- sessions ;
- sessions engagees ;
- vues de pages ;
- duree moyenne de session ;
- taux d'engagement ;
- conversions ;
- revenu total ;
- source, medium, campagne, device et pays ;
- imports, statuts, lignes importees et erreurs.

### Bing Webmaster Tools

Sources :

- `BingWebmasterConnection` ;
- `BingWebmasterSite` ;
- `BingWebmasterMetric` ;
- `BingWebmasterCrawlStat` ;
- `BingWebmasterSitemap` ;
- `BingWebmasterImportRun`.

Champs disponibles :

- site rattache ;
- connexion active ;
- derniere synchronisation ;
- derniere erreur ;
- site Bing verifie ;
- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- query ;
- page ;
- pays ;
- device ;
- stats crawl, statut HTTP, type d'issue, categorie et severite ;
- sitemaps, nombre d'URLs, erreurs et warnings ;
- imports et statuts.

### Monitoring

Source :

- `MonitoringEvent`.

Champs disponibles :

- type d'evenement ;
- severite ;
- source ;
- message ;
- details controles ;
- date de creation.

### Alertes

Source :

- `Alert`.

Champs disponibles :

- source ;
- categorie ;
- severite ;
- statut ;
- titre ;
- message ;
- metadata controlee ;
- cle de deduplication ;
- premiere observation ;
- derniere observation ;
- acquittement ;
- resolution.

### Orchestration

Sources :

- `ProcessingJob` ;
- `ProcessingJobLog` ;
- `ProcessingWorker`.

Champs disponibles :

- type de job ;
- statut ;
- priorite ;
- payload controle ;
- cle d'idempotence ;
- tentatives ;
- dates de disponibilite, reservation, debut, fin et echec ;
- message ;
- details controles ;
- worker ;
- expiration de verrou ;
- evenement monitoring associe ;
- logs ;
- statut et heartbeat des workers.

## 8. KPI SEO disponibles

KPI SEO retenus car les donnees sources existent :

- nombre d'analyses SEO ;
- nombre d'analyses SEO par statut ;
- score SEO moyen par page analysee ;
- score SEO global moyen depuis `SeoAnalysis.global_score` lorsque disponible ;
- nombre de pages SEO analysees ;
- taux de couverture SEO : `pages_analyzed / pages_total` si `pages_total > 0` ;
- nombre total d'issues ;
- issues par severite ;
- issues critiques selon le mapping existant `critical` et `major` ;
- warnings selon le mapping existant `medium`, `minor`, `warning` ;
- top issues par code, famille, message et occurrences ;
- pages SEO les plus faibles ;
- derniere analyse SEO complete ou partielle ;
- analyses SEO en erreur.

KPI SEO non retenus :

- Core Web Vitals reels, car aucun modele dedie n'existe ;
- positionnement SEO, car les positions organiques viennent de GSC/Bing et non du module SEO ;
- score de maillage interne avance, car aucune table dediee n'existe.

## 9. KPI GEO disponibles

KPI GEO retenus :

- nombre d'analyses GEO ;
- nombre d'analyses GEO par statut ;
- `geo_score` moyen ;
- `llm_score` moyen ;
- `global_score` moyen ;
- nombre de providers demandes ;
- nombre de resultats providers ;
- taux de resultats providers en erreur ;
- nombre de pages GEO analysees ;
- taux de couverture GEO : `pages_analyzed / pages_total` si `pages_total > 0` ;
- recommandations par severite ;
- recommandations par priorite ;
- recommandations par type ;
- recommandations a fort impact lorsque `impact_score` est renseigne ;
- score GEO par page depuis `normalized_response.geo_score` ou `geo_signals` lorsque presents ;
- meilleures et pires pages GEO ;
- analyses GEO en erreur ou partielles.

KPI GEO non retenus :

- part de voix IA externe ;
- citations par marque dans les moteurs IA ;
- comparaison temps reel entre ChatGPT, Gemini, Claude, Perplexity et Mistral ;
- couts LLM ;
- hallucination score.

Ces donnees ne sont pas suffisamment normalisees dans les modeles existants pour devenir des KPI Dashboard V2.

## 10. KPI GSC, GA4 et Bing disponibles

### Google Search Console

KPI retenus :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- pages et requetes depuis les dimensions persistees ;
- performance par pays ;
- performance par device ;
- performance par type de recherche ;
- nombre de proprietes ;
- proprietes actives ;
- dernier import complete ou partiel ;
- imports en erreur ;
- pages valides, exclues, en warning et en erreur via les etats d'indexation existants ;
- sitemaps en erreur ou warning.

### Google Analytics 4

KPI retenus :

- sessions ;
- utilisateurs ;
- nouveaux utilisateurs ;
- sessions engagees ;
- vues de pages ;
- duree moyenne de session ponderee par sessions ;
- taux d'engagement pondere par sessions ;
- conversions ;
- revenu total ;
- breakdown par source, medium, campagne, device et pays ;
- nombre de proprietes ;
- proprietes actives ;
- imports en erreur.

### Bing Webmaster Tools

KPI retenus :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- pages et requetes ;
- pays ;
- device ;
- stats crawl par statut HTTP ;
- stats crawl par type d'issue ;
- stats crawl par severite ;
- sitemaps, erreurs et warnings ;
- connexions actives ;
- sites verifies ;
- imports en erreur ;
- derniere synchronisation ou derniere importation.

## 11. Sante globale des sites

La sante globale d'un site doit etre un score deterministe calcule a la demande.

Score global :

```text
site_health_score =
    0.35 * seo_health
  + 0.20 * geo_health
  + 0.15 * search_visibility_health
  + 0.10 * traffic_health
  + 0.10 * technical_health
  + 0.10 * operations_health
```

Regle de donnees manquantes :

- si une composante n'a aucune donnee source, elle est marquee `unavailable` ;
- les composantes indisponibles ne doivent pas etre considerees comme mauvaises ;
- le score global doit etre calcule sur les poids disponibles, renormalises a 100 ;
- la reponse doit exposer `available_components` et `missing_components`.

Bandes de sante :

- `critical` : 0 a 49 ;
- `warning` : 50 a 69 ;
- `good` : 70 a 84 ;
- `excellent` : 85 a 100.

## 12. Regles precises de scoring

### SEO health

Calcul :

```text
seo_health = moyenne des scores SeoPageAnalysis.score disponibles
```

Penalites :

- `-3` par issue `critical` ;
- `-2` par issue `major` ;
- `-1` par issue `warning`, `medium` ou `minor` ;
- penalite plafonnee a `30`.

Score final :

```text
seo_health = clamp(average_page_score - penalty, 0, 100)
```

Si aucun score page n'existe, utiliser `SeoAnalysis.global_score` du dernier SEO exploitable. Si aucun score n'existe,
composante indisponible.

### GEO health

Calcul prioritaire :

```text
geo_health = moyenne des scores GEO par page
```

Sources des scores par page :

- `GeoProviderResult.normalized_response["geo_score"]` si present ;
- moyenne des valeurs numeriques de `normalized_response["geo_signals"]` si present ;
- sinon `GeoAnalysis.geo_score`.

Penalites :

- `-3` par recommandation priorite `1` ;
- `-2` par recommandation priorite `2` ;
- `-1` par recommandation priorite `3` ;
- penalite plafonnee a `25`.

### Search visibility health

Sources :

- GSC ;
- Bing.

Calcul :

- taux CTR GSC moyen pondere par impressions ;
- taux CTR Bing moyen pondere par impressions ;
- position moyenne GSC ;
- position moyenne Bing.

Regles :

- CTR >= 5 % : 100 ;
- CTR 2 % a 5 % : interpolation lineaire 60 a 100 ;
- CTR < 2 % : 40 ;
- position <= 10 : bonus 10 plafonne a 100 ;
- position > 30 : penalite 15 ;
- si GSC et Bing existent, moyenne ponderee par impressions ;
- si une seule source existe, utiliser cette source.

### Traffic health

Source :

- GA4.

Calcul :

- sessions courantes comparees a la periode precedente ;
- engagement rate courant ;
- conversions courantes si des conversions existent.

Regles :

- base 70 ;
- evolution sessions positive : +10 ;
- evolution sessions inferieure a -20 % : -15 ;
- engagement rate >= 0.6 : +10 ;
- engagement rate < 0.3 : -10 ;
- conversions > 0 : +10 ;
- score borne entre 0 et 100.

Si aucune ligne GA4 n'existe, composante indisponible.

### Technical health

Sources :

- Crawl ;
- GSC index coverage ;
- Bing crawl stats ;
- sitemaps GSC et Bing.

Regles :

- base 100 ;
- pages crawl en echec : penalite proportionnelle jusqu'a 25 ;
- pages HTTP >= 400 : penalite proportionnelle jusqu'a 20 ;
- index coverage en erreur : `-3` par URL, plafonne a 20 ;
- Bing crawl stats de severite critique ou erreur : `-2` par ligne, plafonne a 20 ;
- sitemaps avec erreurs : `-2` par sitemap, plafonne a 10.

### Operations health

Sources :

- Alertes ;
- Monitoring ;
- ProcessingJob ;
- ProcessingWorker.

Regles :

- base 100 ;
- alerte critique active : `-10` par alerte, plafonne a 40 ;
- alerte warning active : `-4` par alerte, plafonne a 20 ;
- evenement monitoring critical ou error sur la periode : `-5` par evenement, plafonne a 25 ;
- job failed sur la periode : `-3` par job, plafonne a 20 ;
- job bloque : `-10` par job, plafonne a 30 ;
- aucun worker actif alors que des jobs pending existent : `-20`.

## 13. Traitements et orchestration

Le Dashboard V2 ne declenche aucun traitement.

Il lit l'etat produit par :

- les imports GSC ;
- les imports GA4 ;
- les imports Bing ;
- les crawls ;
- les analyses SEO ;
- les analyses GEO ;
- les jobs d'orchestration ;
- le monitoring ;
- les alertes.

Il doit exposer les traitements sous forme de synthese :

- jobs pending ;
- jobs reserved ;
- jobs running ;
- jobs retry_scheduled ;
- jobs succeeded ;
- jobs failed ;
- jobs cancelled ;
- jobs bloques ;
- derniere activite ;
- prochain job ou prochaine synchronisation lorsque disponible via les planifications.

Le Dashboard V2 ne doit pas proposer d'action de relance. Les actions restent dans le module Orchestrateur.

## 14. Etat des workers

Le Sprint 34 a introduit `ProcessingWorker`.

Indicateurs workers disponibles :

- nombre de workers connus ;
- workers actifs ;
- workers stopped ;
- dernier heartbeat ;
- job courant ;
- version ;
- metadata controlee.

Regles Dashboard :

- un worker dont `status != "STOPPED"` peut etre affiche comme actif ;
- un worker sans heartbeat recent doit etre affiche comme a surveiller si une regle de fraicheur est definie par le
  service ;
- si aucun worker n'existe et qu'aucun job n'est pending/running, l'etat est `not_configured` ;
- si aucun worker n'existe et que des jobs sont pending/running, l'etat est `attention`.

## 15. Monitoring

Le Dashboard V2 doit reutiliser `MonitoringEvent`.

KPI monitoring :

- nombre total d'evenements ;
- evenements sur la periode courante ;
- evenements `warning` ;
- evenements `error` ;
- evenements `critical` ;
- dernier evenement ;
- repartition par source ;
- repartition par type d'evenement.

Le Dashboard V2 ne doit pas produire de nouvel evenement monitoring pendant une consultation.

## 16. Alertes

Le Dashboard V2 doit reutiliser `Alert`.

KPI alertes :

- total ;
- active ;
- acknowledged ;
- resolved ;
- info ;
- warning ;
- critical ;
- derniere alerte ;
- top alertes actives par severite et `last_seen_at`.

Regle :

- seules les alertes `Active` et `Acknowledged` doivent peser dans `operations_health` ;
- les alertes `Resolved` restent consultables dans les tendances mais ne degradent pas le score courant.

## 17. Graphiques et tendances

Aucune dependance de graphique dediee n'existe dans le Desktop actuel.

Approche retenue :

- le backend renvoie des series temporelles simples ;
- le Desktop V2 peut les afficher avec composants PySide6 existants ;
- les tendances peuvent etre rendues en tableaux, barres de progression ou mini-series textuelles ;
- aucune nouvelle dependance graphique dans ce sprint.

Series minimales :

- SEO score moyen par jour, semaine ou mois ;
- GEO score moyen par jour, semaine ou mois ;
- clics GSC ;
- impressions GSC ;
- sessions GA4 ;
- utilisateurs GA4 ;
- clics Bing ;
- impressions Bing ;
- alertes actives ;
- jobs failed ou blocked.

Granularites autorisees :

- `day` ;
- `week` ;
- `month`.

Whitelist de metriques de tendances :

- `seo_score` ;
- `geo_score` ;
- `gsc_clicks` ;
- `gsc_impressions` ;
- `ga4_sessions` ;
- `ga4_users` ;
- `bing_clicks` ;
- `bing_impressions` ;
- `alerts_active` ;
- `jobs_failed` ;
- `jobs_blocked`.

## 18. Recommandations deterministes

Les recommandations Dashboard V2 doivent etre deterministes et non persistees.

Sources :

- issues SEO ;
- recommandations GEO ;
- GSC CTR et position ;
- GA4 sessions, engagement et conversions ;
- Bing crawl stats ;
- alertes ;
- jobs ;
- workers.

Regles de recommandations :

- SEO critique : issue `critical` ou `major` recurrente ;
- GEO prioritaire : recommandation GEO `priority <= 2` ;
- GSC CTR faible : impressions > 0 et CTR inferieur a un seuil documente ;
- position faible : position GSC ou Bing > 30 ;
- trafic en baisse : sessions GA4 en baisse de plus de 20 % vs periode precedente ;
- engagement faible : engagement rate GA4 < 0.3 ;
- indexation en erreur : index coverage GSC en erreur ;
- crawl technique : pages crawl en erreur ou Bing crawl stats en erreur ;
- operations : alertes critiques actives, jobs bloques ou failed.

Chaque recommandation doit contenir :

- type ;
- severite ;
- priorite ;
- titre ;
- message ;
- source ;
- `website_id` si disponible ;
- identifiant de ressource source si disponible ;
- lien de navigation Desktop cible.

## 19. Vue executive multi-sites

La vue multi-sites doit lister les sites suivis avec leurs indicateurs de synthese.

Champs attendus par site :

- `website_id` ;
- nom ;
- URL ;
- actif ;
- score global ;
- bande de sante ;
- score SEO ;
- score GEO ;
- clics GSC ;
- impressions GSC ;
- sessions GA4 ;
- clics Bing ;
- impressions Bing ;
- alertes actives ;
- jobs en erreur ou bloques ;
- derniere activite connue ;
- sources disponibles ;
- sources manquantes.

Tri par defaut :

- sites avec score critique ;
- puis alertes critiques ;
- puis derniere activite recente ;
- puis nom.

Pagination obligatoire :

- `page` ;
- `page_size` limite a 100.

## 20. Filtres globaux

Filtres globaux prevus :

- `website_id` ;
- `entity_id` ;
- `is_active` ;
- `date_from` ;
- `date_to` ;
- `period` ;
- `compare_to_previous` ;
- `source` ;
- `health_status` ;
- `search` ;
- `page` ;
- `page_size` ;
- `sort` ;
- `order`.

Whitelist `source` :

- `seo` ;
- `geo` ;
- `gsc` ;
- `ga4` ;
- `bing` ;
- `crawl` ;
- `monitoring` ;
- `alerts` ;
- `orchestration`.

Whitelist `health_status` :

- `critical` ;
- `warning` ;
- `good` ;
- `excellent` ;
- `unavailable`.

Whitelist `sort` pour la liste des sites :

- `name` ;
- `health_score` ;
- `seo_score` ;
- `geo_score` ;
- `gsc_clicks` ;
- `ga4_sessions` ;
- `bing_clicks` ;
- `active_alerts` ;
- `last_activity_at`.

## 21. Gestion des periodes et periode precedente

Parametres :

- `date_from` ;
- `date_to` ;
- `period` ;
- `compare_to_previous`.

Whitelist `period` :

- `7d` ;
- `30d` ;
- `90d` ;
- `custom`.

Regles :

- si `period=7d`, `30d` ou `90d`, le service calcule `date_from` et `date_to` a partir de la date courante ;
- si `period=custom`, `date_from` et `date_to` sont requis ;
- `date_to` doit etre superieur ou egal a `date_from` ;
- la periode precedente a la meme duree que la periode courante ;
- aucune comparaison n'est calculee si `compare_to_previous=false` ;
- les modules sans date exploitable doivent etre exclus des tendances datees et signales comme partiels.

## 22. Schemas Pydantic prevus

Fichier futur :

- `backend/app/schemas/dashboard_v2.py`.

Schemas prevus :

- `DashboardV2Period` ;
- `DashboardV2Filters` ;
- `DashboardV2MetricDelta` ;
- `DashboardV2SourceAvailability` ;
- `DashboardV2HealthComponent` ;
- `DashboardV2HealthScore` ;
- `DashboardV2SeoKpis` ;
- `DashboardV2GeoKpis` ;
- `DashboardV2GscKpis` ;
- `DashboardV2Ga4Kpis` ;
- `DashboardV2BingKpis` ;
- `DashboardV2OperationsKpis` ;
- `DashboardV2MonitoringKpis` ;
- `DashboardV2AlertKpis` ;
- `DashboardV2WorkerKpis` ;
- `DashboardV2TrendPoint` ;
- `DashboardV2TrendSeries` ;
- `DashboardV2WebsiteSummary` ;
- `DashboardV2WebsiteList` ;
- `DashboardV2Recommendation` ;
- `DashboardV2RecommendationList` ;
- `DashboardV2OverviewResponse` ;
- `DashboardV2TrendsResponse`.

Contraintes :

- Pydantic v2 ;
- `BaseModel` ;
- `Field(default_factory=list)` pour les listes ;
- enums `StrEnum` pour whitelists si necessaire ;
- pas de schema Pydantic ajoute dans le present sprint documentaire.

## 23. Repository prevu

Fichier futur :

- `backend/app/repositories/dashboard_v2.py`.

Role :

- centraliser les lectures SQLAlchemy necessaires au Dashboard V2 ;
- appliquer les filtres SQL ;
- appliquer les agregations SQL ;
- appliquer les whitelists de tri ;
- retourner des structures simples au service.

Responsabilites :

- lister les sites eligibles ;
- agreger crawls par site ;
- agreger SEO par site ;
- agreger GEO par site ;
- agreger GSC par site et periode ;
- agreger GA4 par site et periode ;
- agreger Bing par site et periode ;
- agreger monitoring par periode ;
- agreger alertes ;
- agreger jobs ;
- lister workers ;
- fournir les series de tendances.

Interdictions :

- aucune regle de scoring metier dans le repository ;
- aucune recommandation dans le repository ;
- aucun appel externe ;
- aucune persistance de KPI.

## 24. Service prevu

Fichier futur :

- `backend/app/services/dashboard_v2.py`.

Role :

- orchestrer les appels repository ;
- appliquer les regles de scoring ;
- calculer les deltas periode precedente ;
- assembler les reponses ;
- produire les recommandations deterministes ;
- gerer les donnees manquantes ;
- garantir l'absence de secrets.

Le service doit etre la seule couche a connaitre :

- ponderations ;
- bandes de sante ;
- regles de recommandations ;
- choix de fallback ;
- interpretation des donnees partielles.

## 25. Routes REST prevues

Fichier futur :

- `backend/app/api/v1/routes/dashboard_v2.py`.

Prefixe :

```text
/api/v1/dashboard-v2
```

Endpoints retenus :

```text
GET /api/v1/dashboard-v2/overview
GET /api/v1/dashboard-v2/trends
GET /api/v1/dashboard-v2/websites
GET /api/v1/dashboard-v2/recommendations
```

Ces endpoints sont pertinents :

- `overview` alimente la vue executive ;
- `trends` permet un chargement progressif des graphiques ;
- `websites` isole la liste paginee multi-sites ;
- `recommendations` isole les recommandations potentiellement plus couteuses.

## 26. Parametres des endpoints

### GET /api/v1/dashboard-v2/overview

Parametres :

- `website_id: int | None` ;
- `entity_id: int | None` ;
- `is_active: bool | None` ;
- `period: 7d | 30d | 90d | custom` ;
- `date_from: date | None` ;
- `date_to: date | None` ;
- `compare_to_previous: bool = true` ;
- `source: list[str] | None`.

Pagination :

- aucune pagination pour l'overview ;
- les listes incluses doivent etre limitees par le service.

Permission :

- recommandation : `require_permission("crawl.read")`, coherente avec Dashboard V1, SEO, GEO, GSC, GA4 et Bing ;
- evolution possible : permission dediee `dashboard.read`, a creer dans un sprint d'implementation si le modele de droits
  le demande.

Erreurs possibles :

- `401` authentification requise ;
- `403` permission insuffisante ;
- `422` parametre invalide ;
- `500` erreur serveur.

### GET /api/v1/dashboard-v2/trends

Parametres :

- `website_id: int | None` ;
- `entity_id: int | None` ;
- `period` ;
- `date_from` ;
- `date_to` ;
- `granularity: day | week | month` ;
- `metrics: list[str]`.

Whitelists :

- granularites : `day`, `week`, `month` ;
- metriques : celles definies en section 17.

Pagination :

- aucune ;
- limite interne sur le nombre de points selon la granularite.

Permission :

- `crawl.read` ou future `dashboard.read`.

Erreurs :

- `401`, `403`, `422`, `500`.

### GET /api/v1/dashboard-v2/websites

Parametres :

- tous les filtres globaux ;
- `page` ;
- `page_size` ;
- `search` ;
- `sort` ;
- `order`.

Pagination :

- obligatoire ;
- `page_size` entre 1 et 100.

Whitelists :

- sort : section 20 ;
- order : `asc`, `desc`.

Permission :

- `crawl.read` ou future `dashboard.read`.

Erreurs :

- `401`, `403`, `422`, `500`.

### GET /api/v1/dashboard-v2/recommendations

Parametres :

- `website_id` ;
- `entity_id` ;
- `period` ;
- `date_from` ;
- `date_to` ;
- `source` ;
- `severity` ;
- `priority` ;
- `page` ;
- `page_size` ;
- `sort` ;
- `order`.

Whitelists :

- source : section 20 ;
- severity : `info`, `warning`, `critical` ;
- priority : `1`, `2`, `3`, `4`, `5` ;
- sort : `priority`, `severity`, `source`, `created_at`, `website_name`.

Pagination :

- obligatoire.

Permission :

- `crawl.read` ou future `dashboard.read`.

Erreurs :

- `401`, `403`, `422`, `500`.

## 27. Reponses attendues

### DashboardV2OverviewResponse

Contenu attendu :

- `generated_at` ;
- `filters` ;
- `period` ;
- `previous_period` si demande ;
- `sources` ;
- `global_health` ;
- `seo` ;
- `geo` ;
- `gsc` ;
- `ga4` ;
- `bing` ;
- `technical` ;
- `operations` ;
- `monitoring` ;
- `alerts` ;
- `workers` ;
- `top_websites` ;
- `top_recommendations` ;
- `partial_data`.

### DashboardV2TrendsResponse

Contenu attendu :

- `generated_at` ;
- `filters` ;
- `granularity` ;
- `series`.

Chaque serie :

- `metric` ;
- `label` ;
- `source` ;
- `points`.

Chaque point :

- `date` ;
- `value` ;
- `previous_value` optionnel ;
- `delta_percent` optionnel.

### DashboardV2WebsiteList

Reponse paginee :

- `items` ;
- `total` ;
- `page` ;
- `page_size` ;
- `pages` ;
- `filters`.

### DashboardV2RecommendationList

Reponse paginee :

- `items` ;
- `total` ;
- `page` ;
- `page_size` ;
- `pages` ;
- `filters`.

## 28. Authentification et permissions

Tous les endpoints Dashboard V2 doivent etre authentifies.

Choix recommande pour l'implementation initiale :

- utiliser `require_permission("crawl.read")` pour rester coherent avec Dashboard V1 et les modules de lecture SEO/GEO,
  GSC, GA4 et Bing.

Evolution possible :

- introduire `dashboard.read` uniquement si la gestion des permissions est etendue dans un sprint futur.

Le Dashboard V2 ne doit jamais exposer :

- tokens ;
- secrets ;
- cles API ;
- payloads bruts sensibles ;
- prompts ou reponses LLM brutes ;
- HTML brut des pages crawlees.

## 29. Architecture Desktop

Fichiers futurs :

- `desktop/services/dashboard_v2_service.py` ;
- modification de `desktop/ui/dashboard_page.py`.

Flux obligatoire :

```text
DashboardPage
  -> DashboardV2Service
      -> ApiClient
          -> /api/v1/dashboard-v2/*
```

Le Desktop ne doit pas :

- recalculer les scores ;
- recalculer les recommandations ;
- acceder a PostgreSQL ;
- appeler les APIs externes ;
- contourner `ApiClient`.

Le Desktop peut :

- charger `overview` au demarrage de la page ;
- charger `trends` apres l'overview ;
- charger `websites` au changement de pagination ;
- charger `recommendations` apres les cartes principales ;
- afficher des messages pour les donnees partielles.

## 30. Organisation de la page

Organisation cible :

1. En-tete : titre, periode, filtres, bouton rafraichir.
2. Bandeau sante globale : score global, statut, sources manquantes.
3. Cartes KPI : SEO, GEO, GSC, GA4, Bing, technique, operations.
4. Tendance principale : series simples selon metriques selectionnees.
5. Vue multi-sites paginee.
6. Recommandations prioritaires.
7. Monitoring, alertes et workers.
8. Liens de navigation vers modules sources.

Composants PySide6 reutilisables :

- `QGroupBox` pour sections ;
- `QGridLayout` pour cartes ;
- `QTableWidget` pour listes ;
- `QProgressBar` pour repartitions et scores ;
- `QPushButton` pour actions de navigation et rafraichissement ;
- `QLabel` pour etats et messages.

## 31. Etats chargement, vide, erreur et donnees partielles

Etats obligatoires :

- chargement overview ;
- chargement tendances ;
- chargement liste sites ;
- chargement recommandations ;
- aucun site ;
- aucune donnee SEO ;
- aucune donnee GEO ;
- aucune donnee GSC ;
- aucune donnee GA4 ;
- aucune donnee Bing ;
- API indisponible ;
- authentification requise ;
- permission insuffisante ;
- parametres invalides ;
- donnees partielles.

Une absence de donnee source ne doit pas etre traitee comme une erreur technique.

## 32. Navigation vers les autres modules

Le Dashboard V2 doit permettre une navigation vers :

- Websites ;
- Crawls ;
- SEO Analysis ;
- GEO Analysis ;
- Google Search Console ;
- Google Analytics 4 ;
- Bing Webmaster Tools ;
- Monitoring ;
- Alertes ;
- Orchestrateur ;
- Planifications.

La navigation doit transmettre au minimum le contexte logique lorsque l'interface le permet :

- `website_id` ;
- source ;
- periode ;
- statut ;
- severite.

Si le module cible ne supporte pas encore les filtres entrants, le Dashboard affiche un lien simple vers la page.

## 33. Liste exacte des fichiers qui devront etre crees

Lors de l'implementation future du Sprint 35, fichiers a creer :

- `backend/app/api/v1/routes/dashboard_v2.py` ;
- `backend/app/schemas/dashboard_v2.py` ;
- `backend/app/services/dashboard_v2.py` ;
- `backend/app/repositories/dashboard_v2.py` ;
- `desktop/services/dashboard_v2_service.py` ;
- `tests/repositories/test_dashboard_v2_repository.py` ;
- `tests/services/test_dashboard_v2_service.py` ;
- `tests/api/test_dashboard_v2_routes.py` ;
- `tests/desktop/test_dashboard_v2_service.py` ;
- `tests/desktop/test_dashboard_v2_page.py`.

Aucune migration Alembic ne doit etre creee.

## 34. Liste exacte des fichiers qui devront etre modifies

Lors de l'implementation future du Sprint 35, fichiers a modifier :

- `backend/app/api/v1/router.py` pour inclure le routeur Dashboard V2 ;
- `desktop/ui/dashboard_page.py` pour remplacer ou etendre l'affichage Dashboard existant ;
- eventuellement `desktop/ui/main_window.py` uniquement si une nouvelle page Dashboard V2 distincte est retenue ;
- eventuellement `desktop/core/constants.py` uniquement si une entree de navigation distincte est retenue ;
- eventuellement `backend/app/schemas/__init__.py` si le projet decide d'y exporter les schemas.

Fichiers a ne pas modifier :

- migrations Alembic ;
- modeles SQLAlchemy ;
- connecteurs externes ;
- moteurs SEO/GEO ;
- worker et scheduler sauf besoin explicitement valide dans un autre sprint.

## 35. Tests repository

Tests repository attendus :

- agregation sites avec pagination ;
- whitelists de tri ;
- rejet d'un sort non autorise ;
- agregation SEO par site ;
- agregation GEO par site ;
- agregation GSC par periode ;
- agregation GA4 par periode ;
- agregation Bing par periode ;
- agregation alertes ;
- agregation monitoring ;
- agregation jobs et workers ;
- tendances par granularite ;
- gestion des periodes vides ;
- absence de lecture de champs secrets.

## 36. Tests service

Tests service attendus :

- score global sans donnees ;
- score global avec toutes les composantes ;
- renormalisation des poids quand une source manque ;
- scoring SEO avec issues ;
- scoring GEO avec recommandations ;
- search visibility GSC/Bing ;
- traffic health GA4 ;
- technical health crawl/GSC/Bing ;
- operations health alertes/jobs/workers ;
- periode precedente ;
- recommandations deterministes ;
- donnees partielles ;
- absence de generation LLM ;
- absence d'appel connecteur.

## 37. Tests API

Tests API attendus :

- `GET /api/v1/dashboard-v2/overview` refuse un utilisateur anonyme ;
- `overview` accepte un utilisateur avec permission de lecture ;
- `overview` valide les periodes ;
- `trends` valide les metriques whitelistees ;
- `trends` refuse une granularite inconnue ;
- `websites` applique pagination et tri ;
- `websites` refuse un sort non autorise ;
- `recommendations` applique filtres et pagination ;
- erreurs 422 sur `date_to < date_from` ;
- erreurs 403 sans permission ;
- aucun endpoint ne declenche un traitement.

## 38. Tests Desktop

Tests Desktop attendus :

- le service Desktop appelle `/dashboard-v2/overview` ;
- le service Desktop transmet les filtres ;
- le service Desktop mappe 401, 403, 422, 500 et erreurs reseau ;
- la page affiche l'etat chargement ;
- la page affiche un etat vide ;
- la page affiche les donnees partielles ;
- la page affiche les cartes principales ;
- la page charge progressivement tendances, sites et recommandations ;
- la page ne calcule pas de score ;
- la page utilise uniquement `ApiClient` ;
- la navigation lazy loading reste valide.

## 39. Risques

Risques identifies :

- requetes trop couteuses si le repository charge trop de lignes ;
- confusion entre donnees absentes et mauvaises performances ;
- score global percu comme opaque ;
- permissions trop larges si `crawl.read` reste la seule permission ;
- affichage Desktop trop dense ;
- tendances incompletes selon les sources ;
- correspondance imparfaite des URLs entre crawl, GSC, GA4 et Bing ;
- donnees externes importees avec granularites differentes ;
- jobs et alertes rattaches indirectement aux sites.

Mitigations :

- agregations SQLAlchemy ciblees ;
- pagination obligatoire ;
- listes limitees dans `overview` ;
- exposition des composantes disponibles et manquantes ;
- documentation claire des scores ;
- chargement progressif Desktop ;
- aucune promesse de KPI non source.

## 40. Criteres d'acceptation

La future implementation du Sprint 35 sera acceptable si :

- aucun nouveau modele SQLAlchemy n'est ajoute ;
- aucune migration Alembic n'est ajoutee ;
- aucun KPI n'est persiste ;
- aucun connecteur externe n'est appele par le Dashboard ;
- les quatre endpoints V2 sont disponibles ;
- les endpoints sont authentifies ;
- les routes restent fines ;
- le service porte les regles metier ;
- le repository porte uniquement les acces SQLAlchemy ;
- les schemas sont Pydantic v2 ;
- les filtres et whitelists sont respectes ;
- la periode precedente est geree ;
- les donnees partielles sont explicites ;
- les KPI affiches sont tous relies a des donnees existantes ;
- le Desktop utilise Page -> Service -> ApiClient -> API REST ;
- le Desktop ne recalcule pas les scores ;
- les tests repository, service, API et Desktop sont ajoutes ;
- les commandes de validation passent.

## 41. Plan d'implementation

Plan recommande :

1. Creer les schemas `dashboard_v2.py`.
2. Creer le repository `DashboardV2Repository` avec agregations SQLAlchemy.
3. Creer le service `DashboardV2Service` avec scoring, deltas et recommandations.
4. Creer les routes `dashboard_v2.py`.
5. Inclure le routeur dans `backend/app/api/v1/router.py`.
6. Creer le service Desktop `DashboardV2Service`.
7. Etendre `DashboardPage` avec chargement progressif.
8. Ajouter les tests repository.
9. Ajouter les tests service.
10. Ajouter les tests API.
11. Ajouter les tests Desktop.
12. Executer les commandes de validation.

Ce plan ne doit etre lance qu'apres validation explicite d'un sprint d'implementation.

## 42. Commandes de validation

Commandes a executer lors de l'implementation future :

```text
ruff check backend desktop tests
pytest tests/repositories/test_dashboard_v2_repository.py
pytest tests/services/test_dashboard_v2_service.py
pytest tests/api/test_dashboard_v2_routes.py
pytest tests/desktop/test_dashboard_v2_service.py tests/desktop/test_dashboard_v2_page.py
pytest
```

Commandes de controle documentaire du present sprint :

```text
git status --short
git diff --stat
git diff --check
```

## Conclusion

Le Dashboard V2 doit devenir une synthese executive multi-sites, calculee a la demande depuis les donnees deja
disponibles. L'architecture recommandee est volontairement conservative : aucune nouvelle table, aucune migration, aucun
cache persistant, aucune generation LLM et aucune execution de traitement.

La valeur du Sprint 35 repose sur la consolidation fiable des modules existants, pas sur la creation de nouvelles
sources. Les KPI retenus dans ce document sont limites aux champs reellement presents dans le depot et doivent rester
tracables vers leurs modules d'origine.
