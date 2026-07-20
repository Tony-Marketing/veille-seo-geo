"""Tests for RecommendationRepository."""

from sqlalchemy.orm import Session

from backend.app.models import Website
from backend.app.repositories.recommendations import RecommendationRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.recommendations import RecommendationFilters, RecommendationPriority


def _payload(website_id: int, *, key: str, priority: str = "HIGH") -> dict[str, object]:
    return {
        "website_id": website_id,
        "source": "SEO",
        "source_id": key,
        "category": "metadata",
        "title": f"Recommendation {key}",
        "description": "Description actionnable.",
        "priority": priority,
        "impact": "SEO",
        "difficulty": None,
        "score": 80.0,
        "status": "OPEN",
        "deduplication_key": f"{website_id}|SEO|rule|seo_analysis_issue|{key}",
        "metadata_": {"rule_code": "rule"},
    }


def test_recommendation_repository_filters_sorts_and_updates(db_session: Session) -> None:
    """The repository persists, filters and updates recommendations without business calculations."""

    website = Website(name="Example", url="https://repository.example.com", is_active=True)
    db_session.add(website)
    db_session.commit()
    db_session.refresh(website)
    repository = RecommendationRepository(db_session)
    first = repository.add_pending(_payload(website.id, key="1"))
    repository.add_pending(_payload(website.id, key="2", priority="CRITICAL"))
    repository.commit()

    items, total = repository.list_recommendations(
        PaginationParams(page=1, page_size=20, sort="priority", order="desc"),
        filters=RecommendationFilters(website_id=website.id),
    )

    assert total == 2
    assert [item.priority for item in items] == ["CRITICAL", "HIGH"]
    assert items[0].website.name == "Example"

    repository.update_pending(first, {"status": "ACKNOWLEDGED"})
    repository.commit()
    filtered, filtered_total = repository.list_recommendations(
        PaginationParams(),
        filters=RecommendationFilters(priority=RecommendationPriority.HIGH),
    )

    assert filtered_total == 1
    assert filtered[0].status == "ACKNOWLEDGED"
    assert repository.get_by_deduplication_key(first.deduplication_key) is not None
