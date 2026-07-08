"""Routes Bing Webmaster Tools."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.bing_webmaster_tools import BingWebmasterToolsRepository
from backend.app.schemas.bing_webmaster_tools import (
    BingWebmasterConnectionCreate,
    BingWebmasterConnectionListResponse,
    BingWebmasterConnectionRead,
    BingWebmasterConnectionUpdate,
    BingWebmasterCrawlStatFilters,
    BingWebmasterCrawlStatListResponse,
    BingWebmasterImportRequest,
    BingWebmasterImportRunFilters,
    BingWebmasterImportRunListResponse,
    BingWebmasterImportRunRead,
    BingWebmasterImportStatus,
    BingWebmasterMetricFilters,
    BingWebmasterMetricListResponse,
    BingWebmasterSiteListResponse,
    BingWebmasterSitemapFilters,
    BingWebmasterSitemapListResponse,
    BingWebmasterSiteRead,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.bing_webmaster_tools import BingWebmasterToolsService

router = APIRouter(prefix="/bing-webmaster-tools", tags=["Bing Webmaster Tools"])


def get_service(db: Session = Depends(get_db)) -> BingWebmasterToolsService:
    """Build the Bing Webmaster Tools service from the request database session."""

    return BingWebmasterToolsService(BingWebmasterToolsRepository(db))


@router.get(
    "/connections",
    response_model=BingWebmasterConnectionListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister connexions Bing Webmaster Tools",
    description="Retourne les connexions Bing Webmaster Tools paginees.",
)
def list_connections(
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools connections."""

    return service.list_connections(params)


@router.post(
    "/connections",
    response_model=BingWebmasterConnectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer connexion Bing Webmaster Tools",
    description="Cree une connexion Bing Webmaster Tools suivie par le backend.",
)
def create_connection(
    payload: BingWebmasterConnectionCreate,
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Create a Bing Webmaster Tools connection."""

    return service.create_connection(payload)


@router.get(
    "/connections/{connection_id}",
    response_model=BingWebmasterConnectionRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter connexion Bing Webmaster Tools",
    description="Retourne une connexion Bing Webmaster Tools.",
)
def get_connection(connection_id: int, service: BingWebmasterToolsService = Depends(get_service)) -> Any:
    """Return one Bing Webmaster Tools connection."""

    return service.get_connection(connection_id)


@router.patch(
    "/connections/{connection_id}",
    response_model=BingWebmasterConnectionRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Modifier connexion Bing Webmaster Tools",
    description="Met a jour une connexion Bing Webmaster Tools.",
)
def update_connection(
    connection_id: int,
    payload: BingWebmasterConnectionUpdate,
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Update one Bing Webmaster Tools connection."""

    return service.update_connection(connection_id, payload)


@router.delete(
    "/connections/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Desactiver connexion Bing Webmaster Tools",
    description="Desactive logiquement une connexion Bing Webmaster Tools.",
)
def delete_connection(connection_id: int, service: BingWebmasterToolsService = Depends(get_service)) -> Response:
    """Deactivate one Bing Webmaster Tools connection."""

    service.delete_connection(connection_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/sites",
    response_model=BingWebmasterSiteListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister sites Bing Webmaster Tools",
    description="Retourne les sites Bing Webmaster Tools pagines.",
)
def list_sites(
    connection_id: int | None = Query(default=None, gt=0),
    website_id: int | None = Query(default=None, gt=0),
    is_active: bool | None = Query(default=None),
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools sites."""

    return service.list_sites(params, connection_id=connection_id, website_id=website_id, is_active=is_active)


@router.get(
    "/sites/{bing_site_id}",
    response_model=BingWebmasterSiteRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter site Bing Webmaster Tools",
    description="Retourne un site Bing Webmaster Tools.",
)
def get_site(bing_site_id: int, service: BingWebmasterToolsService = Depends(get_service)) -> Any:
    """Return one Bing Webmaster Tools site."""

    return service.get_site(bing_site_id)


@router.post(
    "/import",
    response_model=BingWebmasterImportRunRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Lancer import manuel Bing Webmaster Tools",
    description="Lance un import manuel Bing Webmaster Tools via le backend.",
)
def run_manual_import(
    payload: BingWebmasterImportRequest,
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Run a manual Bing Webmaster Tools import."""

    return service.run_manual_import(payload)


@router.get(
    "/metrics",
    response_model=BingWebmasterMetricListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister metriques Bing Webmaster Tools",
    description="Retourne les metriques Bing Webmaster Tools paginees avec filtres REST.",
)
def list_metrics(
    website_id: int | None = Query(default=None, gt=0),
    bing_site_id: int | None = Query(default=None, gt=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    query: str | None = Query(default=None, max_length=1000),
    page_url: str | None = Query(default=None, max_length=1000),
    country: str | None = Query(default=None, max_length=10),
    device: str | None = Query(default=None, max_length=40),
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools metric rows."""

    return service.list_metrics(
        params,
        filters=BingWebmasterMetricFilters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
            query=query,
            page_url=page_url,
            country=country,
            device=device,
            search=params.search,
        ),
    )


@router.get(
    "/crawl-stats",
    response_model=BingWebmasterCrawlStatListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister statistiques de crawl Bing Webmaster Tools",
    description="Retourne les statistiques de crawl Bing Webmaster Tools paginees.",
)
def list_crawl_stats(
    website_id: int | None = Query(default=None, gt=0),
    bing_site_id: int | None = Query(default=None, gt=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    http_status: int | None = Query(default=None, ge=100, le=599, alias="status"),
    issue_type: str | None = Query(default=None, max_length=255),
    severity: str | None = Query(default=None, max_length=80),
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools crawl statistic rows."""

    return service.list_crawl_stats(
        params,
        filters=BingWebmasterCrawlStatFilters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            date_from=date_from,
            date_to=date_to,
            status=http_status,
            issue_type=issue_type,
            severity=severity,
            search=params.search,
        ),
    )


@router.get(
    "/sitemaps",
    response_model=BingWebmasterSitemapListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister sitemaps Bing Webmaster Tools",
    description="Retourne les sitemaps Bing Webmaster Tools pagines.",
)
def list_sitemaps(
    website_id: int | None = Query(default=None, gt=0),
    bing_site_id: int | None = Query(default=None, gt=0),
    sitemap_status: str | None = Query(default=None, max_length=80, alias="status"),
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools sitemap rows."""

    return service.list_sitemaps(
        params,
        filters=BingWebmasterSitemapFilters(
            website_id=website_id,
            bing_site_id=bing_site_id,
            status=sitemap_status,
            search=params.search,
        ),
    )


@router.get(
    "/import-runs",
    response_model=BingWebmasterImportRunListResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister imports Bing Webmaster Tools",
    description="Retourne l'historique des imports Bing Webmaster Tools.",
)
def list_import_runs(
    connection_id: int | None = Query(default=None, gt=0),
    bing_site_id: int | None = Query(default=None, gt=0),
    import_status: BingWebmasterImportStatus | None = Query(default=None, alias="status"),
    import_type: str | None = Query(default=None, max_length=50),
    params: PaginationParams = Depends(pagination_params),
    service: BingWebmasterToolsService = Depends(get_service),
) -> Any:
    """Return paginated Bing Webmaster Tools import runs."""

    return service.list_import_runs(
        params,
        filters=BingWebmasterImportRunFilters(
            connection_id=connection_id,
            bing_site_id=bing_site_id,
            status=import_status,
            import_type=import_type,
            search=params.search,
        ),
    )
