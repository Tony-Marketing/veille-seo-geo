"""Tests for GEO analysis service."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models import (
    CrawlPage,
    CrawlSession,
    GeoRecommendation,
    SeoAnalysis,
    SeoAnalysisIssue,
    SeoPageAnalysis,
)
from backend.app.repositories.geo_analysis import GeoAnalysisRepository
from backend.app.schemas.geo_analysis import GeoAnalysisCreate, GeoAnalysisStatus
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.geo.engine import GeoAnalysisEngine
from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED, GeoProvider, GeoProviderResponse
from backend.app.services.geo_analysis import GeoAnalysisService


class FakeProvider(GeoProvider):
    """Provider returning deterministic normalized data."""

    name = "fake"

    def analyze(self, prompt: str, context: object) -> GeoProviderResponse:
        return GeoProviderResponse(
            provider_name=self.name,
            model_name="fake-model",
            status=PROVIDER_STATUS_COMPLETED,
            raw_response="{}",
            normalized_response={
                "summary": "Page exploitable.",
                "geo_signals": {"clarity": 90, "citability": 70},
                "llm_signals": {"extractability": 80, "entity_coverage": 60},
                "recommendations": [
                    {
                        "type": "editorial",
                        "severity": "major",
                        "priority": 1,
                        "title": "Clarifier le contenu",
                        "description": "Ajouter une synthese en haut de page.",
                    },
                ],
            },
        )


def _source_data(db_session: Session, *, seo_status: str = "COMPLETED") -> tuple[CrawlSession, SeoAnalysis]:
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
        final_url="https://example.com/",
        final_normalized_url="https://example.com/",
        depth=0,
        status_code=200,
        content_type="text/html",
        raw_html="<html><body><h1>Example</h1></body></html>",
        discovered_at=datetime.now(UTC),
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)

    seo_analysis = SeoAnalysis(crawl_session_id=crawl.id, status=seo_status, progress_percent=100)
    db_session.add(seo_analysis)
    db_session.commit()
    db_session.refresh(seo_analysis)

    seo_page = SeoPageAnalysis(
        seo_analysis_id=seo_analysis.id,
        crawl_page_id=page.id,
        status="COMPLETED",
        score=75,
        issues_count=1,
    )
    db_session.add(seo_page)
    db_session.commit()
    db_session.refresh(seo_page)

    issue = SeoAnalysisIssue(
        seo_analysis_id=seo_analysis.id,
        seo_page_analysis_id=seo_page.id,
        crawl_page_id=page.id,
        family="title",
        criterion="presence",
        severity="major",
        code="title_missing",
        message="Title absent.",
    )
    db_session.add(issue)
    db_session.commit()
    return crawl, seo_analysis


def _service(db_session: Session) -> GeoAnalysisService:
    engine = GeoAnalysisEngine(providers={"fake": FakeProvider()})
    return GeoAnalysisService(GeoAnalysisRepository(db_session), engine=engine)


def test_geo_analysis_service_creates_pending_analysis(db_session: Session) -> None:
    """The service creates a pending GEO analysis for an existing SEO analysis."""

    _, seo_analysis = _source_data(db_session)

    result = _service(db_session).create(GeoAnalysisCreate(seo_analysis_id=seo_analysis.id, providers=["fake"]))

    assert result.id is not None
    assert result.seo_analysis_id == seo_analysis.id
    assert result.status == GeoAnalysisStatus.PENDING
    assert result.pages_total == 1
    assert result.providers_requested == ["fake"]


def test_geo_analysis_service_rejects_unknown_or_unfinished_seo_analysis(db_session: Session) -> None:
    """Unknown or unfinished SEO analyses are rejected."""

    with pytest.raises(HTTPException) as missing:
        _service(db_session).create(GeoAnalysisCreate(seo_analysis_id=999, providers=["fake"]))

    _, seo_analysis = _source_data(db_session, seo_status="RUNNING")
    with pytest.raises(HTTPException) as unfinished:
        _service(db_session).create(GeoAnalysisCreate(seo_analysis_id=seo_analysis.id, providers=["fake"]))

    assert missing.value.status_code == 404
    assert unfinished.value.status_code == 409


def test_geo_analysis_service_lists_and_gets_analyses(db_session: Session) -> None:
    """The service lists and returns GEO analyses."""

    _, seo_analysis = _source_data(db_session)
    created = _service(db_session).create(GeoAnalysisCreate(seo_analysis_id=seo_analysis.id, providers=["fake"]))

    listed = _service(db_session).list(PaginationParams())
    fetched = _service(db_session).get(created.id)

    assert listed.total == 1
    assert listed.items[0].id == created.id
    assert fetched.id == created.id


def test_geo_analysis_service_runs_analysis_from_persisted_data(db_session: Session) -> None:
    """The service runs GEO analysis without fetching remote pages."""

    _, seo_analysis = _source_data(db_session)
    service = _service(db_session)
    created = service.create(GeoAnalysisCreate(seo_analysis_id=seo_analysis.id, providers=["fake"]))

    result = service.run(created.id)

    assert result.status == GeoAnalysisStatus.COMPLETED
    assert result.progress_percent == 100
    assert result.geo_score == 80
    assert result.llm_score == 70
    assert result.global_score == 75
    assert result.provider_results_count == 1
    assert result.recommendations_count == 1
    assert db_session.query(GeoRecommendation).filter_by(geo_analysis_id=created.id).count() == 1


def test_geo_analysis_service_deletes_analysis(db_session: Session) -> None:
    """The service deletes GEO analyses."""

    _, seo_analysis = _source_data(db_session)
    service = _service(db_session)
    created = service.create(GeoAnalysisCreate(seo_analysis_id=seo_analysis.id, providers=["fake"]))

    service.delete(created.id)

    with pytest.raises(HTTPException) as exc_info:
        service.get(created.id)

    assert exc_info.value.status_code == 404
