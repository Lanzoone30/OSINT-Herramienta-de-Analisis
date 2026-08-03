"""port_service.py - Escaneo básico de puertos comunes."""
import socket
from datetime import datetime

class PortService:
    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        try:
            # Limpio el hostname para aceptar URLs o direcciones simples
            host = target.split(':')[0] if ':' in target else target
            host = host.replace("https://", "").replace("http://", "")
            result = f"PORT SCAN - {host}\n"
            result += "=" * 60 + "\n\n"
            if language == "es":
                result += "ESCANEO DE PUERTOS COMUNES\n"
            else:
                result += "COMMON PORTS SCAN\n"
            result += "-" * 25 + "\n"
            # Lista de puertos comunes: un balance entre cobertura y velocidad
            common_ports = [
                (21, "FTP"), (22, "SSH"), (23, "Telnet"), (25, "SMTP"),
                (53, "DNS"), (80, "HTTP"), (110, "POP3"), (143, "IMAP"),
                (443, "HTTPS"), (465, "SMTPS"), (587, "SMTP"),
                (993, "IMAPS"), (995, "POP3S"), (3306, "MySQL"),
                (3389, "RDP"), (8080, "HTTP-Proxy"), (8443, "HTTPS-Alt")
            ]
            open_ports = []
            # Timeout de 1 segundo para equilibrio entre detección y velocidad
            for port, service in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result_code = sock.connect_ex((host, port))
                    sock.close()
                    if result_code == 0:
                        status = "ABIERTO" if language == "es" else "OPEN"
                        open_ports.append((port, service, status))
                except OSError:
                    pass  # Puerto cerrado o inaccesible; continúo el escaneo
            # Reporte de resultados
            if open_ports:
                if language == "es":
                    result += "PUERTOS ABIERTOS ENCONTRADOS:\n"
                else:
                    result += "OPEN PORTS FOUND:\n"
                for port, service, status in open_ports:
                    result += f"  {port:5} ({service:15}) - {status}\n"
            else:
                if language == "es":
                    result += "No se encontraron puertos abiertos\n"
                else:
                    result += "No open ports found\n"
            # Estadísticas simples para contexto
            total_scanned = len(common_ports)
            total_open = len(open_ports)
            if language == "es":
                result += "\nESTADÍSTICAS DEL ESCANEO\n"
                result += "-" * 25 + "\n"
                result += f"Puertos escaneados : {total_scanned}\n"
                result += f"Puertos abiertos   : {total_open}\n"
                result += f"Porcentaje abierto : {(total_open/total_scanned)*100:.1f}%\n"
            else:
                result += "\nSCAN STATISTICS\n"
                result += "-" * 25 + "\n"
                result += f"Ports scanned      : {total_scanned}\n"
                result += f"Open ports found   : {total_open}\n"
                result += f"Open percentage    : {(total_open/total_scanned)*100:.1f}%\n"
            # Notas sobre limitaciones del escáner
            if language == "es":
                result += "\nNOTAS IMPORTANTES\n"
                result += "-" * 25 + "\n"
                result += "• Escaneo básico sin privilegios\n"
                result += "• Solo puertos comunes\n"
                result += "• Use herramientas especializadas para escaneos completos\n"
            else:
                result += "\nIMPORTANT NOTES\n"
                result += "-" * 25 + "\n"
                result += "• Basic unprivileged scan\n"
                result += "• Common ports only\n"
                result += "• Use specialized tools for complete scans\n"
            result += "\n" + "=" * 60 + "\n"
            result += f"Escaneo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return result
        except Exception as e:
            # Manejo de errores general
            error_msg = f"PORT SCAN ERROR: {str(e)}" if language == "en" else f"ERROR EN PORT SCAN: {str(e)}"
            return f"{error_msg[:200]}\nEscaneo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"