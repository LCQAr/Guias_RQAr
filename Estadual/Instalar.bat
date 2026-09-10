@echo off
setlocal enabledelayedexpansion

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
    echo Criando o ambiente virtual isolado (.guia_venv)...
    python -m venv .guia_venv
)

echo Instalando bibliotecas, uma por uma (se alguma falhar, o script
echo pula para a proxima em vez de parar tudo)...
echo.

if exist falhas_instalacao.txt del falhas_instalacao.txt

for /f "usebackq delims=" %%L in ("requirements.txt") do (
    set "LINHA=%%L"
    if not "!LINHA!"=="" (
        if not "!LINHA:~0,1!"=="#" (
            echo Instalando: %%L
            ".guia_venv\Scripts\python.exe" -m pip install "%%L"
            if errorlevel 1 (
                echo    ATENCAO: falhou ao instalar "%%L" - pulando para a proxima
                echo %%L>>falhas_instalacao.txt
            )
            echo.
        )
    )
)

echo Instalando o conversor de PDF (docx2pdf)...
".guia_venv\Scripts\python.exe" -m pip install docx2pdf --no-deps

echo.
echo Instalando o navegador usado para gerar as imagens das tabelas/mapas...
".guia_venv\Scripts\python.exe" -m playwright install chromium

echo.
echo ==============================================
if exist falhas_instalacao.txt (
    echo  Instalacao concluida, MAS com alguns problemas:
    echo.
    type falhas_instalacao.txt
    echo.
    echo  As bibliotecas acima NAO foram instaladas. O sistema pode nao
    echo  funcionar completamente ate isso ser resolvido. Copie a lista
    echo  acima ^(tambem salva em falhas_instalacao.txt^) e peca ajuda
    echo  para instalar essas especificamente.
    echo  Se algum erro mencionar "geopandas" ou "GDAL", considere instalar
    echo  o Miniconda ^(https://docs.conda.io/en/latest/miniconda.html^)
    echo  e rodar: conda install geopandas
) else (
    echo  Instalacao concluida com sucesso! Use "Abrir Painel.bat"
)
echo ==============================================
pause
