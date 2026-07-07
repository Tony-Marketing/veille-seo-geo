"""Tests du lazy loading des pages Desktop."""

from collections.abc import Iterator

import pytest
from core.constants import (
    NAVIGATION_PAGES,
    PAGE_DASHBOARD,
    PAGE_GEO_ANALYSIS,
    PAGE_GOOGLE_SEARCH_CONSOLE,
    PAGE_WEBSITES,
)
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

        def __init__(self, *_args: object) -> None:
            super().__init__()
            created.append(self.page_name)

    class FakeDashboardPage(FakePage):
        page_name = PAGE_DASHBOARD

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
    monkeypatch.setattr(main_window_module, "GSCPage", fake_page_class(PAGE_GOOGLE_SEARCH_CONSOLE))
    monkeypatch.setattr(main_window_module, "GeoAnalysisPage", fake_page_class(PAGE_GEO_ANALYSIS))
    monkeypatch.setattr(main_window_module, "ProjectTasksPage", fake_page_class("Project Tasks"))
    monkeypatch.setattr(main_window_module, "ReportsPage", fake_page_class("Reports"))
    monkeypatch.setattr(main_window_module, "AdministrationPage", fake_page_class("Administration"))
    monkeypatch.setattr(main_window_module.MainWindow, "_show_login_dialog", lambda self: True)

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
