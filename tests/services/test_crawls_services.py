"""Tests for crawl services."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.crawler.engine import (
    CRAWL_STATUS_COMPLETED,
    CrawlPageResult,
    CrawlProgress,
    CrawlRunResult,
)
from backend.app.models import CrawlPage
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.websites import WebsiteRepository
from backend.app.schemas.crawls import CrawlCreate
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.crawls import CrawlService


class FakeEngine:
    """Engine stub producing one crawled page."""

    def run(self, start_url: str, **kwargs: object) -> CrawlRunResult:
        on_page_result = kwargs["on_page_result"]
        page = CrawlPageResult(
            url=start_url,
            normalized_url=start_url,
            final_url=start_url,
            final_normalized_url=start_url,
            depth=0,
            status_code=200,
            content_type="text/html",
            raw_html="<html><title>Example</title></html>",
            is_redirect=False,
            redirect_url=None,
            redirect_count=0,
            response_time_ms=12,
            error_message=None,
            discovered_at=datetime.now(UTC),
            visited_at=datetime.now(UTC),
            links_found=0,
        )
        progress = CrawlProgress(
            discovered_count=1,
            processed_count=1,
            failed_count=0,
            pending_count=0,
            max_depth_reached=0,
        )
        on_page_result(page, progress)  # type: ignore[operator]
        return CrawlRunResult(
            status=CRAWL_STATUS_COMPLETED,
            pages=[page],
            discovered_count=1,
            processed_count=1,
            failed_count=0,
            pending_count=0,
            max_depth_reached=0,
        )


def _service(db_session: Session) -> CrawlService:
    return CrawlService(CrawlRepository(db_session), WebsiteRepository(db_session), engine=FakeEngine())  # type: ignore[arg-type]


def test_crawl_service_creates_pending_session(db_session: Session) -> None:
    """The service creates a pending crawl session."""

    result = _service(db_session).create(CrawlCreate(start_url="https://example.com", max_depth=1, max_pages=5))

    assert result.id is not None
    assert result.status == "PENDING"
    assert result.normalized_start_url == "https://example.com/"
    assert result.max_depth == 1
    assert result.max_pages == 5


def test_crawl_service_rejects_invalid_start_url(db_session: Session) -> None:
    """Invalid start URLs are rejected before persistence."""

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).create(CrawlCreate(start_url="ftp://example.com/file"))

    assert exc_info.value.status_code == 422


def test_crawl_service_starts_and_persists_pages(db_session: Session) -> None:
    """Starting a crawl persists page results through the repository."""

    service = _service(db_session)
    created = service.create(CrawlCreate(start_url="https://example.com"))

    result = service.start(created.id)
    pages = service.list_pages(created.id, PaginationParams())

    assert result.status == "COMPLETED"
    assert result.pages_found == 1
    assert result.pages_crawled == 1
    assert pages.total == 1
    assert pages.items[0].status_code == 200
    persisted_page = db_session.query(CrawlPage).filter_by(crawl_session_id=created.id).one()
    assert persisted_page.raw_html == "<html><title>Example</title></html>"
    assert not hasattr(pages.items[0], "raw_html")


def test_crawl_service_cancels_pending_session(db_session: Session) -> None:
    """A pending crawl can be cancelled before execution."""

    service = _service(db_session)
    created = service.create(CrawlCreate(start_url="https://example.com"))

    result = service.cancel(created.id)

    assert result.status == "CANCELLED"
    assert result.cancel_requested is True


def test_crawl_service_returns_404_for_unknown_crawl(db_session: Session) -> None:
    """Unknown crawl ids return a 404 error."""

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).get(999)

    assert exc_info.value.status_code == 404
