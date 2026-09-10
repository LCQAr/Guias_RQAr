@echo off
if not exist ".guia_venv\Scripts\pythonw.exe" (
    echo ERRO: Ambiente nao encontrado.
    echo Rode "Instalar.bat" primeiro.
    pause
    exit /b 1
)
start "" ".guia_venv\Scripts\pythonw.exe" "%~dp0painel.py"
