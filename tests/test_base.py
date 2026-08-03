"""
test_base.py - Tests unitarios de los helpers de src/osint/services/base.py.
"""

import socket

import pytest

from osint.services.base import normalize_host, report_header, report_footer, http_get, resolve_ip


class TestNormalizeHost:
    def test_url_con_protocolo(self):
        assert normalize_host("https://www.example.com") == "example.com"

    def test_url_con_ruta(self):
        assert normalize_host("https://example.com/path/page") == "example.com"

    def test_http_y_www(self):
        assert normalize_host("http://www.example.com") == "example.com"

    def test_ip_directa(self):
        assert normalize_host("8.8.8.8") == "8.8.8.8"

    def test_mayusculas_y_espacios(self):
        assert normalize_host("  EXAMPLE.COM  ") == "example.com"

    def test_www_sin_protocolo(self):
        assert normalize_host("www.example.com") == "example.com"


class TestReportHeader:
    def test_formato_basico(self):
        header = report_header("DNS LOOKUP", "example.com")
        assert header.startswith("DNS LOOKUP - example.com")
        assert "=" * 60 in header

    def test_encabezado_contiene_objetivo(self):
        assert "8.8.8.8" in report_header("PING", "8.8.8.8")


class TestReportFooter:
    def test_contiene_timestamp(self):
        footer = report_footer()
        assert "Consulta:" in footer
        assert "=" * 60 in footer

    def test_formato_fecha(self):
        import re
        footer = report_footer()
        assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", footer)


class TestResolveIp:
    def test_ip_ya_resuelta(self):
        assert resolve_ip("8.8.8.8") == "8.8.8.8"

    def test_hostname_valido(self, monkeypatch):
        monkeypatch.setattr("osint.services.base.socket.gethostbyname", lambda x: "93.184.216.34")
        assert resolve_ip("example.com") == "93.184.216.34"

    def test_hostname_invalido_devuelve_target(self, monkeypatch):
        def _fail(_):
            raise socket.gaierror("No address")
        monkeypatch.setattr("osint.services.base.socket.gethostbyname", _fail)
        assert resolve_ip("no-existe.invalid") == "no-existe.invalid"


class TestHttpGet:
    def test_get_exitoso(self, monkeypatch):
        class FakeResponse:
            status_code = 200

        monkeypatch.setattr("osint.services.base.requests.get", lambda *a, **k: FakeResponse())
        resp = http_get("http://example.com")
        assert resp.status_code == 200

    def test_retry_y_exito(self, monkeypatch):
        """Un fallo seguido de éxito: el retry debe recuperarse."""
        import requests
        calls = {"n": 0}

        def _flaky(url, timeout=10, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise requests.Timeout("timeout")
            return type("R", (), {"status_code": 200})()

        monkeypatch.setattr("osint.services.base.requests.get", _flaky)
        resp = http_get("http://example.com")
        assert resp.status_code == 200
        assert calls["n"] == 2

    def test_falla_total_levanta_error(self, monkeypatch):
        import requests

        def _always_fail(url, timeout=10, **kwargs):
            raise requests.Timeout("always down")

        monkeypatch.setattr("osint.services.base.requests.get", _always_fail)
        with pytest.raises(requests.RequestException):
            http_get("http://example.com", retries=1)

    def test_retries_pasados_correctamente(self, monkeypatch):
        captured = {}

        def _fake(url, timeout=10, **kwargs):
            captured["timeout"] = timeout
            captured["kwargs"] = kwargs
            return type("R", (), {"status_code": 200})()

        monkeypatch.setattr("osint.services.base.requests.get", _fake)
        http_get("http://example.com", timeout=5, retries=1, verify=False)
        assert captured["timeout"] == 5
        assert captured["kwargs"] == {"verify": False}
