@echo off
if not exist ".guia_venv\Scripts\python.exe" (
    echo ERRO: Ambiente nao encontrado.
    echo Rode "Instalar.bat" primeiro.
    pause
    exit /b 1
)
".guia_venv\Scripts\python.exe" -m streamlit run dashboard.py
