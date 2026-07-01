# Sprint 17 - Module Desktop URLs

## 1. Contexte

Les sprints precedents ont installe le socle Desktop necessaire aux modules metier :

- le shell Desktop PySide6 et la navigation par modules sont disponibles ;
- le Desktop communique avec FastAPI via `ApiClient` et HTTP REST ;
- l'authentification Desktop transmet automatiquement le token Bearer ;
- les modules Websites, Entities, Keywords et Competitors fournissent le modele CRUD de reference ;
- les erreurs API et reseau sont deja transformees en messages utilisateur dans les services Desktop.

Le Sprint 17 est consacre au module Desktop URLs.

Le Backend expose deja le CRUD securise des URLs. Le sprint ne prevoit aucune evolution Backend et ne doit traiter que
le client Desktop.

## 2. Objectifs

Le Sprint 17 a pour objectifs de :

- remplacer ou finaliser la page Desktop URLs par un module CRUD fonctionnel ;
- permettre l'affichage pagine des URLs depuis l'API REST ;
- permettre la recherche d'URLs ;
- permettre la creation, la modification et la suppression d'une URL ;
- conserver l'architecture Desktop `Page -> Service -> ApiClient -> API REST` ;
- appliquer des validations Desktop minimales avant les appels API ;
- afficher des messages utilisateur lisibles ;
- gerer les erreurs HTTP et les erreurs reseau ;
- ajouter des tests automatiques sur la couche Service Desktop ;
- documenter les limites du module.

Le module doit reprendre fidelement les patterns des modules Desktop Websites, Entities, Keywords et Competitors.

## 3. Perimetre

Le sprint couvre uniquement le module Desktop URLs.

Fonctionnalites incluses :

- affichage pagine des URLs ;
- recherche textuelle lorsque le Backend expose un parametre compatible ;
- rafraichissement manuel de la liste ;
- creation d'une URL ;
- modification de l'URL selectionnee ;
- suppression de l'URL selectionnee apres confirmation ;
- rechargement automatique apres creation, modification et suppression ;
- boite de dialogue URL pour creation et modification ;
- validations Desktop des champs ;
- affichage de messages de succes et d'erreur ;
- gestion des erreurs HTTP courantes ;
- gestion des erreurs reseau ;
- tests du service Desktop.

Le sprint reste volontairement limite au CRUD Desktop.

## 4. Hors Perimetre

Le Sprint 17 ne traite pas :

- le Backend ;
- les migrations Alembic ;
- les modeles SQLAlchemy ;
- les schemas Pydantic Backend ;
- les routes FastAPI ;
- les services Backend ;
- les repositories Backend ;
- l'acces direct a PostgreSQL ;
- l'import de modeles SQLAlchemy dans le Desktop ;
- un refactor generique des pages CRUD ;
- la creation d'une couche commune CRUD ;
- le crawl ;
- l'audit technique automatise ;
- les Core Web Vitals ;
- les statistiques SEO ;
- les graphiques ;
- l'import ou l'export ;
- l'integration Google Search Console ;
- les tests UI PySide6 automatises si le projet n'en contient pas deja.

## 5. Architecture

L'architecture Desktop attendue reste :

```text
URLsPage
    -> URLsService
        -> ApiClient
            -> API FastAPI
```

Aucune nouvelle architecture ne doit etre introduite.

Responsabilites attendues :

| Composant | Responsabilite |
| --- | --- |
| `URLsPage` | Affichage, selection, recherche, pagination, boutons, confirmations et messages utilisateur. |
| `URLsService` | Appels REST, parsing des reponses, normalisation de la pagination et mapping des erreurs. |
| `URLDialog` | Collecte des champs de creation et modification avec validations Desktop minimales. |
| `ApiClient` | Client HTTP generique existant, reutilise sans modification. |

Regles obligatoires :

- le Desktop communique uniquement via l'API REST ;
- aucun acces direct a PostgreSQL ;
- aucun import SQLAlchemy ;
- aucune logique metier dans la page ;
- aucune nouvelle instance d'`ApiClient` si une instance existe deja dans `MainWindow`.

## 6. Composants Concernés

Composants a documenter et a creer lors du developpement :

- `desktop/services/urls_service.py`
- `desktop/ui/dialogs/url_dialog.py`
- `tests/desktop/test_urls_service.py`

Composants a modifier lors du developpement :

- `desktop/ui/urls_page.py`
- `desktop/ui/main_window.py`, uniquement pour injecter l'`ApiClient` existant si necessaire.
- `desktop/core/constants.py`, uniquement pour declarer la page URLs dans la navigation.

Fichiers qui ne doivent pas etre modifies :

- `backend/`
- `backend/alembic/`
- `desktop/core/api_client.py`
- tout fichier hors perimetre du module Desktop URLs.

## 7. Flux Applicatif

Flux general :

1. L'utilisateur ouvre le module URLs depuis la navigation Desktop.
2. `URLsPage` demande la liste a `URLsService`.
3. `URLsService` appelle l'API REST via `ApiClient`.
4. `ApiClient` transmet la requete HTTP avec la session existante.
5. `URLsService` valide et normalise la reponse.
6. `URLsPage` met a jour le tableau, la pagination et le message utilisateur.

Flux d'ecriture :

1. L'utilisateur ouvre la boite de dialogue URL.
2. `URLDialog` collecte les champs et applique les validations Desktop.
3. `URLsPage` transmet le payload valide a `URLsService`.
4. `URLsService` appelle l'API REST via `ApiClient`.
5. La liste est rechargee apres succes.
6. Un message confirme l'action realisee.

## 8. Parcours Utilisateur

### Consultation

1. L'utilisateur ouvre le module URLs.
2. Le tableau affiche la premiere page d'URLs.
3. Un message indique le nombre d'elements trouves et la page courante.
4. Les boutons `Modifier` et `Supprimer` restent desactives tant qu'aucune ligne n'est selectionnee.

### Recherche

1. L'utilisateur saisit une recherche.
2. Il valide la recherche ou utilise le bouton de recherche.
3. La page recharge la liste avec le terme saisi.
4. Le tableau affiche les resultats pagines.
5. Un message indique si aucun resultat n'est disponible.

### Creation

1. L'utilisateur clique sur `Ajouter`.
2. La boite de dialogue URL s'ouvre.
3. L'utilisateur renseigne les champs.
4. Le Desktop valide les champs minimaux.
5. L'URL est creee via le service Desktop.
6. La liste est rechargee.
7. Un message confirme la creation.

### Modification

1. L'utilisateur selectionne une URL.
2. Il clique sur `Modifier` ou double-clique sur la ligne.
3. La boite de dialogue est pre-remplie.
4. Le Desktop valide les champs minimaux.
5. L'URL est modifiee via le service Desktop.
6. La liste est rechargee.
7. Un message confirme la modification.

### Suppression

1. L'utilisateur selectionne une URL.
2. Il clique sur `Supprimer`.
3. Une confirmation explicite est affichee.
4. Si l'utilisateur confirme, l'URL est supprimee via le service Desktop.
5. La liste est rechargee.
6. Un message confirme la suppression.

## 9. Liste Des Ecrans

### Page URLs

Elements attendus :

- titre de page ;
- champ de recherche ;
- bouton de recherche ou validation par entree ;
- bouton `Ajouter` ;
- bouton `Modifier` ;
- bouton `Supprimer` ;
- bouton `Rafraichir` ;
- tableau des URLs ;
- indication de pagination ;
- zone de message utilisateur.

### Tableau URLs

Le tableau doit :

- afficher les URLs recuperees depuis l'API ;
- rester en lecture seule ;
- permettre la selection d'une ligne ;
- activer `Modifier` et `Supprimer` uniquement lorsqu'une URL est selectionnee ;
- conserver une presentation coherente avec Keywords et Competitors ;
- afficher des colonnes issues uniquement des donnees exposees par l'API.

### Boite De Dialogue URL

Le dialogue doit etre place dans :

```text
desktop/ui/dialogs/url_dialog.py
```

Il doit :

- servir a la creation et a la modification ;
- pre-remplir les champs en modification ;
- exposer uniquement les champs reellement disponibles dans l'API ;
- appliquer des validations Desktop minimales ;
- produire un payload compatible avec l'API REST ;
- ne contenir aucune logique Backend.

## 10. Fonctionnalités Prévues

| Fonctionnalite | Comportement attendu |
| --- | --- |
| Affichage pagine | Charger les URLs avec `page` et `page_size`. |
| Recherche | Envoyer le terme recherche via le service Desktop lorsque le Backend le supporte. |
| Rafraichissement | Recharger la page courante avec les filtres actifs. |
| Creation | Ouvrir `URLDialog`, valider, appeler le service, recharger la liste. |
| Modification | Utiliser l'URL selectionnee, pre-remplir le dialogue, appeler le service. |
| Suppression | Demander confirmation avant l'appel de suppression. |
| Double-clic | Ouvrir la modification de la ligne selectionnee. |
| Messages | Afficher les succes, erreurs HTTP, erreurs reseau et payloads inattendus. |

## 11. Validations Desktop

Les validations Desktop doivent rester minimales. Les validations metier finales restent cote API.

Regles attendues :

- les champs obligatoires doivent etre renseignes ;
- les longueurs maximales doivent respecter les contraintes exposees par l'API ;
- les identifiants optionnels doivent etre numeriques lorsqu'ils sont renseignes ;
- les champs optionnels vides doivent etre envoyes sous forme compatible avec l'API ;
- aucune regle SEO avancee ne doit etre ajoutee dans le Desktop.

Le Desktop ne doit pas dupliquer toute la logique metier du Backend.

## 12. Gestion Des Erreurs

Le module doit transformer les erreurs techniques en messages utilisateur comprehensibles.

Cas a gerer :

- erreur reseau ;
- timeout ;
- backend indisponible ;
- `401` : utilisateur non authentifie ;
- `403` : permission insuffisante ;
- `404` : URL introuvable ;
- `409` : conflit ;
- `422` : donnees invalides ;
- erreur serveur `5xx` ;
- payload API inattendu.

Comportements attendus :

- vider le tableau si le chargement echoue ;
- desactiver les boutons d'action pendant un appel API ;
- garder le bouton `Rafraichir` disponible apres retour a un etat stable ;
- afficher les details utiles des erreurs `422` lorsque l'API les fournit ;
- ne pas bloquer la page apres une erreur de creation, modification ou suppression.

## 13. Tests Attendus

Les tests automatiques attendus concernent la couche Service Desktop.

Fichier attendu :

```text
tests/desktop/test_urls_service.py
```

Tests a prevoir :

- chargement de la liste via le service URLs ;
- transmission des parametres de pagination ;
- transmission du terme de recherche ;
- parsing d'une reponse paginee valide ;
- gestion d'une liste vide ;
- creation d'une URL ;
- modification d'une URL ;
- suppression d'une URL ;
- mapping des erreurs `401` vers `unauthorized` ;
- mapping des erreurs `403` vers `forbidden` ;
- mapping des erreurs `404` vers `not_found` ;
- mapping des erreurs `409` vers `conflict` ;
- mapping des erreurs `422` vers `validation_error` ;
- mapping des erreurs `500` vers `server_error` ;
- mapping des erreurs reseau ;
- mapping du backend indisponible ;
- rejet d'un payload pagine invalide ;
- rejet d'un payload ressource invalide.

Les tests UI PySide6 automatises ne sont pas requis si le projet ne dispose pas deja d'une infrastructure dediee.

## 14. Criteres D'Acceptation

Le Sprint 17 sera considere termine si :

- la page URLs est fonctionnelle cote Desktop ;
- l'utilisateur peut consulter les URLs de maniere paginee ;
- l'utilisateur peut rechercher des URLs ;
- l'utilisateur peut creer une URL ;
- l'utilisateur peut modifier une URL ;
- l'utilisateur peut supprimer une URL apres confirmation ;
- la liste est rechargee apres chaque operation ;
- les erreurs HTTP et reseau sont affichees clairement ;
- les validations Desktop minimales fonctionnent ;
- le Desktop passe uniquement par `URLsService` et `ApiClient` ;
- aucun acces direct a PostgreSQL n'est introduit ;
- aucun modele SQLAlchemy Backend n'est importe dans le Desktop ;
- le Backend reste inchange ;
- Ruff passe ;
- Pytest passe.

## 15. Risques

Risques identifies :

- ajouter des regles SEO avancees dans un sprint limite au CRUD ;
- introduire une abstraction CRUD generique trop tot ;
- dupliquer de la logique metier Backend dans la page Desktop ;
- exposer trop d'identifiants techniques dans l'interface ;
- oublier la recherche lors de la pagination ;
- ne pas conserver le terme de recherche apres creation, modification ou suppression ;
- modifier accidentellement `ApiClient` ou le Backend ;
- creer des tests UI hors infrastructure existante.

Mesures de limitation :

- reprendre les patterns de Keywords et Competitors ;
- limiter le sprint aux champs reellement exposes par l'API ;
- isoler les appels REST dans `URLsService` ;
- tester uniquement la couche Service Desktop ;
- documenter les limites fonctionnelles ;
- verifier que seuls les fichiers Desktop et documentation prevus sont modifies.

## 16. Livrables

Livrables attendus lors du developpement :

- `desktop/services/urls_service.py`
- `desktop/ui/urls_page.py`
- `desktop/ui/dialogs/url_dialog.py`
- `tests/desktop/test_urls_service.py`
- `docs/sprints/sprint-17-desktop-urls.md`

Fichiers pouvant etre modifies :

- `desktop/ui/main_window.py`, uniquement pour l'injection de l'`ApiClient` existant ;
- `desktop/core/constants.py`, uniquement pour ajouter la constante et l'entree de navigation URLs ;
- fichiers Desktop strictement necessaires au module URLs si le depot contient deja un placeholder dedie.

Fichiers explicitement exclus :

- `backend/`
- `backend/alembic/`
- `desktop/core/api_client.py`
- fichiers Python hors perimetre du module URLs.

## 17. Checklist De Validation

Avant cloture du Sprint 17 :

- [ ] architecture `Page -> Service -> ApiClient -> API REST` respectee ;
- [ ] aucune modification Backend ;
- [ ] aucun acces direct a PostgreSQL ;
- [ ] aucun import SQLAlchemy dans le Desktop ;
- [ ] aucune nouvelle architecture generique ;
- [ ] recherche fonctionnelle ;
- [ ] pagination fonctionnelle ;
- [ ] creation fonctionnelle ;
- [ ] modification fonctionnelle ;
- [ ] suppression avec confirmation fonctionnelle ;
- [ ] erreurs HTTP affichees ;
- [ ] erreurs reseau affichees ;
- [ ] tests service ajoutes ;
- [ ] `python -m ruff check .` OK ;
- [ ] `python -m pytest` OK ;
- [ ] documentation Sprint 17 a jour.

## 18. Prochaines Etapes

Apres validation du Sprint 17, la suite previsionnelle pourra porter sur :

- le module Desktop Project Tasks ;
- le module Desktop Reports ;
- l'enrichissement progressif du Dashboard avec des donnees metier reelles ;
- l'amelioration des filtres ou de l'ergonomie URLs si un besoin utilisateur est confirme.

Ces evolutions devront rester separees du Sprint 17 afin de conserver un perimetre clair et livrable.
