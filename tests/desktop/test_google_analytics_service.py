"""Tests du service Desktop Google Analytics 4."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.google_analytics_service import GoogleAnalyticsService, GoogleAnalyticsServiceError


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


def _summary_payload() -> dict[str, object]:
    return {
        "generated_at": "2026-07-08T10:00:00Z",
        "filters": {"property_id": 1},
        "data": {
            "rows": 2,
            "sessions": 100,
            "users": 80,
            "new_users": 30,
            "engaged_sessions": 70,
            "screen_page_views": 240,
            "average_session_duration": 62.5,
            "engagement_rate": 0.7,
            "conversions": 5.0,
            "total_revenue": 120.0,
        },
    }


def _breakdown_payload(dimension: str) -> dict[str, object]:
    return {
        "generated_at": "2026-07-08T10:00:00Z",
        "filters": {"property_id": 1},
        "dimension": dimension,
        "data": [
            {
                "dimension": "organic",
                "rows": 1,
                "sessions": 42,
                "users": 35,
                "new_users": 12,
                "engaged_sessions": 28,
                "screen_page_views": 90,
                "average_session_duration": 45.0,
                "engagement_rate": 0.66,
                "conversions": 2.0,
                "total_revenue": 50.0,
            },
        ],
    }


def test_google_analytics_service_loads_properties() -> None:
    """The service loads Google Analytics properties through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "website_id": 2,
                "property_id": "123456",
                "property_name": "Example GA4",
                "account_name": "Example",
                "measurement_id": "G-ABC123",
                "enabled": True,
                "token_expires_at": None,
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    result = GoogleAnalyticsService(_client_with_handler(handler)).list_properties()

    assert result.items == payload["items"]
    assert result.total == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/google-analytics/properties?page=1&page_size=100")]


def test_google_analytics_service_loads_overview_with_filters() -> None:
    """The service forwards overview filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_summary_payload())

    result = GoogleAnalyticsService(_client_with_handler(handler)).overview(
        property_id=1,
        date_from="2026-07-01",
        date_to="2026-07-07",
    )

    assert result.data["sessions"] == 100
    assert seen_requests == [
        httpx.URL(
            "http://api.test/api/v1/google-analytics/overview"
            "?property_id=1&date_from=2026-07-01&date_to=2026-07-07",
        ),
    ]


def test_google_analytics_service_loads_metrics_with_pagination_search_filters_and_sort() -> None:
    """The service forwards metric pagination, search, filters and sort to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 10,
                        "property_id": 1,
                        "import_id": 5,
                        "date": "2026-07-07",
                        "source": "google",
                        "medium": "organic",
                        "campaign": "brand",
                        "device_category": "desktop",
                        "country": "France",
                        "users": 10,
                        "new_users": 4,
                        "sessions": 12,
                        "engaged_sessions": 8,
                        "screen_page_views": 30,
                        "average_session_duration": 40.0,
                        "engagement_rate": 0.7,
                        "conversions": 1.0,
                        "total_revenue": 20.0,
                    },
                ],
                filters={"property_id": 1},
            ),
        )

    result = GoogleAnalyticsService(_client_with_handler(handler)).list_metrics(
        page=2,
        page_size=25,
        search="organic",
        sort="sessions",
        order="desc",
        website_id=3,
        property_id=1,
        date_from="2026-07-01",
        date_to="2026-07-07",
        import_id=5,
        source="google",
        medium="organic",
        campaign="brand",
        device_category="desktop",
        country="France",
    )

    params = seen_requests[0].params
    assert result.items[0]["sessions"] == 12
    assert result.filters == {"property_id": 1}
    assert params["page"] == "2"
    assert params["page_size"] == "25"
    assert params["search"] == "organic"
    assert params["sort"] == "sessions"
    assert params["order"] == "desc"
    assert params["website_id"] == "3"
    assert params["property_id"] == "1"
    assert params["date_from"] == "2026-07-01"
    assert params["date_to"] == "2026-07-07"
    assert params["import_id"] == "5"
    assert params["source"] == "google"
    assert params["medium"] == "organic"
    assert params["campaign"] == "brand"
    assert params["device_category"] == "desktop"
    assert params["country"] == "France"


@pytest.mark.parametrize(
    ("method_name", "path", "dimension"),
    [
        ("traffic", "/traffic", "source"),
        ("acquisition", "/acquisition", "medium"),
        ("engagement", "/engagement", "device_category"),
        ("conversions", "/conversions", "source"),
        ("revenue", "/revenue", "campaign"),
    ],
)
def test_google_analytics_service_loads_breakdown_views(method_name: str, path: str, dimension: str) -> None:
    """The service loads every Google Analytics specialized breakdown view."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_breakdown_payload(dimension))

    service = GoogleAnalyticsService(_client_with_handler(handler))
    result = getattr(service, method_name)(property_id=1, search="organic")

    assert result.dimension == dimension
    assert result.data[0]["sessions"] == 42
    assert seen_requests == [
        httpx.URL(f"http://api.test/api/v1/google-analytics{path}?property_id=1&search=organic"),
    ]


def test_google_analytics_service_loads_history_with_pagination_search_filters_and_sort() -> None:
    """The service forwards history pagination, search, filters and sort to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 9,
                        "property_id": 1,
                        "property_name": "Example GA4",
                        "google_property_id": "123456",
                        "started_at": "2026-07-08T10:00:00Z",
                        "finished_at": "2026-07-08T10:01:00Z",
                        "status": "COMPLETED",
                        "imported_rows": 20,
                        "error_message": None,
                        "duration_seconds": 60.0,
                    },
                ],
                filters={"property_id": 1, "status": "COMPLETED"},
            ),
        )

    result = GoogleAnalyticsService(_client_with_handler(handler)).history(
        page=3,
        page_size=10,
        search="example",
        sort="started_at",
        order="desc",
        property_id=1,
        status="COMPLETED",
    )

    params = seen_requests[0].params
    assert result.items[0]["status"] == "COMPLETED"
    assert result.items[0]["duration_seconds"] == 60.0
    assert result.filters == {"property_id": 1, "status": "COMPLETED"}
    assert params["page"] == "3"
    assert params["page_size"] == "10"
    assert params["search"] == "example"
    assert params["sort"] == "started_at"
    assert params["order"] == "desc"
    assert params["property_id"] == "1"
    assert params["status"] == "COMPLETED"


def test_google_analytics_service_runs_manual_import() -> None:
    """The service runs manual imports through the REST API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    response_payload = {"id": 7, "property_id": 1, "status": "RUNNING", "imported_rows": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    result = GoogleAnalyticsService(_client_with_handler(handler)).run_manual_import(
        property_id=1,
        start_date="2026-07-01",
        end_date="2026-07-07",
        metrics=["sessions", "users"],
        dimensions=["date", "source"],
    )

    assert result == response_payload
    assert seen_requests == [
        (
            "POST",
            httpx.URL("http://api.test/api/v1/google-analytics/import"),
            {
                "property_id": 1,
                "start_date": "2026-07-01",
                "end_date": "2026-07-07",
                "metrics": ["sessions", "users"],
                "dimensions": ["date", "source"],
            },
        ),
    ]


def test_google_analytics_service_loads_imports_and_one_import() -> None:
    """The service uses the existing import list and detail endpoints."""

    seen_requests: list[httpx.URL] = []
    import_payload = {
        "id": 7,
        "property_id": 1,
        "started_at": "2026-07-08T10:00:00Z",
        "finished_at": None,
        "status": "RUNNING",
        "imported_rows": 0,
        "error_message": None,
        "duration_seconds": None,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        if request.url.path.endswith("/imports/7"):
            return httpx.Response(200, json=import_payload)
        return httpx.Response(200, json=_paginated_payload([import_payload]))

    service = GoogleAnalyticsService(_client_with_handler(handler))

    imports = service.list_imports(property_id=1)
    import_item = service.get_import(7)

    assert imports.items[0]["id"] == 7
    assert import_item["status"] == "RUNNING"
    assert seen_requests == [
        httpx.URL("http://api.test/api/v1/google-analytics/imports?page=1&page_size=100&property_id=1"),
        httpx.URL("http://api.test/api/v1/google-analytics/imports/7"),
    ]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (400, "bad_request"),
        (401, "unauthorized"),
        (403, "forbidden"),
        (404, "not_found"),
        (409, "conflict"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_google_analytics_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = GoogleAnalyticsService(_client_with_handler(handler))

    with pytest.raises(GoogleAnalyticsServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code
    assert exc_info.value.details == {"detail": "error"}


def test_google_analytics_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = GoogleAnalyticsService(_client_with_handler(handler))

    with pytest.raises(GoogleAnalyticsServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == "network_error"


def test_google_analytics_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = GoogleAnalyticsService(_client_with_handler(handler))

    with pytest.raises(GoogleAnalyticsServiceError) as exc_info:
        service.list_properties()

    assert exc_info.value.code == "backend_unavailable"
