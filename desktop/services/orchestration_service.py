"""Service Desktop de l'orchestrateur de traitements."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

OrchestrationErrorCode = Literal[
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
class OrchestrationPayload:
    """Generic orchestration payload consumed by the Desktop UI."""

    data: dict[str, Any]


@dataclass(frozen=True)
class OrchestrationPaginatedPayload:
    """Paginated orchestration payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class OrchestrationServiceError(RuntimeError):
    """Readable error raised when orchestration data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: OrchestrationErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class OrchestrationService:
    """Load and update orchestration data through the REST API client."""

    BASE_PATH = "/orchestration"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_summary(self) -> OrchestrationPayload:
        """Return orchestration summary data from the API."""

        return OrchestrationPayload(data=self._get_object("/summary", "summary"))

    def list_jobs(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        status: str | None = None,
        job_type: str | None = None,
        schedule_id: int | None = None,
        search: str | None = None,
    ) -> OrchestrationPaginatedPayload:
        """Return paginated processing jobs from the API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(
            params,
            {
                "status": status,
                "job_type": job_type,
                "schedule_id": schedule_id,
                "search": search,
            },
        )
        return self._get_paginated("/jobs", params=params)

    def get_job(self, job_id: int) -> OrchestrationPayload:
        """Return one processing job from the API."""

        return OrchestrationPayload(data=self._get_object(f"/jobs/{job_id}", "job"))

    def list_job_logs(self, job_id: int) -> OrchestrationPaginatedPayload:
        """Return processing job logs from the API."""

        return self._get_paginated(f"/jobs/{job_id}/logs", params=self._pagination_params(page=1, page_size=100))

    def retry_job(self, job_id: int) -> OrchestrationPayload:
        """Request a controlled retry through the API."""

        return OrchestrationPayload(data=self._post_object(f"/jobs/{job_id}/retry", "job"))

    def cancel_job(self, job_id: int) -> OrchestrationPayload:
        """Cancel a job through the API."""

        return OrchestrationPayload(data=self._post_object(f"/jobs/{job_id}/cancel", "job"))

    def run_scheduler_once(self) -> OrchestrationPayload:
        """Ask the API to run one scheduler cycle."""

        return OrchestrationPayload(data=self._post_object("/scheduler/run-once", "scheduler"))

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

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> OrchestrationPaginatedPayload:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated(payload)

    def _parse_object(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise OrchestrationServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _parse_paginated(self, payload: Any) -> OrchestrationPaginatedPayload:
        if not isinstance(payload, dict):
            raise OrchestrationServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise OrchestrationServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise OrchestrationServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return OrchestrationPaginatedPayload(
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

    def _to_service_error(self, exc: ApiClientError) -> OrchestrationServiceError:
        if exc.status_code == 401:
            return OrchestrationServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return OrchestrationServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 404:
            return OrchestrationServiceError("Job introuvable.", code="not_found", status_code=404, details=exc.details)
        if exc.status_code == 422:
            return OrchestrationServiceError(
                "Parametres d'orchestration invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return OrchestrationServiceError(
                "Erreur serveur orchestration.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return OrchestrationServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return OrchestrationServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return OrchestrationServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
