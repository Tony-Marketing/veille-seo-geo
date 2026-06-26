# Sprint 06 — Interface d'administration Backend

## Objectifs

Le Sprint 06 a pour objectif de mettre en place l'ensemble des fonctionnalités d'administration de la plateforme **Veille SEO-GEO Groupe A.P&Partner**.

Cette interface constitue le centre de pilotage du backend et permet de gérer les paramètres techniques de l'application sans intervention directe dans la base de données.

À l'issue de ce sprint, un administrateur doit pouvoir configurer l'application, gérer les accès, les fournisseurs d'IA, les clés API et consulter l'état général de la plateforme.

---

# Objectifs fonctionnels

Le sprint couvre les domaines suivants :

* Tableau de bord d'administration
* Paramètres globaux
* Gestion des fournisseurs IA
* Gestion des clés API
* Gestion des rôles
* Journalisation
* Santé des services
* Paramètres SEO/GEO globaux

---

# Fonctionnalités

## 1. Dashboard Administrateur

Création d'un tableau de bord affichant :

* nombre de sites enregistrés
* nombre d'utilisateurs
* nombre de fournisseurs IA actifs
* nombre de clés API configurées
* état de la connexion PostgreSQL
* version de l'application
* version de la base
* environnement (Development / Test / Production)
* date de démarrage de l'application
* uptime
* nombre de migrations Alembic appliquées

---

## 2. Paramètres globaux

Création d'un module de configuration générale.

Exemples :

Nom de l'application

```
Veille SEO-GEO Groupe A.P&Partner
```

Version

Fuseau horaire

Langue

URL de base

Répertoire des exports

Répertoire des sauvegardes

Nombre maximum de tâches simultanées

Durée de conservation des journaux

Mode Debug

Activation Swagger

Activation ReDoc

Maintenance

---

## 3. Gestion des fournisseurs IA

Création d'un module permettant de gérer tous les fournisseurs d'IA.

Exemple :

| Fournisseur   | Actif |
| ------------- | ----- |
| OpenAI        | Oui   |
| Anthropic     | Oui   |
| Google Gemini | Oui   |
| Mistral       | Oui   |
| xAI           | Oui   |
| Perplexity    | Oui   |
| DeepSeek      | Oui   |
| Ollama        | Oui   |

Pour chaque fournisseur :

* nom
* description
* site web
* documentation
* modèle par défaut
* timeout
* nombre maximal de requêtes simultanées
* actif / inactif

---

## 4. Gestion des modèles IA

Pour chaque fournisseur :

liste des modèles disponibles.

Exemple OpenAI

* GPT-5.5
* GPT-5.5 Thinking
* GPT-4.1
* GPT-4o

Exemple Gemini

* Gemini 2.5 Pro
* Gemini 2.5 Flash

Chaque modèle possède :

* nom
* identifiant API
* coût entrée
* coût sortie
* contexte maximal
* actif

---

## 5. Gestion des clés API

Module sécurisé permettant de stocker toutes les clés API utilisées par la plateforme.

Exemples :

OpenAI

Anthropic

Google

Google Search Console

Google Analytics

Perplexity

GitHub

DataForSEO

SE Ranking

SerpAPI

Proxy

SMTP

Chaque clé contient :

* nom
* fournisseur
* valeur (chiffrée)
* date d'ajout
* date de modification
* dernière utilisation
* utilisateur créateur
* utilisateur modificateur
* statut actif

Les clés ne doivent jamais être renvoyées en clair par les API.

---

## 6. Gestion des rôles

CRUD complet des rôles.

Exemples :

Administrateur

SEO

Marketing

Développeur

Rédacteur

Consultation

Chaque rôle possède des permissions.

---

## 7. Gestion des permissions

Liste complète des permissions.

Exemples

```
website.read
website.write
website.delete

user.read
user.write

admin.read
admin.write

ai.read
ai.write

apikey.read
apikey.write

settings.read
settings.write

logs.read
```

Association N:N entre rôles et permissions.

---

## 8. Journal des événements

Historique des actions réalisées dans l'application.

Pour chaque événement :

* utilisateur
* date
* module
* action
* adresse IP
* navigateur
* résultat
* durée
* informations complémentaires

Filtres :

* utilisateur
* module
* date
* niveau
* action

---

## 9. Journal des erreurs

Consultation des erreurs applicatives.

Informations :

* exception
* traceback
* endpoint
* utilisateur
* date
* environnement
* niveau
* résolu
* commentaire

---

## 10. Santé des services

Endpoint permettant de vérifier :

* PostgreSQL
* Redis
* API OpenAI
* API Anthropic
* API Gemini
* API GitHub
* espace disque
* mémoire
* CPU

Statuts :

```
Healthy

Warning

Critical
```

---

## 11. Paramètres SEO/GEO

Configuration globale.

Exemples

Temps maximal d'analyse

Nombre maximal de pages crawlées

User-Agent du crawler

Robots.txt

Respect Crawl Delay

Nombre de threads

Timeout HTTP

Retry

Proxy

Rotation User-Agent

---

## 12. Paramètres IA

Configuration globale.

Exemples

Fournisseur par défaut

Modèle par défaut

Température

Top P

Top K

Max Tokens

Timeout

Nombre maximal de requêtes simultanées

Retry

Backoff

Streaming

---

## 13. Sauvegarde de la configuration

Export de toute la configuration :

```
JSON

YAML
```

Import d'une configuration existante.

---

## 14. Documentation OpenAPI

Tous les endpoints doivent être documentés.

Utilisation :

* tags
* descriptions
* exemples
* codes HTTP
* modèles Pydantic

---

# Architecture

Toutes les nouvelles fonctionnalités respectent strictement l'architecture du projet.

```
backend/app/

api/
    routes/
        admin.py
        settings.py
        ai_provider.py
        ai_model.py
        api_key.py
        role.py
        permission.py
        log.py
        health.py

services/
    admin_service.py
    settings_service.py
    ai_provider_service.py
    ai_model_service.py
    api_key_service.py
    role_service.py
    permission_service.py
    log_service.py
    health_service.py

repositories/
    admin_repository.py
    settings_repository.py
    ai_provider_repository.py
    ai_model_repository.py
    api_key_repository.py
    role_repository.py
    permission_repository.py
    log_repository.py
    health_repository.py

models/
    setting.py
    ai_provider.py
    ai_model.py
    api_key.py
    role.py
    permission.py
    role_permission.py
    audit_log.py
    error_log.py

schemas/
    setting.py
    ai_provider.py
    ai_model.py
    api_key.py
    role.py
    permission.py
    audit_log.py
    error_log.py
```

---

# Contraintes techniques

Le développement doit respecter les règles suivantes :

* Python 3.13
* FastAPI
* SQLAlchemy 2.x
* Alembic
* PostgreSQL
* Pydantic v2
* Injection de dépendances via FastAPI
* Typage complet
* Ruff sans avertissement
* Pytest avec couverture des nouvelles fonctionnalités
* Documentation OpenAPI complète
* Aucune logique métier dans les routes
* Services responsables de l'ensemble de la logique métier
* Repositories limités aux accès SQLAlchemy

---

# Livrables attendus

À la fin du Sprint 06, les éléments suivants devront être disponibles :

* modèles SQLAlchemy d'administration
* schémas Pydantic v2
* repositories
* services
* routes REST
* migrations Alembic
* documentation OpenAPI
* jeux de données de démonstration (seed)
* tests unitaires
* tests d'intégration
* rapport de validation Ruff
* rapport d'exécution Pytest

---

# Critères d'acceptation

Le sprint sera considéré comme terminé lorsque :

* tous les modules d'administration seront opérationnels ;
* toutes les API REST répondront avec les codes HTTP appropriés ;
* les clés API seront stockées de manière chiffrée et ne seront jamais exposées en clair ;
* les contrôles d'accès par rôles et permissions seront fonctionnels ;
* les journaux d'audit et d'erreurs seront consultables ;
* les contrôles de santé des services seront disponibles via des endpoints dédiés ;
* toutes les migrations Alembic seront appliquées avec succès ;
* Ruff ne remontera aucune erreur ;
* l'ensemble des tests Pytest sera validé avec succès ;
* la documentation OpenAPI reflétera fidèlement toutes les fonctionnalités du sprint.
