# Sprint 24A - Google Search Console Backend

## 1. Objectif

Le Sprint 24A definit le socle backend complet permettant d'integrer Google Search Console dans l'application Veille
SEO-GEO Groupe A.P&Partner.

Ce sprint prepare l'import, la persistance, l'historisation et l'exposition REST des donnees Google Search Console. Il
constitue la source de verite backend sur laquelle reposera le Sprint 24B Desktop.

Principes obligatoires :

- toute la logique metier Google Search Console est portee cote backend ;
- les imports sont realises uniquement par les services backend ;
- le Desktop n'accede jamais directement a Google ;
- le Desktop n'accede jamais directement a PostgreSQL ;
- le Sprint 24B exploitera exclusivement l'API REST exposee par le backend ;
- aucune authentification Google n'est geree cote Desktop.

Le backend devient l'unique point d'entree applicatif pour les donnees Google Search Console. Les couches Desktop,
Dashboard et rapports consommeront les donnees via l'API REST, sans contourner les services backend.

## 2. Architecture

L'architecture retenue respecte l'organisation existante du projet :

```text
Routes
    |
    v
Services
    |
    v
Repositories
    |
    v
Models
```

Responsabilites par couche :

| Couche | Responsabilite |
| --- | --- |
| Routes FastAPI | Exposer les endpoints REST et deleguer aux services. |
| Services | Porter la logique metier, l'orchestration des imports et la gestion des erreurs. |
| Repositories | Encapsuler les acces SQLAlchemy aux donnees persistantes. |
| Models | Representer les entites persistantes Google Search Console. |
| Schemas Pydantic | Normaliser les payloads d'entree et de sortie de l'API. |
| Connecteur Google | Echanger avec Google Search Console sans contenir de logique metier applicative. |

Les routes doivent rester fines :

- validation du payload HTTP ;
- recuperation du contexte utilisateur si necessaire ;
- appel au service backend ;
- choix du code de reponse ;
- retour d'un schema Pydantic.

Elles ne doivent contenir aucune logique metier, aucun appel direct a Google, aucune requete SQLAlchemy directe et aucune
regle d'import.

Les repositories sont limites aux operations de persistance :

- lire ;
- ecrire ;
- mettre a jour ;
- supprimer ;
- filtrer et paginer via SQLAlchemy.

Les services portent toute la logique applicative :

- validation des droits et du perimetre ;
- orchestration du connecteur Google ;
- normalisation des donnees importees ;
- idempotence des imports ;
- historisation ;
- gestion des erreurs ;
- coordination avec les repositories.

## 3. Base De Donnees

Le Sprint 24A prevoit l'ajout de tables dediees aux donnees Google Search Console. Cette section decrit les entites
principales attendues sans detailler le SQL.

### 3.1 Proprietes Google Search Console

Les proprietes representent les sites ou prefixes d'URL disponibles dans Google Search Console.

Role :

- conserver l'identifiant fonctionnel de la propriete ;
- rattacher une propriete Google a un site suivi par la plateforme lorsque cela est possible ;
- stocker son type, son statut et ses metadonnees utiles ;
- connaitre la derniere synchronisation disponible.

Ces donnees serviront de point d'entree aux imports de performances, d'indexation et de sitemaps.

### 3.2 Performances

Les performances representent les indicateurs Search Console historises.

Donnees attendues :

- clics ;
- impressions ;
- CTR ;
- position moyenne ;
- date ou periode ;
- dimensions possibles : page, requete, pays, appareil.

Ces donnees devront pouvoir etre filtrees et agregees par les services backend pour alimenter le Desktop, le Dashboard
et les rapports futurs.

### 3.3 Donnees D'Indexation

Les donnees d'indexation representent l'etat de couverture des URLs connues par Google.

Role :

- suivre les pages valides ;
- suivre les pages exclues ;
- identifier les erreurs ;
- identifier les avertissements ;
- conserver la date de collecte et le contexte de propriete.

Ces donnees permettront de croiser les informations Google avec les resultats de crawl, SEO et GEO.

### 3.4 Sitemaps

Les sitemaps representent les fichiers soumis ou detectes pour une propriete Google Search Console.

Role :

- stocker l'URL du sitemap ;
- conserver le statut connu ;
- suivre la derniere lecture ;
- stocker le nombre d'URLs declarees si disponible ;
- rattacher le sitemap a sa propriete.

Les actions futures sur les sitemaps devront rester orchestrees par le backend.

### 3.5 Historique Des Imports

L'historique des imports trace chaque operation de synchronisation.

Role :

- conserver le type d'import ;
- conserver la propriete concernee ;
- suivre le statut ;
- enregistrer les dates de debut et de fin ;
- compter les elements importes, ignores ou mis a jour ;
- conserver les erreurs lisibles ;
- permettre l'audit et le diagnostic.

Cette table est essentielle pour la robustesse, le support utilisateur et la comprehension de la fraicheur des donnees.

### 3.6 Configuration OAuth

Si necessaire, une configuration OAuth backend devra etre prevue.

Role :

- rattacher l'autorisation Google a un compte, une organisation ou une configuration applicative ;
- stocker les informations techniques necessaires au renouvellement des tokens ;
- conserver les dates d'expiration et de mise a jour ;
- isoler les secrets et tokens de toute exposition Desktop.

Aucun secret ne doit etre code en dur. Les tokens doivent etre stockes de maniere securisee selon les mecanismes
existants du projet.

## 4. Migration Alembic

La migration du Sprint 24A devra etre explicite et lisible.

Regles obligatoires :

- utiliser `op.create_table()` pour creer les tables ;
- utiliser `op.create_index()` pour creer les index ;
- definir explicitement les contraintes utiles ;
- prevoir les index necessaires aux filtres frequents ;
- fournir une fonction `downgrade()` coherente avec les conventions du projet.

Interdictions :

- ne jamais utiliser `Base.metadata.create_all()` ;
- ne jamais utiliser `Base.metadata.drop_all()` ;
- ne jamais creer la structure de base hors Alembic ;
- ne jamais masquer une migration structurelle dans du code applicatif.

Les index devront notamment faciliter :

- la recherche par propriete ;
- la recherche par date ;
- la recherche par URL ;
- la recherche par type d'import ;
- la consultation de l'historique.

## 5. Connecteur Google Search Console

Le connecteur Google Search Console est responsable uniquement des echanges avec Google.

Il devra etre :

- injectable ;
- mockable ;
- independant des services metier ;
- testable sans appel Internet ;
- remplaceable par une implementation factice en tests.

Responsabilites du connecteur :

- appeler les API Google Search Console autorisees ;
- transmettre les parametres techniques attendus par Google ;
- recuperer les reponses brutes ou semi-normalisees ;
- remonter les erreurs techniques de facon explicite ;
- ne pas persister directement les donnees ;
- ne pas connaitre les models SQLAlchemy ;
- ne pas contenir de regles metier applicatives.

Le connecteur ne decide pas quelles donnees doivent etre importees, historisees ou exposees. Ces decisions appartiennent
aux services backend.

## 6. OAuth

Le Sprint 24A prepare l'authentification OAuth cote backend.

Principes obligatoires :

- aucun secret Google n'est code en dur ;
- aucun token n'est expose au Desktop ;
- aucun flux OAuth n'est execute depuis le Desktop ;
- les tokens sont stockes de maniere securisee ;
- le chiffrement utilise les mecanismes existants du projet ;
- les erreurs d'autorisation sont converties en erreurs metier lisibles.

Le backend est responsable de :

- charger la configuration OAuth depuis l'environnement ou le stockage autorise ;
- renouveler les tokens lorsque c'est necessaire ;
- refuser proprement les imports si l'autorisation est absente ou invalide ;
- journaliser les echecs sans exposer de secret ;
- garantir que les droits applicatifs sont respectes.

Le Desktop ne connait ni les credentials Google, ni les tokens, ni les mecanismes de renouvellement.

## 7. Services Metier

Les services backend constituent le coeur du Sprint 24A.

Ils devront notamment gerer :

- recuperation des proprietes ;
- recuperation des performances ;
- recuperation des donnees d'indexation ;
- recuperation des sitemaps ;
- lancement des imports ;
- historisation des imports ;
- gestion des erreurs ;
- normalisation des donnees Google ;
- verification des droits ;
- idempotence des operations.

Flux conceptuel d'un import :

```text
Service Google Search Console
    |
    +-- valide la demande
    +-- verifie la propriete
    +-- cree une entree d'historique
    +-- appelle le connecteur Google
    +-- normalise les resultats
    +-- persiste via repositories
    +-- met a jour l'historique
    +-- retourne un statut REST
```

Les services ne doivent pas etre melanges aux routes. Ils doivent pouvoir etre testes directement avec un connecteur
mocke et des repositories controles.

Gestion des erreurs attendue :

| Erreur | Comportement attendu |
| --- | --- |
| Propriete inconnue | Refuser l'operation avec une erreur lisible. |
| OAuth absent ou invalide | Refuser l'import sans exposer de secret. |
| Quota Google atteint | Marquer l'import en erreur ou partiel selon le cas. |
| Reponse Google invalide | Conserver une erreur exploitable dans l'historique. |
| Donnees deja importees | Appliquer les regles d'idempotence. |
| Erreur base de donnees | Annuler proprement l'operation transactionnelle. |

## 8. Repositories

Les repositories Google Search Console encapsulent uniquement les acces SQLAlchemy.

Responsabilites attendues :

- creer une propriete ;
- mettre a jour une propriete ;
- rechercher une propriete ;
- lister les proprietes avec filtres ;
- inserer ou mettre a jour les performances ;
- lire les performances avec filtres et pagination ;
- inserer ou mettre a jour les donnees d'indexation ;
- inserer ou mettre a jour les sitemaps ;
- creer et mettre a jour l'historique des imports ;
- supprimer uniquement les donnees autorisees par les cas d'usage definis.

Les repositories ne doivent pas :

- appeler Google ;
- interpreter les quotas ;
- decider du statut metier final d'un import ;
- normaliser les payloads Google ;
- contenir de logique OAuth ;
- retourner de reponse HTTP.

Ils doivent rester predecibles, courts et faciles a tester.

## 9. API REST

Le Sprint 24A expose une API REST backend qui sera consommee par le Sprint 24B Desktop.

Familles d'endpoints prevues :

- proprietes ;
- performances ;
- indexation ;
- sitemaps ;
- import manuel ;
- historique des imports.

Les URLs definitives seront precisees lors de l'implementation, en coherence avec les conventions existantes de l'API.
Le present document ne fige pas les chemins exacts.

### 9.1 Proprietes

Role :

- lister les proprietes disponibles ;
- consulter le detail d'une propriete ;
- exposer l'etat de synchronisation ;
- permettre au Desktop de proposer une selection de propriete.

### 9.2 Performances

Role :

- consulter les indicateurs importes ;
- filtrer par propriete, periode, page, requete, pays ou appareil ;
- retourner des donnees deja normalisees ;
- eviter tout recalcul metier cote Desktop.

### 9.3 Indexation

Role :

- consulter les etats d'indexation importes ;
- restituer les erreurs et avertissements ;
- permettre les croisements futurs avec le crawl et les audits SEO.

### 9.4 Sitemaps

Role :

- lister les sitemaps connus ;
- consulter leur statut ;
- exposer la derniere lecture connue ;
- preparer d'eventuelles actions futures via backend.

### 9.5 Import Manuel

Role :

- declencher un import depuis une demande REST ;
- retourner le statut de lancement ou de fin selon le mode retenu ;
- garantir que le backend reste responsable de tout appel Google.

### 9.6 Historique Des Imports

Role :

- lister les imports ;
- consulter le detail d'un import ;
- afficher les statuts, durees, volumes et erreurs ;
- aider le Desktop a presenter la fraicheur des donnees.

Le Sprint 24B utilisera exclusivement ces endpoints. Il ne doit acceder ni a Google, ni a PostgreSQL, ni aux models
backend.

## 10. Import Des Donnees

Le flux d'import respecte la chaine suivante :

```text
Google Search Console
    |
    v
Connecteur
    |
    v
Services
    |
    v
Repositories
    |
    v
PostgreSQL
```

Les imports devront etre :

- idempotents ;
- journalises ;
- securises ;
- independants du Desktop ;
- relancables sans duplication incoherente ;
- rattaches a une propriete ;
- traces dans l'historique.

Idempotence attendue :

- une meme periode importee plusieurs fois ne doit pas creer de doublons incoherents ;
- les lignes existantes doivent etre mises a jour ou ignorees selon une regle explicite ;
- les cles fonctionnelles doivent etre documentees lors de l'implementation ;
- les erreurs partielles doivent etre visibles dans l'historique.

Journalisation attendue :

- statut de l'import ;
- date de debut ;
- date de fin ;
- type d'import ;
- nombre d'elements traites ;
- nombre d'elements crees ;
- nombre d'elements mis a jour ;
- nombre d'elements ignores ;
- message d'erreur si applicable.

Le Desktop peut demander un import manuel via REST, mais ne participe jamais au processus technique d'import.

## 11. Tests

Le Sprint 24A devra prevoir une strategie de tests complete.

Tests a prevoir :

- modeles ;
- repositories ;
- services ;
- connecteur mock ;
- API REST ;
- imports.

Principes obligatoires :

- aucun appel Internet ;
- connecteur Google mocke ;
- tests deterministes ;
- pas de dependance a un compte Google reel ;
- pas de secret dans les tests ;
- erreurs Google simulees par fixtures ou doubles de test.

Tests de modeles :

- contraintes principales ;
- relations entre proprietes et donnees importees ;
- dates et statuts ;
- champs obligatoires.

Tests de repositories :

- creation et lecture de proprietes ;
- upsert de performances ;
- filtres par periode et propriete ;
- lecture paginee ;
- creation et mise a jour d'historique d'import.

Tests de services :

- import de proprietes ;
- import de performances ;
- import d'indexation ;
- import de sitemaps ;
- idempotence ;
- gestion d'erreurs OAuth ;
- gestion d'erreurs connecteur ;
- historisation des echecs.

Tests API REST :

- consultation des proprietes ;
- consultation des performances ;
- consultation de l'indexation ;
- consultation des sitemaps ;
- lancement d'import manuel ;
- lecture de l'historique ;
- erreurs `404`, `422` et erreurs metier.

Tests de connecteur mock :

- reponses Google simulees ;
- erreurs de quota ;
- erreurs d'autorisation ;
- payloads incomplets ;
- timeouts simules.

## 12. Documentation

Le Sprint 24A prepare directement :

- Sprint 24B Google Search Console Desktop ;
- Sprint 25 Google Analytics 4 Backend.

La documentation future devra couvrir :

- les endpoints REST definitifs ;
- les schemas de reponse ;
- les regles d'idempotence ;
- les statuts d'import ;
- les erreurs metier ;
- les contraintes OAuth ;
- les limites connues des donnees Google.

Le Sprint 24A doit aussi rester compatible avec le Dashboard du Sprint 23. Les donnees Google Search Console enrichiront
les vues existantes sans remplacer les resultats de crawl, SEO ou GEO.

## 13. Hors Perimetre

Le Sprint 24A ne comprend pas :

- interface Desktop ;
- Dashboard ;
- Google Analytics ;
- Bing Webmaster Tools ;
- planification automatique ;
- appels Google depuis le Desktop ;
- rapports ;
- alertes ;
- automatisation periodique des imports ;
- implementation du Sprint 24B ;
- modification des modules SEO ou GEO hors points d'integration documentes.

Toute evolution de ces sujets devra etre traitee dans un sprint dedie.

## 14. Contraintes

Contraintes techniques du projet :

- FastAPI ;
- SQLAlchemy 2.x ;
- Alembic ;
- PostgreSQL ;
- Pydantic v2 ;
- architecture `Routes -> Services -> Repositories -> Models` ;
- aucun acces direct Desktop a PostgreSQL ;
- aucune logique metier dans les routes ;
- connecteur Google injectable ;
- imports idempotents ;
- tests sans Internet.

Contraintes de securite :

- aucun secret code en dur ;
- aucun token expose au Desktop ;
- stockage securise des tokens ;
- journalisation sans fuite de secret ;
- respect des permissions applicatives ;
- isolation des appels Google dans le connecteur backend.

Contraintes d'architecture :

- le Desktop consomme uniquement REST ;
- les services orchestrent les imports ;
- les repositories ne contiennent pas de logique metier ;
- le connecteur ne persiste pas les donnees ;
- les migrations passent exclusivement par Alembic ;
- les tests automatises utilisent des doubles de test pour Google.

## 15. Conclusion

Le Sprint 24A met en place toute l'infrastructure backend Google Search Console.

Il constitue le socle technique indispensable aux developpements suivants :

- Sprint 24B - Google Search Console Desktop ;
- Sprint 25 - Google Analytics 4 Backend ;
- Sprint 26 - Google Analytics 4 Desktop ;
- Sprint 27 - Bing Webmaster Tools.

Le backend devient l'unique point d'acces aux donnees Google Search Console pour l'ensemble de l'application. Il centralise
les imports, la securite OAuth, l'idempotence, la persistance, l'historisation et l'exposition REST.

Les developpements futurs devront respecter cette separation stricte : le backend porte la logique metier et les acces
Google ; le Desktop, le Dashboard et les rapports consomment uniquement les donnees exposees par l'API REST.
