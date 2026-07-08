"""Tests for Bing Webmaster Tools service."""

from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.connectors.bing_webmaster_tools import FakeBingWebmasterConnector
from backend.app.core.security import decrypt_secret
from backend.app.models import BingWebmasterCrawlStat, BingWebmasterMetric, BingWebmasterSitemap
from backend.app.repositories.bing_webmaster_tools import BingWebmasterToolsRepository
from backend.app.schemas.bing_webmaster_tools import (
    BingWebmasterConnectionCreate,
    BingWebmasterConnectionUpdate,
    BingWebmasterImportRequest,
    BingWebmasterMetricFilters,
)
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.bing_webmaster_tools import BingWebmasterToolsService


def _service(
    db_session: Session,
    *,
    connector: FakeBingWebmasterConnector | None = None,
) -> BingWebmasterToolsService:
    return BingWebmasterToolsService(
        BingWebmasterToolsRepository(db_session),
        connector=connector or FakeBingWebmasterConnector(),
    )


def test_bing_webmaster_service_creates_connections_and_encrypts_secrets(db_session: Session) -> None:
    """The service encrypts credentials and never exposes encrypted values in reads."""

    service = _service(db_session)
    created = service.create_connection(
        BingWebmasterConnectionCreate(
            auth_type="API_KEY",
            client_id="client-id",
            api_key="fake-api-key",
            scopes=["webmaster.read"],
        ),
    )
    updated = service.update_connection(created.id, BingWebmasterConnectionUpdate(access_token="fake-access-token"))
    stored = BingWebmasterToolsRepository(db_session).get_connection(created.id)

    assert created.has_api_key is True
    assert updated.has_access_token is True
    assert stored is not None
    assert stored.api_key_encrypted != "fake-api-key"
    assert stored.access_token_encrypted != "fake-access-token"
    assert decrypt_secret(stored.api_key_encrypted or "") == "fake-api-key"
    assert decrypt_secret(stored.access_token_encrypted or "") == "fake-access-token"
    assert not hasattr(created, "api_key_encrypted")


def test_bing_webmaster_service_runs_idempotent_import(db_session: Session) -> None:
    """Manual imports are journaled and upsert imported rows idempotently."""

    connector = FakeBingWebmasterConnector(duplicate_metrics=True)
    service = _service(db_session, connector=connector)
    created = service.create_connection(BingWebmasterConnectionCreate(auth_type="API_KEY", api_key="fake-api-key"))
    payload = BingWebmasterImportRequest(
        connection_id=created.id,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 7),
    )

    first_import = service.run_manual_import(payload)
    second_import = service.run_manual_import(payload)
    connection = BingWebmasterToolsRepository(db_session).get_connection(created.id)
    sites = service.list_sites(PaginationParams())

    assert first_import.status == "COMPLETED"
    assert second_import.status == "COMPLETED"
    assert first_import.items_processed == 4
    assert second_import.items_processed == 4
    assert first_import.duration_seconds is not None
    assert connection is not None
    assert connection.last_sync_at is not None
    assert connection.last_error is None
    assert sites.items[0].last_import_at is not None
    assert db_session.query(BingWebmasterMetric).count() == 1
    assert db_session.query(BingWebmasterCrawlStat).count() == 1
    assert db_session.query(BingWebmasterSitemap).count() == 1
    assert "fetch_metrics" in connector.calls


def test_bing_webmaster_service_runs_empty_import(db_session: Session) -> None:
    """An empty connector response completes the import with zero processed items."""

    service = _service(db_session, connector=FakeBingWebmasterConnector(mode="empty"))
    created = service.create_connection(BingWebmasterConnectionCreate(auth_type="API_KEY", api_key="fake-api-key"))

    import_run = service.run_manual_import(
        BingWebmasterImportRequest(connection_id=created.id, date_from=date(2026, 7, 1), date_to=date(2026, 7, 7)),
    )

    assert import_run.status == "COMPLETED"
    assert import_run.items_processed == 0
    assert db_session.query(BingWebmasterMetric).count() == 0


def test_bing_webmaster_service_handles_authentication_and_network_errors(db_session: Session) -> None:
    """Connector errors are converted to controlled import failures."""

    service = _service(db_session, connector=FakeBingWebmasterConnector(mode="auth_error"))
    created = service.create_connection(BingWebmasterConnectionCreate(auth_type="API_KEY", api_key="fake-api-key"))

    with pytest.raises(HTTPException) as exc:
        service.run_manual_import(
            BingWebmasterImportRequest(connection_id=created.id, date_from=date(2026, 7, 1), date_to=date(2026, 7, 7)),
        )

    connection = BingWebmasterToolsRepository(db_session).get_connection(created.id)
    import_runs = service.list_import_runs(PaginationParams())

    assert exc.value.status_code == 502
    assert connection is not None
    assert connection.last_error is not None
    assert import_runs.items[0].status == "FAILED"
    assert import_runs.items[0].error_message is not None


def test_bing_webmaster_service_validates_filters_dates_and_sort(db_session: Session) -> None:
    """The service validates periods and converts repository sort errors."""

    service = _service(db_session)

    with pytest.raises(HTTPException) as invalid_period:
        service.list_metrics(
            PaginationParams(),
            filters=BingWebmasterMetricFilters(date_from=date(2026, 7, 7), date_to=date(2026, 7, 1)),
        )
    with pytest.raises(HTTPException) as invalid_sort:
        service.list_metrics(PaginationParams(sort="not_allowed"))

    assert invalid_period.value.status_code == 422
    assert invalid_sort.value.status_code == 422


def test_bing_webmaster_service_rejects_inactive_connection(db_session: Session) -> None:
    """Inactive connections cannot be imported."""

    service = _service(db_session)
    created = service.create_connection(
        BingWebmasterConnectionCreate(auth_type="API_KEY", api_key="fake-api-key", is_active=False),
    )

    with pytest.raises(HTTPException) as exc:
        service.run_manual_import(
            BingWebmasterImportRequest(connection_id=created.id, date_from=date(2026, 7, 1), date_to=date(2026, 7, 7)),
        )

    assert exc.value.status_code == 409
