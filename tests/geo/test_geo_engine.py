"""Tests for GEO analysis engine."""

from backend.app.services.geo.engine import GeoAnalysisEngine, GeoPageWorkItem
from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED, GeoProvider, GeoProviderResponse


class FakeProvider(GeoProvider):
    """Provider returning deterministic normalized data."""

    name = "fake"

    def analyze(self, prompt: str, context: object) -> GeoProviderResponse:
        return GeoProviderResponse(
            provider_name=self.name,
            model_name="fake-model",
            status=PROVIDER_STATUS_COMPLETED,
            normalized_response={
                "summary": "Readable page.",
                "geo_signals": {"clarity": 90},
                "llm_signals": {"extractability": 80},
                "recommendations": [],
            },
        )


def test_geo_engine_runs_mock_provider_without_network() -> None:
    """The engine executes injected providers and calculates scores."""

    engine = GeoAnalysisEngine(providers={"fake": FakeProvider()})
    result = engine.run(
        [
            GeoPageWorkItem(
                crawl_page_id=1,
                page={"url": "https://example.com", "status_code": 200},
                raw_html="<html><body>Example</body></html>",
                seo_page_analysis={"status": "COMPLETED", "score": 70.0},
                seo_issues=[],
                seo_score=70.0,
            ),
        ],
        ["fake"],
    )

    assert len(result.executions) == 1
    assert result.executions[0].response.status == PROVIDER_STATUS_COMPLETED
    assert result.executions[0].calculated.geo_score == 90
    assert result.executions[0].calculated.global_score == 80


def test_geo_engine_returns_failed_response_for_unknown_provider() -> None:
    """Unknown providers are reported without crashing the engine."""

    engine = GeoAnalysisEngine(providers={})
    result = engine.run(
        [
            GeoPageWorkItem(
                crawl_page_id=1,
                page={"url": "https://example.com"},
                raw_html="<html></html>",
                seo_page_analysis=None,
                seo_issues=[],
            ),
        ],
        ["unknown"],
    )

    assert result.executions[0].response.status == "FAILED"
    assert result.executions[0].calculated.recommendations[0].source == "unknown"
