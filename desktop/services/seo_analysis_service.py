"""Desktop adapter for the existing SEO Analysis REST endpoints."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

SeoAnalysisErrorCode = Literal[
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
class PaginatedSeoAnalyses:
    """Paginated SEO analyses consumed by the Desktop page."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


class SeoAnalysisServiceError(RuntimeError):
    """Readable error raised by the Desktop SEO adapter."""

    def __init__(
        self,
        message: str,
        *,
        code: SeoAnalysisErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class SeoAnalysisService:
    """Consume SEO Analysis through ApiClient only."""

    BASE_PATH = "/seo-analysis"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_analyses(self, *, page: int = DEFAULT_PAGE, page_size: int = DEFAULT_PAGE_SIZE) -> PaginatedSeoAnalyses:
        """Return persisted SEO analyses."""

        payload = self._request("get", "", params={"page": page, "page_size": page_size})
        if not isinstance(payload, dict):
            raise self._unexpected("la liste SEO n'est pas un objet", payload)
        missing = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing or not isinstance(payload.get("items"), list):
            raise self._unexpected("la liste SEO est incomplete", payload)
        return PaginatedSeoAnalyses(
            items=[item for item in payload["items"] if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def create_analysis(self, crawl_id: int) -> dict[str, Any]:
        """Create a pending SEO analysis through the existing endpoint."""

        return self._object(self._request("post", "", json={"crawl_id": crawl_id}))

    def get_analysis(self, analysis_id: int) -> dict[str, Any]:
        """Return one SEO analysis."""

        return self._object(self._request("get", f"/{analysis_id}"))

    def run_analysis(self, analysis_id: int) -> dict[str, Any]:
        """Run an existing SEO analysis through the REST API."""

        return self._object(self._request("post", f"/{analysis_id}/run"))

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            caller = getattr(self.api_client, method)
            return caller(f"{self.BASE_PATH}{path}", **kwargs)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

    def _object(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise self._unexpected("l'analyse SEO n'est pas un objet", payload)
        return payload

    def _unexpected(self, message: str, payload: Any) -> SeoAnalysisServiceError:
        return SeoAnalysisServiceError(message, code="unexpected", details={"payload": payload})

    def _to_service_error(self, exc: ApiClientError) -> SeoAnalysisServiceError:
        mapping: dict[int, SeoAnalysisErrorCode] = {
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
            422: "validation_error",
        }
        if exc.status_code in mapping:
            return SeoAnalysisServiceError(
                "Erreur API SEO Analysis.",
                code=mapping[exc.status_code],
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return SeoAnalysisServiceError(
                "Erreur serveur SEO Analysis.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            code: SeoAnalysisErrorCode = (
                "backend_unavailable" if isinstance(exc.__cause__, httpx.ConnectError) else "network_error"
            )
            return SeoAnalysisServiceError("SEO Analysis indisponible.", code=code, details=exc.details)
        return SeoAnalysisServiceError(
            "Erreur inattendue SEO Analysis.",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
