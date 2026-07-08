"""Routes d'authentification."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.v1.dependencies import get_current_user
from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.repositories.auth import RoleRepository, UserRepository
from backend.app.repositories.user_invitations import UserInvitationRepository
from backend.app.schemas.auth import (
    AccountActivationRequest,
    AccountActivationResponse,
    LoginRequest,
    TokenResponse,
    UserRead,
)
from backend.app.services.auth import AuthService
from backend.app.services.email import EmailService
from backend.app.services.user_invitations import UserInvitationService

router = APIRouter(prefix="/auth", tags=["Authentification"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Return auth service."""

    return AuthService(UserRepository(db))


def get_user_invitation_service(db: Session = Depends(get_db)) -> UserInvitationService:
    """Return user invitation service."""

    return UserInvitationService(
        UserRepository(db),
        RoleRepository(db),
        UserInvitationRepository(db),
        EmailService(),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion",
    description="Authentifie un utilisateur et retourne un jeton JWT.",
)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Authenticate a user."""

    return service.login(payload)


@router.post(
    "/activate",
    response_model=AccountActivationResponse,
    summary="Activation de compte",
    description="Active un compte invite avec un token d'activation et un nouveau mot de passe.",
)
def activate_account(
    payload: AccountActivationRequest,
    service: UserInvitationService = Depends(get_user_invitation_service),
) -> AccountActivationResponse:
    """Activate an invited account."""

    return service.activate_account(token=payload.token, password=payload.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renouvellement du jeton",
    description="Retourne un nouveau jeton pour l'utilisateur courant.",
)
def refresh(current_user: User = Depends(get_current_user)) -> TokenResponse:
    """Refresh current user token."""

    from backend.app.core.security import create_access_token

    return TokenResponse(access_token=create_access_token(str(current_user.id)))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Utilisateur courant",
    description="Retourne le profil de l'utilisateur authentifié.",
)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return current user."""

    return UserRead.model_validate(current_user)
