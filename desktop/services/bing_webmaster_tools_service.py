"""Desktop adapter for existing Bing Webmaster Tools REST endpoints."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

BingErrorCode = Literal[
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
class PaginatedBingPayload:
    """Paginated Bing payload consumed by the Desktop page."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class BingWebmasterToolsServiceError(RuntimeError):
    """Readable error raised by the Desktop Bing adapter."""

    def __init__(
        self,
        message: str,
        *,
        code: BingErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class BingWebmasterToolsService:
    """Consume Bing data exclusively through ApiClient and the backend REST API."""

    BASE_PATH = "/bing-webmaster-tools"
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_connections(self) -> PaginatedBingPayload:
        return self._get_paginated("/connections", {})

    def list_sites(self, *, website_id: int | None = None) -> PaginatedBingPayload:
        return self._get_paginated("/sites", self._params(website_id=website_id))

    def list_metrics(self, *, website_id: int | None = None) -> PaginatedBingPayload:
        return self._get_paginated("/metrics", self._params(website_id=website_id))

    def list_crawl_stats(self, *, website_id: int | None = None) -> PaginatedBingPayload:
        return self._get_paginated("/crawl-stats", self._params(website_id=website_id))

    def list_sitemaps(self, *, website_id: int | None = None) -> PaginatedBingPayload:
        return self._get_paginated("/sitemaps", self._params(website_id=website_id))

    def list_import_runs(self, *, connection_id: int | None = None) -> PaginatedBingPayload:
        return self._get_paginated("/import-runs", self._params(connection_id=connection_id))

    def run_manual_import(
        self,
        *,
        connection_id: int,
        date_from: str,
        date_to: str,
        bing_site_id: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "connection_id": connection_id,
            "date_from": date_from,
            "date_to": date_to,
            "import_type": "MANUAL",
        }
        if bing_site_id is not None:
            payload["bing_site_id"] = bing_site_id
        try:
            response = self.api_client.post(f"{self.BASE_PATH}/import", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(response, dict):
            raise self._unexpected(response)
        return response

    def _get_paginated(self, path: str, filters: dict[str, Any]) -> PaginatedBingPayload:
        params = {"page": 1, "page_size": self.DEFAULT_PAGE_SIZE, **filters}
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        if not isinstance(payload, dict):
            raise self._unexpected(payload)
        missing = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing or not isinstance(payload.get("items"), list):
            raise self._unexpected(payload)
        response_filters = payload.get("filters")
        return PaginatedBingPayload(
            items=[item for item in payload["items"] if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=response_filters if isinstance(response_filters, dict) else None,
        )

    def _params(self, **values: Any) -> dict[str, Any]:
        return {key: value for key, value in values.items() if value is not None and value != ""}

    def _unexpected(self, payload: Any) -> BingWebmasterToolsServiceError:
        return BingWebmasterToolsServiceError(
            "Reponse Bing Webmaster Tools inattendue.",
            code="unexpected",
            details={"payload": payload},
        )

    def _to_service_error(self, exc: ApiClientError) -> BingWebmasterToolsServiceError:
        mapping: dict[int, BingErrorCode] = {
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
            422: "validation_error",
        }
        if exc.status_code in mapping:
            return BingWebmasterToolsServiceError(
                "Erreur API Bing Webmaster Tools.",
                code=mapping[exc.status_code],
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return BingWebmasterToolsServiceError(
                "Erreur serveur Bing Webmaster Tools.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            code: BingErrorCode = (
                "backend_unavailable" if isinstance(exc.__cause__, httpx.ConnectError) else "network_error"
            )
            return BingWebmasterToolsServiceError("Bing indisponible.", code=code, details=exc.details)
        return BingWebmasterToolsServiceError(
            "Erreur inattendue Bing Webmaster Tools.",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
