"""SQLAlchemy models for GEO analysis results."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class GeoAnalysis(TimestampMixin, Base):
    """Persisted GEO analysis execution linked to a SEO analysis."""

    __tablename__ = "geo_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seo_analysis_id: Mapped[int] = mapped_column(ForeignKey("seo_analyses.id", ondelete="CASCADE"), index=True)
    crawl_session_id: Mapped[int] = mapped_column(ForeignKey("crawl_sessions.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    geo_score: Mapped[float | None] = mapped_column(Float)
    llm_score: Mapped[float | None] = mapped_column(Float)
    global_score: Mapped[float | None] = mapped_column(Float)
    providers_requested: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pages_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provider_results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recommendations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    provider_results: Mapped[list["GeoProviderResult"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[list["GeoRecommendation"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class GeoProviderResult(TimestampMixin, Base):
    """Persisted raw and normalized response from one GEO provider execution."""

    __tablename__ = "geo_provider_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    geo_analysis_id: Mapped[int] = mapped_column(ForeignKey("geo_analyses.id", ondelete="CASCADE"), index=True)
    crawl_page_id: Mapped[int | None] = mapped_column(ForeignKey("crawl_pages.id", ondelete="CASCADE"), index=True)
    provider_name: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(150), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[str | None] = mapped_column(Text)
    normalized_response: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)

    analysis: Mapped[GeoAnalysis] = relationship(back_populates="provider_results")
    recommendations: Mapped[list["GeoRecommendation"]] = relationship(back_populates="provider_result")


class GeoRecommendation(TimestampMixin, Base):
    """Persisted GEO recommendation produced from normalized provider results."""

    __tablename__ = "geo_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    geo_analysis_id: Mapped[int] = mapped_column(ForeignKey("geo_analyses.id", ondelete="CASCADE"), index=True)
    provider_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("geo_provider_results.id", ondelete="SET NULL"),
        index=True,
    )
    crawl_page_id: Mapped[int | None] = mapped_column(ForeignKey("crawl_pages.id", ondelete="CASCADE"), index=True)
    recommendation_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(120), index=True)
    impact_score: Mapped[float | None] = mapped_column(Float)

    analysis: Mapped[GeoAnalysis] = relationship(back_populates="recommendations")
    provider_result: Mapped[GeoProviderResult | None] = relationship(back_populates="recommendations")
