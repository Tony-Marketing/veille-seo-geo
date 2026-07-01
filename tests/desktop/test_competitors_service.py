"""Tests du service Desktop Competitors."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.competitors_service import CompetitorsService, CompetitorsServiceError


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


def _competitor_payload() -> dict[str, object]:
    return {
        "entity_id": None,
        "name": "Concurrent SEO",
        "website_url": "https://competitor.example",
        "is_active": True,
    }


def test_competitors_service_loads_competitors() -> None:
    """The service loads competitors through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "entity_id": None,
                "name": "Concurrent SEO",
                "website_url": "https://competitor.example",
                "is_active": True,
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = CompetitorsService(_client_with_handler(handler))

    result = service.list_competitors()

    assert result.items == payload["items"]
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 100
    assert result.pages == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/competitors?page=1&page_size=100")]


def test_competitors_service_parses_paginated_response() -> None:
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

    service = CompetitorsService(_client_with_handler(handler))

    result = service.list_competitors(page=2, page_size=5)

    assert result.items == []
    assert result.total == 12
    assert result.page == 2
    assert result.page_size == 5
    assert result.pages == 3


def test_competitors_service_returns_empty_list() -> None:
    """An empty paginated response remains a valid result."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_paginated_payload([]))

    service = CompetitorsService(_client_with_handler(handler))

    result = service.list_competitors()

    assert result.items == []
    assert result.total == 0
    assert result.pages == 0


def test_competitors_service_creates_competitor() -> None:
    """The service creates competitors through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = _competitor_payload()
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=response_payload)

    service = CompetitorsService(_client_with_handler(handler))

    result = service.create_competitor(payload)

    assert result == response_payload
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/competitors"), payload)]


def test_competitors_service_updates_competitor() -> None:
    """The service updates competitors through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {"entity_id": None, "name": "Concurrent modifie", "website_url": None, "is_active": False}
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    service = CompetitorsService(_client_with_handler(handler))

    result = service.update_competitor(1, payload)

    assert result == response_payload
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/competitors/1"), payload)]


def test_competitors_service_deletes_competitor() -> None:
    """The service deletes competitors through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        return httpx.Response(204)

    service = CompetitorsService(_client_with_handler(handler))

    assert service.delete_competitor(1) is None
    assert seen_requests == [("DELETE", httpx.URL("http://api.test/api/v1/competitors/1"))]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
    ],
)
def test_competitors_service_maps_access_errors(status_code: int, expected_code: str) -> None:
    """401 and 403 responses are exposed with explicit service codes."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "access refused"})

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.list_competitors()

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
def test_competitors_service_maps_mutation_http_errors(status_code: int, expected_code: str) -> None:
    """Mutation HTTP errors are exposed with explicit service codes."""

    details = {"detail": "error"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=details)

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.create_competitor(_competitor_payload())

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == details


def test_competitors_service_maps_network_error() -> None:
    """Network errors are exposed separately from backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.list_competitors()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_competitors_service_maps_mutation_network_error() -> None:
    """Network errors are also mapped for write operations."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.update_competitor(1, _competitor_payload())

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_competitors_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.list_competitors()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "backend_unavailable"


def test_competitors_service_rejects_invalid_payload() -> None:
    """Unexpected API payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.list_competitors()

    assert exc_info.value.code == "unexpected"


def test_competitors_service_rejects_invalid_competitor_payload() -> None:
    """Unexpected single-resource payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=["not", "a", "competitor"])

    service = CompetitorsService(_client_with_handler(handler))

    with pytest.raises(CompetitorsServiceError) as exc_info:
        service.create_competitor(_competitor_payload())

    assert exc_info.value.code == "unexpected"
