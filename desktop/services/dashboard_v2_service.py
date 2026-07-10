"""Desktop service for Dashboard V2 REST calls."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

DashboardV2ErrorCode = Literal[
    "unauthorized",
    "forbidden",
    "validation_error",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class DashboardV2Payload:
    """Generic Dashboard V2 payload consumed by the Desktop UI."""

    data: dict[str, Any]


@dataclass(frozen=True)
class DashboardV2PaginatedPayload:
    """Paginated Dashboard V2 payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class DashboardV2ServiceError(RuntimeError):
    """Readable error raised when Dashboard V2 cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: DashboardV2ErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class DashboardV2Service:
    """Load Dashboard V2 data through the REST API client."""

    BASE_PATH = "/dashboard-v2"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_overview(self, **filters: Any) -> DashboardV2Payload:
        """Return Dashboard V2 overview data from the API."""

        return DashboardV2Payload(data=self._get_object("/overview", params=self._params(filters)))

    def get_trends(self, **filters: Any) -> DashboardV2Payload:
        """Return Dashboard V2 trends from the API."""

        return DashboardV2Payload(data=self._get_object("/trends", params=self._params(filters)))

    def list_websites(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        **filters: Any,
    ) -> DashboardV2PaginatedPayload:
        """Return Dashboard V2 website summaries from the API."""

        params = {"page": page, "page_size": page_size, **self._params(filters)}
        return self._get_paginated("/websites", params=params)

    def list_recommendations(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        **filters: Any,
    ) -> DashboardV2PaginatedPayload:
        """Return Dashboard V2 recommendations from the API."""

        params = {"page": page, "page_size": page_size, **self._params(filters)}
        return self._get_paginated("/recommendations", params=params)

    def _get_object(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(payload, dict):
            raise DashboardV2ServiceError(
                "Reponse API inattendue : la reponse Dashboard V2 n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> DashboardV2PaginatedPayload:
        payload = self._get_object(path, params=params)
        missing = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing:
            raise DashboardV2ServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise DashboardV2ServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return DashboardV2PaginatedPayload(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _params(self, filters: dict[str, Any]) -> dict[str, Any]:
        params: dict[str, Any] = {}
        for key, value in filters.items():
            if value is None or value == "":
                continue
            params[key] = value
        return params

    def _to_service_error(self, exc: ApiClientError) -> DashboardV2ServiceError:
        if exc.status_code == 401:
            return DashboardV2ServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return DashboardV2ServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 422:
            return DashboardV2ServiceError(
                "Parametres Dashboard V2 invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return DashboardV2ServiceError(
                "Erreur serveur Dashboard V2.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return DashboardV2ServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return DashboardV2ServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return DashboardV2ServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
