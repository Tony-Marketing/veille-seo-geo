"""Tests for Dashboard V2 repository."""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy.orm import Session

from backend.app.models import (
    BingWebmasterMetric,
    BingWebmasterSite,
    CrawlPage,
    CrawlSession,
    GeoAnalysis,
    GoogleAnalyticsMetric,
    GoogleAnalyticsProperty,
    GoogleSearchConsolePerformance,
    GoogleSearchConsoleProperty,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
    Website,
)
from backend.app.repositories.dashboard_v2 import DashboardV2Repository
from backend.app.schemas.pagination import PaginationParams


def _website(db_session: Session) -> Website:
    website = Website(name="Example", url="https://example.com", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.refresh(website)
    return website


def _source_data(db_session: Session) -> Website:
    website = _website(db_session)
    now = datetime(2026, 7, 10, tzinfo=UTC)
    crawl = CrawlSession(
        website_id=website.id,
        start_url=website.url,
        normalized_start_url=website.url,
        status="COMPLETED",
        pages_crawled=2,
        pages_failed=1,
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
        status_code=500,
        discovered_at=now,
        created_at=now,
    )
    db_session.add(page)
    seo = SeoAnalysis(crawl_session_id=crawl.id, status="COMPLETED", pages_total=1, pages_analyzed=1, created_at=now)
    db_session.add(seo)
    db_session.commit()
    db_session.refresh(seo)
    db_session.refresh(page)
    db_session.add(SeoPageAnalysis(seo_analysis_id=seo.id, crawl_page_id=page.id, score=80, created_at=now))
    db_session.add(
        SeoAnalysisIssue(
            seo_analysis_id=seo.id,
            crawl_page_id=page.id,
            family="title",
            criterion="presence",
            severity="critical",
            code="title_missing",
            message="Title absent.",
            created_at=now,
        ),
    )
    geo = GeoAnalysis(
        seo_analysis_id=seo.id,
        crawl_session_id=crawl.id,
        status="COMPLETED",
        geo_score=70,
        providers_requested=["fake"],
        created_at=now,
    )
    db_session.add(geo)
    gsc_property = GoogleSearchConsoleProperty(
        website_id=website.id,
        google_property_id="sc-domain:example.com",
        property_url=website.url,
        is_active=True,
    )
    ga4_property = GoogleAnalyticsProperty(
        website_id=website.id,
        property_id="123",
        property_name="Example",
        enabled=True,
    )
    bing_site = BingWebmasterSite(connection_id=1, website_id=website.id, site_url=website.url, is_verified=True)
    db_session.add_all([gsc_property, ga4_property, bing_site])
    db_session.commit()
    db_session.refresh(gsc_property)
    db_session.refresh(ga4_property)
    db_session.refresh(bing_site)
    metric_date = date(2026, 7, 10)
    db_session.add(
        GoogleSearchConsolePerformance(
            property_id=gsc_property.id,
            date=metric_date,
            clicks=10,
            impressions=100,
            ctr=0.1,
            position=4,
        ),
    )
    db_session.add(
        GoogleAnalyticsMetric(
            property_id=ga4_property.id,
            date=metric_date,
            sessions=50,
            users=40,
            engagement_rate=0.7,
        ),
    )
    db_session.add(
        BingWebmasterMetric(
            bing_site_id=bing_site.id,
            date=metric_date,
            clicks=5,
            impressions=50,
            ctr=0.1,
            average_position=8,
        ),
    )
    db_session.commit()
    return website


def test_dashboard_v2_repository_aggregates_sources(db_session: Session) -> None:
    """Repository returns read-only aggregates from existing tables."""

    website = _source_data(db_session)
    repository = DashboardV2Repository(db_session)
    start = datetime(2026, 7, 1, tzinfo=UTC)
    end = datetime(2026, 7, 31, tzinfo=UTC)
    start_date = date(2026, 7, 1)
    end_date = date(2026, 7, 31)

    websites, total = repository.list_websites(PaginationParams(), search="Example")
    crawl = repository.crawl_aggregates([website.id], start=start, end=end)[website.id]
    seo = repository.seo_aggregates([website.id], start=start, end=end)[website.id]
    gsc = repository.gsc_aggregates([website.id], start_date=start_date, end_date=end_date)[website.id]
    ga4 = repository.ga4_aggregates([website.id], start_date=start_date, end_date=end_date)[website.id]
    bing = repository.bing_aggregates([website.id], start_date=start_date, end_date=end_date)[website.id]

    assert total == 1
    assert websites[0].id == website.id
    assert crawl["pages_failed"] == 1
    assert seo["critical_issues"] == 1
    assert gsc["clicks"] == 10
    assert ga4["sessions"] == 50
    assert bing["impressions"] == 50


def test_dashboard_v2_repository_rejects_unknown_website_sort(db_session: Session) -> None:
    """Repository sort fields are whitelisted."""

    repository = DashboardV2Repository(db_session)

    with pytest.raises(ValueError):
        repository.list_websites(PaginationParams(sort="health_score"))
