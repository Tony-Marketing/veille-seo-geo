"""Tests for GeoIntelligenceService business behavior."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.schemas.geo_intelligence import (
    GeoVisibilityFilters,
    GeoVisibilityImportItem,
    GeoVisibilityImportRequest,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.geo_intelligence import GeoIntelligenceService


def _service(db_session: Session) -> GeoIntelligenceService:
    return GeoIntelligenceService(GeoIntelligenceRepository(db_session))


def _observation(
    website_id: int,
    provider: str,
    day: int,
    score: float,
    citations: int,
    sources: int,
    hash_character: str,
) -> GeoVisibilityImportItem:
    return GeoVisibilityImportItem(
        website_id=website_id,
        provider=provider,
        prompt="meilleure agence seo",
        entity="A.P&Partner",
        visibility_score=score,
        citation_count=citations,
        source_count=sources,
        answer_hash=hash_character * 64,
        captured_at=datetime(2026, 7, day, 9, tzinfo=UTC),
    )


def test_import_is_idempotent_and_score_is_validated(db_session: Session) -> None:
    website = Website(name="Import GEO", url="https://geo-import.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    service = _service(db_session)
    request = GeoVisibilityImportRequest(
        observations=[_observation(website.id, "ChatGPT", 19, 45, 2, 2, "a")],
    )

    first = service.import_observations(request)
    second = service.import_observations(request)

    assert (first.received, first.created, first.duplicates) == (1, 1, 0)
    assert (second.received, second.created, second.duplicates) == (1, 0, 1)
    assert first.items[0].provider == "chatgpt"
    with pytest.raises(ValidationError):
        _observation(website.id, "gemini", 20, 100.1, 0, 0, "b")


def test_summary_history_comparisons_and_recommendation_rules(db_session: Session) -> None:
    website = Website(name="Rules GEO", url="https://geo-rules.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    service = _service(db_session)
    service.import_observations(
        GeoVisibilityImportRequest(
            observations=[
                _observation(website.id, "chatgpt", 19, 60, 10, 3, "a"),
                _observation(website.id, "gemini", 19, 45, 2, 2, "b"),
                _observation(website.id, "chatgpt", 20, 20, 5, 1, "c"),
            ],
        ),
    )

    summary = service.summary(filters=GeoVisibilityFilters(website_id=website.id))
    history = service.history(filters=GeoVisibilityFilters(website_id=website.id))
    signals = service.recommendation_signals()
    rules = {(signal.provider, signal.rule_code) for signal in signals}

    assert summary.captures == 3
    assert summary.average_visibility_score == pytest.approx(41.67)
    assert summary.providers_covered == ["chatgpt", "gemini"]
    assert len(summary.by_provider) == 2
    assert len(history.points) == 3
    assert ("chatgpt", "low_visibility") in rules
    assert ("chatgpt", "significant_decrease") in rules
    assert ("chatgpt", "citation_loss") in rules
    assert ("chatgpt", "insufficient_source_diversity") in rules
    assert ("gemini", "provider_absence") in rules

    listing = service.list_snapshots(
        PaginationParams(page=1, page_size=2, sort="captured_at", order="desc"),
        filters=GeoVisibilityFilters(provider="chatgpt"),
    )
    assert listing.total == 2
    assert listing.pages == 1


def test_service_accepts_an_injected_connector_without_executing_it(db_session: Session) -> None:
    class FakeConnector:
        provider = "custom-provider"
        configured = True

        def collect(self) -> list[GeoVisibilityImportItem]:
            raise AssertionError("Le registre ne doit pas executer le connecteur.")

    service = GeoIntelligenceService(
        GeoIntelligenceRepository(db_session),
        connectors={"custom-provider": FakeConnector()},
    )

    providers = {item.provider: item.configured for item in service.providers().providers}

    assert providers["custom-provider"] is True
    assert providers["chatgpt"] is False
