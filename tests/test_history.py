"""
test_history.py - Tests unitarios del modelo AnalysisHistory.
"""


from osint.models.history import AnalysisHistory


class TestAnalysisHistory:
    def test_inicia_vacia(self):
        h = AnalysisHistory()
        assert h.count() == 0

    def test_agregar_entrada(self):
        h = AnalysisHistory()
        h.add_entry("example.com", "geo")
        assert h.count() == 1
        entry = h.get_history()[0]
        assert entry["target"] == "example.com"
        assert entry["type"] == "geo"
        assert "timestamp" in entry

    def test_orden_mas_reciente_primero(self):
        h = AnalysisHistory()
        h.add_entry("a.com", "geo")
        h.add_entry("b.com", "dns")
        history = h.get_history()
        assert history[0]["target"] == "b.com"
        assert history[1]["target"] == "a.com"

    def test_reverse_false_mantiene_orden(self):
        h = AnalysisHistory()
        h.add_entry("a.com", "geo")
        h.add_entry("b.com", "dns")
        history = h.get_history(reverse=False)
        assert history[0]["target"] == "a.com"
        assert history[1]["target"] == "b.com"

    def test_limite_max_entries(self):
        h = AnalysisHistory(max_entries=3)
        for i in range(5):
            h.add_entry(f"site{i}.com", "geo")
        assert h.count() == 3
        # Las más antiguas se descartan (deque maxlen)
        history = h.get_history()
        assert all(entry["target"] != "site0.com" for entry in history)

    def test_clear(self):
        h = AnalysisHistory()
        h.add_entry("a.com", "geo")
        h.clear()
        assert h.count() == 0

    def test_get_history_no_comparte_referencia(self):
        h = AnalysisHistory()
        h.add_entry("a.com", "geo")
        history = h.get_history()
        history.clear()
        assert h.count() == 1
