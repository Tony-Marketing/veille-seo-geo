# Sprint 08 - Desktop shell PySide6

## Objectif

Le Sprint 08 met en place un premier client Desktop executable pour la plateforme Veille SEO-GEO Groupe A.P&Partner.

L'application Desktop doit demarrer avec :

```powershell
py desktop\main.py
```

Le client Desktop est une interface graphique PySide6. Il communique uniquement avec l'API FastAPI par HTTP REST et ne doit jamais acceder directement a PostgreSQL.

## Architecture Desktop

L'arborescence Desktop est isolee dans `desktop/` :

```text
desktop/
  main.py
  app.py
  core/
    api_client.py
    config.py
    constants.py
  ui/
    main_window.py
    dashboard_page.py
    websites_page.py
    entities_page.py
    keywords_page.py
    competitors_page.py
    reports_page.py
    administration_page.py
  widgets/
    sidebar.py
    topbar.py
    statusbar.py
  styles/
    dark.qss
  resources/
    icons/
    logo/
```

La fenetre principale assemble :

- une barre superieure ;
- un menu lateral ;
- une zone centrale de contenu ;
- une barre d'etat.

La navigation couvre les modules Tableau de bord, Websites, Entities, Keywords, Competitors, Reports et Administration.

## Mode de lancement

Depuis la racine du depot :

```powershell
py desktop\main.py
```

Le backend doit etre lance separement pour que les donnees reelles soient chargees :

```powershell
py -m uvicorn backend.app.main:app --reload
```

## Dependances

Le sprint ajoute la dependance Desktop :

- `PySide6`

La dependance `httpx` etait deja presente dans le projet et reste utilisee pour les appels HTTP REST.

## Fonctionnement ApiClient

`desktop/core/api_client.py` centralise les appels au backend.

La configuration par defaut est :

```python
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
```

Le client expose les methodes :

- `get()`
- `post()`
- `put()`
- `delete()`
- `check_health()`

Les erreurs reseau et les statuts HTTP en erreur sont convertis en `ApiClientError` afin que l'interface affiche un message propre sans crash.

## Module Websites

La page Websites appelle :

```text
GET /api/v1/websites
```

La reponse est traitee comme une reponse paginee avec les champs :

- `items`
- `total`
- `page`
- `page_size`
- `pages`

Le Desktop ne suppose pas que l'endpoint retourne directement une liste.

## Criteres d'acceptation

- L'application demarre avec `py desktop\main.py`.
- Le theme sombre `desktop/styles/dark.qss` est charge.
- La navigation fonctionne entre toutes les pages.
- Le dashboard affiche le nom de l'application, la version, l'utilisateur Admin et l'etat backend.
- La page Websites affiche un tableau avec Nom, URL, Actif et Entite.
- Le bouton Rafraichir recharge les donnees depuis l'API.
- Si l'API est indisponible, l'application affiche un message lisible sans crash.
- Le client Desktop n'accede jamais directement a PostgreSQL.
- Aucun refactor backend global n'est effectue.

## Tests a executer

```powershell
git status
git diff --stat
git diff --check
py -m pytest
py -m ruff check .
py desktop\main.py
```
