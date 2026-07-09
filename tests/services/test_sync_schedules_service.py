"""Tests for synchronization schedule service."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.repositories.sync_schedules import SyncScheduleRepository
from backend.app.schemas.pagination import PaginationParams
from backend.app.schemas.sync_schedules import (
    SyncFrequency,
    SyncScheduleCreate,
    SyncScheduleFilters,
    SyncScheduleUpdate,
    SyncType,
)
from backend.app.services.sync_schedules import SyncScheduleService


def _now() -> datetime:
    return datetime(2026, 7, 9, 8, 0, tzinfo=UTC)


def _service(db_session: Session) -> SyncScheduleService:
    return SyncScheduleService(SyncScheduleRepository(db_session), now_provider=_now)


def test_sync_schedule_service_creates_schedule_and_calculates_next_run(db_session: Session) -> None:
    """The service creates schedules and computes next_run_at."""

    service = _service(db_session)

    created = service.create_schedule(
        SyncScheduleCreate(name="Import GSC", sync_type=SyncType.GSC, frequency=SyncFrequency.DAILY),
        user_id=1,
    )

    assert created.status == "Active"
    assert created.is_active is True
    assert created.next_run_at == datetime(2026, 7, 10, 8, 0)
    assert created.created_by_user_id == 1
    assert created.updated_by_user_id == 1


def test_sync_schedule_service_handles_manual_and_disabled_schedules(db_session: Session) -> None:
    """Manual or disabled schedules do not receive automatic next_run_at."""

    service = _service(db_session)
    manual = service.create_schedule(
        SyncScheduleCreate(name="Import manuel", sync_type=SyncType.GA4, frequency=SyncFrequency.MANUAL),
    )
    disabled = service.create_schedule(
        SyncScheduleCreate(
            name="Import desactive",
            sync_type=SyncType.BING,
            frequency=SyncFrequency.HOURLY,
            is_active=False,
        ),
    )

    assert manual.status == "En attente"
    assert manual.next_run_at is None
    assert disabled.status == "Desactivee"
    assert disabled.next_run_at is None


def test_sync_schedule_service_updates_enables_disables_and_soft_deletes(db_session: Session) -> None:
    """The service manages activation transitions without deleting schedules."""

    service = _service(db_session)
    created = service.create_schedule(
        SyncScheduleCreate(name="Import GSC", sync_type=SyncType.GSC, frequency=SyncFrequency.DAILY),
    )

    updated = service.update_schedule(
        created.id,
        SyncScheduleUpdate(frequency=SyncFrequency.WEEKLY, last_run_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC)),
        user_id=2,
    )
    disabled = service.disable_schedule(created.id, user_id=3)
    enabled = service.enable_schedule(created.id, user_id=4)
    service.delete_schedule(created.id, user_id=5)
    stored = service.get_schedule(created.id)

    assert updated.frequency == "Hebdomadaire"
    assert updated.next_run_at == datetime(2026, 7, 15, 8, 0)
    assert disabled.status == "Desactivee"
    assert disabled.next_run_at is None
    assert enabled.is_active is True
    assert enabled.next_run_at == datetime(2026, 7, 15, 8, 0)
    assert stored.is_active is False
    assert stored.updated_by_user_id == 5


def test_sync_schedule_service_calculates_month_end() -> None:
    """Monthly schedules keep valid calendar dates."""

    service = SyncScheduleService(SyncScheduleRepository.__new__(SyncScheduleRepository), now_provider=_now)
    next_run = service.calculate_next_run(
        frequency=SyncFrequency.MONTHLY,
        is_active=True,
        last_run_at=datetime(2026, 1, 31, 8, 0, tzinfo=UTC),
        reference_at=_now(),
    )

    assert next_run == datetime(2026, 2, 28, 8, 0, tzinfo=UTC)


def test_sync_schedule_service_validates_filters_and_sort(db_session: Session) -> None:
    """The service validates filter dates and converts repository sort errors."""

    service = _service(db_session)

    with pytest.raises(HTTPException) as invalid_period:
        service.list_schedules(
            PaginationParams(),
            filters=SyncScheduleFilters(
                next_run_from=datetime(2026, 7, 10, tzinfo=UTC),
                next_run_to=datetime(2026, 7, 9, tzinfo=UTC),
            ),
        )
    with pytest.raises(HTTPException) as invalid_sort:
        service.list_schedules(PaginationParams(sort="not_allowed"))

    assert invalid_period.value.status_code == 422
    assert invalid_sort.value.status_code == 422
