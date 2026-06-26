"""Dépendances FastAPI d'authentification et d'autorisation."""

from backend.app.core.security import get_current_user, require_admin, require_permission, require_role

__all__ = ["get_current_user", "require_admin", "require_permission", "require_role"]
