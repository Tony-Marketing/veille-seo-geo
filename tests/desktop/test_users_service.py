"""Tests du service Desktop Users."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.users_service import UsersService, UsersServiceError


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def _paginated_payload(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "items": items,
        "total": len(items),
        "page": 1,
        "page_size": 20,
        "pages": 1 if items else 0,
    }


def _user_payload() -> dict[str, object]:
    return {
        "email": "user@example.com",
        "password": "Password123",
        "first_name": "Alice",
        "last_name": "Martin",
        "is_active": True,
        "is_superadmin": False,
        "role_ids": [1],
    }


def test_users_service_loads_users_with_search() -> None:
    """The service loads users through ApiClient with pagination and search."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "email": "user@example.com",
                "first_name": "Alice",
                "last_name": "Martin",
                "is_active": True,
                "is_superadmin": False,
                "roles": [],
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = UsersService(_client_with_handler(handler))

    result = service.list_users(page=2, page_size=10, search="alice", sort="email", order="desc")

    assert result.items == payload["items"]
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 20
    assert result.pages == 1
    assert seen_requests == [
        httpx.URL("http://api.test/api/v1/users?page=2&page_size=10&search=alice&sort=email&order=desc"),
    ]


def test_users_service_creates_user() -> None:
    """The service creates users through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = _user_payload()
    response_payload = {"id": 1, **payload, "roles": []}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=response_payload)

    service = UsersService(_client_with_handler(handler))

    result = service.create_user(payload)

    assert result == response_payload
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/users"), payload)]


def test_users_service_updates_user() -> None:
    """The service updates users through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {"email": "updated@example.com", "first_name": "Alice", "role_ids": [1, 2]}
    response_payload = {"id": 1, **payload, "last_name": None, "is_active": True, "is_superadmin": False, "roles": []}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    service = UsersService(_client_with_handler(handler))

    result = service.update_user(1, payload)

    assert result == response_payload
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/users/1"), payload)]


def test_users_service_sets_user_active() -> None:
    """Activation and deactivation use the existing user update endpoint."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json={"id": 1, "email": "user@example.com", "is_active": False, "roles": []})

    service = UsersService(_client_with_handler(handler))

    result = service.set_user_active(1, False)

    assert result["is_active"] is False
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/users/1"), {"is_active": False})]


def test_users_service_loads_roles() -> None:
    """The service loads roles through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload([{"id": 1, "name": "Administrateur", "description": None, "permissions": []}])

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = UsersService(_client_with_handler(handler))

    result = service.list_roles()

    assert result.items == payload["items"]
    assert seen_requests == [httpx.URL("http://api.test/api/v1/roles?page=1&page_size=100&sort=name&order=asc")]


def test_users_service_loads_permissions() -> None:
    """The service loads permissions through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload([{"id": 1, "code": "admin.read", "label": "Lire", "module": "admin"}])

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = UsersService(_client_with_handler(handler))

    result = service.list_permissions()

    assert result.items == payload["items"]
    assert seen_requests == [httpx.URL("http://api.test/api/v1/permissions?page=1&page_size=100&sort=module&order=asc")]


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
def test_users_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are exposed with explicit service codes."""

    details = {"detail": "error"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=details)

    service = UsersService(_client_with_handler(handler))

    with pytest.raises(UsersServiceError) as exc_info:
        service.create_user(_user_payload())

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == details


def test_users_service_maps_network_error() -> None:
    """Network errors are exposed separately from backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = UsersService(_client_with_handler(handler))

    with pytest.raises(UsersServiceError) as exc_info:
        service.list_users()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_users_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = UsersService(_client_with_handler(handler))

    with pytest.raises(UsersServiceError) as exc_info:
        service.list_roles()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "backend_unavailable"


def test_users_service_rejects_invalid_paginated_payload() -> None:
    """Unexpected paginated payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    service = UsersService(_client_with_handler(handler))

    with pytest.raises(UsersServiceError) as exc_info:
        service.list_users()

    assert exc_info.value.code == "unexpected"


def test_users_service_rejects_invalid_resource_payload() -> None:
    """Unexpected single-resource payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=["not", "a", "user"])

    service = UsersService(_client_with_handler(handler))

    with pytest.raises(UsersServiceError) as exc_info:
        service.create_user(_user_payload())

    assert exc_info.value.code == "unexpected"
