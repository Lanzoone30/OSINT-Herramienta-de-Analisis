"""ping_service.py - Pruebas de conectividad ICMP (ping)."""
import subprocess
import platform
from datetime import datetime

class PingService:
    
    @staticmethod
    def analyze(target: str, language: str = "es") -> str:
        try:
            # Limpio protocolos HTTP/HTTPS del objetivo
            host = target.replace("https://", "").replace("http://", "")
            
            result = f"PING TEST - {host}\n"
            result += "=" * 60 + "\n\n"
            
            # Información de configuración
            if language == "es":
                result += "CONFIGURACIÓN DEL PING\n"
            else:
                result += "PING CONFIGURATION\n"
            result += "-" * 25 + "\n"
            
            if language == "es":
                result += f"Objetivo      : {host}\n"
                result += f"Sistema       : {platform.system()} {platform.release()}\n"
            else:
                result += f"Target        : {host}\n"
                result += f"System        : {platform.system()} {platform.release()}\n"
            
            # Adapto el comando según el sistema operativo
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", "4", host]  # 4 paquetes en Windows
                if language == "es":
                    result += "Comando       : ping -n 4\n"
                else:
                    result += "Command       : ping -n 4\n"
            else:
                cmd = ["ping", "-c", "4", host]  # 4 paquetes en Unix/Linux
                if language == "es":
                    result += "Comando       : ping -c 4\n"
                else:
                    result += "Command       : ping -c 4\n"
            
            try:
                # Ejecuto el ping con timeout de 15 segundos
                ping_result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                # Muestro las últimas líneas (donde está el resumen)
                if language == "es":
                    result += "\nRESULTADO DEL PING\n"
                else:
                    result += "\nPING RESULT\n"
                result += "-" * 25 + "\n"
                
                # Tomo las últimas 8 líneas que contienen estadísticas
                output_lines = ping_result.stdout.split('\n')
                for line in output_lines[-8:]:
                    if line.strip():
                        result += f"{line}\n"
                
                # Interpreto el código de retorno
                if language == "es":
                    result += "\nANÁLISIS\n"
                else:
                    result += "\nANALYSIS\n"
                result += "-" * 25 + "\n"
                
                if ping_result.returncode == 0:
                    if language == "es":
                        result += "Estado        : HOST RESPONDE\n"
                    else:
                        result += "Status        : HOST RESPONDS\n"
                else:
                    if language == "es":
                        result += "Estado        : SIN RESPUESTA\n"
                    else:
                        result += "Status        : NO RESPONSE\n"
                
                if language == "es":
                    result += f"Código salida : {ping_result.returncode}\n"
                else:
                    result += f"Exit code     : {ping_result.returncode}\n"
                    
            except subprocess.TimeoutExpired:
                # Timeout específico para comandos muy lentos
                if language == "es":
                    result += "\nERROR: Timeout (15 segundos)\n"
                else:
                    result += "\nERROR: Timeout (15 seconds)\n"
            
            # Notas importantes para el usuario
            if language == "es":
                result += "\nNOTAS\n"
                result += "-" * 25 + "\n"
                result += "• Traceroute requiere privilegios elevados\n"
                result += "• Algunos hosts bloquean ping (ICMP)\n"
            else:
                result += "\nNOTES\n"
                result += "-" * 25 + "\n"
                result += "• Traceroute requires elevated privileges\n"
                result += "• Some hosts block ping (ICMP)\n"
            
            # Timestamp del test
            result += "\n" + "=" * 60 + "\n"
            result += f"Test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            # Manejo general de errores
            error_msg = f"PING ERROR: {str(e)}" if language == "en" else f"ERROR EN PING: {str(e)}"
            return f"{error_msg[:200]}\nTest: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"