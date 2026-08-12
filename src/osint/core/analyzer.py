"""analyzer.py - Coordinador central que enruta cada análisis a su servicio."""
class AnalysisCoordinator:
    
    @staticmethod
    def perform_analysis(analysis_type, target, language="es"):
        # Punto único de entrada para cualquier tipo de análisis
        # Este método actúa como router central para todos los servicios
        try:
            # Imports condicionales para evitar dependencias circulares
            # En esta sección empleo imports dinámicos para:
            # 1. Reducir tiempo de inicio de la aplicación
            # 2. Evitar importar todos los servicios si no son necesarios
            # 3. Permitir que servicios fallen individualmente sin afectar los demas
            
            if analysis_type == "geo":
                from osint.services.geo_service import GeoService
                return GeoService.analyze(target, language)
            elif analysis_type == "whois":
                from osint.services.whois_service import WhoisService
                return WhoisService.analyze(target, language)
            elif analysis_type == "ping":
                from osint.services.ping_service import PingService
                return PingService.analyze(target, language)
            elif analysis_type == "dns":
                from osint.services.dns_service import DnsService
                return DnsService.analyze(target, language)
            elif analysis_type == "ssl":
                from osint.services.ssl_service import SSLService
                return SSLService.analyze(target, language)
            elif analysis_type == "headers":
                from osint.services.headers_service import HeadersService
                return HeadersService.analyze(target, language)
            elif analysis_type == "portscan":
                from osint.services.port_service import PortService
                return PortService.analyze(target, language)
            elif analysis_type == "reverse":
                from osint.services.reverse_service import ReverseService
                return ReverseService.analyze(target, language)
            else:
                # Manejo de tipo de análisis no soportado
                # Esta excepción es para errores de programación, no de usuario
                raise Exception(f"Tipo de análisis no soportado: {analysis_type}")
                
        except ImportError as e:
            # Error al cargar servicio específico
            # Puede ocurrir si falta un módulo de servicio o hay error en import
            # Nota: Este error es crítico y debe ser registrado para debugging
            raise Exception(f"Error al cargar servicio {analysis_type}: {str(e)}")
        except Exception as e:
            # Error genérico con contexto adicional
            # Capturo cualquier excepción y agrego contexto del tipo de análisis
            # Esto facilita debugging manteniendo limpio el código del llamador
            raise Exception(f"Error en análisis {analysis_type}: {str(e)}")