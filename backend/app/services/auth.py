"""Services métier d'authentification et d'autorisation."""

from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.models import Permission, Role, User
from backend.app.repositories.auth import PermissionRepository, RoleRepository, UserRepository
from backend.app.schemas.auth import LoginRequest, PermissionRead, RoleRead, TokenResponse, UserRead
from backend.app.services.base import CrudService


class PermissionService(CrudService[Permission, PermissionRead]):
    """Business service for permissions."""

    def __init__(self, repository: PermissionRepository) -> None:
        super().__init__(repository, PermissionRead)

    def create(self, payload: BaseModel) -> PermissionRead:
        self._ensure_unique("code", payload.model_dump()["code"])
        return super().create(payload)


class RoleService(CrudService[Role, RoleRead]):
    """Business service for roles."""

    def __init__(self, repository: RoleRepository, permission_repository: PermissionRepository | None = None) -> None:
        super().__init__(repository, RoleRead)
        self.permission_repository = permission_repository

    def create(self, payload: BaseModel) -> RoleRead:
        data = payload.model_dump(exclude_unset=True)
        self._ensure_unique("name", data["name"])
        permission_ids = data.pop("permission_ids", [])
        role = self.repository.create(data)
        if self.permission_repository is not None:
            role.permissions = self.permission_repository.list_by_ids(permission_ids)
            self.repository.db.commit()
            self.repository.db.refresh(role)
        return RoleRead.model_validate(role)

    def update(self, item_id: int, payload: BaseModel) -> RoleRead:
        data = payload.model_dump(exclude_unset=True)
        role = self.repository.get(item_id)
        if role is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle introuvable.")
        if "name" in data:
            self._ensure_unique("name", data["name"], current_id=item_id)
        permission_ids = data.pop("permission_ids", None)
        role = self.repository.update(role, data)
        if permission_ids is not None and self.permission_repository is not None:
            role.permissions = self.permission_repository.list_by_ids(permission_ids)
            self.repository.db.commit()
            self.repository.db.refresh(role)
        return RoleRead.model_validate(role)


class UserService(CrudService[User, UserRead]):
    """Business service for users."""

    def __init__(self, repository: UserRepository, role_repository: RoleRepository | None = None) -> None:
        super().__init__(repository, UserRead)
        self.role_repository = role_repository

    def create(self, payload: BaseModel) -> UserRead:
        data = payload.model_dump(exclude_unset=True)
        self._ensure_unique("email", data["email"])
        role_ids = data.pop("role_ids", [])
        data["password_hash"] = hash_password(data.pop("password"))
        user = self.repository.create(data)
        if self.role_repository is not None:
            user.roles = self.role_repository.list_by_ids(role_ids)
            self.repository.db.commit()
            self.repository.db.refresh(user)
        return UserRead.model_validate(user)

    def update(self, item_id: int, payload: BaseModel) -> UserRead:
        data = payload.model_dump(exclude_unset=True)
        user = self.repository.get(item_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
        if "email" in data:
            self._ensure_unique("email", data["email"], current_id=item_id)
        role_ids = data.pop("role_ids", None)
        if "password" in data:
            data["password_hash"] = hash_password(data.pop("password"))
        user = self.repository.update(user, data)
        if role_ids is not None and self.role_repository is not None:
            user.roles = self.role_repository.list_by_ids(role_ids)
            self.repository.db.commit()
            self.repository.db.refresh(user)
        return UserRead.model_validate(user)


class AuthService:
    """Authentication service."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Authenticate a user and return a token."""

        user = self.user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides.")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Utilisateur désactivé.")
        return TokenResponse(access_token=create_access_token(str(user.id)))
