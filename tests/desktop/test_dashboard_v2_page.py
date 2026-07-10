"""Tests for Dashboard V2 Desktop page."""

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication
from ui import dashboard_page as dashboard_page_module
from ui.dashboard_page import DashboardPage


class FakeDashboardV2Payload:
    """Simple payload wrapper matching the Desktop service contract."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data


class FakeDashboardV2Paginated:
    """Simple paginated wrapper matching the Desktop service contract."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        self.items = items
        self.total = len(items)
        self.page = 1
        self.page_size = 10
        self.pages = 1
        self.filters = {}


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


def test_dashboard_v2_page_loads_progressive_sections(monkeypatch, qt_app: QApplication) -> None:
    """Dashboard page renders V2 data loaded through its Desktop service."""

    calls: list[str] = []

    class FakeDashboardV2Service:
        def __init__(self, _api_client: object) -> None:
            pass

        def get_overview(self) -> FakeDashboardV2Payload:
            calls.append("overview")
            return FakeDashboardV2Payload(
                {
                    "global_health": {"score": 82},
                    "seo": {"average_score": 75},
                    "geo": {"geo_score": 70},
                    "gsc": {"clicks": 10},
                    "ga4": {"sessions": 20},
                    "bing": {"clicks": 5},
                    "alerts": {"active": 1, "critical": 1},
                    "operations": {"failed_jobs": 2, "pending_jobs": 3, "running_jobs": 1, "blocked_jobs": 0},
                    "monitoring": {"period_events": 4, "critical_events": 1},
                    "workers": {"active_workers": 1, "status": "operational"},
                    "partial_data": [],
                },
            )

        def get_trends(self) -> FakeDashboardV2Payload:
            calls.append("trends")
            return FakeDashboardV2Payload(
                {"series": [{"label": "SEO Score", "source": "seo", "points": [{"date": "2026-07-10", "value": 75}]}]},
            )

        def list_websites(self, **_kwargs: object) -> FakeDashboardV2Paginated:
            calls.append("websites")
            return FakeDashboardV2Paginated(
                [
                    {
                        "name": "Example",
                        "health_score": 82,
                        "health_status": "good",
                        "seo_score": 75,
                        "geo_score": 70,
                        "gsc_clicks": 10,
                        "ga4_sessions": 20,
                        "bing_clicks": 5,
                        "active_alerts": 1,
                        "failed_or_blocked_jobs": 2,
                    },
                ],
            )

        def list_recommendations(self, **_kwargs: object) -> FakeDashboardV2Paginated:
            calls.append("recommendations")
            return FakeDashboardV2Paginated(
                [
                    {
                        "priority": 1,
                        "severity": "critical",
                        "source": "seo",
                        "website_name": "Example",
                        "title": "Corriger une issue",
                        "navigation_target": "SEO Analysis",
                    },
                ],
            )

    monkeypatch.setattr(dashboard_page_module, "DashboardV2Service", FakeDashboardV2Service)

    page = DashboardPage(api_client=object())
    page.load_overview()

    assert calls == ["overview", "trends", "websites", "recommendations"]
    assert page.cards["health_score"].text() == "82.0"
    assert page.websites_table.rowCount() == 1
    assert page.recommendations_table.rowCount() == 1
    assert page.trends_table.rowCount() == 1
    assert page.operations_table.rowCount() == 10
