"""compilar_app.py - Compilador de desarrollo: genera .exe + SHA256SUMS para releases.

Uso: python tools/compilar_app.py

Genera Builds/Windows/OSINT-Herramienta_de_Analisis-v<version>-windows-x64.exe
y su archivo SHA256SUMS-v<version>.txt, listos para publicar en GitHub Releases.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from osint import __version__  # noqa: E402


class OSINTCompiler:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent
        self.build_dir = self.root / "Builds" / "Windows"
        self.temp_dir = self.root / "build_temp"
        self.app_name = f"OSINT-Herramienta_de_Analisis-v{__version__}-windows-x64"
        self.running = False
        self.spinner_chars = ["|", "/", "-", "\\"]

    def show_banner(self):
        banner = f"""
        +===========================================+
        |   COMPILADOR OSINT - V {__version__}             |
        +===========================================+
        |   Modo:       Desarrollo                   |
        |   Generando:  .exe auto-contenido         |
        |   Destino:    Builds/Windows/             |
        |   Creditos:   Adrian A. Lanzone            |
        +===========================================+
        """
        print(banner)

    def spinner_animation(self, message="Compilando"):
        i = 0
        while self.running:
            sys.stdout.write(f"\r[{self.spinner_chars[i % len(self.spinner_chars)]}] {message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * 60 + "\r")

    def setup_directories(self):
        print("[1/5] Preparando directorios...")
        for dir_path in [self.build_dir, self.temp_dir]:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                except OSError:
                    return False
            dir_path.mkdir(parents=True)
        return True

    def verify_resources(self):
        print("[2/5] Verificando recursos...")
        icon_path = self.root / "assets" / "icon_app.ico"
        if not icon_path.exists():
            return False
        shutil.copy2(icon_path, self.temp_dir / "icon_app.ico")
        return True

    def copy_source_files(self):
        print("[3/5] Copiando archivos fuente...")
        main_src = self.root / "main.py"
        if main_src.exists():
            shutil.copy2(main_src, self.temp_dir / "main.py")
        for folder in ["assets", "src"]:
            src = self.root / folder
            if src.exists() and src.is_dir():
                shutil.copytree(src, self.temp_dir / folder, dirs_exist_ok=True)
        return True

    def generate_pyinstaller_command(self):
        cmd = [
            "pyinstaller",
            "--onefile",
            "--noconsole",
            "--clean",
            "--windowed",
            "--name", self.app_name,
            "--distpath", str(self.build_dir.resolve()),
            "--workpath", str((self.temp_dir / "work").resolve()),
            "--specpath", str((self.temp_dir / "spec").resolve()),
            "--paths", str((self.temp_dir / "src").resolve()),
        ]
        icon_path = self.temp_dir / "icon_app.ico"
        if icon_path.exists():
            cmd.append(f"--icon={icon_path.resolve()}")
        hidden_imports = [
            "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
            "PyQt6.QtNetwork", "PyQt6.sip",
            "whois", "requests", "dns.resolver", "dns.rdatatype",
        ]
        for imp in hidden_imports:
            cmd.append(f"--hidden-import={imp}")
        assets_dir = self.temp_dir / "assets"
        if assets_dir.exists():
            cmd.extend(["--add-data", f"{assets_dir.resolve()}{os.pathsep}assets"])
        cmd.append(str((self.temp_dir / "main.py").resolve()))
        return cmd

    def compile_project(self):
        print("[4/5] Compilando aplicación...")
        cmd = self.generate_pyinstaller_command()
        self.running = True
        spinner_thread = threading.Thread(target=self.spinner_animation)
        spinner_thread.start()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        finally:
            self.running = False
            spinner_thread.join(timeout=1)
        if result.returncode == 0:
            # En Windows PyInstaller agrega .exe; en Linux no (verificacion dev)
            exe_file = self.build_dir / f"{self.app_name}.exe"
            if not exe_file.exists():
                exe_file = self.build_dir / self.app_name
            if exe_file.exists():
                return True, exe_file

        # La compilacion fallo: muestra la salida de PyInstaller para diagnosticar.
        print("\n[ERROR] PyInstaller fallo (returncode=%s)" % result.returncode)
        if result.stdout:
            print("--- stdout ---\n" + result.stdout[-4000:])
        if result.stderr:
            print("--- stderr ---\n" + result.stderr[-4000:])
        return False, None

    def generate_checksum(self, exe_file):
        sha256 = hashlib.sha256()
        with exe_file.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        sum_file = self.build_dir / f"SHA256SUMS-{__version__}.txt"
        sum_file.write_text(f"{sha256.hexdigest()}  {exe_file.name}\n", encoding="utf-8")
        return sha256.hexdigest()

    def cleanup_temp_files(self):
        print("[5/5] Limpiando archivos temporales...")
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                return True
            except OSError:
                return False
        return True

    def show_summary(self, exe_file, size_mb):
        print("""
        +===========================================+
        |          COMPILACION COMPLETADA           |
        +===========================================+
        """)
        if exe_file and exe_file.exists():
            print(f"  EJECUTABLE: {exe_file.name}")
            print(f"  TAMAÑO:     {size_mb:.1f} MB")
            print(f"  SHA256:     {self.generate_checksum(exe_file)}")
            print(f"  UBICACION:  {self.build_dir.relative_to(self.root)}/")
        print("\n" + "=" * 50)

    def run(self):
        self.show_banner()
        try:
            if not self.setup_directories():
                print("ERROR: No se pudieron preparar los directorios")
                return
            if not self.verify_resources():
                print("ERROR: No se encontro el icono en assets/icon_app.ico")
                return
            if not self.copy_source_files():
                print("ERROR: No se pudieron copiar los archivos fuente")
                return
            success, exe_file = self.compile_project()
            if not success:
                print("ERROR: La compilacion fallo")
                return
            self.cleanup_temp_files()
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            self.show_summary(exe_file, size_mb)
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.running = False


def main():
    OSINTCompiler().run()


if __name__ == "__main__":
    main()
