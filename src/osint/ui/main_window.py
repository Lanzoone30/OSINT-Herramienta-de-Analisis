"""main_window.py - Ventana principal de la aplicación OSINT."""
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                            QFileDialog, QInputDialog, QProgressDialog)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QTextCursor, QIcon

from osint.core.worker import WorkerThread
from osint.core.analyzer import AnalysisCoordinator
from osint.models.history import AnalysisHistory
from osint.exporters.export import export_results
from osint.ui.formatters import build_summary, build_history_text
from osint.ui.i18n import Translations
from osint.ui.layout import setup_ui, RESULT_TABS
from osint.ui.themes import apply_theme, STATUS_STATE_COLORS
from osint.config import IconManager

class AppOSINT(QMainWindow):
    """Ventana principal de la herramienta OSINT.

    Orquesta la UI (construida en layout.py), la lógica de análisis
    (AnalysisCoordinator), el historial y la exportación. Es el punto de
    unión entre la capa de presentación y la de dominio: conecta señales,
    despacha trabajos a hilos y traduce resultados a la interfaz.
    """

    # Tamaño fijo de la ventana: (ancho, alto) en píxeles
    WINDOW_SIZE = (900, 910)

    def __init__(self):
        super().__init__()

        # Configurar UI construida en Python (reemplaza el .ui de Qt Designer)
        setup_ui(self)

        # Cargar preferencias persistentes (idioma); English por defecto si no hay valor guardado.
        settings = QSettings()
        saved_language = settings.value("ui/language", "en", type=str)

        # Aplicar tema oscuro fijo (predefinido de la app)
        apply_theme(QApplication.instance())

        # Configurar ventana principal
        self.setWindowTitle(Translations.resolve("ui.window_title", saved_language))

        # 1. Window flags PRIMERO (antes de cualquier size constraint).
        # En Wayland/WSLg, setWindowFlags puede recrear la ventana, perdiendo
        # el setFixedSize si se aplica despues.
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint
        )

        # 2. Fixed size DESPUES (sobrevive el recreate del flag change)
        self.setFixedSize(*self.WINDOW_SIZE)  # Tamaño fijo para consistencia visual

        # 3. Maximum size como backup para WMs que ignoran WindowMaximizeButtonHint
        # (Wayland/WSLg a veces ignora el hint). Esto limita el tamaño máximo
        # incluso si el compositor intenta maximizar.
        self.setMaximumSize(*self.WINDOW_SIZE)

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
        self.current_language = saved_language  # Desde QSettings (fallback "en")

        # Configurar todas las conexiones de botones
        self.setup_connections()

        # Configurar estado inicial
        self.setup_initial_state()

        # Configurar iconos
        self.setup_icons()

    def changeEvent(self, event):
        # En Wayland/WSLg el compositor puede ofrecer maximizar pese al flag.
        # Si la ventana se maximiza, forzamos volver a tamaño normal para
        # evitar el bucle de configure/resize que crashea en WSLg.
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange and self.isMaximized():
            self.showNormal()
        super().changeEvent(event)

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
        # Usar 'textActivated' (no 'currentTextChanged'): se emite solo cuando
        # el usuario selecciona un item del popup, ya en proceso de cierre.
        # Evita que el popup quede abierto en algunos WMs (Linux/Wayland).
        self.comboLanguage.textActivated.connect(self.change_language)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def setup_initial_state(self):
        # Sincroniza el combo con el idioma persistido (0=Spanish, 1=English).
        self.comboLanguage.setCurrentIndex(0 if self.current_language == "es" else 1)
        self.apply_translations(Translations.get(self.current_language))
        self.set_status("ready")  # Barra de estado: Listo
        self.update_text_placeholders()

    def setup_icons(self):
        # Configurar todos los iconos usando IconManager
        IconManager.setup_all_button_icons(self)
        IconManager.setup_all_tab_icons(self)

    def tr_key(self, key, **kwargs):
        # Resuelve una clave de i18n al idioma actual. "default" (kwarg) es
        # el fallback cuando la clave no existe. kwargs alimenta .format().
        default = kwargs.pop("default", key)
        value = Translations.resolve(key, self.current_language, **kwargs)
        return value if value != key else default

    def get_text_widgets(self):
        return [getattr(self, name) for name in RESULT_TABS]

    def apply_translations(self, translations):
        # Aplicar los textos traducidos a la interfaz (ES o EN)
        ui = translations["ui"]
        buttons = translations["buttons"]
        tooltips = translations["tooltips"]

        # Textos principales
        self.label_title.setText(ui["title"])
        self.label_legal.setText(ui["legal"])
        self.label_instrucciones.setText(ui["instructions"])
        self.entrada_dominio.setPlaceholderText(ui["placeholder"])
        self.label_risk.setText(ui["risk"])
        self.label_risk_text.setText(ui["ready"])
        self.setWindowTitle(ui["window_title"])

        # Botones de herramientas (texto + tooltip)
        self.btn_geo.setText(buttons["geo"])
        self.btn_geo.setToolTip(tooltips["geo"])
        self.btn_whois.setText(buttons["whois"])
        self.btn_whois.setToolTip(tooltips["whois"])
        self.btn_ping.setText(buttons["ping"])
        self.btn_ping.setToolTip(tooltips["ping"])
        self.btn_dns.setText(buttons["dns"])
        self.btn_dns.setToolTip(tooltips["dns"])
        self.btn_ssl.setText(buttons["ssl"])
        self.btn_ssl.setToolTip(tooltips["ssl"])
        self.btn_headers.setText(buttons["headers"])
        self.btn_headers.setToolTip(tooltips["headers"])
        self.btn_portscan.setText(buttons["portscan"])
        self.btn_portscan.setToolTip(tooltips["portscan"])
        self.btn_reverse.setText(buttons["reverse"])
        self.btn_reverse.setToolTip(tooltips["reverse"])

        # Botones de acción
        self.btn_quick.setText(buttons["quick"])
        self.btn_quick.setToolTip(tooltips["quick"])
        self.btn_export.setText(buttons["export"])
        self.btn_export.setToolTip(tooltips["export"])
        self.btn_clear.setText(buttons["clear"])
        self.btn_clear.setToolTip(tooltips["clear"])

        # Botones de iconos con texto
        self.btn_history.setText(buttons["history"])
        self.btn_history.setToolTip(tooltips["history"])
        self.btn_copy.setText(buttons["copy"])
        self.btn_copy.setToolTip(tooltips["copy"])
        self.btn_clear_results.setText(buttons["clear_results"])
        self.btn_clear_results.setToolTip(tooltips["clear_results"])

        # Pestañas
        for i, tab_name in enumerate(translations["tabs"]):
            self.tabWidget.setTabText(i, tab_name)

        # Textos de resultados y créditos
        self.label_results.setText(ui["results"])
        self.label_creditos_2.setText(ui["credits"])

    def update_text_placeholders(self):
        # Actualizar placeholders segun idioma (unica fuente: Translations)
        placeholders = Translations.get(self.current_language)["placeholders"]
        for widget, placeholder in zip(self.get_text_widgets(), placeholders):
            widget.setPlaceholderText(placeholder)
    
    def get_target(self):
        # Lee el campo, valida no-vacío y limpia esquema/www antes de devolverlo.
        target = self.entrada_dominio.text().strip()

        if not target:
            QMessageBox.warning(
                self,
                self.tr_key("dialogs.empty_title"),
                self.tr_key("dialogs.empty_message")
            )
            return None

        # Limpiar y normalizar el objetivo
        target = target.replace("https://", "").replace("http://", "")
        if target.startswith("www."):
            target = target[4:]

        self.current_target = target
        return target
    
    def run_analysis(self, analysis_type):
        # Valida, cambia a la pestaña y delega el trabajo bloqueante a WorkerThread.
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
        self.show_progress(self.tr_key("status.starting", analysis=analysis_type))
        
        # Ejecutar en hilo separado
        self.worker = WorkerThread(self.perform_analysis, analysis_type, target)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(lambda result: self.display_results(analysis_type, result))
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def perform_analysis(self, analysis_type, target):
        # Ejecutado en hilo separado; delega al coordinador de dominio.
        return AnalysisCoordinator.perform_analysis(analysis_type, target, self.current_language)
    
    def run_complete_analysis(self):
        target = self.get_target()
        if not target:
            return

        # Crear diálogo de progreso (se actualiza via signals del worker)
        progress = QProgressDialog(
            self.tr_key("dialogs.progress_title"),
            self.tr_key("dialogs.progress_cancel"),
            0, 8, self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        # Crear worker en hilo separado (no bloquea UI)
        self.complete_worker = WorkerThread(
            self._complete_analysis_task, target
        )
        # Flag compartida para cancelación (UI -> worker)
        self.complete_worker.cancel_flag = False
        progress.canceled.connect(lambda: setattr(self.complete_worker, "cancel_flag", True))

        # Conectar signals a handlers UI (thread-safe via queued connections)
        self.complete_worker.progress.connect(
            lambda idx, label: self._on_complete_progress(progress, idx, label)
        )
        self.complete_worker.item_ready.connect(
            lambda atype, result: self.display_results(atype, result)
        )
        self.complete_worker.finished.connect(
            lambda _: self._on_complete_finished(progress, target)
        )
        self.complete_worker.error.connect(
            lambda msg: self.show_error(msg)
        )

        self.complete_worker.start()

    def _on_complete_progress(self, progress, index, label):
        # Handler UI: actualizar dialogo (corre en hilo principal)
        progress.setValue(index)
        progress.setLabelText(label)

    def _on_complete_finished(self, progress, target):
        # Handler UI: finalizar dialogo + generar resumen
        progress.setValue(8)
        self.generate_summary()
        self.tabWidget.setCurrentIndex(8)
        self.history.add_entry(target, self.tr_key("history_types.complete"))

    def _complete_analysis_task(self, target):
        # Corre en WorkerThread: emite progress()/item_ready() al hilo principal.
        # Cancelación vía flag compartido sondeado entre análisis (no a mitad de HTTP).
        analyses = ["geo", "whois", "ping", "dns", "ssl", "headers", "portscan", "reverse"]
        for i, analysis_type in enumerate(analyses):
            if self.complete_worker.cancel_flag:
                break

            label = Translations.resolve(
                "dialogs.progress_label",
                self.current_language,
                analysis=analysis_type,
            )
            self.complete_worker.progress.emit(i, label)

            result = self.perform_analysis(analysis_type, target)
            self.complete_worker.item_ready.emit(analysis_type, result)

        return None
    
    def generate_summary(self):
        # Generar resumen de todos los análisis realizados
        sections = [
            (self.tr_key("section_labels.geo"), self.text_geo.toPlainText()),
            ("WHOIS", self.text_whois.toPlainText()),
            ("Ping", self.text_ping.toPlainText()),
            ("DNS", self.text_dns.toPlainText()),
            ("SSL/TLS", self.text_ssl.toPlainText()),
            (self.tr_key("section_labels.headers"), self.text_headers.toPlainText()),
            ("Port Scan", self.text_portscan.toPlainText()),
            ("Reverse IP", self.text_reverse.toPlainText())
        ]

        summary = build_summary(self.current_target, sections, self.current_language)

        # Mostrar en pestaña de resumen
        self.text_summary.setPlainText(summary)
    
    def display_results(self, analysis_type, result):
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
        
            # Análisis completado: barra de estado en verde (success)
            self.set_status("success", self.tr_key("status_success", default="Completado"))

        # Registrar la entrada en el historial de análisis
        self.history.add_entry(self.current_target, analysis_type)

    def show_progress(self, message):
        # Mostrar mensaje de progreso (estado "running" / azul)
        self.set_status("running", message)

    def update_progress(self, value, message):
        # Actualizar indicador de progreso
        self.set_status("running", f"{message} ({value}%)")

    def set_status(self, state, message=None):
        """Barra de estado: indica ready / problemas / fallo mediante color + texto.

        Args:
            state: "ready" (verde), "running" (azul), "warning" (naranja),
                   "error" (rojo), "success" (verde).
            message: Texto opcional. Si es None, se usa el texto por defecto
                     del idioma actual (status_ready / status_running / etc.).
        """
        color = STATUS_STATE_COLORS.get(state, STATUS_STATE_COLORS["info"])
        # Indicador visual (cuadrito) cambia de color segun estado
        self.riskIndicator.setStyleSheet(
            f"QFrame {{ background-color: {color}; border-radius: 4px; }}"
        )
        # Texto de estado
        if message is None:
            message = self.tr_key(f"ui.status_{state}", default=state)
        self.label_risk_text.setText(message)
        self.label_risk_text.setStyleSheet(f"color: {color}; font-weight: 600;")

    def on_tab_changed(self, index):
        # Al cambiar de pestaña NO se sobreescribe el status operativo.
        # El status (ready/error/running) es independiente de la navegación.
        pass
    
    def show_error(self, error_message):
        # Mostrar mensaje de error (barra de estado en rojo)
        QMessageBox.critical(
            self,
            self.tr_key("dialogs.error_title"),
            self.tr_key("dialogs.error_message", message=error_message)
        )
        self.set_status("error", self.tr_key("dialogs.error_title"))
    
    def show_history(self):
        # Mostrar historial de análisis
        if self.history.count() == 0:
            QMessageBox.information(
                self,
                self.tr_key("dialogs.history_empty_title"),
                self.tr_key("dialogs.history_empty_message")
            )
            return

        history_text = build_history_text(self.history.get_history(), self.current_language)

        # Mostrar en pestaña de resumen
        self.tabWidget.setCurrentIndex(8)
        self.text_summary.setPlainText(history_text)
    
    def copy_results(self):
        # Copiar resultados de pestaña actual al portapapeles
        current_index = self.tabWidget.currentIndex()
        text_widgets = self.get_text_widgets()

        if current_index < len(text_widgets):
            text = text_widgets[current_index].toPlainText()

            if text:
                QApplication.clipboard().setText(text)

                self.set_status("success", self.tr_key("dialogs.copy_success"))

                # Restaurar a "ready" después de 2 segundos
                QTimer.singleShot(2000, lambda: self.set_status("ready"))

    def clear_current_tab(self):
        # Limpiar resultados de pestaña actual
        current_index = self.tabWidget.currentIndex()
        text_widgets = self.get_text_widgets()

        if current_index < len(text_widgets):
            text_widgets[current_index].clear()

            self.set_status("warning", self.tr_key("dialogs.clear_success"))

            # Restaurar a "ready" después de 2 segundos
            QTimer.singleShot(2000, lambda: self.set_status("ready"))

    def clear_all(self):
        # Limpiar todos los resultados y campo de entrada
        reply = QMessageBox.question(
            self,
            self.tr_key("dialogs.clear_all_title"),
            self.tr_key("dialogs.clear_all_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Limpiar campo de entrada
            self.entrada_dominio.clear()
            self.current_target = ""

            # Limpiar todos los widgets
            for widget in self.get_text_widgets():
                widget.clear()

            # Restaurar placeholders
            self.update_text_placeholders()

            # Mostrar confirmación
            self.set_status("danger", self.tr_key("dialogs.all_cleared"))

            # Restaurar a "ready" después de 2 segundos
            QTimer.singleShot(2000, lambda: self.set_status("ready"))
    
    def export_results(self):
        if not self.current_target:
            QMessageBox.warning(
                self,
                self.tr_key("dialogs.no_data_title"),
                self.tr_key("dialogs.no_data_message")
            )
            return

        # Formatos disponibles
        formats = ["TXT", "CSV", "JSON"]

        # Seleccionar formato
        format_choice, ok = QInputDialog.getItem(
            self,
            self.tr_key("dialogs.input_format_title"),
            self.tr_key("dialogs.input_format_label"),
            formats, 0, False
        )

        if not ok:
            return

        # Elegir ubicación para guardar
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr_key("dialogs.input_format_title"),
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
            QMessageBox.information(
                self,
                self.tr_key("dialogs.export_success_title"),
                self.tr_key("dialogs.export_success_message", path=filename)
            )

        except Exception as e:
            # Mostrar error
            QMessageBox.critical(
                self,
                self.tr_key("dialogs.export_error_title"),
                self.tr_key("dialogs.export_error_message", message=str(e))
            )

    def change_language(self, language):
        # Diferir con QTimer: dejar que Qt cierre el popup y evitar "fantasma" en WSLg/Wayland.
        QTimer.singleShot(0, lambda: self._apply_language(language))

    def _apply_language(self, language):
        if "Spanish" in language:
            self.current_language = "es"
        else:
            self.current_language = "en"

        QSettings().setValue("ui/language", self.current_language)
        self.apply_translations(Translations.get(self.current_language))

        # Actualizar placeholders según nuevo idioma
        self.update_text_placeholders()

        # Forzar repaint para limpiar rastro del popup en WSLg
        QApplication.processEvents()
        self.comboLanguage.repaint()
        self.set_status("ready")