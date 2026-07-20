"""Desktop service for transverse recommendation REST calls."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

RecommendationsErrorCode = Literal[
    "unauthorized",
    "forbidden",
    "validation_error",
    "not_found",
    "conflict",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class RecommendationPayload:
    """One generic recommendation API object."""

    data: dict[str, Any]


@dataclass(frozen=True)
class RecommendationPaginatedPayload:
    """Paginated recommendations consumed by the Desktop page."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class RecommendationsServiceError(RuntimeError):
    """Readable recommendation error exposed to the Desktop page."""

    def __init__(
        self,
        message: str,
        *,
        code: RecommendationsErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class RecommendationsService:
    """Access Recommendation REST endpoints exclusively through ApiClient."""

    BASE_PATH = "/recommendations"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_recommendations(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        website_id: int | None = None,
        source: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> RecommendationPaginatedPayload:
        """Return filtered and paginated recommendations."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        self._add_optional(
            params,
            {
                "website_id": website_id,
                "source": source,
                "category": category,
                "priority": priority,
                "status": status,
                "search": search,
                "sort": sort,
                "order": order,
            },
        )
        return self._get_paginated("", params=params)

    def get_summary(
        self,
        *,
        website_id: int | None = None,
        source: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> RecommendationPayload:
        """Return recommendation summary counters."""

        params: dict[str, Any] = {}
        self._add_optional(
            params,
            {
                "website_id": website_id,
                "source": source,
                "category": category,
                "priority": priority,
                "status": status,
                "search": search,
            },
        )
        return RecommendationPayload(self._get_object("/summary", params=params))

    def get_recommendation(self, recommendation_id: int) -> RecommendationPayload:
        """Return one recommendation."""

        return RecommendationPayload(self._get_object(f"/{recommendation_id}", params={}))

    def update_status(self, recommendation_id: int, status: str) -> RecommendationPayload:
        """Update one recommendation lifecycle state."""

        try:
            payload = self.api_client.patch(f"{self.BASE_PATH}/{recommendation_id}/status", json={"status": status})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return RecommendationPayload(self._parse_object(payload))

    def _get_object(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_object(payload)

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> RecommendationPaginatedPayload:
        payload = self._get_object(path, params=params)
        missing = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing:
            raise RecommendationsServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing))}.",
                code="unexpected",
                details={"payload": payload},
            )
        if not isinstance(payload["items"], list):
            raise RecommendationsServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return RecommendationPaginatedPayload(
            items=[item for item in payload["items"] if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _parse_object(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise RecommendationsServiceError(
                "Reponse API recommandations inattendue.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _add_optional(self, params: dict[str, Any], values: dict[str, Any]) -> None:
        for key, value in values.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> RecommendationsServiceError:
        if exc.status_code == 401:
            return RecommendationsServiceError("Authentification requise.", code="unauthorized", status_code=401)
        if exc.status_code == 403:
            return RecommendationsServiceError("Permission insuffisante.", code="forbidden", status_code=403)
        if exc.status_code == 404:
            return RecommendationsServiceError("Recommandation introuvable.", code="not_found", status_code=404)
        if exc.status_code == 409:
            return RecommendationsServiceError(
                "Transition de statut impossible.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return RecommendationsServiceError(
                "Parametres de recommandations invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return RecommendationsServiceError(
                "Erreur serveur recommandations.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return RecommendationsServiceError("Backend indisponible.", code="backend_unavailable")
            return RecommendationsServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return RecommendationsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
