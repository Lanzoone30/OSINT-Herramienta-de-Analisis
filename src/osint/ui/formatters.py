"""
formatters.py - Formateo de texto para la interfaz.

Funciones puras que construyen los reportes de texto (resumen y
historial) sin depender de Qt, lo que las hace fácilmente testeables.

Why this design: La ventana principal solo pega texto en widgets;
la construcción de los reportes vive aquí.
"""

from datetime import datetime

__all__ = ["build_summary", "build_history_text"]


def build_summary(target: str, sections: list[tuple[str, str]], language: str) -> str:
    """Construir el resumen de un análisis completo.

    Args:
        target: Objetivo analizado.
        sections: Lista de (nombre, contenido) por cada análisis.
        language: Idioma del resumen ("es" o "en").

    Returns:
        Texto del resumen listo para mostrar.
    """
    es = language == "es"

    if es:
        summary = f"""RESUMEN DE ANÁLISIS COMPLETO

OBJETIVO: {target}
FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANÁLISIS REALIZADOS:
"""
    else:
        summary = f"""COMPLETE ANALYSIS SUMMARY

TARGET: {target}
DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ANALYSES PERFORMED:
"""

    # Contar análisis completados (ignorar placeholders sin resultados)
    completed = 0
    for name, content in sections:
        if content and not (content.startswith("Los resultados") or content.startswith("Geolocation results")):
            completed += 1
            summary += f"  • {name}: [{'COMPLETADO' if es else 'COMPLETED'}]\n"
        else:
            summary += f"  • {name}: [{'NO REALIZADO' if es else 'NOT PERFORMED'}]\n"

    # Estadísticas
    if es:
        summary += "\nESTADÍSTICAS:\n"
        summary += f"  • Total de análisis: {len(sections)}\n"
        summary += f"  • Completados: {completed}\n"
        summary += f"  • Porcentaje: {(completed / len(sections)) * 100:.1f}%\n"

        summary += "\nRECOMENDACIONES:\n"
        summary += "  1. Revisar vulnerabilidades SSL/TLS\n"
        summary += "  2. Verificar blacklists de la IP\n"
        summary += "  3. Monitorear cambios en DNS\n"
        summary += "  4. Documentar hallazgos para auditoría\n"

        summary += "\nNOTAS IMPORTANTES:\n"
        summary += "  • Esta herramienta es para fines educativos\n"
        summary += "  • Obtén autorización antes de cualquier prueba\n"
        summary += "  • Cumple con todas las leyes y regulaciones\n"
    else:
        summary += "\nSTATISTICS:\n"
        summary += f"  • Total analyses: {len(sections)}\n"
        summary += f"  • Completed: {completed}\n"
        summary += f"  • Percentage: {(completed / len(sections)) * 100:.1f}%\n"

        summary += "\nRECOMMENDATIONS:\n"
        summary += "  1. Review SSL/TLS vulnerabilities\n"
        summary += "  2. Check IP blacklists\n"
        summary += "  3. Monitor DNS changes\n"
        summary += "  4. Document findings for audit\n"

        summary += "\nIMPORTANT NOTES:\n"
        summary += "  • This tool is for educational purposes\n"
        summary += "  • Get authorization before any testing\n"
        summary += "  • Comply with all laws and regulations\n"

    return summary


def build_history_text(entries: list[dict], language: str) -> str:
    """Construir el texto del historial de análisis.

    Args:
        entries: Lista de entradas con claves timestamp, target y type.
        language: Idioma del texto ("es" o "en").

    Returns:
        Texto del historial listo para mostrar.
    """
    es = language == "es"

    if es:
        text = "HISTORIAL DE ANÁLISIS\n\n"
    else:
        text = "ANALYSIS HISTORY\n\n"

    # Mostrar los más recientes primero
    for i, entry in enumerate(entries, 1):
        text += f"{i}. [{entry['timestamp']}]\n"
        if es:
            text += f"   Objetivo: {entry['target']}\n"
            text += f"   Análisis: {entry['type']}\n"
        else:
            text += f"   Target: {entry['target']}\n"
            text += f"   Analysis: {entry['type']}\n"
        text += f"   {'─' * 40}\n"

    return text
