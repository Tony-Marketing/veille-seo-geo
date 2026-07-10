"""Tests de la page Desktop Alertes."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from PySide6.QtWidgets import QApplication
from ui.alerts_page import AlertsPage


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


def test_alerts_page_loads_filters_and_actions(qt_app: QApplication) -> None:
    """The page displays and updates alerts through the Desktop service."""

    assert qt_app is not None
    seen_requests: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append((request.method, request.url.path))
        if request.url.path.endswith("/summary"):
            return httpx.Response(
                200,
                json={
                    "total": 1,
                    "active": 1,
                    "acknowledged": 0,
                    "resolved": 0,
                    "info": 0,
                    "warning": 1,
                    "critical": 0,
                    "last_alert_at": "2026-07-10T08:00:00Z",
                },
            )
        if request.url.path.endswith("/refresh-from-monitoring"):
            return httpx.Response(200, json={"created": 1, "updated": 0, "total_processed": 1, "alerts": []})
        if request.url.path.endswith("/acknowledge"):
            return httpx.Response(200, json={"id": 1, "status": "Acknowledged"})
        if request.url.path.endswith("/resolve"):
            return httpx.Response(200, json={"id": 1, "status": "Resolved"})
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 1,
                        "source_type": "GSC",
                        "category": "sync",
                        "severity": "Warning",
                        "status": "Active",
                        "title": "Warning - GSC - sync",
                        "first_seen_at": "2026-07-10T08:00:00Z",
                        "last_seen_at": "2026-07-10T08:00:00Z",
                    },
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
                "pages": 1,
            },
        )

    page = AlertsPage(_client_with_handler(handler))
    try:
        assert page.cards["active"].text() == "1"
        assert page.table.rowCount() == 1

        page.status_filter.setCurrentText("Active")
        page.severity_filter.setCurrentText("Warning")
        page.load_data()
        page.refresh_from_monitoring()
        page.table.selectRow(0)
        page.acknowledge_selected()
        page.table.selectRow(0)
        page.resolve_selected()

        methods = [method for method, _path in seen_requests]
        assert methods.count("GET") >= 8
        assert methods.count("POST") == 3
    finally:
        page.close()


def test_alerts_page_displays_service_errors(qt_app: QApplication) -> None:
    """The page renders readable load errors."""

    assert qt_app is not None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "forbidden"})

    page = AlertsPage(_client_with_handler(handler))
    try:
        assert "Acces refuse" in page.message.text()
    finally:
        page.close()
