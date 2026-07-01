"""Service Desktop de consultation des sites Web."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

WebsiteErrorCode = Literal["unauthorized", "forbidden", "backend_unavailable", "network_error", "unexpected"]


@dataclass(frozen=True)
class PaginatedWebsites:
    """Paginated websites payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class WebsitesServiceError(RuntimeError):
    """Readable error raised when websites cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: WebsiteErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class WebsitesService:
    """Load websites through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_websites(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedWebsites:
        """Return websites from the paginated API response."""

        try:
            payload = self.api_client.get("/websites", params={"page": page, "page_size": page_size})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise WebsitesServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedWebsites:
        """Validate and normalize the paginated websites response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedWebsites(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _to_service_error(self, exc: ApiClientError) -> WebsitesServiceError:
        """Convert low-level API errors to websites service errors."""

        if exc.status_code == 401:
            return WebsitesServiceError(
                "Authentification requise pour charger les sites.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return WebsitesServiceError(
                "Permission insuffisante pour consulter les sites.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return WebsitesServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return WebsitesServiceError(
                "Erreur reseau pendant le chargement des sites.",
                code="network_error",
                details=exc.details,
            )
        return WebsitesServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
