"""i18n.py - Traducciones de la interfaz (espanol e ingles).

Mantiene soporte para multiples idiomas sin requerir bibliotecas externas.
Todas las cadenas de la UI viven aqui. Los dialogos, placeholders y
mensajes de estado tienen su propia seccion para facilitar mantenimiento.
"""

from typing import Any


def _get(path: str, data: dict) -> Any:
    """Resolver una clave dotted sobre un dict anidado.

    Args:
        path: Ruta separada por puntos (ej. "ui.title").
        data: Diccionario con los textos.

    Returns:
        El valor encontrado o la misma ruta si no existe (fallback visible).
    """
    node = data
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return path
    return node


class Translations:
    """Diccionarios de traduccion y acceso por clave."""

    _SPANISH = {
        "ui": {
            "title": "OSINT - Herramienta de Análisis",
            "window_title": "OSINT - Herramienta de Análisis de Redes",
            "legal": "Esta herramienta es solo para fines educativos y auditorías autorizadas. Cumpla con todas las leyes y regulaciones locales.",
            "instructions": "Ingrese objetivo para análisis",
            "placeholder": "ejemplo.com | 8.8.8.8 | https://sitio.com",
            "risk": "Estado análisis:",
            "ready": "Listo",
            "risk_active": "Ejecutando {tab}",
            "risk_complete": "Análisis completo",
            "status_ready": "Listo",
            "status_running": "Ejecutando...",
            "status_warning": "Advertencia",
            "status_error": "Error",
            "status_success": "Completado",
            "results": "Resultados",
            "credits": "OSINT Herramienta de Análisis • Desarrollado con fines académicos y librerías de código abierto",
        },
        "buttons": {
            "geo": "Geolocalización",
            "whois": "WHOIS",
            "ping": "Ping/Traceroute",
            "dns": "DNS Lookup",
            "ssl": "SSL/TLS",
            "headers": "Headers HTTP",
            "portscan": "Port Scan",
            "reverse": "Reverse IP",
            "quick": "Análisis Completo",
            "export": "Exportar",
            "clear": "Limpiar lista",
            "history": "Historial",
            "copy": "Copiar",
            "clear_results": "Limpiar",
        },
        "tooltips": {
            "history": "Ver historial de análisis",
            "export": "Exportar resultados (CSV, TXT, JSON)",
            "clear": "Limpiar lista de objetivos",
            "copy": "Copiar resultados al portapapeles",
            "clear_results": "Limpiar todos los resultados",
            "geo": "Geolocalizar el objetivo (resuelve IP y obtiene país, ciudad, ISP)",
            "whois": "Consultar datos WHOIS del dominio (registrar, fechas, nameservers)",
            "ping": "Ping y traceroute al objetivo (latencia y ruta de red)",
            "dns": "Resolver registros DNS (A, AAAA, MX, NS, TXT, CNAME, SOA)",
            "ssl": "Inspeccionar el certificado SSL/TLS (emisor, validez, protocolo)",
            "headers": "Obtener los headers HTTP del sitio web del objetivo",
            "portscan": "Escanear puertos comunes abiertos en el objetivo",
            "reverse": "Buscar hosts que comparten la misma IP (reverse DNS / IP neighbors)",
            "quick": "Ejecutar los 8 análisis en secuencia sobre el objetivo actual",
        },
        "tabs": [
            "Geoloc.",
            "WHOIS",
            "Ping",
            "DNS",
            "SSL/TLS",
            "Headers",
            "Port Scan",
            "Reverse IP",
            "Resumen",
        ],
        "placeholders": [
            "Los resultados de geolocalización aparecerán aquí...",
            "Los resultados WHOIS aparecerán aquí...",
            "Los resultados de ping/traceroute aparecerán aquí...",
            "Los resultados DNS aparecerán aquí...",
            "Los resultados SSL/TLS aparecerán aquí...",
            "Los resultados de headers HTTP aparecerán aquí...",
            "Los resultados de port scan aparecerán aquí...",
            "Los resultados de reverse IP aparecerán aquí...",
            "Resumen consolidado aparecerá aquí después del análisis completo.",
        ],
        "dialogs": {
            "empty_title": "Campo vacío",
            "empty_message": "Por favor ingrese un dominio o IP para analizar.",
            "error_title": "Error en análisis",
            "error_message": "Ocurrió un error:\n\n{message}",
            "history_empty_title": "Historial",
            "history_empty_message": "No hay análisis en el historial.",
            "clear_all_title": "Limpiar todo",
            "clear_all_message": "¿Está seguro que desea limpiar todos los resultados?",
            "no_data_title": "Sin datos",
            "no_data_message": "No hay resultados para exportar.",
            "progress_title": "Ejecutando análisis completo...",
            "progress_cancel": "Cancelar",
            "progress_label": "Analizando {analysis}...",
            "input_format_title": "Formato de exportación",
            "input_format_label": "Seleccione el formato:",
            "input_format_csv": "CSV",
            "input_format_json": "JSON",
            "input_format_txt": "TXT",
            "export_error_title": "Error al exportar",
            "export_error_message": "No se pudo exportar: {message}",
            "export_success_title": "Exportación exitosa",
            "export_success_message": "Resultados exportados a:\n{path}",
            "copy_title": "Copiar resultados",
            "copy_label": "Texto copiado al portapapeles.",
            "copy_success": "Resultados copiados",
            "clear_success": "Resultados limpiados",
            "all_cleared": "Todo limpiado",
        },
        "status": {
            "starting": "Iniciando {analysis}...",
            "running": "Ejecutando {analysis} ({percent}%)",
            "complete": "Análisis completo finalizado",
            "error": "Error: {message}",
        },
        "history_types": {
            "complete": "análisis_completo",
        },
        "section_labels": {
            "geo": "Geolocalización",
            "headers": "Headers HTTP",
        },
        "feedback": {
            "history_target_empty": "Sin objetivo",
        },
    }

    _ENGLISH = {
        "ui": {
            "title": "OSINT - Analysis Tool",
            "window_title": "OSINT - Network Analysis Tool",
            "legal": "This tool is for educational purposes and authorized audits only. Comply with all local laws and regulations.",
            "instructions": "Enter target for analysis",
            "placeholder": "example.com | 8.8.8.8 | https://site.com",
            "risk": "Analysis status:",
            "ready": "Ready",
            "risk_active": "Running {tab}",
            "risk_complete": "Complete analysis",
            "status_ready": "Ready",
            "status_running": "Running...",
            "status_warning": "Warning",
            "status_error": "Error",
            "status_success": "Done",
            "results": "Results",
            "credits": "OSINT Analysis Tool. Developed for academic purposes with open source libraries",
        },
        "buttons": {
            "geo": "Geolocation",
            "whois": "WHOIS",
            "ping": "Ping/Traceroute",
            "dns": "DNS Lookup",
            "ssl": "SSL/TLS",
            "headers": "HTTP Headers",
            "portscan": "Port Scan",
            "reverse": "Reverse IP",
            "quick": "Complete Analysis",
            "export": "Export",
            "clear": "Clear list",
            "history": "History",
            "copy": "Copy",
            "clear_results": "Clear",
        },
        "tooltips": {
            "history": "View analysis history",
            "export": "Export results (CSV, TXT, JSON)",
            "clear": "Clear target list",
            "copy": "Copy results to clipboard",
            "clear_results": "Clear all results",
            "geo": "Geolocate the target (resolve IP and get country, city, ISP)",
            "whois": "Query WHOIS data for the domain (registrar, dates, nameservers)",
            "ping": "Ping and traceroute to the target (latency and network path)",
            "dns": "Resolve DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA)",
            "ssl": "Inspect the SSL/TLS certificate (issuer, validity, protocol)",
            "headers": "Fetch HTTP headers from the target's website",
            "portscan": "Scan common open ports on the target",
            "reverse": "Find hosts sharing the same IP (reverse DNS / IP neighbors)",
            "quick": "Run all 8 analyses in sequence on the current target",
        },
        "tabs": [
            "Geoloc.",
            "WHOIS",
            "Ping",
            "DNS",
            "SSL/TLS",
            "Headers",
            "Port Scan",
            "Reverse IP",
            "Summary",
        ],
        "placeholders": [
            "Geolocation results will appear here...",
            "WHOIS results will appear here...",
            "Ping/traceroute results will appear here...",
            "DNS results will appear here...",
            "SSL/TLS results will appear here...",
            "HTTP headers results will appear here...",
            "Port scan results will appear here...",
            "Reverse IP results will appear here...",
            "Consolidated summary will appear here after the complete analysis.",
        ],
        "dialogs": {
            "empty_title": "Empty field",
            "empty_message": "Please enter a domain or IP to analyze.",
            "error_title": "Analysis Error",
            "error_message": "An error occurred:\n\n{message}",
            "history_empty_title": "History",
            "history_empty_message": "No analysis in history.",
            "clear_all_title": "Clear All",
            "clear_all_message": "Are you sure you want to clear all results?",
            "no_data_title": "No data",
            "no_data_message": "No results to export.",
            "progress_title": "Running complete analysis...",
            "progress_cancel": "Cancel",
            "progress_label": "Analyzing {analysis}...",
            "input_format_title": "Export format",
            "input_format_label": "Select the format:",
            "input_format_csv": "CSV",
            "input_format_json": "JSON",
            "input_format_txt": "TXT",
            "export_error_title": "Export Error",
            "export_error_message": "Could not export: {message}",
            "export_success_title": "Export Successful",
            "export_success_message": "Results exported to:\n{path}",
            "copy_title": "Copy results",
            "copy_label": "Text copied to clipboard.",
            "copy_success": "Results copied",
            "clear_success": "Results cleared",
            "all_cleared": "All cleared",
        },
        "status": {
            "starting": "Starting {analysis}...",
            "running": "Running {analysis} ({percent}%)",
            "complete": "Complete analysis finished",
            "error": "Error: {message}",
        },
        "history_types": {
            "complete": "complete_analysis",
        },
        "section_labels": {
            "geo": "Geolocation",
            "headers": "HTTP Headers",
        },
        "feedback": {
            "history_target_empty": "No target",
        },
    }

    @staticmethod
    def get(language: str) -> dict:
        """Obtener el diccionario de traducciones para un idioma.

        Args:
            language: Codigo de idioma ("es" o "en").

        Returns:
            Diccionario completo con todas las claves de traduccion.
        """
        if language == "en":
            return Translations._ENGLISH
        return Translations._SPANISH

    @staticmethod
    def resolve(key: str, language: str, **kwargs: Any) -> str:
        """Resolver una clave de traduccion con formato opcional.

        Args:
            key: Ruta de la clave (ej. "ui.title").
            language: Codigo de idioma ("es" o "en").
            **kwargs: Variables para .format() en la cadena.

        Returns:
            Cadena traducida, o la misma clave si no se encuentra.
        """
        data = Translations.get(language)
        value = _get(key, data)
        if not isinstance(value, str):
            return str(value)
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError):
                return value
        return value


__all__ = ["Translations"]