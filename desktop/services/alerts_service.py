"""Service Desktop du centre d'alertes."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

AlertsErrorCode = Literal[
    "unauthorized",
    "forbidden",
    "validation_error",
    "not_found",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class AlertPayload:
    """Generic alert payload consumed by the Desktop UI."""

    data: dict[str, Any]


@dataclass(frozen=True)
class AlertPaginatedPayload:
    """Paginated alert payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class AlertsServiceError(RuntimeError):
    """Readable error raised when alert data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: AlertsErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class AlertsService:
    """Load and update alerts through the REST API client."""

    BASE_PATH = "/alerts"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_summary(self) -> AlertPayload:
        """Return alert summary data from the API."""

        return AlertPayload(data=self._get_object("/summary", "summary"))

    def list_alerts(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        source: str | None = None,
        search: str | None = None,
    ) -> AlertPaginatedPayload:
        """Return paginated alerts from the API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(
            params,
            {
                "status": status,
                "severity": severity,
                "category": category,
                "source": source,
                "search": search,
            },
        )
        return self._get_paginated("", params=params)

    def get_alert(self, alert_id: int) -> AlertPayload:
        """Return one alert from the API."""

        return AlertPayload(data=self._get_object(f"/{alert_id}", "alert"))

    def refresh_from_monitoring(self) -> AlertPayload:
        """Ask the API to refresh alerts from persisted monitoring data."""

        return AlertPayload(data=self._post_object("/refresh-from-monitoring", "refresh"))

    def acknowledge_alert(self, alert_id: int) -> AlertPayload:
        """Acknowledge one alert through the API."""

        return AlertPayload(data=self._post_object(f"/{alert_id}/acknowledge", "alert"))

    def resolve_alert(self, alert_id: int) -> AlertPayload:
        """Resolve one alert through the API."""

        return AlertPayload(data=self._post_object(f"/{alert_id}/resolve", "alert"))

    def _get_object(self, path: str, resource_name: str) -> dict[str, Any]:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_object(payload, resource_name)

    def _post_object(self, path: str, resource_name: str) -> dict[str, Any]:
        try:
            payload = self.api_client.post(f"{self.BASE_PATH}{path}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_object(payload, resource_name)

    def _parse_object(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise AlertsServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> AlertPaginatedPayload:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated(payload)

    def _parse_paginated(self, payload: Any) -> AlertPaginatedPayload:
        if not isinstance(payload, dict):
            raise AlertsServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise AlertsServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise AlertsServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return AlertPaginatedPayload(
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

    def _to_service_error(self, exc: ApiClientError) -> AlertsServiceError:
        if exc.status_code == 401:
            return AlertsServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return AlertsServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 404:
            return AlertsServiceError("Alerte introuvable.", code="not_found", status_code=404, details=exc.details)
        if exc.status_code == 422:
            return AlertsServiceError(
                "Parametres d'alertes invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return AlertsServiceError(
                "Erreur serveur alertes.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return AlertsServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return AlertsServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return AlertsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
