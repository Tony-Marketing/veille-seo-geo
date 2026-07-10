"""Base contracts for processing handlers."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class HandlerResult:
    """Normalized result returned to the worker."""

    success: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False


class ProcessingHandler(Protocol):
    """Protocol implemented by all processing handlers."""

    def run(self, payload: dict[str, Any], db: Session) -> HandlerResult:
        """Execute a processing payload through existing business services."""


class UnsupportedProcessingHandler:
    """Handler used when a processing type is not implemented yet."""

    def __init__(self, job_type: str) -> None:
        self.job_type = job_type

    def run(self, payload: dict[str, Any], db: Session) -> HandlerResult:
        """Return a controlled non-retryable failure."""

        return HandlerResult(
            success=False,
            message=f"Traitement non supporte : {self.job_type}.",
            details={"job_type": self.job_type},
            retryable=False,
        )


def int_payload(payload: dict[str, Any], key: str) -> int:
    """Return a positive integer from a handler payload."""

    value = payload.get(key)
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Champ payload invalide ou manquant : {key}.") from exc
    if parsed <= 0:
        raise ValueError(f"Champ payload invalide ou manquant : {key}.")
    return parsed

