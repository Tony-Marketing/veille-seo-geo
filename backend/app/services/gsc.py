"""Business services for Google Search Console backend."""

from __future__ import annotations

from datetime import UTC, date, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.connectors.google_search_console import GoogleSearchConsoleClient
from backend.app.core.config import settings
from backend.app.core.security import encrypt_secret
from backend.app.repositories.gsc import (
    GscDataRepository,
    GscImportRunRepository,
    GscOAuthCredentialRepository,
    GscPropertyRepository,
)
from backend.app.schemas.gsc import (
    GscCoverageList,
    GscCoverageRead,
    GscImportRunCreate,
    GscImportRunList,
    GscImportRunRead,
    GscIndexingInspectionList,
    GscIndexingInspectionRead,
    GscOAuthAuthorizationUrlRead,
    GscOAuthCallback,
    GscOAuthCredentialRead,
    GscOAuthStatus,
    GscOAuthStatusRead,
    GscPerformanceList,
    GscPerformanceRead,
    GscPropertyList,
    GscPropertyRead,
    GscSitemapList,
    GscSitemapRead,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.gsc_import import GoogleSearchConsoleImportService


class GoogleSearchConsoleService:
    """Manage GSC OAuth, properties and persisted data."""

    def __init__(
        self,
        oauth_repository: GscOAuthCredentialRepository,
        property_repository: GscPropertyRepository,
        import_repository: GscImportRunRepository,
        data_repository: GscDataRepository,
        *,
        client: GoogleSearchConsoleClient | None = None,
    ) -> None:
        self.oauth_repository = oauth_repository
        self.property_repository = property_repository
        self.import_repository = import_repository
        self.data_repository = data_repository
        self.client = client or self._default_client()

    def oauth_status(self) -> GscOAuthStatusRead:
        """Return preparatory OAuth status."""

        latest = self.oauth_repository.latest()
        return GscOAuthStatusRead(
            configured=bool(settings.google_oauth_client_id and settings.google_oauth_client_secret),
            active_credentials_count=self.oauth_repository.count_active(),
            latest_credential=GscOAuthCredentialRead.model_validate(latest) if latest else None,
        )

    def authorization_url(self) -> GscOAuthAuthorizationUrlRead:
        """Return a preparatory OAuth authorization URL."""

        return GscOAuthAuthorizationUrlRead(
            authorization_url=self.client.authorization_url(),
            scopes=self._scopes(),
            configured=bool(settings.google_oauth_client_id and settings.google_oauth_client_secret),
        )

    def oauth_callback(self, payload: GscOAuthCallback, user_id: int | None = None) -> GscOAuthCredentialRead:
        """Store a testable OAuth credential from a preparatory callback."""

        token_payload = self.client.exchange_authorization_code(payload.code)
        scopes = payload.scopes or token_payload.scopes or self._scopes()
        credential = self.oauth_repository.create(
            {
                "provider": "google",
                "scopes": scopes,
                "encrypted_access_token": encrypt_secret(token_payload.access_token),
                "encrypted_refresh_token": (
                    encrypt_secret(token_payload.refresh_token) if token_payload.refresh_token else None
                ),
                "token_expires_at": token_payload.expires_at,
                "status": GscOAuthStatus.ACTIVE,
                "error_message": None,
                "created_by_id": user_id,
                "updated_by_id": user_id,
            },
        )
        return GscOAuthCredentialRead.model_validate(credential)

    def delete_credential(self, credential_id: int) -> None:
        """Delete one OAuth credential."""

        credential = self.oauth_repository.get(credential_id)
        if credential is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential GSC introuvable.")
        self.oauth_repository.delete(credential)

    def list_properties(self, params: PaginationParams) -> GscPropertyList:
        """Return paginated GSC properties."""

        items, total = self.property_repository.list(params)
        return GscPropertyList(
            items=[GscPropertyRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get_property(self, property_id: int) -> GscPropertyRead:
        """Return one GSC property."""

        item = self.property_repository.get(property_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete GSC introuvable.")
        return GscPropertyRead.model_validate(item)

    def sync_properties(self) -> GscPropertyList:
        """Synchronize properties from the injected connector."""

        synced = []
        for item in self.client.list_properties():
            synced.append(
                self.property_repository.upsert_property(
                    {
                        "site_url": item.site_url,
                        "property_type": item.property_type,
                        "permission_level": item.permission_level,
                        "is_verified": item.is_verified,
                        "last_synced_at": datetime.now(UTC),
                    },
                ),
            )
        return GscPropertyList(
            items=[GscPropertyRead.model_validate(item) for item in synced],
            total=len(synced),
            page=1,
            page_size=max(len(synced), 1),
            pages=1 if synced else 0,
        )

    def run_import(self, payload: GscImportRunCreate) -> GscImportRunRead:
        """Run a mocked import through the independent import service."""

        return GoogleSearchConsoleImportService(
            self.property_repository,
            self.import_repository,
            self.data_repository,
            client=self.client,
        ).run_import(payload)

    def list_import_runs(self, params: PaginationParams) -> GscImportRunList:
        """Return paginated GSC import runs."""

        items, total = self.import_repository.list(params)
        return GscImportRunList(
            items=[GscImportRunRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get_import_run(self, import_run_id: int) -> GscImportRunRead:
        """Return one import run."""

        item = self.import_repository.get(import_run_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import GSC introuvable.")
        return GscImportRunRead.model_validate(item)

    def list_performance(
        self,
        property_id: int,
        params: PaginationParams,
        *,
        date_start: date | None = None,
        date_end: date | None = None,
    ) -> GscPerformanceList:
        """Return persisted GSC performance rows."""

        self._ensure_property(property_id)
        items, total = self.data_repository.list_performance(
            property_id,
            params,
            date_start=date_start,
            date_end=date_end,
        )
        return GscPerformanceList(
            items=[GscPerformanceRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_coverage(self, property_id: int, params: PaginationParams) -> GscCoverageList:
        """Return persisted coverage snapshots."""

        self._ensure_property(property_id)
        items, total = self.data_repository.list_coverage(property_id, params)
        return GscCoverageList(
            items=[GscCoverageRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_indexing(self, property_id: int, params: PaginationParams) -> GscIndexingInspectionList:
        """Return persisted indexing inspections."""

        self._ensure_property(property_id)
        items, total = self.data_repository.list_indexing(property_id, params)
        return GscIndexingInspectionList(
            items=[GscIndexingInspectionRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def list_sitemaps(self, property_id: int, params: PaginationParams) -> GscSitemapList:
        """Return persisted sitemaps."""

        self._ensure_property(property_id)
        items, total = self.data_repository.list_sitemaps(property_id, params)
        return GscSitemapList(
            items=[GscSitemapRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def _ensure_property(self, property_id: int) -> None:
        if self.property_repository.get(property_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete GSC introuvable.")

    def _default_client(self) -> GoogleSearchConsoleClient:
        return GoogleSearchConsoleClient(
            client_id=settings.google_oauth_client_id,
            client_secret=settings.google_oauth_client_secret,
            redirect_uri=settings.google_oauth_redirect_uri,
            scopes=self._scopes(),
        )

    def _scopes(self) -> list[str]:
        return [scope.strip() for scope in settings.google_search_console_scopes.split(",") if scope.strip()]
