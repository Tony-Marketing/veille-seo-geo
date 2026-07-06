"""Tests for GEO provider interface."""

from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED, GeoProvider, GeoProviderResponse
from backend.app.services.geo.providers.openai_provider import OpenAIProvider


class FakeProvider(GeoProvider):
    """Minimal provider implementation used by tests."""

    name = "fake"

    def analyze(self, prompt: str, context: object) -> GeoProviderResponse:
        return GeoProviderResponse(
            provider_name=self.name,
            model_name="fake-model",
            status=PROVIDER_STATUS_COMPLETED,
            normalized_response={"summary": "ok"},
        )


def test_geo_provider_interface_can_be_mocked() -> None:
    """Providers are replaceable through the shared interface."""

    response = FakeProvider().analyze("prompt", object())

    assert response.provider_name == "fake"
    assert response.status == PROVIDER_STATUS_COMPLETED


def test_openai_provider_returns_controlled_not_implemented_response() -> None:
    """The prepared OpenAI provider does not make network calls."""

    response = OpenAIProvider().analyze("prompt", object())

    assert response.provider_name == "openai"
    assert response.status == "NOT_IMPLEMENTED"
    assert response.error_message is not None
