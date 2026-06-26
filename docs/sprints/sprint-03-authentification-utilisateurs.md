# Sprint 03 — Authentification et gestion des utilisateurs

**Statut :** À réaliser

---

# Objectif

Mettre en place le système complet d'authentification et d'autorisation de l'application.

À la fin de ce sprint, l'application devra permettre :

- l'authentification des utilisateurs ;
- la gestion des rôles ;
- la gestion des permissions ;
- la protection des endpoints ;
- la gestion des sessions via JWT.

Aucune interface graphique ne sera développée durant ce sprint.

---

# Livrables attendus

## Authentification

Mettre en place :

- JWT (JSON Web Token)
- Access Token
- Refresh Token
- expiration des jetons
- renouvellement automatique

Les secrets devront être stockés dans le fichier `.env`.

---

# Utilisateurs

Créer les fonctionnalités suivantes :

- création d'un utilisateur
- modification d'un utilisateur
- suppression d'un utilisateur
- activation
- désactivation
- changement de mot de passe
- réinitialisation de mot de passe

Les mots de passe devront être hachés avec **Argon2** (ou bcrypt si Argon2 n'est pas retenu).

Aucun mot de passe ne devra être enregistré en clair.

---

# Gestion des rôles

Créer les rôles suivants :

- Administrateur
- Manager SEO
- Analyste SEO
- Rédacteur
- Lecteur
- Client

Chaque rôle devra pouvoir évoluer facilement.

---

# Gestion des permissions

Créer un système de permissions indépendant des rôles.

Exemples :

- consulter un module
- modifier un module
- supprimer
- exporter
- administrer

Les permissions devront pouvoir être ajoutées sans modifier le code existant.

---

# Protection des routes

Toutes les routes devront pouvoir être protégées par :

- authentification
- rôle
- permission

Exemple :

```
Utilisateur connecté

↓

JWT valide

↓

Permission vérifiée

↓

Accès autorisé
```

---

# Dépendances FastAPI

Créer les dépendances permettant :

- récupérer l'utilisateur courant
- vérifier un rôle
- vérifier une permission

Exemple :

```
Depends(get_current_user)

Depends(require_role)

Depends(require_permission)
```

---

# Endpoints

Créer les endpoints suivants :

## Authentification

```
POST /auth/login

POST /auth/logout

POST /auth/refresh

GET /auth/me
```

---

## Utilisateurs

```
GET /users

GET /users/{id}

POST /users

PUT /users/{id}

DELETE /users/{id}
```

---

## Rôles

```
GET /roles

POST /roles

PUT /roles/{id}

DELETE /roles/{id}
```

---

## Permissions

```
GET /permissions

POST /permissions

PUT /permissions/{id}

DELETE /permissions/{id}
```

---

# Validation

Toutes les entrées devront être validées via Pydantic.

Les erreurs devront utiliser :

```
HTTPException
```

avec des messages explicites.

---

# Journalisation

Créer un système de journalisation des actions sensibles :

- connexion
- déconnexion
- création utilisateur
- suppression utilisateur
- changement de rôle
- modification des permissions

Les journaux devront être enregistrés dans :

```
audit_logs
```

---

# Sécurité

Mettre en œuvre :

- hachage sécurisé des mots de passe
- protection contre les JWT invalides
- expiration des sessions
- vérification des permissions
- protection des routes sensibles

Les clés secrètes ne devront jamais être présentes dans le code source.

---

# Tests

Créer des tests couvrant notamment :

- connexion
- mot de passe incorrect
- JWT expiré
- accès interdit
- création d'utilisateur
- permissions

---

# Documentation

Mettre à jour :

- README.md
- ARCHITECTURE.md

Documenter les endpoints dans :

```
docs/api/
```

---

# Hors périmètre

Ne pas développer :

- interface React
- tableau de bord
- SEO
- GEO
- connecteurs Google
- connecteurs IA
- scraping
- reporting

Ce sprint concerne uniquement la sécurité et l'authentification.

---

# Critères d'acceptation

Le sprint est considéré terminé si :

✓ Un utilisateur peut se connecter.

✓ Les mots de passe sont correctement hachés.

✓ Les JWT fonctionnent.

✓ Les Refresh Tokens fonctionnent.

✓ Les rôles sont opérationnels.

✓ Les permissions sont vérifiées.

✓ Les routes protégées sont inaccessibles sans authentification.

✓ Les tests passent avec succès.

✓ Les actions sensibles sont journalisées.

---

# Résultat attendu

À la fin du Sprint 03, le backend dispose d'un système complet d'authentification, d'autorisation et de gestion des utilisateurs. Toutes les API peuvent désormais être sécurisées avant l'arrivée de l'interface utilisateur.

---

# Prompt Codex

Respecte strictement les fichiers :

- AGENTS.md
- ARCHITECTURE.md
- README.md
- CONTRIBUTING.md

Travaille exclusivement sur le backend.

N'implémente aucune interface React.

Implémente un système d'authentification robuste basé sur JWT.

Utilise des Access Tokens et Refresh Tokens.

Les mots de passe doivent être hachés avec Argon2 (ou bcrypt si nécessaire).

Ne jamais enregistrer de mot de passe en clair.

Implémente une gestion complète des utilisateurs, des rôles et des permissions.

Toutes les routes sensibles doivent être protégées.

Crée des dépendances FastAPI pour contrôler l'authentification et les autorisations.

Journalise toutes les actions sensibles dans la table `audit_logs`.

Ajoute des tests unitaires et d'intégration couvrant les principaux scénarios d'authentification.

Documente automatiquement les endpoints dans Swagger.

À la fin de ton travail :

- présente l'arborescence des fichiers créés ou modifiés ;
- explique les choix de sécurité retenus ;
- liste les nouveaux endpoints ;
- indique les tests réalisés ;
- n'effectue aucune modification en dehors du périmètre de ce sprint.