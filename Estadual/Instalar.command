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

echo "Instalando bibliotecas, uma por uma (se alguma falhar, o script"
echo "pula para a próxima em vez de parar tudo)..."
echo ""

rm -f falhas_instalacao.txt

while IFS= read -r linha || [ -n "$linha" ]; do
    linha_limpa="$(echo "$linha" | xargs)"  # remove espaços em branco
    if [ -z "$linha_limpa" ] || [[ "$linha_limpa" == \#* ]]; then
        continue
    fi
    echo "Instalando: $linha_limpa"
    if ! ./.guia_venv/bin/python3 -m pip install "$linha_limpa"; then
        echo "   ATENÇÃO: falhou ao instalar '$linha_limpa' - pulando para a próxima"
        echo "$linha_limpa" >> falhas_instalacao.txt
    fi
    echo ""
done < requirements.txt

echo "Instalando o conversor de PDF (docx2pdf)..."
./.guia_venv/bin/python3 -m pip install docx2pdf

echo ""
echo "Instalando o navegador usado para gerar as imagens das tabelas/mapas..."
./.guia_venv/bin/python3 -m playwright install chromium

echo ""
echo "=============================================="
if [ -f falhas_instalacao.txt ]; then
    echo " Instalação concluída, MAS com alguns problemas:"
    echo ""
    cat falhas_instalacao.txt
    echo ""
    echo " As bibliotecas acima NÃO foram instaladas. O sistema pode não"
    echo " funcionar completamente até isso ser resolvido. Copie a lista"
    echo " acima (também salva em falhas_instalacao.txt) e peça ajuda"
    echo " para instalar essas especificamente."
    echo " Se algum erro mencionar 'geopandas' ou 'GDAL', considere instalar"
    echo " o Miniconda (https://docs.conda.io/en/latest/miniconda.html)"
    echo " e rodar: conda install geopandas"
else
    echo " Instalação concluída com sucesso! Use 'Abrir Painel.command'"
fi
echo "=============================================="
read -p "Pressione Enter para fechar..."
