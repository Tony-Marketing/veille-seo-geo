# Contribuer au projet Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit les règles de contribution au projet **Veille SEO-GEO Groupe A.P&Partner**.

Il complète le workflow Git décrit dans `docs/development/Git_Workflow.md` et précise comment proposer des changements propres, relisibles et compatibles avec l'architecture existante.

Il sert de référence pour :

- les contributions backend FastAPI ;
- les contributions Desktop PySide6 ;
- les contributions documentaires ;
- les futures contributions React ;
- les corrections de bugs ;
- les sprints fonctionnels ;
- les interventions assistées par Codex.

Une contribution acceptable doit être ciblée, testable, documentée lorsque nécessaire et conforme aux règles d'architecture du projet.

## 2. Périmètre des contributions

Les contributions peuvent concerner :

| Domaine | Exemples | Exigence principale |
| --- | --- | --- |
| Documentation | guides, sprints, architecture, API | clarté et cohérence avec l'existant |
| Backend | routes, services, repositories, models, schemas | respect strict des couches |
| Desktop | pages, widgets, client API, styles | communication uniquement via API REST |
| Tests | tests unitaires, tests API, fixtures | couverture des comportements importants |
| Corrections | bugs, incohérences, erreurs de validation | changement minimal et vérifiable |
| Sécurité | auth, permissions, secrets, validation | aucune exposition de données sensibles |
| Performance | requêtes, pagination, cache, traitements | mesure ou justification du gain |
| Préparation React | types, conventions, documentation future | pas d'architecture prématurée |

Une contribution ne doit pas mélanger plusieurs sujets sans raison claire.

## 3. Types de contributions acceptées

### Documentation

Les contributions documentaires doivent améliorer la compréhension du projet sans contredire les documents existants.

Exemples :

- guide de workflow ;
- guide de développement ;
- documentation API ;
- notes de sprint ;
- règles de sécurité ;
- documentation de configuration.

### Backend

Les contributions backend doivent respecter :

```text
Routes -> Services -> Repositories -> Models
```

La logique métier doit rester dans les services.

### Desktop

Les contributions Desktop doivent utiliser PySide6 et communiquer avec FastAPI via HTTP REST.

Le Desktop ne doit jamais accéder directement à PostgreSQL.

### Tests

Les contributions de tests doivent utiliser Pytest et rester proches du comportement vérifié.

### Corrections

Une correction doit être limitée au bug ciblé. Elle ne doit pas introduire un refactor global.

### Sécurité

Une contribution sécurité doit préciser le risque traité et éviter toute exposition de secret.

### Performance

Une contribution performance doit expliquer le problème, la solution et le comportement attendu.

### Préparation React

Les futures contributions React devront respecter React, TypeScript, Vite et Tailwind CSS, sans anticiper des dossiers ou abstractions non validés.

## 4. Dépôt officiel

Le dépôt officiel est :

```text
Tony-Marketing/veille-seo-geo
```

Vérification du dépôt distant :

```powershell
git remote -v
```

Sortie attendue :

```text
origin  https://github.com/Tony-Marketing/veille-seo-geo.git (fetch)
origin  https://github.com/Tony-Marketing/veille-seo-geo.git (push)
```

## 5. Dossier local officiel

Le dossier local officiel est :

```text
C:\Users\assistant.marketing\Desktop\Veille SEO-GEO Groupe APPartner
```

Avant toute contribution :

```powershell
Get-Location
```

Sortie attendue :

```text
C:\Users\assistant.marketing\Desktop\Veille SEO-GEO Groupe APPartner
```

## 6. Branche stable

La branche stable est :

```text
main
```

Règles :

- `main` contient uniquement des changements validés ;
- aucune contribution ne doit être développée directement sur `main` ;
- chaque contribution doit passer par une branche dédiée ;
- chaque Pull Request doit cibler `main`.

## 7. Référence au workflow Git

Le workflow Git de référence est :

```text
docs/development/Git_Workflow.md
```

Ce document doit être consulté pour :

- créer une branche ;
- vérifier l'état Git ;
- indexer les fichiers ;
- préparer un commit ;
- pousser une branche ;
- ouvrir une Pull Request ;
- nettoyer après merge.

Le présent guide ne remplace pas le workflow Git. Il décrit les critères de qualité d'une contribution.

## 8. Règles avant de commencer une contribution

Avant toute modification :

```powershell
git branch --show-current
git status --short
```

Vérifier ensuite :

- la branche active ;
- l'absence de modifications non comprises ;
- les fichiers déjà indexés ;
- le périmètre exact de la demande ;
- les fichiers à créer ou modifier ;
- les tests à exécuter ;
- les risques de sécurité ou de migration.

Si le dépôt est incohérent ou incomplet, arrêter la contribution et produire un rapport d'anomalie.

## 9. Vérification de la branche active

Commande :

```powershell
git branch --show-current
```

Sortie correcte pour une contribution documentaire en cours :

```text
docs-development-guides
```

Sortie interdite pour développer :

```text
main
```

Si la branche active est `main`, ne pas modifier les fichiers. Créer d'abord une branche dédiée depuis un `main` à jour.

## 10. Préparation d'une branche dédiée

Depuis `main` :

```powershell
git switch main
git pull --ff-only origin main
git switch -c docs-development-guides
```

Pour une correction :

```powershell
git switch main
git pull --ff-only origin main
git switch -c fix-auth-permissions
```

Pour un sprint backend :

```powershell
git switch main
git pull --ff-only origin main
git switch -c sprint-09-backend-geo
```

Ne pas utiliser une branche existante pour un sujet différent.

## 11. Nommage recommandé des branches de contribution

| Type | Format | Exemple |
| --- | --- | --- |
| Documentation | `docs-sujet` | `docs-development-guides` |
| Fonctionnalité | `feature-sujet` | `feature-dashboard-kpis` |
| Correction | `fix-sujet` | `fix-websites-pagination` |
| Sprint | `sprint-numero-sujet` | `sprint-09-backend-geo` |
| Sécurité | `security-sujet` | `security-api-key-scopes` |
| Performance | `perf-sujet` | `perf-websites-list-query` |
| Hotfix | `hotfix-sujet` | `hotfix-healthcheck` |

Les noms doivent être courts, lisibles, sans accents et sans espaces.

## 12. Contribution documentaire

Une contribution documentaire doit :

- être en français ;
- utiliser un ton clair et opérationnel ;
- respecter la structure existante de `docs/` ;
- éviter les doublons inutiles ;
- référencer les documents liés ;
- ne pas renommer de document existant sans validation ;
- ne pas déplacer de document existant sans validation.

Vérifications recommandées :

```powershell
git status --short
git diff -- docs
git diff --check
```

Une documentation utile doit expliquer quoi faire, pourquoi le faire et comment vérifier le résultat.

## 13. Contribution backend

Une contribution backend doit respecter les technologies du projet :

- Python 3.13 ;
- FastAPI ;
- SQLAlchemy 2.x ;
- Alembic ;
- PostgreSQL ;
- Pydantic v2 ;
- Pytest ;
- Ruff.

Règles :

- pas de logique métier dans les routes ;
- pas d'accès direct à la base dans les routes ;
- pas de SQL brut si SQLAlchemy couvre le besoin ;
- schemas Pydantic pour les entrées et sorties API ;
- services pour les règles métier ;
- repositories pour l'accès aux données ;
- modèles SQLAlchemy pour les tables ;
- tests pour les comportements importants.

## 14. Contribution Desktop PySide6

Une contribution Desktop doit respecter l'organisation existante :

| Dossier | Rôle |
| --- | --- |
| `desktop/ui/` | pages principales |
| `desktop/widgets/` | composants réutilisables |
| `desktop/core/` | configuration, constantes, client API |
| `desktop/styles/` | styles QSS |

Règles :

- utiliser PySide6 ;
- garder les appels réseau dans le client API prévu ;
- utiliser `httpx` pour les appels HTTP ;
- ne jamais accéder directement à PostgreSQL ;
- ne pas dupliquer la logique métier backend ;
- préserver l'ergonomie et le style existants.

Commande utile :

```powershell
python desktop/main.py
```

## 15. Contribution tests

Les tests doivent être placés dans `tests/`.

Exemples :

| Type de test | Emplacement recommandé |
| --- | --- |
| Tests services | `tests/services/` |
| Tests API | `tests/api/` |
| Fixtures partagées | `tests/conftest.py` |

Commandes :

```powershell
pytest
pytest tests/services/test_websites_services.py
pytest tests/api/test_websites_routes.py
```

Un test doit vérifier un comportement observable, pas seulement une implémentation interne fragile.

## 16. Contribution migrations Alembic

Toute modification de structure de base PostgreSQL doit passer par Alembic.

Règles :

- migration explicite ;
- nom de fichier compréhensible ;
- cohérence avec les modèles SQLAlchemy ;
- cohérence avec les schemas Pydantic ;
- pas de `Base.metadata.create_all()` dans les migrations ;
- pas de `Base.metadata.drop_all()` dans les migrations ;
- pas de suppression destructrice sans validation explicite ;
- attention aux données existantes.

Commandes utiles :

```powershell
alembic current
alembic history
alembic upgrade head
```

Avant Pull Request :

```powershell
git diff -- backend/alembic/versions
git diff -- backend/app/models
```

## 17. Contribution sécurité

Une contribution sécurité doit traiter explicitement :

- le risque ;
- le périmètre ;
- le comportement attendu ;
- les tests ou validations ;
- les impacts sur l'authentification et les permissions.

Règles :

- protéger les endpoints sensibles ;
- appliquer les droits adaptés ;
- ne jamais exposer de secret ;
- ne jamais logger de token ou mot de passe ;
- valider les entrées ;
- limiter les informations retournées en erreur ;
- documenter les changements d'accès.

## 18. Contribution performance

Une contribution performance doit être justifiée.

Exemples de sujets acceptés :

- réduction du nombre de requêtes SQL ;
- pagination d'une grande liste ;
- optimisation d'un repository ;
- cache pour données peu volatiles ;
- traitement asynchrone pertinent ;
- réduction d'appels HTTP Desktop inutiles.

Avant et après la modification, préciser ce qui change.

Exemple de vérification :

```powershell
pytest tests/services/test_websites_services.py
```

## 19. Contribution configuration

Les contributions de configuration doivent être prudentes.

Règles :

- ne pas commiter `.env` ;
- ne pas commiter de secret ;
- documenter les variables attendues ;
- fournir des valeurs d'exemple non sensibles si nécessaire ;
- rendre les imports/exports de configuration non destructifs ;
- rendre les imports/exports idempotents lorsque possible.

Un import idempotent peut être relancé sans créer de doublons ni supprimer des données utiles.

## 20. Contribution SEO/GEO

Les contributions SEO/GEO doivent rester modulaires.

Exemples de domaines :

- suivi des mots-clés ;
- analyse des contenus ;
- audit d'URL ;
- visibilité dans les réponses IA ;
- citations de marques ;
- comparaison de modèles IA ;
- historique des résultats ;
- suivi concurrentiel.

Règles :

- isoler les intégrations externes dans `backend/connectors/` si elles sont créées ;
- éviter les appels HTTP directs dans les routes ;
- stocker l'historique utile ;
- prévoir l'extensibilité des modèles IA ;
- tester les règles métier critiques.

## 21. Contribution future React

Le frontend React est prévu plus tard.

Technologies attendues :

- React ;
- TypeScript ;
- Vite ;
- Tailwind CSS.

Règles en attendant le lancement React :

- ne pas créer une architecture frontend complète sans demande ;
- ne pas ajouter de dépendance frontend sans justification ;
- documenter les besoins futurs lorsque nécessaire ;
- préserver les contrats API pour faciliter l'intégration future ;
- éviter les changements backend qui couplent l'API au Desktop uniquement.

## 22. Règles d'architecture backend `Routes -> Services -> Repositories -> Models`

Architecture obligatoire :

```text
Routes FastAPI
   |
   v
Services métier
   |
   v
Repositories SQLAlchemy
   |
   v
Models SQLAlchemy
```

Responsabilités :

| Couche | Responsabilité | Interdit |
| --- | --- | --- |
| Routes | HTTP, dépendances, schemas, codes retour | logique métier lourde |
| Services | règles métier, orchestration | SQL direct |
| Repositories | requêtes SQLAlchemy | décisions métier |
| Models | représentation des tables | logique applicative |
| Schemas | validation API | accès base |

Une contribution qui casse cette séparation doit être retravaillée.

## 23. Règles pour les routes FastAPI

Les routes FastAPI doivent :

- recevoir et valider les entrées via Pydantic ;
- appeler les services ;
- gérer les dépendances FastAPI ;
- retourner les schemas de sortie attendus ;
- appliquer l'authentification et les permissions ;
- rester courtes.

Les routes ne doivent pas :

- contenir de logique métier ;
- interroger directement SQLAlchemy ;
- construire des requêtes complexes ;
- manipuler des secrets ;
- contourner les services existants.

Exemple de principe :

```python
@router.get("/websites")
def list_websites(service: WebsiteService = Depends(get_website_service)):
    return service.list_websites()
```

## 24. Règles pour les services

Les services contiennent la logique métier.

Ils doivent :

- orchestrer les repositories ;
- appliquer les règles métier ;
- vérifier les droits si nécessaire ;
- gérer les cas d'erreur métier ;
- rester testables ;
- éviter les dépendances directes à l'interface Desktop.

Ils ne doivent pas :

- contenir de SQL brut si un repository peut le faire ;
- mélanger plusieurs domaines sans raison ;
- dépendre de détails d'affichage ;
- modifier directement la configuration locale.

## 25. Règles pour les repositories

Les repositories contiennent uniquement l'accès aux données.

Ils doivent :

- utiliser SQLAlchemy 2.x ;
- exposer des méthodes explicites ;
- limiter les requêtes inutiles ;
- gérer la pagination lorsque nécessaire ;
- rester indépendants des routes FastAPI ;
- ne pas contenir de logique métier.

Exemple de responsabilité correcte :

```python
def get_by_id(self, website_id: int) -> Website | None:
    ...
```

Exemple à éviter :

```python
def get_visible_websites_for_dashboard_with_business_rules(...):
    ...
```

## 26. Règles pour les modèles SQLAlchemy

Les modèles SQLAlchemy représentent les tables et relations.

Ils doivent :

- rester cohérents avec les migrations Alembic ;
- utiliser des noms explicites ;
- déclarer les relations nécessaires ;
- éviter la logique métier ;
- ne pas stocker de secret en clair.

Toute modification d'un modèle qui change la structure de base doit être accompagnée d'une migration Alembic.

## 27. Règles pour les schémas Pydantic v2

Les schemas Pydantic v2 gèrent les entrées et sorties API.

Ils doivent :

- valider les données entrantes ;
- limiter les champs exposés ;
- séparer création, mise à jour et lecture si nécessaire ;
- documenter les champs importants ;
- éviter d'exposer des champs internes sensibles.

Exemples de familles de schemas :

```text
WebsiteCreate
WebsiteUpdate
WebsiteRead
WebsiteListItem
```

## 28. Règles pour les migrations Alembic

Une migration Alembic doit être relisible.

Elle doit préciser :

- les tables créées ou modifiées ;
- les colonnes ajoutées ou supprimées ;
- les index ;
- les contraintes ;
- les valeurs par défaut ;
- les impacts sur les données existantes.

Interdits :

```python
Base.metadata.create_all(...)
Base.metadata.drop_all(...)
```

Une migration destructive doit être explicitement validée avant contribution.

## 29. Règles pour le Desktop PySide6

Le Desktop est une interface cliente.

Il doit :

- afficher les données utiles ;
- appeler l'API FastAPI ;
- gérer les erreurs HTTP proprement ;
- éviter les blocages d'interface ;
- respecter les widgets et styles existants ;
- rester découplé de PostgreSQL.

Le Desktop ne doit pas :

- contenir la logique métier principale ;
- ouvrir une connexion base directe ;
- dupliquer les règles de permission backend ;
- stocker des secrets en clair.

## 30. Règles pour l'accès API depuis Desktop

Les appels API Desktop doivent passer par le client prévu dans `desktop/core/`.

Règles :

- utiliser HTTP REST ;
- centraliser l'URL de base ;
- gérer les erreurs réseau ;
- gérer les erreurs d'authentification ;
- éviter les appels redondants ;
- ne pas exposer de token dans les logs.

Exemple de validation manuelle :

```powershell
python desktop/main.py
```

## 31. Règles pour les tests Pytest

Les tests Pytest doivent :

- être déterministes ;
- être lisibles ;
- isoler les cas testés ;
- couvrir les erreurs importantes ;
- utiliser les fixtures existantes ;
- éviter les dépendances réseau réelles non contrôlées.

Commandes :

```powershell
pytest
pytest tests/services
pytest tests/api
```

Si un test ne peut pas être exécuté, le compte rendu doit l'indiquer clairement.

## 32. Règles pour Ruff

Ruff est l'outil de linting Python du projet.

Commande globale :

```powershell
ruff check .
```

Commande ciblée :

```powershell
ruff check backend desktop tests
```

Règles :

- ne pas ignorer une erreur Ruff sans justification ;
- ne pas reformater tout le dépôt pour une correction locale ;
- limiter les changements de style au périmètre ;
- documenter les limites si Ruff ne peut pas être exécuté.

## 33. Règles de sécurité

Règles obligatoires :

- ne jamais commiter de secrets ;
- ne jamais commiter `.env` ;
- ne jamais logger de mot de passe ;
- ne jamais exposer de token dans une réponse API ;
- protéger les endpoints sensibles ;
- vérifier les permissions ;
- valider les entrées utilisateur ;
- limiter les messages d'erreur sensibles ;
- éviter les imports destructifs de configuration.

Avant commit :

```powershell
git diff
git diff --cached
```

Si un secret est détecté dans un commit déjà créé, il doit être révoqué. Une simple suppression dans un commit suivant ne suffit pas.

## 34. Fichiers à ne jamais commiter

| Fichier ou dossier | Raison |
| --- | --- |
| `.venv/` | environnement local |
| `venv/` | environnement local |
| `.codex_deps/` | dépendances locales d'outillage |
| `__pycache__/` | cache Python |
| `*.pyc` | bytecode Python |
| `.pytest_cache/` | cache Pytest |
| `.ruff_cache/` | cache Ruff |
| fichiers temporaires | bruit local |
| fichiers de secrets | risque sécurité |
| `.env` | variables sensibles |
| clés API | secret |
| tokens | secret |
| mots de passe | secret |

Commande de vérification :

```powershell
git status --short
```

Ne pas ajouter un fichier inconnu sans comprendre son origine.

## 35. Règles de qualité attendues

Une contribution de qualité doit être :

- ciblée ;
- lisible ;
- testable ;
- cohérente avec l'architecture ;
- documentée si elle ajoute un comportement important ;
- compatible avec les conventions existantes ;
- limitée au périmètre annoncé.

Elle ne doit pas introduire de dépendance sans justification explicite.

## 36. Règles de lisibilité du code

Code attendu :

- fonctions courtes ;
- noms explicites ;
- type hints en Python ;
- docstrings utiles pour les fonctions complexes ;
- absence de duplication inutile ;
- séparation claire des responsabilités ;
- erreurs gérées proprement.

À éviter :

- fichiers de plusieurs milliers de lignes ;
- fonctions qui mélangent API, métier et base ;
- noms vagues ;
- commentaires qui répètent le code ;
- abstractions prématurées.

## 37. Règles de lisibilité documentaire

Documentation attendue :

- titres clairs ;
- exemples concrets ;
- commandes prêtes à copier ;
- tableaux lorsque cela clarifie ;
- avertissements sur les commandes risquées ;
- liens vers les documents liés ;
- ton technique et opérationnel.

Une documentation ne doit pas promettre une fonctionnalité inexistante sans préciser qu'elle est future.

## 38. Taille recommandée des Pull Requests

Une Pull Request doit rester relisible.

| Taille | Appréciation | Action |
| --- | --- | --- |
| Petite | 1 à 5 fichiers ciblés | idéale |
| Moyenne | plusieurs fichiers cohérents | acceptable avec description claire |
| Grande | nombreux modules | à découper si possible |
| Très grande | backend, desktop, docs, migrations mélangés | à refuser ou retravailler |

Une PR de sprint peut être plus large, mais son périmètre doit être documenté.

## 39. Contenu attendu d'une Pull Request

Une Pull Request doit indiquer :

- objectif ;
- périmètre ;
- fichiers principaux modifiés ;
- comportement ajouté ou corrigé ;
- tests exécutés ;
- résultat des tests ;
- risques ;
- migrations si présentes ;
- captures si interface Desktop ou future interface React.

## 40. Description recommandée d'une Pull Request

Modèle recommandé :

```markdown
## Objectif

## Changements

## Tests

## Sécurité

## Points de vigilance
```

Exemple :

```markdown
## Objectif
Ajouter le guide de contribution du projet.

## Changements
- Création de docs/development/CONTRIBUTING.md
- Ajout des règles backend, Desktop, tests et Codex

## Tests
- git diff --check

## Points de vigilance
- Documentation uniquement
```

## 41. Checklist avant Pull Request

- [ ] La branche active n'est pas `main`.
- [ ] La branche part d'un `main` à jour.
- [ ] Le périmètre est clair.
- [ ] Les fichiers modifiés sont attendus.
- [ ] Aucun secret n'est présent.
- [ ] Les tests utiles ont été exécutés.
- [ ] Ruff a été exécuté si Python est modifié.
- [ ] `git diff --check` ne signale rien.
- [ ] Les migrations sont cohérentes si présentes.
- [ ] La description de PR est complète.

## 42. Checklist avant revue

Avant de demander une revue :

- [ ] Relire le diff complet.
- [ ] Vérifier les fichiers indexés.
- [ ] Vérifier les fichiers non suivis.
- [ ] Relire les tests.
- [ ] Vérifier les messages d'erreur.
- [ ] Confirmer la cible `main`.
- [ ] Signaler les limites connues.

Commandes :

```powershell
git status --short
git diff
git diff --cached
git diff --check
```

## 43. Checklist de revue

Le relecteur doit vérifier :

- respect du périmètre ;
- respect de l'architecture ;
- absence de secrets ;
- lisibilité du code ;
- qualité des tests ;
- cohérence documentaire ;
- absence de refactor non demandé ;
- sécurité des endpoints sensibles ;
- cohérence des migrations ;
- compatibilité Desktop et future React si concernée.

Une revue doit demander des changements précis, pas seulement indiquer que le code ne convient pas.

## 44. Critères d'acceptation d'une contribution

Une contribution peut être acceptée si :

- elle résout le besoin annoncé ;
- elle respecte l'architecture ;
- elle ne contient pas de secret ;
- elle ne modifie pas des fichiers hors périmètre ;
- elle passe les validations pertinentes ;
- elle est relisible ;
- elle ne dégrade pas les modules existants ;
- elle est documentée lorsque nécessaire.

## 45. Cas où une contribution doit être refusée ou retravaillée

Une contribution doit être refusée ou retravaillée si elle :

- développe directement sur `main` ;
- mélange plusieurs sujets sans justification ;
- contient un secret ;
- modifie l'architecture globalement sans validation ;
- place de la logique métier dans les routes ;
- fait accéder le Desktop directement à PostgreSQL ;
- utilise `Base.metadata.create_all()` dans une migration ;
- utilise `Base.metadata.drop_all()` dans une migration ;
- supprime ou renomme des fichiers sans validation ;
- ignore les tests pertinents ;
- introduit une dépendance non justifiée.

## 46. Gestion des retours de revue

Lorsqu'une revue demande des changements :

1. lire tous les commentaires ;
2. regrouper les demandes par thème ;
3. corriger les points actionnables ;
4. répondre aux questions ouvertes ;
5. relancer les tests utiles ;
6. pousser les corrections sur la même branche ;
7. demander une nouvelle revue.

Ne pas réécrire largement la PR si les demandes sont ciblées.

## 47. Gestion des conflits

Diagnostic :

```powershell
git status --short
```

Exemple :

```text
UU backend/app/services/websites.py
```

Résolution :

- ouvrir les fichiers en conflit ;
- chercher `<<<<<<<`, `=======`, `>>>>>>>` ;
- conserver la bonne logique ;
- relire les couches impactées ;
- relancer les tests utiles ;
- indexer uniquement les fichiers résolus.

Ne jamais résoudre un conflit en supprimant du code sans comprendre son rôle.

## 48. Gestion des fichiers non suivis

Un fichier non suivi apparaît ainsi :

```text
?? docs/development/CONTRIBUTING.md
```

Actions recommandées :

| Cas | Action |
| --- | --- |
| Fichier prévu | relire puis indexer au moment du commit |
| Cache | ne pas indexer |
| Secret | ne pas indexer et sécuriser |
| Fichier inconnu | demander confirmation |

Ne jamais utiliser `git add -A` sans inspecter les fichiers non suivis.

## 49. Gestion des fichiers déjà indexés

Afficher les fichiers indexés :

```powershell
git diff --cached --name-only
```

Afficher le diff indexé :

```powershell
git diff --cached
```

Règle importante :

Si des fichiers sont déjà indexés volontairement par l'utilisateur, ne pas les désindexer sans demande explicite.

Codex doit respecter cette règle strictement.

## 50. Contribution avec Codex

Codex peut assister une contribution, mais la contribution reste sous contrôle humain.

Workflow recommandé :

1. indiquer la branche obligatoire ;
2. indiquer les fichiers autorisés ;
3. préciser les fichiers interdits ;
4. demander la vérification de branche ;
5. demander la vérification `git status --short` ;
6. laisser Codex créer ou modifier uniquement le périmètre validé ;
7. demander les vérifications ;
8. relire le résultat ;
9. décider humainement de l'indexation, du commit et du push.

## 51. Ce que Codex peut faire

Codex peut :

- analyser l'existant ;
- lire les documents de référence ;
- créer un fichier explicitement demandé ;
- modifier un fichier explicitement autorisé ;
- proposer une correction ciblée ;
- exécuter Ruff, Pytest ou les vérifications Git ;
- produire un compte rendu ;
- signaler une anomalie au lieu d'inventer.

## 52. Ce que Codex ne doit pas faire sans validation explicite

Codex ne doit pas :

- créer de commit ;
- faire de push ;
- supprimer un fichier ;
- renommer un fichier ;
- déplacer un fichier ;
- refactorer globalement ;
- ajouter une dépendance ;
- modifier des fichiers hors périmètre ;
- désindexer des fichiers déjà indexés ;
- travailler sur `main` ;
- utiliser une commande destructive.

## 53. Prompt Codex recommandé pour une contribution ciblée

Exemple de prompt :

```text
Tu travailles sur la branche docs-development-guides.
Avant toute modification, exécute git branch --show-current et git status --short.
Crée uniquement docs/development/CONTRIBUTING.md.
Ne modifie aucun autre fichier.
Ne modifie pas docs/development/Git_Workflow.md.
N'exécute pas git add, git commit ou git push.
Après création, exécute git status --short, git diff --stat et git diff --check.
Fournis un compte rendu final.
```

Ce type de prompt réduit les risques de changements hors périmètre.

## 54. Exemple de contribution documentaire

Objectif :

```text
Créer un guide de contribution.
```

Commandes :

```powershell
git branch --show-current
git status --short
Test-Path docs/development/CONTRIBUTING.md
```

Après rédaction :

```powershell
git status --short
git diff --check
```

Commit humain possible :

```powershell
git add docs/development/CONTRIBUTING.md
git commit -m "docs: ajout du guide de contribution"
```

Codex ne doit pas exécuter ces deux dernières commandes sans demande explicite.

## 55. Exemple de contribution backend

Objectif :

```text
Ajouter une règle métier de validation pour les sites web.
```

Fichiers possibles :

```text
backend/app/services/websites.py
backend/app/schemas/websites.py
tests/services/test_websites_services.py
```

Commandes :

```powershell
ruff check backend tests
pytest tests/services/test_websites_services.py
git diff --check
```

Critère :

La route appelle le service. La règle métier reste dans le service.

## 56. Exemple de contribution Desktop

Objectif :

```text
Afficher un message d'erreur clair lorsqu'un appel API échoue.
```

Fichiers possibles :

```text
desktop/core/api_client.py
desktop/ui/websites_page.py
```

Commandes :

```powershell
python desktop/main.py
ruff check desktop
git diff --check
```

Critère :

Le Desktop appelle FastAPI via HTTP REST et ne contourne pas l'API.

## 57. Exemple de correction simple

Objectif :

```text
Corriger une erreur de pagination dans la liste des sites.
```

Workflow :

```powershell
git switch main
git pull --ff-only origin main
git switch -c fix-websites-pagination
pytest tests/api/test_websites_routes.py
ruff check backend tests
git diff --check
```

Commit possible :

```powershell
git add backend/app/api/v1/routes/websites.py
git add tests/api/test_websites_routes.py
git commit -m "fix: correction de la pagination websites"
```

## 58. Exemple de modification à refuser

Exemple :

```text
Une PR ajoute une page Desktop, modifie les modèles SQLAlchemy, crée une migration,
change le style global, réécrit un service et met à jour la documentation sans lien direct.
```

Raison du refus :

- périmètre trop large ;
- mélange Desktop, backend, migration et documentation ;
- revue difficile ;
- risque de régression élevé.

Action recommandée :

- découper en plusieurs branches ;
- isoler la migration ;
- isoler la fonctionnalité Desktop ;
- documenter séparément.

## 59. Commandes PowerShell utiles

| Besoin | Commande |
| --- | --- |
| Branche active | `git branch --show-current` |
| État court | `git status --short` |
| Diff non indexé | `git diff` |
| Diff indexé | `git diff --cached` |
| Vérifier les espaces | `git diff --check` |
| Derniers commits | `git log --oneline -5` |
| Fichiers indexés | `git diff --cached --name-only` |
| Dossier courant | `Get-Location` |
| Existence fichier | `Test-Path docs/development/CONTRIBUTING.md` |
| Lint Python | `ruff check .` |
| Tests Python | `pytest` |

Commandes de prudence avant toute action risquée :

```powershell
git status --short
git diff
git diff --cached
```

## 60. Tests et validations recommandés avant demande de merge

Selon le type de contribution :

| Type | Validations minimales |
| --- | --- |
| Documentation | `git diff --check` |
| Backend | `ruff check .`, `pytest` |
| Desktop | `ruff check desktop`, lancement manuel si interface |
| Tests | `pytest` ciblé puis global si pertinent |
| Migration | `alembic upgrade head`, tests liés |
| Sécurité | tests auth/permissions, revue manuelle du diff |
| Performance | tests de non-régression et justification |

Si une validation n'est pas exécutée, l'indiquer dans la Pull Request.

## 61. Critères de merge

Une Pull Request peut être mergée si :

- elle cible `main` ;
- elle a été relue ;
- elle respecte le périmètre ;
- elle ne contient pas de secret ;
- elle ne contient pas de fichiers temporaires ;
- les tests nécessaires sont verts ;
- les migrations sont validées ;
- les conflits sont résolus ;
- le mainteneur valide l'intégration.

Le merge ne doit pas être utilisé pour intégrer une contribution incomplète sans accord explicite.

## 62. Nettoyage après merge

Après merge :

```powershell
git switch main
git pull --ff-only origin main
git status --short
```

Si la branche est mergée et n'est plus utile :

```powershell
git branch -d docs-development-guides
git push origin --delete docs-development-guides
```

Avant suppression, vérifier que la branche est bien mergée.

Commande utile :

```powershell
git branch --merged main
```

## 63. Points à éviter

À éviter :

- développer directement sur `main` ;
- mélanger plusieurs sujets ;
- ignorer `docs/development/Git_Workflow.md` ;
- mettre de la logique métier dans les routes ;
- connecter le Desktop directement à PostgreSQL ;
- utiliser `Base.metadata.create_all()` dans les migrations ;
- utiliser `Base.metadata.drop_all()` dans les migrations ;
- commiter `.env` ;
- commiter des secrets ;
- ajouter une dépendance sans justification ;
- refactorer globalement sans validation ;
- utiliser `git add -A` sans inspection ;
- utiliser `git reset --hard` sans validation explicite ;
- utiliser `git clean -fd` sans validation explicite ;
- utiliser `git push --force` sans validation explicite.

## 64. Liens avec les futurs documents

Documents de référence :

| Document | Statut | Rôle |
| --- | --- | --- |
| `docs/development/Git_Workflow.md` | existant | workflow Git officiel |
| `docs/development/CODING_STANDARDS.md` | futur | conventions de code et style |
| `docs/development/BACKEND_DEVELOPMENT_GUIDE.md` | futur | règles backend détaillées |
| `docs/development/DESKTOP_DEVELOPMENT_GUIDE.md` | futur | règles Desktop détaillées |
| `docs/development/TESTING.md` | futur | stratégie de tests |

Ce guide sera complété par ces documents au fur et à mesure de leur création.

## Matrice de responsabilités

| Responsabilité | Contributeur | Relecteur | Mainteneur | Codex |
| --- | --- | --- | --- | --- |
| Définir le périmètre | Responsable | Vérifie | Peut arbitrer | Suit le périmètre donné |
| Vérifier la branche | Responsable | Peut vérifier | Peut imposer | Obligatoire avant action |
| Modifier les fichiers | Responsable | Non | Peut intervenir | Seulement fichiers autorisés |
| Respecter l'architecture | Responsable | Responsable de revue | Responsable final | Doit appliquer |
| Lancer les tests | Responsable | Peut demander | Peut bloquer | Peut exécuter si demandé ou pertinent |
| Vérifier les secrets | Responsable | Responsable | Responsable final | Doit signaler |
| Créer un commit | Responsable | Non | Peut le faire | Non sans demande explicite |
| Pousser la branche | Responsable | Non | Peut le faire | Non sans demande explicite |
| Ouvrir la PR | Responsable | Non | Peut accompagner | Non sans demande explicite |
| Merger | Non | Recommande | Responsable | Non |

## Matrice de contrôle par type de contribution

| Type | Fichiers typiques | Tests attendus | Revue prioritaire | Risque principal |
| --- | --- | --- | --- | --- |
| Documentation | `docs/` | `git diff --check` | clarté et cohérence | contradiction documentaire |
| Backend route | `backend/app/api/` | tests API | absence de logique métier | contournement services |
| Backend service | `backend/app/services/` | tests services | règles métier | régression fonctionnelle |
| Repository | `backend/app/repositories/` | tests services/API | requêtes SQLAlchemy | performance ou données |
| Model | `backend/app/models/` | migration + tests | cohérence DB | migration manquante |
| Schema | `backend/app/schemas/` | tests API | validation et exposition | fuite de champs |
| Desktop | `desktop/` | lancement manuel + Ruff | UX et appels API | accès direct interdit |
| Sécurité | backend, config | tests auth | droits et secrets | exposition de données |
| Performance | services, repositories | tests non-régression | mesure et requêtes | optimisation fragile |
| React futur | `frontend/` | à définir | conventions React | architecture prématurée |

## Diagramme ASCII du cycle d'une contribution

```text
main à jour
   |
   | git switch -c type-sujet
   v
branche dédiée
   |
   | modifications ciblées
   v
vérifications locales
   |
   | tests + lint + diff
   v
commit humain
   |
   | push de la branche
   v
Pull Request vers main
   |
   | revue + corrections
   v
validation mainteneur
   |
   | merge
   v
main mis à jour
   |
   | suppression branche si inutile
   v
nettoyage
```

## Cas d'erreur fréquents et meilleure action

| Erreur | Symptôme | Meilleure action |
| --- | --- | --- |
| Branche incorrecte | `main` affiché par Git | arrêter et créer une branche dédiée |
| Fichiers déjà indexés | `A  fichier` avant intervention | ne pas désindexer sans demande |
| Fichier non suivi inconnu | `?? fichier` | inspecter avant ajout |
| Secret dans le diff | clé ou token visible | retirer immédiatement, révoquer si exposé |
| Tests en échec | Pytest rouge | corriger ou documenter le blocage |
| Ruff en erreur | sortie Ruff non vide | corriger dans le périmètre |
| Conflit Git | `UU fichier` | résoudre manuellement et tester |
| PR trop large | nombreux sujets mélangés | découper la contribution |
| Migration risquée | suppression de colonne/table | demander validation explicite |
| Warning CRLF | `LF will be replaced by CRLF` | non bloquant sauf sujet fins de ligne |

## Section de prudence pour commandes destructrices

Les commandes suivantes peuvent supprimer du travail local ou réécrire l'historique.

Elles ne doivent pas être utilisées sans validation explicite :

```powershell
git reset --hard
git clean -fd
git push --force
git branch -D nom-de-branche
```

Avant toute commande risquée :

```powershell
git status --short
git diff
git diff --cached
git log --oneline -10
```

Si un doute existe, arrêter et demander confirmation.
