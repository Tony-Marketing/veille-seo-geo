"""SQLAlchemy models for SEO analysis results."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class SeoAnalysis(TimestampMixin, Base):
    """Persisted SEO analysis execution linked to a crawl."""

    __tablename__ = "seo_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crawl_session_id: Mapped[int] = mapped_column(ForeignKey("crawl_sessions.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    global_score: Mapped[float | None] = mapped_column(Float)
    pages_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    issues_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pages: Mapped[list["SeoPageAnalysis"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    issues: Mapped[list["SeoAnalysisIssue"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class SeoPageAnalysis(TimestampMixin, Base):
    """Persisted SEO analysis result for one crawled page."""

    __tablename__ = "seo_page_analyses"
    __table_args__ = (
        UniqueConstraint("seo_analysis_id", "crawl_page_id", name="uq_seo_page_analyses_analysis_page"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seo_analysis_id: Mapped[int] = mapped_column(ForeignKey("seo_analyses.id", ondelete="CASCADE"), index=True)
    crawl_page_id: Mapped[int] = mapped_column(ForeignKey("crawl_pages.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    issues_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    analysis: Mapped[SeoAnalysis] = relationship(back_populates="pages")
    issues: Mapped[list["SeoAnalysisIssue"]] = relationship(
        back_populates="page_analysis",
        cascade="all, delete-orphan",
    )


class SeoAnalysisIssue(TimestampMixin, Base):
    """Persisted deterministic SEO issue found during an analysis."""

    __tablename__ = "seo_analysis_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seo_analysis_id: Mapped[int] = mapped_column(ForeignKey("seo_analyses.id", ondelete="CASCADE"), index=True)
    seo_page_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("seo_page_analyses.id", ondelete="CASCADE"),
        index=True,
    )
    crawl_page_id: Mapped[int | None] = mapped_column(ForeignKey("crawl_pages.id", ondelete="CASCADE"), index=True)
    family: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    criterion: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)

    analysis: Mapped[SeoAnalysis] = relationship(back_populates="issues")
    page_analysis: Mapped[SeoPageAnalysis | None] = relationship(back_populates="issues")

