"""Business service for the administration monitoring center."""

from collections.abc import Callable
from datetime import UTC, datetime, time
from math import ceil

from backend.app.repositories.monitoring import MonitoringRepository
from backend.app.schemas.monitoring import (
    MonitoringConnectorRead,
    MonitoringEventList,
    MonitoringEventRead,
    MonitoringEventType,
    MonitoringOverview,
    MonitoringSeverity,
    MonitoringSyncScheduleList,
    MonitoringSyncScheduleRead,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.sync_schedules import SyncScheduleFilters, SyncScheduleList, SyncScheduleRead, SyncType
from backend.app.services.sync_schedules import SyncScheduleService

NEXT_RUN_LIMIT = 5
SCHEDULE_LIST_LIMIT = 100


class MonitoringService:
    """Aggregate persisted events, connector states and synchronization schedules."""

    def __init__(
        self,
        repository: MonitoringRepository,
        sync_schedule_service: SyncScheduleService,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.sync_schedule_service = sync_schedule_service
        self.now_provider = now_provider or (lambda: datetime.now(UTC))

    def overview(self) -> MonitoringOverview:
        """Return global monitoring counters from persisted data only."""

        active_count = self._schedule_count(is_active=True)
        inactive_count = self._schedule_count(is_active=False)
        return MonitoringOverview(
            total_events=self.repository.count_events(),
            events_today=self.repository.count_events(created_from=self._today_start()),
            warning_events=self.repository.count_events(severity=MonitoringSeverity.WARNING.value),
            error_events=self.repository.count_events(severity=MonitoringSeverity.ERROR.value),
            critical_events=self.repository.count_events(severity=MonitoringSeverity.CRITICAL.value),
            active_sync_schedules=active_count,
            inactive_sync_schedules=inactive_count,
            next_runs=self._next_runs(),
            last_event=self._event_read(self.repository.get_last_event()),
        )

    def list_events(
        self,
        params: PaginationParams,
        *,
        severity: MonitoringSeverity | None = None,
        event_type: MonitoringEventType | None = None,
    ) -> MonitoringEventList:
        """Return paginated monitoring events."""

        severity_value = severity.value if severity is not None else None
        event_type_value = event_type.value if event_type is not None else None
        items, total = self.repository.list_events(params, severity=severity_value, event_type=event_type_value)
        filters = {}
        if severity_value is not None:
            filters["severity"] = severity_value
        if event_type_value is not None:
            filters["event_type"] = event_type_value
        return MonitoringEventList(
            items=[MonitoringEventRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            filters=filters,
        )

    def list_connectors(self) -> list[MonitoringConnectorRead]:
        """Return logical connector health without external API calls."""

        next_sync_by_type = self._next_sync_by_type()
        return [
            self._connector_read(
                name="Google Search Console",
                stats=self.repository.google_search_console_stats(),
                next_sync=next_sync_by_type.get(SyncType.GSC),
            ),
            self._connector_read(
                name="Google Analytics 4",
                stats=self.repository.google_analytics_stats(),
                next_sync=next_sync_by_type.get(SyncType.GA4),
            ),
            self._connector_read(
                name="Bing Webmaster Tools",
                stats=self.repository.bing_webmaster_tools_stats(),
                next_sync=next_sync_by_type.get(SyncType.BING),
            ),
        ]

    def list_sync_schedules(
        self,
        params: PaginationParams,
        *,
        filters: SyncScheduleFilters | None = None,
    ) -> MonitoringSyncScheduleList:
        """Return a read-only monitoring projection of synchronization schedules."""

        schedules = self.sync_schedule_service.list_schedules(params, filters=filters)
        return self._schedule_list_projection(schedules)

    def _schedule_count(self, *, is_active: bool) -> int:
        schedules = self.sync_schedule_service.list_schedules(
            PaginationParams(page=1, page_size=1),
            filters=SyncScheduleFilters(is_active=is_active),
        )
        return schedules.total

    def _next_runs(self) -> list[MonitoringSyncScheduleRead]:
        schedules = self.sync_schedule_service.list_schedules(
            PaginationParams(page=1, page_size=SCHEDULE_LIST_LIMIT, sort="next_run_at", order="asc"),
            filters=SyncScheduleFilters(is_active=True),
        )
        items = [item for item in schedules.items if item.next_run_at is not None]
        sorted_items = sorted(items, key=lambda item: item.next_run_at)
        return [self._schedule_projection(item) for item in sorted_items[:NEXT_RUN_LIMIT]]

    def _next_sync_by_type(self) -> dict[SyncType, datetime]:
        schedules = self.sync_schedule_service.list_schedules(
            PaginationParams(page=1, page_size=SCHEDULE_LIST_LIMIT, sort="next_run_at", order="asc"),
            filters=SyncScheduleFilters(is_active=True),
        )
        next_sync: dict[SyncType, datetime] = {}
        for item in sorted(
            (schedule for schedule in schedules.items if schedule.next_run_at is not None),
            key=lambda schedule: schedule.next_run_at,
        ):
            next_sync.setdefault(item.sync_type, item.next_run_at)
        return next_sync

    def _connector_read(
        self,
        *,
        name: str,
        stats: dict[str, object],
        next_sync: datetime | None,
    ) -> MonitoringConnectorRead:
        enabled_count = int(stats.get("enabled") or 0)
        total_count = int(stats.get("total") or 0)
        error_count = int(stats.get("errors") or 0)
        if total_count <= 0:
            status = "not_configured"
        elif enabled_count <= 0:
            status = "disabled"
        elif error_count > 0:
            status = "attention"
        else:
            status = "operational"
        latest_sync = stats.get("latest_sync")
        return MonitoringConnectorRead(
            name=name,
            status=status,
            enabled=enabled_count > 0,
            last_sync=latest_sync if isinstance(latest_sync, datetime) else None,
            next_sync=next_sync,
        )

    def _schedule_list_projection(self, schedules: SyncScheduleList) -> MonitoringSyncScheduleList:
        return MonitoringSyncScheduleList(
            items=[self._schedule_projection(item) for item in schedules.items],
            total=schedules.total,
            page=schedules.page,
            page_size=schedules.page_size,
            pages=schedules.pages,
            filters=schedules.filters,
        )

    def _schedule_projection(self, item: SyncScheduleRead) -> MonitoringSyncScheduleRead:
        return MonitoringSyncScheduleRead(
            id=item.id,
            name=item.name,
            sync_type=item.sync_type,
            frequency=item.frequency,
            status=item.status,
            is_active=item.is_active,
            last_run_at=item.last_run_at,
            last_run_status=item.last_run_status,
            last_run_message=item.last_run_message,
            next_run_at=item.next_run_at,
        )

    def _event_read(self, item: object | None) -> MonitoringEventRead | None:
        return MonitoringEventRead.model_validate(item) if item is not None else None

    def _today_start(self) -> datetime:
        now = self.now_provider()
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        return datetime.combine(now.date(), time.min, tzinfo=now.tzinfo)
