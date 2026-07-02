"""Duplicate detection for normalized crawl URLs."""


class DuplicateDetector:
    """Track normalized URLs already discovered by a crawl."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def seen(self, normalized_url: str) -> bool:
        """Return whether an URL has already been discovered."""

        return normalized_url in self._seen

    def add(self, normalized_url: str) -> bool:
        """Register an URL and return True when it was new."""

        if normalized_url in self._seen:
            return False
        self._seen.add(normalized_url)
        return True

    def count(self) -> int:
        """Return the number of discovered unique URLs."""

        return len(self._seen)

