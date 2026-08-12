@echo off
chcp 65001 >nul
title Compilador OSINT
color 0F

echo.
echo Compilando OSINT-Herramienta de Analisis de Redes...
echo.

cd /d "%~dp0.."

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    timeout /t 3 >nul
    exit /b 1
)

python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller --quiet
)

echo Instalando dependencias...
pip install -e . --quiet

echo.
echo Iniciando compilacion...
echo ============================
python tools\compilar_app.py

if exist "Builds\Windows\*.exe" (
    echo.
    echo ============================
    echo COMPILACION EXITOSA!
    echo ============================
    echo.
    echo Ejecutable y SHA256 en: Builds\Windows\
    echo.
    echo Cerrando en 10 segundos...
    timeout /t 10 >nul
    exit /b 0
) else (
    echo.
    echo ============================
    echo ERROR EN COMPILACION
    echo ============================
    echo.
    echo Cerrando en 10 segundos...
    timeout /t 10 >nul
    exit /b 1
)
