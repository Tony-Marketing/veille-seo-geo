"""Routes Permissions."""

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.repositories.auth import PermissionRepository
from backend.app.schemas.auth import PermissionCreate, PermissionList, PermissionRead, PermissionUpdate
from backend.app.services.auth import PermissionService

router = create_crud_router(
    prefix="/permissions",
    tags=["Permissions"],
    repository_class=PermissionRepository,
    service_class=PermissionService,
    create_schema=PermissionCreate,
    update_schema=PermissionUpdate,
    read_schema=PermissionRead,
    list_schema=PermissionList,
)
