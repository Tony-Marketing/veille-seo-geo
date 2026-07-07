"""SQLAlchemy models for Google Search Console data."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class GoogleSearchConsoleProperty(TimestampMixin, Base):
    """Google Search Console property attached to an optional tracked website."""

    __tablename__ = "gsc_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    site_url: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    property_type: Mapped[str] = mapped_column(String(40), default="URL_PREFIX", index=True, nullable=False)
    permission_level: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", index=True, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    performances: Mapped[list["GoogleSearchConsolePerformance"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    index_coverages: Mapped[list["GoogleSearchConsoleIndexCoverage"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    sitemaps: Mapped[list["GoogleSearchConsoleSitemap"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    imports: Mapped[list["GoogleSearchConsoleImport"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )


class GoogleSearchConsolePerformance(TimestampMixin, Base):
    """Search performance metrics imported from Google Search Console."""

    __tablename__ = "gsc_performances"
    __table_args__ = (
        UniqueConstraint(
            "property_id",
            "date",
            "page",
            "query",
            "country",
            "device",
            name="uq_gsc_performances_dimensions",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    page: Mapped[str | None] = mapped_column(String(1000), index=True)
    query: Mapped[str | None] = mapped_column(String(500), index=True)
    country: Mapped[str | None] = mapped_column(String(10), index=True)
    device: Mapped[str | None] = mapped_column(String(30), index=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ctr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="performances")


class GoogleSearchConsoleIndexCoverage(TimestampMixin, Base):
    """Index coverage state for one URL."""

    __tablename__ = "gsc_index_coverages"
    __table_args__ = (
        UniqueConstraint("property_id", "url", name="uq_gsc_index_coverages_property_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    coverage_state: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    indexing_state: Mapped[str | None] = mapped_column(String(120), index=True)
    verdict: Mapped[str | None] = mapped_column(String(80), index=True)
    page_fetch_state: Mapped[str | None] = mapped_column(String(120))
    google_canonical: Mapped[str | None] = mapped_column(String(1000))
    user_canonical: Mapped[str | None] = mapped_column(String(1000))
    last_crawl_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    inspected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="index_coverages")


class GoogleSearchConsoleSitemap(TimestampMixin, Base):
    """Sitemap known for a Google Search Console property."""

    __tablename__ = "gsc_sitemaps"
    __table_args__ = (
        UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("gsc_properties.id", ondelete="CASCADE"), index=True)
    sitemap_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    status: Mapped[str | None] = mapped_column(String(80), index=True)
    last_submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    warnings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contents: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="sitemaps")


class GoogleSearchConsoleImport(TimestampMixin, Base):
    """Import execution history for Google Search Console data."""

    __tablename__ = "gsc_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int | None] = mapped_column(ForeignKey("gsc_properties.id", ondelete="SET NULL"), index=True)
    import_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    items_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    import_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    property: Mapped[GoogleSearchConsoleProperty | None] = relationship(back_populates="imports")
