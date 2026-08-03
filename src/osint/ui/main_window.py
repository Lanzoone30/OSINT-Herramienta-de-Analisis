"""main_window.py - Ventana principal de la aplicación OSINT."""
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                            QFileDialog, QInputDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QIcon

from osint.core.worker import WorkerThread
from osint.core.analyzer import AnalysisCoordinator
from osint.models.history import AnalysisHistory
from osint.exporters.export import export_results
from osint.ui.formatters import build_summary, build_history_text
from osint.ui.i18n import Translations
from osint.ui.layout import setup_ui
from osint.ui.themes import apply_theme
from osint.config import IconManager

class AppOSINT(QMainWindow):

    # Tamaño fijo de la ventana: (ancho, alto) en píxeles
    WINDOW_SIZE = (900, 910)

    def __init__(self):
        super().__init__()

        # Configurar UI construida en Python (reemplaza el .ui de Qt Designer)
        setup_ui(self)

        # Aplicar tema por defecto (dark)
        apply_theme(QApplication.instance(), "dark")

        # Configurar ventana principal
        self.setWindowTitle("OSINT - Herramienta de Analisis de Redes")
        self.setFixedSize(*self.WINDOW_SIZE)  # Tamaño fijo para consistencia visual

        # Prohibir maximizar: elimina el botón de maximizar de la barra de título
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint
        )
        
        # Configurar icono usando IconManager
        app_icon = IconManager.get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        else:
            # Fallback al icono anterior si IconManager falla
            try:
                self.setWindowIcon(QIcon("assets/icon_app.ico"))
            except OSError:
                pass
        
        # Inicializar estado de la aplicación
        self.current_target = ""
        self.history = AnalysisHistory(max_entries=50)  # Historial con límite
        self.results_data = {}
        self.current_language = "es"  # Español por defecto
        
        # Configurar todas las conexiones de botones
        self.setup_connections()
        
        # Configurar estado inicial
        self.setup_initial_state()
        
        # Configurar iconos
        self.setup_icons()
        
        print("Aplicación inicializada correctamente")

    def resizeEvent(self, event):
        # Forzar el tamaño fijo incluso si el gestor de ventanas (WM)
        # intenta redimensionar (necesario en Linux/Wayland/WSLg)
        self.resize(*self.WINDOW_SIZE)
        super().resizeEvent(event)

    def setup_connections(self):
        # Configurar todas las conexiones de señales
        # Botones de análisis específicos
        self.btn_geo.clicked.connect(lambda: self.run_analysis("geo"))
        self.btn_whois.clicked.connect(lambda: self.run_analysis("whois"))
        self.btn_ping.clicked.connect(lambda: self.run_analysis("ping"))
        self.btn_dns.clicked.connect(lambda: self.run_analysis("dns"))
        self.btn_ssl.clicked.connect(lambda: self.run_analysis("ssl"))
        self.btn_headers.clicked.connect(lambda: self.run_analysis("headers"))
        self.btn_portscan.clicked.connect(lambda: self.run_analysis("portscan"))
        self.btn_reverse.clicked.connect(lambda: self.run_analysis("reverse"))
        
        # Botones de acción general
        self.btn_quick.clicked.connect(self.run_complete_analysis)
        self.btn_export.clicked.connect(self.export_results)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_history.clicked.connect(self.show_history)
        self.btn_copy.clicked.connect(self.copy_results)
        self.btn_clear_results.clicked.connect(self.clear_current_tab)
        
        # Otros controles
        self.entrada_dominio.returnPressed.connect(lambda: self.run_analysis("geo"))
        self.comboLanguage.currentTextChanged.connect(self.change_language)
        self.comboTheme.currentTextChanged.connect(self.change_theme)
        self.tabWidget.currentChanged.connect(self.update_risk_indicator)

    def change_theme(self, theme_name):
        # Cambiar el tema de la aplicación (dark / light / system)
        app = QApplication.instance()
        apply_theme(app, theme_name.lower())
    
    def setup_initial_state(self):
        # Configurar el estado inicial de la aplicación
        self.apply_translations(Translations.get_spanish())  # Español por defecto
        self.update_risk_indicator(0)  # Indicador en primera pestaña
        self.update_text_placeholders()  # Placeholders en español
    
    def setup_icons(self):
        # Configurar todos los iconos usando IconManager
        IconManager.setup_all_button_icons(self)
        IconManager.setup_all_tab_icons(self)
    
    def apply_translations(self, translations):
        # Aplicar los textos traducidos a la interfaz (ES o EN)
        # Textos principales
        self.label_title.setText(translations["ui"]["title"])
        self.label_legal.setText(translations["ui"]["legal"])
        self.label_instrucciones.setText(translations["ui"]["instructions"])
        self.entrada_dominio.setPlaceholderText(translations["ui"]["placeholder"])
        self.label_risk.setText(translations["ui"]["risk"])
        self.label_risk_text.setText(translations["ui"]["risk_inactive"])

        # Botones de herramientas
        self.btn_geo.setText(translations["buttons"]["geo"])
        self.btn_whois.setText(translations["buttons"]["whois"])
        self.btn_ping.setText(translations["buttons"]["ping"])
        self.btn_dns.setText(translations["buttons"]["dns"])
        self.btn_ssl.setText(translations["buttons"]["ssl"])
        self.btn_headers.setText(translations["buttons"]["headers"])
        self.btn_portscan.setText(translations["buttons"]["portscan"])
        self.btn_reverse.setText(translations["buttons"]["reverse"])

        # Botones de acción
        self.btn_quick.setText(translations["buttons"]["quick"])
        self.btn_export.setText(translations["buttons"]["export"])
        self.btn_clear.setText(translations["buttons"]["clear"])

        # Tooltips
        self.btn_history.setToolTip(translations["tooltips"]["history"])
        self.btn_export.setToolTip(translations["tooltips"]["export"])
        self.btn_clear.setToolTip(translations["tooltips"]["clear"])
        self.btn_copy.setToolTip(translations["tooltips"]["copy"])
        self.btn_clear_results.setToolTip(translations["tooltips"]["clear_results"])

        # Pestañas
        for i, tab_name in enumerate(translations["tabs"]):
            self.tabWidget.setTabText(i, tab_name)

        # Textos de resultados y créditos
        self.label_results.setText(translations["results"])
        self.label_creditos_2.setText(translations["credits"])
    
    def update_text_placeholders(self):
        # Actualizar placeholders según idioma
        if self.current_language == "es":
            placeholders = [
                "Los resultados de geolocalización aparecerán aquí...",
                "Los resultados WHOIS aparecerán aquí...",
                "Los resultados de ping/traceroute aparecerán aquí...",
                "Los resultados DNS aparecerán aquí...",
                "Los resultados SSL/TLS aparecerán aquí...",
                "Los resultados de headers HTTP aparecerán aquí...",
                "Los resultados de port scan aparecerán aquí...",
                "Los resultados de reverse IP aparecerán aquí...",
                "El resumen de análisis aparecerá aquí..."
            ]
        else:
            placeholders = [
                "Geolocation results will appear here...",
                "WHOIS results will appear here...",
                "Ping/traceroute results will appear here...",
                "DNS results will appear here...",
                "SSL/TLS results will appear here...",
                "HTTP headers results will appear here...",
                "Port scan results will appear here...",
                "Reverse IP results will appear here...",
                "Analysis summary will appear here..."
            ]
        
        text_widgets = [
            self.text_geo, self.text_whois, self.text_ping,
            self.text_dns, self.text_ssl, self.text_headers,
            self.text_portscan, self.text_reverse, self.text_summary
        ]
        
        for widget, placeholder in zip(text_widgets, placeholders):
            widget.setPlaceholderText(placeholder)
    
    def get_target(self):
        # Obtener y validar el objetivo del campo de entrada
        target = self.entrada_dominio.text().strip()
        
        if not target:
            if self.current_language == "es":
                QMessageBox.warning(self, "Campo vacío", 
                                   "Por favor, ingresa una IP, dominio o URL")
            else:
                QMessageBox.warning(self, "Empty field", 
                                   "Please enter an IP, domain or URL")
            return None
        
        # Limpiar y normalizar el objetivo
        target = target.replace("https://", "").replace("http://", "")
        if target.startswith("www."):
            target = target[4:]
        
        self.current_target = target
        return target
    
    def run_analysis(self, analysis_type):
        # Ejecutar un análisis específico
        target = self.get_target()
        if not target:
            return
        
        # Cambiar a pestaña correspondiente
        tab_index = {
            "geo": 0, "whois": 1, "ping": 2, "dns": 3,
            "ssl": 4, "headers": 5, "portscan": 6, "reverse": 7
        }
        if analysis_type in tab_index:
            self.tabWidget.setCurrentIndex(tab_index[analysis_type])
        
        # Mostrar progreso
        if self.current_language == "es":
            self.show_progress(f"Iniciando análisis de {analysis_type}...")
        else:
            self.show_progress(f"Starting {analysis_type} analysis...")
        
        # Ejecutar en hilo separado
        self.worker = WorkerThread(self.perform_analysis, analysis_type, target)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(lambda result: self.display_results(analysis_type, result))
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def perform_analysis(self, analysis_type, target):
        # Realizar el análisis (ejecutado en hilo separado)
        return AnalysisCoordinator.perform_analysis(analysis_type, target, self.current_language)
    
    def run_complete_analysis(self):
        # Ejecutar todos los análisis en secuencia
        target = self.get_target()
        if not target:
            return
        
        # Crear diálogo de progreso
        if self.current_language == "es":
            progress = QProgressDialog("Ejecutando análisis completo...", "Cancelar", 0, 8, self)
        else:
            progress = QProgressDialog("Running complete analysis...", "Cancel", 0, 8, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        # Lista de análisis a ejecutar
        analyses = ["geo", "whois", "ping", "dns", "ssl", "headers", "portscan", "reverse"]
        
        # Ejecutar cada análisis secuencialmente
        for i, analysis_type in enumerate(analyses):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            if self.current_language == "es":
                progress.setLabelText(f"Analizando {analysis_type}...")
            else:
                progress.setLabelText(f"Analyzing {analysis_type}...")
            QApplication.processEvents()
            
            try:
                result = self.perform_analysis(analysis_type, target)
                self.display_results(analysis_type, result)
            except Exception as e:
                self.show_error(str(e))
        
        progress.setValue(8)
        
        # Generar resumen final
        self.generate_summary()
        self.tabWidget.setCurrentIndex(8)
        
        # Actualizar historial
        self.history.add_entry(target, "complete_analysis" if self.current_language == "en" else "análisis_completo")
    
    def generate_summary(self):
        # Generar resumen de todos los análisis realizados
        sections = [
            ("Geolocalización" if self.current_language == "es" else "Geolocation", self.text_geo.toPlainText()),
            ("WHOIS", self.text_whois.toPlainText()),
            ("Ping", self.text_ping.toPlainText()),
            ("DNS", self.text_dns.toPlainText()),
            ("SSL/TLS", self.text_ssl.toPlainText()),
            ("Headers HTTP" if self.current_language == "es" else "HTTP Headers", self.text_headers.toPlainText()),
            ("Port Scan", self.text_portscan.toPlainText()),
            ("Reverse IP", self.text_reverse.toPlainText())
        ]

        summary = build_summary(self.current_target, sections, self.current_language)

        # Mostrar en pestaña de resumen
        self.text_summary.setPlainText(summary)
    
    def display_results(self, analysis_type, result):
        # Mostrar resultados en la pestaña correspondiente
        text_widgets = {
            "geo": self.text_geo,
            "whois": self.text_whois,
            "ping": self.text_ping,
            "dns": self.text_dns,
            "ssl": self.text_ssl,
            "headers": self.text_headers,
            "portscan": self.text_portscan,
            "reverse": self.text_reverse
        }
        
        if analysis_type in text_widgets:
            text_widgets[analysis_type].setPlainText(result)
            
            # Desplazar cursor al inicio
            cursor = text_widgets[analysis_type].textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            text_widgets[analysis_type].setTextCursor(cursor)
        
        # Actualizar indicador de riesgo
        self.update_risk_indicator(self.tabWidget.currentIndex())
        
        # Añadir al historial
        self.history.add_entry(self.current_target, analysis_type)
    
    def show_progress(self, message):
        # Mostrar mensaje de progreso
        self.label_risk_text.setText(f"• {message}")
        self.label_risk_text.setStyleSheet("color: #4a90e2;")
    
    def update_progress(self, value, message):
        # Actualizar indicador de progreso
        self.label_risk_text.setText(f"• {message} ({value}%)")
    
    def update_risk_indicator(self, index):
        # Actualizar indicador de riesgo basado en pestaña activa
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0",
                 "#3F51B5", "#00BCD4", "#FF5722", "#795548", "#607D8B"]
        
        if index < len(colors):
            color = colors[index]
            
            # Aplicar color al indicador visual
            self.riskIndicator.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 4px; }}")
            self.label_risk_text.setStyleSheet(f"font-size: 11pt; font-weight: 600; color: {color};")
            
            # Actualizar texto según idioma
            if self.current_language == "es":
                tab_names = ["Geolocalización", "WHOIS", "Ping", "DNS", 
                            "SSL/TLS", "Headers", "Port Scan", "Reverse IP", "Resumen"]
            else:
                tab_names = ["Geolocation", "WHOIS", "Ping", "DNS", 
                            "SSL/TLS", "Headers", "Port Scan", "Reverse IP", "Summary"]
            
            if index < len(tab_names):
                self.label_risk_text.setText(f"• {tab_names[index]}")
    
    def show_error(self, error_message):
        # Mostrar mensaje de error
        if self.current_language == "es":
            QMessageBox.critical(self, "Error en análisis", f"Ocurrió un error:\n\n{error_message}")
            self.label_risk_text.setText("• Error en análisis")
        else:
            QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n\n{error_message}")
            self.label_risk_text.setText("• Analysis Error")
        
        self.label_risk_text.setStyleSheet("color: #f44336;")
    
    def show_history(self):
        # Mostrar historial de análisis
        if self.history.count() == 0:
            if self.current_language == "es":
                QMessageBox.information(self, "Historial", "No hay análisis en el historial.")
            else:
                QMessageBox.information(self, "History", "No analysis in history.")
            return

        history_text = build_history_text(self.history.get_history(), self.current_language)

        # Mostrar en pestaña de resumen
        self.tabWidget.setCurrentIndex(8)
        self.text_summary.setPlainText(history_text)
    
    def copy_results(self):
        # Copiar resultados de pestaña actual al portapapeles
        current_index = self.tabWidget.currentIndex()
        
        text_widgets = [
            self.text_geo, self.text_whois, self.text_ping,
            self.text_dns, self.text_ssl, self.text_headers,
            self.text_portscan, self.text_reverse, self.text_summary
        ]
        
        if current_index < len(text_widgets):
            text = text_widgets[current_index].toPlainText()
            
            if text:
                QApplication.clipboard().setText(text)
                
                if self.current_language == "es":
                    self.label_risk_text.setText("• Resultados copiados")
                else:
                    self.label_risk_text.setText("• Results copied")
                self.label_risk_text.setStyleSheet("color: #4CAF50;")
                
                # Restaurar estado original después de 2 segundos
                QTimer.singleShot(2000, lambda: self.update_risk_indicator(current_index))
    
    def clear_current_tab(self):
        # Limpiar resultados de pestaña actual
        current_index = self.tabWidget.currentIndex()
        
        text_widgets = [
            self.text_geo, self.text_whois, self.text_ping,
            self.text_dns, self.text_ssl, self.text_headers,
            self.text_portscan, self.text_reverse, self.text_summary
        ]
        
        if current_index < len(text_widgets):
            text_widgets[current_index].clear()
            
            if self.current_language == "es":
                self.label_risk_text.setText("• Resultados limpiados")
            else:
                self.label_risk_text.setText("• Results cleared")
            self.label_risk_text.setStyleSheet("color: #FF9800;")
            
            # Restaurar estado original después de 2 segundos
            QTimer.singleShot(2000, lambda: self.update_risk_indicator(current_index))
    
    def clear_all(self):
        # Limpiar todos los resultados y campo de entrada
        if self.current_language == "es":
            reply = QMessageBox.question(self, "Limpiar todo",
                                       "¿Estás seguro de que quieres limpiar todos los resultados?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        else:
            reply = QMessageBox.question(self, "Clear All",
                                       "Are you sure you want to clear all results?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar campo de entrada
            self.entrada_dominio.clear()
            self.current_target = ""
            
            # Lista de todos los widgets de texto
            text_widgets = [
                self.text_geo, self.text_whois, self.text_ping,
                self.text_dns, self.text_ssl, self.text_headers,
                self.text_portscan, self.text_reverse, self.text_summary
            ]
            
            # Limpiar todos los widgets
            for widget in text_widgets:
                widget.clear()
            
            # Restaurar placeholders
            self.update_text_placeholders()
            
            # Mostrar confirmación
            if self.current_language == "es":
                self.label_risk_text.setText("• Todo limpiado")
            else:
                self.label_risk_text.setText("• All cleared")
            self.label_risk_text.setStyleSheet("color: #FF5722;")
            
            # Restaurar estado original después de 2 segundos
            QTimer.singleShot(2000, lambda: self.update_risk_indicator(0))
    
    def export_results(self):
        # Exportar resultados a diferentes formatos
        if not self.current_target:
            if self.current_language == "es":
                QMessageBox.warning(self, "Sin datos", "No hay resultados para exportar.")
            else:
                QMessageBox.warning(self, "No data", "No results to export.")
            return
        
        # Formatos disponibles
        formats = ["TXT", "CSV", "JSON"]
        
        # Seleccionar formato
        if self.current_language == "es":
            format_choice, ok = QInputDialog.getItem(
                self, "Exportar resultados", "Selecciona formato:", formats, 0, False
            )
        else:
            format_choice, ok = QInputDialog.getItem(
                self, "Export Results", "Select format:", formats, 0, False
            )
        
        if not ok:
            return
        
        # Elegir ubicación para guardar
        if self.current_language == "es":
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar resultados",
                f"osint_analysis_{self.current_target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                f"{format_choice} Files (*.{format_choice.lower()})"
            )
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Results",
                f"osint_analysis_{self.current_target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                f"{format_choice} Files (*.{format_choice.lower()})"
            )
        
        if not filename:
            return
        
        try:
            # Recopilar todos los resultados
            all_results = {
                "target": self.current_target,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "geo": self.text_geo.toPlainText(),
                "whois": self.text_whois.toPlainText(),
                "ping": self.text_ping.toPlainText(),
                "dns": self.text_dns.toPlainText(),
                "ssl": self.text_ssl.toPlainText(),
                "headers": self.text_headers.toPlainText(),
                "portscan": self.text_portscan.toPlainText(),
                "reverse": self.text_reverse.toPlainText(),
                "summary": self.text_summary.toPlainText()
            }
            
            # Exportar según formato seleccionado
            export_results(all_results, filename, format_choice.lower(), self.current_language)
            
            # Mostrar confirmación
            if self.current_language == "es":
                QMessageBox.information(self, "Exportación exitosa", 
                                      f"Resultados exportados a:\n{filename}")
            else:
                QMessageBox.information(self, "Export Successful", 
                                      f"Results exported to:\n{filename}")
            
        except Exception as e:
            # Mostrar error
            if self.current_language == "es":
                QMessageBox.critical(self, "Error en exportación", 
                                   f"No se pudo exportar: {str(e)}")
            else:
                QMessageBox.critical(self, "Export Error", 
                                   f"Could not export: {str(e)}")
    
    def change_language(self, language):
        # Cambiar idioma de la interfaz
        if "Español" in language:
            self.current_language = "es"
            self.apply_translations(Translations.get_spanish())
        else:
            self.current_language = "en"
            self.apply_translations(Translations.get_english())
        
        # Actualizar placeholders según nuevo idioma
        self.update_text_placeholders()
        
        # Actualizar indicador de riesgo
        self.update_risk_indicator(self.tabWidget.currentIndex())