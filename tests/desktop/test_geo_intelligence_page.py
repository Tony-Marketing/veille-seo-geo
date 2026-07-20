"""Tests for the GEO Intelligence Desktop page."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from PySide6.QtWidgets import QApplication
from ui.geo_intelligence_page import GeoIntelligencePage


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_page_displays_kpis_filters_history_and_pagination(qt_app: QApplication) -> None:
    assert qt_app is not None
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/providers"):
            return httpx.Response(200, json={"providers": [{"provider": "chatgpt", "configured": False}]})
        if request.url.path.endswith("/summary"):
            return httpx.Response(
                200,
                json={
                    "captures": 1,
                    "average_visibility_score": 25,
                    "providers_covered": ["chatgpt"],
                    "citation_count": 1,
                    "source_count": 1,
                    "appearance_frequency": 100,
                },
            )
        if request.url.path.endswith("/history"):
            return httpx.Response(
                200,
                json={
                    "points": [
                        {
                            "date": "2026-07-20",
                            "provider": "chatgpt",
                            "captures": 1,
                            "average_visibility_score": 25,
                            "citation_count": 1,
                            "source_count": 1,
                            "appearance_frequency": 100,
                        },
                    ],
                },
            )
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "captured_at": "2026-07-20T10:00:00Z",
                        "provider": "chatgpt",
                        "entity": "Marque",
                        "prompt": "Prompt",
                        "visibility_score": 25,
                        "citation_count": 1,
                        "source_count": 1,
                        "ranking": 2,
                    },
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "pages": 1,
            },
        )

    page = GeoIntelligencePage(_client(handler))
    try:
        page.set_website_context({"id": 7, "name": "Website GEO"})
        page.provider_filter.setCurrentText("chatgpt")
        page.apply_filters()

        assert page.cards["score"].text() == "25.0"
        assert page.snapshots_table.rowCount() == 1
        assert page.history_table.rowCount() == 1
        assert page.page_label.text() == "Page 1/1"
        assert any(request.url.params.get("website_id") == "7" for request in seen)
    finally:
        page.close()
