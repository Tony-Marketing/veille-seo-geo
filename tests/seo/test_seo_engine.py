"""Tests for the deterministic SEO analysis engine."""

from backend.app.seo import SeoAnalysisEngine
from backend.app.seo.models import SeoAnalysisContext, SeoPageInput


def _page(raw_html: str | None) -> SeoPageInput:
    return SeoPageInput(
        id=1,
        url="https://example.com/",
        normalized_url="https://example.com/",
        final_url="https://example.com/",
        final_normalized_url="https://example.com/",
        status_code=200,
        content_type="text/html",
        raw_html=raw_html,
        response_time_ms=12,
        is_redirect=False,
        redirect_url=None,
        redirect_count=0,
    )


def test_seo_engine_detects_common_page_issues() -> None:
    """The engine analyzes persisted HTML and returns deterministic issues."""

    html = """
    <html>
      <head>
        <meta name="description" content="">
        <meta name="robots" content="noindex">
        <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article"}</script>
      </head>
      <body>
        <h1>First</h1>
        <h1>Second</h1>
        <h3>Skipped</h3>
        <img src="/image.jpg">
        <a href="/missing"></a>
        <a href="http://external.example.com">Click here</a>
      </body>
    </html>
    """

    result = SeoAnalysisEngine().analyze_page(_page(html), SeoAnalysisContext())
    codes = {issue.code for issue in result.issues}

    assert result.status == "COMPLETED"
    assert "title_missing" in codes
    assert "meta_description_empty" in codes
    assert "robots_noindex" in codes
    assert "h1_multiple" in codes
    assert "heading_level_skip" in codes
    assert "image_alt_missing" in codes
    assert "anchor_empty" in codes
    assert "external_link_http" in codes


def test_seo_engine_fails_page_without_persisted_html() -> None:
    """The engine does not try to fetch HTML when persisted HTML is missing."""

    result = SeoAnalysisEngine().analyze_page(_page(None), SeoAnalysisContext())

    assert result.status == "FAILED"
    assert [issue.code for issue in result.issues] == ["html_missing"]
