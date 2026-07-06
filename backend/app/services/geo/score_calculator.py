"""Centralized GEO score and recommendation calculation."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED, GeoProviderResponse


@dataclass(frozen=True)
class GeoRecommendationDraft:
    """Recommendation prepared by the score calculator before persistence."""

    recommendation_type: str
    severity: str
    priority: int
    title: str
    description: str
    source: str | None
    impact_score: float | None = None


@dataclass(frozen=True)
class GeoCalculatedResult:
    """Scores and recommendations calculated from one provider response."""

    geo_score: float | None
    llm_score: float | None
    global_score: float | None
    summary: str | None
    recommendations: list[GeoRecommendationDraft]


@dataclass(frozen=True)
class GeoAggregatedScores:
    """Aggregated scores for one complete GEO analysis."""

    geo_score: float | None
    llm_score: float | None
    global_score: float | None
    summary: str | None


class GeoScoreCalculator:
    """Calculate GEO scores and recommendations outside providers."""

    def calculate_response(
        self,
        response: GeoProviderResponse,
        *,
        seo_score: float | None = None,
    ) -> GeoCalculatedResult:
        """Transform one provider response into scores and recommendations."""

        if response.status != PROVIDER_STATUS_COMPLETED:
            return GeoCalculatedResult(
                geo_score=None,
                llm_score=None,
                global_score=None,
                summary=response.normalized_response.get("summary") if response.normalized_response else None,
                recommendations=[
                    GeoRecommendationDraft(
                        recommendation_type="geo",
                        severity="medium",
                        priority=3,
                        title=f"Provider {response.provider_name} indisponible",
                        description=(
                            response.error_message or "Le provider GEO n'a pas retourne de resultat exploitable."
                        ),
                        source=response.provider_name,
                        impact_score=None,
                    ),
                ],
            )

        normalized = response.normalized_response
        geo_score = self._score_signals(normalized.get("geo_signals"))
        llm_score = self._score_signals(normalized.get("llm_signals"))
        global_score = self._global_score(geo_score, llm_score, seo_score)
        recommendations = self._recommendations(normalized.get("recommendations"), response.provider_name)
        return GeoCalculatedResult(
            geo_score=geo_score,
            llm_score=llm_score,
            global_score=global_score,
            summary=self._string_or_none(normalized.get("summary")),
            recommendations=recommendations,
        )

    def aggregate(self, calculated: list[GeoCalculatedResult]) -> GeoAggregatedScores:
        """Aggregate page/provider scores into one analysis score set."""

        geo_score = self._average([item.geo_score for item in calculated])
        llm_score = self._average([item.llm_score for item in calculated])
        global_score = self._average([item.global_score for item in calculated])
        summaries = [item.summary for item in calculated if item.summary]
        return GeoAggregatedScores(
            geo_score=geo_score,
            llm_score=llm_score,
            global_score=global_score,
            summary=summaries[0] if summaries else None,
        )

    def _score_signals(self, signals: Any) -> float | None:
        if not isinstance(signals, dict):
            return None
        values = [float(value) for value in signals.values() if isinstance(value, int | float)]
        if not values:
            return None
        return round(max(0.0, min(100.0, mean(values))), 2)

    def _global_score(self, geo_score: float | None, llm_score: float | None, seo_score: float | None) -> float | None:
        values = [value for value in (geo_score, llm_score, seo_score) if value is not None]
        if not values:
            return None
        return round(mean(values), 2)

    def _average(self, values: list[float | None]) -> float | None:
        numeric_values = [value for value in values if value is not None]
        if not numeric_values:
            return None
        return round(mean(numeric_values), 2)

    def _recommendations(self, payload: Any, source: str) -> list[GeoRecommendationDraft]:
        if not isinstance(payload, list):
            return []
        recommendations: list[GeoRecommendationDraft] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            title = self._string_or_none(item.get("title"))
            description = self._string_or_none(item.get("description"))
            if not title or not description:
                continue
            recommendations.append(
                GeoRecommendationDraft(
                    recommendation_type=self._string_or_none(item.get("type")) or "geo",
                    severity=self._string_or_none(item.get("severity")) or "medium",
                    priority=self._priority(item.get("priority")),
                    title=title,
                    description=description,
                    source=source,
                    impact_score=self._float_or_none(item.get("impact_score")),
                ),
            )
        return recommendations

    def _priority(self, value: Any) -> int:
        if isinstance(value, int):
            return max(1, min(5, value))
        return 3

    def _float_or_none(self, value: Any) -> float | None:
        if isinstance(value, int | float):
            return float(value)
        return None

    def _string_or_none(self, value: Any) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None
