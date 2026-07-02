"""Tests for crawler duplicate detection."""

from backend.app.crawler.duplicate_detector import DuplicateDetector


def test_duplicate_detector_tracks_seen_urls() -> None:
    """The first registration wins and later duplicates are rejected."""

    detector = DuplicateDetector()

    assert detector.add("https://example.com/") is True
    assert detector.add("https://example.com/") is False
    assert detector.seen("https://example.com/") is True
    assert detector.count() == 1

