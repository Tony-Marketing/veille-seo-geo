"""Routes Utilisateurs."""

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.api.v1.routes.factory import create_crud_router
from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.repositories.auth import RoleRepository, UserRepository
from backend.app.schemas.auth import UserCreate, UserList, UserRead, UserUpdate
from backend.app.services.auth import UserService


class UserServiceFactory:
    def __call__(self, db: Session = Depends(get_db)) -> UserService:
        return UserService(UserRepository(db), RoleRepository(db))


router = create_crud_router(
    prefix="/users",
    tags=["Utilisateurs"],
    repository_class=UserRepository,
    service_class=UserServiceFactory(),
    create_schema=UserCreate,
    update_schema=UserUpdate,
    read_schema=UserRead,
    list_schema=UserList,
    dependencies=[Depends(require_admin)],
)
