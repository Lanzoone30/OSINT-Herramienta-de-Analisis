"""
app.py - Entry point de la aplicación.

Bootstrap de la aplicación Qt: crea QApplication, configura el icono
y muestra la ventana principal.

Why this design: Separa el arranque (app) de la ventana (ui.main_window)
para permitir ejecutar la app con `python -m osint` o desde main.py.
"""

import sys

from PyQt6.QtWidgets import QApplication

from osint.config import IconManager
from osint.ui.main_window import AppOSINT


def main() -> int:
    """Crear la aplicación Qt y mostrar la ventana principal."""
    # Identidad para QSettings (persistir tema/idioma en todas las plataformas)
    QApplication.setOrganizationName("OSINT")
    QApplication.setApplicationName("OSINT-Analysis")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo moderno

    # Intenta cargar icono de aplicación desde assets/
    app_icon = IconManager.get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = AppOSINT()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
