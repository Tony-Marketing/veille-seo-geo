"""Tests de la page Desktop Orchestrateur."""

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication
from ui import orchestration_page as page_module


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


class FakeOrchestrationService:
    """Fake Desktop service for page tests."""

    def __init__(self, _api_client: object) -> None:
        self.scheduler_runs = 0

    def get_summary(self) -> object:
        return type("Payload", (), {"data": {"pending": 1, "running": 0, "failed": 0, "active_workers": 1}})()

    def list_jobs(self, **_kwargs: object) -> object:
        return type(
            "Payload",
            (),
            {
                "items": [
                    {
                        "id": 1,
                        "job_type": "gsc",
                        "status": "pending",
                        "schedule_id": 1,
                        "attempts": 0,
                        "max_attempts": 3,
                        "message": "Job cree.",
                    },
                ],
            },
        )()

    def list_job_logs(self, _job_id: int) -> object:
        return type("Payload", (), {"items": [{"level": "info", "event": "created", "message": "Cree."}]})()

    def retry_job(self, _job_id: int) -> object:
        return type("Payload", (), {"data": {"id": 1, "status": "retry_scheduled"}})()

    def cancel_job(self, _job_id: int) -> object:
        return type("Payload", (), {"data": {"id": 1, "status": "cancelled"}})()

    def run_scheduler_once(self) -> object:
        self.scheduler_runs += 1
        return type("Payload", (), {"data": {"created": 1, "skipped": 0}})()


@pytest.fixture()
def patched_service(monkeypatch: pytest.MonkeyPatch, qt_app: QApplication) -> Iterator[None]:
    """Replace the REST service with a fake service."""

    assert qt_app is not None
    monkeypatch.setattr(page_module, "OrchestrationService", FakeOrchestrationService)
    yield


def test_orchestration_page_loads_jobs_and_logs(patched_service: None) -> None:
    """The page displays summary, jobs and selected logs."""

    page = page_module.OrchestrationPage(object())
    try:
        assert page.cards["pending"].text() == "1"
        assert page.jobs_table.rowCount() == 1

        page.jobs_table.selectRow(0)
        page.load_selected_logs()

        assert page.logs_table.rowCount() == 1
        assert page.logs_table.item(0, 1).text() == "created"
    finally:
        page.close()


def test_orchestration_page_actions_call_service(patched_service: None) -> None:
    """The page exposes scheduler, retry and cancel actions."""

    page = page_module.OrchestrationPage(object())
    try:
        page.jobs_table.selectRow(0)
        page.run_scheduler_once()
        page.retry_selected()
        page.cancel_selected()

        assert page.jobs_table.rowCount() == 1
        assert "a jour" in page.message.text() or "annule" in page.message.text()
    finally:
        page.close()
