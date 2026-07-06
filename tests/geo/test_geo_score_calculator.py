"""Tests for GEO score calculator."""

from backend.app.services.geo.provider import PROVIDER_STATUS_COMPLETED, GeoProviderResponse
from backend.app.services.geo.score_calculator import GeoScoreCalculator


def test_geo_score_calculator_scores_completed_provider_response() -> None:
    """Scores are calculated centrally from normalized provider signals."""

    response = GeoProviderResponse(
        provider_name="fake",
        model_name="fake-model",
        status=PROVIDER_STATUS_COMPLETED,
        normalized_response={
            "summary": "Page claire.",
            "geo_signals": {"clarity": 80, "citability": 60},
            "llm_signals": {"extractability": 90, "entity_coverage": 70},
            "recommendations": [
                {
                    "type": "geo",
                    "severity": "major",
                    "priority": 1,
                    "title": "Ajouter des preuves",
                    "description": "Ajouter des sources et exemples.",
                    "impact_score": 75,
                },
            ],
        },
    )

    result = GeoScoreCalculator().calculate_response(response, seo_score=50)

    assert result.geo_score == 70
    assert result.llm_score == 80
    assert result.global_score == 66.67
    assert result.recommendations[0].title == "Ajouter des preuves"


def test_geo_score_calculator_handles_not_implemented_provider() -> None:
    """Unavailable providers produce a controlled recommendation and no score."""

    response = GeoProviderResponse(
        provider_name="openai",
        model_name=None,
        status="NOT_IMPLEMENTED",
        normalized_response={"summary": "Provider not implemented."},
        error_message="Not implemented.",
    )

    result = GeoScoreCalculator().calculate_response(response)

    assert result.geo_score is None
    assert result.llm_score is None
    assert result.recommendations[0].source == "openai"


def test_geo_score_calculator_aggregates_available_scores() -> None:
    """Only available scores are used in analysis aggregates."""

    calculator = GeoScoreCalculator()
    first = calculator.calculate_response(
        GeoProviderResponse(
            provider_name="fake",
            model_name=None,
            status=PROVIDER_STATUS_COMPLETED,
            normalized_response={"geo_signals": {"a": 50}, "llm_signals": {"b": 80}},
        ),
    )
    second = calculator.calculate_response(
        GeoProviderResponse(provider_name="openai", model_name=None, status="NOT_IMPLEMENTED"),
    )

    aggregate = calculator.aggregate([first, second])

    assert aggregate.geo_score == 50
    assert aggregate.llm_score == 80
    assert aggregate.global_score == 65
