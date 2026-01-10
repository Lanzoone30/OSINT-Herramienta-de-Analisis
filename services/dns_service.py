import socket
from datetime import datetime

# En esta clase manejo consultas DNS básicas y avanzadas
# La idea aquí es proporcionar información de DNS de forma clara y útil
class DnsService:
    
    @staticmethod
    def analyze(target, language="es"):
        # Analizo un objetivo realizando consultas DNS
        try:
            # Limpio la URL manteniendo solo el hostname
            # Decidí no eliminar subdominios como 'www' para preservar la consulta original
            host = target.replace("https://", "").replace("http://", "")
            
            # Estructura básica del reporte
            result = f"DNS LOOKUP - {host}\n"
            result += "=" * 60 + "\n\n"
            
            # Sección de resolución básica (siempre disponible)
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
                    except:
                        result += f"  {ip}\n"
            except socket.gaierror:
                if language == "es":
                    result += "No se encontraron registros A\n"
                else:
                    result += "No A records found\n"
            
            # Esta sección la separo porque depende de dnspython,
            # una librería opcional para consultas avanzadas
            result += DnsService._try_advanced_lookup(host, language)
            
            # Notas al final para guiar al usuario
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
            
            # Pie de reporte con timestamp
            result += "\n" + "=" * 60 + "\n"
            result += f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            # Trunco errores largos para mantener el reporte legible
            error_msg = f"DNS LOOKUP ERROR: {str(e)}" if language == "en" else f"ERROR EN DNS LOOKUP: {str(e)}"
            return f"{error_msg[:200]}\nConsulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def _try_advanced_lookup(host, language):
        # Intento búsquedas DNS avanzadas si dnspython está instalado
        result = ""
        
        try:
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
            except:
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
            except:
                pass
            
            # Para NS: muestro los servidores de nombres del dominio
            try:
                ns_records = resolver.resolve(host, 'NS')
                if language == "es":
                    result += "\nREGISTROS NS (NAMESERVER):\n"
                else:
                    result += "\nNS RECORDS (NAMESERVER):\n"
                
                for ns in ns_records:
                    result += f"  {ns}\n"
            except:
                pass
                
        except ImportError:
            # Este catch es intencional: no quiero que falle todo el servicio
            # si falta la dependencia opcional
            if language == "es":
                result += "\n[dnspython no instalado para registros avanzados]\n"
            else:
                result += "\n[dnspython not installed for advanced records]\n"
        
        return result