"""Point d'entrée du client Desktop PySide6."""

from __future__ import annotations

import traceback


def main() -> int:
    """Run the Desktop application."""

    if __package__:
        # Lancement en tant que module : python -m desktop.main
        from .app import run_desktop_app
    else:
        # Lancement en script : python desktop/main.py ou double-clic
        from app import run_desktop_app

    return run_desktop_app()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("\n=== Erreur au démarrage du Desktop ===\n")
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")