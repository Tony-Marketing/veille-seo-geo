"""Tests for HTTP fetcher."""

import httpx

from backend.app.crawler.fetcher import HttpFetcher


def test_fetcher_returns_http_response_details() -> None:
    """HTTP responses are normalized for the engine."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, text="<html></html>", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        result = HttpFetcher(client=client).fetch("https://example.com/")
    finally:
        client.close()

    assert result.status_code == 200
    assert result.final_url == "https://example.com/"
    assert result.content_type == "text/html"
    assert result.is_html is True
    assert result.error_message is None


def test_fetcher_maps_network_errors() -> None:
    """Network errors are captured in the fetch result."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        result = HttpFetcher(client=client).fetch("https://example.com/")
    finally:
        client.close()

    assert result.status_code is None
    assert "connection refused" in str(result.error_message)

