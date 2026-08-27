@echo off
echo ==============================================
echo  Instalando (teste com dados reais - Secao 3.1)
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
echo Python encontrado. Instalando bibliotecas (pode demorar alguns minutos)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Algo deu errado instalando as bibliotecas. Veja a mensagem acima.
    echo Se o erro mencionar "geopandas" ou "GDAL", considere instalar o
    echo Miniconda (https://docs.conda.io/en/latest/miniconda.html) e rodar:
    echo    conda install geopandas
    echo antes de tentar de novo.
    pause
    exit /b 1
)
echo.
echo Instalando o navegador usado para gerar as imagens das tabelas/mapas...
playwright install chromium
echo.
echo ==============================================
echo  Instalacao concluida! Use "Abrir Painel.bat"
echo ==============================================
pause
