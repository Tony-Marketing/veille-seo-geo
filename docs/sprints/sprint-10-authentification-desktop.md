# Sprint 10 - Authentification Desktop et session utilisateur

## 1. Titre du sprint

**Sprint 10 - Authentification Desktop et session utilisateur**

## 2. Statut

**Prévu / à cadrer**

Ce document cadre le Sprint 10. Il ne constitue pas une implémentation du sprint.

## 3. Contexte

Le projet **Veille SEO-GEO Groupe A.P&Partner** dispose déjà d'une première base Desktop et d'une communication initiale avec l'API FastAPI.

- Le Sprint 08 a posé le shell Desktop PySide6 : fenêtre principale, thème sombre, sidebar, page Tableau de bord et affichage d'état backend.
- Le Sprint 09 consolide la communication `Desktop -> FastAPI`, notamment autour de `desktop/core/api_client.py`, des erreurs API structurées et des tests sans réseau réel via un transport `httpx` optionnel.
- Le Sprint 10 doit préparer l'authentification du Desktop avant l'arrivée des vrais modules métier protégés.

Le Desktop doit rester un client HTTP REST. Il ne doit jamais accéder directement à PostgreSQL ni importer les modèles SQLAlchemy backend.

## 4. Objectif principal

L'objectif principal du Sprint 10 est de permettre au client Desktop de s'authentifier proprement auprès de l'API FastAPI et de préparer une session utilisateur Desktop basée sur un token API.

Le sprint devra notamment permettre de :

- analyser l'existant côté authentification backend ;
- identifier les routes, schémas, services et dépendances de sécurité déjà disponibles ;
- préparer l'authentification Desktop sans couplage direct au backend ;
- permettre à terme une session utilisateur Desktop basée sur un token API ;
- ajouter le header `Authorization: Bearer <token>` aux appels API authentifiés ;
- gérer proprement les erreurs `401 Unauthorized` et `403 Forbidden` côté Desktop ;
- préparer la protection des pages sensibles côté Desktop, sans remplacer la protection backend.

## 5. Périmètre fonctionnel prévu

Le périmètre fonctionnel prévu pour le Sprint 10 couvre :

- analyse des routes d'authentification backend existantes ;
- analyse des schémas Pydantic d'authentification existants ;
- analyse des services d'authentification existants ;
- vérification des repositories éventuellement impliqués dans l'authentification ;
- préparation d'un écran ou d'une boîte de dialogue de connexion Desktop ;
- envoi identifiant / mot de passe à l'API FastAPI ;
- stockage temporaire du token en mémoire pendant la session Desktop ;
- injection automatique du Bearer token dans les appels API authentifiés ;
- gestion explicite des erreurs d'authentification ;
- gestion des réponses `401` et `403` avec messages utilisateur lisibles ;
- déconnexion ;
- effacement de la session en mémoire lors de la déconnexion ;
- affichage de l'utilisateur connecté dans l'interface ;
- préparation de la protection des pages sensibles côté Desktop.

Ce périmètre devra être confirmé après analyse de l'existant. Aucune route, aucun service et aucun schéma ne doivent être recréés s'ils existent déjà.

## 6. Hors périmètre

Sont explicitement hors périmètre du Sprint 10 :

- refresh token complet si le backend ne le prévoit pas déjà ;
- stockage persistant sécurisé du token ;
- coffre-fort de secrets ;
- gestion avancée des rôles dans l'interface Desktop ;
- CRUD métier ;
- GEO Monitor ;
- refonte graphique du Desktop ;
- migrations Alembic ;
- modifications des modèles SQLAlchemy ;
- modification structurelle de la base PostgreSQL ;
- accès direct du Desktop à PostgreSQL ;
- import de modèles SQLAlchemy backend dans le Desktop ;
- contournement des routes FastAPI ;
- refactor global du backend ;
- refactor global du Desktop.

## 7. Architecture attendue

L'architecture attendue reste :

```text
Desktop -> FastAPI -> Services -> Repositories -> Models -> PostgreSQL
```

Règles obligatoires :

- les routes FastAPI appellent les services ;
- les services contiennent la logique métier ;
- les repositories contiennent uniquement l'accès aux données SQLAlchemy ;
- les modèles SQLAlchemy représentent les tables ;
- les schémas Pydantic gèrent les entrées et sorties API ;
- le Desktop communique uniquement avec FastAPI via HTTP REST ;
- le Desktop ne se connecte jamais directement à PostgreSQL ;
- le Desktop n'importe jamais les modèles SQLAlchemy backend ;
- le Desktop reste découplé du backend et ne duplique pas les règles de sécurité métier.

Le Desktop peut masquer ou désactiver certaines pages selon l'état de session, mais la protection réelle des endpoints sensibles doit rester côté backend.

## 8. Fichiers susceptibles d'être concernés plus tard

La liste suivante est indicative. Elle ne doit pas être appliquée automatiquement.

Le Sprint 10 devra commencer par une analyse de l'existant avant toute implémentation, puis confirmer les fichiers réellement nécessaires.

| Fichier | Rôle potentiel |
| --- | --- |
| `desktop/core/api_client.py` | Injection du Bearer token et gestion structurée des erreurs auth |
| `desktop/core/auth.py` | Utilitaires Desktop liés à l'authentification si ce module est justifié |
| `desktop/core/session.py` | Etat de session utilisateur en mémoire si ce module est justifié |
| `desktop/services/auth_service.py` | Service Desktop responsable des appels auth via `ApiClient` |
| `desktop/ui/login_dialog.py` | Boîte de dialogue de connexion Desktop |
| `desktop/ui/login_page.py` | Page de connexion si une page est préférée à une boîte de dialogue |
| `desktop/ui/main_window.py` | Affichage utilisateur connecté et contrôle d'accès UI minimal |
| `tests/desktop/test_auth_service.py` | Tests du service Desktop d'authentification |
| `tests/desktop/test_api_client_auth.py` | Tests de l'injection Bearer et des erreurs auth dans `ApiClient` |
| `tests/api/test_auth_routes.py` | Tests API auth si l'existant backend le nécessite |

Ces fichiers ne doivent pas être créés ou modifiés avant validation du périmètre réel après analyse.

## 9. Plan d'analyse préalable obligatoire

La première étape du Sprint 10 devra être une analyse technique sans modification.

Cette analyse devra vérifier :

- routes auth backend existantes ;
- schémas auth Pydantic existants ;
- services auth existants ;
- repositories éventuellement impliqués ;
- modèles SQLAlchemy déjà utilisés par l'authentification ;
- dépendances de sécurité FastAPI ;
- mécanisme actuel de génération et validation de token ;
- format exact des réponses d'authentification ;
- format exact des erreurs `401` et `403` ;
- tests auth existants ;
- comportement actuel du Desktop au démarrage ;
- intégration possible dans `ApiClient` sans casser les appels publics comme le healthcheck ;
- structure de session utilisateur adaptée côté Desktop ;
- séparation entre authentification backend et protection visuelle des pages Desktop.

Le résultat attendu de cette analyse est une liste courte des fichiers réellement à créer ou modifier, avec justification, avant toute implémentation.

## 10. Critères d'acceptation prévus

A la fin du Sprint 10, les critères d'acceptation prévus sont :

- le Desktop peut afficher un écran ou une boîte de dialogue de connexion ;
- le Desktop peut appeler l'API d'authentification existante ou validée ;
- un token valide peut être conservé en mémoire pendant la session Desktop ;
- les appels API authentifiés envoient le header `Authorization: Bearer <token>` ;
- les appels publics restent possibles sans token lorsque l'API les autorise ;
- les erreurs `401` et `403` sont gérées proprement côté Desktop ;
- la déconnexion efface la session en mémoire ;
- l'utilisateur connecté est affiché dans l'interface ;
- les pages sensibles peuvent être préparées pour tenir compte de l'état de session ;
- les tests Desktop/API pertinents passent ;
- Ruff passe ;
- Pytest passe ;
- aucune migration Alembic n'est ajoutée sauf décision explicite hors Sprint 10 ;
- aucun accès direct Desktop à PostgreSQL n'est introduit.

## 11. Tests prévus

Les tests à prévoir plus tard, après validation du périmètre réel, sont :

- tests unitaires du service ou de la session d'authentification Desktop ;
- tests de l'injection du Bearer token dans `ApiClient` ;
- tests garantissant l'absence de Bearer token sur les appels publics si nécessaire ;
- tests de gestion `401` ;
- tests de gestion `403` ;
- tests de déconnexion et d'effacement de session en mémoire ;
- tests API auth si l'existant backend le nécessite ;
- tests de non-régression sur le healthcheck ;
- tests de non-régression sur les erreurs réseau déjà couvertes par le Sprint 09.

## 12. Commandes de validation prévues

Commandes PowerShell prévues pour la validation future du Sprint 10 :

```powershell
python -m ruff check desktop tests
python -m pytest tests/desktop tests/api
python -m pytest
git diff --stat
git diff --check
git status --short
```

Ces commandes sont prévues pour la phase d'implémentation du Sprint 10. Le présent document ne lance pas l'implémentation.

## 13. Risques identifiés

Les principaux risques identifiés sont :

- routes auth backend déjà existantes mais comportement non documenté ;
- divergence entre les schémas backend et les attentes Desktop ;
- format de token ou de réponse auth incompatible avec une session Desktop simple ;
- gestion incomplète des erreurs API ;
- confusion entre erreur d'authentification et erreur réseau ;
- couplage excessif entre Desktop et backend ;
- import accidentel de code SQLAlchemy backend dans le Desktop ;
- stockage de token trop précoce ou non sécurisé ;
- confusion entre authentification backend et protection UI ;
- ajout prématuré d'une gestion avancée des rôles côté Desktop ;
- modification inutile de modèles SQLAlchemy ou de migrations Alembic.

## 14. Décision de cadrage

Le Sprint 10 doit commencer par une analyse technique Codex sans modification avant toute implémentation.

L'implémentation ne devra démarrer qu'après confirmation :

- des routes auth backend réellement disponibles ;
- du format de requête et de réponse attendu ;
- de la stratégie de session Desktop en mémoire ;
- des fichiers à créer ou modifier ;
- des tests à ajouter ou adapter.

Ce cadrage confirme que le Sprint 10 vise l'authentification Desktop et la session utilisateur, sans CRUD métier, sans migration Alembic, sans modification de modèles SQLAlchemy et sans accès direct du Desktop à PostgreSQL.
