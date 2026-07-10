"""Bing Webmaster Tools processing handler."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.orchestration.base import HandlerResult, int_payload
from backend.app.repositories.bing_webmaster_tools import BingWebmasterToolsRepository
from backend.app.schemas.bing_webmaster_tools import BingWebmasterImportRequest
from backend.app.services.bing_webmaster_tools import BingWebmasterToolsService


class BingWebmasterProcessingHandler:
    """Run a Bing import through the existing Bing service."""

    def run(self, payload: dict[str, object], db: Session) -> HandlerResult:
        """Execute the Bing processing job."""

        try:
            request = BingWebmasterImportRequest(
                connection_id=int_payload(payload, "target_id"),
                bing_site_id=self._optional_int(payload.get("bing_site_id")),
                date_from=self._date(payload.get("date_from"), default_offset_days=1),
                date_to=self._date(payload.get("date_to"), default_offset_days=1),
                import_type=str(payload.get("import_type") or "SCHEDULED"),
            )
            result = BingWebmasterToolsService(BingWebmasterToolsRepository(db)).run_manual_import(request)
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
            "Import Bing Webmaster Tools termine.",
            {"import_id": result.id, "items_processed": result.items_processed, "status": result.status.value},
        )

    def _date(self, value: object, *, default_offset_days: int) -> datetime.date:
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        if value is not None and hasattr(value, "isoformat"):
            return datetime.fromisoformat(value.isoformat()).date()
        return (datetime.now(UTC) - timedelta(days=default_offset_days)).date()

    def _optional_int(self, value: object) -> int | None:
        if value is None or value == "":
            return None
        parsed = int(value)
        return parsed if parsed > 0 else None
