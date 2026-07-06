"""Tests for SEO analysis SQLAlchemy models."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import CrawlPage, CrawlSession, SeoAnalysis, SeoAnalysisIssue, SeoPageAnalysis


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


def test_seo_analysis_model_relationships(db_session: Session) -> None:
    """SEO analysis models are linked through relationships."""

    crawl = _crawl_session(db_session)
    page = _crawl_page(db_session, crawl)
    analysis = SeoAnalysis(crawl_session_id=crawl.id, status="PENDING", progress_percent=0, pages_total=1)
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    page_analysis = SeoPageAnalysis(
        seo_analysis_id=analysis.id,
        crawl_page_id=page.id,
        status="PENDING",
    )
    db_session.add(page_analysis)
    db_session.commit()
    db_session.refresh(page_analysis)

    issue = SeoAnalysisIssue(
        seo_analysis_id=analysis.id,
        seo_page_analysis_id=page_analysis.id,
        crawl_page_id=page.id,
        family="title",
        criterion="presence",
        severity="major",
        code="title_missing",
        message="Title absent.",
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    db_session.refresh(analysis)
    db_session.refresh(page_analysis)

    assert analysis.pages == [page_analysis]
    assert analysis.issues == [issue]
    assert page_analysis.issues == [issue]
    assert issue.analysis == analysis
    assert issue.page_analysis == page_analysis

