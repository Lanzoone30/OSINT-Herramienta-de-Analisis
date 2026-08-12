"""
themes.py - Tema oscuro fijo de la interfaz.

Define la paleta de colores y genera el QSS completo que se aplica a
toda la aplicacion. Aplica tambien un QPalette para que los dialogos
nativos (QFileDialog, QMessageBox) respeten el tema.

Why this design: Centraliza los colores en un solo lugar para que el
estilo de la app sea un dict + regeneracion de QSS + QPalette, sin
tocar el codigo de la ventana.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

__all__ = ["apply_theme", "STATUS_COLORS"]

# Colores del indicador de estado por pestana (mismo orden que tabWidget)
STATUS_COLORS = [
    "#4CAF50",  # Geoloc.
    "#2196F3",  # WHOIS
    "#FF9800",  # Ping
    "#9C27B0",  # DNS
    "#3F51B5",  # SSL/TLS
    "#00BCD4",  # Headers
    "#FF5722",  # Port Scan
    "#795548",  # Reverse IP
    "#607D8B",  # Summary
]

# Colores para mensajes de feedback (info / error / success / warning / danger).
STATUS_STATE_COLORS = {
    "info": "#4a90e2",
    "error": "#f44336",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#FF5722",
}

_THEMES = {
    "dark": {
        "bg_primary": "#0d0d0d",
        "bg_secondary": "#1a1a1a",
        "bg_tertiary": "#2a2a2a",
        "bg_hover": "#2a2a2a",
        "bg_input": "#1a1a1a",
        "text_primary": "#e8e8e8",
        "text_secondary": "#ffffff",
        "text_muted": "#888888",
        "text_placeholder": "#888888",
        "text_warning": "#ff6b6b",
        "border": "#2a2a2a",
        "border_hover": "#3a3a3a",
        "tab_bg": "#141414",
        "tab_active": "#2a2a2a",
        "tab_text": "#999999",
        "tab_text_active": "#ffffff",
        "qtext_bg": "#0d0d0d",
        "qtext_text": "#e0e0e0",
        "selection_bg": "#3a3a3a",
        "selection_text": "#ffffff",
    },
}


def _build_palette(theme: dict) -> QPalette:
    """Crear un QPalette a partir del tema resuelto.

    Args:
        theme: Dict con los colores del tema.

    Returns:
        QPalette listo para aplicar con QApplication.setPalette().
    """
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(theme["bg_primary"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text_primary"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme["bg_input"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme["text_primary"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme["text_primary"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["text_primary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["selection_bg"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["selection_text"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(theme["text_placeholder"]))
    return palette


def build_qss(theme: dict) -> str:
    """Generar el QSS completo de la aplicacion a partir de una paleta.

    Args:
        theme: Dict de colores del tema oscuro fijo.

    Returns:
        String QSS listo para aplicar con app.setStyleSheet().
    """
    return f"""
QMainWindow, QWidget {{
    background-color: {theme["bg_primary"]};
    color: {theme["text_primary"]};
    font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', 'Helvetica Neue', sans-serif;
    outline: none;
}}

QLabel {{
    color: {theme["text_primary"]};
}}

QLabel[labelClass="title"] {{
    font-size: 20pt;
    font-weight: 600;
    color: {theme["text_secondary"]};
    letter-spacing: 0.8px;
}}

QLabel[labelClass="subtitle"] {{
    font-size: 11px;
    font-weight: 800;
    color: {theme["text_muted"]};
    letter-spacing: 1.5px;
}}

QLabel[labelClass="legal"] {{
    font-size: 8pt;
    font-style: italic;
    color: {theme["text_warning"]};
}}

QLabel[labelClass="results"] {{
    font-size: 12pt;
    font-weight: 600;
    color: {theme["text_secondary"]};
}}

QLabel[labelClass="credits"] {{
    font-size: 8pt;
    color: {theme["text_muted"]};
}}

QLabel[labelClass="status"] {{
    font-size: 11pt;
    font-weight: 600;
}}

QLineEdit {{
    background-color: {theme["bg_input"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    border-radius: 8px;
    padding: 12px;
    font-size: 11pt;
    min-height: 22px;
    selection-background-color: {theme["selection_bg"]};
    selection-color: {theme["selection_text"]};
}}

QLineEdit:focus {{
    border-color: {theme["border_hover"]};
}}

QPushButton {{
    background-color: {theme["bg_secondary"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    border-radius: 8px;
    padding: 12px 18px;
    font-size: 11pt;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {theme["bg_hover"]};
    border-color: {theme["border_hover"]};
}}

QPushButton:pressed {{
    background-color: {theme["bg_tertiary"]};
}}

QPushButton:focus {{
    border-color: {theme["border_hover"]};
}}

QPushButton[toolButton="true"] {{
    text-align: left;
    padding-left: 16px;
}}

QPushButton[quickButton="true"] {{
    min-height: 22px;
}}

QPushButton[actionButton="true"] {{
    min-height: 12px;
    padding: 8px 14px;
}}

QComboBox {{
    background-color: {theme["bg_input"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 11pt;
    font-weight: 500;
    min-width: 120px;
}}

QComboBox:focus {{
    border-color: {theme["border_hover"]};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {theme["bg_input"]};
    color: {theme["text_primary"]};
    selection-background-color: {theme["selection_bg"]};
    selection-color: {theme["selection_text"]};
    border: 1px solid {theme["border"]};
    border-radius: 6px;
    padding: 4px;
    outline: none;
}}

QTabWidget::pane {{
    border: 1px solid {theme["border"]};
    border-radius: 8px;
    background-color: {theme["bg_secondary"]};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {theme["tab_bg"]};
    color: {theme["tab_text"]};
    border: 1px solid {theme["border"]};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 14px;
    font-size: 10pt;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    background-color: {theme["tab_active"]};
    color: {theme["tab_text_active"]};
}}

QTabBar::tab:focus {{
    outline: none;
}}

QPlainTextEdit {{
    background-color: {theme["qtext_bg"]};
    color: {theme["qtext_text"]};
    border: none;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    selection-background-color: {theme["selection_bg"]};
    selection-color: {theme["selection_text"]};
}}

QFrame[statusIndicator="true"] {{
    border-radius: 4px;
    border: 1px solid {theme["border"]};
}}

QScrollBar:vertical {{
    background-color: {theme["bg_primary"]};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {theme["bg_tertiary"]};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {theme["border_hover"]};
}}

QScrollBar:horizontal {{
    background-color: {theme["bg_primary"]};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {theme["bg_tertiary"]};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {theme["border_hover"]};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}

QToolTip {{
    background-color: {theme["bg_secondary"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    border-radius: 4px;
    padding: 4px 8px;
}}

QMenu {{
    background-color: {theme["bg_secondary"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    border-radius: 4px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 20px;
    border-radius: 3px;
}}

QMenu::item:selected {{
    background-color: {theme["selection_bg"]};
    color: {theme["selection_text"]};
}}

QMenu::separator {{
    height: 1px;
    background: {theme["border"]};
    margin: 4px 8px;
}}

QMessageBox, QProgressDialog, QInputDialog {{
    background-color: {theme["bg_secondary"]};
    color: {theme["text_primary"]};
}}

QMessageBox QLabel, QProgressDialog QLabel, QInputDialog QLabel {{
    color: {theme["text_primary"]};
}}

QListView {{
    background-color: {theme["bg_input"]};
    color: {theme["text_primary"]};
    border: 1px solid {theme["border"]};
    selection-background-color: {theme["selection_bg"]};
    selection-color: {theme["selection_text"]};
    outline: none;
}}
"""


def apply_theme(app: QApplication) -> None:
    """Aplicar el tema oscuro fijo a la aplicacion.

    Aplica tanto el QSS (para widgets nativos de Qt) como el QPalette
    (para dialogos nativos que ignoran QSS, ej. QFileDialog).

    Args:
        app: Instancia de QApplication.
    """
    theme = _THEMES["dark"]
    app.setStyleSheet(build_qss(theme))
    app.setPalette(_build_palette(theme))