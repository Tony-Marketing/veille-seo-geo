"""Service Desktop de gestion des taches projet."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

ProjectTaskErrorCode = Literal[
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
class PaginatedProjectTasks:
    """Paginated project tasks payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class ProjectTasksServiceError(RuntimeError):
    """Readable error raised when project tasks cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: ProjectTaskErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class ProjectTasksService:
    """Manage project tasks through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_project_tasks(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedProjectTasks:
        """Return project tasks from the paginated API response."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search

        try:
            payload = self.api_client.get("/project-tasks", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise ProjectTasksServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def create_project_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a project task through the REST API."""

        try:
            response = self.api_client.post("/project-tasks", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_project_task_response(response)

    def update_project_task(self, project_task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a project task through the REST API."""

        try:
            response = self.api_client.put(f"/project-tasks/{project_task_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_project_task_response(response)

    def delete_project_task(self, project_task_id: int) -> None:
        """Delete a project task through the REST API."""

        try:
            self.api_client.delete(f"/project-tasks/{project_task_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedProjectTasks:
        """Validate and normalize the paginated project tasks response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedProjectTasks(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_project_task_response(self, payload: Any) -> dict[str, Any]:
        """Validate and normalize a single project task response."""

        if not isinstance(payload, dict):
            raise ProjectTasksServiceError(
                "Reponse API inattendue : la tache projet retournee n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> ProjectTasksServiceError:
        """Convert low-level API errors to project tasks service errors."""

        if exc.status_code == 401:
            return ProjectTasksServiceError(
                "Authentification requise pour gerer les taches projet.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return ProjectTasksServiceError(
                "Permission insuffisante pour gerer les taches projet.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 404:
            return ProjectTasksServiceError(
                "Tache projet introuvable.",
                code="not_found",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 409:
            return ProjectTasksServiceError(
                "Une tache projet avec ces informations existe deja.",
                code="conflict",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 422:
            return ProjectTasksServiceError(
                "Les donnees envoyees sont invalides.",
                code="validation_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return ProjectTasksServiceError(
                "Erreur serveur pendant la gestion des taches projet.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return ProjectTasksServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return ProjectTasksServiceError(
                "Erreur reseau pendant le chargement des taches projet.",
                code="network_error",
                details=exc.details,
            )
        return ProjectTasksServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
