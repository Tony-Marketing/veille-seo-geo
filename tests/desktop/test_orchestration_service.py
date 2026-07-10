"""Tests du service Desktop Orchestrateur."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.orchestration_service import OrchestrationService, OrchestrationServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]]) -> dict[str, object]:
    return {"items": items, "total": len(items), "page": 1, "page_size": 20, "pages": 1 if items else 0}


def test_orchestration_service_calls_expected_endpoints() -> None:
    """The service communicates only through orchestration REST endpoints."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        if request.url.path.endswith("/summary"):
            return httpx.Response(200, json={"pending": 1, "total": 1})
        if request.url.path.endswith("/logs"):
            return httpx.Response(200, json=_paginated_payload([{"id": 1, "event": "created"}]))
        if request.url.path.endswith("/retry"):
            return httpx.Response(200, json={"id": 1, "status": "retry_scheduled"})
        if request.url.path.endswith("/cancel"):
            return httpx.Response(200, json={"id": 1, "status": "cancelled"})
        if request.url.path.endswith("/scheduler/run-once"):
            return httpx.Response(200, json={"created": 1, "skipped": 0})
        if request.url.path.endswith("/jobs/1"):
            return httpx.Response(200, json={"id": 1, "status": "pending"})
        return httpx.Response(200, json=_paginated_payload([{"id": 1, "job_type": "gsc"}]))

    service = OrchestrationService(_client_with_handler(handler))

    summary = service.get_summary()
    listed = service.list_jobs(status="pending", job_type="gsc", schedule_id=1, search="GSC")
    detail = service.get_job(1)
    logs = service.list_job_logs(1)
    retry = service.retry_job(1)
    cancel = service.cancel_job(1)
    scheduler = service.run_scheduler_once()

    assert summary.data["pending"] == 1
    assert listed.items[0]["job_type"] == "gsc"
    assert detail.data["id"] == 1
    assert logs.items[0]["event"] == "created"
    assert retry.data["status"] == "retry_scheduled"
    assert cancel.data["status"] == "cancelled"
    assert scheduler.data["created"] == 1
    assert [method for method, _url in seen_requests] == ["GET", "GET", "GET", "GET", "POST", "POST", "POST"]
    assert seen_requests[1][1].params["status"] == "pending"
    assert seen_requests[1][1].params["job_type"] == "gsc"


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
def test_orchestration_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = OrchestrationService(_client_with_handler(handler))

    with pytest.raises(OrchestrationServiceError) as exc_info:
        service.get_summary()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_orchestration_service_rejects_invalid_paginated_payload() -> None:
    """Unexpected API payloads are rejected."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": "invalid"})

    service = OrchestrationService(_client_with_handler(handler))

    with pytest.raises(OrchestrationServiceError) as exc_info:
        service.list_jobs()

    assert exc_info.value.code == "unexpected"

