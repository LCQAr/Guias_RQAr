@echo off
echo ==============================================
echo  Instalando (Guia RQAr Nacional)
echo ==============================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado.
    echo Baixe e instale em https://www.python.org/downloads/
    echo IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

if not exist ".guia_venv" (
    echo Criando o ambiente virtual isolado ^(.guia_venv^)...
    python -m venv .guia_venv
)

echo Instalando bibliotecas...
".guia_venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Algo deu errado instalando as bibliotecas. Veja a mensagem acima.
    echo Se o erro mencionar "geopandas" ou "GDAL", considere instalar o
    echo Miniconda e rodar: conda install geopandas
    pause
    exit /b 1
)

echo.
echo Instalando o conversor de PDF ^(docx2pdf^)...
".guia_venv\Scripts\python.exe" -m pip install docx2pdf --no-deps

echo.
echo Instalando o navegador usado para gerar as imagens das tabelas/mapas...
".guia_venv\Scripts\python.exe" -m playwright install chromium

echo.
echo ==================================================
echo  Instalacao concluida! Siga para o próximo passo
echo ==================================================
pause
