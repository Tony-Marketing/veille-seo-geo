"""OpenAI GEO provider placeholder.

The Sprint 22 implementation prepares the provider boundary without making
network calls. A real OpenAI connector can replace this implementation later
without changing the GEO engine contract.
"""

from backend.app.services.geo.provider import PROVIDER_STATUS_NOT_IMPLEMENTED, GeoProvider, GeoProviderResponse


class OpenAIProvider(GeoProvider):
    """Prepared OpenAI provider returning a controlled non-network response."""

    name = "openai"

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or "not-configured"

    def analyze(self, prompt: str, context: object) -> GeoProviderResponse:
        """Return a controlled response until a real connector is configured."""

        return GeoProviderResponse(
            provider_name=self.name,
            model_name=self.model_name,
            status=PROVIDER_STATUS_NOT_IMPLEMENTED,
            raw_response=None,
            normalized_response={
                "summary": "OpenAI provider is prepared but not implemented in Sprint 22.",
                "geo_signals": {},
                "llm_signals": {},
                "recommendations": [],
                "prompt_length": len(prompt),
            },
            error_message="OpenAI provider is not implemented yet.",
            duration_ms=0,
        )
