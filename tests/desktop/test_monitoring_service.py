"""Tests du service Desktop Monitoring."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.monitoring_service import MonitoringService, MonitoringServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]]) -> dict[str, object]:
    return {"items": items, "total": len(items), "page": 1, "page_size": 20, "pages": 1 if items else 0}


def test_monitoring_service_loads_read_only_endpoints() -> None:
    """The service loads monitoring data through read-only endpoints."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        if request.url.path.endswith("/overview"):
            return httpx.Response(200, json={"total_events": 1})
        if request.url.path.endswith("/connectors"):
            return httpx.Response(200, json=[{"name": "Google Search Console"}])
        if request.url.path.endswith("/events"):
            return httpx.Response(200, json=_paginated_payload([{"message": "event"}]))
        return httpx.Response(200, json=_paginated_payload([{"name": "Import GSC"}]))

    service = MonitoringService(_client_with_handler(handler))

    overview = service.get_overview()
    connectors = service.list_connectors()
    events = service.list_events(severity="warning", event_type="sync")
    schedules = service.list_sync_schedules(website_id=12)

    assert overview.data["total_events"] == 1
    assert connectors[0]["name"] == "Google Search Console"
    assert events.items[0]["message"] == "event"
    assert schedules.items[0]["name"] == "Import GSC"
    assert [method for method, _url in seen_requests] == ["GET", "GET", "GET", "GET"]
    assert seen_requests[2][1].params["severity"] == "warning"
    assert seen_requests[2][1].params["event_type"] == "sync"
    assert seen_requests[3][1].params["website_id"] == "12"


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_monitoring_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = MonitoringService(_client_with_handler(handler))

    with pytest.raises(MonitoringServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_monitoring_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = MonitoringService(_client_with_handler(handler))

    with pytest.raises(MonitoringServiceError) as exc_info:
        service.get_overview()

    assert exc_info.value.code == "backend_unavailable"


def test_monitoring_service_rejects_invalid_paginated_payload() -> None:
    """Unexpected API payloads are rejected."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": "invalid"})

    service = MonitoringService(_client_with_handler(handler))

    with pytest.raises(MonitoringServiceError) as exc_info:
        service.list_events()

    assert exc_info.value.code == "unexpected"
