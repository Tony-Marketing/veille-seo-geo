"""Tests du lazy loading des pages Desktop."""

from collections.abc import Iterator

import pytest
from core.constants import (
    NAVIGATION_PAGES,
    PAGE_ALERTS,
    PAGE_BING_WEBMASTER_TOOLS,
    PAGE_DASHBOARD,
    PAGE_GEO_ANALYSIS,
    PAGE_GOOGLE_SEARCH_CONSOLE,
    PAGE_MONITORING,
    PAGE_ORCHESTRATION,
    PAGE_RECOMMENDATIONS,
    PAGE_SEO_ANALYSIS,
    PAGE_SYNC_SCHEDULES,
    PAGE_USERS,
    PAGE_WEBSITES,
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QWidget
from ui import main_window as main_window_module


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


@pytest.fixture()
def page_creation_log(monkeypatch: pytest.MonkeyPatch, qt_app: QApplication) -> Iterator[list[str]]:
    """Replace real pages with lightweight widgets and return the creation log."""

    assert qt_app is not None
    created: list[str] = []

    class FakePage(QWidget):
        page_name = "Fake"
        website_selected = Signal(object)
        navigation_requested = Signal(str, object)
        data_changed = Signal()

        def __init__(self, *_args: object) -> None:
            super().__init__()
            self.website_context: dict[str, object] | None = None
            self.navigation_context: dict[str, object] = {}
            self.refresh_count = 0
            created.append(self.page_name)

        def set_website_context(self, website: dict[str, object] | None) -> None:
            self.website_context = website

        def set_navigation_context(self, context: dict[str, object]) -> None:
            self.navigation_context = context

        def load_data(self) -> None:
            self.refresh_count += 1

    class FakeDashboardPage(FakePage):
        page_name = PAGE_DASHBOARD

        def load_overview(self) -> None:
            self.refresh_count += 1

        def refresh_backend_status(self) -> None:
            """Simulate the dashboard refresh hook."""

        def set_user(self, user: dict[str, object] | None) -> None:
            """Simulate the dashboard user hook."""

    def fake_page_class(page_name: str) -> type[FakePage]:
        return type(f"Fake{page_name.replace(' ', '')}Page", (FakePage,), {"page_name": page_name})

    monkeypatch.setattr(main_window_module, "DashboardPage", FakeDashboardPage)
    monkeypatch.setattr(main_window_module, "WebsitesPage", fake_page_class(PAGE_WEBSITES))
    monkeypatch.setattr(main_window_module, "EntitiesPage", fake_page_class("Entities"))
    monkeypatch.setattr(main_window_module, "KeywordsPage", fake_page_class("Keywords"))
    monkeypatch.setattr(main_window_module, "CompetitorsPage", fake_page_class("Competitors"))
    monkeypatch.setattr(main_window_module, "CrawlsPage", fake_page_class("Crawls"))
    monkeypatch.setattr(main_window_module, "SeoAnalysisPage", fake_page_class(PAGE_SEO_ANALYSIS))
    monkeypatch.setattr(main_window_module, "GSCPage", fake_page_class(PAGE_GOOGLE_SEARCH_CONSOLE))
    monkeypatch.setattr(main_window_module, "GeoAnalysisPage", fake_page_class(PAGE_GEO_ANALYSIS))
    monkeypatch.setattr(main_window_module, "BingWebmasterToolsPage", fake_page_class(PAGE_BING_WEBMASTER_TOOLS))
    monkeypatch.setattr(main_window_module, "SyncSchedulesPage", fake_page_class(PAGE_SYNC_SCHEDULES))
    monkeypatch.setattr(main_window_module, "MonitoringPage", fake_page_class(PAGE_MONITORING))
    monkeypatch.setattr(main_window_module, "AlertsPage", fake_page_class(PAGE_ALERTS))
    monkeypatch.setattr(main_window_module, "OrchestrationPage", fake_page_class(PAGE_ORCHESTRATION))
    monkeypatch.setattr(main_window_module, "RecommendationsPage", fake_page_class(PAGE_RECOMMENDATIONS))
    monkeypatch.setattr(main_window_module, "ProjectTasksPage", fake_page_class("Project Tasks"))
    monkeypatch.setattr(main_window_module, "ReportsPage", fake_page_class("Reports"))
    monkeypatch.setattr(main_window_module, "AdministrationPage", fake_page_class("Administration"))
    monkeypatch.setattr(main_window_module, "UsersPage", fake_page_class(PAGE_USERS))

    def unexpected_login_dialog(_self: object) -> bool:
        raise AssertionError("LoginDialog must not open automatically")

    monkeypatch.setattr(main_window_module.MainWindow, "_show_login_dialog", unexpected_login_dialog)

    yield created


def test_main_window_creates_only_dashboard_on_startup(page_creation_log: list[str]) -> None:
    """MainWindow startup eagerly creates only the dashboard."""

    window = main_window_module.MainWindow()
    try:
        assert page_creation_log == [PAGE_DASHBOARD]
        assert list(window.pages) == [PAGE_DASHBOARD]
        assert window.stack.count() == 1
    finally:
        window.close()


def test_main_window_creates_page_on_first_display(page_creation_log: list[str]) -> None:
    """A business page is created when first displayed."""

    window = main_window_module.MainWindow()
    try:
        window.show_page(PAGE_WEBSITES)

        assert PAGE_WEBSITES in window.pages
        assert page_creation_log == [PAGE_DASHBOARD, PAGE_WEBSITES]
        assert window.stack.count() == 2
    finally:
        window.close()


def test_main_window_reuses_existing_page_instance(page_creation_log: list[str]) -> None:
    """A page is created once and reused on later displays."""

    window = main_window_module.MainWindow()
    try:
        window.show_page(PAGE_WEBSITES)
        first_instance = window.pages[PAGE_WEBSITES]

        window.show_page(PAGE_WEBSITES)

        assert window.pages[PAGE_WEBSITES] is first_instance
        assert page_creation_log == [PAGE_DASHBOARD, PAGE_WEBSITES]
        assert window.stack.count() == 2
    finally:
        window.close()


def test_main_window_can_open_every_navigation_page(page_creation_log: list[str]) -> None:
    """Every navigation entry remains reachable with lazy loading."""

    window = main_window_module.MainWindow()
    try:
        for page_name in NAVIGATION_PAGES:
            window.show_page(page_name)

        assert set(window.pages) == set(NAVIGATION_PAGES)
        assert window.stack.count() == len(NAVIGATION_PAGES)
        assert len(page_creation_log) == len(NAVIGATION_PAGES)
    finally:
        window.close()


def test_main_window_propagates_website_navigation_and_refreshes_open_views(
    page_creation_log: list[str],
) -> None:
    """Qt signals carry Website context and refresh the integrated operational views."""

    window = main_window_module.MainWindow()
    website = {"id": 7, "entity_id": 3, "name": "Site Groupe"}
    try:
        source = window.get_page(PAGE_WEBSITES)
        assert source is not None
        source.website_selected.emit(website)

        assert window.session.current_website_id == 7
        assert window.session.current_entity_id == 3

        source.navigation_requested.emit("Crawls", {"website": website, "crawl_id": 11})
        crawls = window.pages["Crawls"]
        assert window.stack.currentWidget() is crawls
        assert crawls.website_context == website
        assert crawls.navigation_context == {"website": website, "crawl_id": 11}

        dashboard = window.pages[PAGE_DASHBOARD]
        monitoring = window.get_page(PAGE_MONITORING)
        alerts = window.get_page(PAGE_ALERTS)
        assert monitoring is not None
        assert alerts is not None

        source.data_changed.emit()

        assert dashboard.refresh_count == 1
        assert monitoring.refresh_count == 1
        assert alerts.refresh_count == 1
    finally:
        window.close()
