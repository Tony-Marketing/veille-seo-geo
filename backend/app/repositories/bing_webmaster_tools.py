"""Repository for Bing Webmaster Tools data."""

from datetime import date
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import (
    BingWebmasterConnection,
    BingWebmasterCrawlStat,
    BingWebmasterImportRun,
    BingWebmasterMetric,
    BingWebmasterSite,
    BingWebmasterSitemap,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class BingWebmasterToolsRepository(BaseRepository[BingWebmasterConnection]):
    """Encapsulate SQLAlchemy persistence for Bing Webmaster Tools."""

    search_fields = ("client_id", "last_error")
    connection_sort_fields = (
        "id",
        "website_id",
        "auth_type",
        "client_id",
        "is_active",
        "last_sync_at",
        "created_at",
        "updated_at",
    )
    site_sort_fields = ("id", "connection_id", "website_id", "site_url", "is_verified", "is_active", "created_at")
    metric_sort_fields = (
        "id",
        "bing_site_id",
        "import_id",
        "date",
        "query",
        "page_url",
        "country",
        "device",
        "clicks",
        "impressions",
        "ctr",
        "average_position",
        "created_at",
    )
    crawl_stat_sort_fields = (
        "id",
        "bing_site_id",
        "import_id",
        "date",
        "url",
        "http_status",
        "issue_type",
        "issue_category",
        "severity",
        "created_at",
    )
    sitemap_sort_fields = (
        "id",
        "bing_site_id",
        "import_id",
        "sitemap_url",
        "status",
        "url_count",
        "error_count",
        "warning_count",
        "created_at",
        "updated_at",
    )
    import_run_sort_fields = (
        "id",
        "connection_id",
        "bing_site_id",
        "import_type",
        "status",
        "started_at",
        "finished_at",
        "items_processed",
        "created_at",
    )

    def __init__(self, db: Session) -> None:
        super().__init__(db, BingWebmasterConnection)

    def get_connection(self, connection_id: int) -> BingWebmasterConnection | None:
        """Return a Bing Webmaster Tools connection by primary key."""

        return self.db.get(BingWebmasterConnection, connection_id)

    def list_connections(self, params: PaginationParams) -> tuple[list[BingWebmasterConnection], int]:
        """Return paginated Bing Webmaster Tools connections."""

        statement = select(BingWebmasterConnection)
        count_statement = select(func.count()).select_from(BingWebmasterConnection)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterConnection,
            allowed_sort_fields=self.connection_sort_fields,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def deactivate_connection(self, item: BingWebmasterConnection) -> BingWebmasterConnection:
        """Deactivate a connection without deleting stored data."""

        return self.update(item, {"is_active": False})

    def get_site(self, bing_site_id: int) -> BingWebmasterSite | None:
        """Return a Bing Webmaster Tools site by primary key."""

        return self.db.get(BingWebmasterSite, bing_site_id)

    def get_site_by_url(self, connection_id: int, site_url: str) -> BingWebmasterSite | None:
        """Return a site by connection and URL."""

        statement = select(BingWebmasterSite).where(
            BingWebmasterSite.connection_id == connection_id,
            BingWebmasterSite.site_url == site_url,
        )
        return self.db.scalar(statement)

    def upsert_site(self, data: dict[str, Any]) -> BingWebmasterSite:
        """Create or update one Bing Webmaster Tools site."""

        item = self.get_site_by_url(data["connection_id"], data["site_url"])
        return self._upsert(item, BingWebmasterSite, data)

    def list_sites(
        self,
        params: PaginationParams,
        *,
        connection_id: int | None = None,
        website_id: int | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[BingWebmasterSite], int]:
        """Return paginated Bing Webmaster Tools sites."""

        statement = select(BingWebmasterSite)
        count_statement = select(func.count()).select_from(BingWebmasterSite)
        filters = self._site_filters(
            connection_id=connection_id,
            website_id=website_id,
            is_active=is_active,
            search=params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterSite,
            allowed_sort_fields=self.site_sort_fields,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def upsert_metric(self, data: dict[str, Any]) -> BingWebmasterMetric:
        """Create or update one idempotent Bing metric row."""

        statement = select(BingWebmasterMetric).where(
            BingWebmasterMetric.bing_site_id == data["bing_site_id"],
            BingWebmasterMetric.date == data["date"],
            BingWebmasterMetric.query == data.get("query"),
            BingWebmasterMetric.page_url == data.get("page_url"),
            BingWebmasterMetric.country == data.get("country"),
            BingWebmasterMetric.device == data.get("device"),
        )
        item = self.db.scalar(statement)
        return self._upsert(item, BingWebmasterMetric, data)

    def list_metrics(
        self,
        params: PaginationParams,
        *,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        query: str | None = None,
        page_url: str | None = None,
        country: str | None = None,
        device: str | None = None,
        search: str | None = None,
    ) -> tuple[list[BingWebmasterMetric], int]:
        """Return paginated Bing metric rows."""

        statement = select(BingWebmasterMetric).join(BingWebmasterMetric.site)
        count_statement = select(func.count(BingWebmasterMetric.id)).join(BingWebmasterMetric.site)
        filters = self._metric_filters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            page_url=page_url,
            country=country,
            device=device,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterMetric,
            allowed_sort_fields=self.metric_sort_fields,
            default_date_order=True,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def upsert_crawl_stat(self, data: dict[str, Any]) -> BingWebmasterCrawlStat:
        """Create or update one idempotent crawl statistic row."""

        statement = select(BingWebmasterCrawlStat).where(
            BingWebmasterCrawlStat.bing_site_id == data["bing_site_id"],
            BingWebmasterCrawlStat.date == data["date"],
            BingWebmasterCrawlStat.url == data["url"],
            BingWebmasterCrawlStat.http_status == data.get("http_status"),
            BingWebmasterCrawlStat.issue_type == data.get("issue_type"),
        )
        item = self.db.scalar(statement)
        return self._upsert(item, BingWebmasterCrawlStat, data)

    def list_crawl_stats(
        self,
        params: PaginationParams,
        *,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        status: int | None = None,
        issue_type: str | None = None,
        severity: str | None = None,
        search: str | None = None,
    ) -> tuple[list[BingWebmasterCrawlStat], int]:
        """Return paginated crawl statistic rows."""

        statement = select(BingWebmasterCrawlStat).join(BingWebmasterCrawlStat.site)
        count_statement = select(func.count(BingWebmasterCrawlStat.id)).join(BingWebmasterCrawlStat.site)
        filters = self._crawl_stat_filters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
            status=status,
            issue_type=issue_type,
            severity=severity,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterCrawlStat,
            allowed_sort_fields=self.crawl_stat_sort_fields,
            default_date_order=True,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def upsert_sitemap(self, data: dict[str, Any]) -> BingWebmasterSitemap:
        """Create or update one idempotent sitemap row."""

        statement = select(BingWebmasterSitemap).where(
            BingWebmasterSitemap.bing_site_id == data["bing_site_id"],
            BingWebmasterSitemap.sitemap_url == data["sitemap_url"],
        )
        item = self.db.scalar(statement)
        return self._upsert(item, BingWebmasterSitemap, data)

    def list_sitemaps(
        self,
        params: PaginationParams,
        *,
        website_id: int | None = None,
        bing_site_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[BingWebmasterSitemap], int]:
        """Return paginated sitemap rows."""

        statement = select(BingWebmasterSitemap).join(BingWebmasterSitemap.site)
        count_statement = select(func.count(BingWebmasterSitemap.id)).join(BingWebmasterSitemap.site)
        filters = self._sitemap_filters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            status=status,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterSitemap,
            allowed_sort_fields=self.sitemap_sort_fields,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def create_import_run(self, data: dict[str, Any]) -> BingWebmasterImportRun:
        """Persist a new import run."""

        item = BingWebmasterImportRun(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_import_run(
        self,
        item: BingWebmasterImportRun,
        data: dict[str, Any],
    ) -> BingWebmasterImportRun:
        """Update an import run."""

        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_import_runs(
        self,
        params: PaginationParams,
        *,
        connection_id: int | None = None,
        bing_site_id: int | None = None,
        status: str | None = None,
        import_type: str | None = None,
        search: str | None = None,
    ) -> tuple[list[BingWebmasterImportRun], int]:
        """Return paginated import runs."""

        statement = select(BingWebmasterImportRun).join(BingWebmasterImportRun.connection)
        count_statement = select(func.count(BingWebmasterImportRun.id)).join(BingWebmasterImportRun.connection)
        filters = self._import_run_filters(
            connection_id=connection_id,
            bing_site_id=bing_site_id,
            status=status,
            import_type=import_type,
            search=search or params.search,
        )
        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)
        statement = self._order_and_page(
            statement,
            params,
            BingWebmasterImportRun,
            allowed_sort_fields=self.import_run_sort_fields,
        )
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)

    def _upsert(self, item: Any | None, model: type[Any], data: dict[str, Any]) -> Any:
        if item is None:
            item = model(**data)
            self.db.add(item)
        else:
            for key, value in data.items():
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def _order_and_page(
        self,
        statement: Any,
        params: PaginationParams,
        model: type[Any],
        *,
        allowed_sort_fields: tuple[str, ...],
        default_date_order: bool = False,
    ) -> Any:
        if params.sort:
            if params.sort not in allowed_sort_fields or not hasattr(model, params.sort):
                raise ValueError(f"Champ de tri Bing Webmaster Tools non autorise: {params.sort}.")
            sort_column = getattr(model, params.sort)
            statement = statement.order_by(sort_column.desc() if params.order == "desc" else sort_column.asc())
        elif default_date_order and hasattr(model, "date"):
            statement = statement.order_by(model.date.desc(), model.id.desc())
        else:
            statement = statement.order_by(model.id.desc())
        return statement.offset(params.offset).limit(params.page_size)

    def _site_filters(
        self,
        *,
        connection_id: int | None,
        website_id: int | None,
        is_active: bool | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if connection_id is not None:
            filters.append(BingWebmasterSite.connection_id == connection_id)
        if website_id is not None:
            filters.append(BingWebmasterSite.website_id == website_id)
        if is_active is not None:
            filters.append(BingWebmasterSite.is_active == is_active)
        if search:
            filters.append(BingWebmasterSite.site_url.ilike(f"%{search}%"))
        return filters

    def _metric_filters(
        self,
        *,
        website_id: int | None,
        bing_site_id: int | None,
        date_from: date | None,
        date_to: date | None,
        query: str | None,
        page_url: str | None,
        country: str | None,
        device: str | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if website_id is not None:
            filters.append(BingWebmasterSite.website_id == website_id)
        if bing_site_id is not None:
            filters.append(BingWebmasterMetric.bing_site_id == bing_site_id)
        if date_from is not None:
            filters.append(BingWebmasterMetric.date >= date_from)
        if date_to is not None:
            filters.append(BingWebmasterMetric.date <= date_to)
        if query is not None:
            filters.append(BingWebmasterMetric.query == query)
        if page_url is not None:
            filters.append(BingWebmasterMetric.page_url == page_url)
        if country is not None:
            filters.append(BingWebmasterMetric.country == country)
        if device is not None:
            filters.append(BingWebmasterMetric.device == device)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    BingWebmasterMetric.query.ilike(like_pattern),
                    BingWebmasterMetric.page_url.ilike(like_pattern),
                    BingWebmasterSite.site_url.ilike(like_pattern),
                ),
            )
        return filters

    def _crawl_stat_filters(
        self,
        *,
        website_id: int | None,
        bing_site_id: int | None,
        date_from: date | None,
        date_to: date | None,
        status: int | None,
        issue_type: str | None,
        severity: str | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if website_id is not None:
            filters.append(BingWebmasterSite.website_id == website_id)
        if bing_site_id is not None:
            filters.append(BingWebmasterCrawlStat.bing_site_id == bing_site_id)
        if date_from is not None:
            filters.append(BingWebmasterCrawlStat.date >= date_from)
        if date_to is not None:
            filters.append(BingWebmasterCrawlStat.date <= date_to)
        if status is not None:
            filters.append(BingWebmasterCrawlStat.http_status == status)
        if issue_type is not None:
            filters.append(BingWebmasterCrawlStat.issue_type == issue_type)
        if severity is not None:
            filters.append(BingWebmasterCrawlStat.severity == severity)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    BingWebmasterCrawlStat.url.ilike(like_pattern),
                    BingWebmasterCrawlStat.issue_type.ilike(like_pattern),
                    BingWebmasterCrawlStat.details.ilike(like_pattern),
                    BingWebmasterSite.site_url.ilike(like_pattern),
                ),
            )
        return filters

    def _sitemap_filters(
        self,
        *,
        website_id: int | None,
        bing_site_id: int | None,
        status: str | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if website_id is not None:
            filters.append(BingWebmasterSite.website_id == website_id)
        if bing_site_id is not None:
            filters.append(BingWebmasterSitemap.bing_site_id == bing_site_id)
        if status is not None:
            filters.append(BingWebmasterSitemap.status == status)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    BingWebmasterSitemap.sitemap_url.ilike(like_pattern),
                    BingWebmasterSitemap.status.ilike(like_pattern),
                    BingWebmasterSite.site_url.ilike(like_pattern),
                ),
            )
        return filters

    def _import_run_filters(
        self,
        *,
        connection_id: int | None,
        bing_site_id: int | None,
        status: str | None,
        import_type: str | None,
        search: str | None,
    ) -> list[Any]:
        filters = []
        if connection_id is not None:
            filters.append(BingWebmasterImportRun.connection_id == connection_id)
        if bing_site_id is not None:
            filters.append(BingWebmasterImportRun.bing_site_id == bing_site_id)
        if status is not None:
            filters.append(BingWebmasterImportRun.status == status)
        if import_type is not None:
            filters.append(BingWebmasterImportRun.import_type == import_type)
        if search:
            like_pattern = f"%{search}%"
            filters.append(
                or_(
                    BingWebmasterImportRun.status.ilike(like_pattern),
                    BingWebmasterImportRun.import_type.ilike(like_pattern),
                    BingWebmasterImportRun.error_message.ilike(like_pattern),
                    BingWebmasterConnection.client_id.ilike(like_pattern),
                ),
            )
        return filters
