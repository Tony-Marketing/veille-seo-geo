"""Routes Rôles."""

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.repositories.auth import PermissionRepository, RoleRepository
from backend.app.schemas.auth import RoleCreate, RoleList, RoleRead, RoleUpdate
from backend.app.services.auth import RoleService


class RoleServiceFactory:
    def __call__(self, db: Session = Depends(get_db)) -> RoleService:
        return RoleService(RoleRepository(db), PermissionRepository(db))


router = create_crud_router(
    prefix="/roles",
    tags=["Rôles"],
    repository_class=RoleRepository,
    service_class=RoleServiceFactory(),
    create_schema=RoleCreate,
    update_schema=RoleUpdate,
    read_schema=RoleRead,
    list_schema=RoleList,
    dependencies=[Depends(require_admin)],
)
