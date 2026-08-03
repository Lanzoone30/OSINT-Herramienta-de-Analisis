"""
test_formatters.py - Tests unitarios de los formatters de UI (funciones puras).
"""

from osint.ui.formatters import build_summary, build_history_text

SECTIONS = [
    ("Geolocalización", "GEOLOCATION ANALYSIS\ncontenido real"),
    ("WHOIS", ""),
    ("Ping", "PING TEST\ncontenido real"),
]


class TestBuildSummary:
    def test_es_contiene_encabezado(self):
        summary = build_summary("example.com", SECTIONS, "es")
        assert "RESUMEN DE ANÁLISIS COMPLETO" in summary
        assert "example.com" in summary

    def test_en_contiene_encabezado(self):
        summary = build_summary("example.com", SECTIONS, "en")
        assert "COMPLETE ANALYSIS SUMMARY" in summary
        assert "example.com" in summary

    def test_conteo_completados(self):
        summary = build_summary("example.com", SECTIONS, "es")
        assert "[COMPLETADO]" in summary
        assert "[NO REALIZADO]" in summary

    def test_porcentaje_correcto(self):
        # 2 de 3 completados = 66.7%
        summary = build_summary("example.com", SECTIONS, "es")
        assert "66.7%" in summary

    def test_estadisticas_es(self):
        summary = build_summary("example.com", SECTIONS, "es")
        assert "ESTADÍSTICAS" in summary
        assert "Total de análisis: 3" in summary
        assert "Completados: 2" in summary

    def test_estadisticas_en(self):
        summary = build_summary("example.com", SECTIONS, "en")
        assert "STATISTICS" in summary
        assert "Total analyses: 3" in summary

    def test_placeholders_no_cuentan_como_completados(self):
        sections = [("Geo", "Los resultados de geolocalización aparecerán aquí...")]
        summary = build_summary("example.com", sections, "es")
        assert "[NO REALIZADO]" in summary


class TestBuildHistoryText:
    ENTRIES = [
        {"timestamp": "2026-01-01 10:00:00", "target": "a.com", "type": "geo"},
        {"timestamp": "2026-01-02 11:00:00", "target": "b.com", "type": "dns"},
    ]

    def test_es_formato(self):
        text = build_history_text(self.ENTRIES, "es")
        assert "HISTORIAL DE ANÁLISIS" in text
        assert "a.com" in text
        assert "geo" in text

    def test_en_formato(self):
        text = build_history_text(self.ENTRIES, "en")
        assert "ANALYSIS HISTORY" in text
        assert "b.com" in text

    def test_numeracion(self):
        text = build_history_text(self.ENTRIES, "es")
        assert "1." in text
        assert "2." in text

    def test_vacia(self):
        text = build_history_text([], "es")
        assert text == "HISTORIAL DE ANÁLISIS\n\n"
