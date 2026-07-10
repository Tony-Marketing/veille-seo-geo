"""SQLAlchemy model for processing jobs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.processing_job_log import ProcessingJobLog


class ProcessingJob(TimestampMixin, Base):
    """Persistent processing job used by the orchestration queue."""

    __tablename__ = "processing_jobs"
    __table_args__ = (
        Index("ix_processing_jobs_status_available_at", "status", "available_at"),
        Index("ix_processing_jobs_job_type_status", "job_type", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int | None] = mapped_column(ForeignKey("sync_schedules.id", ondelete="SET NULL"), index=True)
    job_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    message: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB(), "postgresql"))
    worker_id: Mapped[str | None] = mapped_column(String(120), index=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    monitoring_event_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("monitoring_events.id", ondelete="SET NULL"),
        index=True,
    )

    logs: Mapped[list[ProcessingJobLog]] = relationship(
        "ProcessingJobLog",
        back_populates="job",
        cascade="all, delete-orphan",
    )
