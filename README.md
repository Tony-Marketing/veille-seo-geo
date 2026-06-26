# Veille SEO-GEO Groupe A.P&Partner

Plateforme interne de pilotage SEO, GEO (Generative Engine Optimization), analyse technique et veille concurrentielle destinée aux différentes entités du Groupe A.P&Partner.

---

# Présentation

Veille SEO-GEO Groupe A.P&Partner est une application web développée en Python permettant de centraliser l'ensemble des données SEO, techniques, éditoriales et liées à la visibilité des marques dans les moteurs d'IA générative.

L'objectif est de fournir une plateforme unique pour :

- suivre les performances SEO
- mesurer la visibilité dans ChatGPT, Gemini, Claude, Perplexity…
- analyser la qualité technique des sites
- gérer les contenus
- suivre les concurrents
- planifier les actions marketing
- automatiser certaines tâches
- générer des rapports décisionnels

---

# Entités suivies

- Europ-Arm
- SIMAC
- Sport-Attitude
- Armurerie Gilles
- Armurerie Auxerre
- Western Guns
- Armurerie Riffaut
- Blog Armurerie France

Chaque entité possède ses propres :

- sites
- mots-clés
- URLs
- concurrents
- contenus
- paramètres
- historiques
- tableaux de bord

---

# Architecture

Le projet est organisé autour d'une architecture modulaire.

```
backend/
    API FastAPI
    Services métier
    Modules SEO
    Modules GEO
    Connecteurs API

frontend/
    Interface utilisateur

database/
    Schéma SQL
    Migrations
    Jeux de données

docs/
    Documentation fonctionnelle
    Documentation technique

scripts/
    Scripts utilitaires

tests/
    Tests unitaires
    Tests d'intégration
```

---

# Technologies

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

## Base de données

- PostgreSQL

## Authentification

- JWT

## Tâches planifiées

- APScheduler
ou
- Celery + Redis

---

# Modules principaux

## Tableau de bord

- KPI SEO
- KPI GEO
- KPI techniques
- Evolution mensuelle
- Statistiques par entité

---

## Marché

- Analyse sectorielle
- Tendances SEO
- Analyse concurrentielle
- Opportunités éditoriales

---

## Analyse SEO

- Audit des balises
- Analyse des URLs
- Détection des erreurs
- Recommandations

---

## Analyse GEO

- Gestion des prompts
- Analyse ChatGPT
- Analyse Gemini
- Analyse Claude
- Analyse Perplexity
- Suivi des citations
- Score GEO

---

## Mots-clés

- Import
- Export
- Historique
- Priorisation
- Performances

---

## URLs

- Audit
- Statuts HTTP
- Temps de réponse
- Détection des erreurs

---

## Planning

- Calendrier éditorial
- Gestion des publications
- Gestion des campagnes

---

## Projet

- Gestion des tâches
- Affectation
- Priorités
- Historique

---

## Automatisation

- WordPress
- YouTube
- Newsletters
- Rapports automatiques

---

## Administration

- Gestion des utilisateurs
- Gestion des rôles
- Gestion des API
- Paramètres
- Journalisation

---

# APIs prévues

## Google

- Search Console
- Analytics 4
- PageSpeed
- Indexing API
- Business Profile

## SEO

- Semrush
- Ahrefs
- Monitorank
- DataForSEO

## IA

- OpenAI
- Gemini
- Claude
- Mistral
- Perplexity

## CMS

- WordPress
- Prestashop
- Shopify
- WooCommerce

---

# Installation

```bash
git clone git@github.com:Tony-Marketing/Veille-SEO-GEO-Groupe-AP-Partners.git

cd Veille-SEO-GEO-Groupe-AP-Partners
```

Créer ensuite l'environnement virtuel.

```bash
python -m venv .venv
```

Activation Windows

```bash
.venv\Scripts\activate
```

Installation des dépendances

```bash
pip install -r requirements.txt
```

---

# Lancement

Backend

```bash
uvicorn app.main:app --reload
```

Frontend

```bash
npm install

npm run dev
```

---

# Feuille de route

## Version 1.0

- Authentification
- Gestion des entités
- Tableau de bord
- Import mots-clés
- Import URLs
- Audit SEO
- Audit technique

## Version 1.1

- Historique SEO
- Graphiques
- Analyse concurrentielle

## Version 1.2

- GEO
- IA
- Prompts
- Visibilité

## Version 1.3

- Planning
- Gestion de projet

## Version 1.4

- Automatisation
- WordPress
- Reporting

## Version 1.5

- Administration avancée

---

# Licence

Projet privé.

© Groupe A.P&Partner.

Tous droits réservés.

---

# Auteur

Anthony Couty

GitHub

https://github.com/Tony-Marketing

---

# Statut

Projet actuellement en développement.