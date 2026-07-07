"""Business service for Google Search Console."""

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.connectors.google_search_console import (
    GoogleSearchConsoleConnector,
    NotConfiguredGoogleSearchConsoleConnector,
)
from backend.app.core.security import encrypt_secret
from backend.app.models import GoogleSearchConsoleProperty
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportList,
    GoogleSearchConsoleImportRead,
    GoogleSearchConsoleImportStatus,
    GoogleSearchConsoleIndexCoverageList,
    GoogleSearchConsoleIndexCoverageRead,
    GoogleSearchConsoleManualImportRequest,
    GoogleSearchConsoleOAuthTokenUpdate,
    GoogleSearchConsolePerformanceList,
    GoogleSearchConsolePerformanceRead,
    GoogleSearchConsolePropertyCreate,
    GoogleSearchConsolePropertyList,
    GoogleSearchConsolePropertyRead,
    GoogleSearchConsolePropertyUpdate,
    GoogleSearchConsoleSitemapList,
    GoogleSearchConsoleSitemapRead,
)
from backend.app.schemas.pagination import PaginationParams


class GoogleSearchConsoleService:
    """Manage Google Search Console properties, data and imports."""

    def __init__(
        self,
        repository: GoogleSearchConsoleRepository,
        *,
        connector: GoogleSearchConsoleConnector | None = None,
    ) -> None:
        self.repository = repository
        self.connector = connector or NotConfiguredGoogleSearchConsoleConnector()

    def list_properties(self, params: PaginationParams) -> GoogleSearchConsolePropertyList:
        """Return paginated Google Search Console properties."""

        items, total = self.repository.list_properties(params)
        return GoogleSearchConsolePropertyList(
            items=[GoogleSearchConsolePropertyRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_remote_properties(self) -> list[GoogleSearchConsolePropertyCreate]:
        """Return properties visible through the injected connector."""

        return [
            GoogleSearchConsolePropertyCreate(
                google_property_id=item.google_property_id,
                property_url=item.property_url,
                property_type=item.property_type,
                display_name=item.display_name,
                permission_level=item.permission_level,
            )
            for item in self.connector.list_properties()
        ]

    def get_property(self, property_id: int) -> GoogleSearchConsolePropertyRead:
        """Return one Google Search Console property."""

        return GoogleSearchConsolePropertyRead.model_validate(self._get_property_model(property_id))

    def create_property(self, payload: GoogleSearchConsolePropertyCreate) -> GoogleSearchConsolePropertyRead:
        """Create a Google Search Console property."""

        existing = self.repository.get_property_by_google_id(payload.google_property_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Propriete Google Search Console deja existante.",
            )
        item = self.repository.create(payload.model_dump())
        return GoogleSearchConsolePropertyRead.model_validate(item)

    def update_property(
        self,
        property_id: int,
        payload: GoogleSearchConsolePropertyUpdate,
    ) -> GoogleSearchConsolePropertyRead:
        """Update a Google Search Console property."""

        item = self._get_property_model(property_id)
        data = payload.model_dump(exclude_unset=True)
        google_property_id = data.get("google_property_id")
        if google_property_id is not None:
            existing = self.repository.get_property_by_google_id(google_property_id)
            if existing is not None and existing.id != property_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Propriete Google Search Console deja existante.",
                )
        return GoogleSearchConsolePropertyRead.model_validate(self.repository.update(item, data))

    def update_oauth_tokens(
        self,
        property_id: int,
        payload: GoogleSearchConsoleOAuthTokenUpdate,
    ) -> GoogleSearchConsolePropertyRead:
        """Store OAuth tokens with the existing encryption mechanism."""

        item = self._get_property_model(property_id)
        data = payload.model_dump(exclude_unset=True)
        if "access_token" in data and data["access_token"] is not None:
            data["encrypted_access_token"] = encrypt_secret(data.pop("access_token"))
        if "refresh_token" in data and data["refresh_token"] is not None:
            data["encrypted_refresh_token"] = encrypt_secret(data.pop("refresh_token"))
        return GoogleSearchConsolePropertyRead.model_validate(self.repository.update(item, data))

    def delete_property(self, property_id: int) -> None:
        """Delete a Google Search Console property."""

        self.repository.delete_property(self._get_property_model(property_id))

    def list_performances(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> GoogleSearchConsolePerformanceList:
        """Return paginated performance rows."""

        items, total = self.repository.list_performances(params, property_id=property_id)
        return GoogleSearchConsolePerformanceList(
            items=[GoogleSearchConsolePerformanceRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_index_coverages(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> GoogleSearchConsoleIndexCoverageList:
        """Return paginated index coverage rows."""

        items, total = self.repository.list_index_coverages(params, property_id=property_id)
        return GoogleSearchConsoleIndexCoverageList(
            items=[GoogleSearchConsoleIndexCoverageRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_sitemaps(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> GoogleSearchConsoleSitemapList:
        """Return paginated sitemap rows."""

        items, total = self.repository.list_sitemaps(params, property_id=property_id)
        return GoogleSearchConsoleSitemapList(
            items=[GoogleSearchConsoleSitemapRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_imports(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> GoogleSearchConsoleImportList:
        """Return paginated import logs."""

        items, total = self.repository.list_imports(params, property_id=property_id)
        return GoogleSearchConsoleImportList(
            items=[GoogleSearchConsoleImportRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def run_manual_import(self, payload: GoogleSearchConsoleManualImportRequest) -> GoogleSearchConsoleImportRead:
        """Run an idempotent manual import through the injected connector."""

        if payload.end_date < payload.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )

        property_item = self._get_property_model(payload.property_id)
        import_log = self.repository.create_import(
            {
                "property_id": property_item.id,
                "import_type": "MANUAL",
                "status": GoogleSearchConsoleImportStatus.RUNNING,
                "start_date": payload.start_date,
                "end_date": payload.end_date,
                "dimensions": self._normalize_dimensions(payload.dimensions),
                "rows_requested": 0,
                "rows_imported": 0,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "completed_at": None,
            },
        )

        try:
            rows_imported = self._import_property_data(property_item, import_log.id, payload)
            import_log = self.repository.update_import(
                import_log,
                {
                    "status": GoogleSearchConsoleImportStatus.COMPLETED,
                    "rows_imported": rows_imported,
                    "completed_at": datetime.now(UTC),
                },
            )
        except Exception as exc:  # noqa: BLE001
            import_log = self.repository.update_import(
                import_log,
                {
                    "status": GoogleSearchConsoleImportStatus.FAILED,
                    "error_message": str(exc),
                    "completed_at": datetime.now(UTC),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Import Google Search Console impossible.",
            ) from exc

        return GoogleSearchConsoleImportRead.model_validate(import_log)

    def _import_property_data(
        self,
        property_item: GoogleSearchConsoleProperty,
        import_id: int,
        payload: GoogleSearchConsoleManualImportRequest,
    ) -> int:
        dimensions = self._normalize_dimensions(payload.dimensions)
        performance_rows = self.connector.fetch_performance(
            property_url=property_item.property_url,
            start_date=payload.start_date,
            end_date=payload.end_date,
            dimensions=dimensions,
            search_type=payload.search_type,
        )
        index_rows = self.connector.fetch_index_coverage(property_url=property_item.property_url)
        sitemap_rows = self.connector.fetch_sitemaps(property_url=property_item.property_url)

        for row in performance_rows:
            self.repository.upsert_performance(
                {
                    "property_id": property_item.id,
                    "import_id": import_id,
                    "date": row.date,
                    "query": row.query,
                    "page": row.page,
                    "country": row.country,
                    "device": row.device,
                    "search_type": row.search_type,
                    "clicks": row.clicks,
                    "impressions": row.impressions,
                    "ctr": row.ctr,
                    "position": row.position,
                },
            )
        for row in index_rows:
            self.repository.upsert_index_coverage(
                {
                    "property_id": property_item.id,
                    "import_id": import_id,
                    "url": row.url,
                    "coverage_state": row.coverage_state,
                    "google_state": row.google_state,
                    "indexing_state": row.indexing_state,
                    "page_fetch_state": row.page_fetch_state,
                    "robots_txt_state": row.robots_txt_state,
                    "verdict": row.verdict,
                    "issue_type": row.issue_type,
                    "sitemap": row.sitemap,
                    "referring_urls": row.referring_urls,
                    "last_crawled_at": row.last_crawled_at,
                },
            )
        for row in sitemap_rows:
            self.repository.upsert_sitemap(
                {
                    "property_id": property_item.id,
                    "import_id": import_id,
                    "sitemap_url": row.sitemap_url,
                    "sitemap_type": row.sitemap_type,
                    "is_pending": row.is_pending,
                    "is_sitemaps_index": row.is_sitemaps_index,
                    "submitted_at": row.submitted_at,
                    "last_downloaded_at": row.last_downloaded_at,
                    "warnings": row.warnings,
                    "errors": row.errors,
                    "contents": row.contents,
                },
            )
        return len(performance_rows) + len(index_rows) + len(sitemap_rows)

    def _get_property_model(self, property_id: int) -> GoogleSearchConsoleProperty:
        item = self.repository.get_property(property_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propriete Google Search Console introuvable.",
            )
        return item

    def _normalize_dimensions(self, dimensions: list[str]) -> list[str]:
        normalized = []
        for dimension in dimensions:
            value = dimension.strip().lower()
            if value and value not in normalized:
                normalized.append(value)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Au moins une dimension Google Search Console est requise.",
            )
        return normalized
