"""Schémas Pydantic d'authentification."""

from pydantic import BaseModel, EmailStr, Field

from backend.app.schemas.common import TimestampRead
from backend.app.schemas.pagination import PaginatedResponse


class PermissionCreate(BaseModel):
    """Payload de création de permission."""

    code: str = Field(min_length=2, max_length=150)
    label: str = Field(min_length=2, max_length=150)
    module: str = Field(min_length=2, max_length=100)
    description: str | None = None


class PermissionUpdate(BaseModel):
    """Payload de modification de permission."""

    code: str | None = Field(default=None, min_length=2, max_length=150)
    label: str | None = Field(default=None, min_length=2, max_length=150)
    module: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None


class PermissionRead(TimestampRead):
    """Permission exposée par l'API."""

    id: int
    code: str
    label: str
    module: str
    description: str | None


class RoleCreate(BaseModel):
    """Payload de création de rôle."""

    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    is_system: bool = False
    permission_ids: list[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Payload de modification de rôle."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    is_system: bool | None = None
    permission_ids: list[int] | None = None


class RoleRead(TimestampRead):
    """Rôle exposé par l'API."""

    id: int
    name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionRead] = Field(default_factory=list)


class UserCreate(BaseModel):
    """Payload de création utilisateur."""

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    is_active: bool = True
    is_superadmin: bool = False
    role_ids: list[int] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Payload de modification utilisateur."""

    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None
    is_superadmin: bool | None = None
    role_ids: list[int] | None = None


class UserRead(TimestampRead):
    """Utilisateur exposé par l'API."""

    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_superadmin: bool
    roles: list[RoleRead] = Field(default_factory=list)


class LoginRequest(BaseModel):
    """Payload de connexion."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Réponse d'authentification JWT."""

    access_token: str
    token_type: str = "bearer"


PermissionList = PaginatedResponse[PermissionRead]
RoleList = PaginatedResponse[RoleRead]
UserList = PaginatedResponse[UserRead]
