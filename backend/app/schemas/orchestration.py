"""Pydantic schemas for processing orchestration."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.common import OrmModel, TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class ProcessingJobStatus(StrEnum):
    """Known lifecycle states for processing jobs."""

    PENDING = "pending"
    RESERVED = "reserved"
    RUNNING = "running"
    RETRY_SCHEDULED = "retry_scheduled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingJobType(StrEnum):
    """Supported processing job types."""

    GSC = "gsc"
    GA4 = "ga4"
    BING = "bing"
    CRAWL = "crawl"
    SEO_ANALYSIS = "seo_analysis"
    GEO_ANALYSIS = "geo_analysis"


class ProcessingLogLevel(StrEnum):
    """Supported processing log levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProcessingWorkerStatus(StrEnum):
    """Supported worker heartbeat states."""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"


class ProcessingJobFilters(BaseModel):
    """REST filters supported by orchestration job endpoints."""

    status: ProcessingJobStatus | None = None
    job_type: ProcessingJobType | None = None
    schedule_id: int | None = Field(default=None, gt=0)
    created_from: datetime | None = None
    created_to: datetime | None = None
    search: str | None = Field(default=None, max_length=255)


class ProcessingJobRead(TimestampRead):
    """Processing job returned by the API."""

    id: int
    schedule_id: int | None
    job_type: ProcessingJobType
    status: ProcessingJobStatus
    priority: int
    payload: dict[str, Any] | None
    idempotency_key: str | None
    attempts: int
    max_attempts: int
    available_at: datetime
    reserved_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    failed_at: datetime | None
    message: str | None
    details: dict[str, Any] | None
    worker_id: str | None
    lock_expires_at: datetime | None
    monitoring_event_id: UUID | None


class ProcessingJobList(PaginatedResponse[ProcessingJobRead]):
    """Paginated processing jobs with applied filters."""

    filters: dict[str, Any] = Field(default_factory=dict)


class ProcessingJobLogRead(OrmModel):
    """Processing job log returned by the API."""

    id: int
    job_id: int
    level: ProcessingLogLevel
    event: str
    message: str
    context: dict[str, Any] | None
    created_at: datetime


class ProcessingJobLogList(PaginatedResponse[ProcessingJobLogRead]):
    """Paginated logs for one processing job."""

    filters: dict[str, Any] = Field(default_factory=dict)


class ProcessingWorkerRead(TimestampRead):
    """Processing worker heartbeat returned by the API."""

    id: int
    worker_id: str
    status: ProcessingWorkerStatus
    last_heartbeat_at: datetime
    current_job_id: int | None
    version: str | None
    metadata_: dict[str, Any] | None = Field(default=None, serialization_alias="metadata")


class ProcessingSummary(BaseModel):
    """Global orchestration counters."""

    pending: int = 0
    reserved: int = 0
    running: int = 0
    retry_scheduled: int = 0
    succeeded: int = 0
    failed: int = 0
    cancelled: int = 0
    blocked: int = 0
    total: int = 0
    last_activity_at: datetime | None = None
    active_workers: int = 0


class SchedulerRunResult(BaseModel):
    """Result returned after one scheduler cycle."""

    scanned: int = 0
    created: int = 0
    skipped: int = 0
    errors: int = 0
    jobs: list[ProcessingJobRead] = Field(default_factory=list)

