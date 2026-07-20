"""Tests for RecommendationService."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models import Alert, CrawlSession, MonitoringEvent, SeoAnalysis, SeoAnalysisIssue, Website
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.recommendations import (
    RecommendationImpact,
    RecommendationPriority,
    RecommendationSource,
    RecommendationStatus,
)
from backend.app.services.recommendations import RecommendationCandidate, RecommendationService


def _service(db_session: Session) -> RecommendationService:
    return RecommendationService(RecommendationRepository(db_session))


def test_recommendation_service_consolidates_deduplicates_and_prioritizes(db_session: Session) -> None:
    """Persisted SEO issues are normalized once with a deterministic priority and key."""

    website = Website(name="Example", url="https://service.example.com", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.refresh(website)
    crawl = CrawlSession(
        website_id=website.id,
        start_url=website.url,
        normalized_start_url=website.url,
        status="COMPLETED",
    )
    db_session.add(crawl)
    db_session.commit()
    db_session.refresh(crawl)
    analysis = SeoAnalysis(crawl_session_id=crawl.id, status="COMPLETED")
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)
    issue = SeoAnalysisIssue(
        seo_analysis_id=analysis.id,
        family="metadata",
        criterion="title",
        severity="critical",
        code="title_missing",
        message="Title absent.",
    )
    db_session.add(issue)
    db_session.commit()

    service = _service(db_session)
    first = service.list_recommendations(PaginationParams())
    second = service.list_recommendations(PaginationParams())

    assert first.total == second.total == 1
    assert first.items[0].priority == "CRITICAL"
    assert first.items[0].source == "SEO"
    assert first.items[0].website_id == website.id
    assert first.items[0].metadata["rule_code"] == "title_missing"


def test_recommendation_service_preserves_lifecycle_and_avoids_monitoring_alert_duplicate(
    db_session: Session,
) -> None:
    """Status survives consolidation and an alert supersedes its direct monitoring event."""

    event_id = uuid4()
    now = datetime(2026, 7, 20, tzinfo=UTC)
    db_session.add(
        MonitoringEvent(
            id=event_id,
            event_type="sync",
            severity="critical",
            source="scheduler",
            message="Synchronisation echouee.",
            created_at=now,
        ),
    )
    db_session.add(
        Alert(
            source_type="monitoring",
            source_id=str(event_id),
            category="sync",
            severity="Critical",
            status="Active",
            title="Synchronisation echouee",
            message="Relancer la synchronisation.",
            deduplication_key="monitoring-sync-test",
            first_seen_at=now,
            last_seen_at=now,
        ),
    )
    db_session.commit()

    service = _service(db_session)
    result = service.list_recommendations(PaginationParams())

    assert result.total == 1
    assert result.items[0].source == "ALERTS"
    updated = service.update_status(result.items[0].id, RecommendationStatus.ACKNOWLEDGED)
    assert updated.status == "ACKNOWLEDGED"

    refreshed = service.list_recommendations(PaginationParams())
    assert refreshed.items[0].status == "ACKNOWLEDGED"


def test_recommendation_deduplication_key_ignores_presentation_text() -> None:
    """The business key depends only on validated stable identity components."""

    values = {
        "website_id": 7,
        "source": RecommendationSource.SEO,
        "rule_code": "title_missing",
        "source_object_type": "seo_analysis_issue",
        "source_object_id": "42",
        "category": "metadata",
        "description": "Description A",
        "priority": RecommendationPriority.HIGH,
        "impact": RecommendationImpact.SEO,
        "score": 80.0,
    }
    first = RecommendationCandidate(title="Titre A", **values)
    second = RecommendationCandidate(title="Titre B", **{**values, "description": "Description B"})

    assert RecommendationService.deduplication_key(first) == RecommendationService.deduplication_key(second)
