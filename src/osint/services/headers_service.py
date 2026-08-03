"""headers_service.py - Análisis de cabeceras HTTP."""
import requests

from osint.services.base import http_get, report_footer

class HeadersService:

    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        # Analizo las cabeceras HTTP de un sitio web
        try:
            # Agrego http:// automáticamente para facilitar al usuario
            if not target.startswith(("http://", "https://")):
                target = "http://" + target
            
            result = f"HTTP HEADERS ANALYSIS - {target}\n"
            result += "=" * 60 + "\n\n"
            
            try:
                # Habilito redirects para capturar la URL final
                # Esto es útil para detectar CDNs o servicios de proxy
                response = http_get(target, timeout=10, allow_redirects=True)
                final_url = response.url
                
                # Información básica de la conexión
                if language == "es":
                    result += "INFORMACIÓN DE CONEXIÓN\n"
                else:
                    result += "CONNECTION INFORMATION\n"
                result += "-" * 25 + "\n"
                
                if language == "es":
                    result += f"URL solicitada : {target}\n"
                    result += f"URL final      : {final_url}\n"
                    result += f"Estado HTTP    : {response.status_code} {response.reason}\n"
                    result += f"Tiempo respuesta: {response.elapsed.total_seconds():.3f}s\n"
                else:
                    result += f"Requested URL  : {target}\n"
                    result += f"Final URL      : {final_url}\n"
                    result += f"HTTP Status    : {response.status_code} {response.reason}\n"
                    result += f"Response time  : {response.elapsed.total_seconds():.3f}s\n"
                
                # Agrupo cabeceras por tipo para mejor análisis
                result += HeadersService._format_headers_by_type(response.headers, language)
                
                # Estadísticas útiles para benchmarking
                result += HeadersService._get_stats(response, language)
                
            except requests.exceptions.RequestException as e:
                # Trunco errores de red para mantener el reporte manejable
                if language == "es":
                    result += f"ERROR DE CONEXIÓN: {str(e)[:100]}\n"
                else:
                    result += f"CONNECTION ERROR: {str(e)[:100]}\n"
            
            # Timestamp para rastreo
            result += report_footer()
            
            return result
            
        except Exception as e:
            # Manejo de errores general
            error_msg = f"HEADERS ANALYSIS ERROR: {str(e)}" if language == "en" else f"ERROR EN ANÁLISIS HEADERS: {str(e)}"
            return f"{error_msg[:200]}{report_footer()}"
    
    @staticmethod
    def _format_headers_by_type(headers, language):
        # Agrupo las cabeceras por categorías funcionales
        # Estos grupos facilitan el análisis de seguridad
        header_groups = {
            'server': ['Server', 'X-Powered-By', 'X-AspNet-Version'],  # Tecnología del backend
            'security': ['Strict-Transport-Security', 'Content-Security-Policy', 
                        'X-Frame-Options', 'X-Content-Type-Options', 
                        'X-XSS-Protection', 'Referrer-Policy'],  # Seguridad web
            'cache': ['Cache-Control', 'Expires', 'Pragma', 'ETag'],  # Políticas de cache
            'content': ['Content-Type', 'Content-Length', 'Content-Encoding', 
                       'Content-Language', 'Content-Disposition'],  # Metadatos
            'cookies': ['Set-Cookie', 'Cookie'],  # Gestión de sesiones
            'misc': ['Date', 'Connection', 'Keep-Alive', 'Via', 'Location']  # Varios
        }
        
        result = ""
        if language == "es":
            result += "\nCABECERAS HTTP\n"
        else:
            result += "\nHTTP HEADERS\n"
        result += "-" * 25 + "\n"
        
        # Solo muestro grupos que tienen cabeceras presentes
        for group_name, header_list in header_groups.items():
            found_headers = []
            for header in header_list:
                if header in headers:
                    found_headers.append((header, headers[header]))
            
            if found_headers:
                if language == "es":
                    group_translations = {
                        'server': 'SERVIDOR',
                        'security': 'SEGURIDAD',
                        'cache': 'CACHE',
                        'content': 'CONTENIDO',
                        'cookies': 'COOKIES',
                        'misc': 'VARIAS'
                    }
                    result += f"\n{group_translations.get(group_name, group_name.upper())}:\n"
                else:
                    result += f"\n{group_name.upper()}:\n"
                
                # Limito valores largos para mejor legibilidad
                for header, value in found_headers:
                    value_display = value[:80] + "..." if len(value) > 80 else value
                    result += f"  {header:25} : {value_display}\n"
        
        return result
    
    @staticmethod
    def _get_stats(response, language):
        # Genero estadísticas útiles sobre la respuesta HTTP
        stats = ""
        if language == "es":
            stats += "\nESTADÍSTICAS\n"
            stats += "-" * 25 + "\n"
            stats += f"Total cabeceras : {len(response.headers)}\n"
            stats += f"Tamaño respuesta: {len(response.content):,} bytes\n"
            stats += f"Codificación    : {response.encoding}\n"
            stats += f"Cookies seteadas: {len(response.cookies)}\n"
            if hasattr(response, 'from_cache'):
                stats += f"Desde cache     : {'SI' if response.from_cache else 'NO'}\n"
        else:
            stats += "\nSTATISTICS\n"
            stats += "-" * 25 + "\n"
            stats += f"Total headers   : {len(response.headers)}\n"
            stats += f"Response size   : {len(response.content):,} bytes\n"
            stats += f"Encoding        : {response.encoding}\n"
            stats += f"Cookies set     : {len(response.cookies)}\n"
            if hasattr(response, 'from_cache'):
                stats += f"From cache      : {'YES' if response.from_cache else 'NO'}\n"
        
        return stats