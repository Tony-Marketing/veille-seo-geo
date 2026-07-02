"""Tests for crawler policies."""

import pytest

from backend.app.crawler.policies import CrawlPolicies


def test_policies_limit_depth_pages_and_host() -> None:
    """Policies enforce depth, max pages and host boundaries."""

    policies = CrawlPolicies.from_start_url("https://example.com", max_depth=1, max_pages=2)

    assert policies.allows("https://example.com/a", depth=1, discovered_count=1) is True
    assert policies.allows("https://example.com/b", depth=2, discovered_count=1) is False
    assert policies.allows("https://example.com/c", depth=1, discovered_count=2) is False
    assert policies.allows("https://other.example.com/a", depth=1, discovered_count=1) is False


def test_policies_reject_invalid_limits() -> None:
    """Invalid policy limits are rejected early."""

    with pytest.raises(ValueError):
        CrawlPolicies(start_url="https://example.com", max_depth=-1)
    with pytest.raises(ValueError):
        CrawlPolicies(start_url="https://example.com", max_pages=0)

