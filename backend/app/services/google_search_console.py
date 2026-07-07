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
    GoogleSearchConsolePerformanceFilters,
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

    SYNCED_IMPORT_STATUSES = (
        GoogleSearchConsoleImportStatus.COMPLETED.value,
        GoogleSearchConsoleImportStatus.PARTIAL.value,
    )
    VALID_INDEX_STATES = {"INDEXED", "VALID", "SUBMITTED_AND_INDEXED", "PASS"}
    EXCLUDED_INDEX_STATES = {"EXCLUDED", "NOT_INDEXED", "BLOCKED", "REMOVED"}
    ERROR_INDEX_STATES = {"ERROR", "FAIL", "FAILED"}
    WARNING_INDEX_STATES = {"WARNING", "WARN", "PARTIAL"}

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
        last_syncs = self.repository.get_latest_import_completed_at_by_property_ids(
            [item.id for item in items],
            statuses=self.SYNCED_IMPORT_STATUSES,
        )
        return GoogleSearchConsolePropertyList(
            items=[self._property_read(item, last_syncs.get(item.id)) for item in items],
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

        item = self._get_property_model(property_id)
        last_sync_at = self.repository.get_latest_import_completed_at(
            item.id,
            statuses=self.SYNCED_IMPORT_STATUSES,
        )
        return self._property_read(item, last_sync_at)

    def create_property(self, payload: GoogleSearchConsolePropertyCreate) -> GoogleSearchConsolePropertyRead:
        """Create a Google Search Console property."""

        existing = self.repository.get_property_by_google_id(payload.google_property_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Propriete Google Search Console deja existante.",
            )
        item = self.repository.create(payload.model_dump())
        return self._property_read(item, None)

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
        updated = self.repository.update(item, data)
        last_sync_at = self.repository.get_latest_import_completed_at(
            updated.id,
            statuses=self.SYNCED_IMPORT_STATUSES,
        )
        return self._property_read(updated, last_sync_at)

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
        updated = self.repository.update(item, data)
        last_sync_at = self.repository.get_latest_import_completed_at(
            updated.id,
            statuses=self.SYNCED_IMPORT_STATUSES,
        )
        return self._property_read(updated, last_sync_at)

    def delete_property(self, property_id: int) -> None:
        """Delete a Google Search Console property."""

        self.repository.delete_property(self._get_property_model(property_id))

    def list_performances(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
        filters: GoogleSearchConsolePerformanceFilters | None = None,
    ) -> GoogleSearchConsolePerformanceList:
        """Return paginated performance rows."""

        filters = self._normalize_performance_filters(filters or GoogleSearchConsolePerformanceFilters())
        items, total = self.repository.list_performances(
            params,
            property_id=property_id,
            start_date=filters.start_date,
            end_date=filters.end_date,
            page=filters.page,
            query=filters.query,
            country=filters.country,
            device=filters.device,
        )
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
        aggregates = self._indexation_aggregates(
            self.repository.list_index_coverage_statuses(property_id=property_id),
        )
        return GoogleSearchConsoleIndexCoverageList(
            items=[GoogleSearchConsoleIndexCoverageRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
            **aggregates,
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
            items=[self._sitemap_read(item) for item in items],
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
            items=[self._import_read(item) for item in items],
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

        return self._import_read(import_log)

    def _property_read(
        self,
        item: GoogleSearchConsoleProperty,
        last_sync_at: datetime | None,
    ) -> GoogleSearchConsolePropertyRead:
        return GoogleSearchConsolePropertyRead.model_validate(item).model_copy(
            update={"last_sync_at": last_sync_at},
        )

    def _sitemap_read(self, item: object) -> GoogleSearchConsoleSitemapRead:
        read = GoogleSearchConsoleSitemapRead.model_validate(item)
        return read.model_copy(update={"url_count": self._sitemap_url_count(read.contents)})

    def _import_read(self, item: object) -> GoogleSearchConsoleImportRead:
        read = GoogleSearchConsoleImportRead.model_validate(item)
        return read.model_copy(
            update={"duration_seconds": self._duration_seconds(read.started_at, read.completed_at)},
        )

    def _normalize_performance_filters(
        self,
        filters: GoogleSearchConsolePerformanceFilters,
    ) -> GoogleSearchConsolePerformanceFilters:
        if filters.start_date is not None and filters.end_date is not None and filters.end_date < filters.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )
        return GoogleSearchConsolePerformanceFilters(
            start_date=filters.start_date,
            end_date=filters.end_date,
            page=self._clean_filter_value(filters.page),
            query=self._clean_filter_value(filters.query),
            country=self._clean_filter_value(filters.country),
            device=self._clean_filter_value(filters.device),
        )

    def _indexation_aggregates(
        self,
        rows: list[tuple[str, str | None, str | None, str | None]],
    ) -> dict[str, int]:
        aggregates = {"valid_pages": 0, "excluded_pages": 0, "errors": 0, "warnings": 0}
        for coverage_state, verdict, google_state, indexing_state in rows:
            states = {
                self._normalize_state(coverage_state),
                self._normalize_state(verdict),
                self._normalize_state(google_state),
                self._normalize_state(indexing_state),
            }
            if states & self.ERROR_INDEX_STATES:
                aggregates["errors"] += 1
            elif states & self.WARNING_INDEX_STATES:
                aggregates["warnings"] += 1
            elif states & self.EXCLUDED_INDEX_STATES:
                aggregates["excluded_pages"] += 1
            elif states & self.VALID_INDEX_STATES:
                aggregates["valid_pages"] += 1
        return aggregates

    def _sitemap_url_count(self, contents: dict[str, object] | None) -> int:
        if not contents:
            return 0
        explicit_count = self._positive_int(contents.get("url_count"))
        if explicit_count is not None:
            return explicit_count
        root_count = self._positive_int(contents.get("submitted")) or self._positive_int(contents.get("indexed"))
        if root_count is not None:
            return root_count
        urls = contents.get("urls")
        if isinstance(urls, list):
            return len(urls)
        nested_contents = contents.get("contents")
        if not isinstance(nested_contents, list):
            return 0
        total = 0
        for content in nested_contents:
            if isinstance(content, dict):
                total += self._positive_int(content.get("submitted")) or self._positive_int(content.get("indexed")) or 0
        return total

    def _duration_seconds(self, started_at: datetime | None, completed_at: datetime | None) -> float | None:
        if started_at is None or completed_at is None:
            return None
        return max((completed_at - started_at).total_seconds(), 0.0)

    def _clean_filter_value(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _normalize_state(self, value: str | None) -> str:
        return (value or "").strip().upper().replace(" ", "_")

    def _positive_int(self, value: object) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int) and value >= 0:
            return value
        return None

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
