"""Desktop page for transverse SEO/GEO recommendations."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
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
from services.recommendations_service import (
    RecommendationPaginatedPayload,
    RecommendationsService,
    RecommendationsServiceError,
)


class RecommendationsPage(QWidget):
    """Display, filter and update recommendations through the Desktop service."""

    navigation_requested = Signal(str, object)
    data_changed = Signal()

    COLUMNS = ["ID", "Priorite", "Statut", "Source", "Categorie", "Website", "Titre", "Impact", "Score"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the recommendations page."""

        super().__init__()
        self.recommendations_service = RecommendationsService(api_client)
        self.current_website: dict[str, Any] | None = None
        self.current_page = RecommendationsService.DEFAULT_PAGE
        self.page_size = RecommendationsService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("Recommandations SEO/GEO")
        title.setObjectName("PageTitle")
        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)
        self.dashboard_button = QPushButton("Ouvrir Dashboard V2")
        self.dashboard_button.clicked.connect(self.open_dashboard)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        for index, (key, label) in enumerate(
            [
                ("open", "Ouvertes"),
                ("acknowledged", "Prises en compte"),
                ("critical", "Critiques"),
                ("high", "Priorite haute"),
                ("resolved", "Resolues"),
                ("ignored", "Ignorees"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 3, index % 3)

        self.source_filter = self._combo(
            ["", "SEO", "GEO", "GEO_INTELLIGENCE", "MONITORING", "ALERTS", "GSC", "GA4", "BING"],
        )
        self.priority_filter = self._combo(["", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.status_filter = self._combo(["", "OPEN", "ACKNOWLEDGED", "RESOLVED", "IGNORED"])
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("Categorie")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche")
        self.filter_button = QPushButton("Filtrer")
        self.filter_button.clicked.connect(self.apply_filters)
        self.reset_button = QPushButton("Reinitialiser")
        self.reset_button.clicked.connect(self.reset_filters)

        self.table = self._table()
        self.acknowledge_button = QPushButton("Prendre en compte")
        self.acknowledge_button.clicked.connect(lambda: self.update_selected_status("ACKNOWLEDGED"))
        self.resolve_button = QPushButton("Resoudre")
        self.resolve_button.clicked.connect(lambda: self.update_selected_status("RESOLVED"))
        self.ignore_button = QPushButton("Ignorer")
        self.ignore_button.clicked.connect(lambda: self.update_selected_status("IGNORED"))
        self.reopen_button = QPushButton("Reouvrir")
        self.reopen_button.clicked.connect(lambda: self.update_selected_status("OPEN"))

        self.previous_button = QPushButton("Precedent")
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button = QPushButton("Suivant")
        self.next_button.clicked.connect(self.next_page)
        self.page_label = QLabel("Page -/-")

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.dashboard_button)
        header_layout.addWidget(self.refresh_button)

        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Source"))
        filters_layout.addWidget(self.source_filter)
        filters_layout.addWidget(QLabel("Priorite"))
        filters_layout.addWidget(self.priority_filter)
        filters_layout.addWidget(QLabel("Statut"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(self.category_filter)
        filters_layout.addWidget(self.search_input)
        filters_layout.addWidget(self.filter_button)
        filters_layout.addWidget(self.reset_button)

        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.acknowledge_button)
        actions_layout.addWidget(self.resolve_button)
        actions_layout.addWidget(self.ignore_button)
        actions_layout.addWidget(self.reopen_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.previous_button)
        actions_layout.addWidget(self.page_label)
        actions_layout.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(filters_layout)
        layout.addWidget(self._section("Recommandations", self.table), stretch=1)
        layout.addLayout(actions_layout)

        self.load_data()

    def load_data(self) -> None:
        """Load summary and recommendations through RecommendationsService."""

        self._set_busy(True)
        self.message.setText("Chargement des recommandations...")
        filters = self._filters()
        try:
            summary = self.recommendations_service.get_summary(**filters).data
            result = self.recommendations_service.list_recommendations(
                page=self.current_page,
                page_size=self.page_size,
                sort="score",
                order="desc",
                **filters,
            )
        except RecommendationsServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_summary(summary)
            self._populate_recommendations(result)
            self.message.setText(f"{result.total} recommandation(s) trouvee(s).")
        finally:
            self._set_busy(False)
            self._update_pagination()

    def apply_filters(self) -> None:
        """Restart pagination with the selected filters."""

        self.current_page = 1
        self.load_data()

    def reset_filters(self) -> None:
        """Clear explicit filters while preserving the shared Website context."""

        for combo in (self.source_filter, self.priority_filter, self.status_filter):
            combo.setCurrentIndex(0)
        self.category_filter.clear()
        self.search_input.clear()
        self.apply_filters()

    def previous_page(self) -> None:
        """Load the previous page when available."""

        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self) -> None:
        """Load the next page when available."""

        if self.total_pages and self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def update_selected_status(self, target: str) -> None:
        """Send one lifecycle action through the Desktop service."""

        recommendation_id = self._selected_id()
        if recommendation_id is None:
            self.message.setText("Selectionnez une recommandation.")
            return
        self._set_busy(True)
        try:
            self.recommendations_service.update_status(recommendation_id, target)
        except RecommendationsServiceError as exc:
            self.message.setText(self._error_message(exc))
            self._set_busy(False)
            return
        self._set_busy(False)
        self.load_data()
        self.data_changed.emit()

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        """Apply the Website selected in the shared Desktop session."""

        self.current_website = website
        self.current_page = 1

    def set_navigation_context(self, context: dict[str, Any]) -> None:
        """Apply filters received from transverse navigation."""

        for key, combo in (
            ("source", self.source_filter),
            ("priority", self.priority_filter),
            ("status", self.status_filter),
        ):
            value = context.get(key)
            if isinstance(value, str):
                index = combo.findData(value.upper())
                if index >= 0:
                    combo.setCurrentIndex(index)
        self.current_page = 1

    def open_dashboard(self) -> None:
        """Navigate back to Dashboard V2 with the current Website context."""

        self.navigation_requested.emit("Tableau de bord", self._website_context())

    def _filters(self) -> dict[str, Any]:
        return {
            **self._website_context(),
            "source": self._combo_value(self.source_filter),
            "priority": self._combo_value(self.priority_filter),
            "status": self._combo_value(self.status_filter),
            "category": self._text(self.category_filter),
            "search": self._text(self.search_input),
        }

    def _website_context(self) -> dict[str, Any]:
        website_id = self.current_website.get("id") if self.current_website is not None else None
        return {"website_id": website_id} if isinstance(website_id, int) else {}

    def _populate_summary(self, payload: dict[str, Any]) -> None:
        for key, label in self.cards.items():
            label.setText(str(payload.get(key) or 0))

    def _populate_recommendations(self, result: RecommendationPaginatedPayload) -> None:
        self.current_page = result.page
        self.page_size = result.page_size
        self.total_pages = result.pages
        self.table.setRowCount(len(result.items))
        for row, item in enumerate(result.items):
            values = [
                item.get("id"),
                item.get("priority"),
                item.get("status"),
                item.get("source"),
                item.get("category"),
                item.get("website_name") or item.get("website_id"),
                item.get("title"),
                item.get("impact"),
                item.get("score"),
            ]
            for column, value in enumerate(values):
                table_item = QTableWidgetItem("" if value is None else str(value))
                if column == 1:
                    table_item.setForeground(self._priority_color(str(value)))
                self.table.setItem(row, column, table_item)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        item = self.table.item(row, 0) if row >= 0 else None
        try:
            return int(item.text()) if item is not None else None
        except ValueError:
            return None

    def _update_pagination(self) -> None:
        pages_label = self.total_pages if self.total_pages else 0
        self.page_label.setText(f"Page {self.current_page}/{pages_label}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(bool(self.total_pages and self.current_page < self.total_pages))

    def _set_busy(self, busy: bool) -> None:
        for button in (
            self.refresh_button,
            self.filter_button,
            self.reset_button,
            self.acknowledge_button,
            self.resolve_button,
            self.ignore_button,
            self.reopen_button,
        ):
            button.setEnabled(not busy)

    def _card(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        value = QLabel("-")
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(group)
        layout.addWidget(value)
        return group

    def _section(self, title: str, widget: QWidget) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    def _table(self) -> QTableWidget:
        table = QTableWidget(0, len(self.COLUMNS))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(self.COLUMNS)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setColumnHidden(0, True)
        return table

    def _combo(self, values: list[str]) -> QComboBox:
        combo = QComboBox()
        for value in values:
            combo.addItem(value or "Tous", value)
        return combo

    def _combo_value(self, combo: QComboBox) -> str | None:
        value = combo.currentData()
        return str(value) if value else None

    def _text(self, widget: QLineEdit) -> str | None:
        value = widget.text().strip()
        return value or None

    def _priority_color(self, priority: str) -> QColor:
        if priority == "CRITICAL":
            return QColor("#d13438")
        if priority == "HIGH":
            return QColor("#f9a825")
        if priority == "MEDIUM":
            return QColor("#2563eb")
        return QColor("#6b7280")

    def _error_message(self, exc: RecommendationsServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter les recommandations."
        if exc.code == "forbidden":
            return "Acces refuse : permission recommandations insuffisante."
        if exc.code == "validation_error":
            return "Parametres de recommandations invalides."
        if exc.code == "not_found":
            return "Recommandation introuvable."
        if exc.code == "conflict":
            return "Cette transition de statut n'est pas autorisee."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement des recommandations."
        return f"Erreur inattendue pendant les recommandations : {exc}"
