"""
layout.py - Construcción del layout de la ventana principal en Python.

Reemplaza el archivo .ui de Qt Designer y su módulo generado. Construye
todo el widget tree y lo expone como atributos de la ventana
(win.btn_geo, win.tabWidget, etc.) para que main_window.py no dependa
de pyuic6.

Why this design: El layout en Python puro es más mantenible, no requiere
herramientas externas y permite que los estilos vengan de themes.py en
runtime (necesario para el theme switching).
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QTabWidget,
    QPlainTextEdit, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
)

__all__ = ["setup_ui"]

# Nombres de los botones de análisis (orden del grid 2x4)
TOOL_BUTTONS = [
    "btn_geo", "btn_whois", "btn_ping", "btn_dns",
    "btn_ssl", "btn_headers", "btn_portscan", "btn_reverse",
]

# Nombres de los editores de texto de cada pestaña
RESULT_TABS = [
    "text_geo", "text_whois", "text_ping", "text_dns",
    "text_ssl", "text_headers", "text_portscan", "text_reverse",
    "text_summary",
]

# Botones de acción de la barra inferior
ACTION_BUTTONS = [
    "btn_copy", "btn_export", "btn_clear", "btn_history", "btn_clear_results",
]


def setup_ui(window: QWidget) -> None:
    """Construir todos los widgets y layouts de la ventana principal.

    Args:
        window: La ventana principal (QMainWindow). Los widgets quedan
            expuestos como atributos: window.btn_geo, window.tabWidget, etc.
    """
    # Widget central contenedor
    central = QWidget(window)
    window.setCentralWidget(central)

    main_layout = QVBoxLayout(central)
    main_layout.setSpacing(24)
    main_layout.setContentsMargins(32, 32, 32, 24)

    # ---------- 1. HEADER: título + legal + idioma + tema ----------
    header = QHBoxLayout()
    header.setSpacing(16)

    title_stack = QVBoxLayout()
    title_stack.setSpacing(4)

    label_title = QLabel(central)
    label_title.setProperty("labelClass", "title")
    title_stack.addWidget(label_title)

    label_legal = QLabel(central)
    label_legal.setProperty("labelClass", "legal")
    label_legal.setWordWrap(True)
    title_stack.addWidget(label_legal)

    header.addLayout(title_stack)
    header.addStretch()

    combo_language = QComboBox(central)
    combo_language.setMinimumSize(140, 36)
    combo_language.addItem("Español")
    combo_language.addItem("English")
    header.addWidget(combo_language)

    combo_theme = QComboBox(central)
    combo_theme.setMinimumSize(130, 36)
    combo_theme.addItem("Dark")
    combo_theme.addItem("Light")
    combo_theme.addItem("System")
    header.addWidget(combo_theme)

    main_layout.addLayout(header)

    # ---------- 2. INPUT: instrucciones + campo de objetivo ----------
    input_section = QVBoxLayout()
    input_section.setSpacing(12)

    label_instrucciones = QLabel(central)
    label_instrucciones.setProperty("labelClass", "subtitle")
    input_section.addWidget(label_instrucciones)

    entrada_dominio = QLineEdit(central)
    input_section.addWidget(entrada_dominio)

    main_layout.addLayout(input_section)

    # ---------- 3. GRID de botones de análisis (2x4) ----------
    tools_grid = QGridLayout()
    tools_grid.setSpacing(10)

    for i, btn_name in enumerate(TOOL_BUTTONS):
        button = QPushButton(central)
        button.setProperty("toolButton", True)
        tools_grid.addWidget(button, i // 4, i % 4)
        setattr(window, btn_name, button)

    main_layout.addLayout(tools_grid)

    # ---------- 4. Botón de análisis completo ----------
    btn_quick = QPushButton(central)
    btn_quick.setProperty("quickButton", True)
    btn_quick.setMinimumHeight(46)
    main_layout.addWidget(btn_quick)
    window.btn_quick = btn_quick

    # ---------- 5. RESULTADOS: header + tabs ----------
    label_results = QLabel(central)
    label_results.setProperty("labelClass", "results")
    main_layout.addWidget(label_results)
    window.label_results = label_results

    tab_widget = QTabWidget(central)
    for text_name in RESULT_TABS:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        text_edit = QPlainTextEdit(tab)
        text_edit.setReadOnly(True)
        tab_layout.addWidget(text_edit)
        tab_widget.addTab(tab, "")
        setattr(window, text_name, text_edit)

    main_layout.addWidget(tab_widget)
    window.tabWidget = tab_widget

    # ---------- 6. BOTONES DE ACCIÓN ----------
    actions_bar = QHBoxLayout()
    actions_bar.setSpacing(10)

    for btn_name in ACTION_BUTTONS:
        button = QPushButton(central)
        button.setProperty("actionButton", True)
        actions_bar.addWidget(button)
        setattr(window, btn_name, button)

    main_layout.addLayout(actions_bar)

    # ---------- 7. FOOTER: estado + créditos ----------
    footer = QHBoxLayout()
    footer.setSpacing(10)

    risk_indicator = QFrame(central)
    risk_indicator.setProperty("statusIndicator", True)
    risk_indicator.setFixedSize(10, 24)
    footer.addWidget(risk_indicator)
    window.riskIndicator = risk_indicator

    label_risk = QLabel(central)
    footer.addWidget(label_risk)
    window.label_risk = label_risk

    label_risk_text = QLabel(central)
    label_risk_text.setProperty("labelClass", "status")
    footer.addWidget(label_risk_text)
    window.label_risk_text = label_risk_text

    footer.addStretch()

    label_creditos = QLabel(central)
    label_creditos.setProperty("labelClass", "credits")
    footer.addWidget(label_creditos)
    window.label_creditos_2 = label_creditos

    main_layout.addLayout(footer)

    # ---------- Exponer los widgets restantes como atributos de la ventana ----------
    window.label_title = label_title
    window.label_legal = label_legal
    window.comboLanguage = combo_language
    window.comboTheme = combo_theme
    window.label_instrucciones = label_instrucciones
    window.entrada_dominio = entrada_dominio
