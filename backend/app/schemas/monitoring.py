"""Pydantic schemas for administration monitoring."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import OrmModel
from backend.app.schemas.pagination import PaginatedResponse
from backend.app.schemas.sync_schedules import SyncFrequency, SyncScheduleStatus, SyncType


class MonitoringEventType(StrEnum):
    """Supported monitoring event categories."""

    SYNC = "sync"
    CONNECTOR = "connector"
    SYSTEM = "system"
    AUTH = "auth"
    IMPORT = "import"
    EXPORT = "export"


class MonitoringSeverity(StrEnum):
    """Supported monitoring severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringEventRead(OrmModel):
    """Monitoring event returned by the API."""

    id: UUID
    event_type: MonitoringEventType
    severity: MonitoringSeverity
    source: str
    message: str
    details: dict[str, Any] | None = None
    created_at: datetime


class MonitoringEventList(PaginatedResponse[MonitoringEventRead]):
    """Paginated monitoring events."""

    filters: dict[str, Any] = Field(default_factory=dict)


class MonitoringSyncScheduleRead(BaseModel):
    """Synchronization schedule projection used by monitoring."""

    id: int
    name: str
    sync_type: SyncType
    frequency: SyncFrequency
    status: SyncScheduleStatus
    is_active: bool
    last_run_at: datetime | None = None
    last_run_status: SyncScheduleStatus | None = None
    last_run_message: str | None = None
    next_run_at: datetime | None = None


class MonitoringSyncScheduleList(PaginatedResponse[MonitoringSyncScheduleRead]):
    """Paginated synchronization schedules as seen by monitoring."""

    filters: dict[str, Any] = Field(default_factory=dict)


class MonitoringConnectorRead(BaseModel):
    """Logical connector health displayed by monitoring."""

    name: str
    status: str
    enabled: bool
    last_sync: datetime | None = None
    next_sync: datetime | None = None


class MonitoringOverview(BaseModel):
    """Global monitoring overview."""

    total_events: int = 0
    events_today: int = 0
    warning_events: int = 0
    error_events: int = 0
    critical_events: int = 0
    active_sync_schedules: int = 0
    inactive_sync_schedules: int = 0
    next_runs: list[MonitoringSyncScheduleRead] = Field(default_factory=list)
    last_event: MonitoringEventRead | None = None
