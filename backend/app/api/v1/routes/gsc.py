"""Routes Google Search Console."""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_permission
from backend.app.models import User
from backend.app.repositories.gsc import (
    GscDataRepository,
    GscImportRunRepository,
    GscOAuthCredentialRepository,
    GscPropertyRepository,
)
from backend.app.schemas.gsc import (
    GscCoverageList,
    GscImportRunCreate,
    GscImportRunList,
    GscImportRunRead,
    GscIndexingInspectionList,
    GscOAuthAuthorizationUrlRead,
    GscOAuthCallback,
    GscOAuthCredentialRead,
    GscOAuthStatusRead,
    GscPerformanceList,
    GscPropertyList,
    GscPropertyRead,
    GscSitemapList,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.gsc import GoogleSearchConsoleService

router = APIRouter(prefix="/gsc", tags=["Google Search Console"])


def get_service(db: Session = Depends(get_db)) -> GoogleSearchConsoleService:
    """Build the GSC service from the request database session."""

    return GoogleSearchConsoleService(
        GscOAuthCredentialRepository(db),
        GscPropertyRepository(db),
        GscImportRunRepository(db),
        GscDataRepository(db),
    )


@router.get(
    "/properties",
    response_model=GscPropertyList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Proprietes GSC",
)
def list_properties(
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated GSC properties."""

    return service.list_properties(params)


@router.post(
    "/properties/sync",
    response_model=GscPropertyList,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="Synchroniser Proprietes GSC",
)
def sync_properties(service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Synchronize properties using the configured connector."""

    return service.sync_properties()


@router.get(
    "/properties/{property_id}",
    response_model=GscPropertyRead,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Consulter Propriete GSC",
)
def get_property(property_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return one GSC property."""

    return service.get_property(property_id)


@router.get(
    "/properties/{property_id}/performance",
    response_model=GscPerformanceList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Performances GSC",
)
def list_performance(
    property_id: int,
    date_start: date | None = Query(default=None),
    date_end: date | None = Query(default=None),
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return persisted performance data."""

    return service.list_performance(property_id, params, date_start=date_start, date_end=date_end)


@router.get(
    "/properties/{property_id}/coverage",
    response_model=GscCoverageList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Couverture GSC",
)
def list_coverage(
    property_id: int,
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return persisted coverage data."""

    return service.list_coverage(property_id, params)


@router.get(
    "/properties/{property_id}/indexing",
    response_model=GscIndexingInspectionList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Indexation GSC",
)
def list_indexing(
    property_id: int,
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return persisted indexing inspections."""

    return service.list_indexing(property_id, params)


@router.get(
    "/properties/{property_id}/sitemaps",
    response_model=GscSitemapList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Sitemaps GSC",
)
def list_sitemaps(
    property_id: int,
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return persisted sitemaps."""

    return service.list_sitemaps(property_id, params)


@router.post(
    "/import-runs",
    response_model=GscImportRunRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="Lancer Import GSC",
)
def create_import_run(
    payload: GscImportRunCreate,
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Run one mocked GSC import."""

    return service.run_import(payload)


@router.get(
    "/import-runs",
    response_model=GscImportRunList,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Lister Imports GSC",
)
def list_import_runs(
    params: PaginationParams = Depends(pagination_params),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Return paginated import runs."""

    return service.list_import_runs(params)


@router.get(
    "/import-runs/{import_run_id}",
    response_model=GscImportRunRead,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Consulter Import GSC",
)
def get_import_run(import_run_id: int, service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return one import run."""

    return service.get_import_run(import_run_id)


@router.get(
    "/oauth/status",
    response_model=GscOAuthStatusRead,
    dependencies=[Depends(require_permission("gsc.read"))],
    summary="Statut OAuth GSC",
)
def oauth_status(service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return OAuth status."""

    return service.oauth_status()


@router.get(
    "/oauth/authorization-url",
    response_model=GscOAuthAuthorizationUrlRead,
    dependencies=[Depends(require_permission("gsc.write"))],
    summary="URL Autorisation OAuth GSC",
)
def authorization_url(service: GoogleSearchConsoleService = Depends(get_service)) -> Any:
    """Return preparatory OAuth authorization URL."""

    return service.authorization_url()


@router.post(
    "/oauth/callback",
    response_model=GscOAuthCredentialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Callback OAuth GSC Preparatoire",
)
def oauth_callback(
    payload: GscOAuthCallback,
    user: User = Depends(require_permission("gsc.write")),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Any:
    """Store a preparatory OAuth credential."""

    return service.oauth_callback(payload, user_id=user.id)


@router.delete(
    "/oauth/credentials/{credential_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer Credential OAuth GSC",
)
def delete_credential(
    credential_id: int,
    user: User = Depends(require_permission("gsc.write")),
    service: GoogleSearchConsoleService = Depends(get_service),
) -> Response:
    """Delete one OAuth credential."""

    assert user.id is not None
    service.delete_credential(credential_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
