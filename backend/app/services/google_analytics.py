"""Business service for Google Analytics 4."""

from collections.abc import Callable
from datetime import UTC, datetime
from math import ceil
from typing import TypeVar

from fastapi import HTTPException, status

from backend.app.connectors.google_analytics import (
    GoogleAnalyticsConnector,
    GoogleAnalyticsOAuthTokenData,
    NotConfiguredGoogleAnalyticsConnector,
)
from backend.app.core.security import decrypt_secret, encrypt_secret
from backend.app.models import GoogleAnalyticsProperty
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.google_analytics import (
    GoogleAnalyticsBreakdownItem,
    GoogleAnalyticsBreakdownResponse,
    GoogleAnalyticsImportFilters,
    GoogleAnalyticsImportHistoryList,
    GoogleAnalyticsImportHistoryRead,
    GoogleAnalyticsImportList,
    GoogleAnalyticsImportRead,
    GoogleAnalyticsImportRequest,
    GoogleAnalyticsImportStatus,
    GoogleAnalyticsKpiRead,
    GoogleAnalyticsMetricFilters,
    GoogleAnalyticsMetricList,
    GoogleAnalyticsMetricRead,
    GoogleAnalyticsOAuthConnectRequest,
    GoogleAnalyticsOAuthRefreshRequest,
    GoogleAnalyticsOAuthResponse,
    GoogleAnalyticsPropertyCreate,
    GoogleAnalyticsPropertyList,
    GoogleAnalyticsPropertyRead,
    GoogleAnalyticsPropertyUpdate,
    GoogleAnalyticsSummaryResponse,
)
from backend.app.schemas.pagination import PaginationParams

RepositoryResult = TypeVar("RepositoryResult")


class GoogleAnalyticsService:
    """Manage Google Analytics properties, OAuth data and imports."""

    METRIC_NAME_MAP = {
        "users": "users",
        "newusers": "new_users",
        "new_users": "new_users",
        "sessions": "sessions",
        "engagedsessions": "engaged_sessions",
        "engaged_sessions": "engaged_sessions",
        "screenpageviews": "screen_page_views",
        "screen_page_views": "screen_page_views",
        "averagesessionduration": "average_session_duration",
        "average_session_duration": "average_session_duration",
        "engagementrate": "engagement_rate",
        "engagement_rate": "engagement_rate",
        "conversions": "conversions",
        "totalrevenue": "total_revenue",
        "total_revenue": "total_revenue",
    }
    DIMENSION_NAME_MAP = {
        "date": "date",
        "source": "source",
        "medium": "medium",
        "campaign": "campaign",
        "devicecategory": "device_category",
        "device_category": "device_category",
        "country": "country",
    }

    def __init__(
        self,
        repository: GoogleAnalyticsRepository,
        *,
        connector: GoogleAnalyticsConnector | None = None,
    ) -> None:
        self.repository = repository
        self.connector = connector or NotConfiguredGoogleAnalyticsConnector()

    def list_properties(self, params: PaginationParams) -> GoogleAnalyticsPropertyList:
        """Return paginated Google Analytics properties."""

        items, total = self.repository.list_properties(params)
        return GoogleAnalyticsPropertyList(
            items=[GoogleAnalyticsPropertyRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def create_property(self, payload: GoogleAnalyticsPropertyCreate) -> GoogleAnalyticsPropertyRead:
        """Create a Google Analytics property."""

        existing = self.repository.get_property_by_property_id(payload.property_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Propriete Google Analytics deja existante.",
            )
        item = self.repository.create(payload.model_dump())
        return GoogleAnalyticsPropertyRead.model_validate(item)

    def update_property(
        self,
        property_pk: int,
        payload: GoogleAnalyticsPropertyUpdate,
    ) -> GoogleAnalyticsPropertyRead:
        """Update one Google Analytics property."""

        item = self._get_property_model(property_pk)
        data = payload.model_dump(exclude_unset=True)
        google_property_id = data.get("property_id")
        if google_property_id is not None:
            existing = self.repository.get_property_by_property_id(google_property_id)
            if existing is not None and existing.id != property_pk:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Propriete Google Analytics deja existante.",
                )
        updated = self.repository.update(item, data)
        return GoogleAnalyticsPropertyRead.model_validate(updated)

    def delete_property(self, property_pk: int) -> None:
        """Delete one Google Analytics property."""

        self.repository.delete_property(self._get_property_model(property_pk))

    def list_imports(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
        filters: GoogleAnalyticsImportFilters | None = None,
    ) -> GoogleAnalyticsImportList:
        """Return paginated import logs."""

        filters = self._normalize_import_filters(filters or GoogleAnalyticsImportFilters(property_id=property_id))
        items, total = self._repository_result(
            self.repository.list_imports,
            params,
            property_id=filters.property_id,
            status=filters.status.value if filters.status is not None else None,
            search=filters.search,
        )
        return GoogleAnalyticsImportList(
            items=[self._import_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_metrics(
        self,
        params: PaginationParams,
        *,
        filters: GoogleAnalyticsMetricFilters | None = None,
    ) -> GoogleAnalyticsMetricList:
        """Return paginated Google Analytics metric rows."""

        filters = self._normalize_metric_filters(filters or GoogleAnalyticsMetricFilters())
        items, total = self._repository_result(
            self.repository.list_metrics,
            params,
            **self._metric_filter_values(filters),
        )
        return GoogleAnalyticsMetricList(
            items=[GoogleAnalyticsMetricRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def overview(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsSummaryResponse:
        """Return backend-computed KPIs for Desktop overview."""

        filters = self._normalize_metric_filters(filters or GoogleAnalyticsMetricFilters())
        return GoogleAnalyticsSummaryResponse(
            generated_at=datetime.now(UTC),
            filters=self._filters_dict(filters),
            data=self._aggregate_kpis(filters),
        )

    def traffic(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsBreakdownResponse:
        """Return traffic aggregates grouped by source."""

        return self._breakdown_response("source", filters)

    def acquisition(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsBreakdownResponse:
        """Return acquisition aggregates grouped by medium."""

        return self._breakdown_response("medium", filters)

    def engagement(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsBreakdownResponse:
        """Return engagement aggregates grouped by device category."""

        return self._breakdown_response("device_category", filters)

    def conversions(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsBreakdownResponse:
        """Return conversion aggregates grouped by source."""

        return self._breakdown_response("source", filters)

    def revenue(self, filters: GoogleAnalyticsMetricFilters | None = None) -> GoogleAnalyticsBreakdownResponse:
        """Return revenue aggregates grouped by campaign."""

        return self._breakdown_response("campaign", filters)

    def history(
        self,
        params: PaginationParams,
        *,
        filters: GoogleAnalyticsImportFilters | None = None,
    ) -> GoogleAnalyticsImportHistoryList:
        """Return paginated and enriched import history."""

        filters = self._normalize_import_filters(filters or GoogleAnalyticsImportFilters())
        items, total = self._repository_result(
            self.repository.list_imports,
            params,
            property_id=filters.property_id,
            status=filters.status.value if filters.status is not None else None,
            search=filters.search,
        )
        return GoogleAnalyticsImportHistoryList(
            items=[self._import_history_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=self._filters_dict(filters),
        )

    def get_import(self, import_id: int) -> GoogleAnalyticsImportRead:
        """Return one import log."""

        item = self.repository.get_import(import_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import Google Analytics introuvable.")
        return self._import_read(item)

    def run_manual_import(self, payload: GoogleAnalyticsImportRequest) -> GoogleAnalyticsImportRead:
        """Run an idempotent manual import through the injected connector."""

        if payload.end_date < payload.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )

        property_item = self._get_property_model(payload.property_id)
        if not property_item.enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La propriete Google Analytics est desactivee.",
            )

        metrics = self._normalize_names(payload.metrics, self.METRIC_NAME_MAP, "metrique")
        dimensions = self._normalize_names(payload.dimensions, self.DIMENSION_NAME_MAP, "dimension")
        import_log = self.repository.create_import(
            {
                "property_id": property_item.id,
                "status": GoogleAnalyticsImportStatus.RUNNING,
                "imported_rows": 0,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "finished_at": None,
            },
        )

        try:
            rows = self.connector.fetch_metrics(
                property_id=property_item.property_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                metrics=metrics,
                dimensions=dimensions,
            )
            for row in rows:
                self.repository.upsert_metric(
                    {
                        "property_id": property_item.id,
                        "import_id": import_log.id,
                        "date": row.date,
                        "source": self._clean_dimension(row.source),
                        "medium": self._clean_dimension(row.medium),
                        "campaign": self._clean_dimension(row.campaign),
                        "device_category": self._clean_dimension(row.device_category),
                        "country": self._clean_dimension(row.country),
                        "users": max(row.users, 0),
                        "new_users": max(row.new_users, 0),
                        "sessions": max(row.sessions, 0),
                        "engaged_sessions": max(row.engaged_sessions, 0),
                        "screen_page_views": max(row.screen_page_views, 0),
                        "average_session_duration": max(row.average_session_duration, 0.0),
                        "engagement_rate": max(row.engagement_rate, 0.0),
                        "conversions": max(row.conversions, 0.0),
                        "total_revenue": max(row.total_revenue, 0.0),
                    },
                )
            import_log = self.repository.update_import(
                import_log,
                {
                    "status": GoogleAnalyticsImportStatus.COMPLETED,
                    "imported_rows": len(rows),
                    "finished_at": datetime.now(UTC),
                },
            )
        except Exception as exc:  # noqa: BLE001
            self.repository.update_import(
                import_log,
                {
                    "status": GoogleAnalyticsImportStatus.FAILED,
                    "error_message": str(exc),
                    "finished_at": datetime.now(UTC),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Import Google Analytics impossible.",
            ) from exc

        return self._import_read(import_log)

    def connect_oauth(self, payload: GoogleAnalyticsOAuthConnectRequest) -> GoogleAnalyticsOAuthResponse:
        """Store OAuth tokens returned by the injected connector."""

        property_item = self._get_property_model(payload.property_id)
        token_data = self.connector.connect_oauth(
            access_token=payload.access_token,
            refresh_token=payload.refresh_token,
            token_scopes=payload.token_scopes,
            token_expires_at=payload.token_expires_at,
        )
        return self._store_oauth_tokens(property_item, token_data, status_text="CONNECTED")

    def refresh_oauth(self, payload: GoogleAnalyticsOAuthRefreshRequest) -> GoogleAnalyticsOAuthResponse:
        """Refresh and store OAuth token data."""

        property_item = self._get_property_model(payload.property_id)
        if not property_item.encrypted_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Aucun refresh token Google Analytics disponible.",
            )
        token_data = self.connector.refresh_oauth(refresh_token=decrypt_secret(property_item.encrypted_refresh_token))
        return self._store_oauth_tokens(property_item, token_data, status_text="REFRESHED")

    def _store_oauth_tokens(
        self,
        property_item: GoogleAnalyticsProperty,
        token_data: GoogleAnalyticsOAuthTokenData,
        *,
        status_text: str,
    ) -> GoogleAnalyticsOAuthResponse:
        data = {
            "encrypted_access_token": encrypt_secret(token_data.access_token),
            "token_expires_at": token_data.token_expires_at,
        }
        if token_data.refresh_token is not None:
            data["encrypted_refresh_token"] = encrypt_secret(token_data.refresh_token)
        updated = self.repository.update(property_item, data)
        return GoogleAnalyticsOAuthResponse(
            property_id=updated.id,
            token_scopes=token_data.token_scopes,
            token_expires_at=updated.token_expires_at,
            status=status_text,
        )

    def _get_property_model(self, property_pk: int) -> GoogleAnalyticsProperty:
        item = self.repository.get_property(property_pk)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete Google Analytics introuvable.")
        return item

    def _normalize_names(self, names: list[str], mapping: dict[str, str], label: str) -> list[str]:
        normalized = []
        for name in names:
            key = name.strip().replace("-", "_").replace(" ", "_").lower()
            value = mapping.get(key.replace("_", ""))
            if value is None:
                value = mapping.get(key)
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"{label.capitalize()} Google Analytics non supportee: {name}.",
                )
            if value not in normalized:
                normalized.append(value)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Au moins une {label} Google Analytics est requise.",
            )
        return normalized

    def _clean_dimension(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _import_read(self, item: object) -> GoogleAnalyticsImportRead:
        read = GoogleAnalyticsImportRead.model_validate(item)
        return read.model_copy(update={"duration_seconds": self._duration_seconds(read.started_at, read.finished_at)})

    def _import_history_read(self, item: object) -> GoogleAnalyticsImportHistoryRead:
        read = GoogleAnalyticsImportHistoryRead.model_validate(item)
        property_item = getattr(item, "property", None)
        return read.model_copy(
            update={
                "duration_seconds": self._duration_seconds(read.started_at, read.finished_at),
                "property_name": getattr(property_item, "property_name", None),
                "google_property_id": getattr(property_item, "property_id", None),
            },
        )

    def _duration_seconds(self, started_at: datetime | None, finished_at: datetime | None) -> float | None:
        if started_at is None or finished_at is None:
            return None
        return max((finished_at - started_at).total_seconds(), 0.0)

    def _normalize_metric_filters(self, filters: GoogleAnalyticsMetricFilters) -> GoogleAnalyticsMetricFilters:
        if filters.date_from is not None and filters.date_to is not None and filters.date_to < filters.date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )
        return GoogleAnalyticsMetricFilters(
            website_id=filters.website_id,
            property_id=filters.property_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            import_id=filters.import_id,
            source=self._clean_dimension(filters.source),
            medium=self._clean_dimension(filters.medium),
            campaign=self._clean_dimension(filters.campaign),
            device_category=self._clean_dimension(filters.device_category),
            country=self._clean_dimension(filters.country),
            search=self._clean_dimension(filters.search),
        )

    def _normalize_import_filters(self, filters: GoogleAnalyticsImportFilters) -> GoogleAnalyticsImportFilters:
        return GoogleAnalyticsImportFilters(
            property_id=filters.property_id,
            status=filters.status,
            search=self._clean_dimension(filters.search),
        )

    def _metric_filter_values(self, filters: GoogleAnalyticsMetricFilters) -> dict[str, object]:
        return filters.model_dump(exclude_none=True)

    def _filters_dict(self, filters: GoogleAnalyticsMetricFilters | GoogleAnalyticsImportFilters) -> dict[str, object]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _repository_result(
        self,
        repository_method: Callable[..., RepositoryResult],
        *args: object,
        **kwargs: object,
    ) -> RepositoryResult:
        try:
            return repository_method(*args, **kwargs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    def _aggregate_kpis(self, filters: GoogleAnalyticsMetricFilters) -> GoogleAnalyticsKpiRead:
        raw = self.repository.aggregate_metrics(**self._metric_filter_values(filters))
        return self._kpis_from_raw(raw)

    def _kpis_from_raw(self, raw: dict[str, float | int]) -> GoogleAnalyticsKpiRead:
        sessions = int(raw["sessions"])
        return GoogleAnalyticsKpiRead(
            rows=int(raw["rows"]),
            sessions=sessions,
            users=int(raw["users"]),
            new_users=int(raw["new_users"]),
            engaged_sessions=int(raw["engaged_sessions"]),
            screen_page_views=int(raw["screen_page_views"]),
            average_session_duration=self._safe_ratio(float(raw["duration_weight"]), sessions),
            engagement_rate=self._safe_ratio(float(raw["engagement_weight"]), sessions),
            conversions=float(raw["conversions"]),
            total_revenue=float(raw["total_revenue"]),
        )

    def _breakdown_response(
        self,
        dimension: str,
        filters: GoogleAnalyticsMetricFilters | None,
    ) -> GoogleAnalyticsBreakdownResponse:
        filters = self._normalize_metric_filters(filters or GoogleAnalyticsMetricFilters())
        rows = self._repository_result(
            self.repository.aggregate_metrics_by_dimension,
            dimension,
            **self._metric_filter_values(filters),
        )
        return GoogleAnalyticsBreakdownResponse(
            generated_at=datetime.now(UTC),
            filters=self._filters_dict(filters),
            dimension=dimension,
            data=[self._breakdown_item(row) for row in rows],
        )

    def _breakdown_item(self, raw: dict[str, float | int | str | None]) -> GoogleAnalyticsBreakdownItem:
        sessions = int(raw["sessions"] or 0)
        return GoogleAnalyticsBreakdownItem(
            dimension=raw["dimension"] if isinstance(raw["dimension"], str) else None,
            rows=int(raw["rows"] or 0),
            sessions=sessions,
            users=int(raw["users"] or 0),
            new_users=int(raw["new_users"] or 0),
            engaged_sessions=int(raw["engaged_sessions"] or 0),
            screen_page_views=int(raw["screen_page_views"] or 0),
            average_session_duration=self._safe_ratio(float(raw["duration_weight"] or 0.0), sessions),
            engagement_rate=self._safe_ratio(float(raw["engagement_weight"] or 0.0), sessions),
            conversions=float(raw["conversions"] or 0.0),
            total_revenue=float(raw["total_revenue"] or 0.0),
        )

    def _safe_ratio(self, numerator: float, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return numerator / denominator
