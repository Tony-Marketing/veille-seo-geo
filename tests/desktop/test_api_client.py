"""Tests du client API Desktop."""

import httpx
import pytest
from core.api_client import ApiClient, ApiClientError


def _client_with_response(response: httpx.Response) -> ApiClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return response

    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def test_api_client_builds_url_from_base_url() -> None:
    """ApiClient combines the configured base URL and relative path."""

    seen_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json={"status": "ok"})

    client = ApiClient(base_url="http://api.test/api/v1/", transport=httpx.MockTransport(handler))

    assert client.get("/health") == {"status": "ok"}
    assert seen_urls == ["http://api.test/api/v1/health"]


def test_get_returns_json_payload() -> None:
    """GET returns the decoded JSON response."""

    client = _client_with_response(httpx.Response(200, json={"items": []}))

    assert client.get("/websites") == {"items": []}


def test_no_content_response_returns_none() -> None:
    """204 responses are normalized to None."""

    client = _client_with_response(httpx.Response(204))

    assert client.delete("/websites/1") is None


def test_http_status_error_raises_api_client_error_with_status_code() -> None:
    """HTTP errors are converted to ApiClientError and keep the status code."""

    client = _client_with_response(httpx.Response(404, json={"detail": "Ressource introuvable."}))

    with pytest.raises(ApiClientError) as exc_info:
        client.get("/missing")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details == {"detail": "Ressource introuvable."}
    assert "Erreur API 404" in str(exc_info.value)


def test_request_error_raises_api_client_error() -> None:
    """Network errors are converted to ApiClientError."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    with pytest.raises(ApiClientError) as exc_info:
        client.get("/health")

    assert exc_info.value.status_code is None
    assert "API indisponible" in str(exc_info.value)


def test_invalid_json_response_raises_api_client_error() -> None:
    """Invalid JSON responses are reported as readable API client errors."""

    client = _client_with_response(httpx.Response(200, content=b"not-json"))

    with pytest.raises(ApiClientError) as exc_info:
        client.get("/health")

    assert exc_info.value.status_code == 200
    assert "Reponse API invalide" in str(exc_info.value)


def test_check_health_returns_true_for_ok_status() -> None:
    """Health check succeeds only when the API returns status ok."""

    client = _client_with_response(httpx.Response(200, json={"status": "ok"}))

    assert client.check_health() is True


def test_check_health_returns_false_when_api_is_unavailable() -> None:
    """Health check hides transport errors behind a False result."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))

    assert client.check_health() is False


def test_check_health_returns_false_for_unexpected_payload() -> None:
    """Health check rejects unexpected payloads."""

    client = _client_with_response(httpx.Response(200, json={"status": "degraded"}))

    assert client.check_health() is False
