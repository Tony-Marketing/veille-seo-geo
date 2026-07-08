"""Tests du service Desktop Bing Webmaster Tools."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.bing_webmaster_tools_service import BingWebmasterToolsService, BingWebmasterToolsServiceError


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


def test_bing_webmaster_tools_service_loads_connections() -> None:
    """The service loads Bing Webmaster Tools connections through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "website_id": 2,
                "auth_type": "API_KEY",
                "client_id": "client-id",
                "is_active": True,
                "last_sync_at": None,
                "last_error": None,
                "has_api_key": True,
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_connections()

    assert result.items == payload["items"]
    assert result.total == 1
    assert seen_requests == [
        httpx.URL("http://api.test/api/v1/bing-webmaster-tools/connections?page=1&page_size=100"),
    ]


def test_bing_webmaster_tools_service_loads_sites_with_filters() -> None:
    """The service forwards site pagination, search and filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 4,
                        "connection_id": 1,
                        "website_id": 2,
                        "site_url": "https://example.com/",
                        "is_verified": True,
                        "is_active": True,
                        "last_import_at": None,
                    },
                ],
            ),
        )

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_sites(
        page=2,
        page_size=25,
        search="example",
        sort="site_url",
        order="desc",
        connection_id=1,
        website_id=2,
        is_active=True,
    )

    params = seen_requests[0].params
    assert result.items[0]["site_url"] == "https://example.com/"
    assert params["page"] == "2"
    assert params["page_size"] == "25"
    assert params["search"] == "example"
    assert params["sort"] == "site_url"
    assert params["order"] == "desc"
    assert params["connection_id"] == "1"
    assert params["website_id"] == "2"
    assert params["is_active"] == "true"


def test_bing_webmaster_tools_service_loads_metrics_with_pagination_search_filters_and_sort() -> None:
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
                        "bing_site_id": 4,
                        "import_id": 5,
                        "date": "2026-07-07",
                        "query": "audit seo",
                        "page_url": "https://example.com/audit",
                        "country": "FRA",
                        "device": "DESKTOP",
                        "clicks": 10,
                        "impressions": 100,
                        "ctr": 0.1,
                        "average_position": 2.5,
                    },
                ],
                filters={"bing_site_id": 4},
            ),
        )

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_metrics(
        page=3,
        page_size=20,
        search="audit",
        sort="clicks",
        order="desc",
        website_id=2,
        bing_site_id=4,
        date_from="2026-07-01",
        date_to="2026-07-07",
        query="audit seo",
        page_url="https://example.com/audit",
        country="FRA",
        device="DESKTOP",
    )

    params = seen_requests[0].params
    assert result.items[0]["clicks"] == 10
    assert result.filters == {"bing_site_id": 4}
    assert params["page"] == "3"
    assert params["page_size"] == "20"
    assert params["search"] == "audit"
    assert params["sort"] == "clicks"
    assert params["order"] == "desc"
    assert params["website_id"] == "2"
    assert params["bing_site_id"] == "4"
    assert params["date_from"] == "2026-07-01"
    assert params["date_to"] == "2026-07-07"
    assert params["query"] == "audit seo"
    assert params["page_url"] == "https://example.com/audit"
    assert params["country"] == "FRA"
    assert params["device"] == "DESKTOP"


def test_bing_webmaster_tools_service_loads_crawl_stats_with_filters() -> None:
    """The service forwards crawl stat filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 12,
                        "bing_site_id": 4,
                        "import_id": 5,
                        "date": "2026-07-07",
                        "url": "https://example.com/missing",
                        "http_status": 404,
                        "issue_type": "NOT_FOUND",
                        "issue_category": "CRAWL",
                        "severity": "ERROR",
                        "details": None,
                    },
                ],
            ),
        )

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_crawl_stats(
        website_id=2,
        bing_site_id=4,
        date_from="2026-07-01",
        date_to="2026-07-07",
        status=404,
        issue_type="NOT_FOUND",
        severity="ERROR",
    )

    params = seen_requests[0].params
    assert result.items[0]["http_status"] == 404
    assert params["website_id"] == "2"
    assert params["bing_site_id"] == "4"
    assert params["date_from"] == "2026-07-01"
    assert params["date_to"] == "2026-07-07"
    assert params["status"] == "404"
    assert params["issue_type"] == "NOT_FOUND"
    assert params["severity"] == "ERROR"


def test_bing_webmaster_tools_service_loads_sitemaps_with_filters() -> None:
    """The service forwards sitemap filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 9,
                        "bing_site_id": 4,
                        "import_id": 5,
                        "sitemap_url": "https://example.com/sitemap.xml",
                        "status": "OK",
                        "url_count": 42,
                        "error_count": 0,
                        "warning_count": 1,
                    },
                ],
                filters={"status": "OK"},
            ),
        )

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_sitemaps(
        page=2,
        search="sitemap",
        website_id=2,
        bing_site_id=4,
        status="OK",
    )

    params = seen_requests[0].params
    assert result.items[0]["url_count"] == 42
    assert result.filters == {"status": "OK"}
    assert params["page"] == "2"
    assert params["search"] == "sitemap"
    assert params["website_id"] == "2"
    assert params["bing_site_id"] == "4"
    assert params["status"] == "OK"


def test_bing_webmaster_tools_service_loads_import_runs_with_filters() -> None:
    """The service forwards import history filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(
            200,
            json=_paginated_payload(
                [
                    {
                        "id": 7,
                        "connection_id": 1,
                        "bing_site_id": 4,
                        "import_type": "MANUAL",
                        "status": "COMPLETED",
                        "items_processed": 3,
                        "duration_seconds": 0.1,
                    },
                ],
            ),
        )

    result = BingWebmasterToolsService(_client_with_handler(handler)).list_import_runs(
        page=4,
        page_size=10,
        search="completed",
        sort="created_at",
        order="desc",
        connection_id=1,
        bing_site_id=4,
        status="COMPLETED",
        import_type="MANUAL",
    )

    params = seen_requests[0].params
    assert result.items[0]["status"] == "COMPLETED"
    assert params["page"] == "4"
    assert params["page_size"] == "10"
    assert params["search"] == "completed"
    assert params["sort"] == "created_at"
    assert params["order"] == "desc"
    assert params["connection_id"] == "1"
    assert params["bing_site_id"] == "4"
    assert params["status"] == "COMPLETED"
    assert params["import_type"] == "MANUAL"


def test_bing_webmaster_tools_service_runs_manual_import() -> None:
    """The service runs manual imports through the REST API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    response_payload = {"id": 7, "connection_id": 1, "bing_site_id": 4, "status": "RUNNING", "items_processed": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    result = BingWebmasterToolsService(_client_with_handler(handler)).run_manual_import(
        connection_id=1,
        bing_site_id=4,
        date_from="2026-07-01",
        date_to="2026-07-07",
    )

    assert result == response_payload
    assert seen_requests == [
        (
            "POST",
            httpx.URL("http://api.test/api/v1/bing-webmaster-tools/import"),
            {
                "connection_id": 1,
                "bing_site_id": 4,
                "date_from": "2026-07-01",
                "date_to": "2026-07-07",
                "import_type": "MANUAL",
            },
        ),
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
def test_bing_webmaster_tools_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = BingWebmasterToolsService(_client_with_handler(handler))

    with pytest.raises(BingWebmasterToolsServiceError) as exc_info:
        service.list_connections()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code
    assert exc_info.value.details == {"detail": "error"}


def test_bing_webmaster_tools_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = BingWebmasterToolsService(_client_with_handler(handler))

    with pytest.raises(BingWebmasterToolsServiceError) as exc_info:
        service.list_connections()

    assert exc_info.value.code == "network_error"


def test_bing_webmaster_tools_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = BingWebmasterToolsService(_client_with_handler(handler))

    with pytest.raises(BingWebmasterToolsServiceError) as exc_info:
        service.list_connections()

    assert exc_info.value.code == "backend_unavailable"
