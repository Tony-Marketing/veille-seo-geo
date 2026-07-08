"""Service Desktop de gestion des utilisateurs, roles et permissions."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

UsersErrorCode = Literal[
    "bad_request",
    "unauthorized",
    "forbidden",
    "not_found",
    "conflict",
    "validation_error",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class PaginatedUsersResponse:
    """Paginated payload consumed by the users Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class UsersServiceError(RuntimeError):
    """Readable error raised when users data cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: UsersErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class UsersService:
    """Manage users, roles and permissions through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_users(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> PaginatedUsersResponse:
        """Return users from the paginated REST API."""

        return self._get_paginated(
            "/users",
            params=self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order),
        )

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a user through the REST API."""

        return self._send_resource("post", "/users", payload=payload, resource_name="utilisateur")

    def update_user(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a user through the REST API."""

        return self._send_resource("put", f"/users/{user_id}", payload=payload, resource_name="utilisateur")

    def set_user_active(self, user_id: int, is_active: bool) -> dict[str, Any]:
        """Activate or deactivate a user through the existing update endpoint."""

        return self.update_user(user_id, {"is_active": is_active})

    def list_roles(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = 100,
        search: str | None = None,
    ) -> PaginatedUsersResponse:
        """Return roles from the paginated REST API."""

        return self._get_paginated(
            "/roles",
            params=self._pagination_params(page=page, page_size=page_size, search=search, sort="name", order="asc"),
        )

    def list_permissions(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = 100,
        search: str | None = None,
    ) -> PaginatedUsersResponse:
        """Return permissions from the paginated REST API."""

        return self._get_paginated(
            "/permissions",
            params=self._pagination_params(page=page, page_size=page_size, search=search, sort="module", order="asc"),
        )

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> PaginatedUsersResponse:
        try:
            payload = self.api_client.get(path, params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise UsersServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc), "payload": payload},
            ) from exc

    def _send_resource(
        self,
        method: Literal["post", "put"],
        path: str,
        *,
        payload: dict[str, Any],
        resource_name: str,
    ) -> dict[str, Any]:
        try:
            if method == "post":
                response = self.api_client.post(path, json=payload)
            else:
                response = self.api_client.put(path, json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_resource_response(response, resource_name)

    def _parse_paginated_response(self, payload: Any) -> PaginatedUsersResponse:
        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedUsersResponse(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise UsersServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _pagination_params(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        sort: str | None,
        order: str | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        self._add_optional_filters(params, {"search": search, "sort": sort, "order": order})
        return params

    def _add_optional_filters(self, params: dict[str, Any], filters: dict[str, Any]) -> None:
        for key, value in filters.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> UsersServiceError:
        if exc.status_code == 400:
            return UsersServiceError(
                "Requete utilisateurs invalide.",
                code="bad_request",
                status_code=400,
                details=exc.details,
            )
        if exc.status_code == 401:
            return UsersServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return UsersServiceError(
                "Permission administrateur requise.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 404:
            return UsersServiceError("Ressource introuvable.", code="not_found", status_code=404, details=exc.details)
        if exc.status_code == 409:
            return UsersServiceError("Cette valeur existe deja.", code="conflict", status_code=409, details=exc.details)
        if exc.status_code == 422:
            return UsersServiceError(
                "Donnees utilisateurs invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return UsersServiceError(
                "Erreur serveur pendant la gestion utilisateurs.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return UsersServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return UsersServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return UsersServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
