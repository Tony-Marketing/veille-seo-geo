"""Fenetre principale du client Desktop."""

from core.api_client import ApiClient
from core.config import APP_NAME
from core.constants import (
    PAGE_ADMINISTRATION,
    PAGE_COMPETITORS,
    PAGE_DASHBOARD,
    PAGE_ENTITIES,
    PAGE_KEYWORDS,
    PAGE_REPORTS,
    PAGE_WEBSITES,
)
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from ui.administration_page import AdministrationPage
from ui.competitors_page import CompetitorsPage
from ui.dashboard_page import DashboardPage
from ui.entities_page import EntitiesPage
from ui.keywords_page import KeywordsPage
from ui.reports_page import ReportsPage
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

        self.api_client = ApiClient()
        self.stack = QStackedWidget()
        self.status_bar = StatusBar()
        self.pages = self._build_pages()

        for page in self.pages.values():
            self.stack.addWidget(page)

        sidebar = Sidebar(self.show_page)
        topbar = TopBar()

        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(sidebar)
        body_layout.addWidget(self.stack, stretch=1)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(topbar)
        main_layout.addLayout(body_layout, stretch=1)
        main_layout.addWidget(self.status_bar)

        container = QWidget()
        container.setObjectName("MainContainer")
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show_page(PAGE_DASHBOARD)

    def show_page(self, page_name: str) -> None:
        """Display a page by navigation name."""

        page = self.pages.get(page_name)
        if page is None:
            return

        self.stack.setCurrentWidget(page)
        self.status_bar.set_message(f"Module actif : {page_name}")

        if page_name == PAGE_DASHBOARD and isinstance(page, DashboardPage):
            page.refresh_backend_status()

    def _build_pages(self) -> dict[str, QWidget]:
        """Create every page available in the shell."""

        return {
            PAGE_DASHBOARD: DashboardPage(self.api_client),
            PAGE_WEBSITES: WebsitesPage(self.api_client),
            PAGE_ENTITIES: EntitiesPage(),
            PAGE_KEYWORDS: KeywordsPage(),
            PAGE_COMPETITORS: CompetitorsPage(),
            PAGE_REPORTS: ReportsPage(),
            PAGE_ADMINISTRATION: AdministrationPage(),
        }
