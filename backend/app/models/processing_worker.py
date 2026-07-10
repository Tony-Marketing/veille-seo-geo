"""SQLAlchemy model for processing workers."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class ProcessingWorker(TimestampMixin, Base):
    """Heartbeat row for an orchestration worker."""

    __tablename__ = "processing_workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    worker_id: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    last_heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    current_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("processing_jobs.id", ondelete="SET NULL"),
        index=True,
    )
    version: Mapped[str | None] = mapped_column(String(80))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
    )
