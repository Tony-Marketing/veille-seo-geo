"""SQLAlchemy model for transverse SEO/GEO recommendations."""

from typing import Any

from sqlalchemy import JSON, CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin
from backend.app.models.entities import Website


class Recommendation(TimestampMixin, Base):
    """Persisted recommendation consolidated from an existing project source."""

    __tablename__ = "recommendations"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')",
            name="ck_recommendations_priority",
        ),
        CheckConstraint(
            "status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'IGNORED')",
            name="ck_recommendations_status",
        ),
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('EASY', 'MEDIUM', 'HARD')",
            name="ck_recommendations_difficulty",
        ),
        Index("uq_recommendations_deduplication_key", "deduplication_key", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(
        ForeignKey("websites.id", ondelete="SET NULL"),
        index=True,
    )
    source: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    source_id: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    impact: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(20), index=True)
    score: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", index=True, nullable=False)
    deduplication_key: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
    )

    website: Mapped["Website | None"] = relationship()
