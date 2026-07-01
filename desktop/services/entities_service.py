"""Service Desktop de gestion des entites."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

EntityErrorCode = Literal[
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
class PaginatedEntities:
    """Paginated entities payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class EntitiesServiceError(RuntimeError):
    """Readable error raised when entities cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: EntityErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class EntitiesService:
    """Manage entities through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_entities(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedEntities:
        """Return entities from the paginated API response."""

        try:
            payload = self.api_client.get("/entities", params={"page": page, "page_size": page_size})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise EntitiesServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def create_entity(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create an entity through the REST API."""

        try:
            response = self.api_client.post("/entities", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_entity_response(response)

    def update_entity(self, entity_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update an entity through the REST API."""

        try:
            response = self.api_client.put(f"/entities/{entity_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_entity_response(response)

    def delete_entity(self, entity_id: int) -> None:
        """Delete an entity through the REST API."""

        try:
            self.api_client.delete(f"/entities/{entity_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedEntities:
        """Validate and normalize the paginated entities response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedEntities(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_entity_response(self, payload: Any) -> dict[str, Any]:
        """Validate and normalize a single entity response."""

        if not isinstance(payload, dict):
            raise EntitiesServiceError(
                "Reponse API inattendue : l'entite retournee n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> EntitiesServiceError:
        """Convert low-level API errors to entities service errors."""

        if exc.status_code == 401:
            return EntitiesServiceError(
                "Authentification requise pour gerer les entites.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return EntitiesServiceError(
                "Permission insuffisante pour gerer les entites.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 404:
            return EntitiesServiceError(
                "Entite introuvable.",
                code="not_found",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 409:
            return EntitiesServiceError(
                "Une entite avec ces informations existe deja.",
                code="conflict",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 422:
            return EntitiesServiceError(
                "Les donnees envoyees sont invalides.",
                code="validation_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return EntitiesServiceError(
                "Erreur serveur pendant la gestion des entites.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return EntitiesServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return EntitiesServiceError(
                "Erreur reseau pendant le chargement des entites.",
                code="network_error",
                details=exc.details,
            )
        return EntitiesServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
