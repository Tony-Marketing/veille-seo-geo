"""Menu lateral de navigation."""

from collections.abc import Callable

from core.constants import NAVIGATION_PAGES, PAGE_DASHBOARD
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class Sidebar(QWidget):
    """Navigation entre les modules Desktop."""

    def __init__(self, on_page_selected: Callable[[str], None]) -> None:
        """Create the sidebar and connect selection events."""

        super().__init__()
        self.setObjectName("Sidebar")
        self._on_page_selected = on_page_selected

        self.navigation = QListWidget()
        self.navigation.setObjectName("SidebarNavigation")
        self.navigation.setSpacing(4)
        for page_name in NAVIGATION_PAGES:
            self.navigation.addItem(QListWidgetItem(page_name))

        self.navigation.currentTextChanged.connect(self._on_current_text_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.addWidget(self.navigation)

        self.select_page(PAGE_DASHBOARD)

    def select_page(self, page_name: str) -> None:
        """Select a page by name when it exists in the menu."""

        matches = self.navigation.findItems(page_name, Qt.MatchFlag.MatchExactly)
        if matches:
            self.navigation.setCurrentItem(matches[0])

    def _on_current_text_changed(self, page_name: str) -> None:
        """Forward page selection to the main window."""

        if page_name:
            self._on_page_selected(page_name)
