"""SQLAlchemy models for Google Analytics 4 data."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class GoogleAnalyticsProperty(TimestampMixin, Base):
    """Google Analytics 4 property linked to a tracked website."""

    __tablename__ = "google_analytics_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="SET NULL"), index=True)
    property_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    property_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    account_name: Mapped[str | None] = mapped_column(String(255), index=True)
    measurement_id: Mapped[str | None] = mapped_column(String(80), index=True)
    encrypted_access_token: Mapped[str | None] = mapped_column(Text)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    metrics: Mapped[list["GoogleAnalyticsMetric"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    imports: Mapped[list["GoogleAnalyticsImport"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )


class GoogleAnalyticsMetric(TimestampMixin, Base):
    """Google Analytics 4 metrics imported for one dimension combination."""

    __tablename__ = "google_analytics_metrics"
    __table_args__ = (
        UniqueConstraint(
            "property_id",
            "date",
            "source",
            "medium",
            "campaign",
            "device_category",
            "country",
            name="uq_ga_metrics_property_date_dimensions",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_analytics_properties.id", ondelete="CASCADE"),
        index=True,
    )
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("google_analytics_imports.id", ondelete="SET NULL"),
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), index=True)
    medium: Mapped[str | None] = mapped_column(String(255), index=True)
    campaign: Mapped[str | None] = mapped_column(String(255), index=True)
    device_category: Mapped[str | None] = mapped_column(String(80), index=True)
    country: Mapped[str | None] = mapped_column(String(120), index=True)
    users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    engaged_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    screen_page_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_session_duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    conversions: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    property: Mapped[GoogleAnalyticsProperty] = relationship(back_populates="metrics")
    import_run: Mapped["GoogleAnalyticsImport | None"] = relationship(back_populates="metrics")
    dimension: Mapped["GoogleAnalyticsDimension | None"] = relationship(
        back_populates="metric",
        cascade="all, delete-orphan",
        uselist=False,
    )


class GoogleAnalyticsDimension(TimestampMixin, Base):
    """Google Analytics 4 dimensions associated with one metric row."""

    __tablename__ = "google_analytics_dimensions"
    __table_args__ = (UniqueConstraint("metric_id", name="uq_ga_dimensions_metric_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_id: Mapped[int] = mapped_column(
        ForeignKey("google_analytics_metrics.id", ondelete="CASCADE"),
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(255), index=True)
    medium: Mapped[str | None] = mapped_column(String(255), index=True)
    campaign: Mapped[str | None] = mapped_column(String(255), index=True)
    device_category: Mapped[str | None] = mapped_column(String(80), index=True)
    country: Mapped[str | None] = mapped_column(String(120), index=True)

    metric: Mapped[GoogleAnalyticsMetric] = relationship(back_populates="dimension")


class GoogleAnalyticsImport(TimestampMixin, Base):
    """Google Analytics 4 import execution log."""

    __tablename__ = "google_analytics_imports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("google_analytics_properties.id", ondelete="CASCADE"),
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    imported_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)

    property: Mapped[GoogleAnalyticsProperty] = relationship(back_populates="imports")
    metrics: Mapped[list[GoogleAnalyticsMetric]] = relationship(back_populates="import_run")
