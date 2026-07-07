"""Tests du service Desktop Google Search Console."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.gsc_service import GSCService, GSCServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]], **extra: object) -> dict[str, object]:
    return {
        "items": items,
        "total": len(items),
        "page": 1,
        "page_size": 100,
        "pages": 1 if items else 0,
        **extra,
    }


def test_gsc_service_loads_properties() -> None:
    """The service loads Google Search Console properties through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "property_url": "https://example.com/",
                "property_type": "URL_PREFIX",
                "is_active": True,
                "last_sync_at": "2026-07-07T10:00:00",
                "display_name": "Example",
                "permission_level": "siteOwner",
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    result = GSCService(_client_with_handler(handler)).list_properties()

    assert result.items == payload["items"]
    assert result.total == 1
    assert seen_requests == [
        httpx.URL("http://api.test/api/v1/google-search-console/properties?page=1&page_size=100"),
    ]


def test_gsc_service_loads_performances_with_filters() -> None:
    """The service forwards performance filters to the REST API."""

    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "date": "2026-07-06",
                        "page": "https://example.com/a",
                        "query": "audit seo",
                        "country": "fra",
                        "device": "DESKTOP",
                        "clicks": 10,
                        "impressions": 100,
                        "ctr": 0.1,
                        "position": 3.2,
                    },
                ],
            ),
        )

    result = GSCService(_client_with_handler(handler)).list_performances(
        property_id=1,
        start_date="2026-07-01",
        end_date="2026-07-07",
        page=2,
        page_url="https://example.com/a",
        query="audit seo",
        country="fra",
        device="DESKTOP",
    )

    params = seen_requests[0].url.params
    assert result.items[0]["clicks"] == 10
    assert params.get_list("page") == ["2", "https://example.com/a"]
    assert params["page_size"] == "100"
    assert params["property_id"] == "1"
    assert params["start_date"] == "2026-07-01"
    assert params["end_date"] == "2026-07-07"
    assert params["query"] == "audit seo"
    assert params["country"] == "fra"
    assert params["device"] == "DESKTOP"


def test_gsc_service_loads_indexation_with_backend_aggregates() -> None:
    """The service exposes backend-provided indexation aggregates."""

    payload = _paginated_payload(
        [
            {
                "url": "https://example.com/a",
                "coverage_state": "VALID",
                "google_state": "INDEXING_ALLOWED",
                "indexing_state": "INDEXING_ALLOWED",
                "verdict": "PASS",
                "issue_type": None,
                "sitemap": "https://example.com/sitemap.xml",
                "last_crawled_at": "2026-07-07T10:00:00",
            },
        ],
        valid_pages=12,
        excluded_pages=3,
        errors=1,
        warnings=2,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    result = GSCService(_client_with_handler(handler)).list_indexation(property_id=1)

    assert result.items == payload["items"]
    assert result.valid_pages == 12
    assert result.excluded_pages == 3
    assert result.errors == 1
    assert result.warnings == 2


def test_gsc_service_loads_sitemaps() -> None:
    """The service loads sitemaps through the REST API."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "sitemap_url": "https://example.com/sitemap.xml",
                        "sitemap_type": "WEB",
                        "is_pending": False,
                        "is_sitemaps_index": False,
                        "submitted_at": "2026-07-01T08:00:00",
                        "last_downloaded_at": "2026-07-07T08:00:00",
                        "warnings": 0,
                        "errors": 0,
                        "url_count": 42,
                    },
                ],
            ),
        )

    result = GSCService(_client_with_handler(handler)).list_sitemaps(property_id=1)

    assert result.total == 1
    assert result.items[0]["url_count"] == 42


def test_gsc_service_loads_import_history() -> None:
    """The service loads import history through the REST API."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 5,
                        "property_id": 1,
                        "import_type": "MANUAL",
                        "status": "COMPLETED",
                        "start_date": "2026-07-01",
                        "end_date": "2026-07-07",
                        "rows_imported": 120,
                        "error_message": None,
                        "started_at": "2026-07-07T10:00:00",
                        "completed_at": "2026-07-07T10:01:00",
                        "duration_seconds": 60.0,
                    },
                ],
            ),
        )

    result = GSCService(_client_with_handler(handler)).list_imports(property_id=1)

    assert result.items[0]["status"] == "COMPLETED"
    assert result.items[0]["duration_seconds"] == 60.0


def test_gsc_service_runs_manual_import() -> None:
    """The service runs manual imports through the REST API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    response_payload = {"id": 7, "property_id": 1, "status": "PENDING", "rows_imported": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    result = GSCService(_client_with_handler(handler)).run_manual_import(
        property_id=1,
        start_date="2026-07-01",
        end_date="2026-07-07",
    )

    assert result == response_payload
    assert seen_requests == [
        (
            "POST",
            httpx.URL("http://api.test/api/v1/google-search-console/imports/manual"),
            {
                "property_id": 1,
                "start_date": "2026-07-01",
                "end_date": "2026-07-07",
                "dimensions": ["query", "page"],
                "search_type": "web",
            },
        ),
    ]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
        (404, "not_found"),
        (409, "conflict"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_gsc_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = GSCService(_client_with_handler(handler))

    with pytest.raises(GSCServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code
    assert exc_info.value.details == {"detail": "error"}


def test_gsc_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = GSCService(_client_with_handler(handler))

    with pytest.raises(GSCServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == "network_error"


def test_gsc_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = GSCService(_client_with_handler(handler))

    with pytest.raises(GSCServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == "backend_unavailable"
