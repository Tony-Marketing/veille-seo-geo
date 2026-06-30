# Git Workflow - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit le workflow Git officiel du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence opérationnelle pour :

- le travail quotidien sur le dépôt ;
- la création et la gestion des branches ;
- les sprints backend FastAPI ;
- les lots documentaires ;
- les développements Desktop PySide6 ;
- les futures évolutions React ;
- les contributions humaines ;
- les interventions Codex.

L'objectif est de protéger la branche stable, de rendre les modifications auditables et de limiter les risques de pertes de données, de commits accidentels ou de divergences entre branches.

## 2. Périmètre du workflow Git

Ce workflow s'applique à toutes les modifications du dépôt :

| Type de travail | Exemples | Branche dédiée requise |
| --- | --- | --- |
| Backend | Routes, services, repositories, models, schemas, migrations Alembic | Oui |
| Desktop | Fenêtres PySide6, widgets, client HTTP `httpx`, styles QSS | Oui |
| Documentation | Guides, spécifications, sprints, architecture | Oui |
| Tests | Pytest, fixtures, tests API, tests services | Oui |
| Corrections | Bug backend, bug desktop, erreur documentaire | Oui |
| Refactor contrôlé | Simplification locale validée explicitement | Oui |
| Hotfix | Correction urgente issue de production ou de validation critique | Oui |

Le workflow ne remplace pas les guides de développement détaillés. Il définit les règles Git minimales à respecter avant, pendant et après chaque intervention.

## 3. Dépôt officiel

Le dépôt officiel du projet est :

```text
Tony-Marketing/veille-seo-geo
```

URL GitHub attendue :

```text
https://github.com/Tony-Marketing/veille-seo-geo
```

Commande de vérification du dépôt distant :

```powershell
git remote -v
```

Sortie attendue, à adapter selon le mode HTTPS ou SSH :

```text
origin  https://github.com/Tony-Marketing/veille-seo-geo.git (fetch)
origin  https://github.com/Tony-Marketing/veille-seo-geo.git (push)
```

## 4. Dossier local officiel

Le dossier local officiel est :

```text
C:\Users\assistant.marketing\Desktop\Veille SEO-GEO Groupe APPartner
```

Avant de lancer des commandes Git, vérifier que le terminal est positionné dans ce dossier :

```powershell
Get-Location
```

Sortie attendue :

```text
Path
----
C:\Users\assistant.marketing\Desktop\Veille SEO-GEO Groupe APPartner
```

## 5. Branche stable

La branche stable du projet est :

```text
main
```

`main` doit contenir uniquement du code et de la documentation validés.

Règles associées :

- aucun développement direct sur `main` ;
- aucune correction directe sur `main` ;
- aucune documentation ajoutée directement sur `main` ;
- tout changement doit passer par une branche dédiée puis par une Pull Request vers `main`.

## 6. Principe général de travail

Le cycle Git standard est le suivant :

```text
main à jour
   |
   v
branche dédiée
   |
   v
modifications ciblées
   |
   v
tests et vérifications
   |
   v
commit lisible
   |
   v
push de la branche
   |
   v
Pull Request vers main
   |
   v
revue et corrections
   |
   v
merge dans main
   |
   v
nettoyage local et distant
```

Ce cycle doit rester identique pour les sprints backend, les développements Desktop, les lots documentaires et les futures évolutions React.

## 7. Règle absolue : ne jamais développer directement sur `main`

Avant toute modification :

```powershell
git branch --show-current
```

Si la sortie est :

```text
main
```

alors il faut s'arrêter et créer une branche dédiée avant de modifier les fichiers.

Si des modifications existent déjà sur `main`, ne pas les commiter directement. Il faut d'abord diagnostiquer leur origine, puis les déplacer vers une branche dédiée si elles doivent être conservées.

## 8. Types de branches recommandés

| Type | Usage | Exemple |
| --- | --- | --- |
| `sprint` | Lot de développement planifié | `sprint-09-backend-geo` |
| `feature` | Fonctionnalité isolée | `feature-dashboard-kpis` |
| `fix` | Correction ciblée | `fix-auth-token-expiration` |
| `docs` | Documentation uniquement | `docs-development-guides` |
| `refactor` | Refactor contrôlé et validé | `refactor-websites-service` |
| `hotfix` | Correction urgente | `hotfix-api-healthcheck` |

Un refactor doit rester explicitement validé avant d'être entrepris. Il ne doit jamais accompagner silencieusement une fonctionnalité ou une correction.

## 9. Convention de nommage des branches

Format recommandé :

```text
type-sujet-court
```

ou, pour les sprints :

```text
sprint-numero-sujet
```

Bonnes pratiques :

- utiliser des minuscules ;
- séparer les mots avec des tirets ;
- éviter les accents et caractères spéciaux ;
- rester descriptif sans être trop long ;
- ne pas réutiliser le nom d'une branche ancienne encore active.

Exemples :

| Besoin | Branche recommandée |
| --- | --- |
| Sprint backend GEO | `sprint-09-backend-geo` |
| Documentation développement | `docs-development-guides` |
| Correction des routes websites | `fix-websites-routes` |
| Ajout page Desktop rapports | `feature-desktop-reports-page` |
| Hotfix sécurité API | `hotfix-api-security` |

## 10. Préparation d'une nouvelle branche

Avant de créer une branche :

1. se placer dans le dossier officiel ;
2. vérifier la branche active ;
3. vérifier l'état Git ;
4. revenir sur `main` si nécessaire ;
5. mettre `main` à jour ;
6. créer une branche dédiée depuis `main`.

Commandes de diagnostic :

```powershell
git branch --show-current
git status --short
git fetch origin
```

Une sortie vide de `git status --short` signifie que le dépôt local est propre.

## 11. Commandes PowerShell pour partir d'un `main` propre

Commandes recommandées :

```powershell
git branch --show-current
git status --short
git switch main
git pull --ff-only origin main
git status --short
```

Sortie attendue pour une branche propre :

```text
main
```

puis :

```text
Already up to date.
```

et enfin aucune ligne pour :

```powershell
git status --short
```

Si `git pull --ff-only` échoue, ne pas forcer. Il faut comprendre la divergence avant de continuer.

## 12. Création d'une branche de sprint

Depuis un `main` propre et à jour :

```powershell
git switch main
git pull --ff-only origin main
git switch -c sprint-09-backend-geo
```

Vérification :

```powershell
git branch --show-current
```

Sortie attendue :

```text
sprint-09-backend-geo
```

Une branche de sprint peut contenir plusieurs fichiers cohérents si le sprint le prévoit, mais elle doit rester limitée au périmètre validé.

## 13. Création d'une branche documentaire

Depuis un `main` propre et à jour :

```powershell
git switch main
git pull --ff-only origin main
git switch -c docs-development-guides
```

Une branche documentaire ne doit modifier que des fichiers de documentation, sauf validation explicite.

Exemples de fichiers attendus dans une branche documentaire :

```text
docs/development/Git_Workflow.md
docs/development/CONTRIBUTING.md
docs/development/TESTING.md
```

Chaque document important peut faire l'objet d'une branche ou d'un commit séparé si cela facilite la revue.

## 14. Création d'une branche de correction

Depuis un `main` propre et à jour :

```powershell
git switch main
git pull --ff-only origin main
git switch -c fix-websites-pagination
```

Une branche de correction doit contenir :

- la correction ciblée ;
- le test associé si le comportement est testable ;
- aucune modification opportuniste hors périmètre.

## 15. Vérification de la branche active

Commande :

```powershell
git branch --show-current
```

Exemples :

```text
docs-development-guides
```

ou :

```text
sprint-09-backend-geo
```

Si la branche active n'est pas celle prévue, s'arrêter avant toute modification.

## 16. Vérification de l'état du dépôt

Commande courte :

```powershell
git status --short
```

Commande détaillée :

```powershell
git status
```

Exemples de sorties :

| Sortie | Signification | Action recommandée |
| --- | --- | --- |
| aucune ligne | dépôt propre | continuer |
| ` M fichier.py` | fichier modifié non indexé | inspecter le diff |
| `A  fichier.py` | fichier ajouté et indexé | vérifier le staged diff |
| `?? fichier.md` | fichier non suivi | confirmer s'il doit être ajouté |
| `UU fichier.py` | conflit Git | résoudre avant de continuer |

## 17. Vérification des modifications non indexées

Commande :

```powershell
git diff
```

Limiter à un fichier :

```powershell
git diff -- backend/app/services/websites.py
```

Utilité :

- vérifier les modifications avant indexation ;
- repérer les changements accidentels ;
- contrôler l'absence de secrets ;
- confirmer que le périmètre est respecté.

## 18. Vérification des modifications indexées

Commande :

```powershell
git diff --cached
```

Statistiques indexées :

```powershell
git diff --cached --stat
```

Cette vérification est obligatoire avant tout commit.

Si le diff indexé contient un fichier non prévu, ne pas commiter. Il faut le désindexer sans perdre les modifications.

## 19. Vérification des espaces et erreurs de diff

Commande :

```powershell
git diff --check
```

Cette commande détecte notamment :

- espaces en fin de ligne ;
- erreurs de marqueurs de conflit ;
- problèmes de whitespace visibles par Git.

Sortie attendue :

```text

```

Une sortie vide signifie qu'aucune erreur de diff n'a été détectée.

## 20. Indexation ciblée des fichiers

Préférer une indexation explicite :

```powershell
git add docs/development/Git_Workflow.md
```

ou :

```powershell
git add backend/app/services/websites.py
git add tests/services/test_websites_services.py
```

Avantages :

- le périmètre du commit est maîtrisé ;
- les fichiers temporaires restent exclus ;
- les changements d'autres contributeurs ne sont pas capturés par accident.

## 21. Indexation progressive fichier par fichier

Workflow recommandé :

```powershell
git status --short
git diff -- docs/development/Git_Workflow.md
git add docs/development/Git_Workflow.md
git diff --cached -- docs/development/Git_Workflow.md
```

Pour indexer partiellement un fichier :

```powershell
git add -p backend/app/services/websites.py
```

`git add -p` est utile lorsque plusieurs changements indépendants sont présents dans un même fichier.

## 22. Indexation à éviter avec `git add -A` dans les cas sensibles

`git add -A` indexe toutes les suppressions, créations et modifications.

Il est à éviter lorsque :

- des fichiers non suivis sont présents ;
- des caches ont été générés ;
- des fichiers `.env` existent ;
- plusieurs tâches sont mélangées ;
- un autre contributeur ou Codex a laissé des fichiers indexés volontairement ;
- la branche contient des modifications hors périmètre.

Si `git add -A` est envisagé, vérifier avant :

```powershell
git status --short
git diff
git diff --cached
```

## 23. Règles de commit

Un commit doit être :

- lisible ;
- ciblé ;
- cohérent ;
- reproductible ;
- limité à un sujet ;
- exempt de secrets ;
- accompagné de tests lorsque le changement le justifie.

Ne pas commiter :

- caches ;
- environnements virtuels ;
- fichiers temporaires ;
- secrets ;
- logs locaux ;
- dépendances locales générées ;
- modifications hors périmètre.

## 24. Convention recommandée des messages de commit

Format recommandé :

```text
type: description courte
```

Types recommandés :

| Type | Usage |
| --- | --- |
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Refactor validé sans changement fonctionnel |
| `chore` | Maintenance sans impact métier |
| `perf` | Performance |
| `security` | Sécurité |

La description doit être en français, courte et explicite.

## 25. Exemples de messages de commit adaptés au projet

```text
docs: ajout du workflow Git détaillé
feat: ajout du service de suivi GEO
fix: correction de la pagination websites
test: ajout des tests du service administration
refactor: simplification contrôlée du repository keywords
security: durcissement de la validation des clés API
chore: mise à jour de la configuration Ruff
```

Exemples à éviter :

```text
update
fix
wip
misc
changes
```

## 26. Push d'une branche

Premier push d'une branche :

```powershell
git push -u origin docs-development-guides
```

Push suivant :

```powershell
git push
```

Avant tout push :

```powershell
git branch --show-current
git status --short
git log --oneline -5
```

Ne jamais pousser depuis `main` pour livrer une fonctionnalité.

## 27. Ouverture d'une Pull Request

La Pull Request doit être ouverte :

```text
branche de travail -> main
```

Exemple :

```text
docs-development-guides -> main
```

Avant ouverture :

- vérifier que la branche est poussée ;
- vérifier que les tests utiles sont passés ;
- vérifier que le diff est limité au périmètre ;
- vérifier qu'aucun secret n'est présent.

## 28. Contenu recommandé d'une Pull Request

Une Pull Request doit contenir :

| Section | Contenu attendu |
| --- | --- |
| Objectif | Pourquoi la modification existe |
| Changements | Liste claire des fichiers et comportements modifiés |
| Tests | Commandes exécutées et résultats |
| Risques | Points de vigilance ou limites |
| Captures | Si interface Desktop ou future interface React |
| Migration | Si Alembic ou changement de base de données |

Modèle simple :

```markdown
## Objectif

## Changements

## Tests

## Points de vigilance
```

## 29. Checklist avant Pull Request

- [ ] La branche active n'est pas `main`.
- [ ] Le dépôt ne contient pas de changements hors périmètre.
- [ ] Le diff a été relu.
- [ ] Les fichiers sensibles sont absents du diff.
- [ ] Les tests utiles ont été exécutés.
- [ ] `git diff --check` ne signale rien.
- [ ] Les migrations Alembic sont cohérentes si la base change.
- [ ] La documentation est mise à jour si nécessaire.
- [ ] La Pull Request cible `main`.

## 30. Merge de Pull Request

Le merge vers `main` doit être fait uniquement lorsque :

- la Pull Request est relue ;
- les tests sont verts ou les limites sont documentées ;
- la branche ne contient plus de conflits ;
- le diff est cohérent ;
- la branche est propre ;
- les migrations sont validées si nécessaire.

Le merge ne doit pas servir à intégrer des travaux partiels non relus.

## 31. Nettoyage après merge

Après merge :

```powershell
git switch main
git pull --ff-only origin main
git status --short
```

Puis, si la branche n'est plus utile :

```powershell
git branch -d docs-development-guides
git push origin --delete docs-development-guides
```

Ne supprimer une branche qu'après confirmation du merge.

## 32. Suppression de branche locale

Suppression normale, uniquement si la branche est mergée :

```powershell
git branch -d docs-development-guides
```

Si Git refuse :

```text
error: The branch 'docs-development-guides' is not fully merged.
```

Action recommandée :

- ne pas utiliser `-D` immédiatement ;
- vérifier si la branche contient encore des commits utiles ;
- demander validation avant suppression forcée.

## 33. Suppression de branche distante

Commande :

```powershell
git push origin --delete docs-development-guides
```

Avant suppression distante :

```powershell
git branch --merged main
git log --oneline main..docs-development-guides
```

Si `git log main..branche` affiche encore des commits, la branche contient du travail non intégré.

## 34. Vérification finale après nettoyage

Commandes :

```powershell
git switch main
git pull --ff-only origin main
git status --short
git branch --show-current
git branch
```

Sortie attendue :

```text
main
```

et aucun changement local.

## 35. Gestion des branches déjà mergées

Lister les branches locales déjà mergées dans `main` :

```powershell
git switch main
git pull --ff-only origin main
git branch --merged main
```

Supprimer une branche locale mergée :

```powershell
git branch -d nom-de-branche
```

Toujours vérifier que la branche n'est plus utilisée par une Pull Request active avant de la supprimer.

## 36. Gestion des branches non mergées

Lister les commits d'une branche non intégrés à `main` :

```powershell
git log --oneline main..nom-de-branche
```

Comparer les changements :

```powershell
git diff --stat main..nom-de-branche
git diff main..nom-de-branche
```

Action recommandée :

- conserver la branche si les commits sont utiles ;
- ouvrir ou mettre à jour une Pull Request ;
- demander validation avant toute suppression forcée.

## 37. Gestion des conflits Git

Un conflit apparaît généralement après :

```powershell
git pull
git merge main
git rebase main
```

Diagnostic :

```powershell
git status --short
```

Exemple :

```text
UU backend/app/services/websites.py
```

Résolution recommandée :

1. ouvrir le fichier en conflit ;
2. chercher les marqueurs `<<<<<<<`, `=======`, `>>>>>>>` ;
3. conserver la version correcte ou fusionner manuellement ;
4. relire le fichier complet ;
5. lancer les tests utiles ;
6. indexer le fichier résolu ;
7. finaliser le merge ou le rebase.

Ne jamais résoudre un conflit en supprimant du code sans comprendre son origine.

## 38. Gestion des fichiers non suivis

Un fichier non suivi apparaît ainsi :

```text
?? docs/development/Git_Workflow.md
```

Actions possibles :

| Cas | Action |
| --- | --- |
| Fichier prévu | relire puis `git add fichier` |
| Fichier temporaire | ne pas indexer |
| Secret ou `.env` | ne pas indexer, vérifier `.gitignore` |
| Fichier inconnu | demander confirmation |

Ne jamais ajouter automatiquement tous les fichiers non suivis sans inspection.

## 39. Gestion des fichiers déjà indexés

Afficher les fichiers indexés :

```powershell
git diff --cached --name-only
```

Afficher leur contenu :

```powershell
git diff --cached
```

Règle importante :

Si certains fichiers sont déjà indexés volontairement par un autre contributeur, Codex ne doit pas les désindexer sans demande explicite.

## 40. Désindexation sans perdre les modifications

Pour retirer un fichier de l'index sans perdre son contenu local :

```powershell
git restore --staged docs/development/Git_Workflow.md
```

Vérification :

```powershell
git status --short
```

Résultat typique :

```text
 M docs/development/Git_Workflow.md
```

ou, pour un nouveau fichier :

```text
?? docs/development/Git_Workflow.md
```

Cette commande ne supprime pas le fichier. Elle retire seulement le fichier de la zone d'indexation.

## 41. Annulation de modifications locales non voulues

Commande à utiliser avec prudence :

```powershell
git restore chemin/du/fichier
```

Effet :

- annule les modifications locales non indexées ;
- revient à la version du dernier commit ;
- peut faire perdre du travail local non sauvegardé.

Avant de l'utiliser :

```powershell
git diff -- chemin/du/fichier
```

Ne jamais exécuter cette commande sur un fichier modifié par quelqu'un d'autre sans validation.

## 42. Récupération d'un fichier depuis `main`

Pour récupérer la version de `main` d'un fichier précis :

```powershell
git restore --source main -- docs/architecture/ARCHITECTURE.md
```

Attention :

- cette commande remplace la version locale du fichier ;
- elle peut supprimer des modifications locales ;
- elle doit être précédée d'un `git diff`.

Diagnostic préalable :

```powershell
git diff -- docs/architecture/ARCHITECTURE.md
git show main:docs/architecture/ARCHITECTURE.md
```

## 43. Sécurité Git

Avant tout commit ou push, vérifier l'absence de données sensibles :

```powershell
git diff
git diff --cached
git status --short
```

Ne jamais commiter :

- clé API ;
- token ;
- mot de passe ;
- fichier `.env` ;
- dump de base de données ;
- archive locale ;
- fichier contenant des identifiants ;
- secret de service tiers.

Si un secret a été commité par erreur, ne pas se contenter d'un commit de suppression. Il faut considérer le secret comme compromis, le révoquer et traiter l'historique Git avec une procédure dédiée.

## 44. Fichiers et dossiers à ne jamais commiter

| Élément | Raison |
| --- | --- |
| `.venv/` | environnement virtuel local |
| `venv/` | environnement virtuel local |
| `.codex_deps/` | dépendances locales d'outillage |
| `__pycache__/` | cache Python |
| `*.pyc` | bytecode Python généré |
| `.pytest_cache/` | cache Pytest |
| `.ruff_cache/` | cache Ruff |
| fichiers temporaires | bruit et données locales |
| fichiers de secrets | risque sécurité |
| `.env` | variables sensibles |
| clés API | secret |
| tokens | secret |
| mots de passe | secret |

Vérifier aussi `.gitignore` lorsque de nouveaux outils génèrent des fichiers locaux.

## 45. Gestion des fins de ligne sous Windows

Sous Windows, Git peut convertir les fins de ligne selon la configuration locale.

Diagnostic :

```powershell
git config --get core.autocrlf
```

Valeurs fréquentes :

| Valeur | Effet |
| --- | --- |
| `true` | checkout en CRLF, commit en LF |
| `input` | commit en LF, pas de conversion au checkout |
| `false` | pas de conversion automatique |

La configuration des fins de ligne doit rester cohérente avec `.gitattributes` si ce fichier est configuré.

## 46. Cas des warnings `LF will be replaced by CRLF`

Warning typique :

```text
warning: in the working copy of 'fichier.md', LF will be replaced by CRLF the next time Git touches it
```

Ce warning n'est pas bloquant sauf demande explicite sur les fins de ligne.

Action recommandée :

- continuer si le diff est correct ;
- ne pas modifier massivement les fins de ligne ;
- ne pas reformater tout le dépôt ;
- signaler le warning si la Pull Request concerne précisément la normalisation des fins de ligne.

## 47. Règles spécifiques pour les migrations Alembic

Toute modification de structure PostgreSQL doit passer par Alembic.

Règles :

- une migration par changement cohérent ;
- nom de migration explicite ;
- modèle SQLAlchemy cohérent avec la migration ;
- schéma Pydantic cohérent avec le modèle ;
- tests ou vérifications de migration lorsque possible ;
- aucune requête SQL brute si SQLAlchemy permet de faire autrement.

Commandes utiles, à adapter depuis la racine ou le dossier backend selon la configuration :

```powershell
alembic current
alembic history
alembic upgrade head
```

Avant commit d'une migration :

```powershell
git diff -- backend/alembic/versions
git diff -- backend/app/models
git diff -- backend/app/schemas
```

## 48. Règles spécifiques pour les développements backend

Architecture à préserver :

```text
Routes -> Services -> Repositories -> Models
```

Règles :

- pas de logique métier dans les routes ;
- pas d'accès base direct depuis les routes ;
- services pour la logique métier ;
- repositories pour l'accès aux données ;
- models SQLAlchemy pour la persistance ;
- schemas Pydantic v2 pour les entrées et sorties ;
- tests Pytest pour les comportements importants.

Commandes de vérification recommandées :

```powershell
ruff check .
pytest
```

Pour une correction backend ciblée :

```powershell
pytest tests/services/test_websites_services.py
pytest tests/api/test_websites_routes.py
```

## 49. Règles spécifiques pour les développements Desktop PySide6

Le Desktop repose sur :

- PySide6 ;
- widgets dédiés ;
- pages dans `desktop/ui/` ;
- composants dans `desktop/widgets/` ;
- configuration dans `desktop/core/` ;
- appels API via `httpx`.

Règles :

- ne pas dupliquer la logique API dans les pages ;
- centraliser les appels HTTP dans le client prévu ;
- préserver les styles QSS existants ;
- éviter les refactors globaux d'interface sans validation ;
- tester les parcours utilisateur concernés.

Commandes utiles :

```powershell
python desktop/main.py
ruff check desktop
```

Si l'interface est modifiée, la Pull Request doit décrire les écrans concernés et ajouter des captures si possible.

## 50. Règles spécifiques pour la documentation

Une branche documentaire doit :

- modifier uniquement les fichiers documentaires prévus ;
- conserver une structure claire ;
- éviter les doublons inutiles ;
- mentionner les documents liés ;
- ne pas renommer ou déplacer des documents existants sans validation.

Avant commit :

```powershell
git status --short
git diff -- docs
git diff --check
```

Les documents de référence doivent rester cohérents avec :

- `README.md` ;
- `AGENTS.md` ;
- `docs/architecture/` ;
- `docs/api/` ;
- `docs/sprints/`.

## 51. Règles spécifiques pour Codex

Codex agit comme développeur logiciel senior, mais il ne remplace pas la validation humaine.

Règles obligatoires :

- vérifier la branche active avant modification ;
- ne jamais travailler directement sur `main` ;
- respecter le périmètre demandé ;
- ne pas supprimer de fichier sans demande explicite ;
- ne pas renommer de fichier sans demande explicite ;
- ne pas refactorer globalement sans validation explicite ;
- ne pas créer de commit sans demande explicite ;
- ne pas push sans demande explicite ;
- ne pas désindexer des fichiers déjà indexés volontairement par l'utilisateur.

## 52. Ce que Codex peut faire

Codex peut :

- analyser le dépôt ;
- lire les fichiers existants ;
- proposer un plan de modification ;
- créer ou modifier les fichiers explicitement demandés ;
- ajouter des tests si le périmètre le justifie ;
- exécuter les commandes de qualité disponibles ;
- produire un compte rendu clair ;
- signaler les anomalies au lieu d'inventer une solution.

Codex doit privilégier l'extension de l'existant.

## 53. Ce que Codex ne doit pas faire sans validation explicite

Codex ne doit pas faire sans validation :

- commit ;
- push ;
- suppression de fichier ;
- renommage de fichier ;
- déplacement de fichier ;
- refactor global ;
- ajout de dépendance ;
- modification hors périmètre ;
- réécriture d'architecture ;
- désindexation de fichiers déjà préparés par l'utilisateur ;
- commande destructive.

## 54. Workflow recommandé avec Codex

Workflow conseillé :

1. l'utilisateur indique la branche obligatoire et le fichier ciblé ;
2. Codex vérifie la branche active ;
3. Codex vérifie `git status --short` ;
4. Codex vérifie l'existence des fichiers concernés ;
5. Codex analyse les conventions existantes ;
6. Codex annonce les fichiers à créer ou modifier ;
7. Codex applique uniquement les changements validés ;
8. Codex exécute les vérifications demandées ;
9. Codex n'indexe rien sauf demande explicite ;
10. Codex fournit un rapport final.

Commandes minimales avant intervention :

```powershell
git branch --show-current
git status --short
```

Commandes minimales après intervention :

```powershell
git status --short
git diff --stat
git diff --check
```

## 55. Exemple de cycle complet pour un sprint backend

Préparation :

```powershell
git switch main
git pull --ff-only origin main
git switch -c sprint-09-backend-geo
```

Développement :

```powershell
git status --short
git diff
ruff check .
pytest
```

Indexation ciblée :

```powershell
git add backend/app/models/geo_result.py
git add backend/app/repositories/geo_results.py
git add backend/app/services/geo_results.py
git add backend/app/api/v1/routes/geo_results.py
git add tests/services/test_geo_results.py
```

Commit :

```powershell
git diff --cached
git commit -m "feat: ajout du suivi des résultats GEO"
```

Push et Pull Request :

```powershell
git push -u origin sprint-09-backend-geo
```

La Pull Request doit cibler `main`.

## 56. Exemple de cycle complet pour un lot documentaire

Préparation :

```powershell
git switch main
git pull --ff-only origin main
git switch -c docs-development-guides
```

Modification documentaire :

```powershell
git status --short
git diff -- docs/development
git diff --check
```

Indexation ciblée :

```powershell
git add docs/development/Git_Workflow.md
```

Commit :

```powershell
git commit -m "docs: ajout du workflow Git détaillé"
```

Push :

```powershell
git push -u origin docs-development-guides
```

## 57. Exemple de cycle complet pour une correction simple

Préparation :

```powershell
git switch main
git pull --ff-only origin main
git switch -c fix-admin-permissions
```

Diagnostic :

```powershell
git status --short
pytest tests/services/test_admin_services.py
```

Après correction :

```powershell
git diff
ruff check backend/app/services/admin.py
pytest tests/services/test_admin_services.py
git diff --check
```

Commit :

```powershell
git add backend/app/services/admin.py
git add tests/services/test_admin_services.py
git commit -m "fix: correction des permissions administration"
```

Push :

```powershell
git push -u origin fix-admin-permissions
```

## 58. Commandes de diagnostic utiles

| Besoin | Commande |
| --- | --- |
| Branche active | `git branch --show-current` |
| État court | `git status --short` |
| État détaillé | `git status` |
| Diff non indexé | `git diff` |
| Diff indexé | `git diff --cached` |
| Statistiques du diff | `git diff --stat` |
| Erreurs whitespace | `git diff --check` |
| Derniers commits | `git log --oneline -10` |
| Branches locales | `git branch` |
| Branches distantes | `git branch -r` |
| Branches mergées | `git branch --merged main` |
| Fichiers indexés | `git diff --cached --name-only` |
| Dépôts distants | `git remote -v` |

## 59. Commandes dangereuses à éviter ou à utiliser avec validation

Certaines commandes peuvent supprimer du travail local ou réécrire l'historique.

| Commande | Risque | Règle |
| --- | --- | --- |
| `git reset --hard` | supprime les modifications locales | Ne pas utiliser sans validation explicite |
| `git clean -fd` | supprime les fichiers non suivis | Ne pas utiliser sans validation explicite |
| `git push --force` | réécrit l'historique distant | Ne pas utiliser sans validation explicite |
| `git branch -D branche` | supprime une branche non mergée | Vérifier les commits avant |
| `git restore fichier` | annule les changements locaux | Relire `git diff` avant |
| `git checkout -- fichier` | ancienne forme destructive | Préférer `git restore`, avec prudence |

Alternative de diagnostic avant toute commande risquée :

```powershell
git status --short
git diff
git diff --cached
git log --oneline --decorate -10
```

## 60. Critères d'acceptation d'une branche propre

Une branche est considérée propre lorsque :

- elle part d'un `main` à jour ;
- elle ne contient que le périmètre prévu ;
- les fichiers sensibles sont absents ;
- les fichiers temporaires sont absents ;
- les tests utiles sont passés ;
- `git diff --check` ne signale rien ;
- la Pull Request cible `main` ;
- les conflits sont résolus ;
- les migrations sont cohérentes si présentes ;
- la documentation est cohérente si modifiée.

## 61. Checklist avant commit

- [ ] La branche active est correcte.
- [ ] La branche active n'est pas `main`.
- [ ] `git status --short` a été relu.
- [ ] `git diff` a été relu.
- [ ] `git diff --check` ne signale rien.
- [ ] Seuls les fichiers prévus sont indexés.
- [ ] `git diff --cached` a été relu.
- [ ] Aucun secret n'est présent.
- [ ] Les tests utiles ont été exécutés.
- [ ] Le message de commit est clair.

## 62. Checklist avant push

- [ ] La branche active est correcte.
- [ ] Aucun commit n'a été fait sur `main`.
- [ ] `git status --short` est propre.
- [ ] Les derniers commits sont cohérents.
- [ ] La branche distante visée est correcte.
- [ ] Aucun fichier sensible n'est dans l'historique récent.
- [ ] La Pull Request prévue cible `main`.

Commandes :

```powershell
git branch --show-current
git status --short
git log --oneline -5
```

## 63. Checklist avant merge

- [ ] La Pull Request cible `main`.
- [ ] La revue est terminée.
- [ ] Les tests sont verts ou les limites sont documentées.
- [ ] Il n'y a pas de conflit.
- [ ] Le diff final est relu.
- [ ] Les migrations sont validées si présentes.
- [ ] La documentation est à jour.
- [ ] Aucun secret n'est présent.
- [ ] La branche peut être supprimée après merge.

## 64. Checklist après merge

- [ ] Revenir sur `main`.
- [ ] Mettre `main` à jour.
- [ ] Vérifier l'état local.
- [ ] Supprimer la branche locale si elle est mergée.
- [ ] Supprimer la branche distante si elle n'est plus utile.
- [ ] Vérifier les branches restantes.
- [ ] Créer une nouvelle branche depuis `main` pour le prochain travail.

Commandes :

```powershell
git switch main
git pull --ff-only origin main
git status --short
git branch --merged main
```

## 65. Points à éviter

À éviter systématiquement :

- travailler sur `main` ;
- mélanger plusieurs sujets dans une branche ;
- mélanger refactor et fonctionnalité ;
- commiter des caches ;
- commiter `.env` ;
- commiter des secrets ;
- utiliser `git add -A` sans inspection ;
- résoudre un conflit sans comprendre les deux versions ;
- supprimer une branche non mergée sans vérification ;
- forcer un push ;
- créer une architecture parallèle ;
- placer la logique métier dans les routes FastAPI ;
- modifier des fichiers hors périmètre ;
- laisser Codex commiter ou pousser sans demande explicite.

## 66. Liens avec les futurs documents

Ce document sera complété par les guides suivants :

| Futur document | Rôle prévu |
| --- | --- |
| `docs/development/CONTRIBUTING.md` | Règles de contribution humaine et revue |
| `docs/development/CODING_STANDARDS.md` | Standards Python, TypeScript, documentation et style |
| `docs/development/BACKEND_DEVELOPMENT_GUIDE.md` | Guide détaillé FastAPI, SQLAlchemy, Alembic, Pydantic |
| `docs/development/DESKTOP_DEVELOPMENT_GUIDE.md` | Guide PySide6, widgets, client API, packaging futur |
| `docs/development/TESTING.md` | Stratégie Pytest, tests API, tests services, qualité |

Ces documents ne remplacent pas le workflow Git. Ils préciseront les règles techniques propres à chaque domaine.

## Matrice de responsabilités

| Responsabilité | Développeur | Relecteur | Mainteneur | Codex |
| --- | --- | --- | --- | --- |
| Vérifier la branche active | Responsable | Vérifie si nécessaire | Peut auditer | Responsable avant action |
| Créer une branche dédiée | Responsable | Non | Peut imposer la convention | Uniquement sur demande |
| Modifier le code ou la documentation | Responsable | Non | Peut intervenir | Oui, dans le périmètre demandé |
| Vérifier le diff | Responsable | Responsable en revue | Responsable final | Responsable avant compte rendu |
| Lancer les tests | Responsable | Peut demander | Peut bloquer le merge | Oui si demandé ou pertinent |
| Créer un commit | Responsable | Non | Peut le faire | Non sans demande explicite |
| Pousser une branche | Responsable | Non | Peut le faire | Non sans demande explicite |
| Ouvrir une Pull Request | Responsable | Non | Peut accompagner | Non sans demande explicite |
| Valider le merge | Non | Recommande | Responsable | Non |
| Supprimer une branche | Responsable après merge | Non | Peut nettoyer | Non sans validation |

## Diagramme ASCII du cycle Git complet

```text
            +----------------+
            | main stable    |
            +----------------+
                    |
                    | git pull --ff-only origin main
                    v
            +----------------+
            | branche dédiée |
            +----------------+
                    |
                    | modifications ciblées
                    v
            +----------------+
            | tests + lint   |
            +----------------+
                    |
                    | commit lisible
                    v
            +----------------+
            | push branche   |
            +----------------+
                    |
                    | Pull Request vers main
                    v
            +----------------+
            | revue + merge  |
            +----------------+
                    |
                    | retour main + pull
                    v
            +----------------+
            | nettoyage      |
            +----------------+
```

## Cas d'erreur fréquents et action recommandée

| Situation | Symptôme | Action recommandée |
| --- | --- | --- |
| Mauvaise branche | `git branch --show-current` affiche `main` | S'arrêter et créer une branche |
| Dépôt sale avant travail | `git status --short` affiche des fichiers | Identifier l'origine avant modification |
| Fichier cible déjà existant | `Test-Path fichier` retourne `True` | S'arrêter et demander confirmation |
| Fichiers non suivis inconnus | `?? fichier` | Ne pas indexer sans comprendre |
| Conflit | `UU fichier` | Résoudre manuellement puis tester |
| Pull impossible | `fatal: Not possible to fast-forward` | Diagnostiquer, ne pas forcer |
| Secret détecté | clé ou token dans le diff | Retirer, révoquer si exposé |
| Warning CRLF | `LF will be replaced by CRLF` | Non bloquant sauf sujet fins de ligne |
| Tests rouges | échec Pytest ou Ruff | Corriger avant PR ou documenter le blocage |

## Référence rapide quotidienne

Début de travail :

```powershell
git branch --show-current
git status --short
git switch main
git pull --ff-only origin main
git switch -c type-sujet
```

Pendant le travail :

```powershell
git status --short
git diff
git diff --check
```

Avant commit :

```powershell
git status --short
git diff
git diff --cached
ruff check .
pytest
```

Après merge :

```powershell
git switch main
git pull --ff-only origin main
git branch -d type-sujet
git push origin --delete type-sujet
```
