# UI/UX Design Specification

Projet : Veille SEO-GEO Groupe A.P&Partner  
Version du document : 1.0  
Statut : Reference officielle UI/UX  
Perimetre : Interface Desktop PySide6 et futures interfaces applicatives  
Langue : Francais

---

## Table des matieres

1. [Introduction](#1-introduction)
2. [Inspirations](#2-inspirations)
3. [Philosophie graphique](#3-philosophie-graphique)
4. [Charte graphique complete](#4-charte-graphique-complete)
5. [Typographie](#5-typographie)
6. [Icones](#6-icones)
7. [Layout general](#7-layout-general)
8. [Sidebar](#8-sidebar)
9. [TopBar](#9-topbar)
10. [Dashboard](#10-dashboard)
11. [Pages de l'application](#11-pages-de-lapplication)
12. [Design System](#12-design-system)
13. [Etats des composants](#13-etats-des-composants)
14. [Tables](#14-tables)
15. [Formulaires](#15-formulaires)
16. [Etats globaux](#16-etats-globaux)
17. [Responsive Desktop](#17-responsive-desktop)
18. [Accessibilite](#18-accessibilite)
19. [Parcours utilisateur](#19-parcours-utilisateur)
20. [Bonnes pratiques](#20-bonnes-pratiques)
21. [Roadmap UI](#21-roadmap-ui)
22. [Annexes](#22-annexes)

---

## 1. Introduction

### 1.1 Presentation du projet

Veille SEO-GEO Groupe A.P&Partner est une plateforme interne de pilotage marketing, SEO et GEO.
Elle centralise les donnees issues des sites du groupe, des moteurs de recherche, des moteurs d'IA generative,
des crawlers, des outils de performance et des modules d'administration.

L'application doit permettre aux equipes marketing, SEO, direction, contenu et technique de surveiller,
diagnostiquer, prioriser et documenter les actions liees a la visibilite numerique du groupe.

Le produit doit etre percus comme un logiciel professionnel durable, robuste et precis. L'interface ne doit pas
ressembler a une maquette marketing, a une page vitrine ou a un tableau de bord decoratif. Elle doit ressembler a
un outil de travail dense, lisible, fiable et extensible.

### 1.2 Vision

La vision UI/UX est la suivante :

> Fournir une interface de pilotage claire, rapide et stable permettant de comprendre l'etat SEO-GEO du groupe en
> quelques secondes, puis d'entrer dans le detail sans rupture de contexte.

L'application doit combiner :

- la densite informationnelle d'un outil d'observabilite ;
- la qualite de navigation d'un IDE moderne ;
- la clarte d'un outil de gestion de projet ;
- la robustesse d'un logiciel d'administration ;
- la souplesse d'une plateforme modulaire.

### 1.3 Objectifs de l'interface

| Objectif | Description | Impact attendu |
|---|---|---|
| Pilotage | Donner une vision globale de l'etat SEO, GEO, technique et contenu | Decisions plus rapides |
| Diagnostic | Permettre l'identification des anomalies, tendances et opportunites | Meilleure priorisation |
| Productivite | Reduire le nombre de clics pour acceder aux informations frequentes | Gain de temps quotidien |
| Fiabilite | Afficher des etats clairs pour les donnees, l'API et les erreurs | Confiance utilisateur |
| Evolutivite | Accueillir de nouveaux modules sans casser les reperes existants | Croissance durable |
| Documentation | Rendre les actions et donnees explicites | Transmission plus facile |

### 1.4 Public vise

| Profil | Besoin principal | Niveau technique | Interface attendue |
|---|---|---:|---|
| Direction | Lire les tendances, alertes et rapports | Faible a moyen | Synthese, KPI, rapports |
| Responsable marketing | Piloter les priorites, contenus et campagnes | Moyen | Dashboard, planning, actions |
| Expert SEO | Analyser URLs, mots-cles, indexation, crawl | Eleve | Tables, filtres, exports |
| Analyste GEO | Suivre prompts, citations, modeles IA | Eleve | Comparaison, historique, sources |
| Administrateur | Gerer users, roles, API, configuration | Eleve | Formulaires, logs, securite |
| Developpeur | Diagnostiquer API, jobs, erreurs, connecteurs | Eleve | Logs, etats systeme, details |

### 1.5 Valeurs UX

Les valeurs UX prioritaires sont :

1. Clarite : chaque zone doit expliquer son role par sa structure, pas par des textes inutiles.
2. Controle : l'utilisateur doit savoir ou il est, ce qui est filtre, ce qui est charge et ce qui a echoue.
3. Rapidite : les parcours frequents doivent etre courts, avec raccourcis et actions visibles.
4. Confiance : les etats systeme doivent etre explicites, les erreurs lisibles, les donnees horodatees.
5. Continuite : les modules doivent partager les memes patterns pour eviter la relecture permanente.
6. Sobriete : l'esthetique sert la comprehension, elle ne concurrence jamais les donnees.

### 1.6 Principes de conception

| Principe | Regle concrete |
|---|---|
| D'abord l'information | Le contenu utile prime sur la decoration |
| Navigation persistante | La Sidebar reste le repere principal |
| Etats visibles | Chargement, erreurs, API, base et synchronisation sont toujours lisibles |
| Modularite | Chaque module est autonome mais coherent avec le shell global |
| Densite maitrisee | Les vues metier peuvent etre denses, mais jamais brouillonnes |
| Actions contextualisees | Les actions sont proches des donnees qu'elles affectent |
| Pas de surprise | Les composants reagissent toujours de la meme facon |
| Progressive disclosure | Les details avances sont disponibles sans saturer la vue initiale |

### 1.7 Objectifs de productivite

- Acceder a un module principal en un clic depuis la Sidebar.
- Rechercher un site, une entite, un mot-cle ou un rapport depuis la TopBar.
- Filtrer une table sans ouvrir de page dediee.
- Exporter les listes importantes depuis la toolbar de table.
- Voir les anomalies critiques depuis le Dashboard.
- Identifier l'etat de connexion API sans ouvrir les parametres.
- Relancer une synchronisation ou un crawl depuis son contexte.

### 1.8 Objectifs de simplicite

La simplicite ne signifie pas suppression des fonctions. Elle signifie :

- un vocabulaire stable ;
- des ecrans organises par priorite ;
- des libelles courts ;
- des actions visibles ;
- des erreurs comprehensibles ;
- une separation nette entre lecture, modification et administration.

### 1.9 Objectifs de lisibilite

| Zone | Exigence de lisibilite |
|---|---|
| Dashboard | Les KPI principaux doivent etre lisibles en moins de 5 secondes |
| Tables | Les colonnes critiques doivent rester visibles sans scroll horizontal excessif |
| Formulaires | Les champs obligatoires, erreurs et aides doivent etre evidents |
| Logs | Les niveaux de severite doivent etre reconnaissables immediatement |
| Graphiques | Les axes, periodes et legendes doivent etre explicites |
| Navigation | Le module actif doit etre visible sans ambiguite |

### 1.10 Objectifs d'evolutivite

L'interface doit prevoir :

- l'ajout de modules SEO, GEO, crawler, LLM, prompts, rapports et administration avancee ;
- l'ajout de sous-menus ;
- l'ajout de favoris ;
- l'ajout d'une recherche globale ;
- l'ajout d'un centre de notifications ;
- l'ajout de themes ;
- l'ajout de permissions par role ;
- l'ajout de vues detail, split view et panneaux lateraux.

---

## 2. Inspirations

### 2.1 Synthese comparative

| Produit | Nature | Qualite principale | Risque a eviter |
|---|---|---|---|
| JetBrains IDE | IDE professionnel | Navigation dense et outils dockables | Trop de complexite initiale |
| Visual Studio Code | Editeur extensible | Sidebar iconique et commandes rapides | Trop orienter l'UI vers le code |
| GitHub Desktop | Client Git | Simplicite des parcours | Manque de densite analytique |
| Grafana | Observabilite | Dashboards, panels, alertes | Surabondance de graphiques |
| Home Assistant | Supervision domotique | Etats temps reel et cartes modulaires | Cartes trop decoratives |
| Azure DevOps | Plateforme projet | Organisation par modules et tables | Interface parfois lourde |
| Notion | Workspace documentaire | Lisibilite et hierarchie editoriale | Trop faible pour l'administration avancee |

### 2.2 JetBrains IDE

| Aspect | Analyse |
|---|---|
| Points forts | Navigation laterale, outils dockables, densite, raccourcis clavier, coherence multi-produits |
| Points faibles | Courbe d'apprentissage elevee, nombreuses zones concurrentes |
| Elements retenus | Sidebar persistante, barre d'etat informative, panneaux contextuels, densite assumee |
| Justification | Le projet doit devenir un outil expert utilise chaque jour par des profils avances |

Elements a adapter :

- utiliser des modules clairs plutot que des tool windows techniques ;
- conserver une densite professionnelle sans multiplier les panneaux par defaut ;
- reserver les panneaux avancés aux vues detail.

### 2.3 Visual Studio Code

| Aspect | Analyse |
|---|---|
| Points forts | Navigation rapide, commandes globales, interface sombre efficace, extensions coherentes |
| Points faibles | Iconographie parfois abstraite, besoin de raccourcis pour etre vraiment productif |
| Elements retenus | TopBar de recherche, Sidebar compacte future, command palette future |
| Justification | L'application aura de nombreux modules et beneficiera d'une recherche transversale |

Elements a adapter :

- ne pas masquer les libelles dans la Sidebar au demarrage ;
- ne pas adopter une logique trop developpeur pour les profils marketing ;
- garder les actions principales visibles.

### 2.4 GitHub Desktop

| Aspect | Analyse |
|---|---|
| Points forts | Parcours simples, actions explicites, etats clairs |
| Points faibles | Peu adapte aux tableaux tres denses |
| Elements retenus | Messages d'etat simples, actions primaires nettes, confirmations sobres |
| Justification | Les modules de creation et configuration doivent rester accessibles |

Elements a adapter :

- appliquer la clarte de GitHub Desktop aux formulaires ;
- eviter son minimalisme pour les vues analytiques ;
- utiliser des empty states aussi explicites.

### 2.5 Grafana

| Aspect | Analyse |
|---|---|
| Points forts | Panels modulaires, visualisation temporelle, alertes, filtres par periode |
| Points faibles | Peut devenir illisible avec trop de panels |
| Elements retenus | KPI cards, time range, alert panels, dashboards configurables a terme |
| Justification | SEO, GEO, crawl et performance sont des donnees temporelles et comparatives |

Elements a adapter :

- limiter le nombre de couleurs par graphique ;
- prioriser les alertes metier, pas seulement les metriques systeme ;
- associer chaque graphique a une action ou une lecture claire.

### 2.6 Home Assistant

| Aspect | Analyse |
|---|---|
| Points forts | Etats systeme, cartes modulaires, dashboard personnalisable |
| Points faibles | Presentation parfois trop orientee widgets |
| Elements retenus | Etats temps reel, cartes statut, alertes visibles |
| Justification | L'application doit afficher clairement API, base, synchronisation, crawls et connecteurs |

Elements a adapter :

- utiliser les cartes pour resumer, pas pour decorer ;
- eviter une grille trop libre qui nuit a la comparaison ;
- conserver une structure stable par role.

### 2.7 Azure DevOps

| Aspect | Analyse |
|---|---|
| Points forts | Modules metier, tables, filtres, permissions, historique |
| Points faibles | Densite parfois lourde, navigation profonde |
| Elements retenus | Organisation par module, tables puissantes, administration robuste |
| Justification | Le projet inclut utilisateurs, roles, API, logs, configuration et rapports |

Elements a adapter :

- reduire les niveaux de navigation ;
- rendre les actions critiques plus visibles ;
- harmoniser les formulaires.

### 2.8 Notion

| Aspect | Analyse |
|---|---|
| Points forts | Lisibilite, hierarchie, edition fluide, documentation integree |
| Points faibles | Peu adapte aux donnees systeme complexes |
| Elements retenus | Espacement editorial, sections claires, pages de documentation et rapports |
| Justification | Les rapports SEO-GEO doivent etre lisibles par des non-techniciens |

Elements a adapter :

- ne pas reprendre l'esthetique trop blanche et vide ;
- utiliser la clarte textuelle pour les rapports et details ;
- conserver les outils experts autour des documents.

---

## 3. Philosophie graphique

### 3.1 Ambiance generale

L'ambiance doit etre :

- sombre par defaut ;
- precise ;
- calme ;
- professionnelle ;
- orientee donnees ;
- compatible avec une utilisation prolongee ;
- inspiree d'outils d'observabilite et d'administration.

Le theme sombre est obligatoire comme experience native. Il reduit la fatigue visuelle, met en valeur les donnees
et donne une identite logicielle serieuse. Un theme clair pourra etre prevu plus tard, mais ne doit pas dicter les
choix initiaux.

### 3.2 Identite visuelle

L'identite du produit repose sur quatre piliers :

| Pilier | Traduction graphique |
|---|---|
| Expertise | Grilles, tables, valeurs precises, hierarchie nette |
| Surveillance | Etats, badges, alertes, historiques, indicateurs |
| Strategie | Dashboards synthétiques, rapports, tendances |
| Extensibilite | Navigation modulaire, composants reutilisables |

### 3.3 Ton de l'interface

Le ton doit etre direct, utile et non commercial.

Exemples de bons libelles :

- "API indisponible"
- "3 erreurs critiques detectees"
- "Derniere synchronisation : aujourd'hui 09:42"
- "Aucun site ne correspond aux filtres"
- "Exporter les mots-cles"

Libelles a eviter :

- "Oups !"
- "Quelque chose s'est mal passe"
- "Decouvrez notre super dashboard"
- "Cliquez ici pour commencer votre aventure"

### 3.4 Densite d'information et lisibilite

| Type d'ecran | Densite cible | Justification |
|---|---:|---|
| Dashboard direction | Moyenne | Lecture rapide, priorite aux KPI |
| Dashboard expert | Elevee | Diagnostic et comparaison |
| Tables SEO | Elevee | Analyse massive de donnees |
| Formulaires | Moyenne | Eviter les erreurs de saisie |
| Administration | Moyenne a elevee | Beaucoup de parametres, besoin de controle |
| Rapports | Faible a moyenne | Lecture et partage |

La densite doit etre geree par :

- des espacements constants ;
- des titres courts ;
- des colonnes configurables ;
- des filtres repliegables ;
- des panneaux detail ;
- des tableaux bien alignes.

### 3.5 Experience utilisateur recherchee

L'utilisateur doit ressentir :

- "Je comprends l'etat du systeme."
- "Je sais ou cliquer."
- "Je peux explorer sans perdre le contexte."
- "Je peux faire confiance aux donnees affichees."
- "Les erreurs sont gerees proprement."
- "L'outil peut grandir sans devenir incoherent."

---

## 4. Charte graphique complete

### 4.1 Palette principale

| Token | HEX | Usage principal | Contraste cible |
|---|---|---|---|
| Primary 50 | `#EFF6FF` | Accent tres clair, theme clair futur | Texte sombre |
| Primary 100 | `#DBEAFE` | Fond info leger | Texte sombre |
| Primary 300 | `#93C5FD` | Focus visible | 3:1 minimum |
| Primary 500 | `#3B82F6` | Actions principales | 4.5:1 sur sombre |
| Primary 600 | `#2563EB` | Bouton primaire, selection active | 4.5:1 |
| Primary 700 | `#1D4ED8` | Hover primaire | 4.5:1 |
| Primary 900 | `#1E3A8A` | Accent profond | Texte clair |

### 4.2 Palette secondaire

| Token | HEX | Usage |
|---|---|---|
| Secondary 50 | `#F8FAFC` | Texte clair maximal |
| Secondary 100 | `#F1F5F9` | Fond clair futur |
| Secondary 300 | `#CBD5E1` | Texte secondaire |
| Secondary 400 | `#94A3B8` | Texte tertiaire |
| Secondary 600 | `#475569` | Bordure forte |
| Secondary 800 | `#1E293B` | Surface secondaire |
| Secondary 900 | `#0F172A` | Surface principale sombre |
| Secondary 950 | `#020617` | Fond tres sombre |

### 4.3 Palette semantique

| Semantique | HEX | Usage | Exemple |
|---|---|---|---|
| Success | `#22C55E` | Etat OK, progression positive | API connectee |
| Success Soft | `#052E16` | Fond badge success | Site actif |
| Warning | `#F59E0B` | Attention, seuil moyen | CWV a surveiller |
| Warning Soft | `#451A03` | Fond badge warning | Crawl lent |
| Error | `#EF4444` | Erreur, danger, action destructive | API en erreur |
| Error Soft | `#450A0A` | Fond badge error | Indexation bloquee |
| Information | `#06B6D4` | Information neutre | Nouvelle synchronisation |
| Info Soft | `#083344` | Fond badge info | Rapport genere |
| Accent GEO | `#A855F7` | Donnees GEO et IA | Score LLM |
| Accent SEO | `#10B981` | Donnees SEO | Progression positions |

### 4.4 Couleurs de surfaces

| Zone | HEX | Usage |
|---|---|---|
| App Background | `#0B1120` | Fond global |
| Main Content | `#111827` | Zone centrale |
| Surface 1 | `#172033` | Cartes et panneaux |
| Surface 2 | `#1F2937` | Surfaces surlevees |
| Surface 3 | `#273449` | Hover, menus, sections actives |
| Sidebar | `#0A0F1C` | Navigation principale |
| TopBar | `#0F172A` | Barre superieure |
| StatusBar | `#0F172A` | Barre d'etat |
| Modal Overlay | `rgba(2, 6, 23, 0.72)` | Arriere-plan modal |

### 4.5 Couleurs par composant

| Composant | Fond | Texte | Bordure | Etat actif |
|---|---|---|---|---|
| Sidebar item | Transparent | `#CBD5E1` | None | `#2563EB` |
| TopBar | `#0F172A` | `#F8FAFC` | `#253044` | N/A |
| StatusBar | `#0F172A` | `#CBD5E1` | `#253044` | Badge statut |
| Card | `#172033` | `#E5E7EB` | `#253044` | Bordure primary |
| Table header | `#1F2937` | `#F8FAFC` | `#253044` | Tri primary |
| Table row | `#111827` | `#E5E7EB` | `#253044` | Selection `#2563EB` |
| Input | `#0F172A` | `#F8FAFC` | `#334155` | Focus `#3B82F6` |
| Modal | `#172033` | `#E5E7EB` | `#334155` | N/A |

### 4.6 Etats de couleur

| Etat | Regle |
|---|---|
| Hover | Eclaircir legerement la surface ou intensifier l'action |
| Focus | Bordure `#3B82F6`, visible au clavier |
| Pressed | Assombrir de 8 a 12 % |
| Disabled | Reduire contraste, ne jamais masquer completement |
| Error | Bordure et message `#EF4444`, fond soft pour zones critiques |
| Success | Badge ou icone `#22C55E`, pas de vert massif en fond |

### 4.7 Bordures

| Usage | Taille | Couleur |
|---|---:|---|
| Separateur leger | 1 px | `#253044` |
| Bordure input | 1 px | `#334155` |
| Bordure focus | 2 px | `#3B82F6` |
| Bordure erreur | 1 px | `#EF4444` |
| Bordure carte active | 1 px | `#2563EB` |

### 4.8 Ombres

Les ombres doivent rester discretes en theme sombre.

| Niveau | Usage | Valeur indicative |
|---|---|---|
| Shadow 1 | Carte simple | `0 1px 2px rgba(0,0,0,0.24)` |
| Shadow 2 | Dropdown, context menu | `0 8px 24px rgba(0,0,0,0.32)` |
| Shadow 3 | Modal | `0 24px 80px rgba(0,0,0,0.45)` |

### 4.9 Coins arrondis

| Element | Rayon |
|---|---:|
| Boutons | 8 px |
| Inputs | 8 px |
| Cartes | 8 px maximum |
| Tables | 8 px |
| Badges | 999 px |
| Modales | 10 px |
| Sidebar item | 8 px |

Regle : ne pas utiliser de coins tres arrondis pour les panneaux professionnels. Les composants doivent rester nets.

### 4.10 Transparence

La transparence doit etre utilisee seulement pour :

- overlays modaux ;
- hover subtil ;
- selection non active ;
- graphiques superposes ;
- zones de comparaison.

Elle ne doit pas rendre les textes moins lisibles.

---

## 5. Typographie

### 5.1 Police officielle

Police retenue : Segoe UI.

Justification :

- excellente integration Windows ;
- bonne lisibilite en application Desktop ;
- disponible nativement ;
- rendu professionnel ;
- compatible avec PySide6 ;
- adaptee aux tableaux et interfaces denses.

Fallbacks :

```text
Segoe UI, Inter, Arial, sans-serif
```

### 5.2 Echelle typographique

| Style | Taille | Graisse | Interligne | Usage |
|---|---:|---:|---:|---|
| H1 | 28 px | 600 | 36 px | Titre d'ecran majeur |
| H2 | 22 px | 600 | 30 px | Section principale |
| H3 | 18 px | 600 | 26 px | Sous-section, carte importante |
| H4 | 16 px | 600 | 24 px | Titre compact |
| Texte | 14 px | 400 | 22 px | Texte courant |
| Texte dense | 13 px | 400 | 20 px | Tables et panneaux |
| Legende | 12 px | 400 | 18 px | Aides, timestamps |
| Tableau | 13 px | 400 | 20 px | Cellules |
| Badge | 12 px | 600 | 16 px | Statuts |
| Bouton | 14 px | 600 | 20 px | Actions |

### 5.3 Regles typographiques

- Ne pas utiliser de texte inferieur a 12 px.
- Ne pas utiliser d'espacement de lettres negatif.
- Ne pas utiliser de majuscules longues pour les titres.
- Utiliser les majuscules pour les badges courts seulement.
- Limiter la graisse 700 aux cas exceptionnels.
- Toujours aligner les nombres a droite dans les colonnes quantitatives.
- Toujours garder les labels de formulaire en 13 ou 14 px.

### 5.4 Exemples de hierarchie

```text
H1  Dashboard
H2  Visibilite globale
H3  Score GEO moyen
TXT Derniere mise a jour : aujourd'hui 09:42
```

### 5.5 Formatage des valeurs

| Type | Format |
|---|---|
| Pourcentage | `87 %` |
| Score | `72 / 100` |
| Date courte | `29/06/2026` |
| Date avec heure | `29/06/2026 09:42` |
| Duree | `1 min 24 s` |
| Nombre | `12 450` |
| Variation positive | `+4,2 %` |
| Variation negative | `-1,8 %` |

---

## 6. Icones

### 6.1 Comparatif

| Bibliotheque | Points forts | Points faibles | Decision |
|---|---|---|---|
| Lucide | Moderne, lineaire, lisible, coherent, leger | Moins exhaustive que Font Awesome | Retenue |
| Material Symbols | Tres complete, systeme Google, nombreuses variantes | Identite tres Google, poids visuel variable | Non retenue |
| Font Awesome | Tres complete, tres connue | Style moins homogene, parfois lourd | Non retenue |

### 6.2 Bibliotheque officielle

Bibliotheque officielle : Lucide.

Justification :

- icones lineaires adaptees au theme sombre ;
- excellente lisibilite en 16, 18, 20 et 24 px ;
- style neutre et professionnel ;
- coherent avec une interface Desktop moderne.

### 6.3 Tailles

| Usage | Taille |
|---|---:|
| Sidebar | 18 px |
| Bouton compact | 16 px |
| Bouton standard | 18 px |
| Stat card | 20 px |
| Empty state | 32 px |
| Page header | 24 px |
| Alerte critique | 20 px |

### 6.4 Couleurs

| Contexte | Couleur |
|---|---|
| Icone neutre | `#94A3B8` |
| Icone active | `#FFFFFF` |
| Icone primary | `#60A5FA` |
| Icone success | `#22C55E` |
| Icone warning | `#F59E0B` |
| Icone error | `#EF4444` |

### 6.5 Icones recommandees par module

| Module | Icone Lucide indicative |
|---|---|
| Dashboard | `LayoutDashboard` |
| Websites | `Globe` |
| Entities | `Building2` |
| Keywords | `KeyRound` |
| Competitors | `Swords` |
| Crawler | `Bot` |
| SEO | `SearchCheck` |
| GEO | `Sparkles` |
| LLM | `BrainCircuit` |
| Prompts | `MessageSquareText` |
| Rapports | `FileBarChart` |
| Administration | `Settings` |
| Logs | `ScrollText` |
| API | `Plug` |
| Utilisateurs | `Users` |

---

## 7. Layout general

### 7.1 Structure principale

Le shell Desktop repose sur quatre zones stables :

- Sidebar a gauche ;
- TopBar en haut ;
- Content Area au centre ;
- StatusBar en bas.

### 7.2 Wireframe global

```text
+----------------------------------------------------------------------------------+
| TopBar                                                                           |
| [Produit]                         [Recherche globale] [Notif] [Profil] [Version] |
+----------------------+-----------------------------------------------------------+
| Sidebar              | Content Area                                              |
|                      |                                                           |
| Logo + app           | Page Header                                               |
| Etat API             | Breadcrumb / Actions                                      |
| Navigation           |                                                           |
| - Dashboard          | Main View                                                 |
| - Websites           |                                                           |
| - Entities           |                                                           |
| - Keywords           |                                                           |
| - Competitors        |                                                           |
| - Reports            |                                                           |
| - Administration     |                                                           |
|                      |                                                           |
+----------------------+-----------------------------------------------------------+
| StatusBar : API OK | PostgreSQL OK | Derniere sync 09:42 | Utilisateur Admin     |
+----------------------------------------------------------------------------------+
```

### 7.3 Dimensions

| Zone | Dimension standard | Dimension minimale | Comportement |
|---|---:|---:|---|
| Sidebar ouverte | 248 px | 220 px | Peut se reduire a icones plus tard |
| TopBar | 56 px | 52 px | Hauteur fixe |
| StatusBar | 32 px | 28 px | Hauteur fixe |
| Content padding | 24 px | 16 px | S'adapte aux petits ecrans |
| Gouttiere grille | 16 px | 12 px | Stable |
| Carte KPI | 220 x 120 px | 180 x 104 px | Grille responsive |

### 7.4 Grille

La Content Area utilise une grille fluide :

| Largeur ecran | Colonnes recommandees |
|---|---:|
| 1366 px | 12 colonnes compactes |
| 1920 px | 12 colonnes standard |
| 2560 px | 16 colonnes |
| 3440 px | 20 colonnes |
| 3840 px | 24 colonnes |

### 7.5 Comportement au redimensionnement

- La Sidebar conserve sa largeur jusqu'au seuil compact.
- Les tables utilisent toute la largeur disponible.
- Les graphiques changent de nombre de colonnes mais gardent leurs proportions.
- Les toolbars passent sur deux lignes si necessaire.
- Les boutons critiques restent visibles.
- Les panneaux secondaires peuvent se replier.

---

## 8. Sidebar

### 8.1 Role

La Sidebar est le repere principal de navigation. Elle doit etre stable, persistante et lisible.
Elle ne doit pas etre surchargee par des actions secondaires.

### 8.2 Contenu cible

| Zone | Contenu |
|---|---|
| Header | Logo, nom court, version |
| Etat systeme | API, PostgreSQL, sync |
| Navigation | Modules principaux |
| Sous-navigation | Modules avances ou sous-pages |
| Favoris futurs | Vues frequentes |
| Recherche future | Filtrage rapide des modules |
| Footer | Utilisateur, role, environnement |

### 8.3 Wireframe Sidebar ouverte

```text
+------------------------------+
| [Logo] Veille SEO-GEO         |
|        v0.1.0                 |
+------------------------------+
| API        ● OK               |
| PostgreSQL ● OK               |
| Sync       09:42              |
+------------------------------+
| NAVIGATION                    |
| ● Tableau de bord             |
|   Websites                    |
|   Entities                    |
|   Keywords                    |
|   Competitors                 |
|   Crawler                     |
|   SEO                         |
|   GEO                         |
|   LLM                         |
|   Prompts                     |
|   Rapports                    |
|   Administration              |
+------------------------------+
| FAVORIS                       |
|   Sites actifs                |
|   Alertes critiques           |
+------------------------------+
| Admin                         |
| Role : Administrateur         |
+------------------------------+
```

### 8.4 Wireframe Sidebar reduite future

```text
+------+
| Logo |
+------+
| ●API |
+------+
| [D]  |
| [W]  |
| [E]  |
| [K]  |
| [C]  |
| [S]  |
| [G]  |
| [A]  |
+------+
| [U]  |
+------+
```

### 8.5 Etats de navigation

| Etat | Apparence |
|---|---|
| Normal | Texte secondaire, fond transparent |
| Hover | Surface 3, texte clair |
| Actif | Fond primary, texte blanc, icone blanche |
| Disabled | Texte tertiaire, pas de hover |
| Alerte | Badge warning ou error a droite |

### 8.6 Etat API

| Etat | Couleur | Texte |
|---|---|---|
| Connecte | Success | `API OK` |
| Degrade | Warning | `API lente` |
| Indisponible | Error | `API offline` |
| Verification | Info | `Verification...` |

### 8.7 Etat PostgreSQL

Le Desktop ne se connecte jamais directement a PostgreSQL. L'etat PostgreSQL affiche dans la Sidebar doit provenir
exclusivement d'un endpoint backend de sante ou d'administration.

### 8.8 Menu et sous-menu

Regles :

- maximum 2 niveaux visibles ;
- sous-menu replie par defaut si le module n'est pas actif ;
- badge d'alerte possible sur parent ;
- ne pas utiliser trois niveaux dans la Sidebar.

### 8.9 Favoris futurs

Les favoris permettront d'epingler :

- une vue filtree ;
- un rapport ;
- une entite ;
- une table sauvegardee ;
- un dashboard secondaire.

---

## 9. TopBar

### 9.1 Role

La TopBar fournit le contexte global, la recherche, les notifications et l'acces au profil.

### 9.2 Variante standard

```text
+----------------------------------------------------------------------------------+
| Veille SEO-GEO | Dashboard > Visibilite globale  [Rechercher...]  [Bell] [Admin] |
+----------------------------------------------------------------------------------+
```

### 9.3 Variante module detail

```text
+----------------------------------------------------------------------------------+
| Websites > Europ-Arm > Audit technique        [Ctrl+K Rechercher] [API OK] [A.C] |
+----------------------------------------------------------------------------------+
```

### 9.4 Variante administration

```text
+----------------------------------------------------------------------------------+
| Administration > Utilisateurs       [Filtrer un utilisateur] [Logs] [Admin]       |
+----------------------------------------------------------------------------------+
```

### 9.5 Elements

| Element | Role |
|---|---|
| Titre court | Rappelle le module courant |
| Breadcrumb | Situe la page dans l'arborescence |
| Recherche globale | Recherche transversale |
| Notifications | Alertes, erreurs, sync terminees |
| Profil | Utilisateur, role, deconnexion future |
| Version | Version app ou environnement |
| Etat API | Badge compact optionnel |

### 9.6 Regles

- Le breadcrumb ne doit pas depasser deux ou trois niveaux visibles.
- La recherche globale doit avoir un raccourci clavier futur `Ctrl+K`.
- Les notifications doivent etre regroupees par severite.
- Le profil ne doit pas contenir d'action metier.

---

## 10. Dashboard

### 10.1 Role

Le Dashboard est la page d'accueil analytique. Il doit repondre a quatre questions :

1. Le systeme fonctionne-t-il ?
2. La visibilite SEO progresse-t-elle ?
3. La visibilite GEO progresse-t-elle ?
4. Quelles actions demandent une attention immediate ?

### 10.2 Wireframe Dashboard global

```text
+----------------------------------------------------------------------------------+
| Dashboard                                      [Periode: 30 jours] [Exporter]     |
+----------------------------------------------------------------------------------+
| KPI SEO       | KPI GEO       | Sites actifs | Alertes critiques | Rapports      |
| Score 82      | Score 64      | 18           | 3                 | 6 generes     |
| +4,2 %        | -1,1 %        | 17 OK        | 2 SEO / 1 API     | cette semaine |
+----------------------------------------------------------------------------------+
| Evolution SEO                         | Evolution GEO                           |
| [courbe positions / trafic]           | [courbe citations / presence IA]        |
+----------------------------------------------------------------------------------+
| Performance technique                 | Activite recente                         |
| [CWV, crawl, erreurs]                 | - Crawl termine Europ-Arm                |
|                                       | - Rapport mensuel genere                 |
|                                       | - 12 mots-cles ajoutes                   |
+----------------------------------------------------------------------------------+
| Alertes prioritaires                  | Rapports recents                         |
| [table courte]                        | [liste]                                  |
+----------------------------------------------------------------------------------+
```

### 10.3 KPI Cards

| KPI | Valeur | Variation | Action |
|---|---|---|---|
| Score SEO | `82 / 100` | `+4,2 %` | Voir SEO |
| Score GEO | `64 / 100` | `-1,1 %` | Voir GEO |
| Sites actifs | `18` | `+1` | Voir Websites |
| URLs indexees | `12 450` | `+320` | Voir Indexation |
| Alertes | `3` | `-2` | Voir Alertes |
| Rapports | `6` | `+2` | Voir Rapports |

### 10.4 Graphique SEO

Doit montrer :

- evolution des positions ;
- trafic organique ;
- impressions ;
- clics ;
- periode selectionnee ;
- comparaison periode precedente.

```text
+----------------------------------------------------------+
| SEO - Evolution organique                       30 jours  |
|                                                          |
| 100 |                       clics                        |
|  80 |              __----__                              |
|  60 |        __---        ---__                          |
|  40 |  __----                  ----__                    |
|  20 | impressions                                      |
|   0 +--------------------------------------------------  |
|      J-30       J-20       J-10       Aujourd'hui        |
+----------------------------------------------------------+
```

### 10.5 Graphique GEO

Doit montrer :

- score GEO ;
- citations par modele ;
- presence de marque ;
- evolution prompts ;
- comparaison ChatGPT, Gemini, Claude, Perplexity, Mistral.

```text
+----------------------------------------------------------+
| GEO - Presence IA par modele                             |
| ChatGPT     ████████████ 78                              |
| Gemini      ████████     54                              |
| Claude      █████████    63                              |
| Perplexity  ██████       41                              |
| Mistral     █████        35                              |
+----------------------------------------------------------+
```

### 10.6 Graphique IA

Doit comparer :

- cout d'usage ;
- latence ;
- qualite des reponses ;
- taux de citation ;
- erreurs connecteurs.

### 10.7 Activite recente

| Donnee | Format |
|---|---|
| Type | Crawl, rapport, sync, configuration, alerte |
| Acteur | Utilisateur ou systeme |
| Module | SEO, GEO, Websites, Administration |
| Horodatage | Relatif et absolu au survol |
| Action | Voir detail |

### 10.8 Alertes

Les alertes doivent etre classees :

| Niveau | Exemple | Affichage |
|---|---|---|
| Critique | API Search Console indisponible | Rouge, en haut |
| Eleve | 125 URLs 5xx | Rouge |
| Moyen | Core Web Vitals degrade | Orange |
| Faible | Rapport en retard | Bleu ou gris |

---

## 11. Pages de l'application

### 11.1 Regle commune

Chaque page doit suivre cette structure :

```text
+----------------------------------------------------------------------------------+
| Page Header : Titre, description courte, actions principales                      |
+----------------------------------------------------------------------------------+
| Toolbar : recherche, filtres, periode, export, refresh                            |
+----------------------------------------------------------------------------------+
| Content : table, graphique, split view, formulaire ou rapport                     |
+----------------------------------------------------------------------------------+
| Footer contextuel optionnel : pagination, selection, statut                       |
+----------------------------------------------------------------------------------+
```

### 11.2 Dashboard

```text
+----------------------------------------------------------------------------------+
| Dashboard [30 jours] [Comparer] [Exporter]                                        |
+----------------------------------------------------------------------------------+
| KPI row                                                                          |
+----------------------------------------------------------------------------------+
| Graphiques SEO/GEO                                                               |
+----------------------------------------------------------------------------------+
| Alertes | Activite recente | Rapports                                            |
+----------------------------------------------------------------------------------+
```

### 11.3 Websites

```text
+----------------------------------------------------------------------------------+
| Websites                                      [Ajouter] [Importer] [Exporter]     |
+----------------------------------------------------------------------------------+
| [Recherche site] [Entite] [Actif] [CMS] [Rafraichir]                              |
+----------------------------------------------------------------------------------+
| Nom              URL                    Actif  Entite       CMS       Actions     |
| Europ-Arm        https://...            Oui    Europ-Arm     WP        ...         |
| SIMAC            https://...            Oui    SIMAC         Custom    ...         |
+----------------------------------------------------------------------------------+
| 1-20 sur 128                                      < 1 2 3 4 >                     |
+----------------------------------------------------------------------------------+
```

### 11.4 Entities

```text
+----------------------------------------------------------------------------------+
| Entities                                      [Ajouter entite] [Exporter]         |
+----------------------------------------------------------------------------------+
| [Recherche] [Statut] [Marche]                                                    |
+----------------------------------------------------------------------------------+
| Entite          Sites  Mots-cles  Score SEO  Score GEO  Alertes  Responsable     |
| Europ-Arm       3      1 240      82         66         2        Marketing       |
+----------------------------------------------------------------------------------+
```

### 11.5 Keywords

```text
+----------------------------------------------------------------------------------+
| Keywords                              [Ajouter] [Import CSV] [Exporter]           |
+----------------------------------------------------------------------------------+
| [Recherche mot-cle] [Entite] [Position] [Priorite] [Tag]                          |
+----------------------------------------------------------------------------------+
| Mot-cle          Position  Volume  URL cible        Entite    Priorite Actions    |
| carabine PCP     4         2900    /carabines-pcp   Europ     Haute    ...        |
+----------------------------------------------------------------------------------+
```

### 11.6 Competitors

```text
+----------------------------------------------------------------------------------+
| Competitors                                  [Ajouter concurrent] [Comparer]      |
+----------------------------------------------------------------------------------+
| [Recherche] [Marche] [Entite suivie]                                            |
+----------------------------------------------------------------------------------+
| Concurrent      Domaine       Marche      Visibilite SEO  GEO  Derniere analyse  |
| Exemple         example.fr    Tir sportif 71             42   29/06/2026         |
+----------------------------------------------------------------------------------+
```

### 11.7 Crawler

```text
+----------------------------------------------------------------------------------+
| Crawler                                      [Nouveau crawl] [Planifier]          |
+----------------------------------------------------------------------------------+
| [Site] [Statut] [Date] [Erreurs]                                                |
+----------------------------------------------------------------------------------+
| Crawl courant : Europ-Arm                                                        |
| Progression : ███████████░░░ 74 %                                                |
| URLs analysees : 8 420 / 11 350                                                  |
+----------------------------------------------------------------------------------+
| Erreurs | Temps de reponse | Profondeur | Maillage interne                       |
+----------------------------------------------------------------------------------+
```

### 11.8 SEO

```text
+----------------------------------------------------------------------------------+
| SEO                                           [Audit] [Exporter]                  |
+----------------------------------------------------------------------------------+
| [Site] [Periode] [Type probleme] [Priorite]                                      |
+----------------------------------------------------------------------------------+
| Score global | Balises | Contenu | Indexation | Maillage | Performance           |
+----------------------------------------------------------------------------------+
| Liste des recommandations                                                        |
+----------------------------------------------------------------------------------+
```

### 11.9 GEO

```text
+----------------------------------------------------------------------------------+
| GEO                                           [Analyse IA] [Comparer modeles]     |
+----------------------------------------------------------------------------------+
| [Entite] [Modele] [Prompt set] [Periode]                                         |
+----------------------------------------------------------------------------------+
| Score GEO | Citations | Presence marque | Sources | Sentiment                   |
+----------------------------------------------------------------------------------+
| Tableau des reponses IA et citations                                             |
+----------------------------------------------------------------------------------+
```

### 11.10 LLM

```text
+----------------------------------------------------------------------------------+
| LLM                                           [Ajouter modele] [Tester]           |
+----------------------------------------------------------------------------------+
| Fournisseur     Modele       Actif  Cout   Latence  Qualite  Dernier test        |
| OpenAI          GPT          Oui    €€     1.2 s    92       29/06/2026          |
+----------------------------------------------------------------------------------+
```

### 11.11 Prompts

```text
+----------------------------------------------------------------------------------+
| Prompts                                      [Nouveau prompt] [Importer]          |
+----------------------------------------------------------------------------------+
| [Recherche] [Module] [Modele] [Statut]                                           |
+----------------------------------------------------------------------------------+
| Prompt                         Module  Version  Dernier resultat  Actions        |
| Comparaison marque/concurrent  GEO     v3       64               ...            |
+----------------------------------------------------------------------------------+
```

### 11.12 IA

```text
+----------------------------------------------------------------------------------+
| IA                                            [Executer analyse] [Historique]     |
+----------------------------------------------------------------------------------+
| Connecteurs | Modeles | Jobs | Couts | Erreurs                                   |
+----------------------------------------------------------------------------------+
| Synthese des executions recentes                                                 |
+----------------------------------------------------------------------------------+
```

### 11.13 Rapports

```text
+----------------------------------------------------------------------------------+
| Rapports                                      [Nouveau rapport] [Planifier]       |
+----------------------------------------------------------------------------------+
| [Type] [Entite] [Periode] [Statut]                                               |
+----------------------------------------------------------------------------------+
| Rapport                  Type       Entite     Statut     Cree le     Actions    |
| Rapport SEO mensuel      SEO        Groupe     Pret       29/06       ...        |
+----------------------------------------------------------------------------------+
```

### 11.14 Administration

```text
+----------------------------------------------------------------------------------+
| Administration                                                                       |
+----------------------------------------------------------------------------------+
| Utilisateurs | Permissions | API | Configuration | Logs | Sante systeme             |
+----------------------------------------------------------------------------------+
| Panneau d'administration selectionne                                                |
+----------------------------------------------------------------------------------+
```

### 11.15 Utilisateurs

```text
+----------------------------------------------------------------------------------+
| Utilisateurs                                  [Inviter] [Exporter]                |
+----------------------------------------------------------------------------------+
| Nom          Email                 Role          Statut      Derniere connexion   |
| Admin        admin@...             Admin         Actif       Aujourd'hui          |
+----------------------------------------------------------------------------------+
```

### 11.16 Permissions

```text
+----------------------------------------------------------------------------------+
| Permissions                                                                         |
+----------------------------------------------------------------------------------+
| Role        Dashboard Websites SEO GEO Rapports Admin                              |
| Admin       Oui       Oui      Oui Oui Oui      Oui                                |
| Marketing   Oui       Oui      Oui Oui Oui      Non                                |
+----------------------------------------------------------------------------------+
```

### 11.17 API

```text
+----------------------------------------------------------------------------------+
| API & Connecteurs                              [Ajouter cle] [Tester connexions]  |
+----------------------------------------------------------------------------------+
| Service                 Statut    Dernier test     Latence     Actions            |
| Search Console          OK        09:42            320 ms      ...                |
| OpenAI                  OK        09:41            890 ms      ...                |
+----------------------------------------------------------------------------------+
```

### 11.18 Configuration

```text
+----------------------------------------------------------------------------------+
| Configuration                                 [Sauvegarder] [Exporter config]     |
+----------------------------------------------------------------------------------+
| Section            Parametre                 Valeur                Modifie        |
| General            Retention logs            90 jours              Non            |
+----------------------------------------------------------------------------------+
```

### 11.19 Logs

```text
+----------------------------------------------------------------------------------+
| Logs                                          [Exporter] [Nettoyer filtres]       |
+----------------------------------------------------------------------------------+
| [Niveau] [Module] [Date] [Recherche]                                             |
+----------------------------------------------------------------------------------+
| Date        Niveau    Module      Message                         Trace          |
| 09:42       ERROR     API         Timeout Search Console           Voir           |
+----------------------------------------------------------------------------------+
```

### 11.20 Futurs modules

| Module futur | Usage prevu | Pattern UI |
|---|---|---|
| Planning editorial | Calendrier contenus | Calendar + table |
| Projets marketing | Taches et priorites | Kanban + table |
| Automatisations | Jobs et workflows | Flow list + logs |
| Marche | Tendances sectorielles | Dashboard + rapports |
| Contenus | Audit editorial | Table + editor panel |
| URLs | Inventaire URL | Table dense + detail |

---

## 12. Design System

### 12.1 Buttons

| Variante | Role | Exemple |
|---|---|---|
| Primary | Action principale | Ajouter un site |
| Secondary | Action secondaire | Annuler |
| Ghost | Action discrete | Voir details |
| Danger | Action destructive | Supprimer |
| Icon | Action compacte | Rafraichir |

Regles :

- un seul bouton primary par zone logique ;
- danger jamais place par defaut a droite sans confirmation ;
- icone + texte pour actions non evidentes ;
- tooltip obligatoire pour bouton icone seul.

### 12.2 Cards

Les cartes servent a regrouper une information coherente.

| Type | Usage |
|---|---|
| KPI Card | Valeur synthetique |
| Status Card | Etat systeme |
| Chart Card | Graphique |
| Action Card | Action guidee |
| Report Card | Rapport recent |

### 12.3 StatCards

Structure :

```text
+----------------------+
| Icone       Libelle   |
| 82 / 100              |
| +4,2 % vs periode     |
+----------------------+
```

### 12.4 Charts

Types autorises :

| Type | Usage |
|---|---|
| Line chart | Evolution temporelle |
| Bar chart | Comparaison |
| Stacked bar | Repartition |
| Donut | Part limitee, max 5 segments |
| Heatmap | Intensite par jour ou module |
| Sparkline | Mini tendance KPI |

Regles :

- pas de graphique sans titre ;
- toujours afficher periode et source ;
- couleurs semantiques stables ;
- eviter les pie charts complexes.

### 12.5 Tables

Voir chapitre 14 pour normes completes.

### 12.6 Forms

Voir chapitre 15 pour normes completes.

### 12.7 Inputs

| Variante | Usage |
|---|---|
| Text | Nom, libelle |
| URL | Adresse site |
| Number | Seuil, volume |
| Password | Cle API masquee |
| Search | Recherche locale |
| Textarea | Prompt, notes |

### 12.8 Select

Regles :

- utiliser Select pour listes connues ;
- afficher recherche interne au-dela de 8 options ;
- permettre clear si filtre optionnel ;
- conserver la valeur selectionnee visible.

### 12.9 Checkbox

Usage :

- selection multiple ;
- options independantes ;
- colonnes de table ;
- permissions.

### 12.10 Switch

Usage :

- activation/desactivation ;
- statut binaire persistant ;
- ne pas utiliser pour une action instantanee irreversible.

### 12.11 DatePicker

Doit permettre :

- date unique ;
- plage de dates ;
- presets : 7 jours, 30 jours, trimestre, annee ;
- affichage timezone si necessaire.

### 12.12 TreeView

Usage :

- structure des sites ;
- arborescence URL ;
- categories de rapports ;
- permissions groupees.

### 12.13 Tabs

Regles :

- utiliser pour sous-sections d'un meme objet ;
- ne pas utiliser comme navigation principale ;
- garder moins de 8 tabs visibles.

### 12.14 Dialogs

Types :

- confirmation ;
- formulaire compact ;
- detail rapide ;
- erreur critique ;
- export.

### 12.15 Toasts

| Type | Duree |
|---|---:|
| Success | 4 s |
| Info | 5 s |
| Warning | 7 s |
| Error | Persistant ou 10 s |

### 12.16 Notifications

Les notifications durables vont dans un centre dedie, pas seulement en toast.

### 12.17 SearchBar

Recherche globale :

- raccourci futur `Ctrl+K` ;
- resultats groupes par module ;
- acces clavier ;
- dernieres recherches.

### 12.18 Loader

Utiliser :

- spinner pour action courte ;
- progress bar pour operation mesurable ;
- skeleton pour chargement de page ;
- message d'etape pour imports/crawls.

### 12.19 Skeleton

Les skeletons doivent reproduire la forme du contenu final.

### 12.20 ProgressBar

Usage :

- crawl ;
- import ;
- export ;
- synchronisation ;
- analyse IA batch.

### 12.21 Badge

| Badge | Usage |
|---|---|
| Success | Actif, OK, termine |
| Warning | En attente, a verifier |
| Error | Erreur, bloque |
| Info | En cours, nouveau |
| Neutral | Archive, inactif |

### 12.22 Tag

Usage :

- mots-cles ;
- segments ;
- priorites ;
- modeles IA ;
- entites.

### 12.23 Accordion

Usage :

- filtres avances ;
- details techniques ;
- groupes de configuration ;
- FAQ interne.

### 12.24 Context Menu

Usage :

- actions sur ligne de table ;
- actions secondaires ;
- copie de valeur ;
- ouverture detail.

### 12.25 Breadcrumb

Format :

```text
Module > Objet > Detail
```

Exemple :

```text
Websites > Europ-Arm > Audit SEO
```

### 12.26 Pagination

Regles :

- affichage `1-20 sur 128` ;
- tailles 20, 50, 100 ;
- navigation clavier future ;
- conserver les filtres lors du changement de page.

### 12.27 Toolbar

La toolbar regroupe recherche, filtres, actions d'export et rafraichissement.

### 12.28 SplitView

Usage :

- table a gauche, detail a droite ;
- logs a gauche, trace a droite ;
- prompts a gauche, resultat a droite.

### 12.29 EmptyState

Structure :

```text
[Icone]
Aucun site trouve
Modifiez les filtres ou ajoutez un premier site.
[Ajouter un site]
```

### 12.30 ErrorState

Structure :

```text
[Icone erreur]
API indisponible
Impossible de charger les sites pour le moment.
[Reessayer] [Voir details]
```

### 12.31 SuccessState

Usage limite :

- import termine ;
- rapport genere ;
- configuration sauvegardee.

---

## 13. Etats des composants

### 13.1 Matrice generale

| Composant | Normal | Hover | Focus | Pressed | Disabled | Loading | Error | Success |
|---|---|---|---|---|---|---|---|---|
| Button | Fond variante | Eclairci | Bordure focus | Assombri | Gris | Spinner | N/A | N/A |
| Input | Bordure neutre | Bordure claire | Bordure primary | N/A | Fond gris | N/A | Bordure error | Bordure success |
| Select | Ferme | Surface hover | Bordure focus | Ouvert | Disabled | Options chargees | Message | N/A |
| Table row | Fond normal | Fond hover | Outline | Selection | N/A | Skeleton | Ligne erreur | Ligne OK |
| Card | Surface 1 | Surface 2 | Bordure primary | N/A | Opacite | Skeleton | Bordure error | Badge OK |
| Toast | Visible | Pause timer | N/A | N/A | N/A | N/A | Rouge | Vert |

### 13.2 Focus clavier

Tout composant interactif doit avoir un focus visible.

Regle :

```text
outline: 2 px primary
offset: 2 px
```

### 13.3 Loading

Ne jamais bloquer toute l'application si seule une zone charge.

### 13.4 Error

Une erreur doit toujours indiquer :

- ce qui a echoue ;
- pourquoi si connu ;
- quoi faire ensuite ;
- si les donnees affichees sont obsoletes.

### 13.5 Success

Un succes doit etre discret et non intrusif sauf action majeure.

---

## 14. Tables

### 14.1 Role

Les tables sont le composant central des modules SEO, GEO, Websites, Keywords, Logs et Administration.

### 14.2 Structure standard

```text
+----------------------------------------------------------------------------------+
| Toolbar : Recherche | Filtres | Colonnes | Export | Rafraichir                   |
+----------------------------------------------------------------------------------+
| [ ] Nom        URL              Actif  Entite  Score  Derniere analyse  Actions  |
| [ ] Europ      https://...      Oui    Europ   82     29/06/2026        ...      |
+----------------------------------------------------------------------------------+
| Selection : 0 | 1-20 sur 128 | Page 1 2 3                                     |
+----------------------------------------------------------------------------------+
```

### 14.3 Tri

| Regle | Description |
|---|---|
| Tri visible | Icone haut/bas sur colonne active |
| Tri unique par defaut | Une colonne active |
| Multi-tri futur | Possible pour vues avancees |
| Reset | Disponible via menu colonnes ou filtre |

### 14.4 Colonnes

Regles :

- colonnes texte alignees a gauche ;
- colonnes numeriques alignees a droite ;
- statuts centres ou badges ;
- actions toujours a droite ;
- selection toujours a gauche.

### 14.5 Recherche

Recherche table :

- debounce 250 a 400 ms ;
- conserve pagination ;
- affiche le nombre de resultats ;
- message si aucun resultat.

### 14.6 Filtres

Filtres standards :

- entite ;
- site ;
- statut ;
- priorite ;
- periode ;
- module ;
- tag.

### 14.7 Exports

Formats futurs :

- CSV ;
- XLSX ;
- PDF pour rapports ;
- JSON pour configuration.

### 14.8 Pagination

| Element | Regle |
|---|---|
| Page size | 20 par defaut |
| Options | 20, 50, 100 |
| Position | Bas de table |
| Affichage | `1-20 sur 128` |

### 14.9 Actions

Actions de ligne :

- voir ;
- modifier ;
- dupliquer si pertinent ;
- archiver ;
- supprimer avec confirmation ;
- copier URL ou identifiant.

### 14.10 Selection

La selection multiple active une barre d'actions contextuelle.

```text
+----------------------------------------------------------------------------------+
| 12 elements selectionnes        [Exporter] [Taguer] [Archiver] [Annuler]         |
+----------------------------------------------------------------------------------+
```

### 14.11 Context Menu

Le clic droit sur une ligne doit ouvrir les actions secondaires sans remplacer les actions visibles.

---

## 15. Formulaires

### 15.1 Structure

```text
+----------------------------------------------------------+
| Ajouter un website                                      |
+----------------------------------------------------------+
| Nom *                                                    |
| [Europ-Arm]                                             |
| URL *                                                    |
| [https://www.europ-arm.com]                             |
| Entite                                                   |
| [Europ-Arm v]                                           |
| Actif                                                    |
| [ON]                                                     |
+----------------------------------------------------------+
| [Annuler]                                  [Enregistrer] |
+----------------------------------------------------------+
```

### 15.2 Disposition

| Type formulaire | Disposition |
|---|---|
| Court | Modal |
| Moyen | Page ou panneau lateral |
| Long | Page dediee avec sections |
| Configuration | Tabs ou accordions |
| Permissions | Matrice |

### 15.3 Validation

Regles :

- validation a la sortie du champ pour contraintes simples ;
- validation serveur apres soumission ;
- message sous le champ ;
- resume d'erreurs en haut si plusieurs erreurs ;
- ne pas effacer les champs apres erreur.

### 15.4 Messages

| Cas | Message |
|---|---|
| Champ requis | `Ce champ est obligatoire.` |
| URL invalide | `Saisissez une URL valide commencant par https://.` |
| Doublon | `Un site utilise deja cette URL.` |
| Erreur API | `Enregistrement impossible : API indisponible.` |
| Succes | `Website enregistre.` |

### 15.5 Aide

L'aide doit etre courte et contextuelle.

Exemple :

```text
URL canonique du site, incluant le protocole https://.
```

### 15.6 Raccourcis

Futurs raccourcis :

| Raccourci | Action |
|---|---|
| Ctrl+S | Enregistrer |
| Esc | Fermer modal |
| Ctrl+Enter | Valider formulaire long |
| Tab | Champ suivant |
| Shift+Tab | Champ precedent |

---

## 16. Etats globaux

### 16.1 Chargement initial

```text
+----------------------------------------------------------------------------------+
| Veille SEO-GEO                                                                    |
| Initialisation de l'application...                                                |
| Verification API                                                                  |
| Chargement configuration                                                          |
+----------------------------------------------------------------------------------+
```

### 16.2 Erreur globale

Une erreur globale doit proposer :

- reessayer ;
- copier les details ;
- ouvrir les logs si disponible ;
- continuer en mode degrade si possible.

### 16.3 Connexion API perdue

```text
+----------------------------------------------------------------------------------+
| Bandeau warning                                                                   |
| Connexion API perdue. Les donnees affichees peuvent ne plus etre a jour.          |
| [Reessayer] [Details]                                                             |
+----------------------------------------------------------------------------------+
```

### 16.4 Timeout

Message :

```text
Le backend ne repond pas dans le delai attendu. Verifiez l'etat de l'API ou reessayez.
```

### 16.5 Base indisponible

Le Desktop l'apprend via API.

Message :

```text
La base PostgreSQL est indisponible d'apres le backend. Les donnees ne peuvent pas etre chargees.
```

### 16.6 Authentification expiree

Comportement futur :

- afficher modal de reconnexion ;
- conserver la page courante ;
- relancer l'action apres reconnexion si possible.

### 16.7 Synchronisation

Afficher :

- module ;
- progression ;
- derniere synchronisation ;
- prochaine execution ;
- erreurs.

### 16.8 Maintenance

```text
+----------------------------------------------------------------------------------+
| Maintenance en cours                                                              |
| Certaines donnees sont temporairement indisponibles.                              |
| Fin estimee : 14:30                                                               |
+----------------------------------------------------------------------------------+
```

---

## 17. Responsive Desktop

### 17.1 Principes

Le produit est Desktop first. Il doit fonctionner sur plusieurs tailles d'ecran professionnelles.

### 17.2 1920 px

| Element | Comportement |
|---|---|
| Sidebar | Ouverte |
| Dashboard | 4 a 5 KPI par ligne |
| Tables | Colonnes principales visibles |
| SplitView | Possible |

### 17.3 2560 px

| Element | Comportement |
|---|---|
| Dashboard | 5 a 6 KPI par ligne |
| Graphiques | Deux ou trois colonnes |
| Tables | Plus de colonnes visibles |
| Panneaux detail | Permanents possibles |

### 17.4 3440 px UltraWide

| Element | Comportement |
|---|---|
| Dashboard | Grille large, eviter l'etirement excessif |
| Content max | Utiliser colonnes, pas lignes infinies |
| SplitView | 2 ou 3 panneaux possibles |
| Logs | Liste + detail + contexte |

### 17.5 3840 px

Regles :

- ne pas etirer les textes sur toute la largeur ;
- limiter la largeur des paragraphes a 960 px ;
- utiliser des grilles multi-panneaux ;
- permettre dashboard de supervision.

### 17.6 Double ecran

Scenarios :

- Dashboard sur un ecran, detail sur l'autre ;
- rapports et tables cote a cote ;
- logs et configuration pendant diagnostic.

### 17.7 UltraWide wireframe

```text
+--------------------------------------------------------------------------------------------------------------+
| Sidebar | Top context                                                                                         |
|         +------------------------------------------------------------------------------------------------------+
|         | KPI Row                                                                                              |
|         +-------------------------------+-------------------------------+--------------------------------------+
|         | SEO Trend                     | GEO Trend                     | Alertes                              |
|         +-------------------------------+-------------------------------+--------------------------------------+
|         | Table principale                                              | Detail selection                      |
|         |                                                              |                                      |
+---------+--------------------------------------------------------------+--------------------------------------+
```

---

## 18. Accessibilite

### 18.1 Contrastes

Objectifs :

- texte normal : ratio 4.5:1 minimum ;
- texte large : ratio 3:1 minimum ;
- icones informatives : ratio 3:1 minimum ;
- focus : visible sur toutes surfaces.

### 18.2 Navigation clavier

Tous les composants interactifs doivent etre accessibles au clavier :

- Tab ;
- Shift+Tab ;
- Enter ;
- Space ;
- Esc ;
- fleches pour menus et tables.

### 18.3 Focus

Le focus ne doit jamais etre supprime. Il doit etre adapte au theme sombre.

### 18.4 Tooltips

Tooltips obligatoires pour :

- bouton icone seul ;
- abrevation technique ;
- valeur tronquee ;
- statut systeme ;
- erreur detaillee.

### 18.5 Raccourcis clavier

| Raccourci futur | Action |
|---|---|
| Ctrl+K | Recherche globale |
| Ctrl+R | Rafraichir page |
| Ctrl+S | Enregistrer |
| Ctrl+F | Recherche locale |
| Esc | Fermer panneau/modal |
| F1 | Aide contextuelle |

### 18.6 Taille minimale

| Element | Taille minimale |
|---|---:|
| Zone cliquable | 32 x 32 px |
| Bouton standard | 36 px hauteur |
| Ligne table dense | 36 px |
| Champ formulaire | 38 px |
| Icone interactive | 16 px |

---

## 19. Parcours utilisateur

### 19.1 Ajout Website

```text
Dashboard ou Websites
        |
        v
[Ajouter]
        |
        v
Formulaire Website
        |
        +-- Saisie nom, URL, entite, actif
        |
        v
Validation locale
        |
        v
POST API
        |
        +-- Succes : toast + table rafraichie
        |
        +-- Erreur : message champ ou erreur globale
```

### 19.2 Ajout Keyword

```text
Keywords > Ajouter
        |
        v
Saisie mot-cle, entite, URL cible, priorite, tags
        |
        v
Verification doublon via API
        |
        v
Enregistrement
        |
        v
Affichage dans table avec badge "Nouveau"
```

### 19.3 Creation Rapport

```text
Rapports > Nouveau rapport
        |
        v
Choix type : SEO / GEO / Technique / Direction
        |
        v
Choix entite + periode + sections
        |
        v
Generation
        |
        +-- En cours : progress bar
        +-- Pret : notification + ouverture preview
        +-- Erreur : details + relancer
```

### 19.4 Consultation Dashboard

```text
Ouverture application
        |
        v
Dashboard
        |
        +-- Lire KPI
        +-- Identifier alertes
        +-- Cliquer sur anomalie
        |
        v
Vue detail filtree
```

### 19.5 Administration

```text
Administration
        |
        +-- Utilisateurs
        +-- Permissions
        +-- API
        +-- Configuration
        +-- Logs
        |
        v
Action avec confirmation si sensible
```

### 19.6 Configuration connecteur API

```text
Administration > API
        |
        v
Ajouter cle
        |
        v
Saisie service + cle masquee
        |
        v
Tester connexion
        |
        +-- OK : enregistrer
        +-- Erreur : afficher cause probable
```

---

## 20. Bonnes pratiques

### 20.1 Toujours faire

| Regle | Raison |
|---|---|
| Afficher l'etat de chargement | Evite l'impression de blocage |
| Conserver les filtres lors de navigation proche | Productivite |
| Utiliser des libelles metier | Clarite |
| Aligner les colonnes selon type | Lisibilite |
| Confirmer les actions destructives | Securite |
| Montrer la source et la date des donnees | Confiance |
| Prevoir empty/error states | Robustesse |
| Garder une action primaire claire | Simplicite |

### 20.2 Ne jamais faire

| Interdit | Raison |
|---|---|
| Utiliser des couleurs sans signification | Confusion |
| Masquer une erreur technique sous un message vague | Perte de confiance |
| Melanger lecture et edition sans separation | Risque utilisateur |
| Ajouter des cartes decoratives sans donnees utiles | Bruit |
| Creer un nouveau pattern pour un cas deja couvert | Incoherence |
| Mettre une logique metier dans l'interface | Mauvaise architecture |
| Utiliser des textes trop longs dans les boutons | UI lourde |
| Faire dependre le Desktop directement de PostgreSQL | Violation architecture |

### 20.3 Regles de coherence

- Meme action, meme libelle, meme position.
- Meme statut, meme couleur, meme icone.
- Meme type de page, meme structure.
- Meme erreur, meme ton, meme niveau de detail.

---

## 21. Roadmap UI

### 21.1 Version 0.1

Objectif :

- shell Desktop ;
- navigation ;
- theme sombre ;
- page Websites ;
- dashboard initial ;
- ApiClient.

### 21.2 Version 0.2

Objectif :

- tables avancees ;
- filtres ;
- formulaires de creation ;
- empty/error states standardises ;
- status API plus complet.

### 21.3 Version 0.3

Objectif :

- modules Keywords, Entities, Competitors ;
- vues detail ;
- exports ;
- recherche locale.

### 21.4 Version 0.4

Objectif :

- Dashboard analytique ;
- graphiques SEO/GEO ;
- alertes ;
- historique.

### 21.5 Version 0.5

Objectif :

- module GEO ;
- prompts ;
- comparaison modeles IA ;
- citations et sources.

### 21.6 Version 0.6

Objectif :

- crawler ;
- SEO technique ;
- indexation ;
- performances.

### 21.7 Version 0.7

Objectif :

- rapports ;
- generation ;
- planification ;
- preview.

### 21.8 Version 0.8

Objectif :

- administration avancee ;
- permissions ;
- logs ;
- connecteurs API.

### 21.9 Version 0.9

Objectif :

- personnalisation ;
- favoris ;
- recherche globale ;
- raccourcis clavier.

### 21.10 Version 1.0

Objectif :

- experience stable ;
- design system complet ;
- monitoring systeme ;
- documentation UI appliquee ;
- accessibilite verifiee.

---

## 22. Annexes

### 22.1 Glossaire

| Terme | Definition |
|---|---|
| SEO | Optimisation pour les moteurs de recherche |
| GEO | Optimisation de la visibilite dans les moteurs d'IA generative |
| LLM | Large Language Model |
| Website | Site web suivi par la plateforme |
| Entity | Entite ou marque du groupe |
| Prompt | Instruction envoyee a un modele IA |
| Citation | Mention ou source fournie par une IA |
| Crawl | Exploration automatisee d'un site |
| KPI | Indicateur cle de performance |
| CWV | Core Web Vitals |

### 22.2 Conventions de nommage UI

| Element | Convention |
|---|---|
| Module | Nom court en anglais si deja present dans l'app |
| Page | Titre singulier ou pluriel selon contenu |
| Bouton primaire | Verbe d'action |
| Filtre | Nom du critere |
| Table | Colonnes courtes |
| Badge | 1 a 2 mots |

### 22.3 Abreviations autorisees

| Abreviation | Usage |
|---|---|
| SEO | Tous contextes |
| GEO | Tous contextes |
| IA | Interface francaise |
| API | Tous contextes |
| URL | Tous contextes |
| LLM | Modules experts |
| CWV | Modules SEO technique |

### 22.4 Checklist UI

| Controle | OK |
|---|---|
| La page respecte le layout global | |
| Le module actif est visible | |
| Les couleurs viennent de la charte | |
| Les composants utilisent les patterns existants | |
| Les textes sont lisibles en theme sombre | |
| Les etats loading/error/empty sont prevus | |
| Les actions principales sont visibles | |
| Les actions destructives sont confirmees | |
| Les tables ont tri, filtres et pagination si necessaire | |
| Les formulaires ont validation et messages | |

### 22.5 Checklist UX

| Controle | OK |
|---|---|
| Le parcours principal est realisable sans aide | |
| Les erreurs expliquent quoi faire | |
| Les donnees critiques indiquent leur source ou date | |
| Les filtres actifs sont visibles | |
| La navigation ne provoque pas de perte de contexte inutile | |
| Le langage est adapte aux utilisateurs internes | |
| Les profils non techniques peuvent comprendre les vues de synthese | |
| Les profils experts peuvent acceder au detail | |

### 22.6 Checklist avant Pull Request

| Controle | OK |
|---|---|
| La modification respecte ce document UI/UX | |
| Aucun nouveau pattern n'est introduit sans justification | |
| Les composants sont reutilisables | |
| Les textes sont en francais ou conformes aux modules existants | |
| Les contrastes sont suffisants | |
| La navigation clavier n'est pas bloquee | |
| Les tailles Desktop principales sont verifiees | |
| Les etats API indisponible sont geres | |
| Les erreurs backend sont affichees proprement | |
| Les captures ou verifications visuelles sont disponibles si necessaire | |

### 22.7 Exemple de page conforme

```text
+----------------------------------------------------------------------------------+
| Websites > Liste des sites                                  [Recherche] [Admin]  |
+----------------------+-----------------------------------------------------------+
| Veille SEO-GEO       | Websites                                      [Ajouter]   |
| v0.1.0               | Sites suivis par entite, statut et CMS.                  |
| API OK               |                                                           |
| PostgreSQL OK        | [Rechercher] [Entite v] [Actif v] [CMS v] [Exporter]     |
|                      |                                                           |
| ● Dashboard          | Nom          URL              Actif Entite CMS Actions    |
| ● Websites           | Europ-Arm    https://...      Oui   Europ  WP  ...        |
|   Entities           | SIMAC        https://...      Oui   SIMAC  -   ...        |
|   Keywords           |                                                           |
|   Competitors        | 1-20 sur 128                              < 1 2 3 >       |
+----------------------+-----------------------------------------------------------+
| API OK | PostgreSQL OK | Derniere sync 09:42 | Admin                              |
+----------------------------------------------------------------------------------+
```

### 22.8 Decision finale

Cette specification est la reference UI/UX officielle du projet Veille SEO-GEO Groupe A.P&Partner.
Toute nouvelle interface doit :

- respecter la structure generale ;
- utiliser les composants decrits ;
- suivre la charte graphique ;
- prevoir les etats de chargement, erreur et vide ;
- rester compatible avec une evolution modulaire ;
- servir la productivite avant la decoration.
