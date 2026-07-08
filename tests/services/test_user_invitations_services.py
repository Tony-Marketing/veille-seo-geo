"""Tests du service d'invitation utilisateur."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import verify_password
from backend.app.models import Role, User, UserInvitation
from backend.app.repositories.auth import RoleRepository, UserRepository
from backend.app.repositories.user_invitations import UserInvitationRepository
from backend.app.schemas.auth import UserInvitationCreate
from backend.app.services.user_invitations import INVITATION_TTL, UserInvitationService


class FakeEmailService:
    """Capture activation emails without sending real messages."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send_activation_email(self, *, email: str, token: str) -> None:
        self.sent.append((email, token))


def _service(db_session: Session, email_service: FakeEmailService) -> UserInvitationService:
    return UserInvitationService(
        UserRepository(db_session),
        RoleRepository(db_session),
        UserInvitationRepository(db_session),
        email_service,  # type: ignore[arg-type]
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def test_invite_user_creates_pending_user_and_hashed_token(db_session: Session) -> None:
    """Invitation creates an inactive user, roles and a hashed one-time token."""

    role = Role(name="Administrateur")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    email_service = FakeEmailService()
    service = _service(db_session, email_service)

    result = service.invite_user(
        UserInvitationCreate(email="Invite@example.com", role_ids=[role.id]),
        created_by_user_id=None,
    )

    user = db_session.query(User).filter(User.email == "invite@example.com").one()
    invitation = db_session.query(UserInvitation).filter(UserInvitation.user_id == user.id).one()
    sent_email, raw_token = email_service.sent[0]

    assert result.user_id == user.id
    assert sent_email == "invite@example.com"
    assert user.is_active is False
    assert user.roles[0].id == role.id
    assert invitation.token_hash != raw_token
    assert invitation.token_hash == service.hash_token(raw_token)
    assert invitation.used_at is None
    assert _as_utc(invitation.expires_at) - datetime.now(UTC) <= INVITATION_TTL


def test_invite_user_rejects_existing_email(db_session: Session) -> None:
    """An existing email cannot be invited twice."""

    db_session.add(User(email="user@example.com", password_hash="hash", is_active=True))
    db_session.commit()
    service = _service(db_session, FakeEmailService())

    try:
        service.invite_user(UserInvitationCreate(email="user@example.com"), created_by_user_id=None)
    except HTTPException as exc:
        assert exc.status_code == 409
    else:
        raise AssertionError("duplicate email should fail")


def test_activate_account_with_valid_token(db_session: Session) -> None:
    """A valid unused token activates the user and replaces the password hash."""

    email_service = FakeEmailService()
    service = _service(db_session, email_service)
    service.invite_user(UserInvitationCreate(email="user@example.com"), created_by_user_id=None)
    raw_token = email_service.sent[0][1]

    result = service.activate_account(token=raw_token, password="Password123")
    user = db_session.query(User).filter(User.email == "user@example.com").one()
    invitation = db_session.query(UserInvitation).filter(UserInvitation.user_id == user.id).one()

    assert result.is_active is True
    assert user.is_active is True
    assert verify_password("Password123", user.password_hash)
    assert invitation.used_at is not None


def test_activate_account_rejects_invalid_token(db_session: Session) -> None:
    """Unknown activation tokens are rejected."""

    service = _service(db_session, FakeEmailService())

    try:
        service.activate_account(token="invalid-token-value-with-enough-length", password="Password123")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Lien d'activation invalide."
    else:
        raise AssertionError("invalid token should fail")


def test_activate_account_rejects_expired_token(db_session: Session) -> None:
    """Expired activation tokens are rejected."""

    email_service = FakeEmailService()
    service = _service(db_session, email_service)
    service.invite_user(UserInvitationCreate(email="expired@example.com"), created_by_user_id=None)
    raw_token = email_service.sent[0][1]
    invitation = db_session.query(UserInvitation).one()
    invitation.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()

    try:
        service.activate_account(token=raw_token, password="Password123")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Lien d'activation expire."
    else:
        raise AssertionError("expired token should fail")


def test_activate_account_rejects_used_token(db_session: Session) -> None:
    """Used activation tokens are rejected."""

    email_service = FakeEmailService()
    service = _service(db_session, email_service)
    service.invite_user(UserInvitationCreate(email="used@example.com"), created_by_user_id=None)
    raw_token = email_service.sent[0][1]
    invitation = db_session.query(UserInvitation).one()
    invitation.used_at = datetime.now(UTC)
    db_session.commit()

    try:
        service.activate_account(token=raw_token, password="Password123")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Lien d'activation deja utilise."
    else:
        raise AssertionError("used token should fail")
