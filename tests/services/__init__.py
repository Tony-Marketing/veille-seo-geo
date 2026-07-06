"""Service tests package.

Pytest can import this directory as a top-level ``services`` package. Extend
that package path to keep existing Desktop imports such as ``services.auth_service`` working.
"""

from pathlib import Path

DESKTOP_SERVICES_PATH = Path(__file__).resolve().parents[2] / "desktop" / "services"
__path__.append(str(DESKTOP_SERVICES_PATH))  # type: ignore[name-defined]
