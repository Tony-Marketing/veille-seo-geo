"""Desktop tests package."""

import sys
from pathlib import Path

DESKTOP_PATH = Path(__file__).resolve().parents[2] / "desktop"
if str(DESKTOP_PATH) not in sys.path:
    sys.path.insert(0, str(DESKTOP_PATH))
