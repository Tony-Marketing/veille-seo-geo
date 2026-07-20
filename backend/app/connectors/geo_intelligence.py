"""Injectable connector contract for GEO Intelligence providers."""

from typing import Protocol

from backend.app.schemas.geo_intelligence import GeoVisibilityImportItem


class GeoIntelligenceConnector(Protocol):
    """Contract implemented by controlled GEO Intelligence data collectors."""

    provider: str
    configured: bool

    def collect(self) -> list[GeoVisibilityImportItem]:
        """Return normalized observations without persisting them."""


class NotConfiguredGeoIntelligenceConnector:
    """Safe default connector that never performs an implicit network call."""

    configured = False

    def __init__(self, provider: str) -> None:
        self.provider = provider

    def collect(self) -> list[GeoVisibilityImportItem]:
        """Reject collection until an explicit connector is injected."""

        raise RuntimeError(f"Le connecteur GEO Intelligence '{self.provider}' n'est pas configure.")
