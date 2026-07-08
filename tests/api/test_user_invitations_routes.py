"""Tests des routes REST d'invitation utilisateur."""

from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.v1.routes import admin as admin_routes
from backend.app.models import Role, User, UserInvitation


class FakeEmailService:
    """Capture activation emails without sending real messages."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send_activation_email(self, *, email: str, token: str) -> None:
        self.sent.append((email, token))


def test_admin_can_invite_user(
    client: TestClient,
    db_session: Session,
    admin_headers: dict[str, str],
) -> None:
    """Admin invitation creates an inactive user and returns no raw token."""

    role = Role(name="Administrateur")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    email_service = FakeEmailService()
    client.app.dependency_overrides[admin_routes.get_email_service] = lambda: email_service

    response = client.post(
        "/api/v1/admin/users/invite",
        headers=admin_headers,
        json={"email": "invite@example.com", "role_ids": [role.id]},
    )

    assert response.status_code == 201
    data = response.json()
    user = db_session.query(User).filter(User.email == "invite@example.com").one()
    invitation = db_session.query(UserInvitation).filter(UserInvitation.user_id == user.id).one()
    assert data["user_id"] == user.id
    assert data["email"] == "invite@example.com"
    assert "token" not in data
    assert user.is_active is False
    assert user.roles[0].id == role.id
    assert invitation.used_at is None
    assert email_service.sent[0][0] == "invite@example.com"


def test_invite_user_requires_admin_rights(
    client: TestClient,
    auth_headers_for: Callable[..., dict[str, str]],
) -> None:
    """Non-admin users cannot invite accounts."""

    headers = auth_headers_for()
    response = client.post(
        "/api/v1/admin/users/invite",
        headers=headers,
        json={"email": "invite@example.com", "role_ids": []},
    )

    assert response.status_code == 403


def test_activate_account_route(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """The public activation endpoint activates the invited account."""

    email_service = FakeEmailService()
    client.app.dependency_overrides[admin_routes.get_email_service] = lambda: email_service
    invite_response = client.post(
        "/api/v1/admin/users/invite",
        headers=admin_headers,
        json={"email": "activation@example.com", "role_ids": []},
    )

    raw_token = email_service.sent[0][1]
    activation_response = client.post(
        "/api/v1/auth/activate",
        json={"token": raw_token, "password": "Password123"},
    )

    assert invite_response.status_code == 201
    assert activation_response.status_code == 200
    data = activation_response.json()
    assert data["email"] == "activation@example.com"
    assert data["is_active"] is True


def test_activate_account_rejects_short_password(client: TestClient) -> None:
    """Password validation remains handled by Pydantic."""

    response = client.post(
        "/api/v1/auth/activate",
        json={"token": "token-value-with-more-than-thirty-two-characters", "password": "short"},
    )

    assert response.status_code == 422
