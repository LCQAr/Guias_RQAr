#!/bin/bash
cd "$(dirname "$0")"
echo "=============================================="
echo " Instalando (teste com dados reais - Secao 3.1)"
echo "=============================================="
echo ""
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python não foi encontrado."
    echo "Baixe e instale em https://www.python.org/downloads/"
    read -p "Pressione Enter para fechar..."
    exit 1
fi
echo "Python encontrado. Instalando bibliotecas (pode demorar alguns minutos)..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "Algo deu errado instalando as bibliotecas. Veja a mensagem acima."
    echo "Se o erro mencionar 'geopandas' ou 'GDAL', considere instalar o"
    echo "Miniconda (https://docs.conda.io/en/latest/miniconda.html) e rodar:"
    echo "   conda install geopandas"
    echo "antes de tentar de novo."
    read -p "Pressione Enter para fechar..."
    exit 1
fi
echo ""
echo "Instalando o navegador usado para gerar as imagens das tabelas/mapas..."
playwright install chromium
echo ""
echo "=============================================="
echo " Instalação concluída! Use 'Abrir Painel.command'"
echo "=============================================="
read -p "Pressione Enter para fechar..."
