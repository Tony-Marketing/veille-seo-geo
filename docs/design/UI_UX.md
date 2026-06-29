# UI/UX Design - Veille SEO-GEO Groupe A.P&Partner

## 1. Objectif du document

Ce document décrit les parcours UX, comportements d'écran et règles d'interaction de **Veille SEO-GEO Groupe A.P&Partner**.

Il s'applique à l'interface Desktop PySide6 actuelle et au futur frontend React. Il transforme les règles du design system, de la palette, des icônes et de la bibliothèque de composants en usages concrets côté expérience utilisateur.

Il ne fournit pas d'implémentation technique, ne crée aucun composant, n'impose aucune bibliothèque et ne remplace aucun document existant.

## 2. Positionnement par rapport à docs/UI_UX.md

`docs/UI_UX.md` est le document global historique et fonctionnel du projet. Il décrit la vision UI/UX générale, les inspirations, la structure globale et des patterns déjà établis.

`docs/design/UI_UX.md` est un document opérationnel de design et d'UX. Il cadre les parcours, interactions, états d'écran, scénarios métier et comportements attendus.

Les deux documents sont complémentaires :

- `docs/UI_UX.md` donne le contexte global ;
- `docs/design/UI_UX.md` précise comment les utilisateurs parcourent et utilisent l'interface ;
- ce fichier ne remplace pas `docs/UI_UX.md` ;
- ce fichier doit rester cohérent avec les documents design spécialisés.

## 3. Documents liés

| Document | Rôle |
|---|---|
| `docs/UI_UX.md` | référence UI/UX globale et historique |
| `docs/design/DESIGN_SYSTEM.md` | principes, structure, états, règles globales |
| `docs/design/COLOR_PALETTE.md` | couleurs, états, contrastes et domaines |
| `docs/design/ICON_GUIDELINES.md` | icônes, libellés, états et accessibilité |
| `docs/design/COMPONENT_LIBRARY.md` | composants, variantes, états et comportements |
| `docs/architecture/DESKTOP_ARCHITECTURE.md` | contraintes Desktop, ApiClient, pages et widgets |
| `docs/architecture/API_ARCHITECTURE.md` | contrats API, erreurs, pagination, compatibilité Desktop |
| `docs/architecture/SECURITY.md` | secrets, permissions, actions sensibles |
| `docs/architecture/LOGGING.md` | logs, trace ID, messages sûrs et observabilité |

## 4. Principes UX généraux

L'interface doit rester claire, sobre, prévisible et orientée données.

Principes :

- clarté : l'utilisateur comprend où il est et quoi faire ;
- sobriété : chaque élément visible a une fonction ;
- prédictibilité : mêmes actions, mêmes comportements ;
- réduction de la charge cognitive : limiter variantes et surprises ;
- feedback immédiat : toute action produit un retour ;
- prévention des erreurs : validations, confirmations, états explicites ;
- actions explicites : verbes courts et précis ;
- navigation stable : sidebar et contexte constants ;
- densité maîtrisée : informations nombreuses mais lisibles ;
- priorité à la donnée utile : les indicateurs priment sur la décoration.

## 5. Profils utilisateurs internes

Les profils sont conceptuels et décrivent des besoins UX, pas des personnes.

| Profil | Objectifs | Besoins | Risques UX | Écrans prioritaires |
|---|---|---|---|---|
| Marketing/SEO | suivre performances et priorités | KPI, tables, filtres, export | surcharge de données | dashboard, SEO, mots-clés |
| Administrateur | gérer accès et paramètres | confirmations, logs, droits | action sensible trop facile | administration, sécurité, logs |
| Reporting | consulter et partager synthèses | périodes, statut, export | rapport sans contexte | rapports, dashboard |
| Configuration | paramétrer connecteurs | secrets masqués, tests, erreurs | fuite ou mauvaise clé | configuration, API keys |
| Consultation seule | lire sans modifier | navigation claire, accès limité | boutons visibles mais interdits | dashboard, rapports |
| Avancé GEO | analyser visibilité IA | modèles, citations, historique | résultats présentés comme absolus | GEO, prompts, comparaisons |

## 6. Structure UX globale

La structure UX doit rester stable entre les modules.

```text
+------------------+--------------------------------------------------+
| Sidebar          | Header : titre, site, période, état API          |
| Navigation       +--------------------------------------------------+
|                  | Filtres globaux / actions principales            |
|                  +--------------------------------------------------+
|                  | Contenu : KPI, tables, graphiques, formulaires   |
|                  +--------------------------------------------------+
|                  | Feedback : alertes, pagination, détails          |
+------------------+--------------------------------------------------+
```

Zones clés :

- sidebar principale ;
- header/top bar ;
- sélecteur de site ;
- filtres globaux ;
- zone de contenu ;
- panneaux secondaires éventuels ;
- feedback utilisateur.

## 7. Parcours de connexion et accès

Ce document ne définit pas l'implémentation d'authentification. Il cadre seulement les comportements UX.

Comportements attendus :

- au lancement, l'application vérifie l'accès et l'état API si ces mécanismes sont disponibles ;
- une session expirée doit expliquer qu'une reconnexion est nécessaire ;
- un accès refusé doit indiquer que les droits sont insuffisants ;
- une API indisponible doit afficher un message clair et une action de réessai ;
- les détails techniques restent masqués, avec trace ID éventuel.

Messages attendus :

- `Accès refusé : droits insuffisants pour cette action.`
- `Session expirée. Reconnectez-vous pour continuer.`
- `API indisponible. Réessayez ou vérifiez l'état du backend.`

## 8. Parcours tableau de bord général

Parcours nominal :

1. Ouvrir le dashboard.
2. Choisir un site si le module est filtré par site.
3. Choisir une période.
4. Lire les KPI principaux.
5. Identifier les alertes.
6. Accéder au détail depuis un KPI, une alerte ou une table de synthèse.

États :

| État | Comportement | Action utilisateur |
|---|---|---|
| Nominal | KPI, graphiques et alertes visibles | consulter, filtrer, ouvrir détail |
| Chargement | skeleton ou texte d'attente | attendre |
| Vide | expliquer l'absence de données | changer période, configurer |
| Erreur API | message avec retry | réessayer |
| Données partielles | signaler la source manquante | consulter détails |

Le dashboard doit aider à décider quoi regarder ensuite, pas remplacer toutes les vues détaillées.

## 9. Parcours sélection de site

Le sélecteur de site définit le contexte de nombreuses vues.

Matrice sélection de site :

| Situation | Comportement attendu | Message | Action |
|---|---|---|---|
| Site sélectionné | les données se rechargent dans le contexte | `Site actif : {nom}` | consulter |
| Aucun site | afficher empty state | `Aucun site configuré.` | ajouter/configurer si autorisé |
| Site désactivé | données consultables selon règles | `Site désactivé.` | réactiver si autorisé |
| Changement avec saisie non sauvegardée | bloquer ou confirmer | `Des modifications ne sont pas enregistrées.` | rester ou quitter |
| API indisponible | conserver ancien état si possible | `Impossible de changer de site.` | réessayer |

La mémorisation du site peut être envisagée plus tard, mais ce document ne l'impose pas.

## 10. Parcours SEO

Les parcours SEO doivent combiner synthèse et analyse détaillée.

Matrice parcours SEO :

| Parcours | Écran concerné | Données clés | Action utilisateur | Risque UX |
|---|---|---|---|---|
| Consulter performance SEO | dashboard SEO | clics, impressions, CTR, positions | ouvrir détail | confondre hausse et succès |
| Analyser mots-clés | table mots-clés | mot-clé, position, URL cible | filtrer, trier | table trop dense |
| Filtrer | SEO/table | site, période, intention, statut | combiner filtres | filtres invisibles |
| Consulter URL cible | détail URL | URL, statut, métriques | ouvrir analyse | URL tronquée sans tooltip |
| Identifier progression | table/KPI | variation, période | ouvrir historique | couleur seule |
| Identifier régression | table/KPI | perte position, trafic | prioriser | rouge abusif |
| Accéder opportunités | recommandations | type, impact, effort | qualifier | promesse non justifiée |
| Données absentes | empty state | période/source | changer filtre | vide confondu avec erreur |

## 11. Parcours GEO

Les parcours GEO doivent rester prudents : les résultats IA ne doivent pas être présentés comme des certitudes absolues.

Matrice parcours GEO :

| Parcours | Données affichées | Action utilisateur | Prudence UX |
|---|---|---|---|
| Consulter visibilité IA | score, période, modèles | ouvrir détail | expliquer l'échelle |
| Filtrer par plateforme IA | ChatGPT, Gemini, Claude, Copilot, Perplexity | comparer | repères internes sobres |
| Comparer plateformes | présence, citations, absence | analyser écarts | ne pas copier logos/couleurs |
| Voir présence | réponse, modèle, date | consulter source | distinguer présence et qualité |
| Voir absence | absence de mention | vérifier prompt | ne pas marquer rouge par défaut |
| Citation marque | extrait court, source | ouvrir détail | contexte obligatoire |
| Citation concurrent | concurrent, modèle, date | comparer | warning selon objectif |
| Historique | évolution temporelle | détecter tendance | période visible |

Les plateformes IA doivent être nommées en texte et représentées par des repères internes sobres.

## 12. Parcours mots-clés

Parcours liste :

- ouvrir la liste ;
- rechercher un mot-clé ;
- filtrer par site, intention, catégorie ou statut ;
- trier par position, variation ou date ;
- ouvrir une URL cible ;
- exporter si autorisé.

Parcours création/modification :

- ouvrir le formulaire ;
- saisir mot-clé, URL cible, intention, catégorie, statut ;
- valider les champs ;
- enregistrer ;
- afficher succès ou erreur.

Règles :

- état vide : `Aucun mot-clé configuré.`
- validation : message proche du champ ;
- suppression : confirmation obligatoire ;
- export : respecter permissions et périmètre filtré.

## 13. Parcours contenus

Les contenus peuvent couvrir page marque, catégorie, fiche produit, landing page et blog.

Parcours :

- consulter la liste des contenus ;
- filtrer par type, site, statut ou catégorie ;
- ouvrir un contenu ;
- lire briefing, statut et données associées ;
- éditer seulement si cette capacité existe dans le périmètre validé ;
- gérer l'absence de contenu par empty state.

Règles :

- ne pas promettre une édition si elle n'est pas décidée ;
- distinguer contenu éditorial, page SEO et rapport ;
- afficher les statuts avec libellé clair.

## 14. Parcours concurrents

Parcours :

- consulter la liste concurrents ;
- ajouter un concurrent si autorisé ;
- modifier nom, domaine, statut ou association ;
- comparer un concurrent avec un site ou domaine ;
- désactiver ou supprimer avec confirmation ;
- afficher les données absentes sans erreur technique.

Règles UX :

- statut actif/inactif visible ;
- comparaison explicite ;
- suppression protégée ;
- domaine concurrent non confondu avec site interne.

## 15. Parcours rapports

Parcours consultation :

- ouvrir la liste des rapports ;
- filtrer par type, période, statut ;
- consulter statut en cours, terminé ou erreur ;
- ouvrir un rapport terminé ;
- exporter si la fonctionnalité et les droits le permettent.

États :

- en cours : progression ou message d'attente ;
- terminé : date, type, période ;
- erreur : cause compréhensible et action possible ;
- aucune donnée : expliquer le filtre ou la période.

La génération ou préparation de rapport peut être documentée comme intention future, sans promesse fonctionnelle.

## 16. Parcours configuration

La configuration manipule des paramètres sensibles.

Matrice configuration :

| Action | Risque | Confirmation | Feedback |
|---|---|---:|---|
| Modifier paramètre | incohérence | selon impact | sauvegarde réussie ou erreur |
| Gérer clé API | fuite secret | oui selon action | clé masquée |
| Tester connexion | faux positif | non | résultat clair |
| Import configuration | écrasement | oui | résumé import |
| Export configuration | exfiltration | selon contenu | export prêt |
| Configuration incomplète | blocage module | non | élément manquant |
| Annuler | perte saisie | si modifications | retour état initial |

Les secrets sont toujours masqués. Aucun tooltip, log visible ou message ne doit exposer une clé complète.

## 17. Parcours administration

Les parcours administration concernent utilisateurs, rôles, permissions et accès.

Règles :

- actions sensibles visibles uniquement si autorisées ;
- accès refusé avec message clair ;
- modification de droits confirmée ;
- activation/désactivation explicite ;
- suppression seulement si prévue et confirmée ;
- aucun secret affiché ;
- l'interface ne décide jamais seule des permissions finales.

Message recommandé : `Accès refusé : droits insuffisants pour gérer les permissions.`

## 18. Parcours logs et observabilité

Parcours :

- ouvrir la vue logs ;
- filtrer par niveau, période et module ;
- consulter un détail log ;
- copier un trace ID si disponible ;
- masquer informations sensibles ;
- distinguer message utilisateur et détail technique ;
- afficher un empty state si aucun log.

Règles :

- niveau log visible en texte ;
- erreurs techniques non exposées brutes ;
- trace ID utile au support ;
- aucune clé, token ou payload sensible visible.

## 19. Comportements des formulaires

Les formulaires doivent protéger la saisie et limiter les erreurs.

Comportements :

- validation immédiate pour formats simples ;
- validation au submit pour règles serveur ;
- erreurs proches des champs ;
- champs obligatoires visibles ;
- aides contextuelles courtes ;
- sauvegarde avec état loading ;
- succès discret ;
- annulation visible ;
- protection contre perte de données non sauvegardées.

Checklist formulaire UX :

- [ ] Labels visibles.
- [ ] Champs obligatoires indiqués.
- [ ] Aide utile.
- [ ] Erreurs compréhensibles.
- [ ] Données conservées après erreur.
- [ ] Loading de sauvegarde.
- [ ] Annulation disponible.
- [ ] Secrets masqués.

## 20. Comportements des tables

Les tables servent à explorer, comparer et agir.

Comportements :

- tri visible ;
- recherche locale ou API selon contexte ;
- filtres actifs visibles ;
- pagination stable ;
- sélection ligne lisible ;
- actions par ligne à droite ;
- actions groupées seulement après sélection ;
- colonnes longues tronquées avec tooltip ;
- état vide, chargement et erreur distincts ;
- densité compacte mais lisible.

Checklist table UX :

- [ ] Tri et filtres disponibles.
- [ ] Pagination indique total.
- [ ] Actions de ligne cohérentes.
- [ ] Valeurs longues lisibles.
- [ ] Empty state différent de l'erreur.
- [ ] Retry si erreur récupérable.
- [ ] Données numériques alignées.

## 21. Comportements des dashboards

Les dashboards guident vers le détail.

Matrice états dashboard :

| État dashboard | Message | Action | Priorité |
|---|---|---|---|
| Nominal | KPI et alertes disponibles | ouvrir détail | haute |
| Chargement | `Chargement du dashboard...` | attendre | moyenne |
| Données absentes | `Aucune donnée pour cette période.` | changer période | moyenne |
| Données partielles | `Certaines sources sont indisponibles.` | voir détails | haute |
| API indisponible | `Dashboard indisponible : API non joignable.` | réessayer | haute |
| Données anciennes | `Données non à jour.` | actualiser | moyenne |

Les KPI doivent toujours afficher période, contexte et sens métier.

## 22. Comportements des modales

Règles :

- ouverture centrée et contextualisée ;
- titre clair ;
- focus placé dans la modale ;
- fermeture explicite ;
- annulation visible ;
- validation nommée ;
- clic extérieur permis seulement si aucune perte ou risque ;
- touche Escape autorisée sauf action critique en cours ;
- action destructive avec texte d'impact ;
- contenu long interdit, préférer page dédiée.

Une modale ne doit pas devenir un écran complet caché.

## 23. Feedback utilisateur

| Situation | Message attendu | Composant | Action possible |
|---|---|---|---|
| Succès | `Enregistrement terminé.` | toast ou inline | continuer |
| Avertissement | `Configuration incomplète.` | alerte | compléter |
| Erreur | `Impossible de charger les données.` | error state | réessayer |
| Information | `Synchronisation lancée.` | toast | suivre |
| Sauvegarde | `Sauvegarde en cours...` | bouton loading | attendre |
| Import/export | `Export en préparation.` | notification | voir détail |
| API indisponible | `API indisponible.` | alerte | réessayer |
| Accès refusé | `Droits insuffisants.` | page/alerte | demander accès |
| Données absentes | `Aucune donnée disponible.` | empty state | changer filtre |

## 24. États UX transverses

Matrice états UX :

| État | Comportement | Message | Action |
|---|---|---|---|
| Loading | bloquer zone concernée | opération nommée | attendre |
| Empty | expliquer absence | message métier | créer, filtrer, configurer |
| Error | afficher cause probable | message clair | réessayer |
| Disabled | réduire interaction | raison si utile | aucune |
| Readonly | valeur lisible | non modifiable | consulter |
| Partial data | garder données disponibles | source manquante | voir détails |
| Offline/API indisponible | conserver si possible | API indisponible | réessayer |
| Forbidden | bloquer action | droits insuffisants | demander accès |
| Unauthorized | session requise | reconnecter | se reconnecter |
| Stale data | signaler ancienneté | données non à jour | actualiser |
| Unsaved changes | prévenir perte | modifications non enregistrées | rester/quitter |

## 25. UX des actions destructives

Actions concernées :

- suppression ;
- désactivation ;
- remplacement de configuration ;
- import sensible ;
- modification de droits ;
- reset.

Règles :

- confirmation obligatoire ;
- libellé explicite ;
- bouton danger ;
- annulation visible ;
- ressource nommée ;
- impact expliqué.

Exemple conceptuel :

```text
Supprimer le site "Europ-Arm" ?
Cette action retirera le site de la liste suivie. Confirmez uniquement si vous êtes certain.
[Annuler] [Supprimer]
```

## 26. UX des imports/exports

Parcours import :

- choisir le fichier ;
- valider format et contenu ;
- présenter un résumé si cette capacité est prévue ;
- lancer l'import ;
- afficher progression ;
- afficher succès, erreurs ou résultat partiel.

Parcours export :

- choisir périmètre ;
- vérifier permissions ;
- lancer export ;
- afficher préparation ;
- signaler succès ou échec.

Règles :

- import non destructif autant que possible ;
- export sensible avec prudence ;
- aucun secret exporté en clair ;
- erreurs par section si disponibles.

## 27. UX des erreurs API

Types :

- API indisponible ;
- timeout ;
- erreur serveur ;
- erreur validation backend ;
- droits insuffisants ;
- données introuvables.

Règles :

- message utilisateur clair ;
- détail technique masqué ;
- trace ID éventuel ;
- action `Réessayer` si récupérable ;
- ne pas effacer les données existantes si un refresh échoue ;
- distinguer 401, 403, 404, 422, 500 et 503 côté message.

Exemple : `Le backend ne répond pas. Réessayez dans quelques instants.`

## 28. UX des données sensibles

Règles :

- clés API masquées ;
- secrets non copiés dans logs visibles ;
- permissions affichées clairement si utile ;
- rôles compréhensibles ;
- exports sensibles signalés ;
- messages prudents ;
- pas d'exposition involontaire ;
- pas de secret dans tooltip.

Une valeur masquée peut indiquer les derniers caractères si la politique le permet, par exemple `sk-************9a2f`.

## 29. UX accessibilité

Règles :

- navigation clavier possible ;
- focus visible ;
- labels toujours présents ;
- messages d'erreur associés aux champs ;
- icônes accompagnées quand l'information est importante ;
- contraste suffisant ;
- taille cliquable suffisante ;
- ordre logique ;
- ne pas dépendre uniquement de la couleur.

Checklist UX accessibilité :

- [ ] Parcours réalisable au clavier.
- [ ] Focus visible.
- [ ] Labels explicites.
- [ ] Erreurs lisibles.
- [ ] Icônes critiques accompagnées.
- [ ] Contraste conforme.
- [ ] Couleur non seule.

## 30. UX Desktop PySide6

Spécificités Desktop :

- densité plus importante possible ;
- usage de fenêtres, panneaux ou split views si utile ;
- interactions clavier/souris stables ;
- chargements non bloquants autant que possible ;
- erreurs réseau affichées sans crash ;
- navigation stable via sidebar ;
- état API visible ;
- aucun accès direct à PostgreSQL ;
- communication exclusivement via FastAPI HTTP REST et ApiClient.

Le Desktop présente les données et orchestre l'interaction. Il ne porte pas la logique métier principale.

## 31. UX futur React

Le futur React doit conserver :

- mêmes parcours ;
- mêmes libellés ;
- mêmes états ;
- mêmes règles de feedback ;
- composants équivalents ;
- respect des mêmes confirmations ;
- responsive futur ;
- cohérence avec Desktop.

Différences acceptables :

- rendu natif web ;
- animations sobres ;
- adaptation responsive ;
- composants techniques différents.

Aucun framework UI React n'est imposé ici.

## 32. Cohérence Desktop / React

| Parcours | Desktop PySide6 | Futur React | Règle commune |
|---|---|---|---|
| Dashboard | page avec KPI et tables | route dashboard | mêmes KPI et états |
| Table | table Qt | table web | tri, filtres, pagination |
| Formulaire | widgets Qt | composants contrôlés | labels, erreurs, loading |
| Configuration | pages/panneaux | pages ou panels | secrets masqués |
| Administration | tables et modales | tables et dialogs | confirmations |
| Logs | table filtrée | table filtrée | trace ID, niveaux |
| Erreur API | error state | error state | message + retry |
| Accès refusé | page/alerte | page/alerte | droits insuffisants |

## 33. Microcopy

Les libellés doivent être courts, précis et orientés métier.

| Contexte | Bon libellé | Libellé à éviter | Raison |
|---|---|---|---|
| Sauvegarde | `Enregistrer` | `OK` | action explicite |
| Suppression | `Supprimer le site` | `Supprimer` seul | ressource nommée |
| API | `API indisponible` | `Erreur inconnue` | cause utile |
| Validation URL | `Saisissez une URL valide.` | `Champ invalide` | correction claire |
| Accès | `Droits insuffisants` | `403` | compréhensible |
| Empty SEO | `Aucune donnée SEO pour cette période.` | `Aucun résultat` | contexte |
| Secret | `Clé API masquée` | clé complète | sécurité |
| Import | `Import en cours...` | `Traitement` | action nommée |

## 34. Anti-patterns UX

À éviter :

- écran sans action évidente ;
- message d'erreur vague ;
- données absentes sans explication ;
- action destructive trop facile ;
- navigation qui change selon les pages ;
- filtres invisibles ;
- dashboard surchargé ;
- tables sans pagination ;
- icônes seules ambiguës ;
- formulaire sans confirmation sur perte de données ;
- secrets visibles ;
- logs trop techniques exposés à l'utilisateur ;
- résultats IA présentés comme certitudes absolues ;
- état vide traité comme une erreur.

## 35. Scénarios utilisateur conceptuels

| Scénario | Objectif | Étapes | Feedback attendu | Erreurs possibles | Résultat attendu |
|---|---|---|---|---|---|
| Performance SEO d'un site | comprendre l'état SEO | choisir site, période, lire KPI, ouvrir détail | KPI chargés, filtres visibles | API indisponible, aucune donnée | priorités identifiées |
| Visibilité GEO multi-IA | comparer modèles | ouvrir GEO, filtrer plateformes, comparer | présence/absence contextualisée | données partielles | tendance comprise |
| Créer un mot-clé | suivre une requête | ouvrir formulaire, saisir, valider | succès ou erreurs champs | doublon, URL invalide | mot-clé ajouté |
| Corriger config API | rendre module opérationnel | ouvrir configuration, lire alerte, compléter | clé masquée, test clair | clé invalide | configuration utilisable |
| Consulter erreur logs | diagnostiquer | filtrer ERROR, ouvrir détail, copier trace ID | détail sans secret | logs indisponibles | support informé |
| Modifier permissions | ajuster accès | ouvrir admin, sélectionner utilisateur, modifier | confirmation explicite | accès refusé | droits mis à jour |
| Exporter un rapport | partager synthèse | filtrer rapports, choisir export | export lancé/terminé | permission, API | fichier disponible si prévu |
| Absence de données | comprendre vide | lire empty state, vérifier filtre/période | message explicatif | confusion avec erreur | action suivante claire |

## 36. Checklists finales

| Checklist | Points à valider |
|---|---|
| Écran | titre, contexte, action principale, états visibles |
| Parcours | objectif clair, étapes courtes, retour utilisateur |
| Formulaire | labels, validation, erreurs, sauvegarde, annulation |
| Table | filtres, tri, pagination, actions, états |
| Dashboard | site, période, KPI, alertes, drill-down |
| Erreur | message utile, action possible, trace ID si disponible |
| Sécurité | secrets masqués, droits clairs, confirmations |
| Accessibilité | clavier, focus, labels, contraste, couleur non seule |
| Desktop/React | mêmes libellés, mêmes états, mêmes règles |

## 37. Conclusion

`docs/design/UI_UX.md` finalise le socle design documentaire en reliant les principes, couleurs, icônes et composants aux parcours utilisateurs concrets.

Il doit servir de référence pour concevoir les écrans Desktop PySide6 actuels et préparer le futur frontend React avec des parcours cohérents, sûrs, lisibles et orientés métier.
