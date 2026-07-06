"""Tests for GEO analysis repository."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    CrawlPage,
    CrawlSession,
    GeoProviderResult,
    GeoRecommendation,
    SeoAnalysis,
    SeoPageAnalysis,
)
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.schemas.pagination import PaginationParams


def _source_data(db_session: Session) -> tuple[CrawlSession, CrawlPage, SeoAnalysis, SeoPageAnalysis]:
    crawl = CrawlSession(
        start_url="https://example.com",
        normalized_start_url="https://example.com/",
        status="COMPLETED",
    )
    db_session.add(crawl)
    db_session.commit()
    db_session.refresh(crawl)

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

    seo_analysis = SeoAnalysis(crawl_session_id=crawl.id, status="COMPLETED", progress_percent=100)
    db_session.add(seo_analysis)
    db_session.commit()
    db_session.refresh(seo_analysis)

    seo_page = SeoPageAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_page_id=page.id,
        status="COMPLETED",
        score=80,
    )
    db_session.add(seo_page)
    db_session.commit()
    db_session.refresh(seo_page)
    return crawl, page, seo_analysis, seo_page


def test_geo_analysis_repository_creates_and_lists_analyses(db_session: Session) -> None:
    """The repository persists and lists GEO analyses."""

    crawl, _, seo_analysis, _ = _source_data(db_session)
    repository = GeoAnalysisRepository(db_session)

    analysis = repository.create(
        {
            "seo_analysis_id": seo_analysis.id,
            "crawl_session_id": crawl.id,
            "status": "PENDING",
            "providers_requested": ["openai"],
        },
    )
    items, total = repository.list(PaginationParams())

    assert analysis.id is not None
    assert total == 1
    assert items == [analysis]
    assert repository.get_seo_analysis(seo_analysis.id) == seo_analysis


def test_geo_analysis_repository_lists_pages_and_issues(db_session: Session) -> None:
    """The repository returns source pages for one SEO analysis."""

    _, page, seo_analysis, seo_page = _source_data(db_session)
    repository = GeoAnalysisRepository(db_session)

    pages = repository.list_pages_for_seo_analysis(seo_analysis.id)

    assert pages == [(page, seo_page)]
    assert repository.count_seo_pages(seo_analysis.id) == 1


def test_geo_analysis_repository_persists_and_clears_results(db_session: Session) -> None:
    """The repository persists provider results and recommendations."""

    crawl, page, seo_analysis, _ = _source_data(db_session)
    repository = GeoAnalysisRepository(db_session)
    analysis = repository.create(
        {
            "seo_analysis_id": seo_analysis.id,
            "crawl_session_id": crawl.id,
            "status": "PENDING",
            "providers_requested": ["openai"],
        },
    )

    provider_result = repository.create_provider_result(
        {
            "geo_analysis_id": analysis.id,
            "crawl_page_id": page.id,
            "provider_name": "openai",
            "status": "NOT_IMPLEMENTED",
        },
    )
    recommendation = repository.create_recommendation(
        {
            "geo_analysis_id": analysis.id,
            "provider_result_id": provider_result.id,
            "crawl_page_id": page.id,
            "recommendation_type": "geo",
            "severity": "medium",
            "priority": 3,
            "title": "Provider indisponible",
            "description": "Configurer le provider.",
        },
    )
    detail = repository.get_with_details(analysis.id)

    assert isinstance(provider_result, GeoProviderResult)
    assert isinstance(recommendation, GeoRecommendation)
    assert detail is not None
    assert detail.provider_results == [provider_result]

    repository.clear_results(analysis.id)

    assert db_session.query(GeoProviderResult).filter_by(geo_analysis_id=analysis.id).count() == 0
    assert db_session.query(GeoRecommendation).filter_by(geo_analysis_id=analysis.id).count() == 0
