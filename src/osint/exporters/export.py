"""
export.py - Exportación de resultados en múltiples formatos.

Proporciona un único punto de entrada para exportar los resultados
de un análisis a TXT, JSON o CSV.

Why this design: Centraliza la lógica de exportación (antes en tres
módulos casi idénticos) y evita duplicación en el llamador.
"""

import csv
import json

__all__ = ["export_results"]


def export_results(all_results: dict, filename: str, format: str, language: str = "es") -> None:
    """Exportar los resultados de un análisis al formato indicado.

    Args:
        all_results: Diccionario con los resultados (target, timestamp y
            secciones de análisis).
        filename: Ruta del archivo de salida.
        format: Formato de exportación: "txt", "csv" o "json".
        language: Idioma del encabezado del informe ("es" o "en").

    Raises:
        ValueError: Si el formato no es soportado.
    """
    if format == "json":
        _export_json(all_results, filename)
    elif format == "csv":
        _export_csv(all_results, filename)
    elif format == "txt":
        _export_txt(all_results, filename, language)
    else:
        raise ValueError(f"Formato de exportación no soportado: {format}")


def _export_json(all_results: dict, filename: str) -> None:
    """Escribir resultados en JSON (UTF-8 para caracteres especiales)."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)


def _export_csv(all_results: dict, filename: str) -> None:
    """Escribir resultados en CSV, limitando a las primeras líneas por sección."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Section", "Content"])
        for key, value in all_results.items():
            if key not in ("target", "timestamp") and value:
                lines = value.split("\n")[:10]
                writer.writerow([key, " ".join(lines[:3])])


def _export_txt(all_results: dict, filename: str, language: str) -> None:
    """Escribir un informe legible en TXT con las secciones con contenido."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("INFORME DE ANÁLISIS OSINT\n" if language == "es" else "OSINT ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")

        if language == "es":
            f.write(f"Objetivo: {all_results['target']}\n")
            f.write(f"Fecha: {all_results['timestamp']}\n\n")
        else:
            f.write(f"Target: {all_results['target']}\n")
            f.write(f"Date: {all_results['timestamp']}\n\n")

        sections = [
            ("Geolocalización" if language == "es" else "Geolocation", "geo"),
            ("WHOIS", "whois"),
            ("Ping/Traceroute", "ping"),
            ("DNS Lookup", "dns"),
            ("SSL/TLS", "ssl"),
            ("Headers HTTP" if language == "es" else "HTTP Headers", "headers"),
            ("Port Scan", "portscan"),
            ("Reverse IP", "reverse"),
            ("Resumen" if language == "es" else "Summary", "summary"),
        ]

        for title, key in sections:
            if all_results.get(key):
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"{title.upper()}\n")
                f.write("=" * 60 + "\n\n")
                f.write(all_results[key] + "\n")
