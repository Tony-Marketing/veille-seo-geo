"""Google Analytics 4 processing handler."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.google_analytics import GoogleAnalyticsImportRequest
from backend.app.services.google_analytics import GoogleAnalyticsService


class GoogleAnalyticsProcessingHandler:
    """Run a GA4 import through the existing Google Analytics service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the GA4 processing job."""

        try:
            request = GoogleAnalyticsImportRequest(
                property_id=int_payload(payload, "target_id"),
                start_date=self._date(payload.get("start_date"), default_offset_days=1),
                end_date=self._date(payload.get("end_date"), default_offset_days=1),
            )
            result = GoogleAnalyticsService(GoogleAnalyticsRepository(db)).run_manual_import(request)
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
            "Import Google Analytics termine.",
            {"import_id": result.id, "imported_rows": result.imported_rows, "status": result.status.value},
        )

    def _date(self, value: object, *, default_offset_days: int) -> datetime.date:
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        if value is not None and hasattr(value, "isoformat"):
            return datetime.fromisoformat(value.isoformat()).date()
        return (datetime.now(UTC) - timedelta(days=default_offset_days)).date()
