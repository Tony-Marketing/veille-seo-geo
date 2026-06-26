# Sprint 04 — Développement du Frontend

**Statut :** À réaliser

---

# Objectif

Développer le socle complet de l'interface utilisateur de l'application.

À la fin de ce sprint, l'utilisateur devra pouvoir :

- se connecter ;
- naviguer dans l'application ;
- accéder aux différents modules (même vides) ;
- communiquer avec l'API FastAPI ;
- disposer d'une interface moderne, responsive et cohérente.

Aucune fonctionnalité métier (SEO, GEO, Dashboard, etc.) ne sera développée durant ce sprint.

---

# Livrables attendus

## Structure React

Créer une architecture claire et évolutive.

```
frontend/

src/

components/

layouts/

pages/

services/

hooks/

contexts/

types/

assets/

styles/

router/
```

---

# Technologies

Utiliser :

- React
- TypeScript
- React Router
- Vite
- TailwindCSS
- Axios

---

# Navigation

Créer une navigation complète.

Modules :

- Tableau de bord
- Marché
- Analyse SEO
- Analyse GEO
- Mots-clés
- URLs
- Planning
- Projet
- Automatisation
- Administration
- Paramètres

Chaque module devra posséder sa propre page.

Les pages pourront afficher un simple contenu temporaire.

---

# Authentification

Créer :

- page Login
- page Déconnexion
- gestion des JWT
- stockage sécurisé des tokens
- protection des routes privées

L'utilisateur non authentifié devra être automatiquement redirigé vers :

```
/login
```

---

# Layout principal

Créer :

- Header
- Sidebar
- Zone principale
- Footer

Le sélecteur d'entité devra être visible dans le Header.

---

# Design

Créer une interface moderne inspirée des applications SaaS.

Principes :

- design clair
- responsive
- coins arrondis
- ombres légères
- animations discrètes
- palette sobre

Prévoir dès maintenant un futur mode sombre.

---

# Composants réutilisables

Créer une bibliothèque de composants :

- Button
- Card
- Modal
- Input
- Select
- Table
- Badge
- Alert
- Loader
- Pagination

Tous les composants devront être réutilisables.

---

# Services API

Créer :

```
services/api.ts
```

Configurer :

- Axios
- URL de l'API
- ajout automatique du JWT
- gestion des erreurs
- renouvellement automatique du token

---

# Gestion globale

Créer les Contexts React :

- AuthContext
- EntityContext
- ThemeContext

Utiliser les hooks React lorsque pertinent.

---

# Gestion des erreurs

Créer :

- page 404
- page 403
- page erreur serveur

---

# Loader global

Afficher un loader pendant les appels API.

---

# Responsive

L'interface devra fonctionner correctement sur :

- écran Full HD
- ordinateur portable
- tablette

---

# Tests

Créer les premiers tests React.

Tester :

- Login
- Navigation
- Composants principaux

---

# Documentation

Mettre à jour :

- README.md
- ARCHITECTURE.md

Documenter l'organisation du frontend.

---

# Hors périmètre

Ne pas développer :

- Dashboard métier
- SEO
- GEO
- Google Search Console
- Scraping
- IA
- Reporting
- Graphiques

Le sprint concerne uniquement la structure du frontend.

---

# Critères d'acceptation

Le sprint est considéré terminé si :

✓ Le frontend démarre correctement.

✓ Le Login fonctionne.

✓ Les routes protégées sont opérationnelles.

✓ La navigation est complète.

✓ Le Layout est terminé.

✓ Les composants réutilisables existent.

✓ Les appels API fonctionnent.

✓ Les tests principaux passent.

---

# Résultat attendu

À la fin du Sprint 04, l'application dispose d'une interface utilisateur moderne entièrement connectée au backend.

Toutes les pages principales existent et peuvent être enrichies progressivement lors des prochains sprints.

---

# Prompt Codex

Respecte strictement les fichiers :

- AGENTS.md
- ARCHITECTURE.md
- README.md
- CONTRIBUTING.md

Travaille exclusivement sur le frontend React.

N'implémente aucune nouvelle logique métier dans le backend.

Construis une architecture React moderne basée sur :

- React
- TypeScript
- Vite
- TailwindCSS
- React Router
- Axios

Crée une navigation complète correspondant aux futurs modules de l'application.

Implémente un système d'authentification côté client compatible avec le backend développé lors du Sprint 03.

Crée un layout moderne composé d'un Header, d'une Sidebar, d'une zone de contenu principale et d'un Footer.

Développe une bibliothèque de composants réutilisables (Button, Card, Table, Modal, Input, Loader, etc.).

Configure un service Axios centralisé avec gestion automatique du JWT et des erreurs.

Prépare les Contexts nécessaires (AuthContext, EntityContext, ThemeContext).

Ajoute les premiers tests React.

À la fin de ton travail :

- présente l'arborescence du frontend ;
- explique les choix techniques ;
- liste les composants créés ;
- indique les pages disponibles ;
- précise les tests réalisés ;
- n'effectue aucune modification en dehors du périmètre de ce sprint.