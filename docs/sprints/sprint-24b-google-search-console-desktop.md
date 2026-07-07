# Sprint 24B — Google Search Console Desktop

## 1. Objectif

Le Sprint 24B consiste à intégrer Google Search Console dans l'application Desktop de la plateforme Veille SEO-GEO Groupe A.P&Partner.

Cette intégration s'appuie exclusivement sur le backend Google Search Console livré au Sprint 24A. Le Desktop agit uniquement comme une interface de consultation et de déclenchement d'actions exposées par l'API REST.

Contraintes obligatoires :

- le Desktop consomme exclusivement l'API REST du backend ;
- aucune communication directe avec Google Search Console n'est autorisée ;
- aucun accès direct à PostgreSQL n'est autorisé ;
- aucun accès direct à SQLAlchemy n'est autorisé ;
- toute la logique métier reste côté backend.

Le Sprint 24B ne doit donc pas recréer de logique Google Search Console côté Desktop. Il doit uniquement permettre à l'utilisateur de consulter les données disponibles via l'API et de déclencher les imports exposés par le backend.

## 2. Architecture Desktop

L'architecture Desktop obligatoire suit le flux suivant :

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

- la page affiche les données, les filtres, les boutons et les états utilisateur ;
- le service Desktop centralise les appels REST liés à Google Search Console ;
- `ApiClient` reste le client HTTP commun déjà présent dans le projet ;
- l'API REST FastAPI reste le seul point d'entrée vers les données Google Search Console.

Le Desktop ne contient aucune logique métier. Il ne calcule pas les métriques, ne transforme pas les règles métier, ne décide pas des statuts d'import et ne communique jamais avec Google Search Console ou PostgreSQL.

## 3. Fonctionnalités

Le Sprint 24B prévoit les fonctionnalités Desktop suivantes.

### Consultation des propriétés

La page Desktop doit permettre de consulter les propriétés Google Search Console connues du backend.

Informations affichées :

- URL ;
- type ;
- état ;
- dernière synchronisation.

Le Desktop se limite à afficher les propriétés retournées par l'API REST. La détection, l'association et l'état métier des propriétés restent gérés côté backend.

### Consultation des performances

La page Desktop doit permettre de consulter les performances Google Search Console exposées par le backend.

Métriques affichées :

- clics ;
- impressions ;
- CTR ;
- position moyenne.

Filtres prévus :

- propriété ;
- période ;
- page ;
- requête ;
- pays ;
- appareil.

Le Desktop transmet les filtres à l'API REST et affiche la réponse. Il ne réalise aucun calcul métier, aucune agrégation locale et aucune correction de données.

### Consultation de l'indexation

La page Desktop doit permettre de consulter les informations d'indexation disponibles via le backend.

Informations affichées :

- pages valides ;
- pages exclues ;
- erreurs ;
- avertissements.

Le Desktop ne classe pas lui-même les statuts d'indexation. Les catégories et les règles d'interprétation restent côté backend.

### Consultation des sitemaps

La page Desktop doit permettre de consulter les sitemaps associés aux propriétés suivies.

Informations affichées :

- URL ;
- état ;
- dernière lecture ;
- nombre d'URL.

Le Desktop affiche uniquement les données renvoyées par l'API REST.

### Import manuel

Le Sprint 24B prévoit un bouton d'import manuel côté Desktop.

Fonctionnement obligatoire :

- l'utilisateur déclenche l'action depuis le Desktop ;
- le Desktop appelle uniquement l'endpoint REST prévu par le backend ;
- le backend réalise l'import Google Search Console ;
- le Desktop affiche simplement le résultat retourné par l'API.

Le Desktop ne lance aucun appel Google direct, ne manipule aucun jeton Google et ne réalise aucun traitement d'import local.

### Historique des imports

La page Desktop doit permettre de consulter l'historique des imports Google Search Console.

Informations affichées :

- date ;
- durée ;
- statut ;
- nombre d'éléments importés ;
- erreurs éventuelles.

L'historique est fourni par le backend. Le Desktop n'interprète pas les erreurs au-delà de leur affichage utilisateur.

## 4. Architecture des classes Desktop

### GSCPage

`GSCPage` est responsable uniquement de l'interface utilisateur.

Responsabilités :

- affichage des données ;
- tableaux ;
- filtres ;
- boutons ;
- états de chargement ;
- messages d'erreur.

`GSCPage` ne contient aucune logique métier. Elle ne communique pas directement avec l'API REST et ne réalise aucun calcul lié à Google Search Console.

### GSCService

`GSCService` est responsable de la couche d'accès REST Google Search Console côté Desktop.

Responsabilités :

- appels REST ;
- transmission des filtres ;
- normalisation des réponses pour la page ;
- remontée des erreurs.

`GSCService` ne contient aucune logique métier. Il ne décide pas des règles d'import, ne calcule pas les métriques et ne communique jamais avec Google Search Console, PostgreSQL ou SQLAlchemy.

### ApiClient

Le Sprint 24B doit réutiliser le client HTTP existant.

Contraintes :

- ne pas créer de nouveau client HTTP ;
- centraliser les appels via `desktop/core/api_client.py` ;
- conserver les mécanismes existants d'authentification, d'erreurs et de configuration ;
- modifier `ApiClient` uniquement si le besoin est confirmé par l'intégration.

## 5. Intégration Dashboard

Le Dashboard pourra progressivement exploiter les données Google Search Console exposées par le backend.

Premières métriques prévues :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- dernière synchronisation.

Le Dashboard ne lance jamais d'import Google Search Console. Les imports restent déclenchés depuis le module dédié ou par les mécanismes backend prévus.

## 6. Fichiers prévus

Futurs fichiers prévus pour l'implémentation du Sprint 24B, à ne pas créer dans ce document :

- `desktop/services/gsc_service.py`
- `desktop/ui/gsc_page.py`
- `tests/desktop/test_gsc_service.py`

## 7. Fichiers qui seront modifiés

Fichiers susceptibles d'être modifiés lors de l'implémentation future du Sprint 24B :

- `desktop/ui/main_window.py`
- `desktop/core/constants.py`
- `desktop/core/api_client.py` uniquement si nécessaire

## 8. Tests prévus

Les tests prévus pour l'implémentation future devront couvrir :

- récupération des propriétés ;
- récupération des performances ;
- récupération de l'indexation ;
- récupération des sitemaps ;
- import manuel ;
- erreurs HTTP ;
- erreurs réseau.

Contraintes de test :

- utiliser exclusivement `httpx.MockTransport` ;
- ne réaliser aucun appel Internet ;
- ne pas appeler Google Search Console ;
- ne pas accéder à PostgreSQL ;
- tester le comportement du service Desktop face aux réponses REST simulées.

## 9. Hors périmètre

Le Sprint 24B ne comprend pas :

- OAuth Desktop ;
- authentification Google ;
- appels directs Google ;
- accès PostgreSQL ;
- modification du backend GSC ;
- Dashboard complexe ;
- Google Analytics ;
- Bing Webmaster Tools.

## 10. Contraintes

Contraintes techniques et architecturales obligatoires :

- PySide6 ;
- httpx ;
- architecture `Page → Service → ApiClient → API REST` ;
- aucune logique métier dans la page ;
- aucune logique métier dans le service ;
- aucune communication directe avec Google Search Console ;
- aucune communication directe avec PostgreSQL ;
- réutilisation du client HTTP existant ;
- séparation stricte entre Desktop, API REST, backend métier et persistance.

## 11. Conclusion

Le Sprint 24B constitue la première intégration Desktop de Google Search Console dans la plateforme Veille SEO-GEO Groupe A.P&Partner.

Il exploitera exclusivement le backend développé au Sprint 24A et préparera l'affichage des données Google Search Console dans l'application Desktop sans introduire de logique métier côté interface.

Ce sprint prépare les futurs développements :

- Sprint 25 — Google Analytics 4 Backend ;
- Sprint 26 — Google Analytics 4 Desktop ;
- Sprint 27 — Bing Webmaster Tools.
