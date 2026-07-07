"""Routes Google Analytics 4."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.google_analytics import (
    GoogleAnalyticsBreakdownResponse,
    GoogleAnalyticsImportFilters,
    GoogleAnalyticsImportHistoryList,
    GoogleAnalyticsImportList,
    GoogleAnalyticsImportRead,
    GoogleAnalyticsImportRequest,
    GoogleAnalyticsImportStatus,
    GoogleAnalyticsMetricFilters,
    GoogleAnalyticsMetricList,
    GoogleAnalyticsOAuthConnectRequest,
    GoogleAnalyticsOAuthRefreshRequest,
    GoogleAnalyticsOAuthResponse,
    GoogleAnalyticsPropertyCreate,
    GoogleAnalyticsPropertyList,
    GoogleAnalyticsPropertyRead,
    GoogleAnalyticsPropertyUpdate,
    GoogleAnalyticsSummaryResponse,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.google_analytics import GoogleAnalyticsService

router = APIRouter(prefix="/google-analytics", tags=["Google Analytics"])


def get_service(db: Session = Depends(get_db)) -> GoogleAnalyticsService:
    """Build the Google Analytics service from the request database session."""

    return GoogleAnalyticsService(GoogleAnalyticsRepository(db))


@router.get(
    "/properties",
    response_model=GoogleAnalyticsPropertyList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister proprietes Google Analytics",
    description="Retourne les proprietes Google Analytics paginees.",
)
def list_properties(
    params: PaginationParams = Depends(pagination_params),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return paginated Google Analytics properties."""

    return service.list_properties(params)


@router.post(
    "/properties",
    response_model=GoogleAnalyticsPropertyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Creer propriete Google Analytics",
    description="Cree une propriete Google Analytics suivie par le backend.",
)
def create_property(
    payload: GoogleAnalyticsPropertyCreate,
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Create a Google Analytics property."""

    return service.create_property(payload)


@router.put(
    "/properties/{property_id}",
    response_model=GoogleAnalyticsPropertyRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Modifier propriete Google Analytics",
    description="Met a jour une propriete Google Analytics.",
)
def update_property(
    property_id: int,
    payload: GoogleAnalyticsPropertyUpdate,
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Update one Google Analytics property."""

    return service.update_property(property_id, payload)


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Supprimer propriete Google Analytics",
    description="Supprime une propriete Google Analytics.",
)
def delete_property(property_id: int, service: GoogleAnalyticsService = Depends(get_service)) -> Response:
    """Delete one Google Analytics property."""

    service.delete_property(property_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/import",
    response_model=GoogleAnalyticsImportRead,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Lancer import manuel Google Analytics",
    description="Lance un import manuel Google Analytics via le backend.",
)
def run_manual_import(
    payload: GoogleAnalyticsImportRequest,
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Run a manual Google Analytics import."""

    return service.run_manual_import(payload)


@router.get(
    "/metrics",
    response_model=GoogleAnalyticsMetricList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister metriques Google Analytics",
    description="Retourne les metriques Google Analytics paginees avec filtres REST.",
)
def list_metrics(
    website_id: int | None = Query(default=None, gt=0),
    property_id: int | None = Query(default=None, gt=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    import_id: int | None = Query(default=None, gt=0),
    source: str | None = Query(default=None, max_length=255),
    medium: str | None = Query(default=None, max_length=255),
    campaign: str | None = Query(default=None, max_length=255),
    device_category: str | None = Query(default=None, max_length=80),
    country: str | None = Query(default=None, max_length=120),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return paginated Google Analytics metric rows."""

    return service.list_metrics(
        params,
        filters=GoogleAnalyticsMetricFilters(
            website_id=website_id,
            property_id=property_id,
            date_from=date_from,
            date_to=date_to,
            import_id=import_id,
            source=source,
            medium=medium,
            campaign=campaign,
            device_category=device_category,
            country=country,
            search=params.search,
        ),
    )


def _metric_filters(
    website_id: int | None = Query(default=None, gt=0),
    property_id: int | None = Query(default=None, gt=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    import_id: int | None = Query(default=None, gt=0),
    source: str | None = Query(default=None, max_length=255),
    medium: str | None = Query(default=None, max_length=255),
    campaign: str | None = Query(default=None, max_length=255),
    device_category: str | None = Query(default=None, max_length=80),
    country: str | None = Query(default=None, max_length=120),
    search: str | None = Query(default=None, max_length=255),
) -> GoogleAnalyticsMetricFilters:
    """Build Google Analytics metric filters from query parameters."""

    return GoogleAnalyticsMetricFilters(
        website_id=website_id,
        property_id=property_id,
        date_from=date_from,
        date_to=date_to,
        import_id=import_id,
        source=source,
        medium=medium,
        campaign=campaign,
        device_category=device_category,
        country=country,
        search=search,
    )


@router.get(
    "/overview",
    response_model=GoogleAnalyticsSummaryResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Synthese Google Analytics",
    description="Retourne les KPIs Google Analytics calcules cote backend.",
)
def overview(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics overview KPIs."""

    return service.overview(filters)


@router.get(
    "/traffic",
    response_model=GoogleAnalyticsBreakdownResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Trafic Google Analytics",
    description="Retourne les agregats de trafic Google Analytics.",
)
def traffic(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics traffic breakdown."""

    return service.traffic(filters)


@router.get(
    "/acquisition",
    response_model=GoogleAnalyticsBreakdownResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Acquisition Google Analytics",
    description="Retourne les agregats d'acquisition Google Analytics.",
)
def acquisition(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics acquisition breakdown."""

    return service.acquisition(filters)


@router.get(
    "/engagement",
    response_model=GoogleAnalyticsBreakdownResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Engagement Google Analytics",
    description="Retourne les agregats d'engagement Google Analytics.",
)
def engagement(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics engagement breakdown."""

    return service.engagement(filters)


@router.get(
    "/conversions",
    response_model=GoogleAnalyticsBreakdownResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Conversions Google Analytics",
    description="Retourne les agregats de conversions Google Analytics.",
)
def conversions(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics conversion breakdown."""

    return service.conversions(filters)


@router.get(
    "/revenue",
    response_model=GoogleAnalyticsBreakdownResponse,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Revenus Google Analytics",
    description="Retourne les agregats de revenus Google Analytics.",
)
def revenue(
    filters: GoogleAnalyticsMetricFilters = Depends(_metric_filters),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return Google Analytics revenue breakdown."""

    return service.revenue(filters)


@router.get(
    "/imports",
    response_model=GoogleAnalyticsImportList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Lister imports Google Analytics",
    description="Retourne l'historique des imports Google Analytics.",
)
def list_imports(
    property_id: int | None = Query(default=None, gt=0),
    import_status: GoogleAnalyticsImportStatus | None = Query(default=None, alias="status"),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return paginated import logs."""

    return service.list_imports(
        params,
        filters=GoogleAnalyticsImportFilters(property_id=property_id, status=import_status, search=params.search),
    )


@router.get(
    "/history",
    response_model=GoogleAnalyticsImportHistoryList,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Historique enrichi Google Analytics",
    description="Retourne l'historique enrichi des imports Google Analytics.",
)
def history(
    property_id: int | None = Query(default=None, gt=0),
    import_status: GoogleAnalyticsImportStatus | None = Query(default=None, alias="status"),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Return enriched import history."""

    return service.history(
        params,
        filters=GoogleAnalyticsImportFilters(property_id=property_id, status=import_status, search=params.search),
    )


@router.get(
    "/imports/{import_id}",
    response_model=GoogleAnalyticsImportRead,
    dependencies=[Depends(require_permission("crawl.read"))],
    summary="Consulter import Google Analytics",
    description="Retourne le detail d'un import Google Analytics.",
)
def get_import(import_id: int, service: GoogleAnalyticsService = Depends(get_service)) -> Any:
    """Return one import log."""

    return service.get_import(import_id)


@router.post(
    "/oauth/connect",
    response_model=GoogleAnalyticsOAuthResponse,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Connecter OAuth Google Analytics",
    description="Prepare et stocke les tokens OAuth Google Analytics de maniere chiffree.",
)
def connect_oauth(
    payload: GoogleAnalyticsOAuthConnectRequest,
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Connect OAuth token data."""

    return service.connect_oauth(payload)


@router.post(
    "/oauth/refresh",
    response_model=GoogleAnalyticsOAuthResponse,
    dependencies=[Depends(require_permission("crawl.write"))],
    summary="Rafraichir OAuth Google Analytics",
    description="Rafraichit manuellement les tokens OAuth Google Analytics.",
)
def refresh_oauth(
    payload: GoogleAnalyticsOAuthRefreshRequest,
    service: GoogleAnalyticsService = Depends(get_service),
) -> Any:
    """Refresh OAuth token data."""

    return service.refresh_oauth(payload)
