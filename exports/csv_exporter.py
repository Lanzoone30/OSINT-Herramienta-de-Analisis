import csv

class CsvExporter:
    # Exportador dedicado para resultados en formato CSV
    @staticmethod
    def export(all_results, filename):
        """Exporta resultados a formato CSV."""
        try:
            # Escritura en UTF-8 para soportar caracteres especiales
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Section", "Content"])
                for key, value in all_results.items():
                    if key not in ['target', 'timestamp'] and value:
                        # Solo guardo primeras líneas para mantener CSV legible
                        lines = value.split('\n')[:10]
                        writer.writerow([key, " ".join(lines[:3])])
        except Exception as e:
            # Capturo cualquier error y lo informo claramente
            raise Exception(f"Error al exportar CSV: {str(e)}")
