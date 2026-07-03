"""Repository for SEO analysis data."""

from typing import Any

from sqlalchemy import func, select
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

    def count_crawl_pages(self, crawl_session_id: int) -> int:
        """Return number of crawled pages for a crawl session."""

        statement = select(func.count()).select_from(CrawlPage).where(CrawlPage.crawl_session_id == crawl_session_id)
        return int(self.db.scalar(statement) or 0)

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

