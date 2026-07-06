"""Repository for SEO analysis data."""

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.app.models import CrawlPage, SeoAnalysis, SeoAnalysisIssue, SeoPageAnalysis
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class SeoAnalysisRepository(BaseRepository[SeoAnalysis]):
    """Encapsulate persistence for SEO analyses."""

    search_fields = ("status",)

    def __init__(self, db: Session) -> None:
        super().__init__(db, SeoAnalysis)

    def get_by_crawl(self, crawl_session_id: int) -> list[SeoAnalysis]:
        """Return SEO analyses linked to a crawl session."""

        statement = select(SeoAnalysis).where(SeoAnalysis.crawl_session_id == crawl_session_id)
        return list(self.db.scalars(statement))

    def get_latest_completed(self, crawl_session_id: int | None = None) -> SeoAnalysis | None:
        """Return the latest completed SEO analysis, optionally filtered by crawl."""

        statement = select(SeoAnalysis).where(SeoAnalysis.status == "COMPLETED")
        if crawl_session_id is not None:
            statement = statement.where(SeoAnalysis.crawl_session_id == crawl_session_id)
        statement = statement.order_by(SeoAnalysis.id.desc()).limit(1)
        return self.db.scalar(statement)

    def count_crawl_pages(self, crawl_session_id: int) -> int:
        """Return number of crawled pages for a crawl session."""

        statement = select(func.count()).select_from(CrawlPage).where(CrawlPage.crawl_session_id == crawl_session_id)
        return int(self.db.scalar(statement) or 0)

    def list_crawl_pages(self, crawl_session_id: int) -> list[CrawlPage]:
        """Return crawl pages to analyze for one crawl session."""

        statement = (
            select(CrawlPage)
            .where(CrawlPage.crawl_session_id == crawl_session_id)
            .order_by(CrawlPage.depth.asc(), CrawlPage.id.asc())
        )
        return list(self.db.scalars(statement))

    def list_page_analyses_with_pages(self, analysis_id: int) -> list[tuple[SeoPageAnalysis, CrawlPage]]:
        """Return SEO page analyses with their crawled pages."""

        statement = (
            select(SeoPageAnalysis, CrawlPage)
            .join(CrawlPage, CrawlPage.id == SeoPageAnalysis.crawl_page_id)
            .where(SeoPageAnalysis.seo_analysis_id == analysis_id)
            .order_by(SeoPageAnalysis.id.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(statement).all()]

    def list_issues_for_analysis(self, analysis_id: int) -> list[SeoAnalysisIssue]:
        """Return SEO issues attached to one analysis."""

        statement = (
            select(SeoAnalysisIssue)
            .where(SeoAnalysisIssue.seo_analysis_id == analysis_id)
            .order_by(SeoAnalysisIssue.severity.asc(), SeoAnalysisIssue.id.asc())
        )
        return list(self.db.scalars(statement))

    def clear_results(self, analysis_id: int) -> None:
        """Delete page analyses and issues attached to an analysis."""

        self.db.execute(delete(SeoAnalysisIssue).where(SeoAnalysisIssue.seo_analysis_id == analysis_id))
        self.db.execute(delete(SeoPageAnalysis).where(SeoPageAnalysis.seo_analysis_id == analysis_id))
        self.db.commit()

    def create_page_analysis(self, data: dict[str, Any]) -> SeoPageAnalysis:
        """Persist one SEO page analysis placeholder."""

        item = SeoPageAnalysis(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_issue(self, data: dict[str, Any]) -> SeoAnalysisIssue:
        """Persist one SEO analysis issue."""

        item = SeoAnalysisIssue(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, params: PaginationParams) -> tuple[list[SeoAnalysis], int]:
        """Return paginated SEO analyses ordered by recent creation."""

        statement = select(self.model)
        count_statement = select(func.count()).select_from(self.model)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(self.model, params.sort):
            sort_column = getattr(self.model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(self.model.id.desc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)
