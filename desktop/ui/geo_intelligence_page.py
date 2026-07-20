"""GEO Intelligence Desktop page."""

from typing import Any

from core.api_client import ApiClient
from PySide6.QtCore import Qt, Signal
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
from services.geo_intelligence_service import GeoIntelligenceService, GeoIntelligenceServiceError


class GeoIntelligencePage(QWidget):
    """Display normalized GEO Intelligence data without business calculations."""

    navigation_requested = Signal(str, object)

    SNAPSHOT_COLUMNS = ["Date", "Provider", "Entite", "Prompt", "Visibilite", "Citations", "Sources", "Rang"]
    HISTORY_COLUMNS = ["Periode", "Provider", "Captures", "Visibilite", "Citations", "Sources", "Frequence"]

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.geo_intelligence_service = GeoIntelligenceService(api_client)
        self.current_website: dict[str, Any] | None = None
        self.current_page = GeoIntelligenceService.DEFAULT_PAGE
        self.page_size = GeoIntelligenceService.DEFAULT_PAGE_SIZE
        self.total_pages = 0

        title = QLabel("GEO Intelligence & IA Generatives")
        title.setObjectName("PageTitle")
        self.website_label = QLabel("Website : tous")
        self.message = QLabel("")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)
        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_data)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        for index, (key, label) in enumerate(
            [
                ("captures", "Captures"),
                ("score", "Visibilite moyenne"),
                ("providers", "Fournisseurs couverts"),
                ("citations", "Citations"),
                ("sources", "Sources"),
                ("frequency", "Frequence d'apparition"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 3, index % 3)

        self.provider_filter = QComboBox()
        self.provider_filter.addItem("")
        self.entity_filter = QLineEdit()
        self.entity_filter.setPlaceholderText("Entite")
        self.prompt_filter = QLineEdit()
        self.prompt_filter.setPlaceholderText("Prompt")
        self.date_from_filter = QLineEdit()
        self.date_from_filter.setPlaceholderText("Depuis (ISO 8601)")
        self.date_to_filter = QLineEdit()
        self.date_to_filter.setPlaceholderText("Jusqu'a (ISO 8601)")
        self.filter_button = QPushButton("Filtrer")
        self.filter_button.clicked.connect(self.apply_filters)
        self.reset_button = QPushButton("Reinitialiser")
        self.reset_button.clicked.connect(self.reset_filters)

        self.snapshots_table = self._table(self.SNAPSHOT_COLUMNS)
        self.history_table = self._table(self.HISTORY_COLUMNS)
        self.previous_button = QPushButton("Precedent")
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button = QPushButton("Suivant")
        self.next_button.clicked.connect(self.next_page)
        self.page_label = QLabel("Page -/-")

        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.website_label)
        header.addWidget(self.refresh_button)

        filters = QHBoxLayout()
        for label, widget in [
            ("Provider", self.provider_filter),
            ("", self.entity_filter),
            ("", self.prompt_filter),
            ("", self.date_from_filter),
            ("", self.date_to_filter),
        ]:
            if label:
                filters.addWidget(QLabel(label))
            filters.addWidget(widget)
        filters.addWidget(self.filter_button)
        filters.addWidget(self.reset_button)

        pagination = QHBoxLayout()
        pagination.addStretch()
        pagination.addWidget(self.previous_button)
        pagination.addWidget(self.page_label)
        pagination.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(filters)
        layout.addWidget(self._section("Captures normalisees", self.snapshots_table), stretch=2)
        layout.addLayout(pagination)
        layout.addWidget(self._section("Historique par fournisseur", self.history_table), stretch=1)
        self._load_providers()
        self.load_data()

    def load_data(self) -> None:
        """Load list, summary and history through the Desktop service."""

        self._set_busy(True)
        filters = self._filters()
        try:
            summary = self.geo_intelligence_service.get_summary(**filters).data
            snapshots = self.geo_intelligence_service.list_snapshots(
                page=self.current_page,
                page_size=self.page_size,
                sort="captured_at",
                order="desc",
                **filters,
            )
            history = self.geo_intelligence_service.get_history(**filters).data
        except GeoIntelligenceServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate_summary(summary)
            self._populate_snapshots(snapshots.items)
            self._populate_history(history)
            self.total_pages = snapshots.pages
            self.message.setText(f"{snapshots.total} capture(s) GEO Intelligence.")
        finally:
            self._set_busy(False)
            self._update_pagination()

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        """Apply the Website selected in the shared Desktop context."""

        self.current_website = website
        self.current_page = 1
        label = str(website.get("name") or website.get("url") or website.get("id")) if website else "tous"
        self.website_label.setText(f"Website : {label}")

    def apply_filters(self) -> None:
        self.current_page = 1
        self.load_data()

    def reset_filters(self) -> None:
        self.provider_filter.setCurrentIndex(0)
        for widget in (self.entity_filter, self.prompt_filter, self.date_from_filter, self.date_to_filter):
            widget.clear()
        self.apply_filters()

    def previous_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self) -> None:
        if self.total_pages and self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def _load_providers(self) -> None:
        try:
            payload = self.geo_intelligence_service.get_providers().data
        except GeoIntelligenceServiceError:
            return
        providers = payload.get("providers")
        if not isinstance(providers, list):
            return
        for item in providers:
            if isinstance(item, dict) and isinstance(item.get("provider"), str):
                self.provider_filter.addItem(item["provider"])

    def _filters(self) -> dict[str, Any]:
        website_id = self.current_website.get("id") if self.current_website else None
        return {
            "website_id": website_id if isinstance(website_id, int) else None,
            "provider": self.provider_filter.currentText() or None,
            "entity": self.entity_filter.text().strip() or None,
            "prompt": self.prompt_filter.text().strip() or None,
            "date_from": self.date_from_filter.text().strip() or None,
            "date_to": self.date_to_filter.text().strip() or None,
        }

    def _populate_summary(self, payload: dict[str, Any]) -> None:
        providers = payload.get("providers_covered")
        self.cards["captures"].setText(str(payload.get("captures") or 0))
        self.cards["score"].setText(self._number(payload.get("average_visibility_score")))
        self.cards["providers"].setText(str(len(providers)) if isinstance(providers, list) else "0")
        self.cards["citations"].setText(str(payload.get("citation_count") or 0))
        self.cards["sources"].setText(str(payload.get("source_count") or 0))
        self.cards["frequency"].setText(self._number(payload.get("appearance_frequency"), suffix=" %"))

    def _populate_snapshots(self, items: list[dict[str, Any]]) -> None:
        self.snapshots_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._set_row(
                self.snapshots_table,
                row,
                [
                    item.get("captured_at"),
                    item.get("provider"),
                    item.get("entity"),
                    item.get("prompt"),
                    item.get("visibility_score"),
                    item.get("citation_count"),
                    item.get("source_count"),
                    item.get("ranking"),
                ],
            )

    def _populate_history(self, payload: dict[str, Any]) -> None:
        points = payload.get("points")
        items = [item for item in points if isinstance(item, dict)] if isinstance(points, list) else []
        self.history_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self._set_row(
                self.history_table,
                row,
                [
                    item.get("date"),
                    item.get("provider"),
                    item.get("captures"),
                    item.get("average_visibility_score"),
                    item.get("citation_count"),
                    item.get("source_count"),
                    item.get("appearance_frequency"),
                ],
            )

    def _set_busy(self, busy: bool) -> None:
        for widget in (self.refresh_button, self.filter_button, self.reset_button):
            widget.setEnabled(not busy)

    def _update_pagination(self) -> None:
        self.page_label.setText(f"Page {self.current_page}/{self.total_pages or 1}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(bool(self.total_pages and self.current_page < self.total_pages))

    def _card(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        value = QLabel("-")
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(group)
        layout.addWidget(value)
        return group

    def _section(self, title: str, table: QTableWidget) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(table)
        return group

    def _table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _set_row(self, table: QTableWidget, row: int, values: list[object]) -> None:
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem("" if value is None else str(value)))

    def _number(self, value: object, *, suffix: str = "") -> str:
        return f"{float(value):.1f}{suffix}" if isinstance(value, int | float) else "-"

    def _error_message(self, exc: GeoIntelligenceServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour consulter GEO Intelligence."
        if exc.code == "forbidden":
            return "Permission insuffisante pour consulter GEO Intelligence."
        if exc.code == "validation_error":
            return "Filtres GEO Intelligence invalides."
        if exc.code == "backend_unavailable":
            return "Backend GEO Intelligence indisponible."
        return f"Erreur GEO Intelligence : {exc}"
