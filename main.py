"""
main.py - Punto de entrada principal de la aplicación.

Añade src/ al path (para ejecutar sin instalación) y delega
en osint.app.main(). Alternativa: `pip install -e .` + `python -m osint`.
"""

import sys
from pathlib import Path

# Permitir importar el paquete osint sin instalarlo
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from osint.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
