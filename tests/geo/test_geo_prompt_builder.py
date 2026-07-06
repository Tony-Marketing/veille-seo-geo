"""Tests for GEO prompt builder."""

from backend.app.services.geo.prompt_builder import GeoPromptBuilder


def test_geo_prompt_builder_uses_structured_context() -> None:
    """The builder includes crawl, HTML and SEO data in a provider-independent prompt."""

    builder = GeoPromptBuilder()
    context = builder.build_context(
        page={
            "url": "https://example.com",
            "final_url": "https://example.com/",
            "status_code": 200,
            "content_type": "text/html",
        },
        raw_html="<html><body><h1>Example</h1></body></html>",
        seo_page_analysis={"status": "COMPLETED", "score": 82.0},
        seo_issues=[
            {
                "severity": "major",
                "family": "title",
                "message": "Title absent.",
            },
        ],
    )

    prompt = builder.build(context)

    assert "https://example.com" in prompt
    assert "Title absent." in prompt
    assert "<h1>Example</h1>" in prompt
    assert context.metrics["html_length"] > 0


def test_geo_prompt_builder_marks_missing_html() -> None:
    """Missing persisted HTML is explicit in the generated prompt."""

    builder = GeoPromptBuilder()
    context = builder.build_context(
        page={"url": "https://example.com"},
        raw_html=None,
        seo_page_analysis=None,
        seo_issues=[],
    )

    prompt = builder.build(context)

    assert "[HTML manquant]" in prompt
