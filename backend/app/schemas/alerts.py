"""Pydantic schemas for the alerts center."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class AlertSeverity(StrEnum):
    """Supported alert severity levels."""

    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertStatus(StrEnum):
    """Supported alert lifecycle states."""

    ACTIVE = "Active"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"


class AlertCategory(StrEnum):
    """Supported alert categories generated from monitoring data."""

    SYNC = "sync"
    CONNECTOR = "connector"
    SYSTEM = "system"
    AUTH = "auth"
    IMPORT = "import"
    EXPORT = "export"
    SEO = "seo"
    GEO = "geo"
    CRAWL = "crawl"


class AlertFilters(BaseModel):
    """REST filters supported by alert endpoints."""

    status: AlertStatus | None = None
    severity: AlertSeverity | None = None
    category: str | None = Field(default=None, max_length=80)
    source_type: str | None = Field(default=None, max_length=80)
    search: str | None = Field(default=None, max_length=255)


class AlertRead(TimestampRead):
    """Alert returned by the API."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    source_type: str
    source_id: str | None = None
    category: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")
    deduplication_key: str
    first_seen_at: datetime
    last_seen_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by_user_id: int | None = None
    resolved_at: datetime | None = None


class AlertList(PaginatedResponse[AlertRead]):
    """Paginated alerts with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class AlertSummary(BaseModel):
    """Aggregated alert counters."""

    total: int = 0
    active: int = 0
    acknowledged: int = 0
    resolved: int = 0
    info: int = 0
    warning: int = 0
    critical: int = 0
    last_alert_at: datetime | None = None


class AlertRefreshResult(BaseModel):
    """Result returned after generating alerts from monitoring data."""

    created: int = 0
    updated: int = 0
    total_processed: int = 0
    alerts: list[AlertRead] = Field(default_factory=list)
