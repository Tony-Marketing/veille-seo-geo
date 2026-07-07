"""Tests for Google Search Console connector boundary."""

from datetime import date

from backend.app.connectors.google_search_console import (
    PreparedGoogleSearchConsoleConnector,
)


def test_prepared_google_search_console_connector_does_not_call_network(monkeypatch) -> None:
    """The prepared connector returns controlled data without any Internet call."""

    def fail_network(*args, **kwargs) -> None:
        raise AssertionError("Network calls are forbidden in tests.")

    monkeypatch.setattr("socket.create_connection", fail_network)
    connector = PreparedGoogleSearchConsoleConnector()

    assert connector.list_properties() == []
    assert connector.fetch_performance("https://example.com/", start_date=date(2026, 7, 1)) == []
    assert connector.fetch_index_coverage("https://example.com/") == []
    assert connector.fetch_sitemaps("https://example.com/") == []
