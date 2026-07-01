"""Service Desktop de gestion des mots-cles."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

KeywordErrorCode = Literal[
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
class PaginatedKeywords:
    """Paginated keywords payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class KeywordsServiceError(RuntimeError):
    """Readable error raised when keywords cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: KeywordErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class KeywordsService:
    """Manage keywords through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_keywords(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedKeywords:
        """Return keywords from the paginated API response."""

        try:
            payload = self.api_client.get("/keywords", params={"page": page, "page_size": page_size})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        try:
            return self._parse_paginated_response(payload)
        except (TypeError, ValueError) as exc:
            raise KeywordsServiceError(
                f"Reponse API inattendue : {exc}",
                code="unexpected",
                details={"error": str(exc)},
            ) from exc

    def create_keyword(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a keyword through the REST API."""

        try:
            response = self.api_client.post("/keywords", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_keyword_response(response)

    def update_keyword(self, keyword_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update a keyword through the REST API."""

        try:
            response = self.api_client.put(f"/keywords/{keyword_id}", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        return self._parse_keyword_response(response)

    def delete_keyword(self, keyword_id: int) -> None:
        """Delete a keyword through the REST API."""

        try:
            self.api_client.delete(f"/keywords/{keyword_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedKeywords:
        """Validate and normalize the paginated keywords response."""

        if not isinstance(payload, dict):
            raise ValueError("la reponse n'est pas un objet pagine")

        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            fields = ", ".join(sorted(missing_fields))
            raise ValueError(f"champ(s) manquant(s) : {fields}")

        items = payload["items"]
        if not isinstance(items, list):
            raise ValueError("le champ items n'est pas une liste")

        return PaginatedKeywords(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_keyword_response(self, payload: Any) -> dict[str, Any]:
        """Validate and normalize a single keyword response."""

        if not isinstance(payload, dict):
            raise KeywordsServiceError(
                "Reponse API inattendue : le mot-cle retourne n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> KeywordsServiceError:
        """Convert low-level API errors to keywords service errors."""

        if exc.status_code == 401:
            return KeywordsServiceError(
                "Authentification requise pour gerer les mots-cles.",
                code="unauthorized",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 403:
            return KeywordsServiceError(
                "Permission insuffisante pour gerer les mots-cles.",
                code="forbidden",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 404:
            return KeywordsServiceError(
                "Mot-cle introuvable.",
                code="not_found",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 409:
            return KeywordsServiceError(
                "Un mot-cle avec ces informations existe deja.",
                code="conflict",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code == 422:
            return KeywordsServiceError(
                "Les donnees envoyees sont invalides.",
                code="validation_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return KeywordsServiceError(
                "Erreur serveur pendant la gestion des mots-cles.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return KeywordsServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return KeywordsServiceError(
                "Erreur reseau pendant le chargement des mots-cles.",
                code="network_error",
                details=exc.details,
            )
        return KeywordsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
