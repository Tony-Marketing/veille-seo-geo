# Stratégie de tests - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit la stratégie de tests du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence pour écrire, organiser, exécuter et relire les tests backend, Desktop et futurs tests React.

Objectifs :

- vérifier les comportements utiles ;
- limiter les régressions ;
- sécuriser les endpoints sensibles ;
- valider les règles métier ;
- contrôler les contrats API ;
- garder les tests simples, ciblés et maintenables ;
- guider les interventions assistées par Codex.

## 2. Périmètre de la stratégie de tests

La stratégie couvre :

| Domaine | Tests concernés |
| --- | --- |
| Backend FastAPI | routes, services, repositories, schemas, erreurs |
| SQLAlchemy | repositories, transactions, contraintes, modèles |
| Alembic | migrations explicites, upgrade, cohérence structurelle |
| Pydantic v2 | validations, entrées, sorties |
| Sécurité | authentification, autorisation, données sensibles |
| Desktop PySide6 | services Desktop, client API, erreurs réseau, formulaires |
| httpx | appels mockés, timeouts, statuts HTTP |
| React futur | composants, services API, contrats |
| Non-régression | bugs corrigés, scénarios critiques |

Les tests ne doivent jamais dépendre de secrets réels ni d'un fichier `.env` réel.

## 3. Principes généraux

Principes obligatoires :

- tester les comportements, pas seulement l'existence des fichiers ;
- garder les tests lisibles ;
- tester les cas nominaux, limites et erreurs ;
- isoler les tests ;
- éviter les dépendances réseau réelles ;
- éviter les secrets réels ;
- éviter les tests destructifs sur une base réelle ;
- privilégier des fixtures explicites ;
- ne pas mocker tellement largement que le test ne valide plus rien d'utile.

Un test acceptable doit pouvoir expliquer quel comportement métier ou technique il protège.

## 4. Stack de tests officielle

| Usage | Outil |
| --- | --- |
| Tests Python | Pytest |
| Client API de test | FastAPI `TestClient` |
| Linting | Ruff |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Desktop | PySide6, services testables |
| HTTP Desktop | httpx mocké |
| Frontend futur | à valider lors de l'implémentation React |

Les commandes doivent être lancées depuis le dossier local officiel du projet.

## 5. Rôle de Pytest

Pytest est l'outil central pour :

- exécuter les tests backend ;
- organiser les fixtures ;
- tester les routes API ;
- tester les services métier ;
- tester les repositories ;
- tester les validations Pydantic ;
- tester les services Desktop ;
- contrôler les régressions.

Commande globale :

```powershell
pytest
```

## 6. Rôle de Ruff dans la validation qualité

Ruff complète les tests.

Il vérifie :

- erreurs de syntaxe ou imports ;
- imports inutilisés ;
- style Python ;
- règles de lint configurées ;
- compatibilité de certaines constructions modernes.

Commande :

```powershell
ruff check .
```

Ruff ne remplace pas les tests métier.

## 7. Structure recommandée du dossier `tests/`

Structure actuelle :

```text
tests/
  api/
  services/
  conftest.py
```

Structure recommandée à terme, à valider selon les besoins :

```text
tests/
  api/
  services/
  repositories/
  schemas/
  migrations/
  desktop/
  conftest.py
```

Ne pas créer de nouveau dossier de test sans besoin réel.

## 8. Types de tests attendus

| Type | Objectif | Exemple |
| --- | --- | --- |
| Unitaire | tester une règle isolée | service métier |
| Intégration | tester plusieurs couches | route + service + DB test |
| API | tester contrat HTTP | statut, JSON |
| Repository | tester requête SQLAlchemy | filtrage, pagination |
| Schema | tester validation Pydantic | champ invalide |
| Migration | tester évolution DB | `alembic upgrade head` |
| Desktop | tester client/service UI | appel API mocké |
| Sécurité | tester auth et droits | 401, 403 |
| Non-régression | verrouiller un bug corrigé | cas spécifique |

## 9. Tests unitaires

Les tests unitaires ciblent un comportement précis.

Recommandé pour :

- fonctions de validation ;
- services métier ;
- helpers ;
- services Desktop ;
- parsing de réponses API ;
- erreurs métier.

Un test unitaire doit être rapide et isolé.

## 10. Tests d'intégration

Les tests d'intégration vérifient plusieurs couches ensemble.

Exemples :

- route FastAPI avec `TestClient` ;
- service + repository + base de test ;
- import de configuration simulé ;
- pagination API complète.

Ils doivent rester déterministes et ne pas toucher une base réelle non dédiée.

## 11. Tests API FastAPI

Les tests API vérifient :

- chemin HTTP ;
- méthode HTTP ;
- code de statut ;
- payload JSON ;
- authentification ;
- autorisation ;
- pagination ;
- filtrage ;
- erreurs standardisées.

Exemple de commande :

```powershell
pytest tests/api
```

## 12. Tests de routes

Les routes doivent être testées comme contrats HTTP.

À vérifier :

- `200`, `201`, `204` selon action ;
- `401` sans authentification ;
- `403` sans permission ;
- `404` ressource absente ;
- `409` conflit métier ;
- `422` payload invalide.

Les tests de routes ne doivent pas vérifier toute l'implémentation interne du service.

## 13. Tests de services

Les tests de services vérifient la logique métier.

À tester :

- validation métier ;
- doublons ;
- conflits ;
- droits métier ;
- transformations ;
- erreurs attendues ;
- appels repositories lorsque pertinent.

Commande :

```powershell
pytest tests/services
```

## 14. Tests de repositories

Les tests de repositories vérifient l'accès aux données.

À tester lorsque nécessaire :

- création ;
- lecture ;
- mise à jour ;
- suppression contrôlée ;
- filtres ;
- pagination ;
- tri ;
- contraintes.

Les repositories ne doivent pas contenir de logique métier.

## 15. Tests de modèles SQLAlchemy

Les tests de modèles sont utiles pour :

- relations ;
- valeurs par défaut ;
- contraintes ;
- champs d'audit ;
- cohérence de mapping.

Ils ne remplacent pas les tests de migrations Alembic.

## 16. Tests de schémas Pydantic v2

Les tests de schemas vérifient :

- champs obligatoires ;
- types ;
- longueurs ;
- formats ;
- validateurs ;
- sérialisation de sortie ;
- non-exposition de champs sensibles.

Un schema d'entrée doit refuser ce que l'API ne doit pas accepter.

## 17. Tests de migrations Alembic

Les tests de migrations doivent vérifier les migrations explicites.

Recommandé :

- `alembic current` ;
- `alembic history` ;
- `alembic upgrade head` sur base dédiée ;
- vérification des tables ou colonnes attendues ;
- vérification des contraintes importantes.

Ne pas utiliser `Base.metadata.create_all()` pour valider une migration Alembic.

## 18. Tests d'authentification

Les tests d'authentification vérifient :

- connexion valide ;
- identifiants invalides ;
- token absent ;
- token expiré ;
- token invalide ;
- accès utilisateur inactif.

Les tokens de test doivent être générés par les helpers de test, pas copiés depuis un environnement réel.

## 19. Tests d'autorisation

Les tests d'autorisation vérifient les droits.

Cas à couvrir :

- utilisateur sans permission ;
- utilisateur avec permission ;
- admin ;
- rôle insuffisant ;
- accès à une ressource hors périmètre.

Un endpoint sensible doit avoir au moins un test de refus.

## 20. Tests des endpoints admin

Les endpoints admin doivent être testés strictement.

À vérifier :

- `401` sans session ;
- `403` sans droit ;
- succès avec droit adapté ;
- validation des entrées ;
- absence de secret dans les réponses ;
- erreurs contrôlées.

Les actions admin destructrices doivent être couvertes par tests et confirmations côté client si applicable.

## 21. Tests de pagination

La pagination doit vérifier :

- page par défaut ;
- `page_size` par défaut ;
- limite maximale ;
- page vide ;
- total ;
- nombre de pages ;
- ordre stable.

Exemple attendu :

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0
}
```

## 22. Tests de filtrage

Le filtrage doit vérifier :

- filtre simple ;
- combinaison de filtres ;
- filtre inconnu ;
- valeur invalide ;
- absence de résultat ;
- sécurité contre injection.

Les filtres doivent être construits avec SQLAlchemy, pas par concaténation SQL.

## 23. Tests de gestion d'erreurs

Les tests d'erreurs doivent vérifier :

- message clair ;
- code HTTP adapté ;
- absence de stack trace ;
- absence de secret ;
- format JSON cohérent ;
- comportement stable.

Une erreur doit être utile pour l'utilisateur ou le client API sans exposer l'interne.

## 24. Tests des imports/exports de configuration

Les imports/exports doivent être testés comme opérations sensibles.

À vérifier :

- format valide ;
- format invalide ;
- idempotence ;
- doublons ;
- aucune suppression implicite ;
- rapport d'import ;
- absence de secret exporté ;
- rollback ou état cohérent en cas d'erreur.

Les tests ne doivent pas modifier une configuration réelle.

## 25. Tests des modules SEO

Les tests SEO peuvent couvrir :

- audits d'URL ;
- balises ;
- contenus ;
- positions ;
- Core Web Vitals ;
- maillage interne ;
- filtres par site ou projet.

Les appels externes doivent être mockés.

## 26. Tests des modules GEO

Les tests GEO peuvent couvrir :

- prompts ;
- réponses IA ;
- citations ;
- scores de visibilité ;
- fournisseurs ;
- modèles ;
- historique ;
- comparaison.

Les clés API IA ne doivent jamais être nécessaires dans les tests.

## 27. Tests des mots-clés

Les tests mots-clés doivent couvrir :

- création ;
- doublons ;
- import ;
- pagination ;
- recherche ;
- filtrage ;
- historique de position si implémenté.

Les imports doivent vérifier les lignes invalides.

## 28. Tests des contenus

Les tests contenus peuvent couvrir :

- création ou lecture de contenu ;
- métadonnées SEO ;
- qualité éditoriale ;
- filtres par site ;
- contenu introuvable ;
- accès non autorisé.

Ne pas inclure de données sensibles réelles dans les fixtures.

## 29. Tests des concurrents

Les tests concurrents doivent vérifier :

- rattachement à un site, projet ou marché ;
- doublons de domaine ;
- listes paginées ;
- comparaisons ;
- droits d'accès.

Les données stratégiques doivent rester fictives.

## 30. Tests des rapports

Les tests rapports doivent couvrir :

- liste des rapports ;
- génération si synchrone ;
- statut de génération si asynchrone ;
- filtres par période ;
- permissions ;
- erreur de rapport introuvable.

Les rapports volumineux doivent être testés avec des données réduites.

## 31. Tests des sites web

Les tests sites web doivent couvrir :

- création ;
- validation de domaine ou URL ;
- doublons ;
- activation/désactivation ;
- pagination ;
- filtrage ;
- suppression contrôlée si prévue.

Ces tests protègent une base transversale des modules SEO/GEO.

## 32. Tests de sécurité backend

Les tests de sécurité backend doivent vérifier :

- endpoints sensibles protégés ;
- permissions ;
- absence de secrets ;
- erreurs sobres ;
- validation stricte ;
- refus des accès non autorisés ;
- absence de stack trace dans la réponse.

Une correction sécurité doit ajouter un test de non-régression.

## 33. Tests de non-régression

Un test de non-régression verrouille un bug corrigé.

Il doit :

- reproduire le bug ;
- échouer avant correction ;
- passer après correction ;
- rester ciblé ;
- utiliser un nom clair.

Exemple de nom :

```python
def test_websites_pagination_keeps_total_when_search_is_empty():
    ...
```

## 34. Tests Desktop PySide6

Les tests Desktop doivent être progressifs.

À tester en priorité :

- client API ;
- services Desktop ;
- parsing de réponses ;
- erreurs réseau ;
- formulaires ;
- vues critiques.

Les tests UI complets sont à prévoir selon l'outillage validé.

## 35. Tests des services Desktop

Les services Desktop doivent être testables sans lancer toute l'application.

À vérifier :

- paramètres API ;
- transformation légère pour l'UI ;
- gestion des erreurs ;
- pagination ;
- filtrage.

Ils ne doivent pas appliquer les règles métier backend.

## 36. Tests des appels API avec `httpx`

Les appels `httpx` doivent être testés avec mocks.

À couvrir :

- succès ;
- `401` ;
- `403` ;
- `404` ;
- `422` ;
- `500` ;
- timeout ;
- erreur réseau ;
- réponse non JSON.

Ne pas faire d'appel réseau réel dans un test unitaire.

## 37. Tests des erreurs réseau Desktop

Les erreurs réseau doivent produire une erreur lisible.

Cas :

- API indisponible ;
- connexion refusée ;
- timeout ;
- DNS ;
- certificat ;
- réponse interrompue.

Le Desktop ne doit pas crasher.

## 38. Tests des timeouts Desktop

Les timeouts doivent être testés si le client API les gère.

À vérifier :

- exception `httpx.TimeoutException` simulée ;
- message utilisateur ;
- état UI restauré ;
- absence de retry infini.

## 39. Tests des formulaires Desktop

Les tests de formulaires peuvent couvrir :

- champs obligatoires ;
- format ;
- bouton désactivé ;
- conservation des valeurs après erreur ;
- affichage des erreurs `422` ;
- confirmation pour action sensible.

À automatiser progressivement.

## 40. Tests des vues critiques Desktop

Vues critiques :

- connexion ;
- administration ;
- configuration ;
- imports/exports ;
- rapports ;
- modules SEO/GEO principaux.

Si l'automatisation UI n'est pas encore disponible, documenter les validations manuelles.

## 41. Tests futurs React

Les tests React seront définis lorsque le frontend sera lancé.

À prévoir :

- tests de composants ;
- tests de services API ;
- tests de formulaires ;
- tests d'erreurs ;
- tests d'authentification ;
- tests de droits ;
- tests de non-régression UI.

Le futur React doit consommer les mêmes contrats API que le Desktop.

## 42. Données de test

Les données de test doivent être :

- fictives ;
- non sensibles ;
- minimales ;
- lisibles ;
- déterministes ;
- adaptées au cas testé.

À éviter :

- données client réelles ;
- secrets ;
- tokens réels ;
- grands volumes sans besoin.

## 43. Fixtures Pytest

Les fixtures Pytest servent à préparer un contexte.

Exemples :

- session base de test ;
- client FastAPI ;
- utilisateur admin ;
- headers d'authentification ;
- repository ;
- service ;
- données métier.

Une fixture doit rester claire et ne pas masquer trop de comportement.

## 44. Mocks et doubles de test

Les mocks servent à isoler un composant.

Utilisations pertinentes :

- appels HTTP externes ;
- client API Desktop ;
- fournisseur IA ;
- service tiers ;
- horloge ;
- génération de fichiers.

À éviter :

- mocker le service dans un test censé tester le service ;
- mocker tout le backend dans un test API ;
- valider seulement que le mock a été appelé sans vérifier le résultat utile.

## 45. Tests avec base de données

Les tests avec base vérifient :

- repositories ;
- contraintes ;
- transactions ;
- intégration route/service/repository ;
- comportements liés aux relations.

La base de test doit être isolée.

Le projet peut utiliser une base en mémoire pour certains tests, mais les migrations Alembic doivent être validées par Alembic, pas par `Base.metadata.create_all()`.

## 46. Tests sans base de données

Les tests sans base conviennent pour :

- logique pure ;
- validations Pydantic ;
- services avec repository mocké ;
- services Desktop ;
- parsing de réponse ;
- helpers.

Ils sont rapides et utiles pour les règles isolées.

## 47. Tests des transactions SQLAlchemy

Les transactions doivent être testées lorsque :

- plusieurs écritures sont liées ;
- un rollback est attendu ;
- un import doit rester cohérent ;
- une erreur partielle peut survenir.

À vérifier :

- état après succès ;
- état après échec ;
- absence de données partielles non voulues.

## 48. Isolation des tests

Chaque test doit être isolé.

Règles :

- pas de dépendance à l'ordre d'exécution ;
- pas de données partagées modifiables sans reset ;
- fixtures propres ;
- pas de secrets globaux ;
- pas d'appel réseau réel non contrôlé.

Un test doit passer seul et dans la suite complète.

## 49. Nettoyage après test

Le nettoyage doit supprimer :

- données temporaires ;
- fichiers temporaires ;
- overrides FastAPI ;
- mocks ;
- variables d'environnement de test ;
- sessions ouvertes.

Les fixtures doivent utiliser `yield` lorsque le nettoyage est nécessaire.

## 50. Tests idempotents

Un test idempotent peut être relancé sans changer le résultat.

Règles :

- données créées dans le test ou fixture ;
- pas de dépendance à l'horloge réelle sauf contrôlée ;
- pas de dépendance à un service externe ;
- nettoyage après exécution.

Les imports/exports de configuration doivent être testés avec cette exigence.

## 51. Tests déterministes

Un test déterministe donne le même résultat à chaque exécution.

À contrôler :

- dates ;
- ordre de liste ;
- générateurs aléatoires ;
- timeouts ;
- réseau ;
- données initiales.

Si l'ordre compte, ajouter un tri explicite.

## 52. Tests à éviter

À éviter :

- test qui vérifie seulement qu'un fichier existe ;
- test qui dépend d'un secret réel ;
- test qui appelle une vraie API externe ;
- test destructif sur base réelle ;
- test qui passe seulement selon l'heure ;
- test trop large et difficile à diagnostiquer ;
- test tellement mocké qu'aucun comportement réel n'est validé.

## 53. Nommage des fichiers de tests

Convention :

```text
test_<module>.py
```

Exemples :

```text
tests/api/test_websites_routes.py
tests/services/test_websites_services.py
tests/repositories/test_websites_repository.py
tests/schemas/test_websites_schemas.py
tests/desktop/test_api_client.py
```

Le nom doit indiquer le domaine et la couche.

## 54. Nommage des fonctions de tests

Convention :

```python
def test_<comportement_attendu>():
    ...
```

Exemples :

```python
def test_create_website_rejects_duplicate_domain():
    ...

def test_list_websites_returns_paginated_response():
    ...
```

Un nom de test doit être compréhensible sans lire tout le corps.

## 55. Organisation par module

Organisation par module :

```text
tests/api/test_websites_routes.py
tests/services/test_websites_services.py
tests/api/test_admin_routes.py
tests/services/test_admin_services.py
```

Cette approche est adaptée quand les modules sont indépendants.

## 56. Organisation par couche applicative

Organisation par couche :

```text
tests/api/
tests/services/
tests/repositories/
tests/schemas/
tests/desktop/
```

Cette approche facilite la revue par responsabilité.

Le projet utilise déjà `tests/api/` et `tests/services/`.

## 57. Tests des cas nominaux

Un cas nominal vérifie le comportement attendu.

Exemples :

- création réussie ;
- liste paginée ;
- lecture d'une ressource ;
- mise à jour valide ;
- import valide ;
- connexion réussie.

Les cas nominaux ne suffisent pas seuls.

## 58. Tests des cas limites

Cas limites :

- page vide ;
- `page_size` maximal ;
- chaîne vide ;
- longueur maximale ;
- date de début égale date de fin ;
- liste sans élément ;
- utilisateur sans rôle.

Les cas limites préviennent les régressions discrètes.

## 59. Tests des cas d'erreur

Cas d'erreur :

- payload invalide ;
- ressource absente ;
- conflit ;
- accès interdit ;
- token expiré ;
- erreur réseau ;
- réponse API inattendue.

Un bon test d'erreur vérifie aussi que l'état reste cohérent.

## 60. Tests des droits insuffisants

Les droits insuffisants doivent produire `403`.

À tester :

- endpoint admin ;
- suppression ;
- export sensible ;
- modification de configuration ;
- accès à une ressource protégée.

Ne pas confondre `401` et `403`.

## 61. Tests des ressources introuvables

Une ressource absente doit produire `404`.

À tester :

- id inexistant ;
- ressource supprimée ;
- ressource hors périmètre si l'API choisit de masquer son existence.

La réponse ne doit pas exposer d'informations internes.

## 62. Tests des conflits

Un conflit métier doit produire `409`.

Exemples :

- doublon ;
- action impossible dans l'état actuel ;
- modification concurrente ;
- import déjà appliqué.

Le message doit être clair.

## 63. Tests des validations Pydantic

Les validations Pydantic doivent produire `422` côté API.

À tester :

- champ manquant ;
- type invalide ;
- longueur invalide ;
- format invalide ;
- valeur hors limite.

Les tests de schema peuvent aussi instancier directement le modèle Pydantic.

## 64. Tests des contraintes PostgreSQL

Les contraintes importantes doivent être couvertes.

Exemples :

- unicité ;
- non-null ;
- clé étrangère ;
- contrainte de domaine ;
- index unique.

Ces tests doivent utiliser une base de test contrôlée.

## 65. Tests des migrations explicites

Une migration explicite doit être testée avec Alembic.

Commande :

```powershell
alembic upgrade head
```

À vérifier :

- table créée ;
- colonne ajoutée ;
- index créé ;
- contrainte créée ;
- données existantes préservées si applicable.

## 66. Interdiction de tester via `Base.metadata.create_all()` dans les migrations

Pour tester une migration, ne pas faire :

```python
Base.metadata.create_all(bind=engine)
```

Cette commande ne teste pas Alembic. Elle crée les tables depuis l'état courant des modèles et peut masquer une migration absente ou incorrecte.

## 67. Interdiction de tester via `Base.metadata.drop_all()` dans les migrations

Pour tester une migration, ne pas faire :

```python
Base.metadata.drop_all(bind=engine)
```

Cette commande ne valide pas le cycle Alembic et peut être dangereuse si elle vise une mauvaise base.

Les migrations doivent être testées par Alembic sur base dédiée.

## 68. Tests des réponses JSON

Les réponses JSON doivent être vérifiées.

À tester :

- champs attendus ;
- absence de champs sensibles ;
- types ;
- format de pagination ;
- format d'erreur ;
- cohérence des valeurs.

Exemple :

```python
payload = response.json()
assert "items" in payload
assert "password" not in payload
```

## 69. Tests des codes HTTP

Les codes HTTP doivent être explicites.

| Code | Test attendu |
| --- | --- |
| `200` | lecture réussie |
| `201` | création réussie |
| `204` | suppression sans contenu |
| `401` | non authentifié |
| `403` | non autorisé |
| `404` | introuvable |
| `409` | conflit |
| `422` | validation |
| `500` | erreur interne sans détails sensibles |

## 70. Tests des logs, si pertinent

Les logs peuvent être testés si le comportement est critique.

À vérifier :

- événement important journalisé ;
- niveau adapté ;
- absence de secret ;
- présence d'un identifiant utile.

Ne pas rendre les tests fragiles en vérifiant tout le texte d'un log si ce n'est pas nécessaire.

## 71. Tests des données sensibles non exposées

À tester pour endpoints sensibles :

- pas de mot de passe ;
- pas de hash si non nécessaire ;
- pas de token ;
- pas de clé API ;
- pas de secret ;
- pas de stack trace.

Exemple :

```python
payload_text = response.text.lower()
assert "password" not in payload_text
assert "token" not in payload_text
```

Adapter selon le contexte pour éviter les faux positifs.

## 72. Commandes PowerShell pour lancer les tests

Commandes générales :

```powershell
pytest
pytest tests
ruff check .
git diff --check
```

Commandes ciblées :

```powershell
pytest tests/api
pytest tests/services
pytest tests/api/test_websites_routes.py
pytest tests/services/test_websites_services.py
```

## 73. Commandes Pytest recommandées

Commandes :

```powershell
pytest
pytest -q
pytest -x
pytest tests/api -q
pytest tests/services -q
pytest tests/api/test_admin_routes.py::test_nom_du_test
```

`pytest -x` arrête à la première erreur, utile pour diagnostiquer rapidement.

## 74. Commandes Ruff recommandées

Commandes :

```powershell
ruff check .
ruff check backend
ruff check desktop
ruff check tests
ruff check backend tests
```

Corriger uniquement dans le périmètre demandé.

## 75. Commandes de validation avant commit

Avant commit :

```powershell
git status --short
git diff
git diff --cached
git diff --check
ruff check .
pytest
```

Codex ne doit pas exécuter `git add`, `git commit` ou `git push` sans demande explicite.

## 76. Commandes de diagnostic en cas d'échec

Diagnostic Pytest :

```powershell
pytest -x -vv
pytest tests/api/test_websites_routes.py -vv
```

Diagnostic Git :

```powershell
git status --short
git diff
git diff --cached
```

Diagnostic Ruff :

```powershell
ruff check . --show-fixes
```

Ne pas corriger hors périmètre sans validation.

## 77. Workflow de test avant Pull Request

Workflow recommandé :

```text
relire le diff
   |
   v
git diff --check
   |
   v
ruff check .
   |
   v
pytest ciblé
   |
   v
pytest global si pertinent
   |
   v
documenter résultats dans la PR
```

Si une commande n'est pas exécutée, le signaler.

## 78. Workflow de test avec Codex

Workflow recommandé :

1. indiquer la branche ;
2. indiquer les fichiers autorisés ;
3. demander l'analyse des tests existants ;
4. demander des tests ciblés ;
5. demander Ruff et Pytest ;
6. demander un compte rendu ;
7. interdire commit et push sauf demande.

Codex doit signaler les tests non exécutés.

## 79. Ce que Codex peut faire pour les tests

Codex peut :

- analyser les tests existants ;
- proposer des cas de test ;
- créer un fichier de test explicitement demandé ;
- modifier un test explicitement autorisé ;
- lancer Pytest ;
- lancer Ruff ;
- diagnostiquer un échec ;
- produire un rapport.

## 80. Ce que Codex ne doit pas faire sans validation explicite

Codex ne doit pas :

- modifier des fichiers hors périmètre ;
- supprimer un test ;
- désactiver un test ;
- marquer un test en skip sans justification ;
- changer la configuration globale Pytest ;
- modifier les fixtures partagées sans validation ;
- utiliser des secrets réels ;
- commiter ;
- pousser.

## 81. Exemple conceptuel de test de route FastAPI

Exemple conceptuel :

```python
def test_list_websites_returns_paginated_response(client, admin_headers):
    response = client.get("/api/v1/websites", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert "total" in payload
```

Adapter aux fixtures et permissions existantes.

## 82. Exemple conceptuel de test de service

Exemple conceptuel :

```python
def test_create_website_rejects_duplicate_domain(service, repository):
    repository.create({"name": "Example", "domain": "example.com"})

    with pytest.raises(WebsiteAlreadyExistsError):
        service.create_website(WebsiteCreate(name="Example 2", domain="example.com"))
```

Le test cible la règle métier.

## 83. Exemple conceptuel de test de repository

Exemple conceptuel :

```python
def test_repository_get_by_domain_returns_matching_row(repository):
    created = repository.create({"name": "Example", "domain": "example.com"})

    result = repository.get_by_domain("example.com")

    assert result == created
```

Le test vérifie l'accès aux données.

## 84. Exemple conceptuel de test de schéma Pydantic

Exemple conceptuel :

```python
def test_website_create_rejects_empty_domain():
    with pytest.raises(ValidationError):
        WebsiteCreate(name="Example", domain="")
```

Ce test vérifie la validation d'entrée.

## 85. Exemple conceptuel de test d'authentification

Exemple conceptuel :

```python
def test_admin_endpoint_requires_authentication(client):
    response = client.get("/api/v1/admin/settings")

    assert response.status_code == 401
```

Le statut exact doit suivre le contrat API existant.

## 86. Exemple conceptuel de test d'autorisation

Exemple conceptuel :

```python
def test_admin_endpoint_rejects_user_without_permission(client, user_headers):
    response = client.get("/api/v1/admin/settings", headers=user_headers)

    assert response.status_code == 403
```

Un endpoint admin doit refuser les droits insuffisants.

## 87. Exemple conceptuel de test de pagination

Exemple conceptuel :

```python
def test_list_websites_respects_page_size(client, admin_headers):
    response = client.get(
        "/api/v1/websites",
        params={"page": 1, "page_size": 2},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["page_size"] == 2
```

Tester aussi les limites.

## 88. Exemple conceptuel de test de filtrage

Exemple conceptuel :

```python
def test_list_keywords_filters_by_search(client, admin_headers):
    response = client.get(
        "/api/v1/keywords",
        params={"search": "seo"},
        headers=admin_headers,
    )

    assert response.status_code == 200
```

Le test doit vérifier le contenu lorsque les fixtures créent des données connues.

## 89. Exemple conceptuel de test d'erreur API

Exemple conceptuel :

```python
def test_get_missing_website_returns_404(client, admin_headers):
    response = client.get("/api/v1/websites/999999", headers=admin_headers)

    assert response.status_code == 404
    assert "detail" in response.json()
```

La réponse ne doit pas exposer de stack trace.

## 90. Exemple conceptuel de test Desktop avec client API mocké

Exemple conceptuel :

```python
def test_desktop_service_loads_websites(api_client):
    api_client.get.return_value = {"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0}
    service = WebsiteDesktopService(api_client)

    payload = service.list_websites(page=1, page_size=20)

    assert payload["total"] == 0
    api_client.get.assert_called_once()
```

Le test ne lance pas toute l'interface.

## 91. Exemple conceptuel de fixture Pytest

Exemple conceptuel :

```python
@pytest.fixture()
def website_payload() -> dict[str, str]:
    return {
        "name": "Example",
        "domain": "example.com",
    }
```

La fixture doit rester explicite.

## 92. Exemple conceptuel de mock `httpx`

Exemple conceptuel :

```python
def test_api_client_handles_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx.Client, "request", raise_timeout)

    with pytest.raises(ApiClientError):
        ApiClient().get("/websites")
```

À adapter selon le client existant et l'outil de mock retenu.

## 93. Exemple conceptuel de test de migration Alembic

Exemple conceptuel :

```python
def test_alembic_upgrade_head(alembic_config):
    command.upgrade(alembic_config, "head")
```

À prévoir avec une base de test dédiée.

Ne pas utiliser une base réelle de production ou de développement partagée.

## 94. Checklist avant écriture de tests

- [ ] Comportement à tester identifié.
- [ ] Couche concernée identifiée.
- [ ] Cas nominal défini.
- [ ] Cas d'erreur défini.
- [ ] Fixtures nécessaires identifiées.
- [ ] Secrets réels exclus.
- [ ] Appels externes mockés.
- [ ] Données fictives préparées.

## 95. Checklist avant lancement des tests

- [ ] Branche active correcte.
- [ ] Environnement Python prêt.
- [ ] Dépendances installées.
- [ ] Base de test isolée si nécessaire.
- [ ] Variables sensibles absentes.
- [ ] Commande ciblée choisie.
- [ ] Diff relu si les tests viennent d'être modifiés.

## 96. Checklist après échec de test

- [ ] Lire le premier échec.
- [ ] Identifier test, fixture ou code en cause.
- [ ] Reproduire avec commande ciblée.
- [ ] Vérifier si l'échec est lié au périmètre.
- [ ] Corriger le comportement ou le test.
- [ ] Relancer le test ciblé.
- [ ] Relancer la suite utile.
- [ ] Documenter les limites si non résolu.

## 97. Checklist avant commit

- [ ] `git status --short` relu.
- [ ] `git diff` relu.
- [ ] `git diff --cached` relu.
- [ ] Aucun secret.
- [ ] Aucun fichier temporaire.
- [ ] Ruff exécuté si Python modifié.
- [ ] Pytest ciblé exécuté.
- [ ] Pytest global exécuté si pertinent.
- [ ] `git diff --check` sans erreur.
- [ ] Message de commit clair.

## 98. Checklist avant Pull Request

- [ ] Tests utiles passés.
- [ ] Résultats documentés.
- [ ] Tests non exécutés signalés.
- [ ] Couverture des cas d'erreur suffisante.
- [ ] Auth et permissions testées si nécessaire.
- [ ] Migrations vérifiées si présentes.
- [ ] Pas de secrets.
- [ ] PR cible `main`.

## 99. Checklist de revue des tests

Le relecteur vérifie :

- test utile ;
- nom clair ;
- fixture compréhensible ;
- absence de secrets ;
- isolation ;
- cas d'erreur ;
- droits si endpoint sensible ;
- pas de mock excessif ;
- pas de test destructif ;
- cohérence avec l'architecture.

## 100. Critères d'acceptation des tests

Des tests sont acceptables si :

- ils protègent un comportement réel ;
- ils sont lisibles ;
- ils sont déterministes ;
- ils ne dépendent pas de secrets ;
- ils isolent leurs données ;
- ils échouent en cas de régression utile ;
- ils restent maintenables ;
- ils respectent les couches applicatives.

## 101. Points à éviter

À éviter systématiquement :

- tests dépendant de `.env` réel ;
- secrets dans les fixtures ;
- appels réseau réels ;
- base réelle destructible ;
- SQL brut dangereux ;
- tests qui ne vérifient rien ;
- mocks trop larges ;
- tests dépendant de l'ordre ;
- `Base.metadata.create_all()` pour tester Alembic ;
- `Base.metadata.drop_all()` pour tester Alembic ;
- logique métier dans les routes ;
- accès Desktop direct à PostgreSQL.

## 102. Liens avec les documents

Documents liés :

| Document | Rôle |
| --- | --- |
| `docs/development/Git_Workflow.md` | workflow Git officiel |
| `docs/development/CONTRIBUTING.md` | règles de contribution |
| `docs/development/CODING_STANDARDS.md` | standards de code |
| `docs/development/BACKEND_DEVELOPMENT_GUIDE.md` | guide backend |
| `docs/development/DESKTOP_DEVELOPMENT_GUIDE.md` | guide Desktop |
| `docs/api/AUTHENTICATION.md` | auth API |
| `docs/api/ERROR_HANDLING.md` | erreurs API |
| `docs/api/PAGINATION.md` | pagination API |
| `docs/api/FILTERING.md` | filtrage API |
| `docs/architecture/BACKEND_ARCHITECTURE.md` | architecture backend |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | architecture Desktop |
| `docs/specifications/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | exigences |

Ces documents doivent rester cohérents avec la stratégie de tests.

## Matrice de responsabilité des tests par couche

| Couche | Responsabilité | Tests prioritaires | À ne pas faire |
| --- | --- | --- | --- |
| Routes | contrat HTTP | statuts, JSON, auth | tester toute la logique métier ici |
| Services | règles métier | cas nominaux, erreurs, conflits | dépendre de FastAPI inutilement |
| Repositories | accès données | requêtes, filtres, pagination | décider des règles métier |
| Modèles | mapping table | relations, contraintes | tester Alembic via modèles |
| Schémas | validation API | champs, types, sorties | exposer des secrets |
| Desktop | client UI | services, httpx mocké, erreurs | accéder à PostgreSQL |
| Tests | protection qualité | déterminisme, lisibilité | mocks trop larges |

## Matrice de couverture par type de module

| Module | Tests API | Tests services | Tests repositories | Tests sécurité | Tests Desktop |
| --- | --- | --- | --- | --- | --- |
| Administration | Obligatoire | Obligatoire | Selon besoin | Obligatoire | Critique |
| Authentification | Obligatoire | Obligatoire | Selon besoin | Obligatoire | Critique |
| Sites web | Obligatoire | Obligatoire | Recommandé | Recommandé | Recommandé |
| SEO | Recommandé | Obligatoire | Recommandé | Selon données | Recommandé |
| GEO | Recommandé | Obligatoire | Recommandé | Clés API | Recommandé |
| Mots-clés | Recommandé | Obligatoire | Recommandé | Selon droits | Recommandé |
| Contenus | Recommandé | Obligatoire | Recommandé | Données sensibles | Recommandé |
| Concurrents | Recommandé | Obligatoire | Recommandé | Données stratégiques | Recommandé |
| Rapports | Recommandé | Obligatoire | Selon besoin | Obligatoire | Critique |
| Configuration | Obligatoire | Obligatoire | Selon besoin | Obligatoire | Critique |

## Diagramme ASCII du flux de validation

```text
Code modifié
    |
    v
Ruff
    |
    v
Pytest ciblé
    |
    v
Pytest global si pertinent
    |
    v
git diff --check
    |
    v
Pull Request
    |
    v
Revue
```

## Diagramme ASCII des couches testées

```text
Tests API
   |
   v
Routes FastAPI
   |
   v
Tests services ---> Services métier
   |
   v
Tests repositories ---> Repositories SQLAlchemy
   |
   v
Tests modèles/migrations ---> Models SQLAlchemy + Alembic
   |
   v
Base de test isolée

Tests Desktop
   |
   v
Services Desktop / ApiClient mocké
   |
   v
Contrats API
```

## Commandes PowerShell de référence

Avant toute modification :

```powershell
git branch --show-current
git status --short
```

Validation documentaire :

```powershell
git diff --check
```

Validation Python :

```powershell
ruff check .
pytest
```

Validation ciblée :

```powershell
pytest tests/api
pytest tests/services
ruff check backend tests
```

## Section de prudence

Ne jamais lancer de tests destructifs sur une base réelle.

Ne jamais utiliser de secrets réels :

```text
mot de passe réel
token réel
clé API réelle
fichier .env réel
```

Ne pas utiliser pour valider des migrations Alembic :

```python
Base.metadata.create_all(bind=engine)
Base.metadata.drop_all(bind=engine)
```

Ne pas utiliser sans validation explicite :

```powershell
git reset --hard
git clean -fd
git push --force
```

En cas d'incertitude, arrêter et demander confirmation.
