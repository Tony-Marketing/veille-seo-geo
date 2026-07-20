"""Tests for the Desktop recommendations service."""

from collections.abc import Callable

import httpx
from core.api_client import ApiClient
from services.recommendations_service import RecommendationsService


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def test_recommendations_service_calls_list_summary_and_patch() -> None:
    """Desktop calls the REST contract with filters and status payload."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/summary"):
            return httpx.Response(200, json={"total": 1, "open": 1})
        if request.method == "PATCH":
            return httpx.Response(200, json={"id": 4, "status": "ACKNOWLEDGED"})
        return httpx.Response(
            200,
            json={"items": [{"id": 4}], "total": 1, "page": 1, "page_size": 20, "pages": 1},
        )

    service = RecommendationsService(_client(handler))
    listing = service.list_recommendations(website_id=7, priority="HIGH", search="title")
    summary = service.get_summary(website_id=7)
    updated = service.update_status(4, "ACKNOWLEDGED")

    assert listing.total == 1
    assert summary.data["open"] == 1
    assert updated.data["status"] == "ACKNOWLEDGED"
    assert requests[0].url.params["website_id"] == "7"
    assert requests[0].url.params["priority"] == "HIGH"
    assert requests[0].url.params["search"] == "title"
    assert requests[-1].method == "PATCH"
    assert requests[-1].content == b'{"status":"ACKNOWLEDGED"}'
