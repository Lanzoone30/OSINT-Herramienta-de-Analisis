import os
import sys
import shutil
import subprocess
import threading
import time
from pathlib import Path

# En esta clase manejo la compilación de la aplicación a un ejecutable .exe
# La idea aquí es automatizar todo el proceso con PyInstaller y manejo de archivos
class OSINTCompiler:
    def __init__(self):
        # Rutas principales: raíz del proyecto y directorios de trabajo
        self.root = Path(__file__).parent
        self.final_dir = self.root / "build_final"   # Ejecutable final aquí
        self.temp_dir = self.root / "build_temp"     # Archivos temporales (se eliminan)
        self.app_name = "OSINT-Herramienta de Analisis de Redes"
        self.running = False  # Para controlar animaciones en hilos
        self.spinner_chars = ["|", "/", "-", "\\"]  # Caracteres para animación
    
    def show_banner(self):
        banner = """
        +===========================================+
        |   COMPILADOR OSINT - V 1.0.0              |
        +===========================================+
        |   Generando: .exe auto-contenido          |
        |   Destino:   build_final/                 |
        |   Temporal:  build_temp/ (auto-eliminado) |
        |   Creditos:  Adrian A. Lanzone            |
        +===========================================+
        """
        print(banner)
    
    def spinner_animation(self, message="Compilando"):
        # Animación simple de spinner para mostrar progreso
        i = 0
        while self.running:
            sys.stdout.write(f"\r[{self.spinner_chars[i % len(self.spinner_chars)]}] {message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * 60 + "\r")  # Limpiar línea
    
    def setup_directories(self):
        print("[1/5] Preparando directorios...")
        
        # Limpio directorios anteriores si existen
        for dir_path in [self.final_dir, self.temp_dir]:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)  # Elimino recursivamente
                except:
                    return False  # Error al limpiar
            
            dir_path.mkdir(parents=True)  # Creo directorios
        
        return True
    
    def verify_resources(self):
        print("[2/5] Verificando recursos...")
        
        # Verifico que el icono principal exista
        icon_path = self.root / "assets" / "icon_app.ico"
        if not icon_path.exists():
            return False
        
        # Copio el icono al directorio temporal
        shutil.copy2(icon_path, self.temp_dir / "icon_app.ico")
        return True
    
    def copy_source_files(self):
        print("[3/5] Copiando archivos fuente...")
        
        # Copio main.py principal
        main_src = self.root / "main.py"
        if main_src.exists():
            shutil.copy2(main_src, self.temp_dir / "main.py")
        
        # Lista de carpetas del proyecto a copiar
        folders_to_copy = ["assets", "config", "core", "exports", "models", "services", "ui"]
        
        for folder in folders_to_copy:
            src = self.root / folder
            if src.exists() and src.is_dir():
                # Copio recursivamente con reemplazo
                shutil.copytree(src, self.temp_dir / folder, dirs_exist_ok=True)
        
        return True
    
    def generate_pyinstaller_command(self):
        # Construyo el comando de PyInstaller con todas las opciones necesarias
        cmd = [
            "pyinstaller",
            "--onefile",      # Un solo archivo .exe
            "--noconsole",    # Sin consola (aplicación de ventana)
            "--clean",        # Limpiar caché de compilaciones anteriores
            "--windowed",     # Aplicación con ventana
            f"--name={self.app_name}",
            f"--distpath={self.final_dir.resolve()}",      # Donde va el .exe final
            f"--workpath={(self.temp_dir / 'work').resolve()}",    # Archivos temporales
            f"--specpath={(self.temp_dir / 'spec').resolve()}",    # Archivo spec
        ]
        
        # Añado icono (si no existe, compilara igual pero sin icono)
        icon_path = self.temp_dir / "icon_app.ico"
        if icon_path.exists():
            cmd.append(f"--icon={icon_path.resolve()}")
        
        # Módulos que PyInstaller no detecta automáticamente
        hidden_imports = [
            "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
            "PyQt6.QtNetwork", "PyQt6.sip",    # Componentes Qt necesarios
            "whois", "requests", "dns.resolver", "dns.rdatatype"  # Dependencias propias
        ]
        
        for imp in hidden_imports:
            cmd.append(f"--hidden-import={imp}")
        
        # Incluir assets recursivamente
        assets_dir = self.temp_dir / "assets"
        if assets_dir.exists():
            # Incluir toda la carpeta assets y su contenido
            cmd.extend(["--add-data", f"{assets_dir.resolve()}{os.pathsep}assets"])
        
        # Incluir config y ui
        for data_folder in ["config", "ui"]:
            data_path = self.temp_dir / data_folder
            if data_path.exists():
                cmd.extend(["--add-data", f"{data_path.resolve()}{os.pathsep}{data_folder}"])
        
        # Archivo principal a compilar
        main_file = self.temp_dir / "main.py"
        cmd.append(str(main_file.resolve()))
        
        return cmd
    
    def compile_project(self):
        print("[4/5] Compilando aplicación...")
        
        cmd = self.generate_pyinstaller_command()
        
        # Inicio animación en hilo separado
        self.running = True
        spinner_thread = threading.Thread(target=self.spinner_animation)
        spinner_thread.start()
        
        try:
            # Ejecuto PyInstaller
            result = subprocess.run(
                cmd,
                cwd=self.temp_dir,  # Ejecutar desde directorio temporal
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'  # Ignorar errores de encoding
            )
            
            # Detengo animación
            self.running = False
            spinner_thread.join(timeout=1)
            
            # Verifico resultado
            if result.returncode == 0:
                exe_file = self.final_dir / f"{self.app_name}.exe"
                if exe_file.exists():
                    size_mb = exe_file.stat().st_size / (1024 * 1024)
                    return True, exe_file, size_mb
                else:
                    return False, None, 0
            else:
                return False, None, 0
                
        except Exception as e:
            self.running = False
            spinner_thread.join(timeout=1)
            return False, None, 0
    
    def cleanup_temp_files(self):
        print("[5/5] Limpiando archivos temporales...")
        
        # Elimino directorio temporal
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                return True
            except:
                return False
        return True
    
    def show_summary(self, exe_file, size_mb):
        summary = """
        +===========================================+
        |          COMPILACION COMPLETADA           |
        +===========================================+
        """
        print(summary)
        
        if exe_file and exe_file.exists():
            print(f"  EJECUTABLE: {exe_file.name}")
            print(f"  TAMAÑO:     {size_mb:.1f} MB")
            print(f"  UBICACION:  build_final/")
        
        print("\n" + "=" * 50)
    
    def run(self):
        # Método principal que orquesta todo el proceso
        self.show_banner()
        
        try:
            # Paso 1: Preparar directorios
            if not self.setup_directories():
                return
            
            # Paso 2: Verificar recursos
            if not self.verify_resources():
                return
            
            # Paso 3: Copiar archivos fuente
            if not self.copy_source_files():
                return
            
            # Paso 4: Compilar con PyInstaller
            success, exe_file, size_mb = self.compile_project()
            
            if not success:
                return
            
            # Paso 5: Limpiar archivos temporales
            self.cleanup_temp_files()
            
            # Mostrar resumen final
            self.show_summary(exe_file, size_mb)
            
        except KeyboardInterrupt:
            self.running = False
        except:
            pass
        finally:
            self.running = False

def main():
    # Punto de entrada
    compiler = OSINTCompiler()
    compiler.run()

if __name__ == "__main__":
    main()