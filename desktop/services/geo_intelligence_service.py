"""Desktop service for GEO Intelligence REST calls."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

GeoIntelligenceErrorCode = Literal[
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
class GeoIntelligencePayload:
    """One object response consumed by the Desktop page."""

    data: dict[str, Any]


@dataclass(frozen=True)
class GeoIntelligencePaginatedPayload:
    """Paginated GEO Intelligence response."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class GeoIntelligenceServiceError(RuntimeError):
    """Readable GEO Intelligence error exposed to the Desktop page."""

    def __init__(
        self,
        message: str,
        *,
        code: GeoIntelligenceErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class GeoIntelligenceService:
    """Access GEO Intelligence exclusively through ApiClient."""

    BASE_PATH = "/geo-intelligence"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_snapshots(self, *, page: int = 1, page_size: int = 20, **filters: Any) -> GeoIntelligencePaginatedPayload:
        """Return filtered and paginated snapshots."""

        params = {"page": page, "page_size": page_size, **self._params(filters)}
        payload = self._get("", params=params)
        missing = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing or not isinstance(payload.get("items"), list):
            raise GeoIntelligenceServiceError(
                "Reponse GEO Intelligence paginee invalide.",
                code="unexpected",
                details=payload,
            )
        response_filters = payload.get("filters")
        return GeoIntelligencePaginatedPayload(
            items=[item for item in payload["items"] if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=response_filters if isinstance(response_filters, dict) else None,
        )

    def get_summary(self, **filters: Any) -> GeoIntelligencePayload:
        """Return consolidated KPI data."""

        return GeoIntelligencePayload(self._get("/summary", params=self._params(filters)))

    def get_providers(self) -> GeoIntelligencePayload:
        """Return provider configuration states."""

        return GeoIntelligencePayload(self._get("/providers", params={}))

    def get_history(self, **filters: Any) -> GeoIntelligencePayload:
        """Return provider history."""

        return GeoIntelligencePayload(self._get("/history", params=self._params(filters)))

    def import_observations(self, observations: list[dict[str, Any]]) -> GeoIntelligencePayload:
        """Send an explicit normalized import batch."""

        try:
            payload = self.api_client.post(f"{self.BASE_PATH}/import", json={"observations": observations})
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return GeoIntelligencePayload(self._parse_object(payload))

    def _get(self, path: str, *, params: dict[str, Any]) -> dict[str, Any]:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_object(payload)

    def _parse_object(self, payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GeoIntelligenceServiceError(
                "Reponse GEO Intelligence inattendue.",
                code="unexpected",
                details=payload,
            )
        return payload

    def _params(self, filters: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in filters.items() if value is not None and value != ""}

    def _to_service_error(self, exc: ApiClientError) -> GeoIntelligenceServiceError:
        messages: dict[int, tuple[str, GeoIntelligenceErrorCode]] = {
            401: ("Authentification requise.", "unauthorized"),
            403: ("Permission GEO Intelligence insuffisante.", "forbidden"),
            404: ("Ressource GEO Intelligence introuvable.", "not_found"),
            409: ("Conflit pendant l'import GEO Intelligence.", "conflict"),
            422: ("Parametres GEO Intelligence invalides.", "validation_error"),
        }
        if exc.status_code in messages:
            message, code = messages[exc.status_code]
            return GeoIntelligenceServiceError(message, code=code, status_code=exc.status_code, details=exc.details)
        if exc.status_code is not None and exc.status_code >= 500:
            return GeoIntelligenceServiceError(
                "Erreur serveur GEO Intelligence.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            code: GeoIntelligenceErrorCode = (
                "backend_unavailable" if isinstance(exc.__cause__, httpx.ConnectError) else "network_error"
            )
            return GeoIntelligenceServiceError("Backend GEO Intelligence indisponible.", code=code, details=exc.details)
        return GeoIntelligenceServiceError(
            f"Erreur API GEO Intelligence ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
