"""Tests des services d'administration."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import decrypt_secret
from backend.app.repositories.admin import (
    AiModelRepository,
    AiProviderRepository,
    ApiKeyRepository,
    SettingRepository,
    SystemParameterRepository,
)
from backend.app.repositories.auth import PermissionRepository, RoleRepository
from backend.app.schemas.admin import (
    AiProviderCreate,
    ApiKeyCreate,
    ConfigurationImport,
    ConfigurationPermissionImport,
    ConfigurationRoleImport,
    SettingCreate,
    SystemParameterCreate,
)
from backend.app.services.admin import AiProviderService, ApiKeyService, ConfigurationService


def test_api_key_service_encrypts_and_masks_value(db_session: Session) -> None:
    """API keys are encrypted and never returned in clear text."""

    service = ApiKeyService(ApiKeyRepository(db_session))
    result = service.create(ApiKeyCreate(name="OpenAI", provider_name="OpenAI", value="sk-secret"))
    stored = ApiKeyRepository(db_session).get(result.id)

    assert stored is not None
    assert stored.encrypted_value != "sk-secret"
    assert decrypt_secret(stored.encrypted_value) == "sk-secret"
    assert result.masked_value != "sk-secret"


def test_ai_provider_service_rejects_duplicate_name(db_session: Session) -> None:
    """AI provider names must stay unique."""

    service = AiProviderService(AiProviderRepository(db_session))
    service.create(AiProviderCreate(name="OpenAI"))

    try:
        service.create(AiProviderCreate(name="OpenAI"))
    except HTTPException as exc:
        assert exc.status_code == 409
    else:
        raise AssertionError("duplicate provider should fail")


def test_configuration_service_imports_idempotently(db_session: Session) -> None:
    """Configuration import creates then updates known resources without deleting anything."""

    service = ConfigurationService(
        SettingRepository(db_session),
        AiProviderRepository(db_session),
        AiModelRepository(db_session),
        SystemParameterRepository(db_session),
        RoleRepository(db_session),
        PermissionRepository(db_session),
    )
    payload = ConfigurationImport(
        settings=[SettingCreate(key="app.language", value="fr", category="global", is_public=True)],
        ai_providers=[AiProviderCreate(name="OpenAI")],
        system_parameters=[SystemParameterCreate(category="seo", key="crawler.user_agent", value="VeilleBot")],
        permissions=[
            ConfigurationPermissionImport(code="admin.read", label="Lire administration", module="admin"),
        ],
        roles=[
            ConfigurationRoleImport(
                name="Administrateur",
                is_system=True,
                permissions=[
                    ConfigurationPermissionImport(code="admin.read", label="Lire administration", module="admin"),
                ],
            ),
        ],
    )

    first_result = service.import_config(payload)
    second_result = service.import_config(payload)
    exported = service.export()

    assert first_result.created["settings"] == 1
    assert first_result.created["permissions"] == 1
    assert second_result.updated["settings"] == 1
    assert second_result.updated["roles"] == 1
    assert exported.settings[0].key == "app.language"
    assert exported.roles[0].permissions[0].code == "admin.read"
