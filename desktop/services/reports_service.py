"""Service Desktop de gestion des rapports."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

ReportErrorCode = Literal[
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
class PaginatedReports:
    """Paginated reports payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class ReportsServiceError(RuntimeError):
    """Readable error raised when reports cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: ReportErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class ReportsService:
    """Manage reports through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_reports(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedReports:
        """Return reports from the paginated API response."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search

        try:
            payload = self.api_client.get("/reports", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise ReportsServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def create_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a report through the REST API."""

        try:
            response = self.api_client.post("/reports", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_report_response(response)

    def update_report(self, report_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a report through the REST API."""

        try:
            response = self.api_client.put(f"/reports/{report_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_report_response(response)

    def delete_report(self, report_id: int) -> None:
        """Delete a report through the REST API."""

        try:
            self.api_client.delete(f"/reports/{report_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedReports:
        """Validate and normalize the paginated reports response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedReports(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_report_response(self, payload: Any) -> dict[str, Any]:
        """Validate and normalize a single report response."""

        if not isinstance(payload, dict):
            raise ReportsServiceError(
                "Reponse API inattendue : le rapport retourne n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> ReportsServiceError:
        """Convert low-level API errors to reports service errors."""

        if exc.status_code == 401:
            return ReportsServiceError(
                "Authentification requise pour gerer les rapports.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return ReportsServiceError(
                "Permission insuffisante pour gerer les rapports.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 404:
            return ReportsServiceError(
                "Rapport introuvable.",
                code="not_found",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 409:
            return ReportsServiceError(
                "Un rapport avec ces informations existe deja.",
                code="conflict",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 422:
            return ReportsServiceError(
                "Les donnees envoyees sont invalides.",
                code="validation_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return ReportsServiceError(
                "Erreur serveur pendant la gestion des rapports.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return ReportsServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return ReportsServiceError(
                "Erreur reseau pendant le chargement des rapports.",
                code="network_error",
                details=exc.details,
            )
        return ReportsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
