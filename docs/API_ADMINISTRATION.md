# API Administration Backend

Cette API couvre le Sprint 06 et respecte la chaîne `Routes -> Services -> Repositories -> Models`.

## Endpoints principaux

- `GET /api/v1/admin/dashboard` : indicateurs d'administration.
- `GET|POST|PUT|DELETE /api/v1/admin/settings` : paramètres globaux.
- `GET|POST|PUT|DELETE /api/v1/admin/ai-providers` : fournisseurs IA.
- `GET|POST|PUT|DELETE /api/v1/admin/ai-models` : modèles IA.
- `GET|POST|PUT|DELETE /api/v1/admin/api-keys` : clés API chiffrées.
- `GET|POST /api/v1/admin/audit-logs` : journal d'audit.
- `GET|POST|PUT /api/v1/admin/error-logs` : journal des erreurs.
- `GET|POST|PUT /api/v1/admin/system-parameters` : paramètres SEO, GEO et IA.
- `GET /api/v1/admin/health` : santé des services.
- `GET /api/v1/admin/config/export` : export JSON de la configuration non secrète.

## Sécurité

Les routes d'administration utilisent la dépendance `require_admin`.
Les clés API sont chiffrées en base via `ApiKeyService` et ne sont jamais renvoyées en clair.
Les réponses exposent uniquement `masked_value` et `value_fingerprint`.

## Pagination

Les listes acceptent `page`, `page_size`, `search`, `sort` et `order`.
