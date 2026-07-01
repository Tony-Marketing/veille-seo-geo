"""Tests du service Desktop URLs."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.urls_service import URLsService, URLsServiceError


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


def _url_payload() -> dict[str, object]:
    return {
        "website_id": None,
        "url": "https://example.com/page",
        "status_code": 200,
        "is_indexable": True,
    }


def test_urls_service_loads_urls() -> None:
    """The service loads URLs through ApiClient."""

    seen_requests: list[httpx.URL] = []
    payload = _paginated_payload(
        [
            {
                "id": 1,
                "website_id": None,
                "url": "https://example.com/page",
                "status_code": 200,
                "is_indexable": True,
            },
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=payload)

    service = URLsService(_client_with_handler(handler))

    result = service.list_urls()

    assert result.items == payload["items"]
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 100
    assert result.pages == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/urls?page=1&page_size=100")]


def test_urls_service_passes_search_parameter() -> None:
    """The service forwards search to the REST API."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_paginated_payload([]))

    service = URLsService(_client_with_handler(handler))

    result = service.list_urls(page=2, page_size=5, search="audit")

    assert result.items == []
    assert result.page == 1
    assert seen_requests == [httpx.URL("http://api.test/api/v1/urls?page=2&page_size=5&search=audit")]


def test_urls_service_parses_paginated_response() -> None:
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

    service = URLsService(_client_with_handler(handler))

    result = service.list_urls(page=2, page_size=5)

    assert result.items == []
    assert result.total == 12
    assert result.page == 2
    assert result.page_size == 5
    assert result.pages == 3


def test_urls_service_returns_empty_list() -> None:
    """An empty paginated response remains a valid result."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_paginated_payload([]))

    service = URLsService(_client_with_handler(handler))

    result = service.list_urls()

    assert result.items == []
    assert result.total == 0
    assert result.pages == 0


def test_urls_service_creates_url() -> None:
    """The service creates URLs through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = _url_payload()
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=response_payload)

    service = URLsService(_client_with_handler(handler))

    result = service.create_url(payload)

    assert result == response_payload
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/urls"), payload)]


def test_urls_service_updates_url() -> None:
    """The service updates URLs through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {"website_id": None, "url": "https://example.com/updated", "status_code": None, "is_indexable": False}
    response_payload = {"id": 1, **payload}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(200, json=response_payload)

    service = URLsService(_client_with_handler(handler))

    result = service.update_url(1, payload)

    assert result == response_payload
    assert seen_requests == [("PUT", httpx.URL("http://api.test/api/v1/urls/1"), payload)]


def test_urls_service_deletes_url() -> None:
    """The service deletes URLs through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        return httpx.Response(204)

    service = URLsService(_client_with_handler(handler))

    assert service.delete_url(1) is None
    assert seen_requests == [("DELETE", httpx.URL("http://api.test/api/v1/urls/1"))]


@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "unauthorized"),
        (403, "forbidden"),
    ],
)
def test_urls_service_maps_access_errors(status_code: int, expected_code: str) -> None:
    """401 and 403 responses are exposed with explicit service codes."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "access refused"})

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.list_urls()

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
def test_urls_service_maps_mutation_http_errors(status_code: int, expected_code: str) -> None:
    """Mutation HTTP errors are exposed with explicit service codes."""

    details = {"detail": "error"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=details)

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.create_url(_url_payload())

    assert exc_info.value.status_code == status_code
    assert exc_info.value.code == expected_code
    assert exc_info.value.details == details


def test_urls_service_maps_network_error() -> None:
    """Network errors are exposed separately from backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.list_urls()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_urls_service_maps_mutation_network_error() -> None:
    """Network errors are also mapped for write operations."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timeout", request=request)

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.update_url(1, _url_payload())

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "network_error"


def test_urls_service_maps_backend_unavailable() -> None:
    """Connection failures are reported as backend unavailability."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.list_urls()

    assert exc_info.value.status_code is None
    assert exc_info.value.code == "backend_unavailable"


def test_urls_service_rejects_invalid_payload() -> None:
    """Unexpected API payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.list_urls()

    assert exc_info.value.code == "unexpected"


def test_urls_service_rejects_invalid_url_payload() -> None:
    """Unexpected single-resource payloads are reported as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json=["not", "an", "url"])

    service = URLsService(_client_with_handler(handler))

    with pytest.raises(URLsServiceError) as exc_info:
        service.create_url(_url_payload())

    assert exc_info.value.code == "unexpected"
