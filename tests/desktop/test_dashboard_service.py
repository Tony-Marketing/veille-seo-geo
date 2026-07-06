"""Tests du service Desktop Dashboard."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.dashboard_service import DashboardService, DashboardServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _overview_payload() -> dict[str, object]:
    return {
        "crawl": {"crawled_pages_count": 2},
        "seo": {"average_score": 75},
        "geo": {"average_score": 70},
        "priority_pages": [],
        "comparison": {"pages": []},
        "seo_score_distribution": [],
        "geo_score_distribution": [],
    }


def test_dashboard_service_loads_overview() -> None:
    """The Desktop service loads Dashboard overview through ApiClient."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_overview_payload())

    result = DashboardService(_client_with_handler(handler)).get_overview()

    assert result.data["crawl"]["crawled_pages_count"] == 2
    assert seen_requests == [httpx.URL("http://api.test/api/v1/dashboard/overview")]


def test_dashboard_service_sends_optional_filters() -> None:
    """Optional filters are forwarded as query parameters."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_overview_payload())

    DashboardService(_client_with_handler(handler)).get_overview(crawl_id=1, seo_analysis_id=2, geo_analysis_id=3)

    assert seen_requests == [
        httpx.URL("http://api.test/api/v1/dashboard/overview?crawl_id=1&seo_analysis_id=2&geo_analysis_id=3"),
    ]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_dashboard_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = DashboardService(_client_with_handler(handler))

    with pytest.raises(DashboardServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_dashboard_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = DashboardService(_client_with_handler(handler))

    with pytest.raises(DashboardServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == "network_error"
