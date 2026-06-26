"""Services métier du module Administration."""

from datetime import UTC, datetime
from math import ceil
from time import monotonic

import psutil
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import encrypt_secret, masked_secret, secret_fingerprint
from backend.app.models import AiModel, AiProvider, ApiKey, ApplicationSetting, AuditLog, ErrorLog, SystemParameter
from backend.app.repositories.admin import (
    AdminRepository,
    AiModelRepository,
    AiProviderRepository,
    ApiKeyRepository,
    AuditLogRepository,
    ErrorLogRepository,
    SettingRepository,
    SystemParameterRepository,
)
from backend.app.repositories.auth import PermissionRepository, RoleRepository
from backend.app.schemas.admin import (
    AdminDashboardRead,
    AiModelRead,
    AiProviderRead,
    ApiKeyRead,
    AuditLogRead,
    ConfigurationExport,
    ConfigurationImport,
    ConfigurationImportResult,
    ErrorLogRead,
    HealthOverviewRead,
    ServiceHealthRead,
    SettingRead,
    SystemParameterRead,
)
from backend.app.schemas.auth import PermissionRead, RoleRead
from backend.app.schemas.pagination import PaginatedResponse, PaginationParams
from backend.app.services.base import CrudService

STARTED_AT = datetime.now(UTC)
START_MONOTONIC = monotonic()


class SettingService(CrudService[ApplicationSetting, SettingRead]):
    """Business service for global settings."""

    def __init__(self, repository: SettingRepository) -> None:
        super().__init__(repository, SettingRead)

    def create(self, payload: BaseModel) -> SettingRead:
        self._ensure_unique("key", payload.model_dump()["key"])
        return super().create(payload)


class AiProviderService(CrudService[AiProvider, AiProviderRead]):
    """Business service for AI providers."""

    def __init__(self, repository: AiProviderRepository) -> None:
        super().__init__(repository, AiProviderRead)

    def create(self, payload: BaseModel) -> AiProviderRead:
        self._ensure_unique("name", payload.model_dump()["name"])
        return super().create(payload)


class AiModelService(CrudService[AiModel, AiModelRead]):
    """Business service for AI models."""

    def __init__(self, repository: AiModelRepository) -> None:
        super().__init__(repository, AiModelRead)


class ApiKeyService(CrudService[ApiKey, ApiKeyRead]):
    """Business service for encrypted API keys."""

    def __init__(self, repository: ApiKeyRepository) -> None:
        super().__init__(repository, ApiKeyRead)

    def list(self, params: PaginationParams) -> PaginatedResponse[ApiKeyRead]:
        items, total = self.repository.list(params)
        return PaginatedResponse[ApiKeyRead](
            items=[self._to_read(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=ceil(total / params.page_size) if total else 0,
        )

    def get(self, item_id: int) -> ApiKeyRead:
        item = self.repository.get(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clé API introuvable.")
        return self._to_read(item)

    def create(self, payload: BaseModel, user_id: int | None = None) -> ApiKeyRead:
        data = payload.model_dump(exclude_unset=True)
        self._ensure_unique("name", data["name"])
        value = data.pop("value")
        data["encrypted_value"] = encrypt_secret(value)
        data["value_fingerprint"] = secret_fingerprint(value)
        data["created_by_id"] = user_id
        data["updated_by_id"] = user_id
        return self._to_read(self.repository.create(data))

    def update(self, item_id: int, payload: BaseModel, user_id: int | None = None) -> ApiKeyRead:
        item = self.repository.get(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clé API introuvable.")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data:
            self._ensure_unique("name", data["name"], current_id=item_id)
        if "value" in data:
            value = data.pop("value")
            data["encrypted_value"] = encrypt_secret(value)
            data["value_fingerprint"] = secret_fingerprint(value)
        data["updated_by_id"] = user_id
        return self._to_read(self.repository.update(item, data))

    def _to_read(self, item: ApiKey) -> ApiKeyRead:
        return ApiKeyRead(
            id=item.id,
            name=item.name,
            provider_id=item.provider_id,
            provider_name=item.provider_name,
            masked_value=masked_secret(item.value_fingerprint),
            value_fingerprint=item.value_fingerprint,
            last_used_at=item.last_used_at,
            created_by_id=item.created_by_id,
            updated_by_id=item.updated_by_id,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


class AuditLogService(CrudService[AuditLog, AuditLogRead]):
    """Business service for audit logs."""

    def __init__(self, repository: AuditLogRepository) -> None:
        super().__init__(repository, AuditLogRead)


class ErrorLogService(CrudService[ErrorLog, ErrorLogRead]):
    """Business service for error logs."""

    def __init__(self, repository: ErrorLogRepository) -> None:
        super().__init__(repository, ErrorLogRead)


class SystemParameterService(CrudService[SystemParameter, SystemParameterRead]):
    """Business service for SEO/GEO/AI parameters."""

    def __init__(self, repository: SystemParameterRepository) -> None:
        super().__init__(repository, SystemParameterRead)


class AdminService:
    """Aggregate administration service."""

    def __init__(
        self,
        db: Session,
        admin_repository: AdminRepository,
        provider_repository: AiProviderRepository,
        api_key_repository: ApiKeyRepository,
    ) -> None:
        self.db = db
        self.admin_repository = admin_repository
        self.provider_repository = provider_repository
        self.api_key_repository = api_key_repository

    def dashboard(self) -> AdminDashboardRead:
        """Build the administration dashboard."""

        return AdminDashboardRead(
            websites_count=self.admin_repository.websites_count(),
            users_count=self.admin_repository.users_count(),
            active_ai_providers_count=self.provider_repository.count_active(),
            configured_api_keys_count=self.api_key_repository.count_configured(),
            postgresql_status=self._database_status(),
            application_version=settings.app_version,
            database_version=self._database_version(),
            environment=settings.environment,
            started_at=STARTED_AT,
            uptime_seconds=int(monotonic() - START_MONOTONIC),
            applied_migrations_count=self._migrations_count(),
        )

    def _database_status(self) -> str:
        try:
            self.db.execute(text("SELECT 1"))
        except Exception:
            return "Critical"
        return "Healthy"

    def _database_version(self) -> str | None:
        try:
            if self.db.bind and self.db.bind.dialect.name == "postgresql":
                return str(self.db.scalar(text("SELECT version()")))
        except Exception:
            return None
        return self.db.bind.dialect.name if self.db.bind else None

    def _migrations_count(self) -> int:
        try:
            return int(self.db.scalar(text("SELECT COUNT(*) FROM alembic_version")) or 0)
        except Exception:
            return 0


class HealthService:
    """Business health checks service."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def overview(self) -> HealthOverviewRead:
        """Return service health overview."""

        services = [
            self._database_health(),
            self._system_metric("disk", psutil.disk_usage(".").percent),
            self._system_metric("memory", psutil.virtual_memory().percent),
            self._system_metric("cpu", psutil.cpu_percent(interval=0.0)),
            ServiceHealthRead(name="Redis", status="Warning", details={"configured": False}),
            ServiceHealthRead(name="API OpenAI", status="Warning", details={"configured": False}),
            ServiceHealthRead(name="API Anthropic", status="Warning", details={"configured": False}),
            ServiceHealthRead(name="API Gemini", status="Warning", details={"configured": False}),
            ServiceHealthRead(name="API GitHub", status="Warning", details={"configured": False}),
        ]
        return HealthOverviewRead(services=services)

    def _database_health(self) -> ServiceHealthRead:
        try:
            self.db.execute(text("SELECT 1"))
        except Exception as exc:
            return ServiceHealthRead(name="PostgreSQL", status="Critical", details={"error": str(exc)})
        return ServiceHealthRead(name="PostgreSQL", status="Healthy")

    def _system_metric(self, name: str, percent: float) -> ServiceHealthRead:
        if percent >= 90:
            status_value = "Critical"
        elif percent >= 75:
            status_value = "Warning"
        else:
            status_value = "Healthy"
        return ServiceHealthRead(name=name, status=status_value, details={"usage_percent": percent})


class ConfigurationService:
    """Business service for configuration import and export."""

    def __init__(
        self,
        setting_repository: SettingRepository,
        provider_repository: AiProviderRepository,
        model_repository: AiModelRepository,
        parameter_repository: SystemParameterRepository,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self.setting_repository = setting_repository
        self.provider_repository = provider_repository
        self.model_repository = model_repository
        self.parameter_repository = parameter_repository
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    def export(self) -> ConfigurationExport:
        """Export non-secret configuration."""

        settings_items = self._list_all(self.setting_repository)
        providers = self._list_all(self.provider_repository)
        models = self._list_all(self.model_repository)
        parameters = self._list_all(self.parameter_repository)
        roles = self._list_all(self.role_repository)
        permissions = self._list_all(self.permission_repository)
        return ConfigurationExport(
            settings=[SettingRead.model_validate(item) for item in settings_items],
            ai_providers=[AiProviderRead.model_validate(item) for item in providers],
            ai_models=[AiModelRead.model_validate(item) for item in models],
            system_parameters=[SystemParameterRead.model_validate(item) for item in parameters],
            roles=[RoleRead.model_validate(item) for item in roles],
            permissions=[PermissionRead.model_validate(item) for item in permissions],
        )

    def import_config(self, payload: ConfigurationImport) -> ConfigurationImportResult:
        """Import configuration with idempotent upserts and no destructive delete."""

        created = self._empty_import_counts()
        updated = self._empty_import_counts()
        skipped = self._empty_import_counts()

        for item in payload.settings:
            self._upsert_by_field(
                self.setting_repository,
                "key",
                item.model_dump(exclude_unset=True),
                created,
                updated,
                "settings",
            )

        for item in payload.ai_providers:
            self._upsert_by_field(
                self.provider_repository,
                "name",
                item.model_dump(exclude_unset=True),
                created,
                updated,
                "ai_providers",
            )

        permission_payloads = {item.code: item for item in payload.permissions}
        for role in payload.roles:
            for permission in role.permissions:
                permission_payloads.setdefault(permission.code, permission)
        for item in permission_payloads.values():
            self._upsert_by_field(
                self.permission_repository,
                "code",
                item.model_dump(exclude_unset=True),
                created,
                updated,
                "permissions",
            )

        for item in payload.system_parameters:
            data = item.model_dump(exclude_unset=True)
            existing = self.parameter_repository.get_by_category_key(data["category"], data["key"])
            if existing is None:
                self.parameter_repository.create(data)
                created["system_parameters"] += 1
            else:
                self.parameter_repository.update(existing, data)
                updated["system_parameters"] += 1

        for item in payload.ai_models:
            data = item.model_dump(exclude_unset=True)
            if self.provider_repository.get(data["provider_id"]) is None:
                skipped["ai_models"] += 1
                continue
            self._upsert_by_field(
                self.model_repository,
                "api_identifier",
                data,
                created,
                updated,
                "ai_models",
            )

        for item in payload.roles:
            data = item.model_dump(exclude={"permission_ids", "permissions"}, exclude_unset=True)
            role = self.role_repository.get_by_field("name", data["name"])
            if role is None:
                role = self.role_repository.create(data)
                created["roles"] += 1
            else:
                role = self.role_repository.update(role, data)
                updated["roles"] += 1

            permission_ids = list(item.permission_ids)
            for permission in item.permissions:
                stored_permission = self.permission_repository.get_by_field("code", permission.code)
                if stored_permission is not None:
                    permission_ids.append(stored_permission.id)
            role.permissions = self.permission_repository.list_by_ids(sorted(set(permission_ids)))
            self.role_repository.db.commit()
            self.role_repository.db.refresh(role)

        return ConfigurationImportResult(created=created, updated=updated, skipped=skipped)

    def _list_all(self, repository: SettingRepository) -> list:
        page = 1
        items = []
        while True:
            batch, total = repository.list(PaginationParams(page=page, page_size=100))
            items.extend(batch)
            if len(items) >= total or not batch:
                return items
            page += 1

    def _upsert_by_field(
        self,
        repository: SettingRepository,
        field_name: str,
        data: dict,
        created: dict[str, int],
        updated: dict[str, int],
        counter_key: str,
    ) -> None:
        existing = repository.get_by_field(field_name, data[field_name])
        if existing is None:
            repository.create(data)
            created[counter_key] += 1
            return
        repository.update(existing, data)
        updated[counter_key] += 1

    def _empty_import_counts(self) -> dict[str, int]:
        return {
            "settings": 0,
            "ai_providers": 0,
            "ai_models": 0,
            "system_parameters": 0,
            "roles": 0,
            "permissions": 0,
        }
