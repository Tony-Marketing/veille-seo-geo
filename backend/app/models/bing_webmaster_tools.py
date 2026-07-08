"""SQLAlchemy models for Bing Webmaster Tools data."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class BingWebmasterConnection(TimestampMixin, Base):
    """Bing Webmaster Tools connection linked to a tracked website."""

    __tablename__ = "bing_webmaster_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    auth_type: Mapped[str] = mapped_column(String(30), default="API_KEY", index=True, nullable=False)
    client_id: Mapped[str | None] = mapped_column(String(255), index=True)
    client_secret_encrypted: Mapped[str | None] = mapped_column(Text)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)

    sites: Mapped[list["BingWebmasterSite"]] = relationship(
        back_populates="connection",
        cascade="all, delete-orphan",
    )
    import_runs: Mapped[list["BingWebmasterImportRun"]] = relationship(
        back_populates="connection",
        cascade="all, delete-orphan",
    )


class BingWebmasterSite(TimestampMixin, Base):
    """Bing Webmaster Tools site attached to one connection."""

    __tablename__ = "bing_webmaster_sites"
    __table_args__ = (UniqueConstraint("connection_id", "site_url", name="uq_bing_sites_connection_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("bing_webmaster_connections.id", ondelete="CASCADE"),
        index=True,
    )
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    site_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    last_import_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    connection: Mapped[BingWebmasterConnection] = relationship(back_populates="sites")
    metrics: Mapped[list["BingWebmasterMetric"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    crawl_stats: Mapped[list["BingWebmasterCrawlStat"]] = relationship(
        back_populates="site",
        cascade="all, delete-orphan",
    )
    sitemaps: Mapped[list["BingWebmasterSitemap"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    import_runs: Mapped[list["BingWebmasterImportRun"]] = relationship(back_populates="site")


class BingWebmasterMetric(Base):
    """Search performance metrics imported from Bing Webmaster Tools."""

    __tablename__ = "bing_webmaster_metrics"
    __table_args__ = (
        UniqueConstraint(
            "bing_site_id",
            "date",
            "query",
            "page_url",
            "country",
            "device",
            name="uq_bing_metrics_site_dimensions",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bing_site_id: Mapped[int] = mapped_column(ForeignKey("bing_webmaster_sites.id", ondelete="CASCADE"), index=True)
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("bing_webmaster_import_runs.id", ondelete="SET NULL"),
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    query: Mapped[str | None] = mapped_column(String(1000), index=True)
    page_url: Mapped[str | None] = mapped_column(String(1000), index=True)
    country: Mapped[str | None] = mapped_column(String(10), index=True)
    device: Mapped[str | None] = mapped_column(String(40), index=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ctr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_position: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site: Mapped[BingWebmasterSite] = relationship(back_populates="metrics")
    import_run: Mapped["BingWebmasterImportRun | None"] = relationship(back_populates="metrics")


class BingWebmasterCrawlStat(Base):
    """Crawl issue or crawl status imported from Bing Webmaster Tools."""

    __tablename__ = "bing_webmaster_crawl_stats"
    __table_args__ = (
        UniqueConstraint(
            "bing_site_id",
            "date",
            "url",
            "http_status",
            "issue_type",
            name="uq_bing_crawl_stats_site_issue",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bing_site_id: Mapped[int] = mapped_column(ForeignKey("bing_webmaster_sites.id", ondelete="CASCADE"), index=True)
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("bing_webmaster_import_runs.id", ondelete="SET NULL"),
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer, index=True)
    issue_type: Mapped[str | None] = mapped_column(String(255), index=True)
    issue_category: Mapped[str | None] = mapped_column(String(255), index=True)
    severity: Mapped[str | None] = mapped_column(String(80), index=True)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site: Mapped[BingWebmasterSite] = relationship(back_populates="crawl_stats")
    import_run: Mapped["BingWebmasterImportRun | None"] = relationship(back_populates="crawl_stats")


class BingWebmasterSitemap(TimestampMixin, Base):
    """Sitemap metadata imported from Bing Webmaster Tools."""

    __tablename__ = "bing_webmaster_sitemaps"
    __table_args__ = (UniqueConstraint("bing_site_id", "sitemap_url", name="uq_bing_sitemaps_site_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bing_site_id: Mapped[int] = mapped_column(ForeignKey("bing_webmaster_sites.id", ondelete="CASCADE"), index=True)
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("bing_webmaster_import_runs.id", ondelete="SET NULL"),
        index=True,
    )
    sitemap_url: Mapped[str] = mapped_column(String(1000), index=True, nullable=False)
    status: Mapped[str | None] = mapped_column(String(80), index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_crawled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    url_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    site: Mapped[BingWebmasterSite] = relationship(back_populates="sitemaps")
    import_run: Mapped["BingWebmasterImportRun | None"] = relationship(back_populates="sitemaps")


class BingWebmasterImportRun(Base):
    """Bing Webmaster Tools import execution log."""

    __tablename__ = "bing_webmaster_import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("bing_webmaster_connections.id", ondelete="CASCADE"),
        index=True,
    )
    bing_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("bing_webmaster_sites.id", ondelete="SET NULL"),
        index=True,
    )
    import_type: Mapped[str] = mapped_column(String(50), default="MANUAL", index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    items_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    connection: Mapped[BingWebmasterConnection] = relationship(back_populates="import_runs")
    site: Mapped[BingWebmasterSite | None] = relationship(back_populates="import_runs")
    metrics: Mapped[list[BingWebmasterMetric]] = relationship(back_populates="import_run")
    crawl_stats: Mapped[list[BingWebmasterCrawlStat]] = relationship(back_populates="import_run")
    sitemaps: Mapped[list[BingWebmasterSitemap]] = relationship(back_populates="import_run")
