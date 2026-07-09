"""Tests de la page Desktop Monitoring."""

from collections.abc import Callable

import httpx
import pytest
from core.api_client import ApiClient
from PySide6.QtWidgets import QApplication
from ui.monitoring_page import MonitoringPage


def _client_with_handler(handler: Callable[[httpx.Request], httpx.Response]) -> ApiClient:
    return ApiClient(base_url="http://api.test/api/v1", transport=httpx.MockTransport(handler))


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


def test_monitoring_page_loads_consultative_data(qt_app: QApplication) -> None:
    """The page displays monitoring data without mutation calls."""

    assert qt_app is not None
    seen_methods: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_methods.append(request.method)
        if request.url.path.endswith("/overview"):
            return httpx.Response(
                200,
                json={
                    "total_events": 2,
                    "events_today": 1,
                    "warning_events": 1,
                    "error_events": 0,
                    "critical_events": 0,
                    "active_sync_schedules": 1,
                    "inactive_sync_schedules": 0,
                    "next_runs": [{"name": "Import GSC"}],
                    "last_event": None,
                },
            )
        if request.url.path.endswith("/connectors"):
            return httpx.Response(
                200,
                json=[
                    {
                        "name": "Google Search Console",
                        "status": "operational",
                        "enabled": True,
                        "last_sync": None,
                        "next_sync": None,
                    },
                ],
            )
        if request.url.path.endswith("/events"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "created_at": "2026-07-09T08:00:00Z",
                            "event_type": "sync",
                            "severity": "warning",
                            "source": "GSC",
                            "message": "Import en retard",
                        },
                    ],
                    "total": 1,
                    "page": 1,
                    "page_size": 10,
                    "pages": 1,
                },
            )
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "name": "Import GSC",
                        "sync_type": "GSC",
                        "frequency": "Quotidien",
                        "status": "Active",
                        "is_active": True,
                        "last_run_at": None,
                        "next_run_at": "2026-07-10T08:00:00Z",
                    },
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
                "pages": 1,
            },
        )

    page = MonitoringPage(_client_with_handler(handler))
    try:
        assert page.cards["total_events"].text() == "2"
        assert page.connectors_table.rowCount() == 1
        assert page.events_table.rowCount() == 1
        assert page.schedules_table.rowCount() == 1
        assert seen_methods == ["GET", "GET", "GET", "GET"]
    finally:
        page.close()


def test_monitoring_page_displays_service_errors(qt_app: QApplication) -> None:
    """The page renders readable load errors."""

    assert qt_app is not None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"detail": "forbidden"})

    page = MonitoringPage(_client_with_handler(handler))
    try:
        assert "Acces refuse" in page.message.text()
    finally:
        page.close()
