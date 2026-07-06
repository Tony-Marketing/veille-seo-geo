"""Tests du service Desktop GEO Analysis."""

import json
from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from services.geo_analysis_service import GeoAnalysisService, GeoAnalysisServiceError


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


def _geo_payload() -> dict[str, object]:
    return {
        "id": 1,
        "seo_analysis_id": 2,
        "crawl_session_id": 3,
        "status": "PENDING",
        "progress_percent": 0,
        "providers_requested": ["openai"],
        "provider_results": [],
        "recommendations": [],
    }


def test_geo_analysis_service_loads_analyses() -> None:
    """The service loads GEO analyses through ApiClient."""

    seen_requests: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request.url)
        return httpx.Response(200, json=_paginated_payload([_geo_payload()]))

    result = GeoAnalysisService(_client_with_handler(handler)).list_geo_analyses()

    assert result.total == 1
    assert result.items[0]["status"] == "PENDING"
    assert seen_requests == [httpx.URL("http://api.test/api/v1/geo-analysis?page=1&page_size=100")]


def test_geo_analysis_service_creates_analysis() -> None:
    """The service creates a GEO analysis through the API."""

    seen_requests: list[tuple[str, httpx.URL, dict[str, object]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url, json.loads(request.content.decode())))
        return httpx.Response(201, json=_geo_payload())

    result = GeoAnalysisService(_client_with_handler(handler)).create_geo_analysis(2, ["openai"])

    assert result["seo_analysis_id"] == 2
    assert seen_requests == [
        (
            "POST",
            httpx.URL("http://api.test/api/v1/geo-analysis"),
            {"seo_analysis_id": 2, "providers": ["openai"]},
        ),
    ]


def test_geo_analysis_service_runs_and_gets_analysis() -> None:
    """The service runs and fetches GEO analyses through the API."""

    seen_requests: list[tuple[str, httpx.URL]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url))
        return httpx.Response(200, json={**_geo_payload(), "status": "PARTIAL"})

    service = GeoAnalysisService(_client_with_handler(handler))

    assert service.run_geo_analysis(1)["status"] == "PARTIAL"
    assert service.get_geo_analysis(1)["status"] == "PARTIAL"
    assert seen_requests == [
        ("POST", httpx.URL("http://api.test/api/v1/geo-analysis/1/run")),
        ("GET", httpx.URL("http://api.test/api/v1/geo-analysis/1")),
    ]


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
def test_geo_analysis_service_maps_http_errors(status_code: int, expected_code: str) -> None:
    """HTTP errors are mapped to readable service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    service = GeoAnalysisService(_client_with_handler(handler))

    with pytest.raises(GeoAnalysisServiceError) as exc_info:
        service.list_geo_analyses()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == status_code


def test_geo_analysis_service_maps_network_error() -> None:
    """Network errors are exposed as service errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    service = GeoAnalysisService(_client_with_handler(handler))

    with pytest.raises(GeoAnalysisServiceError) as exc_info:
        service.list_geo_analyses()

    assert exc_info.value.code == "network_error"
