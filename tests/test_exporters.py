"""
test_exporters.py - Tests unitarios de la exportación de resultados.
"""

import csv
import json

import pytest

from osint.exporters.export import export_results

SAMPLE = {
    "target": "example.com",
    "timestamp": "2026-01-01 12:00:00",
    "geo": "GEOLOCATION ANALYSIS - example.com\nlinea 1\nlinea 2\nlinea 3\nlinea 4\nlinea 5\nlinea 6\nlinea 7\nlinea 8\nlinea 9\nlinea 10\nlinea 11",
    "whois": "",
    "summary": "RESUMEN\ncontenido",
}


@pytest.fixture
def tmp_file(tmp_path):
    return tmp_path / "resultado"


class TestExportJson:
    def test_json_valido_y_utf8(self, tmp_file):
        path = str(tmp_file.with_suffix(".json"))
        export_results(SAMPLE, path, "json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["target"] == "example.com"
        assert data["geo"].startswith("GEOLOCATION")


class TestExportCsv:
    def test_csv_genera_cabecera(self, tmp_file):
        path = str(tmp_file.with_suffix(".csv"))
        export_results(SAMPLE, path, "csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["Section", "Content"]

    def test_csv_excluye_target_y_timestamp(self, tmp_file):
        path = str(tmp_file.with_suffix(".csv"))
        export_results(SAMPLE, path, "csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        sections = {row[0] for row in rows[1:]}
        assert "target" not in sections
        assert "timestamp" not in sections

    def test_csv_trunca_a_3_lineas(self, tmp_file):
        path = str(tmp_file.with_suffix(".csv"))
        export_results(SAMPLE, path, "csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        geo_row = next(row for row in rows if row[0] == "geo")
        # Solo las 3 primeras líneas se unen en una celda
        # (la línea 1 es el encabezado del reporte)
        assert "linea 1" in geo_row[1]
        assert "linea 2" in geo_row[1]
        assert "linea 3" not in geo_row[1]
        assert "linea 11" not in geo_row[1]


class TestExportTxt:
    def test_txt_contiene_objetivo_es(self, tmp_file):
        path = str(tmp_file.with_suffix(".txt"))
        export_results(SAMPLE, path, "txt", "es")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "example.com" in content
        assert "INFORME DE ANÁLISIS OSINT" in content

    def test_txt_ingles(self, tmp_file):
        path = str(tmp_file.with_suffix(".txt"))
        export_results(SAMPLE, path, "txt", "en")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "OSINT ANALYSIS REPORT" in content

    def test_txt_omite_secciones_vacias(self, tmp_file):
        path = str(tmp_file.with_suffix(".txt"))
        export_results(SAMPLE, path, "txt")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "WHOIS" not in content  # sección whois vacía -> no se escribe


class TestExportFormatoInvalido:
    def test_formato_no_soportado(self, tmp_file):
        path = str(tmp_file.with_suffix(".xyz"))
        with pytest.raises(ValueError):
            export_results(SAMPLE, path, "xyz")
