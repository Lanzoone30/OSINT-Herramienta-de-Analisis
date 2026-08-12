"""config.py - Gestión de iconos con compatibilidad PyInstaller."""
import os
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class IconManager:

    @staticmethod
    def _get_base_path():
        # src/osint/config.py -> 3 niveles hasta la raíz del proyecto
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller extrae los archivos en un directorio temporal
            return sys._MEIPASS
        return str(Path(__file__).resolve().parents[2])
    
    @staticmethod
    def _get_buttons_path():
        return os.path.join(IconManager._get_base_path(), "assets", "buttons")
    
    @staticmethod
    def _get_tabs_path():
        return os.path.join(IconManager._get_base_path(), "assets", "tabs")
    
    @staticmethod
    def _get_assets_path():
        return os.path.join(IconManager._get_base_path(), "assets")
    
    BUTTON_SIZE = QSize(32, 32)
    TAB_SIZE = QSize(20, 20)
    SMALL_BUTTON_SIZE = QSize(24, 24)

    SCALE_FACTOR = 1.0

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
        if IconManager.SCALE_FACTOR == 1.0:
            return base_size
        return QSize(
            int(base_size.width() * IconManager.SCALE_FACTOR),
            int(base_size.height() * IconManager.SCALE_FACTOR)
        )
    
    @staticmethod
    def _find_icon_file(filename):
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
        
        for file_path in search_paths:
            if os.path.exists(file_path):
                return file_path

        return None
    
    @staticmethod
    def get_button_icon(icon_name):
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
            
        except Exception:
            return QIcon()  # Cualquier error -> icono vacío
    
    @staticmethod
    def get_tab_icon(icon_name):
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
            
            size = IconManager.get_scaled_size(IconManager.TAB_SIZE)
            pixmap = icon.pixmap(size)
            
            if pixmap.isNull():
                return QIcon()
            
            return QIcon(pixmap)
            
        except Exception:
            return QIcon()
    
    @staticmethod
    def set_scale_factor(factor):
        IconManager.SCALE_FACTOR = factor
    
    @staticmethod
    def setup_button_icon(button, icon_name):
        try:
            icon = IconManager.get_button_icon(icon_name)
            if not icon.isNull():
                button.setIcon(icon)
                
                if icon_name in ["geo", "whois", "ping", "dns", "ssl", "headers", "portscan", "reverse"]:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.BUTTON_SIZE))
                elif icon_name in ["quick", "export", "clear"]:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.BUTTON_SIZE))
                else:
                    button.setIconSize(IconManager.get_scaled_size(IconManager.SMALL_BUTTON_SIZE))
        except Exception:
            pass  # Error silencioso
    
    @staticmethod
    def setup_tab_icon(tab_widget, tab_index, icon_name):
        try:
            icon = IconManager.get_tab_icon(icon_name)
            if not icon.isNull():
                tab_widget.setTabIcon(tab_index, icon)
        except Exception:
            pass
    
    @staticmethod
    def setup_all_button_icons(window):
        try:
            IconManager.setup_button_icon(window.btn_geo, "geo")
            IconManager.setup_button_icon(window.btn_whois, "whois")
            IconManager.setup_button_icon(window.btn_ping, "ping")
            IconManager.setup_button_icon(window.btn_dns, "dns")
            IconManager.setup_button_icon(window.btn_ssl, "ssl")
            IconManager.setup_button_icon(window.btn_headers, "headers")
            IconManager.setup_button_icon(window.btn_portscan, "portscan")
            IconManager.setup_button_icon(window.btn_reverse, "reverse")
            
            IconManager.setup_button_icon(window.btn_quick, "quick")
            IconManager.setup_button_icon(window.btn_export, "export")
            IconManager.setup_button_icon(window.btn_clear, "clear")
            
            IconManager.setup_button_icon(window.btn_history, "history")
            IconManager.setup_button_icon(window.btn_copy, "copy")
            IconManager.setup_button_icon(window.btn_clear_results, "clear_results")
            
        except Exception:
            pass
    
    @staticmethod
    def setup_all_tab_icons(window):
        try:
            tab_icons = [
                "tab_geo", "tab_whois", "tab_ping", "tab_dns",
                "tab_ssl", "tab_headers", "tab_portscan", "tab_reverse", "tab_summary"
            ]
            
            for i, icon_name in enumerate(tab_icons):
                IconManager.setup_tab_icon(window.tabWidget, i, icon_name)
                
        except Exception:
            pass
    
    @staticmethod
    def get_app_icon():
        try:
            file_path = IconManager._find_icon_file("icon_app.ico")
            if file_path:
                icon = QIcon(file_path)
                if not icon.isNull():
                    return icon
        except Exception:
            pass
        
        # Fallback: icono vacío
        return QIcon()