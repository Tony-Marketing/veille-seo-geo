"""Outils d'authentification, d'autorisation et de chiffrement."""

import base64
import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)
ADMIN_ROLE = "Administrateur"


def hash_password(password: str) -> str:
    """Hash a plain text password."""

    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""

    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""

    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""

    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide.",
        ) from exc


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Return the current authenticated user."""

    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")
    payload = decode_access_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton incomplet.")
    user = db.get(User, int(subject))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur invalide.")
    return user


def user_has_permission(user: User, permission_code: str) -> bool:
    """Return whether a user owns a permission."""

    if user.is_superadmin:
        return True
    return any(permission.code == permission_code for role in user.roles for permission in role.permissions)


def require_permission(permission_code: str):
    """Build a FastAPI dependency checking one permission."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if not user_has_permission(user, permission_code):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission insuffisante.")
        return user

    return dependency


def require_role(role_name: str):
    """Build a FastAPI dependency checking one role."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.is_superadmin or any(role.name == role_name for role in user.roles):
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant.")

    return dependency


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require a superadmin user or the administrator role."""

    if user.is_superadmin or any(role.name == ADMIN_ROLE for role in user.roles):
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès administrateur requis.")


def _fernet_key() -> bytes:
    secret = settings.api_key_encryption_secret or settings.secret_key
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_secret(value: str) -> str:
    """Encrypt a secret value for database storage."""

    return Fernet(_fernet_key()).encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str) -> str:
    """Decrypt a secret value."""

    return Fernet(_fernet_key()).decrypt(value.encode("utf-8")).decode("utf-8")


def secret_fingerprint(value: str) -> str:
    """Return a non-reversible fingerprint for a secret."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def masked_secret(fingerprint: str) -> str:
    """Return a stable masked representation without exposing the secret."""

    suffix = fingerprint[-6:] if fingerprint else "******"
    return f"********{suffix}"
