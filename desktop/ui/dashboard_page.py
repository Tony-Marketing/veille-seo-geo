"""Page Dashboard V2."""

from functools import partial
from typing import Any

from core.api_client import ApiClient
from core.config import APP_NAME, APP_VERSION
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from services.dashboard_v2_service import DashboardV2Service, DashboardV2ServiceError


class DashboardPage(QWidget):
    """Display Dashboard V2 data returned by the REST API."""

    website_selected = Signal(object)
    navigation_requested = Signal(str, object)

    WEBSITE_COLUMNS = ["Site", "Sante", "SEO", "GEO", "GSC", "GA4", "Bing", "Alertes", "Jobs", "Activite"]
    TREND_COLUMNS = ["Metrique", "Source", "Points"]
    RECOMMENDATION_COLUMNS = ["Priorite", "Severite", "Source", "Site", "Titre", "Navigation"]
    OPERATIONS_COLUMNS = ["Famille", "Indicateur", "Valeur"]

    def __init__(self, api_client: ApiClient) -> None:
        """Create the dashboard page."""

        super().__init__()
        self.api_client = api_client
        self.dashboard_service = DashboardV2Service(api_client)
        self.current_website: dict[str, Any] | None = None
        self.website_items: list[dict[str, Any]] = []
        self.recommendation_items: list[dict[str, Any]] = []

        title = QLabel("Dashboard V2")
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
        for index, (key, label, target) in enumerate(
            [
                ("health_score", "Sante globale", "Websites"),
                ("seo_score", "SEO", "SEO Analysis"),
                ("geo_score", "GEO", "GEO Analysis"),
                ("gsc_clicks", "Clics GSC", "Google Search Console"),
                ("ga4_sessions", "Sessions GA4", "Google Analytics 4"),
                ("bing_clicks", "Clics Bing", "Bing Webmaster Tools"),
                ("active_alerts", "Alertes actives", "Alertes"),
                ("failed_jobs", "Jobs en erreur", "Orchestrateur"),
            ],
        ):
            card = self._card(label, target)
            self.cards[key] = card.findChild(QLabel, "CardValue") or QLabel("-")
            cards_layout.addWidget(card, index // 4, index % 4)

        self.websites_table = self._table(self.WEBSITE_COLUMNS)
        self.websites_table.itemSelectionChanged.connect(self._select_dashboard_website)
        self.websites_table.itemDoubleClicked.connect(lambda _item: self._open_selected_website())
        self.trends_table = self._table(self.TREND_COLUMNS)
        self.recommendations_table = self._table(self.RECOMMENDATION_COLUMNS)
        self.recommendations_table.itemDoubleClicked.connect(lambda _item: self._open_selected_recommendation())
        self.operations_table = self._table(self.OPERATIONS_COLUMNS)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)

        meta_layout = QHBoxLayout()
        meta_layout.addWidget(app_label)
        meta_layout.addStretch()
        meta_layout.addWidget(self.backend_status)
        meta_layout.addWidget(self.user_label)

        secondary_layout = QHBoxLayout()
        secondary_layout.addWidget(self._section("Tendances", self.trends_table), stretch=1)
        secondary_layout.addWidget(self._section("Operations", self.operations_table), stretch=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addLayout(header_layout)
        layout.addLayout(meta_layout)
        layout.addWidget(self.message)
        layout.addLayout(cards_layout)
        layout.addWidget(self._section("Vue executive multi-sites", self.websites_table), stretch=1)
        layout.addWidget(self._section("Recommandations deterministes", self.recommendations_table), stretch=1)
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
        self.message.setText("Chargement du Dashboard V2...")
        try:
            filters = self._website_filters()
            overview = self.dashboard_service.get_overview(**filters).data
            trends = self.dashboard_service.get_trends(**filters).data
            websites = self.dashboard_service.list_websites(page_size=10, **filters)
            recommendations = self.dashboard_service.list_recommendations(page_size=10, **filters)
        except DashboardV2ServiceError as exc:
            self.message.setText(self._error_message(exc))
        else:
            self._populate(overview)
            self._populate_trends(trends)
            self._populate_websites(websites.items)
            self._populate_recommendations(recommendations.items)
            self.message.setText(self._status_message(overview))
        finally:
            self.refresh_button.setEnabled(True)

    def _populate(self, payload: dict[str, Any]) -> None:
        seo = self._dict(payload.get("seo"))
        geo = self._dict(payload.get("geo"))
        gsc = self._dict(payload.get("gsc"))
        ga4 = self._dict(payload.get("ga4"))
        bing = self._dict(payload.get("bing"))
        alerts = self._dict(payload.get("alerts"))
        operations = self._dict(payload.get("operations"))
        health = self._dict(payload.get("global_health"))

        self.cards["health_score"].setText(self._score(health.get("score")))
        self.cards["seo_score"].setText(self._score(seo.get("average_score") or seo.get("global_score")))
        self.cards["geo_score"].setText(self._score(geo.get("geo_score") or geo.get("global_score")))
        self.cards["gsc_clicks"].setText(str(gsc.get("clicks") or 0))
        self.cards["ga4_sessions"].setText(str(ga4.get("sessions") or 0))
        self.cards["bing_clicks"].setText(str(bing.get("clicks") or 0))
        self.cards["active_alerts"].setText(str(alerts.get("active") or 0))
        self.cards["failed_jobs"].setText(str(operations.get("failed_jobs") or 0))

        self._populate_operations(payload)

    def _populate_websites(self, items: list[dict[str, Any]]) -> None:
        """Render website summaries returned by the API."""

        self.website_items = items
        self.websites_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("name") or ""),
                f"{self._score(item.get('health_score'))} {item.get('health_status') or ''}".strip(),
                self._score(item.get("seo_score")),
                self._score(item.get("geo_score")),
                str(item.get("gsc_clicks") or 0),
                str(item.get("ga4_sessions") or 0),
                str(item.get("bing_clicks") or 0),
                str(item.get("active_alerts") or 0),
                str(item.get("failed_or_blocked_jobs") or 0),
                str(item.get("last_activity_at") or ""),
            ]
            self._set_row(self.websites_table, row, values)

    def _populate_trends(self, payload: dict[str, Any]) -> None:
        """Render trend series returned by the API."""

        items = self._list_of_dicts(payload.get("series"))
        self.trends_table.setRowCount(len(items))
        for row, item in enumerate(items):
            points = self._list_of_dicts(item.get("points"))
            values = [
                str(item.get("label") or item.get("metric") or ""),
                str(item.get("source") or ""),
                self._points_label(points),
            ]
            self._set_row(self.trends_table, row, values)

    def _populate_recommendations(self, items: list[dict[str, Any]]) -> None:
        """Render deterministic recommendations returned by the API."""

        self.recommendation_items = items
        self.recommendations_table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("priority") or ""),
                str(item.get("severity") or ""),
                str(item.get("source") or ""),
                str(item.get("website_name") or item.get("website_id") or ""),
                str(item.get("title") or ""),
                str(item.get("navigation_target") or ""),
            ]
            self._set_row(self.recommendations_table, row, values)

    def _populate_operations(self, payload: dict[str, Any]) -> None:
        """Render operations, alerts, monitoring and workers returned by the API."""

        operations = self._dict(payload.get("operations"))
        monitoring = self._dict(payload.get("monitoring"))
        alerts = self._dict(payload.get("alerts"))
        workers = self._dict(payload.get("workers"))
        rows = [
            ["Jobs", "En attente", operations.get("pending_jobs")],
            ["Jobs", "En cours", operations.get("running_jobs")],
            ["Jobs", "En erreur", operations.get("failed_jobs")],
            ["Jobs", "Bloques", operations.get("blocked_jobs")],
            ["Monitoring", "Evenements periode", monitoring.get("period_events")],
            ["Monitoring", "Critiques", monitoring.get("critical_events")],
            ["Alertes", "Actives", alerts.get("active")],
            ["Alertes", "Critiques", alerts.get("critical")],
            ["Workers", "Actifs", workers.get("active_workers")],
            ["Workers", "Statut", workers.get("status")],
        ]
        self.operations_table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            self._set_row(self.operations_table, row, ["" if value is None else str(value) for value in values])

    def _status_message(self, payload: dict[str, Any]) -> str:
        partial_data = payload.get("partial_data")
        if isinstance(partial_data, list) and partial_data:
            return f"Dashboard V2 a jour. Donnees partielles : {', '.join(str(item) for item in partial_data)}."
        return "Dashboard V2 a jour."

    def _points_label(self, points: list[dict[str, Any]]) -> str:
        if not points:
            return "-"
        return " | ".join(f"{item.get('date')}: {self._score(item.get('value'))}" for item in points[-4:])

    def _card(self, title: str, target: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setCursor(Qt.CursorShape.PointingHandCursor)
        group.setToolTip(f"Ouvrir {target}")
        group.mousePressEvent = partial(self._open_card_target, target)  # type: ignore[method-assign]
        value = QLabel("-")
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(group)
        layout.addWidget(value)
        return group

    def set_website_context(self, website: dict[str, Any] | None) -> None:
        """Apply the Website filter used by every Dashboard V2 request."""

        self.current_website = website

    def _website_filters(self) -> dict[str, Any]:
        website_id = self.current_website.get("id") if self.current_website is not None else None
        return {"website_id": website_id} if isinstance(website_id, int) else {}

    def _select_dashboard_website(self) -> None:
        row = self.websites_table.currentRow()
        if 0 <= row < len(self.website_items):
            item = self.website_items[row]
            website_id = item.get("website_id")
            if isinstance(website_id, int):
                self.website_selected.emit({"id": website_id, "name": item.get("name")})

    def _open_selected_website(self) -> None:
        row = self.websites_table.currentRow()
        if not 0 <= row < len(self.website_items):
            return
        website = self.website_items[row]
        self.navigation_requested.emit("Websites", {"website_id": website.get("website_id")})

    def _open_selected_recommendation(self) -> None:
        row = self.recommendations_table.currentRow()
        if not 0 <= row < len(self.recommendation_items):
            return
        item = self.recommendation_items[row]
        target = item.get("navigation_target")
        if not isinstance(target, str):
            return
        self.navigation_requested.emit(
            target,
            {
                "website_id": item.get("website_id"),
                "source": item.get("source"),
                "source_id": item.get("source_id"),
                "severity": item.get("severity"),
            },
        )

    def _open_card_target(self, target: str, _event: object) -> None:
        self.navigation_requested.emit(target, self._website_filters())

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

    def _error_message(self, exc: DashboardV2ServiceError) -> str:
        if exc.code == "unauthorized":
            return "Connexion requise pour afficher le Dashboard V2."
        if exc.code == "forbidden":
            return "Acces refuse : vous n'avez pas la permission de consulter le Dashboard V2."
        if exc.code == "validation_error":
            return "Parametres Dashboard V2 invalides."
        if exc.code == "server_error":
            return "Erreur serveur pendant le chargement du Dashboard V2."
        if exc.code == "backend_unavailable":
            return "Backend indisponible. Verifiez que l'API FastAPI est lancee."
        if exc.code == "network_error":
            return "Erreur reseau pendant la communication avec l'API."
        return f"Erreur inattendue pendant le chargement du Dashboard V2 : {exc}"

    def _user_label(self, user: dict[str, Any] | None) -> str:
        if not user:
            return "non connecte"
        first_name = str(user.get("first_name") or "").strip()
        last_name = str(user.get("last_name") or "").strip()
        full_name = " ".join(part for part in (first_name, last_name) if part)
        if full_name:
            return full_name
        return str(user.get("email") or "utilisateur connecte")
