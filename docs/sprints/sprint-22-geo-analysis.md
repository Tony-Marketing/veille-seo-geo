# Sprint 22 - Analyse GEO Avec Skills

## 1. Objectif Du Sprint

Le Sprint 22 definit l'architecture fonctionnelle et technique de la couche d'analyse GEO de la plateforme Veille SEO-GEO
Groupe A.P&Partner.

Le Sprint 20 fournit le moteur de crawl et les donnees brutes issues des pages explorees. Le Sprint 21 fournit le moteur
d'analyse SEO technique, deterministe et persistant. Le Sprint 22 ajoute une couche d'analyse complementaire orientee
GEO, c'est-a-dire l'evaluation de la qualite d'une page web vis-a-vis des moteurs et assistants d'intelligence
artificielle generative.

Pipeline cible :

```text
Crawler
    -> HTML brut stocke
        -> Analyse SEO deterministe
            -> Analyse GEO par Skills
                -> Resultats GEO
                    -> API REST
                        -> Desktop
```

Objectifs principaux :

- evaluer la capacite d'une page a etre comprise, citee et reutilisee par des IA generatives ;
- produire un score GEO ;
- produire un score LLM ;
- produire un score global combinant les signaux SEO et GEO ;
- produire des recommandations SEO exploitant les resultats SEO existants ;
- produire des recommandations GEO ;
- produire des recommandations editoriales ;
- produire des analyses par modele ou famille de modele : ChatGPT, Gemini, Claude, Copilot et Perplexity ;
- permettre l'utilisation de plusieurs Skills specialises ;
- permettre l'execution de plusieurs analyses independantes sur une meme base de donnees de crawl et SEO ;
- rester decouple des fournisseurs d'IA, des modeles et des outils d'orchestration.

Le Sprint 22 est une specification d'architecture. Il ne cree aucun modele SQLAlchemy, aucune migration Alembic, aucune
route FastAPI, aucun service Python, aucun test et aucun fichier de code.

## 2. Perimetre

Le Sprint 22 couvre la conception de la future couche d'analyse GEO.

Le perimetre fonctionnel inclut :

- definition du role du moteur GEO ;
- definition du role des Skills ;
- definition du pipeline d'analyse ;
- definition du cycle d'execution ;
- definition des donnees d'entree et de sortie ;
- definition des scores attendus ;
- definition des recommandations attendues ;
- definition des analyses par modele IA ;
- definition des responsabilites des couches backend ;
- definition des principes d'extensibilite ;
- definition des risques, limitations et criteres d'acceptation ;
- preparation de la future strategie de tests.

Le perimetre technique inclut :

- articulation avec le Crawler Engine du Sprint 20 ;
- articulation avec l'analyse SEO deterministe du Sprint 21 ;
- separation stricte entre crawl, SEO et GEO ;
- orchestration de Skills specialises ;
- conception d'un contrat generique pour les analyses par modele IA ;
- preparation d'une persistance future des resultats GEO ;
- preparation d'une exposition future via API REST ;
- preparation d'une restitution future dans le Desktop.

Le Sprint 22 doit rester compatible avec les donnees produites par les Sprints 20 et 21.

## 3. Hors Perimetre

Sont explicitement hors perimetre du Sprint 22 :

- modification du crawler ;
- nouvelle exploration HTTP ;
- nouveau telechargement de page ;
- rendu JavaScript dans un navigateur ;
- collecte de nouvelles ressources reseau ;
- modification du moteur SEO ;
- remplacement du score SEO ;
- appel direct a un fournisseur IA depuis une route API ;
- creation de modele SQLAlchemy ;
- creation de schema Pydantic ;
- creation de migration Alembic ;
- creation de route FastAPI ;
- creation de service backend ;
- creation de repository ;
- creation de connecteur IA ;
- creation de test ;
- creation de module Desktop ;
- creation de commit ;
- creation de Pull Request.

Le Sprint 22 ne developpe pas la fonctionnalite. Il documente l'architecture cible afin que l'implementation ulterieure
puisse etre realisee sans ambiguite.

## 4. Principes Obligatoires

Principes structurants :

- le crawler n'est jamais modifie par le Sprint 22 ;
- le crawler reste uniquement responsable de l'exploration et de la collecte brute ;
- aucune nouvelle exploration HTTP n'est effectuee pendant une analyse GEO ;
- seule l'analyse SEO existante et le HTML persiste sont exploites ;
- le moteur SEO reste entierement deterministe ;
- les Skills ne remplacent jamais le moteur SEO ;
- les Skills constituent une couche supplementaire d'analyse ;
- les Skills ne doivent pas contenir de logique de crawl ;
- les Skills ne doivent pas modifier les donnees de crawl ;
- l'architecture doit rester decouplee des fournisseurs d'IA ;
- le choix d'un modele IA doit etre configurable ;
- le choix d'un fournisseur doit etre interchangeable ;
- plusieurs Skills doivent pouvoir etre executes pour une meme analyse ;
- plusieurs analyses GEO independantes doivent pouvoir coexister pour un meme crawl ou une meme analyse SEO ;
- les resultats doivent etre historisables et comparables dans le temps.

Le moteur GEO n'est pas un moteur SEO bis. Il consomme les resultats SEO et le HTML persiste pour produire une analyse
complementaire orientee comprehension, citabilite, structuration editoriale et restitution par IA generative.

## 5. Architecture Generale

Architecture logique cible :

```text
Desktop
    |
    v
API REST
    |
    v
Geo Analysis Service
    |
    +-- Geo Analysis Orchestrator
    |       |
    |       +-- Input Builder
    |       +-- Skill Router
    |       +-- Skill Runner
    |       +-- Result Normalizer
    |       +-- Score Aggregator
    |       +-- Recommendation Builder
    |
    +-- Repositories
            |
            +-- Crawl Data
            +-- SEO Results
            +-- GEO Results
```

Architecture par responsabilites :

```text
Crawler Engine
    |
    | produit
    v
HTML brut persiste
    |
    | consomme par
    v
SEO Analyzer deterministe
    |
    | produit
    v
Resultats SEO structures
    |
    | enrichissent
    v
GEO Analyzer
    |
    | orchestre
    v
Skills specialises
    |
    | retournent
    v
Resultats GEO normalises
```

Le GEO Analyzer doit etre concu comme une couche d'orchestration. Il prepare les donnees, appelle les Skills selon une
configuration explicite, normalise les reponses et agrege les scores. Il ne doit pas etre couple a un modele IA unique.

## 6. Role Du Crawler

Le Crawler Engine conserve le role defini au Sprint 20.

Responsabilites du crawler :

- explorer les sites selon les politiques de crawl ;
- telecharger les pages autorisees ;
- suivre les redirections ;
- conserver les statuts HTTP ;
- extraire les liens ;
- normaliser les URLs ;
- persister les pages, metadonnees HTTP et HTML brut si disponible ;
- exposer une base stable pour les analyses ulterieures.

Le crawler ne doit pas :

- evaluer la qualite GEO ;
- appeler un Skill ;
- appeler un LLM ;
- produire des recommandations ;
- produire un score GEO ;
- relancer une exploration pour repondre aux besoins GEO ;
- etre modifie pour adapter les resultats GEO.

Le Sprint 22 consomme uniquement les donnees deja disponibles. Si une future implementation constate qu'une donnee de
crawl manque, elle devra etre signalee comme limite ou dependance d'un sprint ulterieur. Elle ne devra pas conduire a
modifier le crawler dans le cadre du Sprint 22.

## 7. Role Du Moteur SEO

Le moteur SEO conserve le role defini au Sprint 21.

Responsabilites du moteur SEO :

- analyser le HTML et les metadonnees de maniere deterministe ;
- calculer un score SEO technique ;
- detecter les anomalies techniques ;
- produire des resultats reproductibles ;
- persister les signaux SEO utiles ;
- fournir une base structuree au moteur GEO.

Le moteur SEO ne doit pas :

- appeler des Skills ;
- appeler des LLM ;
- produire de jugement editorial non deterministe ;
- produire d'analyse par modele IA ;
- se coupler au moteur GEO ;
- changer ses regles pour satisfaire un fournisseur IA.

Le moteur GEO peut utiliser les resultats SEO comme signaux d'entree. Il ne doit jamais ecraser, recalculer ou redefinir
le score SEO. Le score SEO reste une mesure technique deterministe.

## 8. Role Du Moteur GEO

Le moteur GEO est une couche d'analyse supplementaire au-dessus du crawl et du SEO.

Responsabilites du moteur GEO :

- selectionner les pages a analyser ;
- construire un contexte d'analyse a partir du HTML persiste et des resultats SEO ;
- choisir les Skills a executer selon la configuration ;
- executer les Skills de maniere isolee ;
- collecter les resultats par Skill ;
- normaliser les resultats dans un format commun ;
- calculer un score GEO ;
- calculer un score LLM ;
- calculer un score global ;
- produire des recommandations SEO, GEO et editoriales ;
- produire une analyse par modele cible ;
- persister les resultats ;
- permettre le suivi d'etat et d'erreur.

Le moteur GEO doit separer l'orchestration des calculs :

```text
GeoAnalysisService
    -> valide la demande et les droits
    -> charge les donnees sources
    -> cree une execution GEO
    -> delegue au GeoAnalysisOrchestrator

GeoAnalysisOrchestrator
    -> prepare les entrees
    -> choisit les Skills
    -> execute les analyses
    -> normalise les sorties
    -> calcule les scores agreges

GeoScoring
    -> calcule les scores GEO, LLM et global

GeoRecommendations
    -> classe les recommandations
    -> distingue SEO, GEO et editorial
```

Le moteur GEO ne doit pas contenir de logique HTTP crawler ni de logique FastAPI.

## 9. Role Des Skills

Les Skills sont des composants specialises d'analyse.

Ils peuvent etre dedies a :

- un modele IA cible ;
- une famille de modeles ;
- une dimension d'analyse ;
- une typologie de page ;
- une langue ;
- une strategie de recommandation ;
- une verification editoriale ;
- une estimation de citabilite.

Exemples de Skills possibles :

| Skill | Role |
| --- | --- |
| `geo_summary_skill` | Evaluer la clarte et la synthese de la page pour les IA generatives. |
| `geo_citation_skill` | Evaluer la probabilite de citation et les preuves disponibles. |
| `geo_model_chatgpt_skill` | Produire une lecture ciblee pour ChatGPT. |
| `geo_model_gemini_skill` | Produire une lecture ciblee pour Gemini. |
| `geo_model_claude_skill` | Produire une lecture ciblee pour Claude. |
| `geo_model_copilot_skill` | Produire une lecture ciblee pour Copilot. |
| `geo_model_perplexity_skill` | Produire une lecture ciblee pour Perplexity. |
| `geo_editorial_skill` | Produire des recommandations editoriales. |
| `geo_structured_data_skill` | Evaluer les donnees structurees et entites comprehensibles par LLM. |

Principes obligatoires :

- un Skill ne remplace pas le moteur SEO ;
- un Skill ne modifie pas les donnees sources ;
- un Skill doit retourner une sortie structuree ;
- un Skill doit pouvoir echouer sans bloquer toute l'analyse si la configuration le permet ;
- un Skill doit pouvoir etre ajoute ou retire sans refonte du moteur GEO ;
- un Skill ne doit pas etre couple a la persistance ;
- un Skill ne doit pas connaitre FastAPI ;
- un Skill ne doit pas appeler directement les repositories.

Contrat conceptuel d'un Skill :

```text
Skill Input
    - page_url
    - html_excerpt ou text_excerpt
    - seo_summary
    - technical_signals
    - analysis_goal
    - target_model
    - language
    - constraints

Skill Output
    - skill_name
    - skill_version
    - status
    - score
    - findings
    - recommendations
    - model_analysis
    - errors
    - metadata
```

## 10. Pipeline Complet D'Analyse

Pipeline fonctionnel cible :

```text
1. Selection d'une analyse SEO existante
        |
        v
2. Verification du crawl source
        |
        v
3. Chargement des pages et HTML persiste
        |
        v
4. Chargement des resultats SEO deterministes
        |
        v
5. Construction des entrees GEO
        |
        v
6. Selection des Skills et modeles cibles
        |
        v
7. Execution des Skills
        |
        v
8. Normalisation des resultats
        |
        v
9. Calcul des scores GEO, LLM et global
        |
        v
10. Generation des recommandations
        |
        v
11. Persistance des resultats GEO
        |
        v
12. Restitution API et Desktop
```

Le pipeline ne contient aucune etape de crawl. Toutes les donnees exploitees proviennent de la base existante.

## 11. Cycle D'Execution

L'analyse GEO doit etre executable de maniere asynchrone.

Cycle de vie attendu :

```text
PENDING
    -> RUNNING
        -> COMPLETED
```

En cas d'erreur bloquante :

```text
PENDING
    -> RUNNING
        -> FAILED
```

En cas d'annulation :

```text
PENDING
    -> RUNNING
        -> CANCELLING
            -> CANCELLED
```

Etats conceptuels :

| Etat | Signification |
| --- | --- |
| `PENDING` | Analyse creee mais non traitee. |
| `RUNNING` | Analyse en cours d'execution. |
| `COMPLETED` | Analyse terminee avec succes. |
| `FAILED` | Analyse interrompue par une erreur bloquante. |
| `CANCELLING` | Arret demande, les traitements en cours se terminent proprement. |
| `CANCELLED` | Analyse arretee volontairement. |
| `PARTIAL` | Analyse terminee avec au moins un Skill en erreur non bloquante. |

Etapes internes :

```text
Geo Analysis
    |
    +-- Prepare inputs
    |
    +-- Run Skill A
    |
    +-- Run Skill B
    |
    +-- Run Skill C
    |
    +-- Normalize outputs
    |
    +-- Aggregate scores
    |
    +-- Persist results
```

Une future implementation pourra executer les Skills en sequence ou en parallele selon les contraintes de cout, de
quota, de stabilite et de priorite.

## 12. Flux De Donnees

Flux principal :

```text
CrawlSession
    |
    +-- CrawlPage
    |       |
    |       +-- URL finale
    |       +-- code HTTP
    |       +-- HTML brut
    |       +-- metadonnees techniques
    |
    v
SeoAnalysis
    |
    +-- score SEO
    +-- anomalies SEO
    +-- signaux HTML
    +-- structure Hn
    +-- donnees structurees
    +-- liens et ancres
    |
    v
GeoAnalysis
    |
    +-- inputs normalises
    +-- executions de Skills
    +-- resultats par modele
    +-- scores GEO / LLM / global
    +-- recommandations
```

Flux entre composants :

```text
GeoAnalysisService
    |
    | lit
    v
CrawlRepository + SeoAnalysisRepository
    |
    | fournit
    v
GeoInputBuilder
    |
    | transmet
    v
SkillRunner
    |
    | recoit
    v
SkillResult
    |
    | normalise
    v
GeoResultNormalizer
    |
    | agrege
    v
GeoScoreAggregator
    |
    | persiste
    v
GeoAnalysisRepository
```

Le HTML brut peut etre utilise sous forme complete ou sous forme d'extraits selon les limites de taille. Les extraits
doivent etre construits de maniere deterministe autant que possible afin de rendre les analyses comparables.

## 13. Modeles Conceptuels

Cette section decrit des objets conceptuels. Elle ne definit pas de tables, de models SQLAlchemy ni de schemas Pydantic.

### 13.1 GeoAnalysis

Represente une execution GEO.

Champs conceptuels :

- identifiant d'analyse ;
- identifiant du crawl source ;
- identifiant de l'analyse SEO source ;
- statut ;
- configuration d'execution ;
- liste des Skills demandes ;
- liste des modeles cibles ;
- date de creation ;
- date de debut ;
- date de fin ;
- progression ;
- score GEO ;
- score LLM ;
- score global ;
- resume global ;
- erreurs.

### 13.2 GeoPageAnalysis

Represente l'analyse GEO d'une page.

Champs conceptuels :

- identifiant de page crawlee ;
- URL finale ;
- statut de traitement ;
- score GEO de page ;
- score LLM de page ;
- score global de page ;
- synthese ;
- forces ;
- faiblesses ;
- recommandations SEO ;
- recommandations GEO ;
- recommandations editoriales ;
- analyses par modele ;
- erreurs non bloquantes.

### 13.3 GeoSkillExecution

Represente l'execution d'un Skill.

Champs conceptuels :

- nom du Skill ;
- version du Skill ;
- modele cible ;
- fournisseur cible si applicable ;
- statut ;
- duree ;
- score retourne ;
- sortie normalisee ;
- erreurs ;
- cout estime si disponible ;
- metadata technique.

### 13.4 GeoModelAnalysis

Represente l'analyse ciblee pour un modele IA.

Modeles initialement attendus :

- ChatGPT ;
- Gemini ;
- Claude ;
- Copilot ;
- Perplexity.

Champs conceptuels :

- nom du modele cible ;
- famille de modele ;
- fournisseur logique ;
- capacite estimee a comprendre la page ;
- capacite estimee a citer la page ;
- clarte des entites ;
- qualite des preuves ;
- adequation des donnees structurees ;
- risques de mauvaise interpretation ;
- recommandations specifiques.

### 13.5 GeoRecommendation

Represente une recommandation issue de l'analyse GEO.

Types de recommandations :

- `seo` : action technique deja liee au diagnostic SEO ;
- `geo` : action visant la comprehension ou citation par IA ;
- `editorial` : action de clarte, structure, preuves, FAQ, sources ou reformulation.

Champs conceptuels :

- type ;
- severite ;
- priorite ;
- titre ;
- description ;
- justification ;
- page concernee ;
- modele concerne si applicable ;
- Skill source ;
- effort estime ;
- impact estime.

## 14. Scores Attendus

Le Sprint 22 prevoit trois familles de scores.

### 14.1 Score GEO

Le score GEO mesure l'aptitude d'une page a etre comprise, extraite, citee ou synthetisee par des IA generatives.

Dimensions possibles :

| Dimension | Role |
| --- | --- |
| Clarification du sujet | La page expose clairement son sujet principal. |
| Entites identifiables | Les marques, produits, personnes, lieux et concepts sont explicites. |
| Preuves et sources | Les affirmations importantes sont appuyees par des elements verifiables. |
| Structure editoriale | Les sections, titres, listes et blocs repondent a des intentions claires. |
| Donnees structurees | Les schemas et metadonnees facilitent l'interpretation. |
| Citabilite | La page contient des passages reutilisables et attribuables. |
| Fraicheur apparente | Les dates, mises a jour ou contextes temporels sont comprehensibles. |
| Robustesse anti-ambiguite | Les informations reduisent les risques d'interpretation erronee. |

### 14.2 Score LLM

Le score LLM mesure la compatibilite de la page avec les comportements attendus des modeles de langage.

Dimensions possibles :

- comprehension du contenu ;
- extraction de reponses ;
- synthese fidele ;
- detection des entites ;
- alignement avec les intentions de recherche ;
- couverture des questions probables ;
- lisibilite des passages ;
- presence de contexte suffisant ;
- reduction du bruit HTML ;
- coherence entre contenu visible, metadonnees et donnees structurees.

### 14.3 Score Global

Le score global combine les signaux SEO deterministes et les signaux GEO.

Principe cible :

```text
Score global = combinaison ponderee du score SEO, du score GEO et du score LLM
```

La ponderation exacte devra etre definie lors de l'implementation, mais elle devra respecter les principes suivants :

- le score SEO conserve son origine deterministe ;
- le score GEO ne doit pas modifier le score SEO ;
- les scores doivent rester consultables separement ;
- la formule doit etre documentee et versionnee ;
- les resultats doivent indiquer la version de calcul utilisee.

## 15. Recommandations Attendues

Le moteur GEO devra produire plusieurs familles de recommandations.

### 15.1 Recommandations SEO

Les recommandations SEO issues du Sprint 22 s'appuient sur les resultats du Sprint 21. Elles ne remplacent pas les
anomalies SEO deterministes, mais les priorisent dans une logique GEO.

Exemples :

- corriger une title absente sur une page strategique ;
- enrichir une meta description trop vague ;
- corriger une structure Hn confuse ;
- renforcer les donnees structurees ;
- clarifier les ancres internes ;
- corriger les pages noindex incoherentes.

### 15.2 Recommandations GEO

Les recommandations GEO visent la comprehension par les IA generatives.

Exemples :

- expliciter les entites principales ;
- ajouter des definitions courtes et reutilisables ;
- ajouter des blocs de preuve ;
- renforcer les sources internes ;
- structurer les reponses aux questions frequentes ;
- rendre les informations differentiantes plus accessibles ;
- ameliorer la coherence entre contenu, schema.org et metadonnees.

### 15.3 Recommandations Editoriales

Les recommandations editoriales visent la qualite du contenu.

Exemples :

- clarifier l'introduction ;
- reduire les passages ambigus ;
- ajouter une synthese ;
- mieux separer les sections ;
- renforcer les exemples ;
- ajouter des dates ou contextes lorsque necessaire ;
- reformuler les promesses trop generales.

## 16. Analyses Par Modele IA

Le Sprint 22 doit prevoir une architecture generique permettant d'ajouter ou retirer des modeles.

Modeles initiaux :

| Modele | Analyse attendue |
| --- | --- |
| ChatGPT | Capacite a comprendre la page, synthetiser et citer la marque. |
| Gemini | Capacite a relier la page a des intentions de recherche et entites. |
| Claude | Capacite a restituer un contenu long, nuance et structure. |
| Copilot | Capacite a exploiter la page dans un contexte web et productivite. |
| Perplexity | Capacite a citer la page comme source fiable dans une reponse. |

Le moteur GEO ne doit pas contenir de conditions rigides du type :

```text
if model == "chatgpt"
```

Il doit utiliser une configuration ou un registre de modeles :

```text
Model Registry
    |
    +-- chatgpt
    +-- gemini
    +-- claude
    +-- copilot
    +-- perplexity
    +-- future_model
```

Chaque entree du registre pourra definir :

- nom fonctionnel ;
- fournisseur logique ;
- Skill par defaut ;
- contraintes de prompt ;
- format de sortie attendu ;
- seuils specifiques ;
- statut actif ou inactif.

## 17. Responsabilites Des Couches

La future implementation devra respecter l'architecture existante :

```text
Routes
    -> Services
        -> Orchestrators / Engines
            -> Repositories
                -> Models
```

Responsabilites attendues :

| Couche | Responsabilite |
| --- | --- |
| Routes | Exposer les cas d'usage REST et deleguer aux services. |
| Services | Valider les demandes, verifier les droits, orchestrer les cas d'usage. |
| GEO Orchestrator | Executer le pipeline GEO et coordonner les Skills. |
| Skills | Produire des analyses specialisees sans persistance directe. |
| Scoring | Calculer les scores a partir de resultats normalises. |
| Repositories | Lire les donnees sources et persister les resultats GEO. |
| Models | Representer les resultats persistants lors du developpement futur. |
| Desktop | Afficher, filtrer et consulter les analyses via l'API REST. |

Les routes ne doivent jamais contenir :

- appel direct a un Skill ;
- appel direct a un LLM ;
- logique de scoring ;
- lecture directe du HTML ;
- logique metier GEO ;
- appel HTTP externe.

## 18. Gestion Des Erreurs

Types d'erreurs a prevoir :

| Type | Exemple | Comportement attendu |
| --- | --- | --- |
| Donnees sources absentes | HTML manquant | Marquer la page non analysable ou l'analyse en erreur selon criticite. |
| Analyse SEO absente | Aucun resultat SEO disponible | Refuser le lancement ou demander une analyse SEO prealable. |
| Skill indisponible | Skill non installe ou inactif | Marquer le Skill en erreur. |
| Sortie invalide | Reponse non conforme au contrat | Rejeter la sortie et conserver l'erreur. |
| Timeout | Skill trop lent | Arreter le Skill concerne et poursuivre si autorise. |
| Quota | Limite fournisseur atteinte | Mettre l'analyse en `PARTIAL` ou `FAILED` selon configuration. |
| Erreur bloquante | Configuration incoherente | Passer l'analyse en `FAILED`. |

Principes :

- une erreur de Skill ne doit pas forcement annuler toute l'analyse ;
- les erreurs doivent etre persistables ;
- les erreurs doivent etre lisibles dans le Desktop ;
- les erreurs doivent distinguer source, Skill, modele et page ;
- une analyse partielle doit etre clairement signalee ;
- aucune erreur GEO ne doit modifier les resultats SEO ou crawl.

## 19. Performances Attendues

Les analyses GEO peuvent etre plus couteuses que les analyses SEO.

Contraintes attendues :

- ne jamais relancer de crawl pour une analyse GEO ;
- eviter les relectures inutiles du HTML ;
- limiter la taille des entrees transmises aux Skills ;
- permettre une selection de pages ;
- permettre un mode echantillon ;
- permettre une execution par lots ;
- permettre une reprise apres erreur ;
- historiser les resultats pour eviter les recalculs inutiles ;
- journaliser les durees par page, Skill et modele ;
- prevoir des timeouts par Skill ;
- prevoir des limites de concurrence ;
- prevoir des limites de cout si des fournisseurs payants sont utilises.

Une future implementation devra eviter de traiter toutes les pages d'un site avec tous les modeles si l'utilisateur ne
l'a pas explicitement demande. Les analyses GEO doivent pouvoir etre ciblees.

## 20. Extensibilite

L'architecture doit permettre :

- l'ajout d'un nouveau Skill ;
- l'ajout d'un nouveau modele IA ;
- l'ajout d'un nouveau fournisseur ;
- le changement de fournisseur pour un modele existant ;
- l'execution de plusieurs Skills pour une meme page ;
- l'execution de plusieurs analyses independantes ;
- la comparaison de plusieurs analyses dans le temps ;
- la version des prompts, Skills et formules de scoring ;
- l'ajout de nouvelles dimensions de score ;
- l'ajout de nouveaux types de recommandations.

Principe de decouplage :

```text
GEO Orchestrator
    |
    v
Skill Interface
    |
    +-- Skill ChatGPT
    +-- Skill Gemini
    +-- Skill Claude
    +-- Skill Copilot
    +-- Skill Perplexity
    +-- Skill futur
```

Le moteur GEO depend d'une interface fonctionnelle, pas d'un fournisseur specifique.

## 21. Evolutions Futures

Evolutions possibles apres le Sprint 22 :

- module Desktop complet de consultation GEO ;
- comparaison temporelle des scores GEO ;
- comparaison concurrentielle ;
- integration de Google Search Console ;
- integration de Google Analytics ;
- detection des pages prioritaires par potentiel GEO ;
- planification automatique des analyses GEO ;
- rapports PDF ou Excel ;
- alertes de degradation ;
- benchmark de modeles IA ;
- suivi des citations reelles dans des moteurs IA ;
- gestion fine des couts par fournisseur ;
- experimentation de prompts versionnes ;
- evaluation humaine des recommandations ;
- validation automatique de la coherence entre recommandations et resultats SEO.

Ces evolutions doivent rester compatibles avec les principes du Sprint 22.

## 22. Risques

Risques principaux :

| Risque | Impact | Mitigation |
| --- | --- | --- |
| Couplage a un fournisseur IA | Refactorisation couteuse | Utiliser un registre de modeles et une interface de Skill. |
| Resultats non reproductibles | Comparaisons difficiles | Versionner Skills, prompts, modeles et formules de score. |
| Cout trop eleve | Analyses difficiles a generaliser | Prevoir selection de pages, lots, quotas et mode echantillon. |
| Sorties de Skills heterogenes | Aggregation fragile | Imposer un format de sortie normalise. |
| Confusion SEO / GEO | Architecture difficile a maintenir | Garder SEO deterministe et GEO comme couche supplementaire. |
| HTML trop volumineux | Entrees trop lourdes | Construire des extraits deterministes. |
| Erreurs partielles | Experience utilisateur confuse | Distinguer `COMPLETED`, `PARTIAL`, `FAILED` et details par Skill. |

## 23. Limitations

Limitations assumees :

- l'analyse GEO depend de la qualite du HTML persiste ;
- l'analyse GEO depend de la disponibilite des resultats SEO ;
- les scores GEO et LLM sont moins deterministes que le score SEO ;
- les analyses par modele peuvent evoluer avec le comportement des modeles IA ;
- une page non crawlee ne peut pas etre analysee ;
- une page sans HTML exploitable peut etre marquee comme non analysable ;
- le Sprint 22 ne mesure pas les citations reelles dans les moteurs IA ;
- le Sprint 22 ne garantit pas qu'un modele IA citera effectivement une page ;
- le Sprint 22 ne remplace pas une validation humaine editoriale.

Ces limitations doivent etre visibles dans les futures interfaces et documentations utilisateur.

## 24. Criteres D'Acceptation

La specification Sprint 22 est acceptee si elle permet de guider une implementation future respectant les criteres
suivants :

- le crawler n'est pas modifie ;
- aucune nouvelle exploration HTTP n'est effectuee par le moteur GEO ;
- le moteur SEO reste deterministe et separe ;
- les Skills sont une couche supplementaire ;
- plusieurs Skills peuvent etre configures ;
- plusieurs modeles IA peuvent etre analyses ;
- le changement de fournisseur ne necessite pas de refonte ;
- plusieurs analyses GEO independantes peuvent coexister ;
- les resultats GEO sont rattaches a un crawl et a une analyse SEO source ;
- les scores SEO, GEO, LLM et global restent distinguables ;
- les recommandations sont classees par type : SEO, GEO, editorial ;
- les erreurs de Skill sont tracables ;
- une execution partielle peut etre representee ;
- l'architecture respecte Routes -> Services -> Repositories -> Models ;
- le Desktop reste client de l'API et ne traite pas lui-meme le HTML ;
- les futurs tests peuvent valider le pipeline sans appeler de vrai fournisseur IA.

## 25. Strategie De Tests Futurs

Aucun test n'est cree dans le Sprint 22. La strategie suivante devra guider l'implementation future.

Tests unitaires a prevoir :

- construction des entrees GEO ;
- selection des Skills ;
- normalisation des sorties ;
- calcul du score GEO ;
- calcul du score LLM ;
- calcul du score global ;
- classement des recommandations ;
- gestion des erreurs de Skill ;
- validation du registre de modeles.

Tests de services a prevoir :

- creation d'une analyse GEO ;
- refus si l'analyse SEO source est absente ;
- execution avec un Skill unique ;
- execution avec plusieurs Skills ;
- analyse partielle si un Skill echoue ;
- annulation d'une analyse ;
- reprise ou relance d'une analyse selon les regles retenues.

Tests de repositories a prevoir :

- persistance d'une analyse GEO ;
- persistance des resultats par page ;
- persistance des executions de Skills ;
- lecture paginee des resultats ;
- filtrage par statut, score, Skill ou modele ;
- suppression d'une analyse GEO sans suppression du crawl ou du SEO.

Tests API a prevoir :

- creation d'analyse ;
- liste des analyses ;
- consultation du detail ;
- consultation des resultats page par page ;
- filtrage ;
- erreurs `404` et `422` ;
- droits d'acces si le module de permissions l'exige.

Tests Desktop a prevoir :

- affichage de la liste des analyses ;
- lancement d'une analyse via API ;
- suivi de progression ;
- affichage des scores ;
- affichage des recommandations ;
- affichage des erreurs partielles ;
- filtrage par modele et type de recommandation.

Tests sans fournisseur reel :

- utiliser des Skills factices ;
- utiliser des sorties deterministes ;
- simuler timeouts et erreurs ;
- verifier les contrats de sortie ;
- eviter toute dependance a un service externe dans les tests automatises.

## 26. Compatibilite Avec Les Sprints 20 Et 21

Compatibilite Sprint 20 :

- le Sprint 22 utilise les sessions de crawl existantes ;
- le Sprint 22 utilise les pages crawlees existantes ;
- le Sprint 22 utilise le HTML brut persiste ;
- le Sprint 22 ne modifie pas le crawler ;
- le Sprint 22 ne relance pas d'exploration HTTP ;
- le Sprint 22 ne change pas les politiques de crawl.

Compatibilite Sprint 21 :

- le Sprint 22 utilise les analyses SEO existantes ;
- le Sprint 22 conserve le caractere deterministe du moteur SEO ;
- le Sprint 22 ne remplace pas le score SEO ;
- le Sprint 22 enrichit les resultats SEO avec une lecture GEO ;
- le Sprint 22 permet de prioriser certaines recommandations SEO selon leur impact GEO ;
- le Sprint 22 conserve la separation entre analyse technique et analyse IA.

Vue d'ensemble de compatibilite :

```text
Sprint 20
    Crawler Engine
        |
        v
Sprint 21
    SEO Analyzer deterministe
        |
        v
Sprint 22
    GEO Analyzer par Skills
```

Chaque sprint ajoute une couche. Aucun sprint ne doit annuler ou redefinir la responsabilite du precedent.

## 27. Cycle De Vie D'Une Analyse GEO

Diagramme de cycle de vie :

```text
Utilisateur
    |
    | demande une analyse GEO
    v
Desktop
    |
    | appelle l'API
    v
Route API
    |
    | delegue
    v
GeoAnalysisService
    |
    | verifie crawl + SEO
    v
GeoAnalysis PENDING
    |
    | demarre
    v
GeoAnalysis RUNNING
    |
    +-- page 1 -> Skills -> resultats
    +-- page 2 -> Skills -> resultats
    +-- page n -> Skills -> resultats
    |
    | agrege
    v
Scores + recommandations
    |
    | persiste
    v
GeoAnalysis COMPLETED / PARTIAL / FAILED
    |
    | consulte
    v
Desktop
```

Le cycle de vie doit etre lisible par l'utilisateur final, notamment en cas d'analyse partielle.

## 28. Synthese D'Architecture

Le Sprint 22 prepare une couche GEO generique, extensible et decouplee.

Synthese :

- Sprint 20 collecte ;
- Sprint 21 analyse techniquement ;
- Sprint 22 interprete et recommande via Skills ;
- le crawler reste intact ;
- le moteur SEO reste deterministe ;
- les Skills sont interchangeables ;
- les modeles IA sont configurables ;
- les fournisseurs restent substituables ;
- les analyses sont historisables ;
- les scores restent separables ;
- l'implementation future devra respecter l'architecture modulaire du projet.

Cette specification doit servir de base a l'implementation complete du Sprint 22 sans imposer prematurement des fichiers,
models ou endpoints. Toute creation de code, de migration, de test ou d'API devra faire l'objet d'un developpement futur
dedie et conforme aux conventions du depot.

## 29. Implementation Sprint 22

L'implementation retenue conserve l'architecture existante du projet et n'introduit pas de module parallele
`backend/app/geo/`.

Organisation backend effective :

```text
backend/app/api/v1/routes/geo_analysis.py
    -> backend/app/services/geo_analysis.py
        -> backend/app/services/geo/
            -> engine.py
            -> provider.py
            -> prompt_builder.py
            -> score_calculator.py
            -> providers/openai_provider.py
        -> backend/app/repositories/geo_analysis.py
            -> backend/app/models/geo_analysis.py
```

Modeles persistants crees :

- `GeoAnalysis` ;
- `GeoProviderResult` ;
- `GeoRecommendation`.

Provider disponible en V1 :

- `OpenAIProvider`, prepare mais sans appel reseau reel ;
- les autres providers IA ne sont pas implementes dans ce sprint.

Le provider retourne une reponse structuree. Le calcul des scores et recommandations reste centralise dans
`score_calculator.py`.

API REST V1 effective :

```text
POST /api/v1/geo-analysis
POST /api/v1/geo-analysis/{analysis_id}/run
GET /api/v1/geo-analysis/{analysis_id}
GET /api/v1/geo-analysis
DELETE /api/v1/geo-analysis/{analysis_id}
```

Desktop V1 :

- liste des analyses GEO ;
- creation depuis une analyse SEO existante ;
- execution d'une analyse GEO ;
- affichage des scores global, GEO et LLM ;
- affichage des resultats providers ;
- affichage des recommandations.

Cette V1 ne constitue pas un Dashboard GEO complet. Le dashboard SEO/GEO reste reserve au Sprint 23.
