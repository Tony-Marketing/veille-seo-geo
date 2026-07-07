"""Routes Google Search Console."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportList,
    GoogleSearchConsoleImportRead,
    GoogleSearchConsoleIndexCoverageList,
    GoogleSearchConsoleManualImportRequest,
    GoogleSearchConsoleOAuthTokenUpdate,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsolePerformanceList,
    GoogleSearchConsolePropertyCreate,
    GoogleSearchConsolePropertyList,
    GoogleSearchConsolePropertyRead,
    GoogleSearchConsolePropertyUpdate,
    GoogleSearchConsoleSitemapList,
)
from backend.app.schemas.pagination import Order, PaginationParams, pagination_params
from backend.app.services.google_search_console import GoogleSearchConsoleService

router = APIRouter(prefix="/google-search-console", tags=["Google Search Console"])


def get_service(db: Session = Depends(get_db)) -> GoogleSearchConsoleService:
    """Build the Google Search Console service from the request database session."""

    return GoogleSearchConsoleService(GoogleSearchConsoleRepository(db))


@router.get(
    "/properties",
    response_model=GoogleSearchConsolePropertyList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister proprietes Google Search Console",
    description="Retourne les proprietes Google Search Console paginees.",
)
def list_properties(
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console properties."""

    return service.list_properties(params)


@router.get(
    "/properties/remote",
    response_model=list[GoogleSearchConsolePropertyCreate],
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister proprietes Google distantes",
    description="Retourne les proprietes visibles via le connecteur injecte.",
)
def list_remote_properties(service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return remote properties through the connector."""

    return service.list_remote_properties()


@router.post(
    "/properties",
    response_model=GoogleSearchConsolePropertyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer propriete Google Search Console",
    description="Cree une propriete Google Search Console suivie par le backend.",
)
def create_property(
    payload: GoogleSearchConsolePropertyCreate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Create a Google Search Console property."""

    return service.create_property(payload)


@router.get(
    "/properties/{property_id}",
    response_model=GoogleSearchConsolePropertyRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter propriete Google Search Console",
    description="Retourne une propriete Google Search Console.",
)
def get_property(property_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return one Google Search Console property."""

    return service.get_property(property_id)


@router.put(
    "/properties/{property_id}",
    response_model=GoogleSearchConsolePropertyRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Modifier propriete Google Search Console",
    description="Met a jour une propriete Google Search Console.",
)
def update_property(
    property_id: int,
    payload: GoogleSearchConsolePropertyUpdate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Update one Google Search Console property."""

    return service.update_property(property_id, payload)


@router.put(
    "/properties/{property_id}/oauth",
    response_model=GoogleSearchConsolePropertyRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Configurer OAuth Google Search Console",
    description="Stocke les tokens OAuth Google Search Console de maniere chiffree.",
)
def update_oauth_tokens(
    property_id: int,
    payload: GoogleSearchConsoleOAuthTokenUpdate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Update encrypted OAuth token data."""

    return service.update_oauth_tokens(property_id, payload)


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Supprimer propriete Google Search Console",
    description="Supprime une propriete Google Search Console.",
)
def delete_property(property_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Response:
    """Delete one Google Search Console property."""

    service.delete_property(property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/performances",
    response_model=GoogleSearchConsolePerformanceList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister performances Google Search Console",
    description="Retourne les performances Google Search Console paginees.",
)
def list_performances(
    property_id: int | None = Query(default=None, gt=0),
    page: list[str] | None = Query(default=None, description="Numero de page ou filtre URL de page GSC."),
    page_size: int = Query(20, ge=1, le=100, description="Nombre d'elements par page."),
    search: str | None = Query(None, description="Recherche plein texte simple."),
    sort: str | None = Query(None, description="Colonne de tri."),
    order: Order = Query("asc", description="Ordre de tri."),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    query: str | None = Query(default=None, max_length=1000),
    country: str | None = Query(default=None, max_length=10),
    device: str | None = Query(default=None, max_length=40),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated performance rows."""

    pagination_page, performance_page = _performance_page_values(page)
    return service.list_performances(
        PaginationParams(page=pagination_page, page_size=page_size, search=search, sort=sort, order=order),
        property_id=property_id,
        filters=GoogleSearchConsolePerformanceFilters(
            start_date=start_date,
            end_date=end_date,
            page=performance_page,
            query=query,
            country=country,
            device=device,
        ),
    )


def _performance_page_values(values: list[str] | None) -> tuple[int, str | None]:
    pagination_page = 1
    performance_page = None
    for value in values or []:
        if value.isdecimal() and performance_page is None:
            parsed_page = int(value)
            if parsed_page < 1:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Le numero de page doit etre superieur ou egal a 1.",
                )
            pagination_page = parsed_page
        elif performance_page is None:
            performance_page = value
    return pagination_page, performance_page


@router.get(
    "/indexation",
    response_model=GoogleSearchConsoleIndexCoverageList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister indexation Google Search Console",
    description="Retourne les donnees d'indexation Google Search Console paginees.",
)
def list_index_coverages(
    property_id: int | None = Query(default=None, gt=0),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated index coverage rows."""

    return service.list_index_coverages(params, property_id=property_id)


@router.get(
    "/sitemaps",
    response_model=GoogleSearchConsoleSitemapList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister sitemaps Google Search Console",
    description="Retourne les sitemaps Google Search Console pagines.",
)
def list_sitemaps(
    property_id: int | None = Query(default=None, gt=0),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated sitemap rows."""

    return service.list_sitemaps(params, property_id=property_id)


@router.post(
    "/imports/manual",
    response_model=GoogleSearchConsoleImportRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Lancer import manuel Google Search Console",
    description="Lance un import manuel Google Search Console via le backend.",
)
def run_manual_import(
    payload: GoogleSearchConsoleManualImportRequest,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Run a manual Google Search Console import."""

    return service.run_manual_import(payload)


@router.get(
    "/imports",
    response_model=GoogleSearchConsoleImportList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister imports Google Search Console",
    description="Retourne l'historique des imports Google Search Console.",
)
def list_imports(
    property_id: int | None = Query(default=None, gt=0),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated import logs."""

    return service.list_imports(params, property_id=property_id)
