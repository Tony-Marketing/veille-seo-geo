"""Tests for Dashboard V2 service."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models import (
    Alert,
    CrawlPage,
    CrawlSession,
    GeoVisibilitySnapshot,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
    Website,
)
from backend.app.repositories.dashboard_v2 import DashboardV2Repository
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.schemas.dashboard_v2 import DashboardV2Filters, DashboardV2Period
from backend.app.services.dashboard_v2 import DashboardV2Service
from backend.app.services.geo_intelligence import GeoIntelligenceService
from backend.app.services.recommendations import RecommendationService


def _service(db_session: Session) -> DashboardV2Service:
    geo_service = GeoIntelligenceService(GeoIntelligenceRepository(db_session))
    return DashboardV2Service(
        DashboardV2Repository(db_session),
        RecommendationService(RecommendationRepository(db_session), geo_service),
        geo_service,
        now_provider=lambda: datetime(2026, 7, 10, tzinfo=UTC),
    )


def _website(db_session: Session) -> Website:
    website = Website(name="Example", url="https://example.com", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.refresh(website)
    return website


def _seo_data(db_session: Session) -> Website:
    website = _website(db_session)
    now = datetime(2026, 7, 10, tzinfo=UTC)
    crawl = CrawlSession(
        website_id=website.id,
        start_url=website.url,
        normalized_start_url=website.url,
        status="COMPLETED",
        pages_crawled=1,
        created_at=now,
    )
    db_session.add(crawl)
    db_session.commit()
    db_session.refresh(crawl)
    page = CrawlPage(
        crawl_session_id=crawl.id,
        website_id=website.id,
        url=f"{website.url}/a",
        normalized_url=f"{website.url}/a",
        status_code=200,
        discovered_at=now,
        created_at=now,
    )
    db_session.add(page)
    seo = SeoAnalysis(crawl_session_id=crawl.id, status="COMPLETED", pages_total=1, pages_analyzed=1, created_at=now)
    db_session.add(seo)
    db_session.commit()
    db_session.refresh(page)
    db_session.refresh(seo)
    page_analysis = SeoPageAnalysis(
        seo_analysis_id=seo.id,
        crawl_page_id=page.id,
        status="COMPLETED",
        score=80,
        created_at=now,
    )
    db_session.add(page_analysis)
    db_session.commit()
    db_session.refresh(page_analysis)
    db_session.add(
        SeoAnalysisIssue(
            seo_analysis_id=seo.id,
            seo_page_analysis_id=page_analysis.id,
            crawl_page_id=page.id,
            family="title",
            criterion="presence",
            severity="critical",
            code="title_missing",
            message="Title absent.",
            created_at=now,
        ),
    )
    db_session.add(
        Alert(
            source_type="monitoring",
            category="sync",
            severity="Critical",
            status="Active",
            title="Erreur critique",
            message="Une erreur critique est active.",
            deduplication_key="test-critical",
            metadata_={"website_id": website.id},
            first_seen_at=now,
            last_seen_at=now,
        ),
    )
    db_session.commit()
    return website


def test_dashboard_v2_service_returns_empty_overview(db_session: Session) -> None:
    """Dashboard V2 returns stable empty health when no website exists."""

    overview = _service(db_session).overview()

    assert overview.global_health.score is None
    assert overview.global_health.status == "unavailable"
    assert overview.top_websites == []


def test_dashboard_v2_service_scores_health_and_recommendations(db_session: Session) -> None:
    """Dashboard V2 computes health in the service and returns deterministic recommendations."""

    website = _seo_data(db_session)

    overview = _service(db_session).overview(DashboardV2Filters(website_id=website.id))

    assert overview.seo.critical_issues == 1
    assert overview.global_health.score is not None
    assert overview.top_websites[0].active_alerts == 1
    assert {item.type for item in overview.top_recommendations} >= {"seo_critical", "active_alert"}


def test_dashboard_v2_service_requires_custom_dates(db_session: Session) -> None:
    """Custom period requires explicit start and end dates."""

    with pytest.raises(HTTPException) as exc_info:
        _service(db_session).overview(DashboardV2Filters(period=DashboardV2Period.CUSTOM))

    assert exc_info.value.status_code == 422


def test_dashboard_v2_consumes_geo_intelligence_summary_and_history(db_session: Session) -> None:
    website = _website(db_session)
    db_session.add(
        GeoVisibilitySnapshot(
            website_id=website.id,
            provider="chatgpt",
            prompt="Prompt",
            entity="Marque",
            visibility_score=40,
            citation_count=2,
            source_count=2,
            answer_hash="d" * 64,
            captured_at=datetime(2026, 7, 10, 10, tzinfo=UTC),
        ),
    )
    db_session.commit()

    service = _service(db_session)
    overview = service.overview(DashboardV2Filters(website_id=website.id))
    trends = service.trends(filters=DashboardV2Filters(website_id=website.id))

    assert overview.geo_intelligence.captures == 1
    assert overview.geo_intelligence.average_visibility_score == 40
    assert any(source.source.value == "geo_intelligence" and source.available for source in overview.sources)
    assert any(series.metric.value == "geo_visibility_score" for series in trends.series)
