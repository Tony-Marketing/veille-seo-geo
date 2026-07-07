"""Tests for Google Search Console repository."""

from datetime import date

from sqlalchemy.orm import Session

from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportFilters,
    GoogleSearchConsolePerformanceFilters,
)
from backend.app.schemas.pagination import PaginationParams


def test_google_search_console_repository_upserts_properties(db_session: Session) -> None:
    """The repository creates and updates properties by site URL."""

    repository = GoogleSearchConsoleRepository(db_session)

    created, was_created = repository.upsert_property(
        {
            "site_url": "https://example.com/",
            "property_type": "URL_PREFIX",
            "permission_level": "siteOwner",
            "status": "ACTIVE",
        },
    )
    updated, was_created_again = repository.upsert_property(
        {
            "site_url": "https://example.com/",
            "property_type": "URL_PREFIX",
            "permission_level": "siteFullUser",
            "status": "ACTIVE",
        },
    )

    assert was_created is True
    assert was_created_again is False
    assert updated.id == created.id
    assert updated.permission_level == "siteFullUser"
    assert repository.count() == 1


def test_google_search_console_repository_upserts_and_lists_performances(db_session: Session) -> None:
    """The repository keeps performance imports idempotent."""

    repository = GoogleSearchConsoleRepository(db_session)
    gsc_property = repository.create({"site_url": "https://example.com/"})
    payload = {
        "property_id": gsc_property.id,
        "date": date(2026, 7, 1),
        "page": "https://example.com/",
        "query": "example",
        "country": "fra",
        "device": "DESKTOP",
        "clicks": 10,
        "impressions": 100,
        "ctr": 0.1,
        "position": 3.2,
    }

    created, was_created = repository.upsert_performance(payload)
    updated, was_created_again = repository.upsert_performance({**payload, "clicks": 15})
    items, total = repository.list_performances(
        GoogleSearchConsolePerformanceFilters(property_id=gsc_property.id, start_date=date(2026, 7, 1)),
        PaginationParams(),
    )

    assert was_created is True
    assert was_created_again is False
    assert updated.id == created.id
    assert updated.clicks == 15
    assert total == 1
    assert items == [updated]


def test_google_search_console_repository_persists_import_history(db_session: Session) -> None:
    """The repository stores and filters import history."""

    repository = GoogleSearchConsoleRepository(db_session)
    gsc_property = repository.create({"site_url": "https://example.com/"})
    item = repository.create_import(
        {
            "property_id": gsc_property.id,
            "import_type": "performance",
            "status": "RUNNING",
        },
    )

    updated = repository.update_import(item, {"status": "COMPLETED", "items_processed": 4})
    items, total = repository.list_imports(
        GoogleSearchConsoleImportFilters(property_id=gsc_property.id, status="COMPLETED"),
        PaginationParams(),
    )

    assert updated.status == "COMPLETED"
    assert updated.items_processed == 4
    assert total == 1
    assert items == [updated]
