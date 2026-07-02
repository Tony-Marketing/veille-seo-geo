# Sprint 18 - Module Desktop Project Tasks

## 1. Contexte

Les sprints precedents ont installe les fondations Desktop necessaires aux modules metier :

- le shell Desktop PySide6 et la navigation par modules sont disponibles ;
- le Desktop communique avec FastAPI via `ApiClient` et HTTP REST ;
- l'authentification Desktop transmet automatiquement le token Bearer ;
- les modules Entities, Keywords, Competitors et URLs fournissent le modele CRUD de reference ;
- les services Desktop isolent les appels API, le parsing des reponses et le mapping des erreurs ;
- les pages Desktop restent responsables de l'affichage, des selections, des confirmations et des messages utilisateur.

Le Sprint 18 est consacre au module Desktop Project Tasks.

Le Backend dispose deja d'un CRUD securise pour les Project Tasks. Le sprint ne prevoit aucune evolution Backend et ne
doit traiter que le client Desktop.

## 2. Objectifs

Le Sprint 18 a pour objectifs de cadrer le futur module Desktop de gestion des taches projet SEO/GEO.

Objectifs fonctionnels :

- permettre la consultation paginee des taches projet ;
- permettre la recherche de taches ;
- permettre le rafraichissement manuel de la liste ;
- permettre la creation d'une tache ;
- permettre la modification d'une tache ;
- permettre la suppression d'une tache apres confirmation ;
- appliquer des validations Desktop minimales avant les appels API ;
- afficher des messages utilisateur lisibles ;
- gerer les erreurs HTTP ;
- gerer les erreurs reseau ;
- ajouter des tests automatiques sur la couche Service Desktop lors du developpement.

Objectifs techniques :

- conserver l'architecture `Page -> Service -> ApiClient -> API REST` ;
- reprendre la philosophie des Sprints 14, 15, 16 et 17 ;
- ne pas introduire de nouvelle architecture ;
- ne pas creer d'abstraction CRUD generique ;
- ne pas modifier le Backend ;
- ne pas importer de modele SQLAlchemy dans le Desktop.

## 3. Perimetre

Le sprint couvre uniquement le module Desktop Project Tasks.

Fonctionnalites incluses :

- affichage pagine des taches ;
- recherche textuelle lorsque l'API expose un parametre compatible ;
- rafraichissement manuel de la liste ;
- creation d'une tache ;
- modification de la tache selectionnee ;
- suppression de la tache selectionnee apres confirmation ;
- rechargement automatique apres creation, modification et suppression ;
- boite de dialogue dediee aux taches projet ;
- validations utilisateur avant envoi a l'API ;
- affichage des messages de succes et d'erreur ;
- gestion des erreurs HTTP courantes ;
- gestion des erreurs reseau ;
- tests du service Desktop.

Le sprint reste volontairement limite au CRUD Desktop.

## 4. Hors Perimetre

Le Sprint 18 ne traite pas :

- le Backend ;
- les routes FastAPI ;
- les services Backend ;
- les repositories Backend ;
- les schemas Pydantic Backend ;
- les modeles SQLAlchemy ;
- les migrations Alembic ;
- l'acces direct a PostgreSQL ;
- l'import de modeles SQLAlchemy dans le Desktop ;
- la creation d'une architecture generique ;
- un refactor global des pages CRUD ;
- la planification projet avancee ;
- les diagrammes de Gantt ;
- les notifications ;
- les rappels automatiques ;
- l'assignation intelligente ;
- les automatisations metier ;
- les rapports projet ;
- les statistiques ;
- les graphiques ;
- l'import ou l'export ;
- les tests UI PySide6 automatises si le projet ne dispose pas deja d'une infrastructure dediee.

## 5. Architecture

L'architecture Desktop attendue reste :

```text
ProjectTasksPage
    -> ProjectTasksService
        -> ApiClient
            -> API FastAPI
```

Aucune nouvelle architecture ne doit etre introduite.

Responsabilites attendues :

| Composant | Responsabilite |
| --- | --- |
| `ProjectTasksPage` | Affichage, selection, recherche, pagination, boutons, confirmations et messages utilisateur. |
| `ProjectTasksService` | Appels REST, parsing des reponses, normalisation de la pagination et mapping des erreurs. |
| `ProjectTaskDialog` | Collecte des champs de creation et modification avec validations Desktop minimales. |
| `ApiClient` | Client HTTP generique existant, reutilise sans modification. |

Regles obligatoires :

- le Desktop communique uniquement via HTTP REST ;
- aucune page ne doit appeler directement HTTP ou `httpx` ;
- aucun acces direct a PostgreSQL ;
- aucun import SQLAlchemy ;
- aucune logique metier dans la page ;
- aucune nouvelle instance d'`ApiClient` si une instance existe deja dans `MainWindow`.

## 6. Composants Concernés

Composants a documenter et a creer lors du developpement :

- `desktop/services/project_tasks_service.py`
- `desktop/ui/project_tasks_page.py`
- `desktop/ui/dialogs/project_task_dialog.py`
- `tests/desktop/test_project_tasks_service.py`

Composants pouvant etre modifies lors du developpement :

- `desktop/ui/main_window.py`, uniquement pour l'integration de la page et l'injection de l'`ApiClient` existant ;
- le fichier de constantes ou navigation Desktop, uniquement si le module Project Tasks n'est pas encore reference dans le shell.

Fichiers qui ne doivent pas etre modifies :

- `backend/`
- `backend/alembic/`
- `desktop/core/api_client.py`
- tout fichier hors perimetre du module Desktop Project Tasks.

## 7. Informations D'Une Tache Projet

Le module doit rester adapte au modele reellement expose par l'API.

Les champs possibles a prendre en compte cote Desktop, si disponibles dans l'API, sont :

| Information | Usage Desktop attendu |
| --- | --- |
| Titre | Champ principal affiche dans le tableau et obligatoire si l'API le requiert. |
| Description | Detail optionnel de la tache. |
| Statut | Suivi de l'etat de la tache, par exemple a faire, en cours, terminee ou bloquee. |
| Priorite | Priorisation operationnelle, par exemple basse, moyenne, haute ou urgente. |
| Date d'echeance | Date limite ou objectif de livraison. |
| Site concerne | Rattachement optionnel a un site par identifiant ou libelle si l'API le fournit. |
| Entite concernee | Rattachement optionnel a une entite par identifiant ou libelle si l'API le fournit. |
| Utilisateur assigne | Assignation optionnelle si l'API expose cette information. |

Le Desktop ne doit pas inventer de champ absent de l'API.

Si certains champs ne sont pas exposes par le Backend, ils doivent etre exclus du dialogue et du payload. Le document de
developpement final devra preciser les champs effectivement utilises apres verification des schemas API.

## 8. Flux Applicatif

Flux general :

1. L'utilisateur ouvre le module Project Tasks depuis la navigation Desktop.
2. `ProjectTasksPage` demande la liste a `ProjectTasksService`.
3. `ProjectTasksService` appelle l'API REST via `ApiClient`.
4. `ApiClient` transmet la requete HTTP avec la session courante.
5. `ProjectTasksService` valide et normalise la reponse.
6. `ProjectTasksPage` met a jour le tableau, la pagination et le message utilisateur.

Flux d'ecriture :

1. L'utilisateur ouvre la boite de dialogue de tache projet.
2. `ProjectTaskDialog` collecte les champs exposes par l'API.
3. Le dialogue applique les validations Desktop minimales.
4. `ProjectTasksPage` transmet le payload valide a `ProjectTasksService`.
5. `ProjectTasksService` appelle l'API REST via `ApiClient`.
6. La liste est rechargee apres succes.
7. Un message confirme l'action realisee.

## 9. Parcours Utilisateur

### Consultation

1. L'utilisateur ouvre le module Project Tasks.
2. Le tableau affiche la premiere page de taches.
3. Un message indique le nombre de taches trouvees et la page courante.
4. Les boutons `Modifier` et `Supprimer` restent desactives tant qu'aucune ligne n'est selectionnee.

### Recherche

1. L'utilisateur saisit une recherche.
2. Il valide la recherche ou utilise le bouton dedie.
3. La page recharge la liste avec le terme saisi.
4. Le tableau affiche les resultats pagines.
5. Un message indique si aucune tache ne correspond a la recherche.

### Creation

1. L'utilisateur clique sur `Ajouter`.
2. La boite de dialogue de creation s'ouvre.
3. L'utilisateur renseigne les champs disponibles.
4. Le Desktop valide les champs minimaux.
5. La tache est creee via le service Desktop.
6. La liste est rechargee.
7. Un message confirme la creation.

### Modification

1. L'utilisateur selectionne une tache.
2. Il clique sur `Modifier` ou double-clique sur la ligne.
3. La boite de dialogue est pre-remplie.
4. Le Desktop valide les champs minimaux.
5. La tache est modifiee via le service Desktop.
6. La liste est rechargee.
7. Un message confirme la modification.

### Suppression

1. L'utilisateur selectionne une tache.
2. Il clique sur `Supprimer`.
3. Une confirmation explicite est affichee.
4. Si l'utilisateur confirme, la tache est supprimee via le service Desktop.
5. La liste est rechargee.
6. Un message confirme la suppression.

## 10. Liste Des Ecrans

### Page Project Tasks

Elements attendus :

- titre de page ;
- champ de recherche ;
- bouton de recherche ou validation par entree ;
- bouton `Ajouter` ;
- bouton `Modifier` ;
- bouton `Supprimer` ;
- bouton `Rafraichir` ;
- tableau des taches ;
- indication de pagination ;
- zone de message utilisateur.

### Tableau Des Taches

Le tableau doit :

- afficher les taches recuperees depuis l'API ;
- rester en lecture seule ;
- permettre la selection d'une ligne ;
- activer `Modifier` et `Supprimer` uniquement lorsqu'une tache est selectionnee ;
- afficher uniquement les colonnes issues des donnees exposees par l'API ;
- conserver une presentation coherente avec les modules Keywords, Competitors et URLs.

Colonnes candidates, a confirmer selon l'API :

- titre ;
- statut ;
- priorite ;
- date d'echeance ;
- site ;
- entite ;
- utilisateur assigne.

### Boite De Dialogue Project Task

Le dialogue doit etre place dans :

```text
desktop/ui/dialogs/project_task_dialog.py
```

Il doit :

- servir a la creation et a la modification ;
- pre-remplir les champs en modification ;
- exposer uniquement les champs reellement disponibles dans l'API ;
- appliquer des validations Desktop minimales ;
- produire un payload compatible avec l'API REST ;
- ne contenir aucune logique Backend.

## 11. Fonctionnalités Prévues

| Fonctionnalite | Comportement attendu |
| --- | --- |
| Affichage pagine | Charger les taches avec `page` et `page_size`. |
| Recherche | Envoyer le terme recherche via le service Desktop lorsque l'API le supporte. |
| Rafraichissement | Recharger la page courante avec les filtres actifs. |
| Creation | Ouvrir `ProjectTaskDialog`, valider, appeler le service, recharger la liste. |
| Modification | Utiliser la tache selectionnee, pre-remplir le dialogue, appeler le service. |
| Suppression | Demander confirmation avant l'appel de suppression. |
| Double-clic | Ouvrir la modification de la ligne selectionnee. |
| Messages | Afficher les succes, erreurs HTTP, erreurs reseau et payloads inattendus. |

## 12. Validations Desktop

Les validations Desktop doivent rester minimales. Les validations metier finales restent cote API.

Regles attendues :

- les champs obligatoires selon l'API doivent etre renseignes ;
- les longueurs maximales doivent respecter les contraintes exposees par l'API ;
- les identifiants optionnels doivent etre numeriques lorsqu'ils sont renseignes ;
- les dates doivent etre dans un format compatible avec l'API lorsqu'elles sont renseignees ;
- les valeurs de statut et de priorite doivent rester dans les valeurs acceptees par l'API si elles sont exposees ;
- les champs optionnels vides doivent etre envoyes sous forme compatible avec l'API ;
- aucune regle de gestion projet avancee ne doit etre ajoutee dans le Desktop.

Le Desktop ne doit pas dupliquer toute la logique metier du Backend.

## 13. Gestion Des Erreurs

Le module doit transformer les erreurs techniques en messages utilisateur comprehensibles.

Cas a gerer :

- erreur reseau ;
- timeout ;
- backend indisponible ;
- `401` : utilisateur non authentifie ;
- `403` : permission insuffisante ;
- `404` : tache introuvable ;
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

## 14. Tests Attendus

Les tests automatiques attendus concernent la couche Service Desktop.

Fichier attendu :

```text
tests/desktop/test_project_tasks_service.py
```

Tests a prevoir :

- chargement de la liste via le service Project Tasks ;
- transmission des parametres de pagination ;
- transmission du terme de recherche ;
- parsing d'une reponse paginee valide ;
- gestion d'une liste vide ;
- creation d'une tache ;
- modification d'une tache ;
- suppression d'une tache ;
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

## 15. Criteres D'Acceptation

Le Sprint 18 sera considere termine si :

- la page Project Tasks est fonctionnelle cote Desktop ;
- l'utilisateur peut consulter les taches de maniere paginee ;
- l'utilisateur peut rechercher des taches ;
- l'utilisateur peut creer une tache ;
- l'utilisateur peut modifier une tache ;
- l'utilisateur peut supprimer une tache apres confirmation ;
- la liste est rechargee apres chaque operation ;
- les erreurs HTTP et reseau sont affichees clairement ;
- les validations Desktop minimales fonctionnent ;
- le Desktop passe uniquement par `ProjectTasksService` et `ApiClient` ;
- aucun acces direct a PostgreSQL n'est introduit ;
- aucun modele SQLAlchemy Backend n'est importe dans le Desktop ;
- le Backend reste inchange ;
- Ruff passe ;
- Pytest passe.

## 16. Risques

Risques identifies :

- ajouter des fonctionnalites de planification avancee dans un sprint limite au CRUD ;
- introduire une abstraction CRUD generique trop tot ;
- dupliquer de la logique metier Backend dans la page Desktop ;
- exposer trop d'identifiants techniques dans l'interface ;
- supposer des champs non exposes par l'API ;
- oublier de conserver la recherche lors de la pagination ;
- ne pas conserver le contexte de recherche apres creation, modification ou suppression ;
- modifier accidentellement `ApiClient` ou le Backend ;
- creer des tests UI hors infrastructure existante.

Mesures de limitation :

- reprendre les patterns de Keywords, Competitors et URLs ;
- verifier les schemas API avant implementation ;
- limiter le dialogue aux champs reellement exposes par l'API ;
- isoler les appels REST dans `ProjectTasksService` ;
- tester uniquement la couche Service Desktop ;
- documenter les limites fonctionnelles ;
- verifier que seuls les fichiers Desktop et documentation prevus sont modifies.

## 17. Livrables

Livrables attendus lors du developpement :

- `desktop/services/project_tasks_service.py`
- `desktop/ui/project_tasks_page.py`
- `desktop/ui/dialogs/project_task_dialog.py`
- `tests/desktop/test_project_tasks_service.py`
- `docs/sprints/sprint-18-desktop-project-tasks.md`

Fichiers pouvant etre modifies :

- `desktop/ui/main_window.py`, uniquement pour l'injection de l'`ApiClient` existant et l'integration de la page ;
- fichier de constantes ou navigation Desktop, uniquement si necessaire pour rendre le module accessible.

Fichiers explicitement exclus :

- `backend/`
- `backend/alembic/`
- `desktop/core/api_client.py`
- fichiers hors perimetre du module Project Tasks.

## 18. Checklist De Validation

Avant cloture du Sprint 18 :

- [ ] architecture `Page -> Service -> ApiClient -> API REST` respectee ;
- [ ] aucune modification Backend ;
- [ ] aucun acces direct a PostgreSQL ;
- [ ] aucun import SQLAlchemy dans le Desktop ;
- [ ] aucune nouvelle architecture generique ;
- [ ] champs confirmes depuis l'API avant implementation ;
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
- [ ] documentation Sprint 18 a jour.

## 19. Prochaines Etapes

Apres validation du Sprint 18, la suite previsionnelle pourra porter sur :

- le module Desktop Reports ;
- l'enrichissement progressif du Dashboard avec des donnees metier reelles ;
- l'amelioration de l'ergonomie des filtres transverses ;
- l'ajout eventuel de vues projet plus avancees si un besoin utilisateur est confirme.

Ces evolutions devront rester separees du Sprint 18 afin de conserver un perimetre clair et livrable.
