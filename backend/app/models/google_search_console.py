"""SQLAlchemy models for Google Search Console data."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class GoogleSearchConsoleProperty(TimestampMixin, Base):
    """Google Search Console property linked to a tracked website."""

    __tablename__ = "google_search_console_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    google_property_id: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    property_url: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    property_type: Mapped[str] = mapped_column(String(30), default="URL_PREFIX", index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    permission_level: Mapped[str | None] = mapped_column(String(80), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text)
    token_scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

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

    __tablename__ = "google_search_console_performances"
    __table_args__ = (
        UniqueConstraint(
            "property_id",
            "date",
            "query",
            "page",
            "country",
            "device",
            "search_type",
            name="uq_gsc_performances_dimensions",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_search_console_properties.id", ondelete="CASCADE"),
        index=True,
    )
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("google_search_console_imports.id", ondelete="SET NULL"),
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    query: Mapped[str | None] = mapped_column(String(1000), index=True)
    page: Mapped[str | None] = mapped_column(String(1000), index=True)
    country: Mapped[str | None] = mapped_column(String(10), index=True)
    device: Mapped[str | None] = mapped_column(String(40), index=True)
    search_type: Mapped[str] = mapped_column(String(40), default="web", index=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ctr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    position: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="performances")
    import_run: Mapped["GoogleSearchConsoleImport | None"] = relationship(back_populates="performances")


class GoogleSearchConsoleIndexCoverage(TimestampMixin, Base):
    """Index coverage status imported from Google Search Console."""

    __tablename__ = "google_search_console_index_coverages"
    __table_args__ = (
        UniqueConstraint("property_id", "url", name="uq_gsc_index_coverages_property_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_search_console_properties.id", ondelete="CASCADE"),
        index=True,
    )
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("google_search_console_imports.id", ondelete="SET NULL"),
        index=True,
    )
    url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    coverage_state: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    google_state: Mapped[str | None] = mapped_column(String(120), index=True)
    indexing_state: Mapped[str | None] = mapped_column(String(120), index=True)
    page_fetch_state: Mapped[str | None] = mapped_column(String(120))
    robots_txt_state: Mapped[str | None] = mapped_column(String(120))
    verdict: Mapped[str | None] = mapped_column(String(80), index=True)
    issue_type: Mapped[str | None] = mapped_column(String(255), index=True)
    sitemap: Mapped[str | None] = mapped_column(String(1000))
    referring_urls: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="index_coverages")
    import_run: Mapped["GoogleSearchConsoleImport | None"] = relationship(back_populates="index_coverages")


class GoogleSearchConsoleSitemap(TimestampMixin, Base):
    """Sitemap metadata imported from Google Search Console."""

    __tablename__ = "google_search_console_sitemaps"
    __table_args__ = (
        UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_search_console_properties.id", ondelete="CASCADE"),
        index=True,
    )
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("google_search_console_imports.id", ondelete="SET NULL"),
        index=True,
    )
    sitemap_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    sitemap_type: Mapped[str | None] = mapped_column(String(80), index=True)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_sitemaps_index: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    warnings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contents: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="sitemaps")
    import_run: Mapped["GoogleSearchConsoleImport | None"] = relationship(back_populates="sitemaps")


class GoogleSearchConsoleImport(TimestampMixin, Base):
    """Google Search Console import execution log."""

    __tablename__ = "google_search_console_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_search_console_properties.id", ondelete="CASCADE"),
        index=True,
    )
    import_type: Mapped[str] = mapped_column(String(50), default="MANUAL", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, index=True)
    end_date: Mapped[date | None] = mapped_column(Date, index=True)
    dimensions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    rows_requested: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rows_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    property: Mapped[GoogleSearchConsoleProperty] = relationship(back_populates="imports")
    performances: Mapped[list[GoogleSearchConsolePerformance]] = relationship(back_populates="import_run")
    index_coverages: Mapped[list[GoogleSearchConsoleIndexCoverage]] = relationship(back_populates="import_run")
    sitemaps: Mapped[list[GoogleSearchConsoleSitemap]] = relationship(back_populates="import_run")
