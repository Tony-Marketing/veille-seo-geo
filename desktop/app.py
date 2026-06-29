"""Creation et configuration de l'application Desktop."""

from pathlib import Path

from core.config import APP_NAME
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_stylesheet() -> str:
    """Return the configured QSS stylesheet content."""

    stylesheet_path = Path(__file__).resolve().parent / "styles" / "dark.qss"
    return stylesheet_path.read_text(encoding="utf-8")


def create_application() -> QApplication:
    """Create the Qt application and apply global settings."""

    application = QApplication([])
    application.setApplicationName(APP_NAME)
    application.setStyleSheet(load_stylesheet())
    return application


def run_desktop_app() -> int:
    """Start the Desktop application event loop."""

    application = create_application()
    window = MainWindow()
    window.show()
    return application.exec()
