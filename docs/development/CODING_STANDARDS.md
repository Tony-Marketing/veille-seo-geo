# Standards de code - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit les standards de code du projet **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence pour produire un code homogène, lisible, testable et compatible avec l'architecture existante.

Il couvre :

- le backend FastAPI ;
- les services métier ;
- les repositories SQLAlchemy ;
- les modèles SQLAlchemy ;
- les schémas Pydantic v2 ;
- les migrations Alembic ;
- les tests Pytest ;
- le linting Ruff ;
- le Desktop PySide6 ;
- les futurs développements React ;
- les contributions assistées par Codex.

Ce document ne remplace pas les guides spécialisés. Il fixe le socle commun attendu avant toute contribution.

## 2. Périmètre des standards de code

Les standards s'appliquent à toutes les zones du dépôt :

| Zone | Technologies | Standards principaux |
| --- | --- | --- |
| Backend | Python 3.13, FastAPI | couches séparées, typage, tests |
| Données | SQLAlchemy 2.x, PostgreSQL | repositories, migrations explicites |
| Validation | Pydantic v2 | schémas d'entrée et de sortie clairs |
| Qualité | Ruff, Pytest | linting et tests ciblés |
| Desktop | PySide6, httpx | API REST uniquement, pas d'accès base |
| Documentation | Markdown | structure claire, exemples prudents |
| Frontend futur | React, TypeScript, Vite, Tailwind CSS | conventions à prévoir |
| Codex | assistance ciblée | périmètre strict, pas de commit sans demande |

Une règle locale existante prime sur une recommandation générale si elle est cohérente avec l'architecture.

## 3. Principes généraux

Principes obligatoires :

- préserver l'architecture existante ;
- travailler par extension de l'existant ;
- limiter les changements au périmètre demandé ;
- éviter les duplications ;
- écrire du code testable ;
- séparer les responsabilités ;
- ne jamais commiter de secrets ;
- documenter les comportements importants ;
- préférer une solution simple et explicite.

À retenir :

```text
Un changement acceptable doit être lisible, ciblé, vérifiable et réversible par revue.
```

## 4. Standards Python 3.13

Le code Python doit utiliser les capacités modernes de Python 3.13 sans rendre le code inutilement complexe.

Recommandé :

- type hints sur les fonctions publiques ;
- noms explicites ;
- fonctions courtes ;
- exceptions spécifiques ;
- imports organisés ;
- docstrings Google pour les fonctions importantes ;
- compatibilité Ruff ;
- tests Pytest pour les règles métier.

Exemple conceptuel :

```python
def normalize_domain(domain: str) -> str:
    """Normalise un nom de domaine.

    Args:
        domain: Nom de domaine saisi par l'utilisateur.

    Returns:
        Domaine normalisé en minuscules, sans espaces.
    """
    return domain.strip().lower()
```

## 5. Style de nommage Python

Conventions :

| Élément | Convention | Exemple |
| --- | --- | --- |
| Variable | `snake_case` | `website_id` |
| Fonction | `snake_case` | `list_websites` |
| Méthode | `snake_case` | `get_by_id` |
| Classe | `PascalCase` | `WebsiteService` |
| Constante | `UPPER_CASE` | `DEFAULT_PAGE_SIZE` |
| Module | `snake_case.py` | `website_service.py` |
| Test | `test_*.py` | `test_websites_services.py` |

À éviter :

```python
WebsiteID = 1
def GetWebsite():
    ...
```

## 6. Organisation des imports

Les imports doivent rester lisibles et stables.

Ordre recommandé :

1. bibliothèque standard ;
2. dépendances tierces ;
3. imports internes du projet.

Exemple conceptuel :

```python
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.v1.dependencies import get_db
from backend.app.services.websites import WebsiteService
```

Règles :

- éviter les imports inutilisés ;
- éviter les imports circulaires ;
- ne pas masquer les erreurs d'import ;
- laisser Ruff signaler les incohérences.

## 7. Typage Python recommandé

Le typage doit clarifier les contrats.

Recommandé :

```python
def get_website(website_id: int) -> Website | None:
    ...
```

Pour les collections :

```python
def list_domains(websites: list[Website]) -> list[str]:
    ...
```

Pour les mappings :

```python
def build_filters(params: dict[str, str]) -> dict[str, object]:
    ...
```

À éviter :

```python
def get_website(website_id):
    ...
```

Les types ne doivent pas remplacer les tests, mais ils réduisent les ambiguïtés.

## 8. Gestion des constantes

Les constantes doivent être explicites et centralisées lorsque cela évite la duplication.

Exemples :

```python
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
SUPPORTED_AI_PROVIDERS = ("chatgpt", "gemini", "claude", "perplexity", "mistral")
```

Règles :

- éviter les nombres magiques ;
- nommer les constantes en `UPPER_CASE` ;
- ne pas stocker de secret dans une constante ;
- placer les constantes dans le module le plus proche du besoin ;
- centraliser uniquement si plusieurs modules les utilisent réellement.

## 9. Gestion des exceptions

Les exceptions doivent être précises.

Recommandé :

```python
class WebsiteNotFoundError(Exception):
    """Erreur levée lorsqu'un site demandé n'existe pas."""
```

Dans un service :

```python
def get_website(self, website_id: int) -> Website:
    website = self.repository.get_by_id(website_id)
    if website is None:
        raise WebsiteNotFoundError("Site introuvable.")
    return website
```

À éviter :

```python
try:
    ...
except Exception:
    pass
```

Une exception ne doit pas masquer une erreur importante.

## 10. Gestion des logs

Les logs doivent aider au diagnostic sans exposer de données sensibles.

Règles :

- ne jamais logger de mot de passe ;
- ne jamais logger de token ;
- ne jamais logger de clé API ;
- inclure un contexte utile ;
- éviter les logs trop verbeux ;
- utiliser le niveau adapté.

Exemple conceptuel :

```python
logger.info("Création d'un site web", extra={"website_id": website.id})
```

À éviter :

```python
logger.info("Token utilisateur: %s", access_token)
```

## 11. Gestion des commentaires

Les commentaires doivent expliquer l'intention, pas répéter le code.

Recommandé :

```python
# Le tri stable garantit un affichage prévisible côté Desktop.
items.sort(key=lambda item: item.name.lower())
```

À éviter :

```python
# On trie les items.
items.sort()
```

Les commentaires doivent rester rares et utiles.

## 12. Gestion des docstrings

Les docstrings sont recommandées pour :

- services publics ;
- fonctions complexes ;
- connecteurs externes ;
- helpers partagés ;
- comportements métier non évidents.

Format recommandé : Google.

Exemple :

```python
def compute_visibility_score(citations: int, total_answers: int) -> float:
    """Calcule un score de visibilité GEO.

    Args:
        citations: Nombre de réponses citant la marque.
        total_answers: Nombre total de réponses analysées.

    Returns:
        Score entre 0 et 1.
    """
    if total_answers == 0:
        return 0.0
    return citations / total_answers
```

## 13. Lisibilité et simplicité du code

Un code lisible doit être préféré à une abstraction trop générale.

Bonnes pratiques :

- une fonction = une responsabilité principale ;
- conditions courtes ;
- variables nommées selon le métier ;
- duplication limitée mais pas d'abstraction prématurée ;
- retours explicites ;
- erreurs traitées au bon niveau.

À éviter :

- fonctions longues ;
- services qui font tout ;
- noms génériques comme `data`, `result`, `obj` sans contexte ;
- conditions imbriquées sur plusieurs niveaux ;
- logique métier cachée dans des helpers obscurs.

## 14. Découpage des responsabilités

Chaque couche a un rôle précis.

| Couche | Responsabilité | Exemple |
| --- | --- | --- |
| Route | HTTP, dépendances, auth, réponse | `GET /websites` |
| Service | règles métier | vérifier unicité d'un domaine |
| Repository | accès aux données | requête SQLAlchemy |
| Model | table et relations | `Website` |
| Schema | validation et sérialisation | `WebsiteCreate` |
| Client API | appel HTTP côté Desktop | `GET /api/v1/websites` |

Une contribution qui mélange ces responsabilités doit être retravaillée.

## 15. Respect de l'architecture `Routes -> Services -> Repositories -> Models`

Architecture obligatoire :

```text
FastAPI Route
     |
     v
Service métier
     |
     v
Repository SQLAlchemy
     |
     v
Model SQLAlchemy
     |
     v
PostgreSQL
```

Le flux inverse remonte les données vers les schémas de sortie API.

Interdictions :

- route qui interroge directement la base ;
- service qui construit une réponse HTTP ;
- repository qui décide d'une règle métier ;
- Desktop qui lit PostgreSQL directement.

## 16. Standards FastAPI

Les routes FastAPI doivent être simples.

Recommandé :

- `APIRouter` par domaine ;
- dépendances déclarées avec `Depends` ;
- schemas Pydantic en entrée et sortie ;
- codes HTTP cohérents ;
- exceptions HTTP construites au niveau route ou via gestionnaire dédié ;
- protection des endpoints sensibles.

Exemple conceptuel :

```python
router = APIRouter(prefix="/websites", tags=["websites"])
```

## 17. Standards pour les routes

Une route doit :

- recevoir la requête ;
- valider les entrées ;
- appeler un service ;
- traduire les erreurs métier en réponse API ;
- retourner un schema de sortie.

Exemple conceptuel acceptable :

```python
@router.get("/{website_id}", response_model=WebsiteRead)
def get_website(
    website_id: int,
    service: WebsiteService = Depends(get_website_service),
) -> WebsiteRead:
    return service.get_website(website_id)
```

À éviter :

```python
@router.get("/{website_id}")
def get_website(website_id: int, db: Session = Depends(get_db)):
    return db.query(Website).filter(Website.id == website_id).first()
```

## 18. Standards pour les dépendances FastAPI

Les dépendances doivent être réutilisables et explicites.

Recommandé :

- dépendance pour la session base ;
- dépendance pour l'utilisateur courant ;
- dépendance pour les permissions ;
- dépendance pour construire un service.

Exemple conceptuel :

```python
def get_website_service(
    db: Session = Depends(get_db),
) -> WebsiteService:
    repository = WebsiteRepository(db)
    return WebsiteService(repository)
```

Les dépendances ne doivent pas contenir de logique métier lourde.

## 19. Standards pour les services

Les services portent la logique métier.

Ils doivent :

- orchestrer plusieurs repositories si nécessaire ;
- vérifier les règles fonctionnelles ;
- rester indépendants de FastAPI autant que possible ;
- retourner des objets ou schemas selon la convention locale ;
- être testables avec Pytest.

Exemple conceptuel :

```python
class WebsiteService:
    def __init__(self, repository: WebsiteRepository) -> None:
        self.repository = repository

    def create_website(self, payload: WebsiteCreate) -> Website:
        existing = self.repository.get_by_domain(payload.domain)
        if existing is not None:
            raise WebsiteAlreadyExistsError("Ce domaine existe déjà.")
        return self.repository.create(payload)
```

## 20. Standards pour les repositories

Les repositories contiennent l'accès aux données SQLAlchemy.

Ils doivent :

- recevoir une session SQLAlchemy ;
- exposer des méthodes nommées clairement ;
- éviter la logique métier ;
- gérer les requêtes, filtres et pagination ;
- ne pas dépendre de FastAPI ;
- ne pas retourner de réponses HTTP.

Exemple conceptuel :

```python
class WebsiteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_domain(self, domain: str) -> Website | None:
        statement = select(Website).where(Website.domain == domain)
        return self.db.scalar(statement)
```

## 21. Standards SQLAlchemy 2.x

Le code SQLAlchemy doit privilégier le style 2.x.

Recommandé :

```python
statement = select(Website).where(Website.is_active.is_(True))
websites = session.scalars(statement).all()
```

À éviter pour les nouveaux développements :

```python
websites = session.query(Website).filter(Website.is_active == True).all()
```

Règles :

- requêtes dans les repositories ;
- transactions explicites lorsque nécessaire ;
- pagination pour les grandes listes ;
- pas de SQL brut sauf justification forte.

## 22. Standards pour les modèles SQLAlchemy

Les modèles représentent les tables.

Ils doivent :

- déclarer clairement les colonnes ;
- utiliser des types adaptés ;
- définir les index et contraintes utiles ;
- rester cohérents avec Alembic ;
- ne pas contenir de logique métier ;
- ne jamais stocker de secret en clair.

Exemple conceptuel :

```python
class Website(Base):
    __tablename__ = "websites"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
```

## 23. Standards pour les relations SQLAlchemy

Les relations doivent être explicites et utiles.

Recommandé :

```python
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    websites: Mapped[list["Website"]] = relationship(back_populates="project")
```

Règles :

- utiliser `back_populates` lorsque la relation est bidirectionnelle ;
- éviter les relations inutilisées ;
- prévoir le comportement de suppression ;
- documenter les cascades risquées ;
- tester les cas métier dépendants des relations.

## 24. Standards pour les requêtes SQLAlchemy

Les requêtes doivent être :

- lisibles ;
- filtrées au plus tôt ;
- paginées si la liste peut grandir ;
- optimisées pour éviter les chargements inutiles ;
- centralisées dans les repositories.

Exemple conceptuel :

```python
def list_active(self, limit: int, offset: int) -> list[Website]:
    statement = (
        select(Website)
        .where(Website.is_active.is_(True))
        .order_by(Website.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(self.db.scalars(statement))
```

## 25. Standards Pydantic v2

Les schemas Pydantic v2 gèrent la validation et la sérialisation API.

Recommandé :

- schemas séparés pour création, mise à jour et lecture ;
- types explicites ;
- champs optionnels uniquement si nécessaire ;
- validations locales et compréhensibles ;
- pas d'exposition de champs sensibles.

Exemple de familles :

```text
WebsiteCreate
WebsiteUpdate
WebsiteRead
WebsiteListItem
```

## 26. Standards pour les schémas d'entrée

Les schémas d'entrée doivent valider ce que l'utilisateur peut envoyer.

Exemple conceptuel :

```python
class WebsiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    domain: str = Field(min_length=3, max_length=255)
```

Règles :

- ne pas inclure d'id généré par la base ;
- ne pas accepter de champs internes ;
- contraindre les longueurs ;
- valider les formats importants ;
- documenter les champs ambigus.

## 27. Standards pour les schémas de sortie

Les schémas de sortie doivent exposer uniquement ce qui est nécessaire.

Exemple conceptuel :

```python
class WebsiteRead(BaseModel):
    id: int
    name: str
    domain: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
```

Règles :

- ne pas exposer de secret ;
- éviter les champs internes ;
- prévoir des schemas résumés pour les listes ;
- garder les réponses stables pour Desktop et futur React.

## 28. Standards pour les validateurs Pydantic

Les validateurs doivent rester ciblés.

Exemple conceptuel :

```python
class WebsiteCreate(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        return value.strip().lower()
```

Règles :

- valider les formats simples dans Pydantic ;
- garder les règles métier dans les services ;
- éviter les appels base dans les validateurs ;
- tester les validations importantes.

## 29. Standards Alembic

Alembic est obligatoire pour les modifications de structure PostgreSQL.

Une migration doit :

- être explicite ;
- être relisible ;
- correspondre aux modèles SQLAlchemy ;
- gérer les données existantes si nécessaire ;
- être testée ou vérifiée ;
- éviter les opérations destructrices non validées.

Commandes utiles :

```powershell
alembic current
alembic history
alembic upgrade head
```

## 30. Règles pour les migrations explicites

Une migration explicite indique précisément ce qui change.

Exemple conceptuel :

```python
def upgrade() -> None:
    op.add_column("websites", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_websites_is_active", "websites", ["is_active"])
```

Règles :

- nommer les contraintes ;
- prévoir les valeurs par défaut ;
- éviter les suppressions silencieuses ;
- documenter les opérations sensibles dans la PR.

## 31. Interdiction de `Base.metadata.create_all()` dans les migrations

Interdit :

```python
Base.metadata.create_all(bind=engine)
```

Raison :

- contourne Alembic ;
- rend l'historique non fiable ;
- masque les changements précis ;
- complique les environnements existants.

Les migrations doivent utiliser `op.create_table`, `op.add_column`, `op.create_index` et les opérations Alembic adaptées.

## 32. Interdiction de `Base.metadata.drop_all()` dans les migrations

Interdit :

```python
Base.metadata.drop_all(bind=engine)
```

Raison :

- risque de suppression massive ;
- perte potentielle de données ;
- comportement non acceptable en production ;
- absence de contrôle fin.

Toute suppression de table, colonne ou contrainte doit être explicitement validée.

## 33. Standards PostgreSQL

PostgreSQL est la base de données cible.

Standards :

- types adaptés au besoin ;
- contraintes explicites ;
- index sur les champs de recherche fréquents ;
- pagination pour les listes ;
- cohérence entre modèles et migrations ;
- attention aux suppressions ;
- pas de dépendance à SQLite pour la logique métier.

Les tests peuvent utiliser un environnement adapté, mais le comportement attendu doit rester compatible PostgreSQL.

## 34. Standards pour les index

Un index doit répondre à un besoin.

Cas recommandés :

- champ filtré souvent ;
- champ trié souvent ;
- clé étrangère utilisée en jointure ;
- champ unique métier ;
- recherche fréquente par statut ou date.

Exemple conceptuel :

```python
op.create_index("ix_websites_domain", "websites", ["domain"], unique=True)
```

À éviter :

- indexer tous les champs ;
- créer des index non utilisés ;
- oublier l'impact des index sur les écritures.

## 35. Standards pour les contraintes

Les contraintes protègent l'intégrité des données.

Types fréquents :

| Contrainte | Usage |
| --- | --- |
| `unique` | éviter les doublons |
| `nullable=False` | champ obligatoire |
| clé étrangère | relation entre tables |
| check constraint | règle simple côté base |

Les règles métier complexes doivent rester dans les services, avec appui de contraintes base si pertinent.

## 36. Standards pour les suppressions contrôlées

Une suppression doit être pensée.

Questions à poser :

- suppression physique ou désactivation ?
- impact sur les relations ?
- données historiques à conserver ?
- droits nécessaires ?
- audit nécessaire ?

Recommandé pour les entités métier sensibles :

```text
préférer une désactivation logique lorsque l'historique doit être conservé.
```

Une suppression destructive doit être validée explicitement.

## 37. Standards pour les imports/exports de configuration

Les imports et exports de configuration doivent être prudents.

Règles :

- non destructifs autant que possible ;
- idempotents autant que possible ;
- validés avant application ;
- journalisés sans secret ;
- capables de signaler les doublons ;
- testés sur les cas d'erreur.

Un import idempotent peut être relancé sans créer de doublons ni supprimer des données utiles.

## 38. Standards API REST

L'API REST doit être prévisible.

Standards :

- ressources nommées au pluriel lorsque pertinent ;
- méthodes HTTP cohérentes ;
- codes HTTP adaptés ;
- payloads Pydantic ;
- erreurs structurées ;
- pagination pour listes ;
- filtrage documenté ;
- auth sur endpoints sensibles.

Exemples de méthodes :

| Méthode | Usage |
| --- | --- |
| `GET` | lire |
| `POST` | créer ou déclencher une action |
| `PUT` | remplacer |
| `PATCH` | modifier partiellement |
| `DELETE` | supprimer ou désactiver |

## 39. Standards d'authentification et autorisation

Les endpoints sensibles doivent être protégés.

Règles :

- authentifier l'utilisateur ;
- vérifier les droits ;
- limiter les accès par rôle ou permission ;
- ne pas exposer les détails internes ;
- tester les cas refusés ;
- documenter les endpoints sensibles.

Exemple conceptuel :

```python
@router.get("/admin/settings")
def list_settings(
    current_user: User = Depends(require_permission("settings:read")),
) -> list[SettingRead]:
    ...
```

## 40. Standards de gestion des erreurs API

Les erreurs API doivent être claires sans révéler de secret.

Recommandé :

```json
{
  "detail": "Site introuvable."
}
```

À éviter :

```json
{
  "detail": "Database password failed for user admin..."
}
```

Règles :

- codes HTTP cohérents ;
- messages utiles mais sobres ;
- pas de stack trace en réponse ;
- erreurs métier traduites proprement ;
- logs internes sans secret.

## 41. Standards de pagination

Les listes potentiellement longues doivent être paginées.

Paramètres fréquents :

```text
page
page_size
limit
offset
```

Règles :

- taille par défaut raisonnable ;
- taille maximale ;
- total si nécessaire ;
- ordre stable ;
- tests sur limites.

Exemple conceptuel :

```python
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
```

## 42. Standards de filtrage

Le filtrage doit être explicite et sécurisé.

Règles :

- whitelist des champs filtrables ;
- validation Pydantic ;
- pas d'injection SQL ;
- requêtes construites via SQLAlchemy ;
- comportement documenté ;
- tests des filtres critiques.

Exemple conceptuel :

```python
if filters.status is not None:
    statement = statement.where(Website.status == filters.status)
```

## 43. Standards de sécurité applicative

Standards obligatoires :

- validation des entrées ;
- auth sur endpoints sensibles ;
- permissions adaptées ;
- pas de secrets dans Git ;
- pas de secrets dans les logs ;
- pas d'erreurs trop détaillées côté API ;
- dépendances ajoutées uniquement avec justification ;
- configuration via environnement.

Avant toute Pull Request :

```powershell
git diff
git diff --cached
git diff --check
```

## 44. Données sensibles à ne jamais exposer

Données interdites dans le code, les logs, les réponses API et les commits :

| Donnée | Exemple |
| --- | --- |
| Mot de passe | `password=...` |
| Token | JWT, token API |
| Clé API | OpenAI, Google, services tiers |
| Secret applicatif | clé de signature |
| `.env` | variables locales |
| Connexion DB | URL complète avec mot de passe |
| Données personnelles non nécessaires | email ou identifiant exposé sans besoin |

Si un secret est exposé, il doit être considéré comme compromis.

## 45. Standards Desktop PySide6

Le Desktop doit rester un client de l'API.

Standards :

- composants PySide6 lisibles ;
- séparation pages, widgets et core ;
- styles centralisés en QSS si possible ;
- erreurs utilisateur claires ;
- appels API centralisés ;
- pas d'accès PostgreSQL direct ;
- pas de logique métier principale.

Organisation existante à respecter :

```text
desktop/ui/
desktop/widgets/
desktop/core/
desktop/styles/
```

## 46. Standards pour les appels HTTP avec `httpx`

Les appels HTTP Desktop doivent passer par `httpx` dans le client API prévu.

Exemple conceptuel :

```python
class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_websites(self) -> list[dict[str, object]]:
        response = httpx.get(f"{self.base_url}/api/v1/websites", timeout=10.0)
        response.raise_for_status()
        return response.json()
```

Règles :

- timeouts explicites ;
- erreurs réseau gérées ;
- auth centralisée ;
- pas de token dans les logs ;
- pas d'appels API dispersés dans toutes les pages.

## 47. Règles d'interdiction d'accès direct Desktop vers PostgreSQL

Interdit côté Desktop :

```python
engine = create_engine(database_url)
```

Raison :

- contourne l'API ;
- duplique les règles métier ;
- contourne l'authentification ;
- expose potentiellement les secrets ;
- complique les évolutions React futures.

Le seul chemin autorisé :

```text
Desktop PySide6 -> HTTP REST -> FastAPI -> Services -> Repositories -> PostgreSQL
```

## 48. Standards UI Desktop généraux

L'interface Desktop doit rester cohérente.

Standards :

- libellés clairs ;
- états d'erreur visibles ;
- chargements non bloquants lorsque nécessaire ;
- composants réutilisables ;
- style cohérent avec le thème existant ;
- pas de logique métier cachée dans les widgets ;
- comportement testable manuellement.

Validation recommandée :

```powershell
python desktop/main.py
ruff check desktop
```

## 49. Standards pour la future intégration React

React est prévu plus tard.

Standards à prévoir :

- React ;
- TypeScript ;
- Vite ;
- Tailwind CSS ;
- services API côté frontend ;
- types partagés ou générés à valider ;
- composants réutilisables ;
- pas de duplication des règles métier backend.

À ne pas faire avant validation :

- créer une architecture React complète ;
- ajouter des dépendances frontend ;
- déplacer les responsabilités backend vers le frontend ;
- coupler l'API au Desktop uniquement.

## 50. Standards de tests Pytest

Les tests doivent vérifier les comportements importants.

Standards :

- tests déterministes ;
- noms explicites ;
- fixtures réutilisables ;
- cas d'erreur couverts ;
- pas d'appel réseau réel non contrôlé ;
- tests proches du domaine testé.

Commande globale :

```powershell
pytest
```

## 51. Standards de nommage des tests

Conventions :

| Élément | Convention | Exemple |
| --- | --- | --- |
| Fichier | `test_*.py` | `test_websites_services.py` |
| Fonction | `test_*` | `test_create_website_rejects_duplicate_domain` |
| Fixture | nom métier | `website_repository` |
| Classe de test | facultative | `TestWebsiteService` |

Un nom de test doit décrire le comportement attendu.

## 52. Standards de tests routes

Les tests de routes doivent vérifier :

- code HTTP ;
- payload de réponse ;
- validation d'entrée ;
- auth et permissions ;
- erreurs métier ;
- pagination et filtrage si concernés.

Exemple conceptuel :

```python
def test_get_website_returns_404_when_missing(client):
    response = client.get("/api/v1/websites/999")

    assert response.status_code == 404
```

## 53. Standards de tests services

Les tests de services doivent vérifier la logique métier.

Exemple conceptuel :

```python
def test_create_website_rejects_duplicate_domain(service, repository):
    repository.add_domain("example.com")

    with pytest.raises(WebsiteAlreadyExistsError):
        service.create_website(WebsiteCreate(name="Example", domain="example.com"))
```

Règles :

- tester les règles positives et négatives ;
- éviter de tester FastAPI dans les tests services ;
- utiliser des doubles ou fixtures si pertinent.

## 54. Standards de tests repositories

Les tests repositories doivent vérifier l'accès aux données lorsque nécessaire.

À tester :

- création ;
- lecture ;
- filtrage ;
- pagination ;
- contraintes ;
- relations importantes.

Exemple conceptuel :

```python
def test_get_by_domain_returns_matching_website(repository):
    website = repository.create(domain="example.com")

    assert repository.get_by_domain("example.com") == website
```

## 55. Standards de tests Desktop

Les tests Desktop peuvent être progressifs.

À prévoir :

- tests des helpers ;
- tests du client API avec réponses simulées ;
- validation manuelle des écrans ;
- absence d'accès direct base ;
- gestion des erreurs HTTP.

Exemple conceptuel :

```python
def test_api_client_raises_on_server_error(mock_httpx):
    ...
```

L'automatisation UI complète est à valider lors de l'implémentation.

## 56. Standards Ruff

Ruff est l'outil de linting Python du projet.

Standards :

- corriger les erreurs Ruff ;
- éviter les exceptions de lint sans justification ;
- ne pas reformater massivement hors périmètre ;
- lancer Ruff sur le périmètre modifié ;
- lancer Ruff globalement avant une PR importante.

Ruff ne remplace pas la revue de code.

## 57. Commandes de linting recommandées

Commandes PowerShell :

```powershell
ruff check .
ruff check backend
ruff check desktop
ruff check tests
ruff check backend tests
```

Si une commande échoue :

- lire l'erreur ;
- corriger dans le périmètre ;
- relancer la commande ;
- documenter le blocage si la correction sort du périmètre.

## 58. Commandes de tests recommandées

Commandes PowerShell :

```powershell
pytest
pytest tests/services
pytest tests/api
pytest tests/services/test_websites_services.py
pytest tests/api/test_websites_routes.py
```

Pour une modification documentaire :

```powershell
git diff --check
```

Pour une modification Desktop :

```powershell
python desktop/main.py
ruff check desktop
```

## 59. Standards de documentation technique

La documentation technique doit :

- être en français ;
- expliquer le contexte ;
- donner les commandes utiles ;
- préciser les prérequis ;
- indiquer les risques ;
- rester cohérente avec le code existant ;
- éviter les promesses non implémentées.

Un document technique doit aider un contributeur à agir correctement.

## 60. Standards Markdown

Standards Markdown :

- titres hiérarchisés ;
- listes courtes ;
- tableaux pour comparer ;
- blocs de code avec langage ;
- chemins entourés de backticks ;
- liens vers documents liés ;
- pas de mise en forme décorative inutile.

Exemple :

```markdown
## Titre

Commande :

```powershell
git status --short
```
```

## 61. Standards pour les exemples de code dans la documentation

Les exemples de code doivent être conceptuels lorsqu'ils ne correspondent pas à un fichier existant.

Formulations recommandées :

- "Exemple conceptuel" ;
- "Recommandé" ;
- "À prévoir" ;
- "À valider lors de l'implémentation".

Un exemple ne doit pas faire croire qu'une classe, fonction ou route existe déjà si ce n'est pas le cas.

## 62. Standards pour les prompts Codex

Un prompt Codex doit préciser :

- branche obligatoire ;
- fichiers autorisés ;
- fichiers interdits ;
- commandes préalables ;
- périmètre exact ;
- interdiction de commit ;
- interdiction de push ;
- validations attendues ;
- format du compte rendu.

Exemple :

```text
Crée uniquement docs/development/CODING_STANDARDS.md.
Ne modifie pas les autres fichiers.
Vérifie git branch --show-current et git status --short avant modification.
N'exécute pas git add, git commit ou git push.
```

## 63. Ce que Codex peut modifier

Codex peut modifier uniquement :

- les fichiers explicitement demandés ;
- les fichiers explicitement autorisés ;
- les tests associés lorsque la demande les inclut ;
- la documentation associée lorsque la demande le prévoit.

Codex peut aussi :

- analyser l'existant ;
- signaler les anomalies ;
- exécuter les vérifications ;
- produire un rapport final.

## 64. Ce que Codex ne doit pas modifier sans validation

Codex ne doit pas modifier sans validation :

- fichiers hors périmètre ;
- architecture globale ;
- dépendances ;
- migrations destructrices ;
- fichiers déjà indexés par l'utilisateur ;
- fichiers de configuration sensibles ;
- `.env` ;
- secrets ;
- noms ou emplacements de fichiers existants.

Codex ne doit pas supprimer, renommer, refactorer globalement, commiter ou pousser sans demande explicite.

## 65. Exemples de code acceptables

Route fine :

```python
@router.post("/", response_model=WebsiteRead)
def create_website(
    payload: WebsiteCreate,
    service: WebsiteService = Depends(get_website_service),
) -> WebsiteRead:
    return service.create_website(payload)
```

Service métier :

```python
def create_website(self, payload: WebsiteCreate) -> Website:
    if self.repository.get_by_domain(payload.domain) is not None:
        raise WebsiteAlreadyExistsError("Ce domaine existe déjà.")
    return self.repository.create(payload)
```

Repository SQLAlchemy :

```python
def get_by_domain(self, domain: str) -> Website | None:
    statement = select(Website).where(Website.domain == domain)
    return self.db.scalar(statement)
```

## 66. Exemples de code à éviter

Logique métier dans une route :

```python
@router.post("/")
def create_website(payload: WebsiteCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Website).where(Website.domain == payload.domain))
    if existing:
        raise HTTPException(status_code=409, detail="Existe déjà")
    ...
```

Accès direct Desktop vers PostgreSQL :

```python
engine = create_engine("postgresql://user:password@localhost/db")
```

Migration dangereuse :

```python
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
```

Ces exemples doivent être refusés.

## 67. Exemples d'architecture correcte

Exemple conceptuel :

```text
desktop/ui/websites_page.py
    appelle
desktop/core/api_client.py
    appelle HTTP
backend/app/api/v1/routes/websites.py
    appelle
backend/app/services/websites.py
    appelle
backend/app/repositories/websites.py
    utilise
backend/app/models/...
```

Cette architecture protège les règles métier et prépare la future intégration React.

## 68. Exemples d'architecture incorrecte

Architecture incorrecte :

```text
desktop/ui/websites_page.py
    se connecte directement à PostgreSQL
```

Architecture incorrecte :

```text
backend/app/api/v1/routes/websites.py
    contient les requêtes SQLAlchemy
    applique toutes les règles métier
```

Architecture incorrecte :

```text
backend/app/repositories/websites.py
    décide des permissions utilisateur
```

Ces découpages doivent être corrigés avant acceptation.

## 69. Cas fréquents de dette technique

Dette technique fréquente :

| Cas | Risque | Action recommandée |
| --- | --- | --- |
| Route trop longue | logique métier cachée | déplacer vers service |
| Repository métier | règles difficiles à tester | déplacer vers service |
| Schema trop large | fuite de champs | créer un schema de sortie dédié |
| Migration implicite | historique fragile | écrire Alembic explicite |
| Tests absents | régression invisible | ajouter tests ciblés |
| Appels API dispersés | maintenance difficile | centraliser client API |
| Refactor opportuniste | PR trop large | isoler dans une branche dédiée |

## 70. Refactor : règles et limites

Un refactor doit être :

- validé explicitement ;
- limité ;
- motivé ;
- testé ;
- séparé d'une fonctionnalité si possible ;
- documenté dans la Pull Request.

Un refactor ne doit pas :

- changer le comportement sans le dire ;
- renommer massivement ;
- déplacer des fichiers sans validation ;
- masquer une correction métier ;
- s'étendre à tout le dépôt.

## 71. Checklist avant modification

- [ ] Branche active vérifiée.
- [ ] Branche active différente de `main`.
- [ ] `git status --short` relu.
- [ ] Fichiers déjà indexés identifiés.
- [ ] Périmètre confirmé.
- [ ] Architecture concernée comprise.
- [ ] Tests utiles identifiés.
- [ ] Risques de sécurité vérifiés.
- [ ] Fichiers à ne pas modifier identifiés.

Commandes :

```powershell
git branch --show-current
git status --short
```

## 72. Checklist avant commit

- [ ] Diff relu.
- [ ] Diff indexé relu.
- [ ] Aucun secret.
- [ ] Aucun fichier temporaire.
- [ ] Aucun changement hors périmètre.
- [ ] Ruff exécuté si Python modifié.
- [ ] Pytest exécuté si comportement modifié.
- [ ] `git diff --check` sans erreur.
- [ ] Message de commit clair.

Commandes :

```powershell
git status --short
git diff
git diff --cached
git diff --check
```

## 73. Checklist de revue de code

Le relecteur vérifie :

- séparation des couches ;
- absence de logique métier dans les routes ;
- repositories limités aux données ;
- schemas Pydantic adaptés ;
- migrations Alembic explicites ;
- sécurité des endpoints ;
- absence de secrets ;
- tests suffisants ;
- documentation à jour ;
- pas de refactor non demandé.

Une revue doit être concrète et actionnable.

## 74. Critères d'acceptation

Une contribution respecte les standards si :

- elle répond au besoin ;
- elle préserve l'architecture ;
- elle est lisible ;
- elle est testable ;
- elle ne contient pas de secret ;
- elle ne modifie pas de fichiers hors périmètre ;
- elle passe les vérifications utiles ;
- elle ne crée pas de dette technique évidente ;
- elle est documentée lorsque nécessaire.

## 75. Points à éviter

À éviter systématiquement :

- logique métier dans les routes ;
- accès Desktop direct à PostgreSQL ;
- SQL brut sans justification ;
- migrations avec `Base.metadata.create_all()` ;
- migrations avec `Base.metadata.drop_all()` ;
- secrets dans Git ;
- `.env` dans Git ;
- fonctions trop longues ;
- fichiers trop volumineux ;
- dépendances ajoutées sans justification ;
- refactor global non validé ;
- tests ignorés ;
- documentation trompeuse.

## 76. Liens avec les documents

Documents liés :

| Document | Rôle |
| --- | --- |
| `docs/development/Git_Workflow.md` | workflow Git officiel |
| `docs/development/CONTRIBUTING.md` | règles de contribution |
| `docs/development/BACKEND_DEVELOPMENT_GUIDE.md` | guide backend futur |
| `docs/development/DESKTOP_DEVELOPMENT_GUIDE.md` | guide Desktop futur |
| `docs/development/TESTING.md` | guide tests futur |
| `docs/api/AUTHENTICATION.md` | authentification API |
| `docs/api/ERROR_HANDLING.md` | erreurs API |
| `docs/api/PAGINATION.md` | pagination API |
| `docs/api/FILTERING.md` | filtrage API |

Les guides futurs préciseront les règles opérationnelles détaillées par domaine.

## Matrice de responsabilité entre couches

| Responsabilité | Routes | Services | Repositories | Modèles | Schémas | Clients API |
| --- | --- | --- | --- | --- | --- | --- |
| Recevoir une requête HTTP | Oui | Non | Non | Non | Non | Côté client uniquement |
| Appliquer la logique métier | Non | Oui | Non | Non | Non | Non |
| Accéder à SQLAlchemy | Non | Via repository | Oui | Définition table | Non | Non |
| Représenter les tables | Non | Non | Non | Oui | Non | Non |
| Valider les payloads API | Déclenche | Non | Non | Non | Oui | Peut valider côté UI |
| Gérer les permissions | Dépendances | Règles métier si besoin | Non | Non | Non | Non |
| Appeler l'API REST | Non | Non | Non | Non | Non | Oui |
| Accéder à PostgreSQL | Non | Non direct | Oui | Mapping | Non | Non |

## Matrice de conformité par couche technique

| Couche | Conforme | Non conforme | Validation |
| --- | --- | --- | --- |
| FastAPI routes | route courte appelant un service | requête SQL dans la route | revue + tests API |
| Services | règle métier testée | logique HTTP détaillée | tests services |
| Repositories | requête SQLAlchemy claire | décision métier | tests données |
| Models | colonnes et relations | règles métier complexes | migration + revue |
| Pydantic | schema précis | exposition de secret | tests API |
| Alembic | opérations explicites | `create_all` ou `drop_all` | upgrade local |
| Desktop | HTTP REST via client | connexion PostgreSQL directe | lancement manuel |
| Tests | cas métier clairs | tests fragiles d'implémentation | Pytest |
| Documentation | exemples conceptuels signalés | promesse d'une feature absente | revue documentaire |

## Diagramme ASCII de l'architecture backend

```text
Client Desktop / Futur React
          |
          | HTTP REST
          v
   Routes FastAPI
          |
          | appels de services
          v
   Services métier
          |
          | appels repositories
          v
   Repositories SQLAlchemy
          |
          | utilisent les modèles
          v
   Models SQLAlchemy
          |
          | mapping
          v
   PostgreSQL
```

## Commandes PowerShell de référence

Vérifier avant modification :

```powershell
git branch --show-current
git status --short
```

Linting :

```powershell
ruff check .
ruff check backend desktop tests
```

Tests :

```powershell
pytest
pytest tests/services
pytest tests/api
```

Diff et sécurité :

```powershell
git diff
git diff --cached
git diff --check
```

Validation documentaire :

```powershell
git diff -- docs/development
git diff --check
```

## Section de prudence

Les standards de code ne justifient jamais une commande destructive sans validation explicite.

Commandes à ne pas utiliser sans accord clair :

```powershell
git reset --hard
git clean -fd
git push --force
```

Avant toute action risquée :

```powershell
git status --short
git diff
git diff --cached
```

En cas d'incertitude, arrêter la modification et demander confirmation.
