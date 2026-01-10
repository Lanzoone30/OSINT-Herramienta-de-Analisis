import socket
from datetime import datetime

# En esta clase manejo consultas reverse DNS básicas
# La idea aquí es proporcionar información PTR sin requerir APIs externas
class ReverseService:
    
    @staticmethod
    def analyze(target, language="es"):
        # Realizo análisis reverse DNS
        try:
            # Acepto tanto dominios como IPs directamente
            # Esto da flexibilidad al usuario en la entrada
            try:
                ip = socket.gethostbyname(target)
            except:
                ip = target  # Si falla la resolución, asumo que ya es una IP
            
            result = f"REVERSE DNS ANALYSIS - {target}\n"
            result += "=" * 60 + "\n\n"
            
            if language == "es":
                result += "INFORMACIÓN DE RESOLUCIÓN\n"
            else:
                result += "RESOLUTION INFORMATION\n"
            result += "-" * 25 + "\n"
            
            if language == "es":
                result += f"Dominio/Objetivo: {target}\n"
                result += f"Dirección IP    : {ip}\n"
            else:
                result += f"Domain/Target   : {target}\n"
                result += f"IP Address      : {ip}\n"
            
            # Para reverse DNS uso socket.gethostbyaddr (registros PTR nativos)
            try:
                hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
                if language == "es":
                    result += "\nINFORMACIÓN REVERSE DNS\n"
                else:
                    result += "\nREVERSE DNS INFORMATION\n"
                result += "-" * 25 + "\n"
                
                if language == "es":
                    result += f"Nombre de host : {hostname}\n"
                else:
                    result += f"Hostname       : {hostname}\n"
                
                # Limito los alias a 5 para evitar reportes demasiado largos
                if aliaslist:
                    aliases = ', '.join(aliaslist[:5])
                    if language == "es":
                        result += f"Aliases        : {aliases}\n"
                    else:
                        result += f"Aliases        : {aliases}\n"
            except socket.herror:
                # Error específico cuando no hay registros PTR
                if language == "es":
                    result += "\nINFORMACIÓN REVERSE DNS\n"
                    result += "-" * 25 + "\n"
                    result += f"No se encontró reverse DNS para {ip}\n"
                else:
                    result += "\nREVERSE DNS INFORMATION\n"
                    result += "-" * 25 + "\n"
                    result += f"No reverse DNS found for {ip}\n"
            
            # Notas sobre limitaciones del servicio
            if language == "es":
                result += "\nNOTAS Y LIMITACIONES\n"
                result += "-" * 25 + "\n"
                result += "• Consulta básica de reverse DNS\n"
                result += "• Para reverse IP completo se necesitan APIs especializadas\n"
                result += "• Algunos proveedores limitan consultas reverse\n"
            else:
                result += "\nNOTES AND LIMITATIONS\n"
                result += "-" * 25 + "\n"
                result += "• Basic reverse DNS query\n"
                result += "• Full reverse IP requires specialized APIs\n"
                result += "• Some providers limit reverse queries\n"
            
            # Pie de reporte consistente
            result += "\n" + "=" * 60 + "\n"
            result += f"Consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            # Manejo de errores general
            error_msg = f"REVERSE DNS ERROR: {str(e)}" if language == "en" else f"ERROR EN REVERSE DNS: {str(e)}"
            return f"{error_msg[:200]}\nConsulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"