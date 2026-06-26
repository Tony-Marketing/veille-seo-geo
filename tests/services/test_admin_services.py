"""Tests des services d'administration."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import decrypt_secret
from backend.app.repositories.admin import AiProviderRepository, ApiKeyRepository
from backend.app.schemas.admin import AiProviderCreate, ApiKeyCreate
from backend.app.services.admin import AiProviderService, ApiKeyService


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
