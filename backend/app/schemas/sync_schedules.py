"""Pydantic schemas for synchronization schedules."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class SyncType(StrEnum):
    """Supported synchronization types."""

    GSC = "GSC"
    GA4 = "GA4"
    BING = "Bing"
    CRAWL = "Crawl"
    SEO = "SEO"
    GEO = "GEO"


class SyncFrequency(StrEnum):
    """Supported schedule frequencies."""

    MANUAL = "Manuel"
    HOURLY = "Horaire"
    DAILY = "Quotidien"
    WEEKLY = "Hebdomadaire"
    MONTHLY = "Mensuel"


class SyncScheduleStatus(StrEnum):
    """Functional schedule statuses."""

    ACTIVE = "Active"
    DISABLED = "Desactivee"
    PENDING = "En attente"
    ERROR = "Erreur"


class SyncScheduleCreate(BaseModel):
    """Payload used to create a synchronization schedule."""

    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    sync_type: SyncType
    frequency: SyncFrequency
    is_active: bool = True
    website_id: int | None = Field(default=None, gt=0)
    target_id: str | None = Field(default=None, max_length=120)
    target_type: str | None = Field(default=None, max_length=80)
    timezone: str = Field(default="Europe/Paris", min_length=1, max_length=80)


class SyncScheduleUpdate(BaseModel):
    """Payload used to update a synchronization schedule."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    sync_type: SyncType | None = None
    frequency: SyncFrequency | None = None
    status: SyncScheduleStatus | None = None
    is_active: bool | None = None
    website_id: int | None = Field(default=None, gt=0)
    target_id: str | None = Field(default=None, max_length=120)
    target_type: str | None = Field(default=None, max_length=80)
    last_run_at: datetime | None = None
    last_run_status: SyncScheduleStatus | None = None
    last_run_message: str | None = Field(default=None, max_length=2000)
    timezone: str | None = Field(default=None, min_length=1, max_length=80)


class SyncScheduleFilters(BaseModel):
    """REST filters supported by synchronization schedule endpoints."""

    sync_type: SyncType | None = None
    frequency: SyncFrequency | None = None
    status: SyncScheduleStatus | None = None
    is_active: bool | None = None
    website_id: int | None = Field(default=None, gt=0)
    next_run_from: datetime | None = None
    next_run_to: datetime | None = None
    search: str | None = Field(default=None, max_length=255)


class SyncScheduleRead(TimestampRead):
    """Synchronization schedule returned by the API."""

    id: int
    name: str
    description: str | None
    sync_type: SyncType
    frequency: SyncFrequency
    status: SyncScheduleStatus
    is_active: bool
    website_id: int | None
    target_id: str | None
    target_type: str | None
    last_run_at: datetime | None
    last_run_status: SyncScheduleStatus | None
    last_run_message: str | None
    next_run_at: datetime | None
    timezone: str
    created_by_user_id: int | None
    updated_by_user_id: int | None


class SyncScheduleList(PaginatedResponse[SyncScheduleRead]):
    """Paginated synchronization schedules with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)

