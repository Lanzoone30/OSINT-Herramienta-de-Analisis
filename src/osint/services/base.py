"""
base.py - Helpers compartidos por los servicios de análisis.

Funciones puras que eliminan la duplicación entre servicios:
normalización de host, encabezados de reporte y peticiones HTTP
con timeout y reintento centralizados.

Why this design: Una clase base con herencia sería una abstracción
injustificada (solo 3 de 8 servicios usan requests). Un módulo de
funciones es lo mínimo que elimina la duplicación real.
"""

import socket
import time
from datetime import datetime

import requests

__all__ = ["normalize_host", "report_header", "report_footer", "http_get"]


def normalize_host(target: str) -> str:
    """Limpiar un objetivo dejando solo el hostname.

    Quita protocolos, rutas y prefijo www, en minúsculas.

    Args:
        target: Dominio, IP o URL ingresada por el usuario.

    Returns:
        Hostname normalizado.
    """
    host = target.lower().strip()
    host = host.replace("https://", "").replace("http://", "")
    if host.startswith("www."):
        host = host[4:]
    return host.split("/")[0]


def report_header(title: str, target: str) -> str:
    """Generar el encabezado estándar de un reporte.

    Args:
        title: Nombre del análisis (ej: "DNS LOOKUP").
        target: Objetivo analizado.

    Returns:
        Encabezado con título, objetivo y separador.
    """
    return f"{title} - {target}\n" + "=" * 60 + "\n\n"


def report_footer() -> str:
    """Generar el pie de reporte con la marca de tiempo.

    Returns:
        Pie con separador y timestamp actual.
    """
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return "\n" + "=" * 60 + "\n" + f"Consulta: {stamp}"


def http_get(
    url: str,
    timeout: int = 10,
    retries: int = 2,
    **kwargs: object,
) -> requests.Response:
    """Realizar una petición GET con timeout y reintento.

    Centraliza el manejo de errores de red: un reintento con
    backoff de 1s ante fallos transitorios.

    Args:
        url: URL a consultar.
        timeout: Segundos de espera por intento.
        retries: Intentos adicionales ante fallos transitorios.
        **kwargs: Argumentos extra para requests.get (headers, verify, etc.).

    Returns:
        Respuesta de requests.

    Raises:
        requests.RequestException: Si todos los intentos fallan.
    """
    last_error: requests.RequestException | None = None
    for attempt in range(retries + 1):
        try:
            return requests.get(url, timeout=timeout, **kwargs)
        except requests.RequestException as e:
            last_error = e
            if attempt < retries:
                time.sleep(1)
    assert last_error is not None
    raise last_error


def resolve_ip(target: str) -> str:
    """Resolver un hostname a IP, tolerando que el target ya sea una IP.

    Args:
        target: Hostname o dirección IP.

    Returns:
        Dirección IP resuelta (o el target si no resuelve).
    """
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return target
