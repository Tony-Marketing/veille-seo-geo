"""SQLAlchemy models for Google Search Console data."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class GscOAuthCredential(TimestampMixin, Base):
    """Persisted OAuth credential metadata and encrypted tokens for GSC."""

    __tablename__ = "gsc_oauth_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(40), default="google", index=True, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)


class GscProperty(TimestampMixin, Base):
    """Google Search Console property tracked by the application."""

    __tablename__ = "gsc_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    site_url: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    property_type: Mapped[str] = mapped_column(String(30), default="url_prefix", index=True, nullable=False)
    permission_level: Mapped[str | None] = mapped_column(String(80))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    import_runs: Mapped[list["GscImportRun"]] = relationship(back_populates="property")


class GscImportRun(TimestampMixin, Base):
    """One GSC import execution."""

    __tablename__ = "gsc_import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    import_type: Mapped[str] = mapped_column(String(40), default="full", index=True, nullable=False)
    date_start: Mapped[date | None] = mapped_column(Date)
    date_end: Mapped[date | None] = mapped_column(Date)
    rows_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    property: Mapped[GscProperty] = relationship(back_populates="import_runs")


class GscPerformanceDaily(TimestampMixin, Base):
    """Daily GSC performance row with dimensions."""

    __tablename__ = "gsc_performance_daily"
    __table_args__ = (
        UniqueConstraint(
            "property_id",
            "date",
            "page",
            "query",
            "device",
            "country",
            "search_type",
            name="uq_gsc_performance_dimensions",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    import_run_id: Mapped[int | None] = mapped_column(ForeignKey("gsc_import_runs.id", ondelete="SET NULL"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    page: Mapped[str] = mapped_column(String(1000), default="", index=True, nullable=False)
    query: Mapped[str] = mapped_column(String(500), default="", index=True, nullable=False)
    device: Mapped[str] = mapped_column(String(40), default="", index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(10), default="", index=True, nullable=False)
    search_type: Mapped[str] = mapped_column(String(40), default="web", index=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ctr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class GscCoverageSnapshot(TimestampMixin, Base):
    """Aggregated coverage/indexing snapshot from GSC."""

    __tablename__ = "gsc_coverage_snapshots"
    __table_args__ = (
        UniqueConstraint("property_id", "date", "category", "state", name="uq_gsc_coverage_snapshot"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    import_run_id: Mapped[int | None] = mapped_column(ForeignKey("gsc_import_runs.id", ondelete="SET NULL"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    pages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class GscIndexingInspection(TimestampMixin, Base):
    """URL indexing inspection result."""

    __tablename__ = "gsc_indexing_inspections"
    __table_args__ = (
        UniqueConstraint("property_id", "inspected_url", "inspected_at", name="uq_gsc_indexing_inspection"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    import_run_id: Mapped[int | None] = mapped_column(ForeignKey("gsc_import_runs.id", ondelete="SET NULL"), index=True)
    inspected_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    coverage_state: Mapped[str | None] = mapped_column(String(120), index=True)
    indexing_state: Mapped[str | None] = mapped_column(String(120), index=True)
    verdict: Mapped[str | None] = mapped_column(String(80), index=True)
    robots_txt_state: Mapped[str | None] = mapped_column(String(120))
    page_fetch_state: Mapped[str | None] = mapped_column(String(120))
    google_canonical: Mapped[str | None] = mapped_column(String(1000))
    user_canonical: Mapped[str | None] = mapped_column(String(1000))
    last_crawl_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)


class GscSitemap(TimestampMixin, Base):
    """Sitemap known by Google Search Console."""

    __tablename__ = "gsc_sitemaps"
    __table_args__ = (UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    import_run_id: Mapped[int | None] = mapped_column(ForeignKey("gsc_import_runs.id", ondelete="SET NULL"), index=True)
    sitemap_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    path: Mapped[str | None] = mapped_column(String(1000))
    last_submitted: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_downloaded: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_sitemaps_index: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sitemap_type: Mapped[str | None] = mapped_column(String(80))
    errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warnings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contents: Mapped[dict[str, Any] | None] = mapped_column(JSON)
