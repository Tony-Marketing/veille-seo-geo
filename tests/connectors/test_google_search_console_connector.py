"""Tests for Google Search Console connector contracts."""

from datetime import date

import pytest

from backend.app.connectors.google_search_console import (
    GoogleSearchConsolePerformanceRow,
    GoogleSearchConsolePropertyData,
    NotConfiguredGoogleSearchConsoleConnector,
)


def test_not_configured_google_search_console_connector_never_calls_network() -> None:
    """The default connector is inert and raises before any external access."""

    connector = NotConfiguredGoogleSearchConsoleConnector()

    assert connector.list_properties() == []
    with pytest.raises(RuntimeError):
        connector.fetch_performance(
            property_url="sc-domain:example.com",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
            dimensions=["query"],
        )


def test_google_search_console_connector_data_objects_are_local() -> None:
    """Connector rows are simple local data objects that are easy to mock."""

    property_data = GoogleSearchConsolePropertyData(
        google_property_id="sc-domain:example.com",
        property_url="sc-domain:example.com",
        property_type="DOMAIN",
    )
    performance = GoogleSearchConsolePerformanceRow(
        date=date(2026, 7, 1),
        query="audit seo",
        clicks=10,
        impressions=100,
    )

    assert property_data.google_property_id == "sc-domain:example.com"
    assert performance.ctr == 0.0
    assert performance.search_type == "web"
