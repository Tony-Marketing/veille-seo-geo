"""SQLAlchemy model for synchronization schedules."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class SyncSchedule(TimestampMixin, Base):
    """Synchronization schedule configured by administrators."""

    __tablename__ = "sync_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sync_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    frequency: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    target_id: Mapped[str | None] = mapped_column(String(120), index=True)
    target_type: Mapped[str | None] = mapped_column(String(80), index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_run_status: Mapped[str | None] = mapped_column(String(30), index=True)
    last_run_message: Mapped[str | None] = mapped_column(Text)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    timezone: Mapped[str] = mapped_column(String(80), default="Europe/Paris", nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

