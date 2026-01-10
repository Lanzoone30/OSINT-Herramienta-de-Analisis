import os
import sys
import warnings
from datetime import datetime

# Suprimo warnings para mantener la consola limpia
warnings.filterwarnings("ignore")

# En esta clase manejo consultas WHOIS de dominios
# La idea aquí es usar python-whois pero con manejo robusto de errores
class WhoisService:
    
    @staticmethod
    def analyze(target, language="es"):
        # Realizo consulta WHOIS usando python-whois
        try:
            # Limpio el dominio: quito protocolos, www, y espacios
            domain = target.lower().strip()
            domain = domain.replace("https://", "").replace("http://", "")
            if domain.startswith("www."):
                domain = domain[4:]  # Quito www porque no es parte del dominio registrado
            
            # El módulo whois es opcional, así que lo importo dinámicamente
            try:
                import whois
            except ImportError:
                return WhoisService._format_error(domain, "python-whois no está instalado", language)
            
            # La consulta WHOIS puede fallar por muchas razones
            try:
                data = whois.whois(domain)
                
                # Verifico si obtuve datos reales o un objeto vacío
                if not data or (not data.domain_name and not data.registrar):
                    return WhoisService._format_no_data(domain, language)
                
                if language == "es":
                    return WhoisService._format_spanish(domain, data)
                else:
                    return WhoisService._format_english(domain, data)
                    
            except Exception as e:
                error_msg = str(e)
                # Error común cuando falta el archivo de TLDs públicos
                if "public_suffix_list.dat" in error_msg:
                    return WhoisService._handle_missing_file(domain, language)
                else:
                    return WhoisService._format_error(domain, error_msg, language)
                    
        except Exception as e:
            # Error general fuera del flujo normal
            return WhoisService._format_error(target, str(e), language)
    
    @staticmethod
    def _handle_missing_file(domain, language="es"):
        # Manejo el error del archivo faltante public_suffix_list.dat
        try:
            if language == "es":
                result = f"CONSULTA WHOIS: {domain}\n"
                result += "=" * 50 + "\n\n"
                result += "Información básica obtenida (modo limitado):\n\n"
                result += f"Dominio: {domain}\n"
                result += f"TLD: {domain.split('.')[-1] if '.' in domain else 'N/A'}\n"
                result += "\nNota: El módulo whois requiere un archivo adicional\n"
                result += "que no está disponible en esta instalación.\n\n"
            else:
                result = f"WHOIS QUERY: {domain}\n"
                result += "=" * 50 + "\n\n"
                result += "Basic information retrieved (limited mode):\n\n"
                result += f"Domain: {domain}\n"
                result += f"TLD: {domain.split('.')[-1] if '.' in domain else 'N/A'}\n"
                result += "\nNote: The whois module requires an additional file\n"
                result += "that is not available in this installation.\n\n"
            
            # Agrego información alternativa usando métodos más básicos
            result += WhoisService._get_alternative_info(domain, language)
            return result
            
        except Exception as e:
            return WhoisService._format_error(domain, str(e), language)
    
    @staticmethod
    def _get_alternative_info(domain, language="es"):
        # Obtengo información alternativa usando DNS
        try:
            import socket
            
            info = ""
            if language == "es":
                info += "Información DNS alternativa:\n"
                info += "-" * 30 + "\n"
            else:
                info += "Alternative DNS information:\n"
                info += "-" * 30 + "\n"
            
            # Intento resolver el dominio para ver si existe
            try:
                ip_address = socket.gethostbyname(domain)
                if language == "es":
                    info += f"Dirección IP: {ip_address}\n"
                else:
                    info += f"IP Address: {ip_address}\n"
            except:
                if language == "es":
                    info += "Dirección IP: No se pudo resolver\n"
                else:
                    info += "IP Address: Could not resolve\n"
            
            # Verifico si responde en el puerto 80 (HTTP)
            try:
                socket.create_connection((domain, 80), timeout=3)
                if language == "es":
                    info += "Estado: Dominio activo (respuesta en puerto 80)\n"
                else:
                    info += "Status: Domain active (responds on port 80)\n"
            except:
                if language == "es":
                    info += "Estado: Sin respuesta en puerto 80\n"
                else:
                    info += "Status: No response on port 80\n"
            
            return info
            
        except Exception as e:
            if language == "es":
                return f"Error al obtener información alternativa: {str(e)}"
            else:
                return f"Error getting alternative info: {str(e)}"
    
    @staticmethod
    def _format_error(domain, error_msg, language="es"):
        # Formateo mensaje de error
        if language == "es":
            return f"ERROR EN CONSULTA WHOIS: {domain}\n" + \
                   "=" * 50 + "\n\n" + \
                   f"No se pudo obtener información WHOIS.\n\n" + \
                   f"Error técnico: {error_msg[:200]}\n\n" + \
                   "Posibles soluciones:\n" + \
                   "1. Verifica que el dominio exista\n" + \
                   "2. Intenta con otro dominio (ej: github.com)\n" + \
                   "3. El servidor WHOIS puede estar temporalmente no disponible\n\n" + \
                   f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"WHOIS QUERY ERROR: {domain}\n" + \
                   "=" * 50 + "\n\n" + \
                   f"Could not retrieve WHOIS information.\n\n" + \
                   f"Technical error: {error_msg[:200]}\n\n" + \
                   "Possible solutions:\n" + \
                   "1. Verify the domain exists\n" + \
                   "2. Try another domain (eg: github.com)\n" + \
                   "3. WHOIS server may be temporarily unavailable\n\n" + \
                   f"Query: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def _format_no_data(domain, language="es"):
        # Formateo cuando no hay datos disponibles
        if language == "es":
            return f"CONSULTA WHOIS: {domain}\n" + \
                   "=" * 50 + "\n\n" + \
                   "No se encontró información WHOIS pública para este dominio.\n\n" + \
                   "Posibles razones:\n" + \
                   "1. El dominio está protegido por privacidad WHOIS\n" + \
                   "2. El TLD no ofrece información pública\n" + \
                   "3. El servidor WHOIS no respondió\n\n" + \
                   f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return f"WHOIS QUERY: {domain}\n" + \
                   "=" * 50 + "\n\n" + \
                   "No public WHOIS information found for this domain.\n\n" + \
                   "Possible reasons:\n" + \
                   "1. Domain has WHOIS privacy protection\n" + \
                   "2. TLD doesn't provide public information\n" + \
                   "3. WHOIS server didn't respond\n\n" + \
                   f"Query: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def _format_spanish(target, data):
        # Formateo datos de python-whois en español
        def format_date(date):
            if not date:
                return 'N/A'
            if isinstance(date, list):
                return str(date[0]) if date else 'N/A'
            return str(date)
        
        def format_nameservers(ns):
            if not ns:
                return 'N/A'
            if isinstance(ns, list):
                return '\n  ' + '\n  '.join(ns[:5]) + ('\n  ...' if len(ns) > 5 else '')
            return str(ns)
        
        def format_emails(emails):
            if not emails:
                return 'N/A'
            if isinstance(emails, list):
                return ', '.join(emails[:3])
            return str(emails)
        
        result = f"WHOIS - {target}\n"
        result += "=" * 60 + "\n\n"
        
        # Información básica del registro
        result += "INFORMACIÓN DE REGISTRO\n"
        result += "-" * 25 + "\n"
        result += f"Dominio      : {data.domain_name if data.domain_name else 'N/A'}\n"
        result += f"Registrador  : {data.registrar if data.registrar else 'N/A'}\n"
        result += f"Servidor     : {data.whois_server if data.whois_server else 'N/A'}\n\n"
        
        # Fechas clave para análisis
        result += "FECHAS CLAVE\n"
        result += "-" * 25 + "\n"
        result += f"Creación     : {format_date(data.creation_date)}\n"
        result += f"Expiración   : {format_date(data.expiration_date)}\n"
        result += f"Actualizado  : {format_date(data.updated_date)}\n\n"
        
        # Información de contacto
        result += "INFORMACIÓN DE CONTACTO\n"
        result += "-" * 25 + "\n"
        result += f"Nombre       : {data.name if data.name else 'N/A'}\n"
        result += f"Organización : {data.org if data.org else 'N/A'}\n"
        result += f"Email(s)     : {format_emails(data.emails)}\n"
        result += f"País         : {data.country if data.country else 'N/A'}\n"
        result += f"Ciudad       : {data.city if data.city else 'N/A'}\n"
        result += f"Estado       : {data.state if data.state else 'N/A'}\n\n"
        
        # Información técnica
        result += "INFORMACIÓN TÉCNICA\n"
        result += "-" * 25 + "\n"
        result += f"Servidores DNS: {format_nameservers(data.name_servers)}\n"
        result += f"Estado        : {data.status if data.status else 'N/A'}\n"
        result += f"DNSSEC        : {data.dnssec if data.dnssec else 'N/A'}\n\n"
        
        result += "=" * 60 + "\n"
        result += f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return result
    
    @staticmethod
    def _format_english(target, data):
        # Formateo datos de python-whois en inglés
        def format_date(date):
            if not date:
                return 'N/A'
            if isinstance(date, list):
                return str(date[0]) if date else 'N/A'
            return str(date)
        
        def format_nameservers(ns):
            if not ns:
                return 'N/A'
            if isinstance(ns, list):
                return '\n  ' + '\n  '.join(ns[:5]) + ('\n  ...' if len(ns) > 5 else '')
            return str(ns)
        
        def format_emails(emails):
            if not emails:
                return 'N/A'
            if isinstance(emails, list):
                return ', '.join(emails[:3])
            return str(emails)
        
        result = f"WHOIS - {target}\n"
        result += "=" * 60 + "\n\n"
        
        # Basic information
        result += "REGISTRATION INFORMATION\n"
        result += "-" * 25 + "\n"
        result += f"Domain       : {data.domain_name if data.domain_name else 'N/A'}\n"
        result += f"Registrar    : {data.registrar if data.registrar else 'N/A'}\n"
        result += f"Server       : {data.whois_server if data.whois_server else 'N/A'}\n\n"
        
        # Dates
        result += "KEY DATES\n"
        result += "-" * 25 + "\n"
        result += f"Creation     : {format_date(data.creation_date)}\n"
        result += f"Expiration   : {format_date(data.expiration_date)}\n"
        result += f"Last Updated : {format_date(data.updated_date)}\n\n"
        
        # Contact information
        result += "CONTACT INFORMATION\n"
        result += "-" * 25 + "\n"
        result += f"Name         : {data.name if data.name else 'N/A'}\n"
        result += f"Organization : {data.org if data.org else 'N/A'}\n"
        result += f"Email(s)     : {format_emails(data.emails)}\n"
        result += f"Country      : {data.country if data.country else 'N/A'}\n"
        result += f"City         : {data.city if data.city else 'N/A'}\n"
        result += f"State        : {data.state if data.state else 'N/A'}\n\n"
        
        # Technical information
        result += "TECHNICAL INFORMATION\n"
        result += "-" * 25 + "\n"
        result += f"Name Servers : {format_nameservers(data.name_servers)}\n"
        result += f"Status       : {data.status if data.status else 'N/A'}\n"
        result += f"DNSSEC       : {data.dnssec if data.dnssec else 'N/A'}\n\n"
        
        result += "=" * 60 + "\n"
        result += f"Query: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return result