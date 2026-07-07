"""Service Desktop Google Search Console."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx
from core.api_client import ApiClient, ApiClientError

GSCErrorCode = Literal[
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
class PaginatedGSCResponse:
    """Paginated Google Search Console payload consumed by the Desktop UI."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int


@dataclass(frozen=True)
class GSCIndexationResponse(PaginatedGSCResponse):
    """Paginated indexation payload with backend-provided aggregates."""

    valid_pages: int
    excluded_pages: int
    errors: int
    warnings: int


class GSCServiceError(RuntimeError):
    """Readable error raised when Google Search Console data cannot be loaded."""

    def __init__(
        self,
        message: str,
        *,
        code: GSCErrorCode,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class GSCService:
    """Access Google Search Console REST endpoints through ApiClient."""

    BASE_PATH = "/google-search-console"
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_properties(
        self,
        *,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedGSCResponse:
        """Return Google Search Console properties from the REST API."""

        return self._get_paginated("/properties", params={"page": page, "page_size": page_size})

    def list_performances(
        self,
        *,
        property_id: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
        page_url: str | None = None,
        query: str | None = None,
        country: str | None = None,
        device: str | None = None,
    ) -> PaginatedGSCResponse:
        """Return Google Search Console performances from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size)
        if page_url:
            params["page"] = [str(page), page_url]
        self._add_optional_filters(
            params,
            {
                "property_id": property_id,
                "start_date": start_date,
                "end_date": end_date,
                "query": query,
                "country": country,
                "device": device,
            },
        )
        return self._get_paginated("/performances", params=params)

    def list_indexation(
        self,
        *,
        property_id: int | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> GSCIndexationResponse:
        """Return Google Search Console indexation data from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(params, {"property_id": property_id})
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}/indexation", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc

        paginated = self._parse_paginated_response(payload)
        if not isinstance(payload, dict):
            raise GSCServiceError(
                "Reponse API inattendue : la reponse d'indexation n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return GSCIndexationResponse(
            items=paginated.items,
            total=paginated.total,
            page=paginated.page,
            page_size=paginated.page_size,
            pages=paginated.pages,
            valid_pages=int(payload.get("valid_pages") or 0),
            excluded_pages=int(payload.get("excluded_pages") or 0),
            errors=int(payload.get("errors") or 0),
            warnings=int(payload.get("warnings") or 0),
        )

    def list_sitemaps(
        self,
        *,
        property_id: int | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedGSCResponse:
        """Return Google Search Console sitemaps from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(params, {"property_id": property_id})
        return self._get_paginated("/sitemaps", params=params)

    def list_imports(
        self,
        *,
        property_id: int | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> PaginatedGSCResponse:
        """Return Google Search Console import history from the REST API."""

        params = self._pagination_params(page=page, page_size=page_size)
        self._add_optional_filters(params, {"property_id": property_id})
        return self._get_paginated("/imports", params=params)

    def run_manual_import(
        self,
        *,
        property_id: int,
        start_date: str,
        end_date: str,
        dimensions: list[str] | None = None,
        search_type: str = "web",
    ) -> dict[str, Any]:
        """Run a manual Google Search Console import through the REST API."""

        payload = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": dimensions or ["query", "page"],
            "search_type": search_type,
        }
        try:
            response = self.api_client.post(f"{self.BASE_PATH}/imports/manual", json=payload)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_resource_response(response, "import Google Search Console")

    def _get_paginated(self, path: str, *, params: dict[str, Any]) -> PaginatedGSCResponse:
        try:
            payload = self.api_client.get(f"{self.BASE_PATH}{path}", params=params)
        except ApiClientError as exc:
            raise self._to_service_error(exc) from exc
        return self._parse_paginated_response(payload)

    def _parse_paginated_response(self, payload: Any) -> PaginatedGSCResponse:
        if not isinstance(payload, dict):
            raise GSCServiceError(
                "Reponse API inattendue : la reponse n'est pas un objet pagine.",
                code="unexpected",
                details={"payload": payload},
            )
        missing_fields = {"items", "total", "page", "page_size", "pages"} - payload.keys()
        if missing_fields:
            raise GSCServiceError(
                f"Reponse API inattendue : champ(s) manquant(s) {', '.join(sorted(missing_fields))}.",
                code="unexpected",
                details={"payload": payload},
            )
        items = payload["items"]
        if not isinstance(items, list):
            raise GSCServiceError(
                "Reponse API inattendue : items n'est pas une liste.",
                code="unexpected",
                details={"payload": payload},
            )
        return PaginatedGSCResponse(
            items=[item for item in items if isinstance(item, dict)],
            total=int(payload["total"]),
            page=int(payload["page"]),
            page_size=int(payload["page_size"]),
            pages=int(payload["pages"]),
        )

    def _parse_resource_response(self, payload: Any, resource_name: str) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise GSCServiceError(
                f"Reponse API inattendue : {resource_name} n'est pas un objet.",
                code="unexpected",
                details={"payload": payload},
            )
        return payload

    def _pagination_params(self, *, page: int, page_size: int) -> dict[str, Any]:
        return {"page": page, "page_size": page_size}

    def _add_optional_filters(self, params: dict[str, Any], filters: dict[str, Any]) -> None:
        for key, value in filters.items():
            if value is not None and value != "":
                params[key] = value

    def _to_service_error(self, exc: ApiClientError) -> GSCServiceError:
        if exc.status_code == 401:
            return GSCServiceError(
                "Authentification requise.",
                code="unauthorized",
                status_code=401,
                details=exc.details,
            )
        if exc.status_code == 403:
            return GSCServiceError("Permission insuffisante.", code="forbidden", status_code=403, details=exc.details)
        if exc.status_code == 404:
            return GSCServiceError(
                "Ressource Google Search Console introuvable.",
                code="not_found",
                status_code=404,
                details=exc.details,
            )
        if exc.status_code == 409:
            return GSCServiceError(
                "Action impossible dans l'etat actuel.",
                code="conflict",
                status_code=409,
                details=exc.details,
            )
        if exc.status_code == 422:
            return GSCServiceError("Donnees invalides.", code="validation_error", status_code=422, details=exc.details)
        if exc.status_code is not None and exc.status_code >= 500:
            return GSCServiceError(
                "Erreur serveur.",
                code="server_error",
                status_code=exc.status_code,
                details=exc.details,
            )
        if exc.status_code is None:
            if isinstance(exc.__cause__, httpx.ConnectError):
                return GSCServiceError("Backend indisponible.", code="backend_unavailable", details=exc.details)
            return GSCServiceError("Erreur reseau.", code="network_error", details=exc.details)
        return GSCServiceError(
            f"Erreur API inattendue ({exc.status_code}).",
            code="unexpected",
            status_code=exc.status_code,
            details=exc.details,
        )
