"""Tests for GeoIntelligenceRepository."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.repositories.geo_intelligence import GeoIntelligenceRepository
from backend.app.schemas.geo_intelligence import GeoVisibilityFilters, GeoVisibilityImportItem
from backend.app.schemas.pagination import PaginationParams


def _item(website_id: int, provider: str, score: float, hash_character: str) -> GeoVisibilityImportItem:
    return GeoVisibilityImportItem(
        website_id=website_id,
        provider=provider,
        prompt="Prompt marque",
        entity="Marque",
        visibility_score=score,
        citation_count=1,
        source_count=2,
        answer_hash=hash_character * 64,
        captured_at=datetime(2026, 7, 20, 10, tzinfo=UTC),
    )


def test_repository_filters_paginates_and_whitelists_sort(db_session: Session) -> None:
    website = Website(name="Repository GEO", url="https://geo-repository.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    repository = GeoIntelligenceRepository(db_session)
    repository.add_pending(_item(website.id, "chatgpt", 20, "a"))
    repository.add_pending(_item(website.id, "gemini", 80, "b"))
    repository.commit()

    items, total = repository.list_snapshots(
        PaginationParams(page=1, page_size=1, sort="visibility_score", order="desc"),
        filters=GeoVisibilityFilters(website_id=website.id, search="marque"),
    )

    assert total == 2
    assert [item.provider for item in items] == ["gemini"]
    assert repository.find_exact(_item(website.id, "chatgpt", 20, "a")) is not None

    with pytest.raises(ValueError, match="non autorise"):
        repository.list_snapshots(
            PaginationParams(sort="unknown"),
            filters=GeoVisibilityFilters(),
        )
