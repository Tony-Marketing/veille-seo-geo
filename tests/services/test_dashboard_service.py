"""Tests for Dashboard service."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import (
    CrawlPage,
    CrawlSession,
    GeoAnalysis,
    GeoProviderResult,
    GeoRecommendation,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
)
from backend.app.repositories.crawls import CrawlRepository
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.repositories.seo_analysis import SeoAnalysisRepository
from backend.app.services.dashboard import DashboardService


def _source_data(db_session: Session) -> tuple[CrawlSession, SeoAnalysis, GeoAnalysis]:
    crawl = CrawlSession(
        start_url="https://example.com",
        normalized_start_url="https://example.com/",
        status="COMPLETED",
        pages_crawled=2,
        finished_at=datetime.now(UTC),
    )
    db_session.add(crawl)
    db_session.commit()
    db_session.refresh(crawl)

    first_page = CrawlPage(
        crawl_session_id=crawl.id,
        url="https://example.com/a",
        normalized_url="https://example.com/a",
        depth=0,
        status_code=200,
        raw_html="<html>A</html>",
        discovered_at=datetime.now(UTC),
    )
    second_page = CrawlPage(
        crawl_session_id=crawl.id,
        url="https://example.com/b",
        normalized_url="https://example.com/b",
        depth=0,
        status_code=200,
        raw_html="<html>B</html>",
        discovered_at=datetime.now(UTC),
    )
    db_session.add_all([first_page, second_page])
    db_session.commit()
    db_session.refresh(first_page)
    db_session.refresh(second_page)

    seo_analysis = SeoAnalysis(
        crawl_session_id=crawl.id,
        status="COMPLETED",
        progress_percent=100,
        pages_total=2,
        pages_analyzed=2,
    )
    db_session.add(seo_analysis)
    db_session.commit()
    db_session.refresh(seo_analysis)

    first_seo_page = SeoPageAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_page_id=first_page.id,
        status="COMPLETED",
        score=90,
    )
    second_seo_page = SeoPageAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_page_id=second_page.id,
        status="COMPLETED",
        score=45,
    )
    db_session.add_all([first_seo_page, second_seo_page])
    db_session.commit()
    db_session.refresh(first_seo_page)
    db_session.refresh(second_seo_page)

    issue = SeoAnalysisIssue(
        seo_analysis_id=seo_analysis.id,
        seo_page_analysis_id=second_seo_page.id,
        crawl_page_id=second_page.id,
        family="title",
        criterion="presence",
        severity="critical",
        code="title_missing",
        message="Title absent.",
    )
    db_session.add(issue)

    geo_analysis = GeoAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_session_id=crawl.id,
        status="COMPLETED",
        geo_score=65,
        llm_score=70,
        global_score=67,
        providers_requested=["fake"],
    )
    db_session.add(geo_analysis)
    db_session.commit()
    db_session.refresh(geo_analysis)

    first_geo_result = GeoProviderResult(
        geo_analysis_id=geo_analysis.id,
        crawl_page_id=first_page.id,
        provider_name="fake",
        status="COMPLETED",
        normalized_response={"geo_score": 82},
    )
    second_geo_result = GeoProviderResult(
        geo_analysis_id=geo_analysis.id,
        crawl_page_id=second_page.id,
        provider_name="fake",
        status="COMPLETED",
        normalized_response={"geo_score": 35},
    )
    db_session.add_all([first_geo_result, second_geo_result])
    db_session.commit()
    db_session.refresh(second_geo_result)

    recommendation = GeoRecommendation(
        geo_analysis_id=geo_analysis.id,
        provider_result_id=second_geo_result.id,
        crawl_page_id=second_page.id,
        recommendation_type="geo",
        severity="major",
        priority=1,
        title="Clarifier la page",
        description="Ajouter une synthese.",
        source="fake",
    )
    db_session.add(recommendation)
    db_session.commit()
    return crawl, seo_analysis, geo_analysis


def _service(db_session: Session) -> DashboardService:
    return DashboardService(
        CrawlRepository(db_session),
        SeoAnalysisRepository(db_session),
        GeoAnalysisRepository(db_session),
    )


def test_dashboard_service_returns_empty_overview_without_data(db_session: Session) -> None:
    """The dashboard returns a stable empty payload when no source data exists."""

    overview = _service(db_session).overview()

    assert overview.crawl.crawled_pages_count == 0
    assert overview.seo.average_score is None
    assert overview.geo.average_score is None
    assert overview.future_sources.google_search_console.status == "planned"


def test_dashboard_service_aggregates_crawl_seo_and_geo_data(db_session: Session) -> None:
    """The dashboard aggregates persisted crawl, SEO and GEO results."""

    crawl, seo_analysis, geo_analysis = _source_data(db_session)

    overview = _service(db_session).overview(
        crawl_id=crawl.id,
        seo_analysis_id=seo_analysis.id,
        geo_analysis_id=geo_analysis.id,
    )

    assert overview.crawl.crawled_pages_count == 2
    assert overview.seo.average_score == 67.5
    assert overview.seo.best_page is not None
    assert overview.seo.best_page.score == 90
    assert overview.seo.worst_page is not None
    assert overview.seo.worst_page.score == 45
    assert overview.seo.critical_errors_count == 1
    assert overview.geo.average_score == 58.5
    assert overview.geo.best_page is not None
    assert overview.geo.best_page.score == 82
    assert overview.geo.worst_page is not None
    assert overview.geo.worst_page.score == 35
    assert overview.geo.analyses_count == 1
    assert overview.geo.top_recommendations[0].title == "Clarifier la page"
    assert overview.priority_pages[0].url == "https://example.com/b"
    assert overview.comparison.average_gap == 9
    assert sum(bucket.count for bucket in overview.seo_score_distribution) == 2
    assert sum(bucket.count for bucket in overview.geo_score_distribution) == 2
