"""
themes.py - Sistema de temas para la interfaz (dark / light / system).

Define las paletas de colores y genera el QSS completo que se aplica
a toda la aplicación al cambiar de tema.

Why this design: Centraliza los colores en un solo lugar para que el
theme switching sea un cambio de dict + regeneración de QSS, sin tocar
el código de la ventana.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

__all__ = ["apply_theme", "detect_system_theme", "get_theme"]

# Colores del indicador de estado por pestaña (mismo orden que tabWidget)
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

_THEMES = {
    "dark": {
        "bg_primary": "#0d0d0d",
        "bg_secondary": "#1a1a1a",
        "bg_tertiary": "#2a2a2a",
        "bg_hover": "#2a2a2a",
        "bg_input": "#1a1a1a",
        "text_primary": "#e8e8e8",
        "text_secondary": "#ffffff",
        "text_muted": "#666666",
        "text_placeholder": "#888888",
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
    "light": {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#e8e8e8",
        "bg_hover": "#e0e0e0",
        "bg_input": "#ffffff",
        "text_primary": "#1a1a1a",
        "text_secondary": "#000000",
        "text_muted": "#999999",
        "text_placeholder": "#aaaaaa",
        "border": "#d0d0d0",
        "border_hover": "#b0b0b0",
        "tab_bg": "#ececec",
        "tab_active": "#ffffff",
        "tab_text": "#666666",
        "tab_text_active": "#111111",
        "qtext_bg": "#ffffff",
        "qtext_text": "#1a1a1a",
        "selection_bg": "#2196F3",
        "selection_text": "#ffffff",
    },
}


def detect_system_theme() -> str:
    """Detectar si el sistema operativo está en modo oscuro o claro.

    Returns:
        "dark" o "light" según el brillo de la paleta del sistema.
    """
    palette = QApplication.instance().palette()
    window_color = palette.color(QPalette.ColorRole.Window)
    return "dark" if window_color.lightness() < 128 else "light"


def get_theme(name: str) -> dict:
    """Resolver el tema, teniendo en cuenta que "system" se detecta en runtime.

    Args:
        name: Nombre del tema: "dark", "light" o "system".

    Returns:
        Dict con los colores del tema resuelto.
    """
    if name == "system":
        return _THEMES[detect_system_theme()]
    return _THEMES.get(name, _THEMES["dark"])


def build_qss(theme: dict) -> str:
    """Generar el QSS completo de la aplicación a partir de una paleta.

    Args:
        theme: Dict de colores (ver get_theme).

    Returns:
        String QSS listo para aplicar con app.setStyleSheet().
    """
    return f"""
QMainWindow, QWidget {{
    background-color: {theme["bg_primary"]};
    color: {theme["text_primary"]};
    font-family: 'Segoe UI', sans-serif;
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
    color: #ff6b6b;
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

QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}
"""


def apply_theme(app: QApplication, name: str) -> str:
    """Aplicar un tema a la aplicación.

    Args:
        app: Instancia de QApplication.
        name: Nombre del tema: "dark", "light" o "system".

    Returns:
        El nombre del tema resuelto (útil para "system").
    """
    resolved = get_theme(name)
    app.setStyleSheet(build_qss(resolved))
    return name
