"""Tests for Desktop Dashboard V2 service."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.dashboard_v2_service import DashboardV2Service, DashboardV2ServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def test_dashboard_v2_service_loads_overview() -> None:
    """Desktop service loads overview through ApiClient."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json={"generated_at": "2026-07-10T00:00:00", "global_health": {}})

    result = DashboardV2Service(_client_with_handler(handler)).get_overview(period="30d")

    assert result.data["global_health"] == {}
    assert seen_requests == [httpx.URL("http://api.test/api/v1/dashboard-v2/overview?period=30d")]


def test_dashboard_v2_service_loads_paginated_websites() -> None:
    """Desktop service parses paginated website payloads."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("http://api.test/api/v1/dashboard-v2/websites?page=2&page_size=5")
        return httpx.Response(
            200,
            json={"items": [{"name": "Example"}], "total": 1, "page": 2, "page_size": 5, "pages": 1},
        )

    result = DashboardV2Service(_client_with_handler(handler)).list_websites(page=2, page_size=5)

    assert result.items == [{"name": "Example"}]
    assert result.total == 1


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_dashboard_v2_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = DashboardV2Service(_client_with_handler(handler))

    with pytest.raises(DashboardV2ServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == expected_code


def test_dashboard_v2_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = DashboardV2Service(_client_with_handler(handler))

    with pytest.raises(DashboardV2ServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == "network_error"
