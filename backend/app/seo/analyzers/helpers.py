"""Helper functions shared by SEO analyzers."""

from urllib.parse import urljoin, urlparse

from backend.app.seo.models import SeoIssue, SeoPageInput


def issue(
    family: str,
    criterion: str,
    code: str,
    message: str,
    *,
    severity: str = "major",
    details: str | None = None,
) -> SeoIssue:
    """Build a normalized SEO issue."""

    return SeoIssue(
        family=family,
        criterion=criterion,
        severity=severity,
        code=code,
        message=message,
        details=details,
    )


def absolute_url(raw_url: str, page: SeoPageInput) -> str:
    """Resolve an URL using the effective page URL."""

    return urljoin(page.effective_url, raw_url)


def same_host(url: str, page: SeoPageInput) -> bool:
    """Return whether an URL belongs to the same host as the page."""

    target = urlparse(url)
    source = urlparse(page.effective_url)
    return bool(target.netloc and source.netloc and target.netloc.lower() == source.netloc.lower())


def is_absolute_url(raw_url: str) -> bool:
    """Return whether a URL already has a scheme and host."""

    parsed = urlparse(raw_url)
    return bool(parsed.scheme and parsed.netloc)
