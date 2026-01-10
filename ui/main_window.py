import sys
import json
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                            QFileDialog, QInputDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QIcon

# Intentar importar la interfaz generada
try:
    from ui.osint_window_ui import Ui_MainWindow
except ImportError as e:
    print(f"Error al importar la interfaz: {e}")
    print("\nSOLUCIÓN: Ejecuta: pyuic6 osint_app.ui -o ui/osint_window_ui.py")
    sys.exit(1)

# Importar módulos propios
from core.worker import WorkerThread
from core.analyzer import AnalysisCoordinator
from models.history import AnalysisHistory
from exports.txt_exporter import TxtExporter
from exports.json_exporter import JsonExporter
from exports.csv_exporter import CsvExporter
from config.i18n import Translations
from config.icons_manager import IconManager

# En esta clase manejo la ventana principal de la aplicación
# La idea aquí es coordinar toda la interfaz y la lógica de los servicios
class AppOSINT(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        # Configurar UI generada por Qt Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Configurar ventana principal
        self.setWindowTitle("OSINT - Herramienta de Analisis de Redes")
        self.setFixedSize(779, 910)  # Tamaño fijo para consistencia visual
        
        # Configurar icono usando IconManager
        app_icon = IconManager.get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        else:
            # Fallback al icono anterior si IconManager falla
            try:
                self.setWindowIcon(QIcon("assets/icon_app.ico"))
            except:
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
    
    def setup_connections(self):
        # Configurar todas las conexiones de señales
        # Botones de análisis específicos
        self.ui.btn_geo.clicked.connect(lambda: self.run_analysis("geo"))
        self.ui.btn_whois.clicked.connect(lambda: self.run_analysis("whois"))
        self.ui.btn_ping.clicked.connect(lambda: self.run_analysis("ping"))
        self.ui.btn_dns.clicked.connect(lambda: self.run_analysis("dns"))
        self.ui.btn_ssl.clicked.connect(lambda: self.run_analysis("ssl"))
        self.ui.btn_headers.clicked.connect(lambda: self.run_analysis("headers"))
        self.ui.btn_portscan.clicked.connect(lambda: self.run_analysis("portscan"))
        self.ui.btn_reverse.clicked.connect(lambda: self.run_analysis("reverse"))
        
        # Botones de acción general
        self.ui.btn_quick.clicked.connect(self.run_complete_analysis)
        self.ui.btn_export.clicked.connect(self.export_results)
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_history.clicked.connect(self.show_history)
        self.ui.btn_copy.clicked.connect(self.copy_results)
        self.ui.btn_clear_results.clicked.connect(self.clear_current_tab)
        
        # Otros controles
        self.ui.entrada_dominio.returnPressed.connect(lambda: self.run_analysis("geo"))
        self.ui.comboLanguage.currentTextChanged.connect(self.change_language)
        self.ui.tabWidget.currentChanged.connect(self.update_risk_indicator)
    
    def setup_initial_state(self):
        # Configurar el estado inicial de la aplicación
        self.setup_spanish_texts()  # Español por defecto
        self.update_risk_indicator(0)  # Indicador en primera pestaña
        self.update_text_placeholders()  # Placeholders en español
    
    def setup_icons(self):
        # Configurar todos los iconos usando IconManager
        IconManager.setup_all_button_icons(self)
        IconManager.setup_all_tab_icons(self)
    
    def setup_spanish_texts(self):
        # Configurar todos los textos en español
        translations = Translations.get_spanish()
        
        # Textos principales
        self.ui.label_title.setText(translations["ui"]["title"])
        self.ui.label_legal.setText(translations["ui"]["legal"])
        self.ui.label_instrucciones.setText(translations["ui"]["instructions"])
        self.ui.entrada_dominio.setPlaceholderText(translations["ui"]["placeholder"])
        self.ui.label_risk.setText(translations["ui"]["risk"])
        self.ui.label_risk_text.setText(translations["ui"]["risk_inactive"])
        
        # Botones de herramientas
        self.ui.btn_geo.setText(translations["buttons"]["geo"])
        self.ui.btn_whois.setText(translations["buttons"]["whois"])
        self.ui.btn_ping.setText(translations["buttons"]["ping"])
        self.ui.btn_dns.setText(translations["buttons"]["dns"])
        self.ui.btn_ssl.setText(translations["buttons"]["ssl"])
        self.ui.btn_headers.setText(translations["buttons"]["headers"])
        self.ui.btn_portscan.setText(translations["buttons"]["portscan"])
        self.ui.btn_reverse.setText(translations["buttons"]["reverse"])
        
        # Botones de acción
        self.ui.btn_quick.setText(translations["buttons"]["quick"])
        self.ui.btn_export.setText(translations["buttons"]["export"])
        self.ui.btn_clear.setText(translations["buttons"]["clear"])
        
        # Tooltips
        self.ui.btn_history.setToolTip(translations["tooltips"]["history"])
        self.ui.btn_export.setToolTip(translations["tooltips"]["export"])
        self.ui.btn_clear.setToolTip(translations["tooltips"]["clear"])
        self.ui.btn_copy.setToolTip(translations["tooltips"]["copy"])
        self.ui.btn_clear_results.setToolTip(translations["tooltips"]["clear_results"])
        
        # Pestañas
        for i, tab_name in enumerate(translations["tabs"]):
            self.ui.tabWidget.setTabText(i, tab_name)
        
        # Textos de resultados y créditos
        self.ui.label_results.setText(translations["results"])
        self.ui.label_creditos_2.setText(translations["credits"])
    
    def setup_english_texts(self):
        # Configurar todos los textos en inglés
        translations = Translations.get_english()
        
        # Main texts
        self.ui.label_title.setText(translations["ui"]["title"])
        self.ui.label_legal.setText(translations["ui"]["legal"])
        self.ui.label_instrucciones.setText(translations["ui"]["instructions"])
        self.ui.entrada_dominio.setPlaceholderText(translations["ui"]["placeholder"])
        self.ui.label_risk.setText(translations["ui"]["risk"])
        self.ui.label_risk_text.setText(translations["ui"]["risk_inactive"])
        
        # Tool buttons
        self.ui.btn_geo.setText(translations["buttons"]["geo"])
        self.ui.btn_whois.setText(translations["buttons"]["whois"])
        self.ui.btn_ping.setText(translations["buttons"]["ping"])
        self.ui.btn_dns.setText(translations["buttons"]["dns"])
        self.ui.btn_ssl.setText(translations["buttons"]["ssl"])
        self.ui.btn_headers.setText(translations["buttons"]["headers"])
        self.ui.btn_portscan.setText(translations["buttons"]["portscan"])
        self.ui.btn_reverse.setText(translations["buttons"]["reverse"])
        
        # Action buttons
        self.ui.btn_quick.setText(translations["buttons"]["quick"])
        self.ui.btn_export.setText(translations["buttons"]["export"])
        self.ui.btn_clear.setText(translations["buttons"]["clear"])
        
        # Tooltips
        self.ui.btn_history.setToolTip(translations["tooltips"]["history"])
        self.ui.btn_export.setToolTip(translations["tooltips"]["export"])
        self.ui.btn_clear.setToolTip(translations["tooltips"]["clear"])
        self.ui.btn_copy.setToolTip(translations["tooltips"]["copy"])
        self.ui.btn_clear_results.setToolTip(translations["tooltips"]["clear_results"])
        
        # Tabs
        for i, tab_name in enumerate(translations["tabs"]):
            self.ui.tabWidget.setTabText(i, tab_name)
        
        # Results and credits
        self.ui.label_results.setText(translations["results"])
        self.ui.label_creditos_2.setText(translations["credits"])
    
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
            self.ui.text_geo, self.ui.text_whois, self.ui.text_ping,
            self.ui.text_dns, self.ui.text_ssl, self.ui.text_headers,
            self.ui.text_portscan, self.ui.text_reverse, self.ui.text_summary
        ]
        
        for widget, placeholder in zip(text_widgets, placeholders):
            widget.setPlaceholderText(placeholder)
    
    def get_target(self):
        # Obtener y validar el objetivo del campo de entrada
        target = self.ui.entrada_dominio.text().strip()
        
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
            self.ui.tabWidget.setCurrentIndex(tab_index[analysis_type])
        
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
        self.ui.tabWidget.setCurrentIndex(8)
        
        # Actualizar historial
        self.history.add_entry(target, "complete_analysis" if self.current_language == "en" else "análisis_completo")
    
    def generate_summary(self):
        # Generar resumen de todos los análisis realizados
        if self.current_language == "es":
            summary = f"""RESUMEN DE ANÁLISIS COMPLETO

OBJETIVO: {self.current_target}
FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANÁLISIS REALIZADOS:
"""
        else:
            summary = f"""COMPLETE ANALYSIS SUMMARY

TARGET: {self.current_target}
DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANALYSES PERFORMED:
"""
        
        # Lista de análisis con sus contenidos
        analyses = [
            ("Geolocalización" if self.current_language == "es" else "Geolocation", self.ui.text_geo.toPlainText()),
            ("WHOIS", self.ui.text_whois.toPlainText()),
            ("Ping", self.ui.text_ping.toPlainText()),
            ("DNS", self.ui.text_dns.toPlainText()),
            ("SSL/TLS", self.ui.text_ssl.toPlainText()),
            ("Headers HTTP" if self.current_language == "es" else "HTTP Headers", self.ui.text_headers.toPlainText()),
            ("Port Scan", self.ui.text_portscan.toPlainText()),
            ("Reverse IP", self.ui.text_reverse.toPlainText())
        ]
        
        # Contar análisis completados
        completed = 0
        for name, content in analyses:
            if content and not (content.startswith("Los resultados") or content.startswith("Geolocation results")):
                completed += 1
                if self.current_language == "es":
                    summary += f"  • {name}: [COMPLETADO]\n"
                else:
                    summary += f"  • {name}: [COMPLETED]\n"
            else:
                if self.current_language == "es":
                    summary += f"  • {name}: [NO REALIZADO]\n"
                else:
                    summary += f"  • {name}: [NOT PERFORMED]\n"
        
        # Estadísticas
        if self.current_language == "es":
            summary += f"\nESTADÍSTICAS:\n"
            summary += f"  • Total de análisis: {len(analyses)}\n"
            summary += f"  • Completados: {completed}\n"
            summary += f"  • Porcentaje: {(completed/len(analyses))*100:.1f}%\n"
            
            summary += f"\nRECOMENDACIONES:\n"
            summary += f"  1. Revisar vulnerabilidades SSL/TLS\n"
            summary += f"  2. Verificar blacklists de la IP\n"
            summary += f"  3. Monitorear cambios en DNS\n"
            summary += f"  4. Documentar hallazgos para auditoría\n"
            
            summary += f"\nNOTAS IMPORTANTES:\n"
            summary += f"  • Esta herramienta es para fines educativos\n"
            summary += f"  • Obtén autorización antes de cualquier prueba\n"
            summary += f"  • Cumple con todas las leyes y regulaciones\n"
        else:
            summary += f"\nSTATISTICS:\n"
            summary += f"  • Total analyses: {len(analyses)}\n"
            summary += f"  • Completed: {completed}\n"
            summary += f"  • Percentage: {(completed/len(analyses))*100:.1f}%\n"
            
            summary += f"\nRECOMMENDATIONS:\n"
            summary += f"  1. Review SSL/TLS vulnerabilities\n"
            summary += f"  2. Check IP blacklists\n"
            summary += f"  3. Monitor DNS changes\n"
            summary += f"  4. Document findings for audit\n"
            
            summary += f"\nIMPORTANT NOTES:\n"
            summary += f"  • This tool is for educational purposes\n"
            summary += f"  • Get authorization before any testing\n"
            summary += f"  • Comply with all laws and regulations\n"
        
        # Mostrar en pestaña de resumen
        self.ui.text_summary.setPlainText(summary)
    
    def display_results(self, analysis_type, result):
        # Mostrar resultados en la pestaña correspondiente
        text_widgets = {
            "geo": self.ui.text_geo,
            "whois": self.ui.text_whois,
            "ping": self.ui.text_ping,
            "dns": self.ui.text_dns,
            "ssl": self.ui.text_ssl,
            "headers": self.ui.text_headers,
            "portscan": self.ui.text_portscan,
            "reverse": self.ui.text_reverse
        }
        
        if analysis_type in text_widgets:
            text_widgets[analysis_type].setPlainText(result)
            
            # Desplazar cursor al inicio
            cursor = text_widgets[analysis_type].textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            text_widgets[analysis_type].setTextCursor(cursor)
        
        # Actualizar indicador de riesgo
        self.update_risk_indicator(self.ui.tabWidget.currentIndex())
        
        # Añadir al historial
        self.history.add_entry(self.current_target, analysis_type)
    
    def show_progress(self, message):
        # Mostrar mensaje de progreso
        self.ui.label_risk_text.setText(f"• {message}")
        self.ui.label_risk_text.setStyleSheet("color: #4a90e2;")
    
    def update_progress(self, value, message):
        # Actualizar indicador de progreso
        self.ui.label_risk_text.setText(f"• {message} ({value}%)")
    
    def update_risk_indicator(self, index):
        # Actualizar indicador de riesgo basado en pestaña activa
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0",
                 "#3F51B5", "#00BCD4", "#FF5722", "#795548", "#607D8B"]
        
        if index < len(colors):
            color = colors[index]
            
            # Aplicar color al indicador visual
            self.ui.riskIndicator.setStyleSheet(f"QFrame {{ background-color: {color}; border-radius: 4px; }}")
            self.ui.label_risk_text.setStyleSheet(f"font-size: 11pt; font-weight: 600; color: {color};")
            
            # Actualizar texto según idioma
            if self.current_language == "es":
                tab_names = ["Geolocalización", "WHOIS", "Ping", "DNS", 
                            "SSL/TLS", "Headers", "Port Scan", "Reverse IP", "Resumen"]
            else:
                tab_names = ["Geolocation", "WHOIS", "Ping", "DNS", 
                            "SSL/TLS", "Headers", "Port Scan", "Reverse IP", "Summary"]
            
            if index < len(tab_names):
                self.ui.label_risk_text.setText(f"• {tab_names[index]}")
    
    def show_error(self, error_message):
        # Mostrar mensaje de error
        if self.current_language == "es":
            QMessageBox.critical(self, "Error en análisis", f"Ocurrió un error:\n\n{error_message}")
            self.ui.label_risk_text.setText("• Error en análisis")
        else:
            QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n\n{error_message}")
            self.ui.label_risk_text.setText("• Analysis Error")
        
        self.ui.label_risk_text.setStyleSheet("color: #f44336;")
    
    def show_history(self):
        # Mostrar historial de análisis
        if self.history.count() == 0:
            if self.current_language == "es":
                QMessageBox.information(self, "Historial", "No hay análisis en el historial.")
            else:
                QMessageBox.information(self, "History", "No analysis in history.")
            return
        
        if self.current_language == "es":
            history_text = "HISTORIAL DE ANÁLISIS\n\n"
        else:
            history_text = "ANALYSIS HISTORY\n\n"
        
        # Mostrar los más recientes primero
        for i, entry in enumerate(self.history.get_history(), 1):
            history_text += f"{i}. [{entry['timestamp']}]\n"
            if self.current_language == "es":
                history_text += f"   Objetivo: {entry['target']}\n"
                history_text += f"   Análisis: {entry['type']}\n"
            else:
                history_text += f"   Target: {entry['target']}\n"
                history_text += f"   Analysis: {entry['type']}\n"
            history_text += f"   {'─'*40}\n"
        
        # Mostrar en pestaña de resumen
        self.ui.tabWidget.setCurrentIndex(8)
        self.ui.text_summary.setPlainText(history_text)
    
    def copy_results(self):
        # Copiar resultados de pestaña actual al portapapeles
        current_index = self.ui.tabWidget.currentIndex()
        
        text_widgets = [
            self.ui.text_geo, self.ui.text_whois, self.ui.text_ping,
            self.ui.text_dns, self.ui.text_ssl, self.ui.text_headers,
            self.ui.text_portscan, self.ui.text_reverse, self.ui.text_summary
        ]
        
        if current_index < len(text_widgets):
            text = text_widgets[current_index].toPlainText()
            
            if text:
                QApplication.clipboard().setText(text)
                
                if self.current_language == "es":
                    self.ui.label_risk_text.setText("• Resultados copiados")
                else:
                    self.ui.label_risk_text.setText("• Results copied")
                self.ui.label_risk_text.setStyleSheet("color: #4CAF50;")
                
                # Restaurar estado original después de 2 segundos
                QTimer.singleShot(2000, lambda: self.update_risk_indicator(current_index))
    
    def clear_current_tab(self):
        # Limpiar resultados de pestaña actual
        current_index = self.ui.tabWidget.currentIndex()
        
        text_widgets = [
            self.ui.text_geo, self.ui.text_whois, self.ui.text_ping,
            self.ui.text_dns, self.ui.text_ssl, self.ui.text_headers,
            self.ui.text_portscan, self.ui.text_reverse, self.ui.text_summary
        ]
        
        if current_index < len(text_widgets):
            text_widgets[current_index].clear()
            
            if self.current_language == "es":
                self.ui.label_risk_text.setText("• Resultados limpiados")
            else:
                self.ui.label_risk_text.setText("• Results cleared")
            self.ui.label_risk_text.setStyleSheet("color: #FF9800;")
            
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
            self.ui.entrada_dominio.clear()
            self.current_target = ""
            
            # Lista de todos los widgets de texto
            text_widgets = [
                self.ui.text_geo, self.ui.text_whois, self.ui.text_ping,
                self.ui.text_dns, self.ui.text_ssl, self.ui.text_headers,
                self.ui.text_portscan, self.ui.text_reverse, self.ui.text_summary
            ]
            
            # Limpiar todos los widgets
            for widget in text_widgets:
                widget.clear()
            
            # Restaurar placeholders
            self.update_text_placeholders()
            
            # Mostrar confirmación
            if self.current_language == "es":
                self.ui.label_risk_text.setText("• Todo limpiado")
            else:
                self.ui.label_risk_text.setText("• All cleared")
            self.ui.label_risk_text.setStyleSheet("color: #FF5722;")
            
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
                "geo": self.ui.text_geo.toPlainText(),
                "whois": self.ui.text_whois.toPlainText(),
                "ping": self.ui.text_ping.toPlainText(),
                "dns": self.ui.text_dns.toPlainText(),
                "ssl": self.ui.text_ssl.toPlainText(),
                "headers": self.ui.text_headers.toPlainText(),
                "portscan": self.ui.text_portscan.toPlainText(),
                "reverse": self.ui.text_reverse.toPlainText(),
                "summary": self.ui.text_summary.toPlainText()
            }
            
            # Exportar según formato seleccionado
            if format_choice == "TXT":
                TxtExporter.export(all_results, filename, self.current_language)
            elif format_choice == "JSON":
                JsonExporter.export(all_results, filename)
            elif format_choice == "CSV":
                CsvExporter.export(all_results, filename)
            
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
            self.setup_spanish_texts()
        else:
            self.current_language = "en"
            self.setup_english_texts()
        
        # Actualizar placeholders según nuevo idioma
        self.update_text_placeholders()
        
        # Actualizar indicador de riesgo
        self.update_risk_indicator(self.ui.tabWidget.currentIndex())