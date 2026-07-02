"""Tests du service Desktop Reports."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.reports_service import ReportsService, ReportsServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "items": items,
        "total": len(items),
        "page": 1,
        "page_size": 100,
        "pages": 1 if items else 0,
    }


def _report_payload() -> dict[str, object]:
    return {
        "entity_id": None,
        "title": "Rapport SEO",
        "report_type": "seo",
        "status": "draft",
    }


def test_reports_service_loads_reports() -> None:
    """The service loads reports through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "entity_id": None,
                "title": "Rapport SEO",
                "report_type": "seo",
                "status": "draft",
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = ReportsService(_client_with_handler(handler))

    result = service.list_reports()

    assert result.items == payload["items"]
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 100
    assert result.pages == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/reports?page=1&page_size=100")]


def test_reports_service_passes_search_parameter() -> None:
    """The service forwards search to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_paginated_payload([]))

    service = ReportsService(_client_with_handler(handler))

    result = service.list_reports(page=2, page_size=5, search="audit")

    assert result.items == []
    assert result.page == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/reports?page=2&page_size=5&search=audit")]


def test_reports_service_parses_paginated_response() -> None:
    """The service normalizes pagination fields from the API response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "items": [],
                "total": "12",
                "page": "2",
                "page_size": "5",
                "pages": "3",
            },
        )

    service = ReportsService(_client_with_handler(handler))

    result = service.list_reports(page=2, page_size=5)

    assert result.items == []
    assert result.total == 12
    assert result.page == 2
    assert result.page_size == 5
    assert result.pages == 3


def test_reports_service_returns_empty_list() -> None:
    """An empty paginated response remains a valid result."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_paginated_payload([]))

    service = ReportsService(_client_with_handler(handler))

    result = service.list_reports()

    assert result.items == []
    assert result.total == 0
    assert result.pages == 0


def test_reports_service_creates_report() -> None:
    """The service creates reports through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = _report_payload()
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=response_payload)

    service = ReportsService(_client_with_handler(handler))

    result = service.create_report(payload)

    assert result == response_payload
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/reports"), payload)]


def test_reports_service_updates_report() -> None:
    """The service updates reports through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {
        "entity_id": None,
        "title": "Rapport GEO",
        "report_type": "geo",
        "status": "published",
    }
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    service = ReportsService(_client_with_handler(handler))

    result = service.update_report(1, payload)

    assert result == response_payload
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/reports/1"), payload)]


def test_reports_service_deletes_report() -> None:
    """The service deletes reports through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        return httpx.Response(204)

    service = ReportsService(_client_with_handler(handler))

    assert service.delete_report(1) is None
    assert seen_requests == [("DELETE", httpx.URL("http://api.test/api/v1/reports/1"))]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
    ],
)
def test_reports_service_maps_access_errors(status_code: int, expected_code: str) -> None:
    """401 and 403 responses are exposed with explicit service codes."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "access refused"})

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.list_reports()

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == {"detail": "access refused"}


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
def test_reports_service_maps_mutation_http_errors(status_code: int, expected_code: str) -> None:
    """Mutation HTTP errors are exposed with explicit service codes."""

    details = {"detail": "error"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=details)

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.create_report(_report_payload())

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == details


def test_reports_service_maps_network_error() -> None:
    """Network errors are exposed separately from backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.list_reports()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_reports_service_maps_mutation_network_error() -> None:
    """Network errors are also mapped for write operations."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.update_report(1, _report_payload())

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_reports_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.list_reports()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "backend_unavailable"


def test_reports_service_rejects_invalid_payload() -> None:
    """Unexpected API payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.list_reports()

    assert exc_info.value.code == "unexpected"


def test_reports_service_rejects_invalid_report_payload() -> None:
    """Unexpected single-resource payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=["not", "a", "report"])

    service = ReportsService(_client_with_handler(handler))

    with pytest.raises(ReportsServiceError) as exc_info:
        service.create_report(_report_payload())

    assert exc_info.value.code == "unexpected"
