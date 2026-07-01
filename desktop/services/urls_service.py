"""Service Desktop de gestion des URLs."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

UrlErrorCode = Literal[
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
class PaginatedUrls:
    """Paginated URLs payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class URLsServiceError(RuntimeError):
    """Readable error raised when URLs cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: UrlErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class URLsService:
    """Manage URLs through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_urls(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedUrls:
        """Return URLs from the paginated API response."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search

        try:
            payload = self.api_client.get("/urls", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise URLsServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def create_url(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create an URL through the REST API."""

        try:
            response = self.api_client.post("/urls", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_url_response(response)

    def update_url(self, url_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update an URL through the REST API."""

        try:
            response = self.api_client.put(f"/urls/{url_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_url_response(response)

    def delete_url(self, url_id: int) -> None:
        """Delete an URL through the REST API."""

        try:
            self.api_client.delete(f"/urls/{url_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedUrls:
        """Validate and normalize the paginated URLs response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedUrls(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_url_response(self, payload: Any) -> dict[str, Any]:
        """Validate and normalize a single URL response."""

        if not isinstance(payload, dict):
            raise URLsServiceError(
                "Reponse API inattendue : l'URL retournee n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> URLsServiceError:
        """Convert low-level API errors to URLs service errors."""

        if exc.status_code == 401:
            return URLsServiceError(
                "Authentification requise pour gerer les URLs.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return URLsServiceError(
                "Permission insuffisante pour gerer les URLs.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 404:
            return URLsServiceError(
                "URL introuvable.",
                code="not_found",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 409:
            return URLsServiceError(
                "Une URL avec ces informations existe deja.",
                code="conflict",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 422:
            return URLsServiceError(
                "Les donnees envoyees sont invalides.",
                code="validation_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return URLsServiceError(
                "Erreur serveur pendant la gestion des URLs.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return URLsServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return URLsServiceError(
                "Erreur reseau pendant le chargement des URLs.",
                code="network_error",
                details=exc.details,
            )
        return URLsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
