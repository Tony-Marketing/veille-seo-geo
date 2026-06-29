# Icon Guidelines - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document définit les règles officielles d'utilisation des icônes dans **Veille SEO-GEO Groupe A.P&Partner**.

Il s'applique à l'interface Desktop PySide6 actuelle et au futur frontend React. Il complète `docs/design/DESIGN_SYSTEM.md` et `docs/design/COLOR_PALETTE.md` sans les remplacer.

Il ne choisit pas de bibliothèque d'icônes, n'ajoute aucune dépendance et ne fournit aucun code. Il décrit les intentions, usages, tailles, couleurs, états et règles d'accessibilité à respecter.

## 2. Principes généraux

Les icônes servent la compréhension. Elles ne doivent pas devenir une couche décorative.

Principes obligatoires :

- icônes au service de l'information ;
- sobriété visuelle ;
- cohérence entre modules ;
- lisibilité en interface dense ;
- prévisibilité des actions ;
- complémentarité avec les libellés ;
- absence de décoration inutile ;
- information critique jamais transmise uniquement par une icône.

Une icône doit accélérer la reconnaissance, pas obliger l'utilisateur à deviner.

## 3. Rôle des icônes dans l'application

Les icônes interviennent dans les zones suivantes :

- navigation principale et secondaire ;
- actions courantes et actions sensibles ;
- états utilisateur ;
- alertes et messages ;
- modules métier ;
- données SEO ;
- données GEO ;
- configuration ;
- sécurité ;
- logs ;
- administration ;
- feedback utilisateur ;
- filtres, tris et recherches ;
- import et export.

Elles doivent renforcer le libellé, structurer les vues denses et rendre les états plus faciles à scanner.

## 4. Documents liés

| Document | Rôle par rapport aux icônes |
|---|---|
| `docs/design/DESIGN_SYSTEM.md` | définit les principes UI globaux, les composants et les états |
| `docs/design/COLOR_PALETTE.md` | définit les couleurs associées aux états, domaines et actions |
| `docs/UI_UX.md` | fournit la référence UI/UX générale et les intentions déjà établies |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | cadre l'intégration Desktop, les widgets et le shell PySide6 |
| `docs/architecture/API_ARCHITECTURE.md` | définit les états API que l'interface doit afficher proprement |
| `docs/architecture/SECURITY.md` | impose le masquage des secrets et la prudence sur actions sensibles |
| `docs/architecture/LOGGING.md` | définit les niveaux de logs et la séparation message utilisateur / détail technique |

Les icônes doivent respecter les règles de sécurité, de feedback, de contraste et de cohérence définies dans ces documents.

## 5. Style visuel des icônes

Le style attendu est sobre, clair et professionnel.

Règles :

- privilégier des icônes linéaires ou semi-pleines selon le contexte ;
- conserver une famille homogène ;
- éviter les pictogrammes trop illustratifs ;
- éviter les styles mélangés dans une même zone ;
- éviter les icônes trop détaillées en 16 ou 18 px ;
- privilégier des formes simples et reconnaissables ;
- conserver un poids visuel compatible avec les textes ;
- éviter les icônes marketing ou décoratives.

Une bibliothèque pourra être choisie plus tard pour PySide6 et React. Ce choix devra respecter ces intentions sans imposer une dépendance dans ce document.

## 6. Tailles recommandées

Les tailles sont conceptuelles et doivent être adaptées au rendu réel du framework.

| Contexte | Taille recommandée | Usage | Précautions |
|---|---:|---|---|
| Icône de navigation | 18 à 20 px | sidebar, menus principaux | libellé recommandé |
| Icône de bouton | 16 à 18 px | action avec texte | alignement vertical strict |
| Icône de statut | 14 à 18 px | succès, erreur, warning | toujours avec libellé si critique |
| Icône de badge | 12 à 14 px | badge court | éviter détails fins |
| Icône dans table | 14 à 16 px | statut ou action compacte | limiter le nombre par ligne |
| Icône d'alerte | 18 à 24 px | message important | accompagner d'un titre |
| Icône empty state | 32 à 48 px | état vide | sobre, non illustratif |
| Icône dashboard | 20 à 28 px | KPI, statut, synthèse | ne pas concurrencer la valeur |

Une icône interactive doit avoir une zone cliquable suffisante, même si le pictogramme est petit.

## 7. Couleurs des icônes

Les couleurs s'appuient sur `COLOR_PALETTE.md`. Elles doivent rester fonctionnelles.

| Type | Couleur conceptuelle | Usage | À éviter |
|---|---|---|---|
| Icône primaire | `color.primary` | action principale, sélection active | toutes les icônes d'une page |
| Icône secondaire | `color.text.secondary` | action neutre, navigation inactive | signal critique |
| Icône désactivée | `color.text.disabled` | action indisponible | icône interactive active |
| Icône succès | `color.state.success` | réussite, état OK | métrique positive sans contexte |
| Icône avertissement | `color.state.warning` | risque non bloquant | simple information |
| Icône erreur | `color.state.error` | échec ou blocage | baisse non critique |
| Icône information | `color.state.info` | information neutre | validation ou danger |
| Icône sécurité | `color.domain.security` | accès, secret, action sensible | statut admin neutre |
| Icône SEO | `color.domain.seo` | domaine SEO | succès générique |
| Icône GEO | `color.domain.geo` | domaine GEO | copie de marque IA |

Ne pas colorer toutes les icônes. Les icônes neutres doivent rester majoritaires.

## 8. Icônes et libellés

Une icône seule est autorisée uniquement si son sens est évident dans son contexte.

Règles :

- icône + libellé recommandé pour la navigation principale ;
- tooltip obligatoire pour tout bouton icône seul ;
- libellé obligatoire pour une action sensible ;
- message d'erreur jamais remplacé par une simple icône ;
- les icônes de statut doivent avoir un texte ou une valeur associée ;
- les actions destructives doivent être nommées explicitement.

Matrice d'usage :

| Contexte | Icône seule autorisée | Libellé requis | Tooltip requis |
|---|---:|---:|---:|
| Navigation principale | Non | Oui | Non si libellé visible |
| Sidebar compacte future | Oui | Non visible | Oui |
| Bouton primaire | Non | Oui | Optionnel |
| Bouton icône toolbar | Oui | Non visible | Oui |
| Action destructive | Non | Oui | Oui si icône présente |
| État critique | Non | Oui | Optionnel |
| Badge domaine | Oui si texte badge | Oui dans badge | Non |
| Table action secondaire | Oui | Non visible | Oui |
| Formulaire aide | Oui | Non visible | Oui |

## 9. Icônes de navigation

Les icônes de navigation doivent aider à distinguer les modules sans remplacer les libellés.

Matrice navigation :

| Module | Intention d'icône | Usage | Risque d'ambiguïté |
|---|---|---|---|
| Tableau de bord | grille, synthèse, indicateurs | entrée principale | confondre avec rapports |
| Sites web | globe, fenêtre web, domaine | sites suivis | confondre avec URLs |
| Mots-clés | mot, étiquette, recherche | suivi keywords | confondre avec recherche globale |
| Contenus | document, page, édition | pages et contenus | confondre avec rapports |
| Concurrents | comparaison, cible, silhouettes | veille concurrentielle | paraître agressif |
| GEO Monitor | réseau IA, étincelle sobre, réponse | visibilité IA générative | ne pas copier logos IA |
| Rapports | document synthèse, export | rapports générés | confondre avec contenus |
| Configuration | réglages, curseurs | paramètres | confondre avec administration |
| Administration | panneau de contrôle, bouclier sobre | zone admin | trop technique |
| Utilisateurs | personne ou groupe | comptes | confondre avec rôles |
| Rôles | badge, clé de rôle | rôles RBAC | confondre avec permission |
| Permissions | clé, verrou ouvert/fermé | droits atomiques | signaler un risque à tort |
| Logs | liste horodatée, terminal sobre | journaux | trop développeur |
| Sécurité | bouclier, verrou | accès et secrets | surutilisation du danger |

Décrire l'intention visuelle suffit. Les noms d'icônes d'une bibliothèque spécifique ne doivent pas être figés ici.

## 10. Icônes d'action

Les icônes d'action doivent être prévisibles. Une même action garde la même intention dans tous les modules.

| Action | Intention visuelle | Couleur | Confirmation nécessaire | Commentaire |
|---|---|---|---:|---|
| Ajouter | signe plus, création | primaire ou neutre | Non | libellé recommandé |
| Modifier | crayon, édition | neutre | Non | éviter sur action destructive |
| Supprimer | corbeille, retrait | danger | Oui | jamais icône seule |
| Archiver | boîte, archive | neutre | Selon impact | distinguer de supprimer |
| Restaurer | retour, restauration | neutre ou succès | Selon impact | préciser la cible |
| Rechercher | loupe | neutre | Non | standard global |
| Filtrer | entonnoir | neutre | Non | afficher filtres actifs |
| Trier | flèches ordre | neutre | Non | icône proche de colonne |
| Exporter | sortie, fichier sortant | info ou neutre | Selon sensibilité | audit si sensible |
| Importer | entrée, fichier entrant | info ou warning | Selon impact | validation nécessaire |
| Synchroniser | boucle, échange | primaire ou info | Non | afficher chargement |
| Actualiser | flèche circulaire | neutre | Non | éviter double avec sync |
| Sauvegarder | disque, validation | primaire | Non | état loading |
| Annuler | retour, croix sobre | neutre | Non | ne pas confondre avec fermer |
| Valider | coche | succès ou primaire | Non | succès après action |
| Dupliquer | copie | neutre | Non | préciser ressource |
| Consulter | oeil, lecture | neutre | Non | pas d'édition |
| Ouvrir | flèche sortie, fenêtre | neutre | Non | lien externe si applicable |
| Fermer | croix | neutre | Non | éviter rouge |
| Télécharger | flèche bas | neutre ou info | Selon contenu | vérifier permissions |
| Envoyer | flèche, envoi | primaire | Selon action | préciser destination |
| Tester une configuration | prise, signal, test | info | Non | afficher résultat |

## 11. Icônes d'état

Les icônes d'état doivent être associées à un message ou un libellé.

| État | Intention d'icône | Couleur associée | Message complémentaire attendu |
|---|---|---|---|
| Succès | coche, cercle validé | succès | confirmation courte |
| Information | i, cercle information | information | contexte neutre |
| Avertissement | triangle, point d'attention | avertissement | risque et action possible |
| Erreur | croix, cercle erreur | erreur | cause et action possible |
| Danger | alerte forte, corbeille sensible | danger | confirmation obligatoire |
| Chargement | spinner, progression | primaire ou info | opération nommée |
| En attente | horloge | en attente | prochaine étape |
| Désactivé | symbole neutre atténué | désactivé | raison si utile |
| Verrouillé | verrou | sécurité | condition de déverrouillage |
| Accès refusé | bouclier, verrou | erreur ou sécurité | droits insuffisants |
| Configuration manquante | réglage + warning | avertissement | élément manquant |
| API indisponible | serveur barré, nuage barré | erreur | réessayer ou vérifier backend |
| Données partielles | cercle incomplet, warning doux | avertissement | source manquante |

## 12. Icônes SEO

Les icônes SEO doivent représenter des données analytiques sans surcharge visuelle.

Matrice SEO :

| Donnée SEO | Intention d'icône | Usage | Attention design |
|---|---|---|---|
| Position | classement, flèche verticale | KPI, table positions | préciser meilleur/pire sens |
| Clics | curseur, clic, interaction | graphique ou KPI | ne pas confondre avec action UI |
| Impressions | oeil, visibilité | KPI visibilité | ajouter unité |
| CTR | ratio, pourcentage | table, KPI | éviter icône trop abstraite seule |
| Pages indexées | page validée | état couverture | ne pas confondre avec succès global |
| Erreurs SEO | page avec alerte | audit technique | rouge seulement si erreur réelle |
| Opportunités | ampoule sobre, cible | recommandations | ne pas rendre décoratif |
| Progression | flèche montante | variation | vérifier sens métier |
| Régression | flèche descendante | variation | baisse pas toujours négative |
| Mots-clés | tag, mot, recherche | module keywords | libellé recommandé |
| URL cible | lien, cible | table keywords | éviter lien externe si interne |
| Page marque | page + marque | classification contenu | rester générique |
| Page catégorie | dossier, grille | classification contenu | éviter pictogramme e-commerce trop précis |
| Fiche produit | fiche, étiquette | contenu produit | générique |
| Landing page | page avec cible | acquisition | ne pas confondre avec rapport |
| Blog | document éditorial | contenu blog | sobriété |

## 13. Icônes GEO

Les icônes GEO doivent représenter la visibilité IA sans copier les logos, couleurs ou chartes graphiques de ChatGPT, Gemini, Claude, Copilot ou Perplexity.

Les plateformes suivies peuvent être distinguées par des repères internes sobres, toujours accompagnés d'un nom de modèle ou fournisseur lorsque l'information est importante.

Matrice GEO :

| Donnée GEO | Intention d'icône | Usage | Prudence |
|---|---|---|---|
| Visibilité IA | réseau, signal, réponse | KPI GEO | ne pas promettre une mesure absolue |
| Présence dans une réponse générative | bulle validée | état présence | ajouter modèle et période |
| Absence de mention | bulle vide, tiret | état neutre | ne pas mettre rouge par défaut |
| Citation de marque | citation, marque validée | table citations | préciser source |
| Citation concurrent | citation + comparaison | veille concurrentielle | éviter danger par défaut |
| Requête GEO | prompt, question | liste prompts | distinguer du résultat |
| Résultat GEO | réponse, document | détail analyse | ne pas masquer incertitude |
| Moteur IA | puce modèle, processeur sobre | filtre modèle | ne pas copier les logos |
| Historique de réponse | horloge, historique | évolution | période visible |
| Score de confiance | jauge sobre | analyse qualité | expliquer l'échelle |
| Comparaison IA | colonnes, balance | vue comparative | limiter couleurs et icônes |
| ChatGPT | repère IA interne | filtre plateforme | pas de logo officiel |
| Gemini | repère IA interne | filtre plateforme | pas de charte copiée |
| Claude | repère IA interne | filtre plateforme | pas de charte copiée |
| Copilot | repère IA interne | filtre plateforme | pas de charte copiée |
| Perplexity | repère IA interne | filtre plateforme | pas de charte copiée |

## 14. Icônes de configuration

| Élément | Intention d'icône | Usage | Règle |
|---|---|---|---|
| Paramètres globaux | réglages, curseurs | entrée configuration | neutre |
| Clés API | clé masquée | liste clés | ne jamais révéler le secret |
| Connecteurs | prise, lien externe | providers | statut explicite |
| Import | fichier entrant | import configuration | warning si sensible |
| Export | fichier sortant | export configuration | permissions et audit |
| Test de connexion | signal, prise validée | bouton test | afficher résultat |
| Configuration valide | coche | statut | succès discret |
| Configuration incomplète | warning + réglage | alerte | action attendue |
| Configuration en erreur | erreur + réglage | blocage | message détaillé |
| Synchronisation | boucle | sync données | état loading visible |

## 15. Icônes de sécurité

Règles spécifiques :

- icône danger uniquement pour risque réel ;
- action destructive toujours accompagnée d'un libellé et d'une confirmation ;
- ne pas rendre les secrets visibles via icône, tooltip ou message ;
- les droits et rôles doivent rester compréhensibles sans jargon excessif.

| Élément sécurité | Intention d'icône | Couleur | Règle |
|---|---|---|---|
| Accès refusé | verrou, bouclier | erreur ou sécurité | message clair |
| Rôle administrateur | badge, bouclier sobre | neutre | pas une erreur |
| Permission | clé, verrou ouvert | neutre | préciser le droit |
| Secret masqué | oeil barré, clé masquée | neutre | jamais de valeur complète |
| Clé API | clé | neutre ou warning | afficher seulement masque |
| Token expiré | horloge + verrou | warning ou erreur | reconnexion si nécessaire |
| Action destructive | corbeille + alerte | danger | confirmation obligatoire |
| Suppression | corbeille | danger | jamais icône seule |
| Audit | journal, horodatage | neutre | détail consultable |
| Verrouillage | verrou fermé | sécurité | condition explicite |
| Authentification | utilisateur + verrou | neutre | éviter détails techniques |

## 16. Icônes de logs et observabilité

| Élément | Intention d'icône | Couleur | Usage |
|---|---|---|---|
| Debug | outil, point neutre | neutre | diagnostic faible priorité |
| Info | cercle information | information | événement normal |
| Warning | triangle attention | avertissement | anomalie récupérable |
| Error | cercle erreur | erreur | échec opérationnel |
| Critical | alerte forte | danger | incident majeur |
| Trace | lien, empreinte, identifiant | trace | request_id ou correlation_id |
| Événement utilisateur | utilisateur | neutre | action utilisateur |
| Événement système | serveur, engrenage | neutre | backend, jobs |
| Événement sécurité | bouclier | sécurité | auth, permission |
| API indisponible | serveur barré | erreur | état API |
| Latence | chronomètre | warning | performance dégradée |
| Échec de synchronisation | boucle + erreur | erreur | sync bloquée |

Le niveau texte du log reste obligatoire. L'icône accélère la lecture mais ne remplace pas `INFO`, `WARNING`, `ERROR` ou `CRITICAL`.

## 17. Icônes dans les tableaux

Les tableaux sont denses. Les icônes doivent donc être limitées et régulières.

Règles :

- éviter plus de 2 ou 3 icônes visibles par ligne sans menu d'actions ;
- prévoir tooltip ou libellé accessible ;
- ne pas utiliser l'icône comme seule information critique ;
- garder les actions par ligne à droite ;
- réserver les icônes colorées aux états utiles ;
- utiliser des icônes de tri et filtre stables ;
- signaler les données manquantes par texte ou tiret en plus de l'icône.

Usages autorisés :

- icône de statut en cellule ;
- icônes d'action par ligne ;
- icône de tri sur colonne active ;
- icône de filtre dans toolbar ;
- icône de sélection si nécessaire ;
- icône de donnée manquante avec libellé.

## 18. Icônes dans les formulaires

| Contexte formulaire | Intention d'icône | Usage | Règle |
|---|---|---|---|
| Aide contextuelle | information | tooltip ou aide courte | pas critique seule |
| Champ valide | coche | validation discrète | éviter sur chaque frappe |
| Champ en erreur | erreur | validation | message obligatoire |
| Champ obligatoire | astérisque ou marque sobre | label | ne pas remplacer le label |
| Mot de passe / secret masqué | oeil barré | visibilité contrôlée | jamais tooltip avec secret |
| Test de connexion | prise, signal | action test | résultat explicite |
| Chargement | spinner | validation serveur | nommer l'action |
| Sauvegarde | sauvegarde ou coche | action primaire | libellé recommandé |
| Annulation | retour ou croix sobre | action secondaire | ne pas utiliser danger |
| Perte de données | warning | confirmation | message clair |

## 19. Icônes dans les dashboards

Matrice dashboard :

| Zone dashboard | Icône possible | Usage | À éviter |
|---|---|---|---|
| KPI | domaine ou état | renforcer le titre | icône plus visible que valeur |
| Tendance | flèche, courbe | variation | sens couleur seul |
| Alerte | warning, erreur | priorisation | alerte décorative |
| Comparaison | colonnes, balance | concurrents ou modèles | pictogramme ambigu |
| Filtre actif | entonnoir | contexte filtré | masquer le filtre texte |
| Période | calendrier | plage temporelle | date sans libellé |
| Site sélectionné | globe, domaine | contexte site | confondre avec lien externe |
| Source de données | serveur, connecteur | origine donnée | afficher secret |
| Fraîcheur des données | horloge | dernière mise à jour | icône sans date |

Les icônes de dashboard doivent aider à scanner, pas transformer les KPI en cartes décoratives.

## 20. Icônes dans les alertes et messages

Chaque alerte importante doit avoir :

- une icône ;
- un titre ou message clair ;
- un texte explicatif si nécessaire ;
- une action possible si pertinent.

| Type | Intention d'icône | Règle |
|---|---|---|
| Succès | coche | confirmation courte |
| Information | information | contexte neutre |
| Avertissement | attention | risque et action |
| Erreur | erreur | cause et solution |
| Sécurité | bouclier ou verrou | droits, secret, accès |
| API indisponible | serveur barré | réessayer ou vérifier backend |
| Configuration incomplète | réglage + warning | indiquer élément manquant |
| Import/export | fichier entrant/sortant | progression ou résultat |

Ne jamais afficher seulement une icône rouge sans explication.

## 21. Icônes et accessibilité

Règles :

- ne pas transmettre une information uniquement par icône ;
- tout bouton icône seul doit avoir un tooltip ;
- fournir un libellé accessible conceptuel ;
- conserver une zone cliquable suffisante ;
- garantir un contraste suffisant ;
- conserver un focus visible ;
- permettre une navigation clavier cohérente ;
- éviter les ambiguïtés entre actions proches.

Checklist accessibilité icônes :

- [ ] L'icône critique a un libellé texte.
- [ ] Le bouton icône seul a un tooltip.
- [ ] La zone cliquable est suffisante.
- [ ] Le focus clavier est visible.
- [ ] Le contraste est suffisant.
- [ ] L'état n'est pas indiqué uniquement par couleur.
- [ ] La même icône garde la même signification.
- [ ] Les actions destructives sont nommées.

## 22. Icônes et cohérence Desktop PySide6 / futur React

Les implémentations peuvent différer, mais les intentions doivent rester identiques.

| Principe | Desktop PySide6 | Futur React | Règle commune |
|---|---|---|---|
| Même intention | ressources ou icônes Qt futures | bibliothèque ou SVG future | même action, même symbole |
| Même libellé | texte bouton/menu | texte composant | libellé stable |
| Même statut | status bar, table, alertes | badges, alerts, tables | état identique |
| Même tooltip | tooltip Qt | tooltip web | obligatoire si icône seule |
| Même sécurité | confirmation modal/page | confirmation modal/page | destruction jamais seule |
| Même accessibilité | focus Qt | focus navigateur | focus visible |
| Bibliothèque future | choix compatible PySide6 | choix compatible React | non imposée ici |

Le document reste indépendant du framework afin de permettre une traduction propre dans les deux surfaces.

## 23. Nomenclature recommandée

Les tokens conceptuels décrivent l'intention et non une implémentation.

| Token conceptuel | Intention | Usage | Remarque |
|---|---|---|---|
| `icon.navigation.dashboard` | tableau de bord | navigation | synthèse |
| `icon.navigation.sites` | sites web | navigation | domaine ou globe |
| `icon.navigation.keywords` | mots-clés | navigation | tag ou recherche |
| `icon.navigation.reports` | rapports | navigation | document |
| `icon.action.add` | ajouter | bouton | plus |
| `icon.action.edit` | modifier | ligne/table | crayon |
| `icon.action.delete` | supprimer | action danger | confirmation |
| `icon.action.filter` | filtrer | toolbar | filtres actifs |
| `icon.action.export` | exporter | action | permissions |
| `icon.action.import` | importer | action | validation |
| `icon.state.success` | succès | alerte/statut | coche |
| `icon.state.warning` | avertissement | alerte/statut | triangle |
| `icon.state.error` | erreur | alerte/statut | erreur |
| `icon.domain.seo` | domaine SEO | badge/module | accent SEO |
| `icon.domain.geo` | domaine GEO | badge/module | accent GEO |
| `icon.security.lock` | verrouillage | sécurité | accès |
| `icon.config.api_key` | clé API | configuration | secret masqué |
| `icon.logs.error` | log erreur | observabilité | niveau texte requis |

Aucun fichier de tokens ne doit être créé à cette étape.

## 24. Règles d'association icône + couleur

| Situation | Icône | Couleur | Règle |
|---|---|---|---|
| Action neutre | action standard | neutre | majorité des actions |
| Action primaire | action principale | primaire | une par zone |
| Suppression | corbeille | danger | libellé + confirmation |
| Succès | coche | succès | confirmation courte |
| Avertissement | attention | warning | risque non bloquant |
| Erreur | erreur | error | message explicite |
| SEO | symbole domaine | SEO | seulement si utile |
| GEO | symbole domaine | GEO | jamais logo IA copié |
| Configuration | réglage | neutre ou warning | warning si incomplet |
| Sécurité | verrou/bouclier | sécurité | risque réel uniquement |
| Logs | niveau | couleur niveau | texte du niveau obligatoire |

Éviter de colorer toutes les icônes d'une page. Les couleurs doivent guider la priorité.

## 25. Anti-patterns

À éviter :

- icônes décoratives inutiles ;
- trop d'icônes dans une table ;
- icônes sans tooltip ;
- icônes ambiguës ;
- mélange de styles ;
- copie des logos IA ;
- couleur seule comme indicateur ;
- suppression représentée par une icône seule ;
- icônes trop petites ;
- icônes trop détaillées ;
- icône différente pour la même action selon les écrans ;
- même icône pour deux actions différentes ;
- icône danger pour une action non destructive ;
- icône d'état sans message ;
- navigation principale sans libellés au démarrage.

## 26. Exemples conceptuels

Bouton Ajouter un site :

```text
[icône ajouter] Ajouter un site
Intention : création claire, action primaire, libellé obligatoire.
```

Bouton icône seul :

```text
[icône filtrer]
Tooltip obligatoire : "Filtrer les résultats".
```

Ligne de table avec actions :

```text
Site Europ-Arm | [modifier] [supprimer]
Modifier : tooltip autorisé. Supprimer : libellé ou confirmation obligatoire.
```

Alerte API indisponible :

```text
[icône erreur] API indisponible
Impossible de charger les données. Réessayez ou vérifiez l'état du backend.
```

Badge GEO :

```text
[icône GEO] GEO
Accent domaine, texte visible, aucune copie de logo IA.
```

Configuration incomplète :

```text
[icône avertissement] Configuration incomplète
Ajoutez une clé API valide pour lancer les analyses GEO.
```

Action destructive :

```text
[icône danger] Supprimer le site
Confirmation obligatoire avant exécution.
```

## 27. Checklist de validation

Checklist globale :

- [ ] Les icônes servent une information ou une action.
- [ ] Le style est homogène.
- [ ] Les icônes décoratives sont évitées.
- [ ] Les couleurs suivent `COLOR_PALETTE.md`.
- [ ] Les icônes critiques ont un texte.

Checklist navigation :

- [ ] Chaque module a une intention claire.
- [ ] Les libellés restent visibles en navigation principale.
- [ ] L'état actif est compréhensible.
- [ ] Aucune icône ne copie une marque externe.

Checklist action :

- [ ] Même action, même icône.
- [ ] Tooltip sur icône seule.
- [ ] Action destructive avec libellé et confirmation.
- [ ] Action primaire identifiable.

Checklist état :

- [ ] L'état a une icône cohérente.
- [ ] L'état a un texte.
- [ ] La couleur correspond à la gravité.
- [ ] Le chargement indique l'opération.

Checklist tableau :

- [ ] Pas plus de 2 ou 3 icônes visibles par ligne sans menu.
- [ ] Les actions sont à droite.
- [ ] Les statuts ont un libellé ou un tooltip.
- [ ] Les tris et filtres sont stables.

Checklist formulaire :

- [ ] Les erreurs ont icône et message.
- [ ] Les aides ont tooltip ou texte.
- [ ] Les secrets restent masqués.
- [ ] Le focus reste visible.

Checklist dashboard :

- [ ] Les icônes ne concurrencent pas les KPI.
- [ ] Les alertes sont distinguées.
- [ ] Les domaines SEO/GEO restent sobres.
- [ ] La période et la source restent lisibles.

Checklist accessibilité :

- [ ] Icône critique jamais seule.
- [ ] Tooltip sur icône seule.
- [ ] Contraste suffisant.
- [ ] Zone cliquable suffisante.
- [ ] Navigation clavier possible.

Checklist sécurité :

- [ ] Icône danger réservée aux vrais risques.
- [ ] Suppression confirmée.
- [ ] Aucun secret dans tooltip.
- [ ] Permissions et accès refusés sont explicités.

Checklist cohérence Desktop/React :

- [ ] Même intention d'icône.
- [ ] Même libellé.
- [ ] Même statut.
- [ ] Même règle de tooltip.
- [ ] Différences limitées au rendu technique.

## 28. Conclusion

`ICON_GUIDELINES.md` complète `DESIGN_SYSTEM.md` et `COLOR_PALETTE.md` en fixant les règles d'utilisation des icônes pour la navigation, les actions, les états, les modules SEO/GEO, la configuration, la sécurité, les logs, les tableaux, les formulaires et les dashboards.

Ce document servira de base au futur `docs/design/COMPONENT_LIBRARY.md`, qui précisera l'application concrète de ces règles dans les composants.
