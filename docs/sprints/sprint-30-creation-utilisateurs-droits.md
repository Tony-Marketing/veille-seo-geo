# Sprint 30 — Création des utilisateurs, rôles et préparation des droits

Statut : implémentation backend et Desktop réalisée — aucun React modifié

## Objectif fonctionnel

Le Sprint 30 implémente la création des utilisateurs par invitation email avec attribution des rôles et activation du
compte sous 24 heures.

L'objectif est de permettre à un administrateur de créer une invitation depuis l'application Desktop, d'associer un ou
plusieurs rôles au compte créé, puis de laisser l'utilisateur définir lui-même son mot de passe via un lien d'activation.

L'administrateur ne saisit aucun mot de passe définitif. Le backend crée un utilisateur inactif, génère un token
d'activation sécurisé valable 24 heures, stocke uniquement son hash, déclenche l'envoi email, puis active le compte
après validation du token et du mot de passe choisi par l'utilisateur.

## Contexte issu du Sprint 29

À l'issue du Sprint 29, la fenêtre de connexion n'est plus ouverte automatiquement au démarrage de l'application ni lors
de la navigation vers une page Desktop.

L'application démarre directement sur le Dashboard. Le lazy loading des pages Desktop est conservé. Les éléments
`LoginDialog`, `AuthService`, `ApiClient` et la gestion des tokens restent en place pour une réactivation ultérieure.

Ce contexte impose de préparer le Sprint 30 sans réactiver prématurément l'authentification obligatoire au lancement et
sans modifier le comportement de démarrage existant.

## Périmètre inclus

- Création d'utilisateurs par invitation email depuis l'application Desktop.
- Attribution de rôles existants à un utilisateur invité.
- Consultation des rôles existants via les endpoints REST backend disponibles.
- Préparation de l'affichage des droits associés aux rôles.
- Gestion des erreurs API côté Desktop avec messages utilisateur lisibles.
- Respect strict du flux Desktop `Page -> Service -> ApiClient -> API REST`.
- Ajout des endpoints backend nécessaires au flux d'invitation et d'activation.
- Génération, hash, expiration et validation du token côté backend.
- Envoi email côté backend via un service configurable et mockable.
- Activation du compte par définition du mot de passe par l'utilisateur.
- Conservation du lazy loading des pages Desktop.
- Correction minimale pour ne plus ouvrir automatiquement `LoginDialog` au démarrage ni à la navigation.
- Tests backend et Desktop ciblés.

## Hors périmètre

- Aucune modification React.
- Aucune refonte de l'authentification.
- Aucun SSO, OAuth externe, 2FA ou récupération de mot de passe par email.
- Aucun accès direct Desktop à PostgreSQL.
- Aucun accès direct Desktop à Google Search Console, Google Analytics 4 ou Bing Webmaster Tools.
- Aucune logique métier ajoutée dans les pages PySide6.
- Aucune logique métier de permissions dans le Desktop.
- Aucun commit, push ou pull request.

## Architecture Desktop obligatoire

Le développement Desktop respecte le flux suivant :

```text
Page -> Service -> ApiClient -> API REST
```

Règles obligatoires :

- Le Desktop ne communique jamais directement avec PostgreSQL.
- Le Desktop ne communique jamais directement avec Google Search Console.
- Le Desktop ne communique jamais directement avec Google Analytics 4.
- Le Desktop ne communique jamais directement avec Bing Webmaster Tools.
- Le Desktop ne contient pas de logique métier.
- Les pages PySide6 gèrent uniquement l'affichage et les interactions utilisateur.
- Les services Desktop encapsulent les appels API.
- `ApiClient` reste le point unique de communication HTTP.
- Les erreurs HTTP, réseau et contrats de réponse inattendus doivent être traités dans le service ou au plus près de la
  couche d'appel, puis affichés proprement par la page.
- Le lazy loading existant ne doit pas être cassé.

## Architecture Backend obligatoire

Le développement backend respecte le flux suivant :

```text
Routes -> Services -> Repositories -> Models
```

Règles obligatoires :

- Les routes FastAPI ne contiennent pas de logique métier.
- Les routes appellent les services.
- Les services contiennent la logique métier.
- Les repositories contiennent uniquement l'accès aux données SQLAlchemy.
- Les modèles SQLAlchemy représentent les tables.
- Les schémas Pydantic gèrent les entrées et sorties API.
- Les endpoints d'administration doivent être protégés par authentification et droits admin.
- Toute évolution de structure de base de données doit passer par une migration Alembic dédiée.
- Aucun secret, mot de passe en clair ou token ne doit être exposé dans les réponses, les logs ou le code.

## Règles de sécurité Git

- Travailler exclusivement sur la branche `sprint-30`.
- Ne jamais développer directement sur `main`.
- Ne pas committer pendant ce sprint sans validation explicite.
- Ne pas pousser de branche pendant ce sprint sans validation explicite.
- Ne pas ouvrir de pull request pendant ce sprint sans validation explicite.
- Vérifier `git status --short`, `git diff --stat` et `git diff --check` en fin de tâche.
- Ne pas inclure de secret, token, clé API ou donnée sensible dans la documentation.

## Flux d'invitation implémenté

1. L'administrateur ouvre le module Desktop `Utilisateurs`.
2. Il clique sur `Inviter un utilisateur`.
3. Le dialogue Desktop demande uniquement l'email et les rôles.
4. Le service Desktop appelle `POST /api/v1/admin/users/invite` via `ApiClient`.
5. Le backend vérifie les droits admin, l'unicité de l'email et l'existence des rôles.
6. Le backend crée un utilisateur inactif avec un hash temporaire non communiqué.
7. Le backend génère un token cryptographiquement sûr, valable 24 heures.
8. Le backend stocke uniquement le hash du token dans `user_invitations`.
9. Le backend envoie l'email d'activation via le service SMTP configurable.
10. L'utilisateur active son compte via `POST /api/v1/auth/activate` avec token et mot de passe.
11. Le backend vérifie token, expiration, usage unique et mot de passe, puis active le compte.

## Endpoints ajoutés

- `POST /api/v1/admin/users/invite` : invitation utilisateur par email, protégé par `require_admin`.
- `POST /api/v1/auth/activate` : activation publique du compte invité avec token et nouveau mot de passe.

Les réponses n'exposent pas le token brut. Le token brut est uniquement utilisé pour construire le lien d'activation
envoyé par email.

## Modèle et migration ajoutés

Table ajoutée : `user_invitations`.

Champs :

- `id` ;
- `user_id` ;
- `email` ;
- `token_hash` ;
- `expires_at` ;
- `used_at` ;
- `created_at` ;
- `updated_at` ;
- `created_by_user_id`.

Migration ajoutée :

- `backend/alembic/versions/20260708_0010_create_user_invitations.py`.

La migration utilise uniquement des instructions Alembic explicites : `op.create_table`, `op.create_index`,
`op.drop_index` et `op.drop_table`.

## Envoi email

Le service `backend/app/services/email.py` encapsule l'envoi SMTP.

Configuration ajoutée :

- `activation_base_url` ;
- `smtp_host` ;
- `smtp_port` ;
- `smtp_username` ;
- `smtp_password` ;
- `smtp_from_email` ;
- `smtp_use_tls`.

Aucune clé SMTP n'est codée en dur. En tests, un faux service email est injecté et aucun email réel n'est envoyé.

Si la configuration SMTP est absente ou si l'envoi échoue, l'API retourne une erreur propre `503` avec le message
`Email d'activation non envoye.`.

## Critères d'acceptation

- Un administrateur peut inviter un utilisateur depuis la page Desktop `Utilisateurs`.
- Les rôles disponibles sont récupérés depuis l'API REST backend existante.
- La création utilisateur transmet les données attendues au backend via `ApiClient`.
- Les rôles sélectionnés sont envoyés selon le contrat backend existant.
- Aucun mot de passe n'est saisi par l'administrateur.
- Le token d'activation est stocké uniquement sous forme hashée.
- Le lien d'activation est valable 24 heures.
- L'activation définit le mot de passe utilisateur et marque l'invitation comme utilisée.
- Les droits restent pilotés par les rôles backend, sans décision métier côté Desktop.
- Les erreurs 400, 401, 403, 409, 422, 500 et les erreurs réseau sont affichées proprement.
- Aucune requête directe à PostgreSQL n'est introduite dans le Desktop.
- Aucun appel direct aux connecteurs externes n'est introduit dans le Desktop.
- Aucune logique métier n'est placée dans les pages PySide6.
- Le démarrage direct sur le Dashboard reste inchangé.
- `LoginDialog` n'est plus ouvert automatiquement au démarrage ni lors de la navigation.
- Le lazy loading reste opérationnel.
- Les tests ajoutés passent.

## Fichiers créés

- `backend/app/models/user_invitation.py` ;
- `backend/app/repositories/user_invitations.py` ;
- `backend/app/services/email.py` ;
- `backend/app/services/user_invitations.py` ;
- `backend/alembic/versions/20260708_0010_create_user_invitations.py` ;
- `desktop/ui/dialogs/user_invitation_dialog.py` ;
- `tests/api/test_user_invitations_routes.py` ;
- `tests/services/test_user_invitations_services.py` ;
- `tests/desktop/test_user_invitation_dialog.py`.

## Fichiers modifiés

- `desktop/services/users_service.py`
- `desktop/ui/users_page.py`
- `desktop/ui/main_window.py`
- `backend/app/api/v1/routes/admin.py`
- `backend/app/api/v1/routes/auth.py`
- `backend/app/core/config.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/auth.py`
- `tests/desktop/test_users_service.py`
- `tests/desktop/test_main_window_lazy_loading.py`
- `docs/sprints/sprint-30-creation-utilisateurs-droits.md`

`desktop/ui/dialogs/user_dialog.py`, `desktop/core/api_client.py`, `desktop/core/constants.py`, React, GSC, GA4, Bing,
crawls, SEO/GEO et Dashboard ne sont pas modifiés.

## Tests ajoutés

- Création d'une invitation utilisateur par un administrateur.
- Refus d'invitation sans droits admin.
- Refus d'email déjà utilisé.
- Génération d'une invitation expirant à 24 heures.
- Stockage hashé du token.
- Activation réussie avec token valide.
- Refus token invalide.
- Refus token expiré.
- Refus token déjà utilisé.
- Mot de passe correctement hashé à l'activation.
- Invitation marquée comme utilisée.
- Aucun email réel envoyé en tests.
- Appel Desktop du service d'invitation utilisateur.
- Absence de champ mot de passe dans le dialogue d'invitation.
- Lazy loading Desktop sans ouverture automatique de `LoginDialog`.

## Commandes de validation

Commandes à exécuter en fin de Sprint 30 :

```powershell
git status --short
git diff --stat
git diff --check
python -m ruff check .
python -m pytest
```

Dans cette session Windows, la commande littérale `python` peut être absente du PATH. Le Python embarqué Codex peut alors
être utilisé pour exécuter les mêmes validations.

## Risques et points d'attention

- Ne pas réactiver la fenêtre de connexion automatiquement sans demande explicite.
- Ne pas casser le démarrage direct sur le Dashboard.
- Ne pas dupliquer `AuthService`, `ApiClient` ou la gestion des tokens.
- Ne pas créer une logique locale de droits dans le Desktop.
- Ne pas masquer côté Desktop une protection qui doit rester appliquée côté backend.
- Ne pas exposer les mots de passe, tokens ou informations sensibles dans les logs.
- Ne pas introduire d'incohérence entre rôles, permissions et utilisateurs.
- Ne pas ajouter d'autre migration ou endpoint backend hors flux d'invitation.
- Ne pas modifier React dans le cadre du Sprint 30 Desktop.
- Prévoir des messages utilisateur clairs pour les refus d'accès et les erreurs de validation.

## Limites

Le flux ne réactive pas automatiquement l'authentification Desktop au démarrage ni lors de la navigation.

Le Desktop ne reçoit pas le token brut et ne construit pas le lien d'activation. Le token brut reste côté backend et
sert uniquement à composer l'email d'activation.

L'envoi SMTP nécessite une configuration d'environnement. En tests, l'envoi est remplacé par un faux service email afin
de garantir qu'aucun email réel n'est envoyé.

Aucune modification React, GSC, GA4, Bing Webmaster Tools, crawler, analyse SEO/GEO ou Dashboard n'est réalisée.
