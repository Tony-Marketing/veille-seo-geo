"""URL normalization utilities for the crawler engine."""

from posixpath import normpath
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class UrlNormalizer:
    """Normalize URLs into stable values suitable for crawl comparisons."""

    allowed_schemes = {"http", "https"}

    def normalize(self, url: str, base_url: str | None = None) -> str | None:
        """Return a normalized absolute URL, or None when the URL cannot be crawled."""

        raw_url = url.strip()
        if not raw_url:
            return None
        if self._is_ignored_scheme(raw_url):
            return None

        absolute_url = self._absolute_url(raw_url, base_url)
        parts = urlsplit(absolute_url)
        scheme = parts.scheme.lower()
        if scheme not in self.allowed_schemes or not parts.netloc:
            return None

        hostname = (parts.hostname or "").lower()
        if not hostname:
            return None

        netloc = self._netloc(hostname, parts.port, scheme)
        path = self._path(parts.path)
        query = self._query(parts.query)
        return urlunsplit((scheme, netloc, path, query, ""))

    def host(self, url: str) -> str:
        """Return the normalized host for a URL."""

        parts = urlsplit(url)
        return (parts.hostname or "").lower()

    def same_host(self, first_url: str, second_url: str) -> bool:
        """Return whether two URLs belong to the same host."""

        return self.host(first_url) == self.host(second_url)

    def _absolute_url(self, url: str, base_url: str | None) -> str:
        if base_url is None:
            return url

        from urllib.parse import urljoin

        return urljoin(base_url, url)

    def _is_ignored_scheme(self, url: str) -> bool:
        lowered = url.lower()
        return lowered.startswith(("mailto:", "tel:", "javascript:", "data:"))

    def _netloc(self, hostname: str, port: int | None, scheme: str) -> str:
        if port is None or (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            return hostname
        return f"{hostname}:{port}"

    def _path(self, path: str) -> str:
        if not path:
            return "/"

        normalized = normpath(path)
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        if path.endswith("/") and not normalized.endswith("/"):
            normalized = f"{normalized}/"
        return normalized

    def _query(self, query: str) -> str:
        if not query:
            return ""
        params = parse_qsl(query, keep_blank_values=True)
        return urlencode(sorted(params))

