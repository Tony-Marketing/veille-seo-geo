"""Tests for Google Analytics connector contracts."""

from datetime import date

import pytest

from backend.app.connectors.google_analytics import (
    GoogleAnalyticsMetricRow,
    GoogleAnalyticsPropertyData,
    NotConfiguredGoogleAnalyticsConnector,
)


def test_not_configured_google_analytics_connector_never_calls_network() -> None:
    """The default connector is inert and raises before any external access."""

    connector = NotConfiguredGoogleAnalyticsConnector()

    assert connector.list_properties() == []
    with pytest.raises(RuntimeError):
        connector.fetch_metrics(
            property_id="properties/123",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 7),
            metrics=["users"],
            dimensions=["date"],
        )


def test_google_analytics_connector_data_objects_are_local() -> None:
    """Connector rows are simple local data objects that are easy to mock."""

    property_data = GoogleAnalyticsPropertyData(
        property_id="properties/123",
        property_name="Example GA4",
        measurement_id="G-TEST123",
    )
    metric = GoogleAnalyticsMetricRow(
        date=date(2026, 7, 1),
        source="google",
        medium="organic",
        users=10,
        sessions=12,
    )

    assert property_data.property_id == "properties/123"
    assert metric.source == "google"
    assert metric.new_users == 0
    assert metric.total_revenue == 0.0
