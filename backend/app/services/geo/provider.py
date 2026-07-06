"""Provider interface for GEO analysis."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

PROVIDER_STATUS_COMPLETED = "COMPLETED"
PROVIDER_STATUS_FAILED = "FAILED"
PROVIDER_STATUS_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass(frozen=True)
class GeoProviderResponse:
    """Structured response returned by a GEO provider."""

    provider_name: str
    model_name: str | None
    status: str
    raw_response: str | None = None
    normalized_response: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    duration_ms: int | None = None


class GeoProvider(ABC):
    """Common interface implemented by GEO providers."""

    name: str

    @abstractmethod
    def analyze(self, prompt: str, context: object) -> GeoProviderResponse:
        """Analyze a prepared GEO prompt and return a structured response."""
