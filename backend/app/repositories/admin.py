"""Repositories du module Administration."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    AiModel,
    AiProvider,
    ApiKey,
    ApplicationSetting,
    AuditLog,
    ErrorLog,
    Permission,
    Role,
    SystemParameter,
    User,
    Website,
)
from backend.app.repositories.base import BaseRepository
from backend.app.schemas.pagination import PaginationParams


class SettingRepository(BaseRepository[ApplicationSetting]):
    """Repository for global settings."""

    search_fields = ("key", "value", "category", "description")

    def __init__(self, db: Session) -> None:
        super().__init__(db, ApplicationSetting)

    def get_by_key(self, key: str) -> ApplicationSetting | None:
        """Return a setting by key."""

        return self.get_by_field("key", key)


class AiProviderRepository(BaseRepository[AiProvider]):
    """Repository for AI providers."""

    search_fields = ("name", "description", "default_model")

    def __init__(self, db: Session) -> None:
        super().__init__(db, AiProvider)

    def count_active(self) -> int:
        """Return active provider count."""

        return int(self.db.scalar(select(func.count()).where(AiProvider.is_active.is_(True))) or 0)


class AiModelRepository(BaseRepository[AiModel]):
    """Repository for AI models."""

    search_fields = ("name", "api_identifier")

    def __init__(self, db: Session) -> None:
        super().__init__(db, AiModel)

    def list_for_provider(self, provider_id: int, params: PaginationParams) -> tuple[list[AiModel], int]:
        """Return models for a provider."""

        statement = select(AiModel).where(AiModel.provider_id == provider_id)
        count_statement = select(func.count()).select_from(AiModel).where(AiModel.provider_id == provider_id)
        filters = self._search_filters(params.search)
        if filters is not None:
            statement = statement.where(filters)
            count_statement = count_statement.where(filters)
        statement = statement.offset(params.offset).limit(params.page_size)
        return list(self.db.scalars(statement)), int(self.db.scalar(count_statement) or 0)


class ApiKeyRepository(BaseRepository[ApiKey]):
    """Repository for encrypted API keys."""

    search_fields = ("name", "provider_name")

    def __init__(self, db: Session) -> None:
        super().__init__(db, ApiKey)

    def count_configured(self) -> int:
        """Return active configured key count."""

        return int(self.db.scalar(select(func.count()).where(ApiKey.is_active.is_(True))) or 0)


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit logs."""

    search_fields = ("module", "action", "level", "result")

    def __init__(self, db: Session) -> None:
        super().__init__(db, AuditLog)


class ErrorLogRepository(BaseRepository[ErrorLog]):
    """Repository for error logs."""

    search_fields = ("exception", "endpoint", "environment", "level", "comment")

    def __init__(self, db: Session) -> None:
        super().__init__(db, ErrorLog)


class SystemParameterRepository(BaseRepository[SystemParameter]):
    """Repository for SEO/GEO/AI parameters."""

    search_fields = ("category", "key", "value", "description")

    def __init__(self, db: Session) -> None:
        super().__init__(db, SystemParameter)

    def get_by_category_key(self, category: str, key: str) -> SystemParameter | None:
        """Return one parameter by category and key."""

        return self.db.scalar(
            select(SystemParameter).where(SystemParameter.category == category, SystemParameter.key == key),
        )


class AdminRepository:
    """Read-only aggregate repository for administration dashboard."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def websites_count(self) -> int:
        """Return website count."""

        return int(self.db.scalar(select(func.count()).select_from(Website)) or 0)

    def users_count(self) -> int:
        """Return user count."""

        return int(self.db.scalar(select(func.count()).select_from(User)) or 0)

    def roles_count(self) -> int:
        """Return role count."""

        return int(self.db.scalar(select(func.count()).select_from(Role)) or 0)

    def permissions_count(self) -> int:
        """Return permission count."""

        return int(self.db.scalar(select(func.count()).select_from(Permission)) or 0)
