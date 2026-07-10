"""SQLAlchemy model for administration alerts."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class Alert(TimestampMixin, Base):
    """Consultative alert generated from persisted monitoring data."""

    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("severity IN ('Info', 'Warning', 'Critical')", name="ck_alerts_severity"),
        CheckConstraint("status IN ('Active', 'Acknowledged', 'Resolved')", name="ck_alerts_status"),
        Index(
            "uq_alerts_active_deduplication_key",
            "deduplication_key",
            unique=True,
            postgresql_where=text("status IN ('Active', 'Acknowledged')"),
            sqlite_where=text("status IN ('Active', 'Acknowledged')"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
    )
    deduplication_key: Mapped[str] = mapped_column(String(255), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
