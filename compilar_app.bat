@echo off
chcp 65001 >nul
title Compilador OSINT
color 0F

echo.
echo Compilando OSINT-Herramienta de Analisis de Redes...
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    timeout /t 3 >nul
    exit /b 1
)

REM Instalar PyInstaller si falta
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller --quiet
)

REM Instalar dependencias
if exist requirements.txt (
    echo Instalando dependencias...
    pip install -r requirements.txt --quiet
)

REM Ejecutar compilador
echo.
echo Iniciando compilacion...
echo ============================
python compilar_app.py

REM Verificar resultado
if exist "build_final\OSINT-Herramienta de Analisis de Redes.exe" (
    echo.
    echo ============================
    echo COMPILACION EXITOSA!
    echo ============================
    echo.
    echo Ejecutable creado en: build_final\
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