"""geo_service.py - Geolocalización de direcciones IP vía ip-api.com."""
from datetime import datetime

import requests

from osint.services.base import http_get, resolve_ip, report_footer

class GeoService:

    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        # Analizo la geolocalización de un host o dirección IP
        try:
            # Intento resolver hostname a IP automáticamente
            # Si falla, asumo que el target ya es una dirección IP
            ip = resolve_ip(target)

            # Cabecera del reporte - sigo el mismo formato que otros servicios
            result = f"GEOLOCATION ANALYSIS - {target}\n"
            result += "=" * 60 + "\n\n"
            
            # Información de red básica
            if language == "es":
                result += "INFORMACIÓN DE RED\n"
            else:
                result += "NETWORK INFORMATION\n"
            result += "-" * 25 + "\n"
            
            if language == "es":
                result += f"Objetivo       : {target}\n"
                result += f"Dirección IP   : {ip}\n"
            else:
                result += f"Target         : {target}\n"
                result += f"IP Address     : {ip}\n"
            
            # Uso ip-api.com porque es gratuita y no requiere clave
            # El bitmask 66846719 pide todos los campos disponibles
            try:
                response = http_get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=10)
                data = response.json()
                
                if data.get("status") == "success":
                    result += GeoService._format_geo_data(data, language)
                else:
                    if language == "es":
                        result += "\nERROR: No se pudo obtener geolocalización\n"
                    else:
                        result += "\nERROR: Could not retrieve geolocation\n"
                        
            except requests.RequestException as e:
                # Trunco errores de API para mantener el reporte limpio
                if language == "es":
                    result += f"\nERROR API: {str(e)[:100]}\n"
                else:
                    result += f"\nAPI ERROR: {str(e)[:100]}\n"

            # Pie del reporte con timestamp
            result += report_footer()
            
            return result
            
        except Exception as e:
            # Manejo de errores general - mismo patrón que otros servicios
            error_msg = f"GEOLOCATION ERROR: {str(e)}" if language == "en" else f"ERROR EN GEOLOCALIZACIÓN: {str(e)}"
            return f"{error_msg[:200]}\nConsulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def _format_geo_data(data, language):
        # Formateo los datos de geolocalización en secciones organizadas
        result = ""
        
        if language == "es":
            # Sección geográfica primero - datos de ubicación física
            result += "\nINFORMACIÓN GEOGRÁFICA\n"
            result += "-" * 25 + "\n"
            result += f"País          : {data.get('country', 'N/A')}\n"
            result += f"Código país   : {data.get('countryCode', 'N/A')}\n"
            result += f"Región        : {data.get('regionName', 'N/A')}\n"
            result += f"Ciudad        : {data.get('city', 'N/A')}\n"
            result += f"Código postal : {data.get('zip', 'N/A')}\n"
            result += f"Coordenadas   : {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}\n"
            
            # Información del proveedor - útil para identificar tipo de IP
            result += "\nINFORMACIÓN DE PROVEEDOR\n"
            result += "-" * 25 + "\n"
            result += f"ISP           : {data.get('isp', 'N/A')}\n"
            result += f"Organización  : {data.get('org', 'N/A')}\n"
            result += f"ASN           : {data.get('as', 'N/A')}\n"
            
            # Flags adicionales para análisis de seguridad
            result += "\nINFORMACIÓN ADICIONAL\n"
            result += "-" * 25 + "\n"
            result += f"Zona horaria  : {data.get('timezone', 'N/A')}\n"
            result += f"Moneda        : {data.get('currency', 'N/A')}\n"
            result += f"Móvil         : {'SI' if data.get('mobile') else 'NO'}\n"
            result += f"Proxy         : {'SI' if data.get('proxy') else 'NO'}\n"
            result += f"Hospedaje     : {'SI' if data.get('hosting') else 'NO'}\n"
        else:
            # Versión en inglés - misma estructura
            result += "\nGEOGRAPHICAL INFORMATION\n"
            result += "-" * 25 + "\n"
            result += f"Country       : {data.get('country', 'N/A')}\n"
            result += f"Country Code  : {data.get('countryCode', 'N/A')}\n"
            result += f"Region        : {data.get('regionName', 'N/A')}\n"
            result += f"City          : {data.get('city', 'N/A')}\n"
            result += f"ZIP Code      : {data.get('zip', 'N/A')}\n"
            result += f"Coordinates   : {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}\n"
            
            result += "\nPROVIDER INFORMATION\n"
            result += "-" * 25 + "\n"
            result += f"ISP           : {data.get('isp', 'N/A')}\n"
            result += f"Organization  : {data.get('org', 'N/A')}\n"
            result += f"ASN           : {data.get('as', 'N/A')}\n"
            
            result += "\nADDITIONAL INFORMATION\n"
            result += "-" * 25 + "\n"
            result += f"Timezone      : {data.get('timezone', 'N/A')}\n"
            result += f"Currency      : {data.get('currency', 'N/A')}\n"
            result += f"Mobile        : {'YES' if data.get('mobile') else 'NO'}\n"
            result += f"Proxy         : {'YES' if data.get('proxy') else 'NO'}\n"
            result += f"Hosting       : {'YES' if data.get('hosting') else 'NO'}\n"
        
        return result