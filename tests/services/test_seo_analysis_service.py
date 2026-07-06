"""Tests for SEO analysis service."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models import CrawlPage, CrawlSession, SeoAnalysisIssue, SeoPageAnalysis
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.seo_analysis import SeoAnalysisCreate, SeoAnalysisStatus, SeoAnalysisUpdate
from backend.app.services.seo_analysis import SeoAnalysisService


def _crawl_session(db_session: Session) -> CrawlSession:
    crawl = CrawlSession(
        start_url="https://example.com",
        normalized_start_url="https://example.com/",
        status="COMPLETED",
    )
    db_session.add(crawl)
    db_session.commit()
    db_session.refresh(crawl)
    return crawl


def _crawl_page(db_session: Session, crawl: CrawlSession, raw_html: str | None = None) -> CrawlPage:
    page = CrawlPage(
        crawl_session_id=crawl.id,
        url="https://example.com",
        normalized_url="https://example.com/",
        final_url="https://example.com/",
        final_normalized_url="https://example.com/",
        depth=0,
        status_code=200,
        content_type="text/html",
        raw_html=raw_html,
        discovered_at=datetime.now(UTC),
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page


def _service(db_session: Session) -> SeoAnalysisService:
    return SeoAnalysisService(SeoAnalysisRepository(db_session), CrawlRepository(db_session))


class FailingEngine:
    """SEO engine stub raising a deterministic failure."""

    def analyze_page(self, page: object, context: object) -> object:
        raise RuntimeError("boom")


def test_seo_analysis_service_creates_pending_analysis(db_session: Session) -> None:
    """The service creates a pending SEO analysis for an existing crawl."""

    crawl = _crawl_session(db_session)
    _crawl_page(db_session, crawl)

    result = _service(db_session).create(SeoAnalysisCreate(crawl_id=crawl.id))

    assert result.id is not None
    assert result.crawl_session_id == crawl.id
    assert result.status == SeoAnalysisStatus.PENDING
    assert result.progress_percent == 0
    assert result.pages_total == 1
    assert result.pages_analyzed == 0
    assert result.issues_total == 0


def test_seo_analysis_service_rejects_unknown_crawl(db_session: Session) -> None:
    """Unknown crawl ids are rejected."""

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).create(SeoAnalysisCreate(crawl_id=999))

    assert exc_info.value.status_code == 404


def test_seo_analysis_service_lists_and_gets_analyses(db_session: Session) -> None:
    """The service lists and returns SEO analyses."""

    crawl = _crawl_session(db_session)
    created = _service(db_session).create(SeoAnalysisCreate(crawl_id=crawl.id))

    listed = _service(db_session).list(PaginationParams())
    fetched = _service(db_session).get(created.id)

    assert listed.total == 1
    assert listed.items[0].id == created.id
    assert fetched.id == created.id


def test_seo_analysis_service_updates_state(db_session: Session) -> None:
    """The service updates execution state fields."""

    crawl = _crawl_session(db_session)
    created = _service(db_session).create(SeoAnalysisCreate(crawl_id=crawl.id))

    running = _service(db_session).update_state(
        created.id,
        SeoAnalysisUpdate(status=SeoAnalysisStatus.RUNNING, progress_percent=25),
    )
    completed = _service(db_session).update_state(
        created.id,
        SeoAnalysisUpdate(status=SeoAnalysisStatus.COMPLETED),
    )

    assert running.status == SeoAnalysisStatus.RUNNING
    assert running.progress_percent == 25
    assert running.started_at is not None
    assert completed.status == SeoAnalysisStatus.COMPLETED
    assert completed.progress_percent == 100
    assert completed.completed_at is not None


def test_seo_analysis_service_deletes_analysis(db_session: Session) -> None:
    """The service deletes SEO analyses."""

    crawl = _crawl_session(db_session)
    created = _service(db_session).create(SeoAnalysisCreate(crawl_id=crawl.id))

    _service(db_session).delete(created.id)

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).get(created.id)

    assert exc_info.value.status_code == 404


def test_seo_analysis_service_runs_analysis_from_persisted_html(db_session: Session) -> None:
    """The service runs the SEO engine and persists page analyses and issues."""

    crawl = _crawl_session(db_session)
    _crawl_page(
        db_session,
        crawl,
        raw_html="""
        <html>
          <head><meta name="description" content=""></head>
          <body><h1>One</h1><h1>Two</h1></body>
        </html>
        """,
    )
    service = _service(db_session)
    created = service.create(SeoAnalysisCreate(crawl_id=crawl.id))

    result = service.run(created.id)
    page_analysis = db_session.query(SeoPageAnalysis).filter_by(seo_analysis_id=created.id).one()
    issues = db_session.query(SeoAnalysisIssue).filter_by(seo_analysis_id=created.id).all()

    assert result.status == SeoAnalysisStatus.COMPLETED
    assert result.progress_percent == 100
    assert result.pages_analyzed == 1
    assert result.issues_total == len(issues)
    assert page_analysis.status == SeoAnalysisStatus.COMPLETED
    assert page_analysis.issues_count == len(issues)
    assert {issue.code for issue in issues} >= {"title_missing", "h1_multiple"}


def test_seo_analysis_service_marks_missing_html_page_failed(db_session: Session) -> None:
    """A page without persisted HTML is analyzed without a network fallback."""

    crawl = _crawl_session(db_session)
    _crawl_page(db_session, crawl)
    service = _service(db_session)
    created = service.create(SeoAnalysisCreate(crawl_id=crawl.id))

    result = service.run(created.id)
    page_analysis = db_session.query(SeoPageAnalysis).filter_by(seo_analysis_id=created.id).one()
    issue_row = db_session.query(SeoAnalysisIssue).filter_by(seo_analysis_id=created.id).one()

    assert result.status == SeoAnalysisStatus.COMPLETED
    assert page_analysis.status == "FAILED"
    assert issue_row.code == "html_missing"


def test_seo_analysis_service_marks_analysis_failed_on_engine_error(db_session: Session) -> None:
    """Unexpected engine errors are persisted on the analysis state."""

    crawl = _crawl_session(db_session)
    _crawl_page(db_session, crawl, raw_html="<html></html>")
    service = SeoAnalysisService(
        SeoAnalysisRepository(db_session),
        CrawlRepository(db_session),
        engine=FailingEngine(),  # type: ignore[arg-type]
    )
    created = service.create(SeoAnalysisCreate(crawl_id=crawl.id))

    result = service.run(created.id)

    assert result.status == SeoAnalysisStatus.FAILED
    assert result.error_message == "boom"
