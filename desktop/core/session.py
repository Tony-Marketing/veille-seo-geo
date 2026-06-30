"""Session utilisateur Desktop en memoire."""

from typing import Any


class DesktopSession:
    """Store the authenticated Desktop user for the current process only."""

    def __init__(self) -> None:
        self.access_token: str | None = None
        self.user: dict[str, Any] | None = None

    @property
    def is_authenticated(self) -> bool:
        """Return whether the session currently owns an access token."""

        return bool(self.access_token)

    def set_token(self, access_token: str) -> None:
        """Store the current API access token in memory."""

        self.access_token = access_token

    def set_user(self, user: dict[str, Any]) -> None:
        """Store the current API user payload in memory."""

        self.user = user

    def clear(self) -> None:
        """Clear every in-memory authentication value."""

        self.access_token = None
        self.user = None
