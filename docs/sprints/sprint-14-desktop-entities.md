# Sprint 14 - Module Desktop Entities

## 1. Contexte

Les sprints precedents ont installe les fondations Desktop et Backend necessaires :

- le shell Desktop, la sidebar et le dashboard sont disponibles ;
- le Desktop communique avec FastAPI via `ApiClient` et HTTP REST ;
- l'authentification Desktop est en place avec session utilisateur et Bearer automatique ;
- le module Desktop Websites permet deja la consultation et le CRUD complet ;
- les routes metier Backend sont securisees par JWT et permissions RBAC.

Le Sprint 14 ouvre le deuxieme module metier Desktop : les entites.

Les entites constituent le referentiel central de la plateforme. Elles permettent de regrouper les sites, mots-cles,
concurrents, rapports et taches projet autour d'un meme perimetre metier. Sans module Desktop Entities, les modules
suivants resteraient contraints d'exposer des identifiants techniques ou de travailler sans contexte metier clair.

Ce sprint est donc le prochain increment logique apres Websites et la securisation Backend. Il reste volontairement
court afin de pouvoir etre livre dans une seule Pull Request.

## 2. Objectifs

Le Sprint 14 a pour objectifs de :

- remplacer le placeholder Desktop Entities par un module fonctionnel ;
- permettre la consultation des entites depuis l'API REST ;
- permettre la creation, la modification et la suppression d'une entite ;
- conserver une architecture Desktop decouplee du Backend ;
- appliquer une validation Desktop minimale avant les appels API ;
- gerer les erreurs API et reseau de maniere lisible pour l'utilisateur ;
- ajouter des tests automatiques sur la couche Service Desktop ;
- documenter le comportement attendu du module.

## 3. Perimetre

Le sprint couvre uniquement le module Desktop Entities.

Fonctionnalites incluses :

- affichage de la liste paginee des entites ;
- rafraichissement manuel de la liste ;
- creation d'une entite ;
- modification de l'entite selectionnee ;
- suppression de l'entite selectionnee apres confirmation ;
- rechargement automatique apres creation, modification et suppression ;
- affichage des messages de succes et d'erreur ;
- gestion des erreurs API courantes ;
- validation Desktop minimale avant envoi a l'API.

Champs attendus cote Desktop :

- `name` : nom de l'entite ;
- `description` : description optionnelle ;
- `is_active` : statut actif/inactif.

## 4. Hors Perimetre

Le Sprint 14 ne traite pas :

- le module Keywords ;
- le module Competitors ;
- le module URLs ;
- le module Reports ;
- le module Project Tasks ;
- le Dashboard ;
- le module Administration ;
- un refactor generique des pages CRUD ;
- les migrations Alembic ;
- les modeles SQLAlchemy ;
- les schemas Pydantic Backend ;
- les routes Backend ;
- les Services Backend ;
- les Repositories Backend ;
- l'API publique ;
- la pagination Backend ;
- l'import direct de modeles Backend dans le Desktop ;
- l'acces direct du Desktop a PostgreSQL.

Le sprint ne doit pas introduire `pytest-qt`.

## 5. Architecture

L'architecture Desktop attendue reste :

```text
EntitiesPage
    -> EntitiesService
        -> ApiClient
            -> API FastAPI
```

Composants a creer lors du futur developpement :

- `desktop/services/entities_service.py`
- `desktop/ui/dialogs/entity_dialog.py`

Composant a modifier lors du futur developpement :

- `desktop/ui/entities_page.py`

Responsabilites :

- `EntitiesPage` gere l'affichage, la selection, les boutons, les confirmations et les messages utilisateur.
- `EntitiesService` gere les appels REST, le parsing des reponses et la traduction des erreurs `ApiClientError`.
- `EntityDialog` collecte les champs de creation et modification avec validation Desktop minimale.
- `ApiClient` reste le client HTTP generique deja existant.

Le Desktop doit continuer a communiquer uniquement avec FastAPI via HTTP REST.

## 6. Ecrans

### Page Entities

La page Entities doit remplacer le placeholder actuel.

Elements attendus :

- titre de page ;
- tableau des entites ;
- bouton `Ajouter` ;
- bouton `Modifier` ;
- bouton `Supprimer` ;
- bouton `Rafraichir` ;
- zone de message utilisateur.

### Tableau

Colonnes recommandees :

- `Nom` ;
- `Description` ;
- `Actif`.

Le tableau doit :

- afficher les entites recuperees depuis l'API ;
- permettre la selection d'une ligne ;
- activer `Modifier` et `Supprimer` uniquement lorsqu'une entite est selectionnee ;
- rester en lecture seule ;
- vider la selection ou desactiver les actions lors du chargement.

### Dialogue Entity

Le dialogue doit etre place dans :

```text
desktop/ui/dialogs/entity_dialog.py
```

Il doit servir a la creation et a la modification.

Champs attendus :

- champ texte `Nom` ;
- champ texte multi-ligne ou texte simple `Description` ;
- case a cocher `Entite active`.

Le dialogue doit :

- pre-remplir les champs en modification ;
- refuser la validation si les champs obligatoires sont invalides ;
- produire un payload compatible avec l'API REST ;
- ne contenir aucune logique Backend.

### Confirmations

La suppression doit demander une confirmation explicite avant l'appel API.

Message recommande :

```text
Supprimer l'entite "<nom>" ?
```

## 7. Flux Utilisateur

### Consultation

1. L'utilisateur ouvre le module Entities.
2. Le Desktop appelle `GET /entities`.
3. La liste est affichee dans le tableau.
4. Un message indique le nombre d'entites trouvees.

### Creation

1. L'utilisateur clique sur `Ajouter`.
2. Le dialogue de creation s'ouvre.
3. L'utilisateur renseigne les champs.
4. Le Desktop valide les champs minimaux.
5. Le Desktop appelle `POST /entities`.
6. La liste est rechargee automatiquement.
7. Un message confirme la creation.

### Modification

1. L'utilisateur selectionne une entite.
2. Il clique sur `Modifier` ou double-clique sur la ligne.
3. Le dialogue est pre-rempli.
4. Le Desktop valide les champs minimaux.
5. Le Desktop appelle `PUT /entities/{id}`.
6. La liste est rechargee automatiquement.
7. Un message confirme la modification.

### Suppression

1. L'utilisateur selectionne une entite.
2. Il clique sur `Supprimer`.
3. Une confirmation est affichee.
4. Si l'utilisateur confirme, le Desktop appelle `DELETE /entities/{id}`.
5. La liste est rechargee automatiquement.
6. Un message confirme la suppression.

## 8. Appels API

Endpoints reutilises :

- `GET /api/v1/entities`
- `GET /api/v1/entities/{id}`
- `POST /api/v1/entities`
- `PUT /api/v1/entities/{id}`
- `DELETE /api/v1/entities/{id}`

Role des endpoints :

- `GET /entities` : recuperer la liste paginee des entites ;
- `GET /entities/{id}` : recuperer une entite precise si necessaire ;
- `POST /entities` : creer une entite ;
- `PUT /entities/{id}` : modifier une entite existante ;
- `DELETE /entities/{id}` : supprimer une entite existante.

Permissions Backend attendues :

- lecture : `entity.read` ;
- creation : `entity.write` ;
- modification : `entity.write` ;
- suppression : `entity.delete`.

Le Desktop ne doit pas calculer la securite finale. Il affiche les erreurs renvoyees par l'API.

## 9. Gestion Des Erreurs

Le module Desktop doit transformer les erreurs techniques en messages utilisateur comprehensibles.

Cas a gerer :

- erreur reseau ;
- timeout ;
- backend indisponible ;
- `401` : utilisateur non authentifie ;
- `403` : permission insuffisante ;
- `404` : entite introuvable ;
- `409` : conflit, par exemple nom deja utilise ;
- `422` : donnees invalides ;
- erreur serveur `5xx` ;
- payload API inattendu.

Comportements attendus :

- la liste doit etre videe si le chargement echoue ;
- les boutons d'action doivent etre desactives pendant un appel API ;
- les erreurs `422` doivent afficher les details utiles lorsque l'API les fournit ;
- les erreurs `401` et `403` doivent etre explicites ;
- apres une erreur de suppression ou modification, la page doit rester utilisable ;
- le bouton `Rafraichir` doit rester disponible apres retour a un etat stable.

## 10. Validation Desktop

Les validations Desktop restent minimales. Les validations metier finales restent cote Backend.

Validations avant envoi :

- `name` obligatoire ;
- `name` avec au moins 2 caracteres ;
- `name` avec longueur raisonnable compatible avec l'API ;
- `description` optionnelle ;
- `is_active` booleen.

Le Desktop ne doit pas dupliquer toute la logique metier Backend.

## 11. Tests

Les tests automatiques attendus concernent la couche Service Desktop.

Fichier a creer lors du futur developpement :

```text
tests/desktop/test_entities_service.py
```

Tests a prevoir :

- chargement de la liste via `GET /entities` ;
- parsing d'une reponse paginee valide ;
- gestion d'une liste vide ;
- creation via `POST /entities` ;
- modification via `PUT /entities/{id}` ;
- suppression via `DELETE /entities/{id}` ;
- mapping des erreurs `401` vers `unauthorized` ;
- mapping des erreurs `403` vers `forbidden` ;
- mapping des erreurs `404` vers `not_found` ;
- mapping des erreurs `409` vers `conflict` ;
- mapping des erreurs `422` vers `validation_error` ;
- mapping des erreurs reseau ;
- mapping du backend indisponible ;
- rejet d'un payload pagine invalide ;
- rejet d'un payload ressource invalide.

Les tests UI PySide6 restent manuels pour ce sprint.

## 12. Criteres D'Acceptation

Le Sprint 14 est termine si :

- la page Entities n'est plus un placeholder ;
- l'utilisateur peut consulter les entites ;
- l'utilisateur peut creer une entite ;
- l'utilisateur peut modifier une entite ;
- l'utilisateur peut supprimer une entite apres confirmation ;
- la liste est rechargee apres chaque operation ;
- le bouton `Rafraichir` reste disponible ;
- les validations Desktop minimales fonctionnent ;
- les erreurs API et reseau sont affichees clairement ;
- le Desktop passe uniquement par `EntitiesService` et `ApiClient` ;
- aucun acces direct a PostgreSQL n'est introduit ;
- aucun modele SQLAlchemy Backend n'est importe dans le Desktop ;
- aucune modification Backend n'est necessaire ;
- Ruff passe ;
- Pytest passe.

## 13. Livrables

Fichiers qui devraient etre crees lors du futur developpement :

- `desktop/services/entities_service.py`
- `desktop/ui/dialogs/entity_dialog.py`
- `tests/desktop/test_entities_service.py`
- `docs/sprints/sprint-14-desktop-entities.md`

Fichiers qui devraient probablement etre modifies lors du futur developpement :

- `desktop/ui/entities_page.py`

Fichiers qui ne devraient pas etre modifies :

- `backend/`
- `backend/alembic/`
- `desktop/core/api_client.py`, sauf bug bloquant demontre ;
- `desktop/services/websites_service.py` ;
- `desktop/ui/websites_page.py` ;
- modeles SQLAlchemy ;
- schemas Pydantic Backend ;
- routes FastAPI ;
- migrations Alembic.

## 14. Risques

Risques techniques identifies :

- duplication du pattern Websites si plusieurs modules Desktop sont copies sans discernement ;
- tentation de creer une abstraction CRUD generique trop tot ;
- confusion entre validation Desktop minimale et validation metier Backend ;
- messages d'erreur incoherents entre Websites et Entities ;
- oubli des erreurs `401` et `403` depuis la securisation Sprint 13 ;
- UX trop technique si des identifiants internes sont exposes inutilement ;
- tests UI non automatises, validation manuelle necessaire.

Strategie de limitation :

- reprendre le pattern Websites sans refactor global ;
- limiter le sprint a Entities ;
- tester uniquement la couche Service avec `MockTransport` ;
- documenter les limites et exclusions ;
- garder les validations Desktop simples.

## 15. Evolutions Prevues

Le module Entities prepare les prochains modules Desktop.

Apports pour la suite :

- Keywords pourra associer les mots-cles a une entite ;
- Competitors pourra associer les concurrents a une entite ;
- Reports pourra filtrer ou rattacher les rapports a une entite ;
- Project Tasks pourra rattacher les taches projet a une entite ;
- Websites pourra etre ameliore ulterieurement avec une selection d'entite plus ergonomique.

Le Sprint 14 pose donc le socle metier commun sans elargir le perimetre fonctionnel.

## Roadmap

Feuille de route previsionnelle :

- Sprint 14 - Module Desktop Entities
- Sprint 15 - Module Desktop Keywords
- Sprint 16 - Module Desktop Competitors
- Sprint 17 - Module Desktop URLs
- Sprint 18 - Module Desktop Project Tasks
- Sprint 19 - Module Desktop Reports (consultation)
- Sprint 20 - Dashboard enrichi avec donnees metier reelles

Cette feuille de route est indicative. Elle pourra evoluer selon les besoins metier, les retours utilisateurs et les
contraintes techniques identifiees pendant les prochains sprints.
