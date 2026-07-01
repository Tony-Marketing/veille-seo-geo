"""Tests du service Desktop Entities."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.entities_service import EntitiesService, EntitiesServiceError


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


def _entity_payload() -> dict[str, object]:
    return {
        "name": "Groupe APPartner",
        "description": "Entite principale",
        "is_active": True,
    }


def test_entities_service_loads_entities() -> None:
    """The service loads entities through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "name": "Groupe APPartner",
                "description": "Entite principale",
                "is_active": True,
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = EntitiesService(_client_with_handler(handler))

    result = service.list_entities()

    assert result.items == payload["items"]
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 100
    assert result.pages == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/entities?page=1&page_size=100")]


def test_entities_service_parses_paginated_response() -> None:
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

    service = EntitiesService(_client_with_handler(handler))

    result = service.list_entities(page=2, page_size=5)

    assert result.items == []
    assert result.total == 12
    assert result.page == 2
    assert result.page_size == 5
    assert result.pages == 3


def test_entities_service_returns_empty_list() -> None:
    """An empty paginated response remains a valid result."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_paginated_payload([]))

    service = EntitiesService(_client_with_handler(handler))

    result = service.list_entities()

    assert result.items == []
    assert result.total == 0
    assert result.pages == 0


def test_entities_service_creates_entity() -> None:
    """The service creates entities through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = _entity_payload()
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=response_payload)

    service = EntitiesService(_client_with_handler(handler))

    result = service.create_entity(payload)

    assert result == response_payload
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/entities"), payload)]


def test_entities_service_updates_entity() -> None:
    """The service updates entities through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {"name": "Groupe modifie", "description": None, "is_active": False}
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    service = EntitiesService(_client_with_handler(handler))

    result = service.update_entity(1, payload)

    assert result == response_payload
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/entities/1"), payload)]


def test_entities_service_deletes_entity() -> None:
    """The service deletes entities through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        return httpx.Response(204)

    service = EntitiesService(_client_with_handler(handler))

    assert service.delete_entity(1) is None
    assert seen_requests == [("DELETE", httpx.URL("http://api.test/api/v1/entities/1"))]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
    ],
)
def test_entities_service_maps_access_errors(status_code: int, expected_code: str) -> None:
    """401 and 403 responses are exposed with explicit service codes."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "access refused"})

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.list_entities()

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
def test_entities_service_maps_mutation_http_errors(status_code: int, expected_code: str) -> None:
    """Mutation HTTP errors are exposed with explicit service codes."""

    details = {"detail": "error"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=details)

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.create_entity(_entity_payload())

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == details


def test_entities_service_maps_network_error() -> None:
    """Network errors are exposed separately from backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.list_entities()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_entities_service_maps_mutation_network_error() -> None:
    """Network errors are also mapped for write operations."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.update_entity(1, _entity_payload())

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_entities_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.list_entities()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "backend_unavailable"


def test_entities_service_rejects_invalid_payload() -> None:
    """Unexpected API payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.list_entities()

    assert exc_info.value.code == "unexpected"


def test_entities_service_rejects_invalid_entity_payload() -> None:
    """Unexpected single-resource payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=["not", "an", "entity"])

    service = EntitiesService(_client_with_handler(handler))

    with pytest.raises(EntitiesServiceError) as exc_info:
        service.create_entity(_entity_payload())

    assert exc_info.value.code == "unexpected"
