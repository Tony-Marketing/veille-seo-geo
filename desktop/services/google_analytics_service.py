"""Service Desktop Google Analytics 4."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

GoogleAnalyticsErrorCode = Literal[
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
class PaginatedGoogleAnalyticsResponse:
    """Paginated Google Analytics payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    filters: dict[str, Any] | None = None


@dataclass(frozen=True)
class GoogleAnalyticsSummaryPayload:
    """Google Analytics summary payload returned by the REST API."""

    generated_at: str | None
    filters: dict[str, Any]
    data: dict[str, Any]


@dataclass(frozen=True)
class GoogleAnalyticsBreakdownPayload:
    """Google Analytics breakdown payload returned by the REST API."""

    generated_at: str | None
    filters: dict[str, Any]
    dimension: str
    data: list[dict[str, Any]]


class GoogleAnalyticsServiceError(RuntimeError):
    """Readable error raised when Google Analytics data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: GoogleAnalyticsErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class GoogleAnalyticsService:
    """Access Google Analytics REST endpoints through ApiClient."""

    BASE_PATH = "/google-analytics"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_properties(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> PaginatedGoogleAnalyticsResponse:
        """Return Google Analytics properties from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        return self._get_paginated("/properties", params=params)

    def list_metrics(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        website_id: int | None = None,
        property_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        import_id: int | None = None,
        source: str | None = None,
        medium: str | None = None,
        campaign: str | None = None,
        device_category: str | None = None,
        country: str | None = None,
    ) -> PaginatedGoogleAnalyticsResponse:
        """Return Google Analytics metric rows from the REST API."""

        params = self._metric_params(
            page=page,
            page_size=page_size,
            search=search,
            sort=sort,
            order=order,
            website_id=website_id,
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            import_id=import_id,
            source=source,
            medium=medium,
            campaign=campaign,
            device_category=device_category,
            country=country,
        )
        return self._get_paginated("/metrics", params=params)

    def overview(self, **filters: Any) -> GoogleAnalyticsSummaryPayload:
        """Return Google Analytics overview KPIs from the REST API."""

        return self._get_summary("/overview", params=self._filter_params(filters))

    def traffic(self, **filters: Any) -> GoogleAnalyticsBreakdownPayload:
        """Return Google Analytics traffic breakdown from the REST API."""

        return self._get_breakdown("/traffic", params=self._filter_params(filters))

    def acquisition(self, **filters: Any) -> GoogleAnalyticsBreakdownPayload:
        """Return Google Analytics acquisition breakdown from the REST API."""

        return self._get_breakdown("/acquisition", params=self._filter_params(filters))

    def engagement(self, **filters: Any) -> GoogleAnalyticsBreakdownPayload:
        """Return Google Analytics engagement breakdown from the REST API."""

        return self._get_breakdown("/engagement", params=self._filter_params(filters))

    def conversions(self, **filters: Any) -> GoogleAnalyticsBreakdownPayload:
        """Return Google Analytics conversions breakdown from the REST API."""

        return self._get_breakdown("/conversions", params=self._filter_params(filters))

    def revenue(self, **filters: Any) -> GoogleAnalyticsBreakdownPayload:
        """Return Google Analytics revenue breakdown from the REST API."""

        return self._get_breakdown("/revenue", params=self._filter_params(filters))

    def history(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        property_id: int | None = None,
        status: str | None = None,
    ) -> PaginatedGoogleAnalyticsResponse:
        """Return Google Analytics enriched import history from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        self._add_optional_filters(params, {"property_id": property_id, "status": status})
        return self._get_paginated("/history", params=params)

    def list_imports(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        property_id: int | None = None,
        status: str | None = None,
    ) -> PaginatedGoogleAnalyticsResponse:
        """Return Google Analytics import logs from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size, search=search, sort=sort, order=order)
        self._add_optional_filters(params, {"property_id": property_id, "status": status})
        return self._get_paginated("/imports", params=params)

    def get_import(self, import_id: int) -> dict[str, Any]:
        """Return one Google Analytics import from the REST API."""

        try:
            payload = self.api_client.get(f"{self.BASE_PATH}/imports/{import_id}")
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(payload, "import Google Analytics")

    def run_manual_import(
        self,
        *,
        property_id: int,
        start_date: str,
        end_date: str,
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a manual Google Analytics import through the REST API."""

        payload: dict[str, Any] = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        if metrics is not None:
            payload["metrics"] = metrics
        if dimensions is not None:
            payload["dimensions"] = dimensions
        try:
            response = self.api_client.post(f"{self.BASE_PATH}/import", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "import Google Analytics")

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> PaginatedGoogleAnalyticsResponse:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_response(payload)

    def _get_summary(self, path: str, *, params: dict[str, Any]) -> GoogleAnalyticsSummaryPayload:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_summary_response(payload)

    def _get_breakdown(self, path: str, *, params: dict[str, Any]) -> GoogleAnalyticsBreakdownPayload:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_breakdown_response(payload)

    def _parse_paginated_response(self, payload: Any) -> PaginatedGoogleAnalyticsResponse:
        if not isinstance(payload, dict):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise GoogleAnalyticsServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        filters = payload.get("filters")
        return PaginatedGoogleAnalyticsResponse(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
            filters=filters if isinstance(filters, dict) else None,
        )

    def _parse_summary_response(self, payload: Any) -> GoogleAnalyticsSummaryPayload:
        if not isinstance(payload, dict):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : la synthese Google Analytics n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        data = payload.get("data")
        filters = payload.get("filters")
        if not isinstance(data, dict) or not isinstance(filters, dict):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : la synthese Google Analytics est incomplete.",
                code="unexpected",
                details={"payload": payload},
            )
        generated_at = payload.get("generated_at")
        return GoogleAnalyticsSummaryPayload(
            generated_at=generated_at if isinstance(generated_at, str) else None,
            filters=filters,
            data=data,
        )

    def _parse_breakdown_response(self, payload: Any) -> GoogleAnalyticsBreakdownPayload:
        if not isinstance(payload, dict):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : la vue Google Analytics n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        data = payload.get("data")
        filters = payload.get("filters")
        dimension = payload.get("dimension")
        if not isinstance(data, list) or not isinstance(filters, dict) or not isinstance(dimension, str):
            raise GoogleAnalyticsServiceError(
                "Reponse API inattendue : la vue Google Analytics est incomplete.",
                code="unexpected",
                details={"payload": payload},
            )
        generated_at = payload.get("generated_at")
        return GoogleAnalyticsBreakdownPayload(
            generated_at=generated_at if isinstance(generated_at, str) else None,
            filters=filters,
            dimension=dimension,
            data=[item for item in data if isinstance(item, dict)],
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GoogleAnalyticsServiceError(
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

    def _metric_params(self, **values: Any) -> dict[str, Any]:
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
                "property_id": values.get("property_id"),
                "date_from": values.get("date_from"),
                "date_to": values.get("date_to"),
                "import_id": values.get("import_id"),
                "source": values.get("source"),
                "medium": values.get("medium"),
                "campaign": values.get("campaign"),
                "device_category": values.get("device_category"),
                "country": values.get("country"),
            },
        )
        return params

    def _filter_params(self, filters: dict[str, Any]) -> dict[str, Any]:
        params: dict[str, Any] = {}
        self._add_optional_filters(params, filters)
        return params

    def _add_optional_filters(self, params: dict[str, Any], filters: dict[str, Any]) -> None:
        for key, value in filters.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> GoogleAnalyticsServiceError:
        if exc.status_code == 400:
            return GoogleAnalyticsServiceError(
                "Requete Google Analytics invalide.",
                code="bad_request",
                status_code=400,
                details=exc.details,
            )
        if exc.status_code == 401:
            return GoogleAnalyticsServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return GoogleAnalyticsServiceError(
                "Permission insuffisante.",
                code="forbidden",
                status_code=403,
                details=exc.details,
            )
        if exc.status_code == 404:
            return GoogleAnalyticsServiceError(
                "Ressource Google Analytics introuvable.",
                code="not_found",
                status_code=404,
                details=exc.details,
            )
        if exc.status_code == 409:
            return GoogleAnalyticsServiceError(
                "Action Google Analytics impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return GoogleAnalyticsServiceError(
                "Donnees Google Analytics invalides.",
                code="validation_error",
                status_code=422,
                details=exc.details,
            )
        if exc.status_code is not None and exc.status_code >= 500:
            return GoogleAnalyticsServiceError(
                "Erreur serveur Google Analytics.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return GoogleAnalyticsServiceError(
                    "Backend indisponible.",
                    code="backend_unavailable",
                    details=exc.details,
                )
            return GoogleAnalyticsServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return GoogleAnalyticsServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
