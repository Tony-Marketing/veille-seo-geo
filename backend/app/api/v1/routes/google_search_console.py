"""Routes Google Search Console."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.google_search_console import GoogleSearchConsoleRepository
from backend.app.schemas.google_search_console import (
    GoogleSearchConsoleImportFilters,
    GoogleSearchConsoleImportList,
    GoogleSearchConsoleImportRead,
    GoogleSearchConsoleImportRequest,
    GoogleSearchConsoleIndexCoverageFilters,
    GoogleSearchConsoleIndexCoverageList,
    GoogleSearchConsolePerformanceFilters,
    GoogleSearchConsolePerformanceList,
    GoogleSearchConsolePropertyCreate,
    GoogleSearchConsolePropertyList,
    GoogleSearchConsolePropertyRead,
    GoogleSearchConsolePropertyUpdate,
    GoogleSearchConsoleSitemapFilters,
    GoogleSearchConsoleSitemapList,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.google_search_console import GoogleSearchConsoleService

router = APIRouter(prefix="/google-search-console", tags=["Google Search Console"])


def get_service(db: Session = Depends(get_db)) -> GoogleSearchConsoleService:
    """Build the Google Search Console service from the request database session."""

    return GoogleSearchConsoleService(GoogleSearchConsoleRepository(db))


@router.get(
    "/properties",
    response_model=GoogleSearchConsolePropertyList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Proprietes GSC",
    description="Retourne les proprietes Google Search Console paginees.",
)
def list_properties(
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console properties."""

    return service.list_properties(params)


@router.post(
    "/properties",
    response_model=GoogleSearchConsolePropertyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="Creer Propriete GSC",
    description="Cree une propriete Google Search Console manuelle.",
)
def create_property(
    payload: GoogleSearchConsolePropertyCreate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Create one Google Search Console property."""

    return service.create_property(payload)


@router.get(
    "/properties/{property_id}",
    response_model=GoogleSearchConsolePropertyRead,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Consulter Propriete GSC",
    description="Retourne une propriete Google Search Console.",
)
def get_property(property_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return one Google Search Console property."""

    return service.get_property(property_id)


@router.put(
    "/properties/{property_id}",
    response_model=GoogleSearchConsolePropertyRead,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="Modifier Propriete GSC",
    description="Met a jour une propriete Google Search Console.",
)
def update_property(
    property_id: int,
    payload: GoogleSearchConsolePropertyUpdate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Update one Google Search Console property."""

    return service.update_property(property_id, payload)


@router.get(
    "/performances",
    response_model=GoogleSearchConsolePerformanceList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Performances GSC",
    description="Retourne les performances Google Search Console importees.",
)
def list_performances(
    property_id: int = Query(..., gt=0),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    page: str | None = Query(None),
    query: str | None = Query(None),
    country: str | None = Query(None),
    device: str | None = Query(None),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console performances."""

    filters = GoogleSearchConsolePerformanceFilters(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        query=query,
        country=country,
        device=device,
    )
    return service.list_performances(filters, params)


@router.get(
    "/indexation",
    response_model=GoogleSearchConsoleIndexCoverageList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Indexation GSC",
    description="Retourne les donnees d'indexation Google Search Console importees.",
)
def list_index_coverages(
    property_id: int = Query(..., gt=0),
    coverage_state: str | None = Query(None),
    verdict: str | None = Query(None),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console index coverage rows."""

    filters = GoogleSearchConsoleIndexCoverageFilters(
        property_id=property_id,
        coverage_state=coverage_state,
        verdict=verdict,
    )
    return service.list_index_coverages(filters, params)


@router.get(
    "/sitemaps",
    response_model=GoogleSearchConsoleSitemapList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Sitemaps GSC",
    description="Retourne les sitemaps Google Search Console importes.",
)
def list_sitemaps(
    property_id: int = Query(..., gt=0),
    sitemap_status: str | None = Query(None, alias="status"),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console sitemaps."""

    filters = GoogleSearchConsoleSitemapFilters(property_id=property_id, status=sitemap_status)
    return service.list_sitemaps(filters, params)


@router.post(
    "/imports",
    response_model=GoogleSearchConsoleImportRead,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="Lancer Import GSC",
    description="Lance un import manuel Google Search Console cote backend.",
)
def run_import(
    payload: GoogleSearchConsoleImportRequest,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Run one Google Search Console import."""

    return service.run_import(payload)


@router.get(
    "/imports",
    response_model=GoogleSearchConsoleImportList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Imports GSC",
    description="Retourne l'historique des imports Google Search Console.",
)
def list_imports(
    property_id: int | None = Query(None, gt=0),
    import_type: str | None = Query(None),
    import_status: str | None = Query(None, alias="status"),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated Google Search Console import history."""

    filters = GoogleSearchConsoleImportFilters(
        property_id=property_id,
        import_type=import_type,
        status=import_status,
    )
    return service.list_imports(filters, params)


@router.get(
    "/imports/{import_id}",
    response_model=GoogleSearchConsoleImportRead,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Consulter Import GSC",
    description="Retourne le detail d'un import Google Search Console.",
)
def get_import(import_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return one Google Search Console import history row."""

    return service.get_import(import_id)
