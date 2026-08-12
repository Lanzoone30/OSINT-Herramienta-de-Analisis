"""ssl_service.py - Análisis de certificados y seguridad SSL/TLS."""
import socket
import ssl

import requests

from osint.services.base import report_footer

class SSLService:

    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        # Analizo la configuración SSL/TLS de un sitio web
        try:
            # Por defecto asumo HTTPS porque es un servicio de análisis SSL
            if not target.startswith(("http://", "https://")):
                target = "https://" + target
            # Extraigo solo el hostname para la verificación SSL
            hostname = target.replace("https://", "").replace("http://", "").split("/")[0]
            result = f"SSL/TLS ANALYSIS - {hostname}\n"
            result += "=" * 60 + "\n\n"
            try:
                # Uso verify=True para que requests valide automáticamente el certificado
                response = requests.get(target, timeout=10, verify=True, allow_redirects=True)
                final_url = response.url
                if language == "es":
                    result += "ESTADO DE CONEXIÓN\n"
                else:
                    result += "CONNECTION STATUS\n"
                result += "-" * 25 + "\n"
                # Verifico si la conexión final es HTTPS
                is_https = final_url.startswith('https')
                if language == "es":
                    result += f"Protocolo      : {'HTTPS (Seguro)' if is_https else 'HTTP (No seguro)'}\n"
                    result += f"Estado HTTP    : {response.status_code}\n"
                else:
                    result += f"Protocol       : {'HTTPS (Secure)' if is_https else 'HTTP (Not secure)'}\n"
                    result += f"HTTP Status    : {response.status_code}\n"
                # Información detallada del certificado
                cert_info = SSLService._get_certificate_info(hostname, language)
                result += cert_info
                # Cabeceras específicas de seguridad
                result += SSLService._get_security_headers(response, language)
                # Verificaciones automáticas de buenas prácticas
                result += SSLService._get_security_checks(response, language)
            except requests.exceptions.SSLError as e:
                # Error específico para problemas de certificado
                if language == "es":
                    result += f"ERROR SSL        : {str(e)[:100]}\n\n"
                    result += "El certificado SSL no es válido o está autofirmado.\n"
                else:
                    result += f"SSL ERROR        : {str(e)[:100]}\n\n"
                    result += "SSL certificate is invalid or self-signed.\n"
            except requests.RequestException as e:
                # Otros errores de conexión
                if language == "es":
                    result += f"ERROR DE CONEXIÓN: {str(e)[:100]}\n"
                else:
                    result += f"CONNECTION ERROR : {str(e)[:100]}\n"

            # Timestamp consistente con otros servicios
            result += report_footer()
            return result
        except Exception as e:
            # Error general
            error_msg = f"SSL ANALYSIS ERROR: {str(e)}" if language == "en" else f"ERROR EN ANÁLISIS SSL: {str(e)}"
            return f"{error_msg[:200]}{report_footer()}"
    @staticmethod
    def _get_certificate_info(hostname, language):
        # Obtengo información detallada del certificado SSL
        info = ""
        try:
            # Uso el contexto SSL por defecto del sistema
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    if language == "es":
                        info += "\nINFORMACIÓN DEL CERTIFICADO\n"
                    else:
                        info += "\nCERTIFICATE INFORMATION\n"
                    info += "-" * 25 + "\n"
                    # Fechas de validez
                    if 'notBefore' in cert:
                        if language == "es":
                            info += f"Válido desde   : {cert['notBefore']}\n"
                        else:
                            info += f"Valid from     : {cert['notBefore']}\n"
                    if 'notAfter' in cert:
                        if language == "es":
                            info += f"Válido hasta   : {cert['notAfter']}\n"
                        else:
                            info += f"Valid until    : {cert['notAfter']}\n"
                    # Sujeto (commonName)
                    if 'subject' in cert:
                        subject = dict(x[0] for x in cert['subject'])
                        if language == "es":
                            info += f"Sujeto         : {subject.get('commonName', 'N/A')}\n"
                        else:
                            info += f"Subject        : {subject.get('commonName', 'N/A')}\n"
                    # Emisor
                    if 'issuer' in cert:
                        issuer = dict(x[0] for x in cert['issuer'])
                        if language == "es":
                            info += f"Emisor         : {issuer.get('organizationName', 'N/A')}\n"
                        else:
                            info += f"Issuer         : {issuer.get('organizationName', 'N/A')}\n"
        except Exception:
            # Manejo silencioso de errores de conexión SSL
            if language == "es":
                info += "\nINFORMACIÓN DEL CERTIFICADO\n"
                info += "-" * 25 + "\n"
                info += "No se pudo obtener información del certificado\n"
            else:
                info += "\nCERTIFICATE INFORMATION\n"
                info += "-" * 25 + "\n"
                info += "Could not retrieve certificate information\n"
        return info
    @staticmethod
    def _get_security_headers(response, language):
        # Obtengo cabeceras de seguridad específicas
        info = ""
        security_headers = {
            'strict-transport-security': 'HSTS',
            'content-security-policy': 'CSP',
            'x-frame-options': 'Frame Options',
            'x-content-type-options': 'Content Type',
            'x-xss-protection': 'XSS Protection',
            'referrer-policy': 'Referrer Policy'
        }
        found_headers = []
        for header, short_name in security_headers.items():
            if header in response.headers:
                found_headers.append((short_name, response.headers[header]))
        if found_headers:
            if language == "es":
                info += "\nCABECERAS DE SEGURIDAD\n"
            else:
                info += "\nSECURITY HEADERS\n"
            info += "-" * 25 + "\n"
            # Acorto valores de CSP para mejor legibilidad
            for short_name, value in found_headers:
                value_display = value[:50] + "..." if len(value) > 50 else value
                info += f"{short_name:15} : {value_display}\n"
        return info
    @staticmethod
    def _get_security_checks(response, language):
        checks = ""
        if language == "es":
            checks += "\nVERIFICACIONES DE SEGURIDAD\n"
            checks += "-" * 25 + "\n"
        else:
            checks += "\nSECURITY CHECKS\n"
            checks += "-" * 25 + "\n"
        # HTTPS obligatorio
        is_https = response.url.startswith('https')
        if language == "es":
            checks += f"HTTPS          : {'SI' if is_https else 'NO'}\n"
        else:
            checks += f"HTTPS          : {'YES' if is_https else 'NO'}\n"
        # HSTS - previene ataques de downgrade
        has_hsts = 'strict-transport-security' in response.headers
        if language == "es":
            checks += f"HSTS           : {'SI' if has_hsts else 'NO'}\n"
        else:
            checks += f"HSTS           : {'YES' if has_hsts else 'NO'}\n"
        # Validación combinada de certificado y HTTPS
        has_valid_ssl = response.ok and is_https
        if language == "es":
            checks += f"Certificado SSL: {'VALIDAD' if has_valid_ssl else 'INVALIDO'}\n"
        else:
            checks += f"SSL Certificate: {'VALID' if has_valid_ssl else 'INVALID'}\n"
        return checks