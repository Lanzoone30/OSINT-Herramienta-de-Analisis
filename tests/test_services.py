"""
test_services.py - Tests unitarios de los servicios de análisis.

Todos los servicios se prueban con mocks para no depender de red real.
"""

import socket
import subprocess
import sys
import types
from unittest import mock


from osint.services.dns_service import DnsService
from osint.services.geo_service import GeoService
from osint.services.headers_service import HeadersService
from osint.services.ping_service import PingService
from osint.services.port_service import PortService
from osint.services.reverse_service import ReverseService
from osint.services.ssl_service import SSLService
from osint.services.whois_service import WhoisService


def _fake_response(status_code=200, url="https://example.com", json_data=None, headers=None):
    response = mock.Mock()
    response.status_code = status_code
    response.url = url
    response.reason = "OK"
    response.elapsed.total_seconds.return_value = 0.5
    response.json.return_value = json_data or {}
    response.headers = headers or {}
    return response


class TestDnsService:
    def test_analisis_dns_es(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.dns_service.socket.gethostbyname_ex",
            lambda host: (host, [], ["93.184.216.34"]),
        )
        monkeypatch.setattr(
            "osint.services.dns_service.socket.gethostbyaddr",
            lambda ip: ("example.com", [], []),
        )
        monkeypatch.setattr(
            "osint.services.dns_service.DnsService._try_advanced_lookup",
            staticmethod(lambda host, lang: ""),
        )
        result = DnsService.analyze("example.com", "es")
        assert "DNS LOOKUP" in result
        assert "93.184.216.34" in result

    def test_analisis_dns_sin_registros(self, monkeypatch):
        def _fail(_):
            raise socket.gaierror("no address")

        monkeypatch.setattr("osint.services.dns_service.socket.gethostbyname_ex", _fail)
        monkeypatch.setattr(
            "osint.services.dns_service.DnsService._try_advanced_lookup",
            staticmethod(lambda host, lang: ""),
        )
        result = DnsService.analyze("noexiste.invalid", "es")
        assert "No se encontraron registros A" in result


class TestGeoService:
    def test_geo_es_exitoso(self, monkeypatch):
        data = {"status": "success", "country": "United States", "city": "Mountain View"}
        monkeypatch.setattr(
            "osint.services.geo_service.http_get",
            lambda *a, **k: _fake_response(json_data=data),
        )
        monkeypatch.setattr("osint.services.geo_service.resolve_ip", lambda t: "8.8.8.8")
        result = GeoService.analyze("8.8.8.8", "es")
        assert "GEOLOCATION" in result
        assert "8.8.8.8" in result

    def test_geo_error_api(self, monkeypatch):
        import requests
        monkeypatch.setattr(
            "osint.services.geo_service.http_get",
            lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("boom")),
        )
        monkeypatch.setattr("osint.services.geo_service.resolve_ip", lambda t: "8.8.8.8")
        result = GeoService.analyze("8.8.8.8", "es")
        assert "ERROR API" in result

    def test_geo_status_failure(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.geo_service.http_get",
            lambda *a, **k: _fake_response(json_data={"status": "fail"}),
        )
        monkeypatch.setattr("osint.services.geo_service.resolve_ip", lambda t: "8.8.8.8")
        result = GeoService.analyze("8.8.8.8", "es")
        assert "No se pudo obtener geolocalización" in result


class TestHeadersService:
    def test_headers_es(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.headers_service.http_get",
            lambda *a, **k: _fake_response(headers={"Server": "nginx"}),
        )
        monkeypatch.setattr(
            "osint.services.headers_service.HeadersService._format_headers_by_type",
            staticmethod(lambda h, lang: ""),
        )
        monkeypatch.setattr(
            "osint.services.headers_service.HeadersService._get_stats",
            staticmethod(lambda r, lang: ""),
        )
        result = HeadersService.analyze("example.com", "es")
        assert "HEADERS" in result
        assert "example.com" in result

    def test_headers_error_red(self, monkeypatch):
        import requests
        monkeypatch.setattr(
            "osint.services.headers_service.http_get",
            lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("down")),
        )
        result = HeadersService.analyze("example.com", "es")
        assert "ERROR DE CONEXIÓN" in result


class TestSslService:
    def test_ssl_es(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.ssl_service.requests.get",
            lambda *a, **k: _fake_response(url="https://example.com"),
        )
        monkeypatch.setattr(
            "osint.services.ssl_service.SSLService._get_certificate_info",
            staticmethod(lambda h, lang: ""),
        )
        monkeypatch.setattr(
            "osint.services.ssl_service.SSLService._get_security_headers",
            staticmethod(lambda r, lang: ""),
        )
        monkeypatch.setattr(
            "osint.services.ssl_service.SSLService._get_security_checks",
            staticmethod(lambda r, lang: ""),
        )
        result = SSLService.analyze("example.com", "es")
        assert "SSL/TLS" in result
        assert "HTTPS" in result

    def test_ssl_error_certificado(self, monkeypatch):
        import requests
        monkeypatch.setattr(
            "osint.services.ssl_service.requests.get",
            lambda *a, **k: (_ for _ in ()).throw(requests.exceptions.SSLError("bad cert")),
        )
        result = SSLService.analyze("example.com", "es")
        assert "certificado" in result.lower()


class TestPingService:
    def test_ping_es(self, monkeypatch):
        completed = subprocess.CompletedProcess([], 0, stdout="64 bytes from 8.8.8.8\nreply")
        monkeypatch.setattr(subprocess, "run", lambda *a, **k: completed)
        result = PingService.analyze("8.8.8.8", "es")
        assert "PING" in result

    def test_ping_falla(self, monkeypatch):
        monkeypatch.setattr(
            subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no ping"))
        )
        result = PingService.analyze("8.8.8.8", "es")
        assert result  # no debe lanzar excepción


class TestPortService:
    def test_port_abierto(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.port_service.socket.socket.connect_ex", lambda self, addr: 0
        )
        result = PortService.analyze("example.com", "es")
        assert "PUERTOS ABIERTOS" in result

    def test_port_cerrado(self, monkeypatch):
        monkeypatch.setattr(
            "osint.services.port_service.socket.socket.connect_ex", lambda self, addr: 1
        )
        result = PortService.analyze("example.com", "es")
        assert "No se encontraron puertos abiertos" in result


class TestReverseService:
    def test_reverse_es(self, monkeypatch):
        monkeypatch.setattr("osint.services.reverse_service.resolve_ip", lambda t: "8.8.8.8")
        monkeypatch.setattr(
            "osint.services.reverse_service.socket.gethostbyaddr",
            lambda ip: ("dns.google", [], []),
        )
        result = ReverseService.analyze("8.8.8.8", "es")
        assert "REVERSE DNS" in result
        assert "dns.google" in result

    def test_reverse_sin_ptr(self, monkeypatch):
        monkeypatch.setattr("osint.services.reverse_service.resolve_ip", lambda t: "8.8.8.8")

        def _fail(_):
            raise OSError("no PTR")

        monkeypatch.setattr("osint.services.reverse_service.socket.gethostbyaddr", _fail)
        result = ReverseService.analyze("8.8.8.8", "es")
        assert "REVERSE DNS" in result


class TestWhoisService:
    def test_whois_sin_dependencia(self, monkeypatch):
        # Si python-whois no está instalado, devuelve error formateado
        monkeypatch.setitem(sys.modules, "whois", None)
        result = WhoisService.analyze("example.com", "es")
        assert result  # no lanza, devuelve reporte

    def test_whois_con_datos(self, monkeypatch):
        fake_data = mock.Mock()
        fake_data.domain_name = ["example.com"]
        fake_data.registrar = "Example Registrar"

        fake_module = types.ModuleType("whois")
        fake_module.whois = mock.Mock(return_value=fake_data)
        monkeypatch.setitem(sys.modules, "whois", fake_module)

        monkeypatch.setattr(
            "osint.services.whois_service.WhoisService._format_spanish",
            staticmethod(lambda d, data: "REPORTE WHOIS"),
        )
        result = WhoisService.analyze("example.com", "es")
        assert "REPORTE WHOIS" in result
