"""SQLAlchemy models for crawl sessions and pages."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class CrawlSession(TimestampMixin, Base):
    """Persisted crawl execution session."""

    __tablename__ = "crawl_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    start_url: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_start_url: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    max_depth: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    max_pages: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    pages_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_crawled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pending_urls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_depth_reached: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_progress_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pages: Mapped[list["CrawlPage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class CrawlPage(TimestampMixin, Base):
    """Persisted page discovered during a crawl session."""

    __tablename__ = "crawl_pages"
    __table_args__ = (
        UniqueConstraint("crawl_session_id", "normalized_url", name="uq_crawl_pages_session_normalized_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crawl_session_id: Mapped[int] = mapped_column(ForeignKey("crawl_sessions.id", ondelete="CASCADE"), index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    normalized_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    final_url: Mapped[str | None] = mapped_column(String(1000))
    final_normalized_url: Mapped[str | None] = mapped_column(String(1000), index=True)
    depth: Mapped[int] = mapped_column(Integer, default=0, index=True, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, index=True)
    content_type: Mapped[str | None] = mapped_column(String(255))
    raw_html: Mapped[str | None] = mapped_column(Text)
    is_redirect: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    redirect_url: Mapped[str | None] = mapped_column(String(1000))
    redirect_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    visited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    session: Mapped[CrawlSession] = relationship(back_populates="pages")

