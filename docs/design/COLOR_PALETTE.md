# Color Palette - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit la palette de couleurs officielle de **Veille SEO-GEO Groupe A.P&Partner**.

Il complète `docs/design/DESIGN_SYSTEM.md` en détaillant les couleurs, leurs rôles, leurs limites d'usage et les règles de contraste applicables au Desktop PySide6 actuel et au futur frontend React.

Le document reste indépendant de toute bibliothèque graphique. Il ne crée pas de fichier JSON, CSS, QSS ou TypeScript. Il sert de référence fonctionnelle pour les futurs styles QSS, variables CSS, composants React ou tokens de design.

## 2. Principes généraux

Les couleurs servent la compréhension. Elles ne doivent pas décorer l'interface ni remplacer une structure claire.

Principes obligatoires :

- sobriété : limiter les couleurs visibles simultanément ;
- lisibilité : garantir une lecture confortable en interface dense ;
- contraste : préserver la distinction texte, fond, bordures et focus ;
- hiérarchie visuelle : rendre actions, états et priorités identifiables ;
- cohérence multi-modules : même intention, même couleur ;
- information avant esthétique : la couleur doit expliquer un état, un domaine ou une priorité ;
- pas de décoration inutile : éviter les surfaces colorées massives sans valeur métier ;
- accessibilité : ne jamais transmettre une information uniquement par la couleur.

La couleur doit toujours être accompagnée d'un libellé, d'une icône, d'une forme, d'une position ou d'un contexte lorsque l'information est importante.

## 3. Rôle des couleurs dans l'application

Les couleurs interviennent dans plusieurs zones de l'application :

- navigation : module actif, hover, état désactivé ;
- identification des modules : SEO, GEO, reporting, administration ;
- états utilisateur : succès, information, avertissement, erreur, chargement ;
- alertes : API indisponible, configuration incomplète, accès refusé ;
- KPI : tendance, criticité, atteinte d'objectif ;
- tableaux : sélection, hover, erreur, cellule modifiée ;
- graphiques : séries, comparaison, évolution temporelle ;
- badges : statut court, domaine, priorité ;
- configuration : connecteurs, clés masquées, import/export ;
- sécurité : permissions, secrets, rôles, actions destructives ;
- logs : niveaux DEBUG, INFO, WARNING, ERROR, CRITICAL ;
- SEO : positions, indexation, erreurs, opportunités ;
- GEO : visibilité IA, citations, absence de mention, modèles analysés.

Une couleur ne doit pas changer de sens selon l'écran. Si une couleur indique une erreur dans un module, elle ne doit pas indiquer une simple catégorie dans un autre.

## 4. Palette principale

La couleur primaire doit rester sobre, professionnelle et adaptée à un outil analytique. Elle sert aux actions principales, au focus, à la sélection active et aux éléments de navigation prioritaires.

| Nom du token | Valeur hexadécimale proposée | Rôle | Usage recommandé | Usage interdit |
|---|---:|---|---|---|
| `primary` | `#2563EB` | action principale | bouton principal, navigation active | fond de page complet |
| `primary-hover` | `#1D4ED8` | interaction | hover bouton primaire | texte long |
| `primary-active` | `#1E40AF` | état pressé ou sélection forte | bouton pressé, onglet actif | alerte critique |
| `primary-soft` | `#DBEAFE` | fond doux clair | badge léger, sélection claire | texte sur fond blanc sans bordure |
| `primary-soft-dark` | `#172554` | fond doux sombre | sélection en dark mode | surface massive |
| `primary-border` | `#3B82F6` | bordure de focus | focus clavier, contour actif | bordure décorative partout |
| `primary-text` | `#1D4ED8` | texte accentué clair | lien ou action texte | texte de paragraphe long |
| `primary-text-dark` | `#93C5FD` | texte accentué sombre | lien sur fond sombre | KPI critique |

La couleur primaire ne doit pas concurrencer les couleurs d'état. Une erreur reste rouge, même si elle concerne une action primaire.

## 5. Palette secondaire

La palette secondaire sert aux accents non prioritaires, composants secondaires, éléments de contexte et graphiques secondaires.

| Nom du token | Valeur | Rôle | Usage recommandé | Usage interdit |
|---|---:|---|---|---|
| `secondary` | `#475569` | accent neutre | bouton secondaire, bordure forte | action principale |
| `secondary-hover` | `#334155` | hover secondaire | bouton secondaire hover | alerte |
| `secondary-active` | `#1E293B` | état actif secondaire | segment sélectionné secondaire | danger |
| `secondary-soft` | `#F1F5F9` | fond doux clair | panneau secondaire clair | graphique principal |
| `secondary-soft-dark` | `#1E293B` | fond doux sombre | toolbar, header table | erreur ou succès |
| `secondary-border` | `#64748B` | séparation secondaire | contour composant secondaire | focus principal |
| `secondary-text` | `#475569` | texte contextuel | métadonnées, aide secondaire | message critique |
| `secondary-text-dark` | `#CBD5E1` | texte secondaire sombre | label, aide, meta | titre principal |

La palette secondaire doit réduire la charge visuelle, pas ajouter une nouvelle hiérarchie concurrente.

## 6. Neutres

Les neutres structurent l'application. Ils doivent porter la majorité de l'interface.

| Token | Valeur claire | Valeur sombre | Usage |
|---|---:|---:|---|
| `surface.app` | `#F8FAFC` | `#0B1120` | fond application |
| `surface.default` | `#FFFFFF` | `#111827` | contenu principal |
| `surface.raised` | `#F8FAFC` | `#172033` | carte, panneau |
| `surface.subtle` | `#F1F5F9` | `#1F2937` | toolbar, table header |
| `surface.hover` | `#E2E8F0` | `#273449` | hover ligne ou menu |
| `border.default` | `#CBD5E1` | `#253044` | bordure standard |
| `border.subtle` | `#E2E8F0` | `#1E293B` | séparateur léger |
| `separator` | `#E5E7EB` | `#253044` | ligne de séparation |
| `text.primary` | `#0F172A` | `#F8FAFC` | texte principal |
| `text.secondary` | `#475569` | `#CBD5E1` | texte secondaire |
| `text.muted` | `#64748B` | `#94A3B8` | aide, placeholder |
| `text.disabled` | `#94A3B8` | `#64748B` | désactivé |
| `surface.disabled` | `#E5E7EB` | `#334155` | fond désactivé |
| `overlay.modal` | `rgba(15, 23, 42, 0.56)` | `rgba(2, 6, 23, 0.72)` | arrière-plan modal |

Les neutres doivent rester dominants. Les couleurs de domaine et d'état doivent être utilisées comme accents.

## 7. Couleurs d'état

Les couleurs d'état doivent être stables, lisibles et utilisées avec retenue.

| État | Couleur principale | Fond doux | Bordure | Texte | Usage | Exemple de message |
|---|---:|---:|---:|---:|---|---|
| Succès | `#16A34A` | `#DCFCE7` | `#22C55E` | `#166534` | action réussie, état OK | `Configuration enregistrée.` |
| Information | `#0284C7` | `#E0F2FE` | `#38BDF8` | `#075985` | information neutre | `Synchronisation lancée.` |
| Avertissement | `#D97706` | `#FEF3C7` | `#F59E0B` | `#92400E` | risque non bloquant | `Configuration incomplète.` |
| Erreur | `#DC2626` | `#FEE2E2` | `#EF4444` | `#991B1B` | échec ou blocage | `Impossible de charger les données.` |
| Danger | `#B91C1C` | `#FEE2E2` | `#EF4444` | `#7F1D1D` | action destructive | `Suppression définitive à confirmer.` |
| Désactivé | `#94A3B8` | `#E2E8F0` | `#CBD5E1` | `#64748B` | action indisponible | `Action indisponible.` |
| Chargement | `#2563EB` | `#DBEAFE` | `#93C5FD` | `#1D4ED8` | traitement en cours | `Chargement des sites...` |
| En attente | `#7C3AED` | `#EDE9FE` | `#A78BFA` | `#5B21B6` | traitement planifié | `Export en attente.` |

En mode sombre, les fonds doux doivent être remplacés par des variantes sombres des mêmes intentions, afin de conserver le contraste.

## 8. Couleurs par domaine fonctionnel

Les couleurs de domaine identifient un contexte. Elles ne doivent pas colorer massivement les pages.

Matrice domaine :

| Domaine | Couleur d'accent | Usage | Prudence |
|---|---:|---|---|
| SEO | `#10B981` | badges SEO, séries de graphique SEO | ne pas confondre avec succès |
| GEO | `#8B5CF6` | badges GEO, visibilité IA | éviter une interface violette dominante |
| Contenus | `#0EA5E9` | contenus, briefs, pages éditoriales | ne pas remplacer information |
| Concurrents | `#F97316` | comparaison concurrentielle | éviter l'association automatique au danger |
| Reporting | `#6366F1` | rapports, exports, synthèses | garder sobre sur rapports longs |
| Configuration | `#64748B` | paramètres, connecteurs | ne pas masquer les alertes |
| Administration | `#334155` | utilisateurs, rôles, permissions | éviter surfaces trop sombres en mode sombre |
| Sécurité | `#B91C1C` | risque, accès refusé, action sensible | réserver aux vrais risques |
| Logs | `#475569` | journaux, trace, diagnostic | niveau log prioritaire sur domaine |
| Utilisateurs / rôles / permissions | `#0F766E` | gestion RBAC, rôles | ne pas imiter le succès |

Une couleur de domaine peut être utilisée sur une icône, une bordure, un badge ou une série de graphique. Elle ne doit pas devenir le fond principal d'une page.

## 9. Couleurs SEO

Le SEO manipule des métriques dont le sens dépend du contexte. La couleur doit refléter la lecture métier.

Matrice d'usage SEO :

| Donnée SEO | Couleur recommandée | Sens | Prudence |
|---|---:|---|---|
| Position organique améliorée | `#16A34A` | positif | préciser la position gagnée |
| Position organique dégradée | `#DC2626` | négatif | ne pas masquer le volume |
| Clics | `#2563EB` | métrique principale | hausse à interpréter selon période |
| Impressions | `#0EA5E9` | visibilité brute | peut augmenter sans clics |
| CTR | `#7C3AED` | efficacité affichage/clic | baisse possible si impressions montent |
| Pages indexées | `#10B981` | couverture | hausse positive sauf pages faibles |
| Erreurs SEO | `#DC2626` | risque | rouge réservé aux erreurs réelles |
| Opportunités | `#D97706` | action à prioriser | ne pas confondre avec anomalie |
| Progression | `#16A34A` | amélioration | vérifier le sens métier |
| Régression | `#DC2626` | détérioration | afficher valeur et période |

La baisse d'une métrique SEO n'est pas toujours négative. Exemple : baisse des erreurs d'indexation = positif.

## 10. Couleurs GEO

Les couleurs GEO décrivent la visibilité dans les réponses d'IA générative. Elles doivent rester des repères internes sobres et ne pas copier les chartes graphiques de ChatGPT, Gemini, Claude, Copilot ou Perplexity.

Matrice d'usage GEO :

| Donnée GEO | Couleur recommandée | Usage | Prudence |
|---|---:|---|---|
| Présence dans une réponse IA | `#8B5CF6` | badge présence, série GEO | ne pas confondre avec validation qualité |
| Citation de la marque | `#16A34A` | citation favorable ou présence validée | ajouter source ou contexte |
| Citation des concurrents | `#F97316` | comparaison concurrentielle | ne pas marquer en danger par défaut |
| Score de visibilité IA | `#6366F1` | score global GEO | expliquer la période |
| ChatGPT | `#0F766E` | repère interne modèle | ne pas copier la marque |
| Gemini | `#2563EB` | repère interne modèle | ne pas copier la marque |
| Claude | `#7C3AED` | repère interne modèle | ne pas copier la marque |
| Copilot | `#475569` | repère interne modèle | rester neutre |
| Perplexity | `#0891B2` | repère interne modèle | rester sobre |
| Évolution positive | `#16A34A` | amélioration visible | confirmer le sens métier |
| Évolution négative | `#DC2626` | perte de visibilité | afficher modèle et période |
| Absence de mention | `#64748B` | statut neutre ou manque | ne pas utiliser rouge sauf objectif manqué |

Les couleurs de modèles IA ne sont pas des couleurs officielles de marques. Elles servent uniquement à distinguer des séries internes.

## 11. Couleurs pour les KPI

La couleur d'un KPI dépend du sens métier. Une hausse n'est pas toujours positive et une baisse n'est pas toujours négative.

Règles :

- hausse des clics : généralement positive ;
- hausse des erreurs : négative ;
- baisse des erreurs : positive ;
- baisse des impressions : à analyser selon contexte ;
- objectif atteint : succès ;
- objectif non atteint : avertissement ou erreur selon criticité.

| Métrique | Sens de lecture | Couleur recommandée |
|---|---|---:|
| Clics SEO en hausse | positif si trafic qualifié | `#16A34A` |
| Erreurs techniques en hausse | négatif | `#DC2626` |
| Erreurs techniques en baisse | positif | `#16A34A` |
| Visibilité GEO en hausse | positif | `#16A34A` |
| Mentions concurrentes en hausse | à surveiller | `#D97706` |
| API indisponible | critique | `#DC2626` |
| Configuration incomplète | attention | `#D97706` |
| Objectif atteint | succès | `#16A34A` |
| Objectif non atteint | warning ou erreur | `#D97706` ou `#DC2626` |
| Donnée stable | neutre | `#64748B` |

Chaque carte KPI doit afficher le libellé, la valeur, la période et le sens de lecture.

## 12. Couleurs pour les graphiques

Les graphiques doivent rester lisibles. Le nombre recommandé de couleurs simultanées est de 4 à 6 séries visibles, 8 maximum si les labels sont explicites.

Règles :

- éviter trop de séries ;
- privilégier les nuances sobres ;
- garder le rouge pour erreurs, risques ou détériorations métier ;
- ne pas utiliser rouge/vert comme seul moyen de compréhension ;
- ajouter labels, formes, pointillés ou icônes si nécessaire ;
- différencier séries principales et secondaires ;
- garder une couleur stable pour une même série sur tout l'écran.

Palette graphique indicative :

| Série | Couleur | Usage recommandé |
|---|---:|---|
| Série principale | `#2563EB` | métrique centrale |
| Série secondaire | `#0EA5E9` | métrique complémentaire |
| SEO | `#10B981` | visibilité SEO |
| GEO | `#8B5CF6` | visibilité IA |
| Concurrent | `#F97316` | comparaison externe |
| Neutre | `#64748B` | référence, moyenne |
| Warning | `#D97706` | seuil à surveiller |
| Erreur | `#DC2626` | rupture, incident |

Éviter les camemberts complexes. Préférer courbes, barres et tableaux comparatifs lorsque la précision compte.

## 13. Couleurs pour les tableaux

Les tables doivent rester sobres, même avec beaucoup de lignes.

| Token | Valeur claire | Valeur sombre | Usage |
|---|---:|---:|---|
| `table.header.bg` | `#F1F5F9` | `#1F2937` | en-tête |
| `table.row.bg` | `#FFFFFF` | `#111827` | ligne standard |
| `table.row.alt` | `#F8FAFC` | `#0F172A` | alternance légère |
| `table.row.hover` | `#E2E8F0` | `#273449` | survol |
| `table.row.selected` | `#DBEAFE` | `#1E3A8A` | sélection |
| `table.row.error` | `#FEE2E2` | `#450A0A` | ligne en erreur |
| `table.row.disabled` | `#F1F5F9` | `#1E293B` | ligne désactivée |
| `table.cell.modified` | `#FEF3C7` | `#451A03` | cellule modifiée |
| `table.cell.critical` | `#FEE2E2` | `#450A0A` | cellule critique |
| `table.border` | `#E2E8F0` | `#253044` | bordures discrètes |
| `table.badge.bg` | `#F1F5F9` | `#1E293B` | badge dans cellule |

Les lignes alternées sont optionnelles. Elles ne doivent pas créer un effet visuel trop contrasté.

## 14. Couleurs pour les formulaires

Les formulaires doivent rendre la saisie, le focus, les erreurs et les champs désactivés immédiatement compréhensibles.

| Élément | Fond | Texte | Bordure | Usage |
|---|---:|---:|---:|---|
| Champ normal | `#FFFFFF` / `#0F172A` | `#0F172A` / `#F8FAFC` | `#CBD5E1` / `#334155` | saisie standard |
| Champ focus | fond normal | texte normal | `#3B82F6` | focus clavier/souris |
| Champ erreur | `#FEF2F2` / `#450A0A` | `#991B1B` / `#FCA5A5` | `#EF4444` | validation échouée |
| Champ succès | `#F0FDF4` / `#052E16` | `#166534` / `#86EFAC` | `#22C55E` | validation confirmée |
| Champ désactivé | `#E5E7EB` / `#334155` | `#64748B` / `#94A3B8` | `#CBD5E1` / `#475569` | non modifiable |
| Lecture seule | `#F8FAFC` / `#1E293B` | `#334155` / `#CBD5E1` | `#E2E8F0` / `#334155` | donnée consultable |
| Aide contextuelle | transparent | `#64748B` / `#94A3B8` | none | explication |
| Label | transparent | `#334155` / `#E5E7EB` | none | nom de champ |
| Placeholder | transparent | `#94A3B8` / `#64748B` | none | exemple |

Le rouge de formulaire doit être réservé aux erreurs réelles. Une aide contextuelle ne doit pas être rouge.

## 15. Couleurs pour les boutons

Les boutons doivent présenter une intention claire.

| Type | Background | Texte | Bordure | Hover | Active | Focus |
|---|---:|---:|---:|---:|---:|---:|
| Primaire | `#2563EB` | `#FFFFFF` | `#2563EB` | `#1D4ED8` | `#1E40AF` | `#93C5FD` |
| Secondaire | transparent | `#334155` / `#CBD5E1` | `#CBD5E1` / `#475569` | `#F1F5F9` / `#1E293B` | `#E2E8F0` / `#334155` | `#93C5FD` |
| Danger | `#DC2626` | `#FFFFFF` | `#DC2626` | `#B91C1C` | `#991B1B` | `#FCA5A5` |
| Discret | transparent | `#475569` / `#CBD5E1` | transparent | `#F1F5F9` / `#1E293B` | `#E2E8F0` / `#334155` | `#93C5FD` |
| Icône | transparent | `#64748B` / `#CBD5E1` | transparent | `#E2E8F0` / `#273449` | `#CBD5E1` / `#334155` | `#93C5FD` |
| Désactivé | `#E5E7EB` / `#334155` | `#94A3B8` / `#64748B` | `#CBD5E1` / `#475569` | aucun | aucun | aucun |
| Loading | couleur du type | texte du type | bordure du type | inchangé | inchangé | focus visible |

Un bouton danger doit toujours être associé à une confirmation pour une action destructive.

## 16. Couleurs pour les alertes

| Type | Fond | Bordure | Texte | Icône | Usage |
|---|---:|---:|---:|---:|---|
| Succès | `#DCFCE7` | `#22C55E` | `#166534` | `#16A34A` | action réussie |
| Information | `#E0F2FE` | `#38BDF8` | `#075985` | `#0284C7` | information neutre |
| Avertissement | `#FEF3C7` | `#F59E0B` | `#92400E` | `#D97706` | risque non bloquant |
| Erreur | `#FEE2E2` | `#EF4444` | `#991B1B` | `#DC2626` | erreur ou blocage |
| Sécurité | `#FEE2E2` | `#B91C1C` | `#7F1D1D` | `#B91C1C` | accès ou secret |
| API indisponible | `#FEE2E2` | `#EF4444` | `#991B1B` | `#DC2626` | backend indisponible |
| Configuration incomplète | `#FEF3C7` | `#F59E0B` | `#92400E` | `#D97706` | paramètre manquant |
| Import/export | `#E0F2FE` | `#38BDF8` | `#075985` | `#0284C7` | opération longue |

En mode sombre, utiliser des fonds sombres dédiés et conserver des textes suffisamment contrastés.

## 17. Couleurs pour la sécurité

La sécurité utilise des couleurs sobres et strictement proportionnées au risque.

| Usage sécurité | Couleur | Règle |
|---|---:|---|
| Accès refusé | `#DC2626` | erreur bloquante, message clair |
| Action destructive | `#B91C1C` | confirmation obligatoire |
| Clé API masquée | `#64748B` | neutre, jamais rouge si valide |
| Secret expiré | `#D97706` | avertissement avant erreur |
| Token invalide | `#DC2626` | erreur d'authentification |
| Permission manquante | `#D97706` ou `#DC2626` | selon blocage |
| Rôle admin | `#334155` | statut administratif sobre |
| Import sensible | `#D97706` | prudence et confirmation |
| Export sensible | `#D97706` | audit et confirmation |

Le rouge doit être réservé aux vrais risques, erreurs ou actions destructives. Un rôle administrateur n'est pas une erreur.

## 18. Couleurs pour les logs et observabilité

Les logs doivent privilégier la lisibilité et la gravité.

| Niveau ou événement | Couleur | Usage |
|---|---:|---|
| DEBUG | `#64748B` | diagnostic local, faible priorité |
| INFO | `#0284C7` | événement normal |
| WARNING | `#D97706` | anomalie récupérable |
| ERROR | `#DC2626` | échec opérationnel |
| CRITICAL | `#7F1D1D` | incident majeur |
| Trace ID | `#7C3AED` | identifiant de corrélation |
| Événement système | `#475569` | système, backend, health |
| Événement utilisateur | `#0F766E` | action utilisateur |
| Événement sécurité | `#B91C1C` | permission, secret, auth |

Les logs ne doivent jamais afficher de secret en clair. La couleur aide à scanner la gravité mais ne remplace pas le niveau texte.

## 19. Mode clair et mode sombre

Le Desktop actuel vise une expérience sombre professionnelle. Le futur React devra pouvoir reprendre les mêmes intentions en mode sombre et, si besoin, en mode clair.

Principes :

- maintenir un contraste minimum de 4.5:1 pour le texte courant ;
- adapter les surfaces, pas seulement inverser les couleurs ;
- conserver les bordures visibles sur fonds sombres ;
- éviter les rouges et verts trop saturés sur fond sombre ;
- vérifier les graphiques sur les deux modes ;
- garder les tableaux denses lisibles en dark mode ;
- ne pas utiliser uniquement l'ombre pour séparer les surfaces sombres.

Risques du dark mode sur tableaux denses :

- bordures trop faibles ;
- texte secondaire trop peu contrasté ;
- hover invisible ;
- badges trop saturés ;
- graphiques difficiles à comparer.

Chaque token doit donc prévoir une intention claire et, si nécessaire, une valeur adaptée au mode sombre.

## 20. Tokens de design recommandés

La nomenclature de tokens doit rester indépendante du framework.

| Token | Rôle | Exemple de valeur |
|---|---|---:|
| `color.primary` | action principale | `#2563EB` |
| `color.primary.hover` | hover primaire | `#1D4ED8` |
| `color.primary.active` | actif primaire | `#1E40AF` |
| `color.surface.app` | fond application | `#0B1120` |
| `color.surface.default` | surface principale | `#111827` |
| `color.surface.raised` | carte ou panneau | `#172033` |
| `color.border.default` | bordure standard | `#253044` |
| `color.text.primary` | texte principal | `#F8FAFC` |
| `color.text.secondary` | texte secondaire | `#CBD5E1` |
| `color.text.disabled` | texte désactivé | `#64748B` |
| `color.state.success` | succès | `#16A34A` |
| `color.state.info` | information | `#0284C7` |
| `color.state.warning` | avertissement | `#D97706` |
| `color.state.error` | erreur | `#DC2626` |
| `color.state.danger` | danger | `#B91C1C` |
| `color.domain.seo` | domaine SEO | `#10B981` |
| `color.domain.geo` | domaine GEO | `#8B5CF6` |
| `color.domain.security` | sécurité | `#B91C1C` |
| `color.log.warning` | log warning | `#D97706` |
| `color.chart.series.1` | série graphique | `#2563EB` |

Les noms de tokens doivent exprimer l'intention, pas seulement la couleur.

## 21. Correspondance Desktop PySide6 / futur React

La traduction technique sera définie plus tard. Ce document fixe uniquement la correspondance conceptuelle.

| Token | Usage | Desktop PySide6 | Futur React |
|---|---|---|---|
| `color.primary` | bouton principal | variable QSS future | variable CSS ou token |
| `color.surface.default` | fond contenu | QSS widget/page | CSS layout |
| `color.text.primary` | texte principal | QSS label/table | CSS text |
| `color.border.default` | bordure | QSS border | border token |
| `color.state.error` | erreur | QSS alert/input | composant alert/input |
| `color.state.warning` | avertissement | QSS badge/banner | composant badge/banner |
| `color.domain.seo` | domaine SEO | icône, badge, graphique | badge, chart, icon |
| `color.domain.geo` | domaine GEO | icône, badge, graphique | badge, chart, icon |
| `color.log.error` | log error | table logs | table logs |
| `color.security.danger` | action sensible | bouton danger | bouton danger |

PySide6 et React peuvent différer dans le rendu. Les intentions et libellés doivent rester identiques.

## 22. Accessibilité et contrastes

Règles d'accessibilité couleur :

- contraste texte courant : 4.5:1 minimum ;
- contraste texte large : 3:1 minimum ;
- focus visible sur toutes les surfaces ;
- bordure ou outline de focus distincte du hover ;
- information importante jamais uniquement par couleur ;
- rouge/vert toujours complétés par texte, icône ou signe ;
- placeholder moins important que label, mais encore lisible ;
- texte désactivé lisible sans sembler actif.

Checklist accessibilité couleur :

- [ ] Le texte principal respecte le contraste minimum.
- [ ] Les textes secondaires restent lisibles.
- [ ] Le focus clavier est visible.
- [ ] Les états d'erreur ont texte et icône ou message.
- [ ] Les graphiques restent compréhensibles sans couleur.
- [ ] Les badges ont un libellé clair.
- [ ] Les combinaisons rouge/vert ne sont pas le seul signal.
- [ ] Les bordures sont visibles sur fond sombre.

## 23. Règles de combinaison

Les combinaisons doivent préserver la lisibilité.

| Combinaison | Statut | Commentaire |
|---|---|---|
| Texte clair sur surface sombre | Autorisé | vérifier contraste réel |
| Texte sombre sur surface claire | Autorisé | standard pour mode clair |
| Texte rouge sur fond rouge doux | Autorisé | uniquement erreurs, contraste requis |
| Texte vert sur fond vert doux | Autorisé | uniquement succès |
| Primary sur fond application | Autorisé | actions et focus |
| Rouge pour simple variation négative | À éviter | vérifier sens métier |
| Vert pour simple variation positive | À éviter | vérifier sens métier |
| Couleur domaine en fond de page | Interdit | surcharge visuelle |
| Badge coloré sans texte | Interdit | inaccessible |
| Graphique avec plus de 8 couleurs | À éviter | préférer filtres ou regroupement |
| Bordure subtile sur dark mode | Autorisé avec test | risque d'invisibilité |
| Texte coloré long | À éviter | fatigue et contraste variable |

Les badges doivent utiliser des fonds doux et des textes contrastés. Les alertes doivent utiliser une bordure visible en plus de la couleur de fond.

## 24. Anti-patterns couleur

Anti-patterns interdits ou à éviter :

- trop de couleurs dans un dashboard ;
- rouge utilisé pour une simple baisse non critique ;
- vert utilisé sans analyse métier ;
- couleurs de marques externes copiées inutilement ;
- texte coloré sans contraste ;
- badges trop nombreux ;
- tableaux arc-en-ciel ;
- graphiques décoratifs ;
- absence de distinction hors couleur ;
- couleurs différentes pour une même intention ;
- surfaces entières colorées par domaine ;
- boutons danger utilisés pour des actions non destructives ;
- warning utilisé pour attirer l'attention sans risque ;
- focus invisible en mode sombre ;
- logs sans niveau texte.

La couleur doit réduire l'ambiguïté, jamais en créer.

## 25. Exemples conceptuels

Carte KPI positive :

```text
------------------------------------+
| Clics SEO                         |
| 12 480                            |
| +8 % vs période précédente        |
| État : positif (#16A34A)          |
+------------------------------------+
```

Carte KPI négative mais non critique :

```text
------------------------------------+
| Impressions                       |
| 94 200                            |
| -3 % vs période précédente        |
| État : à surveiller (#D97706)     |
+------------------------------------+
```

Alerte API indisponible :

```text
[Erreur] API indisponible.
Impossible de charger les données. Réessayez ou vérifiez l'état du backend.
Couleurs : fond erreur doux, bordure erreur, texte erreur.
```

Badge SEO :

```text
[SEO] Accent #10B981, fond doux, texte contrasté.
```

Badge GEO :

```text
[GEO] Accent #8B5CF6, fond doux, texte contrasté.
```

Ligne de table en erreur :

```text
URL /example | Statut crawl : Erreur | Fond erreur doux | Icône + libellé
```

Message de configuration incomplète :

```text
[Avertissement] Configuration incomplète.
Ajoutez une clé API valide pour lancer les analyses GEO.
```

## 26. Checklist de validation

Checklist globale :

- [ ] Les couleurs respectent les tokens officiels.
- [ ] Chaque couleur a une intention claire.
- [ ] Les couleurs de domaine restent des accents.
- [ ] Les couleurs d'état sont cohérentes entre modules.
- [ ] Aucun secret n'est rendu plus visible que nécessaire.

Checklist dashboard :

- [ ] Les KPI utilisent des couleurs selon le sens métier.
- [ ] Les graphiques ne dépassent pas le nombre de couleurs recommandé.
- [ ] Les alertes critiques sont visibles.
- [ ] Les domaines SEO/GEO sont distingués sans surcharge.

Checklist graphique :

- [ ] Les séries ont des couleurs stables.
- [ ] Rouge et vert ne sont pas seuls à porter le sens.
- [ ] Les labels et légendes sont lisibles.
- [ ] Les couleurs restent compréhensibles en mode sombre.

Checklist table :

- [ ] Hover, sélection et erreur sont distincts.
- [ ] Les bordures restent discrètes mais visibles.
- [ ] Les badges ont un texte.
- [ ] Les cellules critiques ont un message ou une icône.

Checklist formulaire :

- [ ] Focus visible.
- [ ] Erreurs proches du champ.
- [ ] Champs désactivés lisibles.
- [ ] Secrets masqués.

Checklist alerte :

- [ ] Le type d'alerte est identifiable par texte.
- [ ] La couleur correspond à la gravité.
- [ ] L'action utilisateur possible est claire.
- [ ] Le rouge est réservé aux vrais risques.

Checklist accessibilité :

- [ ] Contraste texte conforme.
- [ ] Information non portée uniquement par couleur.
- [ ] Focus visible sur toutes surfaces.
- [ ] Rouge/vert complétés par signes ou libellés.

Checklist cohérence Desktop/React :

- [ ] Les mêmes tokens conceptuels sont utilisés.
- [ ] Les mêmes états ont les mêmes intentions.
- [ ] Les mêmes modules gardent les mêmes accents.
- [ ] Les différences de rendu restent techniques, pas fonctionnelles.

## 27. Conclusion

`COLOR_PALETTE.md` complète `DESIGN_SYSTEM.md` en fixant la palette officielle, les intentions de couleur, les tokens conceptuels, les règles d'usage, les contraintes d'accessibilité et les anti-patterns.

Ce document servira de référence aux prochains documents spécialisés :

- `docs/design/ICON_GUIDELINES.md` ;
- `docs/design/COMPONENT_LIBRARY.md` ;
- `docs/design/UI_UX.md`.

Les futurs styles Desktop PySide6 et React devront respecter ces intentions sans imposer de dépendance graphique particulière.
