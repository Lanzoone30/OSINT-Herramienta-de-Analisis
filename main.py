import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

def main():
    print("=" * 50)
    print("OSINT - Herramienta de Analisis para Redes")
    print("Iniciando aplicación...")
    print("=" * 50)
    
    print("==============================================")
    print("||                                          ||")
    print("||        OSINT-Tool  v1.0.0                ||")
    print("||                                          ||")
    print("==============================================\n")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo moderno
    
    # Intenta cargar icono de aplicación desde assets/
    try:
        app_icon = QIcon("assets/icon_app.ico")
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
    except:
        pass  # Continuar sin icono en caso de no exisiir o ser borrado
    
    # Importar y crear la ventana principal
    from ui.main_window import AppOSINT
    
    print("[✓] Aplicación iniciada correctamente")
    print("    Esperando ventana principal...\n")
    
    window = AppOSINT()
    window.show()
    
    print("✓ Aplicación ejecutándose normalmente")
    print("  Cierre la ventana para finalizar\n")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()