"""Business service for crawl sessions."""

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.crawler.engine import (
    CRAWL_STATUS_CANCELLED,
    CRAWL_STATUS_COMPLETED,
    CRAWL_STATUS_FAILED,
    CrawlerEngine,
    CrawlPageResult,
    CrawlProgress,
)
from backend.app.crawler.normalizer import UrlNormalizer
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.crawls import (
    CrawlCreate,
    CrawlList,
    CrawlPageList,
    CrawlPageRead,
    CrawlRead,
    CrawlStart,
)
from backend.app.schemas.pagination import PaginationParams

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_CANCELLED = "CANCELLED"


class CrawlService:
    """Orchestrate crawl business rules and persistence."""

    def __init__(
        self,
        repository: CrawlRepository,
        website_repository: WebsiteRepository,
        *,
        engine: CrawlerEngine | None = None,
    ) -> None:
        self.repository = repository
        self.website_repository = website_repository
        self.engine = engine or CrawlerEngine()
        self.normalizer = UrlNormalizer()

    def list(self, params: PaginationParams) -> CrawlList:
        """Return paginated crawl sessions."""

        items, total = self.repository.list(params)
        return CrawlList(
            items=[CrawlRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get(self, crawl_id: int) -> CrawlRead:
        """Return one crawl session."""

        session = self.repository.get(crawl_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl introuvable.")
        return CrawlRead.model_validate(session)

    def create(self, payload: CrawlCreate) -> CrawlRead:
        """Create a pending crawl session."""

        start_url = self._start_url(payload)
        normalized_start_url = self.normalizer.normalize(start_url)
        if normalized_start_url is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="URL de depart invalide.")

        session = self.repository.create(
            {
                "website_id": payload.website_id,
                "start_url": start_url,
                "normalized_start_url": normalized_start_url,
                "status": STATUS_PENDING,
                "max_depth": payload.max_depth,
                "max_pages": payload.max_pages,
                "pages_found": 0,
                "pages_crawled": 0,
                "pages_failed": 0,
                "pending_urls": 0,
                "max_depth_reached": 0,
                "cancel_requested": False,
            },
        )
        return CrawlRead.model_validate(session)

    def start(self, crawl_id: int, payload: CrawlStart | None = None) -> CrawlRead:
        """Run a crawl session synchronously and persist results through the repository."""

        session = self.repository.get(crawl_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl introuvable.")
        if session.status == STATUS_RUNNING:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce crawl est deja en cours.")
        if session.status == STATUS_COMPLETED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce crawl est deja termine.")

        max_depth = payload.max_depth if payload and payload.max_depth is not None else session.max_depth
        max_pages = payload.max_pages if payload and payload.max_pages is not None else session.max_pages
        self.repository.delete_pages(session.id)
        session = self.repository.update(
            session,
            {
                "status": STATUS_RUNNING,
                "max_depth": max_depth,
                "max_pages": max_pages,
                "pages_found": 0,
                "pages_crawled": 0,
                "pages_failed": 0,
                "pending_urls": 0,
                "max_depth_reached": 0,
                "cancel_requested": False,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "finished_at": None,
                "last_progress_at": datetime.now(UTC),
            },
        )

        run_result = self.engine.run(
            session.normalized_start_url,
            max_depth=max_depth,
            max_pages=max_pages,
            stop_requested=lambda: self.repository.is_cancel_requested(session.id),
            on_page_result=lambda page, progress: self._persist_page(session.id, session.website_id, page, progress),
        )
        final_status = self._final_status(run_result.status)
        updated = self.repository.update(
            session,
            {
                "status": final_status,
                "pages_found": run_result.discovered_count,
                "pages_crawled": run_result.processed_count,
                "pages_failed": run_result.failed_count,
                "pending_urls": run_result.pending_count,
                "max_depth_reached": run_result.max_depth_reached,
                "error_message": run_result.error_message,
                "finished_at": datetime.now(UTC),
                "last_progress_at": datetime.now(UTC),
            },
        )
        return CrawlRead.model_validate(updated)

    def cancel(self, crawl_id: int) -> CrawlRead:
        """Request cancellation for a crawl session."""

        session = self.repository.get(crawl_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl introuvable.")
        if session.status in {STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED}:
            return CrawlRead.model_validate(session)

        data: dict[str, object] = {"cancel_requested": True, "last_progress_at": datetime.now(UTC)}
        if session.status == STATUS_PENDING:
            data["status"] = STATUS_CANCELLED
            data["finished_at"] = datetime.now(UTC)
        updated = self.repository.update(session, data)
        return CrawlRead.model_validate(updated)

    def list_pages(self, crawl_id: int, params: PaginationParams) -> CrawlPageList:
        """Return pages discovered for a crawl session."""

        if self.repository.get(crawl_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl introuvable.")
        items, total = self.repository.list_pages(crawl_id, params)
        return CrawlPageList(
            items=[CrawlPageRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def _start_url(self, payload: CrawlCreate) -> str:
        if payload.website_id is None:
            return str(payload.start_url)

        website = self.website_repository.get(payload.website_id)
        if website is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site introuvable.")
        return payload.start_url or website.url

    def _persist_page(
        self,
        session_id: int,
        website_id: int | None,
        page: CrawlPageResult,
        progress: CrawlProgress,
    ) -> None:
        self.repository.add_page(
            {
                "crawl_session_id": session_id,
                "website_id": website_id,
                "url": page.url,
                "normalized_url": page.normalized_url,
                "final_url": page.final_url,
                "final_normalized_url": page.final_normalized_url,
                "depth": page.depth,
                "status_code": page.status_code,
                "content_type": page.content_type,
                "is_redirect": page.is_redirect,
                "redirect_url": page.redirect_url,
                "redirect_count": page.redirect_count,
                "response_time_ms": page.response_time_ms,
                "error_message": page.error_message,
                "discovered_at": page.discovered_at,
                "visited_at": page.visited_at,
            },
        )
        session = self.repository.get(session_id)
        if session is None:
            return
        self.repository.update(
            session,
            {
                "pages_found": progress.discovered_count,
                "pages_crawled": progress.processed_count,
                "pages_failed": progress.failed_count,
                "pending_urls": progress.pending_count,
                "max_depth_reached": progress.max_depth_reached,
                "last_progress_at": datetime.now(UTC),
            },
        )

    def _final_status(self, engine_status: str) -> str:
        if engine_status == CRAWL_STATUS_COMPLETED:
            return STATUS_COMPLETED
        if engine_status == CRAWL_STATUS_CANCELLED:
            return STATUS_CANCELLED
        if engine_status == CRAWL_STATUS_FAILED:
            return STATUS_FAILED
        return STATUS_FAILED
