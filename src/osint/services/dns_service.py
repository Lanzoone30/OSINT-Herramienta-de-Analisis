"""dns_service.py - Consultas DNS básicas y avanzadas."""
import socket
from datetime import datetime

class DnsService:
    
    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        try:
            # Decidí no eliminar subdominios como 'www' para preservar la consulta original
            host = target.replace("https://", "").replace("http://", "")

            result = f"DNS LOOKUP - {host}\n"
            result += "=" * 60 + "\n\n"

            if language == "es":
                result += "RESOLUCIÓN DNS BÁSICA\n"
            else:
                result += "BASIC DNS RESOLUTION\n"
            result += "-" * 25 + "\n"
            
            # En esta parte uso socket.gethostbyname_ex porque es
            # la única forma nativa en Python para obtener registros A
            try:
                a_records = socket.gethostbyname_ex(host)
                if language == "es":
                    result += "REGISTROS A (IPv4):\n"
                else:
                    result += "A RECORDS (IPv4):\n"
                
                # Aquí intento la resolución inversa: no todos los servidores
                # DNS responden a PTR, pero lo intento por completitud
                for ip in a_records[2]:
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                        result += f"  {ip:15} -> {hostname}\n"
                    except OSError:
                        result += f"  {ip}\n"
            except socket.gaierror:
                if language == "es":
                    result += "No se encontraron registros A\n"
                else:
                    result += "No A records found\n"
            
            # Esta sección la separo porque depende de dnspython,
            # una librería opcional para consultas avanzadas
            result += DnsService._try_advanced_lookup(host, language)
            
            if language == "es":
                result += "\nNOTAS\n"
                result += "-" * 25 + "\n"
                result += "• Consulta DNS básica\n"
                result += "• Instale dnspython para registros MX, TXT, NS\n"
            else:
                result += "\nNOTES\n"
                result += "-" * 25 + "\n"
                result += "• Basic DNS query\n"
                result += "• Install dnspython for MX, TXT, NS records\n"
            
            result += "\n" + "=" * 60 + "\n"
            result += f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            # Trunco errores largos para mantener el reporte legible
            error_msg = f"DNS LOOKUP ERROR: {str(e)}" if language == "en" else f"ERROR EN DNS LOOKUP: {str(e)}"
            return f"{error_msg[:200]}\nConsulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def _try_advanced_lookup(host, language):
        result = ""
        
        try:
            import dns.exception
            import dns.resolver
            
            # Configuro timeouts agresivos para no bloquear la aplicación
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # Para MX: ordeno por preferencia para mostrar el servidor principal primero
            try:
                mx_records = resolver.resolve(host, 'MX')
                if language == "es":
                    result += "\nREGISTROS MX (MAIL):\n"
                else:
                    result += "\nMX RECORDS (MAIL):\n"
                
                for mx in sorted(mx_records, key=lambda x: x.preference):
                    result += f"  Pri {mx.preference:3} -> {mx.exchange}\n"
            except dns.exception.DNSException:
                pass  # No todos los dominios tienen registros MX
            
            # Para TXT: acorto strings largos para mantener formato
            try:
                txt_records = resolver.resolve(host, 'TXT')
                if language == "es":
                    result += "\nREGISTROS TXT:\n"
                else:
                    result += "\nTXT RECORDS:\n"
                
                for txt in txt_records:
                    txt_str = str(txt).replace('"', '')
                    if len(txt_str) > 80:
                        txt_str = txt_str[:77] + "..."
                    result += f"  {txt_str}\n"
            except dns.exception.DNSException:
                pass
            
            try:
                ns_records = resolver.resolve(host, 'NS')
                if language == "es":
                    result += "\nREGISTROS NS (NAMESERVER):\n"
                else:
                    result += "\nNS RECORDS (NAMESERVER):\n"
                
                for ns in ns_records:
                    result += f"  {ns}\n"
            except dns.exception.DNSException:
                pass
                
        except ImportError:
            # Este catch es intencional: no quiero que falle todo el servicio
            # si falta la dependencia opcional
            if language == "es":
                result += "\n[dnspython no instalado para registros avanzados]\n"
            else:
                result += "\n[dnspython not installed for advanced records]\n"
        
        return result