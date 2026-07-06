"""Service Desktop de gestion des analyses GEO."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

GeoAnalysisErrorCode = Literal[
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
class PaginatedGeoAnalyses:
    """Paginated GEO analyses payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class GeoAnalysisServiceError(RuntimeError):
    """Readable error raised when GEO analyses cannot be managed."""

    def __init__(
        self,
        message: str,
        *,
        code: GeoAnalysisErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class GeoAnalysisService:
    """Manage GEO analyses through the REST API client."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_geo_analyses(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
    ) -> PaginatedGeoAnalyses:
        """Return GEO analyses from the paginated API response."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        try:
            payload = self.api_client.get("/geo-analysis", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_response(payload)

    def create_geo_analysis(self, seo_analysis_id: int, providers: list[str] | None = None) -> dict[str, Any]:
        """Create a GEO analysis through the REST API."""

        payload = {"seo_analysis_id": seo_analysis_id, "providers": providers or ["openai"]}
        try:
            response = self.api_client.post("/geo-analysis", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "analyse GEO")

    def run_geo_analysis(self, analysis_id: int) -> dict[str, Any]:
        """Run a GEO analysis through the REST API."""

        try:
            response = self.api_client.post(f"/geo-analysis/{analysis_id}/run")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "analyse GEO")

    def get_geo_analysis(self, analysis_id: int) -> dict[str, Any]:
        """Return a complete GEO analysis."""

        try:
            response = self.api_client.get(f"/geo-analysis/{analysis_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "analyse GEO")

    def delete_geo_analysis(self, analysis_id: int) -> None:
        """Delete a GEO analysis through the REST API."""

        try:
            self.api_client.delete(f"/geo-analysis/{analysis_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _parse_paginated_response(self, payload: Any) -> PaginatedGeoAnalyses:
        if not isinstance(payload, dict):
            raise GeoAnalysisServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise GeoAnalysisServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise GeoAnalysisServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        return PaginatedGeoAnalyses(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GeoAnalysisServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _to_service_error(self, exc: ApiClientError) -> GeoAnalysisServiceError:
        if exc.status_code == 401:
            return GeoAnalysisServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return GeoAnalysisServiceError(
                "Permission insuffisante.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 404:
            return GeoAnalysisServiceError(
                "Analyse GEO introuvable.",
                code="not_found",
                status_code=404,
                details=exc.details,
            )
        if exc.status_code == 409:
            return GeoAnalysisServiceError(
                "Action impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return GeoAnalysisServiceError(
                "Donnees invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return GeoAnalysisServiceError(
                "Erreur serveur.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return GeoAnalysisServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return GeoAnalysisServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return GeoAnalysisServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
