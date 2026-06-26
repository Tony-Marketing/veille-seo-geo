"""Schémas Pydantic du module Administration."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from backend.app.schemas.auth import PermissionRead, RoleRead
from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class SettingCreate(BaseModel):
    key: str = Field(min_length=2, max_length=150)
    value: str | None = None
    value_type: str = Field(default="string", max_length=30)
    category: str = Field(default="global", max_length=80)
    description: str | None = None
    is_public: bool = False


class SettingUpdate(BaseModel):
    value: str | None = None
    value_type: str | None = Field(default=None, max_length=30)
    category: str | None = Field(default=None, max_length=80)
    description: str | None = None
    is_public: bool | None = None


class SettingRead(TimestampRead):
    id: int
    key: str
    value: str | None
    value_type: str
    category: str
    description: str | None
    is_public: bool


class AiProviderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    website_url: str | None = Field(default=None, max_length=255)
    documentation_url: str | None = Field(default=None, max_length=255)
    default_model: str | None = Field(default=None, max_length=120)
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    max_concurrent_requests: int = Field(default=5, ge=1, le=100)
    is_active: bool = True


class AiProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    website_url: str | None = Field(default=None, max_length=255)
    documentation_url: str | None = Field(default=None, max_length=255)
    default_model: str | None = Field(default=None, max_length=120)
    timeout_seconds: int | None = Field(default=None, ge=1, le=600)
    max_concurrent_requests: int | None = Field(default=None, ge=1, le=100)
    is_active: bool | None = None


class AiProviderRead(TimestampRead):
    id: int
    name: str
    description: str | None
    website_url: str | None
    documentation_url: str | None
    default_model: str | None
    timeout_seconds: int
    max_concurrent_requests: int
    is_active: bool


class AiModelCreate(BaseModel):
    provider_id: int
    name: str = Field(min_length=2, max_length=150)
    api_identifier: str = Field(min_length=2, max_length=150)
    input_cost: float | None = Field(default=None, ge=0)
    output_cost: float | None = Field(default=None, ge=0)
    max_context_tokens: int | None = Field(default=None, ge=1)
    is_active: bool = True


class AiModelUpdate(BaseModel):
    provider_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=150)
    api_identifier: str | None = Field(default=None, min_length=2, max_length=150)
    input_cost: float | None = Field(default=None, ge=0)
    output_cost: float | None = Field(default=None, ge=0)
    max_context_tokens: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class AiModelRead(TimestampRead):
    id: int
    provider_id: int
    name: str
    api_identifier: str
    input_cost: float | None
    output_cost: float | None
    max_context_tokens: int | None
    is_active: bool


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    provider_id: int | None = None
    provider_name: str | None = Field(default=None, max_length=120)
    value: str = Field(min_length=1)
    is_active: bool = True


class ApiKeyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    provider_id: int | None = None
    provider_name: str | None = Field(default=None, max_length=120)
    value: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class ApiKeyRead(TimestampRead):
    id: int
    name: str
    provider_id: int | None
    provider_name: str | None
    masked_value: str
    value_fingerprint: str
    last_used_at: datetime | None
    created_by_id: int | None
    updated_by_id: int | None
    is_active: bool


class AuditLogCreate(BaseModel):
    user_id: int | None = None
    module: str = Field(min_length=2, max_length=100)
    action: str = Field(min_length=2, max_length=120)
    level: str = Field(default="info", max_length=30)
    ip_address: str | None = Field(default=None, max_length=80)
    user_agent: str | None = Field(default=None, max_length=255)
    result: str = Field(default="success", max_length=50)
    duration_ms: int | None = Field(default=None, ge=0)
    details: dict[str, Any] | None = None


class AuditLogUpdate(BaseModel):
    details: dict[str, Any] | None = None


class AuditLogRead(TimestampRead):
    id: int
    user_id: int | None
    module: str
    action: str
    level: str
    ip_address: str | None
    user_agent: str | None
    result: str
    duration_ms: int | None
    details: dict[str, Any] | None


class ErrorLogCreate(BaseModel):
    exception: str = Field(min_length=2, max_length=255)
    traceback: str | None = None
    endpoint: str | None = Field(default=None, max_length=255)
    user_id: int | None = None
    environment: str = Field(default="development", max_length=50)
    level: str = Field(default="error", max_length=30)
    is_resolved: bool = False
    comment: str | None = None


class ErrorLogUpdate(BaseModel):
    is_resolved: bool | None = None
    comment: str | None = None


class ErrorLogRead(TimestampRead):
    id: int
    exception: str
    traceback: str | None
    endpoint: str | None
    user_id: int | None
    environment: str
    level: str
    is_resolved: bool
    comment: str | None


class SystemParameterCreate(BaseModel):
    category: Literal["seo", "geo", "ai"]
    key: str = Field(min_length=2, max_length=150)
    value: str | None = None
    value_type: str = Field(default="string", max_length=30)
    description: str | None = None


class SystemParameterUpdate(BaseModel):
    value: str | None = None
    value_type: str | None = Field(default=None, max_length=30)
    description: str | None = None


class SystemParameterRead(TimestampRead):
    id: int
    category: str
    key: str
    value: str | None
    value_type: str
    description: str | None


class AdminDashboardRead(BaseModel):
    websites_count: int
    users_count: int
    active_ai_providers_count: int
    configured_api_keys_count: int
    postgresql_status: str
    application_version: str
    database_version: str | None
    environment: str
    started_at: datetime
    uptime_seconds: int
    applied_migrations_count: int


class ServiceHealthRead(BaseModel):
    name: str
    status: Literal["Healthy", "Warning", "Critical"]
    details: dict[str, Any] = Field(default_factory=dict)


class HealthOverviewRead(BaseModel):
    services: list[ServiceHealthRead]


class ConfigurationExport(BaseModel):
    settings: list[SettingRead]
    ai_providers: list[AiProviderRead]
    ai_models: list[AiModelRead]
    system_parameters: list[SystemParameterRead]
    roles: list[RoleRead]
    permissions: list[PermissionRead]


SettingList = PaginatedResponse[SettingRead]
AiProviderList = PaginatedResponse[AiProviderRead]
AiModelList = PaginatedResponse[AiModelRead]
ApiKeyList = PaginatedResponse[ApiKeyRead]
AuditLogList = PaginatedResponse[AuditLogRead]
ErrorLogList = PaginatedResponse[ErrorLogRead]
SystemParameterList = PaginatedResponse[SystemParameterRead]
