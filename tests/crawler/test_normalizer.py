"""Tests for crawler URL normalization."""

from backend.app.crawler.normalizer import UrlNormalizer


def test_normalizer_normalizes_http_url() -> None:
    """URLs are lowercased, cleaned and stripped from fragments."""

    normalizer = UrlNormalizer()

    result = normalizer.normalize("HTTPS://Example.COM:443/a/../b/?z=2&a=1#section")

    assert result == "https://example.com/b/?a=1&z=2"


def test_normalizer_resolves_relative_url() -> None:
    """Relative URLs are resolved against the current page."""

    normalizer = UrlNormalizer()

    result = normalizer.normalize("../contact", base_url="https://example.com/blog/page")

    assert result == "https://example.com/contact"


def test_normalizer_ignores_uncrawlable_schemes() -> None:
    """mailto, tel and javascript URLs are not crawl candidates."""

    normalizer = UrlNormalizer()

    assert normalizer.normalize("mailto:contact@example.com") is None
    assert normalizer.normalize("javascript:void(0)") is None
    assert normalizer.normalize("ftp://example.com/file") is None

