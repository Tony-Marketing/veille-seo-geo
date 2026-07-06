"""GEO analysis orchestration engine."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.services.geo.prompt_builder import GeoPromptBuilder
from backend.app.services.geo.provider import PROVIDER_STATUS_FAILED, GeoProvider, GeoProviderResponse
from backend.app.services.geo.providers import OpenAIProvider
from backend.app.services.geo.score_calculator import GeoCalculatedResult, GeoScoreCalculator


@dataclass(frozen=True)
class GeoPageWorkItem:
    """One crawled page enriched with SEO data for GEO analysis."""

    crawl_page_id: int
    page: dict[str, object]
    raw_html: str | None
    seo_page_analysis: dict[str, object] | None
    seo_issues: list[dict[str, object]]
    seo_score: float | None = None


@dataclass(frozen=True)
class GeoProviderExecution:
    """One provider execution result prepared by the GEO engine."""

    crawl_page_id: int
    provider_name: str
    prompt: str
    response: GeoProviderResponse
    calculated: GeoCalculatedResult


@dataclass(frozen=True)
class GeoEngineResult:
    """Complete engine output before persistence."""

    executions: list[GeoProviderExecution]


class GeoAnalysisEngine:
    """Run GEO providers on persisted crawl and SEO data."""

    def __init__(
        self,
        *,
        providers: dict[str, GeoProvider] | None = None,
        prompt_builder: GeoPromptBuilder | None = None,
        score_calculator: GeoScoreCalculator | None = None,
    ) -> None:
        self.providers = providers if providers is not None else {"openai": OpenAIProvider()}
        self.prompt_builder = prompt_builder or GeoPromptBuilder()
        self.score_calculator = score_calculator or GeoScoreCalculator()

    def run(self, pages: list[GeoPageWorkItem], provider_names: list[str]) -> GeoEngineResult:
        """Run requested providers for every page without network fallback logic."""

        executions: list[GeoProviderExecution] = []
        for page in pages:
            context = self.prompt_builder.build_context(
                page=page.page,
                raw_html=page.raw_html,
                seo_page_analysis=page.seo_page_analysis,
                seo_issues=page.seo_issues,
            )
            prompt = self.prompt_builder.build(context)
            for provider_name in provider_names:
                provider_key = provider_name.lower().strip()
                provider = self.providers.get(provider_key)
                if provider is None:
                    response = GeoProviderResponse(
                        provider_name=provider_key or provider_name,
                        model_name=None,
                        status=PROVIDER_STATUS_FAILED,
                        normalized_response={},
                        error_message=f"Provider GEO inconnu: {provider_name}.",
                    )
                else:
                    response = provider.analyze(prompt, context)
                calculated = self.score_calculator.calculate_response(response, seo_score=page.seo_score)
                executions.append(
                    GeoProviderExecution(
                        crawl_page_id=page.crawl_page_id,
                        provider_name=response.provider_name,
                        prompt=prompt,
                        response=response,
                        calculated=calculated,
                    ),
                )
        return GeoEngineResult(executions=executions)
