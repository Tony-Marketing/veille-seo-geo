# Sprint 38 — GEO Intelligence & IA Génératives

## Statut du document

Ce document constitue le cadrage fonctionnel et architectural du Sprint 38. Il décrit les objectifs, les capacités
attendues et les contrats envisagés pour la future brique **GEO Intelligence** de la Version 1.1.

Il ne constitue pas une implémentation. Les choix techniques détaillés, les seuils de calcul, les contrats définitifs
et le périmètre exact des fournisseurs devront être confirmés par une analyse du dépôt avant tout développement.

## Objectifs

Le Sprint 38 a pour objectif d'introduire un moteur d'analyse GEO transverse consacré à la visibilité des sites et des
marques dans les principales intelligences artificielles génératives. Cette nouvelle capacité devra centraliser des
données comparables, historisées et rattachées aux Websites suivis par la plateforme.

Le sprint devra notamment permettre de :

- mesurer la visibilité GEO des sites dans plusieurs IA génératives ;
- centraliser les observations provenant de plusieurs fournisseurs ;
- normaliser ces observations dans un modèle commun et extensible ;
- suivre les citations, les sources et la fréquence d'apparition ;
- comparer les résultats entre fournisseurs et dans le temps ;
- enrichir automatiquement le **Recommendation Engine** avec des signaux GEO exploitables ;
- alimenter **Dashboard V2** avec des indicateurs consolidés, sans déplacer la logique métier dans le Dashboard.

Le moteur devra produire des résultats explicables et traçables. Un même ensemble de données devra conduire aux mêmes
indicateurs et aux mêmes recommandations selon des règles déterministes et documentées.

## Contexte

Le Sprint 37 introduit le **Recommendation Engine** comme point central de normalisation, de consolidation, de
déduplication, de priorisation et de gestion du cycle de vie des recommandations. Les modules métier conservent la
responsabilité de leurs données et constats ; le moteur de recommandations les consomme sans relancer leurs analyses ni
dupliquer leurs règles.

Dans cette organisation, **GEO Intelligence** devient une nouvelle source canonique. Elle produit des observations de
visibilité multi-IA et les met à disposition du Recommendation Engine, du Dashboard V2 et des futurs rapports. Elle ne
remplace pas le module GEO Analysis existant : elle complète son périmètre par un suivi transverse, comparable et
historisé de la présence dans les moteurs d'IA générative.

Les sources canoniques de recommandations sont désormais envisagées comme suit :

- **SEO Analysis** ;
- **GEO Analysis** ;
- **Monitoring** ;
- **Alertes** ;
- **Google Search Console** ;
- **Google Analytics 4** ;
- **Bing Webmaster Tools** ;
- **GEO Intelligence**.

Chaque source demeure propriétaire de ses données. Les échanges entre modules devront passer par les couches de
services et de repositories prévues par l'architecture officielle.

## IA prises en charge

Le périmètre fonctionnel prévoit la prise en charge des fournisseurs suivants :

- **ChatGPT** ;
- **Gemini** ;
- **Claude** ;
- **Microsoft Copilot** ;
- **Perplexity**.

La représentation des fournisseurs devra rester générique. L'ajout ultérieur d'une nouvelle IA ne devra pas imposer
une modification globale du modèle métier, des contrats REST ou des écrans Desktop.

Les particularités techniques de chaque fournisseur devront être isolées hors des routes et de l'interface Desktop.
Les réponses devront être normalisées avant leur exploitation par le service métier afin de rendre les indicateurs
comparables sans masquer les différences connues entre les IA.

## Fonctionnalités attendues

### Visibilité GEO

La plateforme devra mesurer la présence d'un Website, d'une marque ou d'une entité dans les réponses analysées. La
méthode de calcul du score de visibilité devra être explicite, stable et testable.

### Citations

Le système devra comptabiliser les citations détectées et conserver le contexte nécessaire à leur interprétation. Une
citation devra pouvoir être reliée au fournisseur, au prompt, au Website et à la date de capture.

### Nombre et diversité des sources

Les analyses devront mesurer le nombre de sources mentionnées dans les réponses et permettre d'évaluer leur diversité.
Cet indicateur aidera à distinguer une visibilité appuyée sur plusieurs références d'une présence dépendante d'une
source unique.

### Fréquence d'apparition

Le moteur devra suivre la fréquence à laquelle la marque, l'entité ou le site apparaît dans un ensemble de réponses
comparables. Les volumes et périmètres utilisés devront accompagner l'indicateur pour éviter toute interprétation hors
contexte.

### Évolution temporelle

Les captures devront être historisées afin d'observer les progressions, les baisses et les ruptures de visibilité. Les
comparaisons devront porter sur des prompts, fournisseurs et périmètres cohérents.

### Comparaison entre IA

La plateforme devra permettre de comparer la visibilité, les citations, le classement et les sources entre ChatGPT,
Gemini, Claude, Microsoft Copilot et Perplexity. Les écarts devront rester lisibles même lorsqu'un fournisseur ne
retourne pas toutes les informations disponibles chez un autre.

### Score GEO

Un score GEO consolidé devra synthétiser les signaux validés. Sa formule, son échelle, ses pondérations et le traitement
des données manquantes devront être documentés avant l'implémentation. Le score ne devra pas masquer les métriques
élémentaires ayant conduit au résultat.

### Enrichissement du Recommendation Engine

Les constats issus de GEO Intelligence devront pouvoir devenir des recommandations priorisées et actionnables. Le
Recommendation Engine restera l'unique responsable de leur normalisation transverse, de leur déduplication, de leur
priorisation et de leur cycle de vie.

## Architecture Backend

L'architecture cible respecte la séparation officielle des responsabilités :

```text
Routes
  ↓
GeoIntelligenceService
  ↓
GeoIntelligenceRepository
  ↓
GeoVisibilitySnapshot
```

- les **Routes** exposent les contrats HTTP, valident les entrées et délèguent les traitements ;
- `GeoIntelligenceService` porte les règles de normalisation, de consolidation, de scoring et de comparaison ;
- `GeoIntelligenceRepository` centralise les lectures et écritures liées aux captures de visibilité ;
- `GeoVisibilitySnapshot` représente une observation GEO historisée et rattachée à son contexte.

Les routes FastAPI ne devront contenir aucune logique métier. Elles ne devront ni calculer un score, ni comparer des
fournisseurs, ni produire directement des recommandations.

Les intégrations propres aux fournisseurs devront respecter les conventions des connecteurs existants. Aucun appel à
une IA externe ne devra être réalisé directement depuis une route.

## Architecture Desktop

Le client Desktop respectera le flux suivant :

```text
GeoIntelligencePage
  ↓
GeoIntelligenceService
  ↓
ApiClient
  ↓
REST API
```

- `GeoIntelligencePage` assurera uniquement l'affichage, la saisie des filtres et les interactions utilisateur ;
- le service Desktop adaptera les paramètres et les réponses de l'API pour l'interface ;
- `ApiClient` restera l'unique point d'accès HTTP du Desktop ;
- l'API REST restera l'unique accès aux données GEO Intelligence.

Le Desktop ne communiquera jamais directement avec PostgreSQL. Il ne devra pas non plus appeler directement ChatGPT,
Gemini, Claude, Microsoft Copilot, Perplexity ou toute autre API externe.

## Modèle métier

Le futur modèle principal est envisagé sous le nom `GeoVisibilitySnapshot`. Il représente une capture immuable ou
traçable de visibilité GEO pour un contexte donné.

| Champ | Rôle fonctionnel envisagé |
| --- | --- |
| `website` | Website suivi auquel la capture est rattachée. |
| `provider` | Fournisseur d'IA générative ayant produit la réponse analysée. |
| `prompt` | Prompt ou référence stable du prompt utilisé pour la mesure. |
| `entity` | Marque, organisation ou entité recherchée dans la réponse. |
| `visibility_score` | Mesure normalisée de la visibilité observée. |
| `citation_count` | Nombre de citations détectées dans la réponse. |
| `source_count` | Nombre de sources distinctes identifiées. |
| `ranking` | Position ou niveau de classement, lorsqu'il est disponible et comparable. |
| `answer_hash` | Empreinte stable de la réponse utilisée pour la traçabilité et la déduplication. |
| `captured_at` | Date et heure de la capture. |

Ce modèle reste volontairement générique afin de supporter plusieurs IA sans créer une table ou une architecture
différente pour chaque fournisseur. Les types, contraintes, relations, index et règles d'unicité définitifs devront être
confirmés pendant l'analyse technique.

Les réponses brutes, si leur conservation est retenue, devront faire l'objet de règles explicites concernant la
sécurité, la confidentialité, la durée de conservation et le volume de stockage.

## Endpoints prévus

Les endpoints suivants sont prévus pour le Sprint 38 :

| Méthode | Endpoint | Objectif prévu |
| --- | --- | --- |
| `GET` | `/api/v1/geo-intelligence` | Lister les captures ou résultats consolidés avec filtres et pagination. |
| `GET` | `/api/v1/geo-intelligence/summary` | Retourner les KPI GEO consolidés. |
| `GET` | `/api/v1/geo-intelligence/providers` | Présenter les fournisseurs disponibles et leur état fonctionnel. |
| `GET` | `/api/v1/geo-intelligence/history` | Restituer l'évolution temporelle des indicateurs. |
| `POST` | `/api/v1/geo-intelligence/import` | Importer ou déclencher l'intégration contrôlée de nouvelles observations. |

Les routes statiques telles que `/summary`, `/providers` et `/history` devront être déclarées avant toute éventuelle
route dynamique susceptible de les capturer. Les formats, filtres, tris, limites de pagination et comportements de
`/import` devront être validés avant l'implémentation.

## Permissions

Le module prévoit les permissions suivantes :

- `geo.read` : consulter les captures, synthèses, fournisseurs et historiques GEO Intelligence ;
- `geo.write` : importer ou déclencher les traitements autorisés et modifier les données lorsque le contrat le permet.

Le rattachement de ces permissions aux rôles existants devra suivre le système d'autorisations officiel. Aucune route
ne devra contourner les contrôles d'accès existants.

## Intégration avec Dashboard V2

Dashboard V2 devra consommer les données déjà consolidées par `GeoIntelligenceService`. Il pourra notamment présenter
des KPI de visibilité, des tendances, des comparaisons entre IA, des pertes de citations et des indicateurs de synthèse
par Website.

Dashboard V2 ne calculera aucun score GEO, ne normalisera aucune réponse fournisseur et ne portera aucune règle de
comparaison. Il restera une couche de restitution et de navigation transverse.

L'intégration devra préserver les endpoints, KPI, tendances et contrats existants qui ne concernent pas GEO
Intelligence.

## Intégration avec Recommendation Engine

GEO Intelligence deviendra une source canonique de recommandations automatiques. Les observations pertinentes seront
transmises au Recommendation Engine avec un Website, un fournisseur, une règle identifiable, un objet source stable et
les facteurs nécessaires à l'explication de la priorité.

Les recommandations envisageables comprennent notamment :

- une faible visibilité sur ChatGPT ;
- une baisse de visibilité sur Gemini ;
- une absence de présence dans Microsoft Copilot ;
- une perte de citations entre deux périodes comparables ;
- une diversité insuffisante des sources citées.

Ces exemples ne fixent pas encore les seuils. Toute règle devra préciser son périmètre, sa période de référence, le
volume minimal nécessaire et son comportement en présence de données partielles.

Le Recommendation Engine restera l'unique responsable de la déduplication, de la priorité, du score de classement et
du cycle de vie. GEO Intelligence ne devra pas créer un second moteur concurrent.

## Migration prévue

La future migration est prévue sous le nom :

```text
20260720_0016_create_geo_visibility_snapshots.py
```

Elle devra prolonger explicitement la chaîne Alembic existante et créer uniquement les structures validées pendant
l'analyse technique. Les évolutions de schéma utiliseront exclusivement des migrations Alembic explicites, notamment :

- `op.create_table(...)` ;
- `op.create_index(...)`.

Les opérations inverses nécessaires au `downgrade` devront être explicites et ordonnées. L'application ne devra jamais
utiliser :

- `Base.metadata.create_all()` ;
- `Base.metadata.drop_all()`.

Aucune migration implicite ni création automatique de table au démarrage ne sera autorisée.

## Tests prévus

L'implémentation future devra prévoir des tests ciblés couvrant au minimum :

- le modèle `GeoVisibilitySnapshot` et ses contraintes ;
- `GeoIntelligenceRepository` ;
- les règles de `GeoIntelligenceService` ;
- les routes REST et leurs contrats de réponse ;
- les permissions `geo.read` et `geo.write` ;
- la pagination et les tris autorisés ;
- les filtres par Website, fournisseur, entité, prompt et période ;
- les données absentes, partielles ou non comparables ;
- la déduplication au moyen de `answer_hash` et des identifiants métier validés ;
- l'intégration avec le Recommendation Engine ;
- l'alimentation de Dashboard V2 ;
- le service et la page Desktop ;
- les appels Desktop avec `MockTransport` ;
- les cas d'erreur, d'autorisation insuffisante et d'indisponibilité du backend.

Les tests ne devront appeler aucune IA réelle. Les réponses fournisseurs devront être simulées par des fixtures ou des
doubles de test déterministes.

## Résultat attendu

Une fois développé et validé, le Sprint 38 devra permettre de :

- conserver des captures GEO multi-IA homogènes et historisées ;
- consulter la visibilité d'un Website ou d'une entité par fournisseur ;
- mesurer les citations, les sources, la fréquence d'apparition et le classement disponible ;
- comparer les résultats entre IA et entre périodes cohérentes ;
- produire un score GEO explicable à partir de facteurs visibles ;
- alimenter Dashboard V2 avec des indicateurs consolidés ;
- générer des signaux actionnables pour le Recommendation Engine ;
- intégrer de nouveaux fournisseurs sans refactor global.

Le résultat devra respecter l'architecture en couches, les permissions, les conventions REST, la pagination commune et
les exigences de qualité du projet.

## Conclusion

Le Sprint 38 constitue la première brique de la plateforme GEO multi-IA de la Version 1.1. Il doit transformer des
observations dispersées en données comparables, historisées et utiles au pilotage, tout en préservant la responsabilité
de chaque couche.

En s'appuyant sur le Recommendation Engine et Dashboard V2 sans dupliquer leur logique, GEO Intelligence préparera une
plateforme extensible capable de suivre durablement la visibilité des marques dans les principaux moteurs d'IA
générative.
