"""Page Dashboard SEO/GEO."""

from typing import Any

from core.api_client import ApiClient
from core.config import APP_NAME, APP_VERSION
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.dashboard_service import DashboardService, DashboardServiceError


class DashboardPage(QWidget):
    """Display the unified SEO/GEO dashboard through the REST API."""

    PRIORITY_COLUMNS = ["URL", "SEO", "GEO", "Critiques", "Recommandations", "Priorite", "Raison"]
    COMPARISON_COLUMNS = ["URL", "SEO", "GEO", "Ecart", "Interpretation"]
    DISTRIBUTION_COLUMNS = ["Groupe", "Plage", "Pages", "Part"]
    RECOMMENDATION_COLUMNS = ["Type", "Severite", "Priorite", "Titre", "Source"]
    ISSUE_COLUMNS = ["Severite", "Famille", "Code", "Occurrences"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the dashboard page."""

        super().__init__()
        self.api_client = api_client
        self.dashboard_service = DashboardService(api_client)

        title = QLabel("Dashboard SEO / GEO")
        title.setObjectName("PageTitle")

        app_label = QLabel(f"{APP_NAME} - Version {APP_VERSION}")
        app_label.setObjectName("PageSubtitle")

        self.backend_status = QLabel("Backend : non verifie")
        self.backend_status.setObjectName("ValueLabel")

        self.user_label = QLabel("Utilisateur : non connecte")
        self.user_label.setObjectName("ValueLabel")

        self.message = QLabel("Connectez-vous pour charger le Dashboard.")
        self.message.setObjectName("MessageLabel")
        self.message.setWordWrap(True)

        self.refresh_button = QPushButton("Rafraichir")
        self.refresh_button.clicked.connect(self.load_overview)

        self.cards: dict[str, QLabel] = {}
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        for index, (key, label) in enumerate(
            [
                ("crawl_pages", "Pages crawlees"),
                ("seo_average", "Score SEO moyen"),
                ("seo_pages", "Pages SEO analysees"),
                ("seo_critical", "Erreurs critiques"),
                ("geo_average", "Score GEO moyen"),
                ("geo_analyses", "Analyses GEO"),
                ("geo_best", "Meilleure page GEO"),
                ("geo_worst", "Pire page GEO"),
            ],
        ):
            card = self._card(label)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 4, index % 4)

        self.priority_table = self._table(self.PRIORITY_COLUMNS)
        self.comparison_table = self._table(self.COMPARISON_COLUMNS)
        self.seo_distribution_table = self._table(self.DISTRIBUTION_COLUMNS)
        self.geo_distribution_table = self._table(self.DISTRIBUTION_COLUMNS)
        self.recommendations_table = self._table(self.RECOMMENDATION_COLUMNS)
        self.issues_table = self._table(self.ISSUE_COLUMNS)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        meta_layout = QHBoxLayout()
        meta_layout.addWidget(app_label)
        meta_layout.addStretch()
        meta_layout.addWidget(self.backend_status)
        meta_layout.addWidget(self.user_label)

        distribution_layout = QHBoxLayout()
        distribution_layout.addWidget(self._section("Repartition SEO", self.seo_distribution_table), stretch=1)
        distribution_layout.addWidget(self._section("Repartition GEO", self.geo_distribution_table), stretch=1)

        secondary_layout = QHBoxLayout()
        secondary_layout.addWidget(self._section("Principaux problemes SEO", self.issues_table), stretch=1)
        secondary_layout.addWidget(self._section("Recommandations GEO", self.recommendations_table), stretch=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(meta_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addLayout(distribution_layout)
        layout.addWidget(self._section("Pages prioritaires", self.priority_table), stretch=1)
        layout.addWidget(self._section("Comparaison SEO / GEO", self.comparison_table), stretch=1)
        layout.addLayout(secondary_layout)

    def refresh_backend_status(self) -> None:
        """Refresh backend availability and dashboard data."""

        available = self.api_client.check_health()
        status = "connecte" if available else "indisponible"
        self.backend_status.setText(f"Backend : {status}")
        if available:
            self.load_overview()

    def set_user(self, user: dict[str, Any] | None) -> None:
        """Update the displayed current user."""

        self.user_label.setText(f"Utilisateur : {self._user_label(user)}")

    def load_overview(self) -> None:
        """Load dashboard overview from the REST API."""

        self.refresh_button.setEnabled(False)
        self.message.setText("Chargement du Dashboard...")
        try:
            payload = self.dashboard_service.get_overview().data
        except DashboardServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate(payload)
            self.message.setText("Dashboard a jour.")
        finally:
            self.refresh_button.setEnabled(True)

    def _populate(self, payload: dict[str, Any]) -> None:
        crawl = self._dict(payload.get("crawl"))
        seo = self._dict(payload.get("seo"))
        geo = self._dict(payload.get("geo"))
        comparison = self._dict(payload.get("comparison"))

        self.cards["crawl_pages"].setText(str(crawl.get("crawled_pages_count") or 0))
        self.cards["seo_average"].setText(self._score(seo.get("average_score")))
        self.cards["seo_pages"].setText(str(seo.get("analyzed_pages_count") or 0))
        self.cards["seo_critical"].setText(str(seo.get("critical_errors_count") or 0))
        self.cards["geo_average"].setText(self._score(geo.get("average_score")))
        self.cards["geo_analyses"].setText(str(geo.get("analyses_count") or 0))
        self.cards["geo_best"].setText(self._page_label(self._dict(geo.get("best_page"))))
        self.cards["geo_worst"].setText(self._page_label(self._dict(geo.get("worst_page"))))

        self._populate_distribution(self.seo_distribution_table, payload.get("seo_score_distribution"))
        self._populate_distribution(self.geo_distribution_table, payload.get("geo_score_distribution"))
        self._populate_priority_pages(payload.get("priority_pages"))
        self._populate_comparison(comparison.get("pages"))
        self._populate_issues(seo.get("top_issues"))
        self._populate_recommendations(geo.get("top_recommendations"))

    def _populate_distribution(self, table: QTableWidget, payload: object) -> None:
        items = self._list_of_dicts(payload)
        total = sum(int(item.get("count") or 0) for item in items)
        table.setRowCount(len(items))
        for row, item in enumerate(items):
            count = int(item.get("count") or 0)
            values = [
                str(item.get("label") or ""),
                f"{item.get('min_score')}-{item.get('max_score')}",
                str(count),
                "",
            ]
            self._set_row(table, row, values)
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int(count / total * 100) if total else 0)
            progress.setFormat("%p%")
            table.setCellWidget(row, 3, progress)

    def _populate_priority_pages(self, payload: object) -> None:
        items = self._list_of_dicts(payload)
        self.priority_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("url") or ""),
                self._score(item.get("seo_score")),
                self._score(item.get("geo_score")),
                str(item.get("critical_issues_count") or 0),
                str(item.get("recommendations_count") or 0),
                self._score(item.get("priority_score")),
                str(item.get("reason") or ""),
            ]
            self._set_row(self.priority_table, row, values)

    def _populate_comparison(self, payload: object) -> None:
        items = self._list_of_dicts(payload)
        self.comparison_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("url") or ""),
                self._score(item.get("seo_score")),
                self._score(item.get("geo_score")),
                self._score(item.get("gap")),
                str(item.get("interpretation") or ""),
            ]
            self._set_row(self.comparison_table, row, values)

    def _populate_issues(self, payload: object) -> None:
        items = self._list_of_dicts(payload)
        self.issues_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("severity") or ""),
                str(item.get("family") or ""),
                str(item.get("code") or ""),
                str(item.get("count") or 0),
            ]
            self._set_row(self.issues_table, row, values)

    def _populate_recommendations(self, payload: object) -> None:
        items = self._list_of_dicts(payload)
        self.recommendations_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("recommendation_type") or ""),
                str(item.get("severity") or ""),
                str(item.get("priority") or ""),
                str(item.get("title") or ""),
                str(item.get("source") or ""),
            ]
            self._set_row(self.recommendations_table, row, values)

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

    def _table(self, columns: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setObjectName("DataTable")
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _set_row(self, table: QTableWidget, row: int, values: list[str]) -> None:
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            table.setItem(row, column, item)

    def _dict(self, value: object) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _list_of_dicts(self, value: object) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    def _score(self, value: object) -> str:
        if isinstance(value, int | float):
            return f"{float(value):.1f}"
        return "-"

    def _page_label(self, page: dict[str, Any]) -> str:
        if not page:
            return "-"
        score = self._score(page.get("score"))
        url = str(page.get("url") or "page")
        return f"{score} - {url}"

    def _error_message(self, exc: DashboardServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour afficher le Dashboard."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter le Dashboard."
        if exc.code == "validation_error":
            return "Parametres Dashboard invalides."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement du Dashboard."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant le chargement du Dashboard : {exc}"

    def _user_label(self, user: dict[str, Any] | None) -> str:
        if not user:
            return "non connecte"
        first_name = str(user.get("first_name") or "").strip()
        last_name = str(user.get("last_name") or "").strip()
        full_name = " ".join(part for part in (first_name, last_name) if part)
        if full_name:
            return full_name
        return str(user.get("email") or "utilisateur connecte")
