"""Tests for synchronization schedule models."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models import SyncSchedule


def test_sync_schedule_model_persists_core_fields(db_session: Session) -> None:
    """The synchronization schedule model stores planning metadata."""

    schedule = SyncSchedule(
        name="Import GSC quotidien",
        description="Import quotidien des donnees Search Console.",
        sync_type="GSC",
        frequency="Quotidien",
        status="Active",
        is_active=True,
        website_id=None,
        target_id="properties/example",
        target_type="gsc_property",
        last_run_at=datetime(2026, 7, 9, 8, 0, tzinfo=UTC),
        last_run_status="Active",
        last_run_message="Derniere execution OK",
        next_run_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
        timezone="Europe/Paris",
    )

    db_session.add(schedule)
    db_session.commit()
    db_session.refresh(schedule)

    assert schedule.id is not None
    assert schedule.sync_type == "GSC"
    assert schedule.frequency == "Quotidien"
    assert schedule.status == "Active"
    assert schedule.next_run_at is not None

