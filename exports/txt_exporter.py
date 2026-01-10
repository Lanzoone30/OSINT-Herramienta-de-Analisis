from datetime import datetime

class TxtExporter:
    # Exportador dedicado para resultados en formato TXT
    @staticmethod
    def export(all_results, filename, language="es"):
        # Escritura en UTF-8 para soportar caracteres especiales
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            if language == "es":
                f.write(f"INFORME DE ANÁLISIS OSINT\n")
            else:
                f.write(f"OSINT ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            # Encabezado con objetivo y fecha según idioma
            if language == "es":
                f.write(f"Objetivo: {all_results['target']}\n")
                f.write(f"Fecha: {all_results['timestamp']}\n\n")
            else:
                f.write(f"Target: {all_results['target']}\n")
                f.write(f"Date: {all_results['timestamp']}\n\n")
            
            # Secciones principales del informe
            sections = [
                ("Geolocalización" if language == "es" else "Geolocation", "geo"),
                ("WHOIS", "whois"),
                ("Ping/Traceroute", "ping"),
                ("DNS Lookup", "dns"),
                ("SSL/TLS", "ssl"),
                ("Headers HTTP" if language == "es" else "HTTP Headers", "headers"),
                ("Port Scan", "portscan"),
                ("Reverse IP", "reverse"),
                ("Resumen" if language == "es" else "Summary", "summary")
            ]
            
            # Escribo cada sección si contiene resultados
            for title, key in sections:
                if all_results.get(key):
                    f.write("\n" + "=" * 60 + "\n")
                    f.write(f"{title.upper()}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(all_results[key] + "\n")
