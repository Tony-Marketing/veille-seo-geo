"""Tests for processing handlers."""

from backend.app.orchestration.base import HandlerResult
from backend.app.orchestration.registry import ProcessingHandlerRegistry


def test_processing_registry_returns_supported_and_unsupported_handlers() -> None:
    """The registry exposes supported handlers and controlled unsupported handlers."""

    registry = ProcessingHandlerRegistry()

    assert registry.get("gsc").__class__.__name__ == "GoogleSearchConsoleProcessingHandler"
    assert registry.get("unknown").run({}, None).success is False  # type: ignore[arg-type]


def test_handler_result_carries_retry_information() -> None:
    """Handler results expose the worker contract."""

    result = HandlerResult(success=False, message="Erreur temporaire.", retryable=True)

    assert result.success is False
    assert result.retryable is True
    assert result.details == {}

