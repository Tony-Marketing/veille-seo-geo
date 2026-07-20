"""Session utilisateur Desktop en memoire."""

from typing import Any


class DesktopSession:
    """Store the authenticated Desktop user for the current process only."""

    def __init__(self) -> None:
        self.access_token: str | None = None
        self.user: dict[str, Any] | None = None
        self.current_website: dict[str, Any] | None = None
        self.current_entity: dict[str, Any] | None = None

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

    def set_current_website(self, website: dict[str, Any] | None) -> None:
        """Store the current Website and its optional Entity context."""

        self.current_website = dict(website) if website is not None else None
        entity_id = website.get("entity_id") if website is not None else None
        self.current_entity = {"id": entity_id} if isinstance(entity_id, int) else None

    @property
    def current_website_id(self) -> int | None:
        """Return the current Website identifier when available."""

        website_id = self.current_website.get("id") if self.current_website is not None else None
        return website_id if isinstance(website_id, int) else None

    @property
    def current_entity_id(self) -> int | None:
        """Return the Entity associated with the current Website when available."""

        entity_id = self.current_entity.get("id") if self.current_entity is not None else None
        return entity_id if isinstance(entity_id, int) else None

    def clear(self) -> None:
        """Clear every in-memory authentication value."""

        self.access_token = None
        self.user = None
        self.current_website = None
        self.current_entity = None
