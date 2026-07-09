"""Service Desktop du centre de monitoring."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

MonitoringErrorCode = Literal[
    "unauthorized",
    "forbidden",
    "validation_error",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class MonitoringPayload:
    """Generic monitoring payload consumed by the Desktop UI."""

    data: dict[str, Any]


@dataclass(frozen=True)
class MonitoringPaginatedPayload:
    """Paginated monitoring payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class MonitoringServiceError(RuntimeError):
    """Readable error raised when monitoring data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: MonitoringErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class MonitoringService:
    """Load monitoring data through the REST API client."""

    BASE_PATH = "/admin/monitoring"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_overview(self) -> MonitoringPayload:
        """Return monitoring overview data from the API."""

        return MonitoringPayload(data=self._get_object("/overview", "overview"))

    def list_connectors(self) -> list[dict[str, Any]]:
        """Return connector health data from the API."""

        try:
            payload = self.api_client.get(f"{self.BASE_PATH}/connectors")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(payload, list):
            raise MonitoringServiceError(
                "Reponse API inattendue : les connecteurs ne sont pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        return [item for item in payload if isinstance(item, dict)]

    def list_events(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        severity: str | None = None,
        event_type: str | None = None,
    ) -> MonitoringPaginatedPayload:
        """Return paginated monitoring events from the API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(params, {"severity": severity, "event_type": event_type})
        return self._get_paginated("/events", params=params)

    def list_sync_schedules(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> MonitoringPaginatedPayload:
        """Return synchronization schedules as seen by monitoring."""

        return self._get_paginated("/sync-schedules", params=self._pagination_params(page=page, page_size=page_size))

    def _get_object(self, path: str, resource_name: str) -> dict[str, Any]:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(payload, dict):
            raise MonitoringServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> MonitoringPaginatedPayload:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated(payload)

    def _parse_paginated(self, payload: Any) -> MonitoringPaginatedPayload:
        if not isinstance(payload, dict):
            raise MonitoringServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise MonitoringServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise MonitoringServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return MonitoringPaginatedPayload(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _pagination_params(self, *, page: int, page_size: int) -> dict[str, Any]:
        return {"page": page, "page_size": page_size}

    def _add_optional_filters(self, params: dict[str, Any], filters: dict[str, Any]) -> None:
        for key, value in filters.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> MonitoringServiceError:
        if exc.status_code == 401:
            return MonitoringServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return MonitoringServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 422:
            return MonitoringServiceError(
                "Parametres de monitoring invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return MonitoringServiceError(
                "Erreur serveur monitoring.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return MonitoringServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return MonitoringServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return MonitoringServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
