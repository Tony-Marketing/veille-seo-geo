"""Tests for GEO analysis SQLAlchemy models."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    CrawlPage,
    CrawlSession,
    GeoAnalysis,
    GeoProviderResult,
    GeoRecommendation,
    SeoAnalysis,
)


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
        raw_html="<html></html>",
        discovered_at=datetime.now(UTC),
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page


def test_geo_analysis_model_relationships(db_session: Session) -> None:
    """GEO analysis models are linked through relationships."""

    crawl = _crawl_session(db_session)
    page = _crawl_page(db_session, crawl)
    seo_analysis = SeoAnalysis(crawl_session_id=crawl.id, status="COMPLETED", progress_percent=100)
    db_session.add(seo_analysis)
    db_session.commit()
    db_session.refresh(seo_analysis)

    analysis = GeoAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_session_id=crawl.id,
        status="PENDING",
        providers_requested=["openai"],
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    provider_result = GeoProviderResult(
        geo_analysis_id=analysis.id,
        crawl_page_id=page.id,
        provider_name="openai",
        status="NOT_IMPLEMENTED",
    )
    db_session.add(provider_result)
    db_session.commit()
    db_session.refresh(provider_result)

    recommendation = GeoRecommendation(
        geo_analysis_id=analysis.id,
        provider_result_id=provider_result.id,
        crawl_page_id=page.id,
        recommendation_type="geo",
        severity="medium",
        priority=3,
        title="Provider indisponible",
        description="Configurer le provider.",
        source="openai",
    )
    db_session.add(recommendation)
    db_session.commit()
    db_session.refresh(recommendation)
    db_session.refresh(analysis)
    db_session.refresh(provider_result)

    assert analysis.provider_results == [provider_result]
    assert analysis.recommendations == [recommendation]
    assert provider_result.recommendations == [recommendation]
    assert recommendation.analysis == analysis
    assert recommendation.provider_result == provider_result
