"""Desktop application package.

The Desktop codebase historically uses top-level imports such as ``core`` and
``ui`` so that ``desktop/main.py`` can be launched directly. These aliases keep
that convention available when the app is launched as ``python -m desktop.main``.
"""

import sys
from importlib import import_module

for package_name in ("core", "services", "ui", "widgets"):
    sys.modules.setdefault(package_name, import_module(f"{__name__}.{package_name}"))
