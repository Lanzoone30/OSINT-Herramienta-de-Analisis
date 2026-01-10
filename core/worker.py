from PyQt6.QtCore import QThread, pyqtSignal

# En esta clase manejo tareas en segundo plano para no bloquear la UI
class WorkerThread(QThread):
    
    # Defino señales para comunicación segura entre hilos
    finished = pyqtSignal(object)    # Éxito con resultado
    error = pyqtSignal(str)          # Error con mensaje
    progress = pyqtSignal(int, str)  # Progreso (porcentaje + descripción)
    
    def __init__(self, task_func, *args, **kwargs):
        # Inicializo con función y sus argumentos
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        # Ejecuto la tarea en segundo plano con manejo de errores
        try:
            self.progress.emit(10, "Iniciando análisis...")
            result = self.task_func(*self.args, **self.kwargs)
            self.progress.emit(100, "Completado")
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))