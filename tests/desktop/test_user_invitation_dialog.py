"""Tests du dialogue Desktop d'invitation utilisateur."""

import pytest
from PySide6.QtWidgets import QApplication
from ui.dialogs.user_invitation_dialog import UserInvitationDialog


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    """Return a QApplication for widget tests."""

    return QApplication.instance() or QApplication([])


def test_user_invitation_dialog_has_no_password_field(qt_app: QApplication) -> None:
    """The invitation flow does not ask the administrator for a password."""

    assert qt_app is not None
    dialog = UserInvitationDialog(roles=[{"id": 1, "name": "Administrateur"}])
    try:
        assert not hasattr(dialog, "password_input")
        assert not hasattr(dialog, "confirm_password_input")
    finally:
        dialog.close()


def test_user_invitation_dialog_payload_contains_email_and_roles(qt_app: QApplication) -> None:
    """The invitation payload only contains email and selected roles."""

    assert qt_app is not None
    dialog = UserInvitationDialog(roles=[{"id": 1, "name": "Administrateur"}])
    try:
        dialog.email_input.setText("invite@example.com")
        dialog.roles_list.item(0).setSelected(True)

        assert dialog.payload() == {"email": "invite@example.com", "role_ids": [1]}
    finally:
        dialog.close()
