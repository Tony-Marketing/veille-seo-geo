"""SQLAlchemy model for multi-provider GEO visibility snapshots."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin
from backend.app.models.entities import Website


class GeoVisibilitySnapshot(TimestampMixin, Base):
    """Persist one normalized and traceable GEO visibility observation."""

    __tablename__ = "geo_visibility_snapshots"
    __table_args__ = (
        CheckConstraint(
            "visibility_score >= 0 AND visibility_score <= 100",
            name="ck_geo_visibility_snapshots_score",
        ),
        CheckConstraint("citation_count >= 0", name="ck_geo_visibility_snapshots_citations"),
        CheckConstraint("source_count >= 0", name="ck_geo_visibility_snapshots_sources"),
        CheckConstraint("ranking IS NULL OR ranking > 0", name="ck_geo_visibility_snapshots_ranking"),
        UniqueConstraint(
            "website_id",
            "provider",
            "prompt",
            "entity",
            "answer_hash",
            "captured_at",
            name="uq_geo_visibility_snapshots_observation",
        ),
        Index("ix_geo_visibility_snapshots_scope", "website_id", "provider", "entity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int] = mapped_column(
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    visibility_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ranking: Mapped[int | None] = mapped_column(Integer)
    answer_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    website: Mapped[Website] = relationship()
