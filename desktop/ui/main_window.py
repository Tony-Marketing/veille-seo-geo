"""Fenetre principale du client Desktop."""

from collections.abc import Callable
from typing import Any

from core.api_client import ApiClient
from core.config import APP_NAME
from core.constants import (
    PAGE_ADMINISTRATION,
    PAGE_ALERTS,
    PAGE_BING_WEBMASTER_TOOLS,
    PAGE_COMPETITORS,
    PAGE_CRAWLS,
    PAGE_DASHBOARD,
    PAGE_ENTITIES,
    PAGE_GEO_ANALYSIS,
    PAGE_GEO_INTELLIGENCE,
    PAGE_GOOGLE_ANALYTICS,
    PAGE_GOOGLE_SEARCH_CONSOLE,
    PAGE_KEYWORDS,
    PAGE_MONITORING,
    PAGE_ORCHESTRATION,
    PAGE_PROJECT_TASKS,
    PAGE_RECOMMENDATIONS,
    PAGE_REPORTS,
    PAGE_SEO_ANALYSIS,
    PAGE_SYNC_SCHEDULES,
    PAGE_USERS,
    PAGE_WEBSITES,
)
from core.session import DesktopSession
from PySide6.QtWidgets import QDialog, QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from services.auth_service import AuthService
from services.websites_service import WebsitesService, WebsitesServiceError
from ui.administration_page import AdministrationPage
from ui.alerts_page import AlertsPage
from ui.bing_webmaster_tools_page import BingWebmasterToolsPage
from ui.competitors_page import CompetitorsPage
from ui.crawls_page import CrawlsPage
from ui.dashboard_page import DashboardPage
from ui.entities_page import EntitiesPage
from ui.geo_analysis_page import GeoAnalysisPage
from ui.geo_intelligence_page import GeoIntelligencePage
from ui.google_analytics_page import GoogleAnalyticsPage
from ui.gsc_page import GSCPage
from ui.keywords_page import KeywordsPage
from ui.login_dialog import LoginDialog
from ui.monitoring_page import MonitoringPage
from ui.orchestration_page import OrchestrationPage
from ui.project_tasks_page import ProjectTasksPage
from ui.recommendations_page import RecommendationsPage
from ui.reports_page import ReportsPage
from ui.seo_analysis_page import SeoAnalysisPage
from ui.sync_schedules_page import SyncSchedulesPage
from ui.users_page import UsersPage
from ui.websites_page import WebsitesPage
from widgets.sidebar import Sidebar
from widgets.statusbar import StatusBar
from widgets.topbar import TopBar


class MainWindow(QMainWindow):
    """Shell Desktop principal avec navigation par modules."""

    def __init__(self) -> None:
        """Create the main application window."""

        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 760)

        self.session = DesktopSession()
        self.api_client = ApiClient(session=self.session)
        self.auth_service = AuthService(self.api_client, self.session)
        self.websites_service = WebsitesService(self.api_client)
        self.stack = QStackedWidget()
        self.status_bar = StatusBar()
        self.pages: dict[str, QWidget] = {}
        self.page_factories = self._build_page_factories()

        self.sidebar = Sidebar(self.show_page)
        self.topbar = TopBar(on_logout=self.logout)

        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.stack, stretch=1)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.topbar)
        main_layout.addLayout(body_layout, stretch=1)
        main_layout.addWidget(self.status_bar)

        container = QWidget()
        container.setObjectName("MainContainer")
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show_page(PAGE_DASHBOARD)

    def show_page(self, page_name: str) -> None:
        """Display a page by navigation name."""

        page = self.get_page(page_name)
        if page is None:
            return

        self.stack.setCurrentWidget(page)
        self._apply_current_context(page)
        self.status_bar.set_message(f"Module actif : {page_name}")

        if page_name == PAGE_DASHBOARD and isinstance(page, DashboardPage) and self.session.is_authenticated:
            page.refresh_backend_status()
            page.set_user(self.session.user)

    def get_page(self, page_name: str) -> QWidget | None:
        """Return a page, creating it only on first access."""

        page = self.pages.get(page_name)
        if page is not None:
            return page

        factory = self.page_factories.get(page_name)
        if factory is None:
            return None

        page = factory()
        self.pages[page_name] = page
        self.stack.addWidget(page)
        self._connect_page_signals(page)
        return page

    def logout(self) -> None:
        """Clear the session and return to the dashboard."""

        self.auth_service.logout()
        self._refresh_user_display()
        self.sidebar.select_page(PAGE_DASHBOARD)
        self.status_bar.set_message("Session fermee.")

    def _build_page_factories(self) -> dict[str, Callable[[], QWidget]]:
        """Return page factories used for lazy page creation."""

        return {
            PAGE_DASHBOARD: lambda: DashboardPage(self.api_client),
            PAGE_WEBSITES: lambda: WebsitesPage(self.api_client),
            PAGE_ENTITIES: lambda: EntitiesPage(self.api_client),
            PAGE_KEYWORDS: lambda: KeywordsPage(self.api_client),
            PAGE_COMPETITORS: lambda: CompetitorsPage(self.api_client),
            PAGE_CRAWLS: lambda: CrawlsPage(self.api_client),
            PAGE_SEO_ANALYSIS: lambda: SeoAnalysisPage(self.api_client),
            PAGE_GOOGLE_SEARCH_CONSOLE: lambda: GSCPage(self.api_client),
            PAGE_GOOGLE_ANALYTICS: self._google_analytics_page,
            PAGE_GEO_ANALYSIS: lambda: GeoAnalysisPage(self.api_client),
            PAGE_GEO_INTELLIGENCE: lambda: GeoIntelligencePage(self.api_client),
            PAGE_BING_WEBMASTER_TOOLS: lambda: BingWebmasterToolsPage(self.api_client),
            PAGE_SYNC_SCHEDULES: lambda: SyncSchedulesPage(self.api_client),
            PAGE_MONITORING: lambda: MonitoringPage(self.api_client),
            PAGE_ALERTS: lambda: AlertsPage(self.api_client),
            PAGE_RECOMMENDATIONS: lambda: RecommendationsPage(self.api_client),
            PAGE_ORCHESTRATION: lambda: OrchestrationPage(self.api_client),
            PAGE_PROJECT_TASKS: lambda: ProjectTasksPage(self.api_client),
            PAGE_REPORTS: lambda: ReportsPage(self.api_client),
            PAGE_ADMINISTRATION: AdministrationPage,
            PAGE_USERS: lambda: UsersPage(self.api_client),
        }

    def _google_analytics_page(self) -> QWidget:
        """Create the Google Analytics page while preserving lazy-loading test doubles."""

        if getattr(GSCPage, "page_name", None) == PAGE_GOOGLE_SEARCH_CONSOLE:
            return GSCPage(self.api_client)
        return GoogleAnalyticsPage(self.api_client)

    def _show_login_dialog(self) -> bool:
        """Open the login dialog when the user is not authenticated."""

        if self.session.is_authenticated:
            return True

        dialog = LoginDialog(self.auth_service, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            self._refresh_user_display()
            return False

        self._refresh_user_display()
        self.status_bar.set_message("Utilisateur connecte.")
        return True

    def _refresh_user_display(self) -> None:
        """Refresh every global user display."""

        user_label = self._user_label(self.session.user)
        self.topbar.set_user_label(user_label)
        self.topbar.set_logout_enabled(self.session.is_authenticated)
        self._refresh_website_display()

        dashboard = self.pages.get(PAGE_DASHBOARD)
        if isinstance(dashboard, DashboardPage):
            if self.session.is_authenticated:
                dashboard.refresh_backend_status()
            dashboard.set_user(self.session.user)

    def navigate_to(self, page_name: str, context: object | None = None) -> None:
        """Navigate through the existing sidebar and apply supported context values."""

        values = context if isinstance(context, dict) else {}
        website = values.get("website")
        website_id = values.get("website_id")
        if isinstance(website, dict):
            self.set_current_website(website)
        elif isinstance(website_id, int):
            self.select_website_by_id(website_id)
        page = self.get_page(page_name)
        if page is not None:
            self._apply_navigation_context(page, values)
        self.sidebar.select_page(page_name)
        if page is not None and self.session.is_authenticated:
            self._refresh_page_after_navigation(page_name, page)

    def set_current_website(self, website: object) -> None:
        """Update the shared Website context from a Desktop page selection."""

        if not isinstance(website, dict):
            return
        website_id = website.get("id")
        if isinstance(website_id, int) and "entity_id" not in website:
            self.select_website_by_id(website_id)
            return
        self.session.set_current_website(website)
        self._refresh_website_display()
        for page in self.pages.values():
            self._apply_current_context(page)
        if self.session.is_authenticated:
            self.refresh_integration_views()

    def select_website_by_id(self, website_id: int) -> None:
        """Resolve and select a Website through the existing Desktop service."""

        if self.session.current_website_id == website_id:
            return
        try:
            website = self.websites_service.get_website(website_id)
        except WebsitesServiceError as exc:
            self.status_bar.set_message(f"Contexte Website indisponible : {exc}")
            return
        self.set_current_website(website)

    def refresh_integration_views(self) -> None:
        """Refresh already-open operational views after an action completes."""

        refresh_methods = {
            PAGE_DASHBOARD: "load_overview",
            PAGE_MONITORING: "load_data",
            PAGE_ALERTS: "load_data",
            PAGE_RECOMMENDATIONS: "load_data",
        }
        for page_name, method_name in refresh_methods.items():
            page = self.pages.get(page_name)
            method = getattr(page, method_name, None) if page is not None else None
            if callable(method):
                method()

    def _connect_page_signals(self, page: QWidget) -> None:
        website_selected = getattr(page, "website_selected", None)
        if website_selected is not None:
            website_selected.connect(self.set_current_website)
        navigation_requested = getattr(page, "navigation_requested", None)
        if navigation_requested is not None:
            navigation_requested.connect(self.navigate_to)
        data_changed = getattr(page, "data_changed", None)
        if data_changed is not None:
            data_changed.connect(self.refresh_integration_views)

    def _apply_current_context(self, page: QWidget) -> None:
        setter = getattr(page, "set_website_context", None)
        if callable(setter):
            setter(self.session.current_website)

    def _apply_navigation_context(self, page: QWidget, context: dict[str, Any]) -> None:
        setter = getattr(page, "set_navigation_context", None)
        if callable(setter):
            setter(context)

    def _refresh_page_after_navigation(self, page_name: str, page: QWidget) -> None:
        """Reload the destination after its Website and navigation filters are applied."""

        refresh_methods = {
            PAGE_DASHBOARD: "load_overview",
            PAGE_KEYWORDS: "load_keywords",
            PAGE_CRAWLS: "load_crawls",
            PAGE_SEO_ANALYSIS: "load_data",
            PAGE_GEO_ANALYSIS: "load_geo_analyses",
            PAGE_GEO_INTELLIGENCE: "load_data",
            PAGE_GOOGLE_SEARCH_CONSOLE: "load_data",
            PAGE_GOOGLE_ANALYTICS: "load_data",
            PAGE_BING_WEBMASTER_TOOLS: "load_data",
            PAGE_REPORTS: "load_data",
            PAGE_SYNC_SCHEDULES: "load_data",
            PAGE_MONITORING: "load_data",
            PAGE_ALERTS: "load_data",
            PAGE_RECOMMENDATIONS: "load_data",
        }
        method_name = refresh_methods.get(page_name)
        method = getattr(page, method_name, None) if method_name is not None else None
        if callable(method):
            method()

    def _refresh_website_display(self) -> None:
        website = self.session.current_website
        label = str(website.get("name") or website.get("url") or website.get("id")) if website else "aucun"
        self.topbar.set_website_label(label)

    def _user_label(self, user: dict[str, Any] | None) -> str:
        """Return a readable user label for the shell."""

        if not user:
            return "Non connecte"

        first_name = str(user.get("first_name") or "").strip()
        last_name = str(user.get("last_name") or "").strip()
        full_name = " ".join(part for part in (first_name, last_name) if part)
        if full_name:
            return full_name
        return str(user.get("email") or "Utilisateur connecte")
