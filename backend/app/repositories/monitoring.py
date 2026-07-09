"""Repository for monitoring data aggregation."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    BingWebmasterConnection,
    BingWebmasterImportRun,
    GoogleAnalyticsImport,
    GoogleAnalyticsProperty,
    GoogleSearchConsoleImport,
    GoogleSearchConsoleProperty,
    MonitoringEvent,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class MonitoringRepository(BaseRepository[MonitoringEvent]):
    """Encapsulate SQLAlchemy reads for the monitoring center."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, MonitoringEvent)

    def create_event(self, data: dict[str, Any]) -> MonitoringEvent:
        """Persist a monitoring event."""

        return self.create(data)

    def get_event(self, event_id: UUID) -> MonitoringEvent | None:
        """Return one monitoring event."""

        return self.db.get(MonitoringEvent, event_id)

    def list_events(
        self,
        params: PaginationParams,
        *,
        severity: str | None = None,
        event_type: str | None = None,
    ) -> tuple[list[MonitoringEvent], int]:
        """Return paginated monitoring events with optional filters."""

        statement = select(MonitoringEvent)
        count_statement = select(func.count()).select_from(MonitoringEvent)
        filters = self._event_filters(severity=severity, event_type=event_type)
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = statement.order_by(MonitoringEvent.created_at.desc()).offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def count_events(self, *, severity: str | None = None, created_from: datetime | None = None) -> int:
        """Return monitoring event count with optional filters."""

        statement = select(func.count()).select_from(MonitoringEvent)
        filters = []
        if severity is not None:
            filters.append(MonitoringEvent.severity == severity)
        if created_from is not None:
            filters.append(MonitoringEvent.created_at >= created_from)
        if filters:
            statement = statement.where(*filters)
        return int(self.db.scalar(statement) or 0)

    def get_last_event(self) -> MonitoringEvent | None:
        """Return the most recent monitoring event."""

        statement = select(MonitoringEvent).order_by(MonitoringEvent.created_at.desc()).limit(1)
        return self.db.scalar(statement)

    def google_search_console_stats(self) -> dict[str, Any]:
        """Return persisted Google Search Console connector indicators."""

        return {
            "total": self._count(GoogleSearchConsoleProperty),
            "enabled": self._count(GoogleSearchConsoleProperty, GoogleSearchConsoleProperty.is_active.is_(True)),
            "latest_sync": self._as_utc(
                self.db.scalar(
                    select(func.max(GoogleSearchConsoleImport.completed_at)).where(
                        GoogleSearchConsoleImport.status.in_(("COMPLETED", "PARTIAL")),
                        GoogleSearchConsoleImport.completed_at.is_not(None),
                    ),
                ),
            ),
            "errors": self._count(GoogleSearchConsoleImport, GoogleSearchConsoleImport.status == "FAILED"),
        }

    def google_analytics_stats(self) -> dict[str, Any]:
        """Return persisted Google Analytics 4 connector indicators."""

        return {
            "total": self._count(GoogleAnalyticsProperty),
            "enabled": self._count(GoogleAnalyticsProperty, GoogleAnalyticsProperty.enabled.is_(True)),
            "latest_sync": self._as_utc(
                self.db.scalar(
                    select(func.max(GoogleAnalyticsImport.finished_at)).where(
                        GoogleAnalyticsImport.status.in_(("COMPLETED", "PARTIAL")),
                        GoogleAnalyticsImport.finished_at.is_not(None),
                    ),
                ),
            ),
            "errors": self._count(GoogleAnalyticsImport, GoogleAnalyticsImport.status == "FAILED"),
        }

    def bing_webmaster_tools_stats(self) -> dict[str, Any]:
        """Return persisted Bing Webmaster Tools connector indicators."""

        latest_connection_sync = self.db.scalar(
            select(func.max(BingWebmasterConnection.last_sync_at)).where(
                BingWebmasterConnection.last_sync_at.is_not(None),
            ),
        )
        latest_import_sync = self.db.scalar(
            select(func.max(BingWebmasterImportRun.finished_at)).where(
                BingWebmasterImportRun.status.in_(("COMPLETED", "PARTIAL")),
                BingWebmasterImportRun.finished_at.is_not(None),
            ),
        )
        latest_sync_values = [value for value in (latest_connection_sync, latest_import_sync) if value is not None]
        return {
            "total": self._count(BingWebmasterConnection),
            "enabled": self._count(BingWebmasterConnection, BingWebmasterConnection.is_active.is_(True)),
            "latest_sync": self._as_utc(max(latest_sync_values)) if latest_sync_values else None,
            "errors": self._count(BingWebmasterImportRun, BingWebmasterImportRun.status == "FAILED")
            + self._count(BingWebmasterConnection, BingWebmasterConnection.last_error.is_not(None)),
        }

    def _event_filters(self, *, severity: str | None, event_type: str | None) -> list[Any]:
        filters = []
        if severity is not None:
            filters.append(MonitoringEvent.severity == severity)
        if event_type is not None:
            filters.append(MonitoringEvent.event_type == event_type)
        return filters

    def _count(self, model: type[Any], *filters: Any) -> int:
        statement = select(func.count()).select_from(model)
        if filters:
            statement = statement.where(*filters)
        return int(self.db.scalar(statement) or 0)

    def _as_utc(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
