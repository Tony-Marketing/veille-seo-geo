# Guide de développement backend - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document guide le développement backend du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il définit les règles opérationnelles pour créer, modifier, tester et relire les fonctionnalités backend sans casser l'architecture existante.

Il sert de référence pour :

- les nouveaux sprints backend ;
- les évolutions FastAPI ;
- les routes API ;
- les services métier ;
- les repositories SQLAlchemy ;
- les modèles SQLAlchemy ;
- les schémas Pydantic v2 ;
- les migrations Alembic ;
- les tests backend ;
- les imports et exports de configuration ;
- les modules SEO, GEO, contenus, mots-clés, concurrents, rapports et administration ;
- les interventions assistées par Codex.

Ce guide complète `docs/development/Git_Workflow.md`, `docs/development/CONTRIBUTING.md` et `docs/development/CODING_STANDARDS.md`.

## 2. Périmètre du guide backend

Le guide couvre les éléments situés principalement dans :

```text
backend/
tests/
docs/api/
docs/architecture/
```

Il s'applique dès qu'une contribution touche :

| Zone | Exemples |
| --- | --- |
| API FastAPI | route, router, dépendance, statut HTTP |
| Services | validation métier, orchestration, erreurs métier |
| Repositories | requêtes SQLAlchemy, pagination, filtres |
| Models | tables, relations, contraintes |
| Schemas | entrées et sorties Pydantic v2 |
| Alembic | migrations PostgreSQL |
| Tests | Pytest API, services, repositories |
| Sécurité | authentification, permissions, secrets |
| Documentation API | erreurs, pagination, filtrage, auth |

Le Desktop PySide6 et le futur React sont concernés uniquement comme clients de l'API backend.

## 3. Stack backend officielle

Stack officielle :

| Domaine | Technologie |
| --- | --- |
| Langage | Python 3.13 |
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Base de données | PostgreSQL |
| Validation | Pydantic v2 |
| Tests | Pytest |
| Linting | Ruff |
| Client Desktop | PySide6 + httpx via API REST |
| Frontend futur | React + TypeScript + Vite + Tailwind CSS |

Toute nouvelle dépendance doit être justifiée explicitement avant ajout.

## 4. Architecture backend obligatoire

Architecture obligatoire :

```text
Routes -> Services -> Repositories -> Models
```

Règles fondamentales :

- les routes FastAPI ne contiennent pas de logique métier ;
- les routes appellent les services ;
- les services contiennent la logique métier ;
- les repositories contiennent uniquement l'accès aux données SQLAlchemy ;
- les modèles SQLAlchemy représentent les tables ;
- les schémas Pydantic gèrent les entrées et sorties API ;
- les migrations Alembic décrivent explicitement les changements de structure.

Le Desktop et le futur React doivent passer par l'API REST.

## 5. Structure recommandée du backend

Structure actuelle à préserver :

```text
backend/
  app/
    api/
      v1/
        routes/
        dependencies.py
        router.py
    core/
    models/
    repositories/
    schemas/
    services/
    main.py
  alembic/
    versions/
  alembic.ini
tests/
  api/
  services/
  conftest.py
```

Toute extension doit réutiliser ces dossiers avant d'en créer de nouveaux.

## 6. Rôle de `backend/app/main.py`

`backend/app/main.py` est le point d'entrée FastAPI.

Responsabilités :

- créer l'application FastAPI ;
- configurer le titre, la version et la documentation ;
- inclure le router API principal ;
- exposer les endpoints globaux strictement nécessaires.

À éviter :

- y placer de la logique métier ;
- y déclarer toutes les routes ;
- y construire des repositories ;
- y gérer des migrations ;
- y charger des secrets en dur.

## 7. Rôle de `backend/app/api/v1/routes/`

Ce dossier contient les routes API v1 par domaine.

Exemples de domaines existants :

```text
admin.py
auth.py
competitors.py
entities.py
keywords.py
reports.py
websites.py
```

Responsabilités d'une route :

- définir le chemin HTTP ;
- déclarer les dépendances ;
- recevoir les schemas d'entrée ;
- appeler le service ;
- retourner le schema de sortie ;
- traduire les erreurs si nécessaire ;
- appliquer authentification et autorisation.

Une route doit rester fine.

## 8. Rôle de `backend/app/services/`

Les services contiennent la logique métier.

Responsabilités :

- valider les règles fonctionnelles ;
- orchestrer un ou plusieurs repositories ;
- gérer les erreurs métier ;
- préparer les données retournées à l'API ;
- porter les règles de sécurité métier lorsque nécessaire ;
- rester testables indépendamment des routes.

Un service ne doit pas devenir une couche fourre-tout. Si le domaine grandit, créer des services spécialisés à valider lors de l'implémentation.

## 9. Rôle de `backend/app/repositories/`

Les repositories encapsulent l'accès SQLAlchemy.

Responsabilités :

- recevoir une session SQLAlchemy ;
- construire les requêtes ;
- gérer les filtres ;
- gérer la pagination ;
- créer, lire, mettre à jour ou supprimer des lignes ;
- retourner des modèles ou des résultats simples.

Interdits :

- décider des règles métier ;
- retourner des réponses HTTP ;
- dépendre de FastAPI ;
- concaténer des paramètres utilisateur dans du SQL brut.

## 10. Rôle de `backend/app/models/`

Les modèles SQLAlchemy représentent les tables PostgreSQL.

Responsabilités :

- déclarer les colonnes ;
- déclarer les relations ;
- définir les contraintes utiles ;
- rester cohérents avec les migrations Alembic ;
- ne pas stocker de secret en clair.

Les modèles ne doivent pas contenir la logique métier applicative.

## 11. Rôle de `backend/app/schemas/`

Les schémas Pydantic v2 définissent les contrats API.

Responsabilités :

- valider les payloads entrants ;
- définir les réponses sortantes ;
- éviter l'exposition de champs internes ;
- documenter implicitement l'API ;
- stabiliser les contrats pour le Desktop et le futur React.

Bon découpage recommandé :

```text
ResourceCreate
ResourceUpdate
ResourceRead
ResourceListItem
```

## 12. Rôle de `backend/app/core/`

`backend/app/core/` contient les éléments transverses.

Exemples :

- configuration ;
- connexion base ;
- sécurité ;
- paramètres applicatifs ;
- helpers transverses strictement nécessaires.

Règles :

- ne pas y placer de logique métier de domaine ;
- ne pas y mettre de code spécifique à une route ;
- ne pas y stocker de secret en dur ;
- garder les modules transverses simples.

## 13. Rôle de `backend/alembic/`

`backend/alembic/` contient la configuration et les migrations Alembic.

Responsabilités :

- historiser les changements de structure ;
- créer ou modifier les tables ;
- ajouter index et contraintes ;
- gérer les évolutions PostgreSQL ;
- fournir un chemin de migration reproductible.

Les migrations doivent être explicites. Elles ne doivent jamais utiliser `Base.metadata.create_all()` ni `Base.metadata.drop_all()`.

## 14. Rôle du dossier `tests/`

`tests/` contient les tests backend et API.

Structure actuelle :

```text
tests/
  api/
  services/
  conftest.py
```

Rôles :

- `tests/api/` : tests des routes et réponses HTTP ;
- `tests/services/` : tests des règles métier ;
- `tests/conftest.py` : fixtures partagées.

Des tests repositories peuvent être ajoutés si une contribution modifie fortement l'accès aux données.

## 15. Cycle de développement backend recommandé

Cycle recommandé :

```text
comprendre le besoin
   |
   v
identifier les couches impactées
   |
   v
modifier model/schema/repository/service/route
   |
   v
ajouter migration si structure DB modifiée
   |
   v
ajouter tests
   |
   v
exécuter Ruff et Pytest
   |
   v
relire le diff
   |
   v
préparer la Pull Request
```

Commandes initiales :

```powershell
git branch --show-current
git status --short
```

## 16. Création d'une fonctionnalité backend

Pour créer une fonctionnalité backend, déterminer d'abord les couches nécessaires.

Ordre recommandé :

1. définir le comportement attendu ;
2. vérifier les modèles existants ;
3. ajouter ou modifier le modèle si nécessaire ;
4. créer une migration si la base change ;
5. définir les schemas Pydantic ;
6. créer ou étendre le repository ;
7. créer ou étendre le service ;
8. créer ou étendre la route ;
9. ajouter les tests ;
10. documenter l'API si nécessaire.

Ne pas commencer par la route si les règles métier ne sont pas claires.

## 17. Création d'un module API

Un module API correspond à un domaine fonctionnel.

Exemples :

```text
websites
keywords
competitors
reports
geo_results
seo_audits
```

Fichiers possibles, à valider selon le besoin :

```text
backend/app/models/geo_result.py
backend/app/schemas/geo_result.py
backend/app/repositories/geo_result.py
backend/app/services/geo_result.py
backend/app/api/v1/routes/geo_result.py
tests/services/test_geo_result_service.py
tests/api/test_geo_result_routes.py
```

Le nommage exact doit rester cohérent avec les conventions existantes.

## 18. Création d'un modèle SQLAlchemy

Un modèle est nécessaire lorsqu'une nouvelle table ou relation est créée.

Exemple conceptuel :

```python
class GeoResult(Base):
    __tablename__ = "geo_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

À prévoir :

- migration Alembic ;
- schema Pydantic ;
- repository ;
- tests.

## 19. Création d'un schéma Pydantic v2

Un schema définit un contrat API.

Exemple conceptuel :

```python
class GeoResultCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    prompt: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class GeoResultRead(BaseModel):
    id: int
    provider: str
    prompt: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

Les schemas d'entrée ne doivent pas accepter les champs internes comme `created_by` si ces champs sont déterminés par le backend.

## 20. Création d'un repository

Un repository encapsule les accès SQLAlchemy.

Exemple conceptuel :

```python
class GeoResultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, result_id: int) -> GeoResult | None:
        return self.db.get(GeoResult, result_id)

    def list_by_provider(self, provider: str) -> list[GeoResult]:
        statement = select(GeoResult).where(GeoResult.provider == provider)
        return list(self.db.scalars(statement))
```

Le repository ne décide pas si un utilisateur a le droit de voir le résultat. Cette règle appartient au service ou aux dépendances d'autorisation.

## 21. Création d'un service

Un service porte le comportement métier.

Exemple conceptuel :

```python
class GeoResultService:
    def __init__(self, repository: GeoResultRepository) -> None:
        self.repository = repository

    def get_result(self, result_id: int) -> GeoResultRead:
        result = self.repository.get(result_id)
        if result is None:
            raise GeoResultNotFoundError("Résultat GEO introuvable.")
        return GeoResultRead.model_validate(result)
```

Le service peut orchestrer plusieurs repositories si le comportement métier le justifie.

## 22. Création d'une route FastAPI

Une route expose le service via HTTP.

Exemple conceptuel :

```python
@router.get("/{result_id}", response_model=GeoResultRead)
def get_geo_result(
    result_id: int,
    service: GeoResultService = Depends(get_geo_result_service),
) -> GeoResultRead:
    return service.get_result(result_id)
```

La route ne doit pas interroger directement SQLAlchemy.

## 23. Création d'une migration Alembic explicite

Une migration est nécessaire si la structure PostgreSQL change.

Exemple de commande, à adapter à la configuration locale :

```powershell
alembic revision -m "create geo results"
```

Puis écrire explicitement les opérations :

```python
def upgrade() -> None:
    op.create_table(
        "geo_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_geo_results_provider", "geo_results", ["provider"])
```

Ne jamais remplacer une migration par `Base.metadata.create_all()`.

## 24. Création des tests associés

Chaque fonctionnalité métier importante doit avoir des tests.

Tests recommandés :

| Couche | Test |
| --- | --- |
| Route | statut HTTP, payload, auth |
| Service | règles métier, erreurs |
| Repository | requêtes, filtres, pagination |
| Migration | upgrade local si possible |

Commandes :

```powershell
pytest tests/services
pytest tests/api
```

## 25. Règles pour les routes FastAPI

Les routes doivent :

- rester courtes ;
- déclarer les schemas ;
- appeler les services ;
- appliquer les dépendances de sécurité ;
- retourner des réponses cohérentes ;
- éviter la logique métier ;
- éviter les requêtes SQLAlchemy directes.

À éviter :

```python
@router.get("/")
def list_items(db: Session = Depends(get_db)):
    return db.scalars(select(Item)).all()
```

## 26. Règles pour les services métier

Les services doivent :

- contenir les règles métier ;
- valider les invariants ;
- orchestrer les repositories ;
- gérer les erreurs métier ;
- rester indépendants du Desktop ;
- être testables.

Exemples de règles métier :

- empêcher un doublon de domaine ;
- vérifier qu'un rapport appartient au projet ;
- refuser un accès sans permission ;
- calculer un score GEO ;
- valider un import de configuration.

## 27. Règles pour les repositories SQLAlchemy

Les repositories doivent :

- utiliser SQLAlchemy 2.x ;
- recevoir une session ;
- construire des requêtes sûres ;
- ne pas concaténer de paramètres utilisateur dans du SQL brut ;
- gérer pagination et filtres ;
- rester sans logique métier.

Recommandé :

```python
statement = select(Website).where(Website.domain == domain)
```

À éviter :

```python
statement = text(f"SELECT * FROM websites WHERE domain = '{domain}'")
```

## 28. Règles pour les modèles SQLAlchemy

Les modèles doivent :

- correspondre aux tables ;
- utiliser des types adaptés ;
- déclarer les relations utiles ;
- rester cohérents avec Alembic ;
- éviter la logique métier ;
- ne pas exposer de secret.

Toute modification structurelle d'un modèle implique une migration Alembic.

## 29. Règles pour les schémas Pydantic v2

Les schemas doivent :

- utiliser Pydantic v2 ;
- séparer entrée et sortie ;
- limiter les champs exposés ;
- définir les contraintes simples ;
- éviter les règles métier complexes ;
- utiliser `model_config = ConfigDict(from_attributes=True)` lorsque nécessaire pour valider depuis SQLAlchemy.

Les validations nécessitant la base doivent rester dans les services.

## 30. Règles pour les dépendances FastAPI

Les dépendances FastAPI servent à injecter :

- session SQLAlchemy ;
- utilisateur courant ;
- permissions ;
- services ;
- paramètres communs.

Elles ne doivent pas contenir de logique métier lourde.

Exemple conceptuel :

```python
def get_geo_result_service(
    db: Session = Depends(get_db),
) -> GeoResultService:
    repository = GeoResultRepository(db)
    return GeoResultService(repository)
```

## 31. Règles pour l'injection de session SQLAlchemy

La session SQLAlchemy doit être gérée par les dépendances prévues.

Règles :

- ne pas créer de moteur dans les routes ;
- ne pas créer de session globale mutable ;
- fermer ou libérer la session selon la dépendance existante ;
- injecter la session dans les repositories ;
- ne pas transmettre la session au Desktop.

Le Desktop ne reçoit jamais de connexion base.

## 32. Règles pour l'authentification

L'authentification identifie l'utilisateur.

Règles :

- utiliser les dépendances de sécurité existantes ;
- protéger les endpoints sensibles ;
- ne pas exposer les tokens ;
- ne pas logger les secrets ;
- tester les accès refusés ;
- documenter les exigences d'accès.

Un endpoint public doit être volontairement public.

## 33. Règles pour l'autorisation

L'autorisation vérifie les droits.

Règles :

- appliquer les permissions adaptées ;
- distinguer admin, rôle et permission métier ;
- refuser par défaut lorsqu'un doute existe ;
- tester les cas interdits ;
- ne pas déléguer l'autorisation au Desktop.

Exemple conceptuel :

```python
@router.get("/admin/settings")
def list_settings(
    current_user: User = Depends(require_permission("settings:read")),
) -> list[SettingRead]:
    ...
```

## 34. Règles pour les endpoints admin

Les endpoints admin sont sensibles.

Ils doivent :

- exiger une authentification ;
- exiger un rôle ou une permission adaptée ;
- limiter les données retournées ;
- journaliser les actions importantes sans secret ;
- valider strictement les entrées ;
- éviter les actions destructrices non confirmées.

Les imports et exports admin doivent être non destructifs et idempotents autant que possible.

## 35. Règles pour les imports/exports de configuration

Les imports/exports de configuration doivent être sûrs.

Règles :

- valider le format avant application ;
- ne pas supprimer de données sans validation ;
- être idempotents autant que possible ;
- détecter les doublons ;
- retourner un rapport d'import ;
- ne pas exposer de secrets ;
- journaliser les erreurs utiles.

Un import idempotent peut être relancé sans créer de doublons ni casser l'état existant.

## 36. Règles pour les endpoints SEO

Les endpoints SEO doivent couvrir les besoins de référencement naturel.

Exemples de domaines :

- balises ;
- contenus ;
- URLs ;
- positions ;
- Core Web Vitals ;
- maillage interne ;
- audits techniques.

Règles :

- paginer les listes ;
- filtrer par site ou projet ;
- historiser les mesures temporelles ;
- isoler les connecteurs externes dans `backend/connectors/` si ajoutés ;
- ne pas appeler un service externe directement depuis une route.

## 37. Règles pour les endpoints GEO

Les endpoints GEO concernent la visibilité dans les IA génératives.

Domaines :

- prompts analysés ;
- réponses IA ;
- citations de marques ;
- modèles IA ;
- fournisseurs IA ;
- scores de visibilité ;
- comparaison de réponses ;
- historique.

Règles :

- garder le système extensible ;
- éviter le couplage à un seul fournisseur ;
- historiser les résultats ;
- protéger les clés API ;
- isoler les connecteurs externes ;
- tester les calculs de score.

## 38. Règles pour les endpoints mots-clés

Les endpoints mots-clés doivent :

- gérer les listes paginées ;
- permettre le filtrage par site, projet, marché ou statut ;
- éviter les doublons ;
- historiser les positions si nécessaire ;
- garder les calculs métier dans les services ;
- exposer des réponses stables pour Desktop et futur React.

Les imports de mots-clés doivent signaler les lignes invalides.

## 39. Règles pour les endpoints contenus

Les endpoints contenus doivent traiter :

- pages ;
- articles ;
- métadonnées SEO ;
- qualité éditoriale ;
- opportunités d'amélioration ;
- liens internes.

Règles :

- ne pas stocker de contenu sensible sans besoin ;
- filtrer par site ou projet ;
- tracer les analyses importantes ;
- éviter les réponses trop lourdes sans pagination ;
- séparer analyse, stockage et restitution.

## 40. Règles pour les endpoints concurrents

Les endpoints concurrents doivent :

- rattacher les concurrents à un site, marché ou projet ;
- éviter les doublons de domaine ;
- permettre la comparaison ;
- historiser les observations ;
- protéger les données stratégiques par permissions.

Les calculs de comparaison doivent rester dans les services.

## 41. Règles pour les endpoints rapports

Les endpoints rapports doivent :

- générer ou lister des rapports ;
- filtrer par période, site ou projet ;
- éviter les traitements longs dans une requête synchrone si cela devient coûteux ;
- protéger les rapports sensibles ;
- documenter le format de sortie.

Pour les rapports volumineux, prévoir un traitement asynchrone ou un statut de génération à valider lors de l'implémentation.

## 42. Règles pour les endpoints sites web

Les endpoints sites web doivent :

- gérer les domaines ;
- éviter les doublons ;
- vérifier les statuts ;
- fournir une pagination ;
- exposer les informations utiles sans secrets ;
- servir de base aux modules SEO, GEO et rapports.

Les règles de validation des domaines doivent être centralisées dans les services ou helpers validés.

## 43. Règles pour la pagination

Toute liste potentiellement grande doit être paginée.

Paramètres habituels :

```text
page
page_size
search
sort
order
```

Règles :

- page minimale à 1 ;
- taille maximale ;
- ordre stable ;
- total retourné si besoin ;
- tests sur les limites ;
- documentation dans `docs/api/PAGINATION.md` si l'API évolue.

## 44. Règles pour le filtrage

Le filtrage doit être explicite.

Règles :

- whitelist des champs filtrables ;
- validation Pydantic ;
- pas de SQL brut concaténé ;
- filtres appliqués dans les repositories ;
- règles métier de visibilité dans les services ;
- tests sur les filtres importants.

Exemple conceptuel :

```python
if filters.provider is not None:
    statement = statement.where(GeoResult.provider == filters.provider)
```

## 45. Règles pour la gestion d'erreurs

Les erreurs doivent être cohérentes.

Règles :

- erreurs métier dans les services ;
- traduction HTTP au niveau route ou gestionnaire dédié ;
- pas de stack trace en production ;
- messages sobres ;
- logs internes sans secret ;
- codes HTTP adaptés.

Exemple de message acceptable :

```json
{
  "detail": "Ressource introuvable."
}
```

## 46. Règles pour les réponses API

Les réponses API doivent être stables.

Règles :

- utiliser des schemas Pydantic ;
- éviter les champs internes ;
- éviter les secrets ;
- garder un format prévisible ;
- versionner l'API si un changement devient cassant ;
- documenter les changements majeurs.

Les réponses doivent rester compatibles avec le Desktop et le futur React.

## 47. Règles pour les statuts HTTP

Codes recommandés :

| Code | Usage |
| --- | --- |
| `200` | lecture ou mise à jour réussie |
| `201` | création réussie |
| `204` | suppression ou action sans contenu |
| `400` | requête invalide |
| `401` | non authentifié |
| `403` | accès interdit |
| `404` | ressource introuvable |
| `409` | conflit métier |
| `422` | validation FastAPI/Pydantic |
| `500` | erreur interne non exposée en détail |

Un statut doit correspondre au comportement réel.

## 48. Règles pour les transactions SQLAlchemy

Les transactions doivent être maîtrisées.

Règles :

- éviter les commits dispersés sans stratégie ;
- grouper les opérations cohérentes ;
- rollback en cas d'erreur si nécessaire ;
- ne pas laisser une session dans un état incohérent ;
- tester les erreurs critiques ;
- documenter les transactions complexes.

Pour les workflows multi-étapes, la stratégie transactionnelle doit être validée lors de l'implémentation.

## 49. Règles pour les contraintes PostgreSQL

Les contraintes garantissent l'intégrité.

Contraintes recommandées selon le cas :

- `NOT NULL` ;
- `UNIQUE` ;
- clés étrangères ;
- contraintes de vérification ;
- valeurs par défaut.

Les contraintes doivent être cohérentes avec les validations Pydantic et les règles métier.

## 50. Règles pour les index PostgreSQL

Un index doit répondre à un besoin identifié.

Cas fréquents :

- recherche par domaine ;
- filtrage par statut ;
- filtrage par fournisseur IA ;
- tri par date ;
- jointure par clé étrangère ;
- contrainte d'unicité.

À éviter :

- indexer tous les champs ;
- créer un index non utilisé ;
- oublier l'impact sur les écritures.

## 51. Règles pour les suppressions contrôlées

Avant une suppression, décider :

- suppression physique ;
- désactivation logique ;
- archivage ;
- conservation historique ;
- cascade ou restriction ;
- audit.

Pour les données métier importantes, une désactivation logique est souvent recommandée.

Toute suppression destructive doit être explicitement validée.

## 52. Règles pour les champs d'audit

Champs d'audit fréquents :

```text
created_at
updated_at
created_by
updated_by
```

Règles :

- `created_at` défini à la création ;
- `updated_at` mis à jour à chaque modification ;
- `created_by` renseigné depuis l'utilisateur authentifié si disponible ;
- `updated_by` renseigné lors des modifications ;
- ne pas accepter ces champs directement depuis un payload utilisateur sans validation ;
- prévoir index ou filtres si utilisés en recherche.

Les champs d'audit doivent être cohérents avec les besoins d'administration.

## 53. Règles pour l'idempotence

Un traitement idempotent peut être relancé sans effet indésirable.

Cas importants :

- imports de configuration ;
- imports de mots-clés ;
- synchronisations externes ;
- créations à clé naturelle ;
- tâches de maintenance.

Règles :

- utiliser une clé stable ;
- détecter les doublons ;
- retourner un rapport ;
- éviter les suppressions implicites ;
- tester les relances.

## 54. Règles pour les validations métier

Les validations métier appartiennent aux services.

Exemples :

- domaine unique ;
- projet actif ;
- permission nécessaire ;
- période valide ;
- fournisseur IA supporté ;
- limite de volume ;
- cohérence entre site et rapport.

Les validations simples de format peuvent être dans Pydantic, mais les validations dépendant des données doivent être dans les services.

## 55. Règles pour les erreurs métier

Les erreurs métier doivent être compréhensibles.

Recommandé :

```python
class GeoResultNotFoundError(Exception):
    """Résultat GEO introuvable."""
```

Ou, si la convention locale utilise `HTTPException` dans les services, rester cohérent avec l'existant tout en gardant la logique métier dans le service.

À éviter :

```python
raise Exception("error")
```

## 56. Règles pour la journalisation

La journalisation doit aider sans exposer.

Règles :

- pas de tokens ;
- pas de mots de passe ;
- pas de clés API ;
- pas de payload sensible complet ;
- contexte utile ;
- niveau adapté ;
- corrélation possible si un identifiant de requête est ajouté plus tard.

Exemple conceptuel :

```python
logger.info("Rapport généré", extra={"report_id": report.id})
```

## 57. Règles pour la sécurité backend

Règles obligatoires :

- authentifier les endpoints sensibles ;
- vérifier les permissions ;
- valider les entrées ;
- limiter les réponses ;
- ne jamais exposer de secrets ;
- ne pas retourner de stack traces en production ;
- éviter les dépendances non justifiées ;
- gérer les erreurs de manière sobre ;
- auditer les actions admin critiques.

La sécurité doit être intégrée dès la conception, pas ajoutée après coup.

## 58. Données sensibles à ne jamais exposer

Données interdites dans les commits, logs et réponses API :

| Donnée | Exemple |
| --- | --- |
| Mot de passe | `password` |
| Token | JWT, token d'accès |
| Clé API | OpenAI, Google, service tiers |
| Secret applicatif | clé de signature |
| `.env` | variables locales |
| URL DB complète | contient souvent un mot de passe |
| Stack trace production | chemins et détails internes |

Un secret exposé doit être révoqué.

## 59. Variables d'environnement backend

Les variables d'environnement doivent être chargées via la configuration prévue.

Règles :

- ne pas commiter `.env` ;
- documenter les variables attendues ;
- fournir des exemples non sensibles si nécessaire ;
- valider les valeurs obligatoires ;
- ne pas lire l'environnement partout dans le code ;
- centraliser la configuration dans `backend/app/core/`.

Les secrets doivent rester hors Git.

## 60. Gestion des secrets

Les secrets doivent être :

- stockés hors dépôt ;
- injectés par environnement ;
- jamais affichés dans les logs ;
- jamais retournés par l'API ;
- jamais inclus dans les tests réels ;
- remplacés par des valeurs factices dans la documentation.

Exemple de valeur documentaire acceptable :

```text
OPENAI_API_KEY=sk-example-not-a-real-key
```

## 61. Migrations Alembic : règles obligatoires

Règles obligatoires :

- une migration par changement cohérent ;
- opérations explicites ;
- nom de migration descriptif ;
- cohérence modèle/migration ;
- vérification `alembic upgrade head` si possible ;
- prudence sur suppressions et renommages ;
- pas de `create_all` ;
- pas de `drop_all`.

Avant Pull Request :

```powershell
alembic current
alembic history
alembic upgrade head
```

## 62. Interdiction de `Base.metadata.create_all()` dans les migrations

Interdit :

```python
Base.metadata.create_all(bind=engine)
```

Raisons :

- contourne Alembic ;
- ne décrit pas précisément les changements ;
- peut créer des différences entre environnements ;
- rend les revues de migration difficiles.

Utiliser les opérations Alembic explicites.

## 63. Interdiction de `Base.metadata.drop_all()` dans les migrations

Interdit :

```python
Base.metadata.drop_all(bind=engine)
```

Raisons :

- suppression massive ;
- perte de données ;
- comportement incompatible avec une migration contrôlée ;
- risque critique en production.

Toute suppression doit être ciblée, documentée et validée.

## 64. Exemple conceptuel de migration Alembic explicite

Exemple conceptuel :

```python
"""create geo results table"""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        "geo_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_geo_results_provider", "geo_results", ["provider"])


def downgrade() -> None:
    op.drop_index("ix_geo_results_provider", table_name="geo_results")
    op.drop_table("geo_results")
```

Le `downgrade` doit être prudent. S'il est destructeur, le signaler dans la Pull Request.

## 65. Exemple conceptuel de modèle SQLAlchemy

Exemple conceptuel :

```python
class GeoResult(Base):
    __tablename__ = "geo_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

À valider lors de l'implémentation :

- types exacts ;
- contraintes ;
- relation avec site, projet ou entité ;
- champs d'audit ;
- index.

## 66. Exemple conceptuel de schéma Pydantic v2

Exemple conceptuel :

```python
class GeoResultCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    prompt: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class GeoResultRead(BaseModel):
    id: int
    provider: str
    prompt: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

Ne pas exposer de champs sensibles dans les schemas de sortie.

## 67. Exemple conceptuel de repository

Exemple conceptuel :

```python
class GeoResultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict[str, object]) -> GeoResult:
        result = GeoResult(**data)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get(self, result_id: int) -> GeoResult | None:
        return self.db.get(GeoResult, result_id)
```

La stratégie de commit peut être adaptée à la convention locale et aux transactions du service.

## 68. Exemple conceptuel de service

Exemple conceptuel :

```python
class GeoResultService:
    def __init__(self, repository: GeoResultRepository) -> None:
        self.repository = repository

    def create_result(self, payload: GeoResultCreate) -> GeoResultRead:
        result = self.repository.create(payload.model_dump())
        return GeoResultRead.model_validate(result)

    def get_result(self, result_id: int) -> GeoResultRead:
        result = self.repository.get(result_id)
        if result is None:
            raise GeoResultNotFoundError("Résultat GEO introuvable.")
        return GeoResultRead.model_validate(result)
```

Les erreurs métier doivent être traduites en réponses API cohérentes.

## 69. Exemple conceptuel de route FastAPI

Exemple conceptuel :

```python
router = APIRouter(prefix="/geo-results", tags=["GEO"])


@router.post("/", response_model=GeoResultRead, status_code=status.HTTP_201_CREATED)
def create_geo_result(
    payload: GeoResultCreate,
    service: GeoResultService = Depends(get_geo_result_service),
) -> GeoResultRead:
    return service.create_result(payload)
```

La route ne contient pas la règle métier.

## 70. Exemple conceptuel de test route

Exemple conceptuel :

```python
def test_create_geo_result_returns_201(client):
    payload = {
        "provider": "chatgpt",
        "prompt": "Quels acteurs citer ?",
        "answer": "Réponse conceptuelle.",
    }

    response = client.post("/api/v1/geo-results/", json=payload)

    assert response.status_code == 201
    assert response.json()["provider"] == "chatgpt"
```

À adapter aux fixtures d'authentification et de base existantes.

## 71. Exemple conceptuel de test service

Exemple conceptuel :

```python
def test_get_result_raises_when_missing(service):
    with pytest.raises(GeoResultNotFoundError):
        service.get_result(999)
```

Les tests services doivent viser la logique métier, pas les détails HTTP.

## 72. Exemple conceptuel de test repository

Exemple conceptuel :

```python
def test_repository_get_returns_created_result(repository):
    created = repository.create(
        {
            "provider": "chatgpt",
            "prompt": "Prompt",
            "answer": "Answer",
        }
    )

    assert repository.get(created.id) == created
```

Les tests repositories doivent être ajoutés lorsque le comportement SQLAlchemy est significatif.

## 73. Commandes PowerShell utiles pour le backend

Commandes :

```powershell
git branch --show-current
git status --short
ruff check backend
ruff check tests
pytest tests/services
pytest tests/api
git diff --check
```

Diagnostic des fichiers :

```powershell
git diff -- backend
git diff -- tests
git diff --cached
```

## 74. Commandes de tests recommandées

Tests globaux :

```powershell
pytest
```

Tests API :

```powershell
pytest tests/api
```

Tests services :

```powershell
pytest tests/services
```

Tests ciblés :

```powershell
pytest tests/api/test_websites_routes.py
pytest tests/services/test_websites_services.py
```

## 75. Commandes Ruff recommandées

Commandes :

```powershell
ruff check .
ruff check backend
ruff check backend tests
ruff check tests
```

Si Ruff échoue, corriger les erreurs dans le périmètre modifié. Ne pas reformater ou modifier tout le dépôt sans validation.

## 76. Workflow avec Codex pour une fonctionnalité backend

Workflow recommandé :

1. indiquer la branche obligatoire ;
2. indiquer le module backend ciblé ;
3. lister les fichiers autorisés ;
4. interdire les fichiers hors périmètre ;
5. demander `git branch --show-current` ;
6. demander `git status --short` ;
7. demander l'analyse de l'existant ;
8. demander le plan des fichiers à créer ou modifier ;
9. valider avant modification importante ;
10. demander tests, Ruff et compte rendu.

Codex ne doit pas commiter ni pousser sans demande explicite.

## 77. Ce que Codex peut modifier dans un sprint backend

Codex peut modifier, si explicitement demandé :

- routes du module ciblé ;
- services du module ciblé ;
- repositories du module ciblé ;
- modèles concernés ;
- schemas concernés ;
- migrations Alembic nécessaires ;
- tests associés ;
- documentation liée.

Chaque fichier doit être justifié avant modification importante.

## 78. Ce que Codex ne doit pas modifier sans validation explicite

Codex ne doit pas modifier sans validation :

- fichiers hors périmètre ;
- architecture globale ;
- dépendances ;
- configuration sensible ;
- fichiers déjà indexés par l'utilisateur ;
- migrations destructrices ;
- noms de fichiers existants ;
- emplacements de dossiers ;
- secrets ;
- `.env`.

Codex ne doit pas supprimer, renommer, refactorer globalement, commiter ou pousser sans demande explicite.

## 79. Checklist avant modification backend

- [ ] Branche active vérifiée.
- [ ] Branche différente de `main`.
- [ ] `git status --short` relu.
- [ ] Fichiers déjà indexés identifiés.
- [ ] Domaine fonctionnel compris.
- [ ] Couches impactées identifiées.
- [ ] Tests existants localisés.
- [ ] Migrations nécessaires évaluées.
- [ ] Risques de sécurité identifiés.
- [ ] Fichiers hors périmètre exclus.

Commandes :

```powershell
git branch --show-current
git status --short
```

## 80. Checklist avant migration

- [ ] Changement de structure confirmé.
- [ ] Modèle SQLAlchemy mis à jour ou prévu.
- [ ] Migration Alembic explicite.
- [ ] Pas de `Base.metadata.create_all()`.
- [ ] Pas de `Base.metadata.drop_all()`.
- [ ] Données existantes prises en compte.
- [ ] Index et contraintes justifiés.
- [ ] Downgrade relu si présent.
- [ ] `alembic upgrade head` prévu si possible.

## 81. Checklist avant tests

- [ ] Tests routes si endpoint modifié.
- [ ] Tests services si règle métier modifiée.
- [ ] Tests repositories si requête complexe ajoutée.
- [ ] Fixtures adaptées.
- [ ] Cas d'erreur couverts.
- [ ] Auth et permissions testées si endpoint sensible.
- [ ] Pagination et filtrage testés si concernés.
- [ ] Ruff prévu.

## 82. Checklist avant commit

- [ ] `git status --short` relu.
- [ ] `git diff` relu.
- [ ] `git diff --cached` relu.
- [ ] Aucun secret.
- [ ] Aucun fichier temporaire.
- [ ] Aucun changement hors périmètre.
- [ ] Ruff exécuté.
- [ ] Pytest exécuté.
- [ ] `git diff --check` sans erreur.
- [ ] Message de commit clair.

Codex ne doit pas faire ce commit sans demande explicite.

## 83. Checklist de revue backend

Le relecteur vérifie :

- routes fines ;
- logique métier dans les services ;
- repositories limités aux données ;
- modèles cohérents avec Alembic ;
- schemas Pydantic adaptés ;
- auth et permissions ;
- erreurs API cohérentes ;
- pagination et filtrage ;
- tests suffisants ;
- absence de secrets ;
- absence de SQL brut dangereux ;
- compatibilité Desktop et futur React.

## 84. Critères d'acceptation d'une fonctionnalité backend

Une fonctionnalité backend est acceptable si :

- elle répond au besoin ;
- elle respecte `Routes -> Services -> Repositories -> Models` ;
- elle est testée ;
- elle ne contient pas de secret ;
- elle ne modifie pas de fichiers hors périmètre ;
- elle utilise des migrations explicites si nécessaire ;
- elle protège les endpoints sensibles ;
- elle gère les erreurs proprement ;
- elle reste compatible avec les clients API.

## 85. Points à éviter

À éviter systématiquement :

- logique métier dans les routes ;
- accès SQLAlchemy direct depuis les routes ;
- accès Desktop direct à PostgreSQL ;
- SQL brut construit avec des entrées utilisateur ;
- stack traces exposées en production ;
- migrations avec `Base.metadata.create_all()` ;
- migrations avec `Base.metadata.drop_all()` ;
- secrets dans Git ;
- `.env` dans Git ;
- refactor global non validé ;
- dépendance ajoutée sans justification ;
- suppression destructive non validée ;
- tests ignorés.

## 86. Liens avec les documents

Documents liés :

| Document | Rôle |
| --- | --- |
| `docs/development/Git_Workflow.md` | workflow Git officiel |
| `docs/development/CONTRIBUTING.md` | règles de contribution |
| `docs/development/CODING_STANDARDS.md` | standards de code |
| `docs/development/DESKTOP_DEVELOPMENT_GUIDE.md` | guide Desktop futur |
| `docs/development/TESTING.md` | guide tests futur |
| `docs/api/AUTHENTICATION.md` | authentification API |
| `docs/api/ERROR_HANDLING.md` | erreurs API |
| `docs/api/PAGINATION.md` | pagination API |
| `docs/api/FILTERING.md` | filtrage API |
| `docs/architecture/BACKEND_ARCHITECTURE.md` | architecture backend |
| `docs/architecture/API_ARCHITECTURE.md` | architecture API |
| `docs/architecture/DATABASE_ARCHITECTURE.md` | architecture base de données |
| `docs/specifications/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | exigences fonctionnelles |
| `docs/specifications/DATABASE_DESIGN_SPECIFICATION.md` | conception base |

Ces documents doivent rester cohérents entre eux.

## Matrice de responsabilité backend

| Responsabilité | Routes | Services | Repositories | Modèles | Schémas | Migrations | Tests |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Exposer HTTP | Oui | Non | Non | Non | Non | Non | Vérifie |
| Logique métier | Non | Oui | Non | Non | Non | Non | Vérifie |
| Accès données | Non | Orchestre | Oui | Mapping | Non | Structure | Vérifie |
| Validation payload | Déclenche | Complète | Non | Non | Oui | Non | Vérifie |
| Structure DB | Non | Non | Utilise | Déclare | Non | Applique | Vérifie |
| Auth/permissions | Dépendances | Règles métier | Non | Non | Non | Non | Vérifie |
| Pagination | Déclare paramètres | Contrôle | Applique | Non | Décrit | Non | Vérifie |
| Erreurs API | Traduit | Déclenche métier | Non | Non | Non | Non | Vérifie |

## Matrice de contrôle par type de changement backend

| Changement | Fichiers typiques | Contrôles obligatoires | Risque principal |
| --- | --- | --- | --- |
| Nouvelle route | `api/v1/routes/`, `schemas/`, `services/` | tests API, auth | logique métier dans route |
| Nouvelle règle métier | `services/` | tests services | régression fonctionnelle |
| Nouvelle requête | `repositories/` | tests services/repository | performance ou filtre incorrect |
| Nouveau modèle | `models/`, `alembic/versions/` | migration, tests | incohérence DB |
| Nouveau schema | `schemas/` | tests API | exposition de champs |
| Migration | `alembic/versions/` | upgrade local | perte de données |
| Endpoint admin | `routes/admin.py`, services | tests auth/permissions | accès non autorisé |
| Import config | services, schemas, routes | idempotence, tests erreurs | destruction de données |
| Module GEO | models, services, repositories | tests calculs, sécurité clés | couplage fournisseur |
| Rapport | services, routes | tests et volumes | traitement long synchrone |

## Diagramme ASCII de l'architecture obligatoire

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
     |
     v
PostgreSQL
```

## Diagramme ASCII du flux d'une requête API

```text
Client Desktop PySide6 / futur React
        |
        | HTTP REST
        v
FastAPI route (/api/v1/...)
        |
        | Depends(auth, db, service)
        v
Service métier
        |
        | appelle
        v
Repository SQLAlchemy
        |
        | select / insert / update / delete
        v
PostgreSQL
        |
        | résultat
        v
Repository -> Service -> Schema Pydantic -> Réponse JSON
```

## Commandes de diagnostic rapides

Vérification de branche et état :

```powershell
git branch --show-current
git status --short
```

Diff backend :

```powershell
git diff -- backend
git diff -- tests
git diff --check
```

Fichiers indexés :

```powershell
git diff --cached --name-only
git diff --cached
```

## Section de prudence

Ne pas utiliser sans validation explicite :

```powershell
git reset --hard
git clean -fd
git push --force
```

Ne pas utiliser dans les migrations :

```python
Base.metadata.create_all(bind=engine)
Base.metadata.drop_all(bind=engine)
```

Ne pas construire de SQL avec concaténation de paramètres utilisateur :

```python
text(f"SELECT * FROM websites WHERE domain = '{domain}'")
```

En cas d'incertitude, arrêter la modification et demander confirmation.
