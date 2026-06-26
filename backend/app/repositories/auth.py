"""Repositories d'authentification."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import AuditLog, Permission, Role, User
from backend.app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for permissions."""

    search_fields = ("code", "label", "module")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Permission)

    def list_by_ids(self, permission_ids: list[int]) -> list[Permission]:
        """Return permissions matching ids."""

        if not permission_ids:
            return []
        return list(self.db.scalars(select(Permission).where(Permission.id.in_(permission_ids))))


class RoleRepository(BaseRepository[Role]):
    """Repository for roles."""

    search_fields = ("name", "description")

    def __init__(self, db: Session) -> None:
        super().__init__(db, Role)

    def list_by_ids(self, role_ids: list[int]) -> list[Role]:
        """Return roles matching ids."""

        if not role_ids:
            return []
        return list(self.db.scalars(select(Role).where(Role.id.in_(role_ids))))


class UserRepository(BaseRepository[User]):
    """Repository for users."""

    search_fields = ("email", "first_name", "last_name")

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        """Return a user by email."""

        return self.db.scalar(select(User).where(User.email == email))


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for audit logs."""

    search_fields = ("module", "action", "level", "result")

    def __init__(self, db: Session) -> None:
        super().__init__(db, AuditLog)
