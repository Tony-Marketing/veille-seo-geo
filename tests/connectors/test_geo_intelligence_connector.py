"""Tests for injectable GEO Intelligence connectors."""

import pytest

from backend.app.connectors.geo_intelligence import NotConfiguredGeoIntelligenceConnector


def test_default_geo_intelligence_connector_is_inactive_and_never_calls_network() -> None:
    connector = NotConfiguredGeoIntelligenceConnector("chatgpt")

    assert connector.configured is False
    with pytest.raises(RuntimeError, match="n'est pas configure"):
        connector.collect()
