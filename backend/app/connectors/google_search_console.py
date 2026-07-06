"""Mockable Google Search Console connector boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class GscTokenPayload:
    """OAuth token payload returned by a connector."""

    access_token: str
    refresh_token: str | None
    expires_at: datetime
    scopes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GscPropertyPayload:
    """GSC property payload returned by a connector."""

    site_url: str
    property_type: str = "url_prefix"
    permission_level: str | None = "siteOwner"
    is_verified: bool = True


class GoogleSearchConsoleClient:
    """Preparatory GSC connector with no real network calls.

    The real Google implementation can later replace this class while keeping
    the service and tests on the same interface.
    """

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        scopes: list[str] | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or []

    def authorization_url(self) -> str:
        """Return a deterministic preparatory OAuth URL."""

        scope = "%20".join(self.scopes)
        client_id = self.client_id or "not-configured"
        redirect_uri = self.redirect_uri or ""
        return (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        )

    def exchange_authorization_code(self, code: str) -> GscTokenPayload:
        """Return mock tokens for a testable preparatory OAuth callback."""

        now = datetime.now(UTC)
        return GscTokenPayload(
            access_token=f"mock-access-token-{code}",
            refresh_token=f"mock-refresh-token-{code}",
            expires_at=now + timedelta(hours=1),
            scopes=self.scopes,
        )

    def list_properties(self) -> list[GscPropertyPayload]:
        """Return no properties by default until a real or test connector is injected."""

        return []

    def fetch_performance(self, site_url: str, date_start: date | None, date_end: date | None) -> list[dict[str, Any]]:
        """Return no performance rows by default."""

        return []

    def fetch_coverage(self, site_url: str) -> list[dict[str, Any]]:
        """Return no coverage rows by default."""

        return []

    def inspect_urls(self, site_url: str) -> list[dict[str, Any]]:
        """Return no indexing rows by default."""

        return []

    def list_sitemaps(self, site_url: str) -> list[dict[str, Any]]:
        """Return no sitemaps by default."""

        return []
