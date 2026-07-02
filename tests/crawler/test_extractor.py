"""Tests for HTML link extraction."""

from backend.app.crawler.extractor import LinkExtractor


def test_extractor_returns_anchor_hrefs() -> None:
    """Only anchor href values are extracted."""

    html = """
    <html>
        <a href="/a">A</a>
        <a HREF="https://example.com/b">B</a>
        <link href="/ignored.css">
        <a>No href</a>
    </html>
    """

    assert LinkExtractor().extract(html) == ["/a", "https://example.com/b"]

