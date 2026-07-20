"""Business service for the alerts center."""

from collections.abc import Callable
from datetime import UTC, datetime
from math import ceil
from typing import Any

from fastapi import HTTPException, status

from backend.app.models import Alert, MonitoringEvent
from backend.app.repositories.alerts import AlertRepository
from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.schemas.alerts import (
    AlertFilters,
    AlertList,
    AlertRead,
    AlertRefreshResult,
    AlertSeverity,
    AlertStatus,
    AlertSummary,
)
from backend.app.schemas.monitoring import MonitoringSeverity
from backend.app.schemas.pagination import PaginationParams

MONITORING_REFRESH_LIMIT = 100


class AlertService:
    """Manage alert generation, lifecycle transitions and aggregated counters."""

    def __init__(
        self,
        repository: AlertRepository,
        monitoring_repository: MonitoringRepository,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.monitoring_repository = monitoring_repository
        self.now_provider = now_provider or (lambda: datetime.now(UTC))

    def list_alerts(self, params: PaginationParams, *, filters: AlertFilters | None = None) -> AlertList:
        """Return paginated alerts."""

        filters = self._normalize_filters(filters or AlertFilters())
        values = self._filters_dict(filters)
        items, total = self._repository_result(self.repository.list_alerts, params, **values)
        return AlertList(
            items=[AlertRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=values,
        )

    def get_alert(self, alert_id: int) -> AlertRead:
        """Return one alert."""

        return AlertRead.model_validate(self._get_alert_model(alert_id))

    def refresh_from_monitoring(self) -> AlertRefreshResult:
        """Generate or update alerts from persisted monitoring events only."""

        events, _total = self.monitoring_repository.list_events(
            PaginationParams(page=1, page_size=MONITORING_REFRESH_LIMIT),
        )
        created = 0
        updated = 0
        refreshed_alerts: list[Alert] = []
        for event in events:
            alert, was_created = self._upsert_from_monitoring_event(event)
            refreshed_alerts.append(alert)
            if was_created:
                created += 1
            else:
                updated += 1
        return AlertRefreshResult(
            created=created,
            updated=updated,
            total_processed=len(events),
            alerts=[AlertRead.model_validate(item) for item in refreshed_alerts],
        )

    def acknowledge_alert(self, alert_id: int, *, user_id: int | None = None) -> AlertRead:
        """Mark an alert as acknowledged."""

        item = self._get_alert_model(alert_id)
        if item.status == AlertStatus.RESOLVED.value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Une alerte resolue ne peut pas etre acquittee.",
            )
        updated = self.repository.update_alert(
            item,
            {
                "status": AlertStatus.ACKNOWLEDGED.value,
                "acknowledged_at": self._now(),
                "acknowledged_by_user_id": user_id,
            },
        )
        return AlertRead.model_validate(updated)

    def resolve_alert(self, alert_id: int) -> AlertRead:
        """Mark an alert as resolved without deleting it."""

        item = self._get_alert_model(alert_id)
        if item.status == AlertStatus.RESOLVED.value:
            return AlertRead.model_validate(item)
        updated = self.repository.update_alert(
            item,
            {
                "status": AlertStatus.RESOLVED.value,
                "resolved_at": self._now(),
            },
        )
        return AlertRead.model_validate(updated)

    def summary(self) -> AlertSummary:
        """Return aggregated alert counters."""

        return AlertSummary(
            total=self.repository.count_alerts(),
            active=self.repository.count_alerts(status=AlertStatus.ACTIVE.value),
            acknowledged=self.repository.count_alerts(status=AlertStatus.ACKNOWLEDGED.value),
            resolved=self.repository.count_alerts(status=AlertStatus.RESOLVED.value),
            info=self.repository.count_alerts(severity=AlertSeverity.INFO.value),
            warning=self.repository.count_alerts(severity=AlertSeverity.WARNING.value),
            critical=self.repository.count_alerts(severity=AlertSeverity.CRITICAL.value),
            last_alert_at=self.repository.get_last_alert_seen_at(),
        )

    def _upsert_from_monitoring_event(self, event: MonitoringEvent) -> tuple[Alert, bool]:
        data = self._alert_data_from_monitoring_event(event)
        existing = self.repository.get_active_by_deduplication_key(str(data["deduplication_key"]))
        if existing is None:
            legacy_key = self._legacy_deduplication_key(event)
            if legacy_key != data["deduplication_key"]:
                existing = self.repository.get_active_by_deduplication_key(legacy_key)
        if existing is None:
            return self.repository.create_alert(data), True

        updated = self.repository.update_alert(
            existing,
            {
                "severity": data["severity"],
                "title": data["title"],
                "message": data["message"],
                "metadata_": data["metadata_"],
                "deduplication_key": data["deduplication_key"],
                "last_seen_at": data["last_seen_at"],
            },
        )
        return updated, False

    def _alert_data_from_monitoring_event(self, event: MonitoringEvent) -> dict[str, Any]:
        category = self._clean_text(event.event_type) or "system"
        source_type = self._clean_text(event.source) or "monitoring"
        observed_at = self._as_aware(event.created_at)
        severity = self._alert_severity(event.severity)
        return {
            "source_type": source_type,
            "source_id": str(event.id),
            "category": category,
            "severity": severity.value,
            "status": AlertStatus.ACTIVE.value,
            "title": self._title(source_type=source_type, category=category, severity=severity),
            "message": self._clean_text(event.message) or "Alerte issue du monitoring.",
            "metadata_": self._safe_metadata(event.details),
            "deduplication_key": self._deduplication_key(event),
            "first_seen_at": observed_at,
            "last_seen_at": observed_at,
        }

    def _alert_severity(self, value: str) -> AlertSeverity:
        if value == MonitoringSeverity.CRITICAL.value or value == MonitoringSeverity.ERROR.value:
            return AlertSeverity.CRITICAL
        if value == MonitoringSeverity.WARNING.value:
            return AlertSeverity.WARNING
        return AlertSeverity.INFO

    def _deduplication_key(self, event: MonitoringEvent) -> str:
        details = event.details if isinstance(event.details, dict) else {}
        website_id = details.get("website_id")
        parts = [
            "monitoring",
            f"website:{website_id}" if isinstance(website_id, int) else "website:global",
            self._clean_text(event.event_type) or "system",
            self._clean_text(event.source) or "unknown",
            self._clean_text(event.message) or "event",
        ]
        return ":".join(parts)[:255]

    def _legacy_deduplication_key(self, event: MonitoringEvent) -> str:
        parts = [
            "monitoring",
            self._clean_text(event.event_type) or "system",
            self._clean_text(event.source) or "unknown",
            self._clean_text(event.message) or "event",
        ]
        return ":".join(parts)[:255]

    def _title(self, *, source_type: str, category: str, severity: AlertSeverity) -> str:
        return f"{severity.value} - {source_type} - {category}"[:180]

    def _safe_metadata(self, details: dict[str, Any] | None) -> dict[str, Any] | None:
        if not details:
            return None
        blocked_fragments = ("password", "token", "secret", "authorization", "api_key", "apikey")
        return {
            str(key): value
            for key, value in details.items()
            if not any(fragment in str(key).lower() for fragment in blocked_fragments)
        }

    def _get_alert_model(self, alert_id: int) -> Alert:
        item = self.repository.get_alert(alert_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte introuvable.")
        return item

    def _normalize_filters(self, filters: AlertFilters) -> AlertFilters:
        return AlertFilters(
            status=filters.status,
            severity=filters.severity,
            category=self._clean_text(filters.category),
            source_type=self._clean_text(filters.source_type),
            search=self._clean_text(filters.search),
        )

    def _filters_dict(self, filters: AlertFilters) -> dict[str, object]:
        return filters.model_dump(mode="json", exclude_none=True)

    def _repository_result(
        self,
        repository_method: Callable[..., Any],
        *args: object,
        **kwargs: object,
    ) -> Any:
        try:
            return repository_method(*args, **kwargs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _now(self) -> datetime:
        return self._as_aware(self.now_provider())

    def _as_aware(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
