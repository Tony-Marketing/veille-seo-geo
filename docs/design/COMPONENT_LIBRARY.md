# Component Library - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit la bibliothèque officielle des composants d'interface de **Veille SEO-GEO Groupe A.P&Partner**.

Il s'applique à l'interface Desktop PySide6 actuelle et au futur frontend React. Il complète `DESIGN_SYSTEM.md`, `COLOR_PALETTE.md` et `ICON_GUIDELINES.md` sans les remplacer.

Le document définit les intentions, variantes, états, règles d'usage, comportements et contraintes d'accessibilité des composants. Il ne fournit pas d'implémentation technique, ne crée aucun fichier de tokens et n'impose aucune bibliothèque UI.

## 2. Principes généraux

Les composants doivent rester cohérents, réutilisables, sobres et prévisibles.

Principes obligatoires :

- composants cohérents entre modules ;
- composants réutilisables avant composants spécifiques ;
- sobriété visuelle ;
- lisibilité prioritaire en contexte dense ;
- comportements prévisibles ;
- accessibilité dès la conception ;
- alignement Desktop PySide6 / futur React ;
- séparation entre intention de composant et implémentation technique ;
- éviter les composants spécifiques inutiles.

Un nouveau composant ne doit être créé que si un composant existant ne couvre pas correctement le besoin.

## 3. Documents liés

| Document | Rôle pour les composants |
|---|---|
| `docs/design/DESIGN_SYSTEM.md` | fixe les principes UI, les états et les familles de composants |
| `docs/design/COLOR_PALETTE.md` | définit les couleurs, états, domaines et règles de contraste |
| `docs/design/ICON_GUIDELINES.md` | définit l'usage des icônes, tailles, libellés et accessibilité |
| `docs/UI_UX.md` | fournit la référence UI/UX générale et les patterns déjà posés |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | cadre les widgets Desktop, pages, shell et ApiClient |
| `docs/architecture/API_ARCHITECTURE.md` | définit les contrats API, pagination, erreurs et états consommés par l'UI |
| `docs/architecture/SECURITY.md` | impose le masquage des secrets, confirmations et prudence sur actions sensibles |
| `docs/architecture/LOGGING.md` | définit les niveaux de logs, trace ID et messages sans fuite technique |

Tout composant qui affiche une erreur, un secret, un log ou un état API doit respecter les documents de sécurité et logging.

## 4. Niveaux de composants

Les composants sont classés par niveau d'usage pour limiter les doublons.

| Niveau | Exemples | Usage | Attention |
|---|---|---|---|
| Atomiques | bouton, icône, badge, tooltip | actions et signaux simples | ne pas multiplier les variantes |
| Formulaire | input, textarea, select, switch | saisie et validation | labels et erreurs obligatoires |
| Navigation | sidebar, tabs, breadcrumbs | repérage et déplacement | stabilité des libellés |
| Feedback | alertes, toasts, empty states | retour utilisateur | messages actionnables |
| Données | tables, pagination, filtres | listes et exploration | densité maîtrisée |
| Dashboard | KPI cards, panels, graphiques | synthèse et pilotage | éviter le décoratif |
| Sécurité | confirmations, secret field, access denied | actions sensibles | masquage et confirmation |
| Métier SEO/GEO | keyword table, AI visibility card | données spécialisées | sens métier explicite |
| Layout | header, top bar, split view | structure d'écran | ne pas porter de logique métier |

## 5. États communs à tous les composants

Chaque composant interactif doit prévoir ses états principaux.

| État | Comportement visuel | Comportement fonctionnel | Accessibilité |
|---|---|---|---|
| Default | apparence standard | disponible | libellé lisible |
| Hover | accent discret | indique interaction possible | ne remplace pas focus |
| Focus | contour visible | navigation clavier active | obligatoire |
| Active | état pressé ou sélectionné | action en cours ou vue active | annoncé par texte si nécessaire |
| Disabled | contraste réduit | non interactif | raison visible si utile |
| Loading | spinner, skeleton ou texte | action temporairement bloquée | opération nommée |
| Success | couleur succès et message | action réussie | ne pas dépendre uniquement du vert |
| Warning | couleur warning et contexte | attention non bloquante | message clair |
| Error | couleur erreur et message | correction requise | erreur associée au champ ou composant |
| Empty | contenu absent expliqué | action alternative possible | non confondu avec erreur |
| Selected | sélection visible | élément inclus dans action | texte ou état perceptible |
| Readonly | valeur consultable | non modifiable | différent de disabled |

## 6. Boutons

Les boutons déclenchent des actions. Leur variante doit refléter l'importance et le risque.

| Variante | Usage | Couleur | Icône éventuelle | Libellé | États requis | Accessibilité | Anti-patterns |
|---|---|---|---|---|---|---|---|
| Primaire | action principale d'une zone | primary | optionnelle | obligatoire | hover, focus, loading, disabled | focus visible | plusieurs primaires concurrents |
| Secondaire | alternative ou annulation | neutre | optionnelle | obligatoire | hover, focus, disabled | contraste suffisant | remplacer le primaire |
| Danger | suppression ou action sensible | danger | possible | obligatoire | hover, focus, loading, disabled | confirmation obligatoire | icône seule |
| Discret | action secondaire compacte | neutre | possible | recommandé | hover, focus | tooltip si icône seule | action critique |
| Texte | lien d'action léger | primary ou neutre | rarement | obligatoire | hover, focus | zone cliquable suffisante | faux lien externe |
| Icône seul | toolbar, table, compact | neutre ou état | obligatoire visuellement | non visible | hover, focus, disabled | tooltip obligatoire | action ambiguë |
| Avec icône | action importante ou non évidente | selon variante | oui | obligatoire | hover, focus | icône décorative ignorée par lecteur | icône sans texte |
| Loading | action en cours | selon variante | spinner possible | conservé | loading | annonce de progression si possible | changer brutalement la taille |
| Désactivé | action indisponible | disabled | optionnelle | visible | disabled | raison si nécessaire | masquer l'action sans contexte |

Règles :

- une zone ne doit pas contenir plusieurs boutons primaires concurrents ;
- une action destructive ne doit jamais être représentée par une icône seule ;
- une action destructive doit demander confirmation ;
- les libellés utilisent des verbes précis : `Ajouter`, `Enregistrer`, `Exporter`, `Supprimer`.

## 7. Champs texte

Les champs texte servent à saisir une valeur courte : nom, URL, email, mot-clé, identifiant, recherche.

Structure recommandée :

- label visible ;
- champ ;
- aide contextuelle si nécessaire ;
- message d'erreur proche du champ ;
- état focus visible ;
- indication obligatoire si applicable.

Variantes :

- champ texte simple ;
- champ obligatoire ;
- champ optionnel ;
- champ readonly ;
- champ disabled ;
- champ avec aide ;
- champ avec erreur ;
- champ avec validation ;
- champ de recherche.

Règles :

- le placeholder ne remplace jamais le label ;
- le champ readonly reste lisible mais non modifiable ;
- le champ disabled indique une indisponibilité fonctionnelle ;
- l'erreur doit expliquer la correction attendue ;
- le champ de recherche doit pouvoir être réinitialisé.

## 8. Textarea

La textarea sert aux textes longs : notes, briefs, descriptions, commentaires, consignes de rapport ou requêtes GEO.

Règles :

- taille initiale suffisante pour le contexte ;
- redimensionnement ou hauteur adaptée si nécessaire ;
- compteur de caractères si une limite existe ;
- aide contextuelle courte ;
- validation lisible ;
- message d'erreur proche ;
- éviter les zones trop hautes dans les modales.

Cas d'usage :

- brief contenu ;
- description de concurrent ;
- note de rapport ;
- prompt ou requête GEO ;
- commentaire d'administration.

Anti-patterns :

- textarea pour une valeur courte ;
- texte long dans une modale étroite ;
- compteur sans limite réelle ;
- erreur uniquement en rouge sans message.

## 9. Select et listes déroulantes

Les selects servent à choisir une valeur dans une liste bornée.

| Type | Usage | Comportement | Précautions |
|---|---|---|---|
| Select simple | statut, module, rôle | une valeur | options courtes |
| Select multi | filtres multiples | plusieurs valeurs | afficher tags actifs |
| Select avec recherche | liste longue | recherche interne | état vide |
| Select de site | contexte global | site actif | conserver pendant navigation |
| Select de période | dashboard, reporting | période prédéfinie | dates visibles |
| Select de statut | table, filtres | filtre état | valeurs cohérentes |
| Select de module | logs, admin | périmètre | éviter doublons |
| État vide | aucune option | message explicite | action si possible |
| Chargement | options API | loader discret | ne pas bloquer sans texte |
| Erreur API | options indisponibles | message et retry | ne pas afficher liste vide comme succès |

Un select ne doit pas servir à masquer une action importante.

## 10. Checkbox, radio et switch

Ces composants ont des intentions différentes.

| Composant | Usage recommandé | Usage interdit | Exemple |
|---|---|---|---|
| Checkbox | sélection multiple ou option indépendante | choix exclusif unique | sélectionner plusieurs sites |
| Radio | choix unique parmi options visibles | liste longue | type de rapport |
| Switch | activation immédiate d'un état binaire | action destructive | activer un connecteur |

Règles :

- chaque contrôle a un libellé visible ;
- un switch ne doit pas déclencher une opération risquée sans confirmation ;
- les radios doivent afficher toutes les options principales ;
- les checkboxes groupées doivent avoir un titre de groupe ;
- les erreurs doivent être affichées au niveau du groupe si nécessaire.

## 11. Date picker et sélection de période

Les composants de date servent aux analyses, rapports, logs et dashboards.

Variantes :

- date simple ;
- plage de dates ;
- période prédéfinie ;
- comparaison de période ;
- période dashboard ;
- période reporting.

Règles :

- afficher la période active en clair ;
- conserver les dates lors du changement de filtre proche ;
- permettre une réinitialisation ;
- signaler les plages invalides ;
- éviter les formats ambigus ;
- garder la navigation clavier possible.

Une comparaison de période doit indiquer explicitement la période de référence.

## 12. Badges et tags

Les badges indiquent un statut ou domaine. Les tags représentent des filtres, mots-clés ou catégories.

| Type | Usage | Règle |
|---|---|---|
| Badge de statut | actif, erreur, en attente | texte obligatoire |
| Badge SEO | domaine SEO | accent SEO sobre |
| Badge GEO | domaine GEO | accent GEO sobre |
| Badge sécurité | accès, secret, permission | seulement si utile |
| Badge configuration | connecté, incomplet | état lisible |
| Badge rôle | admin, éditeur, lecteur | ne pas utiliser danger par défaut |
| Tag de filtre | filtre actif | supprimable si possible |
| Tag de mot-clé | keyword, intention | court |
| Tag concurrent | entité concurrente | couleur stable |
| Tag plateforme IA | ChatGPT, Gemini, Claude, Copilot, Perplexity | repère interne, pas logo copié |

Règles :

- ne pas multiplier les badges ;
- chaque badge doit avoir une signification claire ;
- couleur + texte obligatoire pour les statuts importants.

## 13. Tooltips

Les tooltips complètent une information courte. Ils ne doivent pas cacher une information indispensable.

Usages autorisés :

- bouton icône seul ;
- aide courte ;
- valeur tronquée ;
- KPI complexe ;
- donnée technique courte ;
- statut nécessitant une précision.

À éviter :

- tooltip avec paragraphe long ;
- instruction critique uniquement dans un tooltip ;
- secret ou clé complète dans un tooltip ;
- tooltip qui remplace un message d'erreur.

Checklist tooltip :

- [ ] Le texte est court.
- [ ] Le tooltip explique une icône ou valeur.
- [ ] L'information critique reste visible ailleurs.
- [ ] Aucun secret n'est affiché.
- [ ] Le tooltip est accessible au clavier si nécessaire.

## 14. Cards

Les cards regroupent une information cohérente. Elles ne doivent pas devenir des conteneurs décoratifs.

Variantes :

- carte simple ;
- carte d'information ;
- carte de détail ;
- carte de configuration ;
- carte dashboard ;
- carte d'état vide ;
- carte d'action.

Structure :

- titre court ;
- contenu principal ;
- métadonnées si utiles ;
- action secondaire éventuelle ;
- état visible si applicable.

Règles :

- densité adaptée au contexte ;
- bordures discrètes ;
- ombre légère si nécessaire ;
- pas de card dans une card ;
- pas de carte vide décorative ;
- action principale claire si carte d'action.

## 15. KPI Cards

Une KPI card synthétise une métrique importante.

Elle contient :

- titre ;
- valeur principale ;
- variation ;
- période ;
- contexte ;
- icône éventuelle ;
- couleur d'état ;
- lien vers détail ;
- tooltip éventuel.

Exemple conceptuel :

```text
[icône SEO] Clics SEO
12 480
+8 % vs période précédente
Période : 30 jours
Action : Voir les mots-clés
```

Matrice KPI :

| Type KPI | Donnée | Sens de lecture | Couleur | Attention métier |
|---|---|---|---|---|
| SEO trafic | clics | hausse souvent positive | succès si qualifié | vérifier période |
| SEO erreurs | erreurs techniques | baisse positive | succès ou erreur | hausse = risque |
| GEO visibilité | présence IA | hausse positive | succès | préciser modèles |
| GEO concurrents | mentions concurrentes | hausse à surveiller | warning | pas danger automatique |
| Configuration | connecteurs actifs | complet positif | succès | incomplet warning |
| API | disponibilité | indisponible critique | erreur | action de retry |

## 16. Tables

Les tables portent les listes et données détaillées.

Variantes :

- table simple ;
- table dense ;
- table avec tri ;
- table avec filtres ;
- table paginée ;
- table avec actions par ligne ;
- table avec sélection ;
- table d'administration ;
- table SEO ;
- table GEO ;
- table logs.

Règles :

- colonnes texte alignées à gauche ;
- colonnes numériques alignées à droite ;
- badges en cellule avec texte ;
- icônes en cellule avec tooltip si nécessaire ;
- actions par ligne à droite ;
- actions groupées visibles après sélection ;
- état vide distinct de l'état loading ;
- état erreur avec message et action possible ;
- pagination visible pour listes longues ;
- densité compacte mais lisible.

Checklist table :

- [ ] Colonnes critiques visibles.
- [ ] Tri visible sur colonne active.
- [ ] Filtres accessibles.
- [ ] Pagination indique total et taille.
- [ ] Actions de ligne cohérentes.
- [ ] État vide prévu.
- [ ] État loading prévu.
- [ ] État erreur prévu.
- [ ] Données numériques alignées à droite.
- [ ] Secrets jamais affichés en clair.

## 17. Filtres et recherche

Les filtres réduisent la liste sans changer le contexte.

Matrice filtres :

| Contexte | Type de filtre | Affichage | Règle |
|---|---|---|---|
| Dashboard | site, période, module | barre globale | visible en haut |
| Table | recherche, statut, tag | toolbar | conserver pagination si pertinent |
| Logs | niveau, période, module | toolbar dense | niveaux explicites |
| SEO | site, keyword, position | filtres avancés | unités visibles |
| GEO | modèle IA, prompt, période | filtres avancés | plateformes nommées |
| Administration | rôle, statut, permission | filtres table | sécurité claire |
| Filtres actifs | tags | sous toolbar | suppression rapide |
| Réinitialisation | bouton discret | toolbar | action explicite |

La recherche doit afficher un état aucun résultat distinct d'un état aucune donnée.

## 18. Pagination

La pagination encadre les listes volumineuses et reflète les contrats API sans les implémenter.

Règles :

- afficher la plage visible et le total ;
- proposer une taille de page standard ;
- indiquer l'état chargement lors du changement de page ;
- conserver les filtres actifs ;
- afficher un état absence de résultat si la page est vide ;
- rester cohérent entre Desktop et React ;
- éviter une pagination invisible en bas d'une table longue sans rappel.

La pagination côté API est un comportement backend ; le composant UI affiche seulement le résultat, les contrôles et les états.

## 19. Tabs et navigation secondaire

Les tabs organisent des sous-sections proches.

Usages :

- page détail ;
- administration ;
- configuration ;
- rapports ;
- vues SEO/GEO liées.

Règles :

- l'onglet actif est visible ;
- l'onglet disabled explique la raison si nécessaire ;
- ne pas dépasser un nombre élevé d'onglets visibles ;
- ne pas remplacer la navigation principale ;
- conserver les filtres quand l'utilisateur change d'onglet proche.

## 20. Sidebar et navigation principale

La sidebar est le repère principal.

Structure :

- logo ou nom produit ;
- groupes de modules ;
- icônes et libellés ;
- état actif ;
- éventuel état réduit futur ;
- indicateurs de statut seulement si utiles.

Règles :

- libellés visibles par défaut ;
- entrée = objectif métier clair ;
- éviter les entrées ambiguës ;
- ne pas placer d'action destructive dans la sidebar ;
- conserver une navigation stable entre modules ;
- éviter plus de deux niveaux.

## 21. Header / Top bar

Le header ou top bar fournit le contexte de la page.

Éléments possibles :

- titre de page ;
- action principale ;
- sélecteur de site ;
- période ;
- état API ;
- profil utilisateur éventuel ;
- notifications éventuelles ;
- recherche globale future.

Règles :

- ne pas surcharger la top bar ;
- garder les actions principales au même endroit ;
- rendre l'état API lisible sans détails techniques ;
- conserver la cohérence entre écrans.

## 22. Breadcrumbs

Les breadcrumbs aident dans les vues profondes.

Usages :

- page détail ;
- sous-section administration ;
- rapport détaillé ;
- configuration avancée.

Règles :

- libellés courts ;
- hiérarchie réelle ;
- pas de breadcrumb sur les écrans de premier niveau ;
- dernier élément non cliquable si page active ;
- éviter les chemins artificiels.

## 23. Modales

Les modales doivent rester courtes et ciblées.

Variantes :

- modale de confirmation ;
- modale de formulaire court ;
- modale d'information ;
- modale d'erreur bloquante ;
- modale d'action destructive.

Règles :

- contenu long = page dédiée ;
- action destructive = confirmation explicite ;
- titre clair ;
- actions en bas ;
- fermeture explicite ;
- focus piégé dans la modale ;
- touche d'échappement possible sauf action critique en cours ;
- message d'impact visible pour actions sensibles.

Anti-patterns :

- table complexe dans une modale ;
- formulaire long ;
- plusieurs étapes cachées ;
- action danger sans libellé.

## 24. Alertes

Les alertes signalent un état important.

| Type | Icône | Couleur | Message | Action possible |
|---|---|---|---|---|
| Succès | succès | success | confirmation courte | ouvrir détail |
| Information | info | info | contexte neutre | consulter |
| Avertissement | warning | warning | risque non bloquant | corriger |
| Erreur | error | error | cause et action | réessayer |
| Sécurité | verrou/bouclier | security | droits ou secret | demander accès |
| Configuration incomplète | réglage warning | warning | élément manquant | compléter |
| API indisponible | serveur barré | error | dépendance indisponible | réessayer |
| Import/export | fichier | info/warning | progression ou résultat | voir détail |
| Sauvegarde | spinner/coche | info/success | état action | attendre |

Une alerte vague est un anti-pattern.

## 25. Toasts et notifications courtes

Les toasts confirment une action brève ou signalent un événement non bloquant.

Usages :

- succès de sauvegarde ;
- tâche lancée ;
- échec mineur ;
- action copiée ;
- export demandé.

Règles :

- durée courte pour succès ;
- persistant ou action visible pour erreur importante ;
- ne pas remplacer une alerte bloquante ;
- texte court ;
- action optionnelle si utile ;
- ne pas afficher de détail technique sensible.

## 26. Empty states

Un empty state explique l'absence de contenu.

| Contexte | Message | Action recommandée | Icône |
|---|---|---|---|
| Aucune donnée | `Aucune donnée disponible.` | vérifier période ou importer | neutre |
| Aucun résultat | `Aucun résultat ne correspond aux filtres.` | réinitialiser filtres | recherche |
| Aucun site configuré | `Aucun site n'est configuré.` | ajouter un site | sites |
| Aucune donnée SEO | `Aucune donnée SEO pour cette période.` | changer période | SEO |
| Aucune donnée GEO | `Aucune donnée GEO disponible.` | lancer une analyse si prévu | GEO |
| Configuration absente | `Configuration incomplète.` | compléter paramètres | warning |
| Accès refusé | `Accès refusé.` | demander les droits | sécurité |

Un empty state n'est pas une erreur technique.

## 27. Loading states

Les états de chargement doivent nommer l'opération.

Variantes :

- chargement page ;
- chargement table ;
- chargement carte KPI ;
- chargement bouton ;
- chargement import/export ;
- chargement API ;
- skeleton éventuel ;
- spinner éventuel ;
- texte d'attente.

Règles :

- utiliser skeleton pour contenu structuré ;
- utiliser spinner pour action courte ;
- afficher un texte pour opérations longues ;
- désactiver uniquement les actions concernées ;
- ne pas bloquer toute l'interface si une zone seulement charge.

## 28. Error states

Les erreurs doivent être utiles et sûres.

Types :

- erreur API ;
- erreur validation ;
- erreur droits ;
- erreur configuration ;
- erreur réseau ;
- erreur import/export ;
- erreur logs ;
- erreur partielle.

Règles :

- message utilisateur clair ;
- action possible ;
- détail technique masqué ;
- trace ID éventuel ;
- aucun secret ;
- conserver les données déjà chargées si possible ;
- distinguer erreur totale et données partielles.

Exemple : `Impossible de charger les sites. API indisponible. Réessayez.`

## 29. Confirmations

Les confirmations protègent les actions sensibles.

| Action | Confirmation requise | Niveau de risque | Texte attendu |
|---|---:|---|---|
| Suppression | Oui | élevé | nommer la ressource supprimée |
| Import sensible | Oui | moyen à élevé | expliquer l'impact |
| Export sensible | Oui si données sensibles | moyen | rappeler permissions |
| Reset configuration | Oui | élevé | indiquer effet |
| Changement de droits | Oui | élevé | nommer utilisateur/rôle |
| Modification clé API | Oui selon impact | élevé | secret masqué |
| Action irréversible | Oui | critique | confirmation explicite |

Une confirmation ne doit pas être purement visuelle. Le texte doit expliquer le risque.

## 30. Formulaires métier

Matrice formulaires :

| Formulaire | Champs clés | Composants | Précautions UX |
|---|---|---|---|
| Site web | nom, URL, entité, actif | input, select, switch | URL validée |
| Mot-clé | mot-clé, URL cible, priorité | input, select, tags | doublons à signaler |
| Contenu | titre, type, URL, statut | input, textarea, select | texte long lisible |
| Concurrent | nom, domaine, secteur | input, tags | ne pas confondre entité interne |
| Configuration | provider, statut, paramètres | cards, selects, switches | prudence sur changements |
| Clé API | provider, clé masquée | secret field, test button | jamais afficher complète |
| Utilisateur | nom, email, statut | inputs, select | droits non implicites |
| Rôle/permission | rôle, permissions | checkbox group, table | confirmation si sensible |
| Requête GEO | prompt, modèle, période | textarea, select | ne pas copier logos IA |

## 31. Composants SEO

Matrice SEO :

| Composant SEO | Usage | Donnée affichée | Attention |
|---|---|---|---|
| Carte performance SEO | synthèse | clics, impressions, CTR | sens métier |
| Table mots-clés | analyse | keyword, position, URL | tri et filtres |
| Badge position | statut position | rang, variation | hausse/baisse contextualisée |
| Badge intention | classification | information, transactionnel | ne pas surcharger |
| URL cible | destination | URL | tronquer proprement |
| Page type | classification | marque, catégorie, produit | libellé stable |
| Opportunité SEO | recommandation | action priorisée | warning non erreur |
| Erreur SEO | audit | anomalie | rouge si réelle |
| Évolution de position | tendance | variation | flèche + valeur |

## 32. Composants GEO

Les composants GEO suivent ChatGPT, Gemini, Claude, Copilot et Perplexity comme plateformes internes de suivi. Ils ne doivent pas copier leurs logos, couleurs ou chartes graphiques.

Matrice GEO :

| Composant GEO | Usage | Donnée affichée | Prudence |
|---|---|---|---|
| Carte visibilité IA | synthèse | score, présence, période | expliquer modèle |
| Table requêtes GEO | analyse | prompt, modèle, résultat | texte long maîtrisé |
| Résultat par plateforme IA | comparaison | ChatGPT, Gemini, Claude, Copilot, Perplexity | repères internes |
| Badge présence/absence | statut | mention ou absence | absence non rouge par défaut |
| Score visibilité | KPI | score interne | échelle visible |
| Citation marque | preuve | source, extrait court | contexte nécessaire |
| Citation concurrent | veille | concurrent cité | warning selon objectif |
| Historique réponse | évolution | dates et changements | période claire |
| Comparaison moteurs IA | benchmark | modèles côte à côte | éviter trop de couleurs |

## 33. Composants configuration

Composants concernés :

- carte configuration ;
- statut clé API ;
- test de connexion ;
- import/export ;
- état configuration incomplète ;
- message secret masqué ;
- action remplacer une clé si cette fonctionnalité existe dans le périmètre futur validé.

Règles :

- secret toujours masqué ;
- statut clair ;
- test de connexion avec résultat explicite ;
- import/export avec prudence ;
- aucune promesse de fonctionnalité non décidée.

## 34. Composants administration

Composants concernés :

- table utilisateurs ;
- table rôles ;
- table permissions ;
- badge admin ;
- statut actif/inactif ;
- action modifier droits ;
- action désactiver ;
- accès refusé.

Règles sécurité UI :

- actions de droits visibles seulement si autorisées ;
- modification sensible confirmée ;
- badge admin sobre, pas danger ;
- accès refusé avec message clair ;
- aucun contournement côté interface.

## 35. Composants logs et observabilité

Composants concernés :

- table logs ;
- filtre niveau ;
- filtre période ;
- trace ID ;
- badge niveau log ;
- détail log ;
- message utilisateur ;
- masquage informations sensibles.

Règles :

- niveau texte obligatoire ;
- couleurs cohérentes avec `COLOR_PALETTE.md` ;
- trace ID copiable si disponible ;
- payload sensible masqué ;
- détail technique séparé du message utilisateur.

## 36. Accessibilité des composants

Les composants doivent être utilisables au clavier et compréhensibles sans couleur seule.

Checklist accessibilité composants :

- [ ] Focus visible.
- [ ] Navigation clavier possible.
- [ ] Labels explicites.
- [ ] Taille cliquable suffisante.
- [ ] Contraste conforme.
- [ ] Message d'erreur accessible.
- [ ] Icônes non seules pour informations critiques.
- [ ] Lecture logique de haut en bas.
- [ ] États non uniquement colorés.
- [ ] Tooltip accessible si nécessaire.

## 37. Cohérence Desktop PySide6 / futur React

Les composants doivent partager la même intention entre Desktop et React.

| Composant | Desktop PySide6 | Futur React | Règle commune |
|---|---|---|---|
| Bouton | widget Qt stylé | composant button | mêmes variantes |
| Input | champ Qt | input contrôlé | label et erreur |
| Select | combo/list Qt | select ou combobox | états API |
| Table | QTable ou widget dédié | table composable | pagination et filtres |
| KPI card | widget card | card React | même structure |
| Alert | banner/status | alert component | message actionnable |
| Modal | dialog Qt | dialog web | focus et confirmation |
| Sidebar | widget navigation | layout nav | mêmes libellés |
| Toast | notification Qt future | toast web | usage court |
| Badge | label stylé | badge component | texte obligatoire |

Différences acceptables : rendu natif, animation, contraintes de framework. Différences non acceptables : libellés, états, sécurité, sens métier.

## 38. Nomenclature recommandée

Les tokens de composants décrivent une intention.

| Token composant | Intention | Usage | Remarque |
|---|---|---|---|
| `component.button.primary` | action principale | header, formulaire | unique par zone |
| `component.button.danger` | action destructive | suppression | confirmation |
| `component.input.text` | saisie courte | formulaires | label requis |
| `component.input.search` | recherche | tables | reset utile |
| `component.table.data` | table standard | listes | pagination |
| `component.card.kpi` | KPI | dashboards | période visible |
| `component.alert.error` | erreur | feedback | action possible |
| `component.badge.status` | statut | table, cards | texte obligatoire |
| `component.modal.confirm` | confirmation | sensible | focus contrôlé |
| `component.dashboard.kpi_grid` | grille KPI | dashboard | densité |
| `component.seo.keyword_table` | table mots-clés | SEO | tri/filtres |
| `component.geo.ai_visibility_card` | visibilité IA | GEO | modèle et période |
| `component.config.secret_field` | secret masqué | configuration | jamais complet |
| `component.logs.level_badge` | niveau log | logs | texte niveau |

Aucun fichier JSON, CSS, QSS, TypeScript ou Python ne doit être créé pour ces tokens à cette étape.

## 39. Anti-patterns

À éviter :

- composants différents pour une même intention ;
- bouton primaire multiple dans une même zone ;
- icône seule pour action destructive ;
- tables sans filtres ;
- formulaires sans message d'erreur clair ;
- modales trop longues ;
- alertes vagues ;
- empty state sans action ;
- couleurs non cohérentes ;
- duplication Desktop/React non maîtrisée ;
- exposition de secrets dans l'interface ;
- composants trop spécifiques dès le départ ;
- états loading bloquant toute l'application sans raison ;
- tooltip contenant une information indispensable ;
- badge sans texte compréhensible.

## 40. Exemples conceptuels

Bouton primaire :

```text
[icône ajouter] Ajouter un site
Variante : primaire. Usage : action principale de la page Sites.
```

Bouton danger avec confirmation :

```text
Supprimer le site
Avant exécution : confirmation nommant le site concerné.
```

Champ texte en erreur :

```text
URL du site *
[https://exemple]
Erreur : Saisissez une URL valide commençant par https://.
```

Carte KPI SEO :

```text
Clics SEO
12 480
+8 % vs période précédente
Période : 30 jours
```

Carte visibilité GEO :

```text
Visibilité IA
42 %
Modèles : ChatGPT, Gemini, Claude
Période : 30 jours
```

Table mots-clés :

```text
Mot-clé | Position | URL cible | Variation | Actions
```

Alerte API indisponible :

```text
API indisponible
Impossible de charger les données. Réessayez ou vérifiez l'état du backend.
```

Empty state aucune donnée GEO :

```text
Aucune donnée GEO disponible.
Modifiez la période ou lancez une analyse si cette action est disponible.
```

Modale confirmation suppression :

```text
Supprimer ce site ?
Cette action retirera le site sélectionné. Confirmez pour continuer.
[Annuler] [Supprimer]
```

Formulaire configuration clé API masquée :

```text
Clé API
sk-************9a2f
[Tester la connexion] [Remplacer]
```

## 41. Checklists finales

| Checklist | Points à valider |
|---|---|
| Composant global | intention claire, variante réutilisée, états prévus, accessibilité, cohérence Desktop/React |
| Bouton | une action primaire par zone, danger confirmé, tooltip si icône seule, loading géré |
| Formulaire | labels visibles, aides utiles, erreurs proches, secrets masqués |
| Table | filtres, tri, pagination, états vide/loading/erreur |
| Dashboard | KPI lisibles, période visible, alertes actionnables, graphiques non décoratifs |
| Modale | contenu court, titre clair, focus géré, action destructive confirmée |
| Alerte | type clair, message utile, action possible, aucun détail sensible |
| SEO | sens métier explicite, positions contextualisées, tables filtrables, couleurs non trompeuses |
| GEO | modèle IA visible, période visible, aucune copie de marque IA, absence de mention sobre |
| Sécurité | secrets masqués, droits explicites, suppression confirmée, accès refusé clair |
| Accessibilité | focus visible, contraste suffisant, libellés accessibles, couleur non seule |
| Desktop/React | même intention, même libellé, même état, même règle de sécurité |

## 42. Conclusion

`COMPONENT_LIBRARY.md` complète `DESIGN_SYSTEM.md`, `COLOR_PALETTE.md` et `ICON_GUIDELINES.md` en définissant les composants UI standards, leurs variantes, états, comportements, usages métier et règles d'accessibilité.

Il servira de référence au futur document `docs/design/UI_UX.md`, qui pourra détailler les parcours et applications écran par écran sans contredire cette bibliothèque.
