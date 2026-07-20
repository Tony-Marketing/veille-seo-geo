"""Tests for the Desktop GEO Intelligence service."""

from collections.abc import Callable

import httpx
from core.api_client import ApiClient
from services.geo_intelligence_service import GeoIntelligenceService


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


def test_desktop_service_uses_rest_contract_without_internet() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/summary"):
            return httpx.Response(200, json={"captures": 1})
        if request.url.path.endswith("/providers"):
            return httpx.Response(200, json={"providers": [{"provider": "chatgpt", "configured": False}]})
        if request.url.path.endswith("/history"):
            return httpx.Response(200, json={"points": []})
        if request.url.path.endswith("/import"):
            return httpx.Response(201, json={"received": 1, "created": 1, "duplicates": 0, "rejected": 0})
        return httpx.Response(200, json={"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0})

    service = GeoIntelligenceService(_client(handler))
    assert service.list_snapshots(website_id=7, provider="chatgpt").total == 0
    assert service.get_summary(website_id=7).data["captures"] == 1
    assert service.get_providers().data["providers"][0]["provider"] == "chatgpt"
    assert service.get_history(website_id=7).data["points"] == []
    assert service.import_observations([{"website_id": 7}]).data["created"] == 1
    assert all(request.url.host == "api.test" for request in requests)
