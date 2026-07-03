# Sprint 21 - Analyse SEO Technique

## 1. Objectif Du Sprint

Le Sprint 21 transforme les donnees produites par le Crawler Engine du Sprint 20 en analyses SEO techniques,
deterministes et exploitables par le backend, l'API REST et le Desktop.

Le Sprint 20 fournit deja :

- le moteur de crawl ;
- l'exploration HTTP ;
- l'extraction des liens ;
- la normalisation des URLs ;
- la persistance des pages decouvertes ;
- l'API Crawls ;
- le module Desktop Crawls.

Le Sprint 21 ne relance pas la conception du crawler. Il exploite les pages deja decouvertes et les donnees brutes
associees afin de produire une analyse SEO technique page par page, puis une synthese rattachee a une session de crawl.

Pipeline cible :

```text
Crawler
    -> HTML
        -> Analyse SEO
            -> Base PostgreSQL
                -> API REST
                    -> Desktop
```

L'objectif principal est de disposer d'une couche d'analyse stable, mesurable et reutilisable pour les sprints suivants.
Le Sprint 22 utilisera ces resultats comme entree d'un Skill GPT specialise, mais aucune intelligence artificielle n'est
utilisee pendant le Sprint 21.

## 2. Principes

Le Sprint 21 repose sur des analyses entierement deterministes.

Principes obligatoires :

- aucune IA ;
- aucun LLM ;
- aucune analyse semantique avancee ;
- aucun jugement editorial automatique ;
- resultats reproductibles a entree identique ;
- regles de calcul explicites ;
- analyses rapides sur un volume important de pages ;
- separation stricte entre crawl, analyse SEO et futures analyses GEO ;
- possibilite de rejouer une analyse SEO sur les donnees d'un crawl existant ;
- persistance des resultats pour eviter les recalculs inutiles.

Les analyses doivent etre fondees sur :

- les informations HTTP collectees par le crawler ;
- le HTML brut recupere ou reference par les pages crawlees si disponible ;
- des parseurs HTML deterministes ;
- des regles de validation documentees ;
- des seuils configurables lorsque cela est pertinent.

Les resultats doivent etre comparables dans le temps. Une meme page analysee avec les memes donnees doit produire les
memes alertes, les memes indicateurs et le meme score.

Le moteur d'analyse SEO travaille exclusivement sur les donnees produites par le moteur de crawl du Sprint 20. Il ne doit
jamais effectuer de nouvelles requetes HTTP vers les sites analyses.

Cette separation garantit :

- la reproductibilite des analyses ;
- des performances elevees ;
- la possibilite de reanalyser un crawl sans relancer un crawl ;
- une separation claire entre Crawl et Analyse SEO.

Si certaines donnees HTML necessaires a l'analyse SEO ne sont pas encore persistees par le Sprint 20, leur persistance
devra faire partie de l'implementation du Sprint 21. Cette persistance ne doit pas remettre en cause le principe : le
crawl collecte, l'analyse SEO exploite.

## 3. Criteres Analyses

Le Sprint 21 couvre les familles d'analyse suivantes. Chaque critere doit pouvoir alimenter :

- un statut par page ;
- une liste d'anomalies ;
- des indicateurs agreges par crawl ;
- le futur score SEO ;
- les futurs tableaux Desktop.

### 3.1 HTTP

L'analyse HTTP exploite les donnees deja produites par le crawler.

Criteres attendus :

- code HTTP ;
- URL demandee ;
- URL finale ;
- presence de redirections ;
- nombre de redirections ;
- chaine de redirection ;
- detection des redirections excessives ;
- detection des boucles de redirection si l'information est disponible ;
- protocole HTTPS ;
- detection des URLs servies en HTTP ;
- compression HTTP si l'information d'en-tete est disponible ;
- temps de reponse ;
- taille HTML ;
- type de contenu ;
- pages non HTML ignorees ou marquees comme non analysables selon le cas.

Exemples d'anomalies :

- page en `4xx` ;
- page en `5xx` ;
- redirection multiple ;
- page finale en HTTP ;
- temps de reponse trop eleve ;
- HTML trop volumineux ;
- type de contenu incompatible avec l'analyse HTML.

### 3.2 Title

Criteres attendus :

- presence de la balise `title` ;
- contenu vide ;
- longueur en caracteres ;
- titre trop court ;
- titre trop long ;
- doublons entre pages d'un meme crawl ;
- nombre de balises `title`.

Le controle des doublons doit se faire a l'echelle de la session de crawl analysee.

### 3.3 Meta Description

Criteres attendus :

- presence de `meta name="description"` ;
- contenu vide ;
- longueur en caracteres ;
- description trop courte ;
- description trop longue ;
- doublons entre pages d'un meme crawl ;
- nombre de balises description.

La meta description n'est pas analysee semantiquement. Le Sprint 21 se limite a la presence, la longueur, la valeur vide
et les doublons.

### 3.4 Canonical

Criteres attendus :

- presence de `link rel="canonical"` ;
- URL canonical absolue ;
- URL canonical relative ;
- canonical auto-referente ;
- canonical differente de l'URL finale ;
- canonical absente sur page indexable ;
- canonical cassée si la cible existe dans les resultats du crawl avec un code d'erreur ;
- boucle canonical si une page A pointe vers B et B pointe vers A dans les donnees disponibles ;
- canonical multiple.

La resolution des canonicals doit utiliser le normalizer d'URL ou une logique equivalente afin de comparer des URLs
stables.

### 3.5 Robots

Criteres attendus :

- presence de `meta name="robots"` ;
- valeurs `index`, `noindex`, `follow`, `nofollow` ;
- autres directives utiles si presentes ;
- presence de l'en-tete `X-Robots-Tag` si disponible ;
- contradiction entre meta robots et X-Robots-Tag ;
- page noindex ;
- page nofollow.

Les directives robots doivent etre normalisees en minuscules pour comparaison.

### 3.6 H1

Criteres attendus :

- nombre de balises `h1` ;
- absence de H1 ;
- H1 vide ;
- H1 multiple ;
- longueur du H1 principal ;
- H1 trop court ;
- H1 trop long.

Le Sprint 21 ne juge pas la pertinence semantique du H1.

### 3.7 H2

Criteres attendus :

- nombre de balises `h2` ;
- H2 vides ;
- longueur indicative des H2 ;
- presence minimale selon type de page si cette information est disponible.

### 3.8 Hierarchie Hn

Criteres attendus :

- extraction ordonnee des balises `h1` a `h6` ;
- detection des sauts de niveau ;
- detection d'une structure commencant par un niveau incoherent ;
- detection de pages sans structure Hn ;
- comptage par niveau.

Exemples :

- `h1 -> h3` sans `h2` ;
- `h2 -> h5` ;
- absence de `h1` mais presence de `h2`.

### 3.9 Images

Criteres attendus :

- nombre d'images ;
- presence de l'attribut `alt` ;
- attribut `alt` vide ;
- presence de l'attribut `title` ;
- presence de `loading="lazy"` ;
- presence des dimensions `width` et `height` ;
- images sans dimensions ;
- images potentiellement cassees si leur URL existe dans les resultats du crawl avec un code d'erreur ;
- images externes ;
- images relatives ;
- images absolues.

Le Sprint 21 ne doit pas telecharger toutes les images si le crawler ne les a pas deja collectees. La detection des images
cassees dependra des informations disponibles dans la base.

### 3.10 Open Graph

Balises principales a detecter :

- `og:title` ;
- `og:description` ;
- `og:url` ;
- `og:type` ;
- `og:image` ;
- `og:site_name` ;
- `og:locale`.

Criteres attendus :

- presence globale Open Graph ;
- balises principales manquantes ;
- valeurs vides ;
- URL ou image relative lorsque cela pose probleme ;
- coherence simple entre `og:url` et l'URL finale si comparable.

### 3.11 Twitter Cards

Balises principales a detecter :

- `twitter:card` ;
- `twitter:title` ;
- `twitter:description` ;
- `twitter:image` ;
- `twitter:site` ;
- `twitter:creator`.

Criteres attendus :

- presence globale Twitter Cards ;
- type de card ;
- balises principales manquantes ;
- valeurs vides.

### 3.12 JSON-LD

Criteres attendus :

- detection des blocs `script type="application/ld+json"` ;
- nombre de blocs JSON-LD ;
- JSON valide ou invalide ;
- extraction des types Schema.org rencontres via `@type` ;
- gestion des tableaux, graphes et objets imbriques ;
- liste des types trouves par page.

Exemples de types a remonter :

- `Organization` ;
- `WebSite` ;
- `WebPage` ;
- `Article` ;
- `BreadcrumbList` ;
- `Product` ;
- `FAQPage` ;
- `LocalBusiness`.

Le Sprint 21 ne valide pas exhaustivement la conformite Schema.org. Il detecte les blocs, leur validite JSON et les types.

### 3.13 hreflang

Criteres attendus :

- detection des balises `link rel="alternate" hreflang="..."` ;
- liste des langues declarees ;
- presence de `x-default` ;
- URLs absolues ou relatives ;
- doublons de langue ;
- hreflang vide ;
- cible absente ou cassée si connue dans le crawl ;
- absence de retour reciproque si les pages ciblees sont presentes dans les donnees ;
- incoherence simple entre langue declaree et attribut `html lang` si disponible.

### 3.14 Liens Internes

Criteres attendus :

- nombre de liens internes ;
- liens relatifs ;
- liens absolus ;
- liens vers la meme page ;
- liens vers ancres ;
- liens internes casses si leur cible est connue avec un code d'erreur ;
- liens internes non decouverts par le crawl ;
- liens internes avec redirection si la cible est connue comme redirigee.

Les URLs doivent etre normalisees avant comparaison.

### 3.15 Liens Externes

Criteres attendus :

- nombre de liens externes ;
- liens externes HTTP ;
- liens externes HTTPS ;
- liens externes non HTTP ignores ou categorises ;
- presence d'attribut `rel="nofollow"` ;
- presence d'attribut `target="_blank"` ;
- absence de `rel="noopener"` sur les liens ouvrant un nouvel onglet.

Le Sprint 21 ne doit pas crawler les sites externes.

### 3.16 Ancres

Criteres attendus :

- ancres vides ;
- ancres composees uniquement d'espaces ;
- ancres generiques de type `cliquez ici`, `en savoir plus`, `lire la suite` ;
- repetitions excessives d'une meme ancre ;
- ancres d'image sans alt exploitable ;
- longueur des ancres.

La liste des ancres generiques doit etre documentee et extensible.

### 3.17 Performance HTML

Sans Lighthouse et sans Core Web Vitals, le Sprint 21 se limite aux indicateurs HTML statiques.

Criteres attendus :

- nombre de scripts ;
- scripts inline ;
- scripts externes ;
- nombre de fichiers CSS ;
- styles inline ;
- nombre d'iframes ;
- poids HTML ;
- nombre de commentaires HTML si pertinent ;
- profondeur approximative du DOM si facilement calculable ;
- presence excessive de scripts ou iframes.

Ces indicateurs ne remplacent pas une mesure navigateur. Ils servent a prioriser les pages a auditer.

### 3.18 Lisibilite

Sans IA, le Sprint 21 calcule des metriques simples :

- nombre de mots ;
- nombre de caracteres ;
- nombre de paragraphes ;
- nombre de phrases ;
- moyenne de mots par phrase ;
- moyenne de caracteres par mot ;
- ratio texte / HTML si disponible.

Ces metriques ne constituent pas une analyse de qualite editoriale.

### 3.19 Langue

Criteres attendus :

- detection de l'attribut `html lang` ;
- valeur vide ;
- format invalide ;
- coherence simple avec les hreflang si disponibles.

Le Sprint 21 ne fait pas de detection automatique de langue par contenu.

### 3.20 Charset

Criteres attendus :

- detection du charset via meta charset ;
- detection via `Content-Type` si disponible ;
- absence de charset ;
- valeurs multiples ou contradictoires ;
- charset non UTF-8.

### 3.21 Viewport

Criteres attendus :

- presence de `meta name="viewport"` ;
- contenu vide ;
- presence de `width=device-width` ;
- presence de `initial-scale` ;
- valeurs incoherentes simples.

### 3.22 Favicon

Criteres attendus :

- detection des liens favicon ;
- types `icon`, `shortcut icon`, `apple-touch-icon` ;
- URL relative ou absolue ;
- favicon absent ;
- favicon cassé si la cible est connue dans le crawl.

### 3.23 Pagination

Criteres attendus :

- detection de `rel="prev"` ;
- detection de `rel="next"` ;
- URLs relatives ou absolues ;
- incoherences simples ;
- cibles cassees si connues dans le crawl.

### 3.24 Balises HTML Importantes

Balises a detecter :

- `main` ;
- `nav` ;
- `header` ;
- `footer` ;
- `article` ;
- `section`.

Criteres attendus :

- presence ou absence ;
- nombre par page ;
- structure minimale indicative.

Ces balises ne sont pas bloquantes pour le SEO, mais elles enrichissent le diagnostic technique et la priorisation.

## 4. Score SEO

Le Sprint 21 doit definir un score SEO technique sur 100 points.

Le score ne doit pas etre une moyenne simple. Il doit etre pondere afin de mieux representer l'impact technique des
problemes detectes.

Proposition de ponderation :

| Famille | Poids | Justification |
| --- | ---: | --- |
| Accessibilite HTTP et indexabilite | 20 | Une page inaccessible, en erreur ou noindex ne peut pas performer correctement. |
| Title et Meta Description | 15 | Balises principales pour l'affichage et le diagnostic SEO de base. |
| Canonical et robots | 15 | Controle de l'indexation, des duplications et des signaux d'URL. |
| Structure Hn | 10 | Structure documentaire utile au diagnostic technique. |
| Maillage interne et ancres | 10 | Navigation, decouverte et coherence interne. |
| Donnees structurees et metadonnees sociales | 10 | JSON-LD, Open Graph et Twitter Cards. |
| Internationalisation | 5 | hreflang et langue HTML. |
| Images | 5 | Alt, dimensions, lazy loading et images cassees. |
| Performance HTML statique | 5 | Poids HTML, scripts, CSS et iframes. |
| Fondations HTML | 5 | Charset, viewport, favicon et balises structurantes. |

Total : 100 points.

Principes de calcul :

- chaque famille dispose de sous-regles ;
- les penalites sont plafonnees par famille ;
- les erreurs critiques retirent plus de points que les avertissements ;
- une page non HTML peut recevoir un statut `not_analyzable` plutot qu'un score complet ;
- une page en erreur HTTP doit etre fortement penalisee ;
- les doublons sont calcules a l'echelle du crawl ;
- les seuils doivent etre documentes et testables ;
- les resultats doivent distinguer score global, score par famille et liste des problemes.

Exemples de severite :

| Severite | Usage |
| --- | --- |
| Critique | Page inaccessible, noindex inattendu, canonical cassée, erreur HTTP. |
| Majeure | Title absent, H1 absent, meta description absente, canonical multiple. |
| Moyenne | Title trop long, Hn saute un niveau, images sans alt. |
| Mineure | Favicon absent, Open Graph incomplet, ancre generique. |

Le score doit aider a prioriser. Il ne remplace pas l'analyse humaine et ne produit aucune recommandation automatique
pendant ce sprint.

## 5. Architecture Backend

L'architecture backend attendue reste strictement conforme au projet :

```text
Routes
    -> Services
        -> Repositories
            -> Models
```

Responsabilites attendues :

| Couche | Responsabilite |
| --- | --- |
| Routes | Exposer les cas d'usage REST et deleguer aux services. |
| Services | Orchestrer l'analyse SEO, appliquer les regles metier et calculer les scores. |
| Repositories | Lire les crawls/pages et persister les resultats SEO. |
| Models | Representer les resultats persistants. |

Le moteur d'analyse SEO doit etre independant du moteur de crawl.

Principe cible :

```text
CrawlSession / CrawlPages
    -> SeoAnalysisService
        -> SeoAnalyzer
            -> SeoAnalysisRepository
                -> SeoAnalysis Models
```

Le Crawler Engine reste responsable de l'exploration. Le futur SEO Analyzer sera responsable de l'analyse technique du
HTML et des metadonnees collectees.

Contraintes d'architecture :

- aucune logique metier dans les routes ;
- aucune logique HTTP crawler dans l'analyse SEO ;
- aucun appel IA ;
- aucun appel Google Search Console ;
- aucun appel Google Analytics ;
- separation claire entre resultats de crawl et resultats d'analyse SEO ;
- possibilite de rejouer une analyse SEO sur un crawl existant ;
- possibilite de supprimer les resultats d'analyse d'un crawl sans supprimer le crawl.

Le Sprint 21 pourra prevoir des modules specialises pour chaque famille d'analyse afin d'eviter un analyseur monolithique.

## 6. Mode D'Execution

L'analyse SEO doit etre executee de maniere asynchrone.

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

Role des etats :

- `PENDING` : l'analyse est creee mais pas encore traitee ;
- `RUNNING` : l'analyse est en cours ;
- `COMPLETED` : l'analyse est terminee avec succes ;
- `FAILED` : l'analyse a echoue.

Le Desktop utilisera ces etats pour afficher la progression et informer l'utilisateur.

## 7. Modele Conceptuel

Le Sprint 21 s'appuie sur les objets fonctionnels suivants :

```text
Crawl
    -> SEO Analysis
        -> Pages analysees
            -> Criteres SEO
                -> Scores
                    -> Anomalies
```

Description fonctionnelle :

- `Crawl` : source de donnees produite par le Sprint 20 ;
- `SEO Analysis` : execution d'analyse rattachee a un crawl ;
- `Pages analysees` : ensemble des pages du crawl traitees par l'analyse SEO ;
- `Criteres SEO` : familles de controles techniques appliquees aux pages ;
- `Scores` : resultats numeriques globaux et par famille ;
- `Anomalies` : problemes detectes, rattaches a une page et a un critere.

Cette section decrit uniquement les objets fonctionnels. Elle ne definit pas de tables SQL, de modele SQLAlchemy ni de
schema de base de donnees.

## 8. API REST

Endpoints prevus, sans implementation dans ce document :

```text
POST /seo-analysis/run/{crawl_id}
GET /seo-analysis/{crawl_id}
GET /seo-analysis/page/{page_id}
DELETE /seo-analysis/{crawl_id}
```

### POST /seo-analysis/run/{crawl_id}

Role :

- lancer l'analyse SEO technique d'une session de crawl ;
- lire les pages crawlees ;
- produire les resultats page par page ;
- calculer les scores ;
- persister la synthese.

Comportements attendus :

- retourner `404` si le crawl n'existe pas ;
- retourner `409` si une analyse est deja en cours ;
- permettre de remplacer ou recalculer une analyse existante selon une regle explicite ;
- retourner un etat de progression ou un resultat final selon le mode retenu.

### GET /seo-analysis/{crawl_id}

Role :

- retourner la synthese SEO d'un crawl ;
- retourner les agregats par famille ;
- retourner les distributions de score ;
- retourner le nombre d'erreurs critiques, majeures, moyennes et mineures.

### GET /seo-analysis/page/{page_id}

Role :

- retourner le detail SEO d'une page crawlee ;
- afficher les balises detectees ;
- afficher les anomalies ;
- afficher le score global et les scores par famille.

### DELETE /seo-analysis/{crawl_id}

Role :

- supprimer les resultats SEO rattaches a une session de crawl ;
- ne pas supprimer la session de crawl ;
- ne pas supprimer les pages crawlees.

Les endpoints devront etre proteges par les permissions adaptees lors de l'implementation.

## 9. Desktop

Le Sprint 21 preparera un futur module Desktop :

```text
SEO Analysis
```

Le Desktop respecte l'architecture existante :

```text
Page
    -> Service
        -> ApiClient
            -> API REST
```

Fonctionnalites attendues :

- selectionner une session de crawl ;
- lancer une analyse SEO ;
- suivre la progression ;
- consulter les resultats globaux ;
- consulter les resultats page par page ;
- filtrer les erreurs ;
- filtrer par severite ;
- filtrer par famille d'analyse ;
- trier par score ;
- trier par code HTTP ;
- trier par nombre d'anomalies ;
- ouvrir la page analysee dans le navigateur systeme ;
- exporter les resultats en CSV ;
- exporter les resultats en Excel.

Les exports CSV et Excel du Sprint 21 correspondent a des exports de donnees brutes ou tabulaires. La generation de
rapports complets reste reservee au Sprint 26.

Vues possibles :

- liste des analyses SEO ;
- synthese du crawl analyse ;
- tableau des pages ;
- detail d'une page ;
- liste des anomalies ;
- filtres par famille ;
- export.

Le Desktop ne doit pas analyser lui-meme le HTML. Il appelle uniquement l'API REST.

Le Desktop ne doit pas acceder a PostgreSQL et ne doit pas importer de modele SQLAlchemy backend.

## 10. Tests

Le Sprint 21 devra etre valide par :

- tests unitaires ;
- tests des services ;
- tests des repositories ;
- tests des routes API ;
- tests du module Desktop.

## 11. Hors Perimetre

Sont explicitement exclus du Sprint 21 :

- intelligence artificielle ;
- recommandations automatiques ;
- analyse semantique ;
- GEO ;
- LLM ;
- Skill GPT ;
- Lighthouse ;
- Core Web Vitals ;
- Google Search Console ;
- Google Analytics ;
- rapports ;
- comparaison concurrentielle ;
- scoring GEO ;
- scoring LLM ;
- generation de contenu ;
- analyse editoriale qualitative ;
- analyse de logs serveur ;
- crawl JavaScript avec navigateur ;
- execution de scripts de pages web.

Le Sprint 21 produit une base SEO technique deterministe. Il ne produit pas de recommandations IA.

Les exports CSV et Excel prevus dans le Sprint 21 ne constituent pas des rapports complets. Les rapports restent hors
perimetre et sont reserves au Sprint 26.

## 12. Preparation Du Sprint 22

Le Sprint 22 exploitera les donnees produites par le Sprint 21 pour alimenter un Skill GPT specialise.

Les donnees SEO techniques fourniront :

- la liste des pages prioritaires ;
- les scores SEO techniques ;
- les familles d'anomalies ;
- les balises detectees ;
- les metadonnees utiles ;
- les contenus HTML ou extraits textuels si disponibles ;
- les signaux de structure ;
- les donnees de maillage interne ;
- les elements utiles a une analyse GEO.

Le Sprint 22 pourra alors traiter :

- score GEO ;
- score LLM ;
- recommandations SEO ;
- recommandations GEO ;
- analyses ChatGPT ;
- analyses Gemini ;
- analyses Claude ;
- analyses Copilot ;
- analyses Perplexity.

Le Sprint 21 doit donc produire des donnees propres, structurees et auditables afin que le Sprint 22 puisse ajouter une
couche d'analyse intelligente sans melanger les responsabilites.

## 13. Conclusion

Le Sprint 21 constitue la premiere couche d'analyse metier au-dessus du Crawler Engine.

Il transforme les donnees brutes de crawl en diagnostic SEO technique, deterministe et persistant. Cette couche doit
rester rapide, reproductible, testable et separee de toute logique IA.

En structurant les criteres, le score, les endpoints prevus et le futur module Desktop, ce document sert de specification
complete pour le developpement du Sprint 21.
