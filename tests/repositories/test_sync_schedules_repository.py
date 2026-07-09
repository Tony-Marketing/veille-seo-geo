"""Tests for synchronization schedule repository."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.pagination import PaginationParams


def _payload(name: str = "Import GSC", *, sync_type: str = "GSC", is_active: bool = True) -> dict[str, object]:
    return {
        "name": name,
        "description": "Planification de test",
        "sync_type": sync_type,
        "frequency": "Quotidien",
        "status": "Active" if is_active else "Desactivee",
        "is_active": is_active,
        "target_id": "target",
        "target_type": "test",
        "next_run_at": datetime(2026, 7, 10, 8, 0, tzinfo=UTC) if is_active else None,
        "timezone": "Europe/Paris",
    }


def test_sync_schedule_repository_creates_lists_updates_and_disables(db_session: Session) -> None:
    """The repository persists, lists, updates and soft-disables schedules."""

    repository = SyncScheduleRepository(db_session)
    schedule = repository.create_schedule(_payload())
    updated = repository.update_schedule(schedule, {"name": "Import GSC matin"})
    disabled = repository.disable_schedule(updated, {"is_active": False, "status": "Desactivee", "next_run_at": None})
    items, total = repository.list_schedules(PaginationParams())

    assert schedule.id is not None
    assert updated.name == "Import GSC matin"
    assert disabled.is_active is False
    assert disabled.next_run_at is None
    assert total == 1
    assert items == [disabled]
    assert repository.get_schedule(schedule.id) == disabled


def test_sync_schedule_repository_filters_searches_paginates_and_sorts(db_session: Session) -> None:
    """The repository applies filters, search, pagination and whitelisted sort fields."""

    repository = SyncScheduleRepository(db_session)
    first = repository.create_schedule(_payload("Import GSC", sync_type="GSC"))
    repository.create_schedule(_payload("Import GA4", sync_type="GA4", is_active=False))

    items, total = repository.list_schedules(
        PaginationParams(page=1, page_size=1, search="GSC", sort="name", order="asc"),
        sync_type="GSC",
        frequency="Quotidien",
        status="Active",
        is_active=True,
    )

    assert total == 1
    assert items == [first]


def test_sync_schedule_repository_rejects_unknown_sort(db_session: Session) -> None:
    """The repository rejects arbitrary sort fields."""

    repository = SyncScheduleRepository(db_session)

    try:
        repository.list_schedules(PaginationParams(sort="not_allowed"))
    except ValueError as exc:
        assert "non autorise" in str(exc)
    else:
        raise AssertionError("Unknown sort should be rejected.")

