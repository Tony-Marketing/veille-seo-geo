# Sprint 24A - Google Search Console Backend

## 1. Objectif Du Sprint

Le Sprint 24A construit le socle backend Google Search Console de la plateforme Veille SEO-GEO Groupe A.P&Partner.

Ce sprint ajoute les fondations permettant de connecter, stocker et consulter des donnees GSC sans modifier le Dashboard
Desktop du Sprint 23.

Objectifs principaux :

- preparer OAuth Google Search Console ;
- stocker les proprietes GSC ;
- importer les performances ;
- stocker clics, impressions, CTR et position moyenne ;
- stocker couverture, indexation et sitemaps ;
- exposer une API REST backend ;
- garantir des imports idempotents ;
- permettre les tests sans Internet via connecteur mockable ;
- preparer Sprint 24B pour l'interface Desktop GSC.

## 2. Hors Perimetre

Sont exclus du Sprint 24A :

- interface Desktop GSC ;
- integration au Dashboard Sprint 23 ;
- appels Google obligatoires en environnement de test ;
- connecteur Google production complet ;
- integration GA4 ;
- integration Bing Webmaster Tools ;
- exports de rapports.

Le Dashboard reste une couche de restitution et ne lance aucun import GSC.

## 3. Architecture Backend

Architecture respectee :

```text
Routes GSC
    -> GoogleSearchConsoleService
        -> GoogleSearchConsoleRepository
            -> Models GSC
```

Le moteur d'import est separe :

```text
GoogleSearchConsoleImportService
    -> GscDataRepository
    -> GoogleSearchConsoleClient
```

Le connecteur `GoogleSearchConsoleClient` ne fait aucun appel reseau dans cette V1. Il sert de frontiere mockable pour
les tests et pour une future implementation Google reelle.

## 4. OAuth

OAuth est preparatoire.

Parametres de configuration :

- `google_oauth_client_id` ;
- `google_oauth_client_secret` ;
- `google_oauth_redirect_uri` ;
- `google_search_console_scopes`.

Aucun secret n'est code en dur.

Le projet possede deja `encrypt_secret`, utilise pour stocker les tokens OAuth.

Flux cible :

```text
GET /api/v1/gsc/oauth/authorization-url
    -> construit une URL OAuth preparatoire

POST /api/v1/gsc/oauth/callback
    -> echange mockable du code
    -> stockage des tokens chiffres
    -> statut ACTIVE
```

## 5. Modele De Donnees

Tables ajoutees :

| Table | Role |
| --- | --- |
| `gsc_oauth_credentials` | Credentials OAuth et tokens chiffres. |
| `gsc_properties` | Proprietes GSC suivies. |
| `gsc_import_runs` | Historique des imports. |
| `gsc_performance_daily` | Performances par date et dimensions. |
| `gsc_coverage_snapshots` | Couverture et indexation agregee. |
| `gsc_indexing_inspections` | Inspection d'indexation par URL. |
| `gsc_sitemaps` | Sitemaps connus par propriete. |

## 6. Idempotence

Les imports sont idempotents.

Contraintes uniques principales :

- performance : propriete, date, page, query, device, country, search type ;
- couverture : propriete, date, categorie, etat ;
- indexation : propriete, URL inspectee, date d'inspection ;
- sitemap : propriete, URL du sitemap ;
- propriete : site URL.

Relancer un import met a jour les lignes existantes au lieu de creer des doublons.

## 7. API REST

Endpoints livres :

```text
GET    /api/v1/gsc/properties
POST   /api/v1/gsc/properties/sync
GET    /api/v1/gsc/properties/{property_id}
GET    /api/v1/gsc/properties/{property_id}/performance
GET    /api/v1/gsc/properties/{property_id}/coverage
GET    /api/v1/gsc/properties/{property_id}/indexing
GET    /api/v1/gsc/properties/{property_id}/sitemaps
POST   /api/v1/gsc/import-runs
GET    /api/v1/gsc/import-runs
GET    /api/v1/gsc/import-runs/{import_run_id}
GET    /api/v1/gsc/oauth/status
GET    /api/v1/gsc/oauth/authorization-url
POST   /api/v1/gsc/oauth/callback
DELETE /api/v1/gsc/oauth/credentials/{credential_id}
```

Les routes ne contiennent aucune logique metier.

## 8. Tests

Les tests utilisent des clients GSC factices.

Aucun test ne depend d'Internet.

Couverture attendue :

- modeles SQLAlchemy ;
- repositories et idempotence ;
- services OAuth et proprietes ;
- service d'import ;
- routes API et permissions.

## 9. Perspectives Sprint 24B

Sprint 24B exploitera cette API pour :

- ajouter une interface Desktop GSC ;
- consulter les proprietes ;
- lancer des imports ;
- afficher performances, couverture, indexation et sitemaps ;
- rapprocher GSC avec SEO et GEO ;
- integrer GSC au Dashboard.

Sprint 24B ne devra pas contourner l'API REST et ne devra pas acceder directement a PostgreSQL.

## 10. Evolutions Futures

L'architecture retenue prepare :

- un connecteur Google Search Console reel ;
- Google Analytics 4 ;
- Bing Webmaster Tools ;
- imports planifies ;
- rapprochement SEO / GEO / GSC ;
- rapports Sprint 26.

Chaque futur connecteur devra conserver le meme principe :

```text
Service d'import
    -> Repository
    -> Connecteur injectable
```
