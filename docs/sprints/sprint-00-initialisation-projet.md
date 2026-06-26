# Sprint 00 — Initialisation du projet

**Statut :** À réaliser

**Objectif**

Mettre en place les fondations techniques du projet afin que tous les développements futurs reposent sur une architecture propre, documentée et reproductible.

Aucune logique métier ne doit être développée durant ce sprint.

---

# Livrables attendus

## Backend

- Initialiser un projet FastAPI.
- Mettre en place une architecture modulaire.
- Créer une factory `create_app()`.
- Ajouter un endpoint de santé :

```
GET /api/v1/health
```

Réponse attendue :

```json
{
    "status": "ok"
}
```

---

## Base de données

Préparer l'intégration PostgreSQL.

Créer :

- SQLAlchemy
- Session database
- Base déclarative
- Configuration Alembic

Aucune table métier ne doit être créée.

---

## Configuration

Mettre en place :

- variables d'environnement
- fichier `.env.example`
- configuration Pydantic Settings
- mode Debug
- URL PostgreSQL configurable

---

## Qualité de code

Configurer :

- Black
- Ruff
- Pytest

Le projet doit être exécutable sans avertissement majeur.

---

## Structure du projet

Créer l'arborescence suivante :

```
backend/
    app/
        api/
        core/
        db/
        models/
        services/
        schemas/

frontend/

database/

scripts/

tests/
```

---

## Docker

Préparer :

- Dockerfile backend
- docker-compose.yml
- PostgreSQL
- API

Le simple lancement de la stack doit fonctionner.

---

## Documentation

Mettre à jour :

- README.md
- ARCHITECTURE.md

Documenter :

- installation
- lancement
- structure
- dépendances

---

# Hors périmètre

Ne pas développer :

- recherche Google
- scraping
- IA
- interface utilisateur
- authentification
- modèles métier
- API fonctionnelles

---

# Critères d'acceptation

Le sprint est considéré terminé si :

- le projet démarre avec `uvicorn`
- `/api/v1/health` répond correctement
- PostgreSQL est prêt à être utilisé
- Alembic fonctionne
- Docker démarre sans erreur
- les tests passent
- la documentation est à jour

---

# Résultat attendu

À la fin du Sprint 00, le projet dispose d'une base technique propre, documentée et prête à accueillir les développements fonctionnels des prochains sprints.

Aucun développement métier n'est attendu à ce stade.