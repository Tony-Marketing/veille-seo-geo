"""Routes FastAPI du module Administration."""

from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models import User
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
    AiModelCreate,
    AiModelList,
    AiModelRead,
    AiModelUpdate,
    AiProviderCreate,
    AiProviderList,
    AiProviderRead,
    AiProviderUpdate,
    ApiKeyCreate,
    ApiKeyList,
    ApiKeyRead,
    ApiKeyUpdate,
    AuditLogCreate,
    AuditLogList,
    AuditLogRead,
    ConfigurationExport,
    ConfigurationImport,
    ConfigurationImportResult,
    ErrorLogCreate,
    ErrorLogList,
    ErrorLogRead,
    ErrorLogUpdate,
    HealthOverviewRead,
    SettingCreate,
    SettingList,
    SettingRead,
    SettingUpdate,
    SystemParameterCreate,
    SystemParameterList,
    SystemParameterRead,
    SystemParameterUpdate,
)
from backend.app.schemas.pagination import PaginationParams, pagination_params
from backend.app.services.admin import (
    AdminService,
    AiModelService,
    AiProviderService,
    ApiKeyService,
    AuditLogService,
    ConfigurationService,
    ErrorLogService,
    HealthService,
    SettingService,
    SystemParameterService,
)

router = APIRouter(prefix="/admin", tags=["Administration"])


def _setting_service(db: Session) -> SettingService:
    return SettingService(SettingRepository(db))


def _provider_service(db: Session) -> AiProviderService:
    return AiProviderService(AiProviderRepository(db))


def _model_service(db: Session) -> AiModelService:
    return AiModelService(AiModelRepository(db))


def _api_key_service(db: Session) -> ApiKeyService:
    return ApiKeyService(ApiKeyRepository(db))


def _audit_service(db: Session) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


def _error_service(db: Session) -> ErrorLogService:
    return ErrorLogService(ErrorLogRepository(db))


def _parameter_service(db: Session) -> SystemParameterService:
    return SystemParameterService(SystemParameterRepository(db))


@router.get(
    "/dashboard",
    response_model=AdminDashboardRead,
    summary="Dashboard d'administration",
    description="Retourne les indicateurs techniques et fonctionnels du backend.",
)
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> AdminDashboardRead:
    service = AdminService(db, AdminRepository(db), AiProviderRepository(db), ApiKeyRepository(db))
    return service.dashboard()


@router.get("/settings", response_model=SettingList, summary="Lister les paramètres globaux")
def list_settings(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _setting_service(db).list(params)


@router.post(
    "/settings",
    response_model=SettingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un paramètre",
)
def create_setting(
    payload: SettingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SettingRead:
    return _setting_service(db).create(payload)


@router.put("/settings/{setting_id}", response_model=SettingRead, summary="Modifier un paramètre")
def update_setting(
    setting_id: int,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SettingRead:
    return _setting_service(db).update(setting_id, payload)


@router.delete("/settings/{setting_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un paramètre")
def delete_setting(setting_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Response:
    _setting_service(db).delete(setting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/ai-providers", response_model=AiProviderList, summary="Lister les fournisseurs IA")
def list_ai_providers(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _provider_service(db).list(params)


@router.post(
    "/ai-providers",
    response_model=AiProviderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un fournisseur IA",
)
def create_ai_provider(
    payload: AiProviderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AiProviderRead:
    return _provider_service(db).create(payload)


@router.put("/ai-providers/{provider_id}", response_model=AiProviderRead, summary="Modifier un fournisseur IA")
def update_ai_provider(
    provider_id: int,
    payload: AiProviderUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AiProviderRead:
    return _provider_service(db).update(provider_id, payload)


@router.delete(
    "/ai-providers/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un fournisseur IA",
)
def delete_ai_provider(provider_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Response:
    _provider_service(db).delete(provider_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/ai-models", response_model=AiModelList, summary="Lister les modèles IA")
def list_ai_models(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _model_service(db).list(params)


@router.post(
    "/ai-models",
    response_model=AiModelRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un modèle IA",
)
def create_ai_model(
    payload: AiModelCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AiModelRead:
    return _model_service(db).create(payload)


@router.put("/ai-models/{model_id}", response_model=AiModelRead, summary="Modifier un modèle IA")
def update_ai_model(
    model_id: int,
    payload: AiModelUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AiModelRead:
    return _model_service(db).update(model_id, payload)


@router.delete("/ai-models/{model_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un modèle IA")
def delete_ai_model(model_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Response:
    _model_service(db).delete(model_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api-keys", response_model=ApiKeyList, summary="Lister les clés API")
def list_api_keys(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _api_key_service(db).list(params)


@router.post(
    "/api-keys",
    response_model=ApiKeyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une clé API",
)
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> ApiKeyRead:
    return _api_key_service(db).create(payload, user_id=user.id)


@router.put("/api-keys/{api_key_id}", response_model=ApiKeyRead, summary="Modifier une clé API")
def update_api_key(
    api_key_id: int,
    payload: ApiKeyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> ApiKeyRead:
    return _api_key_service(db).update(api_key_id, payload, user_id=user.id)


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer une clé API")
def delete_api_key(api_key_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Response:
    _api_key_service(db).delete(api_key_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/audit-logs", response_model=AuditLogList, summary="Lister le journal d'audit")
def list_audit_logs(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _audit_service(db).list(params)


@router.post(
    "/audit-logs",
    response_model=AuditLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un audit log",
)
def create_audit_log(
    payload: AuditLogCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AuditLogRead:
    return _audit_service(db).create(payload)


@router.get("/error-logs", response_model=ErrorLogList, summary="Lister le journal des erreurs")
def list_error_logs(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _error_service(db).list(params)


@router.post(
    "/error-logs",
    response_model=ErrorLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un error log",
)
def create_error_log(
    payload: ErrorLogCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ErrorLogRead:
    return _error_service(db).create(payload)


@router.put("/error-logs/{error_log_id}", response_model=ErrorLogRead, summary="Modifier un error log")
def update_error_log(
    error_log_id: int,
    payload: ErrorLogUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ErrorLogRead:
    return _error_service(db).update(error_log_id, payload)


@router.get("/system-parameters", response_model=SystemParameterList, summary="Lister les paramètres SEO/GEO/IA")
def list_system_parameters(
    params: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Any:
    return _parameter_service(db).list(params)


@router.post(
    "/system-parameters",
    response_model=SystemParameterRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un paramètre SEO/GEO/IA",
)
def create_system_parameter(
    payload: SystemParameterCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SystemParameterRead:
    return _parameter_service(db).create(payload)


@router.put(
    "/system-parameters/{parameter_id}",
    response_model=SystemParameterRead,
    summary="Modifier un paramètre SEO/GEO/IA",
)
def update_system_parameter(
    parameter_id: int,
    payload: SystemParameterUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> SystemParameterRead:
    return _parameter_service(db).update(parameter_id, payload)


@router.get("/health", response_model=HealthOverviewRead, summary="Santé des services")
def health(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> HealthOverviewRead:
    return HealthService(db).overview()


@router.get("/config/export", response_model=ConfigurationExport, summary="Exporter la configuration")
def export_configuration(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> ConfigurationExport:
    service = ConfigurationService(
        SettingRepository(db),
        AiProviderRepository(db),
        AiModelRepository(db),
        SystemParameterRepository(db),
        RoleRepository(db),
        PermissionRepository(db),
    )
    return service.export()


@router.post("/config/import", response_model=ConfigurationImportResult, summary="Importer la configuration")
def import_configuration(
    payload: ConfigurationImport,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> ConfigurationImportResult:
    service = ConfigurationService(
        SettingRepository(db),
        AiProviderRepository(db),
        AiModelRepository(db),
        SystemParameterRepository(db),
        RoleRepository(db),
        PermissionRepository(db),
    )
    return service.import_config(payload)
