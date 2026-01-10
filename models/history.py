from datetime import datetime
from collections import deque

class AnalysisHistory:
    # Maneja historial de análisis con límite configurable
    def __init__(self, max_entries=50):
        self.max_entries = max_entries
        self.history = deque(maxlen=max_entries)
    
    def add_entry(self, target, analysis_type):
        # Registro con objetivo, tipo y marca de tiempo
        entry = {
            "target": target,
            "type": analysis_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
    
    def get_history(self, reverse=True):
        # Devuelve historial, invertido si se solicita
        history_list = list(self.history)
        if reverse:
            history_list = list(reversed(history_list))
        return history_list
    
    def clear(self):
        # Limpia todo el historial
        self.history.clear()
    
    def count(self):
        # Cantidad de entradas actuales
        return len(self.history)
