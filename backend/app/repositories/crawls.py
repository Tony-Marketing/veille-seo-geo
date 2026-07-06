"""Repository for crawl sessions and pages."""

from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.app.models import CrawlPage, CrawlSession
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class CrawlRepository(BaseRepository[CrawlSession]):
    """Encapsulate persistence for crawl sessions."""

    search_fields = ("start_url", "normalized_start_url", "status")

    def __init__(self, db: Session) -> None:
        super().__init__(db, CrawlSession)

    def add_page(self, data: dict[str, Any]) -> CrawlPage:
        """Persist one crawled page."""

        page = CrawlPage(**data)
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def delete_pages(self, session_id: int) -> None:
        """Delete pages attached to a crawl session."""

        self.db.execute(delete(CrawlPage).where(CrawlPage.crawl_session_id == session_id))
        self.db.commit()

    def list_pages(self, session_id: int, params: PaginationParams) -> tuple[list[CrawlPage], int]:
        """Return pages for a crawl session."""

        statement = select(CrawlPage).where(CrawlPage.crawl_session_id == session_id)
        count_statement = select(func.count()).select_from(CrawlPage).where(CrawlPage.crawl_session_id == session_id)
        filters = self._page_search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        if params.sort and hasattr(CrawlPage, params.sort):
            sort_column = getattr(CrawlPage, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        else:
            statement = statement.order_by(CrawlPage.depth.asc(), CrawlPage.id.asc())
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def get_latest(self, website_id: int | None = None) -> CrawlSession | None:
        """Return the latest crawl session, optionally filtered by website."""

        statement = select(CrawlSession)
        if website_id is not None:
            statement = statement.where(CrawlSession.website_id == website_id)
        statement = statement.order_by(CrawlSession.id.desc()).limit(1)
        return self.db.scalar(statement)

    def count_pages_for_session(self, session_id: int) -> int:
        """Return number of crawled pages for one session."""

        statement = select(func.count()).select_from(CrawlPage).where(CrawlPage.crawl_session_id == session_id)
        return int(self.db.scalar(statement) or 0)

    def count_failed_pages_for_session(self, session_id: int) -> int:
        """Return number of failed pages for one session."""

        statement = (
            select(func.count())
            .select_from(CrawlPage)
            .where(
                CrawlPage.crawl_session_id == session_id,
                (CrawlPage.error_message.is_not(None)) | (CrawlPage.status_code >= 400),
            )
        )
        return int(self.db.scalar(statement) or 0)

    def is_cancel_requested(self, session_id: int) -> bool:
        """Return whether a crawl session has received a cancel request."""

        session = self.get(session_id)
        return bool(session and session.cancel_requested)

    def _page_search_filters(self, search: str | None) -> Any | None:
        if not search:
            return None
        return CrawlPage.url.ilike(f"%{search}%") | CrawlPage.normalized_url.ilike(f"%{search}%")

