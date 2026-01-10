import os
import sys
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize

# En esta clase manejo los iconos con compatibilidad para .exe y desarrollo
# La idea aquí es detectar automáticamente si estamos en un ejecutable PyInstaller
class IconManager:
    
    # Método para obtener ruta base compatible con PyInstaller
    @staticmethod
    def _get_base_path():
        # Obtiene ruta base compatible con .exe y desarrollo
        try:
            # Si estamos en un ejecutable de PyInstaller
            # PyInstaller inyecta estas variables cuando se ejecuta desde .exe
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS  # Directorio temporal donde PyInstaller extrae archivos
            else:
                # En desarrollo, desde el directorio raíz del proyecto
                return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except:
            # Fallback por si hay algún error
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Rutas calculadas dinámicamente según el entorno
    @staticmethod
    def _get_buttons_path():
        return os.path.join(IconManager._get_base_path(), "assets", "buttons")
    
    @staticmethod
    def _get_tabs_path():
        return os.path.join(IconManager._get_base_path(), "assets", "tabs")
    
    @staticmethod
    def _get_assets_path():
        return os.path.join(IconManager._get_base_path(), "assets")
    
    # Tamaños fijos (mantenidos de la versión anterior)
    BUTTON_SIZE = QSize(32, 32)
    TAB_SIZE = QSize(20, 20)
    SMALL_BUTTON_SIZE = QSize(24, 24)
    
    # Factor de escala
    SCALE_FACTOR = 1.0
    
    # Mapeo de iconos (igual que antes)
    ICON_MAP = {
        "geo": "geo.ico",
        "whois": "whois.ico",
        "ping": "ping.ico",
        "dns": "dns.ico",
        "ssl": "ssl.ico",
        "headers": "header.ico",
        "portscan": "portscan.ico",
        "reverse": "reverse.ico",
        
        "quick": "quick_scan.ico",
        "export": "export.ico",
        "clear": "clear.ico",
        "copy": "copy.ico",
        "history": "copy.ico",
        "clear_results": "clear.ico",
        
        "tab_geo": "geo.ico",
        "tab_whois": "whois.ico",
        "tab_ping": "ping.ico",
        "tab_dns": "dns.ico",
        "tab_ssl": "ssl.ico",
        "tab_headers": "header.ico",
        "tab_portscan": "portscan.ico",
        "tab_reverse": "reverse.ico",
        "tab_summary": "header.ico",
    }
    
    @staticmethod
    def get_scaled_size(base_size):
        # Escala un tamaño según el factor global
        if IconManager.SCALE_FACTOR == 1.0:
            return base_size
        return QSize(
            int(base_size.width() * IconManager.SCALE_FACTOR),
            int(base_size.height() * IconManager.SCALE_FACTOR)
        )
    
    @staticmethod
    def _find_icon_file(filename):
        # Busca archivo de icono en múltiples ubicaciones posibles
        # Esto es crucial para compatibilidad entre desarrollo y .exe
        
        # Lista de ubicaciones a probar en orden de prioridad
        search_paths = [
            os.path.join(IconManager._get_buttons_path(), filename),
            os.path.join(IconManager._get_tabs_path(), filename),
            os.path.join(IconManager._get_assets_path(), filename),
            os.path.join("assets", "buttons", filename),  # Rutas relativas
            os.path.join("assets", "tabs", filename),
            os.path.join("assets", filename),
            filename  # Último recurso: ruta directa
        ]
        
        # Intento cada ubicación hasta encontrar el archivo
        for file_path in search_paths:
            if os.path.exists(file_path):
                return file_path
        
        # No se encontró el archivo
        return None
    
    @staticmethod
    def get_button_icon(icon_name):
        # Obtengo icono para botón con búsqueda inteligente de archivos
        if icon_name not in IconManager.ICON_MAP:
            return QIcon()
        
        filename = IconManager.ICON_MAP[icon_name]
        file_path = IconManager._find_icon_file(filename)
        
        if not file_path:
            return QIcon()  # Archivo no encontrado en ninguna ubicación
        
        try:
            icon = QIcon(file_path)
            
            if icon.isNull():
                return QIcon()  # Archivo existe pero no es icono válido
            
            # Determino tamaño según tipo de botón
            if icon_name in ["geo", "whois", "ping", "dns", "ssl", "headers", "portscan", "reverse"]:
                size = IconManager.get_scaled_size(IconManager.BUTTON_SIZE)
            elif icon_name in ["quick", "export", "clear"]:
                size = IconManager.get_scaled_size(IconManager.BUTTON_SIZE)
            else:
                size = IconManager.get_scaled_size(IconManager.SMALL_BUTTON_SIZE)
            
            pixmap = icon.pixmap(size)
            if pixmap.isNull():
                return QIcon()  # Error al generar pixmap
            
            return QIcon(pixmap)
            
        except:
            return QIcon()  # Cualquier error -> icono vacío
    
    @staticmethod
    def get_tab_icon(icon_name):
        # Obtengo icono para pestaña
        if icon_name not in IconManager.ICON_MAP:
            return QIcon()
        
        filename = IconManager.ICON_MAP[icon_name]
        file_path = IconManager._find_icon_file(filename)
        
        if not file_path:
            return QIcon()
        
        try:
            icon = QIcon(file_path)
            
            if icon.isNull():
                return QIcon()
            
            # Pestañas siempre usan tamaño TAB_SIZE
            size = IconManager.get_scaled_size(IconManager.TAB_SIZE)
            pixmap = icon.pixmap(size)
            
            if pixmap.isNull():
                return QIcon()
            
            return QIcon(pixmap)
            
        except:
            return QIcon()
    
    @staticmethod
    def set_scale_factor(factor):
        # Cambio factor de escala global
        IconManager.SCALE_FACTOR = factor
    
    @staticmethod
    def setup_button_icon(button, icon_name):
        # Configuro icono en un botón específico
        try:
            icon = IconManager.get_button_icon(icon_name)
            if not icon.isNull():
                button.setIcon(icon)
                
                # Configuro tamaño del icono en el botón
                if icon_name in ["geo", "whois", "ping", "dns", "ssl", "headers", "portscan", "reverse"]:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.BUTTON_SIZE))
                elif icon_name in ["quick", "export", "clear"]:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.BUTTON_SIZE))
                else:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.SMALL_BUTTON_SIZE))
        except:
            pass  # Error silencioso
    
    @staticmethod
    def setup_tab_icon(tab_widget, tab_index, icon_name):
        # Configuro icono en una pestaña específica
        try:
            icon = IconManager.get_tab_icon(icon_name)
            if not icon.isNull():
                tab_widget.setTabIcon(tab_index, icon)
        except:
            pass
    
    @staticmethod
    def setup_all_button_icons(window):
        # Configuro todos los iconos de botones de la ventana
        try:
            IconManager.setup_button_icon(window.ui.btn_geo, "geo")
            IconManager.setup_button_icon(window.ui.btn_whois, "whois")
            IconManager.setup_button_icon(window.ui.btn_ping, "ping")
            IconManager.setup_button_icon(window.ui.btn_dns, "dns")
            IconManager.setup_button_icon(window.ui.btn_ssl, "ssl")
            IconManager.setup_button_icon(window.ui.btn_headers, "headers")
            IconManager.setup_button_icon(window.ui.btn_portscan, "portscan")
            IconManager.setup_button_icon(window.ui.btn_reverse, "reverse")
            
            IconManager.setup_button_icon(window.ui.btn_quick, "quick")
            IconManager.setup_button_icon(window.ui.btn_export, "export")
            IconManager.setup_button_icon(window.ui.btn_clear, "clear")
            
            IconManager.setup_button_icon(window.ui.btn_history, "history")
            IconManager.setup_button_icon(window.ui.btn_copy, "copy")
            IconManager.setup_button_icon(window.ui.btn_clear_results, "clear_results")
            
        except:
            pass
    
    @staticmethod
    def setup_all_tab_icons(window):
        # Configuro todos los iconos de pestañas
        try:
            tab_icons = [
                "tab_geo", "tab_whois", "tab_ping", "tab_dns",
                "tab_ssl", "tab_headers", "tab_portscan", "tab_reverse", "tab_summary"
            ]
            
            for i, icon_name in enumerate(tab_icons):
                IconManager.setup_tab_icon(window.ui.tabWidget, i, icon_name)
                
        except:
            pass
    
    @staticmethod
    def get_app_icon():
        # Obtengo el icono principal de la aplicación
        try:
            file_path = IconManager._find_icon_file("icon_app.ico")
            if file_path:
                icon = QIcon(file_path)
                if not icon.isNull():
                    return icon
        except:
            pass
        
        # Fallback: icono vacío
        return QIcon()