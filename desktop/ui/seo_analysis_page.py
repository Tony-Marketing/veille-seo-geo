"""Desktop page for the existing SEO Analysis module."""

from collections.abc import Callable
from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.seo_analysis_service import SeoAnalysisService, SeoAnalysisServiceError


class SeoAnalysisPage(QWidget):
    """Expose existing SEO Analysis API operations without local business logic."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()
    COLUMNS = ["ID", "Crawl", "Statut", "Progression", "Score", "Pages", "Issues", "Erreur"]

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.seo_service = SeoAnalysisService(api_client)
        self.analyses: list[dict[str, Any]] = []
        self.current_website: dict[str, Any] | None = None

        title = QLabel("SEO Analysis")
        title.setObjectName("PageTitle")
        self.crawl_id_input = QLineEdit()
        self.crawl_id_input.setPlaceholderText("ID crawl")
        self.create_button = QPushButton("Creer")
        self.create_button.clicked.connect(self.create_analysis)
        self.run_button = QPushButton("Lancer")
        self.run_button.clicked.connect(self.run_selected)
        self.run_button.setEnabled(False)
        self.geo_button = QPushButton("Ouvrir GEO Analysis")
        self.geo_button.clicked.connect(self.open_geo_analysis)
        self.geo_button.setEnabled(False)
        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setObjectName("DataTable")
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._update_actions)

        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.crawl_id_input)
        header.addWidget(self.create_button)
        header.addWidget(self.run_button)
        header.addWidget(self.geo_button)
        header.addWidget(self.refresh_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(self.message)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self) -> None:
        """Load SEO analyses and expose homogeneous loading, empty and success states."""

        self._set_busy(True)
        self.message.setText("Chargement des analyses SEO...")
        try:
            result = self.seo_service.list_analyses()
        except SeoAnalysisServiceError as exc:
            self.analyses = []
            self.table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            self._populate(result.items)
            self.message.setText(
                f"{result.total} analyse(s) SEO chargee(s)." if result.items else "Aucune analyse SEO a afficher.",
            )
        finally:
            self._set_busy(False)

    def create_analysis(self) -> None:
        crawl_id = self._input_id(self.crawl_id_input)
        if crawl_id is None:
            self.message.setText("Saisissez un identifiant de crawl valide.")
            return
        self._run_action(lambda: self.seo_service.create_analysis(crawl_id), "Analyse SEO creee.")

    def run_selected(self) -> None:
        analysis = self._selected_analysis()
        analysis_id = analysis.get("id") if analysis is not None else None
        if not isinstance(analysis_id, int):
            self.message.setText("Selectionnez une analyse SEO.")
            return
        self._run_action(lambda: self.seo_service.run_analysis(analysis_id), "Analyse SEO terminee.")

    def open_geo_analysis(self) -> None:
        analysis = self._selected_analysis()
        analysis_id = analysis.get("id") if analysis is not None else None
        if not isinstance(analysis_id, int):
            return
        self.navigation_requested.emit(
            "GEO Analysis",
            {"website": self.current_website, "seo_analysis_id": analysis_id},
        )

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website

    def set_navigation_context(self, context: dict[str, Any]) -> None:
        crawl_id = context.get("crawl_id")
        if isinstance(crawl_id, int):
            self.crawl_id_input.setText(str(crawl_id))

    def _run_action(self, action: Callable[[], dict[str, Any]], success_message: str) -> None:
        self._set_busy(True)
        try:
            action()
        except SeoAnalysisServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self.load_data()
        self.message.setText(success_message)
        self.data_changed.emit()

    def _populate(self, analyses: list[dict[str, Any]]) -> None:
        self.analyses = analyses
        self.table.setRowCount(len(analyses))
        for row, item in enumerate(analyses):
            values = [
                item.get("id"),
                item.get("crawl_session_id"),
                item.get("status"),
                item.get("progress_percent"),
                item.get("global_score"),
                f"{item.get('pages_analyzed', 0)}/{item.get('pages_total', 0)}",
                item.get("issues_total"),
                item.get("error_message"),
            ]
            for column, value in enumerate(values):
                cell = QTableWidgetItem("" if value is None else str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, column, cell)
        self._update_actions()

    def _selected_analysis(self) -> dict[str, Any] | None:
        row = self.table.currentRow()
        return self.analyses[row] if 0 <= row < len(self.analyses) else None

    def _update_actions(self) -> None:
        item = self._selected_analysis()
        status = str(item.get("status") or "") if item is not None else ""
        self.run_button.setEnabled(item is not None and status != "RUNNING")
        self.geo_button.setEnabled(item is not None and status == "COMPLETED")

    def _set_busy(self, busy: bool) -> None:
        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        self.crawl_id_input.setEnabled(not busy)
        if busy:
            self.run_button.setEnabled(False)
            self.geo_button.setEnabled(False)
        else:
            self._update_actions()

    def _input_id(self, widget: QLineEdit) -> int | None:
        value = widget.text().strip()
        return int(value) if value.isdigit() and int(value) > 0 else None

    def _error_message(self, exc: SeoAnalysisServiceError) -> str:
        messages = {
            "unauthorized": "Connexion requise pour consulter SEO Analysis.",
            "forbidden": "Acces refuse a SEO Analysis.",
            "not_found": "Crawl ou analyse SEO introuvable.",
            "conflict": "Action SEO impossible dans l'etat actuel.",
            "validation_error": "Parametres SEO invalides.",
            "server_error": "Erreur serveur pendant SEO Analysis.",
            "backend_unavailable": "Backend indisponible.",
            "network_error": "Erreur reseau pendant SEO Analysis.",
        }
        return messages.get(exc.code, f"Erreur inattendue SEO Analysis : {exc}")
