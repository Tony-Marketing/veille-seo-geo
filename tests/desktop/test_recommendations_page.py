"""Tests for the Desktop recommendations page."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from PySide6.QtWidgets import QApplication
from ui.recommendations_page import RecommendationsPage


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return the shared QApplication used by widget tests."""

    return QApplication.instance() or QApplication([])


def test_recommendations_page_loads_filters_paginates_and_updates(qt_app: QApplication) -> None:
    """The page delegates loading, pagination and lifecycle actions to its service."""

    assert qt_app is not None
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.url.path.endswith("/summary"):
            return httpx.Response(
                200,
                json={
                    "open": 1,
                    "acknowledged": 0,
                    "resolved": 0,
                    "ignored": 0,
                    "critical": 0,
                    "high": 1,
                },
            )
        if request.method == "PATCH":
            return httpx.Response(200, json={"id": 1, "status": "ACKNOWLEDGED"})
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 1,
                        "priority": "HIGH",
                        "status": "OPEN",
                        "source": "SEO",
                        "category": "metadata",
                        "website_name": "Example",
                        "title": "Corriger le Title",
                        "impact": "SEO",
                        "score": 80,
                    },
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "pages": 1,
            },
        )

    page = RecommendationsPage(_client(handler))
    try:
        assert page.cards["open"].text() == "1"
        assert page.table.rowCount() == 1
        page.source_filter.setCurrentText("SEO")
        page.apply_filters()
        page.table.selectRow(0)
        page.update_selected_status("ACKNOWLEDGED")

        assert any(method == "PATCH" for method, _path in seen)
        assert page.page_label.text() == "Page 1/1"
    finally:
        page.close()


def test_recommendations_page_displays_permission_error(qt_app: QApplication) -> None:
    """The page exposes a readable permission error."""

    assert qt_app is not None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "forbidden"})

    page = RecommendationsPage(_client(handler))
    try:
        assert "Acces refuse" in page.message.text()
    finally:
        page.close()
