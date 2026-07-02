"""Service Desktop de gestion des crawls."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

CrawlErrorCode = Literal[
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
class PaginatedCrawls:
    """Paginated crawl sessions payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


@dataclass(frozen=True)
class PaginatedCrawlPages:
    """Paginated crawl pages payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class CrawlsServiceError(RuntimeError):
    """Readable error raised when crawls cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: CrawlErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class CrawlsService:
    """Manage crawl sessions through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_crawls(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedCrawls:
        """Return crawl sessions from the paginated API response."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        try:
            payload = self.api_client.get("/crawls", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_crawls(payload)

    def create_crawl(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a crawl session through the REST API."""

        try:
            response = self.api_client.post("/crawls", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "crawl")

    def start_crawl(self, crawl_id: int, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Start a crawl through the REST API."""

        try:
            response = self.api_client.post(f"/crawls/{crawl_id}/start", json=payload or {})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "crawl")

    def cancel_crawl(self, crawl_id: int) -> dict[str, Any]:
        """Request crawl cancellation through the REST API."""

        try:
            response = self.api_client.post(f"/crawls/{crawl_id}/cancel")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "crawl")

    def list_crawl_pages(
        self,
        crawl_id: int,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedCrawlPages:
        """Return pages discovered by a crawl session."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        try:
            payload = self.api_client.get(f"/crawls/{crawl_id}/pages", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        parsed = self._parse_paginated_response(payload)
        return PaginatedCrawlPages(**parsed.__dict__)

    def _parse_paginated_crawls(self, payload: Any) -> PaginatedCrawls:
        parsed = self._parse_paginated_response(payload)
        return PaginatedCrawls(**parsed.__dict__)

    def _parse_paginated_response(self, payload: Any) -> PaginatedCrawls:
        if not isinstance(payload, dict):
            raise CrawlsServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise CrawlsServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise CrawlsServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        return PaginatedCrawls(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise CrawlsServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> CrawlsServiceError:
        if exc.status_code == 401:
            return CrawlsServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return CrawlsServiceError(
                "Permission insuffisante.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 404:
            return CrawlsServiceError("Crawl introuvable.", code="not_found", status_code=404, details=exc.details)
        if exc.status_code == 409:
            return CrawlsServiceError(
                "Action impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return CrawlsServiceError(
                "Donnees invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return CrawlsServiceError(
                "Erreur serveur.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return CrawlsServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return CrawlsServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return CrawlsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
