import json

class JsonExporter:
    @staticmethod
    def export(all_results, filename):
        # Escritura en UTF-8 para soportar caracteres especiales
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)