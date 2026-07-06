"""Tests for SEO analysis repository."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import CrawlPage, CrawlSession, SeoAnalysisIssue
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.schemas.pagination import PaginationParams


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


def _crawl_page(db_session: Session, crawl: CrawlSession) -> CrawlPage:
    page = CrawlPage(
        crawl_session_id=crawl.id,
        url="https://example.com",
        normalized_url="https://example.com/",
        depth=0,
        discovered_at=datetime.now(UTC),
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page


def test_seo_analysis_repository_creates_and_lists_analyses(db_session: Session) -> None:
    """The repository persists and lists SEO analyses."""

    crawl = _crawl_session(db_session)
    repository = SeoAnalysisRepository(db_session)

    analysis = repository.create({"crawl_session_id": crawl.id, "status": "PENDING", "progress_percent": 0})
    items, total = repository.list(PaginationParams())

    assert analysis.id is not None
    assert total == 1
    assert items == [analysis]
    assert repository.get_by_crawl(crawl.id) == [analysis]


def test_seo_analysis_repository_counts_crawl_pages(db_session: Session) -> None:
    """The repository counts pages attached to a crawl."""

    crawl = _crawl_session(db_session)
    _crawl_page(db_session, crawl)

    assert SeoAnalysisRepository(db_session).count_crawl_pages(crawl.id) == 1


def test_seo_analysis_repository_creates_page_analysis_and_issue(db_session: Session) -> None:
    """The repository persists page placeholders and issues."""

    crawl = _crawl_session(db_session)
    page = _crawl_page(db_session, crawl)
    repository = SeoAnalysisRepository(db_session)
    analysis = repository.create({"crawl_session_id": crawl.id, "status": "PENDING", "progress_percent": 0})

    page_analysis = repository.create_page_analysis(
        {
            "seo_analysis_id": analysis.id,
            "crawl_page_id": page.id,
            "status": "PENDING",
        },
    )
    issue = repository.create_issue(
        {
            "seo_analysis_id": analysis.id,
            "seo_page_analysis_id": page_analysis.id,
            "crawl_page_id": page.id,
            "family": "title",
            "criterion": "presence",
            "severity": "major",
            "code": "title_missing",
            "message": "Title absent.",
        },
    )

    assert page_analysis.id is not None
    assert issue.id is not None
    assert issue.seo_analysis_id == analysis.id


def test_seo_analysis_repository_lists_pages_and_clears_results(db_session: Session) -> None:
    """The repository returns crawl pages and clears previous SEO results."""

    crawl = _crawl_session(db_session)
    page = _crawl_page(db_session, crawl)
    repository = SeoAnalysisRepository(db_session)
    analysis = repository.create({"crawl_session_id": crawl.id, "status": "PENDING", "progress_percent": 0})
    page_analysis = repository.create_page_analysis(
        {"seo_analysis_id": analysis.id, "crawl_page_id": page.id, "status": "COMPLETED"},
    )
    repository.create_issue(
        {
            "seo_analysis_id": analysis.id,
            "seo_page_analysis_id": page_analysis.id,
            "crawl_page_id": page.id,
            "family": "title",
            "criterion": "presence",
            "severity": "major",
            "code": "title_missing",
            "message": "Title absent.",
        },
    )

    pages = repository.list_crawl_pages(crawl.id)
    repository.clear_results(analysis.id)

    assert pages == [page]
    assert db_session.query(SeoAnalysisIssue).filter_by(seo_analysis_id=analysis.id).count() == 0
