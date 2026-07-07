"""Business service for Google Search Console backend."""

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.connectors.google_search_console import (
    GoogleSearchConsoleConnector,
    GoogleSearchConsoleConnectorError,
    PreparedGoogleSearchConsoleConnector,
)
from backend.app.models import GoogleSearchConsoleImport, GoogleSearchConsoleProperty
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportFilters,
    GoogleSearchConsoleImportList,
    GoogleSearchConsoleImportRead,
    GoogleSearchConsoleImportRequest,
    GoogleSearchConsoleImportStatus,
    GoogleSearchConsoleImportType,
    GoogleSearchConsoleIndexCoverageFilters,
    GoogleSearchConsoleIndexCoverageList,
    GoogleSearchConsoleIndexCoverageRead,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsolePerformanceList,
    GoogleSearchConsolePerformanceRead,
    GoogleSearchConsolePropertyCreate,
    GoogleSearchConsolePropertyList,
    GoogleSearchConsolePropertyRead,
    GoogleSearchConsolePropertyUpdate,
    GoogleSearchConsoleSitemapFilters,
    GoogleSearchConsoleSitemapList,
    GoogleSearchConsoleSitemapRead,
)
from backend.app.schemas.pagination import PaginationParams


class GoogleSearchConsoleService:
    """Manage Google Search Console data, imports and history."""

    def __init__(
        self,
        repository: GoogleSearchConsoleRepository,
        *,
        connector: GoogleSearchConsoleConnector | None = None,
    ) -> None:
        self.repository = repository
        self.connector = connector or PreparedGoogleSearchConsoleConnector()

    def list_properties(self, params: PaginationParams) -> GoogleSearchConsolePropertyList:
        """Return paginated Google Search Console properties."""

        items, total = self.repository.list(params)
        return GoogleSearchConsolePropertyList(
            items=[GoogleSearchConsolePropertyRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get_property(self, property_id: int) -> GoogleSearchConsolePropertyRead:
        """Return one Google Search Console property."""

        return GoogleSearchConsolePropertyRead.model_validate(self._property_or_404(property_id))

    def create_property(self, payload: GoogleSearchConsolePropertyCreate) -> GoogleSearchConsolePropertyRead:
        """Create a Google Search Console property manually."""

        if self.repository.get_property_by_site_url(payload.site_url) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Propriete GSC deja existante.")
        item = self.repository.create(payload.model_dump(exclude_unset=True))
        return GoogleSearchConsolePropertyRead.model_validate(item)

    def update_property(
        self,
        property_id: int,
        payload: GoogleSearchConsolePropertyUpdate,
    ) -> GoogleSearchConsolePropertyRead:
        """Update one Google Search Console property."""

        item = self._property_or_404(property_id)
        updated = self.repository.update(item, payload.model_dump(exclude_unset=True))
        return GoogleSearchConsolePropertyRead.model_validate(updated)

    def list_performances(
        self,
        filters: GoogleSearchConsolePerformanceFilters,
        params: PaginationParams,
    ) -> GoogleSearchConsolePerformanceList:
        """Return paginated performance rows."""

        self._property_or_404(filters.property_id)
        items, total = self.repository.list_performances(filters, params)
        return GoogleSearchConsolePerformanceList(
            items=[GoogleSearchConsolePerformanceRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_index_coverages(
        self,
        filters: GoogleSearchConsoleIndexCoverageFilters,
        params: PaginationParams,
    ) -> GoogleSearchConsoleIndexCoverageList:
        """Return paginated index coverage rows."""

        self._property_or_404(filters.property_id)
        items, total = self.repository.list_index_coverages(filters, params)
        return GoogleSearchConsoleIndexCoverageList(
            items=[GoogleSearchConsoleIndexCoverageRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_sitemaps(
        self,
        filters: GoogleSearchConsoleSitemapFilters,
        params: PaginationParams,
    ) -> GoogleSearchConsoleSitemapList:
        """Return paginated sitemaps."""

        self._property_or_404(filters.property_id)
        items, total = self.repository.list_sitemaps(filters, params)
        return GoogleSearchConsoleSitemapList(
            items=[GoogleSearchConsoleSitemapRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_imports(
        self,
        filters: GoogleSearchConsoleImportFilters,
        params: PaginationParams,
    ) -> GoogleSearchConsoleImportList:
        """Return paginated import history."""

        if filters.property_id is not None:
            self._property_or_404(filters.property_id)
        items, total = self.repository.list_imports(filters, params)
        return GoogleSearchConsoleImportList(
            items=[GoogleSearchConsoleImportRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get_import(self, import_id: int) -> GoogleSearchConsoleImportRead:
        """Return one import history row."""

        item = self.repository.get_import(import_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import GSC introuvable.")
        return GoogleSearchConsoleImportRead.model_validate(item)

    def run_import(self, payload: GoogleSearchConsoleImportRequest) -> GoogleSearchConsoleImportRead:
        """Run one synchronous Google Search Console import through the connector."""

        gsc_property = None
        if payload.property_id is not None:
            gsc_property = self._property_or_404(payload.property_id)

        import_history = self.repository.create_import(
            {
                "property_id": payload.property_id,
                "import_type": payload.import_type.value,
                "status": GoogleSearchConsoleImportStatus.RUNNING,
                "started_at": datetime.now(UTC),
                "items_processed": 0,
                "items_created": 0,
                "items_updated": 0,
                "items_skipped": 0,
                "import_metadata": {
                    "start_date": payload.start_date.isoformat() if payload.start_date else None,
                    "end_date": payload.end_date.isoformat() if payload.end_date else None,
                },
            },
        )
        try:
            result = self._execute_import(import_history, payload, gsc_property)
        except GoogleSearchConsoleConnectorError as exc:
            result = self._fail_import(import_history, str(exc))
        except Exception as exc:  # noqa: BLE001
            result = self._fail_import(import_history, str(exc))
        return GoogleSearchConsoleImportRead.model_validate(result)

    def _execute_import(
        self,
        import_history: GoogleSearchConsoleImport,
        payload: GoogleSearchConsoleImportRequest,
        gsc_property: GoogleSearchConsoleProperty | None,
    ) -> GoogleSearchConsoleImport:
        counters = {"processed": 0, "created": 0, "updated": 0, "skipped": 0}
        if payload.import_type == GoogleSearchConsoleImportType.PROPERTIES:
            self._import_properties(counters)
        elif payload.import_type == GoogleSearchConsoleImportType.PERFORMANCE and gsc_property is not None:
            self._import_performances(gsc_property, payload, counters)
        elif payload.import_type == GoogleSearchConsoleImportType.INDEX_COVERAGE and gsc_property is not None:
            self._import_index_coverages(gsc_property, counters)
        elif payload.import_type == GoogleSearchConsoleImportType.SITEMAPS and gsc_property is not None:
            self._import_sitemaps(gsc_property, counters)
        elif payload.import_type == GoogleSearchConsoleImportType.FULL and gsc_property is not None:
            self._import_performances(gsc_property, payload, counters)
            self._import_index_coverages(gsc_property, counters)
            self._import_sitemaps(gsc_property, counters)

        status_value = GoogleSearchConsoleImportStatus.COMPLETED
        if counters["processed"] == 0:
            status_value = GoogleSearchConsoleImportStatus.COMPLETED
        if gsc_property is not None:
            self.repository.update(gsc_property, {"last_synced_at": datetime.now(UTC)})
        return self.repository.update_import(
            import_history,
            {
                "status": status_value,
                "finished_at": datetime.now(UTC),
                "items_processed": counters["processed"],
                "items_created": counters["created"],
                "items_updated": counters["updated"],
                "items_skipped": counters["skipped"],
            },
        )

    def _import_properties(self, counters: dict[str, int]) -> None:
        for item in self.connector.list_properties():
            _, created = self.repository.upsert_property(
                {
                    "site_url": item.site_url,
                    "property_type": item.property_type,
                    "permission_level": item.permission_level,
                    "status": item.status,
                    "last_synced_at": datetime.now(UTC),
                },
            )
            self._count_upsert(counters, created)

    def _import_performances(
        self,
        gsc_property: GoogleSearchConsoleProperty,
        payload: GoogleSearchConsoleImportRequest,
        counters: dict[str, int],
    ) -> None:
        rows = self.connector.fetch_performance(
            gsc_property.site_url,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        for row in rows:
            _, created = self.repository.upsert_performance(
                {
                    "property_id": gsc_property.id,
                    "date": row.date,
                    "page": row.page,
                    "query": row.query,
                    "country": row.country,
                    "device": row.device,
                    "clicks": row.clicks,
                    "impressions": row.impressions,
                    "ctr": row.ctr,
                    "position": row.position,
                },
            )
            self._count_upsert(counters, created)

    def _import_index_coverages(
        self,
        gsc_property: GoogleSearchConsoleProperty,
        counters: dict[str, int],
    ) -> None:
        for row in self.connector.fetch_index_coverage(gsc_property.site_url):
            _, created = self.repository.upsert_index_coverage(
                {
                    "property_id": gsc_property.id,
                    "url": row.url,
                    "coverage_state": row.coverage_state,
                    "indexing_state": row.indexing_state,
                    "verdict": row.verdict,
                    "page_fetch_state": row.page_fetch_state,
                    "google_canonical": row.google_canonical,
                    "user_canonical": row.user_canonical,
                    "last_crawl_time": row.last_crawl_time,
                    "inspected_at": row.inspected_at,
                },
            )
            self._count_upsert(counters, created)

    def _import_sitemaps(
        self,
        gsc_property: GoogleSearchConsoleProperty,
        counters: dict[str, int],
    ) -> None:
        for row in self.connector.fetch_sitemaps(gsc_property.site_url):
            _, created = self.repository.upsert_sitemap(
                {
                    "property_id": gsc_property.id,
                    "sitemap_url": row.sitemap_url,
                    "status": row.status,
                    "last_submitted_at": row.last_submitted_at,
                    "last_downloaded_at": row.last_downloaded_at,
                    "warnings": row.warnings,
                    "errors": row.errors,
                    "contents": row.contents,
                },
            )
            self._count_upsert(counters, created)

    def _fail_import(self, import_history: GoogleSearchConsoleImport, message: str) -> GoogleSearchConsoleImport:
        return self.repository.update_import(
            import_history,
            {
                "status": GoogleSearchConsoleImportStatus.FAILED,
                "finished_at": datetime.now(UTC),
                "error_message": message,
            },
        )

    def _count_upsert(self, counters: dict[str, int], created: bool) -> None:
        counters["processed"] += 1
        if created:
            counters["created"] += 1
        else:
            counters["updated"] += 1

    def _property_or_404(self, property_id: int) -> GoogleSearchConsoleProperty:
        item = self.repository.get(property_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete GSC introuvable.")
        return item
