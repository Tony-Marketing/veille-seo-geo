"""Tests du service Desktop Alertes."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.alerts_service import AlertsService, AlertsServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]]) -> dict[str, object]:
    return {"items": items, "total": len(items), "page": 1, "page_size": 20, "pages": 1 if items else 0}


def test_alerts_service_calls_expected_endpoints() -> None:
    """The service communicates only through the alert REST endpoints."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        if request.url.path.endswith("/summary"):
            return httpx.Response(200, json={"total": 1, "active": 1})
        if request.url.path.endswith("/refresh-from-monitoring"):
            return httpx.Response(200, json={"created": 1, "updated": 0, "total_processed": 1, "alerts": []})
        if request.url.path.endswith("/acknowledge"):
            return httpx.Response(200, json={"id": 1, "status": "Acknowledged"})
        if request.url.path.endswith("/resolve"):
            return httpx.Response(200, json={"id": 1, "status": "Resolved"})
        if request.url.path.endswith("/alerts/1"):
            return httpx.Response(200, json={"id": 1, "status": "Active"})
        return httpx.Response(200, json=_paginated_payload([{"id": 1, "severity": "Warning"}]))

    service = AlertsService(_client_with_handler(handler))

    summary = service.get_summary()
    listed = service.list_alerts(status="Active", severity="Warning", category="sync", source="GSC", search="Import")
    detail = service.get_alert(1)
    refresh = service.refresh_from_monitoring()
    acknowledged = service.acknowledge_alert(1)
    resolved = service.resolve_alert(1)

    assert summary.data["total"] == 1
    assert listed.items[0]["severity"] == "Warning"
    assert detail.data["id"] == 1
    assert refresh.data["created"] == 1
    assert acknowledged.data["status"] == "Acknowledged"
    assert resolved.data["status"] == "Resolved"
    assert [method for method, _url in seen_requests] == ["GET", "GET", "GET", "POST", "POST", "POST"]
    assert seen_requests[1][1].params["status"] == "Active"
    assert seen_requests[1][1].params["source"] == "GSC"


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
        (404, "not_found"),
        (422, "validation_error"),
        (500, "server_error"),
    ],
)
def test_alerts_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = AlertsService(_client_with_handler(handler))

    with pytest.raises(AlertsServiceError) as exc_info:
        service.get_summary()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_alerts_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = AlertsService(_client_with_handler(handler))

    with pytest.raises(AlertsServiceError) as exc_info:
        service.get_summary()

    assert exc_info.value.code == "backend_unavailable"


def test_alerts_service_rejects_invalid_paginated_payload() -> None:
    """Unexpected API payloads are rejected."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": "invalid"})

    service = AlertsService(_client_with_handler(handler))

    with pytest.raises(AlertsServiceError) as exc_info:
        service.list_alerts()

    assert exc_info.value.code == "unexpected"
