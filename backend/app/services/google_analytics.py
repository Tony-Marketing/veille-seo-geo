"""Business service for Google Analytics 4."""

from datetime import UTC, datetime
from math import ceil

from fastapi import HTTPException, status

from backend.app.connectors.google_analytics import (
    GoogleAnalyticsConnector,
    GoogleAnalyticsOAuthTokenData,
    NotConfiguredGoogleAnalyticsConnector,
)
from backend.app.core.security import decrypt_secret, encrypt_secret
from backend.app.models import GoogleAnalyticsProperty
from backend.app.repositories.google_analytics import GoogleAnalyticsRepository
from backend.app.schemas.google_analytics import (
    GoogleAnalyticsImportList,
    GoogleAnalyticsImportRead,
    GoogleAnalyticsImportRequest,
    GoogleAnalyticsImportStatus,
    GoogleAnalyticsOAuthConnectRequest,
    GoogleAnalyticsOAuthRefreshRequest,
    GoogleAnalyticsOAuthResponse,
    GoogleAnalyticsPropertyCreate,
    GoogleAnalyticsPropertyList,
    GoogleAnalyticsPropertyRead,
    GoogleAnalyticsPropertyUpdate,
)
from backend.app.schemas.pagination import PaginationParams


class GoogleAnalyticsService:
    """Manage Google Analytics properties, OAuth data and imports."""

    METRIC_NAME_MAP = {
        "users": "users",
        "newusers": "new_users",
        "new_users": "new_users",
        "sessions": "sessions",
        "engagedsessions": "engaged_sessions",
        "engaged_sessions": "engaged_sessions",
        "screenpageviews": "screen_page_views",
        "screen_page_views": "screen_page_views",
        "averagesessionduration": "average_session_duration",
        "average_session_duration": "average_session_duration",
        "engagementrate": "engagement_rate",
        "engagement_rate": "engagement_rate",
        "conversions": "conversions",
        "totalrevenue": "total_revenue",
        "total_revenue": "total_revenue",
    }
    DIMENSION_NAME_MAP = {
        "date": "date",
        "source": "source",
        "medium": "medium",
        "campaign": "campaign",
        "devicecategory": "device_category",
        "device_category": "device_category",
        "country": "country",
    }

    def __init__(
        self,
        repository: GoogleAnalyticsRepository,
        *,
        connector: GoogleAnalyticsConnector | None = None,
    ) -> None:
        self.repository = repository
        self.connector = connector or NotConfiguredGoogleAnalyticsConnector()

    def list_properties(self, params: PaginationParams) -> GoogleAnalyticsPropertyList:
        """Return paginated Google Analytics properties."""

        items, total = self.repository.list_properties(params)
        return GoogleAnalyticsPropertyList(
            items=[GoogleAnalyticsPropertyRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def create_property(self, payload: GoogleAnalyticsPropertyCreate) -> GoogleAnalyticsPropertyRead:
        """Create a Google Analytics property."""

        existing = self.repository.get_property_by_property_id(payload.property_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Propriete Google Analytics deja existante.",
            )
        item = self.repository.create(payload.model_dump())
        return GoogleAnalyticsPropertyRead.model_validate(item)

    def update_property(
        self,
        property_pk: int,
        payload: GoogleAnalyticsPropertyUpdate,
    ) -> GoogleAnalyticsPropertyRead:
        """Update one Google Analytics property."""

        item = self._get_property_model(property_pk)
        data = payload.model_dump(exclude_unset=True)
        google_property_id = data.get("property_id")
        if google_property_id is not None:
            existing = self.repository.get_property_by_property_id(google_property_id)
            if existing is not None and existing.id != property_pk:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Propriete Google Analytics deja existante.",
                )
        updated = self.repository.update(item, data)
        return GoogleAnalyticsPropertyRead.model_validate(updated)

    def delete_property(self, property_pk: int) -> None:
        """Delete one Google Analytics property."""

        self.repository.delete_property(self._get_property_model(property_pk))

    def list_imports(
        self,
        params: PaginationParams,
        *,
        property_id: int | None = None,
    ) -> GoogleAnalyticsImportList:
        """Return paginated import logs."""

        items, total = self.repository.list_imports(params, property_id=property_id)
        return GoogleAnalyticsImportList(
            items=[self._import_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get_import(self, import_id: int) -> GoogleAnalyticsImportRead:
        """Return one import log."""

        item = self.repository.get_import(import_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import Google Analytics introuvable.")
        return self._import_read(item)

    def run_manual_import(self, payload: GoogleAnalyticsImportRequest) -> GoogleAnalyticsImportRead:
        """Run an idempotent manual import through the injected connector."""

        if payload.end_date < payload.start_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="La date de fin doit etre superieure ou egale a la date de debut.",
            )

        property_item = self._get_property_model(payload.property_id)
        if not property_item.enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La propriete Google Analytics est desactivee.",
            )

        metrics = self._normalize_names(payload.metrics, self.METRIC_NAME_MAP, "metrique")
        dimensions = self._normalize_names(payload.dimensions, self.DIMENSION_NAME_MAP, "dimension")
        import_log = self.repository.create_import(
            {
                "property_id": property_item.id,
                "status": GoogleAnalyticsImportStatus.RUNNING,
                "imported_rows": 0,
                "error_message": None,
                "started_at": datetime.now(UTC),
                "finished_at": None,
            },
        )

        try:
            rows = self.connector.fetch_metrics(
                property_id=property_item.property_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                metrics=metrics,
                dimensions=dimensions,
            )
            for row in rows:
                self.repository.upsert_metric(
                    {
                        "property_id": property_item.id,
                        "import_id": import_log.id,
                        "date": row.date,
                        "source": self._clean_dimension(row.source),
                        "medium": self._clean_dimension(row.medium),
                        "campaign": self._clean_dimension(row.campaign),
                        "device_category": self._clean_dimension(row.device_category),
                        "country": self._clean_dimension(row.country),
                        "users": max(row.users, 0),
                        "new_users": max(row.new_users, 0),
                        "sessions": max(row.sessions, 0),
                        "engaged_sessions": max(row.engaged_sessions, 0),
                        "screen_page_views": max(row.screen_page_views, 0),
                        "average_session_duration": max(row.average_session_duration, 0.0),
                        "engagement_rate": max(row.engagement_rate, 0.0),
                        "conversions": max(row.conversions, 0.0),
                        "total_revenue": max(row.total_revenue, 0.0),
                    },
                )
            import_log = self.repository.update_import(
                import_log,
                {
                    "status": GoogleAnalyticsImportStatus.COMPLETED,
                    "imported_rows": len(rows),
                    "finished_at": datetime.now(UTC),
                },
            )
        except Exception as exc:  # noqa: BLE001
            self.repository.update_import(
                import_log,
                {
                    "status": GoogleAnalyticsImportStatus.FAILED,
                    "error_message": str(exc),
                    "finished_at": datetime.now(UTC),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Import Google Analytics impossible.",
            ) from exc

        return self._import_read(import_log)

    def connect_oauth(self, payload: GoogleAnalyticsOAuthConnectRequest) -> GoogleAnalyticsOAuthResponse:
        """Store OAuth tokens returned by the injected connector."""

        property_item = self._get_property_model(payload.property_id)
        token_data = self.connector.connect_oauth(
            access_token=payload.access_token,
            refresh_token=payload.refresh_token,
            token_scopes=payload.token_scopes,
            token_expires_at=payload.token_expires_at,
        )
        return self._store_oauth_tokens(property_item, token_data, status_text="CONNECTED")

    def refresh_oauth(self, payload: GoogleAnalyticsOAuthRefreshRequest) -> GoogleAnalyticsOAuthResponse:
        """Refresh and store OAuth token data."""

        property_item = self._get_property_model(payload.property_id)
        if not property_item.encrypted_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Aucun refresh token Google Analytics disponible.",
            )
        token_data = self.connector.refresh_oauth(refresh_token=decrypt_secret(property_item.encrypted_refresh_token))
        return self._store_oauth_tokens(property_item, token_data, status_text="REFRESHED")

    def _store_oauth_tokens(
        self,
        property_item: GoogleAnalyticsProperty,
        token_data: GoogleAnalyticsOAuthTokenData,
        *,
        status_text: str,
    ) -> GoogleAnalyticsOAuthResponse:
        data = {
            "encrypted_access_token": encrypt_secret(token_data.access_token),
            "token_expires_at": token_data.token_expires_at,
        }
        if token_data.refresh_token is not None:
            data["encrypted_refresh_token"] = encrypt_secret(token_data.refresh_token)
        updated = self.repository.update(property_item, data)
        return GoogleAnalyticsOAuthResponse(
            property_id=updated.id,
            token_scopes=token_data.token_scopes,
            token_expires_at=updated.token_expires_at,
            status=status_text,
        )

    def _get_property_model(self, property_pk: int) -> GoogleAnalyticsProperty:
        item = self.repository.get_property(property_pk)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propriete Google Analytics introuvable.")
        return item

    def _normalize_names(self, names: list[str], mapping: dict[str, str], label: str) -> list[str]:
        normalized = []
        for name in names:
            key = name.strip().replace("-", "_").replace(" ", "_").lower()
            value = mapping.get(key.replace("_", ""))
            if value is None:
                value = mapping.get(key)
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"{label.capitalize()} Google Analytics non supportee: {name}.",
                )
            if value not in normalized:
                normalized.append(value)
        if not normalized:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Au moins une {label} Google Analytics est requise.",
            )
        return normalized

    def _clean_dimension(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _import_read(self, item: object) -> GoogleAnalyticsImportRead:
        read = GoogleAnalyticsImportRead.model_validate(item)
        return read.model_copy(update={"duration_seconds": self._duration_seconds(read.started_at, read.finished_at)})

    def _duration_seconds(self, started_at: datetime | None, finished_at: datetime | None) -> float | None:
        if started_at is None or finished_at is None:
            return None
        return max((finished_at - started_at).total_seconds(), 0.0)
