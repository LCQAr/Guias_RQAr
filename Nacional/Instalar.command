#!/bin/bash
cd "$(dirname "$0")"
echo "=============================================="
echo " Instalando (Guia RQAr Nacional)"
echo "=============================================="
echo ""
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python não foi encontrado."
    echo "Baixe e instale em https://www.python.org/downloads/"
    read -p "Pressione Enter para fechar..."
    exit 1
fi

if [ ! -d ".guia_venv" ]; then
    echo "Criando o ambiente virtual isolado (.guia_venv)..."
    python3 -m venv .guia_venv
fi

echo "Instalando bibliotecas..."
./.guia_venv/bin/python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "Algo deu errado instalando as bibliotecas. Veja a mensagem acima."
    echo "Se o erro mencionar 'geopandas' ou 'GDAL', considere instalar o"
    echo "Miniconda e rodar: conda install geopandas"
    read -p "Pressione Enter para fechar..."
    exit 1
fi

echo ""
echo "Instalando o conversor de PDF (docx2pdf)..."
./.guia_venv/bin/python3 -m pip install docx2pdf

echo ""
echo "Instalando o navegador usado para gerar as imagens das tabelas/mapas..."
./.guia_venv/bin/python3 -m playwright install chromium

echo ""
echo "================================================="
echo " Instalação concluída! Siga para o próximo passo"
echo "================================================="
read -p "Pressione Enter para fechar..."
