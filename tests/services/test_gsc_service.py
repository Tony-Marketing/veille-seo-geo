"""Tests for Google Search Console service."""

from datetime import UTC, datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.connectors.google_search_console import (
    GoogleSearchConsoleClient,
    GscPropertyPayload,
    GscTokenPayload,
)
from backend.app.repositories.gsc import (
    GscDataRepository,
    GscImportRunRepository,
    GscOAuthCredentialRepository,
    GscPropertyRepository,
)
from backend.app.schemas.gsc import GscOAuthCallback
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.gsc import GoogleSearchConsoleService


class FakeGscClient(GoogleSearchConsoleClient):
    """Deterministic fake GSC client."""

    def exchange_authorization_code(self, code: str) -> GscTokenPayload:
        return GscTokenPayload(
            access_token=f"access-{code}",
            refresh_token=f"refresh-{code}",
            expires_at=datetime.now(UTC),
            scopes=["scope-a"],
        )

    def list_properties(self) -> list[GscPropertyPayload]:
        return [
            GscPropertyPayload(
                site_url="https://example.com/",
                property_type="url_prefix",
                permission_level="siteOwner",
                is_verified=True,
            ),
        ]


def _service(db_session: Session) -> GoogleSearchConsoleService:
    return GoogleSearchConsoleService(
        GscOAuthCredentialRepository(db_session),
        GscPropertyRepository(db_session),
        GscImportRunRepository(db_session),
        GscDataRepository(db_session),
        client=FakeGscClient(scopes=["scope-a"]),
    )


def test_gsc_service_prepares_oauth_and_stores_callback(db_session: Session) -> None:
    """OAuth preparatory endpoints return stable data and store encrypted tokens."""

    service = _service(db_session)

    auth_url = service.authorization_url()
    credential = service.oauth_callback(GscOAuthCallback(code="abc"), user_id=1)
    status = service.oauth_status()

    assert "accounts.google.com" in auth_url.authorization_url
    assert credential.status == "ACTIVE"
    assert credential.created_by_id == 1
    assert status.active_credentials_count == 1
    assert status.latest_credential is not None


def test_gsc_service_syncs_properties_idempotently(db_session: Session) -> None:
    """Property synchronization upserts connector properties."""

    service = _service(db_session)

    first = service.sync_properties()
    second = service.sync_properties()
    listed = service.list_properties(PaginationParams())

    assert first.total == 1
    assert second.total == 1
    assert listed.total == 1
    assert listed.items[0].site_url == "https://example.com/"


def test_gsc_service_reads_property_and_rejects_missing_property(db_session: Session) -> None:
    """Property reads validate missing identifiers."""

    service = _service(db_session)
    created = service.sync_properties().items[0]

    fetched = service.get_property(created.id)

    assert fetched.id == created.id
    with pytest.raises(HTTPException) as exc_info:
        service.get_property(999)
    assert exc_info.value.status_code == 404


def test_gsc_service_deletes_oauth_credential(db_session: Session) -> None:
    """OAuth credentials can be deleted."""

    service = _service(db_session)
    credential = service.oauth_callback(GscOAuthCallback(code="abc"), user_id=1)

    service.delete_credential(credential.id)

    assert service.oauth_status().active_credentials_count == 0
