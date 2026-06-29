# Design System - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit le système de design officiel de la plateforme interne **Veille SEO-GEO Groupe A.P&Partner**.

Il sert de référence commune pour concevoir, développer et vérifier les interfaces Desktop PySide6 actuelles et le futur frontend React. Il complète les documents UI/UX et architecture existants sans les remplacer.

Le design system a trois objectifs principaux :

- garantir une expérience cohérente entre modules SEO, GEO, administration, configuration, reporting et logs ;
- réduire les décisions visuelles isolées lors des futurs développements ;
- fournir à Codex et aux développeurs une base stable pour produire des écrans lisibles, sûrs et maintenables.

Le document cadre les principes globaux. Les détails de palette, icônes, composants et parcours seront décrits dans des documents spécialisés créés plus tard.

## 2. Périmètre couvert

Le design system couvre toutes les surfaces applicatives internes :

- Desktop PySide6 ;
- futur frontend React ;
- dashboards SEO, GEO, administration et configuration ;
- tables de données ;
- formulaires de création, édition et configuration ;
- pages d'administration ;
- pages de configuration ;
- affichage des logs ;
- écrans liés à la sécurité ;
- modules SEO ;
- modules GEO ;
- reporting ;
- contenus ;
- concurrents ;
- états utilisateur : chargement, vide, erreur, succès, accès refusé et API indisponible.

Le périmètre ne définit pas une bibliothèque graphique obligatoire. Il définit des intentions, des comportements et des règles d'usage qui doivent rester compatibles avec PySide6, React et les contraintes futures du projet.

## 3. Documents liés

Documents existants utilisés comme références :

- `docs/UI_UX.md` ;
- `docs/architecture/DESKTOP_ARCHITECTURE.md` ;
- `docs/architecture/API_ARCHITECTURE.md` ;
- `docs/architecture/SECURITY.md` ;
- `docs/architecture/LOGGING.md`.

Documents design prévus pour approfondissement ultérieur :

- `docs/design/COLOR_PALETTE.md` ;
- `docs/design/ICON_GUIDELINES.md` ;
- `docs/design/COMPONENT_LIBRARY.md` ;
- `docs/design/UI_UX.md`.

Ces futurs documents ne sont pas créés par cette étape. Ils devront rester cohérents avec le présent socle.

## 4. Philosophie visuelle

L'interface doit ressembler à un outil de travail interne, pas à une page marketing. Elle doit être professionnelle, sobre, lisible, analytique et orientée données.

Les écrans peuvent être denses, car le produit manipule de nombreuses informations SEO, GEO, techniques et administratives. Cette densité doit rester maîtrisée par une hiérarchie claire, des espacements réguliers, des libellés courts et des états explicites.

La philosophie visuelle repose sur les principes suivants :

- les données utiles passent avant la décoration ;
- les éléments visuels servent la compréhension ;
- les modules partagent des repères communs ;
- les écrans critiques privilégient la précision et la sécurité ;
- les écrans de reporting privilégient la lecture et la synthèse ;
- les actions destructives, sensibles ou administratives sont visuellement distinguées.

L'interface ne doit pas être gadget, spectaculaire ou décorative. Elle doit supporter une utilisation quotidienne par des profils marketing, SEO, direction, contenu, administration et technique.

## 5. Inspirations UI

Les inspirations sont conceptuelles et n'imposent aucune dépendance :

- dashboards SaaS B2B pour la lecture rapide des KPI ;
- consoles d'administration pour les permissions, paramètres et actions sensibles ;
- outils SEO pour les listes filtrables, URLs, mots-clés et tendances ;
- outils de monitoring pour les états système, alertes, logs et incidents ;
- outils d'analytics pour les périodes, comparaisons et graphiques ;
- interfaces de reporting pour les synthèses lisibles ;
- interfaces métier internes pour la stabilité, la sobriété et la productivité.

Les inspirations doivent être adaptées au contexte du projet. Une vue SEO peut être dense et analytique ; une vue de rapport doit être plus lisible ; une vue d'administration doit mettre la sécurité et la traçabilité au premier plan.

## 6. Principes d'interface

Les principes suivants s'appliquent à toutes les surfaces :

- priorité à l'information utile : chaque zone doit porter une donnée, un contexte ou une action ;
- hiérarchie visuelle claire : titre, filtres, contenu, actions et feedback doivent être immédiatement identifiables ;
- navigation stable : l'utilisateur doit toujours savoir dans quel module il se trouve ;
- actions explicites : les boutons utilisent des verbes compréhensibles ;
- feedback utilisateur systématique : toute action longue, réussie, échouée ou interdite doit produire un retour visible ;
- prévention des erreurs : confirmations, validations et séparations visuelles limitent les actions accidentelles ;
- cohérence des libellés : une même action garde le même nom dans tous les modules ;
- réduction de la charge cognitive : ne pas multiplier les variantes de composants sans raison ;
- lisibilité des données : alignements, unités, dates, périodes et statuts doivent être explicites ;
- séparation entre consultation, édition et action destructive.

Une page ne doit pas mélanger lecture, édition et suppression dans une même zone sans séparation claire.

## 7. Ton visuel et éditorial

Le ton de l'interface est sérieux, technique, clair, rassurant, précis et orienté métier.

Les messages doivent aider l'utilisateur à comprendre l'état de l'application et l'action possible. Ils ne doivent pas exposer de détails sensibles, de secrets, de stack trace ou de configuration interne.

Règles de microcopy :

- écrire des messages courts ;
- utiliser des verbes d'action ;
- nommer la ressource concernée quand c'est utile ;
- expliquer les erreurs avec un contexte compréhensible ;
- éviter les messages vagues comme `Une erreur est survenue` sans précision ;
- ne jamais afficher une clé API complète, un token, une chaîne de connexion ou un secret ;
- distinguer message utilisateur et détail technique interne.

Exemples de formulation :

| Situation | Message recommandé | À éviter |
|---|---|---|
| API indisponible | `API indisponible. Réessayez ou vérifiez l'état du backend.` | `Erreur inconnue` |
| Validation URL | `Saisissez une URL valide commençant par https://.` | `Champ incorrect` |
| Accès refusé | `Accès refusé : droits insuffisants pour cette action.` | `403 Forbidden` |
| Secret masqué | `Clé enregistrée : sk-************9a2f` | clé complète |

## 8. Structure générale d'une page

Une page type doit conserver une structure stable :

- sidebar principale ;
- header ou barre supérieure ;
- sélecteur de site quand le module dépend d'un site ;
- filtres globaux ;
- zone de contenu ;
- zone d'actions ;
- zone de feedback ;
- panneau secondaire éventuel pour détail, aide ou historique.

Diagramme ASCII d'une page type :

```text
+------------------+---------------------------------------------------+
| Sidebar          | Header : titre, recherche, utilisateur, statut API |
|                  +---------------------------------------------------+
| Navigation       | Site / période / filtres globaux                   |
| principale       +---------------------------------------------------+
|                  | Actions contextuelles                              |
|                  +---------------------------------------------------+
|                  | Contenu principal : KPI, table, graphe, formulaire |
|                  |                                                   |
|                  +---------------------------+-----------------------+
|                  | Feedback / pagination     | Panneau secondaire   |
+------------------+---------------------------+-----------------------+
```

La sidebar donne le repère permanent. Le contenu varie selon le module, mais les zones de contexte, filtres, actions et feedback doivent rester prévisibles.

## 9. Navigation

La navigation principale donne accès aux modules métier. Une entrée de navigation doit correspondre à un objectif métier clair, par exemple `Dashboard`, `Sites`, `Mots-clés`, `Concurrents`, `Rapports`, `Administration`.

La navigation secondaire sert aux sous-sections d'un module : onglets, vues filtrées, détail, historique ou paramètres locaux.

Règles :

- une entrée de navigation = un objectif métier clair ;
- les noms de modules doivent rester courts ;
- les onglets ne remplacent pas la navigation principale ;
- les sous-sections doivent conserver le contexte du module ;
- un fil d'Ariane peut être utilisé dans les vues profondes ou les pages de détail ;
- les zones d'administration doivent être isolées des vues d'analyse courantes ;
- les actions destructives ne doivent jamais être placées dans la navigation.

## 10. Hiérarchie visuelle

La hiérarchie visuelle organise l'écran par priorité. Elle doit être stable entre modules.

Les titres indiquent le contexte. Les sous-titres précisent l'objectif ou le périmètre. Les blocs regroupent des informations liées. Les cartes résument des indicateurs ou des états. Les tableaux portent les données détaillées. Les alertes signalent les conditions qui demandent attention.

| Priorité | Élément | Usage | Traitement attendu |
|---:|---|---|---|
| 1 | Titre de page | Identifier le module ou l'écran | visible, court, stable |
| 2 | Action principale | Créer, lancer, enregistrer, exporter | unique par zone |
| 3 | Filtres actifs | Site, période, statut, segment | proches du contenu |
| 4 | KPI ou alerte critique | Décision rapide | contraste contrôlé |
| 5 | Table ou détail | Analyse et exploitation | alignement strict |
| 6 | Aide secondaire | Compréhension ponctuelle | discrète, contextuelle |

Un écran ne doit pas contenir plusieurs boutons primaires concurrents dans la même zone. Les actions secondaires doivent être visuellement plus discrètes.

## 11. Couleurs - principes généraux

Le détail complet de la palette sera défini dans `docs/design/COLOR_PALETTE.md`. Le présent document fixe seulement les intentions.

Les couleurs doivent rester sobres, cohérentes et fonctionnelles. Elles ne doivent pas créer une interface trop colorée ni rendre les graphiques décoratifs.

| Usage | Intention | Exemple d'utilisation |
|---|---|---|
| Couleur primaire | Action principale, sélection active, focus | bouton `Enregistrer`, élément de navigation actif |
| Couleur secondaire | Actions alternatives, surfaces secondaires | bouton `Annuler`, panneau secondaire |
| Neutres | Fonds, textes, bordures, séparateurs | layout, table, cartes |
| Succès | Action réussie ou état opérationnel | sauvegarde terminée, API connectée |
| Avertissement | Risque non bloquant ou attention requise | quota proche, configuration incomplète |
| Erreur | Échec, blocage, suppression, danger | API en erreur, suppression |
| Information | Message neutre ou changement d'état | synchronisation lancée |
| SEO | Données et indicateurs SEO | positions, URLs, Core Web Vitals |
| GEO | Données IA génératives | citations, visibilité IA, modèles |
| Sécurité | Droits, accès, secrets, confirmations | accès refusé, clé masquée |
| Configuration | Paramètres et connecteurs | API keys, providers |
| Logs | Gravité, traces, observabilité | INFO, WARNING, ERROR |

Chaque couleur sémantique doit avoir un rôle stable. Ne pas utiliser une couleur d'erreur pour attirer l'attention sur une information neutre.

## 12. Typographie

La typographie doit rester lisible dans des interfaces denses et sur écran desktop. Aucune police propriétaire n'est imposée.

Familles recommandées :

- police système moderne pour l'interface ;
- fallback sans-serif lisible ;
- chasse fixe uniquement pour identifiants, logs, codes, URLs ou valeurs techniques.

Repères :

| Usage | Taille indicative | Règle |
|---|---:|---|
| Titre de page | 24 à 28 px | court, un seul par page |
| Titre de section | 18 à 22 px | hiérarchie claire |
| Texte courant | 13 à 15 px | lisible en densité moyenne |
| Labels | 12 à 14 px | proches du champ |
| Aide contextuelle | 12 à 13 px | discrète mais lisible |
| Message d'erreur | 12 à 14 px | proche du champ ou de la zone |
| Données tabulaires | 12 à 14 px | alignement et chiffres lisibles |

Les données numériques doivent être faciles à comparer. Les unités, périodes et signes de variation doivent être visibles.

## 13. Espacements

Les espacements doivent produire une densité compacte mais lisible.

Principes :

- utiliser une unité de base régulière, par exemple 4 px ou 8 px selon le framework ;
- appliquer des marges de page constantes ;
- séparer clairement les sections ;
- conserver des espacements internes suffisants dans les cartes ;
- rapprocher labels, aides et champs dans les formulaires ;
- garder les lignes de table compactes sans sacrifier la lecture ;
- éviter les grands vides décoratifs sur les vues métier.

Repères :

| Zone | Espacement recommandé | Intention |
|---|---:|---|
| Marge de page | 16 à 24 px | respiration globale |
| Entre sections | 16 à 32 px | séparation visuelle |
| Carte | 12 à 20 px | lisibilité interne |
| Formulaire | 12 à 16 px entre champs | saisie confortable |
| Table | 8 à 12 px horizontal | lecture dense |
| Toolbar | 8 à 12 px | actions groupées |

## 14. Grilles et layouts

Les layouts doivent être prévisibles et adaptés au type de page. Le Desktop est prioritaire, mais les principes doivent rester transposables au futur React.

Matrice de layout :

| Type de page | Structure recommandée | Usage |
|---|---|---|
| Dashboard | filtres globaux, rangée KPI, graphiques, tables de synthèse | pilotage et priorisation |
| Liste | toolbar, filtres, table paginée, actions groupées | sites, mots-clés, concurrents, logs |
| Détail | résumé, tabs, historique, actions contextuelles | analyse d'une ressource |
| Formulaire | sections verticales, validation, actions fixes | création et édition |
| Administration | navigation secondaire, tables, formulaires, confirmations | utilisateurs, rôles, configuration |
| Logs/configuration | filtres précis, table, détail latéral | diagnostic et audit |
| Reporting | période, sections, preview, export | lecture et diffusion interne |

Les dashboards peuvent utiliser plusieurs colonnes. Les formulaires longs doivent préférer une page dédiée plutôt qu'une modale.

## 15. Composants principaux

Les familles de composants à standardiser sont :

- boutons ;
- champs texte ;
- select ;
- checkbox ;
- radio ;
- switch ;
- textarea ;
- date picker ;
- badges ;
- tags ;
- tooltips ;
- cards ;
- KPI cards ;
- tables ;
- modales ;
- alertes ;
- filtres ;
- pagination ;
- breadcrumbs ;
- tabs.

Règles globales :

- un composant doit avoir des états visibles : normal, hover, focus, disabled, loading si applicable ;
- les composants doivent conserver les mêmes libellés et intentions entre Desktop et React ;
- les tooltips expliquent les icônes seules, les valeurs tronquées et les termes techniques ;
- les badges indiquent des statuts courts, pas des phrases ;
- les composants complexes seront détaillés dans `docs/design/COMPONENT_LIBRARY.md`.

## 16. Boutons

Types de boutons :

- primaire : action principale d'une zone ;
- secondaire : action alternative ou non prioritaire ;
- danger : action destructive ou sensible ;
- discret : action secondaire dans une toolbar ou une ligne ;
- icône : action compacte avec tooltip obligatoire si l'icône est seule.

États obligatoires :

- hover ;
- focus visible ;
- disabled ;
- loading pour action longue ;
- pressed si le framework le permet.

Règles d'usage :

- une zone ne doit pas avoir plusieurs actions primaires concurrentes ;
- un bouton danger ne doit jamais déclencher une action destructive sans confirmation ;
- un bouton disabled doit rester lisible et expliquer la raison si nécessaire ;
- les verbes doivent être explicites : `Enregistrer`, `Exporter`, `Relancer`, `Supprimer` ;
- éviter les libellés vagues comme `OK` lorsque l'action peut être nommée.

## 17. Formulaires

Les formulaires privilégient une structure verticale. Les labels sont explicites et toujours visibles. Les champs obligatoires sont signalés clairement.

Règles :

- afficher les aides contextuelles sous le champ ou dans un tooltip ;
- valider localement les formats simples ;
- afficher les erreurs près du champ concerné ;
- conserver les valeurs saisies après erreur ;
- distinguer annulation et sauvegarde ;
- prévenir les pertes de données non enregistrées ;
- confirmer les modifications sensibles ;
- ne jamais afficher de secret en clair après enregistrement.

Checklist formulaire :

- [ ] Le formulaire a un titre clair.
- [ ] Chaque champ a un label explicite.
- [ ] Les champs obligatoires sont identifiés.
- [ ] Les aides sont courtes et utiles.
- [ ] Les validations locales et serveur sont prévues.
- [ ] Les erreurs restent proches du champ.
- [ ] La sauvegarde affiche un état loading.
- [ ] L'annulation est disponible.
- [ ] Les modifications non enregistrées sont protégées.
- [ ] Les secrets sont masqués.

## 18. Tables

Les tables sont centrales pour les modules SEO, GEO, sites, mots-clés, concurrents, administration et logs.

Règles :

- tri visible sur la colonne active ;
- filtres accessibles sans quitter la table ;
- pagination obligatoire pour les longues listes ;
- actions de ligne à droite ;
- actions groupées visibles uniquement quand une sélection existe ;
- colonnes importantes visibles en priorité ;
- colonnes secondaires masquables ou déplaçables à terme ;
- densité compacte mais lisible ;
- état vide explicite ;
- état chargement distinct de l'état vide ;
- état erreur avec action possible ;
- données numériques alignées à droite ;
- dates et périodes au format stable ;
- longues valeurs tronquées avec tooltip ou panneau détail.

Checklist table :

- [ ] La table a une toolbar utile.
- [ ] Les filtres actifs sont visibles.
- [ ] Le tri est compréhensible.
- [ ] La pagination indique le total.
- [ ] Les actions de ligne sont cohérentes.
- [ ] Les actions groupées sont séparées.
- [ ] Les colonnes critiques sont visibles.
- [ ] Les chiffres sont alignés à droite.
- [ ] Les états loading, empty et error sont prévus.
- [ ] Les exports sensibles respectent les permissions.

## 19. Dashboards

Un dashboard sert à comprendre rapidement une situation, pas à accumuler tous les détails disponibles.

Règles :

- afficher un sélecteur de site lorsque les données dépendent d'un site ;
- afficher une période claire ;
- regrouper les filtres globaux ;
- mettre en avant les KPI principaux ;
- montrer les tendances et variations ;
- signaler les alertes utiles ;
- privilégier les graphiques compréhensibles ;
- compléter par des tableaux de synthèse ;
- limiter les composants non actionnables ;
- distinguer dashboard SEO, GEO, configuration et administration.

Matrice dashboard :

| Module | KPI possibles | Attention design |
|---|---|---|
| SEO | positions, pages indexées, erreurs techniques, Core Web Vitals | éviter trop de métriques simultanées |
| GEO | citations IA, présence par modèle, part de visibilité, sources | clarifier modèle, prompt et période |
| Configuration | connecteurs actifs, clés expirées, erreurs de synchronisation | mettre les risques en évidence |
| Administration | utilisateurs, rôles, actions sensibles, accès refusés | ne pas transformer l'admin en dashboard décoratif |
| Reporting | rapports générés, exports, périodes couvertes | privilégier la lecture et le statut |

## 20. Cartes KPI

Une carte KPI doit permettre une lecture immédiate.

Elle contient :

- un titre ;
- une valeur principale ;
- une variation ;
- une période ;
- un contexte ;
- un état positif, négatif ou neutre ;
- un lien vers le détail si utile.

Règles :

- la valeur principale doit être dominante ;
- la variation doit indiquer son sens et sa période ;
- l'état ne doit pas dépendre uniquement de la couleur ;
- les unités doivent être visibles ;
- une carte KPI ne doit pas contenir un paragraphe long.

Exemple conceptuel :

```text
+--------------------------------------+
| Visibilité GEO                       |
| 42 %                                 |
| +6 pts vs période précédente         |
| ChatGPT, Gemini, Claude - 30 jours   |
| Voir le détail                       |
+--------------------------------------+
```

## 21. Visualisation de données

Les visualisations doivent servir la compréhension. Les graphiques décoratifs sont à éviter.

Types autorisés selon usage :

- courbes pour l'évolution temporelle ;
- histogrammes pour comparer des volumes ;
- barres pour comparer des catégories ;
- tableaux comparatifs pour des valeurs précises ;
- heatmaps éventuelles pour repérer des concentrations ;
- graphiques de répartition quand les parts sont utiles ;
- graphiques d'évolution pour tendances SEO/GEO.

Règles SEO/GEO :

- afficher clairement les positions ;
- distinguer visibilité, présence et citation ;
- préciser les modèles IA concernés ;
- afficher la période d'analyse ;
- comparer les concurrents avec des couleurs stables ;
- ne pas masquer les sources des citations IA quand elles existent ;
- éviter les scores opaques sans contexte ;
- privilégier la lecture temporelle pour les évolutions.

## 22. Modales

Les modales doivent rester courtes et ciblées.

Usages autorisés :

- confirmation d'action destructive ;
- formulaire court ;
- avertissement critique ;
- erreur bloquante ;
- détail rapide sans changement de contexte.

Anti-patterns :

- formulaire long dans une modale ;
- table complexe dans une modale ;
- navigation profonde dans une modale ;
- modale qui masque une information nécessaire à la décision ;
- modale utilisée comme page entière.

Quand le contenu est long, utiliser une page dédiée ou un panneau latéral.

## 23. Alertes et feedback utilisateur

Le feedback doit être systématique et proportionné.

| État | Message attendu | Action utilisateur possible |
|---|---|---|
| Succès | confirmation courte et précise | continuer ou ouvrir le détail |
| Avertissement | risque compréhensible, non bloquant | corriger, ignorer si autorisé |
| Erreur | cause probable et action possible | réessayer, corriger, contacter support |
| Information | changement d'état neutre | consulter ou fermer |
| Chargement | opération en cours nommée | attendre ou annuler si possible |
| Sauvegarde en cours | action bloquée temporairement | attendre |
| Données absentes | absence expliquée | créer, modifier filtres, importer |
| API indisponible | dépendance indisponible | réessayer, vérifier backend |
| Accès refusé | droits insuffisants | demander accès |
| Configuration incomplète | élément manquant nommé | compléter la configuration |

Les messages doivent éviter la sur-notification. Un succès courant peut être discret ; une erreur bloquante doit être visible.

## 24. États applicatifs

Les états applicatifs doivent être conçus dès la création d'un écran :

- loading state ;
- empty state ;
- error state ;
- offline ou API indisponible ;
- accès refusé ;
- données partielles ;
- droits insuffisants ;
- configuration absente ;
- import/export en cours.

Un état vide n'est pas une erreur. Il doit expliquer pourquoi aucune donnée n'est affichée et proposer une action utile si elle existe.

Un état de données partielles doit indiquer la source manquante, la période affectée ou la dépendance indisponible.

## 25. Sécurité et design

Les règles UX de sécurité sont obligatoires :

- masquer les secrets ;
- ne jamais afficher les clés API complètes ;
- confirmer les actions sensibles ;
- distinguer lecture, édition et suppression ;
- rendre les droits visibles si cela aide la compréhension ;
- afficher des messages d'accès refusé clairs ;
- rendre les imports/exports non destructifs autant que possible ;
- signaler les effets irréversibles ;
- faire preuve de prudence sur les actions d'administration.

Les écrans liés aux secrets doivent utiliser des valeurs masquées, par exemple `sk-************9a2f`. La copie d'un secret complet ne doit être possible que si le backend et la politique de sécurité l'autorisent explicitement.

## 26. Logging et observabilité côté interface

L'interface doit séparer ce qui est utile à l'utilisateur de ce qui est utile au diagnostic interne.

Règles :

- afficher des messages utilisateur clairs ;
- ne pas exposer directement les erreurs techniques ;
- afficher un identifiant de trace ou de requête si disponible ;
- fournir un feedback utile pour le support ou le debug ;
- ne jamais afficher de secret ;
- ne jamais afficher un dump technique brut ;
- distinguer message utilisateur et détail technique interne.

Exemple de comportement attendu :

- utilisateur : `Impossible de charger les sites. API indisponible.`
- détail support éventuel : `request_id: req_123`
- log interne : erreur technique corrélable, sans secret.

## 27. Accessibilité

L'accessibilité est une contrainte de qualité, pas une option.

Règles :

- respecter des contrastes suffisants ;
- conserver un focus visible ;
- permettre la navigation clavier ;
- fournir des libellés explicites ;
- maintenir des tailles minimales de zones cliquables ;
- accompagner les icônes de texte quand nécessaire ;
- rendre les messages d'erreur accessibles ;
- ne jamais transmettre une information uniquement par la couleur.

Checklist accessibilité :

- [ ] Le focus clavier est visible.
- [ ] Les contrastes sont suffisants.
- [ ] Les champs ont des labels.
- [ ] Les erreurs sont associées au champ concerné.
- [ ] Les boutons icônes ont un tooltip ou un label accessible.
- [ ] Les statuts utilisent texte, icône ou libellé, pas seulement la couleur.
- [ ] Les tables restent lisibles au clavier.
- [ ] Les messages importants sont perceptibles sans animation.

## 28. Cohérence Desktop PySide6 / futur React

Le design system ne dépend pas d'une implémentation graphique spécifique. PySide6 et React peuvent avoir des différences techniques, mais les intentions doivent rester communes.

Matrice de cohérence :

| Principe commun | Desktop PySide6 | Futur React |
|---|---|---|
| Libellés identiques | constantes et widgets réutilisables | composants et dictionnaire UI |
| États applicatifs | pages avec loading, empty, error | composants d'état partagés |
| Feedback | messages et status bar | toasts, banners, inline alerts |
| Navigation stable | sidebar, topbar, pages | layout applicatif, routes |
| Formulaires | widgets Qt structurés | composants contrôlés |
| Tables | QTable/Table widget dédiée | table composable paginée |
| Sécurité | secrets masqués, confirmations | mêmes règles de masquage |
| Logs/support | request_id affichable | request_id affichable |

Les différences acceptables concernent le rendu, les animations, les composants natifs et les contraintes de framework. Les différences non acceptables concernent les libellés, états, règles de sécurité et comportements métier.

## 29. Anti-patterns

À éviter clairement :

- interfaces trop colorées ;
- graphiques décoratifs ;
- tables surchargées sans filtres ;
- messages d'erreur vagues ;
- actions destructives sans confirmation ;
- incohérence entre modules ;
- icônes ambiguës ;
- boutons primaires multiples sur une même zone ;
- modales trop longues ;
- jargon technique inutile côté utilisateur ;
- exposition de secrets ou logs sensibles ;
- valeurs numériques sans unité ;
- périodes non affichées dans les dashboards ;
- états vides confondus avec des erreurs ;
- pages d'administration mélangées aux parcours de consultation courants.

Un nouveau pattern ne doit être introduit que s'il répond à un besoin non couvert par les composants existants ou futurs.

## 30. Checklists finales

Checklist écran :

- [ ] Le module actif est visible.
- [ ] Le titre décrit l'objectif de l'écran.
- [ ] Les actions principales sont explicites.
- [ ] Les filtres actifs sont visibles.
- [ ] Les états loading, empty et error existent.
- [ ] Les libellés sont cohérents avec les autres modules.

Checklist dashboard :

- [ ] Le site et la période sont visibles.
- [ ] Les KPI principaux sont limités et lisibles.
- [ ] Les variations ont un contexte.
- [ ] Les alertes sont actionnables.
- [ ] Les graphiques ne sont pas décoratifs.
- [ ] Les tableaux de synthèse complètent les graphiques.

Checklist table :

- [ ] Tri, filtres et pagination sont disponibles si nécessaire.
- [ ] Les colonnes critiques sont prioritaires.
- [ ] Les actions de ligne sont à droite.
- [ ] Les actions groupées sont séparées.
- [ ] Les valeurs longues sont gérées.
- [ ] Les états vide, chargement et erreur sont distincts.

Checklist formulaire :

- [ ] Structure verticale claire.
- [ ] Labels explicites.
- [ ] Champs obligatoires indiqués.
- [ ] Validations prévues.
- [ ] Erreurs compréhensibles.
- [ ] Protection contre perte de données.
- [ ] Secrets masqués.

Checklist feedback :

- [ ] Les succès sont confirmés.
- [ ] Les erreurs expliquent quoi faire.
- [ ] Les avertissements indiquent le risque.
- [ ] Les opérations longues affichent un état.
- [ ] L'API indisponible est traitée proprement.
- [ ] Un request_id peut être affiché si disponible.

Checklist sécurité UI :

- [ ] Aucun secret complet affiché.
- [ ] Actions sensibles confirmées.
- [ ] Lecture, édition et suppression sont séparées.
- [ ] Accès refusé expliqué.
- [ ] Exports sensibles encadrés.
- [ ] Messages techniques non exposés.

Checklist accessibilité :

- [ ] Focus visible.
- [ ] Contraste suffisant.
- [ ] Navigation clavier possible.
- [ ] Erreurs accessibles.
- [ ] Icônes compréhensibles.
- [ ] Couleur non utilisée seule.

Checklist cohérence Desktop/React :

- [ ] Même libellé pour même action.
- [ ] Même état pour même situation.
- [ ] Même règle de confirmation.
- [ ] Même traitement des secrets.
- [ ] Même structure de navigation.
- [ ] Même logique de feedback.

## 31. Conclusion

Ce document est le socle du système de design de **Veille SEO-GEO Groupe A.P&Partner**.

Il définit les principes communs qui doivent guider la conception du Desktop PySide6, du futur frontend React, des dashboards SEO/GEO, des tables, formulaires, pages d'administration, écrans de configuration, rapports, logs et états applicatifs.

Les documents futurs `COLOR_PALETTE.md`, `ICON_GUIDELINES.md`, `COMPONENT_LIBRARY.md` et `UI_UX.md` détailleront ensuite la palette, les icônes, les composants et les parcours UX sans contredire ce socle.
