"""Tests du service Desktop des planifications de synchronisation."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.sync_schedules_service import SyncSchedulesService, SyncSchedulesServiceError


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


def _schedule_payload() -> dict[str, object]:
    return {
        "id": 1,
        "name": "Import GSC",
        "sync_type": "GSC",
        "frequency": "Quotidien",
        "status": "Active",
        "is_active": True,
        "next_run_at": "2026-07-10T08:00:00Z",
    }


def test_sync_schedules_service_lists_schedules_with_filters() -> None:
    """The service forwards list filters to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_paginated_payload([_schedule_payload()], filters={"sync_type": "GSC"}))

    result = SyncSchedulesService(_client_with_handler(handler)).list_schedules(
        page=2,
        page_size=25,
        search="gsc",
        sort="next_run_at",
        order="desc",
        sync_type="GSC",
        frequency="Quotidien",
        status="Active",
        is_active=True,
        website_id=3,
    )

    params = seen_requests[0].params
    assert result.items[0]["sync_type"] == "GSC"
    assert result.filters == {"sync_type": "GSC"}
    assert params["page"] == "2"
    assert params["page_size"] == "25"
    assert params["search"] == "gsc"
    assert params["sort"] == "next_run_at"
    assert params["order"] == "desc"
    assert params["sync_type"] == "GSC"
    assert params["frequency"] == "Quotidien"
    assert params["status"] == "Active"
    assert params["is_active"] == "true"
    assert params["website_id"] == "3"


def test_sync_schedules_service_creates_updates_and_runs_actions() -> None:
    """The service uses REST endpoints for create, update and state actions."""

    seen_requests: list[tuple[str, str, dict[str, object] | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode()) if request.content else None
        seen_requests.append((request.method, request.url.path, payload))
        return httpx.Response(200, json=_schedule_payload())

    service = SyncSchedulesService(_client_with_handler(handler))

    created = service.create_schedule({"name": "Import GSC", "sync_type": "GSC", "frequency": "Quotidien"})
    updated = service.update_schedule(1, {"frequency": "Hebdomadaire"})
    detail = service.get_schedule(1)
    enabled = service.enable_schedule(1)
    disabled = service.disable_schedule(1)
    recalculated = service.recalculate_schedule(1)

    assert created["id"] == 1
    assert updated["id"] == 1
    assert detail["id"] == 1
    assert enabled["id"] == 1
    assert disabled["id"] == 1
    assert recalculated["id"] == 1
    assert seen_requests == [
        (
            "POST",
            "/api/v1/sync-schedules",
            {"name": "Import GSC", "sync_type": "GSC", "frequency": "Quotidien"},
        ),
        ("PATCH", "/api/v1/sync-schedules/1", {"frequency": "Hebdomadaire"}),
        ("GET", "/api/v1/sync-schedules/1", None),
        ("POST", "/api/v1/sync-schedules/1/enable", None),
        ("POST", "/api/v1/sync-schedules/1/disable", None),
        ("POST", "/api/v1/sync-schedules/1/recalculate", None),
    ]


def test_sync_schedules_service_soft_deletes_schedule() -> None:
    """The service soft-deletes schedules through DELETE."""

    seen_requests: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url.path))
        return httpx.Response(204)

    SyncSchedulesService(_client_with_handler(handler)).delete_schedule(1)

    assert seen_requests == [("DELETE", "/api/v1/sync-schedules/1")]


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
def test_sync_schedules_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = SyncSchedulesService(_client_with_handler(handler))

    with pytest.raises(SyncSchedulesServiceError) as exc_info:
        service.list_schedules()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_sync_schedules_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = SyncSchedulesService(_client_with_handler(handler))

    with pytest.raises(SyncSchedulesServiceError) as exc_info:
        service.list_schedules()

    assert exc_info.value.code == "backend_unavailable"

