# Sprint 15 - Module Desktop Keywords

## 1. Contexte

Les sprints precedents ont installe les fondations Desktop et Backend necessaires :

- le shell Desktop et la navigation par modules sont disponibles ;
- le Desktop communique avec FastAPI via `ApiClient` et HTTP REST ;
- l'authentification Desktop transmet automatiquement le token Bearer ;
- les modules Desktop Websites et Entities fournissent le modele CRUD de reference ;
- les routes metier Backend sont securisees par JWT et permissions RBAC.

Le Sprint 15 ajoute le CRUD Desktop du module Keywords. Il reprend volontairement le modele du Sprint 14 afin de
garder une architecture simple, lisible et homogene avec le reste du client PySide6.

## 2. Objectifs

Le Sprint 15 a pour objectifs de :

- remplacer le placeholder Desktop Keywords par un module fonctionnel ;
- permettre la consultation des mots-cles depuis l'API REST ;
- permettre la creation, la modification et la suppression d'un mot-cle ;
- conserver une architecture Desktop decouplee du Backend ;
- appliquer une validation Desktop minimale avant les appels API ;
- gerer les erreurs API et reseau de maniere lisible pour l'utilisateur ;
- ajouter des tests automatiques sur la couche Service Desktop.

## 3. Perimetre

Le sprint couvre uniquement le module Desktop Keywords.

Fonctionnalites incluses :

- affichage de la liste paginee des mots-cles ;
- rafraichissement manuel de la liste ;
- creation d'un mot-cle ;
- modification du mot-cle selectionne ;
- suppression du mot-cle selectionne apres confirmation ;
- rechargement automatique apres creation, modification et suppression ;
- affichage des messages de succes et d'erreur ;
- gestion des erreurs API courantes ;
- validation Desktop minimale avant envoi a l'API.

Champs pris en charge cote Desktop :

- `term` : mot-cle ;
- `intent` : intention optionnelle ;
- `priority` : priorite optionnelle ;
- `entity_id` : rattachement optionnel a une entite par identifiant.

## 4. Hors Perimetre

Le Sprint 15 ne traite pas :

- le Backend ;
- les migrations Alembic ;
- les modeles SQLAlchemy ;
- les schemas Pydantic Backend ;
- les routes FastAPI ;
- les Services Backend ;
- les Repositories Backend ;
- un refactor generique des pages CRUD ;
- les filtres avances ;
- l'import CSV ;
- l'export ;
- les champs SEO avances absents du Backend actuel ;
- l'affichage du nom d'entite lorsque l'API ne le fournit pas ;
- les tests UI PySide6 automatises.

## 5. Architecture

L'architecture Desktop appliquee reste :

```text
KeywordsPage
    -> KeywordsService
        -> ApiClient
            -> API FastAPI
```

Composants crees :

- `desktop/services/keywords_service.py`
- `desktop/ui/dialogs/keyword_dialog.py`
- `tests/desktop/test_keywords_service.py`
- `docs/sprints/sprint-15-desktop-keywords.md`

Composants modifies :

- `desktop/ui/keywords_page.py`
- `desktop/ui/main_window.py`

Responsabilites :

- `KeywordsPage` gere l'affichage, la selection, les boutons, les confirmations et les messages utilisateur.
- `KeywordsService` gere les appels REST, le parsing des reponses et la traduction des erreurs `ApiClientError`.
- `KeywordDialog` collecte les champs de creation et modification avec validation Desktop minimale.
- `ApiClient` reste le client HTTP generique existant.

## 6. Endpoints Utilises

Endpoints reutilises :

- `GET /api/v1/keywords`
- `GET /api/v1/keywords/{id}`
- `POST /api/v1/keywords`
- `PUT /api/v1/keywords/{id}`
- `DELETE /api/v1/keywords/{id}`

Le Desktop utilise les chemins relatifs suivants via `ApiClient` :

- `GET /keywords`
- `POST /keywords`
- `PUT /keywords/{id}`
- `DELETE /keywords/{id}`

Permissions Backend attendues :

- lecture : `keyword.read` ;
- creation : `keyword.write` ;
- modification : `keyword.write` ;
- suppression : `keyword.delete`.

## 7. Deroulement Du Developpement

Le developpement a ete realise par extension de l'existant :

1. analyse du module Desktop Entities ;
2. verification des routes et schemas Backend Keywords ;
3. creation de `KeywordsService` sur le modele de `EntitiesService` ;
4. creation de `KeywordDialog` sur la philosophie de `EntityDialog` ;
5. remplacement du placeholder `KeywordsPage` par une page CRUD ;
6. injection du `ApiClient` existant depuis `MainWindow` ;
7. ajout des tests du service Desktop ;
8. execution des controles qualite du projet.

## 8. Choix Techniques

Le Sprint 15 ne cree pas d'abstraction CRUD generique. Cette decision preserve le style actuel du projet et evite un
refactor global hors perimetre.

La page affiche l'identifiant d'entite lorsque l'API ne fournit pas d'objet `entity`. Une methode `_entity_label` garde
cependant la page compatible avec une future reponse enrichie.

Les erreurs sont transformees dans le service Desktop avec des codes explicites :

- `unauthorized`
- `forbidden`
- `not_found`
- `conflict`
- `validation_error`
- `server_error`
- `backend_unavailable`
- `network_error`
- `unexpected`

## 9. Validations Desktop

Les validations Desktop restent minimales. Les validations metier finales restent cote Backend.

Validations appliquees :

- `term` obligatoire ;
- `term` limite a 255 caracteres ;
- `intent` limite a 100 caracteres ;
- `priority` limite a 50 caracteres ;
- `entity_id` numerique lorsqu'il est renseigne.

Le Desktop n'ajoute pas de regle metier non presente dans les schemas Backend.

## 10. Gestion Des Erreurs

Le module gere les cas suivants :

- erreur reseau ;
- backend indisponible ;
- `401` : utilisateur non authentifie ;
- `403` : permission insuffisante ;
- `404` : mot-cle introuvable ;
- `409` : conflit ;
- `422` : donnees invalides ;
- erreur serveur `5xx` ;
- payload API inattendu.

Les erreurs `422` affichent les details utiles lorsque l'API les fournit au format FastAPI.

## 11. Tests Realises

Tests ajoutes :

- chargement de la liste via `GET /keywords` ;
- parsing d'une reponse paginee valide ;
- gestion d'une liste vide ;
- creation via `POST /keywords` ;
- modification via `PUT /keywords/{id}` ;
- suppression via `DELETE /keywords/{id}` ;
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

## 12. Resultats Qualite

Commandes a executer en validation finale :

```text
python -m ruff check .
python -m pytest
```

Les resultats exacts sont reportes dans le rapport final de l'intervention.

## 13. Description Fonctionnelle

La page Keywords presente un tableau avec les colonnes suivantes :

- Mot-cle ;
- Intention ;
- Priorite ;
- Entite.

L'utilisateur peut :

- rafraichir la liste ;
- ajouter un mot-cle ;
- selectionner un mot-cle ;
- modifier le mot-cle selectionne ;
- double-cliquer une ligne pour modifier ;
- supprimer un mot-cle apres confirmation.

## 14. Limites Connues

Limites liees a l'etat actuel du Backend :

- pas de filtre dedie par `entity_id` ;
- pas de nom d'entite retourne dans `KeywordRead` ;
- pas de champs `website_id`, `status`, `target_url`, volume ou position ;
- pas d'import ou export de mots-cles ;
- pas de contrainte d'unicite metier visible dans le service Keywords.

## 15. Perspectives Sprint 16

Le Sprint 16 pourra appliquer le meme modele au module Desktop Competitors :

- creation d'un service Desktop dedie ;
- creation d'un dialogue de creation et modification ;
- remplacement du placeholder par une page CRUD ;
- tests de la couche service ;
- maintien strict du passage par `ApiClient`.
