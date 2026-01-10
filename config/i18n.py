# En esta clase manejo las traducciones de la interfaz, con la idea de que me facilite 
# mantener el soporte para múltiples idiomas sin requerir usar bibliotecas externas.

class Translations:
    
    @staticmethod
    def get_spanish():
        # Retorno todas las cadenas en español organizadas jerárquicamente
        # La estructura agrupa por funcionalidad para facilitar mantenimiento
        return {
            "ui": {
                # Nota: Mantengo el título genérico para que sea claro el propósito de la app
                "title": "OSINT - Herramienta de Análisis",
                "legal": "Esta herramienta es solo para fines educativos y auditorías autorizadas. Cumpla con todas las leyes y regulaciones locales.",
                "instructions": "Ingrese objetivo para análisis",
                # ejemplos comunes para guiar al usuario sobre el formato aceptado
                "placeholder": "ejemplo.com | 8.8.8.8 | https://sitio.com",
                "risk": "Estado análisis:",
                "risk_inactive": "• Inactivo"
            },
            # Agrupo los textos de botones en una sección aparte para facilitar mantenimiento
            "buttons": {
                "geo": "Geolocalización",
                "whois": "WHOIS",
                "ping": "Ping/Traceroute",
                "dns": "DNS Lookup",
                "ssl": "SSL/TLS",
                "headers": "Headers HTTP",
                "portscan": "Port Scan",
                "reverse": "Reverse IP",
                "quick": "Análisis Completo",  # Opción que ejecuta múltiples análisis de una vez
                "export": "Exportar",
                "clear": "Limpiar lista"
            },
            # Aquí gestiono los tooltips que aparecen al pasar el cursor sobre elementos UI
            "tooltips": {
                "history": "Ver historial de análisis",
                "export": "Exportar resultados (CSV, TXT, JSON)",  # Muestro los formatos disponibles
                "clear": "Limpiar lista de objetivos",
                "copy": "Copiar resultados al portapapeles",
                "clear_results": "Limpiar todos los resultados"
            },
            # La lista de pestañas debe coincidir exactamente con el orden de las funcionalidades
            "tabs": [
                "Geoloc.",      # Abreviado por espacio en la interfaz
                "WHOIS",
                "Ping",
                "DNS",
                "SSL/TLS",
                "Headers",
                "Port Scan",
                "Reverse IP",
                "Resumen"       # Pestaña final con consolidación de resultados
            ],
            "results": "Resultados",
            # Esta línea de créditos aparece en el pie de la aplicación
            "credits": "OSINT Herramienta de Análisis • Desarrollado con fines académicos y librerías de código abierto"
        }
    
    @staticmethod
    def get_english():
        # Versión en inglés siguiendo la misma estructura que la española
        # Mantengo la misma jerarquía de claves para facilitar el cambio entre idiomas
        return {
            "ui": {
                "title": "OSINT - Analysis Tool",
                "legal": "This tool is for educational purposes and authorized audits only. Comply with all local laws and regulations.",
                "instructions": "Enter target for analysis",
                "placeholder": "example.com | 8.8.8.8 | https://site.com",
                "risk": "Analysis status:",
                "risk_inactive": "• Inactive"
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
                "clear": "Clear List"
            },
            "tooltips": {
                "history": "View analysis history",
                "export": "Export results (CSV, TXT, JSON)",
                "clear": "Clear targets list",
                "copy": "Copy results to clipboard",
                "clear_results": "Clear all results"
            },
            # Nota: Las abreviaturas pueden variar entre idiomas según el espacio disponible en UI
            "tabs": [
                "Geoloc.",
                "WHOIS",
                "Ping",
                "DNS",
                "SSL/TLS",
                "Headers",
                "Port Scan",
                "Reverse IP",
                "Summary"
            ],
            "results": "Results",
            "credits": "OSINT Analysis Tool • Developed for academic purposes and open source libraries"
        }