"""Tests for the GEO Intelligence SQLAlchemy model."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models import GeoVisibilitySnapshot, Website


def test_geo_visibility_snapshot_constraints_and_relationship(db_session: Session) -> None:
    website = Website(name="GEO Model", url="https://geo-model.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    captured_at = datetime(2026, 7, 20, 10, tzinfo=UTC)
    snapshot = GeoVisibilitySnapshot(
        website_id=website.id,
        provider="chatgpt",
        prompt="Quelle marque recommandez-vous ?",
        entity="Marque",
        visibility_score=42,
        citation_count=2,
        source_count=2,
        ranking=1,
        answer_hash="a" * 64,
        captured_at=captured_at,
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)

    assert snapshot.website == website
    assert snapshot.visibility_score == 42

    duplicate = GeoVisibilitySnapshot(
        website_id=website.id,
        provider="chatgpt",
        prompt=snapshot.prompt,
        entity=snapshot.entity,
        visibility_score=50,
        citation_count=0,
        source_count=0,
        answer_hash="a" * 64,
        captured_at=captured_at,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_geo_visibility_snapshot_rejects_out_of_range_score(db_session: Session) -> None:
    website = Website(name="Invalid GEO", url="https://invalid-geo.example", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.add(
        GeoVisibilitySnapshot(
            website_id=website.id,
            provider="gemini",
            prompt="Prompt",
            entity="Entity",
            visibility_score=101,
            citation_count=0,
            source_count=0,
            answer_hash="b" * 64,
            captured_at=datetime(2026, 7, 20, tzinfo=UTC),
        ),
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
