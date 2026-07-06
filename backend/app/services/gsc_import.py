"""Import service for Google Search Console data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from backend.app.connectors.google_search_console import GoogleSearchConsoleClient
from backend.app.repositories.gsc import GscDataRepository, GscImportRunRepository, GscPropertyRepository
from backend.app.schemas.gsc import GscImportRunCreate, GscImportRunRead, GscImportStatus


class GoogleSearchConsoleImportService:
    """Run idempotent GSC imports through a mockable connector."""

    def __init__(
        self,
        property_repository: GscPropertyRepository,
        import_repository: GscImportRunRepository,
        data_repository: GscDataRepository,
        *,
        client: GoogleSearchConsoleClient,
    ) -> None:
        self.property_repository = property_repository
        self.import_repository = import_repository
        self.data_repository = data_repository
        self.client = client

    def run_import(self, payload: GscImportRunCreate) -> GscImportRunRead:
        """Run one synchronous mocked import for the selected property."""

        gsc_property = self.property_repository.get(payload.property_id)
        if gsc_property is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete GSC introuvable.")

        import_run = self.import_repository.create(
            {
                "property_id": payload.property_id,
                "status": GscImportStatus.RUNNING,
                "import_type": payload.import_type,
                "date_start": payload.date_start,
                "date_end": payload.date_end,
                "rows_imported": 0,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "completed_at": None,
            },
        )
        try:
            rows_imported = self._import_all(import_run.id, gsc_property.id, gsc_property.site_url, payload)
        except Exception as exc:  # noqa: BLE001
            failed = self.import_repository.update(
                import_run,
                {
                    "status": GscImportStatus.FAILED,
                    "error_message": str(exc),
                    "completed_at": datetime.now(UTC),
                },
            )
            return GscImportRunRead.model_validate(failed)

        completed = self.import_repository.update(
            import_run,
            {
                "status": GscImportStatus.COMPLETED,
                "rows_imported": rows_imported,
                "completed_at": datetime.now(UTC),
            },
        )
        return GscImportRunRead.model_validate(completed)

    def _import_all(self, import_run_id: int, property_id: int, site_url: str, payload: GscImportRunCreate) -> int:
        rows = 0
        rows += self.data_repository.upsert_performance_rows(
            self._with_import_fields(
                self.client.fetch_performance(site_url, payload.date_start, payload.date_end),
                import_run_id,
                property_id,
            ),
        )
        rows += self.data_repository.upsert_coverage_rows(
            self._with_import_fields(self.client.fetch_coverage(site_url), import_run_id, property_id),
        )
        rows += self.data_repository.upsert_indexing_rows(
            self._with_import_fields(self.client.inspect_urls(site_url), import_run_id, property_id),
        )
        rows += self.data_repository.upsert_sitemaps(
            self._with_import_fields(self.client.list_sitemaps(site_url), import_run_id, property_id),
        )
        return rows

    def _with_import_fields(
        self,
        rows: list[dict[str, Any]],
        import_run_id: int,
        property_id: int,
    ) -> list[dict[str, Any]]:
        return [
            {
                **row,
                "property_id": property_id,
                "import_run_id": import_run_id,
            }
            for row in rows
        ]
