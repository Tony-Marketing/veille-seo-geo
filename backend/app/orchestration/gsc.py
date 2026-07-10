"""Google Search Console processing handler."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import GoogleSearchConsoleManualImportRequest
from backend.app.services.google_search_console import GoogleSearchConsoleService


class GoogleSearchConsoleProcessingHandler:
    """Run a GSC import through the existing GSC service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the GSC processing job."""

        try:
            request = GoogleSearchConsoleManualImportRequest(
                property_id=int_payload(payload, "target_id"),
                start_date=self._date(payload.get("start_date"), default_offset_days=1),
                end_date=self._date(payload.get("end_date"), default_offset_days=1),
                dimensions=[str(item) for item in payload.get("dimensions", ["query", "page"])],
                search_type=str(payload.get("search_type") or "web"),
            )
            result = GoogleSearchConsoleService(GoogleSearchConsoleRepository(db)).run_manual_import(request)
        except HTTPException as exc:
            return HandlerResult(
                False,
                str(exc.detail),
                {"status_code": exc.status_code},
                retryable=exc.status_code >= 500,
            )
        except ValueError as exc:
            return HandlerResult(False, str(exc), retryable=False)
        return HandlerResult(
            True,
            "Import Google Search Console termine.",
            {"import_id": result.id, "rows_imported": result.rows_imported, "status": result.status.value},
        )

    def _date(self, value: object, *, default_offset_days: int) -> datetime.date:
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        if value is not None and hasattr(value, "isoformat"):
            return datetime.fromisoformat(value.isoformat()).date()
        return (datetime.now(UTC) - timedelta(days=default_offset_days)).date()
