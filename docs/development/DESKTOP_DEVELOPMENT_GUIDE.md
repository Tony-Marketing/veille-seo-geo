# Guide de développement Desktop PySide6 - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit les règles de développement Desktop du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence pour créer, modifier, tester et relire les évolutions de l'application Desktop PySide6 sans casser le découplage avec le backend FastAPI.

Le guide couvre :

- l'organisation des vues PySide6 ;
- la consommation de l'API FastAPI via HTTP REST ;
- la gestion des appels `httpx` ;
- l'authentification côté Desktop ;
- les erreurs API ;
- la pagination, le filtrage, le tri et la recherche ;
- les futures vues SEO, GEO, contenus, mots-clés, concurrents, rapports et configuration ;
- les tests Desktop ;
- les interventions assistées par Codex.

## 2. Périmètre du guide Desktop

Le guide s'applique principalement à :

```text
desktop/
  app.py
  main.py
  core/
  ui/
  widgets/
  styles/
  resources/
tests/
docs/architecture/DESKTOP_ARCHITECTURE.md
```

Il concerne aussi les contrats API documentés dans :

```text
docs/api/AUTHENTICATION.md
docs/api/ERROR_HANDLING.md
docs/api/PAGINATION.md
docs/api/FILTERING.md
```

Le guide ne remplace pas le backend. Le Desktop est un client graphique de l'API.

## 3. Stack Desktop officielle

| Domaine | Technologie |
| --- | --- |
| Langage | Python 3.13 |
| Interface | PySide6 |
| HTTP | httpx |
| API consommée | FastAPI HTTP REST |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.x |
| Base | PostgreSQL via backend uniquement |
| Tests | Pytest |
| Linting | Ruff |
| Design | UI moderne inspirée Windows 11 |
| Frontend futur | React + TypeScript, séparé du Desktop |

Toute dépendance Desktop supplémentaire doit être justifiée avant ajout.

## 4. Rôle du Desktop dans le projet

Le Desktop est une interface interne de pilotage.

Il doit :

- afficher les données métier ;
- déclencher des actions utilisateur ;
- appeler l'API FastAPI ;
- présenter les erreurs clairement ;
- respecter l'authentification API ;
- rester réactif ;
- préserver la cohérence UX ;
- évoluer sans bloquer le futur frontend React.

Il ne doit pas porter les règles métier principales.

## 5. Principe fondamental : Desktop -> FastAPI -> PostgreSQL

Flux obligatoire :

```text
Desktop PySide6
    |
    | HTTP REST via httpx
    v
API FastAPI
    |
    v
Services métier
    |
    v
Repositories SQLAlchemy
    |
    v
PostgreSQL
```

Le Desktop ne connaît pas la structure interne de PostgreSQL. Il consomme uniquement des contrats API.

## 6. Interdiction d'accès direct du Desktop à PostgreSQL

Interdit côté Desktop :

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://...")
```

Raisons :

- contournement de l'API ;
- contournement de l'authentification ;
- duplication des règles métier ;
- exposition potentielle de secrets ;
- couplage fort à la base ;
- incompatibilité avec le futur React.

Le Desktop ne doit jamais recevoir d'URL de connexion PostgreSQL.

## 7. Interdiction d'importer les modèles SQLAlchemy côté Desktop

Interdit :

```python
from backend.app.models.website import Website
```

Le Desktop ne doit pas importer :

- modèles SQLAlchemy ;
- repositories backend ;
- services métier backend ;
- dépendances FastAPI ;
- configuration base backend.

Le Desktop peut définir des structures locales légères si nécessaire, mais elles doivent représenter des données d'API, pas des tables.

## 8. Interdiction de contourner l'API

Le Desktop ne doit pas contourner les routes API.

Interdits :

- appel direct aux services backend ;
- import direct des repositories ;
- lecture directe de fichiers backend internes ;
- accès direct PostgreSQL ;
- simulation locale de permissions backend.

Chaque action métier doit passer par un endpoint FastAPI.

## 9. Relation avec le backend FastAPI

Le backend est la source de vérité.

Le Desktop dépend du backend pour :

- authentification ;
- autorisation ;
- données ;
- validation métier ;
- pagination ;
- filtrage ;
- erreurs standardisées ;
- actions admin ;
- imports/exports de configuration.

Le Desktop doit traiter l'API comme un contrat stable, pas comme une implémentation interne.

## 10. Relation avec le futur frontend React

Le Desktop et le futur frontend React doivent consommer la même API.

Règles :

- ne pas créer d'endpoint uniquement utilisable par le Desktop sans justification ;
- garder des réponses API génériques ;
- éviter les formats couplés à PySide6 ;
- documenter les contrats API ;
- ne pas déplacer la logique métier dans le Desktop.

Une bonne intégration Desktop doit faciliter l'arrivée de React.

## 11. Architecture recommandée côté Desktop

Architecture recommandée :

```text
main.py / app.py
    |
    v
MainWindow
    |
    v
Pages UI
    |
    v
Services Desktop si nécessaires
    |
    v
ApiClient centralisé
    |
    v
FastAPI HTTP REST
```

Le niveau "services Desktop" est recommandé lorsque la logique d'orchestration UI devient significative. Il ne doit pas remplacer les services métier backend.

## 12. Organisation recommandée des dossiers Desktop

Organisation actuelle à préserver :

| Dossier | Rôle |
| --- | --- |
| `desktop/core/` | configuration, constantes, client API |
| `desktop/ui/` | pages et fenêtres principales |
| `desktop/widgets/` | composants réutilisables |
| `desktop/styles/` | styles QSS |
| `desktop/resources/` | icônes, logos et ressources |

À prévoir seulement si nécessaire :

| Dossier futur possible | Usage |
| --- | --- |
| `desktop/services/` | orchestration UI locale |
| `desktop/models/` | structures de données Desktop non SQLAlchemy |
| `desktop/workers/` | tâches Qt non bloquantes |
| `tests/desktop/` | tests dédiés Desktop |

Ces ajouts doivent être validés lors de l'implémentation.

## 13. Rôle des fenêtres principales

Les fenêtres principales orchestrent :

- navigation ;
- zones globales ;
- instanciation des pages ;
- partage du client API ;
- statut global ;
- shell visuel.

Dans le projet, `MainWindow` joue ce rôle.

Elle ne doit pas :

- contenir toutes les règles métier ;
- faire des requêtes spécifiques à chaque module si les pages peuvent le faire ;
- gérer les détails de parsing de chaque réponse ;
- stocker des secrets en clair.

## 14. Rôle des widgets

Les widgets sont des composants réutilisables.

Exemples :

- sidebar ;
- topbar ;
- statusbar ;
- composant de pagination ;
- message d'erreur ;
- table générique ;
- sélecteur de site.

Un widget doit rester centré sur l'affichage et l'interaction locale.

## 15. Rôle des services Desktop

Un service Desktop peut être ajouté si une page devient trop complexe.

Rôle recommandé :

- préparer les paramètres API ;
- normaliser une réponse pour l'UI ;
- coordonner plusieurs appels API ;
- isoler une logique UI réutilisable ;
- faciliter les tests.

Il ne doit pas :

- appliquer les règles métier backend ;
- accéder à PostgreSQL ;
- contourner les endpoints ;
- décider des permissions réelles.

## 16. Rôle du client API Desktop

Le client API centralise les appels HTTP.

Responsabilités :

- construire les URLs ;
- appliquer le timeout ;
- ajouter les headers d'authentification si disponibles ;
- normaliser les erreurs ;
- parser les réponses JSON ;
- éviter la duplication des appels `httpx`.

Le projet dispose déjà d'un client API dans `desktop/core/api_client.py`.

## 17. Rôle des modèles de données côté Desktop, si nécessaires

Des modèles Desktop peuvent être prévus pour représenter des réponses API.

Ils doivent :

- rester locaux au Desktop ;
- ne pas hériter de modèles SQLAlchemy ;
- ne pas représenter directement des tables ;
- faciliter l'affichage ;
- rester compatibles avec les schemas API.

Exemple conceptuel :

```python
@dataclass
class WebsiteRow:
    name: str
    url: str
    is_active: bool
```

À valider lors de l'implémentation.

## 18. Rôle de la configuration Desktop

La configuration Desktop contient :

- nom de l'application ;
- version ;
- URL de base API ;
- timeout HTTP ;
- paramètres d'environnement.

Règles :

- pas de mot de passe en dur ;
- pas de token en dur ;
- pas de clé API ;
- URL API configurable selon environnement ;
- valeurs par défaut adaptées au développement local.

## 19. Rôle de la gestion d'état

L'état Desktop doit rester compréhensible.

Exemples d'état :

- utilisateur connecté ;
- token temporaire ;
- site sélectionné ;
- filtres actifs ;
- page courante ;
- état de chargement ;
- message d'erreur.

Règles :

- éviter les variables globales mutables ;
- centraliser les états partagés importants ;
- garder les états locaux dans les pages lorsque possible ;
- ne pas stocker de données sensibles inutilement.

## 20. Rôle de la gestion d'erreurs

Le Desktop doit transformer les erreurs techniques en messages utilisateur.

Objectifs :

- expliquer l'erreur sans exposer de détail sensible ;
- proposer une action lorsque possible ;
- distinguer erreur API, erreur réseau et réponse inattendue ;
- éviter les crashs UI ;
- préserver un état cohérent.

Les erreurs doivent être affichées dans la page ou un composant dédié.

## 21. Rôle de la journalisation

La journalisation Desktop sert au diagnostic.

Elle peut contenir :

- endpoint appelé ;
- statut HTTP ;
- durée approximative ;
- type d'erreur ;
- `request_id` si fourni.

Elle ne doit jamais contenir :

- mot de passe ;
- token ;
- clé API ;
- secret ;
- payload sensible complet.

## 22. Cycle de développement Desktop recommandé

Cycle recommandé :

```text
comprendre le besoin utilisateur
   |
   v
identifier endpoint API nécessaire
   |
   v
vérifier contrat API
   |
   v
créer ou modifier page/widget/service Desktop
   |
   v
centraliser l'appel dans ApiClient ou service Desktop
   |
   v
gérer chargement, vide, erreur, succès
   |
   v
tester manuellement et avec Pytest si possible
   |
   v
relire diff et sécurité
```

Commandes initiales :

```powershell
git branch --show-current
git status --short
```

## 23. Création d'une vue Desktop

Une vue Desktop doit :

- être placée dans `desktop/ui/` ;
- hériter d'un widget PySide6 adapté ;
- recevoir les dépendances utiles ;
- exposer des méthodes claires ;
- gérer chargement, vide, erreur et succès ;
- éviter la logique métier backend.

Exemple de nom :

```text
geo_results_page.py
```

Classe :

```text
GeoResultsPage
```

## 24. Création d'un composant PySide6

Un composant réutilisable doit être placé dans `desktop/widgets/`.

Exemples :

- `PaginationControls` ;
- `ErrorBanner` ;
- `SiteSelector` ;
- `LoadingPanel` ;
- `ConfirmDialog`.

Règles :

- API de composant claire ;
- signaux Qt si interaction ;
- pas d'appel API direct sauf composant explicitement dédié ;
- style cohérent avec QSS existant.

## 25. Création d'un service Desktop

Un service Desktop est utile lorsque plusieurs vues partagent une orchestration.

Exemple conceptuel :

```python
class WebsiteDesktopService:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_websites(self, page: int, page_size: int) -> dict[str, object]:
        return self.api_client.get("/websites", params={"page": page, "page_size": page_size})
```

Le service Desktop ne remplace pas le service métier backend.

## 26. Création d'un appel API avec `httpx`

Les appels `httpx` doivent être centralisés autant que possible.

Exemple conceptuel :

```python
with httpx.Client(timeout=10.0) as client:
    response = client.get(f"{base_url}/websites", params={"page": 1})
    response.raise_for_status()
    payload = response.json()
```

Dans le projet, privilégier le client API existant plutôt que des appels dispersés dans chaque page.

## 27. Création d'un écran de liste

Un écran de liste doit gérer :

- chargement ;
- pagination ;
- filtrage ;
- tri ;
- recherche ;
- liste vide ;
- erreur API ;
- action de rafraîchissement.

Il doit éviter de charger des volumes trop importants sans pagination.

## 28. Création d'un écran de détail

Un écran de détail doit :

- charger une ressource par identifiant ;
- afficher les champs importants ;
- gérer `404` ;
- gérer les permissions ;
- proposer des actions cohérentes ;
- éviter d'exposer des champs sensibles.

Si une ressource n'existe plus, l'utilisateur doit pouvoir revenir à la liste.

## 29. Création d'un formulaire

Un formulaire doit :

- valider les champs côté UI ;
- afficher les erreurs API `422` ;
- désactiver l'action pendant l'envoi ;
- éviter les soumissions multiples ;
- afficher un succès clair ;
- ne pas masquer les erreurs métier `409`.

La validation UI améliore l'expérience, mais ne remplace jamais la validation backend.

## 30. Création d'une boîte de dialogue

Une boîte de dialogue doit être utilisée pour :

- confirmation ;
- choix court ;
- erreur bloquante ;
- formulaire léger ;
- action sensible.

Règles :

- texte clair ;
- action principale explicite ;
- annulation possible pour action sensible ;
- pas de secret affiché ;
- pas de suppression sans confirmation.

## 31. Création d'une table de données

Une table de données doit :

- avoir des colonnes nommées ;
- gérer les listes vides ;
- empêcher l'édition directe si non prévue ;
- supporter sélection de ligne si nécessaire ;
- rester lisible ;
- ne pas afficher de données sensibles inutiles.

Pour les grands volumes, utiliser pagination et filtres API.

## 32. Création d'un tableau de bord

Un tableau de bord doit afficher des indicateurs synthétiques.

Règles :

- appels API limités ;
- chargements non bloquants si possible ;
- erreurs partielles visibles ;
- données datées ;
- pas de calcul métier lourd côté Desktop ;
- actualisation maîtrisée.

Les calculs métier doivent être fournis par le backend.

## 33. Gestion du sélecteur de site

Le sélecteur de site est un composant transversal à prévoir.

Il doit :

- charger les sites via API ;
- afficher le site actif ;
- transmettre l'identifiant sélectionné aux pages ;
- gérer liste vide ;
- gérer erreur API ;
- ne pas stocker la sélection dans la base directement.

L'état sélectionné peut être conservé en mémoire Desktop ou dans une configuration locale non sensible.

## 34. Gestion des modules SEO

Les modules SEO Desktop doivent consommer les endpoints SEO.

Ils peuvent afficher :

- audits d'URL ;
- balises ;
- contenus ;
- positions ;
- Core Web Vitals ;
- maillage interne.

Règles :

- filtrer par site ;
- paginer les résultats ;
- afficher la date d'analyse ;
- ne pas recalculer lourdement côté UI ;
- laisser le backend porter les règles métier.

## 35. Gestion des modules GEO

Les modules GEO Desktop doivent rester extensibles.

Ils peuvent afficher :

- réponses IA ;
- citations de marque ;
- scores de visibilité ;
- fournisseurs IA ;
- modèles IA ;
- historique.

Règles :

- ne jamais stocker de clés API côté UI ;
- filtrer par fournisseur, modèle, période ou site ;
- gérer les volumes avec pagination ;
- afficher les erreurs fournisseur via messages standardisés ;
- ne pas coupler la vue à un seul modèle IA.

## 36. Gestion des mots-clés

Les vues mots-clés doivent :

- afficher les listes paginées ;
- permettre recherche et filtrage ;
- gérer les imports si l'API les propose ;
- afficher les erreurs de validation ;
- éviter les doublons côté UI lorsque possible ;
- déléguer la validation finale au backend.

Les exports doivent passer par des endpoints dédiés.

## 37. Gestion des contenus

Les vues contenus peuvent couvrir :

- pages ;
- articles ;
- métadonnées ;
- score qualité ;
- recommandations ;
- liens internes.

Règles :

- éviter les vues trop lourdes ;
- charger les détails à la demande ;
- ne pas exposer de données sensibles ;
- différencier brouillon, publié et archivé si l'API le fournit.

## 38. Gestion des concurrents

Les vues concurrents doivent :

- rattacher les concurrents à un site ou marché ;
- afficher les comparaisons ;
- gérer les doublons ;
- paginer les historiques ;
- protéger les données stratégiques via permissions backend.

Le Desktop ne décide pas seul des droits d'accès.

## 39. Gestion des rapports

Les vues rapports doivent :

- lister les rapports ;
- filtrer par période ou site ;
- afficher le statut de génération ;
- télécharger ou ouvrir un rapport si endpoint disponible ;
- gérer traitements longs via statut ;
- éviter de bloquer l'interface.

Pour un rapport volumineux, prévoir une expérience asynchrone si le backend le permet.

## 40. Gestion de la configuration

Les vues configuration doivent être prudentes.

Règles :

- afficher uniquement les paramètres autorisés ;
- masquer les secrets ;
- confirmer les changements sensibles ;
- gérer imports/exports non destructifs ;
- montrer un rapport de validation ;
- respecter les permissions backend.

Un export ne doit pas contenir de secret en clair sauf mécanisme explicitement validé.

## 41. Gestion de l'administration

Les vues administration sont sensibles.

Elles doivent :

- exiger une session valide ;
- respecter les permissions backend ;
- afficher clairement les actions ;
- demander confirmation pour actions sensibles ;
- journaliser côté backend si prévu ;
- ne pas simuler des droits côté Desktop.

Le Desktop peut masquer des boutons selon les droits connus, mais le backend doit rester l'autorité.

## 42. Authentification côté Desktop

Le Desktop doit suivre le mécanisme exposé par l'API.

Règles :

- formulaire de connexion dédié ;
- envoi des identifiants via HTTPS en production ;
- stockage prudent du token ;
- ajout du token dans les headers ;
- gestion de session expirée ;
- déconnexion explicite.

Le Desktop ne doit pas inventer un système d'authentification parallèle.

## 43. Stockage temporaire ou sécurisé des tokens

Recommandé :

- garder le token en mémoire si possible ;
- utiliser un stockage sécurisé si persistance nécessaire ;
- ne jamais écrire le token en clair dans un fichier ;
- ne jamais logger le token ;
- supprimer le token à la déconnexion.

À éviter :

```python
Path("token.txt").write_text(access_token)
```

Tout stockage persistant doit être validé avant implémentation.

## 44. Déconnexion côté Desktop

La déconnexion doit :

- supprimer le token local ;
- nettoyer l'état utilisateur ;
- revenir à l'écran de connexion ;
- annuler ou ignorer les requêtes en cours si nécessaire ;
- éviter de conserver des données sensibles en mémoire plus longtemps que nécessaire.

Si l'API fournit un endpoint de révocation, l'utiliser selon le contrat backend.

## 45. Expiration de session

Quand une session expire :

- afficher un message clair ;
- rediriger vers la connexion ;
- ne pas répéter indéfiniment les requêtes ;
- préserver si possible le contexte non sensible ;
- ne pas masquer une erreur `401`.

L'expiration doit être traitée de manière centralisée dans le client API ou un gestionnaire d'état.

## 46. Rafraîchissement de session ou de jeton, si prévu

Le rafraîchissement de jeton doit être utilisé uniquement si l'API le prévoit.

Règles :

- centraliser le mécanisme ;
- éviter les boucles infinies ;
- protéger le refresh token ;
- gérer l'échec de rafraîchissement ;
- documenter le comportement.

Si aucun refresh token n'est prévu, demander une reconnexion.

## 47. Gestion des erreurs 401

`401 Unauthorized` signifie que l'utilisateur n'est pas authentifié ou que la session n'est plus valide.

Action Desktop recommandée :

- supprimer le token local ;
- afficher un message de session expirée ;
- rediriger vers la connexion ;
- ne pas réessayer sans authentification.

## 48. Gestion des erreurs 403

`403 Forbidden` signifie que l'utilisateur est authentifié mais non autorisé.

Action Desktop recommandée :

- afficher un message d'accès refusé ;
- ne pas masquer l'erreur comme une indisponibilité API ;
- désactiver ou masquer l'action si les droits connus le permettent ;
- laisser le backend décider réellement.

## 49. Gestion des erreurs 404

`404 Not Found` signifie que la ressource est introuvable.

Action Desktop recommandée :

- afficher "ressource introuvable" ;
- proposer retour liste ;
- rafraîchir si la ressource a pu être supprimée ;
- ne pas créer localement une ressource de remplacement.

## 50. Gestion des erreurs 409

`409 Conflict` indique un conflit métier.

Exemples :

- doublon ;
- état incompatible ;
- action déjà réalisée ;
- ressource modifiée.

Action Desktop recommandée :

- afficher le message API ;
- conserver les données saisies ;
- proposer correction ou rafraîchissement ;
- ne pas forcer l'action.

## 51. Gestion des erreurs 422

`422 Unprocessable Entity` indique une validation FastAPI/Pydantic.

Action Desktop recommandée :

- afficher les champs invalides si l'API les fournit ;
- conserver le formulaire ;
- mettre en évidence les champs concernés ;
- ne pas présenter cela comme une panne.

La validation UI doit réduire ces erreurs, mais le backend reste l'autorité.

## 52. Gestion des erreurs 429

`429 Too Many Requests` indique une limite de débit.

Action Desktop recommandée :

- afficher un message de limitation ;
- respecter `Retry-After` si fourni ;
- désactiver temporairement l'action ;
- éviter les retries agressifs.

## 53. Gestion des erreurs 500

`500 Internal Server Error` indique une erreur serveur.

Action Desktop recommandée :

- afficher un message sobre ;
- ne pas exposer de stack trace ;
- afficher le `request_id` si disponible ;
- proposer de réessayer ;
- journaliser sans secret.

## 54. Gestion des erreurs réseau

Les erreurs réseau couvrent :

- API indisponible ;
- DNS ;
- connexion refusée ;
- coupure réseau ;
- certificat invalide ;
- proxy mal configuré.

Action Desktop recommandée :

- afficher "API indisponible" ;
- proposer réessayer ;
- préserver l'état de la page ;
- ne pas perdre les saisies en cours.

## 55. Gestion des timeouts

Les timeouts doivent être explicites.

Règles :

- définir un timeout par défaut ;
- afficher un message clair ;
- ne pas bloquer l'interface ;
- éviter les retries infinis ;
- adapter le timeout pour exports ou rapports si l'API le justifie.

Exemple conceptuel :

```python
httpx.Client(timeout=10.0)
```

## 56. Gestion des indisponibilités API

Quand l'API est indisponible :

- indiquer l'état dans la barre de statut ;
- désactiver les actions dépendantes ;
- permettre une tentative de reconnexion ;
- ne pas vider inutilement toutes les données affichées ;
- distinguer panne API et absence de données.

Le dashboard peut afficher un statut de santé backend.

## 57. Gestion du mode dégradé

Un mode dégradé peut être prévu.

Exemples :

- affichage de dernière page consultée en mémoire ;
- désactivation des actions d'écriture ;
- message global d'indisponibilité ;
- navigation limitée.

À valider lors de l'implémentation :

- conservation locale ;
- durée de cache ;
- données sensibles ;
- règles de synchronisation.

## 58. Gestion des réponses API standardisées

Le Desktop doit s'adapter aux réponses standardisées.

Exemple de liste paginée :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0
}
```

Règles :

- valider la présence des champs attendus ;
- gérer les champs manquants ;
- afficher un message de réponse inattendue ;
- ne pas supposer que la réponse est toujours correcte.

## 59. Gestion des erreurs API standardisées

Exemple fréquent :

```json
{
  "detail": "Ressource introuvable."
}
```

Le Desktop doit :

- lire `detail` si disponible ;
- gérer les listes d'erreurs `422` ;
- préserver le statut HTTP ;
- éviter d'afficher des détails techniques non utiles ;
- afficher un message utilisateur clair.

## 60. Gestion du `request_id`

Si l'API fournit un `request_id`, le Desktop doit le conserver dans les messages de diagnostic.

Usage :

- affichage discret dans une erreur critique ;
- logs Desktop ;
- support technique ;
- corrélation avec logs backend.

Exemple de message :

```text
Erreur serveur. Référence : req_123456
```

Ne jamais fabriquer un `request_id` en remplacement de celui du backend pour une erreur serveur.

## 61. Pagination côté Desktop

La pagination Desktop doit utiliser les paramètres API.

Paramètres fréquents :

```text
page
page_size
```

Règles :

- ne pas charger toutes les données ;
- garder la page courante ;
- gérer première et dernière page ;
- rafraîchir après changement de filtre ;
- afficher total et page.

## 62. Filtrage côté Desktop

Le filtrage Desktop doit utiliser les filtres API documentés.

Règles :

- envoyer uniquement les champs supportés ;
- réinitialiser la pagination si le filtre change ;
- afficher les filtres actifs ;
- gérer absence de résultats ;
- éviter les requêtes à chaque frappe sans délai si l'API est sollicitée.

## 63. Tri côté Desktop

Le tri peut être local ou serveur selon le volume.

Recommandé :

- tri serveur pour grandes listes ;
- tri local seulement pour données déjà chargées et limitées ;
- paramètres `sort` et `order` si l'API les expose ;
- indicateur visuel de tri.

Ne pas simuler un tri global sur une seule page paginée si l'utilisateur attend un tri complet.

## 64. Recherche côté Desktop

La recherche doit être prévisible.

Règles :

- champ de recherche explicite ;
- déclenchement contrôlé ;
- debounce si recherche automatique ;
- message liste vide ;
- paramètre API documenté ;
- pas de filtrage local trompeur sur données partielles.

## 65. Gestion des listes vides

Une liste vide n'est pas une erreur.

Messages recommandés :

- "Aucun site trouvé."
- "Aucun rapport pour cette période."
- "Aucun concurrent enregistré."

La page doit rester utilisable et proposer les actions pertinentes.

## 66. Gestion des chargements

Les chargements doivent être visibles.

Règles :

- désactiver les boutons pendant l'action ;
- afficher un indicateur ou message ;
- éviter les doubles clics ;
- conserver le contexte ;
- réactiver les contrôles en fin d'appel.

Pour appels longs, utiliser worker ou tâche non bloquante.

## 67. Gestion des états d'erreur UI

Un état d'erreur UI doit être :

- visible ;
- compréhensible ;
- non technique ;
- récupérable si possible ;
- sans secret.

Ne pas afficher directement une exception Python complète à l'utilisateur.

## 68. Gestion des validations de formulaires

La validation côté Desktop doit améliorer l'expérience.

Exemples :

- champ obligatoire ;
- format URL ;
- longueur minimale ;
- valeur numérique positive ;
- date de début avant date de fin.

Le backend doit toujours refaire la validation.

## 69. Gestion des confirmations utilisateur

Les confirmations sont nécessaires pour :

- suppression ;
- désactivation ;
- import ;
- export sensible ;
- réinitialisation ;
- changement de configuration.

Une confirmation doit expliquer l'effet réel de l'action.

## 70. Gestion des actions destructrices

Une action destructrice doit être rare et contrôlée.

Règles :

- confirmation explicite ;
- permission backend ;
- message clair ;
- pas d'action par double-clic accidentel ;
- journalisation backend si prévue ;
- préférer désactivation logique si le domaine le permet.

Le Desktop ne doit pas contourner une protection backend.

## 71. Gestion des imports/exports de configuration côté Desktop

Les imports/exports doivent être prudents.

Règles :

- validation avant envoi ;
- aperçu si possible ;
- rapport d'import ;
- idempotence côté backend autant que possible ;
- aucune suppression implicite ;
- pas de secrets en clair dans les exports ;
- confirmation avant action sensible.

Le Desktop ne doit pas appliquer localement une configuration backend sans endpoint dédié.

## 72. Gestion des performances UI

Objectifs :

- interface réactive ;
- appels API limités ;
- pagination ;
- chargement à la demande ;
- absence de blocage pendant les requêtes ;
- widgets adaptés au volume.

À éviter :

- charger 10 000 lignes dans une table ;
- faire un appel API à chaque frappe sans contrôle ;
- bloquer le thread UI sur un appel long.

## 73. Gestion du multithreading ou des workers Qt, si nécessaire

Pour les appels longs, prévoir :

- `QThread` ;
- `QRunnable` ;
- signaux Qt ;
- annulation ou timeout ;
- retour d'erreur propre ;
- synchronisation avec l'UI dans le thread principal.

À valider lors de l'implémentation selon la complexité.

## 74. Éviter le blocage de l'interface pendant les appels API

Un appel HTTP dans le thread UI peut bloquer l'interface.

Pour appels rapides, cela peut rester acceptable temporairement. Pour appels longs ou fréquents, prévoir un worker.

Règles :

- afficher un état de chargement ;
- désactiver l'action ;
- utiliser timeout ;
- déplacer les appels longs hors thread UI ;
- mettre à jour l'UI via signaux.

## 75. Standards PySide6

Standards :

- classes en `PascalCase` ;
- fichiers en `snake_case.py` ;
- signaux Qt nommés clairement ;
- widgets configurés dans des méthodes courtes ;
- layouts explicites ;
- styles via QSS autant que possible ;
- pas de logique métier backend dans les widgets.

Exemple :

```python
class ReportsPage(QWidget):
    """Page de consultation des rapports."""
```

## 76. Standards `httpx`

Standards :

- timeout explicite ;
- `raise_for_status()` ou gestion statuts contrôlée ;
- headers centralisés ;
- authentification centralisée ;
- exceptions normalisées ;
- pas de logs de token ;
- client API réutilisable.

Exemple conceptuel :

```python
response = client.request(method, url, params=params, json=json)
response.raise_for_status()
```

## 77. Standards de nommage des classes Desktop

| Élément | Convention | Exemple |
| --- | --- | --- |
| Page | `PascalCase` + `Page` | `WebsitesPage` |
| Widget | `PascalCase` | `Sidebar` |
| Fenêtre | `PascalCase` + `Window` | `MainWindow` |
| Dialog | `PascalCase` + `Dialog` | `ConfirmDeleteDialog` |
| Service Desktop | `PascalCase` + `Service` | `ReportsDesktopService` |
| Client | `PascalCase` + `Client` | `ApiClient` |

Les noms doivent refléter le domaine fonctionnel.

## 78. Standards de nommage des fichiers Desktop

| Élément | Convention | Exemple |
| --- | --- | --- |
| Page | `snake_case_page.py` | `websites_page.py` |
| Widget | `snake_case.py` | `sidebar.py` |
| Service | `snake_case_service.py` | `reports_service.py` |
| Worker | `snake_case_worker.py` | `api_worker.py` |
| Config | `config.py` | `config.py` |

Éviter les fichiers génériques comme `utils.py` si un nom métier est possible.

## 79. Standards de découpage des vues

Une vue doit être découpée en méthodes lisibles.

Exemple recommandé :

```text
__init__()
_build_header()
_build_table()
load_data()
_parse_response()
_populate_table()
_show_error()
```

À éviter :

- tout construire dans une méthode de plusieurs centaines de lignes ;
- mélanger construction UI, appel API et parsing complexe ;
- dupliquer le même code de table dans chaque page.

## 80. Standards de découplage UI / logique applicative

Découplage recommandé :

- UI : affichage, interactions, états visuels ;
- service Desktop : préparation des appels et adaptation légère ;
- ApiClient : HTTP ;
- backend : règles métier.

Une page peut appeler directement `ApiClient` pour un cas simple. Dès que l'orchestration grandit, un service Desktop est recommandé.

## 81. Standards de sécurité Desktop

Règles :

- pas de secrets en clair ;
- pas de token dans les logs ;
- pas de mot de passe conservé après login ;
- pas d'accès base ;
- permissions vérifiées par backend ;
- affichage sobre des erreurs ;
- confirmation des actions sensibles ;
- stockage sécurisé à valider si persistance nécessaire.

## 82. Données sensibles à ne jamais logger

Ne jamais logger :

| Donnée | Exemple |
| --- | --- |
| Mot de passe | champ login |
| Token | access token, refresh token |
| Clé API | OpenAI, Google, autres |
| Secret | clé de signature |
| `.env` | variables locales |
| Données personnelles inutiles | email, identifiant complet si non nécessaire |
| Payload sensible | configuration contenant secrets |

En cas de doute, ne pas logger.

## 83. Variables de configuration Desktop

Variables possibles :

- `API_BASE_URL` ;
- `APP_NAME` ;
- `APP_VERSION` ;
- `HTTP_TIMEOUT_SECONDS` ;
- environnement actif ;
- niveau de log.

Règles :

- valeurs non sensibles dans le code ;
- secrets hors code ;
- configuration centralisée ;
- valeurs de développement explicites.

## 84. Gestion des environnements API

Environnements possibles :

| Environnement | Exemple d'URL |
| --- | --- |
| Local | `http://127.0.0.1:8000/api/v1` |
| Développement | à définir |
| Préproduction | à définir |
| Production | à définir |

Le choix d'environnement doit être explicite et sécurisé.

## 85. Configuration de l'URL API

L'URL API doit être centralisée.

Règles :

- pas d'URL dupliquée dans chaque page ;
- pas d'URL PostgreSQL ;
- chemin `/api/v1` cohérent ;
- possibilité d'adapter par environnement ;
- validation de format si configuration utilisateur.

## 86. Gestion de l'API locale, dev et production

Le Desktop doit pouvoir cibler plusieurs API selon contexte.

Recommandé :

- local pour développement ;
- dev pour tests internes ;
- production pour usage réel ;
- affichage discret de l'environnement si utile ;
- protections contre l'usage accidentel d'un environnement sensible.

À valider lors de l'implémentation.

## 87. Tests Desktop à prévoir

Tests à prévoir progressivement :

- services Desktop ;
- client API avec `httpx` mocké ;
- parsing de réponses ;
- gestion d'erreurs ;
- validations de formulaires ;
- widgets critiques ;
- workflows manuels.

Les tests UI complets peuvent être ajoutés plus tard selon outillage validé.

## 88. Tests unitaires des services Desktop

Un service Desktop doit être testable sans lancer toute l'interface.

Exemple :

```python
def test_service_builds_pagination_params(api_client):
    service = WebsiteDesktopService(api_client)

    service.list_websites(page=2, page_size=20)

    api_client.get.assert_called_once()
```

Les services doivent éviter de dépendre directement de widgets PySide6.

## 89. Tests des appels API mockés

Les appels HTTP doivent être testés avec des réponses simulées.

Exemple conceptuel :

```python
def test_api_client_raises_readable_error_on_500(mock_httpx):
    ...
```

Règles :

- pas d'appel réseau réel en test unitaire ;
- statuts HTTP couverts ;
- timeouts couverts ;
- payload inattendu couvert.

## 90. Tests des erreurs réseau

Cas à couvrir :

- connexion refusée ;
- timeout ;
- erreur DNS ;
- API indisponible ;
- réponse non JSON ;
- statut `500`.

Le résultat attendu doit être une erreur Desktop lisible, pas un crash.

## 91. Tests des formulaires

Les tests de formulaires peuvent vérifier :

- validation des champs ;
- bouton désactivé si invalide ;
- conservation des valeurs après erreur ;
- affichage des erreurs `422` ;
- confirmation avant action sensible.

À automatiser selon faisabilité PySide6 et priorité.

## 92. Tests des vues critiques

Vues critiques :

- login ;
- administration ;
- configuration ;
- imports/exports ;
- rapports ;
- modules SEO/GEO principaux.

Pour ces vues, prévoir au minimum une validation manuelle documentée si les tests UI automatisés ne sont pas encore en place.

## 93. Commandes PowerShell utiles pour le Desktop

Commandes :

```powershell
python desktop/main.py
ruff check desktop
ruff check desktop tests
pytest
git diff --check
```

Diagnostic :

```powershell
git status --short
git diff -- desktop
git diff -- tests
```

## 94. Commandes de tests recommandées

Commandes actuelles :

```powershell
pytest
pytest tests
```

Commandes futures si dossier Desktop dédié :

```powershell
pytest tests/desktop
pytest tests/desktop/test_api_client.py
```

Si aucun test Desktop automatisé n'existe encore, documenter la validation manuelle effectuée.

## 95. Commandes Ruff recommandées

Commandes :

```powershell
ruff check desktop
ruff check desktop tests
ruff check .
```

Règles :

- corriger les erreurs dans le périmètre ;
- ne pas reformater tout le dépôt sans validation ;
- signaler les erreurs hors périmètre au lieu de les modifier.

## 96. Workflow Codex pour une évolution Desktop

Workflow recommandé :

1. vérifier la branche active ;
2. vérifier `git status --short` ;
3. analyser les fichiers Desktop existants ;
4. lister les fichiers à créer ou modifier ;
5. attendre validation pour modification importante ;
6. modifier uniquement le périmètre autorisé ;
7. exécuter les vérifications ;
8. ne pas indexer sans demande ;
9. ne pas commiter ;
10. ne pas pousser.

Commandes minimales :

```powershell
git branch --show-current
git status --short
```

## 97. Ce que Codex peut modifier dans une tâche Desktop

Codex peut modifier si explicitement demandé :

- une page dans `desktop/ui/` ;
- un widget dans `desktop/widgets/` ;
- le client API dans `desktop/core/` ;
- la configuration Desktop non sensible ;
- un service Desktop si son dossier est validé ;
- les tests associés ;
- la documentation liée.

Chaque fichier doit rester dans le périmètre annoncé.

## 98. Ce que Codex ne doit pas modifier sans validation explicite

Codex ne doit pas :

- modifier des fichiers hors périmètre ;
- désindexer des fichiers déjà indexés ;
- créer un commit ;
- faire un push ;
- supprimer ou renommer des fichiers ;
- ajouter une dépendance ;
- refactorer globalement ;
- stocker des secrets ;
- connecter le Desktop à PostgreSQL ;
- importer des modèles backend SQLAlchemy.

## 99. Exemple conceptuel d'organisation Desktop

Organisation conceptuelle possible :

```text
desktop/
  core/
    api_client.py
    config.py
    constants.py
  ui/
    main_window.py
    dashboard_page.py
    websites_page.py
    geo_results_page.py
  widgets/
    sidebar.py
    statusbar.py
    pagination_controls.py
  styles/
    dark.qss
```

Les nouveaux dossiers doivent être ajoutés seulement si le besoin est validé.

## 100. Exemple conceptuel de client API avec `httpx`

Exemple conceptuel :

```python
class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: dict[str, object] | None = None) -> object:
        url = f"{self.base_url}/{path.lstrip('/')}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
```

Cet exemple est conceptuel ; privilégier le client existant et ses conventions.

## 101. Exemple conceptuel d'appel authentifié

Exemple conceptuel :

```python
headers = {"Authorization": f"Bearer {access_token}"}
response = client.get(url, headers=headers)
```

Règles :

- ne pas logger `access_token` ;
- centraliser l'ajout du header ;
- supprimer le token à la déconnexion ;
- gérer `401`.

## 102. Exemple conceptuel de gestion d'erreur API

Exemple conceptuel :

```python
try:
    payload = api_client.get("/websites")
except ApiClientError as exc:
    self.message.setText(f"API indisponible : {exc}")
```

À améliorer selon les statuts :

- `401` vers connexion ;
- `403` accès refusé ;
- `404` ressource introuvable ;
- `422` erreurs de formulaire.

## 103. Exemple conceptuel de pagination côté Desktop

Exemple conceptuel :

```python
payload = api_client.get(
    "/websites",
    params={"page": self.current_page, "page_size": self.page_size},
)

items = payload["items"]
total = payload["total"]
pages = payload["pages"]
```

La vue doit gérer page vide, page invalide et réponse inattendue.

## 104. Exemple conceptuel de filtrage côté Desktop

Exemple conceptuel :

```python
params = {
    "page": 1,
    "page_size": 20,
    "search": self.search_input.text().strip(),
}
payload = api_client.get("/keywords", params=params)
```

Ne pas envoyer de filtres non documentés par l'API.

## 105. Exemple conceptuel de service Desktop

Exemple conceptuel :

```python
class KeywordsDesktopService:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def search_keywords(self, query: str, page: int) -> dict[str, object]:
        return self.api_client.get(
            "/keywords",
            params={"search": query, "page": page, "page_size": 20},
        )
```

Le service prépare l'appel API, mais ne décide pas des règles métier.

## 106. Exemple conceptuel de vue PySide6

Exemple conceptuel :

```python
class KeywordsPage(QWidget):
    def __init__(self, service: KeywordsDesktopService) -> None:
        super().__init__()
        self.service = service
        self.message = QLabel("")
        self.table = QTableWidget()

    def load_keywords(self) -> None:
        try:
            payload = self.service.search_keywords("", page=1)
        except ApiClientError as exc:
            self.message.setText(str(exc))
            return
        self._populate_table(payload["items"])
```

À adapter aux conventions existantes.

## 107. Exemple conceptuel de worker ou tâche non bloquante

Exemple conceptuel :

```python
class ApiWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        try:
            payload = self.api_client.get(self.path)
        except ApiClientError as exc:
            self.failed.emit(str(exc))
        else:
            self.finished.emit(payload)
```

À valider lors de l'implémentation selon le modèle Qt retenu.

## 108. Exemple conceptuel de test Desktop

Exemple conceptuel :

```python
def test_desktop_service_uses_pagination(api_client):
    service = KeywordsDesktopService(api_client)

    service.search_keywords("seo", page=2)

    api_client.get.assert_called_once_with(
        "/keywords",
        params={"search": "seo", "page": 2, "page_size": 20},
    )
```

Le test ne lance pas l'application complète.

## 109. Checklist avant modification Desktop

- [ ] Branche active vérifiée.
- [ ] Branche différente de `main`.
- [ ] `git status --short` relu.
- [ ] Fichiers déjà indexés identifiés.
- [ ] Périmètre Desktop confirmé.
- [ ] Endpoint API identifié.
- [ ] Contrat API compris.
- [ ] Risques de sécurité vérifiés.
- [ ] Tests ou validation manuelle prévus.

## 110. Checklist avant ajout d'une vue

- [ ] Vue placée dans `desktop/ui/`.
- [ ] Classe en `PascalCase`.
- [ ] Fichier en `snake_case.py`.
- [ ] Navigation prévue si nécessaire.
- [ ] États chargement, vide, erreur, succès.
- [ ] Appels API centralisés.
- [ ] Aucun accès PostgreSQL.
- [ ] Aucun import SQLAlchemy backend.
- [ ] Style cohérent.

## 111. Checklist avant ajout d'un appel API

- [ ] Endpoint backend existant ou prévu.
- [ ] Méthode HTTP correcte.
- [ ] Paramètres documentés.
- [ ] Timeout prévu.
- [ ] Auth prévue si nécessaire.
- [ ] Erreurs HTTP gérées.
- [ ] Erreurs réseau gérées.
- [ ] Aucun token loggé.
- [ ] Appel centralisé dans ApiClient ou service Desktop.

## 112. Checklist avant tests

- [ ] Service Desktop testable.
- [ ] Appels API mockés.
- [ ] Erreurs réseau couvertes.
- [ ] Formulaires validés.
- [ ] Vue critique testée ou validée manuellement.
- [ ] Ruff prévu.
- [ ] Tests backend non cassés si API touchée.

## 113. Checklist avant commit

- [ ] `git status --short` relu.
- [ ] `git diff` relu.
- [ ] `git diff --check` sans erreur.
- [ ] Aucun secret.
- [ ] Aucun fichier temporaire.
- [ ] Aucun changement hors périmètre.
- [ ] Tests utiles exécutés.
- [ ] Ruff exécuté si Python modifié.
- [ ] Message de commit clair.

Codex ne doit pas créer ce commit sans demande explicite.

## 114. Checklist de revue Desktop

Le relecteur vérifie :

- découplage Desktop/backend ;
- absence d'accès PostgreSQL ;
- absence d'import SQLAlchemy backend ;
- appels API centralisés ;
- gestion des erreurs ;
- gestion des chargements ;
- validation des formulaires ;
- sécurité des tokens ;
- cohérence UI ;
- tests ou validation manuelle ;
- compatibilité future React.

## 115. Critères d'acceptation d'une fonctionnalité Desktop

Une fonctionnalité Desktop est acceptable si :

- elle répond au besoin utilisateur ;
- elle consomme l'API via HTTP REST ;
- elle ne contourne pas le backend ;
- elle ne contient pas de secret ;
- elle gère les erreurs principales ;
- elle reste réactive ;
- elle respecte les conventions PySide6 ;
- elle est testée ou validée ;
- elle n'introduit pas d'architecture parallèle.

## 116. Points à éviter

À éviter systématiquement :

- accès direct PostgreSQL ;
- import de modèles SQLAlchemy backend ;
- appels API dispersés partout ;
- token écrit en clair ;
- token dans les logs ;
- mot de passe conservé ;
- logique métier backend dans l'UI ;
- interface bloquée par appel long ;
- chargement massif sans pagination ;
- suppression sans confirmation ;
- erreur technique brute affichée à l'utilisateur ;
- refactor global non validé.

## 117. Liens avec les documents

Documents liés :

| Document | Rôle |
| --- | --- |
| `docs/development/Git_Workflow.md` | workflow Git officiel |
| `docs/development/CONTRIBUTING.md` | règles de contribution |
| `docs/development/CODING_STANDARDS.md` | standards de code |
| `docs/development/BACKEND_DEVELOPMENT_GUIDE.md` | guide backend |
| `docs/development/TESTING.md` | guide tests futur |
| `docs/api/AUTHENTICATION.md` | authentification API |
| `docs/api/ERROR_HANDLING.md` | erreurs API |
| `docs/api/PAGINATION.md` | pagination API |
| `docs/api/FILTERING.md` | filtrage API |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | architecture Desktop |
| `docs/architecture/API_ARCHITECTURE.md` | architecture API |
| `docs/design/UI_UX.md` | règles UI/UX |
| `docs/specifications/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | exigences fonctionnelles |

Ces documents doivent rester cohérents avec ce guide.

## Matrice de responsabilité Desktop / backend

| Responsabilité | Vue Desktop | Service Desktop | Client API | API FastAPI | Backend |
| --- | --- | --- | --- | --- | --- |
| Affichage | Oui | Non | Non | Non | Non |
| Interaction utilisateur | Oui | Partiel | Non | Non | Non |
| Préparation paramètres UI | Partiel | Oui | Non | Non | Non |
| Appel HTTP | Non recommandé | Possible via client | Oui | Reçoit | Non |
| Auth header | Non | Non | Oui | Valide | Applique |
| Règles métier | Non | Non | Non | Non | Oui |
| Permissions réelles | Non | Non | Non | Contrôle | Applique |
| Accès PostgreSQL | Non | Non | Non | Non | Via repositories |
| Gestion erreur utilisateur | Oui | Partiel | Normalise | Standardise | Déclenche |
| Pagination | UI | Paramètres | Transmet | Valide | Exécute |

## Matrice de contrôle par type de changement Desktop

| Changement | Fichiers typiques | Contrôles | Risque principal |
| --- | --- | --- | --- |
| Nouvelle page | `desktop/ui/` | lancement manuel, Ruff | page trop couplée |
| Nouveau widget | `desktop/widgets/` | revue UI | composant trop spécifique |
| Appel API | `desktop/core/`, page ou service | erreurs HTTP, timeout | duplication d'appels |
| Auth Desktop | core, login UI | sécurité token | stockage non sûr |
| Pagination | page, widget | listes vides, limites | chargement massif |
| Import config | page, service | confirmation, idempotence | action destructive |
| Rapport | page, worker | non-blocage UI | timeout ou freeze |
| Administration | page admin | permissions, confirmations | action sensible |
| Tests Desktop | `tests/desktop/` futur | Pytest | tests trop couplés UI |

## Diagramme ASCII du flux Desktop vers backend

```text
Desktop PySide6
   |
   | utilisateur clique / filtre / valide
   v
Vue ou widget Desktop
   |
   | prépare l'état UI
   v
Service Desktop optionnel
   |
   | appelle
   v
ApiClient centralisé
   |
   | httpx HTTP REST
   v
FastAPI routes
   |
   v
Services métier
   |
   v
Repositories SQLAlchemy
   |
   v
PostgreSQL
```

## Diagramme ASCII du découpage recommandé d'une fonctionnalité Desktop

```text
Fonctionnalité : liste des mots-clés
   |
   +-- Page PySide6
   |     +-- table
   |     +-- filtres
   |     +-- pagination
   |     +-- états UI
   |
   +-- Service Desktop optionnel
   |     +-- prépare params API
   |     +-- normalise réponse pour la vue
   |
   +-- ApiClient
   |     +-- GET /keywords
   |     +-- gère timeout et erreurs
   |
   +-- API FastAPI
         +-- authentification
         +-- validation
         +-- règles métier backend
```

## Commandes PowerShell de référence

Avant modification :

```powershell
git branch --show-current
git status --short
```

Lancer le Desktop :

```powershell
python desktop/main.py
```

Qualité :

```powershell
ruff check desktop
pytest
git diff --check
```

Diagnostic :

```powershell
git diff -- desktop
git diff -- tests
git diff --cached
```

## Section de prudence

Ne jamais introduire côté Desktop :

```python
create_engine("postgresql://...")
from backend.app.models import ...
```

Ne jamais stocker :

```text
access_token en clair
mot de passe en clair
clé API en clair
```

Ne pas utiliser sans validation explicite :

```powershell
git reset --hard
git clean -fd
git push --force
```

En cas d'incertitude sur une action Desktop sensible, arrêter et demander confirmation.
