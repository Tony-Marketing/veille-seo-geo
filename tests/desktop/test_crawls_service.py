"""Tests du service Desktop Crawls."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.crawls_service import CrawlsService, CrawlsServiceError


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


def _crawl_payload() -> dict[str, object]:
    return {
        "id": 1,
        "start_url": "https://example.com",
        "normalized_start_url": "https://example.com/",
        "status": "PENDING",
        "max_depth": 2,
        "max_pages": 100,
    }


def test_crawls_service_loads_crawls() -> None:
    """The service loads crawls through ApiClient."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_paginated_payload([_crawl_payload()]))

    result = CrawlsService(_client_with_handler(handler)).list_crawls()

    assert result.total == 1
    assert result.items[0]["status"] == "PENDING"
    assert seen_requests == [httpx.URL("http://api.test/api/v1/crawls?page=1&page_size=100")]


def test_crawls_service_creates_crawl() -> None:
    """The service creates a crawl through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []
    payload = {"start_url": "https://example.com", "max_depth": 1, "max_pages": 5}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json={**_crawl_payload(), **payload})

    result = CrawlsService(_client_with_handler(handler)).create_crawl(payload)

    assert result["start_url"] == "https://example.com"
    assert seen_requests == [("POST", httpx.URL("http://api.test/api/v1/crawls"), payload)]


def test_crawls_service_starts_and_cancels_crawl() -> None:
    """The service starts and cancels crawls through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        status = "CANCELLED" if str(request.url).endswith("/cancel") else "COMPLETED"
        return httpx.Response(200, json={**_crawl_payload(), "status": status})

    service = CrawlsService(_client_with_handler(handler))

    assert service.start_crawl(1)["status"] == "COMPLETED"
    assert service.cancel_crawl(1)["status"] == "CANCELLED"
    assert seen_requests == [
        ("POST", httpx.URL("http://api.test/api/v1/crawls/1/start")),
        ("POST", httpx.URL("http://api.test/api/v1/crawls/1/cancel")),
    ]


def test_crawls_service_loads_pages() -> None:
    """The service loads crawl pages through the API."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_paginated_payload([{"id": 1, "url": "https://example.com"}]))

    result = CrawlsService(_client_with_handler(handler)).list_crawl_pages(1)

    assert result.total == 1
    assert result.items[0]["url"] == "https://example.com"


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
def test_crawls_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = CrawlsService(_client_with_handler(handler))

    with pytest.raises(CrawlsServiceError) as exc_info:
        service.list_crawls()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_crawls_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = CrawlsService(_client_with_handler(handler))

    with pytest.raises(CrawlsServiceError) as exc_info:
        service.list_crawls()

    assert exc_info.value.code == "network_error"

