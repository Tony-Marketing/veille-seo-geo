"""Service metier des invitations utilisateur."""

import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from backend.app.core.security import hash_password, secret_fingerprint
from backend.app.models import User, UserInvitation
from backend.app.repositories.auth import RoleRepository, UserRepository
from backend.app.repositories.user_invitations import UserInvitationRepository
from backend.app.schemas.auth import AccountActivationResponse, UserInvitationCreate, UserInvitationRead
from backend.app.services.email import EmailDeliveryError, EmailService

INVITATION_TTL = timedelta(hours=24)


class UserInvitationService:
    """Orchestrate user invitations and account activation."""

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        invitation_repository: UserInvitationRepository,
        email_service: EmailService,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.invitation_repository = invitation_repository
        self.email_service = email_service

    def invite_user(self, payload: UserInvitationCreate, created_by_user_id: int | None) -> UserInvitationRead:
        """Create an inactive invited user and send an activation email."""

        email = payload.email.lower()
        if self.user_repository.get_by_email(email) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un utilisateur existe deja.")

        role_ids = sorted(set(payload.role_ids))
        roles = self.role_repository.list_by_ids(role_ids)
        if len(roles) != len(role_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role introuvable.")

        token = self._generate_token()
        now = self._now()
        user = User(
            email=email,
            password_hash=hash_password(self._generate_placeholder_password()),
            is_active=False,
            is_superadmin=False,
        )
        user.roles = roles

        invitation = UserInvitation(
            user=user,
            email=email,
            token_hash=self.hash_token(token),
            expires_at=now + INVITATION_TTL,
            created_by_user_id=created_by_user_id,
        )

        db = self.user_repository.db
        db.add(user)
        db.add(invitation)
        db.flush()

        try:
            self.email_service.send_activation_email(email=email, token=token)
        except EmailDeliveryError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Email d'activation non envoye.",
            ) from exc

        db.commit()
        db.refresh(user)
        db.refresh(invitation)

        return UserInvitationRead(
            user_id=user.id,
            email=user.email,
            expires_at=invitation.expires_at,
            message="Utilisateur cree. Un email d'activation valable 24 heures a ete envoye.",
        )

    def activate_account(self, *, token: str, password: str) -> AccountActivationResponse:
        """Activate an invited user account using a one-time token."""

        invitation = self.invitation_repository.get_by_token_hash(self.hash_token(token))
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien d'activation invalide.")
        if invitation.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien d'activation deja utilise.")
        if self._is_expired(invitation.expires_at):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien d'activation expire.")

        user = self.user_repository.get(invitation.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

        user.password_hash = hash_password(password)
        user.is_active = True
        invitation.used_at = self._now()

        db = self.user_repository.db
        db.commit()
        db.refresh(user)

        return AccountActivationResponse(
            email=user.email,
            is_active=user.is_active,
            message="Compte active.",
        )

    def hash_token(self, token: str) -> str:
        """Return the persisted hash for an activation token."""

        return secret_fingerprint(token)

    def _is_expired(self, expires_at: datetime) -> bool:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at <= self._now()

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(48)

    def _generate_placeholder_password(self) -> str:
        return secrets.token_urlsafe(64)

    def _now(self) -> datetime:
        return datetime.now(UTC)
