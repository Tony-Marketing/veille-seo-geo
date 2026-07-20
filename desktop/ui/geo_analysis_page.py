"""Page GEO Analysis du client Desktop."""

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
from services.geo_analysis_service import GeoAnalysisService, GeoAnalysisServiceError


class GeoAnalysisPage(QWidget):
    """Display and manage GEO analyses through the REST API."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    ANALYSIS_COLUMNS = ["ID", "SEO", "Statut", "Global", "GEO", "LLM", "Providers", "Recommandations"]
    PROVIDER_COLUMNS = ["Provider", "Modele", "Statut", "Page", "Erreur"]
    RECOMMENDATION_COLUMNS = ["Type", "Severite", "Priorite", "Titre", "Source"]

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.geo_service = GeoAnalysisService(api_client)
        self.analyses: list[dict[str, Any]] = []
        self.current_page = GeoAnalysisService.DEFAULT_PAGE
        self.page_size = GeoAnalysisService.DEFAULT_PAGE_SIZE
        self.current_website: dict[str, Any] | None = None

        title = QLabel("GEO Analysis")
        title.setObjectName("PageTitle")

        self.seo_analysis_input = QLineEdit()
        self.seo_analysis_input.setPlaceholderText("ID analyse SEO")

        self.providers_input = QLineEdit()
        self.providers_input.setPlaceholderText("Providers, ex: openai")
        self.providers_input.setText("openai")

        self.create_button = QPushButton("Creer")
        self.create_button.clicked.connect(self.create_geo_analysis)

        self.run_button = QPushButton("Lancer")
        self.run_button.clicked.connect(self.run_geo_analysis)
        self.run_button.setEnabled(False)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_geo_analyses)

        self.gsc_button = QPushButton("Ouvrir Google Search Console")
        self.gsc_button.clicked.connect(self.open_gsc)

        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.analyses_table = QTableWidget(0, len(self.ANALYSIS_COLUMNS))
        self.analyses_table.setObjectName("DataTable")
        self.analyses_table.setHorizontalHeaderLabels(self.ANALYSIS_COLUMNS)
        self.analyses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.analyses_table.verticalHeader().setVisible(False)
        self.analyses_table.setAlternatingRowColors(True)
        self.analyses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.analyses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.analyses_table.itemSelectionChanged.connect(self._on_analysis_selected)

        provider_label = QLabel("Resultats providers")
        provider_label.setObjectName("PageSubtitle")

        self.providers_table = QTableWidget(0, len(self.PROVIDER_COLUMNS))
        self.providers_table.setObjectName("DataTable")
        self.providers_table.setHorizontalHeaderLabels(self.PROVIDER_COLUMNS)
        self.providers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.providers_table.verticalHeader().setVisible(False)
        self.providers_table.setAlternatingRowColors(True)
        self.providers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        recommendation_label = QLabel("Recommandations")
        recommendation_label.setObjectName("PageSubtitle")

        self.recommendations_table = QTableWidget(0, len(self.RECOMMENDATION_COLUMNS))
        self.recommendations_table.setObjectName("DataTable")
        self.recommendations_table.setHorizontalHeaderLabels(self.RECOMMENDATION_COLUMNS)
        self.recommendations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recommendations_table.verticalHeader().setVisible(False)
        self.recommendations_table.setAlternatingRowColors(True)
        self.recommendations_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.seo_analysis_input)
        header_layout.addWidget(self.providers_input)
        header_layout.addWidget(self.create_button)
        header_layout.addWidget(self.run_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.gsc_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addWidget(self.analyses_table, stretch=2)
        layout.addWidget(provider_label)
        layout.addWidget(self.providers_table, stretch=1)
        layout.addWidget(recommendation_label)
        layout.addWidget(self.recommendations_table, stretch=1)

        self.load_geo_analyses()

    def load_geo_analyses(self) -> None:
        """Load GEO analyses and update the table."""

        self._set_busy(True)
        self.message.setText("Chargement des analyses GEO...")
        try:
            result = self.geo_service.list_geo_analyses(page=self.current_page, page_size=self.page_size)
        except GeoAnalysisServiceError as exc:
            self.analyses = []
            self.analyses_table.setRowCount(0)
            self.providers_table.setRowCount(0)
            self.recommendations_table.setRowCount(0)
            self.message.setText(self._error_message(exc))
        else:
            self._populate_analyses(result.items)
            self.message.setText(f"{result.total} analyse(s) GEO trouvee(s).")
            if not result.items:
                self.message.setText("Aucune analyse GEO a afficher.")
        finally:
            self._set_busy(False)

    def create_geo_analysis(self) -> None:
        """Create a GEO analysis from the SEO analysis id input."""

        seo_analysis_id = self._seo_analysis_id()
        if seo_analysis_id is None:
            self.message.setText("Saisissez un identifiant d'analyse SEO valide.")
            return
        self._set_busy(True)
        try:
            self.geo_service.create_geo_analysis(seo_analysis_id, self._providers())
        except GeoAnalysisServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_geo_analyses()
            self.message.setText("Analyse GEO creee.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)

    def run_geo_analysis(self) -> None:
        """Run the selected GEO analysis."""

        analysis = self._selected_analysis()
        if analysis is None:
            self.message.setText("Selectionnez une analyse GEO a lancer.")
            return
        analysis_id = analysis.get("id")
        if not isinstance(analysis_id, int):
            self.message.setText("Identifiant d'analyse GEO manquant.")
            return
        self._set_busy(True)
        self.message.setText("Analyse GEO en cours...")
        try:
            updated = self.geo_service.run_geo_analysis(analysis_id)
        except GeoAnalysisServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self.load_geo_analyses()
            self._populate_details(updated)
            self.message.setText("Analyse GEO terminee.")
            self.data_changed.emit()
        finally:
            self._set_busy(False)

    def _populate_analyses(self, analyses: list[dict[str, Any]]) -> None:
        self.analyses = analyses
        self.analyses_table.setRowCount(len(analyses))
        for row, analysis in enumerate(analyses):
            values = [
                str(analysis.get("id") or ""),
                str(analysis.get("seo_analysis_id") or ""),
                str(analysis.get("status") or ""),
                self._score(analysis.get("global_score")),
                self._score(analysis.get("geo_score")),
                self._score(analysis.get("llm_score")),
                ", ".join(str(provider) for provider in analysis.get("providers_requested") or []),
                str(analysis.get("recommendations_count") or 0),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.analyses_table.setItem(row, column, item)
        self._update_actions()

    def _populate_details(self, analysis: dict[str, Any]) -> None:
        providers = [item for item in analysis.get("provider_results") or [] if isinstance(item, dict)]
        recommendations = [item for item in analysis.get("recommendations") or [] if isinstance(item, dict)]

        self.providers_table.setRowCount(len(providers))
        for row, provider in enumerate(providers):
            values = [
                str(provider.get("provider_name") or ""),
                str(provider.get("model_name") or ""),
                str(provider.get("status") or ""),
                str(provider.get("crawl_page_id") or ""),
                str(provider.get("error_message") or ""),
            ]
            for column, value in enumerate(values):
                self.providers_table.setItem(row, column, QTableWidgetItem(value))

        self.recommendations_table.setRowCount(len(recommendations))
        for row, recommendation in enumerate(recommendations):
            values = [
                str(recommendation.get("recommendation_type") or ""),
                str(recommendation.get("severity") or ""),
                str(recommendation.get("priority") or ""),
                str(recommendation.get("title") or ""),
                str(recommendation.get("source") or ""),
            ]
            for column, value in enumerate(values):
                self.recommendations_table.setItem(row, column, QTableWidgetItem(value))

    def _on_analysis_selected(self) -> None:
        self._update_actions()
        analysis = self._selected_analysis()
        if analysis is None:
            return
        analysis_id = analysis.get("id")
        if not isinstance(analysis_id, int):
            return
        try:
            detail = self.geo_service.get_geo_analysis(analysis_id)
        except GeoAnalysisServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_details(detail)

    def _selected_analysis(self) -> dict[str, Any] | None:
        row = self.analyses_table.currentRow()
        if row < 0 or row >= len(self.analyses):
            return None
        return self.analyses[row]

    def _set_busy(self, busy: bool) -> None:
        self.create_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy)
        self.seo_analysis_input.setEnabled(not busy)
        self.providers_input.setEnabled(not busy)
        self._update_actions(disabled=busy)

    def _update_actions(self, *, disabled: bool = False) -> None:
        analysis = self._selected_analysis()
        if disabled or analysis is None:
            self.run_button.setEnabled(False)
            return
        status = str(analysis.get("status") or "")
        self.run_button.setEnabled(status in {"PENDING", "FAILED", "PARTIAL", "COMPLETED"})

    def _seo_analysis_id(self) -> int | None:
        value = self.seo_analysis_input.text().strip()
        if not value.isdigit():
            return None
        return int(value)

    def _providers(self) -> list[str]:
        providers = [item.strip().lower() for item in self.providers_input.text().split(",")]
        return [provider for provider in providers if provider] or ["openai"]

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        self.current_website = website

    def set_navigation_context(self, context: dict[str, Any]) -> None:
        seo_analysis_id = context.get("seo_analysis_id")
        if isinstance(seo_analysis_id, int):
            self.seo_analysis_input.setText(str(seo_analysis_id))

    def open_gsc(self) -> None:
        self.navigation_requested.emit("Google Search Console", {"website": self.current_website})

    def _score(self, value: object) -> str:
        if isinstance(value, int | float):
            return f"{float(value):.1f}"
        return "-"

    def _error_message(self, exc: GeoAnalysisServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour gerer les analyses GEO."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de gerer les analyses GEO."
        if exc.code == "not_found":
            return "Analyse GEO introuvable. Rafraichissez la liste."
        if exc.code == "conflict":
            return "Action impossible : verifiez que l'analyse SEO source est terminee."
        if exc.code == "validation_error":
            return "Donnees invalides. Verifiez l'identifiant SEO et les providers."
        if exc.code == "server_error":
            return "Erreur serveur pendant la gestion des analyses GEO."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant la gestion des analyses GEO : {exc}"
