"""Business service for Bing Webmaster Tools."""

from collections.abc import Callable
from datetime import UTC, datetime
from math import ceil
from typing import TypeVar

from fastapi import HTTPException, status

from backend.app.connectors.bing_webmaster_tools import (
    BingWebmasterAuthenticationError,
    BingWebmasterConnector,
    BingWebmasterCredentials,
    BingWebmasterNetworkError,
    NotConfiguredBingWebmasterConnector,
)
from backend.app.core.security import decrypt_secret, encrypt_secret
from backend.app.models import BingWebmasterConnection, BingWebmasterSite
from backend.app.repositories.bing_webmaster_tools import BingWebmasterToolsRepository
from backend.app.schemas.bing_webmaster_tools import (
    BingWebmasterConnectionCreate,
    BingWebmasterConnectionListResponse,
    BingWebmasterConnectionRead,
    BingWebmasterConnectionUpdate,
    BingWebmasterCrawlStatFilters,
    BingWebmasterCrawlStatListResponse,
    BingWebmasterCrawlStatRead,
    BingWebmasterImportRequest,
    BingWebmasterImportRunFilters,
    BingWebmasterImportRunListResponse,
    BingWebmasterImportRunRead,
    BingWebmasterImportStatus,
    BingWebmasterMetricFilters,
    BingWebmasterMetricListResponse,
    BingWebmasterMetricRead,
    BingWebmasterSiteListResponse,
    BingWebmasterSitemapFilters,
    BingWebmasterSitemapListResponse,
    BingWebmasterSitemapRead,
    BingWebmasterSiteRead,
)
from backend.app.schemas.pagination import PaginationParams

RepositoryResult = TypeVar("RepositoryResult")


class BingWebmasterToolsService:
    """Manage Bing Webmaster Tools connections, data and imports."""

    def __init__(
        self,
        repository: BingWebmasterToolsRepository,
        *,
        connector: BingWebmasterConnector | None = None,
    ) -> None:
        self.repository = repository
        self.connector = connector or NotConfiguredBingWebmasterConnector()

    def list_connections(self, params: PaginationParams) -> BingWebmasterConnectionListResponse:
        """Return paginated Bing Webmaster Tools connections."""

        items, total = self._repository_result(self.repository.list_connections, params)
        return BingWebmasterConnectionListResponse(
            items=[self._connection_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
        )

    def create_connection(self, payload: BingWebmasterConnectionCreate) -> BingWebmasterConnectionRead:
        """Create a Bing Webmaster Tools connection."""

        item = self.repository.create(self._connection_data(payload.model_dump()))
        return self._connection_read(item)

    def get_connection(self, connection_id: int) -> BingWebmasterConnectionRead:
        """Return one Bing Webmaster Tools connection."""

        return self._connection_read(self._get_connection_model(connection_id))

    def update_connection(
        self,
        connection_id: int,
        payload: BingWebmasterConnectionUpdate,
    ) -> BingWebmasterConnectionRead:
        """Update a Bing Webmaster Tools connection."""

        item = self._get_connection_model(connection_id)
        data = self._connection_data(payload.model_dump(exclude_unset=True))
        updated = self.repository.update(item, data)
        return self._connection_read(updated)

    def delete_connection(self, connection_id: int) -> None:
        """Deactivate a Bing Webmaster Tools connection."""

        self.repository.deactivate_connection(self._get_connection_model(connection_id))

    def list_sites(
        self,
        params: PaginationParams,
        *,
        connection_id: int | None = None,
        website_id: int | None = None,
        is_active: bool | None = None,
    ) -> BingWebmasterSiteListResponse:
        """Return paginated Bing Webmaster Tools sites."""

        items, total = self._repository_result(
            self.repository.list_sites,
            params,
            connection_id=connection_id,
            website_id=website_id,
            is_active=is_active,
        )
        return BingWebmasterSiteListResponse(
            items=[BingWebmasterSiteRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
        )

    def get_site(self, bing_site_id: int) -> BingWebmasterSiteRead:
        """Return one Bing Webmaster Tools site."""

        return BingWebmasterSiteRead.model_validate(self._get_site_model(bing_site_id))

    def list_metrics(
        self,
        params: PaginationParams,
        *,
        filters: BingWebmasterMetricFilters | None = None,
    ) -> BingWebmasterMetricListResponse:
        """Return paginated Bing Webmaster Tools metrics."""

        filters = self._normalize_metric_filters(filters or BingWebmasterMetricFilters())
        items, total = self._repository_result(
            self.repository.list_metrics,
            params,
            **self._filters_dict(filters),
        )
        return BingWebmasterMetricListResponse(
            items=[BingWebmasterMetricRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
            filters=self._filters_dict(filters),
        )

    def list_crawl_stats(
        self,
        params: PaginationParams,
        *,
        filters: BingWebmasterCrawlStatFilters | None = None,
    ) -> BingWebmasterCrawlStatListResponse:
        """Return paginated Bing Webmaster Tools crawl statistics."""

        filters = self._normalize_crawl_stat_filters(filters or BingWebmasterCrawlStatFilters())
        items, total = self._repository_result(
            self.repository.list_crawl_stats,
            params,
            **self._filters_dict(filters),
        )
        return BingWebmasterCrawlStatListResponse(
            items=[BingWebmasterCrawlStatRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
            filters=self._filters_dict(filters),
        )

    def list_sitemaps(
        self,
        params: PaginationParams,
        *,
        filters: BingWebmasterSitemapFilters | None = None,
    ) -> BingWebmasterSitemapListResponse:
        """Return paginated Bing Webmaster Tools sitemaps."""

        filters = self._normalize_sitemap_filters(filters or BingWebmasterSitemapFilters())
        items, total = self._repository_result(
            self.repository.list_sitemaps,
            params,
            **self._filters_dict(filters),
        )
        return BingWebmasterSitemapListResponse(
            items=[BingWebmasterSitemapRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
            filters=self._filters_dict(filters),
        )

    def list_import_runs(
        self,
        params: PaginationParams,
        *,
        filters: BingWebmasterImportRunFilters | None = None,
    ) -> BingWebmasterImportRunListResponse:
        """Return paginated Bing Webmaster Tools import runs."""

        filters = self._normalize_import_run_filters(filters or BingWebmasterImportRunFilters())
        values = self._filters_dict(filters)
        if filters.status is not None:
            values["status"] = filters.status.value
        items, total = self._repository_result(self.repository.list_import_runs, params, **values)
        return BingWebmasterImportRunListResponse(
            items=[self._import_run_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=self._pages(total, params.page_size),
            filters=self._filters_dict(filters),
        )

    def run_manual_import(self, payload: BingWebmasterImportRequest) -> BingWebmasterImportRunRead:
        """Run an idempotent manual import through the injected connector."""

        if payload.date_to < payload.date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )

        connection = self._get_connection_model(payload.connection_id)
        if not connection.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La connexion Bing Webmaster Tools est desactivee.",
            )

        import_run = self.repository.create_import_run(
            {
                "connection_id": connection.id,
                "bing_site_id": payload.bing_site_id,
                "import_type": payload.import_type,
                "status": BingWebmasterImportStatus.RUNNING,
                "started_at": datetime.now(UTC),
                "finished_at": None,
                "items_processed": 0,
                "error_message": None,
            },
        )

        try:
            sites = self._sites_for_import(connection, payload.bing_site_id)
            items_processed = self._import_sites(connection, sites, import_run.id, payload)
            now = datetime.now(UTC)
            import_run = self.repository.update_import_run(
                import_run,
                {
                    "status": BingWebmasterImportStatus.COMPLETED,
                    "finished_at": now,
                    "items_processed": items_processed,
                    "error_message": None,
                },
            )
            self.repository.update(connection, {"last_sync_at": now, "last_error": None})
        except (BingWebmasterAuthenticationError, BingWebmasterNetworkError, RuntimeError) as exc:
            self.repository.update_import_run(
                import_run,
                {
                    "status": BingWebmasterImportStatus.FAILED,
                    "finished_at": datetime.now(UTC),
                    "error_message": str(exc),
                },
            )
            self.repository.update(connection, {"last_error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Import Bing Webmaster Tools impossible.",
            ) from exc

        return self._import_run_read(import_run)

    def _sites_for_import(
        self,
        connection: BingWebmasterConnection,
        bing_site_id: int | None,
    ) -> list[BingWebmasterSite]:
        if bing_site_id is not None:
            site = self._get_site_model(bing_site_id)
            if site.connection_id != connection.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Site Bing Webmaster Tools introuvable pour cette connexion.",
                )
            if not site.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Le site Bing Webmaster Tools est desactive.",
                )
            return [site]

        credentials = self._credentials(connection)
        remote_sites = self.connector.list_sites(credentials)
        sites = [
            self.repository.upsert_site(
                {
                    "connection_id": connection.id,
                    "website_id": connection.website_id,
                    "site_url": row.site_url,
                    "is_verified": row.is_verified,
                    "is_active": True,
                },
            )
            for row in remote_sites
        ]
        return sites

    def _import_sites(
        self,
        connection: BingWebmasterConnection,
        sites: list[BingWebmasterSite],
        import_id: int,
        payload: BingWebmasterImportRequest,
    ) -> int:
        credentials = self._credentials(connection)
        items_processed = 0
        imported_at = datetime.now(UTC)
        for site in sites:
            metrics = self.connector.fetch_metrics(credentials, site.site_url, payload.date_from, payload.date_to)
            crawl_stats = self.connector.fetch_crawl_stats(
                credentials,
                site.site_url,
                payload.date_from,
                payload.date_to,
            )
            sitemaps = self.connector.fetch_sitemaps(credentials, site.site_url)

            for row in metrics:
                self.repository.upsert_metric(
                    {
                        "bing_site_id": site.id,
                        "import_id": import_id,
                        "date": row.date,
                        "query": self._clean_text(row.query),
                        "page_url": self._clean_text(row.page_url),
                        "country": self._clean_text(row.country),
                        "device": self._clean_text(row.device),
                        "clicks": max(row.clicks, 0),
                        "impressions": max(row.impressions, 0),
                        "ctr": max(row.ctr, 0.0),
                        "average_position": max(row.average_position, 0.0),
                    },
                )
            for row in crawl_stats:
                self.repository.upsert_crawl_stat(
                    {
                        "bing_site_id": site.id,
                        "import_id": import_id,
                        "date": row.date,
                        "url": row.url,
                        "http_status": row.http_status,
                        "issue_type": self._clean_text(row.issue_type),
                        "issue_category": self._clean_text(row.issue_category),
                        "severity": self._clean_text(row.severity),
                        "details": self._clean_text(row.details),
                    },
                )
            for row in sitemaps:
                self.repository.upsert_sitemap(
                    {
                        "bing_site_id": site.id,
                        "import_id": import_id,
                        "sitemap_url": row.sitemap_url,
                        "status": self._clean_text(row.status),
                        "submitted_at": row.submitted_at,
                        "last_crawled_at": row.last_crawled_at,
                        "url_count": max(row.url_count, 0),
                        "error_count": max(row.error_count, 0),
                        "warning_count": max(row.warning_count, 0),
                    },
                )
            items_processed += len(metrics) + len(crawl_stats) + len(sitemaps)
            self.repository.update(site, {"last_import_at": imported_at})
        return items_processed

    def _connection_data(self, data: dict[str, object]) -> dict[str, object]:
        secret_fields = {
            "client_secret": "client_secret_encrypted",
            "access_token": "access_token_encrypted",
            "refresh_token": "refresh_token_encrypted",
            "api_key": "api_key_encrypted",
        }
        transformed = data.copy()
        for public_field, stored_field in secret_fields.items():
            if public_field in transformed:
                value = transformed.pop(public_field)
                transformed[stored_field] = encrypt_secret(value) if isinstance(value, str) else None
        return transformed

    def _credentials(self, connection: BingWebmasterConnection) -> BingWebmasterCredentials:
        return BingWebmasterCredentials(
            auth_type=connection.auth_type,
            client_id=connection.client_id,
            client_secret=self._decrypt_optional(connection.client_secret_encrypted),
            access_token=self._decrypt_optional(connection.access_token_encrypted),
            refresh_token=self._decrypt_optional(connection.refresh_token_encrypted),
            api_key=self._decrypt_optional(connection.api_key_encrypted),
            token_expires_at=connection.token_expires_at,
            scopes=connection.scopes,
        )

    def _connection_read(self, item: BingWebmasterConnection) -> BingWebmasterConnectionRead:
        return BingWebmasterConnectionRead.model_validate(item).model_copy(
            update={
                "has_client_secret": bool(item.client_secret_encrypted),
                "has_access_token": bool(item.access_token_encrypted),
                "has_refresh_token": bool(item.refresh_token_encrypted),
                "has_api_key": bool(item.api_key_encrypted),
            },
        )

    def _import_run_read(self, item: object) -> BingWebmasterImportRunRead:
        read = BingWebmasterImportRunRead.model_validate(item)
        return read.model_copy(update={"duration_seconds": self._duration_seconds(read.started_at, read.finished_at)})

    def _get_connection_model(self, connection_id: int) -> BingWebmasterConnection:
        item = self.repository.get_connection(connection_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connexion Bing Webmaster Tools introuvable.",
            )
        return item

    def _get_site_model(self, bing_site_id: int) -> BingWebmasterSite:
        item = self.repository.get_site(bing_site_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site Bing Webmaster Tools introuvable.")
        return item

    def _normalize_metric_filters(self, filters: BingWebmasterMetricFilters) -> BingWebmasterMetricFilters:
        self._validate_period(filters.date_from, filters.date_to)
        return BingWebmasterMetricFilters(
            website_id=filters.website_id,
            bing_site_id=filters.bing_site_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            query=self._clean_text(filters.query),
            page_url=self._clean_text(filters.page_url),
            country=self._clean_text(filters.country),
            device=self._clean_text(filters.device),
            search=self._clean_text(filters.search),
        )

    def _normalize_crawl_stat_filters(self, filters: BingWebmasterCrawlStatFilters) -> BingWebmasterCrawlStatFilters:
        self._validate_period(filters.date_from, filters.date_to)
        return BingWebmasterCrawlStatFilters(
            website_id=filters.website_id,
            bing_site_id=filters.bing_site_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            status=filters.status,
            issue_type=self._clean_text(filters.issue_type),
            severity=self._clean_text(filters.severity),
            search=self._clean_text(filters.search),
        )

    def _normalize_sitemap_filters(self, filters: BingWebmasterSitemapFilters) -> BingWebmasterSitemapFilters:
        return BingWebmasterSitemapFilters(
            website_id=filters.website_id,
            bing_site_id=filters.bing_site_id,
            status=self._clean_text(filters.status),
            search=self._clean_text(filters.search),
        )

    def _normalize_import_run_filters(self, filters: BingWebmasterImportRunFilters) -> BingWebmasterImportRunFilters:
        return BingWebmasterImportRunFilters(
            connection_id=filters.connection_id,
            bing_site_id=filters.bing_site_id,
            status=filters.status,
            import_type=self._clean_text(filters.import_type),
            search=self._clean_text(filters.search),
        )

    def _validate_period(self, date_from: object, date_to: object) -> None:
        if date_from is not None and date_to is not None and date_to < date_from:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )

    def _filters_dict(self, filters: object) -> dict[str, object]:
        return filters.model_dump(exclude_none=True)

    def _repository_result(
        self,
        repository_method: Callable[..., RepositoryResult],
        *args: object,
        **kwargs: object,
    ) -> RepositoryResult:
        try:
            return repository_method(*args, **kwargs)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    def _clean_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _decrypt_optional(self, value: str | None) -> str | None:
        return decrypt_secret(value) if value else None

    def _duration_seconds(self, started_at: datetime | None, finished_at: datetime | None) -> float | None:
        if started_at is None or finished_at is None:
            return None
        return max((finished_at - started_at).total_seconds(), 0.0)

    def _pages(self, total: int, page_size: int) -> int:
        return ceil(total / page_size) if total else 0
