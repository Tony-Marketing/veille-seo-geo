"""Tests for Bing Webmaster Tools connector contracts."""

from datetime import date

import pytest

from backend.app.connectors.bing_webmaster_tools import (
    BingWebmasterAuthenticationError,
    BingWebmasterCredentials,
    BingWebmasterMetricRow,
    BingWebmasterSiteData,
    FakeBingWebmasterConnector,
    NotConfiguredBingWebmasterConnector,
)


def test_not_configured_bing_webmaster_connector_never_calls_network() -> None:
    """The default connector is inert and raises before any external access."""

    connector = NotConfiguredBingWebmasterConnector()
    credentials = BingWebmasterCredentials(auth_type="API_KEY", api_key="fake-api-key")

    assert connector.list_sites(credentials) == []
    with pytest.raises(RuntimeError):
        connector.fetch_metrics(credentials, "https://example.com/", date(2026, 7, 1), date(2026, 7, 7))
    with pytest.raises(RuntimeError):
        connector.fetch_crawl_stats(credentials, "https://example.com/", date(2026, 7, 1), date(2026, 7, 7))
    with pytest.raises(RuntimeError):
        connector.fetch_sitemaps(credentials, "https://example.com/")


def test_bing_webmaster_connector_data_objects_are_local() -> None:
    """Connector rows are simple local data objects that are easy to mock."""

    site = BingWebmasterSiteData(site_url="https://example.com/")
    metric = BingWebmasterMetricRow(date=date(2026, 7, 1), query="audit seo", clicks=10)

    assert site.site_url == "https://example.com/"
    assert site.is_verified is True
    assert metric.query == "audit seo"
    assert metric.impressions == 0


def test_fake_bing_webmaster_connector_is_deterministic() -> None:
    """The fake connector returns deterministic local data and duplicate rows when requested."""

    connector = FakeBingWebmasterConnector(duplicate_metrics=True)
    credentials = BingWebmasterCredentials(auth_type="API_KEY", api_key="fake-api-key")

    sites = connector.list_sites(credentials)
    metrics = connector.fetch_metrics(credentials, sites[0].site_url, date(2026, 7, 1), date(2026, 7, 7))
    crawl_stats = connector.fetch_crawl_stats(credentials, sites[0].site_url, date(2026, 7, 1), date(2026, 7, 7))
    sitemaps = connector.fetch_sitemaps(credentials, sites[0].site_url)

    assert len(sites) == 1
    assert len(metrics) == 2
    assert metrics[0] == metrics[1]
    assert crawl_stats[0].http_status == 404
    assert sitemaps[0].url_count == 42
    assert connector.calls == ["list_sites", "fetch_metrics", "fetch_crawl_stats", "fetch_sitemaps"]


def test_fake_bing_webmaster_connector_can_simulate_empty_and_auth_errors() -> None:
    """The fake connector covers empty imports and controlled authentication errors."""

    credentials = BingWebmasterCredentials(auth_type="API_KEY", api_key="fake-api-key")
    empty_connector = FakeBingWebmasterConnector(mode="empty")
    error_connector = FakeBingWebmasterConnector(mode="auth_error")

    assert empty_connector.fetch_metrics(credentials, "https://example.com/", date(2026, 7, 1), date(2026, 7, 7)) == []
    with pytest.raises(BingWebmasterAuthenticationError):
        error_connector.list_sites(credentials)
