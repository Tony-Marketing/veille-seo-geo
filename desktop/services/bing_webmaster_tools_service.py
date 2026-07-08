"""Service Desktop Bing Webmaster Tools."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

BingWebmasterToolsErrorCode = Literal[
    "bad_request",
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
class PaginatedBingWebmasterToolsResponse:
    """Paginated Bing Webmaster Tools payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


class BingWebmasterToolsServiceError(RuntimeError):
    """Readable error raised when Bing Webmaster Tools data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: BingWebmasterToolsErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class BingWebmasterToolsService:
    """Access Bing Webmaster Tools REST endpoints through ApiClient."""

    BASE_PATH = "/bing-webmaster-tools"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_connections(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools connections from the REST API."""

        return self._get_paginated(
            "/connections",
            params=self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order),
        )

    def list_sites(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        connection_id: int | None = None,
        website_id: int | None = None,
        is_active: bool | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools sites from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        self._add_optional_filters(
            params,
            {"connection_id": connection_id, "website_id": website_id, "is_active": is_active},
        )
        return self._get_paginated("/sites", params=params)

    def list_metrics(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        query: str | None = None,
        page_url: str | None = None,
        country: str | None = None,
        device: str | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools metric rows from the REST API."""

        params = self._data_params(
            page=page,
            page_size=page_size,
            search=search,
            sort=sort,
            order=order,
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            page_url=page_url,
            country=country,
            device=device,
        )
        return self._get_paginated("/metrics", params=params)

    def list_crawl_stats(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        status: int | None = None,
        issue_type: str | None = None,
        severity: str | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools crawl statistic rows from the REST API."""

        params = self._data_params(
            page=page,
            page_size=page_size,
            search=search,
            sort=sort,
            order=order,
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
        )
        self._add_optional_filters(params, {"status": status, "issue_type": issue_type, "severity": severity})
        return self._get_paginated("/crawl-stats", params=params)

    def list_sitemaps(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        status: str | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools sitemaps from the REST API."""

        params = self._data_params(
            page=page,
            page_size=page_size,
            search=search,
            sort=sort,
            order=order,
            website_id=website_id,
            bing_site_id=bing_site_id,
        )
        self._add_optional_filters(params, {"status": status})
        return self._get_paginated("/sitemaps", params=params)

    def list_import_runs(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        connection_id: int | None = None,
        bing_site_id: int | None = None,
        status: str | None = None,
        import_type: str | None = None,
    ) -> PaginatedBingWebmasterToolsResponse:
        """Return Bing Webmaster Tools import history from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        self._add_optional_filters(
            params,
            {
                "connection_id": connection_id,
                "bing_site_id": bing_site_id,
                "status": status,
                "import_type": import_type,
            },
        )
        return self._get_paginated("/import-runs", params=params)

    def run_manual_import(
        self,
        *,
        connection_id: int,
        date_from: str,
        date_to: str,
        bing_site_id: int | None = None,
        import_type: str = "MANUAL",
    ) -> dict[str, Any]:
        """Run a manual Bing Webmaster Tools import through the REST API."""

        payload: dict[str, Any] = {
            "connection_id": connection_id,
            "date_from": date_from,
            "date_to": date_to,
            "import_type": import_type,
        }
        if bing_site_id is not None:
            payload["bing_site_id"] = bing_site_id

        try:
            response = self.api_client.post(f"{self.BASE_PATH}/import", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "import Bing Webmaster Tools")

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> PaginatedBingWebmasterToolsResponse:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_response(payload)

    def _parse_paginated_response(self, payload: Any) -> PaginatedBingWebmasterToolsResponse:
        if not isinstance(payload, dict):
            raise BingWebmasterToolsServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise BingWebmasterToolsServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise BingWebmasterToolsServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return PaginatedBingWebmasterToolsResponse(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise BingWebmasterToolsServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _pagination_params(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        sort: str | None,
        order: str | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        self._add_optional_filters(params, {"search": search, "sort": sort, "order": order})
        return params

    def _data_params(self, **values: Any) -> dict[str, Any]:
        params = self._pagination_params(
            page=int(values["page"]),
            page_size=int(values["page_size"]),
            search=values.get("search"),
            sort=values.get("sort"),
            order=values.get("order"),
        )
        self._add_optional_filters(
            params,
            {
                "website_id": values.get("website_id"),
                "bing_site_id": values.get("bing_site_id"),
                "date_from": values.get("date_from"),
                "date_to": values.get("date_to"),
                "query": values.get("query"),
                "page_url": values.get("page_url"),
                "country": values.get("country"),
                "device": values.get("device"),
            },
        )
        return params

    def _add_optional_filters(self, params: dict[str, Any], filters: dict[str, Any]) -> None:
        for key, value in filters.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> BingWebmasterToolsServiceError:
        if exc.status_code == 400:
            return BingWebmasterToolsServiceError(
                "Requete Bing Webmaster Tools invalide.",
                code="bad_request",
                status_code=400,
                details=exc.details,
            )
        if exc.status_code == 401:
            return BingWebmasterToolsServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return BingWebmasterToolsServiceError(
                "Permission insuffisante.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 404:
            return BingWebmasterToolsServiceError(
                "Ressource Bing Webmaster Tools introuvable.",
                code="not_found",
                status_code=404,
                details=exc.details,
            )
        if exc.status_code == 409:
            return BingWebmasterToolsServiceError(
                "Action Bing Webmaster Tools impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return BingWebmasterToolsServiceError(
                "Donnees Bing Webmaster Tools invalides.",
                code="validation_error",
                status_code=422,
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
            if isinstance(exc.__cause__, httpx.ConnectError):
                return BingWebmasterToolsServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return BingWebmasterToolsServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return BingWebmasterToolsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
