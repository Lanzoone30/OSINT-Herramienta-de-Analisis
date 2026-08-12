"""worker.py - Hilo de trabajo (QThread) para tareas en segundo plano."""
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(object)        # Exito con resultado
    error = pyqtSignal(str)              # Error con mensaje
    progress = pyqtSignal(int, str)      # Progreso (porcentaje + descripcion)
    item_ready = pyqtSignal(str, object) # Item incremental (clave + resultado)

    def __init__(self, task_func, *args, **kwargs):
        # Inicializo con función y sus argumentos
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.progress.emit(10, "Iniciando análisis...")
            result = self.task_func(*self.args, **self.kwargs)
            self.progress.emit(100, "Completado")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))