"""Service Desktop des planifications de synchronisation."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

SyncScheduleErrorCode = Literal[
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
class PaginatedSyncSchedulesResponse:
    """Paginated synchronization schedules payload consumed by Desktop."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class SyncSchedulesServiceError(RuntimeError):
    """Readable error raised when synchronization schedules cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: SyncScheduleErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class SyncSchedulesService:
    """Access synchronization schedule REST endpoints through ApiClient."""

    BASE_PATH = "/sync-schedules"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_schedules(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        sync_type: str | None = None,
        frequency: str | None = None,
        status: str | None = None,
        is_active: bool | None = None,
        website_id: int | None = None,
    ) -> PaginatedSyncSchedulesResponse:
        """Return synchronization schedules from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        self._add_optional_filters(
            params,
            {
                "sync_type": sync_type,
                "frequency": frequency,
                "status": status,
                "is_active": is_active,
                "website_id": website_id,
            },
        )
        try:
            payload = self.api_client.get(self.BASE_PATH, params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_response(payload)

    def create_schedule(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a synchronization schedule through the REST API."""

        try:
            response = self.api_client.post(self.BASE_PATH, json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response)

    def update_schedule(self, schedule_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a synchronization schedule through the REST API."""

        try:
            response = self.api_client.patch(f"{self.BASE_PATH}/{schedule_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response)

    def get_schedule(self, schedule_id: int) -> dict[str, Any]:
        """Return one synchronization schedule from the REST API."""

        try:
            response = self.api_client.get(f"{self.BASE_PATH}/{schedule_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response)

    def delete_schedule(self, schedule_id: int) -> None:
        """Soft-disable a synchronization schedule through the REST API."""

        try:
            self.api_client.delete(f"{self.BASE_PATH}/{schedule_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def enable_schedule(self, schedule_id: int) -> dict[str, Any]:
        """Enable one synchronization schedule through the REST API."""

        return self._post_action(schedule_id, "enable")

    def disable_schedule(self, schedule_id: int) -> dict[str, Any]:
        """Disable one synchronization schedule through the REST API."""

        return self._post_action(schedule_id, "disable")

    def recalculate_schedule(self, schedule_id: int) -> dict[str, Any]:
        """Recalculate one synchronization schedule through the REST API."""

        return self._post_action(schedule_id, "recalculate")

    def _post_action(self, schedule_id: int, action: str) -> dict[str, Any]:
        try:
            response = self.api_client.post(f"{self.BASE_PATH}/{schedule_id}/{action}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response)

    def _parse_paginated_response(self, payload: Any) -> PaginatedSyncSchedulesResponse:
        if not isinstance(payload, dict):
            raise SyncSchedulesServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise SyncSchedulesServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise SyncSchedulesServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return PaginatedSyncSchedulesResponse(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _parse_resource_response(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise SyncSchedulesServiceError(
                "Reponse API inattendue : la planification n'est pas un objet.",
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

    def _to_service_error(self, exc: ApiClientError) -> SyncSchedulesServiceError:
        if exc.status_code == 400:
            return SyncSchedulesServiceError("Requete planification invalide.", code="bad_request", status_code=400)
        if exc.status_code == 401:
            return SyncSchedulesServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return SyncSchedulesServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 404:
            return SyncSchedulesServiceError("Planification introuvable.", code="not_found", status_code=404)
        if exc.status_code == 409:
            return SyncSchedulesServiceError(
                "Action impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return SyncSchedulesServiceError(
                "Donnees de planification invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return SyncSchedulesServiceError(
                "Erreur serveur planifications.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return SyncSchedulesServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return SyncSchedulesServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return SyncSchedulesServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
