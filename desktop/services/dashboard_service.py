"""Service Desktop de restitution du Dashboard SEO/GEO."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

DashboardErrorCode = Literal[
    "unauthorized",
    "forbidden",
    "validation_error",
    "server_error",
    "backend_unavailable",
    "network_error",
    "unexpected",
]


@dataclass(frozen=True)
class DashboardOverviewPayload:
    """Dashboard payload consumed by the Desktop UI."""

    data: dict[str, Any]


class DashboardServiceError(RuntimeError):
    """Readable error raised when the Dashboard cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: DashboardErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class DashboardService:
    """Load Dashboard data through the REST API client."""

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_overview(
        self,
        *,
        website_id: int | None = None,
        crawl_id: int | None = None,
        seo_analysis_id: int | None = None,
        geo_analysis_id: int | None = None,
    ) -> DashboardOverviewPayload:
        """Return Dashboard overview data from the API."""

        params = self._params(
            website_id=website_id,
            crawl_id=crawl_id,
            seo_analysis_id=seo_analysis_id,
            geo_analysis_id=geo_analysis_id,
        )
        try:
            payload = self.api_client.get("/dashboard/overview", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(payload, dict):
            raise DashboardServiceError(
                "Reponse API inattendue : le Dashboard n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return DashboardOverviewPayload(data=payload)

    def _params(
        self,
        *,
        website_id: int | None,
        crawl_id: int | None,
        seo_analysis_id: int | None,
        geo_analysis_id: int | None,
    ) -> dict[str, int]:
        params: dict[str, int] = {}
        if website_id is not None:
            params["website_id"] = website_id
        if crawl_id is not None:
            params["crawl_id"] = crawl_id
        if seo_analysis_id is not None:
            params["seo_analysis_id"] = seo_analysis_id
        if geo_analysis_id is not None:
            params["geo_analysis_id"] = geo_analysis_id
        return params

    def _to_service_error(self, exc: ApiClientError) -> DashboardServiceError:
        if exc.status_code == 401:
            return DashboardServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return DashboardServiceError(
                "Permission insuffisante.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 422:
            return DashboardServiceError(
                "Parametres invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return DashboardServiceError(
                "Erreur serveur.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return DashboardServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return DashboardServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return DashboardServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
